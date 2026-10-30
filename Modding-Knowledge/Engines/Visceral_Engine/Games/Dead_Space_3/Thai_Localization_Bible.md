# Dead Space 3 + Awakened — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

> **Generated:** 2026-09-11
> **Analyst:** Rivet Engineer Advanced (Antigravity AI)
> **Game:** Dead Space 3 + DLC Awakened (Visceral Games)
> **Mod:** ThaiMod Manual — Mod Thai By Lung Dear
> **Status:** ✅ Complete (10/10 Mandatory Sections)

---

## 1. Overview

**Dead Space 3** ใช้ **Visceral Engine** เวอร์ชันสุดท้าย ระบบไฟล์เปลี่ยนเป็น **VIV Archive** (bigfile) ม็อดภาษาไทยใช้ **Python slot-patching + zlib compression** พร้อม manifest.json ที่ระบุ offset/size/SHA-256 ละเอียดทุกจุด
- **เกมหลัก:** 10,140 บรรทัด (แปลมือทั้งหมด)
- **DLC Awakened:** 393 บรรทัด
- **ฟอนต์:** 7 แบบ ปรับสระ-วรรณยุกต์

**Mod Architecture:** VIV Slot-Patch + zlib — เขียนทับ 6 ช่วงใน 2 ไฟล์ VIV

---

## 2. Technical Stack

| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Visceral Engine v3 |
| **Archive Format** | **VIV** (bigfile4.viv + map_epilogue.viv) |
| **Slot Storage** | **Zlib compressed** (`.z`) — decompress ก่อนเขียนลง VIV |
| **Manifest** | **manifest.json** (ระบุ file, entry, offset, size, orig/mod SHA-256) |
| **Install** | **Python 3.8+** (`install.py`) |
| **Safety** | SHA-256 verify ทั้ง original และ mod state |
| **Mod Complexity** | ★★★★☆ (ซับซ้อนที่สุดในซีรีส์) |

---

## 3. โครงสร้างไฟล์ (File Architecture)

### 3.1 Manifest-Driven Patching

```json
{
  "file": "bigfile4.viv",
  "entry": 167,
  "offset": 2032629760,
  "size": 786432,
  "blob": "base_167.z",
  "orig_sha256": "4aa5f9c0...",
  "mod_sha256": "c3b5a162..."
}
```

**⚡ Key Finding:** DS3 ใช้ระบบ manifest ที่ sophisticated ที่สุดในทั้ง 3 ภาค:
- **Dual SHA-256:** ตรวจทั้ง `orig_sha256` (ไฟล์ต้นฉบับ) และ `mod_sha256` (ม็อดที่ลงแล้ว)
- **Zlib compression:** slot files บีบอัดด้วย zlib เพื่อลดขนาด download
- **VIV Entry Index:** ระบุ entry number ภายใน VIV archive ไม่ใช่แค่ offset

### 3.2 Patched Targets

| ไฟล์ VIV | Entries | เนื้อหา |
|---|---|---|
| `bigfile4.viv` | 167, 410 | เกมหลัก (ฟอนต์ + ข้อความ) |
| `dlc/map_epilogue/map_epilogue.viv` | 29, 64, 255, 650 | DLC Awakened |

Entry 650 ใน DLC มีขนาด **10.5 MB** (ใหญ่สุด — น่าจะเป็น font bank + texture)

---

## 4. Font Analysis

ฟอนต์ไทย **7 แบบ** ฝังอยู่ใน VIV slot (ชื่อฟอนต์ไม่ระบุใน README แต่จาก pattern ของซีรีส์น่าจะเป็น Sarabun family)

---

## 5. Text Analysis

| รายการ | ค่า |
|---|---|
| **เกมหลัก** | 10,140 บรรทัด |
| **DLC Awakened** | 393 บรรทัด |
| **รวม** | **10,533** บรรทัด |
| **เนื้อหา** | บทพูด ซับไตเติล เมนู ไอเทม อาวุธ บันทึกเสียง/ข้อความ ภารกิจ คำอธิบายทุกอย่าง |

---

## 6. Cross-Engine Comparison (Trilogy Evolution)

| Feature | **DS1** | **DS2** | **DS3** |
|---|---|---|---|
| **Year** | 2008 | 2011 | 2013 |
| **Archive** | Loose STR/TOC | Monolithic DAT | VIV (bigfile) |
| **Patch Method** | File copy | Offset-based binary slot | Manifest + zlib slot |
| **SHA Verify** | Checksum file | Pre-write verify | **Dual SHA (orig + mod)** |
| **Text Lines** | 3,223 | 6,449 | **10,533** |
| **Fonts** | 9 Sarabun Bold | 4 Sarabun SemiBold | 7 |
| **DLC** | ❌ | ✅ included | ✅ **Awakened** separate VIV |
| **Co-op** | ❌ | ❌ | ✅ ใช้ได้ปกติ |
| **Complexity** | ★★☆☆☆ | ★★★☆☆ | ★★★★☆ |

---

## 7. Pipeline

1. Unpack VIV entry ที่ต้องการ (กำหนดโดย entry number ใน manifest)
2. แก้ข้อความ/ฟอนต์ภายใน entry
3. Repack เป็น binary blob → บีบอัดด้วย zlib → บันทึกเป็น `.z`
4. สร้าง manifest.json ใหม่ พร้อม SHA-256 ของ orig และ mod

## 8. Troubleshooting

| ปัญหา | วิธีแก้ |
|---|---|
| "ไฟล์เกมไม่ตรงกับรุ่นที่ม็อดทำไว้" | เกมคนละรุ่น → รอม็อดรองรับ |
| ภาษาไทยหายหลังอัปเดต | รัน install ซ้ำ |

## 9. Required Tools

| เครื่องมือ | หน้าที่ |
|---|---|
| **Python 3.8+** | รัน install.py |

## 10. Extracted Assets

| ไฟล์ | ที่อยู่ใน KB |
|---|---|
| `install.py` | `Assets\Packages\` |
| `manifest.json` | `Assets\Packages\` |