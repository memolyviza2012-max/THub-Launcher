# Unreal Engine 4 Font Modding - The Hidden UI Fonts & Internal Name Patching

## 1. ปัญหา: การแก้ไข Roboto แล้ว UI ของเกมล่ม (Crash/Invisible UI)
ในบางเกม (เช่น Expeditions: Rome) นักพัฒนาอาจไม่ได้ใช้ฟอนต์ Roboto ซึ่งเป็นฟอนต์ดีฟอลต์ของ Engine ในการสร้าง UI แต่กลับไปใช้ฟอนต์ Custom อื่นๆ แทน (เช่น Cinzel, EBGaramond, Noto)
- **ข้อควรระวัง:** การที่เราพยายามจะงัดแงะไฟล์ Roboto.uasset / Roboto.ufont เพื่อใส่ภาษาไทย อาจทำให้เกิดผลข้างเคียงคือ ตัว Engine ของ Unreal ทำงานผิดพลาด (Crash) เนื่องจากโครงสร้างฟอนต์ (เช่น UPM, Bounding Box) ถูกเปลี่ยนแปลงจน FreeType เรนเดอร์ไม่ได้ ทำให้ UI หน้าจอว่างเปล่า!
- **ข้อสรุป:** ถ้าเกมมีโฟลเดอร์ฟอนต์เป็นของตัวเอง **อย่าแก้ไข Roboto เด็ดขาด!**

## 2. การค้นหาฟอนต์ที่แท้จริง
ฟอนต์ Custom ของเกมมักถูกเก็บซ่อนไว้ใน pak file เสริม (เช่น pakchunk0_s8.pak, pakchunk0_s4.pak) 
- ควรใช้คำสั่ง epak list <file.pak> | Select-String -Pattern "Font" วนลูปเช็คในไฟล์ pak ทุกไฟล์ที่เกมมี เพื่อหาที่ซ่อนที่แท้จริง!

## 3. เทคนิค: Internal Name Patching (การสวมรอยชื่อฟอนต์)
หากฟอนต์ดั้งเดิมของเกม (เช่น Cinzel) และฟอนต์ภาษาไทยที่เราจะใช้ (เช่น Kanit) มีค่า **UPM (Units Per Em) เท่ากัน** (ตัวอย่างเช่น = 1000) 
แทนที่เราจะทำการ Merge ฟอนต์ให้ยุ่งยากและเสี่ยงพัง เราสามารถ **"สวมรอย"** ฟอนต์ภาษาไทยให้กลายเป็นฟอนต์ดั้งเดิมได้ 100% ด้วยการเขียนทับตารางชื่อ (Name Table) ดังนี้:

### สคริปต์ Python สำหรับสวมรอยฟอนต์
ใช้ไลบรารี ontTools เพื่อก็อปปี้ 
ameID 1, 2, 3, 4, 6 จากฟอนต์ออริจินัลของเกม มายัดใส่ในฟอนต์ภาษาไทย แล้วเซฟทับ .ufont เดิม:

\\\python
import os
from fontTools.ttLib import TTFont

orig_font = TTFont("OriginalGameFont.ufont")
thai_font = TTFont("ThaiFont.ttf")

names_to_copy = {}
for record in orig_font['name'].names:
    if record.nameID in [1, 2, 3, 4, 6]:
        names_to_copy[(record.nameID, record.platformID, record.platEncID, record.langID)] = record

# ลบชื่อเก่าของฟอนต์ไทยทิ้ง
thai_font['name'].names = [r for r in thai_font['name'].names if r.nameID not in [1, 2, 3, 4, 6]]

# ใส่ชื่อออริจินัลของเกมเข้าไปแทน
for key, record in names_to_copy.items():
    thai_font['name'].names.append(record)

# บันทึกเป็นไฟล์ .ufont ใหม่ พร้อมใช้งาน!
thai_font.save("NewPatchedFont.ufont")
\\\

ด้วยเทคนิคนี้ ตัว Engine จะถูกหลอกอย่างสมบูรณ์แบบ มันจะโหลดฟอนต์ภาษาไทยขึ้นมาใช้งานโดยคิดว่าเป็นฟอนต์ดั้งเดิมของเกม ทำให้ไม่เกิดการ Crash ใดๆ ทั้งสิ้น!
