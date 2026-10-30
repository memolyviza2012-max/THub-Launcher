# 📖 คัมภีร์ฉบับสมบูรณ์: การทำม็อดภาษาไทย Dead Island 2
# The Definitive Modding Bible — Dead Island 2 Thai Localization

> **สถานะ:** ฉบับสมบูรณ์ (Final Edition)  
> **เอนจิ้น:** Unreal Engine 4.27 — ระบบ IoStore  
> **แพลตฟอร์ม:** Steam / Epic Games (WindowsNoEditor)  
> **จัดทำโดย:** แอดนดหนวด (Ad-Nod-Nuad) × Antigravity AI  
> **ปรับปรุงล่าสุด:** กรกฎาคม 2026  

---

## สารบัญ

1. [ทำไม Dead Island 2 ถึงม็อดภาษาไทยยากกว่าเกมอื่น?](#1-ทำไม-dead-island-2-ถึงม็อดภาษาไทยยากกว่าเกมอื่น)
2. [เครื่องมือที่ต้องเตรียม (Prerequisites)](#2-เครื่องมือที่ต้องเตรียม-prerequisites)
3. [ภาพรวมของ Pipeline ทั้งหมด](#3-ภาพรวมของ-pipeline-ทั้งหมด)
4. [ขั้นตอนที่ 1: แตกไฟล์ออกจากเกม (Extraction)](#4-ขั้นตอนที่-1-แตกไฟล์ออกจากเกม-extraction)
5. [ขั้นตอนที่ 2: การแปลข้อความ UI (Locres Translation)](#5-ขั้นตอนที่-2-การแปลข้อความ-ui-locres-translation)
6. [ขั้นตอนที่ 3: การแปลซับไตเติลบทสนทนา (Subtitle Translation)](#6-ขั้นตอนที่-3-การแปลซับไตเติลบทสนทนา-subtitle-translation)
7. [ขั้นตอนที่ 4: การสร้างฟอนต์ภาษาไทย (Thai Font Creation)](#7-ขั้นตอนที่-4-การสร้างฟอนต์ภาษาไทย-thai-font-creation)
8. [ขั้นตอนที่ 5: การแพ็คไฟล์เป็นก้อน .pak (UnrealPak)](#8-ขั้นตอนที่-5-การแพ็คไฟล์เป็นก้อน-pak-unrealpak)
9. [ขั้นตอนที่ 6: ปลดล็อคระบบลายเซ็น (Signature Bypass)](#9-ขั้นตอนที่-6-ปลดล็อคระบบลายเซ็น-signature-bypass)
10. [⭐ ขั้นตอนที่ 7: ผ่าตัดฝังฟอนต์ลง IoStore (UCAS Font Injection)](#10-ขั้นตอนที่-7-ผ่าตัดฝังฟอนต์ลง-iostore-ucas-font-injection)
11. [ขั้นตอนที่ 8: ระบบ Build อัตโนมัติ (Automated Pipeline)](#11-ขั้นตอนที่-8-ระบบ-build-อัตโนมัติ-automated-pipeline)
12. [ขั้นตอนที่ 9: สร้าง Smart Installer (.exe)](#12-ขั้นตอนที่-9-สร้าง-smart-installer-exe)
13. [บทเรียนจากความล้มเหลว (Failed Approaches)](#13-บทเรียนจากความล้มเหลว-failed-approaches)
14. [ข้อจำกัดของ Xbox Game Pass (WinGDK)](#14-ข้อจำกัดของ-xbox-game-pass-wingdk)
15. [สรุปผลงาน](#15-สรุปผลงาน)
16. [ภาคผนวก: ตารางค่าคงที่ทางเทคนิค](#16-ภาคผนวก-ตารางค่าคงที่ทางเทคนิค)

---

## 1. ทำไม Dead Island 2 ถึงม็อดภาษาไทยยากกว่าเกมอื่น?

เกม Unreal Engine 4 สมัยก่อน (เช่น XCOM, Dishonored) ใช้ระบบ `.pak` ธรรมดา เราสามารถเอาไฟล์ฟอนต์ภาษาไทยไปวางในโฟลเดอร์ `~mods` แล้วเกมจะโหลดทับไฟล์เดิมได้เลย

แต่ **Dead Island 2** ใช้ระบบแพ็คไฟล์สมัยใหม่ที่เรียกว่า **IoStore** ซึ่งประกอบด้วย:

| ไฟล์ | หน้าที่ | ขนาด |
|------|---------|------|
| `.utoc` (Table of Contents) | สารบัญ — เก็บ Chunk ID, Offset, Length ของทุกไฟล์ | ~5 MB |
| `.ucas` (Container) | ก้อนข้อมูลยักษ์ — เก็บข้อมูลจริงทั้งหมด เข้ารหัส AES-256-ECB | **~3 GB** |

### ปัญหาหลัก 3 ข้อที่ทำให้ม็อดปกติใช้ไม่ได้:

1. **IoStore มี Priority สูงกว่า ~mods:** เอนจิ้นจะดึงฟอนต์จากก้อน `.ucas` ก่อนเสมอ ถึงเราจะเอาฟอนต์ไทยไปวางใน `~mods` เกมก็จะ "เมินมัน" → ตัวอักษรไทยกลายเป็น □□□ (Tofu)
2. **ข้อมูลถูกเข้ารหัส AES:** ก้อน `.ucas` ไม่ใช่ไฟล์ธรรมดา แต่ละบล็อคถูกเข้ารหัส AES-256-ECB ดังนั้นการเขียนทับข้อมูลดิบๆ ลงไปจะทำให้เกมพัง
3. **ระบบ Signature Check:** ไฟล์ `.pak` ของม็อดจะถูกเกมปฏิเสธหากไม่มีลายเซ็นดิจิทัล `.sig` คู่กัน

**สรุป:** เราต้องใช้เทคนิค 3 ชั้นเพื่อทำลายกำแพงทั้ง 3 → **ฝังฟอนต์ + เข้ารหัส AES + ปลอมลายเซ็น**

---

## 2. เครื่องมือที่ต้องเตรียม (Prerequisites)

| เครื่องมือ | จุดประสงค์ | หมายเหตุ |
|-----------|-----------|----------|
| **Python 3.10+** | รันสคริปต์ทั้งหมด | ติดตั้ง pip ด้วย |
| **pycryptodome** | เข้ารหัส/ถอดรหัส AES-256-ECB | `pip install pycryptodome` |
| **UnrealPak.exe** (v4.27) | แพ็คไฟล์เป็น `.pak` | จากโฟลเดอร์ Engine ของ UE4 |
| **pylocres** | แปลง `.locres` ↔ `.csv` | `pip install pylocres` |
| **CUE4Parse CLI หรือ FModel** | แตกไฟล์จาก IoStore | GitHub: FabianFG/CUE4Parse |
| **Unreal Engine 4.27 Editor** | สร้าง Font Asset (`.uasset`) | สำหรับ Scaleform GFX font |
| **AES Key ของ Dead Island 2** | ถอดรหัสข้อมูลในไฟล์เกม | ดูภาคผนวก |

---

## 3. ภาพรวมของ Pipeline ทั้งหมด

```
[เกมต้นฉบับ]
    │
    ▼
[1. Extract] ─── CUE4Parse ──→ Game.locres + DialogueList*.xml + fonts_en.uasset
    │
    ├──→ [2. แปล UI] ─── pylocres → CSV → DeepSeek AI → CSV → pylocres ──→ Game.locres (ไทย)
    │
    ├──→ [3. แปล Subtitles] ─── Python XML → CSV → DeepSeek AI → CSV → Python XML ──→ DialogueList*.xml (ไทย)
    │
    ├──→ [4. สร้างฟอนต์] ─── UE4 Editor → SWF → repack_gfx.py ──→ fonts_en.uasset (ไทย)
    │
    ▼
[5. Pack] ─── UnrealPak ──→ DeadIsland2_TH_P.pak
    │
    ├──→ [6. Signature Bypass] ─── ก๊อป .sig ของเกม → Rename ──→ .sig ปลอม
    │
    ├──→ [7. UCAS Injection] ─── Python → Append + AES Encrypt ──→ แก้ไฟล์ .ucas/.utoc ของเกม
    │
    ▼
[8. Build Auto] ─── build_all_auto.py ──→ ครบทุกขั้นตอนด้วยคำสั่งเดียว
    │
    ▼
[9. Smart Installer] ─── PyInstaller ──→ DeadIsland2_Thai_Installer.exe (แจกผู้เล่น)
```

---

## 4. ขั้นตอนที่ 1: แตกไฟล์ออกจากเกม (Extraction)

### 4.1 ไฟล์ที่ต้องแตกออกมา

| ไฟล์ | ตำแหน่งในเกม | หน้าที่ |
|------|-------------|---------|
| `Game.locres` | `Content/Localization/Game/en/` | ข้อความ UI ทั้งหมด (เมนู, ไอเทม, ภารกิจ) |
| `DialogueList.xml` | `Content/StagedData/DamLoc/Data/` | ซับไตเติลบทสนทนาเกมหลัก |
| `DialogueList_EXP1.xml` | เดียวกัน | ซับไตเติล DLC Haus |
| `DialogueList_EXP2.xml` | เดียวกัน | ซับไตเติล DLC SoLA |
| `DialogueList_Horde.xml` | เดียวกัน | ซับไตเติลโหมด Horde |
| `fonts_en.uasset` | `Content/DI2/UI/Fonts/` | ไฟล์ฟอนต์หลักของเกม (Scaleform GFX) |

### 4.2 วิธีแตก (ใช้ CUE4Parse CLI)

สร้างไฟล์ `0_extract.bat`:
```batch
@echo off
DI2_Extractor.exe ^
    --aes-key=014AEC0148FBDEE9640633AAB67521AAB4E1083A98F76FF33DDCF78DAD05BE66 ^
    --game-dir="C:\Program Files (x86)\Steam\steamapps\common\Dead Island 2\DeadIsland\Content\Paks" ^
    --export-types=locres,xml,uasset ^
    --output-dir=".\Extracted"
```

> **ทางเลือก:** ใช้ **FModel** เป็น GUI Browser สำหรับดูโครงสร้างไฟล์ภายในได้สะดวกกว่า

---

## 5. ขั้นตอนที่ 2: การแปลข้อความ UI (Locres Translation)

### 5.1 แปลง Locres → CSV

```batch
pylocres to-csv -p "Game.locres" -o "Translation\Game_th.csv"
```

ได้ไฟล์ CSV ขนาด ~14 MB ที่มี 61,000+ บรรทัด (Encoding: UTF-16-LE, คั่นด้วย Tab)

**โครงสร้าง CSV:**
| คอลัมน์ | เนื้อหา |
|---------|---------|
| 0 - Namespace | ชื่อกลุ่ม เช่น `DA_UIKeyNamesData` |
| 1 - Key Part 1 | - |
| 2 - Key Part 2 | - |
| 3 - Source | ข้อความภาษาอังกฤษต้นฉบับ |
| 4 - Translation | **ใส่ข้อความภาษาไทยที่นี่** |

### 5.2 เทคนิคการแปลด้วย AI (Tag Masking System)

เราใช้ DeepSeek API ในการแปล แต่ AI มักจะทำให้โค้ดพิเศษในข้อความเกม (เช่น โค้ดสี, ตัวแปร) เสียหาย ดังนั้นเราใช้ระบบ **Tag Masking** เพื่อซ่อนโค้ดก่อนส่งให้ AI:

```python
import re

# Regex จับทุก Tag พิเศษในข้อความเกม
TAG_PATTERN = re.compile(r'(<[^>]+>|\\n|\\r|\n|\r|%[sdiefg]|\{\d+\}|\[\[[^\]]+\]\])')

def mask_tags(text):
    """ซ่อนโค้ดพิเศษก่อนส่งให้ AI แปล"""
    tags = []
    def replacer(match):
        tag = match.group(0)
        placeholder = f"[TAG_{len(tags)}]"
        tags.append(tag)
        return placeholder
    masked = TAG_PATTERN.sub(replacer, text)
    return masked, tags

def unmask_tags(translated_text, tags):
    """นำโค้ดพิเศษกลับมาใส่หลังแปลเสร็จ"""
    result = translated_text
    for i, tag in enumerate(tags):
        result = result.replace(f"[TAG_{i}]", tag)
    return result

# ตัวอย่างการใช้งาน:
original = "<color=red>Warning!</color> Press %s to continue"
masked, tags = mask_tags(original)
# masked = "[TAG_0]Warning![TAG_1] Press [TAG_2] to continue"
# tags = ["<color=red>", "</color>", "%s"]

# ส่ง masked ไปให้ AI แปล → ได้กลับมา: "[TAG_0]คำเตือน![TAG_1] กด [TAG_2] เพื่อดำเนินการต่อ"
translated = unmask_tags(ai_result, tags)
# ผลลัพธ์: "<color=red>คำเตือน!</color> กด %s เพื่อดำเนินการต่อ"
```

### 5.3 การป้องกันชื่อปุ่มกด (Keyboard Key Protection)

ข้อความที่อยู่ใน Namespace `DA_UIKeyNamesData` (เช่น Esc, Enter, Shift, Spacebar) **ต้องไม่ถูกแปล** เพราะเกมใช้ข้อความเหล่านี้ตรงๆ ในการแสดงปุ่มกดบนหน้าจอ

```python
SKIP_NAMESPACES = {"DA_UIKeyNamesData"}
PROTECTED_KEYS = {"Enter", "Esc", "Shift", "Tab", "Spacebar", "Backspace", "Delete"}

def should_skip(namespace, source_text):
    if namespace in SKIP_NAMESPACES:
        return True
    if source_text.strip() in PROTECTED_KEYS:
        return True
    return False
```

### 5.4 ระบบตรวจจับ AI หลอน (Canary Words)

AI แปลภาษาบางครั้งจะ "หลอน" — สร้างข้อความที่ไม่เกี่ยวข้องกับต้นฉบับ เราใช้ระบบ **Canary Words** ตรวจจับ:

```python
CANARY_WORDS = ["กีวางไร่อะ", "หลอนยา", "มั่วซั่ว"]

def is_hallucination(translated_text):
    for canary in CANARY_WORDS:
        if canary in translated_text:
            return True
    return False
```

### 5.5 ระบบ Checkpoint (Atomic Save)

เพื่อป้องกันข้อมูลหายเวลาไฟดับหรือ API ล่มกลางคัน:

```python
import os

def atomic_save(filepath, data):
    """เขียนไฟล์แบบ Atomic — ป้องกันไฟล์พังกลางคัน"""
    tmp_path = filepath + ".tmp"
    with open(tmp_path, "w", encoding="utf-16-le") as f:
        f.write(data)
    os.replace(tmp_path, filepath)  # Atomic operation ของ OS
```

### 5.6 แปลง CSV กลับเป็น Locres

```batch
pylocres from-csv -p "Translation\Game_th.csv" -o "Pack\DeadIsland\Content\Localization\Game\en\Game.locres" -v 2
```

> **สำคัญ:** ใช้ `-v 2` สำหรับ Locres version 2 ซึ่งเป็นเวอร์ชันที่ Dead Island 2 ใช้

---

## 6. ขั้นตอนที่ 3: การแปลซับไตเติลบทสนทนา (Subtitle Translation)

### 6.1 โครงสร้าง XML ของระบบซับไตเติล

Dead Island 2 เก็บซับไตเติลในไฟล์ XML ขนาดยักษ์ (เกมหลัก 12.2 MB, DLC อีก 2.6 MB รวมกัน) โดยมีโครงสร้างดังนี้:

```xml
<DialogueLineVariation Path="/Game/DI2/Dialogue/MainQuest/MQ01/...">
    <Chunk Text="Hey, you look like you could use some help!" Index="0"/>
    <Chunk Text="Welcome to Hell-A, slayer!" Index="1"/>
</DialogueLineVariation>

<DialogueLine Path="/Game/DI2/Dialogue/..." ActorLine="Watch out behind you!"/>
```

### 6.2 การแตกซับไตเติลออกมาเป็น CSV

สคริปต์ `extract_dialogue_subtitles.py` จะอ่านไฟล์ XML ทั้ง 4 ไฟล์:

```python
XML_SOURCES = [
    "DialogueList.xml",       # เกมหลัก (~12.2 MB)
    "DialogueList_EXP1.xml",  # DLC Haus (~914 KB)
    "DialogueList_EXP2.xml",  # DLC SoLA (~1.25 MB)
    "DialogueList_Horde.xml"  # โหมด Horde (~474 KB)
]
```

**วิธีการสร้าง Key:**
- สำหรับ `<Chunk>`: Key = `{Path}#chunk_{Index}`
- สำหรับ `<DialogueLine>`: Key = `{Path}`

**CSV Output (UTF-16, 6 คอลัมน์):**
| Source | XmlPath | Key | English | Type | Thai |
|--------|---------|-----|---------|------|------|
| DialogueList.xml | /Game/DI2/... | path#chunk_0 | Hey, you! | Chunk | เฮ้ คุณ! |

### 6.3 การยัดซับไตเติลกลับเข้า XML

สคริปต์ `inject_translated_subtitles.py` จะนำข้อความไทยจาก CSV กลับไปเขียนทับใน XML:

```python
import xml.etree.ElementTree as ET

def inject_subtitles(xml_path, translations, output_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    for elem in root.iter():
        path = elem.get("Path", "")
        
        # แบบ Chunk (ซับไตเติลแบบแบ่งท่อน)
        for chunk in elem.findall("Chunk"):
            idx = chunk.get("Index", "0")
            key = f"{path}#chunk_{idx}"
            if key in translations:
                chunk.set("Text", translations[key])
        
        # แบบ ActorLine (ซับไตเติลบรรทัดเดียว)
        if elem.get("ActorLine") and path in translations:
            elem.set("ActorLine", translations[path])
    
    tree.write(output_path, encoding="utf-8", xml_declaration=True)
```

---

## 7. ขั้นตอนที่ 4: การสร้างฟอนต์ภาษาไทย (Thai Font Creation)

### 7.1 ปัญหาของฟอนต์ใน Dead Island 2

Dead Island 2 ใช้ฟอนต์ **2 ระบบ** พร้อมกัน:

| ระบบ | ไฟล์ | หน้าที่ |
|------|------|---------|
| **Scaleform GFX** | `fonts_en.uasset` (380 KB) | ฟอนต์หลักสำหรับ UI ของเกม (เมนู, HUD) — เป็นไฟล์ Flash SWF ที่ห่อด้วย UE4 Asset |
| **Engine Fonts** | `Roboto*.ttf`, `Roboto*.ufont` (14 ไฟล์) | ฟอนต์สำรองของเอนจิ้น — ใช้ในบางส่วนของ UI |

### 7.2 การเตรียมฟอนต์ TTF/UFont

เราต้องแทนที่ฟอนต์ Roboto ของเอนจิ้น **ทั้งหมด 14 ไฟล์** ด้วยฟอนต์ภาษาไทยตัวเดียวกัน:

```
Engine/Content/EngineFonts/Faces/
├── RobotoBold.ufont          → แทนที่ด้วยฟอนต์ไทย (108,364 bytes)
├── RobotoBoldItalic.ufont    → แทนที่ด้วยฟอนต์ไทย (108,364 bytes)
├── RobotoItalic.ufont        → แทนที่ด้วยฟอนต์ไทย (108,364 bytes)
├── RobotoLight.ufont         → แทนที่ด้วยฟอนต์ไทย (108,364 bytes)
└── RobotoRegular.ufont       → แทนที่ด้วยฟอนต์ไทย (108,364 bytes)

Engine/Content/Slate/Fonts/
├── Roboto-Black.ttf          → แทนที่ด้วยฟอนต์ไทย (108,364 bytes)
├── Roboto-BlackItalic.ttf    → แทนที่ด้วยฟอนต์ไทย (108,364 bytes)
├── Roboto-Bold.ttf           → แทนที่ด้วยฟอนต์ไทย (108,364 bytes)
├── Roboto-BoldCondensed.ttf  → แทนที่ด้วยฟอนต์ไทย (108,364 bytes)
├── Roboto-BoldCondensedItalic.ttf → แทนที่ (108,364 bytes)
├── Roboto-BoldItalic.ttf     → แทนที่ด้วยฟอนต์ไทย (108,364 bytes)
├── Roboto-Italic.ttf         → แทนที่ด้วยฟอนต์ไทย (108,364 bytes)
├── Roboto-Light.ttf          → แทนที่ด้วยฟอนต์ไทย (108,364 bytes)
└── Roboto-Regular.ttf        → แทนที่ด้วยฟอนต์ไทย (108,364 bytes)
```

> **หมายเหตุ:** ไฟล์ทั้ง 14 ไฟล์มีขนาดเท่ากันหมด (108,364 bytes) เพราะเราใช้ฟอนต์ไทย TTF ตัวเดียวกันแทนที่ทั้งหมด เพื่อให้มั่นใจว่าภาษาไทยจะแสดงผลได้ในทุกจุดของ UI

### 7.3 การสร้าง Scaleform GFX Font (fonts_en.uasset)

นี่คือส่วนที่ซับซ้อนที่สุด — ไฟล์ `fonts_en.uasset` ไม่ใช่ฟอนต์ TTF ธรรมดา แต่เป็น **UE4 Asset ที่ห่อไฟล์ Flash GFX ไว้ข้างใน**

**ขั้นตอน:**
1. เปิดโปรเจค UE4.27 Editor
2. Import ฟอนต์ภาษาไทย เป็น Scaleform GFX Font Asset
3. Export เป็นไฟล์ `.uasset`

### 7.4 การ Repack GFX กลับเข้า UAsset (repack_gfx.py)

หากคุณแก้ไขไฟล์ SWF/GFX โดยตรง (เช่น ใส่ Glyph ภาษาไทยเพิ่ม) ต้องใช้สคริปต์ `repack_gfx.py` ในการยัดกลับเข้า `.uasset`:

```python
def repack_gfx(original_uasset_path, modified_swf_path, output_path):
    """ยัดไฟล์ SWF/GFX ที่แก้ไขแล้วกลับเข้า UAsset"""
    with open(original_uasset_path, "rb") as f:
        original_data = f.read()
    
    with open(modified_swf_path, "rb") as f:
        swf_data = f.read()
    
    # แปลง FWS→GFX, CWS→CFX (ลายเซ็น Scaleform)
    if swf_data[:3] == b"FWS":
        swf_data = b"GFX" + swf_data[3:]
    elif swf_data[:3] == b"CWS":
        swf_data = b"CFX" + swf_data[3:]
    
    # หาตำแหน่งของ GFX/CFX ใน UAsset ต้นฉบับ
    gfx_offset = -1
    for sig in [b"GFX", b"CFX"]:
        pos = original_data.find(sig)
        if pos != -1:
            gfx_offset = pos
            break
    
    if gfx_offset == -1:
        raise ValueError("ไม่พบ GFX signature ในไฟล์ UAsset!")
    
    # อัปเดต Size Fields ใน UAsset Header
    new_gfx_size = len(swf_data)
    header = bytearray(original_data[:gfx_offset])
    
    # ฟิลด์ขนาดอยู่ที่ตำแหน่ง (gfx_offset - 4) และ (gfx_offset - 21)
    import struct
    struct.pack_into('<I', header, gfx_offset - 4, new_gfx_size)
    struct.pack_into('<I', header, gfx_offset - 21, new_gfx_size + 4)
    
    # อัปเดต GFX internal size field (offset 4 ใน GFX)
    swf_data = bytearray(swf_data)
    struct.pack_into('<I', swf_data, 4, new_gfx_size)
    
    # ต่อท้ายด้วย Trailing Bytes (12 bytes)
    trailing = bytes([0x0f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    
    # ประกอบร่างไฟล์ใหม่
    with open(output_path, "wb") as f:
        f.write(bytes(header))
        f.write(bytes(swf_data))
        f.write(trailing)
    
    print(f"✅ Repack GFX สำเร็จ! ขนาดไฟล์ใหม่: {len(header) + len(swf_data) + len(trailing)} bytes")
```

---

## 8. ขั้นตอนที่ 5: การแพ็คไฟล์เป็นก้อน .pak (UnrealPak)

### 8.1 โครงสร้างโฟลเดอร์ Pack

ก่อนแพ็ค ต้องจัดเรียงไฟล์ทั้งหมดให้ตรงกับโครงสร้างของเกมต้นฉบับ:

```
Pack/
├── DeadIsland/
│   └── Content/
│       ├── DI2/
│       │   └── UI/
│       │       └── Fonts/
│       │           ├── fonts_en.uasset          ← ฟอนต์ Scaleform GFX (ไทย)
│       │           └── Font_NeusaNextCompact...  ← ฟอนต์ TTF (ไทย)
│       ├── Localization/
│       │   └── Game/
│       │       └── en/
│       │           └── Game.locres              ← ข้อความ UI (ไทย)
│       └── StagedData/
│           └── DamLoc/
│               └── Data/
│                   ├── DialogueList.xml          ← ซับไตเติลเกมหลัก (ไทย)
│                   ├── DialogueList_EXP1.xml     ← ซับไตเติล DLC Haus (ไทย)
│                   ├── DialogueList_EXP2.xml     ← ซับไตเติล DLC SoLA (ไทย)
│                   └── DialogueList_Horde.xml    ← ซับไตเติลโหมด Horde (ไทย)
└── Engine/
    └── Content/
        ├── EngineFonts/
        │   └── Faces/
        │       ├── RobotoBold.ufont              ← ฟอนต์ไทย (แทนที่)
        │       ├── RobotoBoldItalic.ufont        ← ฟอนต์ไทย (แทนที่)
        │       ├── RobotoItalic.ufont            ← ฟอนต์ไทย (แทนที่)
        │       ├── RobotoLight.ufont             ← ฟอนต์ไทย (แทนที่)
        │       └── RobotoRegular.ufont           ← ฟอนต์ไทย (แทนที่)
        └── Slate/
            └── Fonts/
                ├── Roboto-Black.ttf              ← ฟอนต์ไทย (แทนที่)
                ├── Roboto-BlackItalic.ttf         ← ฟอนต์ไทย (แทนที่)
                ├── ... (รวม 9 ไฟล์ .ttf)
                └── Roboto-Regular.ttf            ← ฟอนต์ไทย (แทนที่)
```

### 8.2 สร้าง Response File และรัน UnrealPak

สคริปต์ `pack_mod.py` จะกวาดไฟล์ทั้งหมดในโฟลเดอร์ `Pack/` แล้วสร้างไฟล์ `response.txt`:

```python
import os
import subprocess

PACK_DIR = r".\Pack"
UNREALPAK = r"E:\Mod_Workspace\Tool\UE4\Unreal\UnrealPak-841\Engine\Binaries\Win64\UnrealPak.exe"
OUTPUT_PAK = "DeadIsland2_TH_P.pak"

def generate_response_file():
    """กวาดรายชื่อไฟล์ทั้งหมดและสร้าง response.txt"""
    lines = []
    for root, dirs, files in os.walk(PACK_DIR):
        for f in files:
            full_path = os.path.join(root, f)
            # สร้าง Virtual Path (เส้นทางภายในเกม)
            rel_path = os.path.relpath(full_path, PACK_DIR)
            virtual_path = "../../../" + rel_path.replace("\\", "/")
            lines.append(f'"{os.path.abspath(full_path)}" "{virtual_path}"')
    
    with open("response.txt", "w") as f:
        f.write("\n".join(lines))
    
    return len(lines)

def pack():
    count = generate_response_file()
    print(f"📦 พบไฟล์ {count} ไฟล์ พร้อมแพ็ค...")
    
    cmd = f'"{UNREALPAK}" "{OUTPUT_PAK}" -Create="response.txt" -compress'
    subprocess.run(cmd, shell=True, check=True)
    print(f"✅ แพ็คสำเร็จ! ได้ไฟล์: {OUTPUT_PAK}")

pack()
```

**ตัวอย่าง response.txt ที่สร้างได้:**
```
"E:\...\Pack\DeadIsland\Content\Localization\Game\en\Game.locres" "../../../DeadIsland/Content/Localization/Game/en/Game.locres"
"E:\...\Pack\DeadIsland\Content\StagedData\DamLoc\Data\DialogueList.xml" "../../../DeadIsland/Content/StagedData/DamLoc/Data/DialogueList.xml"
"E:\...\Pack\DeadIsland\Content\DI2\UI\Fonts\fonts_en.uasset" "../../../DeadIsland/Content/DI2/UI/Fonts/fonts_en.uasset"
```

**คำสั่งรัน:**
```cmd
UnrealPak.exe "DeadIsland2_TH_P.pak" -Create="response.txt" -compress -sign
```

> **หมายเหตุ:** Flag `-sign` จะสร้างไฟล์ `.sig` มาคู่กับ `.pak` อัตโนมัติ แต่ลายเซ็นนี้อาจใช้ไม่ได้กับทุกเกม ดังนั้นเราจึงใช้เทคนิค Signature Bypass ในขั้นตอนถัดไปแทน

---

## 9. ขั้นตอนที่ 6: ปลดล็อคระบบลายเซ็น (Signature Bypass)

### 9.1 ทำไมต้อง Bypass?

เอนจิ้น Unreal Engine 4 จะเช็คว่าทุกไฟล์ `.pak` ที่โหลดจากโฟลเดอร์ `~mods` **ต้องมีไฟล์ `.sig` คู่กัน** หากไม่มี เกมจะเพิกเฉยไฟล์ม็อดนั้นโดยสิ้นเชิง

### 9.2 วิธี Bypass (จับมือทำ)

```
ขั้นตอน 1: เปิดโฟลเดอร์เกม
           C:\...\Dead Island 2\DeadIsland\Content\Paks\

ขั้นตอน 2: มองหาไฟล์ลายเซ็นของเกม
           pakchunk_default-WindowsNoEditor_P.sig  ← ไฟล์นี้!

ขั้นตอน 3: ก๊อปปี้ไฟล์ .sig ออกมา

ขั้นตอน 4: เปลี่ยนชื่อให้ตรงกับไฟล์ม็อดของเรา
           pakchunk_default-WindowsNoEditor_Thai_P.sig

ขั้นตอน 5: นำไฟล์ทั้งสองไปวางในโฟลเดอร์ ~mods
           ~mods/
           ├── pakchunk_default-WindowsNoEditor_Thai_P.pak  ← ม็อดของเรา
           └── pakchunk_default-WindowsNoEditor_Thai_P.sig  ← ลายเซ็นปลอม
```

### 9.3 ทำไมวิธีนี้ถึงใช้ได้?

ระบบตรวจสอบของ UE4 ทำงานดังนี้:
1. เจอไฟล์ `.pak` → มองหาไฟล์ `.sig` ชื่อเดียวกัน
2. ถ้าเจอ `.sig` → ถือว่าผ่าน (ไม่ได้ตรวจเนื้อหาภายในแบบเข้มงวด)
3. ถ้าไม่เจอ `.sig` → ปฏิเสธการโหลด

ดังนั้นเราแค่ **มีไฟล์ `.sig` ที่ชื่อตรงกัน** ก็เพียงพอแล้ว เนื้อหาภายในจะเป็นอะไรก็ได้!

> **Naming Convention สำคัญ:** ชื่อไฟล์ `.pak` ต้องลงท้ายด้วย `_P` เสมอ (หมายถึง Patch Chunk) เพื่อให้เอนจิ้นรู้ว่านี่คือแพตช์ที่ต้องโหลดทับไฟล์เดิม

---

## 10. ⭐ ขั้นตอนที่ 7: ผ่าตัดฝังฟอนต์ลง IoStore (UCAS Font Injection)

**นี่คือหัวใจสำคัญของโปรเจคทั้งหมด** — เป็นเทคนิคที่ทำให้ฟอนต์ภาษาไทยแสดงผลได้สำเร็จ

### 10.1 หลักการทำงาน

```
[ก่อน Injection]
┌────────────────────────────────────┐
│  pakchunk0-WindowsNoEditor.ucas   │
│  ┌─────────┬─────────┬─────────┐  │
│  │ Block 0 │ Block 1 │ ... ... │  │  ← ข้อมูลเข้ารหัส AES ทั้งหมด
│  │ (64KB)  │ (64KB)  │         │  │
│  └─────────┴─────────┴─────────┘  │
│  ▲                                │
│  │ Offset ชี้มาที่นี่ (fonts_en)    │
└────────────────────────────────────┘

[หลัง Injection]
┌────────────────────────────────────────────────────┐
│  pakchunk0-WindowsNoEditor.ucas                    │
│  ┌─────────┬─────────┬─────────┬──────────────────┐│
│  │ Block 0 │ Block 1 │ ... ... │ 🆕 FONT THAI    ││  ← ฟอนต์ไทยถูกเข้ารหัส AES
│  │ (64KB)  │ (64KB)  │         │ (Block ใหม่)     ││    แล้วแปะท้ายไฟล์
│  └─────────┴─────────┴─────────┴──────────────────┘│
│                                  ▲                  │
│                    Offset แก้ให้ชี้มาที่นี่แทน!       │
└────────────────────────────────────────────────────┘
```

### 10.2 โครงสร้างไฟล์ UTOC (สารบัญ) แบบละเอียด

```
UTOC Header (144 bytes):
┌─────────────────────────────────────────────────────────────┐
│ Offset 0x00: TocMagic        (16 bytes)  = 2D 3D 3D 2D ×4 │
│ Offset 0x10: Version         (1 byte)    = 3               │
│ Offset 0x14: TocHeaderSize   (uint32)    = 144             │
│ Offset 0x18: TocEntryCount   (uint32)    = จำนวนไฟล์ทั้งหมด│
│ Offset 0x1C: CompBlockCount  (uint32)    = จำนวนบล็อคบีบอัด│
│ Offset 0x20: CompBlockSize   (uint32)    = 12 (bytes/entry)│
│ Offset 0x24: CompMethodCount (uint32)                      │
│ Offset 0x28: CompMethodLen   (uint32)                      │
│ Offset 0x2C: BlockSize       (uint32)    = 65536 (64 KB)   │
│ Offset 0x30: DirectorySize   (uint32)                      │
│ Offset 0x34: PartitionCount  (uint32)                      │
│ Offset 0x38: ContainerId     (uint64)                      │
│ Offset 0x40: EncryptionGuid  (16 bytes)                    │
│ Offset 0x50: ContainerFlags  (uint32)    = bit flags        │
└─────────────────────────────────────────────────────────────┘

Sections (ต่อจาก Header):
┌───────────────────────────────────────────────────┐
│ Section 1: ChunkIds          (entry_count × 12)   │  ← รหัส Chunk ID ของแต่ละไฟล์
│ Section 2: ChunkOffsetLengths(entry_count × 10)   │  ← Offset 5 bytes + Length 5 bytes (Big-Endian)
│ Section 3: ChunkMetas        (entry_count × 32)   │  ← SHA1 hash + flags
│ Section 4: CompressedBlocks  (block_count × 12)   │  ← ข้อมูลบล็อคบีบอัด (Bit-packed, Little-Endian)
│ Section 5: CompressionNames                        │
│ Section 6: DirectoryIndex    (encrypted)           │
└───────────────────────────────────────────────────┘
```

### 10.3 รูปแบบ Compressed Block Entry (12 bytes, Bit-packed)

```
┌──────────────────────────────────────────────────────┐
│ Bits [0:39]   = Physical Offset ใน UCAS  (40 bits)   │
│ Bits [40:63]  = Compressed Size          (24 bits)   │
│ Bits [64:87]  = Uncompressed Size        (24 bits)   │
│ Bits [88:95]  = Compression Method Index (8 bits)    │
│                 0 = ไม่บีบอัด (None/Raw)              │
└──────────────────────────────────────────────────────┘
Encoding: Little-Endian
```

### 10.4 สคริปต์ UCAS Injection ฉบับสมบูรณ์ (Production Code)

นี่คือโค้ดที่ใช้จริงในตัว Installer:

```python
import os
import struct
from Crypto.Cipher import AES

# ==================== ค่าคงที่ ====================
AES_KEY = bytes.fromhex("014AEC0148FBDEE9640633AAB67521AAB4E1083A98F76FF33DDCF78DAD05BE66")
TARGET_CHUNK_INDEX = 8011  # ตำแหน่งของ fonts_en.uasset ใน UTOC
UTOC_HEADER_SIZE = 144

# ==================== ฟังก์ชันช่วย ====================

def align_to_16(size):
    """ปัดขนาดขึ้นให้หารด้วย 16 ลงตัว (AES Block Size)"""
    return (size + 15) & ~15

def encode_offset_and_length(offset, length):
    """เข้ารหัส Offset (5 bytes) + Length (5 bytes) แบบ Big-Endian"""
    return offset.to_bytes(5, byteorder='big') + length.to_bytes(5, byteorder='big')

def encode_compressed_block_entry(offset, compressed_size, uncompressed_size, method_index):
    """เข้ารหัส Compressed Block Entry (12 bytes, Bit-packed Little-Endian)"""
    raw = (offset & ((1 << 40) - 1))
    raw |= (compressed_size & ((1 << 24) - 1)) << 40
    raw |= (uncompressed_size & ((1 << 24) - 1)) << 64
    raw |= (method_index & 0xFF) << 88
    return raw.to_bytes(12, byteorder='little')

# ==================== ฟังก์ชันหลัก ====================

def inject_font(paks_dir, font_path):
    """
    ฝังฟอนต์ภาษาไทยลงในไฟล์ IoStore ของเกม
    
    paks_dir: โฟลเดอร์ Paks ของเกม
    font_path: พาธไปยังไฟล์ fonts_en.uasset (ภาษาไทย)
    """
    ucas_path = os.path.join(paks_dir, "pakchunk0-WindowsNoEditor.ucas")
    utoc_path = os.path.join(paks_dir, "pakchunk0-WindowsNoEditor.utoc")
    
    # 1. อ่านไฟล์ฟอนต์ภาษาไทย
    with open(font_path, "rb") as f:
        font_data = f.read()
    print(f"📖 อ่านฟอนต์ไทย: {len(font_data):,} bytes")
    
    # 2. อ่าน UTOC Header
    with open(utoc_path, "rb") as f:
        utoc_data = bytearray(f.read())
    
    entry_count = struct.unpack_from('<I', utoc_data, 0x18)[0]
    block_count = struct.unpack_from('<I', utoc_data, 0x1C)[0]
    compression_block_size = struct.unpack_from('<I', utoc_data, 0x2C)[0]  # = 65536
    
    print(f"📋 UTOC: {entry_count:,} entries, {block_count:,} blocks, block_size={compression_block_size}")
    
    # 3. คำนวณ Section Offsets
    chunk_ids_off = UTOC_HEADER_SIZE
    chunk_ol_off = chunk_ids_off + (entry_count * 12)
    chunk_meta_off = chunk_ol_off + (entry_count * 10)
    compressed_blocks_off = chunk_meta_off + (entry_count * 32)
    
    # 4. อ่าน Offset/Length ปัจจุบันของ fonts_en (Chunk #8011)
    ol_pos = chunk_ol_off + (TARGET_CHUNK_INDEX * 10)
    old_offset = int.from_bytes(utoc_data[ol_pos:ol_pos+5], 'big')
    old_length = int.from_bytes(utoc_data[ol_pos+5:ol_pos+10], 'big')
    
    # 5. คำนวณ Block Range เดิม
    first_block = old_offset // compression_block_size
    num_blocks_original = (old_length + compression_block_size - 1) // compression_block_size
    
    # 6. คำนวณ Block Range ใหม่
    mod_blocks_needed = (len(font_data) + compression_block_size - 1) // compression_block_size
    
    if mod_blocks_needed > num_blocks_original:
        print(f"⚠️ ฟอนต์ใหม่ต้องการ {mod_blocks_needed} blocks แต่มีที่ว่างแค่ {num_blocks_original}")
        return False
    
    print(f"🔧 Block range: first={first_block}, original={num_blocks_original}, needed={mod_blocks_needed}")
    
    # 7. เตรียม AES Cipher
    cipher = AES.new(AES_KEY, AES.MODE_ECB)
    
    # 8. Append ฟอนต์ไทยต่อท้ายไฟล์ .ucas (เข้ารหัส AES ทีละ Block)
    with open(ucas_path, "ab") as f_ucas:
        # Align ตำแหน่งเริ่มต้นให้หาร 16 ลงตัว
        current_pos = f_ucas.tell()
        aligned_pos = align_to_16(current_pos)
        if aligned_pos > current_pos:
            f_ucas.write(b'\x00' * (aligned_pos - current_pos))
        
        new_blocks = []
        
        for i in range(mod_blocks_needed):
            # ตัดข้อมูลเป็นชิ้นๆ ขนาด 64 KB
            start = i * compression_block_size
            end = min(start + compression_block_size, len(font_data))
            chunk = font_data[start:end]
            uncompressed_size = len(chunk)
            
            # Pad ให้หาร 16 ลงตัว (AES Block Size = 16 bytes)
            padded_size = align_to_16(len(chunk))
            padded_chunk = chunk + b'\x00' * (padded_size - len(chunk))
            
            # เข้ารหัส AES-256-ECB
            encrypted_chunk = cipher.encrypt(padded_chunk)
            
            # จดตำแหน่งและเขียนลง UCAS
            block_offset = f_ucas.tell()
            f_ucas.write(encrypted_chunk)
            
            new_blocks.append({
                'offset': block_offset,
                'compressed_size': padded_size,
                'uncompressed_size': uncompressed_size
            })
    
    print(f"✅ เขียนฟอนต์ {mod_blocks_needed} blocks ลง UCAS สำเร็จ!")
    
    # 9. อัปเดต UTOC: Offset/Length ของ Chunk #8011
    new_virtual_offset = first_block * compression_block_size
    utoc_data[ol_pos:ol_pos+10] = encode_offset_and_length(new_virtual_offset, len(font_data))
    
    # 10. อัปเดต UTOC: Compressed Block Entries
    for i, block in enumerate(new_blocks):
        block_entry = encode_compressed_block_entry(
            offset=block['offset'],
            compressed_size=block['compressed_size'],
            uncompressed_size=block['uncompressed_size'],
            compression_method_index=0  # 0 = ไม่บีบอัด (Raw + AES)
        )
        block_pos = compressed_blocks_off + ((first_block + i) * 12)
        utoc_data[block_pos:block_pos+12] = block_entry
    
    # 11. เขียน UTOC กลับลงไฟล์
    with open(utoc_path, "wb") as f:
        f.write(utoc_data)
    
    print("✅ อัปเดต UTOC สำเร็จ! ฟอนต์ภาษาไทยพร้อมใช้งานแล้ว!")
    return True
```

### 10.5 ข้อควรระวังสำคัญ

> **⚠️ CAUTION:**
> - ต้องสำรองไฟล์ `pakchunk0-WindowsNoEditor.ucas` และ `.utoc` ก่อนรันทุกครั้ง!
> - ฟอนต์ใหม่ต้องใช้จำนวน Block ไม่เกินฟอนต์เดิม (ต้นฉบับ 351,726 bytes = 6 blocks, ฟอนต์ไทย 380,441 bytes = 6 blocks → พอดี!)
> - ข้อมูลต้องถูก Pad ให้หาร 16 ลงตัวก่อนเข้ารหัส AES
> - Compressed Block Entry ต้องเขียนแบบ **Plaintext** (ไม่เข้ารหัส) — นี่คือจุดสำคัญที่ค้นพบจากการทดลอง

---

## 11. ขั้นตอนที่ 8: ระบบ Build อัตโนมัติ (Automated Pipeline)

สคริปต์ `build_all_auto.py` รวมทุกขั้นตอนด้วยคำสั่งเดียว:

```python
# build_all_auto.py — One-Click Build Pipeline

def main():
    # Step 1: แปลข้อความ (ปิดไว้สำหรับ Distribution)
    # run_command("python run_translation_DI2.py")

    # Step 2: แปลง CSV → Locres
    run_command('pylocres from-csv -p "Translation\\Game_th.csv" '
                '-o "Pack\\DeadIsland\\Content\\Localization\\Game\\en\\Game.locres" -v 2')

    # Step 3: ยัดซับไตเติลไทยกลับเข้า XML
    run_command("python inject_translated_subtitles.py")

    # Step 4: แพ็คเป็นไฟล์ .pak
    run_command("python pack_mod.py")

    # Step 5: คอมไพล์เป็น Smart Installer (.exe)
    # ... (ดูขั้นตอนที่ 9)
```

**การรัน:**
```cmd
python build_all_auto.py
```

---

## 12. ขั้นตอนที่ 9: สร้าง Smart Installer (.exe)

### 12.1 ทำไมต้องมี Installer?

เนื่องจากกระบวนการ UCAS Injection ต้องใช้ Python + pycryptodome ผู้เล่นทั่วไปทำเองไม่ได้ เราจึงสร้างโปรแกรม `.exe` ที่ฝังทุกอย่างไว้ในตัว ผู้เล่นแค่ Double Click ก็ติดตั้งม็อดได้ทันที

### 12.2 ไฟล์ที่ต้องฝังลงใน .exe

| ไฟล์ | ขนาด | หน้าที่ |
|------|------|---------|
| `installer.py` | 6 KB | สคริปต์หลักที่ทำ UCAS Injection + ก๊อปปี้ไฟล์ |
| `fonts_en.uasset` | 380 KB | ฟอนต์ Scaleform GFX ภาษาไทย |
| `pakchunk_default-WindowsNoEditor_Thai_P.pak` | 21.9 MB | ก้อนม็อดข้อความ+ซับ+ฟอนต์ Engine |
| `pakchunk_default-WindowsNoEditor_Thai_P.sig` | ไม่กี่ KB | ลายเซ็นปลอม (Bypass) |

### 12.3 คำสั่ง PyInstaller

```cmd
pyinstaller --onefile --noconsole ^
    --add-data "fonts_en.uasset;." ^
    --add-data "pakchunk_default-WindowsNoEditor_Thai_P.pak;." ^
    --add-data "pakchunk_default-WindowsNoEditor_Thai_P.sig;." ^
    -n DeadIsland2_Thai_Installer ^
    installer.py
```

### 12.4 การทำงานของ Installer

เมื่อผู้ใช้รัน `.exe`:
1. **Auto-Detect:** ค้นหาโฟลเดอร์เกมจาก Registry (Steam) หรือ Default Paths (Epic)
2. **ก๊อปปี้ .pak + .sig** → โฟลเดอร์ `~mods/` ของเกม
3. **UCAS Font Injection** → ผ่าตัดฝังฟอนต์ไทยลงไฟล์ `.ucas`
4. **แสดงผลสำเร็จ** → แจ้งผู้ใช้ว่าติดตั้งเสร็จแล้ว

---

## 13. บทเรียนจากความล้มเหลว (Failed Approaches)

ก่อนจะมาถึงวิธีที่ใช้ได้ผล เราได้ทดลองวิธีอื่นๆ มากมายที่ล้มเหลว:

| วิธีที่ลอง | ผลลัพธ์ | เหตุผลที่ล้มเหลว |
|-----------|---------|------------------|
| วางฟอนต์ไทยในโฟลเดอร์ `~mods/` | ❌ ล้มเหลว | IoStore มี Priority สูงกว่า `~mods` เสมอ → เกมเมินฟอนต์ |
| สร้าง IoStore Container ใหม่ (`.ucas`/`.utoc`) ใส่ฟอนต์แล้ววางใน `~mods/` | ❌ ล้มเหลว | เกมไม่โหลด IoStore จาก `~mods/` — รองรับแค่ `.pak` เท่านั้น |
| ใช้เครื่องมือ `retoc.exe` สร้าง Patch | ❌ ล้มเหลว | ข้อจำกัดของเครื่องมือ — ไม่รองรับ Encrypted Containers |
| เขียนทับ (Overwrite) ข้อมูลฟอนต์ในตำแหน่งเดิมของ `.ucas` | ❌ ล้มเหลว | ฟอนต์ใหม่มีขนาดใหญ่กว่าเดิม → ข้อมูลไฟล์ถัดไปถูกเขียนทับ → เกมพัง |
| ถอดรหัส+เข้ารหัส Compressed Block Array ทั้งหมดใน UTOC | ⚠️ ซับซ้อนเกินไป | ทำได้แต่เสี่ยงพังง่าย — ค้นพบว่า Block Entries เขียนแบบ Plaintext ก็ใช้ได้ |

### วิธีที่ใช้ได้ผล (Final Solution):
**Append + Rewrite** — แปะฟอนต์ท้ายไฟล์ `.ucas` (เข้ารหัส AES) แล้วแก้สารบัญ `.utoc` ให้ชี้มาที่ท้ายไฟล์

---

## 14. ข้อจำกัดของ Xbox Game Pass (WinGDK)

จากการทดลองนำม็อดไปใช้กับเวอร์ชัน Xbox Game Pass (PC) พบว่า **ทำไม่ได้**:

| ปัญหา | รายละเอียด |
|-------|-----------|
| **Signature Verification** | ระบบ Xbox มีการตรวจจับความปลอดภัยที่เข้มงวดกว่า Steam — เทคนิค Bypass ใช้ไม่ได้ |
| **โฟลเดอร์ถูกล็อค** | โฟลเดอร์เกมของ Xbox Game Pass ถูกป้องกันสิทธิ์การเข้าถึง (UWP Sandbox) |
| **IoStore Integrity Check** | แม้จะ Inject ฟอนต์ลง `.ucas` ได้สำเร็จ แอป Xbox จะตรวจ Integrity ของไฟล์เกมเวลาเปิดเกม |

**สรุป:** ม็อดนี้รองรับเฉพาะ **Steam** และ **Epic Games** เท่านั้น

---

## 15. สรุปผลงาน

| หมวด | ปริมาณ |
|------|--------|
| ข้อความ UI ที่แปล | **61,000+** บรรทัด |
| ซับไตเติลบทสนทนา | **32,390** บรรทัด (เกมหลัก + DLC Haus + DLC SoLA + Horde) |
| ฟอนต์ที่แทนที่ | **15** ไฟล์ (1 GFX + 5 UFonts + 9 TTFs) |
| ขนาดไฟล์ม็อด | **~22 MB** (จากเกมขนาด 70 GB+) |
| สคริปต์วิจัย | **35** ไฟล์ (Reverse Engineering) |
| แพลตฟอร์มที่รองรับ | Steam, Epic Games |

---

## 16. ภาคผนวก: ตารางค่าคงที่ทางเทคนิค

### AES Encryption
| รายการ | ค่า |
|--------|-----|
| Algorithm | AES-256-ECB |
| Key (Hex) | `014AEC0148FBDEE9640633AAB67521AAB4E1083A98F76FF33DDCF78DAD05BE66` |
| Block Size | 16 bytes |

### IoStore Target (fonts_en.uasset)
| รายการ | ค่า |
|--------|-----|
| Chunk Index | `8011` |
| Chunk ID | `a037e065e14f812b00000002` (12 bytes) |
| Original Size | 351,726 bytes |
| Modified Size | 380,441 bytes (ฟอนต์ไทย) |
| Virtual Offset | `0x28DD0000` |
| Compression Block Size | 65,536 bytes (64 KB) |

### UTOC Layout Offsets
| Section | Offset | Size per Entry |
|---------|--------|---------------|
| Header | 0 | 144 bytes (fixed) |
| ChunkIds | 144 | 12 bytes |
| ChunkOffsetLengths | 144 + (entry_count × 12) | 10 bytes (5+5, Big-Endian) |
| ChunkMetas | + (entry_count × 10) | 32 bytes |
| CompressedBlocks | + (entry_count × 32) | 12 bytes (Bit-packed, Little-Endian) |

### Translation API Config
| รายการ | ค่า |
|--------|-----|
| API | DeepSeek (deepseek-chat) |
| Temperature | 0.3 |
| Max Tokens | 8,192 |
| Batch Target | 3,000 characters |
| CSV Encoding (UI) | UTF-16-LE |
| CSV Encoding (Subtitles) | UTF-16 (with BOM) |

### คำศัพท์เฉพาะ (Glossary)
| อังกฤษ | ไทย |
|--------|------|
| Hell-A | เฮล-เอ |
| Zombie | ซอมบี้ |
| Slayer | ผู้รอดชีวิต / นักล่าซอมบี้ |
| Autophage | ออโตเฟจ |
| Numen | นูเมน |
| Shambler | แชมเบลอร์ |
| Walker | วอล์กเกอร์ |
| Runner | รันเนอร์ |
| Crusher | ครัชเชอร์ |
| Screamer | สกรีมเมอร์ |
| Slobber | สล็อบเบอร์ |
| Butcher | บุชเชอร์ |
| Mutator | มิวเตเตอร์ |

---

*คัมภีร์ฉบับนี้จัดทำโดย แอดนดหนวด (Ad-Nod-Nuad) × Antigravity AI — กรกฎาคม 2026*
*เอกสารนี้เป็น Knowledge Item (KI) สำหรับใช้อ้างอิงในการทำม็อดภาษาไทยให้เกมอื่นๆ ที่ใช้ Unreal Engine 4/5 ระบบ IoStore*
