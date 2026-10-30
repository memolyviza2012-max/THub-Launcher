# Assassin's Creed Unity — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Assassin's Creed Unity runs on the AnvilNext 2.0 engine, which evolved from the original Scimitar engine. Despite the engine upgrade, the game still heavily relies on the `.forge` container format with the legacy `scimitar` magic bytes. The mod uses a File Replacement architecture, injecting localized assets directly into these `.forge` files.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | AnvilNext 2.0 |
| **Developer** | Ubisoft |
| **Project Codename** | Unity |
| **Archive Format** | .forge |
| **AES Encryption** | No |
| **Compression** | LZO or Zlib block compression typically used in Anvil |
| **Font System** | Custom Bitmap/Vector (Not Standard TTF) |
| **Thai Font Used** | Unknown (Failed to extract valid TTF) |
| **Text System** | Binary embedded LocDB |
| **Text Encoding** | UTF-8 / UTF-16 LE |
| **Mod Complexity** | ★★★☆☆ (Requires Forge repacking tools) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```text
D:\Mods games\Thai Mods\0_Rivet Engineer\Assassin Creed Unity\
├── DataPC.forge (313 MB) - ไฟล์ข้อมูลหลักของเกม
└── DataPC_patch_01.forge (48 MB) - ไฟล์แพตช์ข้อมูลอัปเดต
```

---

## 4. Font Analysis
- Like earlier Assassin's Creed titles, AC Unity packages its fonts inside `.forge` files in a proprietary format.
- Automated extraction carved multiple sections with `00 01 00 00` (TTF Magic). However, they lack standard TrueType table directory structures like a valid `name` table.
- Fonts are typically handled as texture atlases (bitmaps) or proprietary vectors mapped via custom headers.
- Thai rendering considerations (สระลอย, วรรณยุกต์): Standard AnvilNext doesn't natively support complex text shaping for Thai without external modifications or pre-shaping text glyphs before inserting them into the database.

---

## 5. Text Analysis
- Binary scanning of `.forge` files reveals the presence of Thai text sequences.
- `DataPC_patch_01.forge` contains 551 UTF-8 Thai sequences and 96,651 UTF-16LE Thai sequences, heavily suggesting the primary localization database is embedded inside the patch or main forge and relies on UTF-16LE strings.

---

## 6. Cross-Engine Comparison
- While AC Unity runs on AnvilNext 2.0, its fundamental file structure `.forge` starts with the exact same `73 63 69 6D 69 74 61 72` ("scimitar") magic bytes as AC2 and AC Brotherhood. 
- However, the internal block structure and compression algorithms may differ from the older Scimitar games, requiring updated tools like newer versions of AnvilToolkit that specifically support AC Unity.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
**Text Pipeline:**
1. Use AnvilToolkit (with AC Unity support configured) to unpack `DataPC.forge` and `DataPC_patch_01.forge`.
2. Locate localization database files inside the unpacked folders.
3. Export text blocks, inject Thai translations, and re-import using UTF-16LE.
4. Repack the `.forge` files. 

**Font Pipeline:**
1. Locate the font texture atlases and mapping files within the unpacked forge data.
2. Edit the bitmap texture atlas to include Thai glyphs using image editing tools.
3. Update the font mapping files to point to the correct UV coordinates and character widths.
4. Repack the files.

---

## 8. Troubleshooting
- **Game crash on startup**: This often happens if the `.forge` file is repacked incorrectly or file sizes mismatch in a way the engine doesn't expect.
- **Thai vowels/tone marks misaligned (สระลอย)**: Requires manual adjustment of the font's Y-offset and height in the proprietary mapping file, or pre-shaping the text before injecting it into the DB.
- **Text shows as squares**: Ensure the correct font file has been successfully replaced with one containing Thai glyphs. Patch files (e.g., `DataPC_patch_01.forge`) typically override base files, so make sure fonts in the patch are also modified if they exist there.

---

## 9. Required Tools
| Tool Name | Purpose | Source |
|---|---|---|
| AnvilToolkit | Unpacking and repacking `.forge` files | NexusMods/GitHub |
| Hex Editor (HxD) | Manual verification of file headers and text encoding | Official Site |

---

## 10. Extracted Assets
Extraction of standard installable TTF/OTF fonts failed.
See `E:\Mod_Workspace\Modding-Knowledge\Engines\Scimitar_Engine\Games\Assassin's Creed Unity\Assets\Fonts\EXTRACTION_NOTE.txt` for details.

---

## 11. M2M Protocol
### Automated Font Rendering Script (Python)
```python
# M2M Protocol for Bitmap Font Generation
import sys
from PIL import Image, ImageDraw, ImageFont

def generate_bitmap_atlas(text, font_path, out_image_path):
    width, height = 2048, 2048
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    font = ImageFont.truetype(font_path, 32)
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
        'ป'+'ี': 'ป'+'\uF703',
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
