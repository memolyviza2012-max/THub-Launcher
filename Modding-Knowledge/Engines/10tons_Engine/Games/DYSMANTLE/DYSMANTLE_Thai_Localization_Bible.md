# DYSMANTLE (10tons Engine) - Thai Localization Bible

## 1. ข้อมูลทั่วไปของเกม
- **Engine:** Custom 10tons Engine
- **Font Format:** Proprietary `.mft` (MSDF - Multi-channel Signed Distance Field Bitmap)
- **Archive Format:** Custom `.pak` (ZIP-based compression with specific alignment)
- **Localization Files:** XML files (e.g., `language.xml`)

## 2. อุปสรรคทางเทคนิค (Reverse Engineering Log)
ในตอนแรกเราพยายามแก้ไขไฟล์ `.pak` และยัดฟอนต์ `.ttf` ลงไปแทนที่ `.mft` (Option C) แต่พบว่าเอนจินเกมไม่รองรับ TTF แบบเนทีฟเลย ส่งผลให้เกมเรนเดอร์ตัวอักษรเป็นกล่องสี่เหลี่ยมว่างเปล่า 
จากนั้นเราได้พยายามทำ Memory Hooking (Option B) แต่เนื่องจากข้อจำกัดด้าน Compiler บนเครื่อง ทำให้ต้องหาวิธีอื่น
จนกระทั่งเราค้นพบ **Jackpot**: ทางผู้พัฒนาได้แอบใส่ **Official Localization Kit** มาให้ในตัวเกมเลย!

## 3. ขั้นตอนการทำ Mod ภาษาไทย (Official Pipeline)
ด้วย Official Modding Kit เราสามารถ "อบ (Bake)" ฟอนต์ MSDF ออกมาได้อย่างสมบูรณ์ 100% โดยมีขั้นตอนดังนี้:

### 3.1 การเตรียมชุดเครื่องมือ (Localization Kit)
1. เข้าไปที่โฟลเดอร์เกม: `F:\SteamLibrary\steamapps\common\DYSMANTLE\modding_kit\localization_kit`
2. เข้าไปที่ `data-localizations\localizations\` และ `data-localizations-src\localizations\` ทำการก๊อปปี้โฟลเดอร์ `mylang` แล้วเปลี่ยนชื่อเป็น `th`
3. นำฟอนต์ภาษาไทย (เช่น `Tahoma.ttf`) ไปวางไว้ที่:
   `data-localizations-src\localizations\th\fonts\`

### 3.2 การปรับแต่งไฟล์ XML สำหรับสร้างฟอนต์
แก้ไขไฟล์ `small.mft.xml` และ `medium.mft.xml` ในโฟลเดอร์ `th\fonts\`
```xml
<node id="INPUT" 
     ttf="Tahoma.ttf" size_px="20" 
     strings="../../../../data-localizations/localizations/th/language.xml"
     ttf_fallback="Tahoma.ttf" />
```
*จุดสำคัญ: เครื่องมือจะอ่าน `language.xml` ของเราเพื่อหาว่ามีการใช้ "สระ/วรรณยุกต์/พยัญชนะ" ตัวไหนบ้าง และจะ Bake เฉพาะตัวที่มีการใช้งานลงไปใน Texture!*

### 3.3 การอบฟอนต์ (Baking)
1. นำไฟล์ `language.xml` ที่แปลภาษาไทยเสร็จแล้ว ไปวางไว้ที่:
   `data-localizations\localizations\th\language.xml`
2. รันสคริปต์ `create-fonts-for-language.bat th` ผ่าน Command Prompt
3. โปรแกรม `nx-rescaler.exe` จะทำงาน และสร้างไฟล์ `small.mft` และ `medium.mft` ที่สมบูรณ์แบบออกมาให้ในโฟลเดอร์ `data-localizations\localizations\th\fonts\`

### 3.4 การติดตั้งเข้าสู่เกม
สามารถติดตั้งได้ 2 วิธี:
- **วิธีที่ 1 (Native Pak Injection):** นำ `.mft` ไปแพ็กลงใน `data-windows.pak` และนำ `language.xml` ไปแพ็กลงใน `data-localizations.pak` (ใช้สคริปต์ `pack_10tons_pak.py` ของเรา)
- **วิธีที่ 2 (Official Mod System):** นำโฟลเดอร์ `th` ไปวางไว้ที่ `Documents\DYSMANTLE Mods\<ชื่อ Mod>\localizations\th` และเปิดใช้งาน Mod ในเกม

## 4. ข้อควรระวัง (Gotchas)
- ห้ามใช้คำสั่ง Command Line จัดการกับไฟล์ `.pak` ของเกมแบบตรงๆ (เช่น 7zip) เพราะเอนจินต้องการ Alignment ของไฟล์แบบเฉพาะเจาะจง ต้องใช้สคริปต์ Python ที่เราเขียนขึ้นเพื่อแพ็กไฟล์กลับเท่านั้น
- หากแปลคำใหม่ๆ ลงไปในเกม ที่มีตัวอักษรไทยตัวใหม่ (เช่น สมมติว่าในเกมไม่มีตัว 'ฆ' ระฆัง แล้วเราเพิ่งแปลเข้าไป) **จะต้องรันสคริปต์ Baking ฟอนต์ใหม่ทุกครั้ง** เพื่อให้มันอบตัว 'ฆ' ลงไปใน MFT Texture ด้วย มิฉะนั้นตัวอักษรจะหายไป

## 5. บทสรุป
โปรเจกต์นี้สำเร็จอย่างสวยงาม 100% ด้วยการพึ่งพา Official Tool ของผู้พัฒนา ทำให้ได้ฟอนต์ MSDF ที่มีความคมชัดสูง ซูมไม่แตก และไม่ต้องพึ่งพาตัวแครกเกอร์/Hooker ใดๆ ทั้งสิ้น ถือเป็นวิธีการที่เสถียรที่สุดในการทำ Localization ครับ!
