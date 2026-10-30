# Warcraft III: Reforged — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

> **Generated:** 2026-08-30
> **Analyst:** Rivet Engineer Advanced (Antigravity AI)
> **Mod:** Warcraft 3 Reforged Mod Thai By LUNG DEAR
> **Status:** ✅ Complete (10/10 Mandatory Sections)

---

## 1. Overview

**Warcraft III: Reforged** เป็นเกม RTS ระดับตำนานที่ถูกนำมารีมาสเตอร์โดย **Blizzard Entertainment** ตัวม็อดภาษาไทยผลงานของ **ลุงเดียร์ (Lung Dear)** นำเสนอการแปลแบบจัดเต็ม ครอบคลุมทั้งแคมเปญ **Reign of Chaos** และ **The Frozen Throne** รวมทั้งหมด 96 แมพ (Maps) นอกจากนี้ยังแปล UI, ยูนิต, ไอเทม, สกิล และซับไตเติลคัตซีน

**Mod Architecture Pattern:** Loose File Override — วางไฟล์ทับโฟลเดอร์เกมโดยตรง ไม่ได้แก้ไขไฟล์ต้นฉบับเลย เป็นวิธีที่ปลอดภัยและถอดถอนได้ง่าย

---

## 2. Technical Stack

| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Blizzard Engine (Warcraft III Reforged) |
| **Developer** | Blizzard Entertainment |
| **Archive Format** | CASC (Base game), MPQ (`.w3x` maps) |
| **Mod Method** | Loose File Override ในโฟลเดอร์ `_retail_` |
| **Text Encoding** | **UTF-8 BOM** (สมบูรณ์แบบสำหรับภาษาไทย) |
| **Font System** | **TTF Standard** (`fonts\BLQ55Web.ttf`, `BLQ85Web.ttf`) |
| **AES Encryption** | ❌ ไม่มี |
| **Language Slot** | English (Loose files โหลดทับภาษาหลัก) |
| **Mod Complexity** | ★★★☆☆ (กระบวนการแปลตรงไปตรงมา แต่มีข้อจำกัดเรื่อง Game Cache) |

---

## 3. โครงสร้างไฟล์ (File Architecture)

### 3.1 Mod Files

โครงสร้างไฟล์ในชุดม็อด สะท้อนตามโฟลเดอร์ของเกม:

```
_retail_\
├── campaign\
│   └── thaimods\
│       ├── roc\        ← Reign of Chaos campaign maps (.w3x)
│       └── tft\        ← The Frozen Throne campaign maps (.w3x)
├── fonts\
│   ├── BLQ55Web.ttf    ← BlizQuadrata Web (Regular)
│   └── BLQ85Web.ttf    ← BlizQuadrata Web Bold
├── movies\
│   └── captions\       ← Subtitles สำหรับคัตซีน (.srt)
├── ui\
│   └── framedef\       ← UI strings (.fdf)
└── units\              ← Unit/Item/Skill strings (.txt)
```

### 3.2 Install Path

แตกไฟล์ทับโฟลเดอร์ติดตั้งหลัก:
`{GameInstall}\_retail_\`
โฟลเดอร์ย่อยข้างในจะทำงานแบบ Loose file system เข้าไปทับไฟล์เกมเดิมใน Memory โดยไม่เขียนทับไฟล์ gốc (Base Files) ใน CASC Archive

### 3.3 MPQ Container (.w3x)

แมพของ Warcraft III (แม้จะเป็น Reforged) ยังคงเก็บข้อมูลในรูปแบบ **MPQ Archive**:
- Magic: `4D-50-51-1A` (`MPQ `)
- ภายในประกอบด้วยไฟล์ข้อมูลต่างๆ ของแต่ละฉาก (เช่น `war3map.wts` สำหรับ text string)

---

## 4. Font Analysis

### 4.1 ฟอนต์ที่ใช้งาน

เกมใช้ฟอนต์ **BlizQuadrata Web** (ชื่อไฟล์ `BLQ55Web.ttf` และ `BLQ85Web.ttf`) สำหรับแสดงผลข้อความส่วนใหญ่ ม็อดเดอร์ได้ทำการแทนที่ไฟล์เหล่านี้ด้วยฟอนต์ที่มี **Glyph ภาษาไทย** โดยรองรับการแสดงผลสระและวรรณยุกต์ได้อย่างถูกต้อง (แก้ปัญหาสระลอย/จมแล้ว)

| File | Family | Magic | Size |
|---|---|---|---|
| BLQ55Web.ttf | BlizQuadrata Web | `00-01-00-00` (Raw TTF) | 149.6 KB |
| BLQ85Web.ttf | BlizQuadrata Web Bold | `00-01-00-00` (Raw TTF) | 150.7 KB |

### 4.2 ระบบ Font Rendering

รองรับ **UTF-8** สมบูรณ์ การนำเข้าฟอนต์จึงไม่จำเป็นต้องใช้เทคนิคซับซ้อนอย่าง Glyph Remapping (อย่างใน Dunia Engine สมัยก่อน) เพียงแค่นำ TTF ฟอนต์ไทยที่ตั้งชื่อตามต้นฉบับไปวางในโฟลเดอร์ `fonts\`

---

## 5. Text Analysis

### 5.1 ข้อมูลรวม

| รายการ | ค่า |
|---|---|
| **จำนวนเนื้อหา** | 96 Maps, 9 Cutscenes, UI/Units/Items ทั้งหมด |
| **Encoding** | **UTF-8 BOM** |
| **Format** | `.txt`, `.fdf` (UI Definition), `.srt` (Subtitles), `.w3x` (Map Text) |

### 5.2 เนื้อหาที่แปล

**[แคมเปญ]**
- แปลข้อความ Objective และบทสนทนาในด่านแคมเปญ RoC และ TFT ครบ 96 ด่าน

**[คัตซีน]**
- แปล `.srt` สำหรับวิดีโอคัตซีนทั้ง 9 ฉาก (เช่น `introx.srt`, `orced.srt`)

**[ยูนิต ไอเทม และระบบ]**
- `units/` (.txt): ชื่อและคำอธิบาย ยูนิต ไอเทม สกิล
- `ui/` (.fdf, .txt): เมนูหลัก, เป้าหมาย, แจ้งเตือน

### 5.3 ข้อจำกัดร้ายแรง: Game Cache ถูกปิด

Warcraft 3 นำเสนอข้อความแคมเปญแยกเป็นรายด่าน (`.w3x`) 
ม็อดเดอร์ทำการ **เปิดและแก้ไขไฟล์แมพ** เพื่อแปลข้อความภายใน ส่งผลให้เมื่อรันเกม ระบบตรวจจับความถูกต้องของตัวเกม (Checksum/Tampering check) จะพบว่าไม่ใช่แมพทางการ
**ผลลัพธ์:** เกมจะ **ปิดระบบ Game Cache** ทันที ทำให้ "ไอเทม และ เลเวลฮีโร่" ไม่ถูกส่งต่อไปยังด่านถัดไป (ฮีโร่กลับมาเริ่มใหม่ด้วยสถานะเริ่มต้นทุกด่าน)

---

## 6. Cross-Engine Comparison

| Feature | **Warcraft III Reforged** | **Far Cry 2** | **FF7 Rebirth** |
|---|---|---|---|
| **Engine** | **Blizzard Engine** | Dunia Engine | UE5 |
| **Archive** | CASC / Loose / MPQ | MAGM | PAK |
| **Text Encoding** | **UTF-8 BOM** | ISO-8859-1 | UTF-8 |
| **Font** | **TTF (Standard Override)** | Glyph Remapping | TTF (pak replacement) |
| **Install Method** | `_retail_` (Loose files) | แทนที่ Archive เดิม | `~mods` folder |
| **Verify Safe** | ✅ ปลอดภัย (ไม่แก้ไฟล์เดิม) | ✅ ปลอดภัย (มี backup) | ✅ ปลอดภัย |
| **Complexity** | ★★★☆☆ | ★★★☆☆ | ★★★★★ |

**ข้อสรุปเชิงเทคนิค:**
เกมยุคเก่าที่ถูก Reforge ให้ระบบ Override ไฟล์อย่างอิสระ ถือเป็นความสะดวกสำหรับ Modder (คล้าย Bethesda/Skyrim) ทว่าดันมีข้อกำจัดฝังรากลึกใน Engine เดิม ที่เกี่ยวกับการตรวจสอบ Custom Map ทำให้ส่งผลกระทบต่อ Progression ของ Campaign อย่างหลีกเลี่ยงไม่ได้ในขณะนี้

---

## 7. Pipeline — ขั้นตอนสร้างม็อด

### 7.1 Text Pipeline
1. แยกข้อความจากไฟล์ในเกม/ใช้ CASC Extractor
2. แปลข้อความในไฟล์ `.txt`, `.fdf`, `.srt` โดยใช้ Editor ทั่วไป (บันทึกเป็น UTF-8 BOM)
3. สำหรับในแมพ ให้เปิดไฟล์ด่าน `.w3x` ใน **World Editor** ทำการแปล String Editor และเซฟใหม่

### 7.2 Font Pipeline
1. สร้าง/เลือกฟอนต์ TTF ภาษาไทย
2. ตั้งชื่อไฟล์ให้ตรงกับฟอนต์ระบบ (`BLQ55Web.ttf`, `BLQ85Web.ttf`)
3. นำไปใส่ใน `_retail_\fonts\`

### 7.3 Deploy
แตกโฟลเดอร์ไปวางรวมกับโฟลเดอร์ของเกม ตัวเกมจะทำการอ่าน Loose files ขึ้นมาทับตัว Base

---

## 8. Troubleshooting

| ปัญหา | สาเหตุ | วิธีแก้ |
|---|---|---|
| ฮีโร่เลเวลลด/ไอเทมหายตอนขึ้นด่านใหม่ | เกมปิด Game Cache (มองว่าเป็น Custom Map) | ปัจจุบันยังแก้ไม่ได้ ต้องยอมรับข้อจำกัดของ Engine |
| อัปเดตเกมแล้วกลับเป็นภาษาอังกฤษ | แพตช์ไปลบหรือปรับโครงสร้าง Loose file | วางไฟล์ Mod ทับอีกครั้งหลังอัปเดตเสร็จ |
| Credits จบ RoC เป็นภาษาอังกฤษ | ไม่ได้อยู่ในชุดแมพ Reforged | ปกติ (Modder แจ้งไว้แล้ว) |

---

## 9. Required Tools

| เครื่องมือ | หน้าที่ | ที่อยู่ |
|---|---|---|
| **CascView / CASC Explorer** | สกัดไฟล์ต้นฉบับจากตัวเกม | Github (WoW modding tools) |
| **Warcraft III World Editor** | เปิด/แปล ข้อความและบันทึก `.w3x` | มาพร้อมตัวเกม |
| **Text Editor** | แก้ไขข้อความ และตั้ง Encoding เป็น UTF-8 BOM | VSCode / Notepad++ |

---

## 10. Extracted Assets

ฟอนต์ TTF ถูกสกัดออกมาเก็บไว้เรียบร้อย พร้อมสำหรับทำความเข้าใจโครงสร้าง

### Assets (Reference)
ตำแหน่ง: `E:\Mod_Workspace\Modding-Knowledge\Engines\Blizzard_Engine\Games\Warcraft_3_Reforged\`

| โฟลเดอร์ | รายละเอียด |
|---|---|
| `Assets\Fonts\` | เก็บไฟล์ .ttf (BLQ55Web, BLQ85Web) |
| `Assets\Localization\` | เก็บไฟล์ตัวอย่าง `.srt` และ `.txt` (UTF-8 BOM) |
| `Assets\Packages\` | โฟลเดอร์เปล่า (ไม่มีการสร้าง/อ้างอิง Package เฉพาะ) |

---

*เอกสารนี้สร้างจากการวิเคราะห์โครงสร้างไฟล์และฟอนต์จากม็อดที่พัฒนาโดยลุงเดียร์*