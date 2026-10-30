import os
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
from mapping.thai_font_mapper import load_mapping, make_pattern, map_text

fonts_dir = os.path.dirname(os.path.abspath(__file__))
lib_dir = os.path.join(fonts_dir, "library")
preview_dir = os.path.join(fonts_dir, "previews")
os.makedirs(preview_dir, exist_ok=True)

# Load PUA mapping for pixel-perfect specimen rendering without libraqm
mapping_path = Path(fonts_dir) / "mapping" / "Mapping.json"
pua_mapping = load_mapping(mapping_path)
pua_pattern = make_pattern(pua_mapping)

cmap_cache = {}

def get_smart_text(text: str, font_path: str) -> str:
    """Uses PUA mapping if the font has the mapped glyphs; otherwise falls back to standard text."""
    if font_path not in cmap_cache:
        try:
            tt = TTFont(font_path)
            cmap_cache[font_path] = tt.getBestCmap()
        except Exception:
            cmap_cache[font_path] = {}
    cmap = cmap_cache[font_path]
    mapped = map_text(text, pua_mapping, pua_pattern)
    if cmap and all(ord(c) in cmap for c in mapped if ord(c) > 127):
        return mapped
    return text

def pua(text: str) -> str:
    return map_text(text, pua_mapping, pua_pattern)

cat_path = os.path.join(fonts_dir, "catalog.json")
with open(cat_path, "r", encoding="utf-8") as f:
    FONT_CATALOG = json.load(f)

ui_font_path = r"C:\Windows\Fonts\leelawad.ttf"
if not os.path.exists(ui_font_path):
    ui_font_path = r"C:\Windows\Fonts\tahoma.ttf"

lbl_bold_path = r"C:\Windows\Fonts\leelawdb.ttf"
if not os.path.exists(lbl_bold_path):
    lbl_bold_path = ui_font_path

def draw_pill_badge(draw, xy, text, font, bg_color, border_color, text_color, pad_x=22, pad_y=8):
    x, y = xy
    bbox = font.getbbox(text)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    w = tw + pad_x * 2
    h = th + pad_y * 2
    draw.rounded_rectangle([(x, y), (x + w, y + h)], radius=h // 2, fill=bg_color, outline=border_color, width=2)
    text_y = y + pad_y - bbox[1]
    draw.text((x + pad_x, text_y), text, fill=text_color, font=font)
    return w, h

def wrap_text_comma(text, font, max_width):
    lines = []
    parts = text.split(", ")
    cur = ""
    for p in parts:
        cand = (cur + ", " + p) if cur else p
        bbox = font.getbbox(cand)
        if (bbox[2] - bbox[0]) <= max_width:
            cur = cand
        else:
            if cur:
                lines.append(cur)
            cur = p
    if cur:
        lines.append(cur)
    return lines

def generate_crisp_preview(item):
    f_path = os.path.join(lib_dir, item["folder"], item["primary_file"].replace("/", os.sep))
    if not os.path.exists(f_path):
        f_path = os.path.join(lib_dir, item["folder"], item["regular_file"].replace("/", os.sep))

    W, H = 1920, 1080
    img = Image.new("RGB", (W, H), color=(13, 17, 26))
    draw = ImageDraw.Draw(img)

    # Outer Frame & Top Accent
    draw.rectangle([(6, 6), (W - 7, H - 7)], outline=(32, 42, 64), width=3)
    draw.rectangle([(0, 0), (W, 14)], fill=(168, 85, 247))
    draw.rectangle([(22, 22), (W - 23, H - 23)], outline=(22, 29, 44), width=2)

    # Fonts
    font_title = ImageFont.truetype(f_path, 76)
    font_badge = ImageFont.truetype(f_path, 30)
    font_sample_th1 = ImageFont.truetype(f_path, 64)
    font_sample_th2 = ImageFont.truetype(f_path, 48)
    font_sample_en = ImageFont.truetype(f_path, 40)
    font_btn = ImageFont.truetype(f_path, 32)
    font_card_txt = ImageFont.truetype(f_path, 28)
    
    lbl_font = ImageFont.truetype(ui_font_path, 24)
    lbl_bold = ImageFont.truetype(lbl_bold_path, 24)

    # Inspect font cmap and metadata
    if f_path not in cmap_cache:
        try:
            tt = TTFont(f_path)
            cmap_cache[f_path] = tt.getBestCmap()
        except Exception:
            cmap_cache[f_path] = {}
    cmap = cmap_cache[f_path]
    pua_count = sum(1 for c in cmap if 0xF000 <= c <= 0xF8FF)
    is_var = "[" in f_path or "wght" in f_path.lower()
    if is_var:
        pua_badge_text = "Variable Font"
    elif pua_count >= 1500:
        pua_badge_text = f"PUA {pua_count:,} Glyphs"
    elif pua_count >= 20:
        pua_badge_text = f"Windows PUA ({pua_count} Glyphs)"
    else:
        pua_badge_text = "Unicode Standard"

    # Header
    draw.text((70, 48), get_smart_text(f"{item['name_en']}   ({item['name_th']})", f_path), fill=(255, 255, 255), font=font_title)
    
    # Pill badges
    bx = 70
    w1, h1 = draw_pill_badge(draw, (bx, 150), item['category'], font_badge, (30, 41, 59), (168, 85, 247), (216, 180, 254), pad_x=22, pad_y=8)
    bx += w1 + 16
    w2, h2 = draw_pill_badge(draw, (bx, 150), f"สไตล์: {item['tone']}", font_badge, (23, 37, 84), (59, 130, 246), (147, 197, 253), pad_x=22, pad_y=8)
    bx += w2 + 16
    draw_pill_badge(draw, (bx, 150), pua_badge_text, font_badge, (6, 78, 59), (16, 185, 129), (110, 231, 183), pad_x=20, pad_y=8)

    # Divider
    draw.line([(70, 226), (W - 70, 226)], fill=(38, 50, 75), width=2)

    # Thai Specimen
    draw.text((70, 244), "ตัวอย่างการแสดงผลภาษาไทย (Thai Specimen):", fill=(56, 189, 248), font=lbl_bold)
    draw.text((70, 282), get_smart_text("ยินดีต้อนรับสู่อาณาจักร สระและวรรณยุกต์คมชัด", f_path), fill=(248, 250, 252), font=font_sample_th1)
    draw.text((70, 366), get_smart_text("ป่าไม้น้ำใส กิ๊บเก๋ ข้าวเหนียวมู่อุ่นๆ ชี้ช้ำ ปู่ย่า ๑๒๓๔๕", f_path), fill=(226, 232, 240), font=font_sample_th2)

    # English Specimen
    draw.text((70, 444), "English Specimen & Numerals:", fill=(148, 163, 184), font=lbl_bold)
    draw.text((70, 480), "The quick brown fox jumps over the lazy dog 1234567890", fill=(203, 213, 225), font=font_sample_en)

    # Divider
    draw.line([(70, 554), (W - 70, 554)], fill=(32, 43, 64), width=2)

    # In-Game Menu Buttons
    draw.text((70, 570), "จำลองแถบเมนูในเกม (In-Game Menu Simulation):", fill=(148, 163, 184), font=lbl_bold)
    
    buttons = [
        get_smart_text("เริ่มเกมใหม่", f_path),
        get_smart_text("ดำเนินการต่อ", f_path),
        get_smart_text("การตั้งค่า", f_path),
        get_smart_text("ออกจากเกม", f_path),
    ]
    btn_x = 70
    for b_txt in buttons:
        bbox = font_btn.getbbox(b_txt)
        txt_w = bbox[2] - bbox[0]
        txt_h = bbox[3] - bbox[1]
        btn_w = txt_w + 64
        btn_h = 62
        draw.rounded_rectangle([(btn_x, 610), (btn_x + btn_w, 610 + btn_h)], radius=10, fill=(20, 28, 44), outline=(52, 211, 153), width=2)
        tx = btn_x + (btn_w - txt_w) // 2
        ty = 610 + (btn_h - txt_h) // 2 - bbox[1]
        draw.text((tx, ty), b_txt, fill=(52, 211, 153), font=font_btn)
        btn_x += btn_w + 24

    # Recommendation Box
    rec_box_top = 708
    draw.rounded_rectangle([(70, rec_box_top), (W - 70, rec_box_top + 265)], radius=14, fill=(18, 24, 38), outline=(59, 130, 246), width=2)
    
    card_w = (W - 140 - 40) // 3
    
    # Card 1: จุดเด่น (Golden Accent)
    c1_x = 90
    draw.rounded_rectangle([(c1_x, rec_box_top + 20), (c1_x + card_w, rec_box_top + 245)], radius=10, fill=(24, 32, 50), outline=(251, 191, 36), width=1)
    draw.ellipse([(c1_x + 20, rec_box_top + 40), (c1_x + 32, rec_box_top + 52)], fill=(251, 191, 36))
    draw.text((c1_x + 42, rec_box_top + 34), "จุดเด่นและแนวเกมที่เหมาะ:", fill=(251, 191, 36), font=lbl_bold)
    
    best_text = item.get('best_for', 'UI & Subtitles')
    lines = wrap_text_comma(best_text, font_card_txt, card_w - 40)
    ly = rec_box_top + 80
    for line in lines[:3]:
        draw.text((c1_x + 20, ly), get_smart_text(line, f_path), fill=(241, 245, 249), font=font_card_txt)
        ly += 42

    # Card 2: Engine Match (Blue Accent)
    c2_x = c1_x + card_w + 20
    draw.rounded_rectangle([(c2_x, rec_box_top + 20), (c2_x + card_w, rec_box_top + 245)], radius=10, fill=(24, 32, 50), outline=(59, 130, 246), width=1)
    draw.ellipse([(c2_x + 20, rec_box_top + 40), (c2_x + 32, rec_box_top + 52)], fill=(59, 130, 246))
    draw.text((c2_x + 42, rec_box_top + 34), "ระดับความเหมาะสมใน Engine:", fill=(96, 165, 250), font=lbl_bold)
    
    ey = rec_box_top + 80
    if "engines" in item and item["engines"]:
        sorted_eng = sorted(item["engines"].items(), key=lambda x: x[1], reverse=True)[:3]
        for e_name, e_score in sorted_eng:
            draw.text((c2_x + 20, ey), get_smart_text(f"• {e_name}: {e_score}%", f_path), fill=(226, 232, 240), font=font_card_txt)
            ey += 44

    # Card 3: PUA & Mapping (Green Accent)
    c3_x = c2_x + card_w + 20
    draw.rounded_rectangle([(c3_x, rec_box_top + 20), (c3_x + card_w, rec_box_top + 245)], radius=10, fill=(24, 32, 50), outline=(16, 185, 129), width=1)
    draw.ellipse([(c3_x + 20, rec_box_top + 40), (c3_x + 32, rec_box_top + 52)], fill=(16, 185, 129))
    draw.text((c3_x + 42, rec_box_top + 34), "ไฟล์และชุด Mapping:", fill=(52, 211, 153), font=lbl_bold)
    
    if pua_count >= 1500:
        map_line = "• Mapping.json (2,208 ตัว)"
        type_line = "• ฟอนต์ TTF (PUA Shifted)"
    elif is_var:
        map_line = "• ปรับน้ำหนักได้ (wght 100-900)"
        type_line = "• ฟอนต์ TTF (Variable Font)"
    else:
        map_line = f"• Glyph Coverage ({len(cmap)} ตัว)"
        type_line = "• ฟอนต์ TTF (Unicode Standard)"

    draw.text((c3_x + 20, rec_box_top + 80), get_smart_text(type_line, f_path), fill=(226, 232, 240), font=font_card_txt)
    draw.text((c3_x + 20, rec_box_top + 124), get_smart_text(map_line, f_path), fill=(226, 232, 240), font=font_card_txt)
    draw.text((c3_x + 20, rec_box_top + 168), get_smart_text("• Char.txt สำหรับสร้าง SDF", f_path), fill=(226, 232, 240), font=font_card_txt)

    # Watermark
    draw.text((W - 370, H - 75), "THub Modding Font Studio • Full HD 1080p", fill=(71, 85, 105), font=lbl_font)

    # Save
    preview_fn = f"{item['id']}_preview.png"
    out_path = os.path.join(preview_dir, preview_fn)
    img.save(out_path, format="PNG", quality=95)
    return True

if __name__ == "__main__":
    count = 0
    for it in FONT_CATALOG:
        if generate_crisp_preview(it):
            count += 1
    print(f"Generated {count} / {len(FONT_CATALOG)} Full HD previews!")
