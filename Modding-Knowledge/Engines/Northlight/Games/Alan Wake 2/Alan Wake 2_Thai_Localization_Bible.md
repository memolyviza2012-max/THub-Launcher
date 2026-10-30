# Alan Wake 2 — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Alan Wake 2 is an acclaimed survival horror game developed by Remedy Entertainment using their proprietary Northlight Engine. The mod architecture pattern here is a Hybrid, utilizing a file replacement for fonts and a DLL/ASI injection (mod-loader.asi) alongside binary string replacements.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Northlight Engine |
| **Developer** | Remedy Entertainment |
| **Project Codename** | N/A |
| **Archive Format** | Custom / RMDP |
| **AES Encryption** | No |
| **Compression** | Unknown |
| **Font System** | Font Swap / Runtime Injection |
| **Thai Font Used** | Noto Sans Thai ExtraBold |
| **Text System** | Binary (.bin) |
| **Text Encoding** | UTF-16 LE |
| **Mod Complexity** | ★★★★☆ |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```
[Mod Root]
├── d3d12.dll
├── วิธีติดตั้ง.txt
├── plugins/
│   └── mod-loader.asi (1.6 MB)
└── data/
    ├── locale/en/string_table.bin (6.1 MB)
    └── uiresources/game/fonts/
        ├── aktivgroteskcd_*.ttf
        ├── aktivgroteskex_*.ttf
        └── gamertag/notosansthai-regular.ttf (20 KB)
```

---

## 4. Font Analysis
- Font identification: The game uses multiple fonts including Aktiv Grotesk. The Thai font injected is Noto Sans Thai ExtraBold.
- How fonts are stored: Fonts are stored as raw `.ttf` and `.otf` files inside the `data\uiresources\game\fonts\` structure.
- Font swap mapping: The mod overrides native fonts and places the Thai font inside the `gamertag` directory, likely hooked by the ASI loader or game UI.
- Thai rendering considerations: Since raw TTF files are used, standard Windows font rendering may apply, depending on Northlight UI support.

---

## 5. Text Analysis
- File format and encoding: The primary text file is `string_table.bin`. It uses **UTF-16 LE** encoding.
- How text is structured: Key-value binary format starting with Magic Bytes `4E AB 00 00`. Strings are separated with standard null/control characters and UTF-16 encoding.
- Approximate string count / file size: Over 69,000 Thai character instances found in the first 1MB of the 6.1MB file.
- Quest/dialogue organization structure: Key names like `SAVE_SLOT_RETURN_0` are visible.

---

## 6. Cross-Engine Comparison
Compared to Unreal Engine which uses `.locres` for localized text, Northlight Engine uses its proprietary `string_table.bin`. Modifying this requires custom tools or hex editing, hence the inclusion of an ASI mod loader to hook string loading or bypass integrity checks.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
**Font Pipeline:**
1. Generate or download a TTF font that supports Thai (e.g., Noto Sans Thai).
2. Place it into the `data\uiresources\game\fonts\` matching the directory structure of the game's extracted files.

**Text Pipeline:**
1. Extract `string_table.bin`.
2. Convert the UTF-16 LE binary into a translatable format (CSV/JSON) using custom scripts.
3. Repack the binary keeping the identical structure and `4E AB` header.
4. Use `d3d12.dll` and `mod-loader.asi` to ensure the modded files are loaded by the game.

---

## 8. Troubleshooting
- Font not displaying: Check if the ASI loader is correctly placed in the same directory as the game executable.
- Thai vowels/tone marks misaligned (สระลอย): If Northlight doesn't support complex text shaping, an automatic shaper script may be required.
- Game crash after mod installation: Ensure the `string_table.bin` file size/offsets match the required structure exactly if not dynamically allocated.
- Encoding corruption: Always save as UTF-16 LE.

---

## 9. Required Tools
| Tool Name | Purpose | Source |
|---|---|---|
| ASI Loader (d3d12.dll) | Hooking game engine functions to load mods | Ultimate ASI Loader |
| Custom Bin Unpacker | Unpacking string_table.bin | Community Tools |

---

## 10. Extracted Assets
- [NotoSansThai-ExtraBold.ttf](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Northlight/Games/Alan%20Wake%202/Assets/Fonts/NotoSansThai-ExtraBold.ttf)
- [AktivGroteskCD-Regular.ttf](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Northlight/Games/Alan%20Wake%202/Assets/Fonts/AktivGroteskCD-Regular.ttf)

---

## 11. M2M Protocol
**Automated Font Rendering Script (Python):** (N/A - Direct TTF Supported)
**Automated Text Shaping Script (Regex):**
```python
import re
def shape_thai(text):
    # Basic shaping rules for Thai vowels and tones
    text = re.sub(r'([ปฝฟ])([ิีึืุู])([่้๊๋])', r'\1\3\2', text)
    return text
```
