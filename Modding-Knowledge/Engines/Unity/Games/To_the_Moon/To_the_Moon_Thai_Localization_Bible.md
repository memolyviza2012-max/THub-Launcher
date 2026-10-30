# To the Moon (Serenity Forge Remaster) — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
*To the Moon* was originally developed using RPG Maker XP by Freebird Games. However, the version being modded here is the HD Remaster ported to the **Unity Engine** by Serenity Forge (and/or X.D. Network). The Thai localization mod architecture for this version is incredibly simple, relying entirely on Unity's built-in `TextAsset` files for text storage and Unity's OS font fallback system for Thai rendering.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Unity Engine (Ported from RPG Maker XP) |
| **Developer** | Serenity Forge / X.D. Network (Original by Freebird Games) |
| **Archive Format** | `.assets` (Standard Unity `resources.assets`) |
| **AES Encryption** | No |
| **Compression** | Standard Unity LZ4/LZMA (if any) |
| **Font System** | No font modding required (relies on Unity OS Fallback) |
| **Thai Font Used** | System default (e.g., Tahoma/Leelawadee on Windows) |
| **Text System** | Unity `TextAsset` (JSON/TXT format inside `.assets`) |
| **Text Encoding** | Standard UTF-8 |
| **Mod Complexity** | ★☆☆☆☆ (Extremely Simple) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
ม็อดนี้ประกอบด้วยไฟล์เพียงไฟล์เดียวที่ผู้เล่นต้องนำไปทับในโฟลเดอร์เกม:
```text
To the Moon/
└── To the Moon (SerenityForge)/
    └── To the Moon_Data/
        └── resources.assets      (122.7 MB — Unity resources archive)
```
**ภายใน `resources.assets` ประกอบด้วย:**
- ฟอนต์ต้นฉบับ 9 ไฟล์ (เช่น ARIAL, TIMES, LiberationSans, WenQuanYi Zen Hei) — *ไม่มีไฟล์ไหนถูกดัดแปลงให้รองรับภาษาไทยเลย*
- ไฟล์ `TextAsset` หลายไฟล์ โดยไฟล์หลักที่เก็บข้อความแปลภาษาไทยคือ:
  - `Maps_Loc` (3.8 MB) — ข้อความบทสนทนาทั้งหมดในแต่ละแผนที่
  - `Terms_Loc` (44 KB) — คำศัพท์ในเมนูและระบบเกม
  - `Actors_Loc`, `Items_Loc`, `CommonEvents_Loc` ฯลฯ

---

## 4. Font Analysis
- **ไม่จำเป็นต้องดัดแปลงฟอนต์!** นี่คือจุดเด่นของเอนจิน Unity เมื่อนักพัฒนาไม่ได้ล็อกฟอนต์ไว้อย่างเข้มงวด การเรนเดอร์ข้อความ (Text rendering) ของ Unity จะทำงานร่วมกับระบบปฏิบัติการ หากเกมพยายามแสดงอักษรไทย (U+0E00 - U+0E7F) แต่ไม่พบในฟอนต์หลัก Unity จะใช้ **OS Font Fallback** ดึงฟอนต์ภาษาไทยที่มีในเครื่อง (เช่น Tahoma) มาแสดงผลให้โดยอัตโนมัติ
- สระลอย วรรณยุกต์ซ้อน จึงแสดงผลได้อย่างสมบูรณ์แบบตามที่ OS จัดการให้ (Native complex text rendering) ไม่ต้องทำ PUA Stacking เหมือนเกม Warhammer Rogue Trader

---

## 5. Text Analysis
- **ไฟล์ TextAsset:** ข้อความในเกมถูกเก็บในรูปแบบ `TextAsset` ภายในไฟล์ `resources.assets` 
- **รูปแบบเนื้อหา:** คาดว่าเป็นโครงสร้าง JSON หรือ Text data แบบง่ายๆ ที่อิมพอร์ตมาจากฐานข้อมูลของ RPG Maker ดั้งเดิม
- **Encoding:** `UTF-8` รองรับภาษาไทยได้ทันทีเพียงแค่เปิดแก้และเซฟกลับเข้าไป

---

## 6. Cross-Engine Comparison
เปรียบเทียบกับเกม Unity อื่นๆ ใน Knowledge Base:

| Feature | To the Moon (Unity) | Encased (Unity) | Warhammer: Rogue Trader (Unity IL2CPP) |
|---|---|---|---|
| **Text Storage** | `resources.assets` (TextAsset) | `resources.assets` (TextAsset) | SQLite Database / Blueprint JSON |
| **Font Modding** | **None (OS Fallback)** | TTF Replacement (ChakraPetch) | TMP SDF Asset Modification (PUA) |
| **Thai Rendering** | Native OS Rendering | Native OS Rendering | PUA Stacking Script |
| **Complexity** | ★☆☆☆☆ | ★★☆☆☆ | ★★★★☆ |

*To the Moon* จัดว่าเป็นเกมที่ทำม็อดภาษาไทยได้ง่ายที่สุดในกลุ่ม Unity เพราะข้ามขั้นตอนการดัดแปลงฟอนต์ไปได้เลย

---

## 7. Pipeline — ขั้นตอนสร้างม็อด

1. **Unpack:** ใช้โปรแกรม Unity Asset Bundle Extractor (UABEA) หรือ UnityPy เปิดไฟล์ `resources.assets`
2. **Export:** ค้นหาไฟล์ประเภท `TextAsset` (เช่น `Maps_Loc`, `Terms_Loc`) แล้ว Export ออกมาเป็น `.txt`
3. **Translate:** เปิดไฟล์ `.txt` ด้วยโปรแกรม Text Editor (เช่น VSCode) แปลข้อความภาษาอังกฤษเป็นภาษาไทย แล้วบันทึกไฟล์เป็น `UTF-8`
4. **Import:** ใช้ UABEA Import ไฟล์ `.txt` ที่แปลแล้วกลับเข้าไปทับไฟล์เดิมใน `resources.assets`
5. **Save & Play:** บันทึกไฟล์ `resources.assets` นำไปวางทับในโฟลเดอร์เกม เข้าเล่นได้ทันที!

---

## 8. Troubleshooting
- **ข้อความภาษาไทยกลายเป็นสี่เหลี่ยม หรือมองไม่เห็น:**
  - ตรวจสอบว่าบันทึกไฟล์ TextAsset เป็น `UTF-8` (แบบไม่มี BOM) หรือไม่
  - (ในกรณีที่เล่นบนระบบปฏิบัติการอื่นเช่น Linux/Steam Deck) เครื่องนั้นอาจจะไม่มีฟอนต์ภาษาไทยติดตั้งอยู่ ทำให้ระบบ OS Fallback ของ Unity ทำงานไม่ได้ วิธีแก้คือต้องติดตั้งฟอนต์ภาษาไทยลงใน OS ของเครื่องนั้น

---

## 9. Required Tools
| Tool Name | Purpose | Source |
|---|---|---|
| UABEA (Unity Asset Bundle Extractor) | ใช้แตกไฟล์และนำเข้า `TextAsset` | [UABEA GitHub] |
| Text Editor (VS Code / Notepad++) | ใช้แปลข้อความและจัดการ UTF-8 | [VS Code] |

---

## 10. Extracted Assets
- **ไม่มีการนำออกฟอนต์ใดๆ:** เนื่องจากไฟล์ต้นฉบับไม่ได้มีการดัดแปลงฟอนต์ ดูรายละเอียดเพิ่มเติมใน `Assets/Fonts/EXTRACTION_NOTE.txt`
- นำออกไฟล์ **TextAsset** ไว้เป็นตัวอย่าง:
  - `Assets/Text/Maps_Loc.txt`
  - `Assets/Text/Terms_Loc.txt`

---

## 11. M2M Protocol
**(สำหรับ AI Agent ที่ต้องการนำคัมภีร์ไปรันสร้างม็อดอัตโนมัติ)**

AI สามารถทำม็อดเกมนี้ได้ 100% ด้วย Python Script และ `UnityPy` โดยไม่ต้องใช้ GUI tool เลย

### 1. Automated Text Extractor
```python
import os
import UnityPy

def extract_texts(assets_path, output_dir):
    env = UnityPy.load(assets_path)
    os.makedirs(output_dir, exist_ok=True)
    
    for obj in env.objects:
        if obj.type.name == 'TextAsset':
            data = obj.read()
            name = getattr(data, 'm_Name', getattr(data, 'name', 'UnknownText'))
            
            # Handle both string and bytes
            script_data = data.m_Script
            if isinstance(script_data, str):
                text_bytes = script_data.encode('utf-8')
            else:
                text_bytes = bytes(script_data)
                
            out_path = os.path.join(output_dir, f'{name}.txt')
            with open(out_path, 'wb') as f:
                f.write(text_bytes)
            print(f"Extracted {name}")
```

### 2. Automated Text Injector
```python
import os
import UnityPy

def inject_texts(assets_path, translated_dir, output_assets_path):
    env = UnityPy.load(assets_path)
    
    for obj in env.objects:
        if obj.type.name == 'TextAsset':
            data = obj.read()
            name = getattr(data, 'm_Name', getattr(data, 'name', 'UnknownText'))
            
            in_path = os.path.join(translated_dir, f'{name}.txt')
            if os.path.exists(in_path):
                with open(in_path, 'rb') as f:
                    new_bytes = f.read()
                
                # UnityPy: if the original was string, assign string. If bytes, assign bytes.
                if isinstance(data.m_Script, str):
                    data.m_Script = new_bytes.decode('utf-8')
                else:
                    data.m_Script = new_bytes
                    
                data.save()
                print(f"Injected translation into {name}")
                
    with open(output_assets_path, 'wb') as f:
        f.write(env.file.save())
```
