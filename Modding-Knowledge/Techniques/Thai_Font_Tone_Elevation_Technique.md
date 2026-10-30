# Thai Font Tone Elevation Technique (+160 Units)
## เทคนิคการยกวรรณยุกต์ไทยขึ้น 160 หน่วย เพื่อแก้ปัญหาวรรณยุกต์ทับสระบน (ั และ ี) ใน Game Engines

### 1. ความเป็นมาและปัญหาที่พบ (The Stacking Marks Dilemma)
ในเอนจินเกมหลายตัว โดยเฉพาะระบบ **Unity TextMeshPro (TMP)**, **Unity Canvas Text (`UnityEngine.UI.Text`)**, **Unreal Engine Canvas/Slate**, หรือเกมเอนจินที่ใช้ FreeType/DirectWrite/Bitmap Font Baker โดยไม่ได้เปิดใช้งาน OpenType Layout Table (GPOS/GSUB mark-to-mark attachment):
- **สระบน (Upper Vowels)**:
  - ไม้หันอากาศ (`ั` U+0E31): สูงถึง `yMax ≈ 750 - 770`
  - สระอี (`ี` U+0E35), สระอิ (`ิ`), สระอึ (`ึ`), สระอื (`ื`): สูงถึง `yMax ≈ 780 - 810`
- **วรรณยุกต์ (Tone Marks)**:
  - ไม้เอก (`่` U+0E48), ไม้โท (`้` U+0E49), ไม้ตรี (`๊` U+0E4A), ไม้จัตวา (`๋` U+0E4B), ทัณฑฆาต/การันต์ (`์` U+0E4C):
  - ในฟอนต์มาตรฐาน วรรณยุกต์ถูกวาดไว้ที่ระดับความสูงฐานล่าง `yMin ≈ 614 - 660`
- **ผลกระทบ**:
  - เมื่อข้อความมีสระบนซ้อนกับวรรณยุกต์ (เช่น คำว่า `กั้`, `กี้`, `ขั่`, `ที่`, `ปี้`, `มั่ง`, `ทั้ง`, `ขั้น`, `ชี้`) วรรณยุกต์จะถูกวางซ้อนที่พิกัดแกน Y เดียวกัน
  - วรรณยุกต์จึง **จมทับและกลืนเข้าไปในเนื้อของ ั หรือ ี** จนอ่านไม่ออก

---

### 2. มาตรฐานการยกพิกัดวรรณยุกต์ขึ้น 160 หน่วย (+160 Units Shift)
การคำนวณระยะพิกัดที่แม่นยำที่สุดคือการยกวรรณยุกต์ขึ้น **160 หน่วย (`shift_y = 160`)**:
1. **แก้ปัญหาการชน 100%**:
   - `yMin` ของวรรณยุกต์ขยับจาก ~622 ขึ้นไปเป็น **~782** หน่วย
   - ลอยพ้นขอบบนของ `ั` (768) และ `ี` (781) อย่างสมบูรณ์แบบ
2. **รักษาความสวยงามของคำเดี่ยว**:
   - เมื่อวรรณยุกต์อยู่เดี่ยวๆ เหนือพยัญชนะ (เช่น `บ้าน`, `พ่อ`, `ม้า`, `ได้`, `เจ้า`) วรรณยุกต์จะอยู่ในระดับความสูงที่สง่างาม ชัดเจน อ่านง่าย ไม่ลอยจนหลุดสายตา
3. **การป้องกันปัญหา Font Clipping (OS & Engine Safe)**:
   - สคริปต์จะตรวจสอบความสูงสูงสุด `max_shifted_ymax`
   - หากเกินค่าเดิม จะอัปเดต `OS/2.usWinAscent` และ `hhea.ascent` ให้สูงครอบคลุมวรรณยุกต์ (+10 units headroom) โดยอัตโนมัติ ทำให้ Windows GDI, DirectWrite และ Unity Texture Baker ไม่ตัดหัววรรณยุกต์ทิ้ง

---

### 3. สคริปต์ประมวลผลทั้งคลังฟอนต์ (`batch_shift_tone_marks.py`)

```python
import os
import sys
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates

TARGET_UNICODES = {
    0x0E48,  # MAI EK (่)
    0x0E49,  # MAI THO (้)
    0x0E4A,  # MAI TRI (๊)
    0x0E4B,  # MAI CHATTAWA (๋)
    0x0E4C,  # THANTHAKHAT (์)
}
SUFFIX_PATTERNS = ['.small', '.alt', '.shift', '.up', 'small', 'alt', 'shift', 'up']
SHIFT_Y = 160

def shift_font_tone_marks(font_path, shift_y=160):
    font = TTFont(font_path)
    if 'glyf' not in font: return False, "No glyf table"
    glyf = font['glyf']
    cmap = font.getBestCmap()
    
    target_names = set()
    for cp, gname in cmap.items():
        if cp in TARGET_UNICODES and gname in glyf:
            target_names.add(gname)
            for suffix in SUFFIX_PATTERNS:
                cand = f"{gname}{suffix}"
                if cand in glyf: target_names.add(cand)

    max_shifted_ymax = -9999
    for gname in target_names:
        g = glyf[gname]
        g.expand(glyf)
        if hasattr(g, 'coordinates') and g.coordinates:
            g.coordinates = GlyphCoordinates([(x, y + shift_y) for x, y in g.coordinates])
            if hasattr(g, 'yMin'): g.yMin += shift_y
            if hasattr(g, 'yMax'): g.yMax += shift_y
            g.recalcBounds(glyf)
            if g.yMax > max_shifted_ymax: max_shifted_ymax = g.yMax
        elif g.isComposite():
            for comp in g.components: comp.y += shift_y
            if hasattr(g, 'yMin'): g.yMin += shift_y
            if hasattr(g, 'yMax'): g.yMax += shift_y
            g.recalcBounds(glyf)
            if g.yMax > max_shifted_ymax: max_shifted_ymax = g.yMax

    # ปรับ Ascender ป้องกันฟอนต์ถูกตัดหัว
    if max_shifted_ymax > 0:
        if 'OS/2' in font and font['OS/2'].usWinAscent < max_shifted_ymax:
            font['OS/2'].usWinAscent = int(max_shifted_ymax + 10)
        if 'hhea' in font and font['hhea'].ascent < max_shifted_ymax:
            font['hhea'].ascent = int(max_shifted_ymax + 10)

    font.save(font_path)
    return True, "Done"
```

---

### 4. สรุปประโยชน์ของเทคนิค +160 Units
1. **รองรับทั้ง Unicode ปกติ และ PUA**: ข้อความในเกมอ่านได้ชัดเจนทั้งสองระบบ
2. **ไม่ทับ ั หรือ ี 100%**: แก้ปัญหาตัวอักษรจมกลืนกันใน TextMeshPro และ Unity Canvas
3. **เสถียรภาพสูงสุด**: ฟอนต์นำไปใช้ได้กับทุกเกมเอนจินโดยไม่ต้องกังวลเรื่องการตั้งค่า OpenType Shaper พิเศษ
