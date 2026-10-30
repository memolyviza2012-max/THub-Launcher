import os
import customtkinter as ctk
from ui.theme import Theme
from core.knowledge_service import KnowledgeService

class KnowledgeView(ctk.CTkFrame):
    """
    Searchable Modding-Knowledge Viewer.
    Left pane lists categories and guides, right pane displays markdown contents.
    """

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.kb_service = KnowledgeService()
        self.current_guides = self.kb_service.search("")
        self._build_ui()

    def _build_ui(self):
        # 1. Header Banner
        banner = ctk.CTkFrame(self, fg_color=Theme.BG_CARD, corner_radius=12, border_width=1, border_color=Theme.BORDER_SUBTLE)
        banner.pack(fill="x", padx=16, pady=(10, 14))

        b_content = ctk.CTkFrame(banner, fg_color="transparent")
        b_content.pack(fill="x", padx=16, pady=12)

        ctk.CTkLabel(
            b_content,
            text="📚 Modding Knowledge Base",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=18, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        ).pack(anchor="w")

        ctk.CTkLabel(
            b_content,
            text="คลังคู่มือและคัมภีร์โมเกมฉบับเจาะลึก (ค้นหาคำศัพท์ เอนจิ้น หรือเทคนิคสระลอยได้ทันที)",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
            text_color=Theme.TEXT_SECONDARY
        ).pack(anchor="w", pady=(2, 0))

        # 2. Split Frame (Left: Guide List, Right: Reader)
        split = ctk.CTkFrame(self, fg_color="transparent")
        split.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        split.grid_columnconfigure(0, weight=1)
        split.grid_columnconfigure(1, weight=2)
        split.grid_rowconfigure(0, weight=1)

        # ====== LEFT: Guide List & Search ======
        left_panel = ctk.CTkFrame(split, fg_color=Theme.BG_CARD, corner_radius=12, border_width=1, border_color=Theme.BORDER_SUBTLE)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Search Box
        search_box = ctk.CTkEntry(
            left_panel,
            placeholder_text="🔍 ค้นหาคู่มือ...",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12),
            height=32,
            fg_color="#121622",
            border_color=Theme.BORDER_SUBTLE
        )
        search_box.pack(fill="x", padx=12, pady=12)
        search_box.bind("<KeyRelease>", lambda e: self._on_search(search_box.get()))

        # Guides Scrollable List
        self.list_scroll = ctk.CTkScrollableFrame(left_panel, fg_color="transparent")
        self.list_scroll.pack(fill="both", expand=True, padx=8, pady=(0, 12))

        # ====== RIGHT: Reader View ======
        right_panel = ctk.CTkFrame(split, fg_color=Theme.BG_CARD, corner_radius=12, border_width=1, border_color=Theme.BORDER_SUBTLE)
        right_panel.grid(row=0, column=1, sticky="nsew")

        self.lbl_guide_title = ctk.CTkLabel(
            right_panel,
            text="เลือกคู่มือจากรายการด้านซ้ายเพื่อเริ่มอ่าน",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=14, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        )
        self.lbl_guide_title.pack(anchor="w", padx=16, pady=(14, 8))

        self.txt_reader = ctk.CTkTextbox(
            right_panel,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color="#0e121a",
            text_color="#e2e8f0",
            border_width=1,
            border_color=Theme.BORDER_SUBTLE,
            corner_radius=8
        )
        self.txt_reader.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        self._render_guide_list()

    def _on_search(self, query):
        self.current_guides = self.kb_service.search(query)
        self._render_guide_list()

    def _render_guide_list(self):
        for w in self.list_scroll.winfo_children():
            w.destroy()

        if not self.current_guides:
            ctk.CTkLabel(self.list_scroll, text="ไม่พบคู่มือที่ตรงกับคำค้น", text_color=Theme.TEXT_MUTED).pack(pady=20)
            return

        for item in self.current_guides:
            btn = ctk.CTkButton(
                self.list_scroll,
                text=f"📄 {item['title']}",
                anchor="w",
                font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
                fg_color="transparent",
                hover_color=Theme.BG_CARD_HOVER,
                text_color=Theme.TEXT_PRIMARY,
                height=30,
                corner_radius=6,
                command=lambda g=item: self._display_guide(g)
            )
            btn.pack(fill="x", pady=1)

    def _display_guide(self, guide):
        self.lbl_guide_title.configure(text=f"📖 {guide['title']} ({guide['category']})")
        content = self.kb_service.read_markdown(guide["path"])
        self.txt_reader.delete("1.0", "end")
        self.txt_reader.insert("1.0", content)
