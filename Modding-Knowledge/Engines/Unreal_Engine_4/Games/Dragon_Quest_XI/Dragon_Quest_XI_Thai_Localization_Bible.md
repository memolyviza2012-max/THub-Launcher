# Dragon Quest XI — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview

เอกสารนี้วิเคราะห์ม็อดไทย Dragon Quest XI จากไฟล์ต้นฉบับที่ส่งมาเพียงไฟล์เดียว คือ `pakchunk0-WindowsNoEditor_P_TH.pak` ขนาด 27,926,439 B. หลักฐาน footer ยืนยันว่าเป็น Unreal Engine 4 PAK v3 แบบ traditional PAK ไม่ใช่ UE5 IoStore; ผู้พัฒนาเกมคือ Square Enix.

รูปแบบม็อดคือ **archive replacement / custom overlay**: ใช้ PAK ชื่อ `pakchunk0` เพื่อให้เกม mount ทรัพยากรทับของเดิม แต่จาก PAK นี้เพียงไฟล์เดียวไม่อาจยืนยันตำแหน่งติดตั้งหรือ priority ที่เกมใช้ได้. ดัชนีและ payload ของทรัพยากรเป็น opaque bytes จึงต้องถือว่าเป็น pipeline เฉพาะเกม ไม่ใช่ workflow LocRes/FontFace ปกติจนกว่าจะเทียบกับ PAK เกมเวอร์ชันเดียวกัน.

---

## 2. Technical Stack

| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Unreal Engine 4; minor version ไม่พิสูจน์ได้จาก PAK ม็อดเดี่ยว |
| **Developer** | Square Enix |
| **Project Codename** | ไม่พบจากไฟล์ที่ให้มา |
| **Archive Format** | UE PAK v3, mount point `../../../`, 82 entries |
| **AES Encryption** | **No AES encryption on PAK index** — RePak รายงาน `encrypted index: false`, `encryption guid: None`; ไม่พบหลักฐาน AES-key requirement |
| **Compression** | None ที่ชั้น PAK — RePak และ UnrealPak รายงานทุก entry เป็น `compression: None` |
| **Font System** | ระบุไม่ได้จาก PAK นี้; ไม่พบ raw SFNT/TTF/OTF ที่ตรวจสอบผ่าน |
| **Thai Font Used** | ไม่ระบุ — ไม่มี metadata ฟอนต์ที่อ่านได้ใน source ที่ให้มา |
| **Text System** | Opaque proprietary payloads; ไม่พบ LocRes GUID หรือ path `.locres` ที่อ่านได้ |
| **Text Encoding** | ไม่ยืนยัน; ห้ามแปลง/เขียนเป็น UTF-8 หรือ UTF-16 โดยเดา |
| **Mod Complexity** | ★★★★★ — แม้ PAK แตกได้ แต่ path และ payload ไม่เป็น UE standard ที่ระบุชนิดได้ จึงต้องมี base-game comparison/parser ที่รองรับเกม |

---

## 3. โครงสร้างไฟล์ (File Architecture)

```text
Dragon Quest XI/
└── pakchunk0-WindowsNoEditor_P_TH.pak             27,926,439 B
    ├── UE PAK footer @ 0x01AAE3CB (last 44 B)
    │   ├── magic                  E1 12 6F 5A
    │   ├── version                3 (CompressionEncryption)
    │   ├── index offset           27,911,137 (0x01A9E3E1)
    │   ├── index size             15,258 B (0x3B9A)
    │   └── index SHA-1            B7DE92472C19288F584E4AE578A4B229E30A52AE
    └── 82 payload entries         27,906,791 B after unpack
        ├── 38 × leading bytes 3E 7C D5 61 06 00 00 00
        ├── 10 × leading bytes F1 FF FF FF FF FF FF FF
        ├──  6 × leading bytes B0 AB AB B0 FF F2 FF 7F
        └── 28 × other opaque binary headers
```

`repak.exe info` และ UnrealPak `-List` ให้ผลตรงกัน: mount point คือ `../../../`, index ไม่เข้ารหัส, ไม่มี compression และมี 82 files. ขนาดรวมที่ extractor ส่งออกคือ 27,906,791 B; PAK ทั้งก้อนมี SHA-256 `C04D73FD5C7A1CEDAB37CA44063E4E3C88BD287DB8C350DE73EA9F8F6CD5D56C`.

ข้อสังเกตสำคัญ: ชื่อ entry ที่ทั้งสอง parser แสดงเป็นอักขระผิดรูป/opaque อย่างสม่ำเสมอ ไม่ใช่ path UE ที่ใช้ได้ และไฟล์ที่แตกออกมาก็ไม่มีนามสกุลที่เชื่อถือได้. นี่เป็นข้อมูลที่พิสูจน์ได้จาก archive ไม่ใช่ผลของชื่อไฟล์ใน Windows เพียงอย่างเดียว จึงห้ามเดาให้เป็น `.uasset`, `.uexp`, `.locres` หรือ `.ufont`.

---

## 4. Font Analysis

### ผลการสกัด

สแกนทั้ง PAK และ payload ที่แตกออกมาทั้ง 82 รายการหา SFNT TrueType (`00 01 00 00`) และ OpenType CFF (`OTTO`). การยืนยันไม่ได้อาศัย signature สี่ไบต์อย่างเดียว: candidate ต้องมี table count 5–45 และ table directory ที่มี tag สมเหตุผลด้วย ผลคือ **0 valid installable TTF/OTF**.

ไม่มี raw `.ttf`/`.otf`, ไม่มี `.ufont` ที่ระบุได้, และไม่มี metadata ชื่อ family/weight/foundry จึงไม่สามารถตั้งชื่อฟอนต์หรือกล่าวอ้างว่าโม็ด swap ฟอนต์ตัวใดได้อย่างถูกต้อง. `Assets/Fonts/EXTRACTION_NOTE.txt` บันทึกเหตุผลและวิธีตรวจสอบไว้แล้ว.

### ผลกระทบต่อภาษาไทย

การที่ม็อดทำงานเป็นภาษาไทยไม่ได้พิสูจน์ว่ามีฟอนต์ใหม่ใน PAK นี้: อาจใช้ glyph จาก base game, payload เฉพาะเกม หรือมีไฟล์ติดตั้งที่ไม่ได้อยู่ในโฟลเดอร์ต้นทาง. ก่อนแก้ไขต้องทดสอบสระบน (`ิ`, `ี`, `ึ`, `ื`), สระล่าง (`ุ`, `ู`), วรรณยุกต์ (`่`, `้`, `๊`, `๋`) และการตัดบรรทัดใน build เป้าหมายจริง. ห้ามนำไฟล์ opaque ใด ๆ ไปเปลี่ยนนามสกุลเป็น `.ttf` เพราะไม่ผ่าน SFNT validation.

---

## 5. Text Analysis

ไม่มี entry ที่ระบุเป็น `.locres` ได้จาก path และไม่พบ LocRes magic GUID `0E 14 74 75 67 4A 03 FC 4A 15 90 9D C3 37 7F 1B` ใน payload ที่สกัด. ดังนั้นจึงยืนยันไม่ได้ว่าข้อความเป็น key/value, namespace หรือ string table แบบมาตรฐาน UE4.

ตัวเลขที่ยืนยันได้คือ 82 entries / 77 unique payload hashes (มี payload ขนาด 553,240 B ซ้ำกัน 6 entries). ความซ้ำนี้ชี้ว่า archive มีทรัพยากรร่วมกันหรือ placeholder ที่ซ้ำ แต่ไม่พอจะสรุปชนิดไฟล์. ไม่มี raw text dump ที่เชื่อถือได้จาก source นี้ จึงไม่มีจำนวน strings หรือการแบ่ง quest/dialogue ที่รายงานได้โดยไม่เดา.

ขั้นต่อไปที่ถูกต้องคือต้องมี PAK ต้นฉบับของเกม release เดียวกัน: เปรียบเทียบ entry offset, size และ SHA-1, จับคู่ payload ที่เปลี่ยน, แล้วใช้ parser ที่รองรับ asset serialization ของ Dragon Quest XI. เมื่อพบ text container จริง ค่อยตรวจ BOM/UTF-8/UTF-16 และใช้ serializer ของ container นั้นเท่านั้น.

---

## 6. Cross-Engine Comparison

เมื่อเทียบกับ `Unreal_Engine_4/Games/Borderlands_3/Borderlands_3_Thai_Localization_Bible.md` ในฐานความรู้: Borderlands 3 เป็น PAK ที่อ่าน path ได้, มี `.locres` พร้อม GUID มาตรฐาน, และมี raw TrueType FontFace ที่ตรวจแบบ table directory ได้. Dragon Quest XI ใช้ PAK v3 เช่นกันและ index ไม่เข้ารหัสเหมือนกัน แต่แตกต่างอย่างมีนัยสำคัญตรงที่ 82 paths/payloads ไม่เปิดเผยชนิดทรัพยากรตามมาตรฐาน.

จึงนำ pipeline ของ Borderlands 3 (แก้ LocRes และแทน raw TTF โดยรักษา path) มาใช้ตรง ๆ ไม่ได้. ส่วนที่นำมาใช้ร่วมกันได้คือการตรวจ footer, index encryption, compression, hash และการ pack/repack แบบ deterministic; ส่วนการแก้ข้อความ/ฟอนต์ต้องรอการจับคู่กับ base assets ของ Dragon Quest XI.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด

### Archive and base comparison pipeline

1. สำรอง PAK เกมเดิมและบันทึก SHA-256 ของทั้ง base และม็อด; ห้ามเขียนทับ source เดียวที่ใช้วิเคราะห์.
2. ใช้ `repak.exe info` ตรวจ PAK footer และ encryption ก่อนทุกครั้ง. สำหรับไฟล์ที่ตรวจครั้งนี้: version 3, index unencrypted, compression none.
3. ใช้ RePak/UnrealPak list ทั้งคู่และเก็บ offset, size, SHA-1 ของ 82 entries. หากชื่อยัง opaque ให้ใช้ tuple เหล่านี้เป็นตัวระบุชั่วคราวแทน filename.
4. รับ PAK base จาก game build เดียวกัน, ทำ inventory แบบเดียวกัน แล้วจับคู่ entry ที่ต่างกัน. อย่าใช้ offset ข้าม build เป็นตัวระบุถาวร.
5. เปิดเฉพาะ asset ที่จับคู่แล้วด้วย parser ที่รองรับ Dragon Quest XI; ตรวจ magic bytes ของ output ก่อนกำหนด extension ทุกครั้ง.

### Text pipeline

1. เมื่อพบ text container จริง ให้บันทึก magic, byte order, string count และ token/control-code ก่อนแก้ไข.
2. ใช้ exporter/importer เฉพาะ container นั้น; อย่าแก้ bytes แบบ search-replace.
3. เก็บ placeholders (`{}`, `%s`, markup), line breaks และ IDs เดิมทุกตัว; แปลเฉพาะ value.
4. ตรวจ encoding ด้วย output parser แล้ว repack โดยคง path/entry metadata ที่เกมต้องการ.

### Font pipeline

1. หลังจับคู่กับ base assets ให้ค้นหา FontFace/texture atlas/metadata ที่เปลี่ยนจริง.
2. หากพบ SFNT ให้ตรวจ table directory และ `cmap` ก่อนจึงคัดลอกเป็น `.ttf`/`.otf`; จัดเก็บ family/weight/license ลง Bible.
3. หากเป็น atlas/bitmap ให้เก็บ texture และ mapping คู่กัน, บันทึกความละเอียดและ glyph metrics; อย่าพยายาม “แปลง” atlas เป็นฟอนต์เวกเตอร์.
4. ทดสอบ Thai combining marks, fallback glyph, dialog box overflow, menu และ subtitle ในเกมจริงก่อนเผยแพร่.

---

## 8. Troubleshooting

| อาการ | สาเหตุที่เป็นไปได้ | วิธีตรวจ/แก้ |
|---|---|---|
| เกมไม่โหลดม็อด | ตำแหน่ง PAK หรือ priority ไม่ตรง build | ตรวจคำแนะนำติดตั้งของม็อดและ PAK base; อย่าสรุปจากชื่อ `P_TH` ว่าเท่ากับ `_P` ของ UE ทั่วไป |
| UnrealPak แสดงชื่อไฟล์เพี้ยน | path metadata เป็น opaque/custom | ใช้ offset + size + SHA-1 เปรียบเทียบกับ base; อย่าตั้งชื่อ asset เอง |
| แก้ข้อความแล้ว crash | เขียน container หรือ serialization ผิด | กลับไปใช้ parser/serializer ที่พิสูจน์ format แล้ว; หลีกเลี่ยง raw hex edit |
| ภาษาไทยเป็นสี่เหลี่ยม | font/glyph source ไม่อยู่ใน PAK นี้หรือ mapping ผิด | เปรียบเทียบ base assets และหา font/atlas จริงก่อน; ตรวจ `cmap` หรือ glyph mapping |
| สระ/วรรณยุกต์เหลื่อม | shaping/metrics ของ font หรือ atlas ไม่รองรับ | ทดสอบอักษรฐานร่วมสระและวรรณยุกต์, ปรับ metrics/mapping ใน asset ต้นทางที่ระบุได้ |
| PAK ใหม่ถูกปฏิเสธ | version, mount point, index หรือ file metadata เปลี่ยน | repack จาก inventory/build เดียวกัน, ตรวจ footer v3 และทดสอบบนสำเนาเกม |

---

## 9. Required Tools

| เครื่องมือ | หน้าที่ | แหล่งที่มา |
|---|---|---|
| `repak_cli` | อ่าน PAK info/list/unpack/repack และรายงาน encryption/compression | เครื่องมือภายใน `E:\Mod_Workspace\Tool\repak_cli\repak.exe` |
| UnrealPak | cross-check PAK listing และสร้าง PAK ตาม UE build ที่เข้ากัน | Unreal Engine toolchain / `E:\Mod_Workspace\Tool\UE4\...\UnrealPak.exe` |
| FModel หรือ parser ที่รองรับ Dragon Quest XI | เปิด asset หลังจับคู่กับ base game | ต้องใช้เวอร์ชันที่รองรับ serialization ของเกม |
| Hex viewer / Python | ตรวจ magic bytes, footer, offsets, hashes และ font table directory แบบ read-only | Python standard library |
| FontTools | ตรวจ `cmap`/name tables เมื่อพบ SFNT ที่ผ่าน validation | https://fonttools.readthedocs.io/ |

---

## 10. Extracted Assets

| Asset | ที่เก็บ | Metadata / สถานะ |
|---|---|---|
| Source PAK (raw preservation) | `Assets/Raw/pakchunk0-WindowsNoEditor_P_TH.pak` | 27,926,439 B; SHA-256 `C04D73FD5C7A1CEDAB37CA44063E4E3C88BD287DB8C350DE73EA9F8F6CD5D56C`; UE PAK v3, 82 entries |
| Font extraction note | `Assets/Fonts/EXTRACTION_NOTE.txt` | สแกนทั้ง archive และ 82 extracted payloads; ไม่พบ valid TTF/OTF ที่คัดลอก/ติดตั้งได้ |

ไม่ได้จัดเก็บ payload ที่แตกออกมาเป็น asset final เพราะไม่มี filename/format ที่พิสูจน์ได้ และการตั้งชื่อหรือนามสกุลใหม่จะทำให้ฐานความรู้มีข้อมูลเทียม. เก็บ raw PAK ที่ hash ได้แทนเพื่อให้ทำซ้ำการแตกและเทียบกับ base game ได้.
