# TLM Studio 2.0: Game Lore, Variable Protection & Unified Prompt Engineering Guide

## 1. บทนำ (Overview)
**TLM Studio 2.0 (Terminology Language Model Studio)** คือสตูดิโอบัญญัติคำศัพท์และบริหารจัดการ AI Prompt อัจฉริยะสำหรับนักม็อดเกม ออกแบบมาเพื่อแก้ปัญหาคอขวดของการแปลเกมด้วย AI:
1. **AI แปลมั่วหรือแปลตรงตัวเกินไป** ขาดความเข้าใจในบริบทและจักรวาลของเกม (Lore & Universe Tone)
2. **ตัวแปรและแท็กโค้ดในเกมเสียหาย** เช่น `{0}`, `{player_name}`, `[ITEM_ID]`, `<color=...>`, `%s`, `\n` ถูก AI แปลทับหรือเปลี่ยนรูปจนเกมแครช
3. **ปัญหาคำศัพท์จีน/ต่างชาติหลุดรอด (Foreign/CJK Leak)** โดยเฉพาะเกมจีน/เกาหลีที่แปลเป็นอังกฤษแล้วแปลไทยต่อ หรือข้อความที่มีอักษร CJK หลงเหลือ
4. **การขาดการแยกแยะชื่อเฉพาะ (Proper Nouns)** ทำให้คำอย่าง "Bolter" กลายเป็น "ปืนสลักเกลียว" แทนที่จะเป็น "โบลต์เตอร์"
5. **ความซ้ำซ้อนของการตั้งค่าคำสั่ง AI** ระหว่างหน้าต่าง Prompt Settings เดิม และหน้าต่างสกัดคำศัพท์ TLM โดยทำการรวมระบบทั้งหมดเป็น **Unified Studio** หนึ่งเดียว

---

## 2. โครงสร้าง 3 แท็บของ Unified TLM Studio

### 🧭 Tab 1: บริบทและทิศทางการสกัด (Lore & Directives)
- **คลังจักรวาลและโทนเกม 37+ หมวดหมู่ (Universe Tones)**: ครอบคลุม Fantasy, Cyberpunk, Sci-Fi, Grimdark Warhammer 40k, Wuxia, Samurai, Post-Apoc, Tactical Military, Satirical Ultra-Militarism
- **สเกาท์เนื้อเรื่อง (AI Lore Scout)**: กดปุ่ม `🤖 AI สรุปเนื้อเรื่องอัตโนมัติ` ให้ AI สรุปฉากหลัง ธีม ฝ่าย และโทนเกมตามชื่อโปรไฟล์
- **สแกนเนอร์คุ้มครองตัวแปรจาก CSV (`🛡️ สแกนตัวแปรจาก CSV`)**: ตรวจจับรูปแบบตัวแปรทุกตระกูล (`{...}`, `[...]`, `<color>`, `%s`, `\n`) สร้างกฎคุ้มครองแบบเหล็กไหล
- **กฎแปลไทยบริสุทธิ์ ไร้จีน (`🇹🇭 แปลไทย 100% ไร้จีน`)**: บังคับผลลัพธ์ไทย 100% แบนอักษร CJK `[\u4e00-\u9fff]`
- **ถอดเสียงคำเฉพาะ (`💎 วิเคราะห์คำเฉพาะ`)**: สั่งทับศัพท์ชื่อเฉพาะ (เช่น `Bolter` -> `โบลต์เตอร์`)
- **🪄 ปุ่มคอมไพล์เข้า AI Prompts**: ประกอบ Lore + Tone + Rules ทั้งหมดแล้วส่งเข้าแท็บ 2 พร้อมสลับหน้าจอทันที

### ⚙️ Tab 2: สตูดิโอ AI Prompt & ทดสอบสด (AI Prompt Studio & Live Tester)
- **ตัวแก้ไข Prompt 3 ระดับ**:
  - `1. Single Translation Prompt (TStudio)`: แปลเดี่ยว พร้อมปุ่มแทรก `{source_text}` และ `{id}`
  - `2. Three Options Prompt (TStudio)`: แปล 3 ทางเลือกในรูปแบบ JSON Array
  - `3. Batch Translation Prompt (TRun)`: แปลชุดความเร็วสูง
- **🪄 ประกอบ Prompt อัตโนมัติ (Auto-Synthesize)**: ดึงเนื้อหาจากแท็บ 1 มาเรียบเรียงใหม่อย่างชาญฉลาด
- **📚 โหลดแม่แบบ (Templates)**: Default Base, Story & Dialogue, UI & Menus, Strict Direct
- **✅ การตั้งค่า QA Checker**: จำกัดขนาดไบต์ภาษาไทย (Max Byte Limit เช่น 21/63 ไบต์) ป้องกันฟอนต์ล้นบัฟเฟอร์และเกมแครช
- **🧪 Live Prompt Tester**: ช่องใส่ข้อความทดสอบ + ปุ่มกดทดสอบผ่าน AI จริงแบบเรียลไทม์
- **💾 บันทึก Prompt เข้าโปรไฟล์**: บันทึกคำสั่งทั้งหมดลงโปรไฟล์เกมที่เลือก

### 📋 Tab 3: ตะกร้าตรวจสอบคำศัพท์ (Staging Review & Import Grid)
- ตารางรีวิวคำศัพท์ที่ AI สกัดได้ (English, Thai, Tag, Context, Alt)
- กรองคำศัพท์ตามหมวดหมู่และคำค้นหา
- ดับเบิลคลิกแก้ไขคำแปลและสลับคำแปลหลัก-สำรอง (Alt <-> Thai)
- ปุ่มรวมคำศัพท์เข้าสู่คลังโปรไฟล์ (`Merge into Profile` / `Overwrite`)

---

## 3. สถาปัตยกรรมโค้ดและการเชื่อมต่อ (Implementation Architecture)

```
tstudio_tlm_studio.py
├── UNIVERSE_TONES (37 categories dictionary & prompt descriptors)
├── TLMStudioDialog (QDialog)
│   ├── Tab 0: Lore & Directives
│   │   ├── Lore Toolbar: AI Scout, Import, Export, Clear
│   │   ├── Universe Tone Selector (cbo_universe_tone)
│   │   ├── Rule Toolbar: CSV Vars, No-CJK, Proper Noun, Hybrid, Clear
│   │   ├── Action: Start Deep AI Mining -> Switch to Tab 2
│   │   └── Action: Compile to Prompts -> Switch to Tab 1
│   ├── Tab 1: AI Prompt Studio & Live Tester
│   │   ├── Top Toolbar: Auto-Synthesize, Load Templates, Save Prompts
│   │   ├── Single Prompt Editor (txt_p_single)
│   │   ├── Options Prompt Editor (txt_p_opt)
│   │   ├── Batch Prompt Editor (txt_p_batch)
│   │   ├── QA Byte Limit (spin_qa_bytes)
│   │   └── Live Tester (txt_test_input, btn_test_single, btn_test_opt, txt_test_result)
│   └── Tab 2: Staging Review Import Grid
│       ├── Search filter & Category filters
│       ├── Staging table (tbl_staging)
│       └── Merge to Profile Glossary (btn_merge_glossary)

tstudio_ui_shared.py
└── PromptSettingsDialog (Wrapper pointing to TLMStudioDialog with initial_tab=1)

tstudio_app.py
├── Column 2 Glossary Header: Single '✨ TLM Studio' button
├── Profile Menu: '✨ TLM Studio & ตั้งค่า AI Prompt...' (opens initial_tab=1)
├── Menubar Tools: Ctrl+P -> open_prompt_settings(initial_tab=1), Ctrl+L -> open_tlm_studio(initial_tab=0)
└── open_prompt_settings -> delegates to open_tlm_studio(initial_tab=1)
```
