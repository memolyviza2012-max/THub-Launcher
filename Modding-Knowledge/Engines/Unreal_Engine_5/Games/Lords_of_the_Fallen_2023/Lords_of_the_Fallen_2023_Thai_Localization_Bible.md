# Lords of the Fallen (2023) — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
เอกสารนี้วิเคราะห์กลไกม็อดภาษาไทยของ **Lords of the Fallen (2023)** (LOTF2) อย่างละเอียดที่สุด เกมนี้สร้างด้วย **Unreal Engine 5** และใช้ระบบ localization มาตรฐาน **LocRes** ม็อดนี้ได้ผ่านการตรวจสอบคุณภาพระดับ **FINAL AAA READY** (100/100) ครอบคลุมเนื้อหาเกมหลัก + DLC ทั้งหมด โดยใช้ **PAK chunk override** ที่ลำดับ 99 เพื่อ override LocRes เดิมของเกม พร้อมชุดฟอนต์ **31 ตัว** ที่รองรับหลายภาษารวมถึงภาษาไทย

---

## 2. Technical Stack

| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Unreal Engine 5 |
| **Asset System** | PAK v11 (Zlib compression) |
| **Localization System** | **LocRes** (UE standard binary localization) |
| **LocRes Locale Slot** | `en/` (English slot override) |
| **Font System** | `.ufont` (UE5 Font Face assets) |
| **Compression** | Zlib (entropy ~7.5) |
| **Quality** | FINAL V4 / AAA 100% (3,293 entries, 0 issues) |
| **Mod Strategy** | PAK chunk override (`pakchunk99`) |
| **Mod Complexity** | ★★★☆☆ (มาตรฐาน UE5 LocRes + ufont) |

---

## 3. โครงสร้างไฟล์ (File Architecture)

### 3.1 ภาพรวม
```
(root)/
├── pakchunk99-Windows.pak  ← 64.03 MB  ★ ไฟล์ม็อดหลัก (PAK v11)
├── README_EN.txt           ← 1.7 KB    (เอกสาร EN)
└── README_TH.txt           ← 2.6 KB    (เอกสาร TH)
```

### 3.2 เนื้อหาภายใน PAK (32 entries)
```
pakchunk99-Windows.pak
├── Engine/Content/EngineFonts/Faces/         ← 7 ufont (Engine base fonts)
│   ├── DroidSansFallback.ufont
│   ├── DroidSansMono.ufont
│   ├── RobotoBold.ufont
│   ├── RobotoBoldItalic.ufont
│   ├── RobotoItalic.ufont
│   ├── RobotoLight.ufont
│   └── RobotoRegular.ufont
├── LOTF2/Content/Art/UI/Fonts/FontFaces/
│   ├── CaslonPro/                            ← 5 ufont (เกมใช้สำหรับ UI หลัก)
│   │   ├── ACaslonPro-Bold.ufont
│   │   ├── ACaslonPro-BoldItalic.ufont
│   │   ├── ACaslonPro-Italic.ufont
│   │   ├── ACaslonPro-Regular.ufont
│   │   └── ACaslonPro-Semibold.ufont
│   └── NotoSerif/                            ← 19 ufont (multi-language support)
│       ├── NotoSansThai-VariableFont_wdth_wght.ufont  ★ ฟอนต์ไทย
│       ├── NotoSansBengali-VariableFont_wdth_wght.ufont
│       ├── NotoSansDevanagari-VariableFont_wdth_wght.ufont
│       ├── NotoSansDisplay-VariableFont_wdth_wght.ufont
│       ├── NotoSansJP-Regular.ufont
│       ├── NotoSerif-{Bold,BoldItalic,Italic,Regular}.ufont (4)
│       ├── NotoSerifJP-{Bold,Light,Regular}.ufont (3)
│       ├── NotoSerifKR-{Bold,Light,Regular}.ufont (3)
│       └── NotoSerifSC-{Bold,Light,Medium,Regular}.ufont (4)
└── LOTF2/Content/Localization/Game/en/
    └── Game.locres                            ★ ข้อความแปลไทย (3,293 entries)
```

### 3.3 ขนาดรวม
| รายการ | ขนาด |
|---|---|
| `pakchunk99-Windows.pak` | 64.03 MB |
| README files | 4.3 KB |
| **รวมทั้งหมด** | **~64.03 MB** |

---

## 4. PAK Analysis

### 4.1 PAK Header
| ฟิลด์ | ค่า |
|---|---|
| **Format** | UE PAK v11 |
| **Magic** | `E1 12 6F 5A` |
| **Mount Point** | `../../../` |
| **Entry Count** | 32 |
| **Index Offset** | 67,135,167 |
| **Index Size** | 5,870 bytes |
| **Compression** | Zlib |
| **Entropy** | 7.485 (compressed, not encrypted) |

### 4.2 PAK Chunk Priority
ชื่อไฟล์ `pakchunk99` ใช้หมายเลข **99** เพื่อให้มี priority สูงสุด:
- UE5 โหลด PAK chunks ตามลำดับตัวเลข — หมายเลขสูง = priority สูง
- `pakchunk99` จะ override `pakchunk0` ถึง `pakchunk98` ของเกมเดิม
- กลยุทธ์นี้รับประกันว่า LocRes และ fonts ของม็อดจะถูกใช้แทนต้นฉบับ

### 4.3 English Slot Override
LocRes อยู่ในโฟลเดอร์ `en/` (English) — ม็อดนี้ **override locale English**:
- ผู้เล่นเลือกภาษาอังกฤษในเกม → เกมโหลด `Game.locres` จาก `en/`
- PAK chunk 99 override ไฟล์ `en/Game.locres` → แสดงข้อความภาษาไทย
- **ข้อดี:** ไม่ต้องสร้าง locale ใหม่, ใช้กลไกเดิมของ UE5

---

## 5. LocRes — ระบบข้อความ

### 5.1 Format
| ฟิลด์ | ค่า |
|---|---|
| **Format** | UE LocRes (binary localization) |
| **Path ใน PAK** | `LOTF2/Content/Localization/Game/en/Game.locres` |
| **Encoding** | UTF-16LE (UE standard) |
| **Total Entries** | 3,293 |
| **Thai chars detected** | ~4,988 (first 5MB scan) |

### 5.2 Translation Coverage (100%)
จาก README เอกสาร:
| หมวด | สถานะ |
|---|---|
| Core game content | ✅ |
| DLC / PostLaunch | ✅ |
| UI / Boss Rush / Crucible | ✅ |
| Items / Equipment / Armour / Weapons | ✅ |
| Achievements | ✅ |
| Characters | ✅ |
| Cinematics | ✅ |
| In-game messages / Tutorials | ✅ |
| Collector / Digital Artbook | ✅ |
| Stats / Photo mode / Crash report | ✅ |

### 5.3 Quality Metrics
| Metric | ค่า |
|---|---|
| Tone Quality V2 | 99.9% |
| Real Mundane Issues | 0 |
| Real Garbage Issues | 0 |
| English Leftovers | 0 |
| Spacing Issues | 0 |
| **Overall Quality V2** | **100.0/100** |
| **Verdict** | **FINAL AAA READY** |
| Deep Audit V4 (HIGH/MED/LOW) | 0 / 0 / 0 |

---

## 6. Font System — Triple-Layer Architecture

### 6.1 สามชั้นของฟอนต์
ม็อดนี้ override ฟอนต์ **3 ระดับ** เพื่อรองรับอักษรไทยทุกจุด:

| Layer | โฟลเดอร์ | ฟอนต์ | จำนวน | หน้าที่ |
|---|---|---|---|---|
| **Engine** | `Engine/Content/EngineFonts/Faces/` | Droid, Roboto | 7 | Engine UI, debug, console |
| **Game UI** | `LOTF2/.../CaslonPro/` | Adobe Caslon Pro | 5 | UI หลัก, เมนู, ชื่อไอเทม |
| **Multi-lang** | `LOTF2/.../NotoSerif/` | Noto Serif/Sans | 19 | รองรับหลายภาษา |

### 6.2 ฟอนต์ไทยเฉพาะ
| ฟอนต์ | ประเภท | ตำแหน่ง |
|---|---|---|
| **NotoSansThai-VariableFont_wdth_wght.ufont** | Variable Font | NotoSerif/ |

**Variable Font** = ฟอนต์ที่ปรับ weight/width ได้ ณ runtime — ฟอนต์เดียวรองรับทั้ง Regular, Bold, Light, Condensed

### 6.3 Font Coverage by Language
| ภาษา | ฟอนต์ | จำนวน |
|---|---|---|
| **Thai** | NotoSansThai Variable | 1 |
| Japanese | NotoSansJP, NotoSerifJP | 4 |
| Korean | NotoSerifKR | 3 |
| Simplified Chinese | NotoSerifSC | 4 |
| Bengali | NotoSansBengali Variable | 1 |
| Devanagari (Hindi) | NotoSansDevanagari Variable | 1 |
| Latin/Cyrillic | NotoSansDisplay, NotoSerif, Roboto, Caslon | 16 |

---

## 7. Complete Pipeline — ขั้นตอนสร้างม็อด

```
ขั้นตอนที่ 1: สกัด LocRes จากเกม
    ใช้ UnrealPak:
    UnrealPak.exe -Extract {game_paks}/pakchunk0-Windows.pak
    → ได้ Game.locres ต้นฉบับ (English)
        ↓
ขั้นตอนที่ 2: แปลข้อความ
    ใช้เครื่องมือ: LocRes Editor / UAssetGUI
    - แก้ไขข้อความในแต่ละ key
    - แปลจากอังกฤษเป็นไทย (3,293 entries)
    - ทำ QA (Deep Audit V4)
        ↓
ขั้นตอนที่ 3: เตรียมฟอนต์
    - ดาวน์โหลด NotoSansThai Variable Font
    - Wrap เป็น .ufont (UE5 Font Face)
    - เตรียม Engine fonts + Game fonts ที่รองรับไทย
        ↓
ขั้นตอนที่ 4: Pack PAK
    ใช้ UnrealPak:
    - รวม LocRes + 31 Fonts → pakchunk99-Windows.pak
    - ใช้หมายเลข 99 เพื่อ priority สูงสุด
        ↓
ขั้นตอนที่ 5: ติดตั้ง
    วาง pakchunk99-Windows.pak ไปที่:
    {GameInstall}/LOTF2/Content/Paks/
        ↓
เสร็จสิ้น! เลือกภาษาอังกฤษ → แสดงเป็นไทย
```

---

## 8. Required Tools

| เครื่องมือ | หน้าที่ | ระดับความจำเป็น |
|---|---|---|
| **UnrealPak** (UE5 SDK) | Pack/Unpack PAK v11 | ✅ จำเป็น |
| **LocRes Editor** | แก้ไข LocRes binary | ✅ จำเป็น |
| **UAssetGUI** | ตรวจสอบ UAsset structure | ⚡ แนะนำ |
| **Hex Editor** | วิเคราะห์ binary | ⚡ สำหรับวิจัย |

---

## 9. สถิติม็อด

| ข้อมูล | จำนวน |
|---|---|
| **ไฟล์ม็อดหลัก** | 1 ไฟล์ (pakchunk99-Windows.pak) |
| **ขนาดรวม** | 64.03 MB |
| **PAK Version** | 11 |
| **PAK Entries** | 32 (1 LocRes + 31 Fonts) |
| **Translation entries** | 3,293 |
| **Quality Score** | 100/100 (FINAL AAA) |
| **ฟอนต์ Engine** | 7 (.ufont) |
| **ฟอนต์ Game UI (CaslonPro)** | 5 (.ufont) |
| **ฟอนต์ Multi-lang (NotoSerif)** | 19 (.ufont) |
| **ฟอนต์ Thai โดยเฉพาะ** | 1 (NotoSansThai Variable) |

---

## 10. ความพิเศษของม็อดนี้

### 10.1 AAA Quality Standard
ม็อดนี้ผ่าน **Deep Audit V4** ด้วยคะแนน **100/100**:
- 0 HIGH/MEDIUM/LOW issues
- 0 English leftovers
- 0 Placeholder mismatches
- 0 Spacing issues
- 99.9% Tone Quality

### 10.2 Complete Coverage
ครอบคลุมทุกส่วนของเกม — Core + DLC + PostLaunch + Boss Rush + Crucible + Achievements + Cinematics + ทุกอย่าง

### 10.3 Massive Font Override (31 fonts)
ม็อดนี้ override ฟอนต์ **31 ตัว** ครอบคลุม 3 ระดับ:
- Engine fonts (Droid, Roboto)
- Game UI fonts (Adobe Caslon Pro)
- Multi-language fonts (Noto family — JP, KR, SC, Bengali, Devanagari, **Thai**)

### 10.4 pakchunk99 Priority Strategy
ใช้หมายเลข 99 เพื่อ guaranteed highest priority — override ทุก chunk ของเกมเดิม

### 10.5 Non-Destructive
ม็อดไม่แก้ไขไฟล์เกมต้นฉบับ — ลบ `pakchunk99-Windows.pak` = เกมกลับเป็นปกติ

---

## 11. เปรียบเทียบ

| เกม | Engine | Localization | Font Count | Quality | Complexity |
|---|---|---|---|---|---|
| **Lords of the Fallen** | UE5 | LocRes (en/ slot) | 31 ufont | AAA 100/100 | ★★★☆☆ |
| **Gothic Remake** | UE5+Alkimia | LCACHE (encrypted) | Dual (ufont+TTF) | N/A | ★★★★☆ |
| **FF7 Rebirth** | UE5 (SE) | TxtRes (custom) | 38 bitmap atlas | N/A | ★★★★★ |
| **Ghostrunner** | UE4 | LocRes (binary) | 1 ufont | N/A | ★★★☆☆ |

---

## 12. Conclusion

ม็อดภาษาไทยของ **Lords of the Fallen (2023)** เป็นตัวอย่างที่สมบูรณ์แบบที่สุดของ **"Production-Grade UE5 Localization Mod"**:

1. **PAK v11 chunk99** — ใช้ระบบ PAK override ลำดับ 99 เพื่อ guaranteed priority สูงสุด
2. **LocRes (en/ slot)** — override locale English ด้วย LocRes ที่แปลเป็นไทย (3,293 entries)
3. **31 Font Override** — ครอบคลุม Engine, Game UI, และ Multi-language fonts ทั้งหมด
4. **NotoSansThai Variable Font** — ฟอนต์ Variable ที่ปรับ weight/width ได้ ณ runtime
5. **AAA Quality (100/100)** — ผ่าน Deep Audit V4 ด้วยคะแนนสมบูรณ์แบบ ไม่มี issue เหลือ
6. **Complete Coverage** — ครอบคลุมเนื้อหาเกมหลัก + DLC + PostLaunch ทุกส่วน
7. **Non-Destructive** — ลบไฟล์เดียว = เกมกลับเป็นปกติ

---

## 13. Extracted Assets

รายการไฟล์และทรัพยากรที่ถูกดึงออกมาจากม็อดนี้:

- **Fonts:** [Assets/Fonts/](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unreal_Engine_5/Games/Lords_of_the_Fallen_2023/Assets/Fonts)
  - *31 .ufont files อยู่ใน PAK v11 (Zlib compressed) — ต้องใช้ UnrealPak เพื่อแตก*
  - *ฟอนต์ไทยหลัก:* `NotoSansThai-VariableFont_wdth_wght.ufont`

- **Texts / LocRes:** [Assets/Texts/](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unreal_Engine_5/Games/Lords_of_the_Fallen_2023/Assets/Texts)
  - *Game.locres อยู่ใน PAK (compressed) — ต้องใช้ UnrealPak เพื่อแตก*
  - *3,293 Thai translation entries, Quality 100/100*

- **Configs / Metadata:** [Assets/Configs/](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unreal_Engine_5/Games/Lords_of_the_Fallen_2023/Assets/Configs)
  - [PAK_Content_Listing.txt](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unreal_Engine_5/Games/Lords_of_the_Fallen_2023/Assets/Configs/PAK_Content_Listing.txt) — รายชื่อไฟล์ทั้ง 32 entries ภายใน PAK
  - [README_EN.txt](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unreal_Engine_5/Games/Lords_of_the_Fallen_2023/Assets/Configs/README_EN.txt) — เอกสารม็อด (EN)
  - [README_TH.txt](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unreal_Engine_5/Games/Lords_of_the_Fallen_2023/Assets/Configs/README_TH.txt) — เอกสารม็อด (TH)
