import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from ui.theme import Theme
from core.project_service import ProjectService
from core.steam_service import SteamService
from core.engine_scanner import EngineScanner

class ProjectWizardDialog(ctk.CTkToplevel):
    """
    Modern Wizard Dialog for creating or importing a modding project.
    Automatically detects game engine and downloads Steam vertical poster.
    """

    def __init__(self, parent, is_import_mode=False, on_created=None):
        super().__init__(parent)
        self.is_import_mode = is_import_mode
        self.on_created = on_created
        self.project_service = ProjectService()

        self.title("เพิ่มโปรเจกต์ม็อดใหม่" if not is_import_mode else "นำเข้าโปรเจกต์ม็อด")
        self.geometry("620x640")
        self.configure(fg_color=Theme.BG_CANVAS)
        self.resizable(False, False)

        # Make modal
        self.transient(parent)
        self.grab_set()

        self._build_ui()

    def _build_ui(self):
        main_frame = ctk.CTkFrame(self, fg_color=Theme.BG_CARD, corner_radius=14, border_width=1, border_color=Theme.BORDER_SUBTLE)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Header
        ctk.CTkLabel(
            main_frame,
            text="✨ สร้างโปรเจกต์ใหม่ (Standard Workspace)" if not self.is_import_mode else "📂 นำเข้าโปรเจกต์เดิม",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=16, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        ).pack(anchor="w", padx=24, pady=(20, 4))

        ctk.CTkLabel(
            main_frame,
            text="ระบบจะสร้างโฟลเดอร์ทำงาน 01–06 ตามมาตรฐาน THub และสแกนหา Engine อัตโนมัติ",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
            text_color=Theme.TEXT_SECONDARY
        ).pack(anchor="w", padx=24, pady=(0, 16))

        # Form Fields
        form = ctk.CTkFrame(main_frame, fg_color="transparent")
        form.pack(fill="x", padx=24, pady=0)

        # 1. Game Name
        ctk.CTkLabel(form, text="ชื่อเกม / โปรเจกต์ *", font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"), text_color=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(0, 2))
        self.ent_name = ctk.CTkEntry(form, placeholder_text="เช่น The Witcher 3, Atelier Ryza...", height=34, fg_color="#121622", border_color=Theme.BORDER_SUBTLE)
        self.ent_name.pack(fill="x", pady=(0, 12))

        # 2. Workspace Path
        ctk.CTkLabel(form, text="โฟลเดอร์จัดเก็บโปรเจกต์ (Workspace) *", font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"), text_color=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(0, 2))
        ws_row = ctk.CTkFrame(form, fg_color="transparent")
        ws_row.pack(fill="x", pady=(0, 12))

        self.ent_ws = ctk.CTkEntry(ws_row, placeholder_text="เลือกโฟลเดอร์สำหรับสร้างพื้นที่ทำงาน 01-06...", height=34, fg_color="#121622", border_color=Theme.BORDER_SUBTLE)
        self.ent_ws.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(ws_row, text="📂 เลือก", width=70, height=34, fg_color="#2b344d", hover_color="#3a4768", command=self._browse_workspace).pack(side="right")

        # 3. Game Install Directory
        ctk.CTkLabel(form, text="ตำแหน่งติดตั้งเกม (Game Directory - ไม่บังคับ)", font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"), text_color=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(0, 2))
        game_row = ctk.CTkFrame(form, fg_color="transparent")
        game_row.pack(fill="x", pady=(0, 12))

        self.ent_game = ctk.CTkEntry(game_row, placeholder_text="โฟลเดอร์เกมใน Steam / Epic (ใช้สำหรับสแกน Engine)...", height=34, fg_color="#121622", border_color=Theme.BORDER_SUBTLE)
        self.ent_game.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(game_row, text="📂 เลือก", width=70, height=34, fg_color="#2b344d", hover_color="#3a4768", command=self._browse_game_dir).pack(side="right")

        # 4. Languages
        lang_row = ctk.CTkFrame(form, fg_color="transparent")
        lang_row.pack(fill="x", pady=(0, 12))
        lang_row.grid_columnconfigure((0, 1), weight=1)

        src_frame = ctk.CTkFrame(lang_row, fg_color="transparent")
        src_frame.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkLabel(src_frame, text="ภาษาต้นฉบับ:", font=ctk.CTkFont(size=11, weight="bold"), text_color=Theme.TEXT_PRIMARY).pack(anchor="w")
        self.cbo_src = ctk.CTkComboBox(src_frame, values=["English", "Japanese", "Chinese", "Korean"], height=32, fg_color="#121622")
        self.cbo_src.set("English")
        self.cbo_src.pack(fill="x", pady=(2, 0))

        tgt_frame = ctk.CTkFrame(lang_row, fg_color="transparent")
        tgt_frame.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        ctk.CTkLabel(tgt_frame, text="ภาษาเป้าหมาย:", font=ctk.CTkFont(size=11, weight="bold"), text_color=Theme.TEXT_PRIMARY).pack(anchor="w")
        self.cbo_tgt = ctk.CTkComboBox(tgt_frame, values=["Thai", "English", "Japanese"], height=32, fg_color="#121622")
        self.cbo_tgt.set("Thai")
        self.cbo_tgt.pack(fill="x", pady=(2, 0))

        # 5. Author Name
        ctk.CTkLabel(form, text="ชื่อผู้แปล / ทีมพัฒนา:", font=ctk.CTkFont(size=11, weight="bold"), text_color=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(0, 2))
        self.ent_author = ctk.CTkEntry(form, placeholder_text="ชื่อผู้แปลหลัก", height=34, fg_color="#121622", border_color=Theme.BORDER_SUBTLE)
        self.ent_author.insert(0, "หน๊ด หนวด translator")
        self.ent_author.pack(fill="x", pady=(0, 20))

        # Bottom Actions
        actions = ctk.CTkFrame(main_frame, fg_color="transparent")
        actions.pack(fill="x", side="bottom", padx=24, pady=20)

        ctk.CTkButton(
            actions,
            text="ยกเลิก",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12),
            fg_color="#1f2638",
            hover_color="#2b344d",
            text_color=Theme.TEXT_SECONDARY,
            height=36,
            width=90,
            command=self.destroy
        ).pack(side="left")

        ctk.CTkButton(
            actions,
            text="🚀 สร้างและเริ่มโปรเจกต์",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12, weight="bold"),
            fg_color=Theme.GREEN_SUCCESS,
            hover_color=Theme.GREEN_HOVER,
            text_color="#0b1a11",
            height=36,
            command=self._submit
        ).pack(side="right")

    def _browse_workspace(self):
        path = filedialog.askdirectory(title="เลือกโฟลเดอร์สำหรับ Workspace", parent=self)
        if path:
            self.ent_ws.delete(0, "end")
            self.ent_ws.insert(0, path)
            if not self.ent_name.get().strip():
                self.ent_name.insert(0, os.path.basename(path))

    def _browse_game_dir(self):
        path = filedialog.askdirectory(title="เลือกโฟลเดอร์ติดตั้งเกม", parent=self)
        if path:
            self.ent_game.delete(0, "end")
            self.ent_game.insert(0, path)

    def _submit(self):
        name = self.ent_name.get().strip()
        ws_path = self.ent_ws.get().strip()
        game_path = self.ent_game.get().strip()

        if not name or not ws_path:
            messagebox.showerror("Error", "กรุณาระบุชื่อโปรเจกต์และตำแหน่งจัดเก็บ!", parent=self)
            return

        try:
            proj = self.project_service.create_project(
                name=name,
                workspace_path=ws_path,
                game_dir=game_path,
                source_lang=self.cbo_src.get(),
                target_lang=self.cbo_tgt.get(),
                author=self.ent_author.get().strip()
            )

            # Auto-download Steam vertical poster
            cover_dest = os.path.join(ws_path, "thub_cover.jpg")
            SteamService.fetch_vertical_capsule(name, cover_dest)

            if self.on_created:
                self.on_created(proj)

            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"สร้างโปรเจกต์ล้มเหลว: {e}", parent=self)
