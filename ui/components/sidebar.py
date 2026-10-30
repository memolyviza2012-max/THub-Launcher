import os
import customtkinter as ctk
from PIL import Image
from ui.theme import Theme

class Sidebar(ctk.CTkFrame):
    """
    DLSS Swapper-inspired Navigation Sidebar.
    Streamlined to use a single unified Dashboard for all mod projects.
    """

    def __init__(self, parent, on_navigate=None, current_route="dashboard"):
        super().__init__(
            parent,
            width=220,
            corner_radius=0,
            fg_color=Theme.BG_SIDEBAR,
            border_width=0
        )
        self.on_navigate = on_navigate
        self.current_route = current_route
        self.nav_buttons = {}

        self.grid_rowconfigure(7, weight=1) # Spacer pushes status widget to bottom
        self._build_ui()

    def _build_ui(self):
        # 1. Branding Header
        logo_frame = ctk.CTkFrame(self, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=18, pady=(22, 24), sticky="w")

        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        logo_path = os.path.join(base_dir, "assets", "THub.png")

        if os.path.exists(logo_path):
            try:
                logo_img = ctk.CTkImage(light_image=Image.open(logo_path), size=(34, 34))
                lbl_icon = ctk.CTkLabel(logo_frame, text="", image=logo_img)
                lbl_icon.pack(side="left", padx=(0, 10))
            except Exception:
                pass

        brand_text_frame = ctk.CTkFrame(logo_frame, fg_color="transparent")
        brand_text_frame.pack(side="left")

        lbl_title = ctk.CTkLabel(
            brand_text_frame,
            text="THub 2.2",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=17, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        )
        lbl_title.pack(anchor="w")

        lbl_sub = ctk.CTkLabel(
            brand_text_frame,
            text="FLAGSHIP MODDER SUITE",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=8, weight="bold"),
            text_color=Theme.CYAN_TSTUDIO
        )
        lbl_sub.pack(anchor="w")

        # 2. Navigation Items (Unified Dashboard only - no redundant Projects tab)
        menu_items = [
            ("dashboard", "📊", "Dashboard (หน้าหลัก)"),
            ("tstudio",   "📝", "TStudio Hub"),
            ("ai_helper", "🤖", "AI Helper Copilot"),
            ("apps",      "✨", "THub Apps"),
            ("knowledge", "📚", "คลังความรู้ (Docs)")
        ]

        row = 1
        for route_id, icon, label in menu_items:
            is_active = (route_id == self.current_route)
            btn = self._create_nav_button(route_id, icon, label, is_active)
            btn.grid(row=row, column=0, padx=10, pady=3, sticky="ew")
            self.nav_buttons[route_id] = btn
            row += 1

        # 3. Bottom Live Status Widget
        self.status_card = ctk.CTkFrame(self, corner_radius=10, fg_color=Theme.BG_CARD, border_width=1, border_color=Theme.BORDER_SUBTLE)
        self.status_card.grid(row=8, column=0, padx=12, pady=16, sticky="ew")

        status_header = ctk.CTkFrame(self.status_card, fg_color="transparent")
        status_header.pack(fill="x", padx=10, pady=(8, 2))

        ctk.CTkLabel(status_header, text="●", font=ctk.CTkFont(size=11), text_color=Theme.GREEN_SUCCESS).pack(side="left", padx=(0, 6))
        ctk.CTkLabel(status_header, text="พร้อมใช้งาน", font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"), text_color=Theme.TEXT_PRIMARY).pack(side="left")

        lbl_engine_status = ctk.CTkLabel(
            self.status_card,
            text="AI Engine & TStudio: Ready\nTHub Next-Gen v2.2.0",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=10),
            text_color=Theme.TEXT_MUTED,
            justify="left"
        )
        lbl_engine_status.pack(anchor="w", padx=10, pady=(0, 8))

        accent_bar = ctk.CTkFrame(self.status_card, height=3, corner_radius=2, fg_color=Theme.GREEN_SUCCESS)
        accent_bar.pack(fill="x", padx=10, pady=(0, 6))

    def _create_nav_button(self, route_id, icon, label, is_active):
        fg = Theme.BG_CARD if is_active else "transparent"
        text_color = Theme.CYAN_TSTUDIO if is_active else Theme.TEXT_SECONDARY
        font_weight = "bold" if is_active else "normal"

        btn = ctk.CTkButton(
            self,
            text=f"  {icon}  {label}",
            anchor="w",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12, weight=font_weight),
            fg_color=fg,
            text_color=text_color,
            hover_color=Theme.BG_CARD_HOVER,
            corner_radius=8,
            height=36,
            command=lambda r=route_id: self._on_btn_click(r)
        )
        return btn

    def _on_btn_click(self, route_id):
        self.set_active(route_id)
        if self.on_navigate:
            self.on_navigate(route_id)

    def set_active(self, route_id):
        self.current_route = route_id
        for r_id, btn in self.nav_buttons.items():
            is_active = (r_id == route_id)
            fg = Theme.BG_CARD if is_active else "transparent"
            text_color = Theme.CYAN_TSTUDIO if is_active else Theme.TEXT_SECONDARY
            font_weight = "bold" if is_active else "normal"
            btn.configure(
                fg_color=fg,
                text_color=text_color,
                font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12, weight=font_weight)
            )
