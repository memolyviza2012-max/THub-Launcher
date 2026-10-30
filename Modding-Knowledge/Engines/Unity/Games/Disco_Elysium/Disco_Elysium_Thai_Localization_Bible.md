# Disco Elysium — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
เอกสารนี้วิเคราะห์กลไกม็อดภาษาไทยของเกม **Disco Elysium** ซึ่งพัฒนาด้วย **Unity Engine** โดยใช้สถาปัตยกรรม IL2CPP ม็อดตัวนี้มีความแตกต่างจากม็อดทั่วไป เพราะใช้วิธี **Code Injection ผ่าน BepInEx** เพื่อแทรกแซงการโหลดข้อความและการเรนเดอร์ฟอนต์ระหว่างที่เกมกำลังทำงานอยู่ (Runtime) แทนที่จะแพ็กไฟล์กลับเข้าไปในเกม (Repacking)

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Unity (IL2CPP Architecture) |
| **Modding Framework** | **BepInEx** (Core replacement + Plugins) |
| **Font System** | Unity TextMesh Pro (TMP) + Runtime Fallback Injection |
| **Text Localization** | Runtime CSV Injection (`dialoguebundle_translation.csv`) |
| **Code Injection Tool** | HarmonyLib (ฝังอยู่ใน BepInEx) |
| **Mod Complexity** | ★★★★☆ (Runtime injection, ไม่มีการแก้ไฟล์ต้นฉบับเกม) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
ม็อดนี้ประกอบด้วยไฟล์ในโฟลเดอร์หลักของเกม โดยโฟกัสที่โครงสร้างของ BepInEx:
```
Disco Elysium/
├── winhttp.dll                       ← BepInEx Proxy DLL (ดักจับการรันเกม)
├── doorstop_config.ini               ← Config ให้โหลด BepInEx
└── BepInEx/
    ├── core/                         ← ไฟล์ระบบ BepInEx (Harmony, IL2CPP interop)
    └── plugins/
        ├── DiscoTranslation.dll      ← ★ Plugin โหลดข้อความแปล
        ├── dialoguebundle_translation.csv ← ★ ข้อความแปลไทย (~70,270 บรรทัด / 23 MB)
        └── ThaiFont/
            ├── ThaiFont.dll          ← ★ Plugin จัดการฟอนต์ไทย
            └── thai_font.bundle      ← ★ Unity Asset Bundle ของฟอนต์ (86 KB)
```

---

## 4. Font Analysis — TextMesh Pro Fallback

### 4.1 รูปแบบของฟอนต์
เกม Disco Elysium ใช้ระบบ UI ที่วาดด้วย **TextMesh Pro (TMP)** ของ Unity. ฟอนต์ที่ถูกใช้งานจึงไม่ใช่แบบ Vector (TTF/OTF) แต่เป็น **SDF (Signed Distance Field)** ซึ่งคือการแปลงตัวอักษรเป็น "รูปภาพ (Texture Atlas)" แล้วคำนวณระยะห่างเพื่อให้ตัวอักษรคมชัดเมื่อถูกซูมเข้าหรือออก

### 4.2 วิธีการม็อดฟอนต์ของเกมนี้ (Runtime Injection)
แทนที่จะหาทางแตกไฟล์ `.assets` ของเกมเพื่อนำรูปภาพฟอนต์ไปทับ ม็อดเดอร์ใช้วิธีที่ฉลาดและยืดหยุ่นกว่ามาก คือการเขียนโค้ด (ผ่าน `ThaiFont.dll`) เพื่อดักจับ (Hook) การทำงานของ TextMesh Pro ดังนี้:

1. ใช้ **HarmonyPatch** เพื่อแทรกแซง Method: `TMP_FontAsset.get_fallbackFontAssetTable()`
2. เมื่อเกมถูกโหลด `ThaiFont.dll` จะสั่งโหลด `thai_font.bundle`
3. สกัด `TMP_FontAsset` ที่อยู่ข้างใน
4. ยัด (Inject) ฟอนต์ตัวนั้นเข้าสู่ `fallbackFontAssetTable` ของฟอนต์ดั้งเดิมทุกตัวในเกม
5. ผลลัพธ์: เมื่อเกมพยายามแสดงตัวอักษรภาษาไทยแต่ฟอนต์เดิมไม่มี มันจะสลับไปดึงภาพจากฟอนต์ใน `thai_font.bundle` มาใช้ทันที

> **ทำไมถึงดึง Raw Font (TTF/OTF) ไม่ได้?**
> ฟอนต์ที่อยู่ใน `thai_font.bundle` ถูกแปลงเป็น TextMesh Pro Asset แล้ว นั่นหมายความว่ามันถูกบีบอัดและอบ (Bake) เป็นรูปภาพ Texture Atlas (SDF) + ข้อมูลตำแหน่งตัวอักษรไปเรียบร้อยแล้ว ไม่สามารถนำกลับไปเป็นฟอนต์ติดตั้งใน Windows (TTF/OTF) ได้

---

## 5. Text Analysis — Runtime CSV Translation

เช่นเดียวกับฟอนต์ ระบบข้อความก็ใช้วิธี **Runtime Injection**:
1. ข้อมูลการแปลทั้งหมด 70,270 บรรทัด (ขนาด 23 MB) ถูกเก็บไว้ในไฟล์แบบเปิด `dialoguebundle_translation.csv`
2. โครงสร้าง CSV ประกอบด้วย: `conversation_id, conversation_title, entry_id, actor_name, dialogue_text, menu_text, translation`
3. ไฟล์ `DiscoTranslation.dll` จะทำหน้าที่โหลดไฟล์ CSV ขึ้นมาบน RAM ตอนเริ่มเกม
4. ใช้ Harmony ดักจับระบบ Localization ของเกม เมื่อเกมขอข้อความใดๆ ปลั๊กอินจะปาดหน้าดึงข้อความจาก CSV ไปแสดงแทน

> วิธีนี้มีข้อดีคือ: **แปลเกมอัปเดตได้ง่ายมาก** ไม่ต้องแตก-แพ็กไฟล์ใหม่ แค่แก้ CSV ไฟล์เดียวจบ

---

## 6. Required Tools
สำหรับใครที่จะทำม็อดรูปแบบนี้กับเกม Unity IL2CPP:
| เครื่องมือ | หน้าที่ |
|---|---|
| **BepInEx (IL2CPP version)** | Modding Framework สำหรับโหลด Plugin |
| **Il2CppDumper / Cpp2IL** | สกัด DLL โครงสร้างเกมมาใช้อ้างอิงตอนเขียนโค้ด |
| **Visual Studio / Rider** | เขียน C# Plugin และใช้ HarmonyLib สร้าง Patch |
| **Unity Editor** | สร้าง `thai_font.bundle` (TMP Asset) |

---

## 7. เปรียบเทียบกับเทคนิคอื่น

| เกม | Engine | วิธีทำ Mod ข้อความ | วิธีทำ Mod ฟอนต์ |
|---|---|---|---|
| **Disco Elysium** | Unity (IL2CPP) | BepInEx Plugin + CSV | BepInEx Plugin + TMP Bundle (Runtime Fallback) |
| **Front Mission 1st**| Unity (IL2CPP) | XUnity.AutoTranslator | XUnity.AutoTranslator (TTF Override) |
| **Hardspace** | Unity (Mono) | แก้ TextAsset ภายใน `sharedassets` | แก้ Font Asset ภายใน `sharedassets` (Repack) |

---

## 8. Conclusion & Extracted Assets

ม็อดภาษาไทยของ **Disco Elysium** เป็นเคสศึกษาที่ดีเยี่ยมสำหรับการทำม็อดเกม Unity ยุคใหม่ (IL2CPP) ที่ใช้ **BepInEx + Harmony** ในการแทรกแซงเกมแบบเบ็ดเสร็จ (Non-destructive modding)
วิธีนี้ทำให้ไฟล์เกมดั้งเดิมสะอาด อัปเดตเกมได้โดยที่ม็อดพังยากขึ้น (ถ้าโครงสร้างโค้ดเกมไม่เปลี่ยนเยอะ) และสามารถเปิดให้ชุมชนช่วยกันแปลผ่าน Google Sheets หรือ CSV ได้โดยตรง

- **Fonts:** ❌ ไม่สามารถดึง TTF/OTF ออกมาได้ เพราะฟอนต์ถูกแปลงเป็น SDF Image (TextMesh Pro Asset) เรียบร้อยแล้ว (ดูคำอธิบายที่ [EXTRACTION_NOTE.txt](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unity/Games/Disco_Elysium/Assets/Fonts/EXTRACTION_NOTE.txt))
- **Texts:** ✅ ข้อความแปลดึงจากไฟล์ `dialoguebundle_translation.csv` ได้โดยตรง
- **Configs:** ✅ DLL Source Logic จากการ Decompile `ThaiFont.dll` และ `DiscoTranslation.dll` (อ้างอิงด้านบน)
