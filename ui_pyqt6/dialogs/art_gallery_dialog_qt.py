import os
import subprocess
import weakref
from collections import OrderedDict
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QWidget, QFrame, QGridLayout, QSizePolicy, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap, QImage, QImageReader, QColor

from core.art_harvester_service import ArtHarvesterService
from core.qt_tasks import BackgroundTasks, TaskDialogMixin
from core.config_manager import ConfigManager
from i18n_helper import _


class ArtGalleryDialogQt(TaskDialogMixin, QDialog):
    """
    Official Art & Background Gallery Dialog.
    Previews and manages high-res official art harvested from Sony PlayStation Store (PS5 4K)
    and Steam Official CDN. Allows 1-click setting as project cover.
    """

    cover_selected = pyqtSignal(str)
    _thumbnail_cache = OrderedDict()
    _thumbnail_cache_bytes = 0
    MAX_THUMBNAILS = 64
    MAX_THUMBNAIL_BYTES = 16 * 1024 * 1024

    def __init__(self, project=None, game_name="", workspace_path="", parent=None):
        super().__init__(parent)
        self.tasks = BackgroundTasks(self)
        self.project = dict(project) if project else {}
        self.game_name = game_name or self.project.get("name", "")
        self.workspace_path = workspace_path or self.project.get("path", "")
        self.all_artworks = []
        self._filter_mode = "all"
        self._filter_buttons = {}
        self._download_buttons = []
        self._thumbnail_waiters = {}
        self._harvest_in_progress = False

        self.setWindowTitle(_("🎮 คลังภาพพื้นหลัง & อาร์ตเวิร์กอย่างเป็นทางการ — {name}").format(name=self.game_name or "Official Art"))
        self.resize(1020, 740)
        self.setMinimumSize(880, 600)

        self._build_ui()
        self._load_artworks(auto_harvest_if_empty=True)


    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 16, 20, 18)
        main_layout.setSpacing(12)

        # 1. Header Banner
        header = QFrame()
        header.setProperty("class", "ContentBanner")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(16, 12, 16, 12)
        h_layout.setSpacing(12)

        h_text_col = QVBoxLayout()
        h_text_col.setSpacing(3)

        lbl_title = QLabel(_("🎮 คลังภาพพื้นหลัง & อาร์ตเวิร์กอย่างเป็นทางการ (Official 4K Art Gallery)"))
        lbl_title.setStyleSheet("color: #c084fc; font-size: 16px; font-weight: bold;")
        h_text_col.addWidget(lbl_title)

        self.lbl_subtitle = QLabel(
            _("ระบบ AI ค้นหาภาพความละเอียดสูง 4K UHD จาก Sony PlayStation Store และ Steam CDN อัตโนมัติ — เกม: {name}").format(name=self.game_name)
        )
        self.lbl_subtitle.setProperty("class", "Muted")
        self.lbl_subtitle.setStyleSheet("font-size: 11px;")
        h_text_col.addWidget(self.lbl_subtitle)

        h_layout.addLayout(h_text_col, stretch=1)

        # Header Actions
        self.btn_harvest = QPushButton(_("🔄 ดึงภาพจาก Sony && Steam"))
        self.btn_harvest.setProperty("class", "BtnAI")

        self.btn_harvest.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_harvest.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7c3aed, stop:1 #2563eb);
                color: #ffffff;
                font-weight: bold;
                padding: 7px 14px;
                border-radius: 6px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #9333ea, stop:1 #3b82f6);
            }
        """)
        self.btn_harvest.setToolTip(_("สแกนและดาวน์โหลดภาพ 4K จาก Sony PlayStation Store และ Steam Official CDN เข้ามาใหม่"))
        self.btn_harvest.clicked.connect(self._start_harvest)
        h_layout.addWidget(self.btn_harvest)

        self.btn_open_folder = QPushButton(_("📂 เปิดโฟลเดอร์ภาพ"))
        self.btn_open_folder.setProperty("class", "BtnSecondary")
        self.btn_open_folder.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_open_folder.setStyleSheet("padding: 7px 12px; font-size: 11px;")
        self.btn_open_folder.clicked.connect(self._open_art_folder)
        h_layout.addWidget(self.btn_open_folder)

        main_layout.addWidget(header)

        # 1.5 Quick Dimension Download Bar
        quick_dim_box = QFrame()
        quick_dim_box.setProperty("class", "InnerCard")
        qdim_layout = QHBoxLayout(quick_dim_box)
        qdim_layout.setContentsMargins(12, 6, 12, 6)
        qdim_layout.setSpacing(6)

        lbl_quick = QLabel(_("⚡ โหลดขนาดด่วน:"))
        lbl_quick.setStyleSheet("color: #c084fc; font-weight: bold; font-size: 11px;")
        qdim_layout.addWidget(lbl_quick)

        for dim_k, dim_lbl, dim_tip in [
            ("widescreen", _("📺 แนวนอน 16:9"), _("โหลดภาพปกแนวนอน 16:9 (Sony 4K / Steam Capsule)")),
            ("portrait", _("📱 แนวตั้ง (600x900)"), _("โหลดภาพโปสเตอร์แนวตั้ง 2:3 สำหรับ Steam Library Grid")),
            ("hero", _("🚩 แบนเนอร์ (1920x620)"), _("โหลดภาพแบนเนอร์กว้าง Steam Library Hero")),
            ("header", _("🏷️ ส่วนหัว (460x215)"), _("โหลดภาพปกส่วนหัวร้านค้า Steam Store Header")),
            ("logo", _("✨ โลโก้เกม (Logo PNG)"), _("ดึงไฟล์โลโก้เกมแบบโปร่งใส (Transparent PNG) แท้ทันที")),
        ]:
            b = QPushButton(dim_lbl)
            b.setProperty("class", "BtnAI" if dim_k == "logo" else "BtnSecondary")
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setToolTip(dim_tip)
            if dim_k == "logo":
                b.setStyleSheet("font-size: 10.5px; padding: 4px 10px; font-weight: bold; background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7c3aed, stop:1 #d97706); color: #fff; border-radius: 5px;")
            else:
                b.setStyleSheet("font-size: 10px; padding: 4px 8px;")
            b.clicked.connect(lambda chk, k=dim_k: self._quick_download_dimension(k))
            self._download_buttons.append(b)
            qdim_layout.addWidget(b)

        qdim_layout.addStretch()
        main_layout.addWidget(quick_dim_box)

        # 2. Filter Bar
        filter_bar = QHBoxLayout()
        filter_bar.setSpacing(8)

        lbl_filter = QLabel(_("🔍 กรองภาพ:"))
        lbl_filter.setProperty("class", "CardTitle")
        filter_bar.addWidget(lbl_filter)

        filters = [
            ("all", _("🌟 ทั้งหมด")),
            ("widescreen", _("📺 16:9 แนวนอน")),
            ("portrait", _("📱 แนวตั้ง (600x900)")),
            ("hero", _("🚩 แบนเนอร์ (1920x620)")),
            ("header", _("🏷️ ส่วนหัว (460x215)")),
            ("logo", _("✨ โลโก้เกม (Logo PNG)")),
            ("sony", _("🎮 Sony PS Store")),
            ("steam", _("🌐 Steam Store CDN"))
        ]

        for key, label in filters:
            btn = QPushButton(label)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setProperty("filter_key", key)
            btn.clicked.connect(lambda checked, k=key: self._set_filter(k))
            self._filter_buttons[key] = btn
            filter_bar.addWidget(btn)

        filter_bar.addStretch()

        self.lbl_count = QLabel("")
        self.lbl_count.setStyleSheet("color: #94a3b8; font-size: 11px;")
        filter_bar.addWidget(self.lbl_count)

        main_layout.addLayout(filter_bar)
        self._update_filter_styles()

        # 3. Scroll Area for Artwork Cards Grid
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setContentsMargins(0, 4, 8, 8)
        self.grid_layout.setSpacing(14)

        self.scroll.setWidget(self.grid_container)
        main_layout.addWidget(self.scroll, stretch=1)

        # 4. Bottom Footer
        footer = QHBoxLayout()
        footer.setSpacing(10)

        lbl_tip = QLabel(_("💡 เคล็ดลับ: ภาพที่มีเครื่องหมาย 4K UHD จาก Sony PlayStation มักเป็นภาพ Textless Key Art ที่ไม่มีตัวหนังสือโลโก้ เหมาะเป็นภาพปกโปรเจกต์ที่สุด"))
        lbl_tip.setStyleSheet("color: #64748b; font-size: 11px;")
        lbl_tip.setWordWrap(True)
        footer.addWidget(lbl_tip, stretch=1)

        btn_close = QPushButton(_("ปิดหน้าต่าง"))
        btn_close.setProperty("class", "BtnSecondary")
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("padding: 7px 18px; font-size: 11px;")
        btn_close.clicked.connect(self.accept)
        footer.addWidget(btn_close)

        main_layout.addLayout(footer)

    def _set_filter(self, key):
        self._filter_mode = key
        self._update_filter_styles()
        self._render_cards()

    def _update_filter_styles(self):
        for key, btn in self._filter_buttons.items():
            if key == self._filter_mode:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #8b5cf6;
                        color: #ffffff;
                        font-weight: bold;
                        border: 1px solid #a855f7;
                        border-radius: 6px;
                        padding: 5px 12px;
                        font-size: 11px;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(30, 41, 59, 0.7);
                        color: #94a3b8;
                        border: 1px solid rgba(255, 255, 255, 0.08);
                        border-radius: 6px;
                        padding: 5px 12px;
                        font-size: 11px;
                    }
                    QPushButton:hover {
                        background-color: rgba(51, 65, 85, 0.9);
                        color: #e2e8f0;
                    }
                """)

    def _load_artworks(self, auto_harvest_if_empty=False):
        workspace, game_name = self.workspace_path, self.game_name
        self.lbl_count.setText(_("กำลังโหลดภาพ..."))
        def scan():
            artworks = ArtHarvesterService.get_existing_artworks(workspace_path=workspace, game_name=game_name)
            for artwork in artworks:
                artwork["_thumbnail_key"] = self._thumbnail_key(artwork.get("path", ""))
            return artworks
        self.tasks.submit("load-artworks", scan,
            lambda artworks: self._artworks_loaded(artworks, auto_harvest_if_empty),
            lambda error: self.lbl_subtitle.setText(_("โหลดคลังภาพไม่สำเร็จ: {err}").format(err=error)))

    def _artworks_loaded(self, artworks, auto_harvest_if_empty):
        self.all_artworks = artworks
        if not self.all_artworks and auto_harvest_if_empty and ConfigManager().get("steam_auto_capsule", True):
            # If no local artworks exist, trigger auto-harvest in background
            self._start_harvest(automatic=True)
        else:
            self._render_cards()

    def _set_download_busy(self, busy):
        self._harvest_in_progress = busy
        self.btn_harvest.setEnabled(not busy)
        for button in self._download_buttons:
            button.setEnabled(not busy)

    def _start_harvest(self, checked=False, automatic=False):
        if self._harvest_in_progress or "harvest-artworks" in self.tasks.jobs:
            return
        if automatic and not ConfigManager().get("steam_auto_capsule", True):
            return
        self._set_download_busy(True)
        self.btn_harvest.setEnabled(False)
        self.btn_harvest.setText(_("⏳ กำลังดึงภาพจาก Sony && Steam..."))

        game_name, workspace = self.game_name, self.workspace_path
        def do_harvest():
            return ArtHarvesterService.harvest_all_artworks(
                game_name=game_name,
                workspace_path=workspace,
                automatic=automatic
            )

        def on_done(res):
            self._set_download_busy(False)
            self.btn_harvest.setEnabled(True)
            self.btn_harvest.setText(_("🔄 ดึงภาพจาก Sony && Steam"))
            if res and isinstance(res, dict):
                sony_c = res.get("sony_count", 0)
                steam_c = res.get("steam_count", 0)
                total = res.get("total_images", 0)
                if total > 0:
                    self.lbl_subtitle.setText(
                        _("ดึงภาพสำเร็จ! พบภาพทั้งหมด {total} ภาพ (Sony PS Store: {sony}, Steam: {steam})").format(
                            total=total, sony=sony_c, steam=steam_c
                        )
                    )
            self._load_artworks(auto_harvest_if_empty=False)

        self.tasks.submit(
            "harvest-artworks",
            do_harvest,
            on_done,
            self._on_harvest_error
        )

    def _on_harvest_error(self, err):
        self._set_download_busy(False)
        self.btn_harvest.setEnabled(True)
        self.btn_harvest.setText(_("🔄 ดึงภาพจาก Sony && Steam"))


        QMessageBox.warning(self, _("แจ้งเตือน"), _("เกิดข้อผิดพลาดในการดึงภาพ: {err}").format(err=str(err)))

    def _open_art_folder(self):
        if self.workspace_path:
            target = os.path.join(self.workspace_path, "07_Image_Resources", "Official_Art")
            if not os.path.exists(target):
                os.makedirs(target, exist_ok=True)
            try:
                os.startfile(target)
                return
            except Exception:
                pass
        QMessageBox.information(self, _("แจ้งเตือน"), _("ไม่พบโฟลเดอร์ภาพสำหรับโปรเจกต์นี้"))

    def _render_cards(self):
        # Clear existing cards in layout
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        # Filter items
        filtered = []
        for a in self.all_artworks:
            w, h = a.get("width", 0), a.get("height", 0)
            src = a.get("source", "").lower()
            role = str(a.get("role", "")).upper()
            filename = a.get("filename", "").lower()

            if self._filter_mode == "widescreen":
                ratio = w / max(1, h)
                if not (1.55 <= ratio <= 1.85) or "logo" in role.lower():
                    continue
            elif self._filter_mode == "portrait":
                if not (role in ("PORTRAIT", "POSTER") or (h > w * 1.15 and "logo" not in role.lower())):
                    continue
            elif self._filter_mode == "hero":
                if not (role in ("HERO", "STEAM_HERO", "SIXTEEN_BY_NINE_BANNER") or (w / max(1, h) >= 2.5 and "logo" not in role.lower())):
                    continue
            elif self._filter_mode == "header":
                if not (role == "HEADER" or "header" in filename):
                    continue
            elif self._filter_mode == "logo":
                if not (role == "LOGO" or "logo" in filename):
                    continue
            elif self._filter_mode == "sony":
                if "sony" not in src:
                    continue
            elif self._filter_mode == "steam":
                if "steam" not in src:
                    continue
            filtered.append(a)

        self.lbl_count.setText(_("แสดง {count} / {total} ภาพ").format(count=len(filtered), total=len(self.all_artworks)))

        if not filtered:
            empty_box = QFrame()
            empty_layout = QVBoxLayout(empty_box)
            empty_layout.setContentsMargins(40, 60, 40, 60)
            empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            lbl_empty = QLabel(_("🔍 ยังไม่มีภาพในหมวดนี้"))
            lbl_empty.setStyleSheet("color: #94a3b8; font-size: 15px; font-weight: bold;")
            empty_layout.addWidget(lbl_empty, alignment=Qt.AlignmentFlag.AlignCenter)

            btn_harvest_now = QPushButton(_("🚀 สั่งให้ AI ดึงภาพจาก Sony && Steam ทันที"))

            btn_harvest_now.setProperty("class", "BtnAI")
            btn_harvest_now.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_harvest_now.setStyleSheet("padding: 8px 16px; font-size: 12px; margin-top: 10px;")
            btn_harvest_now.clicked.connect(self._start_harvest)
            empty_layout.addWidget(btn_harvest_now, alignment=Qt.AlignmentFlag.AlignCenter)

            self.grid_layout.addWidget(empty_box, 0, 0, 1, 3)
            return

        # Render 3 columns grid
        COLUMNS = 3
        for idx, art in enumerate(filtered):
            card = self._create_artwork_card(art)
            row = idx // COLUMNS
            col = idx % COLUMNS
            self.grid_layout.addWidget(card, row, col)

    @staticmethod
    def _thumbnail_key(path):
        try:
            info = os.stat(path)
            return (os.path.normcase(os.path.abspath(path)), info.st_mtime_ns, info.st_size, 280, 158)
        except OSError:
            return (path, None, None, 280, 158)

    @staticmethod
    def _decode_thumbnail(path):
        """Read/downsample into QImage on a worker; create QPixmap only on Qt's UI thread."""
        reader = QImageReader(path)
        dimensions = reader.size()
        if dimensions.isValid():
            reader.setScaledSize(dimensions.scaled(QSize(280, 158), Qt.AspectRatioMode.KeepAspectRatio))
        image = reader.read()
        if not image.isNull() and (image.width() > 280 or image.height() > 158):
            image = image.scaled(280, 158, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        return image

    @classmethod
    def _cache_thumbnail(cls, key, image):
        previous = cls._thumbnail_cache.pop(key, None)
        if previous is not None:
            cls._thumbnail_cache_bytes -= previous.sizeInBytes()
        cls._thumbnail_cache[key] = image
        cls._thumbnail_cache_bytes += image.sizeInBytes()
        while cls._thumbnail_cache and (len(cls._thumbnail_cache) > cls.MAX_THUMBNAILS or
                cls._thumbnail_cache_bytes > cls.MAX_THUMBNAIL_BYTES):
            removed_key, removed = cls._thumbnail_cache.popitem(last=False)
            cls._thumbnail_cache_bytes -= removed.sizeInBytes()

    def _request_thumbnail(self, art, label):
        path = art.get("path", "")
        key = art.get("_thumbnail_key", (path, "unresolved"))
        image = self._thumbnail_cache.get(key)
        if image is not None:
            self._thumbnail_cache.move_to_end(key)
            self._set_thumbnail(label, image)
            return
        reference = weakref.ref(label)
        if key in self._thumbnail_waiters:
            self._thumbnail_waiters[key].append(reference)
            return
        self._thumbnail_waiters[key] = [reference]
        def decode():
            actual_key = self._thumbnail_key(path)
            return actual_key, self._decode_thumbnail(path)
        self.tasks.submit("thumbnail:" + repr(key), decode,
            lambda result: self._thumbnail_ready(key, path, result),
            lambda error: self._thumbnail_ready(key, path, (key, QImage())))

    def _thumbnail_ready(self, request_key, path, result):
        actual_key, image = result
        self._cache_thumbnail(actual_key, image)
        for artwork in self.all_artworks:
            if artwork.get("path") == path:
                artwork["_thumbnail_key"] = actual_key
        for reference in self._thumbnail_waiters.pop(request_key, []):
            label = reference()
            if label is not None:
                self._set_thumbnail(label, image)

    @staticmethod
    def _set_thumbnail(label, image):
        try:
            if image.isNull():
                label.setText(_("ไม่สามารถแสดงภาพได้"))
            else:
                label.setPixmap(QPixmap.fromImage(image))
        except RuntimeError:
            # Filtering may destroy a label while its worker is still decoding.
            pass

    def _create_artwork_card(self, art: dict) -> QFrame:
        card = QFrame()
        card.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        card.setProperty("class", "PanelCard")
        card.setStyleSheet("""
            QFrame {
                background-color: #131722;
                border: 1px solid rgba(255, 255, 255, 0.09);
                border-radius: 8px;
            }
            QFrame:hover {
                border-color: rgba(168, 85, 247, 0.5);
                background-color: #161c2a;
            }
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        img_path = art.get("path", "")
        w, h = art.get("width", 0), art.get("height", 0)
        source = art.get("source", "Unknown")
        role = art.get("role", "")
        label_text = art.get("label", art.get("filename", ""))
        is_primary = art.get("is_primary", False)

        # 1. Image Thumbnail Preview (280x158 - 16:9 aspect)
        thumb_lbl = QLabel()
        thumb_lbl.setFixedSize(280, 158)
        thumb_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        thumb_lbl.setStyleSheet("background-color: #0b0e14; border-radius: 6px;")
        thumb_lbl.setCursor(Qt.CursorShape.PointingHandCursor)
        thumb_lbl.setToolTip(_("🔍 คลิกเพื่อดูรูปภาพขนาดเต็มในโปรแกรมเปิดภาพของระบบ"))
        thumb_lbl.mousePressEvent = lambda e, p=img_path: self._open_full_image(p)
        thumb_lbl.setObjectName("ArtworkThumbnail")
        thumb_lbl.setText(_("กำลังโหลดภาพ..."))
        self._request_thumbnail(art, thumb_lbl)

        layout.addWidget(thumb_lbl, alignment=Qt.AlignmentFlag.AlignCenter)

        # 2. Badges & Source Meta Row
        badge_row = QHBoxLayout()
        badge_row.setSpacing(6)

        # Source Badge
        lbl_badge = QLabel()
        lbl_badge.setFixedHeight(24)
        is_logo_item = (role == "LOGO" or "logo" in art.get("filename", "").lower())
        if is_logo_item:
            lbl_badge.setText("✨ โลโก้เกม (Logo PNG)")
            lbl_badge.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7c3aed, stop:1 #d97706); color: #ffffff; font-weight: bold; border-radius: 4px; padding: 2px 6px; font-size: 10px;")
        elif "sony" in source.lower():
            if w >= 3840:
                lbl_badge.setText("Sony PS5 4K")
                lbl_badge.setStyleSheet("background-color: #6366f1; color: #ffffff; font-weight: bold; border-radius: 4px; padding: 2px 6px; font-size: 10px;")
            else:
                lbl_badge.setText("Sony 1080p")
                lbl_badge.setStyleSheet("background-color: #0284c7; color: #ffffff; font-weight: bold; border-radius: 4px; padding: 2px 6px; font-size: 10px;")
        elif "steam" in source.lower():
            if "hero" in role.lower():
                lbl_badge.setText("Steam Hero")
                lbl_badge.setStyleSheet("background-color: #d97706; color: #ffffff; font-weight: bold; border-radius: 4px; padding: 2px 6px; font-size: 10px;")
            elif "portrait" in role.lower() or "poster" in role.lower():
                lbl_badge.setText("Steam Poster")
                lbl_badge.setStyleSheet("background-color: #0d9488; color: #ffffff; font-weight: bold; border-radius: 4px; padding: 2px 6px; font-size: 10px;")
            else:
                lbl_badge.setText("Steam Official")
                lbl_badge.setStyleSheet("background-color: #475569; color: #ffffff; font-weight: bold; border-radius: 4px; padding: 2px 6px; font-size: 10px;")
        else:
            lbl_badge.setText(source)
            lbl_badge.setStyleSheet("background-color: #334155; color: #94a3b8; border-radius: 4px; padding: 2px 6px; font-size: 10px;")

        badge_row.addWidget(lbl_badge)

        # Resolution Tag
        res_text = f"{w} × {h}"
        if w >= 3840:
            res_text += " (4K UHD)"
        elif w >= 1920 and h >= 1080:
            res_text += " (Full HD)"
        lbl_res = QLabel(res_text)
        lbl_res.setFixedHeight(24)
        lbl_res.setStyleSheet("color: #94a3b8; font-size: 10px;")
        badge_row.addWidget(lbl_res)

        badge_row.addStretch()

        if is_primary or role == "CURRENT_COVER":
            lbl_active = QLabel("⭐ ปกปัจจุบัน")
            lbl_active.setStyleSheet("background-color: rgba(34, 197, 94, 0.2); color: #22c55e; border: 1px solid #16a34a; font-weight: bold; border-radius: 4px; padding: 2px 6px; font-size: 9px;")
            badge_row.addWidget(lbl_active)

        layout.addLayout(badge_row)

        # 3. Label / Role text
        lbl_caption = QLabel(label_text)
        lbl_caption.setStyleSheet("color: #e2e8f0; font-size: 11px; font-weight: 500;")
        lbl_caption.setWordWrap(True)
        lbl_caption.setFixedHeight(28)
        layout.addWidget(lbl_caption)

        # 4. Action Buttons Row
        btn_box = QHBoxLayout()
        btn_box.setSpacing(6)

        btn_set_cover = QPushButton(_("📌 ตั้งเป็นภาพปก"))
        btn_set_cover.setProperty("class", "BtnAI")
        btn_set_cover.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_set_cover.setStyleSheet("""
            QPushButton {
                background-color: rgba(139, 92, 246, 0.2);
                color: #c084fc;
                border: 1px solid #a855f7;
                border-radius: 5px;
                padding: 4px 8px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8b5cf6;
                color: #ffffff;
            }
        """)
        btn_set_cover.clicked.connect(lambda checked, p=img_path: self._set_as_cover(p))
        btn_box.addWidget(btn_set_cover, stretch=1)

        btn_view = QPushButton(_("🔍 ดูเต็มจอ"))
        btn_view.setProperty("class", "BtnSecondary")
        btn_view.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_view.setStyleSheet("padding: 4px 8px; font-size: 11px;")
        btn_view.clicked.connect(lambda checked, p=img_path: self._open_full_image(p))
        btn_box.addWidget(btn_view)

        btn_copy = QPushButton(_("📋"))
        btn_copy.setProperty("class", "BtnSecondary")
        btn_copy.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_copy.setToolTip(_("คัดลอกพาธไฟล์รูปภาพ/โลโก้ลงคลิปบอร์ด"))
        btn_copy.setStyleSheet("padding: 4px 6px; font-size: 11px;")
        btn_copy.clicked.connect(lambda checked, p=img_path, b=btn_copy: self._copy_path_feedback(p, b))
        btn_box.addWidget(btn_copy)

        layout.addLayout(btn_box)

        return card

    def _set_as_cover(self, image_path: str):
        if not image_path or not os.path.exists(image_path):
            QMessageBox.warning(self, _("แจ้งเตือน"), _("ไม่พบไฟล์ภาพที่เลือก"))
            return

        if "set-cover" in self.tasks.jobs:
            return
        workspace, game_name = self.workspace_path, self.game_name
        self.tasks.submit("set-cover", lambda: ArtHarvesterService.set_as_project_cover(
            workspace_path=workspace, image_path=image_path, game_name=game_name),
            lambda success: self._cover_saved(image_path, success), self._on_harvest_error)

    def _cover_saved(self, image_path, success):
        if success:
            for a in self.all_artworks:
                a["is_primary"] = (a.get("path") == image_path)

            self.cover_selected.emit(image_path)
            self._render_cards()
            QMessageBox.information(
                self,
                _("สำเร็จ"),
                _("ตั้งภาพนี้เป็นภาพปกหลัก (thub_cover.jpg) เรียบร้อยแล้ว!")
            )
        else:
            QMessageBox.critical(self, _("เกิดข้อผิดพลาด"), _("ไม่สามารถคัดลอกภาพเป็นภาพปกหลักได้"))

    def _open_full_image(self, image_path: str):
        if image_path and os.path.exists(image_path):
            try:
                os.startfile(image_path)
            except Exception as e:
                QMessageBox.warning(self, _("แจ้งเตือน"), _("ไม่สามารถเปิดภาพได้: {e}").format(e=str(e)))

    def _quick_download_dimension(self, dim_key: str):
        if self._harvest_in_progress or "harvest-artworks" in self.tasks.jobs:
            return
        self._set_download_busy(True)
        self.btn_harvest.setEnabled(False)
        self.btn_harvest.setText(_("⏳ กำลังโหลดขนาด {key}...").format(key=dim_key))

        game_name, workspace = self.game_name, self.workspace_path
        def work():
            return ArtHarvesterService.get_or_harvest_dimension(
                game_name=game_name,
                workspace_path=workspace,
                dim_key=dim_key
            )

        def on_done(res):
            self._set_download_busy(False)
            self.btn_harvest.setEnabled(True)
            self.btn_harvest.setText(_("🔄 ดึงภาพจาก Sony && Steam"))
            self._load_artworks(auto_harvest_if_empty=False)
            # Switch filter to show this dimension
            target_filter = dim_key if dim_key in self._filter_buttons else "all"
            self._set_filter(target_filter)

        self.tasks.submit(
            "harvest-artworks",
            work,
            on_done,
            self._on_harvest_error
        )

    def _copy_path_feedback(self, path: str, btn: QPushButton):
        if path and os.path.exists(path):
            from PyQt6.QtWidgets import QApplication
            from PyQt6.QtCore import QTimer
            QApplication.clipboard().setText(os.path.normpath(path))
            orig_text = btn.text()
            btn.setText(_("✓"))
            QTimer.singleShot(1500, lambda: btn.setText(orig_text))

