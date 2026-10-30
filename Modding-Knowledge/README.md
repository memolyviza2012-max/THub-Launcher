# 🧠 Modding Knowledge Base (ศูนย์รวมคัมภีร์การทำ Mod)

> 📑 **สารบัญหลักสำหรับการค้นหา:**  
> - **[⚙️ สารบัญจัดระเบียบตามเอนจิ้นเกม (ENGINE_INDEX.md)](_Index/ENGINE_INDEX.md)** *(ค้นหาตามเอนจิ้น → รายชื่อเกม → คัมภีร์)*  
> - **[📖 สารบัญเรียงตามตัวอักษร A-Z (MASTER_INDEX.md)](_Index/MASTER_INDEX.md)**

ยินดีต้อนรับสู่ **Modding Knowledge Base** คลังความรู้ส่วนตัวที่รวบรวมเทคนิค งานวิจัย สคริปต์ และ "คัมภีร์" (Bibles) สำหรับการทำ Mod เกม โดยเฉพาะอย่างยิ่ง **การทำ Mod แปลภาษาไทย (Thai Localization)** และการดัดแปลงกลไกการทำงานของเอนจินเกมต่างๆ

โปรเจกต์นี้ถูกออกแบบมาให้เป็น **"สมองกลส่วนกลาง"** ที่ไม่ได้อัปเดตโดยมนุษย์เพียงอย่างเดียว แต่ทำงานร่วมกับ **AI Assistant** อย่างใกล้ชิด เมื่อใดก็ตามที่เราค้นพบเทคนิคใหม่ สามารถแคร็กไฟล์เกมได้ หรือสร้างเครื่องมือใหม่ๆ ขึ้นมาในโปรเจกต์ใดก็ตาม AI จะทำการบันทึก สรุปผล และส่งความรู้นั้น (Knowledge Item - KI) กลับมาเก็บไว้ที่ Repository แห่งนี้โดยอัตโนมัติ เพื่อให้เป็นรากฐานความรู้ที่สามารถนำไปประยุกต์ใช้กับเกมอื่นๆ ในอนาคตได้ทันที

---

## 📂 โครงสร้างการจัดเก็บข้อมูล (Directory Structure)

ข้อมูลในคลังความรู้นี้ถูกแบ่งออกเป็น 3 หมวดหมู่หลัก เพื่อให้ง่ายต่อการสืบค้นและนำไปใช้งาน:

### 🎮 Games (เจาะลึกเฉพาะเกม)
รวบรวม "คัมภีร์" และคู่มือการทำ Mod แบบ Step-by-Step ของเกมต่างๆ ที่เคยผ่านการวิจัยมาแล้ว เช่น:
- **Dead Island 2** - คู่มือการสร้าง Mod ภาษาไทยและระบบจัดการสคริปต์เสียงแบบสมบูรณ์
- **Dishonored 1** - การจัดการไฟล์และเทคนิคต่างๆ
- **Dying Light 2** - Modding Wiki
- **XCOM: Enemy Unknown** - การเจาะระบบฟอนต์ภาษาไทยของ Unreal Engine และขั้นตอนการทำ Mod
- **Deus Ex: Mankind Divided**, **Marvel's Guardians of the Galaxy**, **Space Hulk: Deathwing** ฯลฯ

### ⚙️ Engines (เจาะลึกระดับเอนจินเกม)
ความรู้ที่ผูกติดกับตัวเอนจินเกม ซึ่งมักจะสามารถนำไปใช้กับเกมอื่นที่สร้างด้วยเอนจินเดียวกันได้:
- **Frostbite Engine** 
  - *Mass Effect: Andromeda* - การสลับโครงสร้างฟอนต์ (Glyph Swapping), การบังคับตัดคำ (ZWSP Word-Wrap) และการแก้ไขไฟล์ `.res` ด้วย Hex/Binary
  - *Dead Space Remake* - กลยุทธ์การแทนที่และแทรกฟอนต์แบบ Custom
- **Fledge Engine** (The Surge) - โครงสร้างและแนวทางเฉพาะของเอนจิน Fledge
- **Unreal Engine** - เทคนิคทางเลือกสำหรับฟอนต์ในเอนจินรุ่นเก่า (Older Font Fallback)

### 🛠️ Techniques (เทคนิคการทำ Mod ทั่วไป)
รวบรวมเทคนิคและเครื่องมือที่เป็นสากล สามารถนำไปปรับใช้ได้กับแทบทุกเกม:
- **AI Modding** - แนวทางการเขียน Prompt ขั้นเทพ (Master Prompt Guide) และโปรโตคอลการอัปโหลดความรู้ของ AI
- **Getting Started** - พื้นฐานสำหรับมือใหม่ เช่น การเริ่มทำ Localization, เครื่องมือที่จำเป็น (Tools of the Trade), พื้นฐานการทำ Font Modding
- **Hooking and Proxy** - การเขียน Proxy DLL (เช่น `dxgi.dll` หรือ `dinput8.dll`) และการใช้ MinHook เพื่อแทรกแซงการทำงานของเกมในระดับหน่วยความจำ
- **Memory Scanning** - เครื่องมือค้นหาและจัดการ Address ด้วย AOB (Array of Bytes) Scanning
- **Data Parsing & Build Automation** - ตัวอ่าน JSON แบบเบา (Lightweight Parser) สำหรับโหลด Config ของ Mod และสคริปต์อัตโนมัติสำหรับการแพ็คและทดสอบ Mod

---

## 🤖 AI Knowledge Syncing
Repository นี้ทำงานด้วย **Global Rule** ของ AI:
> "Whenever a new 'Bible', 'Knowledge Item (KI)', or tutorial guide is created or updated... it MUST be automatically copied and organized into this repository."

ด้วยระบบนี้ ฐานข้อมูลที่นี่จะฉลาดขึ้น เติบโตขึ้น และอัปเดตอยู่เสมอตามโปรเจกต์ใหม่ๆ ที่เราได้ทำร่วมกันครับ!
