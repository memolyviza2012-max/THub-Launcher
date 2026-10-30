# Werewolf: The Apocalypse - Earthblood — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Werewolf: The Apocalypse - Earthblood runs on Unreal Engine 4 (UE4) by Cyanide Studio. The mod uses the standard UE4 **File Replacement** pattern by loading a patched `.pak` file that overrides the original English `.locres` text database and `.ufont` font files.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Unreal Engine 4 |
| **Developer** | Cyanide Studio |
| **Project Codename** | WW |
| **Archive Format** | `.pak` (Standard Unreal Pak) |
| **AES Encryption** | No |
| **Compression** | Zlib |
| **Font System** | `.ufont` (Raw TTF encapsulated) |
| **Thai Font Used** | Bai Jamjuree Medium |
| **Text System** | `.locres` (Unreal Localization Resource) |
| **Text Encoding** | UTF-16 LE (Unreal default for CJK) |
| **Mod Complexity** | ★★☆☆☆ (Standard Unreal Engine 4 Modding pipeline) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```text
D:\Mods games\Thai Mods\0_Rivet Engineer\Werewolf The Apocalypse Earthblood\
└── WW\Content\Paks\
    └── pakchunk99-WindowsNoEditor_9.pak (4.3 MB - Main Mod Archive)
        └── (Unpacked Tree)
            ├── WW\Content\UI\Fonts\
            │   ├── NotoSans-Regular.ufont (156 KB - Actually Bai Jamjuree Medium TTF)
            │   ├── NotoSans-Bold.ufont
            │   └── ... (Total 22 ufont files overridden)
            └── WW\Content\Localization\Dialogues\en\
                ├── Dialogues.locres (698 KB)
                ├── Game.locres (134 KB)
                ├── KeyboardInputs.locres (29 KB)
                └── CyaTools.locres (21 KB)
```

---

## 4. Font Analysis
- The game uses standard Unreal Engine `.ufont` files.
- The magic header of `NotoSans-Regular.ufont` is `00 01 00 00`, confirming that it is a raw TrueType (`.ttf`) file simply renamed to `.ufont`. No special Unreal header exists at the start.
- The font has been verified via Shell Properties as **"Bai Jamjuree Medium"** (an open-source font from Cadson Demak).
- The mod simply overwrites the NotoSans and Oswald font files with Bai Jamjuree to provide Thai glyph support.
- Thai vowels and tone marks (สระลอย) typically render decently in UE4 if HarfBuzz is enabled, but may require pre-shaping if the game engine build is older.

---

## 5. Text Analysis
- The text is stored in `.locres` files, which are Unreal Engine's compiled binary localization resources.
- The files contain UTF-16 LE strings for non-ASCII characters, which is standard for Unreal Engine when packing Thai or CJK languages.
- Total strings are spread across four distinct files (Dialogues, Game, KeyboardInputs, and CyaTools), handling UI, dialogue, and inputs separately.

---

## 6. Cross-Engine Comparison
This follows the textbook UE4 modding workflow seen in games like *The Alters* or *Stray*. It contrasts sharply with UE5 IoStore (which requires `.utoc`/`.ucas`) and UE2.5 (which relies on Scaleform Flash like BioShock). The ability to just drop a raw TTF file renamed to `.ufont` into a PAK is the simplest and most accessible modding pipeline.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
**Font Pipeline:**
1. Choose an open-source Thai TTF font (e.g. Bai Jamjuree).
2. Rename the `.ttf` extension to `.ufont` for all targeted font files.
3. Place them in the exact original directory structure (`WW/Content/UI/Fonts/`).

**Text Pipeline:**
1. Use UnrealLocres or FModel to export the original English `.locres` to `.csv` or `.json`.
2. Translate the strings into Thai.
3. Repack back into `.locres` format using UnrealLocres.
4. Pack all `.locres` and `.ufont` files into a `.pak` using `UnrealPak.exe` or `repak`. Make sure to name it `pakchunk99-WindowsNoEditor_X.pak` to ensure it loads with highest priority.

---

## 8. Troubleshooting
- **Game ignores the mod:** Ensure the PAK file has a higher chunk number (e.g. `pakchunk99`) than the base game paks.
- **Boxes instead of text:** The target `.ufont` file was not successfully replaced, or the TTF used lacks Thai glyphs.
- **Thai vowels/tone marks misaligned (สระลอย):** Ensure you are using a Thai font specifically designed with proper baseline alignment, or use a font pre-patched for non-CTL engines.

---

## 9. Required Tools
| Tool | Purpose | Source |
|---|---|---|
| repak / UnrealPak | Unpack and repack `.pak` files | GitHub (Epic Games / Rust RePak) |
| UnrealLocres | Convert `.locres` to `.csv` and back | GitHub |
| FModel | Explore base game files | GitHub |

---

## 10. Extracted Assets
The font was successfully extracted since it was just a raw TTF file inside the PAK.
- `BaiJamjuree-Medium.ttf` (Saved in `E:\Mod_Workspace\Modding-Knowledge\Engines\Unreal_Engine_4\Games\Werewolf_The_Apocalypse_Earthblood\Assets\Fonts\`)
