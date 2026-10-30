# Medieval Dynasty â€” Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Medieval Dynasty is a survival and town-building game developed by Render Cube and built on Unreal Engine 4. The Thai localization mod uses a **Hybrid Pattern**, employing standard `_P.pak` files for assets and a Runtime Injection method via a proxy DLL (`dsound.dll` -> `bitfix.dll`) and a Lua script (`universal.lua`) to patch font rendering issues natively in memory.

---

## 2. Technical Stack
| à¸£à¸²à¸¢à¸ à¸²à¸£ | à¸£à¸²à¸¢à¸¥à¸°à¹€à¸­à¸µà¸¢à¸” |
|---|---|
| **Game Engine** | Unreal Engine 4 |
| **Developer** | Render Cube |
| **Project Codename** | Medieval_Dynasty |
| **Archive Format** | .pak (Unreal Engine Standard) |
| **AES Encryption** | No |
| **Compression** | Zlib |
| **Font System** | Font Swap (.ufont) + Runtime Memory Patching |
| **Thai Font Used** | KingthingsPetrockPro (TrueType) |
| **Text System** | LocRes (Binary) |
| **Text Encoding** | UTF-16 LE (Unreal locres standard) |
| **Mod Complexity** | â˜…â˜…â˜…â˜…â˜† (Requires understanding of runtime DLL proxy injection and Lua memory patching for font rendering fixes) |

---

## 3. à¹‚à¸„à¸£à¸‡à¸ªà¸£à¹‰à¸²à¸‡à¹„à¸Ÿà¸¥à¹Œ (File Architecture)
```text
Medieval_Dynasty
â”œâ”€â”€ Binaries
â”‚   â””â”€â”€ Win64
â”‚       â”œâ”€â”€ bitfix.dll (1.2 MB) - Memory patcher DLL
â”‚       â”œâ”€â”€ dsound.dll (1.2 MB) - Proxy DLL to inject bitfix.dll
â”‚       â””â”€â”€ bitfix
â”‚           â””â”€â”€ universal.lua (1 KB) - Lua script for hooking hex patterns
â””â”€â”€ Content
    â””â”€â”€ Paks
        â””â”€â”€ Yaklongpae-ModThai_P.pak (4.1 MB) - Asset and Text translations
```

---

## 4. Font Analysis
- **Font Identification**: `KingthingsPetrockPro` and `KingthingsPetrockLightPro` (TrueType, `00 01 00 00` magic header).
- **Storage**: Fonts are packaged as `.ufont` files in the `.pak` archive (`Medieval_Dynasty\Content\Fonts\Kingthings_Petrock_Pro.ufont`).
- **Runtime Patching**: The game exhibits rendering issues with Thai text shaping (common in UE4). To resolve this, a `dsound.dll` proxy is used to inject `bitfix.dll` at runtime. The `universal.lua` script searches for the hex pattern `48 8D 0D ?? ?? ?? ?? E9 ...` and patches the jump instruction with `0xC3` (`RET`). This likely disables problematic UE4 text rendering logic (e.g., outline rendering, or forcing standard text shaping over a custom implementation) that breaks Thai vowels/tone marks.

---

## 5. Text Analysis
- **File Format & Encoding**: Binary `.locres` format (`Medieval_Dynasty\Content\Localization\Game\en\Game.locres`), UTF-16 LE internally.
- **Structure**: The text overrides the English localization folder `\en\`.
- **String Count**: The `Game.locres` is approximately 5.1 MB, suggesting a very large volume of dialogue and item descriptions typical of RPG survival games.

---

## 6. Cross-Engine Comparison
While standard UE4 games (like *Undead Inc* or *The Outer Worlds*) only use `.pak` swapping, Medieval Dynasty is comparable to complex hybrid mods (such as those seen with *Dragon Quest XI* or *Code Vein II* using external tools) because it requires runtime DLL injection to patch the engine's memory natively. This proxy DLL approach is a powerful technique for overriding engine limitations without recompiling the game executable.

---

## 7. Pipeline â€” à¸‚à¸±à¹‰à¸™à¸•à¸­à¸™à¸ªà¸£à¹‰à¸²à¸‡à¸¡à¹‡à¸­à¸”
### Font & Text Pipeline:
1. Extract the `Game.locres` using UnrealLocres, translate, and repack.
2. Prepare Thai `.ttf` fonts and rename them to `.ufont`.
3. Package both into `Yaklongpae-ModThai_P.pak` using `UnrealPak` or `repak_cli`.

### Injection Pipeline:
1. Compile or obtain a proxy DLL (e.g., `dsound.dll` or `xinput1_3.dll`) that loads `bitfix.dll`.
2. Write a Lua script (`universal.lua`) defining the signature scanner and patch payload (`0xC3`).
3. Distribute the `Binaries` folder alongside the `Content` folder.

---

## 8. Troubleshooting
- **Game crashes on startup**: The hex pattern in `universal.lua` might be outdated if the game updates. You will need to find the new memory address and update the pattern.
- **Font rendering issues (à¸ªà¸£à¸°à¸¥à¸­à¸¢)**: Check if `dsound.dll` and `bitfix.dll` are loaded correctly in `Binaries\Win64\`. If they are missing, the runtime memory patch won't execute.
- **Missing text**: Ensure `Yaklongpae-ModThai_P.pak` is inside `Content\Paks\`.

---

## 9. Required Tools
| Tool Name | Purpose | Source |
|---|---|---|
| **repak_cli / UnrealPak** | Unpacking/packing `.pak` archives | [GitHub (repak)](https://github.com/trumank/repak) |
| **UnrealLocres** | Modifying `.locres` binary files | [GitHub](https://github.com/akintos/UnrealLocres) |
| **x64dbg / Cheat Engine** | For finding memory patterns to patch | [x64dbg](https://x64dbg.com/) |

---

## 10. Extracted Assets
- **Extracted Font 1**: [Kingthings_Petrock_Pro.ttf](./Assets/Fonts/Kingthings_Petrock_Pro.ttf)
- **Extracted Font 2**: [Kingthings_Petrock_Light_Pro.ttf](./Assets/Fonts/Kingthings_Petrock_Light_Pro.ttf)
*Note: Fonts were extracted directly from `.ufont` files as they were stored uncompressed without UE4 asset wrapping.*
