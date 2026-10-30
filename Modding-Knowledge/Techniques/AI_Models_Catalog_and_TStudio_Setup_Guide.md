# Walkthrough: การเลือกโมเดลย่อย (Sub-Models), ปุ่มทดสอบ API, และการรองรับ DeepSeek V4

เราได้พัฒนาและอัปเกรดระบบการจัดการ AI ใน **TStudio** และ **Multi-API Manager** ครบถ้วนทั้ง 3 ประเด็นตามความต้องการของผู้ใช้:

---

## 1. ผลการทดสอบและข้อเท็จจริงเกี่ยวกับ DeepSeek V4
> [!IMPORTANT]
> **ข้อเท็จจริงเกี่ยวกับ DeepSeek V4 บนบัญชีของคุณ:**
> - เราได้ทำการส่งคำขอตรวจสอบโมเดลไปยัง official endpoint ของ DeepSeek (`https://api.deepseek.com/models`) ด้วย API Key ของคุณ
> - **ผลลัพธ์พบว่ามีโมเดลจริงในระบบ:**
>   - `deepseek-v4-pro` (โมเดลคิดวิเคราะห์ตรรกะขั้นสูง CoT Reasoning)
>   - `deepseek-flash` (โมเดลความเร็วสูง)
> - เมื่อทดสอบการเรียกใช้งานจริง `deepseek-v4-pro` ตอบกลับ HTTP 200 พร้อมผลการคิดเชิงเหตุผล (Reasoning Content)
> - **การแก้ไขในระบบ:**
>   - ปลดล็อกการ Remap ใน [tstudio_core.py](file:///E:/Mod_Workspace/Modder_project/modder-hub/tools/flagship/Core/tstudio_core.py) เพื่อให้ `deepseek-v4-pro` และ `deepseek-flash` ใช้งานได้โดยตรง
>   - เพิ่มเข้าสู่รายการโมเดลอย่างเป็นทางการ ทั้งบนแถบ Top Bar และใน Settings Dialog

---

## 2. แถบควบคุมด้านบนแบบ 2 ระดับ: เลือกค่าย + เลือกโมเดลย่อย (Sub-Models)

บนแถบควบคุมหลักด้านบน (Unified Top Bar) ได้รับการปรับโครงสร้างใหม่เป็นแบบสองระดับเชื่อมโยงกันอย่างชาญฉลาด:

![TStudio Top Bar Sub-Models Preview](docs/images/tstudio_topbar_v4_preview.png)

1. **`[ 🏢 AI Provider Dropdown ]`**: เลือกค่ายผู้ให้บริการ (`DeepSeek`, `Google Gemini`, `Anthropic Claude`, `OpenAI`, `OpenRouter`, `Local LLM`)
2. **`[ 🤖 Sub-Model Dropdown ]`**: รายการโมเดลย่อยจะอัปเดตตามค่ายที่เลือกทันที เช่น:
   - **DeepSeek**: `DeepSeek-V3`, `DeepSeek-V4 Pro`, `DeepSeek Flash`, `DeepSeek-R1`
   - **Google Gemini**: `Gemini 2.0 Flash`, `Gemini 2.0 Flash Lite`, `Gemini 2.0 Flash Thinking`, `Gemini 2.0 Pro Exp`, `Gemini 1.5 Pro`, `Gemini 1.5 Flash`
   - **Anthropic Claude**: `Claude 3.7 Sonnet`, `Claude 3.5 Sonnet v2`, `Claude 3.5 Haiku`, `Claude 3 Opus`
   - **OpenAI**: `GPT-4o`, `GPT-4o mini`, `o3-mini`, `o1`, `o1-mini`, `GPT-4.5 Preview`
   - **OpenRouter**: รวมโมเดลผ่าน OpenRouter
   - **Local LLM**: `Qwen 2.5 (14B/32B/Coder)`, `QwQ 32B`, `DeepSeek R1 Local`, `Llama 3.3`
3. **`[ 🟢 Status Capsule ⚙️ ]`**: แสดงสถานะคีย์ของค่ายที่ใช้งานอยู่ คลิกเพื่อเปิดหน้าต่างตั้งค่า Multi-API ได้ทันที

---

## 3. ปุ่ม "⚡ ทดสอบ API" ก่อนเริ่มแปล (Interactive API Testing)

เพิ่มระบบทดสอบการเชื่อมต่อแบบ Asynchronous (ไม่ทำให้โปรแกรมค้าง) ทั้งใน **แท็บ 1** และ **แท็บ 2**:

### แท็บ 1: ทดสอบโมเดลที่เลือกใช้งานทันที
![Settings Dialog Tab 1](docs/images/settings_dialog_v4_tab1.png)
- มีปุ่ม **`[ ⚡ ทดสอบโมเดลนี้ ]`** ในแถบสถานะด้านล่าง
- ตรวจสอบการเชื่อมต่อของค่ายและโมเดลที่ตั้งค่าไว้แบบทันที

### แท็บ 2: ทดสอบ API Key ทุกค่ายแยกรายแถว
![Settings Dialog Tab 2](docs/images/settings_dialog_v4_tab2.png)
- แต่ละค่ายมีปุ่ม **`[ ⚡ ทดสอบ API ]`** (และสำหรับ Local LLM มีปุ่ม **`[ ⚡ ทดสอบเชื่อมต่อ ]`**)
- ส่งคำขอไปยัง Endpoint ทางการเพื่อเช็กความถูกต้องของคีย์และสิทธิ์การเข้าถึง
- แสดงผลลัพธ์ชัดเจน:
  - `✅ เชื่อมต่อสำเร็จ! DeepSeek API Key ถูกต้อง (พบโมเดล deepseek-flash, deepseek-v4-pro)`
  - หรือหากผิดพลาดจะขึ้นรายละเอียด เช่น `❌ 401 Unauthorized` / `❌ 402 Insufficient Balance`

---

## 4. ปรับปรุงการเลือกโมเดลย่อย (Sub-Model Dropdown) ในหน้าต่างตั้งค่า

> [!TIP]
> **ปัญหาเดิม:** เมื่อคลิกที่ช่อง `2. 🤖 Model Name (ชื่อโมเดล)` ในหน้าต่าง Settings ระบบเปิดให้พิมพ์ข้อความ (Text Box Cursor) แทนที่จะมีแท็บดรอปดาวน์รายการกางออกมาให้เลือก
>
> **การแก้ไข:**
> 1. เปลี่ยน `cbo_model` ให้เป็น **Dropdown แท้ (`setEditable(False)`)** พร้อมแสดงสัญลักษณ์หัวลูกศรชี้ลง `▾` และเปลี่ยน Cursor เป็นรูปมือ (Pointing Hand) ให้คลิกตรงไหนของช่องก็กางลิสต์โมเดลย่อยออกมาทันที
> 2. เพิ่มปุ่ม **`[ ✏️ พิมพ์เอง ]`** ด้านขวา และตัวเลือก **`✏️ กำหนดชื่อโมเดลเอง (Custom)...`** ในรายการ เพื่อให้ผู้ใช้ที่ต้องการกรอกชื่อโมเดลเฉพาะทางยังสามารถระบุได้ตามต้องการผ่านหน้าต่างป๊อปอัป
> 3. ขยายขนาดหน้าต่างเป็น `620x540` เพื่อให้แสดงชื่อโมเดลและคำอธิบายภาษาไทยได้อย่างครบถ้วน ไม่ตกหล่น

> [!NOTE]
> **เกี่ยวกับโมเดล `deepseek-chat`:**
> - `deepseek-chat` **ไม่ได้หายไปไหนและยังคงเป็นโมเดลหลักเริ่มต้นของระบบ**
> - ในเอกสาร API อย่างเป็นทางการของ DeepSeek ตัวระบุโมเดล (Model ID) ของ **DeepSeek-V3** คือคำว่า `deepseek-chat` ตรงๆ นั่นเอง (เป็นโมเดลที่เร็ว ฉลาด และประหยัดค่าใช้จ่ายที่สุดในปัจจุบัน)
> - เพื่อป้องกันความสับสน เราได้ปรับข้อความกำกับใน Dropdown ให้ระบุชื่อชัดเจนขึ้นเป็น:
>   - **`deepseek-chat (DeepSeek-V3 แนะนำ/ประหยัดสุด)`**
>   - **`deepseek-reasoner (DeepSeek-R1 ตรรกะ CoT)`**
> - ขยายขนาดความกว้างของเมนูดรอปดาวน์เป็น 360px เพื่อให้แสดงข้อความทั้งหมดได้อย่างคมชัด ไม่ถูกตัดตัวอักษร

![DeepSeek Chat Selected Preview](docs/images/settings_deepseek_chat_preview.png)

---

## 5. จัดอันดับ "โมเดลที่ดีและคุ้มค่าที่สุด (Best Value & Most Economical)" ไว้เป็นอันดับ 1 ของทุกค่าย

ตามความต้องการของผู้ใช้ เราได้ทำการจัดลำดับโมเดลใน Dropdown ของทุกค่ายใหม่ทั้งหมด โดยนำโมเดลที่ **"คุณภาพการแปลดีเยี่ยมที่สุด และค่าใช้จ่ายประหยัดที่สุด (คุ้มค่าเทียบเท่า DeepSeek-V3)"** มาเป็นตัวเลือกแรกสุด (Index 0) ของแต่ละค่ายทันทีที่ผู้ใช้กดสลับค่าย:

| ค่ายผู้ให้บริการ (AI Provider) | 🥇 โมเดลอันดับ 1 (แนะนำ/ประหยัดสุด) | ราคาโดยประมาณ (Input / Output ต่อ 1M Tokens) | จุดเด่นสำหรับงานแปลเกม |
| :--- | :--- | :--- | :--- |
| **DeepSeek** | **`deepseek-chat` (DeepSeek-V3)** | **~$0.14 / $1.10** | คุ้มค่าที่สุด ฉลาด เทียบชั้นโมเดลชั้นนำโลก |
| **Google Gemini** | **`gemini-2.0-flash`** | **$0.10 / $0.40** (มี Free Tier 15 RPM) | ถูกและเร็วมาก บริบท 1M tokens แปลเกมยาวๆ ได้ลื่นไหล |
| **OpenAI** | **`gpt-4o-mini`** | **$0.15 / $0.60** | โมเดลประหยัดที่สุดของ OpenAI ประสิทธิภาพใกล้เคียง GPT-4o |
| **Anthropic Claude** | **`claude-3-5-haiku`** | **$0.80 / $4.00** | ราคาถูกกว่า Sonnet ถึง 4 เท่า สละสลวยฉบับ Claude |
| **OpenRouter** | **`deepseek/deepseek-chat`** | **~$0.14 / $1.10** | ตัวเลือกที่ดีและประหยัดที่สุดบนเครือข่าย OpenRouter |
| **Local LLM (Ollama)** | **`qwen2.5:14b`** | **ฟรี 100% (ออฟไลน์)** | Sweet Spot แปลไทยดีที่สุด ทำงานได้บนการ์ดจอ VRAM 10-12GB |

![Google Gemini Flash Preview](docs/images/settings_gemini_flash_preview.png)

---

## 6. สรุปไฟล์ที่ได้ทำการซิงก์เรียบร้อยแล้ว
- Source Code:
  - `tools/flagship/Core/tstudio_core.py`
  - `tools/flagship/Core/tstudio_ui_shared.py`
  - `tools/flagship/TStudio/tstudio_app.py`
- Production Dist (`dist/THub/_internal/`):
  - `dist/THub/_internal/tstudio_core.py`
  - `dist/THub/_internal/tstudio_app.py`
  - `dist/THub/_internal/tools/flagship/Core/tstudio_core.py`
  - `dist/THub/_internal/tools/flagship/Core/tstudio_ui_shared.py`
  - `dist/THub/_internal/tools/flagship/TStudio/tstudio_app.py`
- Modding Knowledge:
  - `E:\Mod_Workspace\Modding-Knowledge\Techniques\AI_Models_Catalog_and_TStudio_Setup_Guide.md`
  - `E:\Mod_Workspace\Modding-Knowledge\Techniques\AI_Modding\AI_Models_Catalog_and_TStudio_Setup_Guide.md`
