# Jump Space — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
เอกสารนี้วิเคราะห์กลไกม็อดภาษาไทยของเกม **Jump Space** ซึ่งพัฒนาด้วย **Unity Engine** โดยใช้ระบบ **Addressables** และ **Unity Localization System** ในการจัดการข้อความ ม็อดนี้เน้นความเรียบง่ายโดยการเข้าไปแทนที่ฐานข้อมูลข้อความ (String Table) ของภาษาอังกฤษโดยตรง 

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Unity |
| **Asset System** | Addressables |
| **Localization System** | Unity Localization Package |
| **File Format** | UnityFS (.bundle) |
| **Mod Complexity** | ★☆☆☆☆ (แทนที่ไฟล์ Bundle ข้อความตรงๆ) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
ม็อดนี้มีไฟล์เพียงไฟล์เดียวเท่านั้น (Minimalist Modding):
```
Jump Space/
└── Jump Space_Data/
    └── StreamingAssets/
        └── aa/
            └── StandaloneWindows64/
                └── localization-string-tables-english(en)_assets_all.bundle  ← ★ (495 KB)
```

---

## 4. Text Analysis — Unity Localization Bundle

ข้อความทั้งหมดของเกมถูกเก็บในไฟล์ `localization-string-tables-english(en)_assets_all.bundle`
- **โครงสร้างข้อมูล:** เป็น UnityFS แบบมาตรฐานที่เก็บ `StringTable`
- **วิธีการม็อด:** 
  1. แกะไฟล์ Bundle นี้ด้วยเครื่องมือเช่น **UABEA** (Unity Asset Bundle Extractor Avalon) หรือ **AssetStudio**
  2. ส่งออกข้อความ (Export to TXT/CSV)
  3. แปลข้อความภาษาไทยทับที่ข้อความต้นฉบับภาษาอังกฤษ
  4. นำเข้า (Import) ทับ StringTable เดิม และเซฟทับไฟล์ Bundle
- **ข้อมูลที่พบ:** จากการทำ String Scan พบคำศัพท์เมนูและชื่อสิ่งต่างๆ ในเกม เช่น `Master Volume`, `Jump Space Early Access!`, รวมถึงชื่อ Faction ต่างๆ เช่น `Materia`, `Legion`, `Atiran`

---

## 5. Font Analysis — System Fallback / Native Support

**ผลการวิเคราะห์ไฟล์อย่างละเอียด (Deep Scan):**
❌ **ไม่มีการแพ็กฟอนต์ไทยมากับม็อดตัวนี้**
- ไฟล์ขนาด 495 KB มีเพียงข้อความแปลเท่านั้น ไม่มีพื้นที่พอที่จะบรรจุฟอนต์ TTF/OTF หรือ TextMesh Pro SDF Atlas สำหรับภาษาไทย
- **สรุปสาเหตุ:** เกม Jump Space น่าจะรองรับการแสดงผลอักษรไทยอยู่แล้วโดยพื้นฐาน (Native Support) เช่น การใช้ฟอนต์ตัวที่รองรับ Unicode กว้างขวางอย่าง Noto Sans CJK/Thai มาเป็นค่าเริ่มต้น หรือตัวเอนจินตั้งค่า Fallback ไปเรียกใช้ฟอนต์ของระบบ Windows แทน ทำให้ม็อดเดอร์ไม่จำเป็นต้องดัดแปลงระบบฟอนต์ของเกมเลยแม้แต่น้อย

> *หมายเหตุ: หากผู้ใช้ต้องการแตกไฟล์ฟอนต์จริง (TTF) จากม็อดนี้ จะไม่สามารถทำได้เพราะไม่มีฟอนต์อยู่ภายในแพ็กเกจ (อ้างอิงจาก [EXTRACTION_NOTE.txt](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unity/Games/Jump_Space/Assets/Fonts/EXTRACTION_NOTE.txt))*

---

## 6. Required Tools
สำหรับผู้ที่ต้องการแปลเกมระบบ Unity Localization ด้วยวิธีนี้:
| เครื่องมือ | หน้าที่ |
|---|---|
| **UABEAvalon (UABEA)** | แกะและยัด StringTable กลับเข้าไปใน Unity Bundle |
| **AssetStudio** | ตรวจสอบโครงสร้างไฟล์ Bundle |
| **UnityPy (Python)** | (ทางเลือก) เขียนสคริปต์สกัดและอัดไฟล์อัตโนมัติ |

---

## 7. Conclusion

ม็อดภาษาไทยของ **Jump Space** เป็นตัวอย่างของม็อดระดับพื้นฐานที่สมบูรณ์แบบสำหรับเกม Unity ยุคใหม่ที่ใช้ Unity Localization Package ม็อดเดอร์เพียงแค่แก้ไข String Table แบบ 1:1 เท่านั้น และโชคดีที่เกมนี้ไม่ต้องต่อสู้กับเรื่องฟอนต์จัตุรัสหรือสระลอย ทำให้ระยะเวลาในการพัฒนาม็อดสั้นลงมาก
