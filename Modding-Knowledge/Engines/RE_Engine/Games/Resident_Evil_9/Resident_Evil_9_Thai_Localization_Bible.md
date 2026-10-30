# Resident Evil 9 (Requiem / RE4 Remake Mod) — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
This mod, referenced as "Resident Evil Requiem," utilizes the RE Engine and is a highly complex localization effort. It replaces dialogue, game system files, and includes fonts. The mod uses REFramework's Loose File Manager to inject loose files directly into the game without modifying the original `.pak` archives.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | RE Engine |
| **Developer** | Capcom |
| **Project Codename** | Requiem / Dev1Term |
| **Archive Format** | Fluffy/REFramework loose files (`natives\stm`) |
| **AES Encryption** | N/A (Mod uses unpacked loose files via REFramework) |
| **Compression** | None (Files are loose) |
| **Font System** | FBFO Proprietary format (`.oft.1`) |
| **Thai Font Used** | Unknown (Embedded in FBFO) |
| **Text System** | RE Engine `.msg.23` (Binary `GMSG` header) |
| **Text Encoding** | UTF-16 LE / UTF-8 |
| **Mod Complexity** | ★★★★☆ (Requires custom parsing for FBFO fonts) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```
Resident_Evil_9\natives\stm\
├── gui\ui0000\font\
│   ├── americantypeitcpro-med.oft.1 (FBFO Format)
├── message\
│   ├── dialog\
│   │   ├── dialog_mangm3.msg.23 (and others)
│   ├── gamesystem\
│       ├── activity.msg.23
```

---

## 4. Font Analysis
- The game uses `.oft.1` extensions for its fonts, but they are NOT standard OpenType files.
- Magic Bytes: `46 42 46 4F` (FBFO) at offset 0.
- This represents an evolution in RE Engine's font handling, moving away from simple raw OTF/TTF files (like in RE7) to a proprietary or encrypted container.
- Consequently, Thai fonts cannot be trivially swapped by simply renaming `.otf` files. A custom FBFO packer/unpacker is required.

---

## 5. Text Analysis
- Texts are stored in `.msg.23` format.
- Magic Bytes: `17 00 00 00 47 4D 53 47` (GMSG at offset 4). The `17` (hex) corresponds to version 23.
- The structure contains complex indexing for dialogue, UI, and system elements, requiring an updated RETool version to parse.

---

## 6. Cross-Engine Comparison
This iteration shows significant changes from older RE Engine games. While RE7 used raw `.oft.1` (which were just renamed `.otf` files) and RE8 relied heavily on `.tex` replacement for environmental text, this title (RE9/RE4 Remake) uses the `.msg.23` format and the new `FBFO` font format. Modding fonts in this generation is substantially harder due to the proprietary FBFO format.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
**Font Pipeline:**
1. Use an FBFO compatible unpacker to decode the `.oft.1` to a standard format (e.g., TTF).
2. Replace or merge Thai glyphs.
3. Repack back to FBFO `.oft.1` format.

**Text Pipeline:**
1. Extract `.msg.23` using an updated RE Engine MSG tool.
2. Translate text to Thai.
3. Repack to `.msg.23` and place in `natives\stm\message\`.

---

## 8. Troubleshooting
- **Game Crash on Boot**: If the `.msg.23` file is incorrectly repacked, the game will crash during load.
- **Font Not Loading**: Since the font is in FBFO format, replacing it with a raw `.otf` file will cause the game to fail to render text or crash. Ensure the FBFO packing is correct.
- **Mod Not Recognized**: The user must enable Loose File Manager in REFramework (Insert key) for the game to read from `natives\stm`.

---

## 9. Required Tools
| Tool | Purpose | Source |
|---|---|---|
| REFramework | Enable loose file loading | Praydog (GitHub) |
| RETool (Updated) | Unpack/Pack `.msg.23` files | FluffyQuack / GitHub |
| FBFO Font Tool | Unpack/Pack `.oft.1` FBFO fonts | Specialized RE modding tools |

---

## 10. Extracted Assets
- Font extraction failed (FBFO proprietary format). See [EXTRACTION_NOTE.txt](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/RE_Engine/Games/Resident_Evil_9/Assets/Fonts/EXTRACTION_NOTE.txt).

---

## 11. M2M Protocol
**Automated Font Rendering Script (Python):**
Since FBFO parsing is undocumented publicly here, a fallback to `.tex` rendering might be required for specific UI injections, though replacing dynamic text requires FBFO.
If a standard TTF can be wrapped:
```python
import struct
# FBFO Magic: FBFO
# Further reverse engineering of the FBFO header is required to automate font injection.
```
