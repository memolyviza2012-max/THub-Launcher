# Atelier Ryza: Ever Darkness & the Secret Hideout — Thai Localization Bible

> คู่มือสร้าง ดูแล ตรวจสอบ และออกชุดแจกม็อดภาษาไทยฉบับใช้งานจริง  
> ม็อดสาธารณะ: **Atelier Ryza Thai Mod v1.0** (internal build v22)  
> ผู้จัดทำ/ผู้แปล: **หน๊ด หนวด translator (NodNuatTranslator)**  
> แพลตฟอร์มที่ตรวจสอบ: **Windows Steam v1.10**

---

## 1. ภาพรวมและขอบเขต

เป้าหมายของโปรเจกต์คือทำให้ **Atelier Ryza: Ever Darkness & the Secret Hideout** แสดงภาษาไทยโดยไม่แก้ไข `Atelier_Ryza.exe` บนดิสก์ งานนี้มีทั้งการแปลข้อความ การสร้าง glyph ไทย การเข้ารหัสข้อความให้ renderer ของเกมอ่านได้ และการจัดตำแหน่งสระวรรณยุกต์ในหน่วยความจำ

ฐานข้อมูลแปลหลักมี 28,944 แถว แบ่งเป็น XML 16,058 แถว และ EBM 12,886 แถว รุ่น public v1.0 มีคำแปล 25,372 ข้อความ:

| หมวด | จำนวนแปล | การใช้งาน |
|---|---:|---|
| EBM | 12,059 | บทสนทนา อีเวนต์ และคำบรรยายปกติ |
| XML | 13,313 | เมนู ข้อความระบบ คำอธิบาย และ UI |
| รวม | **25,372** | ข้อความไทยในชุดม็อด |

อีก 3,572 แถวคงต้นฉบับหรือว่างไว้โดยตั้งใจ เช่น ค่าทางเทคนิค ชื่ออ้างอิง ข้อความที่ไม่ควรแปล หรือรายการที่ยังไม่มีคำแปลผ่านการตรวจทาน

---

## 2. สถาปัตยกรรมของม็อด

เกมใช้ archive แบบ Gust PAK และข้อมูล English slot เป็นฐาน ม็อดไม่เพิ่ม locale ใหม่ แต่แทนข้อความ English slot ด้วย carrier character ที่ชี้ไปยัง glyph ไทยใน atlas ที่สร้างขึ้นเฉพาะงานนี้

```text
Translation Master CSV
  ├─ XML rows → PACK00_04_01.PAK / PACK02.PAK
  └─ EBM rows → PACK01.PAK
                    ↑
Thai token map (1,050 tokens) → carrier characters in game text
Thai font atlas + JFont records → dinput8.dll patches metrics in memory
```

ผู้เล่นต้องติดตั้งไฟล์ทั้ง 5 รายการพร้อมกัน:

| ปลายทางในเกม | หน้าที่ |
|---|---|
| `Data\PACK00_04_01.PAK` | ทรัพยากรฟอนต์และ paired atlas |
| `Data\PACK01.PAK` | บทสนทนาและอีเวนต์ภาษาไทย |
| `Data\PACK02.PAK` | เมนูและข้อความระบบภาษาไทย |
| `AtelierRyzaThai\jfont_patch.bin` | ข้อมูลจัดวาง glyph ไทย |
| `dinput8.dll` | proxy DLL ที่ patch JFont ใน memory |

ห้ามนำ PACK, atlas, `jfont_patch.bin` หรือ `dinput8.dll` จากคนละรุ่นมาปนกัน เพราะ carrier map และภาพ glyph ต้องสัมพันธ์กันทั้งชุด

---

## 3. Workspace และ source of truth

```text
E:\Mod_Workspace\Atelier_Ryza\
├── 01_Original_Backup\        ไฟล์เดิมและ checkpoint ก่อน deploy
├── 02_Translation_Workspace\  ไฟล์คำแปล CSV
├── 03_Font_and_UI\            ฟอนต์ atlas mapping และข้อมูลสระ
├── 04_Packed_Mod\             ผล build และ manifest
├── 05_Scripts_and_Tools\      script และ tool เฉพาะเกม
├── 06_Releases\               ชุดแจก .zip ที่ผ่านตรวจแล้ว
└── 07_Image_Resources\        ภาพและ resource ประกอบ
```

ไฟล์คำแปล canonical มีเพียงไฟล์เดียว:

`E:\Mod_Workspace\Atelier_Ryza\02_Translation_Workspace\AtelierRyza_Thai_Translation_MASTER.csv`

SHA256 ของ master ที่ใช้สร้าง build v22:

```text
2605A28BE7F189CDDFD033271089EC81CDB1E00131C47B5D39284533C6A7A318
```

CSV ต้องมี header และลำดับคอลัมน์นี้เท่านั้น:

```text
key,source,translation,context,file_path
```

โดยปกติแก้เฉพาะ `translation` ห้ามเปลี่ยน `key`, `source` หรือ `file_path` เพราะ key ผูกกับ record จริงใน archive

---

## 4. รูปแบบข้อความและ token ที่ห้ามเสีย

### XML

XML คือข้อความเมนูและระบบ เกมอาจใช้ tag, placeholder, line break หรือ control code จึงต้องรักษาไว้

### EBM

EBM คือ event message key มีรูปแบบ `EBM::event/event_en/mm03/event_message_mm03_010.ebm::24::24` ซึ่งหมายถึงพาธ EBM, ลำดับข้อความในไฟล์ และ `msg_id` ตัว packer จะตรวจ key และ source string กับ record ต้นทางก่อน build จึงไม่ควรสร้าง key ใหม่ ย้าย row หรือเรียง CSV ใหม่โดยไม่มีเหตุผล

### Protected tokens

ข้อความอาจมี `%s`, `%d`, `^12`, `{0}`, tags หรือ newline ผู้แปลต้องคงชนิดและจำนวนให้เท่ากับ source:

```text
Source: Obtain %d items.
Thai:   ได้รับไอเทม %d ชิ้น
```

ห้ามลบ `%d` แม้จะทำให้ภาษาไทยอ่านลื่นกว่า เพราะเกมจะเติมค่าตัวเลขขณะ runtime

---

## 5. ฟอนต์ไทยและ paired atlas carrier encoding

ฟอนต์และ renderer เดิมไม่มี glyph ไทยครบ และ JFont metrics ไม่รองรับการจัดลำดับ Unicode ไทยโดยตรง การใส่ UTF-8 ไทยดิบจะทำให้เกิดกล่องสี่เหลี่ยม ตัวสีขาว หรือสระวรรณยุกต์ผิดตำแหน่ง

วิธีแก้คือ **paired atlas carrier encoding**:

1. วิเคราะห์และแบ่งข้อความไทยเป็น unit ที่ประกอบกลับได้
2. สร้าง token map 1,050 token จาก unit ที่ใช้จริง
3. จับ token กับ carrier character ที่ renderer สนับสนุน เช่น Kana/CJK/full-width
4. วาด glyph ไทยลงตำแหน่ง carrier ใน main font atlas สองชุด
5. แปลงคำแปลไทยใน XML/EBM เป็น carrier characters ก่อนแพ็ก
6. ให้ `dinput8.dll` patch JFont metrics ตอนเกมกำลังรัน

เกมจึงอ่าน carrier ที่ตัวเองรับได้ แต่ผู้เล่นเห็นเป็นไทยจากภาพ glyph ใน atlas

### การแก้สระและวรรณยุกต์

รุ่นสุดท้ายยก `่`, `้`, `๊`, `๋` รวม +140 หน่วยจากฐาน และยก `ุ`, `ู`, `ฺ` 60 หน่วย เพื่อแก้การชนของ cluster ไทย JFont ถูก patch 2,099 records ใน memory เท่านั้น และ `Atelier_Ryza.exe` ไม่ถูกเขียนทับ

---

## 6. เครื่องมือและข้อควรระวัง

| เครื่องมือ/สคริปต์ | บทบาท |
|---|---|
| `gust_ebm.exe` | Decode/build EBM จาก JSON |
| `gust_pak.exe` | แตก PAK เพื่อวิเคราะห์และตรวจผล |
| `AtelierRyza_event_ebm_packer.py` | encode carrier, build EBM และ round-trip verify |
| `AtelierRyza_pack01_preserve_keys.py` | สร้าง PACK01 โดยคง key 20 byte, filename, flags, order และ header |
| `AtelierRyza_native_alltext_atlas_rebuilder.py` | สร้าง atlas/PACK00/PACK02/JFont patch จาก translation master |
| `Mapping.json` | กติกาแบ่ง unit ภาษาไทยเพื่อ tokenization |

`gust_pak.exe` ใช้สร้างและแตก archive ได้ แต่การสร้าง PACK01 ของเกมนี้ด้วย tool โดยตรงทำให้ key table 20 byte ต่อไฟล์ไม่ถูกเก็บครบ เกมจึงอาจโหลดผิดหรือแครช

Flow ที่ถูกต้อง:

```text
gust_ebm / gust_pak → สร้าง payload และตรวจ EBM
AtelierRyza_pack01_preserve_keys.py → สร้าง PACK01 สุดท้าย
gust_pak → แตก PACK01 สุดท้ายเพื่อ independent verification
```

ห้าม deploy หรือแจก PACK01 ที่สร้างจาก `gust_pak.exe` โดยตรง

---

## 7. ขั้นตอนแก้คำแปลอย่างปลอดภัย

1. สำรอง master CSV ก่อนแก้
2. เปิด `AtelierRyza_Thai_Translation_MASTER.csv` ด้วย editor ที่รักษา UTF-8, quote และ newline ของ CSV
3. แก้เฉพาะคอลัมน์ `translation`
4. รักษา placeholder, tag และ line break จาก source
5. บันทึก UTF-8 with BOM โดยไม่เปลี่ยน header/จำนวนคอลัมน์
6. ตรวจ key ซ้ำ, U+FFFD (`�`), NUL และ protected-token mismatch
7. build ใหม่และ round-trip verify ก่อน deploy

ถ้าคำไทยใหม่ใช้รูปคำที่ token map ไม่ครอบคลุม packer จะหยุดพร้อมรายงานตำแหน่ง ต้อง rebuild token map, font atlas, PACK00, PACK02 และ `jfont_patch.bin` ทั้งชุด ห้ามยัด carrier เองแบบสุ่ม

---

## 8. Build PACK01 จาก master

สร้าง staging EBM และตรวจ round-trip:

```powershell
python E:\Mod_Workspace\Atelier_Ryza\05_Scripts_and_Tools\AtelierRyza_event_ebm_packer.py `
  --csv E:\Mod_Workspace\Atelier_Ryza\02_Translation_Workspace\AtelierRyza_Thai_Translation_MASTER.csv `
  --source-root E:\Mod_Workspace\Atelier_Ryza\05_Scripts_and_Tools\event_pack01_analysis `
  --atlas-manifest E:\Mod_Workspace\Atelier_Ryza\04_Packed_Mod\AtelierRyza_Full_Thai_v18_tones_plus140\build_manifest.json `
  --mapping E:\Mod_Workspace\Tool\1_ThaiFont\Mapping.json `
  --gust-ebm E:\Mod_Workspace\Tool\gust_tools_v1.58\gust_ebm.exe `
  --gust-pak E:\Mod_Workspace\Tool\gust_tools_v1.58\gust_pak.exe `
  --output <temporary-output> `
  --staging <new-staging-directory>
```

ค่าที่ต้องผ่านใน build v22:

| รายการตรวจ | ค่า |
|---|---:|
| EBM rows | 12,886 |
| translated EBM rows | 12,059 |
| changed EBM files | 838 |
| round-trip verified EBM files | 1,645 |

สร้าง PACK01 จริงด้วย:

```powershell
python E:\Mod_Workspace\Atelier_Ryza\05_Scripts_and_Tools\AtelierRyza_pack01_preserve_keys.py `
  --manifest E:\Mod_Workspace\Atelier_Ryza\05_Scripts_and_Tools\event_pack01_analysis\PACK01.json `
  --payload-root <new-staging-directory>\pack `
  --template-archive E:\Mod_Workspace\Atelier_Ryza\05_Scripts_and_Tools\event_pack01_analysis\PACK01.PAK `
  --output <release>\Data\PACK01.PAK `
  --report <release>\pack01_build_report.json
```

PACK01 build v22 ผ่าน 8,842 keys/names/payloads และมี SHA256 `170AD3E9D0D9B3AA159B3E2CBF94C792EB8FBA2E9C5C541340F98754CE2D7CC9`

---

## 9. Verification ก่อน deploy

ต้องตรวจทั้ง logical และ binary:

1. CSV schema ถูกต้อง, key ไม่ซ้ำ, U+FFFD/NUL เป็นศูนย์ และ protected tokens ตรง
2. EBM round-trip: encode → build → decode แล้ว carrier text ต้องตรง expected
3. ตรวจ header/file count/encrypted filename/key 20 byte/flags/payload ของ PACK01
4. แตก PACK01 สุดท้ายด้วย `gust_pak.exe` แล้วเทียบ SHA256 ของทุกไฟล์กับ staging payload
5. copy ไป game directory แล้วตรวจ hash ปลายทางซ้ำ
6. เปิดเกมและอ่าน `AtelierRyzaThai\runtime_status.txt`

ผล independent extraction ของ v22 คือ extracted 8,842 files, missing 0 และ changed payloads 0

---

## 10. Deploy, rollback และ release

ก่อน deploy ให้ปิด `Atelier_Ryza.exe` และสำรอง `PACK00_04_01.PAK`, `PACK01.PAK`, `PACK02.PAK`, `AtelierRyzaThai\jfont_patch.bin` และ `dinput8.dll` จากนั้น copy ชุดม็อดพร้อมกัน ห้าม deploy เฉพาะ PACK01 เว้นแต่ atlas/token map/JFont เป็นชุดเดียวกันแน่นอน

checkpoint ล่าสุดก่อน v22 คือ `E:\Mod_Workspace\Atelier_Ryza\01_Original_Backup\20260913_before_v22_repaired_master_deploy\`

ผู้เล่นควรถอนม็อดด้วย Steam > Properties > Installed Files > **Verify integrity of game files** แล้วลบ `AtelierRyzaThai` และ `dinput8.dll` ที่ยังเหลือ

release public v1.0 อยู่ที่ `E:\Mod_Workspace\Atelier_Ryza\06_Releases\Atelier_Ryza_Thai_Mod_v1.0\` ภายใน Zip ต้องมี `Data`, `AtelierRyzaThai`, `dinput8.dll` และคู่มืออยู่ที่ root เดียวกัน เพื่อให้ copy ทับโฟลเดอร์เกมได้ทันที

---

## 11. ข้อจำกัดและบทเรียน

### คำบรรยายฉากเปิด

EBM opening ใน PACK01 มี payload ไทยและผ่าน verification แต่ renderer ของคำบรรยายฉากเปิดบางช่วงยังแสดง source อังกฤษ นี่เป็น runtime/loading path แยกต่างหาก ไม่ใช่คำแปลตกหล่น

ห้ามแก้ด้วย loose `Data\PACK01\...`: เคยทำให้ APPCRASH `0xc0000005` จึงไม่ปลอดภัยสำหรับ release

### PACK03 และ DLL diagnostic

Release v1.0 ไม่เขียนทับ `PACK03.PAK` เพราะเคยทดลอง override แล้วคืนไฟล์ต้นฉบับเพื่อแยกปัญหา ชุดแจกใช้ dinput8 รุ่นเสถียร ไม่ใช้ DLL diagnostic ที่สแกน memory

SHA256 ของ dinput8 รุ่นเสถียร: `0A14C180B7154C13981EB278D9D0AD1432C33E0229D97D66B1694B0DF519C0C5`

---

## 12. Troubleshooting และ checklist รุ่นถัดไป

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| เกมแครชทันที | PAK คนละรุ่นปนกัน, key PACK01 เสีย, loose directory ค้าง | Verify game หรือคืน checkpoint; ใช้ preserve-key packer |
| ไทยเป็นสีขาว/กล่อง | atlas/carrier/JFont คนละชุด | ติดตั้ง PACK00/PACK02/jfont/dinput8 พร้อมกัน |
| สระลอยผิด | font metric รุ่นไม่ตรง | ตรวจ JFont patch และ rebuild font packs หาก token map เปลี่ยน |
| token map ไม่ครอบคลุม | คำใหม่ไม่มี token | rebuild paired atlas ทั้งชุด |
| runtime status error | วาง `jfont_patch.bin` ผิดที่ | ให้วางใน `AtelierRyzaThai` ข้าง executable |

Checklist:

- [ ] สำรอง CSV และ release ก่อนหน้า
- [ ] แก้เฉพาะ `translation`
- [ ] ตรวจ schema, duplicate key, U+FFFD, NUL และ protected tokens
- [ ] build/round-trip EBM ทุกไฟล์
- [ ] สร้าง PACK01 ผ่าน preserve-key packer
- [ ] แตก archive สุดท้ายและเทียบ payload ทุกไฟล์
- [ ] หาก token map เปลี่ยน ให้ rebuild PACK00/PACK02/atlas/JFont patch ทั้งชุด
- [ ] ทดสอบโดยไม่ใช้ loose PACK01 directory
- [ ] สร้าง checksum จาก release จริง

---

## 13. Baseline hashes ของ public v1.0

| ไฟล์ | SHA256 |
|---|---|
| `Data\PACK00_04_01.PAK` | `4E62253F90B7B40E8D58071F039BF56D7C859A854FDCCD5D21C7AD00EFCED3AE` |
| `Data\PACK01.PAK` | `170AD3E9D0D9B3AA159B3E2CBF94C792EB8FBA2E9C5C541340F98754CE2D7CC9` |
| `Data\PACK02.PAK` | `B608CFC921058E2A8ECD332053AA32495CE9377DD442CB7151872151DD0AC9EC` |
| `AtelierRyzaThai\jfont_patch.bin` | `1D6010C6130DEB34ED49847B31F134608AB9249B19EA4D200A0171025E1B59FF` |
| `dinput8.dll` | `0A14C180B7154C13981EB278D9D0AD1432C33E0229D97D66B1694B0DF519C0C5` |

หาก hash ไฟล์ในเครื่องผู้เล่นต่างจากตารางนี้ ให้ถือว่าไม่ใช่ชุด release v1.0 เดียวกันจนกว่าจะตรวจสอบได้
