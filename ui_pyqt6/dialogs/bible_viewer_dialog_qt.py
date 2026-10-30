import os
import subprocess
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QFrame, QMessageBox, QApplication
)
from PyQt6.QtCore import Qt
from core.knowledge_service import KnowledgeService
from i18n_helper import _

class BibleViewerDialogQt(QDialog):
    """
    Dedicated Modern Markdown & Bible Viewer Dialog.
    Allows viewing, reading rendered markdown or raw source,
    copying path, and opening in external editors / Explorer.
    """

    def __init__(self, parent=None, bible_path="", bible_title="", engine_name=""):
        super().__init__(parent)
        self.bible_path = bible_path
        self.bible_title = bible_title or (os.path.basename(bible_path) if bible_path else _("คัมภีร์ม็อดแปลภาษา"))
        self.engine_name = engine_name
        self.kb_service = KnowledgeService.get_instance()
        self.is_rendered = True

        self.setWindowTitle(f"📖 {self.bible_title}")
        self.resize(900, 700)
        self.setMinimumSize(640, 480)

        self._raw_content = ""
        self._load_content()
        self._build_ui()

    def _load_content(self):
        if self.bible_path and os.path.exists(self.bible_path):
            self._raw_content = self.kb_service.read_markdown(self.bible_path)
        else:
            self._raw_content = f"# ไม่พบไฟล์คัมภีร์\n\nเส้นทาง: `{self.bible_path}`"

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        # 1. Header Card
        header_card = QFrame()
        header_card.setStyleSheet("""
            QFrame {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 10px 14px;
            }
        """)
        h_layout = QVBoxLayout(header_card)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setSpacing(6)

        # Title & Badges Row
        title_row = QHBoxLayout()
        title_row.setSpacing(8)

        lbl_icon = QLabel("📖")
        lbl_icon.setStyleSheet("font-size: 20px;")
        title_row.addWidget(lbl_icon)

        lbl_title = QLabel(self.bible_title)
        lbl_title.setStyleSheet("color: #f8fafc; font-size: 15px; font-weight: bold;")
        title_row.addWidget(lbl_title, stretch=1)

        if self.engine_name:
            lbl_eng = QLabel(f" {self.engine_name} ")
            lbl_eng.setStyleSheet("""
                background-color: rgba(56, 189, 248, 0.15);
                color: #38bdf8;
                border: 1px solid #38bdf8;
                border-radius: 4px;
                padding: 3px 8px;
                font-size: 11px;
                font-weight: bold;
            """)
            title_row.addWidget(lbl_eng)

        h_layout.addLayout(title_row)

        # Path & Action Toolbar
        action_row = QHBoxLayout()
        action_row.setSpacing(6)

        lbl_path = QLabel(self.bible_path)
        lbl_path.setStyleSheet("color: #94a3b8; font-size: 11px; font-family: 'Consolas', monospace;")
        lbl_path.setWordWrap(True)
        action_row.addWidget(lbl_path, stretch=1)

        self.btn_toggle_mode = QPushButton("📝 ดูโค้ด Raw")
        self.btn_toggle_mode.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle_mode.setStyleSheet("""
            QPushButton {
                background-color: #334155;
                color: #f8fafc;
                border: 1px solid #475569;
                border-radius: 5px;
                padding: 5px 10px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #475569;
            }
        """)
        self.btn_toggle_mode.clicked.connect(self._toggle_render_mode)
        action_row.addWidget(self.btn_toggle_mode)

        btn_copy = QPushButton("📋 คัดลอก Path")
        btn_copy.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_copy.setStyleSheet("""
            QPushButton {
                background-color: #334155;
                color: #f8fafc;
                border: 1px solid #475569;
                border-radius: 5px;
                padding: 5px 10px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #475569;
            }
        """)
        btn_copy.clicked.connect(self._copy_path)
        action_row.addWidget(btn_copy)

        btn_folder = QPushButton("📁 เปิดโฟลเดอร์")
        btn_folder.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_folder.setStyleSheet("""
            QPushButton {
                background-color: #334155;
                color: #f8fafc;
                border: 1px solid #475569;
                border-radius: 5px;
                padding: 5px 10px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #475569;
            }
        """)
        btn_folder.clicked.connect(self._open_folder)
        action_row.addWidget(btn_folder)

        btn_ext = QPushButton("📝 เปิดโปรแกรมภายนอก")
        btn_ext.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ext.setStyleSheet("""
            QPushButton {
                background-color: #334155;
                color: #f8fafc;
                border: 1px solid #475569;
                border-radius: 5px;
                padding: 5px 10px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #475569;
            }
        """)
        btn_ext.clicked.connect(self._open_external)
        action_row.addWidget(btn_ext)

        h_layout.addLayout(action_row)
        layout.addWidget(header_card)

        # 2. Text Content Viewer
        self.txt_content = QTextEdit()
        self.txt_content.setReadOnly(True)
        self.txt_content.setStyleSheet("""
            QTextEdit {
                background-color: #0b0f19;
                color: #e2e8f0;
                border: 1px solid #1e293b;
                border-radius: 8px;
                padding: 16px;
                font-family: 'Segoe UI', 'Leelawadee UI', sans-serif;
                font-size: 13px;
                line-height: 1.6;
            }
        """)
        self.txt_content.setMarkdown(self._raw_content)
        layout.addWidget(self.txt_content, stretch=1)

        # 3. Footer Bar
        footer_row = QHBoxLayout()
        footer_row.setSpacing(8)

        lbl_chars = QLabel(f"📄 ความยาว: {len(self._raw_content):,} อักขระ | {len(self._raw_content.splitlines()):,} บรรทัด")
        lbl_chars.setStyleSheet("color: #64748b; font-size: 11px;")
        footer_row.addWidget(lbl_chars, stretch=1)

        btn_close = QPushButton("ปิด")
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: #ffffff;
                font-weight: bold;
                border: none;
                border-radius: 6px;
                padding: 7px 22px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        btn_close.clicked.connect(self.accept)
        footer_row.addWidget(btn_close)

        layout.addLayout(footer_row)

    def _toggle_render_mode(self):
        self.is_rendered = not self.is_rendered
        if self.is_rendered:
            self.txt_content.setMarkdown(self._raw_content)
            self.btn_toggle_mode.setText("📝 ดูโค้ด Raw")
        else:
            self.txt_content.setPlainText(self._raw_content)
            self.btn_toggle_mode.setText("📖 เรนเดอร์ Markdown")

    def _copy_path(self):
        if self.bible_path:
            QApplication.clipboard().setText(self.bible_path)
            QMessageBox.information(self, "คัดลอกแล้ว", f"คัดลอกพาธคัมภีร์ลงคลิปบอร์ดแล้ว:\n{self.bible_path}")

    def _open_folder(self):
        if self.bible_path and os.path.exists(self.bible_path):
            folder = os.path.dirname(self.bible_path)
            os.system(f'explorer "{os.path.normpath(folder)}"')
        else:
            QMessageBox.warning(self, "ข้อผิดพลาด", "ไม่พบโฟลเดอร์ของคัมภีร์นี้บนเครื่อง")

    def _open_external(self):
        if self.bible_path and os.path.exists(self.bible_path):
            try:
                os.startfile(self.bible_path)
            except Exception as e:
                QMessageBox.warning(self, "ข้อผิดพลาด", f"ไม่สามารถเปิดไฟล์ด้วยโปรแกรมภายนอกได้:\n{e}")
