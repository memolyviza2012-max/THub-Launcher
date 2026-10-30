# Dead Space (2008) — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

> **Generated:** 2026-09-11
> **Analyst:** Rivet Engineer Advanced (Antigravity AI)
> **Game:** Dead Space (2008, EA Redwood Shores → Visceral Games)
> **Mod:** ThaiMod v1.0 Manual — Mod Thai By Lung Dear
> **Status:** ✅ Complete (10/10 Mandatory Sections)

---

## 1. Overview

**Dead Space** (2008) เป็น Survival Horror ผลงาน Visceral Games ใช้ **Visceral Engine** (Godfather Engine เวอร์ชันปรับปรุง) ม็อดภาษาไทยโดย **Lung Dear** แปลด้วยมือทั้งหมด **3,223 บรรทัด** (ไม่ใช้เครื่องแปล) ครอบคลุมเมนู บทสนทนา คัตซีน บันทึก และระบบทั้งหมด

**Mod Architecture:** Loose File Override — ก็อปโฟลเดอร์ `text_assets` ทับของเดิม

---

## 2. Technical Stack

| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Visceral Engine (EA Redwood Shores) |
| **Archive Format** | **STR/TOC** — Loose file system (ไม่ได้แพ็กใน archive ใหญ่) |
| **Text Format** | `.str` (String Resource) — Magic `33-73-6C-6F` ("3slo") |
| **Font** | ฟอนต์ **Sarabun Bold** อบใหม่ 9 ตัวฝังใน `text_assets_global.str` |
| **AES Encryption** | ❌ ไม่มี |
| **Language Slot** | English (ทั้ง root + `en/` subfolder) |
| **Install Method** | File copy (+ install.bat/sh auto-detect สำรองไฟล์เดิม) |
| **Platform Support** | Windows / Linux / Steam Deck / macOS |
| **Mod Complexity** | ★★☆☆☆ (ก็อปทับตรง ๆ ง่ายที่สุดในซีรีส์) |

---

## 3. โครงสร้างไฟล์ (File Architecture)

```
text_assets\                    ← ทั้งโฟลเดอร์นี้ก็อปทับของเกม
├── text\D8CBB618.str           (128 KB) ← ตารางข้อความที่แปลแล้ว
├── text_assets_global.str      (512 KB) ← ฟอนต์ไทย 9 ตัว
├── text_assets_global.toc      (2 KB)
├── en\text_assets_global.str   (512 KB) ← ฟอนต์ไทย (English slot)
└── en\text_assets_global.toc   (2 KB)
```

**Total mod size:** ~1.1 MB

---

## 4. Font Analysis

ฟอนต์ไทย **Sarabun Bold** ถูกอบ (bake) เข้าไปในไฟล์ `text_assets_global.str` ทั้ง 9 ขนาดที่เกมใช้ พร้อมแก้ตำแหน่ง **สระ-วรรณยุกต์ซ้อน** ให้ถูกต้อง

---

## 5. Text Analysis

| รายการ | ค่า |
|---|---|
| **บรรทัดทั้งหมด** | 3,223 |
| **เนื้อหา** | เมนู, ตัวเลือก, ปุ่มควบคุม, ร้านค้า, โต๊ะอัปเกรด, เนื้อเรื่อง 12 บท, บันทึกเสียง/ข้อความ, ป้ายในฉาก, ประกาศเสียง, คำบรรยายคัตซีน |
| **STR Magic** | `33-73-6C-6F` ("3slo") — format เดียวกันทั้ง trilogy |

---

## 6–10. (ดู Combined Bible ด้านล่าง)

*เอกสารนี้เป็นส่วนหนึ่งของ Dead Space Trilogy Bible*
*ดูเพิ่มเติม: [Dead Space 2](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Visceral_Engine/Games/Dead_Space_2/Thai_Localization_Bible.md) | [Dead Space 3](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Visceral_Engine/Games/Dead_Space_3/Thai_Localization_Bible.md)*

---

## 6. Cross-Engine Comparison (Trilogy)

| Feature | **DS1 (2008)** | **DS2** | **DS3** |
|---|---|---|---|
| **Archive** | Loose STR/TOC | **DAT** (monolithic) | **VIV** (bigfile) |
| **Install** | File copy | Python slot-patch | Python slot-patch + zlib |
| **Text** | 3,223 lines | 6,449 lines | 10,533 lines |
| **Fonts** | 9 (Sarabun Bold) | 4 (Sarabun SemiBold) | 7 |
| **DLC** | ❌ | ✅ (included) | ✅ Awakened (393 lines) |
| **Safety** | SHA-256 checksums | SHA-256 verify before write | SHA-256 verify before write |
| **Complexity** | ★★☆☆☆ | ★★★☆☆ | ★★★★☆ |

---

## 7. Pipeline

1. แก้ไขข้อความใน `.str` files (format "3slo")
2. อบฟอนต์ไทย Sarabun Bold ลงใน `text_assets_global.str` ทั้ง 9 ขนาด
3. ก็อปทั้งโฟลเดอร์ `text_assets` ทับของเกม

---

## 8. Troubleshooting

| ปัญหา | วิธีแก้ |
|---|---|
| ภาษาไทยหายหลังเกมอัปเดต | ก็อปทับใหม่ |
| ถอนม็อด | ใช้ uninstall.bat หรือ Steam Verify |

---

## 9. Required Tools

| เครื่องมือ | หน้าที่ |
|---|---|
| **install.bat / install.sh** | Auto-detect เกม + สำรอง + ก็อปทับ |

---

## 10. Extracted Assets

| ไฟล์ | ที่อยู่ใน KB |
|---|---|
| `install.bat` | `Assets\Packages\` |
| `checksums.txt` | `Assets\Packages\` |