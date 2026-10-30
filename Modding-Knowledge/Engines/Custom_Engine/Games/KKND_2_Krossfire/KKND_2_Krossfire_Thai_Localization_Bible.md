# คัมภีร์สร้าง Mod ภาษาไทย — Krush Kill 'N Destroy 2: Krossfire

เอกสารนี้บันทึกวิธีที่ใช้จริงในการทำให้ **Krush Kill 'N Destroy 2: Krossfire** แสดงภาษาไทยได้ถูกต้อง พร้อมคำแปลครบชุดและฟอนต์ที่จัดวางสระ/วรรณยุกต์ได้ดี เหมาะสำหรับซ่อมบำรุง ต่อยอดคำแปล หรือสร้าง release รุ่นใหม่

## 1. ข้อมูลโครงการ

- เกม: Krush Kill 'N Destroy 2: Krossfire (KKnD2)
- แพลตฟอร์มที่ทดสอบ: Steam / Windows
- เวอร์ชันไฟล์เกม: `kknd2.exe` Product Version `2.0.2-edf37d89`, File Version `2.0.2.0`
- Engine: KKnD2 engine ดั้งเดิมของ Melbourne House / Beam Software; **ไม่ใช่** Unity, Unreal หรือ Godot
- ไฟล์ข้อความ: `strings\en.yaml` (English) และ `strings\th.yaml` (Thai)
- Encoding: UTF-8 **ไม่มี BOM**
- จำนวนข้อความ: 802 key
- Mod version: v1.0
- ผู้สร้าง Mod: หน๊ด หนวด translator

## 2. โครงสร้างไฟล์และแนวทางที่เลือก

เกม Patch 2.0 โหลด YAML จากโฟลเดอร์ `strings` แบบ runtime ตามภาษาที่เลือกใน launcher จึงไม่จำเป็นต้องแกะ archive สำหรับข้อความ UI

```text
KKND 2 Krossfire\
├─ strings\
│  ├─ en.yaml     ← ต้นฉบับภาษาอังกฤษ
│  └─ th.yaml     ← คำแปลภาษาไทยที่เกมโหลดเมื่อเลือก Thai
├─ version.dll    ← Thai renderer hook
└─ thaifont.ini   ← ค่า font hook
```

จึงใช้ **Approach A — Custom Parser Plugin**:

1. Parser อ่าน `en.yaml` → TStudio CSV
2. TStudio ใช้แปลและรีวิว
3. Validator ตรวจ contract และแท็ก
4. Packer สร้าง `th.yaml` แบบ UTF-8 ไม่มี BOM

ไฟล์ archive อื่น เช่น `.lpk`, `.bpk`, `.lps`, `.spk` เป็น asset/font/sound ของ KKnD2 และไม่ใช่แหล่งข้อความหลักของงานแปลนี้

## 3. กฎความปลอดภัยและรูปแบบข้อมูล

### 3.1 YAML ที่เกมยอมรับ

```yaml
Language: Thai
00002FD2: "ไม่สามารถสร้างหน่วยใหม่ได้"
00003A8E: "หอคอยสร้างเสร็จ"
```

ข้อห้าม:

- ห้ามเพิ่ม BOM (`EF BB BF`) หน้าไฟล์
- ห้ามเปลี่ยน key hexadecimal 8 หลัก
- ห้ามเปลี่ยนลำดับหรือทำ key ซ้ำ
- ห้ามเขียน YAML syntax นอกแบบ `KEY: "ข้อความ"`

### 3.2 TStudio CSV contract

```text
key | source | translation | context | file_path
```

- `key`, `source`, `context`, `file_path` ต้องคงเดิม
- แก้เฉพาะ `translation`
- ป้องกันแท็ก `%s`, `{0}`, `<...>`, `\n`, `\r` ให้ครบและเรียงเหมือน source

## 4. เครื่องมือและ Bridge ที่ใช้

```text
E:\Mod_Workspace\Krush_Kill_‘N_Destroy_2_Krossfire\
├─ 02_Translation_Workspace\
│  └─ kknd2_krossfire_en_tstudio.csv
├─ 04_Packed_Mod\strings\th.yaml
└─ 05_Scripts_and_Tools\
   ├─ yaml_parser.py
   ├─ kknd2_krossfire_packer.py
   └─ kknd2_krossfire_validate_translation.py
```

TStudio auto-load plugin อยู่ที่:

```text
E:\Mod_Workspace\Modder_project\modder-hub\tools\flagship\TStudio\CustomParsers\yaml_parser.py
```

ชื่อ plugin ต้องเป็น `yaml_parser.py` เพราะ TStudio map นามสกุล `.yaml` ไปยังชื่อไฟล์นี้ และเรียกฟังก์ชัน `convert_to_csv(filepath, parent_widget=None)`

## 5. ขั้นตอนทำงานเต็มชุด

### 5.1 Extract English

เลือก `strings\en.yaml` ผ่าน TStudio plugin หรือเรียก parser เพื่อสร้าง CSV 802 แถวใน `02_Translation_Workspace`

### 5.2 แปลและรีวิว

เปิด CSV ด้วย TStudio ตั้งค่า API แล้วใช้ batch translation/review ผู้แปลควรเก็บคำศัพท์ UI ให้สม่ำเสมอ เช่น `OPTIONS → ตั้งค่า`, `QUIT → ออกจากเกม`

### 5.3 Validate ก่อน pack

```powershell
py -3 -B "E:\Mod_Workspace\Krush_Kill_‘N_Destroy_2_Krossfire\05_Scripts_and_Tools\kknd2_krossfire_validate_translation.py" `
  --source-csv "E:\Mod_Workspace\Krush_Kill_‘N_Destroy_2_Krossfire\02_Translation_Workspace\kknd2_krossfire_en_tstudio.csv" `
  --translated-csv "<translated CSV>"
```

validator ต้องรายงาน `VALIDATION PASSED: 802 rows; allow_empty=False`

### 5.4 Pack

```powershell
py -3 -B "E:\Mod_Workspace\Krush_Kill_‘N_Destroy_2_Krossfire\05_Scripts_and_Tools\kknd2_krossfire_packer.py" `
  --source-yaml "F:\SteamLibrary\steamapps\common\KKND 2 Krossfire\strings\en.yaml" `
  --translation-csv "<validated CSV>" `
  --output-yaml "E:\Mod_Workspace\Krush_Kill_‘N_Destroy_2_Krossfire\04_Packed_Mod\strings\th.yaml"
```

ก่อนนำไฟล์เข้าเกมต้องตรวจว่า output เป็น UTF-8 ไม่มี BOM และมี 802 key ไม่ซ้ำ

### 5.5 Checkpoint และ deploy

ก่อนเขียนทับ `strings\th.yaml` ใน Game Directory:

1. สำรอง target ไป `01_Original_Backup` โดยห้ามเขียนทับ backup เดิม
2. บันทึก SHA-256 และรายละเอียดใน `session_log.md`
3. คัดลอก `04_Packed_Mod\strings\th.yaml` ไป `Game\strings\th.yaml`
4. ตรวจ SHA-256 ของ source และ target ให้ตรงกัน

## 6. การทำให้ภาษาไทยแสดงถูกต้อง

### ปัญหา

เกมวาดฟอนต์จาก bitmap ทีละ glyph จึงไม่จัดวางสระและวรรณยุกต์ไทยแบบ complex text shaping ทำให้สระลอย

### วิธีที่ผ่านการทดสอบ

ใช้ `version.dll` Thai renderer hook คู่กับ `thaifont.ini`:

```ini
[font]
enabled=1
name=IBM Plex Sans Thai
bold=0
size_adjust=1
x_adjust=0
y_adjust=0
force_all=0
antialias=1
threshold=24
sync_wait_ms=250
```

Hook จะตรวจข้อความที่มีอักษรไทยและวาดใหม่ด้วย Windows font; ภาษาอื่นยังใช้ bitmap font เดิมของเกม

ข้อควรทราบ: `name` คือ **Font Family ที่ติดตั้งใน Windows** ไม่ใช่ path ของ `.ttf` จึงต้องติดตั้ง IBM Plex Sans Thai ก่อนเปิดเกม

## 7. ปัญหาที่พบและวิธีแก้

### TStudio บันทึก CSV แล้ว `file_path` หาย

อาการ: header ยังมี 5 คอลัมน์ แต่ทุก data row เหลือ 4 ค่า ทำให้ `file_path=None` และ validator รายงาน `malformed CSV row`

วิธีแก้ที่ปลอดภัย:

1. เก็บ CSV ที่ผู้แปลแก้ไว้โดยไม่เขียนทับ
2. สร้าง normalized copy
3. คัดลอก `file_path` ของแต่ละ key กลับจาก English source CSV เท่านั้น
4. ห้ามเปลี่ยน `key`, `source`, `translation`, `context`
5. รัน validator อีกครั้งก่อน pack

### แสดงเป็นกล่องสี่เหลี่ยม / ใช้ฟอนต์ผิด

- ตรวจว่าเกมเลือกภาษา Thai จาก launcher
- ตรวจว่ามี `version.dll` และ `thaifont.ini` อยู่ข้าง `kknd2.exe`
- ตรวจว่า IBM Plex Sans Thai ติดตั้งใน Windows และ `name=IBM Plex Sans Thai`
- ปิดเกมแล้วเปิดใหม่ทุกครั้งหลังแก้ `thaifont.ini`

### ตัวอักษรสูงเกิน/ต่ำเกิน

ปรับ `size_adjust` ทีละ 1 และปรับ `y_adjust` ทีละ 1 pixel จากนั้นเปิดเกมใหม่ทดสอบ

## 8. Release และการถอนการติดตั้ง

Release v1.0 ต้องบรรจุ:

```text
KKND2_Krossfire_Thai_Mod_v1.0\
├─ strings\th.yaml
├─ version.dll
├─ thaifont.ini
├─ Fonts\1_IBMPlexSans_fixByNodNuatTranslator_2.ttf
└─ README_TH.txt
```

ผู้เล่นติดตั้งฟอนต์หนึ่งครั้ง แล้วคัดลอกเนื้อหาในโฟลเดอร์ release ทับ root ของเกม เลือก Thai ใน launcher และเปิดเกมใหม่

ก่อน uninstall ให้ restore `strings\th.yaml` ที่สำรองไว้; หากไม่มี backup ใช้ Steam → Properties → Installed Files → Verify integrity of game files

## 9. Checklist ก่อนปล่อย

- [ ] `th.yaml` มี 802 key และ UTF-8 ไม่มี BOM
- [ ] validator ผ่าน 802/802 แถว
- [ ] Main Menu, Options, Save/Load, Singleplayer และ Multiplayer แสดงถูกต้อง
- [ ] ไม่มี tofu, `?`, สระลอย หรือ crash
- [ ] ทดสอบ font IBM Plex Sans Thai แล้ว
- [ ] release ZIP มีคู่มือ, YAML, hook, config และ TTF
- [ ] ระบุเวอร์ชันเกม/mod และเครดิตครบ

## เครดิต

- Thai Localization Mod: หน๊ด หนวด translator
- Thai renderer hook ที่ใช้เป็นฐาน: ช.ช้าง
- เกมต้นฉบับ: Melbourne House / Beam Software
