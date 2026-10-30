import os
import customtkinter as ctk
from PIL import Image
from tkinter import messagebox
from ui.theme import Theme
from core.tool_launcher import ToolLauncher

class AppsView(ctk.CTkFrame):
    """
    Flagship Suite Command Center.
    Displays TStudio, TRun, TPUA, TGlyph, and TVox with one-click launch controls.
    """

    def __init__(self, parent, active_project=None):
        super().__init__(parent, fg_color="transparent")
        self.active_project = active_project
        self._build_ui()

    def _build_ui(self):
        # Header Banner
        banner = ctk.CTkFrame(self, fg_color=Theme.BG_CARD, corner_radius=12, border_width=1, border_color=Theme.BORDER_SUBTLE)
        banner.pack(fill="x", padx=16, pady=(10, 16))

        b_content = ctk.CTkFrame(banner, fg_color="transparent")
        b_content.pack(fill="x", padx=16, pady=12)

        ctk.CTkLabel(
            b_content,
            text="✨ The Flagship Suite",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=18, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        ).pack(anchor="w")

        p_name = self.active_project.get("name", "ไม่ได้เลือกโปรเจกต์") if self.active_project else "ไม่ได้เลือกโปรเจกต์"
        ctk.CTkLabel(
            b_content,
            text=f"ชุดเครื่องมือหลักสำหรับโมเกมและแปลภาษา (โปรเจกต์ที่กำลังทำงานด้วย: {p_name})",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
            text_color=Theme.TEXT_SECONDARY
        ).pack(anchor="w", pady=(2, 0))

        # Cards Scroll Area
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        grid = ctk.CTkFrame(scroll, fg_color="transparent")
        grid.pack(fill="both", expand=True)
        grid.grid_columnconfigure((0, 1), weight=1)

        row, col = 0, 0
        for tool_id, tool_info in ToolLauncher.FLAGSHIP_TOOLS.items():
            card = self._create_app_card(grid, tool_id, tool_info)
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            col += 1
            if col >= 2:
                col = 0
                row += 1

    def _create_app_card(self, parent, tool_id, info):
        card = ctk.CTkFrame(parent, fg_color=Theme.BG_CARD, corner_radius=12, border_width=1, border_color=Theme.BORDER_SUBTLE)
        
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=16, pady=16)

        # Header with Color Indicator
        h_frame = ctk.CTkFrame(inner, fg_color="transparent")
        h_frame.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(
            h_frame,
            text=info["name"],
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=16, weight="bold"),
            text_color=info["color"]
        ).pack(side="left")

        if info["supports_project"]:
            badge = ctk.CTkFrame(h_frame, fg_color="#1a2436", corner_radius=4)
            badge.pack(side="right")
            ctk.CTkLabel(badge, text=" พ่วงโปรเจกต์ ", font=ctk.CTkFont(size=10), text_color=Theme.CYAN_TSTUDIO).pack(padx=4, pady=2)

        # Description
        ctk.CTkLabel(
            inner,
            text=info["desc"],
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
            text_color=Theme.TEXT_SECONDARY,
            anchor="w",
            wraplength=350
        ).pack(fill="x", pady=(0, 16))

        # Launch Button
        btn = ctk.CTkButton(
            inner,
            text=f"🚀 เปิด {info['name']}",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12, weight="bold"),
            fg_color=info["color"],
            hover_color=Theme.BG_CARD_HOVER,
            text_color="#0b1329",
            height=32,
            corner_radius=6,
            command=lambda tid=tool_id: self._launch_app(tid)
        )
        btn.pack(fill="x")
        return card

    def _launch_app(self, tool_id):
        p_path = self.active_project.get("path") if self.active_project else None
        try:
            ToolLauncher.launch_flagship(tool_id, project_path=p_path)
        except Exception as e:
            messagebox.showerror("Error", f"เปิดโปรแกรม {tool_id} ล้มเหลว:\n{e}")
