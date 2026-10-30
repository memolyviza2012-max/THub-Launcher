# คัมภีร์สร้างม็อดภาษาไทย Dragon's Dogma: Dark Arisen

> เอกสารฉบับผลิตจริงของโปรเจกต์ NodNuatTranslator  
> สถานะ: สำเร็จและจัดทำ Release v1.0.0 แล้ว  
> ปรับปรุงล่าสุด: 15 กันยายน 2026 (Asia/Bangkok)

---

## 1. ข้อมูลโครงการ

| รายการ | ค่า |
|---|---|
| เกม | Dragon's Dogma: Dark Arisen |
| แพลตฟอร์มที่ทดสอบ | Steam / Windows PC |
| Steam App ID | `367500` |
| เวอร์ชันไฟล์เกม | `DDDA.exe 1.0.0.0` |
| Steam build ที่ทดสอบ | `2364871` |
| เอนจิน | Capcom MT Framework |
| เวอร์ชันม็อด | `v1.0.0` |
| ผู้สร้างและผู้แปล | หน๊ด หนวด translator |
| โฟลเดอร์เกมที่ทดสอบ | `F:\SteamLibrary\steamapps\common\DDDA` |
| Workspace | `E:\Mod_Workspace\Dragon's_Dogma_Dark_Arisen` |

### สถิติข้อความฉบับเผยแพร่

- ฐานข้อมูล CSV ทั้งหมด `50,142` แถว จาก `9,684` ไฟล์ GMD
- แถวต้นฉบับที่มีข้อความและแปลได้ `46,913` แถว
- แถวที่มีคำแปลไทย `46,802` แถว หรือ `99.76%` ของข้อความที่แปลได้
- ข้อความที่ยังเว้นคำแปลและให้เกมใช้ภาษาอังกฤษเดิม `111` แถว
- ช่องว่าง/ช่องระบบ/รายการสงวนที่ไม่มี source `3,229` แถว
- ข้อความแบบภาพใน UI และโลโก้ได้รับการแก้แยกจากยอด CSV ข้างต้น

ตัวเลขทั้งหมดตรวจจากไฟล์:

`02_Translation_Workspace\DDDA_Thai_Full_VALIDATED_20260902.csv`

---

## 2. สรุปปัญหาหลักและคำตอบสุดท้าย

เกมนี้ไม่ได้มี “ข้อความ” เพียงชนิดเดียว แต่แยกเป็นสามระบบ:

1. **ข้อความแบบ Dynamic** — อยู่ใน GMD ภายใน `message.pck`
2. **รูปอักษรที่เกมใช้วาด Dynamic Text** — อยู่ใน TEX font atlas และตาราง GFD ภายใน ARC
3. **ข้อความที่อบเป็นภาพแล้ว** — เช่นชื่อหน้าเมนู Pause, Quests, Equipment, Status, Credits และโลโก้ ซึ่งอยู่ใน UI texture atlas

ดังนั้นการแก้เฉพาะ CSV ทำให้เกมมีข้อมูลภาษาไทย แต่เกมยังวาดอักษรไทยไม่ได้ หรือบางหัวข้อยังเป็นอังกฤษเพราะเป็นภาพ การผลิตม็อดสำเร็จจึงต้องแก้ครบทั้งสามชั้นและติดตั้งไฟล์จริงเจ็ดไฟล์

### ไฟล์ Runtime ขั้นสุดท้าย

| หน้าที่ | พาธสัมพัทธ์จากโฟลเดอร์เกม |
|---|---|
| ข้อความ GMD ที่แพ็กแล้ว | `nativePC\rom\message\message.pck` |
| ฟอนต์และ GFD ชุดหลัก | `nativePC\rom\bbsrpg_core.arc` |
| ฟอนต์และ GFD ชุดรอง | `nativePC\rom\bbs_rpg.arc` |
| UI atlas และโลโก้หน้า Title | `nativePC\rom\title.arc` |
| UI atlas ที่หน้าเกมเรียกใช้ | `nativePC\rom\game_main.arc` |
| UI atlas ของ Top/Pause Menu | `nativePC\rom\gui\GUIuGUITopMenu.arc` |
| UI atlas ของหน้า Title | `nativePC\rom\gui\GUIuGUITitle.arc` |

ไม่ต้องใช้ DLL, loader, Fluffy Mod Manager หรือ SigBypass ในแพ็กเกจผู้เล่น เกมอ่าน ARC/PCK ที่เขียนทับโดยตรง

---

## 3. โครงสร้าง Workspace ที่แนะนำ

```text
Dragon's_Dogma_Dark_Arisen\
├─ 01_Original_Backup\       ไฟล์ต้นฉบับและ checkpoint ก่อน deploy
├─ 02_Translation_Workspace\ CSV ต้นฉบับ/ไฟล์แปล/ไฟล์ validated
├─ 03_Font_and_UI\           font atlas, GFD, carrier mapping, UI PNG/TEX
├─ 04_Packed_Mod\            build ระหว่างพัฒนา
├─ 05_Scripts_and_Tools\     extractor, validator, packer, verifier
└─ 06_Releases\              แพ็กเกจ ZIP พร้อมแจก
```

กฎสำคัญคือห้ามสร้าง build ทับไฟล์ต้นฉบับโดยตรง ทุกครั้งต้องสร้างใน workspace ตรวจให้ผ่าน สำรองไฟล์เกม แล้วจึง deploy

---

## 4. รูปแบบไฟล์ MT Framework ที่เกี่ยวข้อง

### 4.1 ARC v7

- Magic: `ARC\x00`
- Version: `7`
- แต่ละ resource มักบีบอัดด้วย zlib
- ตาราง resource เก็บชื่อ ชนิด ขนาดบีบอัด ขนาดจริง และตำแหน่งข้อมูล
- เกมไวต่อ offset, order, entry metadata และ archive layout มาก

การ pack ARC ทั้งก้อนด้วยเครื่องมือทั่วไปเคยทำให้เกิด `Fatal error: Failed open file` กับไฟล์ที่ไม่เกี่ยวข้อง เช่นเสียง `.srq` และโมเดล `.mod` เพราะ layout เปลี่ยน แม้ resource เป้าหมายจะถูกต้องก็ตาม

### 4.2 PCK/GMD

`message.pck` เป็น container ข้อความซึ่งมี GMD จำนวนมาก ชุดภาษาอังกฤษถูกเลือกจาก language id ที่ตรงกับ English แล้วส่งออกเป็น CSV

Schema ที่ใช้กับ TRun/TStudio:

```text
key,source,translation,context,file_path
```

- `key` เป็นตัวระบุเฉพาะ ห้ามแก้
- `source` คือข้อความอังกฤษอ้างอิง ห้ามแก้
- `translation` คือช่องภาษาไทย
- `context` และ `file_path` ใช้ผูกคำแปลกลับ GMD ที่ถูกต้อง ห้ามสลับแถว

### 4.3 TEX

- Magic: `TEX\x00`
- ข้อมูลภาพที่ใช้ในงานนี้เข้ารหัส BC3/DXT5
- ต้องคง header 20 ไบต์แรกและชนิด TEX ของ resource เดิม
- Alpha สำคัญมากทั้งกับตัวอักษร ขอบ เงา และส่วนโปร่งใส

### 4.4 GFD

GFD เป็นตาราง mapping glyph ของฟอนต์ ระบุ codepoint ตำแหน่งใน atlas และ metric ที่ใช้วางตัวอักษร เกมนี้มี glyph เดิม `4,055` รายการ แต่ไม่มี Thai shaping ที่เชื่อถือได้

---

## 5. ขั้นตอนสำรวจและพิสูจน์เส้นทางข้อความ

1. สแกน `nativePC` และตรวจ magic/header ของ ARC, TEX, PCK และ GFD
2. สร้าง extractor เฉพาะเกม:
   - `05_Scripts_and_Tools\dragons_dogma_dark_arisen_unpacker.py`
3. แตก `message.pck` ได้ `9,684` GMD และ `50,142` CSV rows
4. สร้าง packer เฉพาะเกม:
   - `05_Scripts_and_Tools\dragons_dogma_dark_arisen_packer.py`
5. ทดสอบ no-op round-trip โดยไม่ใส่คำแปล ผล PCK ต้องเหมือนต้นฉบับแบบ byte-for-byte
6. ทำ POC ข้อความสั้นก่อน เพื่อแยกให้ชัดว่าอาการไม่แสดงไทยมาจาก text path หรือ font path

No-op round-trip เป็น gate ที่สำคัญที่สุดก่อนเริ่มแปล เพราะพิสูจน์ว่า parser/packer เข้าใจโครงสร้างเดิมโดยไม่ทำลายข้อมูล

---

## 6. ปัญหา TRun ที่พบและระบบป้องกัน

ระหว่างแปลพบว่าเครื่องมือแปลอัตโนมัติอาจ:

- ย้าย ลบ หรือสลับตำแหน่ง tag ของเกม
- สร้างข้อความเทียม เช่น `[TAG_n]`
- แทรก marker เช่น `PCK_message_...`
- เลื่อน translation ไปอยู่คนละ key
- เปลี่ยน `source`, `context` หรือ `file_path`
- เติมคำแปลลงในแถวที่ควรเป็นค่าว่าง/ระบบ

จึงเพิ่มเครื่องมือ:

- `sanitize_trun_output.py` — ทำความสะอาด output
- `validate_tstudio_csv.py` — ตรวจ schema, key และ tag
- `test_translation_guards.py` — ทดสอบ guard cases
- `verify_clean_package.py` — ตรวจ package หลังแพ็ก
- `pack_validated_csv_20260914.py` — แพ็กเฉพาะ CSV ที่ผ่าน validation

### กฎ Validation ก่อนแพ็ก

1. จำนวนแถวต้องเท่าต้นฉบับ `50,142`
2. `key` ต้องครบ ไม่ซ้ำ และอยู่แถวที่ถูกต้อง
3. `source`, `context`, `file_path` ต้องเท่าต้นฉบับ
4. tag/placeholder ที่จำเป็นต้องมีครบและลำดับถูกต้อง
5. ห้ามพบ `PCK_message_` หรือ `[TAG_n]` ที่เครื่องมือสร้างเอง
6. แถว source ว่างต้องคงเป็นระบบ/ว่างตามเดิม
7. translation ว่างให้ fallback เป็น English ไม่สร้างข้อความเสีย
8. หลังแพ็กต้องเปิด PCK กลับและตรวจจำนวน GMD/ข้อความซ้ำ

ผลสุดท้ายมี GMD ที่ต้องเขียนใหม่ `1,267` รายการ และ GMD ที่ไม่เปลี่ยน `8,417` รายการ จึงควรรักษา byte ของส่วนที่ไม่เกี่ยวข้องไว้

---

## 7. วิธีทำให้ Dynamic Text แสดงภาษาไทย

### 7.1 เหตุผลที่ใส่ Unicode ไทยตรง ๆ ไม่พอ

ตัว renderer ของ MT Framework รุ่นนี้ไม่จัดรูปภาษาไทยได้สมบูรณ์ และ font mapping ที่ GUI ใช้อ้างไปยัง `id/common/font/ddfont_jpn` ไม่มี glyph ไทยครบ การใส่ UTF-8 ไทยใน GMD จึงเคยเกิดอาการว่าง ตัวแตก สระ/วรรณยุกต์ซ้อนผิด หรือแสดงเป็นรูปร่างอื่น

### 7.2 Carrier Encoding

ทางแก้ที่ใช้จริงคือแปลง “กลุ่มอักษรไทยที่จัดรูปแล้ว” เป็น codepoint ตัวพาหะ CJK ที่เกมมี cell รองรับอยู่แล้ว

กระบวนการ:

1. เก็บ cluster ไทยทั้งหมดจากคำแปล validated
2. จัดกลุ่มตัวอักษรฐาน + สระบน/ล่าง + วรรณยุกต์เป็นหนึ่ง glyph พร้อมวาด
3. เลือก codepoint CJK ที่ไม่ชนกับข้อความใช้งาน
4. ผูก cluster ไทยแต่ละกลุ่มกับ carrier codepoint
5. วาด glyph ไทยที่จัดตำแหน่งแล้วลง cell ของ carrier ใน atlas
6. แก้ GFD ให้ metric/codepoint ชี้ไปยัง cell ใหม่
7. ก่อน pack ข้อความ แปลง cluster ไทยเป็น carrier string

ผลผลิตขั้นสุดท้าย:

- Carrier clusters ใช้งาน `676` กลุ่ม
- Candidate slots ที่สำรวจได้ `883` ช่อง
- ฟอนต์ต้นทางสำหรับ glyph ไทย: Leelawadee UI
- Mapping hash: `18B4A83F9EDE13C0089FAAB0058134E16903A48D98D089866F0D367CB768B59A`

### 7.3 การแก้ atlas แบบรักษาพื้นที่เดิม

เวอร์ชันที่เสถียรใช้วิธีแก้เฉพาะ BC3 blocks ที่ครอบคลุม carrier cells:

- เก็บ block เดิมที่ไม่เกี่ยวข้อง `28,774` blocks
- เขียน block ที่มี carrier glyph `36,762` blocks

วิธีนี้ลดโอกาสให้ glyph อังกฤษ ญี่ปุ่น ไอคอน หรือสีส่วนอื่นเปลี่ยนเพราะการ re-encode ทั้ง atlas

ไฟล์สำคัญ:

- `05_Scripts_and_Tools\analyze_thai_carrier_clusters.py`
- `05_Scripts_and_Tools\build_thai_carrier_package.py`
- `05_Scripts_and_Tools\build_dynamic_font_v2.py`
- `05_Scripts_and_Tools\render_thai_carrier_v2.ps1`
- `03_Font_and_UI\thai_carrier_v2_20260903\ddfont_jpn_00_ID_HQ.tex`
- `03_Font_and_UI\thai_carrier_v2_20260903\ddfont_jpn.gfd`

### 7.4 ต้องแก้ฟอนต์สอง archive

ไฟล์ฟอนต์/GFD ถูกบรรจุซ้ำและมีเส้นทางโหลดหลายจุด จึง patch ทั้ง:

- `nativePC\rom\bbsrpg_core.arc`
- `nativePC\rom\bbs_rpg.arc`

GFD ใหม่มี compressed payload `21,059` ไบต์ มากกว่า slot เดิม `20,409` ไบต์ จึงใช้ append-only payload แล้วอัปเดต pointer ใน entry แทนการขยับ resource อื่นทั้ง archive

---

## 8. ข้อความที่เป็นภาพ: Static UI Atlas

หัวข้อและคำสั่งจำนวนหนึ่งไม่ได้มาจาก GMD แต่ถูกวาดอยู่ใน texture atlas เช่น:

- Pause Menu, Save / Quit, History, Quests, Map, Equipment, Status, Options
- หัวข้อหน้าต่าง Quests/Equipment/Status
- Main Menu, Credits และคำในหน้าปรับแต่ง
- โลโก้ Dragon's Dogma, Dark Arisen และ copyright

ไฟล์ PNG ที่แก้ใน Photoshop อยู่ที่:

`03_Font_and_UI\static_texture_export_20260914\Photoshop_Edit_Set\01_EDIT_THESE_PNG\`

ไฟล์หลัก:

| PNG | เนื้อหา |
|---|---|
| `01_UI_ATLAS_MAIN_EN.png` | Main UI atlas 1024×1024 |
| `02_UI_ATLAS_CUSTOMIZATION_EN.png` | Customization atlas 512×256 |
| `03_UI_ATLAS_EXTRAS_CREDITS_EN.png` | Extras/Credits atlas 1024×512 |
| `10_LOGO_DRAGONS_DOGMA.png` | โลโก้หลัก |
| `11_LOGO_DARK_ARISEN_AND_COPYRIGHT.png` | โลโก้รองและ copyright |

### Resource names

```text
id\localize\<locale>\word_ID_<locale>
id\localize\<locale>\word_1_ID_<locale>
id\DDN\localize\<locale>\ddn_word_ID_<locale>
id\DDN\menu\title_1\mntitle_HQ_ID
id\DDN\menu\title_1\sbtitle_HQ_ID
```

### กฎ Photoshop

1. ห้ามเปลี่ยนขนาด canvas
2. ห้ามย้ายกรอบคำอื่นหรือเปลี่ยนพิกัดของ sprite
3. รักษา alpha และขอบโปร่งใส
4. ก่อน encode ให้ normalize RGB ของ pixel ที่ alpha = 0 เป็นสีดำ เพื่อลดสีรั่วตามขอบ
5. ส่งออก PNG RGBA ขนาดเดิม
6. ตรวจ decoded round-trip หลัง BC3 ทุกครั้ง

---

## 9. บทเรียนเรื่อง Locale และ Load Priority

การเขียนเฉพาะ `word_ID_eng` ไม่ครอบคลุม UI จริงทั้งหมด เพราะ GUI บางหน้ามี default reference ไปที่ `word_ID_jpn` และ runtime อาจอ่าน resource สำเนาจาก archive ต่างกัน

ชุด locale ที่ต้องครอบคลุม:

```text
jpn, eng, fre, spa, ger, ita, zht
```

Main atlas ขั้นสุดท้ายจึงถูกเขียนครบ `7 locale × 4 archive = 28 targets` ใน:

1. `title.arc`
2. `game_main.arc`
3. `GUIuGUITopMenu.arc`
4. `GUIuGUITitle.arc`

นี่คือคำตอบของอาการ “แพ็ก PNG ภาษาไทยแล้ว แต่ Pause Menu ยังเป็นอังกฤษ”: TEX ถูกต้อง แต่อยู่ใน archive/locale ที่หน้านั้นไม่ได้โหลด

Main PNG ขั้นสุดท้าย:

- SHA-256: `056C97F724FAEC782117301CBAD37C8D9D6848C69D1371DE984CD624AF0F1D79`
- TEX ขั้นสุดท้าย: `8E903FA70F559A451DA28EB86730E88BC7713E35F5275B880EA056F84E909867`

---

## 10. ปัญหาโลโก้กลายเป็นสีชมพู

อาการ: โลโก้ทอง/ครีมกลายเป็นชมพูหรือม่วงหลัง pack ทั้งที่ PNG ถูกต้อง

สาเหตุ:

- Main UI atlas เป็น TEX type `0x18` และใช้ RGB ตามปกติ
- โลโก้ `mntitle_HQ_ID` และ `sbtitle_HQ_ID` เป็น TEX type `0x2B` ซึ่งเกมตีความสีเป็น YCbCr
- การนำ RGB BC3 ไปใส่ใน header type `0x2B` ทำให้เกมอ่านช่อง R/G/B เป็น Cr/Y/Cb ผิดความหมาย

วิธีแก้ที่ผ่านการทดสอบ:

1. ตรวจ TEX type จาก header
2. ถ้าเป็น `0x18` ให้ encode RGBA → BC3 ตามปกติ
3. ถ้าเป็น `0x2B` ให้แปลงสี display RGB เป็น raw channel `(Cr, Y, Cb, A)` ก่อน BC3
4. หลัง encode ให้ decode raw กลับเป็น RGB และบันทึกภาพ preview
5. เทียบภาพ round-trip ต้องเป็นสีทอง/ครีม ไม่มี magenta cast

ตรรกะนี้อยู่ใน `05_Scripts_and_Tools\pack_static_ui_atlases.py`

---

## 11. Surgical ARC Patching

ห้าม rebuild ARC ขนาดใหญ่แบบเปลี่ยน layout ทั้งหมดถ้าไม่จำเป็น วิธีที่เสถียรคือ surgical patch:

1. อ่าน ARC header และ resource table
2. ค้น entry ด้วย resource name ที่แน่นอน
3. บีบอัด payload ใหม่ด้วยรูปแบบเดิม
4. ถ้า compressed payload ใหม่มีขนาดไม่เกิน slot เดิม ให้เขียนทับใน slot เดิมและเติมส่วนที่เหลืออย่างปลอดภัย
5. ถ้าใหญ่กว่า slot เดิม ให้ append payload แบบ aligned ที่ท้าย archive
6. อัปเดตเฉพาะ offset, compressed size และ uncompressed size ของ entry เป้าหมาย
7. ห้ามเปลี่ยนชื่อ ลำดับ และ metadata ของ resource อื่น
8. แตก resource เป้าหมายจาก build แล้วเทียบ hash กับ payload ที่ตั้งใจ
9. ตรวจ bytes/entries นอกเป้าหมายว่าไม่เปลี่ยน

สคริปต์หลัก:

- `05_Scripts_and_Tools\surgical_patch_mtf_arc.py`
- `05_Scripts_and_Tools\pack_static_ui_atlases.py`
- `05_Scripts_and_Tools\fix_mtf_arc_v7.py`

วิธีนี้แก้ปัญหา fatal file-open ที่เคยเกิดจาก full repack และรักษา archive ที่เกมไวต่อ layout

---

## 12. Build Pipeline ฉบับเต็ม

### Phase A — เตรียมต้นฉบับ

1. ปิดเกมและ mod manager ทั้งหมด
2. คัดลอกไฟล์เกมต้นฉบับเข้า `01_Original_Backup`
3. บันทึก SHA-256 ของ source ทุกไฟล์
4. ห้ามใช้ไฟล์เกมที่กำลังเปิดเป็น input/output เดียวกัน

### Phase B — Extract ข้อความ

1. รัน `dragons_dogma_dark_arisen_unpacker.py` กับ `message.pck`
2. ยืนยัน `9,684` GMD และ `50,142` rows
3. ตรวจ schema ห้าคอลัมน์
4. เก็บไฟล์ English master ที่ไม่แก้เป็น baseline

### Phase C — แปลและทำความสะอาด

1. ให้ระบบแปลแก้เฉพาะคอลัมน์ `translation`
2. รัน `sanitize_trun_output.py`
3. รัน `validate_tstudio_csv.py`
4. ตรวจ tag, placeholder, key, row order และ source
5. เก็บรายการ 111 แถวที่ยังไม่แปลเป็น English fallback

### Phase D — สร้าง Carrier Mapping และฟอนต์

1. วิเคราะห์ cluster จาก CSV validated
2. สร้าง mapping ไทย → CJK carrier
3. render glyph ไทยลง carrier cells ด้วย Leelawadee UI
4. แก้ GFD metrics ให้สัมพันธ์กับ atlas
5. รักษา BC3 blocks ที่ไม่ใช่ carrier
6. patch font TEX/GFD ลง `bbsrpg_core.arc` และ `bbs_rpg.arc`
7. ตรวจ glyph preview, mapping count และ decompression

### Phase E — Pack ข้อความ

1. แปลง translation ไทยเป็น carrier string ด้วย mapping เดียวกับฟอนต์
2. pack เฉพาะ GMD ที่มี translation
3. เก็บ GMD ที่ไม่เปลี่ยนเป็น byte เดิม
4. สร้าง `message.pck`
5. ตรวจกลับว่ามี `50,142` keys และไม่มี marker/tag เสีย

### Phase F — ทำ Static UI

1. แก้ PNG ใน Photoshop โดยรักษาขนาดและ sprite coordinates
2. encode TEX type `0x18` เป็น RGB BC3
3. encode โลโก้ TEX type `0x2B` เป็น raw `(Cr,Y,Cb,A)` BC3
4. ตรวจ alpha และ decoded round-trip
5. patch resource ให้ครบ archive ที่ runtime โหลด
6. สำหรับ Main atlas เขียนครบทั้งเจ็ด locale ในสี่ archive

### Phase G — Deploy ทดสอบ

1. ตรวจ process เกมปิด
2. สำรอง target เป็น checkpoint ใหม่
3. เทียบ hash backup กับ target ก่อนเขียน
4. คัดลอก build ลงเกม
5. เทียบ hash target กับ build หลังเขียน
6. ทดสอบ Title, Main Menu, Pause, Quests, Equipment, Status, tutorial/loading และบทสนทนา

### Phase H — Release

1. ใช้ไฟล์จากเกมที่ผ่าน playtest แล้วเป็น release source
2. จัดโครงสร้าง `nativePC\...` ให้ตรงกับเกม
3. เพิ่มคู่มือติดตั้ง, version และ checksums
4. สร้าง ZIP โดยให้ `nativePC` อยู่ที่ root ของ ZIP
5. แตก ZIP ในโฟลเดอร์ทดสอบและเทียบ SHA-256 ทุกไฟล์

---

## 13. Quality Gates

### Text Gate

- [ ] CSV มี 50,142 แถว
- [ ] key ไม่ซ้ำและไม่หาย
- [ ] source/context/file_path ตรง master
- [ ] tag และ placeholder ครบ
- [ ] ไม่มี `PCK_message_` หรือ `[TAG_n]`
- [ ] 111 untranslated rows fallback อังกฤษ

### Font Gate

- [ ] mapping มี 676 carrier clusters
- [ ] atlas และ GFD ใช้ mapping ชุดเดียวกัน
- [ ] patch ทั้งสอง font archives
- [ ] BC3 blocks นอก carrier ไม่เปลี่ยน
- [ ] preview แสดงสระ/วรรณยุกต์อ่านได้

### UI Gate

- [ ] PNG dimensions ตรงต้นฉบับ
- [ ] alpha range ถูกต้อง
- [ ] TEX type 0x18/0x2B ถูกเส้นทางสี
- [ ] Main atlas ครบ 28 targets
- [ ] logo round-trip ไม่มีสีชมพู

### Archive Gate

- [ ] magic/version ถูกต้อง
- [ ] จำนวน entries เท่าเดิม
- [ ] resource เป้าหมายแตกกลับได้และ hash ตรง
- [ ] resource นอกเป้าหมายไม่เปลี่ยน
- [ ] เปิดเกมไม่มี `Failed open file`

### Playtest Gate

- [ ] Title/Logo/Copyright
- [ ] Main Menu และเมนูย่อย
- [ ] Pause Menu
- [ ] Quests ทั้ง current/completed
- [ ] Equipment/Status/Inventory
- [ ] บทสนทนาและ tutorial
- [ ] loading tips
- [ ] save/load และเข้า gameplay ได้

---

## 14. Troubleshooting

### เกมยังแสดงอังกฤษเฉพาะชื่อเมนู

สาเหตุที่พบบ่อย: ชื่อนั้นเป็น static texture ไม่ใช่ GMD หรือ patch เฉพาะ `eng` แต่ GUI เรียก `jpn`/archive สำเนาอื่น

การแก้: หา resource name จาก GUI reference แล้ว patch ทุก runtime archive/locale ที่เกี่ยวข้อง ตรวจ hash จากไฟล์เกมจริงหลังติดตั้ง

### ภาษาไทยว่างหรือเป็นตัวประหลาด

สาเหตุ: ข้อความ carrier กับ font mapping ไม่ใช่รุ่นเดียวกัน, patch font ไม่ครบสอง archive หรือเอา Unicode ไทยตรงไปให้ renderer ที่ไม่ shape ไทย

การแก้: rebuild message และ font จาก carrier mapping ชุดเดียวกัน แล้วตรวจ mapping hash

### สระและวรรณยุกต์ซ้อนผิด

สาเหตุ: render อักขระไทยแยกตัวโดยหวังพึ่ง runtime shaping

การแก้: pre-compose เป็น cluster glyph และกำหนด metric/cell ใน carrier atlas

### ตัวอักษรขึ้นเป็นกล่องดำ/แถบดำ

สาเหตุ: alpha/RGB ใต้พื้นที่โปร่งใสผิด, sprite bounds เปลี่ยน หรือ texture ถูกวางผิดตำแหน่งใน atlas

การแก้: รักษาขนาด/พิกัด, normalize fully transparent RGB เป็นดำ และตรวจ alpha round-trip

### โลโก้เป็นชมพู

สาเหตุ: encode RGB ลง TEX type `0x2B` ที่เกมตีความเป็น YCbCr

การแก้: แปลงเป็น `(Cr,Y,Cb,A)` ก่อน BC3 และตรวจภาพ decode

### Fatal error: Failed open file `.srq`, `.mod` หรือไฟล์อื่น

สาเหตุ: full ARC repack เปลี่ยน layout/order/offset ของ resource ที่ไม่ได้ตั้งใจ

การแก้: คืน archive จาก backup แล้วใช้ surgical patch เฉพาะ entry เป้าหมาย

### แพ็กแล้วแต่เกมไม่เปลี่ยน

ตรวจตามลำดับ:

1. เกมปิดตอนคัดลอกหรือไม่
2. เขียนลง `...\steamapps\common\DDDA` จริงหรือไม่
3. ไฟล์ปลายทางมี hash ตรง build หรือไม่
4. หน้านั้นโหลด archive ใดและ locale ใด
5. mod อื่นเขียนทับเจ็ด archive หลังม็อดไทยหรือไม่

---

## 15. ไฟล์ Release v1.0.0 และ SHA-256

| ไฟล์ | ไบต์ | SHA-256 |
|---|---:|---|
| `nativePC\rom\message\message.pck` | 21,751,065 | `2249AADAC2318C36557C2B89355A1CB54EE7641036D367FC4833B742C043D494` |
| `nativePC\rom\bbsrpg_core.arc` | 4,611,347 | `61BA3DDBC350EC60ECADD5E2BEC68A6E9B8C7CAD7F79955319C6D8562DF88A4B` |
| `nativePC\rom\bbs_rpg.arc` | 11,198,883 | `4DAEE2FAC320E3D059A4AC1395A419464271319E396C3C090AB2D9D6FE2CCC6B` |
| `nativePC\rom\title.arc` | 14,208,955 | `109AD3920C24AD60DFAA5119D5155A2CC7711AE1D97AC3DEC9C5EF459EC0FAAA` |
| `nativePC\rom\game_main.arc` | 23,775,211 | `944A917F4B3AEE87BCDB553D33EE9129ADA7DC7C2420C964F82135D6CC823B53` |
| `nativePC\rom\gui\GUIuGUITopMenu.arc` | 5,581,684 | `E054665E46025D40665AF00A1C828E0FC3C69BE07382F830570AF268AD6C49BC` |
| `nativePC\rom\gui\GUIuGUITitle.arc` | 2,398,575 | `B10854329E700A90737006BD25630DC6E5E573CB413ED699B5F0049AB59F3D83` |

Release ใช้วิธีให้ผู้เล่นแตก ZIP แล้วคัดลอกโฟลเดอร์ `nativePC` ไปวางทับในโฟลเดอร์ `DDDA`

---

## 16. วิธีอัปเดตม็อดในอนาคต

### ถ้าแก้เฉพาะคำแปล

1. แก้ CSV validated
2. รัน sanitize + validate
3. ตรวจ cluster ใหม่ว่ามีเกิน 676 mapping เดิมหรือไม่
4. ถ้าไม่มี cluster ใหม่ ให้ rebuild เฉพาะ `message.pck`
5. ถ้ามี cluster ใหม่ ต้อง rebuild mapping, font atlas/GFD และ `message.pck` พร้อมกัน

### ถ้าแก้ Main UI PNG

1. ตรวจ SHA-256 input PNG
2. encode TEX + decode round-trip
3. patch ครบ 7 locales ใน 4 archives
4. ตรวจ resource ครบ 28 จุดจาก archive ที่สร้างและไฟล์เกมหลัง deploy

### ถ้าแก้โลโก้

1. ใช้เส้นทาง TEX `0x2B` YCbCr เท่านั้น
2. patch `mntitle_HQ_ID`/`sbtitle_HQ_ID` ใน `title.arc`
3. ตรวจสีจาก decoded round-trip ก่อน deploy

### การออกเวอร์ชัน

- เพิ่ม patch version เมื่อแก้คำ/ภาพเล็กน้อย เช่น `v1.0.1`
- เพิ่ม minor version เมื่อเพิ่มเนื้อหา/แก้ระบบฟอนต์ เช่น `v1.1.0`
- เพิ่ม major version เมื่อเปลี่ยน compatibility หรือ build pipeline เช่น `v2.0.0`
- สร้าง release directory ใหม่ ห้ามเขียนทับ release เก่า เพื่อย้อนกลับและตรวจสอบได้

---

## 17. บทเรียนที่นำไปใช้กับเกม MT Framework อื่นได้

1. แยก Dynamic Text, Font Rendering และ Static UI ตั้งแต่เริ่ม
2. พิสูจน์ no-op round-trip ก่อนแก้เนื้อหา
3. อย่าเชื่อชื่อ locale เพียงอย่างเดียว ให้ตาม GUI reference และ runtime archive จริง
4. Renderer ที่ไม่รองรับ shaping แก้ได้ด้วย precomposed carrier glyph
5. ตาราง mapping, atlas และข้อความต้องเป็น atomic version เดียวกัน
6. อย่า re-encode texture ทั้งแผ่นหากแก้ได้เฉพาะ BC3 blocks
7. TEX ที่หน้าตาเหมือนกันอาจใช้ color transform คนละแบบ ต้องอ่าน header
8. Full repack เสี่ยงกับ ARC ที่ไวต่อ layout; surgical patch ปลอดภัยกว่า
9. ตรวจ hash ทั้งก่อนและหลัง deploy และตรวจ resource จาก “ไฟล์เกมจริง” ไม่ใช่เฉพาะ build
10. Release แบบ copy-overwrite ต้องมีโครงสร้างพาธตรงเกมและบอกวิธีกู้คืนที่ไม่ทำให้ไฟล์เกมหาย

---

## 18. เครดิต

- ผู้สร้างม็อดและผู้แปล: **หน๊ด หนวด translator**
- โครงการ: **NodNuatTranslator**

เอกสารนี้บันทึกจากกระบวนการผลิตและผลทดสอบจริงของ Dragon's Dogma: Dark Arisen Thai Mod v1.0.0 เพื่อให้สามารถสร้างซ้ำ ตรวจสอบ และดูแลเวอร์ชันต่อไปได้
