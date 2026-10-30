# Bloodstained: Ritual of the Night — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Bloodstained: Ritual of the Night is built on Unreal Engine 4. The localization mod uses a standard file replacement pattern for both fonts (raw TTFs renamed to `.ufont`) and text (which is embedded directly into cooked `.uasset`/`.uexp` files instead of standard `.locres`).

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Unreal Engine 4 |
| **Developer** | ArtPlay |
| **Project Codename** | BloodstainedRotN |
| **Archive Format** | .pak (Standard UE4) |
| **AES Encryption** | No |
| **Compression** | Zlib / None |
| **Font System** | Font Swap (Raw TTF injected as .ufont) |
| **Thai Font Used** | NewCezannePro-M / Press Start Regular |
| **Text System** | Embedded StringTables (.uasset / .uexp) |
| **Text Encoding** | UTF-16 LE / UTF-8 |
| **Mod Complexity** | ★★★☆☆ (Requires UAssetGUI/UAssetAPI to edit strings safely) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```text
pakchunk1-WindowsNoEditor.pak (1.7 MB)
├── BloodstainedRotN/Content/Core/Font/
│   ├── FOT-NewCezannePro-M.ufont (116 KB)
│   ├── OpenSans-Regular.ufont (116 KB)
│   ├── misaki_gothic.ufont (153 KB)
│   └── (Other font overrides)
└── BloodstainedRotN/Content/L10N/en/Core/UI/
    ├── UI_Pause/Menu/CraftMenu/
    ├── UI_Pause/Menu/EquipMenu/
    └── (Multiple UI .uasset and .uexp files containing text)
```

---

## 4. Font Analysis
- **Font Identification**: The mod replaces multiple standard fonts (`FOT-NewCezannePro`, `OpenSans`, `misaki_gothic`) with Thai-supported raw `.ttf` files.
- **How fonts are stored**: Fonts are stored as raw TTF data (magic `00 01 00 00` at offset 0) renamed to `.ufont`. 
- **Font swap mapping**: By replacing `FOT-NewCezannePro-M` and `OpenSans`, the mod ensures UI elements referencing these engine/game fonts will render Thai characters. The pixel fonts (`misaki_gothic`) were also replaced with a pixel font (`Press Start Regular`) that supports Thai.
- **Thai rendering considerations**: Since raw TTF is used, complex rendering (สระลอย) relies heavily on UE4's default shaping. 

---

## 5. Text Analysis
- **File format and encoding**: Unlike most UE4 games which use `.locres`, Bloodstained stores its localized UI text directly inside cooked UI assets (`.uasset` and `.uexp`). 
- **Text Structure**: Text is structured as standard UE4 FString properties inside the UI widgets or StringTables.
- **String Count**: Highly fragmented across hundreds of UI widget files.
- **Quest/dialogue organization**: Separated by UI screen (e.g., CraftMenu, EquipMenu, LoadMenu).

---

## 6. Cross-Engine Comparison
Compared to *Atomic Heart* and *ACE COMBAT 7*, *Bloodstained* handles its UI text much more rigidly by embedding localized text directly into the cooked UI assets (`.uasset`/`.uexp`) in the `L10N` folder, rather than relying on a centralized `.locres` or `.dat` file. However, its font injection method is identical to *Atomic Heart*, using raw `.ttf` files simply renamed to `.ufont`. No AES encryption is used.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
**Font Pipeline:**
1. Select appropriate Thai fonts (e.g., a standard sans-serif and a pixel font).
2. Rename the raw `.ttf` files to match the game's `.ufont` files (e.g., `FOT-NewCezannePro-M.ufont`).
3. Place them in `BloodstainedRotN/Content/Core/Font/`.

**Text Pipeline:**
1. Unpack the base game pak using `repak_cli`.
2. Locate the `.uasset`/`.uexp` files in `Content/L10N/en/Core/UI/`.
3. Use a tool like **UAssetGUI** or **FModel** to inspect the files.
4. Export the String properties, translate to Thai, and re-import them carefully using UAssetGUI to maintain correct byte offsets and string lengths.
5. Repack everything using `repak_cli` into `pakchunk1-WindowsNoEditor.pak`.

---

## 8. Troubleshooting
- **Game crash upon UI opening**: The `.uexp` file was likely corrupted during string editing. When editing `.uexp` in a hex editor without UAssetGUI, the FString length prefix (int32) MUST be updated to match the new string length (including the null terminator), and UTF-16 strings must have negative length values.
- **Font not displaying**: Ensure the font replacement covers all variants (Bold, Italic, Regular) used by the UI.

---

## 9. Required Tools
| Tool | Purpose | Download Source |
|---|---|---|
| **repak_cli** | Unpack and repack UE4 .pak files | [GitHub - repak](https://github.com/trumank/repak) |
| **UAssetGUI** | Edit FStrings inside cooked .uasset/.uexp safely | [GitHub - atenfyr/UAssetGUI](https://github.com/atenfyr/UAssetGUI) |

---

## 10. Extracted Assets
- [NewCezannePro-M.ttf](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/UnrealEngine4/Games/Bloodstained/Assets/Fonts/NewCezannePro-M.ttf)

---

## 11. M2M Protocol
**Automated Font Rendering Script (Python):**
```python
# N/A for standard UE4 - TTF is supported natively
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
