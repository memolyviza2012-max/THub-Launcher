# Translation Studio Template

## สำหรับ AI ที่นำ Template นี้ไปใช้กับโปรเจคใหม่

> **อ่านไฟล์นี้ก่อนแก้โค้ดทุกครั้ง** ไฟล์นี้บอกทุกอย่างที่ต้องทำและต้องไม่ทำ

---

## โครงสร้างไฟล์ในโฟลเดอร์นี้

```
2_Studio_translation/
├── Translation_Studio_Template.py   ← โปรแกรม Studio (UI — ดู/แก้คำแปลด้วยตัวเอง)
├── run_translation_template.py      ← สคริปต์ AI แปลอัตโนมัติแบบ Batch
├── TEMPLATE_README.md               ← ไฟล์นี้ (คู่มือสำหรับ AI)
├── VERSION.txt                      ← ระบุเวอร์ชัน Template สำหรับติดตาม
├── config.json                      ← เก็บ API Key & Model (ใช้ร่วมกันทั้งคู่!)
├── glossary.json                    ← คำศัพท์บังคับ (ใช้ร่วมกันทั้งคู่!)
├── Start_Studio.bat                 ← ดับเบิลคลิกเปิดโปรแกรม Studio
└── Start_AI_Translation.bat         ← ดับเบิลคลิกรัน AI แปลอัตโนมัติ
```

> **จุดเด่นสำคัญ:** ทั้ง 2 โปรแกรมใช้ `config.json` และ `glossary.json` **ไฟล์เดียวกัน**
> แปลว่าตั้งค่า API Key ครั้งเดียว ใช้ได้ทั้ง Studio และ Script แก้คำศัพท์ใน Studio แล้ว Script ก็ใช้ทันที!

---

## ขั้นตอนการดัดแปลงให้เหมาะกับโปรเจคใหม่

### ✅ ขั้นตอนที่ 1: Copy โฟลเดอร์ทั้งหมด
Copy โฟลเดอร์ `2_Studio_translation` ทั้งโฟลเดอร์ไปไว้ในโปรเจคใหม่
(หรือทำงานโดยตรงกับโฟลเดอร์นี้ก็ได้ แล้วแก้ config ให้ชี้ไปหา CSV ของโปรเจคนั้น)

### ✅ ขั้นตอนที่ 2: แก้ไข PROJECT CONFIGURATION (แก้แค่นี้ที่เดียว!)

เปิดไฟล์ `Translation_Studio_Template.py` แล้วหาส่วนนี้ด้านบนสุด:

```python
# ╔══════════════════════════════════════════════════════════════════╗
# ║           PROJECT CONFIGURATION — แก้ตรงนี้เท่านั้น!            ║
# ╚══════════════════════════════════════════════════════════════════╝
GAME_NAME    = "Game Name"
CSV_PATH     = r""
CSV_ENCODING = "utf-8"
COL_ID       = 0
COL_SOURCE   = 1
COL_TRANS    = 2
COL_AI_REF   = 3
```

แก้ค่าตามโปรเจคใหม่:

| ตัวแปร | คำอธิบาย | ตัวอย่าง |
|--------|----------|---------|
| `GAME_NAME` | ชื่อเกม (ใช้ใน AI Prompt และหัวต่าง) | `"Dishonored 2"` |
| `CSV_PATH` | Path เต็มไปยังไฟล์ CSV | `r"E:\...\translation.csv"` |
| `CSV_ENCODING` | Encoding ของไฟล์ CSV | `"utf-8"` หรือ `"utf-16-le"` |
| `COL_ID` | หมายเลขคอลัมน์ที่เก็บ ID | `0` (คอลัมน์แรก) |
| `COL_SOURCE` | หมายเลขคอลัมน์ที่เก็บข้อความต้นฉบับ | `1` |
| `COL_TRANS` | หมายเลขคอลัมน์ที่เก็บคำแปล | `2` |
| `COL_AI_REF` | หมายเลขคอลัมน์ AI Reference (ถ้าไม่มีให้ใส่ค่าเดียวกับ COL_TRANS) | `3` |

> **Encoding Guide:**
> - ไฟล์ที่เปิดด้วย Excel แล้วภาษาไทยแสดงผิด → ลอง `utf-16-le`
> - ไฟล์ทั่วไป → `utf-8` หรือ `utf-8-sig`

### ✅ ขั้นตอนที่ 3: ตั้งค่า API Key ผ่านโปรแกรม
เปิดโปรแกรม → กดปุ่ม **⚙️ Settings** → กรอก API Key และ Model Name → กด Save
(ค่าจะถูกบันทึกลง `config.json` อัตโนมัติ)

---

## สิ่งที่ AI ไม่ควรแก้ไข (ห้ามแตะ!)

- ❌ ห้ามแก้ Dark Theme CSS (`DARK_SS`)
- ❌ ห้ามเปลี่ยนชื่อคลาส Dialog (SettingsDialog, GlossaryDialog ฯลฯ)
- ❌ ห้ามลบปุ่มใดๆ ออกจาก Toolbar
- ❌ ห้ามเปลี่ยนโครงสร้าง 3 กล่องด้านขวา (Original / AI Ref / My Translation)

---

## ฟีเจอร์ที่มีในโปรแกรม (ไม่ต้องเพิ่มใหม่)

| ปุ่ม | หน้าที่ |
|------|--------|
| 🔍 Search | ค้นหาข้อความในตาราง |
| 🔍 Find/Replace | ค้นหาและแทนที่คำแปลแบบ Bulk |
| 📖 Glossary | จัดการคำศัพท์บังคับ (บันทึกใน `glossary.json`) |
| ⚙️ Settings | ตั้งค่า API Key / Model (บันทึกใน `config.json`) |
| 💾 Save CSV | บันทึกคำแปลกลับลงไฟล์ CSV เดิม |
| 🤖 Re-translate (AI) | ส่งประโยคที่เลือกไปให้ AI แปลใหม่ 1 แบบ |
| 🎯 Re-translate (3 Options) | ส่งประโยคที่เลือกไปให้ AI แปลมา 3 สไตล์ให้เลือก |

---

## ตัวอย่างการ Config สำหรับโปรเจคต่างๆ

### โปรเจค XCOM (UTF-8)
```python
GAME_NAME    = "XCOM 2"
CSV_PATH     = r"E:\Mod_Workspace\XCOM2\Translation\xcom2_en.csv"
CSV_ENCODING = "utf-8"
COL_ID       = 0
COL_SOURCE   = 1
COL_TRANS    = 2
COL_AI_REF   = 2   # ถ้าไม่มี AI Ref ให้ชี้ไปคอลัมน์เดิม
```

### โปรเจค Dying Light 2 (UTF-16-LE)
```python
GAME_NAME    = "Dying Light 2"
CSV_PATH     = r"E:\Mod_Workspace\DL2_mod_workspace\Translation\English_Original.csv"
CSV_ENCODING = "utf-16-le"
COL_ID       = 0
COL_SOURCE   = 1
COL_TRANS    = 2
COL_AI_REF   = 3
```

---

## หมายเหตุสำหรับ AI

- Template นี้ถูกออกแบบมาให้ **"หน้าตาเหมือนกันทุกโปรเจค"** เพื่อให้เจ้าของโปรเจค (คุณบอส) ใช้งานได้โดยไม่ต้องเรียนรู้ใหม่
- ถ้าโปรเจคใหม่ต้องการฟีเจอร์พิเศษเฉพาะ (เช่น Export Binsloc, Export PAK) ให้ **"เพิ่มปุ่มใหม่"** เข้าไปใน Toolbar อย่าลบหรือแก้ปุ่มที่มีอยู่แล้ว
- ถ้าโปรเจคใหม่มีระบบ Encoding พิเศษ ให้แก้เฉพาะ `CSV_ENCODING` และฟังก์ชัน `save_csv` เท่านั้น
- เมื่อดัดแปลง Template แล้ว ให้อัปเดต `VERSION.txt` ด้วยทุกครั้ง เพื่อให้ติดตามเวอร์ชันได้ง่าย

---

## ⚠️ จุดสำคัญ: ฟังก์ชัน `is_translated()`

ทั้ง Script (`run_translation_template.py`) และ Studio (`Translation_Studio_Template.py`) ใช้ฟังก์ชันนี้ตรวจว่าแถวไหน "แปลแล้ว" โดยการตรวจหา **อักษรไทย** ในช่องคำแปล:

```python
def is_translated(text):
    return bool(re.search(r'[\u0E00-\u0E7F]', text))  # ← ตรวจอักษรไทยโดยเฉพาะ
```

**ถ้าโปรเจคใหม่แปลเป็นภาษาอื่น ต้องเปลี่ยน Unicode Range ตัวนี้!**

| ภาษาเป้าหมาย | Unicode Range ที่ต้องใช้ |
|-------------|------------------------|
| 🇹🇭 ไทย (ค่าเริ่มต้น) | `[\u0E00-\u0E7F]` |
| 🇯🇵 ญี่ปุ่น | `[\u3040-\u30FF\u4E00-\u9FFF]` |
| 🇨🇳 จีน | `[\u4E00-\u9FFF]` |
| 🇰🇷 เกาหลี | `[\uAC00-\uD7AF]` |
| 🌐 ตรวจว่าไม่ว่าง (Universal) | `text.strip()` แทนการใช้ regex |

> **หมายเหตุ:** ถ้าโปรเจคนั้นมีทั้งภาษาไทยและภาษาอังกฤษปนกันในช่องคำแปล
> (เช่น ชื่อเฉพาะที่ไม่แปล) ให้ใช้วิธี `text.strip()` แทนจะปลอดภัยกว่าครับ
