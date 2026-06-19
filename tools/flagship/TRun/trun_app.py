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
    QMessageBox, QTextEdit, QFileDialog, QSpinBox, QCheckBox, QProgressBar, QSlider
)
from PyQt6.QtCore import Qt, QRunnable, QThreadPool, pyqtSignal, pyqtSlot, QObject, QLocale
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
    def __init__(self, config, profile, input_csv, output_csv, batch_size, delay_ms, max_retries, use_mask, use_glossary, use_pua):
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
            text = text.replace(wrong_word, correct_word)
        return text

    def stop(self):
        self._is_killed = True

    def run(self):
        import csv, time, re
        self.signals.log.emit("Loading CSV file...", "#89b4fa")
        rows = []
        headers = []
        try:
            with open(self.input_csv, 'r', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                headers = next(reader)
                rows = list(reader)
        except Exception as e:
            self.signals.error.emit(f"Failed to read CSV: {e}")
            return

        total_rows = len(rows)
        self.signals.log.emit(f"Found {total_rows} rows to process.", "#a6e3a1")
        
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
            self.signals.log.emit("Initializing TPUA Engine...", "#f9e2af")
            tpua = TPUAEngine()
        
        for batch_idx, batch in enumerate(batches):
            self.signals.batch_progress.emit(batch_idx + 1, total_batches)
            if self._is_killed:
                self.signals.log.emit("Emergency Stop Triggered. Saving checkpoint...", "#f38ba8")
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
                
            user_prompt = "Translate these entries:\n" + "\n".join(lines_to_send)
            full_prompt = system_prompt + "\n\n" + user_prompt
            
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
                            if self.use_pua and tpua:
                                translated = tpua.encode(translated)
                            rows[i][col_trans] = translated
                            processed_count += 1
                            
                            tsnippet = translated[:40].replace("\\n", " ") + ("..." if len(translated) > 40 else "")
                            self.signals.log.emit(f"  ✅ Done: [{game_id}] {tsnippet}", "#a6e3a1")
                        else:
                            self.signals.log.emit(f"  [Warning] Missing ID in response: {game_id}", "#f38ba8")
                            
                    success = True
                    break
                    
                except Exception as e:
                    self.signals.log.emit(f"  [Error] {e}", "#f38ba8")
                    time.sleep(2)
                    
            if not success and not self._is_killed:
                self.signals.log.emit(f"Batch {batch_idx+1} failed after {self.max_retries} retries. Skipping...", "#f38ba8")
                
            # Intermediate Save
            try:
                with open(self.output_csv, 'w', encoding='utf-8-sig', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(headers)
                    writer.writerows(rows)
            except Exception as e:
                self.signals.log.emit(f"Failed to save intermediate: {e}", "#f38ba8")
                
            self.signals.progress.emit(processed_count, total_untrans)
            time.sleep(self.delay_ms / 1000.0)
            
        self.signals.log.emit("Translation process finished.", "#a6e3a1")
        self.signals.finished.emit()


from tstudio_ui_shared import SettingsDialog, PromptSettingsDialog, GlossaryDialog

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
    def __init__(self):
        super().__init__()
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('flagship.trun.app.1.0')
        except:
            pass
        self.setWindowTitle("🚀 TRun: Advanced Batch Translation Engine")
        self.resize(1100, 750)
        self.setStyleSheet(DARK_SS)
        
        logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "assets", "TRun.png"))
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))
        
        self.threadpool = QThreadPool()
        self.profiles_data = TStudioCore.load_profiles()
        self.is_running = False
        
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
        
        btn_new_profile = QPushButton("➕ New")
        btn_new_profile.clicked.connect(self.create_new_profile)
        btn_rename_profile = QPushButton("✏️ Rename")
        btn_rename_profile.clicked.connect(self.rename_profile)
        btn_del_profile = QPushButton("🗑 Delete")
        btn_del_profile.clicked.connect(self.delete_profile)
        
        header_layout.addWidget(btn_new_profile)
        header_layout.addWidget(btn_rename_profile)
        header_layout.addWidget(btn_del_profile)
        
        btn_prompt = QPushButton("📝 Prompts")
        btn_prompt.clicked.connect(self.open_prompts)
        btn_glossary = QPushButton("📖 Glossary")
        btn_glossary.clicked.connect(self.open_glossary)
        btn_settings = QPushButton("⚙️ API Settings")
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
        grp_file = QGroupBox("📁 File Configuration")
        l_file = QVBoxLayout(grp_file)
        
        h1 = QHBoxLayout()
        self.txt_input = QLineEdit()
        self.txt_input.setPlaceholderText("Select Input CSV...")
        btn_in = QPushButton("Browse")
        btn_in.clicked.connect(self.browse_input)
        h1.addWidget(self.txt_input)
        h1.addWidget(btn_in)
        l_file.addLayout(h1)
        
        h2 = QHBoxLayout()
        self.txt_output = QLineEdit()
        self.txt_output.setPlaceholderText("Output CSV Path...")
        btn_out = QPushButton("Browse")
        btn_out.clicked.connect(self.browse_output)
        h2.addWidget(self.txt_output)
        h2.addWidget(btn_out)
        l_file.addLayout(h2)
        
        left_layout.addWidget(grp_file)

        # Batch Engine Config
        grp_engine = QGroupBox("⚙️ Engine Configuration")
        l_engine = QVBoxLayout(grp_engine)
        
        h_batch = QHBoxLayout()
        h_batch.addWidget(QLabel("Batch Size (Lines):"))
        self.slider_batch = QSlider(Qt.Orientation.Horizontal)
        self.slider_batch.setRange(1, 100)
        self.slider_batch.setValue(20)
        self.lbl_batch_val = QLabel("20")
        self.lbl_batch_val.setFixedWidth(30)
        self.slider_batch.valueChanged.connect(lambda v: self.lbl_batch_val.setText(str(v)))
        h_batch.addWidget(self.slider_batch)
        h_batch.addWidget(self.lbl_batch_val)
        
        self.chk_unlock = QCheckBox("⚠️ Unlock Risk Mode")
        self.chk_unlock.setStyleSheet("color: #f38ba8;")
        self.chk_unlock.toggled.connect(self.toggle_risk)
        h_batch.addWidget(self.chk_unlock)
        l_engine.addLayout(h_batch)
        
        h_delay = QHBoxLayout()
        h_delay.addWidget(QLabel("Delay between chunks (ms):"))
        self.spin_delay = QSpinBox()
        self.spin_delay.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
        self.spin_delay.setRange(0, 10000)
        self.spin_delay.setValue(500)
        h_delay.addWidget(self.spin_delay)
        l_engine.addLayout(h_delay)
        
        h_retry = QHBoxLayout()
        h_retry.addWidget(QLabel("Max Retries per chunk:"))
        self.spin_retry = QSpinBox()
        self.spin_retry.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
        self.spin_retry.setRange(0, 10)
        self.spin_retry.setValue(3)
        h_retry.addWidget(self.spin_retry)
        l_engine.addLayout(h_retry)
        
        self.lbl_preview = QLabel("ℹ️ Preview: Select Input CSV to see batch info.")
        self.lbl_preview.setStyleSheet("color: #a6e3a1; font-weight: normal; margin-top: 10px; padding: 6px; border: 1px solid #45475a; border-radius: 4px; background: #181825;")
        self.lbl_preview.setWordWrap(True)
        l_engine.addWidget(self.lbl_preview)
        
        left_layout.addWidget(grp_engine)
        
        # Processing Options
        grp_opts = QGroupBox("🔠 Post-Processing")
        l_opts = QVBoxLayout(grp_opts)
        self.chk_mask = QCheckBox("Auto-Mask Tags (e.g., %s -> [TAG_0])")
        self.chk_mask.setChecked(True)
        self.chk_glossary = QCheckBox("Enforce Glossary Replacement")
        self.chk_glossary.setChecked(True)
        self.chk_pua = QCheckBox("Auto-Apply PUA Encode (Requires TPUA Plugin)")
        self.chk_pua.setChecked(False) # Will implement TPUA next phase
        l_opts.addWidget(self.chk_mask)
        l_opts.addWidget(self.chk_glossary)
        l_opts.addWidget(self.chk_pua)
        left_layout.addWidget(grp_opts)
        
        left_layout.addStretch()
        splitter.addWidget(left_panel)
        
        # --- RIGHT PANEL: Dashboard ---
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 0, 0, 0)
        
        # Stats
        h_batch_stats = QHBoxLayout()
        self.lbl_batch_progress = QLabel("Batch: 0 / 0 (0%)")
        self.lbl_batch_progress.setStyleSheet("color: #89b4fa; font-weight: bold;")
        h_batch_stats.addWidget(self.lbl_batch_progress)
        h_batch_stats.addStretch()
        
        self.lbl_eta = QLabel("ETA: --:--:--")
        h_batch_stats.addWidget(self.lbl_eta)
        right_layout.addLayout(h_batch_stats)
        
        self.batch_progress_bar = QProgressBar()
        self.batch_progress_bar.setValue(0)
        self.batch_progress_bar.setStyleSheet("QProgressBar { border: 1px solid #45475a; border-radius: 4px; text-align: center; } QProgressBar::chunk { background-color: #89b4fa; }")
        right_layout.addWidget(self.batch_progress_bar)
        
        h_stats = QHBoxLayout()
        self.lbl_progress = QLabel("Lines: 0 / 0 (0%)")
        self.lbl_progress.setStyleSheet("color: #a6e3a1; font-weight: bold;")
        h_stats.addWidget(self.lbl_progress)
        h_stats.addStretch()
        right_layout.addLayout(h_stats)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        right_layout.addWidget(self.progress_bar)
        
        # Terminal Log
        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setStyleSheet("background: #181825; color: #a6adc8; font-family: Consolas, monospace;")
        right_layout.addWidget(self.txt_log)
        
        # Actions
        h_action = QHBoxLayout()
        self.btn_start = QPushButton("▶️ START TRANSLATION")
        self.btn_start.setStyleSheet("background: #a6e3a1; color: #1e1e2e; font-size: 16px;")
        self.btn_start.clicked.connect(self.start_translation)
        
        self.btn_stop = QPushButton("⏹ STOP & EMERGENCY SAVE")
        self.btn_stop.setStyleSheet("background: #f38ba8; color: #1e1e2e;")
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.stop_translation)
        
        h_action.addWidget(self.btn_start)
        h_action.addWidget(self.btn_stop)
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
            self.cbo_preset.addItems(list(self.profiles_data["presets"].keys()))
            
            active = self.profiles_data.get("active_preset", "Default")
            if current_text in self.profiles_data["presets"]:
                self.cbo_preset.setCurrentText(current_text)
            elif active in self.profiles_data["presets"]:
                self.cbo_preset.setCurrentText(active)
            self.cbo_preset.blockSignals(False)
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
            self.lbl_preview.setText("ℹ️ Preview: Select a valid Input CSV.")
            return
            
        import os
        if not os.path.exists(input_file):
            self.lbl_preview.setText("ℹ️ Preview: Input CSV does not exist.")
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
            self.lbl_preview.setText("ℹ️ Preview: Error reading CSV.")
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

    def on_preset_changed(self, text):
        if text:
            self.profiles_data["active_preset"] = text
            TStudioCore.save_profiles(self.profiles_data)
            self.log(f"Profile switched to: {text}")

    def create_new_profile(self):
        from PyQt6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "New Profile", "Enter new profile name:")
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
            QMessageBox.warning(self, "Warning", "Cannot rename the Default profile.")
            return
            
        new_name, ok = QInputDialog.getText(self, "Rename Profile", f"Enter new name for '{active}':", text=active)
        if ok and new_name.strip():
            new_name = new_name.strip()
            if new_name == active: return
            if new_name in self.profiles_data["presets"]:
                QMessageBox.warning(self, "Warning", f"Profile '{new_name}' already exists.")
                return
                
            self.profiles_data["presets"][new_name] = self.profiles_data["presets"].pop(active)
            self.profiles_data["active_preset"] = new_name
            TStudioCore.save_profiles(self.profiles_data)
            self.refresh_profiles_combo()
            self.log(f"Profile renamed to '{new_name}'.")

    def delete_profile(self):
        active = self.cbo_preset.currentText()
        if active == "Default":
            QMessageBox.warning(self, "Warning", "Cannot delete the Default profile.")
            return
            
        reply = QMessageBox.question(self, 'Confirm Delete', f"Are you sure you want to delete profile '{active}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            del self.profiles_data["presets"][active]
            self.profiles_data["active_preset"] = "Default"
            TStudioCore.save_profiles(self.profiles_data)
            self.refresh_profiles_combo()
            self.log(f"Profile '{active}' deleted.")

    def open_settings(self):
        dlg = SettingsDialog(self)
        if dlg.exec():
            pass

    def open_prompts(self):
        dlg = PromptSettingsDialog(self)
        if dlg.exec():
            self.refresh_profiles_combo()

    def open_glossary(self):
        dlg = GlossaryDialog(self)
        if dlg.exec():
            self.refresh_profiles_combo()
            
    def browse_input(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Input CSV", "", "Supported Files (*.csv *.bundle *.txt *.*);;CSV Files (*.csv);;Unity Bundles (*.bundle *.txt *.*);;All Files (*.*)")
        if path:
            try:
                from tbundle_manager import TBundleManager
                if TBundleManager.is_unity_bundle(path):
                    csv_out = TBundleManager.extract_text_to_csv(path)
                    if csv_out:
                        path = csv_out
            except Exception as e:
                print(f"Bundle extract error: {e}")

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
                        QMessageBox.information(self, "TFormat", "File has been formatted to standard.")
                    except Exception as e:
                        QMessageBox.critical(self, "Error", f"Failed to format: {e}")
                        return
                else:
                    return

            self.txt_input.setText(path)
            if not self.txt_output.text():
                self.txt_output.setText(path.replace(".csv", "_translated.csv"))
                
    def browse_output(self):
        path, _ = QFileDialog.getSaveFileName(self, "Select Output CSV", "", "CSV Files (*.csv)")
        if path:
            self.txt_output.setText(path)

    def toggle_risk(self, checked):
        if checked:
            reply = QMessageBox.warning(self, "Unlock Risk Mode", 
                "WARNING: Setting batch size over 100 may cause API timeouts, hallucinations, or memory crashes. Proceed?", 
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
            QMessageBox.information(self, "Export Success", f"Exported successfully to:\\n{msg_or_path}")
        else:
            QMessageBox.warning(self, "Export Failed", msg_or_path)

    def start_translation(self):
        if not self.txt_input.text() or not self.txt_output.text():
            QMessageBox.warning(self, "Error", "Please select input and output CSV files first.")
            return
            
        if self.is_running:
            return
            
        self.log("Batch Translation Engine starting...", "#89b4fa")
        self.is_running = True
        
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.cbo_preset.setEnabled(False)
        self.progress_bar.setValue(0)
        self.batch_progress_bar.setValue(0)
        self.lbl_batch_progress.setText("Batch: 0 / 0 (0%)")
        
        cfg = TStudioCore.load_config()
        profile = TStudioCore.get_current_profile_data()
        
        self.worker = TRunWorker(
            config=cfg,
            profile=profile,
            input_csv=self.txt_input.text(),
            output_csv=self.txt_output.text(),
            batch_size=self.slider_batch.value(),
            delay_ms=self.spin_delay.value(),
            max_retries=self.spin_retry.value(),
            use_mask=self.chk_mask.isChecked(),
            use_glossary=self.chk_glossary.isChecked(),
            use_pua=self.chk_pua.isChecked()
        )
        
        self.worker.signals.log.connect(self.log)
        self.worker.signals.progress.connect(self.update_progress)
        self.worker.signals.batch_progress.connect(self.update_batch_progress)
        self.worker.signals.finished.connect(self.on_finished)
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
            
    def on_finished(self):
        self.is_running = False
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.cbo_preset.setEnabled(True)
        self.log("Process complete!", "#a6e3a1")
        
    def on_error(self, err_str):
        self.log(f"CRITICAL ERROR: {err_str}", "#f38ba8")
        self.on_finished()

    def stop_translation(self):
        if not hasattr(self, 'worker') or not self.is_running:
            return
        self.worker.stop()
        self.log("STOP requested. Saving progress and stopping...", "#f38ba8")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TRunApp()
    window.show()
    sys.exit(app.exec())
