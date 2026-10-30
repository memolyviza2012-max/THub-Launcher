# STORY OF SEASONS: Grand Bazaar — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
STORY OF SEASONS: Grand Bazaar (originally Bokujō Monogatari: Yasuragi no Ki) is a farming simulation RPG originally for Nintendo DS, later ported to PC by Marvelous using the **Unity Engine** with the **Addressable Asset System**. The Thai localization mod uses a **Unity Addressable AssetBundle Replacement** architecture: 3 AssetBundle files replace the game's original font and text data. Two bundles contain TextMeshPro SDF font atlases (with Thai glyphs added), and one bundle contains 412 MonoBehaviour text data objects holding 886,509 Thai characters.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Unity Engine (with Addressable Asset System) |
| **Developer** | Marvelous (PC port) |
| **Archive Format** | `.bundle` (Unity AssetBundle, magic `UnityFS\x00`) |
| **AES Encryption** | No |
| **Compression** | Unity LZ4 (standard) |
| **Font System** | TextMeshPro (TMP) SDF Font Atlas |
| **Thai Font Used** | BO-SoftGoStd (Bosco Soft Gothic Std) — Japanese commercial font with Thai subset |
| **Font Variants** | DeBold (2,413 glyphs, 87 Thai) + Heavy (2,413 glyphs, 87 Thai) |
| **SDF Atlas Size** | 4096×4096 pixels (each) |
| **Text System** | MonoBehaviour objects (JSON-like structured data with Id/SubId/Text) |
| **Text Encoding** | UTF-8 (standard Unity) |
| **Mod Complexity** | ★★★☆☆ (TMP SDF atlas creation requires Unity Editor + TMP) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```text
SOSGrandBazaar_Data/StreamingAssets/aa/StandaloneWindows64/
├── 2e97b54ccbbce52fc2e2e82337969f37.bundle    (33.9 MB — TMP SDF Font: BO-SoftGoStd-DeBold)
│   ├── MonoBehaviour: TMP FontAsset (familyName='BO-SoftGoStd-DeBold_subset')
│   ├── Texture2D: SDF Atlas (4096×4096, format=Alpha8)
│   └── Material: TMP SDF Material
│
├── b3e2b521626326aa18ff75d1d3d21c2f.bundle    (33.9 MB — TMP SDF Font: BO-SoftGoStd-Heavy)
│   ├── MonoBehaviour: TMP FontAsset (familyName='BO-SoftGoStd-Heavy_subset')
│   ├── Texture2D: SDF Atlas (4096×4096, format=Alpha8)
│   └── Material: TMP SDF Material
│
└── 55a1190a0e2b33dd2e1ba5952a86e914.bundle    (4.4 MB — Text/Localization Data)
    ├── MonoBehaviour × 412 (text data objects)
    └── MonoScript × 1
```

---

## 4. Font Analysis

### 4.1 TextMeshPro SDF Architecture
เกมนี้ใช้ระบบ TextMeshPro (TMP) ของ Unity ซึ่งเรนเดอร์ฟอนต์ผ่าน **Signed Distance Field (SDF)** texture atlas — เทคนิคเดียวกับ Warhammer: Rogue Trader ในคลังความรู้

- **BO-SoftGoStd-DeBold_subset** (33.9 MB bundle):
  - Font Family: Bosco Soft Gothic Standard — ฟอนต์เชิงพาณิชย์ญี่ปุ่น (BO = Bosco)
  - Point Size: 30.0, Scale: 1.0
  - Glyphs: 2,413 total, **87 Thai characters**
  - SDF Atlas: 4096×4096 pixels, Alpha8 format

- **BO-SoftGoStd-Heavy_subset** (33.9 MB bundle):
  - Font Family: Bosco Soft Gothic Standard — Heavy weight
  - Point Size: 30.0, Scale: 1.0
  - Glyphs: 2,413 total, **87 Thai characters**
  - SDF Atlas: 4096×4096 pixels, Alpha8 format

### 4.2 Thai Coverage
ทั้ง 2 ฟอนต์มี 87 Thai characters — ครอบคลุมพยัญชนะไทยทั้ง 44 ตัว สระ วรรณยุกต์ และเครื่องหมายพิเศษ ครบถ้วนสำหรับการแสดงผลภาษาไทยทั่วไป

### 4.3 "_subset" Suffix
ชื่อฟอนต์ลงท้ายด้วย `_subset` แสดงว่าม็อดเดอร์ใช้ Unity Editor สร้าง TMP FontAsset ใหม่จากฟอนต์ BO-SoftGoStd โดยเลือกเฉพาะ character set ที่จำเป็น (CJK + Thai + Latin) เพื่อควบคุมขนาดของ SDF atlas

### 4.4 Font Extraction
ไม่มีไฟล์ TTF/OTF ต้นฉบับฝังอยู่ใน bundle — ดึงออกมาได้เฉพาะ SDF atlas images (PNG)

---

## 5. Text Analysis
- **Format:** Unity MonoBehaviour objects ภายใน AssetBundle — ข้อมูลมีโครงสร้างแบบ JSON-like:
  ```json
  {"Id": 2291010010, "SubId": 9005, "Text": "ากกก! ากกก!"}
  ```
- **Organization:** 412 MonoBehaviour objects ใน bundle เดียว แต่ละ object น่าจะแทน 1 หมวดข้อความ (e.g., dialogue, item descriptions, UI text)
- **สถิติ:**
  - 405 out of 412 MonoBehaviours contain Thai text (98.3% coverage)
  - **886,509 อักษรไทย** ทั้งหมด

---

## 6. Cross-Engine Comparison
เปรียบเทียบกับเกม Unity อื่นๆ ที่ใช้ TMP:

| Feature | SOS Grand Bazaar | Warhammer: Rogue Trader | Encased |
|---|---|---|---|
| **Font System** | TMP SDF Atlas | TMP SDF Atlas (PUA) | Standard TTF |
| **Asset Delivery** | Addressable AssetBundles | IL2CPP + DLL Bridge | resources.assets |
| **Font Name** | BO-SoftGoStd (Japanese) | Chakra Petch (Thai PUA) | Chakra Petch |
| **Thai Glyphs** | 87 per font | PUA-stacked | Native |
| **SDF Atlas** | 4096×4096 | Custom SDF | N/A |
| **Text Storage** | MonoBehaviour (structured) | SQLite + Blueprint JSON | TextAsset |
| **Complexity** | ★★★☆☆ | ★★★★☆ | ★★☆☆☆ |

สิ่งที่น่าสนใจ: SOS Grand Bazaar ใช้ TMP SDF **โดยไม่ต้อง PUA Stacking** — บ่งชี้ว่า Unity version ของเกมนี้อาจมี HarfBuzz/ICU integration ที่จัดการ Thai complex text shaping ได้โดยกำเนิด

---

## 7. Pipeline — ขั้นตอนสร้างม็อด

### Font Pipeline:
1. **เตรียม TTF ที่มี Thai:** ใช้ฟอนต์ที่รองรับ Thai (e.g., Noto Sans Thai, Google Sans)
2. **สร้าง TMP FontAsset ใน Unity Editor:**
   - Import TTF → Window > TextMeshPro > Font Asset Creator
   - ตั้ง Atlas Resolution: 4096×4096
   - Character Set: เลือก Custom Characters แล้วใส่ Thai range + CJK + Latin
   - Rendering Mode: SDF
3. **Build AssetBundle:** ใช้ Unity's Addressable Asset System หรือ legacy AssetBundle build
4. **ตั้งชื่อ bundle hash:** ต้องตรงกับชื่อ hash ดั้งเดิมของเกม

### Text Pipeline:
1. **แตก bundle:** ใช้ UnityPy load AssetBundle
2. **อ่าน MonoBehaviour:** ใช้ `read_typetree()` เพื่อดึง structured data
3. **แปล Text field:** แปลค่า "Text" ในแต่ละ entry
4. **เขียนกลับ:** ใช้ UnityPy save

---

## 8. Troubleshooting
- **ฟอนต์ไม่แสดงไทย:** ตรวจว่า TMP FontAsset มี Thai characters ครบ (อย่างน้อย 87 ตัว)
- **ตัวอักษรเป็นกล่อง/หายไป:** SDF atlas resolution อาจต่ำเกินไป — ใช้ 4096×4096
- **เกมไม่โหลด bundle:** ชื่อไฟล์ hash ต้องตรงกับ catalog ของ Addressable system — ถ้าเปลี่ยนชื่อเกมจะหา bundle ไม่เจอ
- **สระลอยตำแหน่งผิด:** TMP อาจต้องปรับ Glyph Adjustment ใน FontAsset

---

## 9. Required Tools
| Tool Name | Purpose | Source |
|---|---|---|
| Unity Editor + TMP | สร้าง TMP SDF FontAsset | [Unity Hub] |
| UnityPy | แตก/แก้ไข AssetBundles ด้วย Python | [UnityPy PyPI] |
| UABEA | GUI tool สำหรับ AssetBundle | [UABEA GitHub] |

---

## 10. Extracted Assets
- **SDF Atlas Images (extracted as PNG):**
  - [BO-SoftGoStd-DeBold_SDF_Atlas.png](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unity_Engine/Games/SOS_Grand_Bazaar/Assets/SDF_Atlas/BO-SoftGoStd-DeBold_SDF_Atlas.png) — 4096×4096 SDF atlas
  - [BO-SoftGoStd-Heavy_SDF_Atlas.png](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unity_Engine/Games/SOS_Grand_Bazaar/Assets/SDF_Atlas/BO-SoftGoStd-Heavy_SDF_Atlas.png) — 4096×4096 SDF atlas
- **Note:** No standalone TTF/OTF available. See [EXTRACTION_NOTE.txt](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unity_Engine/Games/SOS_Grand_Bazaar/Assets/Fonts/EXTRACTION_NOTE.txt)

---

## 11. M2M Protocol
**(สำหรับ AI Agent ที่ต้องการนำคัมภีร์ไปรันสร้างม็อดอัตโนมัติ)**

### 1. Automated Text Extractor/Injector
```python
import os
import json
import UnityPy

def extract_texts(bundle_path):
    """Extract all text entries from the text data bundle"""
    env = UnityPy.load(bundle_path)
    all_entries = []
    
    for obj in env.objects:
        if obj.type.name == 'MonoBehaviour':
            try:
                tree = obj.read_typetree()
                if 'list' in tree:
                    for entry in tree['list']:
                        if 'Text' in entry and 'Id' in entry:
                            all_entries.append({
                                'Id': entry['Id'],
                                'SubId': entry.get('SubId', 0),
                                'Text': entry['Text']
                            })
            except:
                pass
    
    return all_entries

def inject_texts(bundle_path, translations, output_path):
    """Inject translated text back into the bundle"""
    env = UnityPy.load(bundle_path)
    
    for obj in env.objects:
        if obj.type.name == 'MonoBehaviour':
            try:
                tree = obj.read_typetree()
                if 'list' in tree:
                    modified = False
                    for entry in tree['list']:
                        key = (entry.get('Id'), entry.get('SubId', 0))
                        if key in translations:
                            entry['Text'] = translations[key]
                            modified = True
                    if modified:
                        obj.save_typetree(tree)
            except:
                pass
    
    with open(output_path, 'wb') as f:
        f.write(env.file.save())
```

### 2. ข้อจำกัดสำหรับ AI
- **Text Pipeline:** ⚠️ AI อ่าน/แปล/เขียนกลับได้ผ่าน UnityPy แต่ต้องทดสอบว่า `save_typetree()` ทำงานถูกต้องกับ bundle version นี้
- **Font Pipeline:** ❌ AI ไม่สามารถสร้าง TMP SDF FontAsset ได้ — ต้องใช้ Unity Editor
- **Addressable System:** ⚠️ ชื่อไฟล์ hash ต้องตรงกับ catalog — ถ้าเกมอัปเดต hash อาจเปลี่ยน
