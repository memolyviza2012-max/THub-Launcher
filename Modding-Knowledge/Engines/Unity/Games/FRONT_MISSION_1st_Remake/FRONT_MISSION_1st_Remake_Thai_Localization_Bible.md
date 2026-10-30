# Front Mission 1st Remake — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer) — Upgraded

---

## 1. Overview
เอกสารนี้วิเคราะห์กลไกม็อดภาษาไทยของ **Front Mission 1st: Remake** อย่างละเอียดที่สุด เกมนี้สร้างด้วย **Unity (Mono runtime)** และใช้ **TextMeshPro (TMP)** สำหรับ text rendering ม็อดนี้ใช้วิธี **Runtime Code Injection** ผ่าน **BepInEx** framework — ไม่แก้ไขไฟล์เกมต้นฉบับเลย แต่ใช้ DLL plugin ที่ intercept ฟังก์ชัน text ของเกมแล้วแทนที่ข้อความอังกฤษด้วยข้อความไทย ณ runtime

---

## 2. Technical Stack

| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Unity (Mono runtime, IL2CPP not used) |
| **Text System** | TextMeshPro (TMP_FontAsset) |
| **Modding Framework** | **BepInEx 6.x** (Unity Doorstop injection) |
| **Injection Method** | Runtime Harmony Patching (MonoMod) |
| **Translation Format** | JSON (key-value, `original` + `translation`) |
| **Subtitle Format** | SRT (SubRip Text) |
| **Font** | NotoSansThai-Regular.ttf (TMP Fallback Font) |
| **Encryption** | ❌ ไม่มี — ข้อความเป็น plaintext JSON |
| **Mod Strategy** | Non-destructive (ไม่แก้ไขไฟล์เกมต้นฉบับ) |
| **Mod Complexity** | ★★★☆☆ (ต้องเขียน C# plugin แต่ระบบชัดเจน) |

---

## 3. โครงสร้างไฟล์ (File Architecture)

### 3.1 ภาพรวม
```
(Game Root)/
├── .doorstop_version                    ← 5 bytes (เวอร์ชัน Doorstop)
├── doorstop_config.ini                  ← 1.4 KB (BepInEx loader config)
├── winhttp.dll                          ← 25.5 KB (Unity Doorstop proxy DLL)
└── BepInEx/
    ├── core/                            ← BepInEx runtime (17 files)
    │   ├── BepInEx.Core.dll             ← 131 KB (BepInEx core)
    │   ├── BepInEx.Unity.Mono.dll       ← 49.5 KB (Unity Mono bridge)
    │   ├── 0Harmony.dll                 ← 257 KB (Harmony patching)
    │   ├── Mono.Cecil.dll               ← 331 KB (IL manipulation)
    │   ├── MonoMod.RuntimeDetour.dll    ← 105 KB (Runtime method detours)
    │   └── MonoMod.Utils.dll            ← 184 KB (MonoMod utilities)
    ├── patchers/                        ← (ว่าง)
    └── plugins/
        ├── font_mod/
        │   ├── FontMod.dll              ← 7.5 KB  ★ Plugin สำหรับ inject ฟอนต์ไทย
        │   └── NotoSansThai-Regular.ttf ← 92.9 KB ★ ฟอนต์ภาษาไทย
        ├── srt_mod/
        │   ├── Kage_seq_TH.srt          ← 3.4 KB  ★ ซับ cutscene (Kage route)
        │   ├── LotF_outro_TH.srt        ← 0.2 KB  ★ ซับ ending (LotF)
        │   └── Ocu_Outro_TH.srt         ← 2.3 KB  ★ ซับ ending (OCU)
        └── translations_mod/
            ├── ThaiMod.dll              ← 21.5 KB ★ Plugin สำหรับ inject ข้อความไทย
            ├── thai_translations.json   ← 1.95 MB ★ ข้อความแปลไทยทั้งหมด
            ├── thai_all_keys.json       ← 1.79 MB ★ รายชื่อ key ทั้งหมด
            └── thai_translations_new.json ← 11 B   (ว่าง — placeholder)
```

### 3.2 ขนาดรวม
| หมวด | ขนาด |
|---|---|
| BepInEx Core | ~1.2 MB |
| Font Plugin + TTF | ~100 KB |
| Translation Plugin + JSON | ~3.77 MB |
| SRT Subtitles | ~6 KB |
| **รวมทั้งหมด** | **~5.1 MB** |

---

## 4. BepInEx Framework — หัวใจของระบบ

### 4.1 BepInEx คืออะไร?
**BepInEx** (Bepis Injector Extensible) เป็น modding framework สำหรับเกม Unity ที่ทำให้สามารถ:
- โหลด C# plugin (DLL) เข้าไปในเกม ณ runtime
- ใช้ **Harmony** สำหรับ patch/intercept method ของเกม
- ไม่แก้ไขไฟล์เกมต้นฉบับเลย (non-destructive)

### 4.2 Boot Sequence
```
1. เกมเริ่มต้น → Unity Mono runtime โหลด
2. winhttp.dll (Unity Doorstop) ถูกโหลดก่อน DLL อื่น (proxy DLL)
3. Doorstop อ่าน doorstop_config.ini → โหลด BepInEx.Unity.Mono.Preloader.dll
4. BepInEx Preloader สแกน plugins/ → พบ:
   - FontMod.dll (com.thaimod.frontmission1st.font)
   - ThaiMod.dll (com.thaimod.frontmission1st)
5. Harmony Patching → intercept Unity/Game methods
6. เกมทำงานปกติ แต่ข้อความถูกแทนที่เป็นไทย
```

### 4.3 doorstop_config.ini (Key Settings)
```ini
enabled = true
target_assembly = BepInEx\core\BepInEx.Unity.Mono.Preloader.dll
dll_search_path_override = "BepInEx\core"
```

---

## 5. Plugin Analysis — FontMod.dll

### 5.1 Plugin ID
```
com.thaimod.frontmission1st.font
Name: "Front Mission 1st Thai Font"
```

### 5.2 หน้าที่
FontMod ทำหน้าที่ **inject ฟอนต์ภาษาไทย** เข้าไปในระบบ TextMeshPro ของเกม:

1. **โหลด TTF** — อ่าน `NotoSansThai-Regular.ttf` จากโฟลเดอร์ plugin
2. **สร้าง TMP_FontAsset** — แปลง TTF เป็น TMP Font Asset ด้วย:
   - `TMP_FontAsset.CreateFontAsset()` — สร้าง font asset ใหม่
   - `AtlasPopulationMode` — ตั้งค่า dynamic atlas population
   - `GlyphRenderMode` — กำหนด rendering mode
3. **เพิ่มเป็น Fallback Font** — เพิ่ม Thai font เข้า `fallbackFontAssetTable` ของ font ที่เกมใช้อยู่
4. **Harmony Patch** — hook `OnFontAwake` เพื่อ inject fallback font เมื่อ TMP font ถูกโหลด

### 5.3 เทคนิค Fallback Font
แทนที่จะ **แทนที่** ฟอนต์เดิม, FontMod **เพิ่ม** ฟอนต์ไทยเป็น fallback:
- เมื่อ TMP render text → หา glyph จากฟอนต์หลัก
- ถ้าไม่พบ (เพราะอักษรไทยไม่อยู่ในฟอนต์เดิม) → ค้นหาใน fallback chain
- พบ glyph ไทยใน NotoSansThai → render ปกติ
- **ข้อดี:** ไม่กระทบตัวอักษร Latin/JP ที่มีอยู่เดิม

---

## 6. Plugin Analysis — ThaiMod.dll

### 6.1 Plugin ID
```
com.thaimod.frontmission1st
Name: "Front Mission 1st Thai Mod"
```

### 6.2 หน้าที่
ThaiMod ทำหน้าที่ **แทนที่ข้อความ** จากภาษาอังกฤษเป็นภาษาไทย:

1. **LoadTranslations** — โหลด `thai_translations.json` เมื่อ plugin เริ่มทำงาน
2. **OnUITextLocalize** — Harmony Patch ที่ intercept ฟังก์ชัน localize ของเกม:
   - จับ key ของข้อความ (เช่น `msg_bar_colo20b`)
   - ค้นหา key ใน dictionary → ถ้าพบ → แทนที่ด้วย `translation`
3. **OnUITextAwake** — Patch สำหรับ UI text components
4. **DiscoverKey / DumpAllKeysFromInstance** — ฟังก์ชันสำหรับ **ค้นหา key ใหม่** จากเกม → บันทึกลง `thai_all_keys.json`
5. **SRT_LoadFromFile_Prefix** — Patch สำหรับ redirect cutscene subtitle loading ให้โหลดไฟล์ SRT ภาษาไทยแทน

### 6.3 Workflow
```
เกม call Localize("msg_bar_colo20b")
    ↓
Harmony intercept → ThaiMod.OnUITextLocalize()
    ↓
Lookup: thai_translations["msg_bar_colo20b"]
    ↓
Found? → Return: "โอลสัน:\nตามผมมา แล้วคุณจะได้โอกาสตามหา..."
Not found? → DiscoverKey() → บันทึกลง thai_all_keys.json → Return original English
```

---

## 7. Translation Data — JSON Format

### 7.1 thai_translations.json
| ฟิลด์ | ค่า |
|---|---|
| **ขนาด** | 1.95 MB (1,999,300 bytes) |
| **Format** | JSON object with metadata + entries |
| **ภาษา** | Thai (`"language": "Thai"`) |
| **จำนวน keys** | **7,978** (ตาม metadata `total_keys`) |
| **จำนวน entries จริง** | **6,315** (parsed) |
| **Encoding** | UTF-8 |

### 7.2 โครงสร้าง JSON
```json
{
  "language": "Thai",
  "description": "Thai translations",
  "total_keys": 7978,
  "entries": {
    "msg_com_ofi1": {
      "original": "Olson:\nHere's the mission intel.",
      "translation": "โอลสัน:\nนี่คือข้อมูล Intel"
    },
    "msg_bar_colo20b": {
      "original": "Olson:\nCome with me...",
      "translation": "โอลสัน:\nตามผมมา..."
    }
  }
}
```

### 7.3 Key Categories (149 prefixes)
| Prefix | ตัวอย่าง | เนื้อหา |
|---|---|---|
| `msg_bar_*` | `msg_bar_colo20b` | บทสนทนาในบาร์ |
| `msg_com_*` | `msg_com_ofi1` | บทสนทนาภารกิจ |
| `msg_bel_*` | `msg_bel_bar` | เมือง Belchka |
| `msg_cam_*` | `msg_cam_city` | เมือง Cam |
| `msg_arn_*` | `msg_arn_vic1` | Arena battles |
| `msg_buy_*` | `msg_buy_item` | ระบบซื้อขาย |
| `msg_input_*` | `msg_input_save` | UI ระบบ Save/Load |

### 7.4 Control Tags ในข้อความ
| Tag | ความหมาย |
|---|---|
| `\NM00` | ชื่อตัวละครหลัก (dynamic) |
| `\NM01` | ชื่อตัวละครรอง (dynamic) |
| `\CT01` / `\CT00` | Control timing (delay text) |
| `\WT01` | Wait before next text |
| `\n` | New line |
| `<sprite name="X">` | ปุ่มกดบนจอย (TextMeshPro rich text) |

### 7.5 thai_all_keys.json
| ฟิลด์ | ค่า |
|---|---|
| **ขนาด** | 1.79 MB |
| **Format** | JSON — เก็บคู่ `original` + `translation` แบบ compact |
| **จำนวน entries** | 6,315 |
| **หน้าที่** | **รวบรวม key ทั้งหมดที่เกมใช้** — ThaiMod dump ออกมาโดยอัตโนมัติ |

---

## 8. Subtitle System — SRT Files

### 8.1 ไฟล์ SRT ทั้ง 3 ไฟล์
| ไฟล์ | ขนาด | เนื้อหา |
|---|---|---|
| `Kage_seq_TH.srt` | 3.4 KB | Cutscene route ของ Kage (Maria's backstory) |
| `LotF_outro_TH.srt` | 0.2 KB | Ending cutscene (Legends of the Forgotten) |
| `Ocu_Outro_TH.srt` | 2.3 KB | Ending cutscene (OCU route) |

### 8.2 SRT Format
```srt
2
00:00:16,216 --> 00:00:20,604
[TH] Maria:
I grew up in a fishing town much like this one,
```
- ใช้ `[TH]` prefix เพื่อบอกว่าเป็นภาษาไทย
- ThaiMod intercept การโหลด SRT ผ่าน `SRT_LoadFromFile_Prefix`

> **หมายเหตุ:** ซับ SRT ในม็อดนี้ยังเป็น**ภาษาอังกฤษ** — มี `[TH]` tag แต่เนื้อหาจริงยังไม่ถูกแปลเป็นไทย (อาจอยู่ระหว่างดำเนินการ)

---

## 9. Font System — TMP Fallback Chain

### 9.1 NotoSansThai-Regular.ttf
| ฟิลด์ | ค่า |
|---|---|
| **ฟอนต์** | Noto Sans Thai (Google) |
| **ขนาด** | 92.9 KB |
| **Format** | TrueType (Magic: `00 01 00 00`) |
| **Weight** | Regular |
| **Thai Coverage** | ✅ ครอบคลุมอักษรไทยทั้งหมด |

### 9.2 TMP Fallback Integration
```
TMP_FontAsset (เกมเดิม: e.g., "FM1_MainFont")
    ├── Primary glyphs: Latin, JP, etc.
    └── fallbackFontAssetTable:
        └── [0] NotoSansThai → Thai glyphs (injected by FontMod)
```

---

## 10. Complete Pipeline — ขั้นตอนสร้างม็อด

```
ขั้นตอนที่ 1: ติดตั้ง BepInEx
    - ดาวน์โหลด BepInEx 6.x (Unity Mono)
    - วาง winhttp.dll + doorstop_config.ini + BepInEx/ ไว้ที่ root ของเกม
        ↓
ขั้นตอนที่ 2: สร้าง FontMod Plugin
    - เขียน C# plugin ที่ inherit BaseUnityPlugin
    - โหลด NotoSansThai-Regular.ttf → สร้าง TMP_FontAsset
    - Patch TMP_FontAsset.Awake() → เพิ่ม fallback
    - Compile เป็น FontMod.dll → วางใน plugins/font_mod/
        ↓
ขั้นตอนที่ 3: สร้าง ThaiMod Plugin
    - เขียน C# plugin สำหรับ text replacement
    - Patch ฟังก์ชัน Localize() → lookup thai_translations.json
    - Patch SRT loader → redirect ไป SRT ภาษาไทย
    - Compile เป็น ThaiMod.dll → วางใน plugins/translations_mod/
        ↓
ขั้นตอนที่ 4: เตรียม Translation Data
    - รันเกมครั้งแรกเพื่อ dump key ทั้งหมด → thai_all_keys.json
    - แปลข้อความ → บันทึกใน thai_translations.json
    - แปลซับไตเติ้ล → บันทึกเป็น .srt
        ↓
ขั้นตอนที่ 5: ติดตั้ง
    คัดลอกทุกอย่างไป game root (non-destructive)
        ↓
เสร็จสิ้น!
```

---

## 11. Required Tools

| เครื่องมือ | หน้าที่ | ระดับความจำเป็น |
|---|---|---|
| **BepInEx 6.x** (Unity Mono) | Plugin runtime framework | ✅ จำเป็น |
| **Visual Studio / Rider** | เขียน C# plugin | ✅ จำเป็น |
| **dnSpy** | Decompile game DLL เพื่อหา method names | ✅ จำเป็น |
| **Unity Doorstop** | DLL proxy สำหรับ boot injection | ✅ จำเป็น (มาพร้อม BepInEx) |
| **Harmony** | Runtime method patching | ✅ จำเป็น (มาพร้อม BepInEx) |

---

## 12. สถิติม็อด

| ข้อมูล | จำนวน |
|---|---|
| **ไฟล์ม็อดทั้งหมด** | 38 ไฟล์ (17 BepInEx core + 8 mod files) |
| **ขนาดรวม** | ~5.1 MB |
| **Translation entries** | 6,315 entries (จาก 7,978 keys) |
| **Key prefixes** | 149 categories |
| **SRT subtitles** | 3 ไฟล์ (cutscenes) |
| **C# Plugins** | 2 (FontMod.dll + ThaiMod.dll) |
| **ฟอนต์** | 1 (NotoSansThai-Regular.ttf, 93 KB) |

---

## 13. ความพิเศษของม็อดนี้

### 13.1 Non-Destructive Modding
ม็อดนี้ **ไม่แก้ไขไฟล์เกมต้นฉบับแม้แต่ไฟล์เดียว** — ทุกอย่างทำงานผ่าน runtime code injection ลบ BepInEx ออก = เกมกลับเป็นปกติทันที

### 13.2 Key Discovery System
ThaiMod มีระบบ **ค้นหา key อัตโนมัติ** (`DiscoverKey` / `DumpAllKeysFromInstance`) — เมื่อเกมแสดงข้อความที่ยังไม่มีในไฟล์แปล → dump key นั้นลง `thai_all_keys.json` เพื่อให้นักแปลเห็นข้อความที่ยังไม่ได้แปล

### 13.3 TMP Fallback Font Injection
แทนที่จะแทนที่ฟอนต์ทั้งหมด, ใช้เทคนิค **fallback font chain** ที่ inject ฟอนต์ไทยเข้าไปเป็น fallback → glyph Latin/JP ยังใช้ฟอนต์เดิม ฟอนต์ไทยจะถูกใช้เฉพาะอักษรที่ฟอนต์เดิมไม่มี

### 13.4 Development Path Exposed
พบ path ในไฟล์ DLL:
```
E:\SteamLibrary\steamapps\common\FRONT MISSION 1st Remake\ThaiMod\
```
→ ม็อดถูกพัฒนาบน Windows, compile ด้วย .NET Framework 4.6 (Release configuration)

---

## 14. เปรียบเทียบ

| เกม | Engine | Modding | Translation Format | Font | Complexity |
|---|---|---|---|---|---|
| **Front Mission 1st** | Unity (Mono) | BepInEx (runtime) | JSON (plaintext) | TMP Fallback | ★★★☆☆ |
| **Two Point Campus** | Unity | File replace | I2LS Bundle | I2LS Built-in | ★★☆☆☆ |
| **33 Immortals** | Unity | File replace | Plaintext TXT | Built-in | ★★☆☆☆ |
| **FF7 Rebirth** | UE5 | PAK/IoStore | TxtRes (binary) | Bitmap Atlas | ★★★★★ |

---

## 15. Conclusion

ม็อดภาษาไทยของ **Front Mission 1st: Remake** เป็นตัวอย่างที่สมบูรณ์แบบของ **"Runtime Code Injection Localization"**:

1. **BepInEx + Harmony** — ระบบ modding ที่ inject code ณ runtime โดยไม่แก้ไขไฟล์เกม
2. **Dual Plugin Architecture** — FontMod (inject ฟอนต์) + ThaiMod (inject ข้อความ) ทำงานแยกกัน
3. **JSON Translation Format** — ข้อความ 6,315 entries เป็น plaintext JSON ที่อ่าน/แก้ไขง่าย
4. **TMP Fallback Font** — inject ฟอนต์ไทยเป็น fallback chain ไม่กระทบ glyph อื่น
5. **Key Auto-Discovery** — ระบบอัตโนมัติที่ค้นหาและบันทึก key ใหม่จากเกม
6. **SRT Subtitle Override** — intercept การโหลด subtitle เพื่อแสดงซับไตเติ้ลภาษาไทย
7. **Completely Reversible** — ลบ BepInEx ออก = เกมกลับเป็นปกติ 100%

---

## 16. Extracted Assets

รายการไฟล์และทรัพยากรที่ถูกดึงออกมาจากม็อดนี้:

- **Fonts:** [Assets/Fonts/](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unity/Games/FRONT_MISSION_1st_Remake/Assets/Fonts)
  - `NotoSansThai-Regular.ttf` (92.9 KB) — ฟอนต์ Noto Sans Thai สำหรับ TMP fallback injection

- **Texts / Translations:** [Assets/Texts/](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unity/Games/FRONT_MISSION_1st_Remake/Assets/Texts)
  - `thai_translations.json` (1.95 MB) — ข้อความแปล 6,315 entries (คู่ original-translation)
  - `thai_all_keys.json` (1.79 MB) — รายชื่อ key ทั้งหมดที่เกมใช้

- **Subtitles:** [Assets/Subtitles/](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unity/Games/FRONT_MISSION_1st_Remake/Assets/Subtitles)
  - `Kage_seq_TH.srt`, `LotF_outro_TH.srt`, `Ocu_Outro_TH.srt` — 3 ไฟล์ซับไตเติ้ล cutscene

- **Configs:** [Assets/Configs/](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unity/Games/FRONT_MISSION_1st_Remake/Assets/Configs)
  - `doorstop_config.ini` — BepInEx loader configuration
