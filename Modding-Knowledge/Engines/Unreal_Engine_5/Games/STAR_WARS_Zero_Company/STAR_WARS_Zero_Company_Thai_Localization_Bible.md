# STAR WARS Zero Company — Thai Localization Bible

> สถานะ: ใช้งานได้จริงกับเกม build `196320` และ Thai Mod `v1.0.0`  
> Engine: Unreal Engine 5, hybrid PAK + IoStore (`.pak`, `.utoc`, `.ucas`)

## 1. เป้าหมายและผลลัพธ์ที่พิสูจน์แล้ว

โปรเจกต์นี้ทำให้ผู้เล่นเลือก `Thai` ได้จาก **Options > Interface > Text Language** โดยไม่แทนที่ภาษา English หรือ Spanish และเกม render ภาษาไทยได้อย่างถูกต้อง รวมถึงสระและวรรณยุกต์

- Game LOCRES: 26,642 entry
- คำแปลที่ pack: 26,642 entry
- ฟอนต์: IBM Plex Sans Thai ที่แก้แล้ว
- Mod container: `pakchunk999-Windows_ThaiFont_EN_P.pak` พร้อม `.utoc` และ `.ucas`

## 2. โครงสร้างไฟล์เกมที่เกี่ยวข้อง

```text
Star Wars Zero Company\
└─ SWZeroCompany\
   ├─ Binaries\Win64\
   │  ├─ dsound.dll
   │  └─ UniversalSigBypasser.asi
   └─ Content\Paks\
      ├─ pakchunk0-Windows.pak
      ├─ global.utoc
      ├─ global.ucas
      ├─ pakchunk999-Windows_ThaiFont_EN_P.pak
      ├─ pakchunk999-Windows_ThaiFont_EN_P.utoc
      └─ pakchunk999-Windows_ThaiFont_EN_P.ucas
```

ข้อค้นพบสำคัญ:

- `global.utoc/.ucas` เป็น IoStore metadata/data ไม่ใช่ตำแหน่งที่ต้องแก้ข้อความหลัก
- ข้อความเกมหลักอยู่ที่ `SWZeroCompany/Content/Localization/Game/en/Game.locres` ภายใน `pakchunk0-Windows.pak`
- รายชื่อภาษาที่ Options อ่านจาก `SWZeroCompany/Content/Localization/Game/Game.locmeta`
- ตัว PAK overlay ต้องชื่อท้าย `_P.pak` และอยู่ใน `SWZeroCompany/Content/Paks`

## 3. เครื่องมือ

| งาน | เครื่องมือ |
|---|---|
| อ่าน/ดึงไฟล์ UE | CUE4Parse CLI |
| Export/Import LOCRES | UnrealLocres.exe |
| Pack/Unpack legacy PAK | repak CLI |
| แปลชุดใหญ่ | THub TRun / TStudio |
| ปลด signature check | UniversalSigBypasser |

ห้ามแก้ไฟล์ engine ของ THub ได้แก่ `trun_app.py`, `tstudio_app.py`, `tstudio_core.py`, และ `file_converter.py`.

## 4. ขั้นตอนดึงข้อความ

1. ดึง `Game.locres` จาก PAK ต้นฉบับด้วย CUE4Parse
2. Export ด้วย UnrealLocres เป็น CSV
3. แปลงเป็น TStudio CSV มาตรฐาน:

```text
key | source | translation | context | file_path
```

4. ใช้ TRun/TStudio แปลเฉพาะคอลัมน์ `translation`
5. ห้ามแก้ `key`, `source`, `context`, `file_path`

CSV หลักของโปรเจกต์อยู่ที่:

```text
02_Translation_Workspace\STAR_WARS_Zero_Company_full_en_to_th.csv
02_Translation_Workspace\STAR_WARS_Zero_Company_full_en_to_th_translated.csv
```

## 5. กฎ protected tags (สำคัญที่สุด)

ข้อความ UE มี game-code แทรกอยู่ เช่น:

```text
<Bold>...</>
<Keyword id="UI.Keyword.Damage.Blaster">...</>
<input id="InputAction.Tactical.CursorSelect"/>
{0}
%s
\n / \r
```

tag เหล่านี้ต้องคงเดิมแบบ byte-for-byte และเรียงลำดับเดิม ห้ามแปลค่า `id` ภายใน tag

ตัวอย่างถูกต้อง:

```text
<Keyword id="UI.Keyword.Damage.Blaster">ความเสียหายบลาสเตอร์</>
```

ตัวอย่างผิด:

```text
<Keyword id="UI.Keyword.Damage.ปืนบลาสเตอร์">ความเสียหายบลาสเตอร์</>
```

หาก tag หาย/เปลี่ยน packer ต้องไม่ pack แถวนั้น เพราะอาจทำให้ UI หรือ runtime format ผิดพลาดได้

## 6. สร้างภาษา Thai โดยไม่แทนที่ภาษาเดิม

1. คัดลอก `Game.locmeta` มาใน overlay PAK
2. เพิ่ม culture `th` ตามรูปแบบข้อมูลเดิมของ LOCMETA
3. Import คำแปลเป็น:

```text
SWZeroCompany/Content/Localization/Game/th/Game.locres
```

4. อย่าสร้าง Thai โดยแทน `en` หรือ `es-ES` เพราะจะทำให้ภาษาเดิมหายจากเมนู
5. เมื่อเลือก Thai เกมจะโหลด `th/Game.locres`; English/Spanish ยังคงทำงานตามปกติ

## 7. แก้ฟอนต์ไทย

ฟอนต์ default ของเกมไม่มี Thai glyph จึงต้อง override ฟอนต์หลักของ UMG/Slate ด้วยฟอนต์ Thai ที่รองรับ Unicode และ combining marks

ฟอนต์ที่พิสูจน์แล้ว:

```text
E:\Mod_Workspace\Tool\1_ThaiFont\fonts_main\1_IBMPlexSans_fixByNodNuatTranslator_2.ttf
```

รูปแบบ `.ufont` ของเกม:

```text
uint32 little-endian: ขนาด TTF/OTF
raw OpenType bytes
```

ต้อง override UFont หลัก 22 ไฟล์ และ Slate TTF 14 ไฟล์ แต่ **ห้าม override** ฟอนต์ CJK/Arial Unicode เหล่านี้ เพราะภาษาใน language selector จะกลายเป็น `()` หรือว่าง:

```text
ArialUnicodeMS.ufont
Chinese*.ufont
Japanese*.ufont
Korean*.ufont
```

## 8. Pack overlay

ใช้ legacy PAK format `V11`, mount point `../../../` และสร้าง PAK ที่มีอย่างน้อย:

```text
SWZeroCompany/Content/Localization/Game/Game.locmeta
SWZeroCompany/Content/Localization/Game/th/Game.locres
Engine/.../*.ufont                 (Thai font overrides)
Engine/Content/Slate/Fonts/*.ttf   (Thai font overrides)
```

คำสั่งตัวอย่าง:

```powershell
repak pack <staging-folder> pakchunk999-Windows_ThaiFont_EN_P.pak --mount-point ../../../ --version V11
```

สำหรับเกมนี้ต้องแจก companion container ด้วย:

```text
pakchunk999-Windows_ThaiFont_EN_P.pak
pakchunk999-Windows_ThaiFont_EN_P.utoc
pakchunk999-Windows_ThaiFont_EN_P.ucas
```

## 9. Pre-pack validation

ก่อน pack ทุกครั้ง:

1. ตรวจ key ไม่ซ้ำ
2. ตรวจ source ใน translated CSV ตรงกับ source CSV
3. ตรวจ protected tags/placeholder ตรงกัน
4. สร้าง report แยกสำหรับแถวผิด
5. import LOCRES และตรวจจำนวน entry เท่าต้นฉบับ 26,642
6. backup PAK เป้าหมายไป `01_Original_Backup` และลง `session_log.md` ก่อน copy เข้า Game Directory

ในโปรเจกต์นี้ใช้สคริปต์:

```text
SWZeroCompany_repair_protected_tags.py
SWZeroCompany_sanitize_translation.py
SWZeroCompany_packer.py
```

ผลรอบ v1.0.0:

- tag ที่คืนอัตโนมัติ: 121 แถว
- tag ที่ตรวจแก้: 26 แถว
- final English fallback จาก protected tags: 0 แถว

## 10. การทดสอบในเกม

1. ติดตั้ง PAK และ UniversalSigBypasser
2. เปิดเกม > Options > Interface > Text Language > Thai
3. ตรวจ Main Menu, Text Language list, tutorial, tooltip, combat UI, dialogue และหน้าจอ loading
4. เกณฑ์ผ่าน: ไม่มี tofu `□`, ไม่มีอักขระเพี้ยน, สระ/วรรณยุกต์ถูกตำแหน่ง, ไม่มี crash

## 11. การปล่อย Release

สร้าง ZIP ที่เมื่อแตกแล้วมีโครงสร้างตรงกับ root เกม:

```text
STAR_WARS_Zero_Company_Thai_Mod_v1.0.0\
├─ README_TH.txt
└─ SWZeroCompany\
   ├─ Binaries\Win64\
   │  ├─ dsound.dll
   │  └─ UniversalSigBypasser.asi
   └─ Content\Paks\
      ├─ pakchunk999-Windows_ThaiFont_EN_P.pak
      ├─ pakchunk999-Windows_ThaiFont_EN_P.ucas
      └─ pakchunk999-Windows_ThaiFont_EN_P.utoc
```

ผู้เล่นเพียง copy โฟลเดอร์ `SWZeroCompany` ไปวางทับในโฟลเดอร์เกม แล้วเลือก Thai ใน Options.
