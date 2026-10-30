# Final Fantasy VII Rebirth — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
เอกสารนี้วิเคราะห์กลไกม็อดภาษาไทยของ **Final Fantasy VII Rebirth** (FF7 Rebirth) อย่างละเอียดที่สุด เกมนี้สร้างด้วย **Unreal Engine 5** (custom build โดย Square Enix) และใช้ระบบ localization เฉพาะที่เรียกว่า **TxtRes (Text Resource)** ซึ่งแบ่งข้อความตามบท/ภูมิภาคของเกม ม็อดนี้ใช้ระบบ **IoStore (UCAS/UTOC)** ที่เป็นรูปแบบ asset ล่าสุดของ UE5 ร่วมกับ **PAK v11** สำหรับ backward compatibility — ผนวกกับระบบ **Bitmap Font Atlas** แทนฟอนต์ TTF แบบเกม UE4 ทั่วไป

---

## 2. Technical Stack

| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Unreal Engine 5 (Square Enix custom build) |
| **Asset System** | **UE5 IoStore** (UCAS/UTOC v2/v3) + **PAK v11** (stub) |
| **Localization System** | **TxtRes** — custom Text Resource per chapter/region |
| **Font System** | **Bitmap Font Atlas** (pre-rendered glyph texture pages) |
| **Naming Convention** | `JP` prefix = Japanese slot ถูก override ด้วยข้อมูลไทย |
| **Compression** | IoStore native compression (entropy ~7.5-7.7) |
| **Mod Strategy** | **Patch PAK/IoStore** (`_P` suffix) |
| **Mod Complexity** | ★★★★★ (ระบบ font atlas ที่ซับซ้อน + IoStore + custom TxtRes) |

---

## 3. โครงสร้างไฟล์ (File Architecture)

### 3.1 ภาพรวม
```
(root)/
├── FF7RE2TH_FONT_P.pak     ←   339 B  (PAK v11 stub → ชี้ไป UCAS)
├── FF7RE2TH_FONT_P.ucas    ← 7.94 MB  (Font bitmap atlas textures)
├── FF7RE2TH_FONT_P.utoc    ← 17.5 KB  (Font table of contents)
├── FF7RE2TH_P.pak           ←   347 B  (PAK v11 stub → ชี้ไป UCAS)
├── FF7RE2TH_P.ucas          ← 1.89 MB  (TxtRes localization data)
└── FF7RE2TH_P.utoc          ← 5.25 KB  (Main table of contents)
```

### 3.2 ขนาดรวม
| ไฟล์ | ขนาด | เนื้อหา |
|---|---|---|
| Font PAK+UCAS+UTOC | **7.96 MB** | 38 font texture pages |
| Main PAK+UCAS+UTOC | **1.89 MB** | 12 TxtRes + font definitions |
| **รวมทั้งหมด** | **~9.85 MB** | |

### 3.3 Naming Convention
```
FF7RE2TH = Final Fantasy 7 REbirth 2 THai
                            ↑ ↑↑     ↑↑
                            RE birth  TH = Thai locale
```
`_P` = Patch (override), `_FONT` = Font-specific patch

---

## 4. PAK v11 — Stub Architecture

### 4.1 ทำไม PAK ถึงเล็กมาก? (339-347 bytes)
FF7 Rebirth ใช้ **PAK v11** ซึ่งเป็นเวอร์ชันล่าสุดของ UE5 ที่ทำหน้าที่เป็น **stub** — เก็บเพียง:
- Header + footer information
- Index pointer ที่ชี้ไปยังไฟล์ UCAS/UTOC ที่เก็บ data จริง

เนื้อหาทั้งหมดถูกเก็บใน **UCAS** (Content Archive Store) และ index อยู่ใน **UTOC** (Table of Contents)

### 4.2 PAK Header
| ฟิลด์ | Font PAK | Main PAK |
|---|---|---|
| **Size** | 339 bytes | 347 bytes |
| **Magic** | `E1 12 6F 5A` | `E1 12 6F 5A` |
| **Version** | 11 | 11 |
| **Mount Point** | (embedded in UTOC) | `../../../` |

---

## 5. IoStore System (UCAS/UTOC)

### 5.1 UTOC — Table of Contents
| ฟิลด์ | Font UTOC | Main UTOC |
|---|---|---|
| **Magic** | `-==--==--==--==-` | `-==--==--==--==-` |
| **Version** | 2 | 3 |
| **Size** | 17,886 bytes | 5,380 bytes |
| **Mount Point** | `../../../End/Content/Menu/Billboard/Common/` | (root) |

### 5.2 UCAS — Content Archive Store
| ฟิลด์ | Font UCAS | Main UCAS |
|---|---|---|
| **Size** | 7.94 MB | 1.89 MB |
| **Entropy** | 7.504 | 7.698 |
| **Content** | Bitmap font textures | TxtRes + font defs |

> **สำคัญ:** Entropy 7.5-7.7 = **compressed** (ไม่ใช่ encrypted) — ข้อมูลถูกบีบอัดด้วย IoStore native compression แต่ยังสามารถ decompress ได้ด้วย UnrealPak

---

## 6. TxtRes — ระบบข้อความ

### 6.1 TxtRes คืออะไร?
**TxtRes (Text Resource)** เป็น format เฉพาะของ Square Enix สำหรับ FF7 Rebirth ที่แบ่งข้อความตาม **บท/ภูมิภาค** ของเกม — แตกต่างจาก LocRes ที่เป็นมาตรฐาน UE4/UE5

### 6.2 ไฟล์ TxtRes ทั้ง 12 ไฟล์
| ไฟล์ | Code | ภูมิภาค/บท |
|---|---|---|
| `0005-TITLB_TxtRes.uasset` | TITLB | Title / บทนำ |
| `4000-MIDGR_TxtRes.uasset` | MIDGR | Midgar / มิดการ์ |
| `8100-GRASE_TxtRes.uasset` | GRASE | Grasslands / ทุ่งหญ้า |
| `8200-JUNOE_TxtRes.uasset` | JUNOE | Junon / จูนอน |
| `8300-CORLE_TxtRes.uasset` | CORLE | Corel / คอเรล |
| `8400-GOLDE_TxtRes.uasset` | GOLDE | Gold Saucer / โกลด์ซอเซอร์ |
| `8500-GONGE_TxtRes.uasset` | GONGE | Gongaga / กอนกากา |
| `8600-COSME_TxtRes.uasset` | COSME | Cosmo Canyon / คอสโมแคนยอน |
| `8700-NIBLE_TxtRes.uasset` | NIBLE | Nibelheim / นิเบลไฮม์ |
| `8800-FOREE_TxtRes.uasset` | FOREE | Forgotten Capital / ป่า |
| `8900-CAPIT_TxtRes.uasset` | CAPIT | Final Chapter / บทสุดท้าย |
| `Resident_TxtRes.uasset` | — | **Common/Shared** (โหลดตลอด) |

> **ระบบ Region-Based Loading:** เกมโหลดเฉพาะ TxtRes ของภูมิภาคที่ผู้เล่นอยู่ + Resident (ตลอดเวลา) — ช่วยลดการใช้ RAM

### 6.3 Language Slot Strategy
ชื่อไฟล์ `FF7RE2TH` มี `TH` = Thai locale — แต่ prefix `U_Com_JP_` ในฟอนต์บ่งบอกว่าม็อด **override slot ของญี่ปุ่น (JP)**:
- ผู้เล่นเลือกภาษาญี่ปุ่นในเกม → เกมโหลด assets ที่มี `JP` prefix
- ม็อดแทนที่ assets `JP` ด้วยข้อความ+ฟอนต์ไทย → แสดงเป็นภาษาไทย

---

## 7. Font System — Bitmap Font Atlas

### 7.1 ทำไมไม่ใช้ TTF?
FF7 Rebirth **ไม่ใช้ .ufont หรือ .ttf** แบบเกม UE ทั่วไป — แต่ใช้ **Bitmap Font Atlas** (pre-rendered glyph textures) แทน:
- แต่ละ "หน้า" ของ font atlas เป็น **texture ที่ render glyph ไว้ล่วงหน้า**
- เกมใช้ lookup table เพื่อหาตำแหน่ง glyph บน texture
- วิธีนี้ให้ **quality สูงกว่า** runtime rendering เพราะ glyph ถูก anti-alias ไว้แล้ว

### 7.2 Font Asset Categories
| หมวด | จำนวน pages | ความละเอียด | หน้าที่ |
|---|---|---|---|
| **LatinFontLarge** | 12 + 9 (4K) | Normal + 4K | ชื่อเมนู, หัวข้อ, billboard |
| **SystemFontLarge** | 1 + 3 (4K) | Normal + 4K | UI ขนาดใหญ่ |
| **SystemFontNormal** | 1 + 2 (4K) | Normal + 4K | UI ขนาดปกติ |
| **SystemFontSmall** | 1 + 2 (4K) | Normal + 4K | UI ขนาดเล็ก |
| **SystemFontXLarge** | 4 + 3 (4K) | Normal + 4K | UI ขนาดใหญ่พิเศษ |
| **รวม** | **38 pages** | | |

### 7.3 4K Support
ม็อดมีฟอนต์ **2 ชุด**:
- **Normal resolution** — สำหรับ 1080p
- **4K resolution** — สำหรับ 4K displays (เพิ่มรายละเอียด glyph)

### 7.4 ผลกระทบต่อม็อดเดอร์
การทำฟอนต์ไทยสำหรับ FF7 Rebirth **ยากกว่าเกมอื่นมาก**:
1. ต้อง **render glyph ภาษาไทย** ลง texture atlas (ไม่ใช่แค่ swap TTF)
2. ต้องสร้าง **glyph lookup table** ที่ถูกต้อง (ตำแหน่ง x,y,width,height ของทุก glyph)
3. ต้องทำ **2 ชุด** (Normal + 4K)
4. ต้องจัดการ **สระลอย, วรรณยุกต์ซ้อน** ที่เป็นความท้าทายของอักษรไทย

---

## 8. Complete Pipeline — ขั้นตอนสร้างม็อด

```
ขั้นตอนที่ 1: แตก IoStore
    ใช้ UnrealPak (UE5 SDK) กับ IoStore support:
    UnrealPak.exe -Extract FF7RE2TH_P.ucas
    UnrealPak.exe -Extract FF7RE2TH_FONT_P.ucas
    → ได้ TxtRes .uasset files + Font texture .uasset files
        ↓
ขั้นตอนที่ 2: แก้ไข TxtRes
    ใช้เครื่องมือ: FF7R TxtRes Editor (community tool) หรือ hex editor
    - แก้ไขข้อความในแต่ละ TxtRes file
    - แปลจากญี่ปุ่น/อังกฤษเป็นไทย
    - ต้องรักษาโครงสร้าง binary ของ TxtRes ไว้
        ↓
ขั้นตอนที่ 3: สร้าง Font Atlas
    - Render glyph ภาษาไทยทั้งหมดลง texture (PNG/DDS)
    - สร้าง glyph metrics table (UV coordinates, advance width, bearing)
    - ทำ 2 ชุด: Normal + 4K resolution
    - Pack เป็น UAsset format
        ↓
ขั้นตอนที่ 4: Repack IoStore
    ใช้ UnrealPak:
    - Pack TxtRes กลับเข้า FF7RE2TH_P.ucas/utoc
    - Pack Font textures กลับเข้า FF7RE2TH_FONT_P.ucas/utoc
    - สร้าง PAK stub files
        ↓
ขั้นตอนที่ 5: วางไฟล์
    คัดลอก 6 ไฟล์ไปที่:
    {GameInstall}/End/Content/Paks/
        ↓
เสร็จสิ้น! เปิดเกม → เลือกภาษาญี่ปุ่น → แสดงเป็นภาษาไทย
```

---

## 9. Required Tools

| เครื่องมือ | หน้าที่ | ระดับความจำเป็น |
|---|---|---|
| **UnrealPak (UE5 SDK)** | Pack/Unpack IoStore (UCAS/UTOC) | ✅ จำเป็น |
| **FF7R TxtRes Editor** | แก้ไข TxtRes binary | ✅ จำเป็น |
| **Bitmap Font Generator** (BMFont, Hiero) | สร้าง glyph atlas | ✅ จำเป็น |
| **Image Editor** (Photoshop, GIMP) | ตรวจสอบ/แก้ไข font textures | ✅ จำเป็น |
| **UAsset Tool** | แก้ไข UAsset metadata | ⚡ แนะนำ |

---

## 10. สถิติม็อด

| ข้อมูล | จำนวน |
|---|---|
| **ไฟล์ม็อด** | 6 ไฟล์ (3 ชุด PAK+UCAS+UTOC) |
| **ขนาดรวม** | ~9.85 MB |
| **PAK Version** | 11 (UE5 stub) |
| **IoStore Version** | 2 (Font) / 3 (Main) |
| **TxtRes files** | 12 (11 chapters + 1 Resident) |
| **Font texture pages** | 38 (Normal + 4K) |
| **Font categories** | 5 (LatinLarge, SysLarge, SysNormal, SysSmall, SysXLarge) |

---

## 11. TxtRes Chapter Mapping

| Code | ชื่อเต็ม | เนื้อหาโดยประมาณ |
|---|---|---|
| **TITLB** | Title/Opening | หน้าจอเปิดเกม, เมนูหลัก |
| **MIDGR** | Midgar | บทที่เกิดใน Midgar (จุดเริ่มต้น) |
| **GRASE** | Grasslands | ทุ่งหญ้า, พื้นที่เปิดแรก |
| **JUNOE** | Junon | เมือง Junon, ท่าเรือ |
| **CORLE** | Corel | Corel, เหมืองแร่ |
| **GOLDE** | Gold Saucer | สวนสนุก Gold Saucer |
| **GONGE** | Gongaga | หมู่บ้าน Gongaga |
| **COSME** | Cosmo Canyon | Cosmo Canyon, ดาวเทียม |
| **NIBLE** | Nibelheim | Nibelheim, บ้านเกิด Cloud |
| **FOREE** | Forgotten Forest | ป่าลึกลับ, Temple of Ancients |
| **CAPIT** | Capital/Final | บทจบ |
| **Resident** | Common | ข้อความที่ใช้ร่วมทุกบท |

---

## 12. เปรียบเทียบ

| เกม | Engine | Localization | Font | IoStore | Complexity |
|---|---|---|---|---|---|
| **FF7 Rebirth** | UE5 (SE) | TxtRes (custom) | Bitmap Atlas | v2/v3 | ★★★★★ |
| **Gothic Remake** | UE5+Alkimia | LCACHE (encrypted) | Dual (ufont+TTF) | v6 | ★★★★☆ |
| **Ghostrunner** | UE4 | LocRes (binary) | .ufont | N/A (PAK v3) | ★★★☆☆ |
| **Dead Island 2** | UE4 | LocRes (binary) | .ufont | N/A | ★★★☆☆ |

---

## 13. Conclusion

ม็อดภาษาไทยของ **Final Fantasy VII Rebirth** เป็นตัวอย่างที่ซับซ้อนที่สุดในคลังความรู้ของเรา:

1. **TxtRes (Custom Format)** — Square Enix สร้าง format เฉพาะที่แบ่งข้อความตามบท/ภูมิภาค (12 ไฟล์) ไม่ใช่ LocRes มาตรฐาน
2. **Bitmap Font Atlas** — ฟอนต์ไม่ใช่ TTF แต่เป็น **texture ที่ render glyph ไว้ล่วงหน้า** (38 pages) ทำให้การสร้างฟอนต์ไทยยากเป็นพิเศษ
3. **4K Dual Resolution** — ต้องสร้างฟอนต์ 2 ชุด (Normal + 4K) สำหรับ display ต่างๆ
4. **IoStore (UCAS/UTOC)** — ใช้ระบบ packaging ล่าสุดของ UE5 (PAK เป็นแค่ stub 339 bytes)
5. **JP Slot Override** — ใช้ slot ภาษาญี่ปุ่น (`U_Com_JP_*`) ในการแทนที่ เพราะ glyph space ของ JP ใหญ่พอสำหรับไทย
6. **Region-Based Loading** — เกมโหลดข้อความเฉพาะภูมิภาคที่ผู้เล่นอยู่ (เทคนิคลด RAM)

---

## 14. Extracted Assets

รายการไฟล์และทรัพยากรที่ถูกดึงออกมาจากม็อดนี้:

- **Fonts:** [Assets/Fonts/](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unreal_Engine_5/Games/FF7_Rebirth/Assets/Fonts)
  - *Font assets เป็น Bitmap Atlas textures ภายใน UCAS (ไม่ใช่ TTF/OTF) — ต้องใช้ UnrealPak + IoStore extractor เพื่อแตกออก*

- **Texts / Strings:** [Assets/Texts/](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unreal_Engine_5/Games/FF7_Rebirth/Assets/Texts)
  - *TxtRes files อยู่ใน UCAS IoStore container (compressed) — ต้องใช้ UnrealPak เพื่อแตก*

- **Configs / Metadata:** [Assets/Configs/](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unreal_Engine_5/Games/FF7_Rebirth/Assets/Configs)
  - [FontUTOC_Listing.txt](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unreal_Engine_5/Games/FF7_Rebirth/Assets/Configs/FontUTOC_Listing.txt) — รายชื่อ font texture assets ทั้ง 38 ไฟล์
  - [MainUTOC_Listing.txt](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unreal_Engine_5/Games/FF7_Rebirth/Assets/Configs/MainUTOC_Listing.txt) — รายชื่อ TxtRes + font definition assets ทั้ง 32 ไฟล์
