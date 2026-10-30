from trun_i18n import _
# -*- coding: utf-8 -*-
import sys
import os
import re as _re_module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Core')))

import csv
import json
import time
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QSplitter, QGroupBox, QComboBox, 
    QMessageBox, QTextEdit, QFileDialog, QSpinBox, QCheckBox, QProgressBar, QSlider,
    QTabWidget, QTableWidget, QTableWidgetItem, QTimeEdit, QListWidget, QAbstractItemView
)
from PyQt6.QtCore import Qt, QRunnable, QThreadPool, pyqtSignal, pyqtSlot, QObject, QLocale, QTime, QTimer
from PyQt6.QtGui import QIcon

from tpua_engine import TPUAEngine
from tstudio_core import TStudioCore, CoreAI
from translation_transport import TranslationGateway, snapshot_config, is_web, WebTransportError
from translation_transport.qt_controls import TranslationChannelWidget


class TRunWorkerSignals(QObject):
    progress = pyqtSignal(int, int)       # current, total
    batch_progress = pyqtSignal(int, int) # current_batch, total_batches
    log = pyqtSignal(str, str)            # text, color
    finished = pyqtSignal()               # completed normally
    stopped = pyqtSignal()                # user-requested stop
    error = pyqtSignal(str)               # fatal error
    row_translated = pyqtSignal(int, str, str) # row_idx, game_id, translated text

class TRunWorker(QRunnable):
    def __init__(self, config, profile, input_csv, output_csv, batch_size=20, delay_ms=0, max_retries=3, use_mask=False, use_glossary=False, use_pua=False, peak_config=None, threads=1, token_burner=False, use_cjk_filter=True, use_eng_filter=False, auto_filter_engine=True, use_dedup=True, selected_row_indices=None, route_config=None):
        super().__init__()
        self.signals = TRunWorkerSignals()
        self.config = snapshot_config(config, route_config)
        from copy import deepcopy
        self.profile = deepcopy(profile)
        self._transport_error = None
        self.input_csv = input_csv
        self.output_csv = output_csv
        self.batch_size = batch_size
        self.delay_ms = delay_ms
        self.max_retries = max_retries
        self.use_mask = use_mask
        self.use_glossary = use_glossary
        self.use_pua = use_pua
        self.peak_config = peak_config
        self.threads = 1 if is_web(self.config) else threads
        self.token_burner = token_burner
        self.use_cjk_filter = use_cjk_filter
        self.use_eng_filter = use_eng_filter
        self.auto_filter_engine = auto_filter_engine
        self.use_dedup = use_dedup
        self.selected_row_indices = set(selected_row_indices) if selected_row_indices is not None else None
        self._is_killed = False
        self._web_disk_signature = self._disk_signature() if is_web(self.config) else None
        self._last_save_time = 0.0
        self.processed_count = 0
        self.total_untrans = 0
        self.result_summary = None
        import threading
        self.save_lock = threading.Lock()

        # Check for companion glossary alongside input_csv for portability ("แปลคอมอื่น")
        if self.input_csv and os.path.exists(self.input_csv):
            try:
                import json
                csv_dir = os.path.dirname(os.path.abspath(self.input_csv))
                base_no_ext = os.path.splitext(os.path.basename(self.input_csv))[0]
                companion_candidates = [
                    os.path.join(csv_dir, f"{base_no_ext}.glossary.json"),
                    os.path.join(csv_dir, "glossary.json")
                ]
                for comp_path in companion_candidates:
                    if os.path.exists(comp_path):
                        with open(comp_path, 'r', encoding='utf-8') as gf:
                            comp_data = json.load(gf)
                        if isinstance(comp_data, dict) and comp_data:
                            self.profile.setdefault("glossary", {})
                            for k, v in comp_data.items():
                                self.profile["glossary"][k] = v
                        break
            except Exception as e:
                print(f"[Warning] Failed to load companion glossary in TRunWorker: {e}")

    def _disk_signature(self):
        import hashlib
        if not os.path.exists(self.output_csv):
            return None
        with open(self.output_csv, 'rb') as handle:
            return hashlib.file_digest(handle, 'sha256').hexdigest() if hasattr(hashlib, 'file_digest') else hashlib.sha256(handle.read()).hexdigest()

    def _generate_translation(self, prompt, is_local):
        try:
            return TranslationGateway.generate_content(self.config, prompt, is_local=is_local,
                                                        cancelled=lambda: self._is_killed)
        except WebTransportError as error:
            self._transport_error = str(error)
            self._is_killed = True
            raise

    @staticmethod
    def is_non_translatable_engine_string(src):
        """Identify engine script internal lines, variables, and control codes that must NOT be sent to LLM."""
        if not src or not isinstance(src, str):
            return True
        raw = src.strip()
        if not raw:
            return True

        # 1. WOLF RPG & RPG Maker internal developer comments or event marks
        # (Only skip if it's purely symbols/event markers or Japanese event headers, not prose/bullet lists like '■ MISSION')
        if raw.startswith(('■', '★', '◆', '▲', '▼')):
            stripped_after = raw.lstrip('■★◆▲▼ \t\r\n')
            if not stripped_after or _re_module.match(r'^[0-9_.\-:=#]+$', stripped_after):
                return True
            if stripped_after.startswith(('文章', '条件', '変数', 'イベント', 'コモン', 'スイッチ', 'ピクチャ', 'SE', 'BGM')):
                return True

        # 2. Pure single ASCII letter or trivial punctuation/code fragments
        if len(raw) == 1 and raw.isascii():
            return True

        # 3. Known engine keywords / variable identifiers that are NOT sentences
        lower_raw = raw.lower()
        ENGINE_EXACT = {
            'unit', 'party', 'array', 'split', 'conv', 'alist', 'alistdb', 
            'systemfile', 'tmpdb', 'flag', 'calc', 'key', 'none', 'null', 'temp', 'dummy',
            'pic', 'sound', 'se', 'bgm', 'me', 'str', 'num', 'var', 'timer',
            'sys', 'db', 'udb', 'cdb', 'sdb', 'x', 'y', 'z', 'w', 'h', 'c', 'l', 'r'
        }
        if lower_raw in ENGINE_EXACT:
            return True

        # 4. Japanese internal event headers / system tags
        if raw.startswith(('Ev開始', '場所移動', '文章表示', 'システム設定', 'コモン処理')):
            return True

        # 5. Pure control tags or variables without prose
        # Strip all known tag patterns (WOLF RPG, RPG Maker, Unity, Ren'Py, HTML/XML)
        stripped = _re_module.sub(r'\\[a-zA-Z0-9]+(?:\[[^\]]*\])?', '', raw)
        stripped = _re_module.sub(r'<[^>]+>', '', stripped)
        stripped = _re_module.sub(r'\[[a-zA-Z0-9_.]+\]', '', stripped)
        stripped = _re_module.sub(r'\{[^}\r\n]+\}', '', stripped)
        stripped = _re_module.sub(r'%[0-9.]*[a-zA-Z0-9]', '', stripped)
        stripped = _re_module.sub(r'[\r\n\t ]+', '', stripped)

        if not stripped:
            return True
        if _re_module.match(r'^[0-9\.,:;/%+\-*$#@_()\[\]{}<>=!\'\"\\|&^~`?←→↑↓・…]+$', stripped):
            return True

        return False

    # Pre-compiled regex patterns at class level to avoid re-compiling on every call
    _RE_THAI = _re_module.compile(r'[\u0E00-\u0E7F]')
    _RE_TAG = _re_module.compile(r'(<[^>]+>|\\n|\\r|\n|\r|\$\$[^\$]+\$\$|#[A-Za-z0-9_]+|~[A-Za-z0-9_]+|\{[^}\r\n]+\}|\[\[[^\]]+\]\]|\[(?!TAG_\d+\])[a-zA-Z0-9_.]+\]|%(?:[0-9.]*[a-zA-Z]+|[0-9]+)|@)')
    _RE_BROKEN_TAG = _re_module.compile(r'\[TAG_\d+\]', _re_module.IGNORECASE)
    _RE_FOREIGN_SCRIPTS = _re_module.compile(r'[\u0400-\u04FF\u0600-\u06FF\u0900-\u097F\uAC00-\uD7AF\u1100-\u11FF\u3040-\u30ff]')
    _RE_TSV_LINE = _re_module.compile(r'^"?([^"\t]+)"?\t(.*)')
    _RE_CODE_FENCE_START = _re_module.compile(r'^```[^\n]*\n?', _re_module.MULTILINE)
    _RE_CODE_FENCE_END = _re_module.compile(r'\n?```$', _re_module.MULTILINE)

    _APPROVED_EXEMPT = {
        'directx', 'opengl', 'vulkan', 'dlss', 'fsr', 'fps', 'nvidia', 'amd', 'intel',
        'cpu', 'gpu', 'ram', 'vram', 'hdr', 'sdr', 'vsync', 'wasd', 'spacebar', 'space',
        'shift', 'ctrl', 'alt', 'tab', 'esc', 'enter', 'backspace', 'delete', 'ok',
        'cancel', 'yes', 'no', 'on', 'off', 'true', 'false', 'n/a', 'hud', 'ui',
        'm16', 'ak-47', 'rpg-7', 'smg', 'lmg', 'dmr', 'humvee', 'apc', '9mm', '5.56mm'
    }

    def is_translated(self, text):
        if not text or not isinstance(text, str): return False
        cleaned = text.strip()
        if not cleaned: return False
        if self._RE_BROKEN_TAG.search(cleaned): return False
        if self._RE_FOREIGN_SCRIPTS.search(cleaned): return False
        if getattr(self, 'use_cjk_filter', True) and TStudioCore.has_cjk(cleaned):
            return False
        if self._RE_THAI.search(cleaned): return True
        if cleaned.lower() in self._APPROVED_EXEMPT: return True
        if _re_module.match(r'^[0-9\.,:;/%+\-*$#@_()\[\]{}<>=!\'\s]+$', cleaned): return True
        return False

    def mask_tags(self, text):
        if not text:
            return "", {}
        placeholders = {}
        parts = []
        last_end = 0
        for idx, m in enumerate(self._RE_TAG.finditer(text)):
            ph = f"[TAG_{idx}]"
            placeholders[ph] = m.group(0)
            parts.append(text[last_end:m.start()])
            parts.append(ph)
            last_end = m.end()
        parts.append(text[last_end:])
        return "".join(parts), placeholders

    def unmask_tags(self, translated_text, placeholders):
        if not translated_text or not placeholders:
            return translated_text
        tag_lookup = {}
        for k, v in placeholders.items():
            tag_lookup[k.upper()] = v
            m = _re_module.search(r'\[TAG_(\d+)\]', k, _re_module.IGNORECASE)
            if m:
                tag_lookup[m.group(1)] = v

        def _replace_placeholder(match):
            full = match.group(0)
            idx = match.group(1)
            if full.upper() in tag_lookup:
                return tag_lookup[full.upper()]
            if idx in tag_lookup:
                return tag_lookup[idx]
            return full

        unmasked = _re_module.sub(r'\[TAG_(\d+)\]', _replace_placeholder, translated_text, flags=_re_module.IGNORECASE)
        for placeholder, original_tag in placeholders.items():
            if placeholder in unmasked:
                unmasked = unmasked.replace(placeholder, original_tag)
        return unmasked

    def extract_english_leaks(self, text):
        from tstudio_core import TStudioCore
        glossary_targets = []
        if self.profile and isinstance(self.profile.get("glossary"), dict):
            for v in self.profile["glossary"].values():
                val = v[0] if isinstance(v, list) and v else v
                if isinstance(val, str) and val.strip():
                    glossary_targets.append(val.strip())
        return TStudioCore.extract_english_leaks(text, allowed_words=glossary_targets)

    def enforce_glossary(self, text):
        if not text:
            return ""
        glossary = self.profile.get("glossary", {})
        if not isinstance(glossary, dict) or not glossary:
            return text
        tag_pat = _re_module.compile(r'(<[^>]+>|\[TAG_\d+\])', _re_module.IGNORECASE)
        parts = tag_pat.split(text)
        sorted_terms = sorted(glossary.items(), key=lambda x: len(str(x[0])), reverse=True)
        for index in range(0, len(parts), 2):
            for wrong_word, correct_val in sorted_terms:
                wrong = str(wrong_word).strip()
                correct = correct_val[0] if isinstance(correct_val, list) and correct_val else correct_val
                right = str(correct or '').strip()
                if wrong and right:
                    flags = _re_module.IGNORECASE if len(wrong) > 2 else 0
                    parts[index] = _re_module.sub(_re_module.escape(wrong), lambda match: right, parts[index], flags=flags)
        return ''.join(parts)

    def _placeholders_valid(self, text, placeholders):
        actual = [match.group().upper() for match in self._RE_BROKEN_TAG.finditer(text)]
        return actual == [key.upper() for key in placeholders]

    def _translation_valid(self, source, target, game_id=''):
        """Fail closed before commit, resume and PUA conversion."""
        from collections import Counter
        if not isinstance(target, str) or not target.strip():
            return False
        if '\ufffd' in target or _re_module.search(r'\[TAG_', target, _re_module.IGNORECASE):
            return False
        if '\t' in target and '\t' not in source:
            return False
        if game_id and game_id not in source and game_id in target:
            return False
        for match in _re_module.finditer(r'(?m)^\s*([A-Za-z0-9][A-Za-z0-9_:#./-]{4,})(?:[ \t]|$)', target):
            candidate = match.group(1)
            if ('_' in candidate or ':' in candidate or candidate in getattr(self, '_input_ids', ())) and candidate not in source:
                return False
        source_tokens = self._RE_TAG.findall(source)
        target_tokens = self._RE_TAG.findall(target)
        if source_tokens != target_tokens:
            return False
        source_prose = self._RE_TAG.sub('', source)
        target_prose = self._RE_TAG.sub('', target)
        if Counter(self._RE_FOREIGN_SCRIPTS.findall(target_prose)) - Counter(self._RE_FOREIGN_SCRIPTS.findall(source_prose)):
            return False
        if self.use_cjk_filter and TStudioCore.has_cjk(target_prose):
            return False
        if self.use_eng_filter and target_prose.strip().lower() not in self._APPROVED_EXEMPT and self.extract_english_leaks(target_prose):
            return False
        return True

    def _write_atomic(self, headers, rows):
        import tempfile
        if is_web(self.config) and self._disk_signature() != self._web_disk_signature:
            import uuid
            recovery = self.output_csv + '.web-conflict-' + uuid.uuid4().hex + '.csv'
            with open(recovery, 'x', encoding='utf-8-sig', newline='') as handle:
                writer = csv.writer(handle)
                writer.writerow(headers)
                writer.writerows(rows)
            raise WebTransportError("ไฟล์ปลายทางถูกแก้ จึงเก็บผล Web แยกไว้ที่: " + recovery)
        temp_path = None
        try:
            fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(self.output_csv)), suffix='.tmp')
            with os.fdopen(fd, 'w', encoding='utf-8-sig', newline='') as handle:
                writer = csv.writer(handle)
                writer.writerow(headers)
                writer.writerows(rows)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_path, self.output_csv)
            if is_web(self.config):
                self._web_disk_signature = self._disk_signature()
            return True
        finally:
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)

    def enforce_arabic_numerals(self, text):
        import unicodedata
        res = []
        for c in text:
            if c.isdecimal():
                res.append(str(unicodedata.decimal(c)))
            else:
                res.append(c)
        return "".join(res)

    def _get_dynamic_glossary(self, source_text_batch):
        glossary = self.profile.get("glossary", {})
        if not glossary or not isinstance(glossary, dict): return ""
        matched_terms = []
        source_raw = str(source_text_batch or "")
        source_lower = source_raw.lower()
        from tstudio_core import TStudioCore

        # Try to import common generic words helper if available
        try:
            from tstudio_tlm_studio import is_common_generic_english_word
        except ImportError:
            is_common_generic_english_word = None

        matched_compounds = []  # To prevent sub-tokens of matched compounds from triggering
        sorted_terms = sorted(glossary.items(), key=lambda x: len(str(x[0])), reverse=True)
        for eng, val in sorted_terms:
            eng_str = str(eng).strip()
            if not eng_str: continue
            thai = val[0] if (isinstance(val, list) and len(val) > 0) else val
            thai_str = str(thai or "").strip()
            if not thai_str: continue

            # If it's a common generic dictionary word and a single word:
            if is_common_generic_english_word and is_common_generic_english_word(eng_str):
                # Common dictionary words should only match if capitalized in source text (proper noun context)
                if not _re_module.search(r'\b' + _re_module.escape(eng_str) + r'\b', source_raw):
                    continue

            term_lower = eng_str.lower()
            if TStudioCore.has_cjk_or_kana(eng_str):
                is_matched = term_lower in source_lower
            else:
                prefix = r'\b' if _re_module.match(r'^\w', eng_str) else r''
                suffix = r'(?:s|es|\'s)?\b' if _re_module.search(r'\w$', eng_str) else r''
                # If single word and starts with uppercase in glossary, require case match in source to avoid lowercase false positives
                if ' ' not in eng_str and eng_str[0].isupper() and eng_str[1:].islower():
                    pattern_cs = prefix + _re_module.escape(eng_str) + suffix
                    is_matched = bool(_re_module.search(pattern_cs, source_raw))
                else:
                    pattern = prefix + _re_module.escape(term_lower) + suffix
                    is_matched = bool(_re_module.search(pattern, source_lower))

            if is_matched:
                # Substring deduplication: if this term is a single word and is already part of a matched compound (e.g. 'Flight' inside 'Joker Flight'), skip it!
                if ' ' not in eng_str and any(term_lower in m_comp for m_comp in matched_compounds):
                    continue

                if ' ' in eng_str:
                    matched_compounds.append(term_lower)

                cat = val[1] if (isinstance(val, list) and len(val) > 1) else "Term"
                matched_terms.append(f"- \"{eng_str}\" ➔ \"{thai_str}\" ({cat})")

                # Cost-Guard: cap maximum injected glossary terms per batch to prevent token explosion
                if len(matched_terms) >= 15:
                    break

        if matched_terms:
            return (
                "CRITICAL TERMINOLOGY RULES (MANDATORY LOCALIZATION GLOSSARY):\n"
                "You MUST strictly translate the following recognized terms using their exact specified Thai translations:\n"
                + "\n".join(matched_terms)
                + "\n(DO NOT translate these terms into alternative synonyms. Follow the glossary strictly.)"
            )
        return ""

    def stop(self):
        self._is_killed = True

    def _interruptible_sleep(self, seconds):
        """Sleep in 100ms chunks so Stop is responsive within 100ms."""
        end_time = time.time() + seconds
        while not self._is_killed and time.time() < end_time:
            remaining = end_time - time.time()
            time.sleep(min(0.1, max(0.0, remaining)))

    def _strip_outer_quotes(self, s):
        """Safely remove surrounding quotes if they exist, without breaking strings that just start or end with a quote."""
        if s.startswith('"') and s.endswith('"') and len(s) >= 2:
            return s[1:-1]
        return s

    def _normalize_id(self, s):
        """Extract only alphanumeric characters to safely match IDs even if AI strips punctuation like # or { or quotes."""
        import re
        return re.sub(r'[^a-zA-Z0-9]', '', s).lower()

    def _check_peak_hour(self):
        if not self.peak_config:
            return
            
        from PyQt6.QtCore import QTime
        import time
        from tstudio_core import TStudioCore
        
        start_time = self.peak_config['start_time']
        end_time = self.peak_config['end_time']
        action = self.peak_config['action'] # 0 = Pause, 1 = Fallback
        
        while True:
            if self._is_killed:
                break
                
            current_time = QTime.currentTime()
            is_peak = False
            
            # Handle overnight peaks (e.g. 22:00 to 06:00)
            if start_time > end_time:
                if current_time >= start_time or current_time <= end_time:
                    is_peak = True
            else:
                if start_time <= current_time <= end_time:
                    is_peak = True
                    
            if not is_peak:
                # Outside peak hours
                if hasattr(self, '_original_profile'):
                    self.signals.log.emit("Peak-Hour ended. Restoring original profile...", "#a6e3a1")
                    self.profile = self._original_profile
                    delattr(self, '_original_profile')
                break
                
            # It IS Peak Hour!
            if action == 0: # Pause
                self.signals.log.emit("Pausing (Peak-Hour) 💤... Waiting 60s...", "#f9e2af")
                for _ in range(60):
                    if self._is_killed: break
                    time.sleep(1)
                continue
                
            elif action == 1: # Fallback
                if not hasattr(self, '_original_profile'):
                    fallback_name = self.peak_config['fallback_profile']
                    self.signals.log.emit(f"Entering Peak-Hour! Switching to Fallback Profile: {fallback_name}...", "#fab387")
                    self._original_profile = self.profile
                    profiles_data = TStudioCore.load_profiles()
                    fallback_data = profiles_data.get("presets", {}).get(fallback_name)
                    if fallback_data:
                        self.profile = fallback_data
                    else:
                        self.signals.log.emit("Fallback profile not found! Continuing with original.", "#f38ba8")
                break

    def run(self):
        try:
            self._run_impl()
        except Exception as e:
            import traceback
            with open('GUI_CRASH_LOG.txt', 'a') as f:
                f.write('CRASH IN TRunWorker.run\n')
                f.write(traceback.format_exc())
            print('WORKER CRASH:', e)
            self.signals.error.emit(str(e))
            self.signals.finished.emit()
            
    def _run_impl(self):
        import csv, time, re, os, concurrent.futures
        if is_web(self.config):
            self.signals.log.emit("ChatGPT Web | " + self.config["_translation_route"]["model"] + " | background", "#89b4fa")
        self.signals.log.emit(_("log_loading_csv") if '_' in globals() else "Loading CSV...", "#89b4fa")
        rows = []
        headers = []
        try:
            with open(self.input_csv, 'r', encoding='utf-8-sig', newline='') as f:
                reader = csv.reader(f, strict=True)
                headers = next(reader)
                rows = list(reader)
                if len(headers) < 3 or any(len(row) != len(headers) for row in rows):
                    raise ValueError('CSV row width differs from header; restore canonical metadata before translation')
                keys = [row[0] for row in rows]
                if not all(keys) or len(keys) != len(set(keys)):
                    raise ValueError('CSV requires nonempty unique keys for safe reply matching')
                
            if os.path.exists(self.output_csv):
                self.signals.log.emit("Found existing output file. Restoring previous translations...", "#f9e2af")
                try:
                    with open(self.output_csv, 'r', encoding='utf-8-sig', newline='') as f_out:
                        reader_out = csv.reader(f_out, strict=True)
                        next(reader_out, None) 
                        out_dict = {}
                        for r in reader_out:
                            gid = r[0] if len(r) > 0 else ""
                            src = r[1] if len(r) > 1 else ""
                            trans = r[2] if len(r) > 2 else ""
                            if not gid: continue
                            if trans:
                                is_engine_junk = self.auto_filter_engine and self.is_non_translatable_engine_string(src)
                                if is_engine_junk or (self.is_translated(trans) and self._translation_valid(src, trans, gid)):
                                    out_dict[gid] = (src, trans)
                                
                    restored = 0
                    for row_idx, row in enumerate(rows):
                        if len(row) > 0 and row[0] in out_dict:
                            # If selected_row_indices is set, do not restore previous translations for target rows so they get re-translated
                            if self.selected_row_indices is not None and row_idx in self.selected_row_indices:
                                continue
                            prev_src, prev_trans = out_dict[row[0]]
                            curr_src = row[1] if len(row) > 1 else ""
                            # Only restore if source matches (fingerprint verification)
                            if prev_src == curr_src:
                                while len(row) <= 2:
                                    row.append("")
                                row[2] = prev_trans
                                restored += 1
                    
                    if restored > 0:
                        self.signals.log.emit(f"Successfully restored {restored} translated rows! Continuing from where it left off...", "#a6e3a1")
                except Exception as resume_err:
                    self.signals.log.emit(f"Could not read previous output file for resume: {resume_err}", "#f38ba8")
                    self.signals.error.emit(f"Failed to resume from existing output: {resume_err}")
                    return
            
        except Exception as e:
            self.signals.error.emit(f"Failed to read CSV: {e}")
            return

        total_rows = len(rows)
        self.signals.log.emit(_("log_found_rows") if '_' in globals() else f"Found {total_rows} total rows", "#a6e3a1")
        
        col_id = 0
        col_source = 1
        col_trans = 2
        self._input_ids = frozenset(row[0] for row in rows if row)
        
        untranslated = []
        auto_skipped_count = 0
        for i, row in enumerate(rows):
            while len(row) <= col_trans:
                row.append("")
            src = row[col_source] if len(row) > col_source else ""

            # Selected rows mode: ONLY translate specified row indices and always re-translate them
            if self.selected_row_indices is not None:
                if i not in self.selected_row_indices:
                    continue
                if self.auto_filter_engine and self.is_non_translatable_engine_string(src):
                    if not row[col_trans]:
                        row[col_trans] = src
                        self.signals.row_translated.emit(i, row[col_id], src)
                    auto_skipped_count += 1
                    continue
                untranslated.append((i, row))
                continue

            # Engine Junk Auto-Filter: prevent non-translatable engine scripts & control tags from burning tokens
            if self.auto_filter_engine and self.is_non_translatable_engine_string(src):
                if not row[col_trans]:
                    row[col_trans] = src  # Pass-through original engine string to preserve game engine scripts
                    self.signals.row_translated.emit(i, row[col_id], src)
                auto_skipped_count += 1
                continue

            if not self.is_translated(row[col_trans]) or not self._translation_valid(src, row[col_trans], row[col_id]):
                untranslated.append((i, row))

        if auto_skipped_count > 0:
            self.signals.log.emit(f"🛡️ Auto-filtered {auto_skipped_count} engine internal scripts/tags (skipped AI translation to save tokens).", "#a6e3a1")

        if self.selected_row_indices is not None:
            self.signals.log.emit(f"🎯 Target Mode: Translating {len(untranslated)} SELECTED rows (Re-translating in Batch Mode)...", "#cba6f7")
        else:
            self.signals.log.emit(f"Found {len(untranslated)} untranslated rows.", "#f9e2af")
        
        if len(untranslated) == 0:
            if auto_skipped_count > 0:
                self._write_atomic(headers, rows)
                self.signals.log.emit(f"✅ Auto-filtered {auto_skipped_count} engine rows and saved to file.", "#a6e3a1")
            self.signals.log.emit("All rows are already translated!", "#a6e3a1")
            self.processed_count = 0
            self.total_untrans = 0
            self.result_summary = dict(accepted=0, failed=0, save_ok=True)
            self.signals.finished.emit()
            return

        is_local = (self.config.get("provider", "") == "Local LLM" or self.config.get("model", "") == "custom-local-llm")
        
        tpua = None
        if self.use_pua:
            self.signals.log.emit(_("log_init_tpua") if '_' in globals() else "Initializing TPUA...", "#f9e2af")
            from tpua_engine import TPUAEngine
            tpua = TPUAEngine()
            
        row_snippets = {}
        for i, row in untranslated:
            src = row[col_source]
            row_snippets[row[col_id]] = src[:40].replace("\n", " ") + ("..." if len(src) > 40 else "")

        self.processed_count = 0
        self.total_untrans = len(untranslated)

        # Prepare deduplication map if enabled
        source_to_indices = {}
        if self.use_dedup:
            for i, row in untranslated:
                src = row[col_source]
                if src not in source_to_indices:
                    source_to_indices[src] = []
                source_to_indices[src].append((i, row))
            unique_tasks = [indices[0] for indices in source_to_indices.values()]
            saved_duplicate_count = len(untranslated) - len(unique_tasks)
            self.signals.log.emit(f"⚡ Deduplication active: {len(untranslated)} rows reduced to {len(unique_tasks)} unique strings (saved {saved_duplicate_count} duplicate AI requests).", "#89b4fa")
            tasks_to_process = unique_tasks
        else:
            source_to_indices = None
            tasks_to_process = untranslated
        
        if self.token_burner:
            self.signals.log.emit("⚡ TOKEN BURNER MODE ACTIVE ⚡. Processing single rows in parallel.", "#f9e2af")
            system_prompt = self.profile.get("single", "")
            if not system_prompt:
                system_prompt = "Translate the following text to Thai. Preserve all tags.\nOriginal text: {source_text}"
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads) as executor:
                futures = []
                for task_idx, (i, row) in enumerate(tasks_to_process):
                    if self._is_killed: break
                    futures.append(
                        executor.submit(self._process_single, task_idx, len(tasks_to_process), i, row[col_id], row[col_source], system_prompt, is_local, tpua, rows, headers, row_snippets, source_to_indices)
                    )
                
                for future in concurrent.futures.as_completed(futures):
                    if self._is_killed: break
                    try:
                        future.result()
                    except Exception as e_fut:
                        self.signals.log.emit(f'[Error] Thread encountered a fatal error: {e_fut}', '#f38ba8') 
        else:
            system_prompt = self.profile.get("batch", "")
            if "{source_text}" in system_prompt:
                system_prompt = system_prompt.replace("{source_text}", "the user prompt text")

            batches = [tasks_to_process[i:i + self.batch_size] for i in range(0, len(tasks_to_process), self.batch_size)]
            
            self.signals.log.emit(f"Processing {len(batches)} batches ({len(tasks_to_process)} unique rows) using {self.threads} concurrent workers...", "#f9e2af")
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads) as executor:
                futures = []
                for batch_idx, batch in enumerate(batches):
                    if self._is_killed: break
                    futures.append(
                        executor.submit(self._process_batch, batch_idx, len(batches), batch, system_prompt, is_local, tpua, rows, headers, row_snippets, source_to_indices)
                    )
                
                for future in concurrent.futures.as_completed(futures):
                    if self._is_killed: break
                    try:
                        future.result()
                    except Exception as e_fut:
                        self.signals.log.emit(f'[Error] Thread encountered a fatal error: {e_fut}', '#f38ba8')
                    
        if self._transport_error:
            self._save_intermediate(headers, rows, force=True)
            self.signals.error.emit(self._transport_error)
            return

        if self._is_killed:
            self._save_intermediate(headers, rows, force=True)
            self.signals.log.emit("⏹ Stopped. Partial progress saved.", "#f9e2af")
            self.signals.stopped.emit()
            time.sleep(0.2)
            return

        try:
            self._write_atomic(headers, rows)
            self.signals.log.emit("✅ Final save complete.", "#a6e3a1")
        except Exception as e_final:
            self.result_summary = dict(accepted=self.processed_count, failed=self.total_untrans-self.processed_count, save_ok=False)
            self.signals.error.emit(f"Final save failed; previous CSV preserved: {e_final}")
            return
        
        self.signals.progress.emit(self.processed_count, self.total_untrans)
        if self.processed_count < self.total_untrans:
            failed_count = self.total_untrans - self.processed_count
            self.signals.log.emit(f"⚠️ Completed with {failed_count} uncompleted/failed rows.", "#fab387")
        else:
            self.signals.log.emit(_("log_translation_finished") if '_' in globals() else "Translation finished", "#a6e3a1")
        self.result_summary = dict(accepted=self.processed_count, failed=self.total_untrans-self.processed_count, save_ok=True)
        self.signals.finished.emit()
        time.sleep(0.2)

    def _save_intermediate(self, headers, rows, force=False):
        import csv, os, time
        now = time.time()
        if not force:
            last_save = getattr(self, '_last_save_time', 0.0)
            if now - last_save < 15.0:  # Throttle full CSV writes to at most once per 15 seconds
                return
        with self.save_lock:
            if not force:
                last_save = getattr(self, '_last_save_time', 0.0)
                if now - last_save < 15.0:
                    return
            self._last_save_time = time.time()
            try:
                self._write_atomic(headers, rows)
            except Exception as e:
                self.signals.log.emit(f"Failed to save intermediate: {e}", "#f38ba8")

    def _update_progress(self, count=1):
        with self.save_lock:
            self.processed_count += count
            self.signals.progress.emit(self.processed_count, self.total_untrans)

    def _process_single(self, task_idx, total_tasks, row_idx, game_id, source_text, system_prompt, is_local, tpua, rows, headers, row_snippets, source_to_indices=None):
        if self._is_killed: return False
        self._check_peak_hour()
        from tstudio_core import CoreAI
        import re
        
        if self.use_mask:
            masked, placeholders = self.mask_tags(source_text)
        else:
            masked, placeholders = source_text, {}
            
        full_prompt = system_prompt.replace("{id}", game_id).replace("{source_text}", masked)
        if is_web(self.config):
            glossary = self._get_dynamic_glossary(source_text)
            if "[GLOSSARY TO USE]" in full_prompt:
                full_prompt = full_prompt.replace("[GLOSSARY TO USE]", glossary)
            elif glossary:
                full_prompt = glossary + "\n\n" + full_prompt
        
        success = False
        target_rows = [(row_idx, game_id)]
        for attempt in range(1, self.max_retries + 1):
            if self._is_killed: break
            try:
                reply = self._generate_translation(full_prompt, is_local)
                translated = reply.strip()
                translated = self._RE_CODE_FENCE_START.sub('', translated)
                translated = self._RE_CODE_FENCE_END.sub('', translated)
                
                translated = translated.replace('\\n', '\n')
                if self.use_mask and not self._placeholders_valid(translated, placeholders):
                    self.signals.log.emit(f"[Rejected] {game_id}: placeholder count/order mismatch", "#fab387")
                    continue
                if self.use_glossary: translated = self.enforce_glossary(translated)
                # Normalize prose while protected tokens are still masked.
                translated = self.enforce_arabic_numerals(translated)
                if self.use_mask: translated = self.unmask_tags(translated, placeholders)
                try:
                    translated, _ = TStudioCore.retrofit_military_text(source_text, translated)
                except Exception:
                    pass
                if self.use_cjk_filter: translated = TStudioCore.clean_cjk_leak(translated)
                if not self._translation_valid(source_text, translated, game_id):
                    self.signals.log.emit(f"[Rejected] {game_id}: unsafe translation; retrying", "#fab387")
                    continue

                if self.use_pua and tpua: translated = tpua.encode(translated)
                
                if source_to_indices and source_text in source_to_indices:
                    target_rows = [(dup_i, dup_row[0]) for dup_i, dup_row in source_to_indices[source_text]]

                with self.save_lock:
                    for t_idx, t_gid in target_rows:
                        rows[t_idx][2] = translated
                for t_idx, t_gid in target_rows:
                    self.signals.row_translated.emit(t_idx, t_gid, translated)
                    
                src_snip = row_snippets.get(game_id, game_id)
                tsnippet = translated[:40].replace('\n', ' ') + ("..." if len(translated) > 40 else "")
                if len(target_rows) > 1:
                    self.signals.log.emit(f"  ✅ [⚡ {task_idx+1}/{total_tasks}] Propagated {len(target_rows)} identical rows ({src_snip} → {tsnippet})", "#a6e3a1")
                else:
                    self.signals.log.emit(f"  ✅ [⚡ {task_idx+1}/{total_tasks}] {src_snip} → {tsnippet}", "#a6e3a1")
                
                success = True
                break
            except WebTransportError:
                return False
            except Exception as e:
                err_str = str(e).lower()
                wait_sec = 65 if ("429" in err_str or "quota" in err_str) else min(2 ** attempt, 30)
                self.signals.log.emit(f"  [Error] {game_id} — Waiting {wait_sec}s...", "#f38ba8")
                self._interruptible_sleep(wait_sec)
                
        if success:
            self._update_progress(len(target_rows))
            if (task_idx + 1) % max(1, (total_tasks // 20)) == 0:
                self._save_intermediate(headers, rows)
                
        return success

    def _process_batch(self, batch_idx, total_batches, batch, batch_system_prompt_base, is_local, tpua, rows, headers, row_snippets, source_to_indices=None):
        if self._is_killed: return False
        self._check_peak_hour()
        from tstudio_core import CoreAI
        import re
        
        self.signals.batch_progress.emit(batch_idx + 1, total_batches)
        
        batch_tasks = []
        lines_to_send = []
        for i, row in batch:
            game_id = row[0]
            source_text = row[1]
            if self.use_mask:
                masked, placeholders = self.mask_tags(source_text)
            else:
                masked, placeholders = source_text, {}
            batch_tasks.append((i, game_id, placeholders))
            lines_to_send.append(f'{game_id}	{masked}')
            
        combined_source = " ".join([row[1] for i, row in batch])
        dyn_glossary = self._get_dynamic_glossary(combined_source)
        
        # Sanitize single-line specific instructions from batch system prompt
        clean_batch_prompt = batch_system_prompt_base
        clean_batch_prompt = clean_batch_prompt.replace("ID: '{id}'.", "")
        clean_batch_prompt = clean_batch_prompt.replace("ID: \"{id}\".", "")
        clean_batch_prompt = clean_batch_prompt.replace("ID: {id}.", "")
        clean_batch_prompt = clean_batch_prompt.replace("{id}", "")
        clean_batch_prompt = re.sub(r'do NOT (?:translate or )?include the Context ID[^\.\n]*[\.\n]?', '', clean_batch_prompt, flags=re.IGNORECASE)
        clean_batch_prompt = clean_batch_prompt.replace("Translate this line.", "Translate each line.")
        clean_batch_prompt = clean_batch_prompt.replace("Return ONLY the pure Thai string, no quotes, no explanations.", "")
        clean_batch_prompt = clean_batch_prompt.replace("Return ONLY the pure Thai string", "")
        clean_batch_prompt = re.sub(r'CRITICAL:\s*If the text is short[^\.\n]*ONLY return the direct translation\.[^\n]*', '', clean_batch_prompt, flags=re.IGNORECASE)
        clean_batch_prompt = clean_batch_prompt.replace("ONLY return the direct translation.", "")
        
        if "[GLOSSARY TO USE]" in clean_batch_prompt:
            batch_system_prompt = clean_batch_prompt.replace("[GLOSSARY TO USE]", dyn_glossary if dyn_glossary else "")
        else:
            batch_system_prompt = clean_batch_prompt
            if dyn_glossary:
                batch_system_prompt = dyn_glossary + "\n\n" + batch_system_prompt
        
        batch_system_prompt += (
            "\n\nCRITICAL FORMAT & PURITY RULES (MUST FOLLOW):\n"
            "1. Reply ONLY with the translations, one per line. No conversational text.\n"
            "2. Each line MUST be formatted exactly as: ID\tTRANSLATION (Do NOT omit the ID prefix or the tab!).\n"
            "3. Do NOT use spaces instead of tabs. Do NOT output markdown tables.\n"
            "4. STRICT THAI ONLY (ZERO ENGLISH LEAKAGE): Translate or phonetically transliterate English words into Thai (e.g. 'Quest' -> 'เควสต์', 'Inventory' -> 'ช่องเก็บของ', 'Attack' -> 'โจมตี').\n"
            "   CRITICAL EXCEPTIONS (KEEP IN ORIGINAL LATIN SCRIPT):\n"
            "   - Keyboard Keys, Mouse & Gamepad: 'Spacebar'/'Space' (NEVER 'สเปคบรา'/'เว้นวรรค'), 'Enter' (NEVER 'เอ็นเทอ'/'ป้อน'), 'Shift', 'Ctrl', 'Alt', 'Tab', 'Esc', 'Backspace', 'Delete', 'Insert', 'Num Lock', 'Page Up', 'Page Down', 'WASD', 'LMB', 'RMB'.\n"
            "   - Firearms, Military & Vehicles: 'M16', 'AK-47', 'RPG-7', 'SMG', 'LMG', 'DMR', 'Humvee', 'APC', '9mm', '5.56mm'.\n"
            "   - Game variables & tags: {0}, %s, <tag>, [KEY].\n"
            "5. STRICT LANGUAGE PURITY: NEVER output Chinese characters (汉字), Japanese Kana, or Chinese commentary.\n"
            "6. Example output line:\n"
            "MyStringID\tคำแปลของฉัน"
        )
        
        success = False
        batch_processed_count = 0
        
        for attempt in range(1, self.max_retries + 1):
            if self._is_killed: break
            user_prompt = (dyn_glossary + "\n\n" if (dyn_glossary and "[GLOSSARY TO USE]" not in clean_batch_prompt) else "") + "Translate these entries:\n" + "\n".join(lines_to_send)
            full_prompt = batch_system_prompt + "\n\n" + user_prompt

            if is_web(self.config):
                # Browser Markdown collapses TSV tabs and escapes plain-text underscores.
                # A fenced JSON payload preserves exact IDs and masked game placeholders.
                import json
                entries = [{'id': line.partition('\t')[0], 'source': line.partition('\t')[2]}
                           for line in lines_to_send]
                web_rules = (
                    '\n\nWEB TRANSPORT OUTPUT CONTRACT (replaces earlier TSV/TAB output rules):\n'
                    'Reply with exactly one fenced json code block containing a JSON array. '
                    'Each object must have exactly "id" and "translation" string fields. '
                    'Copy every id exactly. Preserve all game tags and [TAG_0] style placeholders exactly. '
                    'Do not output a Markdown table or TSV. Do not escape underscores or brackets '
                    'as Markdown inside JSON strings. Return only that JSON code block.\n'
                    'Example: [{"id":"example_key","translation":"คำแปล"}]\n\nENTRIES:\n'
                )
                full_prompt = (batch_system_prompt.split('\n\nCRITICAL FORMAT & PURITY RULES (MUST FOLLOW):')[0]
                               + web_rules + json.dumps(entries, ensure_ascii=False))

            
            try:
                reply = self._generate_translation(full_prompt, is_local)
                if is_web(self.config):
                    try:
                        reply = TranslationGateway.strict_batch_reply(reply, [gid for _, gid, _ in batch_tasks])
                    except WebTransportError as error:
                        self._transport_error = str(error)
                        self._is_killed = True
                        return False
                reply = self._RE_CODE_FENCE_START.sub('', reply.strip())
                reply = self._RE_CODE_FENCE_END.sub('', reply)
                
                results = {}
                seen_ids = set()
                duplicate_ids = set()
                current_id = None
                valid_ids = {game_id for _, game_id, _ in batch_tasks}
                valid_ids_ci = {gid.lower(): gid for _, gid, _ in batch_tasks}
                suffix_map = {}
                for _, gid, _ in batch_tasks:
                    if "::" in gid:
                        sfx = gid.split("::")[-1].strip().lower()
                        suffix_map[sfx] = gid
                    elif "/" in gid:
                        sfx = gid.split("/")[-1].strip().lower()
                        suffix_map[sfx] = gid
                
                for line in reply.split('\n'):
                    stripped = line.strip()
                    if not stripped: continue
                    
                    if '\t' in stripped:
                        tab_pos = stripped.index('\t')
                        candidate_id = self._strip_outer_quotes(stripped[:tab_pos].strip())
                        candidate_val = self._strip_outer_quotes(stripped[tab_pos + 1:].strip())
                        
                        matched_id = None
                        if candidate_id in valid_ids:
                            matched_id = candidate_id
                        elif candidate_id.lower() in valid_ids_ci:
                            matched_id = valid_ids_ci[candidate_id.lower()]
                        elif candidate_id.lower() in suffix_map:
                            matched_id = suffix_map[candidate_id.lower()]
                        
                        if matched_id is not None:
                            if matched_id in seen_ids:
                                # Duplicate ID detected! Mark duplicate and do not overwrite
                                duplicate_ids.add(matched_id)
                                current_id = None
                            else:
                                seen_ids.add(matched_id)
                                current_id = matched_id
                                results[current_id] = candidate_val
                        else:
                            # Unknown ID with tab: DO NOT attach to previous ID!
                            current_id = None
                    elif current_id is not None:
                        # An unframed line invalidates the preceding record.
                        duplicate_ids.add(current_id)
                        current_id = None
                        
                # Auto-recovery fallback:
                # If no valid IDs were matched or some are missing, check if the LLM outputted
                # lines in the exact 1:1 sequence corresponding to batch_tasks.
                clean_reply_lines = [
                    l.strip() for l in reply.split('\n')
                    if l.strip() and not l.strip().startswith('```')
                ]
                if len(clean_reply_lines) == len(batch_tasks) + 1 and clean_reply_lines[0].lower().startswith(('here is', 'here are', 'translations:', 'sure', 'certainly')):
                    clean_reply_lines = clean_reply_lines[1:]

                if len(results) < len(batch_tasks) and len(clean_reply_lines) == len(batch_tasks):
                    for idx_seq, (t_i, t_gid, t_ph) in enumerate(batch_tasks):
                        if t_gid not in results:
                            line_val = clean_reply_lines[idx_seq]
                            if '\t' in line_val:
                                line_val = line_val.split('\t', 1)[1].strip()
                            else:
                                line_val = re.sub(r'^\d+[\.\)]\s*', '', line_val)
                            results[t_gid] = self._strip_outer_quotes(line_val.strip())
                        
                remaining_tasks = []
                remaining_lines = []
                
                for idx_zip, (i, game_id, placeholders) in enumerate(batch_tasks):
                    if game_id in results and game_id not in duplicate_ids:
                        translated = results[game_id]
                        translated = translated.replace('\\n', '\n')
                        
                        source_text = rows[i][1]
                        valid_placeholders = not self.use_mask or self._placeholders_valid(translated, placeholders)
                        if valid_placeholders:
                            if self.use_glossary: translated = self.enforce_glossary(translated)
                            translated = self.enforce_arabic_numerals(translated)
                            if self.use_mask: translated = self.unmask_tags(translated, placeholders)
                            try:
                                translated, _ = TStudioCore.retrofit_military_text(source_text, translated)
                            except Exception:
                                pass
                            if self.use_cjk_filter: translated = TStudioCore.clean_cjk_leak(translated)
                        if not valid_placeholders or not self._translation_valid(source_text, translated, game_id):
                            self.signals.log.emit(f"[Rejected] {game_id}: unsafe translation; retrying", "#fab387")
                            remaining_tasks.append((i, game_id, placeholders))
                            remaining_lines.append(lines_to_send[idx_zip])
                            continue

                        if self.use_pua and tpua: translated = tpua.encode(translated)
                        
                        target_rows = [(i, game_id)]
                        if source_to_indices and source_text in source_to_indices:
                            target_rows = [(dup_i, dup_row[0]) for dup_i, dup_row in source_to_indices[source_text]]

                        with self.save_lock:
                            for t_idx, t_gid in target_rows:
                                rows[t_idx][2] = translated
                                
                        for t_idx, t_gid in target_rows:
                            self.signals.row_translated.emit(t_idx, t_gid, translated)
                            
                        batch_processed_count += len(target_rows)
                        last_src_snip = row_snippets.get(game_id, game_id)
                        last_tsnippet = translated[:40].replace('\n', ' ') + ("..." if len(translated) > 40 else "")
                    else:
                        remaining_tasks.append((i, game_id, placeholders))
                        remaining_lines.append(lines_to_send[idx_zip])
                        
                batch_tasks = remaining_tasks
                lines_to_send = remaining_lines
                
                if batch_processed_count > 0:
                    if batch_processed_count == 1:
                        self.signals.log.emit(f"  ✅ [Batch {batch_idx+1}/{total_batches}] {last_src_snip} → {last_tsnippet}", "#a6e3a1")
                    else:
                        self.signals.log.emit(f"  ✅ [Batch {batch_idx+1}/{total_batches}] Translated {batch_processed_count} rows ({last_src_snip} → {last_tsnippet})", "#a6e3a1")
                
                if len(batch_tasks) == 0:
                    success = True
                    break
                elif len(results) == 0:
                    try:
                        with open(rf"E:\Mod_Workspace\Modder_project\modder-hub\tools\flagship\TRun\batch_{batch_idx+1}_debug.txt", "w", encoding="utf-8") as f:
                            f.write("PROMPT:\n" + full_prompt + "\n\nREPLY:\n" + reply)
                    except: pass
                    wait_sec = min(2 ** attempt, 30)
                    self.signals.log.emit(f"  [Warning] Batch {batch_idx+1} no results (attempt {attempt}). Waiting {wait_sec}s...", "#f38ba8")
                    self._interruptible_sleep(wait_sec)
                else:
                    self.signals.log.emit(f"  [Warning] Batch {batch_idx+1} partial. Retrying {len(batch_tasks)} missing lines...", "#f9e2af")
                    
            except WebTransportError:
                return False
            except Exception as e:
                err_str = str(e).lower()
                wait_sec = 65 if ("429" in err_str or "quota" in err_str) else min(2 ** attempt, 30)
                self.signals.log.emit(f"  [Error] Batch {batch_idx+1} - {e} — Waiting {wait_sec}s...", "#f38ba8")
                self._interruptible_sleep(wait_sec)
                
        if not success and not self._is_killed:
            self.signals.log.emit(f"Batch {batch_idx+1} failed after {self.max_retries} retries. Skipping...", "#f38ba8")
            
        if batch_processed_count > 0:
            self._update_progress(batch_processed_count)
            self._save_intermediate(headers, rows)
            
        self._interruptible_sleep(self.delay_ms / 1000.0)
        return success


from tstudio_ui_shared import SettingsDialog, PromptSettingsDialog, GlossaryWidget

# Dark theme identical to TStudio
DARK_SS = """
QMainWindow, QWidget, QDialog { background: #1e1e2e; color: #cdd6f4; }
QLineEdit, QTextEdit { background: #313244; color: #cdd6f4; border: 1px solid #45475a; border-radius: 4px; padding: 6px; font-size: 14px; }
QPushButton { background: #45475a; color: #cdd6f4; border: none; border-radius: 4px; padding: 8px 16px; font-size: 13px; font-weight: bold; }
QPushButton:hover { background: #585b70; }
QPushButton:disabled { background: #313244; color: #a6adc8; }
QGroupBox { border: 1px solid #45475a; border-radius: 6px; margin-top: 10px; padding-top: 14px; font-weight: bold; color: #89b4fa; }
QComboBox { background: #313244; color: #cdd6f4; border: 1px solid #45475a; border-radius: 4px; padding: 4px 8px; }
QProgressBar { border: 1px solid #45475a; border-radius: 4px; text-align: center; }
QProgressBar::chunk { background-color: #a6e3a1; }
QTableView, QTableWidget { background: #181825; color: #cdd6f4; gridline-color: #313244; selection-background-color: #45475a; alternate-background-color: #1e1e2e; font-size: 13px; }
QHeaderView::section { background: #313244; color: #a6adc8; padding: 6px; border: 1px solid #45475a; font-weight: bold; }
"""

class TRunApp(QMainWindow):
    def __init__(self, project_path=None):
        super().__init__()
        self.project_path = project_path
        
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

        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('flagship.trun.app.1.0')
        except:
            pass
        self.setWindowTitle(_("window_title"))
        self.resize(1100, 750)
        self.setStyleSheet(DARK_SS)
        
        logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "assets", "TRun.ico"))
        if not os.path.exists(logo_path):
            logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "assets", "TRun.png"))
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))
        
        self.threadpool = QThreadPool()
        self.profiles_data = TStudioCore.load_profiles()
        self.is_running = False
        self._workers = []  # Keep ApiWorker references alive until QThreadPool finishes
        
        # High-performance async log buffering
        self._log_queue = []
        self._log_timer = QTimer(self)
        self._log_timer.setInterval(50)  # Flush batched logs every 50ms
        self._log_timer.timeout.connect(self._flush_logs)

        self.init_ui()
        self.refresh_profiles_combo()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        
        # --- HEADER: Profiles & Settings ---
        header_layout = QHBoxLayout()
        self.translation_channel = TranslationChannelWidget(self)
        header_layout.addWidget(self.translation_channel)
        header_layout.addWidget(QLabel("📂 Active Profile:"))
        self.cbo_preset = QComboBox()
        self.cbo_preset.currentTextChanged.connect(self.on_preset_changed)
        header_layout.addWidget(self.cbo_preset)
        
        btn_new_profile = QPushButton(_("btn_new"))
        btn_new_profile.setToolTip(_("tooltip_new_profile"))
        btn_new_profile.clicked.connect(self.create_new_profile)
        btn_rename_profile = QPushButton(_("btn_rename"))
        btn_rename_profile.setToolTip(_("tooltip_rename_profile"))
        btn_rename_profile.clicked.connect(self.rename_profile)
        btn_del_profile = QPushButton(_("btn_delete"))
        btn_del_profile.setToolTip(_("tooltip_del_profile"))
        btn_del_profile.clicked.connect(self.delete_profile)
        
        header_layout.addWidget(btn_new_profile)
        header_layout.addWidget(btn_rename_profile)
        header_layout.addWidget(btn_del_profile)
        
        btn_prompt = QPushButton(_("act_ai_prompt_settings"))
        btn_prompt.setToolTip(_("tooltip_prompt"))
        btn_prompt.clicked.connect(self.open_prompts)
        btn_glossary = QPushButton(_("glossary_dock_title"))
        btn_glossary.setToolTip(_("tooltip_glossary"))
        btn_glossary.clicked.connect(self.open_glossary)
        btn_settings = QPushButton(_("btn_api_settings"))
        btn_settings.setToolTip(_("tooltip_settings"))
        btn_settings.clicked.connect(self.open_settings)
        
        header_layout.addWidget(btn_prompt)
        header_layout.addWidget(btn_glossary)
        header_layout.addWidget(btn_settings)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # --- SPLITTER ---
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # --- LEFT PANEL: Settings & Config ---
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 10, 0)
        
        # File Config
        grp_file = QGroupBox(_("grp_file_config"))
        l_file = QVBoxLayout(grp_file)
        
        # New List Input
        h_buttons = QHBoxLayout()
        btn_in_file = QPushButton(_("btn_file_add") if '_' in globals() else "Add File(s)...")
        btn_in_file.clicked.connect(self.browse_input)
        btn_in_folder = QPushButton(_("btn_folder_add") if '_' in globals() else "Add Folder...")
        btn_in_folder.clicked.connect(self.browse_input_folder)
        btn_remove = QPushButton(_("btn_remove_sel") if '_' in globals() else "Remove Selected")
        btn_remove.setStyleSheet("color: #f38ba8;")
        btn_remove.clicked.connect(self.remove_selected_input)
        btn_clear = QPushButton(_("btn_clear_all") if '_' in globals() else "Clear All")
        btn_clear.setStyleSheet("color: #f38ba8;")
        btn_clear.clicked.connect(self.clear_input_list)
        
        h_buttons.addWidget(btn_in_file)
        h_buttons.addWidget(btn_in_folder)
        h_buttons.addWidget(btn_remove)
        h_buttons.addWidget(btn_clear)
        l_file.addLayout(h_buttons)
        
        from PyQt6.QtWidgets import QHeaderView
        self.tbl_input = QTableWidget(0, 2)
        self.tbl_input.setHorizontalHeaderLabels([_("lbl_file_path") if '_' in globals() else "File Path", _("lbl_profile") if '_' in globals() else "Profile"])
        self.tbl_input.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tbl_input.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_input.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tbl_input.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.tbl_input.setFixedHeight(120)
        self.tbl_input.model().rowsInserted.connect(self.update_preview)
        self.tbl_input.model().rowsRemoved.connect(self.update_preview)
        l_file.addWidget(self.tbl_input)
        
        self.lbl_file_progress = QLabel(_("lbl_file_progress_default"))
        self.lbl_file_progress.setStyleSheet("color: #a6adc8; font-weight: bold; font-size: 11px;")
        self.lbl_file_progress.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_file_progress.hide() # Hidden until batch starts
        
        # We will add it to the progress layout later, wait we need to find where progress is.
        # Actually just add it after l_file.
        l_file.addWidget(self.lbl_file_progress)
        
        self.file_queue = []
        self.total_files = 0
        self.current_file_index = 0
        self.output_is_folder = False
        
        left_layout.addWidget(grp_file)

        # Batch Engine Config
        grp_engine = QGroupBox(_("grp_engine_config"))
        l_engine = QVBoxLayout(grp_engine)
        
        h_batch = QHBoxLayout()
        h_batch.addWidget(QLabel(_("lbl_batch_size")))
        self.slider_batch = QSlider(Qt.Orientation.Horizontal)
        self.slider_batch.setRange(1, 100)
        self.slider_batch.setValue(20)
        self.spin_batch_val = QSpinBox()
        self.spin_batch_val.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
        self.spin_batch_val.setRange(1, 100)
        self.spin_batch_val.setValue(20)
        self.spin_batch_val.setFixedWidth(70)
        
        self.slider_batch.valueChanged.connect(self.spin_batch_val.setValue)
        self.spin_batch_val.valueChanged.connect(self.slider_batch.setValue)
        
        h_batch.addWidget(self.slider_batch)
        h_batch.addWidget(self.spin_batch_val)
        
        self.chk_unlock = QCheckBox(_("chk_unlock_risk"))
        self.chk_unlock.setStyleSheet("color: #f38ba8;")
        self.chk_unlock.toggled.connect(self.toggle_risk)
        h_batch.addWidget(self.chk_unlock)
        l_engine.addLayout(h_batch)
        
        h_delay = QHBoxLayout()
        h_delay.addWidget(QLabel(_("lbl_delay")))
        self.spin_delay = QSpinBox()
        self.spin_delay.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
        self.spin_delay.setRange(0, 10000)
        self.spin_delay.setValue(200)
        h_delay.addWidget(self.spin_delay)
        l_engine.addLayout(h_delay)
        
        h_retry = QHBoxLayout()
        h_retry.addWidget(QLabel(_("lbl_max_retries")))
        self.spin_retry = QSpinBox()
        self.spin_retry.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
        self.spin_retry.setRange(0, 10)
        self.spin_retry.setValue(3)
        h_retry.addWidget(self.spin_retry)
        l_engine.addLayout(h_retry)
        
        # New: Concurrent Workers
        h_threads = QHBoxLayout()
        h_threads.addWidget(QLabel("Concurrent Workers (Threads):" if '_' not in globals() else _("lbl_threads")))
        self.spin_threads = QSpinBox()
        self.spin_threads.setRange(1, 100)
        self.spin_threads.setValue(32) # Default 32 for fast mode
        h_threads.addWidget(self.spin_threads)
        
        self.chk_token_burner = QCheckBox("⚡ Token Burner Mode (Fast, 1 API call per row)" if '_' not in globals() else _("chk_token_burner"))
        self.chk_token_burner.setStyleSheet("color: #f9e2af; font-weight: bold;")
        self.chk_token_burner.toggled.connect(self.on_token_burner_toggled)
        h_threads.addWidget(self.chk_token_burner)
        l_engine.addLayout(h_threads)
        
        self.lbl_preview = QLabel(_("lbl_preview_default"))
        self.lbl_preview.setStyleSheet("color: #a6e3a1; font-weight: normal; margin-top: 10px; padding: 6px; border: 1px solid #45475a; border-radius: 4px; background: #181825;")
        self.lbl_preview.setWordWrap(True)
        l_engine.addWidget(self.lbl_preview)
        
        left_layout.addWidget(grp_engine)
        
        # Processing Options
        grp_opts = QGroupBox(_("grp_post_processing"))
        l_opts = QVBoxLayout(grp_opts)
        self.chk_mask = QCheckBox(_("chk_auto_mask"))
        self.chk_mask.setChecked(True)
        self.chk_glossary = QCheckBox(_("chk_enforce_glossary"))
        self.chk_glossary.setChecked(True)
        self.chk_pua = QCheckBox(_("chk_auto_pua"))
        self.chk_pua.setChecked(False) # Will implement TPUA next phase
        self.chk_cjk_filter = QCheckBox(_("chk_cjk_filter") if '_' in globals() else "🇨🇳 กรอง/ล้างภาษาจีนที่หลุดมา (CJK Leak Filter)")
        self.chk_cjk_filter.setChecked(True)
        self.chk_cjk_filter.setToolTip("ตรวจจับและป้องกันข้อความภาษาจีนหรือคอมเมนต์ AI จาก DeepSeek หลุดเข้าไปในคำแปล")
        self.chk_eng_filter = QCheckBox(_("chk_eng_filter") if '_' in globals() else "🇬🇧 กรอง/แปลซ้ำภาษาอังกฤษตกค้าง (English Leak Filter)")
        self.chk_eng_filter.setChecked(True)
        self.chk_eng_filter.setToolTip("ตรวจจับคำภาษาอังกฤษที่ยังไม่ได้แปล (นอกเหนือจากแท็กเกม) และส่งคำสั่งแปลซ้ำเป็นภาษาไทยล้วนให้อัตโนมัติ")
        self.chk_dedup = QCheckBox(_("chk_dedup") if '_' in globals() else "⚡ แปลเฉพาะข้อความไม่ซ้ำ (Deduplication & Auto-Propagate)")
        self.chk_dedup.setChecked(True)
        self.chk_dedup.setStyleSheet("color: #a6e3a1; font-weight: bold;")
        self.chk_dedup.setToolTip("รวมข้อความที่เหมือนกันให้แปลเพียงครั้งเดียว แล้วกระจายผลลัพธ์ไปยังทุกแถวอัตโนมัติ ประหยัดโทเค็นได้ 50-80%")
        self.chk_engine_filter = QCheckBox(_("chk_engine_filter") if '_' in globals() else "🛡️ กรองคำสั่งเอนจิน/แท็กล้วน ไม่ส่ง AI (Engine Junk Filter)")
        self.chk_engine_filter.setChecked(True)
        self.chk_engine_filter.setStyleSheet("color: #f9e2af; font-weight: bold;")
        self.chk_engine_filter.setToolTip("กรองคำสั่งสคริปต์ภายในเอนจิน (เช่น ■... ใน WOLF RPG) หรือแท็กตัวแปรล้วน ไม่ส่งไป AI เพื่อป้องกันโทเค็นรั่วไหล")
        l_opts.addWidget(self.chk_mask)
        l_opts.addWidget(self.chk_glossary)
        l_opts.addWidget(self.chk_pua)
        l_opts.addWidget(self.chk_cjk_filter)
        l_opts.addWidget(self.chk_eng_filter)
        l_opts.addWidget(self.chk_dedup)
        l_opts.addWidget(self.chk_engine_filter)
        left_layout.addWidget(grp_opts)
        
        # --- Scheduling & Peak-Hour ---
        grp_peak = QGroupBox(_("grp_scheduling_peak") if '_' in globals() else "⏳ Scheduling & Peak-Hour")
        l_peak = QVBoxLayout(grp_peak)
        
        # Schedule Start
        h_sched = QHBoxLayout()
        self.chk_schedule = QCheckBox(_("chk_schedule_start") if '_' in globals() else "Schedule Start Time")
        self.time_schedule = QTimeEdit()
        self.time_schedule.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
        self.time_schedule.setDisplayFormat("HH:mm")
        self.time_schedule.setEnabled(False)
        self.chk_schedule.toggled.connect(self.time_schedule.setEnabled)
        h_sched.addWidget(self.chk_schedule)
        h_sched.addWidget(self.time_schedule)
        l_peak.addLayout(h_sched)
        
        # Auto Shutdown
        self.chk_auto_shutdown = QCheckBox(_("chk_auto_shutdown") if '_' in globals() else "Auto Shutdown when finished")
        self.chk_auto_shutdown.setStyleSheet("color: #f38ba8; font-weight: bold;")
        self.chk_auto_shutdown.setToolTip("Shutdown the computer when all items in the queue finish successfully.")
        l_peak.addWidget(self.chk_auto_shutdown)
        
        # Peak-Hour Management
        self.chk_peak = QCheckBox(_("chk_enable_peak") if '_' in globals() else "Enable Peak-Hour Management")
        l_peak.addWidget(self.chk_peak)
        
        self.w_peak_opts = QWidget()
        self.w_peak_opts.setEnabled(False)
        self.chk_peak.toggled.connect(self.w_peak_opts.setEnabled)
        l_peak_opts = QVBoxLayout(self.w_peak_opts)
        l_peak_opts.setContentsMargins(16, 0, 0, 0)
        
        h_peak_time = QHBoxLayout()
        self.time_peak_start = QTimeEdit()
        self.time_peak_start.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
        self.time_peak_start.setDisplayFormat("HH:mm")
        self.time_peak_start.setTime(QTime(18, 0))
        h_peak_time.addWidget(QLabel("Peak Start:"))
        h_peak_time.addWidget(self.time_peak_start)
        
        self.time_peak_end = QTimeEdit()
        self.time_peak_end.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
        self.time_peak_end.setDisplayFormat("HH:mm")
        self.time_peak_end.setTime(QTime(22, 0))
        h_peak_time.addWidget(QLabel("End:"))
        h_peak_time.addWidget(self.time_peak_end)
        l_peak_opts.addLayout(h_peak_time)
        
        h_peak_action = QHBoxLayout()
        h_peak_action.addWidget(QLabel("Action:"))
        self.cbo_peak_action = QComboBox()
        self.cbo_peak_action.addItems([
            _("opt_peak_pause") if '_' in globals() else "Pause Translation (Sleep)",
            _("opt_peak_fallback") if '_' in globals() else "Switch to Fallback Profile"
        ])
        h_peak_action.addWidget(self.cbo_peak_action)
        l_peak_opts.addLayout(h_peak_action)
        
        h_peak_fallback = QHBoxLayout()
        self.lbl_peak_fallback = QLabel("Fallback Profile:")
        self.cbo_peak_fallback = QComboBox()
        # Profiles will be populated when preset combo changes
        h_peak_fallback.addWidget(self.lbl_peak_fallback)
        h_peak_fallback.addWidget(self.cbo_peak_fallback)
        self.w_peak_fallback = QWidget()
        self.w_peak_fallback.setLayout(h_peak_fallback)
        self.w_peak_fallback.setVisible(False)
        
        self.cbo_peak_action.currentIndexChanged.connect(lambda idx: self.w_peak_fallback.setVisible(idx == 1))
        l_peak_opts.addWidget(self.w_peak_fallback)
        
        l_peak.addWidget(self.w_peak_opts)
        left_layout.addWidget(grp_peak)
        
        left_layout.addStretch()
        splitter.addWidget(left_panel)
        
        # --- RIGHT PANEL: Dashboard ---
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 0, 0, 0)
        
        # Stats
        h_batch_stats = QHBoxLayout()
        self.lbl_batch_progress = QLabel(_("lbl_batch_progress_default"))
        self.lbl_batch_progress.setStyleSheet("color: #89b4fa; font-weight: bold;")
        h_batch_stats.addWidget(self.lbl_batch_progress)
        h_batch_stats.addStretch()
        
        self.lbl_eta = QLabel(_("lbl_eta_default"))
        h_batch_stats.addWidget(self.lbl_eta)
        right_layout.addLayout(h_batch_stats)
        
        self.batch_progress_bar = QProgressBar()
        self.batch_progress_bar.setValue(0)
        self.batch_progress_bar.setStyleSheet("QProgressBar { border: 1px solid #45475a; border-radius: 4px; text-align: center; } QProgressBar::chunk { background-color: #89b4fa; }")
        right_layout.addWidget(self.batch_progress_bar)
        
        h_stats = QHBoxLayout()
        self.lbl_progress = QLabel(_("lbl_lines_default"))
        self.lbl_progress.setStyleSheet("color: #a6e3a1; font-weight: bold;")
        h_stats.addWidget(self.lbl_progress)
        h_stats.addStretch()
        right_layout.addLayout(h_stats)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        right_layout.addWidget(self.progress_bar)
        
        # Tabs for Tracker and Log
        self.tab_right = QTabWidget()
        
        # Queue Tracker Tab
        self.tbl_queue = QTableWidget()
        self.tbl_queue.setColumnCount(2)
        self.tbl_queue.setHorizontalHeaderLabels(["Filename", "Status"])
        self.tbl_queue.horizontalHeader().setStretchLastSection(True)
        self.tbl_queue.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl_queue.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tbl_queue.setStyleSheet("""
            QTableWidget { background: #1e1e2e; color: #cdd6f4; gridline-color: #313244; border: none; }
            QHeaderView::section { background: #181825; color: #a6adc8; padding: 4px; border: 1px solid #313244; }
        """)
        self.tab_right.addTab(self.tbl_queue, _("tab_queue_status") if '_' in globals() else "📋 Queue Status")
        
        # Terminal Log Tab
        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.document().setMaximumBlockCount(1000)
        self.txt_log.setStyleSheet("background: #181825; color: #a6adc8; font-family: Consolas, monospace;")
        self.tab_right.addTab(self.txt_log, _("tab_terminal_log") if '_' in globals() else "💻 Terminal Log")
        
        right_layout.addWidget(self.tab_right)
        
        # Actions
        h_action = QHBoxLayout()
        self.btn_start = QPushButton(_("btn_start_translation"))
        self.btn_start.setToolTip(_("tooltip_start"))
        self.btn_start.setStyleSheet("background: #a6e3a1; color: #1e1e2e; font-size: 16px;")
        self.btn_start.clicked.connect(self.start_translation)
        
        self.btn_stop = QPushButton(_("btn_stop_emergency"))
        self.btn_stop.setToolTip(_("tooltip_stop"))
        self.btn_stop.setStyleSheet("background: #f38ba8; color: #1e1e2e;")
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.stop_translation)
        
        self.btn_deploy_all = QPushButton("Deploy All (Folder)")
        self.btn_deploy_all.setToolTip("Export or deploy all translated files in the output folder")
        self.btn_deploy_all.setStyleSheet("background: #fab387; color: #1e1e2e;")
        self.btn_deploy_all.clicked.connect(self.deploy_all)
        
        h_action.addWidget(self.btn_start)
        h_action.addWidget(self.btn_stop)
        h_action.addWidget(self.btn_deploy_all)
        right_layout.addLayout(h_action)
        
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 700])
        
        self.slider_batch.valueChanged.connect(self.update_preview)
        self.slider_batch.valueChanged.connect(self.update_preview)
        self.spin_delay.valueChanged.connect(self.update_preview)

    def changeEvent(self, event):
        if event.type() == event.Type.ActivationChange and self.isActiveWindow():
            self._reload_profiles_silently()
        super().changeEvent(event)

    def _reload_profiles_silently(self):
        try:
            self.profiles_data = TStudioCore.load_profiles()
            current_text = self.cbo_preset.currentText()
            self.cbo_preset.blockSignals(True)
            self.cbo_preset.clear()
            presets = list(self.profiles_data["presets"].keys())
            self.cbo_preset.addItems(presets)
            
            active = self.profiles_data.get("active_preset", "Default")
            if current_text in presets:
                self.cbo_preset.setCurrentText(current_text)
            elif active in presets:
                self.cbo_preset.setCurrentText(active)
            self.cbo_preset.blockSignals(False)
            
            if hasattr(self, 'cbo_peak_fallback'):
                current_fallback = self.cbo_peak_fallback.currentText()
                self.cbo_peak_fallback.blockSignals(True)
                self.cbo_peak_fallback.clear()
                self.cbo_peak_fallback.addItems(presets)
                if current_fallback in presets:
                    self.cbo_peak_fallback.setCurrentText(current_fallback)
                self.cbo_peak_fallback.blockSignals(False)
        except Exception as e:
            print(f"TRun Silent reload error: {e}")

    def is_translated_preview(self, text):
        import re
        if not text or not isinstance(text, str): return False
        return bool(re.search(r'[฀-๿]', text))

    def on_token_burner_toggled(self, checked):
        if checked:
            self.spin_threads.setValue(10)
            self.slider_batch.setEnabled(False)
            self.spin_batch_val.setEnabled(False)
            self.lbl_preview.setText(_("lbl_token_burner_active") if "_" in globals() else "⚡ Token Burner Mode ACTIVE. Batching disabled. Each row will be sent as an individual API call in parallel. Fast but costs more tokens.")
        else:
            self.spin_threads.setValue(32)
            self.slider_batch.setEnabled(True)
            self.spin_batch_val.setEnabled(True)
            self.update_preview()

    def update_preview(self, *args):
        if hasattr(self, 'chk_token_burner') and self.chk_token_burner.isChecked():
            return
            
        input_file = ""
        if self.tbl_input.rowCount() > 0:
            item = self.tbl_input.item(0, 0)
            if item:
                input_file = item.text()
        batch_size = self.slider_batch.value()
        delay_ms = self.spin_delay.value()
        
        if not input_file:
            self.lbl_preview.setText(_("preview_select_valid") if '_' in globals() else "Please select input file")
            return
            
        import os
        if not os.path.exists(input_file):
            self.lbl_preview.setText(_("preview_not_exist") if '_' in globals() else "File not found")
            return
            
        import csv
        import math
        untranslated = 0
        try:
            with open(input_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                headers = next(reader, None)
                for row in reader:
                    if len(row) > 2:
                        if not self.is_translated_preview(row[2]):
                            untranslated += 1
                    elif len(row) > 1:
                        untranslated += 1
        except Exception:
            self.lbl_preview.setText(_("preview_error_reading"))
            return
            
        batches = math.ceil(untranslated / batch_size) if batch_size > 0 else 0
        # Fix 6: Use observed batch time if available, else fallback to 7s estimate
        avg_api_time = getattr(self, '_avg_batch_time_sec', 7.0)
        total_time_sec = batches * (avg_api_time + (delay_ms / 1000.0))
        m, s = divmod(int(total_time_sec), 60)
        h, m = divmod(m, 60)
        eta_str = f"{h}h {m}m" if h > 0 else f"{m}m {s}s"
        note = "(observed avg)" if hasattr(self, '_avg_batch_time_sec') else "(est. 7s/batch)"
        self.lbl_preview.setText(f"ℹ️ Preview: {untranslated:,} untranslated lines\n📦 Will process in {batches:,} batches\n⏱️ Est. Time: {eta_str} {note}")

    def log(self, text, color="#cdd6f4"):
        html = f'<span style="color:{color};">{text}</span>'
        self._log_queue.append(html)
        if not self._log_timer.isActive():
            self._log_timer.start()

    def _flush_logs(self):
        if not self._log_queue:
            self._log_timer.stop()
            return
        batch = self._log_queue[:]
        self._log_queue.clear()

        cursor = self.txt_log.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        # Using <p style='margin:0; padding:0;'> creates distinct QTextBlocks.
        # This enables Qt's setMaximumBlockCount to discard old blocks in O(1) time
        # and prevents monolithic DOM layout freezes on the Main GUI thread.
        html_chunk = "".join([f"<p style='margin:0; padding:0; line-height:1.2;'>{item}</p>" for item in batch])
        cursor.insertHtml(html_chunk)

        scrollbar = self.txt_log.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        QApplication.processEvents()

    def refresh_profiles_combo(self):
        self.cbo_preset.blockSignals(True)
        self.cbo_preset.clear()
        self.profiles_data = TStudioCore.load_profiles()
        presets = list(self.profiles_data.get("presets", {}).keys())
        self.cbo_preset.addItems(presets)
        active = self.profiles_data.get("active_preset", "Default")
        if active in presets:
            self.cbo_preset.setCurrentText(active)
        self.cbo_preset.blockSignals(False)
        
        if hasattr(self, 'cbo_peak_fallback'):
            current_fallback = self.cbo_peak_fallback.currentText()
            self.cbo_peak_fallback.blockSignals(True)
            self.cbo_peak_fallback.clear()
            self.cbo_peak_fallback.addItems(presets)
            if current_fallback in presets:
                self.cbo_peak_fallback.setCurrentText(current_fallback)
            self.cbo_peak_fallback.blockSignals(False)

    def on_preset_changed(self, text):
        if text:
            self.profiles_data["active_preset"] = text
            TStudioCore.save_profiles(self.profiles_data)
            self.log(f"Profile switched to: {text}")

    def create_new_profile(self):
        from PyQt6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, _("dlg_new_profile_title"), _("dlg_new_profile_label"))
        if ok and name.strip():
            name = name.strip()
            if name not in self.profiles_data["presets"]:
                self.profiles_data["presets"][name] = {"single": "", "opt": "", "glossary": {}}
                self.profiles_data["active_preset"] = name
                TStudioCore.save_profiles(self.profiles_data)
                self.refresh_profiles_combo()
            else:
                self.cbo_preset.setCurrentText(name)

    def remove_selected_input(self):
        rows = sorted(set(item.row() for item in self.tbl_input.selectedItems()), reverse=True)
        for row in rows:
            self.tbl_input.removeRow(row)
            
    def clear_input_list(self):
        self.tbl_input.setRowCount(0)
        
    def find_project_root(self, file_path):
        import os
        current_dir = os.path.dirname(os.path.abspath(file_path))
        while current_dir and current_dir != os.path.dirname(current_dir):
            if os.path.exists(os.path.join(current_dir, "thub_project.json")) or os.path.exists(os.path.join(current_dir, ".thub")):
                return current_dir
            current_dir = os.path.dirname(current_dir)
        return None

    def add_to_list_unique(self, path):
        for i in range(self.tbl_input.rowCount()):
            item = self.tbl_input.item(i, 0)
            if item and item.text() == path:
                return
        row = self.tbl_input.rowCount()
        self.tbl_input.insertRow(row)
        item_path = QTableWidgetItem(path)
        item_path.setFlags(item_path.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.tbl_input.setItem(row, 0, item_path)
        
        project_root = self.find_project_root(path)
        combo_profile = QComboBox()
        
        if project_root:
            from tstudio_core import TStudioCore
            orig_proj = getattr(TStudioCore, '_PROJECT_PATH', None)
            TStudioCore.set_project_path(project_root)
            proj_profiles = TStudioCore.load_profiles()
            presets = list(proj_profiles.get("presets", {}).keys())
            active = proj_profiles.get("active_preset", "Default")
            if orig_proj:
                TStudioCore.set_project_path(orig_proj)
            else:
                TStudioCore._PROJECT_PATH = None
                
            combo_profile.addItems(presets)
            if active in presets:
                combo_profile.setCurrentText(active)
        else:
            combo_profile.addItems([self.cbo_preset.itemText(i) for i in range(self.cbo_preset.count())])
            combo_profile.setCurrentText(self.cbo_preset.currentText())
            
        self.tbl_input.setCellWidget(row, 1, combo_profile)

    def rename_profile(self):
        from PyQt6.QtWidgets import QInputDialog
        active = self.cbo_preset.currentText()
        if active == "Default":
            QMessageBox.warning(self, "Warning", _("warn_cannot_rename_default"))
            return
            
        new_name, ok = QInputDialog.getText(self, _("dlg_rename_profile_title"), f"Enter new name for '{active}':", text=active)
        if ok and new_name.strip():
            new_name = new_name.strip()
            if new_name == active: return
            if new_name in self.profiles_data["presets"]:
                QMessageBox.warning(self, "Warning", _("warn_profile_exists"))
                return
                
            self.profiles_data["presets"][new_name] = self.profiles_data["presets"].pop(active)
            self.profiles_data["active_preset"] = new_name
            TStudioCore.save_profiles(self.profiles_data)
            self.refresh_profiles_combo()
            self.log(f"Profile renamed to '{new_name}'.")

    def delete_profile(self):
        active = self.cbo_preset.currentText()
        if active == "Default":
            QMessageBox.warning(self, "Warning", _("warn_cannot_delete_default"))
            return
            
        reply = QMessageBox.question(self, _("confirm_delete_title"), _("confirm_delete_msg"),
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            del self.profiles_data["presets"][active]
            self.profiles_data["active_preset"] = "Default"
            TStudioCore.save_profiles(self.profiles_data)
            self.refresh_profiles_combo()
            self.log(f"Profile '{active}' deleted.")

    def open_settings(self):
        dlg = SettingsDialog(self)
        dlg.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        if dlg.exec():
            pass

    def open_prompts(self):
        dlg = PromptSettingsDialog(self)
        dlg.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        if dlg.exec():
            self.refresh_profiles_combo()

    def open_glossary(self):
        from PyQt6.QtWidgets import QDialog, QVBoxLayout
        dlg = QDialog(self)
        dlg.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        dlg.setWindowTitle("Glossary")
        layout = QVBoxLayout(dlg)
        widget = GlossaryWidget(dlg)
        layout.addWidget(widget)
        dlg.resize(600, 400)
        if dlg.exec():
            self.refresh_profiles_combo()
            
    def browse_input(self):
        from tstudio_core import TStudioCore
        target_dir = TStudioCore.get_translation_workspace_dir(
            hint_path=getattr(self, 'project_path', None),
            profile_name=getattr(self, 'current_profile_name', None) or (self.cbo_profile.currentText() if hasattr(self, 'cbo_profile') else None)
        )
        paths, _ext = QFileDialog.getOpenFileNames(self, _("Select Input CSV"), target_dir, "Supported Files (*.csv *.bundle *.txt *.pak *.*);;CSV Files (*.csv);;Unity Bundles (*.bundle *.txt *.*);;PAK Files (*.pak);;All Files (*.*)")
        if paths:
            for path in paths:
                def do_work(p=path):
                    try:
                        if p.lower().endswith('.pak'):
                            from tstudio_core import TPakManager, TStudioCore
                            csv_out = TPakManager.extract_pak_to_csv(p)
                            if csv_out:
                                cfg = TStudioCore.load_config()
                                cfg["origin_file"] = p
                                TStudioCore.save_config(cfg)
                                return csv_out
                    except Exception as e:
                        print(f"PAK extract error: {e}")
                    try:
                        from tbundle_manager import TBundleManager
                        if TBundleManager.is_unity_bundle(p):
                            csv_out = TBundleManager.extract_text_to_csv(p)
                            if csv_out:
                                return csv_out
                    except Exception as e:
                        print(f"Bundle extract error: {e}")
                    return p

                def on_result(result_path):
                    self._process_input_path_ui(result_path)

                from tstudio_ui_shared import ApiWorker
                from PyQt6.QtCore import QThreadPool
                worker = ApiWorker(do_work)
                worker.signals.finished.connect(on_result)
                self._workers.append(worker)  # Prevent GC before thread executes
                QThreadPool.globalInstance().start(worker)

    def browse_input_folder(self):
        from tstudio_core import TStudioCore
        target_dir = TStudioCore.get_translation_workspace_dir(
            hint_path=getattr(self, 'project_path', None),
            profile_name=getattr(self, 'current_profile_name', None) or (self.cbo_profile.currentText() if hasattr(self, 'cbo_profile') else None)
        )
        folder = QFileDialog.getExistingDirectory(self, "Select Input Folder (Contains CSVs)", target_dir)
        if folder:
            import glob, os
            csv_files = glob.glob(os.path.join(folder, "*.csv"))
            if not csv_files:
                self.log(f"No CSV files found in {folder}", "#f38ba8")
                return
                
            from tstudio_core import TFormatManager
            from tstudio_ui_shared import SmartImportDialog
            from PyQt6.QtWidgets import QDialog, QMessageBox
            
            # Check first file
            first_file = csv_files[0]
            if not TFormatManager.is_standard_csv(first_file):
                self.log("Non-standard CSV detected. Prompting for format mapping...", "#f9e2af")
                headers = TFormatManager.get_headers(first_file)
                dlg = SmartImportDialog(headers, self)
                if dlg.exec() == QDialog.DialogCode.Accepted:
                    mapping = dlg.get_mapping()
                    formatted_folder = folder + "_formatted"
                    os.makedirs(formatted_folder, exist_ok=True)
                    
                    self.log("Applying standard format to all files in folder...", "#89b4fa")
                    new_csv_files = []
                    for f in csv_files:
                        out_path = os.path.join(formatted_folder, os.path.basename(f))
                        try:
                            TFormatManager.format_to_standard(f, mapping, output_path=out_path)
                            new_csv_files.append(out_path)
                        except Exception as e:
                            self.log(f"Failed to format {os.path.basename(f)}: {e}", "#f38ba8")
                        QApplication.processEvents()  # Keep UI responsive during format loop
                    csv_files = new_csv_files
                    self.log(f"Formatted {len(csv_files)} files successfully.", "#a6e3a1")
                else:
                    self.log("Batch Smart Import cancelled. Adding original files (may fail).", "#f38ba8")
            
            for f in csv_files:
                self.add_to_list_unique(f)
                
            self.log(f"Added {len(csv_files)} CSV files from folder: {folder}", "#a6e3a1")

    def _process_input_path_ui(self, path):
        from tstudio_core import TFormatManager
        if not TFormatManager.is_standard_csv(path):
            headers = TFormatManager.get_headers(path)
            from tstudio_ui_shared import SmartImportDialog
            dlg = SmartImportDialog(headers, self)
            from PyQt6.QtWidgets import QDialog, QMessageBox
            if dlg.exec() == QDialog.DialogCode.Accepted:
                mapping = dlg.get_mapping()
                try:
                    path = TFormatManager.format_to_standard(path, mapping)
                    QMessageBox.information(self, _("tformat_title"), "File has been formatted to standard.")
                except Exception as e:
                    QMessageBox.critical(self, _("warn_select_io_title"), f"Failed to format: {e}")
                    return
            else:
                return

        self.add_to_list_unique(path)

    def toggle_risk(self, checked):
        if checked:
            reply = QMessageBox.warning(self, _("warn_risk_mode_title"), 
                _("warn_risk_mode_msg"), 
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.slider_batch.setRange(1, 500)
                self.spin_batch_val.setRange(1, 500)
            else:
                self.chk_unlock.setChecked(False)
        else:
            self.slider_batch.setRange(1, 100)
            self.spin_batch_val.setRange(1, 100)
            if self.slider_batch.value() > 100:
                self.slider_batch.setValue(100)

    def export_original(self):
        self.deploy_all()

    def deploy_all(self):
        import os
        deploy_list = []
        for i in range(self.tbl_input.rowCount()):
            item = self.tbl_input.item(i, 0)
            if item:
                in_file = item.text()
                out_file = in_file.replace(".csv", "_translated.csv")
                deploy_list.append((in_file, out_file))
                
        if not deploy_list:
            QMessageBox.warning(self, "No Queue", "No files found to deploy. Please add files to the input list.")
            return
            
        self.log(f"Starting Batch Deploy for {len(deploy_list)} files...", "#fab387")
        from tstudio_core import TFormatManager
        from tbundle_manager import TBundleManager

        success_count = 0
        fail_count = 0
        
        for in_file, out_file in deploy_list:
            if not os.path.exists(out_file):
                continue
            
            try:
                stem = os.path.splitext(os.path.basename(out_file))[0]
                base_dir = os.path.dirname(in_file)
                
                real_stem = stem.replace("_translated", "")
                json_path = os.path.join(base_dir, f'{real_stem}_meta.json')
                pak_path = os.path.join(base_dir, f'{real_stem}.pak')

                # Check PAK deployment first
                from tstudio_core import TPakManager
                if os.path.exists(pak_path):
                    try:
                        TPakManager.reconstruct_pak_file(pak_path, out_file, pak_path)
                        success_count += 1
                        self.log(f"Successfully deployed to PAK file at: {pak_path}", "#a6e3a1")
                        continue
                    except Exception as e:
                        fail_count += 1
                        self.log(f"Failed to deploy PAK file: {e}", "#f38ba8")
                        continue

                # Check Bundle first
                if os.path.exists(json_path):
                    success, msg = TBundleManager.deploy_csv_to_bundle(out_file, original_meta_path=json_path)
                    if success:
                        success_count += 1
                    else:
                        fail_count += 1
                        self.log(f"Failed bundle deploy {os.path.basename(out_file)}: {msg}", "#f38ba8")
                    continue
                    
                # Fallback to normal export_original
                success, msg = TFormatManager.export_original(out_file, original_meta_path=json_path if os.path.exists(json_path) else None)
                if success:
                    success_count += 1
                else:
                    fail_count += 1
                    self.log(f"Failed format deploy {os.path.basename(out_file)}: {msg}", "#f38ba8")

            except Exception as deploy_err:
                fail_count += 1
                self.log(f"Error deploying {os.path.basename(out_file)}: {deploy_err}", "#f38ba8")
                
            QApplication.processEvents()
                
        self.log(f"Batch Deploy Finished. Success: {success_count}, Failed: {fail_count}", "#a6e3a1")
        QMessageBox.information(self, "Deploy Complete", f"Batch Deploy finished.\nSuccess: {success_count}\nFailed: {fail_count}")

    def start_translation(self):
        try:
            self._start_translation_impl()
        except Exception as e:
            import traceback
            with open('GUI_CRASH_LOG.txt', 'w') as f:
                f.write(traceback.format_exc())
            raise
    
    def _start_translation_impl(self):
        if self.tbl_input.rowCount() == 0:
            QMessageBox.warning(self, _("warn_select_io_title") if '_' in globals() else "Warning", _("warn_select_io_msg") if '_' in globals() else "Please add files or folders to translate.")
            return

        if self.is_running:
            return
            
        import os
        self.queue = []
        for i in range(self.tbl_input.rowCount()):
            item = self.tbl_input.item(i, 0)
            if not item:
                continue
            in_file = item.text()
            out_file = in_file.replace(".csv", "_translated.csv")
            combo = self.tbl_input.cellWidget(i, 1)
            profile_name = combo.currentText() if combo else self.cbo_preset.currentText()
            project_root = self.find_project_root(in_file)
            self.queue.append((in_file, out_file, profile_name, project_root))
            
        self.tbl_queue.setRowCount(0)
        from PyQt6.QtWidgets import QTableWidgetItem
        from PyQt6.QtCore import Qt
        for i, (in_file, out_file, _, _) in enumerate(self.queue):
            self.tbl_queue.insertRow(i)
            item_name = QTableWidgetItem(os.path.basename(in_file))
            item_status = QTableWidgetItem("Pending ⏳")
            item_status.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tbl_queue.setItem(i, 0, item_name)
            self.tbl_queue.setItem(i, 1, item_status)

        self.log(f"Batch Translation Engine starting with {len(self.queue)} files in queue...", "#89b4fa")
        self.is_running = True
        
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.cbo_preset.setEnabled(False)
        if hasattr(self, 'chk_schedule') and self.chk_schedule.isChecked():
            target_time = self.time_schedule.time()
            current_time = QTime.currentTime()
            msecs = current_time.msecsTo(target_time)
            if msecs < 0:
                msecs += 86400000 # Add 24 hours if target time is tomorrow
            
            self.log(f"Scheduled to start at {target_time.toString('HH:mm')} (in {msecs // 60000} minutes)...", "#f9e2af")
            for filename, _, _, _ in self.queue:
                self._set_queue_status(os.path.basename(filename), "Waiting for Schedule ⏳")
            
            self.schedule_timer = QTimer(self)
            self.schedule_timer.setSingleShot(True)
            self.schedule_timer.timeout.connect(self._do_start_translation)
            self.schedule_timer.start(msecs)
            return

        self._do_start_translation()
        
    def _do_start_translation(self):
        try:
            self._run_next_in_queue()
        except Exception as e:
            import traceback
            with open('crash_log.txt', 'w') as f:
                f.write(traceback.format_exc())
        
    def _set_queue_status(self, filename, status):
        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QBrush, QColor
        for row in range(self.tbl_queue.rowCount()):
            item = self.tbl_queue.item(row, 0)
            if item and item.text() == filename:
                status_item = self.tbl_queue.item(row, 1)
                if status_item:
                    status_item.setText(status)
                    if "✅" in status:
                        status_item.setForeground(QBrush(QColor("#a6e3a1")))
                    elif "❌" in status:
                        status_item.setForeground(QBrush(QColor("#f38ba8")))
                    elif "🔄" in status:
                        status_item.setForeground(QBrush(QColor("#f9e2af")))
                # Scroll to row
                self.tbl_queue.scrollToItem(item)
                break

    def _run_next_in_queue(self):
        try:
            self._run_next_in_queue_impl()
        except Exception as e:
            import traceback
            with open('GUI_CRASH_LOG.txt', 'a') as f:
                f.write('CRASH IN _run_next_in_queue\n')
                f.write(traceback.format_exc())
            self.log(f'[Fatal Error] Worker failed to initialize: {e}', '#f38ba8')
            self.is_running = False
            self.btn_start.setEnabled(True)
            self.btn_stop.setEnabled(False)
            
    def _run_next_in_queue_impl(self):
        if not self.queue:
            self.on_all_queue_finished()
            return
            
        if not self.is_running:
            self.log("Batch queue stopped.", "#f38ba8")
            return
            
        self.current_in_file, self.current_out_file, profile_name, project_root = self.queue.pop(0)
        base_name = os.path.basename(self.current_in_file)
        self.log(f"Processing: {base_name} (Profile: {profile_name})...", "#cba6f7")
        self._set_queue_status(base_name, "Translating 🔄")
        
        import time
        self.current_job_start_time = time.time()
        
        self.progress_bar.setValue(0)
        self.batch_progress_bar.setValue(0)
        self.lbl_batch_progress.setText(_("lbl_batch_progress_default"))
        if hasattr(self, 'lbl_eta'):
            self.lbl_eta.setText("ETA: Calculating...")
        
        from tstudio_core import TStudioCore
        cfg = TStudioCore.load_config()
        if project_root:
            TStudioCore.set_project_path(project_root)
        profiles_data = TStudioCore.load_profiles()
        presets = profiles_data.get("presets", {})
        if profile_name in presets:
            profile = presets[profile_name]
        else:
            profile = presets.get("Default", {})
        
        peak_config = None
        if hasattr(self, 'chk_peak') and self.chk_peak.isChecked():
            peak_config = {
                'start_time': self.time_peak_start.time(),
                'end_time': self.time_peak_end.time(),
                'action': self.cbo_peak_action.currentIndex(),
                'fallback_profile': self.cbo_peak_fallback.currentText()
            }
            
        self.worker = TRunWorker(
            route_config=self.translation_channel.route(),
            config=cfg,
            profile=profile,
            input_csv=self.current_in_file,
            output_csv=self.current_out_file,
            batch_size=self.slider_batch.value(),
            delay_ms=self.spin_delay.value(),
            max_retries=self.spin_retry.value(),
            use_mask=self.chk_mask.isChecked(),
            use_glossary=self.chk_glossary.isChecked(),
            use_pua=self.chk_pua.isChecked(),
            peak_config=peak_config,
            threads=self.spin_threads.value() if hasattr(self, 'spin_threads') else 1,
            token_burner=self.chk_token_burner.isChecked() if hasattr(self, 'chk_token_burner') else False,
            use_cjk_filter=self.chk_cjk_filter.isChecked() if hasattr(self, 'chk_cjk_filter') else True,
            use_eng_filter=self.chk_eng_filter.isChecked() if hasattr(self, 'chk_eng_filter') else True,
            auto_filter_engine=self.chk_engine_filter.isChecked() if hasattr(self, 'chk_engine_filter') else True,
            use_dedup=self.chk_dedup.isChecked() if hasattr(self, 'chk_dedup') else True
        )
        
        # Prevent QObject destruction race condition when QRunnable finishes
        self.worker.signals.setParent(self)

        self.worker.signals.log.connect(self.log)
        self.worker.signals.progress.connect(self.update_progress)
        self.worker.signals.batch_progress.connect(self.update_batch_progress)
        self.worker.signals.finished.connect(self.on_file_finished)
        self.worker.signals.stopped.connect(self.on_worker_stopped)  # user-stop → reset UI only
        self.worker.signals.error.connect(self.on_error)

        self.threadpool.start(self.worker)
        
    def update_batch_progress(self, current, total):
        if total > 0:
            pct = int((current / total) * 100)
            self.batch_progress_bar.setValue(pct)
            self.lbl_batch_progress.setText(f"Batch: {current} / {total} ({pct}%)")
            # Fix 6: Track observed average time per batch for adaptive ETA preview
            import time as _time
            if hasattr(self, 'current_job_start_time') and current > 1:
                elapsed = _time.time() - self.current_job_start_time
                self._avg_batch_time_sec = elapsed / (current - 1)  # per batch
            
    def update_progress(self, current, total):
        if total > 0:
            pct = int((current / total) * 100)
            self.progress_bar.setValue(pct)
            self.lbl_progress.setText(f"Lines: {current} / {total} ({pct}%)")
            
            # ETA Calculation (throttled to at most every 200ms)
            import time
            now = time.time()
            if not hasattr(self, '_last_eta_update') or (now - self._last_eta_update >= 0.2):
                self._last_eta_update = now
                if hasattr(self, 'current_job_start_time') and current > 0:
                    elapsed = now - self.current_job_start_time
                    lines_per_sec = current / elapsed if elapsed > 0 else 0
                    if lines_per_sec > 0:
                        remaining_lines = total - current
                        eta_sec = remaining_lines / lines_per_sec
                        m, s = divmod(int(eta_sec), 60)
                        h, m = divmod(m, 60)
                        eta_str = f"{h}h {m}m {s}s" if h > 0 else f"{m}m {s}s"
                        self.lbl_eta.setText(f"ETA: {eta_str}")
                    else:
                        self.lbl_eta.setText("ETA: Calculating...")
            
    def on_file_finished(self):
        self._flush_logs()
        base_name = os.path.basename(self.current_in_file)
        self.log(f"Finished processing: {base_name}", "#a6e3a1")
        self._set_queue_status(base_name, "Completed ✅")
        if self.is_running:
            self._run_next_in_queue()

    def on_worker_stopped(self):
        """Called when user pressed Stop — resets UI without starting next file."""
        self._flush_logs()
        self.is_running = False
        self.queue = []  # Cancel remaining queue
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.cbo_preset.setEnabled(True)
        if hasattr(self, 'current_in_file'):
            base_name = os.path.basename(self.current_in_file)
            self._set_queue_status(base_name, "Stopped ⏹")
            # Mark remaining queued files as cancelled
        for row in range(self.tbl_queue.rowCount()):
            item = self.tbl_queue.item(row, 1)
            if item and item.text().startswith("Pending"):
                item.setText("Cancelled ❌")
        self.log("Translation stopped by user. Progress saved.", "#f9e2af")
            
    def on_all_queue_finished(self):
        self.is_running = False
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.cbo_preset.setEnabled(True)
        self.log("All files in queue completed successfully!", "#a6e3a1")
        
        if hasattr(self, 'chk_auto_shutdown') and self.chk_auto_shutdown.isChecked():
            self.trigger_shutdown()
        else:
            QMessageBox.information(self, "Done", "All translations completed successfully!")
            
    def trigger_shutdown(self):
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
        from PyQt6.QtCore import QTimer
        import os
        
        dlg = QDialog(self)
        dlg.setWindowTitle("Auto Shutdown")
        dlg.setFixedSize(350, 150)
        
        layout = QVBoxLayout(dlg)
        
        self.shutdown_time_left = 60
        lbl = QLabel(f"All translations finished.\nComputer will shutdown in {self.shutdown_time_left} seconds...")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("font-size: 14px; color: #f38ba8; font-weight: bold;")
        layout.addWidget(lbl)
        
        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton("Cancel Shutdown")
        btn_cancel.setStyleSheet("background: #45475a;")
        btn_cancel.clicked.connect(dlg.reject)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)
        
        timer = QTimer(dlg)
        
        def update_timer():
            self.shutdown_time_left -= 1
            if self.shutdown_time_left <= 0:
                timer.stop()
                dlg.accept()
                os.system("shutdown /s /t 0")
            else:
                lbl.setText(f"All translations finished.\nComputer will shutdown in {self.shutdown_time_left} seconds...")
                
        timer.timeout.connect(update_timer)
        timer.start(1000)
        
        if dlg.exec() == QDialog.DialogCode.Rejected:
            timer.stop()
            self.log("Auto Shutdown cancelled by user.", "#f9e2af")
            QMessageBox.information(self, "Done", "All translations completed successfully!\n(Auto Shutdown Cancelled)")
        
    def on_finished(self):
        pass # Replaced by on_file_finished / on_all_queue_finished

    def on_error(self, err):
        self._flush_logs()
        self.is_running = False
        if hasattr(self, 'current_in_file'):
            self._set_queue_status(os.path.basename(self.current_in_file), "Failed ❌")
        self.queue = []  # Clear queue on error
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.cbo_preset.setEnabled(True)  # Re-enable preset combo that was disabled on start

    def stop_translation(self):
        if hasattr(self, 'schedule_timer') and self.schedule_timer.isActive():
            self.schedule_timer.stop()
            self.log("Scheduled translation cancelled.", "#f38ba8")
            self.is_running = False
            self.btn_start.setEnabled(True)
            self.btn_stop.setEnabled(False)
            self.cbo_preset.setEnabled(True)
            for filename, _, _, _ in self.queue:
                self._set_queue_status(os.path.basename(filename), "Cancelled ❌")
            return
            
        if not hasattr(self, 'worker') or not self.is_running:
            return
            
        self.log(_("log_stop_requested") if '_' in globals() else "Stopping translation...", "#f38ba8")
        self.worker.stop()

    def closeEvent(self, event):
        if self.is_running:
            if hasattr(self, 'worker'):
                self.worker.stop()
            self.threadpool.waitForDone(3000)
        event.accept()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("project", nargs="?", type=str, help="Path to THub project", default=None)
    parser.add_argument("--standalone", action="store_true", help="Run standalone legacy TRun window")
    args, unknown = parser.parse_known_args()
    
    TStudioCore.set_project_path(args.project)
    
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('flagship.trun.batch.1.0')
        except Exception:
            pass

    app = QApplication(sys.argv)
    trun_ico = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "assets", "TRun.ico"))
    if not os.path.exists(trun_ico):
        trun_ico = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "assets", "TRun.png"))
    if os.path.exists(trun_ico):
        app.setWindowIcon(QIcon(trun_ico))

    if args.standalone:
        window = TRunApp(project_path=args.project)
    else:
        try:
            from tstudio_app import TranslationStudio
            window = TranslationStudio(project_path=args.project, default_mode="trun")
        except Exception as e:
            print(f"Failed to launch unified TStudio in TRun mode: {e}")
            window = TRunApp(project_path=args.project)
            
    window.show()
    sys.exit(app.exec())

