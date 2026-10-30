# Far Cry 2 — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

> **Generated:** 2026-08-30
> **Analyst:** Rivet Engineer Advanced (Antigravity AI)
> **Mod:** Far Cry 2 Thai Language Mod v1.5 by Lung Dear (ลุงเดียร์)
> **Status:** ✅ Complete (10/10 Mandatory Sections)

---

## 1. Overview

**Far Cry 2** (2008) เป็นเกม Open-World FPS พัฒนาโดย **Ubisoft Montreal** บน **Dunia Engine** — engine ที่ Ubisoft พัฒนาขึ้นเองสำหรับซีรีส์ Far Cry ม็อดภาษาไทย v1.5 โดย **ลุงเดียร์ (Lung Dear)** แปลด้วยมือทั้งหมด **9,258 ข้อความ ใน 46 หมวด** และแก้ไขฟอนต์ด้วยเทคนิคพิเศษที่เรียกว่า **Glyph Remapping** — วาดทับตัวอักษรพิเศษที่ไม่ใช้งานในฟอนต์เดิมด้วยรูปร่างตัวอักษรไทย เพราะ Dunia Engine ไม่อนุญาตให้เพิ่ม Unicode codepoint ใหม่

**Mod Architecture Pattern:** Game File Replacement — แทนที่ `patch.dat` + `patch.fat` ในโฟลเดอร์ `Data_Win32/`

---

## 2. Technical Stack

| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Dunia Engine (Ubisoft, 2008) |
| **Developer** | Ubisoft Montreal |
| **Archive Format** | Dunia MAGM Container (`.dat`) + FAT2 v5 Index (`.fat`) |
| **Text Encoding** | **ISO-8859-1** — Dunia Engine ไม่รองรับ Unicode โดยตรง |
| **Font System** | **Glyph Remapping** — วาดทับ Private Use Area (PUA) codepoints ในฟอนต์เดิม |
| **Font Format** | ไม่ใช่ TTF/OTF แยกไฟล์ — embedded ใน XBT texture format ภายใน .dat |
| **AES Encryption** | ❌ ไม่มี |
| **Compression** | บางส่วน (ไฟล์ใน .dat บางส่วน raw, บางส่วน compressed) |
| **Install Method** | แทนที่ไฟล์ `Data_Win32/patch.dat` + `Data_Win32/patch.fat` โดยตรง |
| **Language Slot** | **English** — ม็อดแทนที่ข้อความภาษาอังกฤษ (ตั้งภาษาเกมเป็น English เพื่อใช้งาน) |
| **Mod Complexity** | ★★★☆☆ (Dunia Engine เฉพาะ, Glyph Remapping technique, ไม่มีเครื่องมือมาตรฐาน) |

---

## 3. โครงสร้างไฟล์ (File Architecture)

### 3.1 Mod Files

```
FarCry2-ThaiMod\
├── patch.dat          ← 29,738,736 bytes (28.36 MB)  ★ MAGM Container
│   Magic:     4D-41-47-4D  = "MAGM"
│   Contents:  222 entries (ไฟล์ game data รวม text + texture + font)
│   Encoding:  ISO-8859-1 ใน XML; ฟอนต์ embedded เป็น XBT/binary
│   Text data: uncompressed XML segments สลับกับ compressed binary data
│
├── patch.fat          ← 3,572 bytes (3.5 KB)  ★ FAT2 Index
│   Magic:     32-54-41-46  = "2TAF" (little-endian "FAT2")
│   Version:   5  (bytes 4-7 = 0x05000000)
│   Flags:     0x00030001
│   Entries:   222 files
│   Header:    20 bytes (magic 4 + version 4 + flags 4 + count 4 + padding 4)
│   Entry:     16 bytes each (offset:4 + compSize:4 + uncompSize:4 + flags:4)
│
├── INSTALL.bat        ← 3,405 bytes  Auto-installer script
├── UNINSTALL.bat      ← 2,368 bytes  Auto-uninstaller script
└── อ่านก่อนติดตั้ง.txt ← 9,061 bytes  README (Thai)
```

### 3.2 Install Path

```
ม็อดแทนที่ไฟล์ที่:
{GameInstall}\Data_Win32\patch.dat    ← ทับด้วย Thai mod
{GameInstall}\Data_Win32\patch.fat    ← ทับด้วย Thai FAT index

INSTALL.bat สำรองไฟล์เดิมเป็น:
{GameInstall}\Data_Win32\patch.dat.original_backup
{GameInstall}\Data_Win32\patch.fat.original_backup
```

Game folder สแกนอัตโนมัติ: `C-H:\Far Cry 2\`, Steam, Ubisoft Connect, `Program Files (x86)\`

### 3.3 MAGM Container Format

```
patch.dat (MAGM header):
[0-3]  Magic:  4D-41-47-4D = "MAGM"
[4-7]  ?: 0x0000CD41
[8-11] ?: 0x1EAB90AB
[12-15]: A7 00 00 00 = 167 (?)
[16-23]: hash/checksum data
...    compressed binary segments (interleaved with raw XML)

ท้ายไฟล์: CMagmaConfigUIResource XML manifest
<CMagmaConfigUIResource>
  <dependencies>
    <CTextureResource ID="ui\textures\hud_mp\*.xbt" crc_ID="..." />
    ...
  </dependencies>
</package>
```

### 3.4 FAT2 Index Format

```
FAT2 header (20 bytes):
[0-3]   Magic "2TAF" (= "FAT2" LE): 32-54-41-46
[4-7]   Version: 05-00-00-00 (v5)
[8-11]  Flags: 01-03-00-00
[12-15] Entry Count: DE-00-00-00 (= 222)
[16-19] Padding/unknown: 11-9D-12-01

FAT2 entry (16 bytes each, 222 entries):
[0-3]   Data offset in .dat (uint32 LE)
[4-7]   Compressed size
[8-11]  Uncompressed size
[12-15] Flags
```

---

## 4. Font Analysis

### 4.1 Glyph Remapping Technique (เทคนิคเฉพาะ Dunia Engine)

**ปัญหา:** Dunia Engine (2008) รองรับเฉพาะ Latin/Western character sets (ISO-8859-1 based) ไม่สามารถเพิ่ม Unicode codepoint ใหม่สำหรับภาษาไทยได้

**วิธีแก้ (Glyph Remapping):**
```
เกมต้นฉบับมีฟอนต์ที่มี "Private Use Area" characters หรือ
ตัวอักษรพิเศษที่ไม่ใช้งาน (เช่น เครื่องหมายพิเศษ, สัญลักษณ์เก่า)

ม็อดเดอร์:
1. ระบุ codepoints ที่ไม่ใช้งานในเกม
2. วาดรูปร่างตัวอักษรไทย (glyph) ทับ codepoints เหล่านั้น
3. แก้ไขข้อความใน localization files ให้ใช้ codepoints เหล่านั้น

ผล: เวลาเกมแสดงผล codepoint พิเศษ → เห็นเป็นตัวอักษรไทย
```

**ข้อจำกัดที่เกิดจาก Glyph Remapping:**
1. ถ้าเกมแสดง text ที่ม็อดไม่ได้แปล อาจเห็นตัวอักษรแปลกๆ (เพราะ codepoint นั้นถูก remap แล้ว)
2. Map Editor ไม่ได้แปล (เครื่องมือ developer ใช้ codepoints ต่างกัน)
3. บรรทัดยาวอาจมีช่องไฟกว้างผิดปกติ (Dunia ตัดบรรทัดที่ช่องว่างเท่านั้น, ไทยไม่มีช่องว่างระหว่างคำ)

### 4.2 Font Format

- ฟอนต์ใน Far Cry 2 / Dunia Engine เก็บเป็น **XBT (Texture) format** ภายใน `.dat`
- ไม่ใช่ TTF/OTF แยกไฟล์ — extracted ไม่ได้ด้วยวิธีปกติ
- ไม่มีไฟล์ฟอนต์ที่สกัดออกมาได้ใน KB นี้

### 4.3 Thai Character Coverage

- v1.5 แก้ตัวอักษรบางตัว (เช่น ไ ไม้มะลาย) ที่มีเส้นขีดเกินติดมาจาก glyph overlap
- ปรับขนาดตัวอักษรให้เท่ากันทุกตัว (v1.5)

---

## 5. Text Analysis

### 5.1 ข้อมูลรวม

| รายการ | ค่า |
|---|---|
| **จำนวนข้อความ** | **9,258 ข้อความ** (แปลด้วยมือ) |
| **หมวดหมู่** | **46 หมวด** |
| **ภาษาที่แปล** | English slot (ตั้งเกมเป็น English เพื่อใช้) |
| **Encoding ต้นฉบับ** | ISO-8859-1 ใน XML (Dunia Engine) |
| **Encoding ม็อด** | PUA codepoints (remap เป็น Thai glyphs) |

### 5.2 เนื้อหาที่แปล

**[เนื้อเรื่อง]**
- บทพูด/คำบรรยายใต้ภาพ ทั้งเกม: **6,315 ข้อความ**
- เป้าหมายภารกิจ + รายละเอียด: **566 ข้อความ**
- เทปเดอะแจ็คคัล + เทปรุ่นก่อน: **50 ข้อความ**
- ประวัติเพื่อนร่วมทาง 11 คน: **72 ข้อความ**
- บทส่งท้ายตอนจบเกม

**[เมนูและระบบ]**
- เมนูหลัก / เมนูหยุดเกม / ตั้งค่า / เซฟ-โหลด
- สมุดบันทึก, ร้านขายอาวุธ, ภารกิจท้าทาย
- ข้อความสอนเล่น / หน้าจอโหลด / ข้อความแจ้งเตือน

**[ผู้เล่นหลายคน]**
- เมนู, โหมดเล่น, ยศ, สถิติ, ข้อความระบบ

**[ไม่ได้แปล]**
- หน้าแก้ไขแผนที่ (Map Editor)
- ชื่อรุ่นอาวุธ (AK-47, Makarov, SPAS-12 ฯลฯ)
- ชื่อคน, ชื่อสตูดิโอ, เครื่องหมายการค้า

### 5.3 คำเตือนการตัดบรรทัด

Dunia Engine ตัดบรรทัดเฉพาะที่ **space character** เท่านั้น เนื่องจากภาษาไทยไม่มีช่องว่างระหว่างคำ ม็อดเดอร์แก้ปัญหาโดย **แทรก space character ที่ขอบคำ** — ทำให้ข้อความยาวบางบรรทัดมีช่องไฟกว้างกว่าปกติ

---

## 6. Cross-Engine Comparison

| Feature | **Far Cry 2** | **Mortal Shell 2** | **Dragonkin: The Banished** |
|---|---|---|---|
| **Engine** | **Dunia Engine** (Ubisoft 2008) | UE5 | UE5 |
| **Archive** | MAGM .dat + FAT2 .fat | UE5 PAK v11 | UE5 PAK v11 |
| **Text Encoding** | **ISO-8859-1** | UTF-16 LE | UTF-16 LE |
| **Font** | **Glyph Remapping (PUA)** | TH Baijam (TTF) | Noto Sans Thai (TTF) |
| **Font Extract** | ❌ ไม่ได้ (XBT embedded) | ✅ TTF สกัดได้ | ✅ TTF สกัดได้ |
| **AES** | ❌ | ❌ | ❌ |
| **Language Slot** | English | Ukrainian | Thai (ปกติ) |
| **Install Method** | แทนที่ patch.dat/fat | แทนที่ pakchunk0/4 | เพิ่ม mod PAK |
| **Verify Safe** | ✅ (มี backup/restore bat) | ❌ (verify ลบม็อด) | ✅ |
| **Complexity** | ★★★☆☆ | ★★★★☆ | ★★☆☆☆ |

**ข้อสรุปเชิงเทคนิค:**

1. **Glyph Remapping vs Font Replacement:** วิธี GlyphRemap ของ Dunia Engine เป็นวิธีเฉพาะตัว unique ใน KB — ต่างจาก UE5 ที่ swap TTF/ufont ได้โดยตรง Dunia Engine ปี 2008 lock encoding เป็น ISO-8859-1 ทำให้ต้องใช้เทคนิคนี้
2. **ISO-8859-1 Engine:** เครื่องมือ localization UE5 (UnrealLocres, repak) ใช้ไม่ได้กับ Dunia — ต้องใช้เครื่องมือ Dunia-specific
3. **FAT2 v5 + MAGM:** Archive format เฉพาะ Dunia Engine ซึ่งต้องการเครื่องมือ FC2 modding community (Gibbed Tools, Dunia Unpacker) — ไม่ใช่ repak
4. **Backup/Restore บาทสมบูรณ์:** INSTALL.bat สำรองอัตโนมัติ (ต่างจาก Mortal Shell 2 ที่ต้องทำเอง)

---

## 7. Pipeline — ขั้นตอนสร้างม็อด

### 7.1 เครื่องมือ (Dunia-Specific)

```
Dunia Engine ใช้เครื่องมือเฉพาะ:
  - Gibbed.Dunia.Unpack (ต้องหาจาก Far Cry 2 modding community)
  - หรือ DuniaModder / FC2 Modder tools
  ไม่สามารถใช้ repak_cli หรือ UnrealLocres
```

### 7.2 Text Pipeline

```
1. Unpack patch.dat ด้วย Gibbed.Dunia.Unpack:
   > Gibbed.Dunia.Unpack.exe patch.dat ./output/

2. แก้ไข localization XML ใน ./output/
   หาไฟล์ที่ชื่อ localization_en.xml หรือ strings_en.xml
   (encoding: ISO-8859-1 — บันทึกให้ถูก encoding!)

3. Repack:
   > Gibbed.Dunia.Pack.exe ./output/ patch_new.dat
   (FAT จะถูก regenerate อัตโนมัติเป็น patch_new.fat)
```

### 7.3 Font Pipeline (Glyph Remapping)

```
1. Unpack หา font XBT files ใน output/
2. ใช้ image editor แก้ไข glyph bitmap ของ codepoints ที่ไม่ใช้
   (เช่น ตัวอักษร Latin Extended ที่ Far Cry 2 ไม่ใช้)
3. Replace remap codepoints ใน text files ให้ตรงกับ glyph ที่แก้ไว้
4. Repack กลับ

หมายเหตุ: เทคนิคนี้ต้องการความเข้าใจ font glyph และ Dunia's character mapping
```

### 7.4 Deploy

```
copy patch.dat  "{GameInstall}\Data_Win32\patch.dat"
copy patch.fat  "{GameInstall}\Data_Win32\patch.fat"
```

---

## 8. Troubleshooting

| ปัญหา | สาเหตุ | วิธีแก้ |
|---|---|---|
| ตัวหนังสือยังเป็นภาษาอังกฤษ | ตั้งภาษาเกมผิด | ต้องตั้งภาษาเกมเป็น English |
| ตัวหนังสือเป็นสัญลักษณ์แปลก | ไฟล์คัดลอกไม่ครบ | รัน INSTALL.bat ใหม่อีกครั้ง |
| เกมเปิดไม่ขึ้น | ม็อดไม่ compatible | รัน UNINSTALL.bat แล้วทดสอบ |
| ตัวอักษรบางตัวมีเส้นขีดเกิน | Glyph overlap ใน font | v1.5 แก้แล้ว — ตรวจว่าใช้เวอร์ชันล่าสุด |
| ช่องไฟกว้างผิดปกติ | ข้อจำกัด Dunia word wrap | เป็นปกติ — engine ตัดที่ space เท่านั้น |
| ไฟล์สำรองหาย | ลืม backup | ใช้ Steam/Epic Verify/Repair |
| Map Editor แสดงอักษรแปลก | ไม่ได้แปล Map Editor | เป็นที่ทราบ — Map Editor ไม่ได้รวมในม็อด |

---

## 9. Required Tools

| เครื่องมือ | หน้าที่ | ที่อยู่ |
|---|---|---|
| **Gibbed.Dunia.Unpack** | Unpack MAGM .dat | Far Cry 2 modding community / GitHub |
| **Gibbed.Dunia.Pack** | Repack .dat → patch.fat | Far Cry 2 modding community |
| **Image Editor (GIMP/PS)** | แก้ไข glyph bitmap ใน XBT | ใช้ plugin XBT converter |
| **Notepad++ (ISO-8859-1)** | แก้ไข XML text (encoding สำคัญมาก) | https://notepad-plus-plus.org |
| **HxD** | ตรวจ binary header | https://mh-nexus.de/en/hxd/ |
| **INSTALL.bat / UNINSTALL.bat** | Deploy/restore (in-mod) | ในชุดม็อด |

---

## 10. Extracted Assets

### ⚠️ ไม่มีไฟล์ Font แยกสกัดได้

ฟอนต์ใน Far Cry 2 ถูก embed เป็น **XBT texture format** ภายใน MAGM container — ไม่ใช่ TTF/OTF แยกไฟล์ ต้องใช้ Gibbed.Dunia.Unpack เพื่อสกัด และแปลง XBT เป็น image format ก่อน

### Packages (Reference)

ตำแหน่ง: `E:\Mod_Workspace\Modding-Knowledge\Engines\Dunia_Engine\Games\Far_Cry_2\Assets\Packages\`

| ไฟล์ | ขนาด | หมายเหตุ |
|---|---|---|
| patch.fat | 3.5 KB | FAT2 v5 index (222 entries) |
| INSTALL.bat | 3.4 KB | Auto-installer script |
| UNINSTALL.bat | 2.4 KB | Auto-uninstaller/restore script |

> patch.dat (28.36 MB) ไม่ได้เก็บใน KB เพราะขนาดใหญ่เกินไป สามารถดูจากไฟล์ม็อดต้นฉบับได้

### Summary

| รายการ | รายละเอียด |
|---|---|
| ข้อความแปล | 9,258 ข้อความ / 46 หมวด |
| ฟอนต์ | Glyph-remapped version ของ Dunia Engine font (ไม่สกัดแยกได้) |
| ไฟล์ติดตั้ง | patch.dat (MAGM) + patch.fat (FAT2 v5) → Data_Win32/ |
| ภาษา | English slot |

---

*เอกสารนี้สร้างจากการวิเคราะห์ไบนารีจริงของ patch.dat + patch.fat และ README ของม็อด v1.5*
*เนื่องจาก Dunia Engine archive format เฉพาะ บางส่วนต้องพึ่ง community tools ในการแกะออก*