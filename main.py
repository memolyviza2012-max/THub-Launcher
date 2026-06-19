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

# Constants
CURRENT_VERSION = "1.0.1"
UPDATE_FILE_PATH = os.path.join(os.path.dirname(__file__), "updates.json")
CONFIG_FILE = "hub_config.json"
KNOWLEDGE_DIR = os.path.join(os.path.dirname(__file__), "Modding-Knowledge")

TOOL_REGISTRY = {
    "Unreal Engine": [
        {"name": "FModel", "desc": "โปรแกรมเปิดไฟล์ .pak ของ Unreal Engine", "github": "4sval/FModel"},
        {"name": "UnrealPakTool", "desc": "เครื่องมือแพ็ก/แตกไฟล์ .pak", "url": "https://fluffyquack.com/tools/"},
        {"name": "UAssetGUI", "desc": "แก้ไขไฟล์ UAsset ทะลุทะลวง", "github": "atenfyr/UAssetGUI"}
    ],
    "Unity": [
        {"name": "AssetStudio", "desc": "เครื่องมือแกะไฟล์ Unity สุดฮิต", "github": "Perfare/AssetStudio"},
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

class ModderHubApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('flagship.thub.launcher.1.0')
        except:
            pass
            
        self.title("THub Launcher - The Flagship Suite")
        self.geometry("1000x700")
        
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
            self.logo_label = ctk.CTkLabel(self.sidebar_frame, text=" THub Launcher", image=self.hub_img, compound="left", font=ctk.CTkFont(size=20, weight="bold"))
        else:
            self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="THub Launcher", font=ctk.CTkFont(size=22, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 30))

        # Navigation Buttons
        self.btn_home = ctk.CTkButton(self.sidebar_frame, text="🏠 Home", command=self.show_home, anchor="w", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"))
        self.btn_home.grid(row=1, column=0, padx=20, pady=5, sticky="ew")

        self.btn_flagship = ctk.CTkButton(self.sidebar_frame, text="💎 Flagship Products", command=self.show_flagship, anchor="w", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"))
        self.btn_flagship.grid(row=2, column=0, padx=20, pady=5, sticky="ew")

        self.btn_tool = ctk.CTkButton(self.sidebar_frame, text="🧰 Tool Library", command=self.show_tool_library, anchor="w", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"))
        self.btn_tool.grid(row=3, column=0, padx=20, pady=5, sticky="ew")

        self.btn_knowledge = ctk.CTkButton(self.sidebar_frame, text="📚 Knowledge Base", command=self.show_knowledge, anchor="w", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"))
        self.btn_knowledge.grid(row=4, column=0, padx=20, pady=5, sticky="ew")

        self.btn_about = ctk.CTkButton(self.sidebar_frame, text="ℹ️ About Creator", command=self.show_about, anchor="w", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"))
        self.btn_about.grid(row=5, column=0, padx=20, pady=5, sticky="ew")

        # Appearance Mode
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"], command=self.change_appearance_mode)
        self.appearance_mode_optionemenu.set("Dark")
        self.appearance_mode_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 10))
        
        self.update_status_lbl = ctk.CTkLabel(self.sidebar_frame, text="กำลังตรวจสอบอัปเดต...", text_color="gray", font=ctk.CTkFont(size=12))
        self.update_status_lbl.grid(row=9, column=0, padx=20, pady=(0, 20))

        # ====== MAIN FRAME ======
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        # Start at Home
        self.show_home()

        # Check for updates
        self.after(1500, self.check_for_updates)

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
                return config
        return {"tools": {}, "projects": []}

    def save_local_config(self):
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4)

    # --- 1. Home / Dashboard ---
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
        ToolTip(btn_help, "คู่มือใช้งาน")
        
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *args: self._rearrange_project_cards())
        search_entry = ctk.CTkEntry(header_frame, textvariable=self.search_var, placeholder_text="🔍 ค้นหาโปรเจกต์...", width=200)
        search_entry.pack(side="left", padx=(20, 0))
        
        lbl_desc = ctk.CTkLabel(self.main_frame, text="ยินดีต้อนรับสู่ THub Launcher ศูนย์รวมเครื่องมือแปลเกมที่ดีที่สุด", font=ctk.CTkFont(size=14), text_color="gray")
        lbl_desc.pack(anchor="w", padx=30, pady=(0, 20))

    def show_dashboard_help(self):
        help_win = ctk.CTkToplevel(self)
        help_win.title("วิธีใช้งาน Dashboard")
        help_win.geometry("600x500")
        help_win.transient(self)
        help_win.grab_set()
        
        ctk.CTkLabel(help_win, text="คู่มือการใช้งาน Project Dashboard", font=ctk.CTkFont(size=22, weight="bold"), text_color="#89b4fa").pack(pady=(20, 10))
        
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
        
        btn_close = ctk.CTkButton(help_win, text="เข้าใจแล้ว", fg_color="#a6e3a1", text_color="#1e1e2e", hover_color="#94e2d5", font=ctk.CTkFont(weight="bold"), command=help_win.destroy)
        btn_close.pack(pady=20)

        # Active Projects Grid
        self.projects_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        self.projects_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        projects = self.config.get("projects", [])
        self.project_card_widgets = []
        self._current_proj_cols = -1
        
        if not projects:
            ctk.CTkLabel(self.projects_frame, text="ยังไม่มีโปรเจกต์ กด + New Project เพื่อเริ่มต้น!", text_color="gray").grid(row=0, column=0, pady=50)
        else:
            for i, proj in enumerate(projects):
                card = ctk.CTkFrame(self.projects_frame, width=440, height=210, corner_radius=10, fg_color="#1e1e2e", border_width=1, border_color="#45475a")
                card.pack_propagate(False)
                self.project_card_widgets.append((card, proj))
                
                card_top = ctk.CTkFrame(card, fg_color="transparent")
                card_top.pack(fill="x", padx=15, pady=(15, 5))
                
                # Pack right-side buttons first so they don't disappear on resize
                btn_set = ctk.CTkButton(card_top, text="⚙️", width=30, fg_color="transparent", text_color="#94e2d5", hover_color="#313244", command=lambda idx=i: self.set_translation_folder(idx))
                btn_set.pack(side="right")
                
                btn_ren = ctk.CTkButton(card_top, text="✏️", width=30, fg_color="transparent", text_color="#f9e2af", hover_color="#313244", command=lambda idx=i: self.rename_project(idx))
                btn_ren.pack(side="right", padx=(5, 0))
                
                btn_del = ctk.CTkButton(card_top, text="🗑️", width=30, fg_color="transparent", text_color="#f38ba8", hover_color="#313244", command=lambda idx=i: self.delete_project(idx))
                btn_del.pack(side="right", padx=(5, 0))
                
                name_lbl = ctk.CTkLabel(card_top, text=proj.get("name", "Unknown"), font=ctk.CTkFont(size=18, weight="bold"), text_color="#cba6f7", anchor="w")
                name_lbl.pack(side="left", fill="x", expand=True)
                
                path_lbl = ctk.CTkLabel(card, text=proj.get("path", ""), font=ctk.CTkFont(size=12), text_color="gray", anchor="w")
                path_lbl.pack(fill="x", padx=15, pady=0)
                
                # --- PROGRESS SECTION ---
                prog_frame = ctk.CTkFrame(card, fg_color="transparent")
                prog_frame.pack(fill="x", padx=15, pady=(10, 5))
                
                pct_val = proj.get("progress_pct", 0)
                pct_lbl = ctk.CTkLabel(prog_frame, text=f"{pct_val}%", font=ctk.CTkFont(weight="bold"), text_color="#a6e3a1", width=40)
                pct_lbl.pack(side="left")
                
                prog_bar = ctk.CTkProgressBar(prog_frame, progress_color="#a6e3a1")
                prog_bar.pack(side="left", fill="x", expand=True, padx=(5, 10))
                prog_bar.set(pct_val / 100.0)
                
                btn_calc = ctk.CTkButton(prog_frame, text="↻", width=30, fg_color="#313244", hover_color="#45475a", command=lambda idx=i, p=proj.get("path"), plbl=pct_lbl, pbar=prog_bar: self.start_progress_calculation(idx, p, plbl, pbar))
                btn_calc.pack(side="right")
                
                btn_details = ctk.CTkButton(prog_frame, text="📊", width=30, fg_color="#313244", hover_color="#45475a", command=lambda idx=i: self.show_progress_details(idx))
                btn_details.pack(side="right", padx=(0, 5))
                # -------------------------
                
                bottom_frame = ctk.CTkFrame(card, fg_color="transparent")
                bottom_frame.pack(fill="x", padx=15, pady=(5, 15))
                
                btn_open = ctk.CTkButton(bottom_frame, text="📂 Open Folder", fg_color="#89b4fa", text_color="#11111b", hover_color="#b4befe", command=lambda p=proj.get("path"): self.open_project_folder(p))
                btn_open.pack(side="right")
                
            self.projects_frame.bind("<Configure>", self.on_projects_resize)
            self._rearrange_project_cards()

        # Update card removed per user request

    def on_projects_resize(self, event):
        usable_width = event.width - 20
        card_width = 460 # 440 + 20 padding
        cols = max(1, usable_width // card_width)
        
        if self._current_proj_cols != cols:
            self._current_proj_cols = cols
            self._rearrange_project_cards()
            
    def _rearrange_project_cards(self):
        if not hasattr(self, "project_card_widgets"): return
        cols = getattr(self, "_current_proj_cols", 1)
        if cols < 1: cols = 1
        
        query = ""
        if hasattr(self, "search_var"):
            query = self.search_var.get().lower()
            
        for w, p in self.project_card_widgets:
            w.grid_forget()
            
        visible = [w for w, p in self.project_card_widgets if query in p.get("name", "").lower() or query in p.get("path", "").lower()]
        for i, w in enumerate(visible):
            row = i // cols
            col = i % cols
            w.grid(row=row, column=col, padx=10, pady=10, sticky="nw")

    def add_new_project_wizard(self):
        dialog = ctk.CTkInputDialog(text="กรอกชื่อเกม (Game Name):", title="New Project")
        game_name = dialog.get_input()
        
        if game_name:
            base_path = filedialog.askdirectory(title=f"เลือกโฟลเดอร์สำหรับสร้างโปรเจกต์: {game_name}")
            if not base_path:
                return
                
            project_path = os.path.join(base_path, game_name.replace(" ", "_"))
            if os.path.exists(project_path):
                messagebox.showerror("Error", f"มีโปรเจกต์ชื่อนี้อยู่แล้ว:\n{project_path}")
                return
                
            try:
                os.makedirs(project_path)
                os.makedirs(os.path.join(project_path, "01_Original_Backup"))
                os.makedirs(os.path.join(project_path, "02_Translation_Workspace"))
                os.makedirs(os.path.join(project_path, "03_Font_and_UI"))
                os.makedirs(os.path.join(project_path, "04_Packed_Mod"))
                
                self.config.setdefault("projects", []).append({
                    "name": game_name,
                    "path": project_path,
                    "translation_folders": ["02_Translation_Workspace"],
                    "status": "In Progress"
                })
                self.save_local_config()
                self.show_home()
                messagebox.showinfo("Success", f"สร้างโปรเจกต์ {game_name} สำเร็จ!\nโครงสร้างโฟลเดอร์พร้อมใช้งานแล้ว")
            except Exception as e:
                messagebox.showerror("Error", f"สร้างโปรเจกต์ล้มเหลว: {e}")

    def import_project_wizard(self):
        folder_path = filedialog.askdirectory(title="Select Project Folder to Import")
        if not folder_path:
            return
            
        project_name = os.path.basename(folder_path)
        
        # Check if already exists
        for p in self.config.get("projects", []):
            if p.get("path") == folder_path:
                messagebox.showinfo("Info", "โปรเจกต์นี้อยู่ในระบบแล้วครับ!")
                return
                
        try:
            # Create standard folders if they don't exist, WITHOUT touching existing files
            os.makedirs(os.path.join(folder_path, "01_Original_Backup"), exist_ok=True)
            os.makedirs(os.path.join(folder_path, "02_Translation_Workspace"), exist_ok=True)
            os.makedirs(os.path.join(folder_path, "03_Font_and_UI"), exist_ok=True)
            os.makedirs(os.path.join(folder_path, "04_Packed_Mod"), exist_ok=True)
            
            self.config.setdefault("projects", []).append({
                "name": project_name,
                "path": folder_path,
                "status": "Imported"
            })
            self.save_local_config()
            self.show_home()
            messagebox.showinfo("Success", f"นำเข้าโปรเจกต์ {project_name} สำเร็จ!\nระบบได้สร้างโฟลเดอร์มาตรฐานเสริมให้แล้ว (ไฟล์เก่าของคุณยังอยู่ครบครับ)")
        except Exception as e:
            messagebox.showerror("Error", f"นำเข้าโปรเจกต์ล้มเหลว: {e}")

    def rename_project(self, index):
        projects = self.config.get("projects", [])
        if 0 <= index < len(projects):
            old_name = projects[index].get("name", "")
            dialog = ctk.CTkInputDialog(text=f"เปลี่ยนชื่อโปรเจกต์ (เดิม: {old_name}):", title="Rename Project")
            new_name = dialog.get_input()
            if new_name and new_name != old_name:
                projects[index]["name"] = new_name
                self.save_local_config()
                self.show_home()

    def delete_project(self, index):
        projects = self.config.get("projects", [])
        if 0 <= index < len(projects):
            proj_name = projects[index].get("name", "")
            if messagebox.askyesno("Confirm Delete", f"คุณต้องการนำโปรเจกต์ '{proj_name}' ออกจากหน้า Dashboard ใช่หรือไม่?\n\n(ระบบจะไม่ลบโฟลเดอร์และไฟล์จริงของคุณ ข้อมูลทั้งหมดจะยังคงอยู่ในเครื่อง)", parent=self):
                projects.pop(index)
                self.save_local_config()
                self.show_home()

    def set_translation_folder(self, index):
        projects = self.config.get("projects", [])
        if 0 <= index < len(projects):
            proj = projects[index]
            root_path = proj.get("path", "")
            
            # Migration to list
            old_trans = proj.get("translation_folder")
            if "translation_folders" not in proj:
                if isinstance(old_trans, str) and old_trans:
                    proj["translation_folders"] = [old_trans]
                else:
                    proj["translation_folders"] = []
                    
            top = ctk.CTkToplevel(self)
            top.title(f"Manage Translation Folders - {proj.get('name')}")
            top.geometry("500x400")
            top.transient(self)
            top.grab_set()
            
            lbl = ctk.CTkLabel(top, text="เป้าหมายสแกนความคืบหน้า (Multi-Folder)", font=ctk.CTkFont(size=16, weight="bold"))
            lbl.pack(pady=(20, 10))
            
            listbox_frame = ctk.CTkScrollableFrame(top, width=400, height=200)
            listbox_frame.pack(padx=20, pady=10, fill="both", expand=True)
            
            def refresh_list():
                for widget in listbox_frame.winfo_children():
                    widget.destroy()
                
                folders = proj.get("translation_folders", [])
                if not folders:
                    empty_lbl = ctk.CTkLabel(listbox_frame, text="(ยังไม่ได้เลือกโฟลเดอร์ ระบบจะสแกนทั้งโปรเจกต์)", text_color="gray")
                    empty_lbl.pack(pady=20)
                else:
                    for i, f in enumerate(folders):
                        row = ctk.CTkFrame(listbox_frame, fg_color="transparent")
                        row.pack(fill="x", pady=2)
                        
                        disp_name = f if f else "(Root Folder)"
                        f_lbl = ctk.CTkLabel(row, text=f"• {disp_name}", anchor="w")
                        f_lbl.pack(side="left", fill="x", expand=True)
                        
                        btn_del = ctk.CTkButton(row, text="❌", width=30, fg_color="transparent", text_color="#f38ba8", hover_color="#313244", command=lambda idx=i: remove_folder(idx))
                        btn_del.pack(side="right")
                        
            def remove_folder(idx):
                proj["translation_folders"].pop(idx)
                self.save_local_config()
                refresh_list()
                
            def add_folder():
                folder_path = filedialog.askdirectory(title="เลือกโฟลเดอร์แปลภาษา", initialdir=root_path)
                if folder_path:
                    if folder_path.startswith(root_path):
                        rel = os.path.relpath(folder_path, root_path)
                        val = rel if rel != "." else ""
                    else:
                        val = folder_path
                        
                    if val not in proj["translation_folders"]:
                        proj["translation_folders"].append(val)
                        self.save_local_config()
                        refresh_list()
                        
            btn_add = ctk.CTkButton(top, text="➕ Add Folder", command=add_folder, fg_color="#313244", hover_color="#45475a")
            btn_add.pack(pady=(10, 20))
            
            refresh_list()
        projects = self.config.get("projects", [])
        if 0 <= index < len(projects):
            proj = projects[index]
            root_path = proj.get("path", "")
            
            # Show a dialog to pick folder
            folder_path = filedialog.askdirectory(title="เลือกโฟลเดอร์แปลภาษาสำหรับเกมนี้", initialdir=root_path)
            if folder_path:
                if folder_path.startswith(root_path):
                    # Save relative path
                    rel = os.path.relpath(folder_path, root_path)
                    projects[index]["translation_folder"] = rel if rel != "." else ""
                else:
                    # Save absolute path if outside (unlikely but possible)
                    projects[index]["translation_folder"] = folder_path
                self.save_local_config()
                messagebox.showinfo("Success", "บันทึกโฟลเดอร์เป้าหมายสำเร็จ!")

    def start_progress_calculation(self, index, path, pct_lbl, progress_bar):
        if not os.path.exists(path):
            messagebox.showerror("Error", f"ไม่พบโฟลเดอร์โปรเจกต์: {path}")
            return
            
        projects = self.config.get("projects", [])
        proj = projects[index]
        
        # Migration check
        old_trans = proj.get("translation_folder")
        if "translation_folders" not in proj:
            if isinstance(old_trans, str) and old_trans:
                proj["translation_folders"] = [old_trans]
            else:
                proj["translation_folders"] = []
                
        trans_folders = proj.get("translation_folders", [])
        
        scan_paths = []
        if trans_folders:
            for tf in trans_folders:
                p = os.path.join(path, tf) if not os.path.isabs(tf) else tf
                if os.path.exists(p):
                    scan_paths.append(p)
                    
        if not scan_paths:
            # Ask user if they want to map folders
            resp = messagebox.askyesnocancel("ตั้งค่าเป้าหมาย", "คุณยังไม่ได้กำหนด 'โฟลเดอร์แปลภาษา' ให้กับเกมนี้\n\n- กด Yes เพื่อเลือกโฟลเดอร์ (ประหยัดเวลาและแม่นยำ)\n- กด No เพื่อกวาดสแกน 'ทั้งโปรเจกต์' (ใช้เวลานาน)\n- กด Cancel เพื่อยกเลิก")
            if resp is None:
                return # Cancelled
            elif resp is True:
                self.set_translation_folder(index)
                return # Stop scan, let them configure
            else:
                # Proceed with root scan
                scan_paths = [path]
                
        pct_lbl.configure(text="...")
        progress_bar.set(0)
        
        t = threading.Thread(target=self.calculate_translation_progress_worker, args=(index, scan_paths, pct_lbl, progress_bar, path))
        t.daemon = True
        t.start()

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
            sorted_details.insert(0, f"--- สรุปการสแกน ---")
            sorted_details.insert(1, f"โฟลเดอร์เป้าหมาย: {len(scan_paths)} แห่ง")
            sorted_details.insert(2, f"ไฟล์ข้อความที่อ่านสำเร็จ: {scanned_count} ไฟล์")
            sorted_details.insert(3, f"ไฟล์นามสกุลอื่นที่ถูกข้าม: {skipped_count} ไฟล์")
            sorted_details.insert(4, f"-------------------\n")
                
            projects = self.config.get("projects", [])
            if 0 <= index < len(projects):
                projects[index]["progress_pct"] = final_pct
                projects[index]["progress_details"] = sorted_details
                self.save_local_config()
                
            self.after(0, lambda: self._update_progress_ui(pct_lbl, progress_bar, final_pct))
            
        except Exception as e:
            err_msg = f"เกิดข้อผิดพลาดในการสแกน: {e}"
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

    def show_progress_details(self, index):
        projects = self.config.get("projects", [])
        if 0 <= index < len(projects):
            proj = projects[index]
            details = proj.get("progress_details", [])
            name = proj.get("name", "Unknown")
            
            top = ctk.CTkToplevel(self)
            top.title(f"Scan Details - {name}")
            top.geometry("600x450")
            top.transient(self)
            top.grab_set()
            
            lbl = ctk.CTkLabel(top, text=f"File Breakdown: {name}", font=ctk.CTkFont(size=18, weight="bold"))
            lbl.pack(pady=(20, 10))
            
            textbox = ctk.CTkTextbox(top, width=550, height=350, font=ctk.CTkFont(size=12))
            textbox.pack(padx=20, pady=10)
            
            if not details:
                textbox.insert("1.0", "ไม่พบไฟล์ข้อความ หรือยังไม่ได้สแกน\nกรุณากดปุ่ม ↻ บนหน้าการ์ดเพื่อเริ่มสแกน")
            else:
                for line in details:
                    textbox.insert("end", line + "\n")
            textbox.configure(state="disabled")

    def open_project_folder(self, path):
        if os.path.exists(path):
            os.startfile(path)
        else:
            messagebox.showerror("Error", f"ไม่พบโฟลเดอร์: {path}")

    def check_for_updates(self):
        import threading
        threading.Thread(target=self.check_for_updates_bg, daemon=True).start()

    def check_for_updates_bg(self):
        import urllib.request
        import json
        try:
            url = "https://api.github.com/repos/memolyviza2012-max/THub-Launcher/releases/latest"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    tag_name = data.get("tag_name", "v0.0.0")
                    latest_version = tag_name.replace("v", "")
                    body = data.get("body", "ไม่มีข้อมูลอัปเดต")
                    
                    if latest_version > CURRENT_VERSION:
                        # Find download url (look for .zip asset)
                        assets = data.get("assets", [])
                        zip_asset = next((a for a in assets if a["name"].endswith(".zip")), None)
                        if zip_asset:
                            dl_url = "https://ghproxy.net/" + zip_asset["browser_download_url"]
                            self.after(0, self.prompt_update, latest_version, body, dl_url)
                        else:
                            self.after(0, self.update_status, f"มีเวอร์ชันใหม่ (v{latest_version}) แต่ไม่พบไฟล์ .zip", "orange")
                    else:
                        self.after(0, self.update_status, f"คุณใช้งานเวอร์ชันล่าสุดแล้ว (v{CURRENT_VERSION})", "gray")
        except Exception as e:
            print(f"Update check error: {e}")
            self.after(0, self.update_status, "ไม่สามารถตรวจสอบอัปเดตได้ (เครือข่ายมีปัญหา)", "orange")

    def update_status(self, text, color):
        if hasattr(self, 'update_status_lbl') and self.update_status_lbl.winfo_exists():
            self.update_status_lbl.configure(text=text, text_color=color)

    def prompt_update(self, latest_version, notes, dl_url):
        self.update_status(f"มีเวอร์ชันใหม่: v{latest_version} พร้อมอัปเดต!", "green")
        msg = f"มีอัปเดตเวอร์ชันใหม่ (v{latest_version}) บน GitHub!\n\nรายละเอียด:\n{notes}\n\nคุณต้องการอัปเดตเลยหรือไม่? (โปรแกรมจะรีสตาร์ทตัวเอง)"
        if messagebox.askyesno("Update Available", msg, parent=self):
            import threading
            threading.Thread(target=self.perform_self_update_bg, args=(dl_url,), daemon=True).start()

    def perform_self_update_bg(self, dl_url):
        def show_updating_window():
            upd_win = ctk.CTkToplevel(self)
            upd_win.title("Updating")
            upd_win.geometry("400x150")
            upd_win.transient(self)
            upd_win.grab_set()
            ctk.CTkLabel(upd_win, text="กำลังดาวน์โหลดอัปเดต...\nโปรแกรมจะปิดและเปิดใหม่โดยอัตโนมัติเมื่อเสร็จสิ้น", font=ctk.CTkFont(size=14)).pack(pady=40)
            
        self.after(0, show_updating_window)
        import urllib.request
        import zipfile
        import io
        import sys
        import subprocess
        
        try:
            req = urllib.request.Request(dl_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                zip_data = response.read()
                
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
timeout /t 2 /nobreak >nul
xcopy /s /e /y "{temp_dir}\\*" "{current_dir}\\"
rmdir /s /q "{temp_dir}"
start "" "{current_dir}\\{exe_name}"
del "%~f0"
"""
            with open(bat_path, "w", encoding="utf-8") as f:
                f.write(bat_content)
                
            subprocess.Popen([bat_path], shell=True)
            self.after(500, self.destroy) # Close GUI and exit
            
        except Exception as e:
            print(f"Self-update error: {e}")
            self.after(0, lambda: messagebox.showerror("Update Failed", f"เกิดข้อผิดพลาดในการอัปเดต: {e}", parent=self))

    
    # --- 2. Flagship Products ---
    def show_flagship(self):
        self.clear_main_frame()
        
        lbl_title = ctk.CTkLabel(self.main_frame, text="Flagship Products", font=ctk.CTkFont(size=28, weight="bold"))
        lbl_title.pack(anchor="w", padx=30, pady=(20, 10))
        
        # Grid for cards
        self.flagship_grid_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        self.flagship_grid_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        self.flagship_cards = []
        self.current_flagship_cols = 0
        self.main_frame.bind("<Configure>", self._on_flagship_grid_resize, add="+")

        # Loading message
        self._lbl_flagship_loading = ctk.CTkLabel(self.flagship_grid_frame, text="☁️ กำลังซิงค์ข้อมูล Cloud Registry...", text_color="gray", font=ctk.CTkFont(size=14))
        self._lbl_flagship_loading.grid(row=0, column=0, pady=50)

        # Start thread to fetch JSON
        import threading
        threading.Thread(target=self.fetch_flagship_registry_bg, args=(self.flagship_grid_frame,), daemon=True).start()

    def fetch_flagship_registry_bg(self, parent_frame):
        registry_data = [
            {"id": "TStudio", "name": "TStudio", "desc": "สุดยอดเครื่องมือแปลภาษาด้วย AI\n(วิเคราะห์บริบท & แก้ไขแบบ Line-by-Line)\nรองรับการทำงานกับไฟล์ Localization หลายรูปแบบ", "color": "#89b4fa", "exe": "tstudio_app.py", "icon": "assets/TStudio.png"},
            {"id": "TRun", "name": "TRun", "desc": "เครื่องมือแปลภาษาแบบ Batch อัตโนมัติ\n(รองรับไฟล์ขนาดใหญ่และปริมาณมหาศาล)\nแปลทั้งโปรเจกต์ได้อย่างรวดเร็วในคลิกเดียว", "color": "#a6e3a1", "exe": "trun_app.py", "icon": "assets/TRun.png"},
            {"id": "TPUA", "name": "TPUA", "desc": "เครื่องมือจัดการอักขระพิเศษภาษาไทย\n(เข้ารหัส/ถอดรหัส PUA แบบ Drag & Drop)\nแก้ปัญหาสระลอย/จม ในเอนจิ้นเกมต่างๆ", "color": "#cba6f7", "exe": "tpua_app.py", "icon": "assets/TPUA.png"},
            {"id": "TGlyph", "name": "TGlyph", "desc": "เครื่องมือสร้าง Texture ฟอนต์\n(Generate Texture และแผนที่ตัวอักษร)\nสำหรับดัดแปลงฟอนต์ Bitmap ในเกม", "color": "#fab387", "exe": "tglyph_app.py", "icon": "assets/TGlyph.png"},
            {"id": "TVox", "name": "TVox", "desc": "เครื่องมือจัดการ FMV และซับไตเติ้ล\n(วิดีโอเพลเยอร์ & ดึงคลื่นเสียง Waveform)\nออกแบบมาเพื่อการแปลวิดีโอคัทซีนโดยเฉพาะ", "color": "#f38ba8", "exe": "tvox_app.py", "icon": "assets/TVox.png"}
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
        
        exe_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "tools", "flagship", item["id"], item["exe"]))
        
        icon_btn = None
        orig_img = None
        if item.get("icon"):
            try:
                full_logo = os.path.join(os.path.dirname(__file__), item["icon"])
                if os.path.exists(full_logo):
                    orig_img = ctk.CTkImage(light_image=Image.open(full_logo), size=(80, 80))
                    # Use a Button instead of a Label so it's clickable!
                    icon_btn = ctk.CTkButton(card, text="", image=orig_img, fg_color="transparent", hover_color="#313244", width=80, height=80)
                    icon_btn.grid(row=0, column=0, pady=(20, 0))
            except: pass
            
        ctk.CTkLabel(card, text=item["name"], font=ctk.CTkFont(size=20, weight="bold")).grid(row=1, column=0, pady=(15, 5))
        ctk.CTkLabel(card, text=item["desc"], text_color="gray", justify="center").grid(row=2, column=0, pady=(5, 10))
        
        action_frame = ctk.CTkFrame(card, fg_color="transparent")
        action_frame.grid(row=3, column=0, pady=(0, 20))
        
        btn_action = ctk.CTkButton(action_frame, text="🚀 เปิดโปรแกรม", fg_color=item["color"], text_color="#1e1e2e", font=ctk.CTkFont(weight="bold"))
        btn_action.pack(side="left", padx=5)
        
        if icon_btn:
            # Bind the icon button to launch the script with loading animation
            icon_btn.configure(cursor="hand2", command=lambda e=exe_path, b=icon_btn, i=orig_img: self.launch_script_with_loading(e, b, i))
            btn_action.configure(command=lambda e=exe_path, b=icon_btn, i=orig_img: self.launch_script_with_loading(e, b, i))
        else:
            btn_action.configure(command=lambda e=exe_path: self.launch_script(e))
            
        return card
            
    def launch_script_with_loading(self, path, icon_btn, orig_img):
        # Show loading state
        icon_btn.configure(image="", text="⏳\nกำลังโหลด...", font=ctk.CTkFont(size=16, weight="bold"))
        self.update()
        
        # Give UI a tiny bit of time to render the loading state before blocking
        self.after(50, lambda: self._execute_launch(path, icon_btn, orig_img))

    def _execute_launch(self, path, icon_btn, orig_img):
        self.launch_script(path)
        # Revert UI state back to the original icon after a short delay
        self.after(800, lambda: icon_btn.configure(image=orig_img, text=""))

    def launch_script(self, path):
        import subprocess
        import sys
        try:
            if path.endswith(".py"):
                # Use our own THub.exe (sys.executable) to run the .py script!
                subprocess.Popen([sys.executable, path], creationflags=0x00000008, cwd=os.path.dirname(path), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                subprocess.Popen([path], creationflags=0x00000008, cwd=os.path.dirname(path), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            messagebox.showerror("Launch Error", f"ไม่สามารถเปิดโปรแกรมได้:\n{path}\n\nข้อผิดพลาด:\n{e}", parent=self)

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
        
        lbl_desc = ctk.CTkLabel(self.main_frame, text="คลังแสงเครื่องมือม็อดระดับจักรวาล โหลดตรงจากต้นทาง หรือลิงก์ที่มีในเครื่องได้เลย", font=ctk.CTkFont(size=14), text_color="gray")
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
            ctk.CTkLabel(tab_fav, text="ยังไม่มีเครื่องมือโปรด กด ⭐ ที่เครื่องมือเพื่อเพิ่มมาไว้หน้านี้", text_color="gray").pack(pady=20)

    def build_tool_row(self, parent_frame, tool_data, fav_list, is_custom=False, is_fav_tab=False):
        tool_name = tool_data["name"]
        description = tool_data["desc"]
        
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
            btn_site = ctk.CTkButton(row, text="🌐 โหลดเอง", width=80, fg_color="#313244", hover_color="#45475a", command=lambda u=site_url: webbrowser.open(u))
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
            proj_names = ["พ่วงโปรเจกต์: ไม่มี", "พ่วงโปรเจกต์: เลือกโฟลเดอร์..."] + [f"พ่วง: {p['name']}" for p in projects]
            context_var = ctk.StringVar(value="พ่วงโปรเจกต์: ไม่มี")
            
            opt_context = ctk.CTkOptionMenu(row, values=proj_names, variable=context_var, width=150, fg_color="#313244", button_color="#45475a")
            opt_context.grid(row=0, column=col_idx, padx=5, pady=5)
            col_idx += 1
            
            def do_launch(p=tool_path, cvar=context_var):
                cval = cvar.get()
                if cval == "พ่วงโปรเจกต์: ไม่มี":
                    self.launch_linked_tool(p)
                elif cval == "พ่วงโปรเจกต์: เลือกโฟลเดอร์...":
                    folder = filedialog.askdirectory(title="เลือกโฟลเดอร์ที่จะส่งเข้าโปรแกรม")
                    if folder:
                        self.launch_linked_tool(p, folder)
                else:
                    pname = cval.replace("พ่วง: ", "")
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
                btn_cloud = ctk.CTkButton(row, text="☁️ โหลดจาก GitHub", width=130, fg_color="#89b4fa", text_color="#1e1e2e", hover_color="#b4befe", font=ctk.CTkFont(weight="bold"), command=lambda g=tool_data["github"], n=tool_name: self.show_github_versions(n, g))
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
        self.show_tool_category("Unreal Engine", ["Unreal Engine"])
        
        # Start background update checker
        if not hasattr(self, "_update_thread_running") or not self._update_thread_running:
            self._update_thread_running = True
            import threading
            threading.Thread(target=self.check_tool_updates_bg, daemon=True).start()

    def show_tool_category(self, tab_name, categories, is_fav_tab=False):
        self.clear_main_frame()
        
        # Header
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 10))
        
        lbl_title = ctk.CTkLabel(header_frame, text=tab_name, font=ctk.CTkFont(size=28, weight="bold"))
        lbl_title.pack(side="left")
        
        if is_fav_tab:
            lbl_desc = ctk.CTkLabel(self.main_frame, text="เครื่องมือโปรดของคุณ", font=ctk.CTkFont(size=14), text_color="gray")
            lbl_desc.pack(anchor="w", padx=30, pady=(0, 20))
            
            tool_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
            tool_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
            
            fav_list = self.config.get("favorite_tools", [])
            if not fav_list:
                ctk.CTkLabel(tool_frame, text="ยังไม่มีเครื่องมือโปรด กด ⭐ เพื่อเพิ่ม!", text_color="gray").pack(pady=50)
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

        lbl_desc = ctk.CTkLabel(self.main_frame, text=f"รวมเครื่องมือสำหรับ {tab_name}", font=ctk.CTkFont(size=14), text_color="gray")
        lbl_desc.pack(anchor="w", padx=30, pady=(0, 20))
        
        tool_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        tool_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        fav_list = self.config.get("favorite_tools", [])
        
        for cat in categories:
            if cat == "Custom Tools":
                custom_tools = self.config.get("custom_tools", [])
                if not custom_tools:
                    ctk.CTkLabel(tool_frame, text="ยังไม่มีเครื่องมือของคุณ กด + Add Custom Tool เพื่อเพิ่ม!", text_color="gray").pack(pady=50)
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
            if tool_path.startswith(tools_base):
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
            if target_path:
                subprocess.Popen([path, target_path], cwd=os.path.dirname(path), creationflags=0x00000008)
            else:
                subprocess.Popen(path, cwd=os.path.dirname(path), creationflags=0x00000008)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch:\n{e}", parent=self)

    # --- 4. Knowledge Base ---
    def show_knowledge(self):
        self.clear_main_frame()
        self.current_kb_lang = "TH"
        self.current_md_file = None
        
        top_bar = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        top_bar.pack(fill="x", padx=30, pady=(30, 10))
        
        lbl_title = ctk.CTkLabel(top_bar, text="📚 Knowledge Hub", font=ctk.CTkFont(size=28, weight="bold"))
        lbl_title.pack(side="left")
        
        btn_export = ctk.CTkButton(top_bar, text="🌐 อ่านบนบราว์เซอร์ (Printable)", font=ctk.CTkFont(weight="bold"), fg_color="#89b4fa", hover_color="#b4befe", text_color="#1e1e2e", command=self.open_in_browser)
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
            "0_Getting_Started": "🚀 เริ่มต้นการแปลเกม",
            "1_Engine_Hacking": "⚙️ เทคนิคเจาะเอนจิน",
            "2_General_Modding": "🛠️ เทคนิคพื้นฐานทั่วไป",
            "3_Game_Guides": "🎮 คู่มือรายเกม"
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
        
        lbl_name = ctk.CTkLabel(content_frame, text="หน๊ด หนวด translator", font=ctk.CTkFont(size=42, weight="bold"), text_color="#cba6f7")
        lbl_name.pack(pady=0)
        
        lbl_desc = ctk.CTkLabel(content_frame, text="The Ultimate Game Localization & Modding Hub", font=ctk.CTkFont(size=18), text_color="#a6e3a1")
        lbl_desc.pack(pady=(10, 20))
        
        # Social Links
        btn_github = ctk.CTkButton(content_frame, text="⭐ GitHub Profile", fg_color="#313244", hover_color="#45475a", text_color="#cdd6f4", font=ctk.CTkFont(weight="bold"), command=lambda: webbrowser.open("https://github.com/memolyviza2012-max"))
        btn_github.pack(pady=5)
        
        btn_fb = ctk.CTkButton(content_frame, text="📘 Facebook Page", fg_color="#1877F2", hover_color="#166FE5", font=ctk.CTkFont(weight="bold"), command=lambda: webbrowser.open("https://www.facebook.com/NodNuatTranslator/"))
        btn_fb.pack(pady=5)
        
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
        
        btn_donate = ctk.CTkButton(content_frame, text="💖 สนับสนุนการพัฒนาโปรแกรม (Donate)", fg_color="#11111b", border_width=1, border_color="#f38ba8", text_color="#f38ba8", hover_color="#313244", font=ctk.CTkFont(size=14, weight="bold"), command=lambda: webbrowser.open("https://nodnuattranslator.vercel.app/donate-qr.jpg"))
        btn_donate.pack(pady=5)

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    app = ModderHubApp()
    app.mainloop()
