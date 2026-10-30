# Prey (2017) — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

> วิเคราะห์ซ้ำจาก workspace จริงเมื่อ 2026-09-13 เอกสารฉบับนี้แก้ข้อสรุปเดิมที่ระบุว่ามี Noto Sans Thai UI แบบ TTF: payload จริงไม่มี `.ttf`/`.otf` และใช้ Scaleform `DefineFont3` ฝัง vector outlines

---

## 1. Overview

Prey (2017) พัฒนาโดย Arkane Studios Austin บน CryEngine ที่ปรับแต่งสำหรับเกม โครงสร้างม็อดเป็น **File Replacement / ZIP-PAK Overlay** จำนวน 3 ไฟล์: font patch สำหรับ UI, localization patch ของเกมหลัก และ localization patch ของ Mooncrash (`Whiplash`). ไฟล์ `.pak` ทั้งหมดเป็น ZIP มาตรฐาน ไม่มีการเข้ารหัส และโหลดเนื้อหาภาษาไทยผ่านชุดภาษา English.

คำว่า Void Engine ใน Bible เดิมถูกถอดออก: Void เป็นสายเอนจินของเกม Arkane อื่น แต่หลักฐาน workspace ของ Prey ชุดนี้คือรูปแบบ CryEngine PAK, SpreadsheetML localization และ Scaleform GFx.

---

## 2. Technical Stack

| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | CryEngine (Arkane-modified) |
| **Developer** | Arkane Studios Austin |
| **Project Codename** | Danielle (ชื่อที่รู้จักในสายพัฒนา; ไม่ได้ดึงจากสาม PAK นี้) |
| **Mod Architecture** | File Replacement / Overlay ผ่าน PAK ชื่อ `patch` |
| **Archive Format** | Standard ZIP, magic `50 4B 03 04` (`PK\x03\x04`) ที่ offset `0x0`; EOCD `50 4B 05 06` ท้ายไฟล์ |
| **AES Encryption** | No — ZIP entry ทุกตัวมี general-purpose flag bit 0 = 0 |
| **Compression** | ZIP Store (method 0) + Deflate (method 8); CFX/CWS ภายในใช้ zlib |
| **Font System** | Scaleform GFx/SWF vector outlines, SWF tag `DefineFont3` (tag 75) |
| **Thai Font Used** | Runtime slots: Harmonia Sans W1G, Pontiac, Design System C 700R, Agency FB; แหล่ง typeface ของ glyph ไทยระบุไม่ได้จาก binary |
| **Text System** | SpreadsheetML 2003 XML (`Workbook` / `Worksheet` / `Table` / `Row` / `Cell` / `Data`) |
| **Text Encoding** | UTF-8 แบบผสม: 163 ไฟล์มี BOM, 15 ไฟล์ไม่มี BOM |
| **Mod Complexity** | ★★★☆☆ — XML แก้ง่าย แต่การสร้าง GFx font ใหม่ต้องรักษา SWF font layout/code table |

SHA-256 ของ source PAK:

| Source | Bytes | SHA-256 |
|---|---:|---|
| `GameSDK/Precache/patch_thai_fonts.pak` | 438,527 | `1F4F524A5EED8519258F59B441D3892A36E70A039FB96ECD4F78E40CD874567D` |
| `Localization/English_xml_patch.pak` | 1,538,817 | `ACA6C20C99465BB859EA3D259810D894CFC0E033E00F7C4DB76FB476D7BF8790` |
| `Whiplash/Localization/English_xml_patch.pak` | 100,850 | `8C2AEE8C30B6EC6CC1CDFB7DF643E7BF7CC79861B62F8B656F15EF7961CE8A73` |

---

## 3. โครงสร้างไฟล์ (File Architecture)

```text
D:\Mods games\Thai Mods\0_Rivet Engineer\02_Workspace\Prey\
├── GameSDK\Precache\patch_thai_fonts.pak               438,527 B
│   └── libs\ui\_fonts\
│       ├── fontconfig.xml                                1,189 B
│       ├── fonts_EN.gfx                                337,744 B  [GFX v8, uncompressed]
│       └── fonts_EN.swf                                220,035 B  [CWS v8, zlib]
├── Localization\English_xml_patch.pak                1,538,817 B
│   ├── 171 SpreadsheetML XML files
│   ├── gfxfontlib.gfx                                  209,736 B  [CFX v8]
│   ├── HUD_Font_LocFont.gfx                            209,736 B  [identical to gfxfontlib]
│   └── HUD_Font_LocFont_glyphs.gfx                      47,931 B  [CFX v8]
└── Whiplash\Localization\English_xml_patch.pak         100,850 B
    └── 7 SpreadsheetML XML files (Mooncrash)
```

PAK ทั้งสามเริ่ม `PK\x03\x04`; Python `zipfile` และ 7-Zip เปิดได้ตรง ๆ. `fonts_EN.gfx` เริ่ม `47 46 58 08`, ส่วน `fonts_EN.swf` เริ่ม `43 57 53 08` (`CWS`) และ zlib stream เริ่ม offset `0x8`. GFx ใน localization เริ่ม `43 46 58 08` (`CFX`): library inflate จาก 209,736 เป็น declared 354,397 bytes และ glyph file จาก 47,931 เป็น 76,174 bytes.

---

## 4. Font Analysis

### 4.1 เส้นทางโหลด

`fontconfig.xml` กำหนด `fontlib="fonts_EN.gfx"` และ map `Normal`, `NormalLight`, `NormalBold`, `NormalItalic` ไปยัง Harmonia Sans W1G ทั้งสี่ style. นี่คือการแทน library ของ locale English ไม่ใช่การวาง TTF ให้ CryEngine โหลดตรง ๆ.

### 4.2 หลักฐาน DefineFont3

parser อ่าน SWF tag stream หลัง header/การ inflate พบ tag 75 (`DefineFont3`) flags `0x8C` = HasLayout + WideOffsets + WideCodes.

| Container | Runtime name | Glyphs/style | Thai codepoints | DefineFont3 body offset |
|---|---|---:|---:|---:|
| `fonts_EN.gfx` / `fonts_EN.swf` | Harmonia Sans W1G Italic | 801 | 87 | `0x53E` / `0x528` |
| same | Harmonia Sans W1G Light | 801 | 87 | `0x15620` / `0x15665` |
| same | Harmonia Sans W1G Bold | 801 | 87 | `0x29BF7` / `0x29C96` |
| same | Harmonia Sans W1G | 801 | 87 | `0x3E025` / `0x3E11D` |
| `gfxfontlib.gfx` และ HUD copy | Pontiac 4 styles + Design System C 700R | 694 each | 87 each | `0x540`, `0x11829`, `0x22B05`, `0x33DE0`, `0x450BA` |
| `HUD_Font_LocFont_glyphs.gfx` | Agency FB | 760 | 87 | `0x66` |

Thai code table ครอบคลุม `U+0E01–U+0E3A` และ `U+0E3F–U+0E5B` รวม 87 codepoints. `fonts_EN.swf` มี `DefineFontName` ระบุ copyright Harmonia ของ Monotype Imaging (2010). ชื่อ runtime ไม่พิสูจน์ว่า glyph ไทยมาจาก typeface ใด จึงถอดคำอ้าง Noto Sans Thai UI ออก.

### 4.3 Extraction status

ตรวจทั้งไฟล์และ body หลัง zlib inflate ไม่พบ SFNT/TTC ที่ valid (`00 01 00 00`, `OTTO`, `ttcf`: 0 candidate). Scaleform เก็บ code table, metrics และ vector shapes โดยไม่มี OpenType tables ครบชุด จึงย้อนเป็น TTF/OTF ต้นฉบับไม่ได้; ดู `Assets/Fonts/EXTRACTION_NOTE.txt`.

---

## 5. Text Analysis

XML ทั้ง 178 ไฟล์ decode แบบ strict UTF-8 และ parse ผ่านทั้งหมด เป็น SpreadsheetML namespace `urn:schemas-microsoft-com:office:spreadsheet`.

| ชุด | XML | Rows | Rows มีไทย | Data nodes | Thai chars | BOM |
|---|---:|---:|---:|---:|---:|---|
| เกมหลัก | 171 | 17,178 | 12,061 | 49,282 | 556,217 | 156 BOM, 15 no-BOM |
| Mooncrash | 7 | 1,835 | 1,716 | 7,732 | 55,473 | 7 BOM |
| **รวม** | **178** | **19,013** | **13,777** | **57,014** | **611,690** | **163 BOM, 15 no-BOM** |

ตัวอย่าง row จริง:

```text
[FG_LOC_CB_Reinitializing] [Reinitializing] [กำลังเริ่มระบบใหม่] [LOCKED]
[loc_844024417334828333] [A Little Bird Told Me] [นกตัวน้อยบอกฉัน] [LOCKED] []
```

จำนวนคอลัมน์ไม่คงที่: 0–6 `Data` nodes ต่อ Row ในเกมหลัก และ 0–5 ใน Mooncrash. ต้องรักษา sparse `ss:Index`, namespace, escaped markup, token และ `LOCKED`; ห้ามสมมติว่าทุกแถวมี 3 ช่อง. โครงสร้างแยกเป็น objectives, Levels, email/book/lore/note libraries, voices, `text_ui_*` และ Whiplash.

---

## 6. Cross-Engine Comparison

| เกมในฐานข้อมูล | จุดร่วม | จุดต่าง |
|---|---|---|
| [Kingdom Come: Deliverance](../KCD1/KCD1_Thai_Localization_Bible.md) | CryEngine ZIP-PAK + SpreadsheetML + Scaleform GFx | KCD1 มี mod manifest และ glyph GFx ใหญ่; Prey แยก font/base/Whiplash |
| [Ryse: Son of Rome](../Ryse_Son_of_Rome/Ryse_Son_of_Rome_Thai_Localization_Bible.md) | ZIP-PAK + Scaleform CFX | Ryse ใช้ CryXmlB; Prey ใช้ SpreadsheetML plain UTF-8 |

นำวิธีตรวจ `PK`, CFX/CWS zlib และ DefineFont tags ข้ามเกมได้ แต่ชื่อไฟล์, font slots, XML columns และ load priority ต้องยืนยันใหม่ ห้ามยก binary offset จาก KCD/Ryse มาใช้กับ Prey.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด

### Text Pipeline

1. สำรอง PAK และบันทึก SHA-256.
2. แตกด้วย 7-Zip/`zipfile`; รักษา internal path และตัวพิมพ์.
3. Parse XML แบบ namespace-aware ที่ `Row/Cell/Data`; ห้าม replace ทั้งไฟล์แบบไม่เข้าใจโครงสร้าง.
4. รักษา cell position, `ss:Index`, `ss:Type`, `LOCKED`, placeholder, HTML entity และ line-break markup.
5. เขียน UTF-8 โดยรักษา BOM รายไฟล์ ไม่บังคับ policy เดียวทั้ง archive.
6. Validate XML ทุกไฟล์ แล้ว ZIP ด้วย method 0/8 และใช้ชื่อ/ตำแหน่ง `.pak` เดิม.
7. ทดสอบเกมหลักและ `Whiplash` แยกกันในภาษา English.

### Font Pipeline

1. ใช้ source GFx/SWF ที่ตรง build; ห้าม rename TTF เป็น `.gfx`.
2. นำเข้า outline ไทยใน Scaleform font library สำหรับทุก runtime slot ที่เกมเรียก.
3. รักษา DefineFont3 flags, wide code table, layout metrics, exports และ `fontconfig.xml` mapping.
4. ตรวจ 87 Thai codepoints และ metrics ของสระ/วรรณยุกต์; ถ้าเพิ่ม glyph ต้อง rebuild count, offsets และ layout arrays ทั้งชุด.
5. สร้าง GFx/SWF ใหม่ด้วย pipeline ที่เข้าใจ Scaleform แล้ว pack เข้า `GameSDK/Precache/patch_thai_fonts.pak`.
6. ทดสอบ Normal/Light/Bold/Italic, HUD, title, objective, email และ subtitle.

---

## 8. Troubleshooting

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| ตัวไทยเป็นกล่อง | font patch ไม่โหลดหรือ slot ไม่ตรง | ตรวจ `GameSDK/Precache`, `fontconfig.xml`, export name และ U+0E01–U+0E5B |
| UI ไทยแต่ HUD ไม่ได้ | `fonts_EN` กับ `HUD_Font_*` เป็นคนละ library | rebuild ทั้ง Harmonia/Pontiac/Agency paths |
| สระ/วรรณยุกต์ลอย | layout metrics/advance/bearing ไม่พอดีหรือไม่มี shaping | ปรับ source outline/metrics และทดสอบ cluster หลายแบบ |
| เกมค้างตอนโหลด | XML malformed, namespace/column structure เสีย หรือ ZIP path ผิด | parse XML ทั้ง archive, เทียบ path และ restore PAK จาก hash |
| ตัวอักษรเพี้ยน | encoding/BOM ผิด | ใช้ UTF-8 และรักษา BOM รายไฟล์: 163 มี, 15 ไม่มี |
| Mooncrash ยังอังกฤษ | แก้เฉพาะ base PAK | แก้ `Whiplash/Localization/English_xml_patch.pak` แยกด้วย |

---

## 9. Required Tools

| Tool | หน้าที่ | Source |
|---|---|---|
| 7-Zip | แตก/สร้าง standard ZIP-PAK | https://www.7-zip.org/ |
| Python `zipfile` + XML parser | ตรวจ ZIP flags, parse/validate SpreadsheetML | https://www.python.org/ |
| JPEXS Free Flash Decompiler | ตรวจ SWF/GFX tags และ vector shapes | https://github.com/jindrapetrik/jpexs-decompiler |
| Scaleform GFx authoring pipeline/SDK | สร้าง font library ที่เกมโหลดได้ | middleware tooling ที่มีสิทธิ์ใช้งาน |
| FontTools | validate SFNT/TTF/OTF candidates | https://github.com/fonttools/fonttools |
| `Get-FileHash` | provenance ก่อน/หลัง pack | Windows PowerShell |

---

## 10. Extracted Assets

- [`Assets/Packages/`](Assets/Packages/) — PAK ทั้งสามพร้อมชื่อแยก BaseGame/Mooncrash
- [`Assets/Extracted/FontPatch/`](Assets/Extracted/FontPatch/) — `fontconfig.xml`, `fonts_EN.gfx`, `fonts_EN.swf`
- [`Assets/Extracted/BaseGame/`](Assets/Extracted/BaseGame/) — XML เกมหลัก 171 ไฟล์และ HUD GFx
- [`Assets/Extracted/Mooncrash/`](Assets/Extracted/Mooncrash/) — XML Mooncrash 7 ไฟล์
- [`Assets/Fonts/`](Assets/Fonts/) — font-related artifacts 6 ไฟล์และ extraction note

ไม่มี TTF/OTF ที่ตรวจสอบได้; ดู [`EXTRACTION_NOTE.txt`](Assets/Fonts/EXTRACTION_NOTE.txt). `BaseGame_gfxfontlib.gfx` กับ `BaseGame_HUD_Font_LocFont.gfx` มี SHA-256 เดียวกัน (`CCFBC4A7BD1047A5D9CD6C43672D487E588FA3E2913F1D6C82C6C1DFC7C190EB`) และเป็น byte-identical.
