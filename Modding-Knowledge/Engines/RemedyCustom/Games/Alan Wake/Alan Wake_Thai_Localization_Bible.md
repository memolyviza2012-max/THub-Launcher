# Alan Wake — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Alan Wake (Classic) is an action-adventure game by Remedy Entertainment running on their older custom engine. The mod architecture involves replacing `.rmdp` and `.bin` archives which contain the localized text and potentially fonts.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Remedy Custom Engine |
| **Developer** | Remedy Entertainment |
| **Project Codename** | N/A |
| **Archive Format** | .rmdp / .bin |
| **AES Encryption** | No |
| **Compression** | Custom |
| **Font System** | Embedded in archive |
| **Thai Font Used** | Unknown (needs extraction) |
| **Text System** | Binary (.rmdp) |
| **Text Encoding** | UTF-8/UTF-16 |
| **Mod Complexity** | ★★★☆☆ |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```
[Mod Root]
├── ep999-000-en.bin (187 KB)
├── ep999-000-en.rmdp (268 MB)
├── ep999-004-en.bin (296 B)
└── ep999-004-en.rmdp (743 KB)
```

---

## 4. Font Analysis
- Font identification: Fonts are not stored as loose files.
- How fonts are stored: Embedded within the `.rmdp` archives.
- Font swap mapping: N/A.
- Thai rendering considerations: Custom text shaping may be required.

---

## 5. Text Analysis
- File format and encoding: Binary formats within `.rmdp`.
- How text is structured: Likely compressed binary structures requiring a specific tool to unpack and repack.
- Approximate string count / file size: The primary file `ep999-000-en.rmdp` is 268 MB, containing majority of assets and localized text.
- Quest/dialogue organization structure: Handled by internal Remedy index files (`.bin`).

---

## 6. Cross-Engine Comparison
Unlike Alan Wake 2 (Northlight), the older Alan Wake game uses monolithic `.rmdp` files for data. Alan Wake 2 allows some loose files (`string_table.bin`) and ASI injection for easier modding.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
**Font & Text Pipeline:**
1. Extract `.rmdp` using a tool like Remedy Archive Unpacker.
2. Edit localized files.
3. Repack back into `.rmdp` structure.

---

## 8. Troubleshooting
- Mod not loading: Make sure `.bin` index matches `.rmdp` offsets perfectly.
- Crashes: Usually caused by offset mismatches.

---

## 9. Required Tools
| Tool Name | Purpose | Source |
|---|---|---|
| Alan Wake Unpacker | Extract/Repack .rmdp files | XeNTaX / Github |

---

## 10. Extracted Assets
Extraction failed. Fonts are embedded in `.rmdp`.
[EXTRACTION_NOTE.txt](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/RemedyCustom/Games/Alan%20Wake/Assets/Fonts/EXTRACTION_NOTE.txt)

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
