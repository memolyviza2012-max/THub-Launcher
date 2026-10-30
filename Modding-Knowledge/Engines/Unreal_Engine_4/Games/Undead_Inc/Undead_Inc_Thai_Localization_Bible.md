# Undead Inc â€” Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Undead Inc is a resource management simulator developed by Rightsized Games and built on Unreal Engine 4. The Thai localization mod follows a standard "File Replacement" pattern, using `_P` (patch) pak files to inject localized text (`.locres`) and fonts into the game's file system at runtime.

---

## 2. Technical Stack
| à¸£à¸²à¸¢à¸ à¸²à¸£ | à¸£à¸²à¸¢à¸¥à¸°à¹€à¸­à¸µà¸¢à¸” |
|---|---|
| **Game Engine** | Unreal Engine 4 |
| **Developer** | Rightsized Games |
| **Project Codename** | RSG_Parasol |
| **Archive Format** | .pak (Unreal Engine Standard) |
| **AES Encryption** | No |
| **Compression** | Zlib |
| **Font System** | Font Swap (.ufont replacement) |
| **Thai Font Used** | Noto Sans Regular (TrueType) |
| **Text System** | LocRes (Binary) |
| **Text Encoding** | UTF-16 LE (Unreal locres standard) |
| **Mod Complexity** | â˜…â˜…â˜†â˜†â˜† (Standard UE4 pak modding, no encryption, standard font formats) |

---

## 3. à¹‚à¸„à¸£à¸‡à¸ªà¸£à¹‰à¸²à¸‡à¹„à¸Ÿà¸¥à¹Œ (File Architecture)
```text
Undead Inc
â””â”€â”€ RSG_Parasol
    â””â”€â”€ Content
        â””â”€â”€ Paks
            â”œâ”€â”€ Font-WindowsNoEditor_P.pak (4.4 MB) - Contains font overrides
            â””â”€â”€ Thai-WindowsNoEditor_P.pak (23.9 MB) - Contains text translations
```
*Note: The font and text are separated into two patch paks for modularity.*

---

## 4. Font Analysis
- **Font Identification**: The mod uses `Noto Sans Regular` (TrueType, `00 01 00 00` magic header). 
- **Storage**: Fonts are stored as raw `.ttf` files simply renamed with the `.ufont` extension. There is no texture atlas or SDF texture involved in the core font override.
- **Font Swap Mapping**: The mod targets `NotoSans-Regular.ufont` (and its variants: Bold, Italic, Black, etc.) located in `RSG_Parasol\Content\_BaseGame\Art\Font\Familys\NotoSans\`. It also overrides Engine fonts (e.g., `Roboto`) in `Engine\Content\EngineFonts\Faces\`.
- **Thai Rendering Considerations**: Since it's a standard UE4 font implementation without a custom shaping proxy DLL, Thai vowel/tone marks (à¸ªà¸£à¸°à¸¥à¸­à¸¢, à¸§à¸£à¸£à¸“à¸¢à¸¸à¸ à¸•à¹Œ) may require standard UE4 font assets with correct kerning, or text shaping strings, depending on the engine's built-in shaping support (HarfBuzz).

---

## 5. Text Analysis
- **File Format & Encoding**: The text is stored in Unreal Engine's binary `.locres` format (magic `0E 14 74 75 67 4A 03 FC...`). It utilizes UTF-16 LE encoding internally.
- **Structure**: The primary translation file is located at `RSG_Parasol\Content\Localization\BaseGame\en-US\BaseGame.locres`. The mod replaces the English localization directory to force the game to load Thai when English is selected.
- **String Count**: The primary `BaseGame.locres` file size indicates thousands of strings (text data size is ~1.6MB). There is also a `Game.locres` in `RSG_Parasol\Content\Localization\Game\th\`.

---

## 6. Cross-Engine Comparison
Like many standard Unreal Engine 4 games (e.g., *Marvel's Midnight Suns*, *The Outer Worlds*), Undead Inc utilizes the standard `_P.pak` file patching mechanism. It does not employ IoStore (`.ucas`/`.utoc`) like newer UE5 titles (e.g., *Avowed* or *S.T.A.L.K.E.R. 2*), and it doesn't require AES decryption, making it highly accessible. The font implementation is also standard `.ufont` renaming, similar to *Ghostrunner*.

---

## 7. Pipeline â€” à¸‚à¸±à¹‰à¸™à¸•à¸­à¸™à¸ªà¸£à¹‰à¸²à¸‡à¸¡à¹‡à¸­à¸”
### Font Pipeline:
1. Select a Thai-supported TTF font (e.g., Noto Sans Thai).
2. Rename the `.ttf` extension to `.ufont`.
3. Replicate the directory structure: `RSG_Parasol\Content\_BaseGame\Art\Font\Familys\NotoSans\`.
4. Pack the directory into a `.pak` file with the `_P` suffix using `UnrealPak` or `repak_cli`.

### Text Pipeline:
1. Extract the original `BaseGame.locres` using UnrealLocres.
2. Edit the generated `.csv` or `.txt` translation file.
3. Repack the text file back to `.locres` format using UnrealLocres.
4. Place it in `RSG_Parasol\Content\Localization\BaseGame\en-US\`.
5. Pack the directory into a `.pak` file with the `_P` suffix.

---

## 8. Troubleshooting
- **Thai vowels/tone marks misaligned (à¸ªà¸£à¸°à¸¥à¸­à¸¢)**: Ensure the font used has appropriate glyph substitutions (GSUB/GPOS) that UE4's text renderer supports, or pre-shape the text before injecting it into the `.locres` file.
- **Text shows up as English**: Check if the language setting in the game matches the localized directory in the mod (e.g., `en-US`).
- **Mod not loading**: Ensure the pak file is placed in `RSG_Parasol\Content\Paks\` and correctly has the `_P` suffix.

---

## 9. Required Tools
| Tool Name | Purpose | Source |
|---|---|---|
| **repak_cli / UnrealPak** | Unpacking and packing `.pak` archives | [GitHub (repak)](https://github.com/trumank/repak) |
| **UnrealLocres** | Converting `.locres` to text and back | [GitHub](https://github.com/akintos/UnrealLocres) |
| **FModel** | Viewing package structures without extracting | [FModel.app](https://fmodel.app/) |

---

## 10. Extracted Assets
- **Extracted Font**: [NotoSans-Regular.ttf](./Assets/Fonts/NotoSans-Regular.ttf)
*Note: The font was stored as a raw TTF with a `.ufont` extension, allowing direct extraction by simply renaming it.*
