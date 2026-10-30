# Risen — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Risen is an action RPG developed by **Piranha Bytes** using their proprietary **Genome Engine** (same engine as Gothic 3). The Thai localization mod (by **EN0VA**, version 1.7) uses a **Multi-Layer Engine Override** approach: a patched `Engine.dll` for Thai font rendering support, a `gui2.p00` archive containing Thai TTF fonts, and a `strings.p00` archive with all translated text. The `.p00` format is Genome Engine's proprietary **G3V0 archive** format.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Genome Engine (Piranha Bytes proprietary) |
| **Developer** | Piranha Bytes |
| **Mod Author** | EN0VA (v1.7) |
| **Archive Format** | `.p00` (G3V0 Archive, Magic: `\x01\x00\x00\x00G3V0`) |
| **Font System** | Raw TTF embedded in `gui2.p00` |
| **Thai Font** | **Quorum Medium BT** + **Free Sans** (ดัดแปลงเพิ่ม Thai 87 codepoints) |
| **Font License** | Google Sans OFL (แนบใบอนุญาตมาด้วย) |
| **Text System** | G3V0 compiled string tables (`strings.p00`) |
| **Text Encoding** | **UTF-16LE** |
| **DLL Patching** | `Engine.dll` (13.0 MB) — แก้ไขเพื่อรองรับ Thai text rendering |
| **Mod Complexity** | ★★★★☆ (DLL Patch + G3V0 Archive + Custom Font) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
ม็อดนี้มีโครงสร้าง 3 ชั้นที่ต้องทำงานร่วมกัน:

```text
Risen/
├── bin/
│   └── Engine.dll                     (13.0 MB — Patched DLL สำหรับ Thai rendering)
│
├── data/
│   ├── common/
│   │   └── gui2.p00                   (383 KB — G3V0 archive, ฟอนต์ไทย)
│   │       ├── [Embedded] Quorum Medium BT    (191 KB — 87 Thai codepoints)
│   │       └── [Embedded] Free Sans           (191 KB — 87 Thai codepoints)
│   │
│   └── compiled/
│       ├── strings.p00                (29.1 MB — G3V0 archive, ข้อความแปลทั้งหมด)
│       ├── images.p00                 (8.7 KB — G3V0 archive, รูปภาพ UI)
│       └── library.p00               (2.8 KB — G3V0 archive, ข้อมูลอ้างอิง)
│
└── licenses/
    └── GoogleSans-OFL.txt             (4 KB — SIL Open Font License)
```

---

## 4. Font Analysis

### 4.1 Quorum Medium BT — ฟอนต์หลัก
- **Offset:** 48 ใน gui2.p00
- **Size:** 191,834 bytes
- **Thai Coverage:** 87 codepoints (U+0E00–U+0E7F)
- **ลักษณะ:** Serif/rounded typeface ให้ความรู้สึกแฟนตาซียุคกลาง เหมาะกับบรรยากาศเกม

### 4.2 Free Sans — ฟอนต์เสริม
- **Offset:** 191,884 ใน gui2.p00
- **Size:** 191,762 bytes
- **Thai Coverage:** 87 codepoints (U+0E00–U+0E7F)
- **ลักษณะ:** Sans-serif font สำหรับ UI/HUD ที่ต้องการความชัดเจน
- **License:** GNU FreeFont (GPL + Font Exception)

### 4.3 Engine.dll Patching
README ระบุว่ามีการแก้ไข SemiBold 600 weight และตำแหน่งตัวเลขคีย์ลัด — หมายความว่า `Engine.dll` ถูก patch เพื่อ:
- รองรับ Thai text shaping (สระลอย/วรรณยุกต์)
- ปรับ font metrics (SemiBold 600)
- แก้ตำแหน่ง hotkey numbers ให้ตรงกับ Thai glyphs

---

## 5. Text Analysis

### 5.1 G3V0 String Tables (UTF-16LE)
- **ขนาดไฟล์:** 29.1 MB (strings.p00)
- **Encoding:** **UTF-16LE** (ไม่ใช่ UTF-8!)
- **Thai Characters:** **384,642 ตัวอักษร** (UTF-16LE)
- **Format:** G3V0 compiled binary ที่เก็บ string tables หลายภาษาไว้ในไฟล์เดียว

### 5.2 ตัวอย่างข้อความ
ข้อความครอบคลุมทั้ง UI, dialogue, quest descriptions, และ combat messages
(ข้อความถูกเข้ารหัส UTF-16LE ภายใน G3V0 structure จึงต้องใช้ parser เฉพาะในการอ่าน)

---

## 6. Cross-Engine Comparison
เปรียบเทียบกับเกมที่ใช้ Proprietary Engine + DLL Patching:

| Feature | Risen | Medieval Dynasty | Grim Dawn |
|---|---|---|---|
| **Engine** | Genome (G3V0) | UE4 + bitfix | Crate (ARC) |
| **DLL Patch** | ✅ Engine.dll (13 MB) | ✅ dsound.dll + bitfix.dll | ❌ |
| **Archive** | .p00 (G3V0) | .pak (UE4) | .arc |
| **Text Encoding** | UTF-16LE | UTF-16LE | UTF-8 |
| **Font in Archive** | Raw TTF in .p00 | Raw TTF in .pak | FNTX Bitmap |
| **Thai Chars** | 384K | ~200K | ~923K |
| **Complexity** | ★★★★☆ | ★★★★☆ | ★★★☆☆ |

**จุดร่วม:** ทั้ง Risen และ Medieval Dynasty ต้องใช้ DLL Patching เพื่อแก้ปัญหา Thai text rendering ที่ engine ดั้งเดิมไม่รองรับ

---

## 7. Pipeline — ขั้นตอนสร้างม็อด

1. **Reverse Engineering DLL:** วิเคราะห์ `Engine.dll` ด้วย IDA Pro/Ghidra เพื่อหา font rendering functions
2. **DLL Patching:** แก้ไข binary ของ Engine.dll ให้รองรับ Thai text (shaping, metrics)
3. **Font Modification:** ใช้ FontForge เพิ่ม Thai glyphs ลงในฟอนต์ Quorum และ Free Sans
4. **G3V0 Repacking (gui2):** แพ็คฟอนต์กลับเข้า `gui2.p00` ด้วย Genome modding tools
5. **Text Translation:** แปลข้อความและ compile กลับเป็น `strings.p00` (UTF-16LE)
6. **Testing:** ทดสอบว่าสระลอย/วรรณยุกต์แสดงผลถูกต้อง

---

## 8. Troubleshooting
- **ตัวอักษร A-Z แทรกในข้อความ:** เป็นบั๊กที่เกิดจากเล่นต่อเนื่อง (v1.7 แก้แล้ว) — เกิดจาก memory buffer ของ Engine.dll
- **สระลอย/วรรณยุกต์ผิดตำแหน่ง:** Engine.dll patch อาจไม่ครอบคลุม ต้องตรวจ font metrics
- **กลับเป็นภาษาอังกฤษ:** Steam Verify Files จะทับไฟล์ม็อดทั้งหมด ต้องลงม็อดใหม่
- **เกมแครช:** Engine.dll เวอร์ชันไม่ตรง ต้องใช้กับเกมเวอร์ชันที่ถูกต้อง

---

## 9. Required Tools
| Tool Name | Purpose | Source |
|---|---|---|
| Genome G3V0 Tools | Pack/Unpack ไฟล์ `.p00` | [Community / Piranha Bytes modding] |
| FontForge | แก้ไข TTF เพิ่ม Thai glyphs | [FontForge.org] |
| IDA Pro / Ghidra | Reverse engineer Engine.dll | [hex-rays / NSA] |
| HxD | Hex editing สำหรับ DLL patching | [mh-nexus] |

---

## 10. Extracted Assets
- **Quorum Medium BT (ดัดแปลงเพิ่มไทยแล้ว):**
  - [Quorum_Medium_BT.ttf](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Genome_Engine/Games/Risen/Assets/Fonts/Quorum_Medium_BT.ttf) (191 KB, 87 Thai codepoints)
- **Free Sans (ดัดแปลงเพิ่มไทยแล้ว):**
  - [Free_Sans.ttf](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Genome_Engine/Games/Risen/Assets/Fonts/Free_Sans.ttf) (191 KB, 87 Thai codepoints)

---

## 11. M2M Protocol
**(สำหรับ AI Agent ที่ต้องการนำคัมภีร์ไปรันสร้างม็อดอัตโนมัติ)**

### ข้อจำกัดสำหรับ AI
- **Text Translation:** ⚠️ AI อ่าน UTF-16LE ได้ แต่ต้องมี G3V0 parser เพื่อ extract/rebuild strings.p00
- **Font Pipeline:** ✅ AI สามารถแก้ไข TTF ด้วย FontForge CLI ได้
- **DLL Patching:** ❌ AI ไม่สามารถ patch Engine.dll ได้ด้วยตนเอง (ต้องใช้ความรู้ reverse engineering ระดับ x86 assembly)
- **G3V0 Archive:** ⚠️ ต้องมี G3V0 packer/unpacker เฉพาะ
