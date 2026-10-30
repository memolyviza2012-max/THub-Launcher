import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QSizePolicy, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QIcon
from core.font_service import FontService


class FontHdViewerDialog(QDialog):
    """
    High-Definition (Full HD 1080p) Font Specimen Viewer Modal.
    Displays crystal-clear typography specimens with dynamic DPI scaling,
    detailed engine info, inline font & variant switcher, and one-click selection.
    """

    font_chosen = pyqtSignal(str)
    font_chosen_variant = pyqtSignal(str, object)
    open_gallery_requested = pyqtSignal()

    def __init__(self, font_info, preview_path=None, initial_variant=None, parent=None, current_engine=None):
        super().__init__(parent)
        self.font_info = font_info or {}
        self.current_engine = current_engine or getattr(parent, "_current_engine_name", None) or getattr(parent, "current_engine", None)
        self.current_font_id = self.font_info.get("id", "prompt")
        self.preview_path = preview_path or ""
        self.initial_variant = initial_variant
        self.selected_variant = initial_variant
        self._pixmap_orig = None

        self.font_service = FontService()
        self.all_fonts = self.font_service.get_fonts_for_engine(self.current_engine)
        self.variants = self.font_service.get_font_variants(self.current_font_id)

        name_en = self.font_info.get("name_en", "Font")
        name_th = self.font_info.get("name_th", "")
        self.setWindowTitle(f"🔍 {name_en} ({name_th}) — ตัวอย่างฟอนต์ความละเอียดสูง Full HD (1080p)")
        self.resize(1200, 780)
        self.setMinimumSize(920, 600)
        self.setStyleSheet("background-color: #0b0f19; color: #e2e8f0;")

        self._load_pixmap()
        self._build_ui()

    def _load_pixmap(self):
        if self.preview_path and os.path.exists(self.preview_path):
            self._pixmap_orig = QPixmap(self.preview_path)
        else:
            self._pixmap_orig = None

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(18, 14, 18, 16)
        main_layout.setSpacing(10)

        # 1. Top Bar: Font Selector, Switcher Buttons (◀ / ▶), Badges, Hint
        top_bar = QHBoxLayout()
        top_bar.setSpacing(10)

        lbl_font_title = QLabel("🔤 เลือกฟอนต์:")
        lbl_font_title.setStyleSheet("color: #38bdf8; font-size: 13px; font-weight: bold;")
        top_bar.addWidget(lbl_font_title)

        # Prev Font Button
        self.btn_prev_font = QPushButton("◀")
        self.btn_prev_font.setToolTip("ฟอนต์ก่อนหน้า (กด Left Arrow ◀ บนคีย์บอร์ด)")
        self.btn_prev_font.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_prev_font.setFixedSize(32, 30)
        self.btn_prev_font.setStyleSheet("""
            QPushButton {
                background-color: #1e293b;
                color: #cbd5e1;
                border: 1px solid #475569;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #334155;
                color: #38bdf8;
                border-color: #38bdf8;
            }
        """)
        self.btn_prev_font.clicked.connect(self._prev_font)
        top_bar.addWidget(self.btn_prev_font)

        # Font Family ComboBox
        self.cbo_font_family = QComboBox()
        self.cbo_font_family.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cbo_font_family.setStyleSheet("""
            QComboBox {
                background-color: #1e293b;
                color: #f8fafc;
                border: 1px solid #6366f1;
                border-radius: 6px;
                padding: 4px 12px;
                font-size: 12px;
                font-weight: bold;
                min-width: 310px;
            }
            QComboBox:hover {
                border-color: #818cf8;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #0f172a;
                color: #f8fafc;
                selection-background-color: #4f46e5;
                selection-color: #ffffff;
                padding: 4px;
            }
        """)
        self._populate_font_families()
        self.cbo_font_family.currentIndexChanged.connect(self._on_font_family_changed)
        top_bar.addWidget(self.cbo_font_family)

        # Next Font Button
        self.btn_next_font = QPushButton("▶")
        self.btn_next_font.setToolTip("ฟอนต์ถัดไป (กด Right Arrow ▶ บนคีย์บอร์ด)")
        self.btn_next_font.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_next_font.setFixedSize(32, 30)
        self.btn_next_font.setStyleSheet("""
            QPushButton {
                background-color: #1e293b;
                color: #cbd5e1;
                border: 1px solid #475569;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #334155;
                color: #38bdf8;
                border-color: #38bdf8;
            }
        """)
        self.btn_next_font.clicked.connect(self._next_font)
        top_bar.addWidget(self.btn_next_font)

        # Category Badge
        self.lbl_cat = QLabel()
        self.lbl_cat.setStyleSheet("background-color: #1e293b; color: #c084fc; border: 1px solid #a855f7; border-radius: 4px; padding: 3px 8px; font-size: 11px; font-weight: bold;")
        top_bar.addWidget(self.lbl_cat)

        # Tone Badge
        self.lbl_tone = QLabel()
        self.lbl_tone.setStyleSheet("background-color: #0f2744; color: #60a5fa; border: 1px solid #3b82f6; border-radius: 4px; padding: 3px 8px; font-size: 11px;")
        top_bar.addWidget(self.lbl_tone)

        # Variants Count Badge
        self.lbl_var_badge = QLabel()
        self.lbl_var_badge.setStyleSheet("background-color: #064e3b; color: #34d399; border: 1px solid #059669; border-radius: 4px; padding: 3px 8px; font-size: 11px; font-weight: bold;")
        top_bar.addWidget(self.lbl_var_badge)

        top_bar.addStretch()

        lbl_hint = QLabel("💡 ใช้ปุ่ม ◀ / ▶ เปลี่ยนฟอนต์ | Esc ปิด")
        lbl_hint.setStyleSheet("color: #64748b; font-size: 11px;")
        top_bar.addWidget(lbl_hint)

        main_layout.addLayout(top_bar)

        # 2. Main Image Area (High-DPI View)
        self.img_frame = QFrame()
        self.img_frame.setStyleSheet("background-color: #080c14; border: 1px solid #1e293b; border-radius: 8px;")
        img_layout = QVBoxLayout(self.img_frame)
        img_layout.setContentsMargins(4, 4, 4, 4)

        self.lbl_image = QLabel()
        self.lbl_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_image.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        img_layout.addWidget(self.lbl_image)

        main_layout.addWidget(self.img_frame, stretch=1)

        # 3. Bottom Bar: Specs & Actions
        bot_bar = QHBoxLayout()
        bot_bar.setSpacing(10)

        self.lbl_best = QLabel()
        self.lbl_best.setStyleSheet("color: #fbbf24; font-size: 11px; font-weight: bold;")
        bot_bar.addWidget(self.lbl_best)

        bot_bar.addStretch()

        # Style / Weight Selector
        self.lbl_style = QLabel("รูปแบบ / น้ำหนัก:")
        self.lbl_style.setStyleSheet("color: #cbd5e1; font-size: 11px; font-weight: bold;")
        bot_bar.addWidget(self.lbl_style)

        self.cbo_style = QComboBox()
        self.cbo_style.setStyleSheet("""
            QComboBox {
                background-color: #1e293b;
                color: #f1f5f9;
                border: 1px solid #475569;
                border-radius: 6px;
                padding: 5px 12px;
                font-size: 11px;
                min-width: 190px;
            }
            QComboBox:hover {
                border-color: #38bdf8;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #0f172a;
                color: #f1f5f9;
                selection-background-color: #7c3aed;
                selection-color: #ffffff;
            }
        """)
        self.cbo_style.currentIndexChanged.connect(self._on_style_switched)
        bot_bar.addWidget(self.cbo_style)

        # Gallery button
        btn_gallery = QPushButton("🖼️ ดูคลังฟอนต์ทั้งหมด")
        btn_gallery.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_gallery.setStyleSheet("""
            QPushButton {
                background-color: #1e293b;
                color: #cbd5e1;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 7px 14px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #334155;
                color: #ffffff;
            }
        """)
        btn_gallery.clicked.connect(self._on_open_gallery)
        bot_bar.addWidget(btn_gallery)

        # Select Font Button
        btn_select = QPushButton("👉 เลือกฟอนต์นี้")
        btn_select.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_select.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 7px 18px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        btn_select.clicked.connect(self._on_select_font)
        bot_bar.addWidget(btn_select)

        # Close Button
        btn_close = QPushButton("✕ ปิด")
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #94a3b8;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 7px 14px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #1e293b;
                color: #ffffff;
            }
        """)
        btn_close.clicked.connect(self.reject)
        bot_bar.addWidget(btn_close)

        main_layout.addLayout(bot_bar)

        # Initialize current font details into UI
        self._update_font_display(preserve_weight=False)

    def _populate_font_families(self):
        self.cbo_font_family.blockSignals(True)
        self.cbo_font_family.clear()

        fonts = self.font_service.get_fonts_for_engine(self.current_engine)
        self.all_fonts = fonts

        sel_idx = 0
        for idx, f in enumerate(fonts):
            star = "⭐ " if f.get("is_recommended") else ""
            score = f.get("engine_score")
            score_str = f"[{score}%] " if score is not None else ""
            label = f"{star}{score_str}{f.get('name_en')} ({f.get('name_th', '')})"
            self.cbo_font_family.addItem(label, f.get("id"))
            if f.get("id") == self.current_font_id:
                sel_idx = idx

        self.cbo_font_family.setCurrentIndex(sel_idx)
        self.cbo_font_family.blockSignals(False)

    def _update_font_display(self, preserve_weight=True):
        name_en = self.font_info.get("name_en", "Font")
        name_th = self.font_info.get("name_th", "")
        self.setWindowTitle(f"🔍 {name_en} ({name_th}) — ตัวอย่างฟอนต์ความละเอียดสูง Full HD (1080p)")

        cat = self.font_info.get("category", "")
        if cat:
            self.lbl_cat.setText(cat)
            self.lbl_cat.show()
        else:
            self.lbl_cat.hide()

        tone = self.font_info.get("tone", "")
        if tone:
            self.lbl_tone.setText(f"สไตล์: {tone}")
            self.lbl_tone.show()
        else:
            self.lbl_tone.hide()

        best_for = self.font_info.get("best_for", "")
        if best_for:
            self.lbl_best.setText(f"⭐ จุดเด่น: {best_for}")
            self.lbl_best.show()
        else:
            self.lbl_best.hide()

        self.variants = self.font_service.get_font_variants(self.current_font_id)
        if self.variants:
            self.lbl_var_badge.setText(f"🏷️ มีทั้งหมด {len(self.variants)} รูปแบบ / น้ำหนัก")
            self.lbl_var_badge.show()
            self.lbl_style.show()
            self.cbo_style.show()
        else:
            self.lbl_var_badge.hide()
            self.lbl_style.hide()
            self.cbo_style.hide()

        # Update Style combo
        prev_weight = self.selected_variant.get("weight") if (preserve_weight and self.selected_variant) else None
        prev_italic = self.selected_variant.get("is_italic") if (preserve_weight and self.selected_variant) else False

        self.cbo_style.blockSignals(True)
        self.cbo_style.clear()

        sel_var_idx = 0
        found_exact = False

        for idx, v in enumerate(self.variants):
            label = v.get("display_th", v.get("style_name"))
            if v.get("is_default"):
                label += " (ค่าเริ่มต้น)"
            self.cbo_style.addItem(label, v)

            # Variant matching logic
            if preserve_weight and prev_weight is not None:
                if v.get("weight") == prev_weight and v.get("is_italic") == prev_italic:
                    sel_var_idx = idx
                    found_exact = True
                elif v.get("weight") == prev_weight and not found_exact:
                    sel_var_idx = idx
            elif not preserve_weight and self.initial_variant:
                if v.get("rel_path") == self.initial_variant.get("rel_path") or v.get("file_name") == self.initial_variant.get("file_name"):
                    sel_var_idx = idx
                    found_exact = True
            elif not found_exact and v.get("is_default"):
                sel_var_idx = idx

        if self.cbo_style.count() > 0:
            self.cbo_style.setCurrentIndex(sel_var_idx)
            self.selected_variant = self.cbo_style.currentData()
        else:
            self.selected_variant = None

        self.cbo_style.blockSignals(False)

        # Update preview image
        self._refresh_preview_image()

    def _refresh_preview_image(self):
        v_rel = self.selected_variant.get("rel_path") if self.selected_variant else None
        new_p = self.font_service.get_preview_path(self.current_font_id, variant_rel_path=v_rel)
        if new_p and os.path.exists(new_p):
            self.preview_path = new_p
        self._load_pixmap()
        self._update_scaled_image()

    def _on_font_family_changed(self, index):
        fid = self.cbo_font_family.currentData()
        if not fid or fid == self.current_font_id:
            return
        self.current_font_id = fid
        self.font_info = self.font_service.get_font_by_id(fid) or {}
        self._update_font_display(preserve_weight=True)

    def _prev_font(self):
        count = self.cbo_font_family.count()
        if count <= 1:
            return
        curr = self.cbo_font_family.currentIndex()
        nxt = (curr - 1) % count
        self.cbo_font_family.setCurrentIndex(nxt)

    def _next_font(self):
        count = self.cbo_font_family.count()
        if count <= 1:
            return
        curr = self.cbo_font_family.currentIndex()
        nxt = (curr + 1) % count
        self.cbo_font_family.setCurrentIndex(nxt)

    def _on_style_switched(self):
        self.selected_variant = self.cbo_style.currentData()
        self._refresh_preview_image()

    def showEvent(self, event):
        super().showEvent(event)
        self._update_scaled_image()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_scaled_image()

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key.Key_Left:
            self._prev_font()
            event.accept()
            return
        elif key == Qt.Key.Key_Right:
            self._next_font()
            event.accept()
            return
        elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._on_select_font()
            event.accept()
            return
        elif key == Qt.Key.Key_Escape:
            self.reject()
            event.accept()
            return
        super().keyPressEvent(event)

    def _update_scaled_image(self):
        if not self._pixmap_orig or self._pixmap_orig.isNull():
            self.lbl_image.setText("🖼️ ไม่มีภาพตัวอย่าง")
            return

        w = self.img_frame.width() - 10
        h = self.img_frame.height() - 10
        if w < 100 or h < 100:
            return

        dpr = self.devicePixelRatioF() or 1.0
        target_w = int(w * dpr)
        target_h = int(h * dpr)

        scaled = self._pixmap_orig.scaled(
            target_w, target_h,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        scaled.setDevicePixelRatio(dpr)
        self.lbl_image.setPixmap(scaled)

    def _on_select_font(self):
        fid = self.current_font_id
        if hasattr(self, "cbo_style") and self.cbo_style.count() > 0:
            self.selected_variant = self.cbo_style.currentData()
        if fid:
            self.font_chosen.emit(fid)
            self.font_chosen_variant.emit(fid, self.selected_variant)
        self.accept()

    def _on_open_gallery(self):
        self.open_gallery_requested.emit()
        self.accept()
