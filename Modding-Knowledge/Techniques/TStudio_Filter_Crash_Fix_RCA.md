# TStudio PyQt6 Filter Crash & Stability RCA (Root Cause Analysis)

## 📌 บทนำ (Overview)
เมื่อใช้งานระบบคัดกรอง (Filters เช่น คัดกรองตัวละคร, ไอเทม, สกิล, ข้อความที่ยังไม่แปล) หรือพิมพ์ค้นหาใน TStudio โปรแกรมอาจเกิดอาการค้างแล้วเด้งปิดตัวเองทันที (Crash / Abrupt Exit) โดยไม่มี Python Exception Traceback แสดงใน Console

เอกสารนี้ระบุสาเหตุเชิงลึก (Root Cause), กลไกการเกิดข้อผิดพลาดระดับ C++ Qt, แนวทางการแก้ไข และการซิงค์ไฟล์ไปยังตัว Build `dist/THub/_internal/`

---

## 🔍 การวิเคราะห์รากเหง้าของปัญหา (Root Causes)

### 1. Re-entrant `invalidateFilter()` C++ Segfault ใน `on_row_selected` (วิกฤตสูงสุด)
- **จุดเกิดเหตุ**: ใน `tstudio_app.py` ฟังก์ชัน `on_row_selected(self, current, previous)`
- **โค้ดเดิมที่มีปัญหา**:
  ```python
  if hasattr(self, '_is_releasing_filter_row') and not self._is_releasing_filter_row:
      if prev_src_row >= 0:
          if not self.proxy.filterAcceptsRow(prev_src_row, QModelIndex()):
              self._is_releasing_filter_row = True
              try:
                  self.proxy.invalidateFilter() # 💥 ระเบิดตรงนี้!
                  ...
  ```
- **กลไกการแครช**:
  เมื่อผู้ใช้เปลี่ยน Filter Mode หรือพิมพ์คำค้นหา `QSortFilterProxyModel` จะคำนวณแถวใหม่และส่งสัญญาณ `selectionChanged` / `currentChanged` ไปยังตาราง
  เมื่อ Handler `on_row_selected` ถูกเรียกขึ้นมา **ในขณะที่ Qt กำลัง dispatch event ของ selection** แต่ handler กลับไปสั่ง `self.proxy.invalidateFilter()` อีกรอบ!
  การเรียก `invalidateFilter()` ซ้ำซ้อน (Re-entrant) กลางวงการประมวลผล internal mapping table ของ Qt C++ (`QSortFilterProxyModelPrivate`) จะทำให้ตัวชี้ C++ พัง ทริกเกอร์ **Access Violation `0xC0000005`** ส่งผลให้กระบวนการปิดตัวทันทีโดยที่ Python ดักจับไม่ได้

- **วิธีแก้**:
  นำโค้ดการเรียก `invalidateFilter()` ออกจาก `on_row_selected` โดยสิ้นเชิง การรีเฟรชแถวเมื่อแปลเสร็จแล้วย้ายไปแถวถัดไปให้จัดการผ่าน `_advance_filtered_row` (กด `Ctrl+Enter`) ซึ่งทำงานนอก cycle การคลิกเลือกแถวอย่างปลอดภัย

---

### 2. ขาด Null Safety & Type Guard ใน `FilterProxy.filterAcceptsRow`
- **จุดเกิดเหตุ**: ในคลาส `FilterProxy` เมธอด `filterAcceptsRow(self, source_row, source_parent)`
- **ปัญหาเดิม**:
  มีการเรียกใช้ string methods ตรงๆ เช่น:
  ```python
  if self._mode == 1 and item["trans"].strip(): return False
  if len(item["source"]) ...
  ```
  หากไฟล์ข้อมูลบางแถวมีค่าเป็น `None`, ตัวเลข หรือ format ผิดปกติ Python จะโยน `TypeError` หรือ `AttributeError` ออกมา และใน PyQt6 เมื่อเกิด Unhandled Exception ภายใน Virtual Callback ของ C++ อย่าง `filterAcceptsRow` Qt จะสั่ง `std::abort()` ทันที
- **วิธีแก้**:
  1. แปลงค่าทุกฟิลด์ให้เป็น `str` ปลอดภัยเสมอ:
     ```python
     trans_str = str(item.get("trans") or "")
     source_str = str(item.get("source") or "")
     ai_str = str(item.get("ai_ref") or "")
     tag = str(item.get("tag") or "❓")
     ```
  2. ครอบทั้งฟังก์ชันด้วย `try...except Exception: return False` ป้องกันไม่ให้เกิด uncaught exception หลุดกลับไปยัง C++ runtime

---

### 3. ไฟล์ใน Distribution ไม่ได้ถูกอัปเดต (Distribution Desync)
- ตัวโปรแกรมที่ผู้ใช้รันผ่าน THub ใช้งานไฟล์จาก:
  - `modder-hub/dist/THub/_internal/tstudio_app.py`
  - `modder-hub/dist/THub/_internal/tools/flagship/TStudio/tstudio_app.py`
- การแก้ไขเฉพาะไฟล์ต้นทาง `modder-hub/tools/flagship/TStudio/tstudio_app.py` จะไม่ส่งผลต่อตัวโปรแกรมที่เปิดใช้งานจริงใน THub จนกว่าจะซิงค์ไฟล์และคอมไพล์แคช `__pycache__` ให้ตรงกัน

---

## 🛠️ การปรับปรุงประสบการณ์ใช้งาน (UX Enhancements)

1. **Auto-select Row 0**: เมื่อผู้ใช้สลับโหมดฟิลเตอร์หรือค้นหาคำ หากมีผลลัพธ์ โปรแกรมจะไฮไลต์และเลือกแถวแรก (Row 0) ให้ทันที ไม่ทิ้งการเลือกไว้ในสถานะว่าง
2. **Clean State เมื่อไม่พบผลลัพธ์**: เมื่อผลลัพธ์เป็น 0 แถว ระบบจะรีเซ็ตกล่องข้อความ Source, AI Ref และ Translation ให้ว่างเปล่า ป้องกันข้อความแถวเก่าค้าง
3. **Quick Filter Chips Sync**: สลับสเตตัสปุ่มชิปเร็ว (`ทั้งหมด`, `รอแปล`, `แปลแล้ว`) ให้ตรงกับ Dropdown อัตโนมัติ โดยหากเลือกโหมดหมวดหมู่พิเศษ (เช่น สกิล, ไอเทม, เควสต์) ชิปสถานะจะปลดการ active ออกอย่างถูกต้อง

---

## 🧪 การทดสอบยืนยันผล (Verification)
รันชุดทดสอบความเสถียร `verify_filter_stability.py` ผ่านข้อมูลจริง:
1. `Game.csv` (8,949 แถว)
2. `AtelierRyza_Thai_Translation_MASTER.csv` (28,944 แถว)
- สลับโหมดฟิลเตอร์ครบทั้ง 16 โหมด (0 - 15)
- ทดสอบคลิกชิปด่วน และค้นหาคำค้นหาทั้งที่มีและไม่มีในไฟล์ (Zero matches)
- **ผลลัพธ์: ผ่าน 100% ปราศจากการ Crash (Exit code 0)**
