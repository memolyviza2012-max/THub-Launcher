from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGridLayout, QFrame, QMessageBox, QScrollArea
)
from PyQt6.QtCore import Qt
from core.tool_launcher import ToolLauncher
from i18n_helper import _

class AppsViewQt(QWidget):
    """
    Flagship Suite Hub in PyQt6.
    Cards for TStudio, TRun, TPUA, and TGlyph with one-click launch controls.
    """

    def __init__(self, active_project=None, parent=None):
        super().__init__(parent)
        self.active_project = active_project
        self.card_buttons = {}
        self.badge_labels = []
        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 10, 16, 16)
        main_layout.setSpacing(12)

        # Header Banner
        banner = QFrame()
        banner.setProperty("class", "ContentBanner")
        b_layout = QVBoxLayout(banner)
        b_layout.setContentsMargins(16, 12, 16, 12)
        b_layout.setSpacing(3)

        self.lbl_b_title = QLabel(_("✨ The Flagship Suite"))
        self.lbl_b_title.setProperty("class", "BannerTitle")
        b_layout.addWidget(self.lbl_b_title)

        p_name = self.active_project.get("name", _("ไม่ได้เลือกโปรเจกต์")) if self.active_project else _("ไม่ได้เลือกโปรเจกต์")
        self.lbl_b_sub = QLabel(_("ชุดเครื่องมือหลักสำหรับโมเกมและแปลภาษา (โปรเจกต์ปัจจุบัน: {proj})", proj=p_name))
        self.lbl_b_sub.setProperty("class", "Muted")
        b_layout.addWidget(self.lbl_b_sub)
        main_layout.addWidget(banner)

        # Grid of Cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        grid = QGridLayout(container)
        grid.setSpacing(12)
        grid.setAlignment(Qt.AlignmentFlag.AlignTop)

        row, col = 0, 0
        for tool_id, info in ToolLauncher.FLAGSHIP_TOOLS.items():
            card = self._create_card(tool_id, info)
            grid.addWidget(card, row, col)
            col += 1
            if col >= 2:
                col = 0
                row += 1

        scroll.setWidget(container)
        main_layout.addWidget(scroll, stretch=1)

    def _create_card(self, tool_id, info):
        card = QFrame()
        card.setProperty("class", "PanelCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)

        # Title + Badge
        top_row = QHBoxLayout()
        lbl_name = QLabel(info["name"])
        lbl_name.setStyleSheet(f"color: {info['color']}; font-size: 16px; font-weight: bold;")
        top_row.addWidget(lbl_name)
        top_row.addStretch()

        if info["supports_project"]:
            lbl_badge = QLabel(f" {_('พ่วงโปรเจกต์')} ")
            lbl_badge.setStyleSheet("background-color: rgba(56, 189, 248, 0.15); color: #0284c7; border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 4px; font-size: 9px; padding: 2px 4px; font-weight: bold;")
            top_row.addWidget(lbl_badge)
            self.badge_labels.append(lbl_badge)
        layout.addLayout(top_row)

        # Description
        lbl_desc = QLabel(_(info["desc"]))
        lbl_desc.setProperty("class", "Muted")
        lbl_desc.setWordWrap(True)
        layout.addWidget(lbl_desc)

        layout.addSpacing(6)

        # Launch Button
        btn = QPushButton(f"🚀 {_('เปิด')} {info['name']}")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {info['color']};
                color: #081326;
                border: none;
                border-radius: 6px;
                padding: 7px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                opacity: 0.9;
            }}
        """)
        btn.clicked.connect(lambda _, tid=tool_id: self._launch_tool(tid))
        layout.addWidget(btn)
        self.card_buttons[tool_id] = btn

        return card

    def retranslate_ui(self):
        """Update localized strings dynamically upon language change."""
        self.lbl_b_title.setText(_("✨ The Flagship Suite"))
        p_name = self.active_project.get("name", _("ไม่ได้เลือกโปรเจกต์")) if self.active_project else _("ไม่ได้เลือกโปรเจกต์")
        self.lbl_b_sub.setText(_("ชุดเครื่องมือหลักสำหรับโมเกมและแปลภาษา (โปรเจกต์ปัจจุบัน: {proj})", proj=p_name))
        for tool_id, btn in self.card_buttons.items():
            name = ToolLauncher.FLAGSHIP_TOOLS.get(tool_id, {}).get("name", tool_id)
            btn.setText(f"🚀 {_('เปิด')} {name}")
        for lbl_badge in self.badge_labels:
            lbl_badge.setText(f" {_('พ่วงโปรเจกต์')} ")

    def _launch_tool(self, tool_id):
        p_path = self.active_project.get("path") if self.active_project else None
        try:
            ToolLauncher.launch_flagship(tool_id, project_path=p_path)
        except Exception as e:
            QMessageBox.critical(self, _("Error"), f"{_('เปิดโปรแกรม {name} ล้มเหลว', name=tool_id)}:\n{e}")
