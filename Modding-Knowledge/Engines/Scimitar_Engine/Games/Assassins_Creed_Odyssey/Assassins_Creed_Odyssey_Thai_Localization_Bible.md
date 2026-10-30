# Assassin's Creed Odyssey — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Assassin's Creed Odyssey runs on the Scimitar/Anvil Engine. Unlike simple `.forge` patches, this mod leverages a specialized tool called **Forger** to dynamically apply patches (`.forger2` project and `.acod` payload files) into the game at runtime or installation time.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Scimitar/Anvil Engine |
| **Developer** | Ubisoft |
| **Project Codename** | Unknown |
| **Archive Format** | `.forger2` (project) + `.acod` (text payloads) |
| **AES Encryption** | No |
| **Compression** | Oodle (`oo2core_7_win64.dll` included with Forger) |
| **Font System** | Unknown (likely natively supported or injected via Forger) |
| **Thai Font Used** | Unknown |
| **Text System** | Plain text / CSV with BOM |
| **Text Encoding** | UTF-16 LE (Byte Order Mark: `FF FE`) |
| **Mod Complexity** | ★★★☆☆ (Requires external tool `Forger.exe` for application) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```
Assassin creed odyssey/
├── Forger Utility/
│   ├── Forger.exe (367 KB)
│   ├── Newtonsoft.Json.dll
│   └── oo2core_7_win64.dll (Oodle compression)
├── Kassandra_Thai/
│   ├── Kassandra Sub By Manol.forger2 (327 KB - Forger project)
│   └── Thai Subtitles By Mamol/
│       ├── Alexios_ThaiManol_Sub-*.acod (4.6 MB)
│       ├── Alexios_ThaiManol_UI-*.acod (3.3 MB)
│       └── ... (Multiple .acod files for Base game + DLCs 1-5)
```

---

## 4. Font Analysis
No raw font files (`.ttf` or `.otf`) were discovered in the mod's payload. The text payloads only contain the modified strings. The actual font rendering may be handled natively by the game, or another `.acod` file not clearly named as a font could contain font data. Without extracted fonts, no specific TrueType font can be isolated.

---

## 5. Text Analysis
- **Format**: `.acod` files are plain text or structured data payloads.
- **Encoding**: UTF-16 Little Endian.
- **Content**: The `.acod` files start with the magic bytes `FF-FE`, indicating a UTF-16 LE BOM. Hex analysis confirms Thai characters are stored in UTF-16 LE (e.g., `0E 0E` for 'ภ', `01 0E` for 'ก'). The files are segregated into `SUB` (Subtitles) and `UI` (User Interface), and further divided by character choice (Alexios vs. Kassandra) and DLC expansions.

---

## 6. Cross-Engine Comparison
While Shadows and Mirage use pre-patched `.forge` files, Odyssey's modding community created **Forger**, a specialized utility that injects modifications. This approach is highly sophisticated because it avoids distributing massive `.forge` files. Instead, it distributes tiny text payloads (`.acod`) and patches them locally on the user's machine using `Forger.exe` and Oodle compression `oo2core_7_win64.dll`.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
**Text Pipeline:**
1. Use `Forger.exe` to inspect and extract strings from the base game.
2. Translate strings and save them in `.acod` format using UTF-16 LE encoding.
3. Configure the `.forger2` project file (JSON-based) to map the `.acod` files to their respective injection points.
4. Run `Forger.exe` to apply the mod to the game's original `.forge` files.

---

## 8. Troubleshooting
- **Forger error on apply**: Ensure `oo2core_7_win64.dll` and `Newtonsoft.Json.dll` are in the same folder as `Forger.exe`.
- **Text shows as gibberish**: The `.acod` file must be saved with **UTF-16 LE with BOM**. UTF-8 will break the text ingestion.
- **Game updates break mod**: Since Forger relies on specific offsets or structures, an official game update may require a new `.forger2` mapping.

---

## 9. Required Tools
| Tool Name | Purpose | Download Source |
|---|---|---|
| Forger Utility | Applying `.forger2` mods | NexusMods / GitHub |
| Text Editor (VS Code / Notepad++) | Editing `.acod` files (ensure UTF-16 LE encoding) | Built-in / Online |

---

## 10. Extracted Assets
No fonts were extracted for this game as none were present in the `.acod` payloads. See `EXTRACTION_NOTE.txt` for details.
