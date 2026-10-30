# LOST EPIC — Thai Localization Bible

## 1. Engine และโครงสร้างไฟล์

- เกม: **LOST EPIC** (Steam build tested: Release 1.02.1)
- Engine: Unity 2020.3.22f1, IL2CPP, 64-bit Windows.
- ตัวอักษรอยู่ใน Unity serialized assets โดยเฉพาะ `LOSTEPIC_Data/level10` และ `sharedassets0.assets`; มีทั้ง `MonoBehaviour` strings, `TextAsset` และ text objects ที่ถูกจัดกลุ่มตาม locale.
- กลุ่มภาษาใน data tables เรียงเป็น Japanese, English, Chinese Simplified, Chinese Traditional, Korean, Spanish, Portuguese (Brazil), German และ French.
- ไม่มีการยืนยันการใช้ AES encryption กับข้อความ. Unity assets มีโครงสร้าง serialized binary; การเขียนกลับด้วย UnityPy ให้ไฟล์เปิดซ้ำได้ แต่เกมตรวจความสอดคล้องภายในและอาจ crash หาก layout เปลี่ยน.

## 2. การสกัดข้อความและแปลงกลับ

ใช้ bridge scripts ใน `LOST_EPIC/05_Scripts_and_Tools/` เท่านั้น:

- `lost_epic_unpacker.py` สกัดข้อความออกเป็น TStudio CSV.
- `extract_english_by_locale.py` กรอง English ที่เป็น locale จริงจาก array index 1 และ scene hierarchy `En`; ผลลัพธ์คือ `LOST_EPIC_English_TStudio.csv`.
- `split_tstudio_japanese_english.py` แยก Japanese/English สำหรับงานแปลที่ต้องใช้สองต้นฉบับ.
- `prepare_translated_pack.py` ตรวจ tag, normalize character ที่ฟอนต์ไม่มี และแปลง Thai เป็น PUA.
- `build_runtime_translation_map.py` สร้าง dictionary แบบ Base64 TSV สำหรับ runtime.

TStudio CSV ใช้ schema `key | source | translation | context | file_path`; ห้ามแก้ `source` และต้องคง tags เช่น `%s`, `{0}`, `\\n`, `\\r`, `<color=...>` ไว้ครบถ้วน.

การ repack Unity asset แบบ direct ถูกทดลองแล้วทำให้เกม crash ด้วย `Size overflow in allocator.` จึงไม่ใช้ผลลัพธ์ที่ reserialize assets ในชุดแจกจ่าย. วิธีที่ผ่านการทดสอบคือ runtime replacement ผ่าน BepInEx.

## 3. ระบบฟอนต์ไทยและสระวรรณยุกต์

- ฟอนต์ที่ใช้: Prompt Bold PUA.
- ฟอนต์เผยแพร่: `BepInEx/plugins/Prompt-Bold_PUA.ttf`.
- PUA mapping: U+F000–U+F89F, จัดรูปสระและวรรณยุกต์ล่วงหน้า.
- `thai_font_mapper.py` และ `Mapping.json` เป็นแหล่ง mapping.
- สระ ่ ้ ๊ ๋ ใน PUA composites ถูกยกขึ้น 180 font units เพื่อไม่ให้ทับสระอิ/อีและเครื่องหมายบนอื่น.

Plugin สร้าง TextMeshPro/TextCore dynamic atlas ที่ runtime จาก `LOST_EPIC_Thai_Characters.txt` และเปลี่ยน font ให้กับข้อความที่มี Thai/PUA. Log ที่ยืนยันการทำงานรายงาน 600 glyphs/characters; TAB และ NEWLINE ที่ไม่สร้าง glyph เป็น control characters ที่ถูกต้อง.

## 4. Tag protection และความปลอดภัยคำแปล

ก่อนสร้าง runtime map ให้ตรวจว่าชุด protected tokens ใน `source` และ `translation` เท่ากัน. Validator ยอมรับเฉพาะความแตกต่างของ line ending (`\\r`/`\\n`) และต้อง pack จาก source master. แก้ contamination ที่ตรวจพบในคำแปล (Arabic/Cyrillic) ก่อนส่งออก และแทน symbol ที่ฟอนต์ไม่มีด้วย equivalent ที่ปลอดภัย เช่น `Ⅱ` เป็น `II`.

## 5. Automation สำหรับ runtime pack

ลำดับที่ทดสอบแล้ว:

1. ตรวจ CSV ที่แปลเสร็จด้วย `prepare_translated_pack.py`.
2. สร้าง `LOST_EPIC_Thai_Runtime.tsv` ด้วย `build_runtime_translation_map.py`.
3. Compile `LOSTEpicThaiRuntime` และวาง DLL, TTF, TSV และ character list ใน `BepInEx/plugins`.
4. วาง BepInEx 6 IL2CPP loader ที่ game root (`winhttp.dll`, `doorstop_config.ini`, `dotnet/`, `BepInEx/`).

Runtime map มี 4,367 English source mappings จาก 5,735 rows ที่แปลแล้ว. Strings ภาษาอังกฤษที่ซ้ำกันแต่มีคำแปลต่างกันจะใช้คำแปลที่พบบ่อยที่สุด จึงควรตรวจ scene ที่มีข้อความสั้นซ้ำกันเป็นพิเศษเมื่อมีรายงานจากผู้เล่น.

## 6. โครงสร้างชุดแจกจ่าย

```
LOST EPIC_ThaiMod_v1.0/
├─ winhttp.dll
├─ doorstop_config.ini
├─ dotnet/
├─ BepInEx/
│  ├─ core/
│  ├─ patchers/
│  └─ plugins/
│     ├─ LOSTEpicThaiRuntime.dll
│     ├─ LOST_EPIC_Thai_Runtime.tsv
│     ├─ LOST_EPIC_Thai_Characters.txt
│     └─ Prompt-Bold_PUA.ttf
├─ คู่มือติดตั้ง_README.txt
└─ README_TH.txt
```

ผู้เล่นคัดลอกเนื้อหาภายในโฟลเดอร์นี้ไปที่ root ของ LOST EPIC แล้วเลือก Replace/Merge. ไม่แจก Unity asset ที่ reserialize แล้ว.

## 7. ปัญหาและวิธีแก้

| อาการ | สาเหตุ | วิธีแก้ที่ยืนยันแล้ว |
|---|---|---|
| เกม crash ตอนเริ่มด้วย `Size overflow in allocator` | Unity serialized asset ถูกเขียนกลับด้วย layout ที่เกมไม่ยอมรับ | Restore original assets และใช้ BepInEx runtime replacement |
| อักษรไทยเป็นกล่อง | TMP font ไม่มี glyph ไทย | Deploy Prompt PUA และให้ plugin สร้าง dynamic TMP atlas |
| วรรณยุกต์ทับสระบน | metrics ของ glyph composite ต่ำเกินไป | ใช้ Prompt PUA รุ่นยก tone marks +180 units |
| เกมยังเป็นภาษาอังกฤษ | plugin/map ไม่ถูกโหลด | ตรวจ `BepInEx/LogOutput.log`, `LOST_EPIC_Thai_Runtime.tsv`, DLL และ font ใน `plugins/` |
| ข้อความหนึ่งไม่ตรงบริบท | English source ซ้ำหลาย context | ตรวจ key/context ใน CSV และเพิ่ม context-aware mapping เมื่อจำเป็น |

## 8. เปรียบเทียบกับ Unity localization อื่น

รูปแบบนี้ต่างจาก Unity games ที่เก็บ locale เป็น JSON หรือ Addressables แบบ loose file: LOST EPIC เก็บข้อความใน serialized assets และ direct rewrite ไม่ปลอดภัยกับ build นี้. แนวทาง BepInEx + TextMeshPro dynamic font atlas เหมาะเมื่อ Unity IL2CPP สามารถ hook text components ได้และต้องรองรับ Thai shaping ผ่าน PUA. หลักการเดียวกันนำไปใช้ได้กับเกม Unity IL2CPP อื่น แต่ชื่อ components, assets, Unity version และ loader compatibility ต้องตรวจใหม่ทุกเกม.

