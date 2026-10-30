# Final Fantasy XV — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
เอกสารนี้วิเคราะห์กลไกม็อดภาษาไทยของเกม **Final Fantasy XV (FF15)** ซึ่งพัฒนาด้วย **Luminous Engine** ของ Square Enix ตัวเกมใช้สถาปัตยกรรมการแพ็กไฟล์ระดับองค์กรแบบเจาะจง (Proprietary Format) ที่มีความซับซ้อนสูง 

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Luminous Engine (Square Enix Proprietary) |
| **Archive Format** | `.earc` (Enix Archive) |
| **Compression** | Block-level Zlib Compression (128 KB chunks) |
| **Font System** | Proprietary Bitmap/Texture Atlas (`.tex` + `.font`) |
| **Mod Complexity** | ★★★★★ (High Proprietary Barrier) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
ม็อดนี้ประกอบด้วยไฟล์ขนาดใหญ่เพียงไฟล์เดียว ซึ่งทำหน้าที่แพ็กเกจรวมทุกอย่าง:
```
FINAL FANTAS 15/
└── datas/
    └── common/
        └── fontandmessage.earc  ← ★ (168 MB)
```
- **วิเคราะห์ไฟล์ .earc:** `fontandmessage.earc` เป็นไฟล์บีบอัดแบบ Zlib โดยแบ่งบล็อกข้อมูลย่อยบล็อกละ 128 KB (อ้างอิงจากการสแกนด้วยสคริปต์ Decompressor ที่ตรวจจับ Chunk Magic `78 9C`)

---

## 4. Font & Text Analysis

### 4.1 ระบบข้อความ (Message)
- ข้อความและบทสนทนาทั้งหมดของ FFXV ถูกจัดเก็บอยู่ในไฟล์ตระกูล `.msg` หรือ `.exb` ภายในแฟ้ม `.earc`
- เนื่องจากตัวอักษรภาษาไทยมีความซับซ้อน ม็อดเดอร์จึงใช้เครื่องมือเฉพาะทาง (เช่น **Flagrum**) ในการนำเข้าข้อความแปลภาษาไทย เพื่อให้เอนจินเกมรับรู้และโหลดข้อความขึ้นมาได้อย่างถูกต้อง

### 4.2 ระบบฟอนต์ (Font Bitmap)
จากการแกะบล็อก Zlib เพื่อค้นหา Raw Vector Font (`00 01 00 00` / `OTTO`) พบว่า **ไม่ปรากฏฟอนต์เวกเตอร์อยู่ในระบบเลย**
- Luminous Engine ไม่อ่านฟอนต์ TTF/OTF โดยตรง แต่ใช้โปรแกรมแปลงฟอนต์ให้กลายเป็น **รูปภาพแบบ Bitmap/SDF (Texture Atlas)** ในฟอร์แมต `.tex` พร้อมด้วยไฟล์ตารางชี้พิกัดอักษร `.font` 
- ม็อดเดอร์ใช้วิธี Generate ฟอนต์ไทยเข้าสู่ระบบนี้ (Baking) ทำให้ข้อมูลเวกเตอร์แบบเดิมสูญหายไปทั้งหมด คงเหลือแต่ Texture 

> *การดึงฟอนต์:* ไม่สามารถสกัดออกมาเป็นฟอนต์ Windows (.ttf) ได้ ดูรายละเอียดเพิ่มเติมที่ [EXTRACTION_NOTE.txt](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Luminous_Engine/Games/FFXV/Assets/Fonts/EXTRACTION_NOTE.txt)

---

## 5. Required Tools
การสร้างม็อดให้ FFXV ต้องการเครื่องมือเจาะจงเฉพาะเกม:
| เครื่องมือ | หน้าที่ |
|---|---|
| **Flagrum (Modding Tool)** | สุดยอดโปรแกรมจัดการม็อดของ FFXV ใช้ Unpack/Repack ไฟล์ `.earc` จัดการ Asset ฟอนต์และข้อความ |
| **Luminous Engine EARC Extractor** | เครื่องมือเสริมสำหรับแกะไฟล์ .earc (หากไม่ใช้ Flagrum) |

---

## 6. Conclusion

ม็อดภาษาไทยของ **Final Fantasy XV** แสดงให้เห็นถึงการทำงานกับเอนจินแบบกรรมสิทธิ์ (Proprietary Engine) ที่มีความยืดหยุ่นน้อยกว่าเอนจินตลาด (UE/Unity) การทำงานต้องพึ่งพาระบบ Block-Compression และ Texture Baking ทำให้งานหนักตกไปอยู่ที่เครื่องมือของชุมชนม็อดเดอร์ (เช่น Flagrum) ซึ่งช่วยเจาะระบบ `.earc` และทำการแปลงฟอนต์/ข้อความให้เป็นฟอร์แมตที่เกมยอมรับได้
