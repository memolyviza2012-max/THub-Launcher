# 🛡️ Outpost: Infinity Siege — Thai Localization Bible (คัมภีร์ม็อดภาษาไทยฉบับสมบูรณ์)
**เวอร์ชันม็อด:** v1.0 | **ผู้จัดทำ:** หน๊ด หนวด translator (NodNuatTranslator)  
**เกมเอนจิ้น:** Unreal Engine 4/5 (U01 Game Module Architecture)  
**จำนวนข้อความที่แปล:** 8,950 ประโยค / บรรทัด (TStudio Input)  

---

## 1. ภาพรวมโปรเจกต์และสถาปัตยกรรมเกม (Overview & Architecture)

เกม **Outpost: Infinity Siege** พัฒนาขึ้นบน Unreal Engine โดยมีโครงสร้างตัวเกมหลักอยู่ภายใต้โฟลเดอร์โมดูลชื่อ **`U01`** (แทนที่จะเป็นชื่อโฟลเดอร์เกมทั่วไป):
- **Executable & Binaries:** `Outpost\U01\Binaries\Win64\Outpost-Win64-Shipping.exe`
- **Asset Packages (Paks):** `Outpost\U01\Content\Paks\`
- **Localization Files:** ไฟล์ข้อความเกมถูกจัดเก็บเป็นไบนารี `.locres` (Unreal Localization Resource) อยู่ใน `U01\Content\Localization\`
- **Font & Typography:** ใช้ระบบ Slate UFont ผสมผสานระหว่างฟอนต์ภาษาจีน (NotoSansSC) และฟอนต์ระบบ (Roboto / DroidSansFallback)
- **Mod Signature Verification:** ตัวเกมมีการเปิดระบบตรวจสอบความถูกต้องของไฟล์ Pak (Signature Lock) ทำให้การลงม็อดทั่วไปจะไม่โหลด จำเป็นต้องใช้ตัวปลดล็อค Signature Bypass (`dsound.dll` + `UniversalSigBypasser.asi`)

---

## 2. เครื่องมือประจำโปรเจกต์ (Required Tools)

| เครื่องมือ | เส้นทางที่ติดตั้ง | บทบาทการทำงาน |
| :--- | :--- | :--- |
| **UnrealLocres.exe** | `E:\Mod_Workspace\Tool\UnrealLocres.exe` | ใช้แตกไฟล์และแพ็คไฟล์ `.locres` แปลงเป็น/จาก CSV |
| **repak.exe** | `E:\Mod_Workspace\Tool\repak_cli\repak.exe` | CLI ความเร็วสูงสำหรับสร้างไฟล์ Unreal `.pak` (V9/V11) |
| **TStudio** | `modder-hub/tools/flagship/TStudio` | หน้าต่างแปลภาษา GUI พร้อมระบบจัดการ Glossary และ Tag Shield |
| **TRun** | `modder-hub/tools/flagship/TRun` | Batch Translation Engine แปลภาษาไทยอัตโนมัติ 8,950 บรรทัด |
| **UniversalSigBypasser** | `dsound.dll` & `*.asi` | DLL Hook สำหรับบายพาสการตรวจจับ Pak Signature ใน Unreal Engine |

---

## 3. ขั้นตอนการสกัดข้อความ (Text Extraction & Unpacking)

ข้อความเกมอยู่ในโฟลเดอร์ `U01\Content\Localization\**\en\*.locres` โดยถูกสกัดผ่านสคริปต์ `outpost_unpacker.py`:

```python
# รูปแบบคำสั่งการใช้งาน
python outpost_unpacker.py --locres_dir "[Path_to_Extracted_Localization]" --output_csv "TStudio_Input.csv"
```

### กลไกการทำงานสำคัญ:
1. สแกนค้นหาไฟล์ `.locres` ภาษาอังกฤษ (`en/*.locres`) ทั้งหมด
2. รันคำสั่ง `UnrealLocres.exe export [file.locres]` เพื่อแปลงเป็น CSV ชั่วคราว
3. สร้าง Composite Key ในรูปแบบ:
   ```text
   [TargetName]||[KeyID]
   ตัวอย่าง: OP_ST_UI||EnterStoryTipsContext_WithSpiderTankFail::1867131323
   ```
4. รวบรวมข้อความทั้งหมดออกมาเป็น **TStudio CSV** (มีคอลัมน์ `Key`, `Source`, `Translation`) รวมทั้งสิ้น **8,950 ประโยค**

---

## 4. สถาปัตยกรรมฟอนต์และการแก้สระลอย (Font Architecture)

Unreal Engine ในเกมนี้ใช้ฟอนต์หลายตัวสำหรับ UI และเมนูต่างๆ หากไม่ทำการแทนที่ให้ครบจะเกิดปัญหาฟอนต์สี่เหลี่ยม (Tofu □□□) ในบางหน้าต่าง

### รายการ Font Overrides ที่ต้องแทนที่ด้วยฟอนต์ไทย (13 ไฟล์):
```
U01\Content\MainAsset\TextLibrary\Fonts\NotoSansSC-Bold.ufont
U01\Content\MainAsset\TextLibrary\Fonts\NotoSansSC-Regular.ufont
U01\Content\MainAsset\TextLibrary\Fonts\NotoSansSC-Medium.ufont
U01\Content\MainAsset\TextLibrary\Fonts\NotoSansSC-Light.ufont
U01\Content\MainAsset\TextLibrary\Fonts\NotoSansSC-Thin.ufont
U01\Content\MainAsset\TextLibrary\Fonts\NotoSansSC-Black.ufont
U01\Content\MainAsset\TextLibrary\Fonts\ZiTiQuanXinYiGuanHeiTi3_0-2.ufont
Engine\Content\EngineFonts\Faces\RobotoBold.ufont
Engine\Content\EngineFonts\Faces\RobotoRegular.ufont
Engine\Content\EngineFonts\Faces\RobotoLight.ufont
Engine\Content\EngineFonts\Faces\RobotoItalic.ufont
Engine\Content\EngineFonts\Faces\DroidSansFallback.ufont
Engine\Content\Slate\Fonts\DroidSansFallback.ttf
```
*เทคนิค:* สคริปต์ `outpost_packer.py` จะคัดลอกไฟล์ฟอนต์ภาษาไทย (เช่น Noto Sans Thai / Sarabun) ไปเขียนทับเป็นชื่อไฟล์ฟอนต์เดิมทั้งหมด แล้วนำไปแพ็กรวมไว้ในตัวม็อด Pak เดียวกัน

---

## 5. การแพ็คไฟล์ม็อดกลับเข้าเกม (Repacking & Mod Injection)

ใช้สคริปต์ `outpost_packer.py` ในการสร้างไฟล์ `.pak` สำหรับแจกจ่าย:

```python
python outpost_packer.py \
    --csv "TStudio_Output.csv" \
    --base_locres_dir "[Original_Locres_Folder]" \
    --font "E:\Mod_Workspace\Fonts\ThaiFont.ttf" \
    --output_pak "pakchunk999-ThaiMod_P.pak"
```

### ลำดับขั้นตอนการทำงานของสคริปต์:
1. อ่านไฟล์แปลภาษาไทย แยกกลุ่มข้อมูลตาม `TargetName`
2. สร้างไฟล์ CSV เฉพาะของแต่ละ Target แล้วเรียก `UnrealLocres.exe import` เพื่อแปลงกลับเป็น `.locres` ภาษาไทย
3. จัดวางไฟล์ในโครงสร้างโฟลเดอร์เสมือน:
   - `U01\Content\Localization\...` (ไฟล์ .locres แปลไทย)
   - `U01\Content\MainAsset\TextLibrary\Fonts\...` (ฟอนต์ไทย)
   - `Engine\Content\EngineFonts\...` (ฟอนต์ระบบ)
4. สั่ง `repak.exe pack` เพื่อบีบอัดเป็นไฟล์ `pakchunk999-ThaiMod_P.pak`

---

## 6. การจัดทำแพ็คเกจสำหรับแจกจ่าย (06_Releases & Distribution)

โครงสร้างโฟลเดอร์สำหรับแจกจ่ายถูกออกแบบให้ **"ผู้เล่นสามารถ Copy วางทับตัวเกมได้ทันทีแบบ Zero-Friction"**:

### โครงสร้างไฟล์ใน Zip แจกจ่าย (`Outpost_ThaiMod_v1.0.zip`):
```
Outpost_ThaiMod_v1.0/
├── คู่มือติดตั้ง_README.txt
└── U01/
    ├── Binaries/
    │   └── Win64/
    │       ├── dsound.dll               (ตัวโหลด ASI / SigBypass Hook)
    │       └── UniversalSigBypasser.asi  (ตัวปลดล็อคการตรวจสอบ Signature ของ Pak)
    └── Content/
        └── Paks/
            └── ~mods/
                └── pakchunk999-ThaiMod_P.pak (ไฟล์แปลภาษาไทย + ฟอนต์ไทย)
```

---

## 7. ต้นแบบคู่มือการติดตั้ง (Installation Guide Template)

ไฟล์ `คู่มือติดตั้ง_README.txt` ถูกแนบไปพร้อมกับตัวม็อดเสมอ:

```
=============================================================
      Mod ภาษาไทย สำหรับเกม Outpost: Infinity Siege (v1.0) NodNuatTranslator
=============================================================

รายละเอียดการแปล:
-------------------------------------------------------------
แปลภาษาไทยครบถ้วนสมบูรณ์ ทั้งหมด 8,950 ประโยค/บรรทัด

วิธีติดตั้ง (Installation):
-------------------------------------------------------------
1. แตกไฟล์ Zip ที่ดาวน์โหลดมา
2. คุณจะเห็นโฟลเดอร์ชื่อ "U01"
3. ให้นำโฟลเดอร์ "U01" นี้ ไปวางทับในโฟลเดอร์เกม Outpost ของคุณ
   (ตัวอย่างพาทของเกม: SteamLibrary\steamapps\common\Outpost)
4. หากระบบถามให้เขียนทับหรือรวมโฟลเดอร์ ให้กดยอมรับ (Replace/Merge)
5. เข้าเกมและสนุกได้เลย!

* โครงสร้างของ Mod ที่จะถูกติดตั้งเข้าไป:
  1. ไฟล์แปลภาษา: Outpost\U01\Content\Paks\~mods\pakchunk999-ThaiMod_P.pak
  2. ตัวปลดล็อค Mod (SigBypass): Outpost\U01\Binaries\Win64\dsound.dll และ UniversalSigBypasser.asi
  (เนื่องจากเกมนี้มีการล็อคไฟล์ Mod จึงจำเป็นต้องมีตัวปลดล็อคนี้รวมอยู่ด้วย เครื่องอื่นๆ จึงจะสามารถโหลดภาษาไทยได้ครับ)

วิธีลบ Mod ออก (Uninstall):
-------------------------------------------------------------
เข้าไปลบไฟล์ "pakchunk999-ThaiMod_P.pak" ออกจากโฟลเดอร์ 
\Outpost\U01\Content\Paks\~mods เพียงเท่านี้เกมจะกลับเป็นภาษาเดิมครับ

=============================================================
ขอให้สนุกกับการเล่นเกมภาษาไทยครับ!
=============================================================

สามารถสนับสนุนได้ตามช่องทางด้านล่างนี้เลยครับ ขอบคุณทุกการสนับสนุนครับ!
ช่องทางสนับสนุน: สนับสนุน
สามารถติดตามช่องทาง mod อื่นได้ที่หน้าเว็บไซส์ : หน๊ด หนวด translator
ติดต่อพูดคุยผ่าน Facebook : หน๊ด หนวด translator
ผู้จัดทำ: หน๊ด หนวด translator (NodNuatTranslator)
```

---

## 8. สรุปบทเรียนทางเทคนิค (Technical Takeaways)
1. **Unreal Engine Custom Module Naming:** เกม Unreal ไม่ได้ใช้ชื่อเกมเสมอไป ในกรณีนี้ใช้โมดูล `U01` การเขียนสคริปต์และจัดแพ็คเกจต้องอ้างอิงตามชื่อโมดูลจริงของเกม
2. **Signature Bypass is Mandatory:** เกม Unreal Engine สมัยใหม่หลายเกมบล็อก `~mods` ผ่าน Pak Signature Check การรวม `dsound.dll` และ `UniversalSigBypasser.asi` เข้าไปในแพ็คเกจ ทำให้ผู้เล่นทั่วไปไม่ต้องติดตั้งโปรแกรมอื่นเสริม
3. **Comprehensive Font Replacement:** การแทนที่ทั้ง 13 จุดทั้งใน Game Content และ Engine Faces ป้องกันอาการสระลอยและตัวหนังสือสี่เหลี่ยมได้อย่างสมบูรณ์แบบ
