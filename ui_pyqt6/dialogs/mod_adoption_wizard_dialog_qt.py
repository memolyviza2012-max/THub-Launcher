from core.qt_tasks import BackgroundTasks, TaskDialogMixin
# -*- coding: utf-8 -*-
"""
Mod Adoption & Restructuring Wizard Dialog (PyQt6)
===================================================
Interactive dialog allowing modders to adopt and restructure existing/legacy
mod projects from older THub versions or external tools into the standard
THub 01–07 structure, and immediately hand off to AI Helper.
"""

import os
import re
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QFrame, QFileDialog, QMessageBox, QProgressBar, QRadioButton,
    QButtonGroup, QCheckBox, QScrollArea, QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread

from i18n_helper import _
from core.mod_adoption_service import ModAdoptionService
from core.engine_scanner import EngineScanner


class AuditWorker(QThread):
    """Background worker to audit folder without freezing the UI."""
    audit_completed = pyqtSignal(dict)
    audit_failed = pyqtSignal(str)

    def __init__(self, folder_path):
        super().__init__()
        self.folder_path = folder_path

    def run(self):
        try:
            res = ModAdoptionService.audit_legacy_folder(self.folder_path)
            if res.get("success"):
                self.audit_completed.emit(res)
            else:
                self.audit_failed.emit(res.get("error", "Failed to audit folder"))
        except Exception as e:
            self.audit_failed.emit(str(e))


class RestructureWorker(QThread):
    """Background worker to execute the adoption restructure."""
    restructure_completed = pyqtSignal(dict)
    restructure_failed = pyqtSignal(str)

    def __init__(self, folder_path, options):
        super().__init__()
        self.folder_path = folder_path
        self.options = options

    def run(self):
        try:
            res = ModAdoptionService.execute_adoption_restructure(self.folder_path, self.options)
            if res.get("success"):
                self.restructure_completed.emit(res)
            else:
                self.restructure_failed.emit(res.get("error", "Restructure failed"))
        except Exception as e:
            self.restructure_failed.emit(str(e))


class ModAdoptionWizardDialogQt(TaskDialogMixin, QDialog):
    """
    PyQt6 Wizard for adopting and restructuring legacy or external mod projects.
    """

    adoption_completed = pyqtSignal(dict, bool)  # (project_entry, open_ai_helper)

    def __init__(self, parent=None, initial_folder=None, initial_path=None):
        super().__init__(parent)
        self.tasks = BackgroundTasks(self)
        self.setWindowTitle(_("🔄 สานต่องานม็อดเดิมด้วย AI Helper (Mod Adoption & Restructure)"))
        self.setFixedSize(680, 680)
        self.setStyleSheet("""
            QDialog {
                background-color: #0b0f19;
                color: #f1f5f9;
            }
        """)

        self.current_audit = None
        self.audit_worker = None
        self.restructure_worker = None
        self.initial_folder = initial_folder or initial_path

        self._build_ui()

        if self.initial_folder and os.path.exists(self.initial_folder):
            self.ent_folder.setText(os.path.normpath(self.initial_folder))
            self._start_audit(self.initial_folder)

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(18, 14, 18, 16)
        main_layout.setSpacing(12)

        # 1. Top Banner
        banner = QFrame()
        banner.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(107, 33, 168, 0.4),
                    stop:1 rgba(2, 132, 199, 0.25));
                border: 1px solid rgba(192, 132, 252, 0.4);
                border-radius: 8px;
                padding: 10px 14px;
            }
        """)
        b_layout = QVBoxLayout(banner)
        b_layout.setContentsMargins(0, 0, 0, 0)
        b_layout.setSpacing(3)

        lbl_title = QLabel("🔄 สานต่องานม็อดเดิมเข้าสู่มาตรฐาน THub (Legacy Mod Adoption)")
        lbl_title.setStyleSheet("color: #e9d5ff; font-size: 15px; font-weight: bold;")
        b_layout.addWidget(lbl_title)

        lbl_desc = QLabel("นำเข้างานม็อดเดิมจาก THub รุ่นเก่าหรือเครื่องมืออื่น จัดระเบียบเข้าสู่โครงสร้าง 01–07 และให้ AI Helper ช่วยสานต่องานทันที")
        lbl_desc.setStyleSheet("color: #94a3b8; font-size: 11px;")
        b_layout.addWidget(lbl_desc)
        main_layout.addWidget(banner)

        # 2. Folder Selection Row
        lbl_sel = QLabel("📁 โฟลเดอร์งานม็อดเดิมที่ต้องการนำมาสานต่อ *")
        lbl_sel.setStyleSheet("color: #cbd5e1; font-weight: bold; font-size: 11px;")
        main_layout.addWidget(lbl_sel)

        f_row = QHBoxLayout()
        f_row.setSpacing(8)

        self.ent_folder = QLineEdit()
        self.ent_folder.setPlaceholderText("เช่น E:\\Mod_Workspace\\Dishonored_Mod_Workspace...")
        self.ent_folder.textChanged.connect(self._on_folder_changed)
        f_row.addWidget(self.ent_folder, stretch=1)

        btn_browse = QPushButton("📂 เลือกโฟลเดอร์")
        btn_browse.setProperty("class", "BtnSecondary")
        btn_browse.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_browse.clicked.connect(self._browse_folder)
        f_row.addWidget(btn_browse)
        main_layout.addLayout(f_row)

        # 3. Audit Status / Progress
        self.lbl_status = QLabel("")
        self.lbl_status.setStyleSheet("color: #38bdf8; font-size: 11px; font-style: italic;")
        self.lbl_status.setVisible(False)
        main_layout.addWidget(self.lbl_status)

        # 4. Live Audit Result Card
        self.card_audit = QFrame()
        self.card_audit.setStyleSheet("""
            QFrame {
                background-color: rgba(30, 41, 59, 0.7);
                border: 1px solid rgba(56, 189, 248, 0.3);
                border-radius: 8px;
                padding: 10px 12px;
            }
        """)
        ca_layout = QVBoxLayout(self.card_audit)
        ca_layout.setContentsMargins(0, 0, 0, 0)
        ca_layout.setSpacing(8)

        # Title & Engine row
        top_audit_row = QHBoxLayout()
        self.lbl_game_title = QLabel("🎮 ชื่อเกม: กำลังตรวจจับ...")
        self.lbl_game_title.setStyleSheet("color: #f8fafc; font-weight: bold; font-size: 13px;")
        top_audit_row.addWidget(self.lbl_game_title, stretch=1)

        self.lbl_badge = QLabel(" Custom Engine ")
        self.lbl_badge.setStyleSheet("""
            background-color: rgba(16, 20, 30, 220);
            color: #38bdf8;
            border: 1px solid #38bdf8;
            border-radius: 4px;
            padding: 3px 8px;
            font-size: 10px;
            font-weight: bold;
        """)
        top_audit_row.addWidget(self.lbl_badge)
        ca_layout.addLayout(top_audit_row)

        # Progress bar
        pbar_row = QHBoxLayout()
        pbar_row.setSpacing(10)
        self.pbar = QProgressBar()
        self.pbar.setFixedHeight(14)
        self.pbar.setTextVisible(False)
        self.pbar.setStyleSheet("""
            QProgressBar {
                background-color: #1e293b;
                border-radius: 4px;
                border: 1px solid #334155;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10b981, stop:1 #38bdf8);
                border-radius: 4px;
            }
        """)
        pbar_row.addWidget(self.pbar, stretch=1)

        self.lbl_pct = QLabel("0% แปลแล้ว")
        self.lbl_pct.setStyleSheet("color: #10b981; font-weight: bold; font-size: 11px;")
        pbar_row.addWidget(self.lbl_pct)
        ca_layout.addLayout(pbar_row)

        # Breakdown summary
        self.lbl_breakdown = QLabel("กำลังสแกนโครงสร้างและไฟล์ข้อความ...")
        self.lbl_breakdown.setStyleSheet("color: #cbd5e1; font-size: 11px; line-height: 1.4;")
        self.lbl_breakdown.setWordWrap(True)
        ca_layout.addWidget(self.lbl_breakdown)

        self.card_audit.setVisible(False)
        main_layout.addWidget(self.card_audit)

        # 5. Restructuring Options Group
        self.card_opts = QFrame()
        self.card_opts.setStyleSheet("""
            QFrame {
                background-color: rgba(15, 23, 42, 0.6);
                border: 1px solid rgba(148, 163, 184, 0.2);
                border-radius: 8px;
                padding: 10px 12px;
            }
        """)
        co_layout = QVBoxLayout(self.card_opts)
        co_layout.setContentsMargins(0, 0, 0, 0)
        co_layout.setSpacing(6)

        lbl_opt_title = QLabel("⚙️ ตัวเลือกการจัดระเบียบโครงสร้าง (Restructure Options):")
        lbl_opt_title.setStyleSheet("color: #c084fc; font-weight: bold; font-size: 11px;")
        co_layout.addWidget(lbl_opt_title)

        # Mode Radios
        self.btn_grp_mode = QButtonGroup(self)
        self.rad_inplace = QRadioButton("✨ จัดระเบียบในโฟลเดอร์เดิม (In-Place Restructure - สะดวกและเร็วที่สุด)")
        self.rad_inplace.setChecked(True)
        self.btn_grp_mode.addButton(self.rad_inplace)
        co_layout.addWidget(self.rad_inplace)

        self.rad_clone = QRadioButton("📁 คัดลอกและสร้างเป็น Workspace ใหม่ (Clone to New Workspace)")
        self.btn_grp_mode.addButton(self.rad_clone)
        self.rad_clone.toggled.connect(self._on_mode_toggled)
        co_layout.addWidget(self.rad_clone)

        # Clone Target Path Row (visible only when rad_clone is active)
        self.target_row = QWidget()
        tr_layout = QHBoxLayout(self.target_row)
        tr_layout.setContentsMargins(18, 0, 0, 4)
        tr_layout.setSpacing(6)
        self.ent_target = QLineEdit()
        self.ent_target.setPlaceholderText("ระบุโฟลเดอร์ปลายทางใหม่...")
        tr_layout.addWidget(self.ent_target, stretch=1)
        btn_browse_target = QPushButton("📂 เลือก")
        btn_browse_target.setProperty("class", "BtnSecondary")
        btn_browse_target.clicked.connect(self._browse_target)
        tr_layout.addWidget(btn_browse_target)
        self.target_row.setVisible(False)
        co_layout.addWidget(self.target_row)

        # Checkboxes
        self.chk_backup = QCheckBox("🛡️ สร้าง Snapshot Backup โครงสร้างเดิมก่อนจัดระเบียบ (กู้คืนได้เสมอ)")
        self.chk_backup.setChecked(True)
        co_layout.addWidget(self.chk_backup)

        self.chk_templates = QCheckBox("🎨 ติดตั้งเทมเพลต PSD ล่าสุดลง 07_Image_Resources (cover 16-9, Post Facebook, Header)")
        self.chk_templates.setChecked(True)
        co_layout.addWidget(self.chk_templates)

        self.chk_steam_art = QCheckBox("🖼️ ดาวน์โหลดภาพปกและ Official Art จาก Steam อัตโนมัติ")
        self.chk_steam_art.setChecked(True)
        co_layout.addWidget(self.chk_steam_art)

        self.chk_open_ai = QCheckBox("🚀 เปิดหน้าต่าง AI Helper เพื่อเริ่มสานต่องานทันทีเมื่อเสร็จสิ้น")
        self.chk_open_ai.setChecked(True)
        co_layout.addWidget(self.chk_open_ai)

        main_layout.addWidget(self.card_opts)
        main_layout.addStretch()

        # 6. Bottom Action Bar
        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("ยกเลิก")
        btn_cancel.setProperty("class", "BtnSecondary")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_cancel)

        btn_restore = QPushButton("กู้คืนจากสำรอง...")
        btn_restore.setProperty("class", "BtnSecondary")
        btn_restore.clicked.connect(self._restore_backup)
        btn_row.addWidget(btn_restore)

        btn_row.addStretch()

        self.btn_submit = QPushButton("🚀 จัดระเบียบ & เริ่มสานต่องานด้วย AI Helper")
        self.btn_submit.setProperty("class", "BtnAI")
        self.btn_submit.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7c3aed, stop:1 #0284c7);
                color: #ffffff;
                font-weight: bold;
                font-size: 12px;
                border-radius: 6px;
                padding: 8px 18px;
                border: 1px solid rgba(192, 132, 252, 0.4);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #9333ea, stop:1 #0369a1);
            }
            QPushButton:disabled {
                background: #334155;
                color: #64748b;
                border: none;
            }
        """)
        self.btn_submit.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_submit.setEnabled(False)
        self.btn_submit.clicked.connect(self._execute_restructure)
        btn_row.addWidget(self.btn_submit)

        main_layout.addLayout(btn_row)

    def _restore_backup(self):
        manifest_path, selected_filter = QFileDialog.getOpenFileName(
            self, "เลือก snapshot_manifest.json", self.ent_folder.text().strip(), "Backup manifest (snapshot_manifest.json)")
        if not manifest_path:
            return
        def read_manifest():
            import json
            with open(manifest_path, encoding="utf-8") as handle:
                manifest = json.load(handle)
            if not manifest.get("verified"):
                raise ValueError("สำเนาสำรองนี้ยังไม่ผ่านการตรวจสอบ")
            return manifest["source_folder"]
        self.tasks.submit("read-backup", read_manifest,
            lambda source: self._confirm_restore(manifest_path, source), self._on_restructure_error)

    def _confirm_restore(self, manifest_path, source):
        answer = QMessageBox.question(self, "กู้คืนไฟล์เดิม",
            f"กู้คืนไฟล์เดิมลงใน:\n{source}\n\nไฟล์ใหม่ที่เพิ่มหลังสำรองจะยังคงอยู่ ต้องการดำเนินการหรือไม่?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if answer != QMessageBox.StandardButton.Yes:
            return
        from core.project_backup import restore_snapshot
        self.setEnabled(False)
        self.tasks.submit("restore-backup", lambda: restore_snapshot(os.path.dirname(manifest_path)),
                          self._backup_restored, self._on_restructure_error)

    def _backup_restored(self, count):
        self.setEnabled(True)
        QMessageBox.information(self, "กู้คืนสำเร็จ", f"กู้คืนไฟล์เดิมแล้ว {count} ไฟล์")

    def _browse_folder(self):
        d = QFileDialog.getExistingDirectory(self, "เลือกโฟลเดอร์โปรเจกต์ม็อดเดิม", self.ent_folder.text().strip() or r"E:\Mod_Workspace")
        if d:
            self.ent_folder.setText(os.path.normpath(d))

    def _browse_target(self):
        d = QFileDialog.getExistingDirectory(self, "เลือกโฟลเดอร์ปลายทางสำหรับ Workspace ใหม่", self.ent_target.text().strip() or r"E:\Mod_Workspace")
        if d:
            self.ent_target.setText(os.path.normpath(d))

    def _on_folder_changed(self, text):
        path = text.strip()
        if path and os.path.exists(path) and os.path.isdir(path):
            self._start_audit(path)
        else:
            self.card_audit.setVisible(False)
            self.btn_submit.setEnabled(False)
            self.lbl_status.setVisible(False)

    def _on_mode_toggled(self, checked):
        self.target_row.setVisible(checked)
        if checked and not self.ent_target.text().strip():
            src = self.ent_folder.text().strip()
            if src:
                self.ent_target.setText(f"{src}_THub_Restructured")

    def _start_audit(self, folder_path):
        self.lbl_status.setText("🔍 กำลังสแกนและประเมินโครงสร้างไฟล์ม็อดเดิม...")
        self.lbl_status.setVisible(True)
        self.btn_submit.setEnabled(False)

        self.current_audit = None
        self.tasks.submit("audit", lambda: ModAdoptionService.audit_legacy_folder(folder_path),
                          lambda result: self._audit_ready(folder_path, result), self._on_audit_error)

    def _audit_ready(self, folder_path, result):
        if self.ent_folder.text().strip() != folder_path:
            return
        if result.get("success"):
            self._on_audit_success(result)
        else:
            self._on_audit_error(result.get("error", "Audit failed"))

    def _on_audit_success(self, audit):
        self.current_audit = audit
        self.lbl_status.setVisible(False)

        # Update Live Card
        title = audit["game_title"]
        eng_badge = audit["engine_info"]["badge"]
        eng_color = audit["engine_info"].get("badge_color", "#38bdf8")

        self.lbl_game_title.setText(f"🎮 {title}")
        self.lbl_badge.setText(f" {eng_badge} ")
        self.lbl_badge.setStyleSheet(f"""
            background-color: rgba(16, 20, 30, 220);
            color: {eng_color};
            border: 1px solid {eng_color};
            border-radius: 4px;
            padding: 3px 8px;
            font-size: 10px;
            font-weight: bold;
        """)

        stats = audit["stats"]
        pct = stats["progress_pct"]
        self.pbar.setValue(int(pct))
        self.lbl_pct.setText(f"{pct}% แปลแล้ว")

        trans_cnt = stats["translated_count"]
        orig_cnt = stats["original_count"]
        gloss_cnt = stats["glossary_count"]
        font_cnt = stats["font_count"]
        arch_cnt = stats["archive_count"]
        rel_cnt = stats["release_count"]

        type_desc = "ตรวจพบโครงสร้าง THub รุ่นเก่า" if audit.get("is_old_thub") else "ตรวจพบงานม็อดโครงสร้างภายนอก"
        bible_desc = f" | 📖 พบคัมภีร์ตรง: {audit['bible_info']['bible_title']}" if audit.get("bible_info") else ""

        breakdown_text = (
            f"• <b>{type_desc}</b>{bible_desc}<br>"
            f"• <b>ข้อความแปลไทยแล้ว:</b> <font color='#10b981'>{trans_cnt} ไฟล์</font> | "
            f"<b>ข้อความรอแปล:</b> <font color='#38bdf8'>{orig_cnt} ไฟล์</font> | "
            f"<b>คลังคำศัพท์:</b> {gloss_cnt} ไฟล์<br>"
            f"• <b>ฟอนต์ที่พบ:</b> {font_cnt} ไฟล์ | "
            f"<b>แพ็กเกจม็อด/เอาต์พุต:</b> {rel_cnt + arch_cnt} ไฟล์ | "
            f"<b>รวมทั้งหมด:</b> {audit['total_files']} ไฟล์ ({audit['total_size_mb']} MB)"
        )
        self.lbl_breakdown.setText(breakdown_text)
        self.card_audit.setVisible(True)
        self.btn_submit.setEnabled(True)

    def _on_audit_error(self, err_msg):
        self.lbl_status.setText(f"⚠️ สแกนไม่สำเร็จ: {err_msg}")
        self.card_audit.setVisible(False)
        self.btn_submit.setEnabled(False)

    def _execute_restructure(self):
        if not self.current_audit:
            return

        folder = self.ent_folder.text().strip()
        in_place = self.rad_inplace.isChecked()
        target = self.ent_target.text().strip() if not in_place else folder

        if not in_place and not target:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณาระบุโฟลเดอร์ปลายทางสำหรับ Workspace ใหม่")
            return

        options = {
            "in_place": in_place,
            "target_path": target,
            "safe_backup": self.chk_backup.isChecked(),
            "copy_mode": not in_place,
            "deploy_templates": self.chk_templates.isChecked(),
            "download_steam_art": self.chk_steam_art.isChecked(),
            "game_title": self.current_audit["game_title"],
            "engine": self.current_audit["engine_info"]["badge"]
        }

        self.btn_submit.setEnabled(False)
        self.btn_submit.setText("⏳ กำลังจัดระเบียบโครงสร้าง...")

        self.setEnabled(False)
        self.tasks.submit("restructure", lambda: ModAdoptionService.execute_adoption_restructure(folder, options),
                          self._restructure_ready, self._on_restructure_error)

    def _restructure_ready(self, result):
        self.setEnabled(True)
        if result.get("success"):
            self._on_restructure_success(result)
        else:
            recovery = result.get("snapshot_path") or "ไม่มีสำเนาสำรอง"
            self._on_restructure_error(result.get("error", "Failed") + "\nสำรอง: " + recovery)

    def _on_restructure_success(self, res):
        open_ai = self.chk_open_ai.isChecked()
        proj = res.get("project_entry", {})
        
        QMessageBox.information(
            self,
            "จัดระเบียบสำเร็จ",
            f"✅ จัดระเบียบและนำเข้าโปรเจกต์ม็อดสำเร็จ!\n\n"
            f"🎮 เกม: {res.get('game_title')}\n"
            f"📁 โฟลเดอร์: {res.get('target_path')}\n"
            f"⚙️ เอนจิ้น: {res.get('engine')}\n\n"
            f"ระบบสร้างไฟล์พิมพ์เขียว AI_Mod_Continuation_Blueprint.md\n"
            f"และจัดเข้าโฟลเดอร์มาตรฐาน 01–07 เรียบร้อยแล้ว!"
        )

        self.adoption_completed.emit(proj, open_ai)
        self.accept()

    def _on_restructure_error(self, err_msg):
        self.setEnabled(True)
        self.btn_submit.setEnabled(True)
        self.btn_submit.setText("🚀 จัดระเบียบ & เริ่มสานต่องานด้วย AI Helper")
        QMessageBox.critical(self, "ข้อผิดพลาด", f"ไม่สามารถจัดระเบียบโปรเจกต์ได้:\n{err_msg}")
