# 🏠 Home Dashboard & AI Smart Control: Handover & Architecture Bible
> **เอกสารพิมพ์เขียว (Blueprint) สำหรับการยกยอดระบบไปพัฒนาต่อเป็น Web Dashboard ประจำบ้านในแชทใหม่**  
> **วันที่มีผล:** 2026-09-17  
> **สถานะปัจจุบัน:** Production Ready บน NAS (`192.168.1.102:5050`)

---

## 1. วัตถุประสงค์และการต่อยอด (Vision)
นำระบบมอนิเตอร์ไฟฟ้าและควบคุม AI ที่รันอยู่บน NAS ตลอด 24 ชม. มาขยายขอบเขต (Scale Up) ให้กลายเป็น **"เว็บแดชบอร์ดศูนย์กลางของบ้าน (Smart Home & AI Farm Dashboard)"** ที่รวม:
1. **Hardware & Power Monitor**: วัดกำลังไฟและคำนวณค่าไฟ (บาท) ของคอมพิวเตอร์และอุปกรณ์ทั้งหมดในบ้าน
2. **Home Automation & IoT Hub**: เชื่อมต่ออุปกรณ์ Smart Home, อุณหภูมิ, เซ็นเซอร์, หลอดไฟ, ปลั๊กไฟอัจฉริยะ (เช่น Sonoff, Tuya, Home Assistant)
3. **AI Generation Studio**: สตูดิโอสั่งงาน ComfyUI / MiniMax H3 / LLM จากหน้าเว็บเดียว
4. **NAS Network Storage & Media Center**: ดูสถานะพื้นที่ไดรฟ์, ดาวน์โหลด, และเปิดเล่นมีเดียในบ้าน

---

## 2. พิกัดและขุมทรัพย์ไฟล์ที่สามารถดึงไปใช้ได้ทันที (Reusable Assets)

| ส่วนประกอบ | แหล่งไฟล์ต้นทาง | คำอธิบายสิ่งที่นำไปใช้ได้ |
| :--- | :--- | :--- |
| **🎨 หน้าเว็บ Frontend** | `Z:\01_Work\01_ComfyUi_Project\02_NAS_Server_And_Deployment\frontend\` | • `index.html`: โครงสร้างหน้าเว็บดีไซน์หรูหรา Dark Mode + Glassmorphism<br>• `app.js`: ระบบดึงข้อมูลเรียลไทม์ (Polling/WebSocket), กราฟ Chart.js, การสลับแท็บ<br>• `style.css`: ธีมสี Tailwind CSS และการจัดสัดส่วน |
| **🚀 เซิร์ฟเวอร์ Backend** | `Z:\01_Work\01_ComfyUi_Project\02_NAS_Server_And_Deployment\nas_server.py` | • FastAPI Server พอร์ต 5050<br>• ระบบบันทึก Time-Series ลง SQLite (ราย ชม. / วัน / เดือน / ปี)<br>• ระบบคำนวณค่าไฟสูตรประเทศไทย (4.18 บาท/หน่วย)<br>• API พร็อกซีสตรีมวิดีโอและควบคุมคิว ComfyUI |
| **🐳 Docker 24/7 บน NAS** | `Z:\01_Work\01_ComfyUi_Project\02_NAS_Server_And_Deployment\` | • `docker-compose.yml` & `Dockerfile`<br>• ติดตั้ง FFmpeg, ฟอนต์ไทย `fonts-thai-tlwg`, Edge-TTS และตัวอ่านเซ็นเซอร์ Intel RAPL บน NAS |
| **⚡ เอเจนต์ตรวจวัดวัตต์ไฟ** | `Z:\01_Work\01_ComfyUi_Project\03_Power_Telemetry_Agents\` | • `main_pc_agent.py`: เอเจนต์ของเครื่องหลัก (RTX 4080 Super + 5950X)<br>• `aipc1_agent.py`: เอเจนต์ Zero-Subprocess Pynvml บนเครื่อง AI (RTX 4070 + 5800X)<br>• Intel RAPL Hardware reader ใน `nas_server.py` (วัด Intel N100) |
| **📁 ฐานข้อมูล SQLite** | `/volume1/ai_power_monitor/data/power_history.db` บน NAS | โครงสร้างตาราง: `hourly_stats`, `daily_stats`, `monthly_stats`, `yearly_stats`, `render_jobs`, `short_drama_episodes` |
| **🎭 สตูดิโอละครสั้น ComfyUI** | `Z:\01_Work\01_ComfyUi_Project\01_AI_Short_Drama_Engine\` | • `short_drama_engine.py`: ตัวขับเคลื่อนอัตโนมัติ<br>• `MiniMax_H3_Short_Drama_Studio_UI.json`: ผังโหนดภาษาไทย 4 โซนสี |

---

## 3. ข้อมูลเครือข่ายและสเปกฮาร์ดแวร์ประจำบ้าน (Network & Spec Cheat Sheet)

- **NAS UGREEN DXP2800**: `192.168.1.102` (โฮสต์แดชบอร์ดหลักที่พอร์ต `:5050`, Intel N100, RAM 16GB, HDD 8TB + 2x NVMe)
  - SSH: `crysers@192.168.1.102`
  - ไดเรกทอรีทำงาน: `/volume1/ai_power_monitor/`
- **เครื่อง AI (AiPC1)**: `192.168.1.11` (ComfyUI ที่พอร์ต `:8188`, RTX 4070 12GB, Ryzen 7 5800X, RAM 64GB)
  - SSH: `Ai@192.168.1.11`
  - คีย์ SSH: `~/.ssh\id_ed25519`
- **เครื่องฉัน (Main PC)**: `192.168.1.100` (RTX 4080 Super 16GB, Ryzen 9 5950X 16C/32T, RAM 128GB)
  - ไดรฟ์โปรเจกต์: `Z:\01_Work\01_ComfyUi_Project\` หรือ `D:\Home_Dashboard\`

---

## 4. ข้อความแม่แบบสำหรับเปิดแชทใหม่ (New Chat Prompt Template)

เมื่อคุณเปิดแชทใหม่ ให้คัดลอกข้อความด้านล่างนี้ไปวางได้ทันที AI ตัวใหม่จะเข้าใจบริบทและทำงานต่อได้แบบไร้รอยต่อ 100%:

```markdown
สวัสดีครับ นี่คือการเริ่มโปรเจกต์พัฒนา "Web Home Dashboard ประจำบ้าน"
โดยดึงระบบรากฐานจากโปรเจกต์ AI Power Monitor & ComfyUI Studio เดิมมาใช้งาน

กรุณาอ่านข้อมูลสถาปัตยกรรมและไฟล์ต้นแบบเหล่านี้ก่อนเริ่ม:
1. Z:\01_Work\01_ComfyUi_Project\HOME_DASHBOARD_HANDOVER_BIBLE.md
2. Z:\01_Work\01_ComfyUi_Project\COMFYUI_AI_SHORT_DRAMA_MASTER_BIBLE.md
3. Z:\01_Work\01_ComfyUi_Project\02_NAS_Server_And_Deployment\nas_server.py
4. Z:\01_Work\01_ComfyUi_Project\02_NAS_Server_And_Deployment\frontend\index.html

สถานะระบบปัจจุบันที่พร้อมใช้งาน:
- NAS Server (192.168.1.102:5050): รัน Docker FastAPI ให้บริการแดชบอร์ดและบันทึกประวัติค่าไฟลง SQLite ตลอด 24 ชม.
- Client Agents: มีเอเจนต์ส่งวัตต์ไฟจากทั้ง Main PC (192.168.1.100) และ AiPC1 (192.168.1.11)
- AI Studio: เชื่อมต่อ ComfyUI MiniMax H3 (192.168.1.11:8188) พร้อมโมเดลและเอนจินละครสั้น
- ซอร์สโค้ดและโครงสร้างทั้งหมดอยู่ที่ Z:\01_Work\01_ComfyUi_Project\

เป้าหมายในแชทนี้:
[ใส่สิ่งที่คุณต้องการทำต่อ เช่น: "ต้องการเพิ่มเมนูควบคุมอุปกรณ์ Smart Home ในบ้าน", "ต้องการปรับแต่ง UI แดชบอร์ดใหม่", หรือ "ต้องการเพิ่มหน้ารายงานสรุปค่าไฟและอุณหภูมิบ้าน"]
```
