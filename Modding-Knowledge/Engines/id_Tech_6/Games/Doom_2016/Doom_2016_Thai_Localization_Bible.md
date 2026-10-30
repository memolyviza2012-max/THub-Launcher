# DOOM (2016) — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
DOOM (2016) is a first-person shooter developed by **id Software** using the **id Tech 6** engine. The Thai localization mod uses a groundbreaking **Carrier Font Encoding** architecture — the most technically innovative modding approach in the entire Knowledge Base. Because id Tech 6 doesn't support Thai Unicode natively, the modder created a **custom font (tt_supermolot_thai)** where Thai glyphs are placed at Latin Extended codepoints (U+00C0–U+0198), and all translated text is pre-encoded through this mapping. The mod replaces 16 font definitions with Distance Field bitmaps, 320 compiled SWF UI screens (.bswf) with baked Thai text, and 11 language string files — all loaded through DOOMModLoader.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | id Tech 6 |
| **Developer** | id Software |
| **Mod Author** | ม็อดเดอร์ไทย (v1.4) |
| **Mod Loader** | DOOMModLoader v0.6 (ZwipZwapZapony) |
| **Archive Format** | Mod folder structure (no pak required) |
| **Font System** | id Font Distance Field (`idf+` magic, `.dat` metrics + `.bimage` atlas) |
| **Font Encoding** | **Carrier Font Map** — Thai mapped to Latin Extended (U+00C0–U+0198) |
| **Carrier Font** | `tt_supermolot_thai` — custom Distance Field font with Thai glyphs |
| **UI System** | Compiled SWF (`.bswf` = Binary SWF, id Tech's Flash-based UI) |
| **Text System** | `.bfile` (plain text key-value pairs) |
| **Text Encoding** | UTF-8 (carrier-encoded, not raw Thai) |
| **Mod Complexity** | ★★★★★ (Most complex mod in KB — carrier encoding + 16 fonts + 320 BSWF) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```text
Doom 2016/
├── DOOMModLoader.exe                     (5.6 MB — Mod loader by ZwipZwapZapony)
├── วิธีติดตั้ง.txt                       (Install instructions)
└── Mods/Thai/
    ├── fonts/                            (16 font directories — Distance Field metrics)
    │   ├── tt_supermolot_thai/64_df.dat  (5.7 KB — CARRIER FONT! Thai→Latin Extended)
    │   ├── tt_supermolot/64_df.dat       (5.7 KB)
    │   ├── tt_supermolot_bold/64_df.dat
    │   ├── tt_supermolot_light/64_df.dat
    │   ├── tt_supermolot_thin/64_df.dat
    │   ├── tt_supermolot_thin_mono/64_df.dat
    │   ├── eurostileconreg/64_df.dat     (4.9 KB — different glyph count)
    │   ├── pragmatica_book/64_df.dat     (4.9 KB)
    │   ├── idakagi_semibold/64_df.dat
    │   ├── korataki_rg/64_df.dat
    │   ├── microgrammadbolext/64_df.dat
    │   ├── square721_cn_tl/64_df.dat
    │   ├── square721_ex_tl/64_df.dat
    │   ├── uniwars_rg/64_df.dat
    │   ├── venacti_rg/64_df.dat
    │   └── zero_threes/64_df.dat
    │
    ├── generated/
    │   ├── binaryfile/strings/           (11 language files)
    │   │   ├── english.bfile             (2.8 MB — 181 #STR + 29 #font remaps)
    │   │   └── *.bfile × 10              (207B each — "Non-target language guard")
    │   │
    │   ├── decls/material/fonts/         (16 material declarations for fonts)
    │   │   └── */64_df.tga.decl          (~795B each — shader/material config)
    │   │
    │   ├── image/fonts/                  (16 Distance Field bitmap atlases)
    │   │   └── */64_df.tga$...bimage     (~1.4 MB each — compressed DF textures)
    │   │
    │   └── swf/                          (320 compiled SWF UI screens!)
    │       ├── hud/                      (4 files — HUD elements)
    │       ├── menu_shell/               (4 files — Main menus)
    │       ├── loading/                  (3+1 files — Loading screens)
    │       ├── dossier/                  (7 files — Codex entries)
    │       ├── narrative/                (1 file — Story screens)
    │       ├── stations/                 (11 files — Interactive stations)
    │       ├── switches/                 (27+ files — World switches/panels)
    │       ├── screens_whitecollar_corp/ (63 files! — Corporate displays)
    │       ├── screens_bluecollar/       (20 files — Industrial displays)
    │       ├── screens_tech/             (15 files — Tech displays)
    │       ├── screens_narrative/        (10 files — Narrative screens)
    │       ├── dlc/                      (15 files — DLC content)
    │       └── ... (36 categories total)
```

---

## 4. Font Analysis

### 4.1 id Font Distance Field System (`idf+`)
id Tech 6 ใช้ **Distance Field (DF) rendering** สำหรับฟอนต์ — เทคนิคที่ render ฟอนต์จาก distance field texture atlas (คล้ายกับ TMP SDF แต่เป็นระบบของ id Software เอง):
- **`.dat` file** (magic: `idf+`): เก็บ glyph metrics — ~284 glyphs per font (character code, position on atlas, size, advance width)
- **`.bimage` file** (magic: `Wp..`): Distance Field texture atlas — 1.4 MB per font, compressed proprietary format
- **`.decl` file**: Material declaration — ระบุ shader (`fontoutlineglowshadow`), texture path, และ rendering parameters

### 4.2 Carrier Font Encoding — เทคนิคระดับอัจฉริยะ! 🧠
เนื่องจาก id Tech 6 ไม่รองรับ Thai Unicode (U+0E00–U+0E7F) ม็อดเดอร์จึงใช้วิธี **Carrier Font Map**:

1. **สร้างฟอนต์ `tt_supermolot_thai`:** ฟอนต์พิเศษที่มี Thai glyphs วาดอยู่ที่ตำแหน่ง Latin Extended (U+00C0–U+0198)
2. **Encode ข้อความ:** แปลงอักษรไทยเป็นตัวอักษร Latin Extended ตาม mapping table
3. **Remap ฟอนต์ทั้งหมด:** ใช้ `#font_*` → `tt_supermolot_thai` เพื่อเปลี่ยนฟอนต์ทั้งเกมให้ใช้ carrier font

**Carrier Mapping (54 characters):**
```
Thai: ก ข ฃ ค ฅ ... (U+0E01-U+0E5B)
  ↓ mapped to ↓
Latin: À Á Ã Å Æ ... (U+00C0-U+0198)
```

### 4.3 Font Remapping System
ไฟล์ `english.bfile` มี 29 font remap entries ที่เปลี่ยนฟอนต์ทุกตัวในเกม:
```
"#font_akagi_medium"     → "tt_supermolot_thai"
"#font_courier"          → "tt_supermolot_thai"
"#font_zero_threes"      → "tt_supermolot_thai"
"#font_*"                → "tt_supermolot_thai"  // Wildcard catch-all!
```

### 4.4 16 Font Variants
แม้ทุกฟอนต์ถูก remap ไปที่ `tt_supermolot_thai` แต่ม็อดเดอร์สร้าง Distance Field atlas ให้ทั้ง 16 ชื่อฟอนต์เพื่อ compatibility กับ UI ที่อ้างอิงฟอนต์โดยตรง

---

## 5. Text Analysis

### 5.1 String Table (english.bfile)
- **Format:** Plain text key-value pairs (Tab-separated within `{}` block)
- **Content:** 181 `#STR_` entries (game text) + 29 `#font_` entries (font remaps)
- **Encoding:** UTF-8 with carrier-encoded Thai (ไม่มี Thai Unicode จริง!)
- **Example:**
  ```
  "#STR_SGL04_MAP_THEGAUNTLET"   "ÛŘƗÔĔƑŞƗÃĈŒŎÀƘŘŎÓ"
  ```
  (อ่านว่า: ตัวอักษร Latin Extended แต่แสดงเป็นอักษรไทยผ่าน carrier font)

### 5.2 Language Guard System
ม็อดแทนที่ไฟล์ทุกภาษา (chinese, french, german, etc.) ด้วยไฟล์ 207 bytes ที่เขียนว่า "Non-target language guard" เพื่อบังคับให้เกมโหลดเฉพาะ english.bfile

### 5.3 BSWF — Pre-compiled Flash UI
ส่วนที่ใหญ่ที่สุดของม็อด: **320 ไฟล์ .bswf (33 MB)** — เป็น UI screens ที่ถูก compile จาก Flash/SWF พร้อม Thai text baked in ไม่สามารถแก้ไขข้อความใน BSWF ได้โดยตรง ต้อง decompile → แก้ไข → recompile

---

## 6. Cross-Engine Comparison
เปรียบเทียบ carrier encoding กับวิธีอื่น:

| Feature | DOOM 2016 (id Tech 6) | Rogue Trader (Unity/TMP) | KCD2 (CryEngine) |
|---|---|---|---|
| **Thai Support** | ❌ ไม่รองรับ | ⚠️ ต้อง PUA | ⚠️ ต้อง Scaleform |
| **Workaround** | Carrier Font Map | PUA Stacking | Scaleform GFx injection |
| **Font Format** | Distance Field (idf+) | TMP SDF Atlas | Scaleform GFx (CFX) |
| **Text Encoding** | Carrier (Latin Ext→Thai) | PUA→Thai | UTF-8 direct |
| **UI System** | Flash/SWF (compiled) | Unity Canvas | CryEngine UI |
| **UI Modification** | 320 pre-compiled BSWF | None needed | None needed |
| **Complexity** | ★★★★★ | ★★★★☆ | ★★★☆☆ |

DOOM 2016 มี pipeline ที่ซับซ้อนที่สุดในคลัง — ต้องจัดการทั้ง carrier encoding, Distance Field font creation, และ 320 BSWF recompilation

---

## 7. Pipeline — ขั้นตอนสร้างม็อด

### Install Method (DOOMModLoader):
1. วาง `DOOMModLoader.exe` ในโฟลเดอร์เกม
2. วาง `Mods/Thai/` ในโฟลเดอร์เกม
3. รัน `DOOMModLoader.exe` (injects mod files into game runtime)

### Font Pipeline:
1. **สร้าง carrier font source:** ออกแบบ TTF ที่มี Thai glyphs วางอยู่ที่ Latin Extended positions
2. **Generate Distance Field:** ใช้ id Tech 6 tools สร้าง `64_df.dat` (metrics) + `64_df.bimage` (DF atlas)
3. **สร้าง material .decl:** ระบุ shader และ texture path
4. **ทำซ้ำ 16 ครั้ง** สำหรับแต่ละชื่อฟอนต์

### Text Pipeline:
1. **แปลข้อความ:** เขียนข้อความไทย
2. **Encode ผ่าน carrier map:** แปลง Thai → Latin Extended characters
3. **เขียน english.bfile:** Key-value format พร้อม #font_ remaps
4. **Guard other languages:** สร้าง 207B guard files สำหรับภาษาอื่น

### UI Pipeline:
1. **Decompile BSWF:** แปลง .bswf กลับเป็น SWF/FLA source
2. **แก้ไข text:** แทนที่ข้อความด้วย carrier-encoded Thai
3. **Recompile:** สร้าง .bswf ใหม่ (320 files!)

---

## 8. Troubleshooting
- **เกมไม่โหลดม็อด:** ตรวจว่า `DOOMModLoader.exe` อยู่ในโฟลเดอร์เกมหลัก
- **ฟอนต์ไม่แสดง:** ตรวจ `#font_*` remap ใน english.bfile ว่าชี้ไป `tt_supermolot_thai`
- **ข้อความเป็นภาษาต่างประเทศ:** ลบ cache — Steam > Properties > Installed Files > Verify integrity
- **UI ยังเป็นอังกฤษ:** BSWF files ต้องถูกแทนที่ครบทุกตัว (320 files)
- **ม็อดขัดข้อง:** ปิด Steam overlay (Settings > In-Game > uncheck overlay)

---

## 9. Required Tools
| Tool Name | Purpose | Source |
|---|---|---|
| DOOMModLoader v0.6 | Inject mods into DOOM runtime | [GitHub: ZwipZwapZapony] |
| id Tech 6 Font Tools | Generate Distance Field atlas + metrics | [id Software SDK] |
| SWF Decompiler (JPEXS) | Decompile/recompile .bswf Flash UI | [JPEXS FFDec] |
| Carrier Font Encoder | Convert Thai text → carrier encoding | Custom tool (ม็อดเดอร์) |

---

## 10. Extracted Assets
- **Carrier Font Files:**
  - [tt_supermolot_thai_64_df.dat](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/id_Tech_6/Games/Doom_2016/Assets/Fonts/carrier_dat/tt_supermolot_thai_64_df.dat) — idf+ Distance Field metrics (5.7 KB, ~284 glyphs)
  - [tt_supermolot_thai_64_df.bimage](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/id_Tech_6/Games/Doom_2016/Assets/Fonts/carrier_bimage/tt_supermolot_thai_64_df.bimage) — Distance Field texture atlas (1.4 MB)
  - [tt_supermolot_thai_64_df.decl](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/id_Tech_6/Games/Doom_2016/Assets/Fonts/tt_supermolot_thai_64_df.decl) — Material declaration
- **Note:** No TTF/OTF extractable. Distance Field atlas is id Tech 6 proprietary format.

---

## 11. M2M Protocol
**(สำหรับ AI Agent ที่ต้องการนำคัมภีร์ไปรันสร้างม็อดอัตโนมัติ)**

### 1. Carrier Encoding Engine
```python
# The carrier font map maps Thai Unicode to Latin Extended positions
# This mapping must match the glyph positions in tt_supermolot_thai font

CARRIER_MAP = {
    # Thai consonants → Latin Extended (approximate mapping, needs verification)
    # The actual map has 54 carrier chars covering U+00C0-U+0198
    # Map: Thai char → carrier char used in the font
}

# Example carrier chars found in english.bfile:
CARRIER_CHARS = "ÀÁÃÅÆÇÉÊÌÎÒÓÔÕÖØÙÚÛÜÝÞĀĂĄĈĊĎĐĒĔĖĘĜŃŅŇŎŐŒŘŞƄƆƉƊƎƐƑƓƔƖƗƘ"

def encode_thai_to_carrier(thai_text, carrier_map):
    """Convert Thai text to carrier-encoded text for id Tech 6"""
    result = []
    for c in thai_text:
        if c in carrier_map:
            result.append(carrier_map[c])
        else:
            result.append(c)  # Keep non-Thai chars as-is
    return ''.join(result)

def build_bfile(translations, font_remap='tt_supermolot_thai'):
    """Build a DOOM 2016 english.bfile"""
    lines = ['// Thai string table generated from english.bfile',
             '// Values are encoded through the DOOM 2016 Thai carrier font map.',
             '', '{']
    
    for key, value in translations.items():
        lines.append(f'\t"{key}"\t"{value}"')
    
    # Font remaps
    lines.append(f'\t"#font_*"\t"{font_remap}"')
    lines.append('}')
    
    return '\n'.join(lines)
```

### 2. ข้อจำกัดสำหรับ AI
- **Text Encoding:** ⚠️ AI สามารถ encode/decode carrier text ได้ **ถ้ารู้ mapping table** — แต่ mapping table ต้อง reverse-engineer จากม็อดต้นฉบับ
- **Font Creation:** ❌ ต้องใช้ id Tech 6 font tools สำหรับ Distance Field generation
- **BSWF Creation:** ❌ ต้อง decompile/recompile Flash UI (320 files) ด้วย specialized tools
- **Overall:** ม็อดนี้เป็นระดับ expert — ต้องใช้ custom toolchain ทั้งหมด
