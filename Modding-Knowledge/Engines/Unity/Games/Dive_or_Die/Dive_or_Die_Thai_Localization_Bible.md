# Dive or Die: Children of Rain — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Dive or Die: Children of Rain is a survival game built on **Unity 2022.3** (LTS). The Thai localization mod uses a creative **Locale Hijacking** technique — instead of adding a new Thai locale, the modder replaces the **Chinese Traditional (zh-Hant)** locale with Thai text and fonts. The mod consists of 3 core files: a massive `sharedassets0.assets` (388 MB, containing Thai fonts), a localization text bundle (hijacking zh-Hant), and an Addressable catalog for routing.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Unity 2022.3.62f3 (LTS) |
| **Developer** | ไม่ระบุ |
| **Mod Author** | ไม่ระบุ |
| **Archive Format** | Unity SerializedFile (`sharedassets0.assets`) + UnityFS Addressable Bundles |
| **Font System** | TextMeshPro (TMP) SDF |
| **Thai Font** | **Noto Sans Thai Regular/Bold PUA** (87 Thai codepoints) + **Greetings** (display font) |
| **Text System** | Unity Localization (String Tables) via Addressable Bundles |
| **Text Encoding** | UTF-8 |
| **Locale Hijacking** | Thai text ถูกยัดเข้าไปใน Chinese Traditional (zh-Hant) locale |
| **Mod Complexity** | ★★★☆☆ (Addressable + sharedassets replacement + Locale Hijacking) |

---

## 3. โครงสร้างไฟล์ (File Architecture)

```text
Dive or Die/
└── Dive or Die_Data/
    ├── sharedassets0.assets                           (388 MB — ฟอนต์ TMP + Textures)
    │   ├── [Embedded] Noto Sans Thai Regular PUA      (562 KB — 87 Thai codepoints)
    │   ├── [Embedded] Noto Sans Thai Regular PUA #2   (562 KB — สำเนา)
    │   ├── [Embedded] Noto Sans Thai Bold PUA         (563 KB — ตัวหนา)
    │   ├── [Embedded] Greetings Bold                  (82 KB — ฟอนต์ตกแต่ง)
    │   ├── [Embedded] Greetings Regular               (90 KB — ฟอนต์ตกแต่ง)
    │   └── [Embedded] SylfaenARM                      (221 KB — ฟอนต์อาร์เมเนีย)
    │
    └── StreamingAssets/aa/
        ├── catalog.json                               (266 KB — Addressable catalog)
        └── StandaloneWindows64/
            ├── localization-assets-chinese(traditional)...bundle   (64.9 MB — Font assets/textures)
            ├── localization-string-tables-chinese(traditional)...bundle (302 KB — ข้อความไทย!)
            └── localization-string-tables-english(en)...bundle    (184 KB — ข้อความอังกฤษ)
```

### เทคนิค Locale Hijacking 🎭
ม็อดเดอร์ไม่ได้สร้าง locale ใหม่ แต่ **ยึด Chinese Traditional (zh-Hant)** มาใช้แทน!
- ข้อความไทยทั้งหมด 55,218 ตัวอักษร ถูกยัดเข้าไปในไฟล์ `localization-string-tables-chinese(traditional)` 
- ผู้เล่นต้องไปที่ Settings → Language → เลือก "Thai" (ซึ่งจริงๆ คือ zh-Hant ที่ถูกเปลี่ยนชื่อ)

---

## 4. Font Analysis

### 4.1 Noto Sans Thai PUA — ฟอนต์หลัก
- **Full Name:** Noto Sans Thai Regular PUA / Noto Sans Thai Bold PUA
- **Thai Coverage:** 87 codepoints (U+0E00–U+0E7F)
- **PUA:** มีอักขระพิเศษใน Private Use Area (PUA) สำหรับสระลอย/วรรณยุกต์ที่ต้องการตำแหน่งพิเศษ
- **License:** SIL Open Font License (Google Fonts)

### 4.2 Greetings — ฟอนต์ตกแต่ง
- ฟอนต์สไตล์ handwritten/display สำหรับหัวข้อหรือ UI พิเศษ
- มี 2 รูปแบบ: Regular (90 KB) + Bold (82 KB)

### 4.3 SylfaenARM — ฟอนต์เสริม
- ฟอนต์ Armenian/Georgian อาจเป็นฟอนต์ fallback ของระบบ

---

## 5. Text Analysis

### 5.1 String Tables (Addressable Bundles)
- **Thai Chars:** **55,218 ตัวอักษร** (UTF-8, ฝังอยู่ใน zh-Hant bundle)
- **Format:** Unity Localization String Tables ผ่าน Addressable system
- ข้อความเป็นแบบ Key-Value ที่ Unity Localization จัดการให้โดยอัตโนมัติ

### 5.2 ตัวอย่างข้อความไทย:
```
"ออกซิเจน"
"โภชนาการ" 
"สมปัญญะ"
"ปลาวาฬ...อาจมอบพรพิเศษ"
```

---

## 6. Cross-Engine Comparison

| Feature | Dive or Die | Tattoo Tycoon | Sea of Stars |
|---|---|---|---|
| **Unity Version** | 2022.3 | 2021.3 | 2021.x |
| **Bundle System** | Addressables | Addressables | Addressables |
| **Font Location** | sharedassets0.assets | resources.assets | Bundle |
| **Locale Method** | **Hijack zh-Hant** | Override EN | Override EN |
| **Thai Font** | Noto Sans Thai PUA | Liberation Sans | Custom |
| **Thai Chars** | 55K | 218K | ~150K |
| **Assets Size** | 388 MB | 828 KB | Multi-bundle |

**จุดเด่น:** การใช้ PUA (Private Use Area) ในฟอนต์ Noto Sans Thai เพื่อแก้ปัญหาสระลอยเป็นเทคนิคที่น่าสนใจ — แทนที่จะ patch memory เหมือน Medieval Dynasty กลับแก้ที่ระดับ Font Glyph Mapping แทน

---

## 7. Pipeline — ขั้นตอนสร้างม็อด

1. **Font Prep:** เตรียมฟอนต์ Thai PUA ด้วย FontForge (เพิ่ม PUA glyphs สำหรับสระ/วรรณยุกต์)
2. **Build TMP Asset:** ใช้ Unity Editor 2022.3 สร้าง TMP Font Asset จาก TTF ที่เตรียมไว้
3. **Replace sharedassets0:** ใช้ UABEA แทนที่ Font Asset ใน `sharedassets0.assets`
4. **Text Translation:** สร้าง String Tables ด้วย Unity Localization package แล้ว build เป็น Addressable bundle
5. **Locale Hijacking:** ตั้งค่าให้ zh-Hant locale ใช้ข้อความไทยและ TMP Font Asset ไทย
6. **Rebuild Catalog:** สร้าง `catalog.json` ใหม่ที่ชี้ไปที่ bundle ของ zh-Hant
7. **Deployment:** วาง 3 ไฟล์ (sharedassets0 + 2 bundles + catalog) ลงโฟลเดอร์เกม

---

## 8. Troubleshooting
- **ตัวหนังสือเป็นสี่เหลี่ยม:** `sharedassets0.assets` ไม่ได้ถูกแทนที่ หรือเวอร์ชันไม่ตรง (ต้องใช้กับ v1.0.4858.st)
- **ข้อความยังเป็นอังกฤษ:** ไม่ได้เลือก Language เป็น "Thai" ในเมนู Settings → General
- **เกมแครช:** ตรวจสอบว่า catalog.json ตรงกับ bundle files ที่วางไว้
- **ขนาดม็อดใหญ่มาก (388 MB):** เป็นเพราะต้องแทนที่ `sharedassets0.assets` ทั้งไฟล์ ซึ่งรวมถึง texture/mesh อื่นๆ ของเกมด้วย

---

## 9. Required Tools
| Tool Name | Purpose | Source |
|---|---|---|
| UABEA | แก้ไข Unity Assets / Bundles | [GitHub: nesrak1] |
| Unity Editor 2022.3 | สร้าง TMP Font Asset + Addressable bundles | [Unity Hub] |
| FontForge | แก้ไข TTF / สร้าง PUA glyphs | [FontForge.org] |

---

## 10. Extracted Assets
- **Noto Sans Thai PUA (.ttf) — ฟอนต์หลักพร้อม Thai glyphs:**
  - [NotoSansThai-Regular-PUA.ttf](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unity_Engine/Games/Dive_or_Die/Assets/Fonts/NotoSansThai-Regular-PUA.ttf) (562 KB, 87 Thai codepoints)
  - [NotoSansThai-Bold-PUA.ttf](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unity_Engine/Games/Dive_or_Die/Assets/Fonts/NotoSansThai-Bold-PUA.ttf) (563 KB)
- **Greetings (.ttf) — ฟอนต์ตกแต่ง:**
  - [Greetings-Bold.ttf](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unity_Engine/Games/Dive_or_Die/Assets/Fonts/Greetings-Bold.ttf) (82 KB)
  - [Greetings-Regular.ttf](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unity_Engine/Games/Dive_or_Die/Assets/Fonts/Greetings-Regular.ttf) (90 KB)

---

## 11. M2M Protocol
**(สำหรับ AI Agent ที่ต้องการนำคัมภีร์ไปรันสร้างม็อดอัตโนมัติ)**

### ข้อจำกัดสำหรับ AI
- **Text Translation:** ⚠️ AI อ่าน UTF-8 Thai จาก bundle ได้ แต่การแก้ไข Unity Addressable Bundle ต้องใช้ UABEA หรือ Unity Editor
- **Font Pipeline:** ⚠️ การสร้าง PUA glyphs ต้องใช้ FontForge + Unity Editor สำหรับ TMP rebuild
- **Locale Hijacking:** ✅ AI สามารถเข้าใจและแนะนำวิธี hijack locale ได้ แต่การ build catalog ต้องผ่าน Unity Editor
- **Deployment:** ✅ AI สามารถก๊อปไฟล์ลงโฟลเดอร์เกมได้ทันที
