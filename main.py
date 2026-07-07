# Thub - Cloud Launcher and Modding Tools
# Copyright (C) 2026 Danaiwit Kanthawong (NodNuatTranslator)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import customtkinter as ctk
import json
import os
import subprocess
import threading
import re
from tkinter import messagebox, filedialog
import glob
from PIL import Image
import markdown
import webbrowser
import sys
from packaging import version
from i18n_helper import _

# ── PyInstaller resource path helper ──────────────────────────────────────────
def resource_path(relative_path):
    """Get absolute path to resource — works for both dev and PyInstaller builds."""
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative_path)
# ──────────────────────────────────────────────────────────────────────────────

# ── Bootstrap language from config BEFORE any _() calls ──────────────────────
# Read app_lang from hub_config.json early so every _() call at module level
# already uses the correct locale (fixes "language doesn't apply until restart" bug)
try:
    import json as _json
    _cfg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hub_config.json")
    if os.path.exists(_cfg_path):
        with open(_cfg_path, encoding="utf-8") as _f:
            _saved_lang = _json.load(_f).get("app_lang", "th")
        if _saved_lang and _saved_lang != os.environ.get("THUB_LANG", ""):
            os.environ["THUB_LANG"] = _saved_lang
except Exception:
    pass
# ─────────────────────────────────────────────────────────────────────────────

# --- THUB RUNTIME ENGINE ---
# Allows THub.exe to run .py scripts using its bundled environment
if len(sys.argv) > 1 and sys.argv[1].endswith(".py"):
    script_path = os.path.abspath(sys.argv[1])
    sys.argv.pop(1)
    
    script_dir = os.path.dirname(script_path)
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
        
    import runpy
    try:
        runpy.run_path(script_path, run_name="__main__")
    except SystemExit as e:
        sys.exit(e.code)
    except Exception as e:
        import traceback
        traceback.print_exc()
        import tkinter.messagebox
        tkinter.messagebox.showerror("Runtime Error", f"Failed to run script:\n{e}")
    sys.exit(0)
# ---------------------------

import tempfile
import urllib.request
import urllib.error
import zipfile
import io
import tkinter as tk

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tw = None
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)

    def enter(self, event=None):
        if self.tw: return
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tw = tk.Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tw, text=self.text, justify='left',
                       background="#1e1e2e", foreground="#cdd6f4", relief='solid', borderwidth=1,
                       font=("Segoe UI", 12))
        label.pack(ipadx=6, ipady=3)

    def leave(self, event=None):
        if self.tw:
            self.tw.destroy()
            self.tw = None

class ProjectWizardWindow(ctk.CTkToplevel):
    def __init__(self, parent, is_import_mode=False, initial_path=None):
        super().__init__(parent)
        self.parent = parent
        self.is_import_mode = is_import_mode
        self.initial_path = initial_path
        self.result = None
        
        self.title(_("📥 นำเข้าโปรเจกต์") if is_import_mode else _("🚀 สร้างโปรเจกต์ใหม่"))
        self.geometry("650x620")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Center the window relative to parent
        self.update_idletasks()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_w = parent.winfo_width()
        parent_h = parent.winfo_height()
        x = parent_x + (parent_w - 650) // 2
        y = parent_y + (parent_h - 620) // 2
        self.geometry(f"+{x}+{y}")
        
        # Title Label
        lbl_title = ctk.CTkLabel(self, text=_("ตั้งค่ารายละเอียดโปรเจกต์") if is_import_mode else _("สร้างโปรเจกต์แปลเกมใหม่"), font=ctk.CTkFont(size=22, weight="bold"), text_color="#cba6f7")
        lbl_title.pack(pady=(20, 15))
        
        # Main form frame
        form_frame = ctk.CTkFrame(self, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=40)
        
        # Grid config
        form_frame.columnconfigure(0, weight=1)
        form_frame.columnconfigure(1, weight=3)
        form_frame.columnconfigure(2, weight=0)
        
        row = 0
        
        # 1. Project Name
        ctk.CTkLabel(form_frame, text=_("ชื่อโปรเจกต์ / เกม *:"), font=ctk.CTkFont(weight="bold"), anchor="w").grid(row=row, column=0, sticky="w", pady=10)
        self.ent_name = ctk.CTkEntry(form_frame, placeholder_text=_("เช่น Dead Island 2 (ภาษาอังกฤษต้นฉบับ)"))
        self.ent_name.grid(row=row, column=1, columnspan=2, sticky="ew", pady=10)
        self.ent_name.bind("<KeyRelease>", self.on_name_change)
        if is_import_mode and initial_path:
            self.ent_name.insert(0, os.path.basename(initial_path))
        row += 1
        
        # 1.5 Languages
        ctk.CTkLabel(form_frame, text=_("ภาษา (ต้นฉบับ -> แปล):"), font=ctk.CTkFont(weight="bold"), anchor="w").grid(row=row, column=0, sticky="w", pady=10)
        lang_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        lang_frame.grid(row=row, column=1, columnspan=2, sticky="ew", pady=10)
        
        lang_options = ["English", "Thai", "Japanese", "Chinese", "Korean", "French", "Spanish", "German"]
        
        self.cbo_source_lang = ctk.CTkComboBox(lang_frame, values=lang_options, width=120)
        self.cbo_source_lang.set("English")
        self.cbo_source_lang.pack(side="left", padx=(0, 10))
        
        ctk.CTkLabel(lang_frame, text="➡️", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        
        self.cbo_target_lang = ctk.CTkComboBox(lang_frame, values=["Thai", "English", "Japanese", "Chinese", "Korean"], width=120)
        self.cbo_target_lang.set("Thai")
        self.cbo_target_lang.pack(side="left", padx=(10, 0))
        row += 1
        
        # 2. Developer / Author
        ctk.CTkLabel(form_frame, text=_("ผู้พัฒนา / ผู้แปล:"), font=ctk.CTkFont(weight="bold"), anchor="w").grid(row=row, column=0, sticky="w", pady=10)
        self.ent_author = ctk.CTkEntry(form_frame, placeholder_text=_("ชื่อทีมแปล / ผู้แปลหลัก [เว้นว่างได้]"))
        self.ent_author.grid(row=row, column=1, sticky="ew", pady=10, padx=(0, 10))
        self.ent_author.insert(0, self.parent.config.get("default_author", ""))
        
        self.btn_save_author = ctk.CTkButton(form_frame, text=_("💾 จำค่า"), width=80, fg_color="#313244", hover_color="#45475a", command=lambda: self.save_default_value("default_author", self.ent_author.get()))
        self.btn_save_author.grid(row=row, column=2, sticky="ew", pady=10)
        row += 1
        
        # 3. Contributors
        ctk.CTkLabel(form_frame, text=_("ผู้ร่วมแปล / ทีมงาน:"), font=ctk.CTkFont(weight="bold"), anchor="w").grid(row=row, column=0, sticky="w", pady=10)
        self.ent_contributors = ctk.CTkEntry(form_frame, placeholder_text=_("ชื่อสมาชิกคนอื่นๆ [เว้นว่างได้]"))
        self.ent_contributors.grid(row=row, column=1, sticky="ew", pady=10, padx=(0, 10))
        self.ent_contributors.insert(0, self.parent.config.get("default_contributors", ""))
        
        self.btn_save_contributors = ctk.CTkButton(form_frame, text=_("💾 จำค่า"), width=80, fg_color="#313244", hover_color="#45475a", command=lambda: self.save_default_value("default_contributors", self.ent_contributors.get()))
        self.btn_save_contributors.grid(row=row, column=2, sticky="ew", pady=10)
        row += 1
        
        # 4. Project Link
        ctk.CTkLabel(form_frame, text=_("ลิงก์โปรเจกต์ / GitHub:"), font=ctk.CTkFont(weight="bold"), anchor="w").grid(row=row, column=0, sticky="w", pady=10)
        self.ent_link = ctk.CTkEntry(form_frame, placeholder_text=_("เช่น ลิงก์เพจเฟซบุ๊ก หรือลิงก์ Git [เว้นว่างได้]"))
        self.ent_link.grid(row=row, column=1, columnspan=2, sticky="ew", pady=10)
        row += 1
        
        # 5. Workspace Path
        ctk.CTkLabel(form_frame, text=_("ตำแหน่งโปรเจกต์ *:"), font=ctk.CTkFont(weight="bold"), anchor="w").grid(row=row, column=0, sticky="w", pady=10)
        self.ent_path = ctk.CTkEntry(form_frame, placeholder_text=_("เลือกโฟลเดอร์สำหรับสร้างพื้นที่ทำงาน..."))
        self.ent_path.grid(row=row, column=1, sticky="ew", pady=10, padx=(0, 10))
        if is_import_mode and initial_path:
            self.ent_path.insert(0, initial_path)
            self.ent_path.configure(state="disabled")
            
        self.btn_browse_path = ctk.CTkButton(form_frame, text=_("📂 เลือก"), width=80, fg_color="#313244", hover_color="#45475a", command=self.browse_workspace)
        self.btn_browse_path.grid(row=row, column=2, sticky="ew", pady=10)
        if is_import_mode:
            self.btn_browse_path.configure(state="disabled")
        row += 1
        
        # 6. Game Directory
        self.lbl_game_dir = ctk.CTkLabel(form_frame, text=_("ตำแหน่งติดตั้งเกม (Game Dir):"), font=ctk.CTkFont(weight="bold"), anchor="w")
        self.lbl_game_dir.grid(row=row, column=0, sticky="w", pady=10)
        self.ent_game_dir = ctk.CTkEntry(form_frame, placeholder_text=_("เลือกโฟลเดอร์ติดตั้งเกม (Steam/Epic) [ข้ามได้]"))
        self.ent_game_dir.grid(row=row, column=1, sticky="ew", pady=10, padx=(0, 10))
        
        self.btn_browse_game = ctk.CTkButton(form_frame, text=_("📂 เลือก"), width=80, fg_color="#313244", hover_color="#45475a", command=self.browse_game_dir)
        self.btn_browse_game.grid(row=row, column=2, sticky="ew", pady=10)
        row += 1
        
        # 6.5 Tool Directory
        self.lbl_tool_dir = ctk.CTkLabel(form_frame, text=_("ตำแหน่งเครื่องมือ (Tool Dir):"), font=ctk.CTkFont(weight="bold"), anchor="w")
        self.lbl_tool_dir.grid(row=row, column=0, sticky="w", pady=10)
        self.ent_tool_dir = ctk.CTkEntry(form_frame, placeholder_text=_("เลือกโฟลเดอร์ที่เก็บเครื่องมือม็อด (Unpack/Repack) [ข้ามได้]"))
        self.ent_tool_dir.grid(row=row, column=1, sticky="ew", pady=10, padx=(0, 10))
        
        self.btn_browse_tool = ctk.CTkButton(form_frame, text=_("📂 เลือก"), width=80, fg_color="#313244", hover_color="#45475a", command=self.browse_tool_dir)
        self.btn_browse_tool.grid(row=row, column=2, sticky="ew", pady=10)
        
        if is_import_mode:
            self.lbl_game_dir.grid_forget()
            self.ent_game_dir.grid_forget()
            self.btn_browse_game.grid_forget()
            self.lbl_tool_dir.grid_forget()
            self.ent_tool_dir.grid_forget()
            self.btn_browse_tool.grid_forget()
        row += 1
        
        # 7. Notes
        ctk.CTkLabel(form_frame, text=_("คำอธิบาย / บันทึกย่อ:"), font=ctk.CTkFont(weight="bold"), anchor="w").grid(row=row, column=0, sticky="w", pady=10)
        self.ent_notes = ctk.CTkEntry(form_frame, placeholder_text=_("เช่น รายละเอียดเกี่ยวกับวิธีแกะฟอนต์ ข้อมูลสเปกต่างๆ [เว้นว่างได้]"))
        self.ent_notes.grid(row=row, column=1, columnspan=2, sticky="ew", pady=10)
        row += 1
        
        # Setup shortcut bindings to guarantee copy-paste
        for entry in [self.ent_name, self.ent_author, self.ent_contributors, self.ent_link, self.ent_path, self.ent_game_dir, self.ent_tool_dir, self.ent_notes]:
            self.bind_common_shortcuts(entry)
            
        # Action buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", side="bottom", pady=25)
        
        btn_cancel = ctk.CTkButton(btn_frame, text=_("❌ ยกเลิก"), fg_color="#f38ba8", hover_color="#eba0ac", text_color="#1e1e2e", font=ctk.CTkFont(weight="bold"), command=self.destroy)
        btn_cancel.pack(side="right", padx=(10, 40))
        
        btn_create = ctk.CTkButton(btn_frame, text=_("🚀 นำเข้าโปรเจกต์") if is_import_mode else _("🚀 สร้างโปรเจกต์"), fg_color="#a6e3a1", hover_color="#94e2d5", text_color="#1e1e2e", font=ctk.CTkFont(weight="bold"), command=self.on_submit)
        btn_create.pack(side="right")
        
    def bind_common_shortcuts(self, entry):
        def select_all(event):
            entry.select_range(0, 'end')
            entry.icursor('end')
            return 'break'
        entry.bind("<Control-Key-a>", select_all)
        entry.bind("<Control-Key-A>", select_all)
        
    def save_default_value(self, key, value):
        self.parent.config[key] = value.strip()
        self.parent.save_local_config()
        messagebox.showinfo(_("Saved"), _("บันทึกค่าเริ่มต้นสำเร็จ!"), parent=self)
        
    def browse_workspace(self):
        folder = filedialog.askdirectory(title=_("เลือกโฟลเดอร์สำหรับสร้างพื้นที่ทำงาน (Workspace)"), parent=self)
        if folder:
            self.base_workspace_dir = folder
            self.update_path_preview()
            
    def on_name_change(self, event):
        if hasattr(self, 'base_workspace_dir') and self.base_workspace_dir:
            self.update_path_preview()
            
    def update_path_preview(self):
        if not hasattr(self, 'base_workspace_dir') or not self.base_workspace_dir:
            return
            
        proj_name = self.ent_name.get().strip().replace(" ", "_")
        
        # Clean invalid filename characters
        import re
        proj_name = re.sub(r'[\\/*?:"<>|]', "", proj_name)
        
        if proj_name:
            target_path = os.path.join(self.base_workspace_dir, proj_name)
        else:
            target_path = self.base_workspace_dir
            
        self.ent_path.delete(0, 'end')
        self.ent_path.insert(0, target_path)
            
    def browse_game_dir(self):
        folder = filedialog.askdirectory(title=_("เลือกโฟลเดอร์ติดตั้งเกม (Game Directory)"), parent=self)
        if folder:
            self.ent_game_dir.delete(0, 'end')
            self.ent_game_dir.insert(0, folder)
            
    def browse_tool_dir(self):
        folder = filedialog.askdirectory(title=_("เลือกโฟลเดอร์เครื่องมือม็อด (Tool Directory)"), parent=self)
        if folder:
            self.ent_tool_dir.delete(0, 'end')
            self.ent_tool_dir.insert(0, folder)
            
    def on_submit(self):
        name = self.ent_name.get().strip()
        author = self.ent_author.get().strip()
        contributors = self.ent_contributors.get().strip()
        link = self.ent_link.get().strip()
        
        if self.is_import_mode:
            path = self.initial_path
        else:
            path = self.ent_path.get().strip()
            
        game_dir = self.ent_game_dir.get().strip()
        tool_dir = self.ent_tool_dir.get().strip()
        notes = self.ent_notes.get().strip()
        source_lang = self.cbo_source_lang.get().strip()
        target_lang = self.cbo_target_lang.get().strip()
        profile_name = getattr(self, "ent_profile", None)
        profile_name = profile_name.get().strip() if profile_name is not None else ""
        
        if not name:
            messagebox.showerror(_("Error"), _("กรุณากรอกชื่อโปรเจกต์"), parent=self)
            return
        if not path:
            messagebox.showerror(_("Error"), _("กรุณาเลือกโฟลเดอร์สำหรับทำโปรเจกต์"), parent=self)
            return
            
        self.result = {
            "name": name,
            "author": author,
            "contributors": contributors,
            "link": link,
            "path": path,
            "game_dir": game_dir,
            "tool_dir": tool_dir,
            "notes": notes,
            "source_lang": source_lang,
            "target_lang": target_lang,
            "profile_name": profile_name
        }
        self.destroy()

# Constants
CURRENT_VERSION = "1.1.0"
UPDATE_FILE_PATH = os.path.join(os.path.dirname(__file__), "updates.json")
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hub_config.json")
KNOWLEDGE_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Modding-Knowledge"))

TOOL_REGISTRY = {
    "Unreal Engine": [
        {"name": "FModel", "desc": "โปรแกรมเปิดไฟล์ .pak ของ Unreal Engine", "github": "4sval/FModel"},
        {"name": "UnrealPakTool", "desc": "เครื่องมือแพ็ก/แตกไฟล์ .pak", "url": "https://fluffyquack.com/tools/"},
        {"name": "UAssetGUI", "desc": "แก้ไขไฟล์ UAsset ทะลุทะลวง", "github": "atenfyr/UAssetGUI"}
    ],
    "Unity": [
        {"name": "AssetStudio", "desc": "เครื่องมือแกะไฟล์ Unity สุดฮิต", "github": "Perfare/AssetStudio"},
        {"name": "UnityCN-EasyTool", "desc": "เครื่องมือแพ็ก/แตกไฟล์ Asset ของ Unity ครบวงจร", "github": "memolyviza2012-max/UnityCN-EasyTool"},
        {"name": "UABE", "desc": "Unity Asset Bundle Extractor", "github": "SeriousCache/UABE"},
        {"name": "XUnity.AutoTranslator", "desc": "แปลภาษาเกม Unity ดึงจอแบบสดๆ", "github": "bbepis/XUnity.AutoTranslator"}
    ],
    "RE Engine & Frostbite": [
        {"name": "Fluffy Mod Manager", "desc": "โปรแกรมจัดการม็อดเกมค่าย Capcom", "direct_zip": "https://fluffyquack.com/tools/modmanager.zip", "url": "https://www.fluffyquack.com/"},
        {"name": "RETool", "desc": "เครื่องมือบีบอัด/แตกไฟล์ RE Engine", "url": "https://residentevilmodding.boards.net/"},
        {"name": "Frosty Toolsuite", "desc": "เครื่องมือสำหรับ Frostbite Engine", "url": "https://frostytoolsuite.com/"}
    ],
    "General / Text Editors": [
        {"name": "QuickBMS", "desc": "สคริปต์สกัดไฟล์ครอบจักรวาล", "direct_zip": "http://aluigi.altervista.org/papers/quickbms.zip", "url": "http://aluigi.altervista.org/quickbms.htm"},
        {"name": "HxD (Hex Editor)", "desc": "แก้ไขไฟล์ไบนารีและเจาะโค้ดขั้นสูง", "url": "https://mh-nexus.de/en/hxd/"},
        {"name": "Notepad++", "desc": "ตัวเปิดไฟล์ข้อความที่นักม็อดต้องมี", "github": "notepad-plus-plus/notepad-plus-plus"}
    ]
}

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class AIHelperDialog(ctk.CTkToplevel):
    def __init__(self, parent, proj):
        super().__init__(parent)
        self.parent = parent
        self.proj = proj
        self.title(_("🤖 คัดลอก Master Prompt"))
        self.geometry("780x820")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

        self.current_prompt = ""

        # --- Header ---
        self.lbl_title = ctk.CTkLabel(self, text=f"AI Helper: {proj.get('name')}", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_title.pack(pady=(20, 4))

        self.lbl_desc = ctk.CTkLabel(self, text=_("เลือกโหมดและคัดลอกคำสั่งไปวางใน AI ที่คุณใช้งาน"), text_color="gray")
        self.lbl_desc.pack(pady=(0, 10))

        # --- Segmented Button (Tabs) ---
        self.tab_var = ctk.StringVar(value=_("💬 โหมดที่ปรึกษา (วางใน ChatGPT / Claude)"))
        self.seg_btn = ctk.CTkSegmentedButton(
            self,
            values=[_("💬 โหมดที่ปรึกษา (วางใน ChatGPT / Claude)"), _("💻 โหมดปฏิบัติการ (Codex / Claude Code / Antigravity)")],
            variable=self.tab_var,
            command=self.on_tab_change,
            font=ctk.CTkFont(weight="bold")
        )
        self.seg_btn.pack(pady=(0, 10), padx=40, fill="x")

        # --- Agent Options Panel (built early so textbox can reference it) ---
        self.agent_options_frame = ctk.CTkFrame(self, fg_color="#1e1e2e", corner_radius=10)

        opt_label = ctk.CTkLabel(self.agent_options_frame, text=_("⚙️ ตัวเลือกพฤติกรรม Agent"),
                                 font=ctk.CTkFont(weight="bold", size=13), text_color="#cdd6f4")
        opt_label.pack(anchor="w", padx=16, pady=(10, 6))

        self._chk_vars = {}

        def _add_checkbox(key, label, default, description):
            var = ctk.BooleanVar(value=default)
            self._chk_vars[key] = var
            row = ctk.CTkFrame(self.agent_options_frame, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=2)
            ctk.CTkCheckBox(row, text=label, variable=var, onvalue=True, offvalue=False,
                            command=self.rebuild_agent_prompt,
                            font=ctk.CTkFont(size=12, weight="bold"),
                            fg_color="#89b4fa", hover_color="#74c7ec",
                            text_color="#cdd6f4", checkmark_color="#1e1e2e").pack(side="left")
            ctk.CTkLabel(row, text=description, text_color="#585b70",
                         font=ctk.CTkFont(size=11)).pack(side="left", padx=(8, 0))

        _add_checkbox("auto_tool",   _("🔧 ค้นหา & ดาวน์โหลดเครื่องมืออัตโนมัติ"),      True,  _("→ ถ้าไม่เจอให้หาโหลดเองจาก GitHub"))
        _add_checkbox("obstacle",    _("🚧 รายงานข้อจำกัดและเสนอทางเลือก"),               True,  _("→ หยุดถามผู้ใช้เมื่อติดขัด"))
        _add_checkbox("write_log",   _("📋 บันทึก Log การทำงานไว้ใน Workspace"),           True,  _("→ session_log.md ใน 05_Scripts_and_Tools"))
        _add_checkbox("min_confirm", _("✅ ถามก่อนทำ Destructive Actions เท่านั้น"),       False, _("→ ไม่ถามซ้ำในทุกขั้นตอน"))
        _add_checkbox("deep_scan",   _("🔬 Deep Scan Mode (ละเอียดขึ้น, ช้าขึ้น)"),        False, _("→ ไม่ข้ามไฟล์ที่ไม่รู้จัก"))
        _add_checkbox("mem_hook",    _("🧩 อนุญาต Memory Hook Fallback (BepInEx ฯลฯ)"),   False, _("→ ใช้เมื่อแกะ archive โดยตรงไม่ได้"))

        # --- Textbox for Prompt (editable so user can tweak before copying) ---
        self.textbox = ctk.CTkTextbox(self, font=ctk.CTkFont(family="Consolas", size=12))
        self.textbox.pack(fill="both", expand=True, padx=20, pady=(0, 6))

        # --- Bottom Frame ---
        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.pack(fill="x", padx=20, pady=(0, 16))

        self.btn_copy = ctk.CTkButton(
            self.bottom_frame,
            text=_("📋 คัดลอก Prompt (Copy to Clipboard)"),
            height=45,
            font=ctk.CTkFont(weight="bold", size=15),
            fg_color="#f38ba8", text_color="#11111b", hover_color="#eba0ac",
            command=self.copy_prompt
        )
        self.btn_copy.pack(fill="x")

        self.on_tab_change(self.tab_var.get())

    # ── Tab / Mode switching ────────────────────────────────────────────────
    def on_tab_change(self, value):
        # We check for "Codex" or "Antigravity" to match the new Tab 2 name
        if "Codex" in value or "Antigravity" in value:
            self.agent_options_frame.pack(fill="x", padx=20, pady=(0, 8), before=self.textbox)
            self.rebuild_agent_prompt()
        else:
            self.agent_options_frame.pack_forget()
            self._set_textbox(self.get_chat_prompt())

    def rebuild_agent_prompt(self):
        prompt = self.get_agent_prompt()
        self._set_textbox(prompt)
        # Silently save ai_instructions.md
        try:
            proj_path = self.proj.get("path", "")
            if os.path.exists(proj_path):
                with open(os.path.join(proj_path, "ai_instructions.md"), "w", encoding="utf-8") as f:
                    f.write(prompt)
        except Exception:
            pass

    def _set_textbox(self, text):
        self.current_prompt = text
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", text)

    def copy_prompt(self):
        # Read live editable content so user-tweaks are preserved
        self.current_prompt = self.textbox.get("1.0", "end").strip()
        if self.current_prompt:
            self.clipboard_clear()
            self.clipboard_append(self.current_prompt)
            self.update()
            from tkinter import messagebox
            messagebox.showinfo(
                _("Copied"),
                _("คัดลอก Master Prompt ลง Clipboard เรียบร้อยแล้ว!\nนำไปวางในเครื่องมือ AI ของคุณได้เลย"),
                parent=self
            )

    # ── Chat Prompt (bilingual) ──────────────────────────────────────────────
    def get_chat_prompt(self):
        name        = self.proj.get("name", "Unknown")
        path        = self.proj.get("path", "Unknown")
        app_lang    = self.parent.config.get("app_lang", "th")
        game_dir    = self.proj.get("game_dir",  _("[รอการระบุตำแหน่งติดตั้งเกมจากผู้ใช้]") if app_lang == "th" else "[Game directory not set]")
        tool_dir    = self.proj.get("tool_dir",  _("[รอการระบุตำแหน่งโฟลเดอร์เครื่องมือ]") if app_lang == "th" else "[Tool directory not set]")
        source_lang = self.proj.get("source_lang", "English")
        target_lang = self.proj.get("target_lang", "Thai")

        if app_lang == "th":
            template = """🎮 Master Prompt: Game Localization Consultant ({target_lang} Mod) - THub Edition

Context & Role: 
ฉันกำลังสร้าง Mod แปลภาษาระดับมืออาชีพสำหรับเกม: {name} 
โดยทำการแปลจากภาษา **{source_lang}** เป็นภาษา **{target_lang}**
เนื่องจากคุณทำงานบน Web Chat (เบราว์เซอร์) คุณจะ **ไม่มีสิทธิ์เข้าถึงไฟล์ในเครื่องของฉัน** 
ดังนั้น บทบาทของคุณคือ "ผู้เชี่ยวชาญให้คำปรึกษาและผู้เขียน Python Script" โดยฉันจะเป็นคนนำ Script ที่คุณเขียนไปรันบนเครื่องของฉันเอง

Environment & Workspace ของฉัน (เพื่อใช้อ้างอิงในการเขียนโค้ด):
- Workspace: {path} (ใช้โครงสร้าง 01 ถึง 06 ของ THub)
- Game Directory: {game_dir}
- Tool Directory: {tool_dir}
- Modding Knowledge Base: {KNOWLEDGE_DIR}

[สำคัญ] กฎการให้คำปรึกษาและเขียนโค้ด:
1. การเขียน Script ทั้งหมด ต้องอ้างอิงตำแหน่งโฟลเดอร์ตาม Workspace ด้านบน
2. โฟลเดอร์ "01_Original_Backup" ถือเป็นไฟล์ต้นฉบับดั้งเดิม (Read-Only) ห้ามเขียน Script ที่เข้าไปดัดแปลงไฟล์ในนั้น ให้เขียน Script คัดลอกออกมาก่อนเสมอ
3. เมื่อคุณเขียนโค้ด Python โปรดแสดงโค้ดฉบับเต็มที่รันได้จริงเสมอ ห้ามใช้ Placeholder (เช่น # โค้ดส่วนที่เหลือ) ย่อโค้ดเด็ดขาด
4. เมื่อฉันส่งข้อความสั้นๆ, โครงสร้างไฟล์, หรือ Error Code ไป ให้คุณวิเคราะห์ว่าต้องใช้เครื่องมืออะไร และเขียน Script ให้ฉันทีละขั้นตอน

Milestones ที่คุณต้องคอยซัพพอร์ตและเขียน Script ให้ฉัน (เมื่อฉันบอกว่า "เริ่มขั้นตอนที่..." ค่อยให้คำแนะนำ):

1. Extraction & Analysis (วิเคราะห์และสกัดไฟล์ภาษา)
   - ฉันจะส่งข้อมูล Engine ให้คุณวิเคราะห์ หรือขอให้คุณเขียน Script สำหรับค้นหาไฟล์ข้อความ
2. Font & UI Architecture (ทำฟอนต์ภาษา {target_lang})
   - ช่วยฉันวางแผนการทำฟอนต์แบบ PUA (สระหลบหลีก) และเขียนโค้ดคำนวณการเลื่อนสระ
3. Pre-Translation Glossary (ดึงคำศัพท์เฉพาะ)
   - เขียน Script สแกนไฟล์ข้อความทั้งหมดเพื่อดึง "คำเฉพาะ" ออกมาให้ฉันสร้าง Glossary
4. Proof of Concept (แปลและทดสอบหน้าเมนูหลัก)
   - เขียน Script ช่วยดึง/ใส่ข้อความกลับ เพื่อให้ฉันทดสอบหน้า Main Menu
5. Script Customization & Safety Rules (พัฒนาเครื่องมือช่วยแปล)
   - เขียน Script สำหรับดึง/ใส่ข้อความ โดยต้องมีระบบป้องกันไม่ให้แก้ไขแท็กโค้ดของเกม (เช่น %s, {{0}}, <color=red>) อย่างเด็ดขาด
6. Mass Translation & Automated QA (สแกนข้อผิดพลาดก่อนแพ็ค)
   - เขียน Validator Script เพื่อช่วยฉันเทียบเช็คความถูกต้องว่าแท็กโค้ดของไฟล์แปล หล่นหายไปหรือไม่
7. Final Playtest & Release (ทดสอบและบิลด์ม็อด)
   - เขียน Script สร้างไฟล์ .zip สำหรับแจกจ่ายงาน

Instructions for AI:
หากเข้าใจบทบาทของคุณแล้ว ให้ตอบกลับสั้นๆ ว่า "รับทราบ! กรุณาบอกข้อมูล Engine ของเกม หรือส่งตัวอย่างไฟล์มาให้ฉันวิเคราะห์เพื่อเขียน Script ให้คุณในขั้นตอนที่ 1 ได้เลยครับ\""""
        else:
            template = """🎮 Master Prompt: Game Localization Consultant ({target_lang} Mod) - THub Edition

Context & Role: 
I am creating a professional localization Mod for the game: {name} 
Translating from **{source_lang}** to **{target_lang}**.
Since you are operating in a Web Chat environment (browser), you **DO NOT have access to my local files**. 
Therefore, your role is strictly an "Expert Consultant & Python Script Writer". I will run the scripts you write on my local machine.

My Environment & Workspace (Reference for writing code):
- Workspace: {path} (Using THub's 01 to 06 folder structure)
- Game Directory: {game_dir}
- Tool Directory: {tool_dir}
- Modding Knowledge Base: {KNOWLEDGE_DIR}

[IMPORTANT] Consulting & Coding Rules:
1. All scripts you write must output files within the Workspace defined above.
2. The "01_Original_Backup" folder is Read-Only. Never write scripts that modify it. Always copy files out first.
3. When providing Python code, always write the FULL, runnable script. Never use placeholders (like `# rest of the code`).
4. When I provide short context, hex dumps, or error logs, analyze what tools/methods are needed and write a step-by-step script for me to execute.

Milestones to Support Me (Give advice when I say "Start Step..."):

1. Extraction & Analysis
   - I will provide Engine info, or you will write scripts for me to scan for language files.
2. Font & UI Architecture ({target_lang})
   - Help plan PUA character encoding and write scripts to calculate font bounds/rendering.
3. Pre-Translation Glossary
   - Write a script to scan all text files and extract specific terms to help me build a Glossary.
4. Proof of Concept
   - Write scripts to extract/inject text specifically for the Main Menu to test rendering.
5. Script Customization & Safety Rules
   - Write extraction/injection scripts. [Hard Rule] Scripts must never modify or delete game tags/variables (e.g., %s, {{0}}, <color=red>).
6. Mass Translation & Automated QA
   - Write a Validator Script for me to cross-check {target_lang} vs {source_lang} files for missing variables/tags.
7. Final Playtest & Release
   - Write a script to build the final .zip release file.

Instructions for AI: 
If you understand your role, reply briefly with: "Understood! Please provide the game's Engine information or send me a sample file to analyze so I can write the Script for Step 1.\""""

        return template.format(
            name=name, source_lang=source_lang, target_lang=target_lang,
            path=path, game_dir=game_dir, tool_dir=tool_dir,
            KNOWLEDGE_DIR=KNOWLEDGE_DIR
        )

    # ── Agent Prompt (bilingual) ─────────────────────────────────────────────
    def get_agent_prompt(self):
        name        = self.proj.get("name", "Unknown")
        path        = self.proj.get("path", "Unknown")
        app_lang    = self.parent.config.get("app_lang", "th")
        game_dir    = self.proj.get("game_dir",  "[รอการระบุตำแหน่งติดตั้งเกมจากผู้ใช้]" if app_lang == "th" else "[Game directory not set]")
        tool_dir    = self.proj.get("tool_dir",  "[รอการระบุตำแหน่งโฟลเดอร์เครื่องมือ]" if app_lang == "th" else "[Tool directory not set]")
        source_lang = self.proj.get("source_lang", "English")
        target_lang = self.proj.get("target_lang", "Thai")

        opt = {k: v.get() for k, v in self._chk_vars.items()}
        is_en = (app_lang != "th")

        # ── Core Prompt Block ──────────────────────────────────────────────
        if is_en:
            parts = [f"""🎮 Master Prompt: Game Localization Project ({target_lang} Mod) - THub Edition

Context & Goal: 
I want to create a professional localization Mod for the game: {name} 
Translating from **{source_lang}** to **{target_lang}**.
We will work together step-by-step in a systematic and safe manner. Here is the project overview:

Environment & Workspace:
- Workspace: {path} (Using THub's 01 to 06 folder structure)
- Game Directory: {game_dir}
- Tool Directory: {tool_dir}
- Modding Knowledge Base: {KNOWLEDGE_DIR}

[IMPORTANT] Workspace Safety Rules:
1. Never create working files outside this Workspace.
2. The "01_Original_Backup" folder is the original backup (Read-Only). Never overwrite or modify it. Use it for reading and backup only.

Milestones & Workflow (Execute step-by-step. Only move to the next step when I say "Proceed to step..."):

1. Extraction & Analysis:
   - Study the game Engine and search the Modding-Knowledge base for guidance.
   - Locate language files and extract text (dialogues, UI, cutscenes) into 01_Original_Backup.
   - Analyze original file Encoding (e.g., UTF-8, UTF-8 with BOM, or ANSI) to maintain exact encoding.
   - Analyze archive structures (.pak, .arc, .bin, etc.) to identify required Unpack/Pack tools.

2. Font & UI Architecture ({target_lang}):
   - Check where original fonts are stored and their format (.ttf, .otf, Font Atlas/Sprite).
   - Plan character encoding/PUA mapping and prepare the {target_lang} font in 03_Font_and_UI.

3. Pre-Translation Glossary:
   - Scan all text files to extract specific terms (character names, locations, items, skills) into a list for me to define as a standard GLOSSARY.
   - Translated terms must be maintained for reference throughout the project.

4. Proof of Concept (Main Menu translation and test):
   - Translate only the "Main Menu" text in 02_Translation_Workspace, keeping it concise for UI fit.
   - Pack the menu files and fonts, then test in 04_Packed_Mod to confirm font rendering is correct.

5. Script Customization & Safety Rules:
   - Develop or modify scripts to extract/inject translated text, storing them in 05_Scripts_and_Tools.
   - [Hard Rule] Scripts must never modify or delete game tags/variables (e.g. %s, {{0}}, <color=red>, \\n, \\r).
   - After writing scripts, wait for me to provide API Keys and update the Glossary before proceeding.
   - [Coding Rule] Always provide full, runnable code. Never use placeholders.

6. Mass Translation & Automated QA:
   - Translate all remaining text as instructed.
   - Before packing, write a Validator Script to cross-check {target_lang} vs {source_lang} files for missing variables (%s) or mismatched tags. Report errors and stop if found.

7. Final Playtest & Release:
   - Run the game for a real playtest, checking for crashes or font glitches.
   - When ready for release, create a final build (.zip) in the 06_Releases folder.

Instructions for AI: 
If you understand the goals, folder structure, and Milestone agreements, confirm your understanding and immediately begin "Step 1 (Extraction & Analysis)" by telling me which folder you will scan and what additional information you need to identify the game Engine."""]
        else:
            parts = [f"""🎮 Master Prompt: Game Localization Project ({target_lang} Mod) - THub Edition

Context & Goal: 
ฉันต้องการสร้าง Mod แปลภาษาระดับมืออาชีพสำหรับเกม: {name} 
โดยจะทำการแปลจากภาษา **{source_lang}** เป็นภาษา **{target_lang}**
เราจะทำงานร่วมกันทีละขั้นตอนอย่างเป็นระบบและปลอดภัย นี่คือข้อมูลเบื้องต้นของโปรเจค:

Environment & Workspace:
- Workspace: {path} (ใช้โครงสร้าง 01 ถึง 06 ของ THub)
- Game Directory: {game_dir}
- ตำแหน่งเครื่องมือ: {tool_dir}
- แหล่งอ้างอิงข้อมูลม็อด: {KNOWLEDGE_DIR}

[สำคัญ] กฎความปลอดภัยของ Workspace:
1. ห้ามสร้างไฟล์ทำงานนอกเหนือจาก Workspace นี้เด็ดขาด
2. โฟลเดอร์ "01_Original_Backup" ถือเป็นไฟล์ต้นฉบับดั้งเดิม (Read-Only) ห้ามทำการเขียนทับหรือแก้ไขเด็ดขาด ให้ใช้สำหรับการอ่านและแบ็คอัปเท่านั้น

Milestones & Workflow (ทำทีละขั้นตอน เมื่อฉันบอกว่า "ผ่านขั้นตอนที่..." จึงจะย้ายไปข้อถัดไป):

1. Extraction & Analysis (สกัดไฟล์และวิเคราะห์โครงสร้าง):
   - ศึกษา Engine เกม และค้นหาข้อมูลจาก Modding-Knowledge เพื่อเป็นแนวทาง
   - ค้นหาพิกัดไฟล์ภาษาและสกัดไฟล์ข้อความ (บทสนทนา, UI, คัทซีน) ออกมาเก็บไว้ใน 01_Original_Backup
   - วิเคราะห์ Encoding ของไฟล์ดั้งเดิม (เช่น UTF-8, UTF-8 with BOM, หรือ ANSI) เพื่อรักษารหัสไฟล์ให้ตรงตามเดิมป้องกันสระภาษา{target_lang}เสีย
   - วิเคราะห์โครงสร้างก้อนไฟล์ (.pak, .arc, .bin ฯลฯ) เพื่อระบุเครื่องมือ Unpack/Pack ที่ต้องใช้

2. Font & UI Architecture (วิเคราะห์ระบบฟอนต์ภาษา {target_lang}):
   - ตรวจสอบฟอนต์ดั้งเดิมของเกมว่าเก็บอยู่ที่ใดและเป็นฟอร์แมตไหน (.ttf, .otf, Font Atlas/Sprite)
   - วางแผนกระบวนการเข้ารหัสวรรณยุกต์ไทย/สระลอย (เช่น การแปลงสระหลบหลีกเข้าช่วง PUA) และเตรียมฟอนต์ภาษา{target_lang}ให้พร้อมใช้ใน 03_Font_and_UI

3. Pre-Translation Glossary (ดึงคำศัพท์เฉพาะ):
   - ก่อนรันการแปล สแกนไฟล์ข้อความทั้งหมดเพื่อสกัด "คำเฉพาะ" (ชื่อตัวละคร, สถานที่, ไอเทม, ทักษะ) ออกมาแสดงเป็นลิสต์ให้ฉันกำหนดคำศัพท์มาตรฐาน (GLOSSARY)
   - ลิสต์คำศัพท์ที่แปลเรียบร้อยแล้วต้องเก็บไว้ใช้อ้างอิงการแปลตลอดทั้งโปรเจค

4. Proof of Concept (แปลและทดสอบหน้าเมนูหลัก):
   - แปลข้อความเฉพาะส่วน "หน้าเมนูหลัก (Main Menu)" ใน 02_Translation_Workspace โดยเน้นความกระชับไม่ล้นกรอบ UI
   - แพ็คไฟล์เมนูและฟอนต์ที่เตรียมไว้ไปวางทดสอบใน 04_Packed_Mod เพื่อยืนยันว่าฟอนต์ภาษา{target_lang}แสดงผลได้สระไม่เยื้อง/ไม่เป็นกล่องสี่เหลี่ยมเต้าหู้

5. Script Customization & Safety Rules (พัฒนาเครื่องมือช่วยแปล):
   - พัฒนาหรือดัดแปลงสคริปต์สำหรับช่วยดึง/ใส่ข้อความแปลเก็บไว้ใน 05_Scripts_and_Tools
   - [กฎเหล็ก] สคริปต์ต้องห้ามแก้ไข ปรับเปลี่ยน หรือลบแท็กโค้ดและตัวแปรของเกมเด็ดขาด (เช่น %s, {{0}}, <color=red>, \\n, \\r)
   - เมื่อเขียนสคริปต์เสร็จแล้ว ให้หยุดรอฉันป้อน API Key และอัปเดตไฟล์ Glossary ก่อนเริ่มกระบวนการถัดไป
   - [กฎการเขียนโค้ด] เมื่อเขียนสคริปต์หรือโปรแกรม ให้แสดงโค้ดฉบับเต็มเสมอ ห้ามใช้ Placeholder ย่อโค้ดเด็ดขาด

6. Mass Translation & Automated QA (แปลชุดใหญ่และสแกนข้อผิดพลาด):
   - ทำการแปลข้อความที่เหลือทั้งหมดตามคำสั่ง
   - ก่อนจะแพ็คไฟล์กลับ ให้เขียนสคริปต์สแกนตรวจสอบความถูกต้อง (Validator Script) เพื่อเช็คเทียบไฟล์ภาษา{target_lang} กับ {source_lang} ว่ามีตัวแปร (%s) หรือแท็กเปิด/ปิดใดๆ หล่นหายไปหรือไม่ หากตรวจพบ Error ให้แจ้งและหยุดทันที

7. Final Playtest & Release (ทดสอบการเล่นจริงและส่งมอบ):
   - ทำการรันเกมเพื่อทดสอบเล่นจริง ตรวจเช็คการแครชและสระต่างดาว
   - หากพร้อมแจกจ่าย ให้สร้างไฟล์บิลด์สำเร็จรูป (.zip) ไปเก็บไว้ที่โฟลเดอร์ 06_Releases เพื่อส่งมอบงาน

Instructions for AI: 
หากเข้าใจเป้าหมาย โครงสร้างโฟลเดอร์ และข้อตกลงในการทำ Milestones ทั้งหมดแล้ว ให้ยืนยันความเข้าใจ และเริ่มทำงานใน "ขั้นตอนที่ 1 (Extraction & Analysis)" ได้ทันที โดยบอกฉันว่าคุณจะสแกนโฟลเดอร์ใดและต้องการข้อมูลอะไรเพิ่มเติมบ้างเพื่อระบุ Engine ของเกม"""]

        # ── Optional Protocol Blocks ────────────────────────────────────────
        if opt.get("auto_tool"):
            if is_en:
                parts.append(f"""
══════════════════════════════════════════════════════
[Protocol A] Auto Tool Discovery & Download 🔧
══════════════════════════════════════════════════════
When a tool is needed and not found in {tool_dir}:

  Step 1 — Search locally:
    Recursively scan {tool_dir} for .exe / .py / .jar
    matching the required function (e.g. UnrealPak.exe, quickbms.exe).

  Step 2 — Auto-download:
    If not found, search GitHub for the latest open-source release
    (UEViewer, QuickBMS, 7-Zip CLI, AssetStudio, etc.)
    Download the latest binary to {tool_dir}.
    Report: "Downloaded [tool] v[version] → {tool_dir}. Continuing..."

  Step 3 — Report failure:
    If download fails, stop immediately and present:
      [A] Please provide the location of [tool].
      [B] I will try an alternative approach: [describe alternative].
      [C] Skip this step and continue with limited capability.
    → Wait for user decision before continuing.""")
            else:
                parts.append(f"""
══════════════════════════════════════════════════════
[โปรโตคอล A] ค้นหาและโหลดเครื่องมืออัตโนมัติ 🔧
══════════════════════════════════════════════════════
เมื่อต้องการเครื่องมือและไม่พบใน {tool_dir}:

  ขั้น 1 — ค้นหาในเครื่อง:
    สแกน {tool_dir} แบบ Recursive หา .exe / .py / .jar
    ที่ทำหน้าที่ตรงกับที่ต้องการ (เช่น UnrealPak.exe, quickbms.exe)

  ขั้น 2 — ดาวน์โหลดอัตโนมัติ:
    หากไม่เจอ ให้ค้นหา Open-Source Release ล่าสุดบน GitHub
    (UEViewer, QuickBMS, 7-Zip CLI, AssetStudio ฯลฯ)
    แล้วดาวน์โหลด Binary ล่าสุดมาไว้ใน {tool_dir}
    รายงาน: "ดาวน์โหลด [เครื่องมือ] v[เวอร์ชัน] → {tool_dir} สำเร็จ กำลังดำเนินการต่อ..."

  ขั้น 3 — รายงานผู้ใช้ถ้าดาวน์โหลดล้มเหลว:
    หยุดทันทีและแจ้ง:
      [A] กรุณาระบุตำแหน่งของ [เครื่องมือ] ให้ฉัน
      [B] ฉันจะลองวิธีทางเลือก: [อธิบายวิธีทางเลือก]
      [C] ข้ามขั้นตอนนี้และดำเนินการต่อโดยมีความสามารถจำกัด
    → รอการตัดสินใจจากผู้ใช้ก่อนดำเนินการต่อ""")

        if opt.get("obstacle"):
            if is_en:
                parts.append("""
══════════════════════════════════════════════════════
[Protocol B] Obstacle & Limitation Handling 🚧
══════════════════════════════════════════════════════
When encountering any limitation (unknown format, permission denied, tool failure):

  1. Never stop silently or loop without reporting.
  2. Diagnose the cause:
     Unknown format? Missing tool? No permission? DRM? Incomplete data?
  3. Report with ranked solution options, e.g.:

     [⚠️ Obstacle] Cannot identify Font format in [filename]
     Options:
       [A — Recommended] Use binwalk to scan headers for known signatures.
       [B — Slower] Use QuickBMS with a known BMS Script Library.
       [C — Pivot] Look for another asset bundle without encryption.
     → Wait for user decision before continuing.""")
            else:
                parts.append("""
══════════════════════════════════════════════════════
[โปรโตคอล B] การจัดการข้อจำกัดและอุปสรรค 🚧
══════════════════════════════════════════════════════
เมื่อเจอข้อจำกัดใดๆ (Format ไม่รู้จัก, ไม่มีสิทธิ์, เครื่องมือล้มเหลว):

  1. ห้ามหยุดเงียบหรือวนซ้ำโดยไม่รายงาน
  2. วิเคราะห์สาเหตุ:
     Format ไม่รู้จัก? เครื่องมือขาด? ไม่มีสิทธิ์? DRM? ข้อมูลไม่ครบ?
  3. รายงานพร้อมตัวเลือกแก้ปัญหาแบบจัดอันดับ ตัวอย่าง:

     [⚠️ อุปสรรค] ไม่สามารถระบุ Format Font ใน [ชื่อไฟล์]
     ตัวเลือก:
       [A — แนะนำ] ใช้ binwalk สแกน Header เพื่อตรวจจับ Signature
       [B — ช้ากว่า] ใช้ QuickBMS กับ BMS Script Library ที่รู้จัก
       [C — เปลี่ยนเป้า] มองหา Asset Bundle อื่นที่ไม่มีการเข้ารหัส
     → รอการตัดสินใจจากผู้ใช้ก่อนดำเนินการต่อ""")

        if opt.get("write_log"):
            if is_en:
                parts.append(f"""
══════════════════════════════════════════════════════
[Protocol C] Session Log 📋
══════════════════════════════════════════════════════
Log every major step to:
  {path}/05_Scripts_and_Tools/session_log.md

Log format:
  ## [Date/Time] Step X — [Step Name]
  - Action taken: ...
  - Result: Success / Failed
  - Files involved: ...
  - Notes: ...""")
            else:
                parts.append(f"""
══════════════════════════════════════════════════════
[โปรโตคอล C] บันทึก Log การทำงาน 📋
══════════════════════════════════════════════════════
บันทึก Log ทุกขั้นตอนสำคัญลงใน:
  {path}/05_Scripts_and_Tools/session_log.md

รูปแบบ Log:
  ## [วันที่/เวลา] ขั้นตอนที่ X — [ชื่อขั้นตอน]
  - สิ่งที่ทำ: ...
  - ผลลัพธ์: สำเร็จ / ล้มเหลว
  - ไฟล์ที่เกี่ยวข้อง: ...
  - หมายเหตุ: ...""")

        if opt.get("min_confirm"):
            if is_en:
                parts.append("""
══════════════════════════════════════════════════════
[Protocol D] Confirm Before Destructive Actions ✅
══════════════════════════════════════════════════════
Ask for user confirmation only before:
  • Overwriting files in 01_Original_Backup
  • Directly modifying files in the Game Directory
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

        if opt.get("deep_scan"):
            if is_en:
                parts.append("""
══════════════════════════════════════════════════════
[Protocol E] Deep Scan Mode 🔬
══════════════════════════════════════════════════════
Full scan — skip nothing:
  • Inspect every byte header of files with non-standard extensions.
  • Use entropy analysis to detect potentially encrypted files.
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

        if opt.get("mem_hook"):
            if is_en:
                parts.append("""
══════════════════════════════════════════════════════
[Protocol F] Memory Hook Fallback 🧩
══════════════════════════════════════════════════════
Allowed to use memory hooks as a last resort:
  • BepInEx (Unity) — Patch at runtime without touching game files.
  • UnrealModLoader — Unreal Engine.
  • REFramework — RE Engine (Capcom).
  Use only when direct archive extraction/modification is impossible.""")
            else:
                parts.append("""
══════════════════════════════════════════════════════
[โปรโตคอล F] Memory Hook Fallback 🧩
══════════════════════════════════════════════════════
อนุญาตให้ใช้ Memory Hook เป็นแผนสำรอง:
  • BepInEx (Unity) — Patch Runtime โดยไม่แตะไฟล์เกม
  • UnrealModLoader — Unreal Engine
  • REFramework — RE Engine (Capcom)
  ใช้เฉพาะเมื่อการแตก/แก้ Archive โดยตรงทำไม่ได้""")

        if is_en:
            parts.append("""
══════════════════════════════════════════════════════
Begin Work
══════════════════════════════════════════════════════
If you understand the mission, environment, safety rules, and all protocols,
confirm your understanding and immediately begin "Step 1 — Engine Survey & Target Identification".
Tell me which folder you will scan first and what additional information you need from the user.""")
        else:
            parts.append("""
══════════════════════════════════════════════════════
เริ่มต้นการทำงาน
══════════════════════════════════════════════════════
หากเข้าใจภารกิจ สภาพแวดล้อม กฎความปลอดภัย และโปรโตคอลทั้งหมดแล้ว
ให้ยืนยันความเข้าใจและเริ่ม "ขั้นตอนที่ 1 — สำรวจ Engine & ระบุเป้าหมาย" ทันที
บอกว่าคุณจะสแกนโฟลเดอร์ใดก่อน และต้องการข้อมูลใดเพิ่มเติมจากผู้ใช้""")

        return "\n".join(parts)


class AdjustCropDialog(ctk.CTkToplevel):
    def __init__(self, parent, proj):
        super().__init__(parent)
        self.parent_app = parent
        self.proj = proj
        self.title(_("จัดตำแหน่งภาพ (Crop)"))
        self.geometry("500x550")
        self.transient(parent)
        self.grab_set()
        
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 500) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 550) // 2
        self.geometry(f"+{x}+{y}")
        
        ctk.CTkLabel(self, text=_("คลิกลากกรอบสีแดงขึ้น-ลง เพื่อเลือกส่วนที่ต้องการ"), font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        import os
        from PIL import Image, ImageTk
        import tkinter as tk
        cover_path = os.path.join(proj.get("path", ""), "thub_cover.jpg")
        
        try:
            img = Image.open(cover_path)
            ratio = 426 / float(img.width)
            self.new_height = int(float(img.height) * ratio)
            img = img.resize((426, self.new_height), Image.Resampling.LANCZOS)
            self.tk_img = ImageTk.PhotoImage(img)
            
            self.canvas_frame = ctk.CTkFrame(self, width=426, height=self.new_height, fg_color="black")
            self.canvas_frame.pack(pady=10)
            
            self.cvs = tk.Canvas(self.canvas_frame, width=426, height=self.new_height, bg="black", highlightthickness=0)
            self.cvs.pack(fill="both", expand=True)
            
            self.cvs.create_image(0, 0, anchor="nw", image=self.tk_img)
            
            # Load initial offset
            self.offset_y = proj.get("cover_offset_y", 0)
            self.offset_y = max(0, min(self.offset_y, self.new_height - 180))
            
            # Create semi-transparent overlays (using stipple is ugly, so we just use 2 dark rectangles)
            # Actually, just a thick red border is usually enough and very clear
            self.cvs.create_rectangle(0, 0, 426, self.offset_y, fill="black", stipple="gray50", outline="", tags="dim_top")
            self.cvs.create_rectangle(0, self.offset_y + 180, 426, self.new_height, fill="black", stipple="gray50", outline="", tags="dim_bottom")
            self.cvs.create_rectangle(2, self.offset_y, 424, self.offset_y + 180, outline="#f38ba8", width=4, tags="crop_box")
            
            def update_overlays():
                self.cvs.coords("dim_top", 0, 0, 426, self.offset_y)
                self.cvs.coords("dim_bottom", 0, self.offset_y + 180, 426, self.new_height)
                self.cvs.coords("crop_box", 2, self.offset_y, 424, self.offset_y + 180)
            
            def on_press(event):
                self.start_mouse_y = event.y
                self.start_offset_y = self.offset_y
                
            def on_drag(event):
                dy = event.y - self.start_mouse_y
                new_y = self.start_offset_y + dy
                # Clamp the crop box so it stays inside the image
                max_y = max(0, self.new_height - 180)
                if new_y < 0: new_y = 0
                if new_y > max_y: new_y = max_y
                
                self.offset_y = new_y
                update_overlays()
                
            self.cvs.bind("<ButtonPress-1>", on_press)
            self.cvs.bind("<B1-Motion>", on_drag)
            self.cvs.configure(cursor="sb_v_double_arrow")
            
        except Exception as e:
            ctk.CTkLabel(self, text=f"โหลดรูปไม่ได้: {e}").pack(pady=50)
            
        def on_save():
            try:
                self.proj["cover_offset_y"] = int(self.offset_y)
                self.parent_app.save_local_config()
            except:
                pass
            self.destroy()
            self.parent_app.show_home()
            
        ctk.CTkButton(self, text=_("บันทึกตำแหน่ง 💾"), fg_color="#a6e3a1", text_color="#11111b", hover_color="#94e2d5", command=on_save).pack(pady=10)
        ctk.CTkButton(self, text=_("ยกเลิก"), fg_color="transparent", border_width=1, command=self.destroy).pack()

class ChangeCoverDialog(ctk.CTkToplevel):
    def __init__(self, parent, index, proj):
        super().__init__(parent)
        self.parent_app = parent
        self.index = index
        self.proj = proj
        self.title(_("🖼️ เปลี่ยนภาพปก (Change Cover)"))
        self.geometry("900x650")
        self.transient(parent)
        self.grab_set()
        
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 900) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 650) // 2
        self.geometry(f"+{x}+{y}")
        
        self.tabview = ctk.CTkTabview(self, width=880, height=550)
        self.tabview.pack(padx=10, pady=(10, 5), fill="both", expand=True)
        
        self.tab_auto = self.tabview.add(_("🔍 ค้นหาจากเว็บ (Gallery)"))
        self.tab_url = self.tabview.add(_("🔗 ลิงก์รูปภาพ (URL)"))
        self.tab_local = self.tabview.add(_("💻 ไฟล์ในเครื่อง"))
        
        self.setup_auto_tab()
        self.setup_url_tab()
        self.setup_local_tab()
        
        bottom_bar = ctk.CTkFrame(self, fg_color="transparent")
        bottom_bar.pack(fill="x", padx=10, pady=5)
        
        import os
        cover_dest = os.path.join(self.proj.get("path", ""), "thub_cover.jpg")
        
        btn_delete = ctk.CTkButton(bottom_bar, text=_("🗑️ ลบภาพปก"), width=100, fg_color="transparent", text_color="#f38ba8", hover_color="#313244", border_width=1, border_color="#f38ba8", command=self.do_remove_cover)
        btn_delete.pack(side="left", padx=(10, 5))
        if not os.path.exists(cover_dest): btn_delete.configure(state="disabled")
        
        btn_adjust = ctk.CTkButton(bottom_bar, text=_("📐 ปรับสัดส่วน (Crop)"), width=120, fg_color="transparent", text_color="#f9e2af", hover_color="#313244", border_width=1, border_color="#f9e2af", command=self.do_adjust)
        btn_adjust.pack(side="left", padx=5)
        if not os.path.exists(cover_dest): btn_adjust.configure(state="disabled")
        
        btn_cancel = ctk.CTkButton(bottom_bar, text=_("ยกเลิก"), width=80, fg_color="transparent", hover_color="#313244", command=self.destroy)
        btn_cancel.pack(side="right", padx=(5, 10))

    def do_remove_cover(self):
        import os
        from tkinter import messagebox
        cover_dest = os.path.join(self.proj.get("path", ""), "thub_cover.jpg")
        if os.path.exists(cover_dest):
            if messagebox.askyesno(_("ยืนยัน"), _("คุณต้องการลบภาพปกโปรเจกต์นี้ใช่หรือไม่?")):
                try:
                    os.remove(cover_dest)
                    self.parent_app.show_home()
                    self.destroy()
                except Exception as e:
                    messagebox.showerror(_("Error"), f"ลบภาพล้มเหลว: {e}")

    def do_adjust(self):
        self.destroy()
        AdjustCropDialog(self.parent_app, self.proj)

    def setup_auto_tab(self):
        top = ctk.CTkFrame(self.tab_auto, fg_color="transparent")
        top.pack(fill="x", pady=(5, 10))
        
        self.ent_search = ctk.CTkEntry(top, placeholder_text=_("พิมพ์ชื่อเกม..."), width=300)
        self.ent_search.pack(side="left", padx=(5, 10))
        self.ent_search.insert(0, self.proj.get("name", ""))
        self.ent_search.bind("<Return>", lambda e: self.do_auto_search())
        
        self.btn_search = ctk.CTkButton(top, text=_("ค้นหา (Search)"), width=120, command=self.do_auto_search)
        self.btn_search.pack(side="left")
        
        self.lbl_status = ctk.CTkLabel(top, text=_("พร้อมค้นหา..."), text_color="gray")
        self.lbl_status.pack(side="left", padx=15)
        
        main_split = ctk.CTkFrame(self.tab_auto, fg_color="transparent")
        main_split.pack(fill="both", expand=True)
        
        self.gallery_frame = ctk.CTkScrollableFrame(main_split, width=250)
        self.gallery_frame.pack(side="left", fill="y", padx=(5, 10))
        
        preview_frame = ctk.CTkFrame(main_split, fg_color="#1e1e2e")
        preview_frame.pack(side="right", fill="both", expand=True)
        
        self.img_preview_lbl = ctk.CTkLabel(preview_frame, text=_("คลิกเลือกรูปภาพจากรายการด้านซ้าย"))
        self.img_preview_lbl.pack(pady=20, expand=True)
        
        self.btn_apply_auto = ctk.CTkButton(preview_frame, text=_("✅ นำไปใช้ (Apply)"), height=40, font=ctk.CTkFont(weight="bold"), fg_color="#a6e3a1", text_color="#1e1e2e", hover_color="#94e2d5", state="disabled", command=self.apply_auto_image)
        self.btn_apply_auto.pack(pady=20)
        
        self.current_preview_image = None
        self.image_widgets = []
        
    def do_auto_search(self):
        query = self.ent_search.get().strip()
        if not query: return
        
        self.lbl_status.configure(text=_("กำลังค้นหาภาพจาก Web (10-12 รูป)..."))
        self.btn_search.configure(state="disabled")
        
        for w in self.image_widgets:
            w.destroy()
        self.image_widgets.clear()
        
        import threading
        threading.Thread(target=self._search_thread, args=(query,), daemon=True).start()
        
    def _search_thread(self, query):
        urls = []
        
        # 1. DDG Search (Best for older/all games)
        try:
            from ddgs import DDGS
            results = DDGS().images(f"{query} game cover", max_results=10)
            if results:
                for r in results:
                    if r.get("image") and r.get("image") not in urls:
                        urls.append(r.get("image"))
        except Exception as e:
            print("DDG Search Error:", e)
            
        # 2. Steam Search (Good for modern PC games)
        try:
            import urllib.request, urllib.parse, json
            steam_url = f"https://store.steampowered.com/api/storesearch/?term={urllib.parse.quote(query)}&l=english&cc=US"
            req = urllib.request.Request(steam_url, headers={'User-Agent': 'Mozilla/5.0'})
            raw = urllib.request.urlopen(req, timeout=5).read()
            data = json.loads(raw)
            for item in data.get('items', []):
                urls.append(f"https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/{item['id']}/header.jpg")
        except Exception as e:
            print("Steam Search Error:", e)

        # 3. iTunes Search (Good for mobile games/apps)
        try:
            import urllib.request, urllib.parse, json
            itunes_url = f"https://itunes.apple.com/search?term={urllib.parse.quote(query)}&entity=software&limit=5"
            req = urllib.request.Request(itunes_url, headers={'User-Agent': 'Mozilla/5.0'})
            raw = urllib.request.urlopen(req, timeout=5).read()
            data = json.loads(raw)
            for item in data.get('results', []):
                if item.get("artworkUrl512"):
                    urls.append(item["artworkUrl512"])
        except Exception as e:
            print("iTunes Search Error:", e)
            
        # Unique list preserving order
        unique_urls = []
        for u in urls:
            if u not in unique_urls:
                unique_urls.append(u)
        urls = unique_urls[:12]
            
        if urls:
            self.parent_app.after(0, self.lbl_status.configure, {"text": f"เจอลิงก์ {len(urls)} รูป กำลังดาวน์โหลด..."})
            self.expected_images = len(urls)
            self.loaded_images = 0
            self.successful_images = 0
            import threading
            for i, u in enumerate(urls):
                threading.Thread(target=self._load_gallery_thumbnail, args=(u, i), daemon=True).start()
        else:
            self.parent_app.after(0, self.lbl_status.configure, {"text": _("❌ ไม่พบรูปภาพ กรุณาลองเปลี่ยนคำค้นหา")})
            self.parent_app.after(0, self.btn_search.configure, {"state": "normal"})

    def _load_gallery_thumbnail(self, url, index):
        import urllib.request
        from io import BytesIO
        from PIL import Image
        import customtkinter as ctk
        
        success = False
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'})
            raw_data = urllib.request.urlopen(req, timeout=10).read()
            img = Image.open(BytesIO(raw_data))
            if img.mode != "RGB": img = img.convert("RGB")
            
            # thumbnail for gallery list
            img.thumbnail((220, 150))
            ctk_img = ctk.CTkImage(light_image=img, size=(img.width, img.height))
            
            # Append safely
            self.parent_app.after(0, self._add_thumbnail_to_ui, ctk_img, url, index)
            success = True
        except Exception as e:
            print("Image Load Error:", e)
            pass
            
        self.parent_app.after(0, self._check_gallery_complete, success)
        
    def _check_gallery_complete(self, success):
        self.loaded_images += 1
        if success:
            self.successful_images += 1
            
        if self.loaded_images >= self.expected_images:
            self.btn_search.configure(state="normal")
            if self.successful_images > 0:
                self.lbl_status.configure(text=_("เลือกภาพที่ต้องการได้เลย!"))
            else:
                self.lbl_status.configure(text=_("❌ พบลิงก์แต่ภาพโดนบล็อคทั้งหมด กรุณาลองใหม่"))

    def _add_thumbnail_to_ui(self, ctk_img, full_url, index):
        btn = ctk.CTkButton(self.gallery_frame, text="", image=ctk_img, fg_color="transparent", hover_color="#313244", command=lambda u=full_url: self.on_gallery_image_click(u))
        btn.pack(pady=5)
        self.image_widgets.append(btn)

        
    def on_gallery_image_click(self, url):
        self.lbl_status.configure(text=_("กำลังโหลดพรีวิว..."))
        self.btn_apply_auto.configure(state="disabled")
        import threading
        threading.Thread(target=self._download_and_preview, args=(url, True), daemon=True).start()

    def _download_and_preview(self, url, is_auto=True):
        import urllib.request
        from io import BytesIO
        from PIL import Image
        import customtkinter as ctk
        
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            raw_data = urllib.request.urlopen(req, timeout=15).read()
            img = Image.open(BytesIO(raw_data))
            if img.mode != "RGB": img = img.convert("RGB")
                
            if is_auto:
                self.current_preview_image = img.copy()
                img.thumbnail((500, 350))
            else:
                self.current_url_image = img.copy()
                img.thumbnail((400, 250))
                
            ctk_img = ctk.CTkImage(light_image=img, size=(img.width, img.height))
            
            def update_ui_success():
                if is_auto:
                    self.img_preview_lbl.configure(image=ctk_img, text="")
                    self.lbl_status.configure(text=_("✅ พรีวิวพร้อมใช้งาน!"))
                    self.btn_apply_auto.configure(state="normal")
                else:
                    self.url_preview_lbl.configure(image=ctk_img, text="")
                    self.lbl_url_status.configure(text=_("✅ โหลดภาพสำเร็จ"))
                    self.btn_apply_url.configure(state="normal")
                    self.btn_url.configure(state="normal")
            
            self.after(0, update_ui_success)
        except Exception as e:
            def update_ui_error(err=e):
                if is_auto:
                    self.lbl_status.configure(text=f"❌ โหลดพรีวิวล้มเหลว: {err}")
                else:
                    self.lbl_url_status.configure(text=f"❌ โหลดล้มเหลว: {err}")
                    self.btn_url.configure(state="normal")
            self.after(0, update_ui_error)
        
    def apply_auto_image(self):
        if self.current_preview_image:
            import os
            cover_dest = os.path.join(self.proj.get("path", ""), "thub_cover.jpg")
            self.current_preview_image.save(cover_dest, "JPEG")
            self.parent_app.show_home()
            self.destroy()

    def setup_url_tab(self):
        top = ctk.CTkFrame(self.tab_url, fg_color="transparent")
        top.pack(fill="x", pady=20)
        
        self.ent_url = ctk.CTkEntry(top, placeholder_text=_("วางลิงก์รูปภาพ (เช่น https://...)"), width=380)
        self.ent_url.pack(side="left", padx=10)
        
        self.btn_url = ctk.CTkButton(top, text=_("โหลดภาพ"), width=100, command=self.do_url_load)
        self.btn_url.pack(side="left")
        
        self.lbl_url_status = ctk.CTkLabel(self.tab_url, text="", text_color="gray")
        self.lbl_url_status.pack(pady=5)
        
        self.url_preview_lbl = ctk.CTkLabel(self.tab_url, text="")
        self.url_preview_lbl.pack(pady=10, expand=True)
        
        self.btn_apply_url = ctk.CTkButton(self.tab_url, text=_("✅ นำไปใช้ (Apply)"), fg_color="#a6e3a1", text_color="#1e1e2e", hover_color="#94e2d5", state="disabled", command=self.apply_url_image)
        self.btn_apply_url.pack(pady=10)
        
        self.current_url_image = None
        
    def do_url_load(self):
        url = self.ent_url.get().strip()
        if not url: return
        self.lbl_url_status.configure(text=_("ดาวน์โหลด..."))
        self.btn_url.configure(state="disabled")
        self.btn_apply_url.configure(state="disabled")
        import threading
        threading.Thread(target=self._download_and_preview, args=(url, False), daemon=True).start()
            
    def apply_url_image(self):
        if self.current_url_image:
            import os
            cover_dest = os.path.join(self.proj.get("path", ""), "thub_cover.jpg")
            self.current_url_image.save(cover_dest, "JPEG")
            self.parent_app.show_home()
            self.destroy()

    def setup_local_tab(self):
        ctk.CTkLabel(self.tab_local, text=_("เลือกรูปภาพจากในเครื่องคอมพิวเตอร์ของคุณ"), font=ctk.CTkFont(size=14)).pack(pady=20)
        
        def on_local():
            from tkinter import filedialog
            import shutil
            import os
            file_path = filedialog.askopenfilename(title=_("เลือกภาพปก"), filetypes=[("Image Files", "*.jpg *.jpeg *.png *.webp")])
            if file_path:
                try:
                    cover_dest = os.path.join(self.proj.get("path", ""), "thub_cover.jpg")
                    from PIL import Image
                    img = Image.open(file_path)
                    if img.mode != "RGB":
                        img = img.convert("RGB")
                    img.save(cover_dest, "JPEG")
                    self.parent_app.show_home()
                    self.destroy()
                except Exception as e:
                    self.lbl_local_status.configure(text=f"❌ Error: {e}")
                    
        ctk.CTkButton(self.tab_local, text=_("📂 Browse..."), width=150, height=40, font=ctk.CTkFont(weight="bold"), fg_color="#a6e3a1", text_color="#11111b", hover_color="#94e2d5", command=on_local).pack(pady=20)
        self.lbl_local_status = ctk.CTkLabel(self.tab_local, text="", text_color="red")
        self.lbl_local_status.pack(pady=5)

class ModderHubApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('flagship.thub.launcher.1.0')
        except:
            pass
            
        self.title("THub Launcher - The Flagship Suite")
        self.geometry("1700x900")
        
        hub_logo_path = os.path.join(os.path.dirname(__file__), "assets", "THub.png")
        if os.path.exists(hub_logo_path):
            from PIL import Image, ImageTk
            img = Image.open(hub_logo_path)
            self.iconphoto(False, ImageTk.PhotoImage(img))
            try:
                ico_path = os.path.join(os.path.dirname(__file__), "assets", "THub.ico")
                if not os.path.exists(ico_path):
                    img.save(ico_path, format='ICO', sizes=[(64,64)])
                self.iconbitmap(ico_path)
            except:
                pass
        
        # Load local configuration (for Tool Library paths)
        self.config = self.load_local_config()
        os.environ["THUB_LANG"] = self.config.get("app_lang", "th")
        
        # Migrate legacy global profiles to Project-bound profiles
        self.migrate_project_profiles()

        # Grid Layout: 1 row, 2 cols
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ====== LEFT SIDEBAR ======
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1)

        hub_logo_path = os.path.join(os.path.dirname(__file__), "assets", "THub.png")
        if os.path.exists(hub_logo_path):
            self.hub_img = ctk.CTkImage(light_image=Image.open(hub_logo_path), size=(40, 40))
            self.logo_label = ctk.CTkLabel(self.sidebar_frame, text=_(" THub Launcher"), image=self.hub_img, compound="left", font=ctk.CTkFont(size=20, weight="bold"))
        else:
            self.logo_label = ctk.CTkLabel(self.sidebar_frame, text=_("THub Launcher"), font=ctk.CTkFont(size=22, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 30))

        # Navigation Buttons
        self.btn_home = ctk.CTkButton(self.sidebar_frame, text=_("📊 Dashboard"), command=self.show_home, anchor="w", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"))
        self.btn_home.grid(row=1, column=0, padx=20, pady=5, sticky="ew")

        self.btn_flagship = ctk.CTkButton(self.sidebar_frame, text=_("✨ THub Apps"), command=self.show_flagship, anchor="w", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"))
        self.btn_flagship.grid(row=2, column=0, padx=20, pady=5, sticky="ew")

        self.btn_tool = ctk.CTkButton(self.sidebar_frame, text=_("🧰 Tool Library"), command=self.show_tool_library, anchor="w", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"))
        self.btn_tool.grid(row=3, column=0, padx=20, pady=5, sticky="ew")

        self.btn_knowledge = ctk.CTkButton(self.sidebar_frame, text=_("📚 Documentation"), command=self.show_knowledge, anchor="w", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"))
        self.btn_knowledge.grid(row=4, column=0, padx=20, pady=5, sticky="ew")

        self.btn_about = ctk.CTkButton(self.sidebar_frame, text=_("ℹ️ About THub"), command=self.show_about, anchor="w", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"))
        self.btn_about.grid(row=5, column=0, padx=20, pady=5, sticky="ew")

        # UI Language Mode
        self.app_lang_label = ctk.CTkLabel(self.sidebar_frame, text=_("🌐 Language:"), anchor="w")
        self.app_lang_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        
        self.app_lang_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["th (Thai)", "en (English)", "ja (Japanese)", "zh (Chinese)", "ru (Russian)"], command=self.change_app_lang)
        current_lang = self.config.get("app_lang", "th")
        for v in self.app_lang_optionemenu.cget("values"):
            if current_lang in v:
                self.app_lang_optionemenu.set(v)
                break
        self.app_lang_optionemenu.grid(row=8, column=0, padx=20, pady=(5, 10))

        # Appearance Mode
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text=_("Appearance Mode:"), anchor="w")
        self.appearance_mode_label.grid(row=9, column=0, padx=20, pady=(10, 0))
        
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=[_("Light"), _("Dark"), _("System")], command=self.change_appearance_mode)
        self.appearance_mode_optionemenu.set(_("Dark"))
        self.appearance_mode_optionemenu.grid(row=10, column=0, padx=20, pady=(10, 10))
        
        self.auto_update_switch = ctk.CTkSwitch(self.sidebar_frame, text=_("Auto Update"), command=self.toggle_auto_update)
        self.auto_update_switch.grid(row=11, column=0, padx=20, pady=(10, 10))
        if self.config.get("auto_update", True):
            self.auto_update_switch.select()
        else:
            self.auto_update_switch.deselect()
        
        self.update_status_lbl = ctk.CTkLabel(self.sidebar_frame, text=_("กำลังตรวจสอบอัปเดต..."), text_color="gray", font=ctk.CTkFont(size=12))
        self.update_status_lbl.grid(row=12, column=0, padx=20, pady=(0, 20))

        # ====== MAIN FRAME ======
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        # Start at Home
        self.show_home()
        
        # --- Smart Scroll System ---
        self.bind_all("<MouseWheel>", self._global_mousewheel_handler)
        
    def _global_mousewheel_handler(self, event):
        try:
            widget = event.widget
            # Traverse up the widget tree to find a scrollable frame
            while widget:
                # Check if this widget is one of our scrollable frames
                if hasattr(self, "projects_frame") and getattr(self.projects_frame, "_parent_canvas", None) and str(widget).startswith(str(self.projects_frame)):
                    self.projects_frame._parent_canvas.yview_scroll(int(-1*(event.delta/6)), "units")
                    return
                if hasattr(self, "tool_frame") and getattr(self.tool_frame, "_parent_canvas", None) and str(widget).startswith(str(self.tool_frame)):
                    self.tool_frame._parent_canvas.yview_scroll(int(-1*(event.delta/6)), "units")
                    return
                if hasattr(self, "tree_frame") and getattr(self.tree_frame, "_parent_canvas", None) and str(widget).startswith(str(self.tree_frame)):
                    self.tree_frame._parent_canvas.yview_scroll(int(-1*(event.delta/6)), "units")
                    return
                # If we have any other scrollable frames, we can add them here
                widget = getattr(widget, "master", None)
        except Exception:
            pass
        




    def toggle_auto_update(self):
        self.config["auto_update"] = bool(self.auto_update_switch.get())
        self.save_local_config()

    def show_ai_dialog(self, proj):
        dialog = AIHelperDialog(self, proj)
        self.wait_window(dialog)
        
    def change_app_lang(self, new_lang: str):
        lang_code = new_lang.split(" ")[0]
        if self.config.get("app_lang") == lang_code:
            return

        self.config["app_lang"] = lang_code
        self.save_local_config()

        from tkinter import messagebox
        msg = _("ระบบภาษาถูกเปลี่ยนเป็น '{lang_code}' แล้ว\nระบบกำลังรีสตาร์ทโปรแกรมเพื่อนำไปใช้งาน...", lang_code=lang_code)
        messagebox.showinfo(_("Language Changed"), msg, parent=self)

        # ── Reliable Windows restart ──────────────────────────────────────
        import sys, subprocess
        script = os.path.abspath(sys.argv[0])          # full path to main.py
        args   = [sys.executable, script] + sys.argv[1:]
        # DETACHED_PROCESS (0x08) + CREATE_NEW_PROCESS_GROUP (0x200)
        # ensures the child outlives the parent on Windows
        flags  = 0x00000008 | 0x00000200
        try:
            subprocess.Popen(args, cwd=os.path.dirname(script), creationflags=flags)
        except Exception:
            subprocess.Popen(args, cwd=os.path.dirname(script))   # fallback
        self.destroy()
        os._exit(0)   # hard exit — guarantees the process ends immediately

    def change_appearance_mode(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def load_local_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                if "tools" not in config: config["tools"] = {}
                if "projects" not in config: config["projects"] = []
                if "auto_update" not in config: config["auto_update"] = True
                return config
        return {"tools": {}, "projects": [], "auto_update": True}

    def migrate_project_profiles(self):
        import shutil
        projects = self.config.get("projects", [])
        core_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools", "flagship", "Core")
        global_prompts = os.path.join(core_dir, "prompts.json")
        
        for proj in projects:
            proj_path = proj.get("path", "")
            if not proj_path or not os.path.exists(proj_path):
                continue
            
            # Check if project already has local profile
            local_profile_dir = os.path.join(proj_path, ".thub", "profile")
            if os.path.exists(local_profile_dir):
                # If local profile exists, just ensure prompts.json exists
                local_prompts = os.path.join(local_profile_dir, "prompts.json")
                if not os.path.exists(local_prompts) and os.path.exists(global_prompts):
                    try:
                        shutil.copy2(global_prompts, local_prompts)
                    except Exception as e:
                        print(f"Error copying prompts.json for {proj_path}: {e}")
                continue
                
            # Check for legacy profile
            thub_meta_path = os.path.join(proj_path, "thub_project.json")
            if os.path.exists(thub_meta_path):
                try:
                    with open(thub_meta_path, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                    
                    profile_name = meta.get("profile_name", "").strip()
                    os.makedirs(local_profile_dir, exist_ok=True)
                    
                    # 1. Always copy global prompts.json as the baseline
                    local_prompts = os.path.join(local_profile_dir, "prompts.json")
                    if os.path.exists(global_prompts):
                        shutil.copy2(global_prompts, local_prompts)
                    
                    # 2. Copy legacy profile folder (Translation Memory / Lore) if exists
                    if profile_name:
                        legacy_profile_path = os.path.join(core_dir, "profiles", profile_name)
                        if os.path.exists(legacy_profile_path):
                            for item in os.listdir(legacy_profile_path):
                                s = os.path.join(legacy_profile_path, item)
                                d = os.path.join(local_profile_dir, item)
                                if os.path.isdir(s):
                                    shutil.copytree(s, d, dirs_exist_ok=True)
                                else:
                                    shutil.copy2(s, d)
                except Exception as e:
                    print(f"Error migrating profile for {proj_path}: {e}")

    def save_local_config(self):
        try:
            tmp_file = CONFIG_FILE + ".tmp"
            with open(tmp_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            os.replace(tmp_file, CONFIG_FILE)
        except (PermissionError, OSError) as e:
            from tkinter import messagebox
            messagebox.showerror(_("Error"), _("ไม่สามารถบันทึกการตั้งค่าได้: ") + str(e))

    # --- 1. Home / Dashboard ---


    def show_change_cover_dialog(self, index, proj):
        dialog = ChangeCoverDialog(self, index, proj)

    def show_home(self):
        self.clear_main_frame()
        
        # Header Area
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 10))
        
        # Pack right-side buttons first to prevent them from being pushed out
        btn_new_proj = ctk.CTkButton(header_frame, text="+ New Project", font=ctk.CTkFont(weight="bold"), fg_color="#a6e3a1", hover_color="#89dceb", text_color="#1e1e2e", command=self.add_new_project_wizard)
        btn_new_proj.pack(side="right")
        
        btn_import_proj = ctk.CTkButton(header_frame, text="📥 Import Project", font=ctk.CTkFont(weight="bold"), fg_color="transparent", border_width=1, border_color="#89b4fa", text_color="#89b4fa", hover_color="#313244", command=self.import_project_wizard)
        btn_import_proj.pack(side="right", padx=(0, 10))
        
        lbl_title = ctk.CTkLabel(header_frame, text="Project Dashboard", font=ctk.CTkFont(size=28, weight="bold"), anchor="w")
        lbl_title.pack(side="left")
        
        btn_help = ctk.CTkButton(header_frame, text="❓", width=30, fg_color="transparent", text_color="#f9e2af", hover_color="#313244", font=ctk.CTkFont(size=20), command=self.show_dashboard_help)
        btn_help.pack(side="left", padx=(5, 0))
        ToolTip(btn_help, _("คู่มือใช้งาน"))
        
        # Preserve search/sort state across refreshes
        if not hasattr(self, 'search_var'):
            self.search_var = ctk.StringVar()
        if not hasattr(self, 'sort_var'):
            self.sort_var = ctk.StringVar(value=_("เรียงตาม: ล่าสุด"))
        self.search_var.trace_add("write", lambda *args: self._rearrange_project_cards())
        search_entry = ctk.CTkEntry(header_frame, textvariable=self.search_var, placeholder_text=_("🔍 ค้นหาโปรเจกต์..."), width=200)
        search_entry.pack(side="left", padx=(20, 0))
        
        sort_menu = ctk.CTkOptionMenu(header_frame, variable=self.sort_var, values=[_("เรียงตาม: ล่าสุด"), _("เรียงตาม: A-Z"), _("เรียงตาม: Z-A")], command=self.on_sort_changed, fg_color="#313244", button_color="#45475a", button_hover_color="#585b70")
        sort_menu.pack(side="left", padx=(10, 0))
        
        # View Mode Toggle
        if not hasattr(self, 'view_mode_var'):
            self.view_mode_var = ctk.StringVar(value=self.config.get("card_view_mode", "Large"))
        
        def on_view_mode_changed(mode):
            self.config["card_view_mode"] = mode
            self.save_local_config()
            self.show_home()
            
        view_toggle = ctk.CTkSegmentedButton(header_frame, values=["Large", "Medium", "List"], variable=self.view_mode_var, command=on_view_mode_changed, selected_color="#a6e3a1", selected_hover_color="#94e2d5")
        view_toggle.pack(side="left", padx=(20, 0))
        
        lbl_desc = ctk.CTkLabel(self.main_frame, text=_("ยินดีต้อนรับสู่ THub Launcher ศูนย์รวมเครื่องมือแปลเกมที่ดีที่สุด"), font=ctk.CTkFont(size=14), text_color="gray")
        lbl_desc.pack(anchor="w", padx=30, pady=(0, 10))
        
        all_projects = self.config.get("projects", [])
        active_count = sum(1 for p in all_projects if not p.get("is_archived", False))
        archived_count = sum(1 for p in all_projects if p.get("is_archived", False))
        pinned_count = sum(1 for p in all_projects if p.get("is_pinned", False))
        
        stat_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        stat_frame.pack(fill="x", padx=30, pady=(0, 20))
        
        def create_stat_card(parent, title, count, icon, color):
            c = ctk.CTkFrame(parent, fg_color="#1e1e2e", border_width=1, border_color="#313244", corner_radius=10)
            c.pack(side="left", expand=True, fill="x", padx=(0, 15) if title != "Pinned Projects" else 0)
            ctk.CTkLabel(c, text=icon, font=ctk.CTkFont(size=30), text_color=color).pack(side="left", padx=15, pady=15)
            text_frame = ctk.CTkFrame(c, fg_color="transparent")
            text_frame.pack(side="left", fill="both", expand=True, pady=10)
            ctk.CTkLabel(text_frame, text=str(count), font=ctk.CTkFont(size=24, weight="bold"), text_color="#cba6f7", anchor="w").pack(fill="x")
            ctk.CTkLabel(text_frame, text=title, font=ctk.CTkFont(size=12), text_color="gray", anchor="w").pack(fill="x")
            
        create_stat_card(stat_frame, "Active Projects", active_count, "📂", "#89b4fa")
        create_stat_card(stat_frame, "Archived Projects", archived_count, "📦", "#f38ba8")
        create_stat_card(stat_frame, "Pinned Projects", pinned_count, "📌", "#f9e2af")
        
        if not hasattr(self, "current_archive_tab"):
            self.current_archive_tab = "Active"
            
        def on_tab_change(value):
            self.current_archive_tab = value
            self._rearrange_project_cards()
            
        tab_btn = ctk.CTkSegmentedButton(self.main_frame, values=["Active", "Archived"], command=on_tab_change)
        tab_btn.set(self.current_archive_tab)
        tab_btn.pack(anchor="w", padx=30, pady=(0, 10))

        # Active Projects Grid
        self.projects_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent", scrollbar_button_color="#585b70", scrollbar_button_hover_color="#7f849c")
        self.projects_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        


        
        projects = self.config.get("projects", [])
        # Sort so pinned projects are first
        projects.sort(key=lambda p: not p.get("is_pinned", False))
        
        self.project_card_widgets = []
        self._current_proj_cols = -1
        
        if not projects:
            empty_frame = ctk.CTkFrame(self.projects_frame, fg_color="transparent")
            empty_frame.grid(row=0, column=0, sticky="nsew", pady=50, padx=20)
            self.projects_frame.grid_columnconfigure(0, weight=1)
            
            box = ctk.CTkFrame(empty_frame, fg_color="#181825", border_width=2, border_color="#313244", corner_radius=15)
            box.pack(expand=True, padx=20, pady=20)
            
            ctk.CTkLabel(box, text="📁", font=ctk.CTkFont(size=60), text_color="#89b4fa").pack(pady=(30, 10))
            ctk.CTkLabel(box, text=_("ยังไม่มีโปรเจกต์"), font=ctk.CTkFont(size=24, weight="bold"), text_color="#cba6f7").pack(pady=(0, 10))
            ctk.CTkLabel(box, text=_("เริ่มสร้างโปรเจกต์ใหม่เพื่อเริ่มต้นการแปลเกมของคุณ!"), font=ctk.CTkFont(size=14), text_color="gray").pack(pady=(0, 20))
            
            btn_add = ctk.CTkButton(box, text=_("+ สร้างโปรเจกต์แรกของคุณ"), font=ctk.CTkFont(weight="bold", size=16), fg_color="#a6e3a1", hover_color="#89dceb", text_color="#1e1e2e", height=40, command=self.add_new_project_wizard)
            btn_add.pack(pady=(0, 30), padx=50)
        else:
            for i, proj in enumerate(projects):
                proj_path = proj.get("path", "")
                author_name = ""
                meta_path = os.path.join(proj_path, "thub_project.json")
                if os.path.exists(meta_path):
                    try:
                        with open(meta_path, "r", encoding="utf-8") as f:
                            local_meta = json.load(f)
                            author_name = local_meta.get("author", "").strip()
                    except Exception:
                        pass

                view_mode = self.view_mode_var.get()
                
                if view_mode == "List":
                    # List Mode
                    card = ctk.CTkFrame(self.projects_frame, height=60, corner_radius=10, fg_color="#1e1e2e", border_width=1, border_color="#45475a")
                    card.pack_propagate(False)
                    card.bind("<Enter>", lambda e, c=card: self.on_card_enter(e, c))
                    card.bind("<Leave>", lambda e, c=card: self.on_card_leave(e, c))
                    card.bind("<Button-3>", lambda e, idx=i, p=proj: self.show_card_context_menu(e, idx, p))
                    self.project_card_widgets.append((card, proj))
                    
                    content_frame = ctk.CTkFrame(card, fg_color="transparent")
                    content_frame.pack(fill="both", expand=True, padx=15, pady=5)
                    
                    lbl_drag = ctk.CTkLabel(content_frame, text="☰", font=ctk.CTkFont(size=20), text_color="gray", cursor="hand2")
                    lbl_drag.pack(side="left", padx=(0, 10))
                    lbl_drag.bind("<ButtonPress-1>", lambda e, idx=i: self.start_card_drag(e, idx))
                    lbl_drag.bind("<B1-Motion>", lambda e, idx=i: self.on_card_drag(e, idx))
                    
                    is_pinned = proj.get("is_pinned", False)
                    pin_color = "#f9e2af" if is_pinned else "gray"
                    btn_pin = ctk.CTkButton(content_frame, text="📌", width=20, fg_color="transparent", text_color=pin_color, hover_color="#313244", font=ctk.CTkFont(size=14), command=lambda idx=i: self.toggle_pin(idx))
                    btn_pin.pack(side="left", padx=(0, 10))
                    
                    name_lbl = ctk.CTkLabel(content_frame, text=proj.get("name", "Unknown"), font=ctk.CTkFont(size=18, weight="bold"), text_color="#cba6f7", anchor="w")
                    name_lbl.pack(side="left")
                    name_lbl.bind("<Button-3>", lambda e, idx=i, p=proj: self.show_card_context_menu(e, idx, p))
                    content_frame.bind("<Button-3>", lambda e, idx=i, p=proj: self.show_card_context_menu(e, idx, p))
                    
                    btn_open = ctk.CTkButton(content_frame, text="📁", width=35, fg_color="transparent", border_width=1, border_color="#89b4fa", text_color="#89b4fa", hover_color="#313244", command=lambda p=proj.get("path"): self.open_project_folder(p))
                    btn_open.pack(side="right", padx=(5, 0))
                    
                    s2_name = proj.get("shortcut_2_name", "TRun")
                    if "TRun" in s2_name and "▶" not in s2_name: s2_name = f"▶️ {s2_name}"
                    if "TVox" in s2_name and "🎙" not in s2_name: s2_name = f"🎙️ {s2_name}"
                    btn_s2 = ctk.CTkButton(content_frame, text=s2_name, width=100, fg_color="transparent", border_width=1, border_color="#fab387", text_color="#fab387", hover_color="#313244", command=lambda p=proj, s=2: self.launch_card_shortcut(p, s))
                    btn_s2.pack(side="right", padx=5)
                    btn_s2.bind("<Button-3>", lambda e, idx=i, s=2: self.configure_shortcut(idx, s))
                    
                    s1_name = proj.get("shortcut_1_name", "TStudio")
                    if "TStudio" in s1_name and "✏" not in s1_name and "🖊" not in s1_name: s1_name = f"✏️ {s1_name}"
                    if "TVox" in s1_name and "🎙" not in s1_name: s1_name = f"🎙️ {s1_name}"
                    btn_s1 = ctk.CTkButton(content_frame, text=s1_name, width=100, fg_color="transparent", border_width=1, border_color="#a6e3a1", text_color="#a6e3a1", hover_color="#313244", command=lambda p=proj, s=1: self.launch_card_shortcut(p, s))
                    btn_s1.pack(side="right", padx=5)
                    btn_s1.bind("<Button-3>", lambda e, idx=i, s=1: self.configure_shortcut(idx, s))
                    
                    btn_ai = ctk.CTkButton(content_frame, text="🤖 AI Helper", width=100, fg_color="transparent", border_width=1, border_color="#cba6f7", text_color="#cba6f7", hover_color="#313244", command=lambda pj=proj: self.show_ai_dialog(pj))
                    btn_ai.pack(side="right", padx=5)
                    
                    continue

                if view_mode == "Medium":
                    card_w = 320
                    card_h = 210
                    img_h = 120
                    show_btn_text = False
                else:
                    card_w = 426
                    card_h = 280
                    img_h = 180
                    show_btn_text = True
                    
                card = ctk.CTkFrame(self.projects_frame, width=card_w, height=card_h, corner_radius=10, fg_color="#1e1e2e", border_width=1, border_color="#45475a")
                card.pack_propagate(False)
                card.bind("<Enter>", lambda e, c=card: self.on_card_enter(e, c))
                card.bind("<Leave>", lambda e, c=card: self.on_card_leave(e, c))
                card.bind("<Button-3>", lambda e, idx=i, p=proj: self.show_card_context_menu(e, idx, p))
                self.project_card_widgets.append((card, proj))
                
                # Bottom Frame
                bottom_frame = ctk.CTkFrame(card, fg_color="transparent")
                bottom_frame.pack(fill="x", side="bottom", padx=15 if show_btn_text else 10, pady=(5, 12))
        
                bottom_frame.grid_columnconfigure((0, 1, 2), weight=1)
                bottom_frame.grid_columnconfigure(3, weight=0)
                
                ai_text = "🤖 AI Helper" if show_btn_text else "🤖"
                btn_ai = ctk.CTkButton(bottom_frame, text=ai_text, width=0, fg_color="transparent", border_width=1, border_color="#cba6f7", text_color="#cba6f7", hover_color="#313244", command=lambda pj=proj: self.show_ai_dialog(pj))
                btn_ai.grid(row=0, column=0, sticky="ew", padx=(0, 6))

                s1_name = proj.get("shortcut_1_name", "TStudio")
                s2_name = proj.get("shortcut_2_name", "TRun")

                if "TStudio" in s1_name and "✏" not in s1_name and "🖊" not in s1_name: s1_name = f"✏️ {s1_name}"
                if "TRun" in s2_name and "▶" not in s2_name: s2_name = f"▶️ {s2_name}"
                if "TVox" in s1_name and "🎙" not in s1_name: s1_name = f"🎙️ {s1_name}"
                if "TVox" in s2_name and "🎙" not in s2_name: s2_name = f"🎙️ {s2_name}"

                if not show_btn_text:
                    s1_name = s1_name.split()[0]
                    s2_name = s2_name.split()[0]

                btn_s1 = ctk.CTkButton(bottom_frame, text=s1_name, width=0, fg_color="transparent", border_width=1, border_color="#a6e3a1", text_color="#a6e3a1", hover_color="#313244", command=lambda p=proj, s=1: self.launch_card_shortcut(p, s))
                btn_s1.grid(row=0, column=1, sticky="ew", padx=(0, 6))
                btn_s1.bind("<Button-3>", lambda e, idx=i, s=1: self.configure_shortcut(idx, s))

                btn_s2 = ctk.CTkButton(bottom_frame, text=s2_name, width=0, fg_color="transparent", border_width=1, border_color="#fab387", text_color="#fab387", hover_color="#313244", command=lambda p=proj, s=2: self.launch_card_shortcut(p, s))
                btn_s2.grid(row=0, column=2, sticky="ew", padx=(0, 6))
                btn_s2.bind("<Button-3>", lambda e, idx=i, s=2: self.configure_shortcut(idx, s))

                btn_open = ctk.CTkButton(bottom_frame, text="📁", width=35 if show_btn_text else 30, fg_color="transparent", border_width=1, border_color="#89b4fa", text_color="#89b4fa", hover_color="#313244", command=lambda p=proj.get("path"): self.open_project_folder(p))
                btn_open.grid(row=0, column=3, sticky="e")
                
                # Check for cover image
                cover_path = os.path.join(proj.get("path", ""), "thub_cover.jpg")
                if os.path.exists(cover_path):
                    try:
                        from PIL import Image
                        img = Image.open(cover_path)
                        
                        offset_y = proj.get("cover_offset_y", 0)
                        
                        ratio = card_w / float(img.width)
                        new_height = int(float(img.height) * ratio)
                        img = img.resize((card_w, new_height), Image.Resampling.LANCZOS)
                        
                        offset_y = max(0, min(offset_y, new_height - img_h))
                        
                        box = (0, offset_y, card_w, offset_y + img_h)
                        img = img.crop(box)
                        
                        from PIL import ImageDraw, ImageFont
                        draw = ImageDraw.Draw(img)
                        try:
                            fnt = ImageFont.truetype("segoeui.ttf", 12)
                        except Exception:
                            fnt = ImageFont.load_default()
                            
                        raw_p = proj.get("path", "")
                        short_p = raw_p
                        if len(short_p) > 55:
                            short_p = short_p[:15] + "..." + short_p[-35:]
                            
                        # Draw slight shadow (bottom left)
                        draw.text((11, img_h - 19), short_p, font=fnt, fill=(17, 17, 27))
                        # Draw text
                        draw.text((10, img_h - 20), short_p, font=fnt, fill=(205, 214, 244))
                        
                        ctk_img = ctk.CTkImage(light_image=img, size=(card_w, img_h))
                        img_lbl = ctk.CTkLabel(card, image=ctk_img, text="")
                        img_lbl.pack(fill="x", side="top", pady=(0, 5))
                        img_lbl.bind("<Button-3>", lambda e, idx=i, p=proj: self.show_card_context_menu(e, idx, p))
                    except Exception as e:
                        pass
                        
                card_top = ctk.CTkFrame(card, fg_color="transparent")
                card_top.pack(fill="x", side="top", padx=15, pady=(10, 5))
                
                # LEFT SIDE BUTTONS
                lbl_drag = ctk.CTkLabel(card_top, text="☰", font=ctk.CTkFont(size=20), text_color="gray", cursor="hand2")
                lbl_drag.pack(side="left", padx=(0, 5))
                lbl_drag.bind("<ButtonPress-1>", lambda e, idx=i: self.start_card_drag(e, idx))
                lbl_drag.bind("<B1-Motion>", lambda e, idx=i: self.on_card_drag(e, idx))
                
                is_pinned = proj.get("is_pinned", False)
                pin_color = "#f9e2af" if is_pinned else "gray"
                btn_pin = ctk.CTkButton(card_top, text="📌", width=20, fg_color="transparent", text_color=pin_color, hover_color="#313244", font=ctk.CTkFont(size=14), command=lambda idx=i: self.toggle_pin(idx))
                btn_pin.pack(side="left", padx=(0, 5))
                
                name_lbl = ctk.CTkLabel(card_top, text=proj.get("name", "Unknown"), font=ctk.CTkFont(size=18 if show_btn_text else 16, weight="bold"), text_color="#cba6f7", anchor="w")
                name_lbl.pack(side="left")
                name_lbl.bind("<Button-3>", lambda e, idx=i, p=proj: self.show_card_context_menu(e, idx, p))
                card_top.bind("<Button-3>", lambda e, idx=i, p=proj: self.show_card_context_menu(e, idx, p))
                
                # RIGHT SIDE BUTTONS (Removed in favor of Context Menu)
                

                


        self.projects_frame.bind("<Configure>", self.on_projects_resize)
        self._rearrange_project_cards()
        
    def on_card_enter(self, e, card_widget):
        card_widget.configure(border_color="#cba6f7")
        
    def on_card_leave(self, e, card_widget):
        card_widget.configure(border_color="#45475a")
        
    def on_sort_changed(self, choice):
        self._rearrange_project_cards()

    def toggle_archive(self, index):
        projects = self.config.get("projects", [])
        if 0 <= index < len(projects):
            is_arch = projects[index].get("is_archived", False)
            projects[index]["is_archived"] = not is_arch
            self.save_local_config()
            self.show_home()
            
    def show_card_context_menu(self, event, index, proj):
        import tkinter as tk
        menu = tk.Menu(self, tearoff=0, bg="#1e1e2e", fg="#cdd6f4", activebackground="#313244", activeforeground="#cba6f7", font=("Segoe UI", 10))
        
        is_pinned = proj.get("is_pinned", False)
        pin_text = _("📌 เลิกปักหมุด") if is_pinned else _("📌 ปักหมุด")
        menu.add_command(label=pin_text.replace('\ufe0f', ''), command=lambda: self.toggle_pin(index))
        
        is_arch = proj.get("is_archived", False)
        arch_text = _("📤 ดึงกลับจากคลัง") if is_arch else _("🗃️ เก็บเข้าคลัง")
        menu.add_command(label=arch_text.replace('\ufe0f', ''), command=lambda: self.toggle_archive(index))
        
        menu.add_command(label=_("✏️ เปลี่ยนชื่อโปรเจกต์").replace('\ufe0f', ''), command=lambda: self.rename_project(index))
        menu.add_command(label=_("🖼️ เปลี่ยนภาพปก...").replace('\ufe0f', ''), command=lambda: self.show_change_cover_dialog(index, proj))
        
        menu.add_separator()
        menu.add_command(label=_("⚙️ ตั้งค่าโฟลเดอร์เครื่องมือ").replace('\ufe0f', ''), command=lambda: self.set_translation_folder(index))
        menu.add_command(label=_("🗑️ ลบโปรเจกต์").replace('\ufe0f', ''), command=lambda: self.delete_project(index), foreground="#f38ba8", activeforeground="#f38ba8")
        
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def toggle_pin(self, index):
        projects = self.config.get("projects", [])
        if 0 <= index < len(projects):
            is_pinned = projects[index].get("is_pinned", False)
            projects[index]["is_pinned"] = not is_pinned
            self.save_local_config()
            self.show_home()
                    
    def start_card_drag(self, event, index):
                self._drag_start_y = event.y_root
                self._drag_index = index
        
    def on_card_drag(self, event, index):
        if not hasattr(self, '_drag_start_y'): return
        dy = event.y_root - self._drag_start_y
        
        if abs(dy) > 100:
            projects = self.config.get("projects", [])
            
            query = getattr(self, "search_var", ctk.StringVar()).get().lower() if hasattr(self, "search_var") else ""
            is_archived_tab = getattr(self, "current_archive_tab", "Active") == "Archived"
            visual_map = [(i, p) for i, p in enumerate(projects) if (query in p.get("name", "").lower() or query in p.get("path", "").lower()) and p.get("is_archived", False) == is_archived_tab]
            
            sort_choice = getattr(self, "sort_var", ctk.StringVar(value=_("เรียงตาม: ล่าสุด"))).get() if hasattr(self, "sort_var") else _("เรียงตาม: ล่าสุด")
            if sort_choice == _("เรียงตาม: A-Z"):
                visual_map.sort(key=lambda x: x[1].get("name", "").lower())
            elif sort_choice == _("เรียงตาม: Z-A"):
                visual_map.sort(key=lambda x: x[1].get("name", "").lower(), reverse=True)
                
            visual_idx = next((v_idx for v_idx, (abs_idx, _) in enumerate(visual_map) if abs_idx == index), -1)
            
            if visual_idx != -1:
                swap_visual_idx = visual_idx + 1 if dy > 0 else visual_idx - 1
                if 0 <= swap_visual_idx < len(visual_map):
                    swap_idx = visual_map[swap_visual_idx][0]
                    projects[index], projects[swap_idx] = projects[swap_idx], projects[index]
                    self.save_local_config()
                    self._drag_start_y = event.y_root
                    self.show_home()
        

                
    def launch_card_shortcut(self, proj, shortcut_num):
        import subprocess
        # Get target from config
        default_target = r"tools\flagship\TStudio\tstudio_app.py" if shortcut_num == 1 else r"tools\flagship\TRun\trun_app.py"
        target_path = proj.get(f"shortcut_{shortcut_num}_path", default_target)
        abs_target = os.path.join(os.path.dirname(__file__), target_path)
        
        if not os.path.exists(abs_target):
            messagebox.showerror(_("Error"), f"ไม่พบไฟล์โปรแกรม:\n{abs_target}")
            return
            
        proj_path = proj.get("path", "")
        # Run subprocess
        try:
            if abs_target.lower().endswith(".py"):
                import sys
                subprocess.Popen([sys.executable, abs_target, proj_path])
            else:
                subprocess.Popen([abs_target, proj_path])
        except Exception as e:
            messagebox.showerror(_("Error"), f"ไม่สามารถรันโปรแกรมได้: {e}")
            
    def configure_shortcut(self, proj_index, shortcut_num):
        projects = self.config.get("projects", [])
        proj = projects[proj_index]

        top = ctk.CTkToplevel(self)
        top.title(f"ตั้งค่าปุ่มลัด {shortcut_num}")
        top.geometry("350x220")
        top.transient(self)
        top.grab_set()
        
        # Center the dialog
        top.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 350) // 2
        y = self.winfo_y() + (self.winfo_height() - 220) // 2
        top.geometry(f"+{x}+{y}")

        ctk.CTkLabel(top, text=f"ตั้งค่าปุ่มลัดที่ {shortcut_num}", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(20, 10))
        ctk.CTkLabel(top, text=_("เลือกโปรแกรมสำหรับปุ่มลัดนี้:"), text_color="gray").pack(pady=(0, 15))

        options = {
            "✏️ TStudio (โปรแกรมแปล)": ("TStudio", r"tools\\flagship\\TStudio\\tstudio_app.py"),
            _("▶️ TRun (โปรแกรมรันทดสอบ)"): ("TRun", r"tools\\flagship\\TRun\\trun_app.py"),
            _("🎙️ TVox (โปรแกรมเสียง)"): ("TVox", r"tools\\flagship\\TVox\\tvox_app.py")
        }
        
        current_name = proj.get(f"shortcut_{shortcut_num}_name", "")
        # Remove emojis if they exist
        current_name = current_name.replace("✏️", "").replace("▶️", "").strip()
        
        default_val = _("✏️ TStudio (โปรแกรมแปล)")
        for disp, (nm, pth) in options.items():
            if current_name == nm:
                default_val = disp
                break
        
        selected_var = ctk.StringVar(value=default_val)
        opt_menu = ctk.CTkOptionMenu(top, values=list(options.keys()), variable=selected_var, width=250, fg_color="#313244", button_color="#45475a", button_hover_color="#585b70")
        opt_menu.pack(pady=5)

        def save_shortcut():
            disp_name = selected_var.get()
            real_name, path = options[disp_name]
            proj[f"shortcut_{shortcut_num}_name"] = real_name
            proj[f"shortcut_{shortcut_num}_path"] = path
            self.save_local_config()
            top.destroy()
            self.show_home()
        


        btn_save = ctk.CTkButton(top, text=_("บันทึก 💾"), command=save_shortcut, fg_color="#a6e3a1", text_color="#11111b", hover_color="#94e2d5")
        btn_save.pack(pady=20)

    def show_dashboard_help(self):
        help_win = ctk.CTkToplevel(self)
        help_win.title(_("วิธีใช้งาน Dashboard"))
        help_win.geometry("600x500")
        help_win.transient(self)
        help_win.grab_set()
        
        ctk.CTkLabel(help_win, text=_("คู่มือการใช้งาน Project Dashboard"), font=ctk.CTkFont(size=22, weight="bold"), text_color="#89b4fa").pack(pady=(20, 10))
        
        scroll = ctk.CTkScrollableFrame(help_win, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        help_text = """
1. เพิ่มโปรเจกต์ใหม่ (+ New Project):
   • สำหรับสร้างโฟลเดอร์โปรเจกต์งานแปลเกมใหม่ ระบบจะให้คุณเลือกที่เก็บไฟล์ และตั้งชื่อโปรเจกต์

2. นำเข้าโปรเจกต์ (📥 Import Project):
   • หากคุณมีโฟลเดอร์โปรเจกต์งานแปลเก่าอยู่แล้ว สามารถกดนำเข้าเพื่อให้แสดงบน Dashboard ได้ทันที

3. ค้นหาโปรเจกต์ (🔍):
   • พิมพ์ชื่อโปรเจกต์เพื่อกรองค้นหาอย่างรวดเร็ว

4. การจัดการโปรเจกต์ (ปุ่มบนการ์ด):
   • ⚙️ ตั้งค่า: เลือกโฟลเดอร์สำหรับเก็บไฟล์แปลโดยเฉพาะ
   • ✏️ แก้ไขชื่อ: เปลี่ยนชื่อโปรเจกต์ที่แสดงบนหน้าจอ
   • 🗑️ ลบ: ลบโปรเจกต์ออกจาก Dashboard (โฟลเดอร์และไฟล์จริงจะไม่ถูกลบ)

5. ปุ่ม Action (ในตารางไฟล์):
   • ↻ สแกนไฟล์: ตรวจสอบและค้นหาไฟล์ข้อความ (Text/JSON/XML) ภายในโปรเจกต์
   • ℹ️ ดูรายละเอียด: แสดงประวัติว่ามีไฟล์อะไรที่สแกนเจอหรือเกิดข้อผิดพลาดบ้าง
   • 📂 เปิดโฟลเดอร์: เปิดหน้าต่าง Windows Explorer ไปยังที่เก็บโปรเจกต์

6. การส่งโปรเจกต์ไปเปิดในเครื่องมือแปล:
   • เมื่อคุณมีโปรเจกต์แล้ว สามารถไปที่เมนู 'Tool Library'
   • เลือกโปรแกรมที่ต้องการ และเปลี่ยนช่อง 'พ่วงโปรเจกต์: ไม่มี' ให้เป็นชื่อโปรเจกต์ของคุณ
   • จากนั้นกด 🚀 Launch ระบบจะส่งโปรเจกต์ไปเปิดในโปรแกรมแปลนั้นๆ โดยตรง!
"""
        lbl_content = ctk.CTkLabel(scroll, text=help_text.strip(), font=ctk.CTkFont(size=14), justify="left", anchor="w", wraplength=520)
        lbl_content.pack(fill="both", expand=True, padx=10, pady=10)
        
        btn_close = ctk.CTkButton(help_win, text=_("เข้าใจแล้ว"), fg_color="#a6e3a1", text_color="#1e1e2e", hover_color="#94e2d5", font=ctk.CTkFont(weight="bold"), command=help_win.destroy)
        btn_close.pack(pady=20)

        # Update card removed per user request

    def on_projects_resize(self, event):
        usable_width = event.width - 60 
        
        view_mode = "Large"
        if hasattr(self, 'view_mode_var'):
            view_mode = self.view_mode_var.get()
            
        if view_mode == "List":
            cols = 1
        elif view_mode == "Medium":
            card_width = 350
            cols = max(1, usable_width // card_width)
        else:
            card_width = 470 
            cols = max(1, usable_width // card_width)
        
        if getattr(self, "_current_proj_cols", -1) != cols:
            self._current_proj_cols = cols
            self._rearrange_project_cards()
            
            # Smart Reset: Force layout to calculate new height, then snap to top
            def _reset_scroll():
                try:
                    self.projects_frame.update_idletasks()
                    self.projects_frame._parent_canvas.configure(scrollregion=self.projects_frame._parent_canvas.bbox("all"))
                    self.projects_frame._parent_canvas.yview_moveto(0.0)
                    self.projects_frame._parent_canvas.xview_moveto(0.0)
                except Exception:
                    pass
            self.after(50, _reset_scroll)
            
    def _rearrange_project_cards(self):
        if not hasattr(self, "project_card_widgets"): return
        cols = getattr(self, "_current_proj_cols", 1)
        if cols < 1: cols = 1
        
        query = ""
        if hasattr(self, "search_var"):
            query = self.search_var.get().lower()
            
        for w, p in self.project_card_widgets:
            w.grid_forget()
            
        is_archived_tab = getattr(self, "current_archive_tab", "Active") == "Archived"
        visible_items = [(w, p) for w, p in self.project_card_widgets if (query in p.get("name", "").lower() or query in p.get("path", "").lower()) and p.get("is_archived", False) == is_archived_tab]
        
        sort_choice = getattr(self, "sort_var", ctk.StringVar(value=_("เรียงตาม: ล่าสุด"))).get()
        if sort_choice == _("เรียงตาม: A-Z"):
            visible_items.sort(key=lambda x: x[1].get("name", "").lower())
        elif sort_choice == _("เรียงตาม: Z-A"):
            visible_items.sort(key=lambda x: x[1].get("name", "").lower(), reverse=True)
            
        visible = [w for w, p in visible_items]
        
        for i, w in enumerate(visible):
            row = i // cols
            col = i % cols
            
            view_mode = getattr(self, "view_mode_var", ctk.StringVar(value="Large")).get()
            if view_mode == "List":
                w.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
            else:
                w.grid(row=row, column=col, padx=10, pady=10, sticky="nw")
            
        # Adjust weights to allow stretching for List view
        try:
            view_mode = getattr(self, "view_mode_var", ctk.StringVar(value="Large")).get()
            for c in range(15): # Clear any old weights
                self.projects_frame.grid_columnconfigure(c, weight=0)
                
            if view_mode == "List":
                self.projects_frame.grid_columnconfigure(0, weight=1)
            else:
                self.projects_frame.grid_columnconfigure(cols, weight=1)
        except Exception:
            pass
            


    def fetch_and_save_cover_bg(self, project_path, game_name):
        import threading
        import urllib.request
        import urllib.parse
        import json
        from PIL import Image

        def task():
            try:
                query = urllib.parse.quote(game_name)
                url = f"https://store.steampowered.com/api/storesearch/?term={query}&l=english&cc=US"
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req) as response:
                    data = json.loads(response.read().decode('utf-8'))
                    if data.get("total", 0) > 0:
                        appid = data["items"][0]["id"]
                        header_url = f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/header.jpg"
                        
                        # Download image
                        img_req = urllib.request.Request(header_url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(img_req) as img_resp:
                            img_data = img_resp.read()
                            
                        cover_path = os.path.join(project_path, "thub_cover.jpg")
                        with open(cover_path, "wb") as f:
                            f.write(img_data)
                            
                        # Refresh UI
                        self.after(0, self.show_home)
            except Exception as e:
                print(f"Cover fetch failed: {e}")
                
        threading.Thread(target=task, daemon=True).start()

    def add_new_project_wizard(self):
        wizard = ProjectWizardWindow(self, is_import_mode=False)
        self.wait_window(wizard)
        
        if not wizard.result:
            return
            
        res = wizard.result
        game_name = res["name"]
        project_path = res["path"]
        
        if os.path.exists(project_path):
            # Check if already registered
            for p in self.config.get("projects", []):
                if p.get("path") == project_path:
                    messagebox.showerror(_("Error"), f"พื้นที่ทำงานนี้มีการลงทะเบียนในระบบอยู่แล้วครับ:\n{project_path}")
                    return
            if not messagebox.askyesno(_("Folder Exists"), f"มีโฟลเดอร์อยู่แล้วที่พาธ:\n{project_path}\n\nคุณต้องการสร้างโปรเจกต์ทับในโฟลเดอร์นี้หรือไม่?"):
                return
                
        try:
            os.makedirs(os.path.join(project_path, "01_Original_Backup"), exist_ok=True)
            os.makedirs(os.path.join(project_path, "02_Translation_Workspace"), exist_ok=True)
            os.makedirs(os.path.join(project_path, "03_Font_and_UI"), exist_ok=True)
            os.makedirs(os.path.join(project_path, "04_Packed_Mod"), exist_ok=True)
            os.makedirs(os.path.join(project_path, "05_Scripts_and_Tools"), exist_ok=True)
            os.makedirs(os.path.join(project_path, "06_Releases"), exist_ok=True)
            
            # Create Project-Bound Profile folder
            os.makedirs(os.path.join(project_path, ".thub", "profile"), exist_ok=True)
            
            
            # Create thub_project.json
            project_meta = {
                "project_name": game_name,
                "version": "1.0.0",
                "author": res["author"],
                "contributors": res["contributors"],
                "project_link": res["link"],
                "game_path": res.get("game_dir", ""),
                "tool_path": res.get("tool_dir", ""),
                "source_lang": res.get("source_lang", "English"),
                "target_lang": res.get("target_lang", "Thai"),
                "profile_name": res.get("profile_name", ""),
                "notes": res["notes"]
            }
            with open(os.path.join(project_path, "thub_project.json"), "w", encoding="utf-8") as f:
                json.dump(project_meta, f, indent=4, ensure_ascii=False)
                
            # Create README.md
            readme_content = f"""# 📁 โปรเจกต์แปลเกม: {game_name}
_("ยินดีต้อนรับสู่พื้นที่ทำงานแปลเกมผ่านระบบ THub Workspace!")

## รายละเอียดโปรเจกต์ (Project Details)
_("- **ชื่อโปรเจกต์ / เกม**:") {game_name}
_("- **ผู้พัฒนา / ทีมแปล**:") {res["author"] if res["author"] else "-"}
_("- **ทีมงาน / ผู้ร่วมแปล**:") {res["contributors"] if res["contributors"] else "-"}
_("- **ลิงก์โปรเจกต์ / GitHub**:") {res["link"] if res["link"] else "-"}
_("- **บันทึกย่อ**:") {res["notes"] if res["notes"] else "-"}

## โครงสร้างโฟลเดอร์ทำงาน (Workspace Structure)
- **`01_Original_Backup`**: _("โฟลเดอร์สำหรับเก็บไฟล์ข้อความต้นฉบับดั้งเดิมของเกม (เช่น ภาษาอังกฤษ) เพื่อใช้สำรองข้อมูล")
- **`02_Translation_Workspace`**: _("โฟลเดอร์สำหรับทำไฟล์แปลภาษาไทย (.csv, .xlsx, .json) เพื่อเปิดในโปรแกรม TStudio")
- **`03_Font_and_UI`**: _("โฟลเดอร์สำหรับเก็บไฟล์ฟอนต์, แผ่นภาพ Texture (Atlas), พิกัดฟอนต์ (.fnt/.xml), และตัวแมปปิ้งสระ PUA")
- **`04_Packed_Mod`**: _("โฟลเดอร์ทดสอบที่จัดวางโครงสร้างตัวม็อดไว้พร้อมสำหรับการนำไปยัดหรือติดตั้งทับลงเกมจริง")
- **`05_Scripts_and_Tools`**: _("โฟลเดอร์สำหรับเก็บสคริปต์เฉพาะกิจ (เช่น สคริปต์แยกคำแปล, สคริปต์แพ็กกลับ) หรือโปรแกรมแกะไฟล์เฉพาะเกม")
- **`06_Releases`**: _("โฟลเดอร์สำหรับเก็บไฟล์บิลด์สำเร็จรูปสุดท้าย (.zip, .rar) สำหรับนำไปแจกจ่ายให้ผู้ใช้หรือผู้ทดสอบ")

---
_("*จัดระบบการจัดการโดย THub Launcher*")
"""
            with open(os.path.join(project_path, "README.md"), "w", encoding="utf-8") as f:
                f.write(readme_content.strip())

            self.config.setdefault("projects", []).insert(0, {
                "name": game_name,
                "path": project_path,
                "game_dir": res.get("game_dir", ""),
                "tool_dir": res.get("tool_dir", ""),
                "source_lang": res.get("source_lang", "English"),
                "target_lang": res.get("target_lang", "Thai"),
                "profile_name": res.get("profile_name", ""),
                "translation_folders": ["02_Translation_Workspace"],
                "status": "In Progress"
            })
            self.save_local_config()
            self.fetch_and_save_cover_bg(project_path, game_name)
            messagebox.showinfo(_("Success"), f"สร้างโปรเจกต์ {game_name} สำเร็จ!\nโครงสร้างโฟลเดอร์พร้อมใช้งานแล้ว")
            self.show_home()
        except Exception as e:
            messagebox.showerror(_("Error"), f"สร้างโปรเจกต์ล้มเหลว: {e}")

    def import_project_wizard(self):
        folder_path = filedialog.askdirectory(title=_("เลือกโฟลเดอร์โปรเจกต์ที่ต้องการนำเข้า"), parent=self)
        if not folder_path:
            return
            
        for p in self.config.get("projects", []):
            if p.get("path") == folder_path:
                messagebox.showinfo(_("Info"), _("โปรเจกต์นี้อยู่ในระบบแล้วครับ!"))
                return
                
        json_path = os.path.join(folder_path, "thub_project.json")
        project_name = os.path.basename(folder_path)
        author_name = ""
        game_dir = ""
        tool_dir = ""
        source_lang = "English"
        target_lang = "Thai"
        profile_name = ""
        
        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                    project_name = meta.get("project_name", project_name)
                    author_name = meta.get("author", "")
                    game_dir = meta.get("game_path", "")
                    tool_dir = meta.get("tool_path", "")
                    source_lang = meta.get("source_lang", "English")
                    target_lang = meta.get("target_lang", "Thai")
                    profile_name = meta.get("profile_name", "")
            except Exception:
                pass
        else:
            wizard = ProjectWizardWindow(self, is_import_mode=True, initial_path=folder_path)
            self.wait_window(wizard)
            if not wizard.result:
                return
                
            res = wizard.result
            project_name = res["name"]
            author_name = res["author"]
            game_dir = res.get("game_dir", "")
            tool_dir = res.get("tool_dir", "")
            source_lang = res.get("source_lang", "English")
            target_lang = res.get("target_lang", "Thai")
            profile_name = res.get("profile_name", "")
            
            try:
                project_meta = {
                    "project_name": project_name,
                    "version": "1.0.0",
                    "author": author_name,
                    "contributors": res["contributors"],
                    "project_link": res["link"],
                    "game_path": game_dir,
                    "tool_path": tool_dir,
                    "source_lang": source_lang,
                    "target_lang": target_lang,
                    "profile_name": profile_name,
                    "notes": res["notes"]
                }
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(project_meta, f, indent=4, ensure_ascii=False)
                    
                readme_path = os.path.join(folder_path, "README.md")
                if not os.path.exists(readme_path):
                    readme_content = f"""# 📁 โปรเจกต์แปลเกม: {project_name}
_("ยินดีต้อนรับสู่พื้นที่ทำงานแปลเกมผ่านระบบ THub Workspace!")

## รายละเอียดโปรเจกต์ (Project Details)
_("- **ชื่อโปรเจกต์ / เกม**:") {project_name}
_("- **ผู้พัฒนา / ทีมแปล**:") {author_name if author_name else "-"}
_("- **ทีมงาน / ผู้ร่วมแปล**:") {res["contributors"] if res["contributors"] else "-"}
_("- **ลิงก์โปรเจกต์ / GitHub**:") {res["link"] if res["link"] else "-"}
_("- **บันทึกย่อ**:") {res["notes"] if res["notes"] else "-"}

## โครงสร้างโฟลเดอร์ทำงาน (Workspace Structure)
- **`01_Original_Backup`**: _("โฟลเดอร์สำหรับเก็บไฟล์ข้อความต้นฉบับดั้งเดิมของเกม (เช่น ภาษาอังกฤษ) เพื่อใช้สำรองข้อมูล")
- **`02_Translation_Workspace`**: _("โฟลเดอร์สำหรับทำไฟล์แปลภาษาไทย (.csv, .xlsx, .json) เพื่อเปิดในโปรแกรม TStudio")
- **`03_Font_and_UI`**: _("โฟลเดอร์สำหรับเก็บไฟล์ฟอนต์, แผ่นภาพ Texture (Atlas), พิกัดฟอนต์ (.fnt/.xml), และตัวแมปปิ้งสระ PUA")
- **`04_Packed_Mod`**: _("โฟลเดอร์ทดสอบที่จัดวางโครงสร้างตัวม็อดไว้พร้อมสำหรับการนำไปยัดหรือติดตั้งทับลงเกมจริง")
- **`05_Scripts_and_Tools`**: _("โฟลเดอร์สำหรับเก็บสคริปต์เฉพาะกิจ (เช่น สคริปต์แยกคำแปล, สคริปต์แพ็กกลับ) หรือโปรแกรมแกะไฟล์เฉพาะเกม")
- **`06_Releases`**: _("โฟลเดอร์สำหรับเก็บไฟล์บิลด์สำเร็จรูปสุดท้าย (.zip, .rar) สำหรับนำไปแจกจ่ายให้ผู้ใช้หรือผู้ทดสอบ")

---
_("*จัดระบบการจัดการโดย THub Launcher*")
"""
                    with open(readme_path, "w", encoding="utf-8") as f:
                        f.write(readme_content.strip())
            except Exception as e:
                messagebox.showerror(_("Error"), f"สร้างไฟล์ตั้งค่าล้มเหลว: {e}")
                return

        try:
            os.makedirs(os.path.join(folder_path, "01_Original_Backup"), exist_ok=True)
            os.makedirs(os.path.join(folder_path, "02_Translation_Workspace"), exist_ok=True)
            os.makedirs(os.path.join(folder_path, "03_Font_and_UI"), exist_ok=True)
            os.makedirs(os.path.join(folder_path, "04_Packed_Mod"), exist_ok=True)
            os.makedirs(os.path.join(folder_path, "05_Scripts_and_Tools"), exist_ok=True)
            os.makedirs(os.path.join(folder_path, "06_Releases"), exist_ok=True)
            
            self.config.setdefault("projects", []).insert(0, {
                "name": project_name,
                "path": folder_path,
                "game_dir": game_dir,
                "tool_dir": tool_dir,
                "source_lang": source_lang,
                "target_lang": target_lang,
                "profile_name": profile_name,
                "status": "Imported"
            })
            self.save_local_config()
            self.show_home()
        

            messagebox.showinfo(_("Success"), f"นำเข้าโปรเจกต์ {project_name} สำเร็จ!\nระบบได้ตรวจสอบและสร้างโฟลเดอร์มาตรฐานที่ยังขาดให้เรียบร้อยแล้ว")
        except Exception as e:
            messagebox.showerror(_("Error"), f"นำเข้าโปรเจกต์ล้มเหลว: {e}")

    def rename_project(self, index):
        projects = self.config.get("projects", [])
        if 0 <= index < len(projects):
            old_name = projects[index].get("name", "")
            dialog = ctk.CTkInputDialog(text=f"{_('เปลี่ยนชื่อโปรเจกต์ (เดิม:')} {old_name}):", title="Rename Project")
            new_name = dialog.get_input()
            if new_name and new_name != old_name:
                projects[index]["name"] = new_name
                self.save_local_config()
                self.show_home()
        


    def delete_project(self, index):
        projects = self.config.get("projects", [])
        if 0 <= index < len(projects):
            proj_name = projects[index].get("name", "")
            msg = _("คุณต้องการนำโปรเจกต์ '{proj_name}' ออกจากหน้า Dashboard ใช่หรือไม่?\n\n(ระบบจะไม่ลบโฟลเดอร์และไฟล์จริงของคุณ ข้อมูลทั้งหมดจะยังคงอยู่ในเครื่อง)", proj_name=proj_name)
            if messagebox.askyesno(_("Confirm Delete"), msg, parent=self):
                projects.pop(index)
                self.save_local_config()
                self.show_home()
        


    def set_translation_folder(self, index):
        projects = self.config.get("projects", [])
        if 0 <= index < len(projects):
            proj = projects[index]
            root_path = proj.get("path", "")
            
            # Load extra info from thub_project.json
            import json, os
            meta_path = os.path.join(root_path, "thub_project.json")
            meta = {}
            if os.path.exists(meta_path):
                try:
                    with open(meta_path, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                except:
                    pass
            
            top = ctk.CTkToplevel(self)
            top.title(f"⚙️ การตั้งค่าโปรเจกต์: {proj.get('name')}")
            top.geometry("700x750")
            top.transient(self)
            top.grab_set()
            
            lbl_title = ctk.CTkLabel(top, text=_("ตั้งค่ารายละเอียดโปรเจกต์"), font=ctk.CTkFont(size=22, weight="bold"), text_color="#cba6f7")
            lbl_title.pack(pady=(20, 10))
            
            scroll_frame = ctk.CTkScrollableFrame(top, fg_color="transparent")
            scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)
            
            form_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            form_frame.pack(fill="x", expand=True, padx=20)
            
            form_frame.columnconfigure(0, weight=1)
            form_frame.columnconfigure(1, weight=3)
            form_frame.columnconfigure(2, weight=0)
            
            row = 0
            
            # 1. Project Name
            ctk.CTkLabel(form_frame, text=_("ชื่อโปรเจกต์ / เกม *:"), font=ctk.CTkFont(weight="bold"), anchor="w").grid(row=row, column=0, sticky="w", pady=10)
            ent_name = ctk.CTkEntry(form_frame)
            ent_name.grid(row=row, column=1, columnspan=2, sticky="ew", pady=10)
            ent_name.insert(0, proj.get("name", ""))
            row += 1
            
            # 1.5 Profile Name (Removed - using Project-Bound Profiles)
            
            
            # 2. Languages
            ctk.CTkLabel(form_frame, text=_("ภาษา (ต้นฉบับ -> แปล):"), font=ctk.CTkFont(weight="bold"), anchor="w").grid(row=row, column=0, sticky="w", pady=10)
            lang_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
            lang_frame.grid(row=row, column=1, columnspan=2, sticky="ew", pady=10)
            
            lang_options = ["English", "Thai", "Japanese", "Chinese", "Korean", "French", "Spanish", "German"]
            cbo_source_lang = ctk.CTkComboBox(lang_frame, values=lang_options, width=120)
            cbo_source_lang.set(proj.get("source_lang", meta.get("source_lang", "English")))
            cbo_source_lang.pack(side="left", padx=(0, 10))
            
            ctk.CTkLabel(lang_frame, text="➡️", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
            
            cbo_target_lang = ctk.CTkComboBox(lang_frame, values=["Thai", "English", "Japanese", "Chinese", "Korean"], width=120)
            cbo_target_lang.set(proj.get("target_lang", meta.get("target_lang", "Thai")))
            cbo_target_lang.pack(side="left", padx=(10, 0))
            row += 1
            
            # 3. Developer / Author
            ctk.CTkLabel(form_frame, text=_("ผู้พัฒนา / ผู้แปล:"), font=ctk.CTkFont(weight="bold"), anchor="w").grid(row=row, column=0, sticky="w", pady=10)
            ent_author = ctk.CTkEntry(form_frame)
            ent_author.grid(row=row, column=1, sticky="ew", pady=10, padx=(0, 10))
            ent_author.insert(0, meta.get("author", self.config.get("default_author", "")))
            
            def save_default_value(key, value):
                self.config[key] = value.strip()
                self.save_local_config()
                messagebox.showinfo(_("Saved"), _("บันทึกค่าเริ่มต้นสำเร็จ!"), parent=top)
            
            btn_save_author = ctk.CTkButton(form_frame, text=_("💾 จำค่า"), width=80, fg_color="#313244", hover_color="#45475a", command=lambda: save_default_value("default_author", ent_author.get()))
            btn_save_author.grid(row=row, column=2, sticky="ew", pady=10)
            row += 1
            
            # 4. Contributors
            ctk.CTkLabel(form_frame, text=_("ผู้ร่วมแปล / ทีมงาน:"), font=ctk.CTkFont(weight="bold"), anchor="w").grid(row=row, column=0, sticky="w", pady=10)
            ent_contributors = ctk.CTkEntry(form_frame)
            ent_contributors.grid(row=row, column=1, sticky="ew", pady=10, padx=(0, 10))
            ent_contributors.insert(0, meta.get("contributors", self.config.get("default_contributors", "")))
            
            btn_save_contributors = ctk.CTkButton(form_frame, text=_("💾 จำค่า"), width=80, fg_color="#313244", hover_color="#45475a", command=lambda: save_default_value("default_contributors", ent_contributors.get()))
            btn_save_contributors.grid(row=row, column=2, sticky="ew", pady=10)
            row += 1
            
            # 5. Project Link
            ctk.CTkLabel(form_frame, text=_("ลิงก์โปรเจกต์ / GitHub:"), font=ctk.CTkFont(weight="bold"), anchor="w").grid(row=row, column=0, sticky="w", pady=10)
            ent_link = ctk.CTkEntry(form_frame)
            ent_link.grid(row=row, column=1, columnspan=2, sticky="ew", pady=10)
            ent_link.insert(0, meta.get("project_link", ""))
            row += 1
            
            # 6. Workspace Path (Read Only)
            ctk.CTkLabel(form_frame, text=_("ตำแหน่งโปรเจกต์ (Workspace):"), font=ctk.CTkFont(weight="bold"), anchor="w").grid(row=row, column=0, sticky="w", pady=10)
            ent_path = ctk.CTkEntry(form_frame)
            ent_path.grid(row=row, column=1, columnspan=2, sticky="ew", pady=10)
            ent_path.insert(0, proj.get("path", ""))
            ent_path.configure(state="disabled")
            row += 1
            
            # 7. Game Dir
            ctk.CTkLabel(form_frame, text=_("ตำแหน่งติดตั้งเกม (Game Dir):"), font=ctk.CTkFont(weight="bold"), anchor="w").grid(row=row, column=0, sticky="w", pady=10)
            ent_game_dir = ctk.CTkEntry(form_frame)
            ent_game_dir.grid(row=row, column=1, sticky="ew", pady=10, padx=(0, 10))
            ent_game_dir.insert(0, proj.get("game_dir", meta.get("game_path", "")))
            
            def browse_game_dir():
                folder = filedialog.askdirectory(title=_("เลือกโฟลเดอร์ติดตั้งเกม (Game Directory)"), parent=top)
                if folder:
                    ent_game_dir.delete(0, 'end')
                    ent_game_dir.insert(0, folder)
            btn_browse_game = ctk.CTkButton(form_frame, text=_("📂 เลือก"), width=80, fg_color="#313244", hover_color="#45475a", command=browse_game_dir)
            btn_browse_game.grid(row=row, column=2, sticky="ew", pady=10)
            row += 1
            
            # 8. Tool Dir
            ctk.CTkLabel(form_frame, text=_("ตำแหน่งเครื่องมือ (Tool Dir):"), font=ctk.CTkFont(weight="bold"), anchor="w").grid(row=row, column=0, sticky="w", pady=10)
            ent_tool_dir = ctk.CTkEntry(form_frame)
            ent_tool_dir.grid(row=row, column=1, sticky="ew", pady=10, padx=(0, 10))
            ent_tool_dir.insert(0, proj.get("tool_dir", meta.get("tool_path", "")))
            
            def browse_tool_dir():
                folder = filedialog.askdirectory(title=_("เลือกโฟลเดอร์เครื่องมือม็อด (Tool Directory)"), parent=top)
                if folder:
                    ent_tool_dir.delete(0, 'end')
                    ent_tool_dir.insert(0, folder)
            btn_browse_tool = ctk.CTkButton(form_frame, text=_("📂 เลือก"), width=80, fg_color="#313244", hover_color="#45475a", command=browse_tool_dir)
            btn_browse_tool.grid(row=row, column=2, sticky="ew", pady=10)
            row += 1
            
            # 8.5 Steam Cover Button
            def manual_fetch_cover():
                self.fetch_and_save_cover_bg(root_path, ent_name.get().strip())
                messagebox.showinfo(_("กำลังดึงรูป"), _("ระบบกำลังพยายามค้นหาและดึงรูปหน้าปกจาก Steam อยู่เบื้องหลัง..."), parent=top)
            
            btn_fetch = ctk.CTkButton(form_frame, text=_("🖼️ โหลดภาพหน้าปกจาก Steam ใหม่"), command=manual_fetch_cover, fg_color="#313244", hover_color="#45475a")
            btn_fetch.grid(row=row, column=1, sticky="ew", pady=10)
            row += 1
            
            # 9. Notes
            ctk.CTkLabel(form_frame, text=_("คำอธิบาย / บันทึกย่อ:"), font=ctk.CTkFont(weight="bold"), anchor="w").grid(row=row, column=0, sticky="w", pady=10)
            ent_notes = ctk.CTkEntry(form_frame)
            ent_notes.grid(row=row, column=1, columnspan=2, sticky="ew", pady=10)
            ent_notes.insert(0, meta.get("notes", ""))
            row += 1
            
            # --- Save Button ---
            def save_settings():
                new_name = ent_name.get().strip()
                if not new_name:
                    messagebox.showerror(_("Error"), _("กรุณากรอกชื่อโปรเจกต์"), parent=top)
                    return
                    
                proj["name"] = new_name
                proj["game_dir"] = ent_game_dir.get().strip()
                proj["tool_dir"] = ent_tool_dir.get().strip()
                proj["source_lang"] = cbo_source_lang.get().strip()
                proj["target_lang"] = cbo_target_lang.get().strip()
                
                self.save_local_config()
                # Update thub_project.json if exists
                if os.path.exists(meta_path):
                    try:
                        with open(meta_path, "r", encoding="utf-8") as f:
                            m = json.load(f)
                        m["project_name"] = proj["name"]
                        m["game_path"] = proj["game_dir"]
                        m["tool_path"] = proj["tool_dir"]
                        m["source_lang"] = proj["source_lang"]
                        m["target_lang"] = proj["target_lang"]
                        m["author"] = ent_author.get().strip()
                        m["contributors"] = ent_contributors.get().strip()
                        m["project_link"] = ent_link.get().strip()
                        m["notes"] = ent_notes.get().strip()
                        m["profile_name"] = ent_profile.get().strip()
                        with open(meta_path, "w", encoding="utf-8") as f:
                            json.dump(m, f, indent=4, ensure_ascii=False)
                    except:
                        pass
                        
                top.destroy()
                self.show_home() # Refresh cards to show updated name
                messagebox.showinfo(_("Success"), _("บันทึกการตั้งค่าโปรเจกต์สำเร็จ!"), parent=self)
                
            btn_frame = ctk.CTkFrame(top, fg_color="transparent")
            btn_frame.pack(fill="x", side="bottom", pady=20)
            
            btn_cancel = ctk.CTkButton(btn_frame, text=_("❌ ยกเลิก"), fg_color="#f38ba8", hover_color="#eba0ac", text_color="#1e1e2e", font=ctk.CTkFont(weight="bold"), command=top.destroy)
            btn_cancel.pack(side="right", padx=(10, 40))
            
            btn_save = ctk.CTkButton(btn_frame, text=_("💾 บันทึกการตั้งค่า"), command=save_settings, fg_color="#a6e3a1", text_color="#11111b", hover_color="#94e2d5", font=ctk.CTkFont(weight="bold"))
            btn_save.pack(side="right")
            
            def toggle_archive():
                is_arch = proj.get("is_archived", False)
                proj["is_archived"] = not is_arch
                self.save_local_config()
                top.destroy()
                self.show_home()
        

                
            is_archived = proj.get("is_archived", False)
            archive_text = _("📤 นำกลับมา (Unarchive)") if is_archived else _("🗃️ เก็บเข้าคลัง (Archive)")
            archive_color = "#89b4fa" if is_archived else "#fab387"
            
            btn_archive = ctk.CTkButton(btn_frame, text=archive_text, command=toggle_archive, fg_color=archive_color, hover_color="#313244", text_color="#11111b", font=ctk.CTkFont(weight="bold"))
            btn_archive.pack(side="left", padx=(40, 10))

    def calculate_translation_progress_worker(self, index, scan_paths, pct_lbl, progress_bar, root_path):
        try:
            total_lines = 0
            translated_lines = 0
            details = []
            scanned_count = 0
            skipped_count = 0
            
            valid_exts = {".json", ".csv", ".txt", ".xml", ".yaml", ".ini", ".locres", ".lang", ".po", ".pot", ".msg"}
            thai_pattern = re.compile(r'[\u0E00-\u0E7F]')
            encodings_to_try = ['utf-8', 'utf-16', 'utf-16le', 'cp1252']
            
            for target_path in scan_paths:
                for root, dirs, files in os.walk(target_path):
                    for file in files:
                        ext = os.path.splitext(file)[1].lower()
                        if ext in valid_exts:
                            scanned_count += 1
                            file_path = os.path.join(root, file)
                            file_total = 0
                            file_translated = 0
                            
                            lines = []
                            for enc in encodings_to_try:
                                try:
                                    with open(file_path, 'r', encoding=enc) as f:
                                        lines = f.readlines()
                                    break # Success
                                except UnicodeDecodeError:
                                    continue
                            
                            if not lines:
                                # Fallback
                                try:
                                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                        lines = f.readlines()
                                except Exception:
                                    pass
                                    
                            for line in lines:
                                line = line.strip()
                                if not line: continue
                                file_total += 1
                                if thai_pattern.search(line):
                                    file_translated += 1
                                
                            if file_total > 0:
                                total_lines += file_total
                                translated_lines += file_translated
                                pct = int((file_translated / file_total) * 100)
                                
                                rel_path = os.path.relpath(file_path, root_path)
                                status_emoji = "🟢" if pct == 100 else ("🟡" if pct > 0 else "🔴")
                                details.append(f"{status_emoji} {rel_path} - {pct}% ({file_translated}/{file_total} lines)")
                        else:
                            skipped_count += 1
                                
            final_pct = 0
            if total_lines > 0:
                final_pct = int((translated_lines / total_lines) * 100)
                
            sorted_details = sorted(details)
            sorted_details.insert(0, _("--- สรุปการสแกน ---"))
            sorted_details.insert(1, f"{_('โฟลเดอร์เป้าหมาย:')} {len(scan_paths)} {_('แห่ง')}")
            sorted_details.insert(2, f"{_('ไฟล์ข้อความที่อ่านสำเร็จ:')} {scanned_count} {_('ไฟล์')}")
            sorted_details.insert(3, f"{_('ไฟล์นามสกุลอื่นที่ถูกข้าม:')} {skipped_count} {_('ไฟล์')}")
            sorted_details.insert(4, f"-------------------\n")
                
            projects = self.config.get("projects", [])
            if 0 <= index < len(projects):
                projects[index]["progress_pct"] = final_pct
                projects[index]["progress_details"] = sorted_details
                self.save_local_config()
                
            self.after(0, lambda: self._update_progress_ui(pct_lbl, progress_bar, final_pct))
            
        except Exception as e:
            err_msg = f"{_('เกิดข้อผิดพลาดในการสแกน:')} {e}"
            projects = self.config.get("projects", [])
            if 0 <= index < len(projects):
                projects[index]["progress_details"] = [err_msg]
            self.after(0, lambda: self._update_progress_ui(pct_lbl, progress_bar, 0, error=True))

    def _update_progress_ui(self, pct_lbl, progress_bar, pct, error=False):
        try:
            if pct_lbl.winfo_exists():
                if error:
                    pct_lbl.configure(text="Err!")
                else:
                    pct_lbl.configure(text="Done!")
                    self.after(1500, lambda: pct_lbl.configure(text=f"{pct}%") if pct_lbl.winfo_exists() else None)
            if progress_bar.winfo_exists():
                progress_bar.set(pct / 100.0)
        except Exception:
            pass

    def open_project_folder(self, path):
        if os.path.exists(path):
            os.startfile(path)
        else:
            messagebox.showerror(_("Error"), f"ไม่พบโฟลเดอร์: {path}")

    def check_for_updates(self):
        import threading
        threading.Thread(target=self.check_for_updates_bg, daemon=True).start()

    def check_for_updates_bg(self):
        if not self.config.get("auto_update", True): return
        import requests
        try:
            url = "https://api.github.com/repos/memolyviza2012-max/THub-Launcher/releases/latest"
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            if response.status_code == 200:
                data = response.json()
                tag_name = data.get("tag_name", "v0.0.0")
                latest_version = tag_name[1:] if tag_name.lower().startswith("v") else tag_name
                body = data.get("body", _("ไม่มีข้อมูลอัปเดต"))
                
                if version.parse(latest_version) > version.parse(CURRENT_VERSION):
                    # Find download url (look for .zip asset)
                    assets = data.get("assets", [])
                    zip_asset = next((a for a in assets if a["name"].endswith(".zip")), None)
                    if zip_asset:
                        dl_url = "https://ghproxy.net/" + zip_asset["browser_download_url"]
                        self.after(0, self.prompt_update, latest_version, body, dl_url)
                    else:
                        self.after(0, self.update_status, f"{_('มีเวอร์ชันใหม่')} (v{latest_version}) {_('แต่ไม่พบไฟล์ .zip')}", "orange")
                else:
                    self.after(0, self.update_status, f"{_('คุณใช้งานเวอร์ชันล่าสุดแล้ว')} (v{CURRENT_VERSION})", "gray")
            elif response.status_code in (403, 429):
                self.after(0, self.update_status, _("ตรวจสอบอัปเดตไม่สำเร็จ (Rate Limit ติดลิมิต)"), "orange")
            else:
                self.after(0, self.update_status, f"{_('ตรวจสอบอัปเดตไม่สำเร็จ')} (HTTP {response.status_code})", "orange")
        except Exception as e:
            print(f"Update check error: {e}")
            self.after(0, self.update_status, _("ไม่สามารถตรวจสอบอัปเดตได้ (เครือข่ายมีปัญหา)"), "orange")

    def update_status(self, text, color):
        if hasattr(self, 'update_status_lbl') and self.update_status_lbl.winfo_exists():
            self.update_status_lbl.configure(text=text, text_color=color)

    def prompt_update(self, latest_version, notes, dl_url):
        import sys
        if not getattr(sys, 'frozen', False):
            self.update_status(f"{_('มีเวอร์ชันใหม่:')} v{latest_version} {_('บน GitHub (Dev Mode)')}", "green")
            return
            
        self.update_status(f"{_('มีเวอร์ชันใหม่:')} v{latest_version} {_('พร้อมอัปเดต!')}", "green")
        msg = _('มีอัปเดตเวอร์ชันใหม่') + f" (v{latest_version}) " + _('บน GitHub!\n\nรายละเอียด:\n') + f"{notes}\n\n" + _('คุณต้องการอัปเดตเลยหรือไม่? (โปรแกรมจะรีสตาร์ทตัวเอง)')
        if messagebox.askyesno("Update Available", msg, parent=self):
            import threading
            threading.Thread(target=self.perform_self_update_bg, args=(dl_url,), daemon=True).start()

    def perform_self_update_bg(self, dl_url):
        upd_win = None
        lbl_status = None
        prog_bar = None
        
        def show_updating_window():
            nonlocal upd_win, lbl_status, prog_bar
            upd_win = ctk.CTkToplevel(self)
            upd_win.title("Updating")
            upd_win.geometry("400x200")
            upd_win.transient(self)
            upd_win.grab_set()
            
            ctk.CTkLabel(upd_win, text=_("กำลังดาวน์โหลดอัปเดต..."), font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20, 10))
            prog_bar = ctk.CTkProgressBar(upd_win, width=300, progress_color="#a6e3a1")
            prog_bar.pack(pady=10)
            prog_bar.set(0)
            
            lbl_status = ctk.CTkLabel(upd_win, text="0%", font=ctk.CTkFont(size=14, weight="bold"), text_color="#a6e3a1")
            lbl_status.pack(pady=(0, 10))
            
            ctk.CTkLabel(upd_win, text=_("โปรแกรมจะปิดและเปิดใหม่โดยอัตโนมัติเมื่อเสร็จสิ้น"), font=ctk.CTkFont(size=12), text_color="gray").pack(pady=(10, 20))
            
        def update_progress(pct):
            if prog_bar and lbl_status:
                prog_bar.set(pct / 100.0)
                lbl_status.configure(text=f"{int(pct)}%")
                
        self.after(0, show_updating_window)
        import requests
        import zipfile
        import io
        import sys
        import subprocess
        
        try:
            response = requests.get(dl_url, headers={'User-Agent': 'Mozilla/5.0'}, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = response.headers.get('content-length')
            total_size = int(total_size) if total_size else None
            
            downloaded = 0
            zip_data = bytearray()
            
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    zip_data.extend(chunk)
                    downloaded += len(chunk)
                    
                    if total_size:
                        pct = (downloaded / total_size) * 100
                        self.after(0, update_progress, pct)
                        
            temp_dir = os.path.join(os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__), "_temp_update")
            os.makedirs(temp_dir, exist_ok=True)
            
            with zipfile.ZipFile(io.BytesIO(zip_data)) as z:
                # Handle potential root folder inside zip (e.g. THub/THub.exe)
                first_item = z.namelist()[0]
                has_root_folder = '/' in first_item and first_item.split('/')[0] != ''
                if has_root_folder:
                    root_folder = first_item.split('/')[0] + '/'
                else:
                    root_folder = ""
                    
                for file_info in z.infolist():
                    if root_folder and file_info.filename.startswith(root_folder):
                        if not file_info.is_dir():
                            file_info.filename = file_info.filename[len(root_folder):]
                            z.extract(file_info, temp_dir)
                    else:
                        if not file_info.is_dir():
                            z.extract(file_info, temp_dir)
            
            current_dir = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)
            exe_name = os.path.basename(sys.executable)
            bat_path = os.path.join(current_dir, "update.bat")
            
            bat_content = f"""@echo off
timeout /t 1 /nobreak >nul
if exist "{current_dir}\\{exe_name}.old" del /f /q "{current_dir}\\{exe_name}.old"
ren "{current_dir}\\{exe_name}" "{exe_name}.old"
xcopy /s /e /y "{temp_dir}\\*" "{current_dir}\\"
rmdir /s /q "{temp_dir}"
start "" "{current_dir}\\{exe_name}"
del "%~f0"
"""
            with open(bat_path, "w", encoding="utf-8") as f:
                f.write(bat_content)
                
            # DETACHED_PROCESS (0x00000008) so the bat file outlives this process
            subprocess.Popen(f'"{bat_path}"', shell=True, cwd=current_dir, creationflags=0x00000008)
            import os
            os._exit(0) # Force hard exit to release file locks immediately
            
        except Exception as e:
            print(f"Self-update error: {e}")
            err_msg = f"เกิดข้อผิดพลาดในการอัปเดต: {e}"
            self.after(0, lambda m=err_msg: messagebox.showerror(_("Update Failed"), m, parent=self))

    
    # --- 2. Flagship Products ---
    def show_flagship(self):
        self.clear_main_frame()
        
        lbl_title = ctk.CTkLabel(self.main_frame, text="✨ THub Apps", font=ctk.CTkFont(size=28, weight="bold"))
        lbl_title.pack(anchor="w", padx=30, pady=(20, 10))
        
        # Grid for cards
        self.flagship_grid_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        self.flagship_grid_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        self.flagship_cards = []
        self.current_flagship_cols = 0
        # Unbind previous handler before binding again to avoid stacking leaks
        self.main_frame.unbind("<Configure>")
        self.main_frame.bind("<Configure>", self._on_flagship_grid_resize)

        # Loading message
        self._lbl_flagship_loading = ctk.CTkLabel(self.flagship_grid_frame, text=_("☁️ กำลังซิงค์ข้อมูล Cloud Registry..."), text_color="gray", font=ctk.CTkFont(size=14))
        self._lbl_flagship_loading.grid(row=0, column=0, pady=50)

        # Start thread to fetch JSON
        import threading
        threading.Thread(target=self.fetch_flagship_registry_bg, args=(self.flagship_grid_frame,), daemon=True).start()

    def fetch_flagship_registry_bg(self, parent_frame):
        registry_data = [
            {"id": "TStudio", "name": "TStudio", "desc": "สุดยอดเครื่องมือแปลภาษาด้วย AI\n(วิเคราะห์บริบท & แก้ไขแบบ Line-by-Line)\nรองรับการทำงานกับไฟล์ Localization หลายรูปแบบ", "color": "#89b4fa", "exe": "tstudio_app.py", "icon": "assets/TStudio.png"},
            {"id": "TRun", "name": "TRun", "desc": "เครื่องมือแปลภาษาแบบ Batch อัตโนมัติ\n(รองรับไฟล์ขนาดใหญ่และปริมาณมหาศาล)\nแปลทั้งโปรเจกต์ได้อย่างรวดเร็วในคลิกเดียว", "color": "#a6e3a1", "exe": "trun_app.py", "icon": "assets/TRun.png"},
            {"id": "TVox", "name": "TVox", "desc": "เครื่องมือจัดการ FMV และซับไตเติ้ล\n(วิดีโอเพลเยอร์ & ดึงคลื่นเสียง Waveform)\nออกแบบมาเพื่อการแปลวิดีโอคัทซีนโดยเฉพาะ", "color": "#f38ba8", "exe": "tvox_app.py", "icon": "assets/TVox.png"},
            {"id": "flagship.tfont", "folder": "TFont", "name": "TFont Generator", "desc": "เครื่องมือปรับแต่งและสร้างฟอนต์ PUA", "color": "#b4befe", "exe": "tfont_app.py", "icon": "assets/TFONT.png", "no_project": True},
            {"id": "flagship.tpua", "folder": "TPUA", "name": "TPUA Text Converter", "desc": "เครื่องมือแปลงข้อความภาษาไทยเข้าสู่ระบบ PUA", "color": "#cba6f7", "exe": "tpua_app.py", "icon": "assets/TPUA.png", "no_project": True},
            {"id": "TGlyph", "name": "TGlyph", "desc": "เครื่องมือสร้าง Texture ฟอนต์\n(Generate Texture และแผนที่ตัวอักษร)\nสำหรับดัดแปลงฟอนต์ Bitmap ในเกม", "color": "#fab387", "exe": "tglyph_app.py", "icon": "assets/TGlyph.png", "no_project": True}
        ]
            
        self.after(0, lambda: self.render_flagship_cards(parent_frame, registry_data))

    def _on_flagship_grid_resize(self, event=None):
        if not hasattr(self, 'flagship_cards') or not self.flagship_cards:
            return
            
        # We bind to main_frame, so we check flagship_grid_frame width
        if not self.flagship_grid_frame.winfo_exists():
            return
            
        width = self.flagship_grid_frame.winfo_width()
        if width <= 1: 
            width = 800  # Fallback width if not rendered yet
        
        # Determine number of columns based on width (min width per card ~ 320px)
        cols = max(1, width // 320)
        
        if cols != self.current_flagship_cols:
            self.current_flagship_cols = cols
            self._rearrange_flagship_cards()

    def _rearrange_flagship_cards(self):
        # Reset column weights
        for i in range(10):  # Clear old weights
            self.flagship_grid_frame.grid_columnconfigure(i, weight=0)
            
        for i in range(self.current_flagship_cols):
            self.flagship_grid_frame.grid_columnconfigure(i, weight=1)
            
        row, col = 0, 0
        for card in self.flagship_cards:
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            col += 1
            if col >= self.current_flagship_cols:
                col = 0
                row += 1

    def render_flagship_cards(self, parent_frame, registry_data):
        if hasattr(self, "_lbl_flagship_loading"):
            self._lbl_flagship_loading.destroy()
            
        self.flagship_cards = []
        for item in registry_data:
            card = self.create_flagship_card(parent_frame, item)
            self.flagship_cards.append(card)
            
        # Force an initial layout pass
        self.current_flagship_cols = 0 # Force update
        self._on_flagship_grid_resize()

    def create_flagship_card(self, parent, item):
        card = ctk.CTkFrame(parent, corner_radius=15)
        card.grid_columnconfigure(0, weight=1)
        
        folder_name = item.get("folder", item["id"])
        exe_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "tools", "flagship", folder_name, item["exe"]))
        
        icon_btn = None
        orig_img = None
        if item.get("icon"):
            try:
                full_logo = resource_path(item["icon"])
                if not os.path.exists(full_logo):
                    full_logo = os.path.join(os.path.dirname(os.path.abspath(__file__)), item["icon"])
                if os.path.exists(full_logo):
                    orig_img = ctk.CTkImage(light_image=Image.open(full_logo), size=(80, 80))
                    # Use a Button instead of a Label so it's clickable!
                    icon_btn = ctk.CTkButton(card, text="", image=orig_img, fg_color="transparent", hover_color="#313244", width=80, height=80)
                    icon_btn.grid(row=0, column=0, pady=(20, 0))
            except: pass
            
        ctk.CTkLabel(card, text=item["name"], font=ctk.CTkFont(size=20, weight="bold")).grid(row=1, column=0, pady=(15, 5))
        ctk.CTkLabel(card, text=_(item["desc"]), text_color="gray", justify="center").grid(row=2, column=0, pady=(5, 10))
        
        action_frame = ctk.CTkFrame(card, fg_color="transparent")
        action_frame.grid(row=3, column=0, pady=(0, 20))
        no_project = item.get("no_project", False)

        # Context Selector — hidden for tools that don't need a project context
        context_var = ctk.StringVar(value=_("พ่วงโปรเจกต์: ไม่มี"))
        if not no_project:
            projects = self.config.get("projects", [])
            proj_names = [_("พ่วงโปรเจกต์: ไม่มี"), _("พ่วงโปรเจกต์: เลือกโฟลเดอร์...")] + [f"พ่วง: {p['name']}" for p in projects]
            context_var.set(_("พ่วงโปรเจกต์: ไม่มี"))
            opt_context = ctk.CTkOptionMenu(action_frame, values=proj_names, variable=context_var, width=140, fg_color="#313244", button_color="#45475a")
            opt_context.pack(side="top", pady=(0, 10))

        btn_action = ctk.CTkButton(action_frame, text=_("🚀 เปิดโปรแกรม"), fg_color=item["color"], text_color="#1e1e2e", font=ctk.CTkFont(weight="bold"))
        btn_action.pack(side="top", padx=5)

        def do_launch(e=exe_path, b=icon_btn, i=orig_img, cvar=context_var, noproj=no_project):
            if noproj:
                self.launch_script_with_loading(e, b, i)
                return
            cval = cvar.get()
            if cval == _("พ่วงโปรเจกต์: ไม่มี"):
                self.launch_script_with_loading(e, b, i)
            elif cval == _("พ่วงโปรเจกต์: เลือกโฟลเดอร์..."):
                folder = filedialog.askdirectory(title=_("เลือกโฟลเดอร์ที่จะส่งเข้าโปรแกรม"), parent=self)
                if folder:
                    self.launch_script_with_loading(e, b, i, target_path=folder)
            else:
                pname = cval.replace(f"{_('พ่วง:')} ", "")
                proj_path = next((proj["path"] for proj in self.config.get("projects", []) if proj["name"] == pname), None)
                self.launch_script_with_loading(e, b, i, target_path=proj_path)

        if icon_btn:
            icon_btn.configure(cursor="hand2", command=do_launch)
            btn_action.configure(command=do_launch)
        else:
            def fallback_launch(e=exe_path, cvar=context_var, noproj=no_project):
                if noproj:
                    self.launch_script(e)
                    return
                cval = cvar.get()
                if cval == _("พ่วงโปรเจกต์: ไม่มี"):
                    self.launch_script(e)
                elif cval == _("พ่วงโปรเจกต์: เลือกโฟลเดอร์..."):
                    folder = filedialog.askdirectory(title=_("เลือกโฟลเดอร์ที่จะส่งเข้าโปรแกรม"), parent=self)
                    if folder:
                        self.launch_script(e, target_path=folder)
                else:
                    pname = cval.replace(f"{_('พ่วง:')} ", "")
                    proj_path = next((proj["path"] for proj in self.config.get("projects", []) if proj["name"] == pname), None)
                    self.launch_script(e, target_path=proj_path)
            btn_action.configure(command=fallback_launch)

        return card
            
    def launch_script_with_loading(self, path, icon_btn, orig_img, target_path=None):
        # Show loading state
        icon_btn.configure(image="", text=_("⏳\nกำลังโหลด..."), font=ctk.CTkFont(size=16, weight="bold"))
        self.update()
        
        # Give UI a tiny bit of time to render the loading state before blocking
        self.after(50, lambda: self._execute_launch(path, icon_btn, orig_img, target_path))

    def _execute_launch(self, path, icon_btn, orig_img, target_path=None):
        self.launch_script(path, target_path)
        # Revert UI state back to the original icon after a short delay
        self.after(800, lambda: icon_btn.configure(image=orig_img, text=""))

    def launch_script(self, path, target_path=None):
        import subprocess
        import sys
        try:
            cmd = [sys.executable, path] if path.lower().endswith(".py") else [path]
            if target_path:
                cmd.append(target_path)
            subprocess.Popen(cmd, creationflags=0x00000008, cwd=os.path.dirname(path), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            messagebox.showerror(_("Launch Error"), f"ไม่สามารถเปิดโปรแกรมได้:\n{path}\n\nข้อผิดพลาด:\n{e}", parent=self)

    def show_flagship_update_btn(self, parent_frame, item, latest_tag):
        btn_upd = ctk.CTkButton(parent_frame, text=f"🔴 อัปเดต ({latest_tag})", fg_color="#f38ba8", hover_color="#eba0ac", text_color="#1e1e2e", font=ctk.CTkFont(weight="bold"))
        # Using show_github_versions will show the download modal. 
        # When downloaded, we should ideally update `flagship_versions`.
        btn_upd.configure(command=lambda: self.show_github_versions(item["id"], item["repo"]))
        btn_upd.pack(side="left", padx=5)

    def show_tool_library(self):
        self.clear_main_frame()
        
        lbl_title = ctk.CTkLabel(self.main_frame, text="🧰 The Ultimate Tool Library", font=ctk.CTkFont(size=28, weight="bold"))
        lbl_title.pack(anchor="w", padx=30, pady=(30, 5))
        
        lbl_desc = ctk.CTkLabel(self.main_frame, text=_("คลังแสงเครื่องมือม็อดระดับจักรวาล โหลดตรงจากต้นทาง หรือลิงก์ที่มีในเครื่องได้เลย"), font=ctk.CTkFont(size=14), text_color="gray")
        lbl_desc.pack(anchor="w", padx=30, pady=(0, 20))

        tabview = ctk.CTkTabview(self.main_frame, width=800)
        tabview.pack(fill="both", expand=True, padx=30, pady=10)
        
        tab_fav = tabview.add("⭐ Favorites")
        tab_unreal = tabview.add("Unreal Engine")
        tab_unity = tabview.add("Unity")
        tab_re = tabview.add("RE Engine & Frostbite")
        tab_general = tabview.add("General / Text Editors")
        tab_custom = tabview.add("📁 Custom Tools")
        
        # Load Favorites
        fav_list = self.config.get("favorite_tools", [])
        
        # Helper to render tools for a specific category
        def render_category(category_name, parent_frame):
            tools = TOOL_REGISTRY.get(category_name, [])
            for t in tools:
                self.build_tool_row(parent_frame, t, fav_list)

        # Render default registries
        render_category("Unreal Engine", tab_unreal)
        render_category("Unity", tab_unity)
        render_category("RE Engine & Frostbite", tab_re)
        render_category("General / Text Editors", tab_general)
        
        # Render Custom
        custom_tools = self.config.get("custom_tools", [])
        for ct in custom_tools:
            self.build_tool_row(tab_custom, ct, fav_list, is_custom=True)
            
        btn_add_custom = ctk.CTkButton(tab_custom, text="➕ Add Custom Tool", command=self.add_custom_tool_dialog)
        btn_add_custom.pack(pady=10)

        # Render Favorites
        for cat, tools in TOOL_REGISTRY.items():
            for t in tools:
                if t["name"] in fav_list:
                    self.build_tool_row(tab_fav, t, fav_list, is_fav_tab=True)
        for ct in custom_tools:
            if ct["name"] in fav_list:
                self.build_tool_row(tab_fav, ct, fav_list, is_custom=True, is_fav_tab=True)
                
        if not fav_list:
            ctk.CTkLabel(tab_fav, text=_("ยังไม่มีเครื่องมือโปรด กด ⭐ ที่เครื่องมือเพื่อเพิ่มมาไว้หน้านี้"), text_color="gray").pack(pady=20)

    def build_tool_row(self, parent_frame, tool_data, fav_list, is_custom=False, is_fav_tab=False):
        tool_name = tool_data["name"]
        description = _(tool_data["desc"])
        
        row = ctk.CTkFrame(parent_frame, fg_color="transparent")
        row.pack(fill="x", pady=5)
        row.grid_columnconfigure(2, weight=1)
        
        # Star Button
        star_text = "⭐" if tool_name in fav_list else "☆"
        btn_star = ctk.CTkButton(row, text=star_text, width=30, fg_color="transparent", text_color="#f9e2af" if tool_name in fav_list else "gray", hover_color="#313244", font=ctk.CTkFont(size=18), command=lambda: self.toggle_favorite(tool_name))
        btn_star.grid(row=0, column=0, padx=(5, 0), pady=5)
        
        ctk.CTkLabel(row, text=tool_name, font=ctk.CTkFont(weight="bold", size=16), width=150, anchor="w").grid(row=0, column=1, padx=10, pady=5)
        ctk.CTkLabel(row, text=description, text_color="gray", anchor="w").grid(row=0, column=2, padx=10, pady=5, sticky="w")
        
        tool_data_val = self.config.get("tools", {}).get(tool_name, "")
        
        tool_path = ""
        versions = {}
        active_version = ""
        
        if isinstance(tool_data_val, dict):
            active_version = tool_data_val.get("active_version", "")
            versions = tool_data_val.get("versions", {})
            tool_path = versions.get(active_version, "")
        else:
            tool_path = tool_data_val
        
        # Action Buttons Area
        col_idx = 3
        
        # Manual Site Button
        site_url = tool_data.get("url", f"https://github.com/{tool_data.get('github')}" if "github" in tool_data else "")
        if site_url:
            btn_site = ctk.CTkButton(row, text=_("🌐 โหลดเอง"), width=80, fg_color="#313244", hover_color="#45475a", command=lambda u=site_url: webbrowser.open(u))
            btn_site.grid(row=0, column=col_idx, padx=5, pady=5)
            col_idx += 1
            
        if tool_path and os.path.exists(tool_path):
            if len(versions) > 1:
                def switch_version(selected_ver, t_name=tool_name):
                    self.config["tools"][t_name]["active_version"] = selected_ver
                    self.save_local_config()
                    self.show_tool_library()
                    
                opt = ctk.CTkOptionMenu(row, values=list(versions.keys()), command=switch_version, width=100)
                opt.set(active_version)
                opt.grid(row=0, column=col_idx, padx=5, pady=5)
                col_idx += 1
                
            # Context Selector
            projects = self.config.get("projects", [])
            proj_names = [_("พ่วงโปรเจกต์: ไม่มี"), _("พ่วงโปรเจกต์: เลือกโฟลเดอร์...")] + [f"พ่วง: {p['name']}" for p in projects]
            context_var = ctk.StringVar(value=_("พ่วงโปรเจกต์: ไม่มี"))
            
            opt_context = ctk.CTkOptionMenu(row, values=proj_names, variable=context_var, width=150, fg_color="#313244", button_color="#45475a")
            opt_context.grid(row=0, column=col_idx, padx=5, pady=5)
            col_idx += 1
            
            def do_launch(p=tool_path, cvar=context_var):
                cval = cvar.get()
                if cval == _("พ่วงโปรเจกต์: ไม่มี"):
                    self.launch_linked_tool(p)
                elif cval == _("พ่วงโปรเจกต์: เลือกโฟลเดอร์..."):
                    folder = filedialog.askdirectory(title=_("เลือกโฟลเดอร์ที่จะส่งเข้าโปรแกรม"), parent=self)
                    if folder:
                        self.launch_linked_tool(p, folder)
                else:
                    pname = cval.replace(f"{_('พ่วง:')} ", "")
                    proj_path = next((proj["path"] for proj in self.config.get("projects", []) if proj["name"] == pname), None)
                    self.launch_linked_tool(p, proj_path)

            btn_launch = ctk.CTkButton(row, text="🚀 Launch", width=100, fg_color="#a6e3a1", text_color="#1e1e2e", hover_color="#94e2d5", font=ctk.CTkFont(weight="bold"), command=do_launch)
            btn_launch.grid(row=0, column=col_idx, padx=5, pady=5)
            col_idx += 1
            
            btn_link = ctk.CTkButton(row, text="⚙️", width=30, fg_color="#313244", hover_color="#45475a", command=lambda: self.link_tool(tool_name))
            btn_link.grid(row=0, column=col_idx, padx=(0, 5), pady=5)
            col_idx += 1
            
            btn_uninstall = ctk.CTkButton(row, text="🗑️", width=30, fg_color="#f38ba8", hover_color="#eba0ac", text_color="#1e1e2e", command=lambda: self.uninstall_tool(tool_name))
            btn_uninstall.grid(row=0, column=col_idx, padx=5, pady=5)
            col_idx += 1
        else:
            if "github" in tool_data:
                btn_cloud = ctk.CTkButton(row, text=_("☁️ โหลดจาก GitHub"), width=130, fg_color="#89b4fa", text_color="#1e1e2e", hover_color="#b4befe", font=ctk.CTkFont(weight="bold"), command=lambda g=tool_data["github"], n=tool_name: self.show_github_versions(n, g))
                btn_cloud.grid(row=0, column=col_idx, padx=5, pady=5)
                col_idx += 1
            elif "direct_zip" in tool_data:
                btn_cloud = ctk.CTkButton(row, text="📥 1-Click Install", width=130, fg_color="#a6e3a1", text_color="#1e1e2e", hover_color="#94e2d5", font=ctk.CTkFont(weight="bold"), command=lambda u=tool_data["direct_zip"], n=tool_name: self.download_and_extract_direct(n, u))
                btn_cloud.grid(row=0, column=col_idx, padx=5, pady=5)
                col_idx += 1
                
            btn_link = ctk.CTkButton(row, text="🔗 Link .exe", width=100, fg_color="transparent", border_width=1, border_color="#89b4fa", text_color="#89b4fa", command=lambda: self.link_tool(tool_name))
            btn_link.grid(row=0, column=col_idx, padx=5, pady=5)
            col_idx += 1
            
        if is_custom and not is_fav_tab:
            btn_del = ctk.CTkButton(row, text="🗑️", width=30, fg_color="#f38ba8", hover_color="#eba0ac", text_color="#1e1e2e", command=lambda: self.delete_custom_tool(tool_name))
            btn_del.grid(row=0, column=col_idx, padx=5, pady=5)
            
        # Store row reference for update notifier
        if not hasattr(self, "_tool_row_frames"): self._tool_row_frames = {}
        self._tool_row_frames[tool_name] = row
        
        # Check if an update was already found in background
        if hasattr(self, "_found_tool_updates") and tool_name in self._found_tool_updates:
            latest, repo = self._found_tool_updates[tool_name]
            self.show_tool_update_btn(tool_name, latest, repo)

    def check_tool_updates_bg(self):
        if not self.config.get("auto_update", False): return
        
        if not hasattr(self, "_update_thread_running") or not self._update_thread_running:
            self._update_thread_running = True
            import threading
            threading.Thread(target=self._do_check_tool_updates_bg, daemon=True).start()

    def _do_check_tool_updates_bg(self):
        import urllib.request
        import json
        
        if not hasattr(self, "_found_tool_updates"):
            self._found_tool_updates = {}
            
        tools = self.config.get("tools", {})
        
        for cat, tool_list in TOOL_REGISTRY.items():
            for t in tool_list:
                name = t["name"]
                if "github" in t and name in tools and isinstance(tools[name], dict):
                    try:
                        url = f"https://api.github.com/repos/{t['github']}/releases/latest"
                        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(req, timeout=5) as response:
                            data = json.loads(response.read().decode())
                            latest_tag = data.get("tag_name")
                            active_ver = tools[name].get("active_version")
                            if latest_tag and active_ver and latest_tag != active_ver:
                                self._found_tool_updates[name] = (latest_tag, t["github"])
                                self.main_frame.after(0, self.show_tool_update_btn, name, latest_tag, t["github"])
                    except Exception:
                        pass
        self._update_thread_running = False

    def show_tool_category(self, tab_name, categories, is_fav_tab=False):
        self.clear_main_frame()
        
        # Header
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 10))
        
        lbl_title = ctk.CTkLabel(header_frame, text=tab_name, font=ctk.CTkFont(size=28, weight="bold"))
        lbl_title.pack(side="left")
        
        if is_fav_tab:
            lbl_desc = ctk.CTkLabel(self.main_frame, text=_("เครื่องมือโปรดของคุณ"), font=ctk.CTkFont(size=14), text_color="gray")
            lbl_desc.pack(anchor="w", padx=30, pady=(0, 20))
            
            tool_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
            tool_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
            
            fav_list = self.config.get("favorite_tools", [])
            if not fav_list:
                ctk.CTkLabel(tool_frame, text=_("ยังไม่มีเครื่องมือโปรด กด ⭐ เพื่อเพิ่ม!"), text_color="gray").pack(pady=50)
            else:
                for cat, tool_list in TOOL_REGISTRY.items():
                    for t in tool_list:
                        if t["name"] in fav_list:
                            self.build_tool_row(tool_frame, t, fav_list, is_fav_tab=True)
                            
                custom_tools = self.config.get("custom_tools", [])
                for t in custom_tools:
                    if t["name"] in fav_list:
                        self.build_tool_row(tool_frame, t, fav_list, is_custom=True, is_fav_tab=True)
            return

        lbl_desc = ctk.CTkLabel(self.main_frame, text=f"{_('รวมเครื่องมือสำหรับ')} {tab_name}", font=ctk.CTkFont(size=14), text_color="gray")
        lbl_desc.pack(anchor="w", padx=30, pady=(0, 20))
        
        tool_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        tool_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        fav_list = self.config.get("favorite_tools", [])
        
        for cat in categories:
            if cat == "Custom Tools":
                custom_tools = self.config.get("custom_tools", [])
                if not custom_tools:
                    ctk.CTkLabel(tool_frame, text=_("ยังไม่มีเครื่องมือของคุณ กด + Add Custom Tool เพื่อเพิ่ม!"), text_color="gray").pack(pady=50)
                else:
                    for t in custom_tools:
                        self.build_tool_row(tool_frame, t, fav_list, is_custom=True)
                
                # Add Custom Tool Button
                btn_add = ctk.CTkButton(tool_frame, text="+ Add Custom Tool", fg_color="transparent", border_width=1, border_color="#a6e3a1", text_color="#a6e3a1", hover_color="#313244", font=ctk.CTkFont(weight="bold"), command=self.add_custom_tool_dialog)
                btn_add.pack(pady=20)
            else:
                tools = TOOL_REGISTRY.get(cat, [])
                for t in tools:
                    self.build_tool_row(tool_frame, t, fav_list)

    def show_tool_update_btn(self, name, latest_tag, github_repo):
        if hasattr(self, "_tool_row_frames") and name in self._tool_row_frames:
            row = self._tool_row_frames[name]
            if hasattr(row, "_has_update_btn"): return
            row._has_update_btn = True
            
            btn_upd = ctk.CTkButton(row, text=f"🔴 อัปเดต ({latest_tag})", width=80, fg_color="#f38ba8", hover_color="#eba0ac", text_color="#1e1e2e", font=ctk.CTkFont(weight="bold"), command=lambda: self.show_github_versions(name, github_repo))
            btn_upd.grid(row=0, column=99, padx=5, pady=5)

    def toggle_favorite(self, tool_name):
        favs = self.config.setdefault("favorite_tools", [])
        if tool_name in favs:
            favs.remove(tool_name)
        else:
            favs.append(tool_name)
        self.save_local_config()
        self.show_tool_library()

    def add_custom_tool_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Custom Tool")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()
        
        ctk.CTkLabel(dialog, text="Tool Name:").pack(pady=(20, 0), padx=20, anchor="w")
        name_entry = ctk.CTkEntry(dialog, width=360)
        name_entry.pack(pady=5, padx=20)
        
        ctk.CTkLabel(dialog, text="Description:").pack(pady=(10, 0), padx=20, anchor="w")
        desc_entry = ctk.CTkEntry(dialog, width=360)
        desc_entry.pack(pady=5, padx=20)
        
        ctk.CTkLabel(dialog, text="Path to .exe:").pack(pady=(10, 0), padx=20, anchor="w")
        path_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        path_frame.pack(fill="x", padx=20, pady=5)
        path_entry = ctk.CTkEntry(path_frame, width=280)
        path_entry.pack(side="left", padx=(0, 10))
        btn_browse = ctk.CTkButton(path_frame, text="Browse", width=70, command=lambda: path_entry.insert(0, filedialog.askopenfilename(filetypes=[("Executable", "*.exe"), ("All", "*.*")])))
        btn_browse.pack(side="left")
        
        def save_custom():
            t_name = name_entry.get().strip()
            t_desc = desc_entry.get().strip()
            t_path = path_entry.get().strip()
            
            if t_name and t_path:
                custom_tools = self.config.setdefault("custom_tools", [])
                custom_tools.append({"name": t_name, "desc": t_desc})
                
                tools_dict = self.config.setdefault("tools", {})
                tools_dict[t_name] = t_path
                
                self.save_local_config()
                dialog.destroy()
                self.show_tool_library()
                
        btn_save = ctk.CTkButton(dialog, text="Save Tool", fg_color="#a6e3a1", text_color="#1e1e2e", hover_color="#94e2d5", font=ctk.CTkFont(weight="bold"), command=save_custom)
        btn_save.pack(pady=20)

    def uninstall_tool(self, tool_name):
        tool_data = self.config.get("tools", {}).get(tool_name)
        if not tool_data: return
        
        active_version = ""
        versions = {}
        is_dict = isinstance(tool_data, dict)
        
        if is_dict:
            active_version = tool_data.get("active_version", "")
            versions = tool_data.get("versions", {})
            tool_path = versions.get(active_version, "")
        else:
            tool_path = tool_data
            active_version = "custom"
            
        if not tool_path: return
        
        if messagebox.askyesno("Uninstall", f"Are you sure you want to uninstall {tool_name} ({active_version})?", parent=self):
            tools_base = os.path.join(os.path.dirname(__file__), "Tools")
            # Check if the tool_path is actually inside our Tools directory
            if os.path.normcase(tool_path).startswith(os.path.normcase(tools_base)):
                tool_folder = os.path.join(tools_base, tool_name.replace(" ", "_"))
                if active_version and active_version != "custom":
                    ver_folder = os.path.join(tool_folder, active_version)
                    if os.path.exists(ver_folder):
                        try:
                            import shutil
                            shutil.rmtree(ver_folder)
                        except Exception as e:
                            messagebox.showerror("Error", f"Could not delete files: {e}", parent=self)
                            return
                else:
                    if os.path.exists(tool_folder):
                        try:
                            import shutil
                            shutil.rmtree(tool_folder)
                        except Exception as e:
                            messagebox.showerror("Error", f"Could not delete files: {e}", parent=self)
                            return
                            
            # Update config
            if is_dict:
                if active_version in versions:
                    del versions[active_version]
                if versions:
                    self.config["tools"][tool_name]["active_version"] = list(versions.keys())[0]
                else:
                    del self.config["tools"][tool_name]
            else:
                del self.config["tools"][tool_name]
                
            self.save_local_config()
            self.show_tool_library()
            messagebox.showinfo("Success", f"{tool_name} uninstalled successfully.", parent=self)

    def delete_custom_tool(self, tool_name):
        custom_tools = self.config.get("custom_tools", [])
        self.config["custom_tools"] = [t for t in custom_tools if t["name"] != tool_name]
        
        if "tools" in self.config and tool_name in self.config["tools"]:
            del self.config["tools"][tool_name]
            
        favs = self.config.get("favorite_tools", [])
        if tool_name in favs:
            favs.remove(tool_name)
            
        self.save_local_config()
        self.show_tool_library()

    def link_tool(self, tool_name):
        tools_dict = self.config.setdefault("tools", {})
        filepath = filedialog.askopenfilename(title=f"Select executable for {tool_name}", filetypes=[("Executable Files", "*.exe"), ("Batch Files", "*.bat"), ("All Files", "*.*")])
        if filepath:
            tools_dict[tool_name] = filepath
            self.save_local_config()
            self.show_tool_library() # Refresh UI

    def launch_linked_tool(self, path, target_path=None):
        try:
            # Resolve relative paths against the directory containing main.py (or _internal in PyInstaller)
            abs_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), path))
            
            cmd = []
            if abs_path.lower().endswith(".py"):
                import sys
                cmd.append(sys.executable)
            cmd.append(abs_path)
            
            if target_path:
                cmd.append(target_path)
                
            subprocess.Popen(cmd, cwd=os.path.dirname(abs_path), creationflags=0x00000008)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch:\n{e}", parent=self)

    # --- 4. Knowledge Base ---
    def show_knowledge(self):
        self.clear_main_frame()
        self.current_kb_lang = "TH"
        self.current_md_file = None
        
        top_bar = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        top_bar.pack(fill="x", padx=30, pady=(30, 10))
        
        lbl_title = ctk.CTkLabel(top_bar, text="📚 Documentation", font=ctk.CTkFont(size=28, weight="bold"))
        lbl_title.pack(side="left")
        
        btn_export = ctk.CTkButton(top_bar, text=_("🌐 อ่านบนบราว์เซอร์ (Printable)"), font=ctk.CTkFont(weight="bold"), fg_color="#89b4fa", hover_color="#b4befe", text_color="#1e1e2e", command=self.open_in_browser)
        btn_export.pack(side="right", padx=(10, 0))
        
        lang_seg = ctk.CTkSegmentedButton(top_bar, values=["TH", "EN"], command=self.change_kb_lang)
        lang_seg.set("TH")
        lang_seg.pack(side="right")
        
        # Split into left (tree) and right (preview)
        content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        
        # Left sidebar for files
        self.tree_frame = ctk.CTkScrollableFrame(content_frame, width=300)
        self.tree_frame.pack(side="left", fill="y", padx=(0, 20))
        
        # Right textbox for markdown
        self.textbox = ctk.CTkTextbox(content_frame, wrap="word", font=ctk.CTkFont(family="Segoe UI", size=14))
        self.textbox.pack(side="left", fill="both", expand=True)
        
        # Setup Markdown tags
        self.textbox._textbox.tag_config("h1", font=("Segoe UI", 24, "bold"), foreground="#89b4fa", spacing1=10, spacing3=10)
        self.textbox._textbox.tag_config("h2", font=("Segoe UI", 20, "bold"), foreground="#a6e3a1", spacing1=8, spacing3=8)
        self.textbox._textbox.tag_config("h3", font=("Segoe UI", 16, "bold"), foreground="#cba6f7", spacing1=5, spacing3=5)
        self.textbox._textbox.tag_config("bold", font=("Segoe UI", 14, "bold"))
        self.textbox._textbox.tag_config("list", lmargin1=20, lmargin2=35)
        self.textbox._textbox.tag_config("code", font=("Consolas", 13), background="#181825", foreground="#a6adc8")
        
        self.build_kb_tree()

    def change_kb_lang(self, lang):
        self.current_kb_lang = lang
        self.build_kb_tree()

    def build_kb_tree(self):
        for widget in self.tree_frame.winfo_children():
            widget.destroy()
            
        target_dir = os.path.join(KNOWLEDGE_DIR, self.current_kb_lang)
        
        if not os.path.exists(target_dir):
            ctk.CTkLabel(self.tree_frame, text="No files found.").pack(pady=20)
            self.textbox.configure(state="normal")
            self.textbox.delete("0.0", "end")
            self.textbox.configure(state="disabled")
            self.current_md_file = None
            return
            
        first_file = None
        category_map = {
            "0_Getting_Started": _("🚀 เริ่มต้นการแปลเกม"),
            "1_Engine_Hacking": _("⚙️ เทคนิคเจาะเอนจิน"),
            "2_General_Modding": _("🛠️ เทคนิคพื้นฐานทั่วไป"),
            "3_Game_Guides": _("🎮 คู่มือรายเกม")
        }
        drawn_folders = set()
        
        for root, dirs, files in os.walk(target_dir):
            md_files = [f for f in files if f.endswith('.md')]
            
            rel_path = os.path.relpath(root, target_dir)
            if rel_path != ".":
                parts = rel_path.split(os.sep)
                current_path = ""
                for i, part in enumerate(parts):
                    current_path = os.path.join(current_path, part) if current_path else part
                    if current_path not in drawn_folders:
                        drawn_folders.add(current_path)
                        display_name = category_map.get(part, part)
                        indent = i * 15
                        
                        if i == 0:
                            cat_lbl = ctk.CTkLabel(self.tree_frame, text=display_name, font=ctk.CTkFont(size=16, weight="bold"), text_color="#f9e2af", anchor="w")
                            cat_lbl.pack(fill="x", pady=(15, 5), padx=(5 + indent, 5))
                        else:
                            cat_lbl = ctk.CTkLabel(self.tree_frame, text="▪ " + display_name.replace("_", " "), font=ctk.CTkFont(weight="bold"), text_color="#89b4fa", anchor="w")
                            cat_lbl.pack(fill="x", pady=(5, 2), padx=(5 + indent, 5))
            
            if md_files:
                indent = len(rel_path.split(os.sep)) * 15 if rel_path != "." else 0
                for f in md_files:
                    full_path = os.path.join(root, f)
                    if not first_file: first_file = full_path
                    
                    display_name = f.replace(".md", "").replace("_", " ")
                    btn = ctk.CTkButton(self.tree_frame, text="  📄 " + display_name, anchor="w", fg_color="transparent", text_color="#cdd6f4", hover_color="#45475a")
                    btn.configure(command=lambda p=full_path: self.load_markdown(p))
                    btn.pack(fill="x", pady=1, padx=(5 + indent, 5))
                    
        if first_file:
            # Auto select first
            self.load_markdown(first_file)

    def load_markdown(self, filepath):
        self.current_md_file = filepath
        self.textbox.configure(state="normal")
        self.textbox.delete("0.0", "end")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            in_code_block = False
            for line in lines:
                if line.startswith("```"):
                    in_code_block = not in_code_block
                    continue
                    
                if in_code_block:
                    self.textbox.insert("end", line, "code")
                    continue
                    
                if line.startswith("# "):
                    self.textbox.insert("end", line[2:], "h1")
                elif line.startswith("## "):
                    self.textbox.insert("end", line[3:], "h2")
                elif line.startswith("### "):
                    self.textbox.insert("end", line[4:], "h3")
                elif line.startswith("- ") or line.startswith("* "):
                    self.textbox.insert("end", line, "list")
                else:
                    # Simple bold parsing (only one per line supported for simplicity)
                    import re
                    bold_match = re.search(r'\*\*(.*?)\*\*', line)
                    if bold_match:
                        start = bold_match.start()
                        end = bold_match.end()
                        self.textbox.insert("end", line[:start])
                        self.textbox.insert("end", bold_match.group(1), "bold")
                        self.textbox.insert("end", line[end:])
                    else:
                        self.textbox.insert("end", line)
                        
        except Exception as e:
            self.textbox.insert("end", f"Error loading file: {e}")
            
        self.textbox.configure(state="disabled")

    def open_in_browser(self):
        if not hasattr(self, 'current_md_file') or not self.current_md_file:
            messagebox.showwarning("Error", "Please select a file to read.", parent=self)
            return
            
        try:
            with open(self.current_md_file, 'r', encoding='utf-8') as f:
                md_text = f.read()
                
            html_body = markdown.markdown(md_text, extensions=['fenced_code', 'tables', 'nl2br'])
            
            # Simple GitHub-like CSS
            css = """
            <style>
                body { font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif; line-height: 1.6; color: #24292f; background-color: #ffffff; padding: 40px; max-width: 900px; margin: 0 auto; }
                h1, h2, h3, h4, h5, h6 { margin-top: 24px; margin-bottom: 16px; font-weight: 600; line-height: 1.25; }
                h1 { font-size: 2em; padding-bottom: .3em; border-bottom: 1px solid #hsla(210,18%,87%,1); }
                h2 { font-size: 1.5em; padding-bottom: .3em; border-bottom: 1px solid #hsla(210,18%,87%,1); }
                a { color: #0969da; text-decoration: none; }
                p, blockquote, ul, ol, dl, table, pre, details { margin-top: 0; margin-bottom: 16px; }
                code { font-family: ui-monospace,SFMono-Regular,SF Mono,Menlo,Consolas,Liberation Mono,monospace; font-size: 85%; padding: .2em .4em; margin: 0; background-color: rgba(175,184,193,0.2); border-radius: 6px; }
                pre { padding: 16px; overflow: auto; line-height: 1.45; background-color: #f6f8fa; border-radius: 6px; }
                pre code { padding: 0; margin: 0; background-color: transparent; }
                table { border-spacing: 0; border-collapse: collapse; display: block; width: max-content; max-width: 100%; overflow: auto; }
                table th, table td { padding: 6px 13px; border: 1px solid #d0d7de; }
                table tr:nth-child(2n) { background-color: #f6f8fa; }
                blockquote { padding: 0 1em; color: #57606a; border-left: .25em solid #d0d7de; }
                @media print { body { padding: 0; max-width: none; } }
            </style>
            """
            
            title = os.path.basename(self.current_md_file)
            full_html = f"<!DOCTYPE html><html><head><meta charset='utf-8'><title>{title}</title>{css}</head><body>{html_body}</body></html>"
            
            temp_file = os.path.join(tempfile.gettempdir(), f"thub_guide_{title}.html")
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(full_html)
                
            webbrowser.open("file:///" + temp_file.replace('\\', '/'))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate and open HTML:\n{e}", parent=self)

    # --- 5. About / Credits ---
    def show_about(self):
        self.clear_main_frame()
        
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 10))
        
        lbl_title = ctk.CTkLabel(header_frame, text="About THub", font=ctk.CTkFont(size=28, weight="bold"))
        lbl_title.pack(side="left")
        
        content_frame = ctk.CTkFrame(self.main_frame, corner_radius=15, fg_color="#1e1e2e", border_width=1, border_color="#45475a")
        content_frame.pack(fill="both", expand=True, padx=40, pady=30)
        
        # Creator Section
        lbl_creator_head = ctk.CTkLabel(content_frame, text="Creator & Lead Developer", font=ctk.CTkFont(size=16), text_color="gray")
        lbl_creator_head.pack(pady=(60, 5))
        
        lbl_name = ctk.CTkLabel(content_frame, text=_("หน๊ด หนวด translator"), font=ctk.CTkFont(size=42, weight="bold"), text_color="#cba6f7")
        lbl_name.pack(pady=0)
        
        lbl_desc = ctk.CTkLabel(content_frame, text="The Ultimate Game Localization & Modding Hub", font=ctk.CTkFont(size=18), text_color="#a6e3a1")
        lbl_desc.pack(pady=(10, 20))
        
        # Social Links
        btn_github = ctk.CTkButton(content_frame, text="⭐ GitHub Profile", fg_color="#313244", hover_color="#45475a", text_color="#cdd6f4", font=ctk.CTkFont(weight="bold"), command=lambda: webbrowser.open("https://github.com/memolyviza2012-max"))
        btn_github.pack(pady=5)
        
        btn_fb = ctk.CTkButton(content_frame, text="📘 Facebook Page", fg_color="#1877F2", hover_color="#166FE5", font=ctk.CTkFont(weight="bold"), command=lambda: webbrowser.open("https://www.facebook.com/NodNuatTranslator/"))
        btn_fb.pack(pady=5)
        
        btn_discord = ctk.CTkButton(content_frame, text="👾 Discord Server", fg_color="#5865F2", hover_color="#4752C4", font=ctk.CTkFont(weight="bold"), command=lambda: webbrowser.open("https://discord.gg/KnmDYSxnuW"))
        btn_discord.pack(pady=5)
        
        btn_group = ctk.CTkButton(content_frame, text="💬 THub Dev Room", fg_color="#f38ba8", hover_color="#eba0ac", text_color="#1e1e2e", font=ctk.CTkFont(weight="bold"), command=lambda: webbrowser.open("https://www.facebook.com/groups/thubdevroom"))
        btn_group.pack(pady=(5, 30))
        
        # App Info
        info_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        info_frame.pack(pady=10)
        
        ctk.CTkLabel(info_frame, text="License:", font=ctk.CTkFont(weight="bold", size=14)).grid(row=0, column=0, sticky="e", padx=10, pady=5)
        
        btn_license = ctk.CTkButton(info_frame, text="Open Source (GPL License)", fg_color="transparent", text_color="#89b4fa", hover_color="#313244", command=lambda: webbrowser.open("https://www.gnu.org/licenses/gpl-3.0.html"))
        btn_license.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        
        # Additional Links (Website & Donate)
        btn_website = ctk.CTkButton(content_frame, text="🌐 Official Website", fg_color="#11111b", border_width=1, border_color="#89dceb", text_color="#89dceb", hover_color="#313244", font=ctk.CTkFont(size=14, weight="bold"), command=lambda: webbrowser.open("https://nodnuattranslator.vercel.app/"))
        btn_website.pack(pady=(10, 5))
        
        btn_donate = ctk.CTkButton(content_frame, text=_("💖 สนับสนุนการพัฒนาโปรแกรม (Donate)"), fg_color="#11111b", border_width=1, border_color="#f38ba8", text_color="#f38ba8", hover_color="#313244", font=ctk.CTkFont(size=14, weight="bold"), command=lambda: webbrowser.open("https://nodnuattranslator.vercel.app/donate-qr.jpg"))
        btn_donate.pack(pady=5)

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    app = ModderHubApp()
    app.mainloop()
