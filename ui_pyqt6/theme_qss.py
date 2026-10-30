"""
PyQt6 QSS Stylesheets & Dynamic Theme Engine for THub 2.2
==========================================================
Supported Themes (21 Themes + Auto & Random):
  Dark Themes:
    - Dark (Obsidian)
    - Dracula
    - Mocha (Catppuccin Mocha)
    - Ember
    - Rosé Pine
    - Moonlight
    - Slate
    - Midnight
    - Nord
  Light Themes:
    - Light
    - Alucard
    - Latte (Catppuccin Latte)
    - Ember Light
    - Rosé Pine Dawn
    - Sunshine
    - Indigo
    - Ocean
    - Forest
    - Rose
    - Lavender
    - Monochrome
"""

import sys

def detect_os_theme() -> str:
    """Detect Windows system Dark / Light mode preference."""
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
        value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        winreg.CloseKey(key)
        return "light" if value == 1 else "dark"
    except Exception:
        pass

    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtGui import QPalette
        app = QApplication.instance()
        if app:
            bg_lum = app.palette().color(QPalette.ColorRole.Window).lightness()
            return "light" if bg_lum > 128 else "dark"
    except Exception:
        pass

    return "dark"


THEME_PALETTES = {
    # ── DARK THEMES (9) ────────────────────────────────────────────────────────
    "dark": {
        "name": "Dark",
        "is_light": False,
        "bg_canvas": "#0b0e14",
        "bg_sidebar": "#10141e",
        "border_sidebar": "#1c2230",
        "bg_card": "#151926",
        "border_card": "#202638",
        "bg_card_hover": "#1b2133",
        "border_card_hover": "#384566",
        "accent": "#2563eb",
        "accent_hover": "#1d4ed8",
        "accent_text": "#ffffff",
        "primary_btn": "#2563eb",
        "primary_btn_hover": "#1d4ed8",
        "primary_btn_text": "#ffffff",
        "secondary_btn": "#181d2a",
        "secondary_btn_border": "#252c3d",
        "secondary_btn_text": "#94a3b8",
        "secondary_btn_hover": "#22293b",
        "secondary_btn_hover_text": "#f8fafc",
        "nav_btn_active_bg": "#1a2030",
        "text_primary": "#f8fafc",
        "text_secondary": "#94a3b8",
        "text_muted": "#64748b",
        "ai_bg": "#2b1d42",
        "ai_border": "#a855f7",
        "ai_text": "#c084fc",
        "ai_hover_bg": "#3e2663",
        "input_bg": "#141824",
        "input_border": "#252c3d",
        "pill_bg": "#1a2030",
        "menu_bg": "#141824",
        "menu_border": "#242c40",
        "menu_item_selected": "#20283d",
        "tab_pane_bg": "#0e121a",
        "tab_pane_border": "#202638",
        "tab_bar_bg": "#141826",
        "scrollbar_thumb": "#252b3d",
        "scrollbar_thumb_hover": "#3b4460",
    },
    "dracula": {
        "name": "Dracula",
        "is_light": False,
        "bg_canvas": "#282a36",
        "bg_sidebar": "#21222c",
        "border_sidebar": "#383a4c",
        "bg_card": "#343746",
        "border_card": "#44475a",
        "bg_card_hover": "#424450",
        "border_card_hover": "#bd93f9",
        "accent": "#bd93f9",
        "accent_hover": "#a77be8",
        "accent_text": "#282a36",
        "primary_btn": "#50fa7b",
        "primary_btn_hover": "#40e069",
        "primary_btn_text": "#21222c",
        "secondary_btn": "#44475a",
        "secondary_btn_border": "#6272a4",
        "secondary_btn_text": "#f8f8f2",
        "secondary_btn_hover": "#54576c",
        "secondary_btn_hover_text": "#ffffff",
        "nav_btn_active_bg": "#44475a",
        "text_primary": "#f8f8f2",
        "text_secondary": "#bd93f9",
        "text_muted": "#6272a4",
        "ai_bg": "#412d4d",
        "ai_border": "#ff79c6",
        "ai_text": "#ff79c6",
        "ai_hover_bg": "#523661",
        "input_bg": "#21222c",
        "input_border": "#44475a",
        "pill_bg": "#44475a",
        "menu_bg": "#21222c",
        "menu_border": "#44475a",
        "menu_item_selected": "#44475a",
        "tab_pane_bg": "#282a36",
        "tab_pane_border": "#44475a",
        "tab_bar_bg": "#21222c",
        "scrollbar_thumb": "#44475a",
        "scrollbar_thumb_hover": "#6272a4",
    },
    "mocha": {
        "name": "Mocha",
        "is_light": False,
        "bg_canvas": "#1e1e2e",
        "bg_sidebar": "#181825",
        "border_sidebar": "#313244",
        "bg_card": "#252538",
        "border_card": "#313244",
        "bg_card_hover": "#2e2e44",
        "border_card_hover": "#cba6f7",
        "accent": "#cba6f7",
        "accent_hover": "#b48ef2",
        "accent_text": "#11111b",
        "primary_btn": "#a6e3a1",
        "primary_btn_hover": "#94d28f",
        "primary_btn_text": "#11111b",
        "secondary_btn": "#313244",
        "secondary_btn_border": "#45475a",
        "secondary_btn_text": "#cdd6f4",
        "secondary_btn_hover": "#45475a",
        "secondary_btn_hover_text": "#ffffff",
        "nav_btn_active_bg": "#313244",
        "text_primary": "#cdd6f4",
        "text_secondary": "#a6adc8",
        "text_muted": "#6c7086",
        "ai_bg": "#392949",
        "ai_border": "#f5c2e7",
        "ai_text": "#f5c2e7",
        "ai_hover_bg": "#47325b",
        "input_bg": "#181825",
        "input_border": "#313244",
        "pill_bg": "#313244",
        "menu_bg": "#181825",
        "menu_border": "#313244",
        "menu_item_selected": "#313244",
        "tab_pane_bg": "#1e1e2e",
        "tab_pane_border": "#313244",
        "tab_bar_bg": "#181825",
        "scrollbar_thumb": "#313244",
        "scrollbar_thumb_hover": "#45475a",
    },
    "ember": {
        "name": "Ember",
        "is_light": False,
        "bg_canvas": "#140d09",
        "bg_sidebar": "#1c120c",
        "border_sidebar": "#2c1b12",
        "bg_card": "#241810",
        "border_card": "#3b2518",
        "bg_card_hover": "#2f1f15",
        "border_card_hover": "#f97316",
        "accent": "#f97316",
        "accent_hover": "#ea580c",
        "accent_text": "#140d09",
        "primary_btn": "#f97316",
        "primary_btn_hover": "#ea580c",
        "primary_btn_text": "#ffffff",
        "secondary_btn": "#2c1b12",
        "secondary_btn_border": "#432a1c",
        "secondary_btn_text": "#fdba74",
        "secondary_btn_hover": "#3b2518",
        "secondary_btn_hover_text": "#fff7ed",
        "nav_btn_active_bg": "#3b2518",
        "text_primary": "#ffedd5",
        "text_secondary": "#fdba74",
        "text_muted": "#9a6a4d",
        "ai_bg": "#3b1d14",
        "ai_border": "#ef4444",
        "ai_text": "#fca5a5",
        "ai_hover_bg": "#4d2419",
        "input_bg": "#1c120c",
        "input_border": "#3b2518",
        "pill_bg": "#2c1b12",
        "menu_bg": "#1c120c",
        "menu_border": "#3b2518",
        "menu_item_selected": "#3b2518",
        "tab_pane_bg": "#1c120c",
        "tab_pane_border": "#3b2518",
        "tab_bar_bg": "#140d09",
        "scrollbar_thumb": "#3b2518",
        "scrollbar_thumb_hover": "#f97316",
    },
    "rose pine": {
        "name": "Rosé Pine",
        "is_light": False,
        "bg_canvas": "#191724",
        "bg_sidebar": "#1f1d2e",
        "border_sidebar": "#26233a",
        "bg_card": "#211f32",
        "border_card": "#2f2b44",
        "bg_card_hover": "#2b2740",
        "border_card_hover": "#ebbcba",
        "accent": "#ebbcba",
        "accent_hover": "#e2a6a4",
        "accent_text": "#191724",
        "primary_btn": "#31748f",
        "primary_btn_hover": "#286077",
        "primary_btn_text": "#f4ede8",
        "secondary_btn": "#26233a",
        "secondary_btn_border": "#393552",
        "secondary_btn_text": "#e0def4",
        "secondary_btn_hover": "#393552",
        "secondary_btn_hover_text": "#ffffff",
        "nav_btn_active_bg": "#2a283e",
        "text_primary": "#e0def4",
        "text_secondary": "#908caa",
        "text_muted": "#6e6a86",
        "ai_bg": "#322435",
        "ai_border": "#c4a7e7",
        "ai_text": "#c4a7e7",
        "ai_hover_bg": "#422f47",
        "input_bg": "#1f1d2e",
        "input_border": "#2f2b44",
        "pill_bg": "#26233a",
        "menu_bg": "#1f1d2e",
        "menu_border": "#2f2b44",
        "menu_item_selected": "#2a283e",
        "tab_pane_bg": "#191724",
        "tab_pane_border": "#2f2b44",
        "tab_bar_bg": "#1f1d2e",
        "scrollbar_thumb": "#2f2b44",
        "scrollbar_thumb_hover": "#393552",
    },
    "moonlight": {
        "name": "Moonlight",
        "is_light": False,
        "bg_canvas": "#191a2a",
        "bg_sidebar": "#1e2030",
        "border_sidebar": "#2a2d44",
        "bg_card": "#222436",
        "border_card": "#31354e",
        "bg_card_hover": "#2a2c42",
        "border_card_hover": "#82aaff",
        "accent": "#82aaff",
        "accent_hover": "#6f9dfc",
        "accent_text": "#191a2a",
        "primary_btn": "#4fd6be",
        "primary_btn_hover": "#3bc4ab",
        "primary_btn_text": "#191a2a",
        "secondary_btn": "#2a2d44",
        "secondary_btn_border": "#3c4161",
        "secondary_btn_text": "#c8d3f5",
        "secondary_btn_hover": "#363a56",
        "secondary_btn_hover_text": "#ffffff",
        "nav_btn_active_bg": "#2c3049",
        "text_primary": "#c8d3f5",
        "text_secondary": "#828bb8",
        "text_muted": "#636da6",
        "ai_bg": "#2b274a",
        "ai_border": "#c099ff",
        "ai_text": "#c099ff",
        "ai_hover_bg": "#383260",
        "input_bg": "#1e2030",
        "input_border": "#31354e",
        "pill_bg": "#2a2d44",
        "menu_bg": "#1e2030",
        "menu_border": "#31354e",
        "menu_item_selected": "#2c3049",
        "tab_pane_bg": "#191a2a",
        "tab_pane_border": "#31354e",
        "tab_bar_bg": "#1e2030",
        "scrollbar_thumb": "#31354e",
        "scrollbar_thumb_hover": "#444a6e",
    },
    "slate": {
        "name": "Slate",
        "is_light": False,
        "bg_canvas": "#0f172a",
        "bg_sidebar": "#1e293b",
        "border_sidebar": "#334155",
        "bg_card": "#1e293b",
        "border_card": "#334155",
        "bg_card_hover": "#28354b",
        "border_card_hover": "#38bdf8",
        "accent": "#38bdf8",
        "accent_hover": "#0ea5e9",
        "accent_text": "#0f172a",
        "primary_btn": "#0284c7",
        "primary_btn_hover": "#0369a1",
        "primary_btn_text": "#ffffff",
        "secondary_btn": "#334155",
        "secondary_btn_border": "#475569",
        "secondary_btn_text": "#e2e8f0",
        "secondary_btn_hover": "#475569",
        "secondary_btn_hover_text": "#ffffff",
        "nav_btn_active_bg": "#334155",
        "text_primary": "#f8fafc",
        "text_secondary": "#94a3b8",
        "text_muted": "#64748b",
        "ai_bg": "#282747",
        "ai_border": "#818cf8",
        "ai_text": "#a5b4fc",
        "ai_hover_bg": "#35335f",
        "input_bg": "#141d2e",
        "input_border": "#334155",
        "pill_bg": "#334155",
        "menu_bg": "#1e293b",
        "menu_border": "#334155",
        "menu_item_selected": "#334155",
        "tab_pane_bg": "#0f172a",
        "tab_pane_border": "#334155",
        "tab_bar_bg": "#1e293b",
        "scrollbar_thumb": "#334155",
        "scrollbar_thumb_hover": "#475569",
    },
    "midnight": {
        "name": "Midnight",
        "is_light": False,
        "bg_canvas": "#070f1e",
        "bg_sidebar": "#0b172e",
        "border_sidebar": "#162d59",
        "bg_card": "#0f2042",
        "border_card": "#1a366b",
        "bg_card_hover": "#162d5c",
        "border_card_hover": "#38bdf8",
        "accent": "#38bdf8",
        "accent_hover": "#0ea5e9",
        "accent_text": "#070f1e",
        "primary_btn": "#0284c7",
        "primary_btn_hover": "#0369a1",
        "primary_btn_text": "#f0f9ff",
        "secondary_btn": "#15274d",
        "secondary_btn_border": "#23407c",
        "secondary_btn_text": "#93c5fd",
        "secondary_btn_hover": "#1e386e",
        "secondary_btn_hover_text": "#ffffff",
        "nav_btn_active_bg": "#162d5c",
        "text_primary": "#f0f9ff",
        "text_secondary": "#93c5fd",
        "text_muted": "#60a5fa",
        "ai_bg": "#1e1b4b",
        "ai_border": "#6366f1",
        "ai_text": "#a5b4fc",
        "ai_hover_bg": "#2e2978",
        "input_bg": "#0b172e",
        "input_border": "#1d3b75",
        "pill_bg": "#15274d",
        "menu_bg": "#0b172e",
        "menu_border": "#1d3b75",
        "menu_item_selected": "#162d5c",
        "tab_pane_bg": "#0b172e",
        "tab_pane_border": "#1a366b",
        "tab_bar_bg": "#070f1e",
        "scrollbar_thumb": "#1e386e",
        "scrollbar_thumb_hover": "#38bdf8",
    },
    "nord": {
        "name": "Nord",
        "is_light": False,
        "bg_canvas": "#2e3440",
        "bg_sidebar": "#242933",
        "border_sidebar": "#3b4252",
        "bg_card": "#3b4252",
        "border_card": "#434c5e",
        "bg_card_hover": "#485265",
        "border_card_hover": "#88c0d0",
        "accent": "#88c0d0",
        "accent_hover": "#81a1c1",
        "accent_text": "#2e3440",
        "primary_btn": "#88c0d0",
        "primary_btn_hover": "#81a1c1",
        "primary_btn_text": "#2e3440",
        "secondary_btn": "#434c5e",
        "secondary_btn_border": "#4c566a",
        "secondary_btn_text": "#d8dee9",
        "secondary_btn_hover": "#4c566a",
        "secondary_btn_hover_text": "#eceff4",
        "nav_btn_active_bg": "#434c5e",
        "text_primary": "#eceff4",
        "text_secondary": "#d8dee9",
        "text_muted": "#7a8599",
        "ai_bg": "#3c384d",
        "ai_border": "#b48ead",
        "ai_text": "#b48ead",
        "ai_hover_bg": "#4d4763",
        "input_bg": "#242933",
        "input_border": "#434c5e",
        "pill_bg": "#434c5e",
        "menu_bg": "#242933",
        "menu_border": "#434c5e",
        "menu_item_selected": "#434c5e",
        "tab_pane_bg": "#2e3440",
        "tab_pane_border": "#434c5e",
        "tab_bar_bg": "#242933",
        "scrollbar_thumb": "#434c5e",
        "scrollbar_thumb_hover": "#88c0d0",
    },

    # ── LIGHT THEMES (12) ───────────────────────────────────────────────────────
    "light": {
        "name": "Light",
        "is_light": True,
        "bg_canvas": "#f8fafc",
        "bg_sidebar": "#ffffff",
        "border_sidebar": "#e2e8f0",
        "bg_card": "#ffffff",
        "border_card": "#e2e8f0",
        "bg_card_hover": "#f1f5f9",
        "border_card_hover": "#2563eb",
        "accent": "#2563eb",
        "accent_hover": "#1d4ed8",
        "accent_text": "#ffffff",
        "primary_btn": "#2563eb",
        "primary_btn_hover": "#1d4ed8",
        "primary_btn_text": "#ffffff",
        "secondary_btn": "#f1f5f9",
        "secondary_btn_border": "#cbd5e1",
        "secondary_btn_text": "#334155",
        "secondary_btn_hover": "#e2e8f0",
        "secondary_btn_hover_text": "#0f172a",
        "nav_btn_active_bg": "#e0e7ff",
        "text_primary": "#0f172a",
        "text_secondary": "#475569",
        "text_muted": "#94a3b8",
        "ai_bg": "#f3e8ff",
        "ai_border": "#9333ea",
        "ai_text": "#7e22ce",
        "ai_hover_bg": "#e9d5ff",
        "input_bg": "#ffffff",
        "input_border": "#cbd5e1",
        "pill_bg": "#e2e8f0",
        "menu_bg": "#ffffff",
        "menu_border": "#e2e8f0",
        "menu_item_selected": "#e0e7ff",
        "tab_pane_bg": "#ffffff",
        "tab_pane_border": "#e2e8f0",
        "tab_bar_bg": "#f1f5f9",
        "scrollbar_thumb": "#cbd5e1",
        "scrollbar_thumb_hover": "#94a3b8",
    },
    "alucard": {
        "name": "Alucard",
        "is_light": True,
        "bg_canvas": "#f4f4f6",
        "bg_sidebar": "#ffffff",
        "border_sidebar": "#e4e4e7",
        "bg_card": "#ffffff",
        "border_card": "#e4e4e7",
        "bg_card_hover": "#fafafa",
        "border_card_hover": "#dc2626",
        "accent": "#dc2626",
        "accent_hover": "#b91c1c",
        "accent_text": "#ffffff",
        "primary_btn": "#b91c1c",
        "primary_btn_hover": "#991b1b",
        "primary_btn_text": "#ffffff",
        "secondary_btn": "#f4f4f5",
        "secondary_btn_border": "#d4d4d8",
        "secondary_btn_text": "#27272a",
        "secondary_btn_hover": "#e4e4e7",
        "secondary_btn_hover_text": "#09090b",
        "nav_btn_active_bg": "#fee2e2",
        "text_primary": "#18181b",
        "text_secondary": "#52525b",
        "text_muted": "#a1a1aa",
        "ai_bg": "#fef2f2",
        "ai_border": "#dc2626",
        "ai_text": "#b91c1c",
        "ai_hover_bg": "#fee2e2",
        "input_bg": "#ffffff",
        "input_border": "#d4d4d8",
        "pill_bg": "#f4f4f5",
        "menu_bg": "#ffffff",
        "menu_border": "#e4e4e7",
        "menu_item_selected": "#fee2e2",
        "tab_pane_bg": "#ffffff",
        "tab_pane_border": "#e4e4e7",
        "tab_bar_bg": "#f4f4f5",
        "scrollbar_thumb": "#d4d4d8",
        "scrollbar_thumb_hover": "#dc2626",
    },
    "latte": {
        "name": "Latte",
        "is_light": True,
        "bg_canvas": "#eff1f5",
        "bg_sidebar": "#e6e9ef",
        "border_sidebar": "#ccd0da",
        "bg_card": "#ffffff",
        "border_card": "#ccd0da",
        "bg_card_hover": "#f5f6f9",
        "border_card_hover": "#1e66f5",
        "accent": "#1e66f5",
        "accent_hover": "#1855c4",
        "accent_text": "#ffffff",
        "primary_btn": "#40a02b",
        "primary_btn_hover": "#328022",
        "primary_btn_text": "#ffffff",
        "secondary_btn": "#dce0e8",
        "secondary_btn_border": "#bcc0cc",
        "secondary_btn_text": "#4c4f69",
        "secondary_btn_hover": "#ccd0da",
        "secondary_btn_hover_text": "#2a2b3d",
        "nav_btn_active_bg": "#dce0e8",
        "text_primary": "#4c4f69",
        "text_secondary": "#6c6f85",
        "text_muted": "#9ca0b0",
        "ai_bg": "#eaedf7",
        "ai_border": "#8839ef",
        "ai_text": "#8839ef",
        "ai_hover_bg": "#d8def1",
        "input_bg": "#ffffff",
        "input_border": "#ccd0da",
        "pill_bg": "#dce0e8",
        "menu_bg": "#ffffff",
        "menu_border": "#ccd0da",
        "menu_item_selected": "#dce0e8",
        "tab_pane_bg": "#ffffff",
        "tab_pane_border": "#ccd0da",
        "tab_bar_bg": "#e6e9ef",
        "scrollbar_thumb": "#ccd0da",
        "scrollbar_thumb_hover": "#1e66f5",
    },
    "ember light": {
        "name": "Ember Light",
        "is_light": True,
        "bg_canvas": "#fffbeb",
        "bg_sidebar": "#fef3c7",
        "border_sidebar": "#fde68a",
        "bg_card": "#ffffff",
        "border_card": "#fde68a",
        "bg_card_hover": "#fffdf5",
        "border_card_hover": "#ea580c",
        "accent": "#ea580c",
        "accent_hover": "#c2410c",
        "accent_text": "#ffffff",
        "primary_btn": "#ea580c",
        "primary_btn_hover": "#c2410c",
        "primary_btn_text": "#ffffff",
        "secondary_btn": "#fef3c7",
        "secondary_btn_border": "#fcd34d",
        "secondary_btn_text": "#92400e",
        "secondary_btn_hover": "#fde68a",
        "secondary_btn_hover_text": "#78350f",
        "nav_btn_active_bg": "#fed7aa",
        "text_primary": "#78350f",
        "text_secondary": "#92400e",
        "text_muted": "#b45309",
        "ai_bg": "#ffedd5",
        "ai_border": "#f97316",
        "ai_text": "#c2410c",
        "ai_hover_bg": "#fed7aa",
        "input_bg": "#ffffff",
        "input_border": "#fcd34d",
        "pill_bg": "#fef3c7",
        "menu_bg": "#ffffff",
        "menu_border": "#fde68a",
        "menu_item_selected": "#fed7aa",
        "tab_pane_bg": "#ffffff",
        "tab_pane_border": "#fde68a",
        "tab_bar_bg": "#fef3c7",
        "scrollbar_thumb": "#fcd34d",
        "scrollbar_thumb_hover": "#ea580c",
    },
    "rose pine dawn": {
        "name": "Rosé Pine Dawn",
        "is_light": True,
        "bg_canvas": "#faf4ed",
        "bg_sidebar": "#fffaf3",
        "border_sidebar": "#f2e9de",
        "bg_card": "#ffffff",
        "border_card": "#f2e9de",
        "bg_card_hover": "#fffdfa",
        "border_card_hover": "#d7827e",
        "accent": "#d7827e",
        "accent_hover": "#bf6f6b",
        "accent_text": "#ffffff",
        "primary_btn": "#286983",
        "primary_btn_hover": "#1f5368",
        "primary_btn_text": "#ffffff",
        "secondary_btn": "#f2e9de",
        "secondary_btn_border": "#e4d7c7",
        "secondary_btn_text": "#575279",
        "secondary_btn_hover": "#e4d7c7",
        "secondary_btn_hover_text": "#286983",
        "nav_btn_active_bg": "#f2e9de",
        "text_primary": "#575279",
        "text_secondary": "#797593",
        "text_muted": "#9893a5",
        "ai_bg": "#f5edf4",
        "ai_border": "#907aa9",
        "ai_text": "#907aa9",
        "ai_hover_bg": "#ebdde9",
        "input_bg": "#ffffff",
        "input_border": "#e4d7c7",
        "pill_bg": "#f2e9de",
        "menu_bg": "#ffffff",
        "menu_border": "#f2e9de",
        "menu_item_selected": "#f2e9de",
        "tab_pane_bg": "#ffffff",
        "tab_pane_border": "#f2e9de",
        "tab_bar_bg": "#fffaf3",
        "scrollbar_thumb": "#e4d7c7",
        "scrollbar_thumb_hover": "#d7827e",
    },
    "sunshine": {
        "name": "Sunshine",
        "is_light": True,
        "bg_canvas": "#fefce8",
        "bg_sidebar": "#fef9c3",
        "border_sidebar": "#fef08a",
        "bg_card": "#ffffff",
        "border_card": "#fef08a",
        "bg_card_hover": "#fffef0",
        "border_card_hover": "#ca8a04",
        "accent": "#ca8a04",
        "accent_hover": "#a16207",
        "accent_text": "#ffffff",
        "primary_btn": "#eab308",
        "primary_btn_hover": "#ca8a04",
        "primary_btn_text": "#713f12",
        "secondary_btn": "#fef9c3",
        "secondary_btn_border": "#fde047",
        "secondary_btn_text": "#854d0e",
        "secondary_btn_hover": "#fef08a",
        "secondary_btn_hover_text": "#713f12",
        "nav_btn_active_bg": "#fef08a",
        "text_primary": "#713f12",
        "text_secondary": "#854d0e",
        "text_muted": "#a16207",
        "ai_bg": "#fff7ed",
        "ai_border": "#f59e0b",
        "ai_text": "#b45309",
        "ai_hover_bg": "#ffedd5",
        "input_bg": "#ffffff",
        "input_border": "#fde047",
        "pill_bg": "#fef9c3",
        "menu_bg": "#ffffff",
        "menu_border": "#fef08a",
        "menu_item_selected": "#fef08a",
        "tab_pane_bg": "#ffffff",
        "tab_pane_border": "#fef08a",
        "tab_bar_bg": "#fef9c3",
        "scrollbar_thumb": "#fde047",
        "scrollbar_thumb_hover": "#ca8a04",
    },
    "indigo": {
        "name": "Indigo",
        "is_light": True,
        "bg_canvas": "#f5f7ff",
        "bg_sidebar": "#eef2ff",
        "border_sidebar": "#e0e7ff",
        "bg_card": "#ffffff",
        "border_card": "#e0e7ff",
        "bg_card_hover": "#f8f9ff",
        "border_card_hover": "#4f46e5",
        "accent": "#4f46e5",
        "accent_hover": "#4338ca",
        "accent_text": "#ffffff",
        "primary_btn": "#4f46e5",
        "primary_btn_hover": "#4338ca",
        "primary_btn_text": "#ffffff",
        "secondary_btn": "#e0e7ff",
        "secondary_btn_border": "#c7d2fe",
        "secondary_btn_text": "#3730a3",
        "secondary_btn_hover": "#c7d2fe",
        "secondary_btn_hover_text": "#1e1b4b",
        "nav_btn_active_bg": "#e0e7ff",
        "text_primary": "#1e1b4b",
        "text_secondary": "#4338ca",
        "text_muted": "#6366f1",
        "ai_bg": "#ede9fe",
        "ai_border": "#7c3aed",
        "ai_text": "#6d28d9",
        "ai_hover_bg": "#ddd6fe",
        "input_bg": "#ffffff",
        "input_border": "#c7d2fe",
        "pill_bg": "#e0e7ff",
        "menu_bg": "#ffffff",
        "menu_border": "#e0e7ff",
        "menu_item_selected": "#e0e7ff",
        "tab_pane_bg": "#ffffff",
        "tab_pane_border": "#e0e7ff",
        "tab_bar_bg": "#eef2ff",
        "scrollbar_thumb": "#c7d2fe",
        "scrollbar_thumb_hover": "#4f46e5",
    },
    "ocean": {
        "name": "Ocean",
        "is_light": True,
        "bg_canvas": "#f0fdfa",
        "bg_sidebar": "#ccfbf1",
        "border_sidebar": "#99f6e4",
        "bg_card": "#ffffff",
        "border_card": "#99f6e4",
        "bg_card_hover": "#f5fffc",
        "border_card_hover": "#0d9488",
        "accent": "#0d9488",
        "accent_hover": "#0f766e",
        "accent_text": "#ffffff",
        "primary_btn": "#0284c7",
        "primary_btn_hover": "#0369a1",
        "primary_btn_text": "#ffffff",
        "secondary_btn": "#ccfbf1",
        "secondary_btn_border": "#5eead4",
        "secondary_btn_text": "#115e59",
        "secondary_btn_hover": "#99f6e4",
        "secondary_btn_hover_text": "#134e4a",
        "nav_btn_active_bg": "#99f6e4",
        "text_primary": "#134e4a",
        "text_secondary": "#115e59",
        "text_muted": "#0f766e",
        "ai_bg": "#e0f2fe",
        "ai_border": "#0284c7",
        "ai_text": "#0369a1",
        "ai_hover_bg": "#bae6fd",
        "input_bg": "#ffffff",
        "input_border": "#5eead4",
        "pill_bg": "#ccfbf1",
        "menu_bg": "#ffffff",
        "menu_border": "#99f6e4",
        "menu_item_selected": "#99f6e4",
        "tab_pane_bg": "#ffffff",
        "tab_pane_border": "#99f6e4",
        "tab_bar_bg": "#ccfbf1",
        "scrollbar_thumb": "#5eead4",
        "scrollbar_thumb_hover": "#0d9488",
    },
    "forest": {
        "name": "Forest",
        "is_light": True,
        "bg_canvas": "#f0fdf4",
        "bg_sidebar": "#dcfce7",
        "border_sidebar": "#bbf7d0",
        "bg_card": "#ffffff",
        "border_card": "#bbf7d0",
        "bg_card_hover": "#f6fff8",
        "border_card_hover": "#16a34a",
        "accent": "#16a34a",
        "accent_hover": "#15803d",
        "accent_text": "#ffffff",
        "primary_btn": "#15803d",
        "primary_btn_hover": "#166534",
        "primary_btn_text": "#ffffff",
        "secondary_btn": "#dcfce7",
        "secondary_btn_border": "#86efac",
        "secondary_btn_text": "#14532d",
        "secondary_btn_hover": "#bbf7d0",
        "secondary_btn_hover_text": "#14532d",
        "nav_btn_active_bg": "#bbf7d0",
        "text_primary": "#14532d",
        "text_secondary": "#166534",
        "text_muted": "#15803d",
        "ai_bg": "#ecfccb",
        "ai_border": "#65a30d",
        "ai_text": "#4d7c0f",
        "ai_hover_bg": "#d9f99d",
        "input_bg": "#ffffff",
        "input_border": "#86efac",
        "pill_bg": "#dcfce7",
        "menu_bg": "#ffffff",
        "menu_border": "#bbf7d0",
        "menu_item_selected": "#bbf7d0",
        "tab_pane_bg": "#ffffff",
        "tab_pane_border": "#bbf7d0",
        "tab_bar_bg": "#dcfce7",
        "scrollbar_thumb": "#86efac",
        "scrollbar_thumb_hover": "#16a34a",
    },
    "rose": {
        "name": "Rose",
        "is_light": True,
        "bg_canvas": "#fff1f2",
        "bg_sidebar": "#ffe4e6",
        "border_sidebar": "#fecdd3",
        "bg_card": "#ffffff",
        "border_card": "#fecdd3",
        "bg_card_hover": "#fff7f8",
        "border_card_hover": "#e11d48",
        "accent": "#e11d48",
        "accent_hover": "#be123c",
        "accent_text": "#ffffff",
        "primary_btn": "#e11d48",
        "primary_btn_hover": "#be123c",
        "primary_btn_text": "#ffffff",
        "secondary_btn": "#ffe4e6",
        "secondary_btn_border": "#fda4af",
        "secondary_btn_text": "#9f1239",
        "secondary_btn_hover": "#fecdd3",
        "secondary_btn_hover_text": "#881337",
        "nav_btn_active_bg": "#fecdd3",
        "text_primary": "#881337",
        "text_secondary": "#9f1239",
        "text_muted": "#be123c",
        "ai_bg": "#fdf2f8",
        "ai_border": "#db2777",
        "ai_text": "#be185d",
        "ai_hover_bg": "#fce7f3",
        "input_bg": "#ffffff",
        "input_border": "#fda4af",
        "pill_bg": "#ffe4e6",
        "menu_bg": "#ffffff",
        "menu_border": "#fecdd3",
        "menu_item_selected": "#fecdd3",
        "tab_pane_bg": "#ffffff",
        "tab_pane_border": "#fecdd3",
        "tab_bar_bg": "#ffe4e6",
        "scrollbar_thumb": "#fda4af",
        "scrollbar_thumb_hover": "#e11d48",
    },
    "lavender": {
        "name": "Lavender",
        "is_light": True,
        "bg_canvas": "#faf5ff",
        "bg_sidebar": "#f3e8ff",
        "border_sidebar": "#e9d5ff",
        "bg_card": "#ffffff",
        "border_card": "#e9d5ff",
        "bg_card_hover": "#fcf9ff",
        "border_card_hover": "#9333ea",
        "accent": "#9333ea",
        "accent_hover": "#7e22ce",
        "accent_text": "#ffffff",
        "primary_btn": "#9333ea",
        "primary_btn_hover": "#7e22ce",
        "primary_btn_text": "#ffffff",
        "secondary_btn": "#f3e8ff",
        "secondary_btn_border": "#d8b4fe",
        "secondary_btn_text": "#6b21a8",
        "secondary_btn_hover": "#e9d5ff",
        "secondary_btn_hover_text": "#581c87",
        "nav_btn_active_bg": "#e9d5ff",
        "text_primary": "#581c87",
        "text_secondary": "#6b21a8",
        "text_muted": "#9333ea",
        "ai_bg": "#f3e8ff",
        "ai_border": "#a855f7",
        "ai_text": "#7e22ce",
        "ai_hover_bg": "#e9d5ff",
        "input_bg": "#ffffff",
        "input_border": "#d8b4fe",
        "pill_bg": "#f3e8ff",
        "menu_bg": "#ffffff",
        "menu_border": "#e9d5ff",
        "menu_item_selected": "#e9d5ff",
        "tab_pane_bg": "#ffffff",
        "tab_pane_border": "#e9d5ff",
        "tab_bar_bg": "#f3e8ff",
        "scrollbar_thumb": "#d8b4fe",
        "scrollbar_thumb_hover": "#9333ea",
    },
    "monochrome": {
        "name": "Monochrome",
        "is_light": True,
        "bg_canvas": "#ffffff",
        "bg_sidebar": "#f8fafc",
        "border_sidebar": "#e2e8f0",
        "bg_card": "#ffffff",
        "border_card": "#cbd5e1",
        "bg_card_hover": "#f1f5f9",
        "border_card_hover": "#000000",
        "accent": "#0f172a",
        "accent_hover": "#000000",
        "accent_text": "#ffffff",
        "primary_btn": "#0f172a",
        "primary_btn_hover": "#000000",
        "primary_btn_text": "#ffffff",
        "secondary_btn": "#f1f5f9",
        "secondary_btn_border": "#cbd5e1",
        "secondary_btn_text": "#1e293b",
        "secondary_btn_hover": "#e2e8f0",
        "secondary_btn_hover_text": "#000000",
        "nav_btn_active_bg": "#e2e8f0",
        "text_primary": "#000000",
        "text_secondary": "#334155",
        "text_muted": "#64748b",
        "ai_bg": "#f1f5f9",
        "ai_border": "#334155",
        "ai_text": "#0f172a",
        "ai_hover_bg": "#e2e8f0",
        "input_bg": "#ffffff",
        "input_border": "#94a3b8",
        "pill_bg": "#f1f5f9",
        "menu_bg": "#ffffff",
        "menu_border": "#cbd5e1",
        "menu_item_selected": "#e2e8f0",
        "tab_pane_bg": "#ffffff",
        "tab_pane_border": "#cbd5e1",
        "tab_bar_bg": "#f8fafc",
        "scrollbar_thumb": "#cbd5e1",
        "scrollbar_thumb_hover": "#000000",
    }
}

# Aliases for backward compatibility & easy search
THEME_PALETTES["obsidian"] = THEME_PALETTES["dark"]
THEME_PALETTES["rosé pine"] = THEME_PALETTES["rose pine"]
THEME_PALETTES["rosé pine dawn"] = THEME_PALETTES["rose pine dawn"]
THEME_PALETTES["midnight blue"] = THEME_PALETTES["midnight"]


def get_theme_palette(theme_name: str = "dark") -> dict:
    """Safely retrieves the palette dictionary for any theme name."""
    raw = (theme_name or "dark").strip().lower()
    if raw in ("auto", "system"):
        os_mode = detect_os_theme()
        raw = "light" if os_mode == "light" else "dark"
    elif raw == "random":
        import random
        keys = list(THEME_PALETTES.keys())
        raw = random.choice(keys)

    # Direct match or alias match
    if raw in THEME_PALETTES:
        return THEME_PALETTES[raw]

    # Partial substring search
    for key, p in THEME_PALETTES.items():
        if key in raw or raw in key:
            return p

    return THEME_PALETTES["dark"]


def get_theme_stylesheet(theme_name: str = "Dark") -> str:
    """Generate a cohesive, responsive QSS stylesheet for the given theme."""
    p = get_theme_palette(theme_name)
    is_light = p.get("is_light", False)

    return f"""
/* Global Window & Dialogs */
QMainWindow, QWidget#MainRoot, QDialog {{
    background-color: {p["bg_canvas"]};
    color: {p["text_primary"]};
    font-family: 'Segoe UI', 'Prompt', sans-serif;
}}

/* Base & Semantic Labels */
QLabel {{
    color: {p["text_primary"]};
}}

QLabel.PageTitle {{
    color: {p["text_primary"]};
    font-size: 18px;
    font-weight: bold;
}}

QLabel#SidebarTitle, QLabel.SidebarTitle {{
    color: {p["text_primary"]};
    font-size: 17px;
    font-weight: bold;
}}

QLabel#SidebarVersion {{
    color: {p["accent"]};
    font-size: 17px;
    font-weight: 800;
}}

QLabel.BannerTitle {{
    color: {p["text_primary"]};
    font-size: 16px;
    font-weight: bold;
}}

QLabel.CardTitle, QLabel.SectionTitle {{
    color: {p["text_primary"]};
    font-size: 13px;
    font-weight: bold;
}}

QLabel.ProjectTitle {{
    color: {p["text_primary"]};
    font-size: 13px;
    font-weight: bold;
}}

QLabel.StatusText {{
    color: {p["text_secondary"]};
    font-size: 10px;
    font-weight: bold;
}}

QLabel.Muted, QLabel[muted="true"] {{
    color: {p["text_secondary"]};
}}

QLabel.SubText {{
    color: {p["text_muted"]};
}}

/* Content Banners & Cards */
QFrame.ContentBanner, QFrame.BannerCard {{
    background-color: {p["bg_card"]};
    border: 1px solid {p["border_card"]};
    border-radius: 10px;
}}

QFrame.PanelCard, QFrame.AICard {{
    background-color: {p["bg_card"]};
    border: 1px solid {p["border_card"]};
    border-radius: 10px;
}}

QFrame.InnerCard, QFrame.AIInnerCard {{
    background-color: {p["tab_pane_bg"]};
    border: 1px solid {p["input_border"]};
    border-radius: 8px;
}}

QFrame.SegmentBox {{
    background-color: {p["input_bg"]};
    border: 1px solid {p["input_border"]};
    border-radius: 8px;
}}

QTextEdit.CodeEditor, QTextEdit.PromptEditor, QPlainTextEdit.CodeEditor {{
    background-color: {p["input_bg"]};
    color: {p["text_primary"]};
    border: 1px solid {p["input_border"]};
    border-radius: 8px;
    font-family: Consolas, 'Courier New', monospace;
}}

/* Knowledge Base Navigation Item Buttons */
QPushButton.KBItemBtn {{
    background-color: {p["tab_pane_bg"]};
    color: {p["text_primary"]};
    border: 1px solid {p["input_border"]};
    border-radius: 6px;
    padding: 7px 10px;
    text-align: left;
    font-size: 11px;
    font-weight: 500;
}}
QPushButton.KBItemBtn:hover {{
    background-color: {p["bg_card_hover"]};
    border-color: {p["accent"]};
    color: {p["accent"]};
}}

/* Sidebar */
QWidget#Sidebar {{
    background-color: {p["bg_sidebar"]};
    border-right: 1px solid {p["border_sidebar"]};
}}

/* Navigation Buttons */
QPushButton.NavBtn {{
    background-color: transparent;
    color: {p["text_secondary"]};
    border: none;
    border-radius: 8px;
    padding: 9px 14px;
    text-align: left;
    font-size: 13px;
    font-weight: 500;
}}
QPushButton.NavBtn:hover {{
    background-color: {p["bg_card_hover"]};
    color: {p["text_primary"]};
}}
QPushButton.NavBtn[active="true"] {{
    background-color: {p["nav_btn_active_bg"]};
    color: {p["accent"]};
    font-weight: bold;
    border-left: 3px solid {p["accent"]};
}}

/* Sidebar Theme Switcher (Bottom-Left) */
QPushButton.ThemeSidebarBtn {{
    background-color: {p["bg_card"]};
    color: {p["text_primary"]};
    border: 1px solid {p["border_card"]};
    border-radius: 8px;
    padding: 7px 10px;
    text-align: left;
    font-size: 12px;
    font-weight: 500;
}}
QPushButton.ThemeSidebarBtn:hover {{
    background-color: {p["bg_card_hover"]};
    border-color: {p["accent"]};
    color: {p["accent"]};
}}

QPushButton.ThemeToggleBtn {{
    background-color: {p["bg_card"]};
    color: {p["text_primary"]};
    border: 1px solid {p["border_card"]};
    border-radius: 8px;
    padding: 6px;
    font-size: 14px;
}}
QPushButton.ThemeToggleBtn:hover {{
    background-color: {p["bg_card_hover"]};
    border-color: {p["accent"]};
}}

QPushButton.LangSidebarBtn {{
    background-color: {p["bg_card"]};
    color: {p["text_primary"]};
    border: 1px solid {p["border_card"]};
    border-radius: 8px;
    padding: 6px 4px;
    text-align: center;
    font-size: 11px;
    font-weight: bold;
}}
QPushButton.LangSidebarBtn:hover {{
    background-color: {p["bg_card_hover"]};
    border-color: {p["accent"]};
    color: {p["accent"]};
}}

/* Sidebar Status Card */
QFrame#StatusCard {{
    background-color: {p["bg_card"]};
    border: 1px solid {p["border_card"]};
    border-radius: 10px;
}}
QLabel#StatusCardTitle {{
    color: {p["text_primary"]};
    font-size: 11px;
    font-weight: bold;
}}
QLabel#StatusCardSubtitle {{
    color: {p["text_muted"]};
    font-size: 10px;
}}

/* Header Bar */
QWidget#HeaderBar {{
    background-color: transparent;
    border-bottom: 1px solid {p["border_sidebar"]};
}}

QLineEdit.SearchBox, QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: {p["input_bg"]};
    color: {p["text_primary"]};
    border: 1px solid {p["input_border"]};
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 12px;
}}
QLineEdit.SearchBox:focus, QLineEdit:focus, QComboBox:focus, QListWidget:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border: 1px solid {p["accent"]};
}}

/* Filter Chips */
QPushButton.FilterChip {{
    background-color: {p["input_bg"]};
    color: {p["text_secondary"]};
    border: 1px solid {p["input_border"]};
    border-radius: 6px;
    padding: 4px 12px;
    font-size: 11px;
    font-weight: 500;
}}
QPushButton.FilterChip:hover {{
    background-color: {p["bg_card"]};
    color: {p["text_primary"]};
}}
QPushButton.FilterChip[active="true"] {{
    background-color: {p["accent"]};
    color: {p["accent_text"]};
    font-weight: bold;
    border: none;
}}

/* Size Switcher Buttons */
QPushButton.SizeToggleBtn {{
    background-color: {p["input_bg"]};
    color: {p["text_secondary"]};
    border: 1px solid {p["input_border"]};
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 11px;
    font-weight: 500;
}}
QPushButton.SizeToggleBtn:hover {{
    background-color: {p["bg_card"]};
    color: {p["text_primary"]};
}}
QPushButton.SizeToggleBtn[active="true"] {{
    background-color: {p["accent"]};
    color: {p["accent_text"]};
    font-weight: bold;
    border: 1px solid {p["accent"]};
}}

/* Project Card */
QFrame.ProjectCard {{
    background-color: {p["bg_card"]};
    border: 1px solid {p["border_card"]};
    border-radius: 12px;
}}
QFrame.ProjectCard[layout="table"] {{
    border-radius: 8px;
}}
QFrame.ProjectCard:hover {{
    background-color: {p["bg_card_hover"]};
    border: 1px solid {p["border_card_hover"]};
}}
QFrame.ProjectCard[selected="true"] {{
    background-color: {p["bg_card_hover"]};
    border: 2px solid #38bdf8;
}}
QFrame.ProjectCard[layout="table"]:hover {{
    border-color: {p["accent"]};
}}
QFrame.ProjectCard[drop_target="true"] {{
    border: 2px dashed {p["accent"]};
    background-color: {p["bg_card_hover"]};
}}
QFrame.ProjectCard[archived="true"] {{
    background-color: {p["bg_canvas"]};
    border: 1px dashed {p["border_card"]};
}}
QFrame.ProjectCard[archived="true"][selected="true"] {{
    border: 2px solid #38bdf8;
}}

/* Hero Stage Frame (Idea 4.2 Dual-Deck) */
QFrame#HeroStageFrame {{
    background-color: {p["bg_card"]};
    border: 1px solid {p["border_card_hover"]};
    border-radius: 14px;
}}
QFrame#HeroInspectorBox {{
    background-color: {p["bg_canvas"]};
    border: 1px solid {p["border_card"]};
    border-radius: 10px;
}}

/* Table Header */
QFrame#TableHeader {{
    background-color: {p["bg_card"]};
    border: 1px solid {p["border_card"]};
    border-radius: 8px;
}}
QLabel.TableHeaderLabel {{
    color: {p["text_muted"]};
    font-size: 11px;
    font-weight: bold;
}}

/* Context Menu */
QMenu {{
    background-color: {p["menu_bg"]};
    color: {p["text_primary"]};
    border: 1px solid {p["menu_border"]};
    border-radius: 8px;
    padding: 5px;
}}
QMenu::item {{
    padding: 6px 18px;
    border-radius: 5px;
    font-size: 12px;
}}
QMenu::item:selected {{
    background-color: {p["menu_item_selected"]};
    color: {p["accent"]};
}}
QMenu::separator {{
    height: 1px;
    background: {p["border_sidebar"]};
    margin: 4px 6px;
}}

/* Status Pill */
QFrame.StatusPill {{
    background-color: {p["pill_bg"]};
    border-radius: 6px;
}}

/* Buttons on Card */
QPushButton.BtnTStudio {{
    background-color: {p["accent"]};
    color: {p["accent_text"]};
    border: none;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 11px;
    font-weight: bold;
}}
QPushButton.BtnTStudio:hover {{
    background-color: {p["accent_hover"]};
}}

QPushButton.BtnAI {{
    background-color: {p["ai_bg"]};
    color: {p["ai_text"]};
    border: 1px solid {p["ai_border"]};
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 11px;
    font-weight: bold;
}}
QPushButton.BtnAI:hover {{
    background-color: {p["ai_hover_bg"]};
    color: #ffffff;
}}

QPushButton.BtnFolder {{
    background-color: {p["secondary_btn"]};
    color: {p["secondary_btn_text"]};
    border: none;
    border-radius: 6px;
    padding: 6px 8px;
    font-size: 12px;
}}
QPushButton.BtnFolder:hover {{
    background-color: {p["secondary_btn_hover"]};
    color: {p["secondary_btn_hover_text"]};
}}

QPushButton.BtnMore {{
    background-color: {p["secondary_btn"]};
    color: {p["secondary_btn_text"]};
    border: none;
    border-radius: 6px;
    padding: 4px 6px;
    font-size: 13px;
    font-weight: bold;
}}
QPushButton.BtnMore:hover {{
    background-color: {p["secondary_btn_hover"]};
    color: {p["accent"]};
}}

/* Primary & Secondary Action Buttons */
QPushButton.BtnPrimary {{
    background-color: {p["primary_btn"]};
    color: {p["primary_btn_text"]};
    border: none;
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 12px;
    font-weight: bold;
}}
QPushButton.BtnPrimary:hover {{
    background-color: {p["primary_btn_hover"]};
}}

QPushButton.BtnSecondary {{
    background-color: {p["secondary_btn"]};
    color: {p["secondary_btn_text"]};
    border: 1px solid {p["secondary_btn_border"]};
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 12px;
}}
QPushButton.BtnSecondary:hover {{
    background-color: {p["secondary_btn_hover"]};
    color: {p["secondary_btn_hover_text"]};
}}

/* Form Elements (Dialogs, Tabs, Inputs) */
QTabWidget::pane {{
    border: 1px solid {p["tab_pane_border"]};
    border-radius: 8px;
    background-color: {p["tab_pane_bg"]};
    padding: 12px;
}}
QTabBar::tab {{
    background-color: {p["tab_bar_bg"]};
    color: {p["text_secondary"]};
    border: 1px solid {p["tab_pane_border"]};
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 8px 18px;
    margin-right: 4px;
    font-size: 12px;
    font-weight: bold;
}}
QTabBar::tab:selected {{
    background-color: {p["tab_pane_bg"]};
    color: {p["accent"]};
    border-bottom: 2px solid {p["accent"]};
}}

QComboBox, QListWidget {{
    background-color: {p["input_bg"]};
    color: {p["text_primary"]};
    border: 1px solid {p["input_border"]};
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
}}
QComboBox QAbstractItemView {{
    background-color: {p["menu_bg"]};
    color: {p["text_primary"]};
    border: 1px solid {p["menu_border"]};
    selection-background-color: {p["menu_item_selected"]};
    selection-color: {p["accent"]};
}}
QListWidget::item:selected {{
    background-color: {p["menu_item_selected"]};
    color: {p["accent"]};
}}
QCheckBox {{
    color: {p["text_primary"]};
    font-size: 12px;
}}

/* Sliders */
QSlider::groove:horizontal {{
    height: 6px;
    background: {p["border_card"]};
    border-radius: 3px;
}}
QSlider::sub-page:horizontal {{
    background: {p["accent"]};
    border-radius: 3px;
}}
QSlider::handle:horizontal {{
    background: {p["text_primary"]};
    border: 2px solid {p["accent"]};
    width: 14px;
    margin-top: -4px;
    margin-bottom: -4px;
    border-radius: 7px;
}}

/* Modern Scrollbars */
QScrollArea, QScrollArea > QWidget > QWidget {{
    background: transparent;
    border: none;
}}
QScrollBar:vertical {{
    background: transparent;
    width: 8px;
    margin: 0px;
}}
QScrollBar::handle:vertical {{
    background: {p["scrollbar_thumb"]};
    min-height: 24px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical:hover {{
    background: {p["scrollbar_thumb_hover"]};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: transparent;
}}
"""

# Default / backward compatibility
OBSIDIAN_STYLESHEET = get_theme_stylesheet("Dark")
