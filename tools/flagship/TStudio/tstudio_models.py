"""
TStudio Modular Models & Proxy:
- CsvTableModel: High-performance QAbstractTableModel for large CSV datasets
- FilterProxy: QSortFilterProxyModel supporting Quick Chips, Regex, and Multilingual filters
- TransEditorEventFilter: Keyboard event handler for Shift+Enter vs Enter
- SelectionTranslatePill: Floating 1-click selection action pill
"""
import os
import sys
_core_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Core'))
if _core_dir not in sys.path:
    sys.path.append(_core_dir)
import re
import csv
import html
import time

from PyQt6.QtCore import (
    QAbstractTableModel, QSortFilterProxyModel, QObject, Qt, QModelIndex,
    QRect, pyqtSignal, QItemSelection
)
from PyQt6.QtWidgets import (
    QFrame, QPushButton, QHBoxLayout, QGraphicsDropShadowEffect, QApplication,
    QMessageBox
)
from PyQt6.QtGui import QColor

from tstudio_i18n import _
from tstudio_core import TStudioCore

# Column index constants
COL_AI_REF = 3

def get_row_tag(id_str, source_str):
    return TStudioCore.get_row_tag(id_str, source_str)

class CsvTableModel(QAbstractTableModel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = parent
        self._data = []
        self.headers_row = []
        self.is_dirty = False
        self.is_qa_enabled = False
        self.headers = ["✔", _("col_id"), _("col_source"), _("col_ai_translation"), _("col_translation")]

    def set_ai_column_name(self, name):
        self.headers[3] = name
        self.headerDataChanged.emit(Qt.Orientation.Horizontal, 3, 3)

    def clear(self):
        self.beginResetModel()
        self._data = []
        self.headers_row = []
        self.is_dirty = False
        self.csv_read_error = None
        self.endResetModel()

    def load_csv(self, filepath, encoding, col_id, col_src, col_trans, col_ai):
        self.beginResetModel()
        self.headers[3] = _("col_ai_translation")
        self._data = []
        if not filepath or not os.path.exists(filepath):
            self.endResetModel()
            return 0
        self.col_id = col_id
        self.col_src = col_src
        self.col_trans = col_trans
        self.col_ai = col_ai
        self.csv_read_error = None
        try:
            with open(filepath, 'r', encoding=encoding, errors='strict', newline='') as check:
                check.read()
        except UnicodeError as error:
            # Display a damaged decode for review, but prohibit all CSV writes.
            self.csv_read_error = str(error)
        max_col = max(col_id, col_src, col_trans, col_ai) + 1
        with open(filepath, 'r', encoding=encoding, errors='replace', newline='') as f:
            reader = csv.reader(f, strict=True)
            try:
                self.headers_row = next(reader)
            except StopIteration:
                self.headers_row = []
            ai_names = ('ai reference', 'ai ref', 'ai_ref', 'ai_reference')
            self.col_ai = next((index for index, name in enumerate(self.headers_row)
                                if name.strip().lower() in ai_names), -1)
            col_ai = self.col_ai
            max_col = max(col_id, col_src, col_trans, col_ai) + 1
            try:
                for i, row in enumerate(reader):
                    if len(row) != len(self.headers_row):
                        self.csv_read_error = f'Row {i + 2}: column count differs from header'
                    while len(row) < max_col: row.append('')
                    raw_row = list(row)
                    ai_val = row[col_ai] if 0 <= col_ai < len(row) else ''
                    
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
                        "ai_ref": ai_val,
                        "tag": tag_val,
                        "qa_failed": False,
                        "is_idiom": has_idiom,
                        "is_th": is_th_val,
                        "raw_row": raw_row
                    })
            except Exception as e:
                self.csv_read_error = str(e)
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
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self.headers[section]
            elif orientation == Qt.Orientation.Vertical:
                return str(section + 1)
        if role == Qt.ItemDataRole.TextAlignmentRole and orientation == Qt.Orientation.Vertical:
            return Qt.AlignmentFlag.AlignCenter
        return None

    def delete_rows(self, row_indices):
        """Safely remove rows specified by indices in descending order."""
        if not row_indices:
            return 0
        sorted_indices = sorted(set(row_indices), reverse=True)
        self.beginResetModel()
        for idx in sorted_indices:
            if 0 <= idx < len(self._data):
                del self._data[idx]
        self.is_dirty = True
        self.endResetModel()
        return len(sorted_indices)

    def refresh_tags(self):
        """Re-calculate row tags for all rows using updated TStudioCore logic."""
        if not self._data:
            return 0
        self.beginResetModel()
        updated = 0
        for item in self._data:
            new_tag = get_row_tag(item.get("id", ""), item.get("source", ""))
            if item.get("tag") != new_tag:
                item["tag"] = new_tag
                updated += 1
        self.endResetModel()
        return updated

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        try:
            if not index.isValid(): return None
            r, c = index.row(), index.column()
            if r < 0 or r >= len(self._data): return None
            item = self._data[r]
            if not isinstance(item, dict): return None

            if role == Qt.ItemDataRole.UserRole and c == 0:
                if TStudioCore.has_cjk(item.get("trans", "")):
                    return "cjk"
                elif item.get("trans", "").strip():
                    return "translated"
                else:
                    return "pending"

            if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
                val = ""
                if c == 0: val = item.get("tag", "❓")
                elif c == 1: val = item.get("id", "")
                elif c == 2:
                    raw_src = item.get("source", "")
                    if role == Qt.ItemDataRole.DisplayRole and (hasattr(self, 'app')
                        and hasattr(self.app, 'act_toggle_qa_marker')
                        and self.app.act_toggle_qa_marker.isChecked()):
                        try:
                            cur_ver = getattr(self.app, '_html_cache_version', 0)
                            if item.get('_html_ver') != cur_ver:
                                pat = getattr(self.app, '_cached_glossary_pat', None)
                                if pat:
                                    source_text = str(raw_src) if raw_src is not None else ""
                                    if source_text:
                                        if len(source_text) > 1500:
                                            source_text = source_text[:1500] + "..."
                                        esc = html.escape(source_text)
                                        if pat.search(esc):
                                            item['html_source'] = pat.sub(r'<span style="background-color:#f9e2af; color:#11111b; font-weight:bold; padding:0 2px; border-radius:2px;">\1</span>', esc)
                                        else:
                                            item['html_source'] = None
                                    else:
                                        item['html_source'] = None
                                else:
                                    item['html_source'] = None
                                item['_html_ver'] = cur_ver
                            val = item.get('html_source') or raw_src
                        except Exception:
                            val = raw_src
                    else:
                        val = raw_src
                elif c == 3: val = str(item.get("ai_ref") or "")
                elif c == 4: val = item.get("trans", "")

                if role == Qt.ItemDataRole.DisplayRole and isinstance(val, str):
                    if len(val) > 2000 and "<span" not in val:
                        val = val[:2000] + "\n... <TRUNCATED - TEXT TOO LARGE FOR UI>"
                    if '\x00' in val:
                        val = val.replace('\x00', '[NUL]')
                return val

            if role == Qt.ItemDataRole.ForegroundRole:
                if c == 0: return QColor('#cba6f7')
                if c == 1: return QColor('#89b4fa')
                if c == 3: return QColor('#f9e2af')
                if c == 4:
                    tr = item.get("trans", "")
                    if tr:
                        if TStudioCore.has_cjk(tr):
                            return QColor('#fab387') # Peach warning color for CJK leak
                        return QColor('#a6e3a1') if tr != str(item.get("ai_ref") or "") else QColor('#f9e2af')
                    return QColor('#f38ba8')

            if role == Qt.ItemDataRole.BackgroundRole:
                if self.is_qa_enabled and item.get("qa_failed"):
                    return QColor('#451a1a') # Dark red background for QA errors
                if TStudioCore.has_cjk(item.get("trans", "")):
                    return QColor('#3d2218') # Subtle warning tint for CJK leak

            if role == Qt.ItemDataRole.ToolTipRole:
                if c == 0:
                    return f"หมวดหมู่ (Tag): {item.get('tag', '❓')}"
                if c in (3, 4):
                    val = str(item.get("trans" if c == 4 else "ai_ref") or "")
                    if val and TStudioCore.has_cjk(val):
                        chars = "".join(TStudioCore.extract_cjk(val)[:10])
                        return f"🇨🇳 ตรวจพบตัวอักษรจีน/CJK หลุดมา: {chars}"
            return None
        except Exception:
            return None

    def update_trans(self, row, text):
        if 0 <= row < len(self._data):
            old = self._data[row]["trans"]
            self._data[row]["trans"] = text
            self._data[row]["is_th"] = bool(re.search(r'[ก-๙เแไใโ]', text)) if text else False
            self.is_dirty = True
            
            qa_changed = False
            if hasattr(self, 'app') and hasattr(self.app, 'recheck_qa_for_row'):
                qa_changed = self.app.recheck_qa_for_row(row)
                
            # Emit all roles so Column 0 UserRole badge (CJK -> checkmark) and CJK colors refresh immediately
            idx_start = self.index(row, 0)
            idx_end = self.index(row, 4)
            roles = [
                Qt.ItemDataRole.DisplayRole,
                Qt.ItemDataRole.EditRole,
                Qt.ItemDataRole.ForegroundRole,
                Qt.ItemDataRole.BackgroundRole,
                Qt.ItemDataRole.UserRole,
                Qt.ItemDataRole.ToolTipRole
            ]
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
        self._raw_search = ''
        self._search = ''
        self._mode = 0
        self.match_case = False
        self.match_whole_word = False
        self.match_exact = False
        self.match_regex = False
        self._compiled_regex = None

    def set_search(self, text, match_case=False, match_whole_word=False, match_exact=False, match_regex=False):
        self._raw_search = (text or '').strip()
        self.match_case = bool(match_case)
        self.match_whole_word = bool(match_whole_word)
        self.match_exact = bool(match_exact)
        self.match_regex = bool(match_regex)
        self._compiled_regex = None

        query = self._raw_search

        # Smart prefix syntax auto-detection if no specific toggle is on
        if query.startswith('=') and len(query) > 1 and not (self.match_regex or self.match_whole_word):
            self.match_exact = True
            query = query[1:].strip()
        elif query.startswith('"') and query.endswith('"') and len(query) >= 2 and not self.match_regex:
            self.match_whole_word = True
            query = query[1:-1]
        elif query.startswith('/') and len(query) > 2 and ('/' in query[1:]):
            parts = query.rsplit('/', 1)
            pat = parts[0][1:]
            flags_str = parts[1]
            flags = 0
            if 'i' in flags_str or not self.match_case:
                flags |= re.IGNORECASE
            try:
                self._compiled_regex = re.compile(pat, flags)
                self.match_regex = True
                query = pat
            except Exception:
                pass

        self._search = query if self.match_case else query.lower()

        if self.match_whole_word and query and self._compiled_regex is None:
            try:
                self._compiled_regex = build_search_boundary_regex(query, self.match_case)
            except Exception:
                self._compiled_regex = None
        elif self.match_regex and query and self._compiled_regex is None:
            try:
                flags = 0 if self.match_case else re.IGNORECASE
                self._compiled_regex = re.compile(query, flags)
            except Exception:
                self._compiled_regex = None

        self.invalidateFilter()

    def set_filter_mode(self, mode):
        self._mode = mode
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        try:
            src_model = self.sourceModel()
            if src_model is None or not hasattr(src_model, '_data'):
                return False
            if source_row < 0 or source_row >= len(src_model._data):
                return False
            item = src_model._data[source_row]
            if not isinstance(item, dict):
                return False

            trans_str = str(item.get("trans") or "")
            source_str = str(item.get("source") or "")
            ai_str = str(item.get("ai_ref") or "")
            tag = str(item.get("tag") or "❓")

            if self._mode == 1 and trans_str.strip(): return False
            if self._mode == 2 and not trans_str.strip(): return False
            if self._mode == 3:
                src_len = len(source_str)
                trans_len = len(trans_str)
                if trans_len < 200: return False
                if src_len > 0 and (trans_len / src_len) > 4:
                    pass
                else:
                    return False
            if self._mode == 4:
                if item.get("is_idiom", False):
                    pass
                elif ai_str and trans_str != ai_str:
                    pass
                elif source_str and not trans_str:
                    pass
                else:
                    return False

            # Smart Filter Modes
            if self._mode == 5 and "Char" not in tag: return False
            if self._mode == 6 and "Loc" not in tag: return False
            if self._mode == 7 and "Skill" not in tag: return False
            if self._mode == 8 and "Item" not in tag: return False
            if self._mode == 9 and not ("Item" in tag or "Skill" in tag): return False
            if self._mode == 10 and "Quest" not in tag: return False
            if self._mode == 11 and "Sys" not in tag: return False
            if self._mode == 12 and "Talk" not in tag: return False

            if self._mode == 13:
                clean_text = re.sub(r'\{.*?\}|\[.*?\]|<.*?>', '', trans_str)
                has_thai = bool(re.search(r'[\u0E00-\u0E7F]', clean_text))
                has_eng = bool(re.search(r'[a-zA-Z]', clean_text))
                if not (has_thai and has_eng): return False

            if self._mode == 14:
                clean_trans = re.sub(r'\{.*?\}|\[.*?\]|<.*?>', '', trans_str)
                clean_ai = re.sub(r'\{.*?\}|\[.*?\]|<.*?>', '', ai_str)
                has_eng_trans = bool(re.search(r'[a-zA-Z]', clean_trans))
                has_eng_ai = bool(re.search(r'[a-zA-Z]', clean_ai))
                has_thai_trans = bool(re.search(r'[\u0E00-\u0E7F]', clean_trans))
                has_thai_ai = bool(re.search(r'[\u0E00-\u0E7F]', clean_ai))
                if not (has_eng_trans and has_eng_ai): return False
                if has_thai_trans or has_thai_ai: return False

            if self._mode == 15:
                if trans_str.strip():
                    if not TStudioCore.has_cjk(trans_str):
                        return False
                else:
                    if not TStudioCore.has_cjk(ai_str):
                        return False

            if self._raw_search:
                # Special smart keywords only in default substring mode
                if not (self.match_exact or self.match_regex or self.match_whole_word):
                    if self._search == "qa failed" and item.get("qa_failed"):
                        return True
                    if self._search in ("cjk", "chinese", "ภาษาจีน", "จีน"):
                        if trans_str.strip():
                            return TStudioCore.has_cjk(trans_str)
                        return TStudioCore.has_cjk(ai_str)
                    if self._search in ("สกิล", "skill", "skills", "ความสามารถ", "ability", "abilities"):
                        return "Skill" in tag
                    if self._search in ("ตัวละคร", "char", "character", "characters", "ชื่อตัวละคร"):
                        return "Char" in tag
                    if self._search in ("ไอเทม", "item", "items", "อุปกรณ์", "equipment"):
                        return "Item" in tag
                    if self._search in ("บทสนทนา", "dialogue", "dialogues", "talk", "บทพูด"):
                        return "Talk" in tag
                    if self._search in ("เควสต์", "เควส", "quest", "quests", "ภารกิจ", "mission"):
                        return "Quest" in tag
                    if self._search in ("สถานที่", "location", "locations", "loc"):
                        return "Loc" in tag
                    if self._search in ("ระบบ", "system", "ui", "เมนู", "menu"):
                        return "Sys" in tag

                def _check_field(val_raw):
                    if val_raw is None:
                        return False
                    v_raw = str(val_raw)
                    v_str = v_raw.strip()
                    if not v_str:
                        return False

                    # 1. Exact Match Mode (e.g. 'e' matches only exact 'e', handles NFC & lone marks)
                    if self.match_exact:
                        v_norm = unicodedata.normalize('NFC', v_str).strip(' \t\r\n\u200b\u00a0\ufeff')
                        s_norm = unicodedata.normalize('NFC', self._search).strip(' \t\r\n\u200b\u00a0\ufeff')
                        if self.match_case:
                            return v_norm == s_norm
                        return v_norm.lower() == s_norm.lower()

                    # 2. Whole Word / Regex Mode (includes Thai isolated mark boundary)
                    if self._compiled_regex is not None:
                        return bool(self._compiled_regex.search(v_raw))

                    # 3. Default Substring Mode
                    if self.match_case:
                        return self._search in v_raw
                    return self._search in v_raw.lower()

                # For Exact Match: match if source, trans, or id matches exactly
                if self.match_exact:
                    return _check_field(source_str) or _check_field(trans_str) or _check_field(item.get("id", ""))

                # For other modes: check source, trans, id, tag
                return any(_check_field(item.get(k, '')) for k in ["source", "trans", "id", "tag"])
            return True
        except Exception:
            return False

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
def reconstruct_mesg_json_file(csv_path, origin_file):
    import json, csv
    
    # Load translation map
    trans_map = {}
    with open(csv_path, 'r', encoding='utf-8-sig', errors='replace') as f:
        reader = csv.reader(f)
        header = next(reader, None)
        for row in reader:
            if len(row) >= 3:
                uid, source, trans = row[0], row[1], row[2]
                if trans.strip():
                    trans_map[uid] = trans.strip()
                    
    with open(origin_file, 'r', encoding='utf-8') as f:
        odata = json.load(f)
        
    m_script = odata.get("m_Script", "")
    parts = m_script.split('\u0000')
    
    for uid, trans in trans_map.items():
        if uid.startswith("mesg_"):
            try:
                idx = int(uid.split('_')[1])
                orig = parts[idx]
                
                # Match UTF-8 byte length
                orig_bytes = orig.encode('utf-8')
                trans_bytes = trans.encode('utf-8')
                
                if len(trans_bytes) < len(orig_bytes):
                    trans_bytes = trans_bytes.ljust(len(orig_bytes), b' ')
                elif len(trans_bytes) > len(orig_bytes):
                    trans_bytes = trans_bytes[:len(orig_bytes)]
                    trans = trans_bytes.decode('utf-8', errors='ignore')
                    trans_bytes = trans.encode('utf-8').ljust(len(orig_bytes), b' ')
                    
                parts[idx] = trans_bytes.decode('utf-8')
            except Exception:
                pass
            
    odata["m_Script"] = '\u0000'.join(parts)
    
    with open(origin_file, 'w', encoding='utf-8') as f:
        json.dump(odata, f, ensure_ascii=False, indent=2)

# =========================================================
# Main Window
# =========================================================
class TransEditorEventFilter(QObject):
    def __init__(self, parent_window):
        super().__init__(parent_window)
        self.parent_window = parent_window

    def eventFilter(self, obj, event):
        if event.type() == event.Type.KeyPress:
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                    return super().eventFilter(obj, event)
                else:
                    self.parent_window.confirm_and_next_row()
                    return True
        return super().eventFilter(obj, event)

class SelectionTranslatePill(QFrame):
    """Floating quick-action pill appearing near text selections for 1-click snippet translation."""
    def __init__(self, parent_window):
        super().__init__(parent_window)
        self.parent_window = parent_window
        self.active_editor = None
        self.setObjectName("SelectionTranslatePill")
        self.setStyleSheet("""
            #SelectionTranslatePill {
                background: #181825;
                border: 1px solid #89b4fa;
                border-radius: 13px;
            }
            QPushButton {
                background: transparent;
                color: #cdd6f4;
                border: none;
                font-size: 11px;
                font-weight: bold;
                padding: 2px 7px;
            }
            QPushButton:hover {
                background: #313244;
                color: #89b4fa;
                border-radius: 9px;
            }
            QPushButton#btnTransPill {
                color: #89b4fa;
            }
            QPushButton#btnTransPill:hover {
                background: #89b4fa;
                color: #11111b;
            }
            QPushButton#btnTranslitPill {
                color: #a6e3a1;
            }
            QPushButton#btnTranslitPill:hover {
                background: #a6e3a1;
                color: #11111b;
            }
            QPushButton#btnStylesPill {
                color: #fab387;
            }
            QPushButton#btnStylesPill:hover {
                background: #fab387;
                color: #11111b;
            }
            QPushButton#btnClosePill {
                color: #6c7086;
                padding: 2px 5px;
            }
            QPushButton#btnClosePill:hover {
                color: #f38ba8;
            }
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(2)

        self.btn_trans = QPushButton("✨ แปลคำนี้")
        self.btn_trans.setObjectName("btnTransPill")
        self.btn_trans.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_trans.setToolTip("แปลเฉพาะคำที่เลือก (Ctrl+Shift+T)")
        self.btn_trans.clicked.connect(self._on_translate_clicked)
        layout.addWidget(self.btn_trans)

        self.btn_translit = QPushButton("🗣️ ทับศัพท์")
        self.btn_translit.setObjectName("btnTranslitPill")
        self.btn_translit.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_translit.setToolTip("แปลทับศัพท์เฉพาะคำที่เลือก (Ctrl+Shift+Y)")
        self.btn_translit.clicked.connect(self._on_translit_clicked)
        layout.addWidget(self.btn_translit)

        self.btn_styles = QPushButton("💡 3 สไตล์")
        self.btn_styles.setObjectName("btnStylesPill")
        self.btn_styles.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_styles.setToolTip("เลือกแปล 3 รูปแบบสำหรับคำนี้")
        self.btn_styles.clicked.connect(self._on_styles_clicked)
        layout.addWidget(self.btn_styles)

        self.btn_close = QPushButton("✕")
        self.btn_close.setObjectName("btnClosePill")
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.clicked.connect(self.hide)
        layout.addWidget(self.btn_close)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(12)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)
        self.adjustSize()
        self.hide()

    def _on_translate_clicked(self):
        self.parent_window.translate_selected_snippet(source_widget=self.active_editor, style_choice=False)

    def _on_translit_clicked(self):
        self.parent_window.translate_selected_snippet(source_widget=self.active_editor, mode="transliterate")

    def _on_styles_clicked(self):
        self.parent_window.translate_selected_snippet(source_widget=self.active_editor, style_choice=True)

