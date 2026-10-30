# Root Cause Analysis (RCA): CoreAI 'has_cjk' Critical Crash in TStudio

## 1. ปัญหาที่พบ (Symptom & Trigger)
- **อาการ**: เมื่อผู้ใช้สั่งแปลภาษา (ทั้งแปลทีละบรรทัด หรือแปลเป็นชุด Batch) โปรแกรมเกิดอาการค้าง และเด้งกล่องข้อความสีส้มแจ้งเตือน:
  `Critical Error: เกิดข้อผิดพลาดร้ายแรง (Program Crashed)`
  `type object 'CoreAI' has no attribute 'has_cjk'`
  และในบางครั้งโปรแกรมจะปิดตัวลง (Crash / Exit) ทันทีหลังกดปิดกล่องเตือน

---

## 2. สาเหตุที่แท้จริง (Root Cause & Mechanism)

### 2.1 Trace เส้นทางข้อผิดพลาด (Fail Path)
1. เมื่อเริ่มแปล (`retranslate_single` หรือ `retranslate_batch`):
   - `ApiWorker` ทำงานร่วมกับ LLM ใน Background Thread จนได้ผลลัพธ์คำแปลกลับมา (`reply`)
   - สัญญาณ `finished` ส่งผลลัพธ์กลับมายัง Main GUI Thread ผ่าน `_on_single_success` หรือ `_on_batch_row_success`
2. Main Thread เรียกเมธอดตรวจจับข้อความและกรอง Hallucination:
   ```python
   from tstudio_core import CoreAI
   reply = CoreAI.clean_ai_translation(source_text, reply)
   ```
3. ภายใน `CoreAI.clean_ai_translation(cls, source_text, translated_text)`:
   - มีการคำนวณตัวแปรเพื่อปรับเกณฑ์ Hallucination สำหรับภาษาตระกูล CJK (จีน, ญี่ปุ่น, เกาหลี):
     ```python
     is_cjk = cls.has_cjk(source_text) or bool(re.search(r'[぀-ヿ가-힯]', source_text))
     ```
   - เมธอด `has_cjk()` ถูกนิยามไว้ที่คลาส **`TStudioCore`** แต่ไม่ได้ถูกนิยามไว้ที่ **`CoreAI`**
   - เมื่อเรียกผ่าน `cls.has_cjk(...)` Python จึงโยนข้อผิดพลาด **`AttributeError: type object 'CoreAI' has no attribute 'has_cjk'`**
4. เนื่องจาก Exception เกิดขึ้นบน Main Thread ภายใน Qt Slot:
   - `sys.excepthook` จับข้อผิดพลาดและแสดงหน้าต่าง **Critical Error (Program Crashed)**
   - ส่งผลให้หน้าจอค้าง และเมื่อปิดกล่องข้อความ โปรแกรมจะถูกสั่งยกเลิกการทำงาน

---

## 3. วิธีการแก้ไข (The Fix & Engineering Fortification)

### 3.1 การเพิ่มฟังก์ชัน CJK Proxy ใน `CoreAI`
ใน `tools/flagship/Core/tstudio_core.py` ได้ทำการเพิ่ม Static Methods เข้าไปยังคลาส `CoreAI`:
```python
class CoreAI:
    @staticmethod
    def has_cjk(text):
        """Proxy to TStudioCore.has_cjk."""
        return TStudioCore.has_cjk(text)

    @staticmethod
    def extract_cjk(text):
        """Proxy to TStudioCore.extract_cjk."""
        return TStudioCore.extract_cjk(text)

    @staticmethod
    def clean_cjk_leak(text):
        """Proxy to TStudioCore.clean_cjk_leak."""
        return TStudioCore.clean_cjk_leak(text)
```

### 3.2 ป้องกันความปลอดภัยใน `clean_ai_translation`
- เปลี่ยนการเรียก `cls.has_cjk(source_text)` ให้เป็น `TStudioCore.has_cjk(source_text)` โดยตรง
- ครอบด้วยบล็อก `try ... except Exception:` เพื่อรับประกันว่าขั้นตอน Clean ข้อความจะไม่มีวันทำให้โปรแกรมแครช โดยหากเกิดกรณีผิดพลาดจะส่งคืนข้อความต้นฉบับอย่างปลอดภัย

### 3.3 Defensive Post-Processing ใน `tstudio_app.py`
- ครอบจุดเรียก `CoreAI.clean_ai_translation` ในทั้ง `_on_single_success` และ `_on_batch_row_success` ด้วยบล็อก `try-except` ป้องกันไม่ให้ Main Thread หลุดการทำงาน

### 3.4 ซิงก์โค้ดและคอมไพล์ในโฟลเดอร์รันไทม์ `dist/THub/_internal/`
- ซิงก์ไฟล์ `tstudio_core.py` และ `tstudio_app.py` ไปยังโฟลเดอร์รันไทม์จริงของ THub และคอมไพล์ไบต์โค้ดเรียบร้อย
