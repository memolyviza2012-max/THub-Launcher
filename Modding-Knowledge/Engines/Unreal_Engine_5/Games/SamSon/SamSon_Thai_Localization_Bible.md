# SamSon — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
SamSon is an Unreal Engine 5 game that uses the IoStore architecture (.pak, .ucas, .utoc) for its asset packaging. The Thai localization mod utilizes a direct File Replacement pattern by overriding standard LocRes and Font assets inside a `~mods` folder.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Unreal Engine 5 |
| **Developer** | Unknown |
| **Project Codename** | CJ |
| **Archive Format** | IoStore (.pak, .ucas, .utoc) |
| **AES Encryption** | No |
| **Compression** | Oodle / None |
| **Font System** | Font Swap (.ufont) |
| **Thai Font Used** | DejaVu Serif (TTF) |
| **Text System** | LocRes (.locres) |
| **Text Encoding** | UTF-8 |
| **Mod Complexity** | ★★☆☆☆ (Standard IoStore, raw TTF inside UFONT, easy to unpack/repack) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```text
SamSon/CJ/Content/Paks/~mods/
├── zzz_Thai_P.pak  (2.6 MB)
├── zzz_Thai_P.ucas (3.5 MB)
└── zzz_Thai_P.utoc (866 Bytes)

Inside Archive:
CJ/Content/
├── CJ/UI/Fonts/
│   ├── CJConsoleButtons.ufont (390 KB)
│   ├── NeueHaasGrunge-Expanded.ufont (390 KB)
│   ├── NeueHaasGrunge-Light.ufont (390 KB)
│   ├── NeueHaasGrunge-Medium.ufont (390 KB)
│   ├── Samson-Pager.ufont (390 KB)
│   └── SamsonWriting.ufont (390 KB)
└── Localization/Game/en/
    ├── Game.locres (1.7 MB)
    └── Game.locres.txt (2.0 MB)
```

---

## 4. Font Analysis
- **Font Format**: TrueType (TTF). The original font was replaced directly with `DejaVu Serif`.
- **Storage**: The `.ufont` files are essentially raw `.ttf` files; the TTF magic header `00 01 00 00` starts precisely at offset 0.
- **Font Swap Mapping**: Six different original fonts (like `NeueHaasGrunge`) are all replaced with the exact same DejaVu Serif TTF file (each identically 390,636 bytes).
- **Thai Rendering**: Standard TTF rendering.

---

## 5. Text Analysis
- **File Format**: Standard Unreal Engine `.locres` format (alongside a dumped `.locres.txt` version).
- **Encoding**: UTF-8. Verified Thai sequences `E0 B8` inside the file.
- **Structure**: Binary key-value tuples representing the game's text strings.

---

## 6. Cross-Engine Comparison
This mod shares the same basic architecture as other Unreal Engine 5 games utilizing the IoStore system (like **Avowed** or **The Alters**). Modders used to UE4 `.pak` modding must adapt to packing three files (`.pak`, `.ucas`, `.utoc`) using UE5 UnrealPak tools, but the underlying text and font formats (`.locres` and `.ufont`) remain identical to UE4.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
**Font Pipeline:**
1. Rename standard TTF fonts to the required `.ufont` names.
2. Ensure they overwrite all 6 UI fonts to maintain visual consistency.

**Text Pipeline:**
1. Export original English `.locres` to `.csv` or `.json` using UnrealLocres.
2. Translate texts in spreadsheet software keeping the UTF-8 encoding.
3. Import the translated `.csv` back to `.locres` via UnrealLocres.

**Packaging Pipeline:**
1. Create a folder structure mirroring the engine's original tree (`CJ/Content/...`).
2. Run UnrealPak from the UE5 toolset with the `-IoStore` flag to generate the `.pak`, `.ucas`, and `.utoc` files.

---

## 8. Troubleshooting
- **Missing Characters**: If DejaVu Serif lacks certain Thai glyphs (like specific tone marks), replacing it with Noto Sans Thai is recommended.
- **Mod not loading**: The `zzz_Thai_P.pak` acts as a dummy to register the IoStore mount point. It must be present alongside the `.ucas` and `.utoc` files for the engine to load the assets.
- **Game Crash**: Ensure the text files are saved explicitly as UTF-8 without BOM.

---

## 9. Required Tools
| Tool | Purpose | Source |
|---|---|---|
| **repak_cli** | Unpacking UE4/UE5 standard and basic IoStore archives | E:\Mod_Workspace\Tool\repak_cli\repak.exe |
| **UnrealPak** | Official tool to repack `.ucas` and `.utoc` | E:\Mod_Workspace\Tool\RePak\RePak.exe |
| **UnrealLocres** | Edit and modify UE binary text files | GitHub |

---

## 10. Extracted Assets
- [DejaVuSerif.ttf](../../../../../Assets/Fonts/DejaVuSerif.ttf)
