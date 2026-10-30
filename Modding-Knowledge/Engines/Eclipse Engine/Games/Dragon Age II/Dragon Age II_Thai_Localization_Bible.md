# Dragon Age II — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Dragon Age II is an action role-playing game developed by BioWare using the Eclipse Engine. The mod architecture involves File Replacement of BioWare Talk Tables (`.tlk`) and ERF archives (`.erf`) for fonts.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Eclipse Engine (BioWare) |
| **Developer** | BioWare |
| **Project Codename** | DA2 |
| **Archive Format** | .erf (Fonts), .tlk (Text) |
| **AES Encryption** | No |
| **Compression** | Zlib / None |
| **Font System** | Font Swap (.erf containing font data) |
| **Thai Font Used** | Unknown (needs ERF extraction) |
| **Text System** | BioWare Talk Table (.tlk) |
| **Text Encoding** | UTF-8 / Windows-1252 / UTF-16 |
| **Mod Complexity** | ★★★☆☆ (Requires specific ERF/TLK tools) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```
Dragon Age II/
├── font/
│   └── originsfont.erf (1.1 MB)
├── modules/
│   └── campaign_base/data/talktables/
│       └── campaign_base_en-us.tlk (1.9 MB)
└── packages/
    └── core/data/talktables/
        └── core_en-us.tlk (685 KB)
```

---

## 4. Font Analysis
- **Format**: `.erf` archive containing font textures and mapping.
- **Extraction**: Requires an ERF unpacker (like ERFEditor or Gibbed's tools). The actual font is likely a bitmap/texture format (e.g., `.dds` or `.gfx`).
- **Thai rendering**: Eclipse Engine often relies on bitmap fonts, so floating vowels (สระลอย) must be handled by custom mapping or pre-rendering the glyphs correctly in the texture atlas.

---

## 5. Text Analysis
- **Format**: `.tlk` (Talk Table).
- **Structure**: Binary format mapping a string ID to a text string.
- **Tooling**: Requires a TLK Editor (e.g., DA2 TLK Editor).

---

## 6. Cross-Engine Comparison
Similar to Dragon Age: Origins, DA2 uses the Eclipse engine, meaning the `.tlk` and `.erf` formats are highly similar. Tools for DAO often work or have DA2 versions.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
**Font Pipeline:**
1. Unpack `originsfont.erf` using ERFEditor.
2. Edit the font textures (`.dds`) and layout files (`.fnt` or `.xml`).
3. Repack into `.erf`.

**Text Pipeline:**
1. Use a TLK tool to convert `campaign_base_en-us.tlk` to XML/TXT.
2. Translate the text.
3. Convert back to `.tlk`.

---

## 8. Troubleshooting
- **Thai vowels/tone marks misaligned (สระลอย)**: Since it's likely a bitmap font, you will need to pre-adjust the glyphs or use a text-shaper to map Thai characters to specific pre-combined glyphs in the font texture.
- **Text not appearing**: Ensure the TLK file is correctly encoded and IDs match.

---

## 9. Required Tools
| Tool | Purpose | Source |
|---|---|---|
| ERFEditor / Gibbed.Bioware.Erf | Extract/Pack .erf | NexusMods / GitHub |
| DA2 TLK Editor | Edit .tlk files | NexusMods |

---

## 10. Extracted Assets
- [EXTRACTION_NOTE.txt](Assets/Fonts/EXTRACTION_NOTE.txt)


## 11. 🤖 M2M Protocol (Automated Font Creation)
Since this game relies on bitmap fonts, here is the automated protocol for AI agents to generate Thai fonts without human intervention.

### Automated Font Rendering Script (Python)
```python
from PIL import Image, ImageDraw, ImageFont
import struct

def generate_bitmap_font(ttf_path, out_dds_path, char_list):
    # Setup image
    img_size = 2048
    img = Image.new('RGBA', (img_size, img_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(ttf_path, 32)
    
    x, y = 0, 0
    line_height = 40
    
    mapping = []
    
    for char in char_list:
        bbox = draw.textbbox((x, y), char, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        
        if x + w > img_size:
            x = 0
            y += line_height
            
        draw.text((x, y), char, font=font, fill=(255, 255, 255, 255))
        mapping.append({'char': char, 'x': x, 'y': y, 'w': w, 'h': h})
        
        x += w + 2
        
    img.save(out_dds_path.replace('.dds', '.png'))
    # Use external tool like texconv to convert PNG to DDS
    return mapping
```

### Automated Text Shaping Script (Regex)
```python
import re

def shape_thai_text(text):
    # Simplified shaping logic for converting standard Thai to pre-composed glyphs
    # Replace PHO PHAN + SARA I + MAI EK with a specific private use area char
    text = re.sub(r'พี่', '\uE001', text)
    return text
```

### Automated FNT/Mapping Injector (Struct)
```python
def inject_fnt_mapping(fnt_path, mapping):
    with open(fnt_path, 'r+b') as f:
        # Example: seek to mapping table offset
        f.seek(0x100)
        for char_info in mapping:
            # pack: char_code (I), x (H), y (H), width (H), height (H)
            data = struct.pack('<IHHHH', ord(char_info['char']), char_info['x'], char_info['y'], char_info['w'], char_info['h'])
            f.write(data)
```
