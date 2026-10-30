# Resident Evil 2 (1998) — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Resident Evil 2 (1998) is a classic PC port of the survival horror game by Capcom. The Thai localization utilizes the "Runtime Injection (Overlay)" pattern, specifically relying on the **Classic REbirth** patch (a custom `ddraw.dll` hook). This patch intercepts text rendering and asset loading at runtime, allowing modern XML-based text overriding.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Classic RE Engine (PC Port via Classic REbirth) |
| **Developer** | Capcom / Modder (Gemini / Classic REbirth) |
| **Project Codename** | Biohazard 2 |
| **Archive Format** | Loose XML files and .webp images |
| **AES Encryption** | No |
| **Compression** | None |
| **Font System** | DirectDraw overlay injection / High-res texture substitution |
| **Thai Font Used** | Unknown (Sprite based, loaded via REbirth mapping) |
| **Text System** | Loose XML files (Classic REbirth format) |
| **Text Encoding** | Custom mapped hex values (e.g., 0xA2-0xE4 for Thai) |
| **Mod Complexity** | ★★☆☆☆ (Easily modifiable via XML) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```
Resident_Evil_2_1998/RE2Tha_1998/
├── ddraw.dll (3.4 MB) - Classic REbirth runtime hook
├── hires/
│   ├── bgd/
│   └── misc/ (178 .webp images, high-res UI/font elements)
├── mod_thai/
│   ├── encoding.xml (9.2 KB) - Custom character mapping
│   ├── system.xml, item.xml, interact.xml... - Text repositories
│   └── pl0/, pl1/
└── pl0/, pl1/
```

---

## 4. Font Analysis
- **Font Identification:** No standard TTF/OTF vector fonts. Classic REbirth hooks the game's original pixel font rendering and redirects it to high-res `.webp` textures or modifies the sprite memory.
- **How fonts are stored:** Fonts are rendered as 2D sprites.
- **Thai rendering considerations:** In the original game, text is 1-byte per character. The Thai mod cleverly replaces the unused extended ASCII space (0xA2 to 0xE4) in `encoding.xml` with Thai Unicode characters. สระลอย (floating vowels) and วรรณยุกต์ (tone marks) are handled by shifting them and modifying their `indent` and `width` properties in `encoding.xml` to render correctly over consonants.

---

## 5. Text Analysis
- **File format and encoding:** Standard XML files (`system.xml`, `item.xml`, etc.) containing the localized strings.
- **How text is structured:** Structured by categories (e.g., `<Text ID="X">Translated String</Text>`). The `encoding.xml` file explicitly maps hex codes (like `0xA2`) to Thai characters (`ก`), dictating exactly how the `ddraw.dll` engine maps strings to font sprite indices.
- **Approximate string count:** Fully covers the script of RE2 (Leon and Claire scenarios).

---

## 6. Cross-Engine Comparison
Compared to modern engines (Unity/Unreal), Classic REbirth transforms an archaic, hardcoded binary text system into a modern, data-driven XML format. Instead of hex-editing executable files or proprietary `.dat`/`.bin` archives, modders can simply edit plain text XML files. The custom `encoding.xml` feature mirrors Unity's string table flexibility, albeit constrained by 256-character limits per font page.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
**Font Pipeline:**
1. Locate the UI/font texture files in the `hires/misc` folder (in `.webp` format).
2. Edit the texture sprite sheet to include Thai glyphs.
3. Update `mod_thai/encoding.xml` to map hex ID values to the corresponding new Thai characters, carefully adjusting `width` and `indent` attributes so vowels float correctly above consonants.

**Text Pipeline:**
1. Open the `.xml` files in `mod_thai/` (e.g., `item.xml`).
2. Translate the text directly inside the XML tags. Because `ddraw.dll` processes UTF-8 XML and translates it through `encoding.xml`, you can write raw Thai strings directly in the XML!
3. Launch the game; Classic REbirth dynamically loads the new XMLs.

---

## 8. Troubleshooting
- **Thai vowels/tone marks misaligned:** Adjust the `width` and `indent` parameters for the specific character (e.g., `่`, `้`, `ี`) in `encoding.xml`. Example: `<Entry Encode="0xE0" Char="ี" width="0" indent="5"/>`.
- **Text bleeding off-screen:** The classic engine has rigid line-break limits. Manually insert line breaks or shorten translated strings.

---

## 9. Required Tools
| Tool | Purpose | Source |
|---|---|---|
| Classic REbirth | Modding API and DirectDraw patch | Gemini's website |
| Text Editor | Editing XML files | VSCode, Notepad++ |
| Image Editor | Editing `.webp` textures | Photoshop, GIMP |

---

## 10. Extracted Assets
The font used in this mod is a pre-rendered bitmap texture/sprite sequence patched at runtime, not a TTF/OTF vector font.
[EXTRACTION_NOTE.txt](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Classic_RE/Games/Resident_Evil_2/Assets/Fonts/EXTRACTION_NOTE.txt)

---

## 11. 🤖 PHASE 7: MACHINE-TO-MACHINE (M2M) PROTOCOL
**(สำหรับ AI Agent ที่ต้องการนำคัมภีร์ไปรันสร้างม็อดอัตโนมัติ)**

เกม RE2 Classic (ร่วมกับ Classic REbirth) จัดการฟอนต์ผ่านไฟล์รูปภาพ (WebP) และ `encoding.xml` 

### 1. Automated Font Rendering Script (Python)
```python
from PIL import Image, ImageDraw, ImageFont

def create_re2_font_webp(ttf_path, output_webp):
    # สร้าง sprite sheet แบบโปร่งใส
    img = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(ttf_path, 16)
    
    # วาดตัวอักษรไทยเรียงกันเพื่อไปแทนที่ใน .webp 
    # (จำเป็นต้องทราบ Layout ของ REbirth font atlas)
    # ...
    img.save(output_webp, 'WEBP')
```

### 2. Automated Text Shaping Script (Regex)
```python
import xml.etree.ElementTree as ET

def auto_generate_encoding_xml(output_xml):
    root = ET.Element("Encoding", width="7")
    
    # Map ก-ฮ
    base_hex = 0xA2
    thai_chars = "กขฃคฅฆงจฉชซฌญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรลวศษสหฬอฮ"
    for i, char in enumerate(thai_chars):
        ET.SubElement(root, "Entry", Encode=f"0x{base_hex+i:02X}", Char=char)
        
    # Map สระลอยและปรับ indent/width อัตโนมัติ
    vowel_hex = 0xD8
    vowels = [('่', 0, 2), ('้', 0, 4), ('ี', 0, 5)]
    for i, (char, w, ind) in enumerate(vowels):
        ET.SubElement(root, "Entry", Encode=f"0x{vowel_hex+i:02X}", Char=char, width=str(w), indent=str(ind))
        
    tree = ET.ElementTree(root)
    tree.write(output_xml, encoding="utf-8")
```
