# BioShock Remastered — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
BioShock Remastered runs on a heavily modified version of Unreal Engine 2.5 by 2K and Blind Squirrel Games. The translation utilizes a **File Replacement (Locale Hijacking)** pattern, replacing the official Chinese localization files (`_CHN` suffix) with Thai content to bypass font and codepage limitations in the English localization.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Unreal Engine 2.5 (Modified) |
| **Developer** | 2K / Blind Squirrel Games |
| **Project Codename** | Unknown |
| **Archive Format** | `.lbf` (Custom Localization Binary Format), `.swf`, `.gsc` |
| **AES Encryption** | No |
| **Compression** | None (Raw binary for `.lbf`, Uncompressed `FWS` for `.swf`) |
| **Font System** | Scaleform (Flash SWF) |
| **Thai Font Used** | Unknown (Embedded in SWF) |
| **Text System** | `.lbf` and `.srt` |
| **Text Encoding** | UTF-16 LE |
| **Mod Complexity** | ★★★★☆ (Requires LBF parsing and Scaleform SWF editing) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```text
D:\Mods games\Thai Mods\0_Rivet Engineer\BioShock Remastere\
└── ContentBaked\pc\
    ├── Localizedchn.lbf (1.2 MB - Main Text Database)
    ├── BinkMovies\
    │   ├── DC_1-Medical_CHN.srt (28 KB - UTF-16 LE Subtitles)
    │   └── ... (Total 17 subtitle files)
    └── FlashMovies\
        ├── fonts_CHN.swf (3.5 MB - UI Fonts, Flash v6)
        └── fonts_CHN.swf.gsc (30 MB - Game Scaleform Cache)
```

---

## 4. Font Analysis
- Fonts are managed via **Scaleform GFx**, packaged in `fonts_CHN.swf`. 
- The magic header of `fonts_CHN.swf` is `FWS`, which means it is an uncompressed Flash file.
- The `.gsc` file (`fonts_CHN.swf.gsc`) is a compiled cache for Scaleform to load fonts faster. Deleting it usually forces the game to rebuild it from the `.swf`.
- Since it hijacks the `_CHN` locale, the game naturally expects CJK characters, which avoids breaking character width limits often found in UE2's default ASCII modes.

---

## 5. Text Analysis
- The main text data is stored in `Localizedchn.lbf`. The magic bytes are `11 30 00 2D 00 6C 00 69`. 
- Text is encoded in **UTF-16 LE** (Little Endian), confirmed by finding thousands of `0x0E` high-bytes mapping to the Thai Unicode block (0x0E01 - 0x0E5B).
- Video subtitles are stored externally as standard `.srt` files in UTF-16 LE format.

---

## 6. Cross-Engine Comparison
Unlike modern Unreal Engine 4/5 which uses `.locres` and `.ufont`, UE2.5 relies heavily on custom binary formats and Scaleform Flash for UI/Fonts. Using Scaleform for UI was extremely popular in the late 2000s and 2010s (e.g. Skyrim, Borderlands, BioShock), which requires SWF decompilers (like JPEXS) rather than UE Pak extractors.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
**Font Pipeline:**
1. Use JPEXS Free Flash Decompiler (FFDec) to open `fonts_CHN.swf`.
2. Locate the font symbol (DefineFont3) and embed the TTF Thai font.
3. Save the SWF.
4. Delete `fonts_CHN.swf.gsc` to force the game to generate a new cache upon launch.

**Text Pipeline:**
1. Use a custom `.lbf` unpacker/repacker tool (usually written in Python) to convert `Localizedchn.lbf` to `.txt` or `.json`.
2. Translate text into Thai, ensuring encoding remains UTF-16 LE.
3. Repack back to `.lbf`.
4. For cutscenes, directly edit `.srt` files using UTF-16 LE encoding.

---

## 8. Troubleshooting
- **Font not displaying or crashing on load:** Ensure `fonts_CHN.swf.gsc` was deleted after updating the SWF. Scaleform will crash if the cache doesn't match the SWF.
- **Garbage text:** Ensure the `.lbf` and `.srt` files are strictly saved in UTF-16 LE (with BOM for `.srt`).
- **Thai vowels/tone marks misaligned (สระลอย):** Scaleform usually lacks proper complex text layout (CTL) support for Thai. You may need to pre-shape the text using a shaping script before packing.

---

## 9. Required Tools
| Tool | Purpose | Source |
|---|---|---|
| JPEXS (FFDec) | Extract and edit `.swf` files | Open Source |
| Custom LBF Tool | Unpack and repack `.lbf` | GitHub (BioShock Modding) |
| Notepad++ | Edit `.srt` files in UTF-16 LE | Open Source |

---

## 10. Extracted Assets
Extraction to raw TTF/OTF is not directly supported via command line because the vector font data is encapsulated within the `DefineFont` tags of the Flash SWF file.
See `EXTRACTION_NOTE.txt` in the Assets folder.
