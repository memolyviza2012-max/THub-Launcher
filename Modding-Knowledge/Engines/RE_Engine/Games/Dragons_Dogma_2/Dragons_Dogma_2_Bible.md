# Dragon's Dogma 2 — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

> **Generated:** 2026-09-16
> **Analyst:** Rivet Engineer Advanced (Antigravity AI)
> **Game:** Dragon's Dogma 2 (Capcom)
> **Mod:** DD2 Thai Translation v1.1.5 — Copy-Paste Edition
> **Status:** ✅ Complete (10/10 Mandatory Sections)

---

## 1. Overview

**Dragon's Dogma 2** เป็นเกม Action RPG จาก **Capcom** ขับเคลื่อนด้วย **RE Engine** — เอนจินเดียวกับ Resident Evil series ที่มีอยู่ใน KB หลายเกม ม็อดภาษาไทย v1.1.5 ครอบคลุม **39,107 ข้อความ** (**มากที่สุดที่เคยเจอใน KB!**) กระจายใน **795 ไฟล์** ใช้ **REFramework** (dinput8.dll) + **LooseFileLoader** เพื่อโหลดไฟล์ม็อดโดยไม่ต้องแก้ PAK ของเกมเลย

**Mod Architecture:** RE Engine LooseFile Override via REFramework — Non-destructive

---

## 2. Technical Stack

| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | RE Engine (Capcom) |
| **Developer** | Capcom |
| **File Format** | `.msg.24` (RE Engine message binary) + `.oft.1` (RE Engine font) |
| **Files** | **795 ไฟล์** (778 text + 17 font aliases) |
| **Translation Count** | **39,107 ข้อความ** (สูงสุดใน KB!) |
| **Mod Loader** | **REFramework** (`dinput8.dll`, 22 MB, nightly #01417) |
| **Font** | **TH Sarabun New** — PreShaped Thai clusters (GNU GPL v2+) |
| **Thai Clusters** | **580** pre-shaped cluster combinations |
| **Font Aliases** | **17 UI aliases** — ฟอนต์เดียวทับทุกชื่อฟอนต์ของเกม |
| **Destructive** | ❌ **ไม่ทับไฟล์เดิมเลย** (LooseFile override) |
| **Install** | **Copy-Paste** — แตก ZIP แล้วก๊อปลงโฟลเดอร์เกม |
| **SHA-256 Manifest** | ✅ `payload-manifest.json` (ทุกไฟล์มี hash) |
| **Mod Complexity** | ★★★★★ (795 ไฟล์ + PreShaped font + cluster mapping + REFramework) |

---

## 3. โครงสร้างไฟล์ (File Architecture)

### 3.1 ไฟล์ที่ม็อดเพิ่ม (3 รายการ ก๊อปลงโฟลเดอร์ DD2.exe)

```
{GameFolder}\
├── dinput8.dll              ← REFramework (22 MB) — DLL proxy
├── re2_fw_config.txt        ← LooseFileLoader_Enabled=true
└── natives\stm\             ← LooseFile override directory
    ├── appdata\             ← 16 ไฟล์ (DLC/extra content)
    │   └── extracontents\*.msg.24
    ├── gui\ui01\font\       ← 17 ไฟล์ font aliases
    │   ├── akhbarlight.oft.1
    │   ├── BO-CinemaLetterStd-Light.oft.1
    │   ├── BO-UDReiminHangul-Medium.oft.1
    │   ├── ... (ทั้ง 17 ชื่อ → ไฟล์เดียวกัน 504 KB)
    │   └── msunghk-medium.oft.1
    └── message\             ← 762 ไฟล์ข้อความ
        ├── cutscene\*.msg.24     (35 คัตซีน)
        ├── dev1term\*.msg.24     (16 เมนู/UI)
        ├── enemy\*.msg.24        (2 ข้อมูลศัตรู)
        ├── gimmick\*.msg.24      (1)
        ├── npc\*.msg.24          (584 NPC dialogs!)
        ├── questlog\*.msg.24     (73 quest logs)
        └── ui\*.msg.24           (51 UI/HUD)
```

### 3.2 REFramework LooseFile Override Pattern

> **⚡ Key Finding:** นี่คือ pattern ที่ **สะอาดที่สุด** สำหรับ RE Engine modding:
> - `dinput8.dll` (REFramework) inject ตัวเองเข้าเกมตอน startup
> - `re2_fw_config.txt` เปิด `LooseFileLoader_Enabled=true`
> - REFramework จะโหลดไฟล์จาก `natives\` ก่อน PAK — ไฟล์ loose override ไฟล์ใน PAK
> - **ไม่แตะ PAK เลย** → ถอนแค่ลบ 3 รายการ (dinput8.dll, config, natives)
> - Pattern เดียวกับที่ RE Engine modding community ใช้ทั่วโลก
> - เทียบกับ Dragon's Dogma: Dark Arisen (MT Framework) ที่ต้องแก้ .arc archives

### 3.3 Compatibility Note

> **⚠️ สำคัญ:** ถ้าเคยลงม็อดอื่นที่ใช้ REFramework อยู่แล้ว **อย่าทับ dinput8.dll**
> แค่เปิด `LooseFileLoader_Enabled=true` ใน config เดิม แล้วก๊อปเฉพาะ `natives\`

---

## 4. Font Analysis

### 4.1 TH Sarabun New — PreShaped Thai Clusters

| รายการ | ค่า |
|---|---|
| **ชื่อฟอนต์** | TH Sarabun New Regular (ดัดแปลง) |
| **License** | GNU GPL v2 or later + font embedding exception |
| **ขนาด** | 504 KB (`.oft.1` RE Engine font format) |
| **Thai Clusters** | **580 combinations** pre-shaped |
| **Source files** | THSarabunNew.ttf (ต้นฉบับ), THSarabunNew-DD2-PreShaped.ttf (ดัดแปลง) |
| **Build script** | `build_sarabun_installer.py` |
| **Cluster map** | `thai-cluster-mapping.json` |

### 4.2 PreShaped Thai Cluster Technique

> **🔬 เทคนิคขั้นสูง:** ม็อดนี้ใช้ **PreShaped Thai Clusters** — แทนที่จะให้เกม render สระ/วรรณยุกต์ซ้อนทับ พยัญชนะแบบ real-time (ซึ่งมักผิดพลาด):
> 1. สร้างรูปอักขระผสมไว้ล่วงหน้า (**580 combinations** เช่น กา กิ กี กึ กุ กู กำ ...)
> 2. Map แต่ละ cluster ไปยัง glyph ใน font (ผ่าน `thai-cluster-mapping.json`)
> 3. ข้อความไทยใน `.msg.24` ใช้ code ของ cluster แทนอักขระเดี่ยว
> 4. ผลลัพธ์: สระลอย/วรรณยุกต์วางตำแหน่งถูกเป๊ะ 100% ทุกกรณี

### 4.3 17 Font Aliases Pattern

ฟอนต์ทั้ง 17 ไฟล์ใน `gui\ui01\font\` มี **SHA-256 เดียวกันทุกตัว** (`99F88A6B...`):
- เกมใช้ฟอนต์หลายชื่อ (akhbarlight, Galant, FRANCR, fzkt, msunghk, BO-*, cap-*, fot-*, fotk-*)
- ม็อดทับ**ทุกชื่อ**ด้วยฟอนต์ TH Sarabun New PreShaped ตัวเดียว
- ทำให้ข้อความไทยแสดงผลถูกต้องไม่ว่าเกมจะเรียกฟอนต์ตัวไหน

---

## 5. Text Analysis

| รายการ | ค่า |
|---|---|
| **ข้อความทั้งหมด** | **39,107** (มากที่สุดใน KB!) |
| **ไฟล์ข้อความ** | **778 ไฟล์** `.msg.24` |
| **ไฟล์ NPC** | **584 ไฟล์** (มากที่สุด — NPC dialogues หลายเฟส) |
| **ไฟล์ UI** | **51 ไฟล์** (เมนู ไอเทม อาวุธ สกิล ฯลฯ) |
| **ไฟล์เควสต์** | **73 ไฟล์** (quest logs) |
| **ไฟล์คัตซีน** | **35 ไฟล์** |
| **ไฟล์ใหญ่สุด** | `itemdetail.msg.24` (2,284 KB — รายละเอียดไอเทม) |

### 5.1 NPC Phased Dialog System

ม็อดมีไฟล์ NPC แยกเป็นเฟส `commonnpc001` → `commonnpc007` (7 เฟส):
- แต่ละเฟสมี 10+ ไฟล์ย่อย (`_00` ถึง `_10`)
- `*_10.msg.24` ไฟล์ใหญ่สุดของแต่ละเฟส (150-360 KB) — เป็น main dialog
- ระบบนี้สะท้อนว่า DD2 เปลี่ยนบทพูด NPC ตามความก้าวหน้าของเรื่อง

---

## 6. Cross-Engine Comparison (RE Engine Games in KB)

| Feature | **DD2** | **RE 4 Remake** | **RE 9** | **DD: Dark Arisen** |
|---|---|---|---|---|
| **Engine** | RE Engine | RE Engine | RE Engine | **MT Framework** |
| **Mod Method** | **REFramework LooseFile** | PAK mod | PAK mod | .arc replacement |
| **Files** | **795** | ~20 | ~30 | ~50 |
| **Text Count** | **39,107** | ~8,000 | ~15,000 | ~10,000 |
| **Font Aliases** | **17** | 1-3 | 1-3 | 1 |
| **PreShaped** | ✅ **580 clusters** | ❌ | ❌ | ❌ |
| **Destructive** | ❌ | ✅ | ✅ | ✅ |
| **Complexity** | ★★★★★ | ★★★☆☆ | ★★★★☆ | ★★★★★ |

---

## 7. Pipeline

1. แกะ `.msg.24` binary format ของ RE Engine
2. แปล 39,107 ข้อความ (778 ไฟล์)
3. สร้าง TH Sarabun New PreShaped font ด้วย `build_sarabun_installer.py`:
   - วิเคราะห์ข้อความไทยทั้งหมด → สกัด 580 Thai clusters
   - สร้าง pre-shaped glyphs ใน font
   - สร้าง `thai-cluster-mapping.json`
4. สร้าง `.oft.1` จาก TTF + ทับ 17 font aliases ด้วยไฟล์เดียวกัน
5. เขียน `payload-manifest.json` พร้อม SHA-256 ทุกไฟล์
6. Package เป็น ZIP + REFramework + re2_fw_config.txt

---

## 8. Troubleshooting

| ปัญหา | สาเหตุ | วิธีแก้ |
|---|---|---|
| ยังเป็นภาษาอังกฤษ | REFramework ไม่ทำงาน | ตรวจ dinput8.dll + re2_fw_config.txt |
| หน้าต่าง REFramework บังเกม | ปกติ | กด **Insert** เพื่อซ่อน |
| ม็อดอื่นพัง | ทับ dinput8.dll เดิม | ใช้ REFramework เดิม + เปิด LooseFileLoader |
| เกมอัปเดตแล้วม็อดไม่ทำงาน | REFramework ไม่ compatible | รอ REFramework nightly ใหม่ |

---

## 9. Required Tools

| เครื่องมือ | หน้าที่ |
|---|---|
| **7-Zip / WinRAR** | แตก ZIP |
| **REFramework** (dinput8.dll) | DLL proxy — LooseFile loader |

---

## 10. Extracted Assets

ม็อดนี้เป็น **ZIP with loose files** — มี source code และ build tools:

| ไฟล์ | คำอธิบาย |
|---|---|
| `payload-manifest.json` | Manifest + SHA-256 ทุกไฟล์ (142 KB) |
| `THSarabunNew.ttf` | ฟอนต์ต้นฉบับ |
| `THSarabunNew-DD2-PreShaped.ttf` | ฟอนต์ดัดแปลง (PreShaped clusters) |
| `THSarabunNew-DD2-PreShaped.oft.1` | RE Engine font format |
| `build_sarabun_installer.py` | Build script สำหรับสร้างฟอนต์ |
| `thai-cluster-mapping.json` | Mapping 580 Thai clusters |
| `GPL-2.0.txt` | Font license |
| `REFramework-LICENSE.txt` | REFramework license |
| `THSarabunNew-NOTICE.txt` | Font attribution notice |

---

## Appendix A: Thai PreShaped Cluster Technique

เทคนิค **PreShaped Thai Clusters** เป็นวิธีแก้ปัญหา Thai text rendering ที่ game engine ไม่รองรับ complex text shaping:

```
ปัญหา: เกมวาง สระ/วรรณยุกต์ ผิดตำแหน่ง เช่น:
  กิ → ก แล้ววาง สระอิ ทับ (อาจเลื่อน/ซ้อนผิด)

วิธีแก้: สร้าง glyph "กิ" สำเร็จรูปใน font 1 ตัว:
  กิ → glyph เดียว (pre-composed) → วางตำแหน่งถูกเสมอ

Scale: 580 clusters = ครอบคลุมทุกพยัญชนะ × สระ/วรรณยุกต์ที่ใช้จริง
```

## Appendix B: RE Engine `.msg.24` Format

ไฟล์ `.msg.24` เป็น binary message format ของ RE Engine:
- `.msg` = Message data type
- `.24` = Version/revision number ของ RE Engine format
- เก็บข้อความเป็น UTF-16 LE พร้อม metadata (speaker, timing, etc.)
- REFramework LooseFileLoader อ่านจาก `natives\stm\` ก่อน PAK

## Appendix C: THIRD_PARTY_NOTICES

| Component | License |
|---|---|
| TH Sarabun New | GNU GPL v2+ with font embedding exception |
| REFramework | MIT License (nightly #01417) |

---

*Dragon's Dogma 2 เป็นเกมที่ 7 จาก RE Engine ใน KB*
*สถิติใหม่: 39,107 ข้อความ (มากที่สุด) + 795 ไฟล์ (มากที่สุด) + 580 PreShaped clusters*