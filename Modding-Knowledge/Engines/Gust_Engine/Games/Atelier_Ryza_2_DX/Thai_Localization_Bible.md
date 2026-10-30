# Atelier Ryza 2: Lost Legends & the Secret Fairy DX — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

> **Generated:** 2026-09-11
> **Analyst:** Rivet Engineer Advanced (Antigravity AI)
> **Game:** Atelier Ryza 2 DX (GUST / Koei Tecmo)
> **Mod:** ThaiMod v1.0 by Pompoko
> **Status:** ✅ Complete (10/10 Mandatory Sections)

---

## 1. Overview

**Atelier Ryza 2: Lost Legends & the Secret Fairy DX** เป็นภาคต่อจาก Atelier Ryza DX ใช้ **Gust Engine** ตัวเดียวกัน ม็อดภาษาไทยโดย **Pompoko** แปลครบทั้งเกม:
- **บทสนทนา:** 14,521 บรรทัด (มากกว่า Ryza 1 ถึง ~2,000 บรรทัด)
- **ข้อความระบบ/เมนู:** 13,769 ข้อความ (มากกว่า Ryza 1 ถึง ~3,500 ข้อความ)
- **ป้ายชื่อผู้พูด:** 248 ชื่อ / ชื่อมอนสเตอร์: 139 ตัว
- **ภาพบรรยาย (Telop):** 3 ชุด 33 ภาพ + หน้าไตเติลเครดิต

**Mod Architecture Pattern:** เหมือน Ryza 1 — Gust PAK Replacement + DLL Proxy Injection

---

## 2. Technical Stack

| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Gust Engine (Koei Tecmo / GUST) |
| **Developer** | GUST Co., Ltd. |
| **Archive Format** | **Gust PAK v2** (Magic: `00-00-02-00`) |
| **Text Encoding** | UTF-8 (ภายใน PAK) |
| **Font System** | **Custom Glyph Width Table** — ค่าความกว้างฝังใน .exe |
| **DLL Injection** | **dinput8.dll** (207 KB) + **modthai_pompoko.bin** (82 KB) |
| **AES Encryption** | ❌ ไม่มี |
| **Language Slot** | **English** |
| **Mod Complexity** | ★★★★☆ |

---

## 3. โครงสร้างไฟล์ (File Architecture)

### 3.1 Mod Files

```
AtelierRyza2DX_ThaiMod_v1.0\
├── Data\
│   ├── PACK00_04_01.PAK   (565 MB) ← ฟอนต์ไทย + ภาพบรรยาย + หน้าไตเติล
│   ├── PACK01.PAK          (22 MB) ← บทสนทนาไทย
│   └── PACK02.PAK          (77 MB) ← ข้อความระบบ/เมนูไทย
├── dinput8.dll              (207 KB) ← DLL Proxy Loader
├── modthai_pompoko.bin     (82 KB)  ← ตาราง Character Width (R2TH format)
├── README.txt
└── CHANGELOG.txt
```

### 3.2 ความแตกต่างจาก Ryza 1

| รายการ | Ryza 1 DX (v1.2) | **Ryza 2 DX (v1.0)** |
|---|---|---|
| PACK00_04_01 | 684 MB (ภาพ+ไตเติล) | **565 MB** (ฟอนต์+ภาพ+ไตเติล) |
| PACK01 | 17 MB | **22 MB** (+29%) |
| PACK02 | 55 MB | **77 MB** (+40%) |
| dinput8.dll | 210 KB | **207 KB** |
| modthai_pompoko.bin | 56 KB | **82 KB** (+46%) |
| บทสนทนา | 12,565 บรรทัด | **14,521 บรรทัด** |
| ข้อความระบบ | 10,302 | **13,769** |

> **📌 สังเกต:** ไฟล์ `modthai_pompoko.bin` ของ Ryza 2 ใหญ่กว่า Ryza 1 ถึง 46% แสดงว่า Glyph Width Table ของ Ryza 2 มีรายการมากกว่า (อาจมีฟอนต์/ขนาดเพิ่มเติม)

---

## 4. Font Analysis

### 4.1 ระบบ Font — เหมือน Ryza 1

เอนจิน GUST เก็บค่าความกว้างตัวอักษรในไฟล์ `.exe` → ม็อดใช้ **dinput8.dll Proxy** เขียนค่าลง Memory ตอนเปิดเกม → ไฟล์ .exe ไม่ถูกแก้ไข

### 4.2 modthai_pompoko.bin — R2TH Format

| ฟิลด์ | Ryza 1 | Ryza 2 |
|---|---|---|
| **Magic** | `R2TH` | `R2TH` (เหมือนกัน) |
| **Version** | 2 | 2 |
| **Size** | 56 KB | **82 KB** |

### 4.3 ฟอนต์ที่ใช้

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
| **บทสนทนา** | 14,521 บรรทัด (PACK01.PAK) |
| **ข้อความระบบ/เมนู** | 13,769 ข้อความ (PACK02.PAK) |
| **ป้ายชื่อผู้พูด** | 248 ชื่อ |
| **ชื่อมอนสเตอร์** | 139 ตัว |
| **ภาพบรรยาย** | 3 ชุด 33 ภาพ (PACK00_04_01.PAK) |

### 5.2 สิ่งที่คงเป็นภาษาอังกฤษโดยตั้งใจ

- ชื่อไอเทม / Effect / Trait / สกิล / เพลง (รวม DLC)
- การ์ดแนะนำตัวละคร ป้ายชื่อ และ Opening Movie
- ตัวหนังสือที่ฝังมาในภาพศิลป์ (ร้านค้า · เควสต์ · แผนที่ · ผังแร่แปรธาตุ · หน้า DLC)

---

## 6. Cross-Engine Comparison

| Feature | **Atelier Ryza 2 DX** | **Atelier Ryza DX** | **Far Cry 2** |
|---|---|---|---|
| **Engine** | **Gust Engine** | Gust Engine | Dunia Engine |
| **Archive** | Gust PAK v2 | Gust PAK v2 | MAGM/FAT2 |
| **Font Trick** | DLL Proxy + Width Table | DLL Proxy + Width Table | Glyph Remapping (PUA) |
| **EXE Modification** | ❌ (via DLL Proxy) | ❌ (v1.2+) | ❌ |
| **Complexity** | ★★★★☆ | ★★★★☆ | ★★★☆☆ |

**ข้อสรุป:** ทั้ง Atelier Ryza ต้องทำ **Reverse Engineering ระดับ .exe** เพื่อหาตำแหน่ง Glyph Width Table ซึ่งเป็นความท้าทายที่แตกต่างจากเกมเอนจินอื่น ๆ ใน KB ที่ส่วนใหญ่จัดการเรื่องฟอนต์ผ่าน TTF/OTF ปกติ

---

## 7. Pipeline — ขั้นตอนสร้างม็อด

(เหมือน Ryza 1 — ดู [Atelier Ryza DX Bible](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Gust_Engine/Games/Atelier_Ryza_DX/Thai_Localization_Bible.md) Section 7)

---

## 8. Troubleshooting

| ปัญหา | สาเหตุ | วิธีแก้ |
|---|---|---|
| ตัวหนังสือไทยไม่ขึ้น | ภาษาเกมไม่ใช่ English | ตั้งภาษาเป็น English |
| สระ/วรรณยุกต์ซ้อนกัน | dinput8.dll ไม่ทำงาน | ตรวจ modthai.log (ต้อง "ok: N/N runs applied") |
| ไม่มี modthai.log | วาง dinput8.dll ผิดที่ | ต้องอยู่ข้าง .exe ไม่ใช่ใน Data/ |
| "PARTIAL" ใน log | เกมอัปเดตแล้ว | รอม็อดรุ่นใหม่ |

---

## 9. Required Tools

| เครื่องมือ | หน้าที่ | ที่อยู่ |
|---|---|---|
| **gust_tools** (VitaSmith) | Unpack/Repack Gust PAK | GitHub (GPLv3) |
| **Custom DLL Proxy Builder** | สร้าง dinput8.dll | Pompoko's toolchain |
| **Image Editor** | วาด Telop ภาษาไทย | Photoshop / GIMP |

---

## 10. Extracted Assets

ตำแหน่ง: `E:\Mod_Workspace\Modding-Knowledge\Engines\Gust_Engine\Games\Atelier_Ryza_2_DX\`

| โฟลเดอร์ | รายละเอียด |
|---|---|
| `Assets\Packages\dinput8.dll` | DLL Proxy Loader (207 KB) |
| `Assets\Packages\modthai_pompoko.bin` | Character Width Table — R2TH format (82 KB) |
| `README.txt` | คู่มือการติดตั้ง (TH) |
| `CHANGELOG.txt` | ประวัติการเปลี่ยนแปลง v1.0 |

> **หมายเหตุ:** ไฟล์ PAK ไม่ถูก Copy ลง KB เนื่องจากขนาดรวม 664 MB

---

*เอกสารนี้สร้างจากการวิเคราะห์ Binary Header, DLL Proxy, และ Custom R2TH Format*
*ดูเพิ่มเติม: [Atelier Ryza DX Bible](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Gust_Engine/Games/Atelier_Ryza_DX/Thai_Localization_Bible.md)*