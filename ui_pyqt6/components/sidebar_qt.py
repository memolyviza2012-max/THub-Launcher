import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, pyqtSignal
from i18n_helper import _
from ui_pyqt6.components.sidebar_storage_qt import SidebarStorageWidget

class SidebarQt(QWidget):
    """
    DLSS Swapper-inspired Navigation Sidebar in PyQt6.
    Streamlined navigation without unused settings.
    """

    navigated = pyqtSignal(str)
    theme_picker_clicked = pyqtSignal()
    theme_toggle_clicked = pyqtSignal()
    lang_toggle_clicked = pyqtSignal()
    lang_selected = pyqtSignal(str)
    project_selected = pyqtSignal(dict)
    sort_size_requested = pyqtSignal()
    refresh_requested = pyqtSignal()
    move_queue_requested = pyqtSignal()

    def __init__(self, current_route="dashboard", current_theme="Dark", parent=None):
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setFixedWidth(230)
        self.current_route = current_route
        self.current_theme_name = current_theme
        self.nav_buttons = {}

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 20, 14, 16)
        layout.setSpacing(4)

        # 1. Branding Header
        brand_row = QHBoxLayout()
        brand_row.setContentsMargins(4, 0, 4, 16)
        brand_row.setSpacing(10)

        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        logo_path = os.path.join(base_dir, "assets", "THub.png")

        if os.path.exists(logo_path):
            lbl_logo = QLabel()
            lbl_logo.setFixedSize(36, 36)
            pix = QPixmap(logo_path).scaled(36, 36, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            lbl_logo.setPixmap(pix)
            brand_row.addWidget(lbl_logo)

        brand_text_col = QVBoxLayout()
        brand_text_col.setSpacing(1)

        title_row = QHBoxLayout()
        title_row.setSpacing(5)
        title_row.setContentsMargins(0, 0, 0, 0)

        lbl_title = QLabel("THub")
        lbl_title.setObjectName("SidebarTitle")
        title_row.addWidget(lbl_title)

        lbl_ver = QLabel("2.2")
        lbl_ver.setObjectName("SidebarVersion")
        title_row.addWidget(lbl_ver)
        title_row.addStretch()

        brand_text_col.addLayout(title_row)

        lbl_sub = QLabel("FLAGSHIP MODDER SUITE")
        lbl_sub.setStyleSheet("color: #38bdf8; font-size: 8px; font-weight: bold; letter-spacing: 1px;")
        brand_text_col.addWidget(lbl_sub)

        brand_row.addLayout(brand_text_col)
        brand_row.addStretch()
        layout.addLayout(brand_row)

        # 2. Navigation Items
        self.menu_defs = [
            ("dashboard", "📊", "Dashboard (หน้าหลัก)"),
            ("ai_helper", "🤖", "AI Helper Copilot"),
            ("apps",      "✨", "THub Apps"),
            ("knowledge", "📚", "คลังความรู้ (Docs)"),
            ("settings",  "⚙️", "การตั้งค่าระบบ")
        ]

        for route_id, icon, label_key in self.menu_defs:
            btn = QPushButton(f"  {icon}  {_(label_key)}")
            btn.setProperty("class", "NavBtn")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            is_active = (route_id == self.current_route)
            btn.setProperty("active", "true" if is_active else "false")
            btn.clicked.connect(lambda _, r=route_id: self._on_nav(r))
            layout.addWidget(btn)
            self.nav_buttons[route_id] = btn

        layout.addSpacing(6)

        # 3. Storage Analytics Cockpit (Directly under Settings, fills full vertical area)
        self.storage_widget = SidebarStorageWidget(self)
        self.storage_widget.project_selected.connect(self.project_selected.emit)
        self.storage_widget.sort_size_requested.connect(self.sort_size_requested.emit)
        self.storage_widget.refresh_requested.connect(self.refresh_requested.emit)
        self.storage_widget.move_queue_requested.connect(self.move_queue_requested.emit)
        layout.addWidget(self.storage_widget, stretch=1)

        layout.addSpacing(4)

        # 4. Bottom-Left Theme & Language Switcher Controls
        bottom_row = QHBoxLayout()
        bottom_row.setContentsMargins(0, 4, 0, 0)
        bottom_row.setSpacing(5)

        # Theme Picker Button
        self.btn_theme_picker = QPushButton()
        self.btn_theme_picker.setProperty("class", "ThemeSidebarBtn")
        self.btn_theme_picker.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_theme_picker.setToolTip(_("คลิกเพื่อเปิดเมนูเลือกธีมทั้งหมด 21 ธีม"))
        self.btn_theme_picker.clicked.connect(self.theme_picker_clicked.emit)
        bottom_row.addWidget(self.btn_theme_picker, stretch=1)

        # Theme Quick Toggle (Dark / Light)
        self.btn_theme_toggle = QPushButton("🌓")
        self.btn_theme_toggle.setProperty("class", "ThemeToggleBtn")
        self.btn_theme_toggle.setFixedSize(30, 32)
        self.btn_theme_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_theme_toggle.setToolTip(_("สลับโหมด มืด / สว่าง ทันที (Toggle Dark / Light)"))
        self.btn_theme_toggle.clicked.connect(self.theme_toggle_clicked.emit)
        bottom_row.addWidget(self.btn_theme_toggle)

        # Language Switcher Button (Right beside theme!)
        self.btn_lang = QPushButton()
        self.btn_lang.setProperty("class", "LangSidebarBtn")
        self.btn_lang.setFixedSize(62, 32)
        self.btn_lang.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_lang.setToolTip(_("คลิก: สลับภาษา (ไทย ⇄ English) ทันที\nคลิกขวา: เลือกภาษาอื่นๆ"))
        self.btn_lang.clicked.connect(self.lang_toggle_clicked.emit)
        self.btn_lang.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.btn_lang.customContextMenuRequested.connect(self._show_lang_context_menu)
        bottom_row.addWidget(self.btn_lang)

        layout.addLayout(bottom_row)

        self.update_theme_display(self.current_theme_name)
        self.update_lang_display()

    def update_theme_display(self, theme_name: str):
        """Update button label to show active theme name with proper capitalization."""
        self.current_theme_name = theme_name or "Dark"
        display_map = {
            "dark": "Dark", "dracula": "Dracula", "mocha": "Mocha",
            "ember": "Ember", "rose pine": "Rosé Pine", "moonlight": "Moonlight",
            "slate": "Slate", "midnight": "Midnight", "nord": "Nord",
            "light": "Light", "alucard": "Alucard", "latte": "Latte",
            "ember light": "Ember Light", "rose pine dawn": "Rosé Pine Dawn",
            "sunshine": "Sunshine", "indigo": "Indigo", "ocean": "Ocean",
            "forest": "Forest", "rose": "Rose", "lavender": "Lavender",
            "monochrome": "Monochrome", "auto": "Auto", "random": "Random",
            "obsidian": "Dark"
        }
        disp = display_map.get(str(self.current_theme_name).lower(), str(self.current_theme_name).capitalize())
        self.btn_theme_picker.setText(f"🎨 {_('ธีม')}: {disp} ▾")

    def update_lang_display(self, lang_code=None):
        """Update language button text to reflect active language."""
        lang = (lang_code or os.environ.get("THUB_LANG", "th")).lower()
        if lang == "th":
            self.btn_lang.setText("🌐 ไทย")
        elif lang == "en":
            self.btn_lang.setText("🌐 EN")
        elif lang == "ja":
            self.btn_lang.setText("🌐 日本語")
        elif lang == "zh":
            self.btn_lang.setText("🌐 中文")
        else:
            self.btn_lang.setText(f"🌐 {lang.upper()}")

    def _show_lang_context_menu(self, pos):
        """Show context menu on right-click to pick from all available languages."""
        from PyQt6.QtWidgets import QMenu
        menu = QMenu(self)
        langs = [
            ("th", "🇹🇭 ภาษาไทย (Thai)"),
            ("en", "🇬🇧 English (US)"),
            ("ja", "🇯🇵 日本語 (Japanese)"),
            ("zh", "🇨🇳 简体中文 (Chinese)"),
        ]
        current_lang = os.environ.get("THUB_LANG", "th")
        for code, label in langs:
            action = menu.addAction(label)
            if code == current_lang:
                action.setCheckable(True)
                action.setChecked(True)
            action.triggered.connect(lambda checked, c=code: self.lang_selected.emit(c))
        menu.exec(self.btn_lang.mapToGlobal(pos))

    def retranslate_ui(self):
        """Update navigation labels when language changes dynamically."""
        for route_id, icon, label_key in self.menu_defs:
            if route_id in self.nav_buttons:
                self.nav_buttons[route_id].setText(f"  {icon}  {_(label_key)}")
        if hasattr(self, 'lbl_ready'):
            self.lbl_ready.setText(_("พร้อมใช้งาน (Ready)"))
        self.update_theme_display(self.current_theme_name)
        self.update_lang_display()
        if hasattr(self, 'btn_theme_picker'):
            self.btn_theme_picker.setToolTip(_("คลิกเพื่อเปิดเมนูเลือกธีมทั้งหมด 21 ธีม"))
        if hasattr(self, 'btn_theme_toggle'):
            self.btn_theme_toggle.setToolTip(_("สลับโหมด มืด / สว่าง ทันที (Toggle Dark / Light)"))
        if hasattr(self, 'btn_lang'):
            self.btn_lang.setToolTip(_("คลิก: สลับภาษา (ไทย ⇄ English) ทันที\nคลิกขวา: เลือกภาษาอื่นๆ"))

    def _on_nav(self, route_id):
        self.set_active(route_id)
        self.navigated.emit(route_id)

    def set_active(self, route_id):
        self.current_route = route_id
        for r_id, btn in self.nav_buttons.items():
            is_active = (r_id == route_id)
            btn.setProperty("active", "true" if is_active else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def update_storage_data(self, project_sizes):
        """Passes project storage sizes to the sidebar storage card."""
        if hasattr(self, "storage_widget") and self.storage_widget:
            self.storage_widget.update_storage_data(project_sizes)

    def set_storage_scanning(self, is_scanning):
        """Toggles scanning hairline progress bar in sidebar storage card."""
        if hasattr(self, "storage_widget") and self.storage_widget:
            self.storage_widget.set_scanning(is_scanning)

    def set_storage_progress(self, current, total):
        """Updates scan progress in sidebar storage card."""
        if hasattr(self, "storage_widget") and self.storage_widget:
            self.storage_widget.set_progress(current, total)
