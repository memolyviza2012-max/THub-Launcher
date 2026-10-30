# Resident Evil 3 — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Resident Evil 3 is a survival horror game developed by Capcom on the RE Engine. Similar to RE2, the Thai localization mod relies on a File Replacement architecture, replacing specific fonts and `.msg` text files directly in the `natives` directory without packing into an archive.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | RE Engine |
| **Developer** | Capcom |
| **Project Codename** | Escape (as seen in `natives\stm\escape`) |
| **Archive Format** | Loose files in `natives\stm\escape` |
| **AES Encryption** | No |
| **Compression** | None (Loose files) |
| **Font System** | Font Swap (`.oft.1.x64` containing raw OTF) |
| **Thai Font Used** | CS PraKas (OTF) |
| **Text System** | `.msg` / `.msg.15` (RE Engine Message File Version 15) |
| **Text Encoding** | UTF-16 LE |
| **Mod Complexity** | ★★☆☆☆ (Direct font swap + Version 15 MSG modification) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```text
Resident_Evil_3\RE3_CompleteThaiEdition\
└── natives\
    └── stm\
        └── escape\
            ├── message\
            │   └── mes_bonus.msg.15 (Binary text file - Version 15)
            │   └── (Other .msg.15 files)
            └── ui\
                └── ui0000\font\
                    ├── arial.oft.1.x64 (Replaced with CS PraKas)
                    ├── corbelb.oft.1.x64
                    ├── fot-tsukugopro-d.oft.1.x64
                    ├── helveticaneueltw1g-cn.oft.1.x64
                    └── (Other fonts swapped with CS PraKas)
```

---

## 4. Font Analysis
- **Identification:** RE3 replaces multiple base game fonts with an OTF font named **CS PraKas**. 
- **Storage:** Fonts are stored as raw OTF files renamed with the `.oft.1.x64` extension. Magic bytes confirm the `OTTO` header at offset 0.
- **Font Swap Mapping:** Many fonts including Arial, Corbelb, FOT-TsukuGoPro, and Helvetica are overridden. This wide coverage ensures that any UI element calling these fonts will properly render Thai text instead.
- **Thai Rendering Considerations:** As a standard OTF font, shaping (สระลอย, วรรณยุกต์) depends on how the text is authored in the MSG files or the engine's built-in text renderer.

---

## 5. Text Analysis
- **File Format and Encoding:** The game uses RE Engine `.msg.15` format, which is an updated version compared to RE2's `.msg.14`. 
- **Encoding:** The text is encoded in UTF-16 LE. 
- **Structure:** MSG Version 15 has slight header/struct differences from Version 14, requiring specific extraction tools that support RE Engine MSG Version 15. The magic bytes are `0F 00 00 00 47 4D 53 47` (Version 15, "GMSG").

---

## 6. Cross-Engine Comparison
Comparing RE2 to RE3, both use RE Engine and the same directory injection method (`natives`). However, RE3's internal codename is `escape`, meaning its file paths use `natives\stm\escape` instead of RE2's direct `x64` structure. Furthermore, RE3 uses `.msg.15` for text whereas RE2 uses `.msg.14`. Modders cannot reuse the exact same text repacker if it only supports Version 14.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
**Font Pipeline:**
1. Procure a Thai-compatible OTF font (e.g. CS PraKas).
2. Rename it to match the required UI fonts in `natives\stm\escape\ui\ui0000\font\`.
3. Drop it into the `natives` folder to override.

**Text Pipeline:**
1. Extract base game `.msg.15` files using an RE Engine tool updated for RE3 (Version 15 support).
2. Export text to JSON/TXT.
3. Translate strings to Thai, saving in UTF-16 LE.
4. Repack using the Version 15 tool.
5. Place the modified files in `natives\stm\escape\message\`.

---

## 8. Troubleshooting
- **MSG Tool Errors:** If your repack tool crashes, ensure it supports `.msg.15`. Older RE2 tools (for `.msg.14`) will fail.
- **Missing UI Text:** Because RE3 overrides many different fonts (Arial, Corbelb, etc.), ensure you swap all variations if some UI elements display rectangles.
- **Game Crash:** Verify that the folder structure exactly matches the base game (`natives\stm\escape\...`).

---

## 9. Required Tools
| Tool Name | Purpose | Source |
|---|---|---|
| REtool / MSG Tool (Updated) | Extracting and repacking RE Engine `.msg.15` | [Fluffy Manager / RE Modding Wiki] |
| Hex Editor (HxD) | Checking MSG headers and font headers | [HxD] |

---

## 10. Extracted Assets
- [CSPraKas.otf](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/RE%20Engine/Games/Resident%20Evil%203/Assets/Fonts/CSPraKas.otf) (Successfully extracted and verified)

---

## 11. M2M Protocol
*(Optional section for Bitmap font workflows - since this game supports raw OTF, this section is included for completeness but is not strictly necessary for RE3).*
```python
# M2M Automated Script Template (Reference)
# In case a specific UI element requires a baked texture (.tex) instead of OTF
import struct

def shape_thai_text(text):
    pass
```
