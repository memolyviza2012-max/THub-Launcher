# คู่มือการเชื่อมต่อ LM Studio และระบบสลับโมเดล AI บนแถบด้านบน (TStudio Model Switching & Local LLM Guide)

เอกสารรวบรวมองค์ความรู้ด้านสถาปัตยกรรมและการใช้งานระบบ **AI Provider & Model Selector** บน TStudio ครอบคลุมทั้งการเชื่อมต่อ **LM Studio (Local LLM)** และการสลับโมเดลผ่านแถบด้านบน (Top Toolbar)

---

## 1. การเชื่อมต่อ LM Studio กับ TStudio (Local LLM Setup)

### พอร์ตมาตรฐาน (Default Port)
| ระบบ | พอร์ตเริ่มต้น | Endpoint URL |
| :--- | :--- | :--- |
| **LM Studio** | **`:1234`** | `http://localhost:1234/v1/chat/completions` |
| **Ollama** | **`:11434`** | `http://localhost:11434/v1/chat/completions` |

### ขั้นตอนตั้งค่า
1. เปิด **LM Studio** -> ไปที่แท็บ **Developer / Local Server** -> กด **Start Server** (สถานะสีเขียว)
2. โหลดโมเดลที่ต้องการใช้งาน เช่น `qwen2.5-coder-32b-instruct`
3. ใน TStudio:
   - เลือก **Provider** บนแถบด้านบนเป็น `Local LLM`
   - เลือก **Model** เป็น `qwen2.5-coder-32b-instruct` หรือโมเดลที่โหลดไว้
   - หากเชื่อมต่อครั้งแรก สามารถกดปุ่ม **⚙️** (หรือ `Ctrl+I`) ตรวจสอบว่า **Local LLM URL** ตั้งเป็น `http://localhost:1234/v1/chat/completions`

---

## 2. การสลับโมเดลผ่านแถบด้านบน (Top Bar Model Selector)

### ฟีเจอร์และการทำงาน
1. **คัดกรองโมเดลตามค่าย (Dynamic Filtering by Provider)**:
   - เมื่อเปลี่ยนค่าย (Provider) ในช่องแรก รายการในช่องเลือกโมเดลจะอัปเดตตรงตามค่ายนั้นทันที
   - หากโมเดลที่ใช้งานอยู่เป็นโมเดลของค่ายที่เลือก ระบบจะรักษาโมเดลเดิมไว้ ไม่บังคับรีเซ็ตกลับเป็นตัวแรก
2. **ปุ่มใส่ชื่อโมเดลเอง (✏️ Custom Model Input)**:
   - ทุกค่ายจะมีตัวเลือก `✏️ กำหนดชื่อโมเดลเอง (Custom)...`
   - เมื่อเลือก ระบบจะเปิดหน้าต่างป๊อปอัปให้พิมพ์ชื่อโมเดล (เช่น โมเดล LoRA, Fine-tuned, หรือโมเดล LM Studio อื่นๆ) แล้วจะเพิ่มลงในเมนูและบันทึกใช้งานทันที
3. **ป้ายกำกับปุ่มแปลปรับตามโมเดลจริง (Dynamic Button Labels)**:
   - ปุ่ม **แปลบรรทัดนี้ (Smart)** และปุ่ม **แปลทั้งชุด (Batch)** จะแสดงชื่อย่อของโมเดลที่เลือกอยู่ เช่น:
     - `💻 แปลด้วย Qwen 2.5 Coder 32B`
     - `🤖 แปลด้วย DeepSeek-R1`
     - `🤖 แปลด้วย GPT-4o Mini`
   - ทำให้ผู้ใช้งานทราบได้ทันทีว่าคลิกแล้วจะส่งคำขอไปยังโมเดลใด
4. **Badge แสดงสถานะและชื่อโมเดล (Status Badge)**:
   - แสดงสถานะการเชื่อมต่อพร้อมชื่อย่อของโมเดล เช่น `🟢 Local LLM › Qwen 2.5 Coder 32B ⚙️`

---

## 3. สถาปัตยกรรมการแยกเส้นทางคำขอ (API Endpoint Routing Isolation)

### ปัญหาเดิมที่ได้รับการแก้ไข
- เดิมที เมื่อผู้ใช้บันทึกการตั้งค่า Local LLM ค่า URL ของ localhost (`http://localhost:1234/...`) จะถูกบันทึกทับลงในช่อง `base_url` ทำให้เมื่อผู้ใช้สลับกลับไปใช้ค่าย Cloud (เช่น DeepSeek, OpenAI, Gemini) คำขอทั้งหมดถูก Redirect ไปยัง localhost และเกิดข้อผิดพลาด
- โมเดล Local LLM เดิมทีถูกฮาร์ดโค้ดเป็น `"local-model"` ในแกนประมวลผล ทำให้ไม่สามารถส่งชื่อโมเดลเฉพาะเจาะจงไปยัง LM Studio ได้

### สถาปัตยกรรมใหม่ (Architectural Safeguards)
1. **Local Base URL Isolation**:
   - `CoreAI.generate_content` มีระบบตรวจสอบอัตโนมัติ หากตรวจพบ `base_url` เป็น `localhost`, `127.0.0.1`, `:1234`, หรือ `:11434` ระบบจะนำไปใช้เฉพาะกับ **Local LLM** เท่านั้น และจะไม่ยอมให้ดักจับหรือเปลี่ยนเส้นทางของค่าย Cloud API อย่างเด็ดขาด
2. **Model Preservation**:
   - ไม่มีการลบหรือเขียนทับชื่อโมเดลด้วย `"custom-local-llm"` หรือ `"local-model"` โดยพลการ ระบบจะส่งชื่อโมเดลที่ผู้ใช้เลือก (เช่น `qwen2.5-coder-32b-instruct`) ตรงไปยัง API ของ LM Studio เพื่อให้ LM Studio โหลดและจับคู่ Context ได้ถูกต้อง
3. **Settings Dialog Sanitization**:
   - หน้าต่าง Settings ไม่นำ `local_url` ไปเขียนทับช่อง `base_url` อีกต่อไป โดยแยกตัวแปรการตั้งค่าออกจากกันอย่างอิสระ 100%

---

## 4. โมเดลแนะนำสำหรับการแปลเกมภาษาไทย (2025-2026 Recommended Models)

| โมเดล | ค่าย | ประเภท | จุดเด่น | สเปกฮาร์ดแวร์แนะนำ |
| :--- | :--- | :--- | :--- | :--- |
| **Qwen 2.5 Coder 32B Instruct** | Alibaba | Local (LM Studio) | แปลบริบทเกม เก็บไวยากรณ์และโครงสร้างโค้ด/แท็กเกม (`{0}`, `<color>`) ได้ยอดเยี่ยมที่สุด | RTX 4080 (16GB) / RTX 3090 (24GB) |
| **Qwen 2.5 14B Instruct** | Alibaba | Local (LM Studio) | น้ำหนักเบา ความเร็วสูงมาก แปลภาษาไทยลื่นไหล | RTX 4060 / 4070 (8-12GB VRAM) |
| **DeepSeek-V3 (`deepseek-chat`)** | DeepSeek | Cloud API | แม่นยำ ฉลาด คุ้มค่าที่สุด (ถูกกว่าโมเดลอื่น 10 เท่า) | ใช้งานผ่านเน็ต (ไม่เปลืองสเปก) |
| **DeepSeek-R1 (`deepseek-reasoner`)** | DeepSeek | Cloud API | เหมาะกับประโยคปรัชญา กลอน หรือสำนวนเกมซับซ้อน (Chain-of-Thought) | ใช้งานผ่านเน็ต |
