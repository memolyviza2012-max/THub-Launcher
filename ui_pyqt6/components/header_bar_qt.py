from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, QLineEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from i18n_helper import _

class HeaderBarQt(QWidget):
    """
    Top Action Bar in PyQt6.
    Instant search, filter counter, and quick action buttons.
    """

    search_changed = pyqtSignal(str)
    add_clicked = pyqtSignal()
    import_clicked = pyqtSignal()
    adopt_clicked = pyqtSignal()
    ai_copilot_clicked = pyqtSignal()
    settings_clicked = pyqtSignal()

    def __init__(self, title="Dashboard", total_count=0, parent=None):
        super().__init__(parent)
        self.setObjectName("HeaderBar")
        self.setFixedHeight(56)
        self.title_text = title
        self.total_count = total_count
        self.filtered_count = total_count

        self._pending_query = ""
        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(120)
        self._search_timer.timeout.connect(self._emit_search)

        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(12)

        # Left: Title + Counter
        self.lbl_title = QLabel(_(self.title_text))
        self.lbl_title.setProperty("class", "PageTitle")
        layout.addWidget(self.lbl_title)

        self.lbl_counter = QLabel(_("แสดง {filtered} จาก {total}", filtered=self.filtered_count, total=self.total_count))
        self.lbl_counter.setProperty("class", "SubText")
        layout.addWidget(self.lbl_counter)

        layout.addStretch()

        # Right: Search Box
        self.search_box = QLineEdit()
        self.search_box.setProperty("class", "SearchBox")
        self.search_box.setPlaceholderText(_("🔍 ค้นหาชื่อเกม..."))
        self.search_box.setFixedWidth(210)
        self.search_box.textChanged.connect(self._on_search_text_changed)
        layout.addWidget(self.search_box)

        # Action Button: Adopt Legacy / Continue Mod
        self.btn_adopt = QPushButton(_("🔄 สานต่องานม็อด"))
        self.btn_adopt.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_adopt.setToolTip(_("สแกนและนำเข้าโปรเจกต์ม็อดเก่า/ภายนอก เพื่อจัดโครงสร้างใหม่และสานต่องานด้วย AI"))
        self.btn_adopt.setStyleSheet("""
            QPushButton {
                background-color: rgba(139, 92, 246, 0.15);
                color: #c084fc;
                border: 1px solid rgba(168, 85, 247, 0.45);
                border-radius: 6px;
                padding: 6px 14px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(139, 92, 246, 0.35);
                color: #ffffff;
                border-color: #a855f7;
            }
        """)
        self.btn_adopt.clicked.connect(self.adopt_clicked.emit)
        layout.addWidget(self.btn_adopt)

        # Action Button: Import
        self.btn_import = QPushButton(_("📂 นำเข้า"))
        self.btn_import.setProperty("class", "BtnSecondary")
        self.btn_import.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_import.clicked.connect(self.import_clicked.emit)
        layout.addWidget(self.btn_import)

        # Action Button: Add Project
        self.btn_add = QPushButton(_("➕ เพิ่มโปรเจกต์"))
        self.btn_add.setProperty("class", "BtnPrimary")
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.clicked.connect(self.add_clicked.emit)
        layout.addWidget(self.btn_add)

    def retranslate_ui(self):
        """Update header bar labels when language changes."""
        self.lbl_title.setText(_(self.title_text))
        self.lbl_counter.setText(_("แสดง {filtered} จาก {total}", filtered=self.filtered_count, total=self.total_count))
        self.search_box.setPlaceholderText(_("🔍 ค้นหาชื่อเกม..."))
        self.btn_adopt.setText(_("🔄 สานต่องานม็อด"))
        self.btn_import.setText(_("📂 นำเข้า"))
        self.btn_add.setText(_("➕ เพิ่มโปรเจกต์"))

    def set_title(self, title):
        self.title_text = title
        self.lbl_title.setText(_(title))

    def update_counts(self, filtered, total):
        self.filtered_count = filtered
        self.total_count = total
        self.lbl_counter.setText(_("แสดง {filtered} จาก {total}", filtered=filtered, total=total))

    def _on_search_text_changed(self, text):
        self._pending_query = text
        self._search_timer.start()

    def _emit_search(self):
        self.search_changed.emit(self._pending_query)
