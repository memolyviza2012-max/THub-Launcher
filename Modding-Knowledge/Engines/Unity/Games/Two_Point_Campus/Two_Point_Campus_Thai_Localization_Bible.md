# Two Point Campus — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
เอกสารนี้วิเคราะห์กลไกม็อดภาษาไทยของ **Two Point Campus** อย่างละเอียดที่สุด เกมนี้สร้างด้วย **Unity Engine** และใช้ระบบ localization ของ **I2 Localization** (Inter Illusion) ซึ่งเป็น plugin Unity ที่นิยมมากในเกมระดับ AA/AAA ม็อดนี้ทำงานโดยแทนที่ **Unity Addressable Asset Bundle** 2 ไฟล์ — หนึ่งไฟล์สำหรับข้อความ (localization) และอีกหนึ่งไฟล์สำหรับฟอนต์ ที่รองรับอักษรไทย

---

## 2. Technical Stack

| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Unity Engine |
| **Localization Plugin** | **I2 Localization** (Inter Illusion) — ใช้ `[i2t]` / `[i2p_]` markers |
| **Asset System** | **Unity Addressable Asset System** (Addressables) |
| **Archive Format** | **UnityFS** Asset Bundle (Magic: `UnityFS`, Format Version 8) |
| **Text Encoding** | UTF-8 (ยืนยัน: พบ Thai UTF-8 sequences 628,234 ตัวอักษรไทย) |
| **Font System** | TextMeshPro (SDF Fonts + Sprite Assets) |
| **Mod Complexity** | ★★★☆☆ (ต้อง repack UnityFS bundle แต่ไม่ต้องแก้โค้ด) |

---

## 3. โครงสร้างไฟล์ (File Architecture)

### 3.1 ไฟล์ที่ม็อดแก้ไข
```
TPC_Data/
└── StreamingAssets/
    └── aa/
        └── StandaloneWindows64/
            ├── fonts_assets_all.bundle                       ← 64.57 MB (ฟอนต์ทั้งหมด)
            └── localisation_assets_localisationenglish.bundle ← 2.57 MB (ข้อความภาษาไทย)
```

ม็อดนี้มีเพียง **2 ไฟล์** เท่านั้น แต่ทั้งสองเป็น Unity Asset Bundle ที่ต้อง repack

### 3.2 UnityFS Header Structure

| Field | Font Bundle | Loc Bundle |
|---|---|---|
| **Signature** | `UnityFS` | `UnityFS` |
| **Format Version** | 8 | 8 |
| **Unity Version** | `5.x.x` | `5.x.x` |
| **Generator** | `0.0.0` | `0.0.0` |
| **File Size** | 67,703,556 bytes | 2,698,496 bytes |
| **CAB ID** | มี (internal) | มี (internal) |

---

## 4. I2 Localization System — ระบบแปลภาษา

### 4.1 I2 Localization คืออะไร?
**I2 Localization** เป็น Unity plugin ยอดนิยมจาก Inter Illusion ที่ใช้ในเกมหลายร้อยเกม ข้อมูลแปลภาษาจะถูกเก็บเป็น **TextAsset** ภายใน Asset Bundle โดยแต่ละ TextAsset เป็นไฟล์ `.txt` ที่ใช้ format เฉพาะของ I2

### 4.2 I2LS Files (25 ไฟล์)
ข้อมูลแปลภาษาทั้งหมดถูกแบ่งเป็น 25 ไฟล์ `.txt` ภายใน bundle:

| ไฟล์ | เนื้อหา |
|---|---|
| `I2LS_Advisor.txt` | คำแนะนำจากที่ปรึกษา |
| `I2LS_ArchetypeSpecificNames.txt` | ชื่อเฉพาะของ Archetype |
| `I2LS_Challenges.txt` | ภารกิจท้าทาย |
| `I2LS_CharacterNames.txt` | ชื่อตัวละคร |
| `I2LS_Characters.txt` | คำอธิบายตัวละคร |
| `I2LS_CodeRef.txt` | Reference จากโค้ด |
| `I2LS_Courses.txt` | หลักสูตรเรียน |
| `I2LS_DLCs.txt` | เนื้อหา DLC |
| `I2LS_FlavourTraits.txt` | ลักษณะนิสัยตัวละคร |
| `I2LS_Fonts.txt` | การตั้งค่าฟอนต์ |
| `I2LS_General.txt` | ข้อความทั่วไป |
| `I2LS_Input.txt` | การตั้งค่า Input |
| `I2LS_Items.txt` | ไอเทม/สิ่งของ |
| `I2LS_Levels.txt` | ด่าน/แผนที่ |
| `I2LS_Meta.txt` | Metadata |
| `I2LS_Mods.txt` | ระบบ Mods |
| `I2LS_Music_Radio.txt` | เพลง/วิทยุ |
| `I2LS_Objectives.txt` | วัตถุประสงค์ |
| `I2LS_Research_Marketing.txt` | วิจัย/การตลาด |
| `I2LS_Rooms.txt` | ห้องต่างๆ |
| `I2LS_SubGoals.txt` | เป้าหมายย่อย |
| `I2LS_UI.txt` | UI ทั้งหมด (ใหญ่ที่สุด) |
| `I2LS_UI_Settings.txt` | UI ตั้งค่า |
| `I2LS_VO_Radio.txt` | เสียงพากย์วิทยุ |
| `I2LS_VO_Tannoy.txt` | เสียงประกาศ |

### 4.3 I2 Text Format
ข้อความถูกเก็บในรูปแบบ **I2 Custom Serialization** (ไม่ใช่ TSV/CSV มาตรฐาน):

```
{Key}={TranslatedValue}[i2t]{Key}={TranslatedValue}[i2t]...
```

- **`[i2t]`** — Translation Separator (คั่นระหว่าง key-value แต่ละคู่, พบ **15,652 ครั้ง**)
- **`[i2p_One]`** / **`[i2p_Zero]`** — Pluralization Marker (แยกรูปเอกพจน์/พหูพจน์, พบ **166 ครั้ง**)

### 4.4 ตัวอย่างข้อมูลจริง
```
UI/Attribute/Energy=พลังงาน[i2t]
UI/Attribute/Health=สุขภาพกาย[i2t]
UI/Attribute/Hunger=ความหิว[i2t]
UI/Attribute/Hygiene=สุขอนามัย[i2t]
UI/Awards/EndofYearAwards=รางวัลสิ้นปี[i2t]
UI/Awards/TeacherOfTheYear=ครูแห่งปี[i2t]
```

### 4.5 ตัวอย่าง Pluralization
```
SubGoals/Academic_Skill_Level_X=ทำให้ถึง {COUNT} ทักษะ[i2p_One]ทำให้ถึง {COUNT} ทักษะ[i2t]
```
- `[i2p_One]` คั่นระหว่างรูป singular กับ plural
- ภาษาไทยไม่มีเอก/พหูพจน์ จึงใส่ข้อความเหมือนกันทั้งสองรูป

### 4.6 Variable Placeholders
พบ **107 ตัวแปร** ที่เกมจะแทนค่าตอน runtime:

| ตัวแปร | ความหมาย |
|---|---|
| `{COUNT}` | จำนวน |
| `{SCORE}` | คะแนน |
| `{COST}` | ราคา |
| `{YEAR}` | ปี |
| `{COURSE}` | หลักสูตร |
| `{CHARACTER}` | ชื่อตัวละคร |
| `{CLUB}` | ชมรม |
| `{TARGET}` | เป้าหมาย |
| `{ATTRIBUTE}` | คุณลักษณะ |
| `{AVERAGE}` | ค่าเฉลี่ย |
| `{AMOUNT}` | จำนวนเงิน |
| `{BONUS}` | โบนัส |
| ... | รวม 107 ตัวแปร |

> **สำคัญ:** ตัวแปรเหล่านี้ **ห้ามแปล** และ **ห้ามลบ** — เกมจะ crash หรือแสดงผลผิดพลาด

---

## 5. Font Bundle Analysis

### 5.1 ฟอนต์ที่ฝังอยู่ (17 font files)

**ฟอนต์หลักของเกม:**
| ฟอนต์ | รูปแบบ | หน้าที่ |
|---|---|---|
| `Baloo-Regular.ttf` | TTF | ฟอนต์หลัก UI |
| `ALEGREYA-EXTRABOLDITALIC.TTF` | TTF | หัวข้อเน้น |
| `BANGERS-REGULAR.TTF` | TTF | หัวข้อสนุก |
| `CHANGO-REGULAR.TTF` | TTF | ตัวอักษรหนา |
| `Kalam-Regular.ttf` | TTF | ลายมือ |
| `Pacifico-Regular.ttf` | TTF | ตัวเขียน |
| `PalanquinDark-*.ttf` | TTF (3 weights) | เนื้อหาหลัก |
| `RobotoSlab-Bold.ttf` | TTF | ตัวหนา |

**ฟอนต์ CJK (ภาษาเอเชีย):**
| ฟอนต์ | ภาษา |
|---|---|
| `NotoSansCJKjp-Minified-Regular.otf` | ญี่ปุ่น |
| `NotoSansCJKkr-Minified-Regular.otf` | เกาหลี |
| `NotoSansJP-Medium.otf` | ญี่ปุ่น |
| `NotoSansKR-Medium.otf` | เกาหลี |
| `NotoSansSC-Medium.otf` | จีนตัวย่อ |
| `NotoSansTC-Medium.otf` | จีนตัวเต็ม |
| `NotoSansArabic-Regular.ttf` | อารบิก |

### 5.2 TextMeshPro SDF Assets
ฟอนต์ถูกแปลงเป็น SDF (Signed Distance Field) สำหรับ TextMeshPro:
- `Baloo-Regular SDF` — SDF หลัก พร้อม material variants (Black, Shadow)
- NotoSans Dynamic SDF — สร้าง glyph แบบ dynamic สำหรับ CJK

### 5.3 กลยุทธ์ฟอนต์ไทย
จาก bundle ขนาด **64.57 MB** (ใหญ่มาก) แสดงว่ามีการ:
1. **เพิ่มฟอนต์ไทย** เข้าไปใน bundle (หรือแทนที่ฟอนต์เดิมด้วยฟอนต์ที่รองรับอักษรไทย)
2. **สร้าง SDF Atlas ใหม่** ที่มี glyph ภาษาไทยทั้งหมด (สระ, วรรณยุกต์, ตัวเลขไทย)
3. **อัปเดต TMP Font Asset** ให้ชี้ไปที่ฟอนต์ใหม่ + fallback chain

---

## 6. Language Slot Strategy

### 6.1 กลยุทธ์: ทับ English Localization Bundle
ม็อดนี้แทนที่ bundle ชื่อ `localisation_assets_localisationenglish.bundle` โดยตรง:
- **ชื่อไฟล์ยังคงเป็น** `localisationenglish` — เกมคิดว่ากำลังโหลดภาษาอังกฤษ
- **เนื้อหาภายในเป็นภาษาไทยทั้งหมด** — I2LS TextAssets ถูกแทนที่
- **ผู้เล่นเลือก "English" ในเมนูตั้งค่า** → แสดงเป็นภาษาไทย

### 6.2 ทำไมต้องทับ English?
เพราะ Unity Addressable System ใช้ชื่อไฟล์ bundle เป็น key ในการโหลด — ถ้าสร้าง bundle ชื่อใหม่ (เช่น `localisationthai.bundle`) เกมจะไม่รู้จัก ต้องแก้ catalog ด้วย

---

## 7. Addressable Asset System

### 7.1 ทำไมม็อดถึงเลือกใช้ Addressables?
Two Point Campus ใช้ **Unity Addressable Asset System** ในการจัดการทรัพยากร ซึ่งทำงานดังนี้:
1. เกมมี **Catalog** (อาจเป็น `.json` หรือ `.hash`) ที่เก็บ mapping ของ asset address → bundle file
2. เมื่อเกมต้องการ asset → ค้นหาใน catalog → โหลด bundle → ดึง asset ออกมา
3. Bundle files อยู่ใน `StreamingAssets/aa/StandaloneWindows64/`

### 7.2 ข้อจำกัด
- ม็อดนี้มีเฉพาะ **2 bundle files** → แสดงว่า catalog ของเกมไม่ได้ถูกแก้ไข
- เกมโหลด bundle จากชื่อไฟล์เดิม → ม็อดจึงต้องใช้ชื่อไฟล์เดิมเท่านั้น
- ถ้า catalog ใช้ **hash verification** → ต้องปิด integrity check ด้วย

---

## 8. Complete Pipeline — ขั้นตอนสร้างม็อด

```
ขั้นตอนที่ 1: แตก Asset Bundle (localisation bundle)
    ใช้เครื่องมือ: UABEA, AssetStudio, หรือ Asset Bundle Extractor
    แตก I2LS_*.txt ทั้ง 25 ไฟล์ออกมา
        ↓
ขั้นตอนที่ 2: แปลข้อความ
    - เปิดไฟล์ .txt ที่แตกออกมา
    - แปลเฉพาะ Value (หลังเครื่องหมาย =)
    - ห้ามแก้ Key (ก่อนเครื่องหมาย =)
    - ห้ามลบ [i2t], [i2p_One], [i2p_Zero] markers
    - ห้ามลบ {VARIABLE} placeholders
        ↓
ขั้นตอนที่ 3: สร้างฟอนต์ไทย
    - เตรียมฟอนต์ .ttf/.otf ที่รองรับอักษรไทย
    - สร้าง SDF Atlas ด้วย Unity + TextMeshPro
    - Export เป็น Font Asset (.asset)
        ↓
ขั้นตอนที่ 4: Repack Asset Bundle
    ใช้ UABEA หรือ Asset Bundle Extractor:
    - นำเข้า I2LS_*.txt ที่แปลแล้วกลับเข้า localisation bundle
    - นำเข้า Font Asset ที่สร้างใหม่กลับเข้า font bundle
    - บันทึกเป็น .bundle ใหม่
        ↓
ขั้นตอนที่ 5: วางไฟล์ทับ
    คัดลอก 2 ไฟล์ .bundle ไปวางทับที่:
    TPC_Data/StreamingAssets/aa/StandaloneWindows64/
        ↓
เสร็จสิ้น! เปิดเกม → เลือก English → แสดงเป็นภาษาไทย
```

---

## 9. Required Tools

| เครื่องมือ | หน้าที่ | ระดับความจำเป็น |
|---|---|---|
| **UABEA** (Unity Asset Bundle Extractor/Assembler) | แตก/repack `.bundle` | ✅ จำเป็น |
| **AssetStudio** | ดู asset ใน bundle (อ่านอย่างเดียว) | ⚡ แนะนำ |
| **Unity Editor + TextMeshPro** | สร้าง SDF Font Atlas | ✅ จำเป็น (สำหรับฟอนต์) |
| **Text Editor** (VSCode, Notepad++) | แก้ไข I2LS text files | ✅ จำเป็น |
| **AI Translation** | แปลข้อความ 15,000+ รายการ | ⚡ แนะนำ |

---

## 10. สถิติม็อด

| ข้อมูล | จำนวน |
|---|---|
| **ไฟล์ที่ม็อด** | 2 ไฟล์ (.bundle) |
| **ขนาดรวม** | 67.14 MB |
| **I2LS TextAssets** | 25 ไฟล์ |
| **Key-Value Pairs** | ~15,100 คู่ |
| **[i2t] Markers** | 15,652 |
| **[i2p_] Markers** | 166 (One, Zero) |
| **Variable Placeholders** | 107 ชนิด |
| **Thai Characters** | 628,234 ตัวอักษร |
| **ฟอนต์ในม็อด** | 17 font files |

---

## 11. เปรียบเทียบกับเกมที่ใช้ I2 Localization อื่นๆ

Two Point Campus ไม่ใช่เกมเดียวที่ใช้ I2 Localization — เกมอื่นๆ ที่ใช้ I2 Loc ได้แก่:
- **Two Point Hospital** (เกมพี่น้อง — โครงสร้างเหมือนกันเกือบ 100%)
- **Hardspace: Shipbreaker** (ใช้ I2 Loc + Unity)
- **Subnautica** (ใช้ I2 Loc)

ถ้าเข้าใจวิธีม็อด Two Point Campus แล้ว สามารถนำไปใช้กับเกมอื่นที่ใช้ I2 Loc ได้ทันที

---

## 12. Conclusion

ม็อดภาษาไทยของ **Two Point Campus** เป็นตัวอย่างคลาสสิกของ **"Unity Addressable Bundle Override"**:

1. **I2 Localization Plugin** — ระบบแปลภาษาที่เป็นมาตรฐานของ Unity indie/AA games, ใช้ format `Key=Value[i2t]` ที่อ่านง่าย
2. **Addressable Asset Bundle** — ไฟล์ `.bundle` ที่ต้องใช้เครื่องมือ (UABEA) ในการแตก/repack ไม่สามารถแก้ไขด้วย text editor ตรงๆ ได้
3. **Font Bundle ขนาดใหญ่** — 64.57 MB แสดงว่ามีการสร้าง SDF Atlas สำหรับอักษรไทยอย่างเต็มรูปแบบ
4. **Pluralization Support** — มีระบบ `[i2p_One]`/`[i2p_Zero]` สำหรับรองรับภาษาที่มีเอก/พหูพจน์
5. **Variable System** — มีตัวแปร 107 ชนิดที่เกมจะแทนค่าตอน runtime
6. **Knowledge Reuse** — เทคนิคเดียวกันนำไปใช้กับ Two Point Hospital และเกม I2 Loc อื่นๆ ได้ทันที
