# Anno 1800 — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Anno 1800 is a city-building game from Ubisoft Blue Byte using the AnvilNext/custom engine. The mod architecture pattern is a File Replacement and "Locale Hijack", replacing Korean text with Thai via XML files to bypass locale limitations.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | AnvilNext / Custom Ubisoft Engine |
| **Developer** | Ubisoft Blue Byte |
| **Project Codename** | N/A |
| **Archive Format** | RDA / Loose files |
| **AES Encryption** | No |
| **Compression** | N/A (XML is raw text) |
| **Font System** | Font Swap (.ttf) |
| **Thai Font Used** | Sarabun Light (Renamed as md_cgothic_l.ttf) |
| **Text System** | XML |
| **Text Encoding** | UTF-8 |
| **Mod Complexity** | ★★☆☆☆ |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```
[Mod Root]
├── modinfo.Json (997 B)
└── data/
    ├── config/gui/
    │   ├── texts_english.xml (154 B)
    │   └── texts_korean.xml (14 MB)
    └── fonts/
        ├── md_cgothic_l.ttf (83 KB)
        ├── metaoffcpro-norm.ttf
        └── metaserifoffcpro-medium.ttf
```

---

## 4. Font Analysis
- Font identification: The Thai font used is **Sarabun Light**, renamed to `md_cgothic_l.ttf`.
- How fonts are stored: Raw `.ttf` format injected into the `data/fonts` directory.
- Font swap mapping: The mod overrides native font files such as `md_cgothic_l.ttf` and `metaoffcpro` to ensure the Thai text can render correctly when the Korean locale is selected.
- Thai rendering considerations: Since raw TTF files are used and Anno 1800 supports standard TrueType rendering via its GUI system, Thai rendering usually works out of the box.

---

## 5. Text Analysis
- File format and encoding: The primary text file is `texts_korean.xml`. It uses **UTF-8** encoding.
- How text is structured: Standard XML structure replacing Korean locale text entries with Thai.
- Approximate string count / file size: 14 MB of pure text data, thousands of localization keys.
- Quest/dialogue organization structure: Key-Value XML nodes mapping to in-game elements.

---

## 6. Cross-Engine Comparison
Unlike games that use complex binary formats (e.g., Northlight Engine or Unreal Engine), Anno 1800 allows overriding `.xml` files via its native modding support (modinfo.json). This makes text and font modding highly accessible.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
**Font Pipeline:**
1. Generate or download a TTF font (e.g., Sarabun).
2. Rename the font to match the target language font in the game (e.g., `md_cgothic_l.ttf`).
3. Place in `data/fonts/`.

**Text Pipeline:**
1. Extract the base game's `.xml` files.
2. Edit the target locale file (e.g., Korean to hijack the language slot).
3. Save as UTF-8.
4. Define the mod in `modinfo.Json`.

---

## 8. Troubleshooting
- Font not displaying: Ensure the font file names match exactly the fonts requested by the overridden locale.
- Thai vowels/tone marks misaligned (สระลอย): If native shaping fails, you may need a custom shaper script, but XML generally supports standard UTF-8 shaping well in modern Ubisoft games.
- Game crash after mod installation: Ensure XML is well-formed; a single missing tag will break the parser.

---

## 9. Required Tools
| Tool Name | Purpose | Source |
|---|---|---|
| Text Editor (VS Code/Notepad++) | Editing XML and Json files | N/A |

---

## 10. Extracted Assets
- [Sarabun-Light.ttf](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/AnvilNext/Games/Anno%201800/Assets/Fonts/MD_CGothic_L.ttf)

---

## 11. M2M Protocol
**Automated Font Rendering Script (Python):** N/A
**Automated Text Shaping Script (Regex):**
```python
import re
def shape_thai(text):
    # XML handles Thai correctly natively in this engine in most cases.
    return text
```
