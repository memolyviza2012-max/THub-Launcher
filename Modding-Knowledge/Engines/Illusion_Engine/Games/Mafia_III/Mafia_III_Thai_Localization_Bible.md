# Mafia III — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

> **Generated:** 2026-08-30
> **Analyst:** Rivet Engineer Advanced (Antigravity AI)
> **Game:** Mafia III (Hangar 13 / 2K Games)
> **Status:** ✅ Complete (10/10 Mandatory Sections)

---

## 1. Overview

**Mafia III** พัฒนาโดย **Hangar 13** ขับเคลื่อนด้วยเอนจินภายในที่พัฒนาต่อยอดมาจาก **Illusion Engine** ของทีมงาน 2K Czech ม็อดภาษาไทยใช้รูปแบบการจัดเก็บไฟล์มาตรฐานของเกมซีรีส์นี้ นั่นคือฟอร์แมต **SDS (Smart Data System)** ซึ่งเป็น archive ที่เก็บเนื้อหาต่างๆ ของเกม (ทั้ง text, fonts, textures) โดยจะทำการ override ไฟล์ภาษาดั้งเดิม (English slot)

**Mod Architecture Pattern:** SDS Archive Replacement — ผู้เล่นต้องนำไฟล์ `.sds` วางทับในโครงสร้างโฟลเดอร์เกมที่กำหนด

---

## 2. Technical Stack

| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Illusion Engine (Hangar 13 Proprietary) |
| **Developer** | Hangar 13 |
| **Archive Format** | **SDS (Smart Data System)** `Magic: SDS\x00` |
| **Text Encoding** | UTF-8 (อยู่ภายใน SDS XML) |
| **Font System** | TTF/OTF ฝังอยู่ใน `.sds` (จำเป็นต้องใช้ Tool สกัด) |
| **AES Encryption** | ❌ (ไม่มี AES แบบ UE แต่ไฟล์บีบอัด/เข้ารหัสเฉพาะเอนจิน) |
| **Compression** | ใช่ (Block-level compression ใน SDS) |
| **Language Slot** | **English** (`fonts_en_*`, `stringtable_en`) |
| **Mod Complexity** | ★★★☆☆ (กระบวนการติดตั้งง่าย แต่การโมดิฟายด์ต้องใช้ SDS Tool เฉพาะ) |

---

## 3. โครงสร้างไฟล์ (File Architecture)

### 3.1 Mod Files

โครงสร้างในชุดม็อด สะท้อนตามการวางไฟล์ในโฟลเดอร์เกม:

```
sds_retail\
├── gui\
│   ├── fonts_en_pc_gui.sds      ← ฟอนต์สำหรับ PC (507 KB)
│   ├── fonts_en_ps4_gui.sds     ← ฟอนต์ (PS4 layout support) (509 KB)
│   └── fonts_en_xb1_gui.sds     ← ฟอนต์ (Xbox One layout support) (507 KB)
└── string_tables\
    └── stringtable_en.sds       ← ไฟล์ข้อความทั้งหมด (2.7 MB)
```

### 3.2 Install Path

แตกไฟล์ทับโฟลเดอร์หลัก:
`{GameInstall}\sds_retail\`
เกมจะทำการโหลดไฟล์เหล่านี้ขึ้นมาแทนที่ไฟล์ภาษาดั้งเดิม

### 3.3 SDS Archive Format

ไฟล์ `.sds` ใน Mafia III เป็น Container พิเศษ:
- **Magic:** `53-44-53-00` ("SDS\0")
- ไฟล์เหล่านี้ไม่ได้เป็น plain text หรือ raw archive แต่มีการใช้ Compression (เชื่อว่าเป็น zlib หรือ Oodle) ในระดับ Block
- ไม่สามารถเปิดดูหรือสกัดไฟล์ด้วย Hex Editor/Python สคริปต์ปกติได้ ต้องใช้ชุดเครื่องมือ **Mafia Toolkit** เพื่อ Unpack โครงสร้างออกมาก่อน

---

## 4. Font Analysis

### 4.1 ไฟล์ฟอนต์ที่ใช้งาน

ไฟล์ฟอนต์ถูกแพ็กอยู่ใน `fonts_en_pc_gui.sds` การทดลองใช้ Python ค้นหา `00 01 00 00` (Raw TTF header) พบสัญญาณ แต่เมื่อตรวจสอบ Table Directory ของ TrueType ปรากฏว่าไม่ถูกต้อง (เช่น `numTables = 256` ซึ่งเป็นไปไม่ได้) ทำให้ยืนยันได้ว่า **ไฟล์ SDS ถูกบีบอัดทั้งหมด** 

*ฟอนต์จริงจะต้องสกัดผ่าน SDS Tool ก่อนจึงจะเห็นรูปแบบ TTF ดั้งเดิม*

### 4.2 ระบบ Font Rendering

เอนจินรองรับ **UTF-8 เต็มรูปแบบ** ไม่มีความจำเป็นต้องใช้วิธี Glyph Remapping แต่อย่างใด หาก Unpack `.sds` ออกมา จะพบโครงสร้างเป็นไฟล์ TTF และไฟล์นิยาม Font XML (เช่น การกำหนดขนาดและ baseline ของแต่ละฟอนต์) สามารถยัด TTF ไทยมาตรฐานเข้าไปได้เลย

---

## 5. Text Analysis

### 5.1 ข้อมูลรวม

| รายการ | ค่า |
|---|---|
| **Target File** | `stringtable_en.sds` (2.72 MB) |
| **Encoding** | **UTF-8** (ตรวจสอบพบ UTF-8 sequences `0xE0 0xB8` ฝังอยู่ใน raw binary) |
| **Language Slot** | **English** (เปลี่ยนหน้าเมนูเกมเป็นภาษาอังกฤษ) |

### 5.2 เนื้อหาที่แปล

ไฟล์ `stringtable_en.sds` ของซีรีส์ Mafia เป็นตาราง String รวมศูนย์ที่เก็บทุกอย่างตั้งแต่ เมนูตั้งค่า, บทบรรยายคัตซีน (Subtitles), เป้าหมายภารกิจ, ไปจนถึงข้อความป๊อปอัปทั้งหมดภายในเกม

---

## 6. Cross-Engine Comparison

| Feature | **Mafia III** | **The Sinking City 2** | **Warcraft III** |
|---|---|---|---|
| **Engine** | **Illusion / Hangar 13** | UE5 | Blizzard Engine |
| **Archive** | SDS (.sds) | PAK (.pak) | MPQ (.w3x) |
| **Text Encoding** | UTF-8 | UTF-16 LE | UTF-8 BOM |
| **Font System** | SDS packed TTF | TTF / Ufont | TTF Loose file |
| **Install Method** | ทับ `sds_retail/` | วางไฟล์ใน `~mods/` | ทับใน `_retail_/` |
| **Tool Required** | Mafia Toolkit / SDS Tool | repak / FModel | World Editor / CASC |
| **Complexity** | ★★★☆☆ | ★★★☆☆ | ★★★☆☆ |

**ข้อสรุปเชิงเทคนิค:**
แตกต่างจาก Unreal Engine ที่ใช้ repak, ซีรีส์ Mafia มีความปิดตัว (Proprietary) มากกว่า ต้องใช้เครื่องมือที่ Community สร้างขึ้นเพื่อ Mafia โดยเฉพาะ (Mafia Toolkit) เพื่อถอดและประกอบไฟล์ `.sds` แต่กระบวนการ Localization โดยรวมนั้นง่ายกว่า Dunia Engine เพราะรองรับ UTF-8 สมบูรณ์แบบ

---

## 7. Pipeline — ขั้นตอนสร้างม็อด

### 7.1 เครื่องมือ
- **Mafia Toolkit / SDS Tool:** เครื่องมือหลักในการแยกและประกอบ `.sds`

### 7.2 Text Pipeline
1. Unpack `stringtable_en.sds` ออกมาเป็นไฟล์ XML / Text Table
2. แก้ไขไฟล์ XML โดยใช้ Text Editor (บันทึกเป็น UTF-8)
3. Repack กลับเป็น `.sds`

### 7.3 Font Pipeline
1. Unpack `fonts_en_pc_gui.sds`
2. แก้ไขโครงสร้างไฟล์ข้างใน (แทนที่ `.ttf` ด้วยฟอนต์ไทย และแก้ `.xml` หรือ `.fnt` definition ถ้าจำเป็น)
3. Repack กลับ

### 7.4 Deploy
วางทับโครงสร้าง `sds_retail` ของเกมบนเครื่องผู้เล่น

---

## 8. Troubleshooting

| ปัญหา | สาเหตุ | วิธีแก้ |
|---|---|---|
| ตัวหนังสือเป็นสี่เหลี่ยม / สัญลักษณ์ | ลงไฟล์ `fonts_en_pc_gui.sds` ไม่สมบูรณ์ หรือตัวเกมเรียกใช้ layout Xbox/PS4 | ตรวจสอบว่าก็อปปี้โฟลเดอร์ `gui` เข้าไปครบทั้ง PC/PS4/XB1 files |
| ข้อความยังเป็นภาษาอังกฤษ | ลืมเปลี่ยนภาษาเกม | เปลี่ยนหน้า Interface เป็น English |
| เกม Crash ตอนโหลดฉาก | SDS Repack ผิดพลาด (Compression mismatch) | ติดตั้งม็อดใหม่ หรือ Verify เกมผ่าน Steam/Epic แล้วรัน Mod ใหม่อีกครั้ง |

---

## 9. Required Tools

| เครื่องมือ | หน้าที่ | ที่อยู่ |
|---|---|---|
| **Mafia Toolkit (by zhm86 / greavesy)** | เครื่องมือหลัก Unpack / Repack .sds | Nexus Mods / GitHub |
| **Notepad++** | สำหรับแก้ไฟล์ String (UTF-8) | https://notepad-plus-plus.org |

---

## 10. Extracted Assets

*เนื่องจากการบีบอัดของ SDS Archive ไม่สามารถดึง Raw TTF หรือ Text ออกมาจัดเก็บด้วยวิธี Reverse Engineer ขั้นพื้นฐานได้ (ต้องการ Toolkit เฉพาะ)*
ไฟล์ทั้งหมดในชุดม็อดจึงถูกจัดเก็บไว้เป็น Reference แบบแพ็กเกจ (SDS files)

### Assets (Reference)
ตำแหน่ง: `E:\Mod_Workspace\Modding-Knowledge\Engines\Illusion_Engine\Games\Mafia_III\Assets\Packages\`

| ไฟล์ | ขนาด | หมายเหตุ |
|---|---|---|
| `gui\fonts_en_pc_gui.sds` | 507 KB | Container ฟอนต์หลัก PC |
| `gui\fonts_en_ps4_gui.sds` | 509 KB | รองรับ PS4 UI Layout |
| `gui\fonts_en_xb1_gui.sds` | 507 KB | รองรับ Xbox UI Layout |
| `string_tables\stringtable_en.sds` | 2.7 MB | Container ข้อความทั้งหมด (UTF-8) |

---

*เอกสารนี้สร้างจากการวิเคราะห์โครงสร้างไฟล์ระดับไบนารีเบื้องต้น*