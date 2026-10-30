# Miasma Chronicles (Unreal Engine 5) - Thai Localization Bible

เอกสารฉบับนี้รวบรวมเทคนิคและวิธีการเจาะระบบแปลภาษาไทยสำหรับเกม Miasma Chronicles ซึ่งเป็นเกมที่ใช้ Unreal Engine 5 

## 1. การดึงข้อความ (Locres Extraction)
- **เครื่องมือที่ใช้:** `UnrealLocres.exe`
- **ปัญหาที่พบ:** เกมมีไฟล์เป้าหมาย 2 ไฟล์คือ `Miasma_GUI.locres` และ `Miasma_Dialogue.locres`
- **วิธีแก้ปัญหา:** เขียนสคริปต์ `miasma_unpacker.py` เพื่อดึงข้อความจากทั้ง 2 ไฟล์ออกมารวมใน CSV เดียว และใส่ Prefix (เช่น `Miasma_GUI||...`) ไว้ที่ช่อง ID เพื่อใช้ระบุเป้าหมายตอนแพ็คกลับ

## 2. ปัญหาข้อความล่องหน (Double Encoding & Missing Text)
- **อาการ:** เมื่อแปลงไฟล์ CSV เป็น `.locres` กลับเข้าเกม หน้าจอเมนูทุกอย่างว่างเปล่า ข้อความไม่แสดงผลเลยทั้งภาษาไทยและอังกฤษ
- **สาเหตุ:** การจัดการไฟล์ CSV ขาดการเข้ารหัสแบบ UTF-8 BOM ทำให้ไฟล์ `locres` ที่สร้างออกมามีโครงสร้างเสียหาย เกมจึงอ่านไม่พบชุดคำสั่ง (Empty String)
- **วิธีแก้:** ในโค้ด Python ที่สร้าง CSV สำหรับ `UnrealLocres` ต้องกำหนด `encoding='utf-8-sig'` (สำหรับเขียน) เพื่อให้มี BOM หรือใช้ `codecs.BOM_UTF8` นำหน้าเสมอเมื่อเขียนไฟล์ชั่วคราว (Temp CSV) สำหรับการ Import

## 3. ปัญหาตัวอักษรไทยเพี้ยน/ไม่ขึ้น (The Ultimate Font Spoofing)
- **อาการ:** เมื่อ `locres` ซ่อมเสร็จแล้ว ข้อความกลับมาแสดง แต่ภาษาไทยกลายเป็นอักษรเพี้ยนหรือล่องหน (Mojibake) เพราะฟอนต์ดั้งเดิมไม่รองรับ
- **สาเหตุ:** Miasma Chronicles ใช้ Asset แบบแยกส่วนประกอบ (Split System: `.uasset` + `.uexp` + `.ufont`) และไม่ได้ Fallback กลับไปหา Engine Font ในหลายๆ หน้า UI
- **วิธีแก้ (Total Font Override):** 
  คัดลอกฟอนต์ภาษาไทยที่เป็น `.ttf` (เช่น NotoSansThaiLooped) ไปสวมรอยทับไฟล์ฟอนต์ **ทุกสกุล** ในโครงสร้างเกม:
  - ทับไฟล์ `.ufont` ทุกไฟล์ใน `Miasma/Content/UI/FontsFaces/`
  - ทับไฟล์ `.ttf` และ `.otf` ทุกไฟล์ใน `Engine/Content/Slate/Fonts/`
  - ทำการแพ็คด้วย `repak.exe` เหมือนเดิม

## 4. การเปลี่ยนโลโก้หน้าจอเมนูหลัก (Video Logo Replacement)
- **อาการ/เป้าหมาย:** ต้องการเปลี่ยนโลโก้ "MIASMA CHRONICLES" ในหน้าจอหลัก
- **การค้นพบ:** โลโก้ไม่ใช่ไฟล์โมเดลหรือ UI Texture ธรรมดา แต่เป็น **ไฟล์วีดีโอดิบ (.mp4)** แบบพื้นหลังดำ ที่เกมสั่งเล่นวนลูปและใช้ Additive Blending ตัดสีดำทิ้ง 
- **วิธีทำ:**
  1. สร้างไฟล์วีดีโอใหม่ (ขนาด 1024x512, 30fps, ความยาว 20 วินาที, พื้นหลังสีดำ)
  2. ตั้งชื่อว่า `MIASMA_ALPHA_Menu_Logo_1024x512_20s_30fps_LOOP.mp4`
  3. นำไฟล์นี้ไปวางทับในโฟลเดอร์เกมตรงๆ ได้เลย ที่ `SteamLibrary\steamapps\common\Miasma\Miasma\Content\Movies\` โดยไม่ต้องผ่านการแพ็ค `.pak` ใดๆ

## 5. Signature Bypassing
- เกมมีการเช็ค Signature ของไฟล์ `.pak`
- ใช้ `UniversalSigBypasser.asi` คู่กับ `dsound.dll` วางไว้ที่ `Miasma/Binaries/Win64/` เสมอ เพื่อให้อ่านม็อดที่เราแพ็คเข้าไปได้

## การติดตั้งสำหรับผู้เล่น (Distribution)
จัดเตรียมโฟลเดอร์ `Miasma` ที่มีโครงสร้างตรงกับเกมเป๊ะๆ ประกอบด้วย:
1. ไฟล์คำแปล `.pak` ใน `Content\Paks\~mods\`
2. ไฟล์โลโก้ `.mp4` ใน `Content\Movies\`
3. ไฟล์ Bypass ใน `Binaries\Win64\`
แล้วให้ผู้เล่นก๊อปปี้ไปวางทับในโฟลเดอร์ตัวเกมได้ทันที
