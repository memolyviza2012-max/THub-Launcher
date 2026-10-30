# Assassin's Creed Brotherhood — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Assassin's Creed Brotherhood runs on an updated version of the Scimitar engine used in AC2. The mod architecture relies on File Replacement, where the core `.forge` data archives (including WhiteRoom) are patched or replaced to include Thai localization.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Scimitar Engine |
| **Developer** | Ubisoft |
| **Project Codename** | N/A |
| **Archive Format** | .forge |
| **AES Encryption** | No |
| **Compression** | None/Unknown block compression |
| **Font System** | Custom Bitmap/Vector (Not Standard TTF) |
| **Thai Font Used** | Unknown (Failed to extract valid TTF) |
| **Text System** | Binary embedded / Custom |
| **Text Encoding** | UTF-8 / UTF-16 LE |
| **Mod Complexity** | ★★★☆☆ (Requires Forge repacking tools) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```text
D:\Mods games\Thai Mods\0_Rivet Engineer\Assassin's Creed Brotherhood\
├── DataPC.forge (256 MB) - ไฟล์หลัก
├── DataPC_extra.forge (242 MB) - ข้อมูลเพิ่มเติม
├── DataPC_WhiteRoom.forge (108 MB) - ข้อมูลฉากโหลด/เมนู
├── วิธีลง.txt (342 B) - README
└── Videos/
    └── Various .bik video files
```

---

## 4. Font Analysis
- Font formats are stored inside the proprietary `.forge` archives.
- Automated extraction carved blocks matching `00 01 00 00` (TTF Magic) but failed to find valid `name` tables, indicating standard TTFs are not used.
- The fonts are likely bitmap texture atlases. 
- Thai rendering considerations (สระลอย, วรรณยุกต์): Requires exact UV coordinate mapping for tone marks. Pre-shaping or manual mapping adjustments are necessary.

---

## 5. Text Analysis
- The `.forge` archives contain thousands of UTF-16LE and UTF-8 strings.
- Text is stored in proprietary database structures that must be exported and reimported using specialized community tools.

---

## 6. Cross-Engine Comparison
- Very similar to Assassin's Creed 2 (Scimitar) but with larger data partitions (e.g., separating the WhiteRoom assets into `DataPC_WhiteRoom.forge`).
- Does not use the more advanced structure seen in later AnvilNext titles like AC Unity, though it shares the same `.forge` container format and "scimitar" magic bytes.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
**Text Pipeline:**
1. Use AnvilToolkit (with AC Brotherhood support) to unpack the `.forge` files.
2. Locate the localization database assets.
3. Export text to CSV, edit in Thai, and import back.
4. Repack the `.forge` files.

**Font Pipeline:**
1. Locate font textures and `.fnt` (or equivalent) mapping files.
2. Edit the bitmap texture atlas to add Thai characters.
3. Update the mapping file with UV coordinates for the new glyphs.
4. Replace original files and repack.

---

## 8. Troubleshooting
- **Game crash on startup**: Check for `.forge` size mismatches or corrupted repacks. Make sure you repacked the correct game version's files.
- **Thai vowels/tone marks misaligned (สระลอย)**: Requires manual adjustment of the font mapping or pre-shaping the text string (e.g. replacing 'ป'+'ี' with a shifted tone character).
- **WhiteRoom missing text**: Ensure `DataPC_WhiteRoom.forge` is correctly modified, as it handles the loading screen and menus.

---

## 9. Required Tools
| Tool Name | Purpose | Source |
|---|---|---|
| AnvilToolkit | Unpacking and repacking `.forge` files | NexusMods/GitHub |
| Hex Editor (HxD) | Hex viewing and validation | Official Site |

---

## 10. Extracted Assets
Extraction of standard installable TTF/OTF fonts failed.
See `E:\Mod_Workspace\Modding-Knowledge\Engines\Scimitar_Engine\Games\Assassin's Creed Brotherhood\Assets\Fonts\EXTRACTION_NOTE.txt` for details.

---

## 11. M2M Protocol
### Automated Font Rendering Script (Python)
```python
# M2M Protocol for Bitmap Font Generation
import sys
from PIL import Image, ImageDraw, ImageFont

def generate_bitmap_atlas(text, font_path, out_image_path):
    width, height = 1024, 1024
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    font = ImageFont.truetype(font_path, 32)
    x, y, mapping = 0, 0, {}
    
    for char in text:
        bbox = draw.textbbox((x, y), char, font=font)
        char_w, char_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        
        if x + char_w > width:
            x, y = 0, y + 40
            
        draw.text((x, y), char, font=font, fill=(255, 255, 255, 255))
        mapping[char] = (x, y, char_w, char_h)
        x += char_w + 2
        
    image.save(out_image_path)
    return mapping
```

### Automated Text Shaping Script (Regex)
```python
def pre_shape_thai_text(text):
    replacements = { 'ปี': 'ป'+'\uF703', 'ปิ': 'ป'+'\uF701' }
    for k, v in replacements.items(): text = text.replace(k, v)
    return text
```

### Automated FNT/Mapping Injector (Struct)
```python
import struct

def inject_font_mapping(fnt_path, mapping):
    with open(fnt_path, 'r+b') as f:
        for char, (x, y, w, h) in mapping.items():
            packed_data = struct.pack('<H H H H', x, y, w, h)
            # Inject at appropriate offset
```
