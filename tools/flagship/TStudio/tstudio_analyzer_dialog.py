# -*- coding: utf-8 -*-
"""
tstudio_analyzer_dialog.py
==========================
PyQt6 Dashboard for Whole-File Game Localization Intelligence & Analytics.
Provides 6 interactive tabs:
1. Overview & Content Breakdown
2. Dramatis Personae (Cast & Characters)
3. Quests & Tactical Operations Dossier (Missions, Objectives, Lore & Web Search)
4. Asset Bundles (GAS Skills, Quests, Items)
5. Mined Entities & Glossary Suggestions
6. Quality, Conflict & Tag Integrity Auditor
"""

import os
import webbrowser
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QMessageBox, QFileDialog, QSplitter, QTextEdit,
    QProgressBar, QComboBox, QLineEdit, QMenu, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont

from tstudio_analyzer import LocalizationAnalyzer
from tstudio_core import TStudioCore


class QuestLoreDialog(QDialog):
    """
    Dialog for viewing Quest Lore, Canonical Background, and External Verification.
    """
    def __init__(self, quest_item, project_name="Game Project", parent_studio=None, parent=None):
        super().__init__(parent)
        self.quest_item = quest_item
        self.project_name = project_name
        self.parent_studio = parent_studio

        q_title = quest_item.get("title_en", "Quest")
        self.setWindowTitle(f"📜 ข้อมูลเควสต์ & บริบท Lore — {q_title}")
        self.resize(750, 560)
        self.setStyleSheet("""
            QDialog { background-color: #1e1e2e; color: #cdd6f4; font-family: 'Segoe UI', 'Tahoma', sans-serif; }
            QLabel { color: #cdd6f4; }
            QTextEdit { background-color: #11111b; color: #cdd6f4; border: 1px solid #313244; border-radius: 6px; font-size: 13px; line-height: 1.5; padding: 8px; }
            QPushButton { background-color: #313244; color: #cdd6f4; border: 1px solid #45475a; border-radius: 6px; padding: 6px 14px; font-weight: 500; }
            QPushButton:hover { background-color: #45475a; color: #ffffff; }
            QPushButton.primary-btn { background-color: #89b4fa; color: #11111b; font-weight: bold; border: none; }
            QPushButton.primary-btn:hover { background-color: #b4befe; }
        """)

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header Info Box
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #181825; border: 1px solid #313244; border-radius: 8px; padding: 10px;")
        h_layout = QVBoxLayout(header_frame)
        h_layout.setSpacing(4)

        lbl_title = QLabel(f"<b>เควสต์:</b> <span style='color: #89b4fa; font-size: 16px;'>{self.quest_item.get('title_en', '')}</span>")
        lbl_th = QLabel(f"<b>คำแปลไทย:</b> <span style='color: #a6e3a1; font-size: 14px;'>{self.quest_item.get('title_th', '-')}</span>")
        lbl_meta = QLabel(f"<b>ประเภท:</b> <span style='color: #f9e2af;'>{self.quest_item.get('type', '')}</span> | <b>รหัสอ้างอิง:</b> <code>{self.quest_item.get('root_id', '')}</code> | <b>จำนวนบรรทัด:</b> {self.quest_item.get('done_rows', 0)}/{self.quest_item.get('total_rows', 0)} แถว")
        lbl_meta.setStyleSheet("color: #bac2de; font-size: 12px;")

        h_layout.addWidget(lbl_title)
        h_layout.addWidget(lbl_th)
        h_layout.addWidget(lbl_meta)
        layout.addWidget(header_frame)

        # Content Text Area
        lbl_content_title = QLabel("📖 บริบทเนื้อเรื่อง & คำแนะนำการแปล (Lore & Localization Dossier):")
        lbl_content_title.setStyleSheet("color: #fab387; font-weight: bold; font-size: 13px;")
        layout.addWidget(lbl_content_title)

        self.txt_lore = QTextEdit()
        self.txt_lore.setReadOnly(True)
        self._generate_lore_summary()
        layout.addWidget(self.txt_lore, 1)

        # Bottom Button Bar
        btn_bar = QHBoxLayout()
        btn_bar.setSpacing(8)

        btn_google = QPushButton("🌐 เปิด Google บทสรุป")
        btn_google.clicked.connect(lambda: webbrowser.open(self.quest_item.get("search_url", "")))
        btn_bar.addWidget(btn_google)

        btn_wiki = QPushButton("📚 เปิด Game Wiki")
        btn_wiki.clicked.connect(lambda: webbrowser.open(self.quest_item.get("wiki_url", "")))
        btn_bar.addWidget(btn_wiki)

        btn_gemini = QPushButton("✨ ค้นคว้าผ่าน Gemini Web")
        btn_gemini.setStyleSheet("background: #89b4fa; color: #11111b; font-weight: bold;")
        btn_gemini.setToolTip("คัดลอก Prompt ค้นคว้าเควสต์และเปิด Gemini Web เพื่อค้นหาข้อมูลจริงจาก Google Search")
        btn_gemini.clicked.connect(self._launch_gemini_quest_search)
        btn_bar.addWidget(btn_gemini)

        btn_copy = QPushButton("📋 คัดลอกข้อมูล")
        btn_copy.clicked.connect(self._copy_content)
        btn_bar.addWidget(btn_copy)

        btn_bar.addStretch(1)

        btn_close = QPushButton("ปิด")
        btn_close.setProperty("class", "primary-btn")
        btn_close.clicked.connect(self.accept)
        btn_bar.addWidget(btn_close)

        layout.addLayout(btn_bar)

    def _generate_lore_summary(self):
        q = self.quest_item
        t_en = q.get("title_en", "")
        t_th = q.get("title_th", "")
        q_type = q.get("type", "")
        rid = q.get("root_id", "")

        lore_text = (
            f"=== สารบบบริบทเควสต์ (Quest Intelligence Summary) ===\n\n"
            f"• ชื่อภารกิจ: {t_en}\n"
            f"• หมวดหมู่: {q_type}\n"
            f"• รหัสอ้างอิง: {rid}\n"
            f"• คำแปลไทยปัจจุบัน: {t_th}\n\n"
            f"--------------------------------------------------\n"
            f"📌 แนวทางการแปลและบริบททางเนื้อเรื่อง (Localization Lore Notes):\n"
            f"1. บริบทและฝ่ายที่เกี่ยวข้อง (Faction & Setting):\n"
            f"   - ตรวจสอบชื่อองค์กรและฝ่าย เช่น Black Sun Syndicate, Crimson Dawn, Hutt Cartel หรือฝ่ายจักรวรรดิ\n"
            f"   - แนะนำให้คงชื่อเฉพาะทางของฝ่ายตามบัญญัติศัพท์หลักเพื่อความต่อเนื่องตลอดทั้งเกม\n\n"
            f"2. น้ำเสียงและระดับภาษา (Tone & Nuances):\n"
            f"   - หากเป็นภารกิจหลัก (Main Mission): ใช้ระดับภาษาที่เป็นทางการ สื่อความเข้มข้นของการรบ\n"
            f"   - หากเป็นภารกิจสหาย (Companion Quest): สะท้อนมิตรภาพ ความหลัง หรืออารมณ์ขันเฉพาะตัวละคร\n"
            f"   - หากเป็นปฏิบัติการยุทธวิธี (Tactical Operation): เน้นคำกระชับ ชัดเจน เช่น การลาดตระเวน, การบุกโจมตี\n\n"
            f"3. บัญญัติศัพท์สำคัญ (Recommended Glossary Terms):\n"
            f"   - คำว่า 'Launch Mission / Operation' ควรแปลเป็น 'เริ่มปฏิบัติการ' หรือ 'เริ่มภารกิจ' อย่างเป็นระบบ\n"
            f"   - ชื่อยาน ดาว หรือสถานที่ ควรสอบทานกับ Star Wars Wiki / Wookieepedia\n\n"
            f"💡 สามารถคลิกปุ่ม '🌐 เปิด Google บทสรุป' ด้านล่างเพื่ออ่านบทสรุปฉากนี้และ walkthrough ละเอียดได้ทันที!"
        )
        self.txt_lore.setPlainText(lore_text)

    def _copy_content(self):
        text = self.txt_lore.toPlainText()
        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.setText(text)
            QMessageBox.information(self, "คัดลอกสำเร็จ", "คัดลอกข้อมูล Lore เข้าสู่คลิปบอร์ดเรียบร้อยแล้ว")

    def _launch_gemini_quest_search(self):
        q = self.quest_item
        t_en = q.get("title_en", "Quest")
        t_th = q.get("title_th", "")
        rid = q.get("root_id", "")
        prompt = (
            f"คุณคือผู้เชี่ยวชาญด้าน Video Game Lore และ Localization\n"
            f"ช่วยค้นคว้าข้อมูลเควสต์ / ภารกิจนี้จาก Google Search / Wiki ของเกม '{self.project_name}':\n\n"
            f"• ชื่อเควสต์: '{t_en}'\n"
            f"• รหัสอ้างอิง: {rid}\n"
            f"• คำแปลไทยเบื้องต้น: {t_th}\n\n"
            f"กรุณาสรุปข้อมูลจริง: จุดประสงค์ของเควสต์, ตัวละครที่เกี่ยวข้อง, บทสนทนาสำคัญ และคำแนะนำในการแปลภาษาไทยให้ถูกต้องและเข้ากับบริบทของเกม"
        )
        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.setText(prompt)
        webbrowser.open("https://gemini.google.com/app")
        QMessageBox.information(
            self, "เปิด Gemini Web เรียบร้อย",
            f"คัดลอก Prompt สำหรับค้นคว้าเควสต์ '{t_en}' ลงคลิปบอร์ดแล้ว!\n"
            f"สามารถกด [Ctrl + V] ในหน้า Gemini Web เพื่อค้นหาข้อมูลจริงได้ทันที"
        )


class LocalizationAnalyzerDialog(QDialog):
    """
    Whole-File Game Localization Intelligence & Quality Dashboard Dialog.
    """
    jump_to_row_requested = pyqtSignal(int)
    glossary_add_requested = pyqtSignal(str, str, str)  # term, trans, tag
    translation_unify_requested = pyqtSignal(str, str)  # source_text, target_trans

    def __init__(self, data, glossary=None, project_name="Game Project", parent=None):
        super().__init__(parent)
        self.data = data
        self.glossary = glossary or {}
        self.project_name = project_name
        self.parent_studio = parent
        self.report = {}

        self.setWindowTitle(f"📊 ระบบวิเคราะห์ไฟล์ทั้งระบบอัจฉริยะ (Localization Intelligence) — {project_name}")
        self.resize(1260, 800)
        self.setStyleSheet("""
            QDialog { background-color: #1e1e2e; color: #cdd6f4; font-family: 'Segoe UI', 'Tahoma', sans-serif; }
            QTabWidget::pane { border: 1px solid #313244; background: #181825; border-radius: 8px; }
            QTabBar::tab { background: #1e1e2e; color: #a6adc8; padding: 10px 16px; border-top-left-radius: 6px; border-top-right-radius: 6px; font-weight: bold; }
            QTabBar::tab:selected { background: #313244; color: #89b4fa; border-bottom: 2px solid #89b4fa; }
            QTableWidget { background-color: #11111b; alternate-background-color: #181825; gridline-color: #313244; color: #cdd6f4; border: 1px solid #313244; border-radius: 6px; }
            QHeaderView::section { background-color: #1e1e2e; color: #bac2de; padding: 6px; font-weight: bold; border: none; border-bottom: 2px solid #313244; }
            QPushButton { background-color: #313244; color: #cdd6f4; border: 1px solid #45475a; border-radius: 6px; padding: 6px 14px; font-weight: 500; }
            QPushButton:hover { background-color: #45475a; color: #ffffff; }
            QPushButton.primary-btn { background-color: #89b4fa; color: #11111b; font-weight: bold; border: none; }
            QPushButton.primary-btn:hover { background-color: #b4befe; }
            QPushButton.danger-btn { background-color: #f38ba8; color: #11111b; font-weight: bold; border: none; }
            QPushButton.danger-btn:hover { background-color: #eba0ac; }
            QLineEdit, QTextEdit { background-color: #11111b; color: #cdd6f4; border: 1px solid #313244; border-radius: 4px; padding: 6px; }
            QMenu { background-color: #1e1e2e; color: #cdd6f4; border: 1px solid #313244; padding: 4px; }
            QMenu::item:selected { background-color: #313244; color: #89b4fa; border-radius: 4px; }
        """)

        self._build_ui()
        self.run_analysis()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # 1. Header KPI Cards (7 Cards)
        self.kpi_layout = QHBoxLayout()
        self.kpi_layout.setSpacing(8)

        self.card_total = self._create_kpi_card("แถวทั้งหมด (Rows)", "0", "#89b4fa")
        self.card_words = self._create_kpi_card("คำต้นฉบับ (Words)", "0", "#a6e3a1")
        self.card_quests = self._create_kpi_card("เควสต์/ภารกิจ (Quests)", "0", "#f9e2af")
        self.card_progress = self._create_kpi_card("ความคืบหน้า (Done)", "0%", "#89dceb")
        self.card_score = self._create_kpi_card("คะแนนความถูกต้อง (Integrity)", "100/100", "#cba6f7")
        self.card_conflicts = self._create_kpi_card("คำแปลขัดแย้ง (Conflicts)", "0", "#fab387")
        self.card_tags = self._create_kpi_card("แท็กตัวแปรเสีย (Tag Errors)", "0", "#f38ba8")

        self.kpi_layout.addWidget(self.card_total)
        self.kpi_layout.addWidget(self.card_words)
        self.kpi_layout.addWidget(self.card_quests)
        self.kpi_layout.addWidget(self.card_progress)
        self.kpi_layout.addWidget(self.card_score)
        self.kpi_layout.addWidget(self.card_conflicts)
        self.kpi_layout.addWidget(self.card_tags)
        main_layout.addLayout(self.kpi_layout)

        # 2. Tabs (6 Interactive Tabs)
        self.tabs = QTabWidget()
        self.tab_overview = self._build_overview_tab()
        self.tab_cast = self._build_cast_tab()
        self.tab_quests = self._build_quests_tab()
        self.tab_bundles = self._build_bundles_tab()
        self.tab_entities = self._build_entities_tab()
        self.tab_auditor = self._build_auditor_tab()

        self.tabs.addTab(self.tab_overview, "📊 สัดส่วนเนื้อหาเกม (Overview)")
        self.tabs.addTab(self.tab_cast, "👥 ทำเนียบตัวละคร (Cast & Dialogue)")
        self.tabs.addTab(self.tab_quests, "📜 สารบบเควสต์ & ภารกิจ (Quests & Operations)")
        self.tabs.addTab(self.tab_bundles, "📦 ชุดสกิล/ไอเทม (Asset Bundles)")
        self.tabs.addTab(self.tab_entities, "🧠 ขุดคำศัพท์เฉพาะ (Mined Entities)")
        self.tabs.addTab(self.tab_auditor, "⚠️ ตรวจจับความขัดแย้ง & แท็กโค้ด (Integrity Audit)")
        main_layout.addWidget(self.tabs, 1)

        # 3. Bottom Action Bar
        bottom_bar = QHBoxLayout()
        self.lbl_status = QLabel("พร้อมวิเคราะห์")
        self.lbl_status.setStyleSheet("color: #a6adc8; font-size: 12px;")
        bottom_bar.addWidget(self.lbl_status)
        bottom_bar.addStretch(1)

        btn_rescan = QPushButton("🔄 สแกนวิเคราะห์ใหม่")
        btn_rescan.clicked.connect(self.run_analysis)
        bottom_bar.addWidget(btn_rescan)

        btn_export = QPushButton("💾 ส่งออกรายงานวิเคราะห์ (Export Dossier .md)")
        btn_export.setProperty("class", "primary-btn")
        btn_export.clicked.connect(self.export_dossier)
        bottom_bar.addWidget(btn_export)

        btn_close = QPushButton("ปิด")
        btn_close.clicked.connect(self.accept)
        bottom_bar.addWidget(btn_close)

        main_layout.addLayout(bottom_bar)

    def _create_kpi_card(self, title, default_val, color_hex):
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: #181825;
                border: 1px solid #313244;
                border-top: 3px solid {color_hex};
                border-radius: 6px;
                padding: 6px 10px;
            }}
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)

        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color: #a6adc8; font-size: 10px; font-weight: bold;")
        lbl_val = QLabel(default_val)
        lbl_val.setStyleSheet(f"color: {color_hex}; font-size: 17px; font-weight: bold;")

        layout.addWidget(lbl_title)
        layout.addWidget(lbl_val)
        frame.lbl_val = lbl_val
        return frame

    # ----------------------------------------------------
    # Tab 1: Overview
    # ----------------------------------------------------
    def _build_overview_tab(self):
        w = QFrame()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(12, 12, 12, 12)

        lbl_desc = QLabel("สัดส่วนและการแจกแจงประเภทข้อความภายในเกม (คลิกสองครั้งที่แถวเพื่อกรองในตารางหลัก)")
        lbl_desc.setStyleSheet("color: #bac2de; font-size: 12px; margin-bottom: 4px;")
        layout.addWidget(lbl_desc)

        self.tbl_overview = QTableWidget()
        self.tbl_overview.setColumnCount(5)
        self.tbl_overview.setHorizontalHeaderLabels(["หมวดหมู่ (Category)", "จำนวนแถว (Lines)", "แปลแล้ว (Done)", "ความคืบหน้า (%)", "สัดส่วนเนื้อหาทั้งเกม"])
        self.tbl_overview.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_overview.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_overview.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_overview.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_overview.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.tbl_overview.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tbl_overview.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.tbl_overview)
        return w

    # ----------------------------------------------------
    # Tab 2: Cast & Dramatis Personae
    # ----------------------------------------------------
    def _build_cast_tab(self):
        w = QFrame()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(12, 12, 12, 12)

        lbl_desc = QLabel("ทำเนียบตัวละครที่มีบทพูดหรือปรากฏในเกม (ดับเบิลคลิกเพื่อกระโดดไปแถวแรกที่พบตัวละคร)")
        lbl_desc.setStyleSheet("color: #bac2de; font-size: 12px; margin-bottom: 4px;")
        layout.addWidget(lbl_desc)

        self.tbl_cast = QTableWidget()
        self.tbl_cast.setColumnCount(5)
        self.tbl_cast.setHorizontalHeaderLabels(["ตัวละคร (Character)", "ชื่อภาษาไทย (Thai Name)", "บทพูด/ความถี่ (Lines)", "แถวแรกที่พบ (Row)", "ตัวอย่างบทสนทนา (Sample Quote)"])
        self.tbl_cast.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_cast.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_cast.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_cast.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_cast.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.tbl_cast.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tbl_cast.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl_cast.cellDoubleClicked.connect(self._on_cast_double_clicked)
        layout.addWidget(self.tbl_cast)
        return w

    # ----------------------------------------------------
    # Tab 3: Quests & Tactical Operations Dossier
    # ----------------------------------------------------
    def _build_quests_tab(self):
        w = QFrame()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Header controls
        header_row = QHBoxLayout()
        lbl_desc = QLabel("สารบบเควสต์, ภารกิจหลัก, ภารกิจเพื่อนร่วมทาง และปฏิบัติการยุทธวิธี (ดับเบิลคลิกเพื่อกระโดดไปยังแถว)")
        lbl_desc.setStyleSheet("color: #bac2de; font-size: 12px;")
        header_row.addWidget(lbl_desc)
        header_row.addStretch(1)

        # Filter dropdown
        self.cbo_quest_filter = QComboBox()
        self.cbo_quest_filter.addItems([
            "ทั้งหมด (All Quests)",
            "เฉพาะภารกิจหลัก (Main)",
            "เฉพาะภารกิจเพื่อนร่วมทาง (Companion)",
            "เฉพาะวิกฤตการณ์ (Crisis)",
            "เฉพาะปฏิบัติการยุทธวิธี (Tactical)",
            "เฉพาะเควสต์ที่ยังไม่ครบ (Incomplete)"
        ])
        self.cbo_quest_filter.currentIndexChanged.connect(self._populate_quests_table)
        header_row.addWidget(self.cbo_quest_filter)

        # Search box
        self.txt_quest_search = QLineEdit()
        self.txt_quest_search.setPlaceholderText("🔍 ค้นหาเควสต์หรือรหัส...")
        self.txt_quest_search.setFixedWidth(200)
        self.txt_quest_search.textChanged.connect(self._populate_quests_table)
        header_row.addWidget(self.txt_quest_search)

        layout.addLayout(header_row)

        # Table
        self.tbl_quests = QTableWidget()
        self.tbl_quests.setColumnCount(8)
        self.tbl_quests.setHorizontalHeaderLabels([
            "ประเภท (Type)",
            "ชื่อเควสต์ภาษาอังกฤษ (EN)",
            "คำแปลภาษาไทย (TH)",
            "รหัสอ้างอิง (ID)",
            "จำนวนแถว",
            "สถานะ",
            "🌐 ค้นหาออนไลน์",
            "🤖 Lore & AI"
        ])
        self.tbl_quests.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_quests.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_quests.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_quests.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_quests.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_quests.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_quests.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_quests.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_quests.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tbl_quests.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl_quests.cellDoubleClicked.connect(self._on_quest_double_clicked)
        self.tbl_quests.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tbl_quests.customContextMenuRequested.connect(self._show_quest_context_menu)
        layout.addWidget(self.tbl_quests)

        return w

    # ----------------------------------------------------
    # Tab 4: Asset Bundles
    # ----------------------------------------------------
    def _build_bundles_tab(self):
        w = QFrame()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(12, 12, 12, 12)

        header_row = QHBoxLayout()
        lbl_desc = QLabel("ชุดสกิลและไอเทมที่เกี่ยวข้องกัน (จัดกลุ่ม Name + Description + Tooltip อัตโนมัติ)")
        lbl_desc.setStyleSheet("color: #bac2de; font-size: 12px;")
        header_row.addWidget(lbl_desc)
        header_row.addStretch(1)

        self.cbo_bundle_filter = QComboBox()
        self.cbo_bundle_filter.addItems(["ทั้งหมด (All Bundles)", "เฉพาะสกิล (Skills)", "เฉพาะไอเทม (Items)", "เฉพาะชุดที่ยังไม่ครบ (Incomplete)"])
        self.cbo_bundle_filter.currentIndexChanged.connect(self._populate_bundles_table)
        header_row.addWidget(self.cbo_bundle_filter)
        layout.addLayout(header_row)

        self.tbl_bundles = QTableWidget()
        self.tbl_bundles.setColumnCount(6)
        self.tbl_bundles.setHorizontalHeaderLabels(["ประเภท", "รหัสชุด (Root ID)", "ชื่อ (Name)", "คำอธิบาย (Description)", "ทูลทิป/สถิติ (Tooltip)", "สถานะ"])
        self.tbl_bundles.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_bundles.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_bundles.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_bundles.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.tbl_bundles.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_bundles.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_bundles.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tbl_bundles.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl_bundles.cellDoubleClicked.connect(self._on_bundle_double_clicked)
        layout.addWidget(self.tbl_bundles)
        return w

    # ----------------------------------------------------
    # Tab 5: Mined Entities & Glossary Suggestions
    # ----------------------------------------------------
    def _build_entities_tab(self):
        w = QFrame()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(12, 12, 12, 12)

        header_row = QHBoxLayout()
        lbl_desc = QLabel("คำศัพท์เฉพาะ (Proper Nouns & Keywords) ที่พบบ่อยในเกม เหมาะแก่การบรรจุลง Glossary")
        lbl_desc.setStyleSheet("color: #bac2de; font-size: 12px;")
        header_row.addWidget(lbl_desc)
        header_row.addStretch(1)

        btn_batch_add = QPushButton("➕ เพิ่มคำที่เลือกเข้า Glossary ทั้งหมด")
        btn_batch_add.setProperty("class", "primary-btn")
        btn_batch_add.clicked.connect(self._batch_add_selected_entities)
        header_row.addWidget(btn_batch_add)
        layout.addLayout(header_row)

        self.tbl_entities = QTableWidget()
        self.tbl_entities.setColumnCount(5)
        self.tbl_entities.setHorizontalHeaderLabels(["คำศัพท์ (Entity Term)", "ความถี่ (Frequency)", "สถานะใน Glossary", "ตัวอย่างประโยค (Sample Context)", "การกระทำ (Action)"])
        self.tbl_entities.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_entities.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_entities.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_entities.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.tbl_entities.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_entities.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tbl_entities.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl_entities.cellDoubleClicked.connect(self._on_entity_double_clicked)
        layout.addWidget(self.tbl_entities)
        return w

    # ----------------------------------------------------
    # Tab 6: Integrity & Quality Auditor
    # ----------------------------------------------------
    def _build_auditor_tab(self):
        w = QFrame()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(12, 12, 12, 12)

        splitter = QSplitter(Qt.Orientation.Vertical)

        # Upper: 1-to-Many Translation Conflicts
        frame_conflicts = QFrame()
        vbox_c = QVBoxLayout(frame_conflicts)
        vbox_c.setContentsMargins(0, 0, 0, 0)
        lbl_c = QLabel("🔸 ประโยคต้นฉบับเดียวกัน แต่ถูกแปลขัดแย้งกันหลายแบบ (1-to-Many Conflicts) — ดับเบิลคลิกเพื่อดูแถว")
        lbl_c.setStyleSheet("color: #fab387; font-weight: bold; font-size: 12px;")
        vbox_c.addWidget(lbl_c)

        self.tbl_conflicts = QTableWidget()
        self.tbl_conflicts.setColumnCount(4)
        self.tbl_conflicts.setHorizontalHeaderLabels(["ประโยคต้นฉบับ (Source Text)", "จำนวนจุดที่พบ", "จำนวนรูปแบบคำแปล", "รายละเอียดคำแปลที่ใช้ (Variants)"])
        self.tbl_conflicts.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tbl_conflicts.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_conflicts.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_conflicts.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.tbl_conflicts.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tbl_conflicts.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl_conflicts.cellDoubleClicked.connect(self._on_conflict_double_clicked)
        vbox_c.addWidget(self.tbl_conflicts)
        splitter.addWidget(frame_conflicts)

        # Lower: Tag & Variable Syntax Errors
        frame_tags = QFrame()
        vbox_t = QVBoxLayout(frame_tags)
        vbox_t.setContentsMargins(0, 8, 0, 0)
        lbl_t = QLabel("⚠️ แท็กตัวแปรเกมสูญหายหรือไม่ตรง (Game Engine Tag Errors) — อาจทำให้เกมแครช!")
        lbl_t.setStyleSheet("color: #f38ba8; font-weight: bold; font-size: 12px;")
        vbox_t.addWidget(lbl_t)

        self.tbl_tags = QTableWidget()
        self.tbl_tags.setColumnCount(5)
        self.tbl_tags.setHorizontalHeaderLabels(["แถว (Row)", "รหัส (ID)", "แท็กที่ขาดหายไป (Missing)", "แท็กเกิน/ผิดเพี้ยน (Extra)", "ข้อความต้นฉบับ"])
        self.tbl_tags.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_tags.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_tags.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_tags.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_tags.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.tbl_tags.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tbl_tags.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl_tags.cellDoubleClicked.connect(self._on_tag_double_clicked)
        vbox_t.addWidget(self.tbl_tags)
        splitter.addWidget(frame_tags)

        layout.addWidget(splitter)
        return w

    # ----------------------------------------------------
    # Analysis Execution & Data Population
    # ----------------------------------------------------
    def run_analysis(self):
        self.lbl_status.setText("กำลังสแกนวิเคราะห์โครงสร้างทั้งไฟล์...")
        self.report = LocalizationAnalyzer.analyze(self.data, self.glossary, self.project_name)

        # Update KPI Cards
        m = self.report.get("metrics", {})
        self.card_total.lbl_val.setText(f"{m.get('total_rows', 0):,}")
        self.card_words.lbl_val.setText(f"{m.get('total_words', 0):,}")
        self.card_progress.lbl_val.setText(f"{m.get('progress_percent', 0)}%")

        quests_count = len(self.report.get("quests", []))
        self.card_quests.lbl_val.setText(f"{quests_count:,}")

        score = m.get("integrity_score", 100)
        self.card_score.lbl_val.setText(f"{score}/100")
        if score >= 80:
            self.card_score.lbl_val.setStyleSheet("color: #a6e3a1; font-size: 17px; font-weight: bold;")
        elif score >= 50:
            self.card_score.lbl_val.setStyleSheet("color: #fab387; font-size: 17px; font-weight: bold;")
        else:
            self.card_score.lbl_val.setStyleSheet("color: #f38ba8; font-size: 17px; font-weight: bold;")

        conflicts_count = len(self.report.get("conflicts", []))
        self.card_conflicts.lbl_val.setText(f"{conflicts_count:,}")

        tags_count = len(self.report.get("tag_errors", []))
        self.card_tags.lbl_val.setText(f"{tags_count:,}")

        # Populate Tabs
        self._populate_overview_table()
        self._populate_cast_table()
        self._populate_quests_table()
        self._populate_bundles_table()
        self._populate_entities_table()
        self._populate_auditor_tables()

        dur = self.report.get("scan_duration", 0)
        self.lbl_status.setText(f"✅ วิเคราะห์เสร็จสิ้นใน {dur} วินาที | พบเควสต์ {quests_count:,} รายการ, ความขัดแย้ง {conflicts_count:,} จุด, แท็กผิด {tags_count:,} จุด")

    def _populate_overview_table(self):
        m = self.report.get("metrics", {})
        cats = m.get("categories", {})
        c_trans = m.get("category_trans", {})
        total_r = m.get("total_rows", 1)

        self.tbl_overview.setRowCount(len(cats))
        for r_idx, (cat_name, count) in enumerate(sorted(cats.items(), key=lambda x: x[1], reverse=True)):
            done = c_trans.get(cat_name, 0)
            pct = round((done / count * 100), 1) if count > 0 else 0
            share = round((count / total_r * 100), 1)

            it_cat = QTableWidgetItem(cat_name)
            it_count = QTableWidgetItem(f"{count:,}")
            it_done = QTableWidgetItem(f"{done:,}")
            it_pct = QTableWidgetItem(f"{pct}%")
            it_share = QTableWidgetItem(f"{share}% ของไฟล์เกม")

            if pct >= 99.0: it_pct.setForeground(QColor("#a6e3a1"))
            elif pct > 0: it_pct.setForeground(QColor("#f9e2af"))
            else: it_pct.setForeground(QColor("#f38ba8"))

            self.tbl_overview.setItem(r_idx, 0, it_cat)
            self.tbl_overview.setItem(r_idx, 1, it_count)
            self.tbl_overview.setItem(r_idx, 2, it_done)
            self.tbl_overview.setItem(r_idx, 3, it_pct)
            self.tbl_overview.setItem(r_idx, 4, it_share)

    def _populate_cast_table(self):
        cast = self.report.get("cast", [])
        self.tbl_cast.setRowCount(len(cast))
        for r_idx, char in enumerate(cast):
            it_name = QTableWidgetItem(char["name"])
            it_th = QTableWidgetItem(char["thai_name"] or "-")
            it_mentions = QTableWidgetItem(f"{char['mentions']:,}")
            it_row = QTableWidgetItem(str(char["first_row"] + 1))
            it_quote = QTableWidgetItem(char["sample_source"])

            it_name.setData(Qt.ItemDataRole.UserRole, char["first_row"])
            it_name.setForeground(QColor("#89b4fa"))
            it_th.setForeground(QColor("#a6e3a1"))

            self.tbl_cast.setItem(r_idx, 0, it_name)
            self.tbl_cast.setItem(r_idx, 1, it_th)
            self.tbl_cast.setItem(r_idx, 2, it_mentions)
            self.tbl_cast.setItem(r_idx, 3, it_row)
            self.tbl_cast.setItem(r_idx, 4, it_quote)

    def _populate_quests_table(self):
        quests = self.report.get("quests", [])
        filt = self.cbo_quest_filter.currentIndex() if hasattr(self, 'cbo_quest_filter') else 0
        search_txt = self.txt_quest_search.text().strip().lower() if hasattr(self, 'txt_quest_search') else ""

        filtered = []
        for q in quests:
            q_type = q.get("type", "")
            if filt == 1 and not ("Main" in q_type or "Primary" in q_type): continue
            if filt == 2 and not ("Companion" in q_type or "Secondary" in q_type): continue
            if filt == 3 and not ("Crisis" in q_type): continue
            if filt == 4 and not ("Tactical" in q_type or "OT_" in q.get("root_id", "")): continue
            if filt == 5 and q.get("is_complete", False): continue

            if search_txt:
                if (search_txt not in q.get("title_en", "").lower() and
                    search_txt not in q.get("title_th", "").lower() and
                    search_txt not in q.get("root_id", "").lower()):
                    continue

            filtered.append(q)

        self.tbl_quests.setRowCount(len(filtered))
        for r_idx, q in enumerate(filtered):
            it_type = QTableWidgetItem(q["type"])
            it_en = QTableWidgetItem(q["title_en"])
            it_th = QTableWidgetItem(q["title_th"])
            it_rid = QTableWidgetItem(q["root_id"])
            it_rows = QTableWidgetItem(f"{q['done_rows']}/{q['total_rows']}")
            it_status = QTableWidgetItem("✅ ครบถ้วน" if q["is_complete"] else "⏳ กำลังแปล")

            it_en.setData(Qt.ItemDataRole.UserRole, q["first_row"])
            it_en.setForeground(QColor("#89b4fa"))
            it_th.setForeground(QColor("#a6e3a1"))

            if "Companion" in q["type"]: it_type.setForeground(QColor("#cba6f7"))
            elif "Main" in q["type"] or "Primary" in q["type"]: it_type.setForeground(QColor("#f9e2af"))
            elif "Crisis" in q["type"]: it_type.setForeground(QColor("#f38ba8"))
            elif "Tactical" in q["type"]: it_type.setForeground(QColor("#89dceb"))

            if q["is_complete"]: it_status.setForeground(QColor("#a6e3a1"))
            else: it_status.setForeground(QColor("#fab387"))

            # 🌐 1-Click Web Search Button
            btn_search = QPushButton("🌐 Google")
            btn_search.setStyleSheet("padding: 2px 8px; font-size: 11px;")
            search_url = q.get("search_url", "")
            btn_search.clicked.connect(lambda ch, u=search_url: webbrowser.open(u))

            # 🤖 AI Lore Button
            btn_lore = QPushButton("🤖 Lore & AI")
            btn_lore.setStyleSheet("padding: 2px 8px; font-size: 11px; font-weight: bold; background-color: #45475a;")
            btn_lore.clicked.connect(lambda ch, item=q: self._open_quest_lore_dialog(item))

            self.tbl_quests.setItem(r_idx, 0, it_type)
            self.tbl_quests.setItem(r_idx, 1, it_en)
            self.tbl_quests.setItem(r_idx, 2, it_th)
            self.tbl_quests.setItem(r_idx, 3, it_rid)
            self.tbl_quests.setItem(r_idx, 4, it_rows)
            self.tbl_quests.setItem(r_idx, 5, it_status)
            self.tbl_quests.setCellWidget(r_idx, 6, btn_search)
            self.tbl_quests.setCellWidget(r_idx, 7, btn_lore)

    def _show_quest_context_menu(self, pos):
        item = self.tbl_quests.itemAt(pos)
        if not item: return
        row = item.row()
        item_en = self.tbl_quests.item(row, 1)
        if not item_en: return
        first_row = item_en.data(Qt.ItemDataRole.UserRole)
        title_en = item_en.text()

        quests = self.report.get("quests", [])
        quest_obj = next((q for q in quests if q["title_en"] == title_en or q["first_row"] == first_row), None)
        if not quest_obj: return

        menu = QMenu(self)
        act_jump = menu.addAction("🎯 กระโดดไปยังแถวนี้ในตารางหลัก")
        act_search = menu.addAction("🌐 เปิดค้นหาบทสรุปใน Google (Walkthrough)")
        act_wiki = menu.addAction("📚 เปิดค้นหาข้อมูลใน Game Wiki")
        act_lore = menu.addAction("🤖 ตรวจสอบบริบท Lore ด้วย AI ออนไลน์")

        chosen = menu.exec(self.tbl_quests.viewport().mapToGlobal(pos))
        if chosen == act_jump:
            if first_row is not None:
                self.jump_to_row_requested.emit(first_row)
        elif chosen == act_search:
            webbrowser.open(quest_obj.get("search_url", ""))
        elif chosen == act_wiki:
            webbrowser.open(quest_obj.get("wiki_url", ""))
        elif chosen == act_lore:
            self._open_quest_lore_dialog(quest_obj)

    def _open_quest_lore_dialog(self, quest_item):
        dlg = QuestLoreDialog(quest_item, self.project_name, parent_studio=self.parent_studio, parent=self)
        dlg.exec()

    def _populate_bundles_table(self):
        bundles = self.report.get("bundles", [])
        filt = self.cbo_bundle_filter.currentIndex() if hasattr(self, 'cbo_bundle_filter') else 0

        filtered = []
        for b in bundles:
            if filt == 1 and b["type"] != "Skill": continue
            if filt == 2 and b["type"] != "Item": continue
            if filt == 3 and b["is_complete"]: continue
            filtered.append(b)

        self.tbl_bundles.setRowCount(len(filtered))
        for r_idx, b in enumerate(filtered):
            it_type = QTableWidgetItem(b["type"])
            it_root = QTableWidgetItem(b["root_id"])
            it_name = QTableWidgetItem(b["name_th"] or b["name_en"] or "-")
            it_desc = QTableWidgetItem(b["desc_th"] or b["desc_en"] or "-")
            it_tool = QTableWidgetItem(b["tooltip_th"] or b["tooltip_en"] or "-")
            it_status = QTableWidgetItem("✅ ครบถ้วน" if b["is_complete"] else "⏳ แปลไม่ครบ")

            if b["all_indices"]:
                it_root.setData(Qt.ItemDataRole.UserRole, b["all_indices"][0])

            if b["type"] == "Skill": it_type.setForeground(QColor("#cba6f7"))
            elif b["type"] == "Item": it_type.setForeground(QColor("#89b4fa"))
            elif b["type"] == "Quest": it_type.setForeground(QColor("#f9e2af"))

            if b["is_complete"]: it_status.setForeground(QColor("#a6e3a1"))
            else: it_status.setForeground(QColor("#fab387"))

            self.tbl_bundles.setItem(r_idx, 0, it_type)
            self.tbl_bundles.setItem(r_idx, 1, it_root)
            self.tbl_bundles.setItem(r_idx, 2, it_name)
            self.tbl_bundles.setItem(r_idx, 3, it_desc)
            self.tbl_bundles.setItem(r_idx, 4, it_tool)
            self.tbl_bundles.setItem(r_idx, 5, it_status)

    def _populate_entities_table(self):
        entities = self.report.get("entities", [])
        self.tbl_entities.setRowCount(len(entities))
        for r_idx, ent in enumerate(entities):
            it_term = QTableWidgetItem(ent["term"])
            it_freq = QTableWidgetItem(f"{ent['frequency']:,} ครั้ง")
            it_status = QTableWidgetItem("✅ ใน Glossary แล้ว" if ent["in_glossary"] else "⚠️ ยังไม่มี")
            it_sample = QTableWidgetItem(ent["sample_src"])

            it_term.setData(Qt.ItemDataRole.UserRole, ent["sample_row"])
            it_term.setForeground(QColor("#89b4fa"))

            if ent["in_glossary"]: it_status.setForeground(QColor("#a6e3a1"))
            else: it_status.setForeground(QColor("#fab387"))

            btn_add = QPushButton("+ เพิ่มเข้า Glossary")
            btn_add.setStyleSheet("padding: 2px 8px; font-size: 11px;")
            term_val = ent["term"]
            trans_val = ent.get("sample_trans", "")
            btn_add.clicked.connect(lambda ch, t=term_val, tr=trans_val: self._add_single_entity_to_glossary(t, tr))

            self.tbl_entities.setItem(r_idx, 0, it_term)
            self.tbl_entities.setItem(r_idx, 1, it_freq)
            self.tbl_entities.setItem(r_idx, 2, it_status)
            self.tbl_entities.setItem(r_idx, 3, it_sample)
            self.tbl_entities.setCellWidget(r_idx, 4, btn_add)

    def _populate_auditor_tables(self):
        # 1. Conflicts
        conflicts = self.report.get("conflicts", [])
        self.tbl_conflicts.setRowCount(len(conflicts))
        for r_idx, c in enumerate(conflicts):
            it_src = QTableWidgetItem(c["source"])
            it_total = QTableWidgetItem(f"{c['total_count']:,}")
            it_vars = QTableWidgetItem(f"{c['variant_count']} แบบ")

            v_desc_parts = [f'• "{v["trans"]}" ({v["count"]} จุด)' for v in c["variants"]]
            it_desc = QTableWidgetItem("  ".join(v_desc_parts))

            if c["variants"] and c["variants"][0]["row_indices"]:
                it_src.setData(Qt.ItemDataRole.UserRole, c["variants"][0]["row_indices"][0])

            it_src.setForeground(QColor("#fab387"))
            self.tbl_conflicts.setItem(r_idx, 0, it_src)
            self.tbl_conflicts.setItem(r_idx, 1, it_total)
            self.tbl_conflicts.setItem(r_idx, 2, it_vars)
            self.tbl_conflicts.setItem(r_idx, 3, it_desc)

        # 2. Tag Errors
        tag_errors = self.report.get("tag_errors", [])
        self.tbl_tags.setRowCount(len(tag_errors))
        for r_idx, te in enumerate(tag_errors):
            it_row = QTableWidgetItem(str(te["idx"] + 1))
            it_uid = QTableWidgetItem(te["uid"])
            it_miss = QTableWidgetItem(" ".join(te["missing"]) if te["missing"] else "-")
            it_extra = QTableWidgetItem(" ".join(te["extra"]) if te["extra"] else "-")
            it_src = QTableWidgetItem(te["src"])

            it_row.setData(Qt.ItemDataRole.UserRole, te["idx"])
            it_miss.setForeground(QColor("#f38ba8"))
            it_extra.setForeground(QColor("#fab387"))

            self.tbl_tags.setItem(r_idx, 0, it_row)
            self.tbl_tags.setItem(r_idx, 1, it_uid)
            self.tbl_tags.setItem(r_idx, 2, it_miss)
            self.tbl_tags.setItem(r_idx, 3, it_extra)
            self.tbl_tags.setItem(r_idx, 4, it_src)

    # ----------------------------------------------------
    # Double-click jumps to Main Table
    # ----------------------------------------------------
    def _on_cast_double_clicked(self, row, col):
        item = self.tbl_cast.item(row, 0)
        if item:
            row_idx = item.data(Qt.ItemDataRole.UserRole)
            if row_idx is not None:
                self.jump_to_row_requested.emit(row_idx)

    def _on_quest_double_clicked(self, row, col):
        item = self.tbl_quests.item(row, 1)
        if item:
            row_idx = item.data(Qt.ItemDataRole.UserRole)
            if row_idx is not None:
                self.jump_to_row_requested.emit(row_idx)

    def _on_bundle_double_clicked(self, row, col):
        item = self.tbl_bundles.item(row, 1)
        if item:
            row_idx = item.data(Qt.ItemDataRole.UserRole)
            if row_idx is not None:
                self.jump_to_row_requested.emit(row_idx)

    def _on_entity_double_clicked(self, row, col):
        item = self.tbl_entities.item(row, 0)
        if item:
            row_idx = item.data(Qt.ItemDataRole.UserRole)
            if row_idx is not None:
                self.jump_to_row_requested.emit(row_idx)

    def _on_conflict_double_clicked(self, row, col):
        item = self.tbl_conflicts.item(row, 0)
        if item:
            row_idx = item.data(Qt.ItemDataRole.UserRole)
            if row_idx is not None:
                self.jump_to_row_requested.emit(row_idx)

    def _on_tag_double_clicked(self, row, col):
        item = self.tbl_tags.item(row, 0)
        if item:
            row_idx = item.data(Qt.ItemDataRole.UserRole)
            if row_idx is not None:
                self.jump_to_row_requested.emit(row_idx)

    # ----------------------------------------------------
    # Glossary Add Handlers
    # ----------------------------------------------------
    def _add_single_entity_to_glossary(self, term, sample_trans=""):
        tag = "General"
        if any(term.lower().startswith(p) for p in ["darth", "general", "captain", "commander", "master"]):
            tag = "Person"
        elif any(k in term.lower() for k in ["temple", "city", "station", "planet", "base"]):
            tag = "Location"

        self.glossary_add_requested.emit(term, sample_trans, tag)
        QMessageBox.information(self, "เพิ่มเข้า Glossary", f"ส่งคำว่า '{term}' เข้าสู่ระบบ Glossary เรียบร้อยแล้ว")
        self.run_analysis()

    def _batch_add_selected_entities(self):
        selected_rows = set(index.row() for index in self.tbl_entities.selectedIndexes())
        if not selected_rows:
            QMessageBox.information(self, "Glossary", "กรุณาคลิกเลือกแถวคำศัพท์ในตารางก่อนกดปุ่มนี้")
            return

        added_count = 0
        entities = self.report.get("entities", [])
        for r_idx in selected_rows:
            if 0 <= r_idx < len(entities):
                ent = entities[r_idx]
                if not ent["in_glossary"]:
                    self.glossary_add_requested.emit(ent["term"], ent.get("sample_trans", ""), "General")
                    added_count += 1

        QMessageBox.information(self, "บันทึก Glossary", f"เพิ่มคำศัพท์ {added_count} คำเข้าสู่ Glossary เรียบร้อยแล้ว")
        self.run_analysis()

    # ----------------------------------------------------
    # Export Dossier
    # ----------------------------------------------------
    def export_dossier(self):
        markdown_text = LocalizationAnalyzer.generate_markdown_dossier(self.report, self.project_name)

        save_path, _ = QFileDialog.getSaveFileName(
            self, "ส่งออกรายงานสรุปงานแปล (Export Dossier)",
            f"{self.project_name}_Localization_Dossier.md",
            "Markdown Files (*.md);;All Files (*)"
        )
        if save_path:
            try:
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(markdown_text)

                # Automatic Sync to Modding-Knowledge (Global Rule)
                ki_dir = r"E:\Mod_Workspace\Modding-Knowledge\Games"
                os.makedirs(ki_dir, exist_ok=True)
                ki_path = os.path.join(ki_dir, os.path.basename(save_path))
                with open(ki_path, "w", encoding="utf-8") as f:
                    f.write(markdown_text)

                QMessageBox.information(
                    self, "ส่งออกสำเร็จ",
                    f"บันทึกรายงานเรียบร้อยแล้วที่:\n{save_path}\n\nและซิงก์เข้าสู่ Modding-Knowledge ที่:\n{ki_path}"
                )
            except Exception as e:
                QMessageBox.critical(self, "เกิดข้อผิดพลาด", f"ไม่สามารถบันทึกไฟล์ได้:\n{e}")
