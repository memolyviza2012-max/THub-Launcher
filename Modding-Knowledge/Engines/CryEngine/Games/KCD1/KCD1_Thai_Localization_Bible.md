# Kingdom Come: Deliverance — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Kingdom Come: Deliverance is a historical action RPG developed by **Warhorse Studios** using **CryEngine** (modified). The Thai localization mod (v0.8.1.0 by Helious, created 14 Feb 2026) uses the same **CryEngine Mod Pak** architecture as its sequel KCD2 — Scaleform GFx font library + XML localization. However, KCD1 has a simpler mod structure with no font style options, a single glyph atlas (22 MB — the largest single GFx file in the Knowledge Base), and a standard KCD mod manifest.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | CryEngine (Modified by Warhorse Studios) |
| **Developer** | Warhorse Studios |
| **Mod Name** | ThaiLanguageBetaTest v0.8.1.0 (by Helious) |
| **Supported Version** | KCD 1.9.* |
| **Archive Format** | `.pak` (CryEngine = **standard ZIP**, magic `PK\x03\x04`) |
| **AES Encryption** | No |
| **Compression** | ZIP (Deflate) |
| **Font System** | Scaleform GFx (`.gfx` = zlib-compressed SWF, magic `CFX`) |
| **Font Slots** | `CommentFont` → linked to `gfxfontlib_glyphs` |
| **Text System** | XML (plain UTF-8) |
| **Text Encoding** | UTF-8 |
| **Mod Complexity** | ★★★☆☆ (Same as KCD2 — Scaleform GFx font creation is the hard part) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```text
Kingdom Come 1/
├── mod.manifest                          (379B — KCD mod descriptor XML)
├── Data/
│   └── GameData.pak                      (21.2 MB — ZIP containing GFx font files)
│       ├── Libs/UI/gfxfontlib.gfx        (1.7 KB — Font definition library)
│       └── Libs/UI/gfxfontlib_glyphs.gfx (22.2 MB — Glyph atlas, MASSIVE!)
└── Localization/
    └── English_xml.pak                   (4.8 MB — ZIP containing translated XML files)
        ├── text_ui_dialog.xml            (17.2 MB — 197,946 entries, 2.47M Thai chars)
        ├── text_ui_quest.xml             (2.4 MB — 18,876 entries, 459K Thai chars)
        ├── text_ui_menus.xml             (1.2 MB — 9,222 entries, 77K Thai chars)
        ├── text_ui_items.xml             (1.1 MB — 7,914 entries, 203K Thai chars)
        ├── text_ui_soul.xml              (392 KB — 5,472 entries, 56K Thai chars)
        ├── text_ui_tutorials.xml         (130 KB — 447 entries, 22K Thai chars)
        ├── text_ui_ingame.xml            (108 KB — 2,343 entries, 10K Thai chars)
        ├── text_ui_misc.xml              (74 KB — 444 entries, 14K Thai chars)
        ├── text_ui_minigames.xml         (26 KB — 393 entries, 3.8K Thai chars)
        ├── text_rich_presence.xml        (1.7 KB — 36 entries, 179 Thai chars)
        └── text_ui_HUD.xml              (225B — 6 entries, 16 Thai chars)
```

### mod.manifest:
```xml
<kcd_mod>
  <info>
    <name>ThaiLanguageBetaTest</name>
    <description>For Testing Thai Font added and some translated</description>
    <author>Helious</author>
    <version>0.8.1.0</version>
    <created_on>14 February 2026</created_on>
  </info>
  <supports>
    <kcd_version>1.9.*</kcd_version>
  </supports>
</kcd_mod>
```

---

## 4. Font Analysis

### 4.1 Scaleform GFx — เหมือน KCD2 แต่ง่ายกว่า
KCD1 ใช้ระบบ Scaleform GFx เหมือน KCD2 เป๊ะ แต่มีโครงสร้างที่เรียบง่ายกว่า:
- **gfxfontlib.gfx** (1.7 KB): เล็กมากเมื่อเทียบกับ KCD2 (67 KB) — กำหนดแค่ `CommentFont` → link ไปยัง `gfxfontlib_glyphs`
- **gfxfontlib_glyphs.gfx** (22.2 MB): ใหญ่กว่า KCD2 (Modern 3.1 MB / Ancient 5.4 MB) ถึง **4-7 เท่า!** สาเหตุน่าจะเป็นเพราะ glyph atlas มี character coverage กว้างกว่าหรือมี detail สูงกว่า
- **Magic:** `CFX` (Compressed Flash eXtended) — zlib-compressed SWF

### 4.2 Comparison with KCD2
| Feature | KCD1 | KCD2 |
|---|---|---|
| gfxfontlib.gfx | 1.7 KB | 67 KB |
| gfxfontlib_glyphs.gfx | 22.2 MB (1 style) | 3.1-5.4 MB (2 styles) |
| Font style options | None | Modern / Ancient |
| Font slots defined | `CommentFont` | DefaultFont, LightFont, DisplayFont + Bold/Italic |
| Same gfxfontlib? | No (different MD5) | — |

### 4.3 Font Extraction
เช่นเดียวกับ KCD2 ฟอนต์ถูกเก็บในรูป Scaleform GFx vector — ไม่สามารถแยกออกมาเป็น TTF/OTF ได้โดยตรง ดึงออกมาได้เฉพาะไฟล์ `.gfx` ทั้ง set

---

## 5. Text Analysis
- **Format:** Plain XML (UTF-8) — โครงสร้างเดียวกับ KCD2 ทุกประการ
- **Structure:** Key + English + Thai ใน 3 Cells:
  ```xml
  <Row>
    <Cell>buff_agility_potion_desc_t</Cell>
    <Cell>Your joints and muscles have stopped troubling you.&lt;br/&gt;&amp;nbsp;&lt;br/&gt;Agility +5&lt;br/&gt;Defence +5</Cell>
    <Cell>ข้อต่อและกล้ามเนื้อของคุณไม่ทำให้คุณหนักใจ&lt;br/&gt;&amp;nbsp;&lt;br/&gt;ความคล่องตัว +5&lt;br/&gt;การป้องกัน +5</Cell>
  </Row>
  ```
- **สถิติ:**
  - **3,314,378 อักษรไทย** (อันดับ 2 ตลอดกาล รองจาก KCD2!)
  - **243,099 entries**
  - `text_ui_dialog.xml` เพียงไฟล์เดียวมี 197,946 entries กับ 2.47M Thai characters
- **คุณภาพแปล:** ม็อดเดอร์ระบุว่าเป็น "Beta Test" (v0.8.1.0) แต่จำนวน Thai characters บ่งบอกว่าแปลเกือบครบถ้วนแล้ว

---

## 6. Cross-Engine Comparison
เปรียบเทียบสองภาคของ Kingdom Come:

| Feature | KCD1 | KCD2 |
|---|---|---|
| **Engine** | CryEngine | CryEngine (Modified) |
| **Pak Format** | ZIP (PK) | ZIP (PK) |
| **Font System** | Scaleform GFx | Scaleform GFx |
| **Text Format** | XML (UTF-8) | XML (UTF-8) |
| **Mod System** | `mod.manifest` + `mods/` folder | `mods/` folder |
| **Font Styles** | 1 (single) | 2 (Modern / Ancient) |
| **Thai Characters** | 3.31M | 5.17M 🏆 |
| **Entries** | 243K | 611K |
| **Glyphs GFx Size** | 22.2 MB | 3.1-5.4 MB |
| **Complexity** | ★★★☆☆ | ★★★☆☆ |

ทั้งสองภาคใช้สถาปัตยกรรมเหมือนกันเป๊ะ — ม็อดเดอร์ที่ทำภาคหนึ่งได้สามารถทำอีกภาคได้ทันทีโดยไม่ต้องเรียนรู้เพิ่ม

---

## 7. Pipeline — ขั้นตอนสร้างม็อด

### Font Pipeline:
1. **สร้าง GFx SpriteFont:** ใช้ Scaleform SDK หรือ Adobe Flash + GFx Exporter
2. **กำหนด `CommentFont`** ให้ link ไปยัง `gfxfontlib_glyphs`
3. **Pack เป็น ZIP:** `Libs/UI/gfxfontlib.gfx` + `Libs/UI/gfxfontlib_glyphs.gfx` → `GameData.pak`

### Text Pipeline:
1. **แตก `English_xml.pak`:** ใช้ Python zipfile (เพราะ .pak = ZIP)
2. **แก้ XML:** แปลข้อความใน Cell ที่ 3
3. **Pack กลับ:** บีบเป็น `English_xml.pak`

### Mod Manifest:
```xml
<?xml version="1.0" encoding="utf-8"?>
<kcd_mod>
  <info>
    <name>ThaiLanguage</name>
    <description>Thai localization mod</description>
    <author>YourName</author>
    <version>1.0.0.0</version>
    <created_on>2026</created_on>
  </info>
  <supports>
    <kcd_version>1.9.*</kcd_version>
  </supports>
</kcd_mod>
```

### Deployment:
```
GameFolder/mods/thaimod/
├── mod.manifest
├── Data/GameData.pak
└── Localization/English_xml.pak
```

---

## 8. Troubleshooting
- **เกมไม่โหลดม็อด:** ตรวจว่ามีไฟล์ `mod.manifest` อยู่ใน root ของโฟลเดอร์ม็อด และ `<kcd_version>` ตรงกับเวอร์ชันเกม
- **ฟอนต์ไม่แสดงไทย:** ตรวจว่า `GameData.pak` มีไฟล์ `.gfx` ทั้งสองตัวครบ
- **ข้อความยังเป็นอังกฤษ:** ตรวจว่า `English_xml.pak` อยู่ใน `Localization/` (ไม่ใช่ `Data/`)
- **Crash เมื่อเปิดเกม:** `gfxfontlib_glyphs.gfx` ขนาดใหญ่ (22 MB) อาจโหลดช้า — รอสักครู่

---

## 9. Required Tools
| Tool Name | Purpose | Source |
|---|---|---|
| 7-Zip / Python zipfile | แตกและสร้าง `.pak` (ZIP format) | [7-Zip.org] |
| Scaleform GFx SDK | สร้าง/แก้ GFx SpriteFont | [Autodesk] |
| Text Editor (VS Code) | แก้ XML (UTF-8) | [VS Code] |

---

## 10. Extracted Assets
- **Font GFx files:**
  - [gfxfontlib.gfx](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/CryEngine/Games/KCD1/Assets/Fonts/gfxfontlib.gfx) — Font definition (1.7 KB)
  - [gfxfontlib_glyphs.gfx](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/CryEngine/Games/KCD1/Assets/Fonts/gfxfontlib_glyphs.gfx) — Glyph atlas (22.2 MB — largest single font asset in KB!)

---

## 11. M2M Protocol
**(สำหรับ AI Agent ที่ต้องการนำคัมภีร์ไปรันสร้างม็อดอัตโนมัติ)**

AI สามารถใช้ pipeline เดียวกับ KCD2 ได้ทุกประการ (ดูคัมภีร์ KCD2) แต่มีข้อแตกต่าง:

### 1. KCD1 Mod Builder (reuse KCD2 pipeline)
```python
import zipfile
import os

def build_kcd1_mod(translated_xml_dir, font_gfx_dir, output_mod_dir):
    """Build KCD1 Thai mod"""
    os.makedirs(output_mod_dir, exist_ok=True)
    
    # Create mod.manifest
    manifest = '''<?xml version="1.0" encoding="utf-8"?>
<kcd_mod>
  <info>
    <name>ThaiLanguage</name>
    <description>Thai localization</description>
    <author>AI-Generated</author>
    <version>1.0.0.0</version>
  </info>
  <supports>
    <kcd_version>1.9.*</kcd_version>
  </supports>
</kcd_mod>'''
    with open(os.path.join(output_mod_dir, 'mod.manifest'), 'w', encoding='utf-8') as f:
        f.write(manifest)
    
    # Build Localization pak
    loc_pak = os.path.join(output_mod_dir, 'Localization', 'English_xml.pak')
    os.makedirs(os.path.dirname(loc_pak), exist_ok=True)
    with zipfile.ZipFile(loc_pak, 'w', zipfile.ZIP_DEFLATED) as z:
        for fname in os.listdir(translated_xml_dir):
            z.write(os.path.join(translated_xml_dir, fname), fname)
    
    # Build Font pak (GameData.pak, NOT ThaiFont.pak like KCD2!)
    font_pak = os.path.join(output_mod_dir, 'Data', 'GameData.pak')
    os.makedirs(os.path.dirname(font_pak), exist_ok=True)
    with zipfile.ZipFile(font_pak, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(font_gfx_dir):
            for fname in files:
                fpath = os.path.join(root, fname)
                arcname = os.path.relpath(fpath, font_gfx_dir)
                z.write(fpath, arcname)
```

### 2. ข้อแตกต่างจาก KCD2
- **Mod manifest:** KCD1 ต้องมี `mod.manifest` ในรูท, KCD2 ไม่ต้อง
- **Font pak name:** KCD1 ใช้ `GameData.pak`, KCD2 ใช้ `ThaiFont.pak`
- **Font definition:** KCD1 ใช้ `CommentFont`, KCD2 ใช้ DefaultFont/LightFont/DisplayFont

### 3. ข้อจำกัดสำหรับ AI
- **Text Pipeline:** ✅ AI ทำได้ 100% — XML + ZIP เหมือน KCD2
- **Font Pipeline:** ❌ ต้องใช้ Scaleform SDK (เหมือน KCD2)
- **Pak Pipeline:** ✅ AI ทำได้ 100% — ZIP format
