import os
import sys
import re
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, base_dir)

from core.font_service import FontService
from tools.fonts.mapping.thai_font_mapper import load_mapping, make_pattern, map_text

mapping_path = Path(base_dir) / "tools" / "fonts" / "mapping" / "Mapping.json"
pua_mapping = load_mapping(mapping_path)
pua_pattern = make_pattern(pua_mapping)

cmap_cache = {}

def get_smart_text(text: str, font_path: str) -> str:
    """Uses PUA mapping if font supports the mapped glyphs; falls back to standard text otherwise."""
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

def main():
    fs = FontService()
    fonts = fs.get_all_fonts()

    ui_font_path = r"C:\Windows\Fonts\leelawad.ttf"
    lbl_bold_path = r"C:\Windows\Fonts\leelawdb.ttf"
    if not os.path.exists(lbl_bold_path):
        lbl_bold_path = ui_font_path

    preview_dir = os.path.join(fs.fonts_dir, "previews")
    os.makedirs(preview_dir, exist_ok=True)

    W, H = 1920, 1080
    generated_count = 0

    for f in fonts:
        fid = f["id"]
        variants = fs.get_font_variants(fid)
        for v in variants:
            rel_p = v["rel_path"]
            v_fn = os.path.basename(rel_p)
            v_clean = re.sub(r'[^a-zA-Z0-9_]', '_', os.path.splitext(v_fn)[0].lower())
            expected_fn = f"{fid}_{v_clean}_preview.png"
            expected_full = os.path.join(preview_dir, expected_fn)

            if os.path.exists(expected_full) and '--force' not in sys.argv:
                continue

            f_path = v["full_path"]
            if not os.path.exists(f_path):
                continue

            img = Image.new("RGB", (W, H), color=(13, 17, 26))
            draw = ImageDraw.Draw(img)

            draw.rectangle([(6, 6), (W - 7, H - 7)], outline=(32, 42, 64), width=3)
            draw.rectangle([(0, 0), (W, 14)], fill=(168, 85, 247))
            draw.rectangle([(22, 22), (W - 23, H - 23)], outline=(22, 29, 44), width=2)

            try:
                font_title = ImageFont.truetype(f_path, 68)
                font_sample_th1 = ImageFont.truetype(f_path, 60)
                font_sample_th2 = ImageFont.truetype(f_path, 44)
                font_sample_en = ImageFont.truetype(f_path, 38)
                font_btn = ImageFont.truetype(f_path, 30)
            except Exception:
                font_title = font_sample_th1 = font_sample_th2 = font_sample_en = font_btn = ImageFont.truetype(ui_font_path, 32)

            is_var = v.get("is_variable", False)
            if is_var:
                try:
                    font_sample_th1.set_variation_by_axes([750, 100])
                    font_sample_th2.set_variation_by_axes([300, 100])
                except Exception:
                    pass

            if f_path not in cmap_cache:
                try:
                    tt = TTFont(f_path)
                    cmap_cache[f_path] = tt.getBestCmap()
                except Exception:
                    cmap_cache[f_path] = {}
            cmap = cmap_cache[f_path]
            pua_count = sum(1 for c in cmap if 0xF000 <= c <= 0xF8FF)

            lbl_font = ImageFont.truetype(ui_font_path, 24)
            lbl_bold = ImageFont.truetype(lbl_bold_path, 24)

            style_display = v.get("display_th", v.get("style_name", "Regular"))
            draw.text((70, 48), get_smart_text(f"{f['name_en']} — {style_display}", f_path), fill=(255, 255, 255), font=font_title)

            bx = 70
            w1, h1 = draw_pill_badge(draw, (bx, 144), f["category"], lbl_font, (30, 41, 59), (168, 85, 247), (216, 180, 254), pad_x=20, pad_y=6)
            bx += w1 + 14
            w2, h2 = draw_pill_badge(draw, (bx, 144), f"น้ำหนัก: {style_display}", lbl_font, (23, 37, 84), (59, 130, 246), (147, 197, 253), pad_x=20, pad_y=6)
            bx += w2 + 14

            if is_var:
                pua_badge_txt = "ปรับน้ำหนักได้ 100–900"
            elif pua_count >= 1500:
                pua_badge_txt = f"PUA {pua_count:,} Glyphs"
            elif pua_count >= 20:
                pua_badge_txt = f"Windows PUA ({pua_count} Glyphs)"
            else:
                pua_badge_txt = "Unicode Standard"

            draw_pill_badge(draw, (bx, 144), pua_badge_txt, lbl_font, (6, 78, 59), (16, 185, 129), (110, 231, 183), pad_x=18, pad_y=6)

            draw.line([(70, 218), (W - 70, 218)], fill=(38, 50, 75), width=2)

            draw.text((70, 234), f"ตัวอย่างการแสดงผลภาษาไทย (Thai Specimen - {style_display}):", fill=(56, 189, 248), font=lbl_bold)
            draw.text((70, 272), get_smart_text("ยินดีต้อนรับสู่อาณาจักร สระและวรรณยุกต์คมชัด", f_path), fill=(248, 250, 252), font=font_sample_th1)
            draw.text((70, 356), get_smart_text("ป่าไม้น้ำใส กิ๊บเก๋ ข้าวเหนียวมู่อุ่นๆ ชี้ช้ำ ปู่ย่า ๑๒๓๔๕", f_path), fill=(226, 232, 240), font=font_sample_th2)

            draw.text((70, 434), "English Specimen & Numerals:", fill=(148, 163, 184), font=lbl_bold)
            draw.text((70, 470), "The quick brown fox jumps over the lazy dog 1234567890", fill=(203, 213, 225), font=font_sample_en)

            draw.line([(70, 544), (W - 70, 544)], fill=(32, 43, 64), width=2)

            draw.text((70, 560), "จำลองแถบเมนูในเกม (In-Game Menu Simulation):", fill=(148, 163, 184), font=lbl_bold)
            buttons = [
                get_smart_text("เริ่มเกมใหม่", f_path),
                get_smart_text("ดำเนินการต่อ", f_path),
                get_smart_text("การตั้งค่า", f_path),
                get_smart_text("ออกจากเกม", f_path)
            ]
            btn_x = 70
            for b_txt in buttons:
                bbox = font_btn.getbbox(b_txt)
                txt_w = bbox[2] - bbox[0]
                txt_h = bbox[3] - bbox[1]
                btn_w = txt_w + 64
                btn_h = 58
                draw.rounded_rectangle([(btn_x, 598), (btn_x + btn_w, 598 + btn_h)], radius=10, fill=(20, 28, 44), outline=(52, 211, 153), width=2)
                tx = btn_x + (btn_w - txt_w) // 2
                ty = 598 + (btn_h - txt_h) // 2 - bbox[1]
                draw.text((tx, ty), b_txt, fill=(52, 211, 153), font=font_btn)
                btn_x += btn_w + 20

            rec_box_top = 696
            draw.rounded_rectangle([(70, rec_box_top), (W - 70, rec_box_top + 265)], radius=14, fill=(18, 24, 38), outline=(59, 130, 246), width=2)
            card_w = (W - 140 - 40) // 3

            c1_x = 90
            draw.rounded_rectangle([(c1_x, rec_box_top + 20), (c1_x + card_w, rec_box_top + 245)], radius=10, fill=(24, 32, 50), outline=(251, 191, 36), width=1)
            draw.text((c1_x + 20, rec_box_top + 34), "จุดเด่นและแนวเกมที่เหมาะ:", fill=(251, 191, 36), font=lbl_bold)
            draw.text((c1_x + 20, rec_box_top + 80), get_smart_text(f.get("best_for", "UI & Subtitles")[:45], f_path), fill=(241, 245, 249), font=lbl_font)

            c2_x = c1_x + card_w + 20
            draw.rounded_rectangle([(c2_x, rec_box_top + 20), (c2_x + card_w, rec_box_top + 245)], radius=10, fill=(24, 32, 50), outline=(59, 130, 246), width=1)
            draw.text((c2_x + 20, rec_box_top + 34), "ระดับความเหมาะสมใน Engine:", fill=(96, 165, 250), font=lbl_bold)
            ey = rec_box_top + 80
            if "engines" in f and f["engines"]:
                for e_name, e_score in sorted(f["engines"].items(), key=lambda x: x[1], reverse=True)[:3]:
                    draw.text((c2_x + 20, ey), get_smart_text(f"• {e_name}: {e_score}%", f_path), fill=(226, 232, 240), font=lbl_font)
                    ey += 40

            c3_x = c2_x + card_w + 20
            draw.rounded_rectangle([(c3_x, rec_box_top + 20), (c3_x + card_w, rec_box_top + 245)], radius=10, fill=(24, 32, 50), outline=(16, 185, 129), width=1)
            draw.text((c3_x + 20, rec_box_top + 34), "ไฟล์และชุด Mapping:", fill=(52, 211, 153), font=lbl_bold)
            draw.text((c3_x + 20, rec_box_top + 80), f"• ไฟล์: {v_fn}", fill=(226, 232, 240), font=lbl_font)

            if pua_count >= 1500:
                mapping_txt = "• Mapping.json (2,208 ตัว)"
            elif is_var:
                mapping_txt = "• Variable Font (wght 100–900)"
            else:
                mapping_txt = f"• Glyph Coverage ({len(cmap)} ตัว)"

            draw.text((c3_x + 20, rec_box_top + 120), mapping_txt, fill=(226, 232, 240), font=lbl_font)
            draw.text((c3_x + 20, rec_box_top + 160), "• Char.txt สำหรับสร้าง SDF", fill=(226, 232, 240), font=lbl_font)

            draw.text((W - 370, H - 75), "THub Modding Font Studio • Full HD 1080p", fill=(71, 85, 105), font=lbl_font)

            img.save(expected_full, format="PNG", quality=95)
            generated_count += 1
            print(f"Generated ({generated_count}): {expected_fn}")

    print(f"Complete! Generated {generated_count} missing preview images.")

if __name__ == "__main__":
    main()
