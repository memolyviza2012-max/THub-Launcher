from core.qt_tasks import BackgroundTasks, TaskDialogMixin
import os
import shutil
from PIL import Image
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSlider, QLineEdit, QFileDialog, QFrame, QMessageBox, QWidget
)
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath, QColor, QCursor, QImage
from PyQt6.QtCore import Qt, QRectF, QPoint, pyqtSignal
from core.steam_service import SteamService
from core.art_harvester_service import ArtHarvesterService
from ui_pyqt6.dialogs.art_gallery_dialog_qt import ArtGalleryDialogQt
from i18n_helper import _


class CoverPreviewWidget(QWidget):
    """
    Interactive 16:9 Cover Preview (384x216).
    Supports direct click-and-drag panning.
    """
    pan_changed = pyqtSignal(int, int)

    PREVIEW_WIDTH = 384
    PREVIEW_HEIGHT = 216

    def __init__(self, image_path="", offset_x=0, offset_y=0, zoom=1.0, parent=None):
        super().__init__(parent)
        self.setFixedSize(self.PREVIEW_WIDTH, self.PREVIEW_HEIGHT)
        self.setCursor(Qt.CursorShape.SizeAllCursor)

        self.image_path = image_path
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.zoom = zoom
        self._raw_pixmap = None
        self._drag_start = None
        self._start_offset_x = 0
        self._start_offset_y = 0

        if self.image_path and os.path.exists(self.image_path):
            self.set_image_path(self.image_path)

    def set_image_path(self, path):
        self.image_path = path
        if path and os.path.exists(path):
            img = QImage(path)
            if not img.isNull() and img.width() > 0 and img.height() > 0:
                self._raw_pixmap = QPixmap.fromImage(img)
            else:
                self._raw_pixmap = None
        else:
            self._raw_pixmap = None
        self.update()

    def set_params(self, offset_x, offset_y, zoom):
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.zoom = zoom
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start = event.pos()
            self._start_offset_x = self.offset_x
            self._start_offset_y = self.offset_y
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton and self._drag_start is not None:
            delta = event.pos() - self._drag_start
            dx = int(delta.x() / (self.PREVIEW_WIDTH * 0.35) * 100)
            dy = int(delta.y() / (self.PREVIEW_HEIGHT * 0.35) * 100)
            new_x = max(-100, min(100, self._start_offset_x + dx))
            new_y = max(-100, min(100, self._start_offset_y + dy))
            self.pan_changed.emit(new_x, new_y)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_start = None
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        path = QPainterPath()
        path.addRoundedRect(QRectF(0, 0, self.PREVIEW_WIDTH, self.PREVIEW_HEIGHT), 10, 10)
        painter.setClipPath(path)

        # Stylish dark background for preview frame
        painter.fillRect(0, 0, self.PREVIEW_WIDTH, self.PREVIEW_HEIGHT, QColor(15, 23, 42))

        if self._raw_pixmap and not self._raw_pixmap.isNull():
            orig_w = self._raw_pixmap.width()
            orig_h = self._raw_pixmap.height()

            is_logo = ("logo" in (self.image_path or "").lower())
            if is_logo:
                # For transparent PNG logos: fit entire logo centered comfortably with zoom
                scale = min(self.PREVIEW_WIDTH / orig_w, self.PREVIEW_HEIGHT / orig_h) * 0.85 * max(0.5, min(2.0, self.zoom))
                new_w = max(1, int(orig_w * scale))
                new_h = max(1, int(orig_h * scale))
                scaled = self._raw_pixmap.scaled(
                    new_w, new_h,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                pos_x = int((self.PREVIEW_WIDTH - scaled.width()) / 2.0 + (self.offset_x / 100.0) * (self.PREVIEW_WIDTH * 0.35))
                pos_y = int((self.PREVIEW_HEIGHT - scaled.height()) / 2.0 + (self.offset_y / 100.0) * (self.PREVIEW_HEIGHT * 0.35))
                painter.drawPixmap(pos_x, pos_y, scaled)
            else:
                base_scale = max(self.PREVIEW_WIDTH / orig_w, self.PREVIEW_HEIGHT / orig_h)
                scale = base_scale * max(1.0, self.zoom)

                new_w = max(self.PREVIEW_WIDTH, int(orig_w * scale))
                new_h = max(self.PREVIEW_HEIGHT, int(orig_h * scale))

                scaled = self._raw_pixmap.scaled(
                    new_w, new_h,
                    Qt.AspectRatioMode.IgnoreAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )

                center_x = (new_w - self.PREVIEW_WIDTH) / 2.0
                center_y = (new_h - self.PREVIEW_HEIGHT) / 2.0
                max_shift_x = (new_w - self.PREVIEW_WIDTH) / 2.0
                max_shift_y = (new_h - self.PREVIEW_HEIGHT) / 2.0

                crop_x = int(center_x + (self.offset_x / 100.0) * max_shift_x)
                crop_y = int(center_y + (self.offset_y / 100.0) * max_shift_y)

                crop_x = max(0, min(crop_x, new_w - self.PREVIEW_WIDTH))
                crop_y = max(0, min(crop_y, new_h - self.PREVIEW_HEIGHT))

                painter.drawPixmap(0, 0, scaled.copy(crop_x, crop_y, self.PREVIEW_WIDTH, self.PREVIEW_HEIGHT))
        else:
            painter.setPen(QColor(148, 163, 184))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, _("ยังไม่มีภาพปก (กดเลือกภาพด้านล่าง)"))

        painter.setClipping(False)
        painter.setPen(QColor("#2a334d"))
        painter.drawRoundedRect(QRectF(0.5, 0.5, self.PREVIEW_WIDTH - 1, self.PREVIEW_HEIGHT - 1), 10, 10)
        painter.end()


class CoverEditorDialogQt(TaskDialogMixin, QDialog):
    """
    Cover Image Editor Dialog.
    Allows importing from local files, downloading from Steam/URL,
    and fine-tuning 4-way pan offsets (Up/Down/Left/Right) and zoom.
    """
    cover_saved = pyqtSignal(dict)

    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.tasks = BackgroundTasks(self)
        self.project = dict(project)
        self.workspace_path = self.project.get("path", "")
        self.current_cover_path = self._find_existing_cover()
        self.temp_cover_path = self.current_cover_path

        self.offset_x = int(self.project.get("cover_offset_x", 0))
        self.offset_y = int(self.project.get("cover_offset_y", 0))
        self.zoom = float(self.project.get("cover_zoom", 1.0))

        self.setWindowTitle(_("🖼️ ปรับแต่งภาพปก — {name}").format(name=self.project.get('name', 'Game')))
        self.setFixedWidth(560)

        self._build_ui()

    def _find_existing_cover(self):
        if not self.workspace_path or not os.path.exists(self.workspace_path):
            return ""

        candidates = [
            "thub_cover.jpg", "thub_cover.png", "cover.jpg", "cover.png",
            "cover_landscape_616x353.jpg", "header.jpg", "header.png",
            "poster.jpg", "poster.png", "banner.jpg", "banner.png"
        ]
        for c in candidates:
            full = os.path.join(self.workspace_path, c)
            if os.path.exists(full) and os.path.getsize(full) > 500:
                return full

        # Check 07_Image_Resources/Official_Art/
        art_dir = os.path.join(self.workspace_path, "07_Image_Resources", "Official_Art")
        if os.path.exists(art_dir):
            for art_name in ("cover_landscape_616x353.jpg", "cover_header_460x215.jpg", "banner_hero_1920x620.jpg", "cover_portrait_600x900.jpg", "thub_cover.jpg"):
                full = os.path.join(art_dir, art_name)
                if os.path.exists(full) and os.path.getsize(full) > 500:
                    return full

        # Also search for any image file directly inside workspace
        try:
            for item in os.listdir(self.workspace_path):
                if item.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp')):
                    full = os.path.join(self.workspace_path, item)
                    if os.path.isfile(full) and os.path.getsize(full) > 500:
                        return full
        except Exception:
            pass

        # Check central cache
        try:
            from core.steam_service import SteamService
            central = SteamService.get_central_cover_path(self.project.get("name", ""))
            if central and os.path.exists(central):
                return central
        except Exception:
            pass

        return ""

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        # 1. Header
        lbl_h = QLabel(_("🖼️ จัดตำแหน่งและเปลี่ยนภาพปก (16:9 Widescreen)"))
        lbl_h.setProperty("class", "PageTitle")
        layout.addWidget(lbl_h)

        lbl_hint = QLabel(_("คลิกลากเมาส์บนภาพ หรือเลื่อนแถบสไลเดอร์เพื่อจัดตำแหน่งภาพ ขึ้น/ลง/ซ้าย/ขวา"))
        lbl_hint.setProperty("class", "SubText")
        layout.addWidget(lbl_hint)

        # 2. Centered Preview Widget
        preview_box = QHBoxLayout()
        preview_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview = CoverPreviewWidget(
            image_path=self.current_cover_path,
            offset_x=self.offset_x,
            offset_y=self.offset_y,
            zoom=self.zoom
        )
        self.preview.pan_changed.connect(self._on_preview_pan)
        preview_box.addWidget(self.preview)
        layout.addLayout(preview_box)

        # 3. 4-Way Panning & Zoom Controls Frame
        ctrl_frame = QFrame()
        ctrl_frame.setProperty("class", "InnerCard")
        cf_layout = QVBoxLayout(ctrl_frame)
        cf_layout.setContentsMargins(14, 10, 14, 10)
        cf_layout.setSpacing(8)

        # Pan X Slider
        row_x = QHBoxLayout()
        lbl_px = QLabel(_("↔️ ซ้าย - ขวา:"))
        lbl_px.setFixedWidth(85)
        self.slider_x = QSlider(Qt.Orientation.Horizontal)
        self.slider_x.setRange(-100, 100)
        self.slider_x.setValue(self.offset_x)
        self.slider_x.valueChanged.connect(self._on_slider_changed)
        self.lbl_val_x = QLabel(f"{self.offset_x}%")
        self.lbl_val_x.setFixedWidth(40)
        self.lbl_val_x.setProperty("class", "CardTitle")
        row_x.addWidget(lbl_px)
        row_x.addWidget(self.slider_x)
        row_x.addWidget(self.lbl_val_x)
        cf_layout.addLayout(row_x)

        # Pan Y Slider
        row_y = QHBoxLayout()
        lbl_py = QLabel(_("↕️ ขึ้น - ลง:"))
        lbl_py.setFixedWidth(85)
        self.slider_y = QSlider(Qt.Orientation.Horizontal)
        self.slider_y.setRange(-100, 100)
        self.slider_y.setValue(self.offset_y)
        self.slider_y.valueChanged.connect(self._on_slider_changed)
        self.lbl_val_y = QLabel(f"{self.offset_y}%")
        self.lbl_val_y.setFixedWidth(40)
        self.lbl_val_y.setProperty("class", "CardTitle")
        row_y.addWidget(lbl_py)
        row_y.addWidget(self.slider_y)
        row_y.addWidget(self.lbl_val_y)
        cf_layout.addLayout(row_y)

        # Zoom Slider + Reset Button
        row_z = QHBoxLayout()
        lbl_pz = QLabel(_("🔍 ซูมภาพ:"))
        lbl_pz.setFixedWidth(85)
        self.slider_z = QSlider(Qt.Orientation.Horizontal)
        self.slider_z.setRange(100, 250)
        self.slider_z.setValue(int(self.zoom * 100))
        self.slider_z.valueChanged.connect(self._on_slider_changed)
        self.lbl_val_z = QLabel(f"{self.zoom:.1f}x")
        self.lbl_val_z.setFixedWidth(40)
        self.lbl_val_z.setProperty("class", "CardTitle")

        btn_reset = QPushButton(_("🔄 กึ่งกลาง"))
        btn_reset.setProperty("class", "BtnSecondary")
        btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_reset.clicked.connect(self._reset_position)

        row_z.addWidget(lbl_pz)
        row_z.addWidget(self.slider_z)
        row_z.addWidget(self.lbl_val_z)
        row_z.addWidget(btn_reset)
        cf_layout.addLayout(row_z)

        layout.addWidget(ctrl_frame)

        # 3.5 Quick Dimensions & Official Logo Section
        dim_card = QFrame()
        dim_card.setProperty("class", "InnerCard")
        dim_layout = QVBoxLayout(dim_card)
        dim_layout.setContentsMargins(14, 10, 14, 10)
        dim_layout.setSpacing(8)

        lbl_dim_title = QLabel(_("📐 เลือกขนาดหน้าปก & โลโก้ทางการ (Quick Sizes & Logo):"))
        lbl_dim_title.setStyleSheet("color: #c084fc; font-weight: bold; font-size: 11px;")
        dim_layout.addWidget(lbl_dim_title)

        # Dimension Buttons Row
        dim_btn_row = QHBoxLayout()
        dim_btn_row.setSpacing(6)

        self.btn_dim_wide = QPushButton(_("📺 แนวนอน 16:9"))
        self.btn_dim_wide.setProperty("class", "BtnSecondary")
        self.btn_dim_wide.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_dim_wide.setToolTip(_("โหลดภาพแนวนอน 16:9 (Sony 4K UHD / Steam Capsule 616x353)"))
        self.btn_dim_wide.setStyleSheet("font-size: 10px; padding: 5px 4px; font-weight: bold;")
        self.btn_dim_wide.clicked.connect(lambda: self._load_dimension("widescreen"))
        dim_btn_row.addWidget(self.btn_dim_wide)

        self.btn_dim_portrait = QPushButton(_("📱 แนวตั้ง (600x900)"))
        self.btn_dim_portrait.setProperty("class", "BtnSecondary")
        self.btn_dim_portrait.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_dim_portrait.setToolTip(_("โหลดภาพโปสเตอร์แนวตั้ง 2:3 สำหรับ Steam Library Grid (600x900)"))
        self.btn_dim_portrait.setStyleSheet("font-size: 10px; padding: 5px 4px;")
        self.btn_dim_portrait.clicked.connect(lambda: self._load_dimension("portrait"))
        dim_btn_row.addWidget(self.btn_dim_portrait)

        self.btn_dim_hero = QPushButton(_("🚩 แบนเนอร์ (1920x620)"))
        self.btn_dim_hero.setProperty("class", "BtnSecondary")
        self.btn_dim_hero.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_dim_hero.setToolTip(_("โหลดภาพแบนเนอร์กว้าง Steam Library Hero (1920x620)"))
        self.btn_dim_hero.setStyleSheet("font-size: 10px; padding: 5px 4px;")
        self.btn_dim_hero.clicked.connect(lambda: self._load_dimension("hero"))
        dim_btn_row.addWidget(self.btn_dim_hero)

        self.btn_dim_header = QPushButton(_("🏷️ ส่วนหัว (460x215)"))
        self.btn_dim_header.setProperty("class", "BtnSecondary")
        self.btn_dim_header.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_dim_header.setToolTip(_("โหลดภาพปกส่วนหัวร้านค้า Steam Store Header (460x215)"))
        self.btn_dim_header.setStyleSheet("font-size: 10px; padding: 5px 4px;")
        self.btn_dim_header.clicked.connect(lambda: self._load_dimension("header"))
        dim_btn_row.addWidget(self.btn_dim_header)

        self.btn_dim_logo = QPushButton(_("✨ โลโก้เกม (Logo PNG)"))
        self.btn_dim_logo.setProperty("class", "BtnAI")
        self.btn_dim_logo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_dim_logo.setToolTip(_("ดึงไฟล์โลโก้เกมแบบโปร่งใส (Transparent PNG) แท้จาก Official Store ทันที"))
        self.btn_dim_logo.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7c3aed, stop:1 #d97706);
                color: #ffffff;
                font-size: 10px;
                padding: 5px 8px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #9333ea, stop:1 #f59e0b);
            }
        """)
        self.btn_dim_logo.clicked.connect(lambda: self._load_dimension("logo"))
        dim_btn_row.addWidget(self.btn_dim_logo)

        dim_layout.addLayout(dim_btn_row)

        # Dimension Info & Quick Action Strip
        dim_info_box = QHBoxLayout()
        dim_info_box.setSpacing(6)

        self.lbl_dim_status = QLabel(_("💡 คลิกเลือกขนาดภาพปกที่ต้องการ หรือคลิก '✨ โลโก้เกม' เพื่อดึงโลโก้โปร่งใสมาใช้งาน"))
        self.lbl_dim_status.setStyleSheet("color: #94a3b8; font-size: 10px;")
        self.lbl_dim_status.setWordWrap(True)
        dim_info_box.addWidget(self.lbl_dim_status, stretch=1)

        self.btn_open_asset = QPushButton(_("📂 เปิดไฟล์"))
        self.btn_open_asset.setProperty("class", "BtnSecondary")
        self.btn_open_asset.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_open_asset.setStyleSheet("font-size: 10px; padding: 3px 8px;")
        self.btn_open_asset.setToolTip(_("เปิดดูไฟล์รูปภาพ/โลโก้ที่เลือกด้วยโปรแกรมดูภาพของระบบ"))
        self.btn_open_asset.clicked.connect(self._open_current_asset)
        self.btn_open_asset.setVisible(False)
        dim_info_box.addWidget(self.btn_open_asset)

        self.btn_copy_path = QPushButton(_("📋 คัดลอกพาธ"))
        self.btn_copy_path.setProperty("class", "BtnSecondary")
        self.btn_copy_path.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_copy_path.setStyleSheet("font-size: 10px; padding: 3px 8px;")
        self.btn_copy_path.setToolTip(_("คัดลอกตำแหน่งไฟล์ (Absolute Path) ลงคลิปบอร์ด เพื่อนำไปวางใน Photoshop"))
        self.btn_copy_path.clicked.connect(self._copy_current_asset_path)
        self.btn_copy_path.setVisible(False)
        dim_info_box.addWidget(self.btn_copy_path)

        dim_layout.addLayout(dim_info_box)
        layout.addWidget(dim_card)

        # 4. Image Source Options (Browse Local / Steam / URL)
        src_frame = QFrame()
        src_frame.setProperty("class", "InnerCard")
        sf_layout = QVBoxLayout(src_frame)
        sf_layout.setContentsMargins(14, 10, 14, 10)
        sf_layout.setSpacing(8)

        # Local File Row
        row_local = QHBoxLayout()
        lbl_loc = QLabel(_("📂 ภาพในเครื่อง:"))
        lbl_loc.setFixedWidth(100)
        btn_browse = QPushButton(_("📁 เลือกไฟล์รูปภาพ (.png, .jpg, .webp)..."))
        btn_browse.setProperty("class", "BtnSecondary")
        btn_browse.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_browse.clicked.connect(self._browse_local_image)
        row_local.addWidget(lbl_loc)
        row_local.addWidget(btn_browse, stretch=1)
        sf_layout.addLayout(row_local)

        # Sony & Steam Multi-Source Harvester Row
        row_harvester = QHBoxLayout()
        lbl_harv = QLabel(_("🎮 Sony 4K & Steam:"))
        lbl_harv.setFixedWidth(135)


        btn_auto_harvest = QPushButton(_("⚡ ดึงภาพ 4K (Sony && Steam)"))
        btn_auto_harvest.setProperty("class", "BtnAI")
        btn_auto_harvest.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_auto_harvest.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7c3aed, stop:1 #2563eb);
                color: #ffffff;
                font-weight: bold;
                padding: 6px 8px;
                border-radius: 6px;
                font-size: 10.5px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #9333ea, stop:1 #3b82f6);
            }
        """)

        btn_auto_harvest.clicked.connect(self._auto_harvest_sony_steam)
        row_harvester.addWidget(lbl_harv)
        row_harvester.addWidget(btn_auto_harvest, stretch=1)

        btn_gallery = QPushButton(_("🖼️ คลังภาพเกม (Gallery)..."))
        btn_gallery.setProperty("class", "BtnSecondary")
        btn_gallery.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_gallery.setStyleSheet("padding: 6px 10px; font-size: 11px;")
        btn_gallery.clicked.connect(self._open_art_gallery)
        row_harvester.addWidget(btn_gallery)

        sf_layout.addLayout(row_harvester)

        # Steam Search Row
        row_steam = QHBoxLayout()
        lbl_st = QLabel(_("🌐 ค้นหาจาก Steam:"))
        lbl_st.setFixedWidth(100)
        self.txt_steam = QLineEdit(self.project.get("name", ""))
        self.txt_steam.setPlaceholderText(_("ชื่อเกมสำหรับค้นหาบน Steam..."))
        btn_steam = QPushButton(_("🔍 โหลดจาก Steam"))
        btn_steam.setProperty("class", "BtnSecondary")
        btn_steam.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_steam.clicked.connect(self._download_from_steam)
        row_steam.addWidget(lbl_st)
        row_steam.addWidget(self.txt_steam, stretch=1)
        row_steam.addWidget(btn_steam)
        sf_layout.addLayout(row_steam)

        # Direct URL Row
        row_url = QHBoxLayout()
        lbl_u = QLabel(_("🔗 ลิงก์ URL ตรง:"))
        lbl_u.setFixedWidth(100)
        self.txt_url = QLineEdit()
        self.txt_url.setPlaceholderText(_("วาง URL ภาพ (.jpg, .png)..."))
        btn_url = QPushButton(_("📥 โหลดจาก URL"))
        btn_url.setProperty("class", "BtnSecondary")
        btn_url.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_url.clicked.connect(self._download_from_url)
        row_url.addWidget(lbl_u)
        row_url.addWidget(self.txt_url, stretch=1)
        row_url.addWidget(btn_url)
        sf_layout.addLayout(row_url)

        layout.addWidget(src_frame)

        # 5. Bottom Dialog Buttons (Cancel / Save)
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        btn_cancel = QPushButton(_("ยกเลิก"))
        btn_cancel.setProperty("class", "BtnSecondary")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_cancel)

        btn_save = QPushButton(_("💾 บันทึกภาพปก"))
        btn_save.setProperty("class", "BtnPrimary")
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.clicked.connect(self._save_cover)
        btn_row.addWidget(btn_save)

        layout.addLayout(btn_row)

    def _on_preview_pan(self, new_x, new_y):
        self.offset_x = new_x
        self.offset_y = new_y
        self.slider_x.blockSignals(True)
        self.slider_y.blockSignals(True)
        self.slider_x.setValue(new_x)
        self.slider_y.setValue(new_y)
        self.lbl_val_x.setText(f"{new_x}%")
        self.lbl_val_y.setText(f"{new_y}%")
        self.slider_x.blockSignals(False)
        self.slider_y.blockSignals(False)
        self.preview.set_params(self.offset_x, self.offset_y, self.zoom)

    def _on_slider_changed(self):
        self.offset_x = self.slider_x.value()
        self.offset_y = self.slider_y.value()
        self.zoom = self.slider_z.value() / 100.0

        self.lbl_val_x.setText(f"{self.offset_x}%")
        self.lbl_val_y.setText(f"{self.offset_y}%")
        self.lbl_val_z.setText(f"{self.zoom:.1f}x")

        self.preview.set_params(self.offset_x, self.offset_y, self.zoom)

    def _reset_position(self):
        self.slider_x.setValue(0)
        self.slider_y.setValue(0)
        self.slider_z.setValue(100)

    def _browse_local_image(self):
        start_dir = ""
        if self.workspace_path and os.path.exists(self.workspace_path):
            start_dir = os.path.normpath(self.workspace_path)
        else:
            try:
                from core.config_manager import ConfigManager
                default_ws = ConfigManager().get("default_workspace_dir", r"E:\Mod_Workspace")
                if default_ws and os.path.exists(default_ws):
                    start_dir = os.path.normpath(default_ws)
            except Exception:
                pass

        path, _ = QFileDialog.getOpenFileName(
            self,
            "เลือกภาพปกเกม",
            start_dir,
            "รูปภาพ (*.png *.jpg *.jpeg *.webp *.bmp)"
        )
        if path and os.path.exists(path):
            self.temp_cover_path = path
            self.preview.set_image_path(path)
            self._reset_position()

    def _download_from_steam(self):
        game_name = self.txt_steam.text().strip()
        if not game_name:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณาระบุชื่อเกมสำหรับค้นหาบน Steam")
            return

        self._start_download(lambda dest: SteamService.download_steam_cover_sync(game_name, dest), "steam_preview.jpg")

    def _auto_harvest_sony_steam(self):
        game_name = self.txt_steam.text().strip() or self.project.get("name", "")
        if not game_name:
            QMessageBox.warning(self, _("แจ้งเตือน"), _("กรุณาระบุชื่อเกมสำหรับค้นหาภาพ"))
            return

        if "art-harvest" in self.tasks.jobs:
            return

        def work():
            return ArtHarvesterService.harvest_all_artworks(game_name, self.workspace_path)

        def on_done(result):
            if result and result.get("success") and result.get("primary_cover"):
                best_cover = result["primary_cover"]
                self.temp_cover_path = best_cover
                self.preview.set_image_path(best_cover)
                self._reset_position()
                QMessageBox.information(
                    self,
                    _("ดึงภาพสำเร็จ"),
                    _("ดึงภาพความละเอียดสูงจาก Sony & Steam สำเร็จ!\nพบทั้งหมด {total} ภาพ (Sony: {sony}, Steam: {steam})\nและเลือกภาพ 16:9 ที่ดีที่สุดเป็นภาพปกให้เรียบร้อยแล้ว").format(
                        total=result.get("total_images", 0),
                        sony=result.get("sony_count", 0),
                        steam=result.get("steam_count", 0)
                    )
                )
            else:
                QMessageBox.warning(
                    self,
                    _("ผลการค้นหา"),
                    _("ไม่พบภาพใหม่จาก Sony หรือ Steam สำหรับชื่อเกมนี้ คุณสามารถเปิด 'คลังภาพเกม' เพื่อเลือกจากภาพเดิมได้")
                )

        self.tasks.submit(
            "art-harvest",
            work,
            on_done,
            lambda err: QMessageBox.warning(self, _("ข้อผิดพลาด"), str(err))
        )

    def _open_art_gallery(self):
        dlg = ArtGalleryDialogQt(
            project=self.project,
            game_name=self.txt_steam.text().strip() or self.project.get("name", ""),
            workspace_path=self.workspace_path,
            parent=self
        )
        def on_chosen(img_path):
            self.temp_cover_path = img_path
            self.preview.set_image_path(img_path)
            self._reset_position()

        dlg.cover_selected.connect(on_chosen)
        dlg.exec()


    def _download_from_url(self):
        url = self.txt_url.text().strip()
        if not url:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณาระบุ URL ของรูปภาพ")
            return
        self._start_download(lambda dest: SteamService.download_image_from_url(url, dest), "url_preview.jpg")

    def _start_download(self, download, filename):
        if "cover-download" in self.tasks.jobs:
            return
        workspace = self.workspace_path
        def work():
            cache_dir = os.path.join(workspace, ".thub_cache")
            os.makedirs(cache_dir, exist_ok=True)
            dest = os.path.join(cache_dir, filename)
            success, result = download(dest)
            if not success:
                raise OSError(result)
            return dest
        self.tasks.submit("cover-download", work, self._download_ready,
                          lambda error: QMessageBox.warning(self, "ดาวน์โหลดไม่สำเร็จ", error))

    def _download_ready(self, dest):
        self.temp_cover_path = dest
        self.preview.set_image_path(dest)
        self._reset_position()

    def _save_cover(self):
        if not self.workspace_path or not os.path.exists(self.workspace_path):
            QMessageBox.critical(self, "ข้อผิดพลาด", "ไม่พบโฟลเดอร์ของโปรเจกต์นี้ในดิสก์")
            return

        target_cover = os.path.join(self.workspace_path, "thub_cover.jpg")

        # Copy or convert temp image to target_cover if changed
        if self.temp_cover_path and self.temp_cover_path != target_cover and os.path.exists(self.temp_cover_path):
            try:
                with Image.open(self.temp_cover_path) as im:
                    im = im.convert("RGB")
                    im.save(target_cover, "JPEG", quality=95)
            except Exception as e:
                try:
                    shutil.copy2(self.temp_cover_path, target_cover)
                except Exception as e2:
                    QMessageBox.critical(self, "บันทึกไม่สำเร็จ", f"ไม่สามารถบันทึกไฟล์ภาพปกได้:\n{e2}")
                    return

        # Update project parameters
        self.project["cover_offset_x"] = self.offset_x
        self.project["cover_offset_y"] = self.offset_y
        self.project["cover_zoom"] = self.zoom
        self.project["_cached_cover_path"] = target_cover

        # Backup to central cache
        try:
            SteamService.save_to_central_cover(self.project.get("name", ""), target_cover)
        except Exception:
            pass

        # Invalidate global card pixmap cache
        try:
            from ui_pyqt6.components.project_card_qt import ProjectCardQt
            ProjectCardQt.clear_pixmap_cache()
        except Exception:
            pass

        self.cover_saved.emit(self.project)
        self.accept()

    def _load_dimension(self, dim_key):
        game_name = self.txt_steam.text().strip() or self.project.get("name", "")
        if not game_name:
            QMessageBox.warning(self, _("แจ้งเตือน"), _("กรุณาระบุชื่อเกมสำหรับค้นหาภาพ"))
            return

        dim_names = {
            "widescreen": _("แนวนอน 16:9"),
            "portrait": _("แนวตั้ง (600x900)"),
            "hero": _("แบนเนอร์ (1920x620)"),
            "header": _("ส่วนหัว (460x215)"),
            "logo": _("โลโก้เกมโปร่งใส (Logo PNG)"),
        }
        dim_label = dim_names.get(dim_key, dim_key)

        self.lbl_dim_status.setText(_("⏳ กำลังค้นหาและดาวน์โหลด {label}...").format(label=dim_label))
        self.lbl_dim_status.setStyleSheet("color: #38bdf8; font-size: 10px;")

        def work():
            return ArtHarvesterService.get_or_harvest_dimension(
                game_name=game_name,
                workspace_path=self.workspace_path,
                dim_key=dim_key
            )

        def on_done(res):
            if res and res.get("success") and res.get("path"):
                target_path = res["path"]
                self.temp_cover_path = target_path
                self.preview.set_image_path(target_path)
                self._reset_position()

                w = res.get("width", 0)
                h = res.get("height", 0)
                fn = res.get("filename", "")
                is_logo = res.get("is_logo", False)

                if is_logo:
                    msg = _("✨ โหลดโลโก้โปร่งใสสำเร็จ: {fn} ({w}×{h} RGBA) พร้อมนำไปจัดวาง").format(fn=fn, w=w, h=h)
                else:
                    msg = _("✅ โหลดภาพ {label} สำเร็จ: {fn} ({w}×{h})").format(label=dim_label, fn=fn, w=w, h=h)

                self.lbl_dim_status.setText(msg)
                self.lbl_dim_status.setStyleSheet("color: #22c55e; font-size: 10px; font-weight: bold;")
                self.btn_open_asset.setVisible(True)
                self.btn_copy_path.setVisible(True)
            else:
                err = res.get("error", "Not found") if res else "Unknown"
                self.lbl_dim_status.setText(_("⚠️ ไม่พบภาพขนาด {label} จาก Store ({err})").format(label=dim_label, err=err))
                self.lbl_dim_status.setStyleSheet("color: #fb7185; font-size: 10px;")

        self.tasks.submit(
            f"load-dim-{dim_key}",
            work,
            on_done,
            lambda err: self.lbl_dim_status.setText(f"❌ ผิดพลาด: {err}")
        )

    def _open_current_asset(self):
        if self.temp_cover_path and os.path.exists(self.temp_cover_path):
            try:
                os.startfile(os.path.normpath(self.temp_cover_path))
            except Exception as e:
                QMessageBox.warning(self, _("แจ้งเตือน"), str(e))

    def _copy_current_asset_path(self):
        if self.temp_cover_path and os.path.exists(self.temp_cover_path):
            from PyQt6.QtWidgets import QApplication
            from PyQt6.QtCore import QTimer
            QApplication.clipboard().setText(os.path.normpath(self.temp_cover_path))
            old_text = self.btn_copy_path.text()
            self.btn_copy_path.setText(_("✓ คัดลอกแล้ว!"))
            QTimer.singleShot(2000, lambda: self.btn_copy_path.setText(old_text))

