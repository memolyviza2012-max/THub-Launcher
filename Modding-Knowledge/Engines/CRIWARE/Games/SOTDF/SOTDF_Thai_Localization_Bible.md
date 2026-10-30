# SOTDF — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
SOTDF uses the CRIWARE Engine middleware, storing assets in `.cpk` archives. The mod architecture pattern is File Replacement.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | CRIWARE Engine (.cpk) |
| **Developer** | Unknown |
| **Project Codename** | Unknown |
| **Archive Format** | `.cpk` |
| **AES Encryption** | N/A (Standard CRIWARE compression) |
| **Compression** | CRILAYLA or similar proprietary |
| **Font System** | Custom CPK wrapper |
| **Thai Font Used** | Unknown |
| **Text System** | Binary message file (.cpk) |
| **Text Encoding** | UTF-8 |
| **Mod Complexity** | ★★☆☆☆ |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```
SOTDF/
└── chunk_0/
    └── en-us/
        ├── font_en-us.cpk (295 KB)
        └── message_en-us.cpk (3.6 MB) - Contains 114 Thai character sequences
```

---

## 4. Font Analysis
- Font is stored in `font_en-us.cpk`.
- Scanning for standard TTF/OTF signatures revealed no standard font headers (`00 01 00 00` or `OTTO`), meaning the font is wrapped or compressed (e.g. CRILAYLA compressed or bitmap font).

---

## 5. Text Analysis
- Texts are stored in `message_en-us.cpk`, which contains 114 Thai UTF-8 sequences.
- Encoding: UTF-8.

---

## 6. Cross-Engine Comparison
- Unlike Unreal Engine 4/5 which uses `.pak` and `.locres`, CRIWARE uses `.cpk` files for everything (audio, fonts, texts). Modders will need CRI Packed File Maker or similar CRI tools, akin to modding older console games.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
**Text & Font Pipeline:**
1. Extract `.cpk` files using a tool like QuickBMS or CRI Packed File Maker.
2. Edit the extracted files.
3. Repack back into `.cpk`.

---

## 8. Troubleshooting
- **Game crashes:** Check if repacked `.cpk` has the correct alignment.
- **Thai text rendering as squares:** Ensure the font inside the CPK is correctly generated in CRI's proprietary font format.

---

## 9. Required Tools
| Tool Name | Purpose |
|---|---|
| CRI Packed File Maker | Repacking `.cpk` files |
| QuickBMS + CPK Script | Unpacking `.cpk` archives |

---

## 10. Extracted Assets
Extraction failed because the font is either compressed or in a proprietary bitmap format.
[EXTRACTION_NOTE.txt](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/CRIWARE/Games/SOTDF/Assets/Fonts/EXTRACTION_NOTE.txt)
