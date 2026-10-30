# 📖 Thai Localization Bible — Outpost: Infinity Siege

> **Engine:** Unreal Engine 5 (UE5)  
> **Game ID:** Outpost: Infinity Siege (Steam)  
> **ระดับความยาก:** ★★★★☆ (ยาก — Multi-target locres, Signature Lock, Font Spoofing)  
> **สถานะ:** ✅ สำเร็จ — ทดสอบแจกจ่ายผู้เล่นได้  
> **ผู้แปล:** หน๊ด หนวด translator (NodNuatTranslator)  
> **ผู้เขียน:** THub Modding Team  
> **อัปเดตล่าสุด:** 2026-07-07

---

## สารบัญ

1. [ภาพรวมโปรเจค](#1-ภาพรวมโปรเจค)
2. [โครงสร้างไดเรกทอรี](#2-โครงสร้างไดเรกทอรี)
3. [เครื่องมือที่ใช้](#3-เครื่องมือที่ใช้)
4. [ขั้นตอนที่ 1 — แตกไฟล์เกม (Extraction)](#4-ขั้นตอนที่-1--แตกไฟล์เกม-extraction)
5. [ขั้นตอนที่ 2 — ดึงข้อความออกมา (Unpacking Locres)](#5-ขั้นตอนที่-2--ดึงข้อความออกมา-unpacking-locres)
6. [ขั้นตอนที่ 3 — แปลข้อความ (Translation)](#6-ขั้นตอนที่-3--แปลข้อความ-translation)
7. [ขั้นตอนที่ 4 — Font Spoofing (ฝังฟอนต์ไทย)](#7-ขั้นตอนที่-4--font-spoofing-ฝังฟอนต์ไทย)
8. [ขั้นตอนที่ 5 — Pack Mod (สร้างไฟล์ .pak)](#8-ขั้นตอนที่-5--pack-mod-สร้างไฟล์-pak)
9. [ขั้นตอนที่ 6 — Signature Bypass (ปลดล็อค Mod)](#9-ขั้นตอนที่-6--signature-bypass-ปลดล็อค-mod)
10. [ขั้นตอนที่ 7 — Release (แพ็คไฟล์แจกจ่าย)](#10-ขั้นตอนที่-7--release-แพ็คไฟล์แจกจ่าย)
11. [กับดักและบทเรียน (Traps & Lessons Learned)](#11-กับดักและบทเรียน-traps--lessons-learned)
12. [สรุปเทคนิคที่ใช้ทั้งหมด](#12-สรุปเทคนิคที่ใช้ทั้งหมด)
13. [Appendix: รายละเอียดทางเทคนิค](#13-appendix-รายละเอียดทางเทคนิค)

---

## 1. ภาพรวมโปรเจค

เกม **Outpost: Infinity Siege** ใช้ Unreal Engine 5 และมีระบบ Localization ที่ซับซ้อนกว่าเกม UE5 ทั่วไปมาก เพราะผู้พัฒนาได้ **แยกข้อความออกเป็นหลายไฟล์ `.locres`** (Multi-target) ตามด่านและระบบต่างๆ ของเกม

### สิ่งที่ทำให้เกมนี้ยาก

| ความท้าทาย | รายละเอียด |
|---|---|
| **Multi-target Locres** | ข้อความไม่ได้อยู่ในไฟล์ `Game.locres` เพียงไฟล์เดียว แต่กระจายอยู่ใน 17 ไฟล์ `.locres` |
| **Signature Lock** | เกมมีระบบตรวจสอบลายเซ็น (`.sig`) ของไฟล์ `.pak` ทำให้ Mod ใส่เฉยๆ ไม่ทำงาน |
| **Font ไม่รองรับไทย** | เกมใช้ฟอนต์จีน (NotoSansSC, ZiTi) ซึ่งไม่มีกลิฟภาษาไทย ทำให้ข้อความล่องหน |
| **ชื่อไฟล์ Mod** | เกมนี้บังคับให้ไฟล์ `.pak` ต้องขึ้นต้นด้วย `pakchunk` จึงจะโหลดเข้าไปได้ |

### สถิติโปรเจค

- **จำนวนบรรทัดทั้งหมด:** 19,619 บรรทัด (ข้อมูลที่แปลรวม ~21,976 บรรทัด)
- **จำนวน Locres Targets:** 16 ไฟล์ (11 ไฟล์ที่มีข้อความสำคัญ)
- **ขนาดไฟล์ Mod:** ~8.2 MB (pakchunk999-ThaiMod_P.pak)
- **ไฟล์ Mod สุดท้าย:** `pakchunk999-ThaiMod_P.pak`

---

## 2. โครงสร้างไดเรกทอรี

```
E:\Mod_Workspace\Outpost_Infinity_Siege\
├── 01_Original_Backup\         ← ⛔ READ-ONLY! ไฟล์ต้นฉบับที่แตกจากเกม
│   └── U01\Content\
│       ├── Localization\       ← ไฟล์ .locres ทั้งหมด (17 ไฟล์)
│       │   ├── BQ_1\en\BQ_1.locres          (บทสนทนาภารกิจ Chapter 1)
│       │   ├── BQ_2\en\BQ_2.locres          (บทสนทนาภารกิจ Chapter 2)
│       │   ├── BQ_3\en\BQ_3.locres          (บทสนทนาภารกิจ Chapter 3)
│       │   ├── BQ_4\en\BQ_4.locres          (บทสนทนาภารกิจ Chapter 4)
│       │   ├── Game\en\Game.locres           (⭐ ข้อความหลัก UI/เมนู/ไอเทม ~8,949 บรรทัด)
│       │   ├── Game\en\Game_mod.locres       (ข้อความเสริม Mod)
│       │   ├── StoryLevel_L0\en\...          (ซับไตเติ้ลด่าน 0)
│       │   ├── StoryLevel_L1\en\...          (ซับไตเติ้ลด่าน 1)
│       │   ├── StoryLevel_L2\en\...          (ซับไตเติ้ลด่าน 2)
│       │   ├── StoryLevel_L3\en\...          (ซับไตเติ้ลด่าน 3)
│       │   ├── StoryLevel_L4\en\...          (ซับไตเติ้ลด่าน 4)
│       │   ├── StoryLevel_L5\en\ ~ L10\en\  (ด่านที่ 5-10)
│       │   └── ...
│       └── MainAsset\TextLibrary\Fonts\      ← ฟอนต์ดั้งเดิมของเกม
│
├── 02_Translation_Workspace\   ← ไฟล์ CSV สำหรับแปล
│   ├── Outpost_Translation.csv              (ไฟล์ Input สำหรับ TStudio)
│   ├── Outpost_Translation_translated.csv   (ไฟล์ที่แปลเสร็จแล้ว)
│   └── TStudio_Input_Multi.csv              (ไฟล์รวมจาก Multi-target extraction)
│
├── 04_Builds\                  ← ไฟล์ .pak ที่ Build แล้ว
│   └── pakchunk999-ThaiMod_P.pak
│
├── 05_Proper_Build\            ← ฟอนต์ไทยที่เตรียมไว้
│   ├── Engine\Content\Slate\Fonts\DroidSansFallback.ttf  ← ฟอนต์ไทย
│   └── U01\Content\...
│
├── 05_Scripts_and_Tools\       ← สคริปต์อัตโนมัติ
│   └── Pack_Mod.bat                         (สคริปต์สร้าง Mod อัตโนมัติ)
│
└── 06_Release\                 ← ไฟล์สำหรับแจกจ่าย
    ├── Outpost_TH_1.0_NodNuatTranslato\     (โฟลเดอร์ Release)
    │   ├── U01\
    │   │   ├── Binaries\Win64\
    │   │   │   ├── dsound.dll               (ASI Loader)
    │   │   │   └── UniversalSigBypasser.asi (ตัวปลดล็อค Signature)
    │   │   └── Content\Paks\~mods\
    │   │       └── pakchunk999-ThaiMod_P.pak (ไฟล์ Mod ภาษาไทย)
    │   └── วิธีติดตั้ง_README.txt
    └── Outpost_TH_1.0_NodNuatTranslato.7z   (ไฟล์ ZIP สำหรับแจก)
```

---

## 3. เครื่องมือที่ใช้

| เครื่องมือ | ที่อยู่ | หน้าที่ |
|---|---|---|
| **CUE4Parse CLI** | `E:\Mod_Workspace\Tool\` | แตกไฟล์ `.pak` ของ UE5 (รองรับ AES Key) |
| **FModel** | `E:\Mod_Workspace\Tool\FModel\` | สำรวจโครงสร้างไฟล์ในเกม UE5 แบบ GUI |
| **UnrealLocres** | `E:\Mod_Workspace\Tool\UnrealLocres.exe` | Export/Import ข้อความจาก `.locres` ↔ CSV |
| **repak** | `E:\Mod_Workspace\Tool\repak_cli\repak.exe` | Pack ไฟล์ต่างๆ กลับเป็น `.pak` |
| **UniversalSigBypasser** | `E:\Mod_Workspace\Tool\SigBypasser_v1.2\` | ปลดล็อคระบบตรวจสอบลายเซ็น `.sig` |
| **TStudio** | `modder-hub\tools\flagship\TStudio\` | GUI สำหรับแปลข้อความ |
| **TRun** | `modder-hub\tools\flagship\TRun\` | แปลข้อความอัตโนมัติแบบ Batch |

---

## 4. ขั้นตอนที่ 1 — แตกไฟล์เกม (Extraction)

### 4.1 ค้นหา AES Key

เกมนี้เข้ารหัส AES ไฟล์ `.pak` ต้องหา Key ก่อน

- **ที่มาของ AES Key:** ค้นพบระหว่าง Session แรกของการ Reverse Engineer
- **AES Key:** `0xF9167E48D0C006A54B8623BFC56987411DEB231C8098E45C0348B869F1781AA5`

> [!NOTE]
> **IO Store vs PAK:** เกมนี้ใช้ IO Store format (`.ucas`/`.utoc`) สำหรับเก็บ Asset หลัก  
> แต่ระบบ Modding ใช้ไฟล์ `.pak` แบบดั้งเดิมผ่านโฟลเดอร์ `~mods/` เพื่อ Override ข้อมูล  
> ไฟล์ Mod `.pak` ที่สร้างขึ้น **ไม่ต้องเข้ารหัส AES** — AES Key ใช้แค่ตอนแตกไฟล์ต้นฉบับเท่านั้น

### 4.2 แตกไฟล์ด้วย CUE4Parse CLI

```powershell
# แตกไฟล์ pakchunk0-Windows.pak ด้วย AES Key
CUE4ParseCLI.exe extract ^
    --game-dir "F:\SteamLibrary\steamapps\common\Outpost\U01\Content\Paks" ^
    --aes-key "0xF91..." ^
    --output "E:\Mod_Workspace\Outpost_Infinity_Siege\01_Original_Backup"
```

> [!IMPORTANT]
> **ต้องเก็บ Backup ไว้ใน `01_Original_Backup` เสมอ** เพราะ Packer ต้องใช้ Base locres ดั้งเดิมในการ import ข้อความกลับเข้าไป

### 4.3 ไฟล์สำคัญที่ต้องแตกออกมา

| ประเภท | Path ภายใน .pak | จำนวน |
|---|---|---|
| **Localization** | `U01/Content/Localization/*/en/*.locres` | 17 ไฟล์ |
| **Fonts (Game)** | `U01/Content/MainAsset/TextLibrary/Fonts/*.ufont` | 7 ไฟล์ |
| **Fonts (Engine)** | `Engine/Content/EngineFonts/Faces/*.ufont` | 5 ไฟล์ |
| **Fonts (Slate)** | `Engine/Content/Slate/Fonts/DroidSansFallback.ttf` | 1 ไฟล์ |

---

## 5. ขั้นตอนที่ 2 — ดึงข้อความออกมา (Unpacking Locres)

### 5.1 ปัญหา: Multi-target Locres

> [!CAUTION]
> **กับดักสำคัญ:** เกมนี้ **ไม่ได้** เก็บข้อความทั้งหมดไว้ในไฟล์ `Game.locres` เพียงไฟล์เดียว!  
> ข้อความบทสนทนาและซับไตเติ้ลของแต่ละด่าน ถูกแยกเก็บไว้ในไฟล์ `.locres` ของตัวเอง  
> ถ้าดึงแค่ `Game.locres` จะได้ข้อความเพียง ~8,949 บรรทัด จากทั้งหมด ~19,619 บรรทัด

### 5.2 รายการ Locres Targets ทั้งหมด

| Target | ไฟล์ | เนื้อหา | จำนวนบรรทัดโดยประมาณ |
|---|---|---|---|
| `Game` | `Game/en/Game.locres` | UI หลัก, เมนู, ไอเทม, คำอธิบาย | ~8,949 |
| `Game_mod` | `Game/en/Game_mod.locres` | ข้อความเสริมจาก Mod | มีเล็กน้อย |
| `BQ_1` | `BQ_1/en/BQ_1.locres` | บทสนทนาภารกิจ Chapter 1 | หลายร้อย |
| `BQ_2` | `BQ_2/en/BQ_2.locres` | บทสนทนาภารกิจ Chapter 2 | หลายร้อย |
| `BQ_3` | `BQ_3/en/BQ_3.locres` | บทสนทนาภารกิจ Chapter 3 | หลายร้อย |
| `BQ_4` | `BQ_4/en/BQ_4.locres` | บทสนทนาภารกิจ Chapter 4 | หลายร้อย |
| `StoryLevel_L0`~`L10` | `StoryLevel_L*/en/*.locres` | ซับไตเติ้ลและบทสนทนาแต่ละด่าน | แต่ละไฟล์มีหลายสิบถึงหลายร้อย |

### 5.3 วิธีดึงข้อความ (ใช้ outpost_unpacker.py)

สคริปต์ `outpost_unpacker.py` จะสแกนหาทุกไฟล์ `en/*.locres` แบบ Recursive แล้วรวมทั้งหมดเป็น CSV เดียว

```powershell
python outpost_unpacker.py ^
    --locres-dir "E:\...\01_Original_Backup\U01\Content\Localization" ^
    --output "E:\...\02_Translation_Workspace\TStudio_Input_Multi.csv"
```

**กระบวนการทำงาน:**

```
┌─────────────────────────────────────────────────────────┐
│ สแกน Localization/ หาทุกไฟล์ en/*.locres              │
│  ↓                                                      │
│ แต่ละไฟล์ → UnrealLocres export → temp CSV             │
│  ↓                                                      │
│ อ่าน temp CSV → เพิ่ม prefix "TargetName||" หน้า key   │
│  ↓                                                      │
│ รวมทุก target เป็น TStudio_Input_Multi.csv             │
└─────────────────────────────────────────────────────────┘
```

### 5.4 รูปแบบ CSV ที่ได้ (TStudio Format)

```csv
ID,Source,Translation,AI_Reference
Game||OP_ST_DifficultyDesc/RecycleCompensate,"Recovery failure compensation ratio","",""
BQ_1||ST_BaseMission/BQ_1_1,"Chapter 1 Mission 1","",""
StoryLevel_L1||OP_ST_L1/L1_P1_3_3,"It's about time. Come on over when you're ready.","",""
```

> [!NOTE]
> **รูปแบบ ID:** `TargetName||Namespace/Key`  
> - `TargetName` = ชื่อไฟล์ locres ต้นทาง (เช่น `Game`, `BQ_1`, `StoryLevel_L1`)  
> - `||` = ตัวคั่น (Delimiter) ระหว่าง Target กับ Key  
> - `Namespace/Key` = Key ของ UnrealLocres (เช่น `OP_ST_L1/L1_P1_3_3`)

### 5.5 การ Migrate คำแปลเก่า

หากมีคำแปลจากเวอร์ชันเก่า (ที่ใช้รูปแบบ `Namespace,Key::Hash`) สามารถใช้ `migrate_translations.py` เพื่อรวมคำแปลเก่าเข้ากับ CSV ใหม่ได้:

```powershell
python migrate_translations.py ^
    "Outpost_Translation_old.csv" ^
    "TStudio_Input_Multi.csv" ^
    "Outpost_Translation.csv"
```

**กลไกการจับคู่ ID:**
```
รูปแบบเก่า:  ST_BaseMission,BQ_1_1::3354623
                    ↓ ตัด ::Hash ออก
                    ↓ แทน , ด้วย /
รูปแบบใหม่:  ST_BaseMission/BQ_1_1
                    ↓ จับคู่กับ BQ_1||ST_BaseMission/BQ_1_1
```

---

## 6. ขั้นตอนที่ 3 — แปลข้อความ (Translation)

### 6.1 ใช้ TStudio

เปิดไฟล์ `Outpost_Translation.csv` ใน TStudio เพื่อแปลทีละบรรทัด หรือใช้ TRun เพื่อแปลแบบอัตโนมัติ

### 6.2 ใช้ TRun (แปลอัตโนมัติ)

```
Input:  Outpost_Translation.csv
Output: Outpost_Translation_translated.csv
```

> [!TIP]
> ไฟล์ผลลัพธ์จาก TRun จะมีชื่อลงท้ายด้วย `_translated.csv` โดยอัตโนมัติ ซึ่ง Packer จะใช้ไฟล์นี้ในการ Build Mod

---

## 7. ขั้นตอนที่ 4 — Font Spoofing (ฝังฟอนต์ไทย)

### 7.1 ปัญหา: ข้อความล่องหน (Invisible Text)

> [!CAUTION]
> **กับดักอันตราย:** แม้จะ Pack `.locres` ภาษาไทยเข้าเกมสำเร็จแล้ว ข้อความจะ **หายเป็นช่องว่างเปล่า**!  
> เพราะฟอนต์ที่เกมใช้ (NotoSansSC = ฟอนต์จีน) ไม่มีกลิฟ (Glyph) ภาษาไทย

### 7.2 วิธีแก้: Total Font Override (UMG Font Spoofing)

เทคนิคนี้คือการ **เอาฟอนต์ไทย ไปทับชื่อฟอนต์ทุกตัวที่เกมเรียกใช้** ทำให้เกมคิดว่ากำลังโหลดฟอนต์จีน แต่จริงๆ แล้วเป็นฟอนต์ไทย

### 7.3 รายการฟอนต์ที่ต้อง Override ทั้งหมด (13 ไฟล์)

**ฟอนต์ UI หลักของเกม (7 ไฟล์):**
```
U01/Content/MainAsset/TextLibrary/Fonts/NotoSansSC-Bold.ufont
U01/Content/MainAsset/TextLibrary/Fonts/NotoSansSC-Regular.ufont
U01/Content/MainAsset/TextLibrary/Fonts/NotoSansSC-Medium.ufont
U01/Content/MainAsset/TextLibrary/Fonts/NotoSansSC-Light.ufont
U01/Content/MainAsset/TextLibrary/Fonts/NotoSansSC-Thin.ufont
U01/Content/MainAsset/TextLibrary/Fonts/NotoSansSC-Black.ufont
U01/Content/MainAsset/TextLibrary/Fonts/ZiTiQuanXinYiGuanHeiTi3_0-2.ufont
```

**ฟอนต์ Fallback ของ Engine (5 ไฟล์):**
```
Engine/Content/EngineFonts/Faces/RobotoBold.ufont
Engine/Content/EngineFonts/Faces/RobotoRegular.ufont
Engine/Content/EngineFonts/Faces/RobotoLight.ufont
Engine/Content/EngineFonts/Faces/RobotoItalic.ufont
Engine/Content/EngineFonts/Faces/DroidSansFallback.ufont
```

**ฟอนต์ Slate ของ Engine (1 ไฟล์):**
```
Engine/Content/Slate/Fonts/DroidSansFallback.ttf
```

### 7.4 วิธีทำ Font Spoofing

1. เตรียมฟอนต์ไทยที่รองรับทั้งภาษาไทยและอังกฤษ (เช่น `NotoSansThaiLooped`, `Tahoma`, หรือ `DroidSansFallback` ที่มีกลิฟไทย)
2. Copy ไฟล์ฟอนต์ไทย **ทับทุกไฟล์ฟอนต์ข้างต้น** (เปลี่ยนชื่อให้ตรงกับชื่อฟอนต์ดั้งเดิม)

> [!NOTE]
> **ทำไมต้อง Override ทุกตัว?**  
> UE5 ใช้ระบบ **Composite Font** ที่กำหนดฟอนต์หลักและ Fallback ไว้ใน Font Asset  
> ถ้า Override แค่ Fallback (`DroidSansFallback.ttf`) มันจะไม่ทำงาน เพราะเกมดึงฟอนต์หลัก (NotoSansSC) ก่อนเสมอ  
> ต้อง Override ทั้ง Primary Font และ Fallback Font จึงจะครอบคลุมทุกจุดที่เกมเรียกใช้ฟอนต์

---

## 8. ขั้นตอนที่ 5 — Pack Mod (สร้างไฟล์ .pak)

### 8.1 กระบวนการ Pack (outpost_packer.py)

สคริปต์ `outpost_packer.py` ทำทุกอย่างอัตโนมัติ:

```
┌──────────────────────────────────────────────────────────────┐
│ Step 1: อ่าน Translated CSV                                 │
│   → แยกบรรทัดตาม Target (Game, BQ_1, StoryLevel_L1, ...)   │
│                                                              │
│ Step 2: สร้าง locres แต่ละ Target                            │
│   → สร้าง import CSV ต่อ Target                             │
│   → หา base locres ดั้งเดิมของ Target นั้น                   │
│   → รัน UnrealLocres import เพื่อฉีดข้อความเข้า locres      │
│   → วาง locres ที่ได้ตามโครงสร้าง path เดิมของเกม           │
│                                                              │
│ Step 3: Font Spoofing                                        │
│   → Copy ฟอนต์ไทยทับ 13 ไฟล์ฟอนต์                          │
│                                                              │
│ Step 4: Pack ด้วย repak                                      │
│   → repak pack <temp_dir> <output.pak>                       │
│     --mount-point "../../../" --version V11                   │
└──────────────────────────────────────────────────────────────┘
```

### 8.2 คำสั่ง Pack Mod

```powershell
python outpost_packer.py ^
    --csv "...\Outpost_Translation_translated.csv" ^
    --base-locres-dir "...\01_Original_Backup\U01\Content\Localization" ^
    --thai-font "...\05_Proper_Build\Engine\Content\Slate\Fonts\DroidSansFallback.ttf" ^
    --output-pak "...\04_Builds\pakchunk999-ThaiMod_P.pak"
```

หรือใช้ **Batch Script** ที่เตรียมไว้:

```powershell
# ดับเบิ้ลคลิกไฟล์นี้
E:\...\05_Scripts_and_Tools\Pack_Mod.bat
```

### 8.3 UnrealLocres Import — รายละเอียดทางเทคนิค

```powershell
UnrealLocres.exe import <base.locres> <translated.csv>
# ผลลัพธ์: สร้างไฟล์ <base.locres.new> ในตำแหน่งเดียวกัน
```

> [!IMPORTANT]
> **ข้อกำหนด CSV สำหรับ UnrealLocres:**
> - Encoding: **UTF-8 with BOM** (`\xef\xbb\xbf`)
> - Line endings: **CRLF** (`\r\n`)
> - Format: `key,source,target` (3 คอลัมน์)
> - Key format: `Namespace/KeyName` (ใช้ `/` ไม่ใช่ `,`)

### 8.4 repak — ข้อกำหนดการ Pack

```powershell
repak.exe pack <input_dir> <output.pak> --mount-point "../../../" --version V11
```

| พารามิเตอร์ | ค่า | หมายเหตุ |
|---|---|---|
| `--mount-point` | `"../../../"` | มาตรฐานสำหรับ UE5 |
| `--version` | `V11` | เวอร์ชัน PAK ที่ UE5 ใช้ |

> [!WARNING]
> **ชื่อไฟล์ .pak ต้องขึ้นต้นด้วย `pakchunk`!**  
> เกมนี้ตรวจสอบชื่อไฟล์ ถ้าตั้งชื่อแบบอื่น (เช่น `ThaiMod_P.pak`) เกมจะไม่ยอมโหลดเข้าไป  
> ใช้ชื่อ `pakchunk999-ThaiMod_P.pak` (เลข 999 สูงเพื่อให้โหลดทีหลังสุดและทับข้อความเดิม)

---

## 9. ขั้นตอนที่ 6 — Signature Bypass (ปลดล็อค Mod)

### 9.1 ปัญหา: เกมปฏิเสธ Mod จากเครื่องอื่น

> [!CAUTION]
> **กับดักที่ร้ายที่สุด:** Mod ทำงานบนเครื่องพัฒนา แต่ **ไม่ทำงานบนเครื่องอื่น**!  
> สาเหตุ: เครื่องพัฒนามีตัว Signature Bypasser ติดตั้งอยู่แล้ว แต่เครื่องผู้เล่นทั่วไปไม่มี  
> เกม UE5 หลายเกมจะตรวจสอบไฟล์ `.sig` (Signature) คู่กับ `.pak` ถ้าไม่ตรงก็จะไม่โหลด

### 9.2 วิธีแก้: UniversalSigBypasser

ต้อง **รวมไฟล์ Signature Bypass ไว้ในชุด Mod ที่แจกจ่ายด้วย**

ไฟล์ที่จำเป็น (วางใน `U01\Binaries\Win64\`):

| ไฟล์ | หน้าที่ |
|---|---|
| `dsound.dll` | **ASI Loader** — ตัวโหลดที่หลอกให้เกมเรียก `.asi` |
| `UniversalSigBypasser.asi` | **Signature Bypasser** — ตัว Patch ที่ข้ามการตรวจสอบ `.sig` |

### 9.3 วิธีการทำงาน

```
เกมเปิด → โหลด dsound.dll (ASI Loader)
         → dsound.dll โหลด UniversalSigBypasser.asi
         → ASI Patch ฟังก์ชันตรวจ .sig ให้ return true เสมอ
         → เกมยอมรับ .pak ที่ไม่มี .sig คู่
         → Mod ภาษาไทยโหลดสำเร็จ!
```

---

## 10. ขั้นตอนที่ 7 — Release (แพ็คไฟล์แจกจ่าย)

### 10.1 โครงสร้างไฟล์แจกจ่าย

ออกแบบให้ผู้เล่น **ลากโฟลเดอร์ `U01` ไปวางทับในโฟลเดอร์เกม** เพียงอย่างเดียว:

```
📁 Outpost_TH_1.0/
├── 📁 U01/
│   ├── 📁 Binaries/Win64/
│   │   ├── dsound.dll                    ← ASI Loader
│   │   └── UniversalSigBypasser.asi      ← Signature Bypass
│   └── 📁 Content/Paks/~mods/
│       └── pakchunk999-ThaiMod_P.pak     ← Mod ภาษาไทย
└── 📄 วิธีติดตั้ง_README.txt              ← คู่มือติดตั้ง
```

### 10.2 วิธีติดตั้งสำหรับผู้เล่น

1. แตกไฟล์ ZIP/7z ที่ดาวน์โหลดมา
2. ลากโฟลเดอร์ `U01` ไปวางทับในโฟลเดอร์เกม (`Steam\steamapps\common\Outpost\`)
3. กด "Merge/Replace" เมื่อระบบถาม
4. เข้าเกมได้เลย!

> [!TIP]
> **ทำไมใช้โครงสร้างแบบนี้?**  
> เพราะโฟลเดอร์ `U01` ตรงกับโครงสร้างจริงของเกม ผู้เล่นลากวางได้เลยโดยไม่ต้องรู้ว่าไฟล์ต้องไปวางตรงไหนบ้าง  
> ไม่ต้องใช้ `.bat` หรือ Installer ใดๆ (ซึ่งอาจถูก Antivirus บล็อค หรือถูก NexusMods ปฏิเสธ)

---

## 11. กับดักและบทเรียน (Traps & Lessons Learned)

### 🪤 กับดัก 1: ดึง Locres แค่ไฟล์เดียว
- **อาการ:** แปลแล้วมีข้อความหลักแสดงไทย แต่ซับไตเติ้ลและบทสนทนายังเป็นภาษาอังกฤษ
- **สาเหตุ:** ดึงแค่ `Game.locres` ไม่ได้ดึง `BQ_*` และ `StoryLevel_L*`
- **แก้ไข:** ใช้ Recursive scan ดึงทุกไฟล์ `en/*.locres` ใน Localization/

### 🪤 กับดัก 2: ข้อความล่องหน (Invisible Text)
- **อาการ:** Pack locres สำเร็จ เกมโหลดได้ แต่ข้อความเป็นช่องว่าง
- **สาเหตุ:** ฟอนต์จีน (NotoSansSC) ไม่มีกลิฟภาษาไทย
- **แก้ไข:** Total Font Override — เอาฟอนต์ไทยทับฟอนต์ทุกตัวทั้ง UI หลักและ Engine Fallback

### 🪤 กับดัก 3: ชื่อไฟล์ .pak ไม่ถูกต้อง
- **อาการ:** ใส่ไฟล์ .pak แล้วเกมไม่เปลี่ยนภาษา
- **สาเหตุ:** เกมตรวจสอบว่าชื่อไฟล์ต้องขึ้นต้นด้วย `pakchunk`
- **แก้ไข:** เปลี่ยนชื่อเป็น `pakchunk999-ThaiMod_P.pak`

### 🪤 กับดัก 4: Mod ทำงานบนเครื่องเราแต่ไม่ทำงานบนเครื่องอื่น
- **อาการ:** ทดสอบบนเครื่องตัวเองสำเร็จ แต่ผู้เล่นอื่นใส่ Mod แล้วไม่มีผล
- **สาเหตุ:** เครื่องพัฒนามี Signature Bypasser ติดตั้งอยู่แล้ว เครื่องอื่นไม่มี
- **แก้ไข:** รวม `dsound.dll` + `UniversalSigBypasser.asi` ไว้ในชุด Mod ที่แจก

### 🪤 กับดัก 5: ID ไม่ตรงเวลา Migrate คำแปลเก่า
- **อาการ:** รัน Migration script แล้ว Match ได้ 0 บรรทัด
- **สาเหตุ:** รูปแบบ ID ต่างกัน — เก่าใช้ `Namespace,Key::Hash` ใหม่ใช้ `Target||Namespace/Key`
- **แก้ไข:** ตัด `::Hash` ออก แล้วแทน `,` ด้วย `/` เพื่อจับคู่

---

## 12. สรุปเทคนิคที่ใช้ทั้งหมด

| # | เทคนิค | คำอธิบาย |
|---|---|---|
| 1 | **AES Decryption** | ถอดรหัสไฟล์ `.pak` ด้วย AES Key |
| 2 | **Multi-target Locres Extraction** | สแกนหาทุกไฟล์ `.locres` แบบ Recursive และรวมเป็น CSV เดียว |
| 3 | **Target Prefix System** | ใช้ `TargetName||Key` เพื่อจำว่า Key แต่ละอันมาจากไฟล์ locres ไหน |
| 4 | **UnrealLocres Export/Import** | แปลงไฟล์ `.locres` ↔ CSV เพื่อแก้ไขข้อความ |
| 5 | **UMG Font Spoofing (Total Override)** | เอาฟอนต์ไทยไปทับทุกไฟล์ฟอนต์ที่เกมเรียกใช้ (13 ไฟล์) |
| 6 | **repak Packing** | Pack ไฟล์กลับเป็น `.pak` ด้วย Mount Point `"../../../"` และ Version `V11` |
| 7 | **Signature Bypass (ASI Injection)** | ใช้ `dsound.dll` + `UniversalSigBypasser.asi` ข้ามการตรวจ `.sig` |
| 8 | **pakchunk Naming Convention** | ตั้งชื่อ Mod เป็น `pakchunk999-*_P.pak` เพื่อให้เกมโหลดเป็นลำดับสุดท้าย |
| 9 | **Drag-and-Drop Release Structure** | จัดโครงสร้างไฟล์แจกให้ตรงกับโฟลเดอร์เกม ผู้เล่นลากวางทีเดียวจบ |
| 10 | **CSV ID Migration** | แปลง ID จากรูปแบบเก่า (`Namespace,Key::Hash`) เป็นรูปแบบใหม่ (`Namespace/Key`) |

---

## 13. Appendix: รายละเอียดทางเทคนิค

### A. AES Key

```
ดึงจาก FModel AppSettings:
C:\Users\<User>\AppData\Roaming\FModel\AppSettings.json
```

### B. เส้นทางเกมบน Steam

```
F:\SteamLibrary\steamapps\common\Outpost\
├── U01\
│   ├── Binaries\Win64\           ← ไฟล์ .exe ของเกม
│   └── Content\Paks\             ← ไฟล์ .pak ของเกม
│       ├── pakchunk0-Windows.*   ← ไฟล์หลักของเกม
│       └── ~mods\                ← ⭐ โฟลเดอร์สำหรับ Mod (สร้างเองถ้าไม่มี)
```

### C. Pipeline Commands (คำสั่งทั้งหมด)

```powershell
# 1. แตกไฟล์เกม (ครั้งแรกเท่านั้น)
CUE4ParseCLI.exe extract --game-dir "<game_paks>" --aes-key "<key>" --output "01_Original_Backup"

# 2. ดึงข้อความ
python outpost_unpacker.py --locres-dir "01_Original_Backup\U01\Content\Localization" --output "02_Translation_Workspace\TStudio_Input_Multi.csv"

# 3. (ถ้ามีคำแปลเก่า) Migrate
python migrate_translations.py "old.csv" "TStudio_Input_Multi.csv" "Outpost_Translation.csv"

# 4. แปลข้อความ → ใช้ TStudio/TRun → ได้ Outpost_Translation_translated.csv

# 5. Pack Mod
python outpost_packer.py --csv "..._translated.csv" --base-locres-dir "01_Original_Backup\U01\Content\Localization" --thai-font "DroidSansFallback.ttf" --output-pak "pakchunk999-ThaiMod_P.pak"

# 6. ติดตั้งทดสอบ
copy "pakchunk999-ThaiMod_P.pak" "<game>\U01\Content\Paks\~mods\"
```

### D. สคริปต์ที่เกี่ยวข้อง

| ไฟล์ | ที่อยู่ | หน้าที่ |
|---|---|---|
| `outpost_unpacker.py` | `Plugins/OutpostInfinitySiege/` | ดึงข้อความจาก locres → CSV |
| `outpost_packer.py` | `Plugins/OutpostInfinitySiege/` | CSV → locres → pak |
| `migrate_translations.py` | `Plugins/OutpostInfinitySiege/` | รวมคำแปลเก่าเข้ากับ CSV ใหม่ |
| `Pack_Mod.bat` | `05_Scripts_and_Tools/` | Batch script รัน packer อัตโนมัติ |

---

> **สรุป:** เกม Outpost: Infinity Siege เป็นเกม UE5 ที่มีความท้าทายสูงในการทำ Thai Localization เพราะใช้ระบบ Multi-target Locres, Signature Lock, และฟอนต์ที่ไม่รองรับภาษาไทย การแก้ปัญหาทั้งหมดต้องอาศัยเทคนิค 10 อย่างทำงานร่วมกัน โดยมีกับดักสำคัญ 5 จุดที่ต้องระวัง
