from tstudio_i18n import _
# -*- coding: utf-8 -*-
"""
Translation_Studio_Template.py
===============================
Universal Translation Studio Template
Adapted from the Studio Template to handle CSV and direct JSON deployment.
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Core')))
import csv
import sys
csv.field_size_limit(2147483647)
import html
import json
import requests
import re
import file_converter
from tpua_engine import TPUAEngine
from tstudio_core import TStudioCore, CoreAI
from tstudio_telltale import TelltaleManager
from tstudio_ui_shared import SettingsDialog, PromptSettingsDialog, GlossaryWidget, ApiWorker, ThreadSafeWorkerSignalsForwarder

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableView, QHeaderView, QLabel, QPushButton, QLineEdit,
    QSplitter, QGroupBox, QComboBox, QMessageBox, QTextEdit,
    QAbstractItemView, QDialog, QFormLayout, QTableWidget,
    QTableWidgetItem, QRadioButton, QButtonGroup, QScrollArea,
    QFileDialog, QMenu, QSpinBox, QProgressBar, QDockWidget, QMenuBar, QSizePolicy, QToolButton, QCheckBox
)
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex, QSortFilterProxyModel, QTimer, QRunnable, QThreadPool, pyqtSignal, pyqtSlot, QObject
from PyQt6.QtGui import QColor, QKeySequence, QShortcut, QIcon, QPixmap, QAction
from flow_layout import FlowLayout

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

STRICT LENGTH & CONTENT RULES (NON-NEGOTIABLE):
- Your translation MUST match the length and structure of the source text as closely as possible.
- If the source is a short UI label (e.g. 'ID:', 'Rank', 'Mass'), return ONLY its short Thai equivalent. Do NOT write a full sentence.
- If the source is 1-3 words, return 1-5 words maximum.
- Do NOT expand, elaborate, invent, or add any content that is not explicitly in the source text.
- Do NOT use your knowledge of the game's story or lore to add context or flavor text.
- Do NOT add colons, notes, parentheses, backstory, or any extra characters not present in the source.

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
QMainWindow::separator { background: #45475a; width: 6px; height: 6px; }
QMainWindow::separator:hover { background: #89b4fa; }
"""

# Duplicates removed, now imported from tstudio_ui_shared.py

import os
import csv
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QGroupBox, QHBoxLayout, QPushButton, QLineEdit, QMessageBox, QApplication, QFileDialog
from PyQt6.QtCore import Qt

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
        path, _ext = QFileDialog.getOpenFileName(self, "Select Original File", "", "Supported Files (*.csv *.lor *.locres *.tex *.bundle *.txt *.json)")
        if path: self.txt_orig.setText(path)
            
    def browse_trans(self):
        path, _ext = QFileDialog.getOpenFileName(self, "Select Translated File", "", "Supported Files (*.csv *.lor *.locres *.tex *.bundle *.txt *.json)")
        if path: self.txt_trans.setText(path)
            
    def browse_save(self):
        path, _ext = QFileDialog.getSaveFileName(self, "Select Output CSV", "", "CSV Files (*.csv)")
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
                    writer.writerow([_("col_id"), _("col_source"), _("col_translation"), 'AI Reference'])
                    
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
        self.setFixedSize(420, 150)
        layout = QFormLayout(self)
        self.txt_find = QLineEdit()
        self.txt_replace = QLineEdit()
        layout.addRow(_("find_label"), self.txt_find)
        layout.addRow(_("replace_with_label"), self.txt_replace)
        btn = QPushButton(_("replace_all_btn"))
        btn.setToolTip(_("tooltip_btn"))
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
            QMessageBox.information(self, _("success_title"), _("replaced_count_msg"))
        else:
            QMessageBox.information(self, _("not_found_title"), _("no_matches_msg"))

# =========================================================
# UI: Translation 3 Options (Moved to tstudio_ui_shared.py)
# =========================================================
from tstudio_ui_shared import TranslationOptionsDialog

# =========================================================
# Data Model
# =========================================================
import re
def get_row_tag(id_str, source_str):
    id_lower = id_str.lower()
    src_lower = source_str.lower()
    
    # 1. Characters
    if any(k in id_lower for k in ['npc', 'pc_', '_pc', 'chr', 'chara', 'name', 'actor', 'enemy', 'boss', 'mob']):
        return "👤 Char"
    if len(source_str) < 20 and " " not in source_str.strip() and source_str.istitle():
        return "👤 Char"
    if len(source_str) < 30 and any(k in src_lower for k in ['mr.', 'mrs.', 'ms.', 'lord ', 'lady ']) and source_str.istitle():
        return "👤 Char"
        
    # 2. Locations
    if any(k in id_lower for k in ['map', 'loc', 'zone', 'town', 'city', 'area', 'place', 'dungeon', 'room', 'stage', 'level', 'world']):
        return "🗺️ Loc"
        
    # 3. Items/Skills
    if any(k in id_lower for k in ['item', 'wpn', 'weapon', 'armor', 'equip', 'skill', 'magic', 'spell', 'desc', 'prop', 'consumable', 'material', 'craft', 'acc']):
        return "⚔️ Item"
    if any(k in source_str for k in ['HP', 'MP', 'ATK', 'DEF', 'Lv.', 'EXP', 'Cooldown', 'Damage', 'Heal']):
        return "⚔️ Item"
        
    # 4. Quests
    if any(k in id_lower for k in ['quest', 'mission', 'task', 'objective', 'journal', 'diary', 'log', 'bounty', 'hunt']):
        return "📜 Quest"
        
    # 5. System/UI
    if any(k in id_lower for k in ['sys', 'ui', 'menu', 'btn', 'button', 'lbl', 'label', 'title', 'msgbox', 'config', 'option', 'save', 'load']):
        return "⚙️ Sys"
    if len(source_str) < 25 and not any(p in source_str for p in ['. ', '? ', '! ']) and any(k in src_lower for k in ['press', 'select', 'cancel', 'back', 'confirm', 'option', 'save', 'load']):
        return "⚙️ Sys"
    if len(source_str) < 15 and re.search(r'[%#@&$+^0-9]', source_str):
        return "⚙️ Sys"
        
    # 6. Dialogues
    if any(k in id_lower for k in ['talk', 'chat', 'msg', 'voice', 'event', 'dialog', 'scenario', 'cutscene', 'movie', 'tutorial']):
        return "💬 Talk"
    if len(source_str) > 20 and any(p in source_str for p in ['. ', '? ', '! ', '...']):
        return "💬 Talk"
    if re.search(r'["\'\[\]()]', source_str) and len(source_str) > 10:
        return "💬 Talk"
        
    return "❓"

from PyQt6.QtWidgets import QStyledItemDelegate, QStyle
from PyQt6.QtGui import QTextDocument, QAbstractTextDocumentLayout
from PyQt6.QtCore import QSize

class HtmlDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.doc = QTextDocument()
        self.doc.setDefaultStyleSheet("body { color: #cdd6f4; font-family: inherit; font-size: 13px; }")
        self.doc.setDocumentMargin(4)

    def paint(self, painter, option, index):
        from PyQt6.QtWidgets import QStyleOptionViewItem
        options = QStyleOptionViewItem(option)
        self.initStyleOption(options, index)

        painter.save()
        
        # Draw background
        bg = index.data(Qt.ItemDataRole.BackgroundRole)
        if bg:
            painter.fillRect(option.rect, bg)
            
        # Draw selection
        if option.state & QStyle.StateFlag.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())

        text = options.text
        # if text does not contain HTML tags, escape it to avoid parsing issues?
        # In our case, the html_source has tags. If not, it's plain text.
        if "<span" not in text:
            # simple escape
            text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            
        self.doc.setHtml(f"<body>{text}</body>")

        painter.translate(option.rect.left(), option.rect.top())
        clip = option.rect.translated(-option.rect.left(), -option.rect.top())
        painter.setClipRect(clip)

        ctx = QAbstractTextDocumentLayout.PaintContext()
        ctx.palette = option.palette
        self.doc.documentLayout().draw(painter, ctx)
        painter.restore()

    def sizeHint(self, option, index):
        options = option
        self.initStyleOption(options, index)
        text = options.text
        if "<span" not in text:
            text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        self.doc.setHtml(text)
        return QSize(int(self.doc.idealWidth()), 30)

class CsvTableModel(QAbstractTableModel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = parent
        self._data = []
        self.headers_row = []
        self.is_dirty = False
        self.is_qa_enabled = False
        self.headers = [_("col_tag"), _("col_id"), _("col_source"), _("col_ai_translation"), _("col_translation")]

    def set_ai_column_name(self, name):
        self.headers[3] = name
        self.headerDataChanged.emit(Qt.Orientation.Horizontal, 3, 3)

    def load_csv(self, filepath, encoding, col_id, col_src, col_trans, col_ai):
        self.beginResetModel()
        self.headers[3] = _("col_ai_translation")
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
                    
                    # Pre-calculate tag and idiom for performance
                    tag_val = get_row_tag(row[col_id], row[col_src])
                    src_lower = row[col_src].lower()
                    has_quote = bool(re.search(r'["“”][^"“”]+["“”]', row[col_src]))
                    idiom_phrases = ['saying', 'proverb', 'poem', 'quote', 'they say', 'i think', 'phrase', 'metaphor', 'figure of speech', 'rhyme']
                    has_idiom = has_quote or any(w in src_lower for w in idiom_phrases)
                    trans_text = row[col_trans]
                    is_th_val = bool(re.search(r'[ก-๙เแไใโ]', trans_text)) if trans_text else False
                    
                    
                    # Clean up any legacy QA FAILED tags saved in the CSV
                    if "QA FAILED" in tag_val:
                        cleaned_tags = [t.strip() for t in tag_val.split(",") if t.strip() and "QA FAILED" not in t]
                        tag_val = ", ".join(cleaned_tags)
                        
                    self._data.append({
                        "idx": i,
                        "id": row[col_id],
                        "source": row[col_src],
                        "trans": trans_text,
                        "ai_ref": ai_val if ai_val else trans_text,
                        "tag": tag_val,
                        "qa_failed": False,
                        "is_idiom": has_idiom,
                        "is_th": is_th_val
                    })
            except Exception as e:
                print(f"Error reading CSV rows: {e}")
        # TS-W2: track whether any QA FAILED tags were cleaned; don't override with False
        cleaned_any = any(
            "QA FAILED" in item.get("tag", "") for item in []
        )  # placeholder — actual cleaning tracked below
        # Re-scan: mark dirty only if any trans had 'QA FAILED' text
        cleaned_any = False
        for item in self._data:
            if 'QA FAILED' in item.get('trans', ''):
                item['trans'] = item['trans'].replace('QA FAILED - ', '').replace(' - QA FAILED', '').strip()
                cleaned_any = True
        self.is_dirty = cleaned_any
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
        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            if c == 0: return item.get("tag", "❓")
            if c == 1: return item["id"]
            if c == 2:
                if (hasattr(self, 'app')
                    and hasattr(self.app, 'act_toggle_qa_marker')
                    and self.app.act_toggle_qa_marker.isChecked()
                    and 'html_source' in item):
                    return item['html_source']
                return item["source"]
            if c == 3: return item.get("ai_ref", "")
            if c == 4: return item["trans"]
        if role == Qt.ItemDataRole.ForegroundRole:
            if c == 0: return QColor('#cba6f7')
            if c == 1: return QColor('#89b4fa')
            if c == 3: return QColor('#f9e2af')
            if c == 4:
                if item["trans"]:
                    return QColor('#a6e3a1') if item["trans"] != item.get("ai_ref", "") else QColor('#f9e2af')
                return QColor('#f38ba8')
        if role == Qt.ItemDataRole.BackgroundRole:
            if self.is_qa_enabled and item.get("qa_failed"):
                return QColor('#451a1a') # Dark red background for QA errors
        return None

    def update_trans(self, row, text):
        if 0 <= row < len(self._data):
            old = self._data[row]["trans"]
            self._data[row]["trans"] = text
            import re
            self._data[row]["is_th"] = bool(re.search(r'[ก-๙เแไใโ]', text)) if text else False
            self.is_dirty = True
            
            qa_changed = False
            if hasattr(self, 'app') and hasattr(self.app, 'recheck_qa_for_row'):
                qa_changed = self.app.recheck_qa_for_row(row)
                
            idx = self.index(row, 4)
            roles = [Qt.ItemDataRole.DisplayRole]
            if bool(old) != bool(text):
                roles.append(Qt.ItemDataRole.ForegroundRole)
            if qa_changed:
                roles.append(Qt.ItemDataRole.BackgroundRole)
            
            # Since the background color depends on qa_failed (which is row-wide),
            # we should also emit dataChanged for the entire row to be safe.
            idx_start = self.index(row, 0)
            idx_end = self.index(row, 4)
            self.dataChanged.emit(idx_start, idx_end, roles)

    def update_ai_ref(self, row, text):
        """Write AI output to the ai_ref column (Guide Mode)."""
        if 0 <= row < len(self._data):
            self._data[row]["ai_ref"] = text
            self.is_dirty = True
            idx_start = self.index(row, 0)
            idx_end   = self.index(row, COL_AI_REF)
            self.dataChanged.emit(idx_start, idx_end, [Qt.ItemDataRole.DisplayRole])

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        if index.column() == 4:
            return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable
        return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if index.isValid() and role == Qt.ItemDataRole.EditRole and index.column() == 4:
            new_val = str(value)
            old_val = self._data[index.row()]["trans"]
            self._data[index.row()]["trans"] = new_val
            self._data[index.row()]["is_th"] = bool(re.search(r'[ก-๙เแไใโ]', new_val)) if new_val else False
            self.is_dirty = True
            roles = [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole]
            if bool(old_val) != bool(new_val):
                roles.append(Qt.ItemDataRole.ForegroundRole)
            # FIX: Recheck QA status when cell is edited directly in the table
            if hasattr(self, 'app') and hasattr(self.app, 'recheck_qa_for_row'):
                if self.app.recheck_qa_for_row(index.row()):
                    roles.append(Qt.ItemDataRole.BackgroundRole)
                    # Emit for the full row so background color updates across all columns
                    idx_start = self.index(index.row(), 0)
                    idx_end = self.index(index.row(), self.columnCount() - 1)
                    self.dataChanged.emit(idx_start, idx_end, roles)
                    return True
            self.dataChanged.emit(index, index, roles)
            return True
        return False

class FilterProxy(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._search = ''
        self._mode = 0

    def set_search(self, text): self._search = text.lower(); self.invalidateFilter()
    def set_filter_mode(self, mode): self._mode = mode; self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        if source_row < 0 or source_row >= len(self.sourceModel()._data):
            return False
        item = self.sourceModel()._data[source_row]
        tag = item.get("tag", "❓")
        
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
            if item.get("is_idiom", False):
                pass
            elif item.get("ai_ref", "") and item["trans"] != item.get("ai_ref", ""):
                pass
            elif item["source"] and not item["trans"]:
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
        
        if self._mode == 11:
            import re
            clean_text = re.sub(r'\{.*?\}|\[.*?\]|<.*?>', '', item["trans"])
            has_thai = bool(re.search(r'[\u0E00-\u0E7F]', clean_text))
            has_eng = bool(re.search(r'[a-zA-Z]', clean_text))
            if not (has_thai and has_eng): return False

        if self._search:
            # Inline check for better performance
            if self._search == "qa failed" and item.get("qa_failed"):
                return True
            return any(self._search in (str(item.get(k, '')).lower() if item.get(k) else '') for k in ["id", "source", "trans", "tag"])
        return True

def reconstruct_lang_file(csv_path, meta_json_path, output_lang_path):
    import json, csv
    with open(meta_json_path, 'r', encoding='utf-8') as f:
        meta_lines = json.load(f)
        
    translations = {}
    with open(csv_path, 'r', encoding='utf-8-sig', errors='replace') as f:
        reader = csv.reader(f)
        next(reader, None) # skip header
        for row in reader:
            if len(row) >= 3:
                translations[row[0]] = row[2] # row[0] is f"L{line_num}_{key}"
                
    out_lines = []
    for idx, line_info in enumerate(meta_lines):
        line_num = idx + 1
        if line_info["type"] == "comment":
            out_lines.append(line_info["content"] + "\n")
        elif line_info["type"] == "entry":
            key = line_info["key"]
            orig_val = line_info["val"]
            csv_id = f"L{line_num}_{key}"
            trans_val = translations.get(csv_id, "")
            final_val = trans_val if trans_val.strip() else orig_val
            out_lines.append(f"{key}={final_val}\n")
            
    with open(output_lang_path, 'w', encoding='utf-8', newline='\n') as f:
        f.writelines(out_lines)

# =========================================================
# Main Window
# =========================================================
class TranslationStudio(QMainWindow):
    def __init__(self, project_path=None, profile_name=None, source_lang=None, target_lang=None):
        super().__init__()
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('flagship.tstudio.app.1.0')
        except:
            pass
        self.setWindowTitle(f'Translation Studio — {GAME_NAME}')
        self.resize(1400, 800)
        self.setMinimumSize(800, 600)
        self.setStyleSheet(DARK_SS)
        self.current_source_row = -1
        self.current_zoom = 0
        self.threadpool = QThreadPool()
        self._workers = {}  # Keep references to prevent premature garbage collection
        self.csv_path = CSV_PATH
        self.project_path = project_path
        self.csv_encoding = CSV_ENCODING
        self.current_workspace_name = "Default (ค่าเริ่มต้น)"
        
        # Auto-create profile from THub project
        if self.project_path and os.path.exists(os.path.join(self.project_path, "thub_project.json")):
            try:
                import json
                with open(os.path.join(self.project_path, "thub_project.json"), "r", encoding="utf-8") as meta_f:
                    meta = json.load(meta_f)
                prof_name = meta.get("profile_name", meta.get("project_name"))
                if prof_name:
                    pdata = TStudioCore.load_profiles()
                    if prof_name not in pdata.get("presets", {}):
                        pdata.setdefault("presets", {})[prof_name] = {"single": "", "opt": "", "glossary": {}}
                    pdata["active_preset"] = prof_name
                    TStudioCore.save_profiles(pdata)
            except:
                pass

        self.model = CsvTableModel(self)
        self.proxy = FilterProxy(self)
        self.proxy.setDynamicSortFilter(False)
        self.proxy.setSourceModel(self.model)

        self.glossary_dock = QDockWidget(_("glossary_dock_title"), self)
        self.glossary_dock.setObjectName("glossary_dock")
        self.glossary_dock.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        self.glossary_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable | QDockWidget.DockWidgetFeature.DockWidgetFloatable)
        
        self.tlm_dock = QDockWidget(_("tlm_dock_title"), self)
        self.tlm_dock.setObjectName("tlm_dock")
        self.tlm_dock.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        self.tlm_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable | QDockWidget.DockWidgetFeature.DockWidgetFloatable)
        self.tlm_dock.hide()
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.tlm_dock)

        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.glossary_dock)
        self.glossary_dock.hide()

        self.setDockOptions(
            QMainWindow.DockOption.AllowNestedDocks | 
            QMainWindow.DockOption.AllowTabbedDocks | 
            QMainWindow.DockOption.GroupedDragging |
            getattr(QMainWindow.DockOption, 'AnimatedDocks', 0)
        )

        self.setCentralWidget(None)
        
        self.dock_main = QDockWidget("📝 Translation Workspace", self)
        self.dock_main.setObjectName("dock_main")
        self.dock_main.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        self.dock_main.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable | QDockWidget.DockWidgetFeature.DockWidgetFloatable)
        
        main_w = QWidget()
        root = QVBoxLayout(main_w)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)

        # ── Dynamic Toolbar (Flow Layout) ──
        top_widget = QWidget()
        top_layout = FlowLayout(top_widget)
        top_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        
        logo_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "assets", "TStudio.png"))
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))
        self._is_loading_profiles = True
        self._profiles_data = TStudioCore.load_profiles()
        self.cbo_profile = QComboBox()
        self.cbo_profile.setMinimumWidth(80)
        self.cbo_profile.addItems(list(self._profiles_data["presets"].keys()))
        self.cbo_profile.setCurrentText(self._profiles_data["active_preset"])
        self.cbo_profile.currentTextChanged.connect(self.on_profile_changed)
        self.cbo_profile.setToolTip(_("tooltip_profile_combo"))
        self._is_loading_profiles = False
        top_layout.addWidget(self.cbo_profile)

        btn_new_profile = QPushButton(_("btn_new_profile"))
        btn_new_profile.clicked.connect(self.create_new_profile)
        btn_new_profile.setToolTip(_("tooltip_new_profile"))
        top_layout.addWidget(btn_new_profile)

        btn_rename_profile = QPushButton(_("btn_rename_profile"))
        btn_rename_profile.clicked.connect(self.rename_profile)
        btn_rename_profile.setToolTip(_("tooltip_rename_profile"))
        top_layout.addWidget(btn_rename_profile)

        btn_del_profile = QPushButton(_("btn_delete_profile"))
        btn_del_profile.setStyleSheet("color: #f38ba8;")
        btn_del_profile.clicked.connect(self.delete_profile)
        btn_del_profile.setToolTip(_("tooltip_delete_profile"))
        top_layout.addWidget(btn_del_profile)
        # Glossary moved to dock_trans
        if not hasattr(self, 'glossary_widget'):
            self.glossary_widget = GlossaryWidget(self.glossary_dock)
            self.glossary_dock.setWidget(self.glossary_widget)

        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(_("search_placeholder"))
        self.search_input.setToolTip("พิมพ์ข้อความเพื่อค้นหาในตาราง (รองรับทั้งภาษาต้นฉบับและคำแปล)")
        self.search_input.setMinimumWidth(100)
        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(lambda: self.proxy.set_search(self.search_input.text()))
        self.search_input.textChanged.connect(lambda: self._search_timer.start(300))
        top_layout.addWidget(self.search_input)

        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            _("filter_all_rows"), _("filter_untranslated"), _("filter_translated"), _("filter_ai_hallucinations"), _("filter_quotes_idioms"),
            _("filter_characters"), _("filter_locations"), _("filter_items_skills"), _("filter_quests"), _("filter_system_ui"), _("filter_dialogues"),
            _("filter_mixed_lang") if hasattr(self, '_') else "ผสมไทย-อังกฤษ (Mixed)"
        ])
        self.filter_combo.currentIndexChanged.connect(self.proxy.set_filter_mode)
        self.filter_combo.setMinimumWidth(100)
        self.filter_combo.setToolTip("กรองดูเฉพาะแถวที่มีสถานะหรือหมวดหมู่ตรงตามที่เลือก")
        top_layout.addWidget(self.filter_combo)
        

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumWidth(220)
        self.progress_bar.setStyleSheet("QProgressBar { border: 1px solid #45475a; border-radius: 4px; text-align: center; color: #1e1e2e; font-weight: bold; background: #313244; } QProgressBar::chunk { background-color: #a6e3a1; border-radius: 3px; }")
        self.progress_bar.setFormat(_("progress_no_file"))
        self.progress_bar.setValue(0)
        top_layout.addWidget(self.progress_bar)
        
        root.addWidget(top_widget)

        # ── Main Table ──
        self.table = QTableView()
        self.table.setModel(self.proxy)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive)
        self.table.setItemDelegateForColumn(2, HtmlDelegate(self.table))
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.selectionModel().currentChanged.connect(self.on_row_selected)
        
        root.addWidget(self.table)
        root.setStretchFactor(self.table, 1)
        
        self.dock_main.setWidget(main_w)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock_main)

        # ── 1. Original Source Dock ──
        self.dock_source = QDockWidget(_("dock_source_title"), self)
        self.dock_source.setObjectName("dock_source")
        self.dock_source.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        self.dock_source.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable | QDockWidget.DockWidgetFeature.DockWidgetFloatable | QDockWidget.DockWidgetFeature.DockWidgetClosable)
        
        src_w = QWidget()
        l1 = QVBoxLayout(src_w)
        l1.setContentsMargins(5, 5, 5, 5)
        self.txt_source = QTextEdit()
        self.lbl_glossary_cheat = QLabel()
        self.lbl_glossary_cheat.setWordWrap(True)
        self.lbl_glossary_cheat.setStyleSheet("color: #f9e2af; font-size: 12px; background: #313244; padding: 4px; border-radius: 4px;")
        self.lbl_glossary_cheat.hide()
        l1.addWidget(self.lbl_glossary_cheat)
        self.txt_source.setReadOnly(True)
        self.txt_source.setStyleSheet("background:#181825; color:#a6adc8;")
        l1.addWidget(self.txt_source)
        self.dock_source.setWidget(src_w)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock_source)

        # ── 2. AI Translation Dock ──
        self.dock_ai = QDockWidget(_("dock_ai_title"), self)
        self.dock_ai.setObjectName("dock_ai")
        self.dock_ai.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        self.dock_ai.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable | QDockWidget.DockWidgetFeature.DockWidgetFloatable | QDockWidget.DockWidgetFeature.DockWidgetClosable)
        
        ai_w = QWidget()
        l2 = QVBoxLayout(ai_w)
        l2.setContentsMargins(5, 5, 5, 5)
        self.txt_ai = QTextEdit()
        self.txt_ai.setReadOnly(True)
        self.txt_ai.setStyleSheet("background:#181825; color:#f9e2af;")
        l2.addWidget(self.txt_ai)
        self.dock_ai.setWidget(ai_w)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock_ai)

        # ── 3. My Translation Dock ──
        self.dock_trans = QDockWidget(_("dock_trans_title"), self)
        self.dock_trans.setObjectName("dock_trans")
        self.dock_trans.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        self.dock_trans.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable | QDockWidget.DockWidgetFeature.DockWidgetFloatable | QDockWidget.DockWidgetFeature.DockWidgetClosable)
        
        trans_w = QWidget()
        l3 = QVBoxLayout(trans_w)
        l3.setContentsMargins(5, 5, 5, 5)
        
        btn_widget = QWidget()
        btn_row = FlowLayout(btn_widget)
        btn_row.setContentsMargins(0, 0, 0, 0)
        
        self.btn_trans_smart = QPushButton(_("btn_retranslate_smart"))
        self.btn_trans_smart.setObjectName('btnRetranslate')
        self.btn_trans_smart.setStyleSheet("background:#89b4fa; color:#1e1e2e; font-size:12px; padding:4px 8px; font-weight:bold;")
        self.btn_trans_smart.clicked.connect(self.retranslate_smart)
        self.btn_trans_smart.setToolTip(_("tooltip_retranslate_smart"))
        btn_row.addWidget(self.btn_trans_smart)

        self.btn_trans_opt = QPushButton(_("btn_3_options"))
        self.btn_trans_opt.setStyleSheet("background:#f9e2af; color:#1e1e2e; font-size:12px; padding:4px 8px;")
        self.btn_trans_opt.clicked.connect(self.retranslate_options)
        self.btn_trans_opt.setToolTip(_("tooltip_3_options"))
        btn_row.addWidget(self.btn_trans_opt)

        self.btn_trans_special = QPushButton(_("btn_special_adjust"))
        self.btn_trans_special.setToolTip(_("tooltip_btn_trans_special"))
        self.btn_trans_special.setStyleSheet("background:#fab387; color:#1e1e2e; font-size:12px; padding:4px 8px;")
        self.btn_trans_special.clicked.connect(self.show_special_translation_menu_at_cursor)
        self.chk_use_tlm = QCheckBox(_("chk_tlm_toggle"))
        self.chk_use_tlm.setChecked(True)
        self.chk_use_tlm.setToolTip(_("tooltip_tlm_toggle"))
        self.chk_use_tlm.setStyleSheet("color: #a6adc8; font-size: 12px; margin-left: 10px;")
        
        # Build the menu for special adjustments
        self.special_menu = QMenu(self)
        self.special_menu.setStyleSheet("QMenu { font-size: 14px; }")
        
        act_sp_transliterate = self.special_menu.addAction(_("menu_transliterate"))
        act_sp_transliterate.setToolTip(_("tooltip_menu_transliterate"))
        act_sp_transliterate.triggered.connect(lambda: self.retranslate_special("transliterate"))
        self.special_menu.addSeparator()
        
        act_sp_idiom = self.special_menu.addAction(_("menu_idiom"))
        act_sp_idiom.setToolTip(_("tooltip_menu_idiom"))
        act_sp_idiom.triggered.connect(lambda: self.retranslate_special("idiom"))
        
        act_sp_poem = self.special_menu.addAction(_("menu_poem"))
        act_sp_poem.setToolTip(_("tooltip_menu_poem"))
        act_sp_poem.triggered.connect(lambda: self.retranslate_special("poem"))
        
        act_sp_quote = self.special_menu.addAction(_("menu_quote"))
        act_sp_quote.setToolTip(_("tooltip_menu_quote"))
        act_sp_quote.triggered.connect(lambda: self.retranslate_special("quote"))
        self.special_menu.addSeparator()
        
        act_sp_mature = self.special_menu.addAction(_("menu_mature"))
        act_sp_mature.setToolTip(_("tooltip_menu_mature"))
        act_sp_mature.triggered.connect(lambda: self.retranslate_special("mature"))
        
        act_sp_fantasy = self.special_menu.addAction(_("menu_fantasy"))
        act_sp_fantasy.setToolTip(_("tooltip_menu_fantasy"))
        act_sp_fantasy.triggered.connect(lambda: self.retranslate_special("fantasy"))
        
        act_sp_robotic = self.special_menu.addAction(_("menu_robotic"))
        act_sp_robotic.setToolTip(_("tooltip_menu_robotic"))
        act_sp_robotic.triggered.connect(lambda: self.retranslate_special("robotic"))
        
        act_sp_casual = self.special_menu.addAction(_("menu_casual"))
        act_sp_casual.setToolTip(_("tooltip_menu_casual"))
        act_sp_casual.triggered.connect(lambda: self.retranslate_special("casual"))
        
        self.btn_trans_special.setMenu(self.special_menu)
        btn_row.addWidget(self.btn_trans_special)
        btn_row.addWidget(self.chk_use_tlm)

        # ── Guide Mode toggle ──
        self.chk_guide_mode = QCheckBox(_("chk_guide_mode"))
        self.chk_guide_mode.setChecked(False)
        self.chk_guide_mode.setToolTip(_("tooltip_chk_guide_mode"))
        self.chk_guide_mode.setStyleSheet(
            "QCheckBox { color: #cba6f7; font-size: 12px; margin-left: 6px; font-weight: bold; }"
            "QCheckBox::indicator { width: 14px; height: 14px; }"
            "QCheckBox::indicator:checked { background: #cba6f7; border: 2px solid #cba6f7; border-radius: 3px; }"
            "QCheckBox::indicator:unchecked { background: #313244; border: 2px solid #585b70; border-radius: 3px; }"
        )
        self.chk_guide_mode.toggled.connect(self._on_guide_mode_toggled)
        btn_row.addWidget(self.chk_guide_mode)

        l3.addWidget(btn_widget)
        
        self.txt_trans = QTextEdit()
        self._trans_save_timer = QTimer(self)
        self._trans_save_timer.setSingleShot(True)
        self._trans_save_timer.timeout.connect(self.on_trans_changed)
        self.txt_trans.textChanged.connect(lambda: self._trans_save_timer.start(150))
        # When table data changes (via double click edit), update text box if it's the current row
        self.model.dataChanged.connect(self._on_table_data_changed)
        
        # Setup CSV auto-save timer
        self._csv_auto_save_timer = QTimer(self)
        self._csv_auto_save_timer.setSingleShot(True)
        self._csv_auto_save_timer.timeout.connect(self.silent_save_csv)
        self.model.dataChanged.connect(self.on_model_data_changed)
        
        l3.addWidget(self.txt_trans)
        
        self.dock_trans.setWidget(trans_w)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock_trans)
        
        self.setup_menu_bar()
        self.update_button_labels()
        self._setup_batch_progress_widget()
        
        # Capture default layout state before user config overrides it
        self.default_layout_state = self.saveState()
        self.restore_layout_state()
        
        if os.path.exists(self.csv_path):
            self._load_csv()


    
    def setup_menu_bar(self):
        menubar = self.menuBar()
        menubar.clear()
        
        # --- File Menu ---
        file_menu = menubar.addMenu(_("menu_file"))
        
        act_new_proj = QAction(_("act_start_translation"), self)
        act_new_proj.setShortcut('Ctrl+Shift+O')
        act_new_proj.setStatusTip(_("tooltip_act_new_proj_status"))
        act_new_proj.setToolTip(_("tooltip_act_new_proj"))
        act_new_proj.triggered.connect(self.new_project_from_file)
        file_menu.addAction(act_new_proj)

        act_open_proj = QAction(_("act_open_project"), self)
        act_open_proj.setShortcut('Ctrl+O')
        act_open_proj.setStatusTip(_("tooltip_act_open_proj_status"))
        act_open_proj.setToolTip(_("tooltip_act_open_proj"))
        act_open_proj.triggered.connect(self.new_project_from_file)
        file_menu.addAction(act_open_proj)

        file_menu.addSeparator()

        act_save_proj = QAction(_("act_save_project"), self)
        act_save_proj.setShortcut('Ctrl+S')
        act_save_proj.setStatusTip(_("tooltip_act_save_proj_status"))
        act_save_proj.setToolTip(_("tooltip_act_save_proj"))
        act_save_proj.triggered.connect(self.save_csv)
        file_menu.addAction(act_save_proj)

        act_save_csv = QAction(_("act_save_csv_as"), self)
        act_save_csv.setShortcut('Ctrl+Shift+S')
        act_save_csv.setStatusTip(_("tooltip_act_save_csv_status"))
        act_save_csv.setToolTip(_("tooltip_act_save_csv"))
        act_save_csv.triggered.connect(self.save_csv_as)
        file_menu.addAction(act_save_csv)

        file_menu.addSeparator()

        act_deploy = QAction(_("act_deploy"), self)
        act_deploy.setShortcut('Ctrl+D')
        act_deploy.setStatusTip(_("tooltip_act_deploy_status"))
        act_deploy.setToolTip(_("tooltip_act_deploy"))
        act_deploy.triggered.connect(self.deploy_to_game)
        file_menu.addAction(act_deploy)

        file_menu.addSeparator()

        prof_menu = file_menu.addMenu(_("menu_project_profile"))
        act_new_prof = QAction(_("act_new_profile"), self)
        act_new_prof.setToolTip(_("tooltip_act_new_prof"))
        act_new_prof.setStatusTip(_("tooltip_act_new_prof_status"))
        act_new_prof.triggered.connect(self.create_new_profile)
        prof_menu.addAction(act_new_prof)
        
        act_ren_prof = QAction(_("act_rename_profile"), self)
        act_ren_prof.setToolTip(_("tooltip_act_ren_prof"))
        act_ren_prof.setStatusTip(_("tooltip_act_ren_prof_status"))
        act_ren_prof.triggered.connect(self.rename_profile)
        prof_menu.addAction(act_ren_prof)
        
        act_del_prof = QAction(_("act_delete_profile"), self)
        act_del_prof.setToolTip(_("tooltip_act_del_prof"))
        act_del_prof.setStatusTip(_("tooltip_act_del_prof_status"))
        act_del_prof.triggered.connect(self.delete_profile)
        prof_menu.addAction(act_del_prof)
        
        prof_menu.addSeparator()
        
        act_imp_prof = QAction(_("act_import_profile"), self)
        act_imp_prof.setToolTip(_("tooltip_act_imp_prof"))
        act_imp_prof.setStatusTip(_("tooltip_act_imp_prof_status"))
        act_imp_prof.triggered.connect(self.import_profile)
        prof_menu.addAction(act_imp_prof)
        
        act_exp_prof = QAction(_("act_export_profile"), self)
        act_exp_prof.setToolTip(_("tooltip_act_exp_prof"))
        act_exp_prof.setStatusTip(_("tooltip_act_exp_prof_status"))
        act_exp_prof.triggered.connect(self.export_profile)
        prof_menu.addAction(act_exp_prof)
        
        file_menu.addSeparator()
        
        act_export_pua = QAction(_("act_export_pua"), self)
        act_export_pua.setToolTip(_("tooltip_act_export_pua"))
        act_export_pua.setStatusTip(_("tooltip_act_export_pua_status"))
        act_export_pua.triggered.connect(self.export_pua_csv)
        file_menu.addAction(act_export_pua)
        
        act_export_org = QAction(_("act_export_origin"), self)
        act_export_org.setToolTip(_("tooltip_act_export_org"))
        act_export_org.setStatusTip(_("tooltip_act_export_org_status"))
        act_export_org.triggered.connect(self.export_origin_format)
        file_menu.addAction(act_export_org)
        
        act_merge = QAction(_("merge_execute_btn"), self)
        act_merge.setToolTip(_("tooltip_act_merge"))
        act_merge.setStatusTip(_("tooltip_act_merge_status"))
        act_merge.triggered.connect(self.open_merge_dialog)
        file_menu.addAction(act_merge)
        
        file_menu.addSeparator()
        act_exit = QAction(_("act_exit"), self)
        act_exit.setToolTip(_("tooltip_act_exit"))
        act_exit.setStatusTip(_("tooltip_act_exit_status"))
        act_exit.triggered.connect(self.close)
        file_menu.addAction(act_exit)

        # --- Edit Menu ---
        edit_menu = menubar.addMenu(_("menu_edit"))
        
        act_undo = QAction(_("act_undo"), self)
        act_undo.setToolTip(_("tooltip_act_undo"))
        act_undo.setShortcut("Ctrl+Z")
        act_undo.triggered.connect(lambda: QApplication.focusWidget().undo() if hasattr(QApplication.focusWidget(), 'undo') else None)
        edit_menu.addAction(act_undo)
        
        act_redo = QAction(_("act_redo"), self)
        act_redo.setToolTip(_("tooltip_act_redo"))
        act_redo.setShortcut("Ctrl+Y")
        act_redo.triggered.connect(lambda: QApplication.focusWidget().redo() if hasattr(QApplication.focusWidget(), 'redo') else None)
        edit_menu.addAction(act_redo)
        
        edit_menu.addSeparator()
        
        act_cut = QAction(_("act_cut"), self)
        act_cut.setToolTip(_("tooltip_act_cut"))
        act_cut.setShortcut("Ctrl+X")
        act_cut.triggered.connect(lambda: QApplication.focusWidget().cut() if hasattr(QApplication.focusWidget(), 'cut') else None)
        edit_menu.addAction(act_cut)
        
        act_copy = QAction(_("act_copy"), self)
        act_copy.setToolTip(_("tooltip_act_copy"))
        act_copy.setShortcut("Ctrl+C")
        act_copy.triggered.connect(lambda: QApplication.focusWidget().copy() if hasattr(QApplication.focusWidget(), 'copy') else None)
        edit_menu.addAction(act_copy)
        
        act_paste = QAction(_("act_paste"), self)
        act_paste.setToolTip(_("tooltip_act_paste"))
        act_paste.setShortcut("Ctrl+V")
        act_paste.triggered.connect(lambda: QApplication.focusWidget().paste() if hasattr(QApplication.focusWidget(), 'paste') else None)
        edit_menu.addAction(act_paste)
        
        edit_menu.addSeparator()
        
        act_fr = QAction(_("act_find_replace"), self)
        act_fr.setToolTip(_("tooltip_act_fr"))
        act_fr.setShortcut(QKeySequence("Ctrl+F"))
        act_fr.triggered.connect(lambda: FindReplaceDialog(self).exec())
        edit_menu.addAction(act_fr)
        
        edit_menu.addSeparator()
        
        self.act_trans_smart = QAction(_("act_trans_smart"), self)
        self.act_trans_smart.setShortcuts([QKeySequence("Ctrl+T"), QKeySequence("Ctrl+Return"), QKeySequence("Ctrl+Enter")])
        self.act_trans_smart.triggered.connect(self.retranslate_smart)
        edit_menu.addAction(self.act_trans_smart)
        
        self.act_trans_opt = QAction(_("act_trans_opt"), self)
        self.act_trans_opt.setShortcut("Ctrl+3")
        self.act_trans_opt.triggered.connect(self.retranslate_options)
        edit_menu.addAction(self.act_trans_opt)
        
        self.act_trans_special = QAction(_("act_trans_special"), self)
        self.act_trans_special.setShortcut("Ctrl+Shift+T")
        self.act_trans_special.triggered.connect(self.show_special_translation_menu_at_cursor)
        edit_menu.addAction(self.act_trans_special)
        
        self.act_trans_batch = QAction(_("btn_batch_deepseek"), self)
        self.act_trans_batch.setShortcut("Ctrl+Shift+B")
        self.act_trans_batch.triggered.connect(self.retranslate_batch)
        edit_menu.addAction(self.act_trans_batch)
        
        # --- Tools Menu ---
        tools_menu = menubar.addMenu(_("menu_tools"))
        
        act_global = QAction(_("act_global_settings"), self)
        act_global.setToolTip(_("tooltip_act_global"))
        act_global.setShortcut("Ctrl+I")
        act_global.triggered.connect(self.open_settings)
        tools_menu.addAction(act_global)
        
        tools_menu.addSeparator()
        
        act_glossary = QAction(_("act_glossary_manager"), self)
        act_glossary.setToolTip(_("tooltip_act_glossary"))
        act_glossary.setShortcut("Ctrl+B")
        act_glossary.setStatusTip("Open or Focus the Glossary Manager")
        act_glossary.triggered.connect(self.open_glossary)
        tools_menu.addAction(act_glossary)
        
        self.act_toggle_qa = QAction(QIcon(), _("menu_qa_check"), self)
        self.act_toggle_qa.setCheckable(True)
        self.act_toggle_qa.setChecked(False)
        self.act_toggle_qa.setShortcut("Ctrl+Q")
        self.act_toggle_qa.setToolTip(_("tooltip_act_toggle_qa_status"))
        self.act_toggle_qa.triggered.connect(self.on_toggle_qa)
        tools_menu.addAction(self.act_toggle_qa)
        
        self.act_toggle_qa_marker = QAction(QIcon(), _("menu_qa_marker"), self)
        self.act_toggle_qa_marker.setCheckable(True)
        self.act_toggle_qa_marker.setChecked(True)
        self.act_toggle_qa_marker.setShortcut("Ctrl+M")
        self.act_toggle_qa_marker.setToolTip(_("tooltip_act_toggle_qa_marker_status"))
        self.act_toggle_qa_marker.triggered.connect(self.on_toggle_qa_marker)
        tools_menu.addAction(self.act_toggle_qa_marker)
        
        tools_menu.addSeparator()
        
        act_prompts = QAction(_("act_ai_prompt_settings"), self)
        act_prompts.setToolTip(_("tooltip_act_prompts"))
        act_prompts.setShortcut("Ctrl+P")
        act_prompts.triggered.connect(self.open_prompt_settings)
        tools_menu.addAction(act_prompts)
        
        tools_menu.addSeparator()
        
        act_tlm = QAction(_("tlm_dock_title"), self)
        act_tlm.setToolTip(_("tooltip_act_tlm"))
        act_tlm.setShortcut("Ctrl+L")
        act_tlm.setStatusTip("Open or Focus the TLM Extractor")
        act_tlm.triggered.connect(self.toggle_tlm_dock)
        tools_menu.addAction(act_tlm)
        
        # --- View Menu ---
        view_menu = menubar.addMenu(_("menu_view"))
        
        act_zoom_in = QAction(_("act_zoom_in"), self)
        act_zoom_in.setToolTip(_("tooltip_act_zoom_in"))
        act_zoom_in.setShortcut("Ctrl++")
        act_zoom_in.triggered.connect(self.zoom_in)
        view_menu.addAction(act_zoom_in)
        
        act_zoom_out = QAction(_("act_zoom_out"), self)
        act_zoom_out.setToolTip(_("tooltip_act_zoom_out"))
        act_zoom_out.setShortcut("Ctrl+-")
        act_zoom_out.triggered.connect(self.zoom_out)
        view_menu.addAction(act_zoom_out)
        
        act_zoom_reset = QAction(_("act_reset_zoom"), self)
        act_zoom_reset.setToolTip(_("tooltip_act_zoom_reset"))
        act_zoom_reset.setShortcut("Ctrl+0")
        act_zoom_reset.triggered.connect(self.zoom_reset)
        view_menu.addAction(act_zoom_reset)
        
        view_menu.addSeparator()
        
        act_wrap = QAction(_("act_word_wrap"), self)
        act_wrap.setToolTip(_("tooltip_act_wrap"))
        act_wrap.setShortcut("Alt+Z")
        act_wrap.setCheckable(True)
        act_wrap.setChecked(True)
        act_wrap.triggered.connect(self.toggle_word_wrap)
        view_menu.addAction(act_wrap)
        
        view_menu.addSeparator()
        
        self.panels_menu = view_menu.addMenu(_("menu_panels"))
        self.panels_menu.aboutToShow.connect(self.populate_panels_menu)
        
        self.float_menu = view_menu.addMenu(_("menu_float_dock"))
        self.float_menu.aboutToShow.connect(self.populate_float_menu)
        
        view_menu.addSeparator()
        
        # --- Layouts Menu ---
        self.layouts_menu = menubar.addMenu(_("menu_layouts"))
        self.layouts_menu.aboutToShow.connect(self.populate_layouts_menu)

    def populate_panels_menu(self):
        self.panels_menu.clear()
        from PyQt6.QtWidgets import QDockWidget
        from PyQt6.QtGui import QAction
        for dock in self.findChildren(QDockWidget):
            action = QAction(dock.windowTitle(), self)
            action.setCheckable(True)
            action.setChecked(dock.isVisible())
            action.triggered.connect(lambda checked, d=dock: d.setVisible(checked))
            self.panels_menu.addAction(action)

    def zoom_in(self):
        self.current_zoom += 1
        self.apply_zoom()
        
    def zoom_out(self):
        self.current_zoom -= 1
        self.apply_zoom()
        
    def zoom_reset(self):
        self.current_zoom = 0
        self.apply_zoom()
        
    def apply_zoom(self):
        font = self.table.font()
        font.setPointSize(max(6, 10 + self.current_zoom))
        self.table.setFont(font)
        self.table.resizeRowsToContents()
        
    def toggle_word_wrap(self, checked):
        self.table.setWordWrap(checked)
        self.table.resizeRowsToContents()

    def populate_float_menu(self):
        self.float_menu.clear()
        from PyQt6.QtWidgets import QDockWidget
        from PyQt6.QtGui import QAction
        for dock in self.findChildren(QDockWidget):
            prefix = _("act_dock") if dock.isFloating() else _("act_float")
            action = QAction(f"{prefix} {dock.windowTitle()}", self)
            action.triggered.connect(lambda checked, d=dock: d.setFloating(not d.isFloating()))
            self.float_menu.addAction(action)

    def _setup_batch_progress_widget(self):
        """Create a spinner + progress bar embedded in the status bar for batch translate feedback."""
        from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QProgressBar
        from PyQt6.QtCore import QTimer

        self._batch_sb_widget = QWidget()
        self._batch_sb_widget.setFixedHeight(22)
        sb_layout = QHBoxLayout(self._batch_sb_widget)
        sb_layout.setContentsMargins(6, 0, 10, 0)
        sb_layout.setSpacing(6)

        # Spinner label — cycles through unicode braille frames
        self._batch_spinner_label = QLabel("⠋")
        self._batch_spinner_label.setStyleSheet(
            "color: #89b4fa; font-size: 14px; font-weight: bold;"
        )
        sb_layout.addWidget(self._batch_spinner_label)

        # Status text
        self._batch_status_label = QLabel(_("batch_status_translating"))
        self._batch_status_label.setStyleSheet(
            "color: #cdd6f4; font-size: 12px;"
        )
        sb_layout.addWidget(self._batch_status_label)

        # Mini progress bar
        self._batch_mini_bar = QProgressBar()
        self._batch_mini_bar.setFixedWidth(140)
        self._batch_mini_bar.setFixedHeight(10)
        self._batch_mini_bar.setRange(0, 100)
        self._batch_mini_bar.setValue(0)
        self._batch_mini_bar.setTextVisible(False)
        self._batch_mini_bar.setStyleSheet(
            "QProgressBar {"
            "  border: 1px solid #45475a;"
            "  border-radius: 4px;"
            "  background: #313244;"
            "}"
            "QProgressBar::chunk {"
            "  background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            "    stop:0 #89b4fa, stop:1 #a6e3a1);"
            "  border-radius: 3px;"
            "}"
        )
        sb_layout.addWidget(self._batch_mini_bar)

        # Row counter
        self._batch_count_label = QLabel("0 / 0")
        self._batch_count_label.setStyleSheet(
            "color: #a6adc8; font-size: 11px;"
        )
        sb_layout.addWidget(self._batch_count_label)

        # Embed into status bar (left side)
        self.statusBar().insertPermanentWidget(0, self._batch_sb_widget)
        self._batch_sb_widget.hide()

        # Spinner animation timer
        self._spinner_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self._spinner_idx = 0
        self._spinner_timer = QTimer(self)
        self._spinner_timer.setInterval(80)
        self._spinner_timer.timeout.connect(self._tick_spinner)

    def _tick_spinner(self):
        self._spinner_idx = (self._spinner_idx + 1) % len(self._spinner_frames)
        self._batch_spinner_label.setText(self._spinner_frames[self._spinner_idx])

    def _start_batch_progress(self, total: int):
        """Show the batch progress widget and start the spinner."""
        if not hasattr(self, '_batch_sb_widget'):
            return
        self._batch_mini_bar.setValue(0)
        self._batch_count_label.setText(f"0 / {total}")
        self._batch_status_label.setText(_("batch_status_translating"))
        self._batch_sb_widget.show()
        self._spinner_timer.start()

    def _finish_batch_progress(self, success_count: int, total: int):
        """Hide the batch progress widget and stop the spinner."""
        if not hasattr(self, '_batch_sb_widget'):
            return
        self._spinner_timer.stop()
        # Flash 100% briefly before hiding
        self._batch_mini_bar.setValue(100)
        if success_count == total:
            self._batch_status_label.setText(_("batch_status_done").format(total=total))
            self._batch_spinner_label.setText("✓")
            self._batch_spinner_label.setStyleSheet("color: #a6e3a1; font-size: 13px; font-weight: bold;")
        else:
            self._batch_status_label.setText(_("batch_status_done_error").format(error=total - success_count))
            self._batch_spinner_label.setText("!")
            self._batch_spinner_label.setStyleSheet("color: #f38ba8; font-size: 13px; font-weight: bold;")
        # Hide after 2 seconds
        QTimer.singleShot(2000, lambda: (
            self._batch_sb_widget.hide(),
            self._batch_spinner_label.setText("⠋"),
            self._batch_spinner_label.setStyleSheet("color: #89b4fa; font-size: 14px; font-weight: bold;"),
        ))

    def update_progress_stats(self):

        if not hasattr(self, 'model') or not self.model or not self.model._data:
            self.progress_bar.setFormat(_("progress_no_file"))
            self.progress_bar.setValue(0)
            return
            
        total = len(self.model._data)
        if total == 0:
            return
            
        translated_count = 0
        counts = {i: 0 for i in range(12)}
        counts[0] = total

        for item in self.model._data:
            text = item["trans"]
            src = item["source"]
            tag = item.get("tag", "")
            
            # Progress bar count
            if item.get("is_th", False):
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
            if item.get("is_idiom", False):
                counts[4] += 1
                
            # Modes 5-10: Smart Tags
            if "Char" in tag: counts[5] += 1
            if "Loc" in tag: counts[6] += 1
            if "Item" in tag: counts[7] += 1
            if "Quest" in tag: counts[8] += 1
            if "Sys" in tag: counts[9] += 1
            if "Talk" in tag: counts[10] += 1
            
        # Cache for incremental updates
        self._stat_translated = translated_count
        self._stat_counts = counts

        # Update combo box texts
        labels = [
            _("filter_all_rows"), _("filter_untranslated"), _("filter_translated"), _("filter_ai_hallucinations"), _("filter_quotes_idioms"),
            _("filter_characters"), _("filter_locations"), _("filter_items_skills"), _("filter_quests"), _("filter_system_ui"), _("filter_dialogues"),
            _("filter_mixed_lang") if hasattr(self, '_') else "ผสมไทย-อังกฤษ (Mixed)"
        ]
        self.filter_combo.blockSignals(True)
        for i in range(12):
            if i < self.filter_combo.count():
                self.filter_combo.setItemText(i, f"{labels[i]} ({counts[i]:,})")
        self.filter_combo.blockSignals(False)
                
        percent = int((translated_count / total) * 100) if total > 0 else 0
        self.progress_bar.setValue(percent)
        self.progress_bar.setFormat(f"แปลแล้ว {percent}% ({translated_count:,} / {total:,})")

    def _update_stats_for_row(self, row, old_text, new_text):
        if not hasattr(self, '_stat_counts') or self._stat_counts is None:
            self.update_progress_stats()
            # FIX: update_progress_stats() may return early (empty model, etc.) and
            # leave _stat_counts still None.  Guard again before using it.
            if not hasattr(self, '_stat_counts') or self._stat_counts is None:
                return

        item = self.model._data[row]
        src = item["source"]
        
        # 1. Progress bar Thai count
        old_is_th = bool(re.search(r'[ก-๙เแไใโ]', old_text)) if old_text else False
        new_is_th = bool(re.search(r'[ก-๙เแไใโ]', new_text)) if new_text else False
        if old_is_th != new_is_th:
            self._stat_translated += (1 if new_is_th else -1)
            
        # 2. Mode 1: Untranslated
        old_untrans = not old_text.strip()
        new_untrans = not new_text.strip()
        if old_untrans != new_untrans:
            self._stat_counts[1] += (1 if new_untrans else -1)
            
        # 3. Mode 2: Translated
        old_trans = bool(old_text.strip())
        new_trans = bool(new_text.strip())
        if old_trans != new_trans:
            self._stat_counts[2] += (1 if new_trans else -1)
            
        # 4. Mode 3: AI Hallucinations
        src_len = len(src)
        old_len = len(old_text)
        new_len = len(new_text)
        
        old_halluc = (old_len >= 200 and src_len > 0 and (old_len / src_len) > 4)
        new_halluc = (new_len >= 200 and src_len > 0 and (new_len / src_len) > 4)
        if old_halluc != new_halluc:
            self._stat_counts[3] += (1 if new_halluc else -1)
            
        # Update combo box texts incrementally
        labels = [
            _("filter_all_rows"), _("filter_untranslated"), _("filter_translated"), _("filter_ai_hallucinations"), _("filter_quotes_idioms"),
            _("filter_characters"), _("filter_locations"), _("filter_items_skills"), _("filter_quests"), _("filter_system_ui"), _("filter_dialogues"),
            _("filter_mixed_lang") if hasattr(self, '_') else "ผสมไทย-อังกฤษ (Mixed)"
        ]
        self.filter_combo.blockSignals(True)
        for i in [1, 2, 3]:
            if i < self.filter_combo.count():
                self.filter_combo.setItemText(i, f"{labels[i]} ({self._stat_counts[i]:,})")
        self.filter_combo.blockSignals(False)
        
        total = self._stat_counts[0]
        percent = int((self._stat_translated / total) * 100) if total > 0 else 0
        self.progress_bar.setValue(percent)
        self.progress_bar.setFormat(f"แปลแล้ว {percent}% ({self._stat_translated:,} / {total:,})")

    def changeEvent(self, event):
        if event.type() == event.Type.ActivationChange:
            if self.isActiveWindow():
                self._reload_profiles_silently()
            else:
                # Focus lost, save immediately if there are pending edits
                if hasattr(self, '_trans_save_timer') and self._trans_save_timer.isActive():
                    self._trans_save_timer.stop()
                    self.on_trans_changed()
                if hasattr(self, '_csv_auto_save_timer') and self._csv_auto_save_timer.isActive():
                    self._csv_auto_save_timer.stop()
                    self.silent_save_csv()
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


    def populate_layouts_menu(self):
        self.layouts_menu.clear()
        
        from PyQt6.QtGui import QAction
        from PyQt6.QtGui import QIcon
        from tstudio_core import TStudioCore
        cfg = TStudioCore.load_config()
        user_layouts = cfg.get(self.layout_cfg_key, {})
        
        translated_name = self.current_workspace_name
        if self.current_workspace_name == "Default (ค่าเริ่มต้น)":
            translated_name = _("layout_default")
        elif self.current_workspace_name == "AI Focus":
            translated_name = _("layout_ai_focus")
        elif self.current_workspace_name == "Split View":
            translated_name = _("layout_split_view")
        elif self.current_workspace_name == "Compact Tabbed":
            translated_name = _("layout_compact_tabbed")

        # Helper to create checkable actions
        def add_workspace_action(name, func=None, is_custom=False, display_name=None):
            if display_name is None:
                display_name = name
            act = QAction(f"{'🪟 ' if is_custom else ''}{display_name}", self)
            act.setCheckable(True)
            if self.current_workspace_name == name:
                act.setChecked(True)
            if func:
                act.triggered.connect(func)
            else:
                act.triggered.connect(lambda checked, n=name: self.load_custom_layout(n))
            self.layouts_menu.addAction(act)
        
        add_workspace_action("Default (ค่าเริ่มต้น)", self.layout_default, display_name=_("layout_default"))
        if not hasattr(self, 'video_dock'):
            add_workspace_action("AI Focus", self.layout_ai_focus, display_name=_("layout_ai_focus"))
            add_workspace_action("Split View", self.layout_split_view, display_name=_("layout_split_view"))
            add_workspace_action("Compact Tabbed", self.layout_compact_tabbed, display_name=_("layout_compact_tabbed"))
        
        if user_layouts:
            for name in user_layouts.keys():
                add_workspace_action(name, is_custom=True)
                
        self.layouts_menu.addSeparator()
        
        # Reset current workspace
        act_reset = QAction(_("act_reset_layout").replace("{name}", translated_name), self)
        act_reset.setToolTip(_("tooltip_reset_layout"))
        act_reset.triggered.connect(self.reset_layout_default)
        self.layouts_menu.addAction(act_reset)
        
        # Save current custom workspace (only show if it's a custom one)
        if self.current_workspace_name in user_layouts:
            act_save_current = QAction(_("act_save_layout_current").replace("{name}", translated_name), self)
            act_save_current.setToolTip(_("tooltip_save_layout_current"))
            act_save_current.triggered.connect(self.save_current_custom_layout)
            self.layouts_menu.addAction(act_save_current)
        
        self.layouts_menu.addSeparator()
        
        act_save = QAction(_("act_save_layout_new"), self)
        act_save.setToolTip(_("tooltip_save_layout_new"))
        act_save.triggered.connect(self.save_custom_layout)
        self.layouts_menu.addAction(act_save)
        
        act_manage = QAction(_("act_delete_layout"), self)
        act_manage.setToolTip(_("tooltip_delete_layout"))
        act_manage.triggered.connect(self.delete_custom_layout)
        self.layouts_menu.addAction(act_manage)

    def layout_default(self):
        self.current_workspace_name = "Default (ค่าเริ่มต้น)"
        from PyQt6.QtCore import QByteArray
        # Baked-in base64 state from user's "ค่าเริ่มต้น" layout
        b64 = "AAAA/wAAAAD9AAAAAQAAAAEAAAV4AAAC9fwCAAAAAfwAAAAVAAAC9QAAAYwA/////AEAAAAD+wAAABIAZABvAGMAawBfAG0AYQBpAG4BAAAAAAAAAfcAAACVAP////sAAAAaAGcAbABvAHMAcwBhAHIAeQBfAGQAbwBjAGsBAAAB/QAAAbEAAAEsAP////wAAAO0AAABxAAAAJ0A/////AIAAAAD+wAAABYAZABvAGMAawBfAHMAbwB1AHIAYwBlAQAAABUAAAEBAAAAbgD////7AAAADgBkAG8AYwBrAF8AYQBpAQAAARwAAADdAAAAbgD////7AAAAFABkAG8AYwBrAF8AdAByAGEAbgBzAQAAAf8AAAELAAAAjAD///8AAAAAAAAC9QAAAAQAAAAEAAAACAAAAAj8AAAAAA=="
        self.restoreState(QByteArray.fromBase64(b64.encode('utf-8')))
        
        # Ensure new/dynamic docks are hidden if they weren't part of the state
        if hasattr(self, 'video_dock'):
            from PyQt6.QtCore import Qt
            self.video_dock.show()
            self.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea, self.video_dock)
            self.resizeDocks([self.video_dock], [450], Qt.Orientation.Vertical)
            self.video_dock.raise_()
        if hasattr(self, 'tlm_dock'): self.tlm_dock.hide()
        
        self.dock_trans.raise_()

    def layout_ai_focus(self):
        self.current_workspace_name = "AI Focus"
        if hasattr(self, 'tlm_dock'): self.tlm_dock.hide()
        self.dock_main.show()
        self.dock_trans.show()
        if hasattr(self, 'dock_ai'): self.dock_ai.show()
        if hasattr(self, 'glossary_dock'): self.glossary_dock.show()
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock_main)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock_trans)
        if hasattr(self, 'dock_ai'): self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock_ai)
        if hasattr(self, 'glossary_dock'): self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.glossary_dock)
        if hasattr(self, 'dock_ai'): self.dock_ai.raise_()

    def layout_split_view(self):
        self.current_workspace_name = "Split View"
        if hasattr(self, 'glossary_dock'): self.glossary_dock.hide()
        if hasattr(self, 'dock_ai'): self.dock_ai.hide()
        if hasattr(self, 'tlm_dock'): self.tlm_dock.hide()
        
        self.dock_main.show()
        self.dock_source.show()
        self.dock_trans.show()
        
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock_main)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock_source)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock_trans)
        self.dock_source.raise_()
        self.dock_trans.raise_()

    def layout_compact_tabbed(self):
        self.current_workspace_name = "Compact Tabbed"
        if hasattr(self, 'tlm_dock'): self.tlm_dock.hide()
        self.dock_main.show()
        self.dock_source.show()
        self.dock_trans.show()
        if hasattr(self, 'dock_ai'): self.dock_ai.show()
        
        if not hasattr(self, 'glossary_widget'):
            from tstudio_ui_shared import GlossaryWidget
            self.glossary_widget = GlossaryWidget(self.glossary_dock)
            self.glossary_dock.setWidget(self.glossary_widget)

        self.glossary_dock.show()
        
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock_main)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock_source)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock_trans)
        if hasattr(self, 'dock_ai'): self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock_ai)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.glossary_dock)
        
        self.tabifyDockWidget(self.dock_source, self.dock_trans)
        if hasattr(self, 'dock_ai'):
            self.tabifyDockWidget(self.dock_trans, self.dock_ai)
            
        self.tabifyDockWidget(self.dock_main, self.glossary_dock)
            
        self.dock_trans.raise_()

    def save_current_custom_layout(self):
        from tstudio_core import TStudioCore
        cfg = TStudioCore.load_config()
        layouts = cfg.get(self.layout_cfg_key, {})
        if self.current_workspace_name in layouts:
            layouts[self.current_workspace_name] = self.saveState().toBase64().data().decode('utf-8')
            cfg[self.layout_cfg_key] = layouts
            TStudioCore.save_config(cfg)
            self.statusBar().showMessage(f"Workspace '{self.current_workspace_name}' overwritten and saved.", 3000)

    def save_custom_layout(self):
        from PyQt6.QtWidgets import QInputDialog, QMessageBox
        name, ok = QInputDialog.getText(self, "New Workspace", "Enter a name for the new workspace:")
        if ok and name.strip():
            name = name.strip()
            from tstudio_core import TStudioCore
            cfg = TStudioCore.load_config()
            layouts = cfg.get(self.layout_cfg_key, {})
            
            if name in layouts:
                reply = QMessageBox.question(
                    self, "Overwrite Workspace", 
                    f"The workspace '{name}' already exists. Do you want to replace it?", 
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return
                    
            layouts[name] = self.saveState().toBase64().data().decode('utf-8')
            cfg[self.layout_cfg_key] = layouts
            self.current_workspace_name = name
            TStudioCore.save_config(cfg)
            self.statusBar().showMessage(f"Workspace '{name}' saved.", 3000)

    def load_custom_layout(self, name):
        from tstudio_core import TStudioCore
        cfg = TStudioCore.load_config()
        layouts = cfg.get(self.layout_cfg_key, {})
        if name in layouts:
            from PyQt6.QtCore import QByteArray
            self.current_workspace_name = name
            state = QByteArray.fromBase64(layouts[name].encode('utf-8'))
            self.restoreState(state)
            self.statusBar().showMessage(f"Workspace '{name}' loaded.", 3000)

    def delete_custom_layout(self):
        from tstudio_core import TStudioCore
        cfg = TStudioCore.load_config()
        layouts = cfg.get(self.layout_cfg_key, {})
        if not layouts:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Delete Workspace", "No custom workspaces found to delete.")
            return
            
        from PyQt6.QtWidgets import QInputDialog
        items = list(layouts.keys())
        name, ok = QInputDialog.getItem(self, "Delete Workspace", "Select workspace to delete:", items, 0, False)
        if ok and name:
            del layouts[name]
            cfg[self.layout_cfg_key] = layouts
            if self.current_workspace_name == name:
                self.current_workspace_name = "Default (ค่าเริ่มต้น)"
            TStudioCore.save_config(cfg)
            self.statusBar().showMessage(f"Workspace '{name}' deleted.", 3000)

    def reset_layout_default(self):
        # Reset the current workspace to its saved state
        built_in_presets = {
            "Default (ค่าเริ่มต้น)": self.layout_default
        }
        if not hasattr(self, 'video_dock'):
            built_in_presets.update({
                "AI Focus": self.layout_ai_focus,
                "Split View": self.layout_split_view,
                "Compact Tabbed": self.layout_compact_tabbed
            })
        
        if self.current_workspace_name in built_in_presets:
            built_in_presets[self.current_workspace_name]()
        else:
            self.load_custom_layout(self.current_workspace_name)
            
        # Explicitly hide dynamically added docks that weren't present during saveState
        if hasattr(self, 'tlm_dock') and self.tlm_dock.isVisible():
            self.tlm_dock.hide()


    @property
    def layout_cfg_key(self):
        return 'user_layouts_tvox' if hasattr(self, 'video_dock') else 'user_layouts'

    def save_layout_state(self):
        cfg = TStudioCore.load_config()
        if hasattr(self, 'video_dock'):
            cfg['layout_state_tvox'] = self.saveState().toBase64().data().decode('utf-8')
        else:
            cfg['layout_state'] = self.saveState().toBase64().data().decode('utf-8')
            cfg['current_workspace'] = getattr(self, 'current_workspace_name', 'Default (ค่าเริ่มต้น)')
        TStudioCore.save_config(cfg)

    def restore_layout_state(self):
        cfg = TStudioCore.load_config()
        state_key = 'layout_state_tvox' if hasattr(self, 'video_dock') else 'layout_state'
        if not hasattr(self, 'video_dock'):
            self.current_workspace_name = cfg.get('current_workspace', 'Default (ค่าเริ่มต้น)')
        
        if state_key in cfg and cfg[state_key]:
            try:
                from PyQt6.QtCore import QByteArray
                state = QByteArray.fromBase64(cfg[state_key].encode('utf-8'))
                self.restoreState(state)
            except Exception as e:
                print(f"Error restoring layout: {e}")



    def toggle_tlm_dock(self):
        if not hasattr(self, 'tlm_widget'):
            try:
                from tstudio_tlm_library import TLMLoreLibrary
                if not hasattr(self, 'glossary_widget'):
                    self.open_glossary()
                self.tlm_widget = TLMLoreLibrary(self.glossary_widget, self)
                self.tlm_dock.setWidget(self.tlm_widget)
                self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.tlm_dock)
            except Exception as e:
                import traceback
                traceback.print_exc()
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.critical(self, _("error_title"), f"Could not open TLM Library:\n{e}")
                return

        if self.tlm_dock.isVisible():
            self.tlm_dock.hide()
        else:
            self.tlm_dock.show()
            self.tlm_dock.raise_()
            
    def open_tlm_library(self):
        self.toggle_tlm_dock()

    def open_glossary(self):
        # Create it if it doesn't exist
        if not hasattr(self, 'glossary_widget'):
            self.glossary_widget = GlossaryWidget(self.glossary_dock)
            self.glossary_dock.setWidget(self.glossary_widget)
            self._profiles_data = TStudioCore.load_profiles()
            
        # Toggle visibility
        if self.glossary_dock.isVisible():
            self.glossary_dock.hide()
        else:
            self.tabifyDockWidget(self.dock_main, self.glossary_dock)
            self.glossary_dock.show()
            self.glossary_dock.raise_()

    def open_prompt_settings(self):
        PromptSettingsDialog(self).exec()
        self._profiles_data = TStudioCore.load_profiles()

    def open_settings(self):
        SettingsDialog(self).exec()
        self.setup_menu_bar()
        self.update_button_labels()

    def update_button_labels(self):
        cfg = TStudioCore.load_config()
        model = cfg.get("model", "")
        if model.startswith("gemini"):
            self.btn_trans_smart.setText(_("btn_retranslate_model").format(model="Gemini"))
            self.btn_trans_smart.setStyleSheet("background:#a6e3a1; color:#1e1e2e; font-size:12px; padding:4px 8px;")
            if hasattr(self, 'btn_trans_batch'):
                self.btn_trans_batch.setText(_("btn_batch_model").format(model="Gemini"))
                self.btn_trans_batch.setStyleSheet("background:#a6e3a1; color:#1e1e2e; font-size:12px; padding:4px 8px;")
        elif model.startswith("claude"):
            self.btn_trans_smart.setText(_("btn_retranslate_model").format(model="Claude"))
            self.btn_trans_smart.setStyleSheet("background:#fab387; color:#1e1e2e; font-size:12px; padding:4px 8px;")
            if hasattr(self, 'btn_trans_batch'):
                self.btn_trans_batch.setText(_("btn_batch_model").format(model="Claude"))
                self.btn_trans_batch.setStyleSheet("background:#fab387; color:#1e1e2e; font-size:12px; padding:4px 8px;")
        elif model.startswith("deepseek"):
            self.btn_trans_smart.setText(_("btn_retranslate_deepseek"))
            self.btn_trans_smart.setStyleSheet("background:#89b4fa; color:#1e1e2e; font-size:12px; padding:4px 8px;")
            if hasattr(self, 'btn_trans_batch'):
                self.btn_trans_batch.setText(_("btn_batch_deepseek"))
                self.btn_trans_batch.setStyleSheet("background:#89b4fa; color:#1e1e2e; font-size:12px; padding:4px 8px;")
        elif model == "custom-local-llm" or model == "Local LLM" or cfg.get("provider") == "Local LLM":
            self.btn_trans_smart.setText(_("btn_retranslate_local"))
            self.btn_trans_smart.setStyleSheet("background:#cba6f7; color:#1e1e2e; font-size:12px; padding:4px 8px;")
            if hasattr(self, 'btn_trans_batch'):
                self.btn_trans_batch.setText(_("btn_batch_local"))
                self.btn_trans_batch.setStyleSheet("background:#cba6f7; color:#1e1e2e; font-size:12px; padding:4px 8px;")
        else:
            self.btn_trans_smart.setText(_("btn_retranslate_model").format(model="OpenAI"))
            self.btn_trans_smart.setStyleSheet("background:#89b4fa; color:#1e1e2e; font-size:12px; padding:4px 8px;")
            if hasattr(self, 'btn_trans_batch'):
                self.btn_trans_batch.setText(_("btn_batch_model").format(model="OpenAI"))
                self.btn_trans_batch.setStyleSheet("background:#89b4fa; color:#1e1e2e; font-size:12px; padding:4px 8px;")

        # Guide Mode overrides all button colors to purple
        if getattr(self, 'chk_guide_mode', None) and self.chk_guide_mode.isChecked():
            purple_style = "background:#cba6f7; color:#1e1e2e; font-size:12px; padding:4px 8px; font-weight:bold;"
            self.btn_trans_smart.setStyleSheet(purple_style)
            self.btn_trans_opt.setStyleSheet(purple_style)
            self.btn_trans_special.setStyleSheet(purple_style)
            if hasattr(self, 'btn_trans_batch'):
                self.btn_trans_batch.setStyleSheet(purple_style)
        else:
            # Restore default colors for non-primary buttons
            self.btn_trans_opt.setStyleSheet("background:#f9e2af; color:#1e1e2e; font-size:12px; padding:4px 8px;")
            self.btn_trans_special.setStyleSheet("background:#fab387; color:#1e1e2e; font-size:12px; padding:4px 8px;")


    def rename_profile(self):
        active = self.cbo_profile.currentText()
        if active == "Default":
            QMessageBox.warning(self, _("warning_title"), _("cannot_rename_default"))
            return
            
        from PyQt6.QtWidgets import QInputDialog
        new_name, ok = QInputDialog.getText(self, _("rename_profile_title"), f"Enter new name for '{active}':", text=active)
        if ok and new_name.strip():
            new_name = new_name.strip()
            if new_name == active:
                return
            if new_name in self._profiles_data["presets"]:
                QMessageBox.warning(self, _("warning_title"), f"Profile '{new_name}' already exists.")
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
            QMessageBox.warning(self, _("warning_title"), _("cannot_delete_default"))
            return
            
        reply = QMessageBox.question(self, _("confirm_delete_title"), f"Are you sure you want to delete profile '{active}'?",
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
            
            self.on_profile_changed("Default")
            self.statusBar().showMessage(f"Profile '{active}' deleted.", 3000)

    def export_profile(self):
        active = self.cbo_profile.currentText()
        data = self._profiles_data["presets"].get(active)
        if data is None:
            QMessageBox.warning(self, _("warning_title"), f"Profile '{active}' not found.")
            return
        file_path, _ext = QFileDialog.getSaveFileName(self, "Export Profile", f"{active}_profile.json", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                self.statusBar().showMessage(f"Profile exported to {file_path}", 3000)
            except Exception as e:
                QMessageBox.critical(self, _("error_title"), f"Failed to export profile:\n{e}")

    def import_profile(self):
        file_path, _ext = QFileDialog.getOpenFileName(self, _("import_profile_title"), "", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if "single" not in data or "opt" not in data or "glossary" not in data:
                    QMessageBox.warning(self, _("invalid_file_title"), _("invalid_profile_file"))
                    return
                    
                from PyQt6.QtWidgets import QInputDialog, QLineEdit
                import os
                base_name = os.path.basename(file_path)
                if base_name.lower().endswith(".json"):
                    base_name = base_name[:-5]
                if base_name.lower().endswith("_profile"):
                    base_name = base_name[:-8]
                
                name, ok = QInputDialog.getText(
                    self, 
                    _("import_profile_title"), 
                    _("import_profile_prompt"), 
                    QLineEdit.EchoMode.Normal, 
                    base_name
                )
                if ok and name.strip():
                    name = name.strip()
                    if name in self._profiles_data["presets"]:
                        reply = QMessageBox.question(
                            self,
                            _("import_profile_title"),
                            _("profile_overwrite_confirm").format(name=name),
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                        )
                        if reply == QMessageBox.StandardButton.No:
                            return
                    self._profiles_data["presets"][name] = data
                    self._profiles_data["active_preset"] = name
                    TStudioCore.save_profiles(self._profiles_data)
                    
                    self._is_loading_profiles = True
                    if self.cbo_profile.findText(name) == -1:
                        self.cbo_profile.addItem(name)
                    self.cbo_profile.setCurrentText(name)
                    self._is_loading_profiles = False
                    
                    self.on_profile_changed(name)
                    self.statusBar().showMessage(f"Profile '{name}' imported.", 3000)
            except Exception as e:
                QMessageBox.critical(self, _("error_title"), f"Failed to import profile:\n{e}")

    def on_profile_changed(self, text):
        if self._is_loading_profiles or not text: return
        
        # Load fresh data to prevent stale cache overwriting
        fresh_data = TStudioCore.load_profiles()
        fresh_data["active_preset"] = text
        TStudioCore.save_profiles(fresh_data)
        self._profiles_data = fresh_data
        
        # Update GlossaryWidget if it exists so it reflects the new profile
        if hasattr(self, 'glossary_widget'):
            is_visible = self.glossary_dock.isVisible()
            if not getattr(self.glossary_widget, '_is_modified', False):
                self.glossary_widget.setParent(None)
                self.glossary_widget.deleteLater()
                del self.glossary_widget
                if is_visible:
                    self.glossary_widget = GlossaryWidget(self.glossary_dock)
                    self.glossary_dock.setWidget(self.glossary_widget)

                    try:
                        from tstudio_tlm_library import TLMLoreLibrary
                        self.tlm_widget = TLMLoreLibrary(self.glossary_widget, self)
                        self.tlm_dock.setWidget(self.tlm_widget)
                    except Exception as e:
                        print(f"Error initializing TLM: {e}")
            else:
                self.statusBar().showMessage("Glossary has unsaved changes for the old profile. Please save them.", 4000)

        self.statusBar().showMessage(f"Switched to profile: {text}", 3000)

    def create_new_profile(self):
        from PyQt6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, _("new_profile_title"), _("new_profile_prompt"))
        if ok and name.strip():
            name = name.strip()
            if name not in self._profiles_data["presets"]:
                self._profiles_data["presets"][name] = {"single": "", "opt": "", "glossary": {}}
                self._profiles_data["active_preset"] = name
                TStudioCore.save_profiles(self._profiles_data)
                
                self._is_loading_profiles = True
                self.cbo_profile.addItem(name)
                self.cbo_profile.setCurrentText(name)
                self._is_loading_profiles = False
                
                self.on_profile_changed(name)
            else:
                self.cbo_profile.setCurrentText(name)

    def open_project_dialog(self):
        if hasattr(self, 'model') and getattr(self.model, 'is_dirty', False):
            reply = QMessageBox.question(self, _("unsaved_changes_title"), "You have unsaved translations. Do you want to save before opening a project?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
            if reply == QMessageBox.StandardButton.Yes:
                self.save_project()
            elif reply == QMessageBox.StandardButton.Cancel:
                return

        file_path, _ext = QFileDialog.getOpenFileName(self, "Open Project", BASE_DIR, "TStudio Project (*.tproj);;All Files (*.*)")
        if file_path:
            self.load_project(file_path)

    def load_project(self, project_path):
        import json
        try:
            with open(project_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            csv_path = data.get("csv_file")
            if csv_path and os.path.exists(csv_path):
                self.project_path = project_path
                self.csv_path = csv_path
                self._load_csv()
                self.setWindowTitle(f"Translation Studio - {os.path.basename(project_path)}")
                
                active_profile = data.get("active_profile")
                if active_profile:
                    self.cbo_profile.setCurrentText(active_profile)
                    
                last_row = data.get("last_selected_row")
                if last_row is not None and last_row >= 0 and last_row < self.proxy.rowCount():
                    self.table.selectRow(last_row)
                    
            else:
                QMessageBox.warning(self, _("error_title"), f"CSV file not found:\n{csv_path}")
        except Exception as e:
            QMessageBox.critical(self, _("error_title"), f"Failed to load project:\n{str(e)}")

    def save_project(self):
        if not self.model or not self.model._data:
            QMessageBox.warning(self, _("error_title"), "No project loaded to save.")
            return
            
        if not self.project_path:
            file_path, _ext = QFileDialog.getSaveFileName(self, "Save Project As", BASE_DIR, "TStudio Project (*.tproj)")
            if not file_path:
                return
            if not file_path.endswith('.tproj'):
                file_path += '.tproj'
            self.project_path = file_path
            self.setWindowTitle(f"Translation Studio - {os.path.basename(file_path)}")

        self.save_csv()
        
        import json
        try:
            current_row = -1
            if self.table.selectionModel().hasSelection():
                current_row = self.table.selectionModel().selectedRows()[0].row()
                
            data = {
                "csv_file": self.csv_path,
                "active_profile": self._profiles_data.get("active_preset", "Default"),
                "last_selected_row": current_row
            }
            with open(self.project_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
                
            self.statusBar().showMessage(f"Project saved to {os.path.basename(self.project_path)}", 5000)
            QMessageBox.information(self, _("save_success_title"), f"Project saved successfully to:\n{self.project_path}")
        except Exception as e:
            QMessageBox.critical(self, _("error_title"), f"Failed to save project:\n{str(e)}")

    def save_csv_as(self):
        if hasattr(self, '_trans_save_timer') and self._trans_save_timer.isActive():
            self._trans_save_timer.stop()
            self.on_trans_changed()

        if not self.model or not self.model._data:
            QMessageBox.warning(self, _("error_title"), _("no_data_save"))
            return
        from tstudio_core import TStudioCore
        last_dir = TStudioCore.get_last_dir() or BASE_DIR
        file_path, _ext = QFileDialog.getSaveFileName(self, _("save_csv_as_title"), self.csv_path or last_dir, "CSV Files (*.csv)")
        if file_path:
            TStudioCore.set_last_dir(file_path)
            import tempfile, shutil
            tmp_fd, tmp_path = tempfile.mkstemp(
                dir=os.path.dirname(os.path.abspath(file_path)),
                suffix='.tmp'
            )
            try:
                with os.fdopen(tmp_fd, 'w', encoding='utf-8-sig', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([_("col_id"), _("col_source"), _("col_translation"), "AI Reference"])
                    for item in self.model._data:
                        writer.writerow([item["id"], item["source"], item["trans"], item.get("ai_ref", "")])
                shutil.move(tmp_path, file_path)
                QMessageBox.information(self, _("success_title"), f"CSV saved successfully to:\n{os.path.basename(file_path)}")
            except Exception as e:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
                QMessageBox.critical(self, _("error_title"), f"Failed to save CSV:\n{e}")

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

    def new_project_from_file(self):
        if hasattr(self, 'model') and getattr(self.model, 'is_dirty', False):
            reply = QMessageBox.question(self, _("unsaved_changes_title"), _("unsaved_before_open"), QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
            if reply == QMessageBox.StandardButton.Yes:
                self.save_csv()
            elif reply == QMessageBox.StandardButton.Cancel:
                return

        from tstudio_core import TStudioCore
        last_dir = TStudioCore.get_last_dir() or BASE_DIR
        file_path, _ext = QFileDialog.getOpenFileName(
            self,
            _("open_import_file_title"),
            last_dir,
            "Supported Files (*.csv *.tproj *.lor *.locres *.tex *.bundle *.ttarch2 *.win *.txt *.srt *.vtt *.json *.lang *.pak);;TStudio Projects (*.tproj);;CSV Files (*.csv);;Subtitle Files (*.srt *.vtt);;Locres Files (*.locres *.lor);;LANG Files (*.lang);;Texture Files (*.tex);;Unity Bundles (*.bundle *.txt *.json);;PAK Files (*.pak);;All Files (*.*)"
        )
        if file_path:
            TStudioCore.set_last_dir(file_path)
            if file_path.lower().endswith('.tproj'):
                self.load_project(file_path)
                return
            if file_path.lower().endswith('.ttarch2'):
                self.open_telltale_archive(file_path)
                return
            self.statusBar().showMessage(_("loading_file_status"))
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
                    
                try:
                    if file_path.lower().endswith('.win'):
                        import sys
                        sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Core"))
                        from utmt_handler import UTMTHandler
                        csv_out = UTMTHandler.extract_strings_to_csv(file_path)
                        if csv_out:
                            from tstudio_core import TStudioCore
                            cfg = TStudioCore.load_config()
                            cfg["origin_file"] = file_path
                            TStudioCore.save_config(cfg)
                            return csv_out
                except Exception as e:
                    print(f"UTMT extract error: {e}")
                    
                try:
                    if file_path.lower().endswith('.txt'):
                        import re, csv as _csv
                        with open(file_path, 'r', encoding='utf-8-sig', errors='replace') as f:
                            raw = f.readlines()
                        
                        # Detect TellTale format: lines starting with "N) " or "N) CHARACTER"
                        id_pattern = re.compile(r'^(\d+)\)\s*(.*)')
                        entries = []
                        i = 0
                        while i < len(raw):
                            m = id_pattern.match(raw[i].strip())
                            if m:
                                line_id = m.group(1)
                                character = m.group(2).strip()
                                text = ''
                                if i + 1 < len(raw):
                                    next_line = raw[i + 1].strip()
                                    if next_line and not id_pattern.match(next_line):
                                        text = next_line
                                        i += 1  # consume text line
                                entries.append((line_id, character, text))
                            i += 1
                        
                        # Need at least 10 entries to be confident it's TellTale format
                        if len(entries) >= 5:
                            import os as _os
                            base = _os.path.splitext(file_path)[0]
                            csv_out = base + '_telltale.csv'
                            with open(csv_out, 'w', encoding='utf-8-sig', newline='') as f:
                                writer = _csv.writer(f)
                                writer.writerow([_("col_id"), _("col_source"), _("col_translation"), 'AI_Reference'])
                                for (lid, char, text) in entries:
                                    if text:  # skip empty lines
                                        row_id = f"{lid}"
                                        if char:
                                            row_id = f"{lid}_{char.replace(' ', '_')}"
                                        writer.writerow([row_id, text, '', char])
                            return csv_out
                except Exception as e:
                    print(f"TellTale txt parse error: {e}")

                try:
                    if file_path.lower().endswith('.json'):
                        import json as _json, csv as _csv, os as _os
                        with open(file_path, 'r', encoding='utf-8') as f:
                            jdata = _json.load(f)
                            
                        entries = []
                        # 1. c2dictionary (Construct 2/3)
                        if isinstance(jdata, dict) and jdata.get("c2dictionary") is True and "data" in jdata:
                            for k, v in jdata["data"].items():
                                entries.append((k, str(v)))
                        # 2. Flat dict: {"key": "value"}
                        elif isinstance(jdata, dict):
                            for k, v in jdata.items():
                                if isinstance(v, (str, int, float, bool)):
                                    entries.append((k, str(v)))
                        # 3. List of dicts
                        elif isinstance(jdata, list):
                            for i, item in enumerate(jdata):
                                if isinstance(item, dict):
                                    if "id" in item and "text" in item:
                                        entries.append((str(item["id"]), str(item["text"])))
                                    elif "key" in item and "value" in item:
                                        entries.append((str(item["key"]), str(item["value"])))
                                    else:
                                        entries.append((f"row_{i}", _json.dumps(item, ensure_ascii=False)))
                                elif isinstance(item, str):
                                    entries.append((f"row_{i}", item))
                                    
                        if entries:
                            base = _os.path.splitext(file_path)[0]
                            csv_out = base + '_parsed.csv'
                            with open(csv_out, 'w', encoding='utf-8-sig', newline='') as f:
                                writer = _csv.writer(f)
                                writer.writerow([_("col_id"), _("col_source"), _("col_translation"), 'AI_Reference'])
                                for lid, text in entries:
                                    writer.writerow([lid, text, '', ''])
                            return csv_out
                except Exception as e:
                    print(f"JSON parse error: {e}")
                    
                return file_converter.auto_convert_to_csv(file_path, None) # Don't pass UI to thread
                
            def on_success(converted_path):
                QApplication.restoreOverrideCursor()
                if converted_path:
                    self.project_path = None
                    self.setWindowTitle("Translation Studio - Unsaved Project")
                    from tstudio_core import TFormatManager
                    if not TFormatManager.is_standard_csv(converted_path):
                        headers = TFormatManager.get_headers(converted_path)
                        from tstudio_ui_shared import SmartImportDialog
                        dlg = SmartImportDialog(headers, self)
                        if dlg.exec() == QDialog.DialogCode.Accepted:
                            mapping = dlg.get_mapping()
                            try:
                                converted_path = TFormatManager.format_to_standard(converted_path, mapping)
                                QMessageBox.information(self, _("tformat_title"), _("tformat_formatted_msg"))
                            except Exception as e:
                                QMessageBox.critical(self, _("error_title"), f"Failed to format: {e}")
                                return
                        else:
                            return
                    self.csv_path = converted_path
                    
                    # Save origin_file in config!
                    from tstudio_core import TStudioCore
                    cfg = TStudioCore.load_config()
                    cfg["origin_file"] = file_path
                    TStudioCore.save_config(cfg)
                    
                    self._load_csv()
                    
            def on_error(err):
                QApplication.restoreOverrideCursor()
                QMessageBox.critical(self, _("file_error_title"), f"Failed to open or convert file:\n{err}")
                
            worker = ApiWorker(run_convert)
            forwarder = ThreadSafeWorkerSignalsForwarder(on_success, on_error, self)
            worker.signals.finished.connect(forwarder.handle_finished)
            worker.signals.error.connect(forwarder.handle_error)
            self.threadpool.start(worker)


    def open_telltale_archive(self, file_path=None):
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        from PyQt6.QtCore import Qt
        from PyQt6.QtWidgets import QApplication
        import os
        
        if file_path is None:
            file_path, _ext = QFileDialog.getOpenFileName(self, _("select_telltale_title"), BASE_DIR, "Telltale Archives (*.ttarch2);;All Files (*.*)")
        if not file_path:
            return
            
        manager = TelltaleManager()
        missing = manager.check_tools()
        if missing:
            QMessageBox.critical(self, _("telltale_tools_missing_title"), f"Cannot extract Telltale archives because the following tools are missing:\n{', '.join(missing)}\n\nPlease download them and place them in the 'telltale_tools' folder inside 'Core'.")
            return
            
        self.statusBar().showMessage(f"Extracting {os.path.basename(file_path)}...")
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        
        proj_dir = os.path.dirname(file_path)
        temp_dir = os.path.join(proj_dir, ".tstudio_temp", os.path.basename(file_path).replace('.', '_'))
        
        success, msg = manager.extract_ttarch2(file_path, temp_dir)
        QApplication.restoreOverrideCursor()
        
        if not success:
            QMessageBox.critical(self, _("extraction_error_title"), f"Failed to extract archive:\n{msg}")
            return
            
        # Auto-detect English .landb files
        import glob
        landb_files = glob.glob(os.path.join(temp_dir, "*english.landb"))
        if not landb_files:
            landb_files = glob.glob(os.path.join(temp_dir, "*.landb"))
            
        if not landb_files:
            QMessageBox.warning(self, _("no_landb_title"), f"No translation files found in the archive.\n{temp_dir}")
            return
            
        # We will merge ALL found .landb files into one CSV!
        csv_path = os.path.join(temp_dir, "combined_translation.landb.csv")
        try:
            manager.convert_landb_to_csv(landb_files, csv_path)
            self.csv_path = csv_path
            self._load_csv()
            QMessageBox.information(self, _("success_title"), _("loaded_telltale_success"))
        except Exception as e:
            QMessageBox.critical(self, _("error_title"), f"Failed to parse .landb:\n{str(e)}")
    def update_html_sources(self):
        if getattr(self, '_updating_html', False):
            return
        self._updating_html = True
        try:
            from tstudio_core import TStudioCore
            profile = TStudioCore.get_current_profile_data()
            glossary = profile.get("glossary", {})
            if not glossary:
                return
            
            sorted_glossary = sorted(glossary.items(), key=lambda x: len(x[0]), reverse=True)
            import re
            
            # compile patterns for speed
            patterns = []
            for eng, val in sorted_glossary:
                eng_str = eng.strip()
                if not eng_str: continue
                patterns.append( (re.compile(r'\b(' + re.escape(html.escape(eng_str)) + r')\b', re.IGNORECASE), eng_str) )
                
            for item in self.model._data:
                source_text = item["source"]
                html_source = html.escape(source_text)
                for pat, eng_str in patterns:
                    if pat.search(html_source):
                        html_source = pat.sub(r'<span style="background-color:#f9e2af; color:#11111b; font-weight:bold; padding:0 2px; border-radius:2px;">\1</span>', html_source)
                item["html_source"] = html_source
                
            self.model.layoutChanged.emit()
        finally:
            self._updating_html = False

    def on_row_selected(self, current, previous):
        # Flush any pending changes before changing the selected row
        if hasattr(self, '_trans_save_timer') and self._trans_save_timer.isActive():
            self._trans_save_timer.stop()
            self.on_trans_changed()

        # Save immediately on row change if there are unsaved changes
        if hasattr(self, '_csv_auto_save_timer') and self._csv_auto_save_timer.isActive():
            self._csv_auto_save_timer.stop()
            self.silent_save_csv()

        if not current.isValid():
            self.current_source_row = -1
            for w in [self.txt_source, self.txt_ai, self.txt_trans]:
                w.blockSignals(True)
                w.clear()
                w.blockSignals(False)
            return
        src = self.proxy.mapToSource(current)
        row = src.row()
        # Guard: bounds check in case the model was reset (e.g. Find & Replace) between
        # the selection signal and this handler executing.
        if row < 0 or row >= len(self.model._data):
            return
        self.current_source_row = row
        item = self.model._data[self.current_source_row]
        source_text = item["source"].replace('\\n', '\n')
        
        # --- GLOSSARY MARKER SYSTEM ---
        profile = TStudioCore.get_current_profile_data()
        glossary = profile.get("glossary", {})
        matched_terms = []
        highlighted_source = html.escape(source_text)
        
        is_marker_enabled = True
        if hasattr(self, 'act_toggle_qa_marker') and not self.act_toggle_qa_marker.isChecked():
            is_marker_enabled = False
            
        if is_marker_enabled and glossary and hasattr(self, 'lbl_glossary_cheat'):
            import re
            # Sort glossary by length descending so longer terms match first
            sorted_glossary = sorted(glossary.items(), key=lambda x: len(x[0]), reverse=True)
            for eng, val in sorted_glossary:
                eng_str = eng.strip()
                if not eng_str: continue
                
                # Check for word boundary match (case insensitive) against escaped text
                pattern = r'\b(' + re.escape(html.escape(eng_str)) + r')\b'
                if re.search(pattern, highlighted_source, re.IGNORECASE):
                    thai = val[0] if isinstance(val, list) else val
                    matched_terms.append(f"{eng_str} ({thai})")
                    # Highlight in HTML
                    highlighted_source = re.sub(pattern, r'<span style="background-color:#f9e2af; color:#11111b; font-weight:bold; padding:0 2px; border-radius:2px;">\1</span>', highlighted_source, flags=re.IGNORECASE)
            
            if matched_terms:
                self.lbl_glossary_cheat.setText(_("glossary_cheat").format(terms=", ".join(matched_terms)))
                self.lbl_glossary_cheat.show()
                # Use setHtml if there are highlights, replace newlines with <br>
                self.txt_source.blockSignals(True)
                html_source = highlighted_source.replace('\n', '<br>')
                self.txt_source.setHtml(f'<div style="font-family: inherit; font-size: inherit; white-space: pre-wrap;">{html_source}</div>')
                self.txt_source.blockSignals(False)
            else:
                self.lbl_glossary_cheat.hide()
                self.txt_source.blockSignals(True)
                self.txt_source.setPlainText(source_text)
                self.txt_source.blockSignals(False)
        else:
            if hasattr(self, 'lbl_glossary_cheat'): self.lbl_glossary_cheat.hide()
            self.txt_source.blockSignals(True)
            self.txt_source.setPlainText(source_text)
            self.txt_source.blockSignals(False)
            
        # Update AI and Trans boxes
        for w, val in [(self.txt_ai, item.get("ai_ref", "")), (self.txt_trans, item["trans"])]:
            w.blockSignals(True)
            w.setPlainText(val.replace('\\n', '\n'))
            w.blockSignals(False)

    def on_trans_changed(self):
        if self.current_source_row >= 0:
            # Guard: bounds check — model may have been reset (e.g. Find & Replace) while
            # the save-timer was pending, making current_source_row stale.
            if self.current_source_row >= len(self.model._data):
                return
            old_text = self.model._data[self.current_source_row]["trans"]
            new_text = self.txt_trans.toPlainText().replace('\n', '\\n')
            if old_text != new_text:
                self.model.update_trans(self.current_source_row, new_text)
                self._update_stats_for_row(self.current_source_row, old_text, new_text)

    def _on_table_data_changed(self, top_left, bottom_right, roles):
        if not roles or Qt.ItemDataRole.EditRole in roles:
            # Table cell was edited directly
            if self.current_source_row >= top_left.row() and self.current_source_row <= bottom_right.row():
                if top_left.column() <= 4 <= bottom_right.column():
                    # Update text box to match table
                    item = self.model._data[self.current_source_row]
                    self.txt_trans.blockSignals(True)
                    self.txt_trans.setPlainText(item["trans"].replace('\\n', '\n'))
                    self.txt_trans.blockSignals(False)
                    self.update_progress_stats()

    def on_model_data_changed(self, topLeft, bottomRight, roles):
        if hasattr(self, '_csv_auto_save_timer'):
            self._csv_auto_save_timer.start(2000) # Save 2 seconds after data change

    def _load_api_config(self):
        try:
            return TStudioCore.load_config()
        except Exception as e:
            print(f"Error loading API config: {e}")
            return {
                "google_key": "", "anthropic_key": "", "deepseek_key": "", "openai_key": "",
                "model": "deepseek-chat", "local_url": "http://localhost:1234/v1/chat/completions"
            }

    def _apply_glossary(self, text):
        profile = TStudioCore.get_current_profile_data()
        for wrong, val in profile.get("glossary", {}).items():
            right = val[0] if isinstance(val, list) else val
            text = text.replace(wrong, right)
        return text

    def _check_qa_bytes(self, text):
        # FIX: max_bytes_limit is a per-profile setting, not a global config key.
        # Reading it from load_config() always returned 0 and the guard never fired.
        from tstudio_core import TStudioCore
        profile = TStudioCore.get_current_profile_data()
        if profile.get("max_bytes_limit", 0) > 0:
            limit = profile["max_bytes_limit"]
            encoded = text.encode('utf-8')
            if len(encoded) > limit:
                # truncate at character boundary
                truncated = b""
                for char in text:
                    char_bytes = char.encode('utf-8')
                    if len(truncated) + len(char_bytes) > limit:
                        break
                    truncated += char_bytes
                return truncated.decode('utf-8')
        return text

    def _inject_glossary_to_prompt(self, prompt, source_text):
        if hasattr(self, 'chk_use_tlm') and not self.chk_use_tlm.isChecked():
            return prompt
            
        profile = TStudioCore.get_current_profile_data()
        glossary = profile.get("glossary", {})
            
        matched_terms = []
        source_lower = source_text.lower()
        
        for eng, val in glossary.items():
            eng_str = eng.strip()
            if not eng_str: continue
            
            thai = val[0] if isinstance(val, list) else val
            
            pattern = r'\b' + re.escape(eng_str.lower()) + r'\b'
            if re.search(pattern, source_lower):
                matched_terms.append(f"- {eng_str} -> {thai}")
                
        if matched_terms:
            rules = "\n\nCRITICAL TERMINOLOGY RULES:\nYou MUST use the following specific translations for these terms:\n" + "\n".join(matched_terms)
            return prompt + rules
            
        return prompt


    def retranslate_name(self):
        if self.current_source_row < 0: return
        item = self.model._data[self.current_source_row]
        if not item["source"].strip(): return
        cfg = TStudioCore.load_config()
        self.statusBar().showMessage("Translating (Transliterate)...")
        self.btn_trans_smart.setEnabled(False)
        source_text = item["source"].replace('\\n', '\n')
        
        prompt = f"You are a translator. The following text is a proper noun (e.g. character name, location). Your task is to TRANSLITERATE it into Thai pronunciation (แปลทับศัพท์) WITHOUT translating its meaning. For example: 'Weaver' -> 'วีเวอร์', 'Salvage Yard' -> 'ซัลเวจยาร์ด', 'John' -> 'จอห์น'. Return ONLY the transliterated Thai text.\n\nOriginal Text: {source_text}"
        
        safeguard = "\n\nCRITICAL RULES:\n- DO NOT translate or include the Context ID in your output.\n- Return ONLY the translation.\n- Preserve all UI/game tags like {...}, [...], <...> exactly as they appear."
        prompt += safeguard

        worker = ApiWorker(CoreAI.generate_content, cfg, prompt)
        forwarder = ThreadSafeWorkerSignalsForwarder(
            on_success=self._on_name_success,
            on_error=lambda err: self._on_retranslate_error(err, self.btn_trans_smart),
            parent=self
        )
        worker.signals.finished.connect(forwarder.handle_finished)
        worker.signals.error.connect(forwarder.handle_error)
        wid = id(worker)
        worker.signals.finished.connect(lambda _, w_id=wid: self._workers.pop(w_id, None))
        worker.signals.error.connect(lambda _, w_id=wid: self._workers.pop(w_id, None))
        self._workers[wid] = worker
        self.threadpool.start(worker)

    def _on_name_success(self, reply):
        self.btn_trans_smart.setEnabled(True)
        translated = self._apply_glossary(re.sub(r'^"|"$', '', reply))
        self.txt_trans.setPlainText(translated)
        self.statusBar().showMessage(_("retranslated_status"), 3000)


    def retranslate_smart(self):
        selected_indexes = self.table.selectionModel().selectedRows()
        if not selected_indexes:
            # If nothing selected, try to translate current source row
            if self.current_source_row >= 0:
                self.retranslate_single()
            else:
                QMessageBox.information(self, _("no_selection_title"), _("no_selection_msg"))
            return
            
        rows = sorted(list(set(self.proxy.mapToSource(idx).row() for idx in selected_indexes)))
        rows_to_translate = [r for r in rows if self.model._data[r]["source"].strip()]
        
        if len(rows_to_translate) > 1:
            self.retranslate_batch()
        elif len(rows_to_translate) == 1:
            self.current_source_row = rows_to_translate[0]
            self.retranslate_single()
        else:
            QMessageBox.information(self, _("no_content_title"), _("no_content_msg"))

    def show_special_translation_menu_at_cursor(self):
        if hasattr(self, 'special_menu'):
            from PyQt6.QtGui import QCursor
            self.special_menu.exec(QCursor.pos())

    def retranslate_single(self):
        if self.current_source_row < 0: return
        item = self.model._data[self.current_source_row]
        if not item["source"].strip(): return
        cfg = TStudioCore.load_config()
        self.statusBar().showMessage(_("translating_status_simple"))
        self.btn_trans_smart.setEnabled(False)
        source_text = item["source"].replace('\\n', '\n')
        
        profile = TStudioCore.get_current_profile_data()
        s_prompt = profile.get('single', DEFAULT_SINGLE_PROMPT)
        prompt = s_prompt.replace('{id}', item["id"]).replace('{source_text}', source_text)
        prompt = self._inject_glossary_to_prompt(prompt, source_text)
        
        # --- SAFEGUARD: Force rules if not explicitly present in the final prompt ---
        safeguard = "\n\nCRITICAL RULES:\n- DO NOT translate or include the Context ID in your output.\n- Return ONLY the translation.\n- Preserve all UI/game tags like {...}, [...], <...> exactly as they appear."
        if "Context ID" not in prompt and "UI/game tags" not in prompt:
            prompt += safeguard

        worker = ApiWorker(CoreAI.generate_content, cfg, prompt)
        forwarder = ThreadSafeWorkerSignalsForwarder(
            on_success=self._on_single_success,
            on_error=lambda err: self._on_retranslate_error(err, self.btn_trans_smart),
            parent=self
        )
        worker.signals.finished.connect(forwarder.handle_finished)
        worker.signals.error.connect(forwarder.handle_error)
        wid = id(worker)
        worker.signals.finished.connect(lambda _, w_id=wid: self._workers.pop(w_id, None))
        worker.signals.error.connect(lambda _, w_id=wid: self._workers.pop(w_id, None))
        self._workers[wid] = worker
        self.threadpool.start(worker)

    def _on_single_success(self, reply):
        self.btn_trans_smart.setEnabled(True)
        translated = self._apply_glossary(re.sub(r'^"|"$', '', reply))
        row = self.current_source_row

        if getattr(self, 'chk_guide_mode', None) and self.chk_guide_mode.isChecked():
            # Guide Mode: route to ai_ref column
            new_text = translated.replace('\n', '\\n')
            self.model.update_ai_ref(row, new_text)
            self.txt_ai.setPlainText(translated.replace('\\n', '\n'))
            self.statusBar().showMessage("[Guide] แปลเสร็จ — ดูได้ที่ช่อง AI Translation", 4000)
        else:
            self.txt_trans.setPlainText(translated)
            self.statusBar().showMessage(_("retranslated_status"), 3000)

    def _on_retranslate_error(self, err_msg, btn):
        btn.setEnabled(True)
        QMessageBox.critical(self, _("failed_title"), str(err_msg))
        self.statusBar().showMessage(_("translation_failed_status"), 3000)

    def _on_guide_mode_toggled(self, checked: bool):
        """Visual feedback when Guide Mode is toggled on/off."""
        if checked:
            self.statusBar().showMessage(
                "🧭 Guide Mode เปิด — AI จะแปลไปยังช่อง AI Translation เพื่อเป็นไกด์", 4000
            )
            self.chk_guide_mode.setText("🧭 Guide Mode ✓")
        else:
            self.statusBar().showMessage(
                "Guide Mode ปิด — กลับสู่โหมดปกติ", 3000
            )
            self.chk_guide_mode.setText("🧭 Guide Mode")
            
        # Update buttons to reflect guide mode styling
        self.update_button_labels()

    def retranslate_special(self, mode):
        if self.current_source_row < 0: return
        item = self.model._data[self.current_source_row]
        if not item["source"].strip(): return
        cfg = TStudioCore.load_config()
        self.statusBar().showMessage(f"Translating ({mode})...")
        self.btn_trans_special.setEnabled(False)
        source_text = item["source"].replace('\\n', '\n')
        
        mode_text = ""
        length_constraint = "Keep your translation CONCISE. Match the length and structure of the original text as closely as possible. Do NOT write paragraphs if the original is a short sentence."
        
        if mode == "transliterate":
            mode_text = "TRANSLITERATE (แปลทับศัพท์) the original text into Thai pronunciation WITHOUT translating its meaning. Return ONLY the transliterated word."
        elif mode == "idiom":
            mode_text = f"Analyze the underlying meaning carefully. Translate into a natural, contextually appropriate Thai idiom or phrase (สำนวน/คำพังเพย). {length_constraint}"
        elif mode == "poem":
            mode_text = f"Translate into an elegant Thai poetic form (กลอน/บทกวี/คาถา) with appropriate rhyming. {length_constraint}"
        elif mode == "quote":
            mode_text = f"Translate into formal, philosophical, and impactful Thai language (คำคม/ปรัชญา), similar to a famous historical quote. {length_constraint}"
        elif mode == "mature":
            mode_text = f"Translate aggressively using mature, unfiltered, or profane Thai language (หยาบคาย/ดุดัน) appropriate for a gritty action game. {length_constraint}"
        elif mode == "fantasy":
            mode_text = f"Translate using medieval, fantasy, or archaic Thai language (ย้อนยุค/แฟนตาซี) (e.g., ข้า, เจ้า, ฝ่าบาท). {length_constraint}"
        elif mode == "robotic":
            mode_text = f"Translate into cold, systemic, robotic Thai language (ประกาศจากระบบ/AI) (e.g., ตรวจพบ, ระบบขัดข้อง). {length_constraint}"
        elif mode == "casual":
            mode_text = f"Translate into modern, casual, or sarcastic Thai slang (วัยรุ่น/กวนๆ) suitable for natural youth conversation. {length_constraint}"
            
        prompt = f"You are a Master-Level English-to-Thai Video Game Localization Specialist for '{GAME_NAME}'.\n{mode_text}\n\nCRITICAL LORE AWARENESS: You MUST strictly adhere to the Glossary/Terminology provided below for any recognized terms.\nContext ID: '{item['id']}'.\n\nOriginal Text: {source_text}"

        prompt = self._inject_glossary_to_prompt(prompt, source_text)
        
        safeguard = "\n\nCRITICAL RULES:\n- DO NOT translate or include the Context ID in your output.\n- Return ONLY the translation.\n- Preserve all UI/game tags like {...}, [...], <...> exactly as they appear."
        if "Context ID" not in prompt and "UI/game tags" not in prompt:
            prompt += safeguard
        
        is_local = (cfg.get("provider", "") == "Local LLM" or cfg.get("model", "") == "custom-local-llm")
        worker = ApiWorker(CoreAI.generate_content, cfg, prompt, is_local=is_local)
        forwarder = ThreadSafeWorkerSignalsForwarder(
            on_success=lambda reply: self._on_special_success(reply, mode),
            on_error=lambda err: self._on_retranslate_error(err, self.btn_trans_special),
            parent=self
        )
        worker.signals.finished.connect(forwarder.handle_finished)
        worker.signals.error.connect(forwarder.handle_error)
        wid = id(worker)
        worker.signals.finished.connect(lambda _, w_id=wid: self._workers.pop(w_id, None))
        worker.signals.error.connect(lambda _, w_id=wid: self._workers.pop(w_id, None))
        self._workers[wid] = worker
        self.threadpool.start(worker)

    def _on_special_success(self, reply, mode):
        self.btn_trans_special.setEnabled(True)
        translated = self._apply_glossary(re.sub(r'^"|"$', '', reply))
        row = self.current_source_row
        
        if getattr(self, 'chk_guide_mode', None) and self.chk_guide_mode.isChecked():
            new_text = translated.replace('\n', '\\n')
            self.model.update_ai_ref(row, new_text)
            self.txt_ai.setPlainText(translated.replace('\\n', '\n'))
            self.statusBar().showMessage(f"[Guide] แปลเสร็จ ({mode}) — ดูได้ที่ช่อง AI Translation", 4000)
        else:
            self.txt_trans.setPlainText(translated)
            self.statusBar().showMessage(f"Re-translated as {mode}!", 3000)

    def retranslate_options(self):
        if self.current_source_row < 0: return
        item = self.model._data[self.current_source_row]
        if not item["source"].strip(): return
        cfg = TStudioCore.load_config()
        self.statusBar().showMessage(_("fetching_3_options"))
        self.btn_trans_opt.setEnabled(False)
        source_text = item["source"].replace('\\n', '\n')
        
        profile = TStudioCore.get_current_profile_data()
        o_prompt = profile.get('opt', DEFAULT_OPTIONS_PROMPT)
        prompt = o_prompt.replace('{id}', item["id"]).replace('{source_text}', source_text)
        prompt = self._inject_glossary_to_prompt(prompt, source_text)
        
        # --- SAFEGUARD: Force rules if not explicitly present in the final prompt ---
        safeguard = "\n\nCRITICAL RULES:\n- DO NOT translate or include the Context ID in your output.\n- Return ONLY the JSON array.\n- Preserve all UI/game tags like {...}, [...], <...> exactly as they appear."
        if "Context ID" not in prompt and "UI/game tags" not in prompt:
            prompt += safeguard

        worker = ApiWorker(CoreAI.generate_content, cfg, prompt)
        forwarder = ThreadSafeWorkerSignalsForwarder(
            on_success=self._on_options_success,
            on_error=lambda err: self._on_retranslate_error(err, self.btn_trans_opt),
            parent=self
        )
        worker.signals.finished.connect(forwarder.handle_finished)
        worker.signals.error.connect(forwarder.handle_error)
        wid = id(worker)
        worker.signals.finished.connect(lambda _, w_id=wid: self._workers.pop(w_id, None))
        worker.signals.error.connect(lambda _, w_id=wid: self._workers.pop(w_id, None))
        self._workers[wid] = worker
        self.threadpool.start(worker)

    def _on_options_success(self, reply):
        self.btn_trans_opt.setEnabled(True)
        clean_reply = re.sub(r'^```[^\n]*\n?|\n?```$', '', reply.strip(), flags=re.MULTILINE)
        try:
            options = json.loads(clean_reply)
            if not isinstance(options, list) or len(options) == 0: raise ValueError()
        except:
            QMessageBox.warning(self, _("parse_error_title"), f"AI returned invalid format:\n{reply}")
            return
        options = [self._apply_glossary(o) for o in options]
        dlg = TranslationOptionsDialog(self, options)
        if dlg.exec() and dlg.selected_text:
            row = self.current_source_row
            if getattr(self, 'chk_guide_mode', None) and self.chk_guide_mode.isChecked():
                new_text = dlg.selected_text.replace('\n', '\\n')
                self.model.update_ai_ref(row, new_text)
                self.txt_ai.setPlainText(dlg.selected_text)
                self.statusBar().showMessage(_("guide_mode_translated"), 4000)
            else:
                self.txt_trans.setPlainText(dlg.selected_text)
                self.statusBar().showMessage(_("done_status"), 3000)

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
        forwarder = ThreadSafeWorkerSignalsForwarder(
            on_success=lambda reply: self._on_local_success(reply),
            on_error=lambda err: self._on_local_error(err),
            parent=self
        )
        worker.signals.finished.connect(forwarder.handle_finished)
        worker.signals.error.connect(forwarder.handle_error)
        wid = id(worker)
        worker.signals.finished.connect(lambda _, w_id=wid: self._workers.pop(w_id, None))
        worker.signals.error.connect(lambda _, w_id=wid: self._workers.pop(w_id, None))
        self._workers[wid] = worker
        self.threadpool.start(worker)

    def _on_local_success(self, reply):
        translated = self._apply_glossary(re.sub(r'^"|"$', '', reply))
        row = self.current_source_row
        
        if getattr(self, 'chk_guide_mode', None) and self.chk_guide_mode.isChecked():
            new_text = translated.replace('\n', '\\n')
            self.model.update_ai_ref(row, new_text)
            self.txt_ai.setPlainText(translated.replace('\\n', '\n'))
            self.statusBar().showMessage("[Guide] แปลเสร็จ (Local AI) — ดูได้ที่ช่อง AI Translation", 4000)
        else:
            self.txt_trans.setPlainText(translated)
            self.statusBar().showMessage("Re-translated with Local AI!", 3000)

    def _on_local_error(self, err):
        QMessageBox.critical(self, _("failed_title"), f"Is your Local LLM running?\n\nError: {err}")

    def retranslate_batch(self):
        selected_indexes = self.table.selectionModel().selectedRows()
        if not selected_indexes:
            QMessageBox.information(self, _("no_selection_title"), _("no_selection_msg"))
            return
            
        rows = sorted(list(set(self.proxy.mapToSource(idx).row() for idx in selected_indexes)))
        
        # Filter out empty source rows
        rows_to_translate = [r for r in rows if self.model._data[r]["source"].strip()]
        if not rows_to_translate:
            QMessageBox.information(self, _("no_content_title"), _("no_content_msg"))
            return
            
        # Confirm with user if they select many rows
        if len(rows_to_translate) > 5:
            reply = QMessageBox.question(
                self, _("confirm_batch_title"),
                f"ต้องการแปลภาษา {len(rows_to_translate)} บรรทัดที่เลือกใช่หรือไม่?\n(การแปลจะทำงานแบบขนานในเบื้องหลัง)",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return

        # Initialize batch state
        self._batch_total = len(rows_to_translate)
        self._batch_completed = 0
        self._batch_errors = []
        self._batch_done_shown = False  # Guard: prevent duplicate completion dialogs
        self._start_batch_progress(self._batch_total)
        
        # Disable all AI translation buttons during batch translation
        self.btn_trans_smart.setEnabled(False)
        self.btn_trans_opt.setEnabled(False)
        self.btn_trans_special.setEnabled(False)
        if hasattr(self, 'btn_trans_batch'):
            self.btn_trans_batch.setEnabled(False)
        
        self.statusBar().showMessage(_("batch_translating_status").format(current=0, total=self._batch_total))
        
        cfg = TStudioCore.load_config()
        profile = TStudioCore.get_current_profile_data()
        s_prompt = profile.get('single', DEFAULT_SINGLE_PROMPT)
        
        # Validate API settings once before running batch
        try:
            model = cfg.get("model", "")
            is_local = (cfg.get("provider", "") == "Local LLM" or model == "custom-local-llm")
            if not is_local:
                if model.startswith("gemini") and not cfg.get("google_key"):
                    raise Exception("Google Gemini API Key is missing!")
                elif model.startswith("claude") and not cfg.get("anthropic_key"):
                    raise Exception("Anthropic Claude API Key is missing!")
                elif model.startswith("deepseek") and not cfg.get("deepseek_key"):
                    raise Exception("DeepSeek API Key is missing!")
                elif (model.startswith("gpt") or model.startswith("o1") or model.startswith("o3") or model.startswith("o4")) and not cfg.get("openai_key"):
                    raise Exception("OpenAI API Key is missing!")
        except Exception as e:
            QMessageBox.critical(self, _("api_key_error_title"), f"ไม่สามารถเริ่มแปลได้:\n{e}\n\nกรุณาตั้งค่า API Key ใน Settings")
            self.btn_trans_smart.setEnabled(True)
            self.btn_trans_opt.setEnabled(True)
            self.btn_trans_special.setEnabled(True)
            if hasattr(self, 'btn_trans_batch'):
                if hasattr(self, 'btn_trans_batch'): self.btn_trans_batch.setEnabled(True)
            return

        for row in rows_to_translate:
            item = self.model._data[row]
            source_text = item["source"].replace('\\n', '\n')
            prompt = s_prompt.replace('{id}', item["id"]).replace('{source_text}', source_text)
            prompt = self._inject_glossary_to_prompt(prompt, source_text)
            
            safeguard = "\n\nCRITICAL RULES:\n- DO NOT translate or include the Context ID in your output.\n- Return ONLY the translation.\n- Preserve all UI/game tags like {...}, [...], <...> exactly as they appear."
            if "Context ID" not in prompt and "UI/game tags" not in prompt:
                prompt += safeguard
                
            worker = ApiWorker(CoreAI.generate_content, cfg, prompt, is_local=is_local)
            
            forwarder = ThreadSafeWorkerSignalsForwarder(
                on_success=lambda reply, r=row: self._on_batch_row_success(reply, r),
                on_error=lambda err, r=row: self._on_batch_row_error(err, r),
                parent=self
            )
            worker.signals.finished.connect(forwarder.handle_finished)
            worker.signals.error.connect(forwarder.handle_error)
            wid = id(worker)
            worker.signals.finished.connect(lambda _, w_id=wid: self._workers.pop(w_id, None))
            worker.signals.error.connect(lambda _, w_id=wid: self._workers.pop(w_id, None))
            self._workers[wid] = worker
            self.threadpool.start(worker)

    def _on_batch_row_success(self, reply, row):
        # Guard against late-arriving callbacks after the window has been closed.
        if getattr(self, '_is_closing', False):
            return
        translated = self._apply_glossary(re.sub(r'^"|"$', '', reply))
        new_text = translated.replace('\n', '\\n')

        guide_mode = getattr(self, 'chk_guide_mode', None) and self.chk_guide_mode.isChecked()

        if guide_mode:
            # Guide Mode: write to ai_ref column only
            self.model.update_ai_ref(row, new_text)
            if row == self.current_source_row:
                self.txt_ai.blockSignals(True)
                self.txt_ai.setPlainText(translated.replace('\\n', '\n'))
                self.txt_ai.blockSignals(False)
        else:
            old_text = self.model._data[row]["trans"]
            self.model.update_trans(row, new_text)
            self._update_stats_for_row(row, old_text, new_text)
            if row == self.current_source_row:
                self.txt_trans.blockSignals(True)
                self.txt_trans.setPlainText(translated.replace('\\n', '\n'))
                self.txt_trans.blockSignals(False)

        self._batch_completed += 1
        self._update_batch_progress()

    def _on_batch_row_error(self, err, row):
        # FIX: Guard against late-arriving callbacks after the window has been closed.
        if getattr(self, '_is_closing', False):
            return
        self._batch_errors.append((row, str(err)))
        self._batch_completed += 1
        self._update_batch_progress()

    def _update_batch_progress(self):
        if getattr(self, '_is_closing', False):
            return
        if self._batch_completed < self._batch_total:
            # Update mini progress bar
            pct = int(self._batch_completed / self._batch_total * 100)
            if hasattr(self, '_batch_mini_bar'):
                self._batch_mini_bar.setValue(pct)
                self._batch_count_label.setText(f"{self._batch_completed} / {self._batch_total}")
            self.statusBar().showMessage(
                _("batch_translating_status").format(current=self._batch_completed, total=self._batch_total)
            )
        else:
            # Guard: multiple workers finishing simultaneously may each see
            # _batch_completed == _batch_total; only show the dialog once.
            if getattr(self, '_batch_done_shown', False):
                return
            self._batch_done_shown = True

            # Update progress to 100% and show finish state
            if hasattr(self, '_batch_mini_bar'):
                self._batch_mini_bar.setValue(100)
                self._batch_count_label.setText(f"{self._batch_total} / {self._batch_total}")
            success_count = self._batch_total - len(self._batch_errors)
            self._finish_batch_progress(success_count, self._batch_total)

            self.btn_trans_smart.setEnabled(True)
            self.btn_trans_opt.setEnabled(True)
            self.btn_trans_special.setEnabled(True)
            if hasattr(self, 'btn_trans_batch'):
                self.btn_trans_batch.setEnabled(True)
            if self._batch_errors:
                err_msgs = [f"แถวที่ {r+1}: {e}" for r, e in self._batch_errors[:5]]
                if len(self._batch_errors) > 5:
                    err_msgs.append(f"...และอีก {len(self._batch_errors) - 5} รายการ")
                QMessageBox.warning(
                    self, _("batch_complete_with_errors"),
                    f"แปลเสร็จสิ้นแล้ว แต่พบบั๊กหรือข้อผิดพลาดบางรายการ:\n\n" + "\n".join(err_msgs)
                )
                self.statusBar().showMessage(_("batch_translated_status").format(total=self._batch_total), 5000)
            else:
                self.statusBar().showMessage(_("batch_translated_status").format(total=self._batch_total), 5000)
                QMessageBox.information(self, _("success_title"), _("batch_translated_msg").format(total=self._batch_total))


    def export_pua_csv(self):
        if not self.csv_path:
            QMessageBox.warning(self, _("error_title"), _("csv_path_not_configured"))
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
            QMessageBox.information(self, _("export_pua_success_title"), f"Successfully exported to:\n{os.path.basename(pua_path)}\n\nReplaced +{diff} PUA characters.")
        except Exception as e:
            QMessageBox.critical(self, _("export_error_title"), str(e))

    def export_original(self):
        if not getattr(self, 'csv_path', None):
            QMessageBox.warning(self, "No File", _("please_open_file_first"))
            return
            
        # ── LANG Export logic ──
        meta_path = self.csv_path.replace(".csv", "_meta.json")
        if os.path.exists(meta_path):
            self.save_csv()
            out_lang, _ext = QFileDialog.getSaveFileName(self, "Export to LANG File", BASE_DIR, "LANG Files (*.lang)")
            if not out_lang:
                return
            self.statusBar().showMessage("Exporting to LANG file...")
            try:
                reconstruct_lang_file(self.csv_path, meta_path, out_lang)
                self.statusBar().showMessage(f"Exported successfully to {os.path.basename(out_lang)}", 5000)
                QMessageBox.information(self, _("export_success_title"), f"Successfully exported LANG file at:\n{out_lang}")
            except Exception as e:
                QMessageBox.critical(self, _("export_error_title"), f"Failed to export LANG file:\n{e}")
            return

        try:
            from tbundle_manager import TBundleManager
            base_dir = os.path.dirname(self.csv_path)
            json_path = os.path.join(base_dir, f"{os.path.basename(self.csv_path).replace('.csv', '')}_meta.json")
            if os.path.exists(json_path):
                self.save_csv() # Auto save before deploy
                success, msg_or_path = TBundleManager.deploy_csv_to_bundle(self.csv_path)
                if success:
                    QMessageBox.information(self, _("deploy_success_title"), f"Deployed successfully back to Unity Bundle:\n{msg_or_path}")
                else:
                    QMessageBox.warning(self, "Deploy Failed", msg_or_path)
                return
        except Exception as e:
            pass

        from tstudio_core import TFormatManager
        success, msg_or_path = TFormatManager.export_original(self.csv_path)
        if success:
            QMessageBox.information(self, _("export_success_title"), f"Exported successfully to:\n{msg_or_path}")
        else:
            QMessageBox.warning(self, "Export Failed", msg_or_path)

    def save_csv(self):
        import tempfile, shutil
        if hasattr(self, '_trans_save_timer') and self._trans_save_timer.isActive():
            self._trans_save_timer.stop()
            self.on_trans_changed()

        if not self.csv_path:
            QMessageBox.warning(self, _("error_title"), _("csv_path_not_configured"))
            return
        tmp_fd, tmp_path = tempfile.mkstemp(
            dir=os.path.dirname(os.path.abspath(self.csv_path)),
            suffix='.tmp'
        )
        try:
            with os.fdopen(tmp_fd, 'w', encoding=self.csv_encoding, newline='') as f:
                writer = csv.writer(f)
                if self.model.headers_row:
                    writer.writerow(self.model.headers_row)
                for item in self.model._data:
                    row = [''] * (max(COL_ID, COL_SOURCE, COL_TRANS, COL_AI_REF) + 1)
                    row[COL_ID] = item["id"]
                    row[COL_SOURCE] = item["source"]
                    row[COL_TRANS] = item["trans"]
                    if COL_AI_REF < len(row): row[COL_AI_REF] = item.get("ai_ref", "")
                    writer.writerow(row)
            shutil.move(tmp_path, self.csv_path)
            self.model.is_dirty = False
            self.statusBar().showMessage('Saved!', 5000)
            QMessageBox.information(self, _("save_success_title"), f"Translations saved successfully to:\n{self.csv_path}")
        except Exception as e:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            QMessageBox.critical(self, _("error_title"), f"Failed to save:\n{e}")

    def silent_save_csv(self):
        import tempfile, shutil
        if hasattr(self, '_trans_save_timer') and self._trans_save_timer.isActive():
            self._trans_save_timer.stop()
            self.on_trans_changed()

        if not self.csv_path or not self.model or not self.model._data:
            return False
            
        tmp_fd, tmp_path = tempfile.mkstemp(
            dir=os.path.dirname(os.path.abspath(self.csv_path)),
            suffix='.tmp'
        )
        try:
            with os.fdopen(tmp_fd, 'w', encoding=self.csv_encoding, newline='') as f:
                writer = csv.writer(f)
                if self.model.headers_row:
                    writer.writerow(self.model.headers_row)
                for item in self.model._data:
                    row = [''] * (max(COL_ID, COL_SOURCE, COL_TRANS, COL_AI_REF) + 1)
                    row[COL_ID] = item["id"]
                    row[COL_SOURCE] = item["source"]
                    row[COL_TRANS] = item["trans"]
                    if COL_AI_REF < len(row): row[COL_AI_REF] = item.get("ai_ref", "")
                    writer.writerow(row)
            shutil.move(tmp_path, self.csv_path)
            self.model.is_dirty = False
            self.statusBar().showMessage(_("status_auto_saved") if _("status_auto_saved") != "status_auto_saved" else "🟢 Auto-Saved", 3000)
            return True
        except Exception as e:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            print(f"Auto-save failed: {e}")
            return False

    def export_origin_format(self):
        if not self.model or not self.model._data:
            QMessageBox.warning(self, _("error_title"), _("export_no_data"))
            return
            
        file_path, filter_str = QFileDialog.getSaveFileName(
            self,
            _("export_origin_title"),
            BASE_DIR,
            "SubRip Subtitle (*.srt);;Web Video Text Tracks (*.vtt);;JSON Files (*.json);;All Files (*.*)"
        )
        
        if not file_path:
            return
            
        ext = os.path.splitext(file_path)[1].lower()
        try:
            if ext == '.json':
                import json
                export_data = {}
                for item in self.model._data:
                    uid = item["id"]
                    text = item["trans"].strip() if item["trans"].strip() else item["source"].strip()
                    export_data[uid] = text
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=4)
            else:
                with open(file_path, 'w', encoding='utf-8-sig') as f:
                    if ext == '.vtt':
                        f.write("WEBVTT\n\n")
                        
                    for item in self.model._data:
                        uid = item["id"]
                        text = item["trans"].strip() if item["trans"].strip() else item["source"].strip()
                        
                        parts = uid.split('|', 1)
                        if len(parts) == 2:
                            idx, timestamp = parts
                        else:
                            idx = ""
                            timestamp = uid
                            
                        if ext == '.srt':
                            if idx:
                                f.write(f"{idx}\n")
                            timestamp = timestamp.replace('.', ',')
                            f.write(f"{timestamp}\n")
                            f.write(f"{text}\n\n")
                        elif ext == '.vtt':
                            timestamp = timestamp.replace(',', '.')
                            if not re.search(r'\d{2}:\d{2}:\d{2}', timestamp):
                                pass
                            f.write(f"{timestamp}\n")
                            f.write(f"{text}\n\n")
                        else:
                            f.write(f"{text}\n")
                        
            QMessageBox.information(self, _("success_title"), f"Exported to {os.path.basename(file_path)} successfully!")
        except Exception as e:
            QMessageBox.critical(self, _("error_title"), f"Failed to export: {str(e)}")

    def deploy_to_game(self):
        if not hasattr(self, 'csv_path') or not self.csv_path:
            QMessageBox.warning(self, _("error_title"), _("no_file_loaded"))
            return

        try:
            from tstudio_core import TStudioCore
            cfg = TStudioCore.load_config()
            origin_file = cfg.get("origin_file", "")
            
            # ── LANG Deploy logic ──
            if origin_file and origin_file.lower().endswith('.lang'):
                meta_path = self.csv_path.replace(".csv", "_meta.json")
                if os.path.exists(meta_path):
                    self.save_csv()
                    reply = QMessageBox.question(self, _("deploy_lang_title"), 
                                                 f"Are you sure you want to overwrite the original LANG file at:\n{origin_file}?",
                                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                    if reply == QMessageBox.StandardButton.Yes:
                        self.statusBar().showMessage("Deploying to LANG file...")
                        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
                        try:
                            reconstruct_lang_file(self.csv_path, meta_path, origin_file)
                            QApplication.restoreOverrideCursor()
                            QMessageBox.information(self, _("deploy_success_title"), f"Successfully deployed to LANG file at:\n{origin_file}")
                        except Exception as e:
                            QApplication.restoreOverrideCursor()
                            QMessageBox.critical(self, _("deploy_error_title"), f"Failed to deploy LANG file:\n{str(e)}")
                    return

            if origin_file and origin_file.lower().endswith('.win') and "utmt" in self.csv_path.lower():
                self.save_csv()
                reply = QMessageBox.question(self, _("deploy_gamemaker_title"), 
                                             f"Are you sure you want to pack translations back into:\n{origin_file}?\n(This may take a few minutes)",
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    self.statusBar().showMessage("Packing translations to data.win...")
                    QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
                    try:
                        import sys
                        sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Core"))
                        from utmt_handler import UTMTHandler
                        out_win = UTMTHandler.repack_strings_from_csv(origin_file, self.csv_path)
                        QApplication.restoreOverrideCursor()
                        QMessageBox.information(self, _("deploy_success_title"), f"Successfully modded GameMaker archive at:\n{out_win}")
                    except Exception as e:
                        QApplication.restoreOverrideCursor()
                        QMessageBox.critical(self, _("deploy_error_title"), f"Failed to repack .win:\n{str(e)}")
                return

            if origin_file and origin_file.lower().endswith('.pak'):
                self.save_csv()
                reply = QMessageBox.question(self, "Deploy PAK File", 
                                             f"Are you sure you want to pack translations back into:\n{origin_file}?",
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    self.statusBar().showMessage("Packing translations to PAK file...")
                    QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
                    try:
                        from tstudio_core import TPakManager
                        TPakManager.reconstruct_pak_file(origin_file, self.csv_path, origin_file)
                        QApplication.restoreOverrideCursor()
                        QMessageBox.information(self, _("deploy_success_title"), f"Successfully deployed to PAK file at:\n{origin_file}")
                    except Exception as e:
                        QApplication.restoreOverrideCursor()
                        QMessageBox.critical(self, _("deploy_error_title"), f"Failed to deploy PAK file:\n{str(e)}")
                return
        except Exception as e:
            # Only restore cursor if we actually set it in the inner try block.
            # The outer except catches errors before setOverrideCursor is called
            # (e.g. user clicked 'No', or config load failed), so we must not
            # call restoreOverrideCursor unconditionally here — that would pop
            # an extra level and leave the cursor in WaitCursor permanently.
            # The inner try/except blocks each call restoreOverrideCursor already;
            # we just log here.
            print(f"Error checking win deploy: {e}")
            
        if self.csv_path.endswith('.landb.csv'):
            # Telltale Deploy logic
            self.save_csv()
            input_dir = os.path.dirname(self.csv_path)
            
            out_ttarch2, _ext = QFileDialog.getSaveFileName(self, "Save Modded Telltale Archive", BASE_DIR, "Telltale Archives (*.ttarch2)")
            if not out_ttarch2:
                return
                
            self.statusBar().showMessage(_("deploy_telltale_msg"))
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            
            try:
                from tstudio_telltale import TelltaleManager
                manager = TelltaleManager()
                # Inject CSV into landb files in input_dir
                manager.convert_csv_to_landb(self.csv_path, input_dir)
                
                # Pack the directory
                success, msg = manager.pack_ttarch2(input_dir, out_ttarch2)
                
                QApplication.restoreOverrideCursor()
                if success:
                    QMessageBox.information(self, _("success_title"), f"Modded archive successfully created at:\n{out_ttarch2}")
                else:
                    QMessageBox.critical(self, _("error_title"), f"Failed to pack archive:\n{msg}")
            except Exception as e:
                QApplication.restoreOverrideCursor()
                QMessageBox.critical(self, _("error_title"), f"An error occurred during deployment:\n{str(e)}")
            return

        # Fallback for generic files: Use Template Replacement via Custom Dialog
        from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QPushButton, QHBoxLayout
        dialog = QDialog(self)
        dialog.setWindowTitle(_("deploy_template_title"))
        dialog.setMinimumWidth(500)
        
        layout = QVBoxLayout(dialog)
        form_layout = QFormLayout()
        
        txt_template = QLineEdit()
        btn_template = QPushButton(_("browse_btn"))
        btn_template.setToolTip(_("tooltip_btn_template"))
        lay_template = QHBoxLayout()
        lay_template.addWidget(txt_template)
        lay_template.addWidget(btn_template)
        form_layout.addRow(_("original_template_file"), lay_template)
        
        txt_save = QLineEdit()
        btn_save = QPushButton(_("browse_btn"))
        btn_save.setToolTip(_("tooltip_btn_save"))
        lay_save = QHBoxLayout()
        lay_save.addWidget(txt_save)
        lay_save.addWidget(btn_save)
        form_layout.addRow(_("save_deployed_file"), lay_save)
        
        layout.addLayout(form_layout)
        
        btn_deploy = QPushButton(_("btn_deploy"))
        btn_deploy.setToolTip(_("tooltip_btn_deploy"))
        btn_deploy.setStyleSheet("background-color: #2e7d32; color: white; font-weight: bold; padding: 8px;")
        layout.addWidget(btn_deploy)
        
        def browse_template():
            path, _ext = QFileDialog.getOpenFileName(dialog, "Select Original Template File", BASE_DIR, "All Files (*.*)")
            if path:
                txt_template.setText(path)
                # Auto-fill save path
                import os
                base, ext = os.path.splitext(path)
                txt_save.setText(f"{base}_translated{ext}")
                
        def browse_save():
            path, _ext = QFileDialog.getSaveFileName(dialog, "Select Save Location", txt_save.text() or BASE_DIR, "All Files (*.*)")
            if path:
                txt_save.setText(path)
                
        btn_template.clicked.connect(browse_template)
        btn_save.clicked.connect(browse_save)
        btn_deploy.clicked.connect(dialog.accept)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            template_path = txt_template.text()
            save_path = txt_save.text()
            
            if not template_path or not save_path:
                QMessageBox.warning(self, _("warning_title"), _("please_specify_both_paths"))
                return
                
            try:
                self.statusBar().showMessage("Deploying using template...")
                QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
                
                # Auto-detect encoding
                import chardet
                with open(template_path, 'rb') as f:
                    raw = f.read()
                    encoding = chardet.detect(raw)['encoding'] or 'utf-8'
                    
                with open(template_path, 'r', encoding=encoding, errors='ignore') as f:
                    template_text = f.read()
                    
                import re
                replace_count = 0
                
                # Sort by length descending to prevent shorter strings from replacing parts of longer strings
                sorted_data = sorted(self.model._data, key=lambda x: len(x.get("source", "")), reverse=True)
                
                for item in sorted_data:
                    src = item.get("source", "").replace('\\n', '\n')
                    trans = item.get("trans", "").replace('\\n', '\n').strip()
                    if not trans:
                        trans = item.get("ai_ref", "").replace('\\n', '\n').strip()
                        
                    if trans and src and src != trans:
                        # Safeguard: Restore missing {Tags} and [Tags] at the beginning
                        tags_match = re.match(r'^((?:\[.*?\]|\{.*?\})\s*)+', src)
                        if tags_match:
                            tags = tags_match.group(0)
                            if not trans.startswith(tags.strip()):
                                # Strip any potentially mangled tags from trans before prepending original
                                trans_clean = re.sub(r'^((?:\[.*?\]|\{.*?\})\s*)+', '', trans)
                                trans = tags + trans_clean

                        if src in template_text:
                            template_text = template_text.replace(src, trans)
                            replace_count += 1
                            
                with open(save_path, 'w', encoding='utf-8-sig') as f:
                    f.write(template_text)
                    
                QApplication.restoreOverrideCursor()
                QMessageBox.information(self, _("deploy_success_title"), f"Successfully deployed {replace_count} translations to:\n{save_path}")
            except Exception as e:
                QApplication.restoreOverrideCursor()
                QMessageBox.critical(self, _("error_title"), f"Failed to deploy with template:\n{str(e)}")

    def closeEvent(self, event):
        if hasattr(self, '_trans_save_timer') and self._trans_save_timer.isActive():
            self._trans_save_timer.stop()
            self.on_trans_changed()

        if hasattr(self, 'model') and getattr(self.model, 'is_dirty', False):
            reply = QMessageBox.question(
                self, _("unsaved_changes_title"),
                _("unsaved_before_exit"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.save_csv()
                self.save_layout_state()
            elif reply == QMessageBox.StandardButton.No:
                self.save_layout_state()
            else:
                event.ignore()
                return

        else:
            self.save_layout_state()

        # FIX: Signal all in-flight batch workers to drop their callbacks, then
        # wait up to 3 s for the thread-pool to drain so no callback fires into
        # a half-destroyed window after this point.
        self._is_closing = True
        self._workers.clear()  # release references; workers still running finish naturally
        if hasattr(self, 'threadpool'):
            self.threadpool.waitForDone(0)  # non-blocking - don't freeze UI

        event.accept()


    def on_toggle_qa_marker(self, checked):
        if checked:
            self.update_html_sources()
        else:
            self.model.layoutChanged.emit()
            
    def recheck_qa_for_row(self, row_idx):
        if not self.model.is_qa_enabled:
            return False
            
        from tstudio_core import TStudioCore
        profile = TStudioCore.get_current_profile_data()
        glossary = profile.get("glossary", {})
        if not glossary: return False
        
        import re
        sorted_glossary = sorted(glossary.items(), key=lambda x: len(x[0]), reverse=True)
        
        item = self.model._data[row_idx]
        source_text = item["source"]
        trans_text = item["trans"]
        
        has_error = False
        if trans_text.strip():
            for eng, val in sorted_glossary:
                eng_str = str(eng).strip()
                if not eng_str: continue
                
                # FIX: Only add \b where the boundary character is a word character, so special-symbol terms (e.g. [Boltgun], {0}) still match
                _prefix = r'\b' if re.match(r'\w', eng_str) else r''
                _suffix = r'\b' if re.search(r'\w$', eng_str) else r''
                pattern = _prefix + r'(' + re.escape(eng_str) + r')' + _suffix
                if re.search(pattern, source_text, re.IGNORECASE):
                    thai = val[0] if isinstance(val, list) else val
                    if not isinstance(thai, str):
                        thai = str(thai) if thai is not None else ""
                    if not thai:
                        continue
                    # FIX: Case-insensitive check to prevent false positives when target term casing differs
                    if thai.lower() not in trans_text.lower():
                        has_error = True
                        break
                        
        if item.get("qa_failed") != has_error:
            item["qa_failed"] = has_error
            return True
        return False
            
    def on_toggle_qa(self, checked):
        if getattr(self, '_qa_running', False):
            self.act_toggle_qa.blockSignals(True)
            self.act_toggle_qa.setChecked(not checked)  # revert
            self.act_toggle_qa.blockSignals(False)
            return
        self._qa_running = True
        try:
            self.model.is_qa_enabled = checked
            if not checked:
                # Clear QA flags
                for item in self.model._data:
                    item["qa_failed"] = False
                self.model.layoutChanged.emit()
                self.proxy.invalidateFilter()
                return

            # Run QA Check in memory
            from tstudio_core import TStudioCore
            profile = TStudioCore.get_current_profile_data()
            glossary = profile.get("glossary", {})
            if not glossary:
                from PyQt6.QtWidgets import QMessageBox
                self.act_toggle_qa.blockSignals(True)
                self.act_toggle_qa.setChecked(False)
                self.act_toggle_qa.blockSignals(False)
                self.model.is_qa_enabled = False
                QMessageBox.information(self, "QA Check", _("qa_no_glossary"))
                return
                
            import re
            failed_count = 0
            
            # Sort glossary by length descending
            sorted_glossary = sorted(glossary.items(), key=lambda x: len(x[0]), reverse=True)
            
            for item in self.model._data:
                item["qa_failed"] = False # Reset first
                
                source_text = item["source"]
                trans_text = item["trans"]
                
                # Skip if translation is empty
                if not trans_text.strip():
                    continue
                    
                has_error = False
                for eng, val in sorted_glossary:
                    eng_str = str(eng).strip()
                    if not eng_str: continue
                    
                    # Check if english term is in source
                    # FIX: Only add \b where the boundary character is a word character, so special-symbol terms (e.g. [Boltgun], {0}) still match
                    _prefix = r'\b' if re.match(r'\w', eng_str) else r''
                    _suffix = r'\b' if re.search(r'\w$', eng_str) else r''
                    pattern = _prefix + r'(' + re.escape(eng_str) + r')' + _suffix
                    if re.search(pattern, source_text, re.IGNORECASE):
                        # It's in source, check if Thai term is in translation
                        thai = val[0] if isinstance(val, list) else val
                        if not isinstance(thai, str):
                            thai = str(thai) if thai is not None else ""
                        if not thai:
                            continue
                        # FIX: Case-insensitive check to prevent false positives when target term casing differs
                        if thai.lower() not in trans_text.lower():
                            has_error = True
                            break # One missing term is enough to fail
                            
                if has_error:
                    item["qa_failed"] = True
                    failed_count += 1
                    
            # Refresh the model
            self.model.layoutChanged.emit()
            self.proxy.invalidateFilter()
            
            from PyQt6.QtWidgets import QMessageBox
            if failed_count > 0:
                QMessageBox.warning(self, "QA Check", _("qa_failed_msg").format(failed=failed_count))
            else:
                QMessageBox.information(self, "QA Check", _("qa_success_msg"))
        finally:
            self._qa_running = False

    def refresh_glossary_dependent_features(self):
        # 1. Reload profiles data in memory to ensure it is in sync with disk
        from tstudio_core import TStudioCore
        self._profiles_data = TStudioCore.load_profiles()
        
        # 2. Update HTML sources for terms highlight
        if hasattr(self, 'act_toggle_qa_marker') and self.act_toggle_qa_marker.isChecked():
            self.update_html_sources()
        else:
            # Clear html sources if marker is not checked
            for item in self.model._data:
                item.pop("html_source", None)
            self.model.layoutChanged.emit()
            
        # 3. Re-run QA check if enabled
        if hasattr(self, 'model') and self.model.is_qa_enabled:
            profile = TStudioCore.get_current_profile_data()
            glossary = profile.get("glossary", {})
            
            import re
            sorted_glossary = sorted(glossary.items(), key=lambda x: len(x[0]), reverse=True) if glossary else []
            
            for item in self.model._data:
                item["qa_failed"] = False # Reset
                if not glossary:
                    continue
                source_text = item["source"]
                trans_text = item["trans"]
                if not trans_text.strip():
                    continue
                
                has_error = False
                for eng, val in sorted_glossary:
                    eng_str = str(eng).strip()
                    if not eng_str: continue
                    # FIX: Only add \b where the boundary character is a word character, so special-symbol terms (e.g. [Boltgun], {0}) still match
                    _prefix = r'\b' if re.match(r'\w', eng_str) else r''
                    _suffix = r'\b' if re.search(r'\w$', eng_str) else r''
                    pattern = _prefix + r'(' + re.escape(eng_str) + r')' + _suffix
                    if re.search(pattern, source_text, re.IGNORECASE):
                        thai = val[0] if isinstance(val, list) else val
                        if not isinstance(thai, str):
                            thai = str(thai) if thai is not None else ""
                        if not thai:
                            continue
                        # FIX: Case-insensitive check to prevent false positives when target term casing differs
                        if thai.lower() not in trans_text.lower():
                            has_error = True
                            break
                if has_error:
                    item["qa_failed"] = True
            
            self.model.layoutChanged.emit()
            self.proxy.invalidateFilter()
            
        # 4. Refresh the current selected row glossary markers in txt_source
        if hasattr(self, 'current_source_row') and self.current_source_row >= 0:
            current_index = self.table.currentIndex()
            if current_index.isValid():
                self.on_row_selected(current_index, current_index)


if __name__ == '__main__':
    import argparse
    import traceback
    import sys
    from PyQt6.QtWidgets import QMessageBox

    def global_exception_handler(exc_type, exc_value, exc_traceback):
        error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        with open("crash.log", "w", encoding="utf-8") as f:
            f.write(error_msg)
        try:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Critical Error")
            msg.setText(_("msg_fatal_crash"))
            msg.setInformativeText(str(exc_value))
            msg.setDetailedText(error_msg)
            msg.exec()
        except:
            pass
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

    sys.excepthook = global_exception_handler

    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=str, help="Path to the active THub project", default=None)
    args, unknown = parser.parse_known_args()
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    win = TranslationStudio(project_path=args.project)
    win.show()
    sys.exit(app.exec())

