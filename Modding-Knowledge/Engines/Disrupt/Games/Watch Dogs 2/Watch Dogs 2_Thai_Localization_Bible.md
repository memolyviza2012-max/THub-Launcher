# Watch Dogs 2 — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Watch Dogs 2 is an open-world action-adventure game by Ubisoft using the Disrupt Engine. Mods are typically distributed as patch archives (`.dat` and `.fat`).

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Disrupt Engine |
| **Developer** | Ubisoft Montreal |
| **Project Codename** | N/A |
| **Archive Format** | .dat / .fat |
| **AES Encryption** | No |
| **Compression** | Custom Ubisoft Compression |
| **Font System** | Embedded in archives |
| **Thai Font Used** | Unknown (needs extraction) |
| **Text System** | Binary |
| **Text Encoding** | UTF-8 |
| **Mod Complexity** | ★★★☆☆ |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```
[Mod Root]
├── patch3.dat (68 MB)
└── patch3.fat (216 B)
```

---

## 4. Font Analysis
- Font identification: Fonts are packed inside the `.dat` file.
- How fonts are stored: Typically proprietary formats inside the archive.
- Font swap mapping: N/A.
- Thai rendering considerations: Custom shaping may be needed depending on the UI middleware (likely Scaleform).

---

## 5. Text Analysis
- File format and encoding: Binary localization files within the archive.
- How text is structured: String IDs mapped to text.
- Approximate string count / file size: The `.dat` patch is 68 MB and contains updated assets and text.
- Quest/dialogue organization structure: Binary structured lists.

---

## 6. Cross-Engine Comparison
The Disrupt engine uses a classic FAT (File Allocation Table) and DAT (Data) archive structure similar to older Anvil engines. Modifications require rebuilding the `.dat` file and updating the `.fat` index, unlike games with loose files or simple zip archives.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
**Font & Text Pipeline:**
1. Unpack `patch3.dat` using Disrupt Engine unpacking tools (e.g., Gibbed's Disrupt Tools).
2. Edit localized strings.
3. Repack and update the `.fat` file to ensure correct offsets.

---

## 8. Troubleshooting
- Mod not loading: Ensure the `.fat` index matches the `.dat` file.
- Crashes: Usually due to incorrect archive packing.

---

## 9. Required Tools
| Tool Name | Purpose | Source |
|---|---|---|
| Gibbed's Disrupt Tools | Extract/Repack .dat/.fat files | Github |

---

## 10. Extracted Assets
Extraction failed. Fonts are embedded in `.dat`.
[EXTRACTION_NOTE.txt](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Disrupt/Games/Watch%20Dogs%202/Assets/Fonts/EXTRACTION_NOTE.txt)

---

## 11. M2M Protocol
**Automated Font Rendering Script (Python):** N/A
**Automated Text Shaping Script (Regex):**
```python
import re
def shape_thai(text):
    text = re.sub(r'([ปฝฟ])([ิีึืุู])([่้๊๋])', r'\1\3\2', text)
    return text
```
