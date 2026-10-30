# BEYOND: Two Souls — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
BEYOND: Two Souls is an interactive drama action-adventure game developed by Quantic Dream, running on their proprietary Quantic Dream Engine. The Thai localization mod uses a **File Replacement** architecture, directly modifying the massive `.dat` and `.idx` archive files that store the game's core assets, fonts, and text strings.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Quantic Dream Engine |
| **Developer** | Quantic Dream |
| **Project Codename** | N/A |
| **Archive Format** | `.dat` / `.idx` (BigFile format with magic `QUANTICDREAMTABINDEX`) |
| **AES Encryption** | No |
| **Compression** | None (Raw data) |
| **Font System** | Custom Quantic Dream Font / Embedded |
| **Thai Font Used** | Custom Thai Font |
| **Text System** | Binary Embedded within `.dat` |
| **Text Encoding** | UTF-16 LE |
| **Mod Complexity** | ★★★★☆ (Massive 3.6GB files require byte-level manipulation and precise offset management) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```
D:\Mods games\Thai Mods\0_Rivet Engineer\BEYOND Two Souls\
├── BigFile_PC_9900.dat    [3.6 GB]  - Main data archive containing text and fonts
├── BigFile_PC_9900.dep    [24 B]    - Dependency/metadata file
├── BigFile_PC_9900.idx    [41 KB]   - Index file for 9900.dat
├── BigFile_PC_9920.dat    [77 MB]   - Secondary data archive (likely UI/Subtitles)
├── BigFile_PC_9920.dep    [24 B]
└── BigFile_PC_9920.idx    [2 KB]    - Index file for 9920.dat
```

---

## 4. Font Analysis
- The game engine embeds font data directly inside the `.dat` archives.
- The font format is likely a proprietary Quantic Dream format or heavily modified embedded TTF that lacks standard headers that allow easy extraction to a standalone `.ttf` file.
- Thai text requires UTF-16 LE encoding support.
- Thai rendering considerations (สระลอย, วรรณยุกต์, ตัวเลขไทย) are handled either via engine-level shaping or custom pre-rendered glyph placements depending on how the modder injected the font.

---

## 5. Text Analysis
- Text strings are stored in **UTF-16 LE** encoding directly inside the `BigFile_PC_9900.dat` and `BigFile_PC_9920.dat` files.
- The files do not use a standard string table format (like `.csv` or `.locres`), but rather a binary-embedded format indexed by `.idx` files.
- Due to the massive file size (3.6GB), strings must be parsed by chunking the file and scanning for UTF-16 LE sequences (e.g., `0E 0E` ... `5B 0E`).
- An analysis of the first 50MB of `9900.dat` revealed over 10,000 Thai UTF-16 LE characters, indicating dense text regions.

---

## 6. Cross-Engine Comparison
Unlike **Unreal Engine 4/5** (which uses structured `.pak` and `.locres` files) or **Unity** (which uses `resources.assets`), the Quantic Dream Engine uses massive monolithic `.dat` files with separate `.idx` indices. This makes it more similar to older proprietary engines like the **Void Engine (Arkane)** or **Anvil (Ubisoft)**, where extracting and repackaging requires custom tools to rebuild the index (`.idx`) after modifying the data (`.dat`).

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
**Text Pipeline:**
1. Use a hex editor or custom script to locate the target text strings in `BigFile_PC_9900.dat` (encoded in UTF-16 LE).
2. Modify the text, ensuring that the byte length matches the original string unless the `.idx` file is also updated to reflect the new offsets.
3. If strings are longer, the `.idx` index file must be reverse-engineered to update pointers.

**Font Pipeline:**
1. Locate the embedded font block within the `.dat` file.
2. Inject the custom Thai font binary data at the correct offset, being careful to maintain file structure and update any corresponding indices if the size changes.

---

## 8. Troubleshooting
- **Game crash after mod installation:** The `.idx` index file does not match the offsets in the modified `.dat` file. Ensure string lengths remain identical or offsets are properly recalculated.
- **Thai text appears as boxes/question marks:** The font injection failed, or the specific text block does not use the modified font asset.
- **Encoding corruption:** Text must be saved in **UTF-16 LE** (without BOM), not UTF-8.

---

## 9. Required Tools
| Tool | Purpose | Source |
|---|---|---|
| Hex Editor (e.g., HxD) | Direct binary editing of `.dat` files | [Download](https://mh-nexus.de/en/hxd/) |
| Custom Python Scripts | To parse `.idx` indices and automate offset updates | N/A (Requires custom dev) |

---

## 10. Extracted Assets
Extraction of the font as a standard `.ttf` file failed because the engine uses a proprietary/embedded font format.
See `EXTRACTION_NOTE.txt` in the Assets directory for more details.

---

## 11. M2M Protocol
**Automated FNT/Mapping Injector (Struct):**
Because Quantic Dream uses proprietary embedded fonts, automated scripts must patch the font at the byte level.

```python
import struct
import os

def patch_quantic_dream_font(dat_path, font_offset, new_font_data):
    # This is a conceptual structure for patching the font directly in the .dat file
    with open(dat_path, 'r+b') as f:
        f.seek(font_offset)
        # Assuming we can simply overwrite if the new font data fits within the allocated block
        f.write(new_font_data)
        print(f"Injected new font data at offset {font_offset}")

# Placeholder for text string injection
def inject_utf16le_string(dat_path, offset, new_text):
    encoded_text = new_text.encode('utf-16le')
    with open(dat_path, 'r+b') as f:
        f.seek(offset)
        f.write(encoded_text)
```
