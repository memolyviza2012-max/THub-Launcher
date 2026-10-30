import os
import customtkinter as ctk
from ui.theme import Theme
from core.steam_service import SteamService
from core.tool_launcher import ToolLauncher
from core.engine_scanner import EngineScanner

class ProjectCard(ctk.CTkFrame):
    """
    Modern 16:9 Landscape Game Project Card.
    Features:
    - 16:9 widescreen header poster (276x155)
    - Optional Engine badge (DirectX badge omitted)
    - Status pill & title
    - Prominent side-by-side [🚀 TStudio] and [🤖 AI Helper] action buttons
    """

    CARD_WIDTH = 292
    CARD_HEIGHT = 270
    POSTER_WIDTH = 276
    POSTER_HEIGHT = 155

    def __init__(self, parent, project, on_tstudio_click=None, on_ai_click=None, on_select=None):
        super().__init__(
            parent,
            width=self.CARD_WIDTH,
            height=self.CARD_HEIGHT,
            corner_radius=12,
            fg_color=Theme.BG_CARD,
            border_width=1,
            border_color=Theme.BORDER_SUBTLE
        )
        self.project = project
        self.on_tstudio_click = on_tstudio_click
        self.on_ai_click = on_ai_click
        self.on_select = on_select

        self.grid_propagate(False)
        self.pack_propagate(False)

        # Fast engine check (Shallow, no DirectX)
        engine_info = EngineScanner.scan_directory(project.get("game_dir", ""))
        self.badge_text = engine_info.get("badge")
        self.badge_color = engine_info.get("badge_color", Theme.CYAN_TSTUDIO)

        self._build_ui()
        self._bind_hover()

    def _build_ui(self):
        # 1. 16:9 Poster Container
        self.poster_frame = ctk.CTkFrame(self, width=self.POSTER_WIDTH, height=self.POSTER_HEIGHT, fg_color="transparent")
        self.poster_frame.pack(padx=8, pady=(8, 6), fill="x")

        # Load 16:9 Landscape Image
        cover_path = self._get_cover_path()
        img_pil = SteamService.get_rounded_card_image(
            cover_path,
            size=(self.POSTER_WIDTH, self.POSTER_HEIGHT),
            corner_radius=8
        )
        self.poster_img = ctk.CTkImage(light_image=img_pil, size=(self.POSTER_WIDTH, self.POSTER_HEIGHT))
        self.lbl_poster = ctk.CTkLabel(self.poster_frame, text="", image=self.poster_img)
        self.lbl_poster.place(x=0, y=0, relwidth=1, relheight=1)

        # 2. Engine Badge (Only if a real engine like Unreal/Unity/RE is detected - NO DirectX)
        if self.badge_text:
            self.badge_frame = ctk.CTkFrame(
                self.poster_frame,
                corner_radius=6,
                fg_color="#121620",
                border_width=1,
                border_color=self.badge_color
            )
            self.badge_frame.place(relx=0.96, rely=0.06, anchor="ne")

            ctk.CTkLabel(
                self.badge_frame,
                text=f" {self.badge_text} ",
                font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=9, weight="bold"),
                text_color=self.badge_color
            ).pack(padx=4, pady=1)

        # 3. Game Title + Status Row
        info_row = ctk.CTkFrame(self, fg_color="transparent")
        info_row.pack(fill="x", padx=10, pady=(2, 6))

        # Title (Left)
        raw_title = self.project.get("name", "Unknown Game")
        display_title = raw_title if len(raw_title) <= 24 else raw_title[:22] + "..."
        self.lbl_title = ctk.CTkLabel(
            info_row,
            text=display_title,
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=13, weight="bold"),
            text_color=Theme.TEXT_PRIMARY,
            anchor="w"
        )
        self.lbl_title.pack(side="left", fill="x", expand=True)

        # Status Pill (Right)
        status_text = self._get_status_text()
        status_color = self._get_status_color()

        self.pill_frame = ctk.CTkFrame(info_row, fg_color=Theme.BG_PILL, corner_radius=6, height=20)
        self.pill_frame.pack(side="right")

        ctk.CTkLabel(self.pill_frame, text="●", font=ctk.CTkFont(size=9), text_color=status_color).pack(side="left", padx=(5, 2))
        ctk.CTkLabel(
            self.pill_frame,
            text=status_text,
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=10, weight="bold"),
            text_color=Theme.TEXT_SECONDARY
        ).pack(side="left", padx=(0, 6), pady=1)

        # 4. Action Buttons Row: [🚀 TStudio] and [🤖 AI Helper] side-by-side!
        self.action_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.action_bar.pack(fill="x", padx=10, pady=(0, 8))

        # Launch in TStudio Button (Primary Cyan)
        self.btn_tstudio = ctk.CTkButton(
            self.action_bar,
            text="🚀 TStudio",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"),
            fg_color=Theme.CYAN_TSTUDIO,
            hover_color=Theme.CYAN_HOVER,
            text_color="#0b1329",
            height=28,
            corner_radius=6,
            command=self._launch_tstudio
        )
        self.btn_tstudio.pack(side="left", fill="x", expand=True, padx=(0, 4))

        # AI Helper Button (Spotlight Violet side-by-side with TStudio!)
        self.btn_ai = ctk.CTkButton(
            self.action_bar,
            text="🤖 AI Helper",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"),
            fg_color="#2b1f42",
            hover_color="#3e2a63",
            text_color=Theme.VIOLET_AI,
            border_width=1,
            border_color=Theme.VIOLET_AI,
            height=28,
            corner_radius=6,
            command=self._open_ai
        )
        self.btn_ai.pack(side="left", fill="x", expand=True, padx=(0, 4))

        # Open Folder Button
        self.btn_folder = ctk.CTkButton(
            self.action_bar,
            text="📁",
            font=ctk.CTkFont(size=12),
            fg_color="#1c2233",
            hover_color="#28324d",
            text_color=Theme.TEXT_SECONDARY,
            width=32,
            height=28,
            corner_radius=6,
            command=self._open_folder
        )
        self.btn_folder.pack(side="right")

    def _get_cover_path(self):
        p_path = self.project.get("path", "")
        candidates = [
            os.path.join(p_path, "thub_cover.jpg"),
            os.path.join(p_path, "cover.jpg"),
            os.path.join(p_path, "thub_cover.png")
        ]
        for c in candidates:
            if os.path.exists(c):
                return c
        return None

    def _get_status_text(self):
        progress = self.project.get("progress", {})
        pct = progress.get("percentage")
        if pct is not None:
            return f"{pct}%"
        status = self.project.get("status", "In Progress")
        if status == "Completed":
            return "100%"
        elif status == "Imported":
            return "พร้อม"
        return "กำลังแปล"

    def _get_status_color(self):
        progress = self.project.get("progress", {})
        pct = progress.get("percentage", 0)
        if pct >= 100:
            return Theme.GREEN_SUCCESS
        elif pct > 0:
            return Theme.CYAN_TSTUDIO
        return Theme.AMBER_WARN

    def _bind_hover(self):
        for w in [self, self.lbl_title]:
            w.bind("<Enter>", self._on_enter)
            w.bind("<Leave>", self._on_leave)
            w.bind("<Button-1>", self._on_card_click)

    def _on_enter(self, e=None):
        self.configure(fg_color=Theme.BG_CARD_HOVER, border_color=Theme.BORDER_HOVER)

    def _on_leave(self, e=None):
        self.configure(fg_color=Theme.BG_CARD, border_color=Theme.BORDER_SUBTLE)

    def _on_card_click(self, e=None):
        if self.on_select:
            self.on_select(self.project)

    def _launch_tstudio(self):
        p_path = self.project.get("path")
        if self.on_tstudio_click:
            self.on_tstudio_click(self.project)
        else:
            ToolLauncher.launch_tstudio_for_project(p_path)

    def _open_ai(self):
        if self.on_ai_click:
            self.on_ai_click(self.project)

    def _open_folder(self):
        p_path = self.project.get("path")
        if p_path:
            ToolLauncher.open_folder(p_path)
