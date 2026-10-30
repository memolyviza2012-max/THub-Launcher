# HELLDIVERS 2 Thai Localization Bible

## 1. Engine และโครงสร้างไฟล์

HELLDIVERS 2 ใช้เอนจิน custom บนสายเทคโนโลยี Stingray/Noesis UI. ไฟล์ทรัพยากรอยู่ใต้ `data` เป็น archive triad ได้แก่ main (ไม่มีนามสกุล), `.stream` และ `.gpu_resources`; archive หลักมี `bundles*.nxa`. Patch ที่ม็อดใช้มี magic little-endian `0xF0000011` และ TOC ของ resource.

Resource type ที่ยืนยันในโปรเจกต์นี้คือ string table `0x0D972BAB10B40FD3`, font descriptor `0x9EFE0A916AAE7880`, runtime font `0x05106B81DCD58A13` และ texture `0xCD4238C6A0C69E32`.

ไม่มีการยืนยัน compression หรือ AES สำหรับ patch ที่สร้างในโครงการนี้ และไม่ใช้ key/การถอดรหัสใด ๆ. ไฟล์ attribute บางส่วนใต้ `data/game` อาจถูกเข้ารหัส แต่ไม่อยู่ในขอบเขต localization นี้.

## 2. การสกัดและแปลงข้อความ

ใช้ FileDiver export string resources แบบ read-only แล้วใช้ `05_Scripts_and_Tools/HELLDIVERS_2_unpacker.py` แปลงเป็น TStudio CSV: `key | source | translation | context | file_path`.

ชุด English (US) ที่ทดสอบได้มี 18 string tables และ 24,603 key ที่แปลได้. ไฟล์อ้างอิงที่ห้ามแก้คือ `02_Translation_Workspace/HELLDIVERS_2_English_Source_Baseline.csv`; งานแปลที่ผ่านการตรวจอยู่ที่ `HELLDIVERS_2_Thai_Validated.csv` และ output PUA อยู่ที่ `HELLDIVERS_2_Thai_PUA.csv`.

การ pack ใช้ `HELLDIVERS_2_packer.py` กับ raw `.strings.main` ของเกมเวอร์ชันเดียวกันและ text-only Russian patch template. Packer สร้าง patch ใหม่จาก current English resource IDs ไม่เขียน archive หลักหรือ template.

## 3. Font และ Thai shaping

ฟอนต์เกมเดิมไม่มี glyph ไทย. โครงการใช้ Google Sans static PUA ที่สร้าง derivative จาก source font และบรรจุเป็น runtime font. Google Sans PUA ช่วยรวมลำดับสระ/วรรณยุกต์ไทยเป็น glyph PUA สำหรับ renderer ที่ไม่ทำ Thai shaping โดยตรง.

Atlas production เป็น MSDF 1024×1024 จำนวน 1,024 slots, 11 mip levels. ใช้จริง 677 glyph. Tone marks U+0E48/U+0E49/U+0E4A/U+0E4B ถูกเลื่อนขึ้น +160 font units จาก source; nikhahit U+0E4D ใช้ตำแหน่ง source เดิม. Descriptor ทุก glyph ใช้ shared baseline เพื่อไม่ชดเชย vertical offset ซ้ำ.

ไฟล์ช่วยที่เกี่ยวข้อง: `03_Font_and_UI/Mapping.json`, `Char.txt`, `thai_font_mapper.py`, `HELLDIVERS_2_pua_csv_mapper.py`, `HELLDIVERS_2_thai_pua_tone_adjust.py` และ `HELLDIVERS_2_thai_atlas_poc.py`.

## 4. การป้องกัน tag และความปลอดภัยข้อความ

ห้ามแก้ `%s`, `%1$s`, `{0}`, `#VARIABLE`, `<tag>`, `\n`, `\r` และ subtitle timing cues รูปแบบ `{0.00->1.25}`. ใช้ `HELLDIVERS_2_translation_validator.py` เพื่อตรวจ schema, key ซ้ำ, source ที่ถูกแก้, translation ว่าง และ protected token/timing cue ที่ไม่ตรงกัน.

TRun output ต้องผ่าน `HELLDIVERS_2_translation_sanitizer.py` ก่อน pack หากพบ tag หรือ runtime variable ถูกแปลผิด. Sanitizer สร้าง CSV ใหม่ ไม่เขียนทับไฟล์จาก TRun.

## 5. การ pack และ deploy อัตโนมัติ

ลำดับที่ปลอดภัยคือ validate CSV → map PUA → pack text patch → build font/atlas patch → ตรวจ magic/TOC/payload bounds → backup target เดิม → copy เข้า `data` → เทียบ SHA-256.

ไฟล์ release มี 6 ไฟล์: `9ba626afa44a3aa3.patch_0`, `.patch_0.gpu_resources`, `.patch_0.stream`, `.patch_1`, `.patch_2` และ `.patch_3`. `patch_0` เป็น texture descriptor, GPU resources เป็น MSDF atlas, `patch_1` เป็น descriptor, `patch_2` เป็น runtime font และ `patch_3` เป็น string tables.

## 6. โครงสร้าง release และการติดตั้ง

Release v1.0 อยู่ที่ `06_Releases/HELLDIVERS 2_ThaiMod_v1.0/` และวางโฟลเดอร์ `data` ตรงกับ root เกม. ไม่มี loader หรือ DLL เพิ่มเติม. ผู้เล่นปิดเกมก่อน copy `data` ไปทับ game root แล้วลบไฟล์ patch ทั้ง 6 ไฟล์เพื่อถอนม็อด.

`คู่มือติดตั้ง_README.txt` และ `README_TH.txt` ระบุจำนวน 24,603 บรรทัดและข้อจำกัด live content.

## 7. ปัญหาที่พบและแนวทางแก้

อาการ `?` แทนภาษาไทยเกิดจาก glyph fallback ไม่ใช่ UTF-8 เสีย. แก้โดยใช้ Google Sans PUA runtime font และ MSDF atlas. อักษรทับ/สูงต่ำผิดเกิดจาก font unit ไม่ตรง, metric แบบ auto-frame และ tone mark position; แก้ด้วย static font ที่ scale ตาม UPM ของเกม, shared baseline และ shift tone marks.

ข้อความ Control Center / Galactic Campaigns บางส่วน เช่น Archive Data Entry, ชื่อ campaign, status และคำอธิบาย ถูกส่งเป็น live runtime payload. ไม่พบใน 265 local string resources, game data หรือ Arrowhead cache จึงไม่ควรพยายาม patch ผ่าน CSV. รักษาความปลอดภัยการเล่นออนไลน์โดยปล่อย live payload เป็นอังกฤษ.

## 8. เปรียบเทียบข้ามเกม/เอนจิน

ต่างจากเกมที่ใช้ JSON/XML/LOCRES ซึ่งแก้ข้อความแบบ loose file ได้, HELLDIVERS 2 ต้องรักษา Stingray package metadata, type table, resource IDs และ offsets ให้ถูกต้อง. คล้าย custom-engine localization ที่ต้องสร้าง bridge แยก unpack/pack มากกว่า plugin parser ทั่วไป.

ต่างจาก Unity/Unreal ที่มี fallback framework ชัดเจน, Noesis UI ของเกมนี้ต้องพึ่ง runtime font, MSDF descriptor และ atlas ที่ตรงกับ renderer. ดังนั้นการพิสูจน์ฟอนต์ไทยในเกมจริงเป็น gate ก่อน pack งานเต็มเสมอ.
