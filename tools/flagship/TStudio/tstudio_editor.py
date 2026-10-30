"""
TStudio Column 3: Translation Workspace & Editor Stack Module
=============================================================
Encapsulates Tier 1 (Original Source), Tier 2 (AI Reference), and Tier 3 (My Translation Editor)
along with in-editor context menus, snippet selection tracking, and quick-action translation pills.
"""

import html
import json
import re
from PyQt6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QMenu, QCheckBox, QApplication,
    QMessageBox, QInputDialog
)
from PyQt6.QtCore import Qt, QTimer, QPoint, QObject
from PyQt6.QtGui import QAction, QCursor, QKeySequence

from flow_layout import FlowLayout
from tstudio_i18n import _
from tstudio_core import TStudioCore, CoreAI
from tstudio_ui_shared import ApiWorker, ThreadSafeWorkerSignalsForwarder
from tstudio_models import TransEditorEventFilter, SelectionTranslatePill


from translation_transport import TranslationGateway, snapshot_config, RowTarget

class Column3EditorWidget(QWidget):
    """Column 3 Editor Stack: 3-Tier CAT Translation Workspace."""

    def __init__(self, parent_window):
        super().__init__(parent_window)
        self.parent_window = parent_window

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 8, 10, 8)
        layout.setSpacing(6)

        # ── Tier 1: Original Source ──
        tier1_box = QFrame()
        tier1_box.setProperty("class", "editor-card")
        t1_layout = QVBoxLayout(tier1_box)
        t1_layout.setContentsMargins(8, 6, 8, 6)
        t1_layout.setSpacing(4)

        t1_header = QHBoxLayout()
        lbl_t1 = QLabel("1. <b>ต้นฉบับ (EN)</b>")
        lbl_t1.setToolTip("ข้อความภาษาอังกฤษต้นฉบับ")
        lbl_t1.setStyleSheet("color: #89b4fa; font-size: 12px;")
        t1_header.addWidget(lbl_t1)
        t1_header.addStretch(1)

        self.lbl_src_char_count = QLabel("0 ตัว")
        self.lbl_src_char_count.setStyleSheet("background: #11111b; color: #a6adc8; padding: 2px 6px; border-radius: 4px; font-size: 11px;")
        t1_header.addWidget(self.lbl_src_char_count)

        self.btn_copy_src = QPushButton("📋 คัดลอก")
        self.btn_copy_src.setStyleSheet("font-size: 11px; padding: 2px 6px;")
        self.btn_copy_src.clicked.connect(self.copy_source_to_clipboard)
        t1_header.addWidget(self.btn_copy_src)
        t1_layout.addLayout(t1_header)

        self.txt_source = QTextEdit()
        self.txt_source.setReadOnly(True)
        self.txt_source.setMaximumHeight(85)
        self.txt_source.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.txt_source.customContextMenuRequested.connect(self.show_source_context_menu)
        self.txt_source.selectionChanged.connect(lambda: self.on_text_selection_changed(self.txt_source))
        t1_layout.addWidget(self.txt_source)

        # Detected In-Context Glossary Chips
        self.glossary_chips_box = QWidget()
        self.glossary_chips_layout = FlowLayout(self.glossary_chips_box)
        self.glossary_chips_layout.setContentsMargins(0, 0, 0, 0)
        t1_layout.addWidget(self.glossary_chips_box)
        layout.addWidget(tier1_box)

        # ── Tier 2: AI Reference ──
        tier2_box = QFrame()
        tier2_box.setProperty("class", "editor-card")
        t2_layout = QVBoxLayout(tier2_box)
        t2_layout.setContentsMargins(8, 6, 8, 6)
        t2_layout.setSpacing(4)

        t2_header = QHBoxLayout()
        lbl_t2 = QLabel("2. <b>แปลโดย AI</b>")
        lbl_t2.setToolTip("ข้อความร่างคำแปลจาก AI")
        lbl_t2.setStyleSheet("color: #cba6f7; font-size: 12px;")
        t2_header.addWidget(lbl_t2)
        t2_header.addStretch(1)

        self.btn_use_draft = QPushButton("⬇ ใช้ร่าง")
        self.btn_use_draft.setToolTip("นำข้อความแปลร่างของ AI ไปใส่ในกล่องคำแปลของฉัน")
        self.btn_use_draft.setProperty("class", "btn-primary")
        self.btn_use_draft.setStyleSheet("font-size: 11px; padding: 3px 10px; font-weight: bold;")
        self.btn_use_draft.clicked.connect(self.apply_ai_ref_to_editor)
        t2_header.addWidget(self.btn_use_draft)
        t2_layout.addLayout(t2_header)

        self.txt_ai = QTextEdit()
        self.txt_ai.setReadOnly(True)
        self.txt_ai.setMaximumHeight(85)
        self.txt_ai.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.txt_ai.customContextMenuRequested.connect(self.show_ai_context_menu)
        t2_layout.addWidget(self.txt_ai)

        self.ai_cards_container = None
        self.ai_style_cards = []
        layout.addWidget(tier2_box)

        # ── Tier 3: My Translation ──
        tier3_box = QFrame()
        tier3_box.setProperty("class", "editor-card")
        t3_layout = QVBoxLayout(tier3_box)
        t3_layout.setContentsMargins(8, 6, 8, 6)
        t3_layout.setSpacing(4)

        t3_header = QHBoxLayout()
        lbl_t3 = QLabel("3. <b>คำแปลของฉัน</b>")
        lbl_t3.setToolTip("กล่องพิมพ์คำแปลภาษาไทย")
        lbl_t3.setStyleSheet("color: #a6e3a1; font-size: 12px;")
        t3_header.addWidget(lbl_t3)
        t3_header.addStretch(1)

        self.lbl_trans_char_count = QLabel("0 ตัว")
        self.lbl_trans_char_count.setStyleSheet("background: #11111b; color: #a6adc8; padding: 2px 6px; border-radius: 4px; font-size: 11px;")
        t3_header.addWidget(self.lbl_trans_char_count)

        self.btn_trans_smart = QPushButton("✨ แปล AI")
        self.btn_trans_smart.setToolTip("แปลบรรทัดนี้ด้วย AI (Ctrl+Enter / Ctrl+T)")
        self.btn_trans_smart.setObjectName("btnRetranslate")
        self.btn_trans_smart.setProperty("class", "btn-primary")
        self.btn_trans_smart.clicked.connect(self.parent_window.retranslate_smart)
        t3_header.addWidget(self.btn_trans_smart)

        self.btn_trans_special = QPushButton("⚙️ ▾")
        self.btn_trans_special.setToolTip("ตัวเลือกการแปลพิเศษและสไตล์เพิ่มเติม")
        self.btn_trans_special.setStyleSheet("background:#313244; color:#cdd6f4; font-size:12px; padding:4px 8px; font-weight:bold; border:1px solid #45475a; border-radius:6px;")
        self.btn_trans_special.clicked.connect(self.show_special_translation_menu_at_cursor)

        # Build special translation menu
        self.special_menu = QMenu(self)
        self.special_menu.setStyleSheet("QMenu { font-size: 13px; }")
        self.special_menu.addAction("✨ แปลเฉพาะข้อความที่ไฮไลต์ (Ctrl+Shift+T)").triggered.connect(lambda *args: self.translate_selected_snippet())
        self.special_menu.addAction("🗣️ แปลทับศัพท์เฉพาะส่วนที่เลือก (Ctrl+Shift+Y)").triggered.connect(lambda *args: self.translate_selected_snippet(mode="transliterate"))
        self.special_menu.addAction("💡 3 ตัวเลือกสำนวน (3 Options)").triggered.connect(lambda *args: self.translate_selected_snippet(style_choice=True))
        self.special_menu.addSeparator()
        self.special_menu.addAction("🎬 ขัดเกลาภาษาพูดภาพยนตร์ (Cinematic Polish) [Ctrl+Shift+P]").triggered.connect(self.parent_window.polish_selected_cinematic)
        self.special_menu.addAction("🩹 แปลซ่อมคำอังกฤษเฉพาะจุด (English Patch) [Ctrl+Shift+E]").triggered.connect(self.parent_window.patch_selected_english_leaks)
        self.special_menu.addAction("🇨🇳 ล้างคอมเมนต์ภาษาจีน (Clean CJK)").triggered.connect(self.parent_window.clean_selected_cjk)
        self.special_menu.addAction("🎖️ ซ่อมศัพท์อาวุธ & คีย์บอร์ด (0 Token) [Ctrl+Shift+M]...").triggered.connect(self.parent_window.open_military_retrofit_dialog)
        self.special_menu.addSeparator()

        sub_styles = self.special_menu.addMenu("🎨 สไตล์ภาษาเพิ่มเติม (Additional Styles)")
        sub_styles.addAction(_("menu_transliterate")).triggered.connect(lambda *args: self.parent_window.retranslate_special("transliterate"))
        sub_styles.addAction(_("menu_idiom")).triggered.connect(lambda *args: self.parent_window.retranslate_special("idiom"))
        sub_styles.addAction(_("menu_fantasy")).triggered.connect(lambda *args: self.parent_window.retranslate_special("fantasy"))
        sub_styles.addAction(_("menu_casual")).triggered.connect(lambda *args: self.parent_window.retranslate_special("casual"))
        sub_styles.addAction(_("menu_mature")).triggered.connect(lambda *args: self.parent_window.retranslate_special("mature"))
        self.btn_trans_special.setMenu(self.special_menu)
        t3_header.addWidget(self.btn_trans_special)
        t3_layout.addLayout(t3_header)

        # Sub-Action Bar
        sub_act_row = QHBoxLayout()
        self.btn_patch_eng = QPushButton("🩹 ซ่อมคำอังกฤษ")
        self.btn_patch_eng.setToolTip("ตรวจหาและแปลซ่อมคำภาษาอังกฤษที่หลุดออกมาเฉพาะจุดสำหรับแถวที่เลือก โดยคงประโยคภาษาไทยเดิมไว้ (Ctrl+Shift+E)")
        self.btn_patch_eng.setStyleSheet("background:#1e2a24; color:#a6e3a1; border:1px solid #3b5e47; border-radius:4px; padding:2px 8px; font-size:11px; font-weight:bold;")
        self.btn_patch_eng.clicked.connect(self.parent_window.patch_selected_english_leaks)
        sub_act_row.addWidget(self.btn_patch_eng)

        self.btn_retrofit_mil = QPushButton("🎖️ ซ่อมศัพท์ & คีย์บอร์ด")
        self.btn_retrofit_mil.setToolTip("สแกนและซ่อมแซมคำศัพท์อาวุธ ปุ่มคีย์บอร์ด (Spacebar, Enter, Backspace, Keypad) และรหัสโมเดลในไฟล์เดิมโดยไม่เสีย Token (0 Token) [Ctrl+Shift+M]")
        self.btn_retrofit_mil.setStyleSheet("background:#2a2b1e; color:#f9e2af; border:1px solid #5e5a3b; border-radius:4px; padding:2px 8px; font-size:11px; font-weight:bold;")
        self.btn_retrofit_mil.clicked.connect(self.parent_window.open_military_retrofit_dialog)
        sub_act_row.addWidget(self.btn_retrofit_mil)

        self.btn_polish_cinematic = QPushButton("🎬 ขัดเกลาภาษาพูด")
        self.btn_polish_cinematic.setToolTip("ขัดเกลาสำนวนแปลไทยที่ตรงตัว แข็ง หรือแปลเป็นหุ่นยนต์ ให้เป็นภาษาพูดธรรมชาติสไตล์พากย์ไทยภาพยนตร์ [Ctrl+Shift+P]")
        self.btn_polish_cinematic.setStyleSheet("background:#2b261e; color:#f9e2af; border:1px solid #6e5c3b; border-radius:4px; padding:2px 8px; font-size:11px; font-weight:bold;")
        self.btn_polish_cinematic.clicked.connect(self.parent_window.polish_selected_cinematic)
        sub_act_row.addWidget(self.btn_polish_cinematic)

        self.btn_clear_trans = QPushButton("🧹 ลบคำแปล ▾")
        self.btn_clear_trans.setToolTip("ล้างคำแปล (trans & AI) กลับเป็นสถานะ 'รอแปล' โดยไม่ลบแถวออกจากไฟล์")
        self.btn_clear_trans.setStyleSheet("background:#2b2230; color:#f5c2e7; border:1px solid #6b406a; border-radius:4px; padding:2px 8px; font-size:11px; font-weight:bold;")
        self.clear_menu = QMenu(self)
        self.clear_menu.setStyleSheet("QMenu { font-size: 12px; background: #1e1e2e; color: #cdd6f4; border: 1px solid #45475a; } QMenu::item:selected { background: #45475a; }")
        self.clear_menu.addAction("🧹 ลบคำแปลแถวนี้ / แถวที่เลือก (Backspace)").triggered.connect(lambda: self.parent_window.clear_selected_translations(only_ai=False))
        self.clear_menu.addAction("🤖 ลบเฉพาะผลแปล AI แถวที่เลือก").triggered.connect(lambda: self.parent_window.clear_selected_translations(only_ai=True))
        self.clear_menu.addSeparator()
        self.clear_menu.addAction("💥 ลบคำแปลทั้งหมดในไฟล์ (Clear All)...").triggered.connect(lambda: self.parent_window.clear_all_translations(only_ai=False))
        self.clear_menu.addAction("🤖 ลบเฉพาะผลแปล AI ทั้งหมดในไฟล์...").triggered.connect(lambda: self.parent_window.clear_all_translations(only_ai=True))
        self.btn_clear_trans.setMenu(self.clear_menu)
        sub_act_row.addWidget(self.btn_clear_trans)

        self.btn_delete_rows = QPushButton("🗑️ ลบแถว")
        self.btn_delete_rows.setToolTip("ลบบรรทัดที่เลือกออกจากไฟล์ถาวร")
        self.btn_delete_rows.setStyleSheet("background:#2a1e24; color:#f38ba8; border:1px solid #5e313b; border-radius:4px; padding:2px 8px; font-size:11px;")
        self.btn_delete_rows.clicked.connect(lambda: self.parent_window.delete_selected_rows(confirm=True))
        sub_act_row.addWidget(self.btn_delete_rows)

        self.chk_use_tlm = QCheckBox("✓ TLM")
        self.chk_use_tlm.setToolTip("อ้างอิงคลังบริบท TLM")
        self.chk_use_tlm.setChecked(True)
        self.chk_use_tlm.setStyleSheet("color: #a6adc8; font-size: 11px;")
        sub_act_row.addWidget(self.chk_use_tlm)

        self.chk_guide_mode = QCheckBox("โหมดช่วย")
        self.chk_guide_mode.setToolTip("โหมดผู้ช่วยแนะนำคำแปล (Guide Mode)")
        self.chk_guide_mode.setChecked(False)
        self.chk_guide_mode.setStyleSheet("color: #fab387; font-size: 11px; font-weight: bold;")
        self.chk_guide_mode.toggled.connect(self.parent_window._on_guide_mode_toggled)
        sub_act_row.addWidget(self.chk_guide_mode)
        sub_act_row.addStretch(1)
        t3_layout.addLayout(sub_act_row)

        # Main Translation Editor
        self.txt_trans = QTextEdit()
        self.txt_trans.setPlaceholderText("พิมพ์คำแปลภาษาไทยที่นี่... หรือกด Ctrl+Enter เพื่อยืนยันและไปบรรทัดถัดไป")
        self.trans_filter = TransEditorEventFilter(self.parent_window)
        self.txt_trans.installEventFilter(self.trans_filter)
        self.txt_trans.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.txt_trans.customContextMenuRequested.connect(self.show_trans_context_menu)
        self.txt_trans.selectionChanged.connect(lambda: self.on_text_selection_changed(self.txt_trans))

        self._trans_save_timer = QTimer(self)
        self._trans_save_timer.setSingleShot(True)
        self._trans_save_timer.timeout.connect(self.parent_window.on_trans_changed)
        self.txt_trans.textChanged.connect(lambda: self._trans_save_timer.start(250))
        self.txt_trans.setMinimumHeight(180)
        t3_layout.addWidget(self.txt_trans, 1)

        # Bottom Shortcut Hint
        lbl_hint = QLabel("⚡ <b>Ctrl+Enter</b> บันทึกและถัดไป")
        lbl_hint.setWordWrap(True)
        lbl_hint.setStyleSheet("color: #fab387; font-size: 11px; padding: 2px;")
        t3_layout.addWidget(lbl_hint)

        layout.addWidget(tier3_box, 1)

    # -------------------------------------------------------------
    # Context Menus & Selection Handlers
    # -------------------------------------------------------------
    def copy_source_to_clipboard(self):
        txt = self.txt_source.toPlainText()
        if txt:
            QApplication.clipboard().setText(txt)

    def apply_ai_ref_to_editor(self):
        ref = self.txt_ai.toPlainText()
        if ref:
            self.txt_trans.setPlainText(ref)
            self.txt_trans.setFocus()

    def insert_chip_text(self, text):
        self.txt_trans.insertPlainText(text)
        self.txt_trans.setFocus()

    def show_special_translation_menu_at_cursor(self):
        if hasattr(self, 'special_menu'):
            self.special_menu.exec(QCursor.pos())

    def on_text_selection_changed(self, editor_widget):
        """Monitors text selection in editor boxes and shows quick-action pill and updates translate button."""
        cursor = editor_widget.textCursor()
        if not cursor.hasSelection():
            self.clear_selection_pill()
            return

        sel = cursor.selectedText().replace('\u2029', ' ').strip()
        if len(sel) < 2 or len(sel) > 300:
            self.clear_selection_pill()
            return

        self.parent_window._last_selected_text = sel
        self.parent_window._last_selected_widget = editor_widget
        self.parent_window._last_selection_range = (cursor.selectionStart(), cursor.selectionEnd())

        # Dynamically change main translate button to indicate snippet translation
        if not getattr(self.parent_window, '_original_trans_btn_text', None):
            self.parent_window._original_trans_btn_text = self.btn_trans_smart.text()
            self.parent_window._original_trans_btn_style = self.btn_trans_smart.styleSheet()
        self.btn_trans_smart.setText("✨ แปลส่วนที่เลือก")
        self.btn_trans_smart.setStyleSheet(
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #89b4fa, stop:1 #b4befe); "
            "color: #11111b; font-size: 12px; font-weight: bold; border-radius: 6px; padding: 4px 10px;"
        )
        self.btn_trans_smart.setToolTip(f"แปลเฉพาะคำที่เลือก: '{sel[:30]}' (Ctrl+Shift+T)")

        # Position and display floating quick pill
        if not hasattr(self.parent_window, 'selection_pill'):
            self.parent_window.selection_pill = SelectionTranslatePill(self.parent_window)

        pill = self.parent_window.selection_pill
        pill.active_editor = editor_widget
        rect = editor_widget.cursorRect(cursor)
        global_pt = editor_widget.mapTo(self.parent_window, rect.topLeft())

        pill.adjustSize()
        pill_w = pill.sizeHint().width() or 260
        pill_h = pill.sizeHint().height() or 30
        x = global_pt.x() + (rect.width() // 2) - (pill_w // 2)
        y = global_pt.y() - pill_h - 6

        x = max(10, min(x, self.parent_window.width() - pill_w - 10))
        if y < 40:
            y = global_pt.y() + rect.height() + 6

        pill.move(x, y)
        pill.show()
        pill.raise_()

    def clear_selection_pill(self):
        """Hides floating pill and restores translate button to normal state."""
        if hasattr(self.parent_window, 'selection_pill') and self.parent_window.selection_pill.isVisible():
            self.parent_window.selection_pill.hide()
        if getattr(self.parent_window, '_original_trans_btn_text', None):
            self.btn_trans_smart.setText(self.parent_window._original_trans_btn_text)
            self.btn_trans_smart.setStyleSheet(self.parent_window._original_trans_btn_style)
            self.parent_window._original_trans_btn_text = None
            self.parent_window._original_trans_btn_style = None
            self.btn_trans_smart.setToolTip("แปลบรรทัดนี้ด้วย AI (Ctrl+Enter / Ctrl+T)")

    def show_trans_context_menu(self, pos):
        """Custom context menu for txt_trans offering snippet translation and glossary tools."""
        menu = self.txt_trans.createStandardContextMenu()
        cursor = self.txt_trans.textCursor()
        if not cursor.hasSelection():
            click_cursor = self.txt_trans.cursorForPosition(pos)
            click_cursor.select(click_cursor.SelectionType.WordUnderCursor)
            word = click_cursor.selectedText().strip()
            if word and len(word) >= 2:
                cursor = click_cursor
                self.txt_trans.setTextCursor(cursor)
                self.on_text_selection_changed(self.txt_trans)

        if cursor.hasSelection():
            sel = cursor.selectedText().replace('\u2029', ' ').strip()
            if sel:
                first_action = menu.actions()[0] if menu.actions() else None
                label = f"✨ แปลเฉพาะคำนี้: \"{sel[:20]}...\"" if len(sel) > 20 else f"✨ แปลเฉพาะคำนี้: \"{sel}\""
                act_trans = QAction(label, menu)
                act_trans.setShortcut(QKeySequence("Ctrl+Shift+T"))
                act_trans.triggered.connect(lambda: self.translate_selected_snippet(source_widget=self.txt_trans))
                menu.insertAction(first_action, act_trans)

                label_translit = f"🗣️ แปลทับศัพท์เฉพาะคำนี้: \"{sel[:20]}...\"" if len(sel) > 20 else f"🗣️ แปลทับศัพท์เฉพาะคำนี้: \"{sel}\""
                act_translit = QAction(label_translit, menu)
                act_translit.setShortcut(QKeySequence("Ctrl+Shift+Y"))
                act_translit.triggered.connect(lambda: self.translate_selected_snippet(source_widget=self.txt_trans, mode="transliterate"))
                menu.insertAction(first_action, act_translit)

                act_styles = QAction("💡 แปล 3 สไตล์สำหรับคำนี้...", menu)
                act_styles.triggered.connect(lambda: self.translate_selected_snippet(source_widget=self.txt_trans, style_choice=True))
                menu.insertAction(first_action, act_styles)

                act_glossary = QAction(f"📖 บันทึก \"{sel[:15]}\" ลง Glossary...", menu)
                act_glossary.triggered.connect(lambda: self.quick_add_selection_to_glossary(sel))
                menu.insertAction(first_action, act_glossary)

                menu.insertSeparator(first_action)
        menu.exec(self.txt_trans.mapToGlobal(pos))

    def show_source_context_menu(self, pos):
        """Custom context menu for txt_source offering snippet translation into txt_trans."""
        menu = self.txt_source.createStandardContextMenu()
        cursor = self.txt_source.textCursor()
        if not cursor.hasSelection():
            click_cursor = self.txt_source.cursorForPosition(pos)
            click_cursor.select(click_cursor.SelectionType.WordUnderCursor)
            word = click_cursor.selectedText().strip()
            if word and len(word) >= 2:
                cursor = click_cursor
                self.txt_source.setTextCursor(cursor)
                self.on_text_selection_changed(self.txt_source)

        if cursor.hasSelection():
            sel = cursor.selectedText().replace('\u2029', ' ').strip()
            if sel:
                first_action = menu.actions()[0] if menu.actions() else None
                label = f"✨ แปลคำนี้ -> ใส่ในช่องแปล: \"{sel[:20]}...\"" if len(sel) > 20 else f"✨ แปลคำนี้ -> ใส่ในช่องแปล: \"{sel}\""
                act_trans = QAction(label, menu)
                act_trans.triggered.connect(lambda: self.translate_selected_snippet(source_widget=self.txt_source))
                menu.insertAction(first_action, act_trans)

                label_translit = f"🗣️ ทับศัพท์คำนี้ -> ใส่ในช่องแปล: \"{sel[:20]}...\"" if len(sel) > 20 else f"🗣️ ทับศัพท์คำนี้ -> ใส่ในช่องแปล: \"{sel}\""
                act_translit = QAction(label_translit, menu)
                act_translit.setShortcut(QKeySequence("Ctrl+Shift+Y"))
                act_translit.triggered.connect(lambda: self.translate_selected_snippet(source_widget=self.txt_source, mode="transliterate"))
                menu.insertAction(first_action, act_translit)

                act_styles = QAction("💡 แปล 3 สไตล์สำหรับคำนี้...", menu)
                act_styles.triggered.connect(lambda: self.translate_selected_snippet(source_widget=self.txt_source, style_choice=True))
                menu.insertAction(first_action, act_styles)

                act_glossary = QAction(f"📖 บันทึก \"{sel[:15]}\" ลง Glossary...", menu)
                act_glossary.triggered.connect(lambda: self.quick_add_selection_to_glossary(sel))
                menu.insertAction(first_action, act_glossary)

                menu.insertSeparator(first_action)
        menu.exec(self.txt_source.mapToGlobal(pos))

    def show_ai_context_menu(self, pos):
        """Custom context menu for txt_ai to allow extracting parts directly to txt_trans."""
        menu = self.txt_ai.createStandardContextMenu()
        cursor = self.txt_ai.textCursor()
        if cursor.hasSelection():
            sel = cursor.selectedText().replace('\u2029', ' ').strip()
            if sel:
                first_action = menu.actions()[0] if menu.actions() else None
                label = f"⬇ นำส่วนที่เลือกไปใส่ในช่องแปล: \"{sel[:20]}...\"" if len(sel) > 20 else f"⬇ นำส่วนที่เลือกไปใส่ในช่องแปล: \"{sel}\""
                act_insert = QAction(label, menu)
                act_insert.triggered.connect(lambda: self.apply_snippet_replacement(sel, sel, self.txt_ai, 0, 0))
                menu.insertAction(first_action, act_insert)

                label_translit = f"🗣️ แปลทับศัพท์ส่วนนี้ -> ใส่ในช่องแปล: \"{sel[:20]}...\"" if len(sel) > 20 else f"🗣️ แปลทับศัพท์ส่วนนี้ -> ใส่ในช่องแปล: \"{sel}\""
                act_translit = QAction(label_translit, menu)
                act_translit.triggered.connect(lambda: self.translate_selected_snippet(source_widget=self.txt_ai, mode="transliterate"))
                menu.insertAction(first_action, act_translit)

                menu.insertSeparator(first_action)
        menu.exec(self.txt_ai.mapToGlobal(pos))

    def quick_add_selection_to_glossary(self, term):
        """Quickly add highlighted text to the active profile's glossary."""
        term = term.strip()
        if not term:
            return
        prof_name = getattr(self.parent_window, 'current_profile_name', 'Default')
        target, ok = QInputDialog.getText(self, f"บันทึกเข้า Glossary [{prof_name}]", f"คำแปลภาษาไทยสำหรับ '{term}':")
        if ok and target and target.strip():
            target = target.strip()
            cat, ok2 = QInputDialog.getItem(
                self, "หมวดหมู่คำศัพท์", "เลือกหมวดหมู่:", 
                ["General", "Person", "Location", "Faction", "Weapon", "Item", "Skill"], 0, False
            )
            if ok2 and cat:
                prof = TStudioCore.get_current_profile_data(prof_name)
                glossary = prof.get("glossary", {})
                glossary[term] = [target, cat]
                if hasattr(self.parent_window, '_save_glossary_to_active_profile'):
                    self.parent_window._save_glossary_to_active_profile(glossary)
                else:
                    prof["glossary"] = glossary
                    TStudioCore.save_profile_data(prof_name, prof)
                    if hasattr(self.parent_window, 'refresh_glossary_dependent_features'):
                        self.parent_window.refresh_glossary_dependent_features()
                self.parent_window.statusBar().showMessage(f"📖 เพิ่มคำศัพท์ '{term}' = '{target}' ลงใน Glossary สำเร็จ", 3000)

    # -------------------------------------------------------------
    # Snippet Translation Engine
    # -------------------------------------------------------------
    def translate_selected_snippet(self, source_widget=None, style_choice=False, mode=None):
        """Translates or transliterates only the highlighted snippet/word from txt_trans or txt_source with full sentence context."""
        target_widget = source_widget
        if target_widget is None:
            if hasattr(self.parent_window, 'selection_pill') and getattr(self.parent_window.selection_pill, 'active_editor', None):
                target_widget = self.parent_window.selection_pill.active_editor
            elif self.txt_trans.textCursor().hasSelection():
                target_widget = self.txt_trans
            elif self.txt_source.textCursor().hasSelection():
                target_widget = self.txt_source
            else:
                target_widget = self.txt_trans

        if not target_widget:
            return

        cursor = target_widget.textCursor()
        sel_text = ""
        if cursor.hasSelection():
            sel_text = cursor.selectedText().replace('\u2029', ' ').strip()
            sel_start = cursor.selectionStart()
            sel_end = cursor.selectionEnd()
        elif getattr(self.parent_window, '_last_selected_text', None):
            sel_text = self.parent_window._last_selected_text
            sel_start, sel_end = getattr(self.parent_window, '_last_selection_range', (0, 0))
        else:
            self.parent_window.statusBar().showMessage("⚠️ กรุณาลากคุมคำหรือข้อความที่ต้องการแปลก่อน", 3000)
            return

        if not sel_text:
            return

        self.clear_selection_pill()

        row = self.parent_window.current_source_row
        full_source = ""
        row_id = ""
        tag = ""
        if 0 <= row < len(self.parent_window.model._data):
            item = self.parent_window.model._data[row]
            full_source = str(item.get("source") or "").replace('\r\n', '\n')
            row_id = str(item.get("id") or "")
            tag = str(item.get("tag") or "")
        current_trans = self.txt_trans.toPlainText().replace('\r\n', '\n')

        dyn_glossary = self.parent_window._get_dynamic_glossary(full_source if full_source else sel_text)

        self.parent_window.on_trans_changed()
        cfg = self.parent_window.translation_channel.snapshot_config(TStudioCore.load_config())
        target = RowTarget.capture(self.parent_window, row)
        editor_before = self.txt_trans.toPlainText()
        self.btn_trans_smart.setEnabled(False)

        if style_choice:
            self.parent_window.statusBar().showMessage(f"⏳ กำลังประมวลผล 3 สไตล์สำหรับ '{sel_text}'...", 8000)
            prompt = f"""You are a professional video game localization translator (English to Thai).
Provide 3 distinct Thai translation styles for ONLY the selected term "{sel_text}".
Context sentence: "{full_source}"
Row ID: {row_id} | Category: {tag}

Return strictly a JSON object with keys "literal", "casual", "formal":
{{
  "literal": "ตรงตัว",
  "casual": "ภาษาพูด/สละสลวย",
  "formal": "ทางการ"
}}
Return ONLY valid JSON. No markdown wrappers."""
        elif mode == "transliterate":
            self.parent_window.statusBar().showMessage(f"⏳ กำลังแปลทับศัพท์เฉพาะคำว่า '{sel_text}'...", 8000)
            prompt = f"""You are a professional video game localization expert specializing in English-to-Thai phonetic transliteration (ทับศัพท์).
Transliterate ONLY the selected term/name "{sel_text}" into natural, accurate Thai script based on phonetic pronunciation conventions used in modern video games.

CONTEXT:
Game Row ID: {row_id}
Category/Tag: {tag}
Full Source Sentence: {full_source}
Current Translation in Progress: {current_trans}

TERM TO TRANSLITERATE:
"{sel_text}"

CRITICAL RULES:
- TRANSLITERATE (ทับศัพท์) the pronunciation of "{sel_text}" into standard Thai characters.
- DO NOT translate the semantic meaning (e.g., "Shadow" -> "แชโดว์" not "เงา", "Blacksmith" -> "แบล็กสมิธ" not "ช่างตีเหล็ก", "Hunter" -> "ฮันเตอร์" not "นายพราน").
- Match standard Thai gaming phonetic transliteration rules.
- Return ONLY the transliterated Thai word/phrase.
- DO NOT return the entire sentence.
- DO NOT add quotes, markdown, explanations, IPA, or phonetic guides.
- Preserve any internal game/code tokens like {{...}}, <...>, [...] if present inside the term."""
            if dyn_glossary:
                prompt += f"\n\nGLOSSARY REFERENCES:\n{dyn_glossary}"
        elif mode:
            self.parent_window.statusBar().showMessage(f"⏳ กำลังแปลเฉพาะคำว่า '{sel_text}' ({mode})...", 8000)
            mode_text = "Translate into a natural, contextually appropriate Thai phrasing."
            if mode == "idiom":
                mode_text = "Translate into a natural, contextually appropriate Thai idiom or phrase (สำนวน/คำพังเพย)."
            elif mode == "casual":
                mode_text = "Translate into modern, casual, youth Thai slang (ภาษาพูด/วัยรุ่น)."
            elif mode == "mature":
                mode_text = "Translate aggressively using mature, gritty, unfiltered Thai language (หยาบคาย/ดุดัน)."
            elif mode == "fantasy":
                mode_text = "Translate using medieval, fantasy, or archaic Thai language (ย้อนยุค/แฟนตาซี)."

            prompt = f"""You are a professional video game localization translator (English to Thai).
Translate ONLY the selected word, term, or phrase into Thai with the following specific style:
STYLE REQUIREMENT: {mode_text}

CONTEXT:
Game Row ID: {row_id}
Category/Tag: {tag}
Full Source Sentence: {full_source}
Current Translation in Progress: {current_trans}

TERM TO TRANSLATE:
"{sel_text}"

CRITICAL RULES:
- Translate ONLY the term "{sel_text}" considering its context in the full sentence.
- Return ONLY the Thai translation of "{sel_text}".
- DO NOT return the entire sentence.
- DO NOT add quotation marks, markdown, explanations, or notes."""
            if dyn_glossary:
                prompt += f"\n\nGLOSSARY REFERENCES:\n{dyn_glossary}"
        else:
            self.parent_window.statusBar().showMessage(f"⏳ กำลังแปลเฉพาะคำว่า '{sel_text}'...", 8000)
            prompt = f"""You are a professional video game localization translator (English to Thai).
Translate ONLY the selected word, term, or phrase into natural, high-quality Thai suitable for video games.

CONTEXT:
Game Row ID: {row_id}
Category/Tag: {tag}
Full Source Sentence: {full_source}
Current Translation in Progress: {current_trans}

TERM TO TRANSLATE:
"{sel_text}"

CRITICAL RULES:
- Translate ONLY the term "{sel_text}" considering its context in the full sentence.
- Return ONLY the Thai translation of "{sel_text}".
- DO NOT return the entire sentence.
- DO NOT add quotation marks, markdown, explanations, notes, or pronunciation guides.
- If it is a character name, skill, location, or item, provide an appropriate Thai game translation or standard gaming transliteration.
- Preserve any game/UI format tokens like {{...}}, <...>, [...] if present inside the term."""
            if dyn_glossary:
                prompt += f"\n\nGLOSSARY REFERENCES:\n{dyn_glossary}"

        def _worker_func():
            return TranslationGateway.generate_content(cfg, prompt)

        def deliver(rep):
            if (not target.matches(self.parent_window) or self.parent_window.current_source_row != target.row
                    or self.txt_trans.toPlainText() != editor_before):
                self.btn_trans_smart.setEnabled(True)
                self.parent_window._retain_translation_conflict(target, rep)
                return
            self._on_snippet_success(rep, sel_text, target_widget, sel_start, sel_end, style_choice, mode=mode)

        worker = ApiWorker(_worker_func)
        forwarder = ThreadSafeWorkerSignalsForwarder(
            on_success=deliver,
            on_error=lambda err: self.parent_window._on_retranslate_error(err, self.btn_trans_smart),
            parent=self
        )
        worker.signals.finished.connect(forwarder.handle_finished)
        worker.signals.error.connect(forwarder.handle_error)
        wid = id(worker)
        worker.signals.finished.connect(lambda _, w_id=wid: self.parent_window._workers.pop(w_id, None))
        worker.signals.error.connect(lambda _, w_id=wid: self.parent_window._workers.pop(w_id, None))
        self.parent_window._workers[wid] = worker
        self.parent_window.threadpool.start(worker)

    def _on_snippet_success(self, reply, sel_text, target_widget, sel_start, sel_end, style_choice, mode=None):
        self.btn_trans_smart.setEnabled(True)
        self.clear_selection_pill()

        if not reply:
            self.parent_window.statusBar().showMessage("⚠️ ไม่ได้รับผลการแปลจาก AI", 3000)
            return

        reply = TStudioCore.clean_cjk_leak(reply)
        thai_to_arabic = str.maketrans('๑๒๓๔๕๖๗๘๙๐', '1234567890')
        reply = reply.translate(thai_to_arabic)

        if style_choice:
            try:
                clean_json = re.sub(r'^```(?:json)?\s*', '', reply.strip())
                clean_json = re.sub(r'\s*```$', '', clean_json).strip()
                data = json.loads(clean_json)

                menu = QMenu(self)
                menu.setStyleSheet("QMenu { font-size: 13px; padding: 4px; } QMenu::item { padding: 5px 14px; }")
                lbl_act = QAction(f"💡 เลือกสไตล์สำหรับ \"{sel_text}\":", menu)
                lbl_act.setEnabled(False)
                menu.addAction(lbl_act)
                menu.addSeparator()

                for st_key, st_name in [("literal", "1. ตรงตัว"), ("casual", "2. ภาษาพูด"), ("formal", "3. ทางการ")]:
                    val = str(data.get(st_key) or "").strip()
                    if val:
                        act = QAction(f"{st_name}: {val}", menu)
                        act.triggered.connect(lambda _, v=val: self.apply_snippet_replacement(v, sel_text, target_widget, sel_start, sel_end))
                        menu.addAction(act)

                menu.exec(QCursor.pos())
                return
            except Exception as e:
                print(f"[Warning] Failed to parse style choice JSON: {e}, falling back to raw output")

        clean_text = re.sub(r'^["\'「『]|["\'」』]$', '', reply.strip())
        apply_gloss = (mode != "transliterate")
        self.apply_snippet_replacement(clean_text, sel_text, target_widget, sel_start, sel_end, apply_glossary=apply_gloss)
        if mode == "transliterate":
            self.parent_window.statusBar().showMessage(f"🗣️ ทับศัพท์ '{sel_text}' ➔ '{clean_text}' เรียบร้อย", 4000)
        else:
            self.parent_window.statusBar().showMessage(f"✨ แปลส่วนที่เลือก: '{sel_text}' ➔ '{clean_text}' สำเร็จแล้ว!", 4000)

    def apply_snippet_replacement(self, new_text, original_text, target_widget, sel_start, sel_end, apply_glossary=True):
        if not new_text or not hasattr(self, 'txt_trans'):
            return

        if apply_glossary and hasattr(self.parent_window, '_apply_glossary'):
            new_text = self.parent_window._apply_glossary(new_text, source_text=original_text)
        tc = self.txt_trans.textCursor()

        if target_widget == self.txt_trans:
            curr_sel = tc.selectedText().replace('\u2029', ' ').strip() if tc.hasSelection() else ""
            if curr_sel == original_text:
                tc.beginEditBlock()
                tc.insertText(new_text)
                tc.endEditBlock()
                self.txt_trans.setTextCursor(tc)
            else:
                doc_text = self.txt_trans.toPlainText()
                idx = doc_text.find(original_text, max(0, sel_start - 10))
                if idx == -1:
                    idx = doc_text.find(original_text)
                if idx != -1:
                    tc.setPosition(idx)
                    tc.setPosition(idx + len(original_text), tc.MoveMode.KeepAnchor)
                    tc.beginEditBlock()
                    tc.insertText(new_text)
                    tc.endEditBlock()
                    self.txt_trans.setTextCursor(tc)
                else:
                    tc.beginEditBlock()
                    tc.insertText(new_text)
                    tc.endEditBlock()
                    self.txt_trans.setTextCursor(tc)
        else:
            doc_text = self.txt_trans.toPlainText()
            if original_text in doc_text:
                idx = doc_text.find(original_text)
                tc.setPosition(idx)
                tc.setPosition(idx + len(original_text), tc.MoveMode.KeepAnchor)
                tc.beginEditBlock()
                tc.insertText(new_text)
                tc.endEditBlock()
                self.txt_trans.setTextCursor(tc)
            elif tc.hasSelection():
                tc.beginEditBlock()
                tc.insertText(new_text)
                tc.endEditBlock()
                self.txt_trans.setTextCursor(tc)
            else:
                tc.beginEditBlock()
                tc.insertText(new_text)
                tc.endEditBlock()
                self.txt_trans.setTextCursor(tc)

        self.txt_trans.setFocus()
        self.parent_window.statusBar().showMessage(f"✨ แปลส่วนที่เลือก: '{original_text}' ➔ '{new_text}' สำเร็จแล้ว!", 4000)
