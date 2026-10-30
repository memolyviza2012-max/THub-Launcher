# Avowed — Thai Localization Modding Bible
### Opus Edition — Advanced Deep Analysis (Rivet Engineer)

> **Generated:** 2026-07-06  
> **Analyst:** Rivet Engineer Advanced v2 (Antigravity AI)  
> **Mod Author:** Katatrad Team  
> **Status:** ✅ Complete (10/10 Mandatory Sections)

---

## 1. Overview

**Avowed** เป็นเกม Action RPG มุมมองบุคคลที่หนึ่ง พัฒนาโดย **Obsidian Entertainment** (Xbox Game Studios) บน **Unreal Engine 5** โดยใช้ Codename ภายในว่า **"Alabama"** ม็อดภาษาไทยนี้ใช้สถาปัตยกรรมแบบ **Hybrid** — แยกระบบฟอนต์ (Standard PAK) กับระบบข้อความ (IoStore `.ucas`/`.utoc`) ออกจากกันอย่างชัดเจน ทำให้สามารถอัปเดตฟอนต์หรือข้อความได้อิสระจากกัน

**Mod Architecture Pattern:** Hybrid (Font PAK + IoStore Text)

---

## 2. Technical Stack

| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Unreal Engine 5 |
| **Developer** | Obsidian Entertainment (Xbox Game Studios) |
| **Project Codename** | **Alabama** (พบจากชื่อไฟล์ `Alabama-*` ทุกไฟล์) |
| **Archive Format** | UE5 IoStore (`.ucas`/`.utoc`) + Standard PAK (`.pak`) |
| **AES Encryption** | ❌ **No** — Encryption Flag = `0x00`, EncryptionKeyGuid มี non-zero bytes แต่เป็นส่วนของ index metadata ไม่ใช่ AES key |
| **Compression** | **Oodle** (UE5 IoStore default) — UTOC Compression Method Name Length = 0 หมายถึงใช้ default compressor, UCAS header byte `0x01` บ่งชี้ Oodle block format |
| **Font System** | Font Swapping — `.ufont` ภายในบรรจุ raw TTF/OTF โดยตรง (ไม่มี UE wrapper header) |
| **Thai Font Used** | **Pridi Regular** (Cadson Demak / Katatrad Team) — ทุก weight ใช้ Pridi Regular เดียวกัน |
| **Text System** | UE5 LocRes (Binary) ภายใน IoStore container |
| **Text Encoding** | **UTF-16 LE** (LocRes standard) — พบ Thai UTF-16LE sequences ทั่วทั้ง UCAS, ไม่มี UTF-8 Thai sequences |
| **Mod Complexity** | ★★★☆☆ (ไม่ encrypt, แต่ใช้ IoStore ซึ่งซับซ้อนกว่า Standard PAK) |

---

## 3. โครงสร้างไฟล์ (File Architecture)

### 3.1 Mod Files
```
Avowed/
├── Alabama-Fonts_P.pak       ← 621,164 B (607 KB)  ★ ฟอนต์ไทย (Standard PAK v11)
│                                Mount: ../../../
│                                PAK Magic: E1 12 6F 5A @ offset 621,120
│                                Encryption: ❌ (Flag byte = 0x00)
│
├── Alabama-TH_P.ucas         ← 18,015,334 B (17.2 MB)  ★ ข้อความแปลไทย (IoStore Data)
│                                Compression: Oodle (block-based)
│                                Header byte: 0x01 (Oodle signature)
│
├── Alabama-TH_P.utoc         ← 3,835 B (3.7 KB)  ★ สารบัญข้อความ (IoStore Index)
│                                UTOC Magic: 2D-3D-3D-2D (×4 = 16 bytes)
│                                Version: 5
│                                Entries: 2
│                                Compressed Blocks: 276
│                                Container Flags: 0x10000 (65536)
│
└── Alabama-TH_P.pak          ← 347 B  ★ Dummy PAK (IoStore companion)
                                 Mount: ../../../
                                 PAK Magic: ❌ ไม่มี (เป็น stub PAK ที่เล็กเกินไป)
                                 หน้าที่: บังคับให้ UE5 engine mount IoStore container
```

### 3.2 Naming Convention
```
{ProjectCodename}-{Feature}_P.{ext}
       ↓               ↓       ↓
    Alabama          Fonts    _P = Patch content
    Alabama           TH     .pak / .ucas / .utoc
```

### 3.3 Dummy PAK ทำไมต้องมี?
UE5 IoStore ต้องการ companion `.pak` เพื่อ register mount point กับ engine — แม้ `.pak` นั้นจะว่างเปล่า (347 bytes, ไม่มีข้อมูลจริง) engine จะอ่าน mount point `../../../` จาก PAK header แล้วจึงค้นหา `.ucas`/`.utoc` ที่มีชื่อตรงกัน

> **สำคัญ:** ถ้าลบ `Alabama-TH_P.pak` ออก, engine จะไม่โหลด `Alabama-TH_P.ucas`/`.utoc` เลย แม้ไฟล์จะอยู่ในโฟลเดอร์ที่ถูกต้อง

### 3.4 Install Path
```
{GameInstall}/Alabama/Content/Paks/
├── Alabama-Fonts_P.pak
├── Alabama-TH_P.pak
├── Alabama-TH_P.ucas
└── Alabama-TH_P.utoc
```

---

## 4. Font Analysis

### 4.1 Font Identification

ฟอนต์ทั้ง 4 ไฟล์ใน `Alabama-Fonts_P.pak` ถูกตั้งชื่อตาม Espinosa Nova (ฟอนต์เดิมของเกม) แต่ข้างในเป็น **Pridi Regular** ทั้งหมด:

| ไฟล์ .ufont ในเกม (Espinosa Nova) | ฟอนต์ไทยจริงที่ฝัง | Format | ขนาด | Tables |
|---|---|---|---|---|
| `EspinosaNova_Regular_TabularLining.ufont` | **Pridi Regular** | TTF | 384,588 B | 18 tables |
| `EspinosaNova_BoldTabularLiningNumerals.ufont` | **Pridi Regular** | TTF | 384,588 B | 18 tables |
| `EspinosaNova_ItalicTabularLiningNumerals.ufont` | **Pridi Regular** | OTF (CFF) | 293,524 B | 13 tables |
| `EspinosaNova_BoldItalicTabularLiningNumerals.ufont` | **Pridi Regular** | OTF (CFF) | 293,524 B | 13 tables |

> **หมายเหตุ:** ม็อดเดอร์ใช้ Pridi Regular ตัวเดียวกันทุก weight — ไม่ได้แยก Bold/Italic จริง  
> TTF magic: `00-01-00-00`, OTF magic: `4F-54-54-4F` ("OTTO")

### 4.2 Font Metadata (จาก name table)

| Field | Value |
|---|---|
| **Font Family** | Pridi |
| **Font Subfamily** | Regular |
| **Full Name** | Pridi Regular |
| **PostScript Name** | Pridi-Regular |
| **Version** | 1.001 |
| **Unique ID** | `Version 1.001;CDK;Pridi-Regular;2015;FL840` |
| **Manufacturer** | **CadsonDemak** (Cadson Demak Co., Ltd.) |
| **Designer** | **Katatrad Team** |
| **Copyright** | Copyright (c) 2015, Cadson Demak (info@cadsondemak.com) |
| **License** | **SIL Open Font License v1.1** (OFL) ✅ ปลอดภัยสำหรับการแจกจ่ายม็อด |
| **URL Vendor** | www.cadsondemak.com |
| **URL Designer** | www.katatrad.com |

### 4.3 Thai Glyph Support

| การตรวจสอบ | ผลลัพธ์ |
|---|---|
| **OS/2 ulUnicodeRange3** | `0x00210000` |
| **Thai Unicode Range bit (bit 24)** | `False` ⚠️ |
| **ความหมาย** | OS/2 table ไม่ได้ตั้ง Thai range bit อย่างเป็นทางการ **แต่** Pridi เป็นฟอนต์ไทย-อังกฤษจาก Google Fonts ที่มีอักขระไทยครบ (ก-ฮ, สระลอย, วรรณยุกต์, ตัวเลขไทย ๐-๙) — bit นี้อาจไม่ได้ถูก set เพราะ Pridi ถูก build ด้วย tool รุ่นเก่าของ FontForge/Glyphs |
| **สระลอย + วรรณยุกต์** | ✅ รองรับ (Pridi ออกแบบมาสำหรับจอ, มี mark positioning tables) |

### 4.4 Font Swap Mapping

```
ฟอนต์เดิม (Espinosa Nova)              →  ฟอนต์ไทย (Pridi)
─────────────────────────────────────────────────────────────
EspinosaNova_Regular_TabularLining      →  Pridi Regular (TTF)
EspinosaNova_BoldTabularLiningNumerals  →  Pridi Regular (TTF)  ← ⚠️ ไม่ใช่ Bold จริง
EspinosaNova_ItalicTabularLining...     →  Pridi Regular (OTF)  ← ⚠️ ไม่ใช่ Italic จริง
EspinosaNova_BoldItalicTabularLining... →  Pridi Regular (OTF)  ← ⚠️ ไม่ใช่ BoldItalic จริง
```

> **ข้อสังเกต:** หากต้องการ Bold/Italic ไทยที่ถูกต้อง ควรใช้ Pridi Bold / Pridi Light แยกตาม weight จริง (มีให้ใน Google Fonts)

### 4.5 Font Storage Method

ไฟล์ `.ufont` ในเกมนี้เป็น **Raw TTF/OTF** โดยตรง — ไม่มี Unreal Serialization Header หุ้ม (offset 0 = font magic bytes เลย) ดังนั้นการแก้ไขง่ายมาก:

```
การ Extract:  .ufont → เปลี่ยนนามสกุลเป็น .ttf/.otf → ใช้ได้ทันที
การ Replace:  .ttf/.otf → เปลี่ยนนามสกุลเป็น .ufont → วางในโฟลเดอร์เดิม → repack PAK
```

---

## 5. Text Analysis

### 5.1 IoStore Container Analysis

| ฟิลด์ | ค่า |
|---|---|
| **UTOC Magic** | `2D-3D-3D-2D` (ซ้ำ 4 ครั้ง = 16 bytes) |
| **UTOC Version** | 5 (UE5 standard) |
| **Entry Count** | **2** entries |
| **Compressed Blocks** | **276** blocks |
| **Compression** | Oodle (UE5 IoStore default, block-based) |
| **Container Flags** | `0x10000` (65,536) — EncryptedIndex=false |
| **Mount Point** | `../../../` |

### 5.2 Content Paths ใน UTOC

จากการสแกน ASCII strings ใน UTOC พบ path hierarchy:
```
Alabama/
└── Content/
    └── Exported/
        └── BaseGame/
            └── Localized/
                └── enus/
                    └── Text/
                        └── Text_enus.uasset
```

> **สังเกต:** ข้อความอยู่ใน locale slot `enus` (English US) — ม็อดเดอร์ override ข้อความอังกฤษด้วยข้อความไทย แทนที่จะสร้าง locale ใหม่ วิธีนี้ง่ายที่สุดเพราะไม่ต้องแก้ locale config ของเกม

### 5.3 Text Encoding

| การตรวจสอบ | ผลลัพธ์ |
|---|---|
| **BOM** | ไม่มี (No BOM) |
| **Thai UTF-8 sequences** (E0 B8/B9 xx) | **0** ในทุกตำแหน่ง |
| **Thai UTF-16 LE sequences** (xx 0E) | **พบจำนวนมาก** ทั่วทั้งไฟล์ |
| **สรุป Encoding** | **UTF-16 LE** (LocRes standard format) |

#### Encoding Sampling (ทุก offset มี Thai UTF-16LE):
| Offset (UCAS) | Thai UTF-16LE Count (per 20KB) |
|---|---|
| 0 KB | 15 |
| 100 KB | 1,933 |
| 500 KB | 3,226 |
| 1,000 KB | 2,417 |
| 5,000 KB | 2,813 |
| 10,000 KB | 1,494 |
| 15,000 KB | 2,159 |

> ข้อมูลข้างต้นแสดงว่า **ข้อความไทยกระจายอยู่ทั่วทั้ง UCAS** (18 MB) ไม่ได้กระจุกอยู่ที่เดียว — นี่คือลักษณะของ LocRes ที่บรรจุ string table ขนาดใหญ่ (ประมาณ UI, dialogue, quest log, item description ฯลฯ)

### 5.4 LocRes Structure (คาดการณ์)
```
LocRes Binary Format:
├── Magic Header (LOCRES signature)
├── Namespace Table
│   ├── Namespace 1: "quests/al01/..." (Zone 1 quests)
│   ├── Namespace 2: "quests/al02/..." (Zone 2 quests)
│   ├── Namespace 3: "quests/al03/..." (Zone 3 quests)
│   ├── Namespace N: "ui/..." (UI strings)
│   └── ...
├── Key Table
│   ├── Key: "{StringID}" → Value: "ข้อความภาษาไทย" (UTF-16 LE)
│   └── ...
└── Footer
```

---

## 6. Cross-Engine Comparison

### เปรียบเทียบกับเกม UE5 อื่นๆ ในคลังความรู้

| เกม | Archive | Font | Text | AES | Compression | Complexity |
|---|---|---|---|---|---|---|
| **Avowed** | IoStore + PAK (Hybrid) | Pridi (TTF/OTF in .ufont) | LocRes (UTF-16LE) | ❌ No | Oodle | ★★★☆☆ |
| **The Alters** | Standard PAK only | Noto Sans Thai (TTF in .ufont) | LocRes | ❌ No | None (raw) | ★★☆☆☆ |
| **Clair Obscur** | Standard PAK v11 | Bai Jamjuree (TTF in .ufont) | LocRes | ❌ No | Mixed | ★★★☆☆ |
| **S.T.A.L.K.E.R. 2** | IoStore + PAK | Custom | LocRes | ✅ Yes | Oodle | ★★★★☆ |
| **FF7 Rebirth** | Custom SE format | Custom | LocRes variant | ✅ Yes | Oodle | ★★★★★ |
| **Gothic Remake** | Standard PAK | Alkimia wrapper | LocRes | ❌ No | None | ★★★★☆ |

### Key Insights:
1. **Avowed vs The Alters:** Avowed ซับซ้อนกว่า The Alters เพราะใช้ IoStore สำหรับข้อความ (ต้องมี dummy PAK) ส่วน The Alters ใช้ Standard PAK ไฟล์เดียวง่ายกว่ามาก
2. **Avowed vs Clair Obscur:** Clair Obscur แม้จะมีฟอนต์มากกว่า (37 entries vs 4) แต่ pack ทุกอย่างใน PAK ไฟล์เดียว ส่วน Avowed แยก Font/Text เป็นคนละ archive ทำให้ยืดหยุ่นกว่าในการอัปเดต
3. **Avowed vs STALKER 2:** ทั้งคู่ใช้ IoStore + Oodle แต่ STALKER 2 มี AES encryption ทำให้ซับซ้อนกว่า
4. **Font Strategy:** Avowed, The Alters, Clair Obscur ทั้งหมดใช้ฟอนต์จาก **Cadson Demak** (Pridi, Noto Sans Thai, Bai Jamjuree) — แสดงว่า Cadson Demak fonts เป็นมาตรฐานในวงการม็อดไทย

### ข้อได้เปรียบของ Hybrid Architecture (Avowed-style):
- ✅ อัปเดตฟอนต์ได้โดยไม่กระทบข้อความ (แก้แค่ `Alabama-Fonts_P.pak`)
- ✅ อัปเดตข้อความได้โดยไม่กระทบฟอนต์ (แก้แค่ `Alabama-TH_P.*`)
- ❌ ต้องจัดการ 4 ไฟล์ (vs 1 ไฟล์ของ The Alters / Clair Obscur)

---

## 7. Pipeline — ขั้นตอนสร้างม็อด

### Pipeline A: ฟอนต์ (Standard PAK)

```
ขั้นตอนที่ 1: เตรียมฟอนต์ไทย
   - ดาวน์โหลดฟอนต์ TTF จาก Google Fonts (เช่น Pridi, Sarabun, Bai Jamjuree)
   - หรือใช้ฟอนต์ที่สกัดจากม็อดนี้ได้เลย (SIL OFL license)

ขั้นตอนที่ 2: เปลี่ยนชื่อไฟล์ให้ตรงกับฟอนต์เดิมของเกม
   - Pridi-Regular.ttf → EspinosaNova_Regular_TabularLining.ufont
   - Pridi-Bold.ttf → EspinosaNova_BoldTabularLiningNumerals.ufont
   - Pridi-Regular.otf → EspinosaNova_ItalicTabularLiningNumerals.ufont
   - Pridi-Bold.otf → EspinosaNova_BoldItalicTabularLiningNumerals.ufont

ขั้นตอนที่ 3: วางไฟล์ในโครงสร้างโฟลเดอร์
   Alabama/Content/UI/Fonts/EspinosaNova_Faces/
   ├── EspinosaNova_Regular_TabularLining.ufont
   ├── EspinosaNova_BoldTabularLiningNumerals.ufont
   ├── EspinosaNova_ItalicTabularLiningNumerals.ufont
   └── EspinosaNova_BoldItalicTabularLiningNumerals.ufont

ขั้นตอนที่ 4: Pack ด้วย repak_cli
   E:\Mod_Workspace\Tool\repak_cli\repak.exe pack Alabama-Fonts_P.pak
```

### Pipeline B: ข้อความ (IoStore)

```
ขั้นตอนที่ 1: เตรียม LocRes
   - ใช้ FModel หรือ UnrealLocres ดึง .locres ต้นฉบับจากเกม
   - แก้ไข string table เป็นภาษาไทย (encoding: UTF-16 LE)

ขั้นตอนที่ 2: วางไฟล์ในโครงสร้าง
   Alabama/Content/Exported/BaseGame/Localized/enus/Text/
   └── Text_enus.uasset

ขั้นตอนที่ 3: Pack ด้วย IoStore mode
   - ใช้ UnrealPak ด้วย flag -IoStore เพื่อสร้าง .ucas/.utoc
   - สร้าง dummy .pak (347 bytes) สำหรับ mount point registration

ขั้นตอนที่ 4: วางไฟล์ทั้ง 3 ใน Paks/
   Alabama-TH_P.ucas
   Alabama-TH_P.utoc
   Alabama-TH_P.pak  ← ห้ามลืม! (ถ้าขาดจะไม่โหลด)
```

### Pipeline C: ติดตั้งม็อด (สำหรับผู้เล่น)

```
1. คัดลอก 4 ไฟล์ไปที่:
   {GameInstall}/Alabama/Content/Paks/

2. โครงสร้างสุดท้าย:
   .../Paks/
   ├── (original .pak files)
   ├── Alabama-Fonts_P.pak       ← ม็อดฟอนต์
   ├── Alabama-TH_P.pak          ← ม็อด dummy PAK
   ├── Alabama-TH_P.ucas         ← ม็อดข้อความ
   └── Alabama-TH_P.utoc         ← ม็อดสารบัญ

3. เปิดเกม — ข้อความจะเป็นภาษาไทยอัตโนมัติ
   (ม็อดแทนที่ locale "enus" โดยตรง)
```

---

## 8. Troubleshooting

### 🔴 ปัญหาที่ 1: ฟอนต์ไม่แสดงผล (กลายเป็นกล่อง □□□ หรือเป็นฟอนต์เดิม)
| สาเหตุ | วิธีแก้ |
|---|---|
| ชื่อไฟล์ .ufont ไม่ตรงกับชื่อเดิม | ตรวจสอบว่าชื่อ case-sensitive ถูกต้อง เช่น `EspinosaNova_Regular_TabularLining.ufont` |
| โครงสร้างโฟลเดอร์ไม่ถูก | ต้องอยู่ใน `Alabama/Content/UI/Fonts/EspinosaNova_Faces/` |
| PAK priority ต่ำกว่าไฟล์เกม | ตรวจสอบว่าใช้ `_P` suffix (Patch) ในชื่อ PAK |
| ฟอนต์ไม่รองรับ Thai glyphs | ตรวจสอบว่า TTF มี cmap table ครอบคลุม U+0E01-U+0E7F |

### 🔴 ปัญหาที่ 2: สระลอย/วรรณยุกต์แสดงผิดตำแหน่ง (สระ/วรรณยุกต์ไม่เกาะตัวอักษร)
| สาเหตุ | วิธีแก้ |
|---|---|
| ฟอนต์ไม่มี GPOS/GDEF tables | ใช้ฟอนต์ที่ออกแบบมาสำหรับภาษาไทย (เช่น Pridi, Sarabun, Noto Sans Thai) |
| UE5 text shaping ไม่ support complex script | ปัญหานี้หายากใน UE5 เพราะ HarfBuzz shaper มักเปิดอยู่แล้ว — ถ้าเจอ ลองเปลี่ยนฟอนต์ |
| ขนาดฟอนต์เล็กเกินไป | ข้อความไทยต้องการ line height มากกว่าอังกฤษ — อาจต้องปรับ font size ในเกม |

### 🔴 ปัญหาที่ 3: เกม Crash หลังติดตั้งม็อด
| สาเหตุ | วิธีแก้ |
|---|---|
| ขาด `Alabama-TH_P.pak` (dummy) | ต้องมีครบ 4 ไฟล์ — PAK dummy จำเป็นสำหรับ IoStore mount |
| UTOC version ไม่ตรง | ตรวจสอบว่า UTOC ถูก generate ด้วย tool ที่รองรับ UTOC v5 |
| ไฟล์ corrupt จากการ download | ตรวจสอบขนาดไฟล์: Fonts_P.pak ≈ 621KB, TH_P.ucas ≈ 18MB, TH_P.utoc ≈ 3.8KB, TH_P.pak ≈ 347B |
| เกมอัปเดตแล้วม็อดไม่รองรับ | LocRes format อาจเปลี่ยนหลังอัปเดต — ต้อง rebuild จาก locres ใหม่ |

### 🔴 ปัญหาที่ 4: Encoding เพี้ยน (ข้อความเป็นอักขระแปลกๆ)
| สาเหตุ | วิธีแก้ |
|---|---|
| บันทึก locres เป็น UTF-8 แทน UTF-16 LE | UE5 LocRes ต้องเป็น **UTF-16 LE** เท่านั้น — ใช้ tool locres เฉพาะทาง อย่าแก้ด้วย text editor ธรรมดา |
| Text editor เพิ่ม BOM ให้ | LocRes binary ไม่ต้องการ BOM — ปิด auto-BOM ใน editor |
| Windows-874 encoding | ❌ อย่าใช้ — UE5 ไม่รองรับ Windows-874, ต้องเป็น Unicode เท่านั้น |

### 🔴 ปัญหาที่ 5: ข้อความบางส่วนยังเป็นภาษาอังกฤษ
| สาเหตุ | วิธีแก้ |
|---|---|
| ม็อดยังแปลไม่ครบ | ตรวจสอบ string table ใน LocRes ว่าครบทุก key |
| บาง string อยู่ใน hardcode (C++) | ไม่สามารถแก้ด้วย LocRes ได้ — ต้องใช้ binary patch |
| DLC เพิ่ม string ใหม่ | ต้องสร้าง LocRes เพิ่มสำหรับ DLC content |

---

## 9. Required Tools

| เครื่องมือ | หน้าที่ | แหล่งดาวน์โหลด |
|---|---|---|
| **repak_cli** | Unpack/Pack ไฟล์ PAK (Rust-based, fast) | [GitHub - trumank/repak](https://github.com/trumank/repak) |
| **FModel** | แกะไฟล์เกมต้นฉบับ, ดู Asset hierarchy | [GitHub - 4sval/FModel](https://github.com/4sval/FModel) |
| **UnrealPak** (Epic) | Pack IoStore (.ucas/.utoc) ด้วย `-IoStore` flag | Epic Games Launcher → Engine → Binaries |
| **UE5 Locres Tool** | แปลง/แก้ไข LocRes binary ↔ CSV/JSON | Community tools (NexusMods) |
| **HxD / ImHex** | Hex editor สำหรับ binary analysis | [mh-nexus.de](https://mh-nexus.de/en/hxd/) |
| **FontForge** | ตรวจสอบ/แก้ไขฟอนต์ TTF/OTF | [fontforge.org](https://fontforge.org/) |

### Tool Paths (Local)
```
repak_cli: E:\Mod_Workspace\Tool\repak_cli\repak.exe
```

---

## 10. Extracted Assets

### 10.1 Extracted Fonts (สกัดสำเร็จ ✅)

ฟอนต์ทั้ง 4 ไฟล์ถูกสกัดออกมาเป็น TTF/OTF ที่ใช้งานได้จริง:

| ไฟล์ที่สกัด | Font Name | Format | ขนาด | Verified |
|---|---|---|---|---|
| [EspinosaNova_Regular_TabularLining.ufont.ttf](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unreal_Engine_5/Games/Avowed/Assets/Fonts/EspinosaNova_Regular_TabularLining.ufont.ttf) | Pridi Regular | TTF | 384,588 B | ✅ Shell.Application: "Pridi Regular" |
| [EspinosaNova_BoldTabularLiningNumerals.ufont.ttf](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unreal_Engine_5/Games/Avowed/Assets/Fonts/EspinosaNova_BoldTabularLiningNumerals.ufont.ttf) | Pridi Regular | TTF | 384,588 B | ✅ Shell.Application: "Pridi Regular" |
| [EspinosaNova_ItalicTabularLiningNumerals.ufont.otf](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unreal_Engine_5/Games/Avowed/Assets/Fonts/EspinosaNova_ItalicTabularLiningNumerals.ufont.otf) | Pridi Regular | OTF | 293,524 B | ✅ Shell.Application: "Pridi Regular" |
| [EspinosaNova_BoldItalicTabularLiningNumerals.ufont.otf](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unreal_Engine_5/Games/Avowed/Assets/Fonts/EspinosaNova_BoldItalicTabularLiningNumerals.ufont.otf) | Pridi Regular | OTF | 293,524 B | ✅ Shell.Application: "Pridi Regular" |

### 10.2 Font Files Location
```
E:\Mod_Workspace\Modding-Knowledge\Engines\Unreal_Engine_5\Games\Avowed\Assets\Fonts\
├── EspinosaNova_Regular_TabularLining.ufont.ttf        (384 KB)
├── EspinosaNova_BoldTabularLiningNumerals.ufont.ttf    (384 KB)
├── EspinosaNova_ItalicTabularLiningNumerals.ufont.otf  (293 KB)
└── EspinosaNova_BoldItalicTabularLiningNumerals.ufont.otf (293 KB)
```

> **License Note:** ฟอนต์ Pridi ได้รับอนุญาตภายใต้ SIL Open Font License v1.1 — สามารถแจกจ่ายพร้อมม็อดได้อย่างถูกกฎหมาย ✅

---

*📖 Thai Localization Modding Bible — Opus Edition*  
*สร้างโดย Rivet Engineer Advanced Protocol*
