# Mortal Shell 2 (Mortal Shell II) — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

> **Generated:** 2026-08-30
> **Analyst:** Rivet Engineer Advanced (Antigravity AI)
> **Mod:** Thai Mod by Lung Dear (ลุงเดียร์)
> **Status:** ✅ Complete (10/10 Mandatory Sections)

---

## 1. Overview

**Mortal Shell II** (Mortal Shell 2) เป็นเกม Souls-like Action RPG พัฒนาโดย **Cold Symmetry** บน **Unreal Engine 5** โดยใช้ Project Codename ภายในว่า **"Sparta"** (พบจากโฟลเดอร์ `MortalShell2/Content/Sparta/UI/Fonts/`) ม็อดภาษาไทยโดย **ลุงเดียร์ (Lung Dear)** มีลักษณะเฉพาะตัวอย่างมากใน Knowledge Base — เป็น **"Direct Game File Replacement"** ที่แก้ไขไฟล์ PAK ต้นฉบับของเกมโดยตรง เพราะเกมไม่รองรับ external mod PAK

**กลวิธีที่ไม่เหมือนใคร:**
1. **Ukrainian Language Slot Injection** — ใส่ข้อความไทยไว้ใน slot ภาษายูเครน (`uk/`) เพราะรายชื่อภาษาในเมนูถูก hardcode ในเกม
2. **Engine Font Disguise** — แทนที่ `NotoSansThai-Regular.ttf` (UE Engine Thai fallback) ด้วย **TH Baijam** แต่ใช้ชื่อไฟล์เดิม
3. **UI Font Slot Override** — แทนที่ฟอนต์ UI ต้นฉบับ (CrimsonText/Cormorant/PTSerif/Trajan) ด้วย TH Baijam ใน pakchunk4

**Mod Architecture Pattern:** Direct Game PAK Replacement (แก้ไข pakchunk0 + pakchunk4)
**Install Path:** ทับ `{GameInstall}/MortalShell2/Content/Paks/` โดยตรง

---

## 2. Technical Stack

| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Unreal Engine 5 |
| **Developer** | Cold Symmetry |
| **Project Codename** | **Sparta** (พบจากโฟลเดอร์ `MortalShell2/Content/Sparta/UI/Fonts/`) |
| **Archive Format** | UE5 Standard PAK v11 (ไม่มี IoStore) — 2 ไฟล์: pakchunk0 + pakchunk4 |
| **AES Encryption** | ❌ **ไม่มี** — EncryptIndex byte = `0x4F` ('O') เป็นส่วนของ compression method name "Oodle" ที่ embedded ใน footer, ไม่ใช่ AES flag. repak list/unpack ทำงานได้โดยไม่ต้องใช้ AES key ยืนยัน 100% |
| **Compression** | **Oodle** (พบ "Oodle" string ใน PAK footer ของทั้ง 2 ไฟล์) |
| **Mod Pattern** | **Direct Game PAK Replacement** — ไม่มีไฟล์ mod แยก เพราะเกมไม่รับ external PAK |
| **Thai Language Slot** | **Ukrainian (uk/)** — ข้อความไทยซ่อนใน slot `Game/uk/Game.locres` |
| **Font System** | Dual-layer: (1) Engine fallback replacement + (2) UI font slot replacement ใน pakchunk4 |
| **Thai Font Used** | **TH Baijam** — Regular, Bold, Italic (3 weights) |
| **Text System** | UE5 LocRes v3 (Binary) ใน pakchunk0 |
| **Text Encoding** | **UTF-16 LE** |
| **Mod Complexity** | ★★★★☆ (รูปแบบแปลกมาก: ไม่มี mod PAK, Ukrainian slot, engine font disguise, Oodle compression) |

---

## 3. โครงสร้างไฟล์ (File Architecture)

### 3.1 PAK Files (แก้ไขจาก Game Original)

```
MortalShell2\Content\Paks\
├── pakchunk0-Windows.pak     ← 558,837,039 bytes (532.95 MB)  ★ Engine + Game locres
│   Magic:        E1-12-6F-5A  @ offset 558,836,835 (from end: 204 bytes)
│   PAK Version:  11
│   Index Offset: 558,441,353 (0x21492389)
│   Index Size:   104,566 bytes
│   Compression:  Oodle (embedded in footer: "..Oodle..")
│   AES:          ❌ repak อ่านได้โดยไม่ใช้ key
│   Entries:      4,791 files
│   Thai content: uk/Game.locres (1,079 KB)
│   Thai font:    Engine/Content/Slate/Fonts/NotoSansThai-Regular.ttf (แท้จริงคือ TH Baijam)
│
└── pakchunk4-Windows.pak     ← 108,200,069 bytes (103.19 MB)  ★ UI Fonts
    Magic:        E1-12-6F-5A  @ offset 108,199,865 (from end: 204 bytes)
    PAK Version:  11
    Compression:  Oodle
    AES:          ❌
    Entries:      35 files (ufont ทั้งหมด)
    Thai content: 11 ufont เล็กๆ แทนที่ด้วย TH Baijam
```

### 3.2 PAK Footer v11 — Oodle Fingerprint

PAK v11 เก็บ compression method name ไว้ใน footer bytes ตำแหน่งเดียวกับที่ PAK v4 ใช้เป็น EncryptionKeyGUID:

```
Footer[44]:     0x4F = 'O'  ← ส่วนแรกของ "Oodle"
Footer[45-48]:  6F-64-6C-65 = "odle" ← ต่อกันเป็น "Oodle"
→ Footer ASCII: "...Oodle..."
```

**ข้อควรระวัง:** อย่าสับสน Oodle signature นี้กับ AES encryption flag — repak เปิดอ่านได้ปกติโดยไม่ต้องการ key

### 3.3 pakchunk0 — ไฟล์ที่เกี่ยวข้อง

```
pakchunk0-Windows.pak (4,791 entries):
├── Engine/Content/Slate/Fonts/NotoSansThai-Regular.ttf  ← ★ TH Baijam (disguised)
├── Engine/Content/Localization/Engine/*/Engine.locres   ← Engine UI strings (ไม่ได้แก้ไข)
├── MortalShell2/Content/Localization/Game/
│   ├── de/Game.locres, en/Game.locres, ...             ← ไม่ได้แก้ไข
│   └── uk/Game.locres                                  ← ★ ข้อความภาษาไทย (1,079 KB)
└── Engine/Content/Internationalization/icudt64l/
    ├── th_TH.res, th_TH_TRADITIONAL.res               ← ICU Thai locale data (เดิม)
    └── uk.res, uk_UA.res                              ← ICU Ukrainian locale data (เดิม)
```

### 3.4 pakchunk4 — Font Slot Map

```
pakchunk4-Windows.pak (35 entries):
├── [REPLACED: TH Baijam] CrimsonText-Regular.ufont     ← ★ TH Baijam Regular
├── [REPLACED: TH Baijam] CrimsonText-Bold.ufont        ← ★ TH Baijam Bold
├── [REPLACED: TH Baijam] CrimsonText-SemiBold.ufont    ← ★ TH Baijam Bold
├── [REPLACED: TH Baijam] CrimsonText-Italic.ufont      ← ★ TH Baijam Italic
├── [REPLACED: TH Baijam] Cormorant/CormorantUnicase-Regular.ufont  ← ★ TH Baijam Regular
├── [REPLACED: TH Baijam] Cormorant/CormorantUnicase-Bold.ufont     ← ★ TH Baijam Bold
├── [REPLACED: TH Baijam] PTSerif/PTSerif-Regular.ufont  ← ★ TH Baijam Regular
├── [REPLACED: TH Baijam] PTSerif/PTSerif-Bold.ufont     ← ★ TH Baijam Bold
├── [REPLACED: TH Baijam] PTSerif/PTSerif-Italic.ufont   ← ★ TH Baijam Italic
├── [REPLACED: TH Baijam] Trajan_Pro_Regular.ufont       ← ★ TH Baijam Regular
├── [REPLACED: TH Baijam] Trajan_Pro_SemiBold.ufont      ← ★ TH Baijam Bold
├── [UNCHANGED] NotoSans/NotoSansKR-*.ufont (×6)        ← Noto Sans KR (Korean)
├── [UNCHANGED] NotoSans/NotoSansSC-*.ufont (×6)        ← Noto Sans SC (Chinese Simplified)
├── [UNCHANGED] NotoSans/NotoSansTC-*.ufont (×6)        ← Noto Sans TC (Chinese Traditional)
└── [UNCHANGED] NotoSerif/NotoSerifJP-*.ufont (×6)     ← Noto Serif JP (Japanese)
```

---

## 4. Font Analysis

### 4.1 Thai Font: TH Baijam

| Property | Value |
|---|---|
| **Font Family** | TH Baijam (Regular, Bold, Italic) |
| **ผู้สร้าง** | NECTEC (National Electronics and Computer Technology Center, Thailand) |
| **License** | Thai national standard font — free for use (ดาวน์โหลดจาก NECTEC/NSTDA) |
| **Format** | TrueType (sfnt magic `00 01 00 00` = TTF v1.0) |
| **numTables** | 21 tables |
| **OpenType Tables** | GPOS, GSUB, OS/2, PCLT, VDMX, cmap, cvt, feat, fpgm, gasp, glyf, head, hhea, hmtx, kern, loca, maxp, morx, name, post, prep |
| **ขนาด** | Regular: 95.9 KB, Bold: 96.6 KB, Italic: 100.5 KB |
| **Thai rendering** | รองรับ Thai shaping ครบ (GSUB/GPOS tables) รวมสระลอย วรรณยุกต์ |

### 4.2 Font Deployment Strategy (2-Layer)

**Layer 1 — Engine Fallback Font (pakchunk0):**
```
Engine/Content/Slate/Fonts/NotoSansThai-Regular.ttf
  ↑ ชื่อไฟล์เดิมของ UE5 Engine Thai fallback
  ↑ แต่เนื้อหาถูกแทนที่เป็น TH Baijam Regular
  ↑ UE Engine โหลดไฟล์นี้เป็น fallback สำหรับ Thai Unicode characters
```

**Layer 2 — UI Font Slot Override (pakchunk4):**
```
เกมใช้ CrimsonText เป็นฟอนต์ UI หลัก
ม็อดเดอร์แทนที่ CrimsonText ทุก slot ด้วย TH Baijam:
  CrimsonText-Regular  → TH Baijam Regular
  CrimsonText-Bold     → TH Baijam Bold
  CrimsonText-SemiBold → TH Baijam Bold
  CrimsonText-Italic   → TH Baijam Italic
  (+ Cormorant, PTSerif, Trajan ก็ถูกแทนที่เช่นกัน)
```

### 4.3 ufont Format (pakchunk4)

ufont ทุกไฟล์ใน pakchunk4 ใช้ **Wrapped TTF (4-byte UE size header):**
```
Byte 0-3:  XX XX XX 00  ← uint32 LE = payload size (เช่น A4-7F-01-00 = 98,212 bytes)
Byte 4-7:  00-01-00-00  ← sfnt magic TrueType v1.0
Byte 8+:   [sfnt table directory + table data]
```
การสกัด TTF: ข้ามไป 4 bytes (`bytes[4:]`)

---

## 5. Text Analysis

### 5.1 uk/Game.locres — Thai Text File

| Property | Value |
|---|---|
| **Path ใน PAK** | `MortalShell2/Content/Localization/Game/uk/Game.locres` |
| **Magic (bytes 0-15)** | `0E-14-74-75-67-4A-03-FC-4A-15-90-9D-C3-37-7F-1B` |
| **Version** | 3 (UE LocRes v3) |
| **File Size** | 1,104,855 bytes (1,079 KB) |
| **StringTable Offset** | 495,485 bytes |
| **String Count** | **8,209 strings** |
| **Entry/Key Count** | **9,698 entries** |
| **Namespace Count** | **1,159 namespaces** |
| **Thai UTF-16 sequences** | 231,357 |

> README ระบุ "แปลด้วยมือทั้งหมด **9,477 ข้อความ**" (entry count ≈ 9,698 ใกล้เคียงกัน)

### 5.2 Language Slot Strategy

```
Options → Language → เลือก "ไทย (Lung Dear)"
  ถ้าไม่เจอ: หาภาษา "Ukrainian" แทน
  
เพราะ: รายชื่อภาษาในเมนูถูก hardcode ในตัวเกม
  → ไม่สามารถเพิ่มภาษาใหม่ได้
  → ม็อดเดอร์จึงใช้ slot Ukrainian (uk/) เป็นที่อยู่ไทย
  → ภาษาอื่นทุกภาษายังใช้งานได้ตามปกติ
```

### 5.3 ตัวอย่างข้อความจริง

```
"เมื่อตาย เจ้าจะฟื้นคืนชีพที่สัญญาณไฟ"
"กลูมที่เจ้าสะสมไว้จะร่วงหล่นอยู่ ณ จุดที่เจ้าตาย"
"หากเจ้าตายเป็นครั้งที่สองก่อนเก็บกลูมคืน มันจะเน่าเสียและสูญหายไปตลอดกาล"
```
(จาก tutorial/gameplay UI — game mechanics explanations)

### 5.4 Key Pattern

Key format ตัวอย่าง (จาก ASCII scan):
```
ElectricConduitFlavorText   ← item flavor text
```
เนื้อหาครอบคลุม: เมนู, ไอเทม, สกิล, บทสนทนา, เนื้อเรื่อง, คำบรรยาย

---

## 6. Cross-Engine Comparison

| Feature | **Mortal Shell 2** | **The Sinking City 2** | **Dragonkin: The Banished** |
|---|---|---|---|
| **Engine** | UE5 (Cold Symmetry) | UE5 (Frogwares) | UE5 (Bazooka Tango) |
| **PAK Version** | v11 | v4 | v11 |
| **IoStore** | ❌ | ✅ (.ucas/.utoc v8) | ❌ |
| **Mod Method** | **Direct PAK replace** | Add new PAK file | Add new PAK file |
| **Language Slot** | **Ukrainian (uk/)** | Thai slot (ปกติ) | Thai slot (ปกติ) |
| **Font Font** | **TH Baijam** | Noto Sans Thai | Noto Sans Thai Regular |
| **ufont format** | Wrapped TTF (offset 4) | Wrapped + Raw (2 variants) | Raw TTF (offset 0) |
| **Compression** | **Oodle** | ไม่มี | ไม่มี |
| **AES** | ❌ | ❌ | ❌ |
| **Strings** | 9,698 entries | 9,456 entries | 8,955 total |
| **Namespaces** | 1,159 | 90 | 332 |
| **Complexity** | ★★★★☆ | ★★★☆☆ | ★★☆☆☆ |

**ข้อสรุปเชิงเทคนิค:**

1. **Direct PAK Replacement Pattern:** เป็นรูปแบบเดียวใน Knowledge Base ที่ต้องแก้ไข game file โดยตรง เกิดจากเกม lock ไม่ให้ mount PAK เสริม — ผลกระทบ: ม็อดจะถูกลบทันทีเมื่อ verify files หรือ game update
2. **Oodle Compression Footer Signature:** PAK v11 เก็บ compression method "Oodle" ไว้ใน bytes เดียวกับ PAK v4 ที่ใช้เก็บ EncryptionKeyGUID — ทำให้ parser ที่ใช้ offset ผิดอาจอ่านว่ามี AES key ในทั้งที่ไม่มี
3. **Ukrainian Slot Injection:** เทคนิคนี้ใช้ได้กับเกมที่มีภาษา Ukrainian built-in แต่ไม่รองรับเพิ่มภาษาใหม่ — ค้นหา `uk/` ใน PAK ก่อนเสมอสำหรับเกมแนวนี้
4. **TH Baijam font:** เป็นฟอนต์แรกใน KB ที่ใช้ TH Baijam (ฟอนต์มาตรฐาน NECTEC) แทน Noto Sans Thai — ให้รูปแบบตัวอักษรที่เป็นเอกลักษณ์กว่า Noto

---

## 7. Pipeline — ขั้นตอนสร้างม็อด

### 7.1 สิ่งที่ต้องทำก่อน (Critical)

```
⚠️ สำรองไฟล์เดิมก่อนเสมอ:
   pakchunk0-Windows.pak  (532.95 MB)
   pakchunk4-Windows.pak  (103.19 MB)

เหตุผล: ม็อดเขียนทับไฟล์เกมโดยตรง
  → Verify files บน Steam/Epic จะลบม็อดทันที
  → Game update จะ overwrite ม็อด
```

### 7.2 Text Pipeline

```bash
# สกัด uk/Game.locres จาก pakchunk0
repak.exe unpack -o "./extract" -i "MortalShell2/Content/Localization/Game/uk" pakchunk0-Windows.pak

# Export เป็น CSV
UnrealLocres.exe Game.locres --export Game_Thai.csv

# (แก้ไข CSV ด้วย UTF-8 editor)

# Import กลับ
UnrealLocres.exe Game.locres --import Game_Thai.csv
```

### 7.3 Font Pipeline (pakchunk0 — Engine fallback)

```python
import shutil

def replace_engine_thai_font(new_font_path: str, extract_dir: str):
    """แทนที่ NotoSansThai-Regular.ttf ด้วยฟอนต์ใหม่"""
    # ไฟล์นี้เป็น Raw TTF (ไม่มี wrapper)
    dst = f"{extract_dir}/Engine/Content/Slate/Fonts/NotoSansThai-Regular.ttf"
    shutil.copy(new_font_path, dst)
    print(f"Engine font replaced: {dst}")
```

### 7.4 Font Pipeline (pakchunk4 — UI font slots)

```python
import struct, shutil

def make_wrapped_ufont(ttf_path: str, out_path: str):
    """สร้าง ufont แบบ Wrapped (4-byte size header) สำหรับ pakchunk4"""
    with open(ttf_path, 'rb') as f:
        data = f.read()
    assert data[:4] in (b'\x00\x01\x00\x00', b'OTTO')
    with open(out_path, 'wb') as f:
        f.write(struct.pack('<I', len(data)) + data)

# Slots ที่ต้องแทนที่ (11 slots):
THAI_SLOTS_REGULAR = ["CrimsonText-Regular", "CormorantUnicase-Regular",
                      "PTSerif-Regular", "Trajan_Pro_Regular"]
THAI_SLOTS_BOLD    = ["CrimsonText-Bold", "CrimsonText-SemiBold",
                      "CormorantUnicase-Bold", "PTSerif-Bold", "Trajan_Pro_SemiBold"]
THAI_SLOTS_ITALIC  = ["CrimsonText-Italic", "PTSerif-Italic"]
# Noto CJK slots (NotoSansKR/SC/TC, NotoSerifJP) — ไม่ต้องแก้
```

### 7.5 Repack และ Deploy

```powershell
# Repack pakchunk0 (ไม่รองรับ --include สำหรับ repack — ต้อง unpack ทั้งหมดก่อน)
# WARNING: pakchunk0 ขนาด 532MB จะใช้เวลาและ disk space มาก

# แนะนำ: ใช้ patch approach แทน — แก้เฉพาะ bytes ที่เปลี่ยนโดย hex editor/script

# Deploy: วางไฟล์ PAK ที่แก้ไขแล้วทับที่:
# {GameInstall}\MortalShell2\Content\Paks\pakchunk0-Windows.pak
# {GameInstall}\MortalShell2\Content\Paks\pakchunk4-Windows.pak
```

---

## 8. Troubleshooting

| ปัญหา | สาเหตุ | วิธีแก้ |
|---|---|---|
| ไม่เจอภาษาไทยในเมนู | ต้องเลือกภาษาในเมนู | Options → Language → "ไทย (Lung Dear)" หรือ "Ukrainian" |
| ม็อดหายไปเอง | Steam/Epic verify files | ต้องติดตั้งม็อดใหม่หลัง verify หรือ game update |
| ฟอนต์แสดงผิดเพี้ยน | pakchunk4 ไม่ถูก overwrite | ตรวจสอบว่า pakchunk4 ถูกแทนที่แล้ว |
| ตัวอักษรทับซ้อน | ufont wrapper ไม่ถูก | ตรวจว่า ufont มี 4-byte header (ไม่ใช่ raw copy) |
| repak ดู EncryptIndex = 79 ว่า AES | อ่าน footer offset ผิด | ไม่มี AES — "Oodle" string ใน footer ไม่ใช่ key GUID |
| repak repack ไม่ได้ขนาดเดิม | Oodle compression | ไฟล์ที่ repack อาจขนาดต่างไป — ทดสอบว่าเกมยังโหลดได้ |
| ม็อดถูกลบหลัง game update | game overwrites files | รอ mod version ใหม่ที่รองรับ game patch นั้น |

---

## 9. Required Tools

| เครื่องมือ | หน้าที่ | ที่อยู่ |
|---|---|---|
| **repak_cli v0.2.3** | Unpack PAK (สำหรับ extract/list ไม่มี repack ด้วย Oodle) | `E:\Mod_Workspace\Tool\repak_cli\repak.exe` |
| **UnrealLocres** | Export/Import uk/Game.locres ↔ CSV | https://github.com/akintos/UnrealLocres |
| **Python 3.x + struct** | สร้าง ufont Wrapped wrapper | standard |
| **Shell.Application (PS)** | ยืนยัน font family name | Windows built-in |
| **HxD** | ตรวจ/แก้ PAK binary โดยตรง | https://mh-nexus.de/en/hxd/ |

> **⚠️ ข้อจำกัด repak:** repak_cli 0.2.3 สามารถ **list และ unpack** PAK ที่ใช้ Oodle ได้ แต่การ **repack** กลับด้วย Oodle อาจต้องใช้เครื่องมืออื่น (UnrealPak จาก UE SDK หรือ custom tools)

---

## 10. Extracted Assets

### Fonts (สกัดจาก pakchunk0 + pakchunk4)

ตำแหน่ง: `E:\Mod_Workspace\Modding-Knowledge\Engines\Unreal_Engine_5\Games\Mortal_Shell_2\Assets\Fonts\`

| ไฟล์ | Font Family | ขนาด | Source | Verified |
|---|---|---|---|---|
| THBaijam.ttf | TH Baijam | 95.9 KB | pakchunk0: NotoSansThai-Regular.ttf (raw) | ✅ Shell.Application |
| THBaijam-Bold.ttf | TH Baijam Bold | 96.6 KB | pakchunk4: CrimsonText-Bold.ufont (skip 4) | ✅ Shell.Application |
| THBaijam-Italic.ttf | TH Baijam Italic | 100.5 KB | pakchunk4: CrimsonText-Italic.ufont (skip 4) | ✅ Shell.Application |

**หมายเหตุ font path:**
- Engine fallback (pakchunk0): **Raw TTF** (ไม่มี wrapper) — copy ตรงได้
- UI font slots (pakchunk4): **Wrapped TTF** (4-byte size header ก่อน TTF) — ต้อง skip 4 bytes เมื่อสกัด

### Localization

ตำแหน่ง: `E:\Mod_Workspace\Modding-Knowledge\Engines\Unreal_Engine_5\Games\Mortal_Shell_2\Assets\Localization\`

| ไฟล์ | Language Slot | ขนาด | Strings | Keys | Namespaces |
|---|---|---|---|---|---|
| Game_uk_Thai.locres | uk/ (Ukrainian slot = Thai) | 1,079 KB | 8,209 | 9,698 | 1,159 |

### ข้อสังเกต pakchunk4 — Unchanged CJK Fonts

Noto CJK fonts (KR/SC/TC, JP) ใน pakchunk4 **ไม่ได้ถูกแก้ไข** โดยม็อด — ยังเป็นฟอนต์ต้นฉบับของเกม:

| Font Group | Weight variants | ขนาดรวม |
|---|---|---|
| Noto Sans KR (Korean) | 6 weights | ~36.2 MB |
| Noto Sans SC (Chinese Simplified) | 6 weights | ~61.8 MB |
| Noto Sans TC (Chinese Traditional) | 6 weights | ~41.6 MB |
| Noto Serif JP (Japanese) | 6 weights | ~45.0 MB |

---

*เอกสารนี้สร้างจากการวิเคราะห์ไบนารีจริงของ PAK files ที่แก้ไขโดยม็อด Lung Dear*
*ทุกข้อมูลที่ไม่ระบุ "สันนิษฐาน" = ยืนยันจากหลักฐานโดยตรง*