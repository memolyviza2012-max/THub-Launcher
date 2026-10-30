# Mina The Hollower — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Mina The Hollower uses a Custom Engine by YachtClub Games (`.pak.yc` archives). The mod architecture pattern is File Replacement.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Custom Engine (YachtClub Games) |
| **Developer** | Yacht Club Games |
| **Project Codename** | Unknown |
| **Archive Format** | `.pak.yc` |
| **AES Encryption** | No |
| **Compression** | Unknown |
| **Font System** | Embedded |
| **Thai Font Used** | Unknown |
| **Text System** | Embedded in PAK |
| **Text Encoding** | UTF-8 |
| **Mod Complexity** | ★★★☆☆ |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```
MinaTheHollower-ThaiMod-by-LungDear/
├── data/
│   ├── global.pak.yc (16 MB) - Contains 89602 Thai sequences
│   └── global_startup.pak.yc (45 MB) - Contains 70894 Thai sequences
├── Install.bat
├── Uninstall.bat
└── README.txt
```

---

## 4. Font Analysis
- Embedded in `.pak.yc`.

---

## 5. Text Analysis
- Texts are stored in `.pak.yc` files.
- `global.pak.yc` contains 89,602 Thai character sequences.
- `global_startup.pak.yc` contains 70,894 Thai sequences.
- Encoding: UTF-8.

---

## 6. Cross-Engine Comparison
- This is a custom engine, completely different from Unreal Engine or Unity. The `.pak.yc` has magic bytes `YCD`. Modders must write a custom script to pack/unpack these files if tools aren't publicly available.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
**Text & Font Pipeline:**
1. Determine how to unpack `.pak.yc`.
2. Edit text and font.
3. Repack and install using `Install.bat`.

---

## 8. Troubleshooting
- **Game crashes:** The repacked `.pak.yc` might have invalid offsets.

---

## 9. Required Tools
| Tool Name | Purpose |
|---|---|
| Custom YCD Unpacker | Extract/repack `.pak.yc` |

---

## 10. Extracted Assets
Extraction requires custom YCD unpacker.
[EXTRACTION_NOTE.txt](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/YachtClubEngine/Games/MinaTheHollower/Assets/Fonts/EXTRACTION_NOTE.txt)
