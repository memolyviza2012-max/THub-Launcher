from trun_i18n import _
# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Core')))

import os
import csv
import json
import time
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QSplitter, QGroupBox, QComboBox, 
    QMessageBox, QTextEdit, QFileDialog, QSpinBox, QCheckBox, QProgressBar, QSlider,
    QTabWidget, QTableWidget, QTableWidgetItem, QTimeEdit
)
from PyQt6.QtCore import Qt, QRunnable, QThreadPool, pyqtSignal, pyqtSlot, QObject, QLocale, QTime, QTimer
from PyQt6.QtGui import QIcon

from tpua_engine import TPUAEngine
from tstudio_core import TStudioCore, CoreAI


class TRunWorkerSignals(QObject):
    progress = pyqtSignal(int, int) # current, total
    batch_progress = pyqtSignal(int, int) # current_batch, total_batches
    log = pyqtSignal(str, str) # text, color
    finished = pyqtSignal()
    error = pyqtSignal(str)

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

    def is_translated(self, text):
        import re
        if not text or not isinstance(text, str): return False
        return bool(re.search(r'[฀-๿]', text))

    def mask_tags(self, text):
        import re
        tag_pattern = r'(<[^>]+>|\\n|\\r|\n|\r|%[sdiefg]|\{\d+\}|\[\[[^\]]+\]\])'
        tags = re.findall(tag_pattern, text)
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
        glossary = self.profile.get("glossary", {})
        for wrong_word, correct_word in glossary.items():
            if isinstance(correct_word, list):
                correct_word = correct_word[0]
            text = text.replace(wrong_word, correct_word)
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
        if "[GLOSSARY TO USE]" not in prompt:
            return prompt
            
        glossary = self.profile.get("glossary", {})
        if not glossary:
            return prompt.replace("[GLOSSARY TO USE]", "")
            
        matched_terms = []
        source_lower = source_text_batch.lower()
        
        import re as _re
        for eng, val in glossary.items():
            eng_str = eng.strip()
            if not eng_str: continue
            if _re.search(r'\b' + _re.escape(eng_str.lower()) + r'\b', source_lower):
                if isinstance(val, list):
                    term_info = f"- {eng_str} = {val[0]}"
                    if len(val) > 1 and val[1]:
                        term_info += f" ({val[1]})"
                    matched_terms.append(term_info)
                else:
                    matched_terms.append(f"- {eng_str} = {val}")
                    
        if matched_terms:
            glossary_text = "GLOSSARY FOR THIS BATCH:\n" + "\n".join(matched_terms)
            return prompt.replace("[GLOSSARY TO USE]", glossary_text)
        else:
            return prompt.replace("[GLOSSARY TO USE]", "")

    def stop(self):
        self._is_killed = True

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
            
        system_prompt += "\n\nFORMAT RULE: Output MUST be tab-separated lines: ID [TAB] THAI_TRANSLATION"
        
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
            
            # Prepare batch lines
            batch_tasks = []
            lines_to_send = []
            for i, row in batch:
                game_id = row[col_id]
                source_text = row[col_source]
                
                snippet = source_text[:40].replace("\\n", " ") + ("..." if len(source_text) > 40 else "")
                self.signals.log.emit(f"  ⏳ Translating: [{game_id}] {snippet}", "#bac2de")
                
                if self.use_mask:
                    masked, placeholders = self.mask_tags(source_text)
                else:
                    masked, placeholders = source_text, {}
                    
                batch_tasks.append((i, game_id, placeholders))
                lines_to_send.append(f'"{game_id}"	"{masked}"')
                
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
                    
                    # Parse TSV reply
                    reply = re.sub(r'^```[^\n]*\n?', '', reply.strip(), flags=re.MULTILINE)
                    reply = re.sub(r'\n?```$', '', reply, flags=re.MULTILINE)
                    
                    results = {}
                    for line in reply.split('\n'):
                        line = line.strip()
                        if '\t' not in line: continue
                        parts = line.split('\t', 1)
                        results[parts[0].strip().strip('"')] = parts[1].strip().strip('"')
                        
                    # Apply results
                    for i, game_id, placeholders in batch_tasks:
                        if game_id in results:
                            translated = results[game_id]
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
                            
                            tsnippet = translated[:40].replace("\\n", " ") + ("..." if len(translated) > 40 else "")
                            self.signals.log.emit(f"  ✅ Done: [{game_id}] {tsnippet}", "#a6e3a1")
                        else:
                            self.signals.log.emit(f"  [Warning] Missing ID in response: {game_id}", "#f38ba8")
                            
                    if len(results) == 0:
                        self.signals.log.emit(f"  [Warning] AI response parsed but no tab-separated results found (attempt {attempt}). Retrying...", "#f38ba8")
                    else:
                        success = True
                        break
                    
                except Exception as e:
                    self.signals.log.emit(f"  [Error] {e}", "#f38ba8")
                    time.sleep(2)
                    
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
            time.sleep(self.delay_ms / 1000.0)
            
        self.signals.log.emit(_("log_translation_finished"), "#a6e3a1")
        self.signals.finished.emit()


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
        
        btn_prompt = QPushButton(_("btn_prompts"))
        btn_prompt.setToolTip(_("tooltip_prompt"))
        btn_prompt.clicked.connect(self.open_prompts)
        btn_glossary = QPushButton(_("btn_glossary"))
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
        
        h1 = QHBoxLayout()
        self.txt_input = QLineEdit()
        self.txt_input.setPlaceholderText(_("placeholder_input"))
        btn_in_file = QPushButton(_("btn_file"))
        btn_in_file.setToolTip(_("tooltip_in_file"))
        btn_in_file.clicked.connect(self.browse_input)
        btn_in_folder = QPushButton(_("btn_folder"))
        btn_in_folder.setToolTip(_("tooltip_in_folder"))
        btn_in_folder.clicked.connect(self.browse_input_folder)
        h1.addWidget(self.txt_input)
        h1.addWidget(btn_in_file)
        h1.addWidget(btn_in_folder)
        l_file.addLayout(h1)
        
        h2 = QHBoxLayout()
        self.txt_output = QLineEdit()
        self.txt_output.setPlaceholderText(_("placeholder_output"))
        btn_out = QPushButton(_("btn_browse"))
        btn_out.setToolTip(_("tooltip_out"))
        btn_out.clicked.connect(self.browse_output)
        h2.addWidget(self.txt_output)
        h2.addWidget(btn_out)
        l_file.addLayout(h2)
        
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
        self.lbl_batch_val = QLabel("20")
        self.lbl_batch_val.setFixedWidth(30)
        self.slider_batch.valueChanged.connect(lambda v: self.lbl_batch_val.setText(str(v)))
        h_batch.addWidget(self.slider_batch)
        h_batch.addWidget(self.lbl_batch_val)
        
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
        self.spin_delay.setValue(500)
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
        self.time_schedule.setDisplayFormat("HH:mm")
        self.time_schedule.setEnabled(False)
        self.chk_schedule.toggled.connect(self.time_schedule.setEnabled)
        h_sched.addWidget(self.chk_schedule)
        h_sched.addWidget(self.time_schedule)
        l_peak.addLayout(h_sched)
        
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
        self.time_peak_start.setDisplayFormat("HH:mm")
        self.time_peak_start.setTime(QTime(18, 0))
        h_peak_time.addWidget(QLabel("Peak Start:"))
        h_peak_time.addWidget(self.time_peak_start)
        
        self.time_peak_end = QTimeEdit()
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
        
        self.txt_input.textChanged.connect(self.update_preview)
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
        input_file = self.txt_input.text()
        batch_size = self.slider_batch.value()
        delay_ms = self.spin_delay.value()
        
        if not input_file:
            self.lbl_preview.setText(_("preview_select_valid"))
            return
            
        import os
        if not os.path.exists(input_file):
            self.lbl_preview.setText(_("preview_not_exist"))
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
        avg_api_time = 7.0 
        total_time_sec = batches * (avg_api_time + (delay_ms / 1000.0))
        m, s = divmod(int(total_time_sec), 60)
        h, m = divmod(m, 60)
        eta_str = f"{h}h {m}m" if h > 0 else f"{m}m {s}s"
        
        self.lbl_preview.setText(f"ℹ️ Preview: {untranslated:,} untranslated lines\n📦 Will process in {batches:,} batches\n⏱️ Est. Time: {eta_str} (Based on 7s/batch)")

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
        path, _ext = QFileDialog.getOpenFileName(self, _("Select Input CSV"), "", "Supported Files (*.csv *.bundle *.txt *.pak *.*);;CSV Files (*.csv);;Unity Bundles (*.bundle *.txt *.*);;PAK Files (*.pak);;All Files (*.*)")
        if path:
            def do_work():
                try:
                    if path.lower().endswith('.pak'):
                        from tstudio_core import TPakManager, TStudioCore
                        csv_out = TPakManager.extract_pak_to_csv(path)
                        if csv_out:
                            cfg = TStudioCore.load_config()
                            cfg["origin_file"] = path
                            TStudioCore.save_config(cfg)
                            return csv_out
                except Exception as e:
                    print(f"PAK extract error: {e}")
                try:
                    from tbundle_manager import TBundleManager
                    if TBundleManager.is_unity_bundle(path):
                        csv_out = TBundleManager.extract_text_to_csv(path)
                        if csv_out:
                            return csv_out
                except Exception as e:
                    print(f"Bundle extract error: {e}")
                return path

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
            self.txt_input.setText(folder)
            out_folder = folder + "_translated"
            self.txt_output.setText(out_folder)
            
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
                    self.log("Batch Smart Import cancelled. Queueing original files (may fail).", "#f38ba8")
            
            self.queue = [(f, os.path.join(out_folder, os.path.basename(f))) for f in csv_files]
        
        # Populate Queue Table
        self.tbl_queue.setRowCount(0)
        from PyQt6.QtWidgets import QTableWidgetItem
        from PyQt6.QtCore import Qt
        for i, (in_file, out_file) in enumerate(self.queue):
            self.tbl_queue.insertRow(i)
            item_name = QTableWidgetItem(os.path.basename(in_file))
            item_status = QTableWidgetItem("Pending ⏳")
            item_status.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tbl_queue.setItem(i, 0, item_name)
            self.tbl_queue.setItem(i, 1, item_status)
            
        # Log AFTER the loop, not inside it (was logging N times per iteration)
        self.log(f"Selected Folder: {folder}", "#a6e3a1")
        self.log(f"Found {len(self.queue)} CSV files to translate in queue.", "#89b4fa")

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

        self.txt_input.setText(path)
        self.queue = [] # Single file mode clears queue
        if not self.txt_output.text():
            self.txt_output.setText(path.replace(".csv", "_translated.csv"))
            
    def browse_output(self):
        path, _ext = QFileDialog.getSaveFileName(self, _("fdlg_select_output_csv"), "", "CSV Files (*.csv)")
        if path:
            self.txt_output.setText(path)

    def toggle_risk(self, checked):
        if checked:
            reply = QMessageBox.warning(self, _("warn_risk_mode_title"), 
                _("warn_risk_mode_msg"), 
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.slider_batch.setRange(1, 500)
            else:
                self.chk_unlock.setChecked(False)
        else:
            self.slider_batch.setRange(1, 100)
            if self.slider_batch.value() > 100:
                self.slider_batch.setValue(100)

    def export_original(self):
        output_path = self.txt_output.text()
        if not output_path:
            QMessageBox.warning(self, "No File", "Please specify an output file first, or run a translation.")
            return
            
        import os
        if not os.path.exists(output_path):
            QMessageBox.warning(self, "Not Found", f"Output file does not exist yet:\\n{output_path}\\nPlease run the translation first.")
            return
            
        try:
            from tbundle_manager import TBundleManager
            base_dir = os.path.dirname(output_path)
            json_path = os.path.join(base_dir, f"{os.path.basename(output_path).replace('.csv', '')}_meta.json")
            if os.path.exists(json_path):
                success, msg_or_path = TBundleManager.deploy_csv_to_bundle(output_path)
                if success:
                    QMessageBox.information(self, "Deploy Success", f"Deployed successfully back to Unity Bundle:\\n{msg_or_path}")
                else:
                    QMessageBox.warning(self, "Deploy Failed", msg_or_path)
                return
        except Exception as e:
            pass

        from tstudio_core import TFormatManager
        success, msg_or_path = TFormatManager.export_original(output_path)
        if success:
            QMessageBox.information(self, "Export Success", f"Exported successfully to:\n{msg_or_path}")
        else:
            QMessageBox.warning(self, "Export Failed", msg_or_path)

    def deploy_all(self):
        output_path = self.txt_output.text()
        if not output_path or not os.path.isdir(output_path):
            QMessageBox.warning(self, "Folder Mode Only", "Deploy All is only available for Batch Folder translation outputs. Please select an input folder first.")
            return
            
        import glob
        csv_files = glob.glob(os.path.join(output_path, "*.csv"))
        if not csv_files:
            QMessageBox.warning(self, "No Files", f"No CSV files found in {output_path}")
            return
            
        self.log(f"Starting Batch Deploy for {len(csv_files)} files...", "#fab387")
        from tstudio_core import TFormatManager
        from tbundle_manager import TBundleManager

        # Input folder is where the original source files and meta JSONs live (BUG 4 fix)
        input_folder = self.txt_input.text()
        
        success_count = 0
        fail_count = 0
        
        for csv_file in csv_files:
            try:
                # Check PAK deployment first
                from tstudio_core import TStudioCore, TPakManager
                cfg = TStudioCore.load_config()
                origin_file = cfg.get("origin_file", "")
                if origin_file and origin_file.lower().endswith('.pak'):
                    try:
                        TPakManager.reconstruct_pak_file(origin_file, csv_file, origin_file)
                        success_count += 1
                        self.log(f"Successfully deployed to PAK file at: {origin_file}", "#a6e3a1")
                        continue
                    except Exception as e:
                        fail_count += 1
                        self.log(f"Failed to deploy PAK file: {e}", "#f38ba8")
                        continue

                stem = os.path.splitext(os.path.basename(csv_file))[0]
                json_path = os.path.join(input_folder, f'{stem}_meta.json')

                # Check Bundle first
                if os.path.exists(json_path):
                    success, msg = TBundleManager.deploy_csv_to_bundle(csv_file)
                    if success:
                        success_count += 1
                    else:
                        fail_count += 1
                        self.log(f"Failed bundle deploy {os.path.basename(csv_file)}: {msg}", "#f38ba8")
                    continue
                    
                # Fallback to normal export_original
                success, msg = TFormatManager.export_original(csv_file)
                if success:
                    success_count += 1
                else:
                    fail_count += 1
                    self.log(f"Failed format deploy {os.path.basename(csv_file)}: {msg}", "#f38ba8")

            except Exception as deploy_err:
                fail_count += 1
                self.log(f"Error deploying {os.path.basename(csv_file)}: {deploy_err}", "#f38ba8")
                
            QApplication.processEvents()  # Keep UI responsive during batch deploy
                
        self.log(f"Batch Deploy Finished. Success: {success_count}, Failed: {fail_count}", "#a6e3a1")
        QMessageBox.information(self, "Deploy Complete", f"Batch Deploy finished.\nSuccess: {success_count}\nFailed: {fail_count}")

    def start_translation(self):
        if not self.txt_input.text() or not self.txt_output.text():
            QMessageBox.warning(self, _("warn_select_io_title") if '_' in globals() else "Warning", _("warn_select_io_msg") if '_' in globals() else "Please select input and output folders.")
            return

        if self.is_running:
            return
            
        # Initialize queue if not already set (for single file mode)
        if not hasattr(self, 'queue') or not self.queue:
            if os.path.isfile(self.txt_input.text()):
                self.queue = [(self.txt_input.text(), self.txt_output.text())]
                # Populate queue tracker table for single-file mode
                self.tbl_queue.setRowCount(0)
                self.tbl_queue.insertRow(0)
                from PyQt6.QtWidgets import QTableWidgetItem
                item_name = QTableWidgetItem(os.path.basename(self.txt_input.text()))
                item_status = QTableWidgetItem("Pending ⏳")
                item_status.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tbl_queue.setItem(0, 0, item_name)
                self.tbl_queue.setItem(0, 1, item_status)
            else:
                QMessageBox.warning(self, _("warn_select_io_title"), "Input is neither a file nor a valid folder queue.")
                return

        self.log(f"Batch Translation Engine starting with {len(self.queue)} files in queue...", "#89b4fa")
        self.is_running = True
        
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.cbo_preset.setEnabled(False)
        
        # Ensure output directory exists if in folder mode
        if len(self.queue) > 1:
            os.makedirs(self.txt_output.text(), exist_ok=True)
            
        if hasattr(self, 'chk_schedule') and self.chk_schedule.isChecked():
            target_time = self.time_schedule.time()
            current_time = QTime.currentTime()
            msecs = current_time.msecsTo(target_time)
            if msecs < 0:
                msecs += 86400000 # Add 24 hours if target time is tomorrow
            
            self.log(f"Scheduled to start at {target_time.toString('HH:mm')} (in {msecs // 60000} minutes)...", "#f9e2af")
            for filename, _ in self.queue:
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
            
        self.current_in_file, self.current_out_file = self.queue.pop(0)
        base_name = os.path.basename(self.current_in_file)
        self.log(f"Processing: {base_name}...", "#cba6f7")
        self._set_queue_status(base_name, "Translating 🔄")
        
        import time
        self.current_job_start_time = time.time()
        
        self.progress_bar.setValue(0)
        self.batch_progress_bar.setValue(0)
        self.lbl_batch_progress.setText(_("lbl_batch_progress_default"))
        if hasattr(self, 'lbl_eta'):
            self.lbl_eta.setText("ETA: Calculating...")
        
        cfg = TStudioCore.load_config()
        profile = TStudioCore.get_current_profile_data()
        
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
        
        self.worker.signals.log.connect(self.log)
        self.worker.signals.progress.connect(self.update_progress)
        self.worker.signals.batch_progress.connect(self.update_batch_progress)
        self.worker.signals.finished.connect(self.on_file_finished)
        self.worker.signals.error.connect(self.on_error)
        
        self.threadpool.start(self.worker)
        
    def update_batch_progress(self, current, total):
        if total > 0:
            pct = int((current / total) * 100)
            self.batch_progress_bar.setValue(pct)
            self.lbl_batch_progress.setText(f"Batch: {current} / {total} ({pct}%)")
            
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
            
    def on_all_queue_finished(self):
        self.is_running = False
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.cbo_preset.setEnabled(True)
        self.log("All files in queue completed successfully!", "#a6e3a1")
        QMessageBox.information(self, "Done", "All translations completed successfully!")
        
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
            for filename, _ in self.queue:
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
    parser.add_argument("--project", type=str, help="Path to THub project", default=None)
    args, unknown = parser.parse_known_args()
    
    app = QApplication(sys.argv)
    window = TRunApp(project_path=args.project)
    window.show()
    sys.exit(app.exec())
