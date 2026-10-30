# The Blood of Dawnwalker — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

> **Generated:** 2026-09-03
> **Analyst:** Rivet Engineer Advanced (Antigravity AI)
> **Game:** The Blood of Dawnwalker (Rebel Wolves)
> **Mod Versions Analyzed:** v1.1 (Windows) + v2 (WinGDK)
> **Status:** ✅ Complete (10/10 Mandatory Sections)

---

## 1. Overview

**The Blood of Dawnwalker** เป็นเกม Dark Fantasy RPG สร้างโดย **Rebel Wolves** (อดีตทีม The Witcher 3 / Cyberpunk 2077) ขับเคลื่อนด้วย **Unreal Engine 5** ม็อดภาษาไทยมีการปล่อยสองเวอร์ชันสำหรับสองแพลตฟอร์ม Build โดยใช้โครงสร้าง UE5 Patch PAK มาตรฐาน

**Mod Architecture Pattern:** Standard UE5 Patch PAK (`_P` suffix) — ติดตั้งด้วยการวางไฟล์ `.pak` / `.ucas` / `.utoc` ลงในโฟลเดอร์ `Paks` ของเกม

---

## 2. Technical Stack

| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Unreal Engine 5 |
| **Developer** | Rebel Wolves |
| **Archive Format** | PAK + IoStore (`.ucas`, `.utoc`) |
| **Text Encoding** | UTF-16 LE |
| **Font System** | **Raw TTF (.ufont)** — ufont คือ TTF ตรงๆ ไม่มี Unreal header |
| **AES Encryption** | ❌ ไม่มี (repak ทำงานได้ทันที) |
| **Language Slot** | **English (en)** |
| **Platforms** | Windows (`Windows_P`) + Xbox GDK (`WinGDK_P`) |
| **Mod Complexity** | ★★☆☆☆ |

---

## 3. โครงสร้างไฟล์ (File Architecture)

### 3.1 v1.1 (Windows Build)
```
Dawnwalker 1.1\
├── Dawnwalker-Windows_P.pak     (3.31 MB)
├── Dawnwalker-Windows_P.ucas    (3.66 MB)
└── Dawnwalker-Windows_P.utoc    (374 bytes)
```

### 3.2 v2 (WinGDK Build — Xbox Game Development Kit)
```
Dawnwalker (WinGDK)\
├── Dawnwalker-Thai-WinGDK_P.pak      (28 MB)   ← Main mod
├── Dawnwalker-ThaiLogo-WinGDK_P.pak  (0.3 KB)
├── Dawnwalker-ThaiLogo-WinGDK_P.ucas (19.4 MB) ← Thai Logo (IoStore)
├── Dawnwalker-ThaiLogo-WinGDK_P.utoc (4.4 KB)
└── intro_cgi_en.srt                   (4.5 KB)  ← Intro Cinematic subtitle
```

### 3.3 Unpacked Content (WinGDK)
```
Dawnwalker/Content/
├── Localization/
│   ├── Dialogues_All/en/Dialogues_All.locres   (5.69 MB)
│   └── OnScreens_All/en/OnScreens_All.locres   (2.75 MB)
├── _Dawnwalker/UI/Fonts/
│   ├── Afacad-Italic.ufont    (124.1 KB)
│   ├── Afacad-Regular.ufont   (122.6 KB)
│   └── Afacad-SemiBold.ufont  (122.8 KB)
└── _Dawnwalker/UI/_Unified/MainMenu/Textures/
    ├── T_Menu_Logo_Scaled.uasset/.uexp      (8.9 MB)
    ├── T_Menu_Logo_Scaled_Normal.uasset/.uexp (8.9 MB)
    └── T_Menu_Logo_Small.uasset/.uexp         (1.9 MB)
```

### 3.4 Install Path
ไฟล์ pak ทั้งหมด (4 ไฟล์) + `.ucas` + `.utoc` ไปวางที่:
`{GameInstall}\The Blood of Dawnwalker\Content\Dawnwalker\Content\Paks\`

ไฟล์ SRT ไปวางที่:
`{GameInstall}\The Blood of Dawnwalker\Content\Dawnwalker\Content\Movies\`

---

## 4. Font Analysis

### 4.1 ฟอนต์ที่ใช้งาน — Afacad Family

| File | Family Name | Format | v1.1 Size | v2 Size |
|---|---|---|---|---|
| Afacad-Regular.ufont | Afacad Regular | **Raw TTF** | 69.9 KB | **122.6 KB** |
| Afacad-SemiBold.ufont | Afacad SemiBold | **Raw TTF** | 69.9 KB | **122.8 KB** |
| Afacad-Italic.ufont | Afacad Italic | **Raw TTF** | 72.2 KB | **124.1 KB** |

> **⚡ Key Finding:** ฟอนต์ในเวอร์ชัน WinGDK มีขนาดใหญ่กว่า v1.1 เกือบ **2 เท่า** (≈ 52 KB ต่อ weight) แสดงว่าม็อดเดอร์ได้เพิ่ม **Thai Glyph Set ที่สมบูรณ์มากขึ้น** ลงในฟอนต์เวอร์ชัน WinGDK

### 4.2 ความแตกต่างระหว่าง v1.1 และ v2

- **v1.1:** มี RobotoCondensed (5 weights) สำหรับระบบ MetaHumans เพิ่มมาด้วย
- **v2 (WinGDK):** ตัด RobotoCondensed ออก เหลือแค่ Afacad 3 weights แต่ Glyph Thai ครบกว่า

### 4.3 Raw TTF Override

ufont ทุกไฟล์ในม็อดนี้เป็น **Raw TTF** ตรงๆ (magic `00-01-00-00` ที่ offset 0) เปลี่ยนนามสกุล .ttf → .ufont โดยไม่มี UAsset header ห่อหุ้ม

---

## 5. Text Analysis

### 5.1 ข้อมูลรวม

| รายการ | v1.1 | v2 (WinGDK) |
|---|---|---|
| Dialogues_All.locres | 5.39 MB | **5.69 MB** |
| OnScreens_All.locres | 2.71 MB | **2.75 MB** |
| Encoding | UTF-16 LE | UTF-16 LE |
| Format | LocRes v3 | LocRes v3 |

### 5.2 เนื้อหาที่แปล

- **Dialogues_All:** บทสนทนา, Subtitle ทั้งเกม
- **OnScreens_All:** UI, เมนู, Tutorial, ไอเทม, ทักษะ, Objective
- **intro_cgi_en.srt:** ซับไตเติลภาษาไทยสำหรับ Intro Cinematic (UTF-8 BOM)

---

## 6. Texture Analysis (WinGDK เท่านั้น)

### 6.1 Thai Logo Textures

ม็อดนี้แทนที่ **โลโก้เกมบนหน้า Main Menu** ด้วยเวอร์ชันภาษาไทย:

| File | Size | หน้าที่ |
|---|---|---|
| T_Menu_Logo_Scaled.uasset/.uexp | 8.9 MB | โลโก้หลัก (ขนาดใหญ่) |
| T_Menu_Logo_Scaled_Normal.uasset/.uexp | 8.9 MB | Normal Map ของโลโก้ใหญ่ |
| T_Menu_Logo_Small.uasset/.uexp | 1.9 MB | โลโก้เล็ก (Corner badge) |

> **📌 สำคัญ:** Texture เหล่านี้เป็น **UAsset format** (ไม่ใช่ PNG ตรงๆ) ต้องใช้ FModel หรือ UModel ถ้าต้องการดูหรือแก้ไข

### 6.2 ThaiLogo PAK (IoStore)

`Dawnwalker-ThaiLogo-WinGDK_P.ucas` ขนาด 19.4 MB เป็น IoStore container ที่เก็บ Texture ขนาดใหญ่ (น่าจะเป็น Splash Screen / Loading Logo สำหรับแพลตฟอร์ม Xbox GDK)

---

## 7. Cross-Engine Comparison

| Feature | **Dawnwalker WinGDK** | **Mortal Shell 2** | **Dragonkin** |
|---|---|---|---|
| **Engine** | UE5 (Rebel Wolves) | UE5 (Cold Symmetry) | UE5 |
| **PAK Version** | 11 + IoStore | 11 | 11 + IoStore |
| **AES** | ❌ | ❌ | ❌ |
| **Font Format** | Raw TTF (.ufont) | Wrapped TTF (.ufont) | Raw TTF (.ufont) |
| **Language Slot** | English (en) | Ukrainian (uk) | English (en) |
| **Extra Content** | ✅ Logo Textures + SRT | ❌ | ❌ |
| **Complexity** | ★★☆☆☆ | ★★★★☆ | ★★☆☆☆ |

---

## 8. Troubleshooting

| ปัญหา | สาเหตุ | วิธีแก้ |
|---|---|---|
| โลโก้หน้า Main Menu ยังเป็นภาษาอังกฤษ | ลืมวาง ThaiLogo .ucas/.utoc | ตรวจสอบว่า copy ไฟล์ครบทั้ง 4 รายการ |
| Intro Cinematic ไม่มีซับไทย | SRT วางผิดโฟลเดอร์ | วางใน `Content\Movies\` ไม่ใช่ `Paks\` |
| ตัวหนังสือ UI เป็นสี่เหลี่ยม | Afacad ufont โหลดไม่ได้ | ตรวจสอบ path `_Dawnwalker/UI/Fonts/` ใน pak |

---

## 9. Required Tools

| เครื่องมือ | หน้าที่ | ที่อยู่ |
|---|---|---|
| **repak_cli** | Unpack / Repack .pak | `E:\Mod_Workspace\Tool\repak_cli\repak.exe` |
| **FModel** | ดู UAsset Textures | https://fmodel.app |
| **UnrealLocres** | แก้ไขข้อความ .locres | `E:\Mod_Workspace\Tool\` |

---

## 10. Extracted Assets

ตำแหน่ง: `E:\Mod_Workspace\Modding-Knowledge\Engines\Unreal_Engine_5\Games\Dawnwalker\`

### v1.1 (Windows)
| โฟลเดอร์ | รายละเอียด |
|---|---|
| `Assets\Fonts\` | Afacad x3 + RobotoCondensed x5 (Raw TTF) |
| `Assets\Localization\` | Dialogues_All + OnScreens_All.locres |
| `Assets\Packages\` | Mod PAK/UCAS/UTOC |

### v2 (WinGDK) — **ใหม่**
| โฟลเดอร์ | รายละเอียด |
|---|---|
| `Assets\Fonts_WinGDK\` | Afacad x3 (Raw TTF, Full Thai Glyph) — ขนาดใหญ่กว่า v1.1 เกือบ 2x |
| `Assets\Localization_WinGDK\` | Dialogues_All + OnScreens_All.locres + intro_cgi_en.srt |
| `Assets\Textures_WinGDK\` | T_Menu_Logo_Scaled/Normal/Small (uasset + uexp) |
| `Assets\Packages_WinGDK\` | Mod PAK (Thai + ThaiLogo) + UCAS/UTOC |

---

*เอกสารนี้สร้างจากการวิเคราะห์และสกัดไฟล์ทั้งสองเวอร์ชันสมบูรณ์ 100%*