<div align="center">
  <img src="https://img.icons8.com/color/96/000000/launch.png" alt="THub Logo" width="100"/>
  <h1>🚀 THub Launcher : The Flagship Suite</h1>
  <p><b>Ultimate Game Modding & Localization Environment</b></p>
   <p><b>โปรแกรมนี้ยังเป็นช่วง Beta อยู่นะครับ</b></p>
  
  [![Version](https://img.shields.io/badge/Version-1.0.2-blue.svg?style=for-the-badge)](#)
  [![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg?style=for-the-badge)](#)
  [![Python](https://img.shields.io/badge/Built_with-Python_3.11-yellow.svg?style=for-the-badge)](#)
</div>

<br/>

**THub Launcher** คือศูนย์รวมและจุดศูนย์กลาง (Hub) ระดับมืออาชีพสำหรับนักแปลเกม นักม็อด และผู้ใช้งานทั่วไป! 
เป้าหมายหลักของ THub คือการพลิกโฉมวงการ Game Localization โดยการรวบรวมเครื่องมือ **(The Flagship Suite)** ทั้งหมดให้อยู่ในที่เดียว ทำงานภายใต้สภาพแวดล้อมเดียวกัน (Unified Environment) พร้อมระบบการจัดการ Workspace ของแต่ละโปรเจกต์ที่เชื่อมถึงกันอย่างสมบูรณ์แบบ

---

## 💎 The Flagship Suite (ชุดโปรแกรมเรือธง)

THub มาพร้อมกับระบบดาวน์โหลดและเชื่อมต่อกับ 5 สุดยอดเครื่องมือ ที่ถูกออกแบบมาเพื่อรองรับงานดัดแปลงเกมและงานแปลภาษาครบทุกมิติ:

### 1. 📝 TStudio (Advanced Translation Engine)
**"เครื่องมือแปลภาษาด้วย AI แบบ Line-by-Line"**
*หัวใจหลักของการแปลเกม* TStudio ถูกออกแบบมาเพื่อจัดการไฟล์ข้อความขนาดใหญ่ (JSON, XML, CSV, TXT) มีระบบดึง Context เข้าช่วยแปล ทำให้การแปลเกมด้วย AI (Local/Cloud) มีความแม่นยำสูง พร้อมตารางเปรียบเทียบคำต่อคำ (Side-by-side) และระบบคำศัพท์เฉพาะ (Glossary)

### 2. ⚡ TRun (Batch Automation & Runner)
**"เครื่องมือทดสอบและแพตช์ไฟล์แบบรวดเร็ว"**
เครื่องมือสำหรับจำลองการนำไฟล์ที่แปลเสร็จแล้วยัดกลับเข้าสู่ตัวเกม (Repacking) และรันทดสอบการทำงานแบบอัตโนมัติ ช่วยลดเวลาที่ต้องสลับหน้าจอไปมา ลดความผิดพลาดของ Human Error ในระหว่างกระบวนการ Build

### 3. 🔤 TPUA (PUA Font Manager)
**"จัดการและปรับแต่ง Private Use Area Fonts"**
ปัญหาโลกแตกของภาษาไทยในเกมคือ "สระลอย" TPUA จะช่วยประมวลผล จัดเรียง และจัดการรหัสตัวอักษรไทยให้อยู่ในโซน PUA อัตโนมัติ เพื่อนำไปใช้แก้ปัญหาสระลอย/จม ในเอนจิ้นเกมยุคใหม่ได้อย่างหมดจด

### 4. 🎨 TGlyph (Font Texture Generator)
**"ระบบสร้าง Texture ไฟล์ฟอนต์ระดับ Pixel-Perfect"**
หลังจากจัดการตัวอักษรด้วย TPUA แล้ว TGlyph จะรับไม้ต่อในการ Render ตัวอักษรเหล่านั้นให้ออกมาเป็นภาพ (Texture Atlas) เช่นไฟล์ `.DDS`, `.PNG` พร้อมทำแมปปิ้งพิกัด (Coordinates) ที่พร้อมนำไปยัดลงในไฟล์เกม (เช่น Unreal Engine หรือ Unity) ทันที

### 5. 🎬 TVox (FMV Dubbing & Subtitling)
**"ระบบพากย์เสียง AI และจัดการซับไตเติ้ลวิดีโอ (FMV)"**
สำหรับเกมที่ใช้คัทซีนแบบวิดีโอ (Full Motion Video) TVox ออกแบบมาเพื่อถอดเสียง ฝังซับไตเติ้ล (Hardsub) และแม้กระทั่งการทำ AI Voice Dubbing ทับเสียงเดิมในวิดีโอ พร้อม Preview แบบ Real-time!

---

## 🌟 ฟีเจอร์หลักของ Launcher (Core Features)

- **📁 Unified Project Dashboard:** ศูนย์กลางการจัดการไฟล์แปล สร้างโปรเจกต์เดียว สามารถเรียกใช้ได้จากทุก Flagship Tools!
- **☁️ Cloud Registry & Auto-Update:** สมุดหน้าเหลืองออนไลน์ที่เชื่อมต่อกับ GitHub ดึงรายการโปรแกรมและอัปเดต Flagship Tools เป็นเวอร์ชันล่าสุดแบบ Over-The-Air (OTA)
- **🧩 Tool Library:** ศูนย์รวมซอฟต์แวร์เสริมของบุคคลที่สาม (Third-party Tools) เช่น FModel, QuickBMS, AssetStudio กว่า 10 ชนิด ที่กดรันได้ทันทีโดยไม่ต้องไปหาโหลดเอง
- **📚 Modding Knowledge:** คลังความรู้และคู่มือฉบับเจาะลึก ฝังมาในโปรแกรม เพื่อสอนมือใหม่ให้เป็นนักม็อดระดับโปร
- **🎨 Modern Glassmorphism UI:** ดีไซน์หน้าต่างโปรแกรมที่ล้ำสมัย สวยงาม ใช้งานลื่นไหล และรองรับระบบ Dark Mode สมบูรณ์แบบ

---

## 📁 โครงสร้างโปรเจกต์มาตรฐาน (THub Workspace Structure)

เมื่อคุณสร้างโปรเจกต์ใหม่ผ่าน THub Launcher ระบบจะจำลองและสร้างโครงสร้างโฟลเดอร์ทำงานที่เป็นระเบียบและเป็นมาตรฐานของงานแปลภาษาเกมให้โดยอัตโนมัติ ดังนี้:

```text
📁 [โฟลเดอร์โปรเจกต์]/
├── 📁 01_Original_Backup/       # โฟลเดอร์เก็บไฟล์ข้อความดิบต้นฉบับเกม (เช่น ภาษาอังกฤษ) เพื่อใช้สำรองข้อมูล
├── 📁 02_Translation_Workspace/ # โฟลเดอร์สำหรับแก้ไขและบันทึกไฟล์คำแปลภาษาไทย (.csv, .json) ผ่าน TStudio
├── 📁 03_Font_and_UI/           # โฟลเดอร์เก็บไฟล์ฟอนต์, รูปภาพ Atlas, พิกัดตัวอักษร, และการแมปสระ PUA
├── 📁 04_Packed_Mod/            # โครงสร้างตัวม็อดทดสอบที่จัดเรียงพาธเสร็จพร้อมวางทับหรือลงเกมจริง
├── 📁 05_Scripts_and_Tools/     # โฟลเดอร์สำหรับสคริปต์เสริมพิเศษ หรือโปรแกรมดึง/บีบอัดไฟล์เฉพาะเกม
├── 📁 06_Releases/              # โฟลเดอร์จัดเก็บไฟล์ม็อดสำเร็จรูปเวอร์ชันที่เสร็จแล้ว (.zip, .rar) สำหรับนำไปแจกจ่าย
├── 📄 thub_project.json         # บันทึกพาธเกม, ค่าการตั้งค่า, เวอร์ชันม็อด และข้อมูลเฉพาะของโปรเจกต์
└── 📄 README.md                 # เอกสารแนะนำโปรเจกต์ที่สร้างอัตโนมัติ
```

---

## 📥 วิธีติดตั้งและเข้าใช้งาน (Installation)

1. ไปที่หมวด [Releases](../../releases) ของ Repository นี้
2. ดาวน์โหลดไฟล์ **`THub_Release_v1.x.x.zip`** ล่าสุด
3. แตกไฟล์ (Extract) ไว้ในโฟลเดอร์ที่คุณต้องการ (เช่น `D:\THub_Launcher\`)
4. ดับเบิ้ลคลิกที่ไฟล์ **`THub.exe`** 
5. ไปที่เมนู **Flagship Products** เพื่อเริ่มติดตั้ง T-Series ลงในเครื่องของคุณได้ทันที!

---

## ⚙️ โครงสร้างและการทำงาน (For Developers)
THub Launcher ถูกออกแบบมาในรูปแบบ **"Engine Host"** ด้วย `Python (CustomTkinter)`:
- ตัวโปรแกรม `THub.exe` จะทำหน้าที่เป็นเหมือนเครื่องยนต์ประมวลผล Python 
- เมื่อมีการดาวน์โหลด Flagship จาก GitHub โค้ดของโปรแกรมลูกๆ (เช่น `TStudio.py`) จะถูกเก็บไว้ในโฟลเดอร์ `tools/flagship/`
- เมื่อผู้ใช้กดรัน THub จะทำการ Inject สคริปต์เข้าสู่หน่วยความจำตัวเอง ทำให้ไม่ต้อง Compile โปรแกรมใหม่เมื่อมีการอัปเดตย่อยๆ (Micro-updates)
- ทำให้ผู้ใช้งานได้รับประสบการณ์อย่างไร้รอยต่อ และไม่จำเป็นต้องติดตั้งสภาพแวดล้อม (Environment) ใดๆ เพิ่มเติม!

<br/>

<div align="center">
  <b>Made with ❤️ for the Modding Community</b>
</div>
