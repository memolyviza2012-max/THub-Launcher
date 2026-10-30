from core.qt_tasks import BackgroundTasks
import copy
import os
import sys
import json
import re
import subprocess
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QComboBox, QCheckBox, QTextEdit, QFrame, QMessageBox, QApplication,
    QStackedWidget, QScrollArea, QMenu, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap

from core.engine_scanner import EngineScanner
from core.knowledge_service import KnowledgeService
from core.font_service import FontService
from core.art_harvester_service import ArtHarvesterService
from core.mod_adoption_service import ModAdoptionService
from core.tool_launcher import ToolLauncher
from ui_pyqt6.dialogs.font_gallery_dialog import FontGalleryDialog
from ui_pyqt6.dialogs.art_gallery_dialog_qt import ArtGalleryDialogQt
from ai.prompt_engine import PromptEngine
from i18n_helper import _


class AIHelperViewQt(QWidget):
    """
    Spotlight Feature 1: AI Helper Command Center in PyQt6.
    Tri-Deck Studio Architecture:
      - Col 1: Font Studio & Engine Inspector (320px)
      - Col 2: Protocols Deck & Quick Presets (310px)
      - Col 3: Master Plan Studio with 2x3 Plan Grid, Live Editor & Terminal Runner (Stretch)
      - Silent Auto-Save to <workspace>/ai_instructions.md
      - Engine Scanner & Knowledge Base integration
      - Engine-Curated Thai Font & PUA mapping suite
      - Legacy Mod Continuation & Adoption
      - Official 4K Background & Cover Art Harvester (Sony PS5 & Steam)
    """

    adopt_requested = pyqtSignal(dict)
    cover_updated = pyqtSignal(dict)


    PROMPT_MODES_CONFIG = {
        "master": {
            "icon": "🎮",
            "name": "แผนงานรวม (Master)",
            "name_en": "Master Blueprint",
            "desc": "วางโครงสร้าง 10 หมวด",
            "desc_en": "10-section blueprint",
            "category": "คลังคำสั่งหลัก (Core Operations)",
            "category_en": "Core Operations",
            "color": "#0284c7",
            "border": "#38bdf8",
            "bg": "rgba(2, 132, 199, 0.22)",
            "tip": "สร้าง Master Prompt ละเอียด 10 หมวดหมู่สำหรับการวางโครงสร้างโปรเจกต์",
            "file": "ai_instructions.md",
        },
        "step4": {
            "icon": "🧪",
            "name": "โฟกัสสเต็ป 4 (POC)",
            "name_en": "Step 4 Focus (POC)",
            "desc": "สกัดข้อความ & 2 ไฟล์",
            "desc_en": "Extract & 2 CSVs",
            "category": "คลังคำสั่งหลัก (Core Operations)",
            "category_en": "Core Operations",
            "color": "#10b981",
            "border": "#34d399",
            "bg": "rgba(16, 185, 129, 0.22)",
            "tip": "ลุยเจาะจงขั้นตอนที่ 4 สกัดข้อความ รวบรวม 2 ไฟล์ (en_original.csv & translate_TH.csv) และทำ POC",
            "file": "step4_instructions.md",
        },
        "bible": {
            "icon": "📖",
            "name": "เขียนคัมภีร์ (Bible)",
            "name_en": "Modding Bible",
            "desc": "ถอดรหัส & ลงคลังความรู้",
            "desc_en": "Reverse-eng & KB sync",
            "category": "คลังคำสั่งหลัก (Core Operations)",
            "category_en": "Core Operations",
            "color": "#d97706",
            "border": "#fbbf24",
            "bg": "rgba(217, 119, 6, 0.22)",
            "tip": "สร้าง Prompt ถอดรหัสโครงสร้างไฟล์และเขียนคัมภีร์ Modding Bible บันทึกลงคลังความรู้",
            "file": "bible_instructions.md",
        },
        "persona": {
            "icon": "🎭",
            "name": "QA 7 เสาหลัก (Auto Loop)",
            "name_en": "7 Pillars QA (Auto Loop)",
            "desc": "วนลูป 1-7 อัตโนมัติ",
            "desc_en": "Autonomous 7-pass loop",
            "category": "งานขัดเกลา & สานต่อ (Refinement)",
            "category_en": "Refinement & Continuity",
            "color": "#be123c",
            "border": "#fb7185",
            "bg": "rgba(190, 18, 60, 0.22)",
            "tip": "รันพิธีสาร State Machine ตรวจสอบบทแปลวนลูป 1-7 เสาหลักอัตโนมัติ เจาะลึกทีละเสา ไม่รวบรัด ไม่ข้ามขั้นตอน",
            "file": "persona_instructions.md",
        },
        "continue": {
            "icon": "🔄",
            "name": "สานต่องานเดิม (Adopt)",
            "name_en": "Adopt Legacy Mod",
            "desc": "วิเคราะห์ไฟล์ & สั่งลุยต่อ",
            "desc_en": "Analyze legacy files",
            "category": "งานขัดเกลา & สานต่อ (Refinement)",
            "category_en": "Refinement & Continuity",
            "color": "#059669",
            "border": "#34d399",
            "bg": "rgba(5, 150, 105, 0.22)",
            "tip": "สร้าง Prompt วิเคราะห์และสั่งการ AI ให้สานต่อโปรเจกต์ม็อดเดิมที่นำเข้า",
            "file": "continuation_instructions.md",
        },
        "translate": {
            "icon": "🌐",
            "name": "แปลภาษาด้วย Agent",
            "name_en": "Agent Local Translation",
            "desc": "แปลเอง 100% ไม่ง้อ API",
            "desc_en": "Autonomous Zero-API",
            "category": "งานขัดเกลา & สานต่อ (Refinement)",
            "category_en": "Refinement & Continuity",
            "color": "#8b5cf6",
            "border": "#a78bfa",
            "bg": "rgba(139, 92, 246, 0.22)",
            "tip": "ให้ AI Agent แปลภาษาเองทั้งหมดโดยใช้โควต้าตนเอง ยึดตาม Glossary และ AI Prompt จาก TStudio (Zero API / Web)",
            "file": "translate_instructions.md",
        },
    }

    def __init__(self, projects=None, active_project=None, parent=None, font_service=None):
        super().__init__(parent)
        self.tasks = BackgroundTasks(self)
        self._prompt_generation = 0
        self.projects = projects or []
        self.active_project = active_project or (self.projects[0] if self.projects else None)
        self.kb_service = KnowledgeService.get_instance()
        self.font_service = font_service or FontService()
        self.selected_font_id = "prompt"
        self.selected_font_variant = None
        self._current_engine_name = "Unreal Engine"

        self.current_mode = "agent"  # default: agent
        self.prompt_type = "master"  # default: master blueprint
        self.agent_checkboxes = {}
        self.plan_card_buttons = {}

        self._prompt_timer = QTimer(self)
        self._prompt_timer.setSingleShot(True)
        self._prompt_timer.setInterval(120)  # 120ms debounce
        self._prompt_timer.timeout.connect(self._rebuild_prompt)

        self._build_ui()
        if self.active_project:
            self._update_project_details()

    def _schedule_rebuild_prompt(self):
        """Debounced prompt rebuild to prevent main-thread freeze during font/option switching."""
        self._prompt_timer.start()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 8, 14, 14)
        main_layout.setSpacing(10)

        # 1. Top Header & Mode Switcher Bar
        main_layout.addWidget(self._create_header_and_tabs())

        # 2. Tri-Deck Studio Split Layout
        split_layout = QHBoxLayout()
        split_layout.setSpacing(12)

        # Column 1: Font Studio & Engine Inspector (320px)
        split_layout.addWidget(self._create_font_studio_panel())

        # Column 2: Protocols Deck & Quick Presets (310px)
        split_layout.addWidget(self._create_protocols_deck_panel())

        # Column 3: Master Plan Studio with 2x3 Grid & Editor (Stretch)
        split_layout.addWidget(self._create_master_plan_studio(), stretch=1)

        main_layout.addLayout(split_layout)

    # =========================================================================
    # Header & Mode Switcher
    # =========================================================================
    def _create_header_and_tabs(self):
        banner = QFrame()
        banner.setProperty("class", "ContentBanner")
        b_layout = QVBoxLayout(banner)
        b_layout.setContentsMargins(14, 10, 14, 10)
        b_layout.setSpacing(8)

        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        self.lbl_b_title = QLabel(_("🤖 AI Modding Copilot & Tri-Deck Studio"))
        self.lbl_b_title.setStyleSheet("color: #c084fc; font-size: 16px; font-weight: bold;")
        title_col.addWidget(self.lbl_b_title)

        self.lbl_mode_sub = QLabel(_("โหมดปฏิบัติการสำหรับ AI ที่มี Terminal และสิทธิ์แก้ไขไฟล์ในเครื่อง (Claude Code / Antigravity / Cursor)"))
        self.lbl_mode_sub.setProperty("class", "Muted")
        self.lbl_mode_sub.setStyleSheet("font-size: 11px;")
        title_col.addWidget(self.lbl_mode_sub)
        top_row.addLayout(title_col)
        top_row.addStretch()

        # Mode Pills: Web Chat vs Agent
        tabs_box = QFrame()
        tabs_box.setProperty("class", "SegmentBox")
        tabs_layout = QHBoxLayout(tabs_box)
        tabs_layout.setContentsMargins(3, 3, 3, 3)
        tabs_layout.setSpacing(4)

        self.btn_mode_chat = QPushButton(_("💬 ที่ปรึกษา (Web Chat)"))
        self.btn_mode_chat.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_mode_chat.clicked.connect(lambda: self._set_mode("chat"))
        tabs_layout.addWidget(self.btn_mode_chat)

        self.btn_mode_agent = QPushButton(_("💻 ปฏิบัติการ (Agent)"))
        self.btn_mode_agent.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_mode_agent.clicked.connect(lambda: self._set_mode("agent"))
        tabs_layout.addWidget(self.btn_mode_agent)

        top_row.addWidget(tabs_box)
        b_layout.addLayout(top_row)

        self._refresh_tab_styles()
        return banner

    # =========================================================================
    # Column 1: Font Studio & Engine Inspector (Width 320px)
    # =========================================================================
    def _create_font_studio_panel(self):
        scroll = QScrollArea()
        scroll.setFixedWidth(330)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        card = QFrame()
        card.setProperty("class", "PanelCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # 1. Project Selector
        self.lbl_proj = QLabel(_("🎮 เลือกโปรเจกต์เป้าหมาย:"))
        self.lbl_proj.setProperty("class", "CardTitle")
        layout.addWidget(self.lbl_proj)

        self.cbo_project = QComboBox()
        self._populate_projects_combo()
        self.cbo_project.currentIndexChanged.connect(self._on_project_changed)
        layout.addWidget(self.cbo_project)

        self.btn_adopt_legacy = QPushButton(_("🔄 สานต่องาน && นำเข้าโฟลเดอร์เดิม..."))
        self.btn_adopt_legacy.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_adopt_legacy.setToolTip(_("สแกนโครงสร้างและนำเข้าโปรเจกต์ม็อดที่เคยทำไว้เดิมเข้าสู่ THub"))
        self.btn_adopt_legacy.setStyleSheet("""
            QPushButton {
                background-color: rgba(139, 92, 246, 0.12);
                color: #c084fc;
                border: 1px dashed rgba(168, 85, 247, 0.5);
                border-radius: 6px;
                padding: 5px 8px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(139, 92, 246, 0.28);
                color: #ffffff;
                border-color: #a855f7;
            }
        """)
        self.btn_adopt_legacy.clicked.connect(lambda: self.adopt_requested.emit(self.active_project or {}))
        layout.addWidget(self.btn_adopt_legacy)

        # 2. Engine Detection Card
        self.engine_card = QFrame()
        self.engine_card.setProperty("class", "InnerCard")
        ec_layout = QVBoxLayout(self.engine_card)
        ec_layout.setContentsMargins(10, 8, 10, 8)
        ec_layout.setSpacing(3)

        self.lbl_engine_title = QLabel("⚙️ Game Engine: กำลังตรวจสอบ...")
        self.lbl_engine_title.setStyleSheet("color: #38bdf8; font-size: 11px; font-weight: bold;")
        ec_layout.addWidget(self.lbl_engine_title)

        self.lbl_engine_tools = QLabel("เครื่องมือแนะนำ: TStudio, TRun")
        self.lbl_engine_tools.setProperty("class", "Muted")
        self.lbl_engine_tools.setStyleSheet("font-size: 10px;")
        ec_layout.addWidget(self.lbl_engine_tools)
        layout.addWidget(self.engine_card)

        # 3. Engine-Curated Thai Font Section
        font_box = QFrame()
        font_box.setProperty("class", "InnerCard")
        fb_layout = QVBoxLayout(font_box)
        fb_layout.setContentsMargins(10, 8, 10, 8)
        fb_layout.setSpacing(6)

        self.lbl_font_header = QLabel(_("🔤 สตูดิโอฟอนต์ไทย (PUA 2,208 Glyphs):"))
        self.lbl_font_header.setProperty("class", "CardTitle")
        fb_layout.addWidget(self.lbl_font_header)

        self.lbl_font_rec = QLabel("⭐ แนะนำสำหรับ Engine: กำลังคำนวณ...")
        self.lbl_font_rec.setStyleSheet("color: #fbbf24; font-size: 10px; font-weight: bold;")
        fb_layout.addWidget(self.lbl_font_rec)

        self.cbo_font = QComboBox()
        self.cbo_font.currentIndexChanged.connect(self._on_font_changed)
        fb_layout.addWidget(self.cbo_font)

        # Style / Weight Selector
        style_row = QHBoxLayout()
        style_row.setSpacing(6)
        self.lbl_font_style = QLabel(_("รูปแบบ / น้ำหนัก:"))
        self.lbl_font_style.setStyleSheet("color: #cbd5e1; font-size: 11px; font-weight: bold;")
        style_row.addWidget(self.lbl_font_style)

        self.cbo_font_style = QComboBox()
        self.cbo_font_style.currentIndexChanged.connect(self._on_font_style_changed)
        style_row.addWidget(self.cbo_font_style, stretch=1)
        fb_layout.addLayout(style_row)

        # 16:9 Specimen Card (Interactive, Click to open HD viewer)
        self.lbl_font_preview = QLabel()
        self.lbl_font_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_font_preview.setFixedHeight(170)
        self.lbl_font_preview.setProperty("class", "SegmentBox")
        self.lbl_font_preview.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lbl_font_preview.setToolTip(_("🔍 คลิกที่ภาพเพื่อดูตัวอย่างขยายระดับ Full HD (1080p)"))
        self.lbl_font_preview.mousePressEvent = lambda e: self._open_hd_preview()
        fb_layout.addWidget(self.lbl_font_preview)

        # Meta & Quick Zoom hint row
        meta_row = QHBoxLayout()
        self.lbl_font_meta = QLabel("สไตล์ฟอนต์ • PUA 2,208 Glyphs ครบชุด")
        self.lbl_font_meta.setStyleSheet("color: #38bdf8; font-size: 9px;")
        meta_row.addWidget(self.lbl_font_meta)

        meta_row.addStretch()

        self.btn_quick_hd = QPushButton(_("🔍 ดูภาพขยาย HD"))
        self.btn_quick_hd.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_quick_hd.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #a78bfa;
                border: 1px solid rgba(167, 139, 250, 0.4);
                border-radius: 4px;
                padding: 1px 6px;
                font-size: 9px;
            }
            QPushButton:hover {
                background: rgba(167, 139, 250, 0.15);
                color: #c084fc;
            }
        """)
        self.btn_quick_hd.clicked.connect(lambda: self._open_hd_preview())
        meta_row.addWidget(self.btn_quick_hd)
        fb_layout.addLayout(meta_row)

        # Action Buttons Row
        btn_font_row = QHBoxLayout()
        btn_font_row.setSpacing(6)

        self.btn_browse_gallery = QPushButton(_("🖼️ คลังฟอนต์"))
        self.btn_browse_gallery.setProperty("class", "BtnSecondary")
        self.btn_browse_gallery.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_browse_gallery.setToolTip(_("เปิดคลังฟอนต์ทั้งหมด (Font Gallery Dialog)"))
        self.btn_browse_gallery.setStyleSheet("padding: 5px 6px; font-size: 10px;")
        self.btn_browse_gallery.clicked.connect(self._open_font_gallery)
        btn_font_row.addWidget(self.btn_browse_gallery)

        self.btn_deploy_font = QPushButton(_("📥 ติดตั้งฟอนต์"))
        self.btn_deploy_font.setProperty("class", "BtnAI")
        self.btn_deploy_font.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_deploy_font.setToolTip(_("ติดตั้งฟอนต์และชุด Mapping ลงใน 03_Font_and_UI"))
        self.btn_deploy_font.setStyleSheet("padding: 5px 6px; font-size: 10px; font-weight: bold;")
        self.btn_deploy_font.clicked.connect(self._deploy_selected_font)
        btn_font_row.addWidget(self.btn_deploy_font)

        fb_layout.addLayout(btn_font_row)

        self.btn_unity_mcp = QPushButton(_("⚡ ตั้งค่า Unity Native Font MCP Server"))
        self.btn_unity_mcp.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_unity_mcp.setStyleSheet("""
            QPushButton {
                background-color: rgba(34, 197, 94, 0.15);
                color: #22c55e;
                border: 1px dashed rgba(34, 197, 94, 0.5);
                border-radius: 6px;
                padding: 5px 10px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(34, 197, 94, 0.3);
                color: #ffffff;
                border-color: #16a34a;
            }
        """)
        self.btn_unity_mcp.clicked.connect(self._setup_unity_mcp_server)
        self.btn_unity_mcp.setVisible(False)
        fb_layout.addWidget(self.btn_unity_mcp)

        self.btn_udk_mcp = QPushButton(_("⚡ ตั้งค่า UDK MCP Server"))
        self.btn_udk_mcp.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_udk_mcp.setStyleSheet("""
            QPushButton {
                background-color: rgba(59, 130, 246, 0.15);
                color: #3b82f6;
                border: 1px dashed rgba(59, 130, 246, 0.5);
                border-radius: 6px;
                padding: 5px 10px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(59, 130, 246, 0.3);
                color: #ffffff;
                border-color: #2563eb;
            }
        """)
        self.btn_udk_mcp.clicked.connect(self._setup_udk_mcp_server)
        self.btn_udk_mcp.setVisible(False)
        fb_layout.addWidget(self.btn_udk_mcp)

        self.lbl_deploy_status = QLabel("")
        self.lbl_deploy_status.setStyleSheet("color: #10b981; font-size: 9px; font-weight: bold;")
        self.lbl_deploy_status.setWordWrap(True)
        fb_layout.addWidget(self.lbl_deploy_status)

        layout.addWidget(font_box)

        # 4. Official Artwork & 4K Background Harvester Section
        art_box = QFrame()
        art_box.setProperty("class", "InnerCard")
        ab_layout = QVBoxLayout(art_box)
        ab_layout.setContentsMargins(10, 8, 10, 8)
        ab_layout.setSpacing(6)

        lbl_art_header = QLabel(_("🖼️ ภาพพื้นหลัง & ปกเกม (Sony 4K / Steam):"))
        lbl_art_header.setProperty("class", "CardTitle")
        ab_layout.addWidget(lbl_art_header)

        self.lbl_art_status = QLabel(_("ดึงภาพ 4K Textless อัตโนมัติจาก Sony & Steam"))
        self.lbl_art_status.setStyleSheet("color: #38bdf8; font-size: 10px;")
        ab_layout.addWidget(self.lbl_art_status)

        # Action Buttons Row
        btn_art_row = QHBoxLayout()
        btn_art_row.setSpacing(6)

        self.btn_harvest_art = QPushButton(_("⚡ ดึงภาพอัตโนมัติ"))
        self.btn_harvest_art.setProperty("class", "BtnAI")
        self.btn_harvest_art.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_harvest_art.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7c3aed, stop:1 #2563eb);
                color: #ffffff;
                font-weight: bold;
                padding: 5px 8px;
                border-radius: 6px;
                font-size: 10px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #9333ea, stop:1 #3b82f6);
            }
        """)
        self.btn_harvest_art.setToolTip(_("ดึงภาพ 4K Textless จาก Sony PlayStation Store และ Steam CDN อัตโนมัติ"))
        self.btn_harvest_art.clicked.connect(self._harvest_artworks_quick)
        btn_art_row.addWidget(self.btn_harvest_art, stretch=1)

        self.btn_art_gallery = QPushButton(_("🖼️ คลังภาพ 4K"))
        self.btn_art_gallery.setProperty("class", "BtnSecondary")
        self.btn_art_gallery.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_art_gallery.setToolTip(_("เปิดคลังภาพเพื่อเลือกดูและตั้งภาพปกตามใจชอบ (Art Gallery)"))
        self.btn_art_gallery.setStyleSheet("padding: 5px 8px; font-size: 10px;")
        self.btn_art_gallery.clicked.connect(self._open_art_gallery)
        btn_art_row.addWidget(self.btn_art_gallery)

        ab_layout.addLayout(btn_art_row)

        # Quick Dimensions & Logo Row
        quick_dim_row = QHBoxLayout()
        quick_dim_row.setSpacing(4)

        for dim_k, dim_lbl in [
            ("widescreen", _("📺 16:9")),
            ("portrait", _("📱 แนวตั้ง")),
            ("hero", _("🚩 แบนเนอร์")),
            ("logo", _("✨ โลโก้")),
        ]:
            b = QPushButton(dim_lbl)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            if dim_k == "logo":
                b.setStyleSheet("background: rgba(124, 58, 237, 0.2); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.4); border-radius: 4px; padding: 3px 6px; font-size: 9px; font-weight: bold;")
                b.setToolTip(_("ดึงโลโก้เกมโปร่งใส (Transparent PNG) และเปิดไฟล์ให้ใช้งานทันที"))
            else:
                b.setStyleSheet("background: rgba(30, 41, 59, 0.6); color: #94a3b8; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 4px; padding: 3px 5px; font-size: 9px;")
                b.setToolTip(_("โหลดภาพขนาด {dim} จาก Official Store").format(dim=dim_lbl))
            b.clicked.connect(lambda chk, k=dim_k: self._quick_load_dimension_art(k))
            quick_dim_row.addWidget(b)

        ab_layout.addLayout(quick_dim_row)
        layout.addWidget(art_box)

        layout.addStretch()

        scroll.setWidget(card)
        return scroll


    # =========================================================================
    # Column 2: Protocols Deck & Quick Presets (Width 310px)
    # =========================================================================
    def _create_protocols_deck_panel(self):
        scroll = QScrollArea()
        scroll.setFixedWidth(310)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        card = QFrame()
        card.setProperty("class", "PanelCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Header Row: Title + Active Protocols Counter
        head_row = QHBoxLayout()
        head_row.setSpacing(6)

        lbl_deck_title = QLabel(_("⚙️ Agent Protocols"))
        lbl_deck_title.setProperty("class", "CardTitle")
        lbl_deck_title.setStyleSheet("color: #c084fc; font-weight: bold;")
        head_row.addWidget(lbl_deck_title)

        head_row.addStretch()

        self.lbl_protocols_count = QLabel("เปิดใช้ 8 / 11")
        self.lbl_protocols_count.setStyleSheet("""
            background: rgba(192, 132, 252, 0.15);
            color: #c084fc;
            border: 1px solid rgba(192, 132, 252, 0.35);
            border-radius: 10px;
            padding: 2px 8px;
            font-size: 10px;
            font-weight: bold;
        """)
        head_row.addWidget(self.lbl_protocols_count)
        layout.addLayout(head_row)

        # Quick Presets Buttons (POC / Standard / Extreme)
        preset_box = QFrame()
        preset_box.setProperty("class", "InnerCard")
        pb_layout = QVBoxLayout(preset_box)
        pb_layout.setContentsMargins(8, 6, 8, 6)
        pb_layout.setSpacing(5)

        lbl_preset_title = QLabel(_("⚡ พรีเซ็ตด่วน (Quick Presets):"))
        lbl_preset_title.setStyleSheet("color: #94a3b8; font-size: 10px; font-weight: bold;")
        pb_layout.addWidget(lbl_preset_title)

        btn_preset_row = QHBoxLayout()
        btn_preset_row.setSpacing(4)

        self.btn_preset_poc = QPushButton("⚡ ลุยไว (POC)")
        self.btn_preset_poc.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_preset_poc.setToolTip(_("เปิดโหมดลุยขั้นตอน 1-3 ทะลวง POC ทำเมนูหลักทันที ลดคำถามเพื่อความไว"))
        self.btn_preset_poc.setStyleSheet("""
            QPushButton {
                background: rgba(56, 189, 248, 0.12);
                color: #38bdf8;
                border: 1px solid rgba(56, 189, 248, 0.4);
                border-radius: 5px;
                padding: 4px 6px;
                font-size: 9px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(56, 189, 248, 0.28);
                color: #ffffff;
            }
        """)
        self.btn_preset_poc.clicked.connect(lambda: self._apply_preset("poc"))
        btn_preset_row.addWidget(self.btn_preset_poc)

        self.btn_preset_standard = QPushButton("🛡️ มาตรฐาน")
        self.btn_preset_standard.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_preset_standard.setToolTip(_("ค่าเริ่มต้นที่สมดุล: เปิดสร้างคัมภีร์, Auto-Tool, Safe Logging, MCP"))
        self.btn_preset_standard.setStyleSheet("""
            QPushButton {
                background: rgba(34, 197, 94, 0.12);
                color: #22c55e;
                border: 1px solid rgba(34, 197, 94, 0.4);
                border-radius: 5px;
                padding: 4px 6px;
                font-size: 9px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(34, 197, 94, 0.28);
                color: #ffffff;
            }
        """)
        self.btn_preset_standard.clicked.connect(lambda: self._apply_preset("standard"))
        btn_preset_row.addWidget(self.btn_preset_standard)

        self.btn_preset_extreme = QPushButton("🔥 ทะลวงขีดสุด")
        self.btn_preset_extreme.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_preset_extreme.setToolTip(_("เปิดใช้ทุกฟังก์ชัน: เจาะ byte header, สแกนลึก, Memory Hook Fallback"))
        self.btn_preset_extreme.setStyleSheet("""
            QPushButton {
                background: rgba(239, 68, 68, 0.12);
                color: #f87171;
                border: 1px solid rgba(239, 68, 68, 0.4);
                border-radius: 5px;
                padding: 4px 6px;
                font-size: 9px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(239, 68, 68, 0.28);
                color: #ffffff;
            }
        """)
        self.btn_preset_extreme.clicked.connect(lambda: self._apply_preset("extreme"))
        btn_preset_row.addWidget(self.btn_preset_extreme)

        pb_layout.addLayout(btn_preset_row)
        layout.addWidget(preset_box)

        # Dynamic Options Stack (Agent Protocols vs Chat Roadmap)
        self.options_stack = QStackedWidget()

        # Page 0: Chat Roadmap
        self.chat_page = self._build_chat_options_page()
        self.options_stack.addWidget(self.chat_page)

        # Page 1: Agent Protocols (Organized into 3 logical visual groups)
        self.agent_page = self._build_agent_options_page()
        self.options_stack.addWidget(self.agent_page)

        self.options_stack.setCurrentIndex(1)  # Default: Agent
        layout.addWidget(self.options_stack)

        # Modding Knowledge Base Section (Bottom of Deck)
        kb_title_row = QHBoxLayout()
        kb_title_row.setSpacing(6)
        self.lbl_kb = QLabel(_("📚 คัมภีร์ในคลังความรู้:"))
        self.lbl_kb.setProperty("class", "CardTitle")
        self.lbl_kb.setStyleSheet("margin-top: 4px;")
        kb_title_row.addWidget(self.lbl_kb)
        kb_title_row.addStretch()

        self.btn_refresh_kb = QPushButton("🔄")
        self.btn_refresh_kb.setToolTip(_("รีเฟรชคลังคัมภีร์และสแกนไฟล์ใหม่ทันที (Re-scan Knowledge Base)"))
        self.btn_refresh_kb.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_refresh_kb.setFixedSize(22, 22)
        self.btn_refresh_kb.setStyleSheet("""
            QPushButton {
                background: rgba(56, 189, 248, 0.1);
                color: #38bdf8;
                border: 1px solid rgba(56, 189, 248, 0.3);
                border-radius: 4px;
                font-size: 10px;
                padding: 0px;
            }
            QPushButton:hover {
                background: rgba(56, 189, 248, 0.25);
                color: #ffffff;
            }
        """)
        self.btn_refresh_kb.clicked.connect(self._on_refresh_kb)
        kb_title_row.addWidget(self.btn_refresh_kb)
        layout.addLayout(kb_title_row)

        kb_box = QFrame()
        kb_box.setProperty("class", "InnerCard")
        kb_layout = QVBoxLayout(kb_box)
        kb_layout.setContentsMargins(10, 8, 10, 8)
        kb_layout.setSpacing(2)

        self.lbl_guides = QLabel("กำลังสแกน Modding-Knowledge...")
        self.lbl_guides.setStyleSheet("color: #38bdf8; font-size: 10px;")
        self.lbl_guides.setWordWrap(True)
        kb_layout.addWidget(self.lbl_guides)

        lbl_kb_link = QLabel("🌐 ซิงค์ความรู้ล่าสุดเสมอจาก GitHub Repository")
        lbl_kb_link.setProperty("class", "SubText")
        lbl_kb_link.setStyleSheet("font-size: 9px; font-style: italic;")
        kb_layout.addWidget(lbl_kb_link)

        layout.addWidget(kb_box)
        layout.addStretch()

        scroll.setWidget(card)
        return scroll

    def _build_agent_options_page(self):
        page = QFrame()
        page.setProperty("class", "InnerCard")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # 11 Protocols organized into 3 logical visual groups:
        # Group 1: 🚀 Core Execution (ลุยงานหลัก & POC)
        # Group 2: 🎮 Engine Bridges & MCP (การเชื่อมต่อระบบ)
        # Group 3: 🛡️ Safety & Quality (ความปลอดภัย & เจาะลึก)
        protocol_groups = [
            (
                "🚀 ลุยงานหลัก & POC (Core Execution)",
                [
                    ("auto_poc", "⚡ Auto-Pilot 1-3 (POC Fast-Track)", "ลุยขั้นตอน 1-3 รวดเดียวจนแพตช์ Main Menu เพื่อเช็คภาษาไทย", True),
                    ("extreme_breakthrough", "🔥 ฝ่าทางตันขั้นสูงสุด (Extreme Breakthrough)", "ค้นหาข้อมูลเชิงลึกและสร้างเครื่องมือเฉพาะกิจขึ้นมาเองเพื่อสำเร็จ", True),
                    ("auto_tool", "🔧 โหลดเครื่องมืออัตโนมัติ", "สแกนหรือโหลด binary จาก GitHub เมื่อขาด", True),
                    ("sync_bible", "📖 สร้างคัมภีร์ & Sync Modding-Knowledge", "เขียนคัมภีร์ 10 หมวด สกัดฟอนต์ และอัปเดต Master Index", True),
                ]
            ),
            (
                "🎮 การเชื่อมต่อระบบ (Engine & MCP Bridges)",
                [
                    ("unity_mcp_font", "🎮 Unity Native Font MCP", "เชื่อมต่อ MCP Server ฝังฟอนต์ TextMeshPro Native", True),
                    ("udk_mcp_bridge", "🎮 UDK / UE3 MCP Bridge", "เชื่อมต่อ MCP ตรวจแพ็กเกจและควบคุม UDK Editor", True),
                    ("mem_hook", "🧩 อนุญาต Memory Hook Fallback", "BepInEx / UE4SS เมื่อแก้ไฟล์ตรงไม่ได้", False),
                ]
            ),
            (
                "🛡️ ความปลอดภัย & เจาะลึก (Safety & QA)",
                [
                    ("obstacle", "🚧 รับมืออุปสรรค & เสนอทางเลือก", "วิเคราะห์สาเหตุและถามเมื่อติดขัด ห้ามหยุดเงียบ", True),
                    ("write_log", "📋 บันทึก Session Log ลง Workspace", "สร้าง session_log.md ใน 05_Scripts", True),
                    ("min_confirm", "⚡ ลดคำถาม ขออนุมัติเฉพาะเรื่องเสี่ยง", "ลุยต่อเนื่องอัตโนมัติ ถามเฉพาะไฟล์เสี่ยง", False),
                    ("deep_scan", "🔬 Deep Scan Mode (เจาะลึก)", "ตรวจ byte header ทุกไฟล์อย่างละเอียด", False),
                ]
            )
        ]

        for grp_title, items in protocol_groups:
            lbl_g = QLabel(grp_title)
            lbl_g.setStyleSheet("color: #cbd5e1; font-size: 10px; font-weight: bold; margin-top: 4px;")
            layout.addWidget(lbl_g)

            for key, text, hint, default_val in items:
                chk = QCheckBox(text)
                chk.setChecked(default_val)
                chk.setStyleSheet("font-size: 10px; font-weight: 500;")
                chk.toggled.connect(self._on_option_toggled)
                layout.addWidget(chk)

                lbl_hint = QLabel(f"   ↳ {hint}")
                lbl_hint.setProperty("class", "SubText")
                lbl_hint.setStyleSheet("font-size: 9px; margin-bottom: 2px; color: #64748b;")
                lbl_hint.setWordWrap(True)
                layout.addWidget(lbl_hint)

                self.agent_checkboxes[key] = chk

        self._update_protocols_count()
        return page

    def _build_chat_options_page(self):
        page = QFrame()
        page.setProperty("class", "InnerCard")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(6)

        lbl_title = QLabel("🗺️ Roadmap 7 ขั้นตอนสำหรับ Web Chat:")
        lbl_title.setStyleSheet("color: #38bdf8; font-size: 11px; font-weight: bold;")
        layout.addWidget(lbl_title)

        steps = [
            "1. 📦 Extraction & Analysis (วิเคราะห์สกัดไฟล์)",
            "2. 🔤 Font & UI (ทำฟอนต์ไทย PUA เลื่อนสระ)",
            "3. 📖 Pre-Translation Glossary (ดึงคำเฉพาะ)",
            "4. 🧪 Proof of Concept (ทดสอบหน้าเมนูหลัก)",
            "5. 🛡️ Script ปลอดภัยแท็กโค้ด (%s, {0}, <color>)",
            "6. 🔍 Batch Translation & Automated QA",
            "7. 🚀 Build Release, คู่มือติดตั้ง & บันทึกคัมภีร์ลงคลังความรู้"
        ]

        for s in steps:
            lbl_s = QLabel(s)
            lbl_s.setProperty("class", "Muted")
            lbl_s.setStyleSheet("font-size: 10px; padding: 2px 0;")
            layout.addWidget(lbl_s)

        layout.addStretch()
        return page

    def _apply_preset(self, preset_name):
        presets = {
            "poc": {
                "auto_poc": True, "extreme_breakthrough": True, "auto_tool": True,
                "sync_bible": False, "unity_mcp_font": True, "udk_mcp_bridge": True,
                "obstacle": True, "write_log": True, "min_confirm": True,
                "deep_scan": False, "mem_hook": False
            },
            "standard": {
                "auto_poc": True, "extreme_breakthrough": True, "auto_tool": True,
                "sync_bible": True, "unity_mcp_font": True, "udk_mcp_bridge": True,
                "obstacle": True, "write_log": True, "min_confirm": False,
                "deep_scan": False, "mem_hook": False
            },
            "extreme": {
                "auto_poc": True, "extreme_breakthrough": True, "auto_tool": True,
                "sync_bible": True, "unity_mcp_font": True, "udk_mcp_bridge": True,
                "obstacle": True, "write_log": True, "min_confirm": True,
                "deep_scan": True, "mem_hook": True
            }
        }
        cfg = presets.get(preset_name, presets["standard"])
        for k, val in cfg.items():
            if k in self.agent_checkboxes:
                self.agent_checkboxes[k].blockSignals(True)
                self.agent_checkboxes[k].setChecked(val)
                self.agent_checkboxes[k].blockSignals(False)

        self._update_protocols_count()
        self._schedule_rebuild_prompt()

    def _update_protocols_count(self):
        if not hasattr(self, "lbl_protocols_count") or not self.agent_checkboxes:
            return
        active_count = sum(1 for chk in self.agent_checkboxes.values() if chk.isChecked())
        total_count = len(self.agent_checkboxes)
        self.lbl_protocols_count.setText(f"เปิดใช้ {active_count} / {total_count}")

    # =========================================================================
    # Column 3: Master Plan Studio (2x3 Grid, Code Editor, Terminal Runner)
    # =========================================================================
    def _create_master_plan_studio(self):
        right_card = QFrame()
        right_card.setProperty("class", "PanelCard")
        right_layout = QVBoxLayout(right_card)
        right_layout.setContentsMargins(14, 10, 14, 12)
        right_layout.setSpacing(8)

        # 1. Plan Cards 2x3 Grid Header
        grid_head = QHBoxLayout()
        grid_head.setSpacing(6)
        lbl_grid_title = QLabel(_("🗺️ เลือกแผนงานรวม (Master Plan Studio):"))
        lbl_grid_title.setProperty("class", "CardTitle")
        lbl_grid_title.setStyleSheet("color: #f1f5f9; font-weight: bold; font-size: 12px;")
        grid_head.addWidget(lbl_grid_title)
        grid_head.addStretch()

        self.lbl_auto_save = QLabel(_("⚡ ซิงค์ลง Workspace แล้ว"))
        self.lbl_auto_save.setStyleSheet("color: #10b981; font-size: 11px; font-weight: bold;")
        grid_head.addWidget(self.lbl_auto_save)
        right_layout.addLayout(grid_head)

        # 2x3 Grid Container
        grid_widget = QFrame()
        grid_widget.setProperty("class", "InnerCard")
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setContentsMargins(6, 6, 6, 6)
        grid_layout.setSpacing(6)

        plan_keys = [
            ("master", 0, 0),
            ("step4", 0, 1),
            ("bible", 0, 2),
            ("persona", 1, 0),
            ("continue", 1, 1),
            ("translate", 1, 2),
        ]

        for pkey, row, col in plan_keys:
            cfg = self.PROMPT_MODES_CONFIG.get(pkey, {})
            card_title = f"{cfg.get('icon', '🎮')}  {cfg.get('name', pkey)}\n   ↳ {cfg.get('desc', '')}".replace("&", "&&")
            btn = QPushButton(card_title)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(48)
            btn.setToolTip(cfg.get("tip", ""))
            btn.clicked.connect(lambda checked, k=pkey: self._set_prompt_type(k))
            grid_layout.addWidget(btn, row, col)
            self.plan_card_buttons[pkey] = btn

        right_layout.addWidget(grid_widget)

        # 2. Plan Status Strip & Action Buttons
        strip_layout = QHBoxLayout()
        strip_layout.setSpacing(8)

        self.lbl_plan_desc = QLabel("🎮 กำลังใช้งาน: แผนงานรวม (Master)")
        self.lbl_plan_desc.setStyleSheet("color: #38bdf8; font-size: 11px; font-weight: bold;")
        strip_layout.addWidget(self.lbl_plan_desc)

        strip_layout.addStretch()

        self.btn_save = QPushButton(_("💾 บันทึก"))
        self.btn_save.setProperty("class", "BtnSecondary")
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.clicked.connect(self._save_prompt_file)
        strip_layout.addWidget(self.btn_save)

        self.btn_copy = QPushButton(_("📋 คัดลอก Prompt"))
        self.btn_copy.setProperty("class", "BtnPrimary")
        self.btn_copy.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_copy.clicked.connect(self._copy_prompt)
        strip_layout.addWidget(self.btn_copy)

        right_layout.addLayout(strip_layout)

        # 2.5 TStudio Guardrail Banner (Dynamic for Agent Translation)
        self.tstudio_guard_box = QFrame()
        self.tstudio_guard_box.setProperty("class", "InnerCard")
        self.tstudio_guard_layout = QHBoxLayout(self.tstudio_guard_box)
        self.tstudio_guard_layout.setContentsMargins(10, 6, 10, 6)
        self.tstudio_guard_layout.setSpacing(8)

        self.lbl_tstudio_guard = QLabel()
        self.lbl_tstudio_guard.setWordWrap(True)
        self.lbl_tstudio_guard.setStyleSheet("font-size: 11px;")
        self.tstudio_guard_layout.addWidget(self.lbl_tstudio_guard, stretch=1)

        self.btn_open_tstudio = QPushButton(_("🚀 เปิด TStudio ตั้งค่า"))
        self.btn_open_tstudio.setProperty("class", "BtnPrimary")
        self.btn_open_tstudio.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_open_tstudio.clicked.connect(self._open_tstudio_for_active_project)
        self.tstudio_guard_layout.addWidget(self.btn_open_tstudio)

        self.tstudio_guard_box.setVisible(False)
        right_layout.addWidget(self.tstudio_guard_box)

        # 3. Consolas Code Prompt Editor
        self.txt_prompt = QTextEdit()
        self.txt_prompt.setProperty("class", "CodeEditor")
        self.txt_prompt.setStyleSheet(
            "padding: 12px; font-family: 'Consolas', 'Leelawadee UI', 'Courier New', monospace; "
            "font-size: 11px; line-height: 1.45; background: #0c0f17; color: #f1f5f9; border-radius: 8px;"
        )
        right_layout.addWidget(self.txt_prompt)

        # 4. Bottom Terminal Runner Bar
        runner_bar = QFrame()
        runner_bar.setProperty("class", "InnerCard")
        rb_layout = QHBoxLayout(runner_bar)
        rb_layout.setContentsMargins(10, 6, 10, 6)
        rb_layout.setSpacing(8)

        lbl_term_icon = QLabel("💻")
        lbl_term_icon.setStyleSheet("font-size: 12px;")
        rb_layout.addWidget(lbl_term_icon)

        self.lbl_cli_cmd = QLabel('$ claude "อ่าน ai_instructions.md แล้วเริ่มงาน"')
        self.lbl_cli_cmd.setStyleSheet("color: #a5f3fc; font-family: 'Consolas', monospace; font-size: 10px; font-weight: bold;")
        rb_layout.addWidget(self.lbl_cli_cmd, stretch=1)

        self.btn_copy_cli = QPushButton(_("📋 คัดลอกคำสั่งรัน CLI"))
        self.btn_copy_cli.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_copy_cli.setStyleSheet("""
            QPushButton {
                background: rgba(56, 189, 248, 0.15);
                color: #38bdf8;
                border: 1px solid rgba(56, 189, 248, 0.4);
                border-radius: 5px;
                padding: 4px 10px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(56, 189, 248, 0.3);
                color: #ffffff;
            }
        """)
        self.btn_copy_cli.clicked.connect(self._copy_cli_command)
        rb_layout.addWidget(self.btn_copy_cli)

        self.btn_open_terminal = QPushButton(_("⚡ เปิด PowerShell ใน Workspace"))
        self.btn_open_terminal.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_open_terminal.setStyleSheet("""
            QPushButton {
                background: rgba(168, 85, 247, 0.15);
                color: #c084fc;
                border: 1px solid rgba(168, 85, 247, 0.4);
                border-radius: 5px;
                padding: 4px 10px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(168, 85, 247, 0.3);
                color: #ffffff;
            }
        """)
        self.btn_open_terminal.clicked.connect(self._open_terminal)
        rb_layout.addWidget(self.btn_open_terminal)

        right_layout.addWidget(runner_bar)

        # Virtual proxy buttons for backwards compatibility with legacy callers/tests
        self.btn_type_master = QPushButton(_("🎮 แผนงานรวม (Master)"))
        self.btn_type_master.clicked.connect(lambda: self._set_prompt_type("master"))
        self.btn_type_bible = QPushButton(_("📖 เขียนคัมภีร์ (Bible)"))
        self.btn_type_bible.clicked.connect(lambda: self._set_prompt_type("bible"))
        self.btn_type_media = QPushButton(_("🎨 สื่อและโลโก้ (Media Kit)"))
        self.btn_type_media.clicked.connect(lambda: self._set_prompt_type("media_kit"))
        self.btn_type_continue = QPushButton(_("🔄 สานต่องาน (Adopt)"))
        self.btn_type_continue.clicked.connect(lambda: self._set_prompt_type("continue"))
        self.btn_type_persona = QPushButton(_("🎭 บุคลิก สรรพนาม & QA"))
        self.btn_type_persona.clicked.connect(lambda: self._set_prompt_type("persona"))
        self.btn_type_translate = QPushButton(_("🌐 แปลภาษาด้วย Agent"))
        self.btn_type_translate.clicked.connect(lambda: self._set_prompt_type("translate"))
        self.btn_prompt_picker = QPushButton()

        self._refresh_plan_card_styles()
        return right_card

    # =========================================================================
    # Plan Cards & Mode Switchers
    # =========================================================================
    def _set_prompt_type(self, ptype):
        self.prompt_type = ptype
        self._refresh_prompt_type_styles()
        self._refresh_plan_card_styles()
        self._schedule_rebuild_prompt()

    def _refresh_plan_card_styles(self):
        app_lang = os.environ.get("THUB_LANG", "th")
        is_th = (app_lang == "th")

        for pkey, btn in self.plan_card_buttons.items():
            cfg = self.PROMPT_MODES_CONFIG.get(pkey, {})
            icon = cfg.get("icon", "🎮")
            name = cfg.get("name" if is_th else "name_en", pkey)
            desc = cfg.get("desc" if is_th else "desc_en", "")
            btn_text = f"{icon}  {name}\n   ↳ {desc}".replace("&", "&&")
            btn.setText(btn_text)

            if pkey == self.prompt_type:
                color = cfg.get("color", "#0284c7")
                border = cfg.get("border", "#38bdf8")
                bg = cfg.get("bg", "rgba(2, 132, 199, 0.22)")
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {bg};
                        color: #ffffff;
                        border: 1.5px solid {border};
                        border-radius: 8px;
                        padding: 4px 10px;
                        font-size: 10px;
                        font-weight: bold;
                        text-align: left;
                    }}
                    QPushButton:hover {{
                        border-color: #ffffff;
                    }}
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {{
                        background-color: rgba(255, 255, 255, 0.03);
                        color: #94a3b8;
                        border: 1px solid rgba(255, 255, 255, 0.08);
                        border-radius: 8px;
                        padding: 4px 10px;
                        font-size: 10px;
                        font-weight: 500;
                        text-align: left;
                    }}
                    QPushButton:hover {{
                        background-color: rgba(255, 255, 255, 0.08);
                        color: #f1f5f9;
                        border-color: rgba(255, 255, 255, 0.2);
                    }}
                """)

        active_cfg = self.PROMPT_MODES_CONFIG.get(self.prompt_type, self.PROMPT_MODES_CONFIG["master"])
        active_name = active_cfg.get("name" if is_th else "name_en", self.prompt_type)
        active_icon = active_cfg.get("icon", "🎮")
        target_file = active_cfg.get("file", "ai_instructions.md")

        if hasattr(self, "lbl_plan_desc"):
            self.lbl_plan_desc.setText(f"{active_icon} ใช้งาน: {active_name}")
            self.lbl_plan_desc.setStyleSheet(f"color: {active_cfg.get('border', '#38bdf8')}; font-size: 11px; font-weight: bold;")

        if hasattr(self, "lbl_cli_cmd"):
            self.lbl_cli_cmd.setText(f'$ claude "อ่าน {target_file} แล้วเริ่มงาน"')

        # Dynamic TStudio Guardrail Banner (for Agent Local Translation)
        if hasattr(self, "tstudio_guard_box"):
            if self.prompt_type == "translate" and self.active_project:
                has_profile, has_glossary, has_prompt, prof = PromptEngine.has_tstudio_profile(self.active_project)
                preset_name = prof.get("preset_name", self.active_project.get("name", "Default"))
                glossary_count = len(prof.get("glossary", {}))
                self.tstudio_guard_box.setVisible(True)

                if has_glossary and has_prompt:
                    self.tstudio_guard_box.setStyleSheet("""
                        QFrame {
                            background-color: rgba(139, 92, 246, 0.15);
                            border: 1.5px solid #8b5cf6;
                            border-radius: 8px;
                        }
                    """)
                    self.lbl_tstudio_guard.setText(
                        f"🛡️ <b>เชื่อมต่อ TStudio สำเร็จ:</b> ตรวจพบ Profile <b>{preset_name}</b> | "
                        f"คลังคำศัพท์ทางการ: <b style='color:#a78bfa;'>{glossary_count} คำ</b> | "
                        f"System Tone: <b style='color:#10b981;'>พร้อมใช้งาน</b> (Zero-API Local Mode)"
                    )
                    self.lbl_tstudio_guard.setStyleSheet("color: #e2e8f0; font-size: 11px;")
                    self.btn_open_tstudio.setText(_("🚀 เปิด TStudio ตรวจสอบ/เพิ่มคำ"))
                    self.btn_open_tstudio.setStyleSheet("""
                        QPushButton {
                            background-color: #8b5cf6;
                            color: #ffffff;
                            border-radius: 6px;
                            font-weight: bold;
                            padding: 4px 10px;
                        }
                        QPushButton:hover {
                            background-color: #7c3aed;
                        }
                    """)
                else:
                    missing = []
                    if not has_glossary:
                        missing.append("คลังคำศัพท์ (Glossary)")
                    if not has_prompt:
                        missing.append("คำสั่งแนวทางการแปล (System Tone)")
                    missing_str = " และ ".join(missing)

                    self.tstudio_guard_box.setStyleSheet("""
                        QFrame {
                            background-color: rgba(239, 68, 68, 0.15);
                            border: 1.5px solid #ef4444;
                            border-radius: 8px;
                        }
                    """)
                    self.lbl_tstudio_guard.setText(
                        f"🛑 <b>ระงับการแปลอัตโนมัติ:</b> ยังไม่พบ <b>{missing_str}</b> ใน TStudio สำหรับเกมนี้<br/>"
                        f"<span style='color: #fca5a5;'>ตามกฎเหล็ก AI Agent ถูกห้ามแปลและห้ามคิดศัพท์เองโดยพลการ กรุณาสร้างข้อมูลใน TStudio ก่อน</span>"
                    )
                    self.lbl_tstudio_guard.setStyleSheet("color: #fee2e2; font-size: 11px;")
                    self.btn_open_tstudio.setText(_("🚀 เปิด TStudio ตั้งค่าทันที"))
                    self.btn_open_tstudio.setStyleSheet("""
                        QPushButton {
                            background-color: #ef4444;
                            color: #ffffff;
                            border-radius: 6px;
                            font-weight: bold;
                            padding: 4px 10px;
                        }
                        QPushButton:hover {
                            background-color: #dc2626;
                        }
                    """)
            else:
                self.tstudio_guard_box.setVisible(False)

    def _refresh_prompt_type_styles(self):
        """Maintains backwards compatibility for proxy picker button."""
        app_lang = os.environ.get("THUB_LANG", "th")
        is_th = (app_lang == "th")
        cfg = self.PROMPT_MODES_CONFIG.get(self.prompt_type, self.PROMPT_MODES_CONFIG["master"])
        name = cfg["name"] if is_th else cfg["name_en"]
        icon = cfg["icon"]
        if hasattr(self, "btn_prompt_picker"):
            self.btn_prompt_picker.setText(f"{icon}  {name}   ▾")

    def _set_mode(self, mode):
        self.current_mode = mode
        if mode == "chat":
            self.options_stack.setCurrentIndex(0)
        else:  # agent
            self.options_stack.setCurrentIndex(1)
        self._update_mode_description()
        self._refresh_tab_styles()
        self._schedule_rebuild_prompt()

    def _update_mode_description(self):
        if self.current_mode == "chat":
            self.lbl_mode_sub.setText(_("โหมดที่ปรึกษาสำหรับ Web Chat (ChatGPT / Claude) ที่ไม่มีสิทธิ์เข้าถึงไฟล์ในเครื่อง ออกแบบตาม Roadmap 7 ขั้นตอน"))
        else:  # agent
            self.lbl_mode_sub.setText(_("โหมดปฏิบัติการสำหรับ AI ที่มี Terminal และสิทธิ์แก้ไขไฟล์ในเครื่อง (Claude Code / Antigravity / Cursor)"))

    def _refresh_tab_styles(self):
        active_style_chat = """
            QPushButton {
                background-color: #0369a1;
                color: #ffffff;
                border: 1px solid #38bdf8;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 11px;
                font-weight: bold;
            }
        """
        active_style_agent = """
            QPushButton {
                background-color: #6b21a8;
                color: #ffffff;
                border: 1px solid #c084fc;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 11px;
                font-weight: bold;
            }
        """
        inactive_style = """
            QPushButton {
                background-color: transparent;
                color: #94a3b8;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1a2233;
                color: #f1f5f9;
            }
        """
        self.btn_mode_chat.setStyleSheet(active_style_chat if self.current_mode == "chat" else inactive_style)
        self.btn_mode_agent.setStyleSheet(active_style_agent if self.current_mode == "agent" else inactive_style)

    # =========================================================================
    # Project & Engine Detection
    # =========================================================================
    def _populate_projects_combo(self):
        self.cbo_project.blockSignals(True)
        self.cbo_project.clear()
        for p in self.projects:
            self.cbo_project.addItem(p.get("name", "Unknown"), p)
        if self.active_project:
            self.cbo_project.setCurrentText(self.active_project.get("name", ""))
        self.cbo_project.blockSignals(False)

    def _on_project_changed(self, index):
        p = self.cbo_project.currentData()
        if p:
            self.active_project = p
            self._update_project_details()

    def _update_project_details(self):
        if not self.active_project:
            return

        name = self.active_project.get("name", "Unknown")
        game_dir = self.active_project.get("game_dir", "")
        workspace_dir = self.active_project.get("path", "")
        saved_engine = self.active_project.get("engine")

        identity = (workspace_dir, name)
        def details():
            info = EngineScanner.detect_engine(game_dir=game_dir, workspace_dir=workspace_dir, title=name, saved_engine=saved_engine)
            guides = self.kb_service.find_guides_for_engine(info.get("engine_name", "Unknown Engine"),
                game_title=name, tech_keywords=info.get("detected_exts"), max_results=4)
            return info, guides
        self.tasks.submit("project-details", details, lambda result: self._project_details_ready(identity, result),
                          lambda error: self.lbl_guides.setText("อ่านข้อมูลไม่สำเร็จ: " + error))

    def _project_details_ready(self, identity, result):
        if not self.active_project or identity != (self.active_project.get("path", ""), self.active_project.get("name", "Unknown")):
            return
        engine_info, guides = result
        engine_name = engine_info.get("engine_name", "Unknown Engine")
        badge = engine_info.get("badge", engine_name)
        tier = engine_info.get("tier", "unknown")

        tier_confidence_map = {
            "saved": 100,
            "game_dir_root": 95,
            "game_dir_sub": 90,
            "workspace": 85,
            "heuristic": 75,
            "fallback": 40
        }
        confidence = tier_confidence_map.get(tier, 80)
        tools = ", ".join(engine_info.get("tools", ["TStudio", "TRun"]))

        self.lbl_engine_title.setText(f"⚙️ {badge} ({confidence}% Confidence)")
        self.lbl_engine_tools.setText(f"เครื่องมือแนะนำ: {tools}")

        if guides:
            guide_lines = []
            for g in guides:
                mtype = g.get("match_type")
                if mtype == "game_bible":
                    icon = "⭐"
                    prefix = "คัมภีร์ตรง:"
                elif mtype == "tech_guide":
                    icon = "🛠️"
                    prefix = "เทคนิค/เครื่องมือตรง:"
                elif mtype == "engine_guide":
                    icon = "📘"
                    prefix = "คู่มือ Engine:"
                else:
                    icon = "🎮"
                    prefix = "เกมอ้างอิง:"
                guide_lines.append(f"{icon} {prefix} {g['title']}")
            self.lbl_guides.setText("\n".join(guide_lines))
        else:
            self.lbl_guides.setText("ไม่พบคู่มือเฉพาะเกม (ใช้แนวทางวิเคราะห์อัตโนมัติ)")

        # Refresh engine-curated fonts
        self._refresh_font_recommendations(engine_name)

        # Update Unity Native Font MCP Visibility & Auto-activation
        is_unity = "unity" in (engine_name or "").lower()
        if hasattr(self, "btn_unity_mcp"):
            self.btn_unity_mcp.setVisible(is_unity)
        if hasattr(self, "agent_checkboxes") and "unity_mcp_font" in self.agent_checkboxes:
            self.agent_checkboxes["unity_mcp_font"].setVisible(is_unity)
            if is_unity:
                self.agent_checkboxes["unity_mcp_font"].setChecked(True)

        # Update UDK / UE3 MCP Visibility & Auto-activation
        is_ue3 = any(k in (engine_name or "").lower() for k in ["unreal engine 3", "ue3", "udk"])
        if hasattr(self, "btn_udk_mcp"):
            self.btn_udk_mcp.setVisible(is_ue3)
        if hasattr(self, "agent_checkboxes") and "udk_mcp_bridge" in self.agent_checkboxes:
            self.agent_checkboxes["udk_mcp_bridge"].setVisible(is_ue3)
            if is_ue3:
                self.agent_checkboxes["udk_mcp_bridge"].setChecked(True)

        self._update_protocols_count()
        self._refresh_plan_card_styles()
        self._rebuild_prompt()

    def _on_refresh_kb(self):
        """Re-scans Modding-Knowledge and refreshes detected guides immediately."""
        self.lbl_guides.setText("กำลังสแกนคลังคัมภีร์ใหม่...")
        self.tasks.submit("refresh-kb", self.kb_service.reindex, lambda result: self._update_project_details(),
                          lambda error: self.lbl_guides.setText("สแกนไม่สำเร็จ: " + error))

    # =========================================================================
    # Font Studio & Preview Handling
    # =========================================================================
    def _refresh_font_recommendations(self, engine_name):
        """Populates font combobox sorted by recommendation for the detected engine."""
        self._current_engine_name = engine_name
        self.cbo_font.blockSignals(True)
        self.cbo_font.clear()

        fonts = self.font_service.get_fonts_for_engine(engine_name)
        top_font = fonts[0] if fonts else None

        target_font_id = self.selected_font_id or (top_font["id"] if top_font else "prompt")
        selected_idx = 0

        for idx, f in enumerate(fonts):
            star = "⭐ " if f.get("is_recommended") else ""
            score = f.get("engine_score", 70)
            item_text = f"{star}{f['name_en']} ({f['name_th']}) - {score}%"
            self.cbo_font.addItem(item_text, f["id"])
            if f["id"] == target_font_id:
                selected_idx = idx

        self.cbo_font.setCurrentIndex(selected_idx)
        self.cbo_font.blockSignals(False)

        self.selected_font_id = self.cbo_font.currentData()
        if top_font:
            self.lbl_font_rec.setText(f"⭐ เหมาะที่สุดสำหรับ {engine_name}: {top_font['name_en']}")

        self._populate_font_styles(self.selected_font_id)
        self._update_font_preview()

    def _populate_font_styles(self, font_id, target_variant_rel=None):
        """Populates font style/weight combobox for the given font family."""
        if not hasattr(self, "cbo_font_style"):
            return
        self.cbo_font_style.blockSignals(True)
        self.cbo_font_style.clear()

        self.cbo_font_style.blockSignals(False)
        self.tasks.submit("font-variants", lambda: self.font_service.get_font_variants(font_id),
            lambda variants: self._font_styles_ready(font_id, target_variant_rel, variants))

    def _font_styles_ready(self, font_id, target_variant_rel, variants):
        if font_id != self.selected_font_id:
            return
        self.cbo_font_style.blockSignals(True)
        self.cbo_font_style.clear()
        if not variants:
            self.cbo_font_style.addItem("Regular (ปกติ)", None)
            self.selected_font_variant = None
            self.cbo_font_style.blockSignals(False)
            return

        target_fn = os.path.basename(target_variant_rel).lower() if target_variant_rel else None
        selected_idx = 0
        for idx, v in enumerate(variants):
            label = v.get("display_th", v.get("style_name", "Regular"))
            if v.get("is_default"):
                label += " (ค่าเริ่มต้น)"
            self.cbo_font_style.addItem(label, v)
            v_fn = os.path.basename(v.get("rel_path", "")).lower()
            if target_fn and (v_fn == target_fn or v.get("file_name", "").lower() == target_fn):
                selected_idx = idx
            elif not target_fn and v.get("is_default"):
                selected_idx = idx

        self.cbo_font_style.setCurrentIndex(selected_idx)
        self.selected_font_variant = self.cbo_font_style.currentData()
        self.cbo_font_style.blockSignals(False)
        self._update_font_preview()
        self._schedule_rebuild_prompt()

    def _on_font_changed(self, index):
        fid = self.cbo_font.currentData()
        if fid:
            self.selected_font_id = fid
            self._populate_font_styles(fid)
            self._update_font_preview()
            self._schedule_rebuild_prompt()

    def _on_font_style_changed(self, index):
        v = self.cbo_font_style.currentData()
        self.selected_font_variant = v
        self._update_font_preview()
        self._schedule_rebuild_prompt()

    def _update_font_preview(self):
        font_info = self.font_service.get_font_by_id(self.selected_font_id)
        if not font_info:
            return

        variant_rel = self.selected_font_variant.get("rel_path") if self.selected_font_variant else None
        preview_path = self.font_service.get_preview_path(self.selected_font_id, variant_rel_path=variant_rel)
        if preview_path and os.path.exists(preview_path):
            pix = QPixmap(preview_path)
            dpr = self.devicePixelRatioF() or 1.0
            target_w = int(296 * dpr)
            target_h = int(170 * dpr)
            scaled = pix.scaled(
                target_w, target_h,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            scaled.setDevicePixelRatio(dpr)
            self.lbl_font_preview.setPixmap(scaled)
        else:
            self.lbl_font_preview.setText(f"🔤 {font_info.get('name_en')}\n(คลิกเพื่อดูตัวอย่าง)")

        style_meta = ""
        if self.selected_font_variant:
            style_meta = f" • สไตล์: {self.selected_font_variant.get('display_th', '')}"
        self.lbl_font_meta.setText(f"{font_info.get('category')}{style_meta} • PUA 2,208 Glyphs")

    def _open_hd_preview(self, font_id=None):
        fid = font_id or self.selected_font_id
        font_info = self.font_service.get_font_by_id(fid)
        variant_rel = self.selected_font_variant.get("rel_path") if self.selected_font_variant else None
        preview_path = self.font_service.get_preview_path(fid, variant_rel_path=variant_rel)
        if not preview_path or not os.path.exists(preview_path):
            self._open_font_gallery()
            return

        from ui_pyqt6.dialogs.font_hd_viewer import FontHdViewerDialog
        dlg = FontHdViewerDialog(
            font_info,
            preview_path,
            initial_variant=self.selected_font_variant,
            parent=self,
            current_engine=self._current_engine_name
        )
        dlg.open_gallery_requested.connect(self._open_font_gallery)
        dlg.font_chosen_variant.connect(self._on_font_selected_from_dialog)
        dlg.exec()

    def _on_font_selected_from_dialog(self, font_id, variant=None):
        if not font_id:
            return
        self.selected_font_id = font_id
        self.cbo_font.blockSignals(True)
        for i in range(self.cbo_font.count()):
            if self.cbo_font.itemData(i) == font_id:
                self.cbo_font.setCurrentIndex(i)
                break
        self.cbo_font.blockSignals(False)

        target_variant_rel = variant.get("rel_path") if isinstance(variant, dict) else None
        self._populate_font_styles(font_id, target_variant_rel=target_variant_rel)
        if variant and isinstance(variant, dict):
            self.selected_font_variant = variant
        self._update_font_preview()
        self._schedule_rebuild_prompt()

    def _open_font_gallery(self):
        variant_rel = self.selected_font_variant.get("rel_path") if self.selected_font_variant else None
        dlg = FontGalleryDialog(
            current_engine=self._current_engine_name,
            active_font_id=self.selected_font_id,
            active_variant_rel=variant_rel,
            parent=self.window()
        )
        if dlg.exec():
            selected_id = dlg.selected_font_id
            selected_var = getattr(dlg, "selected_variant", None)
            if selected_id:
                self._on_font_selected_from_dialog(selected_id, selected_var)

    def _open_art_gallery(self):
        if not self.active_project:
            QMessageBox.warning(self.window(), _("แจ้งเตือน"), _("กรุณาเลือกโปรเจกต์ม็อดก่อน"))
            return

        dlg = ArtGalleryDialogQt(
            project=self.active_project,
            game_name=self.active_project.get("name", ""),
            workspace_path=self.active_project.get("path", ""),
            parent=self.window()
        )
        def on_cover_chosen(chosen_path):
            self.lbl_art_status.setText(_("✅ เปลี่ยนภาพปกหลักเรียบร้อยแล้ว"))
            self.cover_updated.emit(self.active_project)

        dlg.cover_selected.connect(on_cover_chosen)
        dlg.exec()

    def _harvest_artworks_quick(self):
        if not self.active_project:
            QMessageBox.warning(self.window(), _("แจ้งเตือน"), _("กรุณาเลือกโปรเจกต์ก่อนดึงภาพ"))
            return

        game_name = self.active_project.get("name", "")
        workspace_path = self.active_project.get("path", "")
        self.lbl_art_status.setText(_("⏳ กำลังค้นหาและดึงภาพจาก Sony & Steam..."))
        self.btn_harvest_art.setEnabled(False)

        def work():
            return ArtHarvesterService.harvest_all_artworks(game_name, workspace_path)

        def on_done(res):
            self.btn_harvest_art.setEnabled(True)
            if res and res.get("success"):
                total = res.get("total_images", 0)
                sony = res.get("sony_count", 0)
                steam = res.get("steam_count", 0)
                self.lbl_art_status.setText(_("✅ ดึงสำเร็จ {total} ภาพ (Sony: {sony}, Steam: {steam})").format(
                    total=total, sony=sony, steam=steam
                ))
                self.cover_updated.emit(self.active_project)
                self._open_art_gallery()
            else:
                self.lbl_art_status.setText(_("⚠️ ไม่พบภาพใหม่จาก Sony/Steam"))
                self._open_art_gallery()

        self.tasks.submit(
            "harvest-art-quick",
            work,
            on_done,
            lambda err: self._on_harvest_quick_error(err)
        )

    def _on_harvest_quick_error(self, err):
        self.btn_harvest_art.setEnabled(True)
        self.lbl_art_status.setText(_("❌ เกิดข้อผิดพลาดในการดึงภาพ"))
        QMessageBox.warning(self.window(), _("ข้อผิดพลาด"), str(err))


    def _deploy_selected_font(self):
        if not self.active_project:
            QMessageBox.warning(self.window(), _("แจ้งเตือน"), _("กรุณาเลือกโปรเจกต์ม็อดก่อน"))
            return

        proj_path = self.active_project.get("path", "")
        if not proj_path or not os.path.exists(proj_path):
            QMessageBox.warning(self.window(), _("แจ้งเตือน"), _("ไม่พบโฟลเดอร์ Workspace ของโปรเจกต์"))
            return

        self.btn_deploy_font.setEnabled(False)
        self.lbl_deploy_status.setText("⏳ กำลังติดตั้งฟอนต์และเครื่องมือลงใน 03_Font_and_UI...")
        self.lbl_deploy_status.setStyleSheet("color: #38bdf8; font-size: 9px; font-weight: bold;")
        QApplication.processEvents()

        try:
            variant_rel = self.selected_font_variant.get("rel_path") if self.selected_font_variant else None
            res = self.font_service.deploy_font_to_project(
                self.selected_font_id,
                proj_path,
                selected_variant_rel_path=variant_rel
            )
            if res.get("success"):
                target_dir = os.path.join(proj_path, "03_Font_and_UI")
                style_name = res.get("style_title") or (self.selected_font_variant.get("display_th") if self.selected_font_variant else "")
                style_info = f" ({style_name})" if style_name else ""
                self.lbl_deploy_status.setText(f"⚡ ติดตั้ง {res.get('font_name')}{style_info} เรียบร้อยแล้ว!")
                self.lbl_deploy_status.setStyleSheet("color: #10b981; font-size: 9px; font-weight: bold;")
                self._schedule_rebuild_prompt()

                QMessageBox.information(
                    self.window(),
                    _("ติดตั้งสำเร็จ"),
                    f"✅ ติดตั้งฟอนต์ {res.get('font_name')}{style_info} และชุด Mapping สำเร็จ!\n\n"
                    f"ไฟล์ที่ติดตั้งลงใน {target_dir}:\n"
                    f"  • ไฟล์ฟอนต์ TTF/OTF ทุกรูปแบบในตระกูลฟอนต์\n"
                    f"  • สไตล์หลักที่เลือก: {style_name or 'Default'}\n"
                    f"  • Mapping.json (2,208 อักขระ)\n"
                    f"  • Char.txt (Glyph List)\n"
                    f"  • thai_font_mapper.py (Script แปลง PUA)\n\n"
                    f"พร้อมใช้งานร่วมกับ Master Prompt ได้ทันที!"
                )
            else:
                self.lbl_deploy_status.setText(f"❌ ติดตั้งไม่สำเร็จ: {res.get('message')}")
                self.lbl_deploy_status.setStyleSheet("color: #ef4444; font-size: 9px; font-weight: bold;")
                QMessageBox.critical(self.window(), _("ล้มเหลว"), f"เกิดข้อผิดพลาดในการติดตั้ง: {res.get('message')}")
        except Exception as e:
            self.lbl_deploy_status.setText(f"❌ เกิดข้อผิดพลาด: {e}")
            self.lbl_deploy_status.setStyleSheet("color: #ef4444; font-size: 9px; font-weight: bold;")
            QMessageBox.critical(self.window(), _("ข้อผิดพลาด"), f"ไม่สามารถติดตั้งฟอนต์ได้: {e}")
        finally:
            self.btn_deploy_font.setEnabled(True)

    # =========================================================================
    # MCP Servers Setup
    # =========================================================================
    def _setup_unity_mcp_server(self):
        """Sets up Unity Native Thai Font MCP server in workspace and registers in mcp_config.json."""
        if not self.active_project:
            QMessageBox.warning(self, _("แจ้งเตือน"), _("กรุณาเลือกโปรเจกต์ม็อดก่อน"))
            return

        proj_path = self.active_project.get("path", "")
        if not proj_path or not os.path.exists(proj_path):
            QMessageBox.warning(self, _("แจ้งเตือน"), _("ไม่พบโฟลเดอร์ Workspace ของโปรเจกต์"))
            return

        try:
            mcp_script_src = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "..", "tools", "flagship", "GameBridges", "Unity", "mcp", "unity_font_mcp_server.py")
            )
            scripts_dir = os.path.join(proj_path, "05_Scripts_and_Tools")
            os.makedirs(scripts_dir, exist_ok=True)
            dst_script = os.path.join(scripts_dir, "unity_font_mcp_server.py")
            if os.path.exists(mcp_script_src):
                import shutil
                shutil.copy2(mcp_script_src, dst_script)

            proj_mcp_cfg = os.path.join(proj_path, "mcp_config.json")
            mcp_data = {"mcpServers": {}}
            if os.path.exists(proj_mcp_cfg):
                try:
                    with open(proj_mcp_cfg, "r", encoding="utf-8") as f:
                        mcp_data = json.load(f)
                except Exception:
                    mcp_data = {"mcpServers": {}}

            mcp_data.setdefault("mcpServers", {})["unity-native-font"] = {
                "command": "python",
                "args": [dst_script],
                "env": {
                    "PYTHONIOENCODING": "utf-8"
                }
            }

            with open(proj_mcp_cfg, "w", encoding="utf-8") as f:
                json.dump(mcp_data, f, ensure_ascii=False, indent=2)

            global_mcp_cfg = os.path.expanduser("~/.gemini/config/mcp_config.json")
            if os.path.exists(global_mcp_cfg):
                try:
                    with open(global_mcp_cfg, "r", encoding="utf-8") as f:
                        g_data = json.load(f)
                    g_data.setdefault("mcpServers", {})["unity-native-font"] = {
                        "command": "python",
                        "args": [mcp_script_src],
                        "env": {"PYTHONIOENCODING": "utf-8"}
                    }
                    with open(global_mcp_cfg, "w", encoding="utf-8") as f:
                        json.dump(g_data, f, ensure_ascii=False, indent=2)
                except Exception:
                    pass

            self.lbl_deploy_status.setText("⚡ ติดตั้ง Unity Native Font MCP Server เรียบร้อยแล้ว!")
            QMessageBox.information(
                self,
                _("ตั้งค่าสำเร็จ"),
                f"✅ ติดตั้ง Unity Native Font MCP Server สำเร็จ!\n\n"
                f"สคริปต์เซิร์ฟเวอร์: {dst_script}\n"
                f"การตั้งค่าโปรเจกต์: {proj_mcp_cfg}\n\n"
                f"เครื่องมือ MCP ที่พร้อมให้ AI Agent เรียกใช้งาน:\n"
                f"  • scan_unity_font_references\n"
                f"  • build_thai_subset\n"
                f"  • tune_thai_tone_marks (+160 units)\n"
                f"  • transplant_native_font\n"
                f"  • verify_native_font\n\n"
                f"พร้อมใช้งานร่วมกับ Claude Code, Antigravity, และ Cursor ได้ทันที!"
            )
        except Exception as e:
            QMessageBox.critical(self, _("ล้มเหลว"), f"เกิดข้อผิดพลาดในการตั้งค่า MCP: {e}")

    def _setup_udk_mcp_server(self):
        """Sets up UDK / UE3 MCP server in workspace and registers in mcp_config.json."""
        if not self.active_project:
            QMessageBox.warning(self, _("แจ้งเตือน"), _("กรุณาเลือกโปรเจกต์ม็อดก่อน"))
            return

        proj_path = self.active_project.get("path", "")
        if not proj_path or not os.path.exists(proj_path):
            QMessageBox.warning(self, _("แจ้งเตือน"), _("ไม่พบโฟลเดอร์ Workspace ของโปรเจกต์"))
            return

        try:
            from tools.flagship.GameBridges.UnrealEngine3.ue3_common import find_udk_installation

            udk_info = find_udk_installation()
            udk_found = udk_info.get("found", False)
            udk_exe = udk_info.get("executable", "Not found")

            bridge_dir = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "..", "tools", "flagship", "GameBridges", "UnrealEngine3")
            )
            mcp_script_src = os.path.join(bridge_dir, "mcp", "udk_mcp_server.py")
            ue3_common_src = os.path.join(bridge_dir, "ue3_common.py")
            udk_window_src = os.path.join(bridge_dir, "udk_window.py")

            scripts_dir = os.path.join(proj_path, "05_Scripts_and_Tools", "udk_mcp")
            os.makedirs(scripts_dir, exist_ok=True)
            dst_script = os.path.join(scripts_dir, "udk_mcp_server.py")

            import shutil
            if os.path.exists(mcp_script_src):
                shutil.copy2(mcp_script_src, dst_script)
            if os.path.exists(ue3_common_src):
                shutil.copy2(ue3_common_src, os.path.join(scripts_dir, "ue3_common.py"))
            if os.path.exists(udk_window_src):
                shutil.copy2(udk_window_src, os.path.join(scripts_dir, "udk_window.py"))

            proj_mcp_cfg = os.path.join(proj_path, "mcp_config.json")
            mcp_data = {"mcpServers": {}}
            if os.path.exists(proj_mcp_cfg):
                try:
                    with open(proj_mcp_cfg, "r", encoding="utf-8") as f:
                        mcp_data = json.load(f)
                except Exception:
                    mcp_data = {"mcpServers": {}}

            mcp_data.setdefault("mcpServers", {})["udk-mcp-editor"] = {
                "command": "python",
                "args": [dst_script],
                "env": {
                    "PYTHONIOENCODING": "utf-8"
                }
            }

            with open(proj_mcp_cfg, "w", encoding="utf-8") as f:
                json.dump(mcp_data, f, ensure_ascii=False, indent=2)

            global_mcp_cfg = os.path.expanduser("~/.gemini/config/mcp_config.json")
            if os.path.exists(global_mcp_cfg):
                try:
                    with open(global_mcp_cfg, "r", encoding="utf-8") as f:
                        g_data = json.load(f)
                    g_data.setdefault("mcpServers", {})["udk-mcp-editor"] = {
                        "command": "python",
                        "args": [mcp_script_src],
                        "env": {"PYTHONIOENCODING": "utf-8"}
                    }
                    with open(global_mcp_cfg, "w", encoding="utf-8") as f:
                        json.dump(g_data, f, ensure_ascii=False, indent=2)
                except Exception:
                    pass

            status_msg = f"⚡ ติดตั้ง UDK MCP Server สำเร็จ! ({'พบ UDK.exe' if udk_found else 'ยังไม่พบ UDK.exe'})"
            self.lbl_deploy_status.setText(status_msg)

            udk_status_desc = f"✅ พบตัวติดตั้ง UDK ที่:\n{udk_exe}" if udk_found else "⚠️ ยังตรวจไม่พบ UDK.exe ในไดรฟ์ C:/D:/E: หรือ Registry (สามารถระบุ UDK_ROOT ใน Environment หรือ hub_config.json ได้)"

            QMessageBox.information(
                self,
                _("ตั้งค่าสำเร็จ"),
                f"✅ ติดตั้ง UDK / UE3 MCP Server สำเร็จ!\n\n"
                f"{udk_status_desc}\n\n"
                f"สคริปต์เซิร์ฟเวอร์: {dst_script}\n"
                f"การตั้งค่าโปรเจกต์: {proj_mcp_cfg}\n\n"
                f"พร้อมใช้งานร่วมกับ Claude Code, Antigravity, และ Cursor ได้ทันที!"
            )
        except Exception as e:
            QMessageBox.critical(self, _("ล้มเหลว"), f"เกิดข้อผิดพลาดในการตั้งค่า UDK MCP: {e}")

    # =========================================================================
    # Prompt Generation & Actions
    # =========================================================================
    def _on_option_toggled(self, checked):
        self._update_protocols_count()
        self._schedule_rebuild_prompt()

    def _collect_options(self):
        options = {}
        if self.current_mode == "agent":
            for k, chk in self.agent_checkboxes.items():
                options[k] = chk.isChecked()
        return options

    def _rebuild_prompt(self):
        if not self.active_project:
            self.txt_prompt.setPlainText("กรุณาเลือกหรือสร้างโปรเจกต์ม็อดก่อน")
            return

        options = self._collect_options()
        app_lang = os.environ.get("THUB_LANG", "th")
        selected_font = {
            "id": self.selected_font_id,
            "variant": self.selected_font_variant
        }

        project = copy.deepcopy(self.active_project)
        prompt_type, mode = self.prompt_type, self.current_mode
        self._prompt_generation += 1
        generation = self._prompt_generation
        def build():
            if prompt_type == "continue":
                return ModAdoptionService.generate_continuation_ai_prompt(project, mode=mode)
            if prompt_type == "step4":
                return PromptEngine.get_step_prompt(project, step_index=4, mode=mode,
                    options=options, app_lang=app_lang, selected_font=selected_font)
            return PromptEngine.generate_master_prompt(project, mode=mode, options=options,
                app_lang=app_lang, selected_font=selected_font, prompt_type=prompt_type)
        self.tasks.submit("prompt", build,
            lambda content: self._prompt_ready(generation, project, prompt_type, content),
            lambda error: self.lbl_auto_save.setText("สร้าง Prompt ไม่สำเร็จ: " + error))

    def _prompt_ready(self, generation, project, prompt_type, content):
        if generation != self._prompt_generation or not self.active_project:
            return
        if project.get("path") != self.active_project.get("path") or prompt_type != self.prompt_type:
            return
        self.txt_prompt.setPlainText(content)
        # Silent Auto-Save to Workspace
        self._silent_auto_save(content)

    def _silent_auto_save(self, content):
        if not self.active_project:
            self.lbl_auto_save.setText("ℹ️ ยังไม่ได้เลือกโปรเจกต์")
            self.lbl_auto_save.setStyleSheet("color: #94a3b8; font-size: 11px;")
            return

        proj_path = self.active_project.get("path", "")
        if not proj_path or not os.path.exists(proj_path):
            self.lbl_auto_save.setText("ℹ️ ยังไม่ได้ระบุ Workspace (คัดลอกไปใช้งานได้)")
            self.lbl_auto_save.setStyleSheet("color: #94a3b8; font-size: 11px;")
            return

        target_file = self.PROMPT_MODES_CONFIG.get(self.prompt_type, {}).get("file", "ai_instructions.md")
        dest_path = os.path.join(proj_path, target_file)

        def write():
            import tempfile
            fd, temporary = tempfile.mkstemp(prefix=".thub-prompt-", dir=proj_path)
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as handle:
                    handle.write(content)
                os.replace(temporary, dest_path)
            finally:
                if os.path.exists(temporary):
                    os.unlink(temporary)
        self.tasks.submit("save-prompt:" + dest_path, write,
            lambda result: self.lbl_auto_save.setText(f"⚡ ซิงค์ลง Workspace แล้ว ({target_file})") if self.active_project and self.active_project.get("path") == proj_path else None,
            lambda error: self.lbl_auto_save.setText("ซิงค์อัตโนมัติไม่สำเร็จ: " + error))

    def _copy_prompt(self):
        content = self.txt_prompt.toPlainText()
        if content:
            QApplication.clipboard().setText(content)
            self.btn_copy.setText("✅ คัดลอกสำเร็จ!")
            self.btn_copy.setStyleSheet("""
                QPushButton {
                    background-color: #10b981;
                    color: #ffffff;
                    border: 1px solid #34d399;
                    border-radius: 6px;
                    padding: 5px 14px;
                    font-size: 11px;
                    font-weight: bold;
                }
            """)
            QTimer.singleShot(1500, self._reset_copy_btn)

    def _reset_copy_btn(self):
        self.btn_copy.setText("📋 คัดลอก Prompt")
        self.btn_copy.setStyleSheet("""
            QPushButton {
                background-color: #8b5cf6;
                color: #ffffff;
                border: 1px solid #a855f7;
                border-radius: 6px;
                padding: 5px 14px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7c3aed;
            }
        """)

    def _save_prompt_file(self):
        if not self.active_project:
            return
        p_path = self.active_project.get("path", "")
        if not p_path or not os.path.exists(p_path):
            QMessageBox.critical(self, "Error", "ไม่พบโฟลเดอร์ Workspace ของโปรเจกต์!")
            return

        target_file = self.PROMPT_MODES_CONFIG.get(self.prompt_type, {}).get("file", "ai_instructions.md")
        dest_file = os.path.join(p_path, target_file)
        try:
            with open(dest_file, "w", encoding="utf-8") as f:
                f.write(self.txt_prompt.toPlainText())
            self.lbl_auto_save.setText(f"⚡ บันทึกไฟล์สำเร็จ ({target_file})")
            self.lbl_auto_save.setStyleSheet("color: #10b981; font-size: 11px; font-weight: bold;")
            QMessageBox.information(self, _("สำเร็จ"), f"บันทึกไฟล์คำสั่งสำเร็จที่:\n{dest_file}")
        except Exception as e:
            QMessageBox.critical(self, _("บันทึกล้มเหลว"), f"ไม่สามารถบันทึกไฟล์ได้: {e}")

    def _copy_cli_command(self):
        target_file = self.PROMPT_MODES_CONFIG.get(self.prompt_type, {}).get("file", "ai_instructions.md")
        cmd = f'claude "อ่าน {target_file} แล้วเริ่มงาน"'
        QApplication.clipboard().setText(cmd)
        if hasattr(self, "btn_copy_cli"):
            orig_text = self.btn_copy_cli.text()
            self.btn_copy_cli.setText("✅ คัดลอกแล้ว!")
            QTimer.singleShot(1500, lambda: self.btn_copy_cli.setText(orig_text))

    def _open_terminal(self):
        proj_path = self.active_project.get("path", "") if self.active_project else ""
        if not proj_path or not os.path.exists(proj_path):
            QMessageBox.warning(self.window(), _("แจ้งเตือน"), _("ไม่พบโฟลเดอร์ Workspace ของโปรเจกต์"))
            return
        try:
            subprocess.Popen(["powershell.exe", "-NoExit", "-Command", f"Set-Location '{proj_path}'"])
        except Exception as e:
            QMessageBox.critical(self.window(), _("ข้อผิดพลาด"), f"ไม่สามารถเปิด Terminal ได้: {e}")

    def _open_tstudio_for_active_project(self):
        ws_path = self.active_project.get("path", "") if self.active_project else ""
        try:
            ToolLauncher.launch_tstudio_for_project(ws_path)
        except Exception as e:
            QMessageBox.critical(self.window(), _("ข้อผิดพลาด"), f"ไม่สามารถเปิด TStudio ได้: {e}")

    # =========================================================================
    # External Controller API & Translations
    # =========================================================================
    def retranslate_ui(self):
        """Update prompt and localized texts when language changes."""
        self.lbl_b_title.setText(_("🤖 AI Modding Copilot & Tri-Deck Studio"))
        self.btn_mode_chat.setText(_("💬 ที่ปรึกษา (Web Chat)"))
        self.btn_mode_agent.setText(_("💻 ปฏิบัติการ (Agent)"))
        self._update_mode_description()
        self.lbl_proj.setText(_("🎮 เลือกโปรเจกต์เป้าหมาย:"))
        if hasattr(self, "btn_adopt_legacy"):
            self.btn_adopt_legacy.setText(_("🔄 สานต่องาน & นำเข้าโฟลเดอร์เดิม..."))
        self.lbl_font_header.setText(_("🔤 สตูดิโอฟอนต์ไทย (PUA 2,208 Glyphs):"))
        if hasattr(self, "lbl_font_style"):
            self.lbl_font_style.setText(_("รูปแบบ / น้ำหนัก:"))
        self.btn_browse_gallery.setText(_("🖼️ คลังฟอนต์"))
        self.btn_deploy_font.setText(_("📥 ติดตั้งลง 03_Font_and_UI"))
        self.lbl_kb.setText(_("📚 คัมภีร์ในคลังความรู้:"))
        self.btn_save.setText(_("💾 บันทึก"))
        self.btn_copy.setText(_("📋 คัดลอก Prompt"))
        self._refresh_plan_card_styles()
        if self.active_project:
            self._update_project_details()
        self._rebuild_prompt()

    def set_prompt_type(self, ptype):
        """Allows switching prompt type externally (e.g. from adoption wizard)."""
        self._set_prompt_type(ptype)

    def set_project(self, project):
        """Allows switching active project externally from Dashboard or Launcher."""
        self.active_project = project
        self.cbo_project.setCurrentText(project.get("name", ""))
        self._update_project_details()

    def update_projects(self, projects):
        """Refreshes project dropdown when projects are created or imported."""
        self._prompt_generation += 1
        self.projects = projects or []
        current_name = self.active_project.get("name", "") if self.active_project else ""
        self._populate_projects_combo()
        if current_name:
            self.cbo_project.setCurrentText(current_name)
        if self.active_project:
            self._update_project_details()
        else:
            self.txt_prompt.clear()
            self.lbl_engine_title.setText("ยังไม่มีโปรเจกต์")
            self.lbl_guides.clear()

    def _quick_load_dimension_art(self, dim_key):
        game_name = self.project.get("name", "")
        ws_path = self.project.get("path", "")
        if not game_name:
            return

        dim_names = {
            "widescreen": _("แนวนอน 16:9"),
            "portrait": _("แนวตั้ง (600x900)"),
            "hero": _("แบนเนอร์ (1920x620)"),
            "logo": _("โลโก้เกมโปร่งใส"),
        }
        lbl = dim_names.get(dim_key, dim_key)
        self.lbl_art_status.setText(_("⏳ กำลังโหลด {lbl}...").format(lbl=lbl))
        self.lbl_art_status.setStyleSheet("color: #38bdf8; font-size: 10px;")

        def work():
            from core.art_harvester_service import ArtHarvesterService
            return ArtHarvesterService.get_or_harvest_dimension(game_name, ws_path, dim_key)

        def on_done(res):
            if res and res.get("success") and res.get("path"):
                fp = res["path"]
                fn = res.get("filename", "")
                w = res.get("width", 0)
                h = res.get("height", 0)
                if dim_key == "logo":
                    self.lbl_art_status.setText(_("✨ โลโก้พร้อมใช้งาน: {fn} ({w}×{h})").format(fn=fn, w=w, h=h))
                    self.lbl_art_status.setStyleSheet("color: #c084fc; font-size: 10px; font-weight: bold;")
                    try:
                        import os
                        os.startfile(os.path.normpath(fp))
                    except Exception:
                        pass
                else:
                    self.lbl_art_status.setText(_("✅ โหลด {lbl} สำเร็จ: {fn}").format(lbl=lbl, fn=fn))
                    self.lbl_art_status.setStyleSheet("color: #10b981; font-size: 10px;")
            else:
                self.lbl_art_status.setText(_("⚠️ ไม่พบภาพขนาด {lbl}").format(lbl=lbl))
                self.lbl_art_status.setStyleSheet("color: #fb7185; font-size: 10px;")

        self.tasks.submit(f"quick-dim-{dim_key}", work, on_done, lambda err: self.lbl_art_status.setText(f"❌ {err}"))

