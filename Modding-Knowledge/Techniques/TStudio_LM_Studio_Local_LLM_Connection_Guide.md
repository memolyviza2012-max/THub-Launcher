# คู่มือการเชื่อมต่อ TStudio กับ LM Studio (Local LLM Integration Guide)

เอกสารนี้สรุปวิธีการเชื่อมต่อ **TStudio** เข้ากับ **LM Studio** เพื่อใช้งานโมเดลแปลภาษาฟรีแบบออฟไลน์ (Local LLM) โดยตรงจากการ์ดจอในเครื่อง ไม่ต้องต่อเน็ต และไม่เสียค่าบริการ API

---

## 1. จุดสังเกตของพอร์ตและค่าเริ่มต้น (Port Differences)

| โปรแกรม Local LLM | พอร์ตมาตรฐาน (Default Port) | Endpoint URL |
| :--- | :--- | :--- |
| **LM Studio** | **`:1234`** | `http://localhost:1234/v1/chat/completions` |
| **Ollama** | **`:11434`** | `http://localhost:11434/v1/chat/completions` |

> [!IMPORTANT]
> สาเหตุที่ก่อนหน้านี้ขึ้นแจ้งเตือน `Could not connect to Local LLM at http://localhost:11434/...` เนื่องจากระบบตั้งค่าพอร์ตเริ่มต้นไว้ที่ `11434` (ของ Ollama) แต่ตัว **LM Studio** ของผู้ใช้ทำงานอยู่ที่พอร์ต **`1234`**

---

## 2. ขั้นตอนการตั้งค่าใน LM Studio
1. เปิด **LM Studio** ไปที่แท็บ **Developer (Local Server)**
2. ตรวจสอบว่าได้กดเปิด **Status: Running** (ปุ่มเขียวเปิดอยู่)
3. ตรวจสอบว่าโมเดลได้โหลดเข้าสู่หน่วยความจำแล้ว (เช่น `qwen2.5-coder-32b-instruct`)
4. พอร์ตที่ LM Studio แสดงจะเป็น `http://localhost:1234` หรือ `http://192.168.1.100:1234`

---

## 3. ขั้นตอนการตั้งค่าใน TStudio
1. กดคีย์ลัด **`Ctrl+I`** (หรือกดปุ่ม ⚙️) เพื่อเปิดหน้าต่าง **Settings**
2. ใน **แถบที่ 1 (Active Model & Parameters)**:
   - **Provider**: เลือก `Local LLM`
   - **Model Name**: เลือก `qwen2.5-coder-32b-instruct` (หรือพิมพ์เอง)
   - **Base API URL**: ใส่ `http://localhost:1234/v1/chat/completions`
   - **Batch Concurrency**: แนะนำตั้งไว้ที่ `2-4` เธรด (ขึ้นอยู่กับ VRAM ของการ์ดจอ)
3. ใน **แถบที่ 2 (API Keys & Local Setup)**:
   - ที่หัวข้อ **Local LLM Settings** สามารถกดปุ่ม **`⚡ LM Studio (:1234)`** เพื่อให้ระบบใส่ URL อัตโนมัติได้
   - กดปุ่ม **`⚡ ทดสอบเชื่อมต่อ`** เพื่อตรวจสอบสถานะ
4. กด **บันทึก (Save)**

---

## 4. ผลการทดสอบ (Verification)
- ทดสอบส่งคำสั่งแปลภาษาผ่าน `http://localhost:1234/v1/chat/completions` ไปยังโมเดล `qwen2.5-coder-32b-instruct` บนเครื่อง
- โมเดลตอบกลับภาษาไทยอย่างถูกต้อง รวดเร็ว (ใช้เวลาเฉลี่ย ~1-2 วินาที)
- ซิงก์การแก้ไขไปยัง `tools/flagship/Core/` และ `dist/THub/_internal/` เรียบร้อยแล้ว
