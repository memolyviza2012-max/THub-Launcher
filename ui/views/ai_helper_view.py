import os
import customtkinter as ctk
from tkinter import messagebox
from ui.theme import Theme
from core.engine_scanner import EngineScanner
from core.knowledge_service import KnowledgeService
from ai.prompt_engine import PromptEngine

class AIHelperView(ctk.CTkFrame):
    """
    Spotlight Feature 1: AI Helper Command Center.
    Generates context-aware Master Prompts linked with Modding-Knowledge and Engine Scanners.
    """

    def __init__(self, parent, projects=None, active_project=None):
        super().__init__(parent, fg_color="transparent")
        self.projects = projects or []
        self.active_project = active_project or (self.projects[0] if self.projects else None)
        self.kb_service = KnowledgeService()

        self._build_ui()
        if self.active_project:
            self._update_project_details()

    def _build_ui(self):
        # 1. Header Banner
        banner = ctk.CTkFrame(self, fg_color=Theme.BG_CARD, corner_radius=12, border_width=1, border_color=Theme.BORDER_SUBTLE)
        banner.pack(fill="x", padx=16, pady=(10, 16))

        b_content = ctk.CTkFrame(banner, fg_color="transparent")
        b_content.pack(fill="x", padx=16, pady=12)

        ctk.CTkLabel(
            b_content,
            text="🤖 AI Modding Copilot & Prompt Studio",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=18, weight="bold"),
            text_color=Theme.VIOLET_AI
        ).pack(anchor="w")

        ctk.CTkLabel(
            b_content,
            text="วิเคราะห์เอนจิ้นเกมอัตโนมัติ ผสานคลังความรู้ Modding-Knowledge และสร้าง Master Prompt สำหรับ TStudio",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
            text_color=Theme.TEXT_SECONDARY
        ).pack(anchor="w", pady=(2, 0))

        # 2. Main 2-Column Split
        split_frame = ctk.CTkFrame(self, fg_color="transparent")
        split_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        split_frame.grid_columnconfigure(0, weight=1) # Left config panel
        split_frame.grid_columnconfigure(1, weight=2) # Right prompt output panel
        split_frame.grid_rowconfigure(0, weight=1)

        # ====== LEFT: Project & Mission Config ======
        left_panel = ctk.CTkFrame(split_frame, fg_color=Theme.BG_CARD, corner_radius=12, border_width=1, border_color=Theme.BORDER_SUBTLE)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Project Selector
        ctk.CTkLabel(left_panel, text="🎮 เลือกโปรเจกต์เป้าหมาย:", font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12, weight="bold"), text_color=Theme.TEXT_PRIMARY).pack(anchor="w", padx=14, pady=(14, 4))

        proj_names = [p.get("name", "Unknown") for p in self.projects] if self.projects else ["ไม่มีโปรเจกต์"]
        default_val = self.active_project.get("name") if self.active_project else (proj_names[0] if proj_names else "")
        self.cbo_project = ctk.CTkOptionMenu(
            left_panel,
            values=proj_names,
            command=self._on_project_changed,
            fg_color="#1f2638",
            button_color="#2b344d",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12),
            height=32
        )
        self.cbo_project.set(default_val)
        self.cbo_project.pack(fill="x", padx=14, pady=(0, 12))

        # Engine Detection Status Card
        self.engine_card = ctk.CTkFrame(left_panel, fg_color="#121622", corner_radius=8, border_width=1, border_color=Theme.BORDER_SUBTLE)
        self.engine_card.pack(fill="x", padx=14, pady=(0, 12))

        self.lbl_engine_title = ctk.CTkLabel(self.engine_card, text="⚙️ Game Engine: ตรวจสอบ...", font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12, weight="bold"), text_color=Theme.CYAN_TSTUDIO)
        self.lbl_engine_title.pack(anchor="w", padx=10, pady=(8, 2))

        self.lbl_engine_tools = ctk.CTkLabel(self.engine_card, text="เครื่องมือ: TStudio, TRun", font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=10), text_color=Theme.TEXT_MUTED)
        self.lbl_engine_tools.pack(anchor="w", padx=10, pady=(0, 8))

        # Mission Mode Selector
        ctk.CTkLabel(left_panel, text="🎯 ภารกิจที่ต้องการให้ AI ช่วย:", font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12, weight="bold"), text_color=Theme.TEXT_PRIMARY).pack(anchor="w", padx=14, pady=(4, 4))

        self.mode_var = ctk.StringVar(value="tstudio_bridge")
        modes = [
            ("tstudio_bridge", "📝 แกะไฟล์เกม ➔ TStudio CSV Bridge"),
            ("bible",          "📖 สั่งเขียนคัมภีร์ม็อด (Thai Localization Bible)"),
            ("font_pua",       "🔤 แก้สระลอย / ฟอนต์ภาษาไทย (PUA)"),
            ("dubbing",        "🎙️ พากย์เสียง & ซับไตเติล (TVox)")
        ]

        for val, text in modes:
            rb = ctk.CTkRadioButton(
                left_panel,
                text=text,
                value=val,
                variable=self.mode_var,
                command=self._generate_prompt,
                font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
                text_color=Theme.TEXT_SECONDARY,
                fg_color=Theme.VIOLET_AI,
                hover_color=Theme.VIOLET_HOVER
            )
            rb.pack(anchor="w", padx=14, pady=4)

        # Linked Knowledge Base Guides
        ctk.CTkLabel(left_panel, text="📚 คัมภีร์ที่ตรวจพบในคลังความรู้:", font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12, weight="bold"), text_color=Theme.TEXT_PRIMARY).pack(anchor="w", padx=14, pady=(16, 4))

        self.kb_frame = ctk.CTkFrame(left_panel, fg_color="#121622", corner_radius=8)
        self.kb_frame.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        self.lbl_guides = ctk.CTkLabel(
            self.kb_frame,
            text="กำลังสแกน Modding-Knowledge...",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=10),
            text_color=Theme.TEXT_MUTED,
            justify="left",
            wraplength=220
        )
        self.lbl_guides.pack(anchor="w", padx=10, pady=10)

        # ====== RIGHT: Prompt Preview & Action Controls ======
        right_panel = ctk.CTkFrame(split_frame, fg_color=Theme.BG_CARD, corner_radius=12, border_width=1, border_color=Theme.BORDER_SUBTLE)
        right_panel.grid(row=0, column=1, sticky="nsew")

        # Top Action Bar of Prompt Panel
        prompt_top = ctk.CTkFrame(right_panel, fg_color="transparent")
        prompt_top.pack(fill="x", padx=14, pady=(14, 8))

        ctk.CTkLabel(
            prompt_top,
            text="📜 Generated Master Prompt (พร้อมใช้งานทันที):",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=13, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        ).pack(side="left")

        # Copy Button (Violet Highlight)
        self.btn_copy = ctk.CTkButton(
            prompt_top,
            text="📋 คัดลอก Prompt",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"),
            fg_color=Theme.VIOLET_AI,
            hover_color=Theme.VIOLET_HOVER,
            text_color="#ffffff",
            height=28,
            corner_radius=6,
            command=self._copy_prompt
        )
        self.btn_copy.pack(side="right", padx=(6, 0))

        # Save to Workspace Button
        self.btn_save = ctk.CTkButton(
            prompt_top,
            text="💾 บันทึกไฟล์",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
            fg_color="#232b3d",
            hover_color="#303c54",
            text_color=Theme.TEXT_PRIMARY,
            height=28,
            corner_radius=6,
            command=self._save_prompt_file
        )
        self.btn_save.pack(side="right")

        # Prompt Text Area
        self.txt_prompt = ctk.CTkTextbox(
            right_panel,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color="#0e121a",
            text_color="#e2e8f0",
            border_width=1,
            border_color=Theme.BORDER_SUBTLE,
            corner_radius=8
        )
        self.txt_prompt.pack(fill="both", expand=True, padx=14, pady=(0, 14))

    def _on_project_changed(self, choice):
        for p in self.projects:
            if p.get("name") == choice:
                self.active_project = p
                self._update_project_details()
                break

    def _update_project_details(self):
        if not self.active_project:
            return

        game_dir = self.active_project.get("game_dir", "")
        engine_info = EngineScanner.scan_directory(game_dir)
        engine_name = engine_info.get("engine_name", "Unknown")
        badge = engine_info.get("badge", "DirectX")
        tools = ", ".join(engine_info.get("tools", ["TStudio"]))

        self.lbl_engine_title.configure(text=f"⚙️ {badge} ({engine_name})", text_color=engine_info.get("badge_color", Theme.CYAN_TSTUDIO))
        self.lbl_engine_tools.configure(text=f"เครื่องมือแนะนำ: {tools}")

        # Update Guides
        proj_name = self.active_project.get("name", "")
        guides = self.kb_service.find_guides_for_engine(engine_name, game_title=proj_name, max_results=4)
        if guides:
            guide_lines = []
            for g in guides:
                mtype = g.get("match_type")
                tag = "⭐" if mtype == "game_bible" else ("📘" if mtype == "engine_guide" else "🎮")
                guide_lines.append(f"{tag} {g['title']}")
            self.lbl_guides.configure(text="\n".join(guide_lines), text_color=Theme.CYAN_TSTUDIO)
        else:
            self.lbl_guides.configure(text="ไม่พบเทมเพลตเฉพาะเกม (จะใช้แนวทางวิเคราะห์อัตโนมัติ)", text_color=Theme.TEXT_MUTED)

        self._generate_prompt()

    def _generate_prompt(self):
        if not self.active_project:
            return
        mode = self.mode_var.get()
        prompt_text = PromptEngine.generate_master_prompt(self.active_project, mode=mode)
        self.txt_prompt.delete("1.0", "end")
        self.txt_prompt.insert("1.0", prompt_text)

    def _copy_prompt(self):
        content = self.txt_prompt.get("1.0", "end-1c")
        if content:
            self.clipboard_clear()
            self.clipboard_append(content)
            self.update()
            self.btn_copy.configure(text="✅ คัดลอกสำเร็จ!")
            self.after(1500, lambda: self.btn_copy.configure(text="📋 คัดลอก Prompt"))

    def _save_prompt_file(self):
        if not self.active_project:
            return
        p_path = self.active_project.get("path", "")
        if not p_path or not os.path.exists(p_path):
            messagebox.showerror("Error", "ไม่พบโฟลเดอร์โปรเจกต์!")
            return
        dest_file = os.path.join(p_path, "ai_instructions.md")
        try:
            with open(dest_file, "w", encoding="utf-8") as f:
                f.write(self.txt_prompt.get("1.0", "end-1c"))
            messagebox.showinfo("Success", f"บันทึกไฟล์สำเร็จที่:\n{dest_file}")
        except Exception as e:
            messagebox.showerror("Error", f"บันทึกล้มเหลว: {e}")

    def set_project(self, project):
        self.active_project = project
        self.cbo_project.set(project.get("name", ""))
        self._update_project_details()
