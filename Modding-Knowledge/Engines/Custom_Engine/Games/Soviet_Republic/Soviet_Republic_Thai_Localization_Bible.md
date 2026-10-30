# Workers & Resources: Soviet Republic — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Workers & Resources: Soviet Republic is a city-builder game developed by 3Division running on a Custom Engine. The Thai localization mod architecture pattern is **File Replacement**, directly replacing font resources and custom binary text files (.btf) without any archive extraction needed.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Custom Engine |
| **Developer** | 3Division |
| **Project Codename** | N/A |
| **Archive Format** | None (Loose Files) |
| **AES Encryption** | N/A |
| **Compression** | None |
| **Font System** | Bitmap Font (BMFont + DDS) |
| **Thai Font Used** | PK Pi Mai Medium |
| **Text System** | Custom Binary Text Format (.btf) |
| **Text Encoding** | UTF-16 BE (Big Endian) |
| **Mod Complexity** | ★★★☆☆ (Requires parsing custom BTF format for text, and generating BMFont + DDS for fonts) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```text
Soviet Republic\
├── media_soviet\
│   ├── sovietEnglish.btf      (965 KB - String table containing English and translated Thai text)
│   ├── sovietKorean.btf       (862 KB - String table containing Korean and translated Thai text)
│   └── fontsbitmap\
│       ├── font_config.ini    (Font configuration file for original sizes)
│       ├── font_config_kr.ini (Korean font config mapping various fonts to Thai.fnt)
│       ├── EXPORT.txt         (Developer's notes on BMFont generation)
│       └── data\
│           ├── Thai.fnt       (7 KB - BMFont binary format glyph definitions)
│           ├── Thai_0.dds     (262 KB - Font atlas texture page 0)
│           ├── Thai_1.dds     (262 KB - Font atlas texture page 1)
│           └── Font.rar       (28 KB - Backup containing Thai.fnt and DDS files)
```

---

## 4. Font Analysis
- **Font Format**: The game uses BMFont binary format version 3 for glyph metadata (`.fnt`), and DDS textures for the font atlas (`.dds`).
- **Font Identification**: The internal font name is `PK Pi Mai Medium`, as discovered in the BMFont binary header magic string.
- **How fonts are stored**: They are loose files in `media_soviet\fontsbitmap\data\`. No vector (TTF/OTF) data is shipped with the mod, only rasterized bitmaps.
- **Font Swap Mapping**: Modders map original fonts (like Arial, Square, Courier) to the Thai font inside `font_config_kr.ini` by specifying `binary "Thai.fnt"`.
- **Thai Rendering Considerations**: Since it's a pre-rendered BMFont, Thai rendering (สระลอย, วรรณยุกต์) will rely on pre-composed glyphs or adjusting baseline shifts. There is no runtime text shaping. The `font_config_kr.ini` adjusts `y_adj` parameters (e.g., `-0.07` to `-0.15`) for the font faces to align Thai text properly on screen.

---

## 5. Text Analysis
- **File Format**: The text strings are stored in custom `.btf` (Binary Text Format) files (e.g. `sovietEnglish.btf`).
- **Encoding**: The text strings are encoded in **UTF-16 BE (Big Endian)**. This is crucial—most games use UTF-8 or UTF-16 LE, but this Custom Engine expects Big Endian.
- **Structure**: The file contains a binary header (starting with `00 00 1D ...`) with string offsets or lengths, followed by the UTF-16 BE text buffer at the end of the file. 

---

## 6. Cross-Engine Comparison
This engine’s approach to fonts (BMFont + DDS) is similar to MT Framework (e.g., *Dragon's Dogma*, *Resident Evil 5*) and Luminous Engine (*Final Fantasy XV*), where the font is pre-rasterized. However, unlike Luminous which uses Zlib/EARC compression, this Custom Engine uses entirely loose files, which makes modifying the files much easier. The text encoding, UTF-16 BE, is relatively rare for PC games but occasionally found in older console ports or specific custom engines (unlike Unity's UTF-8 or UE's typical UTF-16 LE).

---

## 7. Pipeline — ขั้นตอนสร้างม็อด

### Font Pipeline
1. Acquire a Thai TTF font (e.g., `PK Pi Mai Medium`).
2. Use BMFont Generator (AngelCode) to generate a binary `.fnt` file (Version 3) and DDS texture pages for the Thai characters.
3. Name the files `Thai.fnt`, `Thai_0.dds`, `Thai_1.dds`, etc.
4. Place them in `media_soviet\fontsbitmap\data\`.
5. Edit `media_soviet\fontsbitmap\font_config_kr.ini` (or the respective language config) to map existing fonts to `Thai.fnt` and tweak `y_adj` if needed.

### Text Pipeline
1. Since `.btf` is a custom format, you need a custom script to parse the binary header and extract the UTF-16 BE strings.
2. Translate the extracted strings.
3. Repack the translated strings using UTF-16 BE encoding.
4. Rebuild the `.btf` header offsets/lengths to match the new string buffer size.
5. Replace `sovietEnglish.btf` or `sovietKorean.btf` with your modified file.

---

## 8. Troubleshooting
- **Thai characters look like squares or spaces**: Ensure the `.btf` file is strictly encoded in UTF-16 **Big Endian**. If saved as Little Endian, the bytes will be swapped, causing the game to look up wrong glyphs.
- **Font characters are misaligned or overlapping**: Check the `y_adj` values in `font_config.ini` or the BMFont y-offsets in `Thai.fnt`.
- **สระลอย (Floating Vowels)**: Because this is BMFont, you must handle Thai text shaping *before* packing the text into `.btf`, using a script to replace standard Thai strings with PUA (Private Use Area) pre-composed characters, and ensuring those PUA characters are generated in the BMFont.

---

## 9. Required Tools
| Tool Name | Purpose | Download |
|---|---|---|
| **BMFont** | Generating binary `.fnt` and `.dds` font textures | [AngelCode](https://www.angelcode.com/products/bmfont/) |
| **Hex Editor** (e.g. HxD) | Analyzing and modifying the `.btf` header | [HxD](https://mh-nexus.de/en/hxd/) |
| **Custom Python Script** | Parsing and rebuilding the `.btf` binary string table | - |

---

## 10. Extracted Assets
- **[EXTRACTION_NOTE.txt](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Custom_Engine/Games/Soviet_Republic/Assets/Fonts/EXTRACTION_NOTE.txt)**: Font extraction to TTF/OTF failed because the game uses pre-rendered BMFont DDS atlases. Read the note for more details.

---

## 11. 🤖 M2M Protocol
**(Automated Font Rendering & Text Shaping for Bitmap Fonts)**

Since this Custom Engine uses Bitmap Fonts (BMFont + DDS) and lacks native runtime text shaping for Thai, AI agents must execute the following automated steps to generate functional mods.

### 11.1 Automated Font Rendering Script (Python + Pillow)
To create `Thai_0.dds` and `Thai_1.dds` without GUI tools:
```python
from PIL import Image, ImageDraw, ImageFont
import struct

def generate_bitmap_font(ttf_path, output_dds_prefix, output_fnt):
    font_size = 64
    font = ImageFont.truetype(ttf_path, font_size)
    atlas_size = (2048, 2048)
    image = Image.new("RGBA", atlas_size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    
    # Track coordinates for characters
    chars = "กขฃคฅฆงจฉชซฌญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรฤลฦวศษสหฬอฮฯะัาำิีึืฺุู฿เแโใไๅๆ็่้๊๋์ํ"
    x, y = 0, 0
    max_h = 0
    char_metadata = []
    
    for char in chars:
        bbox = draw.textbbox((0, 0), char, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        
        if x + w > atlas_size[0]:
            x = 0
            y += max_h + 2
            max_h = 0
            
        draw.text((x, y), char, font=font, fill=(255, 255, 255, 255))
        char_metadata.append((ord(char), x, y, w, h))
        
        x += w + 2
        max_h = max(max_h, h)
        
    # Save as PNG first, then convert to DDS DXT5 using external CLI if needed
    image.save(f"{output_dds_prefix}_0.png")
    
    # Generate .fnt binary (Version 3)
    with open(output_fnt, "wb") as f:
        # BMF\x03 header
        f.write(b'BMF\x03')
        # Info block (Block 1)
        f.write(b'\x01')
        font_name = b"PK Pi Mai Medium\x00"
        f.write(struct.pack('<I', 14 + len(font_name)))
        f.write(struct.pack('<HbbbbbbbB', font_size, 0, 0, 0, 0, 0, 0, 0, 0))
        f.write(b'\x00'*4)
        f.write(font_name)
        
        # Char Block (Block 4)
        f.write(b'\x04')
        f.write(struct.pack('<I', len(char_metadata) * 20))
        for cid, cx, cy, cw, ch in char_metadata:
            # id(4), x(2), y(2), width(2), height(2), xoffset(2), yoffset(2), xadvance(2), page(1), chnl(1)
            f.write(struct.pack('<IHHHHhhHBB', cid, cx, cy, cw, ch, 0, 0, cw, 0, 15))
```

### 11.2 Automated Text Shaping Script (Regex)
Use regular expressions to correct floating vowels (สระลอย) by mapping them to PUA (Private Use Area) before saving to `.btf`.
```python
import re

def shape_thai_text(text):
    # Example rule: ป + ี + ่ -> ป + ี (PUA 1) + ่ (PUA 2)
    # Define mapping dictionary
    mapping = {
        'ปิ': 'ป\uE001',
        'ปี': 'ป\uE002',
        # Add other combinations
    }
    
    for k, v in mapping.items():
        text = text.replace(k, v)
        
    return text
```

### 11.3 Text Packing (UTF-16 BE)
When generating the `.btf`, always encode the modified string as `utf-16-be`.
```python
def encode_to_btf(text):
    shaped_text = shape_thai_text(text)
    return shaped_text.encode('utf-16-be')
```
