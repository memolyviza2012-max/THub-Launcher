# BattleRealms — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
BattleRealms (Zen Edition) uses the custom Liquid Entertainment Engine. The mod architecture pattern is a Hybrid approach, modifying binary archives (`.H2O`) while generating and injecting custom bitmap font atlases (`.TGA`) and font layouts (`.LFR`) at runtime via Python scripts.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Liquid Entertainment Engine (Custom RTS) |
| **Developer** | Liquid Entertainment |
| **Project Codename** | Unknown |
| **Archive Format** | `.H2O` (v7, compressed with PKWARE DCL) |
| **AES Encryption** | No |
| **Compression** | PKWARE DCL |
| **Font System** | Custom Bitmap Font (`.LFR` + `.TGA` Atlas) |
| **Thai Font Used** | Configurable via Tuner Script |
| **Text System** | Binary String Tables (`.ltt` inside `.H2O`) |
| **Text Encoding** | Custom Thai Mapping |
| **Mod Complexity** | ★★★★★ (Requires deep custom font rendering script, binary patchers, and text shaper) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```
BattleRealms-Thai-FontFix-v1.0/
├── Interface/
│   ├── Interface_Text.H2O
│   └── Interface_Text.H2O.original
├── Sound/Dialogue/
│   └── *.H2O (Contains Subtitles)
└── source/
    ├── tune_thai_font.bat
    ├── br_fonttune.py
    └── brthai/
        ├── h2o.py (H2O Archive & PKWARE DCL handler)
        ├── lfr.py (LFR Font and TGA Atlas handler)
        ├── thai.py (Thai text shaping)
        └── build.py (Font renderer)
```

---

## 4. Font Analysis
- **Format**: Bitmap fonts (KeepTalking6.LFR + TGA atlas).
- **Thai rendering considerations**: The engine does NOT support native TTF or complex text shaping. All text must be pre-shaped (สระลอย, วรรณยุกต์ซ้อน).
- **Specific Issues**:
  - The engine raises standard marks by ~0.20 line height, which requires compensating when baking the font.
  - Sra Am (ำ) is split into Nikhahit (วงแหวน) and Sra Aa (า), moving the ring to `U+0E3A` (`ฺ` - Phinthu) space, adjusted for height.
  - Tone marks above upper vowels are shifted to high-tone code points (`ํ U+0E4D` and `๎ U+0E4E`).
- **Extraction**: TrueType fonts are not directly extractable as they are rendered into raster TGA textures by the mod tool.

---

## 5. Text Analysis
- Texts are stored inside `Interface_Text.H2O` and various subtitle `.H2O` files.
- Text requires a custom shaper (in `brthai/thai.py`) to swap floating vowels and shift characters before packing.
- `Sound\Dialogue\*.H2O` contains 1,801 dialogue strings, of which 1,032 need shaping.

---

## 6. Cross-Engine Comparison
- Unlike Unreal Engine or Unity, older custom RTS engines like this require baking TTF into Bitmap Atlases and manually shaping text before injection. This shares similarities with MT Framework or Luminous Engine, where text rendering is dumb and requires pre-baking positions.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
**Text & Font Pipeline:**
1. Extract `.H2O` using `h2o.py` (decompress PKWARE DCL).
2. Use Python `build.py` to render TTF into TGA atlas and update `.LFR` spacing metrics.
3. Run `thai.py` to shape Thai text (swap tone marks to high positions, split Sra Am).
4. Repack `.H2O` archives and inject.

---

## 8. Troubleshooting
- **Tone marks cut off or floating too high**: Adjust the `ความสูงสระ / วรรณยุกต์` ratio in `tune.json`. The engine intrinsically lifts marks by 0.20 line height.
- **`ต่ำ` renders incorrectly**: The font generation script must separate the `ำ` into ring and Sra Aa, mapping the ring to the `U+0E3A` slot with adjusted UVs.
- **Base consonants (ป ฝ ฟ โ ใ ไ ๆ) look misaligned**: Ensure the "จัดฐานตัวอักษรให้ตรงกัน" option is applied during rendering.

---

## 9. Required Tools
| Tool Name | Purpose |
|---|---|
| Python + Pillow | Font baking and rendering |
| BR Font Tuner (br_fonttune.py) | GUI for tuning font parameters and shaping |

---

## 10. Extracted Assets
The font is baked into a TGA atlas. A native TTF is not directly extractable from the mod files (the mod injects user-provided TTF files).
[EXTRACTION_NOTE.txt](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/LiquidEngine/Games/BattleRealms/Assets/Fonts/EXTRACTION_NOTE.txt)

---

## 11. M2M Protocol
**(สำหรับ AI Agent ที่ต้องการนำคัมภีร์ไปรันสร้างม็อดอัตโนมัติ)**

เนื่องจากเป็นระบบ Bitmap Font ที่ต้อง Shape ก่อน

### 1. Automated Font Rendering Script (Python)
```python
from PIL import Image, ImageDraw, ImageFont
import struct

def render_thai_font_to_atlas(ttf_path, output_tga, font_size=30):
    font = ImageFont.truetype(ttf_path, font_size)
    # สมมติขนาด Atlas
    atlas = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    draw = ImageDraw.Draw(atlas)
    
    # วาดพยัญชนะ
    draw.text((10, 10), "ก", font=font, fill=(255, 255, 255, 255))
    # ต้องคำนวณตำแหน่งแต่ละกลิฟฟ์และบันทึก UV...
    
    atlas.save(output_tga)
```

### 2. Automated Text Shaping Script (Regex)
```python
import re

def shape_thai_text(text):
    # แยก ำ เป็น ํ + า และย้าย ํ ไปไว้ที่ 0x0E3A
    text = text.replace('ำ', '\u0e3aา')
    
    # เลื่อนวรรณยุกต์ที่ตามหลังสระบน (ิ ี ึ ื) ให้เป็นตัวสูง
    # สมมติ 0xE4D = ไม้เอกสูง, 0xE4E = ไม้โทสูง
    text = re.sub(r'([ิีึื])่', r'\1\u0e4d', text)
    text = re.sub(r'([ิีึื])้', r'\1\u0e4e', text)
    return text
```

### 3. Automated FNT/Mapping Injector (Struct)
```python
import struct

def patch_lfr_font_metrics(lfr_path, char_code, x, y, w, h):
    with open(lfr_path, 'r+b') as f:
        # Seek to specific character metric offset (engine specific)
        # 8 bytes per char: X (2), Y (2), W (2), H (2)
        offset = HEAD_SIZE + (char_code * 8)
        f.seek(offset)
        f.write(struct.pack('<HHHH', x, y, w, h))
```
