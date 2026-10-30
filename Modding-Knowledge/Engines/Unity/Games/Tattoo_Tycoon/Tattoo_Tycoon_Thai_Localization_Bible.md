# Tattoo Tycoon — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Tattoo Tycoon is a business simulation game built on **Unity Engine 2021.3** (LTS). The Thai localization mod uses a **Dual-Layer Asset Override** approach: an Addressable AssetBundle (`.bundle`) for localized text injection via the game's I2/Custom localization system, and a modified `resources.assets` file containing the replacement TMP font with Thai glyphs. This is a textbook example of a **Unity Addressables + resources.assets Font Embed** architecture.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Unity 2021.3.45f2 (LTS, IL2CPP-compatible) |
| **Developer** | ไม่ระบุ |
| **Mod Author** | ไม่ระบุ |
| **Archive Format** | UnityFS AssetBundle (`.bundle`) + `resources.assets` |
| **Font System** | TextMeshPro (TMP) SDF Font |
| **Thai Font** | **Liberation Sans** (with 87 Thai codepoints) |
| **Text System** | Unity Addressables Localization Bundle |
| **Text Encoding** | UTF-8 |
| **Mod Complexity** | ★★★☆☆ (Addressable bundle + resources.assets replacement) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
ม็อดนี้ประกอบด้วย 2 ไฟล์ ที่ต้องวางทับในโฟลเดอร์เกม:

```text
Tattoo Tycoon/
├── Tattoo Tycoon_Data/
│   ├── resources.assets                          (828 KB — ฟอนต์ TMP)
│   │   ├── [Embedded] Liberation Sans TTF        (361 KB — 87 Thai glyphs)
│   │   ├── [Embedded] Perfect DOS VGA 437 TTF    (ฟอนต์พิกเซลดั้งเดิม)
│   │   └── [TMP Asset] LiberationSans SDF        (TMP Signed Distance Field)
│   │
│   └── StreamingAssets/aa/StandaloneWindows64/
│       └── localisation-english_assets_all_...bundle  (19.4 MB — ข้อความแปลไทย)
```

### ไฟล์ที่ 1: `resources.assets` (828 KB)
- เก็บฟอนต์ **Liberation Sans** (TTF ดิบที่ฝังอยู่ใน Unity SerializedFile) 
- มี TMP SDF Font Asset (`LiberationSans SDF - Drop Shadow`) ที่อ้างอิงฟอนต์นี้
- ม็อดเดอร์แทนที่ Liberation Sans ต้นฉบับด้วยเวอร์ชันที่มี Thai glyphs

### ไฟล์ที่ 2: `localisation-english_...bundle` (19.4 MB)
- เก็บข้อความแปลภาษาไทยทั้งหมด
- **218,132 อักษรไทย** (UTF-8) ฝังอยู่ใน Unity Addressable Bundle
- ชื่อไฟล์บ่งบอกว่าม็อดเดอร์ทำการแก้ไขข้อความภาษา English ให้เป็นภาษาไทย (Override EN locale)

---

## 4. Font Analysis

### 4.1 Liberation Sans — ฟอนต์ Open Source ที่ดัดแปลงเพิ่มไทย
- **Full Name:** Liberation Sans Regular
- **Copyright:** `(c) 2010 Google Corporation` + `(c) 2012 Red Hat, Inc.`
- **Thai Coverage:** 87 codepoints (U+0E00–U+0E7F)
- **License:** SIL Open Font License (เดิมเป็น GPL+exception, ถูกเปลี่ยนเป็น OFL)
- **ขนาดดิบ:** 361,428 bytes

### 4.2 TMP SDF Rendering
ฟอนต์ถูกใช้ผ่านระบบ **TextMeshPro (TMP)** ของ Unity ในรูปแบบ **Signed Distance Field (SDF)**
- TMP จะอ่าน TTF ที่ฝังไว้ใน `resources.assets` แล้วสร้าง SDF Atlas ขึ้นมาเพื่อแสดงผลข้อความที่คมชัดในทุกขนาด
- พบ Asset ชื่อ `LiberationSans SDF - Drop Shadow` → แสดงว่าเกมใช้เอฟเฟกต์เงาตกกระทบ (Drop Shadow) กับฟอนต์

---

## 5. Text Analysis
- **ขนาด Bundle:** 19.4 MB (UnityFS format version 8)
- **Thai Characters:** **218,132 ตัวอักษร** (UTF-8)
- **ประเภทข้อความ:** UI ร้านสัก, ระบบจัดการ, เนื้อเรื่อง

### ตัวอย่างข้อความไทยในเกม:
```
"ที่ปรึกษา"
"พิมพ์ใบปลิว"
"ทำแคมเปญโฆษณาออนไลน์"
"ระดมความคิด"
"เรียนรู้ทักษะ"
"จัดการพนักงาน"
"เติมของ"
"ทำความสะอาด"
"เชิญออกจากร้าน"
"พักสักหน่อย"
```

---

## 6. Cross-Engine Comparison
เปรียบเทียบกับเกม Unity อื่นที่ใช้ Addressables:

| Feature | Tattoo Tycoon | Sea of Stars | SOS: Grand Bazaar |
|---|---|---|---|
| **Unity Version** | 2021.3 | 2021.x | 2020.x |
| **Bundle System** | Addressables | Addressables | Addressables |
| **Font in** | resources.assets | Bundle | Bundle |
| **Thai Font** | Liberation Sans | TMP Bitmap | TMP SDF |
| **Thai Chars** | 218K | ~150K | ~100K |
| **File Count** | 2 | 19 | Multi |

**จุดเด่น:** ม็อดนี้เรียบง่ายมาก — แค่ 2 ไฟล์ ทำให้ติดตั้งง่ายและเสี่ยงพังน้อย

---

## 7. Pipeline — ขั้นตอนสร้างม็อด

1. **Font Prep:** แก้ไข Liberation Sans TTF ด้วย FontForge เพิ่ม Thai glyphs (U+0E00–U+0E7F)
2. **Build TMP Asset:** ใช้ Unity Editor สร้าง TMP Font Asset จาก TTF ที่แก้แล้ว
3. **Replace resources.assets:** ใช้ UABEA หรือ AssetRipper แทนที่ Font Asset ใน `resources.assets`
4. **Text Translation:** ใช้ UABEA เปิด Addressable Bundle แล้วแก้ไขข้อความ English → Thai
5. **Rebuild Bundle:** Export bundle ใหม่จาก UABEA
6. **Deployment:** วาง 2 ไฟล์ (resources.assets + .bundle) ลงโฟลเดอร์เกม

---

## 8. Troubleshooting
- **ตัวหนังสือเป็นสี่เหลี่ยม:** `resources.assets` ไม่ได้ถูกแทนที่ หรือ TMP SDF Atlas ยังไม่ได้ถูก rebuild
- **ข้อความยังเป็นอังกฤษ:** ไฟล์ `.bundle` อาจไม่ตรงเวอร์ชัน หรือ hash ในชื่อไฟล์ไม่ตรงกับ catalog
- **เกมแครช:** เวอร์ชัน Unity ของ `resources.assets` ไม่ตรงกับเกม ต้องสร้างจากเวอร์ชันเดียวกัน (2021.3.45f2)

---

## 9. Required Tools
| Tool Name | Purpose | Source |
|---|---|---|
| UABEA | แก้ไข Unity Assets / Bundles | [GitHub: nesrak1] |
| AssetRipper | แกะ Unity Assets (ทางเลือก) | [GitHub] |
| FontForge | แก้ไข TTF เพิ่ม Thai glyphs | [FontForge.org] |
| Unity Editor 2021.3 | สร้าง TMP Font Asset | [Unity Hub] |

---

## 10. Extracted Assets
- **Liberation Sans TTF (ดัดแปลงเพิ่มไทยแล้ว):**
  - [LiberationSans-Regular.ttf](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unity_Engine/Games/Tattoo_Tycoon/Assets/Fonts/LiberationSans-Regular.ttf) (361 KB, 87 Thai codepoints)

---

## 11. M2M Protocol
**(สำหรับ AI Agent ที่ต้องการนำคัมภีร์ไปรันสร้างม็อดอัตโนมัติ)**

### ข้อจำกัดสำหรับ AI
- **Text Translation:** ⚠️ AI อ่านข้อความ UTF-8 จาก Bundle ได้ แต่การแก้ไข Unity Addressable Bundle ต้องใช้ UABEA หรือเครื่องมือเฉพาะ
- **Font Pipeline:** ⚠️ AI สามารถแก้ไข TTF ด้วย FontForge CLI ได้ แต่การ rebuild TMP SDF Asset ต้องทำผ่าน Unity Editor
- **Deployment:** ✅ AI สามารถก๊อปไฟล์ 2 ไฟล์ไปวางในโฟลเดอร์เกมได้ทันที
