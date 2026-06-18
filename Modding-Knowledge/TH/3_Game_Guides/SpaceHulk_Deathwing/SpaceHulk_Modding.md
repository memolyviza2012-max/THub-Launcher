# 🇹🇭 Space Hulk: Deathwing - Thai Localization Mod Workflow & Techniques

Repository สำหรับเก็บรวบรวมเทคนิค, เครื่องมือ, และโค้ดสำหรับสร้าง Mod ภาษาไทยให้กับเกม **Space Hulk: Deathwing - Enhanced Edition** (Unreal Engine 4.14.3)

## 📌 เทคนิคที่ค้นพบ (Knowledge Items - KI)

### 1. เทคนิค Font Fallback (ไม่ต้อง Cook ฟอนต์ .uasset)
เกมที่พัฒนาด้วย Unreal Engine 4 มีระบบ Slate UI ซึ่งรองรับระบบ Font Fallback โดยธรรมชาติ หากระบบค้นหาตัวอักษรภาษาไทยในฟอนต์หลักของเกมไม่พบ มันจะวิ่งไปหาฟอนต์สำรองที่ถูกตั้งค่าไว้ที่ `Engine\Content\Slate\Fonts\DroidSansFallback.ttf`
- **วิธีการ:** นำไฟล์ฟอนต์ภาษาไทยนามสกุล `.ttf` ทั่วไป มาเปลี่ยนชื่อเป็น `DroidSansFallback.ttf` แล้วแพ็คใส่ไปใน Mod ตามโครงสร้างด้านบน
- **ผลลัพธ์:** เกมสามารถแสดงผลภาษาไทยได้ทันที โดยไม่ต้องโหลด Unreal Engine มาทำการ Cook ไฟล์ฟอนต์ประเภทรุ่นเก่า (Composite Font `.uasset`) ให้ยุ่งยาก และลดความเสี่ยงที่เกมจะ Crash จากเอนจิ้นคนละเวอร์ชัน

### 2. การแก้บั๊กใน Pylocres (Integer Hash Bug)
เมื่อทำการนำเข้าไฟล์ `CSV` กลับไปเป็น `.locres` ผ่านคำสั่ง `pylocres from-csv` มักจะเจอข้อผิดพลาด `struct.error: required argument is not an integer` 
- **สาเหตุ:** เกิดจากช่อง `hash` ในไฟล์ CSV ถูกอ่านขึ้นมาเป็นข้อมูลประเภท String (ตัวอักษร) แต่คำสั่งแพ็คเข้ารหัสของโครงสร้าง C++ ต้องการข้อมูลประเภท Integer
- **วิธีแก้:** ต้องทำการแก้ไขโค้ดในตัวไลบรารีของ pylocres โดยตรง (ไฟล์ `cli.py`) ในบรรทัดที่มีการดึงค่า `source_hash` ให้บังคับแปลงเป็น Integer ทันที:
  ```python
  # โค้ดที่ผ่านการแก้บั๊กแล้ว
  source_hash = int(row.get("hash", 0)) if row.get("hash") else 0
  ```

### 3. ระบบแปลภาษาด้วย AI (DeepSeek) & Glossary Injection
ด้วยความที่ซีรีส์ Warhammer 40,000 มีคำศัพท์เฉพาะที่ซับซ้อนมาก เราจึงสร้างสคริปต์ `run_translation_SHDW.py` ที่ทำงานร่วมกับ DeepSeek API โดยมีฟีเจอร์เด่นคือ:
- **Glossary Injection:** มีการฝังพจนานุกรมคำศัพท์เฉพาะเข้าไปใน System Prompt อย่างเข้มงวด (เช่น Space Marine = สเปซมารีน, Heretic = พวกนอกรีต, Genestealer = จีนสตีลเลอร์)
- **Tag Masking:** ป้องกัน AI ทำโค้ดพังโดยการแทนที่โค้ด `<span color="...">` หรือตัวแปรสูตรต่างๆ ด้วย Tag พิเศษ (เช่น `[TAG_0]`) ก่อนส่งให้ AI แปล แล้วค่อยสลับกลับมาคืนเมื่อแปลเสร็จ
- **Checkpoint System:** แปลงไฟล์ทีละแถว และทำการเซฟลง CSV ทันที ป้องกันปัญหาไฟดับ หรือ API ล่มกลางคัน

## 📂 โครงสร้างของ Workspace

- `/Extracted/` - โฟลเดอร์ที่เก็บไฟล์เกมดั้งเดิมที่ถูกแตกออกมา (ต้นฉบับ)
- `/Pack/` - โฟลเดอร์ที่จำลองโครงสร้างเกม เอาไว้เตรียมนำไปแพ็คเป็น .pak
- `/Translation/` - โฟลเดอร์สำหรับเก็บไฟล์ CSV ที่ Export ออกมา และไฟล์แปลไทย
- `/Tools/` - โฟลเดอร์เก็บโปรแกรมช่วยเหลือ เช่น `repak.exe`
- `1_export_csv.bat` - สคริปต์ดูดข้อความภาษาอังกฤษออกมาเป็น CSV
- `2_import_csv.bat` - สคริปต์ประกอบข้อความภาษาไทยกลับเข้าไปในรูปแบบ .locres
- `3_pack_mod.bat` - สคริปต์แพ็คไฟล์เป็น Mod ท้ายสุด
- `run_translation_SHDW.py` - สคริปต์ AI แปลภาษา

## 🚀 วิธีการใช้งาน

1. รัน `1_export_csv.bat` เพื่อดูดข้อความออกมา
2. รัน `run_translation_SHDW.py` เพื่อสั่ง AI แปลภาษาให้เป็นไทย (หรือแปลเองผ่าน Excel)
3. เมื่อแน่ใจว่าภาษาไทยถูกต้องครบถ้วน ให้รันสคริปต์ Python หรือ Batch ตัวแก้บั๊กเพื่ออิมพอร์ต CSV กลับเข้า Locres
4. รันคำสั่ง `repak pack Pack SpaceHulkGame-WindowsNoEditor_TH.pak -v 4.14` (หรือผ่านสคริปต์)
5. นำไฟล์ `.pak` ที่ได้ไปวางคู่กับไฟล์เกมดั้งเดิมในโฟลเดอร์ Paks ได้เลย!

---
*Created and optimized for Thai Modding Community by Antigravity (AI Modding Assistant).*


---
**จัดทำโดย:** [หน๊ด หนวด translator](https://www.facebook.com/NodNuatTranslator/)
