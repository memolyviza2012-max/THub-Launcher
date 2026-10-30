# Resident Evil 0 HD Remaster — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Resident Evil 0 HD Remaster is a classic survival horror game remastered by Capcom. It runs on the MT Framework engine. The Thai localization mod architecture utilizes the "File Replacement" pattern, overwriting the original `.arc` archives within the `nativePC` directory.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | MT Framework |
| **Developer** | Capcom |
| **Project Codename** | Unknown |
| **Archive Format** | `.arc` (MT Framework Archive) |
| **AES Encryption** | No |
| **Compression** | Zlib |
| **Font System** | Bitmap (.tex + .fnt/font inside .arc) |
| **Thai Font Used** | Unknown (Bitmap texture, no TTF metadata) |
| **Text System** | Binary `.msg` embedded inside `.arc` |
| **Text Encoding** | UTF-8 |
| **Mod Complexity** | ★★★☆☆ (Requires MT Framework .arc/.msg toolchain like arctool) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```
Resident_Evil_1/RE0Tha/
├── วิธีติดตั้ง.txt
└── nativePC/
    └── arc/
        ├── message/
        │   └── msg_eng.arc (195 KB)
        └── ui/
            ├── asia/
            │   └── (23 .arc files, 73KB - 4MB)
            └── rdt/
                └── (46 .arc files, ~68-92KB each)
```

---

## 4. Font Analysis
- **Font Identification:** No TrueType/OpenType font files exist in the mod folder. MT Framework games use rasterized bitmap fonts.
- **How fonts are stored:** Fonts are packed as `.tex` (texture atlas) and `.fnt` / `.font` (glyph mapping) inside the `.arc` files located in the `nativePC/arc/ui` directory.
- **Thai rendering considerations:** Since it uses a bitmap texture atlas, Thai vowels (สระลอย) and tone marks (วรรณยุกต์) must be pre-rendered onto the sprite sheet and manually mapped to UV coordinates in the `.fnt` file, or text must be pre-shaped (swapping upper/lower vowels with special unused ASCII slots).

---

## 5. Text Analysis
- **File format and encoding:** MT Framework uses a proprietary `.msg` format packed inside `.arc` archives. The `.msg` files use UTF-8 encoding.
- **How text is structured:** Binary format containing header, string offsets, and string data.
- **Approximate string count:** Thousands of strings spread across multiple `.arc` files (`msg_eng.arc` for main messages, `cos_XX.arc` for specific items/rooms, etc.)

---

## 6. Cross-Engine Comparison
Compared to Unreal Engine (which uses dynamic `.ufont` and `.locres`), MT Framework is much older and strictly relies on pre-compiled bitmap fonts and static binary message files (`.msg`). This is similar to Luminous Engine's `.tex` + `.font` architecture, where no dynamic TTF rendering is possible at runtime without engine hooking.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
**Font Pipeline:**
1. Unpack `.arc` files containing UI/Fonts using `arctool` (or similar MT Framework tools).
2. Convert `.tex` to `.dds` and edit the font atlas to include Thai characters.
3. Edit the `.fnt` (or `.font`) mapping file using a hex editor or custom script to update the UV coordinates and width/height for the new Thai glyphs.
4. Repack the `.arc` file.

**Text Pipeline:**
1. Unpack `msg_eng.arc` and other `.arc` files using `arctool`.
2. Convert the internal `.msg` files to plaintext (e.g., `.txt` or `.csv`) using an MT Framework `.msg` tool.
3. Translate the text to Thai, applying a Text Shaping script to handle Thai vowels and tone marks (สระลอย) if the font engine does not support dynamic shaping.
4. Convert the text back to `.msg` and repack the `.arc` file.

---

## 8. Troubleshooting
- **Thai vowels/tone marks misaligned (สระลอย):** Ensure your Text Shaping script maps the tone marks to the correct custom glyphs in the `.tex` atlas, and that the UV coordinates in the `.fnt` file match the texture exactly.
- **Game crash after mod installation:** The `.arc` archive might be improperly packed (e.g., incorrect Zlib compression or broken offset tables). Use the correct `arctool` configuration for MT Framework.
- **Missing characters:** The `.fnt` mapping might not include the Unicode range for Thai characters. You must override unused Latin/Symbol ranges if extending the mapping is not supported.

---

## 9. Required Tools
| Tool | Purpose | Source |
|---|---|---|
| arctool | Unpacking and packing MT Framework `.arc` and `.tex` files | Fluffyquack's tools |
| msg tool | Converting MT Framework `.msg` to editable text | Various modding forums |
| Image Editor | Editing `.dds` texture atlases (e.g., Photoshop) | N/A |

---

## 10. Extracted Assets
The font used in this mod is a pre-rendered bitmap texture inside an `.arc` archive, not a TTF/OTF vector font.
[EXTRACTION_NOTE.txt](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/MT_Framework/Games/Resident_Evil_0/Assets/Fonts/EXTRACTION_NOTE.txt)

---

## 11. 🤖 PHASE 7: MACHINE-TO-MACHINE (M2M) PROTOCOL
**(สำหรับ AI Agent ที่ต้องการนำคัมภีร์ไปรันสร้างม็อดอัตโนมัติ)**

เนื่องจาก Resident Evil 0 HD Remaster ใช้เอนจิน MT Framework ที่อาศัยระบบ Bitmap Font (ไม่มี TTF ให้รันไทม์) หากต้องการสร้างม็อดอัตโนมัติ ให้ใช้ Script โครงสร้างต่อไปนี้:

### 1. Automated Font Rendering Script (Python)
```python
from PIL import Image, ImageDraw, ImageFont

def render_thai_bitmap(font_path, output_path):
    # สร้าง Sprite Sheet ขนาด 1024x1024
    img = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font_path, 24)
    
    thai_chars = [chr(i) for i in range(0x0E01, 0x0E5B)]
    # ... โค้ดคำนวณและวาดลง Grid x, y
    img.save(output_path) # บันทึกเป็น PNG แล้วแปลงเป็น .dds / .tex ภายหลัง
```

### 2. Automated Text Shaping Script (Regex)
```python
import re

def shape_thai_text(text):
    # เลื่อนวรรณยุกต์ที่ซ้อนทับให้ไปใช้รหัสพิเศษบน Bitmap
    text = re.sub(r'([ปฝฟ])([ิีึื])([่้๊๋])', r'\1\2\3_shifted', text)
    # ... สร้าง dictionary map ไปยัง Unicode PUA หรือ Slot ว่าง
    return text
```

### 3. Automated FNT/Mapping Injector (Struct)
```python
import struct

def inject_fnt_mapping(fnt_path, char_id, x, y, w, h):
    with open(fnt_path, 'r+b') as f:
        # ข้าม Header ไปที่ตำแหน่งตาราง Character
        f.seek(HEADER_OFFSET + (char_id * ENTRY_SIZE))
        # MT Framework font mapping (ตัวอย่าง 16 bytes: id, uv_x, uv_y, w, h, etc.)
        packed = struct.pack('<Hffff', char_id, x, y, w, h)
        f.write(packed)
```
