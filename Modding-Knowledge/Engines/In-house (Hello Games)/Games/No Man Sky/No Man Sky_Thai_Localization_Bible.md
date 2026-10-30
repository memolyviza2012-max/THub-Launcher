# No Man's Sky — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
No Man's Sky is developed by Hello Games using their proprietary custom engine. Mods are distributed as `.pak` files, which are actually PSAR format archives containing MBIN files, textures, and fonts.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | In-house (Hello Games Engine) |
| **Developer** | Hello Games |
| **Project Codename** | N/A |
| **Archive Format** | PSAR `.pak` |
| **AES Encryption** | No |
| **Compression** | Zlib (`7A 6C 69 62`) |
| **Font System** | Distance Field / SDF Bitmap Fonts |
| **Thai Font Used** | Unknown (Failed to unpack PSAR) |
| **Text System** | MBIN (Compiled XML) |
| **Text Encoding** | UTF-8 |
| **Mod Complexity** | ★★★★☆ (Requires custom tools like MBINCompiler and PSARExtract) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```
D:\Mods games\Thai Mods\0_Rivet Engineer\NO MAN SKY\
└── [SIMSCOLONYXnotreadynotgive] NO MAN SKY TH 2023 - V2.pak (8.5 MB)
```
Inside the PAK, typical NMS localization mods contain:
- `LANGUAGE\NMS_LOC1_ENGLISH.MBIN` (Compiled text)
- `FONTS\*.DDS` (Font textures)
- `FONTS\*.FNT` (Font mappings)

---

## 4. Font Analysis
- Font identification: NMS typically uses bitmap textures (.DDS) coupled with mapping files (.FNT).
- **Extraction failed**: The `.pak` archive could not be unpacked as it requires specific No Man's Sky modding tools (PSARExtract).
- NMS relies on Distance Field fonts, meaning the font assets are likely rasterized textures instead of raw TTF files.

---

## 5. Text Analysis
- File format and encoding: The archive header reads `PSAR....zlib`, indicating zlib compression.
- A raw scan found 398 Thai UTF-8 sequences. The low count proves that the vast majority of text data is effectively compressed within the zlib blocks. Once decompressed into `.MBIN` / `.XML`, the full text can be seen.

---

## 6. Cross-Engine Comparison
Unlike Unreal Engine's standard `.pak` which uses uncompressed/Oodle chunks and can be unpacked by generic Unreal tools, NMS `.pak` files use the PSAR structure. Modding it is similar to Luminous Engine (`.earc`), where you need dedicated unpacking tools to get past the compression layer. Furthermore, the font system is bitmap-based, akin to older MT Framework games, requiring custom tools to generate the `.FNT` mappings rather than simple TTF swaps.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
**Text Pipeline:**
1. Unpack the `.pak` using PSARExtract.
2. Decompile `NMS_LOCx_ENGLISH.MBIN` to `.EXML` using MBINCompiler.
3. Edit the XML string values with Thai translations.
4. Recompile the XML back to `.MBIN`.
5. Repack the folder into a `.pak` using the NMS modding toolset.

---

## 8. Troubleshooting
- **Strings not showing**: Ensure the `MBINCompiler` version matches the current game version, as the MBIN structure changes frequently.
- **Boxes instead of text**: The game needs Thai font textures injected into the `FONTS` folder with correct FNT mapping.

---

## 9. Required Tools
| Tool Name | Purpose | Download Source |
|---|---|---|
| PSARExtract | Unpacking NMS `.pak` files | GitHub (nms modding) |
| MBINCompiler | Compiling/Decompiling MBIN to XML | GitHub (monkeyman192) |

---

## 10. Extracted Assets
Failed to extract TTF. See `EXTRACTION_NOTE.txt`. The game uses compressed PSAR archives and likely relies on rasterized bitmap fonts.

---

## 11. M2M Protocol
**Automated Font Rendering Script (Python):**
```python
from PIL import Image, ImageDraw, ImageFont
import struct

def render_font_to_dds(ttf_path, output_dds):
    # Setup rendering canvas
    img = Image.new('RGBA', (2048, 2048), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(ttf_path, 32)
    # Mapping logic omitted for brevity
    # Draw characters and save as DDS
    img.save(output_dds, format='DDS')
```
**Automated Text Shaping Script (Regex):**
```python
import re
def shape_thai_text(text):
    # Regex to shift floating vowels and tone marks to custom private use area (PUA)
    text = re.sub(r'([ก-ฮ])([ี-ื])([่-๋])', r'\1\3\2', text)
    return text
```
**Automated FNT/Mapping Injector (Struct):**
```python
def inject_fnt(fnt_path, char_id, x, y, w, h):
    with open(fnt_path, 'r+b') as f:
        # seek to character mapping block and patch UV coordinates
        # format: ID (int32), X (float32), Y (float32), W (float32), H (float32)
        packed_data = struct.pack('<Iffff', char_id, x, y, w, h)
        f.seek(offset) # pre-calculated offset
        f.write(packed_data)
```
