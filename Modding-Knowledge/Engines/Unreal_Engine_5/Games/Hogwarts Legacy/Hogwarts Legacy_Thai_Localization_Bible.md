# Hogwarts Legacy — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Hogwarts Legacy utilizes Unreal Engine 5's IoStore architecture. The localization mod uses a File Replacement pattern, providing custom `.ucas`, `.utoc`, and a dummy `.pak` to override the base game's localized text and fonts.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Unreal Engine 5 |
| **Developer** | Avalanche Software |
| **Project Codename** | Hogwarts Legacy |
| **Archive Format** | UE5 IoStore (.ucas + .utoc + .pak) |
| **AES Encryption** | Likely (Requires AES key for full extraction) |
| **Compression** | Oodle |
| **Font System** | Unknown (IoStore Cooked .ufonts) |
| **Thai Font Used** | Unknown (Extraction Failed) |
| **Text System** | UE Localization (.locres via IoStore) |
| **Text Encoding** | UTF-16 LE |
| **Mod Complexity** | ★★★★☆ (IoStore repacking and UE5 Oodle compression required) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```text
D:\Mods games\Thai Mods\0_Rivet Engineer\Hogwarts Legacy\
├── zHWSign_P.pak (339 B)  - Dummy PAK for mount point registration
├── zHWSign_P.ucas (101 MB) - Contains the actual Oodle-compressed assets
└── zHWSign_P.utoc (29 KB)  - Table of Contents mapping the UCAS
```

---

## 4. Font Analysis
- **Font Identification**: Extraction failed due to IoStore limitations.
- **How fonts are stored**: Fonts are packed tightly inside the `zHWSign_P.ucas` file. UE5 generally uses standard cooked `.ufont` assets, often containing raw TTF or OTF data.
- **Font swap mapping**: N/A without extraction.
- **Thai rendering considerations**: UE5 handles complex text layout better than UE4, reducing the need for manual shaping of สระลอย and วรรณยุกต์ if standard TTF fonts are used correctly.

---

## 5. Text Analysis
- **File format and encoding**: The game uses standard `.locres` localization files, but they are cooked into the IoStore container.
- **Text Structure**: Standard UE String Tables, compressed with Oodle.
- **String Count**: The UCAS is large (101 MB), suggesting it contains significant portions of the game's localized text, UI data, and potentially large font assets.
- **Quest/dialogue organization**: Managed via standard UE Localization framework.

---

## 6. Cross-Engine Comparison
Unlike *ACE COMBAT 7*, *Atomic Heart*, and *Bloodstained* which all use standard UE4 `.pak` files without encryption, *Hogwarts Legacy* represents the modern UE5 approach. It uses the IoStore (`.ucas`/`.utoc`) which significantly complicates the modding pipeline. A 339-byte dummy `.pak` file must be included alongside the `.ucas`/`.utoc` files simply to force the engine to register the mod's mount point. This is a critical requirement for UE5 IoStore modding not seen in older engines.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
**Font & Text Pipeline:**
1. You must use Unreal Engine 5 (matching the game's exact minor version, e.g., 5.0 or 5.1).
2. Use a tool like **FModel** with the correct game AES key to extract the original `.locres` and `.ufont` files.
3. Edit the `.locres` using `UnrealLocres`.
4. Inject your Thai TTF into the `.ufont` using UE5 Editor or hex injection.
5. Cook the assets using the UE5 Editor with IoStore enabled (`bUseIoStore=True`).
6. Place the resulting `.ucas` and `.utoc` files into the `~mods` folder along with a generated dummy `.pak` file (created with UnrealPak).

---

## 8. Troubleshooting
- **Mod not loading**: Ensure you included the dummy `.pak` file alongside the `.ucas` and `.utoc`. Without it, UE5 will not mount the IoStore chunks.
- **Game crash**: Using the wrong Oodle compression version or incorrect UE5 version during cooking will instantly crash the game.

---

## 9. Required Tools
| Tool | Purpose | Download Source |
|---|---|---|
| **FModel** | Extract assets from UE5 IoStore | FModel.app |
| **Unreal Engine 5** | Cook modified assets into IoStore format | Epic Games Launcher |
| **UnrealPak** | Generate dummy `.pak` | Unreal Engine installation |

---

## 10. Extracted Assets
- [EXTRACTION_NOTE.txt](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/UnrealEngine5/Games/Hogwarts%20Legacy/Assets/Fonts/EXTRACTION_NOTE.txt)

---

## 11. M2M Protocol
**Automated Font Rendering Script (Python):**
```python
# N/A for standard UE5
pass
```
**Automated Text Shaping Script (Regex):**
```python
# Placeholder for shaping logic
pass
```
**Automated FNT/Mapping Injector (Struct):**
```python
# N/A
pass
```
