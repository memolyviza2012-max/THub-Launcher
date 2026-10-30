# คัมภีร์สร้าง Mod ภาษาไทย — Phantaruk

เอกสารนี้บันทึกกระบวนการที่ใช้สร้างม็อดภาษาไทยสำหรับ **Phantaruk** บน Steam/Windows และผลที่ผ่านการทดสอบในเกมจริง

## 1. ข้อมูลสรุปและโครงสร้าง Engine

- Runtime: Unity Mono 5.3.4f1
- รูปแบบข้อมูล: Unity serialized assets (`*.assets`) และ streamed data (`*.resS`, `*.resource`)
- ไฟล์ข้อความที่แก้: `Data\Phantaruk_Data\sharedassets0.assets` และ `resources.assets`
- TextAsset เป็น XML UTF-8 ไม่มี BOM และมี node ภาษาอังกฤษใต้ `/Language/EN`
- ไม่พบว่าข้อความใน asset เป้าหมายถูกบีบอัดหรือเข้ารหัส AES; ห้ามแก้ `.resS` และ `.resource` เพราะเป็น texture/mesh/audio stream ไม่ใช่ข้อความ

## 2. วิธีสกัดข้อความและแปลงกลับ

ใช้ AssetsTools.NET ที่มากับ UABEA ผ่าน bridge ของโปรเจกต์:

```text
05_Scripts_and_Tools\Phantaruk_unpacker.py
05_Scripts_and_Tools\Phantaruk_packer.py
05_Scripts_and_Tools\Phantaruk_assets_bridge.ps1
```

`unpacker` อ่าน Unity TextAsset, parse XML และสร้าง CSV มาตรฐาน TStudio:

```text
key,source,translation,context,file_path
```

key มีรูปแบบ `asset-file::TextAsset-name::XML-XPath` เช่น:

```text
sharedassets0.assets::Menus::/Language[1]/EN[1]/Text[1]/Content[1]
```

`packer` แก้เฉพาะ node EN ที่มีคำแปล แล้ว rewrite serialized asset ด้วย AssetsTools.NET. Release full build แปลได้ 913 แถวจาก TextAsset 6 รายการใน `sharedassets0.assets` และ 2 รายการใน `resources.assets`.

## 3. ระบบฟอนต์และสระ/วรรณยุกต์

เกมใช้ legacy `UnityEngine.UI.Text` ไม่ใช่ TextMeshPro. Font assets ที่พบประกอบด้วย Lato, GetVoIP Grotesque และ dynamic `Arial`; Lato ไม่มี Thai glyph จึงเกมแสดงอักษรไทยผ่าน Windows font fallback.

POC และ full build แสดงภาษาไทยในเกมได้โดยไม่เกิด tofu และผ่านการทดสอบวรรณยุกต์. ดังนั้น release v1.0 **ไม่ใช้** Prompt PUA, TMP font atlas หรือการขยับ glyph `่ ้ ๊ ๋` +160 units เพราะ metric ดังกล่าวไม่มีผลต่อ glyph ที่ Windows fallback วาดให้.

หาก Windows build อื่นให้รูปแบบต่างจากเครื่องทดสอบ ให้ใช้ Unity legacy Font replacement หรือ runtime hook เป็นงานรุ่นถัดไป ไม่ควรฝืนใช้ pipeline TMP กับเกมนี้.

## 4. ความปลอดภัยของข้อความและแท็ก

Validator คือ `05_Scripts_and_Tools\Phantaruk_translation_validator.py` และต้องใช้ก่อน pack:

```powershell
python Phantaruk_translation_validator.py <translated.csv> --baseline <master.csv> --require-complete
```

ตรวจ schema, key ซ้ำ, คำแปลว่าง และ protected token multiset: `<tag>`, `%s`, `%1$s`, `{0}`, `\n`, `\r`.

Bridge ยังตรวจ key, XPath, asset name และ source content. การอ่าน CSV สามารถ normalize CRLF และ outer whitespace ที่ XML serializer เปลี่ยนได้ แต่ข้อความภายในต้องตรงกับต้นฉบับก่อนเขียนคำแปล.

## 5. ขั้นตอน pack อัตโนมัติ

1. เก็บ CSV reviewed ไว้ใน `02_Translation_Workspace`.
2. รัน validator ด้วย `--require-complete`.
3. ใช้ backup ดั้งเดิมของ `sharedassets0.assets` และ copy ของ `resources.assets` เป็นต้นทาง build.
4. รัน packer ไปยัง `04_Packed_Mod\Phantaruk_Thai_Full\Data\Phantaruk_Data`.
5. extract-back ทั้งสอง asset และเทียบกับคอลัมน์ `translation`; ผล v1.0 คือ 913/913 ตรงกัน.
6. ปิดเกม, ทำ backup write-once, บันทึก checkpoint และ verify SHA256 ก่อน deploy.

## 6. โครงสร้าง Release และคู่มือติดตั้ง

```text
Phantaruk_ThaiMod_v1.0\
├─ Data\Phantaruk_Data\sharedassets0.assets
├─ Data\Phantaruk_Data\resources.assets
├─ คู่มือติดตั้ง_README.txt
├─ README_TH.txt
└─ SHA256SUMS.txt
```

ผู้เล่นปิดเกมแล้ว copy โฟลเดอร์ `Data` ไปทับ root ของเกม. เพราะ asset เดิมถูกแทนที่ การถอนม็อดใช้ Steam Verify integrity of game files หรือคืน backup; ห้ามลบ `.assets` โดยตรง.

## 7. อุปสรรคและแนวทางแก้ไข

- AssetStudio ใช้ตรวจและ dump ได้ แต่ไม่ใช่ writer ที่ปลอดภัยสำหรับ release; ใช้ AssetsTools.NET rebuild แทน.
- CSV extract รุ่นแรกมี `file_path` ว่าง แม้ key มีชื่อ asset ถูกต้อง; bridge รุ่น release จึง derive asset จาก key และ reject metadata ที่ขัดกัน.
- CSV reader ทำให้ CRLF ใน quoted field กลายเป็น LF และ extractor ตัด outer whitespace บาง node; bridge normalize เฉพาะความต่าง serialization ก่อน strict content comparison.
- การส่งไฟล์ `.assets` เดี่ยวให้ PowerShell bridge มีข้อจำกัดกับ `resources.assets`; full build จึงใช้ staging directory ที่มีสอง asset.
- Windows fallback ทำให้ Thai render ได้ แต่ไม่รับประกันว่า font face จะเหมือนกันทุกเครื่อง.

## 8. เปรียบเทียบกับเกม/เอนจินอื่น

ต่างจาก Unity ที่ใช้ TextMeshPro, Phantaruk ไม่มี TMP Font Asset Creator pipeline และไม่เหมาะกับ PUA mapping ที่ออกแบบเพื่อแก้ Thai shaping ใน TMP. ต่างจากเกม Unity ที่ข้อความอยู่ใน JSON/StreamingAssets, เกมนี้เก็บ XML ใน Unity serialized TextAsset จึงต้อง preserve object layout และใช้ serializer ที่เข้าใจ asset format.

ผลที่นำไปใช้ต่อได้คือ: แยก “การแก้ข้อความใน asset” ออกจาก “การจัด glyph”; พิสูจน์ render ในเกมก่อนแปลเต็มชุด; และตรวจ extract-back ก่อนสร้าง release ทุกครั้ง.
