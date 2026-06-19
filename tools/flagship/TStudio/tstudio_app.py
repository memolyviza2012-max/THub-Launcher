# -*- coding: utf-8 -*-
"""
Translation_Studio_Template.py
===============================
Universal Translation Studio Template
Adapted from the Studio Template to handle CSV and direct JSON deployment.
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Core')))
import csv
import sys
csv.field_size_limit(2147483647)
import json
import requests
import re
import file_converter
from tpua_engine import TPUAEngine
from tstudio_core import TStudioCore, CoreAI
from tstudio_ui_shared import SettingsDialog, PromptSettingsDialog, GlossaryDialog, ApiWorker

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableView, QHeaderView, QLabel, QPushButton, QLineEdit,
    QSplitter, QGroupBox, QComboBox, QMessageBox, QTextEdit,
    QAbstractItemView, QDialog, QFormLayout, QTableWidget,
    QTableWidgetItem, QRadioButton, QButtonGroup, QScrollArea,
    QFileDialog, QMenu, QSpinBox, QProgressBar
)
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex, QSortFilterProxyModel, QTimer, QLocale, QRunnable, QThreadPool, pyqtSignal, pyqtSlot, QObject
from PyQt6.QtGui import QColor, QKeySequence, QShortcut, QIcon, QPixmap

# ╔══════════════════════════════════════════════════════════════════╗
# ║           PROJECT CONFIGURATION — GOTG SPECIFIC                 ║
# ╚══════════════════════════════════════════════════════════════════╝
GAME_NAME    = "Your_Game_Name_Here"

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CSV_PATH     = os.path.join(BASE_DIR, "translation.csv")
CSV_ENCODING = "utf-8-sig"
COL_ID       = 0
COL_SOURCE   = 1
COL_TRANS    = 2
COL_AI_REF   = 3
# ═══════════════════════════════════════════════════════════════════

CONFIG_PATH  = os.path.join(BASE_DIR, "config.json")
GLOSSARY_PATH = os.path.join(BASE_DIR, "glossary.json")
PROMPTS_PATH = os.path.join(BASE_DIR, "prompts.json")

DEFAULT_SINGLE_PROMPT = f"""You are a Master-Level English-to-Thai Video Game Localization Specialist for '{GAME_NAME}'.
Translate this line. ID: '{{id}}'. Return ONLY the pure Thai string, no quotes, no explanations.
[GLOSSARY TO USE]
- Character A = Name A
- Gamora = กาโมร่า
- Drax = แดร็กซ์
- Rocket = ร็อคเก็ต
- Groot = กรู้ท
- Mantis = แมนทิส
- Milano = ยานมิลาโน่
- Nova Corps = โนวาคอร์ปส
- Lady Hellbender = เลดี้เฮลเบนเดอร์
- Knowhere = โนว์แวร์
- Cosmo = คอสโม่
- Universal Church of Truth = คริสตจักรแห่งสัจธรรมสากล
- Grand Unifier Raker = แกรนด์ยูนิฟายเออร์เรกเกอร์
- Worldmind = เวิลด์มายด์
- Flark = ฟลาร์ก
- Scut = สคัท

Text: {{source_text}}"""

DEFAULT_OPTIONS_PROMPT = f"""You are a Master-Level English-to-Thai Video Game Localization Specialist for '{GAME_NAME}'.
Translate this into 3 distinct styles:
1. Literal/Direct (แปลตรงตัว)
2. Casual/Slang (ภาษาพูด/สแลง)
3. Polite/Formal (สุภาพ/ทางการ)
ID: '{{id}}'.

[GLOSSARY TO USE]
- Character A = Name A
- Gamora = กาโมร่า
- Drax = แดร็กซ์
- Rocket = ร็อคเก็ต
- Groot = กรู้ท
- Mantis = แมนทิส
- Milano = ยานมิลาโน่
- Nova Corps = โนวาคอร์ปส
- Lady Hellbender = เลดี้เฮลเบนเดอร์
- Knowhere = โนว์แวร์
- Cosmo = คอสโม่
- Universal Church of Truth = คริสตจักรแห่งสัจธรรมสากล
- Grand Unifier Raker = แกรนด์ยูนิฟายเออร์เรกเกอร์
- Worldmind = เวิลด์มายด์
- Flark = ฟลาร์ก
- Scut = สคัท

Return ONLY a valid JSON array of 3 strings: ["option1", "option2", "option3"]
Text: {{source_text}}"""


DARK_SS = """
QMainWindow, QWidget, QDialog { background: #1e1e2e; color: #cdd6f4; }
QTableView, QTableWidget { background: #181825; color: #cdd6f4; gridline-color: #313244;
    selection-background-color: #45475a; alternate-background-color: #1e1e2e;
    font-size: 13px; }
QHeaderView::section { background: #313244; color: #a6adc8; padding: 6px;
    border: 1px solid #45475a; font-weight: bold; }
QLineEdit, QTextEdit { background: #313244; color: #cdd6f4; border: 1px solid #45475a;
    border-radius: 4px; padding: 6px; font-size: 14px; }
QPushButton { background: #45475a; color: #cdd6f4; border: none;
    border-radius: 4px; padding: 8px 16px; font-size: 13px; font-weight: bold; }
QPushButton:hover { background: #585b70; }
QPushButton#btnSave { background: #a6e3a1; color: #1e1e2e; }
QPushButton#btnRetranslate { background: #89b4fa; color: #1e1e2e; font-size: 12px; padding: 4px 8px; }
QGroupBox { border: 1px solid #45475a; border-radius: 6px; margin-top: 10px;
    padding-top: 14px; font-weight: bold; color: #89b4fa; }
QGroupBox::title { subcontrol-origin: margin; left: 10px; }
QComboBox { background: #313244; color: #cdd6f4; border: 1px solid #45475a;
    border-radius: 4px; padding: 4px 8px; }
QSplitter::handle { background: #313244; }
"""

# Duplicates removed, now imported from tstudio_ui_shared.py

import os
import csv
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QGroupBox, QHBoxLayout, QPushButton, QLineEdit, QMessageBox, QApplication, QFileDialog
from PyQt6.QtCore import Qt

class MergeTranslatedDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Merge Translated File")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        # Original File
        group_orig = QGroupBox("Original File")
        layout_orig = QHBoxLayout()
        self.txt_orig = QLineEdit()
        self.txt_orig.setPlaceholderText("Select original English file (Bundle, Locres, CSV)...")
        self.txt_orig.setReadOnly(True)
        btn_orig = QPushButton("Browse")
        btn_orig.clicked.connect(self.browse_orig)
        layout_orig.addWidget(self.txt_orig)
        layout_orig.addWidget(btn_orig)
        group_orig.setLayout(layout_orig)
        layout.addWidget(group_orig)
        
        # Translated File
        group_trans = QGroupBox("Translated File")
        layout_trans = QHBoxLayout()
        self.txt_trans = QLineEdit()
        self.txt_trans.setPlaceholderText("Select partially translated file (Bundle, Locres, CSV)...")
        self.txt_trans.setReadOnly(True)
        btn_trans = QPushButton("Browse")
        btn_trans.clicked.connect(self.browse_trans)
        layout_trans.addWidget(self.txt_trans)
        layout_trans.addWidget(btn_trans)
        group_trans.setLayout(layout_trans)
        layout.addWidget(group_trans)
        
        # Save File
        group_save = QGroupBox("Save File (Output CSV)")
        layout_save = QHBoxLayout()
        self.txt_save = QLineEdit()
        self.txt_save.setPlaceholderText("Select output CSV path to continue working...")
        self.txt_save.setReadOnly(True)
        btn_save = QPushButton("Browse")
        btn_save.clicked.connect(self.browse_save)
        layout_save.addWidget(self.txt_save)
        layout_save.addWidget(btn_save)
        group_save.setLayout(layout_save)
        layout.addWidget(group_save)
        
        # Execute
        self.btn_execute = QPushButton("🧩 Merge Translated File")
        self.btn_execute.setStyleSheet("background: #cba6f7; color: #1e1e2e; font-weight: bold; font-size: 14px; padding: 8px;")
        self.btn_execute.clicked.connect(self.execute_merge)
        layout.addWidget(self.btn_execute)
        
        self.merged_csv_path = None
        
    def browse_orig(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Original File", "", "Supported Files (*.csv *.lor *.locres *.tex *.bundle *.txt *.*)")
        if path: self.txt_orig.setText(path)
            
    def browse_trans(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Translated File", "", "Supported Files (*.csv *.lor *.locres *.tex *.bundle *.txt *.*)")
        if path: self.txt_trans.setText(path)
            
    def browse_save(self):
        path, _ = QFileDialog.getSaveFileName(self, "Select Output CSV", "", "CSV Files (*.csv)")
        if path: self.txt_save.setText(path)
            
    def execute_merge(self):
        orig_path = self.txt_orig.text()
        trans_path = self.txt_trans.text()
        save_path = self.txt_save.text()
        
        if not orig_path or not trans_path or not save_path:
            QMessageBox.warning(self, "Input Required", "Please select all 3 files.")
            return
            
        try:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            
            # Helper to extract to CSV if needed
            def ensure_csv(path):
                from tbundle_manager import TBundleManager
                if path.lower().endswith('.csv'): return path
                if TBundleManager.is_unity_bundle(path):
                    return TBundleManager.extract_text_to_csv(path)
                # Locres fallback? TBundleManager can extract locres too.
                if path.lower().endswith('.locres') or path.lower().endswith('.lor'):
                    return TBundleManager.extract_text_to_csv(path) # Wait, TBundleManager handles locres? No, TLocresManager does!
                # If TStudioCore handles it, let's just use what TStudio uses: TBundleManager or TLocresManager.
                # In tstudio_app.py open_file_dialog logic handles it. Let's do it similarly:
                from tlocres_manager import TLocresManager
                if TLocresManager.is_locres(path):
                    return TLocresManager.extract_locres_to_csv(path)
                return TBundleManager.extract_text_to_csv(path)
                
            orig_csv = ensure_csv(orig_path)
            trans_csv = ensure_csv(trans_path)
            
            if not orig_csv or not trans_csv or not os.path.exists(orig_csv) or not os.path.exists(trans_csv):
                raise Exception("Failed to extract one of the files to CSV.")
                
            # Read translated CSV
            trans_dict = {}
            with open(trans_csv, 'r', encoding='utf-8-sig', errors='ignore') as f:
                reader = csv.reader(f)
                headers = next(reader, None)
                if headers:
                    for row in reader:
                        if len(row) >= 3:
                            t_id = row[0]
                            # Usually translated text is in col 2 or 3 depending on format.
                            # TStudio outputs: ID, Source, Trans, AI_Ref. (Trans is col 2, AI_Ref is col 3)
                            t_text = row[2] if len(row) > 2 else ""
                            # If it's a raw bundle dump, translation might be empty, but let's take whatever has Thai characters or is not same as source
                            # Actually, if the Translated File is a TStudio CSV, translation is in col 2.
                            # If it's a modified bundle, translation is in Source column (col 1) because the bundle only has Source!
                            t_src = row[1] if len(row) > 1 else ""
                            
                            # Heuristic: If col 2 exists and is not empty, use it. Else use col 1.
                            if len(row) > 2 and row[2].strip():
                                final_t = row[2]
                            else:
                                final_t = t_src
                            trans_dict[t_id] = final_t
                            
            # Build merged CSV
            merged_count = 0
            with open(orig_csv, 'r', encoding='utf-8-sig', errors='ignore') as f_in, \
                 open(save_path, 'w', encoding='utf-8-sig', newline='') as f_out:
                reader = csv.reader(f_in)
                writer = csv.writer(f_out)
                headers = next(reader, None)
                if headers:
                    # Write standard headers: ID, Source, Trans, AI_Ref
                    writer.writerow(['ID', 'Source', 'Translation', 'AI Reference'])
                    
                for row in reader:
                    if len(row) >= 2:
                        o_id = row[0]
                        o_src = row[1]
                        trans_val = ""
                        
                        if o_id in trans_dict:
                            # We found a match in translated file
                            t_val = trans_dict[o_id]
                            # Only use it if it actually differs from original source OR if it contains Thai
                            import re
                            if t_val != o_src or re.search(r'[ก-๙เแไใโ]', t_val):
                                trans_val = t_val
                                merged_count += 1
                                
                        # Write row
                        writer.writerow([o_id, o_src, trans_val, trans_val])
                        
            self.merged_csv_path = save_path
            QApplication.restoreOverrideCursor()
            QMessageBox.information(self, "Merge Complete", f"Successfully merged {merged_count} translated entries!\nThe file is ready to use.")
            self.accept()
            
        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, "Error", f"An error occurred during merge:\n{e}")


class FindReplaceDialog(QDialog):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.mw = main_window
        self.setWindowTitle("🔍 Find & Replace")
        self.setFixedSize(420, 150)
        layout = QFormLayout(self)
        self.txt_find = QLineEdit()
        self.txt_replace = QLineEdit()
        layout.addRow("Find:", self.txt_find)
        layout.addRow("Replace with:", self.txt_replace)
        btn = QPushButton("Replace All")
        btn.clicked.connect(self.replace_all)
        btn.setStyleSheet("background: #f38ba8; color: #1e1e2e;")
        layout.addRow("", btn)

    def replace_all(self):
        find_txt = self.txt_find.text()
        rep_txt = self.txt_replace.text()
        if not find_txt: return
        model = self.mw.model
        count = 0
        model.beginResetModel()
        for item in model._data:
            if item["trans"] and find_txt in item["trans"]:
                item["trans"] = item["trans"].replace(find_txt, rep_txt)
                count += 1
        model.endResetModel()
        if count > 0:
            row = self.mw.current_source_row
            if 0 <= row < len(model._data):
                self.mw.txt_trans.blockSignals(True)
                self.mw.txt_trans.setPlainText(model._data[row]["trans"])
                self.mw.txt_trans.blockSignals(False)
            self.mw.statusBar().showMessage(f'Replaced {count} instances. Ctrl+S to save.', 5000)
            QMessageBox.information(self, "Success", f"Replaced {count} instances!")
        else:
            QMessageBox.information(self, "Not Found", "No matches found.")

# =========================================================
# UI: Translation 3 Options
# =========================================================
class TranslationOptionsDialog(QDialog):
    def __init__(self, parent, options):
        super().__init__(parent)
        self.setWindowTitle("🎯 Select Translation Style")
        self.setMinimumSize(500, 280)
        self.selected_text = ""
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("เลือกสไตล์คำแปลที่ต้องการ:"))
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        cl = QVBoxLayout(content)
        self.bg = QButtonGroup(self)
        labels = ["1️⃣ ตรงตัว (Literal)", "2️⃣ ภาษาพูด/สแลง (Casual)", "3️⃣ สุภาพ/ทางการ (Formal)"]
        for i, opt in enumerate(options):
            label = labels[i] if i < len(labels) else f"Option {i+1}"
            rb = QRadioButton(f"{label}:\n{opt}")
            rb.setStyleSheet("font-size: 13px; padding: 6px;")
            if i == 0: rb.setChecked(True)
            self.bg.addButton(rb, i)
            cl.addWidget(rb)
        self.options = options
        cl.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)
        btn_ok = QPushButton("✅ Use Selected")
        btn_ok.clicked.connect(self.on_ok)
        btn_ok.setStyleSheet("background: #a6e3a1; color: #1e1e2e;")
        layout.addWidget(btn_ok)

    def on_ok(self):
        idx = self.bg.checkedId()
        if 0 <= idx < len(self.options):
            self.selected_text = self.options[idx]
        self.accept()

# =========================================================
# Data Model
# =========================================================
import re
def get_row_tag(id_str, source_str):
    id_lower = id_str.lower()
    src_lower = source_str.lower()
    
    # 1. Characters
    if any(k in id_lower for k in ['npc', 'pc_', '_pc', 'chr', 'chara', 'name', 'actor']):
        return "👤 Char"
    if len(source_str) < 15 and " " not in source_str.strip() and source_str.istitle():
        return "👤 Char"
        
    # 2. Locations
    if any(k in id_lower for k in ['map', 'loc', 'zone', 'town', 'city', 'area', 'place']):
        return "🗺️ Loc"
        
    # 3. Items/Skills
    if any(k in id_lower for k in ['item', 'wpn', 'weapon', 'armor', 'equip', 'skill', 'magic', 'spell', 'desc', 'prop']):
        return "⚔️ Item"
        
    # 4. Quests
    if any(k in id_lower for k in ['quest', 'mission', 'task', 'objective', 'journal']):
        return "📜 Quest"
        
    # 5. System/UI
    if any(k in id_lower for k in ['sys', 'ui', 'menu', 'btn', 'button', 'lbl', 'label', 'title', 'msgbox', 'config']):
        return "⚙️ Sys"
        
    # 6. Dialogues
    if any(k in id_lower for k in ['talk', 'chat', 'msg', 'voice', 'event', 'dialog', 'scenario']):
        return "💬 Talk"
    if len(source_str) > 20 and any(p in source_str for p in ['. ', '? ', '! ', '...']):
        return "💬 Talk"
        
    return "❓"

class CsvTableModel(QAbstractTableModel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = []
        self.headers_row = []
        self.is_dirty = False
        self.headers = ['🏷️ Tag', 'ID', 'Source', 'AI Translation', 'Translation']

    def set_ai_column_name(self, name):
        self.headers[3] = name
        self.headerDataChanged.emit(Qt.Orientation.Horizontal, 3, 3)

    def load_csv(self, filepath, encoding, col_id, col_src, col_trans, col_ai):
        self.beginResetModel()
        self._data = []
        if not filepath or not os.path.exists(filepath):
            self.endResetModel()
            return 0
        max_col = max(col_id, col_src, col_trans, col_ai) + 1
        with open(filepath, 'r', encoding=encoding, errors='ignore') as f:
            reader = csv.reader(f)
            try:
                self.headers_row = next(reader)
            except StopIteration:
                self.headers_row = []
            try:
                for i, row in enumerate(reader):
                    while len(row) < max_col: row.append('')
                    ai_val = row[col_ai] if col_ai < len(row) else row[col_trans]
                    self._data.append({
                        "idx": i,
                        "id": row[col_id],
                        "source": row[col_src],
                        "trans": row[col_trans],
                        "ai_ref": ai_val if ai_val else row[col_trans]
                    })
            except Exception as e:
                print(f"Error reading CSV rows: {e}")
        self.is_dirty = False
        self.endResetModel()
        return len(self._data)

    def rowCount(self, parent=QModelIndex()): return len(self._data)
    def columnCount(self, parent=QModelIndex()): return 5

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.headers[section]
        return None

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid(): return None
        r, c = index.row(), index.column()
        item = self._data[r]
        if role == Qt.ItemDataRole.DisplayRole:
            if c == 0: return get_row_tag(item["id"], item["source"])
            if c == 1: return item["id"]
            if c == 2: return item["source"]
            if c == 3: return item["ai_ref"]
            if c == 4: return item["trans"]
        if role == Qt.ItemDataRole.ForegroundRole:
            if c == 0: return QColor('#cba6f7')
            if c == 1: return QColor('#89b4fa')
            if c == 3: return QColor('#f9e2af')
            if c == 4:
                if item["trans"]:
                    return QColor('#a6e3a1') if item["trans"] != item["ai_ref"] else QColor('#f9e2af')
                return QColor('#f38ba8')
        return None

    def update_trans(self, row, text):
        self._data[row]["trans"] = text
        self.is_dirty = True
        idx = self.index(row, 4)
        self.dataChanged.emit(idx, idx, [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.ForegroundRole])

class FilterProxy(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._search = ''
        self._mode = 0

    def set_search(self, text): self._search = text.lower(); self.invalidateFilter()
    def set_filter_mode(self, mode): self._mode = mode; self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        item = self.sourceModel()._data[source_row]
        tag = get_row_tag(item["id"], item["source"])
        
        if self._mode == 1 and item["trans"].strip(): return False
        if self._mode == 2 and not item["trans"].strip(): return False
        if self._mode == 3:
            src_len = len(item["source"])
            trans_len = len(item["trans"])
            if trans_len < 200: return False
            if src_len > 0 and (trans_len / src_len) > 4:
                pass
            else:
                return False
        if self._mode == 4:
            src = item["source"]
            src_lower = src.lower()
            import re
            has_quote = bool(re.search(r'["“”][^"“”]+["“”]', src))
            idiom_phrases = ['saying', 'proverb', 'poem', 'quote', 'they say', 'i think', 'phrase', 'metaphor', 'figure of speech', 'rhyme']
            has_idiom_word = any(w in src_lower for w in idiom_phrases)
            
            if has_quote or has_idiom_word:
                pass
            else:
                return False

        # Smart Filter Modes
        if self._mode == 5 and "Char" not in tag: return False
        if self._mode == 6 and "Loc" not in tag: return False
        if self._mode == 7 and "Item" not in tag: return False
        if self._mode == 8 and "Quest" not in tag: return False
        if self._mode == 9 and "Sys" not in tag: return False
        if self._mode == 10 and "Talk" not in tag: return False

        if self._search:
            return any(self._search in item[k].lower() for k in ["id", "source", "trans"])
        return True

# =========================================================
# Main Window
# =========================================================
class TranslationStudio(QMainWindow):
    def __init__(self):
        super().__init__()
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('flagship.tstudio.app.1.0')
        except:
            pass
        self.setWindowTitle(f'Translation Studio — {GAME_NAME}')
        self.setMinimumSize(1400, 800)
        self.setStyleSheet(DARK_SS)
        self.current_source_row = -1
        self.threadpool = QThreadPool()
        self.csv_path = CSV_PATH
        self.csv_encoding = CSV_ENCODING

        self.model = CsvTableModel(self)
        self.proxy = FilterProxy(self)
        self.proxy.setSourceModel(self.model)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)

        # ── Top Bar (Two Rows) ──
        top_layout = QVBoxLayout()
        top_layout.setSpacing(6)
        
        # Row 1: Profile & Configuration
        row1 = QHBoxLayout()
        logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "assets", "TStudio.png"))
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))
        self._is_loading_profiles = True
        self._profiles_data = TStudioCore.load_profiles()
        
        row1.addWidget(QLabel("🎮 Project Profile:"))
        self.cbo_profile = QComboBox()
        self.cbo_profile.setFixedWidth(160)
        self.cbo_profile.addItems(list(self._profiles_data["presets"].keys()))
        self.cbo_profile.setCurrentText(self._profiles_data["active_preset"])
        self.cbo_profile.currentTextChanged.connect(self.on_profile_changed)
        row1.addWidget(self.cbo_profile)
        
        btn_new_profile = QPushButton("➕ New")
        btn_new_profile.clicked.connect(self.create_new_profile)
        row1.addWidget(btn_new_profile)

        btn_rename_profile = QPushButton("✏️ Rename")
        btn_rename_profile.clicked.connect(self.rename_profile)
        row1.addWidget(btn_rename_profile)

        btn_del_profile = QPushButton("🗑️ Delete")
        btn_del_profile.setStyleSheet("color: #f38ba8;")
        btn_del_profile.clicked.connect(self.delete_profile)
        row1.addWidget(btn_del_profile)

        btn_import_prof = QPushButton("📥 Import")
        btn_import_prof.clicked.connect(self.import_profile)
        row1.addWidget(btn_import_prof)
        
        btn_export_prof = QPushButton("📤 Export")
        btn_export_prof.clicked.connect(self.export_profile)
        row1.addWidget(btn_export_prof)

        btn_merge = QPushButton('🧩 Merge Translated File')
        btn_merge.setStyleSheet("background: #cba6f7; color: #1e1e2e; font-weight: bold;")
        btn_merge.clicked.connect(self.open_merge_dialog)
        row1.addWidget(btn_merge)
        
        self._is_loading_profiles = False
        
        row1.addStretch()
        
        btn_glos = QPushButton('📖 Glossary')
        btn_glos.clicked.connect(self.open_glossary)
        row1.addWidget(btn_glos)
        
        btn_set = QPushButton('⚙️ Global Settings')
        btn_set.clicked.connect(self.open_settings)
        row1.addWidget(btn_set)
        
        top_layout.addLayout(row1)
        
        # Row 2: File Operations & Search
        row2 = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('🔍 Search text...')
        self.search_input.setFixedWidth(250)
        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(lambda: self.proxy.set_search(self.search_input.text()))
        self.search_input.textChanged.connect(lambda: self._search_timer.start(300))
        row2.addWidget(self.search_input)

        btn_fr = QPushButton('🔍 Find/Replace')
        btn_fr.clicked.connect(lambda: FindReplaceDialog(self).exec())
        row2.addWidget(btn_fr)

        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            'All Rows', '❓ Untranslated', '✅ Translated', '🤖 AI Hallucinations', '🎭 Quotes/Idioms',
            '👤 Characters', '🗺️ Locations', '⚔️ Items & Skills', '📜 Quests', '⚙️ System & UI', '💬 Dialogues'
        ])
        self.filter_combo.currentIndexChanged.connect(self.proxy.set_filter_mode)
        self.filter_combo.setFixedWidth(200) # Increased width for new categories
        row2.addWidget(self.filter_combo)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(220)
        self.progress_bar.setStyleSheet("QProgressBar { border: 1px solid #45475a; border-radius: 4px; text-align: center; color: #1e1e2e; font-weight: bold; background: #313244; } QProgressBar::chunk { background-color: #a6e3a1; border-radius: 3px; }")
        self.progress_bar.setFormat("No file loaded")
        self.progress_bar.setValue(0)
        row2.addWidget(self.progress_bar)
        
        row2.addStretch()
        
        btn_open = QPushButton('📂 Open File (Ctrl+O)')
        btn_open.setShortcut(QKeySequence('Ctrl+O'))
        btn_open.setObjectName('btnOpen')
        btn_open.clicked.connect(self.open_file_dialog)
        row2.addWidget(btn_open)

        btn_save = QPushButton('💾 Save CSV (Ctrl+S)')
        btn_save.setObjectName('btnSave')
        btn_save.clicked.connect(self.save_csv)
        row2.addWidget(btn_save)
        
        btn_export_pua = QPushButton('🧩 Export PUA')
        btn_export_pua.setStyleSheet("background: #cba6f7; color: #1e1e2e; font-weight: bold;")
        btn_export_pua.clicked.connect(self.export_pua_csv)
        row2.addWidget(btn_export_pua)

        btn_deploy = QPushButton('🚀 Deploy to Game')
        btn_deploy.setObjectName('btnDeploy')
        btn_deploy.setStyleSheet("background: #fab387; color: #1e1e2e; font-weight: bold;")
        btn_deploy.clicked.connect(self.deploy_to_game)
        row2.addWidget(btn_deploy)
        
        top_layout.addLayout(row2)
        
        root.addLayout(top_layout)

        # ── Splitter ──
        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.table = QTableView()
        self.table.setModel(self.proxy)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.selectionModel().currentChanged.connect(self.on_row_selected)
        splitter.addWidget(self.table)

        # ── Right Panel ──
        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(0, 0, 0, 0)

        grp1 = QGroupBox("🇬🇧 1. Original Source")
        l1 = QVBoxLayout(grp1)
        self.txt_source = QTextEdit()
        self.txt_source.setReadOnly(True)
        self.txt_source.setStyleSheet("background:#181825; color:#a6adc8;")
        l1.addWidget(self.txt_source)
        rl.addWidget(grp1)

        grp2 = QGroupBox("🤖 2. AI Translation (Reference)")
        l2 = QVBoxLayout(grp2)
        self.txt_ai = QTextEdit()
        self.txt_ai.setReadOnly(True)
        self.txt_ai.setStyleSheet("background:#181825; color:#f9e2af;")
        l2.addWidget(self.txt_ai)
        rl.addWidget(grp2)

        grp3 = QGroupBox("✍️ 3. My Translation (Edit Here)")
        l3 = QVBoxLayout(grp3)
        btn_row = QHBoxLayout()
        btn_prompts = QPushButton('⚙️ AI Prompts')
        btn_prompts.setStyleSheet("background:#313244; color:#a6adc8; font-size:12px; padding:4px 8px;")
        btn_prompts.clicked.connect(self.open_prompt_settings)
        btn_row.addWidget(btn_prompts)
        
        btn_row.addStretch()
        self.btn_trans_opt = QPushButton('🎯 Re-translate (3 Options)')
        self.btn_trans_opt.setStyleSheet("background:#f9e2af; color:#1e1e2e; font-size:12px; padding:4px 8px;")
        self.btn_trans_opt.clicked.connect(self.retranslate_options)
        btn_row.addWidget(self.btn_trans_opt)

        self.btn_trans_single = QPushButton('🤖 Re-translate (AI)')
        self.btn_trans_single.setObjectName('btnRetranslate')
        self.btn_trans_single.setStyleSheet("background:#89b4fa; color:#1e1e2e; font-size:12px; padding:4px 8px;")
        self.btn_trans_single.clicked.connect(self.retranslate_single)
        btn_row.addWidget(self.btn_trans_single)

        self.btn_trans_special = QPushButton('✨ แปลพิเศษ...')
        self.btn_trans_special.setStyleSheet("background:#a6e3a1; color:#1e1e2e; font-size:12px; padding:4px 8px;")
        menu = QMenu(self)
        
        action_idiom = menu.addAction("แปลเป็น วลี/สำนวน (Idiom)")
        action_poem = menu.addAction("แปลเป็น กลอน (Poem)")
        action_quote = menu.addAction("แปลเป็น คำพูดบุคคลสำคัญ (Quote)")
        
        action_idiom.triggered.connect(lambda: self.retranslate_special("idiom"))
        action_poem.triggered.connect(lambda: self.retranslate_special("poem"))
        action_quote.triggered.connect(lambda: self.retranslate_special("quote"))
        
        self.btn_trans_special.setMenu(menu)
        btn_row.addWidget(self.btn_trans_special)

        l3.addLayout(btn_row)
        self.txt_trans = QTextEdit()
        self.txt_trans.textChanged.connect(self.on_trans_changed)
        l3.addWidget(self.txt_trans)
        rl.addWidget(grp3)

        splitter.addWidget(right)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)
        root.addWidget(splitter)

        self.update_button_labels()
        
        if os.path.exists(self.csv_path):
            self._load_csv()

    def update_progress_stats(self):
        if not hasattr(self, 'model') or not self.model or not self.model._data:
            self.progress_bar.setFormat("No file loaded")
            self.progress_bar.setValue(0)
            return
            
        total = len(self.model._data)
        if total == 0:
            return
            
        import re
        translated_count = 0
        counts = {i: 0 for i in range(11)}
        counts[0] = total
        
        idiom_phrases = ['saying', 'proverb', 'poem', 'quote', 'they say', 'i think', 'phrase', 'metaphor', 'figure of speech', 'rhyme']

        for item in self.model._data:
            text = item["trans"]
            src = item["source"]
            tag = get_row_tag(item["id"], src)
            
            # Progress bar count
            if text and isinstance(text, str) and re.search(r'[ก-๙เแไใโ]', text):
                translated_count += 1
                
            # Mode 1: Untranslated
            if not text.strip(): counts[1] += 1
            # Mode 2: Translated
            if text.strip(): counts[2] += 1
            # Mode 3: AI Hallucinations
            src_len, trans_len = len(src), len(text)
            if trans_len >= 200 and src_len > 0 and (trans_len / src_len) > 4:
                counts[3] += 1
            # Mode 4: Quotes/Idioms
            src_lower = src.lower()
            if bool(re.search(r'["“”][^"“”]+["“”]', src)) or any(w in src_lower for w in idiom_phrases):
                counts[4] += 1
                
            # Modes 5-10: Smart Tags
            if "Char" in tag: counts[5] += 1
            if "Loc" in tag: counts[6] += 1
            if "Item" in tag: counts[7] += 1
            if "Quest" in tag: counts[8] += 1
            if "Sys" in tag: counts[9] += 1
            if "Talk" in tag: counts[10] += 1
            
        # Update combo box texts
        labels = [
            'All Rows', '❓ Untranslated', '✅ Translated', '🤖 AI Hallucinations', '🎭 Quotes/Idioms',
            '👤 Characters', '🗺️ Locations', '⚔️ Items & Skills', '📜 Quests', '⚙️ System & UI', '💬 Dialogues'
        ]
        self.filter_combo.blockSignals(True)
        for i in range(11):
            if i < self.filter_combo.count():
                self.filter_combo.setItemText(i, f"{labels[i]} ({counts[i]:,})")
        self.filter_combo.blockSignals(False)
                
        percent = int((translated_count / total) * 100) if total > 0 else 0
        self.progress_bar.setValue(percent)
        self.progress_bar.setFormat(f"แปลแล้ว {percent}% ({translated_count:,} / {total:,})")

    def changeEvent(self, event):
        if event.type() == event.Type.ActivationChange and self.isActiveWindow():
            self._reload_profiles_silently()
        super().changeEvent(event)

    def _reload_profiles_silently(self):
        if getattr(self, '_is_loading_profiles', False): return
        self._is_loading_profiles = True
        try:
            new_data = TStudioCore.load_profiles()
            current_text = self.cbo_profile.currentText()
            self.cbo_profile.blockSignals(True)
            self.cbo_profile.clear()
            self.cbo_profile.addItems(list(new_data["presets"].keys()))
            
            # Try to restore the previously selected active preset
            active = new_data.get("active_preset", "Default")
            if current_text in new_data["presets"]:
                self.cbo_profile.setCurrentText(current_text)
            elif active in new_data["presets"]:
                self.cbo_profile.setCurrentText(active)
            self.cbo_profile.blockSignals(False)
            self._profiles_data = new_data
        except Exception as e:
            print(f"Silent reload error: {e}")
        self._is_loading_profiles = False

    def open_glossary(self):
        GlossaryDialog(self).exec()
        self._profiles_data = TStudioCore.load_profiles()

    def open_prompt_settings(self):
        PromptSettingsDialog(self).exec()
        self._profiles_data = TStudioCore.load_profiles()

    def open_settings(self):
        SettingsDialog(self).exec()
        self.update_button_labels()

    def update_button_labels(self):
        cfg = TStudioCore.load_config()
        model = cfg.get("model", "")
        if model.startswith("gemini"):
            self.btn_trans_single.setText("🤖 Re-translate (Gemini)")
            self.btn_trans_single.setStyleSheet("background:#a6e3a1; color:#1e1e2e; font-size:12px; padding:4px 8px;")
        elif model.startswith("claude"):
            self.btn_trans_single.setText("🤖 Re-translate (Claude)")
            self.btn_trans_single.setStyleSheet("background:#fab387; color:#1e1e2e; font-size:12px; padding:4px 8px;")
        elif model.startswith("deepseek"):
            self.btn_trans_single.setText("🤖 Re-translate (DeepSeek)")
            self.btn_trans_single.setStyleSheet("background:#89b4fa; color:#1e1e2e; font-size:12px; padding:4px 8px;")
        elif model == "custom-local-llm" or model == "Local LLM":
            self.btn_trans_single.setText("🖥️ Re-translate (Local AI)")
            self.btn_trans_single.setStyleSheet("background:#cba6f7; color:#1e1e2e; font-size:12px; padding:4px 8px;")
        else:
            self.btn_trans_single.setText("🤖 Re-translate (OpenAI)")
            self.btn_trans_single.setStyleSheet("background:#89b4fa; color:#1e1e2e; font-size:12px; padding:4px 8px;")


    def rename_profile(self):
        active = self.cbo_profile.currentText()
        if active == "Default":
            QMessageBox.warning(self, "Warning", "Cannot rename the Default profile.")
            return
            
        from PyQt6.QtWidgets import QInputDialog
        new_name, ok = QInputDialog.getText(self, "Rename Profile", f"Enter new name for '{active}':", text=active)
        if ok and new_name.strip():
            new_name = new_name.strip()
            if new_name == active:
                return
            if new_name in self._profiles_data["presets"]:
                QMessageBox.warning(self, "Warning", f"Profile '{new_name}' already exists.")
                return
                
            self._profiles_data["presets"][new_name] = self._profiles_data["presets"].pop(active)
            self._profiles_data["active_preset"] = new_name
            TStudioCore.save_profiles(self._profiles_data)
            
            self._is_loading_profiles = True
            idx = self.cbo_profile.currentIndex()
            self.cbo_profile.setItemText(idx, new_name)
            self.cbo_profile.setCurrentText(new_name)
            self._is_loading_profiles = False
            self.statusBar().showMessage(f"Profile renamed to '{new_name}'.", 3000)

    def delete_profile(self):
        active = self.cbo_profile.currentText()
        if active == "Default":
            QMessageBox.warning(self, "Warning", "Cannot delete the Default profile.")
            return
            
        reply = QMessageBox.question(self, 'Confirm Delete', f"Are you sure you want to delete profile '{active}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            del self._profiles_data["presets"][active]
            self._profiles_data["active_preset"] = "Default"
            TStudioCore.save_profiles(self._profiles_data)
            self._is_loading_profiles = True
            self.cbo_profile.clear()
            self.cbo_profile.addItems(list(self._profiles_data["presets"].keys()))
            self.cbo_profile.setCurrentText("Default")
            self._is_loading_profiles = False
            self.statusBar().showMessage(f"Profile '{active}' deleted.", 3000)

    def export_profile(self):
        active = self.cbo_profile.currentText()
        data = self._profiles_data["presets"][active]
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Profile", f"{active}_profile.json", "JSON Files (*.json)")
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            self.statusBar().showMessage(f"Profile exported to {file_path}", 3000)

    def import_profile(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Import Profile", "", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if "single" not in data or "opt" not in data or "glossary" not in data:
                    QMessageBox.warning(self, "Invalid File", "The selected JSON file is not a valid profile format.")
                    return
                    
                from PyQt6.QtWidgets import QInputDialog
                name, ok = QInputDialog.getText(self, "Import Profile", "Enter name for imported profile:")
                if ok and name.strip():
                    name = name.strip()
                    self._profiles_data["presets"][name] = data
                    self._is_loading_profiles = True
                    if self.cbo_profile.findText(name) == -1:
                        self.cbo_profile.addItem(name)
                    self.cbo_profile.setCurrentText(name)
                    self.on_profile_changed(name)
                    self._is_loading_profiles = False
                    self.statusBar().showMessage(f"Profile '{name}' imported.", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to import profile:\n{e}")

    def on_profile_changed(self, text):
        if self._is_loading_profiles or not text: return
        self._profiles_data["active_preset"] = text
        TStudioCore.save_profiles(self._profiles_data)
        self.statusBar().showMessage(f"Switched to profile: {text}", 3000)

    def create_new_profile(self):
        from PyQt6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "New Profile", "Enter new profile name:")
        if ok and name.strip():
            name = name.strip()
            if name not in self._profiles_data["presets"]:
                self._profiles_data["presets"][name] = {"single": "", "opt": "", "glossary": {}}
                self._is_loading_profiles = True
                self.cbo_profile.addItem(name)
                self.cbo_profile.setCurrentText(name)
                self._is_loading_profiles = False
                self.on_profile_changed(name)
            else:
                self.cbo_profile.setCurrentText(name)

    def _load_csv(self):
        count = self.model.load_csv(self.csv_path, self.csv_encoding, COL_ID, COL_SOURCE, COL_TRANS, COL_AI_REF)
        self.setWindowTitle(f'Translation Studio — {GAME_NAME}')
        self.statusBar().showMessage(f'Loaded {count:,} entries from {os.path.basename(self.csv_path)}')
        self.update_progress_stats()

    def open_merge_dialog(self):
        dlg = MergeTranslatedDialog(self)
        if dlg.exec():
            if dlg.merged_csv_path and os.path.exists(dlg.merged_csv_path):
                self.csv_path = dlg.merged_csv_path
                self._load_csv()
                self.model.set_ai_column_name("Merge Translation")
                self.statusBar().showMessage(f"Loaded merged file: {os.path.basename(self.csv_path)}", 5000)

    def open_file_dialog(self):
        if hasattr(self, 'model') and getattr(self.model, 'is_dirty', False):
            reply = QMessageBox.question(self, 'Unsaved Changes', "You have unsaved translations. Do you want to save before opening a new file?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
            if reply == QMessageBox.StandardButton.Yes:
                self.save_csv()
            elif reply == QMessageBox.StandardButton.Cancel:
                return

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Translation File",
            BASE_DIR,
            "Supported Files (*.csv *.lor *.locres *.tex *.bundle *.txt *.*);;CSV Files (*.csv);;Locres Files (*.locres *.lor);;Texture Files (*.tex);;Unity Bundles (*.bundle *.txt *.*);;All Files (*.*)"
        )
        if file_path:
            self.statusBar().showMessage("Loading and Converting file... Please wait.")
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            
            def run_convert():
                try:
                    from tbundle_manager import TBundleManager
                    if TBundleManager.is_unity_bundle(file_path):
                        csv_out = TBundleManager.extract_text_to_csv(file_path)
                        if csv_out:
                            return csv_out
                except Exception as e:
                    print(f"Bundle extract error: {e}")
                return file_converter.auto_convert_to_csv(file_path, None) # Don't pass UI to thread
                
            def on_success(converted_path):
                QApplication.restoreOverrideCursor()
                if converted_path:
                    from tstudio_core import TFormatManager
                    if not TFormatManager.is_standard_csv(converted_path):
                        headers = TFormatManager.get_headers(converted_path)
                        from tstudio_ui_shared import SmartImportDialog
                        dlg = SmartImportDialog(headers, self)
                        if dlg.exec() == QDialog.DialogCode.Accepted:
                            mapping = dlg.get_mapping()
                            try:
                                converted_path = TFormatManager.format_to_standard(converted_path, mapping)
                                QMessageBox.information(self, "TFormat", "File has been formatted to standard.")
                            except Exception as e:
                                QMessageBox.critical(self, "Error", f"Failed to format: {e}")
                                return
                        else:
                            return
                    self.csv_path = converted_path
                    self._load_csv()
                    
            def on_error(err):
                QApplication.restoreOverrideCursor()
                QMessageBox.critical(self, "File Error", f"Failed to open or convert file:\\n{err}")
                
            worker = ApiWorker(run_convert)
            worker.signals.finished.connect(on_success)
            worker.signals.error.connect(on_error)
            self.threadpool.start(worker)

    def on_row_selected(self, current, previous):
        if not current.isValid(): return
        src = self.proxy.mapToSource(current)
        self.current_source_row = src.row()
        item = self.model._data[self.current_source_row]
        for w, val in [(self.txt_source, item["source"]), (self.txt_ai, item["ai_ref"]), (self.txt_trans, item["trans"])]:
            w.blockSignals(True)
            w.setPlainText(val.replace('\\n', '\n'))
            w.blockSignals(False)

    def on_trans_changed(self):
        if self.current_source_row >= 0:
            self.model.update_trans(self.current_source_row, self.txt_trans.toPlainText().replace('\n', '\\n'))
            self.update_progress_stats()

    def _load_api_config(self):
        try:
            return TStudioCore.load_config()
        except Exception as e:
            print(f"Error loading API config: {e}")
            return {
                "google_key": "", "anthropic_key": "", "deepseek_key": "", "openai_key": "",
                "model": "deepseek-chat", "local_url": "http://localhost:1234/v1/chat/completions"
            }

    def _call_translation_api(self, cfg, prompt, is_local=False):
        model = cfg["model"]
        if is_local:
            model = "custom-local-llm"
            
        if model != "custom-local-llm" and model != "Local LLM":
            if model.startswith("gemini") and not cfg.get("google_key"):
                raise Exception("Google Gemini API Key is missing! Please configure it in Settings.")
            elif model.startswith("claude") and not cfg.get("anthropic_key"):
                raise Exception("Anthropic Claude API Key is missing! Please configure it in Settings.")
            elif model.startswith("deepseek") and not cfg.get("deepseek_key"):
                raise Exception("DeepSeek API Key is missing! Please configure it in Settings.")
            elif not model.startswith("gemini") and not model.startswith("claude") and not model.startswith("deepseek") and not cfg.get("openai_key"):
                raise Exception("OpenAI API Key is missing! Please configure it in Settings.")

        if model.startswith("gemini"):
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={cfg['google_key']}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.3}
            }
            res = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=30)
            if res.status_code == 200:
                return res.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
            raise Exception(f"Gemini API Error {res.status_code}: {res.text}")

        elif model.startswith("claude"):
            url = "https://api.anthropic.com/v1/messages"
            headers = {"x-api-key": cfg["anthropic_key"], "anthropic-version": "2023-06-01", "content-type": "application/json"}
            payload = {
                "model": model, "max_tokens": 4096, "temperature": 0.3,
                "messages": [{"role": "user", "content": prompt}]
            }
            res = requests.post(url, json=payload, headers=headers, timeout=30)
            if res.status_code == 200:
                return res.json()["content"][0]["text"].strip()
            raise Exception(f"Claude API Error {res.status_code}: {res.text}")

        else:
            actual_model = model
            url = "https://api.openai.com/v1/chat/completions"
            api_key = cfg["openai_key"]

            if model.startswith("deepseek"):
                url = "https://api.deepseek.com/chat/completions"
                api_key = cfg["deepseek_key"]
            elif model == "custom-local-llm" or model == "Local LLM":
                url = cfg["local_url"]
                actual_model = "local-model"
                api_key = "dummy"

            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            payload = {
                "model": actual_model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3, "max_tokens": 8192
            }
            res = requests.post(url, json=payload, headers=headers, timeout=120 if is_local else 30)
            if res.status_code == 200:
                return res.json()['choices'][0]['message']['content'].strip()
            raise Exception(f"API Error {res.status_code}: {res.text}")

    def _apply_glossary(self, text):
        profile = TStudioCore.get_current_profile_data()
        for wrong, right in profile.get("glossary", {}).items():
            text = text.replace(wrong, right)
        return text

    def _inject_glossary_to_prompt(self, prompt, source_text):
        profile = TStudioCore.get_current_profile_data()
        glossary = profile.get("glossary", {})
            
        matched_terms = []
        source_lower = source_text.lower()
        
        for eng, thai in glossary.items():
            eng_str = eng.strip()
            if not eng_str: continue
            
            pattern = r'\b' + re.escape(eng_str.lower()) + r'\b'
            if re.search(pattern, source_lower):
                matched_terms.append(f"- {eng_str} -> {thai}")
                
        if matched_terms:
            rules = "\n\nCRITICAL TERMINOLOGY RULES:\nYou MUST use the following specific translations for these terms:\n" + "\n".join(matched_terms)
            return prompt + rules
            
        return prompt

    def retranslate_single(self):
        if self.current_source_row < 0: return
        item = self.model._data[self.current_source_row]
        if not item["source"].strip(): return
        cfg = TStudioCore.load_config()
        self.statusBar().showMessage("Translating...")
        self.btn_trans_single.setEnabled(False)
        source_text = item["source"].replace('\\n', '\n')
        
        profile = TStudioCore.get_current_profile_data()
        s_prompt = profile.get('single', DEFAULT_SINGLE_PROMPT)
        prompt = s_prompt.replace('{id}', item["id"]).replace('{source_text}', source_text)
        prompt = self._inject_glossary_to_prompt(prompt, source_text)

        worker = ApiWorker(CoreAI.generate_content, cfg, prompt)
        worker.signals.finished.connect(self._on_single_success)
        worker.signals.error.connect(lambda err: self._on_retranslate_error(err, self.btn_trans_single))
        self.threadpool.start(worker)

    def _on_single_success(self, reply):
        self.btn_trans_single.setEnabled(True)
        translated = self._apply_glossary(re.sub(r'^"|"$', '', reply))
        self.txt_trans.setPlainText(translated)
        self.statusBar().showMessage("Re-translated!", 3000)

    def _on_retranslate_error(self, err_msg, btn):
        btn.setEnabled(True)
        QMessageBox.critical(self, "Failed", str(err_msg))
        self.statusBar().showMessage("Translation Failed", 3000)

    def retranslate_special(self, mode):
        if self.current_source_row < 0: return
        item = self.model._data[self.current_source_row]
        if not item["source"].strip(): return
        cfg = TStudioCore.load_config()
        self.statusBar().showMessage(f"Translating ({mode})...")
        self.btn_trans_special.setEnabled(False)
        source_text = item["source"].replace('\\n', '\n')
        
        mode_text = ""
        if mode == "idiom":
            mode_text = "Analyze the underlying meaning of this phrase carefully. It is likely an idiom or metaphor. Translate it into a natural-sounding, contextually appropriate Thai idiom or phrase (วลี/สำนวน), rather than a literal word-for-word translation."
        elif mode == "poem":
            mode_text = "This text is a poem, song, or rhythmic chant. Translate it into an elegant Thai poetic form (กลอน/คำคล้องจอง) with appropriate rhyming and literary vocabulary, while preserving the original meaning."
        elif mode == "quote":
            mode_text = "This text is a profound quote or proverb. Translate it into formal, philosophical, and impactful Thai language (คำคม/คำพูดบุคคลสำคัญ), similar to how a famous historical figure would speak."
            
        prompt = f"You are a Master-Level English-to-Thai Video Game Localization Specialist for '{GAME_NAME}'.\n{mode_text}\nID: '{item['id']}'. Return ONLY the pure Thai string, no quotes, no explanations.\n\nEnglish: {source_text}"
        prompt = self._inject_glossary_to_prompt(prompt, source_text)
        
        worker = ApiWorker(CoreAI.generate_content, cfg, prompt)
        # Using a lambda to pass 'mode' to the success handler
        worker.signals.finished.connect(lambda reply: self._on_special_success(reply, mode))
        worker.signals.error.connect(lambda err: self._on_retranslate_error(err, self.btn_trans_special))
        self.threadpool.start(worker)

    def _on_special_success(self, reply, mode):
        self.btn_trans_special.setEnabled(True)
        translated = self._apply_glossary(re.sub(r'^"|"$', '', reply))
        self.txt_trans.setPlainText(translated)
        self.statusBar().showMessage(f"Re-translated as {mode}!", 3000)

    def retranslate_options(self):
        if self.current_source_row < 0: return
        item = self.model._data[self.current_source_row]
        if not item["source"].strip(): return
        cfg = TStudioCore.load_config()
        self.statusBar().showMessage("Fetching 3 options...")
        self.btn_trans_opt.setEnabled(False)
        source_text = item["source"].replace('\\n', '\n')
        
        profile = TStudioCore.get_current_profile_data()
        o_prompt = profile.get('opt', DEFAULT_OPTIONS_PROMPT)
        prompt = o_prompt.replace('{id}', item["id"]).replace('{source_text}', source_text)
        prompt = self._inject_glossary_to_prompt(prompt, source_text)

        worker = ApiWorker(CoreAI.generate_content, cfg, prompt)
        worker.signals.finished.connect(self._on_options_success)
        worker.signals.error.connect(lambda err: self._on_retranslate_error(err, self.btn_trans_opt))
        self.threadpool.start(worker)

    def _on_options_success(self, reply):
        self.btn_trans_opt.setEnabled(True)
        clean_reply = re.sub(r'^```[^\n]*\n?|\n?```$', '', reply.strip(), flags=re.MULTILINE)
        try:
            options = json.loads(clean_reply)
            if not isinstance(options, list) or len(options) == 0: raise ValueError()
        except:
            QMessageBox.warning(self, "Parse Error", f"AI returned invalid format:\n{reply}")
            return
        options = [self._apply_glossary(o) for o in options]
        dlg = TranslationOptionsDialog(self, options)
        if dlg.exec() and dlg.selected_text:
            self.txt_trans.setPlainText(dlg.selected_text)
        self.statusBar().showMessage("Done.", 3000)

    def retranslate_local(self):
        if self.current_source_row < 0: return
        item = self.model._data[self.current_source_row]
        if not item["source"].strip(): return
        cfg = TStudioCore.load_config()
        self.statusBar().showMessage("Translating with Local AI...")
        source_text = item["source"].replace('\\n', '\n')
        
        profile = TStudioCore.get_current_profile_data()
        s_prompt = profile.get('single', DEFAULT_SINGLE_PROMPT)
        prompt = s_prompt.replace('{id}', item["id"]).replace('{source_text}', source_text)

        worker = ApiWorker(CoreAI.generate_content, cfg, prompt, is_local=True)
        worker.signals.finished.connect(lambda reply: self._on_local_success(reply))
        worker.signals.error.connect(lambda err: self._on_local_error(err))
        self.threadpool.start(worker)

    def _on_local_success(self, reply):
        translated = self._apply_glossary(re.sub(r'^"|"$', '', reply))
        self.txt_trans.setPlainText(translated)
        self.statusBar().showMessage("Re-translated with Local AI!", 3000)

    def _on_local_error(self, err):
        QMessageBox.critical(self, "Failed", f"Is your Local LLM running?\n\nError: {err}")


    def export_pua_csv(self):
        if not self.csv_path:
            QMessageBox.warning(self, "Error", "CSV_PATH not configured!")
            return
            
        pua_path = self.csv_path.replace(".csv", "_PUA.csv")
        try:
            tpua = TPUAEngine()
            
            # Count PUA characters generated
            original_pua_count = 0
            final_pua_count = 0
            
            with open(pua_path, 'w', encoding=self.csv_encoding, newline='') as f:
                import csv
                writer = csv.writer(f)
                if self.model.headers_row:
                    writer.writerow(self.model.headers_row)
                for item in self.model._data:
                    row = [''] * (max(COL_ID, COL_SOURCE, COL_TRANS, COL_AI_REF) + 1)
                    row[COL_ID] = item["id"]
                    row[COL_SOURCE] = item["source"]
                    
                    orig_trans = item["trans"]
                    original_pua_count += sum(1 for c in orig_trans if 0xF000 <= ord(c) <= 0xF8FF)
                    
                    pua_trans = tpua.encode(orig_trans)
                    final_pua_count += sum(1 for c in pua_trans if 0xF000 <= ord(c) <= 0xF8FF)
                    
                    row[COL_TRANS] = pua_trans
                    
                    if COL_AI_REF < len(row): row[COL_AI_REF] = item.get("ai_ref", "")
                    writer.writerow(row)
            
            diff = final_pua_count - original_pua_count
            QMessageBox.information(self, "Exported PUA", f"Successfully exported to:\n{os.path.basename(pua_path)}\n\nReplaced +{diff} PUA characters.")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))

    def export_original(self):
        if not getattr(self, 'csv_path', None):
            QMessageBox.warning(self, "No File", "Please open a file first.")
            return
            
        try:
            from tbundle_manager import TBundleManager
            base_dir = os.path.dirname(self.csv_path)
            json_path = os.path.join(base_dir, f"{os.path.basename(self.csv_path).replace('.csv', '')}_meta.json")
            if os.path.exists(json_path):
                self.save_csv() # Auto save before deploy
                success, msg_or_path = TBundleManager.deploy_csv_to_bundle(self.csv_path)
                if success:
                    QMessageBox.information(self, "Deploy Success", f"Deployed successfully back to Unity Bundle:\\n{msg_or_path}")
                else:
                    QMessageBox.warning(self, "Deploy Failed", msg_or_path)
                return
        except Exception as e:
            pass

        from tstudio_core import TFormatManager
        success, msg_or_path = TFormatManager.export_original(self.csv_path)
        if success:
            QMessageBox.information(self, "Export Success", f"Exported successfully to:\\n{msg_or_path}")
        else:
            QMessageBox.warning(self, "Export Failed", msg_or_path)

    def save_csv(self):

        if not self.csv_path:
            QMessageBox.warning(self, "Error", "CSV_PATH not configured!")
            return
        try:
            with open(self.csv_path, 'w', encoding=self.csv_encoding, newline='') as f:
                writer = csv.writer(f)
                if self.model.headers_row:
                    writer.writerow(self.model.headers_row)
                for item in self.model._data:
                    row = [''] * (max(COL_ID, COL_SOURCE, COL_TRANS, COL_AI_REF) + 1)
                    row[COL_ID] = item["id"]
                    row[COL_SOURCE] = item["source"]
                    row[COL_TRANS] = item["trans"]
                    if COL_AI_REF < len(row): row[COL_AI_REF] = item["ai_ref"]
                    writer.writerow(row)
            self.statusBar().showMessage('Saved!', 5000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save:\n{e}")

    def deploy_to_game(self):
        retail_path, _ = QFileDialog.getSaveFileName(self, "Select JSON file to Deploy", "", "JSON Files (*.json)")
        if not retail_path:
            return
            
        reply = QMessageBox.question(self, "Deploy", f"Are you sure you want to deploy to:\n{retail_path}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.save_csv()  # Save CSV first
            
            # Export to JSON dictionary for the game
            game_dict = {}
            for item in self.model._data:
                # Need to convert escaped \n back to actual newlines for the game
                key = item["id"].replace('\\n', '\n')
                trans = item["trans"].replace('\\n', '\n')
                ai_ref = item["ai_ref"].replace('\\n', '\n')
                source = item["source"].replace('\\n', '\n')
                
                # Use human translation if available, else AI reference
                final_text = trans if trans.strip() else ai_ref
                
                # Fallback to original English if neither is available
                if not final_text.strip():
                    final_text = source
                    
                game_dict[key] = final_text
                
            try:
                # Save as utf-8-sig if required by the game engine
                tmp_file = retail_path + ".tmp"
                with open(tmp_file, 'w', encoding='utf-8-sig') as f:
                    json.dump(game_dict, f, ensure_ascii=False, indent=4)
                
                if os.path.exists(tmp_file):
                    os.replace(tmp_file, retail_path)
                    
                QMessageBox.information(self, "Success", f"Deployed {len(game_dict):,} strings to game successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to deploy:\n{e}")

    def closeEvent(self, event):
        if hasattr(self, 'model') and getattr(self.model, 'is_dirty', False):
            reply = QMessageBox.question(self, 'Unsaved Changes', "You have unsaved translations. Do you want to save before exiting?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
            if reply == QMessageBox.StandardButton.Yes:
                self.save_csv()
                event.accept()
            elif reply == QMessageBox.StandardButton.No:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    win = TranslationStudio()
    win.show()
    sys.exit(app.exec())
