# Vampyr Thai Localization Bible

## ขอบเขตที่ยืนยันแล้ว

- เกม: **Vampyr** (Windows / Steam)
- เอนจิน: Unreal Engine 4
- Archive หลัก: `AVGame/Content/Paks/AVGame-WindowsNoEditor-Localization.pak`
- รูปแบบ PAK: UE4 PAK V3, mount point `../../../`, Zlib, index ไม่เข้ารหัส
- รูปแบบข้อความ: Unreal `.locres`
- Language slot ที่ใช้: `en-US`
- จำนวนข้อความที่สกัดได้: 20,071 ข้อความ จาก `.locres` 10 ไฟล์

## โครงสร้างข้อความ

```text
AVGame/Content/Localization/
├── Game_GT_Citizens/en-US/Game_GT_Citizens.locres
├── Game_GT_Dialog/en-US/Game_GT_Dialog.locres
├── Game_GT_LD/en-US/Game_GT_LD.locres
├── Game_GT_Misc/en-US/Game_GT_Misc.locres
├── Game_GT_Online/en-US/Game_GT_Online.locres
├── Game_GT_UI/en-US/Game_GT_UI.locres
├── Game_VO_Citizens/en-US/Game_VO_Citizens.locres
├── Game_VO_Enemies/en-US/Game_VO_Enemies.locres
├── Game_VO_Misc/en-US/Game_VO_Misc.locres
└── Game_VO_Missions/en-US/Game_VO_Missions.locres
```

`GT` คือข้อความเกม/เมนู/ระบบ และ `VO` คือข้อความเกี่ยวกับเสียง/บทสนทนา. Main Menu อยู่ใน `Game_GT_UI`.

## Toolchain ที่ใช้

- `u4pak.py` (panzi/u4pak): อ่านและแตก PAK V3 ของ Vampyr
- `UnrealLocres.exe`: แปลง `.locres` ↔ CSV
- `repak.exe`: pack override PAK แบบ V3 พร้อม mount point ที่ถูกต้อง
- THub TRun / TStudio: แปล CSV จำนวนมากเท่านั้น

อย่าใช้ UnrealPak ที่ตีความคำสั่งผิดเป็นการสร้าง PAK โดยชี้ไปที่ Game Directory. ให้ทำงานกับสำเนา/Workspace และ pack output ไปยัง Workspace ก่อนเสมอ.

## Bridge Workflow

1. ใช้ `Vampyr_unpacker.py` แตก `.locres` English (`en-US`) เป็น TStudio CSV
2. ไฟล์ CSV ต้องมีคอลัมน์ `key | source | translation | context | file_path`
3. ห้ามแก้ `key` และ `source`; ส่งให้ TRun/TStudio เติมเฉพาะ `translation`
4. ใช้ `validate_vampyr_translations.py --require-all` ก่อน pack ทุกครั้ง
5. ใช้ `Vampyr_packer.py` สร้าง `.locres` ใหม่จาก template เดิมและ manifest
6. ใช้ RePak สร้าง PAK V3 ใน Workspace
7. ก่อน deploy ให้ backup PAK mod เดิม, บันทึก session log, copy PAK เข้า `AVGame/Content/Paks/~mods/`

Packer ต้องจับคู่ด้วย `key` + manifest เท่านั้น เพราะเครื่องมือแปลอาจล้าง `file_path` หรือปรับข้อความในคอลัมน์ `source`. Source structure ที่สร้าง `.locres` ต้องกลับมาจาก template ภาษาอังกฤษเดิมเสมอ.

## Protected Tokens

ต้องรักษา token เหล่านี้ในคำแปลให้ครบและจำนวนเท่าต้นฉบับ:

- printf placeholders เช่น `%s`, `%d`, `%f`
- named/index placeholders เช่น `{0}`
- colour tags เช่น `<color=red>` และ `</color>`
- literal controls `\n`, `\r`

เครื่องหมายเปอร์เซ็นต์ธรรมดา เช่น `50%` หรือ `{0}%` ไม่ใช่ printf placeholder และไม่ควรถูก validator ตีความว่าเป็น token.

## Thai Font Solution

ใช้ Pridi PUA เป็น Slate fallback โดยนำเข้ามาใน PAK ที่ path นี้:

```text
Engine/Content/Slate/Fonts/DroidSansFallback.ttf
```

วิธีนี้ไม่แก้ฟอนต์เกมต้นฉบับ. สำหรับ build ที่ผ่าน POC ให้ยก glyph วรรณยุกต์ `่ ้ ๊ ๋` (U+0E48–U+0E4B) ขึ้น **+200 font units** จาก Pridi ต้นฉบับ (UPM 1000). การปรับต้องขยับ outline และ recalculate glyph bounds ก่อนบันทึก TTF.

## PAK Override และการติดตั้ง

สร้าง PAK ชื่อที่ลงท้าย `_P.pak` แล้ววางที่:

```text
Vampyr/AVGame/Content/Paks/~mods/Vampyr_ThaiMod_NodNuatTranslator_P.pak
```

ใช้ PAK ภาษาไทยเพียงไฟล์เดียวใน `~mods` เพื่อหลีกเลี่ยง override ซ้ำจาก POC/รุ่นเก่า. Player ต้องตั้งภาษาเกมเป็น English เพื่อให้เกมอ่าน `en-US` language slot ที่ mod ทับไว้.

## Diagnostics

- ภาษาไทยเป็นกล่อง: ตรวจว่า PAK มี `Engine/Content/Slate/Fonts/DroidSansFallback.ttf`
- วรรณยุกต์ต่ำ/ชนกัน: ตรวจว่า release ใช้ Pridi tone marks +200 ไม่ใช่ font เดิม
- เมนูยังเป็นอังกฤษ: ตรวจ language เป็น English, path `~mods`, และชื่อ PAK ลงท้าย `_P.pak`
- เกมไม่โหลด/ผิดปกติ: ลบ PAK mod แล้ว Verify integrity ผ่าน Steam
- PAK ถูกล็อกขณะ deploy: ปิดเกม Vampyr ก่อน copy เสมอ

## Release Checklist

- CSV: key ครบ, translation ไม่ว่าง, validator = 0 errors
- PAK: RePak list พบ 10 `.locres` และ 1 fallback TTF
- Font: tone marks +200
- Installer ZIP: โครงสร้างเริ่มด้วย `AVGame/Content/Paks/~mods/`
- คู่มือ: วิธีติดตั้ง/ถอน, language slot English, เครดิต
- Checksum: SHA-256 ของ PAK และ ZIP
