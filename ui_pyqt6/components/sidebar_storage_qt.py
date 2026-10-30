import os
import math
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QProgressBar, QSizePolicy, QToolTip, QScrollArea
)
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPainterPath
from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal, QTimer
from i18n_helper import _
from core.project_storage_service import ProjectStorageService


class SidebarDonutWidget(QWidget):
    """
    Compact, antialiased circular donut chart engineered for the 230px Navigation Sidebar.
    Features hover slice explosion, dynamic centered metrics, and slice selection signals.
    """
    slice_clicked = pyqtSignal(dict)

    PALETTE = [
        QColor("#38bdf8"),  # Sky Blue
        QColor("#10b981"),  # Emerald
        QColor("#a855f7"),  # Purple
        QColor("#f59e0b"),  # Amber
        QColor("#ec4899"),  # Pink
        QColor("#06b6d4"),  # Cyan
        QColor("#64748b"),  # Slate (Others)
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setFixedSize(120, 120)
        self.data_items = []
        self.total_size = 0
        self.total_size_str = "0 B"
        self.hovered_index = -1

    def set_data(self, project_sizes):
        """Populates slices from project_sizes: list of (project_dict, size_bytes)."""
        self.total_size = sum(sz for _, sz in project_sizes)
        if self.total_size == 0:
            self.data_items = []
            self.total_size_str = "0 B"
            self.update()
            return

        sorted_items = sorted(project_sizes, key=lambda x: x[1], reverse=True)
        # Top 5 + Others
        top_items = sorted_items[:5]
        others = sorted_items[5:]

        self.data_items = []
        for i, (p, sz) in enumerate(top_items):
            pct = (sz / self.total_size) * 100
            color = self.PALETTE[i % len(self.PALETTE)]
            self.data_items.append({
                "name": p.get("name", "Unknown"),
                "size": sz,
                "size_str": ProjectStorageService.format_size(sz),
                "percent": pct,
                "color": color,
                "project": p
            })

        if others:
            other_sz = sum(sz for _, sz in others)
            pct = (other_sz / self.total_size) * 100
            self.data_items.append({
                "name": _(f"อื่นๆ ({len(others)} เกม)"),
                "size": other_sz,
                "size_str": ProjectStorageService.format_size(other_sz),
                "percent": pct,
                "color": self.PALETTE[-1],
                "project": None
            })

        self.total_size_str = ProjectStorageService.format_size(self.total_size)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        cx = w / 2.0
        cy = h / 2.0
        radius = min(w, h) / 2.0 - 6
        inner_radius = radius * 0.62

        if not self.data_items:
            painter.setPen(QPen(QColor("#334155"), 8))
            painter.drawEllipse(QPointF(cx, cy), radius * 0.8, radius * 0.8)
            painter.setPen(QColor("#64748b"))
            painter.setFont(QFont("Segoe UI", 8))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, _("ไม่มีข้อมูล"))
            return

        current_angle = 90.0

        for i, item in enumerate(self.data_items):
            span_angle = (item["percent"] / 100.0) * 360.0
            is_hovered = (i == self.hovered_index)

            slice_r = radius + (3 if is_hovered else 0)
            inner_r = inner_radius - (1 if is_hovered else 0)

            path = QPainterPath()
            outer_rect = QRectF(cx - slice_r, cy - slice_r, slice_r * 2, slice_r * 2)
            inner_rect = QRectF(cx - inner_r, cy - inner_r, inner_r * 2, inner_r * 2)

            path.arcMoveTo(outer_rect, current_angle)
            path.arcTo(outer_rect, current_angle, -span_angle)
            path.arcTo(inner_rect, current_angle - span_angle, span_angle)
            path.closeSubpath()

            fill_color = item["color"]
            if is_hovered:
                fill_color = fill_color.lighter(115)

            painter.setPen(QPen(QColor("#0f172a"), 1.5))
            painter.setBrush(QBrush(fill_color))
            painter.drawPath(path)

            current_angle -= span_angle

        # Draw Center Hole
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor("#090d16")))
        painter.drawEllipse(QPointF(cx, cy), inner_radius - 1, inner_radius - 1)

        # Draw Dynamic Center Text
        if 0 <= self.hovered_index < len(self.data_items):
            hov_item = self.data_items[self.hovered_index]
            painter.setPen(QColor(hov_item["color"]))
            painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            r_top = QRectF(cx - inner_radius, cy - 14, inner_radius * 2, 14)
            painter.drawText(r_top, Qt.AlignmentFlag.AlignCenter, hov_item["size_str"])

            painter.setPen(QColor("#94a3b8"))
            painter.setFont(QFont("Segoe UI", 7))
            r_bot = QRectF(cx - inner_radius, cy, inner_radius * 2, 12)
            painter.drawText(r_bot, Qt.AlignmentFlag.AlignCenter, f"{hov_item['percent']:.1f}%")
        else:
            painter.setPen(QColor("#38bdf8"))
            painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            r_top = QRectF(cx - inner_radius, cy - 14, inner_radius * 2, 14)
            painter.drawText(r_top, Qt.AlignmentFlag.AlignCenter, self.total_size_str)

            painter.setPen(QColor("#64748b"))
            painter.setFont(QFont("Segoe UI", 7))
            r_bot = QRectF(cx - inner_radius, cy, inner_radius * 2, 12)
            painter.drawText(r_bot, Qt.AlignmentFlag.AlignCenter, _("พื้นที่รวม"))

    def mouseMoveEvent(self, event):
        w = self.width()
        h = self.height()
        cx = w / 2.0
        cy = h / 2.0
        dx = event.position().x() - cx
        dy = event.position().y() - cy
        dist = math.hypot(dx, dy)

        radius = min(w, h) / 2.0 - 6
        inner_radius = radius * 0.62

        new_hover = -1
        if inner_radius <= dist <= radius + 6 and self.data_items:
            deg = math.degrees(math.atan2(dy, dx))
            clock_angle = (90 - deg) % 360
            curr = 0.0
            for i, item in enumerate(self.data_items):
                span = (item["percent"] / 100.0) * 360.0
                if curr <= clock_angle <= curr + span:
                    new_hover = i
                    break
                curr += span

        if new_hover != self.hovered_index:
            self.hovered_index = new_hover
            if 0 <= new_hover < len(self.data_items):
                item = self.data_items[new_hover]
                QToolTip.showText(event.globalPosition().toPoint(), f"{item['name']}: {item['size_str']} ({item['percent']:.1f}%)", self)
            else:
                QToolTip.hideText()
            self.update()

        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        self.hovered_index = -1
        QToolTip.hideText()
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and 0 <= self.hovered_index < len(self.data_items):
            item = self.data_items[self.hovered_index]
            if item.get("project"):
                self.slice_clicked.emit(item["project"])
        super().mousePressEvent(event)


class SidebarStorageWidget(QFrame):
    """
    Dedicated Sidebar Storage Widget positioned directly under 'Settings'.
    Engineered to fill the entire vertical height of that section.
    Features:
    - Quick Action Header (Sort & Refresh)
    - Centered Antialiased Donut Chart (with interactive slice explosion & center metrics)
    - Scrollable Top Storage Consumers List with ranks, color dots, micro progress bars, and click-to-select
    - Executive Summary Pill at the bottom
    - Hairline Scanning Progress Bar
    """
    project_selected = pyqtSignal(dict)
    sort_size_requested = pyqtSignal()
    refresh_requested = pyqtSignal()
    move_queue_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SidebarStorageWidget")
        self.setFixedWidth(202)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("""
            QFrame#SidebarStorageWidget {
                background-color: rgba(15, 23, 42, 0.75);
                border: 1px solid rgba(51, 65, 85, 0.55);
                border-radius: 8px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # 1. Header Row: [💾 พื้นที่จัดเก็บ]  [⚡] [🔄]
        hdr = QHBoxLayout()
        hdr.setContentsMargins(2, 0, 2, 0)
        hdr.setSpacing(4)

        lbl_icon = QLabel("💾")
        lbl_icon.setStyleSheet("font-size: 11px;")
        hdr.addWidget(lbl_icon)

        self.lbl_title = QLabel(_("พื้นที่จัดเก็บ"))
        self.lbl_title.setStyleSheet("color: #38bdf8; font-size: 11px; font-weight: bold;")
        hdr.addWidget(self.lbl_title)
        hdr.addStretch()

        btn_style_mini = """
            QPushButton {
                background: rgba(30, 41, 59, 0.6);
                color: #94a3b8;
                border: 1px solid #334155;
                border-radius: 4px;
                font-size: 10px;
                padding: 1px 3px;
                min-width: 18px;
                max-width: 18px;
                min-height: 18px;
                max-height: 18px;
            }
            QPushButton:hover {
                background: #1e293b;
                color: #38bdf8;
                border-color: #38bdf8;
            }
        """

        self.btn_move = QPushButton("🚚")
        self.btn_move.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_move.setToolTip(_("ย้ายโปรเจกต์ทั้งหมดหรือบางส่วนไปยังฮาร์ดดิสก์/ไดรฟ์อื่น (Queue Move)"))
        self.btn_move.setStyleSheet(btn_style_mini)
        self.btn_move.clicked.connect(self.move_queue_requested.emit)
        hdr.addWidget(self.btn_move)

        self.btn_sort = QPushButton("⚡")
        self.btn_sort.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_sort.setToolTip(_("เรียงโปรเจกต์ในการ์ดตามขนาดพื้นที่ (ใหญ่สุดไปเล็กสุด)"))
        self.btn_sort.setStyleSheet(btn_style_mini)
        self.btn_sort.clicked.connect(self.sort_size_requested.emit)
        hdr.addWidget(self.btn_sort)

        self.btn_refresh = QPushButton("🔄")
        self.btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_refresh.setToolTip(_("สแกนคำนวณขนาดพื้นที่ใหม่"))
        self.btn_refresh.setStyleSheet(btn_style_mini)
        self.btn_refresh.clicked.connect(self.refresh_requested.emit)
        hdr.addWidget(self.btn_refresh)

        layout.addLayout(hdr)

        # 2. Scanning Progress Bar (2px hairline)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setFixedHeight(2)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background: transparent;
                border: none;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10b981, stop:1 #38bdf8);
            }
        """)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        # 3. Donut Chart Centered (120x120)
        self.donut = SidebarDonutWidget(self)
        self.donut.slice_clicked.connect(self.project_selected.emit)
        layout.addWidget(self.donut, alignment=Qt.AlignmentFlag.AlignCenter)

        # 4. Scrollable Top Storage Consumers List (Fills remaining height)
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 4px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(100, 116, 139, 0.4);
                border-radius: 2px;
                min-height: 16px;
            }
            QScrollBar::handle:vertical:hover {
                background: #38bdf8;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar:horizontal {
                height: 0px;
                background: transparent;
            }
        """)

        self.top_items_container = QWidget()
        self.top_items_container.setStyleSheet("background: transparent;")
        self.top_items_layout = QVBoxLayout(self.top_items_container)
        self.top_items_layout.setContentsMargins(0, 0, 4, 0)
        self.top_items_layout.setSpacing(4)
        self.top_items_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.top_items_container)

        layout.addWidget(self.scroll_area, stretch=1)

        # 5. Executive Summary Pill at bottom
        self.lbl_summary_bar = QLabel("💾 0 GB • 0 โปรเจกต์")
        self.lbl_summary_bar.setStyleSheet("""
            color: #94a3b8;
            font-size: 10px;
            background: rgba(30, 41, 59, 0.55);
            border: 1px solid rgba(51, 65, 85, 0.4);
            border-radius: 4px;
            padding: 3px 6px;
        """)
        self.lbl_summary_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_summary_bar)

    def set_scanning(self, is_scanning):
        if not is_scanning:
            self.progress_bar.setVisible(False)
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(0)

    def set_progress(self, current, total):
        if not self.progress_bar.isVisible():
            self.progress_bar.show()
        self.progress_bar.setRange(0, max(1, total))
        self.progress_bar.setValue(current)

    def update_storage_data(self, project_sizes):
        """Populates Donut Chart and Scrollable Top Consumers list."""
        self.donut.set_data(project_sizes)

        # Clear existing rows
        while self.top_items_layout.count() > 0:
            item = self.top_items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not project_sizes:
            self.lbl_summary_bar.setText("💾 0 GB • 0 โปรเจกต์")
            return

        sorted_items = sorted(project_sizes, key=lambda x: x[1], reverse=True)
        total_b = sum(sz for _, sz in project_sizes)
        max_b = sorted_items[0][1] if sorted_items else 1

        # Populate top projects (up to 25 projects in scrollable list)
        for i, (p, sz) in enumerate(sorted_items[:25]):
            color = SidebarDonutWidget.PALETTE[i % len(SidebarDonutWidget.PALETTE)] if i < 6 else QColor("#64748b")
            pct = (sz / total_b * 100) if total_b > 0 else 0
            ratio = (sz / max_b) if max_b > 0 else 0

            row = QFrame()
            row.setCursor(Qt.CursorShape.PointingHandCursor)
            row.setStyleSheet("""
                QFrame {
                    background-color: rgba(15, 23, 42, 0.45);
                    border: 1px solid transparent;
                    border-radius: 4px;
                    padding: 2px 4px;
                }
                QFrame:hover {
                    background-color: rgba(30, 41, 59, 0.85);
                    border-color: #334155;
                }
            """)
            row.mousePressEvent = lambda e, prj=p: self.project_selected.emit(prj)

            r_lay = QVBoxLayout(row)
            r_lay.setContentsMargins(4, 2, 4, 2)
            r_lay.setSpacing(2)

            line1 = QHBoxLayout()
            line1.setSpacing(4)

            dot = QLabel("●")
            dot.setStyleSheet(f"color: {color.name()}; font-size: 9px;")
            line1.addWidget(dot)

            raw_name = p.get("name", "Unknown")
            short_name = raw_name if len(raw_name) <= 11 else raw_name[:10] + ".."
            lbl_name = QLabel(short_name)
            lbl_name.setMinimumWidth(0)
            lbl_name.setStyleSheet("color: #e2e8f0; font-size: 10px; font-weight: 500;")
            lbl_name.setToolTip(f"#{i+1} {raw_name}\nขนาด: {ProjectStorageService.format_size(sz)} ({pct:.1f}% ของพื้นที่ทั้งหมด)")
            line1.addWidget(lbl_name, stretch=1)

            lbl_sz = QLabel(ProjectStorageService.format_size(sz))
            lbl_sz.setStyleSheet("color: #94a3b8; font-size: 9px; font-weight: bold;")
            line1.addWidget(lbl_sz)

            r_lay.addLayout(line1)

            # Micro progress bar (2px)
            bar = QProgressBar()
            bar.setFixedHeight(2)
            bar.setTextVisible(False)
            bar.setRange(0, 1000)
            bar.setValue(int(ratio * 1000))
            bar.setStyleSheet(f"""
                QProgressBar {{
                    background-color: rgba(30, 41, 59, 0.8);
                    border: none;
                    border-radius: 1px;
                }}
                QProgressBar::chunk {{
                    background-color: {color.name()};
                    border-radius: 1px;
                }}
            """)
            r_lay.addWidget(bar)

            self.top_items_layout.addWidget(row)

        total_str = ProjectStorageService.format_size(total_b)
        proj_count = len(project_sizes)
        self.lbl_summary_bar.setText(f"💾 {total_str} • {proj_count} โปรเจกต์")
