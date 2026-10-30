# Resident Evil 2 — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Resident Evil 2 is a survival horror game developed by Capcom using the RE Engine. The Thai localization mod uses a File Replacement architecture, where the modified files are placed directly in the `natives` folder to override the base game files.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | RE Engine |
| **Developer** | Capcom |
| **Project Codename** | N/A |
| **Archive Format** | `.pak` (Mod uses loose files in `natives\x64`) |
| **AES Encryption** | No |
| **Compression** | None (Loose files) |
| **Font System** | Font Swap (`.oft.1.x64` containing raw OTF) |
| **Thai Font Used** | CSPraKasFD (OTF) |
| **Text System** | `.msg` / `.msg.14` (RE Engine Message File) |
| **Text Encoding** | UTF-16 LE |
| **Mod Complexity** | ★★☆☆☆ (File Replacement with raw OTF and standard MSG files) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```text
Resident_Evil_2\RE2_CompleteThaiEdition\
└── natives\
    └── x64\
        ├── objectroot\
        │   └── setmodel\textures\
        │       └── (Various environmental textures e.g. .tex.10)
        ├── sectionroot\
        │   ├── message\
        │   │   └── mes_main.msg.14 (Binary text file containing dialogue/UI text)
        │   └── ui\
        │       ├── ui0000\font\
        │       │   ├── fot-tsukugopro-d.oft.1.x64 (Replaced with CSPraKasFD)
        │       │   ├── helveticaneueltw1g-cn.oft.1.x64
        │       │   └── ...
        │       └── (Various UI textures)
        └── streaming\
            └── (More textures and sound .pck files)
```

---

## 4. Font Analysis
- **Identification:** The mod replaces original font files (e.g., `helveticaneueltw1g-cn.oft.1.x64`) with an OTF font named **CSPraKasFD**.
- **Storage:** The font is stored as raw OTF data simply renamed with the RE Engine font extension `.oft.1.x64`. Magic bytes reveal the `OTTO` header starting exactly at offset 0.
- **Font Swap Mapping:** Original fonts like Helvetica Neue and FOT-TsukuGoPro are mapped to the Thai CSPraKasFD font to ensure Thai glyphs are rendered properly across the UI.
- **Thai Rendering Considerations:** Since it's a raw OTF font, shaping logic (สระลอย, วรรณยุกต์) might rely on the game's internal text renderer (such as FreeType) or pre-shaping in the text files.

---

## 5. Text Analysis
- **File Format and Encoding:** Text files use the RE Engine `.msg.14` binary format.
- **Encoding:** The text is encoded in UTF-16 LE, standard for RE Engine. A deep scan revealed 12,874 Thai UTF-16 LE sequences across the message files.
- **Structure:** MSG files in RE Engine start with a header (magic bytes `0E 00 00 00 47 4D 53 47` -> Version 14, "GMSG") followed by an array of string entries.
- **Organization:** Strings are grouped by UI contexts, dialogues, and items, typically matching specific hashes or sequential IDs.

---

## 6. Cross-Engine Comparison
Unlike Unreal Engine 4/5 which uses `.locres` and `.ufont`, RE Engine uses `.msg` (Version 14/17/22 depending on game) and `.oft` (often just renamed OTF/TTF). The loose file override (`natives` folder) behaves similarly to UE's `~mods` folder, but does not require packing into a `.pak` archive to be loaded, making testing significantly easier.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
**Font Pipeline:**
1. Obtain an OTF/TTF font that supports Thai characters.
2. Rename the font file to match the game's target font (e.g., `helveticaneueltw1g-cn.oft.1.x64`).
3. Place it in `natives\x64\sectionroot\ui\ui0000\font\`.

**Text Pipeline:**
1. Extract `.msg` files using RE Engine tools (e.g., MSG Tool or RETool).
2. Export to JSON or TXT.
3. Translate the English text to Thai, ensuring UTF-16 LE encoding compatibility.
4. Repack the translated text back into `.msg.14` format.
5. Place the modified `.msg` file in `natives\x64\sectionroot\message\`.

---

## 8. Troubleshooting
- **Font not displaying / Squares:** Ensure the renamed font file actually contains valid OTF/TTF magic bytes (`OTTO` or `00 01 00 00`) at offset 0.
- **Thai vowels/tone marks misaligned (สระลอย):** If the RE Engine version used by RE2 doesn't support complex text shaping for Thai, you may need to use a pre-shaped font or manually replace floating vowels with non-floating unicode counterparts in the text files.
- **Game crash on text load:** Usually caused by a malformed `.msg` file or incorrect file size/offset in the MSG header. Re-verify the repack tool output.

---

## 9. Required Tools
| Tool Name | Purpose | Source |
|---|---|---|
| REtool / FluffyQuack's Tools | Extracting and repacking RE Engine `.msg` and `.tex` files | [Fluffy Manager / RE Modding Wiki] |
| Hex Editor (HxD) | Verifying magic bytes of fonts and MSG files | [HxD] |

---

## 10. Extracted Assets
- [CSPraKasFD.otf](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/RE%20Engine/Games/Resident%20Evil%202/Assets/Fonts/CSPraKasFD.otf) (Successfully extracted and verified)

---

## 11. M2M Protocol
*(Optional section for Bitmap font workflows - since this game supports raw OTF, this section is included for completeness but is not strictly necessary for RE2).*
```python
# M2M Automated Script Template (Reference)
# In case a specific UI element requires a baked texture (.tex) instead of OTF
import struct

# Example of text shaping logic for floating vowels
def shape_thai_text(text):
    # Mapping table for floating vowels to PUA (Private Use Area)
    # This is highly dependent on the specific font used.
    pass
```
