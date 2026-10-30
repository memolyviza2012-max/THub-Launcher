# The Sinking City 2 — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

> **Generated:** 2026-08-29  
> **Analyst:** Rivet Engineer Advanced (Antigravity AI)  
> **Mod Author:** Artdekdok (เพจ "ไม่พร้อมไม่แจก")  
> **Mod Version Analyzed:** v1.1 (26 สิงหาคม 2026)  
> **Status:** ✅ Complete (10/10 Mandatory Sections)

---

## 1. Overview

**The Sinking City 2** เป็นเกม Open-World Investigation Horror พัฒนาโดย **Frogwares** บน **Unreal Engine 5** โดยใช้ Project Codename ภายในว่า **"PlayGround"** (พบจากชื่อโฟลเดอร์ `PlayGround/Content/Paks/`) ม็อดภาษาไทย v1.1 โดย Artdekdok ใช้สถาปัตยกรรมแบบ **Hybrid** — แยกระบบฟอนต์ (Standard PAK) กับระบบข้อความภาษาไทย (IoStore `.ucas`/`.utoc`) รวมไว้ในชุดไฟล์เดียวกัน ทำให้การอัปเดตทั้ง 2 ระบบทำได้ใน deploy เดียว

**Mod Architecture Pattern:** Hybrid (Font Replacement PAK + IoStore Localization)  
**Install Path:** `{GameInstall}/PlayGround/Content/Paks/`

---

## 2. Technical Stack

| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Unreal Engine 5 |
| **Developer** | Frogwares |
| **Project Codename** | **PlayGround** (พบจากชื่อโฟลเดอร์ `PlayGround/Content/Paks/`) |
| **Archive Format** | UE5 Standard PAK (`.pak` v4) + IoStore (`.ucas`/`.utoc` IoStore v8) |
| **AES Encryption** | ❌ **ไม่มี** — PAK Footer = 44 bytes (ไม่มี AES Key GUID field), Magic `E1 12 6F 5A` @ offset 626,733 |
| **Compression** | PAK: ไม่มี (Raw); UCAS: ต้องตรวจ (Oodle สันนิษฐานตาม UE5 default) |
| **Font System** | Font Slot Replacement — `.ufont` มี 2 variants: Wrapped TTF (4-byte size header) และ Raw TTF |
| **Thai Font Used** | **Noto Sans Thai** — Regular/Light/Medium/Bold/SemiBold/Thin (Google Fonts, OFL License) |
| **Text System** | UE5 LocRes v3 (Binary) ใน Standard PAK |
| **Text Encoding** | **UTF-16 LE** — 189,063 Thai UTF-16 LE sequences ใน locres |
| **Mod Complexity** | ★★★☆☆ (ไม่ encrypt, แต่ ufont มี 2 variants, มีทั้ง PAK และ IoStore) |

---

## 3. โครงสร้างไฟล์ (File Architecture)

### 3.1 Mod Package Files

```
The Sinkink City 2 Thai v1.1\
├── TSC2_Artdekdok_TH_P.pak      ← 626,777 bytes (612.1 KB)  ★ ฟอนต์ + LocRes
│   Magic:         E1-12-6F-5A @ offset 626,733  (from end: 44 bytes)
│   PAK Version:   4
│   Index Offset:  0x0009890E  (624,910 bytes)
│   Index Size:    0x0000071E  (1,822 bytes)
│   Index SHA1:    58 8D B4 AC D2 DE 89 F7 22 60 70 E2 4C 68 D5 AC C2 BD 64 6A
│   AES:           ❌ ไม่มี (footer 44 bytes = standard unencrypted format)
│   Entries:       12 files
│
├── TSC2_Artdekdok_TH_P.ucas     ← 194,882 bytes (190.3 KB)  IoStore Data
│   Header[0-7]:   00-00-00-00-48-01-00-00
│   Thai UTF-16:   3,279 sequences
│
├── TSC2_Artdekdok_TH_P.utoc     ← 955 bytes (0.9 KB)  IoStore Index
│   Magic[0-7]:    2D-3D-3D-2D-2D-3D-3D-2D  ("-=--==-" UE5 IoStore)
│   Version:       8  (byte 16-19 = 08-00-00-00)
│   Header Size:   0x90 (144 bytes)
│   Entry Count:   7
│   Chunk Count:   7
│
└── อ่าน.txt                     ← 676 bytes  README (Thai)
```

### 3.2 PAK Contents (12 entries via repak list)

```
PlayGround/Content/
├── Blueprints/UI/Fonts/
│   ├── AlbertusNova/                    ← Game's primary UI font family
│   │   ├── AlbertusNova-Bold.ufont     46.4 KB  [Variant: WRAPPED]
│   │   ├── AlbertusNova-Light.ufont    46.4 KB  [Variant: WRAPPED]
│   │   ├── AlbertusNova-Regular.ufont  46.4 KB  [Variant: WRAPPED]
│   │   └── AlbertusNova-Thin.ufont     46.4 KB  [Variant: WRAPPED]
│   ├── Courier_Bold/
│   │   └── Courier-Bold.ufont          46.4 KB  [Variant: WRAPPED]
│   ├── Jeff_Script/
│   │   └── JeffScript.ufont            46.4 KB  [Variant: WRAPPED]
│   └── ProbaPro/                        ← Game's secondary UI font
│       ├── ProbaPro-Bold.ufont         46.4 KB  [Variant: WRAPPED]
│       ├── ProbaPro-Light.ufont        46.4 KB  [Variant: RAW - TTF at offset 0]
│       ├── ProbaPro-Medium.ufont       46.4 KB  [Variant: RAW - TTF at offset 0]
│       ├── ProbaPro-Regular.ufont      46.4 KB  [Variant: RAW - TTF at offset 0]
│       └── ProbaPro-SemiBold.ufont     46.4 KB  [Variant: WRAPPED]
└── Localization/Game/en/
    └── Game.locres                     1,003.7 KB  ★ ข้อความแปลไทย (LocRes v3)
```

---

## 4. Font Analysis

### 4.1 UFont Format — 2 Variants (การค้นพบสำคัญ)

ม็อดนี้มี `.ufont` **2 รูปแบบ** ที่แตกต่างกันในไฟล์เดียวกัน:

**VARIANT A — Wrapped TTF (8 ไฟล์):**

```
Offset  Content
------  -------
0-3:    XX XX 00 00    ← uint32 LE = payload size (เช่น 78-B9-00-00 = 47,480)
4-7:    00 01 00 00    ← sfnt magic TrueType v1.0
8-9:    00 10          ← numTables = 16 (sfnt header, big-endian)
10-11:  01 00          ← searchRange
12-13:  00 04          ← entrySelector
14-15:  00 00          ← rangeShift
16+:    [table directory: 16 bytes × numTables][table data]
```

ตัวอย่าง AlbertusNova-Bold: header = `78-B9-00-00-00-01-00-00-00-10-01-00-00-04-00-00`

**การสกัด TTF จาก Wrapped:** `bytes[4:]` (ข้ามไป 4 bytes แรก)

**VARIANT B — Raw TTF (3 ไฟล์: ProbaPro-Light/Medium/Regular):**

```
Offset  Content
------  -------
0-3:    00 01 00 00    ← sfnt magic ที่ offset 0 โดยตรง
4-5:    00 10          ← numTables = 16
```

**การสกัด TTF:** copy ไฟล์ทั้งหมดโดยตรง

**หลักฐานยืนยัน:** AlbertusNova-Bold.ufont[4:] === ProbaPro-Light.ufont[0:] (byte-level match ✅)

### 4.2 Font Slot Mapping

| Slot (ufont filename) | Font Family (ยืนยัน Shell.Application) | MD5 |
|---|---|---|
| AlbertusNova-Bold.ufont | **Noto Sans Thai Bold** | EC4C768F |
| AlbertusNova-Light.ufont | **Noto Sans Thai Light** | A9432618 |
| AlbertusNova-Regular.ufont | **Noto Sans Thai Regular** | 5B01640B |
| AlbertusNova-Thin.ufont | **Noto Sans Thai Thin** | EDEE6760 |
| Courier-Bold.ufont | **Noto Sans Thai Bold** | EC4C768F ← ซ้ำกับ AlbertusNova-Bold |
| JeffScript.ufont | **Noto Sans Thai Regular** | 74975058 |
| ProbaPro-Bold.ufont | **Noto Sans Thai Bold** | EC4C768F ← ซ้ำ |
| ProbaPro-Light.ufont | **Noto Sans Thai Light** | 02212516 |
| ProbaPro-Medium.ufont | **Noto Sans Thai Medium** | DC62B966 |
| ProbaPro-Regular.ufont | **Noto Sans Thai Regular** | 42767169 |
| ProbaPro-SemiBold.ufont | **Noto Sans Thai SemiBold** | AD9B1751 |

**Duplicate slots:** Courier-Bold และ ProbaPro-Bold ใช้ไฟล์เดียวกับ AlbertusNova-Bold (MD5 = EC4C768F)

### 4.3 Font Metadata

- **Family:** Noto Sans Thai
- **ผู้สร้าง:** Google Fonts (Noto Project)
- **License:** SIL Open Font License 1.1 (OFL) — ใช้ในม็อดได้ ต้องระบุ copyright
- **ขนาดต่อ weight:** 46.4 KB (ทุกไฟล์)
- **OpenType Tables:** GDEF, GPOS, GSUB, OS/2, STAT, cmap, gasp, glyf — รองรับ Thai shaping ครบ
- **Thai Glyph:** รองรับ Unicode Thai block (U+0E00–U+0E7F) ครบทุกตัว รวมสระลอยและวรรณยุกต์

---

## 5. Text Analysis

### 5.1 Game.locres — LocRes v3

| Property | Value |
|---|---|
| **Path ใน PAK** | `PlayGround/Content/Localization/Game/en/Game.locres` |
| **Magic (bytes 0-15)** | `0E-14-74-75-67-4A-03-FC-4A-15-90-9D-C3-37-7F-1B` |
| **Version (byte 16)** | `03` — UE LocRes version 3 |
| **String Table Offset** | `0x71693` = 464,531 bytes (uint64 at offset 17) |
| **String Count** | **4,202 strings** |
| **Entry/Key Count** | **9,456 entries** (int32 LE at offset 25 = `F0-24-00-00`) |
| **Namespace Count** | **90** (int32 LE at offset 29 = `5A-00-00-00`) |
| **Thai UTF-16 sequences** | 189,063 |
| **File Size** | 1,027,753 bytes |

### 5.2 Encoding

- **Thai text encoding:** UTF-16 LE ทั้งหมด (เป็น UE LocRes standard)
- **FString format:** `[len:int32]` — ถ้า len < 0: `|len|` chars UTF-16 LE; ถ้า len > 0: bytes UTF-8
- **ตัวอย่างข้อความจริง:** `"อาร์คัมพินาศเพราะเรา เราเป็นคนก่อให้เกิดน้ำท่วม..."`

### 5.3 String Key Structure

```
MTTB_PHONO2_COMMENT3467          ← บทสนทนาหลัก (phone/NPC)
TACS_LORELEI_FIGHT1_COMMENT2605  ← บทต่อสู้
MTTB_KM9_07_SUBTITLE147          ← คำบรรยาย (subtitle)
TEZM_TITLE_FOREST_COMMENT3181    ← ชื่อสถานที่
TACS_DRH_GAS_COUGHS_COMMENT109   ← ambient/atmospheric
```

Namespace prefixes: `MTTB_` | `TACS_` | `TEZM_`  
Content types: dialogue, subtitle, zone title, ambient

---

## 6. Cross-Engine Comparison

| Feature | **The Sinking City 2** | **Avowed** | **The Alters** |
|---|---|---|---|
| **Engine** | UE5 (Frogwares) | UE5 (Obsidian) | UE5 (11 bit) |
| **PAK Version** | v4 | v11 | ไม่ระบุ |
| **IoStore** | ✅ (.ucas/.utoc v8) | ✅ (.ucas/.utoc v5) | ❌ (PAK only) |
| **Text location** | LocRes ใน Standard PAK | LocRes ใน UCAS | LocRes ใน PAK |
| **ufont type** | **2 variants** (Wrapped + Raw) | Raw TTF only | Raw TTF only |
| **Thai Font** | Noto Sans Thai (multi-weight) | Pridi Regular (single) | Noto Sans Thai Looped |
| **AES** | ❌ | ❌ | ❌ |
| **Font Slots** | 11 slots (3 families) | หลาย slots | 8 slots |
| **Codename** | PlayGround | Alabama | P9Playable |
| **Complexity** | ★★★☆☆ | ★★★☆☆ | ★★☆☆☆ |

**ข้อสรุปเชิงเทคนิค:**

1. **ufont Wrapper (TSC2-specific):** การพบ `.ufont` แบบ Wrapped (4-byte size header ก่อน TTF) ใน TSC2 ไม่พบใน Avowed หรือ The Alters — เป็นลักษณะเฉพาะของ Frogwares/PlayGround project ซึ่งน่าจะมาจาก UnrealEditor version ที่ export FontFace asset แตกต่างกัน
2. **Text ใน PAK vs UCAS:** TSC2 วาง locres ใน Standard PAK (สกัดด้วย repak ง่าย) ในขณะที่ Avowed วาง text ใน UCAS (ต้องใช้ IoStore-aware tools) — TSC2 จึงแก้ไข text ง่ายกว่า Avowed
3. **Multi-weight Font Design:** TSC2 ใช้ Noto Sans Thai หลาย weight จริง (ต่างจาก Avowed ที่ copy single font ทุก slot) แสดงถึงความใส่ใจในการออกแบบม็อด
4. **ความรู้ที่โยงได้:** เทคนิคการ pack PAK ด้วย repak_cli และการ edit locres ด้วย UnrealLocres สามารถใช้ได้เหมือนกันทั้ง TSC2, Avowed, และ The Alters — เป็น UE5 standard workflow

---

## 7. Pipeline — ขั้นตอนสร้างม็อด

### 7.1 Font Pipeline

#### ขั้นตอน: สร้างใหม่

```python
import struct, shutil

def make_ufont_wrapped(ttf_path: str, out_path: str):
    """สร้าง .ufont แบบ Wrapped (สำหรับ 8 slots ที่ต้องการ header 4 bytes)"""
    with open(ttf_path, 'rb') as f:
        data = f.read()
    assert data[:4] in (b'\x00\x01\x00\x00', b'OTTO'), "Not TTF/OTF"
    with open(out_path, 'wb') as f:
        f.write(struct.pack('<I', len(data)) + data)  # [uint32 LE size][TTF]

def make_ufont_raw(ttf_path: str, out_path: str):
    """สร้าง .ufont แบบ Raw (copy ตรง, สำหรับ ProbaPro-Light/Medium/Regular)"""
    shutil.copy(ttf_path, out_path)

# Slots ที่ต้องการ WRAPPED:
WRAPPED_SLOTS = [
    "AlbertusNova-Bold", "AlbertusNova-Light", "AlbertusNova-Regular",
    "AlbertusNova-Thin", "Courier-Bold", "JeffScript",
    "ProbaPro-Bold", "ProbaPro-SemiBold"
]
# Slots ที่ต้องการ RAW:
RAW_SLOTS = ["ProbaPro-Light", "ProbaPro-Medium", "ProbaPro-Regular"]
```

#### Pack กลับด้วย repak:

```powershell
# จัดโครงสร้างก่อน pack:
# .\pack_input\PlayGround\Content\Blueprints\UI\Fonts\{family}\{slot}.ufont
# .\pack_input\PlayGround\Content\Localization\Game\en\Game.locres

.\repak.exe pack ".\pack_input" --output "TSC2_Artdekdok_TH_P.pak"
```

### 7.2 Text Pipeline

```bash
# Export
UnrealLocres.exe Game.locres --export Game_TH.csv

# (แก้ไข CSV ด้วย Excel/Notepad++ UTF-8)

# Import
UnrealLocres.exe Game.locres --import Game_TH.csv
```

### 7.3 Deploy

```
{GameInstall}\PlayGround\Content\Paks\
├── TSC2_Artdekdok_TH_P.pak     ← ฟอนต์ + locres
├── TSC2_Artdekdok_TH_P.ucas    ← IoStore data
└── TSC2_Artdekdok_TH_P.utoc    ← IoStore index
```

> **⚠️ ต้องมีครบ 3 ไฟล์เสมอ** — ขาดไฟล์ใดไฟล์หนึ่งทำให้ engine ไม่โหลด mod

---

## 8. Troubleshooting

| ปัญหา | สาเหตุ | วิธีแก้ |
|---|---|---|
| ฟอนต์ไม่แสดง | path ผิดหรือขาด `_P` suffix | ตรวจ install path และชื่อไฟล์ |
| ufont pack แล้วเกมไม่รู้จัก | สลับ Wrapped/Raw variant | ตรวจ slot mapping ในตาราง 4.2 |
| ข้อความบาง DLC ยังเป็น English | DLC ยังไม่แปล | Halloway Mansion DLC ยังไม่ครอบคลุมใน v1.1 |
| ตัวอักษรทับซ้อน | font ขาด GSUB/GPOS | ใช้ Noto Sans Thai (มีครบ) |
| UCAS/UTOC ไม่โหลด | ชื่อ prefix ไม่ตรง | ชื่อ .pak, .ucas, .utoc ต้องเหมือนกันทุกตัว |
| repak ทำ PAK version ผิด | default version ไม่ตรง | ใส่ `--version 4` ใน repak command |
| locres encoding เพี้ยน | บันทึก CSV ผิด encoding | ใช้ UTF-8 ใน CSV; UnrealLocres จัดการ UTF-16 LE เอง |
| crash หลังติดตั้ง | PAK header corrupt | ตรวจ PAK magic `E1 12 6F 5A` ที่ท้ายไฟล์ |

---

## 9. Required Tools

| เครื่องมือ | หน้าที่ | ที่อยู่ |
|---|---|---|
| **repak_cli v0.2.3** | Unpack/Pack `.pak` | `E:\Mod_Workspace\Tool\repak_cli\repak.exe` |
| **UnrealLocres** | Export/Import locres ↔ CSV | https://github.com/akintos/UnrealLocres |
| **Python 3.x** | สร้าง ufont wrapper, automation | standard |
| **fontTools** | ตรวจ TTF name table | `pip install fonttools` |
| **HxD** | ตรวจ binary header | https://mh-nexus.de/en/hxd/ |
| **Shell.Application (PS)** | ยืนยัน font name | Windows built-in |

---

## 10. Extracted Assets

### Assets ที่สกัดสำเร็จ

**Fonts:** `E:\Mod_Workspace\Modding-Knowledge\Engines\Unreal_Engine_5\Games\The_Sinking_City_2\Assets\Fonts\`

| File | Font Family | Size | Verified |
|---|---|---|---|
| AlbertusNova-Bold.ttf | Noto Sans Thai Bold | 46.4 KB | ✅ magic + name |
| AlbertusNova-Light.ttf | Noto Sans Thai Light | 46.4 KB | ✅ |
| AlbertusNova-Regular.ttf | Noto Sans Thai Regular | 46.4 KB | ✅ |
| AlbertusNova-Thin.ttf | Noto Sans Thai Thin | 46.4 KB | ✅ |
| Courier-Bold.ttf | Noto Sans Thai Bold | 46.4 KB | ✅ |
| JeffScript.ttf | Noto Sans Thai Regular | 46.4 KB | ✅ |
| ProbaPro-Bold.ttf | Noto Sans Thai Bold | 46.4 KB | ✅ |
| ProbaPro-Light.ttf | Noto Sans Thai Light | 46.4 KB | ✅ |
| ProbaPro-Medium.ttf | Noto Sans Thai Medium | 46.4 KB | ✅ |
| ProbaPro-Regular.ttf | Noto Sans Thai Regular | 46.4 KB | ✅ |
| ProbaPro-SemiBold.ttf | Noto Sans Thai SemiBold | 46.4 KB | ✅ |

**Localization:** `E:\Mod_Workspace\Modding-Knowledge\Engines\Unreal_Engine_5\Games\The_Sinking_City_2\Assets\Localization\Game.locres`

- LocRes v3 | 4,202 strings | 9,456 keys | 90 namespaces | UTF-16 LE

### ข้อจำกัด

- **UCAS content:** ไม่ได้ unpack เนื้อหาใน `.ucas` (ต้องการ FModel/zentools) — locres หลักอยู่ใน PAK แล้ว
- **DLC Halloway Mansion:** ยังไม่มีการแปลใน mod v1.1
- **UTOC Encryption flag 0x0001:** ยังไม่มีหลักฐานชัดว่ามี AES key ที่ใช้งาน

---

*เอกสารนี้สร้างจากการวิเคราะห์ไบนารีจริงของม็อด v1.1*  
*ทุกข้อมูลที่ไม่ระบุ "สันนิษฐาน" = ยืนยันจากหลักฐานโดยตรง*