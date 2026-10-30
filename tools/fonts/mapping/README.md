# Thai Font Mapping Kit

ชุดนี้แปลงข้อความ UTF-8 ไทยเป็น glyph ใน Private Use Area (PUA) สำหรับฟอนต์ของเกม โดยใช้ `Mapping.json` เป็นข้อมูลหลักและ `Char.txt` เป็นรายการ glyph ที่ต้องมีในฟอนต์

## กติกาที่ต้องรักษา

- Encoding ของทุกไฟล์คือ UTF-8
- จับคู่ข้อความจาก key ที่ยาวที่สุดก่อนเสมอ เช่น `กั่` ต้องถูกแทนก่อน `กั`
- Normalize เป็น NFC และแปลง `U+0E4D U+0E32` (ํา) เป็น `U+0E33` (ำ) ก่อน mapping
- PUA ที่ mapping ใช้คือ `U+F000` ถึง `U+F89F`; ฟอนต์เกมต้องมี glyph ครบทุกตัว

`Char.txt` ฉบับนี้เพิ่ม space (`U+0020`) แล้ว เพื่อให้ font tool สร้าง metrics ของช่องว่างได้หากรองรับ

## ใช้งานกับไฟล์ข้อความ

```powershell
python .\thai_font_mapper.py .\input.txt -o .\output.txt --audit
```

หรือรับข้อความจาก standard input:

```powershell
$OutputEncoding = [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
'ผู้ใช้ 100%: น้ำ' | python .\thai_font_mapper.py --audit > output.txt
```

`output.txt` เป็นข้อความที่มี PUA แล้ว จึงต้องเปิดด้วยฟอนต์เกมที่สร้างจาก `Char.txt` เท่านั้น ไม่ควรส่งให้ผู้แปลแก้ไขโดยตรง

## ให้ AI ใช้งานอย่างปลอดภัย

ส่ง `mapping_manifest.json`, `Mapping.json` และกติกานี้ให้ AI พร้อมคำสั่ง:

> เก็บข้อความต้นฉบับเป็น UTF-8, normalize NFC, แปลง ํา เป็น ำ, และแทนที่ตาม Mapping.json แบบ longest-match-first เท่านั้น ห้ามแก้ไข tag, placeholder (`{0}`, `%s`), key หรือ escape sequence. ให้คืนผลเป็น UTF-8

แนะนำให้ AI แปลเป็น “ข้อความไทยปกติ” ก่อน แล้วให้ `thai_font_mapper.py` เป็นขั้นตอนสุดท้ายในการแปลงเป็น PUA เพราะ AI อาจตีความ PUA เป็นอักขระแปลกและแก้ไขโดยไม่ตั้งใจ

## ตรวจชุดไฟล์และ regression test

```powershell
python .\validate_mapping.py
```

ผลที่ควรได้คือ `OK: 2208 mappings, 6 regression cases, all outputs in Char.txt`

## ข้อจำกัด

mapping นี้จัดการพยัญชนะตามด้วยสระ/วรรณยุกต์ที่กำหนดไว้ 2,208 รูป ไม่ได้แทนที่สระนำ (`เ แ โ ใ ไ`) หรือพยัญชนะเดี่ยว เพราะฟอนต์มี glyph ปกติสำหรับตัวเหล่านั้นอยู่แล้ว หาก audit รายงาน combining mark ที่เหลือ ต้องเพิ่มรูปนั้นใน mapping และสร้าง glyph PUA ที่สัมพันธ์กันในฟอนต์ก่อนใช้งานจริง
