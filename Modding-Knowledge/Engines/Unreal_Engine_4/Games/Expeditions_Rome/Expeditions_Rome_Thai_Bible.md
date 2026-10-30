# Expeditions: Rome - Thai Localization Bible

## 1. ข้อมูลทั่วไปของเกม
- **Engine:** Unreal Engine 4 (เวอร์ชันดัดแปลงเฉพาะ)
- **ระบบแปลภาษา:** โครงสร้างมาตรฐานแบบ .locres ของ Unreal Engine
- **ตำแหน่งไฟล์ภาษา:** ExpeditionsRome\Content\Localization\Game\en และ Dialogue\en
- **เครื่องมือที่ใช้สกัดข้อความ:** UnrealLocres.exe (แปลง .locres เป็น .csv และกลับกัน)

## 2. ปัญหา "ฟอนต์ล่องหน" (Invisible Font) และการวิเคราะห์ Root Cause
ปัญหาสุดคลาสสิกและปราบเซียนของเกมนี้คือ เมื่อพยายามใส่ภาษาไทยเข้าไป แม้จะทำไฟล์ภาษาถูกต้อง แต่ตัวอักษร UI กลับหายไปทั้งแถบ (จอล่องหน) หรือบางครั้งเกม Crash ทันที
จากการทำ Reverse Engineering เชิงลึก พบความลับ 2 ข้อดังนี้:

### ความลับที่ 1: การหลอกลวงของระบบฟอนต์
- เกมมีโฟลเดอร์ฟอนต์ Content\Rome\UI\Fonts และประกาศใช้ Roboto แต่แท้จริงแล้วเกมไม่ได้ใช้ Roboto เรนเดอร์ UI เลย!
- ข้อมูลฟอนต์ที่แท้จริงถูกซ่อนอยู่ภายใต้ไฟล์ pakchunk0_s8-WindowsNoEditor.pak
- เกมใช้ฟอนต์ 3 ตระกูลหลักในการทำงาน:
  1. **Cinzel** (ใช้สำหรับหัวข้อ / UI หลัก)
  2. **EBGaramond** (ใช้สำหรับเนื้อความ / Dialogue)
  3. **NotoSans** (ฟอนต์ระบบทั่วไป)

### ความลับที่ 2: FreeType Renderer Crash เพราะค่า UPM (Units per Em)
- ฟอนต์ต้นฉบับของเกม (เช่น EBGaramond) ถูกสร้างด้วยค่า **UPM = 1000**
- ส่วนฟอนต์ไทยยอดนิยมส่วนใหญ่ถูกสร้างด้วยค่า **UPM = 2048** (เช่น Kanit, NotoSansThai)
- เมื่อเราพยายามนำฟอนต์ที่มี UPM = 2048 ไปสวมรอยทับฟอนต์ที่มี UPM = 1000 (โดยการแก้ Internal Name) Engine จะคำนวณ Bounding Box ของตัวอักษรผิดพลาด (พองขึ้น 2 เท่า)
- ส่งผลให้ระบบเรนเดอร์ข้อความของ UE4 (FreeType) เกิดการ Overrun/Crash นำไปสู่อาการ **UI หาย (ล่องหน)** หรือเกมปิดตัว

## 3. วิธีแก้ปัญหา (The UPM 1000 Patching Technique)
เพื่อแก้ปัญหานี้ เราต้องหาฟอนต์ภาษาไทยที่มีโครงสร้าง **UPM = 1000** เท่ากับต้นฉบับเป๊ะๆ เพื่อให้ Engine คำนวณ Bounding Box ได้ถูกต้อง
1. **การเลือกฟอนต์:** เราเลือกใช้ฟอนต์ **Pridi (ปรีดี)** จาก Google Fonts เนื่องจากมีโครงสร้าง UPM = 1000 โดยธรรมชาติ
2. **การ Mapping สระลอย (PUA):** รันสคริปต์ 	hai_pua_mapper.py เพื่อแก้ไขตำแหน่งสระ วรรณยุกต์ ไม่ให้ซ้อนทับกัน
3. **การสวมรอย (Spoofing Internal Name):** นำฟอนต์ Pridi มาเปิดในโปรแกรม FontForge แล้วแก้ไขรหัสภายใน (Internal Name & Family Name) ให้ปลอมตัวเป็นฟอนต์เป้าหมายทั้ง 17 ไฟล์ ได้แก่:
   - Cinzel-Bold.ttf, Cinzel-Medium.ttf, Cinzel-Regular.ttf, CinzelDecorative-Bold.ttf, CinzelDecorative-Regular.ttf
   - EBGaramond-Bold.ttf, EBGaramond-BoldItalic.ttf, EBGaramond-Italic.ttf, EBGaramond-Medium.ttf, EBGaramond-Regular.ttf, EBGaramond-SemiBold.ttf
   - NotoSans-Bold.ttf, NotoSans-BoldItalic.ttf, NotoSans-Italic.ttf, NotoSans-Light.ttf, NotoSans-Regular.ttf, NotoSans-SemiBold.ttf
4. แปลงไฟล์กลับเป็นนามสกุล .ufont หรือ .ttf ตามต้นฉบับ แล้วโยนเข้าโฟลเดอร์ ExpeditionsRome\Content\Rome\UI\Fonts

เมื่อสร้าง Mod ออกมา อาการจอล่องหนจะหายไปทันที และภาษาไทยจะแสดงผลได้อย่างงดงามสมบูรณ์แบบ!
