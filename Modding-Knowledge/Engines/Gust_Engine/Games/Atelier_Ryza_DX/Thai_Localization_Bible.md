# Atelier Ryza: Ever Darkness & the Secret Hideout DX — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

> **Generated:** 2026-09-11
> **Analyst:** Rivet Engineer Advanced (Antigravity AI)
> **Game:** Atelier Ryza DX (GUST / Koei Tecmo)
> **Mod:** ThaiMod v1.2 by Pompoko
> **Status:** ✅ Complete (10/10 Mandatory Sections)

---

## 1. Overview

**Atelier Ryza: Ever Darkness & the Secret Hideout DX** เป็นเกม JRPG จากค่าย GUST / Koei Tecmo ขับเคลื่อนด้วย **Gust Engine** (เอนจินเฉพาะทางของสตูดิโอ GUST) ม็อดภาษาไทยโดย **Pompoko** แปลครบทั้งเกม:
- **บทสนทนา:** 12,565 บรรทัด
- **ข้อความระบบ/เมนู:** 10,302 ข้อความ
- **ภาพบรรยาย (Telop):** 9 ชุด (ฉากเปิด + ฉากจบ)
- **ป้ายชื่อผู้พูด:** 101 ชื่อ / ชื่อมอนสเตอร์: 86 ตัว

**Mod Architecture Pattern:** Gust PAK Replacement + DLL Proxy Injection — PAK ไฟล์ทับของเดิมตรง + dinput8.dll สำหรับ Glyph Width Table

---

## 2. Technical Stack

| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Gust Engine (Koei Tecmo / GUST) |
| **Developer** | GUST Co., Ltd. |
| **Archive Format** | **Gust PAK v2** (Magic: `00-00-02-00` + Entry Count LE) |
| **Text Encoding** | UTF-8 (ภายใน PAK) |
| **Font System** | **Custom Glyph Width Table** — ค่าความกว้างตัวอักษรฝังอยู่ใน .exe |
| **DLL Injection** | **dinput8.dll** (DLL Proxy) + **modthai_pompoko.bin** (R2TH format) |
| **AES Encryption** | ❌ ไม่มี |
| **Language Slot** | **English** |
| **Mod Complexity** | ★★★★☆ (ต้อง Reverse Engineer ตาราง Glyph Width ใน .exe + สร้าง DLL Proxy) |

---

## 3. โครงสร้างไฟล์ (File Architecture)

### 3.1 Mod Files

```
AtelierRyzaDX_ThaiMod_v1.2\
├── Data\
│   ├── PACK00_04_01.PAK   (684 MB) ← ภาพบรรยายไทย + หน้าไตเติล
│   ├── PACK01.PAK          (17 MB) ← บทสนทนาไทย
│   └── PACK02.PAK          (55 MB) ← ข้อความระบบ/เมนูไทย + ฟอนต์ไทย
├── dinput8.dll              (210 KB) ← DLL Proxy Loader
├── modthai_pompoko.bin     (56 KB)  ← ตาราง Character Width (R2TH format)
├── README.txt
└── CHANGELOG.txt
```

### 3.2 Install Path

- PAK files → `{GameInstall}\Data\` (ทับของเดิม)
- `dinput8.dll` + `modthai_pompoko.bin` → `{GameInstall}\` (ข้าง `.exe` ของเกม)

### 3.3 Gust PAK v2 Format

ไฟล์ `.PAK` ของ Gust Engine ใช้โครงสร้างดังนี้:
- **Header:** `00-00-02-00` (version 2, uint32 LE)
- **Byte 4-7:** Entry count (uint32 LE) — เช่น `62-00-00-00` = 98 entries
- ไม่มี AES Encryption แต่ไฟล์ภายในถูกจัดเรียงตาม Index Table
- **Tool:** `gust_tools` โดย VitaSmith (GPLv3) สำหรับ Unpack/Repack

---

## 4. Font Analysis

### 4.1 ระบบ Font ของ Gust Engine

**⚡ Key Finding — Glyph Width Table ใน .exe:**

เอนจินของ GUST เก็บ **ค่าความกว้างของตัวอักษรแต่ละตัว** ฝังไว้ในไฟล์ `.exe` ของเกมโดยตรง ภาษาไทยมีสระลอย วรรณยุกต์ และตัวอักษรที่มีความกว้างต่างจากอักษรละตินมาก
หากไม่แก้ไขตารางนี้ → **สระและวรรณยุกต์จะวางผิดตำแหน่ง ซ้อนทับกัน อ่านไม่ออก**

### 4.2 วิวัฒนาการของระบบแพตช์ Font

| Version | วิธีการ | ความเสี่ยง |
|---|---|---|
| v1.0–v1.1 | แก้ไฟล์ `.exe` โดยตรง (patch_thai_font.ps1) | ⚠️ ทำให้ลายเซ็นดิจิทัลเสีย |
| **v1.2** | **dinput8.dll Proxy** เขียนลง Memory ตอนเปิดเกม | ✅ ไฟล์ .exe ไม่ถูกแตะเลย |

### 4.3 modthai_pompoko.bin — Custom Binary Format

| ฟิลด์ | ค่า | หมายเหตุ |
|---|---|---|
| **Magic** | `52-32-54-48` ("R2TH") | Custom format ของ Pompoko |
| **Version** | `02-00-00-00` | v2 |
| **Size** | 56 KB (Ryza 1) | เก็บตาราง Width ของ Glyph ไทยทั้งชุด |

### 4.4 ฟอนต์ที่ใช้

| การใช้งาน | ฟอนต์ | License |
|---|---|---|
| บทสนทนา / เมนู / ระบบ | **Google Sans** | SIL OFL 1.1 |
| ภาพบรรยาย (Telop) | **Mitr** | SIL OFL 1.1 |
| ป้ายเครดิตหน้าไตเติล | **PompokoRound** | Custom |

---

## 5. Text Analysis

### 5.1 ข้อมูลรวม

| รายการ | ค่า |
|---|---|
| **บทสนทนา** | 12,565 บรรทัด (PACK01.PAK, 17 MB) |
| **ข้อความระบบ/เมนู** | 10,302 ข้อความ (PACK02.PAK, 55 MB) |
| **ภาพบรรยาย** | 9 ชุด (PACK00_04_01.PAK, 684 MB) |
| **Language Slot** | English |

### 5.2 สิ่งที่คงเป็นภาษาอังกฤษโดยตั้งใจ

- ชื่อไอเทม / Effect / Trait / สกิล / เพลง — เพื่อให้เทียบกับคู่มือภาษาอังกฤษได้
- ข้อความลิขสิทธิ์ของผู้พัฒนา
- ตัวหนังสือที่ฝังมาในภาพศิลป์ (ร้านค้า, เควสต์, แผนที่)

---

## 6. Cross-Engine Comparison

| Feature | **Atelier Ryza DX** | **Atelier Ryza 2 DX** | **Mafia III** |
|---|---|---|---|
| **Engine** | **Gust Engine** | Gust Engine | Illusion Engine |
| **Archive** | Gust PAK v2 | Gust PAK v2 | SDS |
| **Font** | DLL Proxy + Width Table | DLL Proxy + Width Table | SDS packed TTF |
| **Complexity** | ★★★★☆ | ★★★★☆ | ★★★☆☆ |
| **Modder** | Pompoko | Pompoko | Unknown |

---

## 7. Pipeline — ขั้นตอนสร้างม็อด

### 7.1 Text Pipeline
1. ใช้ `gust_tools` (VitaSmith) เพื่อ Unpack Gust PAK
2. แก้ไขไฟล์ข้อความภายใน (UTF-8)
3. Repack ด้วย `gust_tools`

### 7.2 Font Pipeline (Advanced)
1. **Reverse Engineer** ตำแหน่ง Glyph Width Table ในไฟล์ .exe ของเกม
2. สร้าง Binary Patch ที่เก็บค่า Width ของ Glyph ไทยทั้งชุด (format R2TH)
3. สร้าง **DLL Proxy** (dinput8.dll) ที่อ่านค่าจาก `.bin` แล้วเขียนลง Memory ตอนเปิดเกม
4. ฝัง TTF ฟอนต์ไทยใน PACK02.PAK

### 7.3 Image Pipeline (Telop)
1. Unpack PACK00_04_01.PAK เพื่อดึง Texture ภาพบรรยาย
2. วาดข้อความไทยทับภาพบรรยายต้นฉบับ (เฉพาะส่วนที่เปลี่ยน)
3. Repack — ระบบจะเข้ารหัสเฉพาะส่วนที่เปลี่ยน (1-3%) ส่วนที่เหลือคัดลอกของเดิม

---

## 8. Troubleshooting

| ปัญหา | สาเหตุ | วิธีแก้ |
|---|---|---|
| ตัวหนังสือไทยไม่ขึ้น | ภาษาเกมไม่ใช่ English | ตั้งภาษาเป็น English |
| สระ/วรรณยุกต์ซ้อนกัน | dinput8.dll ไม่ทำงาน | ตรวจ modthai.log (ต้อง "ok: 2/2 runs applied") |
| ไม่มี modthai.log | วาง dinput8.dll ผิดที่ | ต้องอยู่ข้าง .exe ไม่ใช่ใน Data/ |
| "PARTIAL" ใน log | เกมอัปเดตแล้ว .exe เปลี่ยน | รอม็อดรุ่นใหม่ หรือ Verify integrity |

---

## 9. Required Tools

| เครื่องมือ | หน้าที่ | ที่อยู่ |
|---|---|---|
| **gust_tools** (VitaSmith) | Unpack/Repack Gust PAK | GitHub (GPLv3) |
| **Custom DLL Proxy Builder** | สร้าง dinput8.dll สำหรับแต่ละเกม | Pompoko's toolchain |
| **Image Editor** | วาด Telop ภาษาไทย | Photoshop / GIMP |

---

## 10. Extracted Assets

ตำแหน่ง: `E:\Mod_Workspace\Modding-Knowledge\Engines\Gust_Engine\Games\Atelier_Ryza_DX\`

| โฟลเดอร์ | รายละเอียด |
|---|---|
| `Assets\Packages\dinput8.dll` | DLL Proxy Loader (210 KB) |
| `Assets\Packages\modthai_pompoko.bin` | Character Width Table — R2TH format (56 KB) |
| `README.txt` | คู่มือการติดตั้ง (TH) |
| `CHANGELOG.txt` | ประวัติการเปลี่ยนแปลง v1.0 → v1.2 |

> **หมายเหตุ:** ไฟล์ PAK ไม่ถูก Copy ลง KB เนื่องจากขนาดรวม 756 MB — Bible บันทึกโครงสร้างและรายละเอียดไว้แทน

---

*เอกสารนี้สร้างจากการวิเคราะห์ Binary Header, DLL Proxy, และ Custom Format R2TH*
*ดูเพิ่มเติม: [Atelier Ryza 2 DX Bible](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Gust_Engine/Games/Atelier_Ryza_2_DX/Thai_Localization_Bible.md)*