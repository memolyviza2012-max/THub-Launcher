# Ghostrunner — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
เอกสารนี้วิเคราะห์กลไกม็อดภาษาไทยของ **Ghostrunner** อย่างละเอียดที่สุด เกมนี้สร้างด้วย **Unreal Engine 4** และใช้ระบบ localization มาตรฐานของ UE4 (`LocRes` format) ม็อดนี้ใช้กลยุทธ์ **Patch PAK Override** (`_P.pak`) ที่เป็นวิธีมาตรฐานและสะอาดที่สุดสำหรับเกม UE4 — ไม่ต้องแก้ไขไฟล์เกมเดิมใดๆ เลย

---

## 2. Technical Stack

| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Unreal Engine 4 |
| **Localization System** | UE4 LocRes (`.locres` — binary localization resource) |
| **Archive Format** | UE4 PAK v3 (Magic: `E1 12 6F 5A`) + Zlib Compression |
| **Signature** | RSA Block-Level Signatures (`.sig` — 1.5 MB, ~2,997 block hashes) |
| **Text Encoding** | UTF-16LE (มาตรฐาน UE4 FString) |
| **Font Format** | `.ufont` (UE4 Font Asset — wrapped TTF/OTF) |
| **Mod Strategy** | **Patch PAK** (`_P.pak`) — override ไม่ต้องแก้ไฟล์เดิม |
| **Mod Complexity** | ★★★☆☆ (ต้องใช้ UnrealPak + LocRes editor แต่มี workflow ชัดเจน) |

---

## 3. โครงสร้างไฟล์ (File Architecture)

### 3.1 ม็อดประกอบด้วย 2 ไฟล์
```
Content/
└── Paks/
    ├── GHOSTRUNNER_THAI_1.0_P.pak   ← 699 KB (Patch PAK)
    └── GHOSTRUNNER_THAI_1.0_P.sig   ← 1.5 MB (RSA Signature)
```

### 3.2 เนื้อหาภายใน PAK (14 ไฟล์)

| # | Path | ชนิด | หน้าที่ |
|---|---|---|---|
| 1-8 | `Fonts/JOVANNY_LEMONAD_-_BENDER*.ufont` (×8) | Font | ฟอนต์ Bender ทุก weight |
| 9 | `Localization/Ghostrunner/en/Ghostrunner.locres` | LocRes | **ข้อความแปลไทยทั้งหมด** |
| 10-11 | `Visual/Game_UI/MainMenu/EndSlate/gr_logo_clean.*` | Texture | โลโก้หน้าจบเกม |
| 12-14 | `Visual/Game_UI/MainMenu/Logo_1K.*` | Texture | โลโก้เมนูหลัก |

### 3.3 สรุปเนื้อหา
| ประเภท | จำนวน | รายละเอียด |
|---|---|---|
| **Fonts** | 8 ไฟล์ | Bender font family ครบทุก weight (Regular, Bold, Italic, Light, Black + ชุดผสม) |
| **Localization** | 1 ไฟล์ | `Ghostrunner.locres` — ข้อความแปลทั้งหมด |
| **Visual** | 5 ไฟล์ | โลโก้เกมที่แก้ไข (อาจเพิ่มข้อความ "ภาษาไทย" หรือแก้ไขเป็นเวอร์ชันไทย) |

---

## 4. PAK Format — โครงสร้าง Archive

### 4.1 UE4 PAK v3 Structure
```
┌─────────────────────────────────────────┐
│ Compressed Data Blocks (Zlib)           │  ← ไฟล์ต่างๆ ถูกบีบอัดด้วย Zlib
│   Block 0: BENDER-BLACK.ufont           │
│   Block 1: BENDER-BLACKITALIC.ufont     │
│   Block 2: BENDER-BOLD.ufont            │
│   ...                                    │
│   Block N: Ghostrunner.locres           │
│   Block N+1: gr_logo_clean.uasset/uexp │
│   Block N+2: Logo_1K.uasset/uexp/ubulk │
├─────────────────────────────────────────┤
│ PAK Index (at offset 713,800)           │  ← ตาราง index ของไฟล์ทั้ง 14 รายการ
│   Mount Point: ../../../Ghostrunner/... │
│   Entry Count: 14                       │
│   [name + offset + sizes + SHA1] × 14   │
├─────────────────────────────────────────┤
│ PAK Footer (last 44 bytes)              │  ← footer ระบุตำแหน่ง index
│   Magic: E1 12 6F 5A                    │
│   Version: 3                            │
│   Index Offset: 713,800                 │
│   Index Size: 2,378                     │
└─────────────────────────────────────────┘
```

### 4.2 Mount Point
```
../../../Ghostrunner/Content/
```
Mount point นี้บอก UE4 ว่าให้ map ไฟล์ใน PAK ไปที่ root ของ Content directory — เมื่อเกมโหลด PAK ที่มี `_P` suffix จะ **override** ไฟล์เดิมที่ path ตรงกัน

### 4.3 Compression
- **Method:** Zlib (compression method = 1)
- **Block-level:** แต่ละ entry ถูกบีบอัดเป็น block ย่อยๆ
- **Ratio:** ประมาณ 2:1 ถึง 3:1 (เช่น font 170KB → 68KB compressed)

---

## 5. Localization Format — LocRes

### 5.1 UE4 LocRes คืออะไร?
**LocRes** (`.locres`) เป็น binary format มาตรฐานของ Unreal Engine สำหรับเก็บข้อความแปลภาษา ใช้ในเกม UE4/UE5 ทุกเกม

### 5.2 LocRes Structure
```
┌───────────────────────────┐
│ Magic (16 bytes)          │  0E 14 74 75 67 4A 03 FC 4A 15 90 9D C3 37 7F 1B
│ Version (1 byte)          │
│ Localized String Count    │
├───────────────────────────┤
│ Namespace Table           │  ← กลุ่มของ key (เช่น "Game", "ST_Chapter1")
│   ├── Namespace 1         │
│   │   ├── Key 1 → Value   │  ← Key = source hash, Value = translated string
│   │   ├── Key 2 → Value   │
│   │   └── ...              │
│   ├── Namespace 2         │
│   │   └── ...              │
│   └── ...                  │
└───────────────────────────┘
```

### 5.3 Text Encoding
- ข้อความทั้งหมดเก็บเป็น **UTF-16LE** (Little Endian) — มาตรฐานของ UE4 FString
- ภาษาไทยอยู่ใน Unicode range `U+0E01` ถึง `U+0E7F`
- ในหน่วยความจำ: ตัวอักษรไทย `ก` = byte sequence `01 0E` (UTF-16LE)

### 5.4 Language Slot Strategy
ม็อดใช้ path `Localization/Ghostrunner/en/Ghostrunner.locres` — **ทับ locale English (`en`) โดยตรง**:
- เมื่อผู้เล่นเลือกภาษา English → เกมโหลด `en/Ghostrunner.locres` → แสดงเป็นภาษาไทย
- ข้อเสีย: ผู้เล่นไม่สามารถสลับกลับไปภาษาอังกฤษได้ (ต้องลบ PAK ออก)

---

## 6. Font System — ระบบฟอนต์

### 6.1 Bender Font Family
เกม Ghostrunner ใช้ฟอนต์ **Bender** ของ Jovanny Lemonad เป็นฟอนต์หลัก ม็อดแทนที่ font file ทั้ง **8 weights**:

| ไฟล์ | Weight |
|---|---|
| `JOVANNY_LEMONAD_-_BENDER.ufont` | Regular |
| `JOVANNY_LEMONAD_-_BENDER-BLACK.ufont` | Black |
| `JOVANNY_LEMONAD_-_BENDER-BLACKITALIC.ufont` | Black Italic |
| `JOVANNY_LEMONAD_-_BENDER-BOLD.ufont` | Bold |
| `JOVANNY_LEMONAD_-_BENDER-BOLDITALIC.ufont` | Bold Italic |
| `JOVANNY_LEMONAD_-_BENDER-ITALIC.ufont` | Italic |
| `JOVANNY_LEMONAD_-_BENDER-LIGHT.ufont` | Light |
| `JOVANNY_LEMONAD_-_BENDER-LIGHTITALIC.ufont` | Light Italic |

### 6.2 กลยุทธ์ฟอนต์
ฟอนต์ Bender เดิม **ไม่รองรับอักษรไทย** ม็อดจึงต้อง:
1. เอาฟอนต์ไทย (เช่น Noto Sans Thai, Sarabun, Kanit) มา **merge glyph** กับ Bender
2. หรือแทนที่ Bender ด้วยฟอนต์ที่รองรับทั้งละตินและไทย
3. Wrap เป็น `.ufont` (UE4 Font Asset) ที่ชี้ไปยัง TTF/OTF ข้างใน

### 6.3 UFont Format
`.ufont` เป็น **UE4 Asset** ที่ภายในประกอบด้วย:
- `.uasset` header (UE4 object serialization)
- TTF/OTF raw data ฝังอยู่ข้างใน
- Font metadata (face name, hinting, fallback)

---

## 7. Visual Assets — โลโก้ที่แก้ไข

### 7.1 โลโก้ 2 ชุด
| Asset | ขนาด | หน้าที่ |
|---|---|---|
| `gr_logo_clean.uasset/uexp` | Logo clean | โลโก้หน้าจบเกม (End Slate) |
| `Logo_1K.uasset/uexp/ubulk` | 1K Logo | โลโก้เมนูหลัก |

ม็อดอาจแก้ไขโลโก้เพื่อ:
- เพิ่มข้อความ "ภาษาไทย" หรือ "Thai Edition"
- แก้ไข subtitle ใต้โลโก้

### 7.2 UBulk Format
ไฟล์ `.ubulk` เก็บ **bulk data** (texture pixels) แยกจาก `.uasset` (metadata) — เป็น UE4 streaming data format

---

## 8. Patch PAK System (_P suffix)

### 8.1 วิธีการทำงาน
UE4 มีระบบ **PAK Priority** ในตัว:
1. เกมโหลด PAK files ตามลำดับตัวอักษร
2. PAK ที่มี suffix `_P` (Patch) จะถูกโหลด **หลังสุด**
3. ถ้ามีไฟล์ path เดียวกัน → PAK ที่โหลดทีหลังจะ **override** ไฟล์เดิม

### 8.2 ข้อดีของ Patch PAK
- ✅ **ไม่ต้องแก้ไขไฟล์เกมเดิม** — ติดตั้งง่าย แค่คัดลอก PAK+SIG ไปวาง
- ✅ **ถอนการติดตั้งง่าย** — แค่ลบ 2 ไฟล์
- ✅ **อัปเดตม็อดง่าย** — แค่แทนที่ PAK ใหม่
- ✅ **ไม่กระทบ game integrity** — Steam/EGS ไม่ตรวจจับว่าไฟล์เกมถูกแก้ไข

### 8.3 SIG File (RSA Signature)
| ฟิลด์ | ค่า |
|---|---|
| **Magic** | `0x73832DAA` (UE4 PAK Signature) |
| **Version** | 1 |
| **Encrypted Hash Size** | 512 bytes (RSA-4096) |
| **Total Size** | 1.5 MB (~2,997 block-level signatures) |

SIG file ใช้สำหรับ **integrity verification** — เกมบางเกมตรวจสอบว่า PAK ถูก sign ด้วย key ที่ถูกต้องหรือไม่ ถ้าเกมบังคับใช้ signature verification จะต้อง bypass ด้วยวิธีอื่น (เช่น engine patch)

---

## 9. Complete Pipeline — ขั้นตอนสร้างม็อด

```
ขั้นตอนที่ 1: แตก LocRes จาก PAK ของเกม
    ใช้เครื่องมือ: UnrealPak.exe (มาพร้อม UE4) หรือ QuickBMS
    แตก Localization/Ghostrunner/en/Ghostrunner.locres
        ↓
ขั้นตอนที่ 2: แก้ไข LocRes
    ใช้เครื่องมือ: UE4 LocRes Editor หรือ LocResEditor (community tool)
    - เปิด .locres → จะเห็นตาราง Namespace → Key → Value
    - แปลค่า Value จากอังกฤษเป็นไทย
    - บันทึกเป็น .locres ใหม่
        ↓
ขั้นตอนที่ 3: เตรียมฟอนต์ไทย
    - เอาฟอนต์ .ttf ที่รองรับอักษรไทยมา merge กับ Bender
    - Wrap เป็น .ufont ด้วย UE4 Editor (หรือ hex edit ไฟล์ .ufont เดิม)
    - สร้าง .ufont ครบ 8 weights
        ↓
ขั้นตอนที่ 4: แก้ไขโลโก้ (ถ้าต้องการ)
    - แก้ไข texture ด้วย image editor
    - Import กลับเป็น .uasset/.uexp/.ubulk
        ↓
ขั้นตอนที่ 5: Pack เป็น Patch PAK
    ใช้ UnrealPak.exe:
    UnrealPak.exe GHOSTRUNNER_THAI_1.0_P.pak -Create=filelist.txt -compress
    (สร้าง file list ที่ระบุ path ของทุกไฟล์ตาม mount point)
        ↓
ขั้นตอนที่ 6: สร้าง SIG file
    ใช้ UnrealPak.exe หรือ signing tool
    (ถ้าเกมไม่บังคับ signature → อาจข้ามขั้นตอนนี้ได้)
        ↓
ขั้นตอนที่ 7: วางไฟล์
    คัดลอก .pak + .sig ไปที่:
    {GameInstall}/Ghostrunner/Content/Paks/
        ↓
เสร็จสิ้น! เปิดเกม → เลือก English → แสดงเป็นภาษาไทย
```

---

## 10. Required Tools

| เครื่องมือ | หน้าที่ | ระดับความจำเป็น |
|---|---|---|
| **UnrealPak** (มากับ UE4 SDK) | Pack/Unpack `.pak` | ✅ จำเป็น |
| **UE4 LocRes Editor** | แก้ไข `.locres` binary | ✅ จำเป็น |
| **QuickBMS** + UE4 script | ทางเลือกในการ unpack `.pak` | ⚡ ทางเลือก |
| **UE4 Editor** | สร้าง `.ufont` assets | ✅ จำเป็น (สำหรับฟอนต์) |
| **Font Merge Tool** (FontForge) | Merge glyph ไทยเข้า Bender | ✅ จำเป็น |
| **Image Editor** | แก้ไขโลโก้ | ⚡ ถ้าต้องการแก้โลโก้ |

---

## 11. สถิติม็อด

| ข้อมูล | จำนวน |
|---|---|
| **ไฟล์ที่ม็อด** | 2 ไฟล์ (.pak + .sig) |
| **เนื้อหาภายใน PAK** | 14 ไฟล์ |
| **ขนาด PAK** | 699 KB |
| **ขนาด SIG** | 1.5 MB |
| **PAK Version** | 3 |
| **Compression** | Zlib (block-level) |
| **Fonts ที่แทนที่** | 8 ไฟล์ (Bender family ครบทุก weight) |
| **LocRes files** | 1 ไฟล์ (`Ghostrunner.locres`) |
| **Visual assets** | 5 ไฟล์ (โลโก้ 2 ชุด) |
| **Mount Point** | `../../../Ghostrunner/Content/` |

---

## 12. เปรียบเทียบกับเกม UE4 อื่น

Ghostrunner ใช้ **วิธีมาตรฐานที่สุด** สำหรับม็อดภาษา UE4:

| เกม | Engine | Archive | Localization | Font | Mod Method |
|---|---|---|---|---|---|
| **Ghostrunner** | UE4 | PAK v3 | LocRes (binary) | .ufont | Patch PAK `_P` |
| Dead Island 2 | UE4 | PAK v11 | LocRes | .ufont | Patch PAK `_P` |
| SpaceHulk Deathwing | UE4 | PAK | LocRes + DataTable | .ufont | Patch PAK |

**Knowledge Reuse:** ถ้าเข้าใจ Ghostrunner แล้ว สามารถนำไปใช้กับเกม UE4 อื่นๆ ได้เกือบทุกเกม — ต่างกันแค่ PAK version และ encryption

---

## 13. Conclusion

ม็อดภาษาไทยของ **Ghostrunner** เป็นตัวอย่างที่สมบูรณ์แบบของ **"UE4 Patch PAK Localization Mod"**:

1. **Patch PAK (`_P` suffix)** — วิธีที่ cleanest สำหรับ UE4 mods, ไม่ต้องแก้ไฟล์เกมเดิม, ติดตั้ง/ลบง่าย
2. **LocRes Binary Format** — binary format มาตรฐานของ UE4 ที่ต้องใช้ dedicated editor, เก็บข้อความเป็น UTF-16LE
3. **Full Font Family Replacement** — แทนที่ Bender font ครบทั้ง 8 weights เพื่อรองรับ glyph ภาษาไทย
4. **RSA Signature** — SIG ขนาด 1.5MB ที่ sign ทุก compression block ด้วย RSA-4096
5. **Logo Customization** — แก้ไขโลโก้เกมเพื่อให้ผู้เล่นรู้ว่ากำลังเล่นเวอร์ชันภาษาไทย
6. **เทคนิคนี้เป็นพื้นฐานของ UE4 modding ทั้งหมด** — เข้าใจระบบนี้แล้วใช้กับเกม UE4 อีกหลายร้อยเกมได้
