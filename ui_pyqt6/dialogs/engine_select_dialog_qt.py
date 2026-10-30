import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QFrame, QMessageBox, QTextEdit, QScrollArea, QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from core.engine_scanner import EngineScanner
from core.engine_database import EngineDatabase
from i18n_helper import _

class EngineSelectDialogQt(QDialog):
    """
    Modern Dialog to select, customize, or override the Game Engine for a project.
    Features live badge preview, comprehensive engine specifications, tools,
    font subsystems, and description across 130+ game engines worldwide.
    """

    engine_saved = pyqtSignal(dict)

    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.project = project
        self.setWindowTitle(_("⚙️ กำหนด Game Engine - {name}").format(name=project.get('name', 'Game')))
        self.setFixedSize(540, 520)

        # Determine current engine
        curr = project.get("engine") or project.get("engine_badge")
        if not curr:
            curr_info = EngineScanner.detect_engine(
                game_dir=project.get("game_dir", ""),
                workspace_dir=project.get("path", ""),
                title=project.get("name", "")
            )
            curr = curr_info.get("badge", "Custom Engine")
        self.current_engine = curr

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(12)

        # Header Title / Description
        lbl_header = QLabel(_("🎮 กำหนด Game Engine ประจำการ์ดเกม"))
        lbl_header.setProperty("class", "PageTitle")
        layout.addWidget(lbl_header)

        lbl_sub = QLabel(_("ระบบมีข้อมูลเจาะลึกเอนจิ้นเกมกว่า 130+ เอนจิ้นทั่วโลก เพื่อแนะนำเครื่องมือและฟอนต์ที่ถูกต้อง"))
        lbl_sub.setProperty("class", "SubText")
        layout.addWidget(lbl_sub)

        # Engine Selection Combo
        layout.addWidget(QLabel(_("เลือก Game Engine:")))
        self.cbo_engine = QComboBox()
        self.cbo_engine.setEditable(True)
        self.cbo_engine.lineEdit().setPlaceholderText(_("เลือกหรือพิมพ์ค้นหา Engine..."))

        # Populate with known engines
        known_engines = EngineScanner.get_known_engines()
        for eng in known_engines:
            self.cbo_engine.addItem(eng)

        # Set current engine
        norm_curr = EngineScanner.normalize_engine_name(self.current_engine)
        if norm_curr in known_engines:
            self.cbo_engine.setCurrentText(norm_curr)
        elif self.current_engine in known_engines:
            self.cbo_engine.setCurrentText(self.current_engine)
        else:
            self.cbo_engine.setEditText(self.current_engine)

        self.cbo_engine.currentTextChanged.connect(self._update_preview)
        layout.addWidget(self.cbo_engine)

        # Live Badge Preview Card
        layout.addWidget(QLabel(_("ตัวอย่าง Badge ที่จะแสดงผลบนการ์ด:")))
        self.preview_box = QFrame()
        self.preview_box.setProperty("class", "InnerCard")
        prev_layout = QHBoxLayout(self.preview_box)
        prev_layout.setContentsMargins(14, 10, 14, 10)

        self.lbl_game_title = QLabel(self.project.get("name", "Game Title"))
        self.lbl_game_title.setProperty("class", "CardTitle")
        prev_layout.addWidget(self.lbl_game_title, stretch=1)

        self.lbl_preview_badge = QLabel()
        prev_layout.addWidget(self.lbl_preview_badge)
        layout.addWidget(self.preview_box)

        # Detailed Engine Intelligence Card
        self.info_card = QFrame()
        self.info_card.setStyleSheet("""
            QFrame {
                background-color: rgba(15, 23, 42, 0.75);
                border: 1px solid rgba(56, 189, 248, 0.25);
                border-radius: 8px;
                padding: 10px 12px;
            }
        """)
        info_layout = QVBoxLayout(self.info_card)
        info_layout.setContentsMargins(8, 8, 8, 8)
        info_layout.setSpacing(6)

        self.lbl_dev_cat = QLabel()
        self.lbl_dev_cat.setStyleSheet("color: #38bdf8; font-weight: bold; font-size: 11px;")
        info_layout.addWidget(self.lbl_dev_cat)

        self.lbl_tools = QLabel()
        self.lbl_tools.setStyleSheet("color: #cbd5e1; font-size: 10px;")
        self.lbl_tools.setWordWrap(True)
        info_layout.addWidget(self.lbl_tools)

        self.lbl_formats = QLabel()
        self.lbl_formats.setStyleSheet("color: #94a3b8; font-size: 10px;")
        self.lbl_formats.setWordWrap(True)
        info_layout.addWidget(self.lbl_formats)

        self.lbl_desc = QLabel()
        self.lbl_desc.setStyleSheet("color: #e2e8f0; font-size: 10px; line-height: 1.4;")
        self.lbl_desc.setWordWrap(True)
        info_layout.addWidget(self.lbl_desc)

        layout.addWidget(self.info_card)
        layout.addStretch()

        # Action Buttons
        btn_row = QHBoxLayout()
        btn_cancel = QPushButton(_("ยกเลิก"))
        btn_cancel.setProperty("class", "BtnSecondary")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_cancel)
        btn_row.addStretch()

        btn_save = QPushButton(_("💾 บันทึก Engine"))
        btn_save.setProperty("class", "BtnPrimary")
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.clicked.connect(self._save)
        btn_row.addWidget(btn_save)

        layout.addLayout(btn_row)

        self._update_preview(self.cbo_engine.currentText())

    def _update_preview(self, engine_name):
        engine_name = engine_name.strip() if engine_name else "Custom Engine"
        color = EngineScanner.get_engine_color(engine_name)
        info = EngineDatabase.get_engine(engine_name)

        self.lbl_preview_badge.setText(f" {info.get('canonical_name', engine_name)} ")
        self.lbl_preview_badge.setStyleSheet(f"""
            background-color: rgba(16, 20, 30, 220);
            color: {color};
            border: 1px solid {color};
            border-radius: 5px;
            padding: 3px 8px;
            font-size: 10px;
            font-weight: bold;
        """)

        # Update metadata info card
        dev = info.get("developer", "Unknown")
        cat = info.get("category", "General")
        country = info.get("origin_country", "")
        origin_str = f" ({country})" if country else ""
        self.lbl_dev_cat.setText(f"🏢 ผู้พัฒนา: {dev}{origin_str}  •  หมวดหมู่: {cat}")

        tools = ", ".join(info.get("recommended_tools", ["TStudio", "TRun"]))
        self.lbl_tools.setText(f"🛠️ เครื่องมือแปล/สกัด: {tools}")

        formats = ", ".join(info.get("text_formats", [])) or "ข้อความทั่วไป"
        font_tech = info.get("font_tech", "TrueType / Bitmap Font")
        self.lbl_formats.setText(f"📦 นามสกุลไฟล์: {formats}  |  🔤 ฟอนต์: {font_tech}")

        desc = info.get("description_th", "") or info.get("description_en", "")
        self.lbl_desc.setText(desc)

    def _save(self):
        engine_name = self.cbo_engine.currentText().strip()
        if not engine_name:
            engine_name = "Custom Engine"
        norm_name = EngineScanner.normalize_engine_name(engine_name)
        color = EngineScanner.get_engine_color(norm_name)

        self.project["engine"] = norm_name
        self.project["engine_badge"] = norm_name
        self.project["engine_color"] = color

        self.engine_saved.emit(self.project)
        self.accept()
