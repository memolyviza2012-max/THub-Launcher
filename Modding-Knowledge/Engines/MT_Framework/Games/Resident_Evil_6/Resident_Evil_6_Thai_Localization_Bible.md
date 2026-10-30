# Resident Evil 6 — Thai Localization Modding Bible
### Opus Edition — Advanced Deep Analysis (Rivet Engineer)

> **Generated:** 2026-07-06  
> **Analyst:** Rivet Engineer Advanced (Antigravity AI)  
> **Mod Author:** Community Thailand  
> **Status:** ✅ Complete (10/10 Mandatory Sections)

---

## 1. Overview

**Resident Evil 6** พัฒนาโดย **Capcom** โดยใช้เอนจิน **MT Framework** รุ่นปรับปรุง ม็อดแปลไทยนี้ใช้สถาปัตยกรรมแบบ **File Replacement (Native Archive)** ซึ่งเป็นการสกัดและปรับแต่งไฟล์ `.arc` ของตัวเกมโดยตรง ไม่มีการใช้ DLL แทรกแซงระบบ (No Injection) ข้อมูลข้อความและฟอนต์ถูกบีบอัดอยู่ภายในไฟล์ Archive เหล่านี้

**Mod Architecture Pattern:** Native File Replacement (ARC)

---

## 2. Technical Stack

| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | MT Framework (Capcom) |
| **Archive Format** | `.arc` (Version 7) — มาตรฐานของเกม MT Framework ยุคเก่า (RE5, RE6, Dragon's Dogma) |
| **AES Encryption** | ❌ **No** — ไม่มีการเข้ารหัส |
| **Compression** | ✅ **Zlib** — ไฟล์แต่ละชิ้นที่บรรจุอยู่ภายใน `.arc` จะถูกบีบอัดด้วย Zlib (โดยสังเกตจาก Flag bit ที่ตำแหน่งที่ 30 ของ File size คือ `0x40000000`) |
| **Font System** | **Baked Bitmap / Texture (TEX)** — ตัวเกมไม่รองรับ TTF/OTF ฟอนต์ถูกเรนเดอร์เป็นภาพบิตแมป (.tex) ทำงานคู่กับไฟล์ FNT/SPC (Spacing/Kerning) |
| **Text System** | ไฟล์สกุล `.gmd` หรือ `.msg` ที่เก็บอยู่ใน ARC |
| **Mod Complexity** | ★★★☆☆ (กระบวนการวาดฟอนต์ Bitmap ทำได้ยากและใช้เวลา) |

---

## 3. โครงสร้างไฟล์ (File Architecture)

```
Resident Evil 6/
├── modinfo.ini                         ← ข้อมูล Metadata ของ Mod สำหรับ Mod Manager (Fluffy)
├── RE6_TH.jpg                          ← รูปหน้าปก Mod
└── nativePC/
    └── arc/
        └── DX9/
            ├── Core.arc                ★ ไฟล์หลัก บรรจุฟอนต์ UI (.tex, .fnt) และระบบพื้นฐาน
            ├── Load_eng.arc            ← ข้อความตอนโหลดหน้าจอ
            ├── Msg_eng.arc             ★ ไฟล์ข้อความหลัก (Main Script)
            ├── Title.arc               ← ภาพหน้าจอ Title
            └── Title_eng.arc           ← ข้อความในจอ Title
```

> **ข้อสังเกต:** ตัวเกมโหลดไฟล์แยกระหว่าง "ภาษาอังกฤษ" (ต่อท้ายด้วย `_eng`) ม็อดเดอร์ทำการแพ็กไฟล์เข้าไปทับเวอร์ชันภาษาอังกฤษโดยตรง (แทนที่ของเดิม)

---

## 4. Font Analysis

### 4.1 Font Identification

MT Framework **ไม่รองรับการโหลดไฟล์ TrueType (.ttf) แบบ Dynamic** ข้อมูลฟอนต์ถูกแปลงเป็นภาพ Bitmap (Texture) ตั้งแต่กระบวนการพัฒนา ม็อดเดอร์ใช้วิธี **"ตีพิมพ์"** สระและพยัญชนะภาษาไทยลงไปบนภาพ Texture

| ไฟล์ที่สกัดจาก Core.arc | Magic Bytes | Format | อธิบาย |
|---|---|---|---|
| `soft\message\font\mes_font_00_ID` | `TEX\x00` (`54 45 58 00`) | MT Framework Texture | ไฟล์ภาพบิตแมปที่วาดฟอนต์ภาษาไทยเอาไว้ |
| `soft\message\font\mes_font` | — | FNT/SPC | ตำแหน่งพิกัด (UV Mapping) และ Spacing ของแต่ละตัวอักษร |

### 4.2 Font Metadata

ไม่สามารถดึงข้อมูลลิขสิทธิ์และชื่อฟอนต์ด้วย Metadata (เช่น TTF header) ได้ เนื่องจากถูกวาดเป็นภาพ Pixel เรียบร้อยแล้ว แต่จากการตรวจสอบด้วยสายตา พบว่าเป็นฟอนต์กลุ่มไม่มีหัว (Sans-Serif) สไตล์ Modern 

### 4.3 Thai Glyph Support & Shaping

- **ไม่มีการทำ Shaping อัตโนมัติ:** เพราะฟอนต์เป็นภาพ Bitmap ตายตัว
- **สระลอย:** ม็อดเดอร์มักใช้วิธี "ยืด/หด" สระ หรือแมปปิ้งสระและวรรณยุกต์พิเศษไว้ในช่องว่างของตาราง ASCII (เช่น ช่วง 0x80-0xFF) แล้วเขียนสคริปต์ (หรือแก้ .fnt) ให้เรียกภาพจากพิกัดนั้นมาแสดงผลเพื่อหลบหลีกปัญหาสระซ้อน

---

## 5. Text Analysis

### 5.1 ARC & MSG File Analysis

- **Header ของ ARC:** ขึ้นต้นด้วย `41 52 43 00` (ARC\x00) เวอร์ชัน 0x0700
- **การบีบอัด (Zlib):** เมื่ออ่าน Header ไฟล์ย่อย จะพบว่า Flag `0x40000000` ทำงาน ตัวข้อมูลถูกขึ้นต้นด้วย Header Zlib `78 9C`
- **ไฟล์ Text (.msg):** เป็นไฟล์ Binary Proprietary ของ Capcom ซึ่งเก็บข้อความที่ผ่านการแทนที่ด้วยรหัสภาษาไทยแล้ว

---

## 6. Cross-Engine Comparison

### เปรียบเทียบกับเกมและ Engine อื่นๆ

| เกม | Engine | Font System | File Format | Mod Pattern |
|---|---|---|---|---|
| **Resident Evil 6** | MT Framework | Baked Bitmap (.tex) | ARC (v7) + Zlib | Native File Replacement |
| **Monster Hunter World** | MT Framework (Gen 2) | Baked Bitmap (.tex) | chunk.bin / PKG | File Replacement |
| **Resident Evil 2/3/4 Remake** | RE Engine | Bitmap / SDF Font (.tex) | PAK (.pak) | File Replacement |
| **Avowed** | Unreal Engine 5 | TrueType (.ufont) | PAK / IoStore | Native File Replacement |
| **Wasteland 3** | Unity | TrueType (.ttf) | Runtime BepInEx | Hybrid (Injection) |

**Key Insights:**
- สไตล์การทำฟอนต์ของ MT Framework และ RE Engine แทบไม่ต่างกันเลยในแง่ของ "ความน่าปวดหัว" ม็อดเดอร์จะต้องวาดตัวอักษรลงบน Texture 2D (.tex) และปรับแก้ไฟล์ mapping (.fnt) ด้วยมือเสมอ
- ต่างจากฝั่ง Unity / UE ที่สามารถนำไฟล์ `.ttf` โยนใส่ได้โดยตรง

---

## 7. Pipeline — ขั้นตอนสร้างม็อด

### การแพ็กไฟล์ ARC
```
1. ใช้โปรแกรม ARCtool หรือ FluffyQuack's ARC Tool แยกไฟล์ .arc ออกเป็นโฟลเดอร์
2. ค้นหาไฟล์ .tex ในโฟลเดอร์ font แล้วแปลง .tex เป็น .dds (DirectDraw Surface)
3. ใช้ Photoshop หรือ GIMP แก้ไขภาพ .dds วาดฟอนต์ไทยลงไป
4. ค้นหาไฟล์ .msg (ข้อความ) ใช้เครื่องมือแกะ .msg ออกมาเป็น .txt
5. แปลข้อความภาษาไทย
6. ใช้เครื่องมือแพ็ก .txt กลับไปเป็น .msg
7. ใช้ ARCtool แพ็กทุกอย่างกลับเป็นไฟล์ .arc (พร้อมระบบบีบอัด Zlib อัตโนมัติ)
```

---

## 8. Troubleshooting

### 🔴 ปัญหาที่ 1: หน้าจอโหลด/ข้อความในเกมค้าง
| สาเหตุ | วิธีแก้ |
|---|---|
| ไฟล์ ARC ถูกบีบอัดหรือแพ็กด้วยเวอร์ชันผิด | ต้องตั้งค่าเวอร์ชันของ ARCtool ให้ตรงกับเกม (RE6 ใช้ Version 7) หากใช้พารามิเตอร์ผิดเกมจะแครชทันที |

### 🔴 ปัญหาที่ 2: สระ/ตัวอักษรภาษาไทยแสดงผลเป็นสีดำหรือโปร่งใส
| สาเหตุ | วิธีแก้ |
|---|---|
| บันทึกไฟล์ .dds ผิด Format (Alpha Channel หาย) | ไฟล์ Texture ของฟอนต์ต้องบันทึกเป็นฟอร์แมต DXT5 หรือ DXT3 ที่มี Alpha Channel เพื่อให้พื้นหลังฟอนต์โปร่งใส |

---

## 9. Required Tools

| เครื่องมือ | หน้าที่ | แหล่งดาวน์โหลด |
|---|---|---|
| **ARCtool** | แตกและแพ็กไฟล์ .arc ของ MT Framework | [Fluffy Manager / ARCtool] |
| **RE6 MSG Tool** | แปลงไฟล์ข้อความ .msg เป็น Text | เครื่องมือจาก Xentax / Zenhax |
| **Noesis / Tex to DDS** | แปลงไฟล์ .tex เป็น .dds เพื่อแก้ฟอนต์ | เสิร์ชคำว่า "RE6 tex to dds converter" |

---

## 10. Extracted Assets

### ⚠️ ไม่สามารถทำการ Extract รูปแบบ TrueType (TTF) ได้

**เหตุผลทางเทคนิค:** ตามกระบวนการ Rivet Engineer Advanced, ทีมงานได้ทำการแกะไฟล์ `Core.arc` ทะลวงระบบบีบอัด Zlib จนไปถึงแก่นไฟล์ `mes_font_00_ID` 

ผลการตรวจสอบพบ Magic Bytes ของไฟล์คือ `TEX\x00` (`54 45 58 00`) 
นั่นหมายความว่า ฟอนต์ในเกม Resident Evil 6 ถูกบันทึกเป็น **ภาพบิตแมป 2 มิติ (Texture Format)** ไม่ได้เป็นการนำเข้าไฟล์ฟอนต์ปกติ (No `.ttf` or `.otf` inside). 

ดังนั้น เราจึง **ไม่สามารถดึงไฟล์ฟอนต์ออกมาให้ผู้ใช้ติดตั้งบนคอมพิวเตอร์หรือพิมพ์ใช้งานได้** สิ่งที่ได้ออกมาจะเป็นเพียงภาพสไปรต์ (Sprite Sheet) ของตัวอักษรเท่านั้นครับ

---

*📖 Thai Localization Modding Bible — Opus Edition*  
*สร้างโดย Rivet Engineer Advanced Protocol*
