# Resident Evil 7 — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Resident Evil 7 (Biohazard) uses the RE Engine developed by Capcom. The mod architecture follows a standard File Replacement pattern, primarily replacing `.msg.12` files for text and `.oft.1` files for fonts.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | RE Engine |
| **Developer** | Capcom |
| **Project Codename** | Unknown |
| **Archive Format** | Standard RE Engine `.pak` (extracted to `natives\x64` in mod) |
| **AES Encryption** | N/A (Mod uses unpacked `natives` folder overriding base PAKs) |
| **Compression** | None (Files are loose) |
| **Font System** | Font Swap (`.oft.1` which are raw OTF files) |
| **Thai Font Used** | CS PraKas |
| **Text System** | RE Engine `.msg.12` (Binary `GMSG` header) |
| **Text Encoding** | UTF-16 LE / UTF-8 |
| **Mod Complexity** | ★★☆☆☆ (Simple file replacement, no complex injection required) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```
RE7Tha\natives\x64\
├── message\
│   ├── ui_common_mes.msg.12 (and many others)
├── ui\
│   ├── ui0000\font\
│   │   ├── cap-durmal.oft.1 (and others replaced by Thai font)
│   ├── ui0200\tex\
│       ├── ui0202_54_im.tex.8 (UI textures)
```

---

## 4. Font Analysis
- The game uses standard OpenType Fonts (.otf) simply renamed to `.oft.1`.
- The mod creator replaced all 16 font files in `ui0000\font\` with an identical 73.1 KB Thai font named "CS PraKas".
- The font is directly installable by renaming `.oft.1` to `.otf`.
- The text engine handles basic Thai rendering.

---

## 5. Text Analysis
- Texts are stored in `.msg.12` format.
- The files are binary, starting with `0C 00 00 00 47 4D 53 47` (GMSG at offset 4).
- The text is organized by key-value pairs or indexed arrays typical of RE Engine Message files.

---

## 6. Cross-Engine Comparison
Compared to later RE Engine games like Resident Evil 9, RE7 uses simple `.oft.1` (raw OTF) fonts which are easily replaced without custom unpacking tools. RE9 shifts to a proprietary `FBFO` encrypted/custom font format.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
**Font Pipeline:**
1. Get a TrueType/OpenType Thai font (e.g., CS PraKas).
2. Rename the extension to `.oft.1`.
3. Replace all original game fonts in `natives\x64\ui\ui0000\font\`.

**Text Pipeline:**
1. Use an RE Engine MSG tool to unpack `.msg.12` to JSON/TXT.
2. Translate the text preserving formatting tags.
3. Repack back to `.msg.12` and place in `natives\x64\message\`.

---

## 8. Troubleshooting
- **Missing Characters**: Ensure the replacement font contains the necessary glyphs.
- **Thai Vowel Misalignment**: "สระลอย" may occur if the font's GPOS tables are not natively parsed by RE Engine properly. Using pre-shaped Thai text or specifically crafted TTFs might be needed if issues arise.
- **Game Crash**: Usually caused by malformed `.msg.12` files. Ensure the repacker uses the correct RE7 version (12).

---

## 9. Required Tools
| Tool | Purpose | Source |
|---|---|---|
| RETool | Unpack/Pack RE Engine PAK files | FluffyQuack |
| RE MSG Tool | Convert `.msg.12` to editable text | Various GitHub repos |

---

## 10. Extracted Assets
- [CS_PraKas.otf](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/RE_Engine/Games/Resident_Evil_7/Assets/Fonts/CS_PraKas.otf)

---

## 11. M2M Protocol
**Automated Font Rendering Script (Python):**
Since RE7 supports direct OTF loading, bitmap rendering is not required for standard text, but if `.tex.8` files need localized UI:
```python
import struct
# .tex.8 uses RE Engine Texture format
# Magic: TEX\x00\x08\x00\x00\x00
```
For basic modding, M2M can just copy and rename `.otf` to `.oft.1`.
