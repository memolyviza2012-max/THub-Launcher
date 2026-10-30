# Ryse: Son of Rome — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Ryse: Son of Rome is an action-adventure game developed by **Crytek** using **CryEngine 3** (CRYENGINE). The Thai localization mod uses a classic **CryEngine Localization Override** architecture — replacing the game's `English_xml.pak` in the `Localization` folder. The pak file is a standard **ZIP archive** containing CryXmlB (Binary XML) localization files and Scaleform GFX font assets. This is the same CryEngine localization pipeline used by Kingdom Come Deliverance 1 & 2, making it familiar territory.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | CryEngine 3 (CRYENGINE) |
| **Developer** | Crytek |
| **Mod Author** | ไม่ระบุ |
| **Archive Format** | `.pak` (ZIP archive, Magic: `PK\x03\x04`) |
| **Font System** | Scaleform GFX (`.gfx`, Magic: `CFX`, zlib compressed) |
| **Thai Font** | **Sabon LT Pro** (embedded in GFX as vector outlines) |
| **Text System** | CryXmlB (Binary XML, Magic: `CryXmlB\x00`) |
| **Text Encoding** | UTF-8 |
| **Mod Complexity** | ★★★☆☆ (CryEngine standard localization + Scaleform GFX font) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
ม็อดนี้ใช้วิธี **Single-PAK Override** เพียงแค่วางไฟล์ `.pak` เดียวลงในโฟลเดอร์ Localization ของเกม:

```text
Ryse Son of Rome/
└── Localization/
    └── English_xml.pak                 (38.4 MB — ZIP archive, 16 files)
        │
        ├── [Text: CryXmlB Binary XML — 11 ไฟล์]
        │   ├── Ryse_achievements.xml    (100 KB — ความสำเร็จ)
        │   ├── Ryse_comic.xml           (222 KB — เนื้อเรื่องการ์ตูน)
        │   ├── Ryse_credits.xml         (799 KB — เครดิต ⚠️ ไม่มีภาษาไทย)
        │   ├── Ryse_hud.xml             (84 KB — HUD/UI)
        │   ├── Ryse_menus.xml           (353 KB — เมนู)
        │   ├── Ryse_messages.xml        (698 KB — ข้อความในเกม)
        │   ├── Ryse_multiplayer.xml     (1.05 MB — Multiplayer ⚠️ ไม่มีภาษาไทย)
        │   ├── Ryse_subtitles.xml       (201 KB — ซับไตเติ้ล)
        │   ├── Ryse_system.xml          (66 KB — ระบบ)
        │   ├── Ryse_upgrades.xml        (259 KB — อัพเกรด)
        │   └── text_platformspecific.xml (19 KB — ⚠️ ไม่มีภาษาไทย)
        │
        ├── [Dialog Recording Lists — 3 ไฟล์]
        │   ├── dialog_recording_list.xml      (9.3 MB — บทบันทึกเสียง SP)
        │   ├── dialog_ai_recording_list.xml   (26.7 MB — บทบันทึกเสียง AI)
        │   └── dialog_mp_recording_list.xml   (216 KB — บทบันทึกเสียง MP)
        │
        └── [Font: Scaleform GFX — 2 ไฟล์]
            ├── HUD_Font_LocFont.gfx           (31 KB — CFX v8, ฟอนต์หลัก)
            └── HUD_Font_LocFont_glyphs.gfx    (81 KB — CFX v8, Glyph Atlas)
```

---

## 4. Font Analysis

### 4.1 Scaleform GFX Font (CFX Compressed)
- **Magic Bytes:** `CFX` (Compressed GFX / Scaleform Flash)
- **Version:** 8
- **Inner Font:** **Sabon LT Pro** (พบชื่อฟอนต์ฝังอยู่ใน GFX decompressed data)
- **HUD_Font_LocFont.gfx:** 31 KB compressed → 44 KB decompressed (ข้อมูลฟอนต์หลัก: Font metrics, kerning pairs, character mapping)
- **HUD_Font_LocFont_glyphs.gfx:** 81 KB compressed → 126 KB decompressed (Glyph shapes เป็นภาพ vector outlines ของตัวอักษร)

### 4.2 Extraction Status
- **ไม่สามารถสกัดเป็น TTF ได้** เนื่องจาก Scaleform GFX เก็บฟอนต์เป็น **Vector Outline Shapes** (DefineFont/DefineShape SWF tags) ไม่ใช่ Raw TTF อย่าง UE4 `.ufont`
- ต้องใช้โปรแกรม **Scaleform GFx Export** หรือ **RAD Game Tools** ในการสร้าง GFX ใหม่
- ฟอนต์ Sabon LT Pro เป็นฟอนต์ลิขสิทธิ์ของ Linotype (ไม่ใช่ Open Source)

---

## 5. Text Analysis

### 5.1 CryXmlB (Binary XML)
เกมนี้ใช้ระบบ **CryXmlB** — ไฟล์ XML ที่ถูกคอมไพล์เป็น Binary โดย CryEngine (Magic: `CryXmlB\x00`) 
- ข้อความภาษาไทยถูกเข้ารหัสเป็น **UTF-8** ภายในโครงสร้าง Binary XML
- สามารถดึงข้อมูลออกมาได้ด้วยโปรแกรมอย่าง `CryXmlBReader` หรือสคริปต์ Python

### 5.2 สถิติข้อความ
| ไฟล์ | Thai Chars | หมายเหตุ |
|---|---|---|
| dialog_recording_list.xml | 69,484 | บทบันทึกเสียง (ใหญ่สุด) |
| dialog_ai_recording_list.xml | 56,876 | บทบันทึกเสียง AI |
| Ryse_messages.xml | 41,381 | ข้อความในเกม |
| Ryse_subtitles.xml | 15,571 | ซับไตเติ้ล |
| Ryse_upgrades.xml | 15,290 | ระบบอัพเกรด |
| Ryse_menus.xml | 14,084 | เมนู |
| Ryse_comic.xml | 10,764 | เนื้อเรื่องการ์ตูน |
| อื่นๆ | 9,099 | achievements, system, HUD, MP dialog |
| **รวม** | **232,549** | — |

### 5.3 ตัวอย่างข้อความไทยในเกม
```
"เจ้าเป็นใคร?"
"เหตุใดเรื่องนี้จึงเกิดขึ้น?"
"บิดาของข้าเป็นวีรบุรุษแห่งโรม"
"บิดาของเจ้าเป็นทั้งแม่ทัพผู้ยิ่งใหญ่และวุฒิสมาชิกที่ได้รับความนิยม"
```

---

## 6. Cross-Engine Comparison
เปรียบเทียบกับเกม CryEngine อื่นๆ ในคลัง:

| Feature | Ryse: Son of Rome | KCD1 | KCD2 |
|---|---|---|---|
| **Engine** | CryEngine 3 | CryEngine (modded) | CryEngine (modded) |
| **PAK Format** | ZIP (`PK\x03\x04`) | ZIP (`PK\x03\x04`) | ZIP (`PK\x03\x04`) |
| **XML Format** | CryXmlB (Binary) | Plain XML | Plain XML |
| **Font System** | Scaleform GFX (CFX) | Scaleform GFX | Scaleform GFX |
| **Text Encoding** | UTF-8 | UTF-8 | UTF-8 |
| **Thai Chars** | 232K | 3.31M | 5.17M |
| **Complexity** | ★★★☆☆ | ★★★☆☆ | ★★★☆☆ |

**จุดเด่น:** Ryse ใช้ CryXmlB (Binary XML) แทน Plain XML ทำให้ไฟล์มีขนาดเล็กกว่า แต่แก้ไขยากกว่า (ต้องมี parser เฉพาะ)
**จุดร่วม:** ระบบ Localization PAK, Scaleform GFX font, และ UTF-8 encoding เหมือนกันหมดในตระกูล CryEngine

---

## 7. Pipeline — ขั้นตอนสร้างม็อด

1. **Extract PAK:** แตกไฟล์ `English_xml.pak` ด้วย 7-Zip หรือ Python `zipfile`
2. **Decode CryXmlB:** ใช้ CryXmlB reader แปลงเป็น Plain XML เพื่อแก้ไข
3. **Translate:** แปลข้อความ UTF-8 ในไฟล์ XML
4. **Encode CryXmlB:** แปลง Plain XML กลับเป็น CryXmlB (ถ้าเกมต้องการ Binary) หรือบางกรณีสามารถใช้ Plain XML ได้เลย
5. **Font GFX:** ใช้ Scaleform GFx SDK หรือ Adobe Flash Professional + Scaleform plugin สร้างไฟล์ `.gfx` ที่มี Thai glyphs
6. **Repack PAK:** บีบอัดไฟล์ทั้งหมดกลับเป็น `.pak` (ZIP format)

```bash
# Repack with Python
python -m zipfile -c English_xml.pak *.xml *.gfx
```

---

## 8. Troubleshooting
- **ตัวอักษรเป็นสี่เหลี่ยม:** ไฟล์ GFX ไม่มี Thai glyphs หรือโหลดไม่สำเร็จ ตรวจสอบว่า `HUD_Font_LocFont.gfx` และ `HUD_Font_LocFont_glyphs.gfx` อยู่ในไฟล์ PAK ครบ
- **เกมแสดงอังกฤษ:** ตรวจว่าไฟล์ `English_xml.pak` อยู่ในโฟลเดอร์ `Localization` ของเกม ไม่ใช่โฟลเดอร์ย่อยอื่น
- **Verify Files (Steam):** หากเกมอัปเดตหรือ Verify Files ไฟล์ PAK ม็อดจะถูกทับด้วยไฟล์ต้นฉบับ ต้องก๊อปม็อดลงใหม่
- **CryXmlB parse error:** ถ้าเจอข้อผิดพลาดตอนแปลง CryXmlB อาจเป็นเพราะเวอร์ชันของ parser ไม่ตรง ให้ลองใช้ parser จาก CryEngine SDK หรือ community tools

---

## 9. Required Tools
| Tool Name | Purpose | Source |
|---|---|---|
| 7-Zip / Python zipfile | Pack/Unpack ไฟล์ `.pak` (ZIP) | [7-zip.org] |
| CryXmlB Reader/Writer | แปลง CryXmlB ↔ Plain XML | [GitHub: CryEngine community] |
| Scaleform GFx SDK | สร้าง/แก้ไขไฟล์ `.gfx` font | [RAD Game Tools] |
| Adobe Flash Pro + Scaleform Plugin | สร้าง GFX font (ทางเลือก) | [Adobe] |

---

## 10. Extracted Assets
- **Font:** ไม่สามารถสกัด TTF ได้ เนื่องจากฟอนต์ **Sabon LT Pro** ถูกฝังเป็น Vector Outline ใน Scaleform GFX format
- **Note:** Sabon LT Pro เป็นฟอนต์ลิขสิทธิ์ของ Linotype ไม่ใช่ Open Source

---

## 11. M2M Protocol
**(สำหรับ AI Agent ที่ต้องการนำคัมภีร์ไปรันสร้างม็อดอัตโนมัติ)**

### ข้อจำกัดสำหรับ AI
- **Text Translation:** ⚠️ AI อ่านไฟล์ CryXmlB ได้ในระดับ raw bytes (UTF-8 Thai strings) แต่ต้องมี CryXmlB parser ที่เขียนมาเฉพาะเพื่อจะแก้ไขและ rebuild ได้อย่างถูกต้อง
- **PAK Pipeline:** ✅ AI ทำได้ 100% — เป็น ZIP ธรรมดา ใช้ `zipfile` module ใน Python จัดการได้
- **Font Generation:** ❌ AI ไม่สามารถสร้าง Scaleform GFX ได้ด้วยตนเอง ต้องส่งต่อให้ Human Operator ใช้ Scaleform SDK
