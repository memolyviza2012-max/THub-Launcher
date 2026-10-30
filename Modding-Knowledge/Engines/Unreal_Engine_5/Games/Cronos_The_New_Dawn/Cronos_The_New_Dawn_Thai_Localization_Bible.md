# Cronos: The New Dawn — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer) — ตัวอักษรมีหัว Variant

---

## 1. Overview
เอกสารนี้วิเคราะห์กลไกม็อดภาษาไทยของ **Cronos: The New Dawn** อย่างละเอียดที่สุด เกมนี้สร้างด้วย **Unreal Engine 5** และใช้ระบบ localization มาตรฐาน **LocRes** แบ่งเป็น 2 ไฟล์ (Game + Dialog) ม็อดนี้สร้างโดย **Artdekdok** (Facebook: notreadynotgive) และมาในรูปแบบ PAK v4 ไฟล์เดียวที่เก็บทั้ง LocRes 2 ไฟล์ + ฟอนต์ 39 entries — โดดเด่นด้วย **ชุดฟอนต์ไทย 5 ตระกูล** ที่ถูกฝังอยู่ภายใน .ufont (Zlib compressed) รวมถึง **109PANIChalam** ซึ่งเป็นฟอนต์ไทยแบบ "มีหัว" (Serif/Looped glyphs)

---

## 2. Technical Stack

| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Unreal Engine 5 |
| **Asset System** | PAK v4 (single file, Zlib compression) |
| **Localization System** | **LocRes** × 2 (Game + Dialog, แยกข้อความเกมกับบทสนทนา) |
| **LocRes Locale Slot** | `en/` (English slot override) |
| **Font System** | `.ufont` + `.ttf` (ฝัง TTF ภายใน UAsset + Slate raw TTF) |
| **Compression** | Zlib (163 blocks) |
| **Mod Author** | Artdekdok (FB: notreadynotgive) |
| **Mod Version** | v1.0 (Game ver.20251021_1503-330668) |
| **Mod Strategy** | PAK Patch override (`_P` suffix) ใน `~mods` folder |
| **Mod Complexity** | ★★★☆☆ (มาตรฐาน UE5 แต่มีฟอนต์เยอะ) |
| **Variant** | **ตัวอักษรมีหัว** (Looped/Serif Thai glyphs) |

---

## 3. โครงสร้างไฟล์ (File Architecture)

### 3.1 ภาพรวม
```
(root)/
├── ตัวอักษรมีหัว/                           ← โฟลเดอร์ variant
│   └── Cronos_TH-Artdekdok_P.pak         ← 2.17 MB  ★ ไฟล์ม็อดหลัก (PAK v4)
├── ภาพตย.jpg                                ← 170 KB  (รูปตัวอย่างม็อด)
└── คำอธิบาย.txt                              ← 1.2 KB  (คำอธิบายการติดตั้ง)
```

### 3.2 เนื้อหาภายใน PAK (39 entries)
```
Cronos_TH-Artdekdok_P.pak
├── Cronos/Content/Game/UI/Fonts/             ← 6 ufont (Game-specific fonts)
│   ├── Atkinson-Hyperlegible-{Bold,BoldItalic,Regular}-102.ufont (3)
│   └── JetBrainsMono-{ExtraBold,Regular}.ufont + NL-SemiBold.ufont (3)
├── Cronos/Content/Localization/
│   ├── Game/en/Game.locres                   ★ ข้อความเกม (UI, items, menus)
│   └── Dialog/en/Dialog.locres               ★ บทสนทนาตัวละคร
├── Engine/Content/EngineFonts/Faces/         ← 6 ufont (Engine fonts)
│   ├── DroidSansFallback.ufont
│   ├── DroidSansMono.ufont
│   └── Roboto-{Bold,BoldItalic,Light,Regular}.ufont (4)
└── Engine/Content/Slate/Fonts/               ← 13 ttf (Slate UI raw fonts)
    ├── NotoSansThai-Regular.ttf              ★ ฟอนต์ไทย Slate
    ├── DroidSans{Fallback,Mono}.ttf (2)
    └── Roboto-{Black,BlackItalic,Bold,...}.ttf (10)
```

### 3.3 ขนาดรวม
| รายการ | ขนาด |
|---|---|
| `Cronos_TH-Artdekdok_P.pak` | 2.17 MB |
| ภาพตย.jpg | 170 KB |
| คำอธิบาย.txt | 1.2 KB |
| **รวม** | **~2.34 MB** |

---

## 4. PAK Analysis

### 4.1 PAK Header
| ฟิลด์ | ค่า |
|---|---|
| **Format** | UE PAK v4 |
| **Magic** | `E1 12 6F 5A` |
| **Mount Point** | `../../../` |
| **Entry Count** | 39 |
| **Index Offset** | 2,270,521 |
| **Index Size** | 6,942 bytes |
| **Compression** | Zlib (163 blocks) |
| **Install Path** | `{GameInstall}/Cronos/Content/Paks/` |

### 4.2 `_P` Suffix + `~mods` Folder
- `_P` = Patch — override `pakchunk0-Windows` เดิมของเกม
- ม็อดวางใน `~mods` subfolder ที่ UE5 สแกนอัตโนมัติ
- ข้อความจาก README: *"คัดลอก Cronos_TH-Artdekdok_P.pak ไปวางที่ Cronos\Content\Paks โฟลเดอร์"*

---

## 5. Dual LocRes — ระบบข้อความ

### 5.1 ทำไมต้อง 2 LocRes?
Cronos แบ่ง localization เป็น **2 domain**:

| LocRes | Path | เนื้อหา |
|---|---|---|
| **Game.locres** | `Cronos/Content/Localization/Game/en/` | UI, menus, items, tutorials, system messages |
| **Dialog.locres** | `Cronos/Content/Localization/Dialog/en/` | บทสนทนาตัวละคร, cutscene text, NPC lines |

> **ข้อดี:** ม็อดเดอร์สามารถอัปเดต Dialog กับ Game แยกกันได้ ไม่ต้อง repack ทั้งหมด

### 5.2 English Slot Override
ทั้ง 2 LocRes อยู่ใน folder `en/` = override ภาษาอังกฤษ (วิธีมาตรฐาน UE5)

---

## 6. Font System — 5 ตระกูลฟอนต์ไทย

### 6.1 ฟอนต์ไทยที่ดึงออกมาได้ (11 ไฟล์ TTF จริง)

#### 🇹🇭 109PANIChalam — ฟอนต์ไทยมีหัว (Looped Glyphs)
| ฟอนต์ | ขนาด | ลักษณะ |
|---|---|---|
| **109PANIChalam.ttf** | 53.4 KB | Regular — **ตัวอักษรมีหัว** (serif/looped) |
| **109PANIChalamBold.ttf** | 53.1 KB | Bold |

> **"109PANIChalam"** = ฟอนต์จาก **109 ฟอนต์ไทย** (PANI Series) ชื่อ "ชะลัม" — เป็นฟอนต์ที่มี **หัวตัวอักษร** (เส้นวนที่หัวพยัญชนะไทย) ซึ่งเป็นรูปแบบดั้งเดิมของอักษรไทย ตรงกับชื่อ variant ของม็อด "ตัวอักษรมีหัว"

#### 🔬 Chakra Petch — Display/UI Font
| ฟอนต์ | ขนาด | ลักษณะ |
|---|---|---|
| **Chakra_Petch_Bold.ttf** | 64 KB | Bold |
| **Chakra_Petch_Medium.ttf** | 64 KB | Medium |
| **Chakra_Petch_SemiBold.ttf** | 64 KB | SemiBold |

> **Chakra Petch** = ฟอนต์ไทย-อังกฤษจาก Google Fonts (Cadson Demak) สไตล์ tech/futuristic ที่เหมาะกับเกม sci-fi

#### 📱 MiSans Thai — Xiaomi System Font
| ฟอนต์ | ขนาด | ลักษณะ |
|---|---|---|
| **MiSans_Thai.ttf** | 45.6 KB | Regular |
| **MiSans_Thai_Bold.ttf** | 45 KB | Bold |
| **MiSans_Thai_Semibold.ttf** | 45 KB | Semibold |

> **MiSans Thai** = ฟอนต์จาก Xiaomi สำหรับ MIUI — เป็น Sans-serif ที่สะอาดและอ่านง่ายบนจอ

#### ✍️ Playpen Sans Thai — Handwriting Style
| ฟอนต์ | ขนาด | ลักษณะ |
|---|---|---|
| **Playpen_Sans_Thai_Bold.ttf** | 64 KB | Bold |
| **Playpen_Sans_Thai_Regular.ttf** | 64 KB | Regular |

> **Playpen Sans Thai** = ฟอนต์ลายมือจาก Google Fonts สไตล์ casual handwriting

#### 📄 Noto Sans Thai — Standard Thai
| ฟอนต์ | ขนาด | ลักษณะ |
|---|---|---|
| **Noto_Sans_Thai_Regular.ttf** | 38.2 KB | Regular |

> **Noto Sans Thai** = ฟอนต์มาตรฐานจาก Google สำหรับอักษรไทย ใช้สำหรับ Slate UI (Engine-level)

### 6.2 ฟอนต์เกม (Non-Thai)

#### Game UI Fonts
| ฟอนต์ | ประเภท | หน้าที่ |
|---|---|---|
| **Atkinson Hyperlegible** (3 weights) | Accessibility | ฟอนต์ที่ออกแบบเพื่อให้อ่านง่าย (accessibility-first) |
| **JetBrains Mono** (3 weights) | Monospace | ฟอนต์สำหรับ code/terminal-style UI |

#### Engine Fonts
| ฟอนต์ | จำนวน |
|---|---|
| DroidSans (Fallback + Mono) | 2 ufont + 2 ttf |
| Roboto (6 weights + 4 extra) | 4 ufont + 10 ttf |

---

## 7. "ตัวอักษรมีหัว" คืออะไร?

ม็อดนี้เป็น variant **"ตัวอักษรมีหัว"** ซึ่งหมายถึงรูปแบบตัวอักษรไทยที่มี **หัว** (loop) ที่ส่วนบนของพยัญชนะ:

```
ตัวอักษรมีหัว (Looped):    ก ข ค ง จ    ← มีเส้นวนที่หัว (traditional)
ตัวอักษรไม่มีหัว (Loopless): ก ข ค ง จ  ← ตัดหัวออก (modern/clean)
```

ฟอนต์ **109PANIChalam** เป็นฟอนต์ "มีหัว" ตรงตามชื่อ variant — ในขณะที่ม็อดอาจมี variant อื่นที่ใช้ฟอนต์ "ไม่มีหัว" (loopless) แทน

---

## 8. Complete Pipeline — ขั้นตอนสร้างม็อด

```
ขั้นตอนที่ 1: สกัด LocRes จากเกม
    ใช้ UnrealPak:
    UnrealPak.exe -Extract pakchunk0-Windows.pak
    → ได้ Game.locres + Dialog.locres ต้นฉบับ (English)
        ↓
ขั้นตอนที่ 2: แปลข้อความ
    - แปล Game.locres (UI, menus, items)
    - แปล Dialog.locres (บทสนทนาตัวละคร)
        ↓
ขั้นตอนที่ 3: เตรียมฟอนต์
    - ดาวน์โหลดฟอนต์ไทย (109PANIChalam, Chakra Petch, MiSans, Playpen Sans, Noto Sans)
    - Wrap เป็น .ufont สำหรับ Game UI + Engine fonts
    - วาง .ttf สำหรับ Slate UI
        ↓
ขั้นตอนที่ 4: Pack PAK
    ใช้ UnrealPak:
    - รวม LocRes × 2 + Fonts × 25 → Cronos_TH-Artdekdok_P.pak
        ↓
ขั้นตอนที่ 5: ติดตั้ง
    วาง PAK ไปที่: {GameInstall}/Cronos/Content/Paks/
        ↓
เสร็จสิ้น!
```

---

## 9. Required Tools

| เครื่องมือ | หน้าที่ | ระดับความจำเป็น |
|---|---|---|
| **UnrealPak** (UE5 SDK) | Pack/Unpack PAK v4 | ✅ จำเป็น |
| **LocRes Editor** | แก้ไข LocRes binary | ✅ จำเป็น |
| **UE5 Editor** | สร้าง .ufont UAsset | ⚡ แนะนำ |
| **FontForge** | ตรวจสอบ/ปรับแต่งฟอนต์ | ⚡ สำหรับวิจัย |

---

## 10. สถิติม็อด

| ข้อมูล | จำนวน |
|---|---|
| **ไฟล์ม็อดหลัก** | 1 ไฟล์ (PAK v4) |
| **ขนาดรวม** | 2.17 MB |
| **PAK Version** | 4 |
| **PAK Entries** | 39 (2 LocRes + 12 ufont + 13 ttf + 12 misc) |
| **LocRes files** | 2 (Game + Dialog) |
| **ฟอนต์ไทยที่ดึงออกมา** | 11 TTF (5 ตระกูล) |
| **ฟอนต์ Game UI** | Atkinson Hyperlegible (3) + JetBrains Mono (3) |
| **ฟอนต์ Engine** | DroidSans (4) + Roboto (14) |

---

## 11. ความพิเศษของม็อดนี้

### 11.1 Multi-Font Thai Typography
ม็อดนี้มี **5 ตระกูลฟอนต์ไทย** ครอบคลุมหลายสไตล์:
- **109PANIChalam** — Serif/Looped (ดั้งเดิม, มีหัว)
- **Chakra Petch** — Tech/Futuristic display
- **MiSans Thai** — Clean system font
- **Playpen Sans Thai** — Handwriting casual
- **Noto Sans Thai** — Standard reference

### 11.2 Dual LocRes (Game + Dialog)
แบ่ง localization เป็น 2 domain — Game (UI/system) กับ Dialog (บทสนทนา) อัปเดตแยกกันได้

### 11.3 "มีหัว" Variant
ม็อดนี้เป็น variant เฉพาะ สำหรับผู้เล่นที่ชอบตัวอักษรไทยแบบดั้งเดิม (looped glyphs)

### 11.4 Accessibility-First Game Fonts
เกม Cronos ใช้ **Atkinson Hyperlegible** ซึ่งเป็นฟอนต์ที่ออกแบบเพื่อ accessibility — ตัวอักษรที่คล้ายกันมีความแตกต่างชัดเจน (เช่น I, l, 1 ดูต่างกัน)

### 11.5 Raw TTF Extraction Success
ถึงแม้ PAK ใช้ Zlib compression แต่สามารถ **decompress แล้วดึง TTF จริง** ออกมาได้สำเร็จ 11 ไฟล์

---

## 12. เปรียบเทียบ

| เกม | Engine | PAK Ver | LocRes | Font Count | Thai Fonts | Complexity |
|---|---|---|---|---|---|---|
| **Cronos: The New Dawn** | UE5 | 4 | 2 (Game+Dialog) | 39 | 5 families (11 files) | ★★★☆☆ |
| **Code Vein II** | UE5 | 3 + IoStore v6 | 1 | 16 (UCAS) | 1 (Sarabun) | ★★★★☆ |
| **Lords of the Fallen** | UE5 | 11 | 1 | 31 | 1 (NotoSansThai) | ★★★☆☆ |
| **Gothic Remake** | UE5+Alkimia | 11 + IoStore v6 | LCACHE | 6 TTF | Multiple | ★★★★☆ |

---

## 13. Conclusion

ม็อดภาษาไทยของ **Cronos: The New Dawn** (variant "ตัวอักษรมีหัว") โดดเด่นด้วย:

1. **5 ตระกูลฟอนต์ไทย** — 109PANIChalam (serif/looped), Chakra Petch (tech), MiSans Thai (system), Playpen Sans Thai (handwriting), Noto Sans Thai (standard) — รวม 11 ไฟล์ TTF
2. **Dual LocRes** — แยก Game (UI) กับ Dialog (สนทนา) ออกจากกัน — อัปเดตง่าย
3. **PAK v4 Single File** — ทุกอย่างอยู่ในไฟล์เดียว 2.17 MB (Zlib compressed)
4. **"มีหัว" Variant** — ใช้ฟอนต์ 109PANIChalam ที่มีหัวตัวอักษรแบบดั้งเดิม
5. **Accessibility Fonts** — เกมใช้ Atkinson Hyperlegible + JetBrains Mono (accessibility + monospace)
6. **Non-Destructive** — ลบ PAK ไฟล์เดียว = เกมกลับเป็นปกติ

---

## 14. Extracted Assets

ไฟล์ที่ดึงออกมาจากม็อดนี้ทั้งหมด:

- **Fonts (11 ไฟล์จริง TTF):** [Assets/Fonts/](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unreal_Engine_5/Games/Cronos_The_New_Dawn/Assets/Fonts)
  - `109PANIChalam.ttf` (53.4 KB) ★ ไทยมีหัว Regular
  - `109PANIChalamBold.ttf` (53.1 KB) ★ ไทยมีหัว Bold
  - `Chakra_Petch_Bold.ttf` (64 KB) — Tech display
  - `Chakra_Petch_Medium.ttf` (64 KB)
  - `Chakra_Petch_SemiBold.ttf` (64 KB)
  - `MiSans_Thai.ttf` (45.6 KB) — Xiaomi Sans Thai
  - `MiSans_Thai_Bold.ttf` (45 KB)
  - `MiSans_Thai_Semibold.ttf` (45 KB)
  - `Noto_Sans_Thai_Regular.ttf` (38.2 KB) — Google Noto
  - `Playpen_Sans_Thai_Bold.ttf` (64 KB) — Handwriting
  - `Playpen_Sans_Thai_Regular.ttf` (64 KB)

- **Texts:** [Assets/Texts/](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unreal_Engine_5/Games/Cronos_The_New_Dawn/Assets/Texts)
  - *Game.locres + Dialog.locres อยู่ใน PAK (compressed) — ต้องใช้ UnrealPak*

- **Configs / Metadata:** [Assets/Configs/](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unreal_Engine_5/Games/Cronos_The_New_Dawn/Assets/Configs)
  - [PAK_Content_Listing.txt](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unreal_Engine_5/Games/Cronos_The_New_Dawn/Assets/Configs/PAK_Content_Listing.txt) — รายชื่อ 39 entries
  - [mod_preview.jpg](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unreal_Engine_5/Games/Cronos_The_New_Dawn/Assets/Configs/mod_preview.jpg) — รูปตัวอย่าง
