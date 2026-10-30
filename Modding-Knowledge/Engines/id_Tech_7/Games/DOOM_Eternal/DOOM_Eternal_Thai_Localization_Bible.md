# DOOM Eternal — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
DOOM Eternal is an id Software first-person shooter built on **id Tech 7**. The supplied Thai v1.4 mod uses an **EternalModInjector file-overlay pipeline**: the injector patches the game/manifest as required and redirects the `gameresources_patch*` mod folders into the running game.

This is not a Unicode-native localization. The source JSON stores Thai text as Private Use Area (PUA) carrier characters, which the custom distance-field font atlas renders as Thai glyphs. Text, atlas and binary mapping resources are therefore a single coupled system.

---

## 2. Technical Stack
| รายการ | รายละเอียดที่ยืนยันจากม็อด |
|---|---|
| **Game Engine** | id Tech 7 |
| **Developer** | id Software |
| **Mod Architecture** | Runtime injector + `gameresources_patch1/2` overlay |
| **Archive Format** | No archive in the supplied mod; loose game-resource override tree |
| **AES Encryption** | N/A — no UE PAK/IoStore container is supplied |
| **Compression** | None at mod level; atlas resources are proprietary streamed data |
| **Loader** | EternalModInjector dated `2026-07-26`; invokes `DEternal_loadMods.exe` with `--redirectBlangContainer "gameresources_patch3"` |
| **Font System** | id Tech 7 proprietary `DIVINITY` distance-field atlas plus binary metric/mapping files |
| **Thai Font Used** | Custom baked glyph atlas; original vector family cannot be identified from supplied resources |
| **Text System** | `EternalMod/strings/english.json`, key/value string array |
| **Text Encoding** | UTF-8 JSON without BOM; rendered text is PUA-carrier encoded, not Thai Unicode |
| **Mod Complexity** | ★★★★★ — every text glyph depends on custom atlas and map data |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```text
DOOMEternal_ModThai_v1.4/
├── EternalModInjector.bat                         65,302 B
├── EternalModManager.exe                           64,000 B
├── base/                                           injector, manifest patcher and helpers
└── Mods/
    ├── gameresources_patch1/
    │   ├── EternalMod/strings/english.json         2,782,898 B
    │   │   └── 13,443 named game-string records
    │   └── fonts/
    │       ├── eternal_bold_jp/64_df...font        2,117,560 B
    │       └── eternal_regular_jp/64_df...font     1,996,606 B
    └── gameresources_patch2/
        ├── eternal bold                             42,311 B
        ├── eternal bold jp                          42,311 B (byte-identical to `eternal bold`)
        ├── eternal regular                          42,314 B
        └── eternal regular jp                       42,314 B (byte-identical to `eternal regular`)
```

Verified magic bytes:

| Resource | First bytes | Meaning |
|---|---|---|
| `english.json` | `7B 0D 0A 20 20 22 73 74 72 69 6E 67 73 22 3A 20` | UTF-8 JSON beginning `{ "strings": [` |
| Both atlas streams | `44 49 56 49 4E 49 54 59 63 00 00 01 ...` | Proprietary `DIVINITY` resource, type byte `0x63`; not a TGA header |
| Bold metrics | `00 40 00 37 FF F7 00 03 0B CB ...` | Proprietary binary map, 42,311 B |
| Regular metrics | `00 40 00 37 FF F7 00 03 0B CB ...` | Proprietary binary map, 42,314 B |

---

## 4. Font Analysis
The `*_jp` atlas overrides are the Thai-glyph carrier resources. Their filenames contain `.tga`, but magic-byte inspection proves they are not standard TGA raster files: both start `DIVINITY`, so they cannot be opened or redistributed as an installable vector font.

The two 42-KiB binary metric pairs carry the relationship between PUA character codes and atlas UV/advance data. The bold and bold-jp files share SHA-256 `FAAA3153C41834A8A354D50BBBFFAAFBE08F4CDDD70C29F6EE8DC97A56DF69AC`; the regular pair shares `1212D94F219DF8DF4AE0A044F9D58D2261FDC8BD7AE3778C1CB664559F76AA18`.

No raw TTF/OTF can be safely extracted. Candidate `00 01 00 00` sequences in the metric resources occur at `0x78F4`, but have `numTables = 257`, which fails the SFNT validity check. `Assets/Fonts/EXTRACTION_NOTE.txt` records the evidence. Thai vowels and tone marks work only because the atlas/map pairing supplies their pre-baked glyphs; replacing only the JSON will produce wrong glyphs or missing text.

---

## 5. Text Analysis
`english.json` has SHA-256 `1E0233EC067B170C8D83C151746BD91C0E3F711E5785BFF2A0216321E322F80F` and parses to **13,443 unique `name` records**. It contains **448,400 PUA characters** and **577 unique PUA code points**, with **zero** raw Thai Unicode characters (`U+0E00`–`U+0E7F`). The v1.4 readme describes 13,526 translated lines; the parsed JSON is the authoritative count for this supplied build.

Records are `{"name": "#STR_...", "text": "..."}` objects. Preserve every string key, placeholder (`%0`, `%1`), literal newline, markup/control character and PUA code. Do not run a normal Thai spell-checker or Unicode normalization across `text`: it will treat carrier characters as unrelated symbols and corrupt the map.

Content covers UI commands, menus, lore, gameplay notifications and subtitles in one table. Online/server-provided strings may remain English because they are not present in this local table.

---

## 6. Cross-Engine Comparison
The existing **DOOM (2016)** Bible in `Engines/id_Tech_6/Games/Doom_2016` documents the same design constraint: id Tech lacks native Thai glyph handling, so localization uses carrier encoding and a distance-field atlas instead of raw Thai text. DOOM (2016) maps Thai to Latin Extended characters and replaces many `.dat`/`.bimage` resources; Eternal instead uses PUA carrier codes, two `DIVINITY` atlas streams, and patch2 binary maps.

Unlike a Ren'Py or UE LocRes mod, JSON here is only the semantic layer. Its apparent text is intentionally unreadable until rendered through the matching font atlas. The correct unit of version control is therefore **JSON + bold atlas/map + regular atlas/map**.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
### Text pipeline
1. Back up all six font resources and `english.json`; validate the original JSON with a parser.
2. Export JSON records keyed by `name`; preserve ordering, duplicate policy (none in this build) and exact placeholders.
3. Translate to normal Thai in an intermediate UTF-8 source, then apply the verified Thai→PUA mapping table.
4. Serialize compactly or pretty-print consistently as UTF-8 **without BOM**, while retaining `strings` array structure.
5. Validate PUA code coverage against the metric/atlas mapping before injection.

### Font pipeline
1. Start from a Thai TTF and render glyphs, including combining vowels/tone marks, into separate bold and regular grayscale distance-field atlases.
2. Produce the engine-compatible `DIVINITY` texture stream and matching binary UV/advance map for every PUA code emitted by the encoder.
3. Keep both direct and `_jp` metric filenames; this mod uses byte-identical copies per weight.
4. Deploy under the same `Mods/gameresources_patch1` and `gameresources_patch2` relative paths.
5. Run `EternalModInjector.bat`, then test small UI labels, long lore entries, `%0/%1` substitutions, HUD, campaign and DLC screens.

Never add a loose `.ttf` to this mod tree: the engine resources reference atlas/map files, not a desktop font loader.

---

## 8. Troubleshooting
| อาการ | สาเหตุที่เป็นไปได้ | วิธีแก้ |
|---|---|---|
| ข้อความเป็นสี่เหลี่ยมหรืออักขระแปลก | JSON PUA code ไม่มี glyph/metrics ใน atlas map | ใช้ mapping ชุดเดียวกับ atlas และตรวจ coverage ทั้ง 577 codes |
| ข้อความไทยหายแต่เกมไม่ crash | ใช้ Thai Unicode ตรง ๆ แทน PUA carrier | แปลง Thai → PUA ก่อน serialize JSON |
| สระ/วรรณยุกต์ลอยผิด | UV/advance/anchor map ไม่ตรงกับ atlas ที่แก้ | rebuild atlas และ metric binary เป็นคู่เดียวกัน; test combining marks |
| เมนูบางส่วนยังอังกฤษ | key ไม่มีใน local JSON หรือเป็น server string | ค้น `#STR_` key ใน JSON; server-sent text แก้ผ่าน mod นี้ไม่ได้ |
| Injector ปฏิเสธเกม | build checksum ใน `EternalPatcher.def` ไม่ตรงเวอร์ชันเกม | อัปเดต injector/definition ให้ตรง executable build; อย่าแก้ checksum สุ่ม |
| เกม crash หลัง inject | resource path/header ถูกเปลี่ยน | คืนชื่อ/ขนาด-structure resource เดิมและค่อยทดสอบทีละ weight |

---

## 9. Required Tools
| เครื่องมือ | วัตถุประสงค์ | แหล่งที่มา |
|---|---|---|
| EternalModInjector | inject/redirect overlay ของ DOOM Eternal | รวมอยู่ในม็อด; readme อ้าง GameBanana tool 7475 |
| Python 3 | parse JSON, validate PUA coverage, automate encoding | Python standard library |
| Pillow + fontTools | render Thai glyphs and inspect source TTF | Python packages |
| Custom id Tech 7 resource builder | encode `DIVINITY` atlas + binary metric map | ต้องใช้ pipeline ที่เข้ากันได้; ไม่มี GUI substitute ที่ปลอดภัย |
| Hex viewer / hash tool | verify magic bytes, duplicate maps and output hashes | Any verified binary tool |

---

## 10. Extracted Assets
| Asset | Stored path | Evidence / use |
|---|---|---|
| Thai carrier JSON | `Assets/Text/english.json` | 2,782,898 B; 13,443 records; PUA carrier text |
| Bold atlas | `Assets/Fonts/Atlas/eternal_bold_jp_64_df.tga.alpha.streamed` | 2,117,560 B; `DIVINITY` distance-field resource |
| Regular atlas | `Assets/Fonts/Atlas/eternal_regular_jp_64_df.tga.alpha.streamed` | 1,996,606 B; `DIVINITY` distance-field resource |
| Four metric resources | `Assets/Fonts/Metrics/` | binary UV/advance/mapping resources, original filenames retained |
| Injector entrypoint | `Assets/Raw/EternalModInjector.bat` | deployment implementation reference |
| Extraction evidence | `Assets/Fonts/EXTRACTION_NOTE.txt` | explains why no TTF/OTF is provided |

---

## 11. M2M Protocol — Bitmap/Carrier Font Automation
The following is a non-GUI automation blueprint. It intentionally separates a reversible intermediate map from the engine-specific packer; do not write an invented header over the existing 42-KiB maps.

### 11.1 Render Thai glyphs into an intermediate atlas
```python
from PIL import Image, ImageDraw, ImageFont

FONT = "ThaiSource.ttf"
PUA_START = 0xE000
chars = "กขฃคฅฆงจฉชซฌญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรฤลฦวศษสหฬอฮะัาำิีึืุูเแโใไๅ็่้๊๋์ํๆฯ๐๑๒๓๔๕๖๗๘๙"
font = ImageFont.truetype(FONT, 64)
atlas = Image.new("L", (2048, 2048), 0)
draw = ImageDraw.Draw(atlas)
metrics = []
x = y = 8; row_h = 0
for code, ch in enumerate(chars, PUA_START):
    box = draw.textbbox((0, 0), ch, font=font, stroke_width=0)
    w, h = box[2] - box[0], box[3] - box[1]
    if x + w + 8 > atlas.width: x, y, row_h = 8, y + row_h + 8, 0
    draw.text((x - box[0], y - box[1]), ch, fill=255, font=font)
    metrics.append((code, x, y, w, h, font.getlength(ch)))
    x += w + 8; row_h = max(row_h, h)
atlas.save("thai_intermediate.png")
```

### 11.2 Shape/encode text deterministically
```python
import re

THAI_TO_PUA = {"ก": "\ue000"}  # populate only from decoded metric map
MARKS = re.compile(r"([ก-ฮ])([ิีึืุูั็่้๊๋์ํ]+)")
def encode_thai(s: str) -> str:
    # Preserve placeholders and normalize mark sequence only in intermediate text.
    s = MARKS.sub(lambda m: m.group(1) + "".join(sorted(m.group(2))), s)
    return "".join(THAI_TO_PUA.get(c, c) for c in s)
```

### 11.3 Inject a decoded map through a declared struct
```python
import struct
# Layout must be derived from a known-good `eternal regular` map before use.
# Example record schema only: code, u, v, width, height, advance (little endian).
REC = struct.Struct("<IHHHHf")
def pack_records(records):
    return b"".join(REC.pack(code, u, v, w, h, advance)
                    for code, u, v, w, h, advance in records)
# A real packer must also write the original header/count/checksum fields and
# encode the PNG/SDF into the matching `DIVINITY` stream. Abort on unknown layout.
```

Automated validation gate: reject any JSON PUA code without a map record; reject any emitted record whose UV rectangle is outside the generated atlas; then hash and preserve the original binaries before injector deployment.
