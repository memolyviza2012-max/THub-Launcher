"""
TStudio Modular Dialogs:
- MergeTranslatedDialog: Merges translated CSV files into base files
- FindReplaceDialog: Fast find & replace dialog with ID filter
- MilitaryTerminologyRetrofitDialog: Zero-Token Military/Sci-Fi terminology retrofit
- GlossarySweeperDialog: Audits and sweeps common words & dead terms from glossaries
- ShortcutsCheatsheetDialog: Interactive keyboard shortcut cheatsheet
"""
import os
import sys
_core_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Core'))
if _core_dir not in sys.path:
    sys.path.append(_core_dir)
import re
import json
import csv
import copy

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QGroupBox, QHBoxLayout, QPushButton, QLineEdit,
    QMessageBox, QApplication, QFileDialog, QFormLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QCheckBox, QRadioButton, QComboBox,
    QLabel, QScrollArea, QTabWidget, QWidget, QGridLayout, QSplitter
)
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QColor, QFont, QCursor

from tstudio_i18n import _
from tstudio_core import TStudioCore, CoreAI
try:
    from tstudio_tlm_studio import is_common_generic_english_word, is_engine_markup_tag, RE_VOCAL_SOUNDS
except Exception:
    RE_VOCAL_SOUNDS = re.compile(r'^(?:[Uu]h+|[Aa]h+|[Oo]h+|[Hh]m+|[Hh]uh+|[Ww]ow|[Yy]eah?|[Nn]ope?|[Hh]ey|[Oo]uch|[Uu]gh|[Gg]asp|[Ss]igh|[Gg]roan|[Ss]ob|[Ll]augh)', re.IGNORECASE)
    def is_common_generic_english_word(w, tag=None, from_lore=False): return False
    def is_engine_markup_tag(w): return False

class MergeTranslatedDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("merge_translated_title"))
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        # Original File
        group_orig = QGroupBox(_("original_file_group"))
        layout_orig = QHBoxLayout()
        self.txt_orig = QLineEdit()
        self.txt_orig.setPlaceholderText("Select original English file (Bundle, Locres, CSV)...")
        self.txt_orig.setReadOnly(True)
        btn_orig = QPushButton(_("browse_btn"))
        btn_orig.setToolTip(_("tooltip_btn_orig"))
        btn_orig.clicked.connect(self.browse_orig)
        layout_orig.addWidget(self.txt_orig)
        layout_orig.addWidget(btn_orig)
        group_orig.setLayout(layout_orig)
        layout.addWidget(group_orig)
        
        # Translated File
        group_trans = QGroupBox(_("translated_file_group"))
        layout_trans = QHBoxLayout()
        self.txt_trans = QLineEdit()
        self.txt_trans.setPlaceholderText("Select partially translated file (Bundle, Locres, CSV)...")
        self.txt_trans.setReadOnly(True)
        btn_trans = QPushButton(_("browse_btn"))
        btn_trans.setToolTip(_("tooltip_btn_trans"))
        btn_trans.clicked.connect(self.browse_trans)
        layout_trans.addWidget(self.txt_trans)
        layout_trans.addWidget(btn_trans)
        group_trans.setLayout(layout_trans)
        layout.addWidget(group_trans)
        
        # Save File
        group_save = QGroupBox(_("save_file_group"))
        layout_save = QHBoxLayout()
        self.txt_save = QLineEdit()
        self.txt_save.setPlaceholderText("Select output CSV path to continue working...")
        self.txt_save.setReadOnly(True)
        btn_save = QPushButton(_("browse_btn"))
        btn_save.setToolTip(_("tooltip_btn_save"))
        btn_save.clicked.connect(self.browse_save)
        layout_save.addWidget(self.txt_save)
        layout_save.addWidget(btn_save)
        group_save.setLayout(layout_save)
        layout.addWidget(group_save)
        
        # Execute
        self.btn_execute = QPushButton(_("merge_execute_btn"))
        self.btn_execute.setToolTip(_("tooltip_btn_execute"))
        self.btn_execute.setStyleSheet("background: #cba6f7; color: #1e1e2e; font-weight: bold; font-size: 14px; padding: 8px;")
        self.btn_execute.clicked.connect(self.execute_merge)
        layout.addWidget(self.btn_execute)
        
        self.merged_csv_path = None
        
    def browse_orig(self):
        path, file_ext = QFileDialog.getOpenFileName(self, "Select Original File", "", "Supported Files (*.csv *.lor *.locres *.tex *.bundle *.txt *.json)")
        if path: self.txt_orig.setText(path)
            
    def browse_trans(self):
        path, file_ext = QFileDialog.getOpenFileName(self, "Select Translated File", "", "Supported Files (*.csv *.lor *.locres *.tex *.bundle *.txt *.json)")
        if path: self.txt_trans.setText(path)
            
    def browse_save(self):
        path, file_ext = QFileDialog.getSaveFileName(self, "Select Output CSV", "", "CSV Files (*.csv)")
        if path: self.txt_save.setText(path)
            
    def execute_merge(self):
        orig_path = self.txt_orig.text()
        trans_path = self.txt_trans.text()
        save_path = self.txt_save.text()
        
        if not orig_path or not trans_path or not save_path:
            QMessageBox.warning(self, _("input_required_title"), _("input_required_msg"))
            return
            
        try:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            
            def ensure_csv(path):
                if path.lower().endswith('.csv'): 
                    return path
                from tbundle_manager import TBundleManager
                if TBundleManager.is_unity_bundle(path):
                    return TBundleManager.extract_text_to_csv(path)
                return file_converter.auto_convert_to_csv(path, None)
                
            orig_csv = ensure_csv(orig_path)
            trans_csv = ensure_csv(trans_path)
            
            if not orig_csv or not trans_csv or not os.path.exists(orig_csv) or not os.path.exists(trans_csv):
                raise Exception("Failed to extract one of the files to CSV.")
                
            # --- Step 1: Read translated CSV into memory (BEFORE any file write) ---
            # This prevents truncation if save_path == trans_csv or save_path == orig_csv
            trans_dict = {}
            with open(trans_csv, 'r', encoding='utf-8-sig', errors='ignore') as f:
                reader = csv.reader(f)
                next(reader, None)  # skip header
                for row in reader:
                    if len(row) >= 2:
                        t_id = row[0]
                        if len(row) >= 3:
                            # TStudio format: ID, Source, Trans, AI_Ref → use col 2 (Trans)
                            t_text = row[2]
                            t_src = row[1]
                            final_t = t_text if t_text.strip() else t_src
                        else:
                            # 2-column format (ID, Trans) from external tools
                            final_t = row[1]
                        trans_dict[t_id] = final_t

            # --- Step 2: Read orig CSV rows into memory (BEFORE any file write) ---
            orig_rows = []
            with open(orig_csv, 'r', encoding='utf-8-sig', errors='ignore') as f_in:
                reader = csv.reader(f_in)
                next(reader, None)  # skip header
                for row in reader:
                    orig_rows.append(row)

            # --- Step 3: Write to temp file, then move to save_path (Safe Save) ---
            import tempfile
            tmp_fd, tmp_path = tempfile.mkstemp(suffix='.csv', dir=os.path.dirname(save_path))
            merged_count = 0
            try:
                with os.fdopen(tmp_fd, 'w', encoding='utf-8-sig', newline='') as f_out:
                    writer = csv.writer(f_out)
                    writer.writerow([_("col_id"), _("col_source"), _("col_translation"), 'AI Reference'])

                    for row in orig_rows:
                        if len(row) >= 2:
                            o_id = row[0]
                            o_src = row[1]
                            trans_val = ""

                            if o_id in trans_dict:
                                t_val = trans_dict[o_id]
                                # Accept if it differs from source OR contains Thai
                                if t_val != o_src or re.search(r'[ก-๙เแไใโ]', t_val):
                                    trans_val = t_val
                                    merged_count += 1

                            writer.writerow([o_id, o_src, trans_val, trans_val])

                shutil.move(tmp_path, save_path)
            except Exception:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
                raise
                        
            self.merged_csv_path = save_path
            QApplication.restoreOverrideCursor()
            QMessageBox.information(self, _("merge_complete_title"), f"Successfully merged {merged_count} translated entries!\nThe file is ready to use.")
            self.accept()
            
        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, _("error_title"), f"An error occurred during merge:\n{e}")


class FindReplaceDialog(QDialog):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.mw = main_window
        self.setWindowTitle(_("find_replace_title"))
        self.setFixedSize(450, 240)
        vbox = QVBoxLayout(self)
        layout = QFormLayout()
        self.txt_find = QLineEdit()
        self.txt_replace = QLineEdit()
        self.txt_id_filter = QLineEdit()
        self.txt_id_filter.setPlaceholderText("e.g. charmsg_sebastian (Leave blank for all)")
        
        layout.addRow("ID Filter:", self.txt_id_filter)
        layout.addRow(_("find_label"), self.txt_find)
        layout.addRow(_("replace_with_label"), self.txt_replace)
        vbox.addLayout(layout)

        # Options Row
        opts_row = QHBoxLayout()
        self.chk_match_case = QCheckBox("Aa ตรงตัวพิมพ์ (Case)")
        self.chk_whole_word = QCheckBox("W ตรงทั้งคำ (Whole Word)")
        self.chk_exact = QCheckBox("= ตรงทั้งประโยค (Exact)")
        opts_row.addWidget(self.chk_match_case)
        opts_row.addWidget(self.chk_whole_word)
        opts_row.addWidget(self.chk_exact)
        vbox.addLayout(opts_row)
        
        btn = QPushButton(_("replace_all_btn"))
        btn.setToolTip(_("tooltip_btn"))
        btn.clicked.connect(self.replace_all)
        btn.setStyleSheet("background: #f38ba8; color: #1e1e2e; font-weight: bold; padding: 6px; border-radius: 4px;")
        vbox.addWidget(btn)

    def replace_all(self):
        find_txt = self.txt_find.text()
        rep_txt = self.txt_replace.text()
        id_filter = self.txt_id_filter.text().strip()
        match_case = self.chk_match_case.isChecked()
        whole_word = self.chk_whole_word.isChecked()
        exact_match = self.chk_exact.isChecked()
        
        if not find_txt: return
        model = self.mw.model
        count = 0
        model.beginResetModel()
        for item in model._data:
            # Check ID Filter first
            if id_filter and id_filter.lower() not in str(item.get("id", "")).lower():
                continue
                
            cur_trans = str(item.get("trans") or "")
            if not cur_trans:
                continue

            if exact_match:
                c_norm = unicodedata.normalize('NFC', cur_trans).strip(' \t\r\n\u200b\u00a0\ufeff')
                f_norm = unicodedata.normalize('NFC', find_txt).strip(' \t\r\n\u200b\u00a0\ufeff')
                is_match = (c_norm == f_norm) if match_case else (c_norm.lower() == f_norm.lower())
                if is_match:
                    item["trans"] = rep_txt
                    count += 1
            elif whole_word:
                pat_regex = build_search_boundary_regex(find_txt, match_case)
                if pat_regex and pat_regex.search(cur_trans):
                    item["trans"] = pat_regex.sub(rep_txt, cur_trans)
                    count += 1
            else:
                if match_case:
                    if find_txt in cur_trans:
                        item["trans"] = cur_trans.replace(find_txt, rep_txt)
                        count += 1
                else:
                    pat = re.escape(find_txt)
                    if re.search(pat, cur_trans, re.IGNORECASE):
                        item["trans"] = re.sub(pat, rep_txt, cur_trans, flags=re.IGNORECASE)
                        count += 1

        model.endResetModel()
        if count > 0:
            row = self.mw.current_source_row
            if 0 <= row < len(model._data):
                self.mw.txt_trans.blockSignals(True)
                self.mw.txt_trans.setPlainText(model._data[row]["trans"])
                self.mw.txt_trans.blockSignals(False)
            self.mw.statusBar().showMessage(f'Replaced {count} instances. Ctrl+S to save.', 5000)
            QMessageBox.information(self, _("success_title"), _("replaced_count_msg"))
        else:
            QMessageBox.information(self, _("not_found_title"), _("no_matches_msg"))


class MilitaryTerminologyRetrofitDialog(QDialog):
    """
    Zero-Token Military, Sci-Fi & Futuristic Weapon Nomenclature Retrofit Studio.
    Supports:
    1. Dynamic Alphanumeric Model Codes (X-99, V-77, ARC-9, Mk.IV, Type-88, AR-23, etc.)
    2. Sci-Fi & Futuristic Weapons / Vehicles (Railgun, Plasma, Pulse, Ion, Gauss, Bolter, Dropship, Mecha, Exosuit)
    3. Real-world Military Firearms, Vehicles, Calibers, Acronyms (M16, AK-47, SMG, APC, Humvee)
    4. In-file Entity Discovery (scans current file for game-specific weapon names with 1-click rule generation)
    5. Custom Rules Manager with Game Presets (save/load JSON presets like Cyberpunk, Helldivers, Warhammer)
    6. In-place Editable Preview Table (double-click to fine-tune before applying)
    """
    def __init__(self, main_window):
        super().__init__(main_window)
        self.mw = main_window
        self.setWindowTitle("🎖️ ศูนย์ซ่อมศัพท์อาวุธ โลกอนาคต/ไซไฟ และยุทโธปกรณ์ (Terminology Retrofit Studio - 0 Token)")
        self.resize(1040, 740)
        self.setStyleSheet("""
            QDialog { background-color: #1e1e2e; color: #cdd6f4; font-family: 'Segoe UI', Tahoma, sans-serif; }
            QTabWidget::pane { border: 1px solid #45475a; background: #1e1e2e; border-radius: 6px; }
            QTabBar::tab { background: #181825; color: #a6adc8; padding: 8px 18px; border-top-left-radius: 6px; border-top-right-radius: 6px; margin-right: 2px; font-weight: bold; }
            QTabBar::tab:selected { background: #313244; color: #89b4fa; border-bottom: 2px solid #89b4fa; }
            QGroupBox { border: 1px solid #45475a; border-radius: 6px; margin-top: 10px; font-weight: bold; color: #89b4fa; padding-top: 10px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }
            QTableWidget { background-color: #181825; color: #cdd6f4; gridline-color: #313244; border: 1px solid #45475a; border-radius: 4px; }
            QHeaderView::section { background-color: #313244; color: #cdd6f4; font-weight: bold; padding: 5px; border: 1px solid #45475a; }
            QCheckBox, QRadioButton { color: #cdd6f4; spacing: 6px; }
            QPushButton { font-weight: bold; border-radius: 4px; padding: 6px 12px; }
            QLineEdit, QComboBox { background-color: #181825; color: #cdd6f4; border: 1px solid #45475a; border-radius: 4px; padding: 4px 8px; }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Tab Widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self._pending_repairs = []
        self._discovered_entities = []

        # Load custom rules from active profile
        from tstudio_core import TStudioCore
        prof_name = getattr(self.mw, 'current_profile_name', "Default")
        prof = TStudioCore.get_current_profile_data(prof_name)
        self.custom_rules = prof.get("retrofit_custom_rules", [])

        # Build 3 Tabs
        self._init_auto_retrofit_tab()
        self._init_discovery_tab()
        self._init_custom_rules_tab()

        # Bottom Bar
        bot_bar = QHBoxLayout()
        self.lbl_global_hint = QLabel("💡 เคล็ดลับ: ระบบใช้ตรรกะเทียบเคียงข้อความต้นฉบับ ปลอดภัย 100% และใช้ 0 API Tokens!")
        self.lbl_global_hint.setStyleSheet("color: #6c7086; font-size: 11px;")
        btn_close = QPushButton("ปิดหน้าต่าง")
        btn_close.setStyleSheet("background: #313244; color: #cdd6f4; padding: 6px 16px;")
        btn_close.clicked.connect(self.reject)

        bot_bar.addWidget(self.lbl_global_hint)
        bot_bar.addStretch()
        bot_bar.addWidget(btn_close)
        layout.addLayout(bot_bar)

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 1: AUTO RETROFIT & PREVIEW
    # ══════════════════════════════════════════════════════════════════════════
    def _init_auto_retrofit_tab(self):
        tab = QWidget()
        vbox = QVBoxLayout(tab)
        vbox.setSpacing(8)

        # Header description
        header_box = QFrame()
        header_box.setStyleSheet("background: #181825; border: 1px solid #313244; border-radius: 6px; padding: 8px;")
        h_layout = QVBoxLayout(header_box)
        h_title = QLabel("🎖️ ระบบสแกนและซ่อมแซมคำศัพท์อาวุธ โลกอนาคต/ไซไฟ และยานพาหนะ (Zero-Token Cost)")
        h_title.setStyleSheet("font-size: 13px; font-weight: bold; color: #a6e3a1;")
        h_desc = QLabel(
            "ตรวจจับและกู้คืนคำศัพท์ที่ AI เคยแปลผิดธรรมชาติในไฟล์เดิม โดยไม่ต้องแปลใหม่ (ใช้ 0 API Tokens!):\n"
            "• 🔮 รหัสโมเดลโลกอนาคต: 'เอ็กซ์ 99' ➔ 'X-99', 'วี 77' ➔ 'V-77', 'มาร์ก 4' ➔ 'Mk.IV', 'เออาร์ 23' ➔ 'AR-23'\n"
            "• 🚀 อาวุธ/ยานเกราะไซไฟ: 'ปืนราง' ➔ 'ปืนเรลกัน', 'ปืนไรเฟิลชีพจร' ➔ 'พัลส์ไรเฟิล', 'ปืนสลักเกลียว' ➔ 'โบลเตอร์', 'เรือทิ้ง' ➔ 'ยานดรอปชิป'\n"
            "• 🔫 ปืนโลกจริง & ยานเกราะ: 'เอ็ม 16' ➔ 'M16', 'เอสเอ็มจี' / 'ปืนกลเบา' ➔ 'SMG', 'ฮัมวี' ➔ 'รถ Humvee', 'เอพีซี' ➔ 'รถเกราะ APC'\n"
            "💡 ปลอดภัย 100%: ตรวจสอบเทียบกับข้อความภาษาอังกฤษต้นฉบับเสมอ และคุณสามารถดับเบิลคลิกแก้ไขผลลัพธ์ในตารางพรีวิวก่อนบันทึกได้"
        )
        h_desc.setStyleSheet("color: #a6adc8; font-size: 11px; line-height: 1.3;")
        h_layout.addWidget(h_title)
        h_layout.addWidget(h_desc)
        vbox.addWidget(header_box)

        # Options & Scope
        opts_layout = QHBoxLayout()

        grp_rules = QGroupBox("รายการหมวดหมู่ที่ต้องการตรวจสอบและซ่อมแซม")
        v_rules = QVBoxLayout(grp_rules)
        self.chk_model_codes = QCheckBox("🔮 รหัสรุ่นและโมเดลสากล/โลกอนาคต (Dynamic Codes: X-99, V-77, ARC-9, Mk.IV, Type-88, AR-23 ฯลฯ)")
        self.chk_model_codes.setChecked(True)
        self.chk_scifi = QCheckBox("🚀 อาวุธและยานเกราะโลกอนาคต & ไซไฟ (Railgun, Plasma, Pulse, Ion, Gauss, Bolter, Dropship, Mecha ฯลฯ)")
        self.chk_scifi.setChecked(True)
        self.chk_weapons = QCheckBox("🔫 อาวุธปืนและโมเดลสงครามจริง (M16, AK-47, M4A1, MP5, RPG-7, Glock ฯลฯ)")
        self.chk_weapons.setChecked(True)
        self.chk_acronyms = QCheckBox("💥 ตัวย่อคลาสอาวุธ ('ปืนกลเบา' ➔ 'SMG', LMG, DMR, AR)")
        self.chk_acronyms.setChecked(True)
        self.chk_vehicles = QCheckBox("🛡️ ยานพาหนะและยานเกราะ ('รถ Humvee', 'รถเกราะ APC', 'รถถังพิฆาต', 'กันชิป')")
        self.chk_vehicles.setChecked(True)
        self.chk_calibers = QCheckBox("🎯 ขนาดกระสุนและพลังงาน ('9mm', '5.56mm', '7.62mm', '.50 cal')")
        self.chk_calibers.setChecked(True)
        self.chk_keys = QCheckBox("⌨️ ปุ่มคีย์บอร์ด & คอนโทรลเลอร์ (Spacebar ไม่ใช่ สเปคบรา, Enter ไม่ใช่ เอ็นเทอ/ป้อน, Shift, Ctrl, Esc ฯลฯ)")
        self.chk_keys.setChecked(True)
        self.chk_glossary = QCheckBox("📖 ปรับใช้คำศัพท์จาก Project Glossary ร่วมด้วย")
        self.chk_glossary.setChecked(True)
        self.chk_custom = QCheckBox("⚙️ ใช้งานกฎที่คุณกำหนดเอง (Custom Rules) ร่วมด้วย")
        self.chk_custom.setChecked(True)

        v_rules.addWidget(self.chk_model_codes)
        v_rules.addWidget(self.chk_scifi)
        v_rules.addWidget(self.chk_weapons)
        v_rules.addWidget(self.chk_acronyms)
        v_rules.addWidget(self.chk_vehicles)
        v_rules.addWidget(self.chk_calibers)
        v_rules.addWidget(self.chk_keys)
        v_rules.addWidget(self.chk_glossary)
        v_rules.addWidget(self.chk_custom)
        opts_layout.addWidget(grp_rules, 3)

        grp_scope = QGroupBox("ขอบเขตการทำงาน (Scope)")
        v_scope = QVBoxLayout(grp_scope)
        self.rad_all = QRadioButton("🌐 สแกนทั้งไฟล์ (ทุกแถว)")
        self.rad_all.setChecked(True)
        selected_count = len(self.mw._get_selected_source_rows()) if hasattr(self.mw, '_get_selected_source_rows') else 0
        self.rad_selected = QRadioButton(f"🎯 เฉพาะแถวที่เลือก ({selected_count} แถว)")
        if selected_count == 0:
            self.rad_selected.setEnabled(False)
        else:
            self.rad_selected.setChecked(True)
        v_scope.addWidget(self.rad_all)
        v_scope.addWidget(self.rad_selected)
        v_scope.addStretch()
        opts_layout.addWidget(grp_scope, 2)

        vbox.addLayout(opts_layout)

        # Action Buttons
        btn_bar = QHBoxLayout()
        self.btn_scan = QPushButton("🔍 1. สแกนและแสดงตัวอย่าง (Preview)")
        self.btn_scan.setStyleSheet("background: #89b4fa; color: #1e1e2e; padding: 8px 16px; font-size: 12px;")
        self.btn_scan.clicked.connect(self.scan_and_preview)

        self.lbl_status = QLabel("พร้อมสแกน (กดปุ่มเพื่อดูตัวอย่างจุดที่ตรวจพบ)")
        self.lbl_status.setStyleSheet("color: #fab387; font-weight: bold; font-size: 12px;")

        btn_bar.addWidget(self.btn_scan)
        btn_bar.addWidget(self.lbl_status, 1)
        vbox.addLayout(btn_bar)

        # Preview Table
        self.tbl_preview = QTableWidget()
        self.tbl_preview.setColumnCount(5)
        self.tbl_preview.setHorizontalHeaderLabels([
            "แถว", "ID", "ข้อความต้นฉบับ (Source)", "คำแปลเดิม (Original Thai)", "คำแปลที่ซ่อมแซมแล้ว (Repaired - ดับเบิลคลิกเพื่อแก้คำได้)"
        ])
        self.tbl_preview.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_preview.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_preview.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.tbl_preview.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        self.tbl_preview.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.tbl_preview.setColumnWidth(2, 230)
        self.tbl_preview.setColumnWidth(3, 230)
        self.tbl_preview.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        vbox.addWidget(self.tbl_preview, 1)

        # Bottom Apply Button
        act_box = QHBoxLayout()
        self.btn_apply = QPushButton("✅ 2. ยืนยันบันทึกการแก้ไขลงในตาราง (Apply Changes)")
        self.btn_apply.setStyleSheet("background: #a6e3a1; color: #1e1e2e; padding: 8px 20px; font-size: 13px;")
        self.btn_apply.setEnabled(False)
        self.btn_apply.clicked.connect(self.apply_changes)

        act_box.addStretch()
        act_box.addWidget(self.btn_apply)
        vbox.addLayout(act_box)

        self.tabs.addTab(tab, "🎖️ 1. ซ่อมแซมอัตโนมัติ (Auto-Retrofit)")

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 2: FILE ENTITY DISCOVERY
    # ══════════════════════════════════════════════════════════════════════════
    def _init_discovery_tab(self):
        tab = QWidget()
        vbox = QVBoxLayout(tab)
        vbox.setSpacing(8)

        # Header description
        header_box = QFrame()
        header_box.setStyleSheet("background: #181825; border: 1px solid #313244; border-radius: 6px; padding: 8px;")
        h_layout = QVBoxLayout(header_box)
        h_title = QLabel("🔬 สแกนค้นพบคำศัพท์เฉพาะในเกมนี้ (File Entity Discovery & 1-Click Fix)")
        h_title.setStyleSheet("font-size: 13px; font-weight: bold; color: #89dceb;")
        h_desc = QLabel(
            "สำหรับเกมที่มีปืนโลกอนาคต ไซไฟ แฟนตาซี หรือรหัสรุ่นที่ไม่มีในโลกความจริง:\n"
            "ระบบจะสแกนคอลัมน์ภาษาอังกฤษทั้งหมดในไฟล์ปัจจุบัน เพื่อตรวจหาชื่ออาวุธ ยานพาหนะ และรหัสรุ่นเฉพาะเกมนี้\n"
            "คุณสามารถเลือกคำที่พบ แล้วสร้างกฎแทนที่ หรือสั่งนำไปใช้กับไฟล์ได้ทันทีในคลิกเดียว!"
        )
        h_desc.setStyleSheet("color: #a6adc8; font-size: 11px; line-height: 1.3;")
        h_layout.addWidget(h_title)
        h_layout.addWidget(h_desc)
        vbox.addWidget(header_box)

        # Action Bar
        top_bar = QHBoxLayout()
        btn_disc = QPushButton("🔎 สแกนค้นหาชื่ออาวุธ/ยานพาหนะ/รหัสรุ่นในไฟล์นี้")
        btn_disc.setStyleSheet("background: #89dceb; color: #1e1e2e; padding: 7px 14px; font-size: 12px;")
        btn_disc.clicked.connect(self.discover_entities)

        self.lbl_disc_status = QLabel("กดปุ่มเพื่อเริ่มค้นหาคำศัพท์เฉพาะจากไฟล์ที่เปิดอยู่")
        self.lbl_disc_status.setStyleSheet("color: #fab387; font-weight: bold; font-size: 12px;")

        top_bar.addWidget(btn_disc)
        top_bar.addWidget(self.lbl_disc_status, 1)
        vbox.addLayout(top_bar)

        # Discovery Table
        self.tbl_discovery = QTableWidget()
        self.tbl_discovery.setColumnCount(4)
        self.tbl_discovery.setHorizontalHeaderLabels([
            "คำศัพท์ในต้นฉบับ (Source Term)", "พบ (ครั้ง)", "ตัวอย่างประโยคต้นฉบับ (Source)", "ตัวอย่างคำแปลปัจจุบัน (Current Thai)"
        ])
        self.tbl_discovery.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.tbl_discovery.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_discovery.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.tbl_discovery.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.tbl_discovery.setColumnWidth(0, 180)
        self.tbl_discovery.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tbl_discovery.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tbl_discovery.itemSelectionChanged.connect(self.on_discovery_row_selected)
        vbox.addWidget(self.tbl_discovery, 1)

        # Quick Rule Creator Panel
        grp_creator = QGroupBox("➕ สร้างกฎแก้ไขจากคำที่เลือกในตาราง")
        f_layout = QVBoxLayout(grp_creator)

        row1 = QHBoxLayout()
        lbl_s = QLabel("คำในต้นฉบับ (Source):")
        lbl_s.setFixedWidth(130)
        self.txt_disc_src = QLineEdit()
        self.txt_disc_src.setPlaceholderText("เช่น Plasma Rifle X-99, ARC-9, Dreadnought")

        lbl_o = QLabel("คำไทยเดิมที่แปลผิด:")
        lbl_o.setFixedWidth(130)
        self.txt_disc_orig = QLineEdit()
        self.txt_disc_orig.setPlaceholderText("คำหรือทับศัพท์เดิมที่ต้องการแทนที่ เช่น ปืนไรเฟิลพลาสมา เอ็กซ์-99")

        row1.addWidget(lbl_s)
        row1.addWidget(self.txt_disc_src, 1)
        row1.addWidget(lbl_o)
        row1.addWidget(self.txt_disc_orig, 1)
        f_layout.addLayout(row1)

        row2 = QHBoxLayout()
        lbl_r = QLabel("คำแปลใหม่ที่ต้องการ:")
        lbl_r.setFixedWidth(130)
        self.txt_disc_rep = QLineEdit()
        self.txt_disc_rep.setPlaceholderText("คำแปลหรือคงภาษาอังกฤษที่ต้องการ เช่น ปืนพลาสมาไรเฟิล X-99, ARC-9")

        btn_add_rule = QPushButton("➕ เพิ่มลงในกฎกำหนดเอง")
        btn_add_rule.setStyleSheet("background: #cba6f7; color: #1e1e2e; padding: 6px 14px;")
        btn_add_rule.clicked.connect(self.add_discovered_to_custom)

        btn_apply_now = QPushButton("🚀 นำกฎนี้ไปใช้กับไฟล์ทันที")
        btn_apply_now.setStyleSheet("background: #a6e3a1; color: #1e1e2e; padding: 6px 16px;")
        btn_apply_now.clicked.connect(self.apply_discovered_rule_now)

        row2.addWidget(lbl_r)
        row2.addWidget(self.txt_disc_rep, 1)
        row2.addWidget(btn_add_rule)
        row2.addWidget(btn_apply_now)
        f_layout.addLayout(row2)

        vbox.addWidget(grp_creator)
        self.tabs.addTab(tab, "🔬 2. ค้นหาศัพท์เฉพาะในเกมนี้ (Discovery)")

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 3: CUSTOM RULES & GAME PRESETS
    # ══════════════════════════════════════════════════════════════════════════
    def _init_custom_rules_tab(self):
        tab = QWidget()
        vbox = QVBoxLayout(tab)
        vbox.setSpacing(8)

        # Header description
        header_box = QFrame()
        header_box.setStyleSheet("background: #181825; border: 1px solid #313244; border-radius: 6px; padding: 8px;")
        h_layout = QVBoxLayout(header_box)
        h_title = QLabel("⚙️ กฎที่คุณกำหนดเองและพรีเซ็ต (Custom Game Rules & Presets)")
        h_title.setStyleSheet("font-size: 13px; font-weight: bold; color: #f9e2af;")
        h_desc = QLabel(
            "กำหนดกฎเฉพาะเกมสำหรับโปรเจกต์นี้ คุณสามารถบันทึกหรือส่งออกเป็นไฟล์ Preset (.json)\n"
            "เพื่อนำไปแจกจ่ายให้ทีมงาน หรือนำกลับมาโหลดใช้ใหม่ในโปรเจกต์อื่นๆ ได้อย่างสะดวกสบาย"
        )
        h_desc.setStyleSheet("color: #a6adc8; font-size: 11px; line-height: 1.3;")
        h_layout.addWidget(h_title)
        h_layout.addWidget(h_desc)
        vbox.addWidget(header_box)

        # Presets Bar
        preset_bar = QHBoxLayout()
        lbl_p = QLabel("🎮 พรีเซ็ตสำเร็จรูป:")
        self.cmb_templates = QComboBox()
        self.cmb_templates.addItem("-- เลือกโหลดตัวอย่าง Preset สำเร็จรูป --")
        self.cmb_templates.addItem("🎮 ตัวอย่าง: Sci-Fi & Cyberpunk 2077")
        self.cmb_templates.addItem("🎮 ตัวอย่าง: Helldivers 2 Arsenal")
        self.cmb_templates.addItem("🎮 ตัวอย่าง: Warhammer 40k & Space Marine")
        self.cmb_templates.currentIndexChanged.connect(self.load_template_preset)

        btn_load_p = QPushButton("📂 โหลด Preset (.json)")
        btn_load_p.setStyleSheet("background: #89b4fa; color: #1e1e2e;")
        btn_load_p.clicked.connect(self.load_preset_file)

        btn_save_p = QPushButton("💾 บันทึกเป็น Preset (.json)")
        btn_save_p.setStyleSheet("background: #a6adc8; color: #1e1e2e;")
        btn_save_p.clicked.connect(self.save_preset_file)

        preset_bar.addWidget(lbl_p)
        preset_bar.addWidget(self.cmb_templates, 1)
        preset_bar.addWidget(btn_load_p)
        preset_bar.addWidget(btn_save_p)
        vbox.addLayout(preset_bar)

        # Custom Rules Table
        self.tbl_custom_rules = QTableWidget()
        self.tbl_custom_rules.setColumnCount(4)
        self.tbl_custom_rules.setHorizontalHeaderLabels([
            "คำในต้นฉบับ (Source Keyword)", "คำไทยเดิมที่แปลผิด (Target Thai)", "คำแปลใหม่ที่ต้องการ (Replacement)", "คำอธิบาย (Description)"
        ])
        self.tbl_custom_rules.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.tbl_custom_rules.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.tbl_custom_rules.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.tbl_custom_rules.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.tbl_custom_rules.setColumnWidth(0, 180)
        self.tbl_custom_rules.setColumnWidth(1, 180)
        self.tbl_custom_rules.setColumnWidth(2, 180)
        self.tbl_custom_rules.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        vbox.addWidget(self.tbl_custom_rules, 1)

        # Add Rule Form
        grp_add = QGroupBox("➕ เพิ่มกฎกำหนดเองใหม่")
        add_layout = QVBoxLayout(grp_add)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("คำในต้นฉบับ:"))
        self.txt_c_src = QLineEdit()
        self.txt_c_src.setPlaceholderText("เช่น Railgun, Doomhammer, Lasgun")
        r1.addWidget(self.txt_c_src, 1)

        r1.addWidget(QLabel("คำไทยเดิม:"))
        self.txt_c_trans = QLineEdit()
        self.txt_c_trans.setPlaceholderText("คำที่ AI แปลทับศัพท์หรือแปลตรงตัวผิด")
        r1.addWidget(self.txt_c_trans, 1)
        add_layout.addLayout(r1)

        r2 = QHBoxLayout()
        r2.addWidget(QLabel("คำแปลใหม่:"))
        self.txt_c_rep = QLineEdit()
        self.txt_c_rep.setPlaceholderText("คำที่ต้องการให้เปลี่ยนเป็น")
        r2.addWidget(self.txt_c_rep, 1)

        r2.addWidget(QLabel("คำอธิบาย:"))
        self.txt_c_desc = QLineEdit()
        self.txt_c_desc.setPlaceholderText("บันทึกช่วยจำ (ไม่บังคับ)")
        r2.addWidget(self.txt_c_desc, 1)
        add_layout.addLayout(r2)

        btn_row = QHBoxLayout()
        btn_add = QPushButton("➕ เพิ่มกฎนี้")
        btn_add.setStyleSheet("background: #a6e3a1; color: #1e1e2e; padding: 6px 16px;")
        btn_add.clicked.connect(self.add_custom_rule)

        btn_del = QPushButton("🗑️ ลบกฎที่เลือก")
        btn_del.setStyleSheet("background: #f38ba8; color: #1e1e2e; padding: 6px 12px;")
        btn_del.clicked.connect(self.delete_custom_rule)

        btn_clear = QPushButton("🧹 ล้างทั้งหมด")
        btn_clear.setStyleSheet("background: #45475a; color: #cdd6f4; padding: 6px 12px;")
        btn_clear.clicked.connect(self.clear_custom_rules)

        btn_row.addStretch()
        btn_row.addWidget(btn_add)
        btn_row.addWidget(btn_del)
        btn_row.addWidget(btn_clear)
        add_layout.addLayout(btn_row)

        vbox.addWidget(grp_add)
        self._refresh_custom_rules_table()
        self.tabs.addTab(tab, "⚙️ 3. กฎที่คุณกำหนดเอง & พรีเซ็ต (Custom Rules)")

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 1 LOGIC: SCAN & APPLY
    # ══════════════════════════════════════════════════════════════════════════
    def scan_and_preview(self):
        from tstudio_core import TStudioCore
        prof_name = getattr(self.mw, 'current_profile_name', "Default")
        prof = TStudioCore.get_current_profile_data(prof_name)
        glossary = prof.get("glossary", {}) if self.chk_glossary.isChecked() else {}

        opts = {
            'model_codes': self.chk_model_codes.isChecked(),
            'scifi': self.chk_scifi.isChecked(),
            'weapons': self.chk_weapons.isChecked(),
            'acronyms': self.chk_acronyms.isChecked(),
            'vehicles': self.chk_vehicles.isChecked(),
            'calibers': self.chk_calibers.isChecked(),
            'keys': self.chk_keys.isChecked(),
            'glossary': glossary
        }

        active_custom_rules = self.custom_rules if self.chk_custom.isChecked() else None

        model_data = getattr(self.mw.model, '_data', [])
        if self.rad_selected.isChecked() and hasattr(self.mw, '_get_selected_source_rows'):
            target_indices = self.mw._get_selected_source_rows()
        else:
            target_indices = list(range(len(model_data)))

        self._pending_repairs = []
        self.tbl_preview.setRowCount(0)

        total_changes_count = 0
        for r in target_indices:
            if 0 <= r < len(model_data):
                item = model_data[r]
                src = str(item.get("source", ""))
                trans = str(item.get("trans", ""))
                if not src or not trans:
                    continue
                repaired, changes = TStudioCore.retrofit_military_text(src, trans, options=opts, custom_rules=active_custom_rules)
                if changes and repaired != trans:
                    self._pending_repairs.append((r, item.get("id", str(r+1)), src, trans, repaired, changes))
                    total_changes_count += len(changes)

        self.tbl_preview.setRowCount(len(self._pending_repairs))
        for row_ui, (r, row_id, src, trans, repaired, changes) in enumerate(self._pending_repairs):
            it_r = QTableWidgetItem(str(r + 1))
            it_id = QTableWidgetItem(str(row_id))
            it_src = QTableWidgetItem(src)
            it_old = QTableWidgetItem(trans)
            it_new = QTableWidgetItem(repaired)

            it_r.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            it_id.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            it_src.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            it_old.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            # Make repaired column editable so user can tweak directly!
            it_new.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable)

            it_r.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            it_old.setForeground(QBrush(QColor("#f38ba8")))
            it_new.setForeground(QBrush(QColor("#a6e3a1")))

            self.tbl_preview.setItem(row_ui, 0, it_r)
            self.tbl_preview.setItem(row_ui, 1, it_id)
            self.tbl_preview.setItem(row_ui, 2, it_src)
            self.tbl_preview.setItem(row_ui, 3, it_old)
            self.tbl_preview.setItem(row_ui, 4, it_new)

        if self._pending_repairs:
            self.lbl_status.setText(f"🎉 ตรวจพบ {total_changes_count} จุด ใน {len(self._pending_repairs)} แถว (สามารถดับเบิลคลิกแก้คำได้ก่อนกดบันทึก)")
            self.lbl_status.setStyleSheet("color: #a6e3a1; font-weight: bold; font-size: 12px;")
            self.btn_apply.setEnabled(True)
        else:
            self.lbl_status.setText("✅ ไม่พบคำศัพท์ที่ผิดปกติในขอบเขตที่เลือก (คำแปลถูกต้องดีแล้ว)")
            self.lbl_status.setStyleSheet("color: #89b4fa; font-weight: bold; font-size: 12px;")
            self.btn_apply.setEnabled(False)

    def apply_changes(self):
        if not self._pending_repairs:
            return

        reply = QMessageBox.question(
            self, "ยืนยันการบันทึก",
            f"ต้องการบันทึกการแก้ไขคำศัพท์ลงใน {len(self._pending_repairs)} แถว ใช่หรือไม่?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        applied_count = 0
        for row_ui, (r, row_id, src, trans, original_repaired, changes) in enumerate(self._pending_repairs):
            it = self.tbl_preview.item(row_ui, 4)
            repaired_text = it.text() if it else original_repaired
            if 0 <= r < len(self.mw.model._data):
                self.mw.model.update_trans(r, repaired_text)
                applied_count += 1

        if hasattr(self.mw, 'current_source_row') and 0 <= self.mw.current_source_row < len(self.mw.model._data):
            curr_item = self.mw.model._data[self.mw.current_source_row]
            self.mw.txt_trans.blockSignals(True)
            self.mw.txt_trans.setPlainText(curr_item.get("trans", ""))
            self.mw.txt_trans.blockSignals(False)

        self.mw.update_progress_stats()
        self.mw.statusBar().showMessage(f"ซ่อมแซมคำศัพท์สำเร็จ {applied_count} แถว (0 Token Used). กด Ctrl+S เพื่อบันทึกไฟล์", 6000)
        QMessageBox.information(self, "สำเร็จ", f"ซ่อมแซมคำศัพท์เรียบร้อยแล้ว {applied_count} แถว!\n\n💡 บันทึกผลลงตารางเรียบร้อย อย่าลืมกด Ctrl+S เพื่อบันทึกไฟล์")
        self.accept()

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 2 LOGIC: DISCOVERY & 1-CLICK FIX
    # ══════════════════════════════════════════════════════════════════════════
    def discover_entities(self):
        from tstudio_core import TStudioCore
        model_data = getattr(self.mw.model, '_data', [])
        if not model_data:
            self.lbl_disc_status.setText("⚠️ ไม่มีข้อมูลในไฟล์ปัจจุบัน")
            return

        self.lbl_disc_status.setText("⏳ กำลังสแกนคำศัพท์จากไฟล์...")
        QApplication.processEvents()

        entities = TStudioCore.extract_game_entities(model_data)
        self._discovered_entities = entities
        self.tbl_discovery.setRowCount(len(entities))

        for row_ui, ent in enumerate(entities):
            term = ent['term']
            count = ent['count']
            sample_src, sample_trans = ent['samples'][0] if ent['samples'] else ("", "")

            it_term = QTableWidgetItem(term)
            it_count = QTableWidgetItem(str(count))
            it_count.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            it_src = QTableWidgetItem(sample_src)
            it_trans = QTableWidgetItem(sample_trans)

            self.tbl_discovery.setItem(row_ui, 0, it_term)
            self.tbl_discovery.setItem(row_ui, 1, it_count)
            self.tbl_discovery.setItem(row_ui, 2, it_src)
            self.tbl_discovery.setItem(row_ui, 3, it_trans)

        self.lbl_disc_status.setText(f"🎉 ค้นพบ {len(entities)} คำศัพท์/รหัสเฉพาะในเกมนี้ (เลือกแถวเพื่อสร้างกฎแก้ไข)")
        self.lbl_disc_status.setStyleSheet("color: #a6e3a1; font-weight: bold;")

    def on_discovery_row_selected(self):
        selected_rows = self.tbl_discovery.selectionModel().selectedRows()
        if not selected_rows:
            return
        r = selected_rows[0].row()
        it_term = self.tbl_discovery.item(r, 0)
        it_trans = self.tbl_discovery.item(r, 3)
        if it_term:
            term = it_term.text()
            self.txt_disc_src.setText(term)
            self.txt_disc_rep.setText(term)
        if it_trans:
            self.txt_disc_orig.setText(it_trans.text())
        self.txt_disc_rep.setFocus()

    def add_discovered_to_custom(self):
        src = self.txt_disc_src.text().strip()
        orig = self.txt_disc_orig.text().strip()
        rep = self.txt_disc_rep.text().strip()
        if not src or not orig or not rep:
            QMessageBox.warning(self, "ข้อมูลไม่ครบ", "กรุณาระบุคำในต้นฉบับ, คำไทยเดิมที่แปลผิด, และคำแปลใหม่ที่ต้องการ")
            return

        new_rule = {
            'src': r'\b' + re.escape(src) + r'\b',
            'trans': re.escape(orig),
            'rep': rep,
            'desc': f"Discovered: {src} ➔ {rep}"
        }
        self.custom_rules.append(new_rule)
        self._save_custom_rules_to_profile()
        self._refresh_custom_rules_table()
        QMessageBox.information(
            self, "สำเร็จ",
            f"เพิ่มกฎสำหรับ '{src}' เรียบร้อยแล้ว!\n\nคุณสามารถกดสลับไปที่แท็บ '1. ซ่อมแซมอัตโนมัติ' แล้วกด 'Preview' เพื่อดูผลลัพธ์ได้ทันที"
        )

    def apply_discovered_rule_now(self):
        src = self.txt_disc_src.text().strip()
        orig = self.txt_disc_orig.text().strip()
        rep = self.txt_disc_rep.text().strip()
        if not src or not orig or not rep:
            QMessageBox.warning(self, "ข้อมูลไม่ครบ", "กรุณาระบุข้อมูลให้ครบถ้วน")
            return

        reply = QMessageBox.question(
            self, "ยืนยันการแทนที่ทันที",
            f"ต้องการค้นหาคำว่า '{orig}' และแทนที่ด้วย '{rep}'\nเฉพาะในแถวที่ต้นฉบับภาษาอังกฤษมีคำว่า '{src}' หรือไม่?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        model_data = getattr(self.mw.model, '_data', [])
        applied_count = 0
        src_pat = re.compile(r'\b' + re.escape(src) + r'\b', re.IGNORECASE)
        orig_pat = re.compile(re.escape(orig), re.IGNORECASE)

        for r, item in enumerate(model_data):
            row_src = str(item.get("source", ""))
            row_trans = str(item.get("trans", ""))
            if src_pat.search(row_src) and orig_pat.search(row_trans):
                new_trans = orig_pat.sub(rep, row_trans)
                if new_trans != row_trans:
                    self.mw.model.update_trans(r, new_trans)
                    applied_count += 1

        if applied_count > 0:
            self.mw.update_progress_stats()
            self.mw.statusBar().showMessage(f"แก้ไขคำศัพท์สำเร็จ {applied_count} แถว (0 Token Used).", 6000)
            QMessageBox.information(self, "สำเร็จ", f"แก้ไขคำศัพท์สำเร็จ {applied_count} แถว!\n\n💡 บันทึกผลลงตารางเรียบร้อย อย่าลืมกด Ctrl+S เพื่อบันทึกไฟล์")
            self.discover_entities()
        else:
            QMessageBox.information(self, "ไม่พบจุดแก้ไข", f"ไม่พบบรรทัดที่ตรงกับเงื่อนไขทั้งสองพร้อมกัน (อาจถูกแก้ไปแล้ว)")

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 3 LOGIC: CUSTOM RULES & PRESETS
    # ══════════════════════════════════════════════════════════════════════════
    def _refresh_custom_rules_table(self):
        self.tbl_custom_rules.setRowCount(len(self.custom_rules))
        for r, crule in enumerate(self.custom_rules):
            self.tbl_custom_rules.setItem(r, 0, QTableWidgetItem(crule.get('src', '')))
            self.tbl_custom_rules.setItem(r, 1, QTableWidgetItem(crule.get('trans', '')))
            self.tbl_custom_rules.setItem(r, 2, QTableWidgetItem(crule.get('rep', '')))
            self.tbl_custom_rules.setItem(r, 3, QTableWidgetItem(crule.get('desc', '')))

    def _save_custom_rules_to_profile(self):
        from tstudio_core import TStudioCore
        prof_name = getattr(self.mw, 'current_profile_name', "Default")
        prof = TStudioCore.get_current_profile_data(prof_name)
        prof["retrofit_custom_rules"] = self.custom_rules

    def add_custom_rule(self):
        src = self.txt_c_src.text().strip()
        trans = self.txt_c_trans.text().strip()
        rep = self.txt_c_rep.text().strip()
        desc = self.txt_c_desc.text().strip() or f"{src} ➔ {rep}"

        if not src or not trans:
            QMessageBox.warning(self, "ข้อมูลไม่ครบ", "กรุณาระบุคำในต้นฉบับและคำไทยเดิมที่แปลผิด")
            return

        self.custom_rules.append({
            'src': src,
            'trans': trans,
            'rep': rep,
            'desc': desc
        })
        self._save_custom_rules_to_profile()
        self._refresh_custom_rules_table()
        self.txt_c_src.clear()
        self.txt_c_trans.clear()
        self.txt_c_rep.clear()
        self.txt_c_desc.clear()

    def delete_custom_rule(self):
        selected_rows = self.tbl_custom_rules.selectionModel().selectedRows()
        if not selected_rows:
            return
        row = selected_rows[0].row()
        if 0 <= row < len(self.custom_rules):
            self.custom_rules.pop(row)
            self._save_custom_rules_to_profile()
            self._refresh_custom_rules_table()

    def clear_custom_rules(self):
        if not self.custom_rules:
            return
        reply = QMessageBox.question(self, "ยืนยัน", "ต้องการล้างกฎที่คุณกำหนดเองทั้งหมดใช่หรือไม่?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.custom_rules.clear()
            self._save_custom_rules_to_profile()
            self._refresh_custom_rules_table()

    def load_preset_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "โหลดไฟล์ Preset คำศัพท์", "", "JSON Files (*.json)")
        if file_path and os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if isinstance(data, list):
                    self.custom_rules = data
                    self._save_custom_rules_to_profile()
                    self._refresh_custom_rules_table()
                    QMessageBox.information(self, "สำเร็จ", f"โหลดพรีเซ็ตสำเร็จ ({len(data)} กฎ)")
                else:
                    QMessageBox.warning(self, "รูปแบบไม่ถูกต้อง", "ไฟล์ JSON ต้องเป็นรายการ List ของ Rules")
            except Exception as e:
                QMessageBox.critical(self, "เกิดข้อผิดพลาด", f"ไม่สามารถโหลดไฟล์ได้: {e}")

    def save_preset_file(self):
        if not self.custom_rules:
            QMessageBox.warning(self, "ไม่มีข้อมูล", "ยังไม่มีกฎสำหรับบันทึกเป็นพรีเซ็ต")
            return
        file_path, _ = QFileDialog.getSaveFileName(self, "บันทึกไฟล์ Preset คำศัพท์", "custom_weapons_preset.json", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.custom_rules, f, ensure_ascii=False, indent=2)
                QMessageBox.information(self, "สำเร็จ", f"บันทึกพรีเซ็ตสำเร็จที่:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "เกิดข้อผิดพลาด", f"ไม่สามารถบันทึกไฟล์ได้: {e}")

    def load_template_preset(self, index):
        if index <= 0:
            return
        
        templates = {
            1: [ # Sci-Fi & Cyberpunk
                {'src': r'\bMantis Blade\b', 'trans': r'ใบมีดตั๊กแตน', 'rep': 'ใบมีดแมนทิส', 'desc': 'Mantis Blade ➔ ใบมีดแมนทิส'},
                {'src': r'\bSandevistan\b', 'trans': r'แซนเดวิสตาน|แซนเดวิสแตน', 'rep': 'แซนเดวิสตาน', 'desc': 'Sandevistan ➔ แซนเดวิสตาน'},
                {'src': r'\bSmart\s*Shotgun\b', 'trans': r'ปืนลูกซองฉลาด', 'rep': 'สมาร์ตช็อตกัน', 'desc': 'Smart Shotgun ➔ สมาร์ตช็อตกัน'},
                {'src': r'\bTech\s*Sniper\b', 'trans': r'สไนเปอร์เทคโนโลยี', 'rep': 'เทคสไนเปอร์', 'desc': 'Tech Sniper ➔ เทคสไนเปอร์'},
                {'src': r'\bMonowire\b', 'trans': r'ลวดเดี่ยว|เส้นลวดโมโน', 'rep': 'โมโนไวร์', 'desc': 'Monowire ➔ โมโนไวร์'},
            ],
            2: [ # Helldivers 2
                {'src': r'\bAutocannon\b', 'trans': r'ปืนใหญ่อัตโนมัติ|ออโต้แคนนอน', 'rep': 'ออโต้แคนนอน', 'desc': 'Autocannon ➔ ออโต้แคนนอน'},
                {'src': r'\bQuasar\s*Cannon\b', 'trans': r'ปืนใหญ่เควาซาร์', 'rep': 'เควซาร์แคนนอน', 'desc': 'Quasar Cannon ➔ เควซาร์แคนนอน'},
                {'src': r'\bStratagem\b', 'trans': r'แผนยุทธการ|กลยุทธ์', 'rep': 'สแตรททาเจม', 'desc': 'Stratagem ➔ สแตรททาเจม'},
                {'src': r'\bHellpod\b', 'trans': r'ฝักนรก|แคปซูลนรก', 'rep': 'เฮลพ็อด', 'desc': 'Hellpod ➔ เฮลพ็อด'},
                {'src': r'\bPatriot\s*Exosuit\b', 'trans': r'ชุดสูทภายนอกแพทริออต', 'rep': 'หุ่นเกราะ Patriot Exosuit', 'desc': 'Patriot Exosuit ➔ หุ่นเกราะ Patriot Exosuit'},
            ],
            3: [ # Warhammer 40k & Space Marine
                {'src': r'\bChainsword\b', 'trans': r'ดาบเลื่อย', 'rep': 'ดาบเชนซอร์ด', 'desc': 'Chainsword ➔ ดาบเชนซอร์ด'},
                {'src': r'\bMelta\s*Gun\b', 'trans': r'ปืนเมลตา|ปืนหลอมละลาย', 'rep': 'ปืนเมลทากัน', 'desc': 'Melta Gun ➔ ปืนเมลทากัน'},
                {'src': r'\bPower\s*Sword\b', 'trans': r'ดาบพลัง|ดาบพลังงาน', 'rep': 'ดาบพาวเวอร์ซอร์ด', 'desc': 'Power Sword ➔ ดาบพาวเวอร์ซอร์ด'},
                {'src': r'\bThunder\s*Hammer\b', 'trans': r'ค้อนสายฟ้า', 'rep': 'ค้อนทันเดอร์แฮมเมอร์', 'desc': 'Thunder Hammer ➔ ค้อนทันเดอร์แฮมเมอร์'},
                {'src': r'\bLasgun\b', 'trans': r'ปืนเลเซอร์', 'rep': 'ปืนลาสกัน', 'desc': 'Lasgun ➔ ปืนลาสกัน'},
            ]
        }

        if index in templates:
            reply = QMessageBox.question(self, "ยืนยันการโหลด", "ต้องการเพิ่มตัวอย่างพรีเซ็ตนี้เข้าไปในรายการกฎใช่หรือไม่?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.custom_rules.extend(templates[index])
                self._save_custom_rules_to_profile()
                self._refresh_custom_rules_table()
                QMessageBox.information(self, "สำเร็จ", f"โหลดตัวอย่างพรีเซ็ตเรียบร้อยแล้ว!")
        self.cmb_templates.blockSignals(True)
        self.cmb_templates.setCurrentIndex(0)
        self.cmb_templates.blockSignals(False)


class GlossarySweeperDialog(QDialog):
    """
    Intelligent Glossary Sweeper & Lore Protector Dialog.
    Audits the project's profile glossary, identifies common words, engine tags, vocal noises,
    and unused terms in the game file, and provides 1-click purging while protecting Lore.
    """
    def __init__(self, main_window):
        super().__init__(main_window)
        self.mw = main_window
        self.setWindowTitle("🧹 กวาดล้างคำศัพท์ทั่วไปและคำที่ไม่ได้ใช้ (Glossary Sweeper & Lore Protector)")
        self.resize(980, 680)
        self.setStyleSheet("""
            QDialog { background-color: #1e1e2e; color: #cdd6f4; font-family: 'Segoe UI', Tahoma, sans-serif; }
            QGroupBox { border: 1px solid #45475a; border-radius: 6px; margin-top: 10px; font-weight: bold; color: #89b4fa; padding-top: 10px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }
            QTableWidget { background-color: #181825; color: #cdd6f4; gridline-color: #313244; border: 1px solid #45475a; border-radius: 4px; }
            QHeaderView::section { background-color: #313244; color: #cdd6f4; font-weight: bold; padding: 5px; border: 1px solid #45475a; }
            QCheckBox { color: #cdd6f4; spacing: 6px; }
            QPushButton { font-weight: bold; border-radius: 4px; padding: 6px 12px; }
            QLineEdit { background-color: #181825; color: #cdd6f4; border: 1px solid #45475a; border-radius: 4px; padding: 4px 8px; }
        """)

        import copy
        self.prof_name = getattr(self.mw, 'current_profile_name', 'Default')
        self.prof_data = TStudioCore.get_current_profile_data(self.prof_name)
        self.original_glossary = copy.deepcopy(self.prof_data.get("glossary", {}))

        # Check if project has rows loaded
        self.has_project_data = False
        self.full_corpus = ""
        self.csv_filename = ""
        if hasattr(self.mw, 'model') and self.mw.model and getattr(self.mw.model, '_data', None):
            self.has_project_data = True
            sources = [str(r.get("source", "")) for r in self.mw.model._data if r and r.get("source")]
            self.full_corpus = "\n".join(sources).lower()
            if getattr(self.mw, 'csv_path', None):
                self.csv_filename = os.path.basename(self.mw.csv_path)

        self._analyzed_items = []
        self._init_ui()
        self._analyze_and_populate()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)

        # ── Header Card & Metric Badges ──
        header_card = QFrame()
        header_card.setStyleSheet("background: #181825; border: 1px solid #313244; border-radius: 6px; padding: 6px;")
        h_layout = QVBoxLayout(header_card)
        h_layout.setSpacing(6)

        title_row = QHBoxLayout()
        lbl_title = QLabel(f"🎮 <b>โปรไฟล์:</b> <span style='color: #89b4fa;'>{self.prof_name}</span>")
        lbl_title.setStyleSheet("font-size: 13px;")
        title_row.addWidget(lbl_title)

        title_row.addStretch(1)

        file_info = f"📄 <b>ไฟล์เกม:</b> {self.csv_filename} ({len(self.mw.model._data) if self.has_project_data else 0} แถว)" if self.has_project_data else "📄 <b>โหมด:</b> คลังศัพท์โปรไฟล์ (ยังไม่ได้โหลดไฟล์บทสนทนา)"
        lbl_file = QLabel(file_info)
        lbl_file.setStyleSheet("color: #a6adc8; font-size: 12px;")
        title_row.addWidget(lbl_file)
        h_layout.addLayout(title_row)

        # Metric badges row
        badges_row = QHBoxLayout()
        badges_row.setSpacing(10)

        self.lbl_b_total = QLabel("📚 คำศัพท์ทั้งหมด: 0")
        self.lbl_b_total.setStyleSheet("background: #313244; color: #cdd6f4; font-weight: bold; border-radius: 4px; padding: 4px 8px; font-size: 11px;")
        badges_row.addWidget(self.lbl_b_total)

        self.lbl_b_generic = QLabel("⚠️ คำทั่วไป/ขยะ: 0")
        self.lbl_b_generic.setStyleSheet("background: #fab387; color: #11111b; font-weight: bold; border-radius: 4px; padding: 4px 8px; font-size: 11px;")
        badges_row.addWidget(self.lbl_b_generic)

        self.lbl_b_unused = QLabel("💤 ไม่พบในไฟล์เกม: 0")
        self.lbl_b_unused.setStyleSheet("background: #cba6f7; color: #11111b; font-weight: bold; border-radius: 4px; padding: 4px 8px; font-size: 11px;")
        badges_row.addWidget(self.lbl_b_unused)

        self.lbl_b_safe = QLabel("🛡️ คำเฉพาะทาง (Lore): 0")
        self.lbl_b_safe.setStyleSheet("background: #a6e3a1; color: #11111b; font-weight: bold; border-radius: 4px; padding: 4px 8px; font-size: 11px;")
        badges_row.addWidget(self.lbl_b_safe)

        badges_row.addStretch(1)
        h_layout.addLayout(badges_row)
        main_layout.addWidget(header_card)

        # ── Filter & Protection Rules GroupBox ──
        grp_rules = QGroupBox("⚙️ กฎการคัดกรองและการคุ้มครองศัพท์เฉพาะ (Filter & Lore Protection Rules)")
        rules_layout = QVBoxLayout(grp_rules)
        rules_layout.setSpacing(6)

        r1 = QHBoxLayout()
        self.chk_rule_common = QCheckBox("🗑️ กวาดล้างคำศัพท์ภาษาอังกฤษทั่วไป (Generic Common Words เช่น Base, White, Flight)")
        self.chk_rule_common.setChecked(True)
        self.chk_rule_common.toggled.connect(self._recalculate_selections)
        r1.addWidget(self.chk_rule_common)

        self.chk_rule_engine = QCheckBox("🗑️ กวาดล้างแท็กเอนจินและโค้ดระบบ (<wait_s>, /size, disableskip)")
        self.chk_rule_engine.setChecked(True)
        self.chk_rule_engine.toggled.connect(self._recalculate_selections)
        r1.addWidget(self.chk_rule_engine)

        self.chk_rule_vocal = QCheckBox("🗑️ กวาดล้างเสียงคราง/คำอุทาน (Haah, Aah, Nnn)")
        self.chk_rule_vocal.setChecked(True)
        self.chk_rule_vocal.toggled.connect(self._recalculate_selections)
        r1.addWidget(self.chk_rule_vocal)
        rules_layout.addLayout(r1)

        r2 = QHBoxLayout()
        self.chk_rule_unused = QCheckBox("💤 กวาดล้างคำที่ไม่พบการใช้งานในไฟล์เกมนี้ (0 ครั้ง)")
        self.chk_rule_unused.setEnabled(self.has_project_data)
        self.chk_rule_unused.setChecked(False)
        self.chk_rule_unused.setToolTip("กวาดล้างคำศัพท์ที่ไม่เคยปรากฏเลยในไฟล์งานแปลปัจจุบัน เพื่อลดขนาด Glossary และประหยัด Token สูงสุด")
        self.chk_rule_unused.toggled.connect(self._recalculate_selections)
        r2.addWidget(self.chk_rule_unused)

        self.chk_protect_lore = QCheckBox("🛡️ ปกป้องคำที่มี Tag (Person, Location, Faction, Weapon, Item) ไม่ให้ถูกลบ")
        self.chk_protect_lore.setChecked(True)
        self.chk_protect_lore.setStyleSheet("color: #a6e3a1; font-weight: bold;")
        self.chk_protect_lore.setToolTip("คงคำศัพท์ที่เป็นชื่อบุคคล สถานที่ ฝ่าย อาวุธ และไอเทมไว้เสมอ แม้คำนั้นจะตรงกับคำทั่วไป")
        self.chk_protect_lore.toggled.connect(self._recalculate_selections)
        r2.addWidget(self.chk_protect_lore)

        r2.addStretch(1)

        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("🔍 ค้นหาคำศัพท์ในตาราง...")
        self.txt_search.setClearButtonEnabled(True)
        self.txt_search.textChanged.connect(self._filter_table_view)
        self.txt_search.setMaximumWidth(220)
        r2.addWidget(self.txt_search)
        rules_layout.addLayout(r2)

        main_layout.addWidget(grp_rules)

        # ── Audit Results Table ──
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            "เลือก (ลบ)", "คำต้นฉบับ (EN)", "คำแปลภาษาไทย (TH)", "หมวดหมู่ (Tag)", "สาเหตุที่แนะนำให้ลบ", "ความถี่ในไฟล์"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 75)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.table.setColumnWidth(1, 180)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.table.setColumnWidth(2, 200)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(3, 90)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(5, 100)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.cellClicked.connect(self._on_cell_clicked)
        main_layout.addWidget(self.table, 1)

        # ── Footer Toolbar ──
        footer = QHBoxLayout()
        btn_sel_all = QPushButton("☑️ เลือกทั้งหมด")
        btn_sel_all.clicked.connect(lambda: self._set_all_checks(True))
        footer.addWidget(btn_sel_all)

        btn_desel_all = QPushButton("⬜ ยกเลิกเลือก")
        btn_desel_all.clicked.connect(lambda: self._set_all_checks(False))
        footer.addWidget(btn_desel_all)

        btn_sel_generic = QPushButton("⚠️ เลือกเฉพาะคำทั่วไป/ขยะ")
        btn_sel_generic.clicked.connect(self._select_generic_only)
        footer.addWidget(btn_sel_generic)

        if self.has_project_data:
            btn_sel_unused = QPushButton("💤 เลือกเฉพาะคำที่พบ 0 ครั้ง")
            btn_sel_unused.clicked.connect(self._select_unused_only)
            footer.addWidget(btn_sel_unused)

        self.lbl_selected_stat = QLabel("💡 เลือกเพื่อลบ: 0 / 0 คำ")
        self.lbl_selected_stat.setStyleSheet("color: #fab387; font-weight: bold; margin-left: 10px;")
        footer.addWidget(self.lbl_selected_stat)

        footer.addStretch(1)

        btn_cancel = QPushButton("ปิด (Cancel)")
        btn_cancel.clicked.connect(self.reject)
        footer.addWidget(btn_cancel)

        self.btn_purge = QPushButton("🧹 กวาดล้างคำที่เลือกทันที (Purge Selected)")
        self.btn_purge.setStyleSheet("background: #f38ba8; color: #11111b; font-weight: bold; padding: 6px 16px; font-size: 12px; border-radius: 4px;")
        self.btn_purge.setToolTip("ลบคำศัพท์ที่ติ๊กเลือกออกจากโปรไฟล์นี้อย่างถาวร (สามารถกด Undo ↩ ได้ในหน้าต่างหลัก)")
        self.btn_purge.clicked.connect(self._execute_purge)
        footer.addWidget(self.btn_purge)

        main_layout.addLayout(footer)

    def _analyze_and_populate(self):
        self._analyzed_items = []
        glossary = self.original_glossary

        generic_count = 0
        unused_count = 0
        safe_count = 0

        for term, val in glossary.items():
            if isinstance(val, (list, tuple)):
                th = str(val[0]) if len(val) > 0 else ""
                tag = str(val[1]) if len(val) > 1 else "General"
            else:
                th = str(val) if val else ""
                tag = "General"

            term_str = str(term).strip()
            term_low = term_str.lower()

            # Classify defects
            is_engine = is_engine_markup_tag(term_str)
            is_vocal = bool(RE_VOCAL_SOUNDS.match(term_str))
            is_common = is_common_generic_english_word(term_str)
            is_lore_tag = tag in ("Person", "Location", "Faction", "Weapon", "Item")

            occ = None
            if self.has_project_data and self.full_corpus:
                pattern = r'\b' + re.escape(term_low) + r'\b'
                occ = len(re.findall(pattern, self.full_corpus))
                if occ == 0:
                    unused_count += 1

            if is_engine or is_vocal or is_common:
                generic_count += 1
            elif is_lore_tag:
                safe_count += 1

            self._analyzed_items.append({
                "term": term_str,
                "th": th,
                "tag": tag,
                "is_engine": is_engine,
                "is_vocal": is_vocal,
                "is_common": is_common,
                "is_lore_tag": is_lore_tag,
                "occurrences": occ,
                "checked": False
            })

        self.lbl_b_total.setText(f"📚 คำศัพท์ทั้งหมด: {len(glossary)}")
        self.lbl_b_generic.setText(f"⚠️ คำทั่วไป/ขยะ: {generic_count}")
        self.lbl_b_unused.setText(f"💤 ไม่พบในไฟล์เกม: {unused_count}")
        self.lbl_b_safe.setText(f"🛡️ คำเฉพาะทาง (Lore): {safe_count}")

        self._recalculate_selections()

    def _recalculate_selections(self):
        purge_common = self.chk_rule_common.isChecked()
        purge_engine = self.chk_rule_engine.isChecked()
        purge_vocal = self.chk_rule_vocal.isChecked()
        purge_unused = self.chk_rule_unused.isChecked()
        protect_lore = self.chk_protect_lore.isChecked()

        for item in self._analyzed_items:
            reasons = []
            should_remove = False

            if purge_engine and item["is_engine"]:
                reasons.append("แท็ก/คำสั่งเอนจินเกม (Engine Tag)")
                should_remove = True
            elif purge_vocal and item["is_vocal"]:
                reasons.append("เสียงคราง/คำอุทาน (Vocal Moan)")
                should_remove = True
            elif purge_common and item["is_common"]:
                reasons.append("คำศัพท์ทั่วไปในพจนานุกรม (Common Word)")
                should_remove = True

            if purge_unused and item["occurrences"] == 0:
                reasons.append("ไม่พบการใช้งานในไฟล์เกม (0 ครั้ง)")
                should_remove = True

            # Lore protection override
            if item["is_lore_tag"] and protect_lore and not item["is_engine"]:
                should_remove = False
                if reasons:
                    reasons = [f"🛡️ ปกป้องโดย Tag ({item['tag']})"]

            item["reasons"] = reasons
            item["checked"] = should_remove

        self._render_table()

    def _render_table(self):
        search_q = self.txt_search.text().lower().strip()
        filtered = []
        for item in self._analyzed_items:
            if search_q:
                if search_q not in item["term"].lower() and search_q not in item["th"].lower():
                    continue
            filtered.append(item)

        self.table.setRowCount(len(filtered))
        for row, item in enumerate(filtered):
            # Checkbox
            chk_item = QTableWidgetItem()
            chk_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            chk_item.setCheckState(Qt.CheckState.Checked if item["checked"] else Qt.CheckState.Unchecked)
            chk_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            chk_item.setData(Qt.ItemDataRole.UserRole, item["term"])
            self.table.setItem(row, 0, chk_item)

            # EN
            en_item = QTableWidgetItem(item["term"])
            en_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            if item["checked"]:
                en_item.setForeground(QColor("#f38ba8"))
            self.table.setItem(row, 1, en_item)

            # TH
            th_item = QTableWidgetItem(item["th"])
            th_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.table.setItem(row, 2, th_item)

            # Tag
            tag_item = QTableWidgetItem(item["tag"])
            tag_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            tag_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if item["is_lore_tag"]:
                tag_item.setForeground(QColor("#a6e3a1"))
            self.table.setItem(row, 3, tag_item)

            # Reasons
            r_str = ", ".join(item["reasons"]) if item["reasons"] else "✅ คำเฉพาะทางของเกม (Game Lore)"
            reason_item = QTableWidgetItem(r_str)
            reason_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            if item["checked"]:
                reason_item.setForeground(QColor("#f9e2af"))
            elif item["is_lore_tag"]:
                reason_item.setForeground(QColor("#a6e3a1"))
            self.table.setItem(row, 4, reason_item)

            # Occurrences
            occ_str = f"{item['occurrences']} ครั้ง" if item["occurrences"] is not None else "—"
            occ_item = QTableWidgetItem(occ_str)
            occ_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            occ_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if item["occurrences"] == 0:
                occ_item.setForeground(QColor("#a6adc8"))
            self.table.setItem(row, 5, occ_item)

        self._update_counts_label()

    def _filter_table_view(self):
        self._render_table()

    def _on_cell_clicked(self, row, col):
        if col == 0:
            item_chk = self.table.item(row, 0)
            if item_chk:
                term = item_chk.data(Qt.ItemDataRole.UserRole)
                is_checked = (item_chk.checkState() == Qt.CheckState.Checked)
                for item in self._analyzed_items:
                    if item["term"] == term:
                        item["checked"] = is_checked
                        break
                self._update_counts_label()

    def _set_all_checks(self, checked):
        state = Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked
        for r in range(self.table.rowCount()):
            it = self.table.item(r, 0)
            if it:
                it.setCheckState(state)
                term = it.data(Qt.ItemDataRole.UserRole)
                for item in self._analyzed_items:
                    if item["term"] == term:
                        item["checked"] = checked
                        break
        self._update_counts_label()

    def _select_generic_only(self):
        for r in range(self.table.rowCount()):
            it = self.table.item(r, 0)
            if it:
                term = it.data(Qt.ItemDataRole.UserRole)
                for item in self._analyzed_items:
                    if item["term"] == term:
                        is_gen = (item["is_engine"] or item["is_vocal"] or item["is_common"])
                        it.setCheckState(Qt.CheckState.Checked if is_gen else Qt.CheckState.Unchecked)
                        item["checked"] = is_gen
                        break
        self._update_counts_label()

    def _select_unused_only(self):
        for r in range(self.table.rowCount()):
            it = self.table.item(r, 0)
            if it:
                term = it.data(Qt.ItemDataRole.UserRole)
                for item in self._analyzed_items:
                    if item["term"] == term:
                        is_un = (item["occurrences"] == 0)
                        it.setCheckState(Qt.CheckState.Checked if is_un else Qt.CheckState.Unchecked)
                        item["checked"] = is_un
                        break
        self._update_counts_label()

    def _update_counts_label(self):
        sel_count = sum(1 for it in self._analyzed_items if it["checked"])
        total_count = len(self._analyzed_items)
        self.lbl_selected_stat.setText(f"💡 กำลังเลือกเพื่อลบ: {sel_count} / {total_count} คำ")
        self.btn_purge.setEnabled(sel_count > 0)
        self.btn_purge.setText(f"🧹 กวาดล้างคำที่เลือก ({sel_count} คำ)")

    def _execute_purge(self):
        import copy
        terms_to_purge = [it["term"] for it in self._analyzed_items if it["checked"]]
        if not terms_to_purge:
            QMessageBox.information(self, "แจ้งเตือน", "ไม่มีคำศัพท์ที่ถูกเลือกสำหรับการกวาดล้าง")
            return

        reply = QMessageBox.question(
            self, "ยืนยันการกวาดล้างคำศัพท์",
            f"คุณต้องการลบคำศัพท์ที่เลือกทั้งหมด {len(terms_to_purge)} คำ\n"
            f"ออกจากโปรไฟล์ '{self.prof_name}' ทันทีหรือไม่?\n\n"
            f"(คำศัพท์ที่เหลือจะคงไว้เฉพาะชื่อ สถานที่ และศัพท์เฉพาะของเกมเท่านั้น)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        new_glossary = copy.deepcopy(self.original_glossary)
        for t in terms_to_purge:
            new_glossary.pop(t, None)

        self.mw._save_glossary_to_active_profile(new_glossary)
        self.mw.statusBar().showMessage(
            f"● กวาดล้างคำศัพท์สำเร็จ! ลบออก {len(terms_to_purge)} คำ คงเหลือคำเฉพาะทาง {len(new_glossary)} คำ (กด ↩ เพื่อเลิกทำได้)",
            4000
        )
        self.accept()


class ShortcutsCheatsheetDialog(QDialog):
    """Modern cheatsheet dialog showing all keyboard shortcuts grouped by category."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⌨️ รายการคีย์ลัดทั้งหมดในโปรแกรม (Keyboard Shortcuts)")
        self.resize(740, 600)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e2e;
                color: #cdd6f4;
                font-family: 'Segoe UI', Tahoma, sans-serif;
            }
            QLabel {
                color: #cdd6f4;
            }
            QScrollArea {
                border: 1px solid #313244;
                background-color: #181825;
                border-radius: 8px;
            }
            QPushButton#btnClose {
                background-color: #89b4fa;
                color: #11111b;
                border: none;
                padding: 8px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton#btnClose:hover {
                background-color: #b4befe;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 16)
        layout.setSpacing(14)

        # Header
        header_layout = QHBoxLayout()
        icon_lbl = QLabel("⌨️")
        icon_lbl.setStyleSheet("font-size: 28px;")
        header_layout.addWidget(icon_lbl)

        title_vbox = QVBoxLayout()
        lbl_title = QLabel("คู่มือคีย์ลัดทั้งหมด (Universal Shortcuts Cheatsheet)")
        lbl_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #89b4fa;")
        lbl_desc = QLabel("คีย์ลัดทุกคำสั่งได้รับการปรับแต่งให้ใช้งานได้จริง รวดเร็ว และไม่มีปัญหาคีย์ชนกัน")
        lbl_desc.setStyleSheet("font-size: 12px; color: #a6adc8;")
        title_vbox.addWidget(lbl_title)
        title_vbox.addWidget(lbl_desc)
        header_layout.addLayout(title_vbox)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Scroll Area for categories
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        scroll_vbox = QVBoxLayout(scroll_content)
        scroll_vbox.setContentsMargins(12, 12, 12, 12)
        scroll_vbox.setSpacing(16)

        categories = [
            ("📁 การจัดการไฟล์และโปรเจกต์ (File & Project)", [
                ("Ctrl+N", "เริ่มแปลไฟล์ใหม่ / นำเข้าไฟล์แปล (Start New Translation)"),
                ("Ctrl+O", "เปิดโปรเจกต์แปล / เปิดไฟล์อื่น (Open File/Project)"),
                ("Ctrl+S", "บันทึกข้อมูล (Save Project / File)"),
                ("Ctrl+Shift+S", "บันทึกเป็นไฟล์ใหม่ (Save CSV As...)"),
                ("Ctrl+D", "นำไฟล์เข้าเกมทันที (Deploy to Game)"),
            ]),
            ("🤖 การแปลภาษาและ AI (Translation & AI)", [
                ("Ctrl+T", "แปลข้อความอัตโนมัติ (Smart AI Retranslate)"),
                ("Ctrl+Shift+O", "ขอคำแปลเปรียบเทียบ 3 สไตล์ (3 Styles Modal)"),
                ("Ctrl+Shift+T", "แปลเฉพาะคำ/ส่วนที่เลือก (Translate Selected Snippet)"),
                ("Ctrl+Shift+Y", "แปลทับศัพท์เฉพาะคำ/ส่วนที่เลือก (Transliterate Selected Snippet)"),
                ("Ctrl+Shift+B", "ส่งแถวที่เลือกไปแปลชุดใน TRun (TRun Batch Engine)"),
                ("Ctrl+1", "เลือกผลแปล AI รูปแบบที่ 1 เข้าช่องแปล"),
                ("Ctrl+2", "เลือกผลแปล AI รูปแบบที่ 2 เข้าช่องแปล"),
                ("Ctrl+3", "เลือกผลแปล AI รูปแบบที่ 3 เข้าช่องแปล"),
                ("Ctrl+Enter / Enter", "ยืนยันการแก้ไขและข้ามไปยังแถวถัดไป (Confirm & Next Row)"),
                ("Shift+Enter", "ขึ้นบรรทัดใหม่ในช่องแปล (New Line)"),
            ]),
            ("📝 การแก้ไขและค้นหา (Editing & Search)", [
                ("Ctrl+F", "โฟกัสช่องค้นหาด่วน (Focus Quick Search)"),
                ("Alt+C", "เปิด/ปิด ตรงตามตัวพิมพ์ใหญ่-เล็ก (Match Case)"),
                ("Alt+W", "เปิด/ปิด ตรงทั้งคำ (Match Whole Word - ค้นหาคำเดี่ยวๆ)"),
                ("Alt+E", "เปิด/ปิด ตรงทั้งประโยคเป๊ะๆ (Exact Match - เช่น 'e' ตัวเดียว)"),
                ("Alt+R", "เปิด/ปิด นิพจน์เรกูลาร์ (Regular Expression)"),
                ("Ctrl+H", "เปิดหน้าต่างค้นหาและแทนที่ข้อความ (Find & Replace Dialog)"),
                ("Ctrl+Z", "ยกเลิกการเปลี่ยนแปลงล่าสุด (Undo)"),
                ("Ctrl+Y", "ทำซ้ำการเปลี่ยนแปลง (Redo)"),
                ("Ctrl+X", "ตัดข้อความ (Cut)"),
                ("Ctrl+C", "คัดลอกข้อความ (Copy)"),
                ("Ctrl+V", "วางข้อความ (Paste)"),
            ]),
            ("📊 การจัดการตารางและการนำทาง (Table & Navigation)", [
                ("Alt+Up", "เลื่อนเลือกแถวก่อนหน้า (Previous Row)"),
                ("Alt+Down", "เลื่อนเลือกแถวถัดไป (Next Row)"),
                ("Delete", "ล้างข้อความแปลในแถวที่เลือก (Clear Translation)"),
                ("Shift+Delete", "ลบแถวที่เลือกออกจากโปรเจกต์ (Delete Row)"),
                ("Backspace", "ล้างข้อความแปลในตาราง (Clear Translation Cell)"),
            ]),
            ("🛠️ เครื่องมือและมุมมอง (Tools & Views)", [
                ("Ctrl+I", "ตั้งค่าระบบและ API Model (Global Settings)"),
                ("Ctrl+B", "เปิดคลังคำศัพท์ (Glossary Manager)"),
                ("Ctrl+Q", "เปิด/ปิด การตรวจจับ QA (Toggle QA Check)"),
                ("Ctrl+M", "เปิด/ปิด ตัวกำกับ QA Marker (Toggle QA Marker)"),
                ("Ctrl+P", "ตั้งค่า AI Prompt Directives"),
                ("Ctrl+L", "เปิด TLM Studio (บริบทและคำศัพท์)"),
                ("F1", "สลับโหมด CAT Studio (โหมดแปลละเอียด)"),
                ("F2", "สลับโหมด Batch AI Runner (โหมดรันแปลความเร็วสูง)"),
                ("Alt+1", "เปิด/ปิด คอลัมน์ 1 (ตารางคำแปล CAT Table)"),
                ("Alt+2", "เปิด/ปิด คอลัมน์ 2 (คลังคำศัพท์ Glossary Window)"),
                ("Alt+3", "เปิด/ปิด คอลัมน์ 3 (พื้นที่แปล Translation Workspace)"),
                ("Ctrl++ / Ctrl+=", "ขยายขนาดตัวอักษร (Zoom In)"),
                ("Ctrl+-", "ย่อขนาดตัวอักษร (Zoom Out)"),
                ("Ctrl+0", "รีเซ็ตขนาดตัวอักษรมาตรฐาน (Reset Zoom)"),
                ("Alt+Z", "เปิด/ปิด การตัดบรรทัดคำ (Word Wrap)"),
                ("F12", "เปิดหน้าต่างแสดงคีย์ลัดนี้ (Shortcuts Cheatsheet)"),
            ]),
        ]

        for cat_title, items in categories:
            cat_box = QGroupBox(cat_title)
            cat_box.setStyleSheet("""
                QGroupBox {
                    font-weight: bold;
                    color: #fab387;
                    border: 1px solid #45475a;
                    border-radius: 6px;
                    margin-top: 10px;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px;
                }
            """)
            cat_layout = QVBoxLayout(cat_box)
            cat_layout.setSpacing(6)

            for key, desc in items:
                row_layout = QHBoxLayout()
                lbl_key = QLabel(f"<b>{key}</b>")
                lbl_key.setStyleSheet("""
                    background-color: #313244;
                    color: #a6e3a1;
                    border: 1px solid #45475a;
                    border-radius: 4px;
                    padding: 2px 8px;
                    font-family: 'Consolas', 'Courier New', monospace;
                    font-size: 12px;
                """)
                lbl_key.setFixedWidth(140)
                lbl_desc = QLabel(desc)
                lbl_desc.setStyleSheet("color: #cdd6f4; font-size: 12px;")
                row_layout.addWidget(lbl_key)
                row_layout.addWidget(lbl_desc, 1)
                cat_layout.addLayout(row_layout)

            scroll_vbox.addWidget(cat_box)

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll, 1)

        # Footer
        footer_layout = QHBoxLayout()
        footer_layout.addStretch()
        btn_close = QPushButton("ปิดหน้าต่าง (Close)")
        btn_close.setObjectName("btnClose")
        btn_close.clicked.connect(self.accept)
        footer_layout.addWidget(btn_close)
        layout.addLayout(footer_layout)


# =========================================================
# UI: Translation 3 Options (Moved to tstudio_ui_shared.py)
