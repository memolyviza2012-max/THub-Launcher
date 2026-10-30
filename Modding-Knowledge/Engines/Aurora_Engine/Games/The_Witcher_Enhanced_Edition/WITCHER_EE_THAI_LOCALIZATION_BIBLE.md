# คัมภีร์ทำม็อดภาษาไทย: The Witcher: Enhanced Edition Director's Cut

> สถานะอ้างอิง: ม็อดภาษาไทย v1.0.0  
> เกมเป้าหมาย: The Witcher: Enhanced Edition Director's Cut (PC, build 1.4.5.1304)  
> ผู้แปล: หน๊ด หนวด translator

เอกสารนี้บันทึกกระบวนการที่ใช้จริงในการทำให้ **The Witcher: Enhanced Edition Director's Cut** แสดงภาษาไทยได้ครบทั้งบทสนทนา, UI, เควสต์ และข้อความสถิตในแผนที่ โดยเน้นหลักการที่นำกลับมาใช้ซ้ำได้กับเกม Aurora รุ่นเดียวกัน

## 1. ผลลัพธ์ของม็อด

ม็อดฉบับ v1.0.0 มีข้อความที่จัดการได้ทั้งหมด **41,518 รายการ**

| ขอบเขต | จำนวน | แหล่งข้อมูล |
|---|---:|---|
| บทสนทนา | 22,959 | `Data/dialogues00.bif` → GFF `DLG` → LocString `Text` |
| UI และระบบ | 2,573 | `Data/dialog_3.tlk` |
| ชื่อ/คำอธิบาย/เควสต์/ข้อความในโมดูล | 15,986 | GFF `LocString` ใน templates, quests และ MOD |
| รวม | **41,518** | ไฟล์ต้นฉบับแปลรวมหนึ่งไฟล์ |

ไม่มีการแปลเสียงพากย์ ไฟล์เสียง และภาพที่มีตัวอักษรฝังอยู่

## 2. สถาปัตยกรรมภาษาและฟอนต์

เกมใช้ Aurora Engine และมีเส้นทางข้อความหลายชนิด จึงไม่สามารถแก้เพียงไฟล์เดียวได้

```text
ข้อความบทสนทนา     dialogues00.bif → DLG/GFF LocString
ข้อความ UI          dialog_3.tlk    → TLK string table
ชื่อและเควสต์       templates/quests/MOD → GFF LocString
การแสดงผลไทย        Data/Override/fonts.2da + fonts_zh.2da + thainoto.ttf
การอ่าน UTF-8 ของ TLK  2da00.bif → FinalEnglish_Short codepage 65001
```

### ฟอนต์ PUA

ฟอนต์เดิมไม่มี glyph ภาษาไทยที่ใช้ได้ตรง ๆ จึงใช้ `thainoto.ttf` แบบ **pure PUA**:

- อักษรละตินปกติไม่ถูกแทนที่ จึงไม่ทำให้คำอังกฤษหรือ token ของเอนจินเพี้ยน
- เครื่องหมายประกอบภาษาไทยใช้ glyph ใน Private Use Area (PUA)
- มีการยกตำแหน่งวรรณยุกต์ `่ ้ ๊ ๋` ขึ้นรวม 160 หน่วยจากการทดสอบภาพจริง เพื่อไม่ให้ชนอักษรฐาน
- สคริปต์แพ็กแปลงข้อความไทยเป็น PUA ด้วย longest-match mapping จาก `Mapping.json` ก่อนเขียนกลับเข้าเกม

### UTF-8 สำหรับ TLK

`dialog_3.tlk` ถูกเขียนเป็น UTF-8 และแก้ code page ของแถว `FinalEnglish_Short` ใน `Data/2da00.bif` จาก 874 เป็น 65001 เพื่อให้ตัวอ่าน TLK ไม่ตีความ UTF-8 เป็นอักขระเพี้ยน

## 3. รูปแบบไฟล์และขอบเขตที่แปลได้อย่างปลอดภัย

### BIF และ MOD

- `.bif` เป็นคลัง resource ของเกม
- `.mod` เป็น archive แบบ `MOD V1.0` สำหรับโมดูล/แผนที่
- resource หลักเป็น GFF v3 (`DLG`, `UTC`, `UTI`, `JRL`, `ARE`, `GIT` และอื่น ๆ)
- GFF มี FieldData แบบความยาวแปรผัน จึงต้อง rebuild buffer และชดเชย offset ของ resource ทุกตัวที่อยู่ถัดไปเสมอ

### LocString เทียบกับ CExoString

`LocString` คือชนิดข้อความหลายภาษา และเป็นขอบเขตที่ใช้ในม็อดแจกจริง

ห้ามแปล `CExoString` แบบเหมารวม แม้จะดูเหมือนข้อความอ่านได้ เพราะชนิดนี้ยังถูกใช้เก็บ:

- tag ของ object และ action point
- ชื่อสคริปต์และ resource reference
- ชื่อ field เชิงเทคนิคและค่า metadata ของ GUI

การส่ง CExoString ทั้งหมดผ่านโปรแกรมแปลทำให้ค่าภายใน เช่น `ap_stand` ถูกแปล และทำให้เกมเด้งระหว่างเริ่มต้นได้ ม็อด v1.0.0 จึงแปลเฉพาะ LocString สำหรับข้อความ static เพื่อคงความเสถียรของเอนจิน

## 4. ไฟล์ต้นฉบับแปลหนึ่งเดียว

ไฟล์ที่ใช้แก้ข้อความทั้งหมดคือ:

```text
02_Translation_Workspace\witcher_ee_thai_localization_master.csv
```

คอลัมน์สำคัญ:

| คอลัมน์ | หน้าที่ | กฎ |
|---|---|---|
| `asset_group` | ระบุปลายทาง: `dialogue`, `ui_system`, `static_locstring` | ห้ามแก้ |
| `key` | ตำแหน่งถาวรของข้อความในไฟล์เกม | ห้ามแก้/ลบ/สลับ |
| `source` | ข้อความอังกฤษต้นฉบับ | เก็บไว้สำหรับตรวจสอบ |
| `translation` | ข้อความไทยที่จะแก้ | แก้เฉพาะคอลัมน์นี้ |
| `context` | บริบทจากแหล่งเดิม | ใช้อ้างอิง ไม่ต้องแปล |
| `file_path` | ข้อมูลประกอบเดิม | TStudio อาจเว้นว่างได้; packer อาศัย `key` |

ก่อนนำไฟล์เข้า TStudio ให้สำรองหนึ่งชุด และหลัง export ต้องตรวจว่า CSV มีครบ 41,518 แถวและค่า `key` ไม่ซ้ำ

## 5. ขั้นตอนผลิตม็อด

### 5.1 สำรองไฟล์เกมก่อนเสมอ

สำรองไฟล์ที่จะถูกแทนที่จาก `Data` ก่อนแก้ไข โดยเฉพาะ `dialogues00.bif`, `dialog_3.tlk`, `2da00.bif`, `templates00.bif`, `quests00.bif` และไฟล์ใน `Data/modules/!Final`.

### 5.2 ส่งออกข้อความ

1. อ่าน `dialogues00.bif` และเลือก effective-English ด้วยลำดับ LocString ID `6 → 4 → 2` ไม่ใช่เลือก ID เดียว
2. ส่งออก UI จาก `dialog_3.tlk`
3. เดิน GFF ใน templates, quests และโมดูล `.mod` แต่รับเฉพาะ `LocString`
4. รวมเป็น master CSV และตรวจ key ซ้ำ/ข้อความว่าง

### 5.3 แปลและตรวจ token

แก้เฉพาะ `translation` โดยคง token ของเอนจินไว้ เช่น:

```text
<ACTIONKEY:...>
<c...> และ </c>
[TAG_...]
```

ตัวแพ็กต้องตรวจและคง token ต้นฉบับไว้ หากโปรแกรมแปลลบหรือทำ tag ปิดเสียรูป เพราะ tag เหล่านี้เป็นคำสั่งของเอนจิน ไม่ใช่ข้อความธรรมดา

### 5.4 แพ็กกลับ

1. แยก master CSV ตาม `asset_group`
2. แปลงอักษรไทยเป็น PUA
3. เขียน `dialogues00.bif` จาก GFF DLG ที่เปลี่ยนความยาว FieldData แล้วอัปเดต BIF resource offset
4. เขียน `dialog_3.tlk` เป็น UTF-8 พร้อมรักษา control tag
5. เขียน LocString ของ `templates00.bif`, `quests00.bif` และ 13 โมดูลใน `Data/modules/!Final`
6. ตรวจจำนวน key ที่แพ็กได้ต้องเท่ากับจำนวน key ที่ส่งเข้าในแต่ละกลุ่ม

### 5.5 ทดสอบก่อนแจก

- เปิดถึง Main Menu และ Options
- เริ่มเกม/โหลดเซฟและทดสอบบทสนทนา
- ตรวจชื่อศัตรูและ NPC เหนือหัว
- ตรวจ quest update, Journal, tutorial และกล่องยืนยัน
- ตรวจวรรณยุกต์ `่ ้ ๊ ๋` ในขนาดฟอนต์หลายระดับ
- ปิดเกม เปิดใหม่ และตรวจไม่มี crash log ใหม่

## 6. โครงสร้างรีลีส v1.0.0

รีลีสคัดลอกทับ root ของเกมได้โดยตรง:

```text
The_Witcher_Enhanced_Edition_Directors_Cut_Thai_Mod_v1.0.0\
├─ README_TH.md
└─ Data\
   ├─ 2da00.bif
   ├─ dialog_3.tlk
   ├─ dialogues00.bif
   ├─ templates00.bif
   ├─ quests00.bif
   ├─ Override\
   │  ├─ fonts.2da
   │  ├─ fonts_zh.2da
   │  └─ thainoto.ttf
   └─ modules\!Final\*.mod  (13 ไฟล์)
```

การถอนม็อดที่ปลอดภัยที่สุดคือ Steam → Properties → Installed Files → Verify integrity of game files เพราะม็อดแทนที่ BIF/MOD ต้นฉบับทั้งไฟล์ ไม่ควรลบไฟล์ BIF หรือ MOD ทิ้งด้วยมือ

## 7. บทเรียนสำคัญ

1. อย่าพิสูจน์เส้นทางฟอนต์ด้วยการแทน glyph ASCII ทั้งชุด: UI ส่วนอื่นจะเพี้ยนทันที
2. UI TLK, บทสนทนา DLG และ static GFF เป็นคนละเส้นทาง ต้องส่งออก/แพ็ก/ทดสอบแยกกัน
3. Text editor อาจทำ CSV, line break และ control tag เสียหาย จึงต้องมี key validation และ sanitizer
4. แปลเฉพาะ field ที่มี semantic เป็น localizable text; ข้อความที่เห็นได้ไม่เท่ากับข้อความที่ปลอดภัยต่อการแปล
5. ทุกครั้งที่ rebuild binary archive ให้ตรวจทั้งโครงสร้าง, จำนวน resource, offset และทดสอบเปิดเกมจริง

