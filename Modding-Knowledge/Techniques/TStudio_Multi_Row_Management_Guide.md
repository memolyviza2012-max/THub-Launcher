# คู่มือเทคนิค: ระบบจัดการหลายแถวพร้อมกัน (Multi-Row Selection & Batch Deletion) ใน TStudio

## 1. บทนำ (Introduction)
ในการแปลภาษาเกม ไฟล์แปลภาษามักจะมีจำนวนหลายพันถึงหลายแสนบรรทัด บ่อยครั้งที่ตัวเกมดึงเอา String ของระบบที่ไม่จำเป็น, โค้ดตัวแปร, หรือบรรทัดขยะ (Garbage rows) ติดมาในไฟล์ CSV การลบทีละบรรทัดทำให้เสียเวลาอย่างมาก ระบบจัดการหลายแถวพร้อมกันจึงถูกออกแบบมาเพื่อรองรับ:
- การคลิกลากคลุมแถวต่อเนื่อง (Drag-selection) ผ่านแถบหมายเลขบรรทัด (Vertical Header) แบบ Excel / Sheets
- การลบแถวออกจากไฟล์พร้อมกันหลายบรรทัดอย่างปลอดภัย (Safe Batch Deletion)
- การคลิกขวาเพื่อจัดการแถวที่เลือก (Context Menu)
- คีย์ลัดด่วนเพื่อประสิทธิภาพสูงสุดในการทำงาน

---

## 2. โครงสร้างและการทำงานเชิงเทคนิค (Technical Architecture)

### 2.1 แถบตัวเลขบรรทัด (Vertical Header)
เปิดใช้งาน `verticalHeader` ใน `QTableView` และเชื่อมต่อกับ `headerData` ของโมเดล:

```python
self.table.verticalHeader().setVisible(True)
self.table.verticalHeader().setDefaultSectionSize(26)
self.table.verticalHeader().setMinimumWidth(50)
self.table.verticalHeader().setHighlightSections(True)
```

ใน `CsvTableModel`:
```python
def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
    if role == Qt.ItemDataRole.DisplayRole:
        if orientation == Qt.Orientation.Horizontal:
            return self.headers[section]
        elif orientation == Qt.Orientation.Vertical:
            return str(section + 1) # 1-based index for human readability
    if role == Qt.ItemDataRole.TextAlignmentRole and orientation == Qt.Orientation.Vertical:
        return Qt.AlignmentFlag.AlignCenter
    return None
```

### 2.2 การลบแถวแบบ Reverse-Sorted Indices
เมื่อทำการลบสมาชิกใน Python list (`del list[i]`) ดัชนีของสมาชิกลำดับถัดไปจะเลื่อนขึ้น หากลบจากน้อยไปมาก ดัชนีจะคลาดเคลื่อนและลบผิดแถวทันที

**กฎเหล็ก**: ต้องเรียงลำดับดัชนีจากมากไปน้อย (`reverse=True`) เสมอ:

```python
def delete_rows(self, row_indices):
    if not row_indices:
        return 0
    sorted_indices = sorted(set(row_indices), reverse=True)
    self.beginResetModel()
    for idx in sorted_indices:
        if 0 <= idx < len(self._data):
            del self._data[idx]
    self.is_dirty = True
    self.endResetModel()
    return len(sorted_indices)
```

### 2.3 การแปลงตำแหน่งจาก QSortFilterProxyModel
เนื่องจากหน้าจอ TStudio รองรับการกรองสถานะ (Untranslated, Translated, Leaks ฯลฯ) ดัชนีที่ผู้ใช้เลือกใน View จะเป็นของ Proxy Model จึงต้องแปลงเป็น Source Model เสมอ:

```python
source_rows = set()
for idx in selected_indexes:
    if idx.isValid():
        src_idx = self.proxy.mapToSource(idx)
        if src_idx.isValid() and 0 <= src_idx.row() < len(self.model._data):
            source_rows.add(src_idx.row())
```

---

## 3. ตารางสรุปคีย์ลัดและฟังก์ชัน (Hotkeys & Actions)

| การกระทำ (Action) | วิธีการ (Method) | ผลลัพธ์ (Result) |
|---|---|---|
| **ลากคลุมหลายแถว** | คลิกลากบนแถบตัวเลขบรรทัดด้านซ้าย หรือคลิกแถวแรกแล้วกด `Shift+คลิก` | เลือกหลายแถวพร้อมกัน |
| **ลบบรรทัดออกจากไฟล์** | ปุ่ม `[ 🗑️ ลบบรรทัด ]` หรือกด `Shift+Delete` | ป็อปอัปยืนยัน -> ลบแถวออกจากไฟล์ CSV ทันที |
| **เมนูจัดการแถว (Prompt)** | กดปุ่ม `Delete` บนคีย์บอร์ด | แสดงตัวเลือกระหว่าง "ลบบรรทัดออกจากไฟล์" กับ "ล้างเฉพาะคำแปล" |
| **ล้างเฉพาะข้อความคำแปล** | กดปุ่ม `Backspace` บนคีย์บอร์ด | เคลียร์ช่องคำแปลให้ว่างเปล่า แต่บรรทัดในไฟล์ยังคงอยู่ |
| **เปิด Context Menu** | คลิกขวาบนตาราง | แสดงเมนูลบบรรทัด, ล้างคำแปล, แปล AI, ล้างจีน, คัดลอกต้นฉบับ/คำแปล |
| **แปล AI หลายแถวพร้อมกัน** | เลือกหลายแถว -> `Ctrl+T` หรือคลิกขวา "แปลบรรทัดที่เลือกด้วย AI" | แปล AI แบบ Batch รวดเร็ว |
