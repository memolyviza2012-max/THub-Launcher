# 🌌 Marvel's Guardians of the Galaxy - Modding & Localization Guide

เอกสารนี้รวบรวมเทคนิคและเครื่องมือที่ถูกนำมาใช้ในโปรเจกต์แปลภาษาไทยสำหรับเกม **Marvel's Guardians of the Galaxy**

## 1. ปัญหาการแปลของ Groot (Groot's Translation Hallucinations)
ในกระบวนการแปลภาษาด้วยระบบ AI ปัญหาที่ใหญ่ที่สุดคือการที่ตัวละคร Groot พูดแต่คำว่า "I am Groot" ซึ่งทำให้ระบบ AI เกิดอาการ **"Hallucination" (จินตนาการคำแปลไปเอง)** ระบบจึงต้องมีสคริปต์กรองพิเศษ:
- `find_hallucinations.py` และ `clear_hallucinations.py`: ทำหน้าที่ตรวจจับคำแปลที่มีความยาวเกินปกติ หรือไม่ตรงกับประโยค "ฉันคือกรู้ท"
- `search_groot.py`: จัดการล็อกข้อความของ Groot ไม่ให้ถูกแปลเพี้ยนไปเป็นประโยคอื่น

## 2. ระบบฟอนต์ PUA (Private Use Area)
ตัวเกมมีอุปสรรคเรื่องการแสดงผลสระและวรรณยุกต์ไทย โปรเจกต์นี้จึงใช้เทคนิค **PUA (Private Use Area)** ในการหลอกเอนจิน:
- `generate_perfect_pua.py` และ `apply_pua.py`: ใช้เพื่อโยงรหัสตัวอักษรไทย (Codepoints) ไปยังพื้นที่ PUA ในฟอนต์ที่สร้างขึ้นใหม่
- `flatten_vowels.py`: จัดการระดับของสระและวรรณยุกต์ไม่ให้ซ้อนทับกันจนลอยหรือจมเกินไป

## 3. การอัปเดตแบบอัตโนมัติ (Automated Build System)
โปรเจกต์นี้มีระบบสคริปต์ที่ค่อนข้างสมบูรณ์ในการอัปเดตไฟล์ เช่น:
- `bump_version.py` และ `update_readme.py`: จัดการการรันเวอร์ชันอัปเดตและการเขียนแพตช์โน้ตอัตโนมัติเมื่อมีการปล่อยม็อดตัวใหม่


---
**จัดทำโดย:** [หน๊ด หนวด translator](https://www.facebook.com/NodNuatTranslator/)
