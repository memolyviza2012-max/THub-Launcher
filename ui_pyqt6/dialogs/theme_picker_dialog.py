"""
THub Theme Picker Dialog / Popup
================================
Interactive 2-column theme selection popup matching the flagship theme switcher UI.
Features 21 curated dark and light themes, plus Auto OS detection and Randomizer.
"""

import random
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QApplication, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QByteArray
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt6.QtSvg import QSvgRenderer
from i18n_helper import _
from ui_pyqt6.theme_qss import get_theme_palette

# ── SVGs for Theme Icons (Lucide Outline Style) ────────────────────────────────
THEME_ICONS_SVG = {
    # Actions
    "auto": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>''',
    "random": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 3h5v5M4 20L21 3M21 16v5h-5M15 15l6 6M4 4l5 5"/></svg>''',
    
    # Dark Themes (9)
    "dark": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>''',
    "dracula": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 10h.01M15 10h.01M12 2a8 8 0 0 0-8 8v12l3-3 2.5 2.5L12 19l2.5 2.5L17 19l3 3V10a8 8 0 0 0-8-8z"/></svg>''',
    "mocha": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 8h1a4 4 0 1 1 0 8h-1M3 8h14v9a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4Z"/><line x1="6" y1="2" x2="6" y2="4"/><line x1="10" y1="2" x2="10" y2="4"/><line x1="14" y1="2" x2="14" y2="4"/></svg>''',
    "ember": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/></svg>''',
    "rose pine": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 4 12 7 12 3 18 10 18 10 22 14 22 14 18 21 18 17 12 20 12 12 2"/></svg>''',
    "moonlight": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/><path d="M19 16a3 3 0 1 1-6 0c0-.3.05-.6.13-.88A4 4 0 1 1 19 16Z"/></svg>''',
    "slate": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>''',
    "midnight": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242"/><path d="M8 19v2"/><path d="M8 13v2"/><path d="M16 19v2"/><path d="M16 13v2"/><path d="M12 21v2"/><path d="M12 15v2"/></svg>''',
    "nord": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m8 3 4 8 5-5 5 15H2L8 3z"/></svg>''',

    # Light Themes (12)
    "light": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>''',
    "alucard": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/></svg>''',
    "latte": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 2h8"/><path d="M9 2v3a4 4 0 0 1-.8 2.4L7 9a6 6 0 0 0-1 3.4V19a3 3 0 0 0 3 3h6a3 3 0 0 0 3-3v-6.6a6 6 0 0 0-1-3.4l-1.2-1.6A4 4 0 0 1 15 5V2"/></svg>''',
    "ember light": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 10V2"/><path d="m4.93 10.93 1.41-1.41"/><path d="M2 18h2"/><path d="M20 18h2"/><path d="m19.07 10.93-1.41-1.41"/><path d="M22 22H2"/><path d="m16 6-4 4-4-4"/><path d="M16 18a4 4 0 0 0-8 0"/>''',
    "rose pine dawn": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 20h10"/><path d="M10 20c5.5-2.5.8-6.4 3-10"/><path d="M9.5 9.4c1.1.8 1.8 2.2 2.3 3.7-2 .4-3.5.4-4.8-.3-1.2-.6-2.3-1.9-3-4.2 2.8-.5 4.4.1 5.5.8z"/><path d="M14.1 6a7 7 0 0 0-1.1 4c1.9-.1 3.3-.6 4.3-1.4 1-1 1.6-2.3 1.7-4.6-2.7.1-4 1-4.9 2z"/></svg>''',
    "sunshine": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v8"/><path d="m4.93 10.93 1.41-1.41"/><path d="M2 18h2"/><path d="M20 18h2"/><path d="m19.07 10.93-1.41-1.41"/><path d="M22 22H2"/><path d="m8 6 4-4 4 4"/><path d="M16 18a4 4 0 0 0-8 0"/></svg>''',
    "indigo": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/></svg>''',
    "ocean": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 6c.6.5 1.2 1 2.5 1C7 7 7 5 9.5 5c2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/><path d="M2 12c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/><path d="M2 18c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/></svg>''',
    "forest": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19v3"/><path d="M18 10a6 6 0 0 0-12 0c0 1.88.87 3.55 2.22 4.63A4.5 4.5 0 0 0 15 19h.5a4.5 4.5 0 0 0 2.5-8.24V10z"/></svg>''',
    "rose": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M12 16.5A4.5 4.5 0 1 1 7.5 12 4.5 4.5 0 1 1 12 7.5a4.5 4.5 0 1 1 4.5 4.5 4.5 4.5 0 1 1-4.5 4.5"/><path d="M12 7.5V9"/><path d="M7.5 12H9"/><path d="M16.5 12H15"/><path d="M12 16.5V15"/></svg>''',
    "lavender": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a4 4 0 0 0-4 4c0 1.48.8 2.77 2 3.46V22h4V9.46c1.2-.69 2-1.98 2-3.46a4 4 0 0 0-4-4Z"/><path d="M8 14h8"/><path d="M8 18h8"/></svg>''',
    "monochrome": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 2a10 10 0 0 0 0 20Z" fill="currentColor"/></svg>'''
}

DARK_THEMES = [
    ("dark", "Dark"),
    ("dracula", "Dracula"),
    ("mocha", "Mocha"),
    ("ember", "Ember"),
    ("rose pine", "Rosé Pine"),
    ("moonlight", "Moonlight"),
    ("slate", "Slate"),
    ("midnight", "Midnight"),
    ("nord", "Nord"),
]

LIGHT_THEMES = [
    ("light", "Light"),
    ("alucard", "Alucard"),
    ("latte", "Latte"),
    ("ember light", "Ember Light"),
    ("rose pine dawn", "Rosé Pine Dawn"),
    ("sunshine", "Sunshine"),
    ("indigo", "Indigo"),
    ("ocean", "Ocean"),
    ("forest", "Forest"),
    ("rose", "Rose"),
    ("lavender", "Lavender"),
    ("monochrome", "Monochrome"),
]

ALL_THEME_KEYS = [k for k, _ in DARK_THEMES] + [k for k, _ in LIGHT_THEMES]


def _render_svg_icon(svg_str: str, color: str = "#cbd5e1", size: int = 18) -> QIcon:
    """Render an SVG string into a crisp QIcon with the specified stroke/fill color."""
    if not svg_str:
        return QIcon()
    svg_colored = svg_str.replace("currentColor", color)
    renderer = QSvgRenderer(QByteArray(svg_colored.encode("utf-8")))
    pix = QPixmap(size, size)
    pix.fill(QColor(0, 0, 0, 0))
    painter = QPainter(pix)
    renderer.render(painter)
    painter.end()
    return QIcon(pix)


class ThemeItemButton(QPushButton):
    """Custom styled button for each theme item."""

    def __init__(self, key: str, label: str, svg_raw: str, palette=None, is_active: bool = False, parent=None):
        super().__init__(parent)
        self.key = key
        self.raw_label = label
        self.svg_raw = svg_raw
        self.palette = palette or {}
        self.is_active = is_active
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(34)
        self.update_appearance(is_active)

    def update_appearance(self, is_active: bool, palette=None):
        if palette:
            self.palette = palette
        self.is_active = is_active
        p = self.palette
        text_color = "#ffffff" if is_active else p.get("text_primary", "#cbd5e1")
        accent = p.get("accent", "#2563eb")
        accent_hover = p.get("accent_hover", "#1d4ed8")
        bg_hover = p.get("bg_card_hover", "#232a3b")
        self.setIcon(_render_svg_icon(self.svg_raw, color=text_color, size=18))
        self.setText(f" {self.raw_label}")

        if is_active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {accent};
                    color: #ffffff;
                    border: none;
                    border-radius: 6px;
                    text-align: left;
                    padding-left: 10px;
                    padding-right: 10px;
                    font-size: 13px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {accent_hover};
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {text_color};
                    border: none;
                    border-radius: 6px;
                    text-align: left;
                    padding-left: 10px;
                    padding-right: 10px;
                    font-size: 13px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: {bg_hover};
                    color: {p.get("text_primary", "#ffffff")};
                }}
            """)


class ThemePickerDialog(QDialog):
    """
    Theme Picker Popup/Dialog.
    Shows Dark & Light theme columns with instant preview and live application.
    """

    theme_selected = pyqtSignal(str)

    def __init__(self, current_theme: str = "dark", parent=None):
        super().__init__(parent, Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setObjectName("ThemePickerDialog")
        self.current_theme = (current_theme or "dark").strip().lower()
        if self.current_theme == "obsidian":
            self.current_theme = "dark"
        self.palette = get_theme_palette(self.current_theme)

        self.buttons = {}
        self._build_ui()

    def _build_ui(self):
        p = self.palette
        # Outer container for rounded background and drop shadow
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(10, 10, 10, 10)

        container = QWidget(self)
        container.setObjectName("ThemeContainer")
        container.setStyleSheet(f"""
            QWidget#ThemeContainer {{
                background-color: {p.get("bg_card", "#181b22")};
                border: 1px solid {p.get("border_card", "#282e3d")};
                border-radius: 12px;
            }}
        """)

        # Drop shadow effect
        shadow = QGraphicsDropShadowEffect(container)
        shadow.setBlurRadius(24)
        shadow.setColor(QColor(0, 0, 0, 160))
        shadow.setOffset(0, 8)
        container.setGraphicsEffect(shadow)

        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(12)

        # ── Top Row: Auto & Random ─────────────────────────────────────────────
        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        # Auto Button
        is_auto = self.current_theme in ("auto", "system")
        self.btn_auto = QPushButton(" Auto")
        self.btn_auto.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_auto.setFixedHeight(36)
        self._style_pill_btn(self.btn_auto, "auto", is_active=is_auto)
        self.btn_auto.clicked.connect(lambda: self._on_select("auto"))
        top_row.addWidget(self.btn_auto)

        # Random Button
        self.btn_random = QPushButton(" Random")
        self.btn_random.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_random.setFixedHeight(36)
        self._style_pill_btn(self.btn_random, "random", is_active=False)
        self.btn_random.clicked.connect(self._on_random_click)
        top_row.addWidget(self.btn_random)

        main_layout.addLayout(top_row)

        # ── Columns: Dark Themes & Light Themes ────────────────────────────────
        cols_row = QHBoxLayout()
        cols_row.setSpacing(14)

        # Column 1: Dark Themes
        col_dark = QVBoxLayout()
        col_dark.setSpacing(3)
        lbl_dark_header = QLabel("DARK THEMES")
        lbl_dark_header.setStyleSheet(f"color: {p.get('text_muted', '#717b91')}; font-size: 11px; font-weight: bold; padding-left: 6px; padding-bottom: 2px;")
        col_dark.addWidget(lbl_dark_header)

        for key, name in DARK_THEMES:
            svg = THEME_ICONS_SVG.get(key, "")
            is_active = (self.current_theme == key)
            btn = ThemeItemButton(key, name, svg, palette=self.palette, is_active=is_active)
            btn.clicked.connect(lambda checked, k=key: self._on_select(k))
            self.buttons[key] = btn
            col_dark.addWidget(btn)

        col_dark.addStretch()
        cols_row.addLayout(col_dark)

        # Column 2: Light Themes
        col_light = QVBoxLayout()
        col_light.setSpacing(3)
        lbl_light_header = QLabel("LIGHT THEMES")
        lbl_light_header.setStyleSheet(f"color: {p.get('text_muted', '#717b91')}; font-size: 11px; font-weight: bold; padding-left: 6px; padding-bottom: 2px;")
        col_light.addWidget(lbl_light_header)

        for key, name in LIGHT_THEMES:
            svg = THEME_ICONS_SVG.get(key, "")
            is_active = (self.current_theme == key)
            btn = ThemeItemButton(key, name, svg, palette=self.palette, is_active=is_active)
            btn.clicked.connect(lambda checked, k=key: self._on_select(k))
            self.buttons[key] = btn
            col_light.addWidget(btn)

        cols_row.addLayout(col_light)
        main_layout.addLayout(cols_row)

        outer_layout.addWidget(container)
        self.setFixedWidth(330)

    def _style_pill_btn(self, btn: QPushButton, icon_key: str, is_active: bool):
        p = self.palette
        text_color = "#ffffff" if is_active else p.get("text_primary", "#cbd5e1")
        accent = p.get("accent", "#2563eb")
        accent_hover = p.get("accent_hover", "#1d4ed8")
        btn_bg = p.get("secondary_btn", "#202430")
        btn_border = p.get("secondary_btn_border", "#2e3547")
        btn_hover = p.get("secondary_btn_hover", "#2a3142")

        btn.setIcon(_render_svg_icon(THEME_ICONS_SVG.get(icon_key, ""), color=text_color, size=18))
        if is_active:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {accent};
                    color: #ffffff;
                    border: none;
                    border-radius: 8px;
                    font-size: 13px;
                    font-weight: bold;
                    padding: 6px 14px;
                }}
                QPushButton:hover {{
                    background-color: {accent_hover};
                }}
            """)
        else:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {btn_bg};
                    color: {text_color};
                    border: 1px solid {btn_border};
                    border-radius: 8px;
                    font-size: 13px;
                    font-weight: 500;
                    padding: 6px 14px;
                }}
                QPushButton:hover {{
                    background-color: {btn_hover};
                    color: {p.get("text_primary", "#ffffff")};
                }}
            """)

    def _on_select(self, key: str):
        self.current_theme = key
        self._update_selection_visuals(key)
        self.theme_selected.emit(key)
        self.accept()

    def _on_random_click(self):
        chosen = random.choice(ALL_THEME_KEYS)
        self.current_theme = chosen
        self._update_selection_visuals(chosen)
        self.theme_selected.emit(chosen)
        self.accept()

    def _update_selection_visuals(self, active_key: str):
        self._style_pill_btn(self.btn_auto, "auto", is_active=(active_key == "auto"))
        for k, btn in self.buttons.items():
            btn.update_appearance(is_active=(k == active_key), palette=self.palette)

    def show_at_widget(self, anchor_widget: QWidget):
        """Position the popup cleanly near the anchor widget (upwards if near bottom)."""
        self.adjustSize()
        if anchor_widget:
            screen = QApplication.primaryScreen().availableGeometry()
            win = anchor_widget.window()

            # Check if anchor is located in the bottom half of the parent window
            anchor_in_win = anchor_widget.mapTo(win, QPoint(0, 0))
            is_bottom = anchor_in_win.y() > (win.height() / 2)

            if is_bottom:
                # Position popup above the button
                pos = anchor_widget.mapToGlobal(QPoint(0, -self.height() - 6))
            else:
                # Position popup below the button
                pos = anchor_widget.mapToGlobal(QPoint(0, anchor_widget.height() + 6))

            x = pos.x()
            y = pos.y()

            # Ensure popup fits within screen bounds
            if x + self.width() > screen.right():
                x = screen.right() - self.width() - 8
            if x < screen.left():
                x = screen.left() + 8

            if y + self.height() > screen.bottom():
                y = screen.bottom() - self.height() - 8
            if y < screen.top():
                y = screen.top() + 8

            self.move(x, y)
        self.exec()
