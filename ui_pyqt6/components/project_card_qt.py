import os
import weakref
from collections import OrderedDict
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, QMenu, QSizePolicy,
    QApplication
)
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath, QColor, QDrag, QCursor, QImage, QImageReader
from PyQt6.QtCore import Qt, QRectF, QPoint, QMimeData, pyqtSignal, QTimer, QSize
from core.tool_launcher import ToolLauncher
from core.engine_scanner import EngineScanner
from core.config_manager import ConfigManager
from ui_pyqt6.dialogs.bible_viewer_dialog_qt import BibleViewerDialogQt
from ui_pyqt6.dialogs.archive_select_dialog_qt import ArchiveSelectDialogQt
from i18n_helper import _

class ClickableStatusPill(QFrame):
    """Interactive status badge that can be clicked to toggle project status."""
    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        try:
            if event.button() == Qt.MouseButton.LeftButton:
                self.clicked.emit()
                event.accept()
                return
        except Exception:
            pass
        super().mousePressEvent(event)


class ProjectCardQt(QFrame):
    """
    PyQt6 16:9 Widescreen Game Card.
    GPU-accelerated, ultra-fast rendering with multi-size support (compact, normal, large),
    drag & drop reordering, and dedicated On Hold / Archive badges.
    """

    SIZE_CONFIGS = {
        "compact": {
            "card_w": 224,
            "card_h": 162,
            "poster_w": 212,
            "poster_h": 119,
            "margin": 6,
            "spacing": 5,
            "title_size": 11,
            "badge_font_size": 8,
            "dot_font_size": 8,
            "status_font_size": 10,
            "btn_font_size": 10,
            "btn_h": 26,
            "btn_folder_w": 24,
            "btn_more_w": 18,
            "title_max_len": 16,
            "tstudio_label": "🚀 TStudio",
            "ai_label": "🤖 AI"
        },
        "normal": {
            "card_w": 284,
            "card_h": 204,
            "poster_w": 268,
            "poster_h": 151,
            "margin": 8,
            "spacing": 6,
            "title_size": 13,
            "badge_font_size": 9,
            "dot_font_size": 9,
            "status_font_size": 11,
            "btn_font_size": 11,
            "btn_h": 28,
            "btn_folder_w": 28,
            "btn_more_w": 20,
            "title_max_len": 22,
            "tstudio_label": "🚀 TStudio",
            "ai_label": "🤖 AI Helper"
        },
        "large": {
            "card_w": 356,
            "card_h": 252,
            "poster_w": 336,
            "poster_h": 189,
            "margin": 10,
            "spacing": 7,
            "title_size": 15,
            "badge_font_size": 10,
            "dot_font_size": 10,
            "status_font_size": 12,
            "btn_font_size": 12,
            "btn_h": 32,
            "btn_folder_w": 32,
            "btn_more_w": 24,
            "title_max_len": 28,
            "tstudio_label": "🚀 TStudio",
            "ai_label": "🤖 AI Helper"
        },
        "table": {
            "card_w": -1,
            "card_h": 54,
            "poster_w": 72,
            "poster_h": 40,
            "margin": 6,
            "spacing": 10,
            "title_size": 13,
            "badge_font_size": 9,
            "dot_font_size": 8,
            "status_font_size": 11,
            "btn_font_size": 11,
            "btn_h": 28,
            "btn_folder_w": 28,
            "btn_more_w": 24,
            "title_max_len": 60,
            "tstudio_label": "🚀 TStudio",
            "ai_label": "🤖 AI"
        }
    }

    tstudio_clicked = pyqtSignal(dict)
    ai_clicked = pyqtSignal(dict)
    selected = pyqtSignal(dict)
    archive_toggled = pyqtSignal(dict)
    archive_requested = pyqtSignal(dict, str)
    pin_toggled = pyqtSignal(dict)
    status_toggled = pyqtSignal(dict)
    status_changed = pyqtSignal(dict, str)
    delete_requested = pyqtSignal(dict)
    cover_edit_requested = pyqtSignal(dict)
    engine_edit_requested = pyqtSignal(dict)
    settings_requested = pyqtSignal(dict)
    adopt_requested = pyqtSignal(dict)
    move_requested = pyqtSignal(dict)
    cover_loaded = pyqtSignal(str)
    poster_ready_changed = pyqtSignal()

    # Keep only bounded, final-size posters. Full-resolution source images are
    # temporary and must never grow the shared cache with every progress update.
    _pixmap_cache = OrderedDict()
    _pixmap_cache_bytes = 0
    MAX_PIXMAP_CACHE_ENTRIES = 128
    MAX_PIXMAP_CACHE_BYTES = 32 * 1024 * 1024

    def __init__(self, project, card_size="normal", parent=None, image_service=None):
        super().__init__(parent)
        self.project = project
        self.image_service = image_service
        self.poster_ready = image_service is None
        self._async_image_key = None
        self._async_service_generation = None
        self._delivered_image = None
        self._cover_request_identity = None
        self._structural_signature = self.structural_signature(project)
        self.card_size = card_size if card_size in self.SIZE_CONFIGS else "normal"
        self.cfg_size = self.SIZE_CONFIGS[self.card_size]
        self.CARD_WIDTH = self.cfg_size["card_w"]
        self.CARD_HEIGHT = self.cfg_size["card_h"]
        self.POSTER_WIDTH = self.cfg_size["poster_w"]
        self.POSTER_HEIGHT = self.cfg_size["poster_h"]

        self.setObjectName("ProjectCard")
        self.setProperty("class", "ProjectCard")
        if self.card_size == "table":
            self.setFixedHeight(self.CARD_HEIGHT)
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            self.setProperty("layout", "table")
        else:
            self.setFixedSize(self.CARD_WIDTH, self.CARD_HEIGHT)
            self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            self.setProperty("layout", "grid")

        self.setCursor(Qt.CursorShape.PointingHandCursor)

        is_archived = self.project.get("is_archived", False)
        self.setProperty("archived", "true" if is_archived else "false")
        self.setProperty("drop_target", "false")
        self.setProperty("selected", "false")

        # Fast Engine Badge Resolution (instant, avoiding synchronous 732-bible deep scan)
        saved_eng = self.project.get("engine") or self.project.get("engine_badge")
        if saved_eng:
            self.badge_text = EngineScanner.normalize_engine_name(saved_eng)
            self.badge_color = EngineScanner.get_engine_color(self.badge_text)
        else:
            engine_info = EngineScanner.detect_engine(
                game_dir=project.get("game_dir", ""),
                workspace_dir=project.get("path", ""),
                title=project.get("name", ""),
                saved_engine=None
            )
            self.badge_text = engine_info.get("badge", "Custom Engine")
            self.badge_color = engine_info.get("badge_color", "#94a3b8")
            self.project["engine"] = self.badge_text

        # Connect thread-safe cover loaded signal
        self.cover_loaded.connect(self._on_cover_loaded)

        self._build_ui()

        # Non-blocking automatic cover retrieval if project has no cover
        if not self._get_cover_path():
            self._trigger_auto_fetch_cover()

    @staticmethod
    def structural_signature(project):
        """Immutable overlay state, even when callers mutate the project dictionary."""
        archived = bool(project.get("is_archived", False))
        archive_status = (project.get("status", "") or project.get("archive_status", "")) if archived else ""
        return bool(project.get("is_pinned", False)), archived, archive_status

    def set_drop_target(self, is_target: bool):
        """Toggles dashed Cyan highlight when a card is dragged over."""
        val = "true" if is_target else "false"
        if self.property("drop_target") != val:
            self.setProperty("drop_target", val)
            self.style().unpolish(self)
            self.style().polish(self)

    def set_selected(self, is_selected: bool):
        """Toggles Cyan highlight border when card is selected on the Hero Stage."""
        val = "true" if is_selected else "false"
        if self.property("selected") != val:
            self.setProperty("selected", val)
            self.style().unpolish(self)
            self.style().polish(self)
        if hasattr(self, "lbl_stage_indicator"):
            self.lbl_stage_indicator.setVisible(is_selected)

    def enterEvent(self, event):
        if hasattr(self, "hover_overlay") and self.card_size != "table":
            self.hover_overlay.show()
            self.hover_overlay.raise_()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if hasattr(self, "hover_overlay") and self.card_size != "table":
            self.hover_overlay.hide()
        super().leaveEvent(event)

    def _build_ui(self):
        if self.card_size == "table":
            self._build_table_row_ui()
        else:
            self._build_grid_card_ui()

    def _build_table_row_ui(self):
        """Build horizontal table row layout for compact list/table view."""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(8, 4, 10, 4)
        main_layout.setSpacing(10)

        # 1. 16:9 Thumbnail Poster (72x40)
        self.poster_container = QWidget(self)
        self.poster_container.setFixedSize(self.POSTER_WIDTH, self.POSTER_HEIGHT)
        self.poster_container.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        self.lbl_poster = QLabel(self.poster_container)
        self.lbl_poster.setFixedSize(self.POSTER_WIDTH, self.POSTER_HEIGHT)
        self.lbl_poster.setPixmap(self._get_cached_rounded_poster())
        self.lbl_poster.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        main_layout.addWidget(self.poster_container)

        # 2. Title + Pin / Archive tag (Stretch=1)
        title_box = QHBoxLayout()
        title_box.setSpacing(6)
        title_box.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        if self.project.get("is_pinned", False):
            lbl_pin = QLabel("📌")
            lbl_pin.setToolTip(_("โปรเจกต์ปักหมุด"))
            lbl_pin.setStyleSheet("font-size: 11px;")
            lbl_pin.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            title_box.addWidget(lbl_pin)

        if self.project.get("is_archived", False):
            arch_status = self.project.get("status", "") or self.project.get("archive_status", "")
            if arch_status == "Completed":
                arch_text = _("📦 เสร็จแล้ว")
                arch_color = "#22c55e"
            elif arch_status in ("Cancelled", "Canceled", "ยกเลิก"):
                arch_text = _("📦 ยกเลิก")
                arch_color = "#ef4444"
            elif arch_status in ("On Hold", "Paused", "Shelved", "ดอง"):
                arch_text = _("📦 ดองไว้")
                arch_color = "#c084fc"
            else:
                arch_text = _("📦 คลัง")
                arch_color = "#fb923c"

            lbl_arch = QLabel(arch_text)
            lbl_arch.setStyleSheet(f"""
                color: {arch_color};
                background: rgba(20, 20, 30, 200);
                border: 1px solid {arch_color};
                border-radius: 4px;
                padding: 1px 4px;
                font-size: 9px;
                font-weight: bold;
            """)
            lbl_arch.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            title_box.addWidget(lbl_arch)

        raw_title = self.project.get("name", "Unknown Game")
        max_chars = self.cfg_size["title_max_len"]
        display_title = raw_title if len(raw_title) <= max_chars else raw_title[:max_chars - 2] + "..."
        self.lbl_title = QLabel(display_title)
        self.lbl_title.setProperty("class", "ProjectTitle")
        self.lbl_title.setToolTip(raw_title)
        self.lbl_title.setStyleSheet(f"font-size: {self.cfg_size['title_size']}px; font-weight: bold;")
        self.lbl_title.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        title_box.addWidget(self.lbl_title, stretch=1)

        main_layout.addLayout(title_box, stretch=1)

        # 3. Engine Badge Column (~100px)
        if self.badge_text:
            self.lbl_badge = QLabel(f" {self.badge_text} ")
            self.lbl_badge.setStyleSheet(f"""
                background-color: rgba(16, 20, 30, 220);
                color: {self.badge_color};
                border: 1px solid {self.badge_color};
                border-radius: 4px;
                padding: 2px 6px;
                font-size: {self.cfg_size['badge_font_size']}px;
                font-weight: bold;
            """)
            self.lbl_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.lbl_badge.setFixedHeight(22)
            self.lbl_badge.setFixedWidth(100)
            self.lbl_badge.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            main_layout.addWidget(self.lbl_badge)
        else:
            dummy_badge = QWidget()
            dummy_badge.setFixedWidth(100)
            main_layout.addWidget(dummy_badge)

        # 3.5 Storage Size Column (~85px)
        size_str = self.project.get("_storage_size_str", "-")
        self.lbl_table_size = QLabel(size_str)
        self.lbl_table_size.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: 600;")
        self.lbl_table_size.setFixedWidth(85)
        self.lbl_table_size.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_table_size.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        main_layout.addWidget(self.lbl_table_size)

        # 4. Status Column (Interactive Pill, ~110px)
        status_text, dot_color = self._get_status_info()
        self.pill = ClickableStatusPill()
        self.pill.setProperty("class", "StatusPill")
        self.pill.setCursor(Qt.CursorShape.PointingHandCursor)
        self.pill.setToolTip(_("คลิกเพื่อเลือกสถานะ (กำลังแปล, ดองไว้, เสร็จแล้ว, ยกเลิก)"))
        self.pill.clicked.connect(self._show_status_menu)
        self.pill.setFixedWidth(110)
        pill_layout = QHBoxLayout(self.pill)
        pill_layout.setContentsMargins(6, 2, 6, 2)
        pill_layout.setSpacing(4)
        pill_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_dot = QLabel("●")
        self.lbl_dot.setStyleSheet(f"color: {dot_color}; font-size: {self.cfg_size['dot_font_size']}px;")
        self.lbl_dot.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.lbl_status = QLabel(status_text)
        self.lbl_status.setProperty("class", "StatusText")
        self.lbl_status.setStyleSheet(f"font-size: {self.cfg_size['status_font_size']}px;")
        self.lbl_status.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        pill_layout.addWidget(self.lbl_dot)
        pill_layout.addWidget(self.lbl_status)
        main_layout.addWidget(self.pill)

        # 5. Actions Column: [🚀 TStudio] [🤖 AI] [📁] [⋮] (~160px)
        action_row = QHBoxLayout()
        action_row.setContentsMargins(0, 0, 0, 0)
        action_row.setSpacing(4)

        btn_h = self.cfg_size["btn_h"]
        btn_f = self.cfg_size["btn_font_size"]

        self.btn_tstudio = QPushButton(self.cfg_size["tstudio_label"])
        self.btn_tstudio.setProperty("class", "BtnTStudio")
        self.btn_tstudio.setFixedHeight(btn_h)
        self.btn_tstudio.setStyleSheet(f"font-size: {btn_f}px; padding: 2px 8px;")
        self.btn_tstudio.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_tstudio.clicked.connect(self._on_tstudio)
        action_row.addWidget(self.btn_tstudio)

        self.btn_ai = QPushButton(self.cfg_size["ai_label"])
        self.btn_ai.setProperty("class", "BtnAI")
        self.btn_ai.setFixedHeight(btn_h)
        self.btn_ai.setStyleSheet(f"font-size: {btn_f}px; padding: 2px 6px;")
        self.btn_ai.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_ai.clicked.connect(self._on_ai)
        action_row.addWidget(self.btn_ai)

        self.btn_folder = QPushButton("📁")
        self.btn_folder.setProperty("class", "BtnFolder")
        self.btn_folder.setFixedSize(self.cfg_size["btn_folder_w"], btn_h)
        self.btn_folder.setStyleSheet(f"font-size: {btn_f}px; padding: 0px;")
        self.btn_folder.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_folder.clicked.connect(self._on_folder)
        action_row.addWidget(self.btn_folder)

        self.btn_more = QPushButton("⋮")
        self.btn_more.setProperty("class", "BtnMore")
        self.btn_more.setFixedSize(self.cfg_size["btn_more_w"], btn_h)
        self.btn_more.setStyleSheet(f"font-size: {btn_f}px; padding: 0px;")
        self.btn_more.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_more.clicked.connect(self._on_more_clicked)
        action_row.addWidget(self.btn_more)

        main_layout.addLayout(action_row)

    def _build_grid_card_ui(self):
        """Build Clean Cinema Card layout for Idea 4.2 grid view."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(
            self.cfg_size["margin"], self.cfg_size["margin"],
            self.cfg_size["margin"], self.cfg_size["margin"]
        )
        main_layout.setSpacing(self.cfg_size["spacing"])

        # 1. 16:9 Poster with Badge Overlay & Hover Quick-Action Dock
        self.poster_container = QWidget(self)
        self.poster_container.setFixedSize(self.POSTER_WIDTH, self.POSTER_HEIGHT)

        self.lbl_poster = QLabel(self.poster_container)
        self.lbl_poster.setFixedSize(self.POSTER_WIDTH, self.POSTER_HEIGHT)
        self.lbl_poster.setPixmap(self._get_cached_rounded_poster())
        self.lbl_poster.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        # Top-Left Badges (Pin / Archive)
        left_offset = 6 if self.card_size == "compact" else 8
        badge_f_size = self.cfg_size["badge_font_size"]
        top_offset = 6 if self.card_size == "compact" else 8

        if self.project.get("is_pinned", False):
            lbl_pin = QLabel("📌 ปักหมุด", self.poster_container)
            lbl_pin.setStyleSheet(f"""
                background-color: rgba(16, 20, 30, 220);
                color: #fbbf24;
                border: 1px solid #f59e0b;
                border-radius: 4px;
                padding: 1px 5px;
                font-size: {badge_f_size}px;
                font-weight: bold;
            """)
            lbl_pin.adjustSize()
            lbl_pin.move(left_offset, top_offset)
            lbl_pin.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            left_offset += lbl_pin.width() + 4

        if self.project.get("is_archived", False):
            arch_status = self.project.get("status", "") or self.project.get("archive_status", "")
            if arch_status == "Completed":
                arch_text = _("📦 คลัง: เสร็จแล้ว")
                arch_color = "#22c55e"
                arch_border = "#16a34a"
            elif arch_status in ("Cancelled", "Canceled", "ยกเลิก"):
                arch_text = _("📦 คลัง: ยกเลิก")
                arch_color = "#ef4444"
                arch_border = "#dc2626"
            elif arch_status in ("On Hold", "Paused", "Shelved", "ดอง"):
                arch_text = _("📦 คลัง: ดองไว้")
                arch_color = "#c084fc"
                arch_border = "#9333ea"
            else:
                arch_text = _("📦 คลังจัดเก็บ")
                arch_color = "#fb923c"
                arch_border = "#ea580c"

            lbl_arch = QLabel(arch_text, self.poster_container)
            lbl_arch.setStyleSheet(f"""
                background-color: rgba(20, 20, 30, 230);
                color: {arch_color};
                border: 1px solid {arch_border};
                border-radius: 4px;
                padding: 1px 5px;
                font-size: {badge_f_size}px;
                font-weight: bold;
            """)
            lbl_arch.adjustSize()
            lbl_arch.move(left_offset, top_offset)
            lbl_arch.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        # Engine Badge (Top-Right)
        if self.badge_text:
            self.lbl_badge = QLabel(f" {self.badge_text} ", self.poster_container)
            self.lbl_badge.setStyleSheet(f"""
                background-color: rgba(16, 20, 30, 220);
                color: {self.badge_color};
                border: 1px solid {self.badge_color};
                border-radius: 4px;
                padding: 1px 5px;
                font-size: {badge_f_size}px;
                font-weight: bold;
            """)
            self.lbl_badge.adjustSize()
            badge_w = self.lbl_badge.width()
            self.lbl_badge.move(self.POSTER_WIDTH - badge_w - top_offset, top_offset)
            self.lbl_badge.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        # Hover Quick-Action Dock at bottom of poster (hidden by default)
        self.hover_overlay = QFrame(self.poster_container)
        self.hover_overlay.setObjectName("HoverActionDock")
        self.hover_overlay.setStyleSheet("""
            QFrame#HoverActionDock {
                background-color: rgba(15, 23, 42, 0.92);
                border: 1px solid rgba(56, 189, 248, 0.45);
                border-radius: 6px;
            }
        """)
        overlay_h = 30 if self.card_size == "compact" else 34
        dock_w = self.POSTER_WIDTH - 12
        self.hover_overlay.setGeometry(6, self.POSTER_HEIGHT - overlay_h - 8, dock_w, overlay_h)
        hover_layout = QHBoxLayout(self.hover_overlay)
        hover_layout.setContentsMargins(4, 2, 4, 2)
        hover_layout.setSpacing(4)

        btn_f = self.cfg_size["btn_font_size"]
        btn_inner_h = overlay_h - 6

        self.btn_tstudio = QPushButton(self.cfg_size["tstudio_label"], self.hover_overlay)
        self.btn_tstudio.setProperty("class", "BtnTStudio")
        self.btn_tstudio.setFixedHeight(btn_inner_h)
        self.btn_tstudio.setStyleSheet(f"font-size: {btn_f}px; padding: 1px 4px;")
        self.btn_tstudio.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_tstudio.clicked.connect(self._on_tstudio)
        hover_layout.addWidget(self.btn_tstudio, stretch=1)

        self.btn_ai = QPushButton(self.cfg_size["ai_label"], self.hover_overlay)
        self.btn_ai.setProperty("class", "BtnAI")
        self.btn_ai.setFixedHeight(btn_inner_h)
        self.btn_ai.setStyleSheet(f"font-size: {btn_f}px; padding: 1px 4px;")
        self.btn_ai.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_ai.clicked.connect(self._on_ai)
        hover_layout.addWidget(self.btn_ai, stretch=1)

        self.btn_folder = QPushButton("📁", self.hover_overlay)
        self.btn_folder.setProperty("class", "BtnFolder")
        self.btn_folder.setFixedSize(self.cfg_size["btn_folder_w"], btn_inner_h)
        self.btn_folder.setStyleSheet(f"font-size: {btn_f}px; padding: 0px;")
        self.btn_folder.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_folder.clicked.connect(self._on_folder)
        hover_layout.addWidget(self.btn_folder)

        self.hover_overlay.hide()

        main_layout.addWidget(self.poster_container)

        # 2. Clean Cinema Footer Row: [Title] [Status Pill] [⋮]
        info_row = QHBoxLayout()
        info_row.setContentsMargins(2, 0, 2, 0)
        info_row.setSpacing(4)

        # Title
        raw_title = self.project.get("name", "Unknown Game")
        max_chars = self.cfg_size["title_max_len"]
        display_title = raw_title if len(raw_title) <= max_chars else raw_title[:max_chars - 2] + "..."
        self.lbl_title = QLabel(display_title)
        self.lbl_title.setProperty("class", "ProjectTitle")
        self.lbl_title.setToolTip(raw_title)
        self.lbl_title.setStyleSheet(f"font-size: {self.cfg_size['title_size']}px; font-weight: bold;")
        self.lbl_title.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        info_row.addWidget(self.lbl_title, stretch=1)

        # Subtle Storage Size Badge (💾 1.2 GB)
        self.lbl_size = QLabel("")
        self.lbl_size.setStyleSheet("""
            color: #94a3b8;
            font-size: 10px;
            font-weight: 600;
            background: rgba(30, 41, 59, 0.65);
            border: 1px solid rgba(51, 65, 85, 0.5);
            border-radius: 4px;
            padding: 1px 4px;
        """)
        self.lbl_size.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        size_str = self.project.get("_storage_size_str", "")
        if size_str:
            self.lbl_size.setText(f"💾 {size_str}")
            self.lbl_size.show()
        else:
            self.lbl_size.hide()
        info_row.addWidget(self.lbl_size)

        # Status Pill (Interactive Status Selector)
        status_text, dot_color = self._get_status_info()
        self.pill = ClickableStatusPill()
        self.pill.setProperty("class", "StatusPill")
        self.pill.setCursor(Qt.CursorShape.PointingHandCursor)
        self.pill.setToolTip(_("คลิกเพื่อเลือกสถานะ (กำลังแปล, ดองไว้, เสร็จแล้ว, ยกเลิก)"))
        self.pill.clicked.connect(self._show_status_menu)
        pill_layout = QHBoxLayout(self.pill)
        pill_pad_x = 4 if self.card_size == "compact" else 6
        pill_layout.setContentsMargins(pill_pad_x, 1, pill_pad_x, 1)
        pill_layout.setSpacing(3)

        self.lbl_dot = QLabel("●")
        self.lbl_dot.setStyleSheet(f"color: {dot_color}; font-size: {self.cfg_size['dot_font_size']}px;")
        self.lbl_dot.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.lbl_status = QLabel(status_text)
        self.lbl_status.setProperty("class", "StatusText")
        self.lbl_status.setStyleSheet(f"font-size: {self.cfg_size['status_font_size']}px;")
        self.lbl_status.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        pill_layout.addWidget(self.lbl_dot)
        pill_layout.addWidget(self.lbl_status)
        info_row.addWidget(self.pill)

        # Subtle More Options Button (⋮)
        self.btn_more = QPushButton("⋮")
        self.btn_more.setProperty("class", "BtnMore")
        self.btn_more.setFixedSize(self.cfg_size["btn_more_w"], 22)
        self.btn_more.setStyleSheet("font-size: 11px; padding: 0px; background: transparent; border: none; color: #94a3b8;")
        self.btn_more.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_more.clicked.connect(self._on_more_clicked)
        info_row.addWidget(self.btn_more)

        main_layout.addLayout(info_row)

    @classmethod
    def clear_pixmap_cache(cls):
        """Clears pixmap cache for all cards immediately."""
        cls._pixmap_cache.clear()
        cls._pixmap_cache_bytes = 0

    @classmethod
    def _remember_pixmap(cls, key, pixmap):
        """Store a rendered poster in the shared LRU within a fixed memory budget."""
        previous = cls._pixmap_cache.pop(key, None)
        if previous is not None:
            cls._pixmap_cache_bytes -= previous.width() * previous.height() * 4
        cls._pixmap_cache[key] = pixmap
        cls._pixmap_cache_bytes += pixmap.width() * pixmap.height() * 4
        while cls._pixmap_cache and (
                len(cls._pixmap_cache) > cls.MAX_PIXMAP_CACHE_ENTRIES or
                cls._pixmap_cache_bytes > cls.MAX_PIXMAP_CACHE_BYTES):
            discarded_key, discarded = cls._pixmap_cache.popitem(last=False)
            cls._pixmap_cache_bytes -= discarded.width() * discarded.height() * 4

    def refresh_poster(self, cover_path=None):
        """Refresh this card's poster while retaining unrelated cards' cached images."""
        # Invalidate by the file fingerprint in the cache key, rather than clearing
        # every other card's cached poster on each ordinary project refresh.
        if cover_path:
            self.project["_cached_cover_path"] = cover_path
        else:
            self.project.pop("_cached_cover_path", None)
        if hasattr(self, "lbl_poster"):
            pixmap = self._get_cached_rounded_poster()
            current = self.lbl_poster.pixmap()
            if current is None or current.cacheKey() != pixmap.cacheKey():
                self.lbl_poster.setPixmap(pixmap)

    def _get_progress_bar_info(self):
        status = self.project.get("status", "In Progress")
        pct = self.project.get("progress", {}).get("percentage")
        if status == "Completed" or (pct is not None and pct >= 100):
            return 100, "#22c55e"
        if status in ("Cancelled", "Canceled", "ยกเลิก"):
            return 100, "#ef4444"
        if status in ("On Hold", "Paused", "Shelved", "ดอง"):
            return max(25, pct if pct is not None else 35), "#c084fc"
        if pct is not None:
            return max(8, pct), "#38bdf8"
        return 42, "#f59e0b"

    def _get_cached_rounded_poster(self):
        if self.image_service is not None:
            generation = self.image_service.generation
            if generation != self._async_service_generation:
                self._async_service_generation = generation
                self._async_image_key = None
        cover_path = self._get_cover_path()
        fingerprint = None
        if cover_path:
            try:
                info = os.stat(cover_path)
                fingerprint = (info.st_mtime_ns, info.st_size)
            except OSError:
                cover_path = None
        offset_x = int(self.project.get("cover_offset_x", 0))  # -100 to +100
        offset_y = int(self.project.get("cover_offset_y", 0))  # -100 to +100
        zoom = float(self.project.get("cover_zoom", 1.0))      # 1.0 to 2.5
        bar_pct, bar_color = self._get_progress_bar_info()
        cache_key = (cover_path, fingerprint, self.POSTER_WIDTH, self.POSTER_HEIGHT, offset_x, offset_y, zoom, bar_pct, bar_color, self.card_size)
        if cache_key in self._pixmap_cache:
            if self.image_service is not None:
                self._async_image_key = self.image_service.key_for(cover_path, self.POSTER_WIDTH, self.POSTER_HEIGHT,
                                                                  offset_x, offset_y, zoom) if cover_path else None
            self.poster_ready = True
            self._pixmap_cache.move_to_end(cache_key)
            return self._pixmap_cache[cache_key]

        async_image = None
        pending = False
        if self.image_service is not None and cover_path:
            request_key = self.image_service.key_for(cover_path, self.POSTER_WIDTH, self.POSTER_HEIGHT,
                                                     offset_x, offset_y, zoom)
            if self._delivered_image is not None and self._delivered_image[0] == request_key:
                async_image = self._delivered_image[1]
            else:
                callback = None
                if self._async_image_key != request_key:
                    self._async_image_key = request_key
                    reference = weakref.ref(self)
                    def callback(image, key=request_key, reference=reference):
                        card = reference()
                        if card is not None:
                            try:
                                card._async_poster_ready(key, image)
                            except RuntimeError:
                                pass
                async_image = self.image_service.request(cover_path, self.POSTER_WIDTH, self.POSTER_HEIGHT,
                    offset_x=offset_x, offset_y=offset_y, zoom=zoom, on_ready=callback)
            pending = async_image is None
        else:
            self._async_image_key = None
        self.poster_ready = not pending

        target_pix = QPixmap(self.POSTER_WIDTH, self.POSTER_HEIGHT)
        target_pix.fill(Qt.GlobalColor.transparent)

        painter = QPainter(target_pix)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        radius = 4 if self.card_size == "table" else 8
        path.addRoundedRect(QRectF(0, 0, self.POSTER_WIDTH, self.POSTER_HEIGHT), radius, radius)
        painter.setClipPath(path)

        if self.image_service is not None:
            # The broker supplies a final-size rectangular crop. Keep rounded
            # clipping and progress overlays here; never crop or zoom it twice.
            if async_image is not None and not async_image.isNull():
                painter.drawImage(0, 0, async_image)
            else:
                painter.fillRect(0, 0, self.POSTER_WIDTH, self.POSTER_HEIGHT, QColor("#181d2a"))
        elif cover_path and os.path.exists(cover_path):
            reader = QImageReader(cover_path)
            source_size = reader.size()
            decoded_target = None
            if source_size.isValid() and source_size.width() > 0 and source_size.height() > 0:
                requested_scale = max(self.POSTER_WIDTH / source_size.width(),
                                      self.POSTER_HEIGHT / source_size.height()) * max(1.0, zoom)
                decoded_target = QSize(max(self.POSTER_WIDTH, int(source_size.width() * requested_scale)),
                                       max(self.POSTER_HEIGHT, int(source_size.height() * requested_scale)))
                # JPEG readers can downsample during decode. Preserve the exact
                # crop dimensions, including zoom, for every supported format.
                reader.setScaledSize(decoded_target)
            img = reader.read()
            # PIL decoding fallback for WebP, progressive JPEGs, or headers with unusual color spaces
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
                base_scale = max(self.POSTER_WIDTH / raw_pix.width(), self.POSTER_HEIGHT / raw_pix.height())
                scale = base_scale * max(1.0, zoom)
                new_w = decoded_target.width() if decoded_target else max(self.POSTER_WIDTH, int(raw_pix.width() * scale))
                new_h = decoded_target.height() if decoded_target else max(self.POSTER_HEIGHT, int(raw_pix.height() * scale))
                scaled = raw_pix.scaled(
                    new_w,
                    new_h,
                    Qt.AspectRatioMode.IgnoreAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )

                center_x = (new_w - self.POSTER_WIDTH) / 2.0
                center_y = (new_h - self.POSTER_HEIGHT) / 2.0

                max_shift_x = (new_w - self.POSTER_WIDTH) / 2.0
                max_shift_y = (new_h - self.POSTER_HEIGHT) / 2.0

                crop_x = int(center_x + (offset_x / 100.0) * max_shift_x)
                crop_y = int(center_y + (offset_y / 100.0) * max_shift_y)

                crop_x = max(0, min(crop_x, new_w - self.POSTER_WIDTH))
                crop_y = max(0, min(crop_y, new_h - self.POSTER_HEIGHT))

                painter.drawPixmap(0, 0, scaled.copy(crop_x, crop_y, self.POSTER_WIDTH, self.POSTER_HEIGHT))
            else:
                painter.fillRect(0, 0, self.POSTER_WIDTH, self.POSTER_HEIGHT, QColor("#181d2a"))
        else:
            painter.fillRect(0, 0, self.POSTER_WIDTH, self.POSTER_HEIGHT, QColor("#181d2a"))

        # Thin 4px progress bar along the bottom edge of grid cards
        if self.card_size != "table":
            bar_h = 4
            bar_y = self.POSTER_HEIGHT - bar_h
            painter.fillRect(0, bar_y, self.POSTER_WIDTH, bar_h, QColor(15, 23, 42, 190))
            fill_w = max(0, min(self.POSTER_WIDTH, int(self.POSTER_WIDTH * (bar_pct / 100.0))))
            painter.fillRect(0, bar_y, fill_w, bar_h, QColor(bar_color))

        painter.end()
        if not pending and not (self.image_service is not None and self.image_service.is_closed):
            self._remember_pixmap(cache_key, target_pix)
        return target_pix

    def _async_poster_ready(self, key, image):
        if key != self._async_image_key:
            return
        current_key = self.image_service.key_for(self._get_cover_path(), self.POSTER_WIDTH, self.POSTER_HEIGHT,
            self.project.get("cover_offset_x", 0), self.project.get("cover_offset_y", 0), self.project.get("cover_zoom", 1.0))
        if current_key != key:
            return
        # Render directly from the delivered QImage even if a very small broker
        # budget evicted it before this callback. Do not retain it on the card.
        self._delivered_image = (key, image)
        try:
            self.refresh_poster(key[0])
        finally:
            self._delivered_image = None
        if self.poster_ready:
            self.poster_ready_changed.emit()

    @staticmethod
    def _usable_cover(path):
        """Treat a disappearing/unreadable cover as missing, not a GUI exception."""
        try:
            return bool(path) and os.stat(path).st_size > 500
        except OSError:
            return False

    def _get_cover_path(self):
        if "_cached_cover_path" in self.project and self.project["_cached_cover_path"]:
            cached = self.project["_cached_cover_path"]
            if self._usable_cover(cached):
                return cached

        p_path = self.project.get("path", "")
        # 1. Check workspace root candidates
        if p_path and os.path.exists(p_path):
            candidates = [
                "thub_cover.jpg", "thub_cover.png", "cover.jpg", "cover.png",
                "cover_landscape_616x353.jpg", "header.jpg", "header.png",
                "poster.jpg", "poster.png", "banner.jpg", "banner.png"
            ]
            for c in candidates:
                full = os.path.join(p_path, c)
                if self._usable_cover(full):
                    self.project["_cached_cover_path"] = full
                    return full

            # 2. Check 07_Image_Resources/Official_Art/
            art_dir = os.path.join(p_path, "07_Image_Resources", "Official_Art")
            if os.path.exists(art_dir):
                art_candidates = [
                    "cover_landscape_616x353.jpg", "cover_header_460x215.jpg",
                    "banner_hero_1920x620.jpg", "cover_portrait_600x900.jpg",
                    "thub_cover.jpg", "cover.jpg"
                ]
                for ac in art_candidates:
                    full = os.path.join(art_dir, ac)
                    if self._usable_cover(full):
                        self.project["_cached_cover_path"] = full
                        return full

        # 3. Check central cache
        try:
            from core.steam_service import SteamService
            central = SteamService.get_central_cover_path(self.project.get("name", ""))
            if central and os.path.exists(central):
                self.project["_cached_cover_path"] = central
                return central
        except Exception:
            pass

        self.project["_cached_cover_path"] = None
        return None

    def _trigger_auto_fetch_cover(self):
        """Asynchronously requests cover download in background without blocking GUI."""
        if not ConfigManager().get("steam_auto_capsule", True):
            return
        game_name = self.project.get("name", "")
        workspace_path = self.project.get("path", "")
        if not game_name:
            return
        identity = (game_name, workspace_path)
        if self._cover_request_identity == identity:
            return
        self._cover_request_identity = identity

        from core.steam_service import SteamService

        card_ref = weakref.ref(self)
        def on_complete(cover_file):
            card = card_ref()
            if card is None or card._cover_request_identity != identity:
                return
            if cover_file and os.path.exists(cover_file):
                try:
                    card.cover_loaded.emit(cover_file)
                except RuntimeError:
                    # Download completion can race deletion of a filtered card.
                    pass

        SteamService.queue_auto_cover_fetch(game_name, workspace_path, on_complete=on_complete)

    def _on_cover_loaded(self, cover_file):
        """Qt Slot executed safely on main GUI thread when background download finishes."""
        try:
            if cover_file and os.path.exists(cover_file):
                self.project["_cached_cover_path"] = cover_file
                self.refresh_poster(cover_file)
        except (RuntimeError, Exception):
            pass

    def update_project(self, project):
        """Refreshes card content when project data updates or card is reused from pool."""
        self.project = project

        # Refresh engine badge
        saved_eng = self.project.get("engine") or self.project.get("engine_badge")
        if saved_eng:
            self.badge_text = EngineScanner.normalize_engine_name(saved_eng)
            self.badge_color = EngineScanner.get_engine_color(self.badge_text)
            if hasattr(self, "lbl_badge"):
                self.lbl_badge.setText(f" {self.badge_text} ")
                self.lbl_badge.setStyleSheet(f"""
                    background-color: rgba(16, 20, 30, 220);
                    color: {self.badge_color};
                    border: 1px solid {self.badge_color};
                    border-radius: 4px;
                    padding: 1px 5px;
                    font-size: {self.cfg_size['badge_font_size']}px;
                    font-weight: bold;
                """)
                self.lbl_badge.adjustSize()
                if self.card_size != "table":
                    right_margin = 6 if self.card_size == "compact" else 8
                    self.lbl_badge.move(self.POSTER_WIDTH - self.lbl_badge.width() - right_margin,
                                        self.lbl_badge.y())

        # Refresh status pill
        status_text, dot_color = self._get_status_info()
        if hasattr(self, "lbl_status"):
            self.lbl_status.setText(status_text)
        if hasattr(self, "lbl_dot"):
            self.lbl_dot.setStyleSheet(f"color: {dot_color}; font-size: {self.cfg_size['dot_font_size']}px;")

        # Refresh title if changed
        if hasattr(self, "lbl_title"):
            raw_title = self.project.get("name", "Unknown Game")
            max_chars = self.cfg_size["title_max_len"]
            display_title = raw_title if len(raw_title) <= max_chars else raw_title[:max_chars - 2] + "..."
            self.lbl_title.setText(display_title)
            self.lbl_title.setToolTip(raw_title)

        # Refresh storage size
        size_str = self.project.get("_storage_size_str", "")
        if hasattr(self, "lbl_size"):
            if size_str:
                self.lbl_size.setText(f"💾 {size_str}")
                self.lbl_size.show()
            else:
                self.lbl_size.hide()
        if hasattr(self, "lbl_table_size"):
            self.lbl_table_size.setText(size_str or "-")

        # Refresh poster
        cover = self._get_cover_path()
        if not cover:
            self._trigger_auto_fetch_cover()
        self.refresh_poster(cover)

    def _get_status_info(self):
        status = self.project.get("status", "In Progress")
        if status == "Completed":
            return _("เสร็จแล้ว (100%)"), "#22c55e"
        if status in ("Cancelled", "Canceled", "ยกเลิก"):
            return _("ยกเลิก"), "#ef4444"
        if status in ("On Hold", "Paused", "Shelved", "ดอง"):
            return _("ดองไว้ 🧊"), "#c084fc"

        progress = self.project.get("progress", {})
        pct = progress.get("percentage")
        if pct is not None:
            color = "#22c55e" if pct >= 100 else ("#38bdf8" if pct > 0 else "#f59e0b")
            label = _("เสร็จแล้ว (100%)") if pct >= 100 else f"{pct}%"
            return label, color

        if status == "Imported":
            return _("พร้อมใช้งาน (Ready)"), "#38bdf8"
        return _("กำลังแปล"), "#f59e0b"

    def _show_status_menu(self):
        try:
            menu = QMenu(self)
            menu.setStyleSheet("""
                QMenu {
                    background-color: #1e293b;
                    color: #f8fafc;
                    border: 1px solid #334155;
                    border-radius: 8px;
                    padding: 4px;
                }
                QMenu::item {
                    padding: 6px 16px;
                    border-radius: 4px;
                    font-size: 11px;
                }
                QMenu::item:selected {
                    background-color: #38bdf8;
                    color: #0f172a;
                    font-weight: bold;
                }
            """)

            curr = self.project.get("status", "In Progress")

            # 1. กำลังแปล (In Progress)
            act_prog = menu.addAction(_("🔄 กำลังแปล (In Progress)"))
            if curr == "In Progress":
                act_prog.setText(_("✓ 🔄 กำลังแปล (In Progress)"))
            act_prog.triggered.connect(lambda: QTimer.singleShot(0, lambda: self._set_project_status("In Progress")))

            # 2. ดองไว้ / พักงาน (On Hold)
            act_hold = menu.addAction(_("🧊 ดองไว้ / พักงาน (On Hold)"))
            if curr in ("On Hold", "Paused", "Shelved", "ดอง"):
                act_hold.setText(_("✓ 🧊 ดองไว้ / พักงาน (On Hold)"))
            act_hold.triggered.connect(lambda: QTimer.singleShot(0, lambda: self._set_project_status("On Hold")))

            # 3. เสร็จแล้ว (Completed)
            act_comp = menu.addAction(_("✅ เสร็จแล้ว (Completed)"))
            if curr == "Completed":
                act_comp.setText(_("✓ ✅ เสร็จแล้ว (Completed)"))
            act_comp.triggered.connect(lambda: QTimer.singleShot(0, lambda: self._set_project_status("Completed")))

            # 4. ยกเลิก (Cancelled)
            act_canc = menu.addAction(_("❌ ยกเลิก (Cancelled)"))
            if curr in ("Cancelled", "Canceled", "ยกเลิก"):
                act_canc.setText(_("✓ ❌ ยกเลิก (Cancelled)"))
            act_canc.triggered.connect(lambda: QTimer.singleShot(0, lambda: self._set_project_status("Cancelled")))

            pos = self.pill.mapToGlobal(QPoint(0, self.pill.height() + 2))
            menu.exec(pos)
        except Exception as e:
            import traceback; traceback.print_exc()

    def _set_project_status(self, new_status):
        try:
            self.project["status"] = new_status
            status_text, dot_color = self._get_status_info()
            if hasattr(self, "lbl_status"):
                self.lbl_status.setText(status_text)
            if hasattr(self, "lbl_dot"):
                self.lbl_dot.setStyleSheet(f"color: {dot_color}; font-size: 9px;")
            self.status_changed.emit(self.project, new_status)
        except Exception as e:
            import traceback; traceback.print_exc()

    # --- Mouse & Drag & Drop Handling ---
    def mouseDoubleClickEvent(self, event):
        try:
            if event.button() == Qt.MouseButton.LeftButton:
                self._on_tstudio()
                event.accept()
                return
        except Exception as e:
            import traceback; traceback.print_exc()
        super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event):
        try:
            if event.button() == Qt.MouseButton.LeftButton:
                self._drag_start_pos = event.pos()
                self.selected.emit(self.project)
            elif event.button() == Qt.MouseButton.RightButton:
                self._show_context_menu(event.globalPosition().toPoint())
                event.accept()
                return
        except Exception as e:
            import traceback; traceback.print_exc()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        try:
            self._drag_start_pos = None
        except Exception:
            pass
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        try:
            if event.buttons() & Qt.MouseButton.LeftButton and getattr(self, "_drag_start_pos", None) is not None:
                dist = (event.pos() - self._drag_start_pos).manhattanLength()
                drag_threshold = max(24, QApplication.startDragDistance() * 2 if QApplication.instance() else 24)
                if dist >= drag_threshold:
                    self._start_drag()
                    return
        except Exception as e:
            import traceback; traceback.print_exc()
        super().mouseMoveEvent(event)

    def _start_drag(self):
        try:
            drag = QDrag(self)
            mime = QMimeData()
            proj_name = self.project.get("name", "")
            mime.setData("application/x-thub-card-name", proj_name.encode("utf-8"))
            drag.setMimeData(mime)

            pix = self.grab()
            thumb = QPixmap(pix.size())
            thumb.fill(Qt.GlobalColor.transparent)
            p = QPainter(thumb)
            p.setOpacity(0.75)
            p.drawPixmap(0, 0, pix)
            p.end()

            drag.setPixmap(thumb)
            hotspot = getattr(self, "_drag_start_pos", None) or QPoint(20, 20)
            drag.setHotSpot(hotspot)
            self._drag_start_pos = None
            drag.exec(Qt.DropAction.MoveAction)
        except Exception as e:
            import traceback; traceback.print_exc()
        finally:
            self._drag_start_pos = None

    def _on_more_clicked(self):
        pos = self.btn_more.mapToGlobal(QPoint(0, self.btn_more.height() + 2))
        self._show_context_menu(pos)

    def _show_context_menu(self, global_pos):
        try:
            menu = QMenu(self)

            act_tstudio = menu.addAction(_("🚀 เปิดโปรเจกต์ด้วย TStudio"))
            act_tstudio.triggered.connect(lambda: QTimer.singleShot(0, self._on_tstudio))

            act_ai = menu.addAction(_("🤖 ผู้ช่วย AI Helper Copilot"))
            act_ai.triggered.connect(lambda: QTimer.singleShot(0, self._on_ai))

            act_folder = menu.addAction(_("📁 เปิดโฟลเดอร์โปรเจกต์ (Workspace)"))
            act_folder.triggered.connect(lambda: QTimer.singleShot(0, self._on_folder))

            # Check if project has an associated Bible or matches one
            bible_path = self.project.get("bible_path")
            bible_title = self.project.get("bible_title")
            engine_name = self.project.get("engine", "")

            if not bible_path or not os.path.exists(bible_path):
                try:
                    from core.knowledge_service import KnowledgeService
                    b_match = KnowledgeService.get_instance().find_exact_bible_by_title(
                        self.project.get("name", ""),
                        engine_name=engine_name
                    )
                    if b_match:
                        bible_path = b_match.get("bible_path")
                        bible_title = b_match.get("bible_title")
                        engine_name = b_match.get("engine_name", engine_name)
                except Exception:
                    pass

            if bible_path and os.path.exists(bible_path):
                act_bible = menu.addAction(_("📖 เปิดอ่านคัมภีร์ม็อดแปลไทย (Modding Bible)"))
                act_bible.triggered.connect(lambda: QTimer.singleShot(0, lambda: self._open_bible(bible_path, bible_title, engine_name)))

            act_adopt = menu.addAction(_("🔄 สานต่องาน & จัดโครงสร้าง THub ด้วย AI Helper..."))
            act_adopt.triggered.connect(lambda: QTimer.singleShot(0, lambda: self.adopt_requested.emit(self.project)))

            act_move = menu.addAction(_("🚚 ย้ายโปรเจกต์ไปยังไดรฟ์อื่น..."))
            act_move.triggered.connect(lambda: QTimer.singleShot(0, lambda: self.move_requested.emit(self.project)))

            menu.addSeparator()

            act_settings = menu.addAction(_("✏️ แก้ไขข้อมูลโปรเจกต์..."))
            act_settings.triggered.connect(lambda: QTimer.singleShot(0, lambda: self.settings_requested.emit(self.project)))

            act_cover = menu.addAction(_("🖼️ เปลี่ยนภาพหน้าปก (Cover Image)..."))
            act_cover.triggered.connect(lambda: QTimer.singleShot(0, lambda: self.cover_edit_requested.emit(self.project)))

            act_engine = menu.addAction(_("⚙️ ตั้งค่า Engine และโครงสร้างเกม..."))
            act_engine.triggered.connect(lambda: QTimer.singleShot(0, lambda: self.engine_edit_requested.emit(self.project)))

            menu_status = menu.addMenu(_("📌 เปลี่ยนสถานะโปรเจกต์ (Status)"))
            curr_status = self.project.get("status", "In Progress")

            act_s_prog = menu_status.addAction(_("🔄 กำลังแปล (In Progress)"))
            if curr_status == "In Progress":
                act_s_prog.setText(_("✓ 🔄 กำลังแปล (In Progress)"))
            act_s_prog.triggered.connect(lambda: QTimer.singleShot(0, lambda: self._set_project_status("In Progress")))

            act_s_comp = menu_status.addAction(_("✅ เสร็จแล้ว (Completed)"))
            if curr_status == "Completed":
                act_s_comp.setText(_("✓ ✅ เสร็จแล้ว (Completed)"))
            act_s_comp.triggered.connect(lambda: QTimer.singleShot(0, lambda: self._set_project_status("Completed")))

            act_s_canc = menu_status.addAction(_("❌ ยกเลิก (Cancelled)"))
            if curr_status in ("Cancelled", "Canceled", "ยกเลิก"):
                act_s_canc.setText(_("✓ ❌ ยกเลิก (Cancelled)"))
            act_s_canc.triggered.connect(lambda: QTimer.singleShot(0, lambda: self._set_project_status("Cancelled")))

            act_s_hold = menu_status.addAction(_("🧊 ดอง / พักไว้ (On Hold)"))
            if curr_status in ("On Hold", "Paused", "Shelved", "ดอง"):
                act_s_hold.setText(_("✓ 🧊 ดอง / พักไว้ (On Hold)"))
            act_s_hold.triggered.connect(lambda: QTimer.singleShot(0, lambda: self._set_project_status("On Hold")))

            is_pinned = self.project.get("is_pinned", False)
            pin_label = _("📌 ยกเลิกปักหมุด") if is_pinned else _("📌 ปักหมุดไว้บนสุด")
            act_pin = menu.addAction(pin_label)
            act_pin.triggered.connect(lambda: QTimer.singleShot(0, lambda: self.pin_toggled.emit(self.project)))

            is_archived = self.project.get("is_archived", False)
            if is_archived:
                act_unarch = menu.addAction(_("📦 นำออกจากคลัง (Unarchive)"))
                act_unarch.triggered.connect(lambda: QTimer.singleShot(0, self._on_unarchive))
            else:
                act_arch = menu.addAction(_("📦 เก็บเข้าคลัง (Archive)..."))
                act_arch.triggered.connect(lambda: QTimer.singleShot(0, self._on_archive_with_dialog))

                menu_arch = menu.addMenu(_("    ↳ ⚡ เลือกสถานะเข้าคลังทันที"))
                act_arch_comp = menu_arch.addAction(_("✅ เสร็จแล้ว (Completed)"))
                act_arch_comp.triggered.connect(lambda: QTimer.singleShot(0, lambda: self._on_archive_with_status("Completed")))

                act_arch_canc = menu_arch.addAction(_("❌ ยกเลิก (Cancelled)"))
                act_arch_canc.triggered.connect(lambda: QTimer.singleShot(0, lambda: self._on_archive_with_status("Cancelled")))

                act_arch_hold = menu_arch.addAction(_("🧊 ดอง (On Hold)"))
                act_arch_hold.triggered.connect(lambda: QTimer.singleShot(0, lambda: self._on_archive_with_status("On Hold")))

            menu.addSeparator()

            act_del = menu.addAction(_("🗑️ ลบโปรเจกต์นี้..."))
            act_del.triggered.connect(lambda: QTimer.singleShot(0, lambda: self.delete_requested.emit(self.project)))

            menu.exec(global_pos)
        except Exception as e:
            import traceback; traceback.print_exc()

    def _on_archive_with_dialog(self):
        chosen = ArchiveSelectDialogQt.get_archive_choice(self, self.project.get("name", ""))
        if chosen:
            self._on_archive_with_status(chosen)

    def _on_archive_with_status(self, status):
        self.project["is_archived"] = True
        self.project["status"] = status
        self.project["archive_status"] = status
        self.archive_requested.emit(self.project, status)

    def _on_unarchive(self):
        self.project["is_archived"] = False
        self.project["archive_status"] = ""
        if self.project.get("status") in ("On Hold", "Cancelled", "ดอง", "ยกเลิก"):
            self.project["status"] = "In Progress"
        self.archive_requested.emit(self.project, "unarchive")

    def _on_tstudio(self):
        self.tstudio_clicked.emit(self.project)

    def _on_ai(self):
        self.ai_clicked.emit(self.project)

    def _on_folder(self):
        p_path = self.project.get("path")
        if p_path:
            ToolLauncher.open_folder(p_path)

    def _open_bible(self, path, title="", engine=""):
        dlg = BibleViewerDialogQt(self, bible_path=path, bible_title=title or self.project.get("name"), engine_name=engine)
        dlg.exec()
