# คัมภีร์สร้าง Mod ภาษาไทย — Deus Ex: Human Revolution Director's Cut

เอกสารนี้บันทึกวิธีที่ใช้จริงจนเกมแสดงภาษาไทยได้สำเร็จ เหมาะสำหรับการทำซ้ำ การแก้บั๊ก และการต่อยอด Mod รุ่นถัดไป โดยยึดหลักว่าเครื่องมือของโปรเจกต์ทำหน้าที่เป็น Bridge ระหว่างไฟล์เกมกับ TStudio CSV เท่านั้น ส่วนการแปลจำนวนมากให้ใช้ TRun

## 1. ข้อมูลโครงการ

- เกม: Deus Ex: Human Revolution — Director's Cut
- เวอร์ชันเกมที่ทดสอบ: Build 2.0.0.0 (Steam/Windows)
- Engine: Crystal Engine แบบปรับแต่งของ Crystal Dynamics
- Archive หลัก: `BIGFILE.000` ถึง `BIGFILE.008`
- Archive Mod: ไฟล์ `.000` ภายในโฟลเดอร์ `mods`
- Workspace: `E:\Mod_Workspace\Deus_Ex_Human_Revolution`
- Game Directory ที่ใช้พัฒนา: `F:\SteamLibrary\steamapps\common\Deus Ex Human Revolution Director's Cut`
- ผู้สร้าง Mod: หน๊ด หนวด translator
- แนวทาง: Approach B — Standalone CLI Bridge เนื่องจากข้อมูลอยู่ใน archive proprietary และมีชั้น DRM/CDRM

## 2. กฎที่ต้องรักษา

1. ห้ามแก้ `trun_app.py`, `tstudio_app.py`, `tstudio_core.py` และ `file_converter.py`
2. ห้ามสร้างวงจรแปลด้วย LLM เอง งานแปลชุดใหญ่ต้องส่งผ่าน TRun
3. CSV ต้องมีคอลัมน์ `key | source | translation | context | file_path`
4. ห้ามแก้ `source`; `key` ต้องไม่ซ้ำ
5. ต้องรักษา token และแท็ก เช่น `%s`, `{0}`, `<color=red>`, `\\n`, `\\r` รวมถึง line break จริง
6. `01_Original_Backup` เป็น read-only ในเชิงกระบวนการ: ห้ามเขียนทับ backup เดิม
7. ก่อนแก้ไฟล์ Game Directory ต้องสร้าง backup และบันทึก checkpoint ใน `session_log.md`
8. ก่อนโทษฟอนต์ ให้พิสูจน์ก่อนว่าไฟล์ที่ pack มีอักษรไทยจริง ไม่ใช่เครื่องหมาย `?`

## 3. เครื่องมือที่ใช้

ชุด Gibbed Deus Ex 3:

- `Gibbed.DeusEx3.Unpack.exe` — แตก BIGFILE/mod archive
- `Gibbed.DeusEx3.Pack.exe` — สร้าง archive `.000`
- `Gibbed.DeusEx3.DRMUnpack.exe` — แตก resource จาก DRM
- `Gibbed.DeusEx3.DRMDecompress.exe` — คลาย CDRM เป็น raw DRM

ตัวโหลด Mod:

- DXHRDC Mod Hook v1.1.0.0 โดย Rick (gibbed)
- ใช้ `DFEngine.dll` ของ Mod Hook เพื่อให้เกมอ่าน archive เพิ่มเติมจากโฟลเดอร์ `mods`
- ห้ามแจก DLL ต้นฉบับของเกม; แจกเฉพาะ DLL ของ Mod Hook พร้อมเครดิตและ notice

Bridge ของโครงการ:

- `05_Scripts_and_Tools\DeusExHR_unpacker.py`
- `05_Scripts_and_Tools\DeusExHR_packer.py`
- `05_Scripts_and_Tools\DeusExHR_validator.py`
- `05_Scripts_and_Tools\DeusExHR_prepare_deploy_csv.py`
- `05_Scripts_and_Tools\DXHR_font_bridge.py`

## 4. โครงสร้างข้อความของเกม

ข้อความภาษาอังกฤษอยู่ที่ resource:

`pc-w\local\locals.bin`

ข้อมูลสำคัญ:

- Locale ภาษาอังกฤษ: `FFFFFD61`
- Archive resource hash: `7CD333D3`
- Encoding ของข้อความ: UTF-8 ไม่มี BOM และจบแต่ละข้อความด้วย null byte
- จำนวนรายการ: 19,490

โครงสร้าง `locals.bin`:

1. Header little-endian `<II>` จำนวน 8 bytes
   - `language_index`
   - `count`
2. ตาราง offset จำนวน `count` ค่า แต่ละค่าเป็น little-endian `uint32`
3. string pool แบบ UTF-8 null-terminated

สำหรับภาษาอังกฤษ `language_index = 0` กุญแจ CSV สร้างแบบคงที่ เช่น `DXHR_LOCALS_EN_00000` เพื่อให้ pack กลับตำแหน่งเดิมได้แน่นอน

## 5. การ Extract ไป TStudio CSV

ขั้นตอนมาตรฐาน:

1. ใช้ Gibbed แตก BIGFILE ที่มี `locals.bin`
2. ใช้ `DeusExHR_unpacker.py` อ่าน header, offset table และ UTF-8 strings
3. ส่งออก CSV ด้วยคอลัมน์มาตรฐาน:
   - `key`: ลำดับคงที่ของข้อความ
   - `source`: ข้อความอังกฤษเดิม
   - `translation`: เว้นว่างก่อนส่ง TRun
   - `context`: locale/index/ข้อมูลช่วยแปล
   - `file_path`: ที่อยู่ resource ต้นทาง
4. ตรวจว่าได้ครบ 19,490 แถว, key ไม่ซ้ำ และ source ไม่ถูกเปลี่ยน

ไฟล์ extraction ต้นฉบับที่ใช้ในโครงการมี SHA-256:

`4E734B097A1B3BF7CEC9F33DDBE6CBB736543BD423D3437FCDA1BC514E8FEE80`

## 6. การแปลและเตรียม Deploy

นำ CSV เข้า TRun เพื่อแปลชุดใหญ่ แล้วตรวจด้วย validator ก่อน pack เสมอ ตัวตรวจต้องครอบคลุม:

- จำนวนแถวและ key
- `source`, `context`, `file_path` ไม่ถูกแก้
- translation ว่าง
- Unicode replacement character `U+FFFD`
- ชุด `????` ที่บ่งชี้ว่า Unicode สูญหาย
- `%s`, `{0}`, tag XML/HTML-like
- escaped `\\n`, `\\r`
- จำนวน actual line break

ในรุ่น v1.0 ใช้ `DeusExHR_prepare_deploy_csv.py` สร้างไฟล์ deploy-safe โดย:

- คืน metadata จาก extraction ต้นฉบับ
- ตัด line break ส่วนเกินที่ TRun เติม
- fallback เป็น source เมื่อ translation ไม่ปลอดภัย
- ไม่พยายามเดาค่าแท็กที่หาย

สถิติไฟล์ที่ deploy:

- รายการทั้งหมด: 19,490
- ช่องข้อความต้นฉบับไม่ว่าง: 19,483
- ช่อง translation ที่มีค่า: 19,483
- รายการที่ตรวจพบอักษรไทย: 18,715
- รายการที่คงข้อความเดิม: 767 (ชื่อเฉพาะ โค้ด ตัวเลข ข้อความที่ควรคงอังกฤษ และ safety fallback)
- safety fallback ที่ source ไม่ว่าง: 39
- ช่องระบบว่าง: 7

SHA-256 ของ deploy-safe CSV:

`164CC808E617AE9C7F84546CF5E77F6564F9C8DA423FD24204B251F12BCC4F8D`

## 7. การ Pack และตรวจแบบ Round-trip

`DeusExHR_packer.py` ต้องสร้าง `locals.bin` ใหม่โดยคง `language_index`, จำนวนรายการ และลำดับ offset ให้ถูกต้อง จากนั้นสร้าง archive ด้วย Gibbed Pack

ห้ามถือว่า pack สำเร็จเพียงเพราะโปรแกรมจบโดยไม่ error ให้ตรวจดังนี้:

1. แตก archive ที่เพิ่งสร้างกลับออกมา
2. ตรวจว่าได้ resource hash `7CD333D3`
3. extract `locals.bin` รอบสอง
4. ยืนยันจำนวน 19,490 รายการ
5. เปรียบเทียบทุกข้อความกับ CSV ที่ใช้ pack
6. ตรวจ hex/UTF-8 ของคำไทยตัวอย่าง เช่น `เล่นต่อ`, `เริ่มเกมใหม่`, `ตั้งค่า`

ไฟล์แปลเต็มที่ผ่าน round-trip:

- `DXHR_Thai_Full.000`
- SHA-256: `C6F5317E06CC8703185E085094C11F6C63C54927D51ABE824DEA5364C5334AB7`

## 8. บทเรียนสำคัญ: เครื่องหมายคำถามไม่ใช่ปัญหาฟอนต์เสมอไป

POC ระยะแรกแสดง `???????` จึงดูคล้ายฟอนต์ไม่มี glyph ภาษาไทย แต่เมื่อแตก archive ที่ deploy แล้วตรวจ payload พบว่า string ถูกบันทึกเป็นเครื่องหมาย `?` จริง ไม่ได้มี byte UTF-8 ภาษาไทยอยู่ในไฟล์

ลำดับวินิจฉัยที่ถูกต้อง:

1. D1 — แตกไฟล์ที่ pack แล้วและตรวจ string/hex ก่อน
2. หาก byte เป็น `?` ให้แก้แหล่ง CSV, encoding หรือ packer
3. หาก byte เป็น UTF-8 ภาษาไทยแต่หน้าจอเป็นสี่เหลี่ยม จึงไปตรวจ font glyph
4. หาก byte ถูกและ glyph มี แต่สระ/วรรณยุกต์ผิด ให้ตรวจ shaping/metric ของฟอนต์

การแก้ CSV ให้มี Unicode ไทยจริงแล้ว pack ใหม่ ทำให้เมนูแสดง `เล่นต่อ`, `เริ่มเกมใหม่`, `โหลดเกม`, `ตั้งค่า`, `รายชื่อผู้สร้าง` และ `เนื้อหาเพิ่มเติม` ได้สำเร็จ

## 9. ระบบฟอนต์ Scaleform CFX/SWF

UI ใช้ Scaleform และเก็บ movie เป็น CFX โครงสร้างที่พบ:

`CFX + version byte + uint32 ขนาด SWF ที่คลายแล้ว + zlib(SWF body)`

เมื่อต้องการเปิดในเครื่องมือ SWF ให้สร้าง FWS ชั่วคราว:

`FWS + version + uint32 file_size + SWF body`

Font tag ที่เกี่ยวข้องเป็น `DefineFont3`:

- Font ID 1: `DeusEx3_Hud`
- Font ID 3: `DeusEx3_Computer`

UI movies อ้าง `$HUDFont` จาก `gfxfontlib.swf` ผ่าน path เช่น `../../gfxfontlib.swf` หรือ `../../../gfxfontlib.swf` ดังนั้นการใส่ TTF ลง SWF แบบสุ่มไม่พอ ต้องเปลี่ยน font bank ที่ movie ใช้งานจริง

ตำแหน่งสำคัญ:

- `globalscaleformdatabase.drm` มี CFX 47 movies; Main Menu คือ index 44 จากการค้นสตริง `TUTORIALS` และ Main Menu
- `generalbank.drm` มี font-library copy
- `globaldatabase.drm` มี font-library copy

ฟอนต์ไทยที่ใช้:

`E:\Mod_Workspace\Tool\1_ThaiFont\fonts_main\1_IBMPlexSans_fixByNodNuatTranslator_2.ttf`

SHA-256:

`BDF635DC2DCE86DA887B909DEABC3ABD495F229A8AABD3390D72883501CD2A16`

ไฟล์ font mod ที่ผ่านการทดสอบ:

- `DXHR_Thai_Font_POC.000` — generalbank compact HUD
  - SHA-256: `0CC8FCAF03FF0C91875C004384D23E112A15A6DAAD27F3AD55A57CC275BFC189`
- `DXHR_Global_Hud_IBM_Plex_Thai_POC.000` — globaldatabase compact HUD
  - SHA-256: `B528BC47DAD8977CE9443AF172CCC556AEBD7C97102CBD770FDA310EB758ECF0`

ชื่อไฟล์ยังมีคำว่า POC เพื่อรักษาชุดไฟล์ที่ทดสอบผ่านและลำดับการโหลดเดิม ไม่ควรเปลี่ยนชื่อโดยไม่มีการทดสอบใหม่

## 10. CDRM และวิธีฉีดฟอนต์อย่างปลอดภัย

CDRM ที่พบมี:

- magic `CDRM`
- version 2
- block count และ block table
- flags: ขนาด uncompressed 24-bit อยู่ในส่วนบน และชนิด block อยู่ low byte
  - type 1 = raw
  - type 2 = zlib
- payload แต่ละ block align 16 bytes; final block ของต้นฉบับอาจไม่มี padding เต็ม

ความล้มเหลวที่สำคัญ: การฝัง IBM Plex แบบ aggressive แล้ว resize section พร้อม pack CDRM ใหม่แบบ generic ทำให้เกมค้างและเปิดไม่ติด แม้ไฟล์จะ parse ได้

แนวทางที่สำเร็จคือ fixed-slot injection:

1. CFX ใหม่ต้องไม่ใหญ่กว่า slot เดิม
2. เติมพื้นที่ให้ resource มีขนาดเดิม
3. รักษาขนาด raw DRM เดิม
4. ใช้ `cdrm-repack-like` โดยยึด block boundaries, block types และ padding จาก CDRM ต้นฉบับทุกจุด
5. เปลี่ยนเฉพาะ resource เป้าหมาย

Generalbank:

- CFX ใหม่ 320,541 bytes ใน slot เดิม 553,831 bytes
- raw DRM คงขนาด 2,765,904 bytes
- รักษา CDRM 505 blocks
- เปลี่ยนเฉพาะ `DTPData\86768.bin` และคงขนาด 553,844 bytes
- archive entry hash `B3AAAFD6`

Globaldatabase:

- CFX ใหม่ 320,541 bytes ใน slotเดิม 553,831 bytes
- raw DRM คงขนาด 2,588,524 bytes
- รักษา CDRM 908 blocks
- เปลี่ยนเฉพาะ `DTPData\86768.bin` และคงขนาดเดิม
- archive entry hash `47B84A2B`

คำสั่งหลักของ `DXHR_font_bridge.py` ได้แก่ `scan`, `extract`, `inject`, `cdrm-pack`, `cdrm-unpack`, `cdrm-repack-like` และ `swf-transplant-font` โดยโหมดปกติควรปฏิเสธไฟล์ที่ใหญ่กว่า section; `--allow-resize-section` ถือเป็นโหมดทดลองที่เสี่ยงและต้องไม่ใช้กับ release โดยไม่มีการทดสอบเต็ม

## 11. วิธี Deploy ที่พิสูจน์แล้ว

1. สำรอง `DFEngine.dll` เดิมของผู้เล่น
2. วาง DXHRDC Mod Hook `DFEngine.dll` ที่โฟลเดอร์รากของเกม
3. สร้าง/รวมโฟลเดอร์ `mods`
4. วาง archive ทั้งสามไฟล์:
   - `DXHR_Thai_Full.000`
   - `DXHR_Thai_Font_POC.000`
   - `DXHR_Global_Hud_IBM_Plex_Thai_POC.000`
5. เปิดเกมและตรวจ Main Menu

เกณฑ์ผ่าน POC:

- ไม่มี `????` หรือ tofu แทนคำไทย
- สระและวรรณยุกต์อยู่ในตำแหน่งอ่านได้ถูกต้อง
- เกมโหลด Main Menu ได้ ไม่ค้างและไม่ crash
- คำเมนูหลักแสดงภาษาไทยจริง

## 12. Diagnostic Tree

หากข้อความไม่ถูกต้อง ให้ตรวจตามลำดับ:

1. Archive โหลดหรือไม่
   - ตรวจ Mod Hook และโฟลเดอร์ `mods`
   - ตรวจชื่อและ hash ของ `.000`
2. Payload มีภาษาไทยหรือไม่
   - แตก archive และ extract `locals.bin`
   - ตรวจ UTF-8/hex และเทียบ CSV
3. เป็น `?` หรืออักษรเพี้ยน
   - แก้ source CSV/encoding/packer
4. เป็นกล่องสี่เหลี่ยม
   - ตรวจ `$HUDFont`, DefineFont3 และ font bank ที่ movie import จริง
5. เกมค้างหลังเปลี่ยนฟอนต์
   - rollback archive ล่าสุด
   - ตรวจ section size และ CDRM block template
   - ใช้ fixed-slot + `cdrm-repack-like`
6. ภาษาไทยถูกแต่ UI ล้น
   - ปรับคำแปลให้กระชับก่อนแก้ layout
   - ทดสอบ resolution และ menu/subtitle หลายแบบ

## 13. Release Checklist

- ตรวจ hash ของ archive ทั้งสามและ Mod Hook
- ทดสอบ ZIP โดยแตกไปโฟลเดอร์ชั่วคราว
- ตรวจว่า ZIP ไม่มีไฟล์จาก `01_Original_Backup` หรือ DLL ต้นฉบับของเกม
- มี README ติดตั้งและถอนการติดตั้ง
- มี third-party notice ของ Mod Hook
- ระบุจำนวนข้อความตามจริง ไม่อ้างว่าแปลไทยทุกแถว
- เล่นทดสอบ Main Menu, HUD, subtitle, inventory, dialogue และ save/load
- เก็บ 39 safety fallback ไว้เป็นรายการตรวจแก้สำหรับ v1.1

## 14. Hash อ้างอิง Release v1.0

- Mod Hook `DFEngine.dll`: `A71C2FC6F15B7C9F4FB4128D6946454589A776F3F6618377709886BF8E2EA378`
- Full translation: `C6F5317E06CC8703185E085094C11F6C63C54927D51ABE824DEA5364C5334AB7`
- General HUD font: `0CC8FCAF03FF0C91875C004384D23E112A15A6DAAD27F3AD55A57CC275BFC189`
- Global HUD font: `B528BC47DAD8977CE9443AF172CCC556AEBD7C97102CBD770FDA310EB758ECF0`

เอกสารนี้ควรอัปเดตเมื่อมีการเปลี่ยน CSV, ฟอนต์, CDRM packing หรือ Mod Hook เพื่อให้ release รุ่นถัดไปสามารถทำซ้ำและตรวจสอบย้อนหลังได้
