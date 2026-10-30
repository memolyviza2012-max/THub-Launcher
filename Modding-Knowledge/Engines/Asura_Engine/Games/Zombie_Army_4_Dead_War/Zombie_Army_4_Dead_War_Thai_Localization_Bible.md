# Thai Localization Bible — Zombie Army 4: Dead War

> สถานะ: วิเคราะห์จากตัวติดตั้งม็อดภาษาไทยแบบไม่รันโปรแกรม และจาก payload ที่สกัดได้
> วันที่วิเคราะห์: 2026-08-30 | ผู้สร้างม็อดที่ระบุในชื่อแพ็กเกจ: Lung Dear

## 1. Game & Engine Profile

| รายการ | หลักฐาน/ค่า |
|---|---|
| เกม | Zombie Army 4: Dead War |
| Engine ที่ยืนยันจากไฟล์ | Asura Engine (resource header เป็น ASCII `Asura   ` ทุกชนิด) |
| รูปแบบม็อด | ตัวติดตั้ง PyInstaller ที่บรรจุ payload สำหรับแทนที่ไฟล์ English ของเกม |
| ขอบเขตที่ผู้สร้างระบุ | 25,992 ข้อความ, 15,299 บรรทัด; เมนู, เควสต์, ไอเทม, อาวุธ, เครดิต และบทสนทนามิชชัน |
| เวอร์ชันที่ README ระบุ | Zombie Army 4 Dead War v1.0 |

## 2. Source, Provenance & Safety

- แหล่งวิเคราะห์: `D:\Mods games\Thai Mods\0_Rivet Engineer\Zombie Army 4 Dead War Mod TH By Lung Dear 4 1 2026-08-30T03-54Z lBecKyHXf`
- ไฟล์ต้นทางมี `ZombieArmy4_ThaiMod_Setup.exe` ขนาด 140,168,831 bytes, SHA-256 `5735A5509D6F0F285D5E4319E7F0C345190F9EE399A8FF6EDDD505D5C09221A3`.
- ไม่ได้รันตัวติดตั้งกับเกมหรือระบบจริง ใช้ `pyinstxtractor.py` แบบอ่านอย่างเดียวในการแยก CArchive; ตรวจพบ PyInstaller 2.1+ และ Python 3.12, entry point คือ `installer.pyc`.
- payload ที่แยกได้มี 37 ไฟล์ รวม 368,888,418 bytes และตรงกับ README ที่กล่าวว่าติดตั้ง Fonts 3, Text 7, Environments 26 และ sound metadata 1 ไฟล์.

## 3. File Map & Magic Bytes

| กลุ่ม | จำนวน | ส่วนหัวที่ตรวจด้วย magic bytes | ข้อสรุปที่ยืนยันได้ |
|---|---:|---|---|
| `Fonts/*.asr` | 3 | `41 73 75 72 61 20 20 20 52 53 46 4C` = `Asura   RSFL` | archive/resource font library ของ Asura |
| `Text/PC/**/*.asr_en` | 7 | `41 73 75 72 61 20 20 20 48 54 58 54` = `Asura   HTXT` | ตารางข้อความภาษา English ที่ถูกแทนที่โดยม็อด |
| `Envs/**/*.pc_en` | 26 | `Asura   DLET` หรือ `Asura   DLLT` | resource ภาษา/บทสนทนาระดับ map/environment |
| `sounds/gmsndmeta.asr_en` | 1 | `Asura   DLET/DLLT` | metadata เสียง/ซับไตเติลที่เกี่ยวข้อง |

อย่าเปลี่ยนนามสกุลหรือแก้ hex ตามการคาดเดา: `RSFL`, `HTXT`, `DLET`, และ `DLLT` เป็น container/protocol เฉพาะของ Asura ที่ตรวจจาก byte จริง ไม่ใช่ไฟล์ข้อความธรรมดา.

## 4. Text Localization Architecture

- ตัวติดตั้งให้เลือกภาษา **English** และวางไฟล์ suffix `_en` ทับไฟล์ภาษา English เดิม; เป็น replacement mod ไม่ใช่ locale ใหม่ที่เลือกจากเมนูเกม.
- ตาราง UI/ระบบอยู่ใต้ `Text/PC`: `credits`, `cutscene`, `dlc_ir_1`, `engine`, `menu`, `objectives`, `presence`.
- บทสนทนาและข้อความตามด่านอยู่ใต้ `Envs`: DLC 4–11, Horde/Railyard, Hellbase, ItalianCity, LavaTown, MilBaseWoods, Rural, StPeters, TrainStation, Venice และ Zoo.
- การสแกน UTF-8 ตรง ๆ ไม่พบข้อความไทยที่ถอดออกมาได้ใน `HTXT`/`DLET` จึงห้ามสรุป encoding หรือจำนวน record จากการเดา; ต้องใช้ parser/repacker ที่เข้าใจ Asura format ก่อนแก้ข้อความรายบรรทัด.

## 5. Font System & Extracted Assets

ฟอนต์เป็นส่วนบังคับของม็อด: README ระบุว่า bake อักขระไทยลงฟอนต์ที่ตรงกับฟอนต์อังกฤษ และแก้ปัญหาสระ/วรรณยุกต์ลอย.

| Asset ที่เก็บแล้ว | ขนาด | SHA-256 | หลักฐานภายใน |
|---|---:|---|---|
| `Assets/Payload/Fonts/fonts.asr.zip` | 70,235,935 (แตก zip: 232,298,851) | `D6FAF4B8C15654883EC83530126F6B14867C9136C3C66AAFA4AB8C61DCC4E05C` | `RSFL`; บีบอัด zip เพื่อไม่ให้เกินขีดจำกัด 100MB ของ GitHub (แตก zip เป็น fonts.asr ใช้งานได้ทันที) |
| `Assets/Payload/Fonts/fonts_console.asr` | 32,691,299 | `0564EB77936EAC31676498815002406DCC6D5D34F15AB129B4A1B048ACA779CA` | `RSFL`; พบ `DDS ` |
| `Assets/Payload/Fonts/fonts_minspec.asr` | 58,909,235 | `FA25154F9907AD16ABB897E6BB77DD1D4A21B482CC9EDADBA46E526D42BD9A15` | `RSFL`; พบ `DDS ` |

ชื่อ resource/atlas ที่พบจริงรวม `DemonicFont`, `SerifGothic_Black`, `SerifGothic_Heavy`, `HUD_Base01`, `Frontend_Base02` และไฟล์ `\graphics\fonts\*.dds`. จัดเก็บ payload ดิบครบทั้ง 37 ไฟล์ที่ `Assets/Payload/` เพื่อให้กู้คืนและเทียบไบต์ได้. ยังไม่มีตัวถอด RSFL ที่ตรวจสอบความถูกต้องได้ จึงไม่ carve DDS/OTF แบบเดาความยาวไฟล์.

## 6. Encoding, Glyph & Rendering Rules

- การมี Thai glyph ใน atlas ไม่ยืนยัน encoding ของ `HTXT`; ต้องแยกการพิสูจน์ **text encoding** ออกจาก **font glyph coverage**.
- ห้าม re-bake เฉพาะ `fonts.asr`: ม็อดมีชุด normal, console และ minspec; เวอร์ชันที่ใช้จริงต้องให้ glyph/metrics สอดคล้องกันทั้งสามชุด.
- ตรวจในเกมอย่างน้อย UI หลัก, HUD, subtitle, หนังสือ/credit และ dialogue map หลังแก้ เพื่อจับ clipping, baseline, สระบน, วรรณยุกต์ และ line-wrap.
- เก็บ backup ของไฟล์เกมเดิมก่อนติดตั้งทุกครั้ง; README ของม็อดระบุว่าตัวติดตั้ง backup เฉพาะไฟล์ที่ตัวม็อดแก้.

## 7. Safe Editing / Repacking Workflow

1. สำรองไฟล์ English เดิมของเกมและบันทึก SHA-256 ของทั้ง input/output.
2. ใช้เครื่องมือ Asura ที่พิสูจน์แล้วว่าสามารถ decode และ repack `HTXT`, `DLET`/`DLLT`, `RSFL` ได้โดยไม่ทำลาย table/offset/checksum.
3. แก้ข้อความในสำเนาที่ decode ได้ โดยรักษา key, record order, control token และ placeholder ทุกตัว.
4. ถ้าจำเป็นต้องเพิ่ม glyph ให้ build atlas/metrics ผ่าน pipeline เดียวกับ font resource แล้ว repack ฟอนต์ทั้งสามชุด.
5. ติดตั้งกับสำเนาเกมทดสอบที่เลือก English; ทดสอบเมนู, HUD, subtitle, DLC และ map ที่มีกล่องข้อความยาว.
6. เปรียบเทียบ hash/ขนาดและเปิดเกมทดสอบก่อนแจกจ่าย. ห้ามใช้การ replace byte แบบสุ่มหรือเปลี่ยน extension เป็น `.txt`.

## 8. Install / Uninstall Notes

- README ระบุให้รัน installer ด้วยสิทธิ์ Administrator, หาโฟลเดอร์เกม, กดติดตั้ง และเลือก English ในเกม.
- สำหรับการทำงานวิศวกรรมย้อนกลับ ไม่ควรรัน EXE ที่ไม่ผ่านการตรวจในเครื่องใช้งานหลัก; ใช้ payload ที่เก็บไว้แทน.
- การถอนควรคืนไฟล์ backup ที่ตรงเวอร์ชันเกม ไม่ใช่ลบโฟลเดอร์ resource แบบกว้าง ๆ.

## 9. Cross-Engine Comparison & Knowledge-Base Check

- ตรวจ `MASTER_INDEX.md` และ `Engines/` แล้วไม่พบรายการ Asura Engine หรือ Zombie Army 4 เดิม ณ วันที่วิเคราะห์ จึงเป็น baseline แรกของ engine นี้ในฐานความรู้.
- ต่างจาก mod ที่ใช้ `.pak` (Unreal) หรือ bundle มาตรฐาน (Unity): header `Asura` และชนิด `RSFL`/`HTXT`/`DLET` ที่พบที่นี่ต้องใช้ parser เฉพาะ Asura; pipeline ของ engine อื่นนำมาใช้ reimport โดยตรงไม่ได้.
- สิ่งที่ใช้ร่วมกันได้ข้าม engine คือหลักฐาน magic bytes, hash ก่อน/หลังแก้, เก็บ asset ดิบ, และทดสอบ glyph + UI ทุกบริบท—not binary layout.

## 10. Confidence, Gaps & Next Research

| หัวข้อ | ระดับ | เหตุผล |
|---|---|---|
| การระบุ Asura/resource family | สูง | ทุกชนิดเริ่มด้วย `Asura` และ tag เฉพาะที่ตรวจจากไฟล์ |
| เส้นทาง text/font ที่ม็อดแก้ | สูง | payload 37 ไฟล์ตรงกับรายการใน README และชื่อ resource font/atlas ถูกพบใน RSFL |
| รูปแบบ record/encoding/checksum ภายใน | ต่ำ | ยังไม่มี decoder/repacker Asura ที่ validate ได้ในเครื่อง |
| การใช้งาน glyph แต่ละ atlas | ปานกลาง | ชื่อ atlas ยืนยันได้ แต่ mapping และ metrics ต้อง parse RSFL |

งานถัดไป: หา/สร้าง parser ที่อ่าน directory และ record ของ `RSFL`/`HTXT`/`DLET` อย่างตรวจสอบได้, dump ออกมาเทียบกับไฟล์ English ต้นฉบับเวอร์ชันเดียวกัน, แล้วจึงสร้าง extractor สำหรับ atlas DDS และ table text. บันทึกนี้ตั้งใจรักษาขอบเขตระหว่างสิ่งที่พิสูจน์แล้วกับสิ่งที่ยังไม่ทราบ.
