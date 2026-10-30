# The Blood of Dawnwalker — Thai Mod Production Bible

เอกสารนี้อธิบายกระบวนการสร้างม็อดภาษาไทยสำหรับ The Blood of Dawnwalker บน Windows Steam ตั้งแต่การแยกข้อความ การแปล การตรวจความถูกต้อง การสร้าง Patch PAK จนถึงการทำตัวเลือกภาษาไทยและโหมดไทย-อังกฤษ

## ขอบเขตและผลลัพธ์

- เกม: The Blood of Dawnwalker
- Engine: Unreal Engine 5
- แพลตฟอร์มที่ทดสอบ: Windows / Steam
- Game version ที่ใช้อ้างอิง: 1.0.2
- ข้อความทั้งหมด: 53,274 รายการ
  - `Dialogues_All`: 40,163 รายการ สำหรับบทสนทนาและซับไตเติลในเกม
  - `OnScreens_All`: 13,111 รายการ สำหรับ UI, เมนู, เควสต์, สกิล, Tutorial และข้อความระบบ
- ม็อดจัดส่งเป็น legacy Patch PAK แบบ V11, Oodle compression, path hash seed `0x3EE55F2D`

## หลักการสำคัญ

1. ใช้ THub/TStudio/TRun เป็นระบบหลักสำหรับงานแปลจำนวนมาก ห้ามแก้ Core ของระบบเหล่านั้น
2. Bridge script มีหน้าที่แปลง CSV ↔ LOCRES และประกอบ PAK เท่านั้น
3. CSV มาตรฐานต้องมีคอลัมน์ `key, source, translation, context, file_path` และ `key` ห้ามซ้ำ
4. ห้ามเปลี่ยนคอลัมน์ `source` ใน master CSV
5. ต้องรักษา placeholder และ markup ของเกมให้ครบ เช่น `{0}`, `%s`, `<BoldCD>`, `</>`, `<img .../>`, `\\n`, `\\r`
6. ก่อน deploy ทุกครั้ง สำรอง PAK เป้าหมายไว้ใน `01_Original_Backup` และบันทึก checkpoint ใน `session_log.md`

## โครงสร้างไฟล์สำคัญ

```text
The_Blood_of_Dawnwalker/
├─ 01_Original_Backup/                 # ห้ามเขียนทับ backup เดิม
├─ 02_Translation_Workspace/
│  └─ 00_ACTIVE/02_TRANSLATED_READY/
│     └─ Dawnwalker_Thai_FINAL_SAFE_v4_PACK_READY.csv
├─ 04_Packed_Mod/                      # stage และ PAK ที่สร้างสำเร็จ
├─ 05_Scripts_and_Tools/
│  ├─ Dawnwalker_locres_validator.py
│  ├─ Dawnwalker_full_master_packer.py
│  ├─ Dawnwalker_thai_english_de_packer.py
│  └─ session_log.md
└─ 06_Releases/                        # แพ็กสำหรับแจก
```

ไฟล์เกมเป้าหมาย:

```text
The Blood of Dawnwalker/
└─ Dawnwalker/
   ├─ Content/Paks/Dawnwalker-Windows_P.pak
   └─ Content/Movies/intro_cgi_es.srt และ intro_cgi_de.srt
```

## เทคโนโลยีและเครื่องมือ

| งาน | เครื่องมือ |
|---|---|
| แปลและตรวจงาน | TStudio / TRun |
| ตรวจ CSV และ tag | `Dawnwalker_locres_validator.py` |
| Import/Export LOCRES | `UnrealLocres.exe` |
| สร้าง/อ่าน PAK | `repak.exe` |
| ฟอนต์ไทย | Pridi PUA ที่ถูกแปลง/วางเป็น `.ufont` |

เกมรับ Patch PAK แบบไม่เข้ารหัสใน workflow นี้ จึงไม่ต้องใช้ AES key ในการ pack หรืออ่าน PAK ที่สร้างเอง

## การแยกและรวมข้อความ

### 1. สร้าง master CSV

ใช้ CSV mapping ของ `OnScreens_All` และ `Dialogues_All` รวมเป็น master เพียงไฟล์เดียว เพื่อให้ผู้แปลไม่ต้องจัดการหลายไฟล์ ขณะ pack ให้ใช้ mapping ทั้งสองเพื่อแยกข้อความกลับลง LOCRES ที่ถูกต้อง

### 2. ตรวจความถูกต้องก่อน pack

ใช้คำสั่ง:

```powershell
python Dawnwalker_locres_validator.py Dawnwalker_Thai_FINAL_SAFE_v4_PACK_READY.csv
```

เกณฑ์ผ่าน:

- ไม่มี translation ว่าง
- ไม่มี key ซ้ำ
- จำนวน/ชนิด placeholder และ rich-text tag ใน `translation` ตรงกับ `source`
- จำนวน line break ที่เกมต้องการไม่เปลี่ยน

หาก validator พบ `<BoldCD>` หรือ `{n}` หาย ห้าม pack ทันที เพราะอาจทำให้ข้อความขาด, styling ผิด หรือ runtime formatting error

### 3. Import LOCRES และสร้าง PAK

`Dawnwalker_full_master_packer.py` ทำงานดังนี้:

1. อ่าน master CSV ที่ผ่าน validator
2. ใช้ mapping เพื่อแบ่งเป็น OnScreens และ Dialogues
3. Import แต่ละชุดด้วย UnrealLocres
4. วางไฟล์ที่ได้ลง stage culture ที่ต้องการ
5. คัดลอก font, language settings และ logo ที่ผ่านการทดสอบจาก stage ฐาน
6. Pack ด้วย `repak.exe` ด้วย V11/Oodle/seed เดิม
7. ใช้ `repak info` และ `repak list` ยืนยันโครงสร้าง PAK

## ระบบภาษาในเกม

### ข้อจำกัดของ culture

เกมมีชุด culture ที่ลงทะเบียนไว้แล้ว การเพิ่ม code ใหม่ เช่น `th` อาจไม่ปรากฏใน selector แม้ LOCRES จะมีไฟล์อยู่ วิธีที่เสถียรคือใช้ slot ที่เกมรองรับอยู่แล้ว แล้ว override LOCRES ของ slot นั้น

### Slot ที่ใช้ในม็อดรุ่นแจก

| ตัวเลือกที่ผู้เล่นเห็น | Culture จริง | การแสดงผล |
|---|---|---|
| `ไทย` | `es` | UI, เมนู, เควสต์, สกิล, บทสนทนา และซับไตเติลเป็นไทย |
| `ไทย-อังกฤษ` | `de` | UI เป็นไทย; บทสนทนา/ซับไตเติลแสดงไทยบรรทัดแรกและ English บรรทัดถัดไป |

ชื่อที่แสดงใน selector ถูก override ด้วย StringTable keys:

```text
ST_Settings_Languages/es = ไทย
ST_Settings_Languages/de = ไทย-อังกฤษ
```

ต้อง override label นี้ใน OnScreens ของ `en`, `es` และ `de` เพื่อให้ชื่อถูกต้องไม่ว่า UI ปัจจุบันจะอยู่ภาษาใด

### การสร้างบทสนทนาสองภาษา

สำหรับทุก key ใน `Dialogues_All/de` ให้รวมข้อความเป็น:

```text
{translation ภาษาไทย}
{source ภาษาอังกฤษ}
```

อย่าใช้วิธีนี้กับ `OnScreens_All/de` เพราะจะทำให้เมนู, HUD และคำอธิบายไอเท็มแสดงซ้ำสองภาษาเกินความจำเป็น

### Intro cinematic

LOCRES ไม่ครอบคลุม intro cinematic ซึ่งใช้ SRT แยกตาม culture:

```text
intro_cgi_es.srt  # ไทยล้วน
intro_cgi_de.srt  # ไทย + English
```

สร้าง `intro_cgi_de.srt` โดยจับคู่ cue number ของ SRT ไทยและอังกฤษ ต้องตรวจว่าจำนวน cue และหมายเลข cue ตรงกันก่อนรวม เพื่อไม่ให้ timing เสีย

## ฟอนต์และโลโก้

ฟอนต์ UI เป็น Raw TTF ที่ใช้นามสกุล `.ufont` จึงต้องมี Thai glyph ครบในทั้ง Afacad และ RobotoCondensed ที่เกมเรียกใช้ หากข้อความเป็นสี่เหลี่ยมหรือหาย ให้ตรวจ path font ใน PAK ก่อนตรวจคำแปล

โลโก้หน้า main menu ต้อง pack asset ที่ใช้งานจริงทั้งรุ่น scaled และ small การแก้ PNG ต้นทางอย่างเดียวไม่มีผลจนกว่าจะ import กลับเป็น UAsset/UEXP และ rebuild PAK

## Checklist ก่อนปล่อยรุ่นใหม่

- [ ] Master CSV ผ่าน validator 0 error
- [ ] PAK ใช้ version V11, Oodle และ seed `3EE55F2D`
- [ ] PAK list มี OnScreens/Dialogues สำหรับ `es` และ `de`
- [ ] Export LOCRES ตรวจ `ST_Settings_Languages/es = ไทย`
- [ ] Export LOCRES ตรวจ `ST_Settings_Languages/de = ไทย-อังกฤษ`
- [ ] Export Dialogues/de ตรวจว่าตัวอย่างมีไทยและ English สองบรรทัด
- [ ] สำรองไฟล์ Game Directory ก่อน deploy และตรวจ SHA-256
- [ ] เปิดเกมใหม่ ทดสอบทั้ง `ไทย` และ `ไทย-อังกฤษ`
- [ ] ทดสอบ main menu, setting, tutorial, skill tree, dialogue, subtitle และ intro

## Troubleshooting

| อาการ | สาเหตุที่เป็นไปได้ | วิธีตรวจ/แก้ |
|---|---|---|
| เลือกภาษาแล้วแสดงข้อความอีกภาษา | ไม่มี LOCRES สำหรับ culture ที่เลือก และเกม fallback | เพิ่ม `OnScreens_All/<culture>` และ `Dialogues_All/<culture>` เข้า PAK |
| ชื่อภาษาใน Settings ยังเป็น Spanish/Deutsch | label StringTable ไม่ถูก override ใน culture ปัจจุบัน | ตรวจ `ST_Settings_Languages/es` และ `ST_Settings_Languages/de` ใน OnScreens ทุก culture ที่ mod ใช้ |
| ไทยขึ้นเป็นสี่เหลี่ยม/หาย | PAK ไม่มี font ไทย หรือ font ไม่ครบ weight | ตรวจ `.ufont` ใน PAK และทดสอบ UI หลายหน้า |
| คำอธิบายสกิลหาย/สีเพี้ยน | `<BoldCD>`, `</>`, `{n}` หรือ `<img>` หายจากคำแปล | รัน validator และคืน tag ให้ตรง source |
| Intro ไม่เป็นไทย | SRT ไม่ได้วางใน `Content/Movies` หรือ culture ไม่ตรง | ตรวจ `intro_cgi_es.srt` / `intro_cgi_de.srt` |
| เกมไม่โหลด PAK ใหม่ | ยังเปิดเกมอยู่, PAK hash เดิม, หรือ PAK metadata ไม่ตรง | ปิดเกม, ตรวจ SHA-256, รัน `repak info` |

## การแจกจ่าย

แพ็กแจกควรคงโครงสร้าง `Dawnwalker/Content/...` เพื่อให้ผู้เล่นแตก Zip แล้ว copy โฟลเดอร์ `Dawnwalker` ทับใน game root ได้ทันที หลีกเลี่ยงการแจก backup ของผู้พัฒนา และให้คู่มือระบุ Steam Verify Integrity เป็นวิธีถอนม็อดที่ปลอดภัยที่สุด

