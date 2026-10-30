# Dragonkin: The Banished — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

> **Generated:** 2026-08-29
> **Analyst:** Rivet Engineer Advanced (Antigravity AI)
> **Mod:** DragonkinThai v1.01
> **Status:** ✅ Complete (10/10 Mandatory Sections)

---

## 1. Overview

**Dragonkin: The Banished** เป็นเกม Action RPG ในแนว Hack-and-Slash พัฒนาบน **Unreal Engine 5** โดยใช้ Project Codename ภายในว่า **"DragonkinTheBanished"** (พบจากโฟลเดอร์ `DragonkinTheBanished/Content/`) ม็อดภาษาไทย v1.01 ใช้สถาปัตยกรรมแบบ **File Replacement** — Standard PAK ไฟล์เดียว ครอบคลุมทั้งฟอนต์ (.ttf + .ufont) และ localization (2 ไฟล์ locres) ไม่ใช้ IoStore (.ucas/.utoc) และไม่มี AES Encryption ทำให้เป็นม็อดที่เข้าถึงและแก้ไขง่ายที่สุดในกลุ่ม UE5

**Mod Architecture Pattern:** File Replacement (Standard PAK only)
**Install Path:** `{GameInstall}/DragonkinTheBanished/Content/Paks/`

---

## 2. Technical Stack

| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Unreal Engine 5 |
| **Developer** | Bazooka Tango |
| **Project Codename** | **DragonkinTheBanished** (จากโฟลเดอร์ `DragonkinTheBanished/Content/`) |
| **Archive Format** | Standard PAK v11 (ไม่มี IoStore) |
| **AES Encryption** | ❌ **ไม่มี** — EncryptIndex = 0x00, EncryptionKeyGUID = all zeros (ยืนยัน 100%) |
| **Compression** | ไม่มี (Raw data ใน PAK) |
| **Font System** | Dual-format Font Replacement — ทั้ง `.ttf` และ `.ufont` ใน Slate/Fonts/ (ทั้งหมดเป็น Raw TTF ที่ offset 0) |
| **Thai Font Used** | **Noto Sans Thai Regular** (ทุก slot, ไฟล์เดียวกันทั้งหมด) |
| **Text System** | UE5 LocRes v3 (Binary) — **2 ไฟล์แยก:** Dialog.locres + Game.locres |
| **Text Encoding** | **UTF-16 LE** |
| **Mod Complexity** | ★★☆☆☆ (ง่ายมาก: PAK ไฟล์เดียว, ไม่ encrypt, raw TTF ทุก slot) |

---

## 3. โครงสร้างไฟล์ (File Architecture)

### 3.1 Mod Package

```
DragonkinThai v1.01\
└── z_DragonkinThai.pak    ← 1,682,426 bytes (1,643 KB)  ★ ไฟล์ม็อดเดียว
    Magic:        E1-12-6F-5A  @ offset 1,682,222 (from end: 204 bytes)
    PAK Version:  11
    Index Offset: 1,681,224 bytes
    Index Size:   210 bytes
    Index Hash:   86-0E-5E-70-11-57-BE-08-BA-F3-B6-3E-9A-22-06-01-7A-E2-30-92
    AES:          ❌ EncryptIndex=0x00, KeyGUID=00×16 (all-zero)
    Entries:      8 files
```

> **หมายเหตุ footer:** PAK v11 footer ขนาด 204 bytes (ใหญ่กว่า standard v4 ที่ 44 bytes) เพราะมี extended fields รวม EncryptionKeyGUID (16 bytes) และ padding สำหรับ UE5 features — แต่ค่าทั้งหมดเป็น zero = ไม่มี encryption จริง

### 3.2 PAK Contents (8 entries)

```
DragonkinTheBanished/Content/
├── Localization/
│   ├── Dialog/en/
│   │   └── Dialog.locres      535,356 bytes (522.8 KB)  ★ บทสนทนา/dialogue
│   └── Game/en/
│       └── Game.locres        910,676 bytes (889.3 KB)  ★ UI/items/names
│
└── Slate/Fonts/
    ├── Gupter-Bold.ttf        39,128 bytes (38.2 KB)    ← Raw TTF (magic offset 0)
    ├── Gupter-Bold.ufont      39,128 bytes (38.2 KB)    ← Identical to .ttf
    ├── NotoSans-Bold.ttf      39,128 bytes (38.2 KB)    ← Identical to all others
    ├── NotoSans-Bold.ufont    39,128 bytes (38.2 KB)    ← Identical
    ├── NotoSans-Regular.ttf   39,128 bytes (38.2 KB)    ← Identical
    └── NotoSans-Regular.ufont 39,128 bytes (38.2 KB)    ← Identical
```

### 3.3 Font Path เฉพาะ

ม็อดนี้วางฟอนต์ใน `Slate/Fonts/` (ไม่ใช่ `Blueprints/UI/Fonts/` หรือ `Content/Fonts/`) ซึ่งเป็น path ของ Unreal Slate UI framework — บ่งบอกว่าเกมใช้ Slate (built-in UE UI framework) แทน UMG/Blueprint สำหรับ UI หลัก

---

## 4. Font Analysis

### 4.1 Raw TTF Format (ไม่มี UE Wrapper)

ทุก `.ttf` และ `.ufont` ทั้ง 6 ไฟล์เป็น **Raw TTF ที่ offset 0** ไม่มี UE header wrapper:

```
Offset  Content
------  -------
0-3:    00-01-00-00       ← sfnt magic TrueType v1.0
4-5:    00-12             ← numTables = 18 (big-endian)
6-7:    01-00             ← searchRange
8-9:    00-04             ← entrySelector
10-11:  00-20             ← rangeShift
12+:    [table directory: 16 bytes × 18][table data]

OpenType tables confirmed: GDEF, GPOS, GSUB, OS/2, cmap, glyf, loca, hhea, hmtx, maxp, name, head, post, prep, fpgm, cvt, gasp, TTFA
```

### 4.2 Font Slot Mapping

| Slot (ชื่อไฟล์ในเกม) | Font จริง | MD5 |
|---|---|---|
| Gupter-Bold.ttf | **Noto Sans Thai Regular** | 3B8502F4 |
| Gupter-Bold.ufont | **Noto Sans Thai Regular** | 3B8502F4 ← identical |
| NotoSans-Bold.ttf | **Noto Sans Thai Regular** | 3B8502F4 ← identical |
| NotoSans-Bold.ufont | **Noto Sans Thai Regular** | 3B8502F4 ← identical |
| NotoSans-Regular.ttf | **Noto Sans Thai Regular** | 3B8502F4 ← identical |
| NotoSans-Regular.ufont | **Noto Sans Thai Regular** | 3B8502F4 ← identical |

**หลักฐาน:** MD5 hash เดียวกันทุกไฟล์ (`3B8502F42413342D3CB1C5BFAC2D8052`) — ม็อดเดอร์ copy ฟอนต์เดียวไว้ทุก slot ทั้ง TTF และ ufont

### 4.3 Font Metadata

- **Family:** Noto Sans Thai Regular
- **ผู้สร้าง:** Google Fonts (Noto Project)
- **License:** SIL Open Font License 1.1 (OFL) — ใช้ในม็อดได้ ต้องระบุ copyright
- **ขนาด:** 39,128 bytes (38.2 KB) ต่อไฟล์
- **Thai Support:** รองรับ Unicode Thai block (U+0E00–U+0E7F) ครบ รวม GSUB/GPOS สำหรับ Thai shaping
- **Glyph count:** ตรวจผ่าน name table — "Noto Sans Thai Regular" (ยืนยัน Shell.Application ✅)

### 4.4 Slate Font Path — ความสำคัญ

เกมใช้ `Slate/Fonts/` แทน path มาตรฐาน UMG แสดงว่า:
- UI ส่วนหลักสร้างด้วย Unreal Slate (C++ based)
- การแทนที่ฟอนต์ครอบคลุม Slate UI ทั้งหมดในทีเดียว
- ม็อดเดอร์ต้องวางทั้ง `.ttf` และ `.ufont` คู่กัน เพราะ Slate อ้างอิงทั้งสองรูปแบบขึ้นอยู่กับ config

---

## 5. Text Analysis

### 5.1 File Overview

| ไฟล์ | หน้าที่ | ขนาด | Strings | Keys | Namespaces | Thai UTF-16 |
|---|---|---|---|---|---|---|
| **Dialog.locres** | บทสนทนา NPC/quest dialogue | 522.8 KB | 1,631 | 1,648 | 308 | 174,926 |
| **Game.locres** | UI / ชื่อตัวละคร / ไอเทม / คำอธิบาย | 889.3 KB | 6,832 | 7,307 | 24 | 212,461 |
| **รวม** | | **1,412.1 KB** | **8,463** | **8,955** | **332** | **387,387** |

### 5.2 Format (ทั้ง 2 ไฟล์)

| Property | Value |
|---|---|
| **Magic (bytes 0-15)** | `0E-14-74-75-67-4A-03-FC-4A-15-90-9D-C3-37-7F-1B` |
| **Version** | 3 (byte 16) — UE LocRes v3 |
| **Encoding** | UTF-16 LE |
| **FString format** | len < 0: `|len|` chars UTF-16 LE; len > 0: bytes UTF-8 |

Dialog.locres StringTable @ offset 99,357 | Game.locres StringTable @ offset 253,004

### 5.3 ตัวอย่างข้อความจริง

```
Dialog.locres:
  "อา! ถ้าอย่างนั้น เจ้าก็คงเป็นพวกเดียวกับ Astrea สินะ"

Game.locres:
  "อสุรกายเนื้อเน่า"
```

### 5.4 Key Structure

**Dialog.locres** — รูปแบบ key:
```
PO_TRAQUE2B_14_DIALOG_CH030_Alaric      ← Quest/scene/line/character
PO_TRAQUE2B_14_DIALOG_CH070_Alaric
PO_TRAQUE2A_04_IN_ACTION_CH010_Ferrywoman
PO_TRAQUE2B_24_DIALOG_CH010_Astrea
```
Pattern: `PO_{QUEST}_{SCENE}_DIALOG_CH{LINE}_{CHARACTER}` — 308 namespaces, 1,631 strings

**Game.locres** — รูปแบบ key:
```
Character_Names.SemiBoss_Red       ← ชื่อ NPC/boss
Ancestor.06_Name                   ← ชื่อตัวละคร
Ancestor.08_Name
Ancestor.10_Desc                   ← คำอธิบาย
EndGame_Boss_Blue_03               ← ชื่อ boss
EndGame_Boss_Violet_02
Ally_Knight                        ← ชื่อ ally
```
Pattern: `{Namespace}.{Type}` — 24 namespaces, 6,832 strings (ส่วนใหญ่เป็น item/character names)

---

## 6. Cross-Engine Comparison

| Feature | **Dragonkin: The Banished** | **The Sinking City 2** | **The Alters** |
|---|---|---|---|
| **Engine** | UE5 (Bazooka Tango) | UE5 (Frogwares) | UE5 (11 bit) |
| **PAK Version** | v11 | v4 | - |
| **IoStore** | ❌ ไม่มี | ✅ (ucas/utoc) | ❌ ไม่มี |
| **LocRes files** | **2 ไฟล์** (Dialog + Game) | 1 ไฟล์ | 1 ไฟล์ |
| **Font path** | **Slate/Fonts/** (เฉพาะ) | Blueprints/UI/Fonts/ | Content/Fonts/ |
| **ufont format** | Raw TTF (no wrapper) | Wrapped + Raw (2 variants) | Raw TTF |
| **Font slots** | 3 TTF + 3 ufont = 6 (แต่ 1 font) | 11 slots (multi-weight) | 8 slots |
| **Thai Font** | Noto Sans Thai Regular (single) | Noto Sans Thai (multi-weight) | Noto Sans Thai Looped |
| **AES** | ❌ | ❌ | ❌ |
| **Complexity** | ★★☆☆☆ | ★★★☆☆ | ★★☆☆☆ |

**ข้อสรุปเชิงเทคนิค:**

1. **Slate Font Path:** Dragonkin ใช้ `Slate/Fonts/` ซึ่งไม่เหมือนเกม UE5 ใดใน Knowledge Base — สาเหตุที่ต้องมีทั้ง `.ttf` และ `.ufont` เพราะ Slate engine อ้างอิงทั้งสอง format
2. **Dual LocRes:** Dialog + Game separation ทำให้แก้ไข dialogue กับ UI แยกกันได้อิสระ (เหมาะกับทีมแปลที่แบ่งงาน)
3. **PAK v11 without IoStore:** Dragonkin ใช้ PAK v11 แต่ไม่มี IoStore ซึ่งต่างจาก TSC2 ที่มีทั้ง PAK v4 + IoStore — ยืนยันว่า PAK version ไม่ได้บ่งบอก IoStore เสมอไป
4. **ความรู้ที่ใช้ได้:** workflow repak_cli + UnrealLocres ใช้เหมือนกันกับ The Sinking City 2 และ The Alters ทุกอย่าง

---

## 7. Pipeline — ขั้นตอนสร้างม็อด

### 7.1 Font Pipeline

```python
import shutil, struct

def create_font_slots(new_ttf: str, output_dir: str):
    """สร้างทุก font slot สำหรับ Dragonkin"""
    # Verify TTF magic
    with open(new_ttf, 'rb') as f:
        magic = f.read(4)
    assert magic in (b'\x00\x01\x00\x00', b'OTTO'), "Not TTF/OTF"
    
    # All 6 slots ใช้ raw copy (ไม่ต้องทำ wrapper)
    slots = [
        "Gupter-Bold.ttf", "Gupter-Bold.ufont",
        "NotoSans-Bold.ttf", "NotoSans-Bold.ufont",
        "NotoSans-Regular.ttf", "NotoSans-Regular.ufont"
    ]
    for slot in slots:
        dst = f"{output_dir}/{slot}"
        shutil.copy(new_ttf, dst)
        print(f"Created: {slot}")
```

### 7.2 Text Pipeline

```bash
# Export Dialog
UnrealLocres.exe Dialog.locres --export Dialog_TH.csv

# Export Game
UnrealLocres.exe Game.locres --export Game_TH.csv

# (แก้ไข CSV ด้วย UTF-8 editor)

# Import กลับ
UnrealLocres.exe Dialog.locres --import Dialog_TH.csv
UnrealLocres.exe Game.locres --import Game_TH.csv
```

### 7.3 Pack และ Deploy

```powershell
# โครงสร้างก่อน pack:
# .\pack_in\DragonkinTheBanished\Content\Slate\Fonts\*.ttf
# .\pack_in\DragonkinTheBanished\Content\Slate\Fonts\*.ufont
# .\pack_in\DragonkinTheBanished\Content\Localization\Dialog\en\Dialog.locres
# .\pack_in\DragonkinTheBanished\Content\Localization\Game\en\Game.locres

.\repak.exe pack ".\pack_in" --output "z_DragonkinThai.pak"

# Deploy:
# {GameInstall}\DragonkinTheBanished\Content\Paks\z_DragonkinThai.pak
```

> **หมายเหตุ naming:** ชื่อขึ้นต้นด้วย `z_` เพื่อโหลดหลังสุดและ override ไฟล์ต้นฉบับ (UE engine โหลด PAK ตามลำดับตัวอักษร)

---

## 8. Troubleshooting

| ปัญหา | สาเหตุ | วิธีแก้ |
|---|---|---|
| ฟอนต์ไม่แสดง | path ผิด หรือขาด `.ufont` คู่ | ต้องมีทั้ง `.ttf` AND `.ufont` ใน `Slate/Fonts/` |
| ข้อความไม่เปลี่ยน | โหลดไฟล์ผิดลำดับ | ชื่อ PAK ต้องขึ้นต้น `z_` เพื่อ override game pak |
| Dialog บางฉากยังเป็น English | แก้แค่ Game.locres | ต้องแก้ Dialog.locres ด้วยสำหรับ quest dialogue |
| Game.locres ครอบคลุม item ไม่หมด | Ancestor/Boss entries ขาด | ตรวจ namespaces: Character_Names, Ancestor, EndGame_Boss |
| TTF magic check fail | copy ไฟล์เสียหาย | ตรวจ bytes 0-3 ต้องได้ `00 01 00 00` |
| repak version ไม่ตรง | PAK v11 format | ใช้ repak_cli 0.2.3+ ที่รองรับ v11 |
| ตัวอักษรทับซ้อน | font ไม่มี Thai GSUB | ใช้ Noto Sans Thai ที่มี GSUB/GPOS/GDEF ครบ |

---

## 9. Required Tools

| เครื่องมือ | หน้าที่ | ที่อยู่ |
|---|---|---|
| **repak_cli v0.2.3** | Unpack/Pack PAK v11 | `E:\Mod_Workspace\Tool\repak_cli\repak.exe` |
| **UnrealLocres** | Export/Import locres ↔ CSV | https://github.com/akintos/UnrealLocres |
| **Python 3.x** | Font slot automation | standard |
| **Shell.Application (PS)** | ยืนยัน font family name | Windows built-in |
| **HxD** | ตรวจ binary header | https://mh-nexus.de/en/hxd/ |

---

## 10. Extracted Assets

### Fonts

ตำแหน่ง: `E:\Mod_Workspace\Modding-Knowledge\Engines\Unreal_Engine_5\Games\Dragonkin_The_Banished\Assets\Fonts\`

| ไฟล์ | Font Family | ขนาด | MD5 | Verified |
|---|---|---|---|---|
| NotoSansThai-Regular.ttf | Noto Sans Thai Regular | 38.2 KB | 3B8502F4 | ✅ magic + Shell.Application |

> หมายเหตุ: มี 6 slots ในม็อดแต่ทั้งหมด identical — เก็บเพียง 1 ไฟล์

### Localization

ตำแหน่ง: `E:\Mod_Workspace\Modding-Knowledge\Engines\Unreal_Engine_5\Games\Dragonkin_The_Banished\Assets\Localization\`

| ไฟล์ | หน้าที่ | ขนาด | Strings | Keys |
|---|---|---|---|---|
| Dialog.locres | Quest/NPC dialogue | 522.8 KB | 1,631 | 1,648 |
| Game.locres | UI/items/names | 889.3 KB | 6,832 | 7,307 |

### Packages

ตำแหน่ง: `E:\Mod_Workspace\Modding-Knowledge\Engines\Unreal_Engine_5\Games\Dragonkin_The_Banished\Assets\Packages\`

- `z_DragonkinThai.pak` — 1,643 KB (original mod PAK สำหรับอ้างอิง)

---

*เอกสารนี้สร้างจากการวิเคราะห์ไบนารีจริงของม็อด v1.01*
*ทุกข้อมูลที่ไม่ระบุ "สันนิษฐาน" = ยืนยันจากหลักฐานโดยตรง*