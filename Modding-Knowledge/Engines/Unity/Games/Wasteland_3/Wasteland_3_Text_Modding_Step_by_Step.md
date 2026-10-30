# คู่มือจับมือทำ: การเจาะไฟล์ข้อความและแพ็กกลับ (Wasteland 3)

เอกสารฉบับนี้คือ "คู่มือจับมือทำ (Step-by-Step Guide)" สำหรับการดึงข้อความเกม Wasteland 3 ออกมาแปล และแพ็กกลับเข้าไปในเกมแบบละเอียดที่สุด เพื่อให้มนุษย์ที่ไม่มีพื้นฐานโปรแกรมมิ่งสามารถทำตามและเข้าใจหลักการทำงานได้

---

## 🛠️ สิ่งที่ต้องเตรียม (Prerequisites)
1. ติดตั้งโปรแกรม **Python** ในเครื่อง
2. ติดตั้งไลบรารีที่จำเป็น เปิด Command Prompt (หรือ PowerShell) แล้วพิมพ์คำสั่ง:
   `pip install UnityPy`
3. ต้องมีโปรแกรมจัดการการแปล (ในที่นี้เราอิงตามมาตรฐาน **THub / TStudio** ของ Modder Hub)

---

## 🔍 ขั้นตอนที่ 1: การตามล่าหาไฟล์ข้อความ (Find the Target)

เกมที่สร้างด้วย Unity มักจะเก็บข้อความไว้ในโฟลเดอร์เกมที่ชื่อว่า `*Data\StreamingAssets\`
สำหรับ Wasteland 3 เราพบว่าไฟล์ข้อความทั้งหมดถูกรวมไว้ในไฟล์นามสกุล `.bundle` 

**ที่อยู่ไฟล์ต้นฉบับ:**
`[โฟลเดอร์เกม]\WL3_Data\StreamingAssets\aa\StandaloneWindows64\oei_assets_stringtabledata_english_e4607_...bundle`

> [!TIP]
> **ข้อแนะนำ:** ให้ Copy ไฟล์ `.bundle` นี้ออกมาเก็บไว้ในโฟลเดอร์ทำงานของเราก่อน (ตั้งชื่อโฟลเดอร์ว่า `01_Original_Backup`) อย่าแก้ไขไฟล์ต้นฉบับในเกมตรงๆ เด็ดขาด!

---

## 🔓 ขั้นตอนที่ 2: การเจาะไฟล์ (Unpack) เพื่อดึงข้อความ

เราจะใช้เขียนสคริปต์ Python เล็กๆ เพื่อเปิดไฟล์ Bundle และดึงข้อความออกมาเป็นตาราง Excel (CSV) สคริปต์นี้ตั้งชื่อว่า `Wasteland3_unpacker.py`

### โค้ดสำหรับ Unpack (ดึงข้อความ)
```python
import os
import csv
import UnityPy

def unpack_localization(bundle_path, output_csv):
    # 1. สั่งให้ UnityPy โหลดไฟล์ Bundle ของเกม
    env = UnityPy.load(bundle_path)
    entries = []
    
    # 2. ค้นหาชิ้นส่วน (Object) ที่ชื่อว่า "StringTableData_English"
    for obj in env.objects:
        if obj.type.name == "MonoBehaviour":
            tree = obj.read_typetree()
            if tree.get("m_Name") == "StringTableData_English":
                
                # 3. พอเจอแล้ว ก็ดึงข้อมูลตารางข้อความทั้งหมดออกมา
                for table in tree.get("stringTables", []):
                    filename = table.get("Filename", "")
                    entry_ids = table.get("entryIDs", [])
                    default_texts = table.get("defaultTexts", [])
                    female_texts = table.get("femaleTexts", [])
                    
                    # 4. นำข้อมูลมาจับคู่กัน (ID คู่กับ ข้อความ)
                    for i in range(len(entry_ids)):
                        entry_id = entry_ids[i]
                        text = default_texts[i] if i < len(default_texts) else ""
                        female_text = female_texts[i] if i < len(female_texts) else ""
                        
                        if text:
                            key = f"{filename}::{entry_id}::default"
                            entries.append((key, text))
                        if female_text:
                            key_f = f"{filename}::{entry_id}::female"
                            entries.append((key_f, female_text))
                            
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    
    # 5. สร้างไฟล์ CSV ตามมาตรฐานของ TStudio (สำคัญมาก: ต้องใช้ utf-8-sig)
    with open(output_csv, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        # หัวคอลัมน์ต้องเป๊ะตามนี้เท่านั้น
        writer.writerow(['ID', 'Source', 'Translation', 'AI_Reference'])
        for key, original in entries:
            writer.writerow([key, original.replace('\r', ''), '', ''])

# วิธีรัน:
BUNDLE_PATH = r"E:\Mod_Workspace\Wasteland_3\01_Original_Backup\oei_assets_stringtabledata_english...bundle"
OUTPUT_CSV = r"E:\Mod_Workspace\Wasteland_3\02_Translation_Workspace\Wasteland3_Strings.csv"
unpack_localization(BUNDLE_PATH, OUTPUT_CSV)
```
**สิ่งที่คุณจะได้:** ไฟล์ `Wasteland3_Strings.csv` ที่มีข้อความกว่า 80,000 บรรทัด รอให้คุณนำไปแปล!

---

## 📝 ขั้นตอนที่ 3: การแปลข้อความ (Translate)
นำไฟล์ `Wasteland3_Strings.csv` ไปเปิดใน **TStudio** หรือ **TRun** เพื่อทำการแปล เมื่อแปลเสร็จเราจะได้ไฟล์ที่แปลแล้ว (สมมติชื่อ `Wasteland3_Strings_translated.csv`)

---

## 📦 ขั้นตอนที่ 4: การแพ็กข้อความกลับเข้าเกม (Pack)

ขั้นตอนนี้คือการนำไฟล์ CSV ที่เราแปลเสร็จแล้ว ไปยัดกลับเข้าไฟล์ `.bundle` ตัวเดิม **จุดที่สำคัญที่สุดคือการแปลงสระภาษาไทยให้เป็น PUA (สระลอย)** ก่อนยัดเข้าเกม! เราจะใช้สคริปต์ชื่อ `Wasteland3_packer.py`

### โค้ดสำหรับ Pack (ยัดข้อความ)
```python
import os
import sys
import csv
import UnityPy

# 1. โหลดเครื่องมือแก้สระลอย (PUA Engine) จาก Modder Hub
THUB_PATH = r"E:\Mod_Workspace\Modder_project\modder-hub\tools\flagship"
sys.path.append(THUB_PATH)
try:
    from Core.tpua_engine import TPUAEngine
    pua = TPUAEngine()
    def convert_to_pua(text): return pua.encode(text) # ฟังก์ชันแปลงสระลอย
except ImportError:
    def convert_to_pua(text): return text

def pack_localization(csv_path, bundle_path, output_bundle_path):
    # 2. อ่านไฟล์ CSV ที่เราแปลเสร็จแล้ว
    translations = {}
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = row.get('ID', '')
            trans = row.get('Translation', '').strip()
            if not trans:
                continue
                
            # แปลงข้อความไทยธรรมดา ให้เป็นข้อความ PUA (แก้สระจม/ทับ)
            translations[key] = convert_to_pua(trans)

    # 3. เปิดไฟล์ Bundle ต้นฉบับขึ้นมาเตรียมแก้ไข
    env = UnityPy.load(bundle_path)
    modified = False
    
    for obj in env.objects:
        if obj.type.name == "MonoBehaviour":
            tree = obj.read_typetree()
            if tree.get("m_Name") == "StringTableData_English":
                
                # 4. ค้นหาข้อความเดิม แล้วเอาข้อความใหม่(ที่แปลและเป็น PUA แล้ว) ไปทับ
                for table in tree.get("stringTables", []):
                    filename = table.get("Filename", "")
                    entry_ids = table.get("entryIDs", [])
                    default_texts = table.get("defaultTexts", [])
                    female_texts = table.get("femaleTexts", [])
                    
                    for i in range(len(entry_ids)):
                        entry_id = entry_ids[i]
                        
                        key = f"{filename}::{entry_id}::default"
                        if key in translations:
                            default_texts[i] = translations[key] # แทนที่!
                            
                        key_f = f"{filename}::{entry_id}::female"
                        if key_f in translations:
                            female_texts[i] = translations[key_f] # แทนที่!
                
                # 5. บันทึกการเปลี่ยนแปลงกลับเข้าไปใน Object
                obj.save_typetree(tree)
                modified = True
            
    # 6. เซฟไฟล์ Bundle ตัวใหม่ออกมา (พร้อมนำไปใช้)
    if modified:
        os.makedirs(os.path.dirname(output_bundle_path), exist_ok=True)
        with open(output_bundle_path, 'wb') as f:
            f.write(env.file.save())

# วิธีรัน:
CSV_PATH = r"E:\Mod_Workspace\Wasteland_3\02_Translation_Workspace\Wasteland3_Strings_translated.csv"
BUNDLE_PATH = r"E:\Mod_Workspace\Wasteland_3\01_Original_Backup\oei_assets_stringtabledata_english...bundle"
OUTPUT_BUNDLE = r"E:\Mod_Workspace\Wasteland_3\04_Packed_Mod\oei_assets_stringtabledata_english...bundle"
pack_localization(CSV_PATH, BUNDLE_PATH, OUTPUT_BUNDLE)
```

---

## 🎮 ขั้นตอนที่ 5: การติดตั้งและทดสอบ (Deploy)

1. นำไฟล์ `.bundle` ใหม่ที่ได้จากขั้นตอนที่ 4 (อยู่ในโฟลเดอร์ `04_Packed_Mod`)
2. คัดลอกไปวางทับไฟล์เดิมในโฟลเดอร์เกม: `[โฟลเดอร์เกม]\WL3_Data\StreamingAssets\aa\StandaloneWindows64\`
3. เข้าเกม! ตัวเกมจะอ่านข้อความจากไฟล์ที่เราดัดแปลง และแสดงผลภาษาไทยที่มีสระลอยสวยงามผ่านฟอนต์ที่เรา Mod ไว้ครับ
