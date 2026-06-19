import sys
import json
import re
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QComboBox, 
    QLineEdit, QLabel, QPushButton, QMessageBox, QTextEdit, 
    QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView, QSpinBox, QApplication
)
from PyQt6.QtCore import Qt, QLocale, QThreadPool, QRunnable, pyqtSignal, QObject, pyqtSlot
from tstudio_core import TStudioCore, CoreAI, DEFAULT_SINGLE_PROMPT, DEFAULT_OPTIONS_PROMPT


class WorkerSignals(QObject):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

class ApiWorker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
            self.signals.finished.emit(result)
        except Exception as e:
            self.signals.error.emit(str(e))

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚙️ Settings (API & Model)")
        self.setFixedSize(450, 250)
        
        self.api_keys = {"Google Gemini": "", "Anthropic Claude": "", "DeepSeek": "", "OpenAI": ""}
        self.models_by_provider = {
            "Google Gemini": ["gemini-3.5-flash", "gemini-3.1-pro", "gemini-3.1-flash-lite", "gemini-2.5-flash", "gemini-1.5-pro", "gemini-1.5-flash"],
            "Anthropic Claude": ["claude-opus-4.7", "claude-sonnet-4.6", "claude-haiku-4.5", "claude-3-5-sonnet-20241022"],
            "DeepSeek": ["deepseek-chat", "deepseek-reasoner", "deepseek-v4-pro", "deepseek-v4-flash"],
            "OpenAI": ["gpt-4o", "gpt-4o-mini", "o1-mini", "o3-mini"],
            "Local LLM": ["custom-local-llm"]
        }
        self.current_provider = "DeepSeek"
        
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        self.cbo_provider = QComboBox()
        self.cbo_provider.addItems(["Google Gemini", "Anthropic Claude", "DeepSeek", "OpenAI", "Local LLM"])
        self.cbo_provider.currentTextChanged.connect(self.on_provider_changed)
        form_layout.addRow("1. AI Provider:", self.cbo_provider)
        
        self.txt_api = QLineEdit()
        self.txt_api.setEchoMode(QLineEdit.EchoMode.Password)
        self.lbl_api = QLabel("2. API Key:")
        form_layout.addRow(self.lbl_api, self.txt_api)
        
        self.cbo_model = QComboBox()
        self.cbo_model.setEditable(True)
        form_layout.addRow("3. Model Name:", self.cbo_model)
        
        self.txt_local_url = QLineEdit()
        self.lbl_local = QLabel("4. Local API URL:")
        form_layout.addRow(self.lbl_local, self.txt_local_url)
        
        layout.addLayout(form_layout)
        layout.addStretch()
        
        btn_save = QPushButton("💾 Save Settings")
        btn_save.clicked.connect(self.save_config)
        layout.addWidget(btn_save)
        
        self.load_config()

    def _infer_provider(self, model):
        if model.startswith("gemini"): return "Google Gemini"
        if model.startswith("claude"): return "Anthropic Claude"
        if model.startswith("gpt") or model.startswith("o1") or model.startswith("o3"): return "OpenAI"
        if model == "custom-local-llm" or model == "local-model": return "Local LLM"
        return "DeepSeek"

    def on_provider_changed(self, new_provider):
        if self.current_provider != "Local LLM":
            self.api_keys[self.current_provider] = self.txt_api.text()
            
        self.current_provider = new_provider
        
        if new_provider == "Local LLM":
            self.txt_api.clear()
            self.txt_api.setEnabled(False)
            self.lbl_api.setText("API Key (Not needed):")
            self.txt_local_url.setEnabled(True)
            self.lbl_local.setStyleSheet("")
        else:
            self.txt_api.setEnabled(True)
            self.txt_api.setText(self.api_keys.get(new_provider, ""))
            self.lbl_api.setText(f"{new_provider} Key:")
            self.txt_local_url.setEnabled(False)
            self.lbl_local.setStyleSheet("color: gray;")
            
        current_model = self.cbo_model.currentText()
        self.cbo_model.clear()
        models = self.models_by_provider.get(new_provider, [])
        self.cbo_model.addItems(models)
        if current_model in models:
            self.cbo_model.setCurrentText(current_model)

    def load_config(self):
        try:
            data = TStudioCore.load_config()
            self.api_keys["Google Gemini"] = data.get("google_key", "")
            self.api_keys["Anthropic Claude"] = data.get("anthropic_key", "")
            self.api_keys["DeepSeek"] = data.get("deepseek_key", "")
            self.api_keys["OpenAI"] = data.get("openai_key", "")
            
            saved_model = data.get("model", "deepseek-chat")
            provider = data.get("provider", self._infer_provider(saved_model))
            
            self.cbo_provider.blockSignals(True)
            self.cbo_provider.setCurrentText(provider)
            self.cbo_provider.blockSignals(False)
            
            self.cbo_model.setCurrentText(saved_model)
            
            local_url = data.get("local_url", "http://localhost:1234/v1/chat/completions")
            self.txt_local_url.setText(local_url)
            
            if provider != "Local LLM":
                self.txt_api.setText(self.api_keys.get(provider, ""))
        except Exception as e:
            print(f"UI load_config error: {e}")
            self.cbo_provider.setCurrentText("DeepSeek")
            self.cbo_model.setCurrentText("deepseek-chat")
            self.txt_local_url.setText("http://localhost:1234/v1/chat/completions")

    def save_config(self):
        if self.current_provider != "Local LLM":
            self.api_keys[self.current_provider] = self.txt_api.text()
            
        data = {
            "google_key": self.api_keys["Google Gemini"].strip(),
            "anthropic_key": self.api_keys["Anthropic Claude"].strip(),
            "deepseek_key": self.api_keys["DeepSeek"].strip(),
            "openai_key": self.api_keys["OpenAI"].strip(),
            "api_key": self.api_keys["DeepSeek"].strip(), # Backwards compatibility
            "model": self.cbo_model.currentText().strip(),
            "provider": self.cbo_provider.currentText(),
            "local_url": self.txt_local_url.text().strip()
        }
        
        TStudioCore.save_config(data)
        QMessageBox.information(self, "Saved", "Settings saved successfully!")
        super().accept()

    def accept(self):
        self.save_config()

class PromptSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_profile = TStudioCore.load_profiles()["active_preset"]
        self.profile_data = TStudioCore.get_current_profile_data()
        
        self.setWindowTitle(f"⚙️ Prompt Settings (Editing: {self.active_profile})")
        self.resize(700, 750)
        layout = QVBoxLayout(self)

        ctx_group = QGroupBox("Auto-Generate Prompts for Game")
        ctx_layout = QHBoxLayout(ctx_group)
        self.txt_game_name = QLineEdit()
        self.txt_game_name.setPlaceholderText("e.g. Elden Ring, The Sims, Cyberpunk 2077")
        btn_gen = QPushButton("✨ Auto-Generate")
        btn_gen.setStyleSheet("background: #f5c2e7; color: #1e1e2e; font-weight: bold; padding: 4px 8px;")
        btn_gen.clicked.connect(self.auto_generate_prompts)
        
        btn_settings = QPushButton("⚙️ Settings")
        btn_settings.clicked.connect(lambda: SettingsDialog(self).exec())
        
        ctx_layout.addWidget(QLabel("Game Name:"))
        ctx_layout.addWidget(self.txt_game_name)
        ctx_layout.addWidget(btn_gen)
        ctx_layout.addWidget(btn_settings)
        layout.addWidget(ctx_group)

        self.txt_single = QTextEdit()
        self.txt_opt = QTextEdit()
        self.txt_batch = QTextEdit()

        grp1 = QGroupBox("1. Single Translation Prompt (TStudio)")
        l1 = QVBoxLayout(grp1)
        l1.addWidget(QLabel("Use {id} and {source_text} in your prompt."))
        l1.addWidget(self.txt_single)
        layout.addWidget(grp1)

        grp2 = QGroupBox("2. Three Options Prompt (TStudio)")
        l2 = QVBoxLayout(grp2)
        l2.addWidget(QLabel("Must return exactly 3 JSON strings: [\"A\", \"B\", \"C\"]"))
        l2.addWidget(self.txt_opt)
        layout.addWidget(grp2)
        
        grp3 = QGroupBox("3. Batch Translation Prompt (TRun)")
        l3 = QVBoxLayout(grp3)
        l3.addWidget(QLabel("Use {source_text} in your prompt for bulk translation."))
        l3.addWidget(self.txt_batch)
        layout.addWidget(grp3)

        btn_layout = QHBoxLayout()
        
        btn_help = QPushButton("❓ วิธีใช้ / Load Default Template")
        btn_help.setStyleSheet("background: #cba6f7; color: #1e1e2e; font-weight: bold; padding: 6px 12px;")
        btn_help.clicked.connect(self.show_help)
        btn_layout.addWidget(btn_help)
        
        btn_layout.addStretch()
        
        btn_save = QPushButton("💾 Save to Profile")
        btn_save.setStyleSheet("background: #a6e3a1; color: #1e1e2e; font-weight: bold; padding: 6px 12px;")
        btn_save.clicked.connect(self.save_current_preset)
        btn_layout.addWidget(btn_save)
        
        layout.addLayout(btn_layout)
        
        self.txt_single.setPlainText(self.profile_data.get("single", DEFAULT_SINGLE_PROMPT))
        self.txt_opt.setPlainText(self.profile_data.get("opt", DEFAULT_OPTIONS_PROMPT))
        self.txt_batch.setPlainText(self.profile_data.get("batch", self.profile_data.get("single", DEFAULT_SINGLE_PROMPT)))
        
        self._is_modified = False
        self.txt_single.textChanged.connect(self.mark_modified)
        self.txt_opt.textChanged.connect(self.mark_modified)
        self.txt_batch.textChanged.connect(self.mark_modified)

    def mark_modified(self):
        self._is_modified = True

    def show_help(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("วิธีใช้ / Default Template")
        msg.setText("นี่คือปุ่มสำหรับดึง Prompt ต้นแบบ (Default Template) กลับมาใช้งาน\n\nระบบจะทำการเขียนทับ Prompt ปัจจุบันของคุณในช่องต่างๆ ด้วยต้นแบบ\nคุณต้องการดำเนินการต่อหรือไม่?")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if msg.exec() == QMessageBox.StandardButton.Yes:
            from tstudio_core import DEFAULT_SINGLE_PROMPT, DEFAULT_OPTIONS_PROMPT
            self.txt_single.setPlainText(DEFAULT_SINGLE_PROMPT)
            self.txt_opt.setPlainText(DEFAULT_OPTIONS_PROMPT)
            self.txt_batch.setPlainText(DEFAULT_SINGLE_PROMPT)

    def auto_generate_prompts(self):
        game_name = self.txt_game_name.text().strip()
        if not game_name:
            QMessageBox.warning(self, "Warning", "Please enter a game name first!")
            return
            
        cfg = TStudioCore.load_config()
        
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        self.setWindowTitle("⚙️ Prompt Settings - Generating... Please wait...")
        QApplication.processEvents()
        
        sys_msg = f"You are an expert prompt engineer. Create a system prompt for translating the video game '{game_name}' from English to Thai. The prompt MUST include the literal text '{{id}}' and '{{source_text}}'. Respond with ONLY the raw prompt string, no quotes, no markdown."
        
        prompt_single = sys_msg + "\n\nRequirements for the output prompt:\n1. Instruct the AI to return ONLY the pure Thai string translation of {source_text}.\n2. Specify the tone, setting, and terminology relevant to " + game_name + "."
        prompt_opt = sys_msg + "\n\nRequirements for the output prompt:\n1. Instruct the AI to return exactly 3 different Thai translation options for {source_text}.\n2. The options must vary slightly in tone or literalness, while remaining fitting for " + game_name + ".\n3. The output MUST be a strict JSON array of 3 strings."
        
        is_local = (cfg.get("provider", "") == "Local LLM" or cfg.get("model", "") == "custom-local-llm")
        
        def run_both():
            r_single = CoreAI.generate_content(cfg, prompt_single, is_local=is_local)
            r_opt = CoreAI.generate_content(cfg, prompt_opt, is_local=is_local)
            return r_single, r_opt
            
        def on_success(res):
            res_single, res_opt = res
            self.txt_single.setPlainText(res_single.strip().strip('`').strip())
            self.txt_opt.setPlainText(res_opt.strip().strip('`').strip())
            self.txt_batch.setPlainText(res_single.strip().strip('`').strip())
            QApplication.restoreOverrideCursor()
            self.setWindowTitle(f"⚙️ Prompt Settings (Editing: {self.active_profile})")
            QMessageBox.information(self, "Success", f"Prompts for '{game_name}' generated successfully!\nDon't forget to click 'Save to Profile' to keep them.")
            
        def on_error(err):
            QApplication.restoreOverrideCursor()
            self.setWindowTitle(f"⚙️ Prompt Settings (Editing: {self.active_profile})")
            QMessageBox.critical(self, "Failed", f"Error generating prompts:\n{err}")
            
        worker = ApiWorker(run_both)
        worker.signals.finished.connect(on_success)
        worker.signals.error.connect(on_error)
        QThreadPool.globalInstance().start(worker)

    def save_current_preset(self):
        data = TStudioCore.load_profiles()
        if self.active_profile in data["presets"]:
            data["presets"][self.active_profile]["single"] = self.txt_single.toPlainText()
            data["presets"][self.active_profile]["opt"] = self.txt_opt.toPlainText()
            data["presets"][self.active_profile]["batch"] = self.txt_batch.toPlainText()
            TStudioCore.save_profiles(data)
            self._is_modified = False
            QMessageBox.information(self, "Saved", f"Prompts saved to profile '{self.active_profile}'!")
            self.accept()

    def closeEvent(self, event):
        if getattr(self, '_is_modified', False):
            reply = QMessageBox.question(self, 'Unsaved Changes', "You have unsaved changes in AI Prompts. Do you want to save them before closing?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
            if reply == QMessageBox.StandardButton.Yes:
                self.save_current_preset()
                event.accept()
            elif reply == QMessageBox.StandardButton.No:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

class GlossaryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_profile = TStudioCore.load_profiles()["active_preset"]
        self.profile_data = TStudioCore.get_current_profile_data()
        
        self.setWindowTitle(f"📖 Glossary Editor (Editing: {self.active_profile})")
        self.resize(600, 500)
        layout = QVBoxLayout(self)

        ctx_group = QGroupBox("Auto-Generate Common Glossary for Game")
        ctx_layout = QHBoxLayout(ctx_group)
        self.txt_game_name = QLineEdit()
        self.txt_game_name.setPlaceholderText("e.g. Elden Ring, The Sims, Cyberpunk 2077")
        btn_gen = QPushButton("✨ Auto-Generate")
        btn_gen.setStyleSheet("background: #f5c2e7; color: #1e1e2e; font-weight: bold; padding: 4px 8px;")
        btn_gen.clicked.connect(self.auto_generate_glossary)
        self.spin_amount = QSpinBox()
        self.spin_amount.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
        self.spin_amount.setRange(1, 100)
        self.spin_amount.setValue(30)
        self.spin_amount.setFixedWidth(80)
        
        btn_settings = QPushButton("⚙️ Settings")
        btn_settings.clicked.connect(lambda: SettingsDialog(self).exec())
        
        ctx_layout.addWidget(QLabel("Game Name:"))
        ctx_layout.addWidget(self.txt_game_name)
        ctx_layout.addWidget(QLabel("Amount:"))
        ctx_layout.addWidget(self.spin_amount)
        ctx_layout.addWidget(btn_gen)
        ctx_layout.addWidget(btn_settings)
        layout.addWidget(ctx_group)

        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["English Word (คำเดิม)", "Thai Translation (คำแปลบังคับ)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        btn_add = QPushButton("➕ Add Row")
        btn_add.clicked.connect(lambda: self.add_row())
        btn_del = QPushButton("🗑 Delete Row")
        btn_del.clicked.connect(self.del_row)
        btn_save = QPushButton("💾 Save to Profile")
        btn_save.clicked.connect(self.save_glossary)
        btn_save.setStyleSheet("background: #a6e3a1; color: #1e1e2e; font-weight: bold; padding: 6px;")
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_del)
        btn_layout.addWidget(btn_save)
        layout.addLayout(btn_layout)
        
        self._is_modified = False
        self.table.itemChanged.connect(self.mark_modified)
        
        self.load_glossary()

    def mark_modified(self):
        self._is_modified = True

    def auto_generate_glossary(self):
        game_name = self.txt_game_name.text().strip()
        if not game_name:
            QMessageBox.warning(self, "Warning", "Please enter a game name first!")
            return
            
        cfg = TStudioCore.load_config()
        
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        self.setWindowTitle("📖 Glossary Editor - Generating... Please wait...")
        QApplication.processEvents()
        
        amount = self.spin_amount.value()
        prompt = f"List {amount} most common specific terminology, items, factions, or character roles in the video game '{game_name}'.\n" \
                 "Translate them from English to Thai in a way that fits the game's lore.\n" \
                 "Return the result STRICTLY as a JSON dictionary where keys are English words and values are Thai words. Example: {{\"Health Potion\": \"น้ำยาฟื้นพลัง\", \"Sword\": \"ดาบ\"}}\n" \
                 "Do not include any other text, markdown formatting, or explanations."
                 
        try:
            is_local = (cfg.get("provider", "") == "Local LLM" or cfg.get("model", "") == "custom-local-llm")
            res = CoreAI.generate_content(cfg, prompt, is_local=is_local)
            clean_res = re.sub(r'^```[^\n]*\n?|\n?```$', '', res.strip(), flags=re.MULTILINE)
            new_terms = json.loads(clean_res)
            
            for eng, thai in new_terms.items():
                self.add_row(eng, thai)
                
            QMessageBox.information(self, "Success", f"Glossary terms for '{game_name}' added successfully!\nYou can review them and click 'Save to Profile' to apply.")
        except Exception as e:
            QMessageBox.critical(self, "Failed", f"Error generating glossary:\n{e}")
        finally:
            QApplication.restoreOverrideCursor()
            self.setWindowTitle(f"📖 Glossary Editor (Editing: {self.active_profile})")

    def load_glossary(self):
        self.table.blockSignals(True)
        self.table.setRowCount(0)
        for wrong, right in self.profile_data.get("glossary", {}).items():
            self.add_row(wrong, right)
        self.table.blockSignals(False)
        self._is_modified = False

    def add_row(self, wrong="", right=""):
        self.table.blockSignals(True)
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(wrong))
        self.table.setItem(row, 1, QTableWidgetItem(right))
        self.table.blockSignals(False)
        self._is_modified = True

    def del_row(self):
        row = self.table.currentRow()
        if row >= 0:
            self.table.removeRow(row)
            self._is_modified = True

    def save_glossary(self):
        data = TStudioCore.load_profiles()
        if self.active_profile in data["presets"]:
            new_glossary = {}
            for r in range(self.table.rowCount()):
                w, c = self.table.item(r, 0), self.table.item(r, 1)
                if w and c and w.text().strip():
                    new_glossary[w.text().strip()] = c.text().strip()
            data["presets"][self.active_profile]["glossary"] = new_glossary
            TStudioCore.save_profiles(data)
            self._is_modified = False
            QMessageBox.information(self, "Saved", f"Glossary saved to profile '{self.active_profile}'!")
            self.accept()

    def closeEvent(self, event):
        if getattr(self, '_is_modified', False):
            reply = QMessageBox.question(self, 'Unsaved Changes', "You have unsaved changes in Glossary. Do you want to save them before closing?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
            if reply == QMessageBox.StandardButton.Yes:
                self.save_glossary()
                event.accept()
            elif reply == QMessageBox.StandardButton.No:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


class SmartImportDialog(QDialog):
    def __init__(self, headers, parent=None):
        super().__init__(parent)
        self.setWindowTitle("TFormat - Smart Import")
        self.resize(450, 300)
        self.headers = headers
        self.mapping = {}
        
        layout = QVBoxLayout(self)
        lbl_info = QLabel("⚠️ พบคอลัมน์ที่ไม่ตรงตามมาตรฐาน!\nโปรดจับคู่คอลัมน์ด้านล่างเพื่อให้ TFormat จัดระเบียบไฟล์ให้คุณ:")
        lbl_info.setStyleSheet("font-weight: bold; color: #f9e2af; font-size: 14px;")
        layout.addWidget(lbl_info)
        layout.addSpacing(10)
        
        form = QFormLayout()
        
        self.cbo_id = QComboBox()
        self.cbo_id.addItems(headers)
        
        self.cbo_src = QComboBox()
        self.cbo_src.addItems(headers)
        
        self.cbo_trans = QComboBox()
        self.cbo_trans.addItem("-- สร้างคอลัมน์แปลใหม่ (ว่างเปล่า) --")
        self.cbo_trans.addItems(headers)
        
        # Auto-guess logic
        for idx, h in enumerate(headers):
            hl = str(h).lower()
            if 'id' in hl or 'key' in hl: self.cbo_id.setCurrentIndex(idx)
            elif 'source' in hl or 'en' in hl or 'text' in hl or 'orig' in hl: self.cbo_src.setCurrentIndex(idx)
            elif 'trans' in hl or 'th' in hl or 'target' in hl: self.cbo_trans.setCurrentIndex(idx + 1)
            
        form.addRow("🔑 ID Column:", self.cbo_id)
        form.addRow("📄 Source Text:", self.cbo_src)
        form.addRow("🇹🇭 Translation (Optional):", self.cbo_trans)
        
        layout.addLayout(form)
        layout.addStretch()
        
        btn_box = QHBoxLayout()
        btn_ok = QPushButton("✅ จัดระเบียบไฟล์ (Format)")
        btn_ok.setStyleSheet("background: #a6e3a1; color: #1e1e2e; font-weight: bold; padding: 6px;")
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton("❌ ยกเลิก")
        btn_cancel.clicked.connect(self.reject)
        
        btn_box.addWidget(btn_cancel)
        btn_box.addWidget(btn_ok)
        layout.addLayout(btn_box)

    def get_mapping(self):
        trans_col = self.cbo_trans.currentText()
        if trans_col == "-- สร้างคอลัมน์แปลใหม่ (ว่างเปล่า) --":
            trans_col = None
            
        return {
            "id": self.cbo_id.currentText(),
            "source": self.cbo_src.currentText(),
            "trans": trans_col
        }

