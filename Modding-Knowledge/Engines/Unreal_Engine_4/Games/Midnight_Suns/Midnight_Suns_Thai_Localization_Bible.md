# Marvel's Midnight Suns — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Marvel's Midnight Suns is a tactical RPG developed by **Firaxis Games** (codename "Coda") using **Unreal Engine 4**. The Thai localization mod uses the classic **UE4 Pak Font Flooding + Locres Replacement** architecture — the same proven pattern as Borderlands 3. The mod floods all 38 font slots (25 game fonts + 13 engine fonts) with **Google Sans** (4 weight variants × 87 Thai glyphs), and replaces the `.locres` localization file with 1,792,657 Thai characters. A clean, efficient, one-pak mod.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Unreal Engine 4 (Firaxis, codename "Coda") |
| **Developer** | Firaxis Games / 2K |
| **Mod Author** | ม็อดเดอร์ไทย (v1.0) |
| **Archive Format** | `.pak` (UE4 standard, repak-compatible) |
| **AES Encryption** | No |
| **Compression** | Zlib (UE4 default) |
| **Font System** | `.ufont` (raw TTF at offset 0) + `.ttf` (Engine Slate fonts) |
| **Thai Font** | **Google Sans** (Regular, Bold, Italic, Bold Italic) |
| **Thai Coverage** | 87 codepoints (U+0E01–U+0E5B) |
| **Text System** | `.locres` (UE4 Localization Resource, UTF-16LE) |
| **Text Encoding** | UTF-16LE |
| **Mod Complexity** | ★★☆☆☆ (Standard UE4 font flood + locres, easy to reproduce) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```text
MidnightSuns/Content/Paks/~mods/
└── zzz_MarvelsMidnightSuns_Thai_P.pak    (8.6 MB — 38 files total)
    │
    ├── CodaGame/Content/Coda/UI/Fonts/Source/    (25 game .ufont files)
    │   ├── BodyFont_Thai.ufont              (112 KB — Google Sans Regular) ★
    │   ├── 1350_Primitive_Russian_R.ufont    (112 KB — Same as BodyFont_Thai)
    │   ├── MightMakesRightBB.ufont          (112 KB — Same)
    │   ├── connor-black.ufont               (112 KB — Google Sans Bold)
    │   ├── headingprodouble-italic.ufont     (114 KB — Google Sans Italic)
    │   ├── MightMakesRightBB_BoldItal.ufont  (114 KB — Google Sans BoldItalic)
    │   └── ... (25 files, 4 unique weights)
    │
    ├── Engine/Content/Slate/Fonts/               (13 engine .ttf files)
    │   ├── NotoSansThai-Regular.ttf         (112 KB — Google Sans Regular)
    │   ├── DFUniGothic-TH-W5.ttf            (112 KB — Google Sans Regular)
    │   ├── DroidSansMono.ttf                (112 KB — Google Sans Regular)
    │   ├── Roboto-Bold.ttf                  (112 KB — Google Sans Bold)
    │   ├── Roboto-Italic.ttf                (114 KB — Google Sans Italic)
    │   ├── Roboto-BoldItalic.ttf            (114 KB — Google Sans BoldItalic)
    │   └── ... (13 files, same 4 weights)
    │
    └── MidnightSuns/Content/Localization/CodaGame/en/
        └── CodaGame.locres                 (12.9 MB — translated text)
```

### Font Flooding Strategy:
| Google Sans Variant | Hash | Replaces (count) |
|---|---|---|
| **Regular** (114,652 B) | `a93067b6` | 19 font files (14 .ufont + 5 .ttf) |
| **Bold** (114,544 B) | `cc9ba05e` | 10 font files (7 .ufont + 3 .ttf) |
| **Italic** (116,548 B) | `907abe29` | 4 font files (3 .ufont + 1 .ttf) |
| **Bold Italic** (116,412 B) | `47b6d47a` | 4 font files (1 .ufont + 3 .ttf) |
| **Total** | **4 unique** | **38 font files** |

---

## 4. Font Analysis

### 4.1 Google Sans — ฟอนต์โดย Google
- **Full Name:** Google Sans Regular / Bold / Italic / Bold Italic
- **Version:** 13.002
- **Designer:** Google Sans Authors
- **Manufacturer:** Google LLC
- **License:** SIL Open Font License v1.1
- **Thai Coverage:** 87 codepoints across 4 segments:
  - U+0E01–U+0E3A (58 chars — พยัญชนะ + สระ)
  - U+0E3F–U+0E4F (17 chars — เครื่องหมาย ฿ + สระ + วรรณยุกต์)
  - U+0E50–U+0E59 (10 chars — เลขไทย ๐-๙)
  - U+0E5A–U+0E5B (2 chars — ฯลฯ, ๛)

### 4.2 Font Flooding — เทคนิคเดียวกับ Borderlands 3
ม็อดเดอร์แทนที่ฟอนต์ทุกตัวในเกม (25 game fonts + 13 engine fonts = 38 files) ด้วย Google Sans 4 weights — ฟอนต์ที่มีชื่อต่างกัน (เช่น "connor-black", "lionheart", "screter") ล้วนถูกแทนที่ด้วย Google Sans เพื่อให้ทุกข้อความแสดง Thai ได้

### 4.3 .ufont = Raw TTF
เหมือน Borderlands 3: ไฟล์ `.ufont` เป็น raw TTF โดยสมบูรณ์ (magic `\x00\x01\x00\x00` ที่ offset 0) สามารถ rename เป็น `.ttf` แล้วใช้ได้ทันที

---

## 5. Text Analysis
- **Format:** `.locres` (UE4 Localization Resource)
- **Encoding:** UTF-16LE
- **File:** `CodaGame.locres` (12.9 MB)
- **สถิติ:**
  - **1,792,657 Thai UTF-16LE characters** — อันดับ 3 ตลอดกาล!
  - 831,924 entries (ตามที่ม็อดเดอร์ระบุ)
  - 34 namespaces (ตามที่ม็อดเดอร์ระบุ)

### Thai Character Ranking (All-Time KB):
| อันดับ | เกม | Thai Chars |
|---|---|---|
| 🥇 1 | KCD2 | 5,170,838 |
| 🥈 2 | KCD1 | 3,314,378 |
| 🥉 3 | **Midnight Suns** | **1,792,657** |
| 4 | Borderlands 3 | ~1,520,000 |

---

## 6. Cross-Engine Comparison
เปรียบเทียบกับเกม UE4 อื่นในคลัง:

| Feature | Midnight Suns | Borderlands 3 | SpaceHulk Deathwing |
|---|---|---|---|
| **Engine** | UE4 (Coda) | UE4 | UE4 |
| **Font Format** | .ufont (raw TTF) | .ufont (raw TTF) | .ufont (raw TTF) |
| **Thai Font** | Google Sans | ไม่ทราบ | ไม่ทราบ |
| **Flooding Strategy** | 4 weights × 38 files | Similar | Similar |
| **Text Format** | .locres (UTF-16LE) | .locres (UTF-16LE) | .locres (UTF-16LE) |
| **Thai Chars** | 1.79M | ~1.52M | ~200K |
| **Complexity** | ★★☆☆☆ | ★★☆☆☆ | ★★☆☆☆ |

สถาปัตยกรรม UE4 ทั้ง 3 เกมเหมือนกันเกือบ 100% — ม็อดเดอร์ที่ทำเกมหนึ่งได้สามารถทำอีกเกมได้ทันที

---

## 7. Pipeline — ขั้นตอนสร้างม็อด

### Font Pipeline:
1. **เตรียมฟอนต์ TTF ที่มี Thai:** เช่น Google Sans, Noto Sans Thai
2. **Flood ทุก font slot:** Copy TTF เดียวกันไปทุกชื่อ .ufont + .ttf ในเกม
3. **จับคู่ weight:** Regular→Regular slots, Bold→Bold slots, Italic→Italic slots

### Text Pipeline:
1. **แตก .locres:** ใช้ UAssetGUI, UnrealLocres, หรือ custom parser
2. **แปลข้อความ:** UTF-16LE key-value pairs
3. **Pack กลับ:** สร้าง .locres ใหม่

### Pak Pipeline:
```bash
repak pack ./mod_content -o zzz_MarvelsMidnightSuns_Thai_P.pak
```

### Deployment:
```
GameFolder/MidnightSuns/Content/Paks/~mods/
└── zzz_MarvelsMidnightSuns_Thai_P.pak
```
ชื่อ `zzz_` prefix ทำให้ UE4 โหลดม็อดนี้ทีหลังเกม (override priority) `~mods/` คือ UE4 mod directory

---

## 8. Troubleshooting
- **ฟอนต์ไม่แสดงไทย:** ตรวจว่า font slot ทั้ง 38 ตัวถูกแทนที่ครบ
- **ข้อความยังเป็นอังกฤษ:** ต้องตั้งภาษาเกมเป็น English บน Steam
- **ตัวอักษรเล็กเกินไป:** Google Sans อาจมี metrics ต่างจากฟอนต์เดิม — ลองปรับ scaling ใน engine settings
- **เกมแครชเมื่อเปิด:** ตรวจว่า pak file อยู่ใน `~mods/` (ไม่ใช่ `Paks/` โดยตรง)
- **ยังเห็นฟอนต์เดิมบางจุด:** อาจมี font slot ที่ไม่ได้ flood — ตรวจ pak content

---

## 9. Required Tools
| Tool Name | Purpose | Source |
|---|---|---|
| repak | Pack/unpack UE4 .pak | [repak GitHub] |
| UnrealLocres / UAssetGUI | แก้ไข .locres | [GitHub] |
| Font Editor (FontForge) | ปรับแต่ง TTF font | [FontForge.org] |

---

## 10. Extracted Assets
- **Google Sans TTF Fonts (extracted from .ufont, ready to use):**
  - [GoogleSans-Regular.ttf](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unreal_Engine_4/Games/Midnight_Suns/Assets/Fonts/GoogleSans-Regular.ttf) — 112 KB (87 Thai chars)
  - [GoogleSans-Bold.ttf](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unreal_Engine_4/Games/Midnight_Suns/Assets/Fonts/GoogleSans-Bold.ttf) — 112 KB
  - [GoogleSans-Italic.ttf](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unreal_Engine_4/Games/Midnight_Suns/Assets/Fonts/GoogleSans-Italic.ttf) — 114 KB
  - [GoogleSans-BoldItalic.ttf](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unreal_Engine_4/Games/Midnight_Suns/Assets/Fonts/GoogleSans-BoldItalic.ttf) — 114 KB

---

## 11. M2M Protocol
**(สำหรับ AI Agent ที่ต้องการนำคัมภีร์ไปรันสร้างม็อดอัตโนมัติ)**

### 1. Automated Font Flood Builder
```python
import os
import shutil

def build_midnight_suns_font_flood(ttf_regular, ttf_bold, ttf_italic, ttf_bolditalic, output_dir):
    """Build font flood structure for Marvel's Midnight Suns"""
    
    # Game font slots
    REGULAR_SLOTS = [
        'CodaGame/Content/Coda/UI/Fonts/Source/1350_Primitive_Russian_R.ufont',
        'CodaGame/Content/Coda/UI/Fonts/Source/BodyFont_Thai.ufont',
        'CodaGame/Content/Coda/UI/Fonts/Source/MightMakesRightBB.ufont',
        'CodaGame/Content/Coda/UI/Fonts/Source/P22Moris-Tro.ufont',
        'CodaGame/Content/Coda/UI/Fonts/Source/headingprodouble-regular.ufont',
        'CodaGame/Content/Coda/UI/Fonts/Source/headingpromedium-regular.ufont',
        'CodaGame/Content/Coda/UI/Fonts/Source/lionheart.ufont',
        'CodaGame/Content/Coda/UI/Fonts/Source/molde-regular.ufont',
        'CodaGame/Content/Coda/UI/Fonts/Source/my_way.ufont',
        'CodaGame/Content/Coda/UI/Fonts/Source/quorthon-darkv.ufont',
        'CodaGame/Content/Coda/UI/Fonts/Source/screter.ufont',
        'CodaGame/Content/Coda/UI/Fonts/Source/straighttohellbb.ufont',
        'CodaGame/Content/Coda/UI/Fonts/Source/TankFont.ufont',
        'CodaGame/Content/Coda/UI/Fonts/Source/workshop_brushFont.ufont',
        'Engine/Content/Slate/Fonts/DFUniGothic-TH-W5.ttf',
        'Engine/Content/Slate/Fonts/DroidSansMono.ttf',
        'Engine/Content/Slate/Fonts/NotoSansThai-Regular.ttf',
        'Engine/Content/Slate/Fonts/Roboto-Light.ttf',
        'Engine/Content/Slate/Fonts/Roboto-Regular.ttf',
    ]
    
    BOLD_SLOTS = [
        'CodaGame/Content/Coda/UI/Fonts/Source/connor-black.ufont',
        'CodaGame/Content/Coda/UI/Fonts/Source/conseration-bold.ufont',
        'CodaGame/Content/Coda/UI/Fonts/Source/headingprodouble-bold.ufont',
        'CodaGame/Content/Coda/UI/Fonts/Source/headingpromedium-bold.ufont',
        'CodaGame/Content/Coda/UI/Fonts/Source/termina-black.ufont',
        'CodaGame/Content/Coda/UI/Fonts/Source/town10display-black.ufont',
        'CodaGame/Content/Coda/UI/Fonts/Source/watertown_black.ufont',
        'Engine/Content/Slate/Fonts/Roboto-Black.ttf',
        'Engine/Content/Slate/Fonts/Roboto-Bold.ttf',
        'Engine/Content/Slate/Fonts/Roboto-BoldCondensed.ttf',
    ]
    
    ITALIC_SLOTS = [
        'CodaGame/Content/Coda/UI/Fonts/Source/MightMakesRightBB_ital.ufont',
        'CodaGame/Content/Coda/UI/Fonts/Source/headingprodouble-italic.ufont',
        'CodaGame/Content/Coda/UI/Fonts/Source/molde-regularitalic.ufont',
        'Engine/Content/Slate/Fonts/Roboto-Italic.ttf',
    ]
    
    BOLDITALIC_SLOTS = [
        'CodaGame/Content/Coda/UI/Fonts/Source/MightMakesRightBB_BoldItal.ufont',
        'Engine/Content/Slate/Fonts/Roboto-BlackItalic.ttf',
        'Engine/Content/Slate/Fonts/Roboto-BoldCondensedItalic.ttf',
        'Engine/Content/Slate/Fonts/Roboto-BoldItalic.ttf',
    ]
    
    for slot in REGULAR_SLOTS:
        dest = os.path.join(output_dir, slot)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(ttf_regular, dest)
    
    for slot in BOLD_SLOTS:
        dest = os.path.join(output_dir, slot)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(ttf_bold, dest)
    
    for slot in ITALIC_SLOTS:
        dest = os.path.join(output_dir, slot)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(ttf_italic, dest)
    
    for slot in BOLDITALIC_SLOTS:
        dest = os.path.join(output_dir, slot)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(ttf_bolditalic, dest)
    
    print(f"Font flood: {len(REGULAR_SLOTS)+len(BOLD_SLOTS)+len(ITALIC_SLOTS)+len(BOLDITALIC_SLOTS)} files")
```

### 2. Automated Pak Builder
```bash
# Pack with repak
repak pack ./mod_content -o zzz_MarvelsMidnightSuns_Thai_P.pak

# Deploy
cp zzz_MarvelsMidnightSuns_Thai_P.pak "GameFolder/MidnightSuns/Content/Paks/~mods/"
```

### 3. ข้อจำกัดสำหรับ AI
- **Font Pipeline:** ✅ AI ทำได้ 100% — แค่ copy TTF ไปทุก slot
- **Text Pipeline:** ⚠️ AI อ่าน/เขียน .locres ได้แต่ต้องใช้ UE4 locres parser
- **Pak Pipeline:** ✅ AI ทำได้ 100% — repak CLI
