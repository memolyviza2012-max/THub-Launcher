import os
import json
import re
import threading
from core.safe_io import write_json_atomic, update_json_atomic
from core.workspace_schema import WorkspaceSchema
from core.config_manager import ConfigManager
from core.engine_scanner import EngineScanner

class ProjectService:
    """Handles project lifecycle, workspace creation, and translation metrics."""
    STANDARD_FOLDERS = [
        "01_Original_Backup",
        "02_Translation_Workspace",
        "03_Font_and_UI",
        "04_Packed_Mod",
        "05_Scripts_and_Tools",
        "06_Releases",
        "07_Image_Resources"
    ]

    VALID_TEXT_EXTS = {".json", ".csv", ".txt", ".xml", ".yaml", ".ini", ".locres", ".lang", ".po", ".pot", ".msg"}
    THAI_PATTERN = re.compile(r'[\u0E00-\u0E7F]')

    def __init__(self, config_manager=None):
        self.cfg = config_manager or ConfigManager()
        self._stats_cache = {}
        self._lock = threading.Lock()

    @classmethod
    def get_template_image_resources_dir(cls):
        """Resolves the 07_Image_Resources template directory.
        Prioritizes live external template depot (E:\\Mod_Workspace\\1_Template\\07_Image_Resources)
        and automatically synchronizes any updated template files to the bundled templates directory.
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        bundled = os.path.join(base_dir, "templates", "07_Image_Resources")
        dev_external = r"E:\Mod_Workspace\1_Template\07_Image_Resources"

        if os.path.exists(dev_external):
            # Auto-synchronize any newer or missing templates from 1_Template to bundled directory
            if os.path.exists(bundled):
                try:
                    import shutil
                    for item in os.listdir(dev_external):
                        s = os.path.join(dev_external, item)
                        d = os.path.join(bundled, item)
                        if os.path.isfile(s):
                            if not os.path.exists(d) or os.path.getmtime(s) > os.path.getmtime(d):
                                shutil.copy2(s, d)
                except Exception as e:
                    print(f"[ProjectService] Template auto-sync error: {e}")
            return dev_external

        if os.path.exists(bundled):
            return bundled
        return bundled

    def get_all_projects(self, include_archived=False):
        all_proj = self.cfg.get_projects()
        if include_archived:
            return all_proj
        return [p for p in all_proj if not p.get("is_archived", False)]

    def get_project_by_name(self, name):
        for p in self.cfg.get_projects():
            if p.get("name") == name:
                return p
        return None

    def create_project(self, name, workspace_path, game_dir="", tool_dir="", source_lang="English", target_lang="Thai", author="", contributors="", notes="", link="", engine=None, bible_info=None):
        """Initializes a new THub standard workspace and registers it."""
        for existing in self.cfg.get_projects():
            if existing.get("name") == name or os.path.normcase(os.path.abspath(existing.get("path") or ".")) == os.path.normcase(os.path.abspath(workspace_path)):
                raise ValueError("A project with this name or workspace is already registered")
        existing_meta = {}
        metadata_path = os.path.join(workspace_path, "thub_project.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, encoding="utf-8-sig") as handle:
                existing_meta = json.load(handle)
            if not isinstance(existing_meta, dict):
                raise ValueError("Invalid existing workspace metadata")
        os.makedirs(workspace_path, exist_ok=True)
        for folder in self.STANDARD_FOLDERS:
            os.makedirs(os.path.join(workspace_path, folder), exist_ok=True)

        # Setup 07_Image_Resources subfolders & copy template files
        img_res_dir = os.path.join(workspace_path, "07_Image_Resources")
        os.makedirs(os.path.join(img_res_dir, "Official_Art"), exist_ok=True)
        os.makedirs(os.path.join(img_res_dir, "Generated_Logo"), exist_ok=True)
        os.makedirs(os.path.join(img_res_dir, "Final_Exports"), exist_ok=True)

        template_dir = self.get_template_image_resources_dir()
        if os.path.exists(template_dir):
            try:
                import shutil
                for item in os.listdir(template_dir):
                    s = os.path.join(template_dir, item)
                    d = os.path.join(img_res_dir, item)
                    if os.path.isfile(s) and not os.path.exists(d):
                        shutil.copy2(s, d)
            except Exception as e:
                print(f"[ProjectService] Copy templates error: {e}")

        # Create Project-Bound Profile folder
        os.makedirs(os.path.join(workspace_path, ".thub", "profile"), exist_ok=True)

        # Detect engine automatically using full context
        engine_info = EngineScanner.detect_engine(
            game_dir=game_dir,
            workspace_dir=workspace_path,
            title=name,
            saved_engine=engine
        )
        resolved_engine = engine_info["badge"]
        resolved_color = engine_info["badge_color"]

        # If bible_info not provided, use engine_info's detected bible
        if not bible_info and engine_info.get("bible"):
            bible_info = engine_info["bible"]

        meta = {
            "project_name": name,
            "version": "1.0.0",
            "author": author,
            "contributors": contributors,
            "project_link": link,
            "game_path": game_dir,
            "tool_path": tool_dir,
            "engine": resolved_engine,
            "source_lang": source_lang,
            "target_lang": target_lang,
            "profile_name": name,
            "notes": notes
        }

        if bible_info:
            meta["bible_reference"] = {
                "title": bible_info.get("bible_title"),
                "path": bible_info.get("bible_path"),
                "rel_path": bible_info.get("rel_path"),
                "game_name": bible_info.get("game_name"),
                "engine": bible_info.get("engine_name"),
                "recommended_tools": bible_info.get("recommended_tools", []),
                "file_extensions": bible_info.get("file_extensions", [])
            }

        meta_file = os.path.join(workspace_path, "thub_project.json")
        meta = {**meta, **existing_meta}
        write_json_atomic(meta_file, meta)

        # Write .thub/bible_reference.json
        if bible_info:
            try:
                thub_dir = os.path.join(workspace_path, ".thub")
                os.makedirs(thub_dir, exist_ok=True)
                with open(os.path.join(thub_dir, "bible_reference.json"), "w", encoding="utf-8") as f:
                    json.dump(bible_info, f, indent=4, ensure_ascii=False, default=str)
            except Exception as e:
                print(f"[ProjectService] Write bible_reference.json error: {e}")

        # Create README.md
        readme_file = os.path.join(workspace_path, "README.md")
        if not os.path.exists(readme_file):
            bible_section = ""
            if bible_info:
                tools_str = ", ".join(bible_info.get("recommended_tools", [])) or "TStudio, TRun"
                exts_str = ", ".join(bible_info.get("file_extensions", [])) or "-"
                bible_section = f"""
## 📖 คัมภีร์อ้างอิงในการแปล (Modding Bible Reference)
- **ชื่อคัมภีร์:** {bible_info.get("bible_title")}
- **ไฟล์คัมภีร์ต้นทาง:** `{bible_info.get("bible_path")}`
- **เอนจิ้นที่ระบุ:** {bible_info.get("engine_name")}
- **เครื่องมือแนะนำ:** {tools_str}
- **นามสกุลไฟล์หลัก:** {exts_str}
"""
            readme_content = f"""# 📁 โปรเจกต์แปลเกม: {name}
ยินดีต้อนรับสู่พื้นที่ทำงานแปลเกมผ่านระบบ THub Workspace!

## รายละเอียดโปรเจกต์ (Project Details)
- **ชื่อโปรเจกต์ / เกม:** {name}
- **เอนจิ้นเกม:** {resolved_engine}
- **ผู้พัฒนา / ทีมแปล:** {author if author else "หน๊ด หนวด translator"}
- **ทีมงาน / ผู้ร่วมแปล:** {contributors if contributors else "-"}
- **ลิงก์โปรเจกต์ / GitHub:** {link if link else "-"}
- **บันทึกย่อ:** {notes if notes else "-"}
{bible_section}
## โครงสร้างโฟลเดอร์ทำงาน (Workspace Structure)
- **`01_Original_Backup`**: โฟลเดอร์สำหรับเก็บไฟล์ข้อความต้นฉบับดั้งเดิมของเกม (เช่น ภาษาอังกฤษ) เพื่อใช้สำรองข้อมูล
- **`02_Translation_Workspace`**: โฟลเดอร์สำหรับทำไฟล์แปลภาษาไทย (.csv, .xlsx, .json) เพื่อเปิดในโปรแกรม TStudio
- **`03_Font_and_UI`**: โฟลเดอร์สำหรับเก็บไฟล์ฟอนต์, แผ่นภาพ Texture (Atlas), พิกัดฟอนต์ (.fnt/.xml), และตัวแมปปิ้งสระ PUA
- **`04_Packed_Mod`**: โฟลเดอร์ทดสอบที่จัดวางโครงสร้างตัวม็อดไว้พร้อมสำหรับการนำไปยัดหรือติดตั้งทับลงเกมจริง
- **`05_Scripts_and_Tools`**: โฟลเดอร์สำหรับเก็บสคริปต์เฉพาะกิจ (เช่น สคริปต์แยกคำแปล, สคริปต์แพ็กกลับ) หรือโปรแกรมแกะไฟล์เฉพาะเกม
- **`06_Releases`**: โฟลเดอร์สำหรับเก็บไฟล์บิลด์สำเร็จรูปสุดท้าย (.zip, .rar) สำหรับนำไปแจกจ่ายให้ผู้ใช้หรือผู้ทดสอบ
- **`07_Image_Resources`**: โฟลเดอร์สำหรับสื่อประชาสัมพันธ์ หน้าปก Facebook/Web, เทมเพลต PSD, ภาพทางการจาก Steam, และคำสั่ง AI เจนโลโก้ชื่อเกมภาษาไทย

---
*จัดระบบการจัดการโดย THub Launcher*
"""
            try:
                with open(readme_file, "w", encoding="utf-8") as f:
                    f.write(readme_content.strip())
            except Exception as e:
                print(f"[ProjectService] Write README.md error: {e}")

        proj_entry = {
            "name": name,
            "path": workspace_path,
            "game_dir": game_dir,
            "tool_dir": tool_dir,
            "engine": resolved_engine,
            "engine_badge": resolved_engine,
            "engine_color": resolved_color,
            "source_lang": source_lang,
            "target_lang": target_lang,
            "profile_name": name,
            "translation_folders": ["02_Translation_Workspace"],
            "status": "In Progress",
            "is_pinned": False,
            "is_archived": False
        }
        if bible_info:
            proj_entry["bible_title"] = bible_info.get("bible_title")
            proj_entry["bible_path"] = bible_info.get("bible_path")
            proj_entry["recommended_tools"] = bible_info.get("recommended_tools", [])
            proj_entry["file_extensions"] = bible_info.get("file_extensions", [])

        projects = self.cfg.get_projects()
        projects.insert(0, proj_entry)
        self.cfg.save_projects(projects)
        return proj_entry

    def migrate_image_resources(self, project, on_complete=None):
        """Retroactively sets up or reorganizes 07_Image_Resources for an existing project.
        Safe and non-destructive: never deletes or overwrites existing user PSDs or images.
        """
        def _worker():
            path = project.get("path", "")
            name = project.get("name", "")
            engine = project.get("engine", "Custom Engine")
            if not path or not os.path.exists(path):
                res = {"success": False, "error": "Invalid workspace path"}
                if on_complete:
                    on_complete(res)
                return res

            img_res_dir = os.path.join(path, "07_Image_Resources")
            os.makedirs(img_res_dir, exist_ok=True)
            official_art_dir = os.path.join(img_res_dir, "Official_Art")
            gen_logo_dir = os.path.join(img_res_dir, "Generated_Logo")
            final_exp_dir = os.path.join(img_res_dir, "Final_Exports")
            os.makedirs(official_art_dir, exist_ok=True)
            os.makedirs(gen_logo_dir, exist_ok=True)
            os.makedirs(final_exp_dir, exist_ok=True)

            # Copy missing templates from bundled templates or 1_Template (never overwrite existing)
            copied_templates = []
            template_dir = self.get_template_image_resources_dir()
            if os.path.exists(template_dir):
                import shutil
                for item in os.listdir(template_dir):
                    s = os.path.join(template_dir, item)
                    d = os.path.join(img_res_dir, item)
                    if os.path.isfile(s) and not os.path.exists(d):
                        try:
                            shutil.copy2(s, d)
                            copied_templates.append(item)
                        except Exception as e:
                            print(f"[ProjectService] Copy template {item} error: {e}")

            # Fetch official Steam capsules & covers
            from core.steam_service import SteamService
            root_cover = os.path.join(path, "thub_cover.jpg")
            downloaded = SteamService.fetch_all_game_capsules_sync(name, official_art_dir, root_cover_dest=root_cover)

            # Update README.md if 07_Image_Resources is not yet mentioned
            readme_path = os.path.join(path, "README.md")
            if os.path.exists(readme_path):
                try:
                    with open(readme_path, "r", encoding="utf-8") as f:
                        readme_txt = f.read()
                    if "07_Image_Resources" not in readme_txt:
                        addition = "\n- **`07_Image_Resources`**: โฟลเดอร์สำหรับสื่อประชาสัมพันธ์ หน้าปก Facebook/Web, เทมเพลต PSD, ภาพทางการจาก Steam, และคำสั่ง AI เจนโลโก้ชื่อเกมภาษาไทย\n"
                        if "06_Releases" in readme_txt:
                            readme_txt = readme_txt.replace(
                                "- **`06_Releases`**",
                                "- **`06_Releases`**" + addition
                            )
                        else:
                            readme_txt += addition
                        with open(readme_path, "w", encoding="utf-8") as f:
                            f.write(readme_txt)
                except Exception as e:
                    print(f"[ProjectService] Update README.md error: {e}")

            res = {
                "success": True,
                "project_name": name,
                "workspace": path,
                "img_res_dir": img_res_dir,
                "copied_templates": copied_templates,
                "downloaded_art": downloaded,
                "logo_prompt_created": logo_created
            }
            if on_complete:
                try:
                    on_complete(res)
                except Exception as e:
                    print(f"[ProjectService] migrate_image_resources callback error: {e}")
            return res

        if on_complete:
            t = threading.Thread(target=_worker, daemon=True)
            t.start()
            return None
        else:
            return _worker()

    def calculate_progress_async(self, project, callback):
        """Calculates translation progress in background and invokes callback(pct, total, translated, file_count)."""
        def _worker():
            path = project.get("path", "")
            target_dirs = WorkspaceSchema.folders(project, "02_Translation_Workspace")
            # Never count backup/release copies as translation progress.
            target_dirs = target_dirs[:1]

            total_lines = 0
            translated_lines = 0
            file_count = 0

            for t_dir in target_dirs:
                for root, _, files in os.walk(t_dir):
                    for file in files:
                        ext = os.path.splitext(file)[1].lower()
                        if ext in self.VALID_TEXT_EXTS:
                            file_path = os.path.join(root, file)
                            file_count += 1
                            lines = []
                            for enc in ['utf-8', 'utf-8-sig', 'utf-16', 'utf-16le', 'cp874', 'cp1252']:
                                try:
                                    with open(file_path, 'r', encoding=enc) as f:
                                        lines = f.readlines()
                                    break
                                except Exception:
                                    continue

                            for line in lines:
                                line = line.strip()
                                if not line:
                                    continue
                                total_lines += 1
                                if self.THAI_PATTERN.search(line):
                                    translated_lines += 1

            pct = int((translated_lines / total_lines) * 100) if total_lines > 0 else 0
            result = {
                "percentage": pct,
                "total_lines": total_lines,
                "translated_lines": translated_lines,
                "file_count": file_count
            }

            with self._lock:
                self._stats_cache[project.get("name", "")] = result

            if callback:
                callback(result)

        t = threading.Thread(target=_worker, daemon=True)
        t.start()

    def toggle_pin(self, project_name):
        projects = self.cfg.get_projects()
        for p in projects:
            if p.get("name") == project_name:
                p["is_pinned"] = not p.get("is_pinned", False)
                break
        self.cfg.save_projects(projects)

    def toggle_archive(self, project_name, status=None):
        projects = self.cfg.get_projects()
        target_proj = None
        for p in projects:
            if p.get("name") == project_name:
                curr_arch = p.get("is_archived", False)
                new_arch = not curr_arch
                p["is_archived"] = new_arch
                if new_arch and status:
                    p["status"] = status
                    p["archive_status"] = status
                elif not new_arch and p.get("status") in ("On Hold", "Cancelled", "ดอง", "ยกเลิก"):
                    p["status"] = "In Progress"
                target_proj = p
                break
        self.cfg.save_projects(projects)

        if target_proj and target_proj.get("path"):
            meta_file = os.path.join(target_proj["path"], "thub_project.json")
            if os.path.exists(meta_file):
                try:
                    with open(meta_file, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                    meta["is_archived"] = target_proj["is_archived"]
                    if "status" in target_proj:
                        meta["status"] = target_proj["status"]
                    update_json_atomic(meta_file, {key: meta[key] for key in ("status", "is_archived", "archive_status", "engine") if key in meta})
                except Exception as e:
                    print(f"[ProjectService] Could not update thub_project.json archive: {e}")
        return target_proj

    def set_archive(self, project_name, is_archived, status=None):
        """Explicitly sets archive state and status ('Completed', 'Cancelled', 'On Hold')."""
        projects = self.cfg.get_projects()
        target_proj = None
        for p in projects:
            if p.get("name") == project_name:
                p["is_archived"] = is_archived
                if status:
                    p["status"] = status
                    p["archive_status"] = status
                elif not is_archived:
                    p["archive_status"] = ""
                    if p.get("status") in ("On Hold", "Cancelled", "ดอง", "ยกเลิก"):
                        p["status"] = "In Progress"
                target_proj = p
                break
        self.cfg.save_projects(projects)

        if target_proj and target_proj.get("path"):
            meta_file = os.path.join(target_proj["path"], "thub_project.json")
            if os.path.exists(meta_file):
                try:
                    with open(meta_file, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                    meta["is_archived"] = is_archived
                    if "status" in target_proj:
                        meta["status"] = target_proj["status"]
                    if "archive_status" in target_proj:
                        meta["archive_status"] = target_proj["archive_status"]
                    update_json_atomic(meta_file, {key: meta[key] for key in ("status", "is_archived", "archive_status", "engine") if key in meta})
                except Exception as e:
                    print(f"[ProjectService] Could not update thub_project.json archive: {e}")
        return target_proj

    def set_status(self, project_name, status):
        """Directly sets project status ('In Progress', 'Completed', 'Cancelled', 'On Hold')."""
        projects = self.cfg.get_projects()
        target_proj = None
        for p in projects:
            if p.get("name") == project_name:
                p["status"] = status
                target_proj = p
                break
        self.cfg.save_projects(projects)

        if target_proj and target_proj.get("path"):
            meta_file = os.path.join(target_proj["path"], "thub_project.json")
            if os.path.exists(meta_file):
                try:
                    with open(meta_file, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                    meta["status"] = status
                    update_json_atomic(meta_file, {key: meta[key] for key in ("status", "is_archived", "archive_status", "engine") if key in meta})
                except Exception as e:
                    print(f"[ProjectService] Could not update thub_project.json status: {e}")
        return target_proj

    def toggle_status(self, project_name):
        """Toggles project status between 'Completed' and 'In Progress', syncing config and thub_project.json."""
        projects = self.cfg.get_projects()
        target_proj = None
        for p in projects:
            if p.get("name") == project_name:
                curr = p.get("status", "In Progress")
                new_status = "In Progress" if curr == "Completed" else "Completed"
                p["status"] = new_status
                target_proj = p
                break
        self.cfg.save_projects(projects)

        # Also synchronize thub_project.json in workspace if present
        if target_proj and target_proj.get("path"):
            meta_file = os.path.join(target_proj["path"], "thub_project.json")
            if os.path.exists(meta_file):
                try:
                    with open(meta_file, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                    meta["status"] = target_proj["status"]
                    update_json_atomic(meta_file, {key: meta[key] for key in ("status", "is_archived", "archive_status", "engine") if key in meta})
                except Exception as e:
                    print(f"[ProjectService] Could not update thub_project.json status: {e}")

        return target_proj

    def delete_project(self, project_name):
        projects = self.cfg.get_projects()
        projects = [p for p in projects if p.get("name") != project_name]
        self.cfg.save_projects(projects)

    def save_project_order(self, ordered_projects):
        """Persists the user-defined project order to hub_config.json."""
        self.cfg.save_projects(ordered_projects)

    def update_project_engine(self, project_name, engine_name, engine_color=None):
        """Updates the game engine for a project in both config and thub_project.json."""
        if not engine_color:
            engine_color = EngineScanner.get_engine_color(engine_name)

        projects = self.cfg.get_projects()
        target_project = None
        for p in projects:
            if p.get("name") == project_name:
                p["engine"] = engine_name
                p["engine_badge"] = engine_name
                p["engine_color"] = engine_color
                target_project = p
                break
        self.cfg.save_projects(projects)

        # Also update workspace thub_project.json if present
        if target_project and target_project.get("path"):
            meta_file = os.path.join(target_project["path"], "thub_project.json")
            if os.path.exists(meta_file):
                try:
                    with open(meta_file, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                    meta["engine"] = engine_name
                    update_json_atomic(meta_file, {key: meta[key] for key in ("status", "is_archived", "archive_status", "engine") if key in meta})
                except Exception as e:
                    print(f"[ProjectService] Could not update thub_project.json: {e}")

        return target_project

    def update_project(self, old_name, updated_data):
        """
        Updates full project configuration in hub_config.json and synchronizes thub_project.json.
        """
        projects = self.cfg.get_projects()
        target_project = None
        target_idx = -1

        for idx, p in enumerate(projects):
            if p.get("name") == old_name:
                target_project = p
                target_idx = idx
                break

        if target_idx == -1:
            raise ValueError(f"Project '{old_name}' not found.")

        # Update engine badge & color if engine was changed
        new_engine = updated_data.get("engine", target_project.get("engine", "Custom Engine"))
        engine_color = updated_data.get("engine_color") or EngineScanner.get_engine_color(new_engine)

        target_project.update(updated_data)
        target_project["engine"] = new_engine
        target_project["engine_badge"] = new_engine
        target_project["engine_color"] = engine_color

        projects[target_idx] = target_project
        self.cfg.save_projects(projects)

        # Synchronize workspace metadata (thub_project.json)
        ws_path = target_project.get("path")
        if ws_path and os.path.exists(ws_path):
            meta_file = os.path.join(ws_path, "thub_project.json")
            meta = {}
            if os.path.exists(meta_file):
                try:
                    with open(meta_file, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                except Exception as e:
                    raise OSError(f"Cannot update unreadable metadata: {meta_file}") from e

            meta.update({
                "project_name": target_project.get("name", ""),
                "version": meta.get("version", "1.0.0"),
                "author": updated_data.get("author", meta.get("author", "")),
                "contributors": updated_data.get("contributors", meta.get("contributors", "")),
                "project_link": updated_data.get("project_link", meta.get("project_link", "")),
                "game_path": target_project.get("game_dir", ""),
                "tool_path": target_project.get("tool_dir", ""),
                "engine": new_engine,
                "source_lang": target_project.get("source_lang", "English"),
                "target_lang": target_project.get("target_lang", "Thai"),
                "profile_name": target_project.get("name", ""),
                "notes": updated_data.get("notes", meta.get("notes", "")),
                "status": target_project.get("status", "In Progress")
            })

            try:
                write_json_atomic(meta_file, meta)
            except Exception as e:
                raise OSError(f"Cannot save project metadata: {meta_file}") from e

        return target_project
