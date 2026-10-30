# Deathloop (Dead Loop) — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer) — with Asset Extraction

---

## 1. Overview
เอกสารนี้อธิบายกลไกการม็อดภาษาไทยของเกม **Deathloop** อย่างละเอียดเชิงลึก จากการวิเคราะห์ไฟล์ม็อดโดยตรง เกมนี้สร้างด้วย **Void Engine** (พัฒนาโดย Arkane Studios พัฒนาต่อยอดจาก id Tech 5/6) ม็อดใช้วิธีการ **แพ็กทรัพยากรใหม่ทั้งหมด (Full Resource Repacking)** เพื่อแทรกข้อความภาษาไทยและฟอนต์เข้าไปในเกม

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Void Engine (Arkane Studios) — สืบทอดมาจาก id Tech 5/6 |
| **Archive Format** | `.resources` (Data Chunks) + `.index` (Master Resource Map) |
| **Serialization Magic** | `05 53 45 52` (`.index`) / `04 53 45 52` (`.resources`) — `SER` = id Tech Serialized Resource |
| **Compression** | OodleLZ (ภายใน `.resources` chunks — พบ magic `OOD` = `4F 4F 44` ที่ byte offset 4) |
| **UI Framework** | **Iggy** (Scaleform alternative) — ไฟล์ `.iggy` (เช่น `lib_loc_english_font.iggy`) |
| **Font Format** | **Bitmap Font** — `.tga` atlas + `.dat` metrics (เช่น `fonts/futura_pt_extra_bold/64_df.tga` + `.dat`) |
| **Localization Approach** | Full Archive Repacking (แทนที่ `.resources` chunks + สร้าง `.index` ใหม่) |

---

## 3. Void Engine Resource Architecture

### 3.1 ระบบไฟล์ของ Void Engine
Void Engine ใช้ระบบ **Streaming Resource** แบ่งเป็น 2 ส่วนหลัก:

```
master_resources.index   ←── สารบัญกลาง (บอกว่าไฟล์ไหนอยู่ chunk ไหน, offset เท่าไหร่)
    │
    ├── rsc_decl_0.resources      ←── Declaration data (ข้อมูล config, shader definitions)
    ├── rsc_gen_0_0.resources     ←── General data chunk 0 (ข้อความ, เสียง, โมเดล)
    ├── rsc_gen_0_1.resources     ←── General data chunk 1 (ข้อมูลเพิ่มเติม)
    └── rsc_images_0_2.resources  ←── Image/Texture data (font atlas, textures)
```

### 3.2 Binary Header ที่พบ

| ไฟล์ | Magic Bytes | ความหมาย |
|---|---|---|
| `master_resources.index` | `05 53 45 52` | SER v5 — Index/Map format |
| `rsc_decl_0.resources` | `04 53 45 52` | SER v4 — ข้อมูลดิบ (Plaintext declarations) |
| `rsc_gen_0_*.resources` | `04 53 45 52 4F 4F 44` | SER v4 + **OOD** (Oodle compressed data) |
| `rsc_images_0_2.resources` | `04 53 45 52 4F 4F 44` | SER v4 + **OOD** (Oodle compressed textures) |

> **สำคัญ:** `rsc_decl_0.resources` **ไม่ได้ถูกบีบอัด** (ข้อมูลภายในเป็น plaintext เช่น `{ semantic float3 in(v) }`) ในขณะที่ `rsc_gen` และ `rsc_images` ถูก **บีบอัดด้วย OodleLZ**

---

## 4. Localization Pipeline — การทำงานเชิงลึก

### 4.1 ระบบ Localization ของ Void Engine
จากข้อมูลที่แกะได้จาก `master_resources.index` พบว่า Deathloop รองรับภาษาต่อไปนี้:

```
arabic, brazilian, english, french, german, italian, 
japanese, korean, mexican, polish, russian, 
simplified_chinese, spanish, traditional_chinese
```

โครงสร้าง Localization อยู่ภายใต้:
```
generated/decls/localized/{language}/speechscene/speech/scene/...
generated/decls/localized/{language}/speechbarks/speech/speech_barks/...
```

> **ข้อสังเกต:** ไม่มีโฟลเดอร์ `thai` ในระบบเดิมของเกม ดังนั้นผู้ทำม็อดน่าจะ**ทับข้อมูลภาษาอังกฤษ (english) โดยตรง** แทนการเพิ่มภาษาใหม่

### 4.2 ระบบ UI & Font
พบไฟล์ UI ที่สำคัญ:
- **`ui/lib_loc_english_font.iggy`** — ไฟล์ Iggy (Scaleform-like) ที่กำหนดฟอนต์ภาษาอังกฤษ ผู้ทำม็อดต้องแก้ไขไฟล์นี้เพื่อให้ระบบ UI โหลดฟอนต์ที่รองรับภาษาไทย

พบฟอนต์เกมเดิม 2 ตัว:
- **`fonts/futura_pt_extra_bold/64_df.tga`** + `.dat` — ฟอนต์หลัก (ตัวหนา)
- **`fonts/futura_pt_medium/64_df.tga`** + `.dat` — ฟอนต์รอง (ตัวปกติ)

โครงสร้างฟอนต์แต่ละตัวประกอบด้วย:
```
fonts/{font_name}/
    ├── 64_df.tga       ←── ภาพ Font Atlas (Distance Field format)
    ├── 64_df.dat       ←── ข้อมูล Metrics (พิกัด glyph, kerning, size)
    └── 64_df.tga.decl  ←── Material declaration (บอก engine ว่าโหลดภาพนี้ยังไง)
```

> **Distance Field Font:** ฟอนต์ใช้เทคนิค **Signed Distance Field (SDF)** ซึ่งเก็บข้อมูลระยะห่างจากขอบตัวอักษรแทนที่จะเก็บพิกเซลจริง ทำให้สามารถขยาย/ย่อขนาดได้โดยไม่เบลอ

### 4.3 ระบบเสียงพูด (Speech)
Void Engine แยกข้อมูลเสียงพูดเป็น:
- **SpeechScene** — บทพูดในฉากคัตซีน
- **SpeechBarks** — เสียงพูดสั้นๆ ของ NPC (เช่น ลาดตระเวน, ตกใจ)

แต่ละอันมีไฟล์ `.decl` แยกตามภาษาและชื่อฉาก

### 4.4 Font Effect System
พบระบบ Font Effect ที่ต้องคำนึงถึง:
- `fontfxglowparms` — เอฟเฟกต์เรืองแสง
- `fontfxglowcolor` — สีเรืองแสง
- `fontfxoutlinecolor` — สีขอบตัวอักษร
- `fontfxparms` — พารามิเตอร์เอฟเฟกต์ทั่วไป
- `fontoutlineglowshadow` — Shader สำหรับเงาและขอบ
- `worldtextfont` — ฟอนต์สำหรับข้อความในเกม 3D

---

## 5. ไฟล์ม็อดที่ให้มา — วิเคราะห์ทีละไฟล์

| ไฟล์ | ขนาด | เนื้อหา |
|---|---|---|
| `master_resources.index` | 60.7 MB | สารบัญหลักที่สร้างใหม่ บอก engine ว่าทรัพยากรทุกชิ้นอยู่ตรงไหนใน `.resources` chunks |
| `rsc_decl_0.resources` | 28.7 MB | Declarations — config, shader defs, material defs (ไม่บีบอัด, plaintext) |
| `rsc_gen_0_0.resources` | 381.3 MB | ข้อมูลหลัก — **ตารางข้อความภาษาไทย**, เสียง, โมเดล (บีบอัด OodleLZ) |
| `rsc_gen_0_1.resources` | 17.6 MB | ข้อมูลเสริม — อาจมีสคริปต์ UI หรือข้อมูลเพิ่มเติม (บีบอัด OodleLZ) |
| `rsc_images_0_2.resources` | 518.9 MB | **ภาพ Font Atlas ภาษาไทย** + ภาพพื้นผิวอื่นๆ (บีบอัด OodleLZ) |

---

## 6. ขั้นตอนที่ผู้ทำม็อดน่าจะใช้ (Reconstructed Pipeline)

```
1. แตกไฟล์ .resources ของเกมต้นฉบับ ด้วย Void Engine Resource Unpacker
       ↓
2. ค้นหาและแก้ไข String Tables ภายใน rsc_gen chunks
   (ทับข้อความอังกฤษด้วยข้อความไทย)
       ↓
3. สร้าง Font Atlas ใหม่:
   - เปิด fonts/futura_pt_*/64_df.tga ด้วย image editor
   - วาดตัวอักษรไทย (สระ, พยัญชนะ, วรรณยุกต์) ลงใน SDF atlas
   - อัปเดต 64_df.dat เพื่อเพิ่ม glyph metrics ของตัวอักษรไทย
       ↓
4. แก้ไข ui/lib_loc_english_font.iggy เพื่อให้ UI โหลดฟอนต์ใหม่
       ↓
5. แพ็กทรัพยากรกลับเป็น .resources chunks ด้วย OodleLZ compression
       ↓
6. สร้าง master_resources.index ใหม่ (อัปเดต offsets, sizes ทั้งหมด)
       ↓
7. วางไฟล์ทั้ง 5 ไฟล์ทับไฟล์เดิมในโฟลเดอร์เกม
```

---

## 7. Required Tools for Modding

| เครื่องมือ | หน้าที่ |
|---|---|
| **Void Engine Resource Unpacker** (QuickBMS + Void Engine scripts) | แตกไฟล์ `.resources` และ parse `.index` |
| **Oodle Decompressor** | คลายการบีบอัด OodleLZ ภายใน `.resources` chunks |
| **Iggy Editor / Flash Decompiler** | แก้ไขไฟล์ `.iggy` สำหรับ UI font mapping |
| **SDF Font Generator** (เช่น Hiero, msdf-atlas-gen) | สร้าง Signed Distance Field font atlas ใหม่ที่มีตัวอักษรไทย |
| **Image Editor** (Photoshop/GIMP + DDS/TGA plugin) | แก้ไข font atlas `.tga` โดยตรง |
| **Hex Editor** (HxD, 010 Editor) | แก้ไข `.dat` glyph metrics และตรวจสอบ binary structure |
| **Void Engine Repacker** | แพ็กไฟล์กลับ + สร้าง `master_resources.index` ใหม่ |

---

## 8. Font Atlas — รายชื่อครบถ้วน

### 8.1 Font Atlas Paths (จาก transmap declarations)
| Path | ลักษณะ |
|---|---|
| `fonts/futura_pt_extra_bold/64_df.tga` | ★ ฟอนต์หลัก (Bold) |
| `fonts/futura_pt_medium/64_df.tga` | ★ ฟอนต์รอง (Medium) |
| `fonts/courier/64_df.tga` | Monospace |
| `fonts/handelson_two/64_df.tga` | Handwriting/Cursive (EN) |
| `fonts/arabic/handelson_two/64_df.tga` | Arabic variant |
| `fonts/japanese/handelson_two/64_df.tga` | Japanese variant |
| `fonts/korean/handelson_two/64_df.tga` | Korean variant |
| `fonts/russian/handelson_two/64_df.tga` | Russian variant |
| `fonts/schinese/handelson_two/64_df.tga` | Simplified Chinese |
| `fonts/tchinese/handelson_two/64_df.tga` | Traditional Chinese |

> **10 Font Atlas files** — ฟอนต์หลัก 3 ตัว (Futura PT Bold, Futura PT Medium, Courier) + Handelson Two × 7 locale variants

### 8.2 Font Effect System
Void Engine มีระบบ Font Effects ที่ซับซ้อน:

| พารามิเตอร์ | หน้าที่ |
|---|---|
| `fontfxglowparms` | เอฟเฟกต์เรืองแสง |
| `fontfxglowcolor` | สีเรืองแสง |
| `fontfxoutlinecolor` | สีขอบตัวอักษร |
| `fontfxparms` | พารามิเตอร์ทั่วไป |
| `fontoutlineglowshadow` | Shader เงา+ขอบ |
| `worldtextfont` | ฟอนต์ 3D world text |

---

## 9. สถิติม็อด

| ข้อมูล | จำนวน |
|---|---|
| **ไฟล์ม็อด** | 5 ไฟล์ (.index + 4 .resources) |
| **ขนาดรวม** | **~1,007 MB (~1 GB)** |
| **Archive Format** | SER v4/v5 |
| **Compression** | OodleLZ |
| **Font Format** | **SDF Bitmap** (TGA + DAT) ★ |
| **Font Atlas Paths** | 10 (3 fonts × locale variants) |
| **UI Framework** | Iggy (Scaleform alternative) |
| **Supported Languages** | 14 (ไม่มี Thai) |
| **Mod Strategy** | English locale override |
| **Font Extraction** | ❌ ไม่สามารถดึง TTF ได้ (SDF bitmap + Oodle) |

---

## 10. ความพิเศษของม็อดนี้

### 10.1 SDF Bitmap Font (ไม่ใช่ TTF/OTF)
Deathloop ใช้ **Signed Distance Field font atlas** — ฟอนต์ถูก pre-render เป็นภาพ TGA กับ glyph metrics ใน DAT — ไม่ใช่ vector font (TTF/OTF) ทำให้:
- ❌ ไม่สามารถดึงฟอนต์ TTF/OTF ออกมาได้
- ✅ แต่สามารถสร้าง SDF atlas ใหม่ที่มีภาษาไทยได้
- Font atlas คือ **ภาพที่มีตัวอักษรทุกตัววาดเรียงกัน** + ไฟล์ DAT บอกตำแหน่งพิกเซลของแต่ละ glyph

### 10.2 Full Archive Repacking (~1 GB)
ม็อดนี้ **repack ทรัพยากรเกมทั้งหมด** 5 ไฟล์ รวม ~1 GB — ซับซ้อนและใหญ่ที่สุดในคลังความรู้

### 10.3 Oodle Compression
ข้อมูลทั้งหมด (ยกเว้น rsc_decl_0) ถูก compress ด้วย **OodleLZ** ซึ่งเป็น proprietary — ต้องใช้ `oo2core_6_win64.dll` ในการ decompress

### 10.4 Iggy UI Framework
Void Engine ใช้ **Iggy** (ไม่ใช่ Scaleform) สำหรับ UI — ไฟล์ `lib_loc_english_font.iggy` เป็นตัวกำหนด font binding

---

## 11. เปรียบเทียบ

| เกม | Engine | Font Format | Font Extracted | Mod Size | Complexity |
|---|---|---|---|---|---|
| **Deathloop** | Void Engine | SDF Bitmap (TGA+DAT) | ❌ (Oodle+SDF) | **1 GB** | ★★★★★ |
| **Gothic Remake** | UE5+Alkimia | TTF in LCACHE | 6 TTF | 1.8 MB | ★★★★☆ |
| **Clair Obscur** | UE5 | TTF in PAK v11 | 16 TTF | 5.5 MB | ★★★☆☆ |
| **Cronos** | UE5 | TTF in PAK v4 | 11 TTF | 2.2 MB | ★★★☆☆ |
| **STALKER 2** | UE5 (GSC) | None (text only) | ❌ | 33 MB | ★★★★☆ |

---

## 12. Conclusion
ม็อดภาษาไทยของ Deathloop ใช้วิธี **Full Archive Repacking** ที่ซับซ้อนที่สุดในคลังความรู้ เนื่องจาก:

1. **SDF Bitmap Font** — ไม่ใช่ TTF/OTF ดังนั้นไม่สามารถดึงฟอนต์จริงออกมาได้
2. **OodleLZ Compression** — ข้อมูลถูก compress ด้วย proprietary codec
3. **Iggy UI** — ต้องแก้ไข font bindings ผ่าน .iggy format
4. **Full Repack** — ม็อดต้อง repack ทรัพยากรทั้งหมด (~1 GB) ไม่ใช่แค่ patch
5. **English Override** — ทับข้อความอังกฤษ (ไม่มี Thai locale ในเกม)
6. **10 Font Atlas** — ครอบคลุม Futura PT (Bold+Medium), Courier, Handelson Two × 7 locales

ขนาดไฟล์ม็อดรวม **~1 GB** สะท้อนให้เห็นว่าเป็นการ repack ทรัพยากรเกมทั้งหมดจริงๆ ไม่ใช่แค่แพตช์บางส่วน

---

## 13. Extracted Assets

- **Fonts:** ❌ **ไม่สามารถดึง TTF/OTF ได้** — Deathloop ใช้ SDF bitmap font (TGA+DAT) ที่ถูก Oodle compressed
  - [EXTRACTION_NOTE.txt](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Void_Engine/Games/Deathloop/Assets/Fonts/EXTRACTION_NOTE.txt)

- **Texts:** ❌ ข้อความถูก Oodle compressed ใน rsc_gen_0_0.resources
  - [Extraction_Note.txt](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Void_Engine/Games/Deathloop/Assets/Texts/Extraction_Note.txt)

- **Configs / Metadata:**
  - [Font_Declarations.txt](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Void_Engine/Games/Deathloop/Assets/Configs/Font_Declarations.txt) — 10 font atlas paths + font effect system
  - [Language_Listing.txt](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Void_Engine/Games/Deathloop/Assets/Configs/Language_Listing.txt) — 14 supported languages + localization structure
