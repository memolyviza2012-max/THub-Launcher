# XCOM: Chimera Squad — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

> **Generated:** 2026-09-11
> **Analyst:** Rivet Engineer Advanced (Antigravity AI)
> **Game:** XCOM: Chimera Squad (Firaxis Games / 2K Games)
> **Mod:** Thai v1.0 Manual — Mod Thai By Lung Dear
> **Status:** ✅ Complete (10/10 Mandatory Sections)

---

## 1. Overview

**XCOM: Chimera Squad** เป็นเกม Turn-based Tactics จาก Firaxis Games ขับเคลื่อนด้วย **Unreal Engine 3** (สาย XCOM ที่ปรับปรุงจาก UE3.5) ม็อดภาษาไทยโดย **Lung Dear** ใช้เทคนิค **Korean Slot Override** — วางข้อความไทยลงในช่องภาษาเกาหลีของเกม ทำให้ไฟล์ภาษาอังกฤษไม่ถูกแตะเลยแม้แต่ไฟล์เดียว

**Mod Architecture:** UE3 Korean Localization Slot Override + GFx Font UPK Replacement

---

## 2. Technical Stack

| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Unreal Engine 3.5 (Firaxis branch) |
| **Developer** | Firaxis Games |
| **Archive Format** | **UPK** (Unreal Package v3) — Magic `C1-83-2A-9E` |
| **Text Format** | `.kor` (INI-like key=value, UTF-16 LE) |
| **Font System** | **GFx (Scaleform) Flash font** ใน `gfxfonts_kor_SF.upk` |
| **Language Slot** | **Korean (KOR)** — ภาษาไทยอยู่ในช่อง Korean |
| **Safety** | SHA-256 dual verify (orig + mod) ทุกไฟล์ |
| **Install** | PowerShell script (`install.ps1`) + BAT wrapper |
| **Mod Complexity** | ★★☆☆☆ |

---

## 3. โครงสร้างไฟล์ (File Architecture)

### 3.1 Mod Files (13 ไฟล์, ~6.4 MB)

```
files\XComGame\
├── CookedPCConsole\
│   ├── gfxfonts_kor_SF.upk                (242 KB) ← ฟอนต์ไทย UI (Scaleform)
│   ├── Startup_LOC_KOR.upk                (103 KB) ← ฟอนต์ไทย Cutscene
│   └── Startup_LOC_KOR.upk.uncompressed_size (9 B)
├── Localization\KOR\
│   ├── XComGame.kor   (1,523 KB) ← เกมเพลย์ ไอเทม สกิล คำอธิบาย
│   ├── VO.kor         (1,208 KB) ← Voice Over subtitles (ใหญ่สุด)
│   ├── Subtitles.kor    (32 KB) ← ซับไตเติลคัตซีน
│   ├── Editor.kor        (3 KB) ← Editor strings
│   ├── TemplateOverrides.kor (2 KB) ← ชื่อตัวละคร/หน่วย
│   ├── Engine.kor        (1 KB)
│   ├── GFxUI.kor         (1 KB) ← Font mapping declaration
│   ├── Launch.kor        (0.2 KB)
│   └── XComLauncher.kor  (0.2 KB)
└── PCConsoleTOC.txt   (3,343 KB) ← TOC อัปเดตขนาดไฟล์ใหม่
```

### 3.2 Install Path & Activation

1. ก็อปไฟล์ทั้ง 13 ลง `{GameInstall}\XComGame\`
2. **⚠️ ขั้นตอนที่ขาดไม่ได้:** Steam → Properties → Language → **Korean**
   - ม็อดใส่ข้อความไทยในช่อง Korean ถ้าไม่เปลี่ยนภาษาเกมจะยังเป็นอังกฤษ
   - ข้อดี: สลับกลับ English ได้ทุกเมื่อ ไฟล์ INT ไม่ถูกแตะ

---

## 4. Font Analysis

### 4.1 GFx / Scaleform Font System

XCOM: Chimera Squad ใช้ **Scaleform GFx** สำหรับ UI ซึ่งฝังฟอนต์เป็น **Flash SWF font** ภายใน UPK

| ไฟล์ UPK | ขนาดเดิม | ขนาดม็อด | หน้าที่ |
|---|---|---|---|
| `gfxfonts_kor_SF.upk` | **5,994 KB** | **242 KB** | ฟอนต์ UI (Scaleform) |
| `Startup_LOC_KOR.upk` | 162 KB | 103 KB | ฟอนต์ซับไตเติลคัตซีน |

> **⚡ Key Finding:** ฟอนต์เกาหลีเดิมขนาด **5.9 MB** ถูกแทนที่ด้วยฟอนต์ไทยขนาดแค่ **242 KB** — ม็อดเดอร์ strip ฟอนต์เกาหลีออกทั้งหมดแล้วใส่ฟอนต์ไทยที่เล็กกว่ามาก

### 4.2 Font Mapping (GFxUI.kor)

```ini
[FontLib]
FontLib=gfxfonts_kor.fonts_kor

[Fonts]
NormalFont=Noto Sans KR Regular,Normal
```

Scaleform จะอ่านชื่อ FontLib จาก `GFxUI.kor` แล้วโหลด UPK ที่ตรงกัน

---

## 5. Text Analysis

### 5.1 ข้อมูลรวม

| ไฟล์ | ขนาด | เนื้อหา |
|---|---|---|
| XComGame.kor | 1,523 KB | เกมเพลย์ เมนู ไอเทม สกิล อาวุธ คำอธิบาย |
| VO.kor | 1,208 KB | Voice Over subtitle text ทั้งหมด |
| Subtitles.kor | 32 KB | ซับไตเติลคัตซีน |
| อื่น ๆ (6 ไฟล์) | ~8 KB | Editor, Engine, Launcher, ชื่อหน่วย |

### 5.2 Text Format

```ini
[SectionName]
KeyName="ข้อความภาษาไทย"
```

INI-like key=value format — encoding UTF-16 LE (standard UE3 localization)

---

## 6. Cross-Engine Comparison

| Feature | **XCOM: Chimera Squad** | **XCOM: Enemy Unknown** | **Dead Space 3** |
|---|---|---|---|
| **Engine** | UE3 (Firaxis) | UE3 (Firaxis) | Visceral Engine |
| **Language Slot** | **Korean override** | (ดู Bible) | English |
| **Font System** | Scaleform GFx (UPK) | Scaleform GFx (UPK) | STR embedded |
| **Text Format** | .kor (INI) | .int (INI) | STR "3slo" |
| **Safety** | SHA-256 dual | — | SHA-256 dual |
| **Modder** | Lung Dear | — | Lung Dear |

---

## 7. Pipeline

1. สร้างไฟล์ `.kor` ทั้ง 9 ไฟล์ (UTF-16 LE, INI format) แปลจาก `.kor` ภาษาเกาหลีต้นฉบับ
2. สร้าง GFx font UPK ที่มีฟอนต์ไทยแทนเกาหลี (`gfxfonts_kor_SF.upk`)
3. อัปเดต `PCConsoleTOC.txt` ให้ขนาดไฟล์ตรงกับไฟล์ม็อด (UE3 ตรวจ TOC)
4. สร้าง `manifest.json` พร้อม SHA-256 ของทั้ง orig และ mod

---

## 8. Troubleshooting

| ปัญหา | สาเหตุ | วิธีแก้ |
|---|---|---|
| เกมยังเป็นภาษาอังกฤษ | ไม่ได้ตั้งภาษาเป็น Korean | Steam → Properties → Language → **Korean** |
| ตัวอักษรเป็นสี่เหลี่ยม | `gfxfonts_kor_SF.upk` ไม่ได้ถูกก็อป | ตรวจสอบว่าก็อปครบ 13 ไฟล์ |
| ภาษาไทยหายหลังอัปเดต | Steam เขียนทับ | รัน INSTALL.bat ซ้ำ |

---

## 9. Required Tools

| เครื่องมือ | หน้าที่ |
|---|---|
| **PowerShell** (มากับ Windows) | รัน install.ps1 / uninstall.ps1 |
| **UE Viewer / UModel** | เปิดดู UPK (ถ้าต้องแก้ไข) |

---

## 10. Extracted Assets

ตำแหน่ง: `E:\Mod_Workspace\Modding-Knowledge\Engines\Unreal_Engine_3\Games\XCOM_Chimera_Squad\`

| ไฟล์ | ที่อยู่ใน KB |
|---|---|
| `manifest.json` | `Assets\Packages\` — รายชื่อ 13 ไฟล์ + dual SHA-256 |
| `install.ps1` | `Assets\Packages\` — PowerShell install script |

---

*เอกสารนี้สร้างจากการวิเคราะห์ UPK magic, GFx font mapping, และ manifest.json*
*ดูเพิ่มเติม: [XCOM Enemy Unknown Bible](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unreal_Engine_3/Games/XCOM_Enemy_Unknown/XCOM_Enemy_Unknown_Thai_Localization_Bible.md)*