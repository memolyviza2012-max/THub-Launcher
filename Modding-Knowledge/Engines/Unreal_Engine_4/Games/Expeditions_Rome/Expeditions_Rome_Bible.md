# Expeditions: Rome (Unreal Engine 4.26) - Localization & Font Modding Bible

## 1. การแปลภาษา (Localization)
- **ไฟล์ภาษา:** ExpeditionsRome/Content/Localization/Game/en/Game.locres
- **เครื่องมือที่ใช้:** UnrealLocres (สำหรับ Export/Import ระหว่าง .locres และ .csv)
- **การตั้งค่าไฟล์:** การแปลสามารถนำไปใส่ในโฟลเดอร์ Mod ได้เลยโดยแพ็คเป็น pakchunk0_P-WindowsNoEditor.pak

## 2. ปัญหาฟอนต์ล่องหน (Invisible UI Bug)
**อาการ:** 
เมื่อทำการแทนที่ฟอนต์ RobotoRegular.ufont (ซึ่งเป็นฟอนต์มาตรฐานของ Engine) ด้วยฟอนต์ภาษาไทย เกมจะเกิดอาการ Crash ที่ระบบ FreeType ทำให้วิดเจ็ต UI ทั้งหมด (เช่น ปุ่มเมนูหลัก) หายไปจากหน้าจอ 100%

**สาเหตุที่แท้จริง:**
1. **ไม่ใช่การพังที่ Roboto:** ความจริงคือตัวเกม Expeditions: Rome **ไม่ได้ใช้ Roboto** ในการแสดงผลหน้า UI หลักเลย!
2. **แหล่งซ่อนฟอนต์:** ฟอนต์ที่ใช้จริงถูกเก็บไว้ในไฟล์แพ็คเกจเสริม pakchunk0_s8-WindowsNoEditor.pak
3. **ฟอนต์ที่ใช้จริง:** 
   - Cinzel (Regular, Bold)
   - EBGaramond (กว่า 10 สไตล์)
   - Noto (Regular, Medium, Bold, Light)
4. เมื่อเราแก้ไข Roboto ซึ่งเป็นฟอนต์แกนกลางของ Engine อย่างไม่สมบูรณ์ (เช่น มีปัญหาเรื่อง UPM หรือ Bounding Box) Engine จะพังตั้งแต่ตอนเริ่มต้น ส่งผลให้ UI ทั้งหมดค้างและไม่แสดงผล

## 3. วิธีการทำฟอนต์ภาษาไทยที่ถูกต้อง (The True Fix)
1. **ห้ามแตะต้อง Roboto:** ปล่อยไฟล์ Roboto ของ Engine ไว้ตามเดิม
2. **Extract ฟอนต์ตัวจริง:** แตกไฟล์จาก pakchunk0_s8 เพื่อนำ .ufont ของ Cinzel, EBGaramond และ Noto ออกมา
3. **Patch Internal Names:** 
   - ฟอนต์ต้นฉบับทั้ง 3 ตัวมีค่า UnitsPerEm (UPM) = 1000 ซึ่งตรงกับฟอนต์ **Kanit**
   - แทนที่จะใช้การ Merge เราใช้สคริปต์ Python (ontTools) นำฟอนต์ Kanit ไป **"สวมรอย"** โดยก็อปปี้ 
ame table (ID 1, 2, 3, 4, 6) จากฟอนต์ต้นฉบับไปทับใน Kanit
   - บันทึกไฟล์ทับ .ufont เดิม 
4. **แพ็คไฟล์:** นำ .ufont ทั้ง 17 ไฟล์ที่ถูกแพตช์แล้ว ไปแพ็คลงในโครงสร้างโฟลเดอร์เดิม (ExpeditionsRome/Content/Rome/UI/Fonts/) และสร้างเป็นแพทช์ .pak

ด้วยวิธีนี้ Engine จะโหลดฟอนต์ตามชื่อเดิมได้อย่างสมบูรณ์แบบโดยไม่เกิดการแครช และภาษาไทยจะแสดงผลได้ 100%!
