# -*- coding: utf-8 -*-
"""
Mod Adoption & Restructuring Service (ระบบสานต่องานม็อดเดิมเข้าสู่มาตรฐาน THub)
=============================================================================
Audits, organizes, and adopts legacy or external game localization workspaces into
the standard THub 01–07 structure, and integrates seamlessly with AI Helper.

Key Capabilities:
1. Deep Audit:
   - Scans text files, auto-detects Thai characters to distinguish translated vs original text.
   - Identifies font files, game archives, packed mods, release files, and media.
   - Detects engine signatures and matches Modding Bibles.
   - Calculates existing translation completion percentage and detects glossaries.
2. Safe & Non-Destructive Restructure:
   - In-place restructuring or copy-to-new-workspace.
   - Creates a timestamped snapshot backup before making changes.
   - Normalizes legacy THub folders (e.g. 01_Original_Backup -> 01_Original_Files).
   - Deploys master PSD templates to 07_Image_Resources.
   - Downloads official Steam art & covers.
3. AI Helper Integration:
   - Generates 'AI_Mod_Continuation_Blueprint.md' in the workspace.
   - Produces tailored AI Continuation Prompts for Claude Code / Antigravity / Web Chat.
   - Registers the project into THub.
"""

import os
import uuid
import copy
from core.project_backup import create_snapshot, restore_snapshot, transfer_unique, contained, is_link
from core.safe_io import write_json_atomic, update_json_atomic
import re
import json
import shutil
import datetime
from pathlib import Path

from core.engine_scanner import EngineScanner
from core.knowledge_service import KnowledgeService
from core.project_service import ProjectService
from core.config_manager import ConfigManager
from core.steam_service import SteamService


class ModAdoptionService:
    """Core service for adopting and restructuring legacy/external mod workspaces."""

    VALID_TEXT_EXTS = {
        ".txt", ".json", ".csv", ".tsv", ".locres", ".lang", ".po", ".pot",
        ".msg", ".xml", ".yaml", ".yml", ".ini", ".int", ".strings", ".lua"
    }

    FONT_EXTS = {".ttf", ".otf", ".fnt", ".bmfc", ".woff", ".woff2"}
    ARCHIVE_EXTS = {".pak", ".upk", ".cpk", ".bnd", ".arc", ".toc", ".sb", ".dat", ".bin", ".assets", ".bundle", ".rpa", ".xp3"}
    RELEASE_EXTS = {".zip", ".rar", ".7z", ".exe", ".msi"}
    IMAGE_EXTS = {".psd", ".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tga", ".dds"}

    THAI_PATTERN = re.compile(r'[\u0E00-\u0E7F]')

    def __init__(self, config_manager=None, project_service=None):
        self.cfg = config_manager or ConfigManager()
        self.project_service = project_service or ProjectService(self.cfg)

    @classmethod
    def audit_legacy_folder(cls, folder_path):
        """
        Deep-audits a legacy or external folder to classify files and assess project status.
        Returns a comprehensive dictionary with file counts, detected engine, translation progress,
        and suggested destination mappings.
        """
        folder_path = os.path.normpath(os.path.abspath(folder_path))
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            return {"success": False, "error": f"Folder not found: {folder_path}"}

        folder_name = os.path.basename(folder_path)
        game_title = cls._clean_title_from_folder(folder_name)

        # 1. Detect Game Engine & Knowledge Bible
        engine_info = EngineScanner.detect_engine(workspace_dir=folder_path, title=game_title)
        bible_info = engine_info.get("bible")
        if not bible_info:
            try:
                bible_info = KnowledgeService.find_matching_bible(game_title=game_title, engine_name=engine_info.get("badge"))
            except Exception:
                bible_info = None

        # 2. File Classification Containers
        original_texts = []
        translated_texts = []
        glossary_files = []
        font_files = []
        archive_files = []
        release_files = []
        media_files = []
        other_files = []

        total_files = 0
        total_size_bytes = 0

        # Check existing THub / legacy markers
        has_thub_meta = os.path.exists(os.path.join(folder_path, "thub_project.json"))
        has_legacy_backup_folder = os.path.exists(os.path.join(folder_path, "01_Original_Backup"))
        has_standard_01 = os.path.exists(os.path.join(folder_path, "01_Original_Files"))

        ignore_dirs = {
            ".thub", ".git", ".svn", ".vscode", ".idea", "__pycache__", "node_modules",
            "_thub_legacy_snapshot", "DerivedDataCache", "Intermediate", "Saved",
            ".vs", "obj", "packages", "03_tools", "tools", "bin"
        }

        for root, dirs, files in os.walk(folder_path):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            rel_root = os.path.relpath(root, folder_path)
            if rel_root == ".":
                rel_root = ""

            for f in files:
                if f in ("thub_project.json", "AI_Mod_Continuation_Blueprint.md"):
                    continue
                total_files += 1
                full_path = os.path.join(root, f)
                rel_path = os.path.join(rel_root, f) if rel_root else f
                try:
                    f_size = os.path.getsize(full_path)
                except OSError:
                    f_size = 0
                total_size_bytes += f_size

                ext = os.path.splitext(f)[1].lower()
                f_lower = f.lower()

                # A. Text files
                if ext in cls.VALID_TEXT_EXTS:
                    is_thai, sample_stats = cls._analyze_text_file(full_path)
                    item = {
                        "path": full_path,
                        "rel_path": rel_path,
                        "size": f_size,
                        "has_thai": is_thai,
                        "stats": sample_stats
                    }

                    # Check for glossary
                    if any(w in f_lower for w in ["glossary", "dict", "term", "ศัพท์", "บัญชีคำศัพท์"]):
                        glossary_files.append(item)

                    if is_thai:
                        translated_texts.append(item)
                    else:
                        original_texts.append(item)

                # B. Fonts
                elif ext in cls.FONT_EXTS or (ext in {".dds", ".png"} and any(w in rel_path.lower() for w in ["font", "fnt"])):
                    font_files.append({"path": full_path, "rel_path": rel_path, "size": f_size})

                # C. Archives / Original Containers
                elif ext in cls.ARCHIVE_EXTS:
                    # Distinguish mod patch from raw game archives
                    if any(m in f_lower for m in ["_p.pak", "mod.pak", "patch.pak", "thai", "th_full"]):
                        release_files.append({"path": full_path, "rel_path": rel_path, "size": f_size})
                    else:
                        archive_files.append({"path": full_path, "rel_path": rel_path, "size": f_size})

                # D. Releases
                elif ext in cls.RELEASE_EXTS:
                    release_files.append({"path": full_path, "rel_path": rel_path, "size": f_size})

                # E. Media & PSD
                elif ext in cls.IMAGE_EXTS:
                    media_files.append({"path": full_path, "rel_path": rel_path, "size": f_size})

                # F. Other
                else:
                    other_files.append({"path": full_path, "rel_path": rel_path, "size": f_size})

        # Calculate translation completion ratio
        total_text_count = len(translated_texts) + len(original_texts)
        if total_text_count > 0:
            progress_pct = round((len(translated_texts) / total_text_count) * 100, 1)
        else:
            progress_pct = 0.0

        # Suggested restructure mappings
        suggested_mappings = cls._generate_suggested_mappings(
            folder_path,
            original_texts=original_texts,
            translated_texts=translated_texts,
            font_files=font_files,
            archive_files=archive_files,
            release_files=release_files,
            media_files=media_files
        )

        return {
            "success": True,
            "folder_path": folder_path,
            "folder_name": folder_name,
            "game_title": game_title,
            "engine_info": engine_info,
            "bible_info": bible_info,
            "total_files": total_files,
            "total_size_mb": round(total_size_bytes / (1024 * 1024), 2),
            "is_old_thub": has_legacy_backup_folder or has_thub_meta,
            "has_standard_01": has_standard_01,
            "stats": {
                "total_text_files": total_text_count,
                "translated_count": len(translated_texts),
                "original_count": len(original_texts),
                "glossary_count": len(glossary_files),
                "font_count": len(font_files),
                "archive_count": len(archive_files),
                "release_count": len(release_files),
                "media_count": len(media_files),
                "progress_pct": progress_pct
            },
            "original_texts": original_texts[:10],
            "translated_texts": translated_texts[:10],
            "glossary_files": glossary_files,
            "font_files": font_files[:10],
            "archive_files": archive_files[:10],
            "release_files": release_files[:10],
            "media_files": media_files[:10],
            "suggested_mappings": suggested_mappings
        }

    @classmethod
    def execute_adoption_restructure(cls, folder_path, options=None):
        """
        Executes the restructuring and adoption process.
        Options:
            - in_place (bool): True = reorganize in the same folder, False = copy to target_path
            - target_path (str): Required if in_place is False
            - safe_backup (bool): Creates a snapshot backup before making changes
            - copy_mode (bool): Copy instead of move (used when in_place=True and user wants to preserve original files)
            - deploy_templates (bool): Deploy master PSD templates to 07_Image_Resources
            - download_steam_art (bool): Fetch official Steam capsules and cover
            - game_title (str): Override detected title
            - engine (str): Override detected engine
            - author (str): Default author
        """
        options = options or {}
        folder_path = os.path.normpath(os.path.abspath(folder_path))
        in_place = options.get("in_place", True)
        target_path = os.path.normpath(os.path.abspath(options.get("target_path", folder_path))) if not in_place else folder_path
        safe_backup = options.get("safe_backup", True)
        copy_mode = options.get("copy_mode", False) or not in_place
        if not in_place and (contained(folder_path, target_path) or contained(target_path, folder_path)):
            raise ValueError("Source and destination must be separate, non-nested folders")
        if is_link(folder_path):
            raise ValueError("Adoption source cannot be a filesystem link")
        deploy_templates = options.get("deploy_templates", True)
        download_steam_art = options.get("download_steam_art", True)

        # Reject unreadable metadata before snapshots, transfers or registration.
        for workspace in {folder_path, target_path}:
            metadata = os.path.join(workspace, "thub_project.json")
            if os.path.exists(metadata):
                with open(metadata, encoding="utf-8-sig") as handle:
                    existing = json.load(handle)
                if not isinstance(existing, dict):
                    raise ValueError(f"Invalid existing project metadata: {metadata}")

        audit = cls.audit_legacy_folder(folder_path)
        if not audit.get("success"):
            return audit

        game_title = options.get("game_title") or audit["game_title"]
        engine_name = options.get("engine") or audit["engine_info"]["badge"]
        engine_color = audit["engine_info"].get("badge_color", "#38bdf8")
        bible_info = audit.get("bible_info")
        author = options.get("author", "หน๊ด หนวด translator")

        logs = []
        logs.append(f"Starting adoption restructure for: {game_title}")
        logs.append(f"Source Folder: {folder_path}")
        logs.append(f"Target Workspace: {target_path}")

        # 1. Create Safe Snapshot Backup if requested
        # A verified copy is mandatory before any moves when safe_backup is enabled.
        snapshot_path = create_snapshot(folder_path) if safe_backup else None
        if snapshot_path:
            logs.append(f"Verified file backup: {snapshot_path}")

        # 2. Ensure Standard THub Directories exist
        standard_dirs = [
            "01_Original_Files",
            "02_Extracted_Text",
            "03_Translated_Text",
            "04_Font_Assets",
            "05_Packed_Mod",
            "06_Release",
            "07_Image_Resources",
            os.path.join("07_Image_Resources", "Official_Art"),
            os.path.join("07_Image_Resources", "Generated_Logo"),
            os.path.join("07_Image_Resources", "Final_Exports"),
            os.path.join(".thub", "profile")
        ]
        for sd in standard_dirs:
            os.makedirs(os.path.join(target_path, sd), exist_ok=True)

        journal = []
        journal_path = os.path.join(target_path, ".thub", "adoption-" + uuid.uuid4().hex + ".json")
        def transfer(src, destination):
            if not contained(folder_path, src) or not contained(target_path, destination):
                raise ValueError("Transfer path escapes the selected workspace")
            actual = transfer_unique(src, destination, copy_only=copy_mode)
            journal.append({"source": src, "destination": actual, "operation": "copy" if copy_mode else "move"})
            write_json_atomic(journal_path, {"snapshot": snapshot_path, "transfers": journal})

        try:
            # 3. Handle Legacy 01_Original_Backup folder if present
            legacy_backup_p = os.path.join(folder_path, "01_Original_Backup")
            std_01_p = os.path.join(target_path, "01_Original_Files")
            if os.path.isdir(legacy_backup_p):
                for item in os.listdir(legacy_backup_p):
                    transfer(os.path.join(legacy_backup_p, item), os.path.join(std_01_p, item))

            # 4. Migrate Categorized Files
            mappings = audit.get("suggested_mappings", [])
            transferred_count = len(journal)
            for m in mappings:
                src = m["src"]
                # Already handled above, including copy-mode sources which still exist.
                if contained(legacy_backup_p, src):
                    continue
                dest_dir = os.path.join(target_path, m["dest_folder"])
                dest_p = os.path.join(dest_dir, os.path.basename(src))
                if os.path.normcase(os.path.abspath(src)) == os.path.normcase(os.path.abspath(dest_p)):
                    continue
                if not os.path.exists(src):
                    raise FileNotFoundError(f"Audited source disappeared: {src}")
                transfer(src, dest_p)
                transferred_count += 1
        except Exception as exc:
            return {"success": False, "error": str(exc), "logs": logs,
                    "snapshot_path": snapshot_path, "journal_path": journal_path,
                    "transferred_count": len(journal)}

        logs.append(f"Verified and organized {transferred_count} paths into THub standard folders.")

        try:
            # 5. Deploy Master PSD Templates to 07_Image_Resources
            if deploy_templates:
                try:
                    tmpl_dir = ProjectService.get_template_image_resources_dir()
                    dest_img_res = os.path.join(target_path, "07_Image_Resources")
                    if os.path.exists(tmpl_dir):
                        for tf in os.listdir(tmpl_dir):
                            tsp = os.path.join(tmpl_dir, tf)
                            tdp = os.path.join(dest_img_res, tf)
                            if os.path.isfile(tsp) and not os.path.exists(tdp):
                                shutil.copy2(tsp, tdp)
                        logs.append("Deployed master PSD templates to 07_Image_Resources/")
                except Exception as e:
                    logs.append(f"Error deploying PSD templates: {e}")

            # 6. Fetch Official Steam Assets
            if download_steam_art:
                try:
                    official_art_dir = os.path.join(target_path, "07_Image_Resources", "Official_Art")
                    root_cover = os.path.join(target_path, "thub_cover.jpg")
                    SteamService.fetch_all_game_capsules_sync(game_title, official_art_dir, root_cover_dest=root_cover)
                    logs.append("Harvested official Steam capsules and cover image.")
                except Exception as e:
                    logs.append(f"Warning: Steam art download failed: {e}")

            # 7. Create AI Mod Continuation Blueprint Markdown
            blueprint_p = cls._generate_blueprint_markdown(
                target_path=target_path,
                game_title=game_title,
                engine_name=engine_name,
                audit=audit,
                author=author
            )
            logs.append(f"Created AI Continuation Blueprint: {os.path.basename(blueprint_p)}")

            # 9. Register project into THub config
            config_mgr = ConfigManager()
            projects = copy.deepcopy(config_mgr.get_projects())
            existing_idx = next((i for i, p in enumerate(projects) if os.path.normpath(p.get("path", "")) == target_path), None)

            proj_entry = {
                "name": game_title,
                "path": target_path,
                "game_dir": audit["engine_info"].get("game_dir", ""),
                "engine": engine_name,
                "engine_color": engine_color,
                "status": "In Progress",
                "is_pinned": False,
                "is_archived": False,
                "bible_path": bible_info.get("bible_path", "") if bible_info else "",
                "bible_title": bible_info.get("bible_title", "") if bible_info else "",
                "adopted_from_legacy": True,
                "adopted_at": datetime.datetime.now().isoformat()
            }

            if existing_idx is not None:
                projects[existing_idx].update(proj_entry)
            else:
                projects.insert(0, proj_entry)

            # Register only after workspace metadata has been written successfully.

            # Write thub_project.json
            meta_file = os.path.join(target_path, "thub_project.json")
            meta_data = {
                "project_name": game_title,
                "version": "1.0.0",
                "author": author,
                "engine": engine_name,
                "source_lang": "English",
                "target_lang": "Thai",
                "adopted_legacy": True,
                "adopted_date": datetime.datetime.now().isoformat(),
                "notes": f"Adopted from legacy workspace into THub 01–07 standard."
            }
            # Retain existing metadata fields and refuse to replace unreadable JSON.
            if os.path.exists(meta_file):
                with open(meta_file, encoding="utf-8-sig") as handle:
                    existing_meta = json.load(handle)
                if not isinstance(existing_meta, dict):
                    raise ValueError("Invalid existing project metadata")
                for key in ("version", "author", "source_lang", "target_lang", "notes"):
                    if key in existing_meta:
                        meta_data[key] = existing_meta[key]
            update_json_atomic(meta_file, meta_data)
            config_mgr.save_projects(projects)
            logs.append(f"Registered project '{game_title}' into THub.")

            return {
                "success": True,
                "game_title": game_title,
                "target_path": target_path,
                "engine": engine_name,
                "project_entry": proj_entry,
                "blueprint_path": blueprint_p,
                "snapshot_path": snapshot_path,
                "journal_path": journal_path,
                "logs": logs,
                "stats": audit["stats"]
            }
        except Exception as exc:
            return {"success": False, "error": str(exc), "logs": logs,
                    "snapshot_path": snapshot_path, "journal_path": journal_path,
                    "transferred_count": len(journal)}

    @classmethod
    def generate_continuation_ai_prompt(cls, project=None, audit_data=None, mode="agent", folder_path=None, project_name=None):
        """
        Generates a specialized AI Prompt to instruct Claude Code / Antigravity / ChatGPT
        on continuing and finishing this adopted legacy mod.
        """
        if isinstance(project, str):
            folder_path = folder_path or project
            project = None
        if not project or not isinstance(project, dict):
            project = {
                "name": project_name or (os.path.basename(folder_path) if folder_path else "Unknown Game"),
                "path": folder_path or "",
                "engine": "Custom Engine"
            }
        elif folder_path and not project.get("path"):
            project["path"] = folder_path

        name = project.get("name", "Unknown Game")
        path = project.get("path", "")
        engine_name = project.get("engine", "Custom Engine")
        bible_title = project.get("bible_title", "")
        bible_path = project.get("bible_path", "")

        # Recalculate audit if not provided
        if not audit_data and path and os.path.exists(path):
            audit_data = cls.audit_legacy_folder(path)

        stats = (audit_data or {}).get("stats", {})
        trans_count = stats.get("translated_count", 0)
        orig_count = stats.get("original_count", 0)
        prog_pct = stats.get("progress_pct", 0.0)
        glossaries = (audit_data or {}).get("glossary_files", [])

        glossary_note = ""
        if glossaries:
            g_names = ", ".join(f"`{os.path.basename(g['path'])}`" for g in glossaries[:3])
            glossary_note = f"\n- **คลังคำศัพท์เดิมที่ตรวจพบ:** {g_names} (ตรวจสอบใน `02_Extracted_Text/` หรือ `03_Translated_Text/`)"

        prompt_agent = f"""🚀 ภารกิจปฏิบัติการ: สานต่องานม็อดเดิมด้วย AI Helper (Legacy Mod Adoption & Continuation Protocol)
========================================================================================

บริบทและเป้าหมายของภารกิจ (Mission Context):
คุณคือ AI Agent (Claude Code / Antigravity) ที่ได้รับมอบหมายให้เข้ามารับช่วงต่อและสานต่องานโปรเจกต์ม็อดแปลเกมภาษาไทย: **{name}**
โปรเจกต์นี้ได้รับการจัดระเบียบโครงสร้างเข้าสู่มาตรฐาน THub เรียบร้อยแล้ว หน้าที่ของคุณคือการสำรวจความคืบหน้าเดิม ดำเนินการแปลส่วนที่เหลือ แปลงฟอนต์ และแพ็กเกจม็อดให้เสร็จสมบูรณ์ 100%

สภาพแวดล้อมและโฟลเดอร์โปรเจกต์ (Project Workspace):
- 🎮 ชื่อเกม / โปรเจกต์:      {name}
- 📁 โฟลเดอร์ Workspace:     {path}
- ⚙️ Game Engine ที่ตรวจพบ:   {engine_name}
- 📖 คัมภีร์แปลม็อดอ้างอิง:     {bible_title or 'สแกนตามหมวดหมู่เอนจิ้นใน E:/Mod_Workspace/Modding-Knowledge/'}
- 📊 สถานะงานแปลเดิม:       แปลแล้วประมาณ {trans_count} ไฟล์ (คิดเป็น ~{prog_pct}%), ไฟล์ที่รอแปล {orig_count} ไฟล์{glossary_note}

โครงสร้างโฟลเดอร์มาตรฐาน 01–07 ที่ต้องปฏิบัติตามอย่างเคร่งครัด:
- 01_Original_Files/     -> ไฟล์เกมและข้อความต้นฉบับดั้งเดิม (ห้ามแก้ไขเด็ดขาด)
- 02_Extracted_Text/     -> ไฟล์ข้อความภาษาอังกฤษ/ญี่ปุ่นที่รอการแปล
- 03_Translated_Text/    -> ไฟล์ข้อความที่แปลเป็นภาษาไทยเรียบร้อยแล้ว
- 04_Font_Assets/        -> ไฟล์ฟอนต์ TTF/OTF, PUA Mapped, SDF Texture Atlas
- 05_Packed_Mod/         -> ไฟล์แพ็กเกจม็อด (.pak, .cpk, .bnd, etc.) สำหรับทดสอบในเกม
- 06_Release/            -> แพ็กเกจพร้อมเผยแพร่และคู่มือติดตั้ง
- 07_Image_Resources/    -> เทมเพลต PSD โพสต์โปรโมท (Official Art, AI Logo, Final Exports)

แผนการปฏิบัติงาน 5 ขั้นตอน (5-Phase Continuation Blueprint):

1. Phase 1: ตรวจสอบและสกัดคลังคำศัพท์เดิม (Audit & Harmonize Glossary)
   - สแกนไฟล์ที่แปลแล้วใน `03_Translated_Text/` เพื่อวิเคราะห์สำนวนและคำศัพท์หลัก (ชื่อตัวละคร, สถานที่, ไอเทม, สกิล)
   - สร้างหรืออัปเดตไฟล์ `{path}/03_Translated_Text/Project_Glossary.json` เพื่อใช้เป็นมาตรฐานเดียวกันในการแปลส่วนที่เหลือ

2. Phase 2: ดำเนินการแปลไฟล์ส่วนที่เหลือ (Complete Remaining Translations)
   - สแกนหาไฟล์ใน `02_Extracted_Text/` ที่ยังไม่มีคู่แปลใน `03_Translated_Text/`
   - ทำการแปลข้อความภาษาไทย โดยรักษาแท็กโค้ดเกม (เช่น %s, {{0}}, <color=red>, \n, \t) ไว้อย่างถูกต้อง 100%
   - บันทึกไฟล์ผลลัพธ์ลงใน `03_Translated_Text/` ให้มีโครงสร้างชื่อไฟล์และโฟลเดอร์ตรงกับต้นฉบับ

3. Phase 3: ตรวจสอบและติดตั้งฟอนต์ภาษาไทย (Font & PUA Verification)
   - ตรวจสอบโฟลเดอร์ `04_Font_Assets/` ว่ามีฟอนต์ไทยที่รองรับ PUA และสอดคล้องกับเอนจิ้น {engine_name} หรือไม่
   - หากใช้ระบบ TTF: แนะนำฟอนต์ LINE Seed Sans TH (ความสูงวรรณยุกต์ +140 units) หรือ Noto Sans Thai PUA
   - หากเป็นระบบ SDF/BMFont: ตรวจสอบ Glyph Atlas และตาราง Character Coordinates

4. Phase 4: แพ็กเกจม็อดและทดสอบในเกม (Pack & Proof-of-Concept Test)
   - สคริปต์แพ็กเกจไฟล์จาก `03_Translated_Text/` และ `04_Font_Assets/` กลับเข้าสู่ฟอร์แมตม็อดของเกมลงใน `05_Packed_Mod/`
   - ตรวจสอบให้แน่ใจว่าเกมสามารถอ่านม็อดได้โดยไม่มีข้อผิดพลาด

5. Phase 5: สื่อประชาสัมพันธ์และการเผยแพร่ (Media Kit & Release)
   - ตรวจสอบเทมเพลตใน `07_Image_Resources/` (cover 16-9.psd, Cover_Post facebook.psd, Header_facebook.psd)
   - จัดทำแพ็กเกจแจกจ่ายลงใน `06_Release/{name}_ThaiMod_v1.0/` พร้อมไฟล์ README_คู่มือการติดตั้ง.txt

คำสั่งเริ่มต้นสำหรับ AI Agent:
กรุณาเปิด Terminal และอ่านไฟล์ `{path}/AI_Mod_Continuation_Blueprint.md` เพื่อตรวจสอบรายชื่อไฟล์ที่ต้องทำต่อ จากนั้นเริ่มดำเนินการใน Phase 1 ทันทีครับ!
"""
        return prompt_agent

    @classmethod
    def _analyze_text_file(cls, file_path):
        """Reads sample lines from a text file to check for Thai characters."""
        try:
            # Read first 64KB
            with open(file_path, "rb") as f:
                raw = f.read(65536)

            # Try encodings
            text = ""
            for enc in ["utf-8", "cp874", "utf-16", "latin-1"]:
                try:
                    text = raw.decode(enc)
                    break
                except UnicodeDecodeError:
                    continue

            if not text:
                return False, {"lines": 0, "thai_chars": 0}

            has_thai = bool(cls.THAI_PATTERN.search(text))
            thai_count = len(cls.THAI_PATTERN.findall(text))
            lines_count = text.count("\n") + 1

            return has_thai, {"lines": lines_count, "thai_chars": thai_count}
        except Exception:
            return False, {"lines": 0, "thai_chars": 0}

    @classmethod
    def _clean_title_from_folder(cls, folder_name):
        """Cleans up folder name into human-readable game title."""
        cleaned = folder_name
        for prefix in ["mod_", "workspace_", "mod_workspace_", "thub_"]:
            if cleaned.lower().startswith(prefix):
                cleaned = cleaned[len(prefix):]
        for suffix in ["_mod_workspace", "_workspace", "_mod"]:
            if cleaned.lower().endswith(suffix):
                cleaned = cleaned[:-len(suffix)]
        return cleaned.replace("_", " ").strip()

    @classmethod
    def _generate_suggested_mappings(cls, folder_path, original_texts, translated_texts, font_files, archive_files, release_files, media_files):
        """Builds a list of suggested moves/copies into standard THub folders."""
        mappings = []

        for item in original_texts:
            # If already in standard folder, skip
            if "01_Original_Files" in item["rel_path"] or "02_Extracted_Text" in item["rel_path"]:
                continue
            mappings.append({
                "src": item["path"],
                "rel_src": item["rel_path"],
                "dest_folder": "02_Extracted_Text",
                "category": "Original Text"
            })

        for item in translated_texts:
            if "03_Translated_Text" in item["rel_path"]:
                continue
            mappings.append({
                "src": item["path"],
                "rel_src": item["rel_path"],
                "dest_folder": "03_Translated_Text",
                "category": "Translated Thai Text"
            })

        for item in font_files:
            if "04_Font_Assets" in item["rel_path"]:
                continue
            mappings.append({
                "src": item["path"],
                "rel_src": item["rel_path"],
                "dest_folder": "04_Font_Assets",
                "category": "Font Asset"
            })

        for item in archive_files:
            if "01_Original_Files" in item["rel_path"] or "05_Packed_Mod" in item["rel_path"]:
                continue
            mappings.append({
                "src": item["path"],
                "rel_src": item["rel_path"],
                "dest_folder": "01_Original_Files",
                "category": "Original Game Archive"
            })

        for item in release_files:
            if "06_Release" in item["rel_path"] or "05_Packed_Mod" in item["rel_path"]:
                continue
            mappings.append({
                "src": item["path"],
                "rel_src": item["rel_path"],
                "dest_folder": "05_Packed_Mod",
                "category": "Packed Mod Output"
            })

        for item in media_files:
            if "07_Image_Resources" in item["rel_path"]:
                continue
            mappings.append({
                "src": item["path"],
                "rel_src": item["rel_path"],
                "dest_folder": os.path.join("07_Image_Resources", "Official_Art"),
                "category": "Image / Media Resource"
            })

        return mappings

    @classmethod
    def _generate_blueprint_markdown(cls, target_path, game_title, engine_name, audit, author):
        """Generates the master AI_Mod_Continuation_Blueprint.md in the workspace."""
        bp_path = os.path.join(target_path, "AI_Mod_Continuation_Blueprint.md")
        stats = audit["stats"]
        dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        lines = [
            f"# 🚀 AI Mod Continuation Blueprint: {game_title}",
            f"> **Adopted into THub Standard Ecosystem on:** {dt}  ",
            f"> **Author / Lead Translator:** {author}  ",
            f"> **Detected Engine:** `{engine_name}`  ",
            "",
            "---",
            "",
            "## 1. ผลการตรวจประเมินโปรเจกต์เดิม (Legacy Mod Audit Summary)",
            "",
            f"- **จำนวนไฟล์ทั้งหมดที่ตรวจพบ:** {audit['total_files']} ไฟล์ ({audit['total_size_mb']} MB)",
            f"- **ไฟล์ข้อความแปลไทยแล้ว (03_Translated_Text):** {stats['translated_count']} ไฟล์",
            f"- **ไฟล์ข้อความต้นฉบับที่รอแปล (02_Extracted_Text):** {stats['original_count']} ไฟล์",
            f"- **ความคืบหน้างานแปลโดยประมาณ:** `{stats['progress_pct']}%`",
            f"- **ไฟล์ฟอนต์ที่พบ (04_Font_Assets):** {stats['font_count']} ไฟล์",
            f"- **แพ็กเกจม็อด / เอาต์พุตเดิม (05_Packed_Mod):** {stats['release_count']} ไฟล์",
            "",
            "---",
            "",
            "## 2. โครงสร้างโฟลเดอร์มาตรฐาน THub (Standard Workspace Inventory)",
            "",
            "```text",
            f"{os.path.basename(target_path)}/",
            "├── 01_Original_Files/      # ไฟล์ต้นฉบับเกมดั้งเดิม",
            "├── 02_Extracted_Text/      # ข้อความภาษาอังกฤษ/ต่างประเทศที่รอการแปล",
            "├── 03_Translated_Text/     # ข้อความที่แปลเป็นภาษาไทยเรียบร้อยแล้ว",
            "├── 04_Font_Assets/         # ฟอนต์ TTF/OTF, PUA Glyph Tables, Textures",
            "├── 05_Packed_Mod/          # ไฟล์แพ็กเกจม็อด (.pak, .upk, .cpk) สำหรับทดสอบ",
            "├── 06_Release/             # ชุดไฟล์แจกจ่ายสำเร็จรูปพร้อมติดตั้ง",
            "└── 07_Image_Resources/     # ภาพปก, แคปซูล และเทมเพลต PSD โพสต์โปรโมท",
            "```",
            "",
            "---",
            "",
            "## 3. รายการไฟล์สำคัญที่ต้องดำเนินการต่อ (Action Items for AI Agent)",
            ""
        ]

        if audit.get("glossary_files"):
            lines.append("### 📖 คลังคำศัพท์เดิมที่ตรวจพบ (Existing Glossaries):")
            for g in audit["glossary_files"]:
                lines.append(f"- `{g['rel_path']}`")
            lines.append("")

        if audit.get("translated_texts"):
            lines.append("### ✅ ตัวอย่างไฟล์ที่แปลแล้ว (Sample Translated Files):")
            for t in audit["translated_texts"][:8]:
                lines.append(f"- `{t['rel_path']}` ({t['stats'].get('lines', 0)} บรรทัด, {t['stats'].get('thai_chars', 0)} อักษรไทย)")
            lines.append("")

        if audit.get("original_texts"):
            lines.append("### ⏳ ตัวอย่างไฟล์ที่ยังรอการแปล (Sample Pending Translation Files):")
            for o in audit["original_texts"][:8]:
                lines.append(f"- `{o['rel_path']}` ({o['stats'].get('lines', 0)} บรรทัด)")
            lines.append("")

        lines.extend([
            "---",
            "",
            "## 4. มาตรฐานฟอนต์และการแสดงผลภาษาไทย (Font Subsystem Directive)",
            f"- **Engine**: `{engine_name}`",
            "- **คำแนะนำฟอนต์**: แนะนำฟอนต์ตระกูล **LINE Seed Sans TH** (ปรับยกวรรณยุกต์ขึ้น +140 หน่วย) หรือ **Noto Sans Thai PUA** เพื่อป้องกันปัญหาวรรณยุกต์ซ้อนกับสระบน",
            "- **PUA Mappings**: ใช้ช่วง Unicode `0xF700` – `0xF71A` สำหรับสระ/วรรณยุกต์ลอย/จมตามมาตรฐานสากล",
            "",
            "---",
            "",
            "## 5. แผนการทดสอบและปล่อยผลงาน (Testing & Release Strategy)",
            "1. รันสคริปต์ Validator เพื่อตรวจเช็ค Tag โค้ดของเกมใน `03_Translated_Text/`",
            "2. บิลด์แพ็กเกจม็อดลงใน `05_Packed_Mod/` และเปิดเกมทดสอบความสมบูรณ์",
            "3. นำภาพ Official Art ไปประกอบลงในไฟล์ PSD ใน `07_Image_Resources/` และเซฟลง `Final_Exports/` สำหรับโพสต์เพจ",
            "4. สร้างไฟล์ติดตั้งหรือ zip สำหรับแจกจ่ายลงใน `06_Release/`",
            "",
            "---",
            "*จัดทำและบันทึกโดย THub Mod Adoption Protocol*"
        ])

        content = "\n".join(lines)
        with open(bp_path, "w", encoding="utf-8") as f:
            f.write(content)

        return bp_path
