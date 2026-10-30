# 🛠️🔥 Extreme Breakthrough & Custom Tool Synthesizer Guide (โปรโตคอลฝ่าทางตันและสร้างเครื่องมือเฉพาะกิจขั้นสูงสุด)

> **คู่มือและโปรโตคอลวิศวกรรมย้อนรอยขั้นสูงสุด (Deep Reverse Engineering & Tool Forge)**: ออกแบบมาเพื่อควบคุมให้ AI Helper และ autonomous coding agents (Antigravity, Claude Code, Cursor) ไม่ยอมแพ้เมื่อพบอุปสรรคทางเทคนิค โดยสั่งการให้ทำการสืบค้นข้อมูลเชิงลึกรอบด้าน (Deep Research) และลงมือสร้างเครื่องมือเฉพาะกิจ (Dedicated Tool Synthesis) ขึ้นมาแก้ปัญหาจนกระทั่งสำเร็จ 100%

---

## 1. ที่มาและปรัชญา (Philosophy & The "Never Surrender" Rule)

ในการทำ Mod แปลภาษาเกม มักจะเจอกำแพงทางเทคนิคที่เครื่องมือสำเร็จรูปทั่วไป (Off-the-shelf tools เช่น QuickBMS, AssetStudio, UnrealPak, UModel) ใช้งานไม่ได้ เช่น:
1. **ไฟล์แพ็คเฉพาะตัว (Proprietary / Custom Archives)** ที่พัฒนาขึ้นเองในสตูดิโอ
2. **การเข้ารหัสและบีบอัดผสม (Hybrid Compression & Encryption)** เช่น Oodle Kraken, Zstandard, AES-256 แบบปรับแต่ง Key/IV
3. **ระบบฟอนต์แบบ Custom Shader หรือ Hardcoded Glyph Atlas** ที่ไม่มีเครื่องมือภายนอกรองรับ
4. **การตรวจจับ Integrity Check หรือ DRM** ที่ทำให้เกมแครชเมื่อไฟล์บนดิสก์ถูกแก้ไข

### กฎเหล็ก: ห้ามยอมแพ้เด็ดขาด (The Never-Surrender Directive)
AI Agent **ห้ามสรุปว่า "ทำไม่ได้", "เกมนี้ไม่รองรับ", หรือหยุดรอเฉยๆ อย่างสิ้นหวัง** เป็นอันขาด เมื่อวิธีมาตรฐานล้มเหลว ให้เปิดโหมด **Extreme Breakthrough** ทันที เพื่อนำทักษะด้าน Software Engineering และ Reverse Engineering ขั้นสูงสุดมาสร้างทางออกใหม่ด้วยตนเอง

---

## 2. แผนผังการทำงาน 5 ขั้นตอน (The 5-Phase Breakthrough Lifecycle)

```
      ┌────────────────────────────────────────────────────────┐
      │   Standard Method Failed / Proprietary Format Blocked   │
      └───────────────────────────┬────────────────────────────┘
                                  │
                                  ▼
      ┌────────────────────────────────────────────────────────┐
      │  Phase 1: 360° Exhaustive Intelligence Gathering       │
      │  (GitHub, QuickBMS Repos, XeNTaX/ZenHax, Binary Hex)   │
      └───────────────────────────┬────────────────────────────┘
                                  │
                                  ▼
      ┌────────────────────────────────────────────────────────┐
      │  Phase 2: Custom Tool Synthesis (Tool Forge)           │
      │  (Write Binary Parser / Repacker / Hook DLL in 05/)    │
      └───────────────────────────┬────────────────────────────┘
                                  │
                                  ▼
      ┌────────────────────────────────────────────────────────┐
      │  Phase 3: Relentless Iterative Validation Loop         │
      │  (Micro-sample test → Roundtrip verification → Fix)    │
      └───────────────────────────┬────────────────────────────┘
                                  │
                  ┌───────────────┴───────────────┐
                  ▼                               ▼
               Success                         Failure
      ┌───────────────────────────┐   ┌───────────────────────────┐
      │ Phase 4: Proceed to POC   │   │ Analyze Crash / Adjust    │
      │ & Knowledge Codification  │   │ Offsets / Memory Hook     │
      └───────────────────────────┘   └─────────────┬─────────────┘
                                                    │
                                                    └─── (Loop Phase 3)
```

---

## 3. รายละเอียดการปฏิบัติการ 5 ขั้นตอน

### Phase 1: สืบค้นข้อมูลเชิงลึก 360 องศา (Exhaustive Deep Research)
เมื่อไฟล์เกมเปิดไม่ได้หรือไม่ทราบโครงสร้าง:
1. **ชุมชนและคลังโค้ดสากล**:
   - ค้นหาใน GitHub (เช่น `"{GameName} tool"`, `"{ArchiveExtension} unpacker"`, `"{Engine} text extract"`)
   - สืบค้นฐานข้อมูลเก่าของ XeNTaX, ZenHax, Xhacker, Zenhax Forum Archive, NexusMods
   - ตรวจสอบคลังสคริปต์ QuickBMS (aluigi.altervista.org) สำหรับโครงสร้างไฟล์ที่คล้ายกัน
2. **ชันสูตรโครงสร้างไฟล์ไบนารี (Binary Forensics)**:
   - ตรวจสอบ Hex 64 ไบต์แรกเพื่อหา **Magic Bytes** (เช่น `UnityFS`, `AKPK`, `RIFF`, `PAK`, `CPK`)
   - ตรวจสอบ **ลายเซ็นการบีบอัด (Compression Signatures)**:
     - `78 9C` / `78 DA` / `78 01`: Zlib Deflate
     - `28 B5 2F FD`: Zstandard (zstd)
     - `04 22 4D 18`: LZ4 Frame
     - `Kraken` / `Mermaid` / `Selkie` / `Leviathan`: RAD Game Tools Oodle
   - ตรวจจับตาราง Offset และขนาด (TOC - Table of Contents): สังเกตตัวเลข uint32/uint64 ที่เรียงตัวเป็นลำดับเพิ่มขึ้น
3. **ชันสูตรไบนารีเกม (Executable / Assembly Forensics)**:
   - รันคำสั่ง `strings` หรือเปิด IDA / Ghidra / x64dbg บนไฟล์ `.exe` หรือ `.dll` ของเกม
   - สำหรับ Unity IL2CPP: ใช้ `Il2CppDumper` ดึง `dump.cs` และ `script.json` เพื่อหา Method ชื่อ `Load`, `Deserialize`, `GetString`
   - ค้นหา Encryption Key หรือ Salt ที่ฝังอยู่ใน Binary

---

### Phase 2: วิศวกรรมสร้างเครื่องมือเฉพาะกิจ (Custom Tool Forge)
ไม่ต้องรอคอยเครื่องมือสำเร็จรูปจากบุคคลอื่น ให้ AI สร้างเครื่องมือเฉพาะทางขึ้นมาเองในโฟลเดอร์โปรเจกต์ `{Workspace}/05_Scripts_and_Tools/` หรือ `tools/flagship/GameBridges/`:

1. **Custom Binary Parser & Repacker (Python `struct` / `io.BytesIO`)**:
   - เขียน Class ตัวอ่านไบนารีที่อ่าน Header, แกะ Chunk Data, ดึง String Table ออกมาเป็น CSV (คอลัมน์มาตรฐาน TStudio: `key,source,translation,context,file_path`)
   - เขียนฟังก์ชัน Repacker ที่คำนวณ:
     - ขนาดความยาวของสตริงใหม่ (String Length Prefix: Pascal uint8/uint16 หรือ C-String null-terminated)
     - ปรับปรุงตาราง Offset ใน Header ให้ชี้ตำแหน่งที่ถูกต้อง
     - Padding ข้อมูลให้ตรงกับ Block Alignment (เช่น 4-byte, 16-byte, หรือ 2048-byte sector boundary)
     - คำนวณ Checksum / CRC32 ใหม่หากไฟล์มีการตรวจสอบ
2. **Custom Decompressor / Decryptor Bridge**:
   - เรียกใช้ Library ภาษา C ผ่าน `ctypes` (เช่น `oo2core_9_win64.dll` สำหรับ Oodle, `zstandard` สำหรับ Zstd)
   - เขียนสคริปต์ XOR / AES decryptor หากข้อมูลถูก Mask ด้วย Key คงที่
3. **Font Surgery & PUA Elevation**:
   - หากเอนจินไม่รองรับ OpenType Shaping ภาษาไทย ให้เขียนสคริปต์แปลงวรรณยุกต์และสระลอยเข้าสู่ PUA (`0xF000`–`0xF89F`)
   - ใช้ `fontTools` ยกวรรณยุกต์ใน Composite Glyphs ขึ้น +160 units ป้องกันสระจม
   - หากเกมใช้ Texture Font Atlas ให้เขียนสคริปต์ PIL/OpenCV เรนเดอร์ตัวอักษรไทยลงบน Atlas พิกัดเดิม
4. **Runtime Memory Hook Fallback (เมื่อไฟล์บนดิสก์ถูกล็อก)**:
   - หากไฟล์ถูกล็อกด้วย Denuvo, Arxan, หรือ File Integrity Hash ที่แก้ไฟล์ดิสก์แล้วเกมแครช:
   - เปลี่ยนกลยุทธ์เป็นการทำ **Runtime Hooking**:
     - สร้าง DLL Proxy (`dxgi.dll`, `version.dll`, `dinput8.dll`) หรือปลั๊กอิน BepInEx/MelonLoader/UE4SS
     - ใช้ MinHook ดักจับฟังก์ชัน `DrawText`, `TextRenderer::Render`, หรือ `GetLocalizedString` แล้วสลับข้อความเป็นภาษาไทยในหน่วยความจำสด

---

### Phase 3: การทดสอบและปรับจูนวนซ้ำจนกว่าจะสำเร็จ (Relentless Iterative Validation)

```
        ┌────────────────────────────────────────────────────────┐
        │ 1. Micro-Test Harness: สกัดและแพ็คเฉพาะ 1 ไฟล์ตัวอย่าง │
        └───────────────────────────┬────────────────────────────┘
                                    │
                                    ▼
        ┌────────────────────────────────────────────────────────┐
        │ 2. Roundtrip Zero-Diff Test:                          │
        │    สกัดข้อความ → แพ็คกลับโดยไม่แก้ → ทำ Binary Diff     │
        │    (ถ้าไฟล์ตรงกับต้นฉบับ 100% แปลว่า Repacker ถูกต้อง)   │
        └───────────────────────────┬────────────────────────────┘
                                    │
                                    ▼
        ┌────────────────────────────────────────────────────────┐
        │ 3. Thai String Injection & In-game Test:               │
        │    ใส่ข้อความไทย "ทดสอบ" → แพ็คเข้าเกม → เปิดเกมดูผล  │
        └───────────────────────────┬────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
                 เกมเปิดได้                      เกมแครช / จอดำ
        ┌───────────────────────────┐   ┌───────────────────────────┐
        │ ผ่านเข้าสู่ขั้นตอนถัดไป   │   │ อ่าน Crash Dump / Log     │
        │ ทำ Proof of Concept ต่อ   │   │ ปรับ Offset & Alignment   │
        └───────────────────────────┘   └─────────────┬─────────────┘
                                                      │
                                                      └─── (ปรับปรุงโค้ดและรันซ้ำ)
```

- **กฎความปลอดภัย**: ทุกการทดสอบต้องทำบนสำเนาไฟล์ หรือมีไฟล์ `.orig` สำรองไว้เสมอ
- **การวินิจฉัยแครช**: หากเกมปิดตัวเอง ให้ตรวจสอบ:
  - ขนาด Chunk Header ผิด หรือ Offset ชี้เลยจุดสิ้นสุดไฟล์ (Out of bounds)
  - String Length Prefix ขาดหรือเกิน ทำให้ Parser อ่านไบต์ถัดไปผิดตำแหน่ง
  - ลืมคำนวณ Checksum / Hash ท้ายไฟล์

---

### Phase 4: บันทึกเป็นองค์ความรู้ถาวร (Knowledge Codification)

เมื่อฝ่าทางตันสำเร็จและสามารถแพตช์เกมได้จริง:
1. นำสคริปต์หรือเครื่องมือเฉพาะกิจที่สร้างขึ้นไปเก็บไว้ใน:
   - โฟลเดอร์โปรเจกต์: `{Workspace}/05_Scripts_and_Tools/`
   - คลังเครื่องมือส่วนกลาง: `tools/flagship/GameBridges/{Engine}/`
2. สร้างเอกสารคู่มือทางเทคนิค (Knowledge Item / Bible) บันทึกโครงสร้างไบนารีและวิธีแก้ปัญหาลงใน:
   - `E:\Mod_Workspace\Modding-Knowledge\Engines\{Engine}\` หรือ `Techniques\`
3. เพิ่มรายการลงใน `MASTER_INDEX.md` และ `ENGINE_INDEX.md` ทันทีตาม Global Rules

---

## 4. ตารางเปรียบเทียบ: AI แบบเดิม vs AI โหมด Extreme Breakthrough

| สถานการณ์ | AI ทั่วไป / แบบเดิม | AI โหมด Extreme Breakthrough 🔥 |
| :--- | :--- | :--- |
| **ไม่พบ Tool สำเร็จรูป** | หยุดทำงาน แล้วบอกผู้ใช้ว่า "ไม่มีเครื่องมือรองรับเกมนี้" | ค้นหา Binary Header, วิเคราะห์โครงสร้าง แล้ว **เขียนสคริปต์แกะไฟล์ขึ้นมาเองทันที** |
| **ไฟล์ถูกบีบอัดด้วยอัลกอริทึมแปลก** | แจ้ง Error แล้วขอยกเลิกงาน | สแกนหา Magic Bytes / Signatures เชื่อมต่อ DLL บีบอัดผ่าน `ctypes` เพื่อคลายไฟล์ |
| **ฟอนต์ไทยสระลอย / เต้าหู้** | บอกให้ผู้ใช้ไปหาฟอนต์ใหม่มาใส่ | ใช้ `fontTools` ยกวรรณยุกต์ +160 units ปรับจูน TrueType composite tables หรือผ่าตัด Font Atlas เอง |
| **แก้ไฟล์ดิสก์แล้วเกมแครช (DRM)** | ยอมแพ้และระบุว่าเกมมีระบบป้องกัน | สลับยุทธวิธีเป็น **Runtime Memory Hooking** ผ่าน MinHook / Proxy DLL เพื่อแทรกแซงในแรม |
| **สคริปต์ที่เขียนรันแล้วพัง** | หยุดถามผู้ใช้ว่าจะให้ทำอย่างไรต่อ | อ่าน Stack Trace วิเคราะห์ Offset ที่คลาดเคลื่อน ปรับ Padding แล้ว **รันแก้ไขซ้ำจนกว่าจะผ่าน** |
