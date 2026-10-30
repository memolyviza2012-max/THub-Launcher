# คู่มือเทคนิค: สถาปัตยกรรม TLM Studio และความเสถียรของระบบสกัดคำศัพท์ร่วมกับโปรไฟล์เดิม (TLM Extraction & Glossary Stability Guide)

## 1. บทนำและปัญหาที่พบ (Overview & Root Cause Analysis)
เมื่อผู้ใช้งานเรียกใช้ฟังก์ชัน **TLM Studio (Thai Localization Master / LTM)** ในโปรแกรม **TStudio** เพื่อสกัดคำศัพท์และบัญญัติศัพท์ใหม่ (Deep AI Mining) หากในโปรไฟล์ปัจจุบัน (Profile) มีการบันทึก **AI Prompts** หรือ **คลังคำศัพท์ (Glossary)** ไว้ก่อนหน้าแล้ว ระบบจะเกิดข้อผิดพลาด (Error / Crash) หรือทำงานผิดปกติอันเนื่องมาจากสาเหตุดังต่อไปนี้:

1. **โครงสร้างข้อมูล Glossary ไม่เข้ากันกับ Consumer เดิม (IndexError / TypeError)**:
   - ฟังก์ชันต่างๆ ใน `tstudio_app.py` เช่น `_apply_glossary`, `_get_dynamic_glossary`, `update_html_sources`, `on_row_selected`, และ `recheck_qa_for_row` เคยเขียนเข้าถึงค่าคำแปลด้วย `val[0] if isinstance(val, list) else val`
   - หากในไฟล์โปรไฟล์มีคำศัพท์ที่ค่าเป็นรายการว่าง `[]`, ค่า `None`, ค่าที่เป็น string ธรรมดา, หรือโครงสร้างที่ไม่สมบูรณ์ คำสั่ง `val[0]` จะทำให้เกิด `IndexError: list index out of range` ทันที
   - การเรียงลำดับคำศัพท์ `sorted(glossary.items(), key=lambda x: len(x[0]))` หาก key ไม่ใช่ string หรือเกิด type mismatch จะทำให้เกิด `TypeError`

2. **ปัญหาการบล็อกกระบวนการเมื่อไม่มีข้อมูล Lore (Blocking UX)**:
   - ฟังก์ชัน `_start_deep_ai_mining` ใน `tstudio_tlm_studio.py` บล็อกการทำงานด้วยข้อความเตือน "ไม่มีข้อมูลอ้างอิง" หากช่อง Lore Notes หรือ Candidate Entities ว่างเปล่า ทั้งที่ผู้ใช้เปิดไฟล์งานแปลและมีคำศัพท์/บทสนทนาอยู่ในตารางหลักแล้ว

3. **ไม่มีระบบป้องกันคำซ้ำ (Lack of Deduplication & Overwrite Risk)**:
   - AI ใน Deep AI Mining ไม่ได้รับรายการคำศัพท์เดิมที่มีอยู่ในโปรไฟล์ ทำให้ AI ส่งคำศัพท์เดิมที่ผู้ใช้เคยแปลหรือปรับแต่งไว้แล้วกลับมาซ้ำซ้อน
   - เมื่อกดนำเข้า ตาราง Staging Grid จะเลือกทุกแถวเป็น Checked ทำให้อาจเขียนทับคำศัพท์เดิมของผู้ใช้โดยไม่ตั้งใจ

4. **ความไม่ยืดหยุ่นของการแปลง JSON จาก AI (JSON Parsing Fragility)**:
   - โมเดล AI รุ่นใหม่ๆ (เช่น DeepSeek-R1, Qwen, Claude, GPT-4) มักส่งคำตอบครอบด้วย Markdown Codeblocks (` ```json ... ``` `), แท็กคิดวิเคราะห์ (`<think>...</think>`), หรือส่งในรูปแบบ Object ครอบ (`{"terms": [...]}`) แทนที่จะเป็น Flat Array ตรงๆ ทำให้คำสั่ง `json.loads` แครช
   - กรณีที่เกิด Token Cutoff ข้อความ JSON จะถูกตัดกลางคันก่อนปิดเครื่องหมาย `]` ทำให้ระบบเดิมล้มเหลวทันที

5. **ปัญหา DeepSeek Reasoning Trap และ Empty Response (Zero-Byte Content)**:
   - มีการตั้งชื่อโมเดลว่า `deepseek-v4-pro` ซึ่งไม่มีอยู่จริงใน DeepSeek API ทำให้ระบบฝั่งเซิร์ฟเวอร์ของ DeepSeek สลับไปใช้ `deepseek-reasoner` (R1)
   - เมื่อส่ง Prompt ขนาดยาวที่มีทั้ง Glossary เดิม และข้อความ Lore/Candidates โมเดลแบบคิดวิเคราะห์ (Reasoning Model) จะใช้โควตาโทเค็นทั้งหมดไปกับการคิดใน `reasoning_content` (กว่า 20,000 ตัวอักษร) จนชนขีดจำกัดโทเค็น (`finish_reason: "length"`) ส่งผลให้ `content` เป็นค่าว่างเปล่า (0 Bytes) และกลายเป็น Parsing Error ในหน้าต่างสกัดคำศัพท์

6. **บั๊ก Type Mismatch ของค่าคอนฟิกตัวเลข**:
   - ค่า `max_tokens`, `temperature`, `timeout` ในบางโปรไฟล์ถูกบันทึกเป็น String (เช่น `"4096"`) ทำให้คำสั่งเปรียบเทียบใน Python เกิด `TypeError: '<' not supported between instances of 'str' and 'int'`

---

## 2. มาตรการและสถาปัตยกรรมที่ปรับปรุง (Architectural Fixes)

### 2.1 ป้องกันความผิดพลาดใน `tstudio_app.py` (Defensive Consumer Hardening)
ทุกจุดที่มีการเรียกใช้หรือประมวลผล Glossary ใน TStudio ได้รับการอัปเกรดให้มีความปลอดภัยสูงสุด:
- **Safe Value Extraction**:
  ```python
  thai = val[0] if (isinstance(val, list) and len(val) > 0) else val
  thai_str = str(thai or "").strip()
  ```
- **Safe Dictionary & Length Sorting**:
  ```python
  sorted_glossary = sorted(glossary.items(), key=lambda x: len(str(x[0])), reverse=True) if isinstance(glossary, dict) else []
  ```
- **Safe Word Boundary for Symbols**:
  รองรับคำศัพท์ที่มีสัญลักษณ์หน้า-หลัง เช่น `[Boltgun]`, `{0}`, `@tag`:
  ```python
  _prefix = r'\b' if re.match(r'\w', eng_str) else r''
  _suffix = r'\b' if re.search(r'\w$', eng_str) else r''
  pattern = _prefix + r'(' + re.escape(eng_str) + r')' + _suffix
  ```

### 2.2 ระบบตรวจจับและป้องกันคำซ้ำใน TLM Studio (Anti-Duplication Intelligence)
- **AI Prompt Directive**:
  ดึงรายชื่อคำศัพท์เดิมในโปรไฟล์ (สูงสุด 150 คำแรก) ส่งเข้าไปใน Prompt ภายใต้หัวข้อ `### STRICT DEDUPLICATION DIRECTIVE (CRITICAL):` สั่ง AI อย่างเด็ดขาดไม่ให้สกัดคำศัพท์เหล่านี้ซ้ำ
- **Auto Staging Deduplication & Safe Uncheck**:
  เมื่อได้รับผลลัพธ์จาก AI ระบบจะตรวจสอบแบบ Case-Insensitive เปรียบเทียบกับคำศัพท์เดิมในโปรไฟล์และคำศัพท์ที่มีอยู่ใน Staging Grid:
  - หากพบคำซ้ำ จะเติมข้อความแจ้งเตือนใน Context: `(มีคำศัพท์ '...' ในคลังเดิมแล้ว)`
  - ปลด Checkbox เป็น **Unchecked โดยอัตโนมัติ** เพื่อไม่ให้ไปเขียนทับคำศัพท์เดิมเมื่อผู้ใช้กดผสานเข้าโปรไฟล์

### 2.3 ระบบ Auto-Scan อัตโนมัติจากไฟล์งานปัจจุบัน (Smart Fallback)
หากผู้ใช้ไม่ได้พิมพ์ Lore Notes หรือ Candidate Entities แต่เปิดไฟล์งานแปลไว้ในหน้าต่างหลัก (`TranslationStudio`):
- ระบบจะสแกนคำนามเฉพาะจากตารางงานแปล (`self.main_app.model._data`) หรือไฟล์ CSV ล่าสุด (`self.main_app.csv_path`) ให้อัตโนมัติในคลิกเดียว
- หากไม่มีไฟล์งานแปลเปิดอยู่ จะ fallback ดึงรายชื่อคำศัพท์เดิมในโปรไฟล์มาเป็นบริบทอ้างอิงให้ AI ทันที

### 2.4 Resilient JSON Parser & Stream Healing ใน `_handle_ai_mining_result`
- ลบแท็ก `<think>...</think>` ทิ้งก่อนประมวลผล
- รองรับ Markdown codeblock extraction
- **Stream Healing**: หากโมเดลตัดจบก่อนปิด `]` ระบบจะค้นหาเครื่องหมาย `}` สมบูรณ์ตัวสุดท้าย แล้วปิดท้ายด้วย `\n]` เพื่อกู้คืนคำศัพท์ทั้งหมดที่สร้างเสร็จ 100%
- ดึง outermost array `[...]` หรือ outermost dict `{...}`
- ลบ trailing comma ก่อน `]` หรือ `}`
- ทำ Regex fallback สำหรับแยก `{...}` รายตัวหาก JSON โดยรวมไม่สมบูรณ์
- แตก Dict wrapper keys อัตโนมัติ: `terms`, `glossary`, `data`, `items`, `results`, `vocabulary`, `words` หรือแปลง direct key-value map
- รองรับ Fallback จาก Markdown Table (`| English | Thai | ...`) และ Bullet Points (`- Term: Thai`)

### 2.5 ปรับสภาพข้อมูลตอนบันทึกลงโปรไฟล์ (Data Normalization)
ใน `_execute_import_to_profile` ข้อมูลทุกคำจะถูกแปลงให้อยู่ในโครงสร้างมาตรฐาน:
```python
normalized_glossary[k_str] = [t_str, tag_str]
```
รับประกันว่าโปรไฟล์จะไม่มีค่าที่เป็น None, key ว่าง, หรือ structure เสียหายหลุดไปบันทึกลงไฟล์คอนฟิกอย่างเด็ดขาด

### 2.6 ระบบตรวจแก้ชื่อโมเดล DeepSeek และ Type Safety (`tstudio_core.py`)
- **Auto Model Remapping**: แก้ไขการแมปชื่อจาก `deepseek-v4-pro` เป็น `deepseek-chat` (โมเดล DeepSeek-V3 ตัวจริง ไม่ใช่ R1 reasoner) ป้องกันการเผาโทเค็นในขั้นตอน reasoning
- **Reasoning Content Recovery**: หากโมเดลคืนค่า `content` เป็นค่าว่างแต่มี `reasoning_content` ระบบจะพยายามค้นหา JSON ภายใน reasoning หรือแจ้งเตือนภาษาไทยที่อ่านเข้าใจง่าย
- **Strict Type Casting**: แปลงค่า `max_tokens`, `temperature`, `timeout` เป็น `int` / `float` อย่างปลอดภัย ป้องกัน `TypeError` จากข้อมูลที่เป็นสตริง

---

## 3. สรุปผลการทดสอบ (Verification & Validation)
ผ่านชุดการทดสอบบูรณาการระดับระบบ (Automated Integration Test Suite):
1. **Dialog Initialization**: โหลดโปรไฟล์เดิมที่มีทั้ง AI Prompt และ Glossary รูปแบบต่างๆ สำเร็จ 100%
2. **Anti-Duplication & Auto-Scan**: สแกนคำนามเฉพาะจากไฟล์งานอัตโนมัติ และป้องกันคำซ้ำได้ถูกต้อง
3. **AI Result Parsing & Duplicate Safety**: ตรวจจับคำซ้ำ ยกเลิกการเลือกเป็น Unchecked ป้องกันการเขียนทับได้แม่นยำ
4. **TStudio Consumers**: การทำงานของ Highlight, Chips, QA Check, Auto-Translate ไม่พบข้อผิดพลาดหรืออาการแครช
