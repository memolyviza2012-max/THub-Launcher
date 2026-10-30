# Tom Clancy's Splinter Cell Blacklist — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

> **Generated:** 2026-09-16
> **Analyst:** Rivet Engineer Advanced (Antigravity AI)
> **Game:** Tom Clancy's Splinter Cell Blacklist (Ubisoft Toronto)
> **Mod:** ThaiMod v1.0 — By Lung Dear
> **Status:** ✅ Complete (10/10 Mandatory Sections)

---

## 1. Overview

**Tom Clancy's Splinter Cell Blacklist** เป็นเกม Stealth Action สร้างโดย **Ubisoft Toronto** ขับเคลื่อนด้วย **LEAD Engine** ม็อดภาษาไทยโดย **Lung Dear** ครอบคลุมเมนู HUD ภารกิจ คู่มือ ฐานข้อมูล ข่าวกรอง และซับไตเติลทั้งเกม ติดตั้งผ่าน Setup .exe ขนาด **247 MB** (ม็อดใหญ่ที่สุดใน KB!) เพราะมี **261 ไฟล์ UMD** อยู่ภายใน

**Mod Architecture:** UMD File Replacement — แทนไฟล์ UMD ทั้ง 261 ไฟล์ พร้อมสำรองต้นฉบับ

---

## 2. Technical Stack

| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | LEAD Engine (Ubisoft Toronto) |
| **Developer** | Ubisoft Toronto |
| **Archive Format** | **UMD** (Ubisoft Media Data) — format เฉพาะทางของ Ubisoft |
| **Files Modified** | **261 ไฟล์** — 1 loc + 1 font/UI + 259 subtitles |
| **Font** | ฟอนต์ไทยที่แก้ปัญหาสระ/วรรณยุกต์ซ้อน |
| **Translation** | **AI (Claude)** เขียนทีละบรรทัด — ไม่ใช้เครื่องแปลอัตโนมัติ |
| **Platform** | Ubisoft Connect (อาจใช้กับ Steam ได้ — ถ้าเวอร์ชันตรงกัน) |
| **Backup** | `_ThaiMod_Backup_Original\` (สำรอง 261 ไฟล์ต้นฉบับ) |
| **Install** | PyInstaller Setup .exe (**247 MB** — ใหญ่ที่สุดใน KB!) |
| **Mod Complexity** | ★★★☆☆ (ไฟล์เยอะ แต่ pattern เป็น file replacement ตรง ๆ) |

---

## 3. โครงสร้างไฟล์ (File Architecture)

### 3.1 ไฟล์ที่ม็อดแตะ (261 ไฟล์)

```
src\SYSTEM\
├── loc-int.umd           ← ข้อความ UI ทั้งหมด (เมนู HUD ภารกิจ ฯลฯ)
├── dynamicwin.umd        ← ฟอนต์ + การตั้งค่าหน้าจอ (ฟอนต์ไทยอยู่ที่นี่)
└── UMDs\
    └── *.umd (259 ไฟล์)  ← ซับไตเติลบทพูดของแต่ละด่าน/คัตซีน
```

### 3.2 UMD Format Pattern

ไฟล์ `.umd` (Ubisoft Media Data) เป็น format เฉพาะทางของ Ubisoft:
- **`loc-int.umd`** — Language localization ภาษาอังกฤษ (int = international/English)
- **`dynamicwin.umd`** — Dynamic content สำหรับ Windows platform (font + UI layout)
- **`UMDs/*.umd`** — Subtitle data แยกตามฉาก/ด่าน (259 ไฟล์ = แต่ละด่าน/คัตซีนมีไฟล์ของตัวเอง)

### 3.3 File Replacement Pattern

> **⚡ Key Finding:** ม็อดนี้ใช้วิธี **แทนไฟล์ทั้งตัว** (261 ไฟล์) ไม่ใช่ in-place patching:
> - เหตุผลคือ UMD format มีโครงสร้างที่เปลี่ยนขนาดได้ (ข้อความไทยยาวกว่า/สั้นกว่าอังกฤษ)
> - ต้นฉบับ 261 ไฟล์ถูกสำรองไว้ที่ `_ThaiMod_Backup_Original\`
> - Installer ขนาด **247 MB** เพราะต้องฝัง 261 ไฟล์ UMD ที่พร้อมใช้

### 3.4 Language Setting

> **⚠️ สำคัญ:** ต้องตั้งภาษาในเกมเป็น **English** — ม็อดแทนเฉพาะไฟล์ `loc-int` (English slot)
> ข้อความที่ฝังในรูปภาพ/วิดีโอจะยังเป็นภาษาอังกฤษ

---

## 4. Font Analysis

| รายการ | ค่า |
|---|---|
| **ตำแหน่ง** | `src\SYSTEM\dynamicwin.umd` |
| **คุณสมบัติ** | แก้ปัญหาสระ/วรรณยุกต์ซ้อน |

ฟอนต์ไทยฝังอยู่ใน `dynamicwin.umd` ซึ่งเป็นไฟล์ที่ควบคุมทั้งฟอนต์และ UI layout — pattern เฉพาะของ LEAD Engine ที่รวม font + UI config ไว้ในไฟล์เดียว

---

## 5. Text Analysis

| รายการ | ค่า |
|---|---|
| **ไฟล์ข้อความหลัก** | `loc-int.umd` (เมนู HUD ภารกิจ คู่มือ ฐานข้อมูล ข่าวกรอง) |
| **ไฟล์ซับไตเติล** | **259 ไฟล์** ใน `UMDs\` (แต่ละด่าน/คัตซีนแยกไฟล์) |
| **แปลโดย** | AI (Claude) เขียนทีละบรรทัด — ไม่ใช้เครื่องแปลอัตโนมัติ |
| **เนื้อหา** | ทั้งเกม — เมนู HUD ภารกิจ คู่มือ ฐานข้อมูล ข่าวกรอง ซับไตเติลทุกด่าน |

### 5.1 Translation Method — AI-Assisted Manual

> **📌 Pattern ใหม่:** ม็อดนี้เป็นม็อดแรกใน KB ที่ README ระบุว่าใช้ **AI (Claude) เขียนทีละบรรทัด** — ต่างจากม็อดเดิมของ Lung Dear ที่ "แปลด้วยมือทั้งเกม" (Dead Space, Plague Tale) หรือ "AI-assisted with human review" ของ Pompoko (Atelier Ryza)

---

## 6. Cross-Engine Comparison

| Feature | **Splinter Cell BL** | **Far Cry 2** | **DOOM: TDA** |
|---|---|---|---|
| **Engine** | **LEAD** (Ubisoft) | Dunia (Ubisoft) | id Tech 7 |
| **Format** | **UMD** | `.dat`/`.fat` | `.resources` |
| **Patch Method** | **File replacement** (261 files!) | File replacement | In-place |
| **File Count** | **261** | ~10 | 2 |
| **Installer Size** | **247 MB** (ใหญ่สุดใน KB!) | ~50 MB | 38 MB |
| **Ubisoft** | ✅ | ✅ | ❌ |

---

## 7. Pipeline

1. แกะ UMD format ของ LEAD Engine
2. แปลข้อความใน `loc-int.umd` (เมนู/UI) + 259 ไฟล์ subtitle ใน `UMDs\`
3. สร้างฟอนต์ไทย + ฝังใน `dynamicwin.umd`
4. สร้าง UMD ใหม่ทั้ง 261 ไฟล์
5. Package เป็น PyInstaller Setup .exe

---

## 8. Troubleshooting

| ปัญหา | สาเหตุ | วิธีแก้ |
|---|---|---|
| ยังเห็นภาษาอังกฤษ | ไม่ได้ตั้งภาษาเกมเป็น English | Settings → Language → English |
| ภาษาไทยหายหลังอัปเดต | เกมเขียนทับ UMD | รัน installer ซ้ำ |
| เกมผิดปกติหลังลงม็อด (Steam) | เวอร์ชันไม่ตรงกับ Ubisoft Connect | กดถอน → ใช้ Verify Integrity |
| ข้อความในรูป/วิดีโอยังเป็นอังกฤษ | ข้อความฝังใน media | ปกติ — แก้ไม่ได้ |

---

## 9. Required Tools

| เครื่องมือ | หน้าที่ |
|---|---|
| **Setup .exe** (PyInstaller, 247 MB) | ติดตั้ง/ถอน + auto-detect เกม |

---

## 10. Extracted Assets

ม็อดนี้เป็น **Setup .exe only** (247 MB) — ไฟล์ UMD ทั้ง 261 ไฟล์ฝังภายใน installer

---

## Appendix A: UMD (Ubisoft Media Data) Format

`.umd` เป็น format เฉพาะทางของ Ubisoft ที่ใช้ใน LEAD Engine:
- `loc-*.umd` — Localization data (loc-int = English, loc-fra = French, etc.)
- `dynamicwin.umd` — Dynamic content สำหรับ Windows (font + UI layout + platform-specific config)
- ไฟล์ subtitle แยกตามฉาก/ด่าน — ทำให้เกมโหลดเฉพาะ subtitle ที่ต้องใช้ในแต่ละด่านได้

## Appendix B: Lung Dear Translation Method Evolution

| ม็อด | วิธีแปล |
|---|---|
| Dead Space trilogy | แปลด้วยมือทั้งเกม (manual) |
| A Plague Tale Requiem | แปลด้วยมือทั้งเกม 18,728 บรรทัด |
| IfSunSets | แปลด้วยมือ 16,734 ข้อความ |
| Beast of Reincarnation | แปลด้วยมือ 12,546 บรรทัด |
| **Splinter Cell Blacklist** | **AI (Claude) เขียนทีละบรรทัด** ← ใหม่! |

---

*Splinter Cell Blacklist เป็นเกมแรกจาก LEAD Engine ใน KB*
*ม็อดที่มี installer ใหญ่ที่สุด (247 MB) และแตะไฟล์มากที่สุด (261 ไฟล์)*