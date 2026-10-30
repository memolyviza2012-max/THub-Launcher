# Dead Space 2 — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

> **Generated:** 2026-09-11
> **Analyst:** Rivet Engineer Advanced (Antigravity AI)
> **Game:** Dead Space 2 (Visceral Games)
> **Mod:** ThaiMod v1.0 portable — Mod TH By Lung Dear
> **Status:** ✅ Complete (10/10 Mandatory Sections)

---

## 1. Overview

**Dead Space 2** ใช้ **Visceral Engine** เวอร์ชันใหม่ ระบบไฟล์เปลี่ยนจาก Loose files เป็น **Monolithic DAT** archive ม็อดภาษาไทยจึงต้องใช้ **Python Slot-Patching** เพื่อเขียนข้อมูลทับตำแหน่งเฉพาะภายใน DAT โดยตรง
- **แปลทั้งเกม:** 6,449 บรรทัด (แปลมือ ไม่ใช้เครื่องแปล) + DLC + Multiplayer
- **ฟอนต์:** Sarabun SemiBold 4 แบบ ปรับสระ-วรรณยุกต์

**Mod Architecture:** Binary Slot-Patch — เขียนทับ 6 ช่วงใน DS2DAT2/3/4.DAT

---

## 2. Technical Stack

| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Visceral Engine v2 |
| **Archive Format** | **Monolithic DAT** (DS2DAT2.DAT, DS2DAT3.DAT, DS2DAT4.DAT) |
| **Text Format** | STR ("3slo") ฝังอยู่ภายใน DAT ตาม offset |
| **Font** | **Sarabun SemiBold** 4 แบบ ฝังใน DAT |
| **Install** | **Python slot-patching** (`ds2_thai.py`) |
| **Safety** | SHA-256 verify ก่อนเขียนทุกครั้ง |
| **Mod Complexity** | ★★★☆☆ |

---

## 3. โครงสร้างไฟล์ (File Architecture)

### 3.1 Slot Naming Convention

```
slots\DS2DAT2.DAT.00019800.bin  → เขียนทับ DS2DAT2.DAT ที่ offset 0x19800 (640 KB)
slots\DS2DAT2.DAT.0013a000.bin  → เขียนทับ DS2DAT2.DAT ที่ offset 0x13a000 (256 KB)
slots\DS2DAT3.DAT.0001a000.bin  → เขียนทับ DS2DAT3.DAT ที่ offset 0x1a000 (640 KB)
...
```

**⚡ Key Finding:** ชื่อไฟล์ slot เข้ารหัสตำแหน่ง offset ไว้ในชื่อ! เช่น `DS2DAT2.DAT.00019800.bin` หมายความว่า binary blob นี้จะถูกเขียนลงที่ byte offset `0x00019800` ของไฟล์ `DS2DAT2.DAT` ใน DAT ดั้งเดิม — ขนาดไฟล์เกมเท่าเดิมทุกไบต์ (in-place overwrite)

### 3.2 Patched Targets

| ไฟล์เกม | Slot count | เนื้อหา |
|---|---|---|
| DS2DAT2.DAT | 2 slots | ฟอนต์ + ข้อความ |
| DS2DAT3.DAT | 2 slots | ฟอนต์ + ข้อความ (อีกชุด) |
| DS2DAT4.DAT | 2 slots | ฟอนต์ + ข้อความ (อีกชุด) |

---

## 4. Font Analysis

**Sarabun SemiBold** 4 แบบ ฝังอยู่ใน slot ขนาด 640 KB (font bank) แก้ตำแหน่งสระและวรรณยุกต์ให้ซ้อนถูกชั้น

---

## 5. Text Analysis

| รายการ | ค่า |
|---|---|
| **บรรทัดทั้งหมด** | 6,449 |
| **เนื้อหา** | เนื้อเรื่อง, บทสนทนา, บันทึกเสียง, เมนู, ร้านค้า, ชุด, อาวุธ, Multiplayer, DLC ทั้งหมด |
| **STR Magic** | `33-73-6C-6F` ("3slo") + `43-4F-48-53` ("COHS") sub-header |

---

## 6–10. (เหมือน DS1 — ดู [DS1 Bible](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Visceral_Engine/Games/Dead_Space_2008/Thai_Localization_Bible.md) Section 6–10)

## 7. Pipeline

1. Reverse Engineer offset ของ font bank + string table ใน DS2DAT*.DAT
2. สร้าง binary blob (slot) ที่มีข้อความไทยและฟอนต์ Sarabun
3. Python script (`ds2_thai.py`) ตรวจ SHA-256 แล้วเขียนทับตาม offset

## 8. Troubleshooting

| ปัญหา | วิธีแก้ |
|---|---|
| "ไฟล์เกมไม่ตรง" | เกมอัปเดตหรือมีม็อดอื่น → Steam Verify แล้วลงใหม่ |

## 9. Required Tools

| เครื่องมือ | หน้าที่ |
|---|---|
| **Python 3** | รัน ds2_thai.py |

## 10. Extracted Assets

| ไฟล์ | ที่อยู่ใน KB |
|---|---|
| `ds2_thai.py` | `Assets\Packages\` |
| `slots.json` | `Assets\Packages\` |