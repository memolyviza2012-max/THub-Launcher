"""
TStudio Custom Item Delegates
- StatusPillDelegate: Renders clean status badges (Translated, Pending, CJK Leak)
- TagIconDelegate: Renders circular category icons for Glossary (Person, Location, Weapon, Item, etc.)
- HtmlDelegate: High-performance & safe HTML span rendering for Glossary Term Highlights
"""
import re
from PyQt6.QtWidgets import QStyledItemDelegate, QStyle, QStyleOptionViewItem
from PyQt6.QtGui import QTextDocument, QAbstractTextDocumentLayout, QPainter, QColor, QFont, QPen, QBrush
from PyQt6.QtCore import QSize, Qt, QRect

class StatusPillDelegate(QStyledItemDelegate):
    """
    Renders clean status badges:
    - Translated: Green circle with checkmark ✔
    - Pending: Gray outline circle ◯
    - CJK Leak: Peach badge 🇨🇳
    """
    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(self, painter, option, index):
        if option.state & QStyle.StateFlag.State_Selected:
            painter.fillRect(option.rect, QColor("#2a2b3d"))
            painter.fillRect(QRect(option.rect.x(), option.rect.y(), 3, option.rect.height()), QColor("#89b4fa"))
        elif option.state & QStyle.StateFlag.State_MouseOver:
            painter.fillRect(option.rect, QColor("#1e1e2e"))

        status_type = index.model().data(index, Qt.ItemDataRole.UserRole)
        if status_type is None:
            status_type = index.model().data(index, Qt.ItemDataRole.DisplayRole)

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = option.rect
        center_x = rect.x() + rect.width() // 2
        center_y = rect.y() + rect.height() // 2

        if status_type == "cjk":
            badge_w = 60
            badge_h = 20
            bx = center_x - badge_w // 2
            by = center_y - badge_h // 2
            painter.setBrush(QBrush(QColor("#fab387")))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(bx, by, badge_w, badge_h, 6, 6)
            painter.setPen(QPen(QColor("#11111b")))
            f = painter.font()
            f.setPointSize(9)
            f.setBold(True)
            painter.setFont(f)
            painter.drawText(QRect(bx, by, badge_w, badge_h), Qt.AlignmentFlag.AlignCenter, "🇨🇳 จีนหลุด")
        elif status_type == "translated":
            # Green circle with checkmark
            radius = 9
            painter.setBrush(QBrush(QColor("#a6e3a1")))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)
            painter.setPen(QPen(QColor("#11111b")))
            f = painter.font()
            f.setPointSize(10)
            f.setBold(True)
            painter.setFont(f)
            painter.drawText(QRect(center_x - radius, center_y - radius, radius * 2, radius * 2), Qt.AlignmentFlag.AlignCenter, "✔")
        else:
            # Pending: Gray outline circle
            radius = 8
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(QColor("#585b70"), 1.5))
            painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)

        painter.restore()


class TagIconDelegate(QStyledItemDelegate):
    """
    Renders Icon-Only circular badges for the Glossary Tag column:
    - Person: 👤 (Orange)
    - Location: 📍 (Green)
    - Faction: 🛡️ (Purple)
    - Weapon: ⚔️ (Red/Rose)
    - Item: 💎 (Cyan)
    - General / Other: 🌐 (Slate)
    Saves ~80px horizontal space, expanding term & target columns!
    """
    TAG_MAP = {
        "Person": ("👤", "#fab387", "#11111b", "บุคคล / ตัวละคร (Person)"),
        "Location": ("📍", "#a6e3a1", "#11111b", "สถานที่ / โลก (Location)"),
        "Faction": ("🛡️", "#cba6f7", "#11111b", "ฝ่าย / กิลด์ / ตระกูล (Faction)"),
        "Weapon": ("⚔️", "#f38ba8", "#11111b", "อาวุธ (Weapon)"),
        "Item": ("💎", "#89b4fa", "#11111b", "ไอเทม / วัตถุดิบ (Item)"),
        "Quest": ("📜", "#f9e2af", "#11111b", "ภารกิจ (Quest)"),
        "General": ("🌐", "#45475a", "#cdd6f4", "ทั่วไป (General)"),
        "Other": ("🏷️", "#585b70", "#cdd6f4", "อื่นๆ (Other)")
    }

    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(self, painter, option, index):
        if option.state & QStyle.StateFlag.State_Selected:
            painter.fillRect(option.rect, QColor("#2a2b3d"))
        elif option.state & QStyle.StateFlag.State_MouseOver:
            painter.fillRect(option.rect, QColor("#1e1e2e"))

        tag_name = index.model().data(index, Qt.ItemDataRole.DisplayRole) or "General"
        icon_str, bg_color_hex, fg_color_hex, tooltip_text = self.TAG_MAP.get(
            tag_name, ("🏷️", "#585b70", "#cdd6f4", tag_name)
        )

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = option.rect
        center_x = rect.x() + rect.width() // 2
        center_y = rect.y() + rect.height() // 2
        size = 22
        bx = center_x - size // 2
        by = center_y - size // 2

        # Draw circle badge
        painter.setBrush(QBrush(QColor(bg_color_hex)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(bx, by, size, size, size // 2, size // 2)

        # Draw icon
        painter.setPen(QPen(QColor(fg_color_hex)))
        f = painter.font()
        f.setPointSize(10)
        painter.setFont(f)
        painter.drawText(QRect(bx, by, size, size), Qt.AlignmentFlag.AlignCenter, icon_str)

        painter.restore()


class HtmlDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._doc = None
        self._in_paint = False

    def _get_doc(self):
        if self._doc is None:
            self._doc = QTextDocument()
            self._doc.setDefaultStyleSheet("body { color: #cdd6f4; font-family: inherit; font-size: 13px; }")
            self._doc.setDocumentMargin(4)
        return self._doc

    def paint(self, painter, option, index):
        if getattr(self, '_in_paint', False):
            try:
                super().paint(painter, option, index)
            except Exception:
                pass
            return

        self._in_paint = True
        try:
            options = QStyleOptionViewItem(option)
            self.initStyleOption(options, index)
            text = options.text

            # FAST PATH: If cell is empty or does not contain html tags, use native Qt renderer
            if not text or "<span" not in text:
                super().paint(painter, option, index)
                return

            # SLOW PATH: Render highlighted HTML spans safely
            painter.save()
            try:
                # Draw background
                bg = index.data(Qt.ItemDataRole.BackgroundRole)
                if bg:
                    painter.fillRect(option.rect, bg)
                    
                # Draw selection
                if option.state & QStyle.StateFlag.State_Selected:
                    painter.fillRect(option.rect, option.palette.highlight())

                doc = self._get_doc()
                doc.clear()
                target_width = max(10, option.rect.width())
                doc.setTextWidth(target_width)
                doc.setHtml(f"<body>{text}</body>")

                painter.translate(option.rect.left(), option.rect.top())
                clip = option.rect.translated(-option.rect.left(), -option.rect.top())
                painter.setClipRect(clip)

                ctx = QAbstractTextDocumentLayout.PaintContext()
                ctx.palette = option.palette
                doc.documentLayout().draw(painter, ctx)
            finally:
                painter.restore()
        except Exception:
            # Bulletproof fallback: Never allow an exception in delegate paint to abort Qt
            try:
                super().paint(painter, option, index)
            except Exception:
                pass
        finally:
            self._in_paint = False

    def sizeHint(self, option, index):
        try:
            return super().sizeHint(option, index)
        except Exception:
            return QSize(100, 28)
