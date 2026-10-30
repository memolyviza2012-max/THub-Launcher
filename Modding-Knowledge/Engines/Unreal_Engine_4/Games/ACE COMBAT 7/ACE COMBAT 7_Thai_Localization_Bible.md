# ACE COMBAT 7 — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
ACE COMBAT 7 uses Unreal Engine 4 and features a file replacement mod architecture pattern. The mod replaces standard UE4 engine fonts and custom `.dat` localization files to implement Thai text in the game.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Unreal Engine 4 |
| **Developer** | Bandai Namco Studios |
| **Project Codename** | Nimbus |
| **Archive Format** | .pak (Standard UE4) |
| **AES Encryption** | No |
| **Compression** | Zlib / None |
| **Font System** | Font Swap (.ttf direct replacement) |
| **Thai Font Used** | TH Niramit AS Bold |
| **Text System** | Custom Binary (.dat) |
| **Text Encoding** | UTF-8 |
| **Mod Complexity** | ★★☆☆☆ (Simple file replacement, no encryption, standard TTF injection) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```text
Game\Content\Paks\~mods\pakchunk0-WindowsNoEditor_0_P_P.pak (756 KB)
├── Engine/Content/Slate/Fonts/
│   ├── DroidSans.tps (272 B)
│   ├── DroidSansFallback.ttf (95 KB)
│   ├── DroidSansMono.ttf (95 KB)
│   ├── Roboto-Bold.ttf (95 KB)
│   ├── Roboto-Light.ttf (95 KB)
│   ├── Roboto-Regular.ttf (95 KB) - Replaced with TH Niramit AS Bold
│   └── Roboto.tps (691 B)
└── Nimbus/Content/Localization/Game/
    └── A.dat (524 KB) - Contains Thai UTF-8 text
```

---

## 4. Font Analysis
- **Font Identification**: The mod uses `TH Niramit AS Bold` disguised as `Roboto-Regular.ttf` and other standard Android/Roboto fonts.
- **How fonts are stored**: The TTF fonts are stored in raw format (magic bytes: `00 01 00 00`) inside the PAK file, rather than being wrapped in `.ufont` assets.
- **Font swap mapping**: The game's UI relies on standard engine fonts (`Roboto-*.ttf`, `DroidSans*.ttf`). The mod replaces all of these with copies of `TH Niramit AS Bold` to ensure Thai characters render everywhere.
- **Thai rendering considerations**: As raw TTF fonts are used without complex reshaping logic in standard UE4 Slate, specific Thai shaping (สระลอย, วรรณยุกต์) may require pre-shaping in the text files or rely on the OS/Engine text renderer if supported.

---

## 5. Text Analysis
- **File format and encoding**: The game uses a custom binary format `.dat` (magic: `A6 C9 4E AA 15 83 D6 DB`) located in `Nimbus/Content/Localization/Game/`.
- **Text Structure**: Text is stored in UTF-8 format within the `.dat` file.
- **String Count**: The `.dat` file is large (~524 KB) and contains game dialogue and UI text.
- **Quest/dialogue organization**: Embedded directly in the `.dat` file.

---

## 6. Cross-Engine Comparison
Unlike newer Unreal Engine 5 games like *Hogwarts Legacy* which use IoStore `.ucas`/`.utoc` and Oodle compression, *ACE COMBAT 7* uses the older standard `.pak` format without AES encryption. Also, rather than using cooked `.ufont` assets typical in most UE4 games, it replaces raw `.ttf` files directly in the `Engine/Content/Slate/Fonts` directory. This is similar to *Bloodstained: Ritual of the Night* which also relies heavily on standard UE4 pak chunk modding.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
**Font Pipeline:**
1. Obtain the desired Thai TTF font (e.g., TH Niramit AS).
2. Rename the font to `Roboto-Regular.ttf`, `Roboto-Bold.ttf`, `Roboto-Light.ttf`, `DroidSansFallback.ttf`, and `DroidSansMono.ttf`.
3. Recreate the directory structure `Engine/Content/Slate/Fonts/`.

**Text Pipeline:**
1. Extract `A.dat` using repak.
2. Edit the UTF-8 text within `A.dat` using a hex editor or custom script capable of parsing the format.
3. Repack the modified `A.dat` into `Nimbus/Content/Localization/Game/`.
4. Use `repak` to pack the folders into `pakchunk0-WindowsNoEditor_0_P_P.pak` and place it in the `~mods` folder.

---

## 8. Troubleshooting
- **Font not displaying**: Ensure the font files are named exactly as the original engine fonts.
- **Game crash after mod installation**: The `.dat` file structure might have been broken during text editing. Ensure text offsets/lengths (if any) are updated when changing string lengths.
- **Thai vowels/tone marks misaligned**: Text may need to be pre-shaped before inserting into `A.dat`, replacing problematic characters with correct display glyphs.

---

## 9. Required Tools
| Tool | Purpose | Download Source |
|---|---|---|
| **repak_cli** | Unpack and repack UE4 .pak files | [GitHub - repak](https://github.com/trumank/repak) |
| **Hex Editor** | Edit `A.dat` safely | HxD / VSCode Hex Editor |

---

## 10. Extracted Assets
- [THNiramitAS-Bold.ttf](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/UnrealEngine4/Games/ACE%20COMBAT%207/Assets/Fonts/THNiramitAS-Bold.ttf)

---

## 11. M2M Protocol
**Automated Font Rendering Script (Python):**
```python
# ACE COMBAT 7 does not require Bitmap Font injection. It supports raw TTF natively.
# This section is generally for Bitmap Font engines, but provided as a stub.
pass
```
**Automated Text Shaping Script (Regex):**
```python
import re
def shape_thai(text):
    # Example: replace ป + ี + ่ with specially mapped characters if required.
    return re.sub(r'ปี(่)', r'ป\1', text)
```
**Automated FNT/Mapping Injector (Struct):**
```python
# N/A for ACE COMBAT 7 as it uses raw TTF.
pass
```
