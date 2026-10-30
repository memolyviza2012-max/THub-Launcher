# Wasteland 3 Thai Localization Bible

## 1. ข้อมูลพื้นฐานและสถาปัตยกรรมของเกม
Wasteland 3 สร้างขึ้นด้วย **Unity Engine** และใช้ระบบจัดการทรัพยากรแบบ **Addressables** ข้อความภายในเกมทั้งหมด (ตั้งแต่หน้าต่าง UI, บทสนทนา, ชื่อไอเทม ไปจนถึงเควสต่างๆ) จะถูกแพ็กรวมอยู่ในไฟล์นามสกุล `.bundle` 

**ตำแหน่งไฟล์ข้อความหลัก:**
*   **Base Game:** `WL3_Data/StreamingAssets/aa/StandaloneWindows64/oei_assets_stringtabledata_english_...bundle`
*   **DLC 1 (The Battle of Steeltown):** `WL3_Data/StreamingAssets/aa/StandaloneWindows64/DLC1/oei_dlc1_assets_all.bundle`
*   **DLC 2 (Cult of the Holy Detonation):** `WL3_Data/StreamingAssets/aa/StandaloneWindows64/DLC2/oei_dlc2_assets_all.bundle`

---

## 2. โครงสร้างข้อมูลข้อความ (StringTableData)
ภายในไฟล์ `.bundle` ข้อความจะถูกเก็บในรูปแบบของออบเจกต์ **MonoBehaviour** ที่มีชื่อว่า `StringTableData_English` (ตามภาษาต้นฉบับ) ระบบจะใช้โครงสร้างคู่ขนาน (Parallel Arrays) ได้แก่ `entryIDs` และ `defaultTexts` 

**ตัวอย่าง Key:**
`mission_d1001_flushed::10000::default` 
*   หมายถึง เควสชื่อ Flushed จาก DLC1 (รหัส d1001) Entry ที่ 10000 

---

## 3. ขั้นตอนทางเทคนิคในการทำ Localization
การแปลภาษาไทยสำหรับเกมนี้แบ่งออกเป็น 4 ขั้นตอนหลัก:

### 3.1 การสกัดข้อความ (Extraction)
เราใช้ไลบรารี **UnityPy** ใน Python เปิดอ่านไฟล์ Bundle และค้นหาออบเจกต์ `MonoBehaviour` ที่ชื่อว่า `StringTableData_English` จากนั้นลูปเพื่อดึงข้อมูลรหัส (Key) และข้อความต้นฉบับออกมาเป็นไฟล์ CSV

### 3.2 การแสดงผลฟอนต์ไทย (Font Rendering)
ตัวเกมใช้ **TextMeshPro (TMP)** ในการเรนเดอร์ตัวอักษร เราจำเป็นต้องใช้ **BepInEx Plugin** เข้ามาแทรกแซง (Hook) ตอนที่เกมรัน เพื่อทำการเปลี่ยนฟอนต์ (Font Replacement) จากฟอนต์ดั้งเดิมของเกม ให้เป็นฟอนต์ที่เรา Custom ขึ้นมาให้มีอักขระภาษาไทย (มักใช้ไฟล์ .ttf หรือ .asset)

### 3.3 การแพ็กข้อความกลับ (String Injection)
เมื่อแปล CSV เสร็จสิ้น เราจะใช้ UnityPy โหลดไฟล์ Bundle ต้นฉบับขึ้นมาอีกครั้ง แล้วนำข้อความภาษาไทยเขียนทับ (Inject) ข้อความภาษาอังกฤษเดิมตรงๆ ในโครงสร้าง Typetree ของ `StringTableData_English` 

### 3.4 การบีบอัดไฟล์และเซฟ (LZ4 Compression)
เมื่อเขียนทับเสร็จ **จะต้องบีบอัดไฟล์แบบ LZ4** เท่านั้น (`packer="lz4"`) เพื่อให้เอนจิน Unity ของเกมสามารถโหลดและสตรีมทรัพยากรได้อย่างราบรื่น หากใช้การบีบอัดแบบอื่น (เช่น LZMA หรือไม่บีบอัด) อาจทำให้เกมแครชในหน้าโหลดเข้าเกมได้

---

## 4. การค้นพบสำคัญ (Key Discoveries & Troubleshooting)

### 🚨 ปัญหา PUA (Private Use Area) vs Standard Unicode
ในอดีต การทำ Mod ภาษาไทยใน Unity มักจะต้องนำข้อความไปผ่านกระบวนการแปลงรหัส (Encoding) แบบ PUA (เช่น การใช้ TPUAEngine) เพื่อแก้ปัญหาสระลอยและวรรณยุกต์จม แต่กระบวนการนี้ทำให้สคริปต์ทำงานช้ามาก (ใช้เวลาหลายนาทีต่อการแพ็ก 1 ครั้ง) และทำให้แพ็กเกอร์ค้างเมื่อเจอข้อความจำนวนหลักแสนบรรทัด

**ทางแก้ที่ดีที่สุด:** ฟอนต์ Custom ยุคใหม่ถูกพัฒนาให้รองรับการจัดเรียง **Standard Thai Unicode (UTF-8)** ได้ในตัว เราจึงทำการ **ข้าม (Bypass) กระบวนการแปลง PUA ทั้งหมด** และ Inject ภาษาไทยดิบๆ เข้าไปตรงๆ ผลลัพธ์คือการแพ็กไฟล์เสร็จสิ้นภายใน "ไม่กี่วินาที" และข้อความในเกมแสดงผลถูกต้อง 100%

### 🚨 ปัญหา DLC Strings โชว์เป็นภาษาอังกฤษแม้แปลแล้ว
บ่อยครั้งที่ผู้เล่นแจ้งว่าเควส DLC (เช่น Steeltown) ยังเป็นภาษาอังกฤษ ทั้งที่ไฟล์แพ็กเสร็จสมบูรณ์แล้ว
**สาเหตุ:** 
1. ผู้เล่นไม่ได้แตกไฟล์ Mod นำโฟลเดอร์ `DLC1` และ `DLC2` ไปวางทับโฟลเดอร์ต้นฉบับใน `WL3_Data/StreamingAssets/aa/StandaloneWindows64/` (บางคนก๊อปปี้ไปแค่ไฟล์ Base Game)
2. สตรีมคลาวด์ (Steam Cloud) หรือระบบอัปเดตแอบกู้คืนไฟล์ DLC ดั้งเดิม

**วิธีตรวจสอบ:** ตรวจสอบขนาดไฟล์ (File Size) และ วันที่แก้ไข (Date Modified) ของไฟล์ `.bundle` ในเครื่องผู้เล่น หากไม่ตรงกับตัว Mod แปลว่าวางทับไม่สำเร็จ

---

## 5. สรุป Workflow ของ Packer Script
1. อ่านไฟล์ CSV เข้ามาเป็น Dictionary (`ID` เป็น Key, `Translation` เป็น Value)
2. โหลด `.bundle` ด้วย `UnityPy`
3. วนลูปหา `StringTableData_English`
4. วนลูปหา ID ในตาราง หากตรงกัน ให้แทนที่ `defaultTexts[i]` ด้วยข้อความที่แปลแล้ว
5. สั่ง `env.save(packer="lz4")` เขียนไฟล์ใหม่ลงโฟลเดอร์ Mod
6. แจกจ่ายไฟล์ `.bundle` พร้อมฟอนต์ BepInEx ให้ผู้ใช้ก๊อปปี้ทับโฟลเดอร์เกม
