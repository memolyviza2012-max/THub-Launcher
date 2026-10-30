# 🧠 TLM Studio: Translation Lore & Memory Engineering Guide
**ระบบคลังบริบทจักรวาล วิศวกรรมศัพท์เฉพาะ และแม่แบบพร้อมต์อัจฉริยะ สำหรับม็อดแปลภาษาไทย**

**ผู้พัฒนา:** [หน๊ด หนวด translator](https://www.facebook.com/NodNuatTranslator/) (Official Facebook Fanpage)  
**แพลตฟอร์ม:** TStudio Web (Community Crowdsourced Localization Platform)  
**ตำแหน่งในระบบ:** `E:\Mod_Workspace\Modding-Knowledge\Tools\TLM_Studio_Terminology_Engineering_Guide.md`

---

## 🌟 1. บทนำและวัตถุประสงค์ (Overview & Philosophy)

ในการแปลเกมขนาดใหญ่ที่มีเนื้อเรื่องลึกซึ้ง (Lore-Heavy RPGs, Dark Fantasy, Sci-Fi) ปัญหาที่พบบ่อยที่สุดของระบบ Crowdsourcing และ AI ทั่วไปคือ:
1. **สำนวนแตกแยก (Tone Drift)**: นักแปลแต่ละคนหรือ AI แต่ละรอบใช้สรรพนามและน้ำเสียงไม่ตรงกัน เช่น พระเอกพูด "ข้า-เจ้า" ในฉากหนึ่ง แต่อีกฉากกลายเป็น "ฉัน-นาย"
2. **ศัพท์เฉพาะหลุด (Terminology Inconsistency)**: ชื่อมอนสเตอร์ สถานที่ หรือไอเทมถูกแปลคนละคำกันในแต่ละไฟล์
3. **แท็กคำสั่งเกมพัง & ตัวอักษรเกินขนาด (Tag Loss & Byte Overflow)**: สตริงภาษาไทยมีความยาวเกินขีดจำกัดหน่วยความจำของเอนจินเกม (Byte Limit) จนตัวหนังสือทะลักกรอบ UI
4. **ความไม่ต่อเนื่องระหว่างไฟล์ (Context Isolation)**: AI ทั่วไปมองเห็นเฉพาะข้อความบรรทัดเดียว ไม่รับรู้กฎจักรวาลของเกม

**TLM Studio (Translation Lore & Memory)** ถูกพัฒนาขึ้นเพื่อแก้ปัญหาเหล่านี้อย่างเบ็ดเสร็จ โดยทำหน้าที่เป็น **"มันสมองกลาง (Central Brain)"** ที่หลอมรวม **จักรวาลเกม (Lore), กฎศัพท์เฉพาะ (Glossary), ขีดจำกัดทางเทคนิคของเกม (Tech Limits)** และ **แม่แบบคำสั่ง AI (Custom Prompts)** เข้าด้วยกัน

---

## 🏛️ 2. สถาปัตยกรรม 4 เสาหลักของ TLM Studio (The 4 Pillars)

```mermaid
graph TD
    subgraph TLM_Studio["🧠 TLM Studio"]
        Tab0["🧭 1. Lore & Universe Tone<br/>โทนจักรวาล, ปรัชญา, วิกิเกม"]
        Tab1["⛏️ 2. AI Deep Mining<br/>สกัดศัพท์อัตโนมัติจากสตริงเกม"]
        Tab2["📊 3. Staging Grid<br/>คัดกรอง, จัดหมวด, โหวตสำนวนทางเลือก"]
        Tab3["🧪 4. Prompt Studio<br/>ออกแบบพร้อมต์, คุมขนาดไบต์, ทดสอบสด"]
    end

    Tab0 --> AI_Engine["🤖 AI Translation Services<br/>(Quick Translate / TRun / 3-Tone)"]
    Tab1 --> Tab2
    Tab2 --> Glossary["📚 Project Glossary<br/>(Official Master & Alternatives)"]
    Tab3 --> AI_Engine
    Tab3 --> QA_Linter["🛡️ TagGuard & Byte Linter<br/>(Real-time Warnings)"]
```

---

## 🧭 เสาหลักที่ 1: Lore & Universe Tone (บริบทและทิศทางจักรวาล)

- **Universe Tone Presets**: เลือกโทนบรรยากาศของเกมได้ทันที เช่น:
  - *Dark Medieval Fantasy* (สำนวนโบราณ เคร่งขรึม สรรพนาม ข้า-เจ้า)
  - *Grimdark Dystopian Cyberpunk* (ดิบ หยาบคาย สรรพนาม มึง-กู สแลงสตรีท)
  - *High Fantasy Epic* (สละสลวย ทางการ ราชาศัพท์)
  - *Modern Casual / Comedy* (เป็นกันเอง สบายๆ ยุคปัจจุบัน)
- **Directives & Philosophy**: ระบุหลักการแปล เช่น *"คงชื่อเฉพาะของบอสเป็นภาษาอังกฤษตามต้นฉบับ"*, *"เว้นช่องไฟหน้าคำอุทาน"*, *"ห้ามแปลทับศัพท์คำว่า Rune ให้ใช้ รูน"*
- **Lore Scout & Web Wiki Fetcher**:
  - ดึงข้อมูล Lore จาก URL วิกิของเกม (เช่น Fandom Wiki, Wikipedia) โดยมีระบบ **Automatic URL Normalization** (`https://`) และ **CORS Proxy Fallback** (AllOrigins) ป้องกันปัญหาเบราว์เซอร์บล็อก Cross-Origin
  - AI Scout วิเคราะห์สรุปประเด็นจักรวาลให้อัตโนมัติด้วย Token Cap 4,096 tokens

---

## ⛏️ เสาหลักที่ 2: AI Deep Mining (การขุดสกัดศัพท์อัจฉริยะ)

- **Targeted Category Extraction**: สกัดคำศัพท์ได้ 5 หมวดหมู่หลัก:
  1. 👤 Character & NPC Names (ชื่อตัวละครและตำแหน่ง)
  2. 🗺️ Locations & Realms (สถานที่ อาณาจักร ดันเจียน)
  3. ⚔️ Items, Skills & Spells (ไอเทม ทักษะ เวทมนตร์ อาวุธ)
  4. 📜 Lore & Artifact Concepts (แนวคิดจักรวาล วัตถุโบราณ)
  5. 🖥️ UI & Game Mechanics (คำศัพท์ระบบและเมนู)
- **High-Capacity Mining Engine**:
  - ยกระดับเพดาน Token ของ LLM ขึ้นเป็น **6,000 Tokens** รองรับการสกัดคำศัพท์คราวละ 25–50 คำ พร้อมคำอธิบายและคำแปลทางเลือก
- **Resilient Truncation Recovery**:
  - กรณีที่ข้อความยาวจัดจน AI หยุดส่งกลางคัน ระบบมีตัวกู้คืน JSON Array แบบ Partial อัตโนมัติ (`recoverPartialJsonArray`) เพื่อสกัดคำศัพท์คู่ที่สมบูรณ์ออกมาใช้งานได้ทันทีโดยไม่เกิด Runtime Crash
  - มี Regex Fallback Extractor ตรวจจับแพทเทิร์น `{ "source": "...", "target": "..." }` แม้ JSON จะปิดแท็กไม่สมบูรณ์

---

## 📊 เสาหลักที่ 3: Staging Grid & Glossary Term Management (ตะแกรงคัดกรอง)

- **Safety Quarantine**: คำศัพท์ที่สกัดได้จะไม่ถูกยัดเข้าพจนานุกรมจริงทันที แต่จะเข้าสู่ **Staging Grid** เพื่อให้ Host หรือ Lead Review ก่อน
- **Granular Selection**: มีช่องติ๊กเลือกคำศัพท์ทีละคำ หรือเลือกทั้งหมด
- **Alternative Translations Preservation**:
  - เมื่อนำเข้าคำศัพท์จาก Staging ระบบจะเก็บคำแปลทางเลือก (`alternatives`) ไว้ด้วยเสมอ ทำให้นักแปลในทีมสามารถเข้ามาร่วมโหวตเลือกสำนวนที่ดีที่สุดได้ภายหลัง
- **Smart Primary Key Merging**:
  - เมื่อกดผสานเข้าพจนานุกรมโปรเจกต์ (`handleMergeTLMTerms`) ระบบจะตรวจสอบว่ามีคำศัพท์เดิมอยู่หรือไม่ หากมีอยู่แล้ว จะคง `id` เดิมไว้ เพื่อให้การบันทึกไปยัง Supabase Cloud เป็นการ **UPDATE** ไม่เกิดข้อมูลซ้ำซ้อน (Duplicate Rows)

---

## 🧪 เสาหลักที่ 4: Prompt Studio & Custom Engineering (วิศวกรรมพร้อมต์)

- **Prompt Presets**: มีแม่แบบมาตรฐาน 3 รูปแบบ:
  1. *Story & Dialogue Focus* (เน้นอารมณ์ บทสนทนา และความลื่นไหลของภาษาไทย)
  2. *Strict Terminology & UI* (เน้นความเป๊ะของคีย์และปุ่มเมนู ห้ามแปลงเกินตัวอักษร)
  3. *Unreal/Unity Game Engine Safe* (เน้นความปลอดภัยของแท็กคำสั่ง `%s`, `{0}`, `\n`)
- **Preserve Lore & Rules on Template Switch**:
  - เมื่อสลับแม่แบบ ระบบจะไม่ล้าง Lore หรือข้อกำหนดจักรวาลที่พิมพ์ไว้ แต่จะคงไว้ในบริบทพร้อมต์เสมอ
- **TagGuard Engine (Game Tag Preservation)**:
  - ระบบเชื่อมต่อกับ `tagGuard.ts` โดยตรง ทำการตรวจสอบความปลอดภัยของแท็กคำสั่งตัวแปรเกม เช่น `%s`, `{0}`, `\n`, `<tag>` เพื่อป้องกันไม่ให้เอนจินเกมพังหรือข้อความไม่แสดงผล
  - การแจ้งเตือนขนาดไบต์ (Max Byte Limit Warning) ได้รับการปิด/ปลดออก เพื่อให้นักแปลสามารถพิมพ์แปลเนื้อเรื่องและบทสนทนาได้อย่างอิสระโดยไม่มีแถบเตือนสีแดงมากวนใจ
- **Live Test Translation Bench**:
  - กล่องทดสอบคำแปลจริงพร้อมแทนที่ `[GLOSSARY TO USE]` และส่งไปยัง LLM API เพื่อดูผลลัพธ์ก่อนนำไปใช้งานจริง

---

## 🔒 3. ระบบสิทธิ์และการเข้าถึง (Role-Based Access & Read-Only Mode)

- **Lead Role**: มีสิทธิ์เต็มในการแก้ไข Lore, รัน Deep Mining, ปรับแต่ง Prompt Studio, และกดบันทึกเข้า Cloud / Local Storage
- **Non-Lead Members (Translators / Proofreaders)**:
  - เดิมทีระบบจะล็อกปิดไม่ให้เข้า แต่ในเวอร์ชันปรับปรุงใหม่นี้ สมาชิกทั่วไปสามารถกดเปิด **TLM Studio ในโหมด Read-Only** เพื่อ:
    - เข้ามาอ่าน **Universe Tone** และ **Directives** ของโปรเจกต์
    - ดูแนวทางการแปลและปรัชญาภาษาไทยที่หัวหน้าทีมวางไว้
    - ดูการทดสอบพร้อมต์เพื่อเข้าใจบริบทของเกม
    - โดยปุ่มบันทึกและนำเข้าคำศัพท์จะแสดงสถานะ `🔒 เฉพาะ Lead ที่บันทึกได้`

---

## ⌨️ 4. การเข้าถึงและการใช้งานในห้องแปล (Integration & Shortcuts)

1. **คีย์ลัดระดับสากล (`Ctrl + L`)**:
   - กด `Ctrl + L` (หรือ `Cmd + L` บน Mac) ได้จากทุกที่ในหน้าห้องแปล ทั้งแบบ **Table Mode (ตารางโปรเจกต์)** และ **Standard 3-Column Studio** เพื่อเปิด/ปิดหน้าต่าง TLM Studio ทันที
2. **ปุ่มแถบเครื่องมือหลัก**:
   - มีปุ่ม **`🧠 TLM Studio`** สีทองเด่นชัดบน Toolbar ด้านบนของทั้งสองหน้าจอ
3. **Interactive Universe Tone Banner**:
   - แบนเนอร์แสดงสถานะโทนจักรวาลที่ถูกบังคับใช้ (Enforced) สามารถคลิกเพื่อกระโดดเข้าหน้า TLM ได้ทันที
   - หากโปรเจกต์ยังไม่ได้ตั้งค่า TLM แบนเนอร์จะแสดงเป็นกรอบประสีน้ำเงินพร้อมข้อความชวนตั้งค่า:
     `✨ ตั้งค่าบริบทจักรวาล TLM Studio (เปิด Studio →)`

---

## ☁️ 5. ระบบซิงค์ข้อมูลสองชั้น (Double-Write Hybrid Vault)

เพื่อให้ข้อมูล Lore และกฎของจักรวาลไม่สูญหายแม้ทำงานออฟไลน์หรือเปลี่ยนเครื่อง:
1. **Cloud Database (`supabase.projects.tlm_lore` / `tlm_prompts`)**:
   - ข้อมูลถูกเก็บเป็น JSONB Columns ในตาราง `projects` บน Supabase ทำให้ทุกคนในทีมที่เปิดโปรเจกต์เดียวกันได้รับชุดคำสั่ง Lore เดียวกันแบบเรียลไทม์
2. **IndexedDB Local Project Cache**:
   - ข้อมูลถูกสำรองไว้ใน IndexedDB ของเบราว์เซอร์ เพื่อให้โหลดขึ้นมาแสดงได้ทันทีในระดับมิลลิวินาที (Zero-Latency Instant Hydration)
3. **Global Vault Backup (`__sys_tlm_vault__`)**:
   - มีระบบ Cloud Vault สำรองสำหรับกู้คืนการตั้งค่าในกรณีที่โครงสร้างโปรเจกต์มีการเปลี่ยนแปลง

---

---

## 📚 6. ระบบวงจรชีวิตและการแก้ไขคำศัพท์ในคลังศัพท์ (Glossary Lifecycle & Term Editing System)

เพื่อให้การจัดการคลังศัพท์มีความยืดหยุ่นสูงสุดและตอบสนองต่อการขัดเกลาสำนวนจริงของโปรเจกต์ม็อด ระบบจึงเปิดให้สามารถ **แก้ไขคำศัพท์ (Edit Glossary Terms)** ได้อย่างครอบคลุม:

```mermaid
graph TD
    Trigger["🖱️ ผู้ใช้คลิกปุ่ม 'แก้ไข' (SidePanel / Table View / Workarea)"]
    PermCheck{"🔒 ตรวจสอบสิทธิ์<br/>(canEditGlossaryTerm)"}
    Modal["📝 หน้าต่าง EditGlossaryModal<br/>- Source EN & Target TH<br/>- หมวดหมู่ Category<br/>- บริบท Lore Notes<br/>- คำต้องห้าม Forbidden Terms<br/>- ศัพท์ทางการ Official Toggle<br/>- จัดการสำนวนทางเลือก Alternatives"]
    Save["💾 บันทึกการแก้ไข (Save)"]
    
    Trigger --> PermCheck
    PermCheck -- ผ่าน --> Modal
    PermCheck -- ไม่ผ่าน --> Deny["🚫 ซ่อนปุ่ม / ไม่อนุญาต"]
    Modal --> Save
    
    Save --> State["1. React State (App.tsx: glossary)"]
    Save --> LocalCache["2. IndexedDB Local Cache (Instant Hydration)"]
    Save --> CloudDB["3. Supabase Cloud Database (glossary_terms)"]
    Save --> AuditLog["4. Audit Log บันทึกประวัติการเปลี่ยนแปลง"]
```

### 6.1 โครงสร้างข้อมูลและการปรับแต่ง (Editable Fields)
ผู้มีสิทธิ์สามารถปรับปรุงข้อมูลของคำศัพท์ใน `EditGlossaryModal` ได้ทุกมิติ:
1. **Source Term (EN)**: คำศัพท์ภาษาอังกฤษต้นฉบับ
2. **Target Term (TH)**: คำแปลหลักภาษาไทยที่ถูกต้องและผ่านการขัดเกลา
3. **Category**: หมวดหมู่คำศัพท์ (`general` ทั่วไป, `character` ตัวละคร/บอส, `location` สถานที่, `item` ไอเทม/อาวุธ, `skill` สกิล/เวทมนตร์)
4. **Lore Notes & Context**: บันทึกบริบทของเนื้อเรื่อง เหตุผลในการเลือกใช้คำ หรือตำแหน่งฉากที่พบคำนี้
5. **Forbidden Terms**: คำต้องห้ามที่ไม่ควรใช้แปล โดยระบบจะแยกคำด้วยเครื่องหมายจุลภาค (`,`) และเชื่อมโยงเข้ากับตัวตรวจคำผิด (TagGuard & Quality Linter)
6. **Official Term Toggle**: สถานะรับรองเข้าสู่คลังศัพท์ทางการหลัก (Official)
7. **Alternative Proposals Management**: ผู้ตรวจทานสามารถขัดเกลาข้อความของสำนวนทางเลือกที่แนบมา หรือกดลบสำนวนทางเลือกที่ไม่เหมาะสมออกได้ทันที

### 6.2 ลำดับขั้นสิทธิ์ในการแก้ไข (Permission Hierarchy)
- **ผู้ตรวจทาน (Lead Modder, Admin, Modder, Proofreader)**:
  - มีสิทธิ์สูงสุดในการแก้ไขคำศัพท์ทุกคำในระบบ ไม่ว่าจะเป็นคำที่เสนอโดยสมาชิกคนใด
  - มีสิทธิ์เปลี่ยนสถานะคำศัพท์เป็นทางการ (Official Toggle)
- **ผู้เสนอคำศัพท์ (Proposal Authors)**:
  - สมาชิกในบทบาทนักแปลทั่วไป (`translator`, `premium`) สามารถกดแก้ไขคำศัพท์ที่ตนเองเป็นผู้เสนอ (`term.proposedBy === currentUser.displayName`) ได้ตลอดเวลา **ตราบใดที่คำศัพท์นั้นยังไม่ได้รับรองเป็นศัพท์ทางการ**
- **ผู้เยี่ยมชม (Viewer, Guest)**:
  - ได้รับสิทธิ์แบบ Read-Only เท่านั้น ไม่แสดงปุ่มแก้ไขคำศัพท์

### 6.3 ทางลัดการแก้ไขบนหน้าจอแปลงาน (Editor Integration & Quick Shortcuts)
- **SidePanel (แท็บคลังศัพท์)**: มีปุ่ม **`✏️ แก้ไข`** สีครามบนการ์ดคำศัพท์ทุกคำ และบนสำนวนทางเลือกทุกสำนวน
- **TableTranslateView & TranslationWorkarea**: บริเวณแท็กชิปคำศัพท์ที่ตรวจพบในข้อความปัจจุบัน จะมีปุ่มไอคอนรูปดินสอขนาดกะทัดรัดติดอยู่ข้างคำแปล ช่วยให้นักแปลสามารถคลิกแก้ไขคำศัพท์ได้ทันทีที่พบจุดบกพร่องในฉากแปล โดยไม่ต้องเสียเวลาสลับแท็บไปค้นหาใน SidePanel

---

## 🛡️ 7. สถาปัตยกรรมความเสถียรและระบบซิงค์ URL (Fault Tolerance & URL Deep Linking)

### 7.1 ป้องกันจอค้างและจอดำมืด (Zero-Crash Defensive Type Guards)
ในการทำงานจริง ข้อมูล Lore หรือ Category ที่ถูกบันทึกในฐานข้อมูลหรือแคชอาจมีโครงสร้างที่ผิดเพี้ยนไปได้ (เช่น ถูกแปลงเป็น JSON String, Object หรือ Null) TLM Studio จึงมีชั้นการกรองข้อมูลแบบ **Ironclad Type Guards**:
1. **Bulletproof Category Parsing**: ตรวจสอบ `targetCategories` อย่างรัดกุม รองรับทั้งรูปแบบ Array มาตรฐาน, JSON String (`"[\"General\",\"Person\"]"`), Comma-separated String, และ Fallback เมื่อข้อมูลเป็น Null/Undefined ทำให้การวนลูป `.forEach()` ไม่เกิด `TypeError` ขัดข้อง
2. **Safe Navigation ใน Staging Grid**: ฟังก์ชัน `filteredStagedTerms` มีการครอบคลุม Safe Fallbacks `(term?.context || '').toLowerCase()` เพื่อป้องกันกรณีสตริงว่างเปล่า
3. **Safe Universe Tone Split**: ทุกจุดที่มีการดึงส่วนหัวของโทนจักรวาลผ่าน `.split('/')[0]` (เช่น ในแถบแบนเนอร์และ Prompt Compiler) จะถูกตรวจสอบชนิดตัวแปร `typeof universeTone === 'string'` เสมอ

### 7.2 ระบบ ErrorBoundary ป้องกันจอดำ (Fail-Safe Application Shield)
ใน React 18 หากเกิดข้อผิดพลาดรันไทม์ที่ไม่ได้ดักจับ (Unhandled Runtime Exception) คอมโพเนนต์จะ Unmount ทั้งหมดจนกลายเป็นจอดำมืด (#0f111a) ระบบจึงติดตั้ง:
- **Global ErrorBoundary**: ครอบ `<App />` ใน `main.tsx` รับประกันว่าหน้าเว็บจะไม่มืดสนิท หากมีข้อผิดพลาดจะแสดงการ์ดแจ้งเตือนสีแดงกึ่งโปร่งใส พร้อมปุ่มทางรอด:
  - 🏠 **กลับสู่หน้ารวมโปรเจกต์ (Back to Portal)**: รีเซ็ตสเตตและคืนสถานะแอปสู่หน้าหลัก
  - 🔄 **รีโหลดหน้าเว็บ (Reload Page)**
  - 📋 **คัดลอกรายละเอียดข้อผิดพลาด (Copy Error Details)**
- **Modal-Level ErrorBoundary**: ครอบ `<TLMStudioModal />` แยกต่างหาก เพื่อป้องกันไม่ให้ข้อผิดพลาดภายในสตูดิโอกระทบต่อพื้นที่แปลงานหลัก

### 7.3 การเชื่อมโยง URL เบราว์เซอร์และการแชร์ลิงก์ (URL Deep Linking & History Sync)
- เมื่อเข้าสู่ห้องแปลของโปรเจกต์ใดๆ เบราว์เซอร์จะอัปเดต URL เป็น `/?project=<slugOrId>` อัตโนมัติผ่าน `window.history.pushState`
- **รองรับการกดรีเฟรช (F5)**: ตัวระบบจะอ่านพารามิเตอร์ URL ในจังหวะ Cold Start และเปิดโปรเจกต์เดิมให้ทันทีโดยไม่เด้งกลับหน้าพอร์ทัล
- **รองรับปุ่ม Back / Forward**: ติดตั้ง `popstate` Event Listener ทำให้การกดปุ่มย้อนกลับของเบราว์เซอร์สลับระหว่างหน้ารวมโปรเจกต์และห้องแปลได้อย่างลื่นไหล

### 7.4 การปฏิบัติตามกฎของ React Hooks (Strict Rules of Hooks & Conditional Mounting)
- **Minified React Error #310 ("Rendered more hooks than during the previous render")**:
  - เกิดจากการวาง Hook เช่น `useMemo` หรือ `useState` ไว้หลังคำสั่ง Early Return เช่น `if (!isOpen) return null;` ซึ่งทำให้จำนวน Hook ที่ React รันในจังหวะปิดโมดอล (18 hooks) ไม่เท่ากับตอนเปิดโมดอล (19 hooks)
  - **แนวทางแก้ไข**:
    1. **Unconditional Top-Level Hooks**: ย้าย Hooks ทั้งหมด (`useState`, `useRef`, `useMemo`, `useEffect`) ขึ้นไปประกาศไว้ที่หัวฟังก์ชันคอมโพเนนต์เสมอ ห้ามมี `return` ใดๆ คั่นกลาง
    2. **Conditional Mounting ในระดับ Parent (`App.tsx`)**: สั่งเรนเดอร์โมดอลด้วย `{isOpen && <Modal />}` แทนการเรนเดอร์ทิ้งไว้ใน DOM เพื่อให้เกิดการ Mount และ Unmount อย่างสะอาด ป้องกัน Hook Desync ข้าม Render cycle 100%

---

## 📝 8. บันทึกประวัติการปรับปรุง (Changelog)

- **v2.2.0 (กันยายน 2026)**:
  - เพิ่มระบบแก้ไขคำศัพท์ในคลังศัพท์แบบเต็มรูปแบบ (`EditGlossaryModal`)
  - รองรับการแก้ไขคำแปล (TH), คำศัพท์ต้นฉบับ (EN), หมวดหมู่, บริบท Lore, คำต้องห้าม (Forbidden Terms), และการปรับปรุงสำนวนทางเลือก
  - เพิ่มปุ่มแก้ไขคำศัพท์บน SidePanel และปุ่มลัดแก้ไขบนแท็กชิปของทั้ง Table Mode และ Workarea Mode
  - ออกแบบระบบสิทธิ์ `canEditGlossaryTerm` รองรับทั้งกลุ่ม Reviewers และผู้เสนอคำศัพท์รายบุคคล
  - ซิงค์ข้อมูลอัตโนมัติ 4 ชั้น (State, IndexedDB, Supabase Database, Audit Log)
- **v2.1.1 (กันยายน 2026)**:
  - แก้ไขข้อผิดพลาด `Minified React error #310` (Hook count mismatch) โดยจัดระเบียบ Hooks ใน `TLMStudioModal`, `BatchTranslateModal`, `AIGlossaryModal` ให้อยู่ส่วนบนของคอมโพเนนต์อย่างไม่มีเงื่อนไข และใช้ Conditional Mounting `{isOpen && <Modal />}` ใน `App.tsx`
- **v2.1.0 (กันยายน 2026)**:
  - แก้ไขปัญหาจอดำค้างเมื่อกดเปิด TLM Studio โดยเพิ่ม Defensive Type Guards ใน `TLMStudioModal`, `TableTranslateView`, `TranslationWorkarea` และ `BatchTranslateModal`
  - ติดตั้ง `ErrorBoundary` ทั้งระดับแอปพลิเคชันและระดับโมดอล พร้อม UI สำหรับกู้คืนสถานะ
  - เพิ่มระบบ URL Synchronization และ Deep Linking (`/?project=slug`) รองรับการแชร์ลิงก์และปุ่ม Back/Forward ของเบราว์เซอร์
- **v2.0.0 (กันยายน 2026)**:
  - แก้ปัญหา Token Cap 1200 ให้เป็น Dynamic Options (4096 สำหรับทดสอบ, 6000 สำหรับ Deep Mining)
  - เพิ่ม Resilient Partial JSON Array Recovery ป้องกันบั๊กสกัดคำศัพท์หลุดกึ่งกลาง
  - เชื่อมโยง `maxBytesLimit` เข้ากับ Linter `tagGuard.ts` แสดงคำเตือนแบบเรียลไทม์
  - เพิ่มปุ่ม TLM Studio และ Interactive Banner ใน Table Translate View และ Workarea
  - เพิ่มคีย์ลัด `Ctrl+L` ทั่วทั้งแอปพลิเคชัน
  - ปรับปรุงการนำเข้าคำศัพท์ไม่ให้เกิด Duplicate Key ใน Supabase
  - เพิ่ม Read-Only Mode สำหรับนักแปลทั่วไป

