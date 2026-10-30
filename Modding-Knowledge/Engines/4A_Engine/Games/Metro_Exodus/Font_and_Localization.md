# Metro Exodus: Font & Localization Architecture

## สถาปัตยกรรม 4A Engine

1. **Virtual File System (.vfs0, .vfx):**
   เกมใช้ระบบ Archive แบบ VFS ไฟล์เกือบทั้งหมดจะถูกแพ็คอยู่ใน `content.vfx` (ไฟล์ดัชนี) และ `content.vfs0` (ไฟล์ข้อมูล)

2. **Font Architecture (LZ4 + BC7):**
   * ต่างจากเกมอื่นๆ (เช่น C-Engine หรือ RE Engine) ที่มักแยกไฟล์ภาพ (Texture) กับไฟล์พิกัด (Metrics) ออกจากกันอย่างชัดเจน
   * 4A Engine เก็บข้อมูลฟอนต์อยู่ในรูปของ `.2048` (หรือขนาดอื่นๆ เช่น `.512`) 
   * โครงสร้างของ `.2048` คือภาพฟอนต์แบบบีบอัด **BC7** ที่ถูกเข้ารหัสทับด้วย **LZ4 block compression** 
   * **Font Metrics (UV Data):** ข้อมูลความกว้างความสูงของแต่ละตัวอักษร ไม่ได้แยกเป็นไฟล์อิสระ แต่ถูกแพ็คเข้ารหัสฝังลึกลงไปพร้อมกับโครงสร้าง VFS ในกระบวนการ Build ของ Engine การแก้ไขภาพด้วยวิธี OCR และเขียนทับ (Glyph Squatting) จึงทำได้ยากมากเพราะไม่สามารถแก้ไข Font Metrics แบบแมนนวลได้ง่ายๆ

3. **Localization Strings (.lng):**
   * ข้อความถูกเก็บอยู่ในโครงสร้าง `.lng` 
   * การแก้ไขโดยตรงเป็นไปได้ยากเพราะมี String ID mapping และ Offset เฉพาะ

## วิธีการ Mod ภาษาที่แนะนำ (Official SDK + RPA)

วิธีที่เสถียรที่สุดในการทำ Localization สำหรับ Metro Exodus คือการพึ่งพา **Official Exodus SDK (บน Steam)** เนื่องจาก SDK มีเครื่องมือสำหรับ Import/Export และการคำนวณ Font Metrics อย่างสมบูรณ์

**ข้อจำกัดของ SDK:**
* UI มีความซับซ้อน ผู้ใช้อาจใช้งานได้ยาก

**แนวทางการบูรณาการกับ TStudio (Modder Hub):**
* **Unpacker**: สกัดข้อความที่ Export จาก SDK ให้อยู่ในรูป TStudio CSV (id, original, translation)
* **Packer**: แปลงจาก TStudio CSV โดยมีขั้นตอนคือ:
  1. **PUA Mapping**: อ้างอิงตารางแปลงอักษรไทยเป็น PUA (เช่น `กั` -> ``) เพื่อแก้ปัญหาสระลอย
  2. **SDK CSV Generation**: สร้าง CSV ในรูปแบบที่ Exodus SDK รองรับ
  3. **UI Automation (RPA)**: ใช้ Python (เช่น `pywinauto`) ทำการเปิดโปรแกรม `Exodus_SDK.exe` ขยับเมาส์ไปกดเมนู `Localization Manager` -> `Import CSV` -> `Generate Fonts` แบบอัตโนมัติ เพื่อซ่อนความซับซ้อนของเครื่องมือ
