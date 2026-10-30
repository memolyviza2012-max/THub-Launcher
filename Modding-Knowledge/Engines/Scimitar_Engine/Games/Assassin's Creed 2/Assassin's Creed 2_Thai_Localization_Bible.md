# Assassin's Creed 2 — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Assassin's Creed 2 is a classic title developed by Ubisoft, running on the Scimitar engine. This mod represents a File Replacement architecture, modifying the core `.forge` data archives to support Thai localization text.

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
D:\Mods games\Thai Mods\0_Rivet Engineer\Assassin's Creed 2\
├── DataPC.forge (90.7 MB) - ไฟล์หลัก
├── DataPC_extra.forge (109 MB) - ข้อมูลเพิ่มเติม
├── วิธีลง.txt (247 B) - README
└── Videos/
    ├── UBI_LOGO.bik
    └── en/warning_disclaimer.bik
```

---

## 4. Font Analysis
- The game uses proprietary `.forge` archives which obfuscate the font format.
- Automated extraction carved multiple blocks starting with `00 01 00 00` (TTF Magic) and matching structural requirements (5-45 tables).
- However, none of the carved files contained a valid `name` table or structure recognizable by standard Windows TTF APIs or Python's `fonttools`.
- Font is likely stored as a proprietary vector format or a bitmap texture atlas with `.fnt` style mapping.
- Thai rendering considerations (สระลอย, วรรณยุกต์, ตัวเลขไทย): The engine does not natively support complex Thai text shaping. The text likely uses custom pre-rendered characters or requires specific coordinate mapping for tone marks.

---

## 5. Text Analysis
- Binary scanning of `DataPC.forge` revealed 1,597 Thai UTF-8 sequences and 114,451 Thai UTF-16LE sequences.
- Binary scanning of `DataPC_extra.forge` revealed thousands of Thai text blocks as well.
- The sheer number of Thai UTF-16LE sequences indicates the text is heavily embedded in UTF-16LE throughout the engine's localization database format inside the Forge file.

---

## 6. Cross-Engine Comparison
- Compared to modern Ubisoft games running on AnvilNext (e.g. Assassin's Creed Unity), Scimitar's `forge` implementation in AC2 uses an older structural format. 
- The magic bytes `73 63 69 6D 69 74 61 72` (scimitar) clearly distinguish it from newer Anvil games. Modding requires older specific tools (like ARIA or AnvilToolkit with legacy support) compared to newer games.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
**Text Pipeline:**
1. Use AnvilToolkit (or specialized Forge unpackers) to unpack `DataPC.forge` and `DataPC_extra.forge`.
2. Locate the localization DB files (often named with `.loc` or `.db` extensions internally).
3. Export text to CSV, translate, and import back using UTF-16LE encoding.
4. Repack the `.forge` files.

**Font Pipeline:**
1. Locate font textures and mapping files inside the unpacked forge data.
2. Edit the bitmap texture atlas to include Thai glyphs.
3. Update the mapping file (glyph width, UV coordinates) to point to the new Thai glyphs.
4. Replace the old font files and repack.

---

## 8. Troubleshooting
- **Game crash on startup**: This often happens if the `.forge` file is repacked incorrectly or file sizes mismatch in a way the engine doesn't expect.
- **Thai vowels/tone marks misaligned (สระลอย)**: Requires manual adjustment of the font's Y-offset and height in the proprietary mapping file, or pre-shaping the text before injecting it into the DB.
- **Text shows as squares**: Ensure the correct font file in `DataPC.forge` has been successfully replaced with one containing Thai glyphs.

---

## 9. Required Tools
| Tool Name | Purpose | Source |
|---|---|---|
| AnvilToolkit | Unpacking and repacking `.forge` files | NexusMods/GitHub |
| Hex Editor (HxD) | Manual verification of file headers and text encoding | Official Site |
| Custom Forge Extractor | Legacy tool specifically for AC1/AC2 (if AnvilToolkit fails) | Modding Forums |

---

## 10. Extracted Assets
Extraction of standard installable TTF/OTF fonts failed.
See `E:\Mod_Workspace\Modding-Knowledge\Engines\Scimitar_Engine\Games\Assassin's Creed 2\Assets\Fonts\EXTRACTION_NOTE.txt` for details.

---

## 11. M2M Protocol
### Automated Font Rendering Script (Python)
```python
# M2M Protocol for Bitmap Font Generation
import sys
from PIL import Image, ImageDraw, ImageFont

def generate_bitmap_atlas(text, font_path, out_image_path):
    # Setup image parameters
    width, height = 1024, 1024
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Load Thai TTF
    font = ImageFont.truetype(font_path, 32)
    
    # Draw characters and save mapping
    x, y = 0, 0
    mapping = {}
    for char in text:
        bbox = draw.textbbox((x, y), char, font=font)
        char_w = bbox[2] - bbox[0]
        char_h = bbox[3] - bbox[1]
        
        if x + char_w > width:
            x = 0
            y += 40
            
        draw.text((x, y), char, font=font, fill=(255, 255, 255, 255))
        mapping[char] = (x, y, char_w, char_h)
        x += char_w + 2
        
    image.save(out_image_path)
    return mapping
```

### Automated Text Shaping Script (Regex)
```python
import re

def pre_shape_thai_text(text):
    # Mapping table for upper/lower vowels to avoid overlap
    replacements = {
        'ป'+'ี': 'ป'+'\uF703', # Example: Shifted vowel for tall consonants
        'ป'+'ิ': 'ป'+'\uF701'
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text
```

### Automated FNT/Mapping Injector (Struct)
```python
import struct

def inject_font_mapping(fnt_path, mapping):
    with open(fnt_path, 'r+b') as f:
        # Example struct: ID (4 bytes), X (2), Y (2), Width (2), Height (2)
        for char, (x, y, w, h) in mapping.items():
            char_id = ord(char)
            # Find char_id in the binary mapping (assuming sorted or fixed offset)
            # and overwrite the coordinates
            packed_data = struct.pack('<H H H H', x, y, w, h)
            # f.write(packed_data)
```
