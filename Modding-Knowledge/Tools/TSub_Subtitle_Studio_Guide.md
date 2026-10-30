# 🎬 TSub - Subtitle Translation Studio (Standalone Edition)

โปรแกรมแปลไฟล์คำบรรยาย **`.srt` (SubRip Subtitle)** ฉบับ **Standalone 100%** สำหรับงานภาพยนตร์, อนิเมะ, ซีรีส์ และแอนิเมชัน ผสาน 2 โหมดการทำงานระดับโปรในโปรแกรมเดียว:
1. **🎬 Subtitle Studio (ตรวจสอบ & แปลรายบรรทัดแบบละเอียด)**
2. **⚡ Batch Pipeline (ระบบแปลความเร็วสูงระดับอุตสาหกรรมแบบ TRun สำหรับไฟล์ขนาดใหญ่)**

---

## 🌟 ฟีเจอร์หลัก (Key Features)

### 1. 🎬 หน้าที่ 1: Subtitle Studio (โหมดสตูดิโอ & ตรวจสอบละเอียด)
- ตารางกริดเสมือนจริง (Virtualized Grid) รองรับไฟล์ขนาดใหญ่หลายหมื่นบรรทัด
- มาตรวัดความเร็ว **CPS Inspector** แจ้งเตือนสีแดงเมื่อข้อความยาวเกินเวลาอ่าน (CPS > 25)
- ระบบแปลอัจฉริยะ (**Smart Translate**), แปล 3 สไตล์ (**Options - F3**), และ **Cinematic Tones** 7 อารมณ์
- ปุ่มตัดคำบรรยายภาษาไทย 2 บรรทัดอัตโนมัติ (**Auto Line-Break**)
- ตัวแก้ไขคำแปลและคำอ้างอิง AI (AI Reference)

### 2. ⚡ หน้าที่ 2: Batch Pipeline (ระบบแปลข้อความเยอะแบบ TRun)
- **High-Throughput Chunking:** รวมส่งข้อมูลครั้งละ 15 - 50 ซับไตเติ้ลต่อ Request ประหยัดโทเคน 80% และแปลเร็วขึ้น 5-10 เท่า
- **Tag Masking:** เข้ารหัสป้องกัน HTML/SRT Tags (`<i>`, `<b>`, `<font>`) ป้องกัน AI ทำลายโครงสร้างซับ
- **Auto Incremental Save:** บันทึกไฟล์ `.srt` ลงดิสก์อัตโนมัติทุกๆ Batch ไม่ต้องกลัวแครช
- **Full Control:** ปุ่ม **Start 🚀 / Pause ⏸️ / Resume ▶️ / Stop ⏹️**
- **Live Colored Console:** หน้าต่าง Terminal รายงานสถานะแบบเรียลไทม์ (ความเร็ว subs/s, เวลาที่ใช้, และเวลาคาดการณ์ ETA)
- **Two-Way Sync:** ข้อมูลที่แปลจาก Batch Pipeline จะซิงก์กลับเข้าสู่ Studio อัตโนมัติทันที

### 3. 📁 Profile System & Auto-Generate Prompts
- จัดการโปรไฟล์แยกตามเรื่อง (**New, Clone, Rename, Delete**)
- กำหนดคู่ภาษา: **ต้นทาง (English, Japanese, Chinese, Korean ฯลฯ) -> ปลายทาง (Thai, English ฯลฯ)**
- ปุ่ม **`✨ สร้างข้อมูลอัตโนมัติ`** สำหรับสร้าง Main Prompt, 3-Options Prompt และสรุป **Lore Context (เรื่องย่อ, บุคลิก/เพศตัวละคร, คำศัพท์เฉพาะ)**

### 4. 🌐 Multi-API Provider & Glossary
- รองรับ **OpenAI** (`gpt-5.6-luna`, `gpt-5.4-mini`, `gpt-4o`, `o4-mini`, `o3-mini`), **DeepSeek**, **Google Gemini**, **Anthropic Claude**, และ **Local LLM** (LM Studio / Ollama แบบออฟไลน์ฟรี 100%)
- คลังคำศัพท์ **Glossary Manager** พร้อมระบบ **Anti-Drift** บังคับคำแปลชื่อเฉพาะให้แม่นยำตลอดทั้งเรื่อง

---

## 🚀 วิธีเปิดใช้งาน (How to Run)

### วิธีที่ 1: ดับเบิลคลิกไอคอนบน Desktop (TSub)
หรือดับเบิลคลิกที่ไฟล์ **`run_tsub.bat`** ในโฟลเดอร์นี้

### วิธีที่ 2: รันผ่าน Terminal / PowerShell
```powershell
cd E:\Mod_Workspace\Modder_project\modder-hub\tools\Standalone\TSub
python main.py
```