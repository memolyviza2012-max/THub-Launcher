from core.qt_tasks import BackgroundTasks, TaskDialogMixin
import os
import re
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QFileDialog, QMessageBox, QFrame, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal
from core.project_service import ProjectService
from core.steam_service import SteamService
from core.engine_scanner import EngineScanner
from core.game_scanner import GameScanner
from core.config_manager import ConfigManager
from ui_pyqt6.dialogs.bible_viewer_dialog_qt import BibleViewerDialogQt
from i18n_helper import _

class ProjectWizardDialogQt(TaskDialogMixin, QDialog):
    """
    Project Wizard in PyQt6.
    Fast creation of standard 01-06 workspace, real-time Engine detection,
    automatic installed game scanning, and auto-fetching of 16:9 covers.
    """

    project_created = pyqtSignal(dict)

    def __init__(self, is_import_mode=False, parent=None):
        super().__init__(parent)
        self.tasks = BackgroundTasks(self)
        self.is_import_mode = is_import_mode
        self.project_service = ProjectService()
        self.cfg = ConfigManager()
        self.game_scanner = GameScanner.get_instance()

        self._ws_manually_edited = False
        self._game_manually_edited = False
        self._current_suggested_game = None
        self._current_bible = None

        self.setWindowTitle(_("เพิ่มโปรเจกต์ม็อดใหม่") if not is_import_mode else _("นำเข้าโปรเจกต์ม็อด"))
        self.setFixedSize(640, 680)

        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(12)

        # Header
        lbl_title = QLabel(_("✨ สร้างโปรเจกต์ใหม่ (Standard Workspace)") if not self.is_import_mode else _("📂 นำเข้าโปรเจกต์เดิม"))
        lbl_title.setProperty("class", "PageTitle")
        main_layout.addWidget(lbl_title)

        lbl_desc = QLabel(_("ระบบจะสร้างโฟลเดอร์ 01–06 ตามมาตรฐาน THub สแกนหาเกมในเครื่อง และตรวจ Engine อัตโนมัติ"))
        lbl_desc.setProperty("class", "SubText")
        main_layout.addWidget(lbl_desc)

        # 1. Game Name
        main_layout.addWidget(QLabel("ชื่อเกม / โปรเจกต์ *"))
        self.ent_name = QLineEdit()
        self.ent_name.setPlaceholderText("เช่น The Witcher 3, Atelier Ryza, Bleak Faith...")
        self.ent_name.textChanged.connect(self._on_name_changed)
        main_layout.addWidget(self.ent_name)

        # Suggestion Banner (Appears when installed game found on PC)
        self.lbl_suggestion = QLabel()
        self.lbl_suggestion.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lbl_suggestion.setStyleSheet("""
            background-color: rgba(56, 189, 248, 0.12);
            color: #38bdf8;
            border: 1px solid rgba(56, 189, 248, 0.4);
            border-radius: 6px;
            padding: 6px 10px;
            font-size: 11px;
            font-weight: bold;
        """)
        self.lbl_suggestion.setVisible(False)
        self.lbl_suggestion.mousePressEvent = self._on_suggestion_clicked
        main_layout.addWidget(self.lbl_suggestion)

        # 2. Workspace Path
        main_layout.addWidget(QLabel("โฟลเดอร์จัดเก็บโปรเจกต์ (Workspace) *"))
        ws_row = QHBoxLayout()
        ws_row.setSpacing(6)
        self.ent_ws = QLineEdit()
        self.ent_ws.setPlaceholderText("เช่น E:\\Mod_Workspace\\Game_Name...")
        self.ent_ws.textEdited.connect(self._on_ws_text_edited)

        btn_browse_ws = QPushButton("📂 เลือก")
        btn_browse_ws.setProperty("class", "BtnSecondary")
        btn_browse_ws.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_browse_ws.clicked.connect(self._browse_workspace)
        ws_row.addWidget(self.ent_ws, stretch=1)
        ws_row.addWidget(btn_browse_ws)
        main_layout.addLayout(ws_row)

        # 3. Game Directory
        main_layout.addWidget(QLabel("ตำแหน่งติดตั้งเกม (Game Directory - มีระบบค้นหาในเครื่องอัตโนมัติ)"))
        game_row = QHBoxLayout()
        game_row.setSpacing(6)
        self.ent_game = QLineEdit()
        self.ent_game.setPlaceholderText("โฟลเดอร์เกมใน Steam / Epic (ใช้สำหรับสแกน Engine)...")
        self.ent_game.textEdited.connect(self._on_game_text_edited)
        self.ent_game.textChanged.connect(self._on_game_changed)

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
        main_layout.addLayout(game_row)

        # 4. Game Engine (Auto-detected + Manual Override)
        engine_box = QVBoxLayout()
        engine_box.setSpacing(4)
        lbl_eng_title = QLabel("🎮 Game Engine (ตรวจจับอัตโนมัติ):")
        engine_box.addWidget(lbl_eng_title)

        eng_row = QHBoxLayout()
        self.cbo_engine = QComboBox()
        self.cbo_engine.setEditable(True)
        for eng in EngineScanner.get_known_engines():
            self.cbo_engine.addItem(eng)
        self.cbo_engine.setCurrentText("Custom Engine")
        self.cbo_engine.currentTextChanged.connect(self._on_engine_selected)

        self.lbl_engine_badge = QLabel(" Custom Engine ")
        self._update_engine_badge_preview("Custom Engine", "#94a3b8")

        eng_row.addWidget(self.cbo_engine, stretch=1)
        eng_row.addWidget(self.lbl_engine_badge)
        engine_box.addLayout(eng_row)
        main_layout.addLayout(engine_box)

        # 4.5. Modding Bible Knowledge Banner (Auto-matched)
        self.bible_box = QFrame()
        self.bible_box.setStyleSheet("""
            QFrame {
                background-color: rgba(30, 41, 59, 0.7);
                border: 1px solid rgba(56, 189, 248, 0.35);
                border-radius: 8px;
                padding: 10px 12px;
            }
        """)
        bb_layout = QVBoxLayout(self.bible_box)
        bb_layout.setContentsMargins(0, 0, 0, 0)
        bb_layout.setSpacing(6)

        bb_top = QHBoxLayout()
        bb_top.setSpacing(8)

        lbl_b_icon = QLabel("📖")
        lbl_b_icon.setStyleSheet("font-size: 16px;")
        bb_top.addWidget(lbl_b_icon)

        self.lbl_bible_title = QLabel("พบข้อมูลจากคัมภีร์แปลม็อด!")
        self.lbl_bible_title.setStyleSheet("color: #38bdf8; font-weight: bold; font-size: 12px;")
        bb_top.addWidget(self.lbl_bible_title, stretch=1)

        self.btn_view_bible = QPushButton("👁️ เปิดอ่านคัมภีร์")
        self.btn_view_bible.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_view_bible.setStyleSheet("""
            QPushButton {
                background-color: #0284c7;
                color: #ffffff;
                font-weight: bold;
                border: none;
                border-radius: 5px;
                padding: 4px 10px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #0369a1;
            }
        """)
        self.btn_view_bible.clicked.connect(self._open_bible_viewer)
        bb_top.addWidget(self.btn_view_bible)
        bb_layout.addLayout(bb_top)

        self.lbl_bible_details = QLabel()
        self.lbl_bible_details.setStyleSheet("color: #94a3b8; font-size: 11px;")
        self.lbl_bible_details.setWordWrap(True)
        bb_layout.addWidget(self.lbl_bible_details)

        self.bible_box.setVisible(False)
        main_layout.addWidget(self.bible_box)

        # 5. Languages
        lang_row = QHBoxLayout()
        lang_row.setSpacing(12)

        col_src = QVBoxLayout()
        col_src.addWidget(QLabel("ภาษาต้นฉบับ:"))
        self.cbo_src = QComboBox()
        self.cbo_src.addItems(["English", "Japanese", "Chinese", "Korean", "French", "German"])
        col_src.addWidget(self.cbo_src)
        lang_row.addLayout(col_src)

        col_tgt = QVBoxLayout()
        col_tgt.addWidget(QLabel("ภาษาเป้าหมาย:"))
        self.cbo_tgt = QComboBox()
        self.cbo_tgt.addItems(["Thai", "English", "Japanese"])
        col_tgt.addWidget(self.cbo_tgt)
        lang_row.addLayout(col_tgt)
        main_layout.addLayout(lang_row)

        main_layout.addStretch()

        # Bottom Buttons
        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("ยกเลิก")
        btn_cancel.setProperty("class", "BtnSecondary")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_cancel)
        btn_row.addStretch()

        btn_submit = QPushButton("🚀 สร้างและเริ่มโปรเจกต์")
        btn_submit.setProperty("class", "BtnPrimary")
        btn_submit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_submit.clicked.connect(self._submit)
        btn_row.addWidget(btn_submit)
        main_layout.addLayout(btn_row)

    def _on_ws_text_edited(self):
        self._ws_manually_edited = True
        self._auto_detect_engine()

    def _on_game_text_edited(self):
        self._game_manually_edited = True
        self._auto_detect_engine()

    def _on_game_changed(self):
        self._auto_detect_engine()

    def _on_name_changed(self, text):
        raw_name = text.strip()

        # 1. Auto-fill Workspace if not manually customized
        if not self._ws_manually_edited and not self.is_import_mode:
            default_ws = self.cfg.get("default_workspace_dir", r"E:\Mod_Workspace")
            if raw_name:
                safe_name = re.sub(r'[^a-zA-Z0-9_\u0E00-\u0E7F]+', '_', raw_name).strip('_')
                self.ent_ws.setText(os.path.normpath(os.path.join(default_ws, safe_name)))
            else:
                self.ent_ws.setText("")

        # 2. Auto-scan for matching installed game on PC in a worker.
        if raw_name and len(raw_name) >= 2:
            def find():
                return (self.game_scanner.find_installed_games(raw_name, limit=3),
                        self.game_scanner.get_best_match(raw_name, min_score=90))
            self.tasks.submit("suggest-game", find, lambda result: self._game_suggestions_ready(raw_name, result))
        else:
            self.lbl_suggestion.setVisible(False)
            self._current_suggested_game = None
        self._auto_detect_engine()

    def _game_suggestions_ready(self, name, result):
        if self.ent_name.text().strip() != name:
            return
        matches, exact_match = result
        self._current_suggested_game = matches[0] if matches else None
        self.lbl_suggestion.setVisible(bool(matches))
        if matches:
            best = matches[0]
            self.lbl_suggestion.setText(f"🎮 ตรวจพบในเครื่อง: {best['name']} ({best['source']}) — คลิกเพื่อใช้โฟลเดอร์นี้")
            if exact_match and not self.ent_game.text().strip() and not self._game_manually_edited:
                self.ent_game.setText(exact_match["path"])
                self._auto_detect_engine()

    def _on_suggestion_clicked(self, event):
        if self._current_suggested_game:
            self.ent_game.setText(self._current_suggested_game["path"])
            self._auto_detect_engine()
            self.lbl_suggestion.setText(f"✅ เลือกโฟลเดอร์เกม: {self._current_suggested_game['name']}")

    def _scan_installed_game(self):
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
            self._auto_detect_engine()
            QMessageBox.information(self, "พบเกมในเครื่อง", f"พบโฟลเดอร์เกม:\n{best['path']}\n\nระบบตั้งค่าและตรวจจับ Engine เรียบร้อยแล้ว!")
        else:
            menu = QMenu(self)
            for m in matches:
                act = menu.addAction(f"🎮 {m['name']} ({m['source']})\n   {m['path']}")
                act.triggered.connect(lambda _, p=m['path']: self._apply_game_dir(p))
            menu.exec(self.btn_scan_game.mapToGlobal(self.btn_scan_game.rect().bottomLeft()))

    def _apply_game_dir(self, path):
        self.ent_game.setText(path)
        self._auto_detect_engine()

    def _browse_workspace(self):
        d = QFileDialog.getExistingDirectory(self, "เลือกโฟลเดอร์สำหรับ Workspace", self.ent_ws.text().strip())
        if d:
            self.ent_ws.setText(os.path.normpath(d))
            self._ws_manually_edited = True
            if not self.ent_name.text().strip():
                self.ent_name.setText(os.path.basename(d))
            self._auto_detect_engine()

    def _browse_game_dir(self):
        d = QFileDialog.getExistingDirectory(self, "เลือกโฟลเดอร์ติดตั้งเกม", self.ent_game.text().strip())
        if d:
            self.ent_game.setText(os.path.normpath(d))
            self._game_manually_edited = True
            self._auto_detect_engine()

    def _auto_detect_engine(self):
        name = self.ent_name.text().strip()
        ws = self.ent_ws.text().strip()
        game = self.ent_game.text().strip()
        if not name and not ws and not game:
            self.bible_box.setVisible(False)
            self._current_bible = None
            return

        identity = (name, ws, game, getattr(self, "_engine_revision", 0))
        self.tasks.submit("detect-engine", lambda: EngineScanner.detect_engine(game_dir=game, workspace_dir=ws, title=name),
                          lambda info: self._engine_detection_ready(identity, info))

    def _engine_detection_ready(self, identity, info):
        if identity != (self.ent_name.text().strip(), self.ent_ws.text().strip(), self.ent_game.text().strip(), getattr(self, "_engine_revision", 0)):
            return
        badge = info.get("badge", "Custom Engine")
        color = info.get("badge_color", "#94a3b8")
        self.cbo_engine.blockSignals(True)
        self.cbo_engine.setCurrentText(badge)
        self.cbo_engine.blockSignals(False)
        self._update_engine_badge_preview(badge, color)

        # Update Modding Bible Knowledge Banner / Engine Intelligence
        bible = info.get("bible")
        if bible:
            self._current_bible = bible
            b_title = bible.get("bible_title", "Modding Bible")
            b_eng = bible.get("engine_name", badge)
            tools = ", ".join(bible.get("recommended_tools", [])) or "TStudio, TRun"
            exts = ", ".join(bible.get("file_extensions", [])) or "-"

            self.lbl_bible_title.setText(f"📖 พบคัมภีร์ตรงกับเกมนี้: {b_title}")
            self.lbl_bible_details.setText(f"🎮 เอนจิ้น: {b_eng}  |  🛠️ เครื่องมือ: {tools}  |  📦 นามสกุลไฟล์: {exts}")
            self.btn_view_bible.setVisible(True)
            self.bible_box.setVisible(True)
        else:
            self._current_bible = None
            from core.engine_database import EngineDatabase
            eng_meta = EngineDatabase.get_engine(badge)
            if badge != "Custom Engine" and eng_meta.get("developer"):
                dev = eng_meta.get("developer", "")
                tools = ", ".join(eng_meta.get("recommended_tools", []))
                exts = ", ".join(eng_meta.get("text_formats", []))
                self.lbl_bible_title.setText(f"🎮 ข้อมูลเอนจิ้น: {badge} ({dev})")
                self.lbl_bible_details.setText(f"🛠️ เครื่องมือแนะนำ: {tools}  |  📦 นามสกุลไฟล์: {exts}\n🔤 ระบบฟอนต์: {eng_meta.get('font_tech', '-')}")
                self.btn_view_bible.setVisible(False)
                self.bible_box.setVisible(True)
            else:
                self.bible_box.setVisible(False)

    def _open_bible_viewer(self):
        if not self._current_bible:
            return
        b_path = self._current_bible.get("bible_path", "")
        b_title = self._current_bible.get("bible_title", "")
        b_eng = self._current_bible.get("engine_name", "")
        dlg = BibleViewerDialogQt(self, bible_path=b_path, bible_title=b_title, engine_name=b_eng)
        dlg.exec()

    def _on_engine_selected(self, engine_name):
        self._engine_revision = getattr(self, "_engine_revision", 0) + 1
        engine_name = engine_name.strip() if engine_name else "Custom Engine"
        color = EngineScanner.get_engine_color(engine_name)
        self._update_engine_badge_preview(engine_name, color)

        if not self._current_bible:
            from core.engine_database import EngineDatabase
            eng_meta = EngineDatabase.get_engine(engine_name)
            if engine_name != "Custom Engine" and eng_meta.get("developer"):
                dev = eng_meta.get("developer", "")
                tools = ", ".join(eng_meta.get("recommended_tools", []))
                exts = ", ".join(eng_meta.get("text_formats", []))
                self.lbl_bible_title.setText(f"🎮 ข้อมูลเอนจิ้น: {engine_name} ({dev})")
                self.lbl_bible_details.setText(f"🛠️ เครื่องมือแนะนำ: {tools}  |  📦 นามสกุลไฟล์: {exts}\n🔤 ระบบฟอนต์: {eng_meta.get('font_tech', '-')}")
                self.btn_view_bible.setVisible(False)
                self.bible_box.setVisible(True)
            else:
                self.bible_box.setVisible(False)

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

    def _submit(self):
        name = self.ent_name.text().strip()
        ws = self.ent_ws.text().strip()
        game = self.ent_game.text().strip()
        selected_engine = self.cbo_engine.currentText().strip() or "Custom Engine"
        default_tool = self.cfg.get("default_tools_dir", r"E:\Mod_Workspace\Tool")
        default_author = self.cfg.get("default_author", "หน๊ด หนวด translator")

        if not name or not ws:
            QMessageBox.critical(self, "ข้อผิดพลาด", "กรุณาระบุชื่อโปรเจกต์และตำแหน่งจัดเก็บ Workspace!")
            return

        if "create-project" in self.tasks.jobs:
            return
        # Capture widget values before entering the worker.
        source_lang, target_lang = self.cbo_src.currentText(), self.cbo_tgt.currentText()
        bible_info = self._current_bible
        auto_capsule = self.cfg.get("steam_auto_capsule", True)
        self.setEnabled(False)
        def create():
            proj = self.project_service.create_project(
                name=name, workspace_path=ws, game_dir=game, tool_dir=default_tool,
                source_lang=source_lang, target_lang=target_lang, author=default_author,
                engine=selected_engine, bible_info=bible_info)
            # Download full set of Steam capsules & covers into 07_Image_Resources/Official_Art
            if auto_capsule:
                SteamService.fetch_all_game_capsules(name, os.path.join(ws, "07_Image_Resources", "Official_Art"),
                                                    root_cover_dest=os.path.join(ws, "thub_cover.jpg"))
            return proj
        self.tasks.submit("create-project", create, self._project_created, self._creation_failed)

    def _project_created(self, project):
        self.setEnabled(True)
        self.project_created.emit(project)
        self.accept()

    def _creation_failed(self, error):
        self.setEnabled(True)
        QMessageBox.critical(self, "ข้อผิดพลาด", f"สร้างโปรเจกต์ล้มเหลว:\n{error}")
