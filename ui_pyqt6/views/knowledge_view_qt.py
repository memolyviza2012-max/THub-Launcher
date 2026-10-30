from core.qt_tasks import BackgroundTasks
import os
import subprocess
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTextEdit, QFrame, QScrollArea, QApplication
)
from PyQt6.QtCore import Qt
from core.knowledge_service import KnowledgeService
from core.engine_scanner import EngineScanner
from i18n_helper import _

class KnowledgeViewQt(QWidget):
    """
    Hierarchical Modding-Knowledge Base View in PyQt6.
    Allows browsing by Game Engine -> Game Bibles,
    with instant search, rich Markdown rendering, and Explorer actions.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tasks = BackgroundTasks(self)
        self.kb_service = KnowledgeService.get_instance()
        self.current_engine_folder = None  # None = Root Engine Catalog, or string folder name
        self.active_category_filter = "All"  # "All", "Engines", "Techniques", "Tools"
        self.current_guide = None
        self.render_mode_markdown = True
        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 10, 16, 16)
        main_layout.setSpacing(12)

        # Header Banner
        banner = QFrame()
        banner.setProperty("class", "ContentBanner")
        b_layout = QVBoxLayout(banner)
        b_layout.setContentsMargins(16, 12, 16, 12)
        b_layout.setSpacing(3)

        self.lbl_b_title = QLabel(_("📚 Modding Knowledge Base — คลังความรู้และคัมภีร์โมเกม"))
        self.lbl_b_title.setProperty("class", "BannerTitle")
        b_layout.addWidget(self.lbl_b_title)

        self.lbl_b_sub = QLabel(_("จัดระเบียบตามเอนจิ้นเกม (คลิกที่เอนจิ้นเพื่อดูรายชื่อเกมและเปิดอ่านคัมภีร์เจาะลึก)"))
        self.lbl_b_sub.setProperty("class", "Muted")
        b_layout.addWidget(self.lbl_b_sub)
        main_layout.addWidget(banner)

        # Split Layout
        split = QHBoxLayout()
        split.setSpacing(12)

        # ─────────────────────────────────────────────────────────────
        # Left Panel: Navigator (Engines / Games)
        # ─────────────────────────────────────────────────────────────
        self.left_card = QFrame()
        self.left_card.setFixedWidth(360)
        self.left_card.setProperty("class", "PanelCard")
        self.left_layout = QVBoxLayout(self.left_card)
        self.left_layout.setContentsMargins(12, 12, 12, 12)
        self.left_layout.setSpacing(8)

        # Breadcrumb / Back button bar
        self.nav_header = QWidget()
        self.nav_header_layout = QHBoxLayout(self.nav_header)
        self.nav_header_layout.setContentsMargins(0, 0, 0, 0)
        self.nav_header_layout.setSpacing(6)

        self.btn_back_engine = QPushButton(_("⬅️ เอนจิ้นทั้งหมด"))
        self.btn_back_engine.setProperty("class", "BtnSecondary")
        self.btn_back_engine.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_back_engine.clicked.connect(self._go_to_engine_catalog)
        self.btn_back_engine.setVisible(False)
        self.nav_header_layout.addWidget(self.btn_back_engine)

        self.lbl_nav_title = QLabel(_("⚙️ เลือกเอนจิ้นเกม (Engines)"))
        self.lbl_nav_title.setProperty("class", "CardTitle")
        self.nav_header_layout.addWidget(self.lbl_nav_title, stretch=1)
        self.left_layout.addWidget(self.nav_header)

        # Search box
        self.search_box = QLineEdit()
        self.search_box.setProperty("class", "SearchBox")
        self.search_box.setPlaceholderText(_("🔍 ค้นหาเอนจิ้น, เกม หรือคัมภีร์..."))
        self.search_box.textChanged.connect(self._on_search)
        self.left_layout.addWidget(self.search_box)

        # Scroll Area for List Items
        self.list_scroll = QScrollArea()
        self.list_scroll.setWidgetResizable(True)
        self.list_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.list_container = QWidget()
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(4)
        self.list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.list_scroll.setWidget(self.list_container)
        self.left_layout.addWidget(self.list_scroll)

        split.addWidget(self.left_card)

        # ─────────────────────────────────────────────────────────────
        # Right Panel: Document Reader & Actions
        # ─────────────────────────────────────────────────────────────
        right_card = QFrame()
        right_card.setProperty("class", "PanelCard")
        right_layout = QVBoxLayout(right_card)
        right_layout.setContentsMargins(14, 12, 14, 14)
        right_layout.setSpacing(8)

        # Reader Toolbar Header
        reader_bar = QHBoxLayout()
        reader_bar.setSpacing(8)

        self.lbl_guide_title = QLabel(_("เลือกเอนจิ้นและเกมจากรายการด้านซ้ายเพื่อเปิดอ่านคัมภีร์"))
        self.lbl_guide_title.setProperty("class", "CardTitle")
        reader_bar.addWidget(self.lbl_guide_title, stretch=1)

        # Action button: Open Folder
        self.btn_open_folder = QPushButton(_("📂 เปิดโฟลเดอร์"))
        self.btn_open_folder.setProperty("class", "BtnSecondary")
        self.btn_open_folder.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_open_folder.clicked.connect(self._open_in_explorer)
        self.btn_open_folder.setEnabled(False)
        reader_bar.addWidget(self.btn_open_folder)

        # Action button: Copy Path
        self.btn_copy_path = QPushButton(_("📋 คัดลอก Path"))
        self.btn_copy_path.setProperty("class", "BtnSecondary")
        self.btn_copy_path.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_copy_path.clicked.connect(self._copy_guide_path)
        self.btn_copy_path.setEnabled(False)
        reader_bar.addWidget(self.btn_copy_path)

        # Action button: Toggle Render Mode
        self.btn_toggle_mode = QPushButton("📖 Render")
        self.btn_toggle_mode.setProperty("class", "BtnSecondary")
        self.btn_toggle_mode.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle_mode.clicked.connect(self._toggle_render_mode)
        reader_bar.addWidget(self.btn_toggle_mode)

        right_layout.addLayout(reader_bar)

        # Breadcrumb info label
        self.lbl_path_info = QLabel("Modding-Knowledge")
        self.lbl_path_info.setProperty("class", "SubText")
        right_layout.addWidget(self.lbl_path_info)

        # Markdown Text Reader
        self.txt_reader = QTextEdit()
        self.txt_reader.setReadOnly(True)
        self.txt_reader.setProperty("class", "CodeEditor")
        self.txt_reader.setStyleSheet("""
            QTextEdit {
                padding: 14px;
                font-family: 'Segoe UI', 'Leelawadee UI', sans-serif;
                font-size: 12px;
                line-height: 1.6;
            }
        """)
        right_layout.addWidget(self.txt_reader)

        split.addWidget(right_card, stretch=1)
        main_layout.addLayout(split)

        # Initial render: Engine Catalog
        self._render_engine_catalog()

    def retranslate_ui(self):
        """Live retranslate for Knowledge View."""
        self.lbl_b_title.setText(_("📚 Modding Knowledge Base — คลังความรู้และคัมภีร์โมเกม"))
        self.lbl_b_sub.setText(_("จัดระเบียบตามเอนจิ้นเกม (คลิกที่เอนจิ้นเพื่อดูรายชื่อเกมและเปิดอ่านคัมภีร์เจาะลึก)"))
        self.btn_back_engine.setText(_("⬅️ เอนจิ้นทั้งหมด"))
        self.btn_open_folder.setText(_("📂 เปิดโฟลเดอร์"))
        self.btn_copy_path.setText(_("📋 คัดลอก Path"))
        self.btn_toggle_mode.setText("📖 Render" if not self.render_mode_markdown else "📝 Raw Markdown")
        self.search_box.setPlaceholderText(_("🔍 ค้นหาเอนจิ้น, เกม หรือคัมภีร์..."))
        if not self.current_engine_folder:
            self.lbl_nav_title.setText(_("⚙️ เลือกเอนจิ้นเกม (Engines)"))
            self._render_engine_catalog()
        else:
            self._render_games_for_engine(self.current_engine_folder)

    def _clear_list(self):
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    # ─────────────────────────────────────────────────────────────
    # Navigation: Engine Catalog (Level 1)
    # ─────────────────────────────────────────────────────────────
    def _go_to_engine_catalog(self):
        self.current_engine_folder = None
        self.btn_back_engine.setVisible(False)
        self.lbl_nav_title.setText("⚙️ เลือกเอนจิ้นเกม (Engines)")
        self.search_box.clear()
        self._render_engine_catalog()

    def _render_engine_catalog(self):
        self._clear_list()
        engines = self.kb_service.get_engines()

        if not engines:
            lbl_none = QLabel("ไม่พบข้อมูลเอนจิ้นใน Modding-Knowledge")
            lbl_none.setStyleSheet("color: #64748b; font-size: 11px; padding: 10px;")
            self.list_layout.addWidget(lbl_none)
            return

        # Engines Section Title
        lbl_eng_sec = QLabel(f"🎮 เกมแยกตามเอนจิ้น ({len(engines)} เอนจิ้น)")
        lbl_eng_sec.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: bold; padding: 4px 6px;")
        self.list_layout.addWidget(lbl_eng_sec)

        for eng in engines:
            btn = QPushButton()
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
            # Badge color
            color = self._get_engine_color(eng["name"])
            games_cnt = eng["total_games"]
            guides_cnt = eng["total_guides"]
            cnt_text = f"{games_cnt} เกม" if games_cnt > 0 else f"{guides_cnt} คู่มือ"
            if games_cnt > 0 and guides_cnt > 0:
                cnt_text = f"{games_cnt} เกม ({guides_cnt} คู่มือ)"

            btn.setText(f"⚙️ {eng['name']}  •  {cnt_text}")
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #171c2b;
                    color: #f1f5f9;
                    text-align: left;
                    border: 1px solid #232a3d;
                    border-left: 4px solid {color};
                    border-radius: 6px;
                    padding: 8px 10px;
                    font-size: 11px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: #1e2538;
                    border-color: {color};
                    color: #ffffff;
                }}
            """)
            btn.clicked.connect(lambda _, e=eng["folder"]: self._select_engine(e))
            self.list_layout.addWidget(btn)

        # Other Categories Section
        cats = self.kb_service.get_categories()
        if cats:
            lbl_cat_sec = QLabel("🛠️ เทคนิคและเครื่องมือสากล (General Guides)")
            lbl_cat_sec.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: bold; padding: 10px 6px 4px 6px;")
            self.list_layout.addWidget(lbl_cat_sec)

            for cat_name, items in cats.items():
                btn_cat = QPushButton(f"📂 {cat_name}  •  {len(items)} ฉบับ")
                btn_cat.setCursor(Qt.CursorShape.PointingHandCursor)
                btn_cat.setStyleSheet("""
                    QPushButton {
                        background-color: #131722;
                        color: #cbd5e1;
                        text-align: left;
                        border: 1px solid #1f2536;
                        border-left: 4px solid #a855f7;
                        border-radius: 6px;
                        padding: 7px 10px;
                        font-size: 11px;
                    }
                    QPushButton:hover {
                        background-color: #1a2030;
                        border-color: #c084fc;
                        color: #ffffff;
                    }
                """)
                btn_cat.clicked.connect(lambda _, c=cat_name: self._select_category(c))
                self.list_layout.addWidget(btn_cat)

    # ─────────────────────────────────────────────────────────────
    # Navigation: Games in Engine (Level 2)
    # ─────────────────────────────────────────────────────────────
    def _select_engine(self, engine_folder):
        self.current_engine_folder = engine_folder
        self.btn_back_engine.setVisible(True)
        eng_data = self.kb_service.get_engine(engine_folder)
        eng_name = eng_data["name"] if eng_data else engine_folder
        self.lbl_nav_title.setText(f"⚙️ {eng_name}")
        self.search_box.clear()
        self._render_games_for_engine(engine_folder)

    def _render_games_for_engine(self, engine_folder, filter_text=""):
        self._clear_list()
        eng_data = self.kb_service.get_engine(engine_folder)
        if not eng_data:
            return

        games = eng_data.get("games", [])
        guides = eng_data.get("engine_guides", [])

        # Filter by search text if any
        if filter_text:
            ft = filter_text.lower().strip()
            games = [g for g in games if ft in g["name"].lower() or any(ft in b["filename"].lower() for b in g["bibles"])]
            guides = [g for g in guides if ft in g["title"].lower() or ft in g["filename"].lower()]

        # 1. Engine Guides section (e.g. Unity_Engine.md)
        if guides:
            lbl_guides = QLabel(f"📘 คู่มือประจำเอนจิ้น ({len(guides)})")
            lbl_guides.setStyleSheet("color: #38bdf8; font-size: 11px; font-weight: bold; padding: 4px 6px;")
            self.list_layout.addWidget(lbl_guides)

            for g in guides:
                btn = QPushButton(f"📖 {g['title']}")
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #171c2b;
                        color: #7dd3fc;
                        text-align: left;
                        border: 1px solid #1e2638;
                        border-radius: 5px;
                        padding: 6px 8px;
                        font-size: 11px;
                    }
                    QPushButton:hover {
                        background-color: #1e2840;
                        border-color: #38bdf8;
                    }
                """)
                btn.clicked.connect(lambda _, item=g: self._display_guide(item))
                self.list_layout.addWidget(btn)

        # 2. Games List section
        lbl_games = QLabel(f"🎮 รายชื่อเกมและคัมภีร์ ({len(games)} เกม)")
        lbl_games.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: bold; padding: 8px 6px 4px 6px;")
        self.list_layout.addWidget(lbl_games)

        if not games:
            lbl_none = QLabel("ไม่พบคัมภีร์ที่ตรงกับคำค้นหา")
            lbl_none.setStyleSheet("color: #64748b; font-size: 11px; padding: 10px;")
            self.list_layout.addWidget(lbl_none)
            return

        for g in games:
            for b in g["bibles"]:
                btn = QPushButton(f"📄 {g['name']}")
                btn.setToolTip(b["filename"])
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                
                # Active highlight
                is_active = (self.current_guide and self.current_guide.get("path") == b["path"])
                bg = "#1e293b" if is_active else "#121622"
                border = "#38bdf8" if is_active else "#1e2436"
                txt_color = "#38bdf8" if is_active else "#f1f5f9"

                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {bg};
                        color: {txt_color};
                        text-align: left;
                        border: 1px solid {border};
                        border-radius: 5px;
                        padding: 6px 8px;
                        font-size: 11px;
                    }}
                    QPushButton:hover {{
                        background-color: #1c2438;
                        border-color: #38bdf8;
                        color: #ffffff;
                    }}
                """)
                btn.clicked.connect(lambda _, item=b: self._display_guide(item))
                self.list_layout.addWidget(btn)

    # ─────────────────────────────────────────────────────────────
    # Navigation: Category (Techniques / Tools)
    # ─────────────────────────────────────────────────────────────
    def _select_category(self, cat_name):
        self.current_engine_folder = f"CAT_{cat_name}"
        self.btn_back_engine.setVisible(True)
        self.lbl_nav_title.setText(f"🛠️ {cat_name}")
        self.search_box.clear()
        
        self._clear_list()
        cats = self.kb_service.get_categories()
        items = cats.get(cat_name, [])

        lbl_sec = QLabel(f"📂 {cat_name} ({len(items)} ฉบับ)")
        lbl_sec.setStyleSheet("color: #c084fc; font-size: 11px; font-weight: bold; padding: 4px 6px;")
        self.list_layout.addWidget(lbl_sec)

        for it in items:
            btn = QPushButton(f"📄 {it['title']}")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #121622;
                    color: #f1f5f9;
                    text-align: left;
                    border: 1px solid #1e2436;
                    border-radius: 5px;
                    padding: 6px 8px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #1c2438;
                    border-color: #c084fc;
                    color: #ffffff;
                }
            """)
            btn.clicked.connect(lambda _, item=it: self._display_guide(item))
            self.list_layout.addWidget(btn)

    # ─────────────────────────────────────────────────────────────
    # Search Handling
    # ─────────────────────────────────────────────────────────────
    def _on_search(self, text):
        query = text.strip()
        if not query:
            if self.current_engine_folder and not self.current_engine_folder.startswith("CAT_"):
                self._render_games_for_engine(self.current_engine_folder)
            elif self.current_engine_folder and self.current_engine_folder.startswith("CAT_"):
                self._select_category(self.current_engine_folder[4:])
            else:
                self._render_engine_catalog()
            return

        # If user is in an engine, filter within engine
        if self.current_engine_folder and not self.current_engine_folder.startswith("CAT_"):
            self._render_games_for_engine(self.current_engine_folder, filter_text=query)
            return

        # Global search mode
        self._clear_list()
        results = self.kb_service.search(query)
        lbl_res = QLabel(f"🔍 ผลการค้นหา ({len(results)} รายการ)")
        lbl_res.setStyleSheet("color: #38bdf8; font-size: 11px; font-weight: bold; padding: 4px 6px;")
        self.list_layout.addWidget(lbl_res)

        if not results:
            lbl_none = QLabel("ไม่พบคู่มือหรือคัมภีร์ที่ตรงกัน")
            lbl_none.setStyleSheet("color: #64748b; font-size: 11px; padding: 10px;")
            self.list_layout.addWidget(lbl_none)
            return

        for r in results[:40]:
            eng_badge = f"[{r.get('engine')}] " if r.get('engine') else ""
            btn = QPushButton(f"📄 {eng_badge}{r['title']}")
            btn.setToolTip(r["rel_path"])
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #121622;
                    color: #f1f5f9;
                    text-align: left;
                    border: 1px solid #1e2436;
                    border-radius: 5px;
                    padding: 6px 8px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #1c2438;
                    border-color: #38bdf8;
                    color: #ffffff;
                }
            """)
            btn.clicked.connect(lambda _, item=r: self._display_guide(item))
            self.list_layout.addWidget(btn)

    # ─────────────────────────────────────────────────────────────
    # Reader & Document Display
    # ─────────────────────────────────────────────────────────────
    def _display_guide(self, guide):
        self.current_guide = guide
        title = guide.get("game") or guide.get("title") or guide.get("filename")
        engine = guide.get("engine") or guide.get("category") or "General"
        
        self.lbl_guide_title.setText(f"📖 {title}")
        self.lbl_path_info.setText(f"📍 {guide.get('rel_path', '')}")
        self.btn_open_folder.setEnabled(True)
        self.btn_copy_path.setEnabled(True)

        path = guide["path"]
        self.tasks.submit("read-guide", lambda: self.kb_service.read_markdown(path),
                          lambda content: self._guide_ready(path, content))

    def _guide_ready(self, path, content):
        if self.current_guide and self.current_guide.get("path") == path:
            self._reader_content = content
            self._set_reader_content(content)

    def _set_reader_content(self, content):
        if self.render_mode_markdown:
            self.txt_reader.setMarkdown(content)
        else:
            self.txt_reader.setPlainText(content)

    def _toggle_render_mode(self):
        self.render_mode_markdown = not self.render_mode_markdown
        self.btn_toggle_mode.setText("📖 Render" if self.render_mode_markdown else "📝 Raw Text")
        if self.current_guide:
            content = getattr(self, "_reader_content", "กำลังโหลด...")
            self._set_reader_content(content)

    def _open_in_explorer(self):
        if not self.current_guide:
            return
        path = self.current_guide.get("path")
        if path and os.path.exists(path):
            folder = os.path.dirname(path)
            try:
                os.startfile(folder)
            except Exception:
                subprocess.Popen(f'explorer /select,"{path}"')

    def _copy_guide_path(self):
        if not self.current_guide:
            return
        path = self.current_guide.get("path", "")
        if path:
            cb = QApplication.clipboard()
            if cb:
                cb.setText(path)
                self.btn_copy_path.setText("✅ คัดลอกแล้ว")
                from PyQt6.QtCore import QTimer
                QTimer.singleShot(1500, lambda: self.btn_copy_path.setText("📋 คัดลอก Path"))

    def _get_engine_color(self, engine_name):
        return EngineScanner.ENGINE_COLORS.get(engine_name, "#38bdf8")

