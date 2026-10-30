import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PyQt6.QtCore import Qt
from i18n_helper import _

class ArchiveSelectDialogQt(QDialog):
    """
    Modern Dialog to select the archive status for a project:
    - เสร็จแล้ว (Completed)
    - ยกเลิก (Cancelled)
    - ดอง / พักไว้ (On Hold)
    """

    def __init__(self, parent=None, project_name=""):
        super().__init__(parent)
        self.project_name = project_name
        self.selected_status = None

        self.setWindowTitle(_("📦 จัดเก็บโปรเจกต์เข้าคลัง (Archive)"))
        self.setFixedSize(520, 390)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(14)

        # Header Title
        lbl_title = QLabel(_("📦 จัดเก็บโปรเจกต์เข้าคลัง"))
        lbl_title.setProperty("class", "PageTitle")
        lbl_title.setStyleSheet("font-size: 17px; font-weight: bold; color: #f8fafc;")
        layout.addWidget(lbl_title)

        # Subtitle
        display_name = self.project_name if len(self.project_name) <= 35 else self.project_name[:32] + "..."
        lbl_desc = QLabel(_("โปรดเลือกสถานะของโปรเจกต์ <b>'{name}'</b> ก่อนนำเข้าคลัง:").format(name=display_name))
        lbl_desc.setStyleSheet("color: #94a3b8; font-size: 12px;")
        lbl_desc.setWordWrap(True)
        layout.addWidget(lbl_desc)

        # Options Container
        opts_box = QVBoxLayout()
        opts_box.setSpacing(10)

        # 1. เสร็จแล้ว (Completed)
        btn_comp = self._create_option_button(
            icon="✅",
            title=_("เสร็จแล้ว (Completed)"),
            desc=_("แปลเสร็จสมบูรณ์ 100% แล้ว จัดเก็บเข้าคลังเป็นผลงานที่สำเร็จ"),
            border_color="#22c55e",
            hover_bg="rgba(34, 197, 94, 0.15)",
            status_value="Completed"
        )
        opts_box.addWidget(btn_comp)

        # 2. ยกเลิก (Cancelled)
        btn_canc = self._create_option_button(
            icon="❌",
            title=_("ยกเลิก (Cancelled)"),
            desc=_("ยกเลิกการแปลหรือยุติการพัฒนาโปรเจกต์นี้ จัดเก็บเข้าคลัง"),
            border_color="#ef4444",
            hover_bg="rgba(239, 68, 68, 0.15)",
            status_value="Cancelled"
        )
        opts_box.addWidget(btn_canc)

        # 3. ดอง (On Hold)
        btn_hold = self._create_option_button(
            icon="🧊",
            title=_("ดอง / พักไว้ (On Hold)"),
            desc=_("พักการแปลไว้ชั่วคราว (ดองไว้) สามารถนำกลับมาแปลต่อได้ทุกเมื่อ"),
            border_color="#a855f7",
            hover_bg="rgba(168, 85, 247, 0.15)",
            status_value="On Hold"
        )
        opts_box.addWidget(btn_hold)

        layout.addLayout(opts_box)
        layout.addStretch()

        # Bottom Cancel Button
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_cancel = QPushButton(_("ยกเลิก"))
        btn_cancel.setProperty("class", "BtnSecondary")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #1e293b;
                color: #94a3b8;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 6px 18px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #334155;
                color: #f8fafc;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_cancel)
        layout.addLayout(btn_row)

    def _create_option_button(self, icon, title, desc, border_color, hover_bg, status_value):
        btn = QPushButton()
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #1e293b;
                border: 1px solid #334155;
                border-left: 4px solid {border_color};
                border-radius: 8px;
                text-align: left;
                padding: 10px 14px;
            }}
            QPushButton:hover {{
                background-color: {hover_bg};
                border-color: {border_color};
            }}
        """)

        # Internal Layout for Button
        btn_layout = QHBoxLayout(btn)
        btn_layout.setContentsMargins(4, 2, 8, 2)
        btn_layout.setSpacing(12)

        lbl_icon = QLabel(icon)
        lbl_icon.setStyleSheet("font-size: 22px; background: transparent;")
        lbl_icon.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        btn_layout.addWidget(lbl_icon)

        text_col = QVBoxLayout()
        text_col.setContentsMargins(0, 0, 0, 0)
        text_col.setSpacing(2)

        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(f"font-size: 13px; font-weight: bold; color: #f8fafc; background: transparent;")
        lbl_title.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        text_col.addWidget(lbl_title)

        lbl_desc = QLabel(desc)
        lbl_desc.setStyleSheet("font-size: 11px; color: #94a3b8; background: transparent;")
        lbl_desc.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        text_col.addWidget(lbl_desc)

        btn_layout.addLayout(text_col, stretch=1)

        btn.clicked.connect(lambda: self._select_and_accept(status_value))
        return btn

    def _select_and_accept(self, status_value):
        self.selected_status = status_value
        self.accept()

    @classmethod
    def get_archive_choice(cls, parent=None, project_name=""):
        """Convenience method to show dialog and return selected status or None."""
        dlg = cls(parent=parent, project_name=project_name)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            return dlg.selected_status
        return None
