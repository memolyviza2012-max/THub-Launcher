# -*- coding: utf-8 -*-
"""
tglyph_app.py — Main GUI Application for TGlyph (Thai PUA Font Studio)
=========================================================================

A PyQt6-based font studio for generating PUA-mapped Thai font atlases
for game engines.  Features a Catppuccin Mocha dark theme, three-panel
workspace, real-time text preview, atlas viewer, and per-glyph adjustment.

Usage::

    python tglyph_app.py

Requires: PyQt6, Pillow, numpy
"""

from __future__ import annotations

import sys
import os
import json
import copy
from pathlib import Path
from typing import Any, Optional

# Ensure UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------------------
# PyQt6 import guard
# ---------------------------------------------------------------------------
try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QSplitter, QTableView, QHeaderView, QLabel, QLineEdit, QPushButton,
        QComboBox, QSlider, QSpinBox, QToolBar, QStatusBar, QFileDialog,
        QDialog, QDialogButtonBox, QGraphicsView, QGraphicsScene,
        QGraphicsPixmapItem, QGroupBox, QFormLayout, QMessageBox,
        QAbstractItemView, QSizePolicy, QScrollArea,
    )
    from PyQt6.QtCore import (
        Qt, QAbstractTableModel, QModelIndex, QSortFilterProxyModel,
        QTimer, QSize, QRectF, pyqtSignal,
    )
    from PyQt6.QtGui import (
        QAction, QPixmap, QImage, QFont, QColor, QPainter, QIcon,
        QShortcut, QKeySequence, QWheelEvent, QPen,
    )
except ImportError:
    print("=" * 60)
    print("  ERROR: PyQt6 is not installed.")
    print("  Please install it with:  pip install PyQt6")
    print("=" * 60)
    sys.exit(1)

# ---------------------------------------------------------------------------
# Local module imports
# ---------------------------------------------------------------------------
_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))

from i18n import I18n, PRESET_TEXTS
import pua_engine
import font_renderer
import atlas_packer
import scr_parser
import dds_converter


# =========================================================================== #
#  Catppuccin Mocha Colour Palette                                             #
# =========================================================================== #

class Mocha:
    """Catppuccin Mocha colour constants."""
    BG       = "#1e1e2e"
    BG2      = "#181825"
    SURFACE  = "#313244"
    TEXT     = "#cdd6f4"
    SUBTLE   = "#a6adc8"
    BLUE     = "#89b4fa"
    GREEN    = "#a6e3a1"
    YELLOW   = "#f9e2af"
    RED      = "#f38ba8"
    HOVER    = "#585b70"
    OVERLAY  = "#45475a"


def build_stylesheet() -> str:
    """Return the full Catppuccin Mocha QSS stylesheet."""
    return f"""
    /* ── Global ──────────────────────────────────────────────── */
    QMainWindow, QDialog, QWidget {{
        background-color: {Mocha.BG};
        color: {Mocha.TEXT};
        font-family: "Segoe UI", "Noto Sans Thai", sans-serif;
        font-size: 13px;
    }}
    QToolBar {{
        background-color: {Mocha.BG2};
        border: none;
        spacing: 6px;
        padding: 4px;
    }}
    QToolBar QToolButton {{
        background-color: transparent;
        color: {Mocha.TEXT};
        border: 1px solid transparent;
        border-radius: 4px;
        padding: 5px 10px;
        font-size: 13px;
    }}
    QToolBar QToolButton:hover {{
        background-color: {Mocha.HOVER};
        border: 1px solid {Mocha.OVERLAY};
    }}
    QStatusBar {{
        background-color: {Mocha.BG2};
        color: {Mocha.SUBTLE};
        font-size: 12px;
    }}
    /* ── Splitter ─────────────────────────────────────────────── */
    QSplitter::handle {{
        background-color: {Mocha.SURFACE};
        width: 3px;
    }}
    QSplitter::handle:hover {{
        background-color: {Mocha.BLUE};
    }}
    /* ── Inputs ───────────────────────────────────────────────── */
    QLineEdit, QSpinBox, QComboBox {{
        background-color: {Mocha.SURFACE};
        color: {Mocha.TEXT};
        border: 1px solid {Mocha.OVERLAY};
        border-radius: 4px;
        padding: 4px 8px;
    }}
    QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
        border: 1px solid {Mocha.BLUE};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 20px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {Mocha.SURFACE};
        color: {Mocha.TEXT};
        selection-background-color: {Mocha.HOVER};
        border: 1px solid {Mocha.OVERLAY};
    }}
    /* ── Push buttons ─────────────────────────────────────────── */
    QPushButton {{
        background-color: {Mocha.SURFACE};
        color: {Mocha.TEXT};
        border: 1px solid {Mocha.OVERLAY};
        border-radius: 4px;
        padding: 5px 14px;
    }}
    QPushButton:hover {{
        background-color: {Mocha.HOVER};
        border: 1px solid {Mocha.BLUE};
    }}
    QPushButton:pressed {{
        background-color: {Mocha.OVERLAY};
    }}
    /* ── Tables ───────────────────────────────────────────────── */
    QTableView {{
        background-color: {Mocha.BG2};
        color: {Mocha.TEXT};
        gridline-color: {Mocha.SURFACE};
        border: 1px solid {Mocha.SURFACE};
        selection-background-color: {Mocha.SURFACE};
        selection-color: {Mocha.BLUE};
    }}
    QHeaderView::section {{
        background-color: {Mocha.SURFACE};
        color: {Mocha.SUBTLE};
        border: none;
        border-bottom: 1px solid {Mocha.OVERLAY};
        padding: 4px 8px;
        font-weight: bold;
    }}
    /* ── Sliders ──────────────────────────────────────────────── */
    QSlider::groove:horizontal {{
        height: 6px;
        background: {Mocha.SURFACE};
        border-radius: 3px;
    }}
    QSlider::handle:horizontal {{
        background: {Mocha.BLUE};
        width: 14px;
        height: 14px;
        margin: -4px 0;
        border-radius: 7px;
    }}
    QSlider::handle:horizontal:hover {{
        background: {Mocha.GREEN};
    }}
    /* ── Group boxes ──────────────────────────────────────────── */
    QGroupBox {{
        border: 1px solid {Mocha.SURFACE};
        border-radius: 6px;
        margin-top: 12px;
        padding-top: 14px;
        font-weight: bold;
        color: {Mocha.SUBTLE};
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 4px;
    }}
    /* ── Scroll area ─────────────────────────────────────────── */
    QScrollArea {{
        border: none;
    }}
    QScrollBar:vertical {{
        background: {Mocha.BG2};
        width: 10px;
        border-radius: 5px;
    }}
    QScrollBar::handle:vertical {{
        background: {Mocha.SURFACE};
        min-height: 30px;
        border-radius: 5px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {Mocha.HOVER};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    QScrollBar:horizontal {{
        background: {Mocha.BG2};
        height: 10px;
        border-radius: 5px;
    }}
    QScrollBar::handle:horizontal {{
        background: {Mocha.SURFACE};
        min-width: 30px;
        border-radius: 5px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background: {Mocha.HOVER};
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0;
    }}
    /* ── Graphics view ───────────────────────────────────────── */
    QGraphicsView {{
        background-color: {Mocha.BG2};
        border: 1px solid {Mocha.SURFACE};
    }}
    /* ── Labels ───────────────────────────────────────────────── */
    QLabel {{
        color: {Mocha.TEXT};
    }}
    """


# =========================================================================== #
#  Configuration Helper                                                        #
# =========================================================================== #

import os
_CONFIG_PATH = Path(os.environ.get("APPDATA", str(_SCRIPT_DIR))) / "TSuite" / "TGlyph" / "config.json"
os.makedirs(_CONFIG_PATH.parent, exist_ok=True)


def load_config() -> dict[str, Any]:
    """Load application config; return defaults if file missing."""
    defaults: dict[str, Any] = {
        "default_language": "en",
        "window_width": 1600,
        "window_height": 900,
        "default_font_size": 42,
        "supersampling_factor": 3,
        "atlas_width": 4096,
        "atlas_height": 4096,
        "atlas_padding": 2,
        "quality_threshold_ok": 85,
        "quality_threshold_warn": 70,
        "max_undo_history": 50,
        "last_font_path": "",
        "last_project_path": "",
        "last_export_path": "",
        "default_export_profile": "dying_light_2",
    }
    try:
        with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        defaults.update(data)
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return defaults


def save_config(cfg: dict[str, Any]) -> None:
    """Persist the config dict to config.json."""
    try:
        with open(_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4, ensure_ascii=False)
    except OSError as exc:
        print(f"[WARN] Could not save config: {exc}")


# =========================================================================== #
#  Thai Character Category Helpers                                             #
# =========================================================================== #

# Thai Unicode sub-ranges
_CONSONANTS = set(range(0x0E01, 0x0E2F))
_VOWELS_ABOVE = {0x0E31} | set(range(0x0E34, 0x0E38))
_VOWELS_BELOW = set(range(0x0E38, 0x0E3B))
_TONE_MARKS = set(range(0x0E48, 0x0E4D))
_SYMBOLS = set(range(0x0E2F, 0x0E34)) | set(range(0x0E3F, 0x0E48)) | set(range(0x0E4F, 0x0E60))
_PUA_RANGE = set(range(0xE000, 0xF900))


def classify_char(ch: str) -> str:
    """Return the category key for a character."""
    cp = ord(ch) if len(ch) == 1 else 0
    if cp in _CONSONANTS:
        return "consonant"
    if cp in _VOWELS_ABOVE:
        return "vowel_above"
    if cp in _VOWELS_BELOW:
        return "vowel_below"
    if cp in _TONE_MARKS:
        return "tone_mark"
    if cp in _SYMBOLS:
        return "symbol"
    if cp in _PUA_RANGE:
        return "pua"
    if 0x0030 <= cp <= 0x0039 or 0x0E50 <= cp <= 0x0E59:
        return "number"
    if 0x0041 <= cp <= 0x007A:
        return "latin"
    return "other"


def get_full_charset() -> list[dict[str, Any]]:
    """Build a list of ALL characters for the glyph table.

    Includes: ASCII printable, Latin Extended, Thai, Thai digits.
    Returns a list of dicts: {char, codepoint, category, fill_pct, status}
    """
    chars: list[dict[str, Any]] = []

    # ASCII printable (U+0020–U+007E): space, punctuation, digits, A-Z, a-z
    for cp in range(0x0020, 0x007F):
        ch = chr(cp)
        chars.append({
            "char": ch,
            "codepoint": cp,
            "category": classify_char(ch),
            "fill_pct": 0.0,
            "status": "ok",
        })

    # Latin Extended-A commonly used (U+00C0–U+017E): À Á Â ... Ž ž
    for cp in range(0x00C0, 0x017F):
        ch = chr(cp)
        chars.append({
            "char": ch,
            "codepoint": cp,
            "category": "latin",
            "fill_pct": 0.0,
            "status": "ok",
        })

    # Thai consonants (U+0E01–U+0E2E)
    for cp in range(0x0E01, 0x0E2F):
        ch = chr(cp)
        chars.append({
            "char": ch,
            "codepoint": cp,
            "category": classify_char(ch),
            "fill_pct": 0.0,
            "status": "ok",
        })

    # Thai vowels, tone marks, symbols, digits (U+0E2F–U+0E5B)
    for cp in range(0x0E2F, 0x0E5C):
        ch = chr(cp)
        chars.append({
            "char": ch,
            "codepoint": cp,
            "category": classify_char(ch),
            "fill_pct": 0.0,
            "status": "ok",
        })

    return chars


# =========================================================================== #
#  Glyph Table Model                                                           #
# =========================================================================== #

_COL_CHAR     = 0
_COL_UNICODE  = 1
_COL_CATEGORY = 2
_COL_FILL     = 3
_COL_STATUS   = 4
_NUM_COLS     = 5


class GlyphTableModel(QAbstractTableModel):
    """Table model holding glyph data for QTableView."""

    def __init__(self, i18n: I18n, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._i18n = i18n
        self._glyphs: list[dict[str, Any]] = []

    # -- Public API ---------------------------------------------------------

    def set_glyphs(self, glyphs: list[dict[str, Any]]) -> None:
        """Replace all glyph data and refresh the view."""
        self.beginResetModel()
        self._glyphs = glyphs
        self.endResetModel()

    def glyph_at(self, row: int) -> Optional[dict[str, Any]]:
        """Return glyph dict at *row*, or None."""
        if 0 <= row < len(self._glyphs):
            return self._glyphs[row]
        return None

    def update_glyph(self, row: int, data: dict[str, Any]) -> None:
        """Update specific fields for the glyph at *row*."""
        if 0 <= row < len(self._glyphs):
            self._glyphs[row].update(data)
            left = self.index(row, 0)
            right = self.index(row, _NUM_COLS - 1)
            self.dataChanged.emit(left, right)

    @property
    def glyphs(self) -> list[dict[str, Any]]:
        return self._glyphs

    # -- QAbstractTableModel overrides --------------------------------------

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._glyphs)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return _NUM_COLS

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None
        g = self._glyphs[index.row()]
        col = index.column()

        if role == Qt.ItemDataRole.DisplayRole:
            if col == _COL_CHAR:
                return g["char"]
            if col == _COL_UNICODE:
                return f'U+{g["codepoint"]:04X}'
            if col == _COL_CATEGORY:
                cat_key = f'cat_{g["category"]}'
                return self._i18n.t(cat_key)
            if col == _COL_FILL:
                return f'{g["fill_pct"]:.0f}%'
            if col == _COL_STATUS:
                s = g["status"]
                if s == "ok":
                    return self._i18n.t("status_ok")
                elif s == "warn":
                    return self._i18n.t("status_warn")
                return self._i18n.t("status_error")

        if role == Qt.ItemDataRole.TextAlignmentRole:
            if col in (_COL_FILL, _COL_STATUS):
                return Qt.AlignmentFlag.AlignCenter
            return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter

        if role == Qt.ItemDataRole.ForegroundRole:
            if col == _COL_STATUS:
                s = g["status"]
                if s == "ok":
                    return QColor(Mocha.GREEN)
                elif s == "warn":
                    return QColor(Mocha.YELLOW)
                return QColor(Mocha.RED)
            if col == _COL_CHAR:
                return QColor(Mocha.BLUE)

        # Store category in UserRole for proxy filter
        if role == Qt.ItemDataRole.UserRole:
            return g["category"]

        return None

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            keys = ["col_char", "col_unicode", "col_category", "col_fill", "col_status"]
            if 0 <= section < len(keys):
                return self._i18n.t(keys[section])
        return None


# =========================================================================== #
#  Glyph Filter Proxy                                                          #
# =========================================================================== #

class GlyphFilterProxy(QSortFilterProxyModel):
    """Proxy model with category + text search filtering."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._category_filter: str = "all"
        self._search_text: str = ""

    def set_category_filter(self, category: str) -> None:
        self._category_filter = category
        self.invalidateFilter()

    def set_search_text(self, text: str) -> None:
        self._search_text = text.strip().lower()
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        model = self.sourceModel()
        if model is None:
            return True

        # Category filter
        cat = model.data(model.index(source_row, _COL_CATEGORY), Qt.ItemDataRole.UserRole)
        if self._category_filter != "all":
            if self._category_filter == "problems":
                status_idx = model.index(source_row, _COL_STATUS)
                status_text = model.data(status_idx, Qt.ItemDataRole.UserRole)
                # Use the glyph dict directly
                glyph = model.glyph_at(source_row)
                if glyph and glyph.get("status") == "ok":
                    return False
            elif cat != self._category_filter:
                return False

        # Text search
        if self._search_text:
            char_val = model.data(model.index(source_row, _COL_CHAR), Qt.ItemDataRole.DisplayRole) or ""
            uni_val = model.data(model.index(source_row, _COL_UNICODE), Qt.ItemDataRole.DisplayRole) or ""
            haystack = (char_val + " " + uni_val).lower()
            if self._search_text not in haystack:
                return False

        return True


# =========================================================================== #
#  Zoomable Graphics View (Atlas Viewer)                                       #
# =========================================================================== #

class ZoomableGraphicsView(QGraphicsView):
    """QGraphicsView with Ctrl+Scroll zoom support and manual panning."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._zoom_factor: float = 1.0
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        
        self._is_panning = False
        self._pan_start = None

    def mousePressEvent(self, event) -> None:
        if event.button() in (Qt.MouseButton.LeftButton, Qt.MouseButton.MiddleButton):
            self._is_panning = True
            self._pan_start = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self._is_panning and self._pan_start is not None:
            delta = event.pos() - self._pan_start
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - int(delta.x()))
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - int(delta.y()))
            self._pan_start = event.pos()
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() in (Qt.MouseButton.LeftButton, Qt.MouseButton.MiddleButton):
            self._is_panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def wheelEvent(self, event: QWheelEvent) -> None:  # type: ignore[override]
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            angle = event.angleDelta().y()
            factor = 1.15 if angle > 0 else 1 / 1.15
            self._zoom_factor *= factor
            self._zoom_factor = max(0.1, min(self._zoom_factor, 20.0))
            self.setTransform(
                self.transform().scale(factor, factor)  # type: ignore[arg-type]
            )
        else:
            super().wheelEvent(event)

    def zoom_fit(self) -> None:
        """Fit the entire scene into the viewport."""
        self.fitInView(self.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self._zoom_factor = 1.0


# =========================================================================== #
#  Export Dialog                                                                #
# =========================================================================== #

class ExportDialog(QDialog):
    """Dialog for choosing export profile and output folder."""

    def __init__(self, i18n: I18n, config: dict, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._i18n = i18n
        self._config = config
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setWindowTitle(self._i18n.t("export_title"))
        self.setMinimumSize(480, 220)
        layout = QVBoxLayout(self)

        form = QFormLayout()

        # Profile combo
        self.profile_combo = QComboBox()
        self.profile_combo.addItem(self._i18n.t("profile_dl2"), "dying_light_2")
        self.profile_combo.addItem(self._i18n.t("profile_bmfont"), "bmfont")
        self.profile_combo.addItem(self._i18n.t("profile_json"), "json_atlas")
        form.addRow(self._i18n.t("export_profile") + ":", self.profile_combo)

        # Output path
        path_row = QHBoxLayout()
        self.path_edit = QLineEdit(self._config.get("last_export_path", ""))
        self.path_edit.setMinimumWidth(280)
        btn_browse = QPushButton(self._i18n.t("export_browse"))
        btn_browse.clicked.connect(self._browse_output)
        path_row.addWidget(self.path_edit)
        path_row.addWidget(btn_browse)
        form.addRow(self._i18n.t("export_path") + ":", path_row)

        # Output path (removed base image)

        layout.addLayout(form)
        layout.addSpacing(12)

        # Buttons
        btn_box = QHBoxLayout()
        btn_box.addStretch()
        self.btn_export = QPushButton(self._i18n.t("export_start"))
        self.btn_export.setStyleSheet(
            f"background-color: {Mocha.BLUE}; color: {Mocha.BG}; font-weight: bold;"
        )
        self.btn_export.clicked.connect(self.accept)
        btn_cancel = QPushButton(self._i18n.t("export_cancel"))
        btn_cancel.clicked.connect(self.reject)
        btn_box.addWidget(btn_cancel)
        btn_box.addWidget(self.btn_export)
        layout.addLayout(btn_box)

    def _browse_output(self) -> None:
        folder = QFileDialog.getExistingDirectory(
            self, self._i18n.t("export_path"), self.path_edit.text()
        )
        if folder:
            self.path_edit.setText(folder)

    def get_profile(self) -> str:
        return self.profile_combo.currentData() or "dying_light_2"

    def get_output_path(self) -> str:
        return self.path_edit.text()


# =========================================================================== #
#  Startup Dialog                                                              #
# =========================================================================== #

class StartupDialog(QDialog):
    """Setup dialog shown on launch — lets the user pick a font file,
    optional base image, and cell-size preset before opening the main window."""

    _PRESET_SIZES: list[tuple[str, int]] = [
        ("Auto (detect from base image)", 0),
        ("16 × 16 px", 16),
        ("24 × 24 px", 24),
        ("32 × 32 px", 32),
        ("48 × 48 px", 48),
        ("64 × 64 px", 64),
        ("Custom...", -1),
    ]

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("TGlyph — Setup")
        self.setMinimumSize(520, 380)
        self.setStyleSheet(
            f"QDialog {{ background-color: {Mocha.BG}; color: {Mocha.TEXT}; }}"
        )
        self._setup_ui()

    # ── UI construction ───────────────────────────────────────────────

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # Title label
        title = QLabel("TGlyph — Setup")
        title.setStyleSheet(
            f"font-size: 18px; font-weight: bold; color: {Mocha.BLUE};"
        )
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        layout.addSpacing(6)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        form.setSpacing(10)

        # ── Font File row ─────────────────────────────────────────────
        font_row = QHBoxLayout()
        self._font_edit = QLineEdit()
        self._font_edit.setReadOnly(True)
        self._font_edit.setPlaceholderText("Select a .ttf or .otf font file…")
        self._font_edit.setMinimumWidth(300)
        btn_font = QPushButton("Browse")
        btn_font.clicked.connect(self._browse_font)
        font_row.addWidget(self._font_edit)
        font_row.addWidget(btn_font)
        form.addRow("Font File:", font_row)

        # ── Base Image row (Optional) ─────────────────────────────────
        base_row = QHBoxLayout()
        self._base_edit = QLineEdit()
        self._base_edit.setReadOnly(True)
        self._base_edit.setPlaceholderText("Leave empty for blank atlas")
        self._base_edit.setMinimumWidth(300)
        btn_base = QPushButton("Browse")
        btn_base.clicked.connect(self._browse_base_image)
        base_row.addWidget(self._base_edit)
        base_row.addWidget(btn_base)
        form.addRow("Base Image (Optional):", base_row)

        # ── Cell Size Preset row ──────────────────────────────────────
        self._size_combo = QComboBox()
        for label, value in self._PRESET_SIZES:
            self._size_combo.addItem(label, value)
        self._size_combo.setCurrentIndex(0)
        self._size_combo.currentIndexChanged.connect(self._on_preset_changed)
        form.addRow("Cell Size Preset:", self._size_combo)

        # ── Custom Size row (only active for "Custom...") ─────────────
        self._custom_spin = QSpinBox()
        self._custom_spin.setRange(8, 256)
        self._custom_spin.setValue(32)
        self._custom_spin.setSuffix(" px")
        self._custom_spin.setEnabled(False)
        form.addRow("Custom Cell Size:", self._custom_spin)

        layout.addLayout(form)
        layout.addStretch()

        # ── Start button ──────────────────────────────────────────────
        self._btn_start = QPushButton("▶  Start")
        self._btn_start.setMinimumHeight(40)
        self._btn_start.setStyleSheet(
            f"QPushButton {{"
            f"  background-color: {Mocha.BLUE}; color: {Mocha.BG};"
            f"  font-size: 15px; font-weight: bold; border-radius: 6px;"
            f"}}"
            f"QPushButton:hover {{ background-color: {Mocha.GREEN}; }}"
        )
        self._btn_start.clicked.connect(self._on_start)
        layout.addWidget(self._btn_start)

    # ── Slots ─────────────────────────────────────────────────────────

    def _browse_font(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Font File", "",
            "Font Files (*.ttf *.otf);;All Files (*)",
        )
        if path:
            self._font_edit.setText(path)

    def _browse_base_image(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Base Image", "",
            "PNG Images (*.png);;All Files (*)",
        )
        if path:
            self._base_edit.setText(path)

    def _on_preset_changed(self, index: int) -> None:
        value = self._size_combo.currentData()
        self._custom_spin.setEnabled(value == -1)

    def _on_start(self) -> None:
        if not self._font_edit.text().strip():
            QMessageBox.warning(
                self, "Font Required",
                "Please select a font file before starting.",
            )
            return
        font_path = self._font_edit.text().strip()
        if not os.path.isfile(font_path):
            QMessageBox.warning(
                self, "File Not Found",
                f"The selected font file does not exist:\n{font_path}",
            )
            return
        self.accept()

    # ── Public getters ────────────────────────────────────────────────

    def get_font_path(self) -> str:
        """Return the selected font file path."""
        return self._font_edit.text().strip()

    def get_base_image_path(self) -> str:
        """Return the selected base-image path, or empty string."""
        return self._base_edit.text().strip()

    def get_cell_size(self) -> int:
        """Return the chosen cell size (0 = auto, >0 = pixels)."""
        value = self._size_combo.currentData()
        if value == -1:       # Custom
            return self._custom_spin.value()
        return value if value else 0


# =========================================================================== #
#  Main Window                                                                 #
# =========================================================================== #

class TGlyphApp(QMainWindow):
    """Main application window for TGlyph."""

    def __init__(
        self,
        font_path: Optional[str] = None,
        base_image_path: Optional[str] = None,
        cell_size: int = 0,
    ) -> None:
        super().__init__()
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('flagship.tglyph.app.1.0')
        except:
            pass

        # -- State ----------------------------------------------------------
        self._config = load_config()
        self._i18n = I18n(self._config.get("default_language", "en"))
        self._font_path: Optional[str] = font_path
        self._font_name: str = ""
        self._adjustments: dict[int, dict[str, Any]] = {}   # cp → {x_off, y_off, scale, ...}
        self._undo_stack: list[dict[int, dict[str, Any]]] = []
        self._redo_stack: list[dict[int, dict[str, Any]]] = []
        self._max_undo = int(self._config.get("max_undo_history", 50))
        self._selected_cp: Optional[int] = None
        self._glyph_images: dict[str, Any] = {}     # char → np.ndarray
        self._glyph_metrics: dict[str, dict] = {}   # char → metrics dict
        # Glyph preview cache (avoid re-rendering on every slider tick)
        self._cached_preview_cp: Optional[int] = None
        self._cached_preview_scale: int = 100
        self._cached_preview_qimg: Optional[QImage] = None

        # -- Base image & cell size from startup dialog ---------------------
        self._base_image_path: Optional[str] = base_image_path
        self._base_image_arr: Optional[object] = None  # loaded base image (np.ndarray)
        self._cell_size: int = cell_size

        if base_image_path and os.path.isfile(base_image_path):
            try:
                from PIL import Image
                import numpy as np
                with Image.open(base_image_path) as img:
                    self._base_image_arr = np.array(img.convert('RGBA'))
            except Exception as exc:
                print(f"[WARN] Could not load base image: {exc}")

        # -- Window setup ---------------------------------------------------
        self.setWindowTitle(self._i18n.t("app_title"))
        w = int(self._config.get("window_width", 1600))
        h = int(self._config.get("window_height", 900))
        self.resize(w, h)
        
        logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "assets", "TGlyph.png"))
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))

        # -- Build UI -------------------------------------------------------
        self._build_toolbar()
        self._build_central_widget()
        self._build_status_bar()
        self._setup_shortcuts()
        self._setup_timers()

        # -- Load initial state ---------------------------------------------
        self._populate_empty_table()
        self._update_status_bar()

        # If a font path was provided by the startup dialog, load it now
        if self._font_path and os.path.isfile(self._font_path):
            self._font_name = Path(self._font_path).stem
            self._config["last_font_path"] = str(Path(self._font_path).parent)
            save_config(self._config)
            self._populate_glyph_table_from_font(self._font_path)
            self._update_status_bar()
            msg = self._i18n.t("msg_font_loaded").format(self._font_name)
            self.status_label.setText(msg)

    # =================================================================== #
    #  Toolbar                                                              #
    # =================================================================== #

    def _build_toolbar(self) -> None:
        tb = QToolBar("Main Toolbar")
        tb.setMovable(False)
        tb.setIconSize(QSize(20, 20))
        self.addToolBar(tb)

        self.act_load_font = QAction(self._i18n.t("load_font"), self)
        self.act_load_font.triggered.connect(self._on_load_font)
        tb.addAction(self.act_load_font)

        tb.addSeparator()

        self.act_load_project = QAction(self._i18n.t("load_project"), self)
        self.act_load_project.triggered.connect(self._on_load_project)
        tb.addAction(self.act_load_project)

        self.act_save_project = QAction(self._i18n.t("save_project"), self)
        self.act_save_project.triggered.connect(self._on_save_project)
        tb.addAction(self.act_save_project)

        tb.addSeparator()

        self.act_export = QAction(self._i18n.t("export"), self)
        self.act_export.triggered.connect(self._on_export)
        tb.addAction(self.act_export)

        tb.addSeparator()

        self.act_lang = QAction(self._i18n.t("language"), self)
        self.act_lang.triggered.connect(self._on_toggle_language)
        tb.addAction(self.act_lang)

    # =================================================================== #
    #  Central Widget — Three-Panel Splitter                                #
    # =================================================================== #

    def _build_central_widget(self) -> None:
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(3)

        # LEFT panel (25%) — Glyph Table
        left = self._build_left_panel()
        splitter.addWidget(left)

        # CENTER panel (50%) — Preview + Atlas
        center = self._build_center_panel()
        splitter.addWidget(center)

        # RIGHT panel (25%) — Adjust Panel
        right = self._build_right_panel()
        splitter.addWidget(right)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        splitter.setStretchFactor(2, 1)
        splitter.setSizes([400, 800, 400])

        self.setCentralWidget(splitter)

    # ── LEFT: Glyph Table ──────────────────────────────────────────────

    def _build_left_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Title
        self.lbl_glyph_table = QLabel(self._i18n.t("glyph_table"))
        self.lbl_glyph_table.setStyleSheet(
            f"font-size: 14px; font-weight: bold; color: {Mocha.BLUE}; padding: 2px;"
        )
        layout.addWidget(self.lbl_glyph_table)

        # Filter combo
        self.filter_combo = QComboBox()
        self._populate_filter_combo()
        self.filter_combo.currentIndexChanged.connect(self._on_filter_changed)
        layout.addWidget(self.filter_combo)

        # Search bar
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText(self._i18n.t("search_placeholder"))
        self.search_edit.textChanged.connect(self._on_search_text_changed)
        layout.addWidget(self.search_edit)

        # Table model + proxy
        self._glyph_model = GlyphTableModel(self._i18n)
        self._glyph_proxy = GlyphFilterProxy()
        self._glyph_proxy.setSourceModel(self._glyph_model)

        # Table view
        self.glyph_table = QTableView()
        self.glyph_table.setModel(self._glyph_proxy)
        self.glyph_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.glyph_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.glyph_table.setAlternatingRowColors(False)
        self.glyph_table.verticalHeader().setVisible(False)
        self.glyph_table.horizontalHeader().setStretchLastSection(True)
        self.glyph_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self.glyph_table.setShowGrid(False)
        self.glyph_table.clicked.connect(self._on_glyph_selected)
        layout.addWidget(self.glyph_table, 1)

        return panel

    def _populate_filter_combo(self) -> None:
        """Fill the filter combo with category options."""
        self.filter_combo.clear()
        filters = [
            ("all",         "filter_all"),
            ("latin",       "filter_latin"),
            ("consonant",   "filter_consonants"),
            ("vowel_above", "filter_vowels_above"),
            ("vowel_below", "filter_vowels_below"),
            ("tone_mark",   "filter_tone_marks"),
            ("symbol",      "filter_symbols"),
            ("number",      "filter_numbers"),
            ("pua",         "filter_pua"),
            ("problems",    "filter_problems"),
        ]
        for data_key, i18n_key in filters:
            self.filter_combo.addItem(self._i18n.t(i18n_key), data_key)

    # ── CENTER: Preview + Atlas ────────────────────────────────────────

    def _build_center_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        vsplitter = QSplitter(Qt.Orientation.Vertical)

        # -- TOP: Text preview -------
        preview_widget = QWidget()
        pv_layout = QVBoxLayout(preview_widget)
        pv_layout.setContentsMargins(0, 0, 0, 0)
        pv_layout.setSpacing(4)

        self.lbl_preview_title = QLabel(self._i18n.t("preview_title"))
        self.lbl_preview_title.setStyleSheet(
            f"font-size: 14px; font-weight: bold; color: {Mocha.BLUE}; padding: 2px;"
        )
        pv_layout.addWidget(self.lbl_preview_title)

        # Preview display (QLabel showing a QPixmap)
        self.preview_label = QLabel()
        self.preview_label.setMinimumHeight(80)
        self.preview_label.setMaximumHeight(250)
        self.preview_label.setScaledContents(False)
        self.preview_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        self.preview_label.setStyleSheet(
            f"background-color: {Mocha.BG2}; border: 1px solid {Mocha.SURFACE}; "
            f"border-radius: 4px; padding: 8px;"
        )
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setText("—")
        pv_layout.addWidget(self.preview_label, 1)

        # Text input row
        input_row = QHBoxLayout()
        self.preview_input = QLineEdit()
        self.preview_input.setPlaceholderText(self._i18n.t("preview_input"))
        self.preview_input.textChanged.connect(self._on_preview_text_changed)
        input_row.addWidget(self.preview_input, 1)
        pv_layout.addLayout(input_row)

        # Preset buttons row (scrollable)
        preset_scroll = QScrollArea()
        preset_scroll.setWidgetResizable(True)
        preset_scroll.setFixedHeight(36)
        preset_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        preset_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        preset_container = QWidget()
        self.preset_layout = QHBoxLayout(preset_container)
        self.preset_layout.setContentsMargins(0, 0, 0, 0)
        self.preset_layout.setSpacing(4)
        self._rebuild_preset_buttons()
        preset_scroll.setWidget(preset_container)
        pv_layout.addWidget(preset_scroll)

        vsplitter.addWidget(preview_widget)

        # -- BOTTOM: Atlas viewer ----
        atlas_widget = QWidget()
        at_layout = QVBoxLayout(atlas_widget)
        at_layout.setContentsMargins(0, 0, 0, 0)
        at_layout.setSpacing(4)

        # Atlas title + zoom controls
        atlas_header = QHBoxLayout()
        self.lbl_atlas_title = QLabel(self._i18n.t("atlas_title"))
        self.lbl_atlas_title.setStyleSheet(
            f"font-size: 14px; font-weight: bold; color: {Mocha.BLUE}; padding: 2px;"
        )
        atlas_header.addWidget(self.lbl_atlas_title)
        atlas_header.addStretch()

        self.btn_zoom_in = QPushButton(self._i18n.t("zoom_in"))
        self.btn_zoom_in.setFixedWidth(40)
        self.btn_zoom_in.clicked.connect(self._on_zoom_in)
        atlas_header.addWidget(self.btn_zoom_in)

        self.btn_zoom_out = QPushButton(self._i18n.t("zoom_out"))
        self.btn_zoom_out.setFixedWidth(40)
        self.btn_zoom_out.clicked.connect(self._on_zoom_out)
        atlas_header.addWidget(self.btn_zoom_out)

        self.btn_zoom_fit = QPushButton(self._i18n.t("zoom_fit"))
        self.btn_zoom_fit.setFixedWidth(50)
        self.btn_zoom_fit.clicked.connect(self._on_zoom_fit)
        atlas_header.addWidget(self.btn_zoom_fit)

        at_layout.addLayout(atlas_header)

        # Atlas graphics view
        self.atlas_scene = QGraphicsScene()
        self.atlas_view = ZoomableGraphicsView()
        self.atlas_view.setScene(self.atlas_scene)
        self._atlas_pixmap_item: Optional[QGraphicsPixmapItem] = None
        at_layout.addWidget(self.atlas_view, 1)

        vsplitter.addWidget(atlas_widget)
        vsplitter.setStretchFactor(0, 1)
        vsplitter.setStretchFactor(1, 2)

        layout.addWidget(vsplitter)
        return panel

    def _rebuild_preset_buttons(self) -> None:
        """Create preset text buttons from PRESET_TEXTS."""
        # Clear existing
        while self.preset_layout.count():
            item = self.preset_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        presets = self._i18n.get_presets()
        for key, (label, text) in presets.items():
            btn = QPushButton(label)
            btn.setFixedHeight(26)
            btn.setStyleSheet(f"font-size: 11px; padding: 2px 8px;")
            btn.clicked.connect(lambda checked, t=text: self.preview_input.setText(t))
            self.preset_layout.addWidget(btn)
        self.preset_layout.addStretch()

    # ── RIGHT: Adjust Panel ────────────────────────────────────────────

    def _build_right_panel(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)

        # Title
        self.lbl_adjust_title = QLabel(self._i18n.t("adjust_title"))
        self.lbl_adjust_title.setStyleSheet(
            f"font-size: 14px; font-weight: bold; color: {Mocha.BLUE}; padding: 2px;"
        )
        layout.addWidget(self.lbl_adjust_title)

        # ── Character Info ──
        info_group = QGroupBox("Character Info")
        info_layout = QFormLayout(info_group)
        self.lbl_info_char = QLabel("—")
        self.lbl_info_char.setStyleSheet(f"font-size: 28px; color: {Mocha.BLUE};")
        info_layout.addRow("Char:", self.lbl_info_char)
        self.lbl_info_unicode = QLabel("—")
        info_layout.addRow("Unicode:", self.lbl_info_unicode)
        self.lbl_info_category = QLabel("—")
        info_layout.addRow("Category:", self.lbl_info_category)
        layout.addWidget(info_group)

        # ── Glyph Preview Canvas ──
        preview_group = QGroupBox("Glyph Preview")
        pv_layout = QVBoxLayout(preview_group)
        self.glyph_preview_canvas = QLabel()
        self.glyph_preview_canvas.setFixedSize(240, 200)
        self.glyph_preview_canvas.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.glyph_preview_canvas.setStyleSheet(
            f"background-color: {Mocha.BG2}; border: 1px solid {Mocha.SURFACE}; border-radius: 4px;"
        )
        self.glyph_preview_canvas.setText("Select a glyph")
        pv_layout.addWidget(self.glyph_preview_canvas)
        layout.addWidget(preview_group)

        # ── Font Size / Generate Controls ──
        gen_group = QGroupBox("Font Size & Generate")
        gen_layout = QVBoxLayout(gen_group)
        gen_layout.setSpacing(6)

        # Preset size combo
        size_row = QHBoxLayout()
        size_row.addWidget(QLabel("Cell Size:"))
        self.cell_size_combo = QComboBox()
        self.cell_size_combo.addItem("Auto", 0)
        self.cell_size_combo.addItem("16 × 16 px", 16)
        self.cell_size_combo.addItem("24 × 24 px", 24)
        self.cell_size_combo.addItem("32 × 32 px", 32)
        self.cell_size_combo.addItem("48 × 48 px", 48)
        self.cell_size_combo.addItem("64 × 64 px", 64)
        self.cell_size_combo.addItem("Custom...", -1)
        self.cell_size_combo.currentIndexChanged.connect(self._on_cell_size_changed)
        size_row.addWidget(self.cell_size_combo, 1)
        gen_layout.addLayout(size_row)

        # Custom size spinbox (hidden by default)
        custom_row = QHBoxLayout()
        custom_row.addWidget(QLabel("Custom (px):"))
        self.custom_size_spin = QSpinBox()
        self.custom_size_spin.setRange(8, 256)
        self.custom_size_spin.setValue(32)
        self.custom_size_spin.setEnabled(False)
        custom_row.addWidget(self.custom_size_spin, 1)
        gen_layout.addLayout(custom_row)

        # Fill empty spaces checkbox
        from PyQt6.QtWidgets import QCheckBox
        self.fill_empty_cb = QCheckBox("เติมลงในช่องว่างของ Base Image (ถ้ามี)")
        self.fill_empty_cb.setChecked(False)
        self.fill_empty_cb.setStyleSheet(f"color: {Mocha.TEXT}; margin-top: 5px; margin-bottom: 5px;")
        gen_layout.addWidget(self.fill_empty_cb)

        # Autofit checkbox
        self.autofit_cb = QCheckBox("ลดขนาด Cell อัตโนมัติเพื่อให้พอดีกรอบ Base Image")
        self.autofit_cb.setChecked(False)
        self.autofit_cb.setStyleSheet(f"color: {Mocha.TEXT}; margin-bottom: 5px;")
        gen_layout.addWidget(self.autofit_cb)

        # Generate button
        self.btn_generate = QPushButton("🔄  Generate Font Sheet")
        self.btn_generate.setMinimumHeight(40)
        self.btn_generate.setStyleSheet(
            f"QPushButton {{ background-color: {Mocha.BLUE}; color: {Mocha.BG}; "
            f"font-weight: bold; font-size: 14px; border-radius: 6px; }}"
            f"QPushButton:hover {{ background-color: {Mocha.GREEN}; }}"
        )
        self.btn_generate.clicked.connect(self._on_generate_sheet)
        gen_layout.addWidget(self.btn_generate)

        layout.addWidget(gen_group)

        # ── Offset / Scale Sliders ──
        slider_group = QGroupBox("Adjustments")
        sl_layout = QVBoxLayout(slider_group)
        sl_layout.setSpacing(2)

        # Helper: create a row with Label + Slider + Reset button
        def make_slider_row(label_text, slider, default_val, layout_target):
            row = QHBoxLayout()
            row.setSpacing(4)
            lbl = QLabel(label_text)
            lbl.setMinimumWidth(60)
            row.addWidget(lbl)
            row.addWidget(slider, 1)
            btn = QPushButton("↺")
            btn.setFixedSize(24, 24)
            btn.setToolTip(f"Reset to {default_val}")
            btn.setStyleSheet(
                f"QPushButton {{ background: {Mocha.SURFACE}; border: 1px solid {Mocha.OVERLAY}; "
                f"border-radius: 4px; font-size: 14px; color: {Mocha.SUBTLE}; padding: 0; }}"
                f"QPushButton:hover {{ background: {Mocha.RED}; color: {Mocha.BG}; }}"
            )
            btn.clicked.connect(lambda: slider.setValue(default_val))
            row.addWidget(btn)
            layout_target.addLayout(row)
            return lbl

        # X Offset
        self.slider_x = QSlider(Qt.Orientation.Horizontal)
        self.slider_x.setRange(-150, 150)
        self.slider_x.setValue(0)
        self.lbl_x_off = make_slider_row(
            self._i18n.t("x_offset") + ": 0", self.slider_x, 0, sl_layout
        )
        self.slider_x.valueChanged.connect(
            lambda v: self.lbl_x_off.setText(f'{self._i18n.t("x_offset")}: {v}')
        )
        self.slider_x.valueChanged.connect(self._on_slider_changed)
        self.slider_x.valueChanged.connect(lambda _: self._update_glyph_preview())

        # Y Offset
        self.slider_y = QSlider(Qt.Orientation.Horizontal)
        self.slider_y.setRange(-150, 150)
        self.slider_y.setValue(0)
        self.lbl_y_off = make_slider_row(
            self._i18n.t("y_offset") + ": 0", self.slider_y, 0, sl_layout
        )
        self.slider_y.valueChanged.connect(
            lambda v: self.lbl_y_off.setText(f'{self._i18n.t("y_offset")}: {v}')
        )
        self.slider_y.valueChanged.connect(self._on_slider_changed)
        self.slider_y.valueChanged.connect(lambda _: self._update_glyph_preview())

        # Scale
        self.slider_scale = QSlider(Qt.Orientation.Horizontal)
        self.slider_scale.setRange(50, 150)
        self.slider_scale.setValue(100)
        self.lbl_scale = make_slider_row(
            self._i18n.t("scale") + ": 100%", self.slider_scale, 100, sl_layout
        )
        self.slider_scale.valueChanged.connect(
            lambda v: self.lbl_scale.setText(f'{self._i18n.t("scale")}: {v}%')
        )
        self.slider_scale.valueChanged.connect(self._on_slider_changed)
        self.slider_scale.valueChanged.connect(lambda _: self._update_glyph_preview())

        layout.addWidget(slider_group)

        # ── Override Sliders ──
        override_group = QGroupBox("Overrides")
        ov_layout = QVBoxLayout(override_group)
        ov_layout.setSpacing(2)

        # Width Override
        self.slider_width = QSlider(Qt.Orientation.Horizontal)
        self.slider_width.setRange(0, 200)
        self.slider_width.setValue(0)
        self.lbl_width_ov = make_slider_row(
            self._i18n.t("width_override") + ": 0", self.slider_width, 0, ov_layout
        )
        self.slider_width.valueChanged.connect(
            lambda v: self.lbl_width_ov.setText(f'{self._i18n.t("width_override")}: {v}')
        )
        self.slider_width.valueChanged.connect(self._on_slider_changed)
        self.slider_width.valueChanged.connect(lambda _: self._update_glyph_preview())
        self.slider_width.valueChanged.connect(lambda _: self._preview_timer.start())

        # Height Override
        self.slider_height = QSlider(Qt.Orientation.Horizontal)
        self.slider_height.setRange(0, 200)
        self.slider_height.setValue(0)
        self.lbl_height_ov = make_slider_row(
            self._i18n.t("height_override") + ": 0", self.slider_height, 0, ov_layout
        )
        self.slider_height.valueChanged.connect(
            lambda v: self.lbl_height_ov.setText(f'{self._i18n.t("height_override")}: {v}')
        )
        self.slider_height.valueChanged.connect(self._on_slider_changed)
        self.slider_height.valueChanged.connect(lambda _: self._update_glyph_preview())
        self.slider_height.valueChanged.connect(lambda _: self._preview_timer.start())

        # Advance Override
        self.slider_advance = QSlider(Qt.Orientation.Horizontal)
        self.slider_advance.setRange(0, 200)
        self.slider_advance.setValue(0)
        self.lbl_advance_ov = make_slider_row(
            self._i18n.t("advance_override") + ": 0", self.slider_advance, 0, ov_layout
        )
        self.slider_advance.valueChanged.connect(
            lambda v: self.lbl_advance_ov.setText(f'{self._i18n.t("advance_override")}: {v}')
        )
        self.slider_advance.valueChanged.connect(self._on_slider_changed)
        self.slider_advance.valueChanged.connect(lambda _: self._update_glyph_preview())
        self.slider_advance.valueChanged.connect(lambda _: self._preview_timer.start())

        layout.addWidget(override_group)

        # ── Action Buttons ──
        self.btn_reset = QPushButton(self._i18n.t("reset"))
        self.btn_reset.clicked.connect(self._on_reset_adjustment)
        layout.addWidget(self.btn_reset)

        self.btn_apply_category = QPushButton(self._i18n.t("apply_category"))
        self.btn_apply_category.clicked.connect(self._on_apply_to_category)
        layout.addWidget(self.btn_apply_category)

        # ── Quality Info ──
        quality_group = QGroupBox(self._i18n.t("quality"))
        q_layout = QFormLayout(quality_group)
        self.lbl_fill_w = QLabel("—")
        q_layout.addRow(self._i18n.t("fill_w") + ":", self.lbl_fill_w)
        self.lbl_fill_h = QLabel("—")
        q_layout.addRow(self._i18n.t("fill_h") + ":", self.lbl_fill_h)
        self.lbl_quality_status = QLabel("—")
        self.lbl_quality_status.setStyleSheet(f"font-weight: bold;")
        q_layout.addRow(self._i18n.t("col_status") + ":", self.lbl_quality_status)
        layout.addWidget(quality_group)

        layout.addStretch()

        scroll.setWidget(panel)
        return scroll

    # =================================================================== #
    #  Status Bar                                                           #
    # =================================================================== #

    def _build_status_bar(self) -> None:
        sb = QStatusBar()
        self.setStatusBar(sb)
        self.status_label = QLabel(self._i18n.t("status_ready"))
        sb.addPermanentWidget(self.status_label, 1)
        
        credit_label = QLabel("หน๊ด หนวด translator")
        credit_label.setStyleSheet(f"color: {Mocha.SUBTLE}; font-size: 11px; margin-right: 10px;")
        sb.addPermanentWidget(credit_label)

    def _update_status_bar(self) -> None:
        """Rebuild the status bar text from current state."""
        parts = [self._i18n.t("status_ready")]
        if self._font_name:
            parts.append(f'{self._i18n.t("status_font")}: {self._font_name}')
        else:
            parts.append(self._i18n.t("status_no_font"))
        glyph_count = self._glyph_model.rowCount()
        parts.append(f'{self._i18n.t("status_glyphs")}: {glyph_count}')

        # Quality summary
        ok_count = sum(1 for g in self._glyph_model.glyphs if g.get("status") == "ok")
        total = max(glyph_count, 1)
        pct = ok_count / total * 100
        parts.append(f'{self._i18n.t("status_quality")}: {pct:.0f}% OK')

        self.status_label.setText("  |  ".join(parts))

    # =================================================================== #
    #  Shortcuts                                                            #
    # =================================================================== #

    def _setup_shortcuts(self) -> None:
        QShortcut(QKeySequence("Ctrl+Z"), self, self._on_undo)
        QShortcut(QKeySequence("Ctrl+Y"), self, self._on_redo)
        QShortcut(QKeySequence("Ctrl+S"), self, self._on_save_project)
        QShortcut(QKeySequence("Ctrl+O"), self, self._on_load_font)

    # =================================================================== #
    #  Timers                                                               #
    # =================================================================== #

    def _setup_timers(self) -> None:
        # Debounce timer for search
        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(300)
        self._search_timer.timeout.connect(self._apply_search_filter)

        # Debounce timer for slider adjustments
        self._slider_timer = QTimer(self)
        self._slider_timer.setSingleShot(True)
        self._slider_timer.setInterval(100)
        self._slider_timer.timeout.connect(self._apply_slider_adjustment)

        # Debounce timer for preview re-render
        self._preview_timer = QTimer(self)
        self._preview_timer.setSingleShot(True)
        self._preview_timer.setInterval(150)
        self._preview_timer.timeout.connect(self._render_preview)

    # =================================================================== #
    #  Signal Handlers                                                      #
    # =================================================================== #

    # -- Toolbar actions ----------------------------------------------------

    def _on_load_font(self) -> None:
        """Open file dialog to load a .ttf or .otf font."""
        start_dir = self._config.get("last_font_path", "") or str(_SCRIPT_DIR)
        path, _ = QFileDialog.getOpenFileName(
            self,
            self._i18n.t("load_font"),
            start_dir,
            self._i18n.t("font_filter"),
        )
        if not path:
            return

        self._font_path = path
        self._font_name = Path(path).stem
        self._config["last_font_path"] = str(Path(path).parent)
        save_config(self._config)

        # Populate glyph table with Thai characters
        self._populate_glyph_table_from_font(path)
        self._update_status_bar()

        # Show confirmation
        msg = self._i18n.t("msg_font_loaded").format(self._font_name)
        self.status_label.setText(msg)

    def _on_load_project(self) -> None:
        """Load a .ppfs project JSON file."""
        start_dir = self._config.get("last_project_path", "") or str(_SCRIPT_DIR)
        path, _ = QFileDialog.getOpenFileName(
            self,
            self._i18n.t("load_project"),
            start_dir,
            self._i18n.t("project_filter"),
        )
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                project = json.load(f)
        except (json.JSONDecodeError, OSError) as exc:
            QMessageBox.warning(self, "Error", str(exc))
            return

        # Restore state
        self._font_path = project.get("font_path")
        self._font_name = project.get("font_name", "")
        # Restore adjustments (keys are stored as string codepoints)
        raw_adj = project.get("adjustments", {})
        self._adjustments = {int(k): v for k, v in raw_adj.items()}
        self._undo_stack.clear()
        self._redo_stack.clear()

        if self._font_path and Path(self._font_path).exists():
            self._populate_glyph_table_from_font(self._font_path)
        else:
            self._populate_empty_table()

        self._config["last_project_path"] = str(Path(path).parent)
        save_config(self._config)
        self._update_status_bar()
        msg = self._i18n.t("msg_project_loaded").format(Path(path).name)
        self.status_label.setText(msg)

    def _on_save_project(self) -> None:
        """Save current state to a .ppfs JSON file."""
        start_dir = self._config.get("last_project_path", "") or str(_SCRIPT_DIR)
        path, _ = QFileDialog.getSaveFileName(
            self,
            self._i18n.t("save_project"),
            start_dir,
            self._i18n.t("project_filter"),
        )
        if not path:
            return
        if not path.endswith(".ppfs"):
            path += ".ppfs"

        project = {
            "font_path": self._font_path,
            "font_name": self._font_name,
            "adjustments": {str(k): v for k, v in self._adjustments.items()},
            "glyphs": [
                {
                    "char": g["char"],
                    "codepoint": g["codepoint"],
                    "category": g["category"],
                    "fill_pct": g["fill_pct"],
                    "status": g["status"],
                }
                for g in self._glyph_model.glyphs
            ],
        }

        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(project, f, indent=2, ensure_ascii=False)
        except OSError as exc:
            QMessageBox.warning(self, "Error", str(exc))
            return

        self._config["last_project_path"] = str(Path(path).parent)
        save_config(self._config)
        msg = self._i18n.t("msg_project_saved").format(Path(path).name)
        self.status_label.setText(msg)

    def _on_export(self) -> None:
        """Open the Export dialog and run the pipeline."""
        dlg = ExportDialog(self._i18n, self._config, self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        profile = dlg.get_profile()
        output_path = dlg.get_output_path()
        if not output_path:
            QMessageBox.warning(self, "Error", "No output folder selected.")
            return

        if not self._font_path or not Path(self._font_path).exists():
            QMessageBox.warning(self, "Error", "No font loaded. Cannot export.")
            return

        self._config["last_export_path"] = output_path
        save_config(self._config)

        out_dir = Path(output_path)
        out_dir.mkdir(parents=True, exist_ok=True)
        
        # Determine glyphs to export (skip ones marked as error)
        glyphs_to_export = [g for g in self._glyph_model.glyphs if g.get("status") != "error"]
        if not glyphs_to_export:
            QMessageBox.warning(self, "Error", "No valid glyphs to export.")
            return
            
        from PyQt6.QtWidgets import QProgressDialog
        total_steps = len(glyphs_to_export) + 5
        progress = QProgressDialog(self._i18n.t("export_start"), "Cancel", 0, total_steps, self)
        progress.setWindowTitle(self._i18n.t("export_title"))
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)
        progress.show()

        try:
            target_h = int(self._config.get("default_font_size", 42))
            ss_factor = int(self._config.get("supersampling_factor", 3))
            
            glyph_images = {}
            glyph_metrics_export = {}
            
            step = 0
            # 1) Render all valid glyphs
            for g in glyphs_to_export:
                if progress.wasCanceled():
                    return
                cp = g["codepoint"]
                char_str = g["char"]
                cat = g["category"]
                
                # Apply user adjustments
                adj = self._adjustments.get(cp, {})
                scale_pct = adj.get("scale", 100) / 100.0
                req_h = max(int(target_h * scale_pct), 1)
                req_w = req_h  # will be trimmed by renderer
                
                try:
                    if cat == "pua":
                        combo = pua_engine.get_combo_for_pua(cp)
                        img = font_renderer.render_composite(
                            self._font_path, combo[0], combo[1:], 
                            target_w=req_w*2, target_h=req_h, ss_factor=ss_factor
                        )
                    else:
                        img = font_renderer.render_glyph(
                            self._font_path, char_str, 
                            target_w=req_w*2, target_h=req_h, ss_factor=ss_factor
                        )
                    
                    if img.shape[0] > 0 and img.shape[1] > 0:
                        glyph_images[cp] = img
                        
                        # Calculate advance width
                        if cat != "pua":
                            m = font_renderer.measure_glyph(self._font_path, char_str, font_size=req_h)
                            adv = m.get("width", img.shape[1])
                        else:
                            # Advance for PUA is usually base consonant's width
                            combo = pua_engine.get_combo_for_pua(cp)
                            m = font_renderer.measure_glyph(self._font_path, combo[0], font_size=req_h)
                            adv = m.get("width", img.shape[1])
                            
                        # Overrides
                        if adj.get("advance", 0) > 0:
                            adv = adj["advance"]
                        
                        glyph_metrics_export[cp] = {
                            "ox": adj.get("x_offset", 0),
                            "oy": adj.get("y_offset", 0),
                            "adv": adv
                        }
                except Exception as e:
                    print(f"[Export] Failed to render U+{cp:04X}: {e}")
                
                step += 1
                if step % 50 == 0:
                    progress.setValue(step)
                    QApplication.processEvents()
                    
            # 2) Pack Atlas
            profile = dlg.get_profile()
            is_rgba_profile = profile in ("bmfont", "json_atlas")
            
            atlas_w = int(self._config.get("atlas_width", 4096))
            atlas_h = int(self._config.get("atlas_height", 4096))

            # 3) Create Atlas Image & Packing Data
            progress.setLabelText("Generating images...")
            progress.setValue(step + 2)
            QApplication.processEvents()

            if hasattr(self, '_base_image_arr') and self._base_image_arr is not None:
                # If using a base image, the user expects the export to EXACTLY match the "Generate Font Sheet" preview.
                if not hasattr(self, '_generated_canvas') or self._generated_canvas is None:
                    # Auto-generate with default or current UI settings if they didn't click Generate
                    combo_val = self.cell_size_combo.currentData()
                    cell_sz = self.custom_size_spin.value() if combo_val == -1 else (32 if combo_val == 0 else combo_val)
                    self._generate_base_image_sheet(cell_sz)
                
                atlas_img = self._generated_canvas
                if not is_rgba_profile and atlas_img.ndim == 3 and atlas_img.shape[2] == 4:
                    # Convert to grayscale if profile requires it
                    from PIL import Image
                    import numpy as np
                    atlas_img = np.array(Image.fromarray(atlas_img, 'RGBA').convert('L'))
                
                rects = getattr(self, '_generated_rects', [])
                
            else:
                import numpy as np
                if is_rgba_profile:
                    base_img_np = np.zeros((atlas_h, atlas_w, 4), dtype=np.uint8)
                else:
                    base_img_np = np.zeros((atlas_h, atlas_w), dtype=np.uint8)

                packer = atlas_packer.AtlasPacker(
                    width=atlas_w,
                    height=atlas_h,
                    padding=int(self._config.get("atlas_padding", 2))
                )
                
                # Pack input: (codepoint, width, height)
                pack_input = [(cp, img.shape[1], img.shape[0]) for cp, img in glyph_images.items()]
                rects = packer.pack(pack_input)
                atlas_img = packer.get_atlas_image(rects, glyph_images, base_image=base_img_np)
            from PIL import Image
            
            # Auto-detect mode based on array shape (RGBA if 3D, L if 2D)
            img_mode = "RGBA" if (atlas_img.ndim == 3 and atlas_img.shape[2] == 4) else "L"
            pil_atlas = Image.fromarray(atlas_img, mode=img_mode)
            png_path = out_dir / f"{self._font_name}_atlas.png"
            pil_atlas.save(png_path)
            
            # 4) Save DDS
            progress.setLabelText("Converting to DDS...")
            progress.setValue(step + 3)
            QApplication.processEvents()
            
            if profile == "dying_light_2":
                dds_path = out_dir / f"{self._font_name}_atlas.dds"
                dds_converter.png_to_dds_bc4(str(png_path), str(dds_path))
                    
            # 5) Generate metadata (.scr / json)
            progress.setLabelText("Generating metadata...")
            progress.setValue(step + 4)
            QApplication.processEvents()
            
            # Save mapping json
            mapping = pua_engine.generate_full_mapping()
            with open(out_dir / "mapping.json", "w", encoding="utf-8") as f:
                json.dump(mapping, f, indent=2, ensure_ascii=False)
                
            # Generate SCR file for Dying Light 2
            if profile == "dying_light_2":
                scr_content = []
                for r in rects:
                    cp = r.codepoint
                    m = glyph_metrics_export.get(cp, {"ox":0, "oy":0, "adv":r.w})
                    
                    # Apply overrides to SCR
                    adj = self._adjustments.get(cp, {})
                    w_val = adj.get("width", 0) or r.w
                    h_val = adj.get("height", 0) or r.h
                    
                    # Format: Char(codepoint, bw, bh, ax, ay, ox, oy, adv, page)
                    scr_line = f"    Char({cp}, {w_val}, {h_val}, {r.x}, {r.y}, {m['ox']}, {m['oy']}, {m['adv']}, 0)"
                    scr_content.append(scr_line)
                
                scr_path = out_dir / f"{self._font_name}.scr"
                with open(scr_path, "w", encoding="utf-8") as f:
                    f.write("sub font()\n{\n")
                    f.write("\n".join(scr_content))
                    f.write("\n}\n")
                    
            # Save summary
            summary = {
                "profile": profile,
                "font": self._font_name,
                "glyph_count": len(rects),
                "atlas_size": f"{pil_atlas.width}x{pil_atlas.height}",
                "adjustments_applied": len(self._adjustments)
            }
            with open(out_dir / "export_summary.json", "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
                    
            # Finish
            progress.setValue(total_steps)
            msg = self._i18n.t("msg_export_done").format(output_path)
            self.status_label.setText(msg)
            QMessageBox.information(self, self._i18n.t("export_title"), msg)

        except Exception as exc:
            import traceback
            traceback.print_exc()
            err = self._i18n.t("msg_export_error").format(str(exc))
            QMessageBox.critical(self, "Export Error", err)
        finally:
            progress.close()

    def _on_toggle_language(self) -> None:
        """Switch between EN and TH and refresh all labels."""
        new_lang = self._i18n.switch()
        self._config["default_language"] = new_lang
        save_config(self._config)
        self._refresh_all_labels()

    # -- Glyph table -------------------------------------------------------

    def _on_filter_changed(self, index: int) -> None:
        cat = self.filter_combo.itemData(index)
        if cat:
            self._glyph_proxy.set_category_filter(cat)

    def _on_search_text_changed(self, text: str) -> None:
        self._search_timer.start()

    def _apply_search_filter(self) -> None:
        self._glyph_proxy.set_search_text(self.search_edit.text())

    def _on_glyph_selected(self, proxy_index: QModelIndex) -> None:
        """Handle glyph selection in the table."""
        source_index = self._glyph_proxy.mapToSource(proxy_index)
        glyph = self._glyph_model.glyph_at(source_index.row())
        if not glyph:
            return

        cp = glyph["codepoint"]
        self._selected_cp = cp

        # Update info display
        self.lbl_info_char.setText(glyph["char"])
        self.lbl_info_unicode.setText(f'U+{cp:04X}')
        cat_key = f'cat_{glyph["category"]}'
        self.lbl_info_category.setText(self._i18n.t(cat_key))

        # Load adjustments into sliders (block signals to prevent feedback loop)
        adj = self._adjustments.get(cp, {})
        self._set_sliders_blocked(adj)

        # Update quality labels
        self.lbl_fill_w.setText(f'{glyph["fill_pct"]:.0f}%')
        self.lbl_fill_h.setText(f'{glyph["fill_pct"]:.0f}%')

        status = glyph.get("status", "ok")
        if status == "ok":
            self.lbl_quality_status.setText(self._i18n.t("status_ok"))
            self.lbl_quality_status.setStyleSheet(f"font-weight: bold; color: {Mocha.GREEN};")
        elif status == "warn":
            self.lbl_quality_status.setText(self._i18n.t("status_warn"))
            self.lbl_quality_status.setStyleSheet(f"font-weight: bold; color: {Mocha.YELLOW};")
        else:
            self.lbl_quality_status.setText(self._i18n.t("status_error"))
            self.lbl_quality_status.setStyleSheet(f"font-weight: bold; color: {Mocha.RED};")

        # Render the glyph preview
        self._update_glyph_preview()

    # -- Sliders / spinboxes ------------------------------------------------

    def _on_slider_changed(self, _value: int = 0) -> None:
        """Start the debounce timer when any slider/spinbox changes."""
        self._slider_timer.start()

    def _apply_slider_adjustment(self) -> None:
        """Read current slider values and store in adjustments dict."""
        if self._selected_cp is None:
            return

        cp = self._selected_cp

        # Push current state for undo before modifying
        self._push_undo()

        adj = {
            "x_offset": self.slider_x.value(),
            "y_offset": self.slider_y.value(),
            "scale": self.slider_scale.value(),
            "width": self.slider_width.value(),
            "height": self.slider_height.value(),
            "advance": self.slider_advance.value(),
        }
        self._adjustments[cp] = adj

        # Update the glyph entry in the table to reflect the adjustment
        for row, g in enumerate(self._glyph_model.glyphs):
            if g["codepoint"] == cp:
                # Recalculate fill based on scale
                base_fill = g.get("_base_fill_pct", g["fill_pct"])
                if "_base_fill_pct" not in g:
                    g["_base_fill_pct"] = base_fill  # save original
                scaled_fill = base_fill * (adj["scale"] / 100.0)
                g["fill_pct"] = round(min(scaled_fill, 100.0), 1)

                ok_thresh = int(self._config.get("quality_threshold_ok", 85))
                warn_thresh = int(self._config.get("quality_threshold_warn", 70))
                if g["fill_pct"] >= ok_thresh:
                    g["status"] = "ok"
                elif g["fill_pct"] >= warn_thresh:
                    g["status"] = "warn"
                else:
                    g["status"] = "error"

                # Notify the model to refresh this row
                self._glyph_model.update_glyph(row, g)

                # Update quality labels in adjust panel
                self.lbl_fill_w.setText(f'{g["fill_pct"]:.0f}%')
                self.lbl_fill_h.setText(f'{g["fill_pct"]:.0f}%')
                status = g["status"]
                if status == "ok":
                    self.lbl_quality_status.setText(self._i18n.t("status_ok"))
                    self.lbl_quality_status.setStyleSheet(f"font-weight: bold; color: {Mocha.GREEN};")
                elif status == "warn":
                    self.lbl_quality_status.setText(self._i18n.t("status_warn"))
                    self.lbl_quality_status.setStyleSheet(f"font-weight: bold; color: {Mocha.YELLOW};")
                else:
                    self.lbl_quality_status.setText(self._i18n.t("status_error"))
                    self.lbl_quality_status.setStyleSheet(f"font-weight: bold; color: {Mocha.RED};")
                break

        # Update status bar quality count
        self._update_status_bar()

        # Update single-glyph visual preview
        self._update_glyph_preview()

        # Trigger text preview re-render
        self._preview_timer.start()

    def _set_sliders_blocked(self, adj: dict) -> None:
        """Set slider values without triggering signals."""
        for w in (self.slider_x, self.slider_y, self.slider_scale,
                  self.slider_width, self.slider_height, self.slider_advance):
            w.blockSignals(True)

        self.slider_x.setValue(adj.get("x_offset", 0))
        self.slider_y.setValue(adj.get("y_offset", 0))
        self.slider_scale.setValue(adj.get("scale", 100))
        self.slider_width.setValue(adj.get("width", 0))
        self.slider_height.setValue(adj.get("height", 0))
        self.slider_advance.setValue(adj.get("advance", 0))

        for w in (self.slider_x, self.slider_y, self.slider_scale,
                  self.slider_width, self.slider_height, self.slider_advance):
            w.blockSignals(False)

        # Update all labels
        self.lbl_x_off.setText(f'{self._i18n.t("x_offset")}: {self.slider_x.value()}')
        self.lbl_y_off.setText(f'{self._i18n.t("y_offset")}: {self.slider_y.value()}')
        self.lbl_scale.setText(f'{self._i18n.t("scale")}: {self.slider_scale.value()}%')
        self.lbl_width_ov.setText(f'{self._i18n.t("width_override")}: {self.slider_width.value()}')
        self.lbl_height_ov.setText(f'{self._i18n.t("height_override")}: {self.slider_height.value()}')
        self.lbl_advance_ov.setText(f'{self._i18n.t("advance_override")}: {self.slider_advance.value()}')

    # -- Reset / Apply Category --------------------------------------------

    def _on_reset_adjustment(self) -> None:
        """Reset selected glyph's adjustments to defaults."""
        if self._selected_cp is None:
            return
        self._push_undo()
        self._adjustments.pop(self._selected_cp, None)
        self._set_sliders_blocked({})

        # Reset table row status back to original fill
        for row, g in enumerate(self._glyph_model.glyphs):
            if g["codepoint"] == self._selected_cp:
                if "_base_fill_pct" in g:
                    g["fill_pct"] = g["_base_fill_pct"]
                ok_thresh = int(self._config.get("quality_threshold_ok", 85))
                warn_thresh = int(self._config.get("quality_threshold_warn", 70))
                if g["fill_pct"] >= ok_thresh:
                    g["status"] = "ok"
                elif g["fill_pct"] >= warn_thresh:
                    g["status"] = "warn"
                else:
                    g["status"] = "error"
                self._glyph_model.update_glyph(row, g)
                # Update quality labels
                self.lbl_fill_w.setText(f'{g["fill_pct"]:.0f}%')
                self.lbl_fill_h.setText(f'{g["fill_pct"]:.0f}%')
                status = g["status"]
                if status == "ok":
                    self.lbl_quality_status.setText(self._i18n.t("status_ok"))
                    self.lbl_quality_status.setStyleSheet(f"font-weight: bold; color: {Mocha.GREEN};")
                elif status == "warn":
                    self.lbl_quality_status.setText(self._i18n.t("status_warn"))
                    self.lbl_quality_status.setStyleSheet(f"font-weight: bold; color: {Mocha.YELLOW};")
                else:
                    self.lbl_quality_status.setText(self._i18n.t("status_error"))
                    self.lbl_quality_status.setStyleSheet(f"font-weight: bold; color: {Mocha.RED};")
                break

        # Invalidate glyph preview cache & refresh
        self._cached_preview_qimg = None
        self._cached_preview_cp = None
        self._update_glyph_preview()
        self._update_status_bar()
        self._preview_timer.start()

    def _on_apply_to_category(self) -> None:
        """Apply current glyph's adjustments to all glyphs in the same category."""
        if self._selected_cp is None:
            return
        adj = self._adjustments.get(self._selected_cp)
        if not adj:
            return

        # Find the category of the selected glyph
        sel_cat = None
        for g in self._glyph_model.glyphs:
            if g["codepoint"] == self._selected_cp:
                sel_cat = g["category"]
                break
        if not sel_cat:
            return

        self._push_undo()
        for g in self._glyph_model.glyphs:
            if g["category"] == sel_cat:
                self._adjustments[g["codepoint"]] = copy.deepcopy(adj)

        self._preview_timer.start()

    # -- Preview ------------------------------------------------------------

    def _on_preview_text_changed(self, text: str) -> None:
        self._preview_timer.start()

    def _render_preview(self) -> None:
        """Render the preview text cluster-by-cluster with per-glyph adjustments.
        
        Thai text is segmented into grapheme clusters (consonant + combining
        marks).  Each cluster is rendered via QPainter (HarfBuzz shaping) then
        composed onto the canvas with that cluster's adjustment applied.
        """
        text = self.preview_input.text()
        if not text:
            self.preview_label.setPixmap(QPixmap())
            self.preview_label.setText("—")
            return

        if self._font_path and Path(self._font_path).exists():
            try:
                from PyQt6.QtGui import QFontDatabase, QFontMetrics

                # Load the custom font into Qt's font system
                font_id = QFontDatabase.addApplicationFont(self._font_path)
                if font_id >= 0:
                    families = QFontDatabase.applicationFontFamilies(font_id)
                    family_name = families[0] if families else "Segoe UI"
                else:
                    family_name = "Segoe UI"

                target_h = int(self._config.get("default_font_size", 42))
                base_font_size = target_h * 2

                # ── Segment text into grapheme clusters ──
                clusters = self._segment_thai_clusters(text)

                # ── First pass: measure total width ──
                base_font = QFont(family_name, base_font_size)
                base_fm = QFontMetrics(base_font)
                total_w = 40  # padding
                cluster_infos = []

                for cluster in clusters:
                    # Get adjustment for the base character of this cluster
                    base_cp = ord(cluster[0])

                    # For the selected glyph, read directly from sliders
                    # (they may not be saved to _adjustments yet due to debounce)
                    if base_cp == self._selected_cp:
                        adj = {
                            "x_offset": self.slider_x.value(),
                            "y_offset": self.slider_y.value(),
                            "scale": self.slider_scale.value(),
                            "width": self.slider_width.value(),
                            "height": self.slider_height.value(),
                            "advance": self.slider_advance.value(),
                        }
                    else:
                        adj = self._adjustments.get(base_cp, {})

                    scale_pct = adj.get("scale", 100) / 100.0
                    w_override = adj.get("width", 0)
                    adv_override = adj.get("advance", 0)

                    # Measure cluster at scaled font size
                    scaled_size = max(int(base_font_size * scale_pct), 8)
                    cluster_font = QFont(family_name, scaled_size)
                    cfm = QFontMetrics(cluster_font)
                    cw = cfm.horizontalAdvance(cluster)

                    # Apply width override
                    draw_w = w_override if w_override > 0 else cw
                    # Apply advance override
                    advance = adv_override if adv_override > 0 else draw_w

                    cluster_infos.append({
                        "text": cluster,
                        "cp": base_cp,
                        "adj": adj,
                        "font": cluster_font,
                        "fm": cfm,
                        "draw_w": draw_w,
                        "natural_w": cw,
                        "advance": advance,
                        "scale_pct": scale_pct,
                    })
                    total_w += advance

                # ── Create canvas ──
                canvas_w = max(total_w + 40, 400)
                canvas_h = max(base_fm.height() + 60, base_font_size + 60)

                img = QImage(canvas_w, canvas_h, QImage.Format.Format_ARGB32)
                img.fill(QColor(30, 30, 46))

                painter = QPainter(img)
                painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)

                # ── Draw baseline guide ──
                baseline_y = (canvas_h + base_fm.ascent() - base_fm.descent()) // 2
                painter.setPen(QPen(QColor(Mocha.SURFACE), 1, Qt.PenStyle.DashLine))
                painter.drawLine(0, baseline_y, canvas_w, baseline_y)

                # ── Second pass: draw each cluster ──
                cursor_x = 20
                for ci in cluster_infos:
                    adj = ci["adj"]
                    x_off = adj.get("x_offset", 0)
                    y_off = adj.get("y_offset", 0)
                    h_override = adj.get("height", 0)
                    scale_pct = ci["scale_pct"]

                    # Set font and color
                    painter.setFont(ci["font"])

                    # Highlight adjusted characters
                    has_adj = (x_off != 0 or y_off != 0 or scale_pct != 1.0
                               or adj.get("width", 0) > 0 or h_override > 0)
                    if has_adj:
                        painter.setPen(QColor(137, 180, 250))  # Blue for adjusted
                    else:
                        painter.setPen(QColor(205, 214, 244))  # Default text color

                    # Calculate Y based on this cluster's font metrics
                    cfm = ci["fm"]
                    cluster_baseline = (canvas_h + cfm.ascent() - cfm.descent()) // 2

                    # Calculate width/height scale factors from overrides
                    w_override = adj.get("width", 0)
                    w_scale = (w_override / ci["natural_w"]) if (w_override > 0 and ci["natural_w"] > 0) else 1.0
                    h_scale = (h_override / cfm.height()) if (h_override > 0 and cfm.height() > 0) else 1.0

                    # Apply width/height override by scaling the painter
                    if w_scale != 1.0 or h_scale != 1.0:
                        painter.save()
                        painter.translate(cursor_x + x_off, cluster_baseline + y_off)
                        painter.scale(w_scale, h_scale)
                        painter.drawText(0, 0, ci["text"])
                        painter.restore()
                    else:
                        draw_x = cursor_x + x_off
                        draw_y = cluster_baseline + y_off
                        painter.drawText(draw_x, draw_y, ci["text"])

                    cursor_x += ci["advance"]

                painter.end()

                pixmap = QPixmap.fromImage(img)

                # Scale to fit the preview label width
                label_w = self.preview_label.width() - 16
                if label_w > 0 and pixmap.width() > label_w:
                    pixmap = pixmap.scaledToWidth(
                        label_w,
                        Qt.TransformationMode.SmoothTransformation,
                    )

                self.preview_label.setText("")
                self.preview_label.setPixmap(pixmap)
                return
            except Exception as exc:
                print(f"[Preview] Render error: {exc}")

        # Fallback: just show the text as-is with a styled label
        self.preview_label.setPixmap(QPixmap())
        self.preview_label.setText(text)
        self.preview_label.setStyleSheet(
            f"background-color: {Mocha.BG2}; border: 1px solid {Mocha.SURFACE}; "
            f"border-radius: 4px; padding: 8px; font-size: 32px; color: {Mocha.TEXT};"
        )

    @staticmethod
    def _segment_thai_clusters(text: str) -> list[str]:
        """Segment text into grapheme clusters for per-character rendering.
        
        A Thai grapheme cluster = base consonant + following combining marks
        (above/below vowels, tone marks, etc.).  Latin/number characters are
        each their own cluster.
        """
        # Thai combining character ranges
        _COMBINING = set()
        _COMBINING.update(range(0x0E31, 0x0E3B))  # sara i..sara ue, mai han akat, etc.
        _COMBINING.update(range(0x0E47, 0x0E4F))  # maitaikhu..yamakkan
        # Also include sara am's nikhahit component
        _COMBINING.add(0x0E4D)  # nikhahit

        clusters: list[str] = []
        i = 0
        while i < len(text):
            ch = text[i]
            cluster = ch
            i += 1
            # Collect following Thai combining characters
            while i < len(text) and ord(text[i]) in _COMBINING:
                cluster += text[i]
                i += 1
            clusters.append(cluster)
        return clusters

    # -- Single-glyph visual preview ----------------------------------------

    def _update_glyph_preview(self) -> None:
        """Render the currently selected glyph on the preview canvas with offset/scale.
        
        Uses a cache: the glyph is only re-rendered from the font when the
        selected codepoint or scale changes.  X/Y offset changes just
        recompose the cached image at a new position (instant).
        """
        if self._selected_cp is None:
            self.glyph_preview_canvas.setPixmap(QPixmap())
            self.glyph_preview_canvas.setText("Select a glyph")
            return

        if not self._font_path or not Path(self._font_path).exists():
            self.glyph_preview_canvas.setPixmap(QPixmap())
            self.glyph_preview_canvas.setText("Load a font first")
            return

        canvas_w = 240
        canvas_h = 200

        # Read current slider values directly for instant response
        x_off = self.slider_x.value()
        y_off = self.slider_y.value()
        cur_scale = self.slider_scale.value()
        scale_pct = cur_scale / 100.0

        # Check if we need to re-render the glyph (codepoint or scale changed)
        need_render = (
            self._cached_preview_qimg is None
            or self._cached_preview_cp != self._selected_cp
            or self._cached_preview_scale != cur_scale
        )

        if need_render:
            try:
                # Find the character string for this codepoint
                char_str = None
                for g in self._glyph_model.glyphs:
                    if g["codepoint"] == self._selected_cp:
                        char_str = g["char"]
                        break

                if char_str:
                    target_h = int(self._config.get("default_font_size", 42))
                    render_h = max(int(target_h * scale_pct * 2.5), 8)
                    render_w = render_h * 2

                    if len(char_str) == 1:
                        glyph_arr = font_renderer.render_glyph(
                            self._font_path, char_str,
                            target_w=render_w, target_h=render_h, ss_factor=2
                        )
                    else:
                        glyph_arr = font_renderer.render_composite(
                            self._font_path, char_str[0], char_str[1:],
                            target_w=render_w, target_h=render_h, ss_factor=2
                        )

                    if glyph_arr.shape[0] > 0 and glyph_arr.shape[1] > 0:
                        from PIL import Image as PILImage
                        pil_glyph = PILImage.fromarray(glyph_arr, mode="L")
                        rgba = PILImage.new("RGBA", pil_glyph.size, (0, 0, 0, 0))
                        glyph_colored = PILImage.new("RGBA", pil_glyph.size, (137, 180, 250, 255))
                        rgba.paste(glyph_colored, mask=pil_glyph)

                        rgba_data = rgba.tobytes("raw", "RGBA")
                        raw_qimg = QImage(
                            rgba_data, rgba.width, rgba.height,
                            rgba.width * 4, QImage.Format.Format_RGBA8888
                        )
                        # .copy() ensures Qt owns the pixel data (no GC issues)
                        self._cached_preview_qimg = raw_qimg.copy()
                        self._cached_preview_cp = self._selected_cp
                        self._cached_preview_scale = cur_scale
                    else:
                        self._cached_preview_qimg = None
                else:
                    self._cached_preview_qimg = None
            except Exception as exc:
                print(f"[GlyphPreview] Render error: {exc}")
                self._cached_preview_qimg = None

        # --- Compose canvas (fast — no font rendering) ---
        img = QImage(canvas_w, canvas_h, QImage.Format.Format_ARGB32)
        img.fill(QColor(Mocha.BG2))

        painter = QPainter(img)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw grid
        painter.setPen(QColor(Mocha.SURFACE))
        grid = 20
        for gx in range(0, canvas_w, grid):
            painter.drawLine(gx, 0, gx, canvas_h)
        for gy in range(0, canvas_h, grid):
            painter.drawLine(0, gy, canvas_w, gy)

        # Draw baseline
        baseline_y = canvas_h // 2 + 20
        center_x = canvas_w // 2
        painter.setPen(QColor(Mocha.BLUE))
        painter.drawLine(0, baseline_y, canvas_w, baseline_y)
        # Vertical center
        painter.setPen(QColor(Mocha.OVERLAY))
        painter.drawLine(center_x, 0, center_x, canvas_h)

        # Draw cached glyph at offset position (with Width/Height overrides)
        if self._cached_preview_qimg is not None:
            gw = self._cached_preview_qimg.width()
            gh = self._cached_preview_qimg.height()

            # Apply Width/Height overrides as visual stretch
            w_override = self.slider_width.value()
            h_override = self.slider_height.value()
            draw_w = w_override if w_override > 0 else gw
            draw_h = h_override if h_override > 0 else gh

            glyph_x = center_x - draw_w // 2 + x_off
            glyph_y = baseline_y - draw_h + y_off

            target_rect = QRectF(glyph_x, glyph_y, draw_w, draw_h)
            source_rect = QRectF(0, 0, gw, gh)
            painter.drawImage(target_rect, self._cached_preview_qimg, source_rect)

            # Draw bounding box outline (green dashed) to show override size
            if w_override > 0 or h_override > 0:
                painter.setPen(QPen(QColor(Mocha.GREEN), 1, Qt.PenStyle.DashLine))
                painter.drawRect(target_rect)

        # Draw origin crosshair (red)
        origin_x = center_x + x_off
        origin_y = baseline_y + y_off
        pen = QPen(QColor(Mocha.RED), 2)
        painter.setPen(pen)
        painter.drawLine(origin_x - 10, origin_y, origin_x + 10, origin_y)
        painter.drawLine(origin_x, origin_y - 10, origin_x, origin_y + 10)

        # Draw info text
        painter.setPen(QColor(Mocha.SUBTLE))
        painter.setFont(QFont("Segoe UI", 9))
        w_val = self.slider_width.value()
        h_val = self.slider_height.value()
        adv_val = self.slider_advance.value()
        info_text = f"X:{x_off:+d} Y:{y_off:+d} S:{cur_scale}%"
        painter.drawText(4, 14, info_text)
        if w_val > 0 or h_val > 0 or adv_val > 0:
            info2 = f"W:{w_val} H:{h_val} Adv:{adv_val}"
            painter.drawText(4, canvas_h - 6, info2)

        painter.end()

        pixmap = QPixmap.fromImage(img)
        self.glyph_preview_canvas.setText("")
        self.glyph_preview_canvas.setPixmap(pixmap)

    # -- Atlas zoom controls ------------------------------------------------

    def _on_zoom_in(self) -> None:
        self.atlas_view.scale(1.25, 1.25)

    def _on_zoom_out(self) -> None:
        self.atlas_view.scale(0.8, 0.8)

    def _on_zoom_fit(self) -> None:
        self.atlas_view.zoom_fit()

    # -- Cell size / Generate handlers --------------------------------------

    def _on_cell_size_changed(self, index: int) -> None:
        data = self.cell_size_combo.currentData()
        self.custom_size_spin.setEnabled(data == -1)

    def _on_generate_sheet(self) -> None:
        """Generate/regenerate the font sheet with current settings."""
        if not self._font_path:
            QMessageBox.warning(self, "No Font", "Please load a font file first.")
            return

        # Determine cell size
        combo_val = self.cell_size_combo.currentData()
        if combo_val == -1:  # Custom
            cell_size = self.custom_size_spin.value()
        elif combo_val == 0:  # Auto
            cell_size = self._cell_size if hasattr(self, '_cell_size') and self._cell_size > 0 else 32
        else:
            cell_size = combo_val

        self.statusBar().showMessage(f"Generating font sheet (cell: {cell_size}px)...", 0)
        QApplication.processEvents()

        try:
            self._generate_base_image_sheet(cell_size)
            self.statusBar().showMessage(f"✅ Font sheet generated! Cell size: {cell_size}px", 5000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Generation failed:\n{e}")
            self.statusBar().showMessage(f"❌ Generation failed", 5000)

    def _generate_base_image_sheet(self, cell_size: int) -> None:
        """Core logic for generating a font sheet onto the base image or blank canvas."""
        from PIL import Image, ImageDraw, ImageFont
        import numpy as np

        # Get the Thai charset to render (including PUA ligatures)
        glyph_items = []
        for cp in range(0x0E01, 0x0E5C):  # Thai Unicode range
            glyph_items.append((cp, chr(cp)))
            
        try:
            import pua_engine
            for pua_cp in pua_engine.get_all_pua_codepoints():
                combo = pua_engine.get_combo_for_pua(pua_cp)
                glyph_items.append((pua_cp, combo))
        except Exception as e:
            print(f"Warning: Could not load PUA ligatures: {e}")

        # Determine canvas
        if hasattr(self, '_base_image_arr') and self._base_image_arr is not None:
            base_h, base_w = self._base_image_arr.shape[:2]
            autofit = hasattr(self, 'autofit_cb') and self.autofit_cb.isChecked()
            fill_empty = hasattr(self, 'fill_empty_cb') and self.fill_empty_cb.isChecked()
            
            best_cell_size = cell_size
            test_sizes = range(cell_size, 7, -1) if autofit else [cell_size]
            
            for test_sz in test_sizes:
                cols = base_w // test_sz
                if cols == 0:
                    cols = 1

                # Find the last non-empty row in the base image
                used_rows = 0
                for row_idx in range(base_h // test_sz):
                    y_start = row_idx * test_sz
                    y_end = min(y_start + test_sz, base_h)
                    row_slice = self._base_image_arr[y_start:y_end, :]
                    
                    if row_slice.ndim == 3 and row_slice.shape[2] == 4:
                        rgb_max = np.max(row_slice[:, :, :3], axis=2)
                        alpha = row_slice[:, :, 3]
                        is_occupied = np.any(alpha > 10)
                    else:
                        is_occupied = np.any(row_slice > 10)
                        
                    if is_occupied:
                        used_rows = row_idx + 1

                # Calculate needed rows for Thai chars
                available_cells = []
                
                if fill_empty:
                    for row_idx in range(base_h // test_sz):
                        for col_idx in range(cols):
                            y_start = row_idx * test_sz
                            y_end = min(y_start + test_sz, base_h)
                            x_start = col_idx * test_sz
                            x_end = min(x_start + test_sz, base_w)
                            
                            cell_slice = self._base_image_arr[y_start:y_end, x_start:x_end]
                            if cell_slice.size == 0:
                                continue
                                
                            # Check if empty (treat pure black background as empty)
                            if cell_slice.ndim == 3 and cell_slice.shape[2] == 4:
                                rgb_max = np.max(cell_slice[:, :, :3], axis=2)
                                alpha = cell_slice[:, :, 3]
                                is_empty = not np.any(alpha > 10)
                            else:
                                is_empty = not np.any(cell_slice > 10)
                                
                            if is_empty:
                                available_cells.append((row_idx, col_idx))

                remaining_chars = max(0, len(glyph_items) - len(available_cells))
                thai_rows_needed = (remaining_chars + cols - 1) // cols if cols > 0 else 0
                total_rows_needed = used_rows + thai_rows_needed
                new_h = max(base_h, total_rows_needed * test_sz)
                
                if autofit:
                    if new_h <= base_h:
                        best_cell_size = test_sz
                        break
                    else:
                        best_cell_size = test_sz # fallback to smallest tested if none fits
                else:
                    break
                    
            cell_size = best_cell_size

            # Create expanded canvas
            if base_h < new_h:
                canvas = np.zeros((new_h, base_w, 4), dtype=np.uint8) if self._base_image_arr.ndim == 3 else np.zeros((new_h, base_w), dtype=np.uint8)
                canvas[:base_h, :base_w] = self._base_image_arr
            else:
                canvas = self._base_image_arr.copy()

            start_row = used_rows
        else:
            # Blank canvas
            available_cells = []
            cols = 16  # default 16 columns
            rows_needed = (len(glyph_items) + cols - 1) // cols
            base_w = cols * cell_size
            base_h = rows_needed * cell_size
            canvas = np.zeros((base_h, base_w, 4), dtype=np.uint8)
            start_row = 0

        # Render each Thai character
        font_size_px = int(cell_size * 0.8)
        try:
            pil_font = ImageFont.truetype(self._font_path, font_size_px)
        except Exception as e:
            raise RuntimeError(f"Cannot load font: {e}")

        # Add dummy Rect class locally for compatibility with Export packer output
        class DummyRect:
            def __init__(self, cp, x, y, w, h):
                self.codepoint = cp
                self.x = x
                self.y = y
                self.w = w
                self.h = h
                

        if canvas.shape[1] < cell_size:
            pad_w = cell_size - canvas.shape[1]
            if canvas.ndim == 3:
                canvas = np.pad(canvas, ((0,0), (0, pad_w), (0,0)), mode='constant')
            else:
                canvas = np.pad(canvas, ((0,0), (0, pad_w)), mode='constant')

        self._generated_rects = []

        chars_placed_in_empty = 0
        for i, (codepoint, char_str) in enumerate(glyph_items):
            if available_cells:
                row, col = available_cells.pop(0)
                chars_placed_in_empty += 1
            else:
                idx = i - chars_placed_in_empty
                col = idx % cols
                row = start_row + (idx // cols)
                
            x = col * cell_size
            y = row * cell_size

            if y + cell_size > canvas.shape[0]:
                break

            # Render character to a small cell image
            cell_img = Image.new('RGBA', (cell_size, cell_size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(cell_img)

            # Measure text
            bbox = draw.textbbox((0, 0), char_str, font=pil_font)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            tx = (cell_size - tw) // 2 - bbox[0]
            ty = (cell_size - th) // 2 - bbox[1]

            draw.text((tx, ty), char_str, font=pil_font, fill=(255, 255, 255, 255))

            cell_arr = np.array(cell_img)

            # Paste onto canvas
            if canvas.ndim == 3 and canvas.shape[2] == 4:
                canvas[y:y+cell_size, x:x+cell_size] = cell_arr
            elif canvas.ndim == 3 and canvas.shape[2] == 3:
                canvas[y:y+cell_size, x:x+cell_size] = cell_arr[:, :, :3]
            else:
                canvas[y:y+cell_size, x:x+cell_size] = cell_arr[:, :, 0]
                
            self._generated_rects.append(DummyRect(codepoint, x, y, cell_size, cell_size))

        self._generated_canvas = canvas

        # Update the atlas view
        self._update_atlas_from_array(canvas)

    def _update_atlas_from_array(self, arr) -> None:
        """Update the atlas viewer with a numpy array."""
        from PIL import Image

        if arr.ndim == 2:
            pil_img = Image.fromarray(arr, 'L').convert('RGBA')
        elif arr.ndim == 3 and arr.shape[2] == 3:
            pil_img = Image.fromarray(arr, 'RGB').convert('RGBA')
        elif arr.ndim == 3 and arr.shape[2] == 4:
            pil_img = Image.fromarray(arr, 'RGBA')
        else:
            return

        # Convert to QImage
        self._last_atlas_data = pil_img.tobytes()
        qimg = QImage(self._last_atlas_data, pil_img.width, pil_img.height, pil_img.width * 4, QImage.Format.Format_RGBA8888)
        pixmap = QPixmap.fromImage(qimg.copy())  # .copy() to detach from buffer

        if getattr(self, '_atlas_pixmap_item', None) is None:
            self._atlas_pixmap_item = self.atlas_scene.addPixmap(pixmap)
        else:
            self._atlas_pixmap_item.setPixmap(pixmap)
            
        self.atlas_scene.setSceneRect(QRectF(pixmap.rect()))
        self.atlas_view.zoom_fit()

    # =================================================================== #
    #  Undo / Redo                                                          #
    # =================================================================== #

    def _push_undo(self) -> None:
        """Save current adjustments snapshot for undo."""
        snapshot = copy.deepcopy(self._adjustments)
        self._undo_stack.append(snapshot)
        if len(self._undo_stack) > self._max_undo:
            self._undo_stack.pop(0)
        self._redo_stack.clear()

    def _on_undo(self) -> None:
        if not self._undo_stack:
            return
        # Save current state as redo
        self._redo_stack.append(copy.deepcopy(self._adjustments))
        self._adjustments = self._undo_stack.pop()

        # Re-load sliders if a glyph is selected
        if self._selected_cp is not None:
            adj = self._adjustments.get(self._selected_cp, {})
            self._set_sliders_blocked(adj)
        self._preview_timer.start()
        self.status_label.setText(f'{self._i18n.t("undo")} ← ({len(self._undo_stack)} left)')

    def _on_redo(self) -> None:
        if not self._redo_stack:
            return
        self._undo_stack.append(copy.deepcopy(self._adjustments))
        self._adjustments = self._redo_stack.pop()

        if self._selected_cp is not None:
            adj = self._adjustments.get(self._selected_cp, {})
            self._set_sliders_blocked(adj)
        self._preview_timer.start()
        self.status_label.setText(f'{self._i18n.t("redo")} → ({len(self._redo_stack)} left)')

    # =================================================================== #
    #  Data Population                                                      #
    # =================================================================== #

    def _populate_empty_table(self) -> None:
        """Populate the glyph table with all characters (no font)."""
        chars = get_full_charset()
        self._glyph_model.set_glyphs(chars)
        self._update_atlas_placeholder()

    def _populate_glyph_table_from_font(self, font_path: str) -> None:
        """Load font and populate the glyph table with metrics from it."""
        chars = get_full_charset()

        # Add PUA composites from the engine
        pua_codepoints = pua_engine.get_all_pua_codepoints()
        for pua_cp in pua_codepoints:
            try:
                combo = pua_engine.get_combo_for_pua(pua_cp)
                chars.append({
                    "char": combo,
                    "codepoint": pua_cp,
                    "category": "pua",
                    "fill_pct": 0.0,
                    "status": "ok",
                })
            except KeyError:
                pass

        # Measure glyphs for quality assessment
        ok_thresh = int(self._config.get("quality_threshold_ok", 85))
        warn_thresh = int(self._config.get("quality_threshold_warn", 70))
        target_h = int(self._config.get("default_font_size", 42))

        for entry in chars:
            if entry["category"] != "pua" and len(entry["char"]) == 1:
                try:
                    metrics = font_renderer.measure_glyph(font_path, entry["char"])
                    w = metrics.get("width", 0)
                    h = metrics.get("height", 0)
                    if w > 0 and h > 0:
                        fill = min(h / target_h * 100, 100) if target_h > 0 else 0
                        entry["fill_pct"] = round(fill, 1)
                        if fill >= ok_thresh:
                            entry["status"] = "ok"
                        elif fill >= warn_thresh:
                            entry["status"] = "warn"
                        else:
                            entry["status"] = "error"
                        # Store metrics for preview rendering
                        self._glyph_metrics[entry["char"]] = {
                            "ox": 0, "oy": -int(h * 0.8),
                            "adv": w, "bw": w, "bh": h,
                        }
                except Exception:
                    pass

        self._glyph_model.set_glyphs(chars)
        self._update_atlas_placeholder()
        self._update_status_bar()

    def _update_atlas_placeholder(self) -> None:
        """Render a real atlas preview with actual glyphs from the loaded font."""
        glyph_count = self._glyph_model.rowCount()

        preview_size = 512
        atlas_w = int(self._config.get("atlas_width", 4096))
        atlas_h = int(self._config.get("atlas_height", 4096))

        # If no font loaded, show info-only placeholder
        if not self._font_path or not Path(self._font_path).exists():
            img = QImage(preview_size, preview_size, QImage.Format.Format_ARGB32)
            img.fill(QColor(Mocha.BG2))
            painter = QPainter(img)
            painter.setPen(QColor(Mocha.SUBTLE))
            painter.setFont(QFont("Segoe UI", 14))
            painter.drawText(
                QRectF(0, 0, preview_size, preview_size),
                Qt.AlignmentFlag.AlignCenter,
                f"Atlas: {atlas_w}×{atlas_h}\nLoad a font to preview",
            )
            painter.end()
            pixmap = QPixmap.fromImage(img)
            
            if getattr(self, '_atlas_pixmap_item', None) is None:
                self._atlas_pixmap_item = self.atlas_scene.addPixmap(pixmap)
            else:
                self._atlas_pixmap_item.setPixmap(pixmap)
                
            self.atlas_scene.setSceneRect(QRectF(pixmap.rect()))
            return

        # Render a sample of glyphs onto a mini atlas
        img = QImage(preview_size, preview_size, QImage.Format.Format_ARGB32)
        img.fill(QColor(24, 24, 37))  # Mocha.BG2

        painter = QPainter(img)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw subtle grid
        painter.setPen(QColor(Mocha.SURFACE))
        for x in range(0, preview_size, 32):
            painter.drawLine(x, 0, x, preview_size)
        for y in range(0, preview_size, 32):
            painter.drawLine(0, y, preview_size, y)

        # Render up to 200 base glyphs (non-PUA, single char) into the atlas
        cell_w = 28
        cell_h = 32
        padding = 2
        cursor_x = padding
        cursor_y = padding
        row_height = cell_h
        rendered = 0

        glyphs = self._glyph_model.glyphs
        for g in glyphs:
            if g["category"] == "pua":
                continue
            if len(g["char"]) != 1:
                continue
            if rendered >= 200:
                break

            ch = g["char"]
            cp = g["codepoint"]

            # Wrap to next row
            if cursor_x + cell_w > preview_size - padding:
                cursor_x = padding
                cursor_y += row_height + padding
                if cursor_y + cell_h > preview_size - padding:
                    break

            try:
                # Render glyph
                glyph_arr = font_renderer.render_glyph(
                    self._font_path, ch,
                    target_w=cell_w, target_h=cell_h, ss_factor=2
                )

                if glyph_arr.shape[0] > 0 and glyph_arr.shape[1] > 0:
                    from PIL import Image as PILImage
                    pil_g = PILImage.fromarray(glyph_arr, mode="L")
                    rgba = PILImage.new("RGBA", pil_g.size, (0, 0, 0, 0))
                    white = PILImage.new("RGBA", pil_g.size, (205, 214, 244, 255))
                    rgba.paste(white, mask=pil_g)

                    rgba_data = rgba.tobytes("raw", "RGBA")
                    glyph_qimg = QImage(
                        rgba_data, rgba.width, rgba.height,
                        rgba.width * 4, QImage.Format.Format_RGBA8888
                    )
                    painter.drawImage(cursor_x, cursor_y, glyph_qimg)
                    rendered += 1

            except Exception:
                pass

            cursor_x += cell_w + padding

        # Draw summary info at bottom
        painter.setPen(QColor(Mocha.BLUE))
        painter.setFont(QFont("Segoe UI", 10))
        info = f"Atlas {atlas_w}×{atlas_h} | Showing {rendered}/{glyph_count} glyphs"
        painter.drawText(
            QRectF(0, preview_size - 24, preview_size, 24),
            Qt.AlignmentFlag.AlignCenter,
            info,
        )

        painter.end()

        pixmap = QPixmap.fromImage(img)
        if getattr(self, '_atlas_pixmap_item', None) is None:
            self._atlas_pixmap_item = self.atlas_scene.addPixmap(pixmap)
        else:
            self._atlas_pixmap_item.setPixmap(pixmap)
            
        self.atlas_scene.setSceneRect(QRectF(pixmap.rect()))

    # =================================================================== #
    #  Language Refresh                                                     #
    # =================================================================== #

    def _refresh_all_labels(self) -> None:
        """Re-apply all i18n labels after a language switch."""
        self.setWindowTitle(self._i18n.t("app_title"))

        # Toolbar
        self.act_load_font.setText(self._i18n.t("load_font"))
        self.act_load_project.setText(self._i18n.t("load_project"))
        self.act_save_project.setText(self._i18n.t("save_project"))
        self.act_export.setText(self._i18n.t("export"))
        self.act_lang.setText(self._i18n.t("language"))

        # Left panel
        self.lbl_glyph_table.setText(self._i18n.t("glyph_table"))
        self.search_edit.setPlaceholderText(self._i18n.t("search_placeholder"))
        self._populate_filter_combo()

        # Refresh the table header (model emits headerDataChanged implicitly on reset)
        self._glyph_model.beginResetModel()
        self._glyph_model.endResetModel()

        # Center panel
        self.lbl_preview_title.setText(self._i18n.t("preview_title"))
        self.preview_input.setPlaceholderText(self._i18n.t("preview_input"))
        self.lbl_atlas_title.setText(self._i18n.t("atlas_title"))
        self.btn_zoom_in.setText(self._i18n.t("zoom_in"))
        self.btn_zoom_out.setText(self._i18n.t("zoom_out"))
        self.btn_zoom_fit.setText(self._i18n.t("zoom_fit"))
        self._rebuild_preset_buttons()

        # Right panel
        self.lbl_adjust_title.setText(self._i18n.t("adjust_title"))
        self.lbl_x_off.setText(f'{self._i18n.t("x_offset")}: {self.slider_x.value()}')
        self.lbl_y_off.setText(f'{self._i18n.t("y_offset")}: {self.slider_y.value()}')
        self.lbl_scale.setText(f'{self._i18n.t("scale")}: {self.slider_scale.value()}%')
        self.btn_reset.setText(self._i18n.t("reset"))
        self.btn_apply_category.setText(self._i18n.t("apply_category"))

        # Status bar
        self._update_status_bar()


# =========================================================================== #
#  Entry Point                                                                 #
# =========================================================================== #

def main() -> None:
    """Launch the TGlyph application."""
    # Force English locale so numbers (e.g. in QSpinBox) use Arabic numerals
    from PyQt6.QtCore import QLocale
    QLocale.setDefault(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(build_stylesheet())

    # Set application-wide font that supports Thai
    app_font = QFont("Segoe UI", 10)
    app_font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(app_font)

    # Set application window icon
    app.setWindowIcon(QIcon(str(_SCRIPT_DIR / "Logo.png")))

    # Show startup dialog
    startup = StartupDialog()
    if startup.exec() != QDialog.DialogCode.Accepted:
        sys.exit(0)

    font_path = startup.get_font_path()
    base_image_path = startup.get_base_image_path()
    cell_size = startup.get_cell_size()

    window = TGlyphApp(
        font_path=font_path,
        base_image_path=base_image_path,
        cell_size=cell_size,
    )
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
