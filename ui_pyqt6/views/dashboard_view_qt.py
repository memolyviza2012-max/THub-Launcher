import os
import json
import time
from collections import OrderedDict
from core.startup_images import StartupImageService
from core.qt_tasks import BackgroundTasks
from core.safe_io import update_json_atomic
from core.workspace_schema import WorkspaceSchema
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QGridLayout,
    QPushButton, QLabel, QFrame, QPlainTextEdit, QMenu, QSizePolicy
)
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath, QColor, QImage
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QRectF, QPoint
from i18n_helper import _
from core.config_manager import ConfigManager
from core.tool_launcher import ToolLauncher
from core.engine_scanner import EngineScanner
from core.project_storage_service import ProjectStorageService, StorageScanWorker
from ui_pyqt6.components.project_card_qt import ProjectCardQt
from ui_pyqt6.dialogs.bible_viewer_dialog_qt import BibleViewerDialogQt


class CardsDropContainer(QWidget):
    """Container widget supporting drag-and-drop card reordering."""
    def __init__(self, dashboard_view, parent=None):
        super().__init__(parent)
        self.dashboard_view = dashboard_view
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-thub-card-name"):
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("application/x-thub-card-name"):
            event.acceptProposedAction()
            target_idx = self.dashboard_view.get_target_card_index(event.position().toPoint())
            self.dashboard_view.highlight_drop_target(target_idx)

    def dragLeaveEvent(self, event):
        self.dashboard_view.clear_drop_highlights()
        event.accept()

    def dropEvent(self, event):
        if event.mimeData().hasFormat("application/x-thub-card-name"):
            card_name = bytes(event.mimeData().data("application/x-thub-card-name")).decode("utf-8")
            target_idx = self.dashboard_view.get_target_card_index(event.position().toPoint())
            event.acceptProposedAction()
            # Defer reordering slightly so QDrag.exec() unwinds completely before layout is rebuilt
            QTimer.singleShot(20, lambda: self.dashboard_view.handle_card_dropped(card_name, target_idx))


class DashboardViewQt(QWidget):
    """
    Main Unified Dashboard in PyQt6 — Idea 4.2 (Dual-Deck Hero Stage + Clean Cinema Cards Grid).
    Features:
    - Top Dual-Deck Hero Stage (Cover & Media controls + Command Launchpad & 1-Click Folder Grid + Live Workspace Inspector & Notes)
    - Collapsible Stage Mode (switches between Full Dual-Deck Stage and Compact 1-Row Action Bar)
    - Bottom Clean 16:9 Cinema Cards Grid with hover quick-launch dock, progress bar, and drag & drop reordering.
    """

    tstudio_requested = pyqtSignal(dict)
    ai_requested = pyqtSignal(dict)
    project_selected = pyqtSignal(dict)
    counts_changed = pyqtSignal(int, int)
    archive_toggled = pyqtSignal(dict)
    archive_requested = pyqtSignal(dict, str)
    pin_toggled = pyqtSignal(dict)
    status_toggled = pyqtSignal(dict)
    status_changed = pyqtSignal(dict, str)
    delete_requested = pyqtSignal(dict)
    order_changed = pyqtSignal(list)
    cover_edit_requested = pyqtSignal(dict)
    engine_edit_requested = pyqtSignal(dict)
    settings_requested = pyqtSignal(dict)
    adopt_requested = pyqtSignal(dict)
    move_requested = pyqtSignal(dict)
    move_queue_requested = pyqtSignal()
    storage_data_updated = pyqtSignal(list)
    storage_scanning_changed = pyqtSignal(bool)
    storage_progress_changed = pyqtSignal(int, int)

    FILTER_DEFS = [
        ("all", "ทั้งหมด"),
        ("translating", "กำลังแปล"),
        ("on_hold", "ดองไว้ 🧊"),
        ("completed", "เสร็จแล้ว ✅"),
        ("pinned", "ปักหมุด ⭐"),
        ("archived", "คลังจัดเก็บ 📦")
    ]

    def __init__(self, projects=None, parent=None):
        super().__init__(parent)
        self.cfg = ConfigManager()
        self.card_size = self.cfg.get("dashboard_card_size", "normal")
        if self.card_size not in ProjectCardQt.SIZE_CONFIGS:
            self.card_size = "normal"

        self.stage_collapsed = bool(self.cfg.get("dashboard_stage_collapsed", False))
        self.storage_collapsed = not bool(self.cfg.get("dashboard_show_storage_cockpit", True))
        self.storage_worker = None
        self.tasks = BackgroundTasks(self)
        self.image_service = StartupImageService(tasks=self.tasks, parent=self)
        self._hero_image_requests = set()
        self._dirty_notes = {}
        self._saving_notes = {}
        self._hero_pixmap_cache = OrderedDict()
        self._inspection_cache = {}
        self._closing = False

        self.all_projects = projects or []
        self.filtered_projects = list(self.all_projects)
        self.selected_project = self.all_projects[0] if self.all_projects else None
        self.card_widgets = []
        self._card_pool = {}
        self.active_filter_id = "all"
        self.filter_buttons = {}
        self.size_buttons = {}
        self.current_cols = 3
        self._last_query = ""
        self._updating_note_programmatically = False

        self._note_save_timer = QTimer(self)
        self._note_save_timer.setSingleShot(True)
        self._note_save_timer.setInterval(500)
        self._note_save_timer.timeout.connect(self._save_quick_note)

        self._storage_panel_update_timer = QTimer(self)
        self._storage_panel_update_timer.setSingleShot(True)
        self._storage_panel_update_timer.setInterval(400)
        self._storage_panel_update_timer.timeout.connect(self._apply_cached_storage_sizes)

        self._build_ui()
        self._apply_cached_storage_sizes()
        # Smooth startup: Defer background storage scan by 800ms so window finishes mapping without flicker
        QTimer.singleShot(800, lambda: self._start_storage_scan_worker(force_refresh=False))

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 6, 14, 10)
        main_layout.setSpacing(8)

        # ═══════════════════════════════════════════════════════════════════════
        # 1. TOP HERO STAGE (Idea 4.2: Dual-Deck Hero Stage + 4.3 Compact Bar)
        # ═══════════════════════════════════════════════════════════════════════
        self._build_hero_stage_ui(main_layout)
        self._build_compact_stage_ui(main_layout)

        # ═══════════════════════════════════════════════════════════════════════
        # 2. CONTROLS BAR: Filter Chips + Stage Collapse Toggle + Card Size Switcher
        # ═══════════════════════════════════════════════════════════════════════
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 0)
        top_bar.setSpacing(8)

        # Filter Chips Row
        filter_row = QHBoxLayout()
        filter_row.setSpacing(5)

        for fid, label_key in self.FILTER_DEFS:
            btn = QPushButton(_(label_key))
            btn.setProperty("class", "FilterChip")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            is_active = (fid == self.active_filter_id)
            btn.setProperty("active", "true" if is_active else "false")
            btn.clicked.connect(lambda _, f=fid: self._set_filter(f))
            filter_row.addWidget(btn)
            self.filter_buttons[fid] = btn

        top_bar.addLayout(filter_row)
        top_bar.addStretch()

        # Stage Collapse / Expand Toggle Button
        self.btn_toggle_stage = QPushButton()
        self.btn_toggle_stage.setProperty("class", "SizeToggleBtn")
        self.btn_toggle_stage.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle_stage.setToolTip(_("สลับการแสดงผลเวทีด้านบน (ย่อเป็นแถบเล็ก / ขยายเต็มเวที)"))
        self.btn_toggle_stage.clicked.connect(self.toggle_stage_collapsed)
        top_bar.addWidget(self.btn_toggle_stage)

        # Separator
        sep = QLabel("|")
        sep.setStyleSheet("color: #334155; font-size: 12px; margin: 0px 2px;")
        top_bar.addWidget(sep)

        # Card Size Switcher (Compact / Normal / Large / Table)
        size_box = QHBoxLayout()
        size_box.setSpacing(4)

        lbl_size = QLabel(_("ขนาดการ์ด:"))
        lbl_size.setStyleSheet("color: #64748b; font-size: 11px; font-weight: 500; margin-right: 2px;")
        size_box.addWidget(lbl_size)

        size_options = [
            ("compact", "📱 " + _("เล็ก")),
            ("normal", "💻 " + _("กลาง")),
            ("large", "🖥️ " + _("ใหญ่")),
            ("table", "📋 " + _("แถบตาราง"))
        ]
        for sid, slabel in size_options:
            sbtn = QPushButton(slabel)
            sbtn.setProperty("class", "SizeToggleBtn")
            sbtn.setCursor(Qt.CursorShape.PointingHandCursor)
            sbtn.setToolTip(_("ปรับขนาดการ์ดแสดงผล: ") + slabel)
            is_active = (sid == self.card_size)
            sbtn.setProperty("active", "true" if is_active else "false")
            sbtn.clicked.connect(lambda _, s=sid: self.set_card_size(s))
            size_box.addWidget(sbtn)
            self.size_buttons[sid] = sbtn

        top_bar.addLayout(size_box)
        main_layout.addLayout(top_bar)

        # ═══════════════════════════════════════════════════════════════════════
        # 3. TABLE HEADER BAR (shown only when card_size == "table")
        # ═══════════════════════════════════════════════════════════════════════
        self.table_header = QFrame(self)
        self.table_header.setObjectName("TableHeader")
        self.table_header.setStyleSheet("""
            QFrame#TableHeader {
                background-color: rgba(30, 41, 59, 0.45);
                border: 1px solid rgba(51, 65, 85, 0.4);
                border-radius: 8px;
                padding: 2px 0px;
            }
            QLabel.TableHeaderLabel {
                color: #94a3b8;
                font-size: 11px;
                font-weight: bold;
            }
        """)
        th_layout = QHBoxLayout(self.table_header)
        th_layout.setContentsMargins(16, 6, 18, 6)
        th_layout.setSpacing(10)

        lbl_th_cover = QLabel(_("หน้าปก"))
        lbl_th_cover.setProperty("class", "TableHeaderLabel")
        lbl_th_cover.setFixedWidth(72)
        lbl_th_cover.setAlignment(Qt.AlignmentFlag.AlignCenter)
        th_layout.addWidget(lbl_th_cover)

        lbl_th_title = QLabel(_("ชื่อโปรเจกต์"))
        lbl_th_title.setProperty("class", "TableHeaderLabel")
        th_layout.addWidget(lbl_th_title, stretch=1)

        lbl_th_engine = QLabel(_("เอนจินเกม"))
        lbl_th_engine.setProperty("class", "TableHeaderLabel")
        lbl_th_engine.setFixedWidth(100)
        lbl_th_engine.setAlignment(Qt.AlignmentFlag.AlignCenter)
        th_layout.addWidget(lbl_th_engine)

        lbl_th_size = QLabel(_("ขนาดพื้นที่"))
        lbl_th_size.setProperty("class", "TableHeaderLabel")
        lbl_th_size.setFixedWidth(85)
        lbl_th_size.setAlignment(Qt.AlignmentFlag.AlignCenter)
        th_layout.addWidget(lbl_th_size)

        lbl_th_status = QLabel(_("สถานะ"))
        lbl_th_status.setProperty("class", "TableHeaderLabel")
        lbl_th_status.setFixedWidth(110)
        lbl_th_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        th_layout.addWidget(lbl_th_status)

        lbl_th_actions = QLabel(_("คำสั่ง / เครื่องมือ"))
        lbl_th_actions.setProperty("class", "TableHeaderLabel")
        lbl_th_actions.setFixedWidth(160)
        lbl_th_actions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        th_layout.addWidget(lbl_th_actions)

        self.table_header.setVisible(self.card_size == "table")
        main_layout.addWidget(self.table_header)

        # ═══════════════════════════════════════════════════════════════════════
        # 4. SCROLLABLE CLEAN CINEMA CARDS GRID
        # ═══════════════════════════════════════════════════════════════════════
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.verticalScrollBar().setSingleStep(40)
        self.scroll_area.viewport().setAutoFillBackground(False)
        self.scroll_area.viewport().setStyleSheet("background: transparent;")

        self.cards_container = CardsDropContainer(self)
        self.cards_container.setAutoFillBackground(False)
        self.cards_container.setStyleSheet("background: transparent;")
        self.grid_layout = QGridLayout(self.cards_container)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        size_cfg = ProjectCardQt.SIZE_CONFIGS.get(self.card_size, ProjectCardQt.SIZE_CONFIGS["normal"])
        self.grid_layout.setSpacing(size_cfg["spacing"])
        if self.card_size == "table":
            self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        else:
            self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        self.scroll_area.setWidget(self.cards_container)
        main_layout.addWidget(self.scroll_area, stretch=1)

        self._apply_stage_visibility()
        self.apply_search_and_filter()

    # ═══════════════════════════════════════════════════════════════════════════
    # HERO STAGE UI BUILDERS (Idea 4.2 Dual-Deck + 4.3 Compact Mode)
    # ═══════════════════════════════════════════════════════════════════════════
    def _build_hero_stage_ui(self, parent_layout):
        """Builds the 3-Zone Dual-Deck Hero Stage at the top of the Dashboard."""
        self.hero_stage_frame = QFrame(self)
        self.hero_stage_frame.setObjectName("HeroStageFrame")
        self.hero_stage_frame.setFixedHeight(210)

        stage_layout = QHBoxLayout(self.hero_stage_frame)
        stage_layout.setContentsMargins(14, 12, 14, 12)
        stage_layout.setSpacing(16)

        # ── LEFT ZONE: 16:9 Cover Preview + Media Quick Actions (272px) ───────
        left_zone = QVBoxLayout()
        left_zone.setContentsMargins(0, 0, 0, 0)
        left_zone.setSpacing(6)

        self.HERO_COVER_W = 272
        self.HERO_COVER_H = 152
        self.lbl_hero_cover = QLabel(self.hero_stage_frame)
        self.lbl_hero_cover.setFixedSize(self.HERO_COVER_W, self.HERO_COVER_H)
        self.lbl_hero_cover.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lbl_hero_cover.setToolTip(_("คลิกเพื่อเปลี่ยนหรือปรับแต่งภาพหน้าปก"))
        self.lbl_hero_cover.mousePressEvent = lambda e: (
            self.cover_edit_requested.emit(self.selected_project)
            if e.button() == Qt.MouseButton.LeftButton and self.selected_project else None
        )
        left_zone.addWidget(self.lbl_hero_cover)

        media_row = QHBoxLayout()
        media_row.setContentsMargins(0, 0, 0, 0)
        media_row.setSpacing(4)

        btn_style_media = """
            QPushButton {
                background-color: rgba(30, 41, 59, 0.75);
                color: #cbd5e1;
                border: 1px solid #334155;
                border-radius: 5px;
                font-size: 10px;
                font-weight: 600;
                padding: 3px 6px;
            }
            QPushButton:hover {
                background-color: #1e293b;
                color: #38bdf8;
                border-color: #38bdf8;
            }
        """

        self.btn_hero_cover = QPushButton(_("🖼️ เปลี่ยนปก"))
        self.btn_hero_cover.setStyleSheet(btn_style_media)
        self.btn_hero_cover.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_hero_cover.clicked.connect(lambda: self.selected_project and self.cover_edit_requested.emit(self.selected_project))
        media_row.addWidget(self.btn_hero_cover)

        self.btn_hero_engine = QPushButton(_("⚙️ Engine"))
        self.btn_hero_engine.setStyleSheet(btn_style_media)
        self.btn_hero_engine.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_hero_engine.clicked.connect(lambda: self.selected_project and self.engine_edit_requested.emit(self.selected_project))
        media_row.addWidget(self.btn_hero_engine)

        self.btn_hero_settings = QPushButton(_("✏️ ตั้งค่า"))
        self.btn_hero_settings.setStyleSheet(btn_style_media)
        self.btn_hero_settings.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_hero_settings.clicked.connect(lambda: self.selected_project and self.settings_requested.emit(self.selected_project))
        media_row.addWidget(self.btn_hero_settings)

        left_zone.addLayout(media_row)
        stage_layout.addLayout(left_zone)

        # ── CENTER ZONE: Command Launchpad + 2x3 Subfolder Jump Grid ──────────
        center_zone = QVBoxLayout()
        center_zone.setContentsMargins(0, 0, 0, 0)
        center_zone.setSpacing(8)

        # Row 1: Title + Engine Badge + Status Pill + Pin Button
        header_row = QHBoxLayout()
        header_row.setContentsMargins(0, 0, 0, 0)
        header_row.setSpacing(8)

        self.btn_hero_pin = QPushButton("📌")
        self.btn_hero_pin.setFixedSize(26, 26)
        self.btn_hero_pin.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_hero_pin.setToolTip(_("ปักหมุด / ยกเลิกปักหมุดโปรเจกต์นี้"))
        self.btn_hero_pin.clicked.connect(lambda: self.selected_project and self.pin_toggled.emit(self.selected_project))
        header_row.addWidget(self.btn_hero_pin)

        self.lbl_hero_title = QLabel(_("ยังไม่ได้เลือกโปรเจกต์"))
        self.lbl_hero_title.setProperty("class", "ProjectTitle")
        self.lbl_hero_title.setStyleSheet("font-size: 19px; font-weight: 800;")
        header_row.addWidget(self.lbl_hero_title, stretch=1)

        self.lbl_hero_engine_badge = QLabel("Engine")
        self.lbl_hero_engine_badge.setFixedHeight(24)
        header_row.addWidget(self.lbl_hero_engine_badge)

        self.lbl_hero_size_badge = QLabel("")
        self.lbl_hero_size_badge.setFixedHeight(24)
        self.lbl_hero_size_badge.setStyleSheet("""
            background-color: rgba(30, 41, 59, 0.85);
            color: #38bdf8;
            border: 1px solid #0284c7;
            border-radius: 5px;
            padding: 2px 8px;
            font-size: 11px;
            font-weight: bold;
        """)
        header_row.addWidget(self.lbl_hero_size_badge)

        self.btn_hero_status = QPushButton("● กำลังแปล")
        self.btn_hero_status.setFixedHeight(24)
        self.btn_hero_status.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_hero_status.setToolTip(_("คลิกเพื่อเปลี่ยนสถานะโปรเจกต์"))
        self.btn_hero_status.clicked.connect(self._show_hero_status_menu)
        header_row.addWidget(self.btn_hero_status)

        center_zone.addLayout(header_row)

        # Row 2: Primary Command Launch Buttons
        launch_row = QHBoxLayout()
        launch_row.setContentsMargins(0, 0, 0, 0)
        launch_row.setSpacing(8)

        self.btn_hero_tstudio = QPushButton(_("🚀 เปิดแปลด้วย TStudio"))
        self.btn_hero_tstudio.setProperty("class", "BtnTStudio")
        self.btn_hero_tstudio.setFixedHeight(36)
        self.btn_hero_tstudio.setStyleSheet("font-size: 13px; font-weight: bold; padding: 4px 14px;")
        self.btn_hero_tstudio.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_hero_tstudio.clicked.connect(lambda: self.selected_project and self.tstudio_requested.emit(self.selected_project))
        launch_row.addWidget(self.btn_hero_tstudio, stretch=2)

        self.btn_hero_ai = QPushButton(_("🤖 AI Helper Copilot"))
        self.btn_hero_ai.setProperty("class", "BtnAI")
        self.btn_hero_ai.setFixedHeight(36)
        self.btn_hero_ai.setStyleSheet("font-size: 13px; font-weight: bold; padding: 4px 14px;")
        self.btn_hero_ai.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_hero_ai.clicked.connect(lambda: self.selected_project and self.ai_requested.emit(self.selected_project))
        launch_row.addWidget(self.btn_hero_ai, stretch=2)

        self.btn_hero_adopt = QPushButton(_("🔄 สานต่องาน"))
        self.btn_hero_adopt.setProperty("class", "BtnFolder")
        self.btn_hero_adopt.setFixedHeight(36)
        self.btn_hero_adopt.setToolTip(_("สานต่องานและจัดโครงสร้าง THub อัตโนมัติ"))
        self.btn_hero_adopt.setStyleSheet("font-size: 11px; font-weight: 600; padding: 4px 10px;")
        self.btn_hero_adopt.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_hero_adopt.clicked.connect(lambda: self.selected_project and self.adopt_requested.emit(self.selected_project))
        launch_row.addWidget(self.btn_hero_adopt)

        center_zone.addLayout(launch_row)

        # Row 3: 1-Click Subfolder Jump Grid (2x3)
        folder_grid = QGridLayout()
        folder_grid.setContentsMargins(0, 2, 0, 0)
        folder_grid.setSpacing(6)

        sub_btn_style = """
            QPushButton {
                background-color: rgba(15, 23, 42, 0.55);
                color: #cbd5e1;
                border: 1px solid #283548;
                border-radius: 6px;
                font-size: 11px;
                font-weight: 600;
                padding: 5px 8px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: rgba(30, 41, 59, 0.9);
                color: #38bdf8;
                border-color: #38bdf8;
            }
        """
        sub_btn_highlight_style = """
            QPushButton {
                background-color: rgba(14, 116, 144, 0.18);
                color: #38bdf8;
                border: 1px solid rgba(56, 189, 248, 0.45);
                border-radius: 6px;
                font-size: 11px;
                font-weight: bold;
                padding: 5px 8px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: rgba(14, 116, 144, 0.35);
                color: #7dd3fc;
                border-color: #38bdf8;
            }
        """

        self.btn_sub_01 = QPushButton("📂 01_Original (0)")
        self.btn_sub_01.setStyleSheet(sub_btn_style)
        self.btn_sub_01.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_sub_01.clicked.connect(lambda: self._open_subfolder("01_Original_Backup"))
        folder_grid.addWidget(self.btn_sub_01, 0, 0)

        self.btn_sub_02 = QPushButton("📂 02_Translation (0)")
        self.btn_sub_02.setStyleSheet(sub_btn_highlight_style)
        self.btn_sub_02.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_sub_02.clicked.connect(lambda: self._open_subfolder("02_Translation_Workspace"))
        folder_grid.addWidget(self.btn_sub_02, 0, 1)

        self.btn_sub_03 = QPushButton("🔤 03_Font_and_UI (0)")
        self.btn_sub_03.setStyleSheet(sub_btn_style)
        self.btn_sub_03.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_sub_03.clicked.connect(lambda: self._open_subfolder("03_Font_and_UI"))
        folder_grid.addWidget(self.btn_sub_03, 0, 2)

        self.btn_sub_04 = QPushButton("📦 04_Packed_Mod (0)")
        self.btn_sub_04.setStyleSheet(sub_btn_style)
        self.btn_sub_04.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_sub_04.clicked.connect(lambda: self._open_subfolder("04_Packed_Mod"))
        folder_grid.addWidget(self.btn_sub_04, 1, 0)

        self.btn_sub_bible = QPushButton(_("📖 คัมภีร์ Modding Bible"))
        self.btn_sub_bible.setStyleSheet(sub_btn_style)
        self.btn_sub_bible.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_sub_bible.clicked.connect(self._open_hero_bible)
        folder_grid.addWidget(self.btn_sub_bible, 1, 1)

        self.btn_sub_gamedir = QPushButton(_("🎮 โฟลเดอร์ตัวเกมจริง"))
        self.btn_sub_gamedir.setStyleSheet(sub_btn_style)
        self.btn_sub_gamedir.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_sub_gamedir.clicked.connect(self._open_hero_game_dir)
        folder_grid.addWidget(self.btn_sub_gamedir, 1, 2)

        center_zone.addLayout(folder_grid)
        center_zone.addStretch()
        stage_layout.addLayout(center_zone, stretch=1)

        # ── RIGHT ZONE: Live Workspace Inspector & Quick Note (310px) ─────────
        self.inspector_box = QFrame(self.hero_stage_frame)
        self.inspector_box.setObjectName("HeroInspectorBox")
        self.inspector_box.setFixedWidth(315)
        insp_layout = QVBoxLayout(self.inspector_box)
        insp_layout.setContentsMargins(10, 8, 10, 8)
        insp_layout.setSpacing(5)

        # Inspector Header
        insp_hdr = QHBoxLayout()
        insp_hdr.setContentsMargins(0, 0, 0, 0)
        lbl_insp_title = QLabel(_("⚡ ข้อมูลเวิร์กสเปซ & บันทึกด่วน"))
        lbl_insp_title.setStyleSheet("color: #38bdf8; font-size: 11px; font-weight: bold;")
        insp_hdr.addWidget(lbl_insp_title)
        insp_hdr.addStretch()

        self.lbl_note_saved = QLabel("")
        self.lbl_note_saved.setStyleSheet("color: #22c55e; font-size: 10px; font-weight: bold;")
        insp_hdr.addWidget(self.lbl_note_saved)

        btn_open_root = QPushButton(_("📁 โฟลเดอร์หลัก"))
        btn_open_root.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_open_root.setStyleSheet("""
            QPushButton {
                background-color: rgba(30, 41, 59, 0.8);
                color: #94a3b8;
                border: 1px solid #334155;
                border-radius: 4px;
                font-size: 10px;
                padding: 1px 6px;
            }
            QPushButton:hover {
                color: #f8fafc;
                border-color: #38bdf8;
            }
        """)
        btn_open_root.clicked.connect(lambda: self._open_subfolder(""))
        insp_hdr.addWidget(btn_open_root)
        insp_layout.addLayout(insp_hdr)

        # Live Translation Files Summary
        self.lbl_insp_files = QLabel(_("📄 ไฟล์แปล: -"))
        self.lbl_insp_files.setStyleSheet("color: #cbd5e1; font-size: 11px;")
        self.lbl_insp_files.setWordWrap(False)
        insp_layout.addWidget(self.lbl_insp_files)

        # Live Fonts Summary
        self.lbl_insp_fonts = QLabel(_("🔤 ฟอนต์: -"))
        self.lbl_insp_fonts.setStyleSheet("color: #94a3b8; font-size: 11px;")
        self.lbl_insp_fonts.setWordWrap(False)
        insp_layout.addWidget(self.lbl_insp_fonts)

        # Live Folder Storage Size
        self.lbl_insp_size = QLabel(_("💾 ขนาดโฟลเดอร์: -"))
        self.lbl_insp_size.setStyleSheet("color: #94a3b8; font-size: 11px;")
        self.lbl_insp_size.setWordWrap(False)
        insp_layout.addWidget(self.lbl_insp_size)

        # Quick Note Editor
        self.txt_hero_note = QPlainTextEdit(self.inspector_box)
        self.txt_hero_note.setPlaceholderText(_("📝 พิมพ์บันทึกช่วยจำสำหรับโปรเจกต์นี้ (บันทึกอัตโนมัติ)..."))
        self.txt_hero_note.setStyleSheet("""
            QPlainTextEdit {
                background-color: rgba(15, 23, 42, 0.55);
                color: #e2e8f0;
                border: 1px solid #283548;
                border-radius: 6px;
                font-size: 11px;
                padding: 4px;
            }
            QPlainTextEdit:focus {
                border: 1px solid #38bdf8;
            }
        """)
        self.txt_hero_note.textChanged.connect(self._on_quick_note_changed)
        insp_layout.addWidget(self.txt_hero_note, stretch=1)

        stage_layout.addWidget(self.inspector_box)
        parent_layout.addWidget(self.hero_stage_frame)

    def _build_compact_stage_ui(self, parent_layout):
        """Builds the sleek 1-Row Compact Action Bar (Idea 4.3 collapsed mode)."""
        self.compact_stage_frame = QFrame(self)
        self.compact_stage_frame.setObjectName("HeroStageFrame")
        self.compact_stage_frame.setFixedHeight(50)

        cbar_layout = QHBoxLayout(self.compact_stage_frame)
        cbar_layout.setContentsMargins(10, 6, 10, 6)
        cbar_layout.setSpacing(10)

        self.lbl_compact_cover = QLabel(self.compact_stage_frame)
        self.lbl_compact_cover.setFixedSize(64, 36)
        cbar_layout.addWidget(self.lbl_compact_cover)

        lbl_sel_tag = QLabel(_("🎬 โปรเจกต์ที่เลือก:"))
        lbl_sel_tag.setStyleSheet("color: #38bdf8; font-size: 11px; font-weight: bold;")
        cbar_layout.addWidget(lbl_sel_tag)

        self.lbl_compact_title = QLabel("-")
        self.lbl_compact_title.setProperty("class", "ProjectTitle")
        self.lbl_compact_title.setStyleSheet("font-size: 14px; font-weight: bold;")
        cbar_layout.addWidget(self.lbl_compact_title, stretch=1)

        self.lbl_compact_engine = QLabel("")
        self.lbl_compact_engine.setFixedHeight(22)
        cbar_layout.addWidget(self.lbl_compact_engine)

        self.lbl_compact_size = QLabel("")
        self.lbl_compact_size.setStyleSheet("color: #38bdf8; font-size: 11px; font-weight: bold;")
        cbar_layout.addWidget(self.lbl_compact_size)

        self.lbl_compact_status = QLabel("")
        self.lbl_compact_status.setStyleSheet("color: #cbd5e1; font-size: 11px; font-weight: 600;")
        cbar_layout.addWidget(self.lbl_compact_status)

        btn_c_tstudio = QPushButton(_("🚀 เปิด TStudio"))
        btn_c_tstudio.setProperty("class", "BtnTStudio")
        btn_c_tstudio.setFixedHeight(30)
        btn_c_tstudio.setStyleSheet("font-size: 11px; font-weight: bold; padding: 2px 10px;")
        btn_c_tstudio.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_c_tstudio.clicked.connect(lambda: self.selected_project and self.tstudio_requested.emit(self.selected_project))
        cbar_layout.addWidget(btn_c_tstudio)

        btn_c_ai = QPushButton(_("🤖 AI Helper"))
        btn_c_ai.setProperty("class", "BtnAI")
        btn_c_ai.setFixedHeight(30)
        btn_c_ai.setStyleSheet("font-size: 11px; font-weight: bold; padding: 2px 10px;")
        btn_c_ai.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_c_ai.clicked.connect(lambda: self.selected_project and self.ai_requested.emit(self.selected_project))
        cbar_layout.addWidget(btn_c_ai)

        btn_c_trans = QPushButton("📂 02_Translation")
        btn_c_trans.setProperty("class", "BtnFolder")
        btn_c_trans.setFixedHeight(30)
        btn_c_trans.setStyleSheet("font-size: 11px; padding: 2px 8px;")
        btn_c_trans.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_c_trans.clicked.connect(lambda: self._open_subfolder("02_Translation_Workspace"))
        cbar_layout.addWidget(btn_c_trans)

        btn_c_root = QPushButton("📁")
        btn_c_root.setProperty("class", "BtnFolder")
        btn_c_root.setFixedSize(30, 30)
        btn_c_root.setToolTip(_("เปิดโฟลเดอร์หลักของโปรเจกต์"))
        btn_c_root.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_c_root.clicked.connect(lambda: self._open_subfolder(""))
        cbar_layout.addWidget(btn_c_root)

        parent_layout.addWidget(self.compact_stage_frame)

    def toggle_stage_collapsed(self):
        """Toggles between Full Dual-Deck Hero Stage (4.2) and Compact Bar (4.3)."""
        self.stage_collapsed = not self.stage_collapsed
        self.cfg.set("dashboard_stage_collapsed", self.stage_collapsed)
        self._apply_stage_visibility()

    def _apply_stage_visibility(self):
        has_projects = bool(self.all_projects)
        self.hero_stage_frame.setVisible(has_projects and not self.stage_collapsed)
        self.compact_stage_frame.setVisible(has_projects and self.stage_collapsed)
        if hasattr(self, "btn_toggle_stage"):
            if self.stage_collapsed:
                self.btn_toggle_stage.setText("🔽 " + _("ขยายเวทีด้านบน"))
                self.btn_toggle_stage.setProperty("active", "false")
            else:
                self.btn_toggle_stage.setText("🔼 " + _("ย่อเวทีด้านบน"))
                self.btn_toggle_stage.setProperty("active", "true")
            self.btn_toggle_stage.style().unpolish(self.btn_toggle_stage)
            self.btn_toggle_stage.style().polish(self.btn_toggle_stage)

    # ═══════════════════════════════════════════════════════════════════════════
    # HERO STAGE DATA POPULATION & INTERACTION
    # ═══════════════════════════════════════════════════════════════════════════
    def select_project(self, project):
        """Selects a project into the Top Hero Stage and highlights its card."""
        if not project:
            return
        self._save_quick_note()
        self.selected_project = project
        self._update_hero_stage(project)
        self._update_selected_card_highlight()
        self.project_selected.emit(project)

    def _update_selected_card_highlight(self):
        sel_key = self._get_project_key(self.selected_project) if self.selected_project else None
        for k, card in self._card_pool.items():
            card.set_selected(k == sel_key)

    def _render_hero_cover_pixmap(self, project, width, height, radius=8):
        """Reuse rendered covers while file content, crop and progress stay unchanged."""
        cover_path = None
        if project:
            # Resolve cover path via card helper or cached path
            key = self._get_project_key(project)
            card = self._card_pool.get(key)
            if card:
                cover_path = card._get_cover_path()
            else:
                cover_path = project.get("_cached_cover_path")

        image = QImage()
        request_key = self.image_service.key_for(
            cover_path, width, height, project.get("cover_offset_x", 0) if project else 0,
            project.get("cover_offset_y", 0) if project else 0,
            project.get("cover_zoom", 1.0) if project else 1.0)
        if cover_path and not self._closing:
            callback = None
            if request_key not in self._hero_image_requests:
                project_key = self._get_project_key(project)
                callback = lambda result: self._hero_image_ready(project_key, request_key)
                self._hero_image_requests.add(request_key)
            image = self.image_service.request(
                cover_path, width, height, project.get("cover_offset_x", 0),
                project.get("cover_offset_y", 0), project.get("cover_zoom", 1.0), on_ready=callback)
            if image is not None:
                self._hero_image_requests.discard(request_key)
        key = (request_key, radius, image is None,
               project.get("status") if project else None,
               project.get("progress", {}).get("percentage") if project else None)
        if key in self._hero_pixmap_cache:
            self._hero_pixmap_cache.move_to_end(key)
            return self._hero_pixmap_cache[key]
        pixmap = self._paint_hero_cover_pixmap(project, width, height, radius, None, image)
        self._hero_pixmap_cache[key] = pixmap
        while len(self._hero_pixmap_cache) > 24:
            self._hero_pixmap_cache.popitem(last=False)
        return pixmap

    def _hero_image_ready(self, project_key, request_key):
        self._hero_image_requests.discard(request_key)
        self._hero_pixmap_cache.clear()
        if not self._closing and self.selected_project and self._get_project_key(self.selected_project) == project_key:
            self.lbl_hero_cover.setPixmap(self._render_hero_cover_pixmap(self.selected_project, self.HERO_COVER_W, self.HERO_COVER_H, 10))
            self.lbl_compact_cover.setPixmap(self._render_hero_cover_pixmap(self.selected_project, 64, 36, 4))

    def _paint_hero_cover_pixmap(self, project, width, height, radius, cover_path, decoded_image=None):
        target_pix = QPixmap(width, height)
        target_pix.fill(Qt.GlobalColor.transparent)

        painter = QPainter(target_pix)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(QRectF(0, 0, width, height), radius, radius)
        painter.setClipPath(path)

        offset_x = int(project.get("cover_offset_x", 0)) if project else 0
        offset_y = int(project.get("cover_offset_y", 0)) if project else 0
        zoom = float(project.get("cover_zoom", 1.0)) if project else 1.0

        if decoded_image is not None and not decoded_image.isNull():
            # The worker already applied the exact crop. Round and overlay on Qt's UI thread.
            painter.drawImage(0, 0, decoded_image)
        elif cover_path and os.path.exists(cover_path):
            img = QImage(cover_path)
            if img.isNull() or img.width() <= 0 or img.height() <= 0:
                try:
                    from PIL import Image
                    with Image.open(cover_path) as pil_img:
                        pil_img = pil_img.convert("RGBA")
                        data = pil_img.tobytes("raw", "RGBA")
                        img = QImage(data, pil_img.width, pil_img.height, QImage.Format.Format_RGBA8888)
                except Exception:
                    img = QImage()

            if not img.isNull() and img.width() > 0 and img.height() > 0:
                raw_pix = QPixmap.fromImage(img)
                base_scale = max(width / raw_pix.width(), height / raw_pix.height())
                scale = base_scale * max(1.0, zoom)
                new_w = max(width, int(raw_pix.width() * scale))
                new_h = max(height, int(raw_pix.height() * scale))
                scaled = raw_pix.scaled(
                    new_w, new_h,
                    Qt.AspectRatioMode.IgnoreAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                center_x = (new_w - width) / 2.0
                center_y = (new_h - height) / 2.0
                crop_x = max(0, min(int(center_x + (offset_x / 100.0) * center_x), new_w - width))
                crop_y = max(0, min(int(center_y + (offset_y / 100.0) * center_y), new_h - height))
                painter.drawPixmap(0, 0, scaled.copy(crop_x, crop_y, width, height))
            else:
                painter.fillRect(0, 0, width, height, QColor("#181d2a"))
        else:
            painter.fillRect(0, 0, width, height, QColor("#181d2a"))

        # Progress bar at bottom of Hero cover
        if project and height >= 80:
            status = project.get("status", "In Progress")
            pct = project.get("progress", {}).get("percentage")
            if status == "Completed" or (pct is not None and pct >= 100):
                bar_pct, bar_color = 100, "#22c55e"
            elif status in ("Cancelled", "Canceled", "ยกเลิก"):
                bar_pct, bar_color = 100, "#ef4444"
            elif status in ("On Hold", "Paused", "Shelved", "ดอง"):
                bar_pct, bar_color = max(25, pct if pct is not None else 35), "#c084fc"
            elif pct is not None:
                bar_pct, bar_color = max(8, pct), "#38bdf8"
            else:
                bar_pct, bar_color = 42, "#f59e0b"

            bar_h = 5
            bar_y = height - bar_h
            painter.fillRect(0, bar_y, width, bar_h, QColor(15, 23, 42, 200))
            fill_w = max(0, min(width, int(width * (bar_pct / 100.0))))
            painter.fillRect(0, bar_y, fill_w, bar_h, QColor(bar_color))

        painter.end()
        return target_pix

    def _update_hero_stage(self, project):
        """Updates all 3 zones of the Hero Stage and Compact Stage Bar for the selected project."""
        if not project:
            return

        # 1. Cover Pixmaps
        self.lbl_hero_cover.setPixmap(self._render_hero_cover_pixmap(project, self.HERO_COVER_W, self.HERO_COVER_H, radius=10))
        self.lbl_compact_cover.setPixmap(self._render_hero_cover_pixmap(project, 64, 36, radius=4))

        # 2. Title & Pin
        name = project.get("name", "Unknown Game")
        self.lbl_hero_title.setText(name)
        self.lbl_hero_title.setToolTip(name)
        self.lbl_compact_title.setText(name)

        is_pinned = project.get("is_pinned", False)
        if is_pinned:
            self.btn_hero_pin.setStyleSheet("""
                QPushButton {
                    background-color: rgba(245, 158, 11, 0.2);
                    color: #fbbf24;
                    border: 1px solid #f59e0b;
                    border-radius: 6px;
                    font-size: 12px;
                }
            """)
        else:
            self.btn_hero_pin.setStyleSheet("""
                QPushButton {
                    background-color: rgba(30, 41, 59, 0.5);
                    color: #64748b;
                    border: 1px solid #334155;
                    border-radius: 6px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    color: #fbbf24;
                    border-color: #f59e0b;
                }
            """)

        # 3. Engine Badge
        eng_raw = project.get("engine") or project.get("engine_badge") or "Custom Engine"
        eng_name = EngineScanner.normalize_engine_name(eng_raw)
        eng_color = EngineScanner.get_engine_color(eng_name)
        eng_qss = f"""
            background-color: rgba(16, 20, 30, 220);
            color: {eng_color};
            border: 1px solid {eng_color};
            border-radius: 5px;
            padding: 2px 8px;
            font-size: 11px;
            font-weight: bold;
        """
        self.lbl_hero_engine_badge.setText(f" {eng_name} ")
        self.lbl_hero_engine_badge.setStyleSheet(eng_qss)
        self.lbl_compact_engine.setText(f" {eng_name} ")
        self.lbl_compact_engine.setStyleSheet(eng_qss)

        # 4. Status Button
        status = project.get("status", "In Progress")
        pct = project.get("progress", {}).get("percentage")
        if status == "Completed" or (pct is not None and pct >= 100):
            s_text, s_color = _("เสร็จแล้ว (100%)"), "#22c55e"
        elif status in ("Cancelled", "Canceled", "ยกเลิก"):
            s_text, s_color = _("ยกเลิก"), "#ef4444"
        elif status in ("On Hold", "Paused", "Shelved", "ดอง"):
            s_text, s_color = _("ดองไว้ 🧊"), "#c084fc"
        elif pct is not None:
            s_text, s_color = f"กำลังแปล ({pct}%)", "#38bdf8"
        else:
            s_text, s_color = _("กำลังแปล"), "#f59e0b"

        self.btn_hero_status.setText(f"● {s_text}")
        self.btn_hero_status.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(30, 41, 59, 0.85);
                color: {s_color};
                border: 1px solid {s_color};
                border-radius: 5px;
                padding: 2px 8px;
                font-size: 11px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #1e293b;
            }}
        """)
        self.lbl_compact_status.setText(f"● {s_text}")
        self.lbl_compact_status.setStyleSheet(f"color: {s_color}; font-size: 11px; font-weight: bold;")

        # 5. Live Workspace Subfolder Counts & File Inspector
        ws_path = project.get("path", "")
        self._request_inspection(project)
        inspection = self._inspection_cache.get(self._get_project_key(project), {}).get("folders", {})
        c01, _f01 = inspection.get("01_Original_Backup", (0, []))
        c02, files02 = inspection.get("02_Translation_Workspace", (0, []))
        c03, files03 = inspection.get("03_Font_and_UI", (0, []))
        c04, _f04 = inspection.get("04_Packed_Mod", (0, []))

        self.btn_sub_01.setText(f"📂 01_Original ({c01})")
        self.btn_sub_02.setText(f"📂 02_Translation ({c02})")
        self.btn_sub_03.setText(f"🔤 03_Font_and_UI ({c03})")
        self.btn_sub_04.setText(f"📦 04_Packed_Mod ({c04})")

        if files02:
            preview_f = ", ".join(files02[:2])
            if len(preview_f) > 30:
                preview_f = preview_f[:28] + "..."
            if len(files02) > 2:
                preview_f += f" (+{len(files02) - 2})"
            self.lbl_insp_files.setText(f"📄 ไฟล์แปล: {preview_f}")
            self.lbl_insp_files.setToolTip("\n".join(files02))
        else:
            self.lbl_insp_files.setText(_("📄 ไฟล์แปล: ยังไม่มีไฟล์ใน 02_Translation"))
            self.lbl_insp_files.setToolTip("")

        font_files = [f for f in files03 if f.lower().endswith((".ttf", ".otf", ".fnt", ".ttc"))]
        if font_files:
            preview_fnt = ", ".join(font_files[:2])
            if len(preview_fnt) > 28:
                preview_fnt = preview_fnt[:26] + "..."
            if len(font_files) > 2:
                preview_fnt += f" (+{len(font_files) - 2})"
            self.lbl_insp_fonts.setText(f"🔤 ฟอนต์: {preview_fnt}")
            self.lbl_insp_fonts.setToolTip("\n".join(font_files))
        elif files03:
            self.lbl_insp_fonts.setText(f"🔤 03_Font_and_UI: {len(files03)} ไฟล์")
            self.lbl_insp_fonts.setToolTip("\n".join(files03))
        else:
            self.lbl_insp_fonts.setText(_("🔤 ฟอนต์: ยังไม่มีฟอนต์ใน 03_Font_and_UI"))
            self.lbl_insp_fonts.setToolTip("")

        # 5.5 Update Folder Storage Size Badge
        sz_bytes = project.get("_storage_bytes")
        sz_str = project.get("_storage_size_str")
        if not sz_str and ws_path:
            cache = ProjectStorageService.get_cached_sizes()
            c_entry = cache.get(ws_path)
            if c_entry:
                sz_bytes = c_entry.get("size", 0)
                sz_str = ProjectStorageService.format_size(sz_bytes)
                project["_storage_bytes"] = sz_bytes
                project["_storage_size_str"] = sz_str

        if sz_str:
            self.lbl_hero_size_badge.setText(f"💾 {sz_str}")
            self.lbl_hero_size_badge.show()
            self.lbl_compact_size.setText(f"💾 {sz_str}")
            self.lbl_compact_size.show()
            self.lbl_insp_size.setText(f"💾 ขนาดโฟลเดอร์: {sz_str}")
        else:
            self.lbl_hero_size_badge.hide()
            self.lbl_compact_size.hide()
            self.lbl_insp_size.setText(_("💾 ขนาดโฟลเดอร์: กำลังคำนวณ..."))

        # 6. Quick Note Field (load from project dict or thub_project.json)
        note_val = project.get("notes")
        # Metadata fallback is loaded by the inspector worker, never during painting.
        key = self._get_project_key(project)
        if key in self._dirty_notes:
            note_val = self._dirty_notes[key][1]
        self._updating_note_programmatically = True
        if self.txt_hero_note.toPlainText() != (note_val or ""):
            self.txt_hero_note.setPlainText(note_val or "")
        if key not in self._dirty_notes:
            self.lbl_note_saved.setText("")
        self._updating_note_programmatically = False

    def _scan_folder_files(self, ws_path, subfolder):
        if not ws_path or not os.path.exists(ws_path):
            return 0, []
        target = os.path.join(ws_path, subfolder) if subfolder else ws_path
        if not os.path.exists(target):
            return 0, []
        try:
            items = [
                f for f in os.listdir(target)
                if not f.startswith(".") and os.path.isfile(os.path.join(target, f))
            ]
            return len(items), items
        except Exception:
            return 0, []

    def _open_subfolder(self, subfolder):
        if not self.selected_project:
            return
        ws_path = self.selected_project.get("path", "")
        if not ws_path:
            return
        target = WorkspaceSchema.folder(self.selected_project, subfolder) if subfolder else ws_path
        if not os.path.exists(target):
            try:
                os.makedirs(target, exist_ok=True)
            except Exception:
                target = ws_path
        ToolLauncher.open_folder(target)

    def _open_hero_game_dir(self):
        if not self.selected_project:
            return
        game_dir = self.selected_project.get("game_dir") or self.selected_project.get("game_path")
        if game_dir and os.path.exists(game_dir):
            ToolLauncher.open_folder(game_dir)
        else:
            # Open project settings so user can set game directory
            self.settings_requested.emit(self.selected_project)

    def _open_hero_bible(self):
        if not self.selected_project:
            return
        bible_path = self.selected_project.get("bible_path")
        bible_title = self.selected_project.get("bible_title")
        engine_name = self.selected_project.get("engine", "")

        if not bible_path or not os.path.exists(bible_path):
            try:
                from core.knowledge_service import KnowledgeService
                b_match = KnowledgeService.get_instance().find_exact_bible_by_title(
                    self.selected_project.get("name", ""),
                    engine_name=engine_name
                )
                if b_match:
                    bible_path = b_match.get("bible_path")
                    bible_title = b_match.get("bible_title")
                    engine_name = b_match.get("engine_name", engine_name)
            except Exception:
                pass

        if bible_path and os.path.exists(bible_path):
            dlg = BibleViewerDialogQt(
                self,
                bible_path=bible_path,
                bible_title=bible_title or self.selected_project.get("name"),
                engine_name=engine_name
            )
            dlg.exec()
        else:
            self._open_subfolder("07_Image_Resources")

    def _show_hero_status_menu(self):
        if not self.selected_project:
            return
        menu = QMenu(self)
        curr = self.selected_project.get("status", "In Progress")

        options = [
            ("In Progress", _("🔄 กำลังแปล (In Progress)")),
            ("On Hold", _("🧊 ดองไว้ / พักงาน (On Hold)")),
            ("Completed", _("✅ เสร็จแล้ว (Completed)")),
            ("Cancelled", _("❌ ยกเลิก (Cancelled)"))
        ]
        for st_code, st_label in options:
            act = menu.addAction(f"✓ {st_label}" if curr == st_code else st_label)
            act.triggered.connect(lambda _, sc=st_code: self._set_hero_status(sc))

        pos = self.btn_hero_status.mapToGlobal(QPoint(0, self.btn_hero_status.height() + 2))
        menu.exec(pos)

    def _set_hero_status(self, new_status):
        if not self.selected_project:
            return
        self.selected_project["status"] = new_status
        self.status_changed.emit(self.selected_project, new_status)

    def _request_inspection(self, project):
        key = self._get_project_key(project)
        cached = self._inspection_cache.get(key)
        if self._closing or (cached and time.monotonic() - cached["time"] < 30):
            return
        job_key = "inspect:" + key
        if job_key in self.tasks.jobs:
            return
        snapshot = dict(project)
        def inspect():
            folders = {}
            for logical in ("01_Original_Backup", "02_Translation_Workspace", "03_Font_and_UI", "04_Packed_Mod"):
                files = []
                for directory in WorkspaceSchema.folders(snapshot, logical):
                    with os.scandir(directory) as entries:
                        files.extend(entry.name for entry in entries if not entry.name.startswith('.') and entry.is_file(follow_symlinks=False))
                folders[logical] = (len(files), files)
            note = snapshot.get("notes")
            meta_file = os.path.join(snapshot.get("path", ""), "thub_project.json")
            if note is None and os.path.isfile(meta_file):
                with open(meta_file, encoding="utf-8-sig") as handle:
                    note = json.load(handle).get("notes", "")
            return {"folders": folders, "note": note, "time": time.monotonic()}
        self.tasks.submit(job_key, inspect, lambda result: self._inspection_ready(key, result),
                          lambda error: self._inspection_ready(key, {"folders": {}, "note": None, "time": time.monotonic()}))

    def _inspection_ready(self, key, result):
        self._inspection_cache[key] = result
        for project in self.all_projects:
            if self._get_project_key(project) == key and key not in self._dirty_notes and project.get("notes") is None:
                project["notes"] = result.get("note") or ""
        if not self._closing and self.selected_project and self._get_project_key(self.selected_project) == key:
            self._update_hero_stage(self.selected_project)

    def _on_quick_note_changed(self):
        if self._updating_note_programmatically or not self.selected_project:
            return
        key = self._get_project_key(self.selected_project)
        note = self.txt_hero_note.toPlainText()
        self.selected_project["notes"] = note
        self._dirty_notes[key] = (dict(self.selected_project), note)
        self.lbl_note_saved.setText(_("กำลังบันทึก..."))
        self._note_save_timer.start()

    def _save_quick_note(self):
        """Persist captured notes by project identity, including notes from previous selections."""
        self._note_save_timer.stop()
        for key, (project, note) in list(self._dirty_notes.items()):
            # Repeated selection/close events should not cancel an identical in-flight save.
            if self._saving_notes.get(key) == note:
                continue
            self._saving_notes[key] = note
            def save(project=project, note=note):
                ws_path = project.get("path", "")
                meta_file = os.path.join(ws_path, "thub_project.json") if ws_path else ""
                if meta_file and os.path.exists(meta_file):
                    update_json_atomic(meta_file, {"notes": note})
                # Patch the current registry rather than replacing it with an old view list.
                with self.cfg._lock:
                    projects = self.cfg.get_projects()
                    for current in projects:
                        if self._get_project_key(current) == self._get_project_key(project):
                            current["notes"] = note
                            self.cfg.save_projects(projects)
                            break
                return note
            self.tasks.submit("note:" + key, save,
                lambda value, key=key: self._note_saved(key, value),
                lambda error, key=key: self._note_failed(key, error))

    def _note_failed(self, key, error):
        self._saving_notes.pop(key, None)
        self.lbl_note_saved.setText("บันทึกไม่สำเร็จ: " + error)

    def _note_saved(self, key, note):
        self._saving_notes.pop(key, None)
        if key in self._dirty_notes and self._dirty_notes[key][1] == note:
            self._dirty_notes.pop(key)
        if self.selected_project and self._get_project_key(self.selected_project) == key:
            self.lbl_note_saved.setText(_("✓ บันทึกแล้ว") if key not in self._dirty_notes else _("กำลังบันทึก..."))

    def prepare_shutdown(self):
        self._closing = True
        self.image_service.close()
        self._hero_image_requests.clear()
        self._save_quick_note()
        if self.storage_worker and self.storage_worker.isRunning():
            self.storage_worker.cancel()

    def startup_ready(self):
        """The initial cards and their requested images are delivered, not just placeholders."""
        return (self.image_service.is_idle() and not self.tasks.busy() and
                all(getattr(card, "poster_ready", True) for card in self.card_widgets))

    def is_busy(self):
        return self.tasks.busy() or bool(self.storage_worker and self.storage_worker.isRunning())

    def _on_card_cover_loaded(self, proj, cover_file):
        """Updates Hero Stage cover if the background cover fetcher finished for the selected project."""
        if self.selected_project and self._get_project_key(proj) == self._get_project_key(self.selected_project):
            self.lbl_hero_cover.setPixmap(self._render_hero_cover_pixmap(self.selected_project, self.HERO_COVER_W, self.HERO_COVER_H, radius=10))
            self.lbl_compact_cover.setPixmap(self._render_hero_cover_pixmap(self.selected_project, 64, 36, radius=4))

    # ═══════════════════════════════════════════════════════════════════════════
    # CARD SIZE, FILTERING, AND GRID MANAGEMENT
    # ═══════════════════════════════════════════════════════════════════════════
    def set_card_size(self, size_id):
        if size_id not in ProjectCardQt.SIZE_CONFIGS:
            return
        if self.card_size == size_id:
            return
        self.card_size = size_id
        self.cfg.set("dashboard_card_size", size_id)

        # Update button visual styling
        for sid, btn in self.size_buttons.items():
            is_active = (sid == size_id)
            btn.setProperty("active", "true" if is_active else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        self.table_header.setVisible(size_id == "table")

        size_cfg = ProjectCardQt.SIZE_CONFIGS.get(self.card_size, ProjectCardQt.SIZE_CONFIGS["normal"])
        self.grid_layout.setSpacing(size_cfg["spacing"])

        # Invalidate existing pool to force card resizing
        for k, card in list(self._card_pool.items()):
            card.setParent(None)
            card.deleteLater()
        self._card_pool.clear()

        self.apply_search_and_filter()

    def _calculate_category_counts(self):
        counts = {
            "all": 0,
            "translating": 0,
            "on_hold": 0,
            "completed": 0,
            "pinned": 0,
            "archived": 0
        }
        for p in self.all_projects:
            is_archived = p.get("is_archived", False)
            status = p.get("status", "")
            arch_status = p.get("archive_status", "")
            pct = p.get("progress", {}).get("percentage", 0)

            is_on_hold = status in ("On Hold", "Paused", "Shelved", "ดอง") or arch_status in ("On Hold", "Paused", "Shelved", "ดอง")
            is_completed = (status == "Completed") or (pct >= 100) or (arch_status == "Completed")
            is_cancelled = status in ("Cancelled", "Canceled", "ยกเลิก") or arch_status in ("Cancelled", "Canceled", "ยกเลิก")

            if is_archived:
                counts["archived"] += 1
                if is_on_hold:
                    counts["on_hold"] += 1
            else:
                counts["all"] += 1
                if p.get("is_pinned", False):
                    counts["pinned"] += 1
                if is_on_hold:
                    counts["on_hold"] += 1
                elif is_completed:
                    counts["completed"] += 1
                elif not is_cancelled:
                    counts["translating"] += 1

        return counts

    def _update_filter_button_labels(self, counts):
        for fid, base_label in self.FILTER_DEFS:
            if fid in self.filter_buttons:
                c = counts.get(fid, 0)
                self.filter_buttons[fid].setText(f"{_(base_label)} ({c})")

    def retranslate_ui(self):
        """Retranslate filter chips and refresh view upon language change."""
        counts = self._calculate_category_counts()
        self._update_filter_button_labels(counts)
        self._apply_stage_visibility()
        self.apply_search_and_filter()

    def _set_filter(self, filter_id):
        self.active_filter_id = filter_id
        for fid, btn in self.filter_buttons.items():
            is_active = (fid == filter_id)
            btn.setProperty("active", "true" if is_active else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self.apply_search_and_filter()

    def apply_search_and_filter(self, query=None):
        if query is not None:
            self._last_query = query
        q = (self._last_query or "").lower().strip()
        filtered = []

        counts = self._calculate_category_counts()
        self._update_filter_button_labels(counts)

        is_archive_view = (self.active_filter_id == "archived")
        is_on_hold_view = (self.active_filter_id == "on_hold")

        for p in self.all_projects:
            is_archived = p.get("is_archived", False)
            status = p.get("status", "")
            arch_status = p.get("archive_status", "")
            pct = p.get("progress", {}).get("percentage", 0)

            is_on_hold = status in ("On Hold", "Paused", "Shelved", "ดอง") or arch_status in ("On Hold", "Paused", "Shelved", "ดอง")
            is_completed = (status == "Completed") or (pct >= 100) or (arch_status == "Completed")
            is_cancelled = status in ("Cancelled", "Canceled", "ยกเลิก") or arch_status in ("Cancelled", "Canceled", "ยกเลิก")

            if is_archive_view:
                if not is_archived:
                    continue
            elif is_on_hold_view:
                if not is_on_hold:
                    continue
            else:
                if is_archived:
                    continue  # Hide archived projects from regular tabs

                if self.active_filter_id == "translating":
                    if is_completed or is_cancelled or is_on_hold:
                        continue
                elif self.active_filter_id == "completed":
                    if not is_completed:
                        continue
                elif self.active_filter_id == "pinned":
                    if not p.get("is_pinned", False):
                        continue

            if q and q not in p.get("name", "").lower():
                continue

            filtered.append(p)

        self.filtered_projects = filtered

        # Ensure selected_project is valid and up-to-date
        if self.selected_project:
            sel_key = self._get_project_key(self.selected_project)
            matched = next((p for p in self.all_projects if self._get_project_key(p) == sel_key), None)
            if matched:
                self.selected_project = matched
            else:
                self.selected_project = self.filtered_projects[0] if self.filtered_projects else (self.all_projects[0] if self.all_projects else None)
        else:
            self.selected_project = self.filtered_projects[0] if self.filtered_projects else (self.all_projects[0] if self.all_projects else None)

        self._render_cards()
        self._apply_stage_visibility()
        if self.selected_project:
            self._update_hero_stage(self.selected_project)
        self._update_selected_card_highlight()

        active_count = sum(1 for p in self.all_projects if not p.get("is_archived", False))
        self.counts_changed.emit(len(filtered), active_count)

    def _get_project_key(self, proj):
        return proj.get("path") or proj.get("name") or str(id(proj))

    def _create_card_widget(self, proj):
        card = ProjectCardQt(proj, card_size=self.card_size, parent=self.cards_container, image_service=self.image_service)
        card.tstudio_clicked.connect(self.tstudio_requested.emit)
        card.ai_clicked.connect(self.ai_requested.emit)
        card.selected.connect(self.select_project)
        card.archive_toggled.connect(self.archive_toggled.emit)
        card.archive_requested.connect(self.archive_requested.emit)
        card.pin_toggled.connect(self.pin_toggled.emit)
        card.status_toggled.connect(self.status_toggled.emit)
        card.status_changed.connect(self.status_changed.emit)
        card.delete_requested.connect(self.delete_requested.emit)
        card.cover_edit_requested.connect(self.cover_edit_requested.emit)
        card.engine_edit_requested.connect(self.engine_edit_requested.emit)
        card.settings_requested.connect(self.settings_requested.emit)
        card.adopt_requested.connect(self.adopt_requested.emit)
        card.move_requested.connect(self.move_requested.emit)
        card.cover_loaded.connect(lambda cover_file, p=proj: self._on_card_cover_loaded(p, cover_file))
        return card

    def _render_cards(self):
        # 1. Clean up cards in pool that are no longer in all_projects
        all_keys = {self._get_project_key(p) for p in self.all_projects}
        for k in list(self._card_pool.keys()):
            if k not in all_keys:
                old_card = self._card_pool.pop(k)
                old_card.setParent(None)
                old_card.deleteLater()

        # 2. Re-use or instantiate cards for filtered projects
        visible_cards = []
        active_keys = set()

        for proj in self.filtered_projects:
            k = self._get_project_key(proj)
            active_keys.add(k)
            card = self._card_pool.get(k)
            if card is not None:
                # If card visual state or card_size changed, recreate just this card
                if (getattr(card, "card_size", "normal") != self.card_size or
                    getattr(card, "_structural_signature", None) != ProjectCardQt.structural_signature(proj)):
                    card.setParent(None)
                    card.deleteLater()
                    card = None

            if card is not None:
                card.update_project(proj)
                card.show()
                visible_cards.append(card)
            else:
                card = self._create_card_widget(proj)
                self._card_pool[k] = card
                visible_cards.append(card)

        # 3. Hide any cards in pool that are not visible in current filter/search
        for k, card in self._card_pool.items():
            if k not in active_keys:
                card.hide()

        self.card_widgets = visible_cards
        self._rearrange_grid()

    def _rearrange_grid(self):
        available = self.width() - 32
        if available < 300:
            available = self.scroll_area.viewport().width()
        if available < 300:
            available = 1000
        size_cfg = ProjectCardQt.SIZE_CONFIGS.get(self.card_size, ProjectCardQt.SIZE_CONFIGS["normal"])
        cols = 1 if self.card_size == "table" else max(1, available // (size_cfg["card_w"] + size_cfg["spacing"] * 2))
        signature = (self.card_size, cols, tuple(id(card) for card in self.card_widgets))
        if getattr(self, "_grid_signature", None) == signature:
            return
        self._grid_signature = signature
        while self.grid_layout.count():
            self.grid_layout.takeAt(0)

        if self.card_size == "table":
            self.current_cols = 1
            self.grid_layout.setSpacing(6)
            self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            for idx, card in enumerate(self.card_widgets):
                self.grid_layout.addWidget(card, idx, 0)
        else:
            self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
            avail_w = self.width() - 32
            if avail_w < 300:
                avail_w = self.scroll_area.viewport().width()
            if avail_w < 300:
                avail_w = 1000

            size_cfg = ProjectCardQt.SIZE_CONFIGS.get(self.card_size, ProjectCardQt.SIZE_CONFIGS["normal"])
            self.grid_layout.setSpacing(size_cfg["spacing"])
            card_total_w = size_cfg["card_w"] + size_cfg["spacing"] * 2
            cols = max(1, avail_w // card_total_w)
            self.current_cols = cols

            for idx, card in enumerate(self.card_widgets):
                row = idx // cols
                col = idx % cols
                self.grid_layout.addWidget(card, row, col)

    # --- Drag & Drop Helpers ---
    def get_target_card_index(self, pos):
        if not self.card_widgets:
            return 0

        for idx, card in enumerate(self.card_widgets):
            if card.geometry().contains(pos):
                return idx

        closest_idx = 0
        min_dist = float('inf')
        for idx, card in enumerate(self.card_widgets):
            c = card.geometry().center()
            dist = (c.x() - pos.x()) ** 2 + (c.y() - pos.y()) ** 2
            if dist < min_dist:
                min_dist = dist
                closest_idx = idx

        c = self.card_widgets[closest_idx].geometry().center()
        threshold = 24 if self.card_size == "table" else 60
        if pos.y() > c.y() + threshold or (abs(pos.y() - c.y()) <= threshold and pos.x() > c.x()):
            return min(closest_idx + 1, len(self.card_widgets) - 1)
        return closest_idx

    def highlight_drop_target(self, target_idx):
        for idx, card in enumerate(self.card_widgets):
            card.set_drop_target(idx == target_idx)

    def clear_drop_highlights(self):
        for card in self.card_widgets:
            card.set_drop_target(False)

    def handle_card_dropped(self, card_name, target_idx):
        try:
            self.clear_drop_highlights()
            if not self.filtered_projects or target_idx < 0:
                return

            target_idx = max(0, min(target_idx, len(self.filtered_projects) - 1))
            target_proj = self.filtered_projects[target_idx]
            if target_proj.get("name") == card_name:
                return

            src_proj = next((p for p in self.all_projects if p.get("name") == card_name), None)
            if not src_proj:
                return

            # Determine relative movement direction in filtered list
            src_filtered_idx = next((i for i, p in enumerate(self.filtered_projects) if p.get("name") == card_name), 0)

            # Reorder within self.all_projects
            self.all_projects.remove(src_proj)
            target_all_idx = self.all_projects.index(target_proj)

            if src_filtered_idx < target_idx:
                self.all_projects.insert(target_all_idx + 1, src_proj)
            else:
                self.all_projects.insert(target_all_idx, src_proj)

            self.order_changed.emit(self.all_projects)
            self.apply_search_and_filter()
        except Exception:
            import traceback; traceback.print_exc()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.card_size != "table":
            size_cfg = ProjectCardQt.SIZE_CONFIGS.get(self.card_size, ProjectCardQt.SIZE_CONFIGS["normal"])
            card_total_w = size_cfg["card_w"] + size_cfg["spacing"] * 2
            avail_w = self.width() - 32
            new_cols = max(1, avail_w // card_total_w)
            if new_cols != self.current_cols:
                self._rearrange_grid()

    def showEvent(self, event):
        super().showEvent(event)
        self._rearrange_grid()

    def _apply_cached_storage_sizes(self):
        cache = ProjectStorageService.get_cached_sizes()
        size_tuples = []
        for p in self.all_projects:
            path = p.get("path", "")
            cached = cache.get(path)
            if "_storage_bytes" in p and p["_storage_bytes"] > 0:
                sz = p["_storage_bytes"]
            elif cached:
                sz = cached.get("size", 0)
                p["_storage_bytes"] = sz
                p["_storage_size_str"] = ProjectStorageService.format_size(sz)
            else:
                sz = 0
            size_tuples.append((p, sz))

        self.storage_data_updated.emit(size_tuples)

    def _start_storage_scan_worker(self, force_refresh=False):
        if self._closing:
            return
        if self.storage_worker and self.storage_worker.isRunning():
            self._storage_rescan_pending = True
            self._storage_rescan_force = getattr(self, "_storage_rescan_force", False) or force_refresh
            return
        if not self.all_projects:
            return

        self.storage_scanning_changed.emit(True)
        self.storage_worker = StorageScanWorker(self.all_projects, force_refresh=force_refresh, parent=self)
        self.storage_worker.progress_updated.connect(self.storage_progress_changed.emit)
        self.storage_worker.project_scanned.connect(self._on_single_project_scanned)
        self.storage_worker.scan_finished.connect(self._on_storage_scan_finished)
        self.storage_worker.scan_failed.connect(self._on_storage_scan_failed)
        self.storage_worker.finished.connect(self._storage_worker_finished)
        self.storage_worker.start()

    def _storage_worker_finished(self):
        worker = self.storage_worker
        self.storage_worker = None
        if worker:
            worker.deleteLater()
        if getattr(self, "_storage_rescan_pending", False) and not self._closing:
            self._storage_rescan_pending = False
            force = getattr(self, "_storage_rescan_force", False)
            self._storage_rescan_force = False
            self._start_storage_scan_worker(force_refresh=force)

    def _on_single_project_scanned(self, path, size_bytes):
        size_str = ProjectStorageService.format_size(size_bytes)
        for p in self.all_projects:
            if p.get("path") == path:
                p["_storage_bytes"] = size_bytes
                p["_storage_size_str"] = size_str
                # Update card if currently rendered
                k = self._get_project_key(p)
                card = self._card_pool.get(k)
                if card:
                    card.update_project(p)
                # Update hero stage if currently selected
                if self.selected_project and self._get_project_key(self.selected_project) == k:
                    self._update_hero_stage(self.selected_project)
                break
        if hasattr(self, "_storage_panel_update_timer"):
            self._storage_panel_update_timer.start()

    def _on_storage_scan_failed(self, error):
        self.lbl_insp_size.setToolTip("สแกนพื้นที่ไม่สำเร็จ: " + error)

    def _on_storage_scan_finished(self, cache_dict):
        self.storage_scanning_changed.emit(False)
        self._apply_cached_storage_sizes()
        if self.selected_project:
            self._update_hero_stage(self.selected_project)

    def _refresh_storage_scan(self):
        self._start_storage_scan_worker(force_refresh=True)

    def _sort_projects_by_size(self):
        # Sort descending by disk size
        self.all_projects.sort(key=lambda p: p.get("_storage_bytes", 0), reverse=True)
        self.order_changed.emit(self.all_projects)
        self.apply_search_and_filter()

    def update_projects(self, projects):
        for project in projects:
            dirty = self._dirty_notes.get(self._get_project_key(project))
            if dirty:
                project["notes"] = dirty[1]
        self.all_projects = projects
        self._apply_cached_storage_sizes()
        self.apply_search_and_filter()
        self._start_storage_scan_worker(force_refresh=False)
