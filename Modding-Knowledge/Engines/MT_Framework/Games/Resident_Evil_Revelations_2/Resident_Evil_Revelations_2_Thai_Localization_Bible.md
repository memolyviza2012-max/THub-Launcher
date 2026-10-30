# Resident Evil Revelations 2 — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

> วิเคราะห์ 2026-09-13 จากม็อด `Resident Evil Revelations 2` ของ Lung Dear v1.0; ไม่รันตัวติดตั้งและไม่แก้ไฟล์เกมจริง

## 1. Overview

ม็อดนี้ใช้วิธี **file replacement** ของไฟล์ MT Framework ในเกม Resident Evil Revelations 2: ARC version 7, GMD ข้อความ และคู่ภาพฟอนต์ TEX/GFD. ตัวติดตั้ง batch สำรองต้นฉบับใน `_ThaiMod_Backup_Original` แล้วแทนไฟล์ในช่องภาษา English; DLC ที่ไม่ติดตั้งจะถูกข้าม. README ระบุแปลด้วยมือ 5,886 ข้อความและใช้ Sarabun; ตัวเลข/ชื่อฟอนต์เป็นคำกล่าวของผู้สร้าง ไม่ใช่จำนวน record หรือ metadata ที่ถอดจากไฟล์.

## 2. Technical Stack

| รายการ | สิ่งที่ตรวจพบ |
|---|---|
| Game engine/developer | MT Framework / CAPCOM — ARC/GMD/TEX/GFD family ตรงกับเกมในตระกูลเดียวกัน |
| Project codename | ไม่พบใน payload |
| Archive | `ARC\0` (`41 52 43 00`) ที่ offset 0; version `07 00` ที่ 0x04, count little-endian ที่ 0x06 |
| Encryption | ไม่พบใน ARC ที่ให้มา; entries ทั้ง 4,519 แตก zlib ได้โดยไม่ใช้ key. ไม่ใช่ UE จึงไม่มี UE PAK AES flag |
| Compression | zlib ครบ 4,519/4,519 ARC entries; sampled stream เริ่ม `78 9C`. Packed/raw length และ offset อยู่ใน 80-byte directory entries หลัง 8-byte header |
| Text | GMD binary `47 4D 44 00` (`GMD\0`) version bytes `02 03 01 00`; 227 loose `_eng.gmd` |
| Text encoding | payload ไม่ใช่ UTF-8 ภาษาไทยตรง ๆ; text region ถอด UTF-8 บางส่วนได้เป็น Cyrillic/Latin Extended ที่ remap glyph. ตาราง map ยังไม่พิสูจน์ |
| Font | Bitmap atlas `TEX\0` 7 แผ่น + glyph descriptor `GFD\0` 4 ไฟล์; ไม่มี TTF/OTF |
| Thai source font | README: Sarabun / SIL OFL; เวอร์ชัน/weight/ต้นฉบับจริงตรวจจาก bitmap ไม่ได้ |
| Complexity | ★★★★☆ — ต้องรักษา ARC/GMD, codepoint remap และ UV/metrics ของ GFD พร้อมกัน |

## 3. โครงสร้างไฟล์ (File Architecture)

พาธจริง: `D:\Mods games\Thai Mods\0_Rivet Engineer\02_Workspace\Resident Evil Revelations 2\Resident Evil Revelations 2\` (พาธที่ผู้ใช้ส่งมี backslash และ `_` แยกเกินมา). Scan ได้ **351 ไฟล์ / 104,238,111 bytes**.

```text
Resident Evil Revelations 2/
├── อ่านก่อนติดตั้ง.txt                    8,924 B
├── Install_ThaiMod.bat                    10,665 B
└── mod/
    ├── files.txt                          14,724 B; 348 unique entries ทุกพาธมีไฟล์จริง
    ├── nativePCNext/arc/DX9NEXT/          82 ARC
    ├── nativePCNext/message/win/          227 GMD (_eng)
    ├── nativePCNext/ui_N/00_font/         7 TEX + 4 GFD
    └── dat/DLC_EPISODE_*/arc/DX9NEXT/    28 ARC
```

รวม ARC 110 ไฟล์ / 97,975,084 bytes; GMD 227 / 1,453,149 bytes; TEX 7 / 4,718,732 bytes; GFD 4 / 56,833 bytes. ภายใน ARC 110 ไฟล์มี 4,519 entries; directory เริ่ม offset `0x08`, entry ละ 80 bytes: path 64 bytes ตามด้วย 4 little-endian DWORD ที่สังเกตเป็น type id, packed size, raw size+flags, data offset. ทดสอบ bounds และ zlib inflate ของทุก entry ผ่าน ไม่มี raw-size mismatch. ตัวอย่าง `d2000.arc` มี 22 entries, data แรกที่ offset `0x8000`, compressed stream `78 9C`.

Batch ใช้ `mod/files.txt` ติดตั้ง 348 ไฟล์: 320 ใต้ `nativePCNext` และ 28 ใต้ DLC. `fc /b` ตรวจไฟล์ที่เคยลง, สำรองเพียงครั้งแรก, เขียนผ่าน `.new` แล้ว move ไปแทน. การถอนคืน backup แล้วลบ backup folder หลังคืนสำเร็จ; ควรเก็บ backup เพิ่มเองก่อนทดลอง.

## 4. Font Analysis

GFD ทั้งสี่ตัว: `cap.gfd` 7,873 B, `deco.gfd` 4,984 B, `small.gfd` 13,499 B, `sys_eng.gfd` 30,477 B. ทุกไฟล์เริ่ม `GFD\0 06 0C 01 00`; ชื่อภายในตรงกับกลุ่ม `ui_N\00_font\...`. TEX ทุกไฟล์เริ่ม `TEX\0 9D 20 00 20`. จับคู่จาก basename: cap 2 หน้า, deco 1, small 2, sys_eng 2.

แปลง TEX บนสำเนาด้วย ARCtool 0.9.713 แล้วตรวจ DDS magic `44 44 53 20`:

| Atlas | จำนวน | DDS resolution/codec |
|---|---:|---|
| cap | 2 | 1024×512, DXT5 |
| deco | 1 | 1024×512, DXT5 |
| small | 2 | 1024×1024, DXT5 |
| sys_eng | 2 | 1024×1024, DXT1 |

นี่คือ bitmap atlas ไม่ใช่ฟอนต์ติดตั้ง; ไม่พบ valid SFNT/TTF/OTF ใน loose files หรือ 4,519 inflated ARC entries. ชื่อ Sarabun และ licence มาจาก README เท่านั้น. ไม่ทราบพิกัด UV, advance, bearing, kerning หรือ remap codepoint รายตัวของ GFD อย่างยืนยันได้ จึงไม่เขียน offset injector แบบสมมติ. สระบน/ล่างและวรรณยุกต์ต้องทดสอบกับ atlas + GFD คู่กัน.

## 5. Text Analysis

GMD loose 227 ไฟล์เริ่ม `GMD\0 02 03 01 00`; ที่ 0x14 และ 0x18 เป็น 32-bit fields ที่ผันตามไฟล์ เช่น `d1000_eng.gmd` = 67 และ 68 แต่ยังไม่ยืนยันความหมายของ field จึงไม่ใช้เป็นจำนวนข้อความ. README อ้าง 5,886 ข้อความ; ไม่ควรสับสนกับจำนวน files/metadata. `m03_sys_title_topmenu_eng.gmd` มี label เช่น `03_press_start`, `03_main_menu`, `03_options`; `d1000_eng.gmd` มี key ของ episode/cutscene. ชุด `m*_sys_*` เป็น UI, `d*` บทพูด, `file_*` เอกสาร, `s*` ข้อความฉาก/อื่น ๆ ตามชื่อไฟล์.

การ scan bytes ไม่พบ Thai UTF‑8 sequence ใน GMD เลย แม้ส่วนข้อความท้ายไฟล์ถอด UTF‑8 เป็น Cyrillic/Latin Extended ได้ เช่น `д`, `Ф`, `Ą`; จึงมีหลักฐานการใช้ codepoint remap ให้ atlas ไทย แต่ยังไม่ทราบ mapping แบบหนึ่งต่อหนึ่ง. อย่าแทนข้อความด้วย Unicode Thai ตรง ๆ จนกว่าจะถอด mapping และ validate ในเกม. 259 GMD English entries ที่พบทั้งใน ARC และ loose path **ตรงกันทุกไบต์**; การแก้ข้อความต้อง sync สองตำแหน่ง. DLC ARC เพิ่ม 25 English GMD entries ที่ตรวจได้.

## 6. Cross-Engine Comparison

- [Resident Evil 6](../Resident_Evil_6/Resident_Evil_6_Thai_Localization_Bible.md) ใช้ ARC v7 + zlib และ bitmap TEX เหมือนกัน แต่ Revelations 2 มี GFD แบบ loose และ GMD `_eng` ที่ซ้ำใน ARC; ห้ามนำ offset หรือ text codec ของ RE6 มาใช้ทันที.
- [Resident Evil 0 HD](../Resident_Evil_0/Resident_Evil_0_Thai_Localization_Bible.md) เป็น MT Framework อีกเกมที่แทน archive และ font atlas; ชื่อไฟล์และ layout แตกต่าง. แนวทางที่ใช้ร่วมกันได้คือ scan magic, แตก ARC บนสำเนา, รักษาลำดับ entries และตรวจคู่ atlas/metrics.
- ต่างจาก Prey/CryEngine ที่แก้ SpreadsheetML ใน ZIP ได้ตรง ๆ, Revelations 2 ต้องรักษา GMD binary, remap และ GFD; การทำ text search/replace ระดับ byte เสี่ยงทำให้ offsets เสีย.

## 7. Pipeline — ขั้นตอนสร้างม็อด

1. สำรองเกมเดิมทั้งหมดที่ manifest ระบุ; เก็บ SHA-256 ก่อนแก้. อย่ารัน batch ใน workspace วิเคราะห์.
2. สำหรับ ARC ให้ใช้ ARCtool 0.9.713 `-REV2 -x -txt` บนสำเนา; เก็บ order list ที่ tool สร้างเพื่อ repack. ทดสอบแตก/repack round-trip กับไฟล์ตัวอย่างและเปรียบเทียบรายการ/ข้อมูลภายในก่อนติดตั้ง.
3. สำหรับ GMD ให้ dump label, string pool, offsets และ codepoint mapping จากไฟล์เดิม; อย่าใช้ `-gmd` ของ ARCtool เพราะ README ของ tool ระบุรองรับเฉพาะ Dragon's Dogma. ระบุ placeholder/control codes ก่อนแปล.
4. ปรับข้อความโดย encoder ที่พิสูจน์แล้วว่าแปลง Thai เป็นรหัส slot เดิม; เขียน GMD ใหม่พร้อมแก้ offsets/counts/checksums ที่ format ต้องการ.
5. sync loose GMD กับสำเนา GMD ภายใน ARC ที่คู่กัน; เปรียบเทียบ hash ของ payload ที่ควรเหมือนกัน.
6. สำหรับฟอนต์ แก้ DDS/atlas บนสำเนา, convert กลับ TEX เฉพาะเมื่อรู้ codec/ขนาดเดิม และ inject metrics ใน GFD ด้วย parser ที่พิสูจน์จาก before/after fixtures. ห้ามเปลี่ยนขนาด/format โดยไม่ทดสอบ.
7. ติดตั้งบนสำเนาเกมที่ตรง build ใน English, ทดสอบทุก episode, Raid, UI, file, subtitle และสระ/วรรณยุกต์. DLC ที่ไม่มีในเครื่องควรข้ามตาม script.

## 8. Troubleshooting

| อาการ | ตรวจ |
|---|---|
| ตัวไทยเป็นกล่อง/ผิดรูป | TEX/GFD คู่กันหรือไม่, เกมเลือก English, codepoint mapping ตรงกับ GMD หรือไม่ |
| สระ/วรรณยุกต์ซ้อน | ตรวจ anchor/bearing/advance ใน GFD และ glyph ใน DDS; อย่าแก้ text อย่างเดียว |
| บางฉากยังเป็นอังกฤษ | ตรวจคู่ loose GMD + embedded ARC, DLC episode path และ manifest |
| เกมค้าง | ARC entry order/offset/size, GMD string offsets และ TEX codec ไม่ตรงเดิม |
| ถอนแล้วไม่กลับอังกฤษ | Backup อาจขาดเพราะไฟล์เคยเป็นม็อดก่อนรัน installer; ใช้ Steam Verify กับ build ที่ถูกต้อง |
| `Missing in game` | เวอร์ชันเกมไม่ตรงหรือ DLC ไม่ติดตั้ง; อ่าน install_log และเทียบพาธจริงก่อนคัดลอก |

## 9. Required Tools

| Tool | ใช้ทำอะไร | Source |
|---|---|---|
| ARCtool 0.9.713 (`-REV2`) | แตก/แพ็ก ARC และแปลง TEX↔DDS บนสำเนา | `E:\Mod_Workspace\Tool\ARCtool_0.9.5\ARCtool.exe`, readme ในโฟลเดอร์เดียวกัน |
| Python `struct`/`zlib`/hashlib | ตรวจ ARC v7, bounds, decompression และ hashes | Python standard library |
| DDS viewer / image editor แบบ offline | ตรวจ glyph atlas ที่แปลงแล้ว | เครื่องมืออ่าน DDS ที่ผู้ใช้มีสิทธิ์ใช้ |
| GMD/GFD parser ที่ validate กับ build นี้ | จำเป็นก่อนแก้ text/metrics อัตโนมัติ | ยังไม่พบ parser ที่ยืนยันได้ใน workspace |

## 10. Extracted Assets

- [Assets/Payload](Assets/Payload/) เก็บม็อดต้นทางครบ 351 ไฟล์ / 104,238,111 bytes รวม batch/readme/manifest; ไม่ได้แตะเกมจริง.
- [Assets/Fonts](Assets/Fonts/) เก็บ TEX 7 และ GFD 4 ตัวที่เป็นฟอนต์จริง.
- [Assets/Textures](Assets/Textures/) เก็บ DDS ที่แปลงจาก atlas 7 แผ่น พร้อม TEX ต้นทางและ metadata ของ converter.
- [Assets/Analysis/d2000](Assets/Analysis/d2000/) เป็นตัวอย่าง ARC ที่แตกผ่าน 22 entries ใช้ยืนยันเส้นเชื่อม ARC ↔ GMD.
- [Assets/Fonts/EXTRACTION_NOTE.txt](Assets/Fonts/EXTRACTION_NOTE.txt) อธิบายเหตุผลที่ไม่มี TTF/OTF ให้สกัด.

## 11. M2M Protocol — bitmap-font automation boundary

Phase 7 ใช้เพราะเกมนี้มี bitmap atlas. Pipeline อัตโนมัติทำได้เฉพาะเมื่อมี **GMD codepoint map และ GFD record layout ที่พิสูจน์แล้ว**; ข้อมูลสองส่วนนี้ยังไม่ครบ จึงไม่ปลอมสคริปต์ว่า copy/run แล้วสร้างม็อดสำเร็จ. โครงสร้างที่ AI ถัดไปต้องทำมีดังนี้:

```python
# 1. Render atlas from a licensed source font, never overwrite the only source.
from PIL import Image, ImageDraw, ImageFont
font = ImageFont.truetype('licensed-source.ttf', 48)
sheet = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
draw = ImageDraw.Draw(sheet)
# slots must come from a verified GFD decoder, including original UV/metrics.
for slot in verified_slots:
    draw.text((slot.x, slot.y), slot.character, font=font, fill=(255,255,255,255))
sheet.save('atlas-preview.png')  # encode DXT1/DXT5 only after verified comparison

# 2. Shape/map text with a verified table; never infer from visual similarity.
import unicodedata
def encode_thai(text, verified_map):
    text = unicodedata.normalize('NFC', text)
    return ''.join(verified_map.get(ch, ch) for ch in text)

# 3. Guarded GFD injection: offsets and field types must be decoded/validated.
import struct
def write_verified_uv(data, record, uv):
    assert data[:4] == bytes((0x47, 0x46, 0x44, 0x00))
    assert data[record.offset:record.offset+len(record.before)] == record.before
    assert 0 <= record.offset <= len(data)-16
    struct.pack_into('<4f', data, record.offset, *uv)
```

`verified_slots`, `verified_map` และ `record.offset/before` ไม่ใช่ค่าที่เดาได้จาก extension; ต้องได้จาก parser, fixture และ in-game round-trip ที่ตรวจ hash/ภาพ. หากไม่มีข้อมูลเหล่านี้ **หยุดก่อน repack** เพื่อไม่สร้าง GFD/GMD เสีย.
