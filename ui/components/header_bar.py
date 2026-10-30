import customtkinter as ctk
from ui.theme import Theme

class HeaderBar(ctk.CTkFrame):
    """
    DLSS Swapper-style Header Action Bar.
    Contains Title with counter, search entry, and quick action buttons.
    """

    def __init__(self, parent, title="เกม", total_count=0, on_search=None, on_add=None, on_import=None, on_ai_copilot=None):
        super().__init__(
            parent,
            height=60,
            fg_color="transparent"
        )
        self.total_count = total_count
        self.filtered_count = total_count
        self.section_title = title
        self.on_search = on_search
        self.on_add = on_add
        self.on_import = on_import
        self.on_ai_copilot = on_ai_copilot

        self._build_ui()

    def _build_ui(self):
        # Left: Title + Counter (e.g. "โปรเจกต์ม็อด แสดง 12 จาก 12")
        self.title_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.title_frame.pack(side="left", padx=(10, 20), pady=12)

        self.lbl_main_title = ctk.CTkLabel(
            self.title_frame,
            text=self.section_title,
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=20, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        )
        self.lbl_main_title.pack(side="left")

        self.lbl_counter = ctk.CTkLabel(
            self.title_frame,
            text=f"  แสดง {self.filtered_count} จาก {self.total_count}",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12),
            text_color=Theme.TEXT_MUTED
        )
        self.lbl_counter.pack(side="left", pady=(3, 0))

        # Right: Action Buttons + Search
        right_frame = ctk.CTkFrame(self, fg_color="transparent")
        right_frame.pack(side="right", padx=(0, 10), pady=12)

        # AI Copilot Button (Spotlight Violet)
        self.btn_ai = ctk.CTkButton(
            right_frame,
            text="🤖 AI Copilot",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12, weight="bold"),
            fg_color="#2c1a4d",
            hover_color="#3e236e",
            text_color=Theme.VIOLET_AI,
            border_width=1,
            border_color=Theme.VIOLET_AI,
            corner_radius=8,
            height=32,
            command=self.on_ai_copilot
        )
        self.btn_ai.pack(side="right", padx=(6, 0))

        # Add Project Button (Green / Accent)
        self.btn_add = ctk.CTkButton(
            right_frame,
            text="➕ เพิ่มโปรเจกต์",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12, weight="bold"),
            fg_color=Theme.GREEN_SUCCESS,
            hover_color=Theme.GREEN_HOVER,
            text_color="#091c10",
            corner_radius=8,
            height=32,
            command=self.on_add
        )
        self.btn_add.pack(side="right", padx=(6, 0))

        # Import Project Button
        self.btn_import = ctk.CTkButton(
            right_frame,
            text="📂 นำเข้า",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12),
            fg_color=Theme.BG_CARD,
            hover_color=Theme.BG_CARD_HOVER,
            text_color=Theme.TEXT_SECONDARY,
            border_width=1,
            border_color=Theme.BORDER_SUBTLE,
            corner_radius=8,
            height=32,
            command=self.on_import
        )
        self.btn_import.pack(side="right", padx=(6, 0))

        # Search Entry (DLSS Swapper style)
        self.search_entry = ctk.CTkEntry(
            right_frame,
            placeholder_text="🔍 ค้นหาชื่อเกม, Engine...",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12),
            width=220,
            height=32,
            corner_radius=8,
            fg_color=Theme.BG_CARD,
            border_width=1,
            border_color=Theme.BORDER_SUBTLE,
            text_color=Theme.TEXT_PRIMARY
        )
        self.search_entry.pack(side="right", padx=(0, 6))
        self.search_entry.bind("<KeyRelease>", self._on_search_change)

    def _on_search_change(self, event=None):
        if self.on_search:
            self.on_search(self.search_entry.get().strip())

    def update_counts(self, filtered, total):
        self.filtered_count = filtered
        self.total_count = total
        self.lbl_counter.configure(text=f"  แสดง {filtered} จาก {total}")

    def set_title(self, title):
        self.section_title = title
        self.lbl_main_title.configure(text=title)
