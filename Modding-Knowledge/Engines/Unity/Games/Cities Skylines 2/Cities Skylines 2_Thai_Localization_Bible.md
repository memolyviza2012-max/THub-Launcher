# Cities Skylines 2 — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Cities: Skylines 2 is a city-building game developed by Colossal Order on the Unity engine. The game features an official modding API, which this Thai localization mod leverages via C# Runtime Injection (IMod) to inject new locale assets dynamically.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Unity |
| **Developer** | Colossal Order |
| **Project Codename** | N/A |
| **Archive Format** | `.loc` (Custom Binary Localization Format) |
| **AES Encryption** | No / N/A |
| **Compression** | None |
| **Font System** | Built-in UI (Cohtml) font rendering |
| **Thai Font Used** | Unknown/Built-in |
| **Text System** | Custom Binary Database (.loc) with C# Asset Database integration |
| **Text Encoding** | UTF-8 |
| **Mod Complexity** | ★★☆☆☆ (Relies on official Modding API and `.loc` asset generation) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```
D:\Mods games\Thai Mods\0_Rivet Engineer\Cities Skylines 2\
├── Content\
│   └── th-TH.loc (2.6 MB) [Compiled Localization Binary]
├── Localization\
│   └── th-TH\ [Source JSON files for translations]
├── Sources\
│   └── ModsUI\ [UI Integration code]
├── Mod.cs (8 KB) [Mod Entry Point / IMod implementation]
└── Tools\
    └── GenLOC.py [Script to generate .loc file]
```

---

## 4. Font Analysis
- Font identification: The mod does not contain explicit font replacement. Cities: Skylines 2 UI uses web technologies (Cohtml) for its UI, which likely falls back to system fonts or game-provided web fonts for Thai rendering.
- Thai rendering considerations: Since the game uses a web-based UI layer, standard Thai rendering (floating vowels, tone marks) works automatically if the font supports it.

---

## 5. Text Analysis
- File format and encoding: The compiled `th-TH.loc` file is a custom binary structure parsed directly into a `Colossal.Localization.LocaleAsset`.
- Analysis found `592,020` Thai UTF-8 sequences in the compiled binary.
- The `th-TH.loc` header signature starts with `01 00 04 54 68 61 69 05 74 68 2D 54 48 15 E0 B8 A0 E0 B8 B2 E0 B8 A9 E0 B8 B2 E0 B9 84 E0 B8 97`. This corresponds to C# `BinaryReader` reading:
  - `UInt16` (0x0001)
  - `SystemLanguage` string (length 4, "Thai" = 54 68 61 69)
  - `Locale ID` string (length 5, "th-TH" = 74 68 2D 54 48)
  - `Localized Name` string (length 21 bytes, "ภาษาไทย" in UTF-8)
- After the header, it contains two dictionaries: one for standard string key-value pairs, and another for integer-mapped keys.

---

## 6. Cross-Engine Comparison
Unlike typical Unity games (where text is stored in `.bundle` asset files or `resources.assets`), Cities: Skylines 2 uses a custom Unity asset database system provided by Colossal Order. It loads `.loc` binaries using the `Colossal.IO.AssetDatabase` API. This is more akin to custom engine localization systems than standard Unity string tables.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
**Text Pipeline:**
1. Edit translations in the JSON source files located in `Localization\th-TH\`.
2. Run `Tools\GenLOC.py` to compile the JSON strings into the binary `th-TH.loc` format.
3. The C# code in `Mod.cs` handles loading this `th-TH.loc` at runtime by injecting a new `LocaleAsset` into `AssetDatabase.game` and forcing the `LocalizationManager` to switch to `th-TH`.

---

## 8. Troubleshooting
- **Locale not changing**: The mod checks if `th-TH` is already supported. Ensure that `_localizationManager.SetActiveLocale()` is called after loading the `.loc` asset.
- **Missing Strings**: Ensure the `GenLOC.py` correctly mapped the keys to the binary dictionary.

---

## 9. Required Tools
| Tool Name | Purpose | Download Source |
|---|---|---|
| Python (GenLOC.py) | Compiling JSON to `.loc` | Python.org |
| C# Compiler (.NET) | Compiling the Mod DLL | Microsoft |

---

## 10. Extracted Assets
No fonts were extracted as the mod relies on the game's built-in web-based UI font rendering which supports Thai natively.
