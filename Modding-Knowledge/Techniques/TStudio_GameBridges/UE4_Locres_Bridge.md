# TStudio GameBridge: Unreal Engine 4 (.locres) Integration

## ภาพรวม (Overview)
เกมที่ใช้เอนจิน Unreal 4 มักจะเก็บข้อความภาษาไว้ในไฟล์ .locres ซึ่งเป็นฟอร์แมตปิด 
เพื่อเชื่อมต่อไฟล์ประเภทนี้เข้ากับระบบแปลภาษาของ **Modder Hub (TStudio / TRun)** เราจำเป็นต้องสร้าง Bridge Script (สคริปต์สะพานเชื่อม) แทนที่จะไปแก้ไข Core หลักของแอปพลิเคชัน

## เครื่องมือที่ใช้ (Dependencies)
- **UnrealLocres:** เครื่องมือสำหรับสกัด/แพ็คไฟล์ .locres กลับไปมาเป็น .csv

## กระบวนการทำงาน (Workflow)
ระบบ Bridge ประกอบด้วยสคริปต์ 2 ตัว:
1. **Unpacker Script ([Game]_unpacker.py):**
   - หน้าที่: รันคำสั่ง UnrealLocres เพื่อแตก .locres เป็น CSV ดั้งเดิม
   - การแปลง: อ่านไฟล์ CSV ดั้งเดิม และแปลงคอลัมน์ให้อยู่ในฟอร์แมตมาตรฐานของ TStudio ได้แก่ ID, ต้นฉบับ, คำแปล, AI_Reference
   - ผลลัพธ์: ได้ไฟล์ [Game].csv ที่พร้อมโยนเข้า TStudio ทันที

2. **Packer Script ([Game]_packer.py):**
   - หน้าที่: รับไฟล์ที่แปลเสร็จแล้วจาก TStudio ([Game]_translated.csv)
   - การแปลง: อ่านและแปลงโครงสร้างคอลัมน์กลับไปเป็นฟอร์แมตที่ UnrealLocres ต้องการ
   - การแพ็ค: รันคำสั่ง UnrealLocres แบบ import เพื่อฉีดข้อความกลับเข้าไปใน .locres ต้นฉบับ
   - ผลลัพธ์: ได้ไฟล์ [Game]_Thai.locres ที่พร้อมนำไปใส่ในโฟลเดอร์ Mod

## ตัวอย่างการเรียกใช้งาน (CLI Usage)
`ash
# ถอดรหัส
python ExpeditionsRome_unpacker.py "path/to/Game.locres"

# แพ็คกลับ (ต้องใช้ไฟล์ locres ต้นฉบับเป็นโครงสร้างอ้างอิง)
python ExpeditionsRome_packer.py "path/to/Game_translated.csv" "path/to/Game.locres"
`

การแยกส่วน Bridge Scripts ออกมาเป็น Standalone ช่วยรับประกันว่าระบบ Core ของ TStudio จะไม่พังและรองรับการขยายตัวกับเกมที่มีฟอร์แมตแปลกๆ ในอนาคตได้แบบ 100%!
