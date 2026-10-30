# XCOM Franchise Thai Modding Knowledge Transfer

เอกสารนี้รวบรวมองค์ความรู้จากการทำม็อดภาษาไทยของเกม XCOM: Enemy Unknown & Within เพื่อใช้เป็นฐานข้อมูลสำหรับ AI ในการทำม็อดเกมภาคต่อๆ ไป (เช่น XCOM 2 และ XCOM: Chimera Squad)

## 1. โครงสร้าง Engine และระบบ UI
- **Engine:** XCOM ภาคแรก (และ XCOM 2) ใช้ Unreal Engine 3 (หรือเวอร์ชั่นดัดแปลง) ร่วมกับระบบ UI ของ **Scaleform (Flash/ActionScript)**
- **Font System:** ฟอนต์ที่ใช้ในเกมจะถูกคอมไพล์อยู่ในไฟล์ .upk (Unreal Package) เช่น gfxfonts_ch_SF.upk หรือ XcomThaiFont.upk
- **ปัญหาภาษาไทยดั้งเดิม:** Scaleform ในเกมเก่าๆ มักจะจัดการสระลอยและวรรณยุกต์ภาษาไทย (สระบน/ล่าง) ไม่ถูกต้อง ทำให้สระทับซ้อนกันหรือลอยผิดตำแหน่ง

## 2. การแก้ปัญหาสระลอย (PUA Mapping)
เนื่องจากตัวเกมไม่รองรับสระลอยไทยตามมาตรฐาน (เช่น ไม้โทบนสระอิ) เราจึงต้องใช้เทคนิค **PUA (Private Use Area)**:
1. **Font Modification:** เรานำฟอนต์ไทยมาแก้ตารางตัวอักษร (Glyphs) โดยการแมปสระผสม (เช่น ฟ + ิ + ้) ไปไว้ในช่องว่างของตาราง Unicode (ช่วง PUA เช่น E000 เป็นต้นไป) แล้วสร้างเป็นไฟล์ .swf หรือ .upk ใหม่
2. **Text Modification:** เราต้องเขียนสคริปต์ Python เพื่อสแกนข้อความแปลไทยทั้งหมด และแปลงตัวอักษรไทยที่มีสระซ้อนทับกัน ให้กลายเป็นรหัส Unicode PUA เพื่อให้สอดคล้องกับฟอนต์ที่เราทำไว้
3. *บทเรียน:* ห้ามใช้สคริปต์ ActionScript ในการแปลง PUA แบบ Real-time ในเกม XCOM เพราะเกมมีข้อจำกัดในการรันสคริปต์ ทำให้ตัวหนังสือหาย การใช้ Python แปลงไฟล์ .int ล่วงหน้าเป็นวิธีที่เสถียรที่สุด

## 3. โครงสร้างไฟล์ภาษา (Localization)
- ไฟล์ภาษาใน Unreal Engine 3 คือไฟล์นามสกุล .int (สำหรับภาษาอังกฤษ)
- ตัวเกมมีระบบ Priority ในการโหลดไฟล์ .int ดังนี้:
  - **อันดับ 1 (สูงสุด):** โฟลเดอร์ Documents\My Games\XCOM...\XComGame\Localization\INT
  - **อันดับ 2:** โฟลเดอร์ Steam XComGame\Localization\INT
  - **อันดับ 3:** โฟลเดอร์ Steam Engine\Localization\INT
- *ข้อควรระวัง:* ต้องแยกไฟล์ระบบ (GFxUI.int, Engine.int) ไว้ในโฟลเดอร์ Engine และไฟล์เนื้อเรื่อง/ซับไตเติ้ล (Subtitles.int, XComGame.int) ไว้ใน XComGame ให้ถูกต้อง มิฉะนั้นเกมจะดึงไฟล์ผิดประเภทและแสดงผลเป็นภาษาดั้งเดิม

## 4. ปัญหาซับไตเติ้ลในคัตซีน (Subtitles)
- แม้จะแปลไฟล์ Subtitles.int แล้ว ซับคัตซีนก็ยังอาจกลายเป็นสี่เหลี่ยม (Tofu) เพราะเกมล็อกชื่อฟอนต์สำหรับซับไตเติ้ลไว้
- **วิธีแก้:** ต้องแก้ไขไฟล์ DefaultEngine.ini (ในโฟลเดอร์ Steam) และ XComEngine.ini (ในโฟลเดอร์ Documents) 
- ค้นหาคำว่า SubtitleFontName= และเปลี่ยนให้ชี้ไปยังฟอนต์ไทยของเรา (เช่น SubtitleFontName=XcomThaiFont.SubtitleThai)

## 5. การพัฒนา Tooling (Installer & Translator)
- **การแปล:** ใช้ Python + DeepSeek AI (ผ่าน API) ช่วยแปลไฟล์ .int ซึ่งสามารถแปลข้อความได้เป็นหมื่นบรรทัดในเวลาไม่นาน
- **การติดตั้ง:** ควรเขียนเป็นโปรแกรม .exe ด้วย Python (Tkinter + PyInstaller) เพื่อให้ตัวติดตั้งสามารถค้นหาที่อยู่เกมใน Registry (Steam) และ Copy ไฟล์ทั้งในโฟลเดอร์เกมและโฟลเดอร์ Documents ได้อัตโนมัติ เพื่อลดภาระของผู้ใช้ (เพราะระบบเกม XCOM ซับซ้อนเกินกว่าจะลงแบบ Manual ได้อย่างแม่นยำ 100%)


---
**จัดทำโดย:** [หน๊ด หนวด translator](https://www.facebook.com/NodNuatTranslator/)
