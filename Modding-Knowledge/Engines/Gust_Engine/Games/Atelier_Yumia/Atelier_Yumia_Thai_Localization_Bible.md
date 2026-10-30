# คัมภีร์สร้าง Mod ภาษาไทย — Atelier Yumia

เอกสารนี้บันทึกกระบวนการที่ใช้จริงจนเกม **Atelier Yumia: The Alchemist of Memories and the Envisioned Land** แสดงภาษาไทยแบบ native ได้สำเร็จ ครอบคลุมทั้งข้อความ JSON/EBM, การใช้ช่องภาษาญี่ปุ่น, PUA carrier, ฟอนต์ G1N SDF, การตรวจสอบ และการออก release

## 1. ข้อมูลโครงการ

- เกม: Atelier Yumia: The Alchemist of Memories and the Envisioned Land
- เวอร์ชันที่ทดสอบในเกม: Ver. 1.70
- File/Product Version ของ `Atelier_Yumia.exe`: 1.0.7.0
- แพลตฟอร์ม: Steam / Windows
- Runtime/Engine: proprietary Alchemy / KidsMotor ของ Gust / Koei Tecmo
- Archive ข้อความ: Gust A22/64-bit `PACK00.pak` (A26 master key)
- ข้อความระบบ: JSON
- บทสนทนา/เหตุการณ์: EBM
- Font container: `PDRK0000` ครอบ `IDRK0000` ใน `.fdata`
- Font payload: `_N1G0000` / G1N, 2 glyph tables, 64×64, 8bpp SDF
- แนวทางสำเร็จ: Japanese locale replacement + precomposed Thai PUA + CJK carrier + native G1N SDF
- ผู้สร้าง Mod: หน๊ด หนวด translator
- ระดับความซับซ้อน: ★★★★★

## 2. ผลลัพธ์สุดท้าย

Mod v1.0 แก้ไฟล์เกมเพียง 2 ไฟล์:

```text
Atelier Yumia\Data\PACK00.pak
Atelier Yumia\Motor\jaJP\0xe9d4dd97.fdata
```

จำนวนข้อความ:

| แหล่งข้อมูล | จำนวน |
|---|---:|
| JSON (`message.json`) | 20,322 |
| EBM (857 source files) | 10,402 |
| รวม | 30,724 |

CSV master มี schema มาตรฐาน THub/TStudio:

```text
key | source | translation | context | file_path
```

ไฟล์ master รุ่น release:

```text
02_Translation_Workspace\Atelier_Yumia_FULL_en_to_th_TStudio_reviewed.csv
```

## 3. กฎและข้อจำกัดที่ต้องรักษา

1. ห้ามแก้ THub Core: `trun_app.py`, `tstudio_app.py`, `tstudio_core.py`, `file_converter.py`
2. Bridge มีหน้าที่แปลง format เกม ↔ TStudio CSV เท่านั้น งานแปลจำนวนมากใช้ TRun/TStudio
3. ห้ามแก้คอลัมน์ `source`; `key` ต้องไม่ซ้ำ
4. ต้องรักษา protected tokens เช่น `%s`, `%d`, `{0}`, `<CLEG>`, `<CLNR>`, `<CR>`, `<KEY_...>`
5. `01_Original_Backup` เป็น read-only ในกระบวนการ ห้ามเขียนทับ backup เดิม
6. ก่อน deploy ต้องปิดเกม, ตรวจ backup, บันทึก checkpoint และตรวจ hash
7. ห้ามใส่ Thai combining marks ตรง ๆ ในข้อความสุดท้าย เพราะ renderer ไม่จัด shaping ภาษาไทย
8. ต้อง precompose ไทยเป็น PUA และแปลง PUA เป็น CJK carrier ก่อน pack
9. ต้องใช้ช่อง `jaJP` และตั้ง Steam Language เป็น Japanese
10. ห้ามใช้ runtime overlay/hook ใน release native

## 4. การค้นหา Engine และ Text Resource

### 4.1 สิ่งที่พบจาก static scan

- `Motor\root.rdb` และ `Motor\root.rdx` เป็น index ของ resource
- `Motor\<locale>\*.fdata` เป็น PDRK/IDRK container
- `.fdata` ภาษาอังกฤษที่ตรวจช่วงแรกมี texture/font ไม่ใช่ text table
- `Data\PACK00.pak` ไม่ใช่ ZIP/PAK มาตรฐาน แต่ `gust_pak` v1.58 อ่านได้เป็น A22/64-bit

### 4.2 Dynamic discovery

การสแกน process แบบ read-only พบ Main Menu table ใน memory:

```text
STR_MENU_DEFINE_336 = CONTINUE
STR_MENU_DEFINE_337 = LOAD GAME
STR_MENU_DEFINE_338 = NEW GAME
STR_MENU_DEFINE_339 = OPTIONS
STR_MENU_DEFINE_340 = EXTRAS
STR_MENU_DEFINE_341 = QUIT GAME
STR_MENU_DEFINE_342 = PRESS ANY BUTTON
```

จาก key เหล่านี้จึงย้อนค้นใน archive และพบ resource จริง:

```text
master/eng/fixed_data/message/message.json
```

### 4.3 เครื่องมือ archive

ใช้ `gust_pak.exe` จาก gust_tools v1.58:

```powershell
gust_pak.exe PACK00.pak
```

คำสั่งนี้แตก archive และสร้าง `PACK00.json` ซึ่งจำเป็นต่อการ repack

การ repack ต้องส่ง manifest JSON:

```powershell
gust_pak.exe PACK00.json
```

ข้อควรระวัง: อย่าทำ manifest หาย เพราะ metadata, key และ extra fields ต้องใช้สร้าง PAK กลับ

## 5. Text Bridge

### 5.1 JSON Bridge

สคริปต์:

```text
05_Scripts_and_Tools\AtelierYumia_message_bridge.py
```

ฟังก์ชันหลัก:

- `extract`: `message.json` → TStudio CSV
- `apply`: translated CSV → `message.json`
- ตรวจ `NAME_LABEL` เป็น key
- ตรวจ source reference
- ตรวจ protected tags แบบ multiset

ตัวอย่าง apply:

```powershell
python AtelierYumia_message_bridge.py apply `
  --input master\eng\fixed_data\message\message.json `
  --source-reference master\eng\fixed_data\message\message.json `
  --csv Atelier_Yumia_FULL_carrier.csv `
  --output master\jpn\fixed_data\message\message.json
```

### 5.2 EBM Bridge

สคริปต์:

```text
05_Scripts_and_Tools\AtelierYumia_ebm_bridge.py
```

EBM source corpus มี 857 ไฟล์ และข้อความ non-empty 10,402 รายการ รูป key:

```text
EBM::<relative-path>::<record-index-5-digits>
```

ตัวอย่าง:

```text
EBM::event_message_cm01_010.ebm::00000
```

คำสั่ง pack:

```powershell
python AtelierYumia_ebm_bridge.py pack `
  --ebm-root AtelierYumia_bridge_resources\master\eng\eventmessagedata `
  --csv Atelier_Yumia_FULL_carrier.csv `
  --output-root build\master\jpn\eventmessagedata
```

ข้อค้นพบสำคัญ:

- English source มี 857 EBM แต่ Japanese archive มี 875 EBM
- มีไฟล์เฉพาะญี่ปุ่นเพิ่ม 18 ไฟล์ซึ่งไม่มี row แปลอังกฤษ
- ตอนสร้าง stage ต้องนำ 18 ไฟล์ที่ขาดจาก Japanese stage ที่ตรวจแล้วมาเติม โดยห้ามทับ 857 ไฟล์ที่ rebuild จาก CSV

## 6. Full Extraction และ Translation QA

รวม JSON และ EBM เป็น CSV เดียว 30,724 แถว จากนั้นใช้ TRun/TStudio แปล English → Thai

Validator:

```powershell
python AtelierYumia_translation_validator.py `
  Atelier_Yumia_FULL_en_to_th_TStudio_reviewed.csv `
  --require-complete
```

เกณฑ์ก่อน pack:

- rows = 30,724
- unique keys = 30,724
- translated = 30,724
- protected-token mismatch = 0
- translation ห้ามว่าง
- source ห้ามเปลี่ยน

Language QA อาจรายงาน `no_thai`, `unchanged_source`, `cjk_leftover` ได้ บางรายการเป็นชื่อเฉพาะ ตัวเลข ปุ่ม หรือข้อความที่ตั้งใจคงเดิม จึงต้อง review ไม่ใช่ลบอัตโนมัติ

## 7. เหตุผลที่ Thai Unicode ตรง ๆ ใช้ไม่ได้

POC แรกพิสูจน์ว่าเกมโหลด UTF-8 ภาษาไทยจาก PAK ได้ แต่ฟอนต์ไม่มี glyph จึงแสดง tofu เมื่อเพิ่ม glyph ไทยตรง ๆ ยังพบปัญหา:

- renderer ไม่มี Thai shaping
- สระและวรรณยุกต์แยกตำแหน่ง
- combining marks ใช้ advance/metric แบบ glyph แยก
- native table ไม่มี Thai codepoints

แนวทางสำเร็จจึงใช้ **precomposed PUA**: รวมหนึ่งเซลล์พยัญชนะ+สระ+วรรณยุกต์เป็น glyph เดียว แล้วแทน glyph นั้นด้วย codepoint CJK ที่มี record อยู่ใน Japanese G1N

## 8. PUA Carrier Pipeline

### 8.1 Input

- PUA mapping: `E:\Mod_Workspace\Tool\1_ThaiFont\Mapping.json`
- Font: `Kanit-Regular_PUA.ttf`
- Carrier candidates: codepoint CJK/Japanese ที่มีใน G1N และไม่ปรากฏ literal ใน corpus

### 8.2 Bridge

สคริปต์:

```text
AtelierYumia_pua_carrier_bridge.py
```

ขั้นตอน:

1. Normalize translation เป็น NFC
2. แปลง `ํา` เป็น `ำ` ตาม normalization rule
3. longest-match Thai cluster ตาม `Mapping.json`
4. แทน cluster ด้วย PUA glyph
5. ตรวจว่าไม่มี Thai combining mark เหลือ
6. เก็บ glyph ไทย/PUA ที่ถูกใช้จริง
7. จัด one-to-one mapping ไปยัง CJK carrier
8. เขียน carrier CSV และ `full_glyph_map.tsv`

Release v1.0 ใช้ carrier ทั้งหมด 660 glyph

คำสั่งตัวอย่าง:

```powershell
python AtelierYumia_pua_carrier_bridge.py `
  --input Atelier_Yumia_FULL_en_to_th_TStudio_reviewed.csv `
  --pua-mapping Mapping.json `
  --output Atelier_Yumia_FULL_carrier.csv `
  --glyph-map full_glyph_map.tsv `
  --carrier-list carrier_candidates.txt
```

## 9. Native Font Discovery

Japanese font อยู่ที่:

```text
Motor\jaJP\0xe9d4dd97.fdata
```

ภายในเป็น:

```text
PDRK0000
└─ IDRK0000
   └─ root_font_jaJP.g1n (_N1G0000)
```

คุณสมบัติ G1N ที่ยืนยันแล้ว:

- 2 glyph tables
- carrier glyph ขนาด logical 64×64
- pixel payload 4,096 bytes/glyph
- 8bpp SDF
- `Unk=-32`
- original Japanese glyph ต้องคง byte-identical ยกเว้น carrier ที่เลือก

## 10. การสร้าง Kanit Native G1N

Builder:

```text
AtelierYumia_G1NPuaCarrierBuild.cs/.exe
```

Release metrics ที่ผ่าน playtest:

```text
Width     = 64 (คง logical width ของ carrier)
Height    = 64
XAdvance  = 44
XOffset   = 0
Baseline  = 64
Unk       = -32
```

การวาง bitmap:

```csharp
startX = (64 - sdf.Width) / 2;
startY = 64 - sdf.Height;
```

เหตุผล:

- center แนวนอนป้องกัน glyph ซ้อน/เบี้ยว
- bottom align และ baseline เดียวป้องกันอักษรกระโดดสูงต่ำ
- `XAdvance=28` เคยทำให้ glyph ซ้อนกัน
- advance CJK เดิมทำให้ไทยห่างเกินไป
- `44` เป็นค่าที่ผ่าน playtest

## 11. Continuous SDF — จุดที่ทำให้ฟอนต์คม

รุ่นแรก quantize SDF:

```csharp
(value >> 5) * 36
```

ผลคือ glyph ไทยมีเพียงประมาณ 5 ระดับสี (`0,36,72,108,144`) เมื่อ UI ย่อลง เส้นและสระเล็กจึงฟุ้ง/บาง

การวิเคราะห์ native Japanese พบ:

- max value โดยทั่วไปประมาณ 148–164
- distinct values ประมาณ 126–163
- native ไม่ได้เร่งถึง 255 แต่เก็บ distance gradient ต่อเนื่อง

วิธีแก้ที่ถูกต้อง:

```csharp
canvas[...] = value;
```

ผล release v1.0:

- sample Thai glyph มี 78–87 ระดับ เฉลี่ย 84.8
- max 144–146 ใกล้ native
- รายละเอียดขอบ สระ และวรรณยุกต์ชัดขึ้นมาก
- ไม่ทำ stroke บวมจากการ remap เป็น 255

## 12. การปรับวรรณยุกต์ Kanit

ใช้ `AtelierYumia_raise_thai_tones.py` แก้ outline ในสำเนา TTF ภายใน build output ไม่แก้ font master

ตำแหน่ง release:

- `่` U+0E48: +160 font units
- `้` U+0E49: +240 font units (เริ่ม +160 แล้วเพิ่มอีก +80)
- `๊` U+0E4A: +160 font units
- `๋` U+0E4B: +160 font units

สคริปต์ตรวจทุก outline coordinate หลัง save/reload ว่า delta ตรงค่าที่กำหนด

## 13. Repack Font fdata

ใช้:

```text
AtelierYumia_repack_native_fdata.py
```

คำสั่ง:

```powershell
python AtelierYumia_repack_native_fdata.py `
  --original 01_Original_Backup\Motor\jaJP\0xe9d4dd97.fdata `
  --replacement root_font_jaJP_thai.g1n `
  --output build\0xe9d4dd97.fdata `
  --fixed-slots
```

Round-trip check:

```powershell
python AtelierYumia_repack_native_fdata.py `
  --original build\0xe9d4dd97.fdata `
  --replacement root_font_jaJP_thai.g1n `
  --output build\roundtrip.fdata `
  --fixed-slots
```

ต้องได้:

```text
changed=[]
SHA256(candidate) == SHA256(roundtrip)
```

## 14. Full Pack Workflow

ลำดับมาตรฐานสำหรับแก้คำแปลรุ่นถัดไป:

1. แก้เฉพาะ `translation` ใน reviewed CSV
2. รัน translation validator
3. รัน PUA carrier bridge ด้วย carrier list เดิม
4. ยืนยัน glyph map ยังมี 660 entries หรือ rebuild font หาก glyph set เปลี่ยน
5. Apply JSON ไปยัง `master/jpn/fixed_data/message/message.json`
6. Pack 857 EBM ไป `master/jpn/eventmessagedata`
7. เติม Japanese-only EBM 18 ไฟล์ที่ขาด
8. ใช้ manifest `PACK00.json` จาก original extraction
9. รัน `gust_pak.exe PACK00.json`
10. แตก PAK candidate ไป verify directory
11. เทียบ JSON 20,322 ค่าและ EBM 10,402 ค่า กับ carrier CSV
12. ต้อง mismatch = 0 ทั้งสองชุด
13. ตรวจเกมปิด, backup/hash และ log checkpoint
14. Deploy เฉพาะ `Data\PACK00.pak`
15. Font ไม่ต้อง rebuild หาก glyph set/font parameters ไม่เปลี่ยน

## 15. Release v1.0 Hashes

```text
Data\PACK00.pak
SHA256 2DE548DCD8AFE0E475DB37CF6BACA13F7F0FD7EEC36397F563F388856ACF2400

Motor\jaJP\0xe9d4dd97.fdata
SHA256 2FE7EC44238A72F492579085CBA01190458A059FD15FE827B26AE8FEC4C7BB49
```

Original backups:

```text
PACK00.pak
BF826861D2B98D9B3A9999D9E6C6BB037157E91B3B1B770B083382010F338E58

jaJP\0xe9d4dd97.fdata
46CB0C2B0D6B2A84004CE1ECC4A92AD559E312912B7F7465CC189833D11764FA
```

## 16. แนวทางที่ทดลองแล้วแต่ไม่ใช้ใน Release

### 16.1 Windows overlay

- DirectX fullscreen/topmost วาดทับ overlay
- ไม่ครอบคลุม UI ทุกหน้า
- ไม่ใช่ native localization

### 16.2 Runtime hook

- แสดงไทยบางส่วนได้ แต่ผิดเป้าหมาย native mod
- เพิ่ม dependency และความเสี่ยง crash

### 16.3 เพิ่ม Thai Unicode glyph ตรง ๆ

- ไม่มี shaping
- combining marks และ metrics ผิด
- ไม่แก้ปัญหาตาราง codepoint เดิม

### 16.4 Raw bitmap / tile / MSDF ที่ไม่ตรง codec

- แสดงเป็น block/noise
- G1N variant นี้ต้องใช้ native 64×64 8bpp SDF semantics

### 16.5 Quantized SDF 5–8 ระดับ

- บีบอัดง่าย แต่ตัวหนังสือเล็กไม่คม
- release ต้องใช้ continuous gradient

### 16.6 English locale

- POC ภาษาอังกฤษเปลี่ยน text ได้ แต่ font/load path ไม่เหมาะกับ carrier strategy
- Japanese locale มี CJK glyph records จำนวนมากและเป็นช่องที่ใช้จริงใน release

## 17. การติดตั้ง Release สำหรับผู้เล่น

1. ตั้ง Steam Language เป็น Japanese (日本語)
2. ปิดเกม
3. คัดลอก `Data` และ `Motor` จาก release ไปทับโฟลเดอร์ `Atelier Yumia`
4. ยอมรับ Replace/Merge
5. เปิดเกม

การถอนใช้ Steam `Verify integrity of game files` เพื่อคืนทั้ง PAK และ font fdata

## 18. Checklist ก่อนออกเวอร์ชันใหม่

- [ ] เกม version ตรงกับ build ที่รองรับ
- [ ] CSV 30,724 rows / unique 30,724 / translated 30,724
- [ ] Protected tokens mismatch = 0
- [ ] Thai combining marks หลัง carrier bridge = 0
- [ ] Glyph map ครอบทุก glyph
- [ ] G1N spacing validator ผ่านทุก table
- [ ] Font fdata round-trip `changed=[]`
- [ ] PAK extract-back JSON mismatch = 0/20,322
- [ ] PAK extract-back EBM mismatch = 0/10,402
- [ ] Main Menu, tutorial, dialog, options และหลาย resolution ผ่าน playtest
- [ ] Backup original ไม่ถูกเขียนทับ
- [ ] Release มี README, CHANGELOG, SHA256SUMS

## 19. สรุปเทคนิคสำคัญที่สุด

Atelier Yumia รองรับข้อความ Unicode แต่ระบบฟอนต์ไม่มี Thai shaping และใช้ native G1N SDF ที่อิง glyph table เดิม วิธีที่เสถียรคือ:

```text
Thai translation
→ precompose cluster เป็น PUA
→ map PUA ไป CJK carrier ใน Japanese locale
→ วาด Kanit PUA ลง pixel payload ของ carrier เดิม
→ metrics คงที่ 64/44/0/64
→ continuous native-range SDF
→ repack jaJP fdata + PACK00
```

หัวใจของความสำเร็จไม่ใช่เพียง “ใส่ glyph ไทย” แต่คือการรักษา contract ของ renderer ทั้ง codepoint, carrier record, shaping, metrics, SDF range, archive metadata และ locale load path ให้ตรงกันทุกชั้น

