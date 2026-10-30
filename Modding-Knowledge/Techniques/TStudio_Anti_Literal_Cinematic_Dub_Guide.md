# คู่มือเทคนิคการแปลขจัดสำนวนฝรั่ง & พากย์ไทยภาพยนตร์ (Cinematic War Dub & Anti-Literal Guide)

> **หมวดหมู่:** Techniques / AI_Modding / Localization  
> **ซอฟต์แวร์:** TStudio & TLM Studio (Modder Hub Flagship)  
> **แก้ไขล่าสุด:** กันยายน 2026  
> **ใช้ได้กับ:** Wolfenstein, Dishonored, Metro, Cyberpunk, Warhammer และเกมแอ็กชัน/สงครามทุกประเภท

---

## 1. ที่มาและปัญหาการแปลตรงตัว (The Literal Translation Trap)

ในการแปลเกมเนื้อเรื่องเข้มข้นหรือเกมสงคราม (เช่น **Wolfenstein: The New Order**, **Dishonored**) บ่อยครั้งที่ AI ทั่วไปจะติดกับดักการแปลแบบ **"คำต่อคำ (Word-for-Word)"** และ **สำนวนแปลฝรั่งแข็งกระด้าง (Translationese)** ส่งผลให้อารมณ์ของเกมเสียไปอย่างสิ้นเชิง เช่น:

| ข้อความต้นฉบับ (English Source) | แปลตรงตัวแบบเดิม (Stiff & Literal ❌) | แปลแบบพากย์ไทยภาพยนตร์ (Cinematic Dub ✅) |
| :--- | :--- | :--- |
| *"And I'll be damned if I will let some Jerry come here..."* | *"และฉันจะถูกสาปถ้าฉันปล่อยให้พวกเจอร์รี่มาที่นี่..."* | *"และฝันไปเถอะว่าฉันจะยอมให้พวกนาซีมาเหยียบถิ่นเรา..."* |
| *"Even as the enemy stands at our doorstep..."* | *"แม้ศัตรูจะยืนอยู่ที่ธรณีประตูของเรา..."* | *"ต่อให้ศัตรูบุกมาจ่อคอหอยอยู่หน้าบ้านเรา..."* |
| *"The RAF will go to hell and back to kick them out"* | *"กองทัพอากาศจะไปนรกและกลับมาเพื่อเตะพวกเขาออกไป"* | *"RAF จะบุกน้ำลุยไฟพลิกแผ่นดินเพื่อไล่ตะเพิดพวกมัน"* |
| *"The Americans are on their knees"* | *"พวกอเมริกันคุกเข่าอยู่"* | *"พวกอเมริกันจนตรอกแล้ว / ศิโรราบแล้ว"* |
| *"The RAF were forced to retreat"* | *"กองทัพอากาศถูกบังคับให้ถอยหลัง"* | *"RAF จำต้องล่าถอย / ต้องถอยร่น"* |
| *"Bite the bullet"* | *"กัดกระสุน"* | *"กัดฟันสู้ / จำใจกลืนเลือด"* |

---

## 2. ฟังก์ชันใหม่ในระบบ TLM Studio (สำหรับการสร้าง LMT / Prompt)

เพื่อป้องกันไม่ให้เกิดปัญหานี้ตั้งแต่ขั้นตอนเริ่มต้นวางแผนทำ Mod ระบบ TLM Studio ได้รับการอัปเกรดดังนี้:

### 2.1 ปรัชญาการแปลใหม่ (Translation Philosophy)
ใน **Tab 1: ปรัชญาการแปล (Translation Philosophy)** ได้เพิ่มตัวเลือก:
- **`🎬 พากย์ไทยภาพยนตร์ & ขจัดสำนวนฝรั่ง (Cinematic War Dub - ไม่แปลตรงตัว แปลเอาอารมณ์ ภาษาพูดธรรมชาติ)`**

### 2.2 ปุ่ม Quick Rule ฉีดกฎเหล็กในคลิกเดียว
ในแถบเครื่องมือ Quick Rules ได้เพิ่มปุ่มสีทอง:
- **`🎬 ไม่แปลตรงตัว / พากย์ไทยภาพยนตร์`**
- เมื่อกดปุ่ม ระบบจะฉีดกฎเหล็ก Anti-Literal ที่มีตัวอย่างเปรียบเทียบชัดเจน (I'll be damned, doorstep, hell and back, on their knees, Jerry/Kraut, passive voice) เข้าสู่ช่อง Custom Rules ทันที

### 2.3 แม่แบบ Prompt สำเร็จรูปใน Tab 2
ในเมนู **"📚 โหลดแม่แบบ (Templates)..."** ของหน้า AI Prompt Studio:
- **`2. 🎬 Cinematic War Dub & Anti-Literal (พากย์ไทยภาพยนตร์ ขจัดสำนวนฝรั่ง)`**  
  โหลดโครงสร้าง Prompt ที่สั่ง AI สวมบทบาทนักเขียนบทพากย์หนังฮอลลีวูดมืออาชีพ พร้อมข้อยกเว้นชื่อปืน/ยุทโธปกรณ์แบบสากล

### 2.4 One-Click Easy Mode ฉลาดขึ้น
เมื่อเปิด Easy Mode หากระบบตรวจพบว่าเป็นเกมแอ็กชัน สงคราม ดีเซลพังก์ หรือสตรีท (เช่น Wolfenstein, Dishonored, Battlefield) ระบบจะ **เลือกปรัชญา Cinematic War Dub และฉีดกฎ Anti-Literal ให้อัตโนมัติ 100%**

---

## 3. ฟังก์ชันใหม่ใน TStudio Editor (สำหรับขัดเกลาไฟล์เดิม)

สำหรับไฟล์ที่แปลไปแล้ว เช่น `english_strings_step4.csv` ใน Wolfenstein:

### 3.1 ปุ่ม "🎬 ขัดเกลาภาษาพูด" (Cinematic Polish)
- **ตำแหน่ง:** แถบคำสั่งย่อย (Panel 3 Sub-Action Bar) และคลิกขวาในตาราง
- **คีย์ลัด:** `Ctrl+Shift+P`
- **การทำงาน:** 
  1. เลือกแถวที่ต้องการ (เลือกแถวเดียว หรือคลุมดำหลายสิบแถวได้)
  2. กดปุ่ม `🎬 ขัดเกลาภาษาพูด` หรือกด `Ctrl+Shift+P`
  3. AI จะนำข้อความภาษาอังกฤษต้นฉบับ + คำแปลเดิม มาเขียนใหม่ให้เป็นภาษาพูดธรรมชาติที่ดุดัน สละสลวย ขจัดคำว่า *"ถูก..."*, *"ทำการ..."*, *"ฉันจะถูกสาปถ้า..."* โดยคงตัวแปรและแท็กเกมไว้อย่างแม่นยำ

---

## 4. โปรไฟล์สำเร็จรูป: Wolfenstein: The New Order

ระบบได้บรรจุ Preset โปรไฟล์ `Wolfenstein: The New Order` เข้าสู่คลัง `prompts.json` เรียบร้อยแล้ว:
- **Tone:** Dieselpunk & Alternate History / ดีเซลพังก์ สงครามโลกสมมติ
- **Pronouns:** 🪖 ทหารยุทธวิธี / สายลุย / ตำรวจ (ผม/ฉัน - นาย/พวกนาย/ผู้หมวด)
- **Lore Context:** กองทัพนาซีชนะสงครามด้วย Da'at Yichud, บี.เจ. บลาซโกวิกซ์, ขบวนการกบฏไครเซา (Kreisau Circle)
- **Weapons & Vehicles Guard:** คงรหัสปืน MP40, STG44, Flak 88, Panzerhund, Kampfhund, Laserkraftwerk, RPG, SMG ไว้ตามมาตรฐานสากล

---

## 5. ระบบคุ้มครองปุ่มคีย์บอร์ดและคอนโทรลเลอร์ (Keyboard & Controller Input Protection)

### 5.1 ปัญหาการแปลงปุ่มเพี้ยน (Key Transliteration & Literal Hallucination)
ในการแปลส่วน UI การตั้งค่าปุ่ม (Key Bindings) และข้อความแนะนำในเกม (Tutorial Hints) AI มักจะเกิดปัญหา 2 แบบ:
1. **ทับศัพท์สัทอักษรผิดเพี้ยน:** `Spacebar` ➔ `สเปคบรา`, `Enter` ➔ `เอ็นเทอ` / `เอนเทอร์`, `Backspace` ➔ `แบ็กสเปซ`, `Caps Lock` ➔ `แคปส์ล็อก`, `Esc` ➔ `เอสเคป`
2. **แปลตรงตัวจนเสียความหมาย:** `Space` ➔ `เว้นวรรค`, `Enter (Keypad)` ➔ `ป้อน (แป้นตัวเลข)`, `INS (Keypad)` ➔ `แทรก (แป้นตัวเลข)`, `END (Keypad)` ➔ `จบ (แป้นตัวเลข)`, `Pause` ➔ `หยุดชั่วคราว`

### 5.2 สาเหตุเชิงลึกใน Pipeline
เมื่อ AI แปลงชื่อปุ่มเป็นตัวอักษรละติน (เช่น `Spacebar`, `Enter`) ระบบตรวจจับภาษาอังกฤษรั่วไหล (English Leak Filter) เดิมจะมองว่าเป็นคำภาษาอังกฤษที่ยังไม่ได้แปล จึงกระตุ้นคำสั่ง **Retry** และบังคับ AI ว่า *"ห้ามมีภาษาอังกฤษหลงเหลือ ให้แปลหรือทับศัพท์เป็นภาษาไทย 100%"* ส่งผลให้ AI ฝืนทับศัพท์เสียงกลายเป็น "สเปคบรา" และ "เอ็นเทอ"

### 5.3 กลไกการป้องกันแบบเบ็ดเสร็จ (Permanent Triple-Layer Solution)
ระบบได้รับการแก้ไขถาวรใน 3 ระดับ:
1. **Prompt Matrix Whitelist:**
   - ระบุข้อยกเว้นชัดเจนใน Single Prompt, Options Prompt และ Batch Prompt ของทั้ง TStudio, TRun และ TLM Studio ให้คงชื่อปุ่มมาตรฐานในอักษรละตินสากล (`Spacebar`, `Enter`, `Shift`, `Ctrl`, `Alt`, `Tab`, `Esc`, `Backspace`, `Delete`, `WASD`, `LMB`, `RMB`)
2. **TRun English Leak Whitelist:**
   - บรรจุคำศัพท์ปุ่มกด เมาส์ และคอนโทรลเลอร์ทั้งหมดลงใน `COMMON_ALLOWED_GAMING_ACRONYMS` ของ `TStudioCore` เพื่อให้ระบบ Leak Filter อนุญาตให้มีปุ่มกดเหล่านี้ในผลลัพธ์ได้โดยไม่สั่ง Retry ผิดพลาด
3. **Zero-Token Terminology Retrofit Engine (สแกนซ่อมแซม 0 Token):**
   - ใน `TStudioCore.retrofit_military_text` เพิ่มหมวดหมู่ `'keys': True`
   - ในกล่องเครื่องมือ `MilitaryTerminologyRetrofitDialog` เพิ่มเช็กบ็อกซ์ `⌨️ ปุ่มคีย์บอร์ด & คอนโทรลเลอร์`
   - ระบบใช้ตรรกะ **High-Precision Pattern Matching** ตรวจจับเฉพาะชื่อปุ่มหรือข้อผิดพลาดสัทอักษรเท่านั้น โดยไม่ไปกระทบคำกริยาภาษาไทยทั่วไปในบทสนทนา (เช่น ประโยค "เข้าไปในห้อง" หรือ "หลบหนีออกจากค่าย" จะไม่ถูกแทนที่เป็น Enter หรือ Esc)
   - ปรับชื่อแป้นตัวเลข `(Keypad)` / `(คีย์แพด)` ให้เป็นมาตรฐานเดียวกันคือ `(แป้นตัวเลข)` ทั้งหมด

### 5.4 วิธีการรันแก้ไขไฟล์เดิม (How to Run Retrofit on Existing Files)

#### วิธีที่ 1: ผ่านหน้าต่างโปรแกรม TStudio (GUI)
1. เปิดไฟล์แปลในโปรแกรม TStudio
2. กดคีย์ลัด **`Ctrl + Shift + M`** หรือกดปุ่ม **`🎖️ ซ่อมศัพท์ & คีย์บอร์ด`** ในแถบคำสั่งย่อย (Panel 3 Sub-Action Bar)
3. ติ๊กเลือกหมวดหมู่ที่ต้องการซ่อมแซม (เช่น `⌨️ ปุ่มคีย์บอร์ด & คอนโทรลเลอร์`, `🔮 รหัสรุ่นและโมเดล`, `🔫 อาวุธปืน`)
4. กดปุ่ม **`🔍 1. สแกนและแสดงตัวอย่าง (Preview)`** ตรวจสอบตารางผลลัพธ์
5. กดปุ่ม **`💾 2. บันทึกและแทนที่ลงในตารางหลัก`**

#### วิธีที่ 2: รันผ่านคำสั่ง Terminal / Python CLI (รวดเร็ว 1 บรรทัด)
เปิด PowerShell หรือ Command Prompt ในโฟลเดอร์ Modder Hub แล้วสั่งรัน:
```bash
# สแกนและแก้ไขไฟล์โดยอัตโนมัติ (พร้อมสำรองไฟล์ .bak ให้อัตโนมัติ):
python tools/flagship/TStudio/retrofit_cli.py "E:\Path\To\your_file.csv"

# ตรวจสอบดูตัวอย่างก่อนแก้ไข (Dry Run / Preview ไม่แก้ไฟล์จริง):
python tools/flagship/TStudio/retrofit_cli.py "E:\Path\To\your_file.csv" --preview

# ซ่อมเฉพาะปุ่มคีย์บอร์ด & แป้นตัวเลขอย่างเดียว:
python tools/flagship/TStudio/retrofit_cli.py "E:\Path\To\your_file.csv" --keys-only
```

#### วิธีที่ 3: ผ่านไฟล์แบตช์สำเร็จรูป (Batch File)
- ดับเบิลคลิกที่ไฟล์ `tools/flagship/TStudio/run_retrofit.bat` แล้วลากไฟล์ CSV ที่ต้องการแก้มาวางลงในหน้าต่าง หรือกด Enter เพื่อระบุตำแหน่งไฟล์
