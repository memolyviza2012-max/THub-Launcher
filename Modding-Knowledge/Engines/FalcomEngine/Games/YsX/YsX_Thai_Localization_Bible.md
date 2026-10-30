# Ys X: Nordics — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Ys X: Nordics uses the Falcom Engine proprietary archive format (`.p3a`). The mod architecture pattern is File Replacement, as the original `.p3a` files are directly replaced with the modded ones.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Falcom Engine (.p3a) |
| **Developer** | Nihon Falcom |
| **Project Codename** | Unknown |
| **Archive Format** | `.p3a` |
| **AES Encryption** | No |
| **Compression** | Unknown/Proprietary (Magic: PH3ARCV) |
| **Font System** | Embedded within asset archives |
| **Thai Font Used** | Unknown |
| **Text System** | Binary (.p3a) |
| **Text Encoding** | UTF-8 |
| **Mod Complexity** | ★★★☆☆ (Requires proprietary tools for packing/unpacking Falcom `.p3a` archives) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```
Ys X Proud Nordics/
├── asset_image.p3a  (4.15 GB)
├── misc.p3a         (19.29 MB)
└── script.p3a       (132.80 MB) - Contains 8332 Thai character sequences
```

---

## 4. Font Analysis
- Font is likely stored in `asset_image.p3a` or `misc.p3a`.
- Extraction failed because the `.p3a` unpacker is required to extract the inner files.
- Thai rendering considerations: Custom engines often require testing for floating vowels (สระลอย) and tone marks (วรรณยุกต์).

---

## 5. Text Analysis
- Texts are stored in `script.p3a` which contains 8332 Thai UTF-8 sequences.
- Encoding: UTF-8.
- Format is proprietary Falcom binary.

---

## 6. Cross-Engine Comparison
- Unlike Unreal Engine 4/5 which uses standard `.pak` and `.locres`, Falcom Engine uses a proprietary `.p3a` format. Modders moving from UE to Falcom Engine will need specialized unpackers rather than standard tools like FModel.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
**Text Pipeline:**
1. Unpack `script.p3a` using a Falcom archive tool.
2. Edit extracted text files.
3. Repack back into `.p3a`.

**Font Pipeline:**
1. Locate font files within `asset_image.p3a` or `misc.p3a`.
2. Replace with a Thai TTF/OTF font or a generated Bitmap/SDF if required by the engine.

---

## 8. Troubleshooting
- **Game crashes on launch:** Check if the repacked `.p3a` is correctly formatted.
- **Thai text rendering as squares:** The font file inside the archive was not successfully replaced or mapped.

---

## 9. Required Tools
| Tool Name | Purpose |
|---|---|
| Falcom .p3a Unpacker | Extracting and repacking `.p3a` archives |
| Hex Editor | Analyzing binary offsets |

---

## 10. Extracted Assets
Extraction of fonts failed as the `.p3a` archive is in a proprietary format and cannot be trivially parsed without an unpacker.
[EXTRACTION_NOTE.txt](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/FalcomEngine/Games/YsX/Assets/Fonts/EXTRACTION_NOTE.txt)
