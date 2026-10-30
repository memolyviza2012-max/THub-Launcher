# คัมภีร์: การดัดแปลงโปรเจค Marvel's GOTG เพื่อรองรับภาษายูเครน (Ukrainian Localization)

คู่มือฉบับนี้จะจับมือทำทีละขั้นตอน (Step-by-Step) เพื่อดัดแปลงโปรเจค `version.dll` (ที่เดิมทีใช้สำหรับภาษาไทย) ให้สามารถอ่านและแสดงผล **ภาษายูเครน (อักษร Cyrillic)** ในเกม Marvel's Guardians of the Galaxy ได้สำเร็จ

---

## 🛠️ สรุปหลักการทำงานของ Mod
ตัวเกมดั้งเดิมใช้เอนจิ้น Dawn Engine ซึ่งจะใช้ฟังก์ชั่น `FT_New_Memory_Face` (จากไลบรารี FreeType) ในการโหลดฟอนต์จากไฟล์ในตัวเกม
ตัว Mod ของเราใช้ **MinHook** ในการเข้าไปแทรกแซง (Detour) การทำงานของ 2 ส่วนหลักคือ:
1. **Font Hook:** สลับเอาไฟล์ฟอนต์ของเรา (`font_th.ttf` -> จะเปลี่ยนเป็น `font_uk.ttf`) ไปให้เกมโหลดแทน
2. **Text Hook:** ดักจับข้อความภาษาอังกฤษผ่าน `GetText` / `OnSetText` แล้วสลับเป็นคำแปลที่ดึงมาจากไฟล์ `strings.json`

ภาษายูเครนใช้อักษร **Cyrillic** ซึ่งทำงานบนระบบ Unicode (UTF-8) ได้ตามปกติเหมือนภาษาไทย แต่โชคดีกว่าตรงที่ไม่มีปัญหาสระลอย/จม จึงแทบไม่ต้องเขียนโค้ดจัดรูปแบบ (Text Shaping) เพิ่มเติม

---

## 📝 ขั้นตอนที่ 1: เตรียมไฟล์ฟอนต์ภาษายูเครน (Cyrillic Font)

เอนจิ้นของเกมต้องการไฟล์ฟอนต์ประเภท TrueType (`.ttf`) หรือ OpenType (`.otf`) ที่รองรับอักษร Cyrillic

1. หาฟอนต์ที่อ่านง่ายและเข้ากับธีมอวกาศ/ไซไฟ (เช่น *Roboto*, *Open Sans*, หรือฟอนต์เกม) ที่รองรับ **Cyrillic script**
2. เปลี่ยนชื่อไฟล์ฟอนต์นั้นเป็น `font_uk.ttf`
3. นำไฟล์ `font_uk.ttf` ไปวางเตรียมไว้ในโฟลเดอร์เดียวกับตัวเกม (ที่เดียวกับ `version.dll` เช่น โฟลเดอร์ `retail/`)

> [!IMPORTANT]
> ขนาดไฟล์ฟอนต์ไม่ควรใหญ่เกินไป (ไม่เกิน 5-10MB) เพราะตัว Mod จะต้องโหลดฟอนต์นี้เก็บไว้ใน RAM (Buffer) ตลอดเวลาที่เล่นเกม

---

## 📝 ขั้นตอนที่ 2: สร้างไฟล์แปลภาษา `strings_uk.json`

โปรเจคของเราใช้ JSON ในการเก็บคำแปล โครงสร้างคือ `"ประโยคภาษาอังกฤษดั้งเดิม" : "คำแปลภาษายูเครน"`

1. สร้างไฟล์ชื่อ `strings_uk.json`
2. บันทึกไฟล์ในรูปแบบ **UTF-8 (หรือ UTF-8 with BOM)** 
3. ตัวอย่างโครงสร้างในไฟล์:
```json
{
    "Start Game": "Почати гру",
    "Options": "Налаштування",
    "Quit": "Вийти",
    "I am Groot": "Я є Ґрут"
}
```
4. นำไฟล์ `strings_uk.json` ไปวางไว้ในโฟลเดอร์เดียวกับเกม

---

## 📝 ขั้นตอนที่ 3: แก้ไขโค้ด C++ (สลับจากไทยเป็นยูเครน)

ถึงเวลาเข้าไปแก้ Source Code ในโปรเจค (โฟลเดอร์ `02_Source_CPP`) เพื่อให้มันโหลดฟอนต์ยูเครนแทนฟอนต์ไทย

### 3.1 แก้ไขไฟล์ `TranslationHooks.cpp`

ค้นหาโค้ดส่วนที่เกี่ยวกับการโหลดฟอนต์ `font_th.ttf` แล้วเปลี่ยนเป็น `font_uk.ttf`

```diff
- // ตัวแปรสำหรับฟอนต์ไทย
- void* g_thai_font_buffer = nullptr;
- DWORD g_thai_font_size = 0;
- bool g_thai_font_loaded = false;

+ // ตัวแปรสำหรับฟอนต์ยูเครน
+ void* g_uk_font_buffer = nullptr;
+ DWORD g_uk_font_size = 0;
+ bool g_uk_font_loaded = false;
```

ในฟังก์ชั่นที่ติดตั้ง Hook (`install_all_hooks` หรือจุดที่เรียก `CreateFileW`):

```diff
- std::wstring font_path = std::wstring(exe_dir) + L"font_th.ttf";
+ std::wstring font_path = std::wstring(exe_dir) + L"font_uk.ttf";

  HANDLE hFont = CreateFileW(font_path.c_str(), GENERIC_READ, ...);
  if (hFont != INVALID_HANDLE_VALUE) {
-     g_thai_font_size = GetFileSize(hFont, nullptr);
-     g_thai_font_buffer = new char[g_thai_font_size];
+     g_uk_font_size = GetFileSize(hFont, nullptr);
+     g_uk_font_buffer = new char[g_uk_font_size];
```

และในฟังก์ชั่น `detour_FT_New_Memory_Face` (ตัวสลับฟอนต์ในหน่วยความจำ):

```diff
- if (g_thai_font_loaded && (file_size == 404856 || file_size == 241940)) {
+ if (g_uk_font_loaded && (file_size == 404856 || file_size == 241940)) {
      // สลับฟอนต์
-     return g_orig_FT_New_Memory_Face(library, g_thai_font_buffer, g_thai_font_size, face_index, aface);
+     return g_orig_FT_New_Memory_Face(library, g_uk_font_buffer, g_uk_font_size, face_index, aface);
  }
```

> [!NOTE]
> ตัวเลข `file_size == 404856` คือขนาดไฟล์ฟอนต์ต้นฉบับภาษาอังกฤษของเกม (UI Font) ถ้าเราต้องการแทนที่ฟอนต์ตัวไหน เราต้องรู้ขนาด Memory ของฟอนต์นั้นก่อน ซึ่งสามารถดูได้จาก `GOTG_Mod.log` เวลาเปิดโหมด Debug

### 3.2 แก้ไขไฟล์ `GOTG_Mod.ini` (ฝั่งผู้ใช้)

ปรับไฟล์การตั้งค่าเพื่อให้ชี้ไปยังไฟล์ JSON ของภาษายูเครนแทนภาษาไทย

```ini
[Language]
EnableTranslation=1
; ชี้ไปยังไฟล์แปลภาษายูเครน
StringsJSON=strings_uk.json
```

---

## 📝 ขั้นตอนที่ 4: การ Compile และนำไปใช้งาน

1. เปิด Command Prompt หรือ PowerShell ในโฟลเดอร์ `02_Source_CPP`
2. สั่งรันสคริปต์บิ้วท์: `build_cli.bat`
3. โปรเจคจะทำการ Compile ออกมาเป็นไฟล์ `version.dll`
4. นำไฟล์ทั้งหมดด้านล่างไปวางในโฟลเดอร์ `retail` ของตัวเกม:
   - `version.dll` (ที่เราเพิ่ง Compile)
   - `font_uk.ttf` (ฟอนต์ยูเครน)
   - `strings_uk.json` (คำแปล)
   - `GOTG_Mod.ini` (ไฟล์ตั้งค่า)

---

## 💡 ทิปส์เพิ่มเติมและข้อควรระวัง (Troubleshooting)

- **ตัวอักษรเป็นสี่เหลี่ยม (Tofu / □□□):** 
  แสดงว่าไฟล์ `font_uk.ttf` ที่คุณหามา ขาดตารางอักษร (Glyph) สำหรับ Cyrillic ให้ลองเปลี่ยนไปใช้ฟอนต์ตัวอื่นที่ระบุชัดเจนว่ารองรับ Cyrillic 100%
- **เกมเด้งตอนโหลดเข้าเมนู:** 
  อาจเกิดจากไฟล์ฟอนต์ขนาดใหญ่เกินไป หรือ Buffer ในโค้ด Hook เล็กเกินไป ให้ลองเช็ค `safe_buf` ในไฟล์ `TranslationHooks.cpp` ว่ารองรับขนาด string ยาวพอหรือไม่ (ยูเครนใช้ UTF-8 ซึ่ง 1 ตัวอักษรอาจกินพื้นที่ถึง 2-3 bytes)
- **การใช้ Regex หรือ Variables:**
  ในเกมจะมีโค้ดตัวแปร เช่น `[BTN_A]` หรือ `{0}` ให้คงรูปแบบตัวแปรเหล่านี้ไว้ใน `strings_uk.json` เป๊ะๆ ห้ามลบหรือแปลส่วนนี้ เพราะจะทำให้เกมค้างเวลาพยายามแสดงผลปุ่มกด
