# คัมภีร์การทำม็อดภาษาไทย — STORY OF SEASONS: A Wonderful Life

> สถานะเอกสาร: Checkpoint 2+ (ยืนยันจากการทดสอบเล่นจริงเมื่อ 17 กรกฎาคม 2026)  
> ขอบเขต: แปลและแสดงภาษาไทยในเมนู, UI, การสร้างตัวละคร, บันทึกเกม, กล่องยืนยัน และบทสนทนาหลักของเกมเวอร์ชัน Steam

เอกสารนี้บันทึกวิธีที่ใช้ได้ผลจริงกับโปรเจกต์นี้ เพื่อให้แก้คำแปล สร้างฟอนต์ใหม่ แพ็ก และติดตั้งซ้ำได้โดยไม่ต้องย้อนทดลองจากศูนย์

## 1. ผลลัพธ์ที่ยืนยันแล้ว

ระบบนี้ทำให้ข้อความภาษาไทยแสดงได้จริงในส่วนต่อไปนี้

- เมนูหลักและเมนูตัวเลือก
- หน้าสร้างตัวละคร, การตั้งชื่อ และหน้าต่างยืนยัน
- UI ระหว่างเกม, บันทึกเกม และข้อความระบบ
- บทสนทนาและคำบรรยายเหตุการณ์ รวมถึงข้อความที่มีชื่อผู้เล่น
- ตัวอักษรไทยที่มีสระบน สระล่าง วรรณยุกต์ สระนำ และ `ำ`
- อักษรละตินที่ปนในประโยค เช่น ชื่อผู้เล่น ชื่อสถานที่ และเครื่องหมาย `?` โดยใช้สไตล์ฟอนต์ชุดเดียวกับภาษาไทย

ข้อจำกัดที่ทราบ: เครดิตเปิดเกมแบบตัวอักษรเลื่อน (opening credits) ยังไม่รองรับภาษาไทย และต้องปล่อยไว้ตามสภาพปัจจุบันเพื่อไม่ให้กระทบเสถียรภาพของเกม ดูรายละเอียดที่หัวข้อ 12

## 2. หลักความปลอดภัย

1. ห้ามแก้ไขไฟล์ใด ๆ ใน `01_Original_Backup` เพราะเป็นต้นฉบับย้อนกลับ
2. แก้คำแปลเฉพาะไฟล์ต้นฉบับสำหรับทำงานตามหัวข้อ 4 เท่านั้น
3. ปิดเกมก่อนแพ็กหรือคัดลอก `disc` เข้าโฟลเดอร์เกมเสมอ
4. ห้ามใช้ 7-Zip, WinRAR หรือโปรแกรม ZIP ทั่วไปเปิดแล้วบันทึกทับ `disc` เพราะไฟล์เกมเป็น ZIP เข้ารหัสที่มี layout เฉพาะ
5. ห้ามแก้ไฟล์แกนของ TStudio/TRun เพื่อรองรับเกมนี้ การเชื่อมต่อใช้สคริปต์ bridge แยกต่างหาก
6. ทุก build ต้องผ่าน validator และเทียบ hash ของไฟล์ `disc` ที่คัดลอกแล้ว

## 3. แผนที่โฟลเดอร์และหน้าที่ของไฟล์

| ตำแหน่ง | หน้าที่ |
|---|---|
| `E:\Mod_Workspace\STORY_OF_SEASONS_A_Wonderful_Life\01_Original_Backup` | ต้นฉบับที่แตกไฟล์แล้ว — อ่านอย่างเดียว |
| `...\02_Translation_Workspace` | CSV คำแปลและงานตรวจทาน |
| `...\03_Font_and_UI` | mapping อักษร, ข้อมูลฟอนต์ และผลสร้างฟอนต์ |
| `...\04_Packed_Mod` | ไฟล์ build พร้อมติดตั้ง, โดยเฉพาะ `disc` |
| `...\05_Scripts_and_Tools` | ตัวแปลง, ตัวสร้างฟอนต์, bridge, validator และ log |
| `F:\SteamLibrary\steamapps\common\STORY OF SEASONS A Wonderful Life\disc` | ไฟล์เกมปลายทางที่ถูกติดตั้ง |

ไฟล์สำคัญที่สุดสำหรับการแก้คำแปลคือ

```text
E:\Mod_Workspace\STORY_OF_SEASONS_A_Wonderful_Life\02_Translation_Workspace\vallay_message_all_GB_translate_only_typography_qa.csv
```

ไฟล์นี้คือ **master ที่มนุษย์แก้ไข** ห้ามแก้ไฟล์ `*_game_private.csv` โดยตรง เพราะเป็นไฟล์ที่ข้อความไทยถูกแปลงเป็นรหัส PUA เพื่อให้เกมวาดฟอนต์ได้แล้ว

## 4. สถาปัตยกรรมข้อความของเกม

### 4.1 ชั้นข้อมูล

ข้อความภาษาอังกฤษของเกมอยู่ใน

```text
01_Original_Backup\extracted\resource\message\vallay_message_all_GB.lzs
```

ไฟล์นี้เป็น container LZ4 ของข้อมูลข้อความเกม ไม่ใช่ TXT ธรรมดา จึงใช้ TStudio เปิดโดยตรงไม่ได้

สคริปต์ bridge ของโปรเจกต์คือ

```text
05_Scripts_and_Tools\sosawl_tstudio_bridge.py
```

หน้าที่ของมันคือแปลงระหว่าง LZS ของเกมและ CSV มาตรฐาน โดยไม่แตะระบบแกนกลางของ TStudio หรือ TRun

### 4.2 ชั้นแปล

ใช้ TStudio หรือ TRun กับ CSV ตามปกติได้ แต่ทุกแถวต้องรักษาโค้ดเกมให้เหมือนต้นฉบับ เช่น

```text
<blue>ข้อความ</blue>
<wait:30>
<playername>
<face:...>
{LF}
%s
{0}
```

แปลเฉพาะข้อความที่มนุษย์เห็น ห้ามลบ สลับ หรือแก้ไขแท็ก ตัวแปร หรือ `{LF}` เพราะสิ่งเหล่านี้เป็นคำสั่งควบคุม UI / เหตุการณ์ของเกม

### 4.3 ชั้นรหัสแสดงผล

เกมไม่มีระบบ Thai shaping ตาม Unicode ปกติ การใส่ `ก`, `่`, `ำ` ลงไปตรง ๆ จึงเคยทำให้เป็นกล่อง สระแยก หรือวางผิดตำแหน่ง

วิธีที่สำเร็จคือแปลงข้อความไทยเป็น glyph ส่วนตัวในช่วง Unicode Private Use Area (PUA) เริ่มที่ `U+E010` ก่อนแพ็กเข้าข้อมูลเกม ตัวเกมคิดว่ากำลังวาดอักษรเดี่ยวทั่วไป แต่ glyph นั้นเป็นภาพของพยางค์ไทยที่จัดรูปเสร็จแล้ว

ไฟล์ผลลัพธ์ที่เกมใช้คือ

```text
02_Translation_Workspace\vallay_message_all_GB_translate_only_game_private.csv
```

ไฟล์ mapping เพื่อให้ build ครั้งถัดไปใช้รหัสเดิมคือ

```text
03_Font_and_UI\thai_private_glyph_mapping.json
```

**ต้องเก็บ mapping นี้ไว้เสมอ** หากเปลี่ยน mapping โดยไม่มีการสร้างฟอนต์ใหม่ให้ตรงกัน ตัวเกมจะวาดอักษรผิดตัวทันที

## 5. เทคนิค PUA และการจัดรูปอักษรไทย

### 5.1 เหตุผลที่ต้องใช้ pre-shaped glyph

ภาษาไทยหนึ่งสิ่งที่เห็นบนจออาจประกอบด้วยหลาย Unicode codepoint เช่น พยัญชนะ + สระบน + วรรณยุกต์ หรือพยัญชนะ + `ำ` หากปล่อยให้ engine จัดเองจะเกิดปัญหาเหล่านี้

- สระนำ `เ แ โ ใ ไ` หลุดห่างจากพยัญชนะ
- วรรณยุกต์และสระบนทับกันหรือสูงเกิน
- สระล่างชนกับตัวอักษร
- `ำ` หายไปเหลือเพียง `ํ` หรือวางผิดตำแหน่ง

โปรเจกต์นี้จึงแบ่งข้อความเป็นกลุ่มอักขระที่ต้องวาดร่วมกัน แล้วทำกลุ่มนั้นเป็น glyph เดียวใน PUA เช่น พยัญชนะพร้อมเครื่องหมายประกอบ หรือสระนำพร้อมพยัญชนะที่ตามมา

### 5.2 กฎสำคัญของ `ำ`

ปัญหา `ำ` เคยเป็นบั๊กสำคัญ: หากแยกเป็น `ํ` และสระอาในระหว่างการเรนเดอร์ บางส่วนของรูปอักษรจะหายหรืออยู่ผิดจุด

วิธีที่แก้สำเร็จคือ

1. ถือ `ำ` และกลุ่มอักขระที่เกี่ยวข้องเป็น cluster เดียว
2. เรนเดอร์ข้อความของ cluster ทั้งชุดลง atlas โดยตรง
3. เก็บเป็น glyph PUA เดียว แทนการประกอบด้วย glyph ย่อยขณะรันเกม

ดังนั้นคำอย่าง `กำลัง`, `ทุกอย่าง`, `ตั้งค่า` จะแสดงได้ถูกต้องตามภาพทดสอบ Checkpoint 2

### 5.3 การรักษา markup ขณะแปลง

ตัวแปลงต้องสแกนและข้ามส่วนที่เป็นแท็กเกมก่อนสร้าง glyph เสมอ ตัวอย่างเช่น ในข้อความ

```text
<blue>กำลังโหลด</blue>{LF}<wait:30>
```

เฉพาะ `กำลังโหลด` เท่านั้นที่กลายเป็น PUA ส่วน `<blue>`, `</blue>`, `{LF}` และ `<wait:30>` ต้องคง byte และลำดับเดิมทุกตัว

## 6. การสร้างฟอนต์แบบ Bitmap Atlas

### 6.1 โครงสร้างฟอนต์

ฟอนต์เกมแยกเป็นสองส่วนที่ต้องตรงกัน

```text
common\font_all.lzs      = metric/ตำแหน่ง/advance ของ glyph
common\font_all_tex.lzs  = texture atlas (DDS/BC7) ที่เป็นภาพของ glyph
```

หากแก้เฉพาะ texture แต่ไม่แก้ metric ตัวอักษรจะว่าง ซ้อนกัน หรือกระโดดตำแหน่ง หากแก้เฉพาะ metric แต่ไม่มีภาพ glyph ก็จะมองไม่เห็น

### 6.2 ฟอนต์ต้นทางและรูปแบบที่ใช้

ใช้ `Leelawadee UI` เป็นต้นทางในการวาดภาษาไทยและอักษรละตินใหม่ลง atlas ผ่าน ImageMagick จากนั้นสร้าง DDS BC7 ด้วย `texconv` เพื่อให้ตรงกับ texture ของเกม

ส่วนที่สร้างและแก้ไขได้โดยสคริปต์คือ family หลักเหล่านี้

```text
FOT-PopJoyStd-B_param.bin
FOT-UDMarugo_LargePro-B_param.bin
FOT-UDMarugo_LargePro-B_S_param.bin
FZDaLTJF_Cu_param.bin
FZDaLTJF_Cu_S_param.bin
FZShaoEr-M11_param.bin
DFYuanMXBold-B5_param.bin
DFYuanMXBold-B5_S_param.bin
DFGirlW7-B5_param.bin
KoreanATR_param.bin
KoreanATR_S_param.bin
KoreanDRDSR_param.bin
FOT-PopJoyStd-B_Credit_param.bin
```

### 6.3 การวัด metric ที่ทำให้ข้อความดีขึ้น

การใช้ช่องขนาดเท่ากันทุกตัว เช่น 32×32 และ advance ตายตัว ทำให้ภาษาไทยเว้นห่างหรือซ้อนกัน วิธีที่ใช้ได้ผลคือวัดขอบหมึกจริงจาก alpha ของภาพที่เรนเดอร์แล้ว

- ใช้ความกว้างหมึกจริง + ระยะปลอดภัย 1 px เป็น advance ของ cluster ปกติ
- สระนำใช้ความกว้างหมึก + 1 px เพื่อให้ชิดพยัญชนะ ไม่ลอยออกไปด้านหน้า
- คงค่า baseline/vertical bearing จากภาพจริง เพื่อให้สระบน สระล่าง และวรรณยุกต์อยู่ระดับเดียวกัน
- ใช้ outline 1 px เพื่อให้อ่านบนฉากสว่างได้ แต่ไม่ทำให้ cluster กว้างเกิน

นี่คือสาเหตุที่ข้อความใน checkpoint หลัง ๆ อ่านง่ายขึ้น และสระนำ/วรรณยุกต์ไม่แยกจากตัวหลักแบบ build แรก

### 6.4 การทำให้ละตินและไทยเป็นฟอนต์เดียวกัน

ช่วงแรกเกมยังใช้ glyph อังกฤษดั้งเดิม ขณะที่ไทยเป็น glyph ใหม่ จึงเห็นความต่างชัดใน `?`, ชื่อผู้เล่นอย่าง `Crysers`, ตัวเลข และ Latin ที่แทรกในประโยค

วิธีแก้ที่สำเร็จคือวาด ASCII ที่แสดงผลได้ (`!` ถึง `~`) รวมถึงเครื่องหมายสำคัญ เช่น smart quote, dash, ellipsis และ Euro ด้วย `Leelawadee UI` ลงใน atlas เดียวกัน แล้วเขียน metric ทับ glyph เดิม

ผลคือข้อความไทยและอังกฤษที่อยู่ใน family หลักเดียวกันมีน้ำหนักและสัดส่วนใกล้กันมากขึ้น โดยไม่ต้องแปลงชื่อผู้เล่นหรือ markup เป็น PUA

### 6.5 ฟอนต์ขนาดเล็ก

บาง family มีพื้นที่ว่างใน atlas ไม่พอสำหรับอักษรไทยทั้งหมด สคริปต์จึงสร้าง glyph แบบกระชับสำหรับ family ที่ใช้ใน UI ขนาดเล็ก ได้แก่

```text
DFYuanMXBold-B5_S_param.bin
FZDaLTJF_Cu_S_param.bin
```

การมีชุด compact นี้ทำให้หัวข้อ UI และปุ่มขนาดเล็กมีภาษาไทย โดยไม่ต้องลดคุณภาพฟอนต์หลักของบทสนทนา

## 7. สคริปต์ที่เป็นแกนของ workflow

| สคริปต์ | หน้าที่ |
|---|---|
| `convert_sosawl_thai_to_private_glyphs.py` | แปลง CSV ที่คนแก้เป็น CSV PUA และอัปเดต mapping |
| `build_sosawl_mass_thai_fonts.py` | สร้าง atlas/metric ภาษาไทยและละตินสำหรับ family หลัก |
| `build_sosawl_mass_thai_private_fonts.py` | สร้าง glyph PUA จำนวนมากจาก mapping ปัจจุบัน |
| `patch_sosawl_private_small_fonts.py` | เติม glyph PUA แบบ compact ให้ฟอนต์เล็ก |
| `sosawl_tstudio_bridge.py` | แปลง/แพ็ก LZS ข้อความเกมกับ CSV |
| `build_main_menu_poc.py` | ประกอบไฟล์ข้อความและฟอนต์กลับเข้า `disc` โดยรักษา archive layout/การเข้ารหัส |
| `validate_menu_poc_archive.py` | ตรวจว่า 3 รายการสำคัญอยู่ใน `disc` และโครงสร้าง archive ยังถูกต้อง |

## 8. ขั้นตอนทำงานมาตรฐานเมื่อแก้คำแปล

### ขั้นที่ 1 — แก้ CSV ที่ถูกต้อง

เปิดและแก้เฉพาะไฟล์นี้ด้วย TStudio, spreadsheet editor ที่รองรับ UTF-8 หรือ text editor ที่ไม่ทำให้ CSV เสีย

```text
02_Translation_Workspace\vallay_message_all_GB_translate_only_typography_qa.csv
```

ตรวจสอบให้แน่ใจว่าคอลัมน์ ID ไม่เปลี่ยน และแท็ก/ตัวแปรคงเดิม

### ขั้นที่ 2 — สร้างรหัส PUA ใหม่

เปิด PowerShell ที่โฟลเดอร์สคริปต์ แล้วรัน

```powershell
python E:\Mod_Workspace\STORY_OF_SEASONS_A_Wonderful_Life\05_Scripts_and_Tools\convert_sosawl_thai_to_private_glyphs.py
```

ผลที่คาดหวัง

- CSV `vallay_message_all_GB_translate_only_game_private.csv` ถูกอัปเดต
- `thai_private_glyph_mapping.json` ถูกอัปเดตโดยรักษารหัสเก่าที่เคยมี
- รายงานจำนวน glyph และจำนวนข้อความที่แปลงแล้ว

### ขั้นที่ 3 — สร้างฟอนต์ให้ตรงกับ mapping

รันตามลำดับนี้

```powershell
python E:\Mod_Workspace\STORY_OF_SEASONS_A_Wonderful_Life\05_Scripts_and_Tools\build_sosawl_mass_thai_fonts.py
python E:\Mod_Workspace\STORY_OF_SEASONS_A_Wonderful_Life\05_Scripts_and_Tools\build_sosawl_mass_thai_private_fonts.py
python E:\Mod_Workspace\STORY_OF_SEASONS_A_Wonderful_Life\05_Scripts_and_Tools\patch_sosawl_private_small_fonts.py
```

คำเตือน: หากข้ามขั้นนี้หลังเพิ่มคำไทยใหม่ เกมอาจแสดงตัวว่าง/อักษรผิด เพราะ CSV อ้าง PUA ที่ยังไม่มีใน atlas

### ขั้นที่ 4 — แพ็กข้อความกลับเป็น LZS

```powershell
python E:\Mod_Workspace\STORY_OF_SEASONS_A_Wonderful_Life\05_Scripts_and_Tools\sosawl_tstudio_bridge.py pack `
  E:\Mod_Workspace\STORY_OF_SEASONS_A_Wonderful_Life\01_Original_Backup\extracted\resource\message\vallay_message_all_GB.lzs `
  E:\Mod_Workspace\STORY_OF_SEASONS_A_Wonderful_Life\02_Translation_Workspace\vallay_message_all_GB_translate_only_game_private.csv `
  E:\Mod_Workspace\STORY_OF_SEASONS_A_Wonderful_Life\04_Packed_Mod\resource\message\vallay_message_all_GB.lzs
```

### ขั้นที่ 5 — สร้าง `disc`

```powershell
python E:\Mod_Workspace\STORY_OF_SEASONS_A_Wonderful_Life\05_Scripts_and_Tools\build_main_menu_poc.py
python E:\Mod_Workspace\STORY_OF_SEASONS_A_Wonderful_Life\05_Scripts_and_Tools\validate_menu_poc_archive.py
```

ตัวสร้าง `disc` ไม่ได้สร้าง ZIP ใหม่แบบทั่วไป แต่คงรูปแบบ ZipCrypto, data descriptor และตำแหน่งรายการของเกมไว้ จึงเป็นขั้นตอนบังคับ

### ขั้นที่ 6 — ติดตั้งและตรวจสอบ hash

ปิดเกมก่อน จากนั้นรัน

```powershell
Copy-Item `
  E:\Mod_Workspace\STORY_OF_SEASONS_A_Wonderful_Life\04_Packed_Mod\disc `
  F:\SteamLibrary\steamapps\common\STORY OF SEASONS A Wonderful Life\disc `
  -Force

Get-FileHash E:\Mod_Workspace\STORY_OF_SEASONS_A_Wonderful_Life\04_Packed_Mod\disc
Get-FileHash 'F:\SteamLibrary\steamapps\common\STORY OF SEASONS A Wonderful Life\disc'
```

ค่า SHA256 สองบรรทัดต้องตรงกันจึงถือว่าติดตั้งสำเร็จ

## 9. การตรวจคุณภาพก่อนส่งทดสอบ

ตรวจอย่างน้อย 6 จุดหลัง build ทุกครั้ง

1. เมนูหลัก: โหลด/เล่นต่อ/เริ่มเกมใหม่/ตั้งค่า
2. หน้าต่างตั้งชื่อ: ข้อความไทย + ชื่อผู้เล่นละติน + `?`
3. หน้าสร้างตัวละคร: หัวข้อ ปุ่ม และข้อความช่วยเหลือ
4. หน้าบันทึกเกม: วันที่ สถานที่ ชื่อตัวละคร และข้อความระบบ
5. บทนำชายหาด: ประโยคยาวหลายบรรทัด มี `ำ`, สระนำ และวรรณยุกต์
6. บทสนทนากลางเกม: ชื่อผู้พูด ภาษาไทยผสมชื่อ/คำละติน และ tag สีหรือคำสั่ง

เกณฑ์ผ่าน

- ไม่มีตัวกล่องหรือช่องว่างแทนอักษรไทย
- `ำ` วาดครบทั้งรูป ไม่ขาดเป็นจุด/สระเดี่ยว
- สระนำไม่ลอยห่างจากพยัญชนะ
- บรรทัดไม่ชนกัน และข้อความไม่หลุดกรอบในหน้าที่ทดสอบ
- เครื่องหมายและ Latin ที่แทรกมีสัดส่วนเข้ากับไทย
- เกมเข้าสู่เมนูและเล่นต่อได้โดยไม่ crash

## 10. ตารางแก้ปัญหาจากอาการ

| อาการ | สาเหตุที่น่าจะเป็น | วิธีตรวจ/แก้ |
|---|---|---|
| เมนูว่างทั้งปุ่ม | `disc` ใหม่ไม่ถูกติดตั้ง หรือ archive เสีย | รัน validator, ตรวจ hash และคัดลอกใหม่ขณะเกมปิด |
| ไทยเป็นกล่อง/ว่าง | CSV มี PUA แต่ atlas ไม่มี glyph นั้น | รัน conversion และ build font ทั้ง 3 ขั้นใหม่ |
| วรรณยุกต์/สระวางผิด | กลุ่มไทยถูกแยกเป็น codepoint หรือ metric ใช้ advance ตายตัว | ตรวจ cluster logic และใช้ metric จาก ink bounds |
| `ำ` หายหรือผิดตำแหน่ง | แยก `ำ` เป็นชิ้นย่อยขณะ render | รักษา cluster `ำ` เป็น pre-shaped glyph เดียว |
| `เ` ลอยห่างจากพยัญชนะ | advance ของสระนำกว้างเกิน | ใช้ ink width + 1 px สำหรับสระนำ |
| `?` หรือชื่ออังกฤษดูคนละฟอนต์ | ยังใช้ Latin glyph เดิมของเกม | build ส่วน Latin replacement ใน family ที่ใช้ |
| ข้อความมี tag โผล่หรือ UI ทำงานผิด | แท็ก/ตัวแปรถูกแก้หรือลบใน CSV | คืน tag จาก source แล้วแปลเฉพาะข้อความ visible |
| แก้ CSV แล้วเกมเหมือนไม่เปลี่ยน | ใช้ไฟล์ผิด หรือข้าม conversion/pack | ตรวจว่าแก้ `*_typography_qa.csv` และรันครบขั้น 2–6 |

## 11. สิ่งที่ไม่ควรทำ

- อย่าแก้ `vallay_message_all_GB_translate_only_game_private.csv` ด้วยมือ
- อย่าลบหรือ reset `thai_private_glyph_mapping.json`
- อย่าใช้ตัวแปลง Unicode ไทยตรง ๆ โดยไม่ผ่าน PUA/pre-shaped glyph
- อย่าเปลี่ยนขนาด cell หรือ metric ทั้งหมดแบบ global โดยไม่ทำ preview และทดสอบจริง
- อย่าเอา `disc` ผ่านคำสั่ง ZIP/recompress ของโปรแกรมทั่วไป
- อย่าแก้ `01_Original_Backup` หรือใช้มันเป็น output build
- อย่าแก้ core ของ TStudio/TRun เพื่อใส่ logic เกมนี้

## 12. ข้อจำกัดที่ทราบ: เครดิตเปิดเกม

ฉาก opening credits ใช้ family พิเศษ

```text
FOT-PopJoyStd-B_Credit_param.bin
```

atlas ของ family นี้มีพื้นที่ว่างไม่พอที่จะรองรับ private glyph ภาษาไทยจำนวนมากที่ต้องใช้ในข้อความเครดิต การแสดงผลในฉากดังกล่าวจึงเป็นเส้นตัวอักษรเล็กมาก หรือเหมือนค้างเพราะ glyph ที่เรียกไม่มีในฟอนต์นั้น

การแก้แบบสมบูรณ์ต้องออกแบบ atlas/metric สำหรับ credit scroll แยกต่างหาก แล้วทดสอบ animation timing ของฉากเครดิตโดยเฉพาะ ซึ่งมีความเสี่ยงต่อระบบสูงกว่าส่วน UI และบทสนทนาปกติ

สถานะที่ตกลงไว้ในโปรเจกต์คือ **ไม่แก้ส่วนเครดิตต่อในตอนนี้** เพื่อรักษา build ที่เกมเล่นได้และแสดงไทยในส่วนหลักได้ดี

## 13. สถานะ Checkpoint 2 ที่ควรยึดเป็นฐาน

Checkpoint 2 คือจุดที่ยืนยันได้ว่า

- ม็อดภาษาไทยถูกแพ็กใน `disc` แล้ว
- เมนู/UI/กล่องยืนยัน/การสร้างตัวละคร/บันทึกเกม/บทสนทนาหลักแสดงไทย
- `ำ` ได้รับการแก้แบบ cluster rendering
- Latin และเครื่องหมายหลักได้รับการทำให้สไตล์สอดคล้องกับไทย
- การจัดวางข้อความดีขึ้นจากการใช้ ink-bound metrics

หากจะทดลองวิธีใหม่กับฟอนต์ ให้เก็บสำเนา `04_Packed_Mod\disc` ที่ผ่าน checkpoint นี้ไว้ก่อนเสมอ แล้วทดลองบน output แยก ไม่แก้ทับฐานที่ใช้งานได้

## 14. เช็กลิสต์สำหรับผู้แปลและผู้แพ็ก

### เมื่อผู้แปลส่งงาน

- [ ] แก้เฉพาะ `vallay_message_all_GB_translate_only_typography_qa.csv`
- [ ] ไม่เปลี่ยน ID, tag, variable และ `{LF}`
- [ ] ตรวจชื่อเฉพาะให้ใช้คำเดียวกันทั้งเกม
- [ ] แจ้งว่าบันทึกไฟล์เป็น UTF-8 และปิดไฟล์แล้ว

### เมื่อผู้แพ็ก build

- [ ] รัน convert PUA
- [ ] รัน builder font ทั้งหมดเมื่อมีคำ/cluster ใหม่
- [ ] pack LZS
- [ ] build `disc`
- [ ] รัน validator
- [ ] ติดตั้งขณะเกมปิด
- [ ] เทียบ SHA256
- [ ] ทดสอบเมนู, UI, บทนำ และบทสนทนาอย่างน้อยหนึ่งฉาก
- [ ] บันทึกผลลง `05_Scripts_and_Tools\session_log.md`

## 15. สรุปเทคนิคที่ทำให้โปรเจกต์สำเร็จ

1. ใช้ bridge แยกเกมกับ TStudio/TRun เพื่อรักษาเครื่องมือแปลหลักให้เป็น generic
2. แปลงข้อความไทยเป็น PUA แทนการบังคับ engine ให้รองรับ Unicode Thai
3. ทำ pre-shaped glyph สำหรับกลุ่มไทย ไม่ใช่ glyph เดี่ยวทุก codepoint
4. จัดการ `ำ` เป็น cluster เต็มรูปก่อน render
5. สร้าง bitmap atlas พร้อม metric ที่วัดจาก ink bounds จริง
6. ให้สระนำมี advance แคบพอดีและคง baseline ของสระ/วรรณยุกต์
7. แทนที่ glyph ละตินและเครื่องหมายที่ใช้จริง เพื่อให้ไทย-อังกฤษในประโยคเดียวกันกลมกลืน
8. มี font compact แยกสำหรับ UI ขนาดเล็ก
9. แพ็ก `disc` ด้วย script ที่รักษาการเข้ารหัสและ layout ของ archive เกม
10. ตรวจ validator, hash และทดสอบในเกมทุก build

เมื่อยึด workflow นี้ การแก้คำแปลในอนาคตจะเป็นงานแก้ CSV → สร้าง PUA/ฟอนต์ → แพ็ก → ติดตั้ง โดยไม่ต้องย้อนแก้ไฟล์เกมด้วยมือ
