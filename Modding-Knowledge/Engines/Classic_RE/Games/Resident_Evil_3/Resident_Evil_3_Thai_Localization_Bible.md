# Resident Evil 3 (1999) — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Resident Evil 3 (1999) is a classic PC survival horror game by Capcom. Similar to RE2, the Thai localization relies entirely on the **Classic REbirth** patch (`ddraw.dll` and `dinput8.dll`). This "Runtime Injection (Overlay)" architecture hooks into the game's legacy rendering pipeline to load external XML-based text and high-res sprite fonts.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Classic RE Engine (PC Port via Classic REbirth) |
| **Developer** | Capcom / Modder (Gemini / Classic REbirth) |
| **Project Codename** | Biohazard 3 |
| **Archive Format** | Loose XML files and .webp images |
| **AES Encryption** | No |
| **Compression** | None |
| **Font System** | DirectDraw overlay injection / High-res texture substitution |
| **Thai Font Used** | Unknown (Sprite based, loaded via REbirth mapping) |
| **Text System** | Loose XML files (`xml/` folder) |
| **Text Encoding** | Custom mapped hex values |
| **Mod Complexity** | ★★☆☆☆ (Easily modifiable via XML) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```
Resident_Evil_3_1999/RE3Tha_1999/
├── ddraw.dll (4.6 MB) - Classic REbirth hook
├── dinput8.dll (2.1 MB) - Input hook (often needed for RE3 REbirth)
├── hires/ - High resolution texture overrides
├── mod_thai/
│   ├── description.txt
│   ├── encoding.xml (10.5 KB) - Custom Thai character mapping
│   └── xml/
│       ├── system.xml, map.xml, prompt.xml... - Text repositories
│       └── rdt/
└── zmovie/ - FMV cutscenes
```

---

## 4. Font Analysis
- **Font Identification:** No standard TTF/OTF fonts. The game uses rasterized sprites replaced at runtime via Classic REbirth.
- **How fonts are stored:** Fonts are rendered as 2D sprites, typically stored as `.webp` in the `hires` directory or injected into the original `.tim` memory buffers.
- **Thai rendering considerations:** Handled via `encoding.xml`. The custom XML maps hex IDs (0xA2 onwards) to Thai characters, allowing the game's 1-byte text renderer to display Thai. `width` and `indent` attributes in the XML handle the complex spacing requirements of floating vowels (สระลอย) and tone marks (วรรณยุกต์).

---

## 5. Text Analysis
- **File format and encoding:** Standard XML files (e.g., `system.xml`, `prompt.xml`, `status_mapping.xml`).
- **How text is structured:** Structured by categories with text tags mapping to game IDs. 
- **Approximate string count:** Covers the entire RE3 scenario, mercs mode, and epilogues (`epilogue.xml`, `mercs.xml`).

---

## 6. Cross-Engine Comparison
The architecture is identical to Resident Evil 2's Classic REbirth mod. It provides a massive leap in moddability over traditional hex editing of `.RDT` files. Compared to modern MT Framework or Unreal Engine mods, this is significantly easier to translate as it abstracts the binary text formatting into plain XML.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
**Font Pipeline:**
1. Locate the UI/font texture files in the `hires` folder.
2. Edit the texture sprite sheet to include Thai glyphs.
3. Update `mod_thai/encoding.xml` to map the new glyphs and adjust their widths and indents for proper vertical alignment.

**Text Pipeline:**
1. Open the `.xml` files in `mod_thai/xml/` (e.g., `system.xml`).
2. Translate the text directly inside the XML tags using standard Thai text.
3. Classic REbirth will dynamically parse the XML and render it via the `encoding.xml` map.

---

## 8. Troubleshooting
- **Thai vowels/tone marks misaligned:** Fine-tune the `width` and `indent` parameters in `encoding.xml` for the specific problematic character.
- **Game crashes on load:** Ensure that the XML syntax is strictly valid. An unclosed tag in `prompt.xml` or `system.xml` will crash Classic REbirth.
- **"dinput8.dll" missing error:** RE3 Classic REbirth requires `dinput8.dll` in addition to `ddraw.dll` for modern controller and mouse support.

---

## 9. Required Tools
| Tool | Purpose | Source |
|---|---|---|
| Classic REbirth | Modding API and DirectDraw patch | Gemini's website |
| Text Editor | Editing XML files | VSCode, Notepad++ |
| Image Editor | Editing `.webp` textures | Photoshop, GIMP |

---

## 10. Extracted Assets
The font used in this mod is a pre-rendered bitmap texture/sprite sequence, not a TTF/OTF vector font.
[EXTRACTION_NOTE.txt](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Classic_RE/Games/Resident_Evil_3/Assets/Fonts/EXTRACTION_NOTE.txt)

---

## 11. 🤖 PHASE 7: MACHINE-TO-MACHINE (M2M) PROTOCOL
**(สำหรับ AI Agent ที่ต้องการนำคัมภีร์ไปรันสร้างม็อดอัตโนมัติ)**

เนื่องจากเป็น Classic REbirth โครงสร้างจึงเหมือนกับ RE2 ทุกประการ:

### 1. Automated Font Rendering Script (Python)
```python
from PIL import Image, ImageDraw, ImageFont

def create_re3_font_webp(ttf_path, output_webp):
    # สร้าง sprite sheet สำหรับ RE3 (Classic REbirth)
    img = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(ttf_path, 16)
    
    # วาดตัวอักษรไทยเรียงกันเพื่อไปแทนที่ใน .webp
    # ...
    img.save(output_webp, 'WEBP')
```

### 2. Automated Text Shaping Script (Regex)
(ใช้ร่วมกับ `auto_generate_encoding_xml` ของ RE2 ได้เลย เนื่องจากโครงสร้าง `encoding.xml` เหมือนกันทุกประการ)
