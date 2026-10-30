# F.E.A.R. 3 — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
F.E.A.R. 3 เป็นเกมแนว First-Person Shooter สยองขวัญที่พัฒนาโดย Day 1 Studios ตัวเกมใช้เอนจิ้น Despair Engine ในการพัฒนา สถาปัตยกรรมของม็อดเป็นรูปแบบ **File Replacement** โดยตรง เนื่องจากตัวเกมยอมให้อ่านไฟล์ที่แตกออกมาวางไว้ในแฟ้มข้อมูลหลักได้ทันที

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Despair Engine |
| **Developer** | Day 1 Studios |
| **Archive Format** | `.dsPack` (Proprietary) |
| **AES Encryption** | No |
| **Compression** | Raw / Proprietary Stream |
| **Font System** | Bitmap Font Swap (`.dsFont` + `.tif`) |
| **Thai Font Used** | (To be injected via TGlyph onto `.tif`) |
| **Text System** | `.dsLocaleText` (Custom Binary) |
| **Text Encoding** | UTF-16 LE |
| **Mod Complexity** | ★★★☆☆ (Requires in-place replacement and bitmap injection) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```text
FEAR 3/
├── Boot/
│   ├── Fonts/
│   │   ├── English/
│   │   │   ├── ArialReg20_01.tif (Texture Atlas)
│   │   │   └── Base02Reg18.dsFont (Font Metadata)
│   ├── Text/
│   │   └── default_English.dsLocaleText (Primary Text Archive)
```

---

## 4. Font Analysis
- **รูปแบบ:** ตัวเกมไม่ได้ใช้ TrueType Font (.ttf) โดยตรง แต่ทำการแรนเดอร์ภาพตัวอักษรเก็บไว้ในไฟล์ `.tif` แล้วใช้ไฟล์ `.dsFont` ในการระบุพิกัด UV (X, Y, Width, Height) ของแต่ละตัวอักษร
- **การปรับแต่งสำหรับภาษาไทย:** เนื่องจาก `.dsFont` มีการเข้ารหัสพิกัดที่ซับซ้อน เราจึงใช้วิธี **Glyph Replacement** โดยวาดสระและพยัญชนะภาษาไทยทับลงไปในช่องของตัวอักษรละตินส่วนขยายในไฟล์ภาพ `.tif` (ด้วยเครื่องมือ TGlyph) และตั้งค่า Text Shaping สลับรหัสตัวอักษรแทน

---

## 5. Text Analysis
- **รูปแบบ:** ไฟล์ `.dsLocaleText` เก็บข้อความทั้งหมดไว้รวมกันในรูปแบบ `UTF-16LE`
- **โครงสร้าง:** ไม่ใช่ Key-Value ปกติ แต่เป็น Binary Block ที่ชี้ Pointer กลับไปกลับมา
- **ข้อควรระวัง:** การเปลี่ยนความยาวของข้อความแปลให้ยาวขึ้นกว่าข้อความต้นฉบับจะทำให้ Pointer ขัดข้อง จึงต้องใช้เทคนิค **In-place Replacement** (จำกัดความยาวเท่าเดิมและแพดด้วยช่องว่าง)

---

## 6. Cross-Engine Comparison
- เมื่อเทียบกับ **Unreal Engine** ที่ใช้ `.locres` หรือ **Unity** ที่ใช้ StringTable การปรับแก้ Text ของ Despair Engine ทำได้ยากกว่ามากเพราะไม่มี Tool สมบูรณ์แบบที่ปรับแต่ง Pointer ได้อิสระ
- เมื่อเทียบกับ **Luminous Engine** ที่เป็น Bitmap Font เช่นกัน เทคนิค Glyph Replacement นี้นิยมใช้ในโปรเจกต์ภาษาไทยดั้งเดิม (เช่น ยุค PS2 หรือเอนจิ้นเก่าที่อ่าน TTF ไม่ได้)

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
**Text Pipeline:**
1. ใช้ `FEAR3_unpacker.py` สกัดไฟล์ `.dsLocaleText` เป็น CSV
2. แปลภาษาผ่าน TStudio / TRun
3. ใช้ `FEAR3_packer.py` เพื่อแพ็คข้อความแปลกลับลง `.dsLocaleText` โดยแทนที่ที่เดิม (In-place)

**Font Pipeline:**
1. นำไฟล์ `.tif` ตัวอักษร เช่น `ArialReg20_01.tif` เข้าสู่โปรแกรม TGlyph
2. สั่ง TGlyph วาดตัวอักษรภาษาไทยลงไปในช่องตัวอักษรที่ไม่ได้ใช้ (ผ่าน Command Line)
3. บันทึกทับไฟล์ `.tif` เดิม

---

## 8. Troubleshooting
- **ข้อความหายไปในเกม:** ความยาวข้อความแปลเกินกว่าต้นฉบับจน `FEAR3_packer.py` ทำการ Truncate หรือโครงสร้างเสียหาย ให้ลดความยาวคำแปลลง
- **สระลอย:** ฟอนต์ Bitmap รองรับเฉพาะการแทนที่ Glyph ตำแหน่งคงที่ หากมีปัญหาสระลอย ต้องใช้ PUA Text Shaping จาก TGlyph สลับอักขระก่อนแพ็คไฟล์ด้วย Packer

---

## 9. Required Tools
| Tool Name | Purpose |
|---|---|
| `FEAR3_unpacker.py` | ดึงข้อความจากเกมมาเป็น CSV (TStudio Compatible) |
| `FEAR3_packer.py` | ยัดข้อความกลับแบบ In-place (ความยาวตายตัว) |
| `TGlyph` (THub) | เปลี่ยนและวาดอักขระไทยลงบนไฟล์ Bitmap (.tif) |

---

## 10. Extracted Assets
- [default_English.dsLocaleText](file:///E:/Mod_Workspace/FEAR3/01_Original_Backup/Boot/Text/default_English.dsLocaleText)
- [ArialReg20_01.tif](file:///E:/Mod_Workspace/FEAR3/01_Original_Backup/Boot/Fonts/English/ArialReg20_01.tif)
- [Base02Reg18.dsFont](file:///E:/Mod_Workspace/FEAR3/01_Original_Backup/Boot/Fonts/English/Base02Reg18.dsFont)

---

## 11. M2M Protocol (Automated Font Workflow)
สำหรับการรันอัตโนมัติ (M2M) เครื่องมือ TGlyph สามารถสั่งรันผ่าน Command Line เพื่อแก้ไขภาพบิตแมปของ FEAR 3 ได้ โดยการกำหนดตาราง Glyph Map อัตโนมัติ (Automated Rendering Script) ซึ่งจะอ่านภาพต้นฉบับ ค้นหาตำแหน่ง UV และเขียนตัวอักษรภาษาไทยทับลงไป
