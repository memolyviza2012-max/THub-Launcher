# Kingdom Come: Deliverance — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer) · verified 2026-07-20

---

## 1. Overview

Kingdom Come: Deliverance is a Warhorse Studios game built on a modified CryEngine. The Thai package is a **File Replacement** mod: one CryEngine PAK supplies Scaleform GFx font resources, while a second PAK replaces the English XML localization tables with Thai text.

The delivered PAK files are conventional ZIP containers, not Unreal PAK archives; extraction, validation, and rebuilding must therefore preserve CryEngine paths inside a ZIP-compatible PAK.

---

## 2. Technical Stack

| Item | Detail |
|---|---|
| **Game Engine** | Modified CryEngine / Warhorse Kingdom Come engine |
| **Developer** | Warhorse Studios |
| **Mod Architecture** | File Replacement: `Data/GameData.pak` + `Localization/English_xml.pak` |
| **Archive Format** | CryEngine PAK implemented as ZIP (`PK 03 04`; end record `PK 05 06`) |
| **AES Encryption** | No AES flag or encrypted ZIP entries observed |
| **Compression** | XML entries use ZIP Deflate (method 8); GFx entries are stored (method 0) |
| **Font System** | Scaleform GFx font library / glyph resource, `CFX` header and zlib payload |
| **Thai Font Used** | Not identifiable as an installable font from supplied GFx binaries |
| **Text System** | XML `<Table><Row><Cell>…` tables in `English_xml.pak` |
| **Text Encoding** | UTF-8 without BOM, CRLF |
| **Mod Complexity** | ★★★★☆ — text is straightforward, but Thai font assets are proprietary Scaleform GFx |

---

## 3. File Architecture

```text
Kingdom Come 1/
├── mod.manifest                                  379 B
├── Data/GameData.pak                       22,224,867 B  ZIP PAK, 4 entries
│   └── Libs/UI/
│       ├── gfxfontlib.gfx                       1,755 B  CFX 08; zlib at +0x08
│       └── gfxfontlib_glyphs.gfx           22,222,514 B  CFX 0F; zlib at +0x08
└── Localization/English_xml.pak              5,007,658 B  ZIP PAK, 11 Deflate XML files
    ├── text_ui_dialog.xml                  17,217,594 B
    ├── text_ui_quest.xml                    2,415,739 B
    ├── text_ui_items.xml                    1,125,868 B
    └── other UI/HUD/menu/tutorial tables
```

`GameData.pak` begins `50 4B 03 04` and stores its GFx entries without ZIP compression. `English_xml.pak` begins the same ZIP local-file header but its first XML entry uses method 8 (Deflate); its trailing EOCD signature is `50 4B 05 06`. This proves ZIP PAK structure and no separate PAK encryption layer.

---

## 4. Font Analysis

No raw `.ttf`/`.otf` is present. `gfxfontlib.gfx` begins `43 46 58 08` (`CFX`) and `gfxfontlib_glyphs.gfx` begins `43 46 58 0F`; byte offset `0x08` begins zlib (`78 DA` and `78 9C` respectively). The second resource is the large glyph library used by Scaleform GFx.

The binaries are retained under `Assets/Fonts/`, but they are not installable fonts and must not be renamed to `.ttf`. Thai combining vowels and tone marks are prebuilt into the GFx glyph/shaping resource; replacing only XML cannot add missing glyphs. Test text with U+0E34/U+0E48 combinations and long dialogue lines after each font rebuild.

---

## 5. Text Analysis

The localization PAK expands to 22,716,591 bytes across 11 UTF-8 XML tables. It contains **81,033 `<Row>` records** and **3,314,378 Thai Unicode code points**. Each row has a stable key in the first `<Cell>`, an English source in the next, and Thai localized text in a later cell. `text_ui_dialog.xml` dominates the mod with 65,982 rows and 2,469,521 Thai code points; quests, items, menus, HUD, minigames, soul, and tutorials are separate tables.

Preserve row count, key cell, cell order, XML escaping, markup, and placeholders. Do not save to a legacy Thai code page or insert a BOM unless the game build specifically requires it.

---

## 6. Cross-Engine Comparison

KCD1 and the existing KCD2 Bible share CryEngine PAK-as-ZIP packaging, UTF-8 XML tables, and Scaleform GFx `CFX` font resources. Unlike loose-file Unity font replacement, a Thai font change here requires a valid GFx font/glyph pair and a correctly rooted PAK; merely dropping in a TTF will not be loaded.

The KCD2 package has four selectable translation/font combinations, while KCD1 uses a single font pair and a single localization PAK. The same archive-root and XML-key preservation rules apply to both.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด

### Font pipeline

1. Extract `Libs/UI/gfxfontlib.gfx` and `gfxfontlib_glyphs.gfx` from `GameData.pak`.
2. Build compatible Scaleform GFx resources from a Thai-capable source font; retain glyph coverage and metrics for Thai combining marks.
3. Put both files back under exactly `Libs/UI/` in `GameData.pak`.
4. Validate PAK with a ZIP lister and test menus, dialogue, small UI, and subtitles.

### Text pipeline

1. Read each XML as UTF-8 without BOM.
2. Change only translation cells; preserve key cells, tags, markup, format tokens, and newlines.
3. Validate XML and compare row count against the 81,033-row baseline.
4. ZIP the XML files at the PAK root — never under an added `English_xml/` directory — using Deflate-compatible entries.

---

## 8. Troubleshooting

| Symptom | Resolution |
|---|---|
| Thai glyphs are squares or absent | Deploy both GFx files together; XML has no fallback TTF loader. |
| Tone marks collide | Rebuild or adjust the GFx source font metrics/anchors; do not reorder Thai Unicode. |
| Mod is ignored | Confirm PAK internal roots are `Libs/UI/...` and raw `text_ui_*.xml`, not an extra parent folder. |
| Startup/load error | Verify ZIP central directory and compression method; restore stored GFx entries if the packer recompressed them unexpectedly. |
| Text corruption | Restore UTF-8 no-BOM and valid XML escapes (`&amp;`, `&lt;`, etc.). |

---

## 9. Required Tools

| Tool | Purpose | Source |
|---|---|---|
| 7-Zip | Inspect/list/rebuild ZIP-compatible PAK files | https://www.7-zip.org/ |
| Python `zipfile` + `xml.etree` | Automated PAK and XML validation | Python standard library |
| JPEXS FFDec / Scaleform tooling | Inspect or rebuild GFx/SWF font resources | https://github.com/jindrapetrik/jpexs-decompiler |
| Hex editor | Confirm `PK`, `CFX`, and zlib offsets | Any trusted hex editor |

---

## 10. Extracted Assets

| Asset | Destination | Status |
|---|---|---|
| `gfxfontlib.gfx` | `Assets/Fonts/gfxfontlib.gfx` | Extracted original CFX library, 1,755 B |
| `gfxfontlib_glyphs.gfx` | `Assets/Fonts/gfxfontlib_glyphs.gfx` | Extracted original CFX glyph resource, 22,222,514 B |
| `EXTRACTION_NOTE.txt` | `Assets/Fonts/EXTRACTION_NOTE.txt` | Explains why no TTF/OTF can truthfully be produced |

---

## 11. M2M Protocol

This is a bitmap/vector-runtime GFx workflow, so automation must generate a compatible glyph atlas/mapping rather than pretend a raw TTF is the game asset.

```python
# render_thai_sheet.py — render needed Thai glyphs deterministically
from PIL import Image, ImageDraw, ImageFont
font = ImageFont.truetype('ThaiSource.ttf', 48)
chars = ''.join(chr(c) for c in range(0x0E00, 0x0E7F + 1))
sheet = Image.new('L', (2048, 2048)); draw = ImageDraw.Draw(sheet)
# place every glyph, record x/y/w/h/advance in a JSON mapping for the GFx builder
```

```python
# Preserve Unicode logical order; only normalize invalid duplicate combining marks.
import re, unicodedata
def shape_source(s):
    return re.sub(r'([\u0E31\u0E34-\u0E3A\u0E47-\u0E4E])\1+', r'\1', unicodedata.normalize('NFC', s))
```

```python
# Mapping payload concept for a verified GFx builder, not a blind file overwrite.
import struct
record = struct.pack('<IHHHHh', codepoint, x, y, width, height, advance)
```

Generate the atlas and mapping, then use a GFx-aware builder to emit `gfxfontlib*.gfx`; validate `CFX` headers and test the completed PAK. The supplied files do not expose enough public structure to safely inject these records by offset alone.
