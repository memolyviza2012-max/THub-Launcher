# Darksiders Warmastered Edition — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Darksiders Warmastered Edition runs on a custom engine originally developed by Vigil Games and later adapted by THQ Nordic/Kaiko. The mod utilizes a File Replacement architecture, modifying the `media/pc.mnfst` manifest and `media/ui_en.oppc` packages to inject Thai text and fonts directly into the game's UI layout.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Vigil / THQ Custom Engine |
| **Developer** | Kaiko / THQ Nordic (Orig. Vigil Games) |
| **Project Codename** | N/A |
| **Archive Format** | .mnfst (Manifest) / .oppc (Object Package) |
| **AES Encryption** | No |
| **Compression** | Unknown |
| **Font System** | Font Swap |
| **Thai Font Used** | Unknown |
| **Text System** | Binary String Map in .oppc |
| **Text Encoding** | UTF-16 LE (94+ chars found in ui_en.oppc) |
| **Mod Complexity** | ★★★☆☆ (Requires .mnfst / .oppc repackers) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```text
D:\Mods games\Thai Mods\0_Rivet Engineer\Darksiders Warmastered\Darksiders-Warmastered-Thai-by-LungDear\
├── media\
│   ├── pc.mnfst (3.8 MB) - Resource manifest/index file
│   └── ui_en.oppc (161 KB) - UI and Text object package (Magic: OBPK)
└── Install/Uninstall scripts (.ps1, .bat) + README
```

---

## 4. Font Analysis
- **Format:** Fonts are either stored as embedded data in the `.oppc` packages or defined via the `pc.mnfst` manifest linking to font texture resources. 
- **Thai rendering considerations:** Darksiders uses standard bitmap or structured fonts. Thai tone marks and floating vowels (สระลอย) must be baked or specifically injected into the font system, as the native Vigil engine does not support dynamic complex text shaping.

---

## 5. Text Analysis
- **File format and encoding:** The text data resides in `ui_en.oppc` using **UTF-16 LE** encoding.
- **Evidence:** Analysis of the `ui_en.oppc` binary revealed 94 Thai UTF-16LE characters. The file header magic is `OBPK` (`4F 42 50 4B`).
- **Structure:** The `.oppc` format is a proprietary package format holding UI strings, coordinates, and localization keys.

---

## 6. Cross-Engine Comparison
Unlike Unreal Engine's `.pak` and `.locres`, the Vigil engine uses a highly proprietary `.oppc` and `.mnfst` pair. This is conceptually similar to the Disrupt engine's FAT/DAT combo but on a more granular level, often separating UI and localized strings into specific `_en` or `_ru` suffixed files rather than a single monolithic dat file.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
**Text & Font Pipeline:**
1. **Unpacking:** Utilize community tools for Darksiders `.oppc` and `.mnfst` (e.g., quickbms scripts or Darksiders modding tools).
2. **Font Editing:** Locate font map assets. Inject Thai glyphs into the font texture atlases and update the coordinate XML/binaries.
3. **Text Editing:** Extract the string tables from `ui_en.oppc`. Translate to Thai ensuring UTF-16 LE encoding is preserved.
4. **Repacking:** Repack the modified strings back into `ui_en.oppc` and ensure `pc.mnfst` correctly maps the updated file offsets and sizes.

---

## 8. Troubleshooting
- **Missing UI Elements:** An improperly packed `ui_en.oppc` will cause the UI to disappear entirely or crash the game.
- **Text showing as '?' or boxes:** The font texture atlas was not updated, or the encoding in the `.oppc` file broke the expected UTF-16 LE structure.
- **Thai text spacing issues:** Floating vowels may overlap or separate incorrectly due to a lack of engine-level text shaping (requires pre-shaping the text in the string file).

---

## 9. Required Tools
| Tool Name | Purpose | Download Source |
|---|---|---|
| Darksiders Modding Tools / QuickBMS | Unpacking/Repacking .oppc and .mnfst | GitHub/Zenhax |
| HxD Hex Editor | Validating OBPK magics and offsets | https://mh-nexus.de/en/hxd/ |

---

## 10. Extracted Assets
Extraction of raw `.ttf` files directly from `pc.mnfst` and `ui_en.oppc` failed due to the engine using proprietary font formats or texture atlases.
See `EXTRACTION_NOTE.txt` for details.
