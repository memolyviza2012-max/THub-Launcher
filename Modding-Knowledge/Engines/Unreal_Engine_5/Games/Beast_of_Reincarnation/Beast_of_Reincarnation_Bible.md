# Beast of Reincarnation — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

> **Generated:** 2026-09-13
> **Analyst:** Rivet Engineer Advanced (Antigravity AI)
> **Game:** Beast of Reincarnation (UE5 — รองรับ Steam + Xbox Game Pass)
> **Mod:** ThaiMod v1.1.1 — TH By Lung Dear
> **Status:** ✅ Complete (10/10 Mandatory Sections)

---

## 1. Overview

**Beast of Reincarnation** เป็นเกมที่ขับเคลื่อนด้วย **Unreal Engine 5** ม็อดภาษาไทยโดย **Lung Dear** แปลด้วยมือทั้งหมด **12,546 บรรทัด** (ไม่ใช้เครื่องแปล) รองรับทั้ง **Steam (Win64)** และ **Xbox Game Pass (WinGDK)** ซึ่งเป็น pattern ที่เคยเห็นใน Dawnwalker WinGDK

**Mod Architecture:** UE5 PAK Additive + dsound.dll DLL Proxy — เพิ่มไฟล์ใหม่ ไม่ทับไฟล์เกมเดิมแม้แต่ไฟล์เดียว

---

## 2. Technical Stack

| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Unreal Engine 5 |
| **Archive Format** | **UE5 PAK + UCAS + UTOC** (IoStore container) |
| **Text Format** | LocRes (ฝังใน PAK) |
| **Font** | ฝังใน PAK |
| **Platform** | **Steam (Win64)** + **Xbox Game Pass (WinGDK)** — dual platform! |
| **DLL Proxy** | **dsound.dll** — patch ในหน่วยความจำให้เกมโหลด mod PAK |
| **Lua Script** | **bitfix\bor.lua** — ตัวช่วยเสริม |
| **Install** | PyInstaller Setup .exe (41.9 MB) |
| **Mod Complexity** | ★★★☆☆ |

---

## 3. โครงสร้างไฟล์ (File Architecture)

### 3.1 ไฟล์ที่ม็อดเพิ่ม (ไม่ทับไฟล์เดิมเลย!)

```
BeastOfReincarnation\
├── Binaries\
│   ├── Win64\                          (Steam)
│   │   ├── dsound.dll                  ← DLL proxy (memory patching)
│   │   └── bitfix\bor.lua             ← Lua helper script
│   └── WinGDK\                         (Xbox Game Pass)
│       ├── dsound.dll                  ← DLL proxy (memory patching)
│       └── bitfix\bor.lua             ← Lua helper script
└── Content\Paks\
    ├── pakchunk0-Windows_P.pak         ← ฟอนต์ + คำแปล
    ├── pakchunk0-Windows_P.ucas        ← IoStore container data
    └── pakchunk0-Windows_P.utoc        ← IoStore table of contents
```

### 3.2 dsound.dll DLL Proxy Pattern

> **⚡ Key Finding:** Beast of Reincarnation ใช้ **dsound.dll proxy** — pattern เดียวกับ Atelier Ryza (dinput8.dll):
> - DLL โหลดตอนเกมเริ่ม → patch หน่วยความจำให้เกมยอมโหลด mod PAK
> - **ไม่แก้ไฟล์ executable บนดิสก์** — แก้เฉพาะในหน่วยความจำ
> - ถอนม็อดแค่ลบไฟล์ทิ้ง — เกมกลับเป็นปกติ
> - DLL proxy ต่างจาก Atelier ตรงที่ Ryza ใช้ dinput8.dll (DirectInput) ส่วนนี้ใช้ dsound.dll (DirectSound)

### 3.3 Dual Platform Support

ม็อดนี้ **รองรับ 2 แพลตฟอร์ม** ในชุดเดียวกัน:
- **Steam (Win64):** `Binaries\Win64\dsound.dll`
- **Xbox Game Pass (WinGDK):** `Binaries\WinGDK\dsound.dll`

เป็น pattern เดียวกับ Dawnwalker ที่เคยวิเคราะห์ (WinGDK = Xbox Game Development Kit build)

---

## 4. Font Analysis

ฟอนต์ไทยฝังอยู่ใน `pakchunk0-Windows_P.pak` — ไม่มีข้อมูลชื่อฟอนต์จาก README แต่จาก pattern ของ Lung Dear น่าจะเป็น Google Sans หรือ Sarabun family

---

## 5. Text Analysis

| รายการ | ค่า |
|---|---|
| **บรรทัดทั้งหมด** | **12,546** |
| **เนื้อหา** | ทั้งเกม — เมนู ไอเทม สกิล คัตซีน เควสต์ |
| **v1.1 additions** | +15 ข้อความใหม่ (รีเซ็ตทักษะ สกินคัตซีน ทิปส์ท่าผลิบาน) |
| **v1.1 fixes** | แก้สระ/วรรณยุกต์ซ้อนในคำ "ำ" — **325 จุด** |
| **Version Support** | เกม v1.0.11 |

### 5.1 UNKNOWN_LOCALIZE_KEY Pattern

README ระบุว่าถ้าเกมอัปเดตแล้วเพิ่มข้อความใหม่ จะขึ้น `UNKNOWN_LOCALIZE_KEY` — แสดงว่าเกมใช้ **key-based localization** ที่ถ้าหา key ไม่เจอในม็อดจะ fallback เป็น key name

---

## 6. Cross-Engine Comparison

| Feature | **Beast of Reincarnation** | **Dawnwalker** | **Atelier Ryza** |
|---|---|---|---|
| **Engine** | UE5 | UE5 | Gust Engine |
| **DLL Proxy** | **dsound.dll** | ❌ (native PAK) | **dinput8.dll** |
| **WinGDK** | ✅ | ✅ | ❌ |
| **Destructive** | ❌ (additive) | ❌ (PAK patching) | ❌ (DLL only) |

---

## 7. Pipeline

1. สร้างฟอนต์ไทย + แปล LocRes → pack เป็น UE5 PAK/UCAS/UTOC
2. สร้าง dsound.dll proxy ที่ patch memory ให้โหลด mod PAK
3. สร้าง bor.lua helper script
4. Package ทั้ง Win64 + WinGDK เป็น PyInstaller Setup .exe

---

## 8. Troubleshooting

| ปัญหา | วิธีแก้ |
|---|---|
| UNKNOWN_LOCALIZE_KEY | เกมอัปเดต → รอม็อดเวอร์ชันใหม่ |
| ภาษาไทยหาย | รัน installer ซ้ำ |
| Xbox Game Pass หาเกมไม่เจอ | ดูใน `XboxGames\Beast of Reincarnation\Content\` |

---

## 9. Required Tools

| เครื่องมือ | หน้าที่ |
|---|---|
| **Setup .exe** (PyInstaller) | ติดตั้ง/ถอน + auto-detect ทั้ง Steam/Game Pass |

---

## 10. Extracted Assets

ม็อดนี้เป็น **Setup .exe only** (41.9 MB) — ไฟล์ม็อดฝังภายใน installer