# Assassin's Creed IV: Black Flag (Resynced) — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Assassin's Creed IV: Black Flag เป็นเกม Action-Adventure โดย **Ubisoft** ใช้ **Scimitar Engine** (เดียวกับ Ghost Recon Wildlands) ม็อดนี้เป็นเวอร์ชัน **Resynced 1.0.5** ซึ่งใช้เทคนิค **Font Saturation** — แทนที่ฟอนต์ AvenirNextWorld ทั้ง 20 variants ด้วยฟอนต์เดียวกันที่เพิ่ม Thai glyphs ผ่าน PUA (Private Use Area) เข้าไป ทำให้ทุก font weight ในเกมแสดงผลภาษาไทยได้หมด

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Scimitar Engine (Ubisoft proprietary) |
| **Developer** | Ubisoft Montreal |
| **Mod Version** | Resynced 1.0.5 |
| **Archive Format** | `.forge` (Scimitar archive, Magic: `scimitar\x00`, version 50) |
| **Font System** | TTF replacement ใน `resources/` |
| **Thai Font** | **Avenir Next World PUA** (20 variants ทั้งหมดมีขนาดเท่ากัน 574 KB) |
| **Text Encoding** | ข้อความอยู่ใน .forge (UTF-16LE, Scimitar binary format) |
| **Mod Technique** | Font Saturation + Forge Patch |
| **Mod Complexity** | ★★★☆☆ |

---

## 3. โครงสร้างไฟล์ (File Architecture)

```text
Assassin's Creed Black Flag Resynced 1.0.5/
├── DataPC_boot_patch_02.forge           (4.8 MB — Scimitar forge archive)
│   └── [Internal] Text/UI data patches
│
└── resources/                           (20 × TTF fonts, 574 KB each)
    ├── AvenirNextWorld-Regular.ttf       ← "Avenir Next World Regular PUA"
    ├── AvenirNextWorld-Bold.ttf
    ├── AvenirNextWorld-Demi.ttf
    ├── AvenirNextWorld-Medium.ttf
    ├── AvenirNextWorld-Light.ttf
    ├── AvenirNextWorld-Heavy.ttf
    ├── AvenirNextWorld-ExtraBold.ttf
    ├── AvenirNextWorld-Black.ttf
    ├── AvenirNextWorld-Thin.ttf
    ├── AvenirNextWorld-UltLt.ttf
    ├── AvenirNextWorld-Italic.ttf
    ├── AvenirNextWorld-BoldIt.ttf
    ├── AvenirNextWorld-DemiIt.ttf
    ├── AvenirNextWorld-MediumIt.ttf
    ├── AvenirNextWorld-LightIt.ttf
    ├── AvenirNextWorld-HeavyIt.ttf
    ├── AvenirNextWorld-ExtraBoldIt.ttf
    ├── AvenirNextWorld-BlackIt.ttf
    ├── AvenirNextWorld-ThinIt.ttf
    └── AvenirNextWorld-UltLtIt.ttf
```

### เทคนิค "Font Saturation" 🎨
ม็อดเดอร์ใช้เทคนิคที่น่าสนใจ — แทนที่ฟอนต์ **ทั้ง 20 weight variants** ด้วยไฟล์เดียวกัน (574,276 bytes ทุกไฟล์!) ที่ถูกดัดแปลงเพิ่ม Thai glyphs ผ่าน PUA เข้าไป ไม่ว่าเกมจะเรียก weight ไหน (Thin, Light, Regular, Bold, Black) ก็จะได้ฟอนต์ที่รองรับภาษาไทย ทำให้ **ไม่มี weight ไหนหลุดไม่แสดงไทย**

---

## 4. Font Analysis

### 4.1 Avenir Next World PUA
- **Full Name:** Avenir Next World Regular PUA
- **Size:** 574,276 bytes (574 KB)
- **Tables:** 18
- **Thai Coverage:** 87 codepoints (U+0E00–U+0E7F)
- **PUA (Private Use Area):** ใช้ PUA สำหรับ composite Thai characters (สระ/วรรณยุกต์ที่ต้อง position พิเศษ)
- **Technique:** ม็อดเดอร์สร้าง single TTF ที่รองรับไทยแล้วก๊อปทับทุก weight (20 variants = 1 font × 20)

### 4.2 ข้อสังเกต
- ฟอนต์ต้นฉบับ Avenir Next World ไม่รองรับไทย
- ม็อดเดอร์ใช้ FontForge หรือ tool คล้ายกันเพื่อเพิ่ม Thai glyphs + PUA composites
- ทุก weight กลายเป็น Regular weight เดียวกันหมด (เสียความหลากหลายของ weight)

---

## 5. Text Analysis

### 5.1 Forge Archive — Scimitar Format
- **ขนาดไฟล์:** 4.8 MB (DataPC_boot_patch_02.forge)
- **Magic:** `scimitar\x00` (version 50)
- **โครงสร้าง:** Scimitar binary packed archive
- **Thai in Forge:** แทบไม่มี (12 genuine Thai chars เท่านั้น)
- **สาเหตุ:** ข้อความแปลไทยน่าจะถูกส่งผ่านระบบ Resynced runtime injection แยกต่างหาก ไม่ได้ฝังใน forge

### 5.2 Resynced System
ชื่อ "Resynced" บ่งบอกว่าม็อดนี้อาจใช้ระบบ patching แบบ real-time ที่ inject text ผ่าน memory หรือ hook API แทนที่จะแก้ไข string ใน forge โดยตรง

---

## 6. Cross-Engine Comparison (Scimitar Family)

| Feature | AC Black Flag Resynced | Ghost Recon Wildlands | Anno 1800 |
|---|---|---|---|
| **Engine** | Scimitar | Scimitar | AnvilNext |
| **Archive** | .forge | .forge | XML + TTF |
| **Font Approach** | TTF Saturation (20×) | N/A | Locale Hijack (Korean) |
| **Thai Font** | Avenir Next World PUA | N/A | Sarabun Light |
| **Text Location** | Runtime injection (Resynced) | N/A | texts_korean.xml |
| **Complexity** | ★★★☆☆ | ★★★★☆ | ★★☆☆☆ |

---

## 7. Pipeline — ขั้นตอนสร้างม็อด

1. **สร้างฟอนต์ PUA:** ใช้ FontForge เพิ่ม Thai glyphs + PUA composites ลงใน Avenir Next World
2. **Font Saturation:** ก๊อปฟอนต์ที่แก้แล้วทับทุก weight (20 ไฟล์)
3. **Forge Patching:** ใช้ Scimitar forge tools แก้ไขข้อมูลใน `DataPC_boot_patch_02.forge`
4. **ติดตั้ง:** วาง forge + resources ลงในโฟลเดอร์เกม
5. **ทดสอบ:** ตรวจสอบว่าทุก UI element แสดงผลไทยถูกต้อง

---

## 8. Troubleshooting
- **ฟอนต์บาง weight หายไป:** ตรวจสอบว่าก๊อปทับครบ 20 ไฟล์
- **อักษรเพี้ยน/สระผิดตำแหน่ง:** PUA mapping อาจผิด ตรวจ cmap table
- **เกมอัปเดตแล้วฟอนต์หาย:** Steam Verify Files จะทับคืน ต้องลงใหม่
- **เวอร์ชัน Resynced ไม่ตรง:** v1.0.5 อาจไม่ compatible กับ game version อื่น

---

## 9. Required Tools
| Tool Name | Purpose | Source |
|---|---|---|
| FontForge | สร้าง/แก้ไข TTF เพิ่ม Thai PUA glyphs | [FontForge.org] |
| Scimitar Forge Tools | Pack/Unpack ไฟล์ `.forge` | [Ubisoft modding community] |
| HxD | ตรวจสอบ binary structure ของ forge | [mh-nexus] |

---

## 10. Extracted Assets
- **Avenir Next World PUA (3 representative weights จาก 20 ที่เหมือนกัน):**
  - [AvenirNextWorld-Regular-PUA.ttf](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Scimitar_Engine/Games/AC_Black_Flag_Resynced/Assets/Fonts/AvenirNextWorld-Regular-PUA.ttf) (574 KB, 87 Thai codepoints)
  - [AvenirNextWorld-Bold-PUA.ttf](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Scimitar_Engine/Games/AC_Black_Flag_Resynced/Assets/Fonts/AvenirNextWorld-Bold-PUA.ttf) (574 KB)
  - [AvenirNextWorld-Demi-PUA.ttf](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Scimitar_Engine/Games/AC_Black_Flag_Resynced/Assets/Fonts/AvenirNextWorld-Demi-PUA.ttf) (574 KB)
- **หมายเหตุ:** ทั้ง 20 variants เป็นไฟล์เดียวกัน (574,276 bytes) — เก็บตัวแทนไว้ 3 ตัว

---

## 11. M2M Protocol
**(สำหรับ AI Agent ที่ต้องการนำคัมภีร์ไปรันสร้างม็อดอัตโนมัติ)**

### AI Automation Score: ★★★☆☆ (ปานกลาง)
- **Font Creation:** ⚠️ AI ต้องใช้ FontForge CLI เพื่อ inject Thai glyphs + PUA composites
- **Font Saturation:** ✅ AI ทำได้ 100% — แค่ก๊อปไฟล์เดียวทับ 20 ไฟล์
- **Forge Patching:** ❌ AI ไม่สามารถ pack/unpack Scimitar .forge ได้ด้วยตัวเอง (ต้องใช้ community tools)
- **Text Translation:** ⚠️ ถ้าใช้ระบบ Resynced อาจเข้าถึงได้ผ่าน config files
