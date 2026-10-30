# Call of Duty: Ghosts — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Call of Duty: Ghosts is a first-person shooter developed by Infinity Ward running on the IW6 engine. The localization modding architecture follows a Highly Encrypted Archive pattern, where all localized UI strings and fonts are packaged into proprietary FastFiles (`.ff`). Because offline decompilation of IW6 `.ff` files is highly restricted, memory hooking during runtime is the primary strategy for asset extraction.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | IW Engine (IW6) |
| **Developer** | Infinity Ward |
| **Project Codename** | N/A |
| **Archive Format** | FastFile (`.ff`) and standard Pak (`.pak` for media) |
| **AES Encryption** | N/A (Uses LZX Compression and proprietary obfuscation instead of AES) |
| **Compression** | LZX / Zlib (Custom IW block format starting with `IWffu100`) |
| **Font System** | Custom Bitmap/SDF |
| **Thai Font Used** | N/A (Extraction Pending) |
| **Text System** | Binary String Tables |
| **Text Encoding** | Unknown (Likely UTF-8, but compressed) |
| **Mod Complexity** | ★★★★★ (Requires memory hooking and undocumented repacking) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```text
Call of Duty Ghosts/
├── english/
│   ├── eng_ui.ff           # Main UI Strings (Target for translation)
│   ├── eng_common.ff       # Common Strings
│   ├── eng_code_post_gfx.ff
│   └── eng_soundfile*.pak  # Audio files
├── ui.ff                   # UI Logic and Layouts
├── common.ff               # Common Assets
└── iw6sp64_ship.exe        # Main Game Executable
```

---

## 4. Font Analysis
- Font identification: Stored inside `.ff` files, likely as texture atlases (`.iwi` or similar image formats) accompanied by a binary mapping file for glyph dimensions.
- Because offline extraction failed, the exact format is unconfirmed but historical IW engines use raw bitmap textures for fonts.
- Thai rendering considerations: Since the engine does not natively support complex text shaping for Thai, standard PUA (Private Use Area) injection for floating vowels and tone marks (สระลอย/วรรณยุกต์) will be mandatory.

---

## 5. Text Analysis
- File format: Compiled String Tables inside `IWffu100` archives.
- A brute-force zlib extraction of `eng_ui.ff` yields a 44MB binary file containing asset references, but the text strings are obfuscated or further compressed.
- Texts are generally organized in key-value pairs (e.g., `MENU_CAMPAIGN` -> `Campaign`).

---

## 6. Cross-Engine Comparison
Compared to older IW engine games (CoD4, WaW, MW2), which had robust community tools like *CoD-FF-Tools* for seamless unpacking and repacking, IW6 (Ghosts) overhauled the FastFile structure. Modders cannot use `offzip` or standard BMS scripts here. Instead, it closely mirrors the closed ecosystem of modern CoD titles where **Greyhound** (a memory scraper) is the only viable method to extract assets, similar to the process used for *Black Ops III* and *Modern Warfare 2019*.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
**Text & Font Pipeline:**
1. **Extraction (Live):** Launch *Call of Duty: Ghosts*. Wait for the Main Menu to load.
2. Launch **Greyhound**. Hook into the `iw6sp64_ship.exe` process.
3. Export `StringTable` and `Font` assets.
4. **Translation:** Edit the exported CSV/JSON string tables.
5. **Repacking:** Due to the lack of an IW6 `.ff` repacker, translated strings must be injected either via a custom DLL memory hook (like an ASI loader), or by overriding the `english` folder with raw parsed strings if the engine's `fs_game` / loose files flag is enabled.

---

## 8. Troubleshooting
- **Game crash after mod installation:** The IW6 engine is highly sensitive to FastFile sizes. If using a brute-force hex replacement on `.ff` files, the new string MUST perfectly match the byte length of the original string (padded with spaces).
- **Thai vowels/tone marks misaligned (สระลอย):** Ensure the font texture atlas has been updated and the UV coordinates in the font mapping file correctly point to the PUA characters.
- **Greyhound fails to attach:** Ensure no anti-cheat is active, and run Greyhound as Administrator.

---

## 9. Required Tools
| Tool | Purpose | Download |
|---|---|---|
| Greyhound | Memory hooking and asset extraction | https://github.com/Scobalula/Greyhound |
| HxD | Hex editing raw files (fallback method) | https://mh-nexus.de/en/hxd/ |

---

## 10. Extracted Assets
[EXTRACTION_NOTE.txt](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/IW_Engine/Games/Call_of_Duty_Ghosts/Assets/Fonts/EXTRACTION_NOTE.txt)

---

## 11. M2M Protocol
**Automated Extraction is BLOCKED:**
Since Greyhound requires a live game process and manual UI interaction, M2M automation for extraction is technically impossible without the game running. 
If an AI agent needs to translate this game in a headless environment, it must prompt the human user to complete Phase 1 manually using Greyhound, or write a memory patching ASI plugin in C++ to detour the `R_DrawText` or `StringTable_Lookup` functions at runtime.
