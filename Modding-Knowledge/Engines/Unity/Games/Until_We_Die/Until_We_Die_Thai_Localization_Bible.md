# Until We Die — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Until We Die is a base-defense strategy game developed by **Pixeye Games** using **Unity Engine (IL2CPP)**. The Thai localization mod (by **LUNG DEAR**) takes a brilliantly different approach: **Runtime Injection (No-Asset-Modification)**. Instead of unpacking and repacking Unity archives (`.assets`/`.bundle`), the mod uses the **BepInEx 6** framework to inject a custom C# plugin (`ThaiFontFallback.dll`) into the game's memory at runtime. This plugin dynamically loads Thai fonts from the Windows OS and injects Thai translations directly into the game's I2 Localization system.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Unity Engine (IL2CPP build) |
| **Developer** | Pixeye Games |
| **Mod Author** | LUNG DEAR (v2.1.0) |
| **Mod Framework** | BepInEx 6 (IL2CPP) |
| **Archive Format** | None (Runtime Injection) |
| **Font System** | TextMeshPro (TMP) + Dynamic OS Font Fallback |
| **Thai Font** | Leelawadee UI / Tahoma (Loaded from `C:\Windows\Fonts`) |
| **Text System** | I2 Localization (injected via code) + XUnity.AutoTranslator |
| **Text Encoding** | UTF-8 |
| **Mod Complexity** | ★★★★☆ (Advanced reverse engineering & C# Harmony patching) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
ม็อดนี้เป็นแบบ "Drop-in Portable Package" ที่ทำงานทับซ้อน (Overlay) บนตัวเกม โดยไม่ดัดแปลงไฟล์ดั้งเดิมของเกมเลย:

```text
Until We Die/
├── winhttp.dll                       (Proxy DLL โหลด BepInEx)
├── doorstop_config.ini               (ตั้งค่า Doorstop)
├── .doorstop_version                 (Doorstop version flag)
├── dotnet/                           (CoreCLR runtime สำหรับรัน C# บน IL2CPP)
└── BepInEx/
    ├── core/                         (BepInEx Framework)
    ├── unity-libs/                   (Unity IL2CPP Interop assemblies)
    ├── plugins/
    │   ├── XUnity.AutoTranslator/    (ปลั๊กอินแปลภาษาแบบเรียลไทม์)
    │   ├── XUnity.ResourceRedirector/(Helper สำหรับ AutoTranslator)
    │   └── ThaiFontFallback.dll      (★ Custom Plugin หัวใจหลักของม็อด)
    │
    ├── Translation/th/Text/          (ไฟล์คำแปลสำหรับ XUnity - 388 บรรทัด)
    ├── th_inject.txt                 (ไฟล์คำแปลสำหรับ I2 Localization - 493 บรรทัด)
    └── _thaifont_src/                (Source code ของ ThaiFontFallback.dll)
```

---

## 4. Font Analysis

### 4.1 Dynamic OS Font Fallback (ไม่ต้องยัดฟอนต์เข้าเกม!)
เกมนี้ใช้ TextMeshPro (TMP) ซึ่งปกติจะต้องสร้าง Font Asset (`.asset`) แต่เนื่องจากผู้สร้างม็อดไม่ต้องการแตะไฟล์เกม จึงใช้วิธี **Harmony Patching**:
1. **Hook `FontEngine.LoadFontFace`**: เมื่อเกมพยายามโหลดฟอนต์ Plugin จะแทรกแซงและบังคับให้ไปโหลดฟอนต์จาก OS (`C:\Windows\Fonts\leelawui.ttf` หรือ `tahoma.ttf`)
2. **Dynamic TMP Asset Creation**: สร้าง `TMP_FontAsset` ขึ้นมาใน memory สดๆ ระหว่างรันเกม (ใช้โหมด `GlyphRenderMode.SDFAA` และ `AtlasPopulationMode.Dynamic`)
3. **Pre-add Thai Block**: เติมช่วงอักขระ U+0E00 ถึง U+0E7F เข้าไปใน Character Table ของฟอนต์ที่สร้างใหม่
4. **Global Fallback Injection**: นำฟอนต์ที่สร้างใหม่นี้ไปยัดใส่ `TMP_Settings.fallbackFontAssets` ทำให้ **ทุกฟอนต์ในเกมที่แสดงภาษาไทยไม่ได้ จะเด้งมาใช้ฟอนต์นี้โดยอัตโนมัติ**

นี่เป็นเทคนิคขั้นสูงที่ทำให้ตัวม็อดมีขนาดเล็กมาก และไม่ต้องห่วงเรื่องลิขสิทธิ์ฟอนต์ หรือปัญหาแพทช์เกมอัปเดตแล้วไฟล์ฟอนต์พัง

---

## 5. Text Analysis

### 5.1 Dual-Layer Translation System
ม็อดนี้ใช้ 2 ระบบทำงานควบคู่กัน:

#### 1. I2 Localization Injection (`th_inject.txt`)
- **ขนาด:** 493 บรรทัด (22,532 อักษรไทย)
- **การทำงาน:** Plugin จะ Hook ฟังก์ชัน `LocalizationManager.UpdateSources` ของ I2 Localization (ปลั๊กอินแปลภาษาชื่อดังของ Unity) เมื่อเกมโหลดข้อมูลภาษาเสร็จ ม็อดจะแอบแทรกภาษา "Thai" เข้าไปใน Source และดึงข้อความจาก `th_inject.txt` ไปยัดทับใน Dictionary ของ I2 แบบสดๆ

#### 2. XUnity.AutoTranslator (`Translation/th/Text/*.txt`)
- **ขนาด:** 4 ไฟล์, 388 บรรทัด (12,510 อักษรไทย)
- **การทำงาน:** เป็นระบบดักจับ Text (Text Hooking) ที่คอยดักข้อความก่อนแสดงผลบนหน้าจอ ถ้าตรงกับที่ตั้งไว้ในไฟล์ จะสลับเป็นข้อความไทยให้ เหมาะสำหรับข้อความที่หลุดรอดจากระบบ I2

**สถิติรวม:** ~35,042 อักษรไทย (ม็อดขนาดเล็ก-กลาง เน้นเนื้อหา UI และ Tutorial)

---

## 6. Cross-Engine Comparison
เปรียบเทียบกับเกม Unity อื่นๆ:

| Feature | Until We Die | Sea of Stars | SOS: Grand Bazaar |
|---|---|---|---|
| **Unity Build** | IL2CPP | Mono / Addressables | Addressables |
| **Mod Method** | BepInEx Runtime Injection | AssetBundle Replacement | AssetBundle Replacement |
| **Font System** | Dynamic OS Font (Code) | TMP Bitmap Font (Atlas) | TMP SDF Font (Atlas) |
| **Text System** | I2 Inject + AutoTranslator | MonoBehaviour Edits | MonoBehaviour Edits |
| **Mod Size** | 24 MB (รวม Framework) | 192 MB | 72 MB |
| **Update Resilience** | ทนต่อแพทช์สูงมาก (ไม่พังง่าย) | พังทันทีที่เกมอัปเดต | พังทันทีที่เกมอัปเดต |
| **Complexity** | ★★★★☆ (Code-based) | ★★★☆☆ (Asset-based) | ★★★☆☆ (Asset-based) |

---

## 7. Pipeline — ขั้นตอนสร้างม็อด

ด้วยระบบ Runtime Injection เราแทบไม่ต้องใช้โปรแกรมแกะไฟล์เกมเลย:

1. **เขียน C# Plugin:** เขียนโค้ด Hook ฟังก์ชันที่ต้องการด้วย Harmony (ดู `Plugin.cs`)
2. **คอมไพล์ Plugin:** คอมไพล์เป็น `ThaiFontFallback.dll` สำหรับ BepInEx IL2CPP
3. **ดึง Text ต้นฉบับ:** ใช้โค้ด `DumpI2()` ดึงข้อความทั้งหมดออกมาเป็นไฟล์ `i2_terms.txt`
4. **แปลข้อความ:** แก้ไข `th_inject.txt`
5. **สร้างโครงสร้าง BepInEx:** นำ DLL และไฟล์ Text ไปวางในโครงสร้างโฟลเดอร์ให้ถูกต้อง

---

## 8. Troubleshooting
- **เกมโหลดครั้งแรกช้า (1-2 นาที):** เป็นเรื่องปกติ เพราะ BepInEx กำลัง Unhollow / Generate IL2CPP Interop assemblies (จะทำแค่ครั้งแรกหรือตอนเกมอัปเดต)
- **เข้าเกมแล้วไม่เป็นภาษาไทย:** ต้องแน่ใจว่าติดตั้ง BepInEx ครบทุกไฟล์ (winhttp.dll)
- **ตัวหนังสือไทยหาย (OS Font):** เครื่องต้องมีฟอนต์ Leelawadee UI หรือ Tahoma (ปกติมีมากับ Windows อยู่แล้ว)
- **เกมอัปเดตใหญ่แล้วม็อดพัง:** ให้ลบโฟลเดอร์ `BepInEx\interop` ทิ้ง แล้วเข้าเกมเพื่อให้มัน Generate ใหม่

---

## 9. Required Tools
| Tool Name | Purpose | Source |
|---|---|---|
| BepInEx 6 (IL2CPP) | Modding Framework (Hook/Inject) | [GitHub: BepInEx] |
| Visual Studio / Rider | เขียนและคอมไพล์ C# Plugin | [Microsoft] |
| XUnity.AutoTranslator | ระบบแปลสดสำหรับ Unity | [GitHub: bbepis] |

---

## 10. Extracted Assets
เนื่องจากเป็นม็อดแบบ Code Injection สิ่งที่มีค่าที่สุดคือ Source Code ที่ม็อดเดอร์ให้มาด้วย:
- [Plugin.cs](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unity_Engine/Games/Until_We_Die/Assets/SourceCode/Plugin.cs) — ซอร์สโค้ดหลักของ ThaiFontFallback.dll 
- [ThaiFont.csproj](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unity_Engine/Games/Until_We_Die/Assets/SourceCode/ThaiFont.csproj) — ไฟล์ Project สำหรับ Compile
- [i2_terms.txt](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unity_Engine/Games/Until_We_Die/Assets/SourceCode/i2_terms.txt) — ไฟล์ Dump ดึงข้อมูลข้อความดิบจากเกมออกมาทั้งหมด (44 KB)

---

## 11. M2M Protocol
**(สำหรับ AI Agent ที่ต้องการนำคัมภีร์ไปรันสร้างม็อดอัตโนมัติ)**

### 1. โค้ดสำคัญสำหรับการฉีดฟอนต์ (TMP Dynamic Font Creation)
*(ดูเต็มๆ ใน `Plugin.cs`)*
```csharp
// สร้างฟอนต์แบบ Dynamic จากไฟล์ TTF ใน Windows
var osFont = new Font("ThaiFallback");
TMP_FontAsset fa = TMP_FontAsset.CreateFontAsset(osFont, 90, 9, GlyphRenderMode.SDFAA, 1024, 1024, AtlasPopulationMode.Dynamic, true);

// ใส่ Characters ไทยเข้าไปล่วงหน้า
var sb = new System.Text.StringBuilder();
for (int c = 0x0E00; c <= 0x0E7F; c++) sb.Append((char)c);
fa.TryAddCharacters(sb.ToString(), false);

// ยัดเข้า Fallback หลักของเกม
TMP_Settings.fallbackFontAssets.Add(fa);
```

### 2. ข้อจำกัดสำหรับ AI
- **Mod Method:** ✅ AI สามารถศึกษา `Plugin.cs` เป็นแม่แบบ (Template) สำหรับนำไปใช้กับเกม Unity IL2CPP อื่นๆ ได้อย่างสมบูรณ์แบบ
- **Code Injection:** เป็นวิธีที่ฉลาดที่สุดในการทำม็อด Unity เพราะ **ไม่ต้องยุ่งกับไฟล์เกม (No Asset Manipulation)** ทำให้ไม่ติดปัญหาเรื่องลิขสิทธิ์ Asset เกม และทนต่อการแพทช์อัปเดตเกมได้ดีเยี่ยม
