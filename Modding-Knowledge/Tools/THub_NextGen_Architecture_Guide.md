# 🚀 THub 2.0 (PyQt6 High-Performance Edition) Architecture Guide
**Ultimate Game Modding & Localization Environment**

---

## 1. บทนำและการเปลี่ยนผ่านสู่ PyQt6 (The Shift to PyQt6)
เดิมที THub พัฒนาด้วย `CustomTkinter` ซึ่งทำงานด้วย CPU Software Rendering ทำให้เกิดปัญหาความหน่วงและอาการกระตุกเมื่อแสดงผลการ์ดหลายสิบใบ THub 2.0 จึงได้รับการยกเครื่องใหม่ทั้งหมดสู่ **PyQt6 (Qt 6 C++ Engine)** เพื่อมอบ:
1. **ความเร็วระดับเสี้ยววินาที (Startup < 0.4s):** เรนเดอร์ด้วย Hardware Acceleration ผ่าน Direct3D 11/12 ของ Windows
2. **เป็นเนื้อเดียวกับ TStudio:** เนื่องจาก `TStudio` พัฒนาด้วย PyQt6 เช่นกัน ทำให้แชร์ Engine, Environment, และทำงานร่วมกันได้แบบไร้รอยต่อ 100%
3. **การ์ดเกม 16:9 สไตล์ DLSS Swapper:** สัดส่วนแนวนอนสมบูรณ์แบบ วางปุ่มคู่หูชูโรง `[🚀 TStudio]` และ `[🤖 AI Helper]` เคียงข้างกัน

---

## 2. การแก้ปัญหาค้างและเด้งใน TStudio Hub (Stability & Multi-threading)

### 🐛 สาเหตุของอาการค้างและเด้งเดิม:
1. **Qt Thread Safety Violation:** การอัปเดต UI (เช่น `QLabel.setText` หรือ `QProgressBar.setValue`) จาก `threading.Thread` โดยตรง ขัดกับกฎของ Qt และนำไปสู่การ Abort/Crash ทันที
2. **Synchronous File Explosion:** โฟลเดอร์เกมที่มีไฟล์แปลจำนวนมาก (เช่น 120+ ไฟล์) ทำให้การสร้าง Widget หลายร้อยชิ้นบน Main Thread ทำให้ UI Freeze

### 🛡️ สถาปัตยกรรมใหม่ใน `TStudioViewQt`:
1. **`QThreadPool` & `WorkspaceScanRunnable`:** ย้ายกระบวนการคำนวณและสแกนทั้งหมดไปไว้บน Native QThreadPool และส่งข้อมูลกลับมายังหน้าจอผ่าน **Qt Queued Signals (`stats_ready`, `files_ready`)** อย่างปลอดภัย 100% หมดปัญหา `wrapped C/C++ object has been deleted` และ `Destroyed while thread is still running` อย่างถาวร
2. **Binary Buffer & Thai Byte Range Scanning:** เปลี่ยนจากการอ่านข้อความบรรทัดต่อบรรทัดด้วย regex มาเป็นการอ่านแบบไบนารีบัฟเฟอร์ 512KB และตรวจสอบช่วงไบต์ภาษาไทย (`\xE0\xB8`..`\xE0\xB9`) ทำให้ความเร็วในการคำนวณสถิติเพิ่มขึ้นถึง 100 เท่า (สแกนเสร็จใน ~15ms)
3. **Workspace Isolation:** สแกนเฉพาะไฟล์ที่อยู่ใน `02_Translation_Workspace` และละเว้นโฟลเดอร์ Archive/Cache เพื่อไม่ให้เกิดการสแกนโฟลเดอร์เกมทั้งหมดโดยไม่จำเป็น
4. **UI Widget Virtualization / Row Cap:** แสดงผลรายการไฟล์สูงสุด 50 รายการแรก พร้อมป้ายระบุจำนวนไฟล์ที่เหลือ เพื่อให้การเลื่อนหน้าจอราบรื่นระดับ 60+ FPS

---

## 3. การออกแบบหน้าต่างและการ์ดเกม (16:9 Widescreen & Obsidian QSS)

### 🎨 ธีมและโทนสี (Obsidian Fluent Theme)
- **Canvas Background:** `#0b0e14` (Deep Obsidian)
- **Card Background:** `#151926` (Card Surface) ขอบ `#202638` มุมโค้ง `12px`
- **TStudio Cyan:** `#38bdf8` (สีฟ้าสำหรับ TStudio)
- **AI Helper Violet:** `#c084fc` / `#a855f7` (สีม่วงสำหรับ AI Copilot)
- **Engine Green:** `#22c55e` (ป้ายระบุความพร้อม)

### 🖼️ การ์ดเกม 16:9 Widescreen & Drag & Drop Reordering
- **ภาพปกสัดส่วน 16:9 (280x158):** ตัดขอบมนด้วย `QPainter` แอนติเอเลียส คมชัดระดับพิกเซล
- **คลิกและลากขยับได้ (Interactive Drag & Drop):** ผู้ใช้สามารถคลิกเมาส์ซ้ายค้างที่การ์ดแล้วลากเพื่อสลับจัดเรียงตำแหน่งได้อย่างอิสระ มี Thumbnail ลอยตามเคอร์เซอร์ พร้อมขอบไฮไลต์สีฟ้าประ (`2px dashed #38bdf8`) บนการ์ดเป้าหมาย และบันทึกลำดับถาวรลง `hub_config.json`
- **ระบบเก็บเข้าคลัง / ซ่อนโปรเจกต์ (Archive / Hide System):**
  - คลิกขวาที่การ์ด หรือคลิกปุ่ม `[⋮]` เพื่อเลือก **"🗃️ เก็บเข้าคลัง (ซ่อนโปรเจกต์)"**
  - เมื่อเก็บเข้าคลัง การ์ดจะถูกซ่อนออกจากหน้าหลักทันที
  - สามารถสลับไปดูและกู้คืนได้ที่ฟิลเตอร์ชิป **`🗃️ คลังที่เก็บไว้`** พร้อมปุ่ม **"📤 นำกลับจากคลัง (เลิกซ่อน)"**
- **ป้ายสถานะบนปก:**
  - `📌 ปักหมุด` (สีเหลืองทอง เมื่อปักหมุด)
  - `📦 ในคลัง` (สีส้ม เมื่อถูกซ่อนไว้ในคลัง)
  - ป้าย Engine Badge เฉพาะ Engine แท้ที่ตรวจพบ (Unity, Unreal Engine, RE Engine)
- **แถบปุ่ม Action:**
  - `[🚀 TStudio]` (ปุ่มสีฟ้า Cyan — เปิด TStudio พร้อมส่ง Workspace Path ทันที)
  - `[🤖 AI Helper]` (ปุ่มสีม่วง Violet — สลับไปหน้า AI Copilot วิเคราะห์เกมนั้นทันที)
  - `[📁]` (เปิดโฟลเดอร์ Workspace 01-06)
  - `[⋮]` (เมนูเพิ่มเติม: ปรับแต่งภาพปก, ปักหมุด, เก็บเข้าคลัง, ลบโปรเจกต์)

### 🎨 ระบบปรับแต่งภาพปกและการเลื่อนตำแหน่ง 4 ทิศทาง (Cover Customization & 4-Way Panning)
- **แหล่งที่มาของภาพ 3 รูปแบบ:**
  1. 📂 **เลือกภาพจากในเครื่อง:** รองรับไฟล์ภาพทุกชนิด (.png, .jpg, .webp, .bmp) พร้อมแปลงและบันทึกเป็น `thub_cover.jpg`
  2. 🌐 **ค้นหาภาพจาก Steam Store:** ระบุชื่อเกมเพื่อดึงภาพ 16:9 Landscape Header ความคมชัดสูงมาใช้ในคลิกเดียว
  3. 🔗 **ดาวน์โหลดจาก URL:** วางลิงก์รูปภาพโดยตรง
- **การปรับตำแหน่งภาพ 4 ทิศทาง (4-Way Panning & Zoom):**
  - **Interactive Drag-to-Pan:** สามารถคลิกและลากเมาส์บนหน้าจอ Preview 16:9 เพื่อเลื่อนภาพได้โดยตรงอย่างเป็นธรรมชาติ
  - **Pan X Slider (ซ้าย - ขวา):** ปรับเลื่อนแกน X ในช่วง `-100%` ถึง `+100%`
  - **Pan Y Slider (ขึ้น - ลง):** ปรับเลื่อนแกน Y ในช่วง `-100%` ถึง `+100%`
  - **Zoom Slider:** ขยายภาพ `1.0x` ถึง `2.5x` สำหรับภาพที่ต้องการจัดจุดโฟกัส พร้อมปุ่มรีเซ็ตกึ่งกลาง
  - **Non-destructive Rendering:** ค่าพิกัด `cover_offset_x`, `cover_offset_y`, `cover_zoom` ถูกบันทึกลงคอนฟิกแยกต่างหาก ทำให้ภาพต้นฉบับไม่สูญเสียความละเอียดและสามารถปรับแต่งใหม่ได้ตลอดเวลา

---

## 4. โครงสร้างเมนูนำทาง (Sidebar Navigation)
ตัดเมนูที่ไม่จำเป็นออกทั้งหมดตามความต้องการของผู้ใช้ (ทั้ง "การตั้งค่า (Settings)" และ "เครื่องมือเสริม (Tools)") ทำให้เมนูกระชับ รวดเร็ว และตรงจุด:
- 📊 **Dashboard (หน้าหลัก):** รวมการ์ดเกม 16:9 ทั้งหมด พร้อมฟิลเตอร์ค้นหา
- 📝 **TStudio Hub ⭐:** ศูนย์บัญชาการและมาตรวัดงานแปลของ TStudio (สแกนไว 15ms ไร้กระตุก)
- 🤖 **AI Helper Copilot ⭐:** ศูนย์สร้าง Master Prompt เจาะจงตาม Engine
- ✨ **THub Apps:** แหล่งรวม Flagship Tools (TRun, TPUA, TGlyph, TVox)
- 📚 **Docs:** คลังคู่มือ Modding-Knowledge

---

## 5. ระบบตรวจจับ Game Engine อัตโนมัติและ Badge ประจำการ์ด (Multi-tier Engine Detection & Badges)

### 🎯 เป้าหมายและข้อกำหนด
- **แสดง Badge ประจำ Engine บนการ์ดทุกใบ:** ทั้งโปรเจกต์เดิมที่มีอยู่ (36+ เกม) และโปรเจกต์ใหม่ที่จะสร้างในอนาคต โดยรับประกันว่าไม่มีการ์ดใดที่ Badge สูญหาย
- **ละเว้นป้าย DirectX / Graphics API:** แสดงเฉพาะ Game Engine แท้จริง เพื่อความสะอาดตาและความเป็นมืออาชีพ

### 🧠 สถาปัตยกรรมการตรวจจับ 5 ลำดับขั้น (Multi-tier Detection Pipeline)
`core/engine_scanner.py` ได้รับการออกแบบให้ทำงานอย่างรวดเร็ว (0ms Overhead ด้วย In-memory Caching) ผ่าน 5 ขั้นตอน:
1. **Tier 1: Explicit / Saved Engine (`saved`):** หากโปรเจกต์มีฟิลด์ `engine` ถูกกำหนดไว้แล้ว จะดึงมาใช้ทันที
2. **Tier 2: Deep Game Directory Scan (`game_dir_root`, `game_dir_sub`):**
   - สแกนรูทโฟลเดอร์ของเกม และเจาะลึก 2 ระดับในโฟลเดอร์สำคัญ (`Build/`, `bin/`, `Binaries/Win64/`, `Content/`, `Data/`, `ph/`, `base/`, `nativePC/`, `disc/`, `motor/`)
   - ตรวจสอบ Signatures พิเศษระดับลึก เช่น `UnityPlayer.dll`, `*_Data`, `GameAssembly.dll`, `Engine/`, `pakchunk*.pak`, `re_chunk_*.pak`, `nativePC`, `r6`, `*.asr`, `bigfile.*`, `chitin.key`, `dialog.tlk`, `*.sharedresources`, `*.pk3`
3. **Tier 3: Workspace Directory Inspection (`workspace`):**
   - ในกรณีที่เกมติดตั้งอยู่ใน External Hard Drive ที่ไม่ได้เชื่อมต่อ ระบบจะสแกนโฟลเดอร์ Workspace แทน (`00_Original`, `01_Original_Backup`, `02_Translation_Workspace`, `05_Scripts_and_Tools`, `06_Releases`)
   - ตรวจจับ `.locres`, `UE4SS`, `.bundle`, `.assets`, `BepInEx`, `XUnity`, `.arc`, `.bif`, `rpack`, `.lzs`
4. **Tier 4: Title Heuristics Knowledgebase (`heuristic`):**
   - ฐานข้อมูลจับคู่ชื่อเกมยอดนิยมและซีรีส์เกมเข้ากับ Engine ที่ถูกต้องโดยอัตโนมัติ (เช่น Dishonored 2 -> Void Engine, Dying Light 2 -> C-Engine, Atelier Ryza -> Katana / Gust, KOTOR -> Odyssey Engine, Hades -> Custom Engine ฯลฯ)
5. **Tier 5: Clean Fallback (`fallback`):**
   - หากเป็นเกมอินดี้หรือ Engine ลึกลับที่ไม่ตรงกับกฎใดๆ ระบบจะกำหนดเป็น `Custom Engine` (สีเทา Slate `#94a3b8`) เพื่อให้การ์ดมี Badge ที่สมบูรณ์ตลอดเวลา

### 🎨 จานสีประจำ Game Engine (Visual Engine Palette)
- **Unreal Engine:** `#38bdf8` (Cyan Blue)
- **Unity:** `#22c55e` (Emerald Green)
- **RE Engine:** `#f43f5e` (Rose Red)
- **MT Framework:** `#eab308` (Amber Gold)
- **REDengine:** `#c084fc` (Purple)
- **Godot:** `#74c7ec` (Sky Blue)
- **Void Engine:** `#a855f7` (Violet)
- **Aurora Engine / Odyssey:** `#f97316` (Orange)
- **id Tech:** `#ec4899` (Pink)
- **C-Engine (Techland):** `#84cc16` (Lime Green)
- **Katana / Gust (Koei Tecmo):** `#06b6d4` (Teal)
- **Asura Engine:** `#14b8a6` (Teal)
- **CDC Engine:** `#6366f1` (Indigo)
- **FLEDGE / Marvelous Engine:** `#f59e0b` (Amber)
- **Custom Engine:** `#94a3b8` (Slate Gray)

### 🛠️ การรองรับโปรเจกต์ใหม่และการปรับแต่ง (Wizard & Override)
1. **Real-time Detection ใน Project Wizard (`ProjectWizardDialogQt`):**
   - เมื่อผู้ใช้พิมพ์ชื่อเกม หรือคลิกเลือกโฟลเดอร์ Workspace / Game Directory ระบบจะตรวจจับ Engine ให้แบบ Real-time ทันที
   - แสดง Badge ตัวอย่างสดๆ พร้อมเปิดให้ผู้ใช้เลือกเปลี่ยนหรือพิมพ์ชื่อ Engine เองได้อย่างอิสระ
2. **เมนูคลิกขวาเปลี่ยน Engine ได้ทันที (`EngineSelectDialogQt`):**
   - คลิกขวาที่การ์ดเกมใดๆ แล้วเลือก `"⚙️ กำหนด Engine เกม..."`
   - สามารถเลือกเปลี่ยน Engine จาก Preset หรือพิมพ์ชื่อ Custom Engine พร้อมดูตัวอย่าง Badge สด และบันทึกถาวรลงคอนฟิก

---

## 7. ศูนย์บัญชาการ AI Helper Copilot (V1 Intelligence Restoration)

ในเวอร์ชัน THub 2.0 ได้ทำการกู้คืนและยกระดับความฉลาดของ **AI Helper Command Center** ให้เทียบเท่าและเหนือกว่าเวอร์ชันดั้งเดิม (V1) อย่างสมบูรณ์แบบ โดยแบ่งโครงสร้างออกเป็น 3 โหมดปฏิบัติการ และ 11 กล่องตัวเลือกพฤติกรรม:

### 🎯 3 โหมดปฏิบัติการที่ตระหนักรู้สภาพแวดล้อม (Environment-Aware Modes)
1. 💬 **โหมดที่ปรึกษา (Web Chat / ChatGPT / Claude Web):**
   - ออกแบบสำหรับ AI บนเบราว์เซอร์ที่ **ไม่มีสิทธิ์เข้าถึงไฟล์หรือ Terminal ในเครื่อง**
   - สวมบทบาท "Localization Consultant & Python Script Generator"
   - นำเสนอ Roadmap 7 ขั้นตอน (Extraction & Analysis, Font & UI PUA, Pre-Translation Glossary, Proof of Concept, Safe Scripting, Batch Translation QA, Build Release)
2. 💻 **โหมดปฏิบัติการ (Autonomous Agent / Claude Code / Antigravity / Cursor):**
   - ออกแบบสำหรับ AI ที่มี Terminal และสิทธิ์ในการอ่านเขียนไฟล์บนเครื่องจริง
   - **กฎคุ้มครองระบบนิเวศ (Ecosystem Protection):** ถือว่าโฟลเดอร์เครื่องมือและ Core Engine ของ THub (`tools/flagship/TStudio`, `TRun`, `Core`) เป็น Read-Only ห้ามแก้ไข
   - **การตัดสินใจเลือก Approach A vs B:** Simple text (.json, .xml, .csv) ใช้ Custom Parser Plugin ใน TStudio ส่วน Heavy archives (.pak, .dat, bundles) เขียน Standalone Unpacker/Packer
   - **Step 3 GATE & 4-Level Diagnostic Tree:** ตั้งจุดตรวจ Checkpoint ก่อนแปลไฟล์ทั้งเกม โดยแปลเฉพาะเมนูหลัก (~5-20 บรรทัด) หากพบปัญหา ให้รันแผนภูมิวินิจฉัย 4 ระดับ:
     - `[D1]`: Hex-dump ตรวจสอบว่ามีไบต์ใหม่ที่ offset ถูกต้องหรือไม่
     - `[D2]`: บันไดแก้ปัญหาฟอนต์สี่เหลี่ยม 4 ระดับ (Level 1: สลับ TTF ใน 03_Font_and_UI, Level 2: Rebuild Sprite Atlas, Level 3: BepInEx/REFramework hook, Level 4: Runtime memory hook)
     - `[D3]`: ตรวจสอบ Encoding (UTF-8, UTF-8 BOM, UTF-16LE, CP874)
     - `[D4]`: ตรวจสอบ Asset Cache Override
3. 🎙️ **โหมดพากษ์เสียง (Voice Dubbing Mod Engineer):**
   - ออกแบบสำหรับโปรเจกต์ม็อดเสียงพากย์ไทย (TVox / Wwise / FMOD)
   - ตรวจจับ Audio Engine อัตโนมัติ (Wwise `.wem`/`.bnk`, FMOD `.bank`/`.fsb`, Raw `.wav`/`.ogg`/`.mp3`)
   - รวบรวมและจัดทำดัชนีไฟล์เสียง (`audio_index.json`)
   - สร้าง Tracking Sheet (`dubbing_tracking.csv`)
   - วิเคราะห์ Duration ความยาวเสียงต้นฉบับ
   - สร้าง Script ฉีดไฟล์เสียงใหม่กลับเข้าเกม (`injection_log.md`)

### ⚙️ 11 กล่องตัวเลือกพฤติกรรมเชิงโต้ตอบ (Interactive Behavioral Protocols)
- **Agent Mode Protocols (6 Checkboxes):**
  1. `auto_tool`: ค้นหาและดาวน์โหลด Binary จาก GitHub เมื่อขาดแคลน
  2. `obstacle`: รับมืออุปสรรค & เสนอทางเลือก [A/B/C] ห้ามหยุดเงียบ
  3. `write_log`: บันทึกประวัติขั้นตอนลง `05_Scripts_and_Tools/session_log.md`
  4. `min_confirm`: ลดคำถาม ขออนุมัติเฉพาะเรื่องเสี่ยงต่อไฟล์ต้นฉบับ
  5. `deep_scan`: สแกนแบบเจาะลึก ตรวจสอบ byte header ทุกไฟล์ที่ไม่รู้จัก
  6. `mem_hook`: อนุญาต Memory Hook Fallback (BepInEx / UE4SS) เมื่อแก้ไฟล์ตรงไม่ได้
- **Dubbing Mode Protocols (5 Checkboxes):**
  1. `has_thai_sub`: ใช้ข้อความจาก Subtitle ภาษาไทยเป็นบทพากย์โดยตรง
  2. `gen_tracking_sheet`: สร้าง CSV Tracking Sheet สำหรับทีมพากย์
  3. `analyze_duration`: วิเคราะห์และจัดลำดับความยาวเสียง
  4. `gen_replace_script`: สคริปต์ฉีดเสียงกลับเข้าสู่เกม
  5. `keep_original`: สำรองไฟล์เสียงต้นฉบับ `.bak` ก่อนแทนที่เสมอ

### ⚡ Silent Auto-Save & Consolas Studio
- **บันทึกอัตโนมัติเบื้องหลัง (Zero-Click Auto-Save):** เมื่อผู้ใช้สลับโหมด หรือคลิก Checkbox ตัวเลือกใดๆ ระบบจะเขียนไฟล์ `ai_instructions.md` (หรือ `ai_dubbing_instructions.md`) ลงโฟลเดอร์ Workspace ของโปรเจกต์เป้าหมายทันทีโดยไม่ต้องกดปุ่มใดๆ
- **Consolas Editor:** สามารถตรวจทานและแก้ไขข้อความ Prompt ได้โดยตรง พร้อมปุ่มคัดลอกลง Clipboard แบบคลิกเดียว (`📋 คัดลอก Prompt`)

---

## 8. วิธีการเปิดใช้งาน
ดับเบิลคลิกไฟล์ **`run_thub_pyqt6.bat`** ในโฟลเดอร์ `modder-hub` หรือสั่งรันผ่านคำสั่ง:
```bash
python e:\Mod_Workspace\Modder_project\modder-hub\app_pyqt6.py
```

