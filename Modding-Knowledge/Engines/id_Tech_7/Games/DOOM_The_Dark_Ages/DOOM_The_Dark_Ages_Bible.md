# DOOM: The Dark Ages — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

> **Generated:** 2026-09-16
> **Analyst:** Rivet Engineer Advanced (Antigravity AI)
> **Game:** DOOM: The Dark Ages (id Software / Bethesda)
> **Mod:** ThaiMod v1.0 — Mod TH By Lung Dear
> **Status:** ✅ Complete (10/10 Mandatory Sections)

---

## 1. Overview

**DOOM: The Dark Ages** เป็นเกม First Person Shooter จาก **id Software** ขับเคลื่อนด้วย **id Tech 7** (เอนจินที่สร้างจาก id Tech 6/DOOM 2016 สาย) ม็อดภาษาไทยโดย **Lung Dear** ติดตั้งผ่าน Setup .exe ไฟล์เดียว (38.5 MB) รองรับ **Steam, Xbox Game Pass, และ Epic** ทดสอบกับเกม v1.12.60.0

**Mod Architecture:** id Tech Resources In-Place Patch — แก้เฉพาะส่วนภายในไฟล์ `.resources` โดยขนาดไฟล์ไม่เปลี่ยน + Atomic Rollback

---

## 2. Technical Stack

| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | id Tech 7 (id Software) |
| **Developer** | id Software / Bethesda |
| **Archive Format** | **`.resources`** — id Tech resource container |
| **Patched Files** | `base\common_patch1.resources` + `base\common_patch2.resources` |
| **Patch Method** | **In-place overwrite** (ขนาดไฟล์เท่าเดิมทุกไบต์) |
| **Font** | **Noto Sans Thai** (ดัดแปลง) — SIL Open Font License |
| **Version Lock** | ✅ เกม v1.12.60.0 — ตรวจก่อนเขียนทุกครั้ง |
| **Safety** | ✅ Pre-write verify + **Atomic rollback** (คืนค่าถ้าเขียนไม่สำเร็จ) |
| **Backup** | `base\ThaiMod_Backup\` (เฉพาะส่วนที่แก้ ไม่ก๊อปทั้งไฟล์) |
| **Platform** | **Steam + Xbox Game Pass + Epic** — 3 platforms! |
| **Install** | PyInstaller Setup .exe (38.5 MB) |
| **Mod Complexity** | ★★★★☆ (Resources format ซับซ้อน + in-place patching) |

---

## 3. โครงสร้างไฟล์ (File Architecture)

### 3.1 ไฟล์ที่ม็อดแตะ

```
base\
├── common_patch1.resources    ← แก้ส่วนภายใน (ขนาดไม่เปลี่ยน)
├── common_patch2.resources    ← แก้ส่วนภายใน (ขนาดไม่เปลี่ยน)
└── ThaiMod_Backup\            ← สำรองเฉพาะส่วนที่แก้
```

### 3.2 id Tech Resources In-Place Patching

> **⚡ Key Finding:** ม็อดเดอร์ใช้เทคนิค **in-place overwrite** ภายใน `.resources`:
> - **ขนาดไฟล์ไม่เปลี่ยน** — เขียนทับข้อมูลเดิมตรง offset เดิมเป๊ะ
> - **สำรองเฉพาะส่วนที่แก้** ไว้ใน `ThaiMod_Backup` (ไม่ก๊อปไฟล์ทั้ง GB)
> - **Atomic rollback** — ถ้าเขียนไม่สำเร็จกลางทาง (เช่นเกมยังเปิดอยู่) จะคืนค่าส่วนที่เขียนไปแล้วให้เองอัตโนมัติ
> - เทคนิคนี้คล้าย Dead Space 2 (slot patching) แต่ซับซ้อนกว่าเพราะมี rollback

### 3.3 Triple Platform Auto-Detect

ตัวติดตั้งรองรับ 3 แพลตฟอร์ม:
- **Steam** — `steamapps\common\DOOMTheDarkAges\`
- **Xbox Game Pass** — `XboxGames\DOOM- The Dark Ages\Content\`
- **Epic** — ตาม Epic Games install path

---

## 4. Font Analysis

| รายการ | ค่า |
|---|---|
| **ชื่อฟอนต์** | Noto Sans Thai (ดัดแปลง) |
| **License** | SIL Open Font License |
| **DOOM 1993 Mode** | ฟอนต์พิกเซลเล็กเกินใส่ไทย → ใช้ตัวอักษรปกติแทน (เลข HUD ยังเป็นพิกเซล) |

> **หมายเหตุ:** เกมมีโหมด DOOM 1993 retro ที่ HUD ใช้ฟอนต์พิกเซล — ม็อดเดอร์ตัดสินใจให้ข้อความแจ้งเตือนในโหมดนี้ใช้ฟอนต์ปกติแทน เพราะฟอนต์พิกเซลเล็กเกินจะใส่ตัวอักษรไทยได้

---

## 5. Text Analysis

| รายการ | ค่า |
|---|---|
| **เนื้อหา** | ทั้งเกม — เมนู บทสนทนา ซับไตเติล HUD ไอเทม |
| **ข้อความอังกฤษเหลือ** | ข้อความสำหรับโปรแกรมอ่านหน้าจอ (accessibility) + ข้อความเก่าที่เกมไม่แสดง |
| **Format** | ฝังอยู่ภายใน `.resources` archive |

---

## 6. Cross-Engine Comparison

| Feature | **DOOM: The Dark Ages** | **A Plague Tale Requiem** | **Dead Space 2** |
|---|---|---|---|
| **Engine** | **id Tech 7** | Asobo Engine | Visceral Engine |
| **Archive** | `.resources` | DPC | Monolithic DAT |
| **Patch Method** | **In-place overwrite** | Append + TOC rewrite | Slot overwrite |
| **File Size** | **ไม่เปลี่ยน** | +260 KB | ไม่เปลี่ยน |
| **Rollback** | ✅ **Atomic** | ✅ JSON state | ✅ SHA-256 verify |
| **Platforms** | **3** (Steam/Xbox/Epic) | 1 | 1 |
| **Complexity** | ★★★★☆ | ★★★★☆ | ★★★☆☆ |

---

## 7. Pipeline

1. Reverse Engineer `.resources` container format ของ id Tech 7
2. หาตำแหน่ง font data + string table ภายใน `common_patch1/2.resources`
3. สร้างฟอนต์ไทย Noto Sans Thai (ดัดแปลง) ใส่แทน font เดิม
4. แปลข้อความ → เขียนทับตำแหน่งเดิม (in-place, ขนาดเท่าเดิม)
5. สร้าง backup ของส่วนที่จะแก้ + ระบบ atomic rollback
6. Package เป็น PyInstaller Setup .exe พร้อม 3-platform auto-detect

---

## 8. Troubleshooting

| ปัญหา | สาเหตุ | วิธีแก้ |
|---|---|---|
| "เปิดไฟล์เพื่อเขียนไม่ได้" | เกมยังเปิดอยู่ | ปิดเกมก่อน |
| "เวอร์ชันไม่ตรง" | เกมอัปเดตแล้ว | ถอนม็อดก่อน → รอม็อดใหม่ |
| ภาษาไทยหายหลังอัปเดต | เกมเขียนทับ `.resources` | ถอนก่อน → ลองติดตั้งใหม่ |
| ข้อความ HUD โหมด 1993 ไม่เป็นพิกเซล | ตั้งใจ — ฟอนต์พิกเซลใส่ไทยไม่ได้ | ปกติ |
| บางข้อความยังเป็นอังกฤษ | Accessibility text / unused text | ปกติ |

---

## 9. Required Tools

| เครื่องมือ | หน้าที่ |
|---|---|
| **Setup .exe** (PyInstaller) | ติดตั้ง/ถอน + auto-detect 3 platforms |

---

## 10. Extracted Assets

ม็อดนี้เป็น **Setup .exe only** (38.5 MB) — ไฟล์ม็อดฝังภายใน installer

---

## Appendix A: id Tech 7 Resources Format

id Tech 7 ใช้ไฟล์ `.resources` เป็น container หลักสำหรับเก็บ assets ทั้งหมดของเกม:
- **`common_patch1.resources`** และ **`common_patch2.resources`** เป็น patch files ที่เกมโหลดทับ base resources
- Format เป็น proprietary ของ id Software — ไม่ใช่ ZIP หรือ format มาตรฐาน
- ม็อดเดอร์ต้อง reverse engineer ตำแหน่ง entry ภายใน resources เพื่อเขียนทับ
- เทคนิค "in-place" ต้องการให้ข้อมูลใหม่มีขนาดพอดีกับช่องเดิม — เป็นข้อจำกัดสำคัญของ id Tech modding

---

*DOOM: The Dark Ages เป็นเกมแรกจาก id Tech 7 ใน KB*
*ฟอนต์ดัดแปลงจาก Noto Sans Thai (SIL Open Font License)*