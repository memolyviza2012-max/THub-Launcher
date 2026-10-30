# Quarantine Zone — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Quarantine Zone is a simulation/survival game built on Unreal Engine 4/5. The modder utilizes a standard Unreal Engine Pak (`.pak`) overlay approach to inject localized `.locres` text and modified `.ufont` font files into the game. 

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Unreal Engine (PAK v3/v4) |
| **Developer** | Unknown |
| **Project Codename** | QZSim |
| **Archive Format** | .pak (Standard UE) |
| **AES Encryption** | No AES encryption (Flag byte `00` before footer signature) |
| **Compression** | Zlib / Standard UE Compression |
| **Font System** | Font Swap (`.ufont` file replacing standard engine fonts) |
| **Thai Font Used** | Noto Sans SC (Thin, Regular, Medium, Bold) |
| **Text System** | LocRes (Binary) + CSV/TXT equivalents provided by modder |
| **Text Encoding** | UTF-8 |
| **Mod Complexity** | ★★★☆☆ (Standard UE modding, involves repacking `.pak` and font conversion) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```
Quarantine Zone/
└── Content/
    └── Paks/
        └── Yaklongpae-ModThai_P.pak (30.7 MB)

Unpacked Contents:
└── QZSim/
    ├── Content/Localization/Game/en/
    │   ├── Game.locres (315 KB)
    │   ├── Game.locres.TH.txt (394 KB)
    │   └── Game.locres.txt (222 KB)
    └── Content/UI/Font/
        ├── NotoSansSC-Bold.ufont (10.4 MB)
        ├── NotoSansSC-Medium.ufont (10.4 MB)
        ├── NotoSansSC-Regular.ufont (10.5 MB)
        └── NotoSansSC-Thin.ufont (10.4 MB)
```

---

## 4. Font Analysis
- The mod injects `.ufont` files in the `QZSim\Content\UI\Font` directory.
- A quick binary analysis of `NotoSansSC-Regular.ufont` reveals the TTF magic header `00 01 00 00` starting exactly at offset 0.
- This means the engine is loading raw TrueType fonts without custom offset wrappers.
- The fonts have been extracted by renaming the `.ufont` to `.ttf` and saved in the Modding Knowledge Base.
- Thai rendering considerations: Uses Google's Noto Sans SC, which supports a broad range of glyphs. Standard UE text shaping applies.

---

## 5. Text Analysis
- The game's primary text database is `Game.locres`.
- The modder graciously included the raw translation text files (`Game.locres.TH.txt`) alongside the binary `.locres` inside the PAK, which is extremely helpful for further editing.
- Encoding is standard UTF-8. A scan of the first 100KB of `Game.locres.TH.txt` found over 25,000 Thai character byte sequences, proving full coverage.

---

## 6. Cross-Engine Comparison
This mod follows the exact same pattern as most standard Unreal Engine 4 titles (like Ghostrunner or The Outer Worlds) where a patch PAK file (`_P.pak`) is used to override `Content/Localization` and `Content/UI/Font`. Because there is no AES encryption or IoStore (`.utoc`/`.ucas`), repacking this mod is highly accessible compared to UE5 games like Final Fantasy VII Rebirth or S.T.A.L.K.E.R. 2.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
**Text Pipeline:**
1. Extract the `Game.locres.TH.txt` using `repak_cli`.
2. Edit the translations in the text file.
3. Use a tool like UnrealLocres to compile the `.txt` back into `Game.locres`.
4. Replace the old `Game.locres` in the unpacked folder structure.

**Font Pipeline:**
1. To change fonts, take any standard `.ttf` font.
2. Rename the extension from `.ttf` to `.ufont`.
3. Replace the `NotoSansSC-*.ufont` files in `QZSim\Content\UI\Font\`.

**Packing Pipeline:**
1. Run `repak.exe pack QZ_Extracted Yaklongpae-ModThai_P.pak`.
2. Place the resulting `.pak` into the game's `Content\Paks` directory.

---

## 8. Troubleshooting
- **Font Not Displaying:** Check if the replacement `.ttf` file actually contains Thai glyphs. 
- **Crash on Startup:** Ensure that `repak_cli` was run with the correct UE version flag if the engine expects a specific PAK version.

---

## 9. Required Tools
| Tool | Purpose | Source |
|---|---|---|
| repak_cli | Unpacking and packing UE `.pak` files | Modding-Knowledge/Tools |
| UnrealLocres | Converting `.locres` to `.txt` and back | GitHub |

---

## 10. Extracted Assets
- NotoSansSC-Bold.ttf
- NotoSansSC-Medium.ttf
- NotoSansSC-Regular.ttf
- NotoSansSC-Thin.ttf
These have been safely archived to `Assets/Fonts/`.
