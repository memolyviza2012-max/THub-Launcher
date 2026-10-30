from core.qt_tasks import BackgroundTasks, TaskDialogMixin
import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTabWidget, QWidget, QFileDialog, QMessageBox, QListWidget, QCheckBox,
    QComboBox, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from core.config_manager import ConfigManager
from core.game_scanner import GameScanner
from ui_pyqt6.theme_qss import get_theme_stylesheet
from i18n_helper import _, set_language

class SettingsDialogQt(TaskDialogMixin, QDialog):
    """
    Global THub Settings Dialog in PyQt6.
    Allows configuring permanent workspace dir, permanent tools dir,
    game library scan paths, default author, theme, and language.
    """
    settings_saved = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tasks = BackgroundTasks(self)
        self.cfg = ConfigManager()
        self.game_scanner = GameScanner.get_instance()

        active_theme = self.cfg.get("active_theme", "Obsidian")
        self.setStyleSheet(get_theme_stylesheet(active_theme))

        self.setWindowTitle(_("⚙️ การตั้งค่าระบบ THub (Global Settings)"))
        self.setFixedSize(650, 560)

        self._build_ui()
        self._load_current_settings()

    def _build_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(20, 16, 20, 16)
        root_layout.setSpacing(12)

        # Header Title
        header_col = QVBoxLayout()
        header_col.setSpacing(2)
        lbl_title = QLabel(_("⚙️ การตั้งค่า THub Launcher"))
        lbl_title.setProperty("class", "PageTitle")
        lbl_sub = QLabel(_("กำหนดตำแหน่งโฟลเดอร์หลัก คลังสแกนเกมในเครื่อง และค่าเริ่มต้นของโปรแกรม"))
        lbl_sub.setProperty("class", "SubText")
        header_col.addWidget(lbl_title)
        header_col.addWidget(lbl_sub)
        root_layout.addLayout(header_col)

        # Tab Widget
        self.tabs = QTabWidget()

        # Tab 1: Paths & Workspaces
        tab_paths = QWidget()
        self._build_paths_tab(tab_paths)
        self.tabs.addTab(tab_paths, _("📁 ตำแหน่งโฟลเดอร์หลัก"))

        # Tab 2: Game Libraries & Scanner
        tab_scanner = QWidget()
        self._build_scanner_tab(tab_scanner)
        self.tabs.addTab(tab_scanner, _("🎮 คลังเกมและตัวสแกน"))

        # Tab 3: General Settings
        tab_general = QWidget()
        self._build_general_tab(tab_general)
        self.tabs.addTab(tab_general, _("🎨 ทั่วไป & ธีม"))

        root_layout.addWidget(self.tabs, stretch=1)

        # Bottom Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        btn_cancel = QPushButton(_("ยกเลิก"))
        btn_cancel.setProperty("class", "BtnSecondary")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_cancel)

        btn_row.addStretch()

        btn_save = QPushButton(_("💾 บันทึกการตั้งค่า"))
        btn_save.setProperty("class", "BtnPrimary")
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.clicked.connect(self._save_settings)
        btn_row.addWidget(btn_save)

        root_layout.addLayout(btn_row)

    def _build_paths_tab(self, parent):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(12, 14, 12, 14)
        layout.setSpacing(14)

        # 1. Default Workspace Directory
        box_ws = QVBoxLayout()
        box_ws.setSpacing(4)
        lbl_ws = QLabel(_("📂 ตำแหน่งโฟลเดอร์โปรเจกต์ถาวร (Default Workspace Directory):"))
        lbl_ws.setProperty("class", "CardTitle")
        box_ws.addWidget(lbl_ws)

        lbl_ws_desc = QLabel(_("เมื่อเริ่มสร้างโปรเจกต์ใหม่ ระบบจะสร้างโฟลเดอร์ในตำแหน่งนี้โดยอัตโนมัติ (เช่น E:\\Mod_Workspace\\GameName)"))
        lbl_ws_desc.setProperty("class", "SubText")
        box_ws.addWidget(lbl_ws_desc)

        row_ws = QHBoxLayout()
        self.ent_default_ws = QLineEdit()
        self.ent_default_ws.setPlaceholderText("เช่น E:\\Mod_Workspace")
        btn_browse_ws = QPushButton(_("📂 เลือก"))
        btn_browse_ws.setProperty("class", "BtnSecondary")
        btn_browse_ws.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_browse_ws.clicked.connect(self._browse_default_ws)
        row_ws.addWidget(self.ent_default_ws, stretch=1)
        row_ws.addWidget(btn_browse_ws)
        box_ws.addLayout(row_ws)
        layout.addLayout(box_ws)

        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setProperty("class", "InnerCard")
        layout.addWidget(line)

        # 2. Default Tools Directory
        box_tool = QVBoxLayout()
        box_tool.setSpacing(4)
        lbl_tool = QLabel(_("🛠️ ตำแหน่งเครื่องมือถาวร (Default Tools Directory):"))
        lbl_tool.setProperty("class", "CardTitle")
        box_tool.addWidget(lbl_tool)

        lbl_tool_desc = QLabel(_("โฟลเดอร์จัดเก็บชุดเครื่องมือ Modding ส่วนกลาง เช่น TStudio, TPUA, โปรแกรมแกะไฟล์ ฯลฯ"))
        lbl_tool_desc.setProperty("class", "SubText")
        box_tool.addWidget(lbl_tool_desc)

        row_tool = QHBoxLayout()
        self.ent_default_tools = QLineEdit()
        self.ent_default_tools.setPlaceholderText("เช่น E:\\Mod_Workspace\\Tool")
        btn_browse_tool = QPushButton(_("📂 เลือก"))
        btn_browse_tool.setProperty("class", "BtnSecondary")
        btn_browse_tool.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_browse_tool.clicked.connect(self._browse_default_tools)
        row_tool.addWidget(self.ent_default_tools, stretch=1)
        row_tool.addWidget(btn_browse_tool)
        box_tool.addLayout(row_tool)
        layout.addLayout(box_tool)

        layout.addStretch()

    def _build_scanner_tab(self, parent):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(12, 14, 12, 14)
        layout.setSpacing(10)

        lbl_scan_info = QLabel(_("🎮 คลังเกมในเครื่องที่เปิดให้ระบบสแกนอัตโนมัติ:"))
        lbl_scan_info.setProperty("class", "CardTitle")
        layout.addWidget(lbl_scan_info)

        lbl_desc = QLabel(_("ระบบจะตรวจจับ Steam Libraries ทุกไดรฟ์โดยอัตโนมัติ และคุณสามารถเพิ่มโฟลเดอร์ติดตั้งเกมอื่นๆ เพิ่มเติมได้ที่นี่"))
        lbl_desc.setProperty("class", "SubText")
        layout.addWidget(lbl_desc)

        # List of library paths
        self.list_libraries = QListWidget()
        self.list_libraries.setFixedHeight(140)
        layout.addWidget(self.list_libraries)

        # Add / Remove Custom Library Buttons
        btn_lib_row = QHBoxLayout()
        btn_add_lib = QPushButton(_("➕ เพิ่มโฟลเดอร์คลังเกม"))
        btn_add_lib.setProperty("class", "BtnSecondary")
        btn_add_lib.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add_lib.clicked.connect(self._add_custom_library)

        btn_remove_lib = QPushButton(_("🗑️ ลบโฟลเดอร์ที่เลือก"))
        btn_remove_lib.setProperty("class", "BtnSecondary")
        btn_remove_lib.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_remove_lib.clicked.connect(self._remove_custom_library)

        btn_lib_row.addWidget(btn_add_lib)
        btn_lib_row.addWidget(btn_remove_lib)
        btn_lib_row.addStretch()
        layout.addLayout(btn_lib_row)

        # Scanner Stats Card
        stats_card = QFrame()
        stats_card.setProperty("class", "InnerCard")
        stats_layout = QHBoxLayout(stats_card)
        stats_layout.setContentsMargins(14, 10, 14, 10)

        self.lbl_game_count = QLabel(_("🎮 กำลังตรวจนับเกมในเครื่อง..."))
        self.lbl_game_count.setProperty("class", "CardTitle")
        stats_layout.addWidget(self.lbl_game_count)

        stats_layout.addStretch()

        btn_refresh_scan = QPushButton(_("🔄 สแกนใหม่"))
        btn_refresh_scan.setProperty("class", "BtnPrimary")
        btn_refresh_scan.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_refresh_scan.clicked.connect(self._refresh_scanner_stats)
        stats_layout.addWidget(btn_refresh_scan)

        layout.addWidget(stats_card)
        layout.addStretch()

    def _build_general_tab(self, parent):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(12, 14, 12, 14)
        layout.setSpacing(14)

        # Default Author
        box_author = QVBoxLayout()
        box_author.setSpacing(4)
        box_author.addWidget(QLabel(_("ชื่อผู้แปลเริ่มต้น (Default Author):")))
        self.ent_author = QLineEdit()
        self.ent_author.setPlaceholderText("ชื่อหรือนามแฝงของคุณ...")
        box_author.addWidget(self.ent_author)
        layout.addLayout(box_author)

        # App Theme
        box_theme = QVBoxLayout()
        box_theme.setSpacing(6)
        box_theme.addWidget(QLabel(_("ธีมสีของแอปพลิเคชัน (Active Theme):")))

        theme_row = QHBoxLayout()
        theme_row.setSpacing(8)

        self.cbo_theme = QComboBox()
        self.cbo_theme.addItem(_("🖥️ Auto (ตามระบบปฏิบัติการ)"), "auto")
        self.cbo_theme.addItem(_("🔀 Random (สุ่มธีม)"), "random")

        # Dark Themes
        self.cbo_theme.addItem(_("── ธีมมืด (Dark Themes) ──"), None)
        dark_themes = [
            ("Dark", "dark"),
            ("Dracula", "dracula"),
            ("Mocha", "mocha"),
            ("Ember", "ember"),
            ("Rosé Pine", "rose pine"),
            ("Moonlight", "moonlight"),
            ("Slate", "slate"),
            ("Midnight", "midnight"),
            ("Nord", "nord"),
        ]
        for name, key in dark_themes:
            self.cbo_theme.addItem(f"🌙 {name}", key)

        # Light Themes
        self.cbo_theme.addItem(_("── ธีมสว่าง (Light Themes) ──"), None)
        light_themes = [
            ("Light", "light"),
            ("Alucard", "alucard"),
            ("Latte", "latte"),
            ("Ember Light", "ember light"),
            ("Rosé Pine Dawn", "rose pine dawn"),
            ("Sunshine", "sunshine"),
            ("Indigo", "indigo"),
            ("Ocean", "ocean"),
            ("Forest", "forest"),
            ("Rose", "rose"),
            ("Lavender", "lavender"),
            ("Monochrome", "monochrome"),
        ]
        for name, key in light_themes:
            self.cbo_theme.addItem(f"☀️ {name}", key)

        theme_row.addWidget(self.cbo_theme, stretch=1)

        btn_open_picker = QPushButton(_("🎨 เปิดเมนูเลือกธีม"))
        btn_open_picker.setProperty("class", "BtnSecondary")
        btn_open_picker.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_open_picker.clicked.connect(self._open_theme_picker_dialog)
        theme_row.addWidget(btn_open_picker)

        box_theme.addLayout(theme_row)
        layout.addLayout(box_theme)

        # App Language
        box_lang = QVBoxLayout()
        box_lang.setSpacing(4)
        box_lang.addWidget(QLabel(_("ภาษาของระบบ (App Language):")))
        self.cbo_lang = QComboBox()
        self.cbo_lang.addItems([_("ไทย (Thai)"), _("English")])
        box_lang.addWidget(self.cbo_lang)
        layout.addLayout(box_lang)

        # Auto Capsule Checkbox
        self.chk_steam_capsule = QCheckBox(_("ดาวน์โหลดภาพปก 16:9 จาก Steam อัตโนมัติเมื่อสร้างโปรเจกต์ใหม่"))
        layout.addWidget(self.chk_steam_capsule)

        layout.addStretch()

    def _open_theme_picker_dialog(self):
        from ui_pyqt6.dialogs.theme_picker_dialog import ThemePickerDialog
        current = self.cbo_theme.currentData() or "dark"
        dlg = ThemePickerDialog(current_theme=str(current), parent=self)
        dlg.theme_selected.connect(self._on_theme_picked_from_dialog)
        dlg.exec()

    def _on_theme_picked_from_dialog(self, theme_key: str):
        for i in range(self.cbo_theme.count()):
            if self.cbo_theme.itemData(i) == theme_key:
                self.cbo_theme.setCurrentIndex(i)
                break

    def _load_current_settings(self):
        # Paths
        default_ws = self.cfg.get("default_workspace_dir", r"E:\Mod_Workspace")
        default_tools = self.cfg.get("default_tools_dir", r"E:\Mod_Workspace\Tool")
        self.ent_default_ws.setText(default_ws)
        self.ent_default_tools.setText(default_tools)

        # Libraries
        self._refresh_library_list()

        # General
        self.ent_author.setText(self.cfg.get("default_author", "หน๊ด หนวด translator"))
        theme = str(self.cfg.get("active_theme", "dark")).strip().lower()
        if theme == "obsidian":
            theme = "dark"
        found = False
        for i in range(self.cbo_theme.count()):
            data = self.cbo_theme.itemData(i)
            if data and str(data).lower() == theme:
                self.cbo_theme.setCurrentIndex(i)
                found = True
                break
        if not found:
            for i in range(self.cbo_theme.count()):
                if self.cbo_theme.itemData(i) == "dark":
                    self.cbo_theme.setCurrentIndex(i)
                    break

        lang = self.cfg.get("app_lang", "th")
        self.cbo_lang.setCurrentIndex(0 if lang == "th" else 1)
        self.chk_steam_capsule.setChecked(self.cfg.get("steam_auto_capsule", True))

        # Initial scan count
        self._refresh_scanner_stats()

    def _refresh_library_list(self):
        self.tasks.submit("libraries", self.game_scanner.get_all_library_folders, self._libraries_ready,
                          lambda error: self.lbl_game_count.setText("สแกนไม่สำเร็จ: " + error))

    def _libraries_ready(self, libraries):
        self.list_libraries.clear()
        for lib in libraries:
            src = lib.get("source", "System")
            path = lib.get("path", "")
            icon = "🎮" if src == "Steam" else "📁"
            self.list_libraries.addItem(f"{icon} [{src}] {path}")

    def _refresh_scanner_stats(self):
        self.lbl_game_count.setText("กำลังสแกนเกม...")
        self.tasks.submit("games", lambda: self.game_scanner.scan_installed_games(force_refresh=True),
            lambda games: self.lbl_game_count.setText(_("🎮 ตรวจพบทั้งหมด: {count} เกมที่ติดตั้งในเครื่องของคุณ", count=len(games))),
            lambda error: self.lbl_game_count.setText("สแกนไม่สำเร็จ: " + error))

    def _browse_default_ws(self):
        d = QFileDialog.getExistingDirectory(self, _("เลือกตำแหน่งโฟลเดอร์โปรเจกต์ถาวร"), self.ent_default_ws.text().strip())
        if d:
            self.ent_default_ws.setText(os.path.normpath(d))

    def _browse_default_tools(self):
        d = QFileDialog.getExistingDirectory(self, _("เลือกตำแหน่งโฟลเดอร์เครื่องมือถาวร"), self.ent_default_tools.text().strip())
        if d:
            self.ent_default_tools.setText(os.path.normpath(d))

    def _add_custom_library(self):
        d = QFileDialog.getExistingDirectory(self, _("เลือกโฟลเดอร์คลังติดตั้งเกม"))
        if d:
            norm_d = os.path.normpath(d)
            custom_paths = self.cfg.get("game_library_paths", []) or []
            if norm_d not in custom_paths:
                custom_paths.append(norm_d)
                self.cfg.set("game_library_paths", custom_paths)
                self._refresh_library_list()
                self._refresh_scanner_stats()

    def _remove_custom_library(self):
        item = self.list_libraries.currentItem()
        if not item:
            return
        text = item.text()
        if "[Custom]" not in text:
            QMessageBox.information(self, _("ไม่สามารถลบได้"), _("โฟลเดอร์นี้เป็นคลัง Steam/System ของเครื่องที่ตรวจพบอัตโนมัติ สามารถลบได้เฉพาะโฟลเดอร์ที่เพิ่มเอง [Custom] เท่านั้น"))
            return

        # Extract path
        clean_path = text.split("] ", 1)[-1]
        custom_paths = self.cfg.get("game_library_paths", []) or []
        if clean_path in custom_paths:
            custom_paths.remove(clean_path)
            self.cfg.set("game_library_paths", custom_paths)
            self._refresh_library_list()
            self._refresh_scanner_stats()

    def _save_settings(self):
        ws_dir = self.ent_default_ws.text().strip()
        tools_dir = self.ent_default_tools.text().strip()
        author = self.ent_author.text().strip()
        theme_raw = self.cbo_theme.currentData()
        if not theme_raw:
            theme_raw = "dark"
        lang_code = "th" if self.cbo_lang.currentIndex() == 0 else "en"
        auto_capsule = self.chk_steam_capsule.isChecked()

        if ws_dir and not os.path.exists(ws_dir):
            try:
                os.makedirs(ws_dir, exist_ok=True)
            except Exception:
                pass

        if tools_dir and not os.path.exists(tools_dir):
            try:
                os.makedirs(tools_dir, exist_ok=True)
            except Exception:
                pass

        self.cfg.set("default_workspace_dir", ws_dir, auto_save=False)
        self.cfg.set("default_tools_dir", tools_dir, auto_save=False)
        self.cfg.set("default_author", author, auto_save=False)
        self.cfg.set("active_theme", str(theme_raw), auto_save=False)
        self.cfg.set("app_lang", lang_code, auto_save=False)
        self.cfg.set("steam_auto_capsule", auto_capsule, auto_save=True)

        set_language(lang_code)

        self._refresh_scanner_stats()

        self.settings_saved.emit()
        self.accept()
