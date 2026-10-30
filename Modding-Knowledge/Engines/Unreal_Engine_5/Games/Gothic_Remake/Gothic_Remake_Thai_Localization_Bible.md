# Gothic Remake — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
เอกสารนี้วิเคราะห์กลไกม็อดภาษาไทยของ **Gothic Remake** (Gothic 1 Remake) อย่างละเอียดที่สุด เกมนี้สร้างด้วย **Unreal Engine 5** ที่ผนวกกับระบบเฉพาะของ **Alkimia Engine** (เอนจินภายในของ THQ Nordic / Piranha Bytes) ม็อดนี้มีความซับซ้อนสูงเพราะใช้ระบบ **Hybrid Architecture** — ผสมระหว่าง UE5 IoStore, UE4 PAK, และ Alkimia Localization Cache ที่ **เข้ารหัส (Encrypted)**

---

## 2. Technical Stack

| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | **Unreal Engine 5** + **Alkimia Engine** (THQ Nordic proprietary layer) |
| **Asset System** | **Hybrid**: UE5 IoStore (UCAS/UTOC v6) + UE4 PAK v3 |
| **Localization System** | Alkimia Localization Cache (`.lcache` — proprietary, encrypted) |
| **Dialogue System** | Alkimia Story/Conversation system (แยกจาก UE5) |
| **Font System (UE5)** | `.ufont` (UE5 Font Asset) ใน PAK |
| **Font System (Alkimia)** | Raw `.ttf` files ใน `Story/Conversation/fonts/` |
| **Encryption** | LCACHE encrypted (Entropy 7.8 bits/byte) |
| **Compression** | UCAS/UTOC: UE5 IoStore compression; PAK: Zlib |
| **Mod Complexity** | ★★★★☆ (ระบบ dual-engine, ไฟล์เข้ารหัส, ต้องเข้าใจทั้ง UE5 และ Alkimia) |

---

## 3. โครงสร้างไฟล์ (File Architecture)

### 3.1 ภาพรวม
```
G1R/
├── Content/
│   └── Paks/
│       ├── G1R-Windows_P.pak    ← 2.07 MB  (UE4 Legacy PAK — ฟอนต์ UI)
│       ├── G1R-Windows_P.ucas   ← 9.25 MB  (UE5 IoStore — เนื้อหาเข้ารหัส)
│       └── G1R-Windows_P.utoc   ← 1.98 KB  (UE5 IoStore — สารบัญ)
└── Story/
    ├── Cache/
    │   └── AlkimiaLocalization_00000000.lcache  ← 36.42 MB (ข้อความแปลเข้ารหัส)
    └── Conversation/
        └── fonts/              ← ฟอนต์ TTF ดิบ (ไม่เข้ารหัส)
            ├── BerkshireSwash-Regular.ttf   (1.3 MB)
            ├── Boucherie-Block.ttf          (1.7 MB)
            ├── NotoSerif-Bold.ttf           (215 KB)
            ├── NotoSerif-BoldItalic.ttf     (267 KB)
            ├── NotoSerif-Italic.ttf         (270 KB)
            └── NotoSerif-Regular.ttf        (211 KB)
```

### 3.2 ขนาดรวม
| ไฟล์ | ขนาด |
|---|---|
| `G1R-Windows_P.pak` | 2.07 MB |
| `G1R-Windows_P.ucas` | 9.25 MB |
| `G1R-Windows_P.utoc` | 1.98 KB |
| `AlkimiaLocalization_00000000.lcache` | 36.42 MB |
| Fonts (6 TTF files) | 3.99 MB |
| **รวมทั้งหมด** | **~51.73 MB** |

---

## 4. Dual-Engine Architecture — ระบบเอนจินคู่

### 4.1 ทำไมถึงมีสองระบบ?
Gothic Remake ใช้ UE5 เป็นฐาน แต่มีระบบ **Alkimia** ซ้อนทับอยู่ด้านบนสำหรับจัดการ:
- **Dialogue/Conversation** — ระบบบทสนทนาเฉพาะ RPG
- **Story/Quest** — ระบบเนื้อเรื่องและภารกิจ
- **Localization Cache** — ระบบเก็บข้อความแปลภาษา

ส่วน UE5 ดูแล:
- **Rendering, Physics, Audio** — ระบบ core ของเกม
- **UI Fonts** — ฟอนต์ที่ใช้แสดงบน UI (ผ่าน `.ufont` ใน PAK)
- **Assets** — textures, meshes, materials ฯลฯ

### 4.2 ผลกระทบต่อม็อด
ม็อดต้องแก้ไขไฟล์ **2 ระบบพร้อมกัน**:
1. **UE5 side** — PAK/UCAS/UTOC สำหรับฟอนต์ UI
2. **Alkimia side** — LCACHE สำหรับข้อความ + TTF สำหรับฟอนต์บทสนทนา

---

## 5. PAK Analysis — UE4 Legacy PAK (ฟอนต์ UI)

### 5.1 PAK Structure
| ฟิลด์ | ค่า |
|---|---|
| **Format** | UE4 PAK v3 |
| **Magic** | `E1 12 6F 5A` |
| **Mount Point** | `../../../G1R/Content/UI/Fonts/` |
| **Entry Count** | 6 |
| **Index Offset** | 2,168,539 |
| **Index Size** | 1,987 bytes |
| **Compression** | Zlib |

### 5.2 ไฟล์ภายใน PAK (6 entries)
| ไฟล์ | หน้าที่ |
|---|---|
| `BoucherieBlockExtended.ufont` | ฟอนต์หัวข้อ/ตัวเด่น |
| `FiraSansExtraCondensed-Bold.ufont` | ฟอนต์ UI หลัก (ตัวหนาแคบ) |
| `NotoSerif-Regular.ufont` | ฟอนต์เนื้อหา |
| `NotoSerif-Bold.ufont` | ฟอนต์เนื้อหาตัวหนา |
| `NotoSerif-Italic.ufont` | ฟอนต์เนื้อหาตัวเอียง |
| `NotoSerif-BoldItalic.ufont` | ฟอนต์เนื้อหาตัวหนาเอียง |

> **หมายเหตุ:** PAK ใช้ mount point `UI/Fonts/` แสดงว่าฟอนต์เหล่านี้ใช้สำหรับ **UI ของเกม** (เมนู, HUD, inventory ฯลฯ)

---

## 6. IoStore Analysis — UE5 UCAS/UTOC

### 6.1 UTOC (Table of Contents)
| ฟิลด์ | ค่า |
|---|---|
| **Magic** | `-==--==--==--==-` (UE5 IoStore signature) |
| **Version** | 6 |
| **Size** | 1,979 bytes |

### 6.2 UCAS (Content Archive Store)
| ฟิลด์ | ค่า |
|---|---|
| **Size** | 9.25 MB |
| **Entropy** | 7.8 bits/byte (**เข้ารหัส/บีบอัดสูง**) |

UCAS เก็บข้อมูล asset ที่อ้างอิงจาก UTOC — ในม็อดนี้คาดว่าเก็บ **LocRes** หรือ asset อื่นๆ ที่เกี่ยวกับ localization ที่ถูกเข้ารหัส

### 6.3 _P Suffix (Patch)
ทั้ง PAK, UCAS, UTOC ใช้ชื่อ `G1R-Windows_P` — suffix `_P` หมายถึง **Patch** ที่จะ override ไฟล์เดิมของเกม เหมือนกลไก Patch PAK ของ UE4

---

## 7. Alkimia Localization Cache (.lcache)

### 7.1 Format Analysis
| ฟิลด์ | ค่า |
|---|---|
| **ชื่อไฟล์** | `AlkimiaLocalization_00000000.lcache` |
| **ขนาด** | 36.42 MB |
| **Magic** | `F1 FC 1B 81 27 01 AC 66` (Alkimia proprietary) |
| **Entropy** | **7.808 bits/byte** → **ENCRYPTED** |
| **Readable ASCII** | ไม่มี (ไฟล์ทั้งหมดเป็น encrypted binary) |

### 7.2 ความหมายของการเข้ารหัส
- Entropy ใกล้ 8.0 = ข้อมูลถูก **เข้ารหัสอย่างแน่นอน** (random distribution)
- ไม่สามารถอ่านหรือแก้ไขด้วย text editor หรือ hex editor ตรงๆ ได้
- ต้องใช้เครื่องมือ decryption เฉพาะของ Alkimia Engine หรือ mod tool ที่รองรับ
- ชื่อไฟล์ `_00000000` อาจบ่งบอก locale ID (0 = default/English)

### 7.3 เนื้อหาคาดว่าจะเป็น
- **บทสนทนาทั้งหมด** ของเกม (dialogue, quest text, item descriptions)
- **ข้อความ UI** ส่วนที่ Alkimia จัดการ
- ขนาด 36 MB บ่งบอกว่ามีข้อความจำนวนมหาศาล (Gothic เป็น RPG ที่มีบทสนทนาเยอะมาก)

---

## 8. Font System — ระบบฟอนต์คู่

### 8.1 ฟอนต์ UE5 (ใน PAK)
ฟอนต์ 6 ตัวที่ใช้สำหรับ UI ของเกม — อยู่ในรูปแบบ `.ufont` (UE5 font asset):

| ฟอนต์ | ประเภท | หน้าที่ |
|---|---|---|
| **FiraSansExtraCondensed-Bold** | Sans-Serif (ตัวแคบหนา) | UI หลัก, เมนู |
| **BoucherieBlockExtended** | Display/Decorative | หัวข้อ, ชื่อ |
| **NotoSerif-Regular** | Serif | เนื้อหาหลัก |
| **NotoSerif-Bold** | Serif Bold | เนื้อหาเน้น |
| **NotoSerif-Italic** | Serif Italic | เนื้อหาเอียง |
| **NotoSerif-BoldItalic** | Serif Bold Italic | เนื้อหาเน้น+เอียง |

### 8.2 ฟอนต์ Alkimia (TTF ดิบ ใน Story/Conversation/fonts/)
ฟอนต์ 6 ตัวที่ใช้สำหรับ **ระบบบทสนทนา** ของ Alkimia — เป็นไฟล์ `.ttf` ที่วางตรงๆ:

| ฟอนต์ | ขนาด | รองรับไทย? | หน้าที่ |
|---|---|---|---|
| **BerkshireSwash-Regular.ttf** | 1.3 MB | ✅ มี Thai glyphs | หัวข้อบทสนทนา |
| **Boucherie-Block.ttf** | 1.7 MB | ✅ มี Thai glyphs | ชื่อตัวละคร/สถานที่ |
| **NotoSerif-Regular.ttf** | 211 KB | ✅ มี Thai glyphs | เนื้อหาบทสนทนา |
| **NotoSerif-Bold.ttf** | 215 KB | ✅ มี Thai glyphs | เน้น |
| **NotoSerif-Italic.ttf** | 270 KB | ✅ มี Thai glyphs | เอียง |
| **NotoSerif-BoldItalic.ttf** | 267 KB | ⚠️ ไม่พบ | Bold Italic |

> **สำคัญ:** ฟอนต์เหล่านี้ถูก **แก้ไขเพิ่ม glyph ภาษาไทย** เข้าไปแล้ว (ยืนยันจากการตรวจพบ Thai glyph references ใน binary)

### 8.3 ข้อดีของ Dual Font System
- ฟอนต์ Alkimia เป็น **TTF ดิบ** → แก้ไขง่ายมาก (แค่ swap ไฟล์)
- ฟอนต์ UE5 เป็น `.ufont` → ต้อง repack ใน PAK แต่ยังง่ายกว่า custom binary

---

## 9. Complete Pipeline — ขั้นตอนสร้างม็อด

```
ขั้นตอนที่ 1: เตรียมฟอนต์ไทย
    A. สร้าง TTF ที่รองรับอักษรไทย (merge กับ NotoSerif, BerkshireSwash, Boucherie)
    B. วาง TTF → Story/Conversation/fonts/ (สำหรับบทสนทนา Alkimia)
    C. Wrap เป็น .ufont → repack ใน PAK (สำหรับ UI ของ UE5)
        ↓
ขั้นตอนที่ 2: แก้ไข Localization Cache
    ใช้เครื่องมือ: Alkimia Localization tool / community decryptor
    - Decrypt LCACHE
    - แปลข้อความจากอังกฤษเป็นไทย
    - Re-encrypt + repack เป็น .lcache ใหม่
        ↓
ขั้นตอนที่ 3: จัดการ UCAS/UTOC (ถ้าจำเป็น)
    ใช้ UnrealPak หรือ IoStore tools:
    - แก้ไข LocRes ภายใน IoStore
    - Repack UCAS/UTOC
        ↓
ขั้นตอนที่ 4: วางไฟล์
    คัดลอกไปที่:
    {GameInstall}/G1R/Content/Paks/ (PAK + UCAS + UTOC)
    {GameInstall}/G1R/Story/Cache/ (LCACHE)
    {GameInstall}/G1R/Story/Conversation/fonts/ (TTF)
        ↓
เสร็จสิ้น!
```

---

## 10. Required Tools

| เครื่องมือ | หน้าที่ | ระดับความจำเป็น |
|---|---|---|
| **UnrealPak** (UE5 SDK) | Pack/Unpack PAK + UCAS/UTOC | ✅ จำเป็น |
| **Alkimia Localization Decryptor** | Decrypt/Re-encrypt `.lcache` | ✅ จำเป็น (community tool) |
| **FontForge / Font Merge Tool** | สร้างฟอนต์ที่รองรับอักษรไทย | ✅ จำเป็น |
| **UE5 Editor** | สร้าง `.ufont` assets | ⚡ แนะนำ |
| **Hex Editor** (HxD, 010) | วิเคราะห์ binary format | ⚡ สำหรับวิจัย |

---

## 11. สถิติม็อด

| ข้อมูล | จำนวน |
|---|---|
| **ไฟล์ทั้งหมด** | 9 ไฟล์ |
| **ขนาดรวม** | ~51.73 MB |
| **PAK entries** | 6 (fonts .ufont) |
| **LCACHE ขนาด** | 36.42 MB (encrypted) |
| **UCAS/UTOC IoStore Version** | 6 (UE5) |
| **ฟอนต์ TTF** | 6 ไฟล์ (5 มี Thai glyphs) |
| **ฟอนต์ UFont** | 6 ไฟล์ (อยู่ใน PAK) |

---

## 12. ความพิเศษของม็อดนี้

### 12.1 Alkimia Engine — เอนจินหายาก
Gothic Remake เป็นหนึ่งในเกมไม่กี่เกมที่ใช้ Alkimia Engine — ไม่มีเอกสารสาธารณะ ทำให้การ reverse engineer ต้องอาศัย community research

### 12.2 Encrypted Localization
LCACHE ขนาด 36MB ที่เข้ารหัสทั้งไฟล์ (entropy 7.8) — ม็อดเดอร์ต้องหาวิธี decrypt/re-encrypt ให้ได้ก่อนถึงจะแปลข้อความได้

### 12.3 Dual Font Pipeline
ต้องจัดการฟอนต์ 2 ระบบพร้อมกัน:
- UE5 `.ufont` (ใน PAK) สำหรับ UI
- Raw `.ttf` (ใน Story/) สำหรับ dialogue

### 12.4 UE5 IoStore + UE4 PAK
ม็อดใช้ทั้ง PAK (legacy) และ UCAS/UTOC (modern) — เป็นตัวอย่างของ UE5 ที่ยังรองรับ backward compatibility

---

## 13. เปรียบเทียบ

| เกม | Engine | Localization | Encryption | Font System |
|---|---|---|---|---|
| **Gothic Remake** | UE5 + Alkimia | LCACHE (encrypted) | ✅ Encrypted | Dual (ufont + TTF) |
| **Ghostrunner** | UE4 | LocRes (binary) | ❌ No | .ufont only |
| **Dead Island 2** | UE4 | LocRes (binary) | ❌ No | .ufont only |
| **33 Immortals** | Unity | Plaintext TXT | ❌ No | Built-in |

---

## 14. Conclusion

ม็อดภาษาไทยของ **Gothic Remake** เป็นตัวอย่างที่ซับซ้อนที่สุดของ **"Hybrid Engine Localization"**:

1. **Alkimia Engine Layer** — เอนจินเฉพาะของ THQ Nordic ที่ซ้อนทับ UE5 เพื่อจัดการ dialogue/quest/localization
2. **Encrypted LCACHE** — ข้อความแปลภาษา 36MB ถูกเข้ารหัสทั้งไฟล์ (entropy 7.8) — ท้าทายที่สุดในการ reverse engineer
3. **UE5 IoStore (v6)** — ใช้ระบบ UCAS/UTOC ล่าสุดของ UE5 ซึ่งยังเป็นที่ค่อนข้างใหม่สำหรับ modding community
4. **Dual Font System** — ต้องจัดการฟอนต์ 2 ระบบ: `.ufont` สำหรับ UE5 UI และ raw `.ttf` สำหรับ Alkimia dialogue
5. **Patch PAK Override** — ใช้ `_P` suffix เหมือน UE4 แบบเดิม ทำให้ติดตั้ง/ลบง่าย
6. **ฟอนต์ไทยพร้อมใช้** — ฟอนต์ TTF ทั้ง 5 ตัวมี Thai glyph ฝังมาแล้ว (ยืนยันจาก binary scan)

---

## 15. Extracted Assets

รายการไฟล์และทรัพยากรที่ถูกดึงออกมาจากม็อดนี้ เพื่อเก็บไว้ในคลังความรู้สำหรับการศึกษาหรือนำไปใช้งานต่อ:

- **Fonts:** [Assets/Fonts/](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unreal_Engine_5/Games/Gothic_Remake/Assets/Fonts)
  - `BerkshireSwash-Regular.ttf`
  - `Boucherie-Block.ttf`
  - `NotoSerif-*.ttf` (4 ไฟล์)
  - *ฟอนต์เหล่านี้เป็นไฟล์ TTF ดิบที่รวม Thai glyphs ไว้แล้ว สามารถติดตั้งและใช้งานได้ทันที*

- **Texts / Strings:** [Assets/Texts/](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unreal_Engine_5/Games/Gothic_Remake/Assets/Texts)
  - *ข้อความแปล:* ไม่สามารถดึงออกได้เนื่องจากระบบป้องกันของเกม (LCACHE File is encrypted - Entropy 7.8) ต้องใช้เครื่องมือเฉพาะของ Alkimia Engine ในการ Decrypt ก่อน
