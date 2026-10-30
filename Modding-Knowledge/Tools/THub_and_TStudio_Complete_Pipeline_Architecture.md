# 🗺️ THub & TStudio 2.0: Complete Pipeline Architecture

เอกสารผังโครงสร้างสถาปัตยกรรมและไปป์ไลน์การทำงานทั้งหมดของ **THub Ecosystem** และ **TStudio 2.0** ตั้งแต่ขั้นตอนการสกัดไฟล์เกม (Extraction) จนถึงการ Deploy ม็อดเข้าตัวเกมจริง (Final Deployment)

---

## 📊 ผังภาพไปป์ไลน์การทำงานแบบองค์รวม (End-to-End Master Pipeline)

```mermaid
flowchart TD
    %% Styling Definitions
    classDef raw fill:#313244,stroke:#6c7086,stroke-width:2px,color:#cdd6f4;
    classDef thub fill:#1e1e2e,stroke:#89b4fa,stroke-width:3px,color:#89b4fa,font-weight:bold;
    classDef analysis fill:#181825,stroke:#f9e2af,stroke-width:2px,color:#f9e2af;
    classDef trans fill:#181825,stroke:#a6e3a1,stroke-width:2px,color:#a6e3a1;
    classDef qa fill:#181825,stroke:#fab387,stroke-width:2px,color:#fab387;
    classDef media fill:#181825,stroke:#cba6f7,stroke-width:2px,color:#cba6f7;
    classDef deploy fill:#181825,stroke:#f38ba8,stroke-width:3px,color:#f38ba8,font-weight:bold;

    %% STAGE 1: INGESTION
    subgraph S1 ["ขั้นที่ 1: การสกัดและนำเข้าไฟล์เกม (Extraction & Ingestion)"]
        GameFiles["🎮 ไฟล์เกมต้นฉบับ (PAK / Bundle / Locres / LandB / JSON / CSV)"]:::raw
        ExtractTools["🛠️ Modder Tool Library (FModel / QuickBMS / AssetStudio / UTMT)"]:::raw
        GameFiles --> ExtractTools
    end

    %% STAGE 2: THUB WORKSPACE & PROFILES
    subgraph S2 ["ขั้นที่ 2: ศูนย์บัญชาการ THub (Unified Workspace & Profile Sync)"]
        THubCore["🚀 THub Launcher & Engine Host"]:::thub
        ProfileSync["🔄 Linked Profiles (API Keys / Shared Glossary / Prompts)"]:::thub
        Workspace["📁 6-Folder Workspace Architecture
        (01_Backup | 02_Workspace | 03_Font_UI | 04_Packed | 05_Tools | 06_Releases)"]:::thub
        
        ExtractTools -->|"นำเข้าไฟล์ดิบ"| Workspace
        THubCore --> ProfileSync
        THubCore --> Workspace
    end

    %% STAGE 3: INTELLIGENCE & LORE
    subgraph S3 ["ขั้นที่ 3: วิเคราะห์ข้อมูลเชิงลึกและล็อกจักรวาล (Intelligence & Lore)"]
        Analyzer["🔍 Whole-File Deep Analyzer (6-Dimension Matrix)
        - Cast Discovery (แยกบทพูดตัวละคร)
        - Quests Dossier & Asset Bundles
        - Auto Entity & Glossary Miner
        - Tag Integrity Auditor"]:::analysis
        
        TLM["🧠 TLM Studio 2.0 (Translation Lore Master)
        - Universe Tone Matrix (Sci-Fi, Cyberpunk, 40k, Medieval, etc.)
        - Directive Matrix (คุมสรรพนามและกฎการแปล)
        - Staging Grid & Color-Coded Tags"]:::analysis

        Workspace -->|"โหลดไฟล์แปล"| Analyzer
        Analyzer -->|"สกัดศัพท์ & บทพูด"| TLM
        ProfileSync -.->|"ฉีดกฎกลาง"| TLM
    end

    %% STAGE 4: TRANSLATION ENGINES
    subgraph S4 ["ขั้นที่ 4: การประมวลผลการแปลด้วย AI (Core Translation Engines)"]
        direction TB
        
        AI_Providers["🌐 Multi-AI Engine Selector
        (Cloud: Gemini 2.0, DeepSeek V3/R1, Claude 3.7, GPT-4o
        Local: LM Studio / Ollama Qwen 2.5)"]:::trans

        subgraph PathA ["ทางเลือกที่ 1: TStudio 2.0 (เน้นคุณภาพ & จัดการรายบรรทัด)"]
            TStudio["📝 TStudio 2.0 Editor
            - Side-by-Side Table (Source / Target / AI Ref)
            - 3-Option Translation (ตรงตัว / พูด / ทางการ)
            - Special Modes (Poem / Quote / Idiom)"]:::trans
            
            PatchFeature["🩹 In-Line English Patch (Ctrl+Shift+E)
            - ตรวจจับคำอังกฤษหลุด
            - ซ่อมเฉพาะจุดโดยคงประโยคไทยเดิม
            - Smart Skip แถวที่แปลครบแล้ว"]:::trans
            
            Snippet["✂️ Snippet Transliteration (ทับศัพท์เฉพาะคำไฮไลท์)"]:::trans
            
            TStudio --> PatchFeature
            TStudio --> Snippet
        end

        subgraph PathB ["ทางเลือกที่ 2: TRun (เน้นความเร็ว & แปลแบบ Batch อัตโนมัติ)"]
            TRun["⚡ TRun Batch Engine
            - Background Multi-threaded Queue
            - Smart Cache (ลดค่า Token 90%)
            - Smart Routing (Off-Peak / Local LLM Switch)
            - Auto Resume เมื่อถูกขัดจังหวะ"]:::trans
        end

        TLM -->|"แนบ Prompt & Tone"| TStudio
        TLM -->|"แนบ Prompt & Cache"| TRun
        AI_Providers <-->|"API Call / Stream"| TStudio
        AI_Providers <-->|"API Call / Stream"| TRun
    end

    %% STAGE 5: QA & SAFETY
    subgraph S5 ["ขั้นที่ 5: การควบคุมคุณภาพและความปลอดภัยของไฟล์เกม (QA & Crash Guard)"]
        QA_Engine["🛡️ Zero-Crash Safety Guard
        - Tag & Variable Protection (%s, {0}, <color>)
        - Auto Thai Digit Converter (๑-๙ เป็น 1-9 กันเกมเด้ง)
        - Hallucination & Leak Detector
        - UTF-8 BOM / Encoding Validation"]:::qa
        
        TStudio --> QA_Engine
        TRun --> QA_Engine
    end

    %% STAGE 6: TYPOGRAPHY, FONT & AUDIO
    subgraph S6 ["ขั้นที่ 6: จัดการฟอนต์ สระลอย และสื่อมัลติมีเดีย (Font & Audio Studio)"]
        TPUA["🔤 TPUA (PUA Font Manager)
        - Thai Vowel De-floating (แก้สระลอย/จม)
        - Auto Y-Raise & Smart Bounds
        - Visual Font Tuner"]:::media

        TGlyph["🎨 TGlyph (Font Texture Generator)
        - Pixel-Perfect Font Atlas (.DDS / .PNG)
        - UV Coordinates Mapping (Unreal / Unity)"]:::media

        TVox["🎬 TVox (FMV & Cutscene Studio)
        - Video Player & FFmpeg Waveform
        - Whisper Subtitle Extraction
        - AI Voice Dubbing (พากย์เสียงทับวิดีโอ)"]:::media

        QA_Engine -->|"ส่งข้อความแปล"| TPUA
        TPUA -->|"ส่งพิกัดรหัส PUA"| TGlyph
        QA_Engine -.->|"ข้อความซับไตเติล"| TVox
    end

    %% STAGE 7: DEPLOYMENT & RELEASE
    subgraph S7 ["ขั้นที่ 7: การประกอบไฟล์ม็อดและส่งเข้าเกม (Packing & Deployment)"]
        FormatConv["🔄 Universal TFormat Converter
        (แปลงกลับเป็น JSON / CSV / Locres / LandB / Asset)"]:::deploy

        Deploy1Click["🚀 1-Click Deploy to Game
        (ยิงไฟล์ม็อดลง 04_Packed_Mod และโฟลเดอร์เกมทันที)"]:::deploy

        ReleaseBuild["📦 Release Packaging
        (ส่งออกเป็นไฟล์ Zip/Rar ลง 06_Releases พร้อมแจกจ่าย)"]:::deploy

        QA_Engine --> FormatConv
        TGlyph --> FormatConv
        TVox --> FormatConv
        FormatConv --> Deploy1Click
        Deploy1Click --> ReleaseBuild
    end
```

---

## 🔄 เจาะลึกกระบวนการทำงานในแต่ละสเต็ป (Step-by-Step Data Flow)

### 1️⃣ การสกัดไฟล์ (Asset Ingestion)
- นักม็อดใช้ชุดเครื่องมือแกะไฟล์ใน **Modder Tool Library** ที่ฝังอยู่ใน THub (เช่น FModel สำหรับ Unreal Engine, AssetStudio สำหรับ Unity หรือ UTMT สำหรับ GameMaker) เพื่อดึงข้อความดิบออกมา
- ไฟล์ดิบจะถูกจัดเก็บเข้า `01_Original_Backup/` เพื่อความปลอดภัย ไม่ให้มีข้อมูลสูญหาย

### 2️⃣ ตั้งค่าและเชื่อมต่อผ่าน THub (Workspace & Profile Sync)
- เมื่อสร้างโปรเจกต์ใน THub ระบบจะจำลองโครงสร้างโฟลเดอร์ทำงาน 6 โฟลเดอร์มาตรฐาน
- ค่า API Key (Google, DeepSeek, Claude, OpenAI), พจนานุกรมคำศัพท์ (Glossary) และ Prompt สากล จะถูกแชร์ให้กับทุกเครื่องมือใน Suite โดยอัตโนมัติ

### 3️⃣ วิเคราะห์เนื้อหาและวางกลยุทธ์ (Deep Intelligence & Lore Staging)
- **Whole-File Deep Analyzer**: สแกนหาความสัมพันธ์ของบทสนทนา, นับบรรทัดของตัวละครแต่ละตัว (Dramatis Personae), แยกเควสต์ และดึงชื่อเฉพาะออกมาเป็นคลังศัพท์อัตโนมัติ
- **TLM Studio 2.0**: ล็อก "จักรวาลของเกม" (Universe Tone) เพื่อกำหนดสรรพนาม โทนเสียง และคำสั่ง Directive Matrix ให้ AI ปฏิบัติตามอย่างเคร่งครัด

### 4️⃣ ดำเนินการแปลด้วย AI (Dual Translation Paths)
- **เส้นทาง TStudio 2.0 (เน้นคุณภาพงานแปล)**:
  - เหมาะสำหรับแปลเนื้อเรื่องหลักและบทสนทนาสำคัญ
  - สามารถเลือกแปล 3 รูปแบบพร้อมกัน หรือใช้โหมดแปลบทกวี/สำนวน
  - **ฟีเจอร์เด็ด 🩹 In-Line English Patch (`Ctrl+Shift+E`)**: ซ่อมแซมเฉพาะคำภาษาอังกฤษที่หลุดออกมา โดยไม่ลบโครงสร้างประโยคไทยเดิมที่ขัดเกลาไว้
- **เส้นทาง TRun (เน้นความเร็วและคิวงานขนาดใหญ่)**:
  - เหมาะสำหรับไฟล์เมนู, รายการไอเทม, หรือสคริปต์ขนาดหมื่นบรรทัด
  - ทำงานอัตโนมัติเบื้องหลัง พร้อมระบบ Smart Cache ลดต้นทุนโทเค็นลงถึง 90%

### 5️⃣ ตรวจสอบความปลอดภัยและคุณภาพ (Zero-Crash QA Guard)
- **Tag Protection**: ตรวจสอบและป้องกันตัวแปรของเกมไม่ให้เสียหาย เช่น `%s`, `{0}`, `<color=red>`, `\n`
- **Auto Thai Digit Converter**: สแกนและแปลงเลขไทย (๑-๙) ให้กลับเป็นเลขอารบิก (1-9) โดยอัตโนมัติ ป้องกันไม่ให้เอนจิ้นเกม Crash
- **Encoding Check**: ตรวจสอบการเข้ารหัส UTF-8 และ BOM ให้เข้ากับระบบไฟล์ของเกม

### 6️⃣ แก้สระลอยและจัดการมัลติมีเดีย (Typography & Audio Studio)
- **TPUA**: นำข้อความที่ผ่านการแปลแล้วมาจัดเรียงรหัสตัวอักษรใหม่อยู่ในย่าน PUA (Private Use Area) เพื่อแก้ปัญหาสระลอย/สระจม
- **TGlyph**: เรนเดอร์ฟอนต์เป็น Texture Atlas (.DDS, .PNG) พร้อมสร้างตารางพิกัด UV ไปใส่ในเอนจิ้นเกม
- **TVox**: สำหรับเกมที่มีคัทซีนวิดีโอ (FMV) สามารถเล่นพรีวิวซับไตเติลแบบเรียลไทม์ พร้อมระบบ AI ถอดเสียงและพากย์เสียงภาษาไทยทับวิดีโอเดิม

### 7️⃣ ประกอบไฟล์และติดตั้งลงเกม (Packaging & 1-Click Deploy)
- **TFormat Engine**: แปลงไฟล์คำแปลกลับไปเป็นฟอร์แมตดั้งเดิมของตัวเกม
- **1-Click Deploy**: คัดลอกและจัดเรียงไฟล์เข้าสู่โฟลเดอร์เกมจริงเพื่อทดสอบการเล่นได้ทันที
- **Release Packaging**: บีบอัดไฟล์ม็อดสำเร็จรูปลงใน `06_Releases/` พร้อมสร้างเอกสาร Readme สำหรับนำไปแจกจ่ายให้ผู้เล่น

---

## 💡 สรุปจุดเด่นของสถาปัตยกรรม (Architectural Highlights)

| ด้าน | จุดเด่น | ผลลัพธ์ที่ได้ |
| :--- | :--- | :--- |
| **ความลื่นไหลของระบบ (Performance)** | สถาปัตยกรรม Asynchronous Multi-threading (PyQt6) | หน้าต่างโปรแกรมไม่ค้าง แม้ AI กำลังสตรีมข้อมูลหรือแปลไฟล์เป็นหมื่นบรรทัด |
| **การประหยัดทรัพยากร (Cost Efficiency)** | Translation Memory & Smart Cache (Exact & Fuzzy Match) | ประหยัดค่าบริการ AI API สูงถึง 90% เมื่อเทียบกับการแปลแบบดั้งเดิม |
| **ความแม่นยำของงานแปล (Quality & Tone)** | TLM Lore Master + Contextual In-Line Patching | คุมสรรพนามตรงตามจักรวาลเกม ซ่อมคำหลุดได้โดยไม่ทำลายสำนวนเดิม |
| **ความปลอดภัยของตัวเกม (Stability)** | Tag Guard + Thai Digit Converter + Encoding Validator | ม็อดไม่ทำให้เกมหลุด (Crash-Free) และแสดงผลได้อย่างสมบูรณ์แบบ |
