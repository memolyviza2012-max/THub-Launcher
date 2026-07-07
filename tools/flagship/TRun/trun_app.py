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


class TRunWorkerSignals(QObject):
    progress = pyqtSignal(int, int)       # current, total
    batch_progress = pyqtSignal(int, int) # current_batch, total_batches
    log = pyqtSignal(str, str)            # text, color
    finished = pyqtSignal()               # completed normally
    stopped = pyqtSignal()                # user-requested stop
    error = pyqtSignal(str)               # fatal error

class TRunWorker(QRunnable):
    def __init__(self, config, profile, input_csv, output_csv, batch_size, delay_ms, max_retries, use_mask, use_glossary, use_pua, peak_config=None):
        super().__init__()
        self.signals = TRunWorkerSignals()
        self.config = config
        self.profile = profile
        self.input_csv = input_csv
        self.output_csv = output_csv
        self.batch_size = batch_size
        self.delay_ms = delay_ms
        self.max_retries = max_retries
        self.use_mask = use_mask
        self.use_glossary = use_glossary
        self.use_pua = use_pua
        self.peak_config = peak_config
        self._is_killed = False

    # Pre-compiled regex patterns at class level to avoid re-compiling on every call
    _RE_THAI = _re_module.compile(r'[\u0E00-\u0E7F]')
    _RE_TAG = _re_module.compile(r'(<[^>]+>|\\n|\\r|\n|\r|%[sdiefg]|\{\d+\}|\[\[[^\]]+\]\])')
    _RE_TSV_LINE = _re_module.compile(r'^"?([^"\t]+)"?\t(.*)')
    _RE_CODE_FENCE_START = _re_module.compile(r'^```[^\n]*\n?', _re_module.MULTILINE)
    _RE_CODE_FENCE_END = _re_module.compile(r'\n?```$', _re_module.MULTILINE)

    def is_translated(self, text):
        if not text or not isinstance(text, str): return False
        return bool(self._RE_THAI.search(text))

    def mask_tags(self, text):
        tags = self._RE_TAG.findall(text)
        masked_text = text
        placeholders = {}
        for idx, tag in enumerate(tags):
            placeholder = f"[TAG_{idx}]"
            if placeholder not in placeholders:
                placeholders[placeholder] = tag
            masked_text = masked_text.replace(tag, placeholder, 1)
        return masked_text, placeholders

    def unmask_tags(self, translated_text, placeholders):
        unmasked = translated_text
        for placeholder, original_tag in placeholders.items():
            unmasked = unmasked.replace(placeholder, original_tag)
        return unmasked

    def enforce_glossary(self, text):
        # Fix 3: Use word boundary to avoid replacing substrings
        glossary = self.profile.get("glossary", {})
        for wrong_word, correct_word in glossary.items():
            if isinstance(correct_word, list):
                correct_word = correct_word[0]
            try:
                text = _re_module.sub(r'\b' + _re_module.escape(str(wrong_word)) + r'\b',
                                      str(correct_word), text)
            except _re_module.error:
                text = text.replace(str(wrong_word), str(correct_word))
        return text

    def enforce_arabic_numerals(self, text):
        import unicodedata
        res = []
        for c in text:
            if c.isdecimal():
                res.append(str(unicodedata.decimal(c)))
            else:
                res.append(c)
        return "".join(res)

    def _inject_glossary_to_prompt(self, prompt, source_text_batch):
        # Fix 1: Fallback injection — works even if [GLOSSARY TO USE] is absent from prompt
        glossary = self.profile.get("glossary", {})
        if not glossary:
            return prompt.replace("[GLOSSARY TO USE]", "") if "[GLOSSARY TO USE]" in prompt else prompt

        matched_terms = []
        source_lower = source_text_batch.lower()

        for eng, val in glossary.items():
            eng_str = eng.strip()
            if not eng_str: continue
            if _re_module.search(r'\b' + _re_module.escape(eng_str.lower()) + r'\b', source_lower):
                if isinstance(val, list):
                    term_info = f"- {eng_str} = {val[0]}"
                    if len(val) > 1 and val[1]:
                        term_info += f" ({val[1]})"
                    matched_terms.append(term_info)
                else:
                    matched_terms.append(f"- {eng_str} = {val}")

        glossary_section = ""
        if matched_terms:
            glossary_section = "GLOSSARY FOR THIS BATCH:\n" + "\n".join(matched_terms)

        if "[GLOSSARY TO USE]" in prompt:
            return prompt.replace("[GLOSSARY TO USE]", glossary_section)
        else:
            # Fallback: append glossary section even when placeholder is missing
            if glossary_section:
                return prompt + "\n\n" + glossary_section
            return prompt

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
        import csv, time, re, os
        self.signals.log.emit(_("log_loading_csv"), "#89b4fa")
        rows = []
        headers = []
        try:
            with open(self.input_csv, 'r', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                headers = next(reader)
                rows = list(reader)
                
            # --- Smart Resume Logic ---
            if os.path.exists(self.output_csv):
                self.signals.log.emit("Found existing output file. Restoring previous translations...", "#f9e2af")
                try:
                    with open(self.output_csv, 'r', encoding='utf-8-sig') as f_out:
                        reader_out = csv.reader(f_out)
                        next(reader_out, None) # skip headers
                        out_dict = {}
                        for r in reader_out:
                            if len(r) > 2 and self.is_translated(r[2]):
                                out_dict[r[0]] = r[2]
                                
                    restored = 0
                    for row in rows:
                        if len(row) > 0 and row[0] in out_dict:
                            while len(row) <= 2:
                                row.append("")
                            row[2] = out_dict[row[0]]
                            restored += 1
                    
                    if restored > 0:
                        self.signals.log.emit(f"Successfully restored {restored} translated rows! Continuing from where it left off...", "#a6e3a1")
                except Exception as resume_err:
                    self.signals.log.emit(f"Could not read previous output file for resume: {resume_err}", "#f38ba8")
                    self.signals.error.emit(f"Failed to resume from existing output: {resume_err}")
                    return
            # --------------------------
            
        except Exception as e:
            self.signals.error.emit(f"Failed to read CSV: {e}")
            return

        total_rows = len(rows)
        self.signals.log.emit(_("log_found_rows"), "#a6e3a1")
        
        # Determine columns
        col_id = 0
        col_source = 1
        col_trans = 2
        
        # Filter untranslated
        untranslated = []
        for i, row in enumerate(rows):
            if len(row) > col_trans:
                if not self.is_translated(row[col_trans]):
                    untranslated.append((i, row))
            elif len(row) > col_source:
                row.append("")
                untranslated.append((i, row))
                
        self.signals.log.emit(f"Found {len(untranslated)} untranslated rows.", "#f9e2af")
        
        system_prompt = self.profile.get("batch", "")
        # Replace {source_text} with rules in batch mode if the user didn't modify it properly
        if "{source_text}" in system_prompt:
            system_prompt = system_prompt.replace("{source_text}", "the user prompt text")

        # Optimized FORMAT RULE — concise but effective (~87 tokens instead of ~171)
        system_prompt += (
            "\n\nFORMAT: Reply ONLY as tab-separated lines, no headers/explanation/markdown.\n"
            "Each line: ORIGINAL_ID[TAB]THAI_TRANSLATION\n"
            "Copy ORIGINAL_ID exactly (same case, punctuation, {M}/{F} suffix). "
            "Preserve [TAG_N] placeholders. Use real tab, not spaces.\n"
            "Example: #Grenadier{M}\tมือระเบิด{ชาย}"
        )
        
        batches = [untranslated[i:i + self.batch_size] for i in range(0, len(untranslated), self.batch_size)]
        total_batches = len(batches)
        
        processed_count = 0
        total_untrans = len(untranslated)
        
        is_local = (self.config.get("provider", "") == "Local LLM" or self.config.get("model", "") == "custom-local-llm")
        
        tpua = None
        if self.use_pua:
            self.signals.log.emit(_("log_init_tpua"), "#f9e2af")
            tpua = TPUAEngine()
        
        for batch_idx, batch in enumerate(batches):
            self.signals.batch_progress.emit(batch_idx + 1, total_batches)
            
            self._check_peak_hour()
            
            if self._is_killed:
                self.signals.log.emit(_("log_emergency_stop") if '_' in globals() else "Emergency Stop", "#f38ba8")
                break
                
            self.signals.log.emit(f"Processing Batch {batch_idx+1}/{len(batches)} ({len(batch)} items)...", "#89b4fa")
            
            # Build lines — use simple tab-only format (no outer quotes)
            # This avoids breaking when game_id or source contains " characters
            batch_tasks = []
            lines_to_send = []
            row_snippets = {}  # store snippets for post-result logging
            for i, row in batch:
                game_id = row[col_id]
                source_text = row[col_source]
                
                snippet = source_text[:40].replace("\\n", " ") + ("..." if len(source_text) > 40 else "")
                row_snippets[game_id] = snippet
                
                if self.use_mask:
                    masked, placeholders = self.mask_tags(source_text)
                else:
                    masked, placeholders = source_text, {}
                    
                batch_tasks.append((i, game_id, placeholders))
                # No outer quotes — avoids conflicts with content that has " chars
                lines_to_send.append(f'{game_id}\t{masked}')
                
            if not lines_to_send:
                # Entire batch was resolved by TM, skip AI call
                continue
                
            combined_source = " ".join([row[col_source] for i, row in batch])
            batch_system_prompt = self._inject_glossary_to_prompt(system_prompt, combined_source)
            
            user_prompt = "Translate these entries:\n" + "\n".join(lines_to_send)
            full_prompt = batch_system_prompt + "\n\n" + user_prompt
            
            # API Call
            success = False
            for attempt in range(1, self.max_retries + 1):
                if self._is_killed: break
                try:
                    self.signals.log.emit(f"  Attempt {attempt}/{self.max_retries}...", "#a6adc8")
                    reply = CoreAI.generate_content(self.config, full_prompt, is_local=is_local)
                    
                    # Parse TSV reply — strip markdown fences
                    reply = self._RE_CODE_FENCE_START.sub('', reply.strip())
                    reply = self._RE_CODE_FENCE_END.sub('', reply)

                    results = {}
                    current_id = None
                    valid_ids = {game_id for _, game_id, _ in batch_tasks}
                    # Case-insensitive fallback: maps lowercased ID → original ID
                    # Handles AI returning {m} instead of {M}, etc.
                    valid_ids_ci = {gid.lower(): gid for _, gid, _ in batch_tasks}

                    for line in reply.split('\n'):
                        stripped = line.strip()
                        if not stripped:
                            continue  # skip blank lines entirely

                        if '\t' in stripped:
                            # Split on first tab — robust to IDs with quotes or special chars
                            tab_pos = stripped.index('\t')
                            candidate_id = stripped[:tab_pos].strip()
                            candidate_id = self._strip_outer_quotes(candidate_id)
                            
                            candidate_val = stripped[tab_pos + 1:].strip()
                            candidate_val = self._strip_outer_quotes(candidate_val)
                                
                            # 1) Exact match
                            if candidate_id in valid_ids:
                                current_id = candidate_id
                                results[current_id] = candidate_val
                            # 2) Case-insensitive fallback (AI changed {M}->{m} etc.)
                            elif candidate_id.lower() in valid_ids_ci:
                                current_id = valid_ids_ci[candidate_id.lower()]
                                results[current_id] = candidate_val
                            else:
                                # 3) Robust alphanumeric prefix match (AI stripped punctuation like # or truncated long text)
                                norm_candidate = self._normalize_id(candidate_id)
                                matching_ids = []
                                if len(norm_candidate) >= 3:
                                    matching_ids = [gid for gid in valid_ids if self._normalize_id(gid).startswith(norm_candidate)]
                                    
                                if len(matching_ids) == 1:
                                    current_id = matching_ids[0]
                                    results[current_id] = candidate_val
                                elif current_id is not None:
                                    # Line has tab but unknown ID: treat as continuation
                                    results[current_id] += '\n' + self._strip_outer_quotes(stripped)
                        elif current_id is not None:
                            # No tab — continuation of previous multi-line entry
                            results[current_id] += '\n' + self._strip_outer_quotes(stripped)
                        
                    # Apply results
                    remaining_tasks = []
                    remaining_lines = []
                    for idx_zip, (i, game_id, placeholders) in enumerate(batch_tasks):
                        if game_id in results:
                            translated = results[game_id]
                            # Bug A Fix: Convert literal \n escape sequences to real newlines
                            translated = translated.replace('\\n', '\n')
                            if self.use_mask:
                                translated = self.unmask_tags(translated, placeholders)
                            if self.use_glossary:
                                translated = self.enforce_glossary(translated)
                            # Always enforce Arabic numerals for all languages
                            translated = self.enforce_arabic_numerals(translated)
                            if self.use_pua and tpua:
                                translated = tpua.encode(translated)
                            rows[i][col_trans] = translated
                            processed_count += 1

                            # Fix 4: Log after result (with source snippet for context)
                            src_snip = row_snippets.get(game_id, game_id)
                            tsnippet = translated[:40].replace('\n', ' ') + ("..." if len(translated) > 40 else "")
                            self.signals.log.emit(f"  ✅ [{game_id}] {src_snip} → {tsnippet}", "#a6e3a1")
                        else:
                            self.signals.log.emit(f"  [Warning] Missing ID in response: {game_id}", "#f38ba8")
                            remaining_tasks.append((i, game_id, placeholders))
                            remaining_lines.append(lines_to_send[idx_zip])

                    batch_tasks = remaining_tasks
                    lines_to_send = remaining_lines

                    if len(batch_tasks) == 0:
                        success = True
                        break
                    elif len(results) == 0:
                        # Exponential backoff — interruptible so Stop responds immediately
                        wait_sec = min(2 ** attempt, 30)
                        self.signals.log.emit(f"  [Warning] No results parsed (attempt {attempt}). Waiting {wait_sec}s...", "#f38ba8")
                        self._interruptible_sleep(wait_sec)
                    else:
                        self.signals.log.emit(f"  [Warning] Partial success. Retrying {len(batch_tasks)} missing lines (attempt {attempt})...", "#f9e2af")
                        user_prompt = "Translate these entries:\n" + "\n".join(lines_to_send)
                        full_prompt = batch_system_prompt + "\n\n" + user_prompt

                except Exception as e:
                    err_str = str(e).lower()
                    if "429" in err_str or "quota" in err_str or "exhausted" in err_str:
                        wait_sec = 65
                        self.signals.log.emit(f"  [Rate Limit] API Quota exceeded. Waiting 65s for reset...", "#f9e2af")
                    else:
                        wait_sec = min(2 ** attempt, 30)
                        self.signals.log.emit(f"  [Error] {e} — Waiting {wait_sec}s...", "#f38ba8")
                    
                    self._interruptible_sleep(wait_sec)
                    
            if not success and not self._is_killed:
                self.signals.log.emit(f"Batch {batch_idx+1} failed after {self.max_retries} retries. Skipping...", "#f38ba8")
                
            # Intermediate Save
            try:
                temp_csv = self.output_csv + ".tmp"
                with open(temp_csv, 'w', encoding='utf-8-sig', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(headers)
                    writer.writerows(rows)
                os.replace(temp_csv, self.output_csv)
            except Exception as e:
                self.signals.log.emit(f"Failed to save intermediate: {e}", "#f38ba8")
                
            self.signals.progress.emit(processed_count, total_untrans)
            # Inter-batch delay — interruptible so Stop responds immediately
            self._interruptible_sleep(self.delay_ms / 1000.0)

        # After batch loop: emit appropriate signal based on stop state
        if self._is_killed:
            # User-requested stop: save partial progress then signal stopped
            try:
                with open(self.output_csv, 'w', encoding='utf-8-sig', newline='') as f_stop:
                    writer_stop = csv.writer(f_stop)
                    writer_stop.writerow(headers)
                    writer_stop.writerows(rows)
                self.signals.log.emit("⏹ Stopped. Partial progress saved.", "#f9e2af")
            except Exception as e_stop:
                self.signals.log.emit(f"[Warning] Could not save partial progress: {e_stop}", "#f38ba8")
            self.signals.stopped.emit()
            time.sleep(0.2)  # Allow pending signals to be processed before QRunnable is deleted
            return

        # Bug B Fix: Final save after all batches done (ensures last batch is always persisted)
        try:
            with open(self.output_csv, 'w', encoding='utf-8-sig', newline='') as f_final:
                writer_final = csv.writer(f_final)
                writer_final.writerow(headers)
                writer_final.writerows(rows)
            self.signals.log.emit("✅ Final save complete.", "#a6e3a1")
        except Exception as e_final:
            self.signals.log.emit(f"[Warning] Final save failed: {e_final}", "#f38ba8")

        self.signals.log.emit(_("log_translation_finished"), "#a6e3a1")
        self.signals.finished.emit()
        time.sleep(0.2)  # Allow pending signals to be processed before QRunnable is deleted


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
        
        logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "assets", "TRun.png"))
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))
        
        self.threadpool = QThreadPool()
        self.profiles_data = TStudioCore.load_profiles()
        self.is_running = False
        self._workers = []  # Keep ApiWorker references alive until QThreadPool finishes
        
        self.init_ui()
        self.refresh_profiles_combo()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        
        # --- HEADER: Profiles & Settings ---
        header_layout = QHBoxLayout()
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
        l_opts.addWidget(self.chk_mask)
        l_opts.addWidget(self.chk_glossary)
        l_opts.addWidget(self.chk_pua)
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

    def update_preview(self, *args):
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
        self.txt_log.append(f'<span style="color:{color};">{text}</span>')
        self.txt_log.verticalScrollBar().setValue(self.txt_log.verticalScrollBar().maximum())

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
        paths, _ext = QFileDialog.getOpenFileNames(self, _("Select Input CSV"), "", "Supported Files (*.csv *.bundle *.txt *.pak *.*);;CSV Files (*.csv);;Unity Bundles (*.bundle *.txt *.*);;PAK Files (*.pak);;All Files (*.*)")
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
        folder = QFileDialog.getExistingDirectory(self, "Select Input Folder (Contains CSVs)")
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
        self._run_next_in_queue()
        
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
            peak_config=peak_config
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
            
            # ETA Calculation
            import time
            if hasattr(self, 'current_job_start_time') and current > 0:
                elapsed = time.time() - self.current_job_start_time
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
        base_name = os.path.basename(self.current_in_file)
        self.log(f"Finished processing: {base_name}", "#a6e3a1")
        self._set_queue_status(base_name, "Completed ✅")
        if self.is_running:
            self._run_next_in_queue()

    def on_worker_stopped(self):
        """Called when user pressed Stop — resets UI without starting next file."""
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
    args, unknown = parser.parse_known_args()
    
    TStudioCore.set_project_path(args.project)
    
    app = QApplication(sys.argv)
    window = TRunApp(project_path=args.project)
    window.show()
    sys.exit(app.exec())
