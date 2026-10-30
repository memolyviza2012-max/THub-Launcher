# Dyson Sphere Program — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Dyson Sphere Program is a factory simulation game built on Unity. The localization mod architecture uses a simple File Replacement pattern targeting plain text files for translations.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Unity |
| **Developer** | Youthcat Studio |
| **Project Codename** | DSP |
| **Archive Format** | Plain Text |
| **AES Encryption** | No |
| **Compression** | None |
| **Font System** | Unity Default / TextMeshPro |
| **Thai Font Used** | Depends on system/mod |
| **Text System** | Plain Text Key-Value |
| **Text Encoding** | UTF-8 |
| **Mod Complexity** | ★☆☆☆☆ (Extremely simple text replacement) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```
Dyson Sphere Program/
└── Locale/
    └── 1033/
        ├── base.txt (669 KB)
        ├── creation.txt (5 KB)
        ├── dictionary.txt (10 KB)
        └── prototype.txt (285 KB)
```

---

## 4. Font Analysis
- **Format**: Unity Asset Bundles / TextMeshPro (TMP).
- **Extraction**: Unity fonts usually require AssetStudio or UABEA for extraction. If the mod only translates text, it might rely on Unity's default fallback fonts or a BepInEx plugin for font injection.

---

## 5. Text Analysis
- **Format**: Plain text files (`.txt`).
- **Encoding**: Must be UTF-8 for Thai characters to render correctly.
- **Structure**: Simple Key-Value or line-based text, very easy to edit.

---

## 6. Cross-Engine Comparison
Unlike typical Unity games that hide text in `resources.assets` or AssetBundles, DSP exposes localization as loose text files in the `Locale` folder, making it much easier to mod than games like Disco Elysium.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
**Text Pipeline:**
1. Open the `.txt` files in `Locale/1033/` using Notepad++ or VSCode.
2. Ensure encoding is set to UTF-8.
3. Translate the values.
4. Save the files.

---

## 8. Troubleshooting
- **Encoding corruption**: If you see weird symbols instead of Thai, the file was likely saved in ANSI or Windows-874 instead of UTF-8.
- **Missing characters**: The game's default Unity font might lack Thai support, requiring a font replacement via BepInEx if boxes appear.

---

## 9. Required Tools
| Tool | Purpose | Source |
|---|---|---|
| VSCode / Notepad++ | Edit .txt files | Official Sites |

---

## 10. Extracted Assets
- [EXTRACTION_NOTE.txt](Assets/Fonts/EXTRACTION_NOTE.txt)
