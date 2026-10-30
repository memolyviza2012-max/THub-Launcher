# Resident Evil 4 — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Resident Evil 4 (Remake) is a survival horror game developed by Capcom on the RE Engine. The Thai localization mod follows a direct File Replacement pattern by injecting modified files into the `natives` folder, overriding the original game's UI fonts and `.msg` files.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | RE Engine |
| **Developer** | Capcom |
| **Project Codename** | Chainsaw (as seen in `natives\stm\_chainsaw`) |
| **Archive Format** | Loose files in `natives\stm\_chainsaw` |
| **AES Encryption** | No |
| **Compression** | None (Loose files) |
| **Font System** | Font Swap (`.oft.1` containing raw OTF) |
| **Thai Font Used** | CS PraKas Bold (OTF) |
| **Text System** | `.msg` / `.msg.22` (RE Engine Message File Version 22) |
| **Text Encoding** | UTF-16 LE |
| **Mod Complexity** | ★★★☆☆ (Direct font swap + Version 22 MSG modification) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```text
Resident_Evil_4\RE4RE_Tha\
└── natives\
    └── stm\
        └── _chainsaw\
            ├── message\
            │   └── ao_mes_main_accessory.msg.22 (Binary text file - Version 22)
            │   └── (Other .msg.22 files)
            └── ui\
                └── ui0000\font\
                    ├── cs_cour.oft.1 (Replaced with CS PraKas Bold)
                    ├── fot-tsukugopro-d.oft.1
                    ├── HelveticaNeueLTW1G-Cn.oft.1
                    └── (Other fonts swapped with CS PraKas Bold)
```

---

## 4. Font Analysis
- **Identification:** RE4 replaces various original fonts with an OTF font named **CS PraKas Bold**. 
- **Storage:** Fonts are stored as raw OTF files renamed with the `.oft.1` extension (Notice it drops `.x64` seen in older RE games). Magic bytes confirm the `OTTO` header at offset 0.
- **Font Swap Mapping:** Many fonts like Courier, FOT-TsukuGoPro, and Helvetica are overridden. This wide coverage ensures that any UI element calling these fonts will properly render Thai text instead.
- **Thai Rendering Considerations:** As a standard OTF font, proper vowel and tone mark placement depends on text shaping handled by either the game's font rendering engine or pre-shaping in the `.msg` files.

---

## 5. Text Analysis
- **File Format and Encoding:** The game uses the RE Engine `.msg.22` format, a newer version compared to RE2's `.msg.14` and RE3's `.msg.15`. 
- **Encoding:** The text is encoded in UTF-16 LE, the standard for RE Engine.
- **Structure:** MSG Version 22 introduces structural differences in the header and offsets. The magic bytes are `16 00 00 00 47 4D 53 47` (Version 22, "GMSG").

---

## 6. Cross-Engine Comparison
While RE2, RE3, and RE4 all use the RE Engine and the `natives` loose file injection method, they each use different MSG versions:
- RE2: `.msg.14`
- RE3: `.msg.15`
- RE4: `.msg.22`
Additionally, the internal codenames change the folder structure: RE2 uses `natives\x64`, RE3 uses `natives\stm\escape`, and RE4 uses `natives\stm\_chainsaw`. Font extensions also slightly changed in RE4 from `.oft.1.x64` to `.oft.1`. Modders must use tools specifically updated for each game's MSG version.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
**Font Pipeline:**
1. Procure a Thai-compatible OTF font (e.g. CS PraKas Bold).
2. Rename it to match the required UI fonts in `natives\stm\_chainsaw\ui\ui0000\font\`. Ensure you use `.oft.1` as the extension.
3. Place into the `natives` directory.

**Text Pipeline:**
1. Extract base game `.msg.22` files using an RE Engine tool updated for RE4 Remake (Version 22 support).
2. Export text to JSON/TXT.
3. Translate strings to Thai, saving in UTF-16 LE.
4. Repack using the Version 22 tool.
5. Place the modified files in `natives\stm\_chainsaw\message\`.

---

## 8. Troubleshooting
- **MSG Tool Errors:** If your repack tool crashes, ensure it supports `.msg.22`. Tools made for RE2/RE3 will absolutely fail on RE4 files.
- **Missing UI Text:** Ensure you swap all variations of the fonts in the UI directory, as different menus might call different base fonts.
- **Game Crash:** Verify that the folder structure exactly matches the base game (`natives\stm\_chainsaw\...`).

---

## 9. Required Tools
| Tool Name | Purpose | Source |
|---|---|---|
| REtool / MSG Tool (Updated for RE4) | Extracting and repacking RE Engine `.msg.22` | [Fluffy Manager / RE Modding Wiki] |
| Hex Editor (HxD) | Checking MSG headers and font headers | [HxD] |

---

## 10. Extracted Assets
- [CSPraKasBold.otf](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/RE%20Engine/Games/Resident%20Evil%204/Assets/Fonts/CSPraKasBold.otf) (Successfully extracted and verified)

---

## 11. M2M Protocol
*(Optional section for Bitmap font workflows - since this game supports raw OTF, this section is included for completeness but is not strictly necessary for RE4).*
```python
# M2M Automated Script Template (Reference)
# In case a specific UI element requires a baked texture (.tex) instead of OTF
import struct

def shape_thai_text(text):
    pass
```
