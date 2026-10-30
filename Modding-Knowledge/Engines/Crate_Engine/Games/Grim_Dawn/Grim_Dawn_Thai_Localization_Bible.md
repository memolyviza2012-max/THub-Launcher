# Grim Dawn — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Grim Dawn is an ARPG developed by **Crate Entertainment** using their proprietary **PathEngine / Crate Engine** (an evolution of the Titan Quest engine). The Thai localization mod (by **LUNG DEAR**) uses an **Asset Override (Drop-in Archive)** architecture. The mod overrides the game's core archive files (`.arc`) for dialogue and quests, and uses loose text files (`.txt`) for UI, items, and skills. The font system uses a proprietary bitmap format (`.fnt` / `FNTX`).

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Crate Engine (Titan Quest Engine) |
| **Developer** | Crate Entertainment |
| **Mod Author** | LUNG DEAR |
| **Archive Format** | `.arc` (Magic: `ARC\x00`) |
| **Font System** | `.fnt` (Proprietary `FNTX` Bitmap Font) |
| **Thai Font** | Custom rendered bitmap (รองรับสระ/วรรณยุกต์ลอยเต็มรูปแบบ) |
| **Text System 1** | Compiled Dialogue/Quests in `.arc` |
| **Text System 2** | Loose `.txt` tags in `settings/text_en/` |
| **Text Encoding** | UTF-8 with BOM |
| **Mod Complexity** | ★★★☆☆ (Proprietary font & archive formats) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
ม็อดนี้ใช้วิธี **Asset Replacement + Loose File Override**:

```text
GrimDawn/
├── gdx1/resources/                (ภาคเสริม Ashes of Malmouth)
│   ├── Conversations.arc
│   └── Quests.arc
├── gdx2/resources/                (ภาคเสริม Forgotten Gods)
│   ├── Conversations.arc
│   └── Quests.arc
├── resources/                     (ตัวเกมหลัก)
│   ├── Conversations.arc          (637 KB - ไฟล์คอมไพล์บทสนทนา)
│   └── Quests.arc                 (355 KB - ไฟล์คอมไพล์บันทึกเควสต์)
│
└── settings/                      (หมวด Loose Files)
    ├── fonts/
    │   ├── briosopro.fnt          (2.2 MB - FNTX Bitmap Font)
    │   ├── cinematic.fnt          (1.4 MB)
    │   └── ... (รวม 21 font slots)
    │
    └── text_en/                   (หมวดข้อความ UI, Item, Skill)
        ├── tags_items.txt         (UTF-8 with BOM)
        ├── tags_skills.txt
        └── ... (รวม 19 ไฟล์)
```

---

## 4. Font Analysis

### 4.1 FNTX Proprietary Format (`.fnt`)
- **Magic Bytes:** `FNTX\x02\x00\x00\x00` (`46 4E 54 58 02 00 00 00`)
- ฟอนต์ของ Grim Dawn ไม่ใช่ TTF/OTF แต่เป็น **Proprietary Bitmap Font** ที่ประกอบไปด้วย Metadata ของระยะห่างตัวอักษร (Kerning/Metrics) และรูปภาพตัวอักษรที่ถูกเรนเดอร์ลงในแผ่น Atlas
- ม็อดเดอร์ทำการ Flooding ฟอนต์ทั้ง 21 ตัว (เช่น briosopro, cinematic, jura, nevis) ด้วยฟอนต์ไทยที่ออกแบบมาพิเศษ (มีการจัดเรียงสระบน-ล่างเพื่อแก้ปัญหาสระลอย)
- **Extraction:** ไม่สามารถสกัดออกมาเป็นฟอนต์ TTF ปกติได้ ต้องใช้โปรแกรมเฉพาะทางอย่าง `FontCompiler` ของ Grim Dawn Modding Tools ในการอ่าน/สร้าง

---

## 5. Text Analysis

เกมนี้แบ่งข้อความออกเป็น 2 ระบบชัดเจน:

### 5.1 Loose Tags System (`settings/text_en/*.txt`)
- ใช้สำหรับ UI, ชื่อไอเทม, คำอธิบายสกิล, ชื่อมอนสเตอร์
- **Format:** Key-Value plain text (เช่น `tagSkillName=ท่าโจมตี`)
- **Encoding:** UTF-8 with BOM
- **สถิติ:** มีอักษรไทยทั้งหมด **862,814 ตัวอักษร**

### 5.2 Compiled ARC System (`resources/*.arc`)
- ใช้สำหรับระบบ Dialogue (บทสนทนา NPC แบบมีเงื่อนไข/ทางเลือก) และ Quests
- **Format:** คอมไพล์เก็บไว้ใน `.arc`
- **สถิติ:** มีอักษรไทย (UTF-8 bytes `E0 B8 XX`) ซ่อนอยู่ประมาณ **60,295 ลำดับ**

**สถิติรวม:** ~923,109 อักษรไทย (ม็อดขนาดใหญ่ เกม ARPG เน้นเนื้อหา)

---

## 6. Cross-Engine Comparison
เปรียบเทียบกับเอนจินอื่นๆ ที่เคยวิเคราะห์:

| Feature | Grim Dawn (Crate) | Midnight Suns (UE4) | Hades II (SGE) |
|---|---|---|---|
| **Archive** | .arc (`ARC\x00`) | .pak | ไม่มี |
| **Font Format** | .fnt (`FNTX`) | .ufont (TTF) | .fnt (BMFont) |
| **Text Format** | .txt (Tags) + .arc | .locres | .sjson |
| **Text Encoding** | UTF-8 with BOM | UTF-16LE | UTF-8 |
| **Mod Method** | Override files | Pak insertion | Lua override |

**จุดเด่น:** ระบบของ Crate Engine เปิดกว้างให้ทำม็อดง่าย (Loose file override) แต่จะยากตรงเรื่อง Font ที่เป็นฟอร์แมตปิด ต้องใช้ Tools เฉพาะของทีมพัฒนาในการสร้าง

---

## 7. Pipeline — ขั้นตอนสร้างม็อด

1. **Text (UI/Items):** เปิดโฟลเดอร์เกมด้วย Grim Dawn Asset Manager แตกไฟล์ `text_en.arc` เอา `.txt` ออกมาแปลด้วย Text Editor ทั่วไป (อย่าลืมเซฟเป็น UTF-8 with BOM)
2. **Text (Dialogue):** เปิดโปรแกรม **ConversationEditor** (แถมมากับเกม) แปลบทสนทนา แล้วเซฟ
3. **Fonts:** ใช้ **Asset Manager** สร้าง `.fnt` (FNTX) โดยต้องเตรียมรูปภาพ Bitmap และ Metric file
4. **Build:** นำไฟล์ที่แก้แล้วไป Build กลับเป็น `.arc` หรือวางไว้ในโฟลเดอร์ `settings` และ `resources` แบบ Loose Files
5. **Deployment:** ผู้เล่นแค่ Copy โฟลเดอร์ไปวางทับในเครื่องตัวเอง

---

## 8. Troubleshooting
- **Verify Files (Steam):** ถ้าเกมอัปเดตหรือผู้เล่นกด Verify ไฟล์เกมใน Steam ไฟล์ `.arc` จะถูกดาวน์โหลดกลับเป็นภาษาอังกฤษ ม็อดเดอร์จึงทำ `INSTALL_THAIMOD.bat` ไว้ให้รันซ้ำ
- **สระ/วรรณยุกต์ลอย:** เกิดจากการคำนวณระยะ (Kerning) ใน `FNTX` ไม่ถูกต้อง ต้องแก้ที่ไฟล์ Source ก่อนแปลงเป็น `FNTX`
- **ม็อดซ้อนทับ (Grimmest / Survival):** ถ้าลงม็อดอื่นที่แก้ `.arc` เดียวกัน (เช่นม็อดเพิ่มมอนสเตอร์) จะชนกัน ม็อดนี้จึงมีการเตรียม `.arc` พิเศษไว้สำหรับ Grimmest โดยเฉพาะ

---

## 9. Required Tools
| Tool Name | Purpose | Source |
|---|---|---|
| ArchiveTool.exe | Unpack/Pack ไฟล์ `.arc` | [แถมมาในโฟลเดอร์เกม Grim Dawn] |
| AssetManager.exe | จัดการคอมไพล์ Font/Textures | [แถมมาในโฟลเดอร์เกม Grim Dawn] |
| ConversationEditor.exe| แปล/สร้างโครงข่ายบทสนทนา | [แถมมาในโฟลเดอร์เกม Grim Dawn] |

---

## 10. Extracted Assets
- ไม่สามารถสกัด TTF ได้เนื่องจากฟอนต์อยู่ในรูป `FNTX` Bitmap format

---

## 11. M2M Protocol
**(สำหรับ AI Agent ที่ต้องการนำคัมภีร์ไปรันสร้างม็อดอัตโนมัติ)**

### ข้อจำกัดสำหรับ AI
- **Text Translation:** ✅ AI ทำได้ 100% — สามารถอ่าน/เขียนไฟล์ `settings/text_en/*.txt` ได้โดยตรง
- **Dialogue Translation:** ⚠️ ค่อนข้างยาก เนื่องจากต้องแปลง `.arc` เป็นรูปแบบที่แก้ไขได้ (เช่น XML/JSON) ผ่าน `ArchiveTool.exe` ก่อน แล้วค่อยให้ AI แปล จากนั้นค่อยแพ็คกลับ
- **Font Generation:** ❌ AI ไม่สามารถสร้าง FNTX ได้เอง ต้องส่งต่อให้ Human Operator ใช้โปรแกรม `AssetManager.exe` สร้างให้
