# คัมภีร์การสร้าง Mod ภาษาไทย — Remnant II (UE5)

เอกสารนี้บันทึก pipeline ที่ทดสอบใช้งานจริงสำหรับ Remnant II: ตั้งแต่การค้นหาไฟล์ภาษา, การทำ CSV มาตรฐาน TStudio, การแก้ข้อจำกัด UTF-16LE ของ `.locres`, การใส่ฟอนต์ไทย, การแพ็ก V11 และการออกชุดแจก

## 1. ขอบเขตและผลลัพธ์

- เกม: **Remnant II** (Unreal Engine 5)
- build ที่ทดสอบ: `453438_UE`
- รูปแบบแจก: override pak ใน `Remnant2\Content\Paks\~mods`
- ไฟล์ภาษาอังกฤษที่พบ: 6 `.locres`
- รายการข้อความใน CSV รวม: **48,501**
- Mod รุ่นเผยแพร่: `v1.0.0`
- คำแปลที่ inject ใน build ล่าสุด: **46,277** รายการที่ไม่ใช่ข้อความเดิม

ตัวเลข 48,501 คือจำนวน record ใน string table ของ LocRes ไม่ได้เท่ากับจำนวนประโยคเล่าเรื่องล้วน ๆ เพราะรวม UI, engine, ชื่อปุ่ม, ข้อความระบบ และข้อความออนไลน์ด้วย

## 2. โครงสร้างโปรเจกต์

```text
E:\Mod_Workspace\Remnant2
├─ 01_Original_Backup\                 # สำรอง ห้ามแก้
├─ 01_Extract_Assets\AllEnglishLocRes\ # LocRes อังกฤษที่ extract แล้ว
├─ 01_Extract_Assets\Mappings\         # UE4SS-generated USMAP
├─ 02_Translation_Workspace\            # CSV สำหรับ TStudio/TRun
├─ 03_Font_and_UI\                      # แหล่งงานฟอนต์
├─ 04_Build\                            # pak build ปัจจุบัน
├─ 04_Build_AllLocRes\                  # staging ก่อน RePak
├─ 05_Scripts_and_Tools\                # bridge scripts เท่านั้น
└─ 06_Releases\                         # โครงสร้างและ ZIP สำหรับแจก
```

หลักสำคัญ: ห้ามแก้ไฟล์ใน `01_Original_Backup` และห้ามแก้ core ของ TStudio/TRun (`tstudio_app.py`, `trun_app.py`, `tstudio_core.py`, `file_converter.py`) เพื่อใส่ logic เฉพาะเกม

## 3. ไฟล์ภาษาและตำแหน่ง mount

ไฟล์ทั้งหกถูก extract ไว้ใต้ `01_Extract_Assets\AllEnglishLocRes` และต้องแพ็กกลับโดยรักษา path เดิม:

```text
Engine/Content/Localization/Engine/en/Engine.locres
Engine/Plugins/Online/OnlineSubsystem/Content/Localization/OnlineSubsystem/en/OnlineSubsystem.locres
Engine/Plugins/Online/OnlineSubsystemSteam/Content/Localization/OnlineSubsystemSteam/en/OnlineSubsystemSteam.locres
Engine/Plugins/Online/OnlineSubsystemUtils/Content/Localization/OnlineSubsystemUtils/en/OnlineSubsystemUtils.locres
Remnant2/Content/Localization/Remnant2/en/Remnant2.locres
Remnant2/Plugins/Shared/XeSS/Content/Localization/XeSS/en/XeSS.locres
```

`Remnant2.locres` คือข้อความเกมหลัก 22,774 record; `Engine.locres` มีข้อความระบบ/UE 25,662 record ส่วนที่เหลือเป็น Online/XeSS

## 4. การ extract และสร้าง TStudio CSV

ใช้ bridge ต่อไปนี้ ไม่ใช้ UnrealLocres.exe สำหรับการเขียนไฟล์:

```powershell
python E:\Mod_Workspace\Remnant2\05_Scripts_and_Tools\Remnant2_unpacker.py `
  --all-locres-root E:\Mod_Workspace\Remnant2\01_Extract_Assets\AllEnglishLocRes `
  --output E:\Mod_Workspace\Remnant2\02_Translation_Workspace\Remnant2_ALL_TStudio_THub.csv
```

CSV มาตรฐานต้องมีคอลัมน์เรียงตามนี้เท่านั้น:

```csv
key,source,translation,context,file_path
```

- `key` เป็น identifier ที่ห้ามเปลี่ยน
- `source` คือข้อความอังกฤษต้นฉบับที่ห้ามแก้
- `translation` คือช่องเดียวที่นักแปลควรแก้
- `context` และ `file_path` ต้องเก็บไว้ เพื่อย้อนกลับไปยัง LocRes ที่ถูกต้อง

นำ CSV เข้า TStudio หรือ TRun เพื่อแปล ห้ามสร้าง loop แปล LLM ใหม่ใน bridge ของเกม

## 5. ข้อจำกัด LocRes และการแก้ encoding ภาษาไทย

UE5 LocRes เก็บ string ได้ทั้ง UTF-8 และ UTF-16LE โดยความยาวเป็น signed integer:

- ความยาวบวก: UTF-8
- ความยาวลบ: UTF-16LE

ภาษาไทยต้องเขียนเป็น UTF-16LE พร้อมความยาวติดลบ มิฉะนั้นเกมมักแสดง `?????` แม้ฟอนต์จะถูกต้องแล้ว

`translate_locres.py` เป็น injector ที่ได้รับการทดสอบสำหรับงานนี้:

1. อ่าน string array ของ LocRes ต้นฉบับ
2. จับคู่จาก `source` ไปยัง `translation`
3. เขียนคำแปลไทยเป็น UTF-16LE และ signed length ติดลบ
4. รักษา reference count ของ LocRes version 2+ ไว้
5. รองรับ LocRes version 1 (ไม่มี reference count) และ version 3

ห้ามใช้ UnrealLocres.exe เพื่อเขียน LocRes ไทยใน pipeline นี้

## 6. ฟอนต์ไทย

ไฟล์คำแปลอย่างเดียวไม่เพียงพอ ต้องมี `ThaiFont_P.pak` ที่ inject ฟอนต์ Thai (IBMPlexSans) ลงใน font assets ที่ใช้งานจริงของเกม

ไฟล์แจกต้องมีทั้ง:

```text
pakchunk99-Windows_P.pak  # ข้อความไทย
ThaiFont_P.pak            # glyph/fallback ภาษาไทย
```

หากมีภาษาไทยแต่แสดงเป็นสี่เหลี่ยม/กล่อง ให้ตรวจ `ThaiFont_P.pak` ก่อน หากเป็น `?????` ให้ตรวจ encoding ของ LocRes ก่อน

## 7. การตรวจ CSV ก่อนแพ็ก

ใช้ validator เสมอ:

```powershell
python E:\Mod_Workspace\Remnant2\05_Scripts_and_Tools\Remnant2_validator.py `
  E:\Mod_Workspace\Remnant2\02_Translation_Workspace\<translated>.csv
```

สิ่งที่ตรวจ:

- tag เช่น `<Tag>`
- placeholder เช่น `{0}`, `{Name}`, `%s`
- ลำดับบรรทัดใหม่

### ข้อควรระวัง TRun/Spreadsheet

- TRun อาจ normalize `CRLF` เป็น `LF`; bridge packer จะคืน line break ตาม source ก่อน inject
- อย่าแก้ `source`, `key`, `context`, `file_path`
- Excel/Spreadsheet สามารถ auto-format ข้อมูล เช่น `+10`, `1/10`, `16:9`, หรือข้อความขึ้นต้น `-` ให้เสียเป็นตัวเลข/วันที่/`#NAME?`
- หากเกิดเหตุนี้ ให้ใช้ `Remnant2_repair_spreadsheet_damage.py` เพื่อคืน metadata จาก CSV ต้นฉบับก่อนแพ็ก

## 8. ชื่อปุ่ม input ต้องเป็นอังกฤษ

Unreal เก็บ display name ของ keyboard, mouse, gamepad และ VR input เป็น block เดียวใน Engine LocRes. เพื่อให้ prompt ตรงกับปุ่มจริง ให้ใช้:

```powershell
python E:\Mod_Workspace\Remnant2\05_Scripts_and_Tools\Remnant2_restore_input_key_labels.py `
  <translated.csv> <keyboard_english.csv>
```

ผลที่ต้องได้ เช่น `Escape`, `Enter`, `Tab`, `LMB`, `Left Ctrl`, `Up` ไม่ใช่คำทับศัพท์/คำแปลไทย

## 9. Pack และ deploy

ใช้ packer รวมเท่านั้น เพราะต้องแยก CSV ตาม `file_path` และเขียนกลับครบ 6 LocRes:

```powershell
python E:\Mod_Workspace\Remnant2\05_Scripts_and_Tools\Remnant2_all_locres_packer.py `
  E:\Mod_Workspace\Remnant2\02_Translation_Workspace\<translated>.csv `
  E:\Mod_Workspace\Remnant2\02_Translation_Workspace\Remnant2_ALL_TStudio_THub.csv `
  --deploy
```

ขั้นตอนของ packer:

1. ตรวจ key set และคืน metadata จาก CSV อังกฤษต้นฉบับ
2. คืน CRLF ที่ TRun normalize
3. ปฏิเสธ translation ที่มี token/placeholder ไม่ตรง
4. สร้าง bridge CSV `source,translation` แยกตาม LocRes
5. เรียก `translate_locres.py` ทุกไฟล์
6. ใช้ RePak version V11 และ mount point `../../../`
7. สำรอง mod เดิมไป `01_Original_Backup\Deploy_Backups`
8. deploy ไปยัง `Remnant2\Content\Paks\~mods`

หลังแพ็กให้ตรวจ:

```powershell
repak.exe list F:\SteamLibrary\steamapps\common\Remnant2\Remnant2\Content\Paks\~mods\pakchunk99-Windows_P.pak
```

ผลต้องมี LocRes ทั้ง 6 path ในหัวข้อ 3

## 10. สร้าง release สำหรับผู้เล่น

สร้างโครงสร้าง:

```text
Remnant2_Thai_Mod_v1.0.0_NodNuatTranslator
├─ README_TH.txt
└─ Remnant2\Content\Paks\~mods\
   ├─ pakchunk99-Windows_P.pak
   └─ ThaiFont_P.pak
```

ZIP ต้องบรรจุโฟลเดอร์ release นี้ทั้งโฟลเดอร์ ผู้เล่นจึงแตก ZIP แล้ว copy โฟลเดอร์ `Remnant2` ไป merge กับโฟลเดอร์เกมได้ทันที โดยไม่ต้องใช้ tool เพิ่ม

## 11. Smoke test หลังติดตั้ง

1. เปิดเกมและเข้าหน้าเมนู/เลือกตัวละคร
2. ตรวจภาษาไทยไม่ขึ้น `?????` หรือสี่เหลี่ยม
3. ตรวจชื่อปุ่ม เช่น `Escape`, `Tab`, `LMB` เป็นอังกฤษ
4. เปิดเมนู, settings, inventory และข้อความระบบ
5. หากมีข้อผิดพลาด ให้เอา pak ออกสองไฟล์เพื่อยืนยันว่าเกมกลับสู่ภาษาเดิมได้

## 12. สิ่งที่ต้องเก็บเป็นหลักฐาน

- CSV อังกฤษต้นฉบับ
- CSV ที่ใช้แพ็กจริง (`*_pack_safe.csv`)
- pak build และ release ZIP
- backup ก่อน deploy
- `session_log.md`

การเก็บชุดนี้ทำให้ย้อนเวอร์ชัน แก้คำแปลรายบรรทัด และสร้าง release ใหม่ได้โดยไม่ต้อง extract เกมใหม่
