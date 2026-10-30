# Fallout: New Vegas — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Fallout: New Vegas uses the Gamebryo engine (an early version of what became the Creation Engine) by Obsidian Entertainment and Bethesda. The mod architecture pattern is **File Replacement** and **Plugin Injection**, primarily relying on modified `.esp` (Elder Scrolls Plugin) files and custom bitmap font textures.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Gamebryo / Creation Engine |
| **Developer** | Obsidian Entertainment / Bethesda Softworks |
| **Project Codename** | Vegas |
| **Archive Format** | `.esp` (Magic: `TES4`) |
| **AES Encryption** | N/A |
| **Compression** | Zlib / Raw |
| **Font System** | Bitmap (.fnt + .tex) |
| **Thai Font Used** | Unknown (Rasterized into bitmap) |
| **Text System** | Binary embedded in `.esp` records |
| **Text Encoding** | Windows-874 / TIS-620 |
| **Mod Complexity** | ★★★☆☆ (Requires .esp editors and bitmap font generation) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```text
D:\Mods games\Thai Mods\0_Rivet Engineer\FnV\FNV_Thai_Translation_v2\
├── Data\
│   ├── FalloutNV_Thai.esp (10 MB - Main Translation Plugin)
│   ├── DeadMoney_Thai.esp (1.3 MB)
│   ├── HonestHearts_Thai.esp (690 KB)
│   ├── OldWorldBlues_Thai.esp (973 KB)
│   ├── LonesomeRoad_Thai.esp (494 KB)
│   ├── GunRunnersArsenal_Thai.esp (13 KB)
│   └── Textures\Fonts\
│       ├── NVFontmai33.fnt / .tex (1 MB)
│       ├── NVFontmaitermi.fnt / .tex (1 MB)
│       └── ... (Total 7 font pairs)
└── INI\
    ├── Fallout.ini (Modified to load new fonts)
    └── FalloutPrefs.ini
```

---

## 4. Font Analysis
- The fonts in Gamebryo are split into `.fnt` (XML-like or binary coordinate data) and `.tex` (bitmap texture).
- The `.tex` files contain the rasterized glyphs. Magic `00 02 00 00` indicates a specialized texture format (likely a DXT5 or raw 8-bit alpha).
- The `.fnt` files (Magic: `00 00 0C 42`) store character UV mappings.
- The fonts are pre-rendered so Thai rendering issues like floating vowels (สระลอย) must be solved at the text-shaping level before being mapped to the bitmap.

---

## 5. Text Analysis
- All in-game text (dialogue, UI, items) is stored inside the `.esp` files.
- The strings use Windows-874 (TIS-620) encoding to fit Thai characters into the single-byte ANSI encoding expected by the engine.
- Approximate string count is massive (FalloutNV_Thai.esp is 10MB, translating thousands of records).

---

## 6. Cross-Engine Comparison
Unlike modern Unreal Engine 4/5 games (which use `.locres` and true-type `.ufont` files), Gamebryo relies on monolithic plugin files (`.esp`/`.esm`) that contain both text and game logic, alongside primitive bitmap fonts. This is identical to older Bethesda titles like Oblivion, Fallout 3, and Skyrim (pre-Special Edition). 

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
**Font Pipeline:**
1. Generate a bitmap texture containing Thai glyphs.
2. Create/edit the `.fnt` file to map the UV coordinates of each character on the texture.
3. Update `Fallout.ini` under `[Fonts]` to point to the new `.fnt` files.

**Text Pipeline:**
1. Use xEdit (FNVEdit) or a dedicated `.esp` translation tool.
2. Shape the Thai text (combining floating vowels) and encode it as Windows-874.
3. Inject the strings into the appropriate `.esp` records.

---

## 8. Troubleshooting
- **Font not displaying:** Ensure the `.ini` file correctly references the `.fnt` files. Check if ArchiveInvalidation is required.
- **Thai vowels/tone marks misaligned (สระลอย):** The text in the `.esp` wasn't properly shaped for the custom font map. Ensure text is shaped before injecting.
- **Encoding corruption:** Gamebryo expects ANSI (Windows-1252 usually). Ensure your system locale or the injection tool isn't re-encoding to UTF-8.

---

## 9. Required Tools
| Tool | Purpose | Source |
|---|---|---|
| xEdit (FNVEdit) | Edit `.esp` files | NexusMods |
| ESP-Esm Translator | Bulk translate text | NexusMods |
| Bitmap Font Generator | Create `.fnt` / `.tex` pairs | Custom / BMFont |

---

## 10. Extracted Assets
Extraction of `.ttf`/`.otf` failed because the fonts are stored as rasterized bitmaps (`.tex`). 
See `EXTRACTION_NOTE.txt` in the Assets folder.

---

## 11. M2M Protocol
**Automated Font Rendering Script (Python):**
```python
from PIL import Image, ImageDraw, ImageFont

def render_thai_font_to_bitmap(ttf_path, output_path, font_size=32):
    font = ImageFont.truetype(ttf_path, font_size)
    chars = "กขฃคฅฆงจฉชซฌญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรฤลฦวศษสหฬอฮฯะัาำิีึืฺุูเแโใไๅๆ็่้๊๋์ํ"
    
    img_width, img_height = 1024, 1024
    img = Image.new("RGBA", (img_width, img_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    x, y = 0, 0
    for char in chars:
        bbox = font.getbbox(char)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text((x, y), char, font=font, fill="white")
        x += w + 2
        if x > img_width - font_size:
            x = 0
            y += font_size + 2
            
    img.save(output_path, "DDS") # Or specific .tex format converter
```

**Automated Text Shaping Script (Regex):**
```python
import re

def shape_thai_text(text):
    # Example: Shift upper vowels to a different code point for the custom font
    text = re.sub(r'([ปฝฟ])([ิีึื])', r'\1' + chr(0xF701), text) # Custom code point
    return text.encode('cp874')
```

**Automated FNT/Mapping Injector (Struct):**
```python
import struct

def inject_fnt(fnt_path, char_id, x, y, width, height):
    with open(fnt_path, 'r+b') as f:
        f.seek(0x20 + (char_id * 16)) # Example offset
        data = struct.pack('<ffff', x, y, width, height)
        f.write(data)
```
