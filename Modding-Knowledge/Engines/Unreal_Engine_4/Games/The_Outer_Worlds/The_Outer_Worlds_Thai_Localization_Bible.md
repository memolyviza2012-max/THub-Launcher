# The Outer Worlds — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
The Outer Worlds is an action RPG developed by **Obsidian Entertainment** using **Unreal Engine 4**. The Thai localization mod uses an **Asset Override** architecture packed into a standard UE4 `.pak` file. Unlike modern UE4 games that use `.locres` for localization, Obsidian opted for an older / custom pipeline compiling localizations into `.uasset` + `.uexp` (String Tables/Data Tables) directly. The font system uses the classic UE4 **Font Flooding** technique.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Unreal Engine 4 (Project "Indiana") |
| **Developer** | Obsidian Entertainment |
| **Mod Author** | ไม่ระบุ (จากโฟลเดอร์ 0_Rivet Engineer) |
| **Archive Format** | `.pak` (UE4 standard, ไม่มี AES) |
| **Font System** | `.ufont` (Raw TTF) |
| **Thai Font** | Avenir Next World Medium (ดัดแปลงเพิ่มภาษาไทย) |
| **Text System** | `.uasset` + `.uexp` (UE4 String Tables) |
| **Text Encoding** | UTF-16LE |
| **Mod Complexity** | ★★★☆☆ (UE4 String Table editing) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
แพ็คเกจม็อดถูกบีบอัดมาในไฟล์เดียวชื่อ `TH-WindowsNoEditor.pak` (5.5 MB) เมื่อแตกไฟล์ออกมาจะพบโครงสร้างดังนี้:

```text
TH-WindowsNoEditor.pak
└── Indiana/Content/
    ├── Exported/                      (หมวดข้อความ - Text)
    │   ├── BaseGame/Localized/EN/Text/
    │   │   ├── Text_en.uasset
    │   │   └── Text_en.uexp           (12.7 MB - เกมหลัก)
    │   ├── INX1/Localized/EN/Text/
    │   │   ├── Text_en.uasset
    │   │   └── Text_en.uexp           (3.0 MB - DLC 1: Peril on Gorgon)
    │   └── INX2/Localized/EN/Text/
    │       ├── Text_en.uasset
    │       └── Text_en.uexp           (3.4 MB - DLC 2: Murder on Eridanos)
    │
    └── UI/Library/Font/               (หมวดฟอนต์ - Font Flooding)
        ├── DroidSansFallback.ufont    (640 KB - Avenir Next World Medium)
        ├── Font2_0_Light.ufont        (640 KB - Avenir Next World Medium)
        ├── Font2_0_Regular.ufont      (640 KB - Avenir Next World Medium)
        ├── TCM_Regular.ufont          (640 KB - Avenir Next World Medium)
        ├── Font2_0_Bold.ufont         (642 KB - Avenir Next World Bold)
        ├── OBSTOW_Bold.ufont          (642 KB - Avenir Next World Bold)
        └── TCM_Bold.ufont             (642 KB - Avenir Next World Bold)
```

---

## 4. Font Analysis

### 4.1 Font Flooding
เหมือน UE4 ทั่วไป ไฟล์ `.ufont` ของ The Outer Worlds เป็นไฟล์ **Raw TTF** 100% 
ม็อดเดอร์ใช้วิธี **Font Flooding** โดยเอาฟอนต์ไทยไปสวมทับชื่อฟอนต์ทั้งหมด 7 สล็อตที่เกมใช้งาน แบ่งเป็น 2 Weights หลักๆ คือ:
- **Regular (Hash: 0d50a9db):** ฟอนต์ **Avenir Next World Medium** (ดัดแปลงยัดอักขระไทย)
- **Bold (Hash: 88e337f2):** ฟอนต์ตัวหนา 

วิธีนี้ทำให้เกมไม่ต้องพึ่งพา Font Material หรือ Asset Bundle ใหม่ แค่ให้เครื่องอ่าน TTF ที่ม็อดเดอร์เตรียมไว้ให้แทน

---

## 5. Text Analysis

### 5.1 Obsidian's `.uexp` String Tables (Not `.locres`)
จุดเด่นที่ทำให้เกมนี้แตกต่างจาก Borderlands 3 หรือ Midnight Suns คือ **ไม่ได้ใช้ `.locres`**
- ข้อความทั้งหมดถูกคอมไพล์ลงใน **String Tables (`.uasset` + `.uexp`)** ซึ่งเป็นฟอร์แมตดั้งเดิมของ Unreal 
- การเข้ารหัสสตริงยังคงใช้ **UTF-16LE** (บ่งบอกด้วยความยาวสตริงที่ติดลบตามสเปคของ UAsset)

### 5.2 สถิติข้อความ 
(นับเฉพาะอักขระไทย `U+0E00` ถึง `U+0E7F` ในโครงสร้าง UTF-16LE)
- **Base Game:** 793,162 chars
- **INX1 (Peril on Gorgon):** 208,207 chars
- **INX2 (Murder on Eridanos):** 234,049 chars
- **Total Thai Chars:** **1,235,418 Characters** (รวมทั้งเกมและ DLC)

*(อยู่อันดับ 5 ของฐานข้อมูลเกมที่มีข้อความไทยเยอะที่สุด)*

---

## 6. Cross-Engine Comparison
เปรียบเทียบในหมวด Unreal Engine 4:

| Feature | The Outer Worlds | Midnight Suns | Borderlands 3 |
|---|---|---|---|
| **Engine** | UE4 | UE4 (Coda) | UE4 |
| **Font Format** | .ufont (TTF) | .ufont (TTF) | .ufont (TTF) |
| **Text Format** | **.uasset + .uexp** | .locres | .locres |
| **Text Encoding** | UTF-16LE | UTF-16LE | UTF-16LE |
| **Thai Chars** | 1.23 Million | 1.79 Million | 1.52 Million |
| **Complexity** | ★★★☆☆ | ★★☆☆☆ | ★★☆☆☆ |

**จุดแข็ง:** การรวบรวม text ไว้ใน uexp เพียง 3 ไฟล์ (เกมหลัก + 2 DLC) ทำให้แก้ไขง่ายกว่าเกมที่กระจาย uexp ไปทุกแผนที่ 
**จุดอ่อน:** การแก้ `.uexp` ทำได้ยากกว่า `.locres` เพราะต้องรักษาระยะ Offset ให้เป๊ะ หรือใช้โปรแกรม UAssetAPI/UAssetGUI ในการ Rebuild ซึ่งยุ่งยากกว่าโปรแกรมแปลง Locres สำเร็จรูป

---

## 7. Pipeline — ขั้นตอนสร้างม็อด

1. **Text Extraction:** ใช้ `UAssetGUI` หรือสคริปต์ `UAssetAPI` เปิดไฟล์ `Text_en.uasset` และทำการ Export เป็น JSON
2. **Translation:** แปลไฟล์ JSON
3. **Text Re-packing:** Import กลับเข้า `UAssetGUI` เพื่อสร้างไฟล์ `.uexp` ฉบับแปลไทย โดยตัวโปรแกรมจะคำนวณ Name Map และ String Offset ให้ใหม่
4. **Font Flooding:** โคลน TTF ภาษาไทยเป็น 7 ชื่อ (.ufont) ไปวางทับโฟลเดอร์ Font ของ UI เกม
5. **Pak Generation:** ใช้โปรแกรม `UnrealPak` หรือ `repak` คอมไพล์โฟลเดอร์เป็น `TH-WindowsNoEditor.pak`
6. **Deployment:** วางไฟล์ pak ลงใน `Indiana/Content/Paks/~mods` หรือ `Paks/` ตรงๆ ก็ได้ (ขึ้นอยู่กับ Mod Loader ของเกม)

---

## 8. Required Tools
| Tool Name | Purpose | Source |
|---|---|---|
| repak / UnrealPak | Pack/Unpack ไฟล์ `.pak` | [repak GitHub] |
| UAssetGUI / UAssetAPI | ดึงข้อความจาก String Tables `.uasset` | [GitHub] |
| Font Editor | แก้ไขฟอนต์ TTF ก่อนนำไป Flood | [FontForge] |

---

## 9. Extracted Assets
- **Avenir Next World (.ttf) ที่เตรียมการเพิ่มภาษาไทยแล้ว:**
  - [Font_Regular.ttf](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unreal_Engine_4/Games/The_Outer_Worlds/Assets/Fonts/Font_Regular.ttf) (640 KB)
  - [Font_Bold.ttf](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unreal_Engine_4/Games/The_Outer_Worlds/Assets/Fonts/Font_Bold.ttf) (642 KB)

---

## 10. M2M Protocol
**(สำหรับ AI Agent ที่ต้องการนำคัมภีร์ไปรันสร้างม็อดอัตโนมัติ)**

### ข้อจำกัดสำหรับ AI
- **Text Translation:** ⚠️ AI สามารถอ่านและแปลเนื้อหาได้ **แต่** ไม่สามารถแก้ Binary ของ `.uexp` ได้โดยตรง (มิฉะนั้นเกมจะแครชเพราะ Offset พัง) **ต้อง** ส่งต่อให้ Human Operator ใช้ UAssetGUI ทำการ Export/Import หรือเขียน Python Parser สำหรับ StringTable UEXP ให้เป๊ะๆ
- **Font Pipeline:** ✅ AI สามารถสร้าง Directory structure และก็อปปี้ TTF ไปทำ Font Flooding ทั้ง 7 สล็อตได้เอง 100%
- **Pak Pipeline:** ✅ AI สามารถรัน `repak` ผ่าน Terminal ได้ด้วยตัวเอง
