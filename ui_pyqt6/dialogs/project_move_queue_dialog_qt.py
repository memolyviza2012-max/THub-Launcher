"""
Project Move & Migration Queue Dialog for THub.
Allows queuing multiple projects or all projects to move to another drive/HDD,
monitoring real-time progress, verifying 100% integrity, and safely freeing up disk space.
"""

import os
import sys
import shutil
from typing import List, Dict, Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QProgressBar, QFrame,
    QFileDialog, QMessageBox, QWidget, QAbstractItemView, QTextEdit,
    QCheckBox, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QColor, QFont, QBrush

from core.qt_tasks import BackgroundTasks, TaskDialogMixin
from i18n_helper import _
from core.project_storage_service import ProjectStorageService
from core.project_move_service import (
    ProjectMoveService, ProjectMoveWorker, ProjectMoveTask, MoveTaskStatus
)
from core.config_manager import ConfigManager


class ProjectMoveQueueDialogQt(TaskDialogMixin, QDialog):
    """
    Queue Manager Dialog for moving mod projects across drives/HDDs.
    Features:
    - Target drive storage capacity and dynamic headroom gauge.
    - Multi-select projects (All, Drive E: only, or custom).
    - Queue table with live per-project progress bars and status badges.
    - Real-time speed (MB/s), ETA, and overall queue completion.
    - Zero data-loss verified transfer with safe source space reclamation.
    """

    projects_moved = pyqtSignal(list)  # list of (project_name, new_path)

    def __init__(self, projects: List[Dict], preselected_project: Optional[Dict] = None, parent=None):
        super().__init__(parent)
        self.tasks = BackgroundTasks(self)
        self._worker_close_result = None
        self.all_projects = [dict(p) for p in (projects or [])]
        self.preselected_project = preselected_project
        self.worker: Optional[ProjectMoveWorker] = None
        self.moved_results = []  # list of (name, new_path)

        # Drive caching (includes physical HDDs and RaiDrive cloud/NAS mounts)
        self.available_drives = []

        self.setWindowTitle(_("🚚 ระบบย้ายโปรเจกต์และคืนพื้นที่ฮาร์ดดิสก์ (Project Move Queue)"))
        self.resize(920, 760)
        self.setMinimumSize(840, 680)

        self._build_ui()
        self._populate_projects_table()
        self._update_space_calculation()
        self.tasks.submit("drives", ProjectMoveService.get_available_drives, self._drives_ready,
                          lambda error: self.lbl_space_summary.setToolTip(error))

    def _drives_ready(self, drives):
        self.available_drives = drives
        self._populate_drive_shortcuts()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(18, 16, 18, 16)
        main_layout.setSpacing(12)

        # ====================================================
        # 1. Header Banner
        # ====================================================
        hdr = QHBoxLayout()
        hdr.setSpacing(12)

        lbl_icon = QLabel("🚚")
        lbl_icon.setStyleSheet("font-size: 32px;")
        hdr.addWidget(lbl_icon)

        hdr_texts = QVBoxLayout()
        hdr_texts.setSpacing(2)

        lbl_title = QLabel(_("ระบบย้ายโปรเจกต์ข้ามไดรฟ์ & กู้คืนพื้นที่ดิสก์ (Project Move Queue)"))
        lbl_title.setStyleSheet("color: #f8fafc; font-size: 16px; font-weight: bold;")
        hdr_texts.addWidget(lbl_title)

        lbl_sub = QLabel(_("ย้ายโฟลเดอร์โปรเจกต์ทั้งหมดไปยังไดรฟ์/HDD อื่น ตรวจสอบความถูกต้อง 100% และลบต้นทางเพื่อคืนพื้นที่ดิสก์อัตโนมัติ"))
        lbl_sub.setStyleSheet("color: #94a3b8; font-size: 11px;")
        hdr_texts.addWidget(lbl_sub)

        hdr.addLayout(hdr_texts, stretch=1)
        main_layout.addLayout(hdr)

        # ====================================================
        # 2. Destination Drive & Path Selection Card
        # ====================================================
        dest_card = QFrame()
        dest_card.setStyleSheet("""
            QFrame {
                background-color: rgba(30, 41, 59, 0.7);
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 6px;
            }
        """)
        dest_layout = QVBoxLayout(dest_card)
        dest_layout.setContentsMargins(10, 8, 10, 8)
        dest_layout.setSpacing(8)

        dest_row = QHBoxLayout()
        dest_row.setSpacing(8)

        lbl_dest = QLabel(_("📁 โฟลเดอร์ปลายทางที่ต้องการย้ายไป:"))
        lbl_dest.setStyleSheet("color: #38bdf8; font-weight: bold; font-size: 12px;")
        dest_row.addWidget(lbl_dest)

        # Guess default destination: pick drive with most free space that is NOT drive E:
        default_dest = self._recommend_default_dest()
        self.ent_dest = QLineEdit(default_dest)
        self.ent_dest.setPlaceholderText(_("เช่น D:\\Mod_Workspace หรือ F:\\Mod_Workspace"))
        self.ent_dest.textChanged.connect(self._on_dest_changed)
        self.ent_dest.setStyleSheet("""
            QLineEdit {
                background: #0f172a;
                color: #f8fafc;
                border: 1px solid #475569;
                border-radius: 4px;
                padding: 5px 8px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #38bdf8;
            }
        """)
        dest_row.addWidget(self.ent_dest, stretch=1)

        btn_browse = QPushButton(_("📂 เลือกโฟลเดอร์..."))
        btn_browse.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_browse.setStyleSheet("""
            QPushButton {
                background: #1e293b;
                color: #e2e8f0;
                border: 1px solid #475569;
                border-radius: 4px;
                padding: 5px 12px;
                font-size: 11px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #334155;
                color: #38bdf8;
                border-color: #38bdf8;
            }
        """)
        btn_browse.clicked.connect(self._browse_dest)
        dest_row.addWidget(btn_browse)

        dest_layout.addLayout(dest_row)

        # Quick Drive Pickers Row
        drives_row = QHBoxLayout()
        drives_row.setSpacing(6)
        lbl_drives = QLabel(_("ไดรฟ์แนะนำ:"))
        lbl_drives.setStyleSheet("color: #64748b; font-size: 11px;")
        drives_row.addWidget(lbl_drives)

        self._drives_row = drives_row
        drives_row.addStretch()
        dest_layout.addLayout(drives_row)

        # Overwrite / Merge Checkbox
        self.chk_overwrite = QCheckBox(_("เขียนทับ / อัปเดตไฟล์หากโฟลเดอร์ปลายทางมีอยู่แล้ว (Overwrite & Merge)"))
        self.chk_overwrite.setChecked(True)
        self.chk_overwrite.setStyleSheet("color: #38bdf8; font-size: 11px;")
        self.chk_overwrite.setToolTip(_("หากมีโฟลเดอร์หรือไฟล์สำรองเดิมอยู่บนไดรฟ์เป้าหมายแล้ว จะทำการอัปเดตไฟล์ให้สมบูรณ์และตรวจสอบ 100% ก่อนลบต้นทาง"))
        dest_layout.addWidget(self.chk_overwrite)

        # Live Target Space Gauge
        self.lbl_space_summary = QLabel()
        self.lbl_space_summary.setStyleSheet("color: #94a3b8; font-size: 11px;")
        dest_layout.addWidget(self.lbl_space_summary)

        main_layout.addWidget(dest_card)

        # ====================================================
        # 3. Filter & Selection Toolbar
        # ====================================================
        filter_row = QHBoxLayout()
        filter_row.setSpacing(8)

        lbl_filter = QLabel(_("🔍 ตัวกรองคิว:"))
        lbl_filter.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: bold;")
        filter_row.addWidget(lbl_filter)

        btn_style_filter = """
            QPushButton {
                background: #1e293b;
                color: #94a3b8;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 4px 10px;
                font-size: 11px;
            }
            QPushButton:hover {
                background: #334155;
                color: #f8fafc;
            }
        """

        self.btn_filter_e = QPushButton(_("💾 เฉพาะโปรเจกต์ในไดรฟ์ E: (Drive E: Only)"))
        self.btn_filter_e.setStyleSheet(btn_style_filter + "QPushButton { color: #f59e0b; font-weight: bold; }")
        self.btn_filter_e.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_filter_e.clicked.connect(self._select_drive_e_only)
        filter_row.addWidget(self.btn_filter_e)

        self.btn_select_all = QPushButton(_("☑️ เลือกทั้งหมด"))
        self.btn_select_all.setStyleSheet(btn_style_filter)
        self.btn_select_all.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_select_all.clicked.connect(lambda: self._set_all_selected(True))
        filter_row.addWidget(self.btn_select_all)

        self.btn_deselect_all = QPushButton(_("⬜ ล้างการเลือก"))
        self.btn_deselect_all.setStyleSheet(btn_style_filter)
        self.btn_deselect_all.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_deselect_all.clicked.connect(lambda: self._set_all_selected(False))
        filter_row.addWidget(self.btn_deselect_all)

        filter_row.addStretch()

        self.ent_search = QLineEdit()
        self.ent_search.setPlaceholderText(_("พิมพ์ค้นหาชื่อโปรเจกต์..."))
        self.ent_search.setFixedWidth(200)
        self.ent_search.textChanged.connect(self._filter_table_by_search)
        self.ent_search.setStyleSheet("""
            QLineEdit {
                background: #0f172a;
                color: #e2e8f0;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 3px 8px;
                font-size: 11px;
            }
        """)
        filter_row.addWidget(self.ent_search)

        main_layout.addLayout(filter_row)

        # ====================================================
        # 4. Project Queue Table
        # ====================================================
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            _("เลือก"),
            _("ชื่อโปรเจกต์"),
            _("ตำแหน่งปัจจุบัน (ต้นทาง)"),
            _("ขนาดพื้นที่"),
            _("สถานะ / ความคืบหน้า")
        ])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #0b1120;
                border: 1px solid #1e293b;
                border-radius: 6px;
                gridline-color: transparent;
            }
            QHeaderView::section {
                background-color: #1e293b;
                color: #94a3b8;
                border: none;
                border-bottom: 1px solid #334155;
                padding: 6px 8px;
                font-weight: 600;
                font-size: 11px;
            }
            QTableWidget::item {
                border-bottom: 1px solid rgba(51, 65, 85, 0.35);
                padding: 4px 6px;
                color: #e2e8f0;
            }
            QTableWidget::item:selected {
                background-color: rgba(56, 189, 248, 0.12);
            }
        """)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 56)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.table.setColumnWidth(1, 220)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(3, 100)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(4, 230)

        main_layout.addWidget(self.table, stretch=1)

        # ====================================================
        # 5. Live Queue Cockpit & Activity
        # ====================================================
        cockpit_frame = QFrame()
        cockpit_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(15, 23, 42, 0.85);
                border: 1px solid #1e293b;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        cockpit_lay = QVBoxLayout(cockpit_frame)
        cockpit_lay.setContentsMargins(10, 8, 10, 8)
        cockpit_lay.setSpacing(6)

        line_top = QHBoxLayout()
        self.lbl_queue_status = QLabel(_("สถานะ: พร้อมเริ่มการย้าย"))
        self.lbl_queue_status.setStyleSheet("color: #38bdf8; font-weight: bold; font-size: 12px;")
        line_top.addWidget(self.lbl_queue_status)
        line_top.addStretch()

        self.lbl_speed_eta = QLabel("")
        self.lbl_speed_eta.setStyleSheet("color: #10b981; font-weight: 600; font-size: 11px;")
        line_top.addWidget(self.lbl_speed_eta)
        cockpit_lay.addLayout(line_top)

        # Overall Progress Bar
        self.prog_overall = QProgressBar()
        self.prog_overall.setFixedHeight(8)
        self.prog_overall.setTextVisible(False)
        self.prog_overall.setRange(0, 100)
        self.prog_overall.setValue(0)
        self.prog_overall.setStyleSheet("""
            QProgressBar {
                background: #1e293b;
                border: none;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10b981, stop:1 #38bdf8);
                border-radius: 4px;
            }
        """)
        cockpit_lay.addWidget(self.prog_overall)

        self.lbl_current_file = QLabel(_("ยังไม่มีงานที่กำลังทำงาน"))
        self.lbl_current_file.setStyleSheet("color: #64748b; font-size: 10px;")
        cockpit_lay.addWidget(self.lbl_current_file)

        main_layout.addWidget(cockpit_frame)

        # ====================================================
        # 6. Safety Warning Alert Card
        # ====================================================
        alert_box = QFrame()
        alert_box.setStyleSheet("""
            QFrame {
                background-color: rgba(245, 158, 11, 0.1);
                border: 1px solid rgba(245, 158, 11, 0.4);
                border-radius: 6px;
                padding: 6px;
            }
        """)
        a_lay = QHBoxLayout(alert_box)
        a_lay.setContentsMargins(8, 4, 8, 4)
        a_lay.setSpacing(8)

        lbl_shield = QLabel("🛡️")
        lbl_shield.setStyleSheet("font-size: 16px;")
        a_lay.addWidget(lbl_shield)

        lbl_safety_text = QLabel(_(
            "<b>ความปลอดภัย 100%:</b> ระบบจะคัดลอกไฟล์ทั้งหมด ตรวจสอบความถูกต้องสมบูรณ์ และอัปเดตการตั้งค่าใน THub ให้ก่อนเสมอ "
            "จากนั้นจึงจะลบโฟลเดอร์ต้นทางเพื่อคืนพื้นที่ในฮาร์ดดิสก์ หากกดยกเลิกหรือเกิดข้อผิดพลาด ข้อมูลต้นทางจะไม่ถูกลบเด็ดขาด"
        ))
        lbl_safety_text.setStyleSheet("color: #fbbf24; font-size: 10px;")
        lbl_safety_text.setWordWrap(True)
        a_lay.addWidget(lbl_safety_text, stretch=1)

        main_layout.addWidget(alert_box)

        # ====================================================
        # 7. Action Footer Controls
        # ====================================================
        footer = QHBoxLayout()
        footer.setSpacing(10)

        self.btn_start = QPushButton(_("🚀 เริ่มย้ายข้อมูลตามคิว (Start Move Queue)"))
        self.btn_start.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_start.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10b981, stop:1 #059669);
                color: #ffffff;
                font-weight: bold;
                font-size: 12px;
                border: none;
                border-radius: 6px;
                padding: 8px 18px;
            }
            QPushButton:hover {
                background: #10b981;
            }
            QPushButton:disabled {
                background: #334155;
                color: #64748b;
            }
        """)
        self.btn_start.clicked.connect(self._start_queue)
        footer.addWidget(self.btn_start)

        self.btn_pause = QPushButton(_("⏸️ หยุดชั่วคราว"))
        self.btn_pause.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pause.setEnabled(False)
        self.btn_pause.setStyleSheet("""
            QPushButton {
                background: #1e293b;
                color: #e2e8f0;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 8px 14px;
                font-size: 11px;
            }
            QPushButton:hover {
                background: #334155;
            }
        """)
        self.btn_pause.clicked.connect(self._toggle_pause)
        footer.addWidget(self.btn_pause)

        self.btn_cancel = QPushButton(_("⏹️ ยกเลิก"))
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background: rgba(239, 68, 68, 0.2);
                color: #fca5a5;
                border: 1px solid rgba(239, 68, 68, 0.4);
                border-radius: 6px;
                padding: 8px 14px;
                font-size: 11px;
            }
            QPushButton:hover {
                background: rgba(239, 68, 68, 0.35);
            }
        """)
        self.btn_cancel.clicked.connect(self._cancel_queue)
        footer.addWidget(self.btn_cancel)

        footer.addStretch()

        self.btn_close = QPushButton(_("ปิดหน้าต่าง"))
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background: #1e293b;
                color: #94a3b8;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 11px;
            }
            QPushButton:hover {
                background: #334155;
                color: #f8fafc;
            }
        """)
        self.btn_close.clicked.connect(self.close)
        footer.addWidget(self.btn_close)

        main_layout.addLayout(footer)

    def _recommend_default_dest(self) -> str:
        """Finds a target drive with the highest free space (excluding E: if possible)."""
        if os.path.exists(r"Z:\07_Mod_Workspace"):
            return r"Z:\07_Mod_Workspace"
        if os.path.exists(r"D:\Mod_Workspace"):
            return r"D:\Mod_Workspace"

        best_drive = None
        best_free = -1
        for d in self.available_drives:
            letter = d["letter"].upper()
            if letter != "E:":
                if d["free"] > best_free:
                    best_free = d["free"]
                    best_drive = d
        if not best_drive and self.available_drives:
            best_drive = self.available_drives[0]
        if best_drive:
            return os.path.join(f"{best_drive['letter']}\\", "Mod_Workspace")
        return r"D:\Mod_Workspace"

    def _populate_drive_shortcuts(self):
        drives_row = self._drives_row
        # Keep the label and stretch; append only the asynchronously-discovered drives.
        while drives_row.count() > 2:
            item = drives_row.takeAt(1)
            if item.widget():
                item.widget().deleteLater()
        for d in self.available_drives:
            letter = d["letter"]
            is_cloud = d.get("is_cloud", False)
            btn_title = f"{letter} (☁️ RaiDrive)" if is_cloud else f"{letter} (ว่าง {d['free_str']})"
            btn_drv = QPushButton(btn_title)
            btn_drv.setCursor(Qt.CursorShape.PointingHandCursor)
            is_full = d["percent_used"] > 88
            border_c = "#38bdf8" if is_cloud else ("#ef4444" if is_full else "#334155")
            text_c = "#38bdf8" if is_cloud else ("#fca5a5" if is_full else "#cbd5e1")
            btn_drv.setStyleSheet(f"""
                QPushButton {{
                    background: rgba(15, 23, 42, 0.6);
                    color: {text_c};
                    border: 1px solid {border_c};
                    border-radius: 4px;
                    padding: 2px 8px;
                    font-size: 10px;
                }}
                QPushButton:hover {{
                    background: #1e293b;
                    color: #38bdf8;
                    border-color: #38bdf8;
                }}
            """)
            btn_drv.clicked.connect(lambda _, l=letter: self._apply_drive_shortcut(l))
            drives_row.insertWidget(drives_row.count() - 1, btn_drv)


    def _apply_drive_shortcut(self, drive_letter: str):
        if drive_letter.upper() == "Z:":
            if os.path.exists(r"Z:\07_Mod_Workspace"):
                self.ent_dest.setText(r"Z:\07_Mod_Workspace")
                return
            elif os.path.exists(r"Z:\0_BackUp\04_Mod_Workspace_Backup"):
                self.ent_dest.setText(r"Z:\0_BackUp\04_Mod_Workspace_Backup")
                return
            else:
                self.ent_dest.setText(r"Z:\Mod_Workspace")
                return

        curr_text = self.ent_dest.text().strip()
        folder_name = "Mod_Workspace"
        if curr_text:
            parts = os.path.splitdrive(curr_text)
            if parts[1]:
                folder_name = parts[1].lstrip("\\/")
        self.ent_dest.setText(os.path.join(f"{drive_letter}\\", folder_name))

    def _browse_dest(self):
        d = QFileDialog.getExistingDirectory(
            self,
            _("เลือกโฟลเดอร์ปลายทางสำหรับเก็บโปรเจกต์"),
            self.ent_dest.text().strip()
        )
        if d:
            self.ent_dest.setText(os.path.normpath(d))

    def _on_dest_changed(self):
        self._update_space_calculation()

    def _populate_projects_table(self):
        self.table.setRowCount(0)
        cached_sizes = ProjectStorageService.get_cached_sizes()

        for row_idx, p in enumerate(self.all_projects):
            self.table.insertRow(row_idx)

            # Checkbox
            chk = QCheckBox()
            chk.setStyleSheet("margin-left: 14px;")

            # Selection logic:
            if self.preselected_project:
                is_selected = (p.get("name") == self.preselected_project.get("name"))
            else:
                # Default: select all projects on drive E:
                p_path = p.get("path", "")
                is_selected = p_path.upper().startswith("E:")

            chk.setChecked(is_selected)
            chk.stateChanged.connect(self._update_space_calculation)

            chk_widget = QWidget()
            chk_lay = QHBoxLayout(chk_widget)
            chk_lay.addWidget(chk)
            chk_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
            chk_lay.setContentsMargins(0, 0, 0, 0)
            self.table.setCellWidget(row_idx, 0, chk_widget)

            # Project Name + Engine badge
            name_item = QTableWidgetItem(p.get("name", "Unknown"))
            name_item.setToolTip(p.get("name", "Unknown"))
            name_item.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            self.table.setItem(row_idx, 1, name_item)

            # Source Path
            src_path = p.get("path", "")
            path_item = QTableWidgetItem(src_path)
            path_item.setToolTip(src_path)
            path_item.setForeground(QBrush(QColor("#94a3b8")))
            self.table.setItem(row_idx, 2, path_item)

            # Size
            size_bytes = p.get("_storage_bytes")
            if size_bytes is None:
                cached_entry = cached_sizes.get(src_path)
                size_bytes = cached_entry.get("size", 0) if cached_entry else 0
            size_str = ProjectStorageService.format_size(size_bytes)
            size_item = QTableWidgetItem(size_str)
            size_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            size_item.setData(Qt.ItemDataRole.UserRole, size_bytes)
            self.table.setItem(row_idx, 3, size_item)

            # Status / Progress Cell
            status_widget = QWidget()
            s_lay = QVBoxLayout(status_widget)
            s_lay.setContentsMargins(4, 2, 4, 2)
            s_lay.setSpacing(2)

            lbl_stat = QLabel(_("รอคิว (Queued)"))
            lbl_stat.setObjectName("lbl_status")
            lbl_stat.setStyleSheet("color: #94a3b8; font-size: 10px;")
            s_lay.addWidget(lbl_stat)

            bar = QProgressBar()
            bar.setObjectName("bar_progress")
            bar.setFixedHeight(4)
            bar.setTextVisible(False)
            bar.setRange(0, 100)
            bar.setValue(0)
            bar.setStyleSheet("""
                QProgressBar {
                    background: #1e293b;
                    border: none;
                    border-radius: 2px;
                }
                QProgressBar::chunk {
                    background: #38bdf8;
                    border-radius: 2px;
                }
            """)
            s_lay.addWidget(bar)

            self.table.setCellWidget(row_idx, 4, status_widget)

    def _get_row_checkbox(self, row: int) -> Optional[QCheckBox]:
        w = self.table.cellWidget(row, 0)
        if w:
            return w.findChild(QCheckBox)
        return None

    def _set_all_selected(self, selected: bool):
        for r in range(self.table.rowCount()):
            chk = self._get_row_checkbox(r)
            if chk and not self.table.isRowHidden(r):
                chk.setChecked(selected)
        self._update_space_calculation()

    def _select_drive_e_only(self):
        for r in range(self.table.rowCount()):
            path_item = self.table.item(r, 2)
            chk = self._get_row_checkbox(r)
            if chk and path_item:
                is_e = path_item.text().strip().upper().startswith("E:")
                chk.setChecked(is_e)
        self._update_space_calculation()

    def _filter_table_by_search(self, query: str):
        query = query.strip().lower()
        for r in range(self.table.rowCount()):
            name_item = self.table.item(r, 1)
            path_item = self.table.item(r, 2)
            match = True
            if query:
                name_text = name_item.text().lower() if name_item else ""
                path_text = path_item.text().lower() if path_item else ""
                match = (query in name_text or query in path_text)
            self.table.setRowHidden(r, not match)

    def _update_space_calculation(self):
        dest_dir = self.ent_dest.text().strip()

        # Sum selected projects size
        selected_count = 0
        total_req_bytes = 0

        for r in range(self.table.rowCount()):
            chk = self._get_row_checkbox(r)
            if chk and chk.isChecked():
                selected_count += 1
                size_item = self.table.item(r, 3)
                if size_item:
                    total_req_bytes += (size_item.data(Qt.ItemDataRole.UserRole) or 0)

        self.btn_start.setEnabled(False)
        self.tasks.submit("drive-space", lambda: ProjectMoveService.get_drive_for_path(dest_dir),
                          lambda info: self._space_ready(dest_dir, selected_count, total_req_bytes, info),
                          lambda error: self.lbl_space_summary.setText("ตรวจพื้นที่ไม่สำเร็จ: " + error))

    def _space_ready(self, dest_dir, selected_count, total_req_bytes, drive_info):
        if self.ent_dest.text().strip() != dest_dir:
            return
        if self.worker and self.worker.isRunning():
            return
        req_str = ProjectStorageService.format_size(total_req_bytes)

        if not drive_info:
            self.lbl_space_summary.setText(_(
                "⚠️ ไม่พบข้อมูลไดรฟ์ปลายทาง | เลือกแล้ว <b>{count}</b> โปรเจกต์ (รวม <b>{req}</b>)"
            ).format(count=selected_count, req=req_str))
            self.btn_start.setEnabled(False)
            return

        free_bytes = drive_info["free"]
        free_str = drive_info["free_str"]
        letter = drive_info["letter"]

        # Check sufficiency with 256MB safety headroom
        headroom = 256 * 1024 * 1024
        is_enough = free_bytes >= (total_req_bytes + headroom)

        if is_enough:
            remaining = free_bytes - total_req_bytes
            rem_str = ProjectStorageService.format_size(remaining)
            color = "#10b981"
            status_text = _("✅ พื้นที่เพียงพอ (เหลือว่างอีก {rem} หลังย้าย)").format(rem=rem_str)
            self.btn_start.setEnabled(selected_count > 0 and bool(dest_dir))
        else:
            deficit = (total_req_bytes + headroom) - free_bytes
            def_str = ProjectStorageService.format_size(deficit)
            color = "#ef4444"
            status_text = _("❌ พื้นที่ในไดรฟ์ {drv} ไม่เพียงพอ! (ขาดอีก {def_sz})").format(drv=letter, def_sz=def_str)
            self.btn_start.setEnabled(False)

        summary_html = _(
            "<b>ไดรฟ์เป้าหมาย ({drv}):</b> ว่าง <b>{free}</b> / ทั้งหมด {total} ({pct}% ใช้งาน) | "
            "เลือกย้าย <b>{count}</b> โปรเจกต์ (รวม <b>{req}</b>) • <span style='color: {color}; font-weight: bold;'>{status}</span>"
        ).format(
            drv=letter,
            free=free_str,
            total=drive_info["total_str"],
            pct=drive_info["percent_used"],
            count=selected_count,
            req=req_str,
            color=color,
            status=status_text
        )
        self.lbl_space_summary.setText(summary_html)

    # ====================================================
    # Queue Execution
    # ====================================================
    def _start_queue(self):
        dest_dir = self.ent_dest.text().strip()
        if not dest_dir:
            QMessageBox.warning(self, _("แจ้งเตือน"), _("กรุณาระบุโฟลเดอร์ปลายทาง"))
            return

        tasks = []
        for r in range(self.table.rowCount()):
            chk = self._get_row_checkbox(r)
            if chk and chk.isChecked():
                p = self.all_projects[r]
                size_item = self.table.item(r, 3)
                sz = size_item.data(Qt.ItemDataRole.UserRole) or 0
                tasks.append(ProjectMoveTask(
                    project_name=p.get("name"),
                    source_path=p.get("path"),
                    dest_parent_dir=dest_dir,
                    total_bytes=sz,
                    allow_overwrite=self.chk_overwrite.isChecked()
                ))

        if not tasks:
            QMessageBox.information(self, _("แจ้งเตือน"), _("กรุณาเลือกโปรเจกต์ที่ต้องการย้ายอย่างน้อย 1 รายการ"))
            return

        # Confirm Move Dialog
        total_sz = sum(t.total_bytes for t in tasks)
        confirm = QMessageBox.question(
            self,
            _("ยืนยันการย้ายโปรเจกต์"),
            _(
                "คุณต้องการย้ายโปรเจกต์จำนวน {count} รายการ (รวม {sz})\n"
                "ไปยังปลายทาง:\n'{dest}'\n\n"
                "ระบบจะทำการคัดลอก ตรวจสอบความถูกต้องของไฟล์ 100% "
                "และลบข้อมูลต้นทางเพื่อคืนพื้นที่ดิสก์ในไดรฟ์เดิม\n\n"
                "ต้องการดำเนินการต่อหรือไม่?"
            ).format(count=len(tasks), sz=ProjectStorageService.format_size(total_sz), dest=dest_dir),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        # Disable configuration inputs
        self.ent_dest.setEnabled(False)
        self.btn_start.setEnabled(False)
        self.btn_filter_e.setEnabled(False)
        self.btn_select_all.setEnabled(False)
        self.btn_deselect_all.setEnabled(False)
        self.btn_pause.setEnabled(True)
        self.btn_cancel.setEnabled(True)
        self.btn_close.setEnabled(False)

        # Disable checkboxes in table
        for r in range(self.table.rowCount()):
            chk = self._get_row_checkbox(r)
            if chk:
                chk.setEnabled(False)

        # Start background worker
        self.worker = ProjectMoveWorker(tasks, parent=self)
        self.worker.task_status_changed.connect(self._on_task_status_changed)
        self.worker.task_progress.connect(self._on_task_progress)
        self.worker.task_completed.connect(self._on_task_completed)
        self.worker.task_failed.connect(self._on_task_failed)
        self.worker.queue_progress.connect(self._on_queue_progress)
        self.worker.queue_finished.connect(self._on_queue_finished)
        self.worker.start()

    def _toggle_pause(self):
        if not self.worker:
            return
        if self.worker.is_paused():
            self.worker.resume()
            self.btn_pause.setText(_("⏸️ หยุดชั่วคราว"))
            self.lbl_queue_status.setText(_("สถานะ: กำลังดำเนินการต่อ..."))
        else:
            self.worker.pause()
            self.btn_pause.setText(_("▶️ ดำเนินการต่อ"))
            self.lbl_queue_status.setText(_("สถานะ: หยุดพักชั่วคราว (Paused)"))

    def _cancel_queue(self):
        if not self.worker:
            return
        ans = QMessageBox.question(
            self,
            _("ยืนยันการยกเลิก"),
            _("คุณต้องการยกเลิกคิวการย้ายที่เหลือหรือไม่?\n(โปรเจกต์ที่กำลังย้ายจะถูกยกเลิกอย่างปลอดภัย และข้อมูลต้นทางจะไม่สูญหาย)"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if ans == QMessageBox.StandardButton.Yes:
            self.worker.cancel()
            self.btn_cancel.setEnabled(False)
            self.lbl_queue_status.setText(_("สถานะ: กำลังยกเลิกคิว..."))

    def _find_row_by_project_name(self, name: str) -> int:
        for r in range(self.table.rowCount()):
            item = self.table.item(r, 1)
            if item and item.text() == name:
                return r
        return -1

    def _on_task_status_changed(self, project_name: str, status: str, message: str):
        row = self._find_row_by_project_name(project_name)
        if row != -1:
            w = self.table.cellWidget(row, 4)
            if w:
                lbl = w.findChild(QLabel, "lbl_status")
                if lbl:
                    lbl.setText(f"{status}: {message}")
                    if status == MoveTaskStatus.COPYING.value:
                        lbl.setStyleSheet("color: #38bdf8; font-weight: bold; font-size: 10px;")
                    elif status == MoveTaskStatus.VERIFYING.value:
                        lbl.setStyleSheet("color: #a855f7; font-weight: bold; font-size: 10px;")
                    elif status == MoveTaskStatus.COMPLETED.value:
                        lbl.setStyleSheet("color: #10b981; font-weight: bold; font-size: 10px;")
                    elif status == MoveTaskStatus.FAILED.value:
                        lbl.setStyleSheet("color: #ef4444; font-weight: bold; font-size: 10px;")
                    elif status == MoveTaskStatus.CANCELLED.value:
                        lbl.setStyleSheet("color: #94a3b8; font-size: 10px;")

        self.lbl_queue_status.setText(f"โปรเจกต์: {project_name} • {message}")

    def _on_task_progress(self, project_name: str, moved: int, total: int, current_file: str, speed_bps: float, eta_sec: float):
        row = self._find_row_by_project_name(project_name)
        pct = int((moved / total) * 100) if total > 0 else 0

        if row != -1:
            w = self.table.cellWidget(row, 4)
            if w:
                bar = w.findChild(QProgressBar, "bar_progress")
                if bar:
                    bar.setValue(pct)
                lbl = w.findChild(QLabel, "lbl_status")
                if lbl:
                    moved_str = ProjectStorageService.format_size(moved)
                    total_str = ProjectStorageService.format_size(total)
                    lbl.setText(f"กำลังคัดลอก {pct}% ({moved_str}/{total_str})")

        # Format speed & ETA
        speed_mb = speed_bps / (1024 * 1024)
        if eta_sec > 60:
            eta_str = f"{int(eta_sec // 60)} นาที {int(eta_sec % 60)} วินาที"
        else:
            eta_str = f"{int(eta_sec)} วินาที"

        self.lbl_speed_eta.setText(f"⚡ {speed_mb:.1f} MB/s • เหลืออีก {eta_str}")
        self.lbl_current_file.setText(f"📄 กำลังย้าย: {current_file}")

    def _on_task_completed(self, project_name: str, new_path: str, bytes_freed: int):
        self.moved_results.append((project_name, new_path))
        row = self._find_row_by_project_name(project_name)
        if row != -1:
            # Update path item in table
            path_item = self.table.item(row, 2)
            if path_item:
                path_item.setText(new_path)
                path_item.setForeground(QBrush(QColor("#10b981")))

            w = self.table.cellWidget(row, 4)
            if w:
                bar = w.findChild(QProgressBar, "bar_progress")
                if bar:
                    bar.setValue(100)
                    bar.setStyleSheet("QProgressBar::chunk { background: #10b981; }")
                lbl = w.findChild(QLabel, "lbl_status")
                if lbl:
                    lbl.setText(f"✅ ย้ายสำเร็จ! (คืนพื้นที่ {ProjectStorageService.format_size(bytes_freed)})")
                    lbl.setStyleSheet("color: #10b981; font-weight: bold; font-size: 10px;")

    def _on_task_failed(self, project_name: str, err: str):
        row = self._find_row_by_project_name(project_name)
        if row != -1:
            w = self.table.cellWidget(row, 4)
            if w:
                lbl = w.findChild(QLabel, "lbl_status")
                if lbl:
                    lbl.setText(f"❌ ล้มเหลว: {err}")
                    lbl.setStyleSheet("color: #ef4444; font-size: 10px;")

    def _on_queue_progress(self, comp_count: int, total_count: int, moved_bytes: int, total_bytes: int):
        pct = int((moved_bytes / total_bytes) * 100) if total_bytes > 0 else 0
        self.prog_overall.setValue(pct)
        moved_s = ProjectStorageService.format_size(moved_bytes)
        total_s = ProjectStorageService.format_size(total_bytes)
        self.lbl_queue_status.setText(f"ความคืบหน้ารวม: {comp_count}/{total_count} โปรเจกต์ ({pct}%) • {moved_s} / {total_s}")

    def _on_queue_finished(self, comp_count: int, fail_count: int, total_freed: int):
        self.btn_pause.setEnabled(False)
        self.btn_cancel.setEnabled(False)
        self.btn_close.setEnabled(True)
        self.prog_overall.setValue(100 if fail_count == 0 else self.prog_overall.value())
        self.lbl_speed_eta.setText("")
        self.lbl_current_file.setText(_("🎉 คิวการทำงานเสร็จสิ้นทั้งหมด"))

        freed_str = ProjectStorageService.format_size(total_freed)
        self.lbl_queue_status.setText(_(
            "🏁 สำเร็จ {comp} โปรเจกต์, ล้มเหลว {fail} • คืนพื้นที่ได้ทั้งหมด {freed}"
        ).format(comp=comp_count, fail=fail_count, freed=freed_str))

        if self.moved_results:
            self.projects_moved.emit(self.moved_results)

        # Show Completion Notification
        if (comp_count > 0 and self._worker_close_result is None
                and not getattr(self.parent(), "_closing", False)):
            QMessageBox.information(
                self,
                _("ย้ายโปรเจกต์สำเร็จ"),
                _(
                    "ย้ายโปรเจกต์สำเร็จทั้งหมด {comp} รายการ!\n"
                    "กู้คืนพื้นที่ฮาร์ดดิสก์เดิมได้: {freed}\n\n"
                    "พาธและการตั้งค่าทั้งหมดใน THub ได้รับการอัปเดตเรียบร้อยแล้ว"
                ).format(comp=comp_count, freed=freed_str)
            )

    def done(self, result):
        """Wait for cooperative cancellation without blocking or destroying a live worker."""
        if self.worker and self.worker.isRunning():
            if self._worker_close_result is None:
                answer = QMessageBox.question(
                    self, _("กำลังทำงาน"),
                    _("ระบบกำลังย้ายโปรเจกต์อยู่ในขณะนี้ หากปิดหน้าต่างคิวจะถูกยกเลิก\nต้องการปิดหรือไม่?"),
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No)
                if answer != QMessageBox.StandardButton.Yes:
                    return
                self._worker_close_result = result
                self.setEnabled(False)
                self.worker.finished.connect(self._finish_worker_close)
                self.worker.cancel()
            return
        super().done(result)

    def _finish_worker_close(self):
        result = self._worker_close_result
        self._worker_close_result = None
        self.setEnabled(True)
        super().done(result)

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            event.ignore()
            self.done(QDialog.DialogCode.Rejected)
        else:
            super().closeEvent(event)
