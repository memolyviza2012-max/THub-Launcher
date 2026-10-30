import customtkinter as ctk
from ui.theme import Theme
from ui.components.project_card import ProjectCard

class DashboardView(ctk.CTkFrame):
    """
    Main Unified Dashboard View (16:9 widescreen card grid).
    Combines project workspace overview and instant filter chips.
    """

    CARD_TOTAL_WIDTH = 308
    CARD_TOTAL_HEIGHT = 285

    def __init__(self, parent, projects=None, on_tstudio_click=None, on_ai_click=None, on_select_project=None):
        super().__init__(parent, fg_color="transparent")
        self.all_projects = projects or []
        self.filtered_projects = list(self.all_projects)
        self.on_tstudio_click = on_tstudio_click
        self.on_ai_click = on_ai_click
        self.on_select_project = on_select_project
        self.card_widgets = []
        self.current_cols = 3

        self._build_ui()
        self.bind("<Configure>", self._on_resize)

    def _build_ui(self):
        # 1. Filter Chips Row
        self.filter_frame = ctk.CTkFrame(self, fg_color="transparent", height=36)
        self.filter_frame.pack(fill="x", padx=14, pady=(4, 10))

        self.filter_vars = ["ทั้งหมด", "กำลังแปล", "แปลเสร็จ", "ปักหมุด"]
        self.active_filter = "ทั้งหมด"
        self.filter_buttons = {}

        for f_name in self.filter_vars:
            is_active = (f_name == self.active_filter)
            btn = ctk.CTkButton(
                self.filter_frame,
                text=f_name,
                font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold" if is_active else "normal"),
                fg_color=Theme.CYAN_TSTUDIO if is_active else Theme.BG_CARD,
                text_color="#0b1329" if is_active else Theme.TEXT_SECONDARY,
                hover_color=Theme.CYAN_HOVER if is_active else Theme.BG_CARD_HOVER,
                border_width=0 if is_active else 1,
                border_color=Theme.BORDER_SUBTLE,
                corner_radius=6,
                height=26,
                width=75,
                command=lambda fn=f_name: self._set_filter(fn)
            )
            btn.pack(side="left", padx=(0, 8))
            self.filter_buttons[f_name] = btn

        # 2. Scrollable Container
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=8, pady=(0, 10))

        self.cards_container = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.cards_container.pack(fill="both", expand=True)

        self._render_cards()

    def _set_filter(self, filter_name):
        self.active_filter = filter_name
        for fn, btn in self.filter_buttons.items():
            is_active = (fn == filter_name)
            btn.configure(
                fg_color=Theme.CYAN_TSTUDIO if is_active else Theme.BG_CARD,
                text_color="#0b1329" if is_active else Theme.TEXT_SECONDARY,
                font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold" if is_active else "normal"),
                border_width=0 if is_active else 1
            )
        self.apply_search_and_filter()

    def apply_search_and_filter(self, search_query=""):
        q = (search_query or "").lower().strip()
        filtered = []

        for p in self.all_projects:
            if self.active_filter == "กำลังแปล" and p.get("status") == "Completed":
                continue
            if self.active_filter == "แปลเสร็จ" and p.get("status") != "Completed":
                continue
            if self.active_filter == "ปักหมุด" and not p.get("is_pinned", False):
                continue

            if q:
                name_match = q in p.get("name", "").lower()
                engine_match = q in (p.get("engine_badge") or "").lower()
                if not (name_match or engine_match):
                    continue

            filtered.append(p)

        self.filtered_projects = filtered
        self._render_cards()

    def _on_resize(self, event=None):
        if not event or event.width < 100:
            return
        available_width = event.width - 30
        cols = max(1, available_width // self.CARD_TOTAL_WIDTH)
        if cols != self.current_cols:
            self.current_cols = cols
            self._rearrange_grid()

    def _render_cards(self):
        for c in self.card_widgets:
            c.destroy()
        self.card_widgets.clear()

        for proj in self.filtered_projects:
            card = ProjectCard(
                self.cards_container,
                project=proj,
                on_tstudio_click=self.on_tstudio_click,
                on_ai_click=self.on_ai_click,
                on_select=self.on_select_project
            )
            self.card_widgets.append(card)

        self._rearrange_grid()

    def _rearrange_grid(self):
        for c in range(self.current_cols + 2):
            self.cards_container.grid_columnconfigure(c, weight=0)

        for col_idx in range(self.current_cols):
            self.cards_container.grid_columnconfigure(col_idx, weight=1)

        row, col = 0, 0
        for card in self.card_widgets:
            card.grid(row=row, column=col, padx=6, pady=6, sticky="n")
            col += 1
            if col >= self.current_cols:
                col = 0
                row += 1

    def update_projects(self, projects):
        self.all_projects = projects
        self.apply_search_and_filter()
