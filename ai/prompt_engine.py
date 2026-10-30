import os
import re
from core.engine_scanner import EngineScanner
from core.knowledge_service import KnowledgeService

KNOWLEDGE_DIR = r"E:\Mod_Workspace\Modding-Knowledge"
GITHUB_KB_URL = "https://github.com/memolyviza2012-max/Modding-Knowledge"

class PromptEngine:
    """
    Advanced Engineering Prompt Engine for THub 2.2.
    Generates high-precision, context-aware Master Prompts for:
      1. Web Chat (ChatGPT / Claude Web) - Consultant Mode
      2. Autonomous Agents (Claude Code / Antigravity / Cursor) - Operation Mode
    """

    @classmethod
    def get_bible_info(cls, engine_name, safe_name, doc_type="Thai_Localization_Bible", matched_engine_folder=None, matched_bible=None, workspace_path=""):
        """
        Determines the exact standardized Bible file path, font assets folder, and Index paths.
        Aligns with Modding-Knowledge & Rivet Engineer Advanced standards:
          Engines/{engine_folder}/Games/{game_folder}/{game_folder}_{doc_type}.md
        """
        target_folder = matched_engine_folder
        game_folder = safe_name

        if matched_bible:
            if matched_bible.get("engine_folder"):
                target_folder = matched_bible["engine_folder"]
            if matched_bible.get("game_folder"):
                game_folder = matched_bible["game_folder"]

        if not target_folder:
            clean_alnum = re.sub(r'[^a-z0-9]', '', (engine_name or "").lower())
            ALIAS_MAP = {
                "unrealengine": "Unreal_Engine_5",
                "unreal": "Unreal_Engine_5",
                "unrealengine5": "Unreal_Engine_5",
                "unrealengine4": "Unreal_Engine_4",
                "unrealengine3": "Unreal_Engine_3",
                "unrealengine2": "Unreal_Engine_2",
                "cengine": "C_Engine",
                "c": "C_Engine",
                "reengine": "RE_Engine",
                "mtframework": "MT_Framework",
                "fledge": "Fledge",
                "fledgeengine": "Fledge",
                "asura": "Asura_Engine",
                "asuraengine": "Asura_Engine",
                "void": "Void_Engine",
                "voidengine": "Void_Engine",
                "marvelous": "Marvelous_Engine",
                "marvelousengine": "Marvelous_Engine",
                "aurora": "Aurora_Engine",
                "auroraengine": "Aurora_Engine",
                "odyssey": "Aurora_Engine",
                "odysseyengine": "Aurora_Engine",
                "cdc": "Crystal Dynamics Foundation Engine",
                "cdcengine": "Crystal Dynamics Foundation Engine",
                "crystaldynamics": "Crystal Dynamics Foundation Engine",
                "foundationengine": "Crystal Dynamics Foundation Engine",
                "katana": "Gust_Engine",
                "gust": "Gust_Engine",
                "katanagust": "Gust_Engine",
                "gustengine": "Gust_Engine",
                "10tons": "10tons_Engine",
                "10tonsengine": "10tons_Engine",
                "dawn": "Dawn_Engine",
                "dawnengine": "Dawn_Engine",
                "idtech": "id_Tech_6",
                "idtech6": "id_Tech_6",
                "idtech7": "id_Tech_7",
                "custom": "Custom_Engine",
                "customengine": "Custom_Engine",
                "unity": "Unity",
            }
            if clean_alnum in ALIAS_MAP:
                target_folder = ALIAS_MAP[clean_alnum]
            else:
                eng_dir = os.path.join(KNOWLEDGE_DIR, "Engines")
                if os.path.isdir(eng_dir):
                    try:
                        for ef in os.listdir(eng_dir):
                            if clean_alnum == re.sub(r'[^a-z0-9]', '', ef.lower()):
                                target_folder = ef
                                break
                    except Exception:
                        pass

        filename = f"{game_folder}_{doc_type}.md"
        if target_folder:
            rel_dir = f"Engines/{target_folder}/Games/{game_folder}"
        else:
            rel_dir = f"Games/{game_folder}"
            
        full_path = f"{KNOWLEDGE_DIR}/{rel_dir}/{filename}".replace("\\", "/")
        font_assets_dir = f"{KNOWLEDGE_DIR}/{rel_dir}/Assets/Fonts/".replace("\\", "/")
        master_index_path = f"{KNOWLEDGE_DIR}/_Index/MASTER_INDEX.md".replace("\\", "/")
        engine_index_path = f"{KNOWLEDGE_DIR}/_Index/ENGINE_INDEX.md".replace("\\", "/")
        workspace_bible = f"{workspace_path}/05_Scripts_and_Tools/{filename}".replace("\\", "/") if workspace_path else ""

        return {
            "filename": filename,
            "game_folder": game_folder,
            "rel_dir": rel_dir,
            "full_path": full_path,
            "font_assets_dir": font_assets_dir,
            "master_index_path": master_index_path,
            "engine_index_path": engine_index_path,
            "workspace_bible_path": workspace_bible,
            "engine_folder": target_folder or engine_name or "Unknown Engine"
        }

    @classmethod
    def _build_bible_specification_block(cls, bible_info, project_name, engine_name, workspace_path, is_en=False):
        """
        Builds the comprehensive, standardized Bible Specification & Knowledge Sync block.
        Strictly conforms to Rivet Engineer Advanced and Modding-Knowledge standards:
          1. Exact naming & title convention
          2. Complete Table of Contents
          3. 10 Mandatory Technical Sections
          4. 5 Destination paths & sync protocol
        """
        fname = bible_info["filename"]
        game_folder = bible_info["game_folder"]
        full_path = bible_info["full_path"]
        font_assets_dir = bible_info["font_assets_dir"]
        ws_bible = bible_info.get("workspace_bible_path") or f"{workspace_path}/05_Scripts_and_Tools/{fname}".replace("\\", "/")
        m_index = bible_info["master_index_path"]
        e_index = bible_info["engine_index_path"]
        eng_folder = bible_info["engine_folder"]

        if is_en:
            return f"""══════════════════════════════════════════════════════
📖 BIBLE SPECIFICATION & KNOWLEDGE SYNC (RIVET ENGINEER STANDARD)
══════════════════════════════════════════════════════
You MUST document the complete technical modding knowledge into a standardized Bible:

1. NAMING & HEADER CONVENTION (STRICT COMPLIANCE):
   • Exact Filename: `{fname}`
     ⚠️ CRITICAL: NEVER use generic names like `Thai_Localization_Bible.md` or `Bible.md`.
        The filename MUST strictly match the game folder: `{fname}`.
   • H1 Main Title: `# 📖 {project_name} — Thai Localization Modding Bible`
   • Subtitle: `### Advanced Deep Analysis Edition (Rivet Engineer)`
   • Standard Metadata Blockquote (Right under title):
     > **Engine:** {engine_name}  
     > **Game ID / Version:** {project_name} (Steam / PC)  
     > **Complexity Rating:** ★★★☆☆ (Specify reason: e.g. Multi-target locres, Pak lock, code tags)  
     > **Status:** ✅ Verified & Playable  
     > **Translator:** หน๊ด หนวด translator (NodNuatTranslator)  
     > **Documented by:** THub Modding Team  
     > **Last Updated:** [YYYY-MM-DD]

2. TABLE OF CONTENTS:
   Must include anchor links jumping to all 10 mandatory sections:
   1. [1. Overview & Mod Architecture Pattern](#1-overview--mod-architecture-pattern)
   2. [2. Technical Stack](#2-technical-stack)
   3. [3. File Architecture](#3-file-architecture)
   4. [4. Font Analysis & Typography](#4-font-analysis--typography)
   5. [5. Text System Analysis](#5-text-system-analysis)
   6. [6. Cross-Engine Comparison](#6-cross-engine-comparison)
   7. [7. Modding Pipeline & Build Scripts](#7-modding-pipeline--build-scripts)
   8. [8. Troubleshooting, Traps & Lessons Learned](#8-troubleshooting-traps--lessons-learned)
   9. [9. Required Tools](#9-required-tools)
   10. [10. Extracted Assets & Releases](#10-extracted-assets--releases)

3. 10 MANDATORY TECHNICAL SECTIONS (NEVER SKIP ANY SECTION):
   Section 1 — Overview & Mod Architecture Pattern:
     - Game overview, developer, engine version.
     - Mod pattern classification: File Replacement / Runtime Injection (BepInEx, REFramework) / Binary Patch Overlay / Hybrid.
   Section 2 — Technical Stack Table:
     - Markdown table with Engine, Developer, Archive Format, AES Encryption flag, Compression algorithm (Zlib/LZ4/Oodle/None), Font System, Thai Font Used, Text Container, Text Encoding, and Mod Complexity (1-5 stars with justification).
   Section 3 — File Architecture (ASCII Directory Tree):
     - Complete annotated ASCII tree covering original game assets, unpacked assets, and THub workspace folders (01_Original_Backup to 07_Image_Resources).
   Section 4 — Font Analysis & Typography:
     - Font asset format (.ufont, raw TTF/OTF, Unity TMP SDF Atlas, bitmap .fnt).
     - Raw font extraction details or font swap mappings.
     - Thai typography handling: PUA range U+F000 to U+F89F (2,208 glyphs), tone mark shifting / floating vowel avoidance.
   Section 5 — Text System Analysis:
     - Container format (.locres, .msg, .json, .csv, string table), total string counts.
     - File encoding (UTF-8, UTF-8 BOM, UTF-16 LE, CP874).
     - Strict preservation rules for game placeholder tags (%s, {{0}}, <color=red>, \\n, \\r).
   Section 6 — Cross-Engine Comparison:
     - Cross-reference with at least 1 other game in Modding-Knowledge utilizing the same/similar engine to contrast techniques.
   Section 7 — Modding Pipeline & Build Scripts:
     - Step-by-step pipeline divided into Font Pipeline and Text Pipeline.
     - Provide FULL, production-ready, runnable Python bridge scripts (Unpacker, Packer, Tag Validator) with zero placeholder code.
   Section 8 — Troubleshooting, Traps & Lessons Learned:
     - Real-world obstacles encountered & solutions (PAK encryption locks, signature bypass, font tofu □□□, crash on load, encoding corruption).
   Section 9 — Required Tools Table:
     - Markdown table with Tool Name, Version, Specific Purpose, and Source/Link.
   Section 10 — Extracted Assets, Releases & Media:
     - Direct links to extracted real font files (TTF/OTF) in Assets/Fonts/ or `EXTRACTION_NOTE.txt` explaining why vector data was destroyed.
     - Overview of 06_Releases folder structure and คู่มือติดตั้ง_README.txt.
     - Overview of 07_Image_Resources (Official Art, PSD Templates, AI Logo Generation Prompts).

4. 5 DESTINATION PATHS & KNOWLEDGE SYNC PROTOCOL:
   You MUST write or sync the outputs to ALL 5 destinations:
   [Dest 1] Primary Bible in Modding-Knowledge:
            `{full_path}`
   [Dest 2] Extracted Fonts Directory:
            `{font_assets_dir}`
            (Save installable TTF/OTF fonts or EXTRACTION_NOTE.txt here)
   [Dest 3] Workspace Local Copy:
            `{ws_bible}`
   [Dest 4] Master Index Registration:
            `{m_index}`
            Insert alphabetically (A-Z) into the table:
            `| **{project_name}** | {eng_folder} | [{fname}](file:///{full_path}) |`
   [Dest 5] Engine Index Registration:
            `{e_index}`
            Insert under `## ⚙️ {eng_folder}`:
            `| **{project_name}** | `{game_folder}` | [{fname}](file:///{full_path}) |`"""
        else:
            return f"""══════════════════════════════════════════════════════
📖 ข้อกำหนดการเขียนคัมภีร์ม็อด & ซิงค์คลังความรู้ (มาตรฐาน Rivet Engineer)
══════════════════════════════════════════════════════
คุณต้องจัดทำคัมภีร์ทางเทคนิค (Bible) ฉบับสมบูรณ์ตามมาตรฐานวิศวกรรมย้อนกลับของ Modding-Knowledge:

1. มาตรฐานการตั้งชื่อและหัวเรื่อง (Header & Naming Rules - กฎเหล็ก):
   • ชื่อไฟล์คัมภีร์: `{fname}`
     ⚠️ กฎเหล็ก: ห้ามใช้ชื่อทั่วๆ ไปอย่าง `Thai_Localization_Bible.md` หรือ `Bible.md` อย่างเด็ดขาด
        ชื่อไฟล์ต้องขึ้นต้นด้วยชื่อโฟลเดอร์ของเกมเสมอ: `{fname}`
   • หัวเรื่องหลัก H1: `# 📖 {project_name} — Thai Localization Modding Bible`
   • หัวเรื่องรอง Subtitle: `### Advanced Deep Analysis Edition (Rivet Engineer)`
   • บล็อก Metadata มาตรฐาน (วางใต้หัวเรื่องทันที):
     > **Engine:** {engine_name}  
     > **Game ID / Version:** {project_name} (Steam / PC)  
     > **ระดับความยาก (Complexity):** ★★★☆☆ (ระบุเหตุผล เช่น Multi-target locres, ล็อก Signature, แท็กโค้ดซับซ้อน)  
     > **สถานะ (Status):** ✅ สำเร็จ — ทดสอบและเล่นได้จริง  
     > **ผู้แปล (Translator):** หน๊ด หนวด translator (NodNuatTranslator)  
     > **ผู้เขียนเอกสาร (Documented by):** THub Modding Team  
     > **อัปเดตล่าสุด (Last Updated):** [ระบุวันที่ YYYY-MM-DD]

2. สารบัญ (Table of Contents):
   ต้องมีสารบัญพร้อม Anchor Link ไปยังหัวข้อหลักทั้ง 10 หมวดหมู่อย่างครบถ้วน:
   1. [1. ภาพรวมโปรเจค & สถาปัตยกรรมม็อด](#1-ภาพรวมโปรเจค--สถาปัตยกรรมม็อด)
   2. [2. ตาราง Technical Stack](#2-ตาราง-technical-stack)
   3. [3. โครงสร้างไดเรกทอรีและไฟล์](#3-โครงสร้างไดเรกทอรีและไฟล์)
   4. [4. การวิเคราะห์ระบบฟอนต์](#4-การวิเคราะห์ระบบฟอนต์)
   5. [5. การวิเคราะห์ระบบข้อความ](#5-การวิเคราะห์ระบบข้อความ)
   6. [6. การเปรียบเทียบข้ามเอนจิ้น](#6-การเปรียบเทียบข้ามเอนจิ้น)
   7. [7. ขั้นตอนการสร้างม็อด & สคริปต์อัตโนมัติ](#7-ขั้นตอนการสร้างม็อด--สคริปต์อัตโนมัติ)
   8. [8. กับดักและบทเรียนที่ได้รับ](#8-กับดักและบทเรียนที่ได้รับ)
   9. [9. เครื่องมือที่จำเป็น](#9-เครื่องมือที่จำเป็น)
   10. [10. ไฟล์ที่สกัดได้ & สรุปชุดแจกจ่าย](#10-ไฟล์ที่สกัดได้--สรุปชุดแจกจ่าย)

3. โครงสร้างเนื้อหา 10 หมวดหมู่วิศวกรรมย้อนกลับ (บังคับครบทุกหมวด ห้ามข้าม):
   หมวดที่ 1 — ภาพรวมโปรเจค & สถาปัตยกรรมม็อด (Overview & Mod Architecture Pattern):
     - ข้อมูลเกม, ผู้พัฒนา, เวอร์ชัน Engine
     - จำแนกรูปแบบม็อด: File Replacement / Runtime Injection (BepInEx, REFramework) / Binary Patch Overlay / Hybrid
   หมวดที่ 2 — ตาราง Technical Stack & สรุปข้อมูลทางเทคนิค:
     - ตาราง Markdown: Engine, Developer, Archive Format, การเข้ารหัส AES, ขั้นตอนการบีบอัด (Zlib/LZ4/Oodle/None), ระบบฟอนต์, ฟอนต์ไทยที่ใช้, ชนิดข้อความ (.locres/.json/.msg/CSV), Encoding, ระดับความยาก
   หมวดที่ 3 — โครงสร้างไดเรกทอรีและไฟล์ (File Architecture):
     - วาด ASCII Tree แสดงตำแหน่งไฟล์จริงในเกมและโครงสร้าง Workspace (01_Original_Backup ถึง 07_Image_Resources) พร้อมคำอธิบาย
   หมวดที่ 4 — การวิเคราะห์ระบบฟอนต์ (Font Analysis & Typography):
     - โครงสร้างจัดเก็บฟอนต์ (.ufont, raw TTF/OTF, Unity TMP SDF Atlas, bitmap .fnt)
     - วิธีสกัดฟอนต์จริง (TTF/OTF) หรือการทำ Font Swap
     - สเปกฟอนต์ไทยและการจัดการสระลอย/วรรณยุกต์ซ้อน (ช่วงรหัส PUA U+F000 ถึง U+F89F รวม 2,208 รูป)
   หมวดที่ 5 — การวิเคราะห์ระบบข้อความ (Text System Analysis):
     - โครงสร้างไฟล์ข้อความ (.locres, .msg, .json, .csv, string table), จำนวนบรรทัด/ประโยคทั้งหมด
     - การตรวจสอบ Encoding (UTF-8, UTF-8 BOM, UTF-16 LE, CP874)
     - กฎเหล็กในการคงแท็กโค้ดของเกม (%s, {{0}}, <color=red>, \\n, \\r) ห้ามตกหล่นเด็ดขาด
   หมวดที่ 6 — การเปรียบเทียบกับเกมอื่น/เอนจินอื่น (Cross-Engine Comparison):
     - เทียบเคียงกับเกมอื่นในคลังความรู้ Modding-Knowledge ที่ใช้เอนจินเดียวกัน เพื่อถ่ายทอดแนวทางเทคนิค
   หมวดที่ 7 — ขั้นตอนการสร้างม็อด & สคริปต์อัตโนมัติ (Modding Pipeline & Automation Scripts):
     - ลำดับขั้นตอน Font Pipeline และ Text Pipeline
     - แนบโค้ดสคริปต์ Python ฉบับเต็มที่รันได้จริง (Unpacker, Packer, Tag Validator) ห้ามใช้โค้ดย่อ
   หมวดที่ 8 — อุปสรรค กับดัก และบทเรียนที่ได้รับ (Troubleshooting, Traps & Lessons Learned):
     - ปัญหาที่พบจริงและวิธีแก้ (PAK Lock, Signature Bypass, ตัวอักษรล่องหน, สระลอย, ปัญหา Encoding)
   หมวดที่ 9 — ตารางเครื่องมือที่จำเป็น (Required Tools Table):
     - สรุปเครื่องมือ เวอร์ชัน หน้าที่การทำงาน และลิงก์ดาวน์โหลด (TStudio, TRun, repak, FModel, UABEA ฯลฯ)
   หมวดที่ 10 — ไฟล์ที่สกัดได้, สรุปชุดแจกจ่าย & สื่อประชาสัมพันธ์ (Extracted Assets, Release & Media):
     - ลิงก์ไปยังฟอนต์ที่สกัดได้จริงในโฟลเดอร์ Assets/Fonts/ (หากสกัดไม่ได้ต้องมี EXTRACTION_NOTE.txt อธิบายสาเหตุ)
     - โครงสร้างโฟลเดอร์แจกจ่าย 06_Releases พร้อมไฟล์ คู่มือติดตั้ง_README.txt
     - สรุปทรัพยากรโฟลเดอร์สื่อประชาสัมพันธ์ 07_Image_Resources (ภาพ Official Art จาก Steam, เทมเพลต PSD สำหรับ Facebook/Header, และไฟล์คำสั่ง AI Logo Prompt)

4. ปลายทางบันทึกและซิงค์ข้อมูลทั้ง 5 แห่ง (5 Destination Paths & Sync Protocol):
   คุณต้องบันทึกหรือซิงค์ไฟล์คัมภีร์ลงในทั้ง 5 ตำแหน่งนี้:
   [จุดที่ 1] คลังความรู้หลัก Modding-Knowledge:
            `{full_path}`
   [จุดที่ 2] โฟลเดอร์เก็บไฟล์ฟอนต์จริงที่สกัดได้ (Assets/Fonts):
            `{font_assets_dir}`
            (บันทึกไฟล์ฟอนต์ TTF/OTF หรือไฟล์ EXTRACTION_NOTE.txt ที่นี่)
   [จุดที่ 3] สำเนาใน Workspace โปรเจกต์:
            `{ws_bible}`
   [จุดที่ 4] ลงทะเบียนใน Master Index (เรียง A-Z):
            `{m_index}`
            เพิ่มแถวในตาราง:
            `| **{project_name}** | {eng_folder} | [{fname}](file:///{full_path}) |`
   [จุดที่ 5] ลงทะเบียนใน Engine Index (แยกตามเอนจิ้น):
            `{e_index}`
            เพิ่มแถวใต้หัวข้อ `## ⚙️ {eng_folder}`:
            `| **{project_name}** | `{game_folder}` | [{fname}](file:///{full_path}) |`"""

    @classmethod
    def _build_font_block(cls, selected_font, path, engine_name, is_en=False):
        """Builds engine-specific font and PUA instruction block."""
        try:
            from core.font_service import FontService
            fs = FontService()
            chosen_variant = None
            if isinstance(selected_font, str):
                font = fs.get_font_by_id(selected_font)
            elif isinstance(selected_font, dict):
                if "variant" in selected_font:
                    font = selected_font.get("font") or fs.get_font_by_id(selected_font.get("id"))
                    chosen_variant = selected_font.get("variant")
                elif "id" in selected_font and "style_name" in selected_font:
                    font = fs.get_font_by_id(selected_font["id"])
                    chosen_variant = selected_font
                else:
                    font = selected_font
            else:
                rec_fonts = fs.get_fonts_for_engine(engine_name)
                font = rec_fonts[0] if rec_fonts else fs.get_font_by_id("prompt")
        except Exception:
            font = None

        if not font:
            return ""

        fid = font.get("id", "prompt")
        fname_en = font.get("name_en", "Prompt")
        fname_th = font.get("name_th", "พร้อม")
        folder = font.get("folder", "Prompt")
        
        if chosen_variant and chosen_variant.get("rel_path"):
            primary_file = chosen_variant["rel_path"].replace("/", os.sep)
            chosen_style_th = chosen_variant.get("display_th", chosen_variant.get("style_name", "Bold (หนา)"))
            chosen_style_en = chosen_variant.get("style_name", "Bold")
        else:
            primary_file = font.get("primary_file", f"{folder}-Bold_PUA.ttf").replace("/", os.sep)
            chosen_style_th = "Bold (หนา) [ค่าเริ่มต้น]"
            chosen_style_en = "Bold [Default]"

        category = font.get("category", "Modern Sans")
        eng_lower = (engine_name or "").lower()

        if "unity" in eng_lower:
            engine_guide_th = f"""  • วิธีทำฟอนต์สำหรับ Unity (TextMeshPro Native & MCP Pipeline):
    1. ใช้ Unity Native Font MCP Server (`unity-native-font`) เพื่อจัดการฟอนต์และเรนเดอร์อัตโนมัติ
    2. รัน `build_thai_subset` ดึงอักขระ ASCII + Thai PUA จาก CSV สร้างเป็น characters.txt
    3. รัน `tune_thai_tone_marks` ยกวรรณยุกต์ไทย +160 units บนฟอนต์ PUA ({primary_file}) ป้องกันสระลอย/ตกขอบ
    4. สร้าง TMP Font Asset ใน Unity Editor ตามเวอร์ชันของเกม (Resolution 4096 x 4096 | Mode SDFAA)
    5. รัน `transplant_native_font` ฝัง FontAsset และ Texture Atlas ลงไฟล์ .assets ตรงๆ ผ่าน AssetsTools.NET
    6. รัน `verify_native_font` ตรวจสอบความถูกต้องของ Asset ป้องกันปัญหา Size overflow in allocator"""
            engine_guide_en = f"""  • Unity (TextMeshPro Native & MCP Pipeline):
    1. Use Unity Native Font MCP Server (`unity-native-font`) for automated native font transplanting.
    2. Run `build_thai_subset` to extract exact characters from translated CSV for TMP Font Asset Creator.
    3. Run `tune_thai_tone_marks` to elevate Thai tone marks (+160 units) on PUA font ({primary_file}).
    4. Build TMP Font AssetBundle in matching Unity engine version (4096 x 4096 | SDFAA mode).
    5. Run `transplant_native_font` to inject FontAsset & Atlas into target .assets file via AssetsTools.NET without allocator crashes.
    6. Run `verify_native_font` to confirm clean read-back and PUA glyph integrity."""
        elif "unreal" in eng_lower:
            engine_guide_th = f"""  • วิธีทำฟอนต์สำหรับ Unreal Engine (Slate / UMG):
    1. นำ {primary_file} ไปวางใน {path}/03_Font_and_UI/{folder}/
    2. สร้างหรือเปิด Font Asset ใน Unreal Content Browser
    3. เพิ่ม Font Face ชี้ไปที่ไฟล์ {primary_file}
    4. ฟอนต์ชุดนี้มี PUA (2,208 รูป) และ Glyph ครบถ้วน รองรับ FreeType Text Shaper ของ Unreal
    5. สำหรับไฟล์ข้อความที่แปลง ให้รัน {path}/03_Font_and_UI/thai_font_mapper.py เพื่อเลื่อนสระให้อัตโนมัติ"""
            engine_guide_en = f"""  • Unreal Engine (Slate / UMG) Font Workflow:
    1. Place {primary_file} in {path}/03_Font_and_UI/{folder}/
    2. In Unreal Editor, create or override a Font Asset / Font Face referencing {primary_file}.
    3. Font contains full PUA (2,208 glyphs) supporting Unreal's FreeType Text Shaper.
    4. Run {path}/03_Font_and_UI/thai_font_mapper.py on translated text files for clean vowel positioning."""
        elif "re" in eng_lower or "capcom" in eng_lower:
            engine_guide_th = f"""  • วิธีทำฟอนต์สำหรับ RE Engine (Capcom):
    1. ฟอนต์แนะนำคือ {fname_en} ({chosen_style_th}) เพื่อความคมชัดในสนามรบ
    2. ใช้ไฟล์ {primary_file} และชุดอักขระ {path}/03_Font_and_UI/Char.txt สำหรับสร้าง font atlas (.tex) หรือแทนที่ font_th.ttf
    3. รัน {path}/03_Font_and_UI/thai_font_mapper.py แปลงข้อความแปลเป็น PUA ก่อนแพ็คลง .pak"""
            engine_guide_en = f"""  • RE Engine (Capcom) Font Workflow:
    1. Recommended font is {fname_en} ({chosen_style_en}) for in-combat readability.
    2. Use {primary_file} and character set {path}/03_Font_and_UI/Char.txt to generate font atlas (.tex) or replace font_th.ttf.
    3. Run {path}/03_Font_and_UI/thai_font_mapper.py to encode text to PUA before repacking into .pak."""
        else:
            engine_guide_th = f"""  • วิธีทำฟอนต์ทั่วไป:
    1. สลับฟอนต์เกมด้วย {primary_file} ใน {path}/03_Font_and_UI/{folder}/
    2. ใช้ {path}/03_Font_and_UI/Char.txt สำหรับสร้าง Bitmap / Atlas Texture
    3. รัน {path}/03_Font_and_UI/thai_font_mapper.py กับข้อความแปล เพื่อป้องกันปัญหาสระลอย/สระจม"""
            engine_guide_en = f"""  • General Game Font Workflow:
    1. Replace game font with {primary_file} in {path}/03_Font_and_UI/{folder}/
    2. Use {path}/03_Font_and_UI/Char.txt for bitmap/atlas texture generation.
    3. Run {path}/03_Font_and_UI/thai_font_mapper.py on translated strings to prevent floating vowels."""

        if is_en:
            return f"""══════════════════════════════════════════════════════
🔤 THAI FONT & PUA GLYPH SPECIFICATIONS
══════════════════════════════════════════════════════
Selected Font:        {fname_en} ({fname_th}) — {category}
Selected Style:       {chosen_style_en}
Target TTF File:      {path}/03_Font_and_UI/{folder}/{os.path.basename(primary_file)}
PUA Mapping Range:    U+F000 to U+F89F (2,208 pre-shifted Thai glyphs)
Mapping Kit Files:    • {path}/03_Font_and_UI/Mapping.json
                      • {path}/03_Font_and_UI/Char.txt
                      • {path}/03_Font_and_UI/thai_font_mapper.py

{engine_guide_en}"""
        else:
            return f"""══════════════════════════════════════════════════════
🔤 ข้อมูลสเปกฟอนต์ไทยและระบบเลื่อนสระ PUA (THub Font Suite)
══════════════════════════════════════════════════════
ฟอนต์ที่เลือกใช้งาน:      {fname_en} ({fname_th}) — {category}
รูปแบบ / น้ำหนัก:       {chosen_style_th}
ไฟล์ฟอนต์เป้าหมาย (TTF): {path}/03_Font_and_UI/{folder}/{os.path.basename(primary_file)}
ช่วงรหัส PUA:            U+F000 ถึง U+F89F (จัดรูปสระวรรณยุกต์ล่วงหน้า 2,208 รูป)
ไฟล์ชุดเครื่องมือในโปรเจกต์: • {path}/03_Font_and_UI/Mapping.json
                         • {path}/03_Font_and_UI/Char.txt
                         • {path}/03_Font_and_UI/thai_font_mapper.py

{engine_guide_th}"""

    @classmethod
    def get_chat_prompt(cls, project, app_lang="th", selected_font=None):
        """Consultant Mode for browser-based Web Chat where AI has no local file access."""
        name = project.get("name", "Unknown Game")
        safe_name = re.sub(r'_+', '_', "".join(c if c.isalnum() or c in (" ", "_", "-") else "_" for c in name).strip().replace(" ", "_")).strip('_')
        path = project.get("path", "")
        game_dir = project.get("game_dir", "[ระบุตำแหน่งโฟลเดอร์ติดตั้งเกม]" if app_lang == "th" else "[Game directory not set]")
        tool_dir = project.get("tool_dir", "[ระบุตำแหน่งโฟลเดอร์เครื่องมือ]" if app_lang == "th" else "[Tool directory not set]")
        source_lang = project.get("source_lang", "English")
        target_lang = project.get("target_lang", "Thai")

        # Detect engine using multi-tier scanner
        engine_info = EngineScanner.detect_engine(
            game_dir=project.get("game_dir", ""),
            workspace_dir=path,
            title=name,
            saved_engine=project.get("engine")
        )
        engine_name = engine_info.get("badge", "Unknown Engine")
        suggested_tools = ", ".join(engine_info.get("tools", ["TStudio", "TRun"]))

        kb = KnowledgeService.get_instance()
        guides = kb.find_guides_for_engine(engine_name, game_title=name, tech_keywords=engine_info.get("detected_exts"), max_results=4)
        formatted_hints = []
        for g in guides:
            mtype = g.get("match_type")
            if mtype == "game_bible":
                prefix = "[⭐ คัมภีร์ตรงกับเกมนี้]"
            elif mtype == "tech_guide":
                prefix = "[🛠️ คู่มือเทคนิค/ระบบไฟล์ตรงกัน]"
            elif mtype == "engine_guide":
                prefix = "[📘 คู่มือ Engine]"
            else:
                prefix = "[🎮 เกม Engine เดียวกัน]"
            formatted_hints.append(f"  • {prefix} {g['title']} ({g['rel_path']})")
        guide_hints = "\n".join(formatted_hints)
        if not guide_hints:
            guide_hints = "  • (ค้นหาคู่มือเพิ่มเติมได้ที่ " + KNOWLEDGE_DIR + ")"

        matched_bible = guides[0] if guides and guides[0].get("match_type") == "game_bible" else None
        matched_ef = guides[0].get("engine_folder") if guides else None
        bible_info = cls.get_bible_info(
            engine_name, safe_name,
            matched_engine_folder=matched_ef,
            matched_bible=matched_bible,
            workspace_path=path
        )
        bible_spec = cls._build_bible_specification_block(bible_info, name, engine_name, path, is_en=(app_lang != "th"))

        font_block = cls._build_font_block(selected_font, path, engine_name, is_en=(app_lang != "th"))

        if app_lang == "th":
            return f"""🎮 Master Prompt: Game Localization Consultant ({target_lang} Mod) - THub Edition
========================================================================================

Context & Role: 
ฉันกำลังสร้าง Mod แปลภาษาระดับมืออาชีพสำหรับเกม: {name} 
โดยทำการแปลจากภาษา **{source_lang}** เป็นภาษา **{target_lang}**
เนื่องจากคุณทำงานบน Web Chat (เบราว์เซอร์) คุณจะ **ไม่มีสิทธิ์เข้าถึงไฟล์ในเครื่องของฉัน** 
ดังนั้น บทบาทของคุณคือ "ผู้เชี่ยวชาญให้คำปรึกษาและผู้เขียน Python Script" โดยฉันจะเป็นคนนำ Script ที่คุณเขียนไปรันบนเครื่องของฉันเอง

Environment & Workspace ของฉัน (เพื่อใช้อ้างอิงในการเขียนโค้ด):
- ชื่อเกม:              {name}
- Workspace:            {path} (ใช้โครงสร้าง 01 ถึง 07 ของ THub)
- Game Directory:       {game_dir}
- Tool Directory:       {tool_dir}
- ตรวจพบ Engine:        {engine_name} (เครื่องมือแนะนำ: {suggested_tools})
- Modding Knowledge:    {KNOWLEDGE_DIR}
- GitHub Knowledge:     {GITHUB_KB_URL}

คู่มือเทคนิคที่เกี่ยวข้องจากคลังความรู้:
{guide_hints}

{font_block}

══════════════════════════════════════════════════════
[สำคัญ] กฎเหล็กในการให้คำปรึกษาและเขียนโค้ด:
══════════════════════════════════════════════════════
1. ไฟล์ที่ต้องเขียนหรือบันทึก ทั้งหมดต้องอยู่ในขอบเขต Workspace ด้านบนเท่านั้น
2. โฟลเดอร์ "01_Original_Backup" มีไว้สำหรับสำรองข้อมูลดั้งเดิม ห้ามเขียน Script ใดๆ ที่เข้าไปแก้ไขไฟล์ในโฟลเดอร์นี้ ให้ Copy ออกมาทำงานข้างนอกเสมอ
3. เมื่อเขียน Script โปรดเขียนโค้ดแบบ "สมบูรณ์ พร้อมรันได้ทันที (Full Code)" ห้ามละไว้ในฐานที่เข้าใจหรือเขียนคอมเมนต์ประเภท `# เขียนโค้ดต่อตรงนี้`
4. เมื่อฉันส่งข้อมูลหรือ Log ข้อผิดพลาดมา ให้คุณวิเคราะห์เครื่องมือที่เหมาะสมและเขียนโค้ดแก้ปัญหาให้ฉันทีละขั้น

══════════════════════════════════════════════════════
ขั้นตอนการทำงานที่จะร่วมมือกัน (Milestones):
══════════════════════════════════════════════════════
1. Extraction & Analysis (สกัดไฟล์และวิเคราะห์โครงสร้าง)
   - แนะนำวิธีค้นหาและสกัดไฟล์ภาษาจากโฟลเดอร์เกม
2. Font & UI Architecture (วิเคราะห์ระบบฟอนต์และการแสดงผล)
   - วางแผนแปลงฟอนต์ตามสเปก PUA และระบบฟอนต์ที่ระบุด้านบน
3. Pre-Translation Glossary (วิเคราะห์คำศัพท์เฉพาะ)
   - เขียน Script สำหรับกวาดคำศัพท์เฉพาะ (ชื่อคน, สถานที่, ไอเทม) ออกมาทำ Glossary
4. Proof of Concept (แปลและทดสอบหน้าเมนูหลัก)
   - เขียน Script ช่วยดึง/ใส่ข้อความกลับ เพื่อให้ฉันทดสอบหน้า Main Menu
5. Script Customization & Deep Extraction (สกัดข้อความทั้งเกมแบบ Deep Scan):
   - เขียน Script สกัดข้อความทั้งเกมอย่างละเอียด (Deep Scan ครอบคลุม AssetBundles, MonoBehaviour, TextAsset, Localization Tables โดยเฉพาะ Unity ที่มักซ่อนลึก)
   - รวมข้อความทั้งหมดเข้าสู่โครงสร้าง 2 ไฟล์หลักใน Workspace: `en_original.csv` (ต้นฉบับอังกฤษ 100%) และ `translate_TH.csv` (พร้อมแปลใน TStudio)
   - ย้ายไฟล์ทดสอบเดิม (POC slices) ไปเก็บใน `02_Translation_Workspace/_archive_test/` (ห้ามลบทิ้ง) เพื่อป้องกันไฟล์สับสน
   - ระบบป้องกันไม่ให้แก้ไขแท็กโค้ดของเกม (เช่น %s, {{0}}, <color=red>) อย่างเด็ดขาด
6. Mass Translation & Automated QA (แปลชุดใหญ่, พิธีสารแปลสกิล & สแกนข้อผิดพลาด):
   - นำไฟล์ `translate_TH.csv` ไปแปลชุดใหญ่ด้วย TStudio หรือ TRun
   - **กฎเหล็กการอ่านครบทุกประโยค (100% Comprehensive Line Reading):** AI จำเป็นต้องอ่าน ตรวจสอบ และแปลข้อความทุกประโยคแบบครบถ้วน 100% ห้ามทำข้ามๆ หรือละไว้ในฐานที่เข้าใจ
   - **พิธีสารการแปลสกิลและวลีเกม (Skill, Spell & Phrase Localization Protocol):**
     * ต้องสืบค้นบริบท ธีมเกม คลาส และเอฟเฟกต์สกิลอย่างละเอียดก่อนแปล ห้ามแปลเดาสุ่ม
     * หากเป็นเกมแฟนตาซีและชื่อสกิลไม่ยาวเกินไป ให้แปลเป็น "วลีสั้นๆ 2-6 พยางค์" ที่สละสลวย (เช่น "ดาบเพลิงพิฆาต", "ระบำเงา", "ศรวายุ", "อสุนีบาตฟาด", "ทัณฑ์เทวา") แทนการแปลยาวทื่อๆ คำต่อคำ
     * หากเป็นคำเฉพาะ ชื่อเฉพาะ หรือศัพท์เฉพาะที่หาคำแปลตรงตัวไม่ได้ ให้ใช้ "การทับศัพท์" (เช่น "แร็กนาร็อค", "กุงเนียร์", "โอเวอร์ไดรฟ์", "ฟิเรก้า") ห้ามแปลแถไปเรื่อยจนความหมายเพี้ยน
     * บัญชีดำคำแปลกลไกผิด: Strike = ฟาดฟัน (ห้าม นัดหยุดงาน), Cast = ร่าย (ห้าม หล่อ/คัดเลือก), Cooldown = คูลดาวน์ (ห้าม เย็นลง), Checkpoint = แยกบริบท: เช็คพอยท์ สำหรับระบบเซฟ (ห้าม จุดตรวจ) / ด่านตรวจ สำหรับด่านทหาร-ตำรวจ (ห้าม เช็คพอยท์), Passive = สกิลติดตัว (ห้าม เฉยชา), Critical = คริติคอล (ห้าม วิกฤต), Lifesteal = ดูดเลือด (ห้าม ขโมยชีวิต), Respawn = เกิดใหม่ (ห้าม วางไข่)
   - เขียน Validator Script เพื่อเทียบเช็ค `translate_TH.csv` กับ `en_original.csv` ว่าแท็กโค้ดและตัวแปรไม่หล่นหายก่อนแพ็คกลับเข้าเกม
7. Final Release Package, Installation Guide & Knowledge Sync (ปิดงานและเผยแพร่)
   - เขียน Script จัดเตรียมโฟลเดอร์แจกจ่ายใน {path}/06_Releases/{name}_ThaiMod_v1.0/ โดยจัดโครงสร้างไฟล์ให้ตรงกับรูทของเกม เพื่อให้ผู้เล่นเพียงแค่ Copy ไปวางทับตัวเกมได้ทันที
   - สร้างไฟล์ "คู่มือติดตั้ง_README.txt" พร้อมนับสถิติประโยคที่แปล โครงสร้างม็อด วิธีลบม็อด และเครดิตผู้จัดทำ: "หน๊ด หนวด translator" (NodNuatTranslator)
   - จัดทำคัมภีร์ม็อดภาษาไทย (Thai Localization Bible) ตามมาตรฐานวิศวกรรมย้อนกลับ 10 หมวด และบันทึกลงปลายทางทั้ง 5 แห่ง:

{bible_spec}

   - เขียน Script บีบอัดเป็น .zip สำหรับแจกจ่ายงาน
8. Social Media Branding, PSD Templates & Thai Logo (07_Image_Resources)
   - ตรวจสอบและดึงภาพหน้าปกทางการของเกมจาก Steam CDN (Landscape 16:9, Poster 600x900, Hero 1920x620, Logo PNG) มาเก็บไว้ที่ {path}/07_Image_Resources/Official_Art/
   - ร่วมกันคิดไอเดียชื่อเกมภาษาไทย พร้อมสร้างไฟล์คำสั่ง {path}/07_Image_Resources/Generated_Logo/AI_Logo_Prompt.md สำหรับสั่ง AI เจนโลโก้ชื่อไทย 3D แบบพื้นหลังดำ เพื่อนำไปไดคัทง่ายๆ
   - นำไปประกอบกับเทมเพลต PSD ใน {path}/07_Image_Resources/ (เช่น Cover_Post facebook.psd, Header_facebook.psd, cover 16-9.psd) และเซฟไฟล์ภาพพร้อมโพสต์ลงเพจ หน๊ด หนวด translator ไว้ที่ 07_Image_Resources/Final_Exports/

Instructions for AI:
หากเข้าใจบทบาทของคุณแล้ว ให้ตอบกลับสั้นๆ ว่า:
"รับทราบ! ฉันเข้าใจบทบาทที่ปรึกษาและสภาพแวดล้อม Workspace เรียบร้อยแล้ว กรุณาแจ้งผลการสแกนหรือส่งตัวอย่างไฟล์ข้อความ เพื่อเริ่มขั้นตอนที่ 1 ได้ทันทีครับ"
"""
        else:
            return f"""🎮 Master Prompt: Game Localization Consultant ({target_lang} Mod) - THub Edition
========================================================================================

Context & Role: 
I am creating a professional localization Mod for the game: {name} 
Translating from **{source_lang}** to **{target_lang}**.
Since you are operating in a Web Chat environment (browser), you **DO NOT have access to my local files**. 
Therefore, your role is strictly an "Expert Consultant & Python Script Writer". I will run the scripts you write on my local machine.

My Environment & Workspace:
- Game:                 {name}
- Workspace:            {path} (Using THub's 01 to 07 folder structure)
- Game Directory:       {game_dir}
- Tool Directory:       {tool_dir}
- Detected Engine:      {engine_name} (Suggested Tools: {suggested_tools})
- Local Knowledge:      {KNOWLEDGE_DIR}
- GitHub Knowledge:     {GITHUB_KB_URL}

Relevant Knowledge Guides:
{guide_hints}

{font_block}

══════════════════════════════════════════════════════
[IMPORTANT] Consulting & Coding Rules:
══════════════════════════════════════════════════════
1. All scripts you write must output files within the Workspace defined above.
2. The "01_Original_Backup" is Read-Only — never overwrite it. Copy out before modifying.
3. When providing Python code, always write the FULL, runnable script. Never use placeholders (like `# rest of code`).
4. When I provide short context, hex dumps, or error logs, analyze what tools/methods are needed and write a step-by-step script for me to execute.

══════════════════════════════════════════════════════
Milestones to Support Me:
══════════════════════════════════════════════════════
1. Extraction & Analysis: scan for language files and unpack archives.
2. Font & UI Architecture: plan PUA encoding and glyph replacement per font specs above.
3. Pre-Translation Glossary: extract terms for glossary creation.
4. Proof of Concept: inject translated Main Menu to test rendering.
5. Script Customization & Deep Extraction:
   - Write deep extraction scripts (recursively scanning AssetBundles, MonoBehaviours, and localization assets, especially in Unity).
   - Consolidate all extracted text into 2 primary workspace files: `en_original.csv` (100% English master baseline) and `translate_TH.csv` (ready for TStudio translation).
   - Quarantine/archive Step 3 test slices into `_archive_test/` (never delete them).
   - Enforce strict game tag and variable preservation (%s, {{0}}, <color=red>).
6. Mass Translation, Skill Localization & Automated QA:
   - Process translate_TH.csv via TStudio or TRun.
   - **100% Line-by-Line Exhaustive Processing:** Read and translate every single line thoroughly. Never skip, omit, or summarize lines.
   - **Skill, Spell & Combat Phrase Localization Protocol:**
     * Conduct deep context & lore research (class, element, animation, fantasy genre) before translating.
     * Fantasy skill naming: For concise skill names (1-3 words), formulate punchy, elegant Thai compound phrases (e.g., 'ดาบเพลิงพิฆาต', 'ระบำเงา', 'ศรวายุ', 'ทัณฑ์เทวา') instead of robotic literal translations.
     * Transliteration (ทับศัพท์) for proper nouns, mythological terms, and untranslatable fantasy jargon (e.g., Ragnarok, Gungnir, Overdrive, Firaga). Never fabricate nonsensical translations.
     * Anti-MT blunder blacklist: Checkpoint -> Context-aware: เช็คพอยท์ for save mechanics (NEVER จุดตรวจ) vs ด่านตรวจ for military/police outposts (NEVER เช็คพอยท์), Strike -> ฟาดฟัน (NEVER นัดหยุดงาน), Cast -> ร่าย (NEVER หล่อ/คัดเลือก), Cooldown -> คูลดาวน์ (NEVER เย็นลง), Passive -> สกิลติดตัว (NEVER เฉยชา), Critical -> คริติคอล (NEVER วิกฤต), Lifesteal -> ดูดเลือด (NEVER ขโมยชีวิต), Respawn -> เกิดใหม่ (NEVER วางไข่).
   - Cross-check translate_TH.csv against en_original.csv using Validator scripts to verify no dropped tags or lines before repacking.
7. Final Release Package, Installation Guide & Knowledge Sync:
   - Structure the release in {path}/06_Releases/{name}_ThaiMod_v1.0/ so players can simply copy-paste directly into their game root folder to overwrite/merge.
   - Generate "คู่มือติดตั้ง_README.txt" with translated sentences count, installation steps, mod file structure, uninstall guide, and credit: "หน๊ด หนวด translator" (NodNuatTranslator).
   - Document a comprehensive technical Bible adhering strictly to Rivet Engineer 10-section standards and sync to all 5 destinations:

{bible_spec}

   - Compress the release into a final distribution .zip.
8. Social Media Branding, PSD Templates & Thai Logo (07_Image_Resources):
   - Check and download official game cover artworks from Steam CDN to {path}/07_Image_Resources/Official_Art/ (landscape 16:9, portrait 600x900, hero banner 1920x620, transparent logo.png).
   - Formulate creative Thai title translation concepts and generate/update {path}/07_Image_Resources/Generated_Logo/AI_Logo_Prompt.md for Midjourney / FLUX.1 / SDXL to render isolated 3D Thai game title logos.
   - Assemble promotional assets using PSD templates in {path}/07_Image_Resources/ (Facebook post, banner header, 16:9 cover) and export to 07_Image_Resources/Final_Exports/.

Instructions for AI:
If you understand your role, reply briefly with:
"Understood! I acknowledge my role as Consultant and know your Workspace paths. Please provide your engine files or directory listing to begin Step 1."
"""

    @classmethod
    def get_agent_prompt(cls, project, options=None, app_lang="th", selected_font=None):
        """Autonomous Agent Mode (Claude Code / Antigravity / Cursor) with full permissions, Gate system & Diagnostic Tree."""
        options = options or {}
        name = project.get("name", "Unknown Game")
        safe_name = re.sub(r'_+', '_', "".join(c if c.isalnum() or c in (" ", "_", "-") else "_" for c in name).strip().replace(" ", "_")).strip('_')
        path = project.get("path", "")
        game_dir = project.get("game_dir", "[ระบุตำแหน่งโฟลเดอร์ติดตั้งเกม]" if app_lang == "th" else "[Game directory not set]")
        tool_dir = project.get("tool_dir", "[ระบุตำแหน่งโฟลเดอร์เครื่องมือ]" if app_lang == "th" else "[Tool directory not set]")
        source_lang = project.get("source_lang", "English")
        target_lang = project.get("target_lang", "Thai")

        # Detect engine
        engine_info = EngineScanner.detect_engine(
            game_dir=project.get("game_dir", ""),
            workspace_dir=path,
            title=name,
            saved_engine=project.get("engine")
        )
        engine_name = engine_info.get("badge", "Unknown Engine")
        suggested_tools = ", ".join(engine_info.get("tools", ["TStudio", "TRun"]))
        tier = engine_info.get("tier", "unknown")
        tier_confidence_map = {
            "saved": 100,
            "game_dir_root": 95,
            "game_dir_sub": 90,
            "workspace": 85,
            "heuristic": 75,
            "fallback": 40
        }
        scanner_confidence = tier_confidence_map.get(tier, 70)
        auto_poc = options.get("auto_poc", True)

        is_en = (app_lang != "th")
        kb = KnowledgeService.get_instance()
        guides = kb.find_guides_for_engine(engine_name, game_title=name, tech_keywords=engine_info.get("detected_exts"), max_results=4)
        formatted_hints = []
        for g in guides:
            mtype = g.get("match_type")
            if is_en:
                prefix = "[⭐ Game Bible]" if mtype == "game_bible" else ("[🛠️ Tech/Format Guide]" if mtype == "tech_guide" else ("[📘 Engine Guide]" if mtype == "engine_guide" else "[🎮 Similar Engine Game]"))
            else:
                prefix = "[⭐ คัมภีร์ตรงกับเกมนี้]" if mtype == "game_bible" else ("[🛠️ คู่มือเทคนิค/ระบบไฟล์ตรงกัน]" if mtype == "tech_guide" else ("[📘 คู่มือ Engine]" if mtype == "engine_guide" else "[🎮 เกม Engine เดียวกัน]"))
            formatted_hints.append(f"  • {prefix} {g['title']} ({g['rel_path']})")
        guide_hints = "\n".join(formatted_hints)
        if not guide_hints:
            guide_hints = "  • (ค้นหาคู่มือเพิ่มเติมได้ที่ " + KNOWLEDGE_DIR + ")"

        matched_bible = guides[0] if guides and guides[0].get("match_type") == "game_bible" else None
        matched_ef = guides[0].get("engine_folder") if guides else None
        bible_info = cls.get_bible_info(
            engine_name, safe_name,
            matched_engine_folder=matched_ef,
            matched_bible=matched_bible,
            workspace_path=path
        )
        bible_path = bible_info["full_path"]
        bible_filename = bible_info["filename"]
        bible_spec = cls._build_bible_specification_block(bible_info, name, engine_name, path, is_en=is_en)

        if auto_poc:
            workflow_header_en = f"""══════════════════════════════════════════════════════
Milestones & Workflow (Autonomous POC Fast-Track Mode ⚡)
══════════════════════════════════════════════════════
⚡ [AUTONOMOUS FAST-TRACK EXECUTION: STEPS 1 TO 3]:
If you assess "High Confidence (Confidence >= 80%)" based on the detected engine, Knowledge Base guides, or standard formats:
  • You MUST execute Step 1 → Step 2 → Step 3 continuously in a single automated loop!
  • DO NOT stop or ask for user confirmation between Steps 1 and 2.
  • You are responsible for creating immutable backups (01_Original_Backup/), writing bridge scripts, extracting Main Menu lines, tuning/prepping the PUA font, patching {target_lang} text into the game, and verifying read-back.
  • The ONLY checkpoint where you pause for the user is: "Step 3 Proof of Concept Gate" — so the user can immediately launch the game to test {target_lang} rendering!
  • If confidence is LOW (< 80% e.g. unknown encryption, anti-cheat, high risk), pause at Step 1 to consult."""
            step1_decision_en = f"""
  1.4  [CONFIDENCE ASSESSMENT & AUTO-PILOT TRIGGER]
       Evaluate your Confidence Score before proceeding:
       • HIGH CONFIDENCE (>= 80%):
         Criteria: Recognized engine ({engine_name}, Scanner Confidence: {scanner_confidence}%), documented in Knowledge Base, standard format (.locres, .json, .csv, Unity MonoBehaviours), or bridge available, and NO blocking anti-cheat.
         → ACTION: Proceed IMMEDIATELY to Step 2 and Step 3 without waiting for user confirmation!
       • LOW CONFIDENCE (< 80%):
         Criteria: Unknown proprietary archive, custom encryption, or potential save/system corruption risk.
         → ACTION: Stop, report findings, and ask for user alignment before writing code."""
            step2_autopilot_en = f"""
  • [Fast-Track Auto-Pilot]: When Step 2 scripts are tested with a sample extract, proceed immediately to Step 3 (Proof of Concept) without pausing."""
            step3_gate_en = f"""
  3.5  [POC GATE — HANDOFF FOR IN-GAME VERIFICATION]
       Once you have:
         1. Extracted Main Menu text (~5–20 lines)
         2. Translated to {target_lang}
         3. Created read-only backup in 01_Original_Backup/
         4. Prepared/tuned font (PUA / MCP / vertical shift +160 units)
         5. Patched the translated menu and font into the Game Directory
       → PAUSE at this exact point, report a summary of actions, and instruct the user:
         "🎮 Autonomous POC (Steps 1–3) complete! Please launch the game now to verify if {target_lang} renders properly on the Main Menu!"
       → Await user verification. Once user confirms {target_lang} renders without bugs, proceed to Step 4."""

            workflow_header_th = f"""══════════════════════════════════════════════════════
Milestones & Workflow (โหมด Autonomous POC Fast-Track ⚡)
══════════════════════════════════════════════════════
⚡ [ระบบปฏิบัติการขั้นตอนที่ 1–3 อัตโนมัติ (Fast-Track)]:
หาก AI ประเมินแล้วว่ามี "ความมั่นใจเพียงพอ (Confidence Assessment: High >= 80%)":
  • ให้ AI ดำเนินการขั้นตอนที่ 1 → 2 → 3 ต่อเนื่องกันรวดเดียวโดยอัตโนมัติ!
  • ไม่ต้องหยุดรอการยืนยันทีละสเต็ประหว่างขั้นตอนที่ 1 และ 2
  • AI มีหน้าที่ทำไฟล์ต้นฉบับสำรอง (01_Original_Backup), เขียน Bridge, สกัดข้อความ Main Menu, จูนฟอนต์ PUA, แพตช์เมนูหลักภาษา{target_lang}เข้าเกม และตรวจสอบ Read-back ให้เสร็จสรรพ
  • จุดหยุดรอเดียว (Gate) คือ: "ขั้นตอนที่ 3 — ส่งมอบให้ผู้ใช้เปิดเกมทดสอบผลลัพธ์หน้า Main Menu"
  • หากความมั่นใจต่ำ (< 80% เช่น ติด Anti-cheat, รูปแบบบีบอัดไม่รู้จัก, ไฟล์เข้ารหัสซับซ้อน) ให้หยุดรายงานและปรึกษาผู้ใช้ที่ขั้นตอนที่ 1 ทันที"""
            step1_decision_th = f"""
  1.4  [การประเมินความมั่นใจ & การตัดสินใจรันอัตโนมัติ]
       ประเมินระดับความมั่นใจ (Confidence Score) ก่อนดำเนินการต่อ:
       • มั่นใจสูง (High Confidence >= 80%):
         เกณฑ์: ตรวจพบ Engine ชัดเจน ({engine_name}, Scanner Confidence: {scanner_confidence}%), มีคัมภีร์ใน Knowledge Base, หรือโครงสร้างไฟล์มาตรฐาน (.locres, .json, .csv, Unity MonoBehaviours ฯลฯ), และไม่มี Anti-Cheat ขัดขวาง
         → ปฏิบัติการ: ดำเนินการต่อเข้าสู่ "ขั้นตอนที่ 2" และ "ขั้นตอนที่ 3" ทันทีโดยไม่ต้องรอผู้ใช้สั่ง!
       • มั่นใจต่ำ (Low Confidence < 80%):
         เกณฑ์: รูปแบบไฟล์ไม่คุ้นเคย, เข้ารหัส/บีบอัดไม่ทราบชนิด, เสี่ยงกระทบไฟล์สำคัญหรือเซฟเกม
         → ปฏิบัติการ: หยุดรายงานผลและปรึกษาผู้ใช้ก่อนเขียนโค้ด"""
            step2_autopilot_th = f"""
  • [หมายเหตุ Fast-Track Auto-Pilot]: เมื่อเขียนและทดสอบสคริปต์สกัด/แพ็กเบื้องต้นสำเร็จ ให้ลุยต่อเข้าสู่ "ขั้นตอนที่ 3 (Proof of Concept)" ทันทีโดยไม่ต้องหยุดรอคำสั่ง!"""
            step3_gate_th = f"""
  3.5  [POC GATE — การส่งมอบให้ผู้ใช้เปิดเกมทดสอบจริง]
       เมื่อ AI ดำเนินการ:
         1. สกัดข้อความ Main Menu (~5–20 บรรทัด)
         2. แปลเป็นภาษา{target_lang}
         3. สำรองไฟล์เกมเดิมไปยัง 01_Original_Backup/ (ตั้งเป็น Read-only)
         4. ปรับจูนฟอนต์{target_lang} (PUA / MCP / TrueType offset +160 units)
         5. แพตช์ไฟล์แปลภาษา{target_lang}เข้าสู่ Game Directory เรียบร้อยแล้ว
       → ให้หยุดการทำงานที่จุดนี้ แล้วรายงานสรุปสิ่งที่ทำทั้งหมด พร้อมเชิญชวนผู้ใช้:
         "🎮 ดำเนินการขั้นตอนที่ 1 - 3 สำเร็จแล้ว! กรุณาเปิดเกมเพื่อทดสอบหน้า Main Menu ได้เลยครับ!"
       → รอผู้ใช้ตรวจสอบและแจ้งผล หากหน้าเมนูแสดงภาษา{target_lang}ได้สมบูรณ์ จึงค่อยผ่าน GATE ไปขั้นตอนที่ 4"""
        else:
            workflow_header_en = f"""══════════════════════════════════════════════════════
Milestones & Workflow
(Step-by-step. Only move forward when I say "Proceed to step...")
══════════════════════════════════════════════════════"""
            step1_decision_en = ""
            step2_autopilot_en = ""
            step3_gate_en = ""

            workflow_header_th = f"""══════════════════════════════════════════════════════
Milestones & Workflow
(ทำทีละขั้นตอน เมื่อฉันบอก "ผ่านขั้นตอนที่..." จึงจะย้ายไปข้อถัดไป)
══════════════════════════════════════════════════════"""
            step1_decision_th = ""
            step2_autopilot_th = ""
            step3_gate_th = ""

        parts = []

        if is_en:
            core = f"""🎮 Master Prompt: Game Localization Project ({target_lang} Mod) - THub Edition

Context & Goal:
I want to create a professional {target_lang} localization Mod for the game: {name}
Translating from **{source_lang}** to **{target_lang}**.
We will work together step-by-step. Here is the full project overview:

Environment & Workspace:
- Workspace:          {path}  (THub 01–07 folder structure)
- Game Directory:     {game_dir}
- Tool Directory:     {tool_dir}
- Detected Engine:    {engine_name} (Scanner Confidence: {scanner_confidence}%, Tier: {tier}, Tools: {suggested_tools})
- Modding Knowledge:  {KNOWLEDGE_DIR}
- Modding Knowledge (GitHub, always latest): {GITHUB_KB_URL}

Relevant Knowledge Guides:
{guide_hints}

══════════════════════════════════════════════════════
🏭 ECOSYSTEM: THub Translation Engine (READ-ONLY — DO NOT MODIFY)
══════════════════════════════════════════════════════
A stable, production-ready translation engine is already available at:
  {path}/tools/flagship/

  • TStudio  (TStudio/tstudio_app.py)    — GUI workspace for review & deploy
  • TRun     (TRun/trun_app.py)          — Automated batch translation engine
  • Core     (Core/tstudio_core.py,
              TStudio/file_converter.py) — API handler, format converter

⛔ CRITICAL CONSTRAINTS — NEVER VIOLATE:
  1. DO NOT modify core files: trun_app.py, tstudio_app.py, tstudio_core.py, file_converter.py
  2. DO NOT write your own LLM translation loop — use TRun for all batch translation
  3. Your scripts act as a Bridge only:
       Unpack  : game format  →  TStudio CSV
       Pack    : TStudio CSV  →  game format

TStudio CSV Standard Format:
  Columns : key | source | translation | context | file_path
  Example : MENU_001 | "New Game" | "" | "Main Menu > Buttons" | ui/menu.json
  Rules   : key must be unique · translation is empty when handed to TRun · never alter source column

══════════════════════════════════════════════════════
[IMPORTANT] Workspace Safety Rules
══════════════════════════════════════════════════════
  1. Never create files outside this Workspace.
  2. "01_Original_Backup" is Read-Only — never overwrite it. Copy out before modifying.
  3. Always write FULL, runnable code. Never use placeholders like "# rest of code".
  4. [CHECKPOINT RULE] Before every Pack operation that modifies Game Directory files,
     backup the target files to 01_Original_Backup/ and log the action in session_log.md.

{workflow_header_en}

────────────────────────────────────────────────────
Step 1 — Game File Analysis & Approach Decision
────────────────────────────────────────────────────
  1.1  Scan {game_dir} to identify:
         - Engine ({engine_name} detected)
         - Text container format (.json, .xml, .locres, .pak, .bin, proprietary...)
         - File encoding (UTF-8, UTF-8 BOM, ANSI, UTF-16...)
         - Archive structure wrapping the text (if any)

  1.2  [MANDATORY — KNOWLEDGE BASE CONSULTATION]
       Immediately after identifying the Engine/Format, before writing any code:
         → Search BOTH sources using these keywords:
             Local: {KNOWLEDGE_DIR}
             GitHub (always latest): {GITHUB_KB_URL}
             • Engine name  (e.g. "{engine_name}")
             • Format name  (e.g. "LOCRES", "PAK", "STR", "WIN", "BIN")
             • Game name    (e.g. "{name}")
         → Report your findings clearly:
             ✅ FOUND:     "Found [filename] — [brief summary of relevant guidance]"
             ❌ NOT FOUND: "No guide for [Engine/Format] in Knowledge Base. Will analyze from scratch."
         → If found: apply the guide's approach. Do not contradict it.
         → If not found: proceed with analysis and explain your reasoning.

  1.3  Choose & declare your Approach:
       [APPROACH A] Simple/parseable formats (.json, .xml, .csv, .txt, .locres...)
         → Write a Custom Parser Plugin:
            File: {path}/tools/flagship/TStudio/CustomParsers/[GameName]_parser.py
            Must implement: convert_to_csv(filepath) → TStudio CSV
            TStudio loads it automatically via its Plugin Manager.

       [APPROACH B] Heavy archives (.pak, .dat, .arc, .bin, encrypted bundles...)
         → Write two Standalone CLI scripts:
            [GameName]_unpacker.py  — extracts text → TStudio CSV
            [GameName]_packer.py    — reads translated CSV → repacks game format
            Store both in: {path}/05_Scripts_and_Tools/

       State which Approach you chose and WHY before writing any code.{step1_decision_en}

────────────────────────────────────────────────────
Step 2 — Write Bridge Script (TStudio Integration)
────────────────────────────────────────────────────
  • Write the extraction/injection script per your chosen Approach.
  • Output must be valid TStudio CSV (columns: key | source | translation | context | file_path).
  • Store all scripts in: {path}/05_Scripts_and_Tools/
  • [HARD RULE] Scripts must NEVER modify game tags/variables: %s {{0}} <color=red> \\n \\r{step2_autopilot_en}

────────────────────────────────────────────────────
⭐ Step 3 — Proof of Concept: Make Main Menu Show {target_lang}
[GATE — DO NOT proceed to Step 4 until {target_lang} renders correctly in-game]
────────────────────────────────────────────────────
  Goal: Prove the game CAN render {target_lang} before translating everything.

  3.1  Extract ONLY the Main Menu text (~5–20 lines) using your Step 2 script.

  3.2  Translate those lines yourself immediately (no TStudio / TRun needed here).
       Example translations for testing:
         "New Game"    →  "New Game ({target_lang} test)"
         "Continue"    →  "Continue ({target_lang} test)"
         "Settings"    →  "Settings ({target_lang} test)"
         "Quit"        →  "Quit ({target_lang} test)"
       [CHECKPOINT] Backup original files → then Pack the translated lines back.

  3.3  Tell the user to launch the game and check the Main Menu.
       ✅ SUCCESS criteria (ALL must pass):
         • No □□□ tofu/squares replacing text
         • No garbled characters or question marks
         • Vowels/diacritics in correct positions (critical for Thai)
         • No crash on menu load

  3.4  If {target_lang} does NOT display correctly — run this Diagnostic Tree:

       [D1] Is the text even replaced in the file?
            → Hex-dump the packed file. Confirm new bytes exist at the right offset.
            → If NOT replaced: the pack script has a bug. Fix it first.

       [D2] Text is replaced but showing squares/tofu?
            → Font does not support {target_lang} Unicode range.
            → Escalation Ladder:
                Level 1: Swap game font with a {target_lang}-compatible TTF
                          (e.g. Noto Sans Thai). Store in {path}/03_Font_and_UI/
                Level 2: If font is a Sprite/Atlas: rebuild the atlas with {target_lang} glyphs
                Level 3: If font is embedded in engine: patch via BepInEx/REFramework hook
                Level 4 (Last Resort): Runtime hook — intercept render call and replace font in memory

       [D3] Text shows but encoding is wrong (garbled output)?
            → File encoding mismatch. Try: UTF-8 → UTF-8 BOM → UTF-16LE → CP874
            → Re-pack with correct encoding and test again.

       [D4] Text shows but game ignores the file (old version loaded)?
            → Game may cache or hash-check assets.
            → Try: clear cache folder · disable integrity check · use loose file override

       Repeat 3.2–3.4 until SUCCESS. Do not move to Step 4 until GATE is cleared.{step3_gate_en}

────────────────────────────────────────────────────
Step 4 — Full Extraction → Hand off to TStudio/TRun (Deep Scan & 2-File Workspace)
(Only after Step 3 GATE is cleared)
────────────────────────────────────────────────────
  4.1 Deep Extraction Protocol (Zero-Omission Scan):
      • Aggressively extract ALL game text. In complex engines like Unity, text is often nested deeply:
        - Unity Deep Scan: Recursively scan all AssetBundles & Addressables in StreamingAssets/ and all subdirectories.
        - Inspect resources.assets, sharedassets*.assets, globalgamemanagers.
        - Scan serialized MonoBehaviour assets (ScriptableObjects, Dialogue System nodes, Quest trees, UI Text/TMP) that standard TextAsset dumpers miss.
        - Check Unity Localization Package (StringTable/AssetTable) and I2 Localization (I2Languages.asset).
        - Inspect IL2CPP metadata (global-metadata.dat / string literals) for hardcoded UI text.
        - Scan nested formats: JSON, XML, Yarn Spinner, Ink bytecode, Naninovel, SQLite databases.
      • Audit total strings to guarantee zero missing dialogue or UI strings.

  4.2 Consolidated 2-File Workspace Architecture:
      • Merge and organize all extracted text into: {path}/02_Translation_Workspace/
      • The workspace root must strictly contain ONLY 2 primary files for translation:
        1. en_original.csv  → 100% untouched English master baseline (Single Source of Truth) for QA diffing and validation.
        2. translate_TH.csv → Prepared Thai translation target in TStudio CSV format (columns: key | source | translation | context | file_path), ready for immediate batch translation via TStudio or TRun.

  4.3 Archive POC & Test Slices (Safety Quarantine — DO NOT DELETE):
      • Intermediate slices and POC test files from Step 3 contain critical offset, header, and binary structure context: NEVER delete them!
      • Automatically quarantine/move all test files into:
        {path}/02_Translation_Workspace/_archive_test/ (or {path}/01_Original_Backup/test_slices/)
      • Keep the main workspace clean so TStudio and TRun never ingest outdated test fragments.

  4.4 Handoff, Skill Localization & Validation:
      • Instruct the user to run TRun or open TStudio on translate_TH.csv to perform the batch translation.
      • Enforce 100% line-by-line exhaustive processing (read and translate every single line without skipping).
      • Apply Skill, Spell & Combat Phrase Localization Protocol: Research game lore/class context; translate concise fantasy skill names into punchy Thai compound phrases (e.g. 'ดาบเพลิงพิฆาต', 'ระบำเงา', 'ศรวายุ', 'ทัณฑ์เทวา'); use transliteration for proper nouns/mythical terms; block MT blunders (Checkpoint -> Context-aware: เช็คพอยท์ for save mechanics vs ด่านตรวจ for military/police outposts, Strike -> ฟาดฟัน NOT นัดหยุดงาน, Cast -> ร่าย NOT หล่อ).
      • Prepare the Packer script to inject translated strings from translate_TH.csv back into game assets based on file_path.
      • Write a Validator Script to cross-check translate_TH.csv against en_original.csv to guarantee no tags (%s, {{0}}, <color=...>) or lines were lost.

────────────────────────────────────────────────────
Step 5 — Packaging, Installation Guide & Modding Knowledge Sync
────────────────────────────────────────────────────
When translation and playtesting are complete and approved:

5.1 Document Technical Bible to Modding-Knowledge:
{bible_spec}

5.2 Prepare 06_Releases Directory (Direct Game-Root Overwrite Structure):
    • Clean & setup folder: {path}/06_Releases/{name}_ThaiMod_v1.0/
    • Structure the release folder so gamers can simply copy-paste directly into their game root directory to overwrite/merge:
      e.g.
        [GameRootDir]/
          └── Content/Paks/~mods/pakchunk999-ThaiMod_P.pak
          └── (Any required bypass/loaders like SigBypass / dsound.dll / BepInEx if needed)

5.3 Generate Installation Guide (คู่มือติดตั้ง_README.txt):
    • Count total lines/dialogues translated from the workspace CSV.
    • Create {path}/06_Releases/{name}_ThaiMod_v1.0/คู่มือติดตั้ง_README.txt (and README_TH.txt) using this exact template:

=============================================================
      Mod ภาษาไทย สำหรับเกม {name} (v1.0) NodNuatTranslator
=============================================================

รายละเอียดการแปล:
-------------------------------------------------------------
แปลภาษาไทยครบถ้วนสมบูรณ์ ทั้งหมด [ระบุจำนวนประโยค] ประโยค/บรรทัด

วิธีติดตั้ง (Installation):
-------------------------------------------------------------
1. แตกไฟล์ Zip ที่ดาวน์โหลดมา
2. คุณจะเห็นโฟลเดอร์สำหรับติดตั้ง
3. ให้นำโฟลเดอร์หรือไฟล์ทั้งหมดนี้ ไปวางทับในโฟลเดอร์เกม {name} ของคุณ
   (ตัวอย่างพาทของเกม: {game_dir})
4. หากระบบถามให้เขียนทับหรือรวมโฟลเดอร์ ให้กดยอมรับ (Replace/Merge)
5. เข้าเกมและสนุกได้เลย!

* โครงสร้างของ Mod ที่จะถูกติดตั้งเข้าไป:
  1. ไฟล์แปลภาษา: [ระบุไฟล์แปลภาษา เช่น .pak, .assets, หรือ .json]
  2. ตัวเสริม/ปลดล็อค: [ระบุ dll หรือ loader ถ้ามี เช่น SigBypass, BepInEx]

วิธีลบ Mod ออก (Uninstall):
-------------------------------------------------------------
เข้าไปลบไฟล์ [ระบุไฟล์ Mod ที่ติดตั้ง] ออก เพียงเท่านี้เกมจะกลับเป็นภาษาเดิมครับ

=============================================================
ขอให้สนุกกับการเล่นเกมภาษาไทยครับ!
=============================================================

สามารถสนับสนุนได้ตามช่องทางด้านล่างนี้เลยครับ ขอบคุณทุกการสนับสนุนครับ!
ช่องทางสนับสนุน: สนับสนุน
สามารถติดตามช่องทาง mod อื่นได้ที่หน้าเว็บไซส์ : หน๊ด หนวด translator
ติดต่อพูดคุยผ่าน Facebook : หน๊ด หนวด translator
ผู้จัดทำ: หน๊ด หนวด translator (NodNuatTranslator)

5.4 Build Distribution Archive:
    • Compress {path}/06_Releases/{name}_ThaiMod_v1.0/ into:
      {path}/06_Releases/{safe_name}_ThaiMod_v1.0.zip
    • Verify the zip contains both the ready-to-copy game files and the คู่มือติดตั้ง_README.txt

5.5 Social Media Branding & Thai Logo Generation (07_Image_Resources):
    • Ensure official game covers are saved in {path}/07_Image_Resources/Official_Art/ (Landscape 16:9, Portrait Poster 600x900, Hero Banner 1920x620, Transparent Logo PNG).
    • Formulate creative Thai title translation concepts and generate/update {path}/07_Image_Resources/Generated_Logo/AI_Logo_Prompt.md for Midjourney / FLUX.1 / SDXL to render isolated 3D Thai game title logos.
    • Guide the user to place official art and generated logos into the Photoshop PSD templates in {path}/07_Image_Resources/ (Facebook post, Facebook header, 16:9 cover) and export to 07_Image_Resources/Final_Exports/."""
            parts.append(core)
        else:
            core = f"""🎮 Master Prompt: Game Localization Project ({target_lang} Mod) - THub Edition

Context & Goal:
ฉันต้องการสร้าง Mod แปลภาษา {target_lang} ระดับมืออาชีพสำหรับเกม: {name}
โดยจะทำการแปลจากภาษา **{source_lang}** เป็นภาษา **{target_lang}**
เราจะทำงานร่วมกันทีละขั้นตอนอย่างเป็นระบบ นี่คือข้อมูลภาพรวมของโปรเจค:

Environment & Workspace:
- Workspace:          {path}  (ใช้โครงสร้าง 01–07 ของ THub)
- Game Directory:     {game_dir}
- Tool Directory:     {tool_dir}
- ตรวจพบ Engine:      {engine_name} (Scanner Confidence: {scanner_confidence}%, Tier: {tier}, เครื่องมือแนะนำ: {suggested_tools})
- Modding Knowledge:  {KNOWLEDGE_DIR}
- Modding Knowledge (GitHub, always latest): {GITHUB_KB_URL}

คลังความรู้ที่ตรวจพบ:
{guide_hints}

══════════════════════════════════════════════════════
🏭 ECOSYSTEM: THub Translation Engine (ห้ามแก้ไขโดยเด็ดขาด)
══════════════════════════════════════════════════════
โปรเจกต์นี้มี Translation Engine ที่ Stable และพร้อมใช้งานอยู่แล้วที่:
  {path}/tools/flagship/

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

{workflow_header_th}

────────────────────────────────────────────────────
ขั้นตอนที่ 1 — วิเคราะห์ไฟล์เกมและเลือก Approach
────────────────────────────────────────────────────
  1.1  สแกน {game_dir} เพื่อระบุ:
         - Engine ที่ใช้ ({engine_name} ตรวจพบ)
         - Format ไฟล์ข้อความ (.json, .xml, .locres, .pak, .bin, proprietary...)
         - Encoding ของไฟล์ (UTF-8, UTF-8 BOM, ANSI, UTF-16...)
         - โครงสร้าง Archive ที่ครอบข้อความอยู่ (ถ้ามี)

  1.2  [บังคับ — ค้น Knowledge Base ก่อนเขียนโค้ดใดๆ]
       ทันทีที่ระบุ Engine/Format ได้แล้ว ต้องทำก่อนเสมอ:
         → ค้นหาใน **ทั้ง 2 แหล่ง** ด้วย keyword เหล่านี้:
             Local : {KNOWLEDGE_DIR}
             GitHub (อัปเดตตลอด): {GITHUB_KB_URL}
             • ชื่อ Engine  (เช่น "{engine_name}")
             • ชื่อ Format  (เช่น "LOCRES", "PAK", "STR", "WIN", "BIN")
             • ชื่อเกม      (เช่น "{name}")
         → รายงานผลการค้นหาอย่างชัดเจน:
             ✅ พบ:     "พบไฟล์ [ชื่อไฟล์] — [สรุปแนวทางที่เกี่ยวข้อง]"
             ❌ ไม่พบ:  "ไม่พบข้อมูลสำหรับ [Engine/Format] ใน Knowledge Base จะวิเคราะห์เอง"
         → ถ้าพบคัมภีร์: ต้องนำแนวทางในคัมภีร์มาใช้ ห้ามทำขัดกับคัมภีร์
         → ถ้าไม่พบ: ค่อยวิเคราะห์เองและอธิบายเหตุผล

  1.3  ประกาศ Approach ที่เลือก:
       [APPROACH A] Format เรียบง่ายหรือแกะได้ (.json, .xml, .csv, .txt, .locres...)
         → เขียน Custom Parser Plugin:
            ไฟล์: {path}/tools/flagship/TStudio/CustomParsers/[GameName]_parser.py
            ต้องมีฟังก์ชัน: convert_to_csv(filepath) → TStudio CSV
            TStudio โหลดอัตโนมัติผ่าน Plugin Manager

       [APPROACH B] Archive หนัก (.pak, .dat, .arc, .bin, bundle ที่เข้ารหัส...)
         → เขียน Standalone CLI Scripts สองไฟล์:
            [GameName]_unpacker.py  — แตกข้อความ → TStudio CSV
            [GameName]_packer.py    — อ่าน CSV ที่แปลแล้ว → repack format เกม
            เก็บทั้งคู่ใน: {path}/05_Scripts_and_Tools/

        ระบุว่าเลือก Approach ไหนและเหตุผลก่อนเขียนโค้ด{step1_decision_th}

────────────────────────────────────────────────────
ขั้นตอนที่ 2 — เขียน Bridge Script (TStudio Integration)
────────────────────────────────────────────────────
  • เขียน script ตาม Approach ที่เลือกในขั้นตอนที่ 1
  • Output ต้องเป็น TStudio CSV มาตรฐาน (คอลัมน์: key | source | translation | context | file_path)
  • เก็บ script ทั้งหมดไว้ใน: {path}/05_Scripts_and_Tools/
  • [กฎเหล็ก] Script ต้องห้ามแก้ไขหรือลบแท็กโค้ดของเกมเด็ดขาด: %s {{0}} <color=red> \\n \\r{step2_autopilot_th}

────────────────────────────────────────────────────
⭐ ขั้นตอนที่ 3 — Proof of Concept: ทำให้ Main Menu แสดงภาษา{target_lang}
[GATE — ห้ามผ่านไปขั้นตอนที่ 4 จนกว่าภาษา{target_lang}จะแสดงในเกมได้จริง]
────────────────────────────────────────────────────
  เป้าหมาย: พิสูจน์ว่าเกมสามารถ render ภาษา{target_lang}ได้ก่อนที่จะแปลทั้งหมด

  3.1  ดึงเฉพาะข้อความ Main Menu (~5–20 บรรทัด) โดยใช้ script จากขั้นตอนที่ 2

  3.2  แปลข้อความเหล่านั้นเป็นภาษา{target_lang}ด้วยตัวคุณเองเลยทันที
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

  3.4  ถ้าภาษา{target_lang}ยังไม่แสดงถูกต้อง — ให้วินิจฉัยตาม Diagnostic Tree:

       [D1] ข้อความถูกแทนที่จริงในไฟล์หรือไม่?
            → Hex-dump ไฟล์ที่ packed แล้ว ยืนยันว่า byte ใหม่อยู่ที่ offset ถูกต้อง
            → ถ้าไม่ถูกแทนที่: pack script มี bug → แก้ script ก่อน

       [D2] ข้อความถูกแทนที่แล้วแต่แสดงเป็นกล่องสี่เหลี่ยม (tofu)?
            → Font ของเกมไม่รองรับ Unicode ภาษา{target_lang}
            → Escalation Ladder:
                Level 1: สลับ font ของเกมด้วย TTF ที่รองรับ{target_lang}
                          (เช่น Noto Sans Thai) เก็บไว้ใน {path}/03_Font_and_UI/
                Level 2: ถ้า font เป็น Sprite/Atlas: rebuild atlas ให้มี glyph ภาษา{target_lang}
                Level 3: ถ้า font ฝังอยู่ใน engine: patch ผ่าน BepInEx/REFramework hook
                Level 4 (สุดท้าย): Runtime hook — สกัดกั้น render call แล้วสลับ font ใน memory

       [D3] ข้อความแสดงแต่ encoding ผิด (ตัวอักษรเพี้ยน)?
            → Encoding ไม่ตรง → ลองตามลำดับ: UTF-8 → UTF-8 BOM → UTF-16LE → CP874
            → Repack ด้วย encoding ที่ถูกต้องแล้วทดสอบใหม่

       [D4] ข้อความแสดงถูกแต่เกมโหลดไฟล์เก่าอยู่?
            → เกมอาจ cache หรือ hash-check assets
            → ลอง: ล้าง cache folder · ปิด integrity check · ใช้ loose file override

       วนซ้ำ 3.2–3.4 จนสำเร็จ ห้ามไปขั้นตอนที่ 4 จนกว่า GATE จะผ่าน{step3_gate_th}

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
      • รวมข้อความทั้งหมดที่สกัดได้ไว้ที่: {path}/02_Translation_Workspace/
      • ที่รูทของโฟลเดอร์ Workspace จะต้องมีเพียง 2 ไฟล์หลักนี้เท่านั้น:
        1. en_original.csv  → ไฟล์ต้นฉบับภาษาอังกฤษสมบูรณ์ 100% (Single Source of Truth / Read-only Reference) ห้ามแก้ไข ใช้สำหรับเทียบ Diff และทำ Automated QA
        2. translate_TH.csv → ไฟล์เป้าหมายสำหรับนำไปแปลภาษาไทย ตามฟอร์แมตมาตรฐาน TStudio (คอลัมน์: key | source | translation | context | file_path) พร้อมส่งต่อให้ TStudio หรือ TRun แปลชุดใหญ่ทันที

  4.3 จัดเก็บไฟล์ทดสอบเดิมเข้าคลังปลอดภัย (Quarantine & Archive Test Slices — ห้ามลบทิ้ง):
      • ไฟล์ข้อความชิ้นส่วนที่เคยสกัดมาเทสในขั้นตอนที่ 3 (POC / slice test files) มีข้อมูล offset, header, และ binary layout ที่สำคัญมาก "ห้ามลบทิ้งเด็ดขาด"
      • ให้เขียนสคริปต์ย้ายไฟล์ทดสอบทั้งหมดไปเก็บไว้ที่:
        {path}/02_Translation_Workspace/_archive_test/ (หรือ {path}/01_Original_Backup/test_slices/)
      • เพื่อให้โฟลเดอร์ทำงานสะอาดเรียบร้อย และป้องกันไม่ให้ TStudio/TRun ดึงไฟล์เทสไปแปลปนกับงานจริง

  4.4 การส่งต่องาน, พิธีสารแปลสกิล & การตรวจสอบ (Handoff, Skill Localization & Validation):
      • แจ้งให้ฉันนำไฟล์ translate_TH.csv ไปใช้กับ TRun หรือ TStudio เพื่อแปลชุดใหญ่
      • ยึดถือกฎเหล็กการอ่านครบทุกประโยค 100% (ห้ามทำข้ามๆ ห้ามข้ามบรรทัด)
      • บังคับใช้พิธีสารการแปลสกิลและวลีเกม (Skill & Phrase Localization Protocol): สืบค้นบริบท Lore และคลาสอย่างละเอียด; แปลชื่อสกิลแฟนตาซีสั้นๆ เป็นวลีสั้นสละสลวย 2-6 พยางค์ (เช่น 'ดาบเพลิงพิฆาต', 'ระบำเงา', 'ศรวายุ', 'ทัณฑ์เทวา'); ใช้ทับศัพท์เมื่อเป็นคำเฉพาะ (เช่น 'แร็กนาร็อค', 'กุงเนียร์', 'โอเวอร์ไดรฟ์'); และบล็อกคำแปลกลไกผิด (Checkpoint -> แยกบริบท: เช็คพอยท์ สำหรับระบบเซฟ vs ด่านตรวจ สำหรับด่านทหาร-ตำรวจ, Strike -> ฟาดฟัน ห้าม นัดหยุดงาน, Cast -> ร่าย ห้าม หล่อ)
      • เตรียม Packer script สำหรับนำ translate_TH.csv ที่แปลเสร็จแล้ว Pack กลับเข้าเกมตาม file_path ดั้งเดิม
      • เขียน Validator Script เพื่อตรวจสอบเทียบ translate_TH.csv กับ en_original.csv ว่าไม่มีแท็กโค้ด (%s, {{0}}, <color=...>) หรือบรรทัดใดตกหล่น

────────────────────────────────────────────────────
ขั้นตอนที่ 5 — การแพ็คไฟล์แจกจ่าย (06_Releases), คู่มือติดตั้ง & บันทึกคัมภีร์ลง Modding-Knowledge
────────────────────────────────────────────────────
เมื่อทดสอบเล่นเกมจริงผ่าน และได้รับการอนุมัติว่างานแปลสมบูรณ์:

5.1 บันทึกคัมภีร์ลงคลังความรู้ (Game Localization Bible):
{bible_spec}

5.2 จัดโครงสร้างโฟลเดอร์ 06_Releases ให้ผู้เล่น Copy ทับตัวเกมได้ทันที:
    • จัดเตรียมโฟลเดอร์: {path}/06_Releases/{name}_ThaiMod_v1.0/
    • วางโครงสร้างโฟลเดอร์ให้ตรงกับรูทของตัวเกมเป๊ะๆ เพื่อให้ผู้เล่นเพียงแค่ Copy โฟลเดอร์ไปวางทับใน Game Directory ก็เล่นได้เลย
      (รวมไฟล์แปลภาษา, ฟอนต์, รวมถึงตัวปลดล็อค mod เช่น SigBypass, dsound.dll, BepInEx หากเกมนั้นต้องใช้)

5.3 สร้างคู่มือติดตั้งภาษาไทย (คู่มือติดตั้ง_README.txt):
    • นับจำนวนบรรทัด/ประโยคทั้งหมดที่แปลจาก CSV ใน Workspace
    • เขียนไฟล์ {path}/06_Releases/{name}_ThaiMod_v1.0/คู่มือติดตั้ง_README.txt (และ README_TH.txt) ตามเทมเพลตมาตรฐานดังนี้:

=============================================================
      Mod ภาษาไทย สำหรับเกม {name} (v1.0) NodNuatTranslator
=============================================================

รายละเอียดการแปล:
-------------------------------------------------------------
แปลภาษาไทยครบถ้วนสมบูรณ์ ทั้งหมด [ระบุจำนวน] ประโยค/บรรทัด

วิธีติดตั้ง (Installation):
-------------------------------------------------------------
1. แตกไฟล์ Zip ที่ดาวน์โหลดมา
2. คุณจะเห็นโฟลเดอร์สำหรับติดตั้ง
3. ให้นำโฟลเดอร์หรือไฟล์ทั้งหมดนี้ ไปวางทับในโฟลเดอร์เกม {name} ของคุณ
   (ตัวอย่างพาทของเกม: {game_dir})
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
    • บีบอัดโฟลเดอร์เป็น: {path}/06_Releases/{safe_name}_ThaiMod_v1.0.zip
    • ตรวจสอบว่าในไฟล์ .zip มีโฟลเดอร์เกมที่พร้อมวางทับ และมี "คู่มือติดตั้ง_README.txt" เรียบร้อยแล้ว

5.5 สื่อประชาสัมพันธ์ & โลโก้เกมภาษาไทย (07_Image_Resources):
    • ตรวจสอบและดึงภาพหน้าปกทางการจาก Steam CDN ให้ครบทุกขนาดใน {path}/07_Image_Resources/Official_Art/ (Capsule 16:9, โปสเตอร์แนวตั้ง 600x900, Hero Banner 1920x620, และ โลโก้แท้พื้นหลังใส logo.png)
    • ออกแบบไอเดียชื่อเกมภาษาไทย พร้อมสร้าง/อัปเดตไฟล์ {path}/07_Image_Resources/Generated_Logo/AI_Logo_Prompt.md บรรจุชุดคำสั่ง Prompt คุณภาพสูง (Midjourney v6.1 / FLUX.1 / SDXL / DALL-E) สำหรับเจนตัวอักษรโลโก้ไทย 3D แบบพื้นหลังดำสนิท (Isolated on black background) สำหรับไดคัทลง PSD
    • แนะนำขั้นตอนการนำภาพ Official Art และภาพโลโก้ที่เจนแล้ว ไปประกอบลงในไฟล์ PSD เทมเพลตใน {path}/07_Image_Resources/ (เช่น Cover_Post facebook.psd, Header_facebook.psd, cover 16-9.psd) และเซฟไฟล์ภาพสุดท้ายไว้ที่ 07_Image_Resources/Final_Exports/ เพื่อใช้โพสต์โปรโมทลงเพจ "หน๊ด หนวด translator" """
            parts.append(core)

        # ── Font & PUA Architecture Block ──────────────────────────────────
        font_block = cls._build_font_block(selected_font, path, engine_name, is_en=is_en)
        if font_block:
            parts.append(font_block)

        # ── Protocol Blocks (Interactive Checkboxes) ───────────────────────
        if options.get("auto_tool", True):
            if is_en:
                parts.append(f"""
══════════════════════════════════════════════════════
[Protocol A] Auto Tool Discovery & Download 🔧
══════════════════════════════════════════════════════
When a tool is needed and not found in {tool_dir}:
  Step 1 — Search locally: scan {tool_dir} recursively for binaries.
  Step 2 — Auto-download: if not found, search GitHub for latest release binary,
           download to {tool_dir}, and report progress.
  Step 3 — Report failure: if download fails, stop immediately and present options [A/B/C].""")
            else:
                parts.append(f"""
══════════════════════════════════════════════════════
[โปรโตคอล A] ค้นหาและโหลดเครื่องมืออัตโนมัติ 🔧
══════════════════════════════════════════════════════
เมื่อต้องการเครื่องมือและไม่พบใน {tool_dir}:
  ขั้น 1 — ค้นหาในเครื่อง: สแกน {tool_dir} แบบ Recursive หา binary ที่ต้องการ
  ขั้น 2 — ดาวน์โหลดอัตโนมัติ: ค้นหา Release ล่าสุดบน GitHub (QuickBMS, UEViewer, AssetStudio ฯลฯ)
           ดาวน์โหลด Binary มาไว้ใน {tool_dir} แล้วรายงานความคืบหน้า
  ขั้น 3 — รายงานผู้ใช้: หากโหลดล้มเหลว ให้หยุดและถามผู้ใช้พร้อมเสนอทางเลือก [A/B/C]""")

        if options.get("sync_bible", True):
            if is_en:
                parts.append(f"""
══════════════════════════════════════════════════════
[Protocol S] Modding Knowledge Sync & Font Extraction 📖
══════════════════════════════════════════════════════
Strictly follow the 10 mandatory Bible sections. Extract installable TTF/OTF fonts to:
  {bible_info['font_assets_dir']}
Register the entry in MASTER_INDEX.md and ENGINE_INDEX.md upon milestone completion.""")
            else:
                parts.append(f"""
══════════════════════════════════════════════════════
[โปรโตคอล S] ซิงค์คัมภีร์ & สกัดฟอนต์ลงคลังความรู้ 📖
══════════════════════════════════════════════════════
ปฏิบัติตามมาตรฐานคัมภีร์ 10 หมวดหมู่อย่างเคร่งครัด สกัดไฟล์ฟอนต์จริง (TTF/OTF) ลงใน:
  {bible_info['font_assets_dir']}
พร้อมบันทึกลงสารบัญ MASTER_INDEX.md และ ENGINE_INDEX.md ทันทีที่งานเสร็จสมบูรณ์""")

        if options.get("obstacle", True):
            if is_en:
                parts.append("""
══════════════════════════════════════════════════════
[Protocol B] Obstacle & Limitation Handling 🚧
══════════════════════════════════════════════════════
When encountering any limitation (unknown format, missing tools, encoding issues, tool failure):
  1. Never stop silently or loop without reporting.
  2. If technical roadblock: Activate [Protocol X] Extreme Breakthrough immediately — search deep sources and forge custom specialized tools to overcome it.
  3. If severe non-technical risk (anti-cheat ban, data wipe, DRM lock): Diagnose root cause, report with ranked options: [A - Recommended], [B - Slower], [C - Pivot], and wait for user alignment.""")
            else:
                parts.append("""
══════════════════════════════════════════════════════
[โปรโตคอล B] การจัดการข้อจำกัดและอุปสรรค 🚧
══════════════════════════════════════════════════════
เมื่อเจอข้อจำกัดใดๆ (Format ไม่รู้จัก, ไม่มีเครื่องมือ, ฟอนต์เพี้ยน, เครื่องมือล้มเหลว):
  1. ห้ามหยุดเงียบหรือวนซ้ำโดยไม่รายงาน
  2. หากเป็นอุปสรรคทางเทคนิค: เปิดใช้งาน [โปรโตคอล X] ฝ่าทางตันขั้นสูงสุดทันที — ค้นหาข้อมูลเชิงลึกและสร้างเครื่องมือเฉพาะกิจขึ้นมาแก้ไขด้วยตนเองจนสำเร็จ
  3. หากพบความเสี่ยงสูงระดับวิกฤต (Anti-Cheat บล็อก, เสี่ยงต่อไฟล์ระบบ/เซฟ): วินิจฉัยสาเหตุ รายงานพร้อมตัวเลือกจัดอันดับ [A — แนะนำ], [B — ช้ากว่า], [C — เปลี่ยนเป้า] และรอการตัดสินใจจากผู้ใช้""")

        if options.get("extreme_breakthrough", True):
            if is_en:
                parts.append(f"""
══════════════════════════════════════════════════════
[Protocol X] Extreme Breakthrough & Custom Tool Synthesizer 🛠️🔥
══════════════════════════════════════════════════════
MANDATE: IF YOU ENCOUNTER A ROADBLOCK OR CANNOT ACCOMPLISH A TASK THROUGH CONVENTIONAL MEANS, YOU MUST NEVER SURRENDER OR SAY "IT IS IMPOSSIBLE". USE THE HIGHEST LEVEL OF REVERSE ENGINEERING TO RESEARCH AND FORGE SPECIALIZED TOOLS TO SUCCEED:

1. ABSOLUTE DETERMINATION (NEVER GIVE UP):
   • Never declare a game "unsupported" or halt helplessly.
   • When standard tools (QuickBMS, AssetStudio, UModel, UnrealPak, etc.) fail or do not exist, transition immediately into Custom Reverse Engineering Mode.

2. EXHAUSTIVE DEEP RESEARCH (360° RECONNAISSANCE):
   • Search web, GitHub, XeNTaX / ZenHax archives, QuickBMS script repositories, Steam guides, NexusMods, and Modding-Knowledge.
   • Conduct Binary Forensics:
     - Inspect the first 64 bytes of the target file for magic numbers, header structures, offsets, and chunk tables.
     - Identify compression signatures: Zlib (78 9C / 78 DA), Oodle (Kraken, Mermaid, Selkie), LZ4, Zstandard (28 B5 2F FD), Deflate, LZMA.
     - Search binary strings in game executables / DLLs (GameAssembly.dll, engine binaries) for function names, serialization structs, encryption keys, or salt hashes.

3. CUSTOM TOOL FORGE (ENGINEER DEDICATED TOOLS):
   • Do not wait for existing tools. Directly synthesize custom standalone Python, C#, or C++ utilities inside:
     `{path}/05_Scripts_and_Tools/` or `tools/flagship/GameBridges/`
     - Custom Binary Parser & Repacker: Write precise binary handlers using Python struct, ctypes, or io.BytesIO that read chunk headers, unpack payloads, allow text editing, and repack with correct alignments and updated header offsets/lengths.
     - Custom Transcoder / Decryptor: Implement decryption or decompression routines for proprietary formats.
     - Font Surgery & Atlas Generator: If native font replacement fails, generate a custom TrueType PUA font, elevate tone marks (+160 units), or patch font textures directly into asset containers.
     - Runtime Memory Hook Fallback: If disk files are locked by DRM or integrity verification, deploy a runtime injection / memory hook (e.g., MinHook proxy DLL like dxgi.dll, version.dll, dinput8.dll, or BepInEx/MelonLoader for Unity) to intercept text rendering and swap strings dynamically.

4. RELENTLESS ITERATIVE VALIDATION:
   • Create a micro-test harness: Test on 1–2 strings or a single asset chunk before processing full files.
   • Perform Roundtrip Validation: Extract → Repack unmodified → Binary Diff against original. If identical or functionally valid, proceed to inject {target_lang} text.
   • Read error logs and exceptions, diagnose stack traces, adjust alignment/offsets, and iterate relentlessly until the Proof of Concept succeeds!

5. KNOWLEDGE CODIFICATION:
   • Document the newly discovered format, algorithms, and synthesized tool in Modding-Knowledge immediately so that future projects inherit this capability.""")
            else:
                parts.append(f"""
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
     `{path}/05_Scripts_and_Tools/` หรือ `tools/flagship/GameBridges/`
     - Custom Binary Parser & Repacker: เขียนสคริปต์ Binary โดยใช้ struct, ctypes, หรือ io.BytesIO เพื่อแกะ Header, คลาย Payload, ดึงข้อความออกมาเป็น CSV/JSON และแพ็คกลับพร้อมคำนวณ Offset/Size/Checksum ใหม่ให้ถูกต้องสมบูรณ์
     - Custom Decryptor/Decompressor: เขียนอัลกอริทึมถอดรหัสหรือคลายการบีบอัดเฉพาะของเกมนั้นๆ
     - Font Surgery & Atlas Generator: หากฟอนต์แทนที่ไม่ได้ ให้ผ่าตัด Asset หรือสร้างฟอนต์ PUA เฉพาะกิจ ยกวรรณยุกต์ลอย +160 units
     - Runtime Memory Hook Fallback: หากไฟล์ในดิสก์ถูกล็อกด้วย DRM หรือระบบตรวจ Integrity Check ให้เปลี่ยนไปใช้เทคนิค Hook Memory (เช่น MinHook, DLL Proxy dxgi.dll/version.dll/dinput8.dll, หรือ BepInEx สำหรับ Unity) เพื่อดักจับและเปลี่ยนข้อความ/ฟอนต์ในหน่วยความจำขณะเกมทำงาน

4. การทดสอบและปรับจูนวนซ้ำจนกว่าจะสำเร็จ (Relentless Iterative Validation):
   • สร้างชุดทดสอบขนาดเล็ก (Micro-test): ทดลองกับข้อความ 1-2 บรรทัด หรือไฟล์ตัวอย่าง 1 ชิ้นก่อนเสมอ
   • ตรวจสอบความสมบูรณ์แบบ Roundtrip: สกัดไฟล์ → แพ็คกลับโดยไม่แก้ข้อความ → Binary Diff เทียบกับต้นฉบับ หากตรงกันหรือเกมเปิดได้ปกติ จึงเริ่มใส่ภาษา{target_lang}
   • หากเกิด Exception หรือเกมแครช ให้อ่าน Error log วิเคราะห์ Stack Trace ปรับ Offset, Padding, Alignment แล้วรันซ้ำจนกว่าจะสำเร็จ 100%!

5. บันทึกองค์ความรู้ถาวร (Knowledge Codification):
   • เมื่อพิชิตอุปสรรคได้แล้ว ให้บันทึกโครงสร้างไฟล์และโค้ดของเครื่องมือเฉพาะกิจลงใน Modding-Knowledge ทันที เพื่อเป็นคัมภีร์ถาวรสำหรับโปรเจกต์ต่อๆ ไป""")

        if options.get("write_log", True):
            if is_en:
                parts.append(f"""
══════════════════════════════════════════════════════
[Protocol C] Session Log 📋
══════════════════════════════════════════════════════
Log every major step to:
  {path}/05_Scripts_and_Tools/session_log.md
Format:
  ## [Timestamp] Step X — [Name]
  - Action taken: ...
  - Result: Success / Failed
  - Files involved: ...""")
            else:
                parts.append(f"""
══════════════════════════════════════════════════════
[โปรโตคอล C] บันทึก Log การทำงาน 📋
══════════════════════════════════════════════════════
บันทึก Log ทุกขั้นตอนสำคัญลงใน:
  {path}/05_Scripts_and_Tools/session_log.md
รูปแบบ:
  ## [วันที่/เวลา] ขั้นตอนที่ X — [ชื่อขั้นตอน]
  - สิ่งที่ทำ: ...
  - ผลลัพธ์: สำเร็จ / ล้มเหลว
  - ไฟล์ที่เกี่ยวข้อง: ...""")

        if options.get("min_confirm", False):
            if is_en:
                parts.append("""
══════════════════════════════════════════════════════
[Protocol D] Confirm Before Destructive Actions ✅
══════════════════════════════════════════════════════
Ask for confirmation only before:
  • Overwriting files in 01_Original_Backup
  • Directly modifying files in Game Directory
  • Installing or modifying system-level dependencies
For all other steps, proceed autonomously.""")
            else:
                parts.append("""
══════════════════════════════════════════════════════
[โปรโตคอล D] การยืนยันก่อนทำ Destructive Action ✅
══════════════════════════════════════════════════════
ขอการยืนยันจากผู้ใช้เฉพาะก่อนทำสิ่งเหล่านี้:
  • เขียนทับไฟล์ใน 01_Original_Backup
  • แก้ไขไฟล์ใน Game Directory โดยตรง
  • ติดตั้ง/แก้ไข Dependency ของระบบ
สำหรับขั้นตอนอื่นๆ ดำเนินการต่อได้เลย""")

        if options.get("deep_scan", False):
            if is_en:
                parts.append("""
══════════════════════════════════════════════════════
[Protocol E] Deep Scan Mode 🔬
══════════════════════════════════════════════════════
Full scan — skip nothing:
  • Inspect byte headers of files with non-standard extensions.
  • Use entropy analysis to detect potentially encrypted assets.
  • Report the format of every unrecognized file.""")
            else:
                parts.append("""
══════════════════════════════════════════════════════
[โปรโตคอล E] Deep Scan Mode 🔬
══════════════════════════════════════════════════════
สแกนแบบเต็มรูปแบบ — ไม่ข้ามไฟล์ที่ไม่รู้จัก:
  • ตรวจทุก Byte Header ของไฟล์ที่ไม่มีนามสกุลมาตรฐาน
  • ใช้ Entropy Analysis เพื่อตรวจหาไฟล์ที่อาจถูกเข้ารหัส
  • รายงาน Format ของทุกไฟล์ที่ไม่รู้จัก""")

        if options.get("mem_hook", False):
            if is_en:
                parts.append("""
══════════════════════════════════════════════════════
[Protocol F] Memory Hook Fallback 🧩
══════════════════════════════════════════════════════
Allowed to use memory hooks as a last resort:
  • BepInEx (Unity) — Patch at runtime without touching game files.
  • UnrealModLoader / UE4SS — Unreal Engine.
  • REFramework — RE Engine (Capcom).
Use only when direct archive extraction/modification is impossible.""")
            else:
                parts.append("""
══════════════════════════════════════════════════════
[โปรโตคอล F] Memory Hook Fallback 🧩
══════════════════════════════════════════════════════
อนุญาตให้ใช้ Memory Hook เป็นแผนสำรอง:
  • BepInEx (Unity) — Patch Runtime โดยไม่แตะไฟล์เกม
  • UnrealModLoader / UE4SS — Unreal Engine
  • REFramework — RE Engine (Capcom)
ใช้เฉพาะเมื่อการแตก/แก้ Archive โดยตรงทำไม่ได้""")

        if options.get("unity_mcp_font", True) and "unity" in (engine_name or "").lower():
            mcp_server_script = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "tools", "flagship", "GameBridges", "Unity", "mcp", "unity_font_mcp_server.py")
            ).replace("\\", "/")
            if is_en:
                parts.append(f"""
══════════════════════════════════════════════════════
[Protocol U] Unity Native Thai Font MCP Server 🎮
══════════════════════════════════════════════════════
A specialized Model Context Protocol (MCP) server for Unity Native Thai Font is configured:
  Server Name : unity-native-font
  Server Path : {mcp_server_script}

Available MCP Tools (Invoke directly or via python script):
  1. `scan_unity_font_references(asset_path)`
     → Scans game asset (.assets/level*) to find existing TMP FontAsset (TypeId 114), Material (TypeId 21), and Atlas Texture2D (TypeId 28) with their PathIDs.
  2. `build_thai_subset(csv_path)`
     → Extracts minimal unique character subset (ASCII + Thai PUA) from translated CSV for compact 1-atlas font creation.
  3. `tune_thai_tone_marks(input_font_path, output_font_path, raise_units=160)`
     → Automatically shifts Thai tone marks (uni0E48-uni0E4B) vertically by +160 units in PUA composite glyphs to prevent clipping.
  4. `transplant_native_font(target_asset_path, output_asset_path, font_bundle_path, target_font_pathid, target_material_pathid, target_atlas_pathid)`
     → Safely transplants the TMP FontAsset and texture atlas into target asset using AssetsTools.NET without allocator crashes.
  5. `verify_native_font(original_asset_path, packed_asset_path)`
     → Performs independent read-back inspection to verify font integrity and PUA glyph rendering.

GOAL: Build and transplant a native Thai TextMeshPro font into the game's serialized assets with ZERO memory corruption or allocator overflow.""")
            else:
                parts.append(f"""
══════════════════════════════════════════════════════
[โปรโตคอล U] Unity Native Thai Font MCP Server 🎮
══════════════════════════════════════════════════════
ระบบได้ติดตั้งและเชื่อมต่อ Model Context Protocol (MCP) Server สำหรับทำฟอนต์ Unity ภาษาไทยแบบ Native ไว้แล้ว:
  ชื่อ Server  : unity-native-font
  ตำแหน่งสคริปต์: {mcp_server_script}

เครื่องมือ MCP ที่พร้อมใช้งาน (เรียกใช้ผ่าน MCP หรือรันผ่าน Python Bridge):
  1. `scan_unity_font_references(asset_path)`
     → สแกนไฟล์ asset (.assets/level*) เพื่อหา PathID ของ TextMeshPro FontAsset (TypeId 114), Material (TypeId 21), และ Atlas Texture2D (TypeId 28)
  2. `build_thai_subset(csv_path)`
     → สกัดชุดอักขระเฉพาะที่จำเป็นจาก CSV (ASCII + Thai PUA) เพื่อสร้าง Font Atlas ขนาดกะทัดรัดแผ่นเดียว ไม่เปลืองหน่วยความจำ
  3. `tune_thai_tone_marks(input_font_path, output_font_path, raise_units=160)`
     → ยกวรรณยุกต์ไทย (ไม้เอก-จัตวา) ขึ้น +160 units ใน TrueType glyf composite table ป้องกันสระลอยและข้อความทับซ้อน
  4. `transplant_native_font(target_asset_path, output_asset_path, font_bundle_path, target_font_pathid, target_material_pathid, target_atlas_pathid)`
     → ฝัง FontAsset และ Texture2D ลงไฟล์ .assets ของเกมผ่าน AssetsTools.NET อย่างปลอดภัย ไม่ทำให้เกิดบั๊ก Size overflow in allocator
  5. `verify_native_font(original_asset_path, packed_asset_path)`
     → ตรวจสอบความถูกต้องของ Asset หลังแพ็ก ยืนยันการอ่านออกและเรนเดอร์อักขระ PUA ได้จริง

เป้าหมาย: ใช้เครื่องมือ MCP เหล่านี้ในการสร้างและฝังฟอนต์ไทย Native ลงในไฟล์ Asset ของเกมให้สำเร็จ 100%""")

        is_ue3 = any(k in (engine_name or "").lower() for k in ["unreal engine 3", "ue3", "udk"])
        if options.get("udk_mcp_bridge", True) and is_ue3:
            udk_mcp_script = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "tools", "flagship", "GameBridges", "UnrealEngine3", "mcp", "udk_mcp_server.py")
            ).replace("\\", "/")
            if is_en:
                parts.append(f"""
══════════════════════════════════════════════════════
[Protocol K] UDK 2011-09 MCP Bridge (Unreal Engine 3) 🎮
══════════════════════════════════════════════════════
A specialized Model Context Protocol (MCP) server for Unreal Engine 3 / UDK (September 2011 build) is configured:
  Server Name : udk-mcp-editor
  Server Path : {udk_mcp_script}

Available MCP Tools:
  1. `udk_status()`
     → Checks UDK installation (auto-detects Binaries/Win64/UDK.exe), engine version, running processes, and active editor windows.
  2. `udk_inspect_package(package_path)`
     → Reads 64-byte package header, extracts FileVersion and LicenseeVersion, and verifies whether the package is stock UDK compatible (LicenseeVersion == 0) or game-specific (e.g. Dishonored LicenseeVersion == 30).
  3. `udk_package_info(package_path)`
     → Runs UDK PkgInfo commandlet in an isolated process to dump object tables and font assets.
        ⚠️ Preflight Check: Strictly verifies stock compatibility first. Will reject cooked custom-licensee packages.
  4. `udk_list_commandlets()` / `udk_commandlet_help(commandlet_name)`
     → Lists available commandlets and views usage documentation safely without hanging the editor.
  5. `udk_window_info(target="editor"|"browser"|"new"|"save")`
     → Queries window coordinates, title, and handles for UDK Editor or dialogs.
  6. `udk_window_screenshot(target="editor"|"browser"|"new"|"save")`
     → Captures DPI-aware client-coordinate screenshots of UDK Editor or dialog windows for visual verification.
  7. `udk_window_click(target, x, y)`
     → Simulates mouse click with occlusion check and window focus validation.
  8. `udk_window_key(target, key_name)` / `udk_window_type_text(target, text)`
     → Sends keystrokes and Unicode text without polluting clipboard.

⚠️ CRITICAL UE3 RULES & SAFEGUARDS:
  • Stock UDK vs Cooked Game Packages:
    Dishonored cooked packages (.upk) have LicenseeVersion == 30, whereas stock UDK expects LicenseeVersion == 0.
    NEVER attempt or claim to open cooked Dishonored UPK files directly in stock UDK Editor or PkgInfo!
    Use dedicated reverse-engineering scripts (e.g. Decompress.exe, UPK unpackers, custom byte patchers) for cooked files.
    Use UDK 2011-09 specifically for authoring clean font assets, MultiFont textures, or testing stock packages.
  • Safe Automation:
    Window actions require verification of active UDK processes and fail-safe occlusion checks before sending clicks.
  • Commandlet Isolation:
    All commandlets run in separate isolated processes with strict timeouts to prevent freezing the UI or system.""")
            else:
                parts.append(f"""
══════════════════════════════════════════════════════
[โปรโตคอล K] UDK 2011-09 MCP Bridge (Unreal Engine 3) 🎮
══════════════════════════════════════════════════════
ระบบได้ติดตั้งและเชื่อมต่อ Model Context Protocol (MCP) Server สำหรับ Unreal Engine 3 / UDK (กันยายน 2011) ไว้แล้ว:
  ชื่อ Server  : udk-mcp-editor
  ตำแหน่งสคริปต์: {udk_mcp_script}

เครื่องมือ MCP ที่พร้อมใช้งาน (เรียกใช้ผ่าน MCP หรือรันผ่าน Python Bridge):
  1. `udk_status()`
     → ตรวจสอบตำแหน่งติดตั้ง UDK (สแกนหา Binaries/Win64/UDK.exe อัตโนมัติ), เช็คเวอร์ชัน, โพรเซส และหน้าต่าง Editor ที่กำลังเปิดอยู่
  2. `udk_inspect_package(package_path)`
     → อ่าน Header ขนาด 64 ไบต์ ตรวจสอบ FileVersion และ LicenseeVersion เพื่อเช็คว่าเป็นแพ็กเกจ Stock UDK (LicenseeVersion == 0) หรือแพ็กเกจเกมเฉพาะ (เช่น Dishonored LicenseeVersion == 30)
  3. `udk_package_info(package_path)`
     → รันคำสั่ง UDK PkgInfo ในโพรเซสแยก เพื่อดูตาราง Object, Font, และ Texture
        ⚠️ มีระบบ Preflight Check: ตรวจสอบความเข้ากันได้ก่อนเสมอ และจะปฏิเสธการรันหากเป็นแพ็กเกจ Cooked Licensee ต่างเกม
  4. `udk_list_commandlets()` / `udk_commandlet_help(commandlet_name)`
     → ค้นหาและดูคู่มือ Commandlet ของ UDK อย่างปลอดภัยโดยไม่ทำให้โปรแกรมค้าง
  5. `udk_window_info(target="editor"|"browser"|"new"|"save")`
     → ตรวจสอบพิกัด, ชื่อหน้าต่าง, และ Handle ของ UDK Editor หรือหน้าต่างลูก
  6. `udk_window_screenshot(target="editor"|"browser"|"new"|"save")`
     → ถ่ายภาพหน้าจอของ UDK Editor ตามพิกัด Client แบบคำนวณ DPI เพื่อยืนยันการทำงานด้วยสายตา
  7. `udk_window_click(target, x, y)`
     → คลิกปุ่มหรือเมนูใน UDK พร้อมระบบป้องกันการคลิกผิด (ตรวจสอบการบังของหน้าต่างอื่น)
  8. `udk_window_key(target, key_name)` / `udk_window_type_text(target, text)`
     → ส่งปุ่มกดและพิมพ์ข้อความภาษาไทย/อังกฤษลง UDK โดยตรงโดยไม่กวน Clipboard ของผู้ใช้

⚠️ กฎเหล็กและความปลอดภัยสำหรับ Unreal Engine 3:
  • Stock UDK กับไฟล์ Cooked ของเกม Dishonored:
    แพ็กเกจ Cooked ของเกม Dishonored มี LicenseeVersion = 30 ขณะที่ Stock UDK รองรับเฉพาะ LicenseeVersion = 0
    ห้ามเคลมหรือสั่งให้ Stock UDK Editor / PkgInfo พยายามเปิดหรือแพ็กไฟล์ Cooked ของ Dishonored โดยตรงเด็ดขาด!
    สำหรับไฟล์ของ Dishonored ให้ใช้เครื่องมือ Reverse Engineering เฉพาะทาง (เช่น Decompress.exe, UPK unpacker, หรือสคริปต์ไบต์แพตช์)
    Stock UDK มีไว้เพื่อสร้างชุดฟอนต์ใหม่ (MultiFont / Canvas Font / Texture2D) หรือตรวจสอบแพ็กเกจ Stock เท่านั้น
  • การควบคุมหน้าต่างอย่างปลอดภัย:
    คำสั่งควบคุมหน้าต่างต้องตรวจสอบโพรเซส UDK ก่อนเสมอ และจะยกเลิกทันทีหากหน้าต่างถูกย่อหรือถูกบัง
  • การรัน Commandlet แบบแยกโพรเซส:
    Commandlet ทุกตัวจะรันในโพรเซสแยกที่มีระบบ Timeout เพื่อป้องกันการค้างของระบบ""")

        if options.get("auto_poc", True):
            if is_en:
                parts.append(f"""
══════════════════════════════════════════════════════
[Protocol P] Autonomous POC Fast-Track Protocol ⚡
══════════════════════════════════════════════════════
Eliminate manual babysitting for Steps 1–3:
  1. Confidence Evaluation Matrix:
     • High Confidence (>= 80%):
       - Engine is recognized ({engine_name}, Scanner Confidence: {scanner_confidence}%)
       - Documented in Modding-Knowledge or standard format (.locres, .json, .csv, Unity assets, etc.)
       - Ready-to-use bridge tools or MCP available
       - No blocking anti-cheat
       → ACTION: Autonomously execute Step 1 (Analysis) → Step 2 (Bridge scripts) → Step 3 (Backup, Font prep, Main Menu patch) continuously without asking for confirmation!
     • Low Confidence (< 80%):
       - Unrecognized proprietary archive or unknown compression/encryption
       - High risk of game crash or save corruption
       → ACTION: Stop at Step 1, report findings, and ask for user alignment.
  2. Safety Guarantees:
     • ALWAYS copy original target files to 01_Original_Backup/ (marked read-only) before modifying game files.
     • ALWAYS record actions and file paths in 05_Scripts_and_Tools/session_log.md.
     • Perform read-back check to ensure the patched file is non-corrupt before declaring POC ready.
  3. The Handoff:
     • The user's primary responsibility in early modding is simply launching the game to confirm {target_lang} text displays properly.
     • Pause ONLY at Step 3 POC Gate and clearly instruct the user what to verify in-game.""")
            else:
                parts.append(f"""
══════════════════════════════════════════════════════
[โปรโตคอล P] Autonomous POC Fast-Track (ปฏิบัติการอัตโนมัติ ขั้นตอน 1–3) ⚡
══════════════════════════════════════════════════════
ลดภาระของผู้ใช้ในการคอยกดยืนยันทีละสเต็ปในขั้นตอนที่ 1 ถึง 3:
  1. เมทริกซ์การประเมินความมั่นใจ (Confidence Evaluation Matrix):
     • มั่นใจสูง (High Confidence >= 80%):
       - ตรวจพบ Engine ชัดเจน ({engine_name}, Scanner Confidence: {scanner_confidence}%)
       - มีคู่มือ/คัมภีร์ใน Modding-Knowledge หรือไฟล์เป็นมาตรฐาน (.locres, .json, .csv, Unity MonoBehaviours ฯลฯ)
       - มีเครื่องมือแกะหรือ MCP Server พร้อมใช้งาน
       - ไม่มี Anti-Cheat ที่ขัดขวางการแก้ไฟล์
       → ปฏิบัติการ: ลุยขั้นตอนที่ 1 (วิเคราะห์) → ขั้นตอนที่ 2 (เขียน Bridge) → ขั้นตอนที่ 3 (สำรองไฟล์, จูนฟอนต์, แพตช์ Main Menu ภาษา{target_lang}เข้าเกม) รวดเดียวโดยไม่ต้องหยุดถาม!
     • มั่นใจต่ำ (Low Confidence < 80%):
       - รูปแบบไฟล์ไม่คุ้นเคย หรือมีการเข้ารหัส/บีบอัดที่ไม่ทราบอัลกอริทึม
       - มีความเสี่ยงต่อไฟล์ระบบหรือเซฟเกม
       → ปฏิบัติการ: หยุดรายงานผลที่ขั้นตอนที่ 1 และสอบถามผู้ใช้ก่อนเขียนโค้ด
  2. กฎความปลอดภัยระหว่างรันอัตโนมัติ:
     • ต้องคัดลอกไฟล์ต้นฉบับไปยัง 01_Original_Backup/ (และตั้งค่าเป็น Read-only) ก่อนแตะไฟล์เกมจริงเสมอ
     • บันทึกการกระทำทุกขั้นตอนลงใน {path}/05_Scripts_and_Tools/session_log.md
     • ทำ Read-back Verification ตรวจสอบความถูกต้องของไฟล์ที่แพตช์ก่อนประกาศว่า POC พร้อม
  3. การส่งมอบงาน (POC Gate Handoff):
     • ผู้ใช้มีหน้าที่หลักเพียงแค่เปิดเกมเพื่อดูว่าภาษา{target_lang}แสดงผลได้จริง
     • หยุดรอผู้ใช้เฉพาะที่จุด "ขั้นตอนที่ 3 (Proof of Concept Gate)" เท่านั้น พร้อมแจ้งข้อแนะนำการตรวจเช็คในเกม""")

        # Closing
        if is_en:
            if options.get("auto_poc", True):
                parts.append(f"""
══════════════════════════════════════════════════════
Begin Work (Autonomous POC Fast-Track Mode ⚡)
══════════════════════════════════════════════════════
Confirm your understanding of the ecosystem, safety rules, Fast-Track protocol, and Extreme Breakthrough protocol.
Then immediately begin Step 1:
Scan {game_dir}, identify the Engine, and check the Knowledge Base.
• If Confidence is High (>= 80%): Proceed autonomously through Step 1 → Step 2 → Step 3 (backup + extract/translate Main Menu + tune font + patch game) in one seamless run, then invite me to launch the game and verify!
• If Confidence is Low (< 80%): Report findings at Step 1 and ask for guidance before writing code.
• If you encounter roadblocks or missing tools at any stage: NEVER SURRENDER. Activate [Protocol X] Extreme Breakthrough immediately — research deep sources and forge dedicated custom tools to accomplish the task at all costs!""")
            else:
                parts.append(f"""
══════════════════════════════════════════════════════
Begin Work
══════════════════════════════════════════════════════
Confirm your understanding of the ecosystem, constraints, and all milestones.
Then immediately begin Step 1: scan {game_dir}, identify the Engine and text format,
consult the Knowledge Base, declare your Approach, and report before writing any code.
• If you encounter roadblocks or missing tools at any stage: NEVER SURRENDER. Activate [Protocol X] Extreme Breakthrough immediately — research deep sources and forge dedicated custom tools to accomplish the task at all costs!""")
        else:
            if options.get("auto_poc", True):
                parts.append(f"""
══════════════════════════════════════════════════════
เริ่มต้นการทำงาน (โหมด Autonomous POC Fast-Track ⚡)
══════════════════════════════════════════════════════
ยืนยันความเข้าใจใน ecosystem, กฎความปลอดภัย, ระบบ Fast-Track และโปรโตคอลฝ่าทางตันขั้นสูงสุด (Extreme Breakthrough)
จากนั้นเริ่มขั้นตอนที่ 1 ทันที:
สแกน {game_dir}, ตรวจสอบ Engine และค้น Knowledge Base
• หากความมั่นใจสูง (>= 80%): ดำเนินการขั้นตอนที่ 1 → 2 → 3 (แบ็กอัป + สกัด/แปล Main Menu + จูนฟอนต์ + แพตช์เข้าเกม) ต่อเนื่องอัตโนมัติทันที แล้วจึงส่งมอบให้ฉันเปิดเกมทดสอบ!
• หากความมั่นใจต่ำ (< 80%): รายงานผลที่ขั้นตอนที่ 1 และสอบถามข้อตกลงก่อนดำเนินการต่อ
• หากติดขัดหรือทำไม่ได้ด้วยวิธีปกติ: ห้ามยอมแพ้เด็ดขาด ให้เปิดใช้งาน [โปรโตคอล X] ฝ่าทางตันขั้นสูงสุด ค้นหาข้อมูลเชิงลึกและสร้างเครื่องมือเฉพาะกิจขึ้นมาเองจนสำเร็จให้จงได้ โดยใช้เทคนิคขั้นสูงสุด!""")
            else:
                parts.append(f"""
══════════════════════════════════════════════════════
เริ่มต้นการทำงาน
══════════════════════════════════════════════════════
ยืนยันความเข้าใจใน ecosystem, ข้อจำกัด และ Milestone ทั้งหมด
จากนั้นเริ่มขั้นตอนที่ 1 ทันที: สแกน {game_dir} ระบุ Engine และ format,
ค้น Knowledge Base แล้วรายงานผล และประกาศ Approach ก่อนเขียนโค้ดใดๆ
• หากติดขัดหรือทำไม่ได้ด้วยวิธีปกติ: ห้ามยอมแพ้เด็ดขาด ให้เปิดใช้งาน [โปรโตคอล X] ฝ่าทางตันขั้นสูงสุด ค้นหาข้อมูลเชิงลึกและสร้างเครื่องมือเฉพาะกิจขึ้นมาเองจนสำเร็จให้จงได้ โดยใช้เทคนิคขั้นสูงสุด!""")

        return "\n".join(parts)

    @classmethod
    def get_bible_prompt(cls, project, mode="agent", options=None, app_lang="th", selected_font=None):
        """
        Specialized Prompt for Deep Reverse-Engineering, Font Extraction & Bible Creation.
        Executes the Rivet Engineer Advanced protocol to produce the 10-section Bible.
        """
        options = options or {}
        name = project.get("name", "Unknown Game")
        safe_name = re.sub(r'_+', '_', "".join(c if c.isalnum() or c in (" ", "_", "-") else "_" for c in name).strip().replace(" ", "_")).strip('_')
        path = project.get("path", "")
        game_dir = project.get("game_dir", "[ระบุตำแหน่งโฟลเดอร์ติดตั้งเกม]" if app_lang == "th" else "[Game directory not set]")
        tool_dir = project.get("tool_dir", "[ระบุตำแหน่งโฟลเดอร์เครื่องมือ]" if app_lang == "th" else "[Tool directory not set]")

        # Detect engine
        engine_info = EngineScanner.detect_engine(
            game_dir=project.get("game_dir", ""),
            workspace_dir=path,
            title=name,
            saved_engine=project.get("engine")
        )
        engine_name = engine_info.get("badge", "Unknown Engine")
        suggested_tools = ", ".join(engine_info.get("tools", ["repak", "FModel", "UnrealLocres", "TStudio"]))

        is_en = (app_lang != "th")
        kb = KnowledgeService.get_instance()
        guides = kb.find_guides_for_engine(engine_name, game_title=name, tech_keywords=engine_info.get("detected_exts"), max_results=4)
        matched_bible = guides[0] if guides and guides[0].get("match_type") == "game_bible" else None
        matched_ef = guides[0].get("engine_folder") if guides else None

        bible_info = cls.get_bible_info(
            engine_name, safe_name,
            matched_engine_folder=matched_ef,
            matched_bible=matched_bible,
            workspace_path=path
        )

        formatted_hints = []
        for g in guides:
            mtype = g.get("match_type")
            if is_en:
                prefix = "[⭐ Game Bible]" if mtype == "game_bible" else ("[🛠️ Tech/Format Guide]" if mtype == "tech_guide" else ("[📘 Engine Guide]" if mtype == "engine_guide" else "[🎮 Similar Engine Game]"))
            else:
                prefix = "[⭐ คัมภีร์ตรงกับเกมนี้]" if mtype == "game_bible" else ("[🛠️ คู่มือเทคนิค/ระบบไฟล์ตรงกัน]" if mtype == "tech_guide" else ("[📘 คู่มือ Engine]" if mtype == "engine_guide" else "[🎮 เกม Engine เดียวกัน]"))
            formatted_hints.append(f"  • {prefix} {g['title']} ({g['rel_path']})")
        guide_hints = "\n".join(formatted_hints) or ("  • (ค้นหาคู่มือเพิ่มเติมได้ที่ " + KNOWLEDGE_DIR + ")")

        bible_spec = cls._build_bible_specification_block(bible_info, name, engine_name, path, is_en=is_en)
        font_block = cls._build_font_block(selected_font, path, engine_name, is_en=is_en)

        parts = []
        if is_en:
            core = f"""📖 Master Prompt: Reverse Engineering & Thai Localization Bible Creation (Rivet Engineer)
========================================================================================
Mission: Deep Forensic Analysis, Font Extraction & Technical Bible Documentation
Target Game: {name} | Engine: {engine_name}

Context & Role:
You are an expert Game Mod Reverse Engineer and Technical Author operating under the
"Rivet Engineer Advanced" protocol. Your primary mission is to conduct a deep forensic
analysis of {name}, extract usable real font files (TTF/OTF), analyze text systems, and
authoritatively document the complete 10-section Thai Localization Bible.

Environment & Target Paths:
- Game Title:           {name}
- Workspace:            {path} (THub 01–07 folder architecture)
- Game Directory:       {game_dir}
- Tool Directory:       {tool_dir}
- Detected Engine:      {engine_name} (Suggested Tools: {suggested_tools})
- Local Knowledge Base: {KNOWLEDGE_DIR}
- Remote GitHub KB:     {GITHUB_KB_URL}

Relevant Knowledge Base Guides:
{guide_hints}

══════════════════════════════════════════════════════
Rivet Engineer Advanced — 5 Operational Phases:
══════════════════════════════════════════════════════

PHASE 0: PRE-FLIGHT CHECK
  1. Verify paths and tools exist. Check {KNOWLEDGE_DIR}/_Index/MASTER_INDEX.md.
  2. If an existing Bible exists for this game, inspect it. NEVER overwrite silently without acknowledging its contents.

PHASE 1: RECONNAISSANCE & ARCHITECTURE CLASSIFICATION
  1. Scan {game_dir} recursively for file extensions, archives, binaries, and configurations.
  2. Classify the mod architecture pattern into:
     • File Replacement (direct archive repacking or folder drop)
     • Runtime Injection (BepInEx for Unity, REFramework for Capcom, UE4SS for Unreal)
     • Binary Patch / Overlay
     • Hybrid Pattern (e.g. PAK fonts + IoStore text)

PHASE 2: DEEP BINARY ANALYSIS
  1. Check archive magic header bytes (first 32 bytes).
  2. If Unreal Engine: MANDATORY check for AES encryption on PAK footer. Note AES key requirement or explicitly state "No AES encryption".
  3. Compression identification: Zlib, LZ4, Oodle, or None (raw data).
  4. Container metadata inspection: parse index tables, UTOC/UCAS chunk sizes if UE5 IoStore.

PHASE 3: REAL FONT ASSET EXTRACTION (CRITICAL)
  ⭐ GOLDEN RULE: Extract real, installable TTF or OTF files, NOT raw text dumps!
  1. Locate font files: .ufont (carve TTF/OTF from header magic 00 01 00 00 or OTTO),
     .bundle (TMP_FontAsset or Unity Font object via UnityPy), or raw .ttf in plugins/.
  2. Save extracted font files into:
     {bible_info['font_assets_dir']}
  3. Verify extracted font metadata (Font family name, weight, style, designer, license).
  4. If extraction is technically impossible (e.g. SDF Atlas where vector curves are destroyed),
     create EXTRACTION_NOTE.txt in the same directory explaining why and proposing source candidates.

PHASE 4: TEXT SYSTEM & ENCODING ANALYSIS
  1. Identify container formats (.locres, .msg, .json, .csv, string tables).
  2. Check exact character encoding (UTF-8, UTF-8 BOM, UTF-16 LE, CP874).
  3. Enforce strict preservation of placeholders and tags (%s, {{0}}, <color=red>, \\n, \\r).

PHASE 5: COMPOSE BIBLE & KNOWLEDGE SYNC
  Document the complete findings following the mandatory Bible specification below.

{bible_spec}"""
        else:
            core = f"""📖 Master Prompt: เจาะลึกวิศวกรรมย้อนกลับและเขียนคัมภีร์ม็อดภาษาไทย (Rivet Engineer)
========================================================================================
ภารกิจ: วิเคราะห์สถาปัตยกรรมม็อดเชิงลึก, สกัดไฟล์ฟอนต์จริง (TTF/OTF) และเขียนคัมภีร์ฉบับสมบูรณ์ 10 หมวด
เกมเป้าหมาย: {name} | Engine: {engine_name}

บริบทและบทบาทของคุณ:
คุณคือ "วิศวกรย้อนกลับระบบเกมระดับสูง (Senior Reverse Engineer & Technical Author)" 
ปฏิบัติการภายใต้โปรโตคอล "Rivet Engineer Advanced" 
ภารกิจหลักของคุณคือการสแกนและเจาะลึกระบบไฟล์ของเกม {name} อย่างละเอียด, ค้นหาและสกัดไฟล์ฟอนต์จริง (TTF/OTF),
วิเคราะห์โครงสร้างข้อความ และเขียนเอกสารคัมภีร์ม็อดภาษาไทยฉบับสมบูรณ์ 10 หมวดหมู่อย่างเป็นทางการ

สภาพแวดล้อมและพาทเป้าหมาย:
- ชื่อเกม:              {name}
- Workspace:            {path} (ใช้โครงสร้าง 01 ถึง 07 ของ THub)
- Game Directory:       {game_dir}
- Tool Directory:       {tool_dir}
- ตรวจพบ Engine:        {engine_name} (เครื่องมือแนะนำ: {suggested_tools})
- Modding Knowledge:    {KNOWLEDGE_DIR}
- GitHub Knowledge:     {GITHUB_KB_URL}

คัมภีร์และคู่มือที่ตรวจพบในคลังความรู้:
{guide_hints}

══════════════════════════════════════════════════════
ขั้นตอนปฏิบัติการ 5 ลำดับของ Rivet Engineer Advanced:
══════════════════════════════════════════════════════

ลำดับที่ 0: ตรวจสอบความพร้อมและคัมภีร์เดิม (Pre-Flight Check)
  1. ตรวจสอบพาทและเครื่องมือที่จำเป็น ค้นหาชื่อเกมใน {KNOWLEDGE_DIR}/_Index/MASTER_INDEX.md
  2. หากมีคัมภีร์เดิมอยู่แล้ว ต้องตรวจสอบเนื้อหาเดิมและอัปเกรด ห้ามเขียนทับโดยไม่แจ้งรายละเอียดเดิมเด็ดขาด

ลำดับที่ 1: ลาดตระเวนและจำแนกสถาปัตยกรรม (Reconnaissance)
  1. สแกนโครงสร้างไดเรกทอรีใน {game_dir} แบบ Recursive เพื่อดูนามสกุลไฟล์, ขนาด, Archive และ Container
  2. จำแนกรูปแบบม็อด (Mod Architecture Pattern):
     • File Replacement (แทนที่ไฟล์ใน Archive ตรงๆ)
     • Runtime Injection (BepInEx สำหรับ Unity, REFramework สำหรับ RE Engine, UE4SS สำหรับ Unreal)
     • Binary Patch / Overlay
     • Hybrid Pattern (ผสมผสาน เช่น ฟอนต์ผ่าน PAK แต่ข้อความผ่าน IoStore)

ลำดับที่ 2: เจาะลึกโครงสร้างไบนารี (Deep Binary Analysis)
  1. ตรวจ Magic Header 32 ไบต์แรกของทุกไฟล์ Archive
  2. หากเป็น Unreal Engine: บังคับตรวจการเข้ารหัส AES ที่ PAK Footer (ระบุคีย์ หรือระบุชัดเจนว่า "No AES")
  3. ระบุอัลกอริทึมการบีบอัด: Zlib, LZ4, Oodle, หรือ None (ไฟล์ดิบ)
  4. วิเคราะห์ Container Metadata: ขนาด Partition, Chunk และ Mount Point

ลำดับที่ 3: สกัดไฟล์ฟอนต์จริง (Font Asset Extraction - สำคัญมาก)
  ⭐ กฎทอง: ผู้ใช้ต้องการไฟล์ฟอนต์จริงที่นำไปติดตั้งได้ (TTF/OTF) ไม่ใช่แค่ Text Dump
  1. ค้นหาไฟล์ฟอนต์: .ufont (สแกนหา Magic 00 01 00 00 หรือ OTTO แล้ว Carve ฟอนต์ออกมา), 
     .bundle (แกะ TMP_FontAsset หรือ Unity Font Object ผ่าน UnityPy), หรือไฟล์ .ttf ในโฟลเดอร์ Plugin
  2. บันทึกไฟล์ฟอนต์ที่สกัดได้จริงลงใน:
     {bible_info['font_assets_dir']}
  3. ตรวจสอบชื่อตระกูลฟอนต์จริง (Font Family Name, น้ำหนัก, สไตล์, สัญญาอนุญาต)
  4. หากสกัดไม่ได้เนื่องจากโครงสร้างถูกทำลาย (เช่น SDF Atlas) ให้เขียน EXTRACTION_NOTE.txt อธิบายเหตุผลในโฟลเดอร์เดียวกัน

ลำดับที่ 4: วิเคราะห์ระบบข้อความและ Encoding (Text Analysis)
  1. ระบุ Format ข้อความ (.locres, .msg, .json, .csv, string tables)
  2. ตรวจสอบ Character Encoding อย่างแม่นยำ (UTF-8, UTF-8 BOM, UTF-16 LE, CP874)
  3. กำหนดกฎคงแท็กโค้ดของเกมอย่างเด็ดขาด (%s, {{0}}, <color=red>, \\n, \\r)

ลำดับที่ 5: บันทึกคัมภีร์และซิงค์คลังความรู้ทั้ง 5 แห่ง (Compose Bible & Knowledge Sync)
  เขียนเอกสารคัมภีร์ตามข้อกำหนดมาตรฐาน 10 หมวดหมู่ด้านล่างนี้อย่างเคร่งครัด:

{bible_spec}"""
        parts.append(core)

        if font_block:
            parts.append(font_block)

        # Append protocols if requested or agent mode
        if mode == "agent":
            if options.get("auto_tool", True):
                if is_en:
                    parts.append(f"""
══════════════════════════════════════════════════════
[Protocol A] Auto Tool Discovery & Download 🔧
══════════════════════════════════════════════════════
Scan {tool_dir} for binaries or download missing reverse engineering tools from GitHub.""")
                else:
                    parts.append(f"""
══════════════════════════════════════════════════════
[โปรโตคอล A] ค้นหาและโหลดเครื่องมืออัตโนมัติ 🔧
══════════════════════════════════════════════════════
สแกนหาเครื่องมือใน {tool_dir} หรือโหลดเครื่องมือวิศวกรรมย้อนกลับจาก GitHub อัตโนมัติเมื่อขาดแคลน""")

            if options.get("deep_scan", True):
                if is_en:
                    parts.append("""
══════════════════════════════════════════════════════
[Protocol E] Deep Scan & Forensic Analysis 🔬
══════════════════════════════════════════════════════
Inspect byte headers of unknown extensions and calculate entropy to detect encrypted sections.""")
                else:
                    parts.append("""
══════════════════════════════════════════════════════
[โปรโตคอล E] Deep Scan Mode (เจาะลึกไบนารี) 🔬
══════════════════════════════════════════════════════
ตรวจสอบทุก Byte Header ของไฟล์ที่ไม่รู้จัก และคำนวณ Entropy เพื่อวิเคราะห์การเข้ารหัส""")

            if options.get("write_log", True):
                if is_en:
                    parts.append(f"""
══════════════════════════════════════════════════════
[Protocol C] Session Log 📋
══════════════════════════════════════════════════════
Record every reverse-engineering step to: {path}/05_Scripts_and_Tools/session_log.md""")
                else:
                    parts.append(f"""
══════════════════════════════════════════════════════
[โปรโตคอล C] บันทึก Log การทำงาน 📋
══════════════════════════════════════════════════════
บันทึกผลการวิเคราะห์ทุกขั้นตอนลงใน: {path}/05_Scripts_and_Tools/session_log.md""")

            if is_en:
                parts.append(f"""
══════════════════════════════════════════════════════
Begin Reverse Engineering
══════════════════════════════════════════════════════
Confirm your understanding of the Rivet Engineer Advanced protocol.
Immediately begin Phase 0 & Phase 1: scan {game_dir}, inspect file signatures,
verify existing Bibles, and report your preliminary architectural findings.""")
            else:
                parts.append(f"""
══════════════════════════════════════════════════════
เริ่มต้นปฏิบัติการวิศวกรรมย้อนกลับ
══════════════════════════════════════════════════════
ยืนยันความเข้าใจในโปรโตคอล Rivet Engineer Advanced ทั้งหมด
จากนั้นเริ่มขั้นตอนที่ 0 และ 1 ทันที: สแกน {game_dir}, ตรวจสอบ Signature ของไฟล์,
เช็คความซ้ำซ้อนใน Master Index และรายงานผลการวิเคราะห์เบื้องต้นก่อนเริ่มสกัดฟอนต์""")
        else:
            # Consultant / Web Chat Closing
            if is_en:
                parts.append("""
══════════════════════════════════════════════════════
Instructions for AI Consultant:
══════════════════════════════════════════════════════
If you understand your role, reply briefly with:
"Understood! I am ready to guide you through the 5 phases of Rivet Engineer Advanced. Please provide your directory listing or sample file headers to begin Phase 1."
""")
            else:
                parts.append("""
══════════════════════════════════════════════════════
คำแนะนำสำหรับ AI ที่ปรึกษา:
══════════════════════════════════════════════════════
หากเข้าใจบทบาทของคุณแล้ว ให้ตอบกลับสั้นๆ ว่า:
"รับทราบ! ฉันพร้อมนำทางคุณผ่านขั้นตอนปฏิบัติการทั้ง 5 ลำดับของ Rivet Engineer Advanced แล้ว กรุณาส่งรายการไฟล์หรือหัวไบนารีของไฟล์เกม เพื่อเริ่มขั้นตอนที่ 1 ได้ทันทีครับ"
""")

        return "\n".join(parts)

    @classmethod
    def get_media_kit_prompt(cls, project, app_lang="th"):
        """Generates a dedicated Media & Branding Kit setup and retrofit prompt for 07_Image_Resources."""
        name = project.get("name", "Unknown Game")
        path = project.get("path", "")
        engine_name = project.get("engine", "Custom Engine")
        is_en = (app_lang != "th")

        if is_en:
            return f"""🎨 Media Kit & Branding Retrofit Protocol: 07_Image_Resources
Target Game: {name} | Engine: {engine_name}
Creator: "หน๊ด หนวด translator" (NodNuatTranslator)

══════════════════════════════════════════════════════
Context & Workspace Environment:
══════════════════════════════════════════════════════
- Game:                 {name}
- Workspace:            {path}
- Target Directory:     {path}/07_Image_Resources/
- PSD Template Depot:   E:\\Mod_Workspace\\1_Template\\07_Image_Resources\\
- Engine Architecture:  {engine_name}

══════════════════════════════════════════════════════
5-Phase Operational Mission (Safe Retrofit & Branding Kit):
══════════════════════════════════════════════════════

PHASE 1: SAFE DIRECTORY AUDIT & SETUP
  • Create {path}/07_Image_Resources/ if not already present.
  • Ensure 3 standard subdirectories exist:
    1. {path}/07_Image_Resources/Official_Art/
    2. {path}/07_Image_Resources/Generated_Logo/
    3. {path}/07_Image_Resources/Final_Exports/
  ⚠️ CRITICAL SAFETY RULE: If 07_Image_Resources already contains existing PSDs, artwork, or customized files from the user, NEVER delete or overwrite them! Preserve 100% of user data.

PHASE 2: INSTALL CENTRAL PHOTOSHOP PSD TEMPLATES
  • Inspect template depot at E:\\Mod_Workspace\\1_Template\\07_Image_Resources\\
  • Copy ONLY missing template files into {path}/07_Image_Resources/:
    - Cover_Post facebook.psd (Facebook announcement post template)
    - Header copy.psd (Header banner template)
    - Header_facebook.psd (Facebook page header template)
    - cover 16-9.psd (16:9 main cover template)

PHASE 3: HARVEST MAXIMUM RESOLUTION LOGO IN MULTIPLE SIZES (MULTI-TIER DISCOVERY)
  • Discover and harvest the largest, crispest official game logo available across 4 tiers:
    1. Tier 1 (Steam Retina 2X CDN):
       - Download `logo_2x.png` (High-DPI 2X Retina transparent PNG @ 1280px+ or 4K)
       - Download fallback `logo.png` (Standard transparent PNG)
       - Also download full official Steam capsules:
         • banner_hero_1920x620.jpg (Ultra-wide Hero Banner)
         • cover_portrait_600x900.jpg (2:3 Library Poster Capsule)
         • cover_landscape_616x353.jpg (16:9 Landscape Capsule)
         • cover_header_460x215.jpg (Standard Store Header)
    2. Tier 2 (Wikimedia Commons Vector & High-Res Master):
       - Query Wikimedia Commons MediaWiki API for `{name} logo`
       - If vector SVG exists: render at master resolution (2048px or 3840px PNG)
       - If high-res PNG/JPG exists: extract original master uncompressed asset
    3. Tier 3 (Local Game Installation & Workspace Deep Scan):
       - Scan `{path}` and `01_Original_Backup` for uncompressed splash screens, title bitmaps, and UI assets (`*splash*.bmp/png`, `*logo*.png`, `*title*.png`, `*title_atlas*.png`)
    4. Tier 4 (Resolution Comparator & Master Selection):
       - Compare pixel count (width × height) across all candidates and select the largest, sharpest image as Master Logo
  • Standardized Multi-Resolution Suite Generator:
    Resample with high-quality filter (Lanczos) and save into `{path}/07_Image_Resources/Official_Art/Logos/`:
    1. `logo_master_original.png` (Maximum original resolution, untouched crisp transparent RGBA)
    2. `logo_ultra_4k_2048px.png` (2048px width — for print, posters, and 4K ultra-wide banners)
    3. `logo_large_1280px.png` (1280px width — for 1080p hero banners and Facebook cover 16:9)
    4. `logo_medium_800px.png` (800px width — for Facebook post art and mod showcase headers)
    5. `logo_standard_512px.png` (512px width — for THub dashboard cards and store capsule art)
    6. `logo_small_256px.png` (256px width — for dialog UI, toolbars, and modal popups)
    7. `logo_icon_128px.png` (128px width — for badges, app icons, and thumbnails)
  • Preserve Source Candidates:
    Save individual discovery assets as `candidate_*.png` in `Logos/` so the modder can choose alternate variants.
  • Backward Compatibility:
    Copy `logo_large_1280px.png` (or master) to `{path}/07_Image_Resources/Official_Art/official_logo.png`
    Copy `cover_landscape_616x353.jpg` to `{path}/thub_cover.jpg` for THub UI dashboard cards.

PHASE 4: BRAINSTORM THAI TITLE CONCEPTS & AUTHOR AI_LOGO_PROMPT.MD
  • Analyze the theme, atmosphere, and lore of {name} to propose 3–5 creative Thai title concepts:
    - Transliterated modern title
    - Thematic fantasy/sci-fi translated title
    - Catchy short title
  • Author/update {path}/07_Image_Resources/Generated_Logo/AI_Logo_Prompt.md:
    Generate comprehensive prompts for Midjourney v6.1, FLUX.1, SDXL, and DALL-E 3 with the mandatory constraint:
    "heavy 3D extruded lettering, completely isolated on pure solid flat black background" for 1-click Photoshop die-cutting.

PHASE 5: 1-CLICK PHOTOSHOP COMPOSITION GUIDE
  • Guide the user to place the generated logo (black background) onto the PSD templates in {path}/07_Image_Resources/ and change layer Blending Mode to Screen, or use Select Subject to strip black background in seconds.
  • Blend with official art from {path}/07_Image_Resources/Official_Art/ as backdrops.
  • Save final graphics in {path}/07_Image_Resources/Final_Exports/ ready for public release.

══════════════════════════════════════════════════════
Automated Execution Script (Run Immediately):
══════════════════════════════════════════════════════
If you are an autonomous AI Agent (Claude Code / Antigravity), execute this Python script via terminal to complete the entire retrofit, download assets, and write the logo prompt in seconds:

```python
import os, sys, shutil, urllib.request, urllib.parse, io, json

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

game_name = "{name}"
ws_path = r"{path}"
engine_name = "{engine_name}"

img_res = os.path.join(ws_path, "07_Image_Resources")
official_art = os.path.join(img_res, "Official_Art")
logos_dir = os.path.join(official_art, "Logos")
gen_logo = os.path.join(img_res, "Generated_Logo")
final_exp = os.path.join(img_res, "Final_Exports")
for d in [official_art, logos_dir, gen_logo, final_exp]:
    os.makedirs(d, exist_ok=True)

tmpl_candidates = [
    r"templates\\07_Image_Resources",
    r"E:\\Mod_Workspace\\1_Template\\07_Image_Resources"
]
tmpl_src = next((d for d in tmpl_candidates if os.path.exists(d)), tmpl_candidates[0])
if os.path.exists(tmpl_src):
    for f in os.listdir(tmpl_src):
        src_f = os.path.join(tmpl_src, f)
        dst_f = os.path.join(img_res, f)
        if os.path.isfile(src_f) and not os.path.exists(dst_f):
            shutil.copy2(src_f, dst_f)
            print(f"Copied template: {{f}}")

# 1. Resolve Steam AppID
appid = None
query = urllib.parse.quote(game_name.strip())
url = f"https://store.steampowered.com/api/storesearch/?term={{query}}&l=english&cc=US"
req = urllib.request.Request(url, headers={{'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}})
try:
    with urllib.request.urlopen(req, timeout=8) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        if data.get("total", 0) > 0:
            appid = data["items"][0]["id"]
            print(f"🎯 Resolved Steam AppID: {{appid}} ({{data['items'][0]['name']}})")
except Exception as e:
    print(f"Steam search notice: {{e}}")

# 2. Multi-Tier Logo Discovery
has_pil = False
try:
    from PIL import Image
    has_pil = True
except ImportError:
    pass

candidates = []

# Tier 1: Steam Retina 2X & Standard CDN
if appid:
    steam_urls = [
        ("Steam 2X Retina", f"https://cdn.akamai.steamstatic.com/steam/apps/{{appid}}/logo_2x.png"),
        ("Steam 2X Fastly", f"https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/{{appid}}/logo_2x.png"),
        ("Steam Standard", f"https://cdn.akamai.steamstatic.com/steam/apps/{{appid}}/logo.png"),
    ]
    for src_label, u in steam_urls:
        try:
            r = urllib.request.Request(u, headers={{'User-Agent': 'Mozilla/5.0'}})
            with urllib.request.urlopen(r, timeout=6) as res:
                if res.status == 200:
                    content = res.read()
                    if len(content) > 1000:
                        if has_pil:
                            im = Image.open(io.BytesIO(content))
                            candidates.append((src_label, im, content, f"steam_{{im.width}}x{{im.height}}.png"))
                            print(f"✅ Found {{src_label}}: {{im.width}}x{{im.height}} ({{len(content):,}} bytes)")
                        else:
                            candidates.append((src_label, None, content, "steam_logo.png"))
                        break
        except Exception:
            pass

    capsules = [
        ("cover_landscape_616x353.jpg", f"https://cdn.akamai.steamstatic.com/steam/apps/{{appid}}/capsule_616x353.jpg"),
        ("cover_portrait_600x900.jpg", f"https://cdn.akamai.steamstatic.com/steam/apps/{{appid}}/library_600x900_2x.jpg"),
        ("banner_hero_1920x620.jpg", f"https://cdn.akamai.steamstatic.com/steam/apps/{{appid}}/library_hero.jpg"),
        ("cover_header_460x215.jpg", f"https://cdn.akamai.steamstatic.com/steam/apps/{{appid}}/header.jpg"),
    ]
    for fn, u in capsules:
        fp = os.path.join(official_art, fn)
        try:
            r = urllib.request.Request(u, headers={{'User-Agent': 'Mozilla/5.0'}})
            with urllib.request.urlopen(r, timeout=6) as res:
                if res.status == 200:
                    content = res.read()
                    if len(content) > 500:
                        with open(fp, "wb") as out:
                            out.write(content)
                        print(f"Downloaded: {{fn}} ({{len(content):,}} bytes)")
        except Exception:
            pass

    best_cover = os.path.join(official_art, "cover_landscape_616x353.jpg")
    if os.path.exists(best_cover):
        shutil.copy2(best_cover, os.path.join(ws_path, "thub_cover.jpg"))

# Tier 2: Wikimedia Commons (Vectors & High-Res PNGs)
try:
    wiki_api = "https://commons.wikimedia.org/w/api.php"
    search_params = {{"action": "query", "list": "search", "srsearch": f"{{game_name}} logo", "srnamespace": "6", "format": "json"}}
    w_req = urllib.request.Request(f"{{wiki_api}}?{{urllib.parse.urlencode(search_params)}}", headers={{'User-Agent': 'ModderHub/2.2'}})
    with urllib.request.urlopen(w_req, timeout=6) as wr:
        wdata = json.loads(wr.read().decode('utf-8'))
        search_items = wdata.get("query", {{}}).get("search", [])
        for item in search_items[:3]:
            title = item.get("title")
            info_params = {{"action": "query", "titles": title, "prop": "imageinfo", "iiprop": "url|size|mime", "iiurlwidth": "2048", "format": "json"}}
            ireq = urllib.request.Request(f"{{wiki_api}}?{{urllib.parse.urlencode(info_params)}}", headers={{'User-Agent': 'ModderHub/2.2'}})
            with urllib.request.urlopen(ireq, timeout=6) as ir:
                idata = json.loads(ir.read().decode('utf-8'))
                pages = idata.get("query", {{}}).get("pages", {{}})
                for _, pdata in pages.items():
                    for ii in pdata.get("imageinfo", []):
                        target_url = ii.get("thumburl") or ii.get("url")
                        mime = ii.get("mime", "")
                        if "png" in mime or "svg" in mime or "jpeg" in mime:
                            try:
                                dl_req = urllib.request.Request(target_url, headers={{'User-Agent': 'Mozilla/5.0'}})
                                with urllib.request.urlopen(dl_req, timeout=8) as dl_resp:
                                    content = dl_resp.read()
                                    if len(content) > 1000 and has_pil:
                                        im = Image.open(io.BytesIO(content))
                                        candidates.append((f"Wikimedia ({{title}})", im, content, f"wikimedia_{{im.width}}x{{im.height}}.png"))
                                        print(f"✅ Found Wikimedia Asset ({{title}}): {{im.width}}x{{im.height}} ({{len(content):,}} bytes)")
                            except Exception:
                                pass
except Exception as e:
    print(f"Wikimedia notice: {{e}}")

# Tier 3: Local Workspace / Backup Deep Scan
search_dirs = [ws_path]
orig_dir = os.path.join(ws_path, "01_Original_Backup")
if os.path.exists(orig_dir):
    search_dirs.append(orig_dir)

for s_dir in search_dirs:
    for root, _, files in os.walk(s_dir):
        if "07_Image_Resources" in root:
            continue
        for f in files:
            f_lower = f.lower()
            if any(k in f_lower for k in ["splash", "logo", "title"]) and f_lower.endswith((".png", ".bmp", ".jpg")):
                local_fp = os.path.join(root, f)
                try:
                    with open(local_fp, "rb") as lf:
                        content = lf.read()
                    if has_pil:
                        im = Image.open(io.BytesIO(content))
                        if im.width >= 400 and im.height >= 100:
                            candidates.append((f"Local File ({{f}})", im, content, f"local_{{im.width}}x{{im.height}}.png"))
                            print(f"✅ Found Local Asset ({{f}}): {{im.width}}x{{im.height}}")
                except Exception:
                    pass

# Tier 4: Select Master & Generate Multi-Size Pack
if candidates and has_pil:
    candidates.sort(key=lambda c: c[1].width * c[1].height, reverse=True)
    best_label, best_img, best_bytes, _ = candidates[0]
    print(f"\n👑 Selected Master Logo: {{best_label}} ({{best_img.width}}x{{best_img.height}})")

    for label, c_img, c_bytes, c_fname in candidates[:4]:
        cand_fp = os.path.join(logos_dir, f"candidate_{{c_fname}}")
        if not os.path.exists(cand_fp):
            try:
                c_img.save(cand_fp, format="PNG")
            except Exception:
                pass

    master_path = os.path.join(logos_dir, "logo_master_original.png")
    best_img.save(master_path, format="PNG")
    print(f"📁 Saved Master Logo: {{master_path}} ({{best_img.width}}x{{best_img.height}})")

    target_widths = [
        ("logo_ultra_4k_2048px.png", 2048),
        ("logo_large_1280px.png",   1280),
        ("logo_medium_800px.png",    800),
        ("logo_standard_512px.png",  512),
        ("logo_small_256px.png",     256),
        ("logo_icon_128px.png",      128),
    ]

    aspect = best_img.height / max(1, best_img.width)
    resample_filter = getattr(Image, "Resampling", Image).LANCZOS

    for fname, target_w in target_widths:
        target_h = max(1, int(target_w * aspect))
        out_fp = os.path.join(logos_dir, fname)
        resized_im = best_img.resize((target_w, target_h), resample=resample_filter)
        resized_im.save(out_fp, format="PNG")
        print(f"  ↳ Generated {{fname}}: {{target_w}}x{{target_h}}")

    compat_logo = os.path.join(official_art, "official_logo.png")
    large_logo = os.path.join(logos_dir, "logo_large_1280px.png")
    compat_src = large_logo if os.path.exists(large_logo) else master_path
    shutil.copy2(compat_src, compat_logo)
    print(f"📁 Linked official_logo.png -> {{os.path.basename(compat_src)}}")
elif candidates:
    best_label, _, best_bytes, _ = candidates[0]
    out_fp = os.path.join(official_art, "official_logo.png")
    with open(out_fp, "wb") as f:
        f.write(best_bytes)
    print(f"Saved logo: {{out_fp}}")

print("07_Image_Resources retrofit and multi-size logo harvest completed successfully!")
```

Instructions for AI:
Acknowledge receipt and run the script above to reorganize directories, harvest maximum-resolution logos in multiple sizes, write AI_Logo_Prompt.md, and brainstorm 3-5 Thai game title concepts immediately!
"""
        else:
            return f"""🎨 Media Kit & Branding Retrofit Protocol: 07_Image_Resources
เป้าหมาย: ยกระดับ, ติดตั้ง, และจัดระเบียบสื่อประชาสัมพันธ์สำหรับโปรเจกต์แปลเกม: {name}
ผู้จัดทำ: "หน๊ด หนวด translator" (NodNuatTranslator)

══════════════════════════════════════════════════════
บริบทและสภาพแวดล้อม:
══════════════════════════════════════════════════════
- ชื่อเกม:              {name}
- Workspace:            {path}
- โฟลเดอร์เป้าหมาย:     {path}/07_Image_Resources/
- คลังเทมเพลต PSD:      E:\\Mod_Workspace\\1_Template\\07_Image_Resources\\
- Engine:               {engine_name}

══════════════════════════════════════════════════════
ภารกิจ 5 ขั้นตอน (Safe Retrofit & Branding Kit):
══════════════════════════════════════════════════════

ขั้นตอนที่ 1: ตรวจสอบและจัดโครงสร้างโฟลเดอร์ (Safe Structure Audit)
  • สร้างโฟลเดอร์ {path}/07_Image_Resources/ (หากยังไม่มี)
  • สร้าง 3 โฟลเดอร์ย่อยมาตรฐาน:
    1. {path}/07_Image_Resources/Official_Art/
    2. {path}/07_Image_Resources/Generated_Logo/
    3. {path}/07_Image_Resources/Final_Exports/
  ⚠️ กฎเหล็กความปลอดภัย: หากในโฟลเดอร์ 07_Image_Resources มีไฟล์ PSD หรือรูปภาพเดิมที่ผู้ใช้เคยทำไว้ ห้ามลบหรือเขียนทับเด็ดขาด! ให้คงไฟล์เดิมไว้ 100%

ขั้นตอนที่ 2: ติดตั้ง Photoshop PSD Templates จากคลังกลาง
  • ตรวจสอบไฟล์เทมเพลตจาก E:\\Mod_Workspace\\1_Template\\07_Image_Resources\\
  • คัดลอกเฉพาะไฟล์ที่ยังไม่มีในโฟลเดอร์โปรเจกต์:
    - Cover_Post facebook.psd (สำหรับภาพโพสต์เพจ Facebook)
    - Header copy.psd (สำหรับส่วนหัวของม็อด)
    - Header_facebook.psd (สำหรับภาพปกแบนเนอร์เพจ)
    - cover 16-9.psd (สำหรับภาพหน้าปกแนวนอน 16:9)

ขั้นตอนที่ 3: สกัดและจัดหาภาพโลโก้ขนาดใหญ่ คมชัดสูงสุด ครบทุกขนาด (High-Res Multi-Size Logo Harvesting)
  • ค้นหาและดึงภาพโลโก้ทางการที่มีขนาดใหญ่และคมชัดที่สุดผ่าน 4 ลำดับชั้น (Multi-Tier Discovery):
    1. ลำดับที่ 1 (Steam Retina 2X CDN):
       - ดาวน์โหลด `logo_2x.png` (ภาพโลโก้ Retina ความละเอียด 2 เท่า กว้าง 1280px+ พื้นหลังโปร่งใส Alpha คมกริบ)
       - ดาวน์โหลด `logo.png` (ภาพโลโก้มาตรฐานสำหรับกรณีสำรอง)
       - ดาวน์โหลดภาพสื่อทางการจาก Steam Store ครบชุด:
         • banner_hero_1920x620.jpg (Ultra-wide Hero Banner คมชัดสูง)
         • cover_portrait_600x900.jpg (โปสเตอร์แนวตั้ง 2:3 Library Capsule)
         • cover_landscape_616x353.jpg (Capsule 16:9 แนวนอน)
         • cover_header_460x215.jpg (Header มาตรฐาน)
    2. ลำดับที่ 2 (Wikimedia Commons Vector SVG & 4K Master):
       - ค้นหาผ่าน Wikimedia Commons MediaWiki API ด้วยคำค้น `{name} logo`
       - หากพบไฟล์ Vector (`.svg`) ให้เรนเดอร์ขนาดความคมชัดสูงสุดระดับ Master (`2048px` หรือ `3840px` PNG)
       - หากพบไฟล์ `.png` หรือ `.jpg` ความละเอียดสูง ให้ดาวน์โหลดไฟล์ Master ดั้งเดิมมาใช้งาน
    3. ลำดับที่ 3 (สแกนเจาะลึกไฟล์เกมในเครื่องและ Workspace):
       - สแกนหาไฟล์ภาพโลโก้หรือ Splash Screen ต้นฉบับจากโฟลเดอร์เกมหรือ `01_Original_Backup` (เช่น `*splash*.bmp`, `*splash*.png`, `*logo*.png`, `*title*.png`, `*title_atlas*.png`) ซึ่งหลายเกมใส่ภาพ 1080p หรือ 4K Uncompressed ไว้ในตัวเกม
    4. ลำดับที่ 4 (เปรียบเทียบและเลือก Master Logo ที่ชัดที่สุด):
       - คำนวณความละเอียด Pixel (width × height) ของทุกภาพที่หาได้ แล้วคัดเลือกภาพที่มีความละเอียดและคุณภาพสูงสุดเป็น Master Logo
  • สร้างชุดภาพโลโก้มาตรฐานครบทุกขนาด (Standardized Multi-Resolution Suite):
    ประมวลผลด้วยฟิลเตอร์คุณภาพสูง (Lanczos Resampling) บันทึกลงในโฟลเดอร์ `{path}/07_Image_Resources/Official_Art/Logos/`:
    1. `logo_master_original.png` (ขนาดจริงดั้งเดิม คมชัด 100% ไม่ลดทอนความละเอียด)
    2. `logo_ultra_4k_2048px.png` (ขนาดใหญ่พิเศษ 2K/4K — กว้าง 2048px สำหรับโปสเตอร์ / งานพิมพ์ / แบนเนอร์ยักษ์)
    3. `logo_large_1280px.png` (ขนาดใหญ่ 1080p — กว้าง 1280px สำหรับ Cover 16:9 / Full HD)
    4. `logo_medium_800px.png` (ขนาดกลาง — กว้าง 800px สำหรับภาพโพสต์ Facebook / Artwork Header)
    5. `logo_standard_512px.png` (ขนาดมาตรฐาน — กว้าง 512px สำหรับการ์ด THub / Store Capsule)
    6. `logo_small_256px.png` (ขนาดเล็ก — กว้าง 256px สำหรับ UI Dialog / Modal)
    7. `logo_icon_128px.png` (ขนาดไอคอน — กว้าง 128px สำหรับ Badge / App Icon)
  • บันทึกไฟล์ภาพค้นพบต้นฉบับ (Preserve Candidates):
    - บันทึกไฟล์โลโก้ดิบที่หาได้จากแต่ละแหล่งเป็น `candidate_*.png` เก็บไว้ใน `Logos/` เพื่อให้เลือกใช้ยามจำเป็น
  • ความเข้ากันได้ย้อนหลัง (Backward Compatibility):
    - คัดลอก `logo_large_1280px.png` (หรือ master) ไปไว้ที่ `{path}/07_Image_Resources/Official_Art/official_logo.png` เพื่อให้พร้อมเปิดทำงานใน Photoshop Template ทันที
    - คัดลอก `cover_landscape_616x353.jpg` ไปไว้ที่ `{path}/thub_cover.jpg` เพื่อให้การ์ดใน THub แสดงภาพสวยงาม

ขั้นตอนที่ 4: ระดมสมองคิดชื่อไตเติลภาษาไทย & เขียนไฟล์ AI Logo Prompt
  • วิเคราะห์เนื้อเรื่องและธีมของเกม {name} เพื่อเสนอไอเดียชื่อเกมภาษาไทย 3-5 แบบ:
    - แบบทับศัพท์โมเดิร์น
    - แบบแปลความหมายแฟนตาซี/ไซไฟ
    - แบบสั้นกระชับติดหู
  • สร้าง/อัปเดตไฟล์ {path}/07_Image_Resources/Generated_Logo/AI_Logo_Prompt.md
    บรรจุชุดคำสั่ง Prompt คุณภาพสูงสำหรับ Midjourney v6.1, FLUX.1, SDXL, DALL-E 3
    โดยบังคับคีย์เวิร์ด: 3D extruded lettering, completely isolated on pure solid flat black background เพื่อให้นำไปไดคัทใน Photoshop ได้ทันทีใน 1 คลิก

ขั้นตอนที่ 5: คู่มือประกอบงานใน Photoshop (1-Click Workflow)
  • แนะนำเทคนิคการนำภาพโลโก้พื้นหลังดำ ไปวางใน PSD Template แล้วเปลี่ยน Blending Mode เป็น Screen หรือใช้ Select Subject ลบพื้นหลังดำออกใน 3 วินาที
  • นำภาพ Official Art (Hero banner หรือ Portrait) มาวางเป็นฉากหลัง
  • เซฟภาพผลงานสำเร็จรูปไว้ที่ {path}/07_Image_Resources/Final_Exports/

══════════════════════════════════════════════════════
สคริปต์อัตโนมัติ (Automation Script - รันได้ทันที):
══════════════════════════════════════════════════════
หากคุณเป็น AI Agent (Claude Code / Antigravity) หรือผู้ใช้ ให้รันสคริปต์ Python ด้านล่างนี้เพื่อดำเนินการอัปเกรดโฟลเดอร์ ดาวน์โหลดภาพ และสร้าง Prompt ทั้งหมดให้เสร็จสิ้นใน 3 วินาที:

```python
import os, sys, shutil, urllib.request, urllib.parse, io, json

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

game_name = "{name}"
ws_path = r"{path}"
engine_name = "{engine_name}"

img_res = os.path.join(ws_path, "07_Image_Resources")
official_art = os.path.join(img_res, "Official_Art")
logos_dir = os.path.join(official_art, "Logos")
gen_logo = os.path.join(img_res, "Generated_Logo")
final_exp = os.path.join(img_res, "Final_Exports")
for d in [official_art, logos_dir, gen_logo, final_exp]:
    os.makedirs(d, exist_ok=True)

tmpl_candidates = [
    r"templates\\07_Image_Resources",
    r"E:\\Mod_Workspace\\1_Template\\07_Image_Resources"
]
tmpl_src = next((d for d in tmpl_candidates if os.path.exists(d)), tmpl_candidates[0])
if os.path.exists(tmpl_src):
    for f in os.listdir(tmpl_src):
        src_f = os.path.join(tmpl_src, f)
        dst_f = os.path.join(img_res, f)
        if os.path.isfile(src_f) and not os.path.exists(dst_f):
            shutil.copy2(src_f, dst_f)
            print(f"Copied template: {{f}}")

# 1. Resolve Steam AppID
appid = None
query = urllib.parse.quote(game_name.strip())
url = f"https://store.steampowered.com/api/storesearch/?term={{query}}&l=english&cc=US"
req = urllib.request.Request(url, headers={{'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}})
try:
    with urllib.request.urlopen(req, timeout=8) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        if data.get("total", 0) > 0:
            appid = data["items"][0]["id"]
            print(f"🎯 Resolved Steam AppID: {{appid}} ({{data['items'][0]['name']}})")
except Exception as e:
    print(f"Steam search notice: {{e}}")

# 2. Multi-Tier Logo Discovery
has_pil = False
try:
    from PIL import Image
    has_pil = True
except ImportError:
    pass

candidates = []

# Tier 1: Steam Retina 2X & Standard CDN
if appid:
    steam_urls = [
        ("Steam 2X Retina", f"https://cdn.akamai.steamstatic.com/steam/apps/{{appid}}/logo_2x.png"),
        ("Steam 2X Fastly", f"https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/{{appid}}/logo_2x.png"),
        ("Steam Standard", f"https://cdn.akamai.steamstatic.com/steam/apps/{{appid}}/logo.png"),
    ]
    for src_label, u in steam_urls:
        try:
            r = urllib.request.Request(u, headers={{'User-Agent': 'Mozilla/5.0'}})
            with urllib.request.urlopen(r, timeout=6) as res:
                if res.status == 200:
                    content = res.read()
                    if len(content) > 1000:
                        if has_pil:
                            im = Image.open(io.BytesIO(content))
                            candidates.append((src_label, im, content, f"steam_{{im.width}}x{{im.height}}.png"))
                            print(f"✅ Found {{src_label}}: {{im.width}}x{{im.height}} ({{len(content):,}} bytes)")
                        else:
                            candidates.append((src_label, None, content, "steam_logo.png"))
                        break
        except Exception:
            pass

    capsules = [
        ("cover_landscape_616x353.jpg", f"https://cdn.akamai.steamstatic.com/steam/apps/{{appid}}/capsule_616x353.jpg"),
        ("cover_portrait_600x900.jpg", f"https://cdn.akamai.steamstatic.com/steam/apps/{{appid}}/library_600x900_2x.jpg"),
        ("banner_hero_1920x620.jpg", f"https://cdn.akamai.steamstatic.com/steam/apps/{{appid}}/library_hero.jpg"),
        ("cover_header_460x215.jpg", f"https://cdn.akamai.steamstatic.com/steam/apps/{{appid}}/header.jpg"),
    ]
    for fn, u in capsules:
        fp = os.path.join(official_art, fn)
        try:
            r = urllib.request.Request(u, headers={{'User-Agent': 'Mozilla/5.0'}})
            with urllib.request.urlopen(r, timeout=6) as res:
                if res.status == 200:
                    content = res.read()
                    if len(content) > 500:
                        with open(fp, "wb") as out:
                            out.write(content)
                        print(f"Downloaded: {{fn}} ({{len(content):,}} bytes)")
        except Exception:
            pass

    best_cover = os.path.join(official_art, "cover_landscape_616x353.jpg")
    if os.path.exists(best_cover):
        shutil.copy2(best_cover, os.path.join(ws_path, "thub_cover.jpg"))

# Tier 2: Wikimedia Commons (Vectors & High-Res PNGs)
try:
    wiki_api = "https://commons.wikimedia.org/w/api.php"
    search_params = {{"action": "query", "list": "search", "srsearch": f"{{game_name}} logo", "srnamespace": "6", "format": "json"}}
    w_req = urllib.request.Request(f"{{wiki_api}}?{{urllib.parse.urlencode(search_params)}}", headers={{'User-Agent': 'ModderHub/2.2'}})
    with urllib.request.urlopen(w_req, timeout=6) as wr:
        wdata = json.loads(wr.read().decode('utf-8'))
        search_items = wdata.get("query", {{}}).get("search", [])
        for item in search_items[:3]:
            title = item.get("title")
            info_params = {{"action": "query", "titles": title, "prop": "imageinfo", "iiprop": "url|size|mime", "iiurlwidth": "2048", "format": "json"}}
            ireq = urllib.request.Request(f"{{wiki_api}}?{{urllib.parse.urlencode(info_params)}}", headers={{'User-Agent': 'ModderHub/2.2'}})
            with urllib.request.urlopen(ireq, timeout=6) as ir:
                idata = json.loads(ir.read().decode('utf-8'))
                pages = idata.get("query", {{}}).get("pages", {{}})
                for _, pdata in pages.items():
                    for ii in pdata.get("imageinfo", []):
                        target_url = ii.get("thumburl") or ii.get("url")
                        mime = ii.get("mime", "")
                        if "png" in mime or "svg" in mime or "jpeg" in mime:
                            try:
                                dl_req = urllib.request.Request(target_url, headers={{'User-Agent': 'Mozilla/5.0'}})
                                with urllib.request.urlopen(dl_req, timeout=8) as dl_resp:
                                    content = dl_resp.read()
                                    if len(content) > 1000 and has_pil:
                                        im = Image.open(io.BytesIO(content))
                                        candidates.append((f"Wikimedia ({{title}})", im, content, f"wikimedia_{{im.width}}x{{im.height}}.png"))
                                        print(f"✅ Found Wikimedia Asset ({{title}}): {{im.width}}x{{im.height}} ({{len(content):,}} bytes)")
                            except Exception:
                                pass
except Exception as e:
    print(f"Wikimedia notice: {{e}}")

# Tier 3: Local Workspace / Backup Deep Scan
search_dirs = [ws_path]
orig_dir = os.path.join(ws_path, "01_Original_Backup")
if os.path.exists(orig_dir):
    search_dirs.append(orig_dir)

for s_dir in search_dirs:
    for root, _, files in os.walk(s_dir):
        if "07_Image_Resources" in root:
            continue
        for f in files:
            f_lower = f.lower()
            if any(k in f_lower for k in ["splash", "logo", "title"]) and f_lower.endswith((".png", ".bmp", ".jpg")):
                local_fp = os.path.join(root, f)
                try:
                    with open(local_fp, "rb") as lf:
                        content = lf.read()
                    if has_pil:
                        im = Image.open(io.BytesIO(content))
                        if im.width >= 400 and im.height >= 100:
                            candidates.append((f"Local File ({{f}})", im, content, f"local_{{im.width}}x{{im.height}}.png"))
                            print(f"✅ Found Local Asset ({{f}}): {{im.width}}x{{im.height}}")
                except Exception:
                    pass

# Tier 4: Select Master & Generate Multi-Size Pack
if candidates and has_pil:
    candidates.sort(key=lambda c: c[1].width * c[1].height, reverse=True)
    best_label, best_img, best_bytes, _ = candidates[0]
    print(f"\n👑 Selected Master Logo: {{best_label}} ({{best_img.width}}x{{best_img.height}})")

    for label, c_img, c_bytes, c_fname in candidates[:4]:
        cand_fp = os.path.join(logos_dir, f"candidate_{{c_fname}}")
        if not os.path.exists(cand_fp):
            try:
                c_img.save(cand_fp, format="PNG")
            except Exception:
                pass

    master_path = os.path.join(logos_dir, "logo_master_original.png")
    best_img.save(master_path, format="PNG")
    print(f"📁 Saved Master Logo: {{master_path}} ({{best_img.width}}x{{best_img.height}})")

    target_widths = [
        ("logo_ultra_4k_2048px.png", 2048),
        ("logo_large_1280px.png",   1280),
        ("logo_medium_800px.png",    800),
        ("logo_standard_512px.png",  512),
        ("logo_small_256px.png",     256),
        ("logo_icon_128px.png",      128),
    ]

    aspect = best_img.height / max(1, best_img.width)
    resample_filter = getattr(Image, "Resampling", Image).LANCZOS

    for fname, target_w in target_widths:
        target_h = max(1, int(target_w * aspect))
        out_fp = os.path.join(logos_dir, fname)
        resized_im = best_img.resize((target_w, target_h), resample=resample_filter)
        resized_im.save(out_fp, format="PNG")
        print(f"  ↳ Generated {{fname}}: {{target_w}}x{{target_h}}")

    compat_logo = os.path.join(official_art, "official_logo.png")
    large_logo = os.path.join(logos_dir, "logo_large_1280px.png")
    compat_src = large_logo if os.path.exists(large_logo) else master_path
    shutil.copy2(compat_src, compat_logo)
    print(f"📁 Linked official_logo.png -> {{os.path.basename(compat_src)}}")
elif candidates:
    best_label, _, best_bytes, _ = candidates[0]
    out_fp = os.path.join(official_art, "official_logo.png")
    with open(out_fp, "wb") as f:
        f.write(best_bytes)
    print(f"Saved logo: {{out_fp}}")

print("07_Image_Resources retrofit and multi-size logo harvest completed successfully!")
```

คำแนะนำสำหรับ AI:
หากเข้าใจบทบาทแล้ว ให้รันสคริปต์ข้างต้นเพื่อจัดระเบียบและดึงภาพโลโก้ความละเอียดสูงหลายขนาด จากนั้นสร้างไฟล์ `07_Image_Resources/Generated_Logo/AI_Logo_Prompt.md` และรายงานผลการจัดระเบียบพร้อมไอเดียชื่อไตเติลไทย 3-5 แบบให้ฉันเลือกทันทีครับ!
"""

    @classmethod
    def _resolve_tstudio_profile(cls, project):
        """Resolves active TStudio preset, tone instructions, and glossary for a given project."""
        import json
        game_name = project.get("name", "")
        ws_path = project.get("path", "")
        preset_name = None
        system_prompt = ""
        glossary = {}
        source_desc = "Default"

        target_paths = []
        if ws_path and os.path.exists(ws_path):
            local_p = os.path.join(ws_path, ".thub", "profile", "prompts.json")
            if os.path.exists(local_p):
                target_paths.append((local_p, "Local Project Profile (.thub/profile/prompts.json)"))

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        core_prompts = os.path.join(base_dir, "tools", "flagship", "Core", "prompts.json")
        if os.path.exists(core_prompts):
            target_paths.append((core_prompts, "Global TStudio Presets"))

        cwd_prompts = os.path.abspath(os.path.join("tools", "flagship", "Core", "prompts.json"))
        if os.path.exists(cwd_prompts) and (cwd_prompts, "Global TStudio Presets") not in target_paths:
            target_paths.append((cwd_prompts, "Global TStudio Presets"))

        proj_candidates = [game_name, os.path.basename(ws_path)] if ws_path else [game_name]
        if ws_path and os.path.exists(os.path.join(ws_path, "thub_project.json")):
            try:
                with open(os.path.join(ws_path, "thub_project.json"), "r", encoding="utf-8") as f:
                    meta = json.load(f)
                    p_name = meta.get("profile_name") or meta.get("project_name")
                    if p_name:
                        proj_candidates.insert(0, p_name)
            except Exception:
                pass

        for ppath, pdesc in target_paths:
            try:
                with open(ppath, "r", encoding="utf-8") as f:
                    pdata = json.load(f)
                presets = pdata.get("presets", {})
                for cand in proj_candidates:
                    if not cand:
                        continue
                    cand_clean = re.sub(r'[^a-zA-Z0-9]', '', cand).lower()
                    for k, v in presets.items():
                        k_clean = re.sub(r'[^a-zA-Z0-9]', '', k).lower()
                        if k_clean and (k_clean == cand_clean or cand_clean in k_clean or k_clean in cand_clean):
                            preset_name = k
                            system_prompt = v.get("batch") or v.get("single", "")
                            glossary = v.get("glossary", {})
                            source_desc = f"{k} ({pdesc})"
                            break
                    if preset_name:
                        break
                if preset_name:
                    break
            except Exception:
                continue

        if not glossary and ws_path and os.path.exists(ws_path):
            standalone_glossary_candidates = [
                os.path.join(ws_path, ".thub", "profile", "glossary.json"),
                os.path.join(ws_path, "translation.glossary.json"),
                os.path.join(ws_path, "02_Translation_Workspace", "translation.glossary.json"),
                os.path.join(ws_path, "02_Translation_Workspace", "glossary.json"),
            ]
            for g_path in standalone_glossary_candidates:
                if os.path.exists(g_path):
                    try:
                        with open(g_path, "r", encoding="utf-8") as gf:
                            g_data = json.load(gf)
                        if isinstance(g_data, dict) and g_data:
                            glossary = g_data
                            source_desc += f" + Standalone Glossary ({os.path.basename(g_path)})"
                            break
                    except Exception:
                        pass

        return {
            "preset_name": preset_name or (game_name if game_name else "Default"),
            "system_prompt": system_prompt,
            "glossary": glossary,
            "source_desc": source_desc
        }

    @classmethod
    def has_tstudio_profile(cls, project):
        """
        Validates whether the project has a configured TStudio profile with non-empty glossary and system prompt.
        Returns: (has_profile, has_glossary, has_prompt, profile_data)
        """
        prof = cls._resolve_tstudio_profile(project)
        preset_name = prof.get("preset_name")
        system_prompt = prof.get("system_prompt", "").strip()
        glossary = prof.get("glossary", {})

        has_glossary = bool(glossary and len(glossary) > 0)
        has_prompt = bool(system_prompt and len(system_prompt) > 15 and system_prompt != "Default")
        has_profile = bool(preset_name and preset_name != "Default" and (has_glossary or has_prompt))

        return has_profile, has_glossary, has_prompt, prof

    @classmethod
    def get_persona_prompt(cls, project, mode="agent", options=None, app_lang="th", **kwargs):
        """
        Generates the specialized Game Localization Persona, Pronoun & Dialogue QA Specialist prompt.
        Focuses on 6 Comprehensive Pillars:
          1. Character Persona & Pronoun Calibration (Female soldiers, AWACS/Wingman dynamics)
          2. Context, Mannerisms & Tone Polish (Radio brevity vs intimacy, emotional delivery)
          3. Skill, Spell & Combat Phrase Localization Protocol (Deep lore research, punchy compounds for fantasy skills, transliteration for proper nouns, anti-MT blacklist)
          4. Item, Gaming Terminology & Firearms Protocol (Checkpoint -> แยกแยะจุดเซฟ = เช็คพอยท์ vs ด่านตรวจทหาร/ตำรวจ = ด่านตรวจ; Guns M60, M4A1, AK-47)
          5. Dialogue QA, 100% Line-by-Line Reading & Speech Leak Detection (Exhaustive line processing, detect untranslated lines, empty cells, CJK leaks, tag safety)
          6. TStudio Project Profile Bridge & AI Translation Integration (Select project profile, batch translate)
        """
        game_name = project.get("name", "Unknown Game")
        engine_name = project.get("engine") or project.get("engine_badge") or "Custom Engine"
        ws_path = project.get("path", "")

        # Dynamic Workspace Scan: Detect text files and glossaries
        detected_text_files = []
        glossary_files = []
        if ws_path and os.path.exists(ws_path):
            target_dirs = [
                os.path.join(ws_path, "02_Translation_Workspace"),
                os.path.join(ws_path, "03_Translated_Text"),
                os.path.join(ws_path, "02_Extracted_Text"),
                ws_path
            ]
            seen_files = set()
            for d in target_dirs:
                if not os.path.exists(d):
                    continue
                for root, _, files in os.walk(d):
                    if any(x in root for x in ["03_tools", "tools", ".git", "__pycache__", "07_Image_Resources", "01_Original_Files", "bin", "obj", "DerivedDataCache"]):
                        continue
                    for f in files:
                        f_lower = f.lower()
                        if f_lower.endswith((".csv", ".tsv", ".txt", ".locres.csv", ".json", ".ini", ".int", ".po", ".xml")):
                            rel_p = os.path.relpath(os.path.join(root, f), ws_path).replace("\\", "/")
                            if rel_p not in seen_files:
                                seen_files.add(rel_p)
                                if any(k in f_lower for k in ["glossary", "term", "dict", "tlm"]):
                                    glossary_files.append(rel_p)
                                else:
                                    detected_text_files.append(rel_p)

        file_list_str = "\n".join(f"  - `{f}`" for f in detected_text_files[:10]) if detected_text_files else "  - (ไม่พบไฟล์ข้อความในโฟลเดอร์ 02_Translation_Workspace หรือ 03_Translated_Text)"
        if len(detected_text_files) > 10:
            file_list_str += f"\n  - ... และไฟล์อื่นๆ อีก {len(detected_text_files) - 10} ไฟล์"

        glossary_str = "\n".join(f"  - `{g}`" for g in glossary_files[:5]) if glossary_files else "  - ไม่พบไฟล์คลังคำศัพท์แยกเป็นเอกเทศ"

        # Resolve TStudio Profile & Presets
        prof = cls._resolve_tstudio_profile(project)
        preset_name = prof["preset_name"]
        system_tone_prompt = prof["system_prompt"]
        project_glossary = prof["glossary"]
        source_desc = prof["source_desc"]
        glossary_count = len(project_glossary)

        tone_summary = (
            system_tone_prompt.strip()[:350] + "..."
            if len(system_tone_prompt.strip()) > 350
            else (system_tone_prompt.strip() if system_tone_prompt.strip() else "(ใช้ค่าเริ่มต้น Cinematic Game Localization Standard)")
        )

        glossary_table_md = ""
        if project_glossary:
            sample_items = list(project_glossary.items())[:12]
            sample_rows = [f"| `{k}` | **{v}** |" for k, v in sample_items]
            glossary_table_md = "\n".join([
                "| คำศัพท์ต้นฉบับ (Source) | คำแปลทางการประจำโปรเจกต์ (Glossary) |",
                "| :--- | :--- |"
            ] + sample_rows)
            if glossary_count > 12:
                glossary_table_md += f"\n| *(และคำศัพท์อื่นอีก {glossary_count - 12} คำ)* | *(ดึงจาก Profile {preset_name})* |"
        else:
            glossary_table_md = "*(ยังไม่มีคำศัพท์เฉพาะในพรีเซ็ต — ให้สร้าง Character Dossier & Custom Terms ระหว่างตรวจแก้)*"

        is_agent_mode = (mode == "agent")
        mode_header = "โหมดปฏิบัติการอัตโนมัติ (Autonomous Agent Mode - Claude Code / Antigravity / Cursor)" if is_agent_mode else "โหมดที่ปรึกษาการแปล (Consultant Web Chat Mode - ChatGPT / Claude Web)"

        step1_instruction = (
            "ทำการสแกนไฟล์เพื่อสร้าง **Character Dossier & Pronoun Matrix** พร้อมตรวจจับประโยคบทพูดที่หลงแปล และนำไปประยุกต์ใช้ในการเขียนโค้ดแก้ไฟล์จริงทันที:"
            if is_agent_mode else
            "ก่อนลงมือแก้ไฟล์ ให้ทำการสแกนไฟล์เพื่อสร้าง **Character Dossier & Pronoun Matrix** และรายงานข้อความที่หลงแปลเสนอผู้ใช้:"
        )

        game_clean = re.sub(r'[^a-zA-Z0-9_]', '_', game_name).strip('_')

        prompt = f"""# Role & Mission: Game Localization Persona, Dialogue QA & Weapon Specialist
========================================================================================
> **ระบบ:** THub AI Helper Copilot — Persona, Pronoun, Context Polish & Full Dialogue QA Suite
> **โหมดการทำงาน:** {mode_header}
> **โปรเจกต์เป้าหมาย:** {game_name} ({engine_name})
> **Workspace Path:** `{ws_path}`
> **TStudio Project Profile:** `{preset_name}` ({source_desc})

คุณคือผู้เชี่ยวชาญระดับอาวุโสด้านการตรวจแก้บทแปลเกมภาษาไทย (Senior Thai Game Localization Editor & QA Lead)
มีภารกิจหลักในการควบคุมคุณภาพการแปลแบบรอบด้าน 7 มิติ (The 7 QA & Localization Pillars):
1. **คุมบุคลิกและสรรพนามตัวละคร (Persona & Pronouns Matrix):** ขจัดปัญหากฎทหารเหมารวม (ตัวละครหญิงพูด 'ผม/ครับ') และปรับสรรพนามตามลำดับความสัมพันธ์
2. **ขัดเกลากิริยาบทและบริบท (Context, Mannerisms & Tone Polish):** ปรับแก้สำนวนแข็งทื่อของการแปลตรงตัว ถ่ายทอดอารมณ์ฉากและวิทยุสนามรบให้เข้าปาก
3. **พิธีสารการแปลสกิล เวทมนตร์ วลี และทักษะเกมแฟนตาซี/แอ็กชัน (Skill, Spell & Combat Phrase Protocol):** สืบค้นบริบทเกม/Lore/คลาสอย่างละเอียด แปลชื่อสกิลแฟนตาซีสั้นๆ เป็นวลีสั้นสละสลวย 2-6 พยางค์ หรือทับศัพท์หากเป็นคำเฉพาะ/ชื่อเฉพาะ บังคับใช้บัญชีดำกลไกเกมผิดมหันต์
4. **กฎเหล็กชื่อไอเท็ม, คำศัพท์ระบบเกม และอาวุธปืน (Item, Gaming Terminology & Firearms Protocol):** บังคับใช้กฎห้ามทับศัพท์ชื่อรุ่นปืนเป็นไทย (`M60`, `M4A1`) และ **แยกแยะคำว่า `Checkpoint` ตามบริบท: กลไกเซฟเกม = "เช็คพอยท์", ด่านทหาร/ตำรวจ = "ด่านตรวจ" ห้ามเหมารวมเด็ดขาด**
5. **ความสอดคล้องของชื่อเควสต์และเงื่อนไขเป้าหมาย 100% (Quest Log, Objectives & Title Consistency Protocol):** ชื่อเควสต์ข้ามหัวข้อ บันทึก Log และบทสนทนาต้องตรงกัน 100%
6. **ตรวจจับบทสนทนาหลุดแปล & กฎเหล็กอ่านครบทุกประโยคห้ามข้าม 100% (Dialogue Leak QA & Typography):** ค้นหาบทพูดที่ยังไม่ได้แปล ค้างเป็นภาษาอังกฤษ หลุด CJK ตรวจสระลอย PUA พร้อมยึดกฎต้องอ่านและแปลครบทุกประโยค
7. **พิธีสารการแปลบันทึก ปูมหลัง และสารานุกรมในเกม (Codex, Lore, Books & In-Game Readables Protocol):** แยกแยะระดับภาษาน้ำเสียงตามประเภทเอกสาร ร้อยเรียงย่อหน้าให้อ่านลื่นไหล ห้ามย่อความเด็ดขาด และห้ามแต่งเติมเรื่องเอง

---

## 📂 ข้อมูลสภาพแวดล้อมโปรเจกต์ & โปรไฟล์ TStudio (Project & Profile Inventory)
- 🎮 **ชื่อเกม / Game Title:** {game_name}
- ⚙️ **Game Engine:** {engine_name}
- 📁 **โฟลเดอร์ Workspace:** `{ws_path}`
- 🎯 **TStudio Profile ที่จับคู่ได้:** `{preset_name}`
- 🎭 **แนวทางโทนและคำสั่งแปลเฉพาะ (Tone & System Directive):**
  > {tone_summary}
- 📖 **คลังคำศัพท์ของโปรเจกต์ (Project Glossary - {glossary_count} รายการ):**
{glossary_table_md}
- 📄 **ไฟล์บทแปลที่ตรวจพบใน Workspace:**
{file_list_str}
- 📚 **ไฟล์สารบรรณคำศัพท์ที่ตรวจพบ:**
{glossary_str}

---

## 🏛️ สถาปัตยกรรมเสาหลักการตรวจสอบ 7 มิติ (The 7 QA & Localization Pillars)

### 📌 เสาหลักที่ 1: สารบบตัวละคร สรรพนาม และลำดับชั้นความสัมพันธ์ (Persona & Pronoun Matrix)
{step1_instruction}
1. ค้นหาบทพูด ชื่อตัวละคร Callsign หรือ Context ในไฟล์แปล (เช่น เรย์ / Ray, ตัวละครหญิง, นักบิน, เจ้าหน้าที่เรดาร์ / AWACS, ผบ., เพื่อนร่วมทีม)
2. วิเคราะห์เพศ บุคลิก สถานะ และความสัมพันธ์
3. จัดหมวดหมู่ในตารางอ้างอิง:
   | ชื่อตัวละคร / Callsign | เพศ / บทบาท | สรรพนามแทนตัวเอง (1st Person) | สรรพนามเรียกผู้อื่น (2nd Person) | คำลงท้าย |
   |---|---|---|---|---|
   | (เช่น Ray) | (หญิง, นักบินร่วมฝูง/Wingman) | ฉัน / (หรือชื่อเล่น) | นาย / คุณ / หัวหน้าฝูง | ไม่ใส่ลงท้าย (เน้นกระชับ) / หรือ ค่ะ ในบทดราม่า |
   | (เช่น AWACS / Control) | (หญิง, เจ้าหน้าที่เรดาร์) | ฉัน / ดิฉัน (รายงาน ผบ.) | คุณ / สัญญาณเรียกขาน (Callsign) | รับทราบ (ตัด ค่ะ/คะ ออกเมื่อรบ) |
   | (เช่น Commander) | (ชาย, ผู้บังคับบัญชา) | ฉัน / ผู้การ | นาย / พวกนาย / ผู้หมวด | ไม่มีลงท้าย (สั่งการเด็ดขาด) |
4. **กฎเกณฑ์สรรพนามในบริบททหาร/วิทยุการบิน (Military & Radio Brevity)**:
   - **ตัวละครหญิงในหน้าที่ทหาร / วิทยุสนามรบ**:
     - เมื่อสื่อสารทางวิทยุหรือรายงานเหตุการณ์: เน้นกระชับ ฉับไว **ห้ามใช้ "ผม/ครับ" เด็ดขาด** และตัดคำสร้อย "ค่ะ/คะ" ในเวลาคับขัน
     - แทนตัวเอง: ใช้ **"ฉัน"** (ธรรมชาติที่สุดในสนามรบ) หรือ **"ดิฉัน"** (เมื่อรายงานผู้บังคับบัญชาชั้นสูงเป็นทางการ)
     - เรียกเพื่อนร่วมทีม/คู่สนทนา: ใช้ **"นาย"**, **"คุณ"**, หรือเรียก **Callsign/ยศ** (เช่น "แจ็คเกิล", "หัวหน้าฝูง", "ผู้การ")
   - **ตัวละครหญิงในบทสนทนาส่วนตัว/ดราม่า**:
     - ใช้ "ฉัน - เธอ/นาย", คำลงท้าย "ค่ะ/คะ" ตามระดับความสนิทสนม
   - **ตัวละครชาย**:
     - ใช้ "ผม/ครับ" เมื่อพูดกับผู้บังคับบัญชา หรือใช้ "ฉัน/นาย" ในระดับเพื่อนร่วมฝูงบินตามสายการบังคับบัญชา

---

### 📌 เสาหลักที่ 2: ขัดเกลาบริบท กิริยาบท อารมณ์ และสำนวนภาษา (Context, Mannerisms & Tone Polish)
ไม่ใช่แค่เปลี่ยนคำสรรพนาม แต่ต้องปรับสำนวนให้เข้ากับกิริยาบท อารมณ์ และสถานการณ์ของฉาก:
1. **ตัดความแข็งทื่อของการแปลตรงตัว (Anti-Literal Translation / Anti-MT Stiffness)**:
   - แปลงภาษาแปลหุ่นยนต์ให้เป็น "บทพูดที่มนุษย์จริงๆ ในสถานการณ์นั้นจะพูดออกมา"
   - ประโยคคำถาม ปฏิเสธ หรือประโยคอุทาน ต้องเข้าปากและสอดคล้องกับอารมณ์ของตัวละคร
2. **ปรับตามกิริยาบทและสถานการณ์ของฉาก (Situational Dynamics)**:
   - **สถานการณ์ฉุกเฉิน/การปะทะ (Combat & Emergency)**: ภาษาฉับไว เด็ดขาด สั้นกระชับ ตัดคำฟุ่มเฟือย
   - **บทสนทนาพักรบ/ส่วนตัว (Downtime & Personal Intimacy)**: เป็นกันเอง แสดงความรู้สึกได้อย่างเปิดเผย
   - **บทสนทนาเสียดสี/หยอกล้อ (Sarcasm & Banter)**: เล่นสำนวน มุกตลกประชดประชัน ไม่แปลตรงตัวเป็นข้อความทื่อๆ
   - **การแสดงอารมณ์โกรธ สูญเสีย หรือหวาดกลัว**: เลือกระดับคำที่ถ่ายทอดน้ำหนักอารมณ์ได้อย่างสมจริง

---

### 📌 เสาหลักที่ 3: พิธีสารการแปลสกิล เวทมนตร์ วลี และทักษะเกมแฟนตาซี/แอ็กชัน (Skill, Spell & Combat Phrase Protocol)
1. **การสืบค้นบริบทและ Lore ของสกิลอย่างละเอียดก่อนแปล (Pre-Translation Deep Context & Lore Research)**:
   - 🛑 **ห้ามแปลเดาสุ่มจากสตริงที่ลอยมาโดยไม่ดูบริบท**
   - วิเคราะห์ธีมเกม, สายอาชีพ, อาวุธ, ธาตุ และแอนิเมชันก่อนแปลเสมอ
2. **การแปลชื่อสกิลเกมแฟนตาซี — "วลีสั้น สละสลวย ได้ใจความ 2-6 พยางค์"**:
   - ❌ **ห้ามแปลเป็นประโยคยาวเหยียด** หรือมีคำฟุ่มเฟือยแบบหุ่นยนต์ (เช่น "การ...", "ที่มี...")
   - ✅ **ร้อยเรียงคำเป็น "วลีสั้นๆ 2-6 พยางค์" ที่ทรงพลัง สละสลวย:**
     - `Flame Slash` ➔ ✅ **"ดาบเพลิงพิฆาต"** *(ไม่ใช่ "การสแลชเปลวไฟ")*
     - `Shadow Step` ➔ ✅ **"ก้าวเงา"** *(ไม่ใช่ "ขั้นตอนเงา")*
     - `Frost Nova` ➔ ✅ **"ระเบิดเยือกแข็ง"**
     - `Thunder Strike` ➔ ✅ **"อสุนีบาตฟาด"**
     - `Divine Smite` ➔ ✅ **"ทัณฑ์เทวา"**
     - `Soul Harvest` ➔ ✅ **"กลืนวิญญาณ"**
3. **การใช้ทับศัพท์สำหรับคำเฉพาะและชื่อเฉพาะที่ไม่มีคำแปลตรงตัว**:
   - `Ragnarok` ➔ ✅ **"แร็กนาร็อค"** | `Gungnir` ➔ ✅ **"กุงเนียร์"** | `Excalibur` ➔ ✅ **"เอ็กซ์คาลิเบอร์"**
   - `Dash` ➔ **"แดช"** | `Parry` ➔ **"แพร์รี่"** | `Burst` ➔ **"เบิร์ส"** | `Overdrive` ➔ **"โอเวอร์ไดรฟ์"**
4. **บัญชีดำคำแปลกลไกเกมผิดมหันต์ (Anti-MT Blunder Blacklist) — [Critical QA]**:
   - 🛑 `Strike` ➔ แปลว่า `ฟาดฟัน / จู่โจม / ประหาร` (❌ ห้ามแปลว่า "นัดหยุดงาน")
   - 🛑 `Cast` ➔ แปลว่า `ร่าย` (❌ ห้ามแปลว่า "หล่อโลหะ" หรือ "คัดเลือกนักแสดง")
   - 🛑 `Cooldown` ➔ แปลว่า `คูลดาวน์ / เวลารอใช้ใหม่` (❌ ห้ามแปลว่า "เย็นลง")
   - 🛑 `Passive Skill` ➔ แปลว่า `สกิลติดตัว` (❌ ห้ามแปลว่า "ทักษะเฉยชา")
   - 🛑 `Critical Hit` ➔ แปลว่า `คริติคอล / โจมตีติดคริ` (❌ ห้ามแปลว่า "การโจมตีวิกฤต")
   - 🛑 `Lifesteal` ➔ แปลว่า `ดูดเลือด` (❌ ห้ามแปลว่า "ขโมยชีวิต")
   - 🛑 `Respawn` ➔ แปลว่า `เกิดใหม่` (❌ ห้ามแปลว่า "วางไข่")

---

### 📌 เสาหลักที่ 4: กฎเหล็กชื่อไอเท็ม, คำศัพท์ระบบเกม และอาวุธปืน/ยุทโธปกรณ์ (Item, Gaming Terminology & Firearms Protocol)
1. **Checkpoint (การแยกแยะบริบท 2 กรณีอย่างเคร่งครัด — Dual-Context Disambiguation) — [Critical QA]**:
   - 🟢 **กลไกบันทึกเกม / จุดเกิดใหม่ / UI Progress (Save / Respawn / UI):**
     - ✅ **ต้องแปล/ทับศัพท์ว่า "เช็คพอยท์" (หรือ "จุดเช็คพอยท์") เท่านั้น!**
     - ❌ **ห้ามแปลว่า "จุดตรวจ" หรือ "ด่านตรวจ" เด็ดขาด!** (เช่น `Checkpoint reached` ➔ `ถึงจุดเช็คพอยท์แล้ว`)
   - 🔴 **ด่านตรวจทหาร / ตำรวจ / กองกำลังศัตรู / ชายแดนในเนื้อเรื่อง (Physical Outpost):**
     - ✅ **ต้องแปลว่า "ด่านตรวจ" หรือ "จุดตรวจ" เสมอ!**
     - ❌ **ห้ามแปลว่า "เช็คพอยท์" เด็ดขาด!** (เช่น `Enemy checkpoint` ➔ `ด่านตรวจของศัตรู`)
2. **หมวดอาวุธปืน ยุทโธปกรณ์ และขนาดกระสุน (Firearms & Calibers) — [กฎเหล็กห้ามละเมิดเด็ดขาด]**:
   - 🛑 **ห้ามถอดเสียงทับศัพท์ชื่อรุ่นปืนเป็นตัวอักษรไทยเด็ดขาด!** (ห้ามแปล "เอ็ม 60", "เอ็ม 4", "เอเค 47")
   - ✅ **ต้องคงเป็นรหัสชื่อรุ่นภาษาอังกฤษและตัวเลขอารบิกเดิมเสมอ:** `M60`, `M4A1`, `AK-47`, `MP5`, `RPG-7`, `Glock 19`, `9mm`, `5.56mm`
   - ✅ **ใส่คำบอกประเภทภาษาไทยนำหน้าได้:** `ปืนกล M60`, `ปืนเล็กยาว M4A1`, `ปืนพก Glock 19`

---

### 📌 เสาหลักที่ 5: ความสอดคล้องของชื่อเควสต์และเงื่อนไขเป้าหมาย 100% (Quest Log & Objective Title Consistency Protocol)
1. **ความสอดคล้องของชื่อเควสต์ข้ามระบบ (Cross-System Quest Title Parity):**
   - ชื่อเควสต์ที่ปรากฏในหัวข้อเควสต์ (Quest Title), หน้าต่างติดตามเป้าหมาย (Objective Tracker), บันทึกย่อ (Log/Journal), และบทสนทนา **ต้องใช้ชื่อภาษาไทยตรงกันเป๊ะ 100% ห้ามแปลเพี้ยนคนละแบบ**
2. **การแปลกริยาเงื่อนไขเควสต์ให้กระชับ ชัดเจน (Action-Oriented Objective Verbs):**
   - `Investigate...` ➔ **"สำรวจ..."** | `Eliminate... / Defeat...` ➔ **"กำจัด..."** / **"ปราบ..."**
   - `Retrieve... / Recover...` ➔ **"กู้คืน..."** / **"นำ...กลับมา"** | `Speak with...` ➔ **"คุยกับ..."** | `Escort...` ➔ **"คุ้มกัน..."**
3. **การรักษาตัวนับและแท็กสถานะ:** รักษารหัสตัวนับจำนวน `{0}/{1}`, `%d/%d`, `[COMPLETED]` ให้สมบูรณ์

---

### 📌 เสาหลักที่ 6: ตรวจจับบทสนทนาหลุดแปล, กฎเหล็กอ่านครบทุกประโยคห้ามข้าม 100% & Typography (Dialogue Leak QA & Typography)
1. **กฎเหล็กการอ่านครบทุกประโยค 100% ห้ามข้าม ห้ามละเลยเด็ดขาด (100% Line-by-Line Zero Omission)**:
   - 🛑 **ต้องอ่าน ตรวจสอบ และแปล "ทุกประโยค ทุกบรรทัด 100%" ห้ามข้าม ห้ามย่อความเด็ดขาด!**
2. **ตรวจจับบทพูดที่ยังไม่ได้แปล (Speech Leaks)**:
   - ช่อง `translation` ว่างเปล่า หรือยังเป็นภาษาอังกฤษ
   - แปลค้างครึ่งๆ กลางๆ (Partial Code-switching) หรือมีอักษร CJK หลงเหลือ
3. **การรักษาแท็กเกมและโค้ดควบคุม (Strict Tag Integrity)**:
   - ห้ามทำแท็กหลุด: `{{0}}`, `{{name}}`, `%s`, `%d`, `<color=...>`, `\\n`, `[TAG_n]`
4. **ความถูกต้องทางวรรณยุกต์และฟอนต์ (Typography & Floating Vowels)**:
   - ตรวจสอบตำแหน่งสระลอย สระจม รองรับชุดรหัส PUA ภาษาไทย

---

### 📌 เสาหลักที่ 7: พิธีสารการแปลบันทึก ปูมหลัง หนังสือ และสารานุกรมในเกม (Codex, Lore, Books & In-Game Readables Protocol)
1. **จำแนกระดับภาษาและน้ำเสียงตามประเภทเอกสาร (Document Register Matrix):**
   - 📜 **จารึกโบราณ / คัมภีร์เวท:** ภาษาโบราณ ขึงขัง ศักดิ์สิทธิ์ สละสลวย ใช้คำวรรณคดี (*กาลก่อน, บรรพกาล, จุติ, วิบัติ, สถิต*)
   - 🔬 **รายงานวิจัย / ล็อกเทอร์มินัล:** ทางการ กึ่งวิชาการ เยือกเย็น เป็นระเบียบ
   - 🩸 **ไดอารีส่วนตัว / บันทึกสั่งเสีย:** ภาษาพูดส่วนบุคคล สะท้อนอารมณ์ ห้ามแปลแข็งทื่อเป็นเอกสารราชการ
   - ⚔️ **คำสั่งยุทธวิธี / บันทึกสนามรบ:** ภาษาทหาร กระชับ รัดกุม ชัดเจน
   - 🐉 **สารานุกรมมอนสเตอร์:** กึ่งสารคดีธรรมชาติวิทยา บรรยายรูปร่าง ถิ่นที่อยู่ พฤติกรรม และจุดอ่อน
2. **กฎเหล็กห้ามย่อความและห้ามแต่งเติมเอง (Strict Zero-Omission & Anti-Hallucination):**
   - 🛑 แปลครบถ้วนทุกประโยค ห้ามสรุปใจความเหลือ 1-2 บรรทัด และห้ามแต่งเรื่องเพิ่มเอง
"""

        if is_agent_mode:
            target_demo_csv = detected_text_files[0] if detected_text_files else '02_Translation_Workspace/Game_Text.csv'
            prompt += f"""
---

## 🤖 พิธีสารปฏิบัติการวนลูปอัตโนมัติ 7 เสาหลัก (Autonomous 7-Stage Chained State Machine Protocol)
> **สำหรับ AI Agent (Claude Code / Antigravity / Cursor):**
> 🛑 **กฎเหล็กเพื่อป้องกันงานไม่ละเอียด (STRICT ANTI-DILUTION RULE):**
> **ห้ามทำรวดเดียว 1-7 ในรอบเดียวเด็ดขาด!** เพราะจะทำให้เกิด Attention Dilution สมาธิเจือจาง และงานจะออกมาชุ่ย/รวบรัด
> **คุณต้องปฏิบัติตามสถานะ State Machine วนลูปทีละเสา (Pass 1 ถึง Pass 7) ตามลำดับอย่างเคร่งครัด**
> ในแต่ละรอบ ให้โฟกัสความสนใจ 100% กับกฎของเสานั้นๆ เขียนบันทึก Diff ลงดิสก์ แล้วจึงสั่งตัวเองก้าวสู่เสาถัดไปจนเสร็จสิ้น!

### 📋 วงจรการทำงานของ State Machine (Autonomous Execution Loop):

#### 🚀 ขั้นตอนที่ 0: เริ่มต้นและสร้างไฟล์สำรอง (Stage 0: INIT & Auto-Backup)
1. ตรวจสอบไฟล์บทแปลเป้าหมาย: `{target_demo_csv}`
2. สร้างไฟล์สำรองทันที: คัดลอกเก็บไว้ที่ `{target_demo_csv}.pre_qa_backup.csv`
3. สร้างโฟลเดอร์ `05_Scripts_and_Tools/` (หากยังไม่มี)
4. สร้างไฟล์ติดตามสถานะ `05_Scripts_and_Tools/qa_state.json`:
   ```json
   {{
     "project": "{game_name}",
     "target_file": "{target_demo_csv}",
     "current_stage": "PASS_1_PERSONA",
     "stages": {{
       "pass1_persona": "PENDING",
       "pass2_context_tone": "PENDING",
       "pass3_skills_spells": "PENDING",
       "pass4_items_firearms": "PENDING",
       "pass5_quests": "PENDING",
       "pass6_leaks_typography": "PENDING",
       "pass7_codex_lore": "PENDING"
     }},
     "completed_stages": [],
     "pass_reports": {{}}
   }}
   ```

#### 🎭 ขั้นตอนที่ 1: วนลูป Pass 1 — ตรวจสอบเสาที่ 1 (Persona & Pronouns Matrix)
1. อ่านไฟล์บทแปล สแกนหาชื่อตัวละคร เพศ ความสัมพันธ์ และบทพูดทั้งหมด
2. บังคับใช้กฎ: ตัวละครหญิง/อัศวินหญิง/นักบินหญิง ห้ามพูด "ผม/ครับ" เด็ดขาด! ปรับสรรพนามตามเมทริกซ์ความสัมพันธ์
3. บันทึกผลการตรวจแก้ลง `05_Scripts_and_Tools/qa_pass1_persona.json` (ระบุ row_index, key, original, modified, reason)
4. อัปเดต `qa_state.json`: `"pass1_persona": "DONE"`, `"current_stage": "PASS_2_CONTEXT_TONE"`
5. **สั่งตัวเองก้าวเข้าสู่ Pass 2 ทันทีโดยอัตโนมัติ**

#### 💬 ขั้นตอนที่ 2: วนลูป Pass 2 — ตรวจสอบเสาที่ 2 (Context, Mannerisms & Tone Polish)
1. นำข้อมูลจาก Pass 1 มาประมวลผลต่อ
2. ขจัดสำนวนแปลตรงตัวแข็งทื่อ (Anti-Literal MT) ปรับสำนวนอุปมาอุปไมย (Idiomatic Transcreation) ให้เข้าปากและถ่ายทอดอารมณ์ฉากได้สมจริง
3. บันทึกผลการตรวจแก้ลง `05_Scripts_and_Tools/qa_pass2_tone.json`
4. อัปเดต `qa_state.json`: `"pass2_context_tone": "DONE"`, `"current_stage": "PASS_3_SKILLS_SPELLS"`
5. **สั่งตัวเองก้าวเข้าสู่ Pass 3 ทันทีโดยอัตโนมัติ**

#### ⚔️ ขั้นตอนที่ 3: วนลูป Pass 3 — ตรวจสอบเสาที่ 3 (Skill, Spell & Combat Phrase Protocol)
1. โหลดข้อมูลจาก Pass 2 คัดกรองแถวที่เป็นชื่อสกิล คาถา ท่าต่อสู้ ทักษะติดตัว
2. แปลชื่อสกิลแฟนตาซีสั้นๆ เป็น **"วลีสั้น 2-6 พยางค์"** สละสลวยทรงพลัง (เช่น `Whirlwind Slash` ➔ `ดาบวายุหมุน`, `Flame Strike` ➔ `ดาบเพลิงพิฆาต`)
3. ใช้การทับศัพท์สำหรับชื่อเฉพาะและเวทมนตร์โบราณ (`Ragnarok` ➔ `แร็กนาร็อค`, `Gungnir` ➔ `กุงเนียร์`)
4. บังคับใช้บัญชีดำคำแปลกลไกเกมผิดมหันต์ (Strike ≠ นัดหยุดงาน, Cast ≠ หล่อโลหะ, Cooldown ≠ เย็นลง, Passive ≠ เฉยชา, Lifesteal ≠ ดูดเลือด, Respawn ≠ วางไข่)
5. บันทึกผลการตรวจแก้ลง `05_Scripts_and_Tools/qa_pass3_skills.json`
6. อัปเดต `qa_state.json`: `"pass3_skills_spells": "DONE"`, `"current_stage": "PASS_4_ITEMS_FIREARMS"`
7. **สั่งตัวเองก้าวเข้าสู่ Pass 4 ทันทีโดยอัตโนมัติ**

#### 🔫 ขั้นตอนที่ 4: วนลูป Pass 4 — ตรวจสอบเสาที่ 4 (Item, Gaming Terminology & Firearms Protocol)
1. โหลดข้อมูลจาก Pass 3 ตรวจสอบชื่อไอเท็ม ปืน และคำศัพท์ระบบเกม
2. **บังคับใช้กฎชื่อปืน 100%**: แก้ชื่อปืนที่ทับศัพท์ไทย ("เอ็ม 60", "เอเค 47") กลับเป็นรหัสรุ่นสากล `M60`, `M4A1`, `AK-47`, `Glock 19`
3. **แยกแยะ Checkpoint 2 กรณีอย่างเคร่งครัด**: จุดเซฟเกม/เกิดใหม่/UI = `เช็คพอยท์` (ห้าม `จุดตรวจ`), ด่านทหาร/ตำรวจ/ศัตรู = `ด่านตรวจ` (ห้าม `เช็คพอยท์`)
4. บันทึกผลการตรวจแก้ลง `05_Scripts_and_Tools/qa_pass4_items.json`
5. อัปเดต `qa_state.json`: `"pass4_items_firearms": "DONE"`, `"current_stage": "PASS_5_QUESTS"`
6. **สั่งตัวเองก้าวเข้าสู่ Pass 5 ทันทีโดยอัตโนมัติ**

#### 📜 ขั้นตอนที่ 5: วนลูป Pass 5 — ตรวจสอบเสาที่ 5 (Quest Log & Objective Title Consistency)
1. โหลดข้อมูลจาก Pass 4 รวบรวมชื่อเควสต์ทั้งหมดในเกม
2. ตรวจสอบความสอดคล้อง 100%: ชื่อเควสต์ในหัวข้อ (Title), ในเป้าหมาย (Objective), ในบันทึก Log, และในบทสนทนา ต้องใช้ชื่อเดียวกันเป๊ะ ห้ามแปลคนละอย่าง
3. บันทึกผลการตรวจแก้ลง `05_Scripts_and_Tools/qa_pass5_quests.json`
4. อัปเดต `qa_state.json`: `"pass5_quests": "DONE"`, `"current_stage": "PASS_6_LEAKS_TYPOGRAPHY"`
5. **สั่งตัวเองก้าวเข้าสู่ Pass 6 ทันทีโดยอัตโนมัติ**

#### 🔍 ขั้นตอนที่ 6: วนลูป Pass 6 — ตรวจสอบเสาที่ 6 (Dialogue Leak QA & Typography)
1. โหลดข้อมูลจาก Pass 5 สแกนหาข้อความที่ยังค้างเป็นภาษาอังกฤษ 100%, ค่าว่าง, หรือหลุด CJK
2. นำกฎและ Glossary จาก TStudio Profile (`{preset_name}`) มาแปลประโยคที่หลงแปลให้สมบูรณ์
3. ตรวจสอบสระลอย สระจม และรักษาแท็กเกม `{0}`, `%s`, `\\n`, `[TAG]` ให้สมบูรณ์ 100%
4. บันทึกผลการตรวจแก้ลง `05_Scripts_and_Tools/qa_pass6_leaks.json`
5. อัปเดต `qa_state.json`: `"pass6_leaks_typography": "DONE"`, `"current_stage": "PASS_7_CODEX_LORE"`
6. **สั่งตัวเองก้าวเข้าสู่ Pass 7 ทันทีโดยอัตโนมัติ**

#### 📖 ขั้นตอนที่ 7: วนลูป Pass 7 — ตรวจสอบเสาที่ 7 (Codex, Lore, Books & In-Game Readables)
1. โหลดข้อมูลจาก Pass 6 คัดกรองแถวที่เป็นหนังสือ บันทึก ไดอารี และศิลาจารึก
2. ปรับระดับภาษาตามประเภทเอกสาร (จารึกโบราณ = วรรณคดีขึงขัง, ไดอารี = ภาษาพูดส่วนตัวสะท้อนอารมณ์, รายงานทหาร = กระชับรัดกุม)
3. ยึดกฎเหล็ก: ห้ามย่อความ และห้ามแต่งเรื่องเองเด็ดขาด
4. บันทึกผลการตรวจแก้ลง `05_Scripts_and_Tools/qa_pass7_codex.json`
5. อัปเดต `qa_state.json`: `"pass7_codex_lore": "DONE"`, `"current_stage": "SYNTHESIS_MERGE"`
6. **สั่งตัวเองก้าวเข้าสู่รอบ Final Synthesis ทันที**

#### 🏆 ขั้นตอนที่ 8: ผสานรวมข้อมูล (Final Synthesis & Masterpiece Generation)
1. นำผลการแก้ไขสะสมทั้งหมดจาก Pass 1 ถึง Pass 7 มาเขียนทับลงไฟล์บทแปลจริง `{target_demo_csv}`
2. ต้องใช้ `encoding='utf-8-sig'` และ `newline=''` เสมอ คงโครงสร้างคอลัมน์เดิม 100%
3. อัปเดต `qa_state.json`: `"status": "COMPLETED"`, `"current_stage": "FINISHED"`
4. สร้างเอกสารรายงานสรุปฉบับสมบูรณ์: `05_Scripts_and_Tools/QA_7_PILLARS_MASTERPIECE_REPORT.md`
   - ตาราง Character Dossier & Pronoun Matrix
   - สรุปสถิติจำนวนบรรทัดที่แก้ไขในแต่ละเสา 1 - 7
   - ตารางเปรียบเทียบ Before vs After ของตัวอย่างสำคัญในแต่ละเสา
   - ตำแหน่งไฟล์ Backup และไฟล์ที่ผ่านการตรวจแก้เสร็จสมบูรณ์
5. สรุปความสำเร็จให้ผู้ใช้ทราบใน Terminal/แชท
"""
        else:
            prompt += f"""
---

## 💬 รูปแบบการตอบสนองสำหรับ Web Chat (Step-by-Step Cascade Mode)
> สำหรับผู้ใช้งานใน ChatGPT หรือ Claude Web:
> เพื่อให้งานได้คุณภาพสูงสุดระดับ Masterpiece ให้คุณส่งคำสั่งให้ AI ทำทีละเสาตามสคริปต์ Cascade ด้านล่างนี้:

### 🪜 ลำดับคำสั่งแบบ Cascade (สั่งทีละรอบในแชทเดิม):
* **รอบที่ 1 (ตรวจเสาที่ 1 - Persona):**
  > *"เริ่มตรวจสอบเฉพาะเสาหลักที่ 1 (Persona & Pronoun Matrix) บนข้อความด้านล่างนี้ โดยจำแนกเพศ ความสัมพันธ์ ตัวละครหญิงห้ามใช้ 'ผม/ครับ' และส่งมอบตาราง Character Dossier พร้อมบทแปลที่แก้สรรพนามแล้ว:"*
* **รอบที่ 2 (ตรวจเสาที่ 2 - Context & Tone):**
  > *"นำผลการแปลจากรอบที่ 1 มาตรวจแก้เฉพาะเสาหลักที่ 2 (Context, Mannerisms & Tone Polish) ขจัดสำนวนแปลตรงตัว ปรับสำนวนอุปมาอุปไมยให้เข้าปาก และถ่ายทอดอารมณ์ฉากให้สมจริง"*
* **รอบที่ 3 (ตรวจเสาที่ 3 - Skills & Spells):**
  > *"ตรวจสอบเฉพาะเสาหลักที่ 3 (Skill, Spell & Combat Phrases) แปลชื่อสกิลสั้นเป็นวลีสั้น 2-6 พยางค์ ทับศัพท์ชื่อเฉพาะ และบังคับใช้บัญชีดำห้าม Strike=นัดหยุดงาน, Cast=หล่อโลหะ"*
* **รอบที่ 4 (ตรวจเสาที่ 4 - Items & Firearms):**
  > *"ตรวจสอบเฉพาะเสาหลักที่ 4 บังคับใช้กฎชื่อปืนต้องคงรหัสสากล (M60, M4A1) ห้ามทับศัพท์ไทย และแยกแยะคำว่า Checkpoint (เซฟเกม=เช็คพอยท์ vs ด่านตรวจทหาร=ด่านตรวจ)"*
* **รอบที่ 5 (ตรวจเสาที่ 5 - Quest Consistency):**
  > *"ตรวจสอบเฉพาะเสาหลักที่ 5 เช็คชื่อเควสต์ระหว่าง Title, Objective, Log ให้ตรงกัน 100%"*
* **รอบที่ 6 (ตรวจเสาที่ 6 - Dialogue Leaks & Typography):**
  > *"ตรวจสอบเฉพาะเสาหลักที่ 6 ค้นหาบทพูดที่หลงแปล ค้างภาษาอังกฤษ หรือหลุด CJK พร้อมรักษารหัสแท็กโค้ดเกมให้ครบถ้วน 100%"*
* **รอบที่ 7 (ตรวจเสาที่ 7 - Codex & Lore):**
  > *"ตรวจสอบเฉพาะเสาหลักที่ 7 ขัดเกลาภาษาเอกสาร หนังสือ จารึกโบราณ ให้สละสลวยตามวรรณศิลป์ ห้ามย่อความเด็ดขาด"*
* **รอบ Final (รวมและส่งมอบ):**
  > *"สรุปผลการตรวจแก้ทั้ง 7 เสา และส่งมอบตารางบทแปลฉบับสมบูรณ์ (CSV Schema เดิม) พร้อมใช้งาน"*
"""
        return prompt


    @classmethod
    def generate_master_prompt(cls, project, mode="agent", options=None, app_lang="th", selected_font=None, prompt_type="master"):
        """Main entry point for Master Prompt generation across all modes and types."""
        if prompt_type == "media_kit" or mode == "media_kit":
            return cls.get_media_kit_prompt(project, app_lang=app_lang)
        if prompt_type == "bible" or mode == "bible":
            return cls.get_bible_prompt(project, mode=mode, options=options, app_lang=app_lang, selected_font=selected_font)
        if prompt_type == "persona":
            return cls.get_persona_prompt(project, mode=mode, options=options, app_lang=app_lang)
        if prompt_type == "continue":
            from core.mod_adoption_service import ModAdoptionService
            return ModAdoptionService.generate_continuation_ai_prompt(project, mode=mode)
        if prompt_type == "translate":
            return cls.get_agent_translation_prompt(project, mode=mode, options=options, app_lang=app_lang)
        if prompt_type == "step4":
            return cls.get_step_prompt(project, step_index=4, mode=mode, options=options, app_lang=app_lang, selected_font=selected_font)
        if mode in ("chat", "consultant"):
            return cls.get_chat_prompt(project, app_lang=app_lang, selected_font=selected_font)
        else:  # agent / operation / tstudio_bridge
            return cls.get_agent_prompt(project, options=options, app_lang=app_lang, selected_font=selected_font)

    @classmethod
    def get_step_prompt(cls, project, step_index=4, mode="agent", options=None, app_lang="th", selected_font=None):
        """Generates a high-precision, focused instruction prompt specifically for one milestone step (1 to 7)."""
        options = options or {}
        name = project.get("name", "Unknown Game")
        safe_name = re.sub(r'_+', '_', "".join(c if c.isalnum() or c in (" ", "_", "-") else "_" for c in name).strip().replace(" ", "_")).strip('_')
        path = project.get("path", "")
        game_dir = project.get("game_dir", "[Game directory not specified]")
        is_en = (app_lang != "th")

        engine_info = EngineScanner.detect_engine(
            game_dir=project.get("game_dir", ""),
            workspace_dir=path,
            title=name,
            saved_engine=project.get("engine")
        )
        engine_name = engine_info.get("badge", "Unknown Engine")
        is_unity = "unity" in (engine_name or "").lower()
        is_ue = any(k in (engine_name or "").lower() for k in ["unreal", "ue3", "ue4", "ue5", "udk"])

        font_name = "LINE Seed Sans TH"
        if selected_font and isinstance(selected_font, dict):
            f_id = selected_font.get("id")
            if f_id:
                font_name = f_id

        if step_index == 1:
            if is_en:
                return f"""### STEP 1: ASSET DECOMPILATION, ENGINE DETECTION & FORMAT ANALYSIS
Target Game: {name} | Engine: {engine_name} | Workspace: {path}
Game Directory: {game_dir}

DIRECTIVE & TASKS:
1. DEEP FILE SCANNING:
   - Scan `{game_dir}` to confirm directory structure, asset bundles, and main executables.
   - Identify text containers (.json, .locres, .pak, .assets, .bin, .str, or proprietary archives).
   - Detect binary encoding (UTF-8, UTF-8 BOM, UTF-16LE, CP874).

2. KNOWLEDGE BASE CONSULTATION:
   - Search {KNOWLEDGE_DIR} and GitHub: {GITHUB_KB_URL} for existing Bibles or format unpackers.
   - Query keywords: `{name}`, `{engine_name}`, text extensions.

3. DECLARE APPROACH:
   - Approach A (Parseable): Write parser plugin for TStudio.
   - Approach B (Heavy Archive): Write unpacker/packer CLI scripts in `05_Scripts_and_Tools/`.
   - Store all raw dump files in `01_Original_Backup/raw_dump/`."""
            else:
                return f"""### ขั้นตอนที่ 1: วิเคราะห์ไฟล์เกม แกะโครงสร้าง และค้นหาคัมภีร์ (Step 1 Protocol)
เป้าหมายเกม: {name} | Engine: {engine_name} | Workspace: {path}
ไดเรกทอรีเกม: {game_dir}

คำสั่งปฏิบัติการ (Directives):
1. ตรวจสอบโครงสร้างไฟล์และเอนจินเกม:
   - ตรวจสอบโฟลเดอร์ติดตั้งเกม `{game_dir}` เพื่อระบุประเภทไฟล์ข้อความ (.pak, .assets, .locres, .json, .bin)
   - วิเคราะห์ Encoding ของไฟล์ (UTF-8, UTF-8 BOM, UTF-16LE หรือ ANSI)
   - สำรวจตัวเข้ารหัสหรือระบบบีบอัดไฟล์ (เช่น Oodle, LZ4, Zlib, AssetBundle)

2. สแกนคลังความรู้ Modding-Knowledge:
   - ตรวจสอบคู่มือและคัมภีร์ใน `{KNOWLEDGE_DIR}` และ GitHub: `{GITHUB_KB_URL}`
   - ค้นหาด้วยคำสำคัญ: `{name}`, `{engine_name}` หรือนามสกุลไฟล์
   - หากพบคัมภีร์ ให้ปฏิบัติตามโครงสร้างที่บันทึกไว้ 100%

3. ประกาศแนวทาง (Approach A หรือ B):
   - Approach A: เขียน Parser สำหรับไฟล์เปิด (.json, .csv, .locres)
   - Approach B: เขียน Unpacker/Packer CLI ลงใน `05_Scripts_and_Tools/` สำหรับไฟล์บีบอัด
   - ให้สำรองไฟล์ต้นฉบับลงใน `01_Original_Backup/raw_dump/` เสมอ"""

        elif step_index == 2:
            mcp_instruction = "• เปิดใช้ Unity Native Font MCP Server เพื่อฝัง TextMeshPro Atlas พร้อม PUA Offset (+160 units)" if is_unity else "• เตรียมฟอนต์ TTF/OTF และทำตาราง Glyph Mapping"
            if is_en:
                return f"""### STEP 2: THAI PUA FONT SETUP & NATIVE MCP BRIDGE
Target Game: {name} | Engine: {engine_name} | Active Font: {font_name}

DIRECTIVE & TASKS:
1. THAI FONT DEPLOYMENT:
   - Deploy `{font_name}` with full PUA 2,208 glyph set into `{path}/03_Font_and_UI/`.
   - Generate `Mapping.json` and `thai_font_mapper.py` for automated PUA vowel/diacritic shifting.

2. MCP & ENGINE BRIDGE:
   {mcp_instruction}
   - Configure project `mcp_config.json` in workspace root.
   - Ensure upper vowels (อิ, อี, อึ, อื) and tone marks (่, ้,๊, ๋) have proper vertical clearance (+160 units).

3. READ-BACK TEST:
   - Run a test render on sample Thai phrases: "ที่นี่มี ป่าไม้ร่มรื่น", "ต้นน้ำลำธาร", "ผู้กล้าแห่งดินแดน"."""
            else:
                return f"""### ขั้นตอนที่ 2: ติดตั้งฟอนต์ไทย PUA & เชื่อมต่อ MCP Native Bridge (Step 2 Protocol)
เป้าหมายเกม: {name} | Engine: {engine_name} | ฟอนต์ที่เลือก: {font_name}

คำสั่งปฏิบัติการ (Directives):
1. ติดตั้งชุดฟอนต์ไทย PUA 2,208 Glyphs:
   - ติดตั้ง `{font_name}` ลงใน `{path}/03_Font_and_UI/`
   - เตรียมสคริปต์ `thai_font_mapper.py` และ `Mapping.json` สำหรับแปลงรหัสสระ-วรรณยุกต์ลอย/จม
   - กำหนดระยะยกวรรณยุกต์และสระบน (+160 units) ป้องกันวรรณยุกต์ชนสระ

2. เชื่อมต่อเครื่องมือเฉพาะ Engine (MCP Bridge):
   {mcp_instruction}
   - ตรวจสอบการลงทะเบียนใน `mcp_config.json` ให้เครื่องมือ `scan_unity_font_references` หรือ `transplant_native_font` พร้อมทำงาน

3. ทดสอบการแสดงผลฟอนต์ (Font Verification):
   - ทดสอบพิมพ์ประโยคภาษาไทยที่มีสระซ้อน: "ที่นี่มี ป่าไม้ร่มรื่น", "ผู้ยิ่งใหญ่", "ติดตั้งสำเร็จ"
   - ยืนยันว่าไม่มีสี่เหลี่ยม □ หรือปัญหาตัวอักษรกลายเป็นเครื่องหมายคำถาม ?"""

        elif step_index == 3:
            if is_en:
                return f"""### STEP 3: PRE-TRANSLATION GLOSSARY & KEYWORD EXTRACTION
Target Game: {name} | Engine: {engine_name}

DIRECTIVE & TASKS:
1. EXTRACT GAME TERMINOLOGY:
   - Extract character names, locations, skills, weapons, and UI terms.
   - Scan dialogue scripts and item tables.

2. BUILD GLOSSARY STRUCTURE:
   - Save to: `{path}/02_Translation_Workspace/pre_glossary.json`
   - Include schema: {{ "term": "...", "thai_translation": "...", "category": "character|place|item|ui", "context": "..." }}

3. ALIGNMENT & CONSISTENCY:
   - Ensure weapon and real-world acronyms remain standardized (e.g. M60, M4A1, RPG-7).
   - Establish consistent character pronouns before proceeding to batch translation."""
            else:
                return f"""### ขั้นตอนที่ 3: สกัดคำศัพท์เฉพาะ Pre-Glossary & บันทึกพจนานุกรมเกม (Step 3 Protocol)
เป้าหมายเกม: {name} | Engine: {engine_name}

คำสั่งปฏิบัติการ (Directives):
1. สแกนคำศัพท์เฉพาะและชื่อตัวละคร:
   - สกัดชื่อตัวละคร, สถานที่, ชื่อเควสต์, ไอเทม, อาวุธ และเมนู UI
   - ค้นหาคำที่ปรากฏซ้ำบ่อยในบทสนทนา

2. จัดทำโครงสร้างพจนานุกรม (Glossary):
   - บันทึกลงใน: `{path}/02_Translation_Workspace/pre_glossary.json`
   - โครงสร้าง: {{ "term": "คำอังกฤษ", "thai_translation": "คำแปลไทย", "category": "หมวดหมู่", "notes": "หมายเหตุ" }}

3. ควบคุมความเป็นเอกภาพของคำศัพท์:
   - บังคับคงชื่อปืนและรหัสมาตรฐานสากล (เช่น M60, M4A1, RPG, MP5)
   - กำหนดสรรพนามตัวละครหลักและตัวละครรองให้สอดคล้องกันทั้งเกม"""

        elif step_index == 4:
            unity_deep = """• เจาะลึก Asset ใน Unity (Zero-Omission Scan):
     - สแกน StreamingAssets/ (AssetBundles, Addressables)
     - สแกน resources.assets, sharedassets*.assets, globalgamemanagers
     - สแกน MonoBehaviour serialized objects (ScriptableObjects, DialogueTrees, StringTables)
     - สแกน Unity Localization Package (StringTable) และ I2 Localization
     - สแกน IL2CPP metadata (global-metadata.dat) หากมีข้อความฝังในโค้ด C#""" if is_unity else "• สแกนและแตกข้อความทั้งหมดออกจากแพ็กเกจเกมให้ครบ 100% ห้ามตกหล่น"

            if is_en:
                return f"""### STEP 4: DEEP TEXT EXTRACTION, CONSOLIDATED 2-FILE WORKSPACE & POC VERIFICATION
Target Game: {name} | Engine: {engine_name} | Workspace: {path}

DIRECTIVE & TASKS:
1. DEEP ZERO-OMISSION SCAN:
   {unity_deep}
   - Extract 100% of game dialogues, menus, subtitles, and system prompts.

2. STRICT TWO-FILE WORKSPACE ARCHITECTURE:
   - Output directly to `{path}/02_Translation_Workspace/`
   - The workspace root MUST strictly contain ONLY 2 files:
     1. `en_original.json` (or .csv): Untouched English master baseline (Single Source of Truth, Read-only).
     2. `translate_TH.json` (or .csv): Thai translation target formatted for TStudio and batch translation.
   - QUARANTINE / SAFETY RULE: Move all raw dump test files and slices to:
     `{path}/01_Original_Backup/raw_dump/` or `{path}/02_Translation_Workspace/_archive_test/`
     Do NOT scatter test fragments in the workspace root.

3. PROOF OF CONCEPT (POC) VERIFICATION GATE:
   - Extract and translate Main Menu strings (~5-20 lines: Play, Settings, Continue, Quit).
   - Patch into game via `{path}/04_Packed_Mod/` or direct game root.
   - Instruct user to launch game and verify that Thai vowels and tone marks render without boxes or overlap."""
            else:
                return f"""### ขั้นตอนที่ 4: สกัดข้อความเกมทั้งหมด & สร้าง 2 ไฟล์มาตรฐาน (en_original + translate_TH)
เป้าหมายเกม: {name} | Engine: {engine_name} | Workspace: {path}

คำสั่งปฏิบัติการ (Directives):
1. การสกัดข้อความแบบเจาะลึก (Deep Extraction Protocol):
   {unity_deep}
   - สกัดข้อความบทพูด เมนู เควสต์ คำอธิบายไอเทม ออกมาให้ครบถ้วน 100% ห้ามตกหล่น

2. กฎเหล็ก 2 ไฟล์มาตรฐานใน 02_Translation_Workspace (Two-File Architecture):
   - โฟลเดอร์ `{path}/02_Translation_Workspace/` จะต้องมีเพียง 2 ไฟล์หลักนี้เท่านั้น:
     1. `en_original.json` (หรือ .csv): ไฟล์ภาษาอังกฤษต้นฉบับสมบูรณ์ 100% ห้ามแก้ไขเด็ดขาด (Single Source of Truth)
     2. `translate_TH.json` (หรือ .csv): ไฟล์สำหรับนำไปแปลภาษาไทยและเปิดใน TStudio / TRun
   - กฎความปลอดภัย (Safety Quarantine):
     * ไฟล์แกะทดสอบ, slices, และ raw dump ทั้งหมด ให้ย้ายไปเก็บที่ `{path}/01_Original_Backup/raw_dump/` หรือ `{path}/02_Translation_Workspace/_archive_test/`
     * ห้ามลบทิ้ง และห้ามวางไฟล์กระจัดกระจายในโฟลเดอร์ 02_Translation เด็ดขาด

3. ทดสอบ POC หน้าเมนูหลัก (Proof of Concept Gate):
   - ดึงและแปลเฉพาะคำสั่งหน้า Main Menu (Play -> เล่นเกม, Settings -> ตั้งค่า, Quit -> ออกเกม)
   - แพตช์ไฟล์ทดสอบเข้า `{path}/04_Packed_Mod/` เพื่อเปิดเกมจริง
   - ยืนยันว่าสระไม่จม วรรณยุกต์ไม่ลอย ตัวหนังสือไม่เป็นสี่เหลี่ยม □ ก่อนส่งไฟล์ทั้งโปรเจกต์ให้แปลต่อ"""

        elif step_index == 5:
            if is_en:
                return f"""### STEP 5: TAG SHIELDING, ESCAPING & TEXT SANITIZATION
Target Game: {name} | Engine: {engine_name}

DIRECTIVE & TASKS:
1. CODE TAG SHIELDING:
   - Identify format placeholders: `%s`, `%d`, `{{0}}`, `<color=#FF0000>`, `\\n`, `\\r`.
   - Ensure translator engines or AI loops NEVER translate or remove these tags.

2. ESCAPING & CLEANING:
   - Sanitize double quotes and escape characters in JSON/CSV.
   - Write a validation script in `05_Scripts_and_Tools/validate_tags.py` to compare `translate_TH` against `en_original`.

3. VERIFY 100% INTEGRITY:
   - Confirm tag count parity between original and translated strings."""
            else:
                return f"""### ขั้นตอนที่ 5: ป้องกัน Tag โค้ด & Clean Text (Step 5 Protocol)
เป้าหมายเกม: {name} | Engine: {engine_name}

คำสั่งปฏิบัติการ (Directives):
1. ตรวจจับและล็อก Tag โค้ดของเกม:
   - ปกป้องตัวแปรระบบ: `%s`, `%d`, `{{0}}`, `{player_name}`, `<color=...>`, `\\n`, `\\r`
   - บังคับห้ามแปลหรือลบแท็กเหล่านี้โดยเด็ดขาด

2. ตรวจสอบ Escape Characters และโครงสร้างไฟล์:
   - ป้องกันเครื่องหมายคำพูดซ้อน `"` ใน JSON หรือ Comma ใน CSV
   - เขียนสคริปต์ตรวจสอบความปลอดภัยใน `05_Scripts_and_Tools/validate_tags.py`

3. ตรวจสอบความเท่ากันของ Tag (Tag Parity Check):
   - เช็กว่าจำนวนแท็กใน `translate_TH` ตรงกับ `en_original` ครบทุกประโยคก่อนแพ็กเข้าเกม"""

        elif step_index == 6:
            if is_en:
                return f"""### STEP 6: BATCH TRANSLATION HANDOFF, SKILL LOCALIZATION & PERSONA QA
Target Game: {name} | Engine: {engine_name}

DIRECTIVE & TASKS:
1. HANDOFF TO TSTUDIO / TRUN & 100% LINE-BY-LINE PROCESSING:
   - Open `translate_TH.json` or `translate_TH.csv` in TStudio.
   - Run batch translation with selected LLM profile.
   - 🛑 MANDATORY: Process every single line thoroughly without skipping or omitting any strings!

2. SKILL, SPELL & COMBAT PHRASE LOCALIZATION PROTOCOL:
   - Research game lore, class mechanics, elements, and animations thoroughly before translating.
   - For fantasy skills (1-3 English words), translate into concise, punchy Thai compound phrases (2-6 syllables, e.g. 'ดาบเพลิงพิฆาต', 'ระบำเงา', 'ศรวายุ', 'ทัณฑ์เทวา') instead of robotic literal translations.
   - For proper nouns, mythical entities, or untranslatable jargon, use standard transliteration (ทับศัพท์, e.g. Ragnarok -> แร็กนาร็อค, Gungnir -> กุงเนียร์, Overdrive -> โอเวอร์ไดรฟ์).
   - Enforce anti-MT blacklist: Checkpoint -> Context-aware: เช็คพอยท์ for save mechanics (NEVER จุดตรวจ) vs ด่านตรวจ for military/police outposts (NEVER เช็คพอยท์), Strike -> ฟาดฟัน (NEVER นัดหยุดงาน), Cast -> ร่าย (NEVER หล่อ/คัดเลือก), Cooldown -> คูลดาวน์ (NEVER เย็นลง), Passive -> สกิลติดตัว (NEVER เฉยชา), Critical -> คริติคอล (NEVER วิกฤต).

3. PERSONA & PRONOUN QA AUDIT:
   - Verify speech tones match character personas (heroic, casual, villainous, military).
   - Ensure consistent pronouns (ฉัน, ผม, ข้า, เจ้า, นาย).
   - Audit untranslated keys, empty strings, and CJK residue."""
            else:
                return f"""### ขั้นตอนที่ 6: แปลภาษาแบบ Batch, พิธีสารแปลสกิล & ตรวจ QA บทพูด (Step 6 Protocol)
เป้าหมายเกม: {name} | Engine: {engine_name}

คำสั่งปฏิบัติการ (Directives):
1. ส่งไฟล์เข้าสู่ TStudio / TRun & กฎเหล็กอ่านครบทุกประโยค 100%:
   - เปิดไฟล์ `translate_TH.json` หรือ `translate_TH.csv` ใน TStudio
   - รันการแปลแบบ Batch ด้วยโปรไฟล์ AI ที่ตั้งค่าไว้
   - 🛑 กฎเหล็ก: ระบบต้องอ่าน ตรวจสอบ และแปล "ทุกประโยค ทุกบรรทัด 100%" ห้ามทำข้ามๆ หรือละเว้นเด็ดขาด

2. พิธีสารการแปลสกิล เวทมนตร์ วลี และทักษะการต่อสู้ (Skill Localization Protocol):
   - ต้องสืบค้นบริบท ธีมเกม คลาส และเอฟเฟกต์สกิลอย่างละเอียดก่อนแปล ห้ามแปลเดาสุ่ม
   - หากเป็นเกมแฟนตาซีและชื่อสกิลไม่ยาวเกินไป (1-3 คำ) ให้แปลเป็น "วลีสั้นๆ 2-6 พยางค์" ที่สละสลวย (เช่น "ดาบเพลิงพิฆาต", "ระบำเงา", "ศรวายุ", "อสุนีบาตฟาด", "ทัณฑ์เทวา") แทนการแปลยาวทื่อๆ คำต่อคำ
   - หากเป็นคำเฉพาะ ชื่อเฉพาะ หรือศัพท์เฉพาะที่หาคำแปลตรงตัวไม่ได้ ให้ใช้ "การทับศัพท์" (เช่น "แร็กนาร็อค", "กุงเนียร์", "โอเวอร์ไดรฟ์", "ฟิเรก้า") ห้ามแปลแถไปเรื่อยจนความหมายเพี้ยน
   - บัญชีดำคำแปลกลไกผิด: Strike = ฟาดฟัน (ห้าม นัดหยุดงาน), Cast = ร่าย (ห้าม หล่อ/คัดเลือก), Cooldown = คูลดาวน์ (ห้าม เย็นลง), Checkpoint = แยกบริบท: เช็คพอยท์ สำหรับระบบเซฟ (ห้าม จุดตรวจ) / ด่านตรวจ สำหรับด่านทหาร-ตำรวจ (ห้าม เช็คพอยท์), Passive = สกิลติดตัว (ห้าม เฉยชา), Critical = คริติคอล (ห้าม วิกฤต), Lifesteal = ดูดเลือด (ห้าม ขโมยชีวิต), Respawn = เกิดใหม่ (ห้าม วางไข่)

3. ตรวจสอบสำนวน สรรพนาม และบทพูดหลงแปล (Persona, Pronoun & Dialogue QA):
   - ตรวจสอบอารมณ์และบุคลิกตัวละครให้ตรงตามบริบท
   - ตรวจความสม่ำเสมอของสรรพนาม (ฉัน/ผม/ข้า/ท่าน/นาย)
   - ตรวจสอบคำแปลตาม `pre_glossary.json` และกวาดตรวจหาประโยคภาษาอังกฤษหรือ CJK ที่ตกหล่น"""

        elif step_index == 7:
            bible_info = cls.get_bible_info(engine_name, safe_name, workspace_path=path)
            bible_spec = cls._build_bible_specification_block(bible_info, name, engine_name, path, is_en=is_en)
            if is_en:
                return f"""### STEP 7: BUILD RELEASE, INSTALLATION GUIDE & MODDING BIBLE SYNC
Target Game: {name} | Engine: {engine_name} | Workspace: {path}

DIRECTIVE & TASKS:
1. PACK DISTRIBUTION BUILD:
   - Pack mod into `{path}/06_Releases/{name}_ThaiMod_v1.0/`.
   - Setup structure for direct game-root copy-paste installation.

2. GENERATE INSTALLATION GUIDE:
   - Create `{path}/06_Releases/{name}_ThaiMod_v1.0/คู่มือติดตั้ง_README.txt`.
   - Include clear step-by-step install and uninstall instructions.

3. WRITE TECHNICAL BIBLE & SYNC TO MODDING-KNOWLEDGE:
{bible_spec}
   - Document all 10 technical categories in `{bible_info['filename']}`.
   - Copy real font files and update `{bible_info['full_path']}`."""
            else:
                return f"""### ขั้นตอนที่ 7: Build Release, จัดทำคู่มือติดตั้ง & บันทึกคัมภีร์ลง Modding-Knowledge
เป้าหมายเกม: {name} | Engine: {engine_name} | Workspace: {path}

คำสั่งปฏิบัติการ (Directives):
1. แพ็กไฟล์ม็อดฉบับสมบูรณ์ (Distribution Build):
   - บิลด์ไฟล์ม็อดลงใน `{path}/06_Releases/{name}_ThaiMod_v1.0/`
   - จัดโครงสร้างให้ผู้เล่นสามารถ Copy วางทับลงโฟลเดอร์เกม `{game_dir}` ได้ทันทีแบบ 1 คลิก

2. จัดทำคู่มือติดตั้ง (คู่มือติดตั้ง_README.txt):
   - เขียนวิธีติดตั้งและวิธีถอนการติดตั้งอย่างละเอียด
   - บันทึกจำนวนประโยคที่แปลและเครดิตผู้จัดทำ

3. เขียนคัมภีร์เทคนิค & ซิงค์เข้า Modding-Knowledge (Global Rule):
{bible_spec}
   - บันทึกคัมภีร์ 10 หมวดหมู่ลงใน `{bible_info['filename']}`
   - ซิงค์เข้า `{KNOWLEDGE_DIR}` และคัดลอกไฟล์ฟอนต์จริงเข้าสู่โฟลเดอร์ Assets/Fonts/ ทันที"""

        return cls.generate_master_prompt(project, mode=mode, options=options, app_lang=app_lang, selected_font=selected_font)



    @classmethod
    def generate_ai_logo_prompt_content(cls, game_name, engine_name="Custom Engine"):
        """Generates a comprehensive AI Logo Generation & Branding Guide markdown for 07_Image_Resources/Generated_Logo/AI_Logo_Prompt.md."""
        gn_lower = game_name.lower()
        eng_lower = engine_name.lower()

        # Infer thematic art direction
        if any(w in gn_lower for w in ["horror", "resident", "evil", "silent", "fear", "vampyr", "blood", "dead", "dark"]):
            theme_name = "Dark Gothic / Psychological Horror"
            texture_desc = "distressed scratched steel with dried crimson blood splatters, ancient weathered decrepit wood, eerie sinister vignette"
            colors = "Obsidian Black, Blood Crimson, Ash Gray, Pale Bone White"
            lighting = "Moody low-key cinematic lighting, sharp crimson backlight rim"
        elif any(w in gn_lower for w in ["cyber", "deus", "wars", "star", "space", "mecha", "future", "helldivers", "outpost", "infinite"]):
            theme_name = "Futuristic Sci-Fi / Cybernetic"
            texture_desc = "hard surface chamfered titanium chrome with glowing cyan-amber circuit lines, subtle chromatic aberration and lens flare"
            colors = "Graphite Grey, Neon Cyan, Warning Amber, High-tech Laser Blue"
            lighting = "Volumetric neon rim light, sharp specular metallic reflections"
        elif any(w in gn_lower for w in ["dragon", "witcher", "atelier", "story of seasons", "harvest", "fantasy", "sword", "magic", "epic", "doraemon", "reincarnation"]):
            theme_name = "High Fantasy / Epic Adventure"
            texture_desc = "ancient mystical chiseled stone with deep gold filigree inlay, subtle radiant elemental rune glow, polished bronze bevel"
            colors = "Royal Gold, Deep Rune Azure, Imperial Crimson, Weathered Granite"
            lighting = "Warm heroic cinematic key light with mystical ethereal aura"
        else:
            theme_name = "Cinematic Action / Modern Adventure"
            texture_desc = "heavy 3D beveled industrial alloy, high contrast metallic finish with brushed texture, subtle distress edges"
            colors = "Titanium Silver, High-impact Orange, Deep Charcoal, Electric Blue"
            lighting = "Dramatic high-contrast rim lighting, cinematic 3D depth"

        return f"""# 🎨 AI Logo & Branding Design Prompt: {game_name}
### คู่มือและชุดคำสั่ง Prompt สำหรับสร้าง "โลโก้ชื่อเกมภาษาไทย" และสื่อประชาสัมพันธ์ (หน๊ด หนวด translator)

เอกสารนี้รวบรวมคำสั่ง Prompt คุณภาพสูงสำหรับนำไปใช้กับ AI สร้างภาพ (**Midjourney v6.1**, **FLUX.1**, **Stable Diffusion / ComfyUI**, **DALL-E 3**) เพื่อสร้าง **"โลโก้ชื่อเกมภาษาไทย" (Thai Stylized Game Title Logo)** ที่ถอดรหัส Art Direction, Lighting, และ Texture จากเกมต้นฉบับ สำหรับนำมาประกอบลงใน PSD Templates ใน `07_Image_Resources/`

---

## 1. ข้อมูลอัตลักษณ์ทางศิลป์ของเกม (Game Visual DNA)
- **ชื่อเกมภาษาอังกฤษ:** {game_name}
- **Engine สถาปัตยกรรม:** {engine_name}
- **ธีมและอารมณ์ศิลป์ (Theme & Atmosphere):** {theme_name}
- **โทนสีหลัก (Color Palette):** {colors}
- **พื้นผิวและเอฟเฟกต์ (Material & Texture):** {texture_desc}
- **การจัดแสง (Lighting):** {lighting}

### 💡 แนวคิดชื่อเกมภาษาไทย (Thai Title Concepts):
> แนะนำให้นำชื่อที่ถูกใจไปใส่แทนที่คำว่า `[THAI_TITLE]` ในกล่อง Prompt ด้านล่างนี้:
1. **แบบทับศัพท์หนักแน่น:** `{game_name}` (สลักตัวอักษรไทยสไตล์โมเดิร์น)
2. **แบบแปลความหมายแฟนตาซี/ไซไฟ:** `[ระบุชื่อไทยที่สอดคล้องกับเนื้อเรื่อง เช่น มังกรทมิฬกลืนพิภพ / อภินิหารตำนานดาบ]`
3. **แบบสั้นกระชับติดหู:** `[ชื่อย่อ 2-4 พยางค์สำหรับวางคู่กับโลโก้ภาษาอังกฤษ]`

---

## 2. ชุดคำสั่งสร้างภาพโลโก้ (Ready-to-Use Image Prompts)

### 🌟 2.1 Midjourney (v6.1) — แนะนำสูงสุดสำหรับงาน Typography & Logo
> **วิธีใช้:** คัดลอกข้อความในกล่องโค้ดด้านล่างนี้ ไปวางใน Discord ช่องสั่งงาน Midjourney

```text
/imagine prompt: professional cinematic video game title logo typography, modern stylized 3D typography reading "[THAI_TITLE]", heavy extruded beveled lettering, {texture_desc}, {lighting}, high contrast, completely isolated on pure solid flat black background, no background elements, no characters, vector graphic design aesthetics, 8k resolution, Unreal Engine 5 visual style --ar 16:9 --v 6.1 --style raw
```

---

### ⚡ 2.2 FLUX.1 (Dev / Schnell) — ทรงพลังด้านรูปทรงตัวอักษรคมชัด
> **วิธีใช้:** ใช้ได้บน Fal.ai, Replicate, หรือ ComfyUI

**Positive Prompt:**
```text
Game logo title typography for "{game_name}", bold 3D extruded lettering reading "[THAI_TITLE]", stylized Thai glyph aesthetics, {lighting}, {texture_desc}, ultra clean sharp edges, centered, completely isolated on solid black background, graphic design masterpiece, cinematic promotional game logo, 8k
```

---

### 🎨 2.3 Stable Diffusion XL (SDXL) / ComfyUI
**Positive Prompt:**
```text
(masterpiece, best quality:1.3), game title logo, bold 3D typography, extruded dimensional letters reading "[THAI_TITLE]", {lighting}, {texture_desc}, (isolated on solid black background:1.4), clean silhouette, vector logo style, sharp focus, volumetric lighting, centered composition, game banner asset, 8k
```

**Negative Prompt (บังคับใส่ในช่อง Negative เสมอ เพื่อให้ได้ภาพไดคัทง่าย):**
```text
(photorealistic humans:1.4), characters, complex background, blurry, noisy, lowres, deformed letters, illegible mess, clutter, watercolor, gradient background, white background, multiple logos, frames, borders, watermark, signature
```

---

### 🤖 2.4 DALL-E 3 (ChatGPT Plus / Bing Image Creator)
```text
Create a high-resolution cinematic 3D video game title logo for "{game_name}". The logo should feature bold, extruded 3D typography reading "[THAI_TITLE]" with an aesthetic matching {theme_name}. The letters should have a material texture of {texture_desc}, accented by {lighting}. Critical requirement: The logo must be perfectly centered and completely isolated on a pure flat solid black background with absolutely no background illustrations, scenery, or characters, making it ready for transparent cutout in Photoshop.
```

---

## 3. ขั้นตอนการนำโลโก้ไปประกอบลงใน PSD Templates (1 คลิกเสร็จ)

1. **บันทึกภาพโลโก้:** เมื่อได้ภาพที่พอใจจาก AI ให้เซฟไฟล์ภาพ (ที่มีพื้นหลังดำสนิท) ไว้ใน:  
   `07_Image_Resources/Generated_Logo/{game_name}_Logo_AI.png`
2. **เปิดไฟล์ Photoshop Templates:** เปิดไฟล์เทมเพลตใน `07_Image_Resources/` เช่น:
   - `Cover_Post facebook.psd` (สำหรับโพสต์รูปประกาศเปิดตัวม็อด)
   - `Header_facebook.psd` (สำหรับแบนเนอร์ปกเพจ)
   - `cover 16-9.psd` (สำหรับหน้าปกหลักอัตราส่วน 16:9)
3. **เทคนิคการตัดพื้นหลังสีดำใน Photoshop (ไม่ต้องไดคัทให้เมื่อย):**
   - **วิธีที่ 1 (Blend Mode Screen):** ลากภาพโลโก้เข้ามาวางบนเลเยอร์บนสุด แล้วเปลี่ยน Blending Mode เป็น **Screen** — พื้นหลังสีดำจะหายไปทันที เหลือเฉพาะเนื้อโลโก้และแสงเรือง
   - **วิธีที่ 2 (Color Range / Select Subject):** ไปที่เมนู `Select > Color Range` จิ้มสีดำแล้วกด Invert เพื่อเลือกเฉพาะตัวอักษร จากนั้นกด Add Layer Mask
4. **วางภาพฉากหลัง Official Art:** ดึงภาพพื้นหลังความละเอียดสูงจาก:  
   `07_Image_Resources/Official_Art/banner_hero_1920x620.jpg` หรือ `cover_portrait_600x900.jpg` มาวางเป็นแบ็คกราวด์ด้านหลัง
5. **บันทึกภาพพร้อมแจกจ่าย:** เมื่อจัดวางเสร็จแล้ว ให้กด Export เป็น `.png` หรือ `.jpg` แล้วเซฟไว้ใน:  
   `07_Image_Resources/Final_Exports/` พร้อมนำไปโพสต์ลงเพจ **"หน๊ด หนวด translator"** ได้ทันที!
"""


    @classmethod
    def get_agent_translation_prompt(cls, project, mode="agent", options=None, app_lang="th", **kwargs):
        """
        Generates the specialized Autonomous AI Agent Local Translation Suite prompt.
        Translates entire project text files locally using the Agent's own CLI/subscription quota (zero external API/Web).
        Strictly enforces TStudio Glossary & System Prompt.
        If missing, halts execution and instructs user to create them in TStudio first.
        """
        import re
        game_name = project.get("name", "Unknown Game")
        engine_name = project.get("engine") or project.get("engine_badge") or "Custom Engine"
        ws_path = project.get("path", "")

        # Dynamic Workspace Scan: Detect text files (safe shallow scan)
        detected_text_files = []
        if ws_path and os.path.exists(ws_path):
            target_dirs = [
                os.path.join(ws_path, "02_Translation_Workspace"),
                os.path.join(ws_path, "03_Translated_Text"),
                os.path.join(ws_path, "02_Extracted_Text"),
            ]
            seen_files = set()
            for d in target_dirs:
                if not os.path.exists(d):
                    continue
                for root, _, files in os.walk(d):
                    if len(detected_text_files) >= 50:
                        break
                    if any(x in root for x in ["03_tools", "tools", ".git", "__pycache__", "07_Image_Resources", "01_Original_Files", "bin", "obj", "DerivedDataCache"]):
                        continue
                    for f in files:
                        f_lower = f.lower()
                        if f_lower.endswith((".csv", ".tsv", ".txt", ".locres.csv", ".json", ".ini", ".int", ".po", ".xml")):
                            rel_p = os.path.relpath(os.path.join(root, f), ws_path).replace("\\", "/")
                            if rel_p not in seen_files:
                                seen_files.add(rel_p)
                                detected_text_files.append(rel_p)
                                if len(detected_text_files) >= 50:
                                    break
            # If still empty, check top-level of ws_path only (non-recursive)
            if not detected_text_files and os.path.isdir(ws_path):
                try:
                    for f in os.listdir(ws_path):
                        f_lower = f.lower()
                        if f_lower.endswith((".csv", ".tsv", ".txt", ".json", ".ini")):
                            detected_text_files.append(f)
                except Exception:
                    pass

        target_demo_file = detected_text_files[0] if detected_text_files else "02_Translation_Workspace/Game_Text.csv"
        file_list_str = "\n".join(f"  - `{f}`" for f in detected_text_files[:10]) if detected_text_files else "  - (ยังไม่พบไฟล์ข้อความในโฟลเดอร์ 02_Translation_Workspace)"
        if len(detected_text_files) > 10:
            file_list_str += f"\n  - ... และไฟล์อื่นๆ อีก {len(detected_text_files) - 10} ไฟล์"

        has_profile, has_glossary, has_prompt, prof = cls.has_tstudio_profile(project)
        preset_name = prof.get("preset_name", game_name)
        system_tone_prompt = prof.get("system_prompt", "").strip()
        project_glossary = prof.get("glossary", {})
        source_desc = prof.get("source_desc", "Default")
        glossary_count = len(project_glossary)

        is_agent_mode = (mode == "agent")

        # =========================================================================
        # GUARDRAIL TRIGGER: IF GLOSSARY OR SYSTEM PROMPT IS MISSING -> HALT
        # =========================================================================
        if not (has_glossary and has_prompt):
            missing_reasons = []
            if not has_glossary:
                missing_reasons.append("❌ ยังไม่พบคลังคำศัพท์ทางการ (Official Glossary) ใน TStudio")
            if not has_prompt:
                missing_reasons.append("❌ ยังไม่พบคำสั่งแนวทางการแปลเฉพาะ (System Tone Directive) ใน TStudio")
            reasons_md = "\n".join(missing_reasons)

            return f"""# 🛑 คำสั่งถูกระงับ: ไม่พบคลังคำศัพท์ (Glossary) หรือ AI Prompt จาก TStudio
========================================================================================
> **ระบบ:** THub AI Helper Copilot — Autonomous Agent Local Translation Suite
> **โปรเจกต์เป้าหมาย:** {game_name} ({engine_name})
> **Workspace Path:** `{ws_path}`
> **สถานะการตรวจสอบ:** ⚠️ ขาดข้อมูลตั้งต้นจาก TStudio สำหรับโปรเจกต์นี้

## 🚨 กฎเหล็กความปลอดภัยขั้นเด็ดขาด (STRICT LOCALIZATION GUARDRAIL):
🛑 **สำหรับ AI Agent (Claude Code / Antigravity / Cursor / Windsurf):**
**ห้ามทำการแปลไฟล์ภาษาไทยเด็ดขาด! และห้ามสร้างคลังคำศัพท์สมมุติขึ้นมาเองโดยพลการ!**

{reasons_md}

ตามมาตรฐานวิศวกรรมการแปลเกมระดับมืออาชีพของ THub:
การแปลภาษาเกมขนาดใหญ่โดยใช้โควต้าของ AI Agent จำเป็นต้องมี **"คลังคำศัพท์ (Glossary)"** และ **"แนวทางการแปล (AI System Prompt)"** 
ที่ผ่านการกำหนดโดยผู้กำกับการแปล (Lead Localization Editor) ใน **TStudio** เสียก่อน
หากปล่อยให้ AI แปลโดยไม่มี Glossary กำกับ จะก่อให้เกิดความเสียหายร้ายแรง:
1. ชื่อตัวละคร, สกิล, และสถานที่ จะถูกแปลสลับไปสลับมาคนละแบบในแต่ละไฟล์
2. สรรพนามจะขัดแย้งและไม่เข้ากับบุคลิกของตัวละคร
3. ศัพท์เฉพาะและชื่อรุ่นอาวุธอาจถูกแปลตรงตัวจนเสียอรรถรส

---

## 📋 คำสั่งที่ AI Agent ต้องปฏิบัติตามทันที:
1. **หยุดการทำงานทันที (HALT EXECUTION):** ห้ามเขียนโค้ดเพื่อแปลไฟล์ ห้ามสร้างไฟล์แปลใหม่ และห้ามดัดแปลงไฟล์ใน `{ws_path}`
2. **รายงานแจ้งเตือนผู้ใช้งานใน Terminal / แชท:**
   > *"⚠️ ระบบระงับการแปลอัตโนมัติสำหรับเกม **{game_name}** เนื่องจากยังไม่มีการสร้าง **คลังคำศัพท์ (Glossary)** และ **AI System Prompt** ในโปรแกรม TStudio"*
   > *"กรุณาเปิดโปรแกรม **TStudio** แล้วกำหนด Glossary (คำศัพท์เฉพาะ) และ System Prompt (โทนเรื่อง) ประจำเกมนี้ก่อน จึงจะสามารถสั่งรันการแปลอัตโนมัติได้"*
3. **แนะนำขั้นตอนแก่ผู้ใช้:**
   - กดปุ่ม **"🚀 เปิด TStudio ตั้งค่า"** ในหน้าต่าง THub AI Helper
   - หรือเปิด TStudio -> เมนู **Project Profile** -> สร้างโปรไฟล์ชื่อ `{game_name}`
   - เพิ่มคำศัพท์หลัก (เช่น ชื่อตัวละคร, ฝ่าย, โลกในเกม) และกำหนด System Prompt
   - บันทึกโปรไฟล์ แล้วกลับมากดสร้าง Prompt ใน THub ใหม่อีกครั้ง
"""

        # =========================================================================
        # FULL AUTONOMOUS AGENT LOCAL TRANSLATION ENGINE (WHEN GLOSSARY & PROMPT EXIST)
        # =========================================================================
        glossary_rows = [f"| `{k}` | **{v}** |" for k, v in project_glossary.items()]
        glossary_table_md = "\n".join([
            "| คำศัพท์ต้นฉบับ (Source Term) | คำแปลทางการประจำเกม (Official Glossary Translation) |",
            "| :--- | :--- |"
        ] + glossary_rows)

        mode_header = "โหมดปฏิบัติการอัตโนมัติ (Autonomous Agent Mode - Claude Code / Antigravity / Cursor)" if is_agent_mode else "โหมดที่ปรึกษาการแปล (Consultant Web Chat Mode - ChatGPT / Claude Web)"

        prompt = f"""# Role & Mission: Autonomous Thai Game Localization Engine (Zero-API / Local Agent Mode)
========================================================================================
> **ระบบ:** THub AI Helper Copilot — Autonomous Agent Local Translation Suite
> **โหมดการทำงาน:** {mode_header}
> **โปรเจกต์เป้าหมาย:** {game_name} ({engine_name})
> **Workspace Path:** `{ws_path}`
> **TStudio Project Profile:** `{preset_name}` ({source_desc})
> **โควต้าการแปล:** ใช้สมองและโควต้าของ AI Agent โดยตรง 100% (Zero External API / Zero Web Calls)

คุณคือหัวหน้านักแปลเกมภาษาไทยระดับอาวุโส (Senior Game Localization Lead)
ได้รับมอบหมายให้ทำหน้าที่แปลไฟล์บทภาษาของเกม **{game_name}** ลงสู่ภาษาไทยฉบับสมบูรณ์แบบระดับ Masterpiece
โดยการทำงานจะ **ไม่พึ่งพา API ภายนอก และไม่ใช้ Web Translator** แต่ใช้ขีดความสามารถ โควต้า และการเขียนสคริปต์ของ AI Agent เองทั้งหมด

---

## 🎭 1. แนวทางและโทนเสียงการแปลทางการจาก TStudio (System Tone Directive)
> ข้อกำหนดด้านบุคลิก โทนเรื่อง และระดับภาษาที่ผู้กำกับการแปลได้ระบุไว้ใน TStudio ประจำโปรเจกต์นี้:

{system_tone_prompt}

---

## 📖 2. คลังคำศัพท์ทางการประจำเกมจาก TStudio (Official Glossary - {glossary_count} รายการ)
> 🛑 **กฎเหล็กข้อบังคับสูงสุด (100% STRICT GLOSSARY ENFORCEMENT):**
> หากมีคำศัพท์ภาษาอังกฤษต่อไปนี้ปรากฏในประโยคต้นฉบับ คุณ **ต้องแปลเป็นภาษาไทยตรงตามตารางนี้เป๊ะ 100%**
> **ห้ามแปลงเป็นคำอื่น ห้ามทับศัพท์แปลกแยก และห้ามคิดคำใหม่ขึ้นมาแทนเด็ดขาด!**

{glossary_table_md}

---

## 🏛️ 3. กฎเกณฑ์การแปลระดับ Master (Core Quality Rules)
1. **ยึดถือ Glossary 100%:** สอดคล้องกับตารางด้านบนทุกคำ ทุกบริบท
2. **รักษาแท็กและโค้ดของเกมครบถ้วน 100% (Strict Tag & Variable Preservation):**
   - รักษารหัสตัวแปร: `{{0}}`, `{{1}}`, `%s`, `%d`, `\\n`, `\\r\\n`, `<color=...>`, `</color>`, `[TAG_NAME]`
   - ห้ามแปลคำข้างในแท็ก หรือทำเครื่องหมายปีกกาหลุดหายเด็ดขาด
3. **สำนวนภาษาไทยธรรมชาติ ไม่แข็งทื่อ (Anti-MT Stiffness / Natural Flow):**
   - แปลงประโยคและสำนวนภาษาอังกฤษให้เป็น "บทพูดที่คนจริงๆ ในสถานการณ์นั้นจะพูดออกมา"
   - ปรับตามระดับอารมณ์และบริบทของเกมตามที่ TStudio System Directive กำหนด
4. **มาตรฐานชื่อปืนและคำศัพท์สากล (Gaming Standard):**
   - ชื่อรุ่นปืนคงรหัสสากลเดิมเสมอ: `M60`, `M4A1`, `AK-47`, `MP5`, `RPG-7`, `Glock 19` (ห้ามทับศัพท์ไทย "เอ็ม 60")
   - **Checkpoint แยกแยะ 2 กรณี:** เซฟเกม/เกิดใหม่/UI = "เช็คพอยท์" (ห้าม "ด่านตรวจ"), ด่านทหาร/ตำรวจในเนื้อเรื่อง = "ด่านตรวจ"

---

## 📂 4. ไฟล์ข้อความที่ตรวจพบใน Workspace:
{file_list_str}
- ไฟล์เป้าหมายสำหรับการแปลรอบแรก: `{target_demo_file}`
"""

        if is_agent_mode:
            prompt += f"""
---

## 🤖 5. พิธีสารการแปลวนลูปอัตโนมัติแบบแบ่งแบทช์ (Autonomous Batch Chunking State Machine)
> **สำหรับ AI Agent (Claude Code / Antigravity / Cursor):**
> 🛑 **กฎเหล็กป้องกัน Token Cutoff และ Context Window ล้น:**
> **ห้ามแปลไฟล์ขนาดใหญ่ทั้งหมดในรอบเดียวเด็ดขาด!** 
> คุณต้องปฏิบัติตาม **State Machine** วนลูปแปลทีละแบทช์ (Batch Size: 60 - 80 แถวต่อรอบ) บันทึกชิ้นส่วนลงดิสก์ แล้วสั่งตัวเองก้าวสู่แบทช์ถัดไปอัตโนมัติ

### 📋 วงจรการทำงานของ State Machine (Step-by-Step Loop):

#### 🚀 ขั้นตอนที่ 0: สำรองไฟล์และตั้งต้นระบบ (Stage 0: INIT & Auto-Backup)
1. ตรวจสอบไฟล์บทแปลเป้าหมาย: `{target_demo_file}`
2. สำรองไฟล์ทันที: `{target_demo_file}.pre_trans_backup.csv`
3. สร้างโฟลเดอร์ `05_Scripts_and_Tools/` และโฟลเดอร์เก็บแบทช์ `05_Scripts_and_Tools/translation_batches/`
4. สร้างไฟล์ควบคุมสถานะ `05_Scripts_and_Tools/translation_state.json`:
   ```json
   {{
     "project": "{game_name}",
     "target_file": "{target_demo_file}",
     "total_rows": 0,
     "batch_size": 75,
     "current_batch": 1,
     "total_batches": 1,
     "completed_batches": [],
     "status": "IN_PROGRESS",
     "started_at": "..."
   }}
   ```

#### ⚙️ ขั้นตอนที่ 1: วนลูปแปลทีละแบทช์ (Autonomous Batch Loop)
1. อ่านข้อมูลแถวที่ `(batch_idx - 1) * 75` ถึง `batch_idx * 75` จากไฟล์ต้นฉบับ
2. ดำเนินการแปลด้วยตนเอง โดยบังคับใช้:
   - **TStudio System Tone Directive**
   - **TStudio Official Glossary**
   - **Tag Preservation 100%**
3. บันทึกผลลัพธ์ของแบทช์ลงไฟล์: `05_Scripts_and_Tools/translation_batches/batch_{{batch_idx}}.csv`
4. อัปเดต `translation_state.json`: บันทึกว่า `batch_{{batch_idx}}` สำเร็จแล้ว และปรับ `current_batch = batch_idx + 1`
5. **สั่งตัวเองเข้าสู่แบทช์ถัดไปทันทีโดยไม่ต้องรอคำสั่งจากผู้ใช้ จนกระทั่งแปลครบทุกแถว 100%**

#### 🏆 ขั้นตอนที่ 2: ประกอบรวมไฟล์และส่งมอบ (Assembly, Verification & Masterpiece Report)
1. นำผลลัพธ์จากทุกแบทช์ `batch_*.csv` มารวมกันตามลำดับแถวเดิม
2. เขียนทับลงในไฟล์บทแปลจริง: `{target_demo_file}` และทำสำเนาไว้ที่ `03_Translated_Text/`
3. บังคับใช้การบันทึกด้วยรหัส `encoding='utf-8-sig'` (UTF-8 with BOM) เสมอ
4. ทำการตรวจสอบความสมบูรณ์ (Verification):
   - ตรวจสอบว่าจำนวนบรรทัดเท่ากับต้นฉบับเดิมเป๊ะ
   - ตรวจสอบว่าไม่มีแท็กเกมหลุดหาย
   - ตรวจสอบว่าศัพท์ใน Glossary ถูกนำไปใช้ครบถ้วน
5. อัปเดต `translation_state.json`: `"status": "COMPLETED"`
6. สร้างเอกสารรายงานสรุป: `05_Scripts_and_Tools/TRANSLATION_COMPLETION_REPORT.md`
7. สรุปความสำเร็จให้ผู้ใช้ทราบใน Terminal / แชท
"""
        else:
            prompt += f"""
---

## 💬 5. แนวทางการแปลสำหรับ Web Chat (Step-by-Step Batch Mode)
> สำหรับผู้ใช้งานใน ChatGPT หรือ Claude Web:
> ให้ส่งข้อความมาให้ AI แปลทีละ 50-70 บรรทัด โดยระบุคำสั่ง:
> *"แปลข้อความภาษาอังกฤษด้านล่างนี้เป็นภาษาไทย โดยยึดถือ TStudio Glossary และแนวทางแปลตามที่ระบุไว้ด้านบน 100% คงแท็ก {{0}}, \\n ไว้ครบถ้วน และส่งมอบในรูปแบบตาราง CSV Schema เดิม:"*
"""
        return prompt

