# Wasteland 2 Director's Cut: Thai Localization Bible

## 1. ข้อมูลพื้นฐานของเกม (Game Engine & Architecture)
- **Engine:** Unity 5 (เวอร์ชันเก่า)
- **Architecture:** Mono (64-bit) 
  *(คำเตือน: ห้ามใช้ BepInEx เวอร์ชัน IL2CPP เด็ดขาด มิฉะนั้นเกมจะแครชด้วย Error Access Violation ใน `mono.dll`)*
- **ระบบข้อความ (Localization):** เกมโหลดข้อความหลักจากไฟล์ Text ภายนอกที่อยู่ในโฟลเดอร์ `StreamingAssets` โดยไม่ต้องพึ่งพา AutoTranslator ใดๆ

## 2. โครงสร้างไฟล์ภาษา (Localization Files)
- **ตำแหน่งไฟล์:** `WL2_Data\StreamingAssets\Localization\Main_en.txt`
- **รูปแบบไฟล์:** 
  - เป็นไฟล์ Text เข้ารหัส **UTF-16 LE** (จำเป็นต้องเข้ารหัสนี้เท่านั้น มิฉะนั้นเกมจะอ่านไม่ขึ้น)
  - รูปแบบข้อมูลในไฟล์จะใช้ขึ้นต้นด้วย `#<@>` สำหรับคีย์ และ `=` สำหรับข้อความแปล
  - ตัวอย่าง:
    ```
    #<@>New Game
    =เริ่มเกมใหม่
    ```

## 3. ปัญหาสระลอยและการเข้ารหัส (Text Encoding & PUA)
เนื่องจาก Unity 5 ไม่รองรับสระลอยภาษาไทย เราต้องใช้วิธี **PUA (Private Use Area)** ในการหลอกเอนจิน
- **เครื่องมือแปลงข้อความ:** ใช้ `PUA-Thai-Converter` แปลงข้อความจากไฟล์ `Main_en.txt` ก่อนแพ็กกลับ 
- **ข้อควรระวัง (Mapping Sync):** การแปลงข้อความจะต้องใช้คู่กับ **"ฟอนต์ที่ใช้ Mapping เดียวกันแบบ 1:1 เท่านั้น"** มิฉะนั้นสระลอยบางตัว (เช่น ิ, ่, ุ) จะกลายเป็นตัวอักษรล่องหน (เช่น "เริ่มเกมใหม่" กลายเป็น "เมเกมให")

## 4. การจัดการฟอนต์ (Font Modding)
ฟอนต์ของเกมถูกฝังอยู่ในไฟล์ `.assets` หลายไฟล์ (ไม่ได้ใช้ไฟล์แยกต่างหาก) ต้องใช้ `UnityPy` เพื่อสกัดและแทนที่

### 4.1 ตำแหน่งของฟอนต์ (Font Locations)
จากการสแกน พบฟอนต์ที่ต้องแทนที่ทั้งหมด 6 ตำแหน่ง:
1. `resources.assets`: ฟอนต์ `cour`, `OCRAEXT`, `arial`, `Electrickle`
2. `sharedassets5.assets`: ฟอนต์ `consola`
3. `sharedassets6.assets`: ฟอนต์ `FRADMCN`

### 4.2 การหลอมฟอนต์ (Font Generation)
เพื่อให้แก้ปัญหาสระล่องหนได้อย่างเด็ดขาด ต้องทำตามสเต็ปนี้:
1. ดึงไฟล์ฟอนต์ต้นฉบับ เช่น `IBMPlexSans` มา
2. ใช้สคริปต์ `custom_font_pua_generator.py` โดยอ่านตาราง `mapping.json` ของตัวแปลงข้อความ แล้วสร้าง Composite Glyph ฝังเข้าไปในฟอนต์
3. เซฟเป็นฟอนต์ใหม่ (เช่น `Wasteland2_PUA.ttf`)

### 4.3 การฝังฟอนต์ลงเกม (Font Injection)
ใช้ `UnityPy` โหลดไฟล์ `.assets` ค้นหา Object ประเภท `Font` และเขียนข้อมูล Raw bytes ของ `Wasteland2_PUA.ttf` ทับลงไปที่ `m_FontData` จากนั้น Save ไฟล์ `.assets` ทับของเดิม

## 5. บทสรุปและคำแนะนำ
- Wasteland 2 **ไม่ต้องใช้ BepInEx หรือ XUnityAutoTranslator** ในการแปลไฟล์ข้อความหลัก การแปลแบบ Native ผ่าน `Main_en.txt` ได้ผลลัพธ์ที่ดีและเสถียรกว่ามาก
- ปัญหาใหญ่ที่สุดของเกมยุคนี้คือ **Mapping Mismatch** ระหว่างโปรแกรมแปลงข้อความและไฟล์ฟอนต์ เมื่อใดที่ตัวอักษรบางตัวหายไป ให้ตั้งข้อสงสัยเรื่อง Mapping ทันที (ดูเพิ่มที่ `Modding-Knowledge\Techniques\Font_PUA_Mapping_Sync.md`)
