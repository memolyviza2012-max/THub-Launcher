# Digimon Story: Cyber Sleuth Complete Edition — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

> **Generated:** 2026-09-16
> **Analyst:** Rivet Engineer Advanced (Antigravity AI)
> **Game:** Digimon Story: Cyber Sleuth Complete Edition (Media.Vision / Bandai Namco)
> **Mod:** ModThai v1.2 — By EN0VA
> **Status:** ✅ Complete (10/10 Mandatory Sections)

---

## 1. Overview

**Digimon Story: Cyber Sleuth Complete Edition** เป็นเกม JRPG สร้างโดย **Media.Vision** ขับเคลื่อนด้วย **Media.Vision Engine** — เอนจินเดียวกับ **Digimon Story: Time Stranger** ที่มีอยู่ใน KB ม็อดภาษาไทย v1.2 โดย **EN0VA** ติดตั้งโดยแตก ZIP ทับไฟล์เกม + ใช้ custom .NET launcher เพื่อโหลดม็อด ผ่านการแก้ไขมา 3 เวอร์ชัน (แก้ crash ตอนบันทึก, แก้ข้อความยาวแสดงไม่ครบ)

**Mod Architecture:** MVGL File Replacement + Custom .NET Mod Loader — แทนไฟล์ MVGL + ใช้ launcher พิเศษ

---

## 2. Technical Stack

| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Media.Vision Engine (proprietary) |
| **Developer** | Media.Vision / Bandai Namco |
| **Archive Format** | **MVGL** (Media.Vision Game Library) |
| **DB Files** | `DSDBS.steam.mvgl` (140 MB) + `DSDBSP.steam.mvgl` (143 MB) — Database + Patch |
| **Media Files** | `M100-M104.mvgl` (original) + `MTH100-MTH104.mvgl` (Thai) |
| **Mod Loader** | **Custom .NET EXE** (`Digimon Story CS.exe`, 13.5 MB) |
| **Language Slot** | **English** — ต้องตั้งภาษาเกมเป็น English |
| **Version** | Game build 23932740, Mod v1.2 |
| **Modder** | **EN0VA** |
| **Mod Complexity** | ★★★★☆ (MVGL proprietary format + custom launcher) |

---

## 3. โครงสร้างไฟล์ (File Architecture)

### 3.1 ไฟล์ม็อดทั้งหมด

```
{GameFolder}\
├── app_digister\
│   └── Digimon Story CS.exe        ← .NET Mod Loader (13.5 MB)
├── resources\
│   ├── DSDBS.steam.mvgl             ← Database (140 MB)
│   ├── DSDBSP.steam.mvgl            ← Database Patch (143 MB)
│   └── media\
│       ├── M100.mvgl   (5.9 MB)    ← Original media
│       ├── M101.mvgl   (0.4 MB)
│       ├── M102.mvgl   (6.8 MB)
│       ├── M103.mvgl   (1.7 MB)
│       ├── M104.mvgl   (1.9 MB)
│       ├── MTH100.mvgl (2.3 MB)    ← Thai media (MTH = Media THai)
│       ├── MTH101.mvgl (2.1 MB)
│       ├── MTH102.mvgl (3.8 MB)
│       ├── MTH103.mvgl (2.1 MB)
│       └── MTH104.mvgl (2.2 MB)
└── วิธีติดตั้ง.txt
```

### 3.2 MVGL Naming Pattern

> **⚡ Key Finding:** ม็อดใช้ naming convention **MTH** = **M**edia **TH**ai:
> - `M100-M104` = ไฟล์ media ดั้งเดิม (น่าจะถูก replace ด้วยเวอร์ชันที่มีข้อความไทย)
> - `MTH100-MTH104` = ไฟล์ media ใหม่ที่มีข้อความไทย (ไฟล์เพิ่ม)
> - รวม **12 ไฟล์ MVGL** ถูกแก้/เพิ่ม + 1 launcher EXE

### 3.3 Custom .NET Mod Loader

> **📌 Pattern ใหม่:** ม็อดนี้ไม่ใช้ PyInstaller installer เหมือน Lung Dear แต่ใช้ **custom .NET executable** (`Digimon Story CS.exe`) เป็น mod loader:
> - ผู้เล่นต้องเปิด launcher นี้แทนที่จะเปิดเกมตรง ๆ
> - Launcher จัดการโหลดไฟล์ม็อด MVGL + จัดการ compatibility
> - ตรวจพบ DSCS/DigimonStory markers ใน binary — เป็น purpose-built loader

### 3.4 MVGL Magic Bytes

| Pattern | Header | ไฟล์ |
|---|---|---|
| DB type | `0C-92-8D-60` | DSDBS, DSDBSP |
| Media type A | `0E-82-9B-1E` | M100, M103, M104 |
| Media type B | `41-D7-CF-51` | M101, M102, MTH100-MTH104 |

> **เปรียบเทียบ Time Stranger:** Time Stranger ใช้ `MDB1` magic สำหรับ `app_text01.dx11.mvgl` — แต่ Cyber Sleuth ใช้ magic ต่างออกไป อาจเป็นคนละ version ของ MVGL format

---

## 4. Font Analysis

ฟอนต์ไทยฝังอยู่ภายในไฟล์ MVGL — จากข้อมูลของ Time Stranger Bible พบว่า Media.Vision engine เก็บฟอนต์ในรูปแบบ indexed `bin font\commonfont` resource ภายใน MVGL

---

## 5. Text Analysis

| รายการ | ค่า |
|---|---|
| **ภาษาที่ต้องใช้** | English (ม็อดทับข้อความ English) |
| **เวอร์ชันม็อด** | v1.2 |
| **v1.2 fixes** | แก้อาการเกมปิดขณะอ่านข้อความ + ข้อความยาวแสดงไม่ครบ |
| **v1.1 fixes** | แก้อาการเกมปิดเมื่อบันทึกเซฟ |
| **Text System** | MBE (Media.Vision Binary Entry) ภายใน MVGL |

### 5.1 Version History — Bug Fixes

ม็อดผ่านการแก้ไข critical bugs มา 2 ครั้ง:
1. **v1.1** — เกมปิดเมื่อบันทึกเซฟ (save corruption fix)
2. **v1.2** — เกมปิดขณะอ่านข้อความ + ข้อความยาวแสดงไม่ครบ

แสดงว่า MVGL format มีข้อจำกัดด้านขนาดข้อมูลที่ต้องระวัง — ข้อความไทยที่ยาวกว่าอังกฤษอาจทำให้ overflow หรือ crash ได้

---

## 6. Cross-Engine Comparison

| Feature | **Cyber Sleuth** | **Time Stranger** | **Atelier Ryza** |
|---|---|---|---|
| **Engine** | Media.Vision | Media.Vision | Gust Engine |
| **Format** | MVGL (multi-magic) | MVGL (MDB1) | Gust PAK v2 |
| **MVGL Magic** | `0C-92-8D-60` / `41-D7-CF-51` | `MDB1` | N/A |
| **Mod Loader** | ✅ **.NET EXE** | ❌ (file replace) | DLL Proxy (dinput8.dll) |
| **Modder** | **EN0VA** | — | Pompoko |
| **Install** | ZIP + launcher | — | DLL injection |

---

## 7. Pipeline

1. แกะ MVGL format ของ Media.Vision engine (Cyber Sleuth variant)
2. แปลข้อความใน MBE text/message entries
3. สร้างฟอนต์ไทย + ฝังใน MVGL
4. สร้าง MVGL ที่มี M files + MTH files
5. สร้าง .NET mod loader เพื่อจัดการโหลดม็อด
6. Package เป็น ZIP + README

---

## 8. Troubleshooting

| ปัญหา | สาเหตุ | วิธีแก้ |
|---|---|---|
| เกมยังเป็นภาษาอังกฤษ | ไม่ได้เปิดผ่าน launcher | ใช้ `app_digister\Digimon Story CS.exe` |
| ภาษาเกมไม่ใช่ English | ม็อดทับเฉพาะ English | Steam → Properties → Language → English |
| กลับเป็นไฟล์เดิม | — | Steam → Verify Integrity of Game Files |

---

## 9. Required Tools

| เครื่องมือ | หน้าที่ |
|---|---|
| **7-Zip / WinRAR** | แตก ZIP ม็อด |
| **Digimon Story CS.exe** (.NET launcher) | Mod loader — ต้องเปิดผ่านไฟล์นี้ |

---

## 10. Extracted Assets

ตำแหน่ง: `E:\Mod_Workspace\Modding-Knowledge\Engines\Media_Vision\Games\Digimon_Story_Cyber_Sleuth\`

ม็อดมีไฟล์ loose ที่วิเคราะห์ได้ (ไม่ใช่ installer) — รวม **14 ไฟล์**:
- MVGL archives: 12 ไฟล์ (DSDBS + DSDBSP + M100-M104 + MTH100-MTH104)
- .NET Launcher: 1 ไฟล์ (Digimon Story CS.exe)
- README: 1 ไฟล์

**หมายเหตุ:** ไฟล์ MVGL มีขนาดรวม ~320 MB — ไม่ได้ copy เข้า KB เพราะขนาดใหญ่เกินไป

---

## Appendix A: MVGL Format Variants (Cyber Sleuth vs Time Stranger)

| Feature | Cyber Sleuth | Time Stranger |
|---|---|---|
| **Platform suffix** | `.steam.mvgl` | `.dx11.mvgl` |
| **DB Magic** | `0C-92-8D-60` | `MDB1` (4D-44-42-31) |
| **Media Magic** | `0E-82-9B-1E` / `41-D7-CF-51` | `MDB1` |
| **Naming** | DSDBS/DSDBSP + M/MTH series | app_text01 + patch_text01 |

แม้จะเป็น Media.Vision engine เดียวกัน แต่ Cyber Sleuth ใช้ format version ที่แตกต่าง — Magic bytes ไม่ตรงกัน และ naming convention ต่างกัน (steam vs dx11 suffix)

---

*Digimon Story: Cyber Sleuth เป็นเกมที่ 2 จาก Media.Vision Engine ใน KB*
*ม็อดเดอร์ EN0VA — ม็อดเดอร์คนที่ 3 ใน KB (หลัง Lung Dear และ Pompoko)*