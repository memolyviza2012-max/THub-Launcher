
try:
    from tstudio_i18n import _
except ImportError:
    try:
        from trun_i18n import _
    except ImportError:
        try:
            from i18n_helper import _
        except ImportError:
            _ = lambda x: x


import os
import json
import re
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QMessageBox, QLabel, QComboBox, 
    QLineEdit, QFileDialog, QDialog, QScrollArea, QButtonGroup, QRadioButton,
    QFormLayout, QTextEdit, QGroupBox, QSpinBox, QDoubleSpinBox, QApplication
)
from PyQt6.QtCore import Qt, QLocale, QThreadPool, QRunnable, pyqtSignal, QObject, pyqtSlot
from tstudio_core import TStudioCore, CoreAI, DEFAULT_SINGLE_PROMPT, DEFAULT_OPTIONS_PROMPT

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
        btn_ok = QPushButton(_("btn_use_selected"))
        btn_ok.setToolTip(_("tooltip_btn_ok"))
        btn_ok.clicked.connect(self.on_ok)
        btn_ok.setStyleSheet("background: #a6e3a1; color: #1e1e2e;")
        layout.addWidget(btn_ok)

    def on_ok(self):
        idx = self.bg.checkedId()
        if 0 <= idx < len(self.options):
            self.selected_text = self.options[idx]
        self.accept()

class WorkerSignals(QObject):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

class ThreadSafeWorkerSignalsForwarder(QObject):
    def __init__(self, on_success=None, on_error=None, parent=None):
        super().__init__(parent)
        self.on_success = on_success
        self.on_error = on_error

    @pyqtSlot(object)
    def handle_finished(self, val):
        try:
            if self.on_success:
                self.on_success(val)
        finally:
            self.deleteLater()

    @pyqtSlot(str)
    def handle_error(self, err_msg):
        try:
            if self.on_error:
                self.on_error(err_msg)
        finally:
            self.deleteLater()


class ApiWorker(QRunnable):
    _active_signals = set()
    
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        # Prevent premature garbage collection of signals
        ApiWorker._active_signals.add(self.signals)
        self.signals.finished.connect(self._cleanup)
        self.signals.error.connect(self._cleanup)

    def _cleanup(self, *args):
        try:
            ApiWorker._active_signals.remove(self.signals)
        except KeyError:
            pass

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
        self.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
        self.setFixedSize(450, 360)
        
        self.api_keys = {"Google Gemini": "", "Anthropic Claude": "", "DeepSeek": "", "OpenAI": ""}
        self.models_by_provider = {
            "Google Gemini": ["gemini-3.5-flash", "gemini-3.5-pro", "gemini-3.1-pro", "gemini-3-flash", "gemini-3.1-flash-lite", "gemini-2.5-flash", "gemini-2.5-pro"],
            "Anthropic Claude": ["claude-fable-5", "claude-mythos-5", "claude-opus-4.8", "claude-sonnet-4.6"],
            "DeepSeek": ["deepseek-chat", "deepseek-reasoner", "deepseek-v4-pro", "deepseek-v4-flash"],
            "OpenAI": ["gpt-5.5", "gpt-5.5-pro", "gpt-5.4", "gpt-5.4-pro", "gpt-5.4-mini", "gpt-5.4-nano", "gpt-4o", "gpt-4o-mini", "o3-mini"],
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
        
        self.txt_base_url = QLineEdit()
        self.txt_base_url.setPlaceholderText("Optional (e.g. OpenRouter URL)")
        self.lbl_base = QLabel("4. Base API URL:")
        form_layout.addRow(self.lbl_base, self.txt_base_url)

        self.spn_temp = QDoubleSpinBox()
        self.spn_temp.setRange(0.0, 2.0)
        self.spn_temp.setSingleStep(0.1)
        form_layout.addRow("5. Temperature:", self.spn_temp)

        self.spn_max_tokens = QSpinBox()
        self.spn_max_tokens.setRange(256, 128000)
        self.spn_max_tokens.setSingleStep(1024)
        form_layout.addRow("6. Max Tokens:", self.spn_max_tokens)

        self.spn_timeout = QSpinBox()
        self.spn_timeout.setRange(10, 600)
        self.spn_timeout.setSuffix(" sec")
        form_layout.addRow("7. Timeout:", self.spn_timeout)
        
        layout.addLayout(form_layout)
        layout.addStretch()
        
        btn_save = QPushButton(_("btn_save_settings"))
        btn_save.setToolTip(_("tooltip_btn_save"))
        btn_save.clicked.connect(self.save_config)
        layout.addWidget(btn_save)
        
        self.load_config()

    def _infer_provider(self, model):
        if model.startswith("gemini"): return "Google Gemini"
        if model.startswith("claude"): return "Anthropic Claude"
        if model.startswith("gpt") or model.startswith("o1") or model.startswith("o3") or model.startswith("o4"): return "OpenAI"
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
            self.txt_base_url.setPlaceholderText("http://localhost:1234/v1/chat/completions")
        else:
            self.txt_api.setEnabled(True)
            self.txt_api.setText(self.api_keys.get(new_provider, ""))
            self.lbl_api.setText(f"{new_provider} Key:")
            self.txt_base_url.setPlaceholderText("Optional (e.g. OpenRouter URL)")
            # Auto-clear localhost URL to prevent conflicts when switching to Cloud provider
            current_url = self.txt_base_url.text().strip().lower()
            if "localhost" in current_url or "127.0.0.1" in current_url:
                self.txt_base_url.clear()
            
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
            
            base_url = data.get("base_url", data.get("local_url", ""))
            self.txt_base_url.setText(base_url)
            self.spn_temp.setValue(float(data.get("temperature", 0.3)))
            self.spn_max_tokens.setValue(int(data.get("max_tokens", 4096)))
            self.spn_timeout.setValue(int(data.get("timeout", 30)))
            
            if provider != "Local LLM":
                self.txt_api.setText(self.api_keys.get(provider, ""))
        except Exception as e:
            print(f"UI load_config error: {e}")
            self.cbo_provider.setCurrentText("DeepSeek")
            self.cbo_model.setCurrentText("deepseek-chat")
            self.txt_base_url.setText("")
            self.spn_temp.setValue(0.3)
            self.spn_max_tokens.setValue(4096)
            self.spn_timeout.setValue(30)

    def save_config(self):
        if self.current_provider != "Local LLM":
            self.api_keys[self.current_provider] = self.txt_api.text()
            
        data = TStudioCore.load_config()
        
        data["google_key"] = self.api_keys["Google Gemini"].strip()
        data["anthropic_key"] = self.api_keys["Anthropic Claude"].strip()
        data["deepseek_key"] = self.api_keys["DeepSeek"].strip()
        data["openai_key"] = self.api_keys["OpenAI"].strip()
        data["api_key"] = self.api_keys["DeepSeek"].strip() # Backwards compatibility
        data["model"] = self.cbo_model.currentText().strip()
        data["provider"] = self.cbo_provider.currentText()
        data["base_url"] = self.txt_base_url.text().strip()
        data["local_url"] = data["base_url"] # For backwards compatibility
        data["temperature"] = self.spn_temp.value()
        data["max_tokens"] = self.spn_max_tokens.value()
        data["timeout"] = self.spn_timeout.value()
        
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
        self.resize(750, 850)
        
        main_layout = QVBoxLayout(self)
        
        # 1. Scrollable Interface
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; }")
        
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        
        # 2. Prompt Builder
        ctx_group = QGroupBox("✨ Auto-Generate Prompts for Game")
        ctx_layout = QVBoxLayout(ctx_group)
        
        row1 = QHBoxLayout()
        self.txt_game_name = QLineEdit()
        self.txt_game_name.setPlaceholderText("e.g. Elden Ring, The Sims, Cyberpunk 2077")
        
        self.txt_source_lang = QLineEdit()
        self.txt_source_lang.setPlaceholderText("Source (e.g. English)")
        
        self.txt_target_lang = QLineEdit()
        self.txt_target_lang.setPlaceholderText("Target (e.g. Thai)")
        _preset_name = self.profile_data.get("game_title", self.active_profile)
        if _preset_name and _preset_name != "Default":
            self.txt_game_name.setText(_preset_name)
        row1.addWidget(QLabel("Game Name:"))
        row1.addWidget(self.txt_game_name)
        
        self.cbo_tone = QComboBox()
        self.cbo_tone.setEditable(True)
        self.cbo_tone.addItems(["General/Default", "Fantasy RPG", "Sci-Fi / Cyberpunk", "Modern Casual", "Horror / Dark", "Formal / Polite"])
        row1.addWidget(QLabel("Tone/Style:"))
        row1.addWidget(self.cbo_tone)
        
        ctx_layout.addLayout(row1)
        
        row2 = QHBoxLayout()
        self.txt_rules = QLineEdit()
        self.txt_rules.setPlaceholderText("e.g. Do not translate character names, Keep UI terms in English")
        row2.addWidget(QLabel("Extra Rules:"))
        row2.addWidget(self.txt_rules)
        
        self.btn_gen = QPushButton(_("btn_auto_generate"))
        self.btn_gen.setToolTip(_("tooltip_btn_gen"))
        self.btn_gen.setStyleSheet("background: #f5c2e7; color: #1e1e2e; font-weight: bold; padding: 4px 8px;")
        self.btn_gen.clicked.connect(self.auto_generate_prompts)
        row2.addWidget(self.btn_gen)
        
        ctx_layout.addLayout(row2)
        layout.addWidget(ctx_group)

        self.txt_single = QTextEdit()
        self.txt_opt = QTextEdit()
        self.txt_batch = QTextEdit()
        
        # Helper to create insert buttons
        def create_insert_toolbar(target_txt):
            tb = QHBoxLayout()
            tb.setContentsMargins(0, 0, 0, 0)
            lbl = QLabel("Insert:")
            lbl.setStyleSheet("color: gray; font-size: 11px;")
            tb.addWidget(lbl)
            
            btn_src = QPushButton("{source_text}")
            btn_src.setToolTip(_("tooltip_btn_src"))
            btn_src.setStyleSheet("padding: 2px 6px; font-size: 11px; background: #313244;")
            btn_src.clicked.connect(lambda: target_txt.insertPlainText("{source_text}"))
            tb.addWidget(btn_src)
            
            btn_id = QPushButton("{id}")
            btn_id.setToolTip(_("tooltip_btn_id"))
            btn_id.setStyleSheet("padding: 2px 6px; font-size: 11px; background: #313244;")
            btn_id.clicked.connect(lambda: target_txt.insertPlainText("{id}"))
            tb.addWidget(btn_id)
            
            tb.addStretch()
            return tb

        grp1 = QGroupBox("1. Single Translation Prompt (TStudio)")
        l1 = QVBoxLayout(grp1)
        l1.addWidget(QLabel("Use {id} and {source_text} in your prompt."))
        l1.addLayout(create_insert_toolbar(self.txt_single))
        l1.addWidget(self.txt_single)
        layout.addWidget(grp1)

        grp2 = QGroupBox("2. Three Options Prompt (TStudio)")
        l2 = QVBoxLayout(grp2)
        l2.addWidget(QLabel("Must return exactly 3 JSON strings: [\"A\", \"B\", \"C\"]"))
        l2.addLayout(create_insert_toolbar(self.txt_opt))
        l2.addWidget(self.txt_opt)
        layout.addWidget(grp2)
        
        grp3 = QGroupBox("3. Batch Translation Prompt (TRun)")
        l3 = QVBoxLayout(grp3)
        l3.addWidget(QLabel("Use {source_text} in your prompt for bulk translation."))
        l3.addLayout(create_insert_toolbar(self.txt_batch))
        l3.addWidget(self.txt_batch)
        layout.addWidget(grp3)
        
        # QA Settings
        grp_qa = QGroupBox("✅ QA Checker Settings")
        l_qa = QHBoxLayout(grp_qa)
        l_qa.addWidget(QLabel("Max Byte Limit (e.g. for Asian fonts 21/63 bytes):"))
        self.spin_qa_bytes = QSpinBox()
        self.spin_qa_bytes.setRange(0, 9999)
        self.spin_qa_bytes.setValue(self.profile_data.get("max_bytes_limit", 63))
        self.spin_qa_bytes.setToolTip("Sets the maximum allowed bytes for Thai text to prevent game crashes (0 = unlimited).")
        self.spin_qa_bytes.valueChanged.connect(self.mark_modified)
        l_qa.addWidget(self.spin_qa_bytes)
        l_qa.addStretch()
        layout.addWidget(grp_qa)

        
        # Live Tester
        grp_test = QGroupBox("🧪 Test Your Prompt (Live Tester)")
        l_test = QVBoxLayout(grp_test)
        row_t1 = QHBoxLayout()
        row_t1.addWidget(QLabel("Test Input:"))
        self.txt_test_input = QLineEdit()
        self.txt_test_input.setText("Hello wanderer, welcome to the shop. What can I get for you today?")
        row_t1.addWidget(self.txt_test_input)
        
        btn_test_single = QPushButton("Test Single")
        btn_test_single.setToolTip(_("tooltip_btn_test_single"))
        btn_test_single.clicked.connect(lambda: self.run_live_test("single"))
        row_t1.addWidget(btn_test_single)
        
        btn_test_opt = QPushButton("Test Options")
        btn_test_opt.setToolTip(_("tooltip_btn_test_opt"))
        btn_test_opt.clicked.connect(lambda: self.run_live_test("opt"))
        row_t1.addWidget(btn_test_opt)
        l_test.addLayout(row_t1)
        
        self.txt_test_result = QTextEdit()
        self.txt_test_result.setReadOnly(True)
        self.txt_test_result.setFixedHeight(60)
        self.txt_test_result.setPlaceholderText("Translation result will appear here...")
        l_test.addWidget(self.txt_test_result)
        layout.addWidget(grp_test)
        
        self.scroll.setWidget(content_widget)
        main_layout.addWidget(self.scroll)

        # Bottom Buttons
        btn_layout = QHBoxLayout()
        
        from PyQt6.QtWidgets import QToolButton, QMenu
        self.btn_template = QToolButton()
        self.btn_template.setText("📚 Load Template...")
        self.btn_template.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.btn_template.setStyleSheet("background: #cba6f7; color: #1e1e2e; font-weight: bold; padding: 6px 12px;")
        
        menu_tpl = QMenu(self)
        menu_tpl.addAction("1. Default (TStudio Base)", lambda: self.load_template("default"))
        menu_tpl.addAction("2. Story & Dialogue (Creative & Emotional)", lambda: self.load_template("story"))
        menu_tpl.addAction("3. UI & Menus (Short & Literal)", lambda: self.load_template("ui"))
        menu_tpl.addAction("4. Strict / Direct Translation", lambda: self.load_template("strict"))
        self.btn_template.setMenu(menu_tpl)
        btn_layout.addWidget(self.btn_template)
        
        btn_settings = QPushButton(_("btn_ai_settings"))
        btn_settings.clicked.connect(lambda: SettingsDialog(self).exec())
        btn_settings.setToolTip(_("tooltip_btn_ai_settings"))
        btn_layout.addWidget(btn_settings)
        
        btn_layout.addStretch()
        
        btn_save = QPushButton(_("btn_save_to_profile"))
        btn_save.setToolTip(_("tooltip_btn_save"))
        btn_save.setStyleSheet("background: #a6e3a1; color: #1e1e2e; font-weight: bold; padding: 6px 12px;")
        btn_save.clicked.connect(self.save_current_preset)
        btn_layout.addWidget(btn_save)
        
        main_layout.addLayout(btn_layout)
        
        self.txt_single.setPlainText(self.profile_data.get("single", DEFAULT_SINGLE_PROMPT))
        self.txt_opt.setPlainText(self.profile_data.get("opt", DEFAULT_OPTIONS_PROMPT))
        self.txt_batch.setPlainText(self.profile_data.get("batch", self.profile_data.get("single", DEFAULT_SINGLE_PROMPT)))
        
        self._is_modified = False
        self.txt_single.textChanged.connect(self.mark_modified)
        self.txt_opt.textChanged.connect(self.mark_modified)
        self.txt_batch.textChanged.connect(self.mark_modified)

    def mark_modified(self):
        self._is_modified = True

    def load_template(self, tpl_type):
        msg = QMessageBox(self)
        msg.setWindowTitle("Load Template")
        msg.setText("This will overwrite your current prompts. Continue?")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if msg.exec() == QMessageBox.StandardButton.Yes:
            from tstudio_core import DEFAULT_SINGLE_PROMPT, DEFAULT_OPTIONS_PROMPT
            
            if tpl_type == "default":
                self.txt_single.setPlainText(DEFAULT_SINGLE_PROMPT)
                self.txt_opt.setPlainText(DEFAULT_OPTIONS_PROMPT)
                self.txt_batch.setPlainText(DEFAULT_SINGLE_PROMPT)
            elif tpl_type == "story":
                sys = "You are a creative writer and game localization expert. Translate the following video game dialogue/story text into Thai.\nFocus on natural flow, emotional resonance, and fitting character voices.\nUse {id} and {source_text}."
                self.txt_single.setPlainText(sys + "\n\n- Return ONLY the Thai string.")
                self.txt_opt.setPlainText(sys + "\n\n- Return exactly 3 slightly different emotional/creative options as a JSON array of strings.")
                self.txt_batch.setPlainText(sys + "\n\n- Return ONLY the Thai string.")
            elif tpl_type == "ui":
                sys = "You are a UI/UX localization expert. Translate the following game interface text into Thai.\nKeep the translation as short, concise, and literal as possible to fit UI buttons.\nUse {id} and {source_text}."
                self.txt_single.setPlainText(sys + "\n\n- Return ONLY the Thai string.")
                self.txt_opt.setPlainText(sys + "\n\n- Return exactly 3 concise options as a JSON array of strings.")
                self.txt_batch.setPlainText(sys + "\n\n- Return ONLY the Thai string.")
            elif tpl_type == "strict":
                sys = "Translate the following {source_text} into Thai directly and literally.\nDo not adapt, localize, or add creative flair.\nReturn ONLY the pure Thai string."
                self.txt_single.setPlainText(sys)
                self.txt_opt.setPlainText("Translate {source_text} into Thai.\nReturn exactly 3 literal translation options as a JSON array of strings.")
                self.txt_batch.setPlainText(sys)

    def auto_generate_prompts(self):
        game_name = self.txt_game_name.text().strip()
        if not game_name:
            QMessageBox.warning(self, "Warning", "Please enter a game name first!")
            return
            
        data = TStudioCore.load_profiles()
        if self.active_profile in data["presets"]:
            data["presets"][self.active_profile]["game_title"] = game_name
            data["presets"][self.active_profile]["source_language"] = self.txt_source_lang.text().strip()
            data["presets"][self.active_profile]["target_language"] = self.txt_target_lang.text().strip()
            TStudioCore.save_profiles(data)
            self.profile_data = data["presets"][self.active_profile]
            
        tone = self.cbo_tone.currentText().strip()
        rules = self.txt_rules.text().strip()

        data = TStudioCore.load_profiles()
        if self.active_profile in data["presets"]:
            data["presets"][self.active_profile]["game_title"] = game_name
            data["presets"][self.active_profile]["source_language"] = self.txt_source_lang.text().strip()
            data["presets"][self.active_profile]["target_language"] = self.txt_target_lang.text().strip()
            TStudioCore.save_profiles(data)
            self.profile_data = data["presets"][self.active_profile]

        cfg = TStudioCore.load_config()
        
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        self.btn_gen.setText("⏳ Generating...")
        self.btn_gen.setEnabled(False)
        self.setWindowTitle("⚙️ Prompt Settings - Generating... Please wait...")
        QApplication.processEvents()
        
        sys_msg = f"You are an expert prompt engineer. Create a system prompt for translating the video game '{game_name}' from English to Thai. The prompt MUST include the literal text '{{id}}' and '{{source_text}}'. Respond with ONLY the raw prompt string, no quotes, no markdown."
        
        req_single = f"\n\nRequirements for the output prompt:\n1. Instruct the AI to return ONLY the pure Thai string translation of {{source_text}}.\n2. Specify the tone relevant to {game_name}.\n3. MUST explicitly instruct the AI to NOT include the Context ID ({{id}}) in its output.\n4. MUST explicitly instruct the AI to preserve all UI/game tags like {{...}}, [...], <...> exactly as they appear."
        req_opt = f"\n\nRequirements for the output prompt:\n1. Instruct the AI to return exactly 3 different Thai translation options for {{source_text}}.\n2. The options must vary slightly in tone, while remaining fitting for {game_name}.\n3. The output MUST be a strict JSON array of 3 strings.\n4. MUST explicitly instruct the AI to NOT include the Context ID ({{id}}) in its output.\n5. MUST explicitly instruct the AI to preserve all UI/game tags like {{...}}, [...], <...> exactly as they appear."
        
        if tone and tone.lower() != "general/default":
            req_single += f"\n5. The translation MUST strictly follow this Tone/Style: '{tone}'."
            req_opt += f"\n6. The translation MUST strictly follow this Tone/Style: '{tone}'."
            
        if rules:
            req_single += f"\n4. The prompt MUST explicitly command the AI to obey these rules: '{rules}'."
            req_opt += f"\n5. The prompt MUST explicitly command the AI to obey these rules: '{rules}'."
            
        prompt_single = sys_msg + req_single
        prompt_opt = sys_msg + req_opt
        
        is_local = (cfg.get("provider", "") == "Local LLM" or cfg.get("model", "") == "custom-local-llm")
        
        def run_both():
            r_single = CoreAI.generate_content(cfg, prompt_single, is_local=is_local)
            r_opt = CoreAI.generate_content(cfg, prompt_opt, is_local=is_local)
            return r_single, r_opt
            
        def on_success(res):
            try:
                self.isVisible()  # Guard: raises RuntimeError if C++ object is deleted
            except RuntimeError:
                return
            res_single, res_opt = res
            self.txt_single.setPlainText(res_single.strip().strip('`').strip())
            self.txt_opt.setPlainText(res_opt.strip().strip('`').strip())
            self.txt_batch.setPlainText(res_single.strip().strip('`').strip())
            self.btn_gen.setText("✨ Auto-Generate")
            self.btn_gen.setEnabled(True)
            QApplication.restoreOverrideCursor()
            self.setWindowTitle(f"⚙️ Prompt Settings (Editing: {self.active_profile})")
            QMessageBox.information(self, "Success", f"Prompts for '{game_name}' generated successfully!\nDon't forget to click 'Save to Profile' to keep them.")
            
        def on_error(err):
            try:
                self.isVisible()  # Guard: raises RuntimeError if C++ object is deleted
            except RuntimeError:
                return
            self.btn_gen.setText("✨ Auto-Generate")
            self.btn_gen.setEnabled(True)
            QApplication.restoreOverrideCursor()
            self.setWindowTitle(f"⚙️ Prompt Settings (Editing: {self.active_profile})")
            QMessageBox.critical(self, "Failed", f"Error generating prompts:\n{err}")
            
        worker = ApiWorker(run_both)
        worker.signals.finished.connect(on_success)
        worker.signals.error.connect(on_error)
        QThreadPool.globalInstance().start(worker)

    def run_live_test(self, mode):
        test_text = self.txt_test_input.text().strip()
        if not test_text:
            QMessageBox.warning(self, "Warning", "Please enter some test input first.")
            return
            
        prompt_template = self.txt_single.toPlainText() if mode == "single" else self.txt_opt.toPlainText()
        if "{source_text}" not in prompt_template:
            QMessageBox.warning(self, "Warning", "Your prompt does not contain '{source_text}', so the AI won't receive your test input!")
            return
            
        final_prompt = prompt_template.replace("{source_text}", test_text).replace("{id}", "TEST_001")
        
        self.txt_test_result.setPlainText("Translating... please wait.")
        cfg = TStudioCore.load_config()
        is_local = (cfg.get("provider", "") == "Local LLM" or cfg.get("model", "") == "custom-local-llm")
        
        def do_translate():
            return CoreAI.generate_content(cfg, final_prompt, is_local=is_local)
            
        def on_success(res):
            try:
                self.isVisible()  # Guard: raises RuntimeError if C++ object is deleted
            except RuntimeError:
                return
            self.txt_test_result.setPlainText(res.strip())
            
        def on_error(err):
            try:
                self.isVisible()  # Guard: raises RuntimeError if C++ object is deleted
            except RuntimeError:
                return
            self.txt_test_result.setPlainText(f"Error: {err}")
            
        worker = ApiWorker(do_translate)
        worker.signals.finished.connect(on_success)
        worker.signals.error.connect(on_error)
        QThreadPool.globalInstance().start(worker)

    def save_current_preset(self):
        s1 = self.txt_single.toPlainText()
        s2 = self.txt_opt.toPlainText()
        
        if "{source_text}" not in s1 or "{source_text}" not in s2:
            reply = QMessageBox.warning(self, "Missing {source_text}", "Your prompt is missing the '{source_text}' tag. The AI will not know what to translate.\n\nAre you sure you want to save anyway?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
                return

        data = TStudioCore.load_profiles()
        if self.active_profile in data["presets"]:
            data["presets"][self.active_profile]["single"] = s1
            data["presets"][self.active_profile]["opt"] = s2
            data["presets"][self.active_profile]["batch"] = self.txt_batch.toPlainText()
            data["presets"][self.active_profile]["max_bytes_limit"] = self.spin_qa_bytes.value()
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

GLOSSARY_TAGS = ['General', 'Person', 'Location', 'Weapon', 'Item', 'Faction', 'Quest', 'Other']

from PyQt6.QtWidgets import QStyledItemDelegate

class TagColumnDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        combo = QComboBox(parent)
        combo.addItems(GLOSSARY_TAGS)
        return combo

    def setEditorData(self, editor, index):
        text = index.model().data(index, Qt.ItemDataRole.EditRole) or ""
        if text in GLOSSARY_TAGS:
            editor.setCurrentText(text)
        else:
            editor.setCurrentText("General")

    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentText(), Qt.ItemDataRole.EditRole)

    def paint(self, painter, option, index):
        # Draw standard item background (selection highlight, hover states, etc.)
        self.parent().style().drawControl(
            self.parent().style().ControlElement.CE_ItemViewItem,
            option, painter, self.parent()
        )
        
        text = index.model().data(index, Qt.ItemDataRole.DisplayRole)
        if not text:
            return
            
        painter.save()
        painter.setRenderHint(painter.RenderHint.Antialiasing)
        
        # Color mapping for tags
        tag_colors = {
            "Weapon": ("#f38ba8", "#11111b"),
            "Faction": ("#cba6f7", "#11111b"),
            "Person": ("#fab387", "#11111b"),
            "Location": ("#a6e3a1", "#11111b"),
            "Item": ("#89b4fa", "#11111b"),
            "Quest": ("#f9e2af", "#11111b"),
            "General": ("#45475a", "#cdd6f4"),
            "Other": ("#585b70", "#cdd6f4")
        }
        
        bg_color_str, text_color_str = tag_colors.get(text, ("#585b70", "#cdd6f4"))
        
        from PyQt6.QtGui import QColor, QBrush, QPen
        bg_color = QColor(bg_color_str)
        text_color = QColor(text_color_str)
        
        # Calculate badge bounds inside the cell
        rect = option.rect
        margin_h = 10
        margin_v = 4
        
        badge_width = min(80, rect.width() - (margin_h * 2))
        badge_height = rect.height() - (margin_v * 2)
        badge_x = rect.x() + (rect.width() - badge_width) // 2
        badge_y = rect.y() + margin_v
        
        from PyQt6.QtCore import QRect
        badge_rect = QRect(badge_x, badge_y, badge_width, badge_height)
        
        # Draw pill background
        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(badge_rect, 8, 8)
        
        # Draw tag text
        painter.setPen(QPen(text_color))
        font = painter.font()
        font.setPointSize(9)
        font.setBold(True)
        painter.setFont(font)
        
        painter.drawText(badge_rect, Qt.AlignmentFlag.AlignCenter, text)
        painter.restore()

class GlossaryWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_profile = TStudioCore.load_profiles()["active_preset"]
        self.profile_data = TStudioCore.get_current_profile_data()
        
        self.setWindowTitle(f"📖 Glossary Editor (Editing: {self.active_profile})")
        self.setMinimumWidth(300)
        layout = QVBoxLayout(self)

        ctx_group = QGroupBox("TLM Context & Glossary Extraction")
        ctx_group.setCheckable(True)
        ctx_group.setChecked(False) # Collapsed by default as requested
        
        ctx_main_layout = QVBoxLayout(ctx_group)
        ctx_main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.ctx_container = QWidget()
        ctx_layout = QVBoxLayout(self.ctx_container)
        ctx_layout.setContentsMargins(5, 5, 5, 5)
        
        from PyQt6.QtWidgets import QSizePolicy
        ctx_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        
        from PyQt6.QtWidgets import QGridLayout
        grid = QGridLayout()
        grid.setSpacing(6)
        
        self.txt_game_name = QLineEdit()
        self.txt_game_name.setPlaceholderText("Game Name")
        
        self.txt_source_lang = QLineEdit()
        self.txt_source_lang.setPlaceholderText("Source (e.g. English)")
        
        self.txt_target_lang = QLineEdit()
        self.txt_target_lang.setPlaceholderText("Target (e.g. Thai)")
        _preset_name = self.profile_data.get("game_title", self.active_profile)
        if _preset_name and _preset_name != "Default":
            self.txt_game_name.setText(_preset_name)
            
        self.cbo_category = QComboBox()
        self.cbo_category.setEditable(True)
        self.cbo_category.addItems(["General", "Characters & NPCs", "Locations & World", "Items & Weapons", "Factions & Lore", "UI & Menus"])
        
        self.spin_amount = QSpinBox()
        self.spin_amount.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
        self.spin_amount.setRange(1, 100)
        self.spin_amount.setValue(30)
        self.spin_amount.setMinimumWidth(60)
        
        self.btn_gen = QPushButton(_("btn_extract"))
        self.btn_gen.setToolTip(_("tooltip_btn_extract"))
        self.btn_gen.setStyleSheet("background-color: #cba6f7; color: #1e1e2e; font-weight: bold; border-radius: 4px; padding: 4px 12px; min-height: 22px;")
        self.btn_gen.clicked.connect(self.auto_generate_glossary)
        self.btn_gen.setToolTip("สกัดคำศัพท์ที่พบบ่อยจากเกมนี้ และแปลอัตโนมัติด้วย AI")
        
        # Game Title Column
        grid.addWidget(QLabel("Game Title"), 0, 0)
        grid.addWidget(self.txt_game_name, 1, 0)
        
        # Category Column
        grid.addWidget(QLabel("Category"), 0, 1)
        grid.addWidget(self.cbo_category, 1, 1)
        
        # Amount Column
        grid.addWidget(QLabel("Amount"), 0, 2)
        grid.addWidget(self.spin_amount, 1, 2)
        
        # Extract Button
        grid.addWidget(self.btn_gen, 1, 3)
        
        grid.setColumnStretch(0, 3)
        grid.setColumnStretch(1, 2)
        grid.setColumnStretch(2, 1)
        grid.setColumnStretch(3, 1)
        
        self.txt_tlm_context = QTextEdit()
        self.txt_tlm_context.setPlaceholderText("Paste game lore, wiki, or dialog text here... (Optional)")
        self.txt_tlm_context.setMaximumHeight(50)
        
        ctx_layout.addLayout(grid)
        ctx_layout.addWidget(self.txt_tlm_context)
        
        ctx_main_layout.addWidget(self.ctx_container)
        ctx_group.toggled.connect(self.ctx_container.setVisible)
        self.ctx_container.setVisible(ctx_group.isChecked())
        
        layout.addWidget(ctx_group)

        # Search & Filter Bar
        search_layout = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search...")
        self.search_box.setToolTip("พิมพ์คำศัพท์เพื่อค้นหา")
        self.search_box.textChanged.connect(self.filter_glossary)
        search_layout.addWidget(self.search_box, 3)
        
        search_layout.addWidget(QLabel("Tag:"))
        self.combo_filter_tag = QComboBox()
        self.combo_filter_tag.addItems(["All"] + GLOSSARY_TAGS)
        self.combo_filter_tag.currentTextChanged.connect(self.filter_glossary)
        search_layout.addWidget(self.combo_filter_tag, 1)
        
        btn_settings = QPushButton("⚙️")
        btn_settings.clicked.connect(lambda: SettingsDialog(self).exec())
        btn_settings.setToolTip(_("tooltip_btn_ai_settings"))
        btn_settings.setStyleSheet("background-color: #313244; color: #cdd6f4; border: 1px solid #45475a; border-radius: 4px; padding: 4px 8px; min-height: 22px; font-size: 14px;")
        search_layout.addWidget(btn_settings)
        
        layout.addLayout(search_layout)

        self.table = QTableWidget(0, 3)
        self.table.setItemDelegateForColumn(2, TagColumnDelegate(self))
        self.table.setHorizontalHeaderLabels([_("glossary_col_word"), _("glossary_col_thai"), _("glossary_col_tag")])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.table)

        btn_add = QPushButton(_("btn_add_row"))
        btn_add.setToolTip(_("tooltip_btn_add"))
        btn_add.clicked.connect(lambda: self.add_row())
        btn_add.setStyleSheet("background-color: #313244; color: #cdd6f4; border: 1px solid #45475a; border-radius: 4px; padding: 4px 8px; min-height: 22px;")
        
        btn_auto_tag = QPushButton(_("btn_auto_tag"))
        btn_auto_tag.setStyleSheet("background-color: #89b4fa; color: #1e1e2e; font-weight: bold; border-radius: 4px; padding: 4px 8px; min-height: 22px;")
        btn_auto_tag.setToolTip(_("tooltip_btn_auto_tag"))
        btn_auto_tag.clicked.connect(self.auto_tag_general_rows)
        btn_auto_tag.setToolTip("ใช้ AI ช่วยจัดหมวดหมู่ (Tag) คำศัพท์อัตโนมัติ")
        
        from PyQt6.QtWidgets import QToolButton, QMenu
        self.btn_retrans = QToolButton()
        self.btn_retrans.setText(_("btn_retranslate"))
        self.btn_retrans.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.btn_retrans.setStyleSheet("QToolButton { background-color: #f9e2af; color: #1e1e2e; font-weight: bold; border-radius: 4px; padding: 4px 8px; min-height: 22px; } QToolButton::menu-button { border: none; }")
        menu_retrans = QMenu(self)
        act_opt = menu_retrans.addAction(_("menu_gen_3_options"))
        act_opt.triggered.connect(self.retranslate_options)
        act_custom = menu_retrans.addAction(_("menu_custom_trans"))
        act_custom.triggered.connect(self.retranslate_custom)
        
        menu_retrans.addSeparator()
        menu_retrans.addAction(_("menu_transliterate")).triggered.connect(lambda: self.retranslate_special("transliterate"))
        menu_retrans.addAction(_("menu_idiom")).triggered.connect(lambda: self.retranslate_special("idiom"))
        menu_retrans.addAction(_("menu_poem")).triggered.connect(lambda: self.retranslate_special("poem"))
        menu_retrans.addAction(_("menu_quote")).triggered.connect(lambda: self.retranslate_special("quote"))
        menu_retrans.addSeparator()
        menu_retrans.addAction(_("menu_mature")).triggered.connect(lambda: self.retranslate_special("mature"))
        menu_retrans.addAction(_("menu_fantasy")).triggered.connect(lambda: self.retranslate_special("fantasy"))
        menu_retrans.addAction(_("menu_robotic")).triggered.connect(lambda: self.retranslate_special("robotic"))
        menu_retrans.addAction(_("menu_casual")).triggered.connect(lambda: self.retranslate_special("casual"))
        self.btn_retrans.setMenu(menu_retrans)
        self.btn_retrans.setToolTip(_("tooltip_btn_retranslate"))
        
        btn_del = QPushButton(_("btn_delete_row"))
        btn_del.clicked.connect(self.del_row)
        btn_del.setToolTip(_("tooltip_btn_delete_row"))
        btn_del.setStyleSheet("background-color: #313244; color: #cdd6f4; border: 1px solid #45475a; border-radius: 4px; padding: 4px 8px; min-height: 22px;")
        
        btn_save = QPushButton(_("btn_save_to_profile"))
        btn_save.clicked.connect(lambda: self.save_glossary(True))
        btn_save.setToolTip(_("tooltip_btn_save_glossary"))
        btn_save.setStyleSheet("background-color: #a6e3a1; color: #1e1e2e; font-weight: bold; border-radius: 4px; padding: 4px 8px; min-height: 22px;")
        
        btn_export = QPushButton(_("btn_export"))
        btn_export.clicked.connect(self.export_glossary)
        btn_export.setToolTip(_("tooltip_btn_export_glossary"))
        btn_export.setStyleSheet("background-color: #313244; color: #cdd6f4; border: 1px solid #45475a; border-radius: 4px; padding: 4px 8px; min-height: 22px;")
        
        btn_import = QPushButton("📥 Import")
        btn_import.clicked.connect(self.import_glossary)
        btn_import.setToolTip("นำเข้า Glossary จากไฟล์ JSON (รวมเข้ากับของเดิม)")
        btn_import.setStyleSheet("background-color: #313244; color: #cdd6f4; border: 1px solid #45475a; border-radius: 4px; padding: 4px 8px; min-height: 22px;")
        
        btn_layout_top = QHBoxLayout()
        btn_layout_top.setSpacing(6)
        btn_layout_top.addWidget(btn_add)
        btn_layout_top.addWidget(btn_auto_tag)
        btn_layout_top.addWidget(btn_del)
        
        btn_layout_bottom = QHBoxLayout()
        btn_layout_bottom.setSpacing(6)
        btn_layout_bottom.addWidget(btn_import)
        btn_layout_bottom.addWidget(btn_export)
        btn_layout_bottom.addWidget(self.btn_retrans)
        btn_layout_bottom.addWidget(btn_save)
        
        btn_container = QVBoxLayout()
        btn_container.setSpacing(4)
        btn_container.addLayout(btn_layout_top)
        btn_container.addLayout(btn_layout_bottom)
        layout.addLayout(btn_container)
        
        self._is_modified = False
        
        # Setup auto-save timer
        from PyQt6.QtCore import QTimer
        self.save_timer = QTimer(self)
        self.save_timer.setSingleShot(True)
        self.save_timer.timeout.connect(lambda: self.save_glossary(show_msg=False))
        
        self.table.itemChanged.connect(self.mark_modified)
        self.load_glossary()


    def mark_modified(self):
        self._is_modified = True
        if hasattr(self, 'save_timer'):
            self.save_timer.start(500) # Auto-save 500ms after user stops typing

    def filter_glossary(self, *args, **kwargs):
        search_text = self.search_box.text().lower()
            
        filter_tag = self.combo_filter_tag.currentText()
        
        for row in range(self.table.rowCount()):
            item_en = self.table.item(row, 0)
            item_th = self.table.item(row, 1)
            en_text = item_en.text().lower() if item_en else ""
            th_text = item_th.text().lower() if item_th else ""
            
            item_tag = self.table.item(row, 2)
            row_tag = item_tag.text() if item_tag else "General"
            
            match_text = search_text in en_text or search_text in th_text
            match_tag = (filter_tag == "All") or (filter_tag == row_tag)
            
            self.table.setRowHidden(row, not (match_text and match_tag))

    def auto_generate_glossary(self):
        import json, re
        game_name = self.txt_game_name.text().strip()
        if not game_name:
            QMessageBox.warning(self, "Warning", "Please enter a game name first!")
            return
            
        data = TStudioCore.load_profiles()
        if self.active_profile in data["presets"]:
            data["presets"][self.active_profile]["game_title"] = game_name
            data["presets"][self.active_profile]["source_language"] = self.txt_source_lang.text().strip()
            data["presets"][self.active_profile]["target_language"] = self.txt_target_lang.text().strip()
            TStudioCore.save_profiles(data)
            self.profile_data = data["presets"][self.active_profile]

        cfg = TStudioCore.load_config()
        
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        self.btn_gen.setText("⏳ Generating...")
        self.btn_gen.setEnabled(False)
        self.setWindowTitle("🧠 TLM Extractor - Generating... Please wait...")
        QApplication.processEvents()
        
        amount = self.spin_amount.value()
        category_text = self.cbo_category.currentText().strip()
        cat_prompt_part = f"specifically in the category of '{category_text}'" if category_text and category_text.lower() != "general" else "including terminology, items, factions, or character names"
        
        existing_words = []
        for r in range(self.table.rowCount()):
            item_en = self.table.item(r, 0)
            if item_en and item_en.text().strip():
                existing_words.append(item_en.text().strip())
                
        anti_dup_prompt = ""
        if existing_words:
            anti_dup_prompt = f"\nCRITICAL: Do NOT extract any of the following terminology, as they already exist in the glossary:\n{json.dumps(existing_words, ensure_ascii=False)}\n"
            
        tlm_text = self.txt_tlm_context.toPlainText().strip()
        if tlm_text:
            prompt = f"You are a video game localization expert. Your task is to extract exactly {amount} key terminology (names, places, items) from the following context for the game '{game_name}'.\n\n--- CONTEXT ---\n{tlm_text[:8000]}\n---------------\n\n" \
                     f"{anti_dup_prompt}" \
                     "You MUST output ONLY a valid JSON array. Do not use any nested objects. Each object in the array must have exactly three string keys: 'en', 'th', and 'tag'.\n" \
                     "- 'en': The English word.\n" \
                     "- 'th': The Thai translation.\n" \
                     "- 'tag': MUST be exactly one of the following words: General, Person, Location, Weapon, Item, Faction, Quest, Other.\n" \
                     "Output ONLY the JSON array. Do NOT output markdown formatting like ```json."
        else:
            prompt = f"You are a video game localization expert. Your task is to extract exactly {amount} most common terminology for the game '{game_name}', {cat_prompt_part}.\n" \
                     f"{anti_dup_prompt}" \
                     "You MUST output ONLY a valid JSON array. Do not use any nested objects. Each object in the array must have exactly three string keys: 'en', 'th', and 'tag'.\n" \
                     "- 'en': The English word.\n" \
                     "- 'th': The Thai translation.\n" \
                     "- 'tag': MUST be exactly one of the following words: General, Person, Location, Weapon, Item, Faction, Quest, Other.\n" \
                     "Example of expected output:\n" \
                     '[\n  {"en": "Health Potion", "th": "ยาฟื้นฟูพลังชีวิต", "tag": "Item"},\n  {"en": "Sword", "th": "ดาบ", "tag": "Weapon"}\n]\n' \
                     "Output ONLY the JSON array. Do NOT output markdown formatting like ```json."
                 
        is_local = (cfg.get("provider", "") == "Local LLM" or cfg.get("model", "") == "custom-local-llm")
        
        def do_gen():
            from tstudio_core import CoreAI
            return CoreAI.generate_content(cfg, prompt, is_local=is_local)
            
        def on_success(res):
            try:
                self.isVisible()  # Guard: raises RuntimeError if C++ object is deleted
            except RuntimeError:
                QApplication.restoreOverrideCursor()
                return
            try:
                import re, json
                match = re.search(r'\[.*\]', res, re.DOTALL)
                if match:
                    clean_res = match.group(0)
                else:
                    clean_res = re.sub(r'^```[^\n]*\n?|\n?```$', '', res.strip(), flags=re.MULTILINE)
                    
                new_terms = json.loads(clean_res)
                
                if isinstance(new_terms, dict):
                    raise Exception("AI returned a JSON Dictionary instead of an Array.")
                if not isinstance(new_terms, list):
                    raise Exception("AI did not return a JSON Array.")
                
                self.merge_new_terms(new_terms, game_name)
                
                self.btn_gen.setText("🧠 Extract from TLM")
                self.btn_gen.setEnabled(True)
                QApplication.restoreOverrideCursor()
                self.setWindowTitle(f"🧠 TLM Extractor")
            except Exception as e:
                on_error(f"Data parsing error: {e}\n\nRaw Response:\n{res[:200]}...")
                
        def on_error(err):
            try:
                self.isVisible()  # Guard: raises RuntimeError if C++ object is deleted
            except RuntimeError:
                QApplication.restoreOverrideCursor()
                return
            self.btn_gen.setText("🧠 Extract from TLM")
            self.btn_gen.setEnabled(True)
            QApplication.restoreOverrideCursor()
            self.setWindowTitle(f"🧠 TLM Extractor")
            QMessageBox.critical(self, "Failed", f"Error generating glossary:\n{err}")
            
        worker = ApiWorker(do_gen)
        forwarder = ThreadSafeWorkerSignalsForwarder(on_success, on_error, self)
        worker.signals.finished.connect(forwarder.handle_finished)
        worker.signals.error.connect(forwarder.handle_error)
        QThreadPool.globalInstance().start(worker)

    def merge_new_terms(self, new_terms, game_name=""):
        added_count = 0
        merged_count = 0
        
        # Pre-fetch existing glossary items for deduplication
        existing_terms = {}
        for r in range(self.table.rowCount()):
            item_en = self.table.item(r, 0)
            item_th = self.table.item(r, 1)
            if item_en and item_th:
                existing_terms[item_en.text().strip().lower()] = (r, item_th.text().strip())
                
        for item in new_terms:
            if not isinstance(item, dict): continue
            en = item.get("en", "").strip()
            th = item.get("th", "").strip()
            tag = item.get("tag", "General")
            if not en or not th: continue
            
            en_lower = en.lower()
            if en_lower in existing_terms:
                # Collision! Check if Thai translation is different
                row_idx, old_th = existing_terms[en_lower]
                if old_th != th and th not in old_th:
                    new_th = f"{old_th} / {th}"
                    self.table.item(row_idx, 1).setText(new_th)
                    existing_terms[en_lower] = (row_idx, new_th) # update cache
                    self.mark_modified()
                    merged_count += 1
            else:
                self.add_row(en, th, tag)
                existing_terms[en_lower] = (self.table.rowCount() - 1, th)
                added_count += 1
        
        if added_count == 0 and merged_count == 0:
            raise Exception("AI returned valid JSON, but no new or unique terms were extracted.")
            
        self.save_glossary(show_msg=False)
        QMessageBox.information(self, "Success", f"Glossary terms updated!\nAdded: {added_count} terms\nMerged: {merged_count} duplicates")

    def load_glossary(self):
        self.table.blockSignals(True)
        self.table.setRowCount(0)
        
        target_lang = self.profile_data.get("target_language", "Target") if self.profile_data else "Target"
        if not target_lang:
            target_lang = "Target"
            
        ui_lang = os.environ.get("THUB_LANG", "th")
        if target_lang.lower() in ["thai", "th", "ไทย"]:
            target_header = _("glossary_col_thai")
        else:
            if ui_lang == "th":
                target_header = f"คำแปลภาษา {target_lang} (จำเป็น)"
            else:
                target_header = f"{target_lang} Translation (Required)"
        
        self.table.setHorizontalHeaderLabels([_("glossary_col_word"), target_header, _("glossary_col_tag")])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

        for wrong, val in self.profile_data.get("glossary", {}).items():
            if isinstance(val, list):
                right = val[0]
                tag = val[1] if len(val) > 1 else "General"
            else:
                right = val
                tag = "General"
            self.add_row(wrong, right, tag)
        self.table.blockSignals(False)
        self._is_modified = False

    def add_row(self, wrong="", right="", tag="General"):
        self.table.blockSignals(True)
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(wrong))
        self.table.setItem(row, 1, QTableWidgetItem(right))
        
        tag_item = QTableWidgetItem(tag)
        tag_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 2, tag_item)
        
        self.table.blockSignals(False)
        self._is_modified = True

    def export_glossary(self):
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        import json
        
        path, _ext = QFileDialog.getSaveFileName(self, "Export Glossary", "", "JSON Files (*.json)")
        if not path:
            return
            
        data = TStudioCore.load_profiles()
        glossary_data = data["presets"][self.active_profile].get("glossary", {})
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(glossary_data, f, ensure_ascii=False, indent=2)
            QMessageBox.information(self, "Success", f"Glossary exported successfully to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export glossary:\n{str(e)}")
            
    def import_glossary(self):
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        import json
        
        path, _ext = QFileDialog.getOpenFileName(self, "Import Glossary", "", "JSON Files (*.json)")
        if not path:
            return
            
        try:
            with open(path, 'r', encoding='utf-8') as f:
                imported_data = json.load(f)
                
            if not isinstance(imported_data, dict):
                QMessageBox.warning(self, "Error", "Invalid JSON format. Expected a dictionary.")
                return
                
            data = TStudioCore.load_profiles()
            current_glossary = data["presets"][self.active_profile].get("glossary", {})
            
            # Merge imported data
            for eng, val in imported_data.items():
                if isinstance(val, list) and len(val) >= 2:
                    current_glossary[eng] = val
                elif isinstance(val, str):
                    current_glossary[eng] = [val, "General"]
            
            data["presets"][self.active_profile]["glossary"] = current_glossary
            TStudioCore.save_profiles(data)
            
            self.profile_data = data["presets"][self.active_profile]
            self.load_glossary()  # Fixed: was self.load_data() which doesn't exist
            QMessageBox.information(self, "Success", "Glossary imported successfully!")
            
            # Notify TranslationStudio main window to refresh QA checks and markers
            p = self.parent()
            while p:
                if p.__class__.__name__ == 'TranslationStudio' and hasattr(p, 'refresh_glossary_dependent_features'):
                    p.refresh_glossary_dependent_features()
                    break
                p = p.parent()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to import glossary:\n{str(e)}")



    def del_row(self):
        row = self.table.currentRow()
        if row >= 0:
            self.table.removeRow(row)
            self._is_modified = True
            if hasattr(self, 'save_timer'):
                self.save_timer.start(0) # Save deletion immediately

    def save_glossary(self, show_msg=True):
        data = TStudioCore.load_profiles()
        if self.active_profile in data["presets"]:
            new_glossary = {}
            for r in range(self.table.rowCount()):
                w, c = self.table.item(r, 0), self.table.item(r, 1)
                tag_item = self.table.item(r, 2)
                if w and c and w.text().strip():
                    tag = tag_item.text() if tag_item else "General"
                    new_glossary[w.text().strip()] = [c.text().strip(), tag]
            data["presets"][self.active_profile]["glossary"] = new_glossary
            TStudioCore.save_profiles(data)
            self._is_modified = False
            if show_msg:
                QMessageBox.information(self, "Saved", f"Glossary saved to profile '{self.active_profile}'!")
            
            # Notify TranslationStudio main window to refresh QA checks and markers
            p = self.parent()
            while p:
                if p.__class__.__name__ == 'TranslationStudio' and hasattr(p, 'refresh_glossary_dependent_features'):
                    p.refresh_glossary_dependent_features()
                    break
                p = p.parent()

    def closeEvent(self, event):
        if getattr(self, '_is_modified', False):
            if hasattr(self, 'save_timer') and self.save_timer.isActive():
                self.save_timer.stop()
            self.save_glossary(show_msg=False)
        event.accept()


    def auto_tag_general_rows(self):
        rows_to_tag = []
        terms_to_tag = []
        for r in range(self.table.rowCount()):
            tag_item = self.table.item(r, 2)
            w = self.table.item(r, 0)
            c = self.table.item(r, 1)
            row_tag = tag_item.text() if tag_item else "General"
            if w and c and row_tag == "General":
                if w.text().strip() and c.text().strip():
                    rows_to_tag.append(r)
                    terms_to_tag.append({"en": w.text().strip(), "th": c.text().strip()})
        
        if not terms_to_tag:
            QMessageBox.information(self, "Auto-Tag", "No 'General' items to tag!")
            return
            
        cfg = TStudioCore.load_config()
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        self.setWindowTitle("📖 Glossary Editor - Auto-Tagging... Please wait...")
        QApplication.processEvents()
        
        prompt = "You are a video game localization expert.\n" \
                 "Categorize the following glossary terms into exactly one of these tags: General, Person, Location, Weapon, Item, Faction, Quest, Other.\n" \
                 "Input terms:\n" + json.dumps(terms_to_tag, ensure_ascii=False) + "\n\n" \
                 "You MUST output ONLY a valid JSON array matching the exact same order. Do not use nested objects. Each object must have a 'tag' string key.\n" \
                 "Example of expected output:\n" \
                 '[\n  {"tag": "Item"},\n  {"tag": "Person"}\n]\n' \
                 "Output ONLY the JSON array. Do NOT output markdown formatting like ```json."
                 
        is_local = (cfg.get("provider", "") == "Local LLM" or cfg.get("model", "") == "custom-local-llm")
        
        def do_tag():
            return CoreAI.generate_content(cfg, prompt, is_local=is_local)
            
        def on_success(res):
            try:
                self.isVisible()  # Guard: raises RuntimeError if C++ object is deleted
            except RuntimeError:
                QApplication.restoreOverrideCursor()
                return
            try:
                match = re.search(r'\[.*\]', res, re.DOTALL)
                if match:
                    clean_res = match.group(0)
                else:
                    clean_res = re.sub(r'^```[^\n]*\n?|\n?```$', '', res.strip(), flags=re.MULTILINE)
                    
                new_tags = json.loads(clean_res)
                
                if not isinstance(new_tags, list):
                    raise Exception("AI did not return a JSON Array.")
                if len(new_tags) != len(rows_to_tag):
                    raise Exception(f"AI returned {len(new_tags)} tags but expected {len(rows_to_tag)}.")
                
                for idx, item in enumerate(new_tags):
                    tag = item.get("tag", "General")
                    if tag in GLOSSARY_TAGS:
                        row = rows_to_tag[idx]
                        tag_item = self.table.item(row, 2)
                        if tag_item:
                            tag_item.setText(tag)
                        else:
                            tag_item = QTableWidgetItem(tag)
                            tag_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                            self.table.setItem(row, 2, tag_item)
                            
                self.save_glossary(show_msg=False)
                self.btn_gen.setText("🧠 Extract from TLM")
                self.btn_gen.setEnabled(True)
                QApplication.restoreOverrideCursor()
                self.setWindowTitle(f"📖 Glossary Editor (Editing: {self.active_profile})")
                QMessageBox.information(self, "Success", f"Successfully auto-tagged {len(rows_to_tag)} items and saved to profile!")
            except Exception as e:
                on_error(f"Data parsing error: {e}\n\nRaw Response:\n{res[:200]}...")
                
        def on_error(err):
            try:
                self.isVisible()  # Guard: raises RuntimeError if C++ object is deleted
            except RuntimeError:
                QApplication.restoreOverrideCursor()
                return
            self.btn_gen.setText("🧠 Extract from TLM")
            self.btn_gen.setEnabled(True)
            QApplication.restoreOverrideCursor()
            self.setWindowTitle(f"📖 Glossary Editor (Editing: {self.active_profile})")
            QMessageBox.critical(self, "Failed", f"Error auto-tagging:\n{err}")

        worker = ApiWorker(do_tag)
        forwarder = ThreadSafeWorkerSignalsForwarder(on_success, on_error, self)
        worker.signals.finished.connect(forwarder.handle_finished)
        worker.signals.error.connect(forwarder.handle_error)
        QThreadPool.globalInstance().start(worker)




    def retranslate_options(self):
        row = self.table.currentRow()
        if row < 0:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Warning", "Please select a row first!")
            return

        item_en = self.table.item(row, 0)
        if not item_en or not item_en.text().strip():
            return

        # CO-C2: capture item identity instead of stale integer row
        anchor_item = self.table.item(row, 0)

        cfg = TStudioCore.load_config()
        self.setWindowTitle("📖 Glossary Editor - Translating... Please wait...")
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        QApplication.processEvents()

        source_text = item_en.text().strip()
        prompt = f"You are a professional video game localization expert.\n" \
                 f"Provide 3 different Thai translation options for the glossary term: '{source_text}'.\n" \
                 f"Output ONLY a JSON array of strings containing the 3 options. No markdown formatting."

        is_local = (cfg.get("provider", "") == "Local LLM" or cfg.get("model", "") == "custom-local-llm")

        def do_opt():
            return CoreAI.generate_content(cfg, prompt, is_local=is_local)

        def on_success(res):
            try:
                import re
                match = re.search(r'\[.*\]', res, re.DOTALL)
                if match:
                    clean_res = match.group(0)
                else:
                    clean_res = re.sub(r'^```[^\n]*\n?|\n?```$', '', res.strip(), flags=re.MULTILINE)

                import json
                options = json.loads(clean_res)

                if not isinstance(options, list) or len(options) == 0:
                    raise Exception("Invalid JSON Array format from AI.")

                QApplication.restoreOverrideCursor()
                self.setWindowTitle(f"📖 Glossary Editor (Editing: {self.active_profile})")

                dlg = TranslationOptionsDialog(self, options)
                if dlg.exec() and dlg.selected_text:
                    # CO-C2: resolve current row from anchor_item to avoid stale index
                    if anchor_item is None:
                        return
                    target_row = None
                    for r in range(self.table.rowCount()):
                        if self.table.item(r, 0) is anchor_item:
                            target_row = r
                            break
                    if target_row is None:
                        return
                    item_th = self.table.item(target_row, 1)
                    if not item_th:
                        from PyQt6.QtWidgets import QTableWidgetItem
                        item_th = QTableWidgetItem()
                        self.table.setItem(target_row, 1, item_th)
                    item_th.setText(dlg.selected_text)
                    self.mark_modified()

            except Exception as e:
                on_error(f"Data parsing error: {e}\n\nRaw Response:\n{res[:200]}...")

        def on_error(err):
            from PyQt6.QtWidgets import QMessageBox
            QApplication.restoreOverrideCursor()
            self.setWindowTitle(f"📖 Glossary Editor (Editing: {self.active_profile})")
            QMessageBox.critical(self, "Failed", f"Error generating options:\n{err}")

        worker = ApiWorker(do_opt)
        forwarder = ThreadSafeWorkerSignalsForwarder(on_success, on_error, self)
        worker.signals.finished.connect(forwarder.handle_finished)
        worker.signals.error.connect(forwarder.handle_error)
        QThreadPool.globalInstance().start(worker)


    def retranslate_custom(self):
        row = self.table.currentRow()
        if row < 0:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Warning", "Please select a row first!")
            return

        item_en = self.table.item(row, 0)
        if not item_en or not item_en.text().strip():
            return

        # CO-C2: capture item identity instead of stale integer row
        anchor_item = self.table.item(row, 0)

        from PyQt6.QtWidgets import QInputDialog, QApplication
        from PyQt6.QtCore import Qt
        custom_prompt, ok = QInputDialog.getMultiLineText(self, "Custom Translation", "Enter your custom prompt for this term (use {term} for the English word):", "Translate the glossary term: '{term}' to Thai. Output only the translated word.")
        if ok and custom_prompt.strip():
            cfg = TStudioCore.load_config()
            self.setWindowTitle("📖 Glossary Editor - Translating... Please wait...")
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            QApplication.processEvents()

            source_text = item_en.text().strip()
            prompt = custom_prompt.replace('{term}', source_text)

            is_local = (cfg.get("provider", "") == "Local LLM" or cfg.get("model", "") == "custom-local-llm")

            def do_cus():
                return CoreAI.generate_content(cfg, prompt, is_local=is_local)

            def on_success(res):
                import re
                clean_res = re.sub(r'^```[^\n]*\n?|\n?```$', '', res.strip(), flags=re.MULTILINE)

                QApplication.restoreOverrideCursor()
                self.setWindowTitle(f"📖 Glossary Editor (Editing: {self.active_profile})")

                # CO-C2: resolve current row from anchor_item to avoid stale index
                if anchor_item is None:
                    return
                target_row = None
                for r in range(self.table.rowCount()):
                    if self.table.item(r, 0) is anchor_item:
                        target_row = r
                        break
                if target_row is None:
                    return
                item_th = self.table.item(target_row, 1)
                if not item_th:
                    from PyQt6.QtWidgets import QTableWidgetItem
                    item_th = QTableWidgetItem()
                    self.table.setItem(target_row, 1, item_th)
                item_th.setText(clean_res)
                self.mark_modified()

            def on_error(err):
                from PyQt6.QtWidgets import QMessageBox
                QApplication.restoreOverrideCursor()
                self.setWindowTitle(f"📖 Glossary Editor (Editing: {self.active_profile})")
                QMessageBox.critical(self, "Failed", f"Error translating:\n{err}")

            worker = ApiWorker(do_cus)
            forwarder = ThreadSafeWorkerSignalsForwarder(on_success, on_error, self)
            worker.signals.finished.connect(forwarder.handle_finished)
            worker.signals.error.connect(forwarder.handle_error)
            QThreadPool.globalInstance().start(worker)

    def retranslate_special(self, mode):
        row = self.table.currentRow()
        if row < 0:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Warning", "Please select a row first!")
            return
            
        item_en = self.table.item(row, 0)
        if not item_en or not item_en.text().strip():
            return
            
        anchor_item = self.table.item(row, 0)
        cfg = TStudioCore.load_config()
        self.setWindowTitle(f"📖 Glossary Editor - Translating ({mode})...")
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        QApplication.processEvents()

        source_text = item_en.text().strip()
        
        mode_text = ""
        length_constraint = "Keep your translation CONCISE. Match the length and structure of the original text as closely as possible."
        
        if mode == "transliterate":
            mode_text = "TRANSLITERATE (แปลทับศัพท์) the original text into Thai pronunciation WITHOUT translating its meaning. Return ONLY the transliterated word."
        elif mode == "idiom":
            mode_text = f"Analyze the underlying meaning carefully. Translate into a natural, contextually appropriate Thai idiom or phrase (สำนวน/คำพังเพย). {length_constraint}"
        elif mode == "poem":
            mode_text = f"Translate into an elegant Thai poetic form (กลอน/บทกวี/คาถา) with appropriate rhyming. {length_constraint}"
        elif mode == "quote":
            mode_text = f"Translate into formal, philosophical, and impactful Thai language (คำคม/ปรัชญา). {length_constraint}"
        elif mode == "mature":
            mode_text = f"Translate aggressively using mature, unfiltered, or profane Thai language (หยาบคาย/ดุดัน) appropriate for a gritty action game. {length_constraint}"
        elif mode == "fantasy":
            mode_text = f"Translate using medieval, fantasy, or archaic Thai language (ย้อนยุค/แฟนตาซี) (e.g., ข้า, เจ้า, ฝ่าบาท). {length_constraint}"
        elif mode == "robotic":
            mode_text = f"Translate into cold, systemic, robotic Thai language (ประกาศจากระบบ/AI). {length_constraint}"
        elif mode == "casual":
            mode_text = f"Translate into modern, casual, or sarcastic Thai slang (วัยรุ่น/กวนๆ) suitable for natural youth conversation. {length_constraint}"
            
        prompt = f"You are a professional video game localization expert.\n{mode_text}\n\nOriginal Text: '{source_text}'\n\nOutput ONLY the translated term without quotes or formatting."

        is_local = (cfg.get("provider", "") == "Local LLM" or cfg.get("model", "") == "custom-local-llm")
        
        def do_special():
            return CoreAI.generate_content(cfg, prompt, is_local=is_local)
            
        def on_success(res):
            try:
                import re
                clean_res = re.sub(r'^```[^\n]*\n?|\n?```$', '', res.strip(), flags=re.MULTILINE)
                clean_res = re.sub(r'^"|"$', '', clean_res).strip()
                
                if anchor_item is None: return
                target_row = None
                for r in range(self.table.rowCount()):
                    if self.table.item(r, 0) is anchor_item:
                        target_row = r
                        break
                if target_row is None: return
                
                item_th = self.table.item(target_row, 1)
                if not item_th:
                    from PyQt6.QtWidgets import QTableWidgetItem
                    item_th = QTableWidgetItem()
                    self.table.setItem(target_row, 1, item_th)
                item_th.setText(clean_res)
                self.mark_modified()
            except Exception as e:
                on_error(f"Data parsing error: {e}")
            finally:
                QApplication.restoreOverrideCursor()
                self.setWindowTitle(f"📖 Glossary Editor (Editing: {self.active_profile})")
                
        def on_error(err):
            from PyQt6.QtWidgets import QMessageBox
            QApplication.restoreOverrideCursor()
            self.setWindowTitle(f"📖 Glossary Editor (Editing: {self.active_profile})")
            QMessageBox.critical(self, "API Error", f"Failed to connect to API:\n{err}")

        worker = ApiWorker(do_special)
        forwarder = ThreadSafeWorkerSignalsForwarder(on_success=on_success, on_error=on_error, parent=self)
        worker.signals.finished.connect(forwarder.handle_finished)
        worker.signals.error.connect(forwarder.handle_error)
        QThreadPool.globalInstance().start(worker)

    # --- duplicate retranslate_options (blocking/wrong import) and duplicate retranslate_custom (bare signals) removed ---

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
        btn_ok = QPushButton(_("btn_format_file"))
        btn_ok.setToolTip(_("tooltip_btn_ok"))
        btn_ok.setStyleSheet("background: #a6e3a1; color: #1e1e2e; font-weight: bold; padding: 6px;")
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton(_("btn_cancel"))
        btn_cancel.setToolTip(_("tooltip_btn_cancel"))
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


