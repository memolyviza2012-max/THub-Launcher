# คู่มือแคตตาล็อกโมเดล AI ล่าสุด & การตั้งค่าใน TStudio และ TRun (AI Models Catalog & Setup Guide)

## 1. บทนำ (Introduction)
เอกสารนี้รวบรวมรายชื่อโมเดล AI ยุคล่าสุด (Frontier, Reasoning, Open-Weights, และ OpenRouter) พร้อมแนวทางการตั้งค่าใช้งานร่วมกับเครื่องมือแปลเกมภาษาไทย **TStudio**, **TRun**, และ **TSub** ในระบบ THub

---

## 2. หมวดหมู่โมเดลและการเลือกใช้งานสำหรับงานแปลเกม (Model Selection by Use Case)

### 🥇 สายคุ้มค่า ประหยัดงบ และแปลมหาศาล (High-Volume Bulk Translation)
* **โมเดลแนะนำ**: `deepseek-chat` (DeepSeek-V3), `deepseek-flash`
* **ข้อดี**: ราคาต่อโทเค็นถูกที่สุดในกลุ่มโมเดลระดับท็อป (ล้านละไม่กี่สตางค์) ความเร็วสูง สำนวนภาษาไทยเป็นธรรมชาติ
* **ข้อควรระวัง**: โมเดล DeepSeek อาจมีคอมเมนต์ภาษาจีนหลุดมาบางครั้ง (ระบบ TStudio และ TRun มีฟิลเตอร์ CJK Leak ช่วยตัดให้อัตโนมัติแล้ว)

### 🥇 สาย DeepSeek เจเนอเรชันใหม่ & วิเคราะห์เชิงลึก (DeepSeek V4 & Reasoning)
* **โมเดลแนะนำ**: `deepseek-v4-pro`, `deepseek-flash`, `deepseek-reasoner` (DeepSeek-R1)
* **สถานะโมเดล DeepSeek V4**: บัญชี API ของผู้ใช้รองรับโมเดล `deepseek-v4-pro` และ `deepseek-flash` โดยตรงจาก endpoint ทางการ (`api.deepseek.com/models`)
* **จุดเด่น**: มีกระบวนการคิดวิเคราะห์ (Reasoning / Chain-of-Thought) ระดับสูง ช่วยให้แปลประโยคกำกวม ซับซ้อน หรือโครงสร้างโค้ดได้แม่นยำยิ่งขึ้น
* **คำแนะนำ**: เนื่องจาก `deepseek-v4-pro` มี Reasoning Tokens ควรกำหนด `Max Tokens` ในหน้า Settings ไว้ที่อย่างน้อย 4096 - 8192 โทเค็น

### 🥇 สายสำนวนวรรณศิลป์ & ซับซ้อนสูง (Narrative & Literary Translation)
* **โมเดลแนะนำ**: `claude-3-7-sonnet-20250219` (Claude 3.7 Sonnet) หรือ `claude-3-5-sonnet-20241022`
* **ข้อดี**: เข้าใจบริบท มุกตลก คำสแลง และอารมณ์ตัวละครได้ดีที่สุดในตลาด ไม่แปลแบบทื่อๆ
* **การตั้งค่า**: รองรับทั้ง Direct API จาก Anthropic หรือเรียกผ่าน OpenRouter (`anthropic/claude-3.7-sonnet`)

### 🥇 สาย Context ขนาดยักษ์ & โหลดคลังศัพท์ทั้งเกม (Massive Lore & Glossary Consistency)
* **โมเดลแนะนำ**: `gemini-2.0-flash` หรือ `gemini-1.5-pro`
* **ข้อดี**: รองรับ Context Window ระดับ 1M ถึง 2M Tokens สามารถยัดคลังคำศัพท์ (Glossary) หลายพันคำพร้อมประวัติศาสตร์เกมลงไปในพรอมต์ได้ทั้งหมดโดยที่โมเดลไม่หลงลืม

### 🥇 สายคิดวิเคราะห์ & ตรรกะแม่นยำ (CoT / Reasoning)
* **โมเดลแนะนำ**: `o3-mini` (OpenAI), `deepseek-reasoner` (DeepSeek-R1), `deepseek-v4-pro`, `gemini-2.0-flash-thinking-exp-01-21`
* **ข้อดี**: มีกระบวนการคิดในหัวก่อนตอบ เหมาะมากกับการถอดรหัสโค้ด, ตรวจสอบความถูกต้องของสคริปต์, หรือแปลประโยคที่มีตัวแปรแทรกซับซ้อน

### 🥇 สายออฟไลน์ / ปลอดภัยในเครื่อง (Local / Offline Translation)
* **โมเดลแนะนำ**: `qwen2.5:14b`, `qwen2.5:32b`, `qwq:32b`, `llama3.3:70b`
* **ข้อดี**: ใช้งานฟรี รันผ่าน Ollama หรือ LM Studio ในเครื่อง ไม่ต้องต่ออินเทอร์เน็ต

---

## 3. ตารางโมเดลย่อย (Sub-Models) ที่มีใน TStudio Settings

| AI Provider (ค่าย) | Model Name (Identifier) | หมายเหตุ / จุดเด่น |
|---|---|---|
| **DeepSeek** | `deepseek-chat` | DeepSeek-V3 โมเดลหลัก แนะนำสำหรับงานแปลทั่วไป |
| | `deepseek-v4-pro` | DeepSeek-V4 Pro โมเดลรุ่นใหม่ล่าสุด รองรับ CoT Reasoning เชิงลึก |
| | `deepseek-flash` | DeepSeek Flash ความเร็วสูง ตอบสนองฉับไว |
| | `deepseek-reasoner` | DeepSeek-R1 โมเดลคิดวิเคราะห์ตรรกะสูง CoT |
| **Google Gemini** | `gemini-2.0-flash` | Gemini 2.0 Flash แนะนำ เร็วมาก 1M Context |
| | `gemini-2.0-flash-lite` | Gemini 2.0 Flash Lite ความเร็วสูงสุด ประหยัดสุด |
| | `gemini-2.0-flash-thinking-exp-01-21` | Gemini 2.0 Flash Thinking โหมดคิดวิเคราะห์ |
| | `gemini-2.0-pro-exp-02-05` | Gemini 2.0 Pro Experimental คุณภาพสูงสุด |
| | `gemini-1.5-pro` | Gemini 1.5 Pro รองรับ 2M Tokens มหาศาล |
| | `gemini-1.5-flash` | Gemini 1.5 Flash เสถียร |
| | `gemini-1.5-flash-8b` | Gemini 1.5 Flash 8B จิ๋วและเร็ว |
| **Anthropic Claude** | `claude-3-7-sonnet-20250219` | Claude 3.7 Sonnet ตัวท็อปล่าสุด Hybrid Reasoning สำนวนยอดเยี่ยมที่สุด |
| | `claude-3-5-sonnet-20241022` | Claude 3.5 Sonnet v2 มาตรฐานงานแปล |
| | `claude-3-5-haiku-20241022` | Claude 3.5 Haiku เร็วและประหยัด |
| | `claude-3-opus-20240229` | Claude 3 Opus รุ่นใหญ่ |
| **OpenAI** | `gpt-4o` | GPT-4o Omni Flagship เร็ว แม่นยำ |
| | `gpt-4o-mini` | GPT-4o mini เร็วและประหยัด |
| | `o3-mini` | o3-mini โมเดลใช้เหตุผลความเร็วสูง |
| | `o1` | o1 โมเดลใช้เหตุผลเต็มรูปแบบ |
| | `o1-mini` | o1-mini |
| | `gpt-4.5-preview` | GPT-4.5 Frontier Preview |
| | `chatgpt-4o-latest` | Dynamic latest ChatGPT |
| **OpenRouter** | `anthropic/claude-3.7-sonnet` | Claude 3.7 ผ่าน OpenRouter |
| | `deepseek/deepseek-chat` | DeepSeek V3 ผ่าน OpenRouter |
| | `deepseek/deepseek-r1` | DeepSeek R1 ผ่าน OpenRouter |
| | `google/gemini-2.0-flash-001` | Gemini 2.0 Flash ผ่าน OpenRouter |
| | `google/gemini-2.0-pro-exp-02-05:free` | Gemini 2.0 Pro Exp Free |
| | `openai/gpt-4o` | GPT-4o ผ่าน OpenRouter |
| | `qwen/qwen-2.5-72b-instruct` | Qwen 2.5 72B |
| | `meta-llama/llama-3.3-70b-instruct` | Llama 3.3 70B |
| **Local LLM** | `qwen2.5:14b` / `qwen2.5:32b` | Ollama Local LLM (พอร์ต 11434) |
| | `qwq:32b` | QwQ Reasoning Local Model |
| | `deepseek-r1:14b` / `8b` | DeepSeek-R1 Local Distill |
| | `llama3.3:70b` | Ollama Llama 3.3 |
| | `custom-local-llm` | LM Studio (พอร์ต 1234) หรือระบุชื่อโมเดลเอง |

---

## 4. วิธีการตั้งค่าและการใช้งานในโปรแกรม (How to Configure & Test)

### 🚀 4.1 แถบควบคุมด้านบนแบบสองระดับ (Top Bar Two-Tier Model Selector)
บนแถบควบคุมหลักด้านบนของ **TStudio Desktop** ได้รับการอัปเกรดให้สามารถเลือกค่ายและโมเดลย่อยได้อย่างสะดวก:
1. **Dropdown ที่ 1: ค่าย AI (Provider Selector)**:
   - เลือกค่ายได้ทันที: `DeepSeek`, `Google Gemini`, `Anthropic Claude`, `OpenAI`, `OpenRouter`, `Local LLM`
2. **Dropdown ที่ 2: โมเดลย่อย (Sub-Model Selector)**:
   - เมื่อสลับค่าย รายชื่อโมเดลย่อยทั้งหมดของค่ายนั้นจะถูกอัปเดตลงใน Dropdown นี้อัตโนมัติ
   - แสดงผลพร้อมคำอธิบาย เช่น `DeepSeek-V4 Pro (Reasoning ตรรกะ)`, `Gemini 2.0 Flash Lite (ประหยัดสุด)`, `Claude 3.7 Sonnet (Hybrid Reasoning)`
3. **ปุ่มสถานะ API (Status Badge Capsule)**:
   - แสดงสถานะทันที เช่น `🟢 DeepSeek ⚙️` หรือ `⚠️ Gemini (ยังไม่มีคีย์) ⚙️`
   - **คลิกที่ปุ่ม**: จะเปิดหน้าต่าง **SettingsDialog (Multi-API Manager)** ทันที
   - **ชี้เมาส์ (Hover)**: แสดงสรุปสถานะคีย์ทุกค่ายและ URL Local LLM

### ⚡ 4.2 ระบบทดสอบ API ทันทีก่อนเริ่มแปล (Interactive API Testing)
ในหน้าต่างการตั้งค่า (`SettingsDialog`) มีระบบทดสอบการเชื่อมต่อแบบ Non-blocking (ไม่ค้างหน้าจอ):
1. **ในแท็บ 1: 🎯 โมเดลหลัก & พารามิเตอร์**:
   - มีปุ่ม **`[ ⚡ ทดสอบโมเดลนี้ ]`** ในกล่องสถานะด้านล่าง
   - เมื่อคลิก ระบบจะทดสอบคีย์และโมเดลที่กำลังเลือกอยู่ทันที พร้อมแสดงผลลัพธ์แบบเรียลไทม์ เช่น `✅ เชื่อมต่อสำเร็จ! DeepSeek API Key ถูกต้อง (พบโมเดล deepseek-flash, deepseek-v4-pro)`
2. **ในแท็บ 2: 🔑 จัดการ API Keys หลายค่าย**:
   - ข้างช่องกรอกคีย์ของทุกค่าย (DeepSeek, Google Gemini, OpenAI, Claude, OpenRouter) จะมีปุ่ม **`[ ⚡ ทดสอบ API ]`**
   - เมื่อกรอกคีย์แล้ว สามารถกดปุ่มนี้เพื่อยิงคำขอเช็กการเชื่อมต่อไปยังเซิร์ฟเวอร์ทางการได้ทันทีโดยไม่ต้องรันคำแปลจริง
   - สำหรับ Local LLM จะมีปุ่ม **`[ ⚡ ทดสอบเชื่อมต่อ ]`** สำหรับ ping หา Ollama หรือ LM Studio ในเครื่อง
   - หากคีย์ถูกต้อง จะขึ้นข้อความสีเขียว `✅ เชื่อมต่อสำเร็จ!` พร้อมจำนวนโมเดลหรือสถานะบัญชี
   - หากคีย์ผิดพลาดหรือเงินหมด จะแจ้งรหัสข้อผิดพลาดอย่างชัดเจน เช่น `❌ 401 Unauthorized` หรือ `❌ 402 Insufficient Balance`
