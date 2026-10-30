# Marvel's Avengers — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Marvel's Avengers runs on the Crystal Dynamics Foundation Engine (the same proprietary engine used in modern Tomb Raider games). The Thai localization mod uses a **Hybrid File Replacement** approach, directly injecting modified `.tiger` archives alongside their corresponding metadata (`.nfo`) to substitute original game text and font assets.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Crystal Dynamics Foundation Engine (TAFS) |
| **Developer** | Crystal Dynamics / Eidos-Montréal |
| **Project Codename** | Unknown |
| **Archive Format** | `.tiger` (Tiger Archive File System) & `.nfo` |
| **AES Encryption** | No |
| **Compression** | Specific chunk compression within TAFS (often Zlib or LZ4 variant) |
| **Font System** | Scaleform / Bitmap Texture Atlas (SDF) |
| **Thai Font Used** | Unknown (Embedded in Scaleform or SDF) |
| **Text System** | Binary String DB within TAFS chunks |
| **Text Encoding** | UTF-8 / UTF-16 LE |
| **Mod Complexity** | ★★★★★ (Requires specialized TAFS/Tiger unpackers and Scaleform/GFX modifiers) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```
D:\Mods games\Thai Mods\0_Rivet Engineer\Marvels Avengers\
├── bigfile._mod.000.000.nfo             [159 B]  - Mod metadata / mount instructions
├── bigfile._mod.000.000.tiger           [27 MB]  - Core mod assets (likely fonts / UI)
├── bigfile._mod.000.001.tiger           [229 MB] - Additional mod assets
└── bigfile._mod.000_english.000.tiger   [2.2 GB] - Main locale file containing English/Thai text replacement
```

---

## 4. Font Analysis
- The Foundation engine generally uses Scaleform (GFX/SWF) for UI, which embeds fonts directly, or SDF (Signed Distance Field) texture atlases.
- Extracting standard `.ttf` files directly from `.tiger` archives is not possible without reverse-engineering the specific UI chunk format.
- The Thai mod likely modifies the original English Scaleform files to include Thai glyphs, swapping the English font linkage with a custom Thai font inside the `.gfx` file.
- Thai rendering considerations (สระลอย, วรรณยุกต์) must be handled by the UI engine or pre-shaped since Scaleform standard text fields sometimes struggle with complex Thai shaping out of the box.

---

## 5. Text Analysis
- The massive 2.2GB `bigfile._mod.000_english.000.tiger` file contains the game's localized text.
- Text is likely stored in binary string tables within the TAFS chunks. Our analysis found thousands of UTF-8 and UTF-16 LE Thai character sequences in the `.tiger` files, indicating the text is mixed or different subsystems use different encodings.
- The `.nfo` file is a crucial mount manifest, instructing the engine to load these `.tiger` files as a mod (`custom mod:Marvels Avengers THAI MOD`) and overriding base assets.

---

## 6. Cross-Engine Comparison
The Foundation Engine's `.tiger` system is identical to that used in the **Tomb Raider** reboot series (e.g., Shadow of the Tomb Raider). Modding tools for Tomb Raider (like *Tiger Unpacker* or *CdcEngine tools*) are often applicable here. Unlike **Unreal Engine**, which relies on a clear `.pak` and `.locres` structure, `.tiger` archives are heavily chunk-based and require specialized tools to parse the `TAFS` headers (`54 41 46 53`).

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
**Text Pipeline:**
1. Unpack the original `.tiger` archives using a compatible CdcEngine/Tomb Raider extraction tool.
2. Locate the localized string database files (often `.drm` or `.dtp` extensions inside the unpacked archive).
3. Translate and inject the Thai text.
4. Repack the archive into a custom `.tiger` file.

**Font Pipeline:**
1. Locate the UI `.gfx` / `.swf` files or font textures.
2. Use JPEXS Free Flash Decompiler (if Scaleform) to inject the Thai font and update embedding properties.
3. Repackage into the `.tiger` archive.
4. Update the `.nfo` file to mount the new archive as a mod with higher priority than base files.

---

## 8. Troubleshooting
- **Game ignores the mod:** Ensure the `.nfo` file is correctly formatted and placed in the right directory. The engine uses this file to mount the `.tiger` archives.
- **Missing characters (boxes):** The font injection in the `.gfx` file missed specific Thai glyph ranges.
- **Game crash on text load:** The binary string database was repacked incorrectly (string length mismatches or invalid chunk headers).

---

## 9. Required Tools
| Tool | Purpose | Source |
|---|---|---|
| Tiger Unpacker / CdcEngine Tools | Unpacking/Repacking `.tiger` archives | Community modding forums (e.g., XeNTaX) |
| JPEXS Free Flash Decompiler | Editing Scaleform `.gfx` files for font injection | [Download](https://github.com/jindrapetrik/jpexs-decompiler) |

---

## 10. Extracted Assets
Extraction of the font as a standard `.ttf` file failed because the engine uses Scaleform (SWF/GFX) embedded fonts or proprietary SDF textures.
See `EXTRACTION_NOTE.txt` in the Assets directory for more details.

---

## 11. M2M Protocol
**Automated Font Injection for Scaleform (Flash):**
If this game relies on Scaleform for fonts, an automated pipeline must manipulate SWF tags programmatically using a library like `swfmill` or custom Python SWF parsing to inject DefineFont3 tags containing Thai glyphs.

```python
import os

def inject_swf_font(base_gfx_path, ttf_font_path, output_gfx_path):
    # Conceptual: converting GFX to SWF, using swfmill to inject TTF, then back to GFX
    # Requires external swfmill binary
    os.system(f"swfmill swf2xml {base_gfx_path} temp.xml")
    
    # 1. Parse temp.xml
    # 2. Add <DefineFont3> or replace existing font's glyph mapping with Thai TTF data
    # 3. Save modified_temp.xml
    
    os.system(f"swfmill xml2swf modified_temp.xml {output_gfx_path}")
    print("Font injected into Scaleform GFX.")
```
