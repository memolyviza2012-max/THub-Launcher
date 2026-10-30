# Hardspace Shipbreaker — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
เอกสารนี้วิเคราะห์กลไกม็อดภาษาไทยของเกม **Hardspace: Shipbreaker** ซึ่งพัฒนาด้วย **Unity Engine** ตัวเกมไม่ได้พึ่งพาการดัดแปลงไฟล์หลักของเอนจิน (Asset Bundle) แต่ใช้การเขียนปลั๊กอิน (BepInEx) แทรกแซงโค้ดแทน ซึ่งทำให้ม็อดมีความทนทานต่อการอัปเดตของเกมสูงมาก 

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Unity |
| **Modding Framework** | BepInEx (Runtime Injection) |
| **Font System** | TextMesh Pro (Dynamic Font Asset Injection) |
| **Text System** | Raw CSV (LocDB) |
| **Mod Complexity** | ★★☆☆☆ (ใช้ BepInEx แต่หลักการไม่ซับซ้อน) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
เมื่อตรวจสอบไดเรกทอรีของม็อด พบไฟล์ที่เป็นหัวใจสำคัญดังนี้:
```
Hardspace Shipbreaker/
├── BepInEx/
│   ├── core/ (ไฟล์ระบบ BepInEx และ Harmony)
│   └── plugins/
│       └── ThaiFontMod/
│           ├── ShipbreakerFontMod.dll (ปลั๊กอินที่ใช้แทรกโค้ด)
│           └── thai_font.ttf (ฟอนต์ภาษาไทยแบบ Raw TTF)
└── Data/
    └── LocDB/
        └── en (ไฟล์ฐานข้อมูลข้อความ)
```

---

## 4. Text & Font Analysis

### 4.1 ระบบข้อความ (Text / LocDB)
- ข้อความในเกมไม่ได้ถูกจับยัดใน Unity Bundle แต่ถูกวางไว้แบบเปลือยๆ ในโฟลเดอร์ `Data/LocDB/en`
- จากการวิเคราะห์ไฟล์ `en` พบว่ามันคือ **ไฟล์ CSV ธรรมดาที่ไม่ได้เข้ารหัส แต่เซฟในรูปแบบ UTF-8 (No BOM)**
- ม็อดเดอร์ใช้วิธีแปลข้อความและนำไปทับไฟล์เดิมได้เลยทันที (ไม่ต้องพึ่งโปรแกรมแกะไฟล์) ข้อสังเกตคือหากเปิดใน Notepad หรือโปรแกรมที่ไม่อ่าน UTF-8 เป็นค่าเริ่มต้น อาจจะเห็นตัวอักษรกลายเป็น `???` ได้

### 4.2 ระบบฟอนต์ (Dynamic TextMesh Pro Injection)
- **การค้นพบที่น่าสนใจ:** เกม Unity ยุคใหม่ใช้ระบบ TextMesh Pro (TMP) ซึ่งปกติจะต้องเอาฟอนต์ไปทำ (Bake) เป็นไฟล์ภาพ SDF Texture แต่ในเคสนี้ **ม็อดเดอร์ใส่ไฟล์ Raw `.ttf` เข้ามาแบบดื้อๆ เลย!**
- **สถาปัตยกรรมโค้ด (Decompiled DLL):** จากการสแกน `ShipbreakerFontMod.dll` พบชุดคำสั่ง:
  - `TMP_FontAsset.CreateFontAsset()`
  - `TMP_Settings.fallbackFontAssets`
- **สรุปกระบวนการ:** ปลั๊กอินจะดึงไฟล์ `thai_font.ttf` โหลดขึ้นมากลางอากาศขณะรันเกม (Runtime) สร้างเป็น Dynamic Font Asset ของ TextMesh Pro แล้วสั่งยัดเข้าสู่ระบบ "Fallback Font" ของเกม เพื่อให้ทุกครั้งที่เกมแสดงตัวอักษรไทยที่ฟอนต์หลักไม่มี มันจะเด้งมาใช้ฟอนต์นี้ทันที นี่เป็นเทคนิคที่ชาญฉลาดและหลีกเลี่ยงการ Bake ไฟล์ภาพได้อย่างหมดจด!

> ✅ **ผลการดึง Asset:**
> สกัดไฟล์ฟอนต์จริงสำเร็จแบบไม่ต้องแกะไฟล์ใดๆ เนื่องจากม็อดเดอร์ใส่มาให้ตรงๆ! 
> **ชื่อฟอนต์:** `TH Niramit AS Bold`
> **พิกัดไฟล์:** ถูกคัดลอกลงคลังความรู้แล้วที่ [thai_font.ttf](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unity/Games/Hardspace_Shipbreaker/Assets/Fonts/thai_font.ttf)

---

## 5. Required Tools
สำหรับผู้ที่ต้องการดัดแปลงม็อดตัวนี้เพิ่มเติม:
| เครื่องมือ | หน้าที่ |
|---|---|
| **Text Editor (VSCode / Notepad++)** | ใช้แก้ไขไฟล์ข้อความ `.csv` (ต้องจำกัด Save เป็น UTF-8) |
| **Visual Studio / Rider** | สำหรับแก้ไขหรือปรับปรุงโค้ด `ShipbreakerFontMod.dll` หากเกมอัปเดตจนปลั๊กอินพัง |
| **ILSpy / dnSpy** | ใช้ Decompile ตัว `.dll` เพื่อศึกษาโค้ดดั้งเดิม |

---

## 6. Conclusion
ม็อด **Hardspace: Shipbreaker** แสดงให้เห็นถึงพลังของ BepInEx ที่นำมาใช้กับระบบ Dynamic TextMesh Pro ของ Unity ได้อย่างเต็มประสิทธิภาพ การที่ม็อดเดอร์ไม่ต้องต่อสู้กับการแพ็กไฟล์ Bundle ทำให้การสร้างม็อดตัวนี้ง่ายและมีเสถียรภาพสูงมาก และเป็นตัวอย่างที่ยอดเยี่ยมสำหรับเกม Unity สมัยใหม่
