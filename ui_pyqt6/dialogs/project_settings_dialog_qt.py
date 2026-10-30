from core.qt_tasks import BackgroundTasks, TaskDialogMixin
import os
import json
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QFileDialog, QMessageBox, QFrame, QTextEdit, QScrollArea, QWidget, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal
from core.project_service import ProjectService
from core.engine_scanner import EngineScanner
from core.game_scanner import GameScanner
from core.config_manager import ConfigManager
from i18n_helper import _

class ProjectSettingsDialogQt(TaskDialogMixin, QDialog):
    """
    Comprehensive Project Settings Dialog.
    Allows editing workspace path, game installation directory (with auto-scanner),
    tool directory, game engine, status, translation languages, author, and notes.
    Synchronizes both hub_config.json and thub_project.json.
    """
    project_updated = pyqtSignal(dict)

    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.tasks = BackgroundTasks(self)
        self.project = dict(project)
        self.old_name = project.get("name", "")
        self.project_service = ProjectService()
        self.cfg_manager = ConfigManager()
        self.game_scanner = GameScanner.get_instance()

        self.setWindowTitle(_("🛠️ ตั้งค่าโปรเจกต์ - {name}").format(name=self.old_name))
        self.setFixedSize(620, 680)

        # Read existing workspace thub_project.json if present to prefill extra fields
        self.workspace_meta = self._load_workspace_meta()

        self._build_ui()

    def _load_workspace_meta(self):
        ws_path = self.project.get("path", "")
        if ws_path and os.path.exists(ws_path):
            meta_file = os.path.join(ws_path, "thub_project.json")
            if os.path.exists(meta_file):
                try:
                    with open(meta_file, "r", encoding="utf-8") as f:
                        return json.load(f)
                except Exception:
                    pass
        return {}

    def _build_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(20, 16, 20, 16)
        root_layout.setSpacing(12)

        # Header Title
        header_row = QHBoxLayout()
        header_text_col = QVBoxLayout()
        header_text_col.setSpacing(2)

        lbl_title = QLabel(_("🛠️ แก้ไขการตั้งค่าโปรเจกต์"))
        lbl_title.setProperty("class", "PageTitle")
        header_text_col.addWidget(lbl_title)

        lbl_sub = QLabel(_("ปรับปรุงเส้นทางโฟลเดอร์ เครื่องมือ Engine และข้อมูลสรุปของโปรเจกต์นี้"))
        lbl_sub.setProperty("class", "SubText")
        header_text_col.addWidget(lbl_sub)
        header_row.addLayout(header_text_col)
        header_row.addStretch()

        root_layout.addLayout(header_row)

        # Scroll Area for Form Content
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QWidget()
        form_layout = QVBoxLayout(container)
        form_layout.setContentsMargins(4, 4, 10, 4)
        form_layout.setSpacing(12)

        # 1. Project Name
        form_layout.addWidget(QLabel("ชื่อโปรเจกต์ / เกม *"))
        self.ent_name = QLineEdit(self.project.get("name", ""))
        self.ent_name.setPlaceholderText("ชื่อโปรเจกต์ม็อด...")
        form_layout.addWidget(self.ent_name)

        # 2. Workspace Directory
        form_layout.addWidget(QLabel("โฟลเดอร์พื้นที่ทำงาน (Workspace) *"))
        ws_row = QHBoxLayout()
        ws_row.setSpacing(6)
        self.ent_ws = QLineEdit(self.project.get("path", ""))
        self.ent_ws.setPlaceholderText("เช่น E:\\Mod_Workspace\\Game_Name")
        btn_browse_ws = QPushButton("📂 เลือก")
        btn_browse_ws.setProperty("class", "BtnSecondary")
        btn_browse_ws.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_browse_ws.clicked.connect(self._browse_workspace)
        ws_row.addWidget(self.ent_ws, stretch=1)
        ws_row.addWidget(btn_browse_ws)
        btn_move_ws = QPushButton("🚚 ย้ายข้ามไดรฟ์...")
        btn_move_ws.setProperty("class", "BtnSecondary")
        btn_move_ws.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_move_ws.setToolTip(_("ย้ายโฟลเดอร์โปรเจกต์นี้ไปยังไดรฟ์อื่นพร้อมคืนพื้นที่ดิสก์ (Queue Move)"))
        btn_move_ws.clicked.connect(self._open_move_dialog)
        ws_row.addWidget(btn_move_ws)
        form_layout.addLayout(ws_row)

        # 3. Game Installation Directory
        form_layout.addWidget(QLabel("ตำแหน่งติดตั้งเกม (Game Directory)"))
        game_row = QHBoxLayout()
        game_row.setSpacing(6)
        self.ent_game = QLineEdit(self.project.get("game_dir", "") or self.workspace_meta.get("game_path", ""))
        self.ent_game.setPlaceholderText("เช่น F:\\SteamLibrary\\steamapps\\common\\GameName")
        self.ent_game.textChanged.connect(self._on_game_dir_changed)

        btn_browse_game = QPushButton("📂 เลือก")
        btn_browse_game.setProperty("class", "BtnSecondary")
        btn_browse_game.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_browse_game.clicked.connect(self._browse_game_dir)

        self.btn_scan_game = QPushButton("🔍 สแกนหาเกม")
        self.btn_scan_game.setProperty("class", "BtnPrimary")
        self.btn_scan_game.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_scan_game.clicked.connect(self._scan_installed_game)

        game_row.addWidget(self.ent_game, stretch=1)
        game_row.addWidget(btn_browse_game)
        game_row.addWidget(self.btn_scan_game)
        form_layout.addLayout(game_row)

        # 4. Tool Directory
        form_layout.addWidget(QLabel("ตำแหน่งเครื่องมือ (Tool Directory)"))
        tool_row = QHBoxLayout()
        tool_row.setSpacing(6)
        default_tools = self.cfg_manager.get("default_tools_dir", r"E:\Mod_Workspace\Tool")
        curr_tool = self.project.get("tool_dir", "") or self.workspace_meta.get("tool_path", "") or default_tools
        self.ent_tool = QLineEdit(curr_tool)
        self.ent_tool.setPlaceholderText("เช่น E:\\Mod_Workspace\\Tool")

        btn_browse_tool = QPushButton("📂 เลือก")
        btn_browse_tool.setProperty("class", "BtnSecondary")
        btn_browse_tool.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_browse_tool.clicked.connect(self._browse_tool_dir)

        btn_default_tool = QPushButton("🔄 ค่าเริ่มต้น")
        btn_default_tool.setProperty("class", "BtnSecondary")
        btn_default_tool.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_default_tool.clicked.connect(lambda: self.ent_tool.setText(default_tools))

        tool_row.addWidget(self.ent_tool, stretch=1)
        tool_row.addWidget(btn_browse_tool)
        tool_row.addWidget(btn_default_tool)
        form_layout.addLayout(tool_row)

        # 5. Game Engine Selector + Live Preview
        engine_box = QVBoxLayout()
        engine_box.setSpacing(4)
        engine_box.addWidget(QLabel("Game Engine (เอนจิ้นประจำโปรเจกต์):"))

        eng_row = QHBoxLayout()
        self.cbo_engine = QComboBox()
        self.cbo_engine.setEditable(True)
        for eng in EngineScanner.KNOWN_ENGINES:
            self.cbo_engine.addItem(eng)

        curr_engine = self.project.get("engine") or self.project.get("engine_badge") or "Custom Engine"
        if curr_engine in EngineScanner.KNOWN_ENGINES:
            self.cbo_engine.setCurrentText(curr_engine)
        else:
            self.cbo_engine.setEditText(curr_engine)

        self.cbo_engine.currentTextChanged.connect(self._on_engine_changed)

        self.lbl_engine_badge = QLabel(f" {curr_engine} ")
        curr_color = self.project.get("engine_color") or EngineScanner.get_engine_color(curr_engine)
        self._update_engine_badge_preview(curr_engine, curr_color)

        eng_row.addWidget(self.cbo_engine, stretch=1)
        eng_row.addWidget(self.lbl_engine_badge)
        engine_box.addLayout(eng_row)
        form_layout.addLayout(engine_box)

        # 6. Status & Languages Row
        status_lang_row = QHBoxLayout()
        status_lang_row.setSpacing(10)

        # Status
        col_status = QVBoxLayout()
        col_status.addWidget(QLabel("สถานะโปรเจกต์:"))
        self.cbo_status = QComboBox()
        status_options = [
            ("In Progress", _("⏳ กำลังแปล (In Progress)")),
            ("Completed", _("✅ แปลเสร็จสมบูรณ์ (Completed)")),
            ("Imported", _("📦 นำเข้าข้อมูลแล้ว (Imported)"))
        ]
        curr_status = self.project.get("status", "In Progress")
        selected_idx = 0
        for idx, (code, display) in enumerate(status_options):
            self.cbo_status.addItem(display, code)
            if code == curr_status:
                selected_idx = idx
        self.cbo_status.setCurrentIndex(selected_idx)
        col_status.addWidget(self.cbo_status)
        status_lang_row.addLayout(col_status, stretch=1)

        # Source Lang
        col_src = QVBoxLayout()
        col_src.addWidget(QLabel("ภาษาต้นฉบับ:"))
        self.cbo_src = QComboBox()
        self.cbo_src.addItems(["English", "Japanese", "Chinese", "Korean", "French", "German"])
        self.cbo_src.setCurrentText(self.project.get("source_lang", "English"))
        col_src.addWidget(self.cbo_src)
        status_lang_row.addLayout(col_src, stretch=1)

        # Target Lang
        col_tgt = QVBoxLayout()
        col_tgt.addWidget(QLabel("ภาษาเป้าหมาย:"))
        self.cbo_tgt = QComboBox()
        self.cbo_tgt.addItems(["Thai", "English", "Japanese"])
        self.cbo_tgt.setCurrentText(self.project.get("target_lang", "Thai"))
        col_tgt.addWidget(self.cbo_tgt)
        status_lang_row.addLayout(col_tgt, stretch=1)

        form_layout.addLayout(status_lang_row)

        # 7. Author & Contributors
        author_row = QHBoxLayout()
        author_row.setSpacing(10)

        col_author = QVBoxLayout()
        col_author.addWidget(QLabel("ผู้แปล / ผู้สร้าง (Author):"))
        default_author = self.cfg_manager.get("default_author", "หน๊ด หนวด translator")
        curr_author = self.workspace_meta.get("author", default_author)
        self.ent_author = QLineEdit(curr_author)
        col_author.addWidget(self.ent_author)
        author_row.addLayout(col_author, stretch=1)

        col_contrib = QVBoxLayout()
        col_contrib.addWidget(QLabel("ผู้มีส่วนร่วม (Contributors):"))
        self.ent_contrib = QLineEdit(self.workspace_meta.get("contributors", ""))
        self.ent_contrib.setPlaceholderText("เช่น ทีมงานแปล, ผู้ตรวจทาน...")
        col_contrib.addWidget(self.ent_contrib)
        author_row.addLayout(col_contrib, stretch=1)

        form_layout.addLayout(author_row)

        # 8. Notes
        form_layout.addWidget(QLabel("บันทึกย่อ (Notes):"))
        self.txt_notes = QTextEdit()
        self.txt_notes.setFixedHeight(65)
        self.txt_notes.setPlaceholderText("รายละเอียดเพิ่มเติมเกี่ยวกับโปรเจกต์...")
        self.txt_notes.setText(self.project.get("notes", self.workspace_meta.get("notes", "")))
        form_layout.addWidget(self.txt_notes)

        scroll_area.setWidget(container)
        root_layout.addWidget(scroll_area, stretch=1)

        # Bottom Buttons Row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        btn_cancel = QPushButton("ยกเลิก")
        btn_cancel.setProperty("class", "BtnSecondary")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_cancel)

        btn_row.addStretch()

        btn_save = QPushButton("💾 บันทึกการตั้งค่า")
        btn_save.setProperty("class", "BtnPrimary")
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.clicked.connect(self._save_settings)
        btn_row.addWidget(btn_save)

        root_layout.addLayout(btn_row)

    def _browse_workspace(self):
        d = QFileDialog.getExistingDirectory(self, "เลือกโฟลเดอร์ Workspace ของโปรเจกต์", self.ent_ws.text().strip())
        if d:
            self.ent_ws.setText(os.path.normpath(d))

    def _open_move_dialog(self):
        from ui_pyqt6.dialogs.project_move_queue_dialog_qt import ProjectMoveQueueDialogQt
        projects = self.project_service.get_all_projects(include_archived=True)
        dlg = ProjectMoveQueueDialogQt(projects, preselected_project=self.project, parent=self)
        def on_moved(moved_list):
            for name, new_path in moved_list:
                if name == self.old_name:
                    self.ent_ws.setText(new_path)
                    self.project["path"] = new_path
        dlg.projects_moved.connect(on_moved)
        dlg.exec()

    def _browse_game_dir(self):
        d = QFileDialog.getExistingDirectory(self, "เลือกโฟลเดอร์ติดตั้งเกม", self.ent_game.text().strip())
        if d:
            self.ent_game.setText(os.path.normpath(d))
            self._auto_detect_engine_from_game()

    def _browse_tool_dir(self):
        d = QFileDialog.getExistingDirectory(self, "เลือกโฟลเดอร์เครื่องมือ", self.ent_tool.text().strip())
        if d:
            self.ent_tool.setText(os.path.normpath(d))

    def _scan_installed_game(self):
        """Scans PC for games matching the project name and offers matches."""
        name = self.ent_name.text().strip()
        if not name:
            QMessageBox.information(self, "สแกนหาเกม", "กรุณาระบุชื่อเกมก่อนทำการสแกน")
            return

        self.tasks.submit("find-game", lambda: self.game_scanner.find_installed_games(name, limit=5),
                          lambda matches: self._installed_games_ready(name, matches),
                          lambda error: QMessageBox.warning(self, "สแกนไม่สำเร็จ", error))

    def _installed_games_ready(self, name, matches):
        if self.ent_name.text().strip() != name:
            return
        if not matches:
            QMessageBox.information(
                self, "ไม่พบเกมในเครื่อง",
                f"ไม่พบโฟลเดอร์เกมที่ตรงกับ '{name}' ในคลัง Steam หรือไดรฟ์ที่สแกน\n"
                "คุณสามารถเลือกโฟลเดอร์ด้วยตนเองได้ผ่านปุ่ม '📂 เลือก'"
            )
            return

        if len(matches) == 1:
            best = matches[0]
            self.ent_game.setText(best["path"])
            self._auto_detect_engine_from_game()
            QMessageBox.information(self, "พบเกมในเครื่อง", f"พบโฟลเดอร์เกม:\n{best['path']}\n\nระบบตั้งค่าและตรวจจับ Engine เรียบร้อยแล้ว!")
        else:
            # Show menu of multiple matches
            menu = QMenu(self)
            for m in matches:
                act = menu.addAction(f"🎮 {m['name']} ({m['source']})\n   {m['path']}")
                act.triggered.connect(lambda _, p=m['path']: self._apply_game_dir(p))
            menu.exec(self.btn_scan_game.mapToGlobal(self.btn_scan_game.rect().bottomLeft()))

    def _apply_game_dir(self, path):
        self.ent_game.setText(path)
        self._auto_detect_engine_from_game()

    def _on_game_dir_changed(self):
        self._auto_detect_engine_from_game()

    def _auto_detect_engine_from_game(self):
        game_path = self.ent_game.text().strip()
        ws_path = self.ent_ws.text().strip()
        name = self.ent_name.text().strip()
        if not game_path and not ws_path:
            return

        identity = (game_path, ws_path, name)
        self.tasks.submit("engine", lambda: EngineScanner.detect_engine(game_dir=game_path, workspace_dir=ws_path, title=name),
                          lambda info: self._engine_ready(identity, info))

    def _engine_ready(self, identity, info):
        if identity != (self.ent_game.text().strip(), self.ent_ws.text().strip(), self.ent_name.text().strip()):
            return
        badge = info.get("badge", "Custom Engine")
        color = info.get("badge_color", "#94a3b8")

        self.cbo_engine.blockSignals(True)
        self.cbo_engine.setCurrentText(badge)
        self.cbo_engine.blockSignals(False)
        self._update_engine_badge_preview(badge, color)

    def _on_engine_changed(self, engine_name):
        engine_name = engine_name.strip() if engine_name else "Custom Engine"
        color = EngineScanner.get_engine_color(engine_name)
        self._update_engine_badge_preview(engine_name, color)

    def _update_engine_badge_preview(self, badge, color):
        self.lbl_engine_badge.setText(f" {badge} ")
        self.lbl_engine_badge.setStyleSheet(f"""
            background-color: rgba(16, 20, 30, 220);
            color: {color};
            border: 1px solid {color};
            border-radius: 5px;
            padding: 4px 8px;
            font-size: 10px;
            font-weight: bold;
        """)

    def _save_settings(self):
        new_name = self.ent_name.text().strip()
        new_ws = self.ent_ws.text().strip()
        new_game = self.ent_game.text().strip()
        new_tool = self.ent_tool.text().strip()
        new_engine = self.cbo_engine.currentText().strip() or "Custom Engine"
        new_status = self.cbo_status.currentData() or self.cbo_status.currentText().strip()
        new_src = self.cbo_src.currentText().strip()
        new_tgt = self.cbo_tgt.currentText().strip()
        new_author = self.ent_author.text().strip()
        new_contrib = self.ent_contrib.text().strip()
        new_notes = self.txt_notes.toPlainText().strip()

        if not new_name or not new_ws:
            QMessageBox.critical(self, "ข้อผิดพลาด", "กรุณาระบุชื่อโปรเจกต์และโฟลเดอร์ Workspace")
            return

        engine_color = EngineScanner.get_engine_color(new_engine)

        updated_data = {
            "name": new_name,
            "path": new_ws,
            "game_dir": new_game,
            "tool_dir": new_tool,
            "engine": new_engine,
            "engine_badge": new_engine,
            "engine_color": engine_color,
            "status": new_status,
            "source_lang": new_src,
            "target_lang": new_tgt,
            "author": new_author,
            "contributors": new_contrib,
            "notes": new_notes
        }

        if "save-project" in self.tasks.jobs:
            return
        self.setEnabled(False)
        self.tasks.submit("save-project", lambda: self.project_service.update_project(self.old_name, updated_data),
                          self._settings_saved, self._settings_failed)

    def _settings_saved(self, saved_proj):
        self.setEnabled(True)
        self.project_updated.emit(saved_proj)
        self.accept()

    def _settings_failed(self, error):
        self.setEnabled(True)
        QMessageBox.critical(self, "เกิดข้อผิดพลาด", f"ไม่สามารถบันทึกการตั้งค่าได้:\n{error}")
