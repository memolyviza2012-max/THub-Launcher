# Darksiders II Deathinitive Edition — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Darksiders II Deathinitive Edition runs on the Vigil Engine (THQ). The Thai localization mod by Lung Dear is distributed as a custom standalone executable patcher (`ThaiMod-DarksidersII-LungDear.exe`) which directly modifies the base game's archive, specifically targeting `media.upak` to inject Thai strings and fonts.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Vigil Engine |
| **Developer** | Gunfire Games / Vigil Games |
| **Project Codename** | N/A |
| **Archive Format** | .upak |
| **AES Encryption** | No |
| **Compression** | Custom |
| **Font System** | Font Swap via Patcher |
| **Thai Font Used** | Sarabun (SIL Open Font License 1.1) |
| **Text System** | Embedded within .upak |
| **Text Encoding** | UTF-16 LE (Standard for Vigil Engine) |
| **Mod Complexity** | ★★★☆☆ (Mod uses automated binary patcher) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```text
D:\Mods games\Thai Mods\0_Rivet Engineer\Darksiders II\
├── ThaiMod-DarksidersII-LungDear.exe (15.8 MB) - Patcher executable
└── วิธีลง.txt - README file detailing installation and media.upak
```
*Note: The patcher is a custom compiled executable (MZ magic) rather than a standard 7-zip SFX.*

---

## 4. Font Analysis
- **Format:** The mod injects the "Sarabun" font (by Cadson Demak) directly into the game's UI layout stored in `media.upak`.
- **Thai rendering considerations:** Like Darksiders Warmastered, the Vigil Engine handles fonts via texture atlases or specific mapping files. The patcher automates the injection of these mapped textures.

---

## 5. Text Analysis
- **File format and encoding:** The text strings are packaged inside `media.upak`. Based on similarities to Darksiders Warmastered, they are likely UTF-16 LE encoded string maps.
- **Evidence:** The README confirms that `media.upak` is the primary target for localization modification.
- **Structure:** Strings are integrated into the proprietary UPAK archive system.

---

## 6. Cross-Engine Comparison
Both Darksiders I (Warmastered) and Darksiders II (Deathinitive) use iterations of the Vigil Engine. While Darksiders I uses `.mnfst` and `.oppc` pairs, Darksiders II consolidates assets into `.upak` archives. Modding Darksiders II requires a UPAK unpacker/repacker, whereas Darksiders I requires OPPC tools.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
**Text & Font Pipeline:**
1. **Unpacking:** Use a specialized Darksiders II `.upak` unpacker/repacker tool (e.g., QuickBMS UPAK script).
2. **Font Editing:** Locate the embedded font textures and mapping metadata. Replace them with the generated Sarabun font atlas and update the UV coordinates.
3. **Text Editing:** Extract the binary string files. Translate to Thai using UTF-16 LE encoding and repack the binary.
4. **Repacking:** Rebuild the `media.upak` file with the modified assets. (The mod author automated this step using a custom patcher script.)

---

## 8. Troubleshooting
- **SmartScreen Block:** Custom python-compiled patchers (like this mod's `.exe`) are often flagged by Windows Defender. Users must bypass SmartScreen to patch `media.upak`.
- **Game Crash:** If `media.upak` is corrupted during patching, the game will fail to load. A backup is strictly required.
- **V-Sync and Shadow Issues:** The README notes that V-Sync and Shadows can cause game instability, which is an engine quirk rather than a localization issue, but important for testing.

---

## 9. Required Tools
| Tool Name | Purpose | Download Source |
|---|---|---|
| QuickBMS (Darksiders 2 script) | Unpacking/Repacking .upak | Aluigi QuickBMS |
| Custom Patcher Source | Injecting files into UPAK directly | N/A |

---

## 10. Extracted Assets
Extraction failed. The mod is a pre-compiled `.exe` patcher, preventing direct extraction of the Sarabun font or text strings without first patching a vanilla `media.upak` file and unpacking it.
See `EXTRACTION_NOTE.txt` for details.
