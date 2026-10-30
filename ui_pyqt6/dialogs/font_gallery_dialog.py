import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QWidget, QFrame, QGridLayout, QSizePolicy, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont
from core.font_service import FontService


class FontGalleryDialog(QDialog):
    """
    Rich visual font gallery dialog.
    Allows browsing all 15 curated PUA font families with high-definition preview cards,
    engine filtering, and one-click selection for AI Helper and Project deployment.
    """

    font_selected = pyqtSignal(str)

    def __init__(self, current_engine="Unreal Engine", active_font_id="prompt", active_variant_rel=None, parent=None):
        super().__init__(parent)
        self.current_engine = current_engine or "Unreal Engine"
        self.active_font_id = active_font_id or "prompt"
        self.active_variant_rel = active_variant_rel
        self.selected_font_id = self.active_font_id
        self.selected_variant = None

        self.font_service = FontService()
        self.all_fonts = self.font_service.get_all_fonts()

        self.setWindowTitle("🔤 คลังฟอนต์เกมภาษาไทย - Thai Game Font Library & PUA")
        self.resize(980, 720)
        self.setMinimumSize(850, 600)

        self._filter_mode = "engine"  # default filter: engine recommended
        self._filter_buttons = {}
        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 16, 20, 18)
        main_layout.setSpacing(12)

        # 1. Header Banner
        header = QFrame()
        header.setProperty("class", "ContentBanner")
        h_layout = QVBoxLayout(header)
        h_layout.setContentsMargins(14, 10, 14, 10)
        h_layout.setSpacing(4)

        lbl_title = QLabel("🔤 คลังฟอนต์เกมภาษาไทยพร้อมชุด PUA เลื่อนสระวรรณยุกต์ (2,208 Glyphs)")
        lbl_title.setStyleSheet("color: #c084fc; font-size: 16px; font-weight: bold;")
        h_layout.addWidget(lbl_title)

        lbl_sub = QLabel("ฟอนต์ทุกชุดผ่านการจัดทำตำแหน่งสระลอย/สระจม และแปลง PUA เรียบร้อยแล้ว พร้อมนำไปสร้าง SDF หรือแปลงไฟล์ข้อความเข้าสู่ Game Engine ทันที")
        lbl_sub.setProperty("class", "Muted")
        lbl_sub.setStyleSheet("font-size: 11px;")
        lbl_sub.setWordWrap(True)
        h_layout.addWidget(lbl_sub)

        main_layout.addWidget(header)

        # 2. Filter Bar
        filter_bar = QHBoxLayout()
        filter_bar.setSpacing(8)

        lbl_filter = QLabel("🔍 กรองตาม:")
        lbl_filter.setProperty("class", "CardTitle")
        filter_bar.addWidget(lbl_filter)

        filters = [
            ("engine", f"⭐ แนะนำสำหรับ {self.current_engine}"),
            ("all", f"🌟 ทั้งหมด ({len(self.all_fonts)} ตระกูล)"),
            ("loopless", "✨ ไร้หัว (Loopless / UI สมัยใหม่)"),
            ("unreal", "⚡ Unreal Engine"),
            ("unity", "🧩 Unity (TMP)"),
            ("re_engine", "🧟 RE Engine (Capcom)"),
            ("fantasy", "📜 แฟนตาซี / ย้อนยุค / ลายมือ")
        ]

        for key, text in filters:
            btn = QPushButton(text)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, k=key: self._set_filter(k))
            filter_bar.addWidget(btn)
            self._filter_buttons[key] = btn

        filter_bar.addStretch()
        main_layout.addLayout(filter_bar)
        self._refresh_filter_styles()

        # 3. Scrollable Grid of Font Cards
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")

        self.cards_container = QWidget()
        self.cards_layout = QGridLayout(self.cards_container)
        self.cards_layout.setContentsMargins(12, 12, 12, 12)
        self.cards_layout.setSpacing(14)

        self._render_cards()
        scroll_area.setWidget(self.cards_container)
        main_layout.addWidget(scroll_area, stretch=1)

        # 4. Bottom Action Bar
        bottom_bar = QHBoxLayout()
        bottom_bar.setSpacing(10)

        lbl_note = QLabel("💡 คลิกปุ่ม 'เลือกใช้งาน' เพื่อนำฟอนต์ไปใช้ใน Master Prompt และเตรียมติดตั้งลงโปรเจกต์")
        lbl_note.setProperty("class", "SubText")
        lbl_note.setStyleSheet("font-size: 11px; font-style: italic;")
        bottom_bar.addWidget(lbl_note)
        bottom_bar.addStretch()

        btn_close = QPushButton("ปิดหน้าต่าง")
        btn_close.setProperty("class", "BtnSecondary")
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.clicked.connect(self.reject)
        bottom_bar.addWidget(btn_close)

        main_layout.addLayout(bottom_bar)

    def _set_filter(self, filter_key):
        self._filter_mode = filter_key
        self._refresh_filter_styles()
        self._render_cards()

    def _refresh_filter_styles(self):
        active_style = """
            QPushButton {
                background-color: #8b5cf6;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 5px 12px;
                font-size: 11px;
                font-weight: bold;
            }
        """
        for k, btn in self._filter_buttons.items():
            if k == self._filter_mode:
                btn.setStyleSheet(active_style)
            else:
                btn.setStyleSheet("")
                btn.setProperty("class", "BtnSecondary")
                btn.style().unpolish(btn)
                btn.style().polish(btn)

    def _render_cards(self):
        # Clear existing cards
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Determine filtered fonts
        if self._filter_mode == "engine":
            fonts_to_show = self.font_service.get_fonts_for_engine(self.current_engine)
        elif self._filter_mode == "loopless":
            loopless_ids = ["noto_sans_thai", "prompt", "kanit", "bai_jamjuree", "ibm_plex_sans_thai", "google_sans", "line_seed_sans_th", "chakra_petch"]
            fonts_to_show = [f for f in self.all_fonts if f.get("id") in loopless_ids or "loopless" in f.get("category", "").lower()]
        elif self._filter_mode == "unreal":
            fonts_to_show = self.font_service.get_fonts_for_engine("Unreal Engine")
        elif self._filter_mode == "unity":
            fonts_to_show = self.font_service.get_fonts_for_engine("Unity")
        elif self._filter_mode == "re_engine":
            fonts_to_show = self.font_service.get_fonts_for_engine("RE Engine")
        elif self._filter_mode == "fantasy":
            fantasy_ids = ["charm", "charmonman", "pridi", "sriracha", "sarabun", "cts_rattikal", "chonburi"]
            fonts_to_show = [f for f in self.all_fonts if f.get("id") in fantasy_ids]
        else:  # all
            fonts_to_show = self.all_fonts

        # 2-column grid layout
        col_count = 2
        for idx, f_info in enumerate(fonts_to_show):
            row = idx // col_count
            col = idx % col_count
            card = self._create_font_card(f_info)
            self.cards_layout.addWidget(card, row, col)

    def _create_font_card(self, f_info):
        card = QFrame()
        is_active = (f_info.get("id") == self.active_font_id)
        card.setProperty("class", "InnerCard")
        if is_active:
            card.setStyleSheet("border: 2px solid #a855f7;")

        c_layout = QVBoxLayout(card)
        c_layout.setContentsMargins(10, 10, 10, 10)
        c_layout.setSpacing(6)

        # Retrieve available variants for this font family
        variants = self.font_service.get_font_variants(f_info.get("id"))

        # 1. Preview Image (High-DPI 16:9 Specimen)
        lbl_img = QLabel()
        lbl_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_img.setFixedHeight(230)
        lbl_img.setProperty("class", "SegmentBox")
        lbl_img.setCursor(Qt.CursorShape.PointingHandCursor)
        lbl_img.setToolTip("🔍 คลิกที่ภาพเพื่อดูตัวอย่างขยายระดับ Full HD (1080p)")

        preview_path = self.font_service.get_preview_path(f_info.get("id"))
        if preview_path and os.path.exists(preview_path):
            pix = QPixmap(preview_path)
            dpr = self.devicePixelRatioF() or 1.0
            target_w = int(450 * dpr)
            target_h = int(230 * dpr)
            scaled = pix.scaled(
                target_w, target_h,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            scaled.setDevicePixelRatio(dpr)
            lbl_img.setPixmap(scaled)
        else:
            lbl_img.setText("🖼️ ไม่มีภาพตัวอย่าง")
            lbl_img.setProperty("class", "SubText")
            lbl_img.setStyleSheet("font-size: 11px;")

        c_layout.addWidget(lbl_img)

        # 2. Header Row: Name, Variant Count, Score Tag
        h_row = QHBoxLayout()
        lbl_name = QLabel(f"{f_info.get('name_en')} ({f_info.get('name_th')})")
        lbl_name.setProperty("class", "CardTitle")
        h_row.addWidget(lbl_name)

        h_row.addStretch()

        if variants:
            lbl_v_count = QLabel(f"🏷️ {len(variants)} รูปแบบ")
            lbl_v_count.setStyleSheet("color: #38bdf8; font-size: 10px; font-weight: bold; background-color: rgba(56, 189, 248, 0.12); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 4px; padding: 2px 6px;")
            h_row.addWidget(lbl_v_count)

        score = f_info.get("engine_score")
        if score and score >= 90:
            lbl_score = QLabel(f"⭐ เหมาะมาก ({score}%)")
            lbl_score.setStyleSheet("color: #fbbf24; font-size: 10px; font-weight: bold; background-color: rgba(251, 191, 36, 0.15); border: 1px solid rgba(251, 191, 36, 0.4); border-radius: 4px; padding: 2px 6px;")
            h_row.addWidget(lbl_score)

        c_layout.addLayout(h_row)

        # 3. Category & Tone Row with HD button
        cat_row = QHBoxLayout()
        lbl_cat = QLabel(f"สไตล์: {f_info.get('category')}  •  {f_info.get('tone')}")
        lbl_cat.setStyleSheet("color: #38bdf8; font-size: 10px; font-weight: bold;")
        cat_row.addWidget(lbl_cat)

        cat_row.addStretch()

        btn_zoom = QPushButton("🔍 ดูรูปขยาย (HD)")
        btn_zoom.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_zoom.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #a78bfa;
                border: 1px solid rgba(167, 139, 250, 0.4);
                border-radius: 4px;
                padding: 2px 7px;
                font-size: 9px;
            }
            QPushButton:hover {
                background-color: rgba(167, 139, 250, 0.15);
                color: #c084fc;
            }
        """)
        cat_row.addWidget(btn_zoom)
        c_layout.addLayout(cat_row)

        # 4. Description TH
        lbl_desc = QLabel(f_info.get("description_th", ""))
        lbl_desc.setProperty("class", "Muted")
        lbl_desc.setStyleSheet("font-size: 10px;")
        lbl_desc.setWordWrap(True)
        lbl_desc.setFixedHeight(34)
        c_layout.addWidget(lbl_desc)

        # 5. Best For
        lbl_best = QLabel(f"🎯 จุดเด่น: {f_info.get('best_for', '')}")
        lbl_best.setStyleSheet("color: #a78bfa; font-size: 9px;")
        lbl_best.setWordWrap(True)
        c_layout.addWidget(lbl_best)

        # 6. Style selector dropdown on card
        style_box = QHBoxLayout()
        style_box.setSpacing(6)
        lbl_s_prompt = QLabel("สไตล์/น้ำหนัก:")
        lbl_s_prompt.setStyleSheet("color: #94a3b8; font-size: 10px; font-weight: bold;")
        style_box.addWidget(lbl_s_prompt)

        cbo_card_style = QComboBox()
        cbo_card_style.setStyleSheet("""
            QComboBox {
                background-color: #1e293b;
                color: #f1f5f9;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 3px 8px;
                font-size: 10px;
            }
            QComboBox QAbstractItemView {
                background-color: #0f172a;
                color: #f1f5f9;
                selection-background-color: #7c3aed;
            }
        """)
        card_selected_idx = 0
        for v_idx, v in enumerate(variants):
            label = v.get("display_th", v.get("style_name"))
            if v.get("is_default"):
                label += " (ค่าเริ่มต้น)"
            cbo_card_style.addItem(label, v)
            if is_active and self.active_variant_rel and v.get("rel_path") == self.active_variant_rel:
                card_selected_idx = v_idx
        cbo_card_style.setCurrentIndex(card_selected_idx)
        style_box.addWidget(cbo_card_style, stretch=1)
        c_layout.addLayout(style_box)

        # Dynamic card image updater when switching style
        def _update_card_image(var_data):
            v_rel = var_data.get("rel_path") if isinstance(var_data, dict) else None
            p_path = self.font_service.get_preview_path(f_info.get("id"), variant_rel_path=v_rel)
            if p_path and os.path.exists(p_path):
                pix = QPixmap(p_path)
                dpr = self.devicePixelRatioF() or 1.0
                target_w = int(450 * dpr)
                target_h = int(230 * dpr)
                scaled = pix.scaled(
                    target_w, target_h,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                scaled.setDevicePixelRatio(dpr)
                lbl_img.setPixmap(scaled)

        cbo_card_style.currentIndexChanged.connect(lambda idx, cbo=cbo_card_style: _update_card_image(cbo.currentData()))
        if is_active and self.active_variant_rel:
            _update_card_image(cbo_card_style.currentData())

        # Hook image click and zoom button with selected variant and matching preview
        def _open_hd_for_card(cbo=cbo_card_style, info=f_info):
            v_data = cbo.currentData()
            v_rel = v_data.get("rel_path") if isinstance(v_data, dict) else None
            p_path = self.font_service.get_preview_path(info.get("id"), variant_rel_path=v_rel)
            self._open_hd_viewer(info, p_path, initial_variant=v_data)

        lbl_img.mousePressEvent = lambda e: _open_hd_for_card()
        btn_zoom.clicked.connect(lambda checked: _open_hd_for_card())

        # 7. Action Button
        btn_select = QPushButton("✅ ฟอนต์ที่เลือกอยู่" if is_active else "👉 เลือกใช้งานฟอนต์นี้")
        if is_active:
            btn_select.setStyleSheet("""
                QPushButton {
                    background-color: #10b981;
                    color: #ffffff;
                    border: none;
                    border-radius: 6px;
                    padding: 5px 12px;
                    font-size: 11px;
                    font-weight: bold;
                }
            """)
        else:
            btn_select.setProperty("class", "BtnSecondary")
            btn_select.setStyleSheet("font-size: 11px; font-weight: bold;")
        btn_select.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_select.clicked.connect(lambda checked, fid=f_info.get("id"), cbo=cbo_card_style: self._select_font(fid, cbo.currentData()))
        c_layout.addWidget(btn_select)

        return card

    def _open_hd_viewer(self, font_info, preview_path, initial_variant=None):
        from ui_pyqt6.dialogs.font_hd_viewer import FontHdViewerDialog
        dlg = FontHdViewerDialog(font_info, preview_path, initial_variant=initial_variant, parent=self)
        dlg.font_chosen.connect(self._select_font)
        dlg.font_chosen_variant.connect(self._select_font)
        dlg.exec()

    def _select_font(self, font_id, variant=None):
        self.selected_font_id = font_id
        self.selected_variant = variant
        self.font_selected.emit(font_id)
        self.accept()
