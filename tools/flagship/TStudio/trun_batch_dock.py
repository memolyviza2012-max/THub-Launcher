from translation_transport import RowTarget
# -*- coding: utf-8 -*-
"""
trun_batch_dock.py
==================
Modular TRun Batch Engine Dock for TStudio.
Provides both Active Project Live Translation (in-memory CAT table updates)
and Multi-file/Folder Batch Queue Translation.
"""

import os
import sys
import csv
import time
import glob
import subprocess

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QSplitter, QGroupBox, QComboBox, QMessageBox, QTextEdit, QFileDialog,
    QSpinBox, QCheckBox, QProgressBar, QSlider, QTabWidget, QTableWidget,
    QTableWidgetItem, QTimeEdit, QAbstractItemView, QDockWidget, QRadioButton,
    QButtonGroup, QHeaderView, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot, QTime, QTimer, QLocale, QThreadPool
from PyQt6.QtGui import QColor, QBrush

# Ensure Core and TRun can be imported
tstudio_dir = os.path.dirname(os.path.abspath(__file__))
flagship_dir = os.path.abspath(os.path.join(tstudio_dir, '..'))
core_dir = os.path.join(flagship_dir, 'Core')
trun_dir = os.path.join(flagship_dir, 'TRun')

for p in [core_dir, trun_dir]:
    if p not in sys.path:
        sys.path.insert(0, p)

from tstudio_core import TStudioCore, CoreAI, TFormatManager, TPakManager
from tstudio_ui_shared import SettingsDialog, PromptSettingsDialog, GlossaryWidget, SmartImportDialog, ApiWorker
from trun_app import TRunWorker, TRunWorkerSignals

try:
    from trun_i18n import _
except ImportError:
    def _(k): return k


class TRunBatchDock(QWidget):
    """
    TRun Batch Engine Workspace for TStudio.
    Provides both Active Project Live Translation (in-memory CAT table updates)
    and Multi-file/Folder Batch Queue Translation in a dedicated full-page layout.
    """
    log_emitted = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("workspace_trun_batch")
        self.parent_window = parent
        self.is_running = False
        self.queue = []
        self._workers = []
        self.threadpool = QThreadPool.globalInstance()
        self.current_job_start_time = 0.0

        # High-performance async UI buffering
        self._log_queue = []
        self._log_timer = QTimer(self)
        self._log_timer.setInterval(50)  # Flush batched logs every 50ms
        self._log_timer.timeout.connect(self._flush_logs)

        self._stats_timer = QTimer(self)
        self._stats_timer.setSingleShot(True)
        self._stats_timer.setInterval(600)  # Debounce stats updates to at most once per 600ms
        self._stats_timer.timeout.connect(self._flush_stats_update)

        self._active_id_to_idx = {}

        self.init_ui()

    def _on_return_to_studio_clicked(self):
        if self.parent_window and hasattr(self.parent_window, 'switch_workspace_mode'):
            self.parent_window.switch_workspace_mode('studio')

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(8)

        # ── Sleek Top Navigation & Header Bar ──
        nav_bar = QWidget()
        nav_bar.setStyleSheet("background: #181825; border: 1px solid #313244; border-radius: 6px;")
        nav_layout = QHBoxLayout(nav_bar)
        nav_layout.setContentsMargins(12, 6, 12, 6)
        nav_layout.setSpacing(12)

        lbl_icon = QLabel("⚡")
        lbl_icon.setStyleSheet("font-size: 20px;")
        nav_layout.addWidget(lbl_icon)

        title_box = QVBoxLayout()
        title_box.setSpacing(1)
        lbl_title = QLabel("TRun — แดชบอร์ดระบบแปลอัตโนมัติความเร็วสูง (Batch AI Runner Workspace)")
        lbl_title.setStyleSheet("font-weight: bold; font-size: 13px; color: #a6e3a1;")
        lbl_sub = QLabel("ระบบแปลอัตโนมัติเต็มหน้าจอ แปลไฟล์เดี่ยวที่กำลังเปิดอยู่ หรือต่อคิวหลายไฟล์พร้อมกันแบบมัลติเธรด")
        lbl_sub.setStyleSheet("font-size: 11px; color: #a6adc8;")
        title_box.addWidget(lbl_title)
        title_box.addWidget(lbl_sub)
        nav_layout.addLayout(title_box, stretch=1)

        btn_back_studio = QPushButton("🔙 กลับไปหน้าแปลภาษา (CAT Studio) [F1]")
        btn_back_studio.setStyleSheet("""
            QPushButton {
                background: #313244;
                color: #89b4fa;
                font-weight: bold;
                font-size: 12px;
                padding: 6px 14px;
                border: 1px solid #45475a;
                border-radius: 5px;
            }
            QPushButton:hover {
                background: #89b4fa;
                color: #1e1e2e;
            }
        """)
        btn_back_studio.setToolTip("สลับกลับไปยังหน้าจอแปลภาษาหลักแบบ 3 คอลัมน์ (F1)")
        btn_back_studio.clicked.connect(self._on_return_to_studio_clicked)
        nav_layout.addWidget(btn_back_studio)

        layout.addWidget(nav_bar)

        # ── Mode Selection Header ──
        mode_box = QGroupBox("🎯 โหมดการรันแปล (Translation Target)")
        mode_box.setStyleSheet("QGroupBox { font-weight: bold; color: #89b4fa; }")
        mode_layout = QHBoxLayout(mode_box)
        mode_layout.setContentsMargins(8, 6, 8, 6)

        self.radio_active_file = QRadioButton("🎯 ไฟล์ที่กำลังเปิดอยู่ใน TStudio (ทั้งไฟล์)")
        self.radio_active_file.setChecked(True)
        self.radio_active_file.setStyleSheet("color: #a6e3a1; font-weight: bold;")
        self.radio_active_file.toggled.connect(self._on_target_mode_changed)

        self.radio_selected_rows = QRadioButton("✨ เฉพาะแถวที่เลือกในตาราง (Selected Rows Only)")
        self.radio_selected_rows.setStyleSheet("color: #cba6f7; font-weight: bold;")
        self.radio_selected_rows.toggled.connect(self._on_target_mode_changed)

        self.radio_file_queue = QRadioButton("📁 คิวไฟล์ภายนอก (Batch Queue Files/Folders)")
        self.radio_file_queue.setStyleSheet("color: #fab387;")
        self.radio_file_queue.toggled.connect(self._on_target_mode_changed)

        mode_layout.addWidget(self.radio_active_file)
        mode_layout.addWidget(self.radio_selected_rows)
        mode_layout.addWidget(self.radio_file_queue)
        mode_layout.addStretch()
        layout.addWidget(mode_box)

        # ── Active File Info Banner ──
        self.active_file_banner = QWidget()
        active_banner_layout = QHBoxLayout(self.active_file_banner)
        active_banner_layout.setContentsMargins(4, 2, 4, 2)
        self.lbl_active_info = QLabel("📄 ไฟล์ปัจจุบัน: ยังไม่มีไฟล์เปิดอยู่")
        self.lbl_active_info.setStyleSheet("color: #cdd6f4; font-size: 12px; background: #313244; padding: 6px 12px; border-radius: 4px;")
        btn_refresh_info = QPushButton("🔄 อัปเดตข้อมูล")
        btn_refresh_info.setStyleSheet("background: #45475a; color: #cdd6f4; padding: 4px 10px; font-size: 11px;")
        btn_refresh_info.clicked.connect(self.sync_active_file_info)

        btn_clear_active = QPushButton("🧹 ลบคำแปลทั้งหมด...")
        btn_clear_active.setToolTip("ลบคำแปลทั้งหมดในไฟล์ปัจจุบันกลับเป็นสถานะ 'รอแปล' เพื่อเริ่มรันใหม่ตั้งแต่ต้น")
        btn_clear_active.setStyleSheet("background: #3c2432; color: #f5c2e7; border: 1px solid #7c3a5e; padding: 4px 10px; font-size: 11px;")
        btn_clear_active.clicked.connect(self.on_clear_active_file_translations)

        active_banner_layout.addWidget(self.lbl_active_info, stretch=1)
        active_banner_layout.addWidget(btn_refresh_info)
        active_banner_layout.addWidget(btn_clear_active)
        layout.addWidget(self.active_file_banner)

        # ── Splitter: Config (Left) and Dashboard (Right) ──
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # ── LEFT: Settings & Engine Controls ──
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 4, 0)
        left_layout.setSpacing(6)

        # File Queue Group (Visible only in Queue mode)
        self.grp_queue = QGroupBox("📁 คิวไฟล์สำหรับรันแปล (Queue)")
        l_queue = QVBoxLayout(self.grp_queue)
        h_q_btns = QHBoxLayout()
        btn_add_file = QPushButton("+ เพิ่มไฟล์...")
        btn_add_file.clicked.connect(self.browse_input_files)
        btn_add_folder = QPushButton("+ เพิ่มโฟลเดอร์...")
        btn_add_folder.clicked.connect(self.browse_input_folder)
        btn_remove_q = QPushButton("ลบที่เลือก")
        btn_remove_q.setStyleSheet("color: #f38ba8;")
        btn_remove_q.clicked.connect(self.remove_selected_queue)
        btn_clear_q = QPushButton("ล้างทั้งหมด")
        btn_clear_q.setStyleSheet("color: #f38ba8;")
        btn_clear_q.clicked.connect(self.clear_queue)
        h_q_btns.addWidget(btn_add_file)
        h_q_btns.addWidget(btn_add_folder)
        h_q_btns.addWidget(btn_remove_q)
        h_q_btns.addWidget(btn_clear_q)
        l_queue.addLayout(h_q_btns)

        self.tbl_input = QTableWidget(0, 2)
        self.tbl_input.setHorizontalHeaderLabels(["File Path", "Profile"])
        self.tbl_input.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tbl_input.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_input.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tbl_input.setFixedHeight(100)
        l_queue.addWidget(self.tbl_input)
        left_layout.addWidget(self.grp_queue)
        self.grp_queue.setVisible(False)

        # Batch Engine Parameters
        grp_engine = QGroupBox("⚡ พารามิเตอร์ระบบ AI (Engine Parameters)")
        l_engine = QVBoxLayout(grp_engine)
        l_engine.setSpacing(6)

        # Batch Size Slider
        h_batch = QHBoxLayout()
        h_batch.addWidget(QLabel("ขนาด Batch (แถว):"))
        self.slider_batch = QSlider(Qt.Orientation.Horizontal)
        self.slider_batch.setRange(1, 100)
        self.slider_batch.setValue(50)
        self.spin_batch_val = QSpinBox()
        self.spin_batch_val.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
        self.spin_batch_val.setRange(1, 100)
        self.spin_batch_val.setValue(50)
        self.spin_batch_val.setFixedWidth(65)
        self.slider_batch.valueChanged.connect(self.spin_batch_val.setValue)
        self.spin_batch_val.valueChanged.connect(self.slider_batch.setValue)
        h_batch.addWidget(self.slider_batch)
        h_batch.addWidget(self.spin_batch_val)

        self.chk_unlock_risk = QCheckBox("ปลดล็อก >100")
        self.chk_unlock_risk.setStyleSheet("color: #f38ba8; font-size: 11px;")
        self.chk_unlock_risk.toggled.connect(self._toggle_risk_mode)
        h_batch.addWidget(self.chk_unlock_risk)
        l_engine.addLayout(h_batch)

        # Delay & Retry & Threads
        h_params = QHBoxLayout()
        h_params.addWidget(QLabel("Delay (ms):"))
        self.spin_delay = QSpinBox()
        self.spin_delay.setRange(0, 10000)
        self.spin_delay.setValue(200)
        self.spin_delay.setFixedWidth(70)
        h_params.addWidget(self.spin_delay)

        h_params.addWidget(QLabel("Retries:"))
        self.spin_retry = QSpinBox()
        self.spin_retry.setRange(0, 10)
        self.spin_retry.setValue(3)
        self.spin_retry.setFixedWidth(50)
        h_params.addWidget(self.spin_retry)

        h_params.addWidget(QLabel("Threads:"))
        self.spin_threads = QSpinBox()
        self.spin_threads.setRange(1, 100)
        self.spin_threads.setValue(16)
        self.spin_threads.setFixedWidth(55)
        h_params.addWidget(self.spin_threads)
        l_engine.addLayout(h_params)

        # Token Burner Mode
        self.chk_token_burner = QCheckBox("⚡ Token Burner Mode (เร็วสูงสุด แปลทีละ 1 แถวแบบขนาน)")
        self.chk_token_burner.setStyleSheet("color: #f9e2af; font-weight: bold;")
        self.chk_token_burner.toggled.connect(self._on_token_burner_toggled)
        l_engine.addWidget(self.chk_token_burner)

        # Post Processing Options
        grp_opts = QGroupBox("🛡️ การประมวลผลและการกรอง (Filters & Guards)")
        l_opts = QVBoxLayout(grp_opts)
        self.chk_mask = QCheckBox("บังคับแท็กโค้ด / พารามิเตอร์ ({0}, <tag>) ไม่ให้ AI แก้")
        self.chk_mask.setChecked(True)
        self.chk_glossary = QCheckBox("บังคับใช้คำศัพท์จาก Glossary (Enforce Terminology)")
        self.chk_glossary.setChecked(True)
        self.chk_pua = QCheckBox("แปลงรหัสอักษรพิเศษ TPUA อัตโนมัติ")
        self.chk_pua.setChecked(False)
        self.chk_cjk_filter = QCheckBox("🇨🇳 กรอง/ล้างภาษาจีนที่หลุดมา (CJK Leak Filter & Auto-Retry)")
        self.chk_cjk_filter.setChecked(True)
        self.chk_cjk_filter.setStyleSheet("color: #fab387; font-weight: bold;")
        self.chk_eng_filter = QCheckBox("🇬🇧 กรอง/แปลซ้ำภาษาอังกฤษตกค้าง (English Leak Auto-Retry)")
        self.chk_eng_filter.setChecked(False)
        self.chk_eng_filter.setStyleSheet("color: #89b4fa; font-weight: bold;")
        self.chk_dedup = QCheckBox("⚡ แปลเฉพาะข้อความไม่ซ้ำและกระจายคำแปลอัตโนมัติ (Deduplication)")
        self.chk_dedup.setChecked(True)
        self.chk_dedup.setStyleSheet("color: #a6e3a1; font-weight: bold;")
        self.chk_dedup.setToolTip("แปลข้อความที่เหมือนกันเพียงครั้งเดียว แล้วกระจายผลลัพธ์ไปยังทุกแถว ประหยัดโทเค็นได้ 50-80%")
        self.chk_engine_filter = QCheckBox("🛡️ กรองคำสั่งเอนจิน/แท็กล้วน ไม่ส่ง AI (Engine Junk Filter)")
        self.chk_engine_filter.setChecked(True)
        self.chk_engine_filter.setStyleSheet("color: #f9e2af; font-weight: bold;")
        self.chk_engine_filter.setToolTip("กรองคำสั่งสคริปต์ภายในเอนจิน (เช่น ■... ใน WOLF RPG) หรือแท็กตัวแปรล้วน ไม่ส่งไป AI เพื่อป้องกันโทเค็นรั่วไหล")

        l_opts.addWidget(self.chk_mask)
        l_opts.addWidget(self.chk_glossary)
        l_opts.addWidget(self.chk_pua)
        l_opts.addWidget(self.chk_cjk_filter)
        l_opts.addWidget(self.chk_eng_filter)
        l_opts.addWidget(self.chk_dedup)
        l_opts.addWidget(self.chk_engine_filter)
        l_engine.addWidget(grp_opts)

        # Peak Hour Management
        grp_peak = QGroupBox("⏳ Peak-Hour & Scheduling")
        l_peak = QVBoxLayout(grp_peak)
        self.chk_peak = QCheckBox("เปิดระบบบริหารช่วงชั่วโมงหนาแน่น (Peak-Hour)")
        l_peak.addWidget(self.chk_peak)

        self.w_peak_opts = QWidget()
        self.w_peak_opts.setEnabled(False)
        self.chk_peak.toggled.connect(self.w_peak_opts.setEnabled)
        l_peak_opts = QVBoxLayout(self.w_peak_opts)
        l_peak_opts.setContentsMargins(12, 0, 0, 0)

        h_pt = QHBoxLayout()
        self.time_peak_start = QTimeEdit(QTime(18, 0))
        self.time_peak_start.setDisplayFormat("HH:mm")
        self.time_peak_end = QTimeEdit(QTime(22, 0))
        self.time_peak_end.setDisplayFormat("HH:mm")
        h_pt.addWidget(QLabel("ช่วงเวลา:"))
        h_pt.addWidget(self.time_peak_start)
        h_pt.addWidget(QLabel("ถึง:"))
        h_pt.addWidget(self.time_peak_end)
        l_peak_opts.addLayout(h_pt)

        h_pa = QHBoxLayout()
        self.cbo_peak_action = QComboBox()
        self.cbo_peak_action.addItems(["พักการแปลชั่วคราว (Pause 60s)", "สลับไปใช้ Profile สำรอง"])
        h_pa.addWidget(QLabel("เมื่อถึงเวลา:"))
        h_pa.addWidget(self.cbo_peak_action)
        l_peak_opts.addLayout(h_pa)
        l_peak.addWidget(self.w_peak_opts)
        l_engine.addWidget(grp_peak)

        left_layout.addWidget(grp_engine)
        left_layout.addStretch()
        splitter.addWidget(left_widget)

        # ── RIGHT: Dashboard, Dual Progress Bars & Logs ──
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(4, 0, 0, 0)
        right_layout.setSpacing(6)

        # Progress Stats
        h_batch_stat = QHBoxLayout()
        self.lbl_batch_progress = QLabel("Batch Progress: 0 / 0 (0%)")
        self.lbl_batch_progress.setStyleSheet("color: #89b4fa; font-weight: bold; font-size: 12px;")
        self.lbl_eta = QLabel("ETA: --:--:--")
        self.lbl_eta.setStyleSheet("color: #a6adc8; font-size: 11px;")
        h_batch_stat.addWidget(self.lbl_batch_progress)
        h_batch_stat.addStretch()
        h_batch_stat.addWidget(self.lbl_eta)
        right_layout.addLayout(h_batch_stat)

        self.batch_bar = QProgressBar()
        self.batch_bar.setValue(0)
        self.batch_bar.setFixedHeight(12)
        self.batch_bar.setTextVisible(False)
        self.batch_bar.setStyleSheet("QProgressBar { border: 1px solid #45475a; border-radius: 4px; background: #313244; } QProgressBar::chunk { background: #89b4fa; border-radius: 3px; }")
        right_layout.addWidget(self.batch_bar)

        h_line_stat = QHBoxLayout()
        self.lbl_line_progress = QLabel("Lines Progress: 0 / 0 (0%)")
        self.lbl_line_progress.setStyleSheet("color: #a6e3a1; font-weight: bold; font-size: 12px;")
        h_line_stat.addWidget(self.lbl_line_progress)
        h_line_stat.addStretch()
        right_layout.addLayout(h_line_stat)

        self.lines_bar = QProgressBar()
        self.lines_bar.setValue(0)
        self.lines_bar.setFixedHeight(14)
        self.lines_bar.setStyleSheet("QProgressBar { border: 1px solid #45475a; border-radius: 4px; text-align: center; color: #1e1e2e; font-weight: bold; background: #313244; } QProgressBar::chunk { background: #a6e3a1; border-radius: 3px; }")
        right_layout.addWidget(self.lines_bar)

        # Dashboard Tabs
        self.dash_tabs = QTabWidget()
        
        # Log Tab
        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.document().setMaximumBlockCount(1500)
        self.txt_log.setStyleSheet("background: #181825; color: #a6adc8; font-family: Consolas, monospace; font-size: 12px;")
        self.dash_tabs.addTab(self.txt_log, "💻 Live Terminal Log")

        # Queue Status Tab
        self.tbl_queue_status = QTableWidget(0, 2)
        self.tbl_queue_status.setHorizontalHeaderLabels(["File", "Status"])
        self.tbl_queue_status.horizontalHeader().setStretchLastSection(True)
        self.tbl_queue_status.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl_queue_status.setStyleSheet("QTableWidget { background: #181825; color: #cdd6f4; border: 1px solid #313244; }")
        self.dash_tabs.addTab(self.tbl_queue_status, "📋 Queue Status")

        right_layout.addWidget(self.dash_tabs)

        # Action Buttons
        h_action = QHBoxLayout()
        self.btn_start = QPushButton("⚡ เริ่มรันแปล (Start Translation)")
        self.btn_start.setStyleSheet("background: #a6e3a1; color: #1e1e2e; font-size: 14px; font-weight: bold; padding: 8px 16px; border-radius: 4px;")
        self.btn_start.clicked.connect(self.start_translation)

        self.btn_stop = QPushButton("⏹️ หยุด (Stop)")
        self.btn_stop.setStyleSheet("background: #f38ba8; color: #1e1e2e; font-size: 14px; font-weight: bold; padding: 8px 16px; border-radius: 4px;")
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.stop_translation)

        self.btn_deploy_all = QPushButton("📦 Deploy All")
        self.btn_deploy_all.setStyleSheet("background: #fab387; color: #1e1e2e; font-size: 13px; font-weight: bold; padding: 8px 14px; border-radius: 4px;")
        self.btn_deploy_all.clicked.connect(self.deploy_all)

        h_action.addWidget(self.btn_start, stretch=2)
        h_action.addWidget(self.btn_stop, stretch=1)
        h_action.addWidget(self.btn_deploy_all, stretch=1)
        right_layout.addLayout(h_action)

        splitter.addWidget(right_widget)
        splitter.setSizes([520, 980])
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        layout.addWidget(splitter, 1)

    def get_selected_source_row_indices(self):
        """Retrieves list of zero-based source row indices currently selected in TStudio table."""
        if not self.parent_window:
            return []
        table = getattr(self.parent_window, 'table', None)
        proxy = getattr(self.parent_window, 'proxy', None)
        if not table or not proxy:
            return []
        sel_model = table.selectionModel()
        if not sel_model:
            return []
        selected_indexes = sel_model.selectedRows()
        if not selected_indexes:
            return []
        source_indices = []
        for idx in selected_indexes:
            if idx.isValid():
                try:
                    src_idx = proxy.mapToSource(idx)
                    if src_idx.isValid():
                        source_indices.append(src_idx.row())
                except Exception:
                    pass
        return sorted(list(set(source_indices)))

    def _on_target_mode_changed(self):
        is_queue = self.radio_file_queue.isChecked()
        self.active_file_banner.setVisible(not is_queue)
        self.grp_queue.setVisible(is_queue)
        if not is_queue:
            self.sync_active_file_info()

    def sync_active_file_info(self):
        """Refreshes the active file path, untranslated count, and selected row status from TStudio."""
        if not self.parent_window:
            return
        
        csv_path = getattr(self.parent_window, 'csv_path', None)
        model = getattr(self.parent_window, 'model', None)
        
        if not csv_path or not os.path.exists(csv_path) or not model:
            self.lbl_active_info.setText("📄 ไฟล์ปัจจุบัน: ยังไม่มีไฟล์โปรเจกต์เปิดอยู่ กรุณาเปิดไฟล์ CSV ก่อน")
            self.lbl_active_info.setStyleSheet("color: #f38ba8; font-size: 12px; background: #313244; padding: 6px 12px; border-radius: 4px;")
            self.radio_selected_rows.setText("✨ เฉพาะแถวที่เลือกในตาราง (ยังไม่ได้เปิดไฟล์)")
            self.radio_selected_rows.setEnabled(False)
            return

        selected_indices = self.get_selected_source_row_indices()
        sel_count = len(selected_indices)
        if sel_count > 0:
            self.radio_selected_rows.setEnabled(True)
            self.radio_selected_rows.setText(f"✨ เฉพาะแถวที่เลือกในตาราง ({sel_count:,} แถว) [แปลใหม่]")
        else:
            self.radio_selected_rows.setText("✨ เฉพาะแถวที่เลือกในตาราง (ยังไม่ได้เลือกแถว)")
            if self.radio_selected_rows.isChecked():
                self.radio_active_file.setChecked(True)
            self.radio_selected_rows.setEnabled(False)

        total_rows = len(model._data)
        untrans_count = sum(1 for item in model._data if not item.get("trans", "").strip())
        base_name = os.path.basename(csv_path)

        if self.radio_selected_rows.isChecked():
            self.lbl_active_info.setText(
                f"📄 ไฟล์: <b>{base_name}</b> | โหมด: <span style='color: #cba6f7; font-weight: bold;'>เฉพาะ {sel_count:,} แถวที่เลือก</span> "
                f"(จะรวมกลุ่มแปลแบบ Batch ใน TRun และเขียนทับแปลใหม่)"
            )
        else:
            self.lbl_active_info.setText(
                f"📄 ไฟล์ปัจจุบัน: <b>{base_name}</b> | ทั้งหมด: <b>{total_rows:,}</b> บรรทัด | "
                f"ยังไม่แปล: <span style='color: #fab387; font-weight: bold;'>{untrans_count:,}</span> บรรทัด"
            )
        self.lbl_active_info.setStyleSheet("color: #cdd6f4; font-size: 12px; background: #313244; padding: 6px 12px; border-radius: 4px;")

    def on_clear_active_file_translations(self):
        """Triggers clear_all_translations on parent window and refreshes the banner."""
        if hasattr(self, 'parent_window') and self.parent_window:
            if hasattr(self.parent_window, 'clear_all_translations'):
                self.parent_window.clear_all_translations(only_ai=False)
            self.sync_active_file_info()

    def update_active_file_banner(self):
        """Alias for sync_active_file_info."""
        self.sync_active_file_info()

    def _toggle_risk_mode(self, checked):
        if checked:
            reply = QMessageBox.warning(
                self, "ปลดล็อกขนาด Batch",
                "คำเตือน: การส่ง Batch ขนาดเกิน 100 บรรทัดอาจทำให้คำตอบจาก AI ถูกตัด หรือเกิน Token Limit ของผู้ให้บริการ\n\nยืนยันต้องการเปิดใช้งานหรือไม่?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.slider_batch.setRange(1, 500)
                self.spin_batch_val.setRange(1, 500)
            else:
                self.chk_unlock_risk.setChecked(False)
        else:
            self.slider_batch.setRange(1, 100)
            self.spin_batch_val.setRange(1, 100)
            if self.slider_batch.value() > 100:
                self.slider_batch.setValue(100)

    def _on_token_burner_toggled(self, checked):
        if checked:
            self.spin_threads.setValue(32)
            self.slider_batch.setEnabled(False)
            self.spin_batch_val.setEnabled(False)
            self.log("⚡ เปิดโหมด Token Burner: ปิดระบบ Batching และรัน 1 API call ต่อ 1 บรรทัดแบบขนานเต็มพิกัด", "#f9e2af")
        else:
            self.spin_threads.setValue(16)
            self.slider_batch.setEnabled(True)
            self.spin_batch_val.setEnabled(True)

    def log(self, text, color="#cdd6f4"):
        timestamp = time.strftime("[%H:%M:%S] ")
        html = f"<span style='color:#585b70;'>{timestamp}</span><span style='color:{color};'>{text}</span>"
        self._log_queue.append(html)
        if not self._log_timer.isActive():
            self._log_timer.start()

    def _flush_logs(self):
        if not self._log_queue:
            self._log_timer.stop()
            return
        batch = self._log_queue[:]
        self._log_queue.clear()
        
        cursor = self.txt_log.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertHtml("<br>".join(batch) + "<br>")
        
        scrollbar = self.txt_log.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _schedule_stats_update(self):
        """Debounce heavy progress stats calculation to avoid freezing the UI event loop."""
        if not self._stats_timer.isActive():
            self._stats_timer.start()

    def _flush_stats_update(self):
        """Immediately compute final stats on thread completion or stop."""
        if self._stats_timer.isActive():
            self._stats_timer.stop()
        if self.parent_window and hasattr(self.parent_window, 'update_progress_stats'):
            self.parent_window.update_progress_stats()

    # ── Queue Handling ──
    def browse_input_files(self):
        from tstudio_core import TStudioCore
        target_dir = ""
        if self.parent_window and hasattr(self.parent_window, 'get_active_translation_workspace'):
            target_dir = self.parent_window.get_active_translation_workspace()
        else:
            target_dir = TStudioCore.get_translation_workspace_dir()
        paths, _ = QFileDialog.getOpenFileNames(
            self, "เลือกไฟล์สำหรับแปล", target_dir,
            "Supported Files (*.csv *.bundle *.txt *.pak *.*);;CSV Files (*.csv);;All Files (*.*)"
        )
        if paths:
            for p in paths:
                self.add_queue_file(p)

    def browse_input_folder(self):
        from tstudio_core import TStudioCore
        target_dir = ""
        if self.parent_window and hasattr(self.parent_window, 'get_active_translation_workspace'):
            target_dir = self.parent_window.get_active_translation_workspace()
        else:
            target_dir = TStudioCore.get_translation_workspace_dir()
        folder = QFileDialog.getExistingDirectory(self, "เลือกโฟลเดอร์ที่มีไฟล์ CSV", target_dir)
        if folder:
            csv_files = glob.glob(os.path.join(folder, "*.csv"))
            if not csv_files:
                self.log(f"ไม่พบไฟล์ CSV ใน {folder}", "#f38ba8")
                return
            for f in csv_files:
                self.add_queue_file(f)
            self.log(f"เพิ่ม {len(csv_files)} ไฟล์จากโฟลเดอร์ {folder}", "#a6e3a1")

    def add_queue_file(self, filepath):
        for r in range(self.tbl_input.rowCount()):
            item = self.tbl_input.item(r, 0)
            if item and item.text() == filepath:
                return
        row = self.tbl_input.rowCount()
        self.tbl_input.insertRow(row)
        self.tbl_input.setItem(row, 0, QTableWidgetItem(filepath))
        
        # Profile combo
        cbo = QComboBox()
        profiles_data = TStudioCore.load_profiles()
        cbo.addItems(list(profiles_data.get("presets", {}).keys()))
        cbo.setCurrentText(profiles_data.get("active_preset", "Default"))
        self.tbl_input.setCellWidget(row, 1, cbo)

    def remove_selected_queue(self):
        selected = self.tbl_input.selectionModel().selectedRows()
        for idx in sorted([s.row() for s in selected], reverse=True):
            self.tbl_input.removeRow(idx)

    def clear_queue(self):
        self.tbl_input.setRowCount(0)

    # ── Execution ──
    def start_translation(self):
        if self.is_running:
            return

        if self.radio_selected_rows.isChecked():
            self._start_selected_rows_translation()
        elif self.radio_active_file.isChecked():
            self._start_active_file_translation()
        else:
            self._start_queue_translation()

    def _start_selected_rows_translation(self):
        if not self.parent_window or not hasattr(self.parent_window, 'csv_path'):
            QMessageBox.warning(self, "ข้อผิดพลาด", "ไม่พบหน้าต่าง TStudio หรือไฟล์ที่กำลังเปิดอยู่")
            return

        csv_path = self.parent_window.csv_path
        if not csv_path or not os.path.exists(csv_path):
            QMessageBox.warning(self, "ข้อผิดพลาด", "กรุณาเปิดไฟล์โปรเจกต์ CSV ใน TStudio ก่อนเริ่มรันแปล")
            return

        selected_indices = self.get_selected_source_row_indices()
        if not selected_indices:
            QMessageBox.warning(self, "ยังไม่ได้เลือกข้อความ", "กรุณาลากคลุมเลือกแถวที่ต้องการแปลในตาราง TStudio ก่อนเริ่มรันแปล")
            return

        # Make sure memory is saved to CSV before worker reads it
        if not self.parent_window.save_csv():
            return

        active_preset = self.parent_window.cbo_profile.currentText()
        profiles_data = TStudioCore.load_profiles()
        profile = profiles_data.get("presets", {}).get(active_preset, {})
        cfg = TStudioCore.load_config()

        self.log(f"🚀 เริ่มรันแปลเฉพาะ {len(selected_indices):,} แถวที่เลือก (Active File: {os.path.basename(csv_path)}, Batch Size: {self.slider_batch.value()} แถว/ชุด)", "#cba6f7")
        
        self.is_running = True
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.current_job_start_time = time.time()

        # Build fast ID lookup cache for smooth O(1) live table updates
        if self.parent_window and hasattr(self.parent_window, 'model') and self.parent_window.model:
            self._active_id_to_idx = {r["id"]: idx for idx, r in enumerate(self.parent_window.model._data)}
        else:
            self._active_id_to_idx = {}

        self._launch_worker(csv_path, csv_path, profile, cfg, is_active_mode=True, selected_row_indices=selected_indices)

    def _start_active_file_translation(self):
        if not self.parent_window or not hasattr(self.parent_window, 'csv_path'):
            QMessageBox.warning(self, "ข้อผิดพลาด", "ไม่พบหน้าต่าง TStudio หรือไฟล์ที่กำลังเปิดอยู่")
            return

        csv_path = self.parent_window.csv_path
        if not csv_path or not os.path.exists(csv_path):
            QMessageBox.warning(self, "ข้อผิดพลาด", "กรุณาเปิดไฟล์โปรเจกต์ CSV ใน TStudio ก่อนเริ่มรันแปล")
            return

        # Make sure memory is saved to CSV before worker reads it
        if not self.parent_window.save_csv():
            return
        
        active_preset = self.parent_window.cbo_profile.currentText()
        profiles_data = TStudioCore.load_profiles()
        profile = profiles_data.get("presets", {}).get(active_preset, {})
        cfg = TStudioCore.load_config()

        self.log(f"🚀 เริ่มรันแปล Active File: {os.path.basename(csv_path)} (Profile: {active_preset})", "#89b4fa")
        
        self.is_running = True
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.current_job_start_time = time.time()

        # Build fast ID lookup cache for smooth O(1) live table updates
        if self.parent_window and hasattr(self.parent_window, 'model') and self.parent_window.model:
            self._active_id_to_idx = {r["id"]: idx for idx, r in enumerate(self.parent_window.model._data)}
        else:
            self._active_id_to_idx = {}

        self._launch_worker(csv_path, csv_path, profile, cfg, is_active_mode=True)

    def _start_queue_translation(self):
        if self.tbl_input.rowCount() == 0:
            QMessageBox.warning(self, "คิวว่างเปล่า", "กรุณาเพิ่มไฟล์หรือโฟลเดอร์ลงในคิวก่อนเริ่มรันแปล")
            return

        self.queue = []
        for i in range(self.tbl_input.rowCount()):
            item = self.tbl_input.item(i, 0)
            if not item: continue
            in_file = item.text()
            out_file = in_file.replace(".csv", "_translated.csv")
            combo = self.tbl_input.cellWidget(i, 1)
            prof_name = combo.currentText() if combo else "Default"
            self.queue.append((in_file, out_file, prof_name))

        self.tbl_queue_status.setRowCount(0)
        for i, (in_f, _, _) in enumerate(self.queue):
            self.tbl_queue_status.insertRow(i)
            self.tbl_queue_status.setItem(i, 0, QTableWidgetItem(os.path.basename(in_f)))
            status_item = QTableWidgetItem("Pending ⏳")
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tbl_queue_status.setItem(i, 1, status_item)

        self.is_running = True
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.log(f"🚀 เริ่มรันแปลคิว {len(self.queue)} ไฟล์...", "#89b4fa")
        self._run_next_queue_item()

    def _run_next_queue_item(self):
        if not self.queue:
            self.log("✅ การรันแปลทุกไฟล์ในคิวเสร็จสมบูรณ์เรียบร้อย!", "#a6e3a1")
            self.is_running = False
            self.btn_start.setEnabled(True)
            self.btn_stop.setEnabled(False)
            return

        if not self.is_running:
            return

        in_file, out_file, prof_name = self.queue.pop(0)
        base_name = os.path.basename(in_file)
        self.log(f"กำลังประมวลผล: {base_name} (Profile: {prof_name})...", "#cba6f7")
        self._set_queue_status(base_name, "Translating 🔄")

        profiles_data = TStudioCore.load_profiles()
        profile = profiles_data.get("presets", {}).get(prof_name, {})
        cfg = TStudioCore.load_config()

        self.current_job_start_time = time.time()
        self._launch_worker(in_file, out_file, profile, cfg, is_active_mode=False)

    def _launch_worker(self, in_file, out_file, profile, cfg, is_active_mode, selected_row_indices=None):
        peak_config = None
        if self.chk_peak.isChecked():
            peak_config = {
                'start_time': self.time_peak_start.time(),
                'end_time': self.time_peak_end.time(),
                'action': self.cbo_peak_action.currentIndex(),
                'fallback_profile': "Default"
            }

        self._active_targets = {}
        if is_active_mode and self.parent_window:
            for index in range(len(self.parent_window.model._data)):
                if selected_row_indices is None or index in selected_row_indices:
                    self._active_targets[index] = RowTarget.capture(self.parent_window, index)
        self.worker = TRunWorker(
            route_config=self.parent_window.translation_channel.route() if self.parent_window else None,
            config=cfg,
            profile=profile,
            input_csv=in_file,
            output_csv=out_file,
            batch_size=self.slider_batch.value(),
            delay_ms=self.spin_delay.value(),
            max_retries=self.spin_retry.value(),
            use_mask=self.chk_mask.isChecked(),
            use_glossary=self.chk_glossary.isChecked(),
            use_pua=self.chk_pua.isChecked(),
            peak_config=peak_config,
            threads=self.spin_threads.value(),
            token_burner=self.chk_token_burner.isChecked(),
            use_cjk_filter=self.chk_cjk_filter.isChecked(),
            use_eng_filter=self.chk_eng_filter.isChecked(),
            auto_filter_engine=self.chk_engine_filter.isChecked(),
            use_dedup=self.chk_dedup.isChecked(),
            selected_row_indices=selected_row_indices
        )

        self.worker.signals.setParent(self)
        self.worker.signals.log.connect(self.log)
        self.worker.signals.progress.connect(self.update_progress)
        self.worker.signals.batch_progress.connect(self.update_batch_progress)
        self.worker.signals.row_translated.connect(lambda r_idx, g_id, text: self.on_row_translated(r_idx, g_id, text, is_active_mode))
        self.worker.signals.finished.connect(lambda: self.on_worker_finished(in_file, is_active_mode))
        self.worker.signals.stopped.connect(self.on_worker_stopped)
        self.worker.signals.error.connect(self.on_worker_error)

        self.threadpool.start(self.worker)

    def on_row_translated(self, row_idx, game_id, text, is_active_mode):
        """Called live when a row is translated. Updates the active TStudio table directly!"""
        if is_active_mode and self.parent_window and hasattr(self.parent_window, 'model'):
            self.parent_window.on_trans_changed()
            target = getattr(self, "_active_targets", {}).get(row_idx)
            if target is None or not target.matches(self.parent_window):
                if target is not None:
                    self.parent_window._retain_translation_conflict(target, text)
                return
            model = self.parent_window.model
            target_idx = -1
            if 0 <= row_idx < len(model._data) and model._data[row_idx]["id"] == game_id:
                target_idx = row_idx
            elif hasattr(self, '_active_id_to_idx') and game_id in self._active_id_to_idx:
                target_idx = self._active_id_to_idx[game_id]
            else:
                for idx, row in enumerate(model._data):
                    if row["id"] == game_id:
                        target_idx = idx
                        break
            
            if target_idx >= 0:
                model.update_trans(target_idx, text)

            # Debounced progress stats update to avoid freezing GUI event loop
            self._schedule_stats_update()

    def update_batch_progress(self, current, total):
        if total > 0:
            pct = int((current / total) * 100)
            self.batch_bar.setValue(pct)
            self.lbl_batch_progress.setText(f"Batch Progress: {current} / {total} ({pct}%)")

    def update_progress(self, current, total):
        if total > 0:
            pct = int((current / total) * 100)
            self.lines_bar.setValue(pct)
            self.lbl_line_progress.setText(f"Lines Progress: {current:,} / {total:,} ({pct}%)")

            # Calculate ETA (throttled to at most every 200ms)
            now = time.time()
            if not hasattr(self, '_last_eta_time') or (now - self._last_eta_time >= 0.2):
                self._last_eta_time = now
                if self.current_job_start_time > 0 and current > 0:
                    elapsed = now - self.current_job_start_time
                    rate = current / elapsed
                    if rate > 0:
                        rem_sec = (total - current) / rate
                        m, s = divmod(int(rem_sec), 60)
                        h, m = divmod(m, 60)
                        self.lbl_eta.setText(f"ETA: {h:02d}:{m:02d}:{s:02d}")
                    else:
                        self.lbl_eta.setText("ETA: Calculating...")

    def on_worker_finished(self, in_file, is_active_mode):
        self._flush_logs()
        self._flush_stats_update()
        base_name = os.path.basename(in_file)
        summary = getattr(getattr(self, 'worker', None), 'result_summary', None)
        complete = bool(summary and summary.get('save_ok') and summary.get('failed', 0) == 0)
        status = "Completed ✅" if complete else "Needs review ⚠️"
        self.log(f"{status}: {base_name}", "#a6e3a1" if complete else "#fab387")
        self._set_queue_status(base_name, status)

        if is_active_mode:
            self.is_running = False
            self.btn_start.setEnabled(True)
            self.btn_stop.setEnabled(False)
            # The worker already saved atomically; do not overwrite it here.
            self.sync_active_file_info()
            if complete:
                QMessageBox.information(self, "เสร็จสิ้น", f"บันทึกคำแปลครบแล้ว: {base_name}")
            else:
                QMessageBox.warning(self, "ต้องตรวจคำแปล", f"งาน {base_name} ยังมีแถวที่ไม่ผ่านหรือสถานะบันทึกไม่สมบูรณ์ กรุณาตรวจรายงานก่อนแพ็ก")
        elif self.is_running:
            self._run_next_queue_item()

    def on_worker_stopped(self):
        self._flush_logs()
        self._flush_stats_update()
        self.is_running = False
        self.queue = []
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.log("⏹️ การรันแปลถูกหยุดโดยผู้ใช้ ข้อมูลที่แปลแล้วถูกบันทึกเรียบร้อย", "#f9e2af")
        if self.radio_active_file.isChecked():
            self.sync_active_file_info()

    def on_worker_error(self, err_msg):
        self._flush_logs()
        self._flush_stats_update()
        self.log(f"❌ เกิดข้อผิดพลาดใน Worker: {err_msg}", "#f38ba8")
        input_file = getattr(getattr(self, 'worker', None), 'input_csv', '')
        if input_file:
            self._set_queue_status(os.path.basename(input_file), "Failed ❌")
        self.is_running = False
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)

    def stop_translation(self):
        if hasattr(self, 'worker') and self.worker:
            self.log("กำลังส่งสัญญาณหยุดไปยัง AI Worker...", "#fab387")
            self.worker.stop()

    def _set_queue_status(self, filename, status):
        for row in range(self.tbl_queue_status.rowCount()):
            item = self.tbl_queue_status.item(row, 0)
            if item and item.text() == filename:
                s_item = self.tbl_queue_status.item(row, 1)
                if s_item:
                    s_item.setText(status)
                    if "✅" in status: s_item.setForeground(QBrush(QColor("#a6e3a1")))
                    elif "❌" in status: s_item.setForeground(QBrush(QColor("#f38ba8")))
                    elif "🔄" in status: s_item.setForeground(QBrush(QColor("#f9e2af")))
                break

    def deploy_all(self):
        deploy_list = []
        for i in range(self.tbl_input.rowCount()):
            item = self.tbl_input.item(i, 0)
            if item:
                in_f = item.text()
                out_f = in_f.replace(".csv", "_translated.csv")
                deploy_list.append((in_f, out_f))

        # Also include active file if in active file mode
        if self.radio_active_file.isChecked() and self.parent_window and hasattr(self.parent_window, 'csv_path'):
            deploy_list.append((self.parent_window.csv_path, self.parent_window.csv_path))

        if not deploy_list:
            QMessageBox.warning(self, "ไม่มีไฟล์", "ไม่พบไฟล์ที่ต้องการ Deploy")
            return

        self.log(f"📦 เริ่มทำการ Deploy สำหรับ {len(deploy_list)} รายการ...", "#fab387")
        success_count = 0
        fail_count = 0

        for in_file, out_file in deploy_list:
            if not os.path.exists(out_file):
                continue
            try:
                stem = os.path.splitext(os.path.basename(out_file))[0]
                base_dir = os.path.dirname(in_file)
                real_stem = stem.replace("_translated", "")
                json_path = os.path.join(base_dir, f'{real_stem}_meta.json')
                pak_path = os.path.join(base_dir, f'{real_stem}.pak')

                if os.path.exists(pak_path):
                    TPakManager.reconstruct_pak_file(pak_path, out_file, pak_path)
                    success_count += 1
                    self.log(f"Deploy PAK สำเร็จ: {pak_path}", "#a6e3a1")
                    continue

                if os.path.exists(json_path):
                    from tbundle_manager import TBundleManager
                    success, msg = TBundleManager.deploy_csv_to_bundle(out_file, original_meta_path=json_path)
                    if success:
                        success_count += 1
                        self.log(f"Deploy Bundle สำเร็จ: {os.path.basename(out_file)}", "#a6e3a1")
                    else:
                        fail_count += 1
                        self.log(f"Deploy Bundle ล้มเหลว: {msg}", "#f38ba8")
                    continue

                success, msg = TFormatManager.export_original(out_file, original_meta_path=json_path if os.path.exists(json_path) else None)
                if success:
                    success_count += 1
                    self.log(f"Export Format สำเร็จ: {os.path.basename(out_file)}", "#a6e3a1")
                else:
                    fail_count += 1
                    self.log(f"Export Format ล้มเหลว: {msg}", "#f38ba8")
            except Exception as e:
                fail_count += 1
                self.log(f"Error deploying {os.path.basename(out_file)}: {e}", "#f38ba8")

        self.log(f"Deploy เสร็จสิ้น: สำเร็จ {success_count} รายการ, ล้มเหลว {fail_count} รายการ", "#a6e3a1")
        QMessageBox.information(self, "Deploy เสร็จสิ้น", f"Deploy เสร็จสิ้น!\nสำเร็จ: {success_count}\nล้มเหลว: {fail_count}")
