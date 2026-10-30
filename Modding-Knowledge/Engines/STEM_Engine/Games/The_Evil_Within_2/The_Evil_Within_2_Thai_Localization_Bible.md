# The Evil Within 2 — Thai Localization Modding Bible
### Revised Edition — Deep Analysis

---

## 1. Overview
เอกสารนี้อธิบายกลไกการม็อดภาษาไทยของเกม **The Evil Within 2** อย่างละเอียดเชิงลึก เกมนี้สร้างด้วย **STEM Engine** ซึ่งพัฒนาต่อยอดมาจาก **id Tech 5** (โดย id Software → Tango Gameworks) ม็อดใช้วิธี **Asset Override ผ่านระบบ Patch Archive** ของเอนจิน

---

## 2. Technical Stack

| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | STEM Engine (Tango Gameworks) — สืบทอดจาก id Tech 5 |
| **Archive Format** | `.pkr` (Packer File — data chunks) + `.ptr` (Pointer Table — index/header) |
| **PKR Magic Bytes** | `83 11 BA FC` — Proprietary STEM Engine archive signature |
| **PTR Magic Bytes** | `46 57 DC FA` (`FW..`) / `35 57 DC FA` (`5W..`) — Pointer Table signature |
| **Compression** | zlib (ภายใน `.pkr` chunks) |
| **Text Format** | `.lanb` (Language Binary — ไฟล์ข้อความ binary ของ STEM Engine) |
| **Text Encoding** | UTF-8 (สำหรับข้อความที่ถูกแก้ไข) |
| **Localization Approach** | Patch Archive Override (แทนที่ `.pkr` + `.ptr` ของภาษาเฉพาะ) |

---

## 3. STEM Engine Archive Architecture

### 3.1 ระบบ Archive แบบ PKR/PTR
STEM Engine (สืบทอดจาก id Tech 5) ใช้ระบบ archive คู่:

```
ptr/
  ├── p1_loc_01.ptr    ←── Pointer Table: สารบัญชี้ตำแหน่ง (Offsets) ใน .pkr
  └── p1_loc_11.ptr    ←── Pointer Table สำหรับ loc_11

p1_loc_01.pkr          ←── Data Chunks: ข้อมูลจริง (ข้อความ, ฟอนต์, เสียง) บีบอัด zlib
p1_loc_11.pkr          ←── Data Chunks สำหรับ loc_11
```

- **`.pkr` (Packer File):** เก็บ asset ทุกประเภทที่เกี่ยวกับ localization (Textures, Models, เสียง, และที่สำคัญที่สุดคือ `.lanb`) โดยแบ่งข้อมูลเป็น Chunks ที่ถูกบีบอัดด้วย zlib เรียงต่อกัน
- **`.ptr` (Pointer File):** เก็บตาราง Header/Pointer ที่ชี้ไปยังตำแหน่ง Offset ของแต่ละ Chunk ภายใน `.pkr`

### 3.2 Binary Header ที่พบ

| ไฟล์ | Magic Bytes (Hex) | ASCII | ขนาด |
|---|---|---|---|
| `p1_loc_01.pkr` | `83 11 BA FC` | (Non-printable) | 3,353,450 bytes |
| `p1_loc_11.pkr` | `83 11 BA FC` | (Non-printable) | 3,358,539 bytes |
| `p1_loc_01.ptr` | `46 57 DC FA` | `FW..` | 1,528 bytes |
| `p1_loc_11.ptr` | `35 57 DC FA` | `5W..` | 1,532 bytes |

> **ข้อสังเกตสำคัญ:**
> - `.pkr` ทั้ง 2 ไฟล์ใช้ magic เดียวกัน (`83 11 BA FC`) — เป็น signature มาตรฐานของ STEM Engine
> - `.ptr` มี magic ต่างกันเล็กน้อย (`46 57` vs `35 57`) — byte แรกอาจเป็น version หรือ variant flag
> - ข้อมูลภายใน `.pkr` เป็น binary ที่ถูกบีบอัดเต็มรูปแบบ (ไม่มี plaintext ให้อ่านได้)

### 3.3 Integrity Check System
STEM Engine มีระบบตรวจสอบความถูกต้อง (Checksum / Offset Validation) ที่เข้มงวดมาก:
- หากแก้ไขไฟล์ `.pkr` แล้ว Offset ไม่ตรงกับที่บันทึกไว้ใน `.ptr` เกมจะ **Crash** ทันที
- ดังนั้น **ต้องสร้าง `.ptr` ใหม่ทุกครั้ง** ที่แก้ไขเนื้อหาใน `.pkr`

---

## 4. Naming Convention — ถอดรหัสชื่อไฟล์

| ส่วนของชื่อ | ความหมาย |
|---|---|
| `p1` | Patch Level 1 — ระบุว่าเป็น patch (ไม่ใช่ base archive) |
| `loc` | Localization — ระบุว่าเป็นไฟล์ภาษา |
| `01` | Language ID 01 — น่าจะเป็น **English** (ภาษาหลัก) |
| `11` | Language ID 11 — น่าจะเป็น **ภาษาอื่น** (เช่น Chinese/Japanese/Korean) |

> **การวิเคราะห์:** ผู้ทำม็อดน่าจะทับ Language Slot ที่มีอยู่ 2 ช่อง — ช่องภาษาอังกฤษ (`01`) และอีกช่องหนึ่ง (`11`) — เพื่อให้สามารถสลับระหว่างภาษาไทยกับภาษาเดิมได้ หรือเพื่อครอบคลุมข้อความทั้งหมดที่กระจายอยู่ใน 2 archive

---

## 5. ขั้นตอนที่ผู้ทำม็อดน่าจะใช้ (Reconstructed Pipeline)

### ขั้นตอนที่ 1: แตกไฟล์ (Unpacking)
```
ใช้ QuickBMS + สคริปต์ `the_evil_within_2.bms` (โดย aluigi)
หรือ Laura (Wraith Laura by DTZxPorter) เพื่อแตกไฟล์
    │
    ├── อ่าน p1_loc_xx.ptr เพื่อหาตำแหน่ง Chunks
    └── แตก p1_loc_xx.pkr เพื่อดึง .lanb และ asset อื่นๆ ออกมา
```

### ขั้นตอนที่ 2: แก้ไขข้อความและฟอนต์
```
แก้ไขไฟล์ .lanb (Language Binary):
    │
    ├── ถอดรหัส .lanb → พบข้อความ UTF-8
    ├── แปลข้อความจากอังกฤษเป็นไทย
    └── แก้ไข/เพิ่ม Font ที่รองรับ Unicode ภาษาไทย
        (ไฟล์ prefix `loc_` คือไฟล์ที่เก็บข้อมูลฟอนต์ Unicode)
```

### ขั้นตอนที่ 3: แพ็กกลับ (The Repacking Magic)
นี่คือขั้นตอนที่ยากที่สุดเพราะ STEM Engine ตรวจสอบ integrity อย่างเข้มงวด:

```
1. QuickBMS Reimport Script หรือ Custom Repacker
   → ใส่ข้อมูลที่แก้แล้วกลับเข้า .pkr
       │
2. Padding Manipulation
   → เติม Null bytes (00) หรือ Garbage bytes
     เพื่อให้ขนาด Chunk ตรงกับ Chunk เดิม
       │
3. Rebuilding PTR
   → สร้างไฟล์ .ptr ใหม่ทั้งหมด
     อัปเดต Offset ของทุก Chunk ให้ตรงกับ .pkr ใหม่
     ตรวจสอบ Checksum ให้ถูกต้อง
       │
4. วางไฟล์ .pkr + .ptr ทับไฟล์เดิมในโฟลเดอร์ patch ของเกม
```

> **คำเตือนสำคัญ:** หากแก้ไข `.pkr` แล้วไม่สร้าง `.ptr` ใหม่ เกมจะ Crash เพราะ Offset ไม่ตรง ระบบ Pointer Table ของ STEM Engine ตรวจสอบทั้ง File-system level (ขนาดไฟล์) และ Internal pointer logic (ตำแหน่ง Chunk ภายใน) พร้อมกัน

---

## 6. Required Tools for Modding

| เครื่องมือ | หน้าที่ |
|---|---|
| **QuickBMS** + `the_evil_within_2.bms` script | แตกไฟล์ `.pkr`/`.ptr` และ reimport |
| **Laura (Wraith Laura by DTZxPorter)** | Asset extractor เฉพาะ STEM Engine |
| **Hex Editor** (HxD, 010 Editor) | ตรวจสอบโครงสร้าง binary, padding, offset |
| **Text Editor** (VSCode, Notepad++) | แก้ไขข้อความ `.lanb` ที่ถูก dump ออกมา |
| **Custom Repacker** (เฉพาะ TEW2) | แพ็กไฟล์กลับ + สร้าง `.ptr` ใหม่ |
| **zlib Decompressor** | คลายการบีบอัด chunks ภายใน `.pkr` |

---

## 7. ความเชื่อมโยงกับเอนจินอื่นในตระกูล id Tech

| เอนจิน | เกม | Archive Format | ความเหมือน |
|---|---|---|---|
| **STEM Engine** | The Evil Within 1 & 2 | `.pkr` + `.ptr` | ตรงนี้ ← |
| **Void Engine** | Dishonored 2, Deathloop | `.resources` + `.index` | เหมือนกันในหลักการ (SER format) |
| **id Tech 5** | RAGE, Wolfenstein | `.resources` + `.index` | ต้นกำเนิดของระบบ |

ทั้งหมดใช้หลักการเดียวกัน: **แยกสารบัญ (Index/PTR) ออกจากข้อมูล (Data/PKR)** และมีระบบ integrity check ที่เข้มงวด

---

## 8. Conclusion
ม็อดภาษาไทยของ The Evil Within 2 ใช้วิธี **Patch Archive Override** ที่ต้องอาศัยความเข้าใจลึกซึ้งเกี่ยวกับโครงสร้าง `.pkr`/`.ptr` ของ STEM Engine ความยากหลักอยู่ที่:

1. **ระบบ Integrity Check** — ต้องสร้าง `.ptr` ใหม่ทุกครั้งที่แก้ไข `.pkr`
2. **Padding Manipulation** — ต้องจัดการ byte padding ให้ขนาด chunk ตรงกับเดิม
3. **zlib Compression** — ข้อมูลภายใน `.pkr` ถูกบีบอัด ต้องคลายก่อนแก้ไขแล้วบีบอัดกลับ

ม็อดนี้แก้ไข 2 language slots (`loc_01` และ `loc_11`) ซึ่งน่าจะเป็นการทับภาษาอังกฤษและอีกภาษาหนึ่งด้วยข้อความไทย
