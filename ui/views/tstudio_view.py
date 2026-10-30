import os
import customtkinter as ctk
from tkinter import messagebox
from ui.theme import Theme
from core.tool_launcher import ToolLauncher
from core.project_service import ProjectService

class TStudioView(ctk.CTkFrame):
    """
    Spotlight Feature 2: TStudio Command Center.
    Direct integration hub for TStudio: translation metrics, quick workspace file explorer, and launch controls.
    """

    def __init__(self, parent, projects=None, active_project=None):
        super().__init__(parent, fg_color="transparent")
        self.projects = projects or []
        self.active_project = active_project or (self.projects[0] if self.projects else None)
        self.project_service = ProjectService()

        self._build_ui()
        if self.active_project:
            self._refresh_stats()

    def _build_ui(self):
        # 1. Header Banner
        banner = ctk.CTkFrame(self, fg_color=Theme.BG_CARD, corner_radius=12, border_width=1, border_color=Theme.BORDER_SUBTLE)
        banner.pack(fill="x", padx=16, pady=(10, 14))

        b_content = ctk.CTkFrame(banner, fg_color="transparent")
        b_content.pack(fill="x", padx=16, pady=12)

        ctk.CTkLabel(
            b_content,
            text="📝 TStudio Translation Hub & Workspace",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=18, weight="bold"),
            text_color=Theme.CYAN_TSTUDIO
        ).pack(anchor="w")

        ctk.CTkLabel(
            b_content,
            text="ศูนย์กลางจัดการงานแปลเกม ตรวจนับความคืบหน้าของไฟล์ใน 02_Translation_Workspace และเปิดเข้า TStudio ในคลิกเดียว",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
            text_color=Theme.TEXT_SECONDARY
        ).pack(anchor="w", pady=(2, 0))

        # 2. Project Selector & Hero Actions Bar
        control_bar = ctk.CTkFrame(self, fg_color=Theme.BG_CARD, corner_radius=12, border_width=1, border_color=Theme.BORDER_SUBTLE)
        control_bar.pack(fill="x", padx=16, pady=(0, 14))

        cb_inner = ctk.CTkFrame(control_bar, fg_color="transparent")
        cb_inner.pack(fill="x", padx=14, pady=12)

        # Left: Project Selector
        ctk.CTkLabel(cb_inner, text="🎮 โปรเจกต์:", font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12, weight="bold"), text_color=Theme.TEXT_PRIMARY).pack(side="left", padx=(0, 8))

        proj_names = [p.get("name", "Unknown") for p in self.projects] if self.projects else ["ไม่มีโปรเจกต์"]
        default_val = self.active_project.get("name") if self.active_project else (proj_names[0] if proj_names else "")
        self.cbo_project = ctk.CTkOptionMenu(
            cb_inner,
            values=proj_names,
            command=self._on_project_changed,
            fg_color="#1f2638",
            button_color="#2b344d",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12),
            height=32,
            width=200
        )
        self.cbo_project.set(default_val)
        self.cbo_project.pack(side="left", padx=(0, 20))

        # Right: Launch TStudio (Big Cyan Button) + TRun + Open Folder
        self.btn_open_folder = ctk.CTkButton(
            cb_inner,
            text="📁 โฟลเดอร์งานแปล",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12),
            fg_color="#1e2436",
            hover_color="#2b344d",
            text_color=Theme.TEXT_SECONDARY,
            height=34,
            corner_radius=8,
            command=self._open_translation_folder
        )
        self.btn_open_folder.pack(side="right")

        self.btn_trun = ctk.CTkButton(
            cb_inner,
            text="⚡ รัน TRun Batch",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12, weight="bold"),
            fg_color="#164e2e",
            hover_color="#1e6b3f",
            text_color=Theme.GREEN_SUCCESS,
            height=34,
            corner_radius=8,
            command=self._launch_trun
        )
        self.btn_trun.pack(side="right", padx=8)

        self.btn_launch_tstudio = ctk.CTkButton(
            cb_inner,
            text="🚀 เปิดใน TStudio",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=13, weight="bold"),
            fg_color=Theme.CYAN_TSTUDIO,
            hover_color=Theme.CYAN_HOVER,
            text_color="#0b1329",
            height=34,
            corner_radius=8,
            command=self._launch_tstudio
        )
        self.btn_launch_tstudio.pack(side="right", padx=8)

        # 3. Stat Cards Row (DLSS Swapper-style 4 stat cards)
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.pack(fill="x", padx=16, pady=(0, 14))
        stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Card 1: Percentage
        self.stat_card_1 = self._create_stat_card(stats_frame, 0, "ความคืบหน้าภาพรวม", "0%", Theme.CYAN_TSTUDIO)
        # Card 2: Translated Lines
        self.stat_card_2 = self._create_stat_card(stats_frame, 1, "บรรทัดแปลภาษาไทย", "0 บรรทัด", Theme.GREEN_SUCCESS)
        # Card 3: Total Lines
        self.stat_card_3 = self._create_stat_card(stats_frame, 2, "ข้อความทั้งหมด", "0 บรรทัด", Theme.TEXT_PRIMARY)
        # Card 4: File Count
        self.stat_card_4 = self._create_stat_card(stats_frame, 3, "ไฟล์ข้อความในคลัง", "0 ไฟล์", Theme.VIOLET_AI)

        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(self, height=8, corner_radius=4, fg_color="#1a2030", progress_color=Theme.CYAN_TSTUDIO)
        self.progress_bar.pack(fill="x", padx=16, pady=(0, 14))
        self.progress_bar.set(0.0)

        # 4. Workspace Files List Frame
        files_frame = ctk.CTkFrame(self, fg_color=Theme.BG_CARD, corner_radius=12, border_width=1, border_color=Theme.BORDER_SUBTLE)
        files_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        files_top = ctk.CTkFrame(files_frame, fg_color="transparent")
        files_top.pack(fill="x", padx=14, pady=(12, 6))

        ctk.CTkLabel(
            files_top,
            text="📑 รายการไฟล์ใน 02_Translation_Workspace:",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=13, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        ).pack(side="left")

        self.btn_refresh = ctk.CTkButton(
            files_top,
            text="🔄 รีเฟรช",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
            fg_color="#1f2638",
            hover_color="#2b344d",
            text_color=Theme.TEXT_SECONDARY,
            height=26,
            width=70,
            command=self._refresh_stats
        )
        self.btn_refresh.pack(side="right")

        self.files_scroll = ctk.CTkScrollableFrame(files_frame, fg_color="transparent")
        self.files_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _create_stat_card(self, parent, col, title, value, val_color):
        card = ctk.CTkFrame(parent, fg_color=Theme.BG_CARD, corner_radius=10, border_width=1, border_color=Theme.BORDER_SUBTLE)
        card.grid(row=0, column=col, padx=4, sticky="ew")

        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=10), text_color=Theme.TEXT_MUTED).pack(anchor="w", padx=12, pady=(10, 2))
        lbl_val = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=18, weight="bold"), text_color=val_color)
        lbl_val.pack(anchor="w", padx=12, pady=(0, 10))
        return lbl_val

    def _on_project_changed(self, choice):
        for p in self.projects:
            if p.get("name") == choice:
                self.active_project = p
                self._refresh_stats()
                break

    def _refresh_stats(self):
        if not self.active_project:
            return

        p_path = self.active_project.get("path", "")
        ws_folder = os.path.join(p_path, "02_Translation_Workspace")

        # Refresh file list
        for widget in self.files_scroll.winfo_children():
            widget.destroy()

        if not os.path.exists(ws_folder):
            ctk.CTkLabel(self.files_scroll, text="ไม่พบโฟลเดอร์ 02_Translation_Workspace", text_color=Theme.TEXT_MUTED).pack(pady=20)
        else:
            files_found = []
            for root, _, files in os.walk(ws_folder):
                for f in files:
                    if os.path.splitext(f)[1].lower() in ProjectService.VALID_TEXT_EXTS:
                        full = os.path.join(root, f)
                        size_kb = os.path.getsize(full) / 1024
                        rel = os.path.relpath(full, ws_folder)
                        files_found.append((rel, f"{size_kb:.1f} KB", full))

            if not files_found:
                ctk.CTkLabel(self.files_scroll, text="ยังไม่มีไฟล์ข้อความในโฟลเดอร์ (นำไฟล์ .csv/.json มาวางเพื่อเริ่มแปล)", text_color=Theme.TEXT_MUTED).pack(pady=20)
            else:
                for rel_name, size_str, full_path in files_found:
                    row = ctk.CTkFrame(self.files_scroll, fg_color="#141824", corner_radius=6, height=32)
                    row.pack(fill="x", pady=2)

                    ctk.CTkLabel(row, text="📄", font=ctk.CTkFont(size=12)).pack(side="left", padx=(10, 6))
                    ctk.CTkLabel(row, text=rel_name, font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"), text_color=Theme.TEXT_PRIMARY).pack(side="left")
                    ctk.CTkLabel(row, text=size_str, font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=10), text_color=Theme.TEXT_MUTED).pack(side="right", padx=10)

        # Async progress calculation
        self.project_service.calculate_progress_async(self.active_project, self._on_progress_calculated)

    def _on_progress_calculated(self, res):
        pct = res.get("percentage", 0)
        total = res.get("total_lines", 0)
        trans = res.get("translated_lines", 0)
        f_count = res.get("file_count", 0)

        self.stat_card_1.configure(text=f"{pct}%")
        self.stat_card_2.configure(text=f"{trans:,} บรรทัด")
        self.stat_card_3.configure(text=f"{total:,} บรรทัด")
        self.stat_card_4.configure(text=f"{f_count} ไฟล์")
        self.progress_bar.set(pct / 100.0)

    def _launch_tstudio(self):
        if not self.active_project:
            return
        p_path = self.active_project.get("path")
        try:
            ToolLauncher.launch_tstudio_for_project(p_path)
        except Exception as e:
            messagebox.showerror("Launch Error", f"ไม่สามารถเปิด TStudio ได้:\n{e}")

    def _launch_trun(self):
        if not self.active_project:
            return
        p_path = self.active_project.get("path")
        try:
            ToolLauncher.launch_trun_for_project(p_path)
        except Exception as e:
            messagebox.showerror("Launch Error", f"ไม่สามารถเปิด TRun ได้:\n{e}")

    def _open_translation_folder(self):
        if not self.active_project:
            return
        ws = os.path.join(self.active_project.get("path", ""), "02_Translation_Workspace")
        ToolLauncher.open_folder(ws)

    def set_project(self, project):
        self.active_project = project
        self.cbo_project.set(project.get("name", ""))
        self._refresh_stats()
