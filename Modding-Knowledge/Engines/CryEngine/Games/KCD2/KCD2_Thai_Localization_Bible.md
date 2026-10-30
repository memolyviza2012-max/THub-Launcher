# Kingdom Come: Deliverance II — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer) · verified 2026-07-20

---

## 1. Overview

Kingdom Come: Deliverance II (Warhorse Studios) uses a modified CryEngine. Its Thai mod is a **CryEngine File Replacement** package with four deliberate install choices: Modern or Ancient font, each paired with Full Translation or Subtitles Only localization.

Every supplied `.pak` is a standard ZIP-compatible CryEngine PAK. Font replacement is Scaleform GFx (`.gfx`), while localization is UTF-8 XML; no Unreal/Unity container, runtime injector, or AES-encrypted archive occurs in the delivered package.

---

## 2. Technical Stack

| Item | Detail |
|---|---|
| **Game Engine** | Modified CryEngine / Warhorse Kingdom Come engine |
| **Developer** | Warhorse Studios |
| **Mod Architecture** | File Replacement: install one of four `mods/thaimod` combinations |
| **Archive Format** | CryEngine PAK = ZIP (`PK 03 04`, EOCD `PK 05 06`) |
| **AES Encryption** | No encrypted ZIP entries observed |
| **Compression** | ZIP Deflate method 8; GFx payload internally begins zlib at offset `0x08` |
| **Font System** | Scaleform GFx font-definition + glyph resources |
| **Thai Font Used** | Two prebuilt styles: Modern and Ancient; original source family is not recoverable as TTF/OTF |
| **Text System** | XML `<Table><Row><Cell>…` localization tables |
| **Text Encoding** | UTF-8 without BOM, CRLF |
| **Mod Complexity** | ★★★★☆ — text is editable, but valid GFx font asset generation/replacement is specialized |

---

## 3. File Architecture

```text
Kingdom Come Deliverance 2/
├── ฟอนต์สมัยใหม่/ (Modern)
│   ├── แปลหมด/mods/thaimod/{Data/ThaiFont.pak, Localization/English_xml.pak}
│   └── เฉพาะซับไตเติล/mods/thaimod/{Data/ThaiFont.pak, Localization/English_xml.pak}
├── ฟอนต์แนวโบราณ/ (Ancient)
│   ├── แปลหมด/mods/thaimod/{Data/ThaiFont.pak, Localization/English_xml.pak}
│   └── เฉพาะซับไตเติล/mods/thaimod/{Data/ThaiFont.pak, Localization/English_xml.pak}
├── ตัวอย่างฟอนต์สมัยใหม่.png                 2,466,623 B
├── ตัวอย่างฟอนต์แนวโบราณ.png                2,467,503 B
└── วิธีลง.txt                                      397 B
```

Each `ThaiFont.pak` has two Deflate entries: `Libs/UI/gfxfontlib.gfx` (67,261 B uncompressed) and `Libs/UI/gfxfontlib_glyphs.gfx`. The English localization PAK always has 11 XML files. Full Translation expands to 48,961,320 B; Subtitles Only expands to 46,664,052 B.

---

## 4. Font Analysis

The common definition file is byte-identical across both styles: `gfxfontlib.gfx`, SHA-256 `46C0FA461ACAB3C7CE4F300E6701E3EA726A267084B917FACB8055274B602C61`. It begins `43 46 58 08` (`CFX`), and its compressed payload begins at `0x08` with `78 DA`.

| Style | Resource | Size | SHA-256 |
|---|---|---:|---|
| Modern | `gfxfontlib_glyphs.gfx` | 3,194,100 B | `6BD9BCD141E4B7F6D4D5C1210DABA3FA3188107147977C33B9F2B50732E7FD81` |
| Ancient | `gfxfontlib_glyphs.gfx` | 5,409,415 B | `1AFB81B72FB6C3F0831DA6507FE7F444F8D116468C562FD4D20C90114057BC2D` |

Both glyph resources begin `43 46 58 0F`; their payload at `0x08` begins `78 9C`. They are GFx runtime resources, not raw TTF/OTF, so no truthful installable-font extraction is possible. Retain the matching definition and glyph file together. Test Thai base characters with U+0E34, U+0E48, and long wrapped subtitles: combining-mark positioning belongs to the prebuilt GFx data, not the XML.

---

## 5. Text Analysis

All localization entries are UTF-8 XML with no BOM. The two scopes keep the same **203,777 `<Row>` records** across 11 tables, but differ in which third-cell strings are Thai:

| Scope | Expanded XML size | Thai code points | Meaning |
|---|---:|---:|---|
| Subtitles Only | 46,664,052 B | 4,020,237 | dialogue table translated; non-dialogue tables remain English |
| Full Translation | 48,961,320 B | 5,170,838 | dialogue plus menus, items, quests, tutorials, rich presence, etc. |

`text_ui_dialog.xml` has 177,679 rows and 4,020,237 Thai code points in either translation scope. In Full Translation, examples of additional translated tables are items (5,243 rows), menus (6,364), quests (8,890), soul (3,468), and tutorials (244). Preserve keys, cell ordering, markup, tokens, XML entities, and CRLF/UTF-8 serialization.

---

## 6. Cross-Engine Comparison

KCD2 uses the same CryEngine ZIP-PAK + XML + GFx pattern as the Kingdom Come: Deliverance Bible in this knowledge base. KCD1 has one font/localization pair and 81,033 rows; KCD2 adds selectable Modern/Ancient glyph payloads and Full/Subtitles localization scopes.

Unlike raw-TTF Unity mods, neither game will load a TTF placed beside the archive. The loader requires exact internal PAK paths and the Scaleform GFx pair.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด

### Font pipeline

1. Choose one style only: Modern or Ancient; do not mix the GFx definition with an unrelated glyph resource.
2. Build or obtain a compatible GFx font/glyph pair from a Thai-capable source font.
3. Pack it under `Libs/UI/gfxfontlib.gfx` and `Libs/UI/gfxfontlib_glyphs.gfx` in `Data/ThaiFont.pak`.
4. Validate `CFX` at offset 0 and zlib at `0x08`, then test every UI scale and Thai combining mark.

### Text pipeline

1. Pick Full Translation or Subtitles Only as the baseline; retain all 11 XML filenames and 203,777 rows.
2. Parse/write UTF-8 XML without BOM; edit only translation cell content.
3. Validate XML and count rows before repacking.
4. ZIP files at the PAK root (e.g., `text_ui_dialog.xml`, not `Localization/text_ui_dialog.xml`) with Deflate and deploy under `mods/thaimod/Localization/`.

---

## 8. Troubleshooting

| Symptom | Resolution |
|---|---|
| Thai glyphs missing | Deploy `gfxfontlib.gfx` and the matching Modern/Ancient glyph file as a pair. |
| Marks overlap | Correct the GFx source/metrics and rebuild; XML Unicode order must stay logical. |
| Mod ignored | Verify `mods/thaimod/Data/ThaiFont.pak` and `mods/thaimod/Localization/English_xml.pak` paths, plus PAK internal roots. |
| Load failure | Ensure a valid ZIP central directory; do not add an outer directory during repacking. |
| Mojibake or broken markup | Restore UTF-8 without BOM, CRLF, and valid XML entities/tokens. |
| Wrong text scope | Use the right baseline: Subtitles Only intentionally leaves many UI tables English. |

---

## 9. Required Tools

| Tool | Purpose | Source |
|---|---|---|
| Python `zipfile`, `xml.etree`, `hashlib` | Validate PAK layout, XML, and reproducible hashes | Python standard library |
| 7-Zip | Inspect ZIP-compatible PAKs | https://www.7-zip.org/ |
| JPEXS FFDec / GFx-compatible tooling | Inspect/rebuild Scaleform/SWF-family resources | https://github.com/jindrapetrik/jpexs-decompiler |
| Hex editor | Confirm `PK`, `CFX`, and zlib magic/offsets | Any trusted hex editor |

---

## 10. Extracted Assets

| Asset | Destination | Verification |
|---|---|---|
| Shared GFx definition | `Assets/Fonts/gfxfontlib.gfx` | 67,261 B; SHA-256 listed in section 4 |
| Modern glyph resource | `Assets/Fonts/Modern/gfxfontlib_glyphs.gfx` | 3,194,100 B; SHA-256 listed in section 4 |
| Ancient glyph resource | `Assets/Fonts/Ancient/gfxfontlib_glyphs.gfx` | 5,409,415 B; SHA-256 listed in section 4 |
| Font screenshots | `Assets/screenshot_modern.png`, `Assets/screenshot_ancient.png` | Source copies retained |
| Extraction explanation | `Assets/Fonts/EXTRACTION_NOTE.txt` | Documents why no TTF/OTF was fabricated |

---

## 11. M2M Protocol

GFx needs a GFx-aware build stage; these scripts automate preparation/validation, not a dangerous blind byte overwrite.

```python
# render_thai_sheet.py
from PIL import Image, ImageDraw, ImageFont
font = ImageFont.truetype('ThaiSource.ttf', 48)
chars = ''.join(chr(c) for c in range(0x0E00, 0x0E80))
sheet = Image.new('L', (2048, 2048)); draw = ImageDraw.Draw(sheet)
# render chars deterministically and emit x/y/w/h/advance for a GFx-aware builder
```

```python
import re, unicodedata
def normalize_thai(text):
    text = unicodedata.normalize('NFC', text)
    return re.sub(r'([\u0E31\u0E34-\u0E3A\u0E47-\u0E4E])\1+', r'\1', text)
```

```python
import struct
# Intermediate glyph-map record; feed to a verified GFx builder, not directly to CFX bytes.
record = struct.pack('<IHHHHh', codepoint, x, y, width, height, advance)
```

After building, assert `data[:4] == b'CFX\x0f'` for glyph resources, inspect PAK paths, and run a game UI/subtitle smoke test. The supplied GFx files do not reveal enough public tag layout for safe generic byte-level injection.
