# 👑 PROJECT MASTER CONTROL BIBLE: Autonomous AI Studio & Home Automation
> **บทบาทเอกสาร:** แหล่งข้อมูลความจริงหนึ่งเดียว (Single Source of Truth - SSOT) ประจำโปรเจกต์  
> **Master Chat Conversation ID:** `ec35ca32-12a6-4378-8ce3-ce0a8d7dc7ad`  
> **Project Directory:** `Z:\01_Work\01_ComfyUi_Project\`  
> **วันที่มีผล:** 2026-09-17  
> **สถานะปัจจุบัน:** Active Master Hub

---

## 1. กฎและโปรโตคอลการทำงานร่วมกันระหว่างแชท (Hub & Spoke Protocol)

ระบบนี้ใช้โครงสร้างแบบ **Hub & Spoke (แชทแม่บท + แชทย่อยเฉพาะทาง)** เพื่อให้การทำงานมีประสิทธิภาพสูงสุด:

```mermaid
flowchart TD
    MasterChat["👑 MASTER CHAT (แชทนี้ - Hub)\n- วางแผนกลยุทธ์ & กำหนดสถาปัตยกรรม\n- บันทึกการเปลี่ยนแปลงค่าคอนฟิกส่วนกลาง\n- กำกับทิศทางทุกแชทย่อย"]
    
    MasterChat <--> MasterDocs[("📁 SSOT Storage (ไดรฟ์ Z)\n• PROJECT_MASTER_CONTROL_BIBLE.md\n• PROJECT_STATE.json\n• COMFYUI_AI_SHORT_DRAMA_MASTER_BIBLE.md\n• HOME_DASHBOARD_HANDOVER_BIBLE.md")]

    SubChat1["🛍️ Worker Chat 1: Affiliate Studio\n(ปักตะกร้าสินค้า / แปลงรูปเป็น 3D / CTA Overlay)"]
    SubChat2["🎙️ Worker Chat 2: Voice Clone & Story\n(โคลนเสียง F5-TTS / สรุปบทเล่าเรื่อง)"]
    SubChat3["🎭 Worker Chat 3: Short Drama Studio\n(บทละคร 3 ฉาก / คุมหน้าตัวละคร / ซับไทย)"]
    SubChat4["🏠 Worker Chat 4: Home Dashboard\n(เว็บแดชบอร์ดบ้าน 24/7 / IoT / วัดค่าไฟ)"]

    MasterDocs -.->|อ่านกฎและสถานะล่าสุด| SubChat1
    MasterDocs -.->|อ่านกฎและสถานะล่าสุด| SubChat2
    MasterDocs -.->|อ่านกฎและสถานะล่าสุด| SubChat3
    MasterDocs -.->|อ่านกฎและสถานะล่าสุด| SubChat4
```

### 📜 กฎเหล็กสำหรับทุก Worker Chat:
1. **Always Read Master State First**: เมื่อเริ่มแชทใหม่หรือเริ่มงานใหม่ ต้องอ่านไฟล์ `PROJECT_MASTER_CONTROL_BIBLE.md` และ `PROJECT_STATE.json` เป็นอันดับแรกเสมอ
2. **Do Not Overwrite Shared Services**: ห้ามแก้ไขพอร์ตเซิร์ฟเวอร์หลัก (`192.168.1.102:5050` และ `192.168.1.11:8188`) หรือเปลี่ยนโครงสร้างฐานข้อมูล `power_history.db` โดยพลการ หากต้องการเพิ่มตาราง ให้ใช้คำสั่ง `CREATE TABLE IF NOT EXISTS` เท่านั้น
3. **Report Back to Master**: เมื่อพัฒนางานหรือสร้างไฟล์ใหม่เสร็จสิ้น ให้บันทึกการเปลี่ยนแปลงลงใน Changelog หรือแจ้งกลับมายัง Master Chat เสมอ

---

## 2. ข้อมูลระบบและพิกัดเครือข่ายส่วนกลาง (Central System Topology)

| เครื่อง / อุปกรณ์ | Network IP | บริการหลัก | สเปกฮาร์ดแวร์ | บทบาทในโปรเจกต์ |
| :--- | :--- | :--- | :--- | :--- |
| **🗄️ NAS Server** | `192.168.1.102:5050` | FastAPI Docker (`ai_power_monitor`) | Intel N100 (4C/4T)<br>RAM 16GB, HDD 8TB + 2x NVMe | **Central AI Multi-GPU Orchestrator & Smart Dispatcher** โฮสต์ Web Hub, บริหารคิวงาน ComfyUI, ตรวจจับสุขภาพและ VRAM, ตัดต่อรวมคลิป FFmpeg + Edge-TTS |
| **💻 เครื่องฉัน (Main PC)** | `192.168.1.100:8188` | ComfyUI Production Node | RTX 4080 SUPER (16GB)<br>Ryzen 9 5950X (16C/32T) | **โหนดความเร็วสูงสุด (Priority 1 Speed)**: เจนเนอเรตงานด่วนและฉากหลัก เมื่อเปิดเครื่อง NAS จะดึงพลังการ์ดจอนี้เป็นอันดับแรก |
| **🤖 เครื่อง AI (AiPC1)** | `192.168.1.11:8188` | ComfyUI Production Node | RTX 4070 (12GB)<br>Ryzen 7 5800X (8C/16T) | **โหนดเรนเดอร์ 24/7 (Priority 2 Standby / Failover)**: เปิดทำงานตลอด 24 ชม. รับงานสำรองทันทีที่เครื่องหลักปิด หรือรับงานพร้อมกันในโหมดขนาน |

### ⚡ สถาปัตยกรรมกระจายงานอัจฉริยะ (Multi-GPU Smart Dispatching Architecture):
1. **Smart Auto-Routing:**
   - NAS ตรวจสอบสถานะและ VRAM ของทั้ง 2 โหนดทุก 2.5 วินาที
   - หาก Main PC (RTX 4080 SUPER) ออนไลน์และว่าง -> ส่งงานให้ Main PC เพื่อความเร็วสูงสุด
   - หาก Main PC ปิดเครื่อง หรือคิวยุ่ง -> ส่งงานให้ AiPC1 (RTX 4070) อัตโนมัติ 100% โดยผู้ใช้ไม่ต้องเปลี่ยน URL
2. **Dual-GPU Parallel Rendering Mode (เรนเดอร์ขนาน 2 การ์ดจอพร้อมกัน):**
   - เมื่อสั่งทำละครสั้น 3 ฉากในโหมด `parallel` และทั้งสองโหนดออนไลน์:
     - Main PC (RTX 4080S) เรนเดอร์: ฉากที่ 1 และ ฉากที่ 2
     - AiPC1 (RTX 4070) เรนเดอร์: ฉากที่ 3
   - ทั้ง 2 การ์ดจอทำงานพร้อมกัน ส่งผลให้เวลาเรนเดอร์ลดลงเหลือเพียง ~50%
3. **Unified Storage & Zero Local Model Redundancy:**
   - คลังโมเดลกลาง: `//192.168.1.102/06_Ai_Model/` ทุกโหนดอ่านไฟล์จาก NAS ไม่ต้องโหลดซ้ำซ้อน
   - คลังผลงานกลาง (Central Footage): `Z:\05_VideoFootage\01_ComfyUi_Footage\` (`/footage` ในคอนเทนเนอร์ NAS)
   - ไฟล์วิดีโอและรูปภาพทั้งหมดจะถูกบันทึกลง NAS โดยตรง และให้บริการผ่านเว็บโดยตรงจากดิสก์ (Direct Disk Streaming) ไม่มีลิงก์เสีย

---

## 3. แผนที่โมดูลและงานของแต่ละแชท (Module Breakdown)

### 👑 แชทแม่บท (Master Chat - แชทนี้)
- **หน้าที่:** ควบคุมทิศทาง, ปรับแก้สถาปัตยกรรม, ตัดสินใจเลือกเทคโนโลยี, บันทึกการเปลี่ยนแปลง (Sync State), และตรวจเช็กความเรียบร้อยของทุกโมดูล

### 🛍️ แชทย่อยที่ 1: ระบบปักตะกร้าสินค้า Affiliate (Affiliate Product Studio)
- **เป้าหมาย:** สร้างวิดีโอรีวิวและโปรโมตสินค้าสำหรับ TikTok Shop / Shopee / Reels
- **โฟลเดอร์ทำงาน:** `01_AI_Short_Drama_Engine/affiliate_engine.py`
- **หน้าที่สำคัญ:**
  - แปลงรูปสินค้า 1 รูป เป็นคลิป 3D หมุนโชว์ความงามด้วย MiniMax H3
  - ซ้อนเลเยอร์ (Overlay): ตะกร้าสีเหลืองกระพริบ + ลูกศรชี้มุมซ้ายล่าง + ป้ายราคาลดพิเศษ
  - เสียงพากย์กระตุ้นการสั่งซื้อ (Call-To-Action)

### 🎙️ แชทย่อยที่ 2: ระบบโคลนเสียง AI & ช่องเล่าเรื่อง (Voice Clone & Storytelling)
- **เป้าหมาย:** สร้างช่องเล่าเรื่อง (เรื่องผี/ประวัติศาสตร์/ข้อคิด) ด้วยเสียงพูดของคุณเอง
- **โฟลเดอร์ทำงาน:** `01_AI_Short_Drama_Engine/storyteller_engine.py` & `voice_cloning_engine.py`
- **หน้าที่สำคัญ:**
  - รับไฟล์เสียงอัด 15-30 วินาที เพื่อโคลนเสียงภาษาไทย (F5-TTS / CosyVoice)
  - เจนเนื้อเรื่อง + คำบรรยายบรรยากาศ + ภาพฉากดาร์กๆ ลึกลับ
  - มิกซ์เสียง Ambient (เสียงฝน, เสียงลม, ดนตรีคลอ) + ซับไตเติล Kinetic ตามคำ

### 🎭 แชทย่อยที่ 3: ระบบละครสั้น AI พูดไทย (Short Drama & Higgsfield Director Studio)
- **สถานะ:** Active Production v2.8 (ติดตั้งทั้งบน Local และ NAS Web Studio `http://192.168.1.102:5050`)
- **โฟลเดอร์ทำงาน:** `01_AI_Short_Drama_Engine/short_drama_engine.py` และ `02_NAS_Server_And_Deployment/short_drama_engine.py`
- **โหมดการทำงานคู่ (Dual Modes):**
  1. `[⚡ พรีเซ็ตด่วน 1-คลิก]`: เลือกพรีเซ็ตบทละครและเสียงพากย์ แล้วสั่งเรนเดอร์จบในคลิกเดียว
  2. `[🎬 Higgsfield Director Studio]`: สตูดิโอกำกับภาพยนตร์ระดับมืออาชีพ
- **หน้าที่และฟีเจอร์ระดับ Higgsfield.ai:**
  - **Character Vault (คลังตัวละคร):** ล็อกใบหน้าและคอสตูมตัวละครให้คงที่ตลอดทั้งเรื่องผ่าน Node 114 (`first_frame`) ของ MiniMax H3 รองรับการสร้าง/อัปโหลดรูปตัวละครจริง
  - **9 Cinematic Camera Motions:** ปรับมุมกล้อง 9 ทิศทาง (Zoom In/Out, Pan L/R, Crane Up, Tilt Down, Orbit 360, Handheld Shake, Static)
  - **Non-Linear Shot-by-Shot Timeline & Per-Shot Re-roll:** แยกการ์ดควบคุมแต่ละฉากเป็นอิสระ สามารถกดเรนเดอร์ใหม่เฉพาะฉากที่ไม่พอใจ (Re-roll) ได้โดยไม่ต้องเรนเดอร์ใหม่ทั้งตอน
  - **Frame Continuity Chaining:** นำภาพเฟรมสุดท้ายของฉากก่อนหน้ามาเป็นจุดเริ่มต้นของฉากถัดไป เพื่อความต่อเนื่องของภาพ
  - **Master Movie Stitcher:** รวบรวมทุกฉากที่ผ่านการตรวจสอบ ตัดต่อรวมภาพและเสียง พร้อมฝังซับไตเติลไทย Garuda ด้วย FFmpeg บันทึกลง `Z:\05_VideoFootage\01_ComfyUi_Footage\04_Finished_Productions\Drama_Episodes\` อัตโนมัติ
  - รองรับโหมดกระจายงาน Multi-GPU (Auto / Dual-GPU Parallel / Main PC / AiPC1)
  - พากย์เสียง AI ภาษาไทย Edge-TTS (เปรมวดี / นิวัฒน์)

### 🏠 แชทย่อยที่ 4: เว็บแดชบอร์ดบ้านอัจฉริยะ (Home Dashboard & Multi-GPU Farm Hub)
- **สถานะ:** Active Production (พอร์ต 5050 รัน 24 ชม. บน NAS Docker)
- **โฟลเดอร์ทำงาน:** `02_NAS_Server_And_Deployment/`
- **หน้าที่สำคัญ:**
  - ศูนย์กลางบ้าน (Home Portal): สภาพอากาศสดเชียงใหม่, ลิงก์ด่วน DSM, UGOS, ComfyUI, TStudio, Home Assistant IoT
  - AI Multi-GPU Farm Hub: ติดตาม VRAM, คิวงาน, สถานะออนไลน์ของ RTX 4080S และ RTX 4070
  - สตูดิโอละครสั้น AI: หน้าจอสร้างละคร 1-Click พร้อม Video Player & Episodes Library
  - แดชบอร์ดสด (Live Monitor): วัตต์แบบเรียลไทม์ 3 อุปกรณ์ และค่าไฟเฉลี่ยต่อชั่วโมง
  - วิเคราะห์ค่าไฟ (Cost Analytics): กราฟแท่งรายชั่วโมง/วัน/เดือน/ปี พร้อมระบบส่งออก CSV

### 🎙️ โมดูลเสริม: ระบบสร้างเสียงพูดขายสินค้าภาษาไทย (Thai Commercial TTS Studio)
- **สถานะ:** Active Production v1.0
- **โฟลเดอร์ทำงาน:** `01_AI_Short_Drama_Engine/Thai_Commercial_TTS_Studio.json` และ `ComfyUI_Thai_Commercial_TTS`
- **หน้าที่สำคัญ:**
  - แก้ปัญหาเสียงภาษาไทยของ MiniMax ที่โทนแบนและออกเสียงทับศัพท์เพี้ยน
  - คลัง 10 สไตล์เสียงภาษาไทยสำเร็จรูปสำหรับการขายสินค้า (แม่ค้าไลฟ์สด, บิวตี้, ไอที, Flash Sale, แบรนด์หรู)
  - Custom Node สำหรับ ComfyUI (`ThaiCommercialTTS` + `ThaiSalesScriptTemplates`)
  - รองรับ ComfyUI Audio Output (`SaveAudioMP3`) และเซฟไฟล์ลง `Z:\05_VideoFootage\01_ComfyUi_Footage\03_Audio\Voiceovers\`
  - สคริปต์ Standalone 1-Click (`run_thai_commercial_tts.bat`) สร้างเสียงได้ทันทีไม่ต้องเปิด ComfyUI

---

## 4. ข้อความสั่งงานสำหรับเริ่มแชทย่อย (Universal Worker Prompt Template)

เมื่อคุณเปิดแชทใหม่ในหัวข้อใดก็ตาม ให้ก๊อปปี้ข้อความนี้ไปวางเปิดหัวได้ทันที:

```markdown
สวัสดีครับ นี่คือ Worker Chat สำหรับภารกิจ: [เลือก: 🛍️ Affiliate Studio / 🎙️ Voice Clone & Story / 🎭 Short Drama / 🏠 Home Dashboard]

กรุณาอ่านพิมพ์เขียวและสถานะล่าสุดของโปรเจกต์จาก Master Chat ก่อนเริ่มงาน:
1. Z:\01_Work\01_ComfyUi_Project\PROJECT_MASTER_CONTROL_BIBLE.md
2. Z:\01_Work\01_ComfyUi_Project\PROJECT_STATE.json

โปรโตคอลการทำงาน:
- ทำงานภายใต้สถาปัตยกรรมและพิกัดระบบเดิม (NAS 192.168.1.102:5050, ComfyUI 192.168.1.11:8188)
- โฟกัสเฉพาะภารกิจของแชทนี้ โดยไม่ไปกระทบระบบส่วนกลาง
- เมื่อทำส่วนใดเสร็จ ให้รายงานสรุปเพื่อนำไปแจ้งอัปเดตสถานะใน Master Chat

เมื่อเข้าใจกฎและข้อมูลแล้ว กรุณารายงานความพร้อม แล้วเริ่มงานในส่วนนี้ได้เลย
```

---

---

## 5. ระบบบูตอัตโนมัติของเครื่อง AI (AiPC1 Autonomous Autostart Architecture)

เพื่อให้เครื่อง `AiPC1` (`192.168.1.11`) ทำงานเสมือน Dedicated Server 24/7 เมื่อเปิดเครื่องหรือรีสตาร์ต ระบบจะรัน ComfyUI และ Telemetry Agent ขึ้นมาโดยอัตโนมัติด้วยคุณสมบัติดังนี้:

1. **Dual Fail-safe Launch Mechanism**:
   - **กลไกที่ 1 (Primary):** Windows Task Scheduler Task `\ComfyUI` ทริกเกอร์แบบ `AtLogOn` (ผู้ใช้ `Ai`) ด้วยสิทธิ์ `Highest` พร้อม Hidden window
   - **กลไกที่ 2 (Secondary):** Windows Startup Folder Script (`%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\Start-ComfyUI.vbs`)
2. **Zero-Window & Background Daemon**:
   - ควบคุมผ่าน VBScript wrapper (`start_comfyui_silent.vbs`) เรียก PowerShell ด้วยโหมด `-WindowStyle Hidden` และ `wscript.exe` ปราศจากหน้าต่างดำ CMD กวนใจบนหน้าจอ
3. **Idempotency & Auto Network Discovery**:
   - `autostart_comfyui.ps1` ทำการ Ping ตรวจสอบเครือข่าย NAS (`192.168.1.102`) นานสูงสุด 30 วินาทีเพื่อรอเน็ตเวิร์กพร้อม
   - ทำการ Map ไดรฟ์โมเดล SMB `\\192.168.1.102\06_Ai_Model` โดยอัตโนมัติ
   - ตรวจสอบพอร์ต 8188 หากพบว่า ComfyUI รันอยู่แล้ว จะไม่รันซ้ำซ้อน (Safe Duplicate Guard)
   - ตรวจสอบ `aipc1_agent.py` หากรันอยู่แล้ว จะไม่เปิดซ้ำ
4. **เครื่องมือบริหารจัดการบน AiPC1 (`C:\ComfyUI_windows_portable\`):**
   - `Check-ComfyUI-Status.bat`: ตรวจสอบสถานะ PID, พอร์ต 8188, และ 15 บรรทัดล่าสุดของ Log
   - `Restart-ComfyUI.bat`: รีสตาร์ต ComfyUI ในเบื้องหลังอย่างปลอดภัย
   - `Stop-ComfyUI.bat`: ปิด ComfyUI และ Telemetry Agent

---

## 6. บันทึกประวัติการปรับปรุงส่วนกลาง (Master Change Log)

| วันที่-เวลา | แชทที่สั่งการ | รายละเอียดการปรับปรุง | ผลกระทบต่อระบบ |
| :--- | :--- | :--- | :--- |
| **2026-09-18 11:20** | 👑 Master Chat | ติดตั้งระบบสร้างเสียงพูดขายสินค้าภาษาไทย (Thai Commercial TTS Studio v1.0) | แก้ปัญหาเสียง MiniMax ภาษาไทยไม่เนียน ด้วยโมเดล Microsoft Neural HD พร้อมคลัง 10 สไตล์เสียงขายสินค้า, ComfyUI Workflow JSON, Custom Node, และ Batch Launcher บันทึกลงคลัง NAS อัตโนมัติ |
| **2026-09-17 22:50** | 👑 Master Chat | อัปเกรดระบบสู่ Higgsfield-Style AI Director Studio (v2.8) | เพิ่มระบบ Character Vault (คุมหน้าและชุดตัวละครผ่าน Node 114 first_frame), แผงควบคุมมุมกล้อง 9 ทิศทาง, ไทม์ไลน์แยกฉากพร้อม Re-roll เฉพาะช็อต, การส่งต่อภาพเฟรมสุดท้าย (Continuity Chaining), และ Master Movie Stitcher พร้อม UI สลับโหมด ด่วน/โปร |
| **2026-09-17 22:15** | 🛍️ Worker Chat: Affiliate | อัปเดตพิกัดระบบและรวมมาตรฐานไดรฟ์ (Unified RaiDrive Z: บน AiPC1) | ปลด SMB เก่าออก ป้องกันชื่อไดรฟ์ชน ทำให้โครงสร้างพาธ Z: ของ Main PC และ AiPC1 ตรงกัน 100% |
| **2026-09-17 15:55** | 🛍️ Worker Chat: Affiliate | พัฒนา Affiliate Product Studio Engine (`affiliate_engine.py`) สำเร็จ v1.0 | สร้างคลิปปักตะกร้า 3D วิดีโอ, ตะกร้าเหลืองกระพริบ, ลูกศรชี้ CTA เด้งดุ๊กดิ๊ก, ป้าย Flash Sale, เสียงพากย์เร่งยอดขาย |
| **2026-09-17 22:05** | 👑 Master Chat | กำหนดคลังผลงานส่วนกลาง `Z:\05_VideoFootage\01_ComfyUi_Footage` | ComfyUI ทุกเครื่องบันทึกไฟล์วิดีโอ/รูปภาพลงคลังกลางอัตโนมัติ 100% |
| **2026-09-17 22:00** | 👑 Master Chat | ติดตั้ง ComfyUI Studio บน Main PC (RTX 4080 SUPER 16GB) | ขยายขีดความสามารถ AI Node 2 พร้อมแชร์โมเดลจาก NAS ก้อนเดียวกัน 100% |
| **2026-09-17 21:35** | 👑 Master Chat | ติดตั้งระบบ Autonomous Autostart บน AiPC1 (Dual Task Scheduler + Startup VBS) | ComfyUI & Telemetry Agent บูตตัวเองอัตโนมัติ 100% ไร้หน้าต่างดำ |
| **2026-09-17 15:30** | 👑 Master Chat | สถาปนาระบบ Master Control & Registry (Hub & Spoke) | สร้างมาตรฐานควบคุมทุกแชทย่อยในโปรเจกต์ |
| **2026-09-17 15:10** | 👑 Master Chat | จัดผังโหนด ComfyUI MiniMax H3 เป็น 4 โซนสีภาษาไทย | สร้างไฟล์ `MiniMax_H3_Short_Drama_Studio_UI.json` ติดตั้งบน AiPC1 |
| **2026-09-17 14:30** | 👑 Master Chat | แก้ไขบั๊กสัดส่วน 9:16 และตัวล้างวรรคตอน Edge-TTS | อัปเกรด `short_drama_engine.py` บน NAS Docker |

