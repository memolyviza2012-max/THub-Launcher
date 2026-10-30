🎮 Master Prompt: Game Localization Project (Thai Mod) - THub Edition

Context & Goal:
ฉันต้องการสร้าง Mod แปลภาษา Thai ระดับมืออาชีพสำหรับเกม: TestGame
โดยจะทำการแปลจากภาษา **English** เป็นภาษา **Thai**
เราจะทำงานร่วมกันทีละขั้นตอนอย่างเป็นระบบ นี่คือข้อมูลภาพรวมของโปรเจค:

Environment & Workspace:
- Workspace:          E:\Mod_Workspace\Modder_project\modder-hub  (ใช้โครงสร้าง 01–06 ของ THub)
- Game Directory:     [ระบุตำแหน่งโฟลเดอร์ติดตั้งเกม]
- Tool Directory:     [ระบุตำแหน่งโฟลเดอร์เครื่องมือ]
- ตรวจพบ Engine:      Unreal Engine (เครื่องมือแนะนำ: TStudio, TRun)
- Modding Knowledge:  E:\Mod_Workspace\Modding-Knowledge
- Modding Knowledge (GitHub, always latest): https://github.com/memolyviza2012-max/Modding-Knowledge

คลังความรู้ที่ตรวจพบ:
  • [📘 คู่มือ Engine] UE4 Older Font Fallback KI (Engines/Unreal_Engine_4/UE4_Older_Font_Fallback_KI.md)
  • [📘 คู่มือ Engine] Unreal Engine (Engines/Unreal_Engine_2/Unreal_Engine.md)
  • [🎮 เกม Engine เดียวกัน] Avowed Thai Localization Bible (Engines/Unreal_Engine_5/Games/Avowed/Avowed_Thai_Localization_Bible.md)
  • [🎮 เกม Engine เดียวกัน] Beast of Reincarnation Thai Localization Bible (Engines/Unreal_Engine_5/Games/Beast_of_Reincarnation/Beast_of_Reincarnation_Thai_Localization_Bible.md)

══════════════════════════════════════════════════════
🏭 ECOSYSTEM: THub Translation Engine (ห้ามแก้ไขโดยเด็ดขาด)
══════════════════════════════════════════════════════
โปรเจกต์นี้มี Translation Engine ที่ Stable และพร้อมใช้งานอยู่แล้วที่:
  E:\Mod_Workspace\Modder_project\modder-hub/tools/flagship/

  • TStudio  (TStudio/tstudio_app.py)    — GUI สำหรับรีวิวและ deploy งานแปล
  • TRun     (TRun/trun_app.py)          — ระบบแปลแบบ Batch อัตโนมัติ
  • Core     (Core/tstudio_core.py,
              TStudio/file_converter.py) — จัดการ API, memory, แปลง format

⛔ กฎเหล็ก — ห้ามละเมิดเด็ดขาด:
  1. ห้ามแก้ไข Core Files: trun_app.py, tstudio_app.py, tstudio_core.py, file_converter.py
  2. ห้ามเขียน LLM translation loop ขึ้นมาเอง — ให้ใช้ TRun สำหรับการแปลชุดใหญ่เสมอ
  3. Script ของคุณทำหน้าที่เป็น Bridge เท่านั้น:
       Unpack  : format เกม  →  TStudio CSV
       Pack    : TStudio CSV  →  format เกม

มาตรฐาน TStudio CSV Format:
  คอลัมน์ : key | source | translation | context | file_path
  ตัวอย่าง : MENU_001 | "New Game" | "" | "Main Menu > ปุ่มหลัก" | ui/menu.json
  กฎ      : key ต้องไม่ซ้ำ · translation ว่างเปล่าตอนส่งให้ TRun · ห้ามแก้ไขคอลัมน์ source

══════════════════════════════════════════════════════
[สำคัญ] กฎความปลอดภัยของ Workspace
══════════════════════════════════════════════════════
  1. ห้ามสร้างไฟล์นอก Workspace นี้เด็ดขาด
  2. "01_Original_Backup" คือ Read-Only — ห้ามเขียนทับ ให้ copy ออกมาก่อนเสมอ
  3. เมื่อเขียนโค้ดต้องแสดงฉบับเต็มที่รันได้จริงเสมอ ห้ามใช้ Placeholder
  4. [กฎ CHECKPOINT] ก่อนทุกครั้งที่จะ Pack ไฟล์กลับเข้า Game Directory:
     ให้ backup ไฟล์เป้าหมายไปที่ 01_Original_Backup/ และบันทึกใน session_log.md ก่อน

══════════════════════════════════════════════════════
Milestones & Workflow (โหมด Autonomous POC Fast-Track ⚡)
══════════════════════════════════════════════════════
⚡ [ระบบปฏิบัติการขั้นตอนที่ 1–3 อัตโนมัติ (Fast-Track)]:
หาก AI ประเมินแล้วว่ามี "ความมั่นใจเพียงพอ (Confidence Assessment: High >= 80%)":
  • ให้ AI ดำเนินการขั้นตอนที่ 1 → 2 → 3 ต่อเนื่องกันรวดเดียวโดยอัตโนมัติ!
  • ไม่ต้องหยุดรอการยืนยันทีละสเต็ประหว่างขั้นตอนที่ 1 และ 2
  • AI มีหน้าที่ทำไฟล์ต้นฉบับสำรอง (01_Original_Backup), เขียน Bridge, สกัดข้อความ Main Menu, จูนฟอนต์ PUA, แพตช์เมนูหลักภาษาไทยเข้าเกม และตรวจสอบ Read-back ให้เสร็จสรรพ
  • จุดหยุดรอเดียว (Gate) คือ: "ขั้นตอนที่ 3 — ส่งมอบให้ผู้ใช้เปิดเกมทดสอบผลลัพธ์หน้า Main Menu"
  • หากความมั่นใจต่ำ (< 80% เช่น ติด Anti-cheat, รูปแบบบีบอัดไม่รู้จัก, ไฟล์เข้ารหัสซับซ้อน) ให้หยุดรายงานและปรึกษาผู้ใช้ที่ขั้นตอนที่ 1 ทันที
══════════════════════════════════════════════════════

────────────────────────────────────────────────────
ขั้นตอนที่ 1 — วิเคราะห์ไฟล์เกมและเลือก Approach
────────────────────────────────────────────────────
  1.1  สแกน [ระบุตำแหน่งโฟลเดอร์ติดตั้งเกม] เพื่อระบุ:
         - Engine ที่ใช้ (Unreal Engine ตรวจพบ)
         - Format ไฟล์ข้อความ (.json, .xml, .locres, .pak, .bin, proprietary...)
         - Encoding ของไฟล์ (UTF-8, UTF-8 BOM, ANSI, UTF-16...)
         - โครงสร้าง Archive ที่ครอบข้อความอยู่ (ถ้ามี)

  1.2  [บังคับ — ค้น Knowledge Base ก่อนเขียนโค้ดใดๆ]
       ทันทีที่ระบุ Engine/Format ได้แล้ว ต้องทำก่อนเสมอ:
         → ค้นหาใน **ทั้ง 2 แหล่ง** ด้วย keyword เหล่านี้:
             Local : E:\Mod_Workspace\Modding-Knowledge
             GitHub (อัปเดตตลอด): https://github.com/memolyviza2012-max/Modding-Knowledge
             • ชื่อ Engine  (เช่น "Unreal Engine")
             • ชื่อ Format  (เช่น "LOCRES", "PAK", "STR", "WIN", "BIN")
             • ชื่อเกม      (เช่น "TestGame")
         → รายงานผลการค้นหาอย่างชัดเจน:
             ✅ พบ:     "พบไฟล์ [ชื่อไฟล์] — [สรุปแนวทางที่เกี่ยวข้อง]"
             ❌ ไม่พบ:  "ไม่พบข้อมูลสำหรับ [Engine/Format] ใน Knowledge Base จะวิเคราะห์เอง"
         → ถ้าพบคัมภีร์: ต้องนำแนวทางในคัมภีร์มาใช้ ห้ามทำขัดกับคัมภีร์
         → ถ้าไม่พบ: ค่อยวิเคราะห์เองและอธิบายเหตุผล

  1.3  ประกาศ Approach ที่เลือก:
       [APPROACH A] Format เรียบง่ายหรือแกะได้ (.json, .xml, .csv, .txt, .locres...)
         → เขียน Custom Parser Plugin:
            ไฟล์: E:\Mod_Workspace\Modder_project\modder-hub/tools/flagship/TStudio/CustomParsers/[GameName]_parser.py
            ต้องมีฟังก์ชัน: convert_to_csv(filepath) → TStudio CSV
            TStudio โหลดอัตโนมัติผ่าน Plugin Manager

       [APPROACH B] Archive หนัก (.pak, .dat, .arc, .bin, bundle ที่เข้ารหัส...)
         → เขียน Standalone CLI Scripts สองไฟล์:
            [GameName]_unpacker.py  — แตกข้อความ → TStudio CSV
            [GameName]_packer.py    — อ่าน CSV ที่แปลแล้ว → repack format เกม
            เก็บทั้งคู่ใน: E:\Mod_Workspace\Modder_project\modder-hub/05_Scripts_and_Tools/

        ระบุว่าเลือก Approach ไหนและเหตุผลก่อนเขียนโค้ด

  1.4  [การประเมินความมั่นใจ & การตัดสินใจรันอัตโนมัติ]
       ประเมินระดับความมั่นใจ (Confidence Score) ก่อนดำเนินการต่อ:
       • มั่นใจสูง (High Confidence >= 80%):
         เกณฑ์: ตรวจพบ Engine ชัดเจน, มีคัมภีร์ใน Knowledge Base, หรือโครงสร้างไฟล์มาตรฐาน (.locres, .json, .csv ฯลฯ), และไม่มี Anti-Cheat ขัดขวาง
         → ปฏิบัติการ: ดำเนินการต่อเข้าสู่ "ขั้นตอนที่ 2" และ "ขั้นตอนที่ 3" ทันทีโดยไม่ต้องรอผู้ใช้สั่ง!
       • มั่นใจต่ำ (Low Confidence < 80%):
         เกณฑ์: รูปแบบไฟล์ไม่คุ้นเคย, เข้ารหัส/บีบอัดไม่ทราบชนิด, เสี่ยงกระทบไฟล์สำคัญหรือเซฟเกม
         → ปฏิบัติการ: หยุดรายงานผลและปรึกษาผู้ใช้ก่อนเขียนโค้ด

────────────────────────────────────────────────────
ขั้นตอนที่ 2 — เขียน Bridge Script (TStudio Integration)
────────────────────────────────────────────────────
  • เขียน script ตาม Approach ที่เลือกในขั้นตอนที่ 1
  • Output ต้องเป็น TStudio CSV มาตรฐาน (คอลัมน์: key | source | translation | context | file_path)
  • เก็บ script ทั้งหมดไว้ใน: E:\Mod_Workspace\Modder_project\modder-hub/05_Scripts_and_Tools/
  • [กฎเหล็ก] Script ต้องห้ามแก้ไขหรือลบแท็กโค้ดของเกมเด็ดขาด: %s {0} <color=red> \n \r
  • [หมายเหตุ Fast-Track Auto-Pilot]: เมื่อเขียนและทดสอบสคริปต์สกัด/แพ็กเบื้องต้นสำเร็จ ให้ลุยต่อเข้าสู่ "ขั้นตอนที่ 3 (Proof of Concept)" ทันทีโดยไม่ต้องหยุดรอคำสั่ง!

────────────────────────────────────────────────────
⭐ ขั้นตอนที่ 3 — Proof of Concept: ทำให้ Main Menu แสดงภาษาThai
[GATE — ห้ามผ่านไปขั้นตอนที่ 4 จนกว่าภาษาThaiจะแสดงในเกมได้จริง]
────────────────────────────────────────────────────
  เป้าหมาย: พิสูจน์ว่าเกมสามารถ render ภาษาThaiได้ก่อนที่จะแปลทั้งหมด

  3.1  ดึงเฉพาะข้อความ Main Menu (~5–20 บรรทัด) โดยใช้ script จากขั้นตอนที่ 2

  3.2  แปลข้อความเหล่านั้นเป็นภาษาThaiด้วยตัวคุณเองเลยทันที
       (ไม่ต้องใช้ TStudio หรือ TRun สำหรับขั้นตอนนี้)
       ตัวอย่าง:
         "New Game"    →  "เริ่มเกมใหม่"
         "Continue"    →  "เล่นต่อ"
         "Settings"    →  "ตั้งค่า"
         "Quit"        →  "ออกจากเกม"
       [CHECKPOINT] Backup ไฟล์ต้นฉบับก่อน → จากนั้น Pack ค่าแปลกลับเข้าเกม

  3.3  แจ้งให้ฉันรันเกมและตรวจสอบ Main Menu
       ✅ เกณฑ์สำเร็จ (ต้องผ่านทุกข้อ):
         • ไม่มีกล่องสี่เหลี่ยม □□□ แทนที่ตัวอักษร
         • ไม่มีตัวอักษรเพี้ยนหรือเครื่องหมายคำถาม
         • สระและวรรณยุกต์อยู่ตำแหน่งถูกต้อง (สำคัญมากสำหรับภาษาไทย)
         • เกมไม่ crash ตอนโหลดเมนู

  3.4  ถ้าภาษาThaiยังไม่แสดงถูกต้อง — ให้วินิจฉัยตาม Diagnostic Tree:

       [D1] ข้อความถูกแทนที่จริงในไฟล์หรือไม่?
            → Hex-dump ไฟล์ที่ packed แล้ว ยืนยันว่า byte ใหม่อยู่ที่ offset ถูกต้อง
            → ถ้าไม่ถูกแทนที่: pack script มี bug → แก้ script ก่อน

       [D2] ข้อความถูกแทนที่แล้วแต่แสดงเป็นกล่องสี่เหลี่ยม (tofu)?
            → Font ของเกมไม่รองรับ Unicode ภาษาThai
            → Escalation Ladder:
                Level 1: สลับ font ของเกมด้วย TTF ที่รองรับThai
                          (เช่น Noto Sans Thai) เก็บไว้ใน E:\Mod_Workspace\Modder_project\modder-hub/03_Font_and_UI/
                Level 2: ถ้า font เป็น Sprite/Atlas: rebuild atlas ให้มี glyph ภาษาThai
                Level 3: ถ้า font ฝังอยู่ใน engine: patch ผ่าน BepInEx/REFramework hook
                Level 4 (สุดท้าย): Runtime hook — สกัดกั้น render call แล้วสลับ font ใน memory

       [D3] ข้อความแสดงแต่ encoding ผิด (ตัวอักษรเพี้ยน)?
            → Encoding ไม่ตรง → ลองตามลำดับ: UTF-8 → UTF-8 BOM → UTF-16LE → CP874
            → Repack ด้วย encoding ที่ถูกต้องแล้วทดสอบใหม่

       [D4] ข้อความแสดงถูกแต่เกมโหลดไฟล์เก่าอยู่?
            → เกมอาจ cache หรือ hash-check assets
            → ลอง: ล้าง cache folder · ปิด integrity check · ใช้ loose file override

       วนซ้ำ 3.2–3.4 จนสำเร็จ ห้ามไปขั้นตอนที่ 4 จนกว่า GATE จะผ่าน

  3.5  [POC GATE — การส่งมอบให้ผู้ใช้เปิดเกมทดสอบจริง]
       เมื่อ AI ดำเนินการ:
         1. สกัดข้อความ Main Menu (~5–20 บรรทัด)
         2. แปลเป็นภาษาไทย
         3. สำรองไฟล์เกมเดิมไปยัง 01_Original_Backup/ (ตั้งเป็น Read-only)
         4. ปรับจูนฟอนต์ไทย (PUA / MCP / TrueType offset +160 units)
         5. แพตช์ไฟล์แปลภาษาไทยเข้าสู่ Game Directory เรียบร้อยแล้ว
       → ให้หยุดการทำงานที่จุดนี้ แล้วรายงานสรุปสิ่งที่ทำทั้งหมด พร้อมเชิญชวนผู้ใช้:
         "🎮 ดำเนินการขั้นตอนที่ 1 - 3 สำเร็จแล้ว! กรุณาเปิดเกมเพื่อทดสอบหน้า Main Menu ได้เลยครับ!"
       → รอผู้ใช้ตรวจสอบและแจ้งผล หากหน้าเมนูแสดงภาษาไทยได้สมบูรณ์ จึงค่อยผ่าน GATE ไปขั้นตอนที่ 4

────────────────────────────────────────────────────
ขั้นตอนที่ 4 — Full Extraction → ส่งต่อให้ TStudio/TRun (Deep Scan & โครงสร้าง 2 ไฟล์หลัก)
(เริ่มได้หลัง Step 3 GATE ผ่านแล้วเท่านั้น)
────────────────────────────────────────────────────
  4.1 การสกัดข้อความทั้งหมดแบบเจาะลึก (Deep Extraction Protocol):
      • สแกนค้นหาข้อความทั้งเกมอย่างละเอียดที่สุด โดยเฉพาะเกม Unity หรือ Engine ซับซ้อนที่ข้อความมักซ่อนลึกกว่าปกติ:
        - Unity Deep Scan: สแกนลึกทุก AssetBundles และ Addressables ใน StreamingAssets/ และโฟลเดอร์ย่อยทั้งหมด
        - สแกน resources.assets, sharedassets*.assets, globalgamemanagers
        - สแกน MonoBehaviour serialized objects (ScriptableObjects, ระบบบทสนทนา Dialogue Trees, เควสต์, UI Text/TextMeshPro) ที่ TextAsset ทั่วไปมองไม่เห็น
        - สแกนระบบ Localization ของ Unity (Unity Localization StringTable/AssetTable, I2 Localization I2Languages.asset)
        - ตรวจสอบ IL2CPP metadata (global-metadata.dat / String Literals) หากมีข้อความถูกคอมไพล์ฝังในโค้ด C#
        - ตรวจสอบ Nested script/data: JSON, XML, Yarn Spinner, Ink bytecode, Naninovel, SQLite
      • ตรวจนับจำนวนบรรทัดและ String ทั้งหมด ให้มั่นใจว่าไม่มีข้อความหลุดรอดแม้แต่ประโยคเดียว

  4.2 รวมไฟล์ให้อยู่ในโครงสร้าง 2 ไฟล์หลักใน Workspace (Consolidated 2-File Structure):
      • รวมข้อความทั้งหมดที่สกัดได้ไว้ที่: E:\Mod_Workspace\Modder_project\modder-hub/02_Translation_Workspace/
      • ที่รูทของโฟลเดอร์ Workspace จะต้องมีเพียง 2 ไฟล์หลักนี้เท่านั้น:
        1. en_original.csv  → ไฟล์ต้นฉบับภาษาอังกฤษสมบูรณ์ 100% (Single Source of Truth / Read-only Reference) ห้ามแก้ไข ใช้สำหรับเทียบ Diff และทำ Automated QA
        2. translate_TH.csv → ไฟล์เป้าหมายสำหรับนำไปแปลภาษาไทย ตามฟอร์แมตมาตรฐาน TStudio (คอลัมน์: key | source | translation | context | file_path) พร้อมส่งต่อให้ TStudio หรือ TRun แปลชุดใหญ่ทันที

  4.3 จัดเก็บไฟล์ทดสอบเดิมเข้าคลังปลอดภัย (Quarantine & Archive Test Slices — ห้ามลบทิ้ง):
      • ไฟล์ข้อความชิ้นส่วนที่เคยสกัดมาเทสในขั้นตอนที่ 3 (POC / slice test files) มีข้อมูล offset, header, และ binary layout ที่สำคัญมาก "ห้ามลบทิ้งเด็ดขาด"
      • ให้เขียนสคริปต์ย้ายไฟล์ทดสอบทั้งหมดไปเก็บไว้ที่:
        E:\Mod_Workspace\Modder_project\modder-hub/02_Translation_Workspace/_archive_test/ (หรือ E:\Mod_Workspace\Modder_project\modder-hub/01_Original_Backup/test_slices/)
      • เพื่อให้โฟลเดอร์ทำงานสะอาดเรียบร้อย และป้องกันไม่ให้ TStudio/TRun ดึงไฟล์เทสไปแปลปนกับงานจริง

  4.4 การส่งต่องานและการตรวจสอบ (Handoff & Validation):
      • แจ้งให้ฉันนำไฟล์ translate_TH.csv ไปใช้กับ TRun หรือ TStudio เพื่อแปลชุดใหญ่
      • เตรียม Packer script สำหรับนำ translate_TH.csv ที่แปลเสร็จแล้ว Pack กลับเข้าเกมตาม file_path ดั้งเดิม
      • เขียน Validator Script เพื่อตรวจสอบเทียบ translate_TH.csv กับ en_original.csv ว่าไม่มีแท็กโค้ด (%s, {{0}}, <color=...>) หรือบรรทัดใดตกหล่น

────────────────────────────────────────────────────
ขั้นตอนที่ 5 — การแพ็คไฟล์แจกจ่าย (06_Releases), คู่มือติดตั้ง & บันทึกคัมภีร์ลง Modding-Knowledge
────────────────────────────────────────────────────
เมื่อทดสอบเล่นเกมจริงผ่าน และได้รับการอนุมัติว่างานแปลสมบูรณ์:

5.1 บันทึกคัมภีร์ลงคลังความรู้ (Game Localization Bible):
    • เขียนคัมภีร์ทางเทคนิคฉบับสมบูรณ์ (Markdown) ประกอบด้วย 8 หมวดหมู่วิศวกรรมย้อนกลับ:
      1. ข้อมูลสรุปและโครงสร้าง Engine ของเกม (File signatures, compression, AES encryption)
      2. วิธีการสกัดข้อความ และสคริปต์แปลงกลับ (Archive tools, .locres/.json/.assets)
      3. ระบบฟอนต์และการแก้ปัญหาสระลอย/วรรณยุกต์ (PUA Font mapping, SDF font injection หรือ TTF replacement)
      4. การป้องกันแท็กโค้ดและความปลอดภัยของข้อความแปล (Tag protection, regex rules)
      5. สคริปต์แพ็คไฟล์กลับเข้าตัวเกมแบบอัตโนมัติ (Python automation)
      6. โครงสร้างโฟลเดอร์แจกจ่าย 06_Releases และคู่มือติดตั้ง_README.txt
      7. อุปสรรคและแนวทางแก้ไขปัญหาที่พบ (Troubleshooting & Workarounds)
      8. การเปรียบเทียบกับเกมอื่น/เอนจินอื่น (Cross-Game/Engine Comparison)
    • บันทึกลงใน:
      E:/Mod_Workspace/Modding-Knowledge/Engines/Unreal_Engine_4/Games/TestGame/TestGame_Thai_Localization_Bible.md
      (ข้อบังคับการตั้งชื่อ: ต้องตั้งชื่อไฟล์ตามชื่อโฟลเดอร์เกมเสมอ `TestGame_Thai_Localization_Bible.md` ห้ามใช้ generic `Thai_Localization_Bible.md` อย่างเด็ดขาด)
    • อัปเดตสารบัญกลาง `E:\Mod_Workspace\Modding-Knowledge/_Index/MASTER_INDEX.md`:
      เพิ่มรายการลงในตารางโดยเรียงตามลำดับตัวอักษร A-Z:
      `| **TestGame** | Unreal Engine | ★★★☆☆ | [TestGame_Thai_Localization_Bible.md](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unreal_Engine_4/Games/TestGame/TestGame_Thai_Localization_Bible.md) |`

5.2 จัดโครงสร้างโฟลเดอร์ 06_Releases ให้ผู้เล่น Copy ทับตัวเกมได้ทันที:
    • จัดเตรียมโฟลเดอร์: E:\Mod_Workspace\Modder_project\modder-hub/06_Releases/TestGame_ThaiMod_v1.0/
    • วางโครงสร้างโฟลเดอร์ให้ตรงกับรูทของตัวเกมเป๊ะๆ เพื่อให้ผู้เล่นเพียงแค่ Copy โฟลเดอร์ไปวางทับใน Game Directory ก็เล่นได้เลย
      (รวมไฟล์แปลภาษา, ฟอนต์, รวมถึงตัวปลดล็อค mod เช่น SigBypass, dsound.dll, BepInEx หากเกมนั้นต้องใช้)

5.3 สร้างคู่มือติดตั้งภาษาไทย (คู่มือติดตั้ง_README.txt):
    • นับจำนวนบรรทัด/ประโยคทั้งหมดที่แปลจาก CSV ใน Workspace
    • เขียนไฟล์ E:\Mod_Workspace\Modder_project\modder-hub/06_Releases/TestGame_ThaiMod_v1.0/คู่มือติดตั้ง_README.txt (และ README_TH.txt) ตามเทมเพลตมาตรฐานดังนี้:

=============================================================
      Mod ภาษาไทย สำหรับเกม TestGame (v1.0) NodNuatTranslator
=============================================================

รายละเอียดการแปล:
-------------------------------------------------------------
แปลภาษาไทยครบถ้วนสมบูรณ์ ทั้งหมด [ระบุจำนวน] ประโยค/บรรทัด

วิธีติดตั้ง (Installation):
-------------------------------------------------------------
1. แตกไฟล์ Zip ที่ดาวน์โหลดมา
2. คุณจะเห็นโฟลเดอร์สำหรับติดตั้ง
3. ให้นำโฟลเดอร์หรือไฟล์ทั้งหมดนี้ ไปวางทับในโฟลเดอร์เกม TestGame ของคุณ
   (ตัวอย่างพาทของเกม: [ระบุตำแหน่งโฟลเดอร์ติดตั้งเกม])
4. หากระบบถามให้เขียนทับหรือรวมโฟลเดอร์ ให้กดยอมรับ (Replace/Merge)
5. เข้าเกมและสนุกได้เลย!

* โครงสร้างของ Mod ที่จะถูกติดตั้งเข้าไป:
  1. ไฟล์แปลภาษา: [ระบุตำแหน่งไฟล์แปล เช่น Content/Paks/~mods/...]
  2. ตัวเสริม/ปลดล็อค: [ระบุ dll หรือ loader ถ้ามี เช่น SigBypass, BepInEx]

วิธีลบ Mod ออก (Uninstall):
-------------------------------------------------------------
เข้าไปลบไฟล์ [ระบุชื่อไฟล์แปล] ออก เพียงเท่านี้เกมจะกลับเป็นภาษาเดิมครับ

=============================================================
ขอให้สนุกกับการเล่นเกมภาษาไทยครับ!
=============================================================

สามารถสนับสนุนได้ตามช่องทางด้านล่างนี้เลยครับ ขอบคุณทุกการสนับสนุนครับ!
ช่องทางสนับสนุน: สนับสนุน
สามารถติดตามช่องทาง mod อื่นได้ที่หน้าเว็บไซส์ : หน๊ด หนวด translator
ติดต่อพูดคุยผ่าน Facebook : หน๊ด หนวด translator
ผู้จัดทำ: หน๊ด หนวด translator (NodNuatTranslator)

5.4 สร้างไฟล์ Zip สำหรับแจกจ่าย:
    • บีบอัดโฟลเดอร์เป็น: E:\Mod_Workspace\Modder_project\modder-hub/06_Releases/TestGame_ThaiMod_v1.0.zip
    • ตรวจสอบว่าในไฟล์ .zip มีโฟลเดอร์เกมที่พร้อมวางทับ และมี "คู่มือติดตั้ง_README.txt" เรียบร้อยแล้ว
══════════════════════════════════════════════════════
🔤 ข้อมูลสเปกฟอนต์ไทยและระบบเลื่อนสระ PUA (THub Font Suite)
══════════════════════════════════════════════════════
ฟอนต์ที่เลือกใช้งาน:      Prompt (พร้อม) — Modern Loopless Sans
ไฟล์ฟอนต์หลัก (TTF):      E:\Mod_Workspace\Modder_project\modder-hub/03_Font_and_UI/Prompt/Prompt-Bold_PUA.ttf
ช่วงรหัส PUA:            U+F000 ถึง U+F89F (จัดรูปสระวรรณยุกต์ล่วงหน้า 2,208 รูป)
ไฟล์ชุดเครื่องมือในโปรเจกต์: • E:\Mod_Workspace\Modder_project\modder-hub/03_Font_and_UI/Mapping.json
                         • E:\Mod_Workspace\Modder_project\modder-hub/03_Font_and_UI/Char.txt
                         • E:\Mod_Workspace\Modder_project\modder-hub/03_Font_and_UI/thai_font_mapper.py

  • วิธีทำฟอนต์สำหรับ Unreal Engine (Slate / UMG):
    1. นำ Prompt-Bold_PUA.ttf ไปวางใน E:\Mod_Workspace\Modder_project\modder-hub/03_Font_and_UI/Prompt/
    2. สร้างหรือเปิด Font Asset ใน Unreal Content Browser
    3. เพิ่ม Font Face ชี้ไปที่ไฟล์ Prompt-Bold_PUA.ttf
    4. ฟอนต์ชุดนี้มี PUA (2,208 รูป) และ Glyph ครบถ้วน รองรับ FreeType Text Shaper ของ Unreal
    5. สำหรับไฟล์ข้อความที่แปลง ให้รัน E:\Mod_Workspace\Modder_project\modder-hub/03_Font_and_UI/thai_font_mapper.py เพื่อเลื่อนสระให้อัตโนมัติ

══════════════════════════════════════════════════════
[โปรโตคอล A] ค้นหาและโหลดเครื่องมืออัตโนมัติ 🔧
══════════════════════════════════════════════════════
เมื่อต้องการเครื่องมือและไม่พบใน [ระบุตำแหน่งโฟลเดอร์เครื่องมือ]:
  ขั้น 1 — ค้นหาในเครื่อง: สแกน [ระบุตำแหน่งโฟลเดอร์เครื่องมือ] แบบ Recursive หา binary ที่ต้องการ
  ขั้น 2 — ดาวน์โหลดอัตโนมัติ: ค้นหา Release ล่าสุดบน GitHub (QuickBMS, UEViewer, AssetStudio ฯลฯ)
           ดาวน์โหลด Binary มาไว้ใน [ระบุตำแหน่งโฟลเดอร์เครื่องมือ] แล้วรายงานความคืบหน้า
  ขั้น 3 — รายงานผู้ใช้: หากโหลดล้มเหลว ให้หยุดและถามผู้ใช้พร้อมเสนอทางเลือก [A/B/C]

══════════════════════════════════════════════════════
[โปรโตคอล B] การจัดการข้อจำกัดและอุปสรรค 🚧
══════════════════════════════════════════════════════
เมื่อเจอข้อจำกัดใดๆ (Format ไม่รู้จัก, ไม่มีเครื่องมือ, ฟอนต์เพี้ยน, เครื่องมือล้มเหลว):
  1. ห้ามหยุดเงียบหรือวนซ้ำโดยไม่รายงาน
  2. หากเป็นอุปสรรคทางเทคนิค: เปิดใช้งาน [โปรโตคอล X] ฝ่าทางตันขั้นสูงสุดทันที — ค้นหาข้อมูลเชิงลึกและสร้างเครื่องมือเฉพาะกิจขึ้นมาแก้ไขด้วยตนเองจนสำเร็จ
  3. หากพบความเสี่ยงสูงระดับวิกฤต (Anti-Cheat บล็อก, เสี่ยงต่อไฟล์ระบบ/เซฟ): วินิจฉัยสาเหตุ รายงานพร้อมตัวเลือกจัดอันดับ [A — แนะนำ], [B — ช้ากว่า], [C — เปลี่ยนเป้า] และรอการตัดสินใจจากผู้ใช้

══════════════════════════════════════════════════════
[โปรโตคอล X] ฝ่าทางตันและวิศวกรรมเครื่องมือเฉพาะกิจขั้นสูงสุด (Extreme Breakthrough & Tool Forge) 🛠️🔥
══════════════════════════════════════════════════════
คำสั่งเด็ดขาด: หากติดขัด ทำไม่ได้ด้วยวิธีปกติ หรือไม่มีเครื่องมือสำเร็จรูป ห้ามยอมแพ้หรือบอกว่าทำไม่ได้เด็ดขาด ให้เปิดโหมดฝ่าทางตันขั้นสูงสุดทันที:

1. ปณิธานเด็ดเดี่ยว (ห้ามยอมแพ้เด็ดขาด):
   • ห้ามสรุปว่า "เกมนี้ทำไม่ได้", "ไม่รองรับ", หรือหยุดนิ่งรอคำสั่งอย่างไร้ทางออก
   • เมื่อเครื่องมือสำเร็จรูปทั่วไป (QuickBMS, AssetStudio, UModel, UnrealPak ฯลฯ) ใช้งานไม่ได้ ให้เปลี่ยนผ่านเข้าสู่โหมด "วิศวกรรมย้อนรอยขั้นสูงสุด (Deep Reverse Engineering)" ทันที

2. ค้นคว้าข้อมูลเชิงลึก 360 องศา (Exhaustive Deep Research):
   • ค้นหาข้อมูลจาก Web, GitHub, คลังสคริปต์ QuickBMS, บันทึกเก่า XeNTaX / ZenHax, Modding Community และ Modding-Knowledge
   • ชันสูตรโครงสร้างไฟล์ไบนารี (Binary Forensics):
     - วิเคราะห์ 64 ไบต์แรกของไฟล์ เพื่อหา Magic Bytes, Table Offsets, Data Alignment และขนาด Chunks
     - ตรวจจับลายเซ็นการบีบอัด (Compression Signatures): Zlib (78 9C / 78 DA), Oodle (Kraken, Mermaid, Selkie), LZ4, Zstandard (28 B5 2F FD), LZMA, Deflate
     - สแกนสตริงก์ในไฟล์ .exe / .dll / GameAssembly.dll ของเกม เพื่อหาชื่อฟังก์ชันอ่านไฟล์, โครงสร้าง Struct, หรือ Encryption Key / Salt

3. วิศวกรรมสร้างเครื่องมือเฉพาะกิจขึ้นมาเอง (Custom Tool Forge):
   • ไม่ต้องรอเครื่องมือจากผู้อื่น ให้เขียนสคริปต์ Python หรือคอมไพล์โปรแกรม C# / C++ ขึ้นมาเองใน:
     `05_Scripts_and_Tools/` หรือ `tools/flagship/GameBridges/`
     - Custom Binary Parser & Repacker: เขียนสคริปต์ Binary โดยใช้ struct, ctypes, หรือ io.BytesIO เพื่อแกะ Header, คลาย Payload, ดึงข้อความออกมาเป็น CSV/JSON และแพ็คกลับพร้อมคำนวณ Offset/Size/Checksum ใหม่ให้ถูกต้องสมบูรณ์
     - Custom Decryptor/Decompressor: เขียนอัลกอริทึมถอดรหัสหรือคลายการบีบอัดเฉพาะของเกมนั้นๆ
     - Font Surgery & Atlas Generator: หากฟอนต์แทนที่ไม่ได้ ให้ผ่าตัด Asset หรือสร้างฟอนต์ PUA เฉพาะกิจ ยกวรรณยุกต์ลอย +160 units
     - Runtime Memory Hook Fallback: หากไฟล์ในดิสก์ถูกล็อกด้วย DRM หรือระบบตรวจ Integrity Check ให้เปลี่ยนไปใช้เทคนิค Hook Memory (เช่น MinHook, DLL Proxy dxgi.dll/version.dll/dinput8.dll, หรือ BepInEx สำหรับ Unity) เพื่อดักจับและเปลี่ยนข้อความ/ฟอนต์ในหน่วยความจำขณะเกมทำงาน

4. การทดสอบและปรับจูนวนซ้ำจนกว่าจะสำเร็จ (Relentless Iterative Validation):
   • สร้างชุดทดสอบขนาดเล็ก (Micro-test): ทดลองกับข้อความ 1-2 บรรทัด หรือไฟล์ตัวอย่าง 1 ชิ้นก่อนเสมอ
   • ตรวจสอบความสมบูรณ์แบบ Roundtrip: สกัดไฟล์ → แพ็คกลับโดยไม่แก้ข้อความ → Binary Diff เทียบกับต้นฉบับ หากตรงกันหรือเกมเปิดได้ปกติ จึงเริ่มใส่ภาษาไทย
   • หากเกิด Exception หรือเกมแครช ให้อ่าน Error log วิเคราะห์ Stack Trace ปรับ Offset, Padding, Alignment แล้วรันซ้ำจนกว่าจะสำเร็จ 100%!

5. บันทึกองค์ความรู้ถาวร (Knowledge Codification):
   • เมื่อพิชิตอุปสรรคได้แล้ว ให้บันทึกโครงสร้างไฟล์และโค้ดของเครื่องมือเฉพาะกิจลงใน Modding-Knowledge ทันที เพื่อเป็นคัมภีร์ถาวรสำหรับโปรเจกต์ต่อๆ ไป

══════════════════════════════════════════════════════
[โปรโตคอล C] บันทึก Log การทำงาน 📋
══════════════════════════════════════════════════════
บันทึก Log ทุกขั้นตอนสำคัญลงใน:
  E:\Mod_Workspace\Modder_project\modder-hub/05_Scripts_and_Tools/session_log.md
รูปแบบ:
  ## [วันที่/เวลา] ขั้นตอนที่ X — [ชื่อขั้นตอน]
  - สิ่งที่ทำ: ...
  - ผลลัพธ์: สำเร็จ / ล้มเหลว
  - ไฟล์ที่เกี่ยวข้อง: ...

══════════════════════════════════════════════════════
[โปรโตคอล P] Autonomous POC Fast-Track (ปฏิบัติการอัตโนมัติ ขั้นตอน 1–3) ⚡
══════════════════════════════════════════════════════
ลดภาระของผู้ใช้ในการคอยกดยืนยันทีละสเต็ปในขั้นตอนที่ 1 ถึง 3:
  1. เมทริกซ์การประเมินความมั่นใจ (Confidence Evaluation Matrix):
     • มั่นใจสูง (High Confidence >= 80%):
       - ตรวจพบ Engine ชัดเจน หรือมีคู่มือ/คัมภีร์ใน Modding-Knowledge
       - มีเครื่องมือแกะหรือ MCP Server พร้อมใช้งาน
       - ไม่มี Anti-Cheat ที่ขัดขวางการแก้ไฟล์
       → ปฏิบัติการ: ลุยขั้นตอนที่ 1 (วิเคราะห์) → ขั้นตอนที่ 2 (เขียน Bridge) → ขั้นตอนที่ 3 (สำรองไฟล์, จูนฟอนต์, แพตช์ Main Menu ภาษาไทยเข้าเกม) รวดเดียวโดยไม่ต้องหยุดถาม!
     • มั่นใจต่ำ (Low Confidence < 80%):
       - รูปแบบไฟล์ไม่คุ้นเคย หรือมีการเข้ารหัส/บีบอัดที่ไม่ทราบอัลกอริทึม
       - มีความเสี่ยงต่อไฟล์ระบบหรือเซฟเกม
       → ปฏิบัติการ: หยุดรายงานผลที่ขั้นตอนที่ 1 และสอบถามผู้ใช้ก่อนเขียนโค้ด
  2. กฎความปลอดภัยระหว่างรันอัตโนมัติ:
     • ต้องคัดลอกไฟล์ต้นฉบับไปยัง 01_Original_Backup/ (และตั้งค่าเป็น Read-only) ก่อนแตะไฟล์เกมจริงเสมอ
     • บันทึกการกระทำทุกขั้นตอนลงใน E:\Mod_Workspace\Modder_project\modder-hub/05_Scripts_and_Tools/session_log.md
     • ทำ Read-back Verification ตรวจสอบความถูกต้องของไฟล์ที่แพตช์ก่อนประกาศว่า POC พร้อม
  3. การส่งมอบงาน (POC Gate Handoff):
     • ผู้ใช้มีหน้าที่หลักเพียงแค่เปิดเกมเพื่อดูว่าภาษาไทยแสดงผลได้จริง
     • หยุดรอผู้ใช้เฉพาะที่จุด "ขั้นตอนที่ 3 (Proof of Concept Gate)" เท่านั้น พร้อมแจ้งข้อแนะนำการตรวจเช็คในเกม

══════════════════════════════════════════════════════
เริ่มต้นการทำงาน (โหมด Autonomous POC Fast-Track ⚡)
══════════════════════════════════════════════════════
ยืนยันความเข้าใจใน ecosystem, กฎความปลอดภัย, ระบบ Fast-Track และโปรโตคอลฝ่าทางตันขั้นสูงสุด (Extreme Breakthrough)
จากนั้นเริ่มขั้นตอนที่ 1 ทันที:
สแกน [ระบุตำแหน่งโฟลเดอร์ติดตั้งเกม], ตรวจสอบ Engine และค้น Knowledge Base
• หากความมั่นใจสูง (>= 80%): ดำเนินการขั้นตอนที่ 1 → 2 → 3 (แบ็กอัป + สกัด/แปล Main Menu + จูนฟอนต์ + แพตช์เข้าเกม) ต่อเนื่องอัตโนมัติทันที แล้วจึงส่งมอบให้ฉันเปิดเกมทดสอบ!
• หากความมั่นใจต่ำ (< 80%): รายงานผลที่ขั้นตอนที่ 1 และสอบถามข้อตกลงก่อนดำเนินการต่อ
• หากติดขัดหรือทำไม่ได้ด้วยวิธีปกติ: ห้ามยอมแพ้เด็ดขาด ให้เปิดใช้งาน [โปรโตคอล X] ฝ่าทางตันขั้นสูงสุด ค้นหาข้อมูลเชิงลึกและสร้างเครื่องมือเฉพาะกิจขึ้นมาเองจนสำเร็จให้จงได้ โดยใช้เทคนิคขั้นสูงสุด!