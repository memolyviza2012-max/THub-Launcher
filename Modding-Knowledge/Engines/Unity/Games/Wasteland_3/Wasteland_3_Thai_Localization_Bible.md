# Wasteland 3 — Thai Localization Modding Bible
### Opus Edition — Advanced Deep Analysis (Rivet Engineer)

> **Generated:** 2026-07-06  
> **Analyst:** Rivet Engineer Advanced (Antigravity AI / Gemini 3.1)  
> **Mod Author:** NodNuatTranslator  
> **Status:** ✅ Complete (10/10 Mandatory Sections)

---

## 1. Overview

**Wasteland 3** เป็นเกม RPG แบบ Turn-based ที่พัฒนาโดย **inXile Entertainment** บน **Unity Engine** ตัวเกมใช้ระบบ IL2CPP และระบบจัดการ Asset แบบ **Unity Addressables** ม็อดแปลไทยนี้ใช้สถาปัตยกรรมแบบ **Hybrid** โดยการใช้ BepInEx แทรกแซงโค้ดเกมเพื่อรันฟอนต์ไทยแบบไดนามิก ควบคู่ไปกับการยัดไฟล์แปลไทยทับไฟล์ String Table ของระบบ Addressables โดยตรง

**Mod Architecture Pattern:** Hybrid (Runtime Injection for Font + File Replacement for Text)

---

## 2. Technical Stack

| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Unity (IL2CPP) |
| **Developer** | inXile Entertainment |
| **Archive Format** | UnityFS (`.bundle`) + DLL Runtime Injection |
| **AES Encryption** | ❌ **No** — UnityFS ไม่มีการเข้ารหัสแบบ Custom สามารถเปิดด้วย UABEA ได้เลย |
| **Compression** | **LZ4** (Standard Unity Addressables compression) |
| **Font System** | Runtime Injection — BepInEx โหลด Raw `.ttf` จากโฟลเดอร์ plugins เพื่อสร้างเป็น Dynamic TextMesh Pro |
| **Thai Font Used** | **IBM Plex Sans Thai Regular** (Custom fix by NodNuatTranslator) |
| **Text System** | OEI StringTableData (บรรจุใน `.bundle`) |
| **Text Encoding** | **UTF-8** (Unity Standard String format) |
| **Mod Complexity** | ★★★☆☆ (การทำ Font ผ่าน BepInEx ง่ายมาก แต่ต้องแพ็กไฟล์ Text ผ่าน UABEA) |

---

## 3. โครงสร้างไฟล์ (File Architecture)

```
Wasteland 3/
├── BepInEx/                                     ← โฟลเดอร์ระบบ BepInEx (IL2CPP)
│   ├── core/
│   ├── interop/                                 ← IL2CPP Interop DLLs
│   └── plugins/
│       └── Wasteland3FontMod/
│           ├── Wasteland3FontMod.dll            ★ ปลั๊กอินแทรกโค้ดฟอนต์
│           └── 1_IBMPlexSans_fixByNodNuat...ttf ★ ฟอนต์ภาษาไทย (Raw TTF)
│
└── WL3_Data/
    └── StreamingAssets/
        └── aa/
            └── StandaloneWindows64/
                └── oei_assets_stringtabledata_english_...bundle ★ ไฟล์ข้อความ
```

> **ข้อสังเกต:** ระบบโครงสร้างของข้อความบ่งบอกว่า inXile น่าจะใช้งานระบบ Dialogue/String ของ **OEI (Obsidian Entertainment Inc.)** ซึ่งเป็นระบบยอดฮิตที่สตูดิโอในเครือ Microsoft มักแชร์เทคโนโลยีกันใช้

---

## 4. Font Analysis

### 4.1 Font Identification

ม็อดเดอร์ไม่ต้องต่อสู้กับการทำภาพ SDF Texture แต่ใช้วิธีโยนไฟล์ Raw TTF เข้าไปให้ BepInEx โหลดสร้างเป็น Dynamic Font กลางอากาศ:

| ไฟล์ในม็อด | ฟอนต์ไทยจริงที่ฝัง | Format | ขนาด |
|---|---|---|---|
| `1_IBMPlexSans_fixByNodNuatTranslator_2.ttf` | **IBM Plex Sans Thai Regular** | TTF | 95 KB |

### 4.2 Font Metadata

| Field | Value |
|---|---|
| **Font Family** | IBM Plex Sans Thai |
| **Full Name** | IBM Plex Sans Thai Regular |
| **Designer** | Mike Abbink, Paul van der Laan, Pieter van Rosmalen |
| **Manufacturer** | Bold Monday |
| **License** | SIL Open Font License v1.1 ✅ |
| **Thai Glyph Support** | ✅ สมบูรณ์ครบถ้วน (ผ่านการปรับปรุง "fixByNodNuatTranslator" เพื่อจัดเรียงสระและวรรณยุกต์ในเอนจิน Unity ให้เป๊ะขึ้น) |

### 4.3 Runtime Injection Method

ปลั๊กอิน `Wasteland3FontMod.dll` ทำหน้าที่ hook เข้ากับ `UnityEngine.TextRenderingModule` และ `Unity.TextMeshPro` เพื่อ:
1. อ่านไฟล์ `.ttf` จากฮาร์ดดิสก์
2. สั่ง `TMP_FontAsset.CreateFontAsset()`
3. ยัดเข้าเป็น Fallback Font ข้ามระบบทั้งหมดของเกม

---

## 5. Text Analysis

### 5.1 UnityFS Bundle Analysis

ไฟล์ข้อความ `oei_assets_stringtabledata_english_[hash].bundle` เก็บข้อมูลบทสนทนา UI และเควสทั้งหมด:

| ฟิลด์ | ค่า |
|---|---|
| **Magic** | `UnityFS` |
| **Version** | 5 |
| **File Object** | StringTableData (MonoBehaviour) |
| **Encoding** | UTF-8 |

ม็อดเดอร์ทำการดึง TextAsset ออกมาจาก Bundle แปลเป็นภาษาไทย แล้วใช้เครื่องมืออย่าง UABEA (Unity Asset Bundle Extractor Avalonia) หรือ UnityPy ยัดกลับคืนเข้าไป

---

## 6. Cross-Engine Comparison

### เปรียบเทียบกับเกม Unity อื่นๆ ในคลังความรู้

| เกม | Архитектура Mod | Font System | Text System | Complexity |
|---|---|---|---|---|
| **Wasteland 3** | Hybrid (BepInEx + Bundle) | Runtime TTF (BepInEx) | Addressables (.bundle) | ★★★☆☆ |
| **Hardspace Shipbreaker** | Hybrid (BepInEx + CSV) | Runtime TTF (BepInEx) | Raw CSV LocDB | ★★☆☆☆ |
| **Disco Elysium** | BepInEx (Code hook only) | Runtime Injection | Code Hooks (StringTable) | ★★★★☆ |
| **Two Point Campus** | File Replacement | TMP SDF Texture | StringTable (.assets) | ★★★☆☆ |

**Key Insights:**
- **Wasteland 3 vs Hardspace Shipbreaker:** ทั้งคู่ใช้ BepInEx โหลดไฟล์ Raw `.ttf` เหมือนกันเป๊ะ! (แสดงว่าเป็นเทคนิคยอดฮิตของ Unity ยุคใหม่) แต่ต่างกันตรงที่ Hardspace อ่านข้อความจากไฟล์ `.csv` ภายนอกได้เลย ในขณะที่ Wasteland 3 ม็อดเดอร์ยังต้องเหนื่อยกับการยัดข้อความกลับเข้าไปใน `.bundle` Addressables

---

## 7. Pipeline — ขั้นตอนสร้างม็อด

### Pipeline A: ข้อความ (Unity Addressables)
```
1. เปิดไฟล์ .bundle ด้วย UABEA (Unity Asset Bundle Extractor)
2. ค้นหา Asset ประเภท MonoBehaviour (StringTableData)
3. Export Dump เป็นไฟล์ .txt หรือ .json
4. แปลภาษาไทย (รักษาโครงสร้าง JSON หรือ Format เดิมไว้)
5. Import Dump กลับเข้าไปใน UABEA
6. File -> Save และนำไฟล์ .bundle ไปวางทับที่โฟลเดอร์ StreamingAssets/aa/
```

### Pipeline B: ฟอนต์ (BepInEx)
```
1. ติดตั้ง BepInEx สำหรับ IL2CPP ลงในโฟลเดอร์เกม
2. นำไฟล์ Wasteland3FontMod.dll ไปวางใน BepInEx/plugins/
3. หาฟอนต์ TTF ที่ต้องการ (ต้องแก้ปัญหาสระลอยมาแล้ว) วางคู่กัน
4. ปลั๊กอินจะจัดการสร้าง TextMesh Pro Font ให้โดยอัตโนมัติ
```

---

## 8. Troubleshooting

### 🔴 ปัญหาที่ 1: สระลอย วรรณยุกต์จม
| สาเหตุ | วิธีแก้ |
|---|---|
| Unity TextMesh Pro (เวอร์ชันเก่า) ไม่รองรับ Thai shaping | ต้องใช้ฟอนต์ที่ผ่านกระบวนการ "Fix" สระลอยมาแล้ว เช่นการชิฟท์ตำแหน่ง (Shift Position) วรรณยุกต์ใน FontForge (เหมือนที่ NodNuatTranslator ทำ) |

### 🔴 ปัญหาที่ 2: ข้อความไทยกลายเป็นกล่องสี่เหลี่ยม
| สาเหตุ | วิธีแก้ |
|---|---|
| BepInEx ปลั๊กอินไม่ทำงาน | ตรวจสอบว่า `doorstop_config.ini` และ `winhttp.dll` วางถูกต้องในโฟลเดอร์รันเกมหรือไม่ และเช็ค log ของ BepInEx |

### 🔴 ปัญหาที่ 3: เกมค้างตอนโหลด
| สาเหตุ | วิธีแก้ |
|---|---|
| ไฟล์ .bundle เสียหายตอนแพ็ก | UABEA บางเวอร์ชันมีปัญหากับ Addressables แนะนำให้ใช้ UABEAvalonia ตัวล่าสุด หรือ UnityPy ในการแพ็กกลับ |

---

## 9. Required Tools

| เครื่องมือ | หน้าที่ | แหล่งดาวน์โหลด |
|---|---|---|
| **UABEA (Avalonia)** | แกะและแพ็กไฟล์ `.bundle` (Unity Addressables) | [GitHub - nesrak1/UABEA](https://github.com/nesrak1/UABEA) |
| **UnityPy** | (ตัวเลือกเสริม) ใช้เขียนสคริปต์ Python แพ็กข้อความ | [GitHub - K0lb3/UnityPy](https://github.com/K0lb3/UnityPy) |
| **BepInEx (IL2CPP)** | Framework สำหรับแทรกโค้ดรันฟอนต์ | [GitHub - BepInEx/BepInEx](https://github.com/BepInEx/BepInEx) |

---

## 10. Extracted Assets

### 10.1 Extracted Fonts (สกัดสำเร็จ ✅)

ฟอนต์ Raw TTF สามารถดึงมาใช้งานได้โดยตรง:

| ไฟล์ที่สกัด | Font Name | Format | ขนาด | Verified |
|---|---|---|---|---|
| [IBMPlexSansThai-Regular.ttf](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unity/Games/Wasteland_3/Assets/Fonts/IBMPlexSansThai-Regular.ttf) | IBM Plex Sans Thai Regular | TTF | 95,160 B | ✅ Shell.Application |

### 10.2 Font Files Location
```
E:\Mod_Workspace\Modding-Knowledge\Engines\Unity\Games\Wasteland_3\Assets\Fonts\
└── IBMPlexSansThai-Regular.ttf
```

> **License Note:** IBM Plex Sans Thai อนุญาตภายใต้ SIL Open Font License v1.1 — สามารถแจกจ่ายพร้อมม็อดได้อย่างถูกกฎหมาย ✅

---

*📖 Thai Localization Modding Bible — Opus Edition*  
*สร้างโดย Rivet Engineer Advanced Protocol*
