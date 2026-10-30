# A Plague Tale: Requiem — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

> **Generated:** 2026-09-13
> **Analyst:** Rivet Engineer Advanced (Antigravity AI)
> **Game:** A Plague Tale: Requiem (Asobo Studio / Focus Entertainment)
> **Mod:** ThaiMod v1.0 — Mod Thai By Lung Dear
> **Status:** ✅ Complete (10/10 Mandatory Sections)

---

## 1. Overview

**A Plague Tale: Requiem** เป็นเกม Action-Adventure สร้างโดย **Asobo Studio** ขับเคลื่อนด้วย **Asobo Engine** (เอนจินเฉพาะทาง) ม็อดภาษาไทยโดย **Lung Dear** แปลด้วยมือทั้งหมด **18,728 บรรทัด** (ไม่ใช้เครื่องแปล) ติดตั้งผ่าน **Setup .exe** ไฟล์เดียวขนาด 32.6 MB

**Mod Architecture:** DPC Archive Append + TRTEXT Replace — ต่อฟอนต์ไทยท้ายไฟล์ DPC (ไม่ทับข้อมูลเดิม) + แทนไฟล์ข้อความ

---

## 2. Technical Stack

| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Asobo Engine (proprietary) |
| **Developer** | Asobo Studio |
| **Archive Format** | **DPC** (Data Pack Container) — format เฉพาะทางของ Asobo |
| **Text Format** | **TRTEXT** (`.pc` extension) — Translation Text ไฟล์เฉพาะทาง |
| **Font** | **Google Sans** ปรับสระ-วรรณยุกต์ตามตำแหน่งจริงของฟอนต์ |
| **Version Lock** | ✅ เกม v1.6.0.0 (ตรวจขนาด UPDATED1.DPC = 2,576,292,384 bytes) |
| **Safety** | ตรวจเวอร์ชันก่อนติดตั้ง + JSON state file สำหรับ uninstall |
| **Install** | PyInstaller Setup .exe (32.6 MB) |
| **Mod Complexity** | ★★★★☆ (DPC format ซับซ้อน + append technique) |

---

## 3. โครงสร้างไฟล์ (File Architecture)

### 3.1 ไฟล์ที่ม็อดแตะ (2 ไฟล์เท่านั้น!)

```
UPDATE\UPDATED1.DPC    (2.5 GB) → ต่อฟอนต์ไทย 260 KB ท้ายไฟล์
                                   ชี้สารบัญ 15 รายการไปหาฟอนต์ใหม่
                                   ข้อมูลเดิม 2.5 GB ไม่ถูกแตะแม้แต่ไบต์
TRTEXT\tt01.pc         → แทนทั้งไฟล์ด้วยข้อความแปลไทย
                         ต้นฉบับสำรองที่ _ThaiMod_Backup_Original\TRTEXT_tt01.pc
```

### 3.2 DPC Append Technique

> **⚡ Key Finding:** ม็อดเดอร์ใช้เทคนิค **"Append"** ที่ brilliant:
> - **ไม่ทับ** ข้อมูลเดิม 2.5 GB ใน DPC
> - **ต่อ** ฟอนต์ไทย 260 KB ไว้ท้ายไฟล์
> - **แก้สารบัญ** (index/TOC) 15 รายการให้ชี้ไปยังฟอนต์ใหม่
> - **บันทึกค่าเดิม** ไว้ที่ `UPDATE\aptr_thai_mod.json` สำหรับ uninstall
> - ผลลัพธ์: ไฟล์ DPC ใหญ่ขึ้นแค่ 260 KB ไม่ต้องก๊อปสำรอง 2.5 GB!

---

## 4. Font Analysis

- **ฟอนต์:** Google Sans
- **ปรับแต่ง:** สระ-วรรณยุกต์ตามตำแหน่งจริงของ font metrics
- **ขนาดที่เพิ่ม:** ~260 KB (ต่อท้าย DPC)
- **จำนวน entry ที่ชี้:** 15 รายการในสารบัญ DPC

---

## 5. Text Analysis

| รายการ | ค่า |
|---|---|
| **บรรทัดทั้งหมด** | **18,728** |
| **Format** | TRTEXT (`.pc` extension) — format เฉพาะทางของ Asobo |
| **เนื้อหา** | เนื้อเรื่อง บทสนทนา เมนู ไอเทม ทั้งเกม |
| **แปลโดย** | Lung Dear (แปลมือ ไม่ใช้เครื่องแปล) |

---

## 6. Cross-Engine Comparison

| Feature | **A Plague Tale Requiem** | **Dead Space 3** | **KCD II** |
|---|---|---|---|
| **Engine** | **Asobo Engine** | Visceral Engine | CryEngine |
| **Archive** | **DPC** (proprietary) | VIV (bigfile) | CryPAK (ZIP) |
| **Patch Method** | **Append + TOC rewrite** | Slot overwrite | Mod directory |
| **Backup Size** | ~0 (JSON state only!) | ~13 MB | 0 (non-destructive) |
| **Complexity** | ★★★★☆ | ★★★★☆ | ★★☆☆☆ |

---

## 7. Pipeline

1. วิเคราะห์โครงสร้าง DPC archive — หาตำแหน่ง TOC entries ที่ชี้ไปยัง font data
2. สร้างฟอนต์ไทย (Google Sans + ปรับ glyph positioning)
3. ต่อฟอนต์ท้าย DPC + แก้ TOC entries 15 จุดให้ชี้ไป offset ใหม่
4. แปลข้อความใน TRTEXT format → สร้างไฟล์ `tt01.pc` ใหม่
5. Package เป็น PyInstaller Setup .exe

---

## 8. Troubleshooting

| ปัญหา | สาเหตุ | วิธีแก้ |
|---|---|---|
| "เปิด UPDATED1.DPC ไม่ได้" | เกมเปิดอยู่ | ปิดเกมก่อน |
| "เวอร์ชันเกมไม่ตรง" | ไม่ใช่ v1.6.0.0 | Steam Verify + รอม็อดรุ่นใหม่ |
| "เขียนไม่ได้" | ไม่ได้ Run as Admin | คลิกขวา → Run as administrator |

---

## 9. Required Tools

| เครื่องมือ | หน้าที่ |
|---|---|
| **Setup .exe** (PyInstaller) | ติดตั้ง/ถอนม็อด + auto-detect เกม |

---

## 10. Extracted Assets

ม็อดนี้เป็น **Setup .exe only** (32.6 MB) — ไฟล์ม็อดฝังอยู่ภายใน installer
ไม่มีไฟล์แยกให้ extract โดยตรง