# IfSunSets — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

> **Generated:** 2026-09-13
> **Analyst:** Rivet Engineer Advanced (Antigravity AI)
> **Game:** IfSunSets
> **Mod:** ThaiMod v1.0 — By Lung Dear
> **Status:** ✅ Complete (10/10 Mandatory Sections)

---

## 1. Overview

**IfSunSets** เป็นเกมที่ขับเคลื่อนด้วย **Unreal Engine 5** ม็อดภาษาไทยโดย **Lung Dear** แปลด้วยมือครบ **16,734 ข้อความ** จาก **57 ตารางข้อความ** ของเกม ใช้ฟอนต์ **IBM Plex Sans Thai Looped** (SIL OFL 1.1) พร้อม **พจนานุกรมตัดคำไทย** ให้ข้อความขึ้นบรรทัดใหม่ได้ถูกที่

**Mod Architecture:** UE5 PAK Additive (Non-destructive) + Japanese Language Slot Override

---

## 2. Technical Stack

| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Unreal Engine 5 |
| **Archive Format** | **UE5 PAK + UCAS + UTOC** (IoStore container) |
| **Language Slot** | **Japanese (日本語)** — ภาษาไทยอยู่ในช่อง Japanese |
| **Font** | **IBM Plex Sans Thai Looped** (© IBM Corp., SIL OFL 1.1) |
| **Word Breaking** | ✅ **พจนานุกรมตัดคำไทย** — ข้อความยาวขึ้นบรรทัดใหม่ได้ถูกที่ |
| **Destructive** | ❌ **ไม่ทับไฟล์เดิมเลย** — เพิ่ม 3 ไฟล์ใหม่เท่านั้น |
| **Install** | PyInstaller Setup .exe (42.5 MB) |
| **Mod Complexity** | ★★☆☆☆ (ติดตั้งง่าย แต่ต้องเปลี่ยนภาษาเกม) |

---

## 3. โครงสร้างไฟล์ (File Architecture)

### 3.1 ไฟล์ที่ม็อดเพิ่ม (3 ไฟล์ ~38 MB)

```
IFSS\Content\Paks\
├── pakchunkThai-Windows_P.pak     ← ฟอนต์ + คำแปล + พจนานุกรมตัดคำ
├── pakchunkThai-Windows_P.ucas    ← IoStore container data
└── pakchunkThai-Windows_P.utoc    ← IoStore table of contents
```

### 3.2 Language Slot: Japanese Override

> **⚠️ ขั้นตอนที่ขาดไม่ได้:** เข้าเกม → ตั้งค่า → ภาษา → เลือก **日本語 (Japanese)**
> - ม็อดใส่ข้อความไทยไว้ในช่อง Japanese (เกมไม่มี Thai slot)
> - ภาษาอื่นไม่ถูกแตะ สลับกลับได้ทุกเมื่อ
> - **Pattern เดียวกับ XCOM Chimera Squad** (ที่ใช้ Korean slot)

### 3.3 Non-Destructive Design

- **ไม่แก้/ไม่ทับไฟล์เกมเดิมแม้แต่ไฟล์เดียว** → ไม่มีโฟลเดอร์สำรอง
- ถอนม็อดแค่ลบ 3 ไฟล์ `pakchunkThai-Windows_P.*`
- UE5 โหลด PAK เพิ่มจาก `Paks/` directory โดยอัตโนมัติ

---

## 4. Font Analysis

### 4.1 IBM Plex Sans Thai Looped

| รายการ | ค่า |
|---|---|
| **ชื่อฟอนต์** | IBM Plex Sans Thai Looped |
| **License** | SIL Open Font License 1.1 (© IBM Corp.) |
| **ไฟล์ License** | OFL.txt (4.4 KB) แนบมากับม็อด |

ฟอนต์ IBM Plex Sans Thai Looped เป็นฟอนต์ไทยแบบ "หัวกลม" (looped style) ที่ IBM ออกแบบ — เหมาะกับ UI ที่ต้องการความอ่านง่ายบนหน้าจอ

### 4.2 Thai Word Breaking Dictionary

> **⚡ Key Finding:** ม็อดนี้มี **พจนานุกรมตัดคำไทย** ฝังอยู่ใน PAK — ทำให้ข้อความยาว ๆ ขึ้นบรรทัดใหม่ได้ถูกที่ (ตัดคำถูกตำแหน่ง) เป็นเทคนิคขั้นสูงที่ไม่ค่อยเห็นในม็อดทั่วไป ม็อดส่วนใหญ่ปล่อยให้เกมตัดตามตัวอักษร

---

## 5. Text Analysis

| รายการ | ค่า |
|---|---|
| **ข้อความทั้งหมด** | **16,734** |
| **ตารางข้อความ** | **57 ตาราง** |
| **เนื้อหา** | เมนู ไอเทม สิ่งก่อสร้าง มอนสเตอร์ บทสนทนา เควสต์ ต้นไม้สกิล คัมภีร์ ไดอารี่ ซับคัตซีน |
| **[DEV] entries** | คงไว้เป็นภาษาอังกฤษ (ข้อความทดสอบของ dev) |

---

## 6. Cross-Engine Comparison

| Feature | **IfSunSets** | **XCOM Chimera Squad** | **Beast of Reincarnation** |
|---|---|---|---|
| **Engine** | UE5 | UE3 | UE5 |
| **Language Slot** | **Japanese** override | **Korean** override | Direct |
| **Word Breaking** | ✅ **พจนานุกรมตัดคำ** | ❌ | ❌ |
| **DLL Proxy** | ❌ | ❌ | ✅ dsound.dll |
| **Destructive** | ❌ | ✅ (file copy) | ❌ |
| **Font License** | **SIL OFL** (IBM Plex) | — | — |

---

## 7. Pipeline

1. แปล LocRes 57 ตาราง (16,734 entries)
2. ฝังฟอนต์ IBM Plex Sans Thai Looped + พจนานุกรมตัดคำ
3. Pack เป็น UE5 PAK/UCAS/UTOC ชื่อ `pakchunkThai-Windows_P`
4. Package เป็น PyInstaller Setup .exe

---

## 8. Troubleshooting

| ปัญหา | สาเหตุ | วิธีแก้ |
|---|---|---|
| เกมยังเป็นภาษาอังกฤษ | ไม่ได้เปลี่ยนภาษาเกม | Settings → Language → **日本語** |
| บางข้อความเป็นอังกฤษ/เกาหลี | [DEV] entries หรือ hardcoded | ปกติ — แจ้ง Lung Dear ได้ |
| เกมเปิดไม่ขึ้นหลังอัปเดต | PAK compatibility issue | ถอนม็อดก่อน → รอม็อดใหม่ |

---

## 9. Required Tools

| เครื่องมือ | หน้าที่ |
|---|---|
| **Setup .exe** (PyInstaller) | ติดตั้ง/ถอน + auto-detect เกม |

---

## 10. Extracted Assets

ม็อดนี้เป็น **Setup .exe only** (42.5 MB) — ไฟล์ม็อดฝังภายใน installer
OFL.txt (SIL Open Font License) แนบมากับม็อดแยกต่างหาก