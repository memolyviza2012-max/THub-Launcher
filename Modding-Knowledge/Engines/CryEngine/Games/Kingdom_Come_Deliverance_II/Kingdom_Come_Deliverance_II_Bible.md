# Kingdom Come: Deliverance II — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

> **Generated:** 2026-09-11
> **Analyst:** Rivet Engineer Advanced (Antigravity AI)
> **Game:** Kingdom Come: Deliverance II (Warhorse Studios)
> **Mod:** ม็อดภาษาไทย (ไม่ระบุม็อดเดอร์/เวอร์ชันชัดเจน)
> **Status:** ✅ Complete (10/10 Mandatory Sections)

---

## 1. Overview

**Kingdom Come: Deliverance II** เป็นเกม Open World RPG ยุค Medieval Bohemia สร้างโดย **Warhorse Studios** ขับเคลื่อนด้วย **CryEngine** (สาย CRYENGINE V ที่ปรับปรุงเฉพาะทาง) ม็อดภาษาไทยมาพร้อม **4 ตัวเลือกให้ผู้เล่น** ผสมกันระหว่าง 2 รูปแบบฟอนต์ × 2 ขอบเขตการแปล พร้อมภาพเปรียบเทียบฟอนต์ให้ดูก่อนตัดสินใจ

**Mod Architecture:** CryEngine Mod Directory — วางโฟลเดอร์ `mods/thaimod/` ในโฟลเดอร์เกม ระบบ Mod Loading ของ CryEngine จะโหลด PAK จาก mod directory โดยอัตโนมัติ ไม่ต้องทับไฟล์เกมเลยแม้แต่ไฟล์เดียว

---

## 2. Technical Stack

| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | CryEngine V (Warhorse Studios branch) |
| **Developer** | Warhorse Studios |
| **Archive Format** | **CryPAK** — ZIP format ตรง ๆ (Magic: `50-4B-03-04` = "PK") ใส่นามสกุล `.pak` |
| **Text Format** | **XML** — Bilingual table `<Row><Cell>key</Cell><Cell>EN</Cell><Cell>TH</Cell></Row>` |
| **Text Encoding** | **UTF-8** |
| **Font Format** | **GFx/Scaleform** — Compressed Flash font (`.gfx`, Magic: `43-46-58` = "CFX") |
| **Language Slot** | **English** (ทับข้อความอังกฤษใน English_xml.pak) |
| **Mod System** | CryEngine native `mods/` directory — **ไม่แตะไฟล์เกมเดิม** |
| **AES Encryption** | ❌ ไม่มี |
| **Install** | วาง `mods/thaimod/` ในโฟลเดอร์เกม → เข้าเกมได้เลย |
| **Mod Complexity** | ★★☆☆☆ (ติดตั้งง่ายมาก แต่การสร้าง GFx font ไม่ง่าย) |

---

## 3. โครงสร้างไฟล์ (File Architecture)

### 3.1 ม็อดมี 4 ตัวเลือก (2×2 Matrix)

| | **เฉพาะซับไตเติล** | **แปลหมด** |
|---|---|---|
| **ฟอนต์สมัยใหม่** | Font 3.1 MB + Loc 12.0 MB | Font 3.1 MB + Loc 13.0 MB |
| **ฟอนต์แนวโบราณ** | Font 5.2 MB + Loc 12.0 MB | Font 5.2 MB + Loc 13.0 MB |

- **ฟอนต์สมัยใหม่** — ตัวอักษรทันสมัย สะอาดตา อ่านง่าย (~3.1 MB)
- **ฟอนต์แนวโบราณ** — ตัวอักษรสไตล์ยุคกลาง เข้ากับบรรยากาศเกม (~5.3 MB)
- **เฉพาะซับไตเติล** — แปลเฉพาะบทสนทนา/ซับไตเติลคัตซีน UI ยังเป็นอังกฤษ
- **แปลหมด** — แปลทุกอย่าง รวมเมนู ไอเทม เควสต์ ทิวทอเรียล (+8% ข้อมูล)

### 3.2 โครงสร้างโฟลเดอร์ (ทุก variant เหมือนกัน)

```
mods/
└── thaimod/
    ├── Data/
    │   └── ThaiFont.pak           ← ฟอนต์ไทย (GFx/Scaleform)
    └── Localization/
        └── English_xml.pak        ← ข้อความภาษาไทย (XML)
```

### 3.3 Install Path

```
{GameInstall}\KingdomComeDeliverance2\mods\thaimod\Data\ThaiFont.pak
{GameInstall}\KingdomComeDeliverance2\mods\thaimod\Localization\English_xml.pak
```

> **📌 สำคัญ:** ม็อดใช้ระบบ `mods/` ของ CryEngine — ไม่ต้องทับ PAK ของเกมเลย! CryEngine จะโหลด PAK จาก mod directory แล้ว override เนื้อหาที่ path ตรงกันโดยอัตโนมัติ ถอนม็อดแค่ลบโฟลเดอร์ `mods/thaimod/` ทิ้ง

---

## 4. Font Analysis

### 4.1 CryEngine GFx/Scaleform Font System

CryEngine ใช้ **Scaleform GFx** สำหรับ UI ทั้งหมด ฟอนต์ถูกเก็บเป็น **Compressed Flash Font** (`.gfx`) ภายใน PAK

| ไฟล์ GFx | หน้าที่ | Magic |
|---|---|---|
| `Libs/UI/gfxfontlib.gfx` | **Font Library** — ตัวกำหนดชื่อฟอนต์และ mapping | `43-46-58` ("CFX") |
| `Libs/UI/gfxfontlib_glyphs.gfx` | **Glyph Atlas** — ข้อมูล Glyph ของตัวอักษรทั้งหมด | `43-46-58` ("CFX") |

### 4.2 เปรียบเทียบ 2 รูปแบบฟอนต์

| รายการ | ฟอนต์สมัยใหม่ | ฟอนต์แนวโบราณ |
|---|---|---|
| **ThaiFont.pak** | 3,127 KB | **5,287 KB** (+69%) |
| **gfxfontlib.gfx** | 65.7 KB | 65.7 KB (เหมือนกัน) |
| **gfxfontlib_glyphs.gfx** | 3,119 KB | **5,283 KB** (+69%) |
| **สไตล์** | ทันสมัย สะอาดตา | ยุคกลาง เข้ากับบรรยากาศ |
| **เหมาะสำหรับ** | อ่านง่าย เน้นประสบการณ์ | Immersion เต็มที่ |

> **⚡ Key Finding:** ไฟล์ `gfxfontlib.gfx` (Font Library / mapping) มีขนาด **เท่ากัน 65.7 KB** ทั้ง 2 variant แสดงว่า mapping ของ font name → glyph เหมือนกัน ต่างกันแค่ Glyph Atlas (รูปร่างตัวอักษร)

### 4.3 GFx Compression

ทั้ง `gfxfontlib.gfx` และ `gfxfontlib_glyphs.gfx` มี header `43-46-58` (CFX) ตามด้วย byte `78-DA` หรือ `78-9C` ซึ่งคือ **zlib compression header** — GFx file เป็น zlib-compressed SWF

---

## 5. Text Analysis

### 5.1 XML Format — Bilingual Table

```xml
<Table>
<Row><Cell>ui_dlc_bandit_camps</Cell><Cell>Brushes with Death</Cell><Cell>สัมผัสแห่งมรณะ</Cell></Row>
<Row><Cell>ui_dlc_barber</Cell><Cell>Barber</Cell><Cell>ช่างตัดผม</Cell></Row>
</Table>
```

**โครงสร้าง:** `<Cell>` 3 คอลัมน์:
1. **Key** — ชื่อตัวแปรของเกม
2. **English** — ข้อความต้นฉบับภาษาอังกฤษ
3. **Thai** — ข้อความแปลภาษาไทย

### 5.2 ไฟล์ข้อความ 11 ไฟล์

| ไฟล์ XML | Sub-only | Full | Diff | เนื้อหา |
|---|---|---|---|---|
| **text_ui_dialog.xml** | 39,132 KB | 39,132 KB | **0%** | บทสนทนา/ซับไตเติล (ใหญ่สุด!) |
| text_ui_quest.xml | 2,543 KB | 3,385 KB | +33% | เควสต์/ภารกิจ |
| text_ui_items.xml | 1,759 KB | 2,365 KB | +34% | ไอเทม/อาวุธ/ชุดเกราะ |
| text_ui_menus.xml | 1,513 KB | 1,966 KB | +30% | เมนู/ตั้งค่า |
| text_ui_soul.xml | 652 KB | 845 KB | +30% | ระบบตัวละคร/สกิล/เลเวล |
| text_ui_misc.xml | 261 KB | 320 KB | +23% | ข้อความทั่วไป |
| text_ui_tutorials.xml | 109 KB | 133 KB | +22% | บทช่วยสอน |
| text_ui_minigames.xml | 18 KB | 23 KB | +25% | มินิเกม (ตีเหล็ก, เล่นแร่แปรธาตุ) |
| text_rich_presence.xml | 1.3 KB | 1.6 KB | +17% | Steam Rich Presence |
| text_ui_menu.xml | 0.9 KB | 1.0 KB | +11% | DLC menu items |
| text_ui_ingame.xml | 0.4 KB | 0.5 KB | +17% | HUD notifications |

### 5.3 ข้อมูลสำคัญ

- **`text_ui_dialog.xml`** ขนาด **39 MB** (uncompressed) — ไฟล์บทสนทนาไฟล์เดียวใหญ่ที่สุดใน KB ทั้งหมด!
- เวอร์ชัน Subtitle-only กับ Full ใช้ **dialog.xml ตัวเดียวกัน** (0% diff) → บทสนทนาแปลครบ 100% ทั้ง 2 variant
- ส่วนต่างอยู่ที่ UI text เช่น ชื่อไอเทม (+34%), เควสต์ (+33%), เมนู (+30%)

---

## 6. Cross-Engine Comparison

| Feature | **KCD II** | **XCOM: Chimera Squad** | **Atelier Ryza DX** |
|---|---|---|---|
| **Engine** | **CryEngine V** | Unreal Engine 3 | Gust Engine |
| **Font System** | GFx/Scaleform (`.gfx`) | GFx/Scaleform (`.upk`) | Glyph Width in .exe |
| **Text Format** | XML bilingual table | INI key=value | PAK internal |
| **Mod Install** | **Native mod dir** (non-destructive!) | File copy (destructive) | PAK overwrite |
| **Multiple Variants** | **✅ 4 variants (2×2)** | ❌ | ❌ |
| **Complexity** | ★★☆☆☆ | ★★☆☆☆ | ★★★★☆ |

> **สิ่งที่โดดเด่น:** KCD II เป็นม็อดเดียวใน KB ที่ใช้ CryEngine native mod system — **ไม่ต้องทับไฟล์เกมเลย** ติดตั้งและถอนได้สะอาดที่สุด

---

## 7. Pipeline — ขั้นตอนสร้างม็อด

### 7.1 Text Pipeline
1. แตก `English_xml.pak` ของเกม (เป็น ZIP ตรง ๆ ใช้ 7-Zip ได้)
2. แก้ไข XML — เพิ่มคอลัมน์ `<Cell>` ที่ 3 เป็นข้อความไทย
3. Pack กลับเป็น ZIP แล้วเปลี่ยนนามสกุลเป็น `.pak`
4. วางใน `mods/thaimod/Localization/`

### 7.2 Font Pipeline
1. สร้าง GFx font ด้วย **Adobe Flash Professional / Animate** หรือ **GFxExport**
2. ฝัง Glyph ไทยทั้งชุดลงใน `gfxfontlib_glyphs.gfx`
3. อัปเดต `gfxfontlib.gfx` ให้ map ชื่อฟอนต์ไปยัง glyph ที่ถูกต้อง
4. Pack ทั้ง 2 ไฟล์ลง `ThaiFont.pak` (ZIP)

### 7.3 Variant Pipeline
- สร้าง 4 ชุดจาก font × scope combination
- ให้ภาพตัวอย่าง (PNG) เพื่อให้ผู้เล่นเลือกก่อนติดตั้ง

---

## 8. Troubleshooting

| ปัญหา | สาเหตุ | วิธีแก้ |
|---|---|---|
| เกมยังเป็นภาษาอังกฤษ | โฟลเดอร์ `mods/` วางผิดที่ | ต้องอยู่ใน `KingdomComeDeliverance2/mods/thaimod/` |
| ฟอนต์ไทยไม่ขึ้น | `ThaiFont.pak` หายหรือวางผิด path | ต้องอยู่ใน `mods/thaimod/Data/` |
| อยากเปลี่ยนฟอนต์ | เลือกผิดชุด | ก็อป `ThaiFont.pak` จากชุดที่ต้องการทับ |
| อยากเปลี่ยนขอบเขตแปล | เลือกผิดชุด | ก็อป `English_xml.pak` จากชุดที่ต้องการทับ |
| ถอนม็อด | — | ลบโฟลเดอร์ `mods/thaimod/` ทั้งหมด |

---

## 9. Required Tools

| เครื่องมือ | หน้าที่ |
|---|---|
| **7-Zip / WinRAR** | แตก/สร้าง PAK (เพราะเป็น ZIP) |
| **Text Editor** (VSCode / Notepad++) | แก้ไข XML |
| **Adobe Animate / GFxExport** | สร้าง GFx font files |

---

## 10. Extracted Assets

ตำแหน่ง: `E:\Mod_Workspace\Modding-Knowledge\Engines\CryEngine\Games\Kingdom_Come_Deliverance_II\`

### Font PAKs
| ไฟล์ | ขนาด | ที่อยู่ใน KB |
|---|---|---|
| ThaiFont_Modern.pak | 3,127 KB | `Assets\Fonts_Modern\` |
| ThaiFont_OldStyle.pak | 5,287 KB | `Assets\Fonts_OldStyle\` |

### Localization PAKs
| ไฟล์ | ขนาด | ที่อยู่ใน KB |
|---|---|---|
| English_xml_SubtitleOnly.pak | 12,250 KB | `Assets\Localization\` |
| English_xml_FullTranslation.pak | 13,269 KB | `Assets\Localization\` |

### Screenshots
| ไฟล์ | ที่อยู่ใน KB |
|---|---|
| ตัวอย่างฟอนต์สมัยใหม่.png | `Assets\Screenshots\` |
| ตัวอย่างฟอนต์แนวโบราณ.png | `Assets\Screenshots\` |

---

## Appendix A: CryEngine PAK Format Deep Dive

CryEngine ใช้ไฟล์ `.pak` ที่เป็น **ZIP format มาตรฐาน** (Magic: `50-4B-03-04`) ตามด้วย:
- Local File Header
- Compressed file data (Deflate)
- Central Directory

สามารถแตก/สร้างด้วยเครื่องมือ ZIP ทั่วไปได้เลยโดยไม่ต้องมีเครื่องมือพิเศษ — เป็นจุดแตกต่างสำคัญจาก Unreal PAK หรือ Gust PAK ที่ต้องใช้เครื่องมือเฉพาะทาง

## Appendix B: GFx Font Format Deep Dive

ไฟล์ `.gfx` ของ Scaleform ประกอบด้วย:
- **Header:** `43-46-58` ("CFX") + version byte
- **Body:** zlib-compressed SWF data (`78-DA` = best compression / `78-9C` = default)
- เก็บ Font Vector data, Glyph metrics, Kerning table ทั้งหมดในรูปแบบ Flash/SWF

## Appendix C: XML Bilingual Format Specification

```xml
<Table>
  <Row>
    <Cell>{string_key}</Cell>         <!-- Internal key name -->
    <Cell>{english_text}</Cell>       <!-- Original English -->
    <Cell>{translated_text}</Cell>    <!-- Thai translation -->
  </Row>
</Table>
```

- Encoding: UTF-8
- ข้อความอังกฤษยังคงอยู่ใน Column 2 เสมอ → สะดวกในการ diff และตรวจสอบ
- สามารถ extract แล้วแปลด้วย spreadsheet (Excel, Google Sheets) ได้ตรง ๆ

---

*เอกสารนี้สร้างจากการวิเคราะห์ ZIP/CryPAK header, GFx CFX format, XML bilingual structure, และ 4-variant architecture*
*ม็อด KCD II เป็นตัวอย่างที่ดีที่สุดของ "Non-destructive modding" — ไม่แตะไฟล์เกมเดิมเลยแม้แต่ไบต์เดียว*