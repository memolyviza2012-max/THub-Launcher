# ขั้นตอนการทำม็อดภาษาไทย XCOM: Enemy Unknown & Within โดยละเอียด

เอกสารนี้สรุปขั้นตอนตั้งแต่เริ่มต้นจนจบในการดึงเนื้อหา, แปลภาษา, แก้ไขฟอนต์, และสร้างตัวติดตั้งสำหรับเกม XCOM (Unreal Engine 3 + Scaleform)

## 1. การเตรียมเครื่องมือ (Tools Preparation)
- **JPEXS Free Flash Decompiler (FFDec):** ใช้สำหรับเปิดและแก้ไขไฟล์ .gfx และ .swf (ดึงฟอนต์ UI จากไฟล์ gfxfonts_ch_SF.upk)
- **UDK (Unreal Development Kit):** ใช้สำหรับบิ้วด์ฟอนต์คัตซีน (สร้างไฟล์ .upk) 
- **Python 3:** ใช้สำหรับเขียนสคริปต์สกัดข้อความ, แปลภาษา, แปลงสระ PUA, และสร้างตัวติดตั้ง

## 2. การดึงและแก้ไขฟอนต์ UI (Scaleform)
ไฟล์ฟอนต์ UI หลักของเกมคือ XComGame/CookedPCConsole/gfxfonts_ch_SF.upk
1. ใช้สคริปต์ Python (inject_swf.py) ดึงไฟล์ gfxfonts_ch_SF.swf ออกมาจาก .upk
2. เปิดไฟล์ .swf ด้วย JPEXS
3. นำฟอนต์ภาษาไทย (เช่น DB Helvethaica) ที่ถูกแก้ไขตาราง PUA (เลื่อนสระลอยไปไว้ในช่องว่าง Unicode) มา Replace ทับฟอนต์เดิม (เช่น Alpha Mack, FPF)
4. ฝังตัวอักษรไทยทั้งหมดลงไปในฟอนต์ (Embed Characters)
5. เซฟไฟล์ .swf แล้วใช้สคริปต์ Python คืนค่าไฟล์ .swf กลับเข้าไปใน .upk

## 3. การสร้างฟอนต์สำหรับ Subtitle (คัตซีน)
ซับไตเติ้ลในคัตซีนใช้ฟอนต์จาก Unreal Engine ไม่ใช่ Scaleform
1. เปิด UDK สร้าง Texture จากฟอนต์ไทย PUA (ใช้ระบบ Font Creation ของ UDK)
2. สร้างไฟล์ Package ใหม่ชื่อ XcomThaiFont.upk และตั้งชื่อฟอนต์ข้างในเป็น SubtitleThai
3. บันทึกและนำไปวางในโฟลเดอร์ CookedPCConsole ของตัวเกม

## 4. การดึงข้อความและแปลภาษา (Localization)
ไฟล์ข้อความทั้งหมดจะอยู่ใน XComGame/Localization/INT นามสกุล .int
1. เขียนสคริปต์สแกนหาไฟล์ .int ทั้งหมด แล้วดึงข้อความภาษาอังกฤษออกมาจัดเก็บในรูป CSV
2. **การแปล:** ส่งข้อความไปแปลผ่าน DeepSeek API โดยต้องกำชับ AI ให้รักษาโครงสร้างโค้ดและตัวแปรไว้เสมอ (เช่น %s, \n, <font>)
3. **การแปลง PUA:** เมื่อแปลเสร็จ โค้ด Python ต้องนำข้อความมารันผ่านฟังก์ชัน pply_pua_mapping ทันที เพื่อแปลงสระและวรรณยุกต์ซ้อนทับ ให้กลายเป็นรหัส PUA เพื่อให้แสดงผลกับฟอนต์ที่เราทำไว้ในข้อ 2 ได้พอดี

## 5. การบังคับใช้ฟอนต์คัตซีน (Engine.ini)
แม้จะมีไฟล์แปลแล้ว แต่เกมจะยังดึงฟอนต์ดั้งเดิมมาใช้ในคัตซีน
- ต้องแก้ไฟล์ DefaultEngine.ini (ในโฟลเดอร์ Steam) และ XComEngine.ini (ใน Documents)
- เปลี่ยนค่าบรรทัด: SubtitleFontName=XcomThaiFont.SubtitleThai

## 6. การสร้างตัวติดตั้งแบบ One-Click (Installer)
เกม XCOM มีพฤติกรรมที่ซับซ้อนคือ มันจะโหลดไฟล์ภาษาจากโฟลเดอร์ Documents/My Games/XCOM... ก่อนโหลดจากโฟลเดอร์เกมใน Steam
- เขียนสคริปต์ installer_gui.py ให้โปรแกรมค้นหาที่อยู่เกมอัตโนมัติจาก Registry ของ Steam
- ค้นหาที่อยู่โฟลเดอร์ Documents อัตโนมัติ
- คัดลอกไฟล์ .int ที่แปลแล้ว และไฟล์ฟอนต์ ไปวางทับทั้งในโฟลเดอร์ Steam และโฟลเดอร์ Documents 
- เขียนคำสั่งใน Python ให้มันเจาะเข้าไปแก้ไขค่า SubtitleFontName= ในไฟล์ .ini ทั้งสองแห่งโดยอัตโนมัติ
- ใช้ PyInstaller แพ็คเกจไฟล์ทั้งหมดและซอร์สโค้ด ให้กลายเป็นไฟล์ .exe ตัวเดียวจบ


---
**จัดทำโดย:** [หน๊ด หนวด translator](https://www.facebook.com/NodNuatTranslator/)
