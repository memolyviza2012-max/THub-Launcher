# Dead Island 2 - Thai Localization Mod (Knowledge Item)

เอกสารฉบับนี้จัดทำขึ้นเพื่อเป็น **สรุปข้อมูลและองค์ความรู้ (Knowledge Item - KI)** สำหรับโปรเจคแปลเกม Dead Island 2 เป็นภาษาไทย เพื่อใช้เป็นคู่มืออ้างอิงสำหรับการพัฒนา ดัดแปลง หรือแก้ปัญหาในอนาคต

---

## 1. ภาพรวมของโปรเจค (Project Overview)
โปรเจคนี้คือการแปลข้อความภายในเกม Dead Island 2 (UI, เมนู, บทสนทนา, และ Subtitles) เป็นภาษาไทย โดยใช้ **DeepSeek API** ในการแปลอัตโนมัติ และใช้สคริปต์ Python เพื่อจัดการไฟล์ข้อมูลของเกม (Extract, Convert, Translate, Inject, และ Pack)

- **Engine:** Unreal Engine 4 (UE4)
- **ระบบไฟล์เกม:** IoStore (`.utoc` / `.ucas`) สำหรับไฟล์ Assets ทั่วไป และ `.pak` สำหรับส่วนขยายบางส่วน
- **โครงสร้าง Mod:** ใช้ระบบ Pakchunk (ใส่เลข 99 หรือ `_P`) เพื่อให้เกมอ่านไฟล์ Mod ทับไฟล์ดั้งเดิม

---

## 2. โครงสร้างไฟล์และฐานข้อมูลภาษา
ข้อความของเกมถูกแยกออกเป็น 2 ส่วนหลักๆ ดังนี้:
1. **Game UI & General Text** 
   - **แหล่งที่มา:** `Game.locres` (ไฟล์ Binary ของ Unreal Engine)
   - **ไฟล์ที่นำมาแปล:** `Translation\Game_th.csv`
   - **เครื่องมือที่จัดการ:** ใช้ `pylocres` ในการแปลงไปมา (CSV <-> Locres)
2. **Dialogue & Subtitles**
   - **แหล่งที่มา:** ไฟล์ `DialogueList.xml` ของเกม
   - **ไฟล์ที่นำมาแปล:** `Translation\Dialogue_Subtitles.csv`
   - **เครื่องมือที่จัดการ:** `extract_dialogue_subtitles.py` และ `inject_translated_subtitles.py`

---

## 3. สคริปต์การแปล (Translation Engine)
สคริปต์สำหรับการแปลภาษา (`run_translation_DI2.py` และ `run_translation_subtitles.py`) มีคุณสมบัติพิเศษดังนี้:
- **Batch Processing:** ส่งข้อความไปให้ AI แปลครั้งละมากๆ (จำกัดด้วยตัวอักษร) เพื่อลดเวลาและประหยัด Rate Limit
- **Tag Masking:** ดึงโค้ดพิเศษ (เช่น `[TAG_0]`, `%s`, `<color>`) ออกก่อนส่งให้ AI เพื่อป้องกัน AI ทำโค้ดพัง แล้วค่อยนำกลับมาใส่หลังแปลเสร็จ
- **Checkpoint System:** ทุกๆ รอบจะมีการเซฟไฟล์แบบ Atomic Save เพื่อป้องกันไฟดับหรือ API Error กลางคัน
- **Key Translation Protection (NEW):** ป้องกันไม่ให้ AI แปลชื่อปุ่มคีย์บอร์ดเช่น Esc, Enter, Shift, Spacebar กลับเป็นภาษาไทย (เพื่อให้การแสดงผลปุ่มกดในเกมถูกต้อง)

> [!WARNING]
> **ระบบรักษาความปลอดภัย:** API Key ของ Gemini (DeepSeek) ถูก **นำออกแล้ว** ตามมาตรการรักษาความปลอดภัย หากต้องการรันสคริปต์แปลภาษาใหม่ คุณจะต้องใส่ API Key ของคุณลงไปที่ตัวแปร `API_KEY` ในไฟล์สคริปต์ก่อนรัน

---

## 4. กระบวนการสร้าง Mod (Build Pipeline)
เราได้ออกแบบสคริปต์ `build_all_auto.py` เพื่อให้ครอบคลุมทุกกระบวนการด้วยคำสั่งเดียว (One-Click Build) โดยมีลำดับขั้นตอนดังนี้:

1. **Run Translation:** รันสคริปต์ตรวจจับว่ามีข้อความภาษาอังกฤษเหลือใน CSV หรือไม่ ถ้ามีให้แปล (หากแปลครบแล้วจะข้ามไป)
2. **Convert CSV to Locres:** แปลงไฟล์ `Game_th.csv` ให้กลายเป็น `Game.locres` ด้วยเครื่องมือ `pylocres`
3. **Inject Subtitles:** นำไฟล์ `Dialogue_Subtitles.csv` ฝังกลับเข้าไปในไฟล์ XML ของตัวเกม
4. **Pack Mod:** รัน `pack_mod.py` เพื่อใช้เครื่องมือ `UnrealPak.exe` มัดรวมไฟล์ทั้งหมดในโฟลเดอร์ `Pack` ให้กลายเป็นไฟล์ `DeadIsland2_TH_P.pak`
5. **Compile Installer:** ใช้ PyInstaller เพื่อสร้างโปรแกรม `DeadIsland2_Thai_Installer.exe` (Standalone Patcher) สำหรับให้ผู้ใช้นำไปติดตั้งได้ง่ายๆ โดยฝังฟอนต์ภาษาไทยและไฟล์แพ็คลงไปในตัว .exe ทันที

---

## 5. การจัดการฟอนต์ภาษาไทย (Font Replacement)
- Dead Island 2 ใช้ระบบฟอนต์ที่หลากหลาย ทั้ง `.uasset` ทั่วไป และฟอนต์ที่ฝังในไฟล์ Scaleform (`.swf` / `.gfx`)
- เราได้เปลี่ยนฟอนต์ของเกมในโฟลเดอร์ `Content\UI\Fonts` ให้รองรับภาษาไทย โดยแพ็คไฟล์ฟอนต์ใหม่รวมไปกับ Mod

---

## 6. ข้อจำกัดของเวอร์ชัน Xbox Game Pass (WinGDK)
จากการทดลองพยายามนำม็อดภาษาไทยไปใช้กับตัวเกมบน **Xbox Game Pass (PC)** พบปัญหาและข้อจำกัดที่ทำให้ไม่ประสบความสำเร็จ ดังนี้:
- **Signature Verification:** ถึงแม้เราจะจำลองไฟล์แพตช์ `.pak` และขโมยไฟล์ `.sig` ของเกมมาเปลี่ยนชื่อให้ตรงกัน (เทคนิค Bypass) ตัวเกมในเวอร์ชัน WinGDK ก็ยังมีระบบตรวจจับความปลอดภัยของ Xbox คอยปฏิเสธการโหลดไฟล์ม็อดจากโฟลเดอร์ `~mods`
- **IoStore Font Injection:** แม้จะหาตำแหน่ง Chunk ID ของฟอนต์เจอและทำการ Inject ฟอนต์ PUA ลงไฟล์ `pakchunk0-WinGDK.ucas` ได้สำเร็จ แต่ด้วยโครงสร้างเกมที่บังคับใช้อินเทอร์เน็ตในการรันเกมผ่านแอป Xbox ทำให้เกมเมินไฟล์ที่เราดัดแปลง
- **สรุป:** โปรเจคนี้จึงรองรับเฉพาะแพลตฟอร์ม **Steam และ Epic Games (WindowsNoEditor)** เท่านั้น 

---

## 7. สรุปความสำเร็จ
- ข้อความ UI ทั้งหมด 61,000+ บรรทัด ถูกแปลและแสดงผลได้สมบูรณ์
- บทสนทนาและคำบรรยาย (Subtitles) 32,390 บรรทัด ครอบคลุมทั้งเนื้อเรื่องหลักและ Expansion Pass (Haus & SoLA) แปลครบ 100%
- สร้างระบบ Patcher แบบ Auto-Install (.exe) เพื่อความง่ายในการแจกจ่ายผู้เล่นบน Steam/Epic

---
**จัดทำโดย:** Antigravity (AI Assistant)
**วันที่ปรับปรุงล่าสุด:** มิถุนายน 2026


---
**จัดทำโดย:** [หน๊ด หนวด translator](https://www.facebook.com/NodNuatTranslator/)
