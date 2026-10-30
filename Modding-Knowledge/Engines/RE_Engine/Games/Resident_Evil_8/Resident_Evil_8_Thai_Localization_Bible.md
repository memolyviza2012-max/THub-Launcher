# Resident Evil 8 (Village) — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Resident Evil 8 (Village) uses an upgraded version of the RE Engine. The mod uses a File Replacement pattern via Fluffy Manager, modifying message files and environmental textures but conspicuously lacking direct font files in this specific distribution.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | RE Engine |
| **Developer** | Capcom |
| **Project Codename** | Village |
| **Archive Format** | Fluffy Manager loose files (`natives\stm`) |
| **AES Encryption** | N/A (Mod uses unpacked loose files) |
| **Compression** | None (Files are loose) |
| **Font System** | Not present in this archive (likely relies on base game fonts, system fonts, or separate mod) |
| **Thai Font Used** | Unknown |
| **Text System** | RE Engine `.msg.33685777` (Binary `GMSG` header) |
| **Text Encoding** | UTF-16 LE / UTF-8 |
| **Mod Complexity** | ★★★☆☆ (Requires modifying many environmental textures `.tex.30` as well as `.msg.33685777`) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```
RE8_CompleteThaiEdition\natives\stm\
├── _ge\environment\textures\
│   ├── sm91_218_johnmemo_a_alba.tex.30 (and many others)
├── message\
│   ├── gui\
│   │   ├── ui_common.msg.33685777
│   ├── sce\
│       ├── sce_chp1.msg.33685777
```

---

## 4. Font Analysis
- No `.oft` or `.ttf` files were found in the mod directory.
- This implies either the text simply maps to a font already provided in another mod, or the RE Engine fallback system for RE8 can render basic OS fonts (unlikely), or the font was packed in a `pak` file not included in this loose directory.
- For a complete Thai experience, environmental text (notes, graffiti) was manually replaced via `.tex.30` files.

---

## 5. Text Analysis
- Texts are stored in `.msg.33685777` format.
- Magic Bytes: `11 01 02 02 47 4D 53 47` (GMSG at offset 4).
- The text is organized by key-value pairs or indexed arrays typical of RE Engine Message files. 

---

## 6. Cross-Engine Comparison
Unlike RE7 which used `.msg.12` and easily replaceable `.oft.1` files, RE8 uses version `.msg.33685777`. RE8 mods heavily rely on modifying `.tex.30` for localized in-game environmental assets (like memos and graffiti) because these are baked into textures rather than rendered text.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
**Text Pipeline:**
1. Extract `.msg.33685777` using REtool.
2. Translate strings to Thai.
3. Repack and maintain directory structure for Fluffy Manager.

**Environmental Texture Pipeline:**
1. Extract `.tex.30` to `.dds`.
2. Edit the texture to translate English/Romanian text to Thai.
3. Repack to `.tex.30`.

---

## 8. Troubleshooting
- **Missing Text**: If the font isn't loaded (since it's missing from this pack), users will see square boxes. A font mod is likely required.
- **Texture glitches**: If `.tex.30` is repacked with the wrong DDS format (e.g., BC7 instead of BC3), it might render incorrectly.

---

## 9. Required Tools
| Tool | Purpose | Source |
|---|---|---|
| RETool | Unpack/Pack RE Engine `.msg` and `.tex` files | FluffyQuack |
| Noesis | Convert `.tex` files to DDS and back | Rich Whitehouse |

---

## 10. Extracted Assets
- Font extraction failed (no font files found). See [EXTRACTION_NOTE.txt](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/RE_Engine/Games/Resident_Evil_8/Assets/Fonts/EXTRACTION_NOTE.txt).

---

## 11. M2M Protocol
**Automated Font Rendering Script (Python):**
For `.tex.30` files, automation requires converting DDS to PNG, editing text, and converting back.
```python
import struct
# Magic: TEX\x00\x1E\x00\x00\x00 (Version 30)
```
For injecting text into .tex:
1. Parse TEX header to find DDS offset.
2. Extract DDS.
3. Use Pillow to draw Thai text onto DDS.
4. Repack DDS back into TEX wrapper.
