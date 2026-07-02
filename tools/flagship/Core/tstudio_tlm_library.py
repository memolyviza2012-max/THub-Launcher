import os
import json
import re
import urllib.request
import urllib.error
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QListWidgetItem,
    QLineEdit, QTextEdit, QLabel, QMessageBox, QSplitter, QApplication, QComboBox, QWidget, QGroupBox, QFormLayout
)
from PyQt6.QtCore import Qt, QThreadPool

from tstudio_core import TStudioCore, CoreAI, BASE_DIR
from tstudio_ui_shared import ApiWorker, ThreadSafeWorkerSignalsForwarder
try:
    from tstudio_i18n import _
except ImportError:
    try:
        from trun_i18n import _
    except ImportError:
        from i18n_helper import _


class SummarizeSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("summarize_settings_title") if _("summarize_settings_title") != "summarize_settings_title" else "📝 Summarize Settings")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel(_("choose_summary_style") if _("choose_summary_style") != "choose_summary_style" else "Choose Summary Style:"))
        self.cbo_style = QComboBox()
        self.cbo_style.addItems([
            "Story Narrative (เล่าเป็นเรื่องราว)",
            "Key Bullet Points (สรุปเป็นข้อๆ)",
            "Character Relations (เจาะลึกความสัมพันธ์)"
        ])
        layout.addWidget(self.cbo_style)
        
        layout.addWidget(QLabel(_("custom_instructions") if _("custom_instructions") != "custom_instructions" else "Custom Instructions (คำสั่งพิเศษ - Optional):"))
        self.txt_custom = QLineEdit()
        self.txt_custom.setPlaceholderText("e.g. เน้นเรื่องอาวุธเป็นพิเศษ...")
        layout.addWidget(self.txt_custom)
        
        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton(_("btn_cancel"))
        btn_cancel.setToolTip(_("tooltip_btn_cancel"))
        btn_cancel.clicked.connect(self.reject)
        self.btn_start = QPushButton(_("btn_generate_summary") if _("btn_generate_summary") != "btn_generate_summary" else "🚀 Generate Summary")
        self.btn_start.setToolTip(_("tooltip_btn_start"))
        self.btn_start.setStyleSheet("background: #f5c2e7; color: #1e1e2e; font-weight: bold;")
        self.btn_start.clicked.connect(self.accept)
        
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(self.btn_start)
        
        layout.addLayout(btn_layout)
        
    def get_settings(self):
        return {
            "style": self.cbo_style.currentText(),
            "custom": self.txt_custom.text().strip()
        }


class TLMLoreLibrary(QWidget):
    def __init__(self, glossary_widget, parent=None):
        super().__init__(parent)
        self.main_app = parent
        self.active_profile = TStudioCore.load_profiles()["active_preset"]
        self.profile_data = TStudioCore.get_current_profile_data()
        
        self.lore_dir = os.path.join(BASE_DIR, "profiles", self.active_profile, "TLM_Lore")
        os.makedirs(self.lore_dir, exist_ok=True)
        
        self.current_editing_file = None
        
        main_layout = QVBoxLayout(self)
        
        # We will use a 3-pane layout using nested splitters
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # --- LEFT PANE: File Manager ---
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        lbl_files = QLabel("📂 " + (_("saved_lore_files") if _("saved_lore_files") != "saved_lore_files" else "Saved Lore Files"))
        lbl_files.setStyleSheet("font-weight: bold;")
        left_layout.addWidget(lbl_files)
        
        self.list_files = QListWidget()
        self.list_files.itemClicked.connect(self.on_file_selected)
        self.list_files.itemChanged.connect(self.on_file_checked)
        left_layout.addWidget(self.list_files)
        
        left_btn_layout = QHBoxLayout()
        btn_new = QPushButton("➕ " + (_("btn_new_file") if _("btn_new_file") != "btn_new_file" else "New File"))
        btn_new.setToolTip(_("tooltip_btn_new"))
        btn_new.clicked.connect(self.new_file)
        btn_del = QPushButton("🗑️ " + _("btn_delete"))
        btn_del.setToolTip(_("tooltip_btn_del"))
        btn_del.clicked.connect(self.delete_file)
        left_btn_layout.addWidget(btn_new)
        left_btn_layout.addWidget(btn_del)
        left_layout.addLayout(left_btn_layout)
        
        main_splitter.addWidget(left_widget)
        
        # --- MIDDLE PANE: Raw Lore Editor & Fetcher ---
        mid_widget = QWidget()
        mid_layout = QVBoxLayout(mid_widget)
        mid_layout.setContentsMargins(0, 0, 0, 0)
        
        lbl_editor = QLabel("📝 " + (_("lore_editor") if _("lore_editor") != "lore_editor" else "Lore Editor & Fetcher"))
        lbl_editor.setStyleSheet("font-weight: bold;")
        mid_layout.addWidget(lbl_editor)
        
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel(_("file_title") if _("file_title") != "file_title" else "File Title:"))
        self.txt_title = QLineEdit()
        title_layout.addWidget(self.txt_title)
        
        btn_save = QPushButton("💾 " + (_("btn_save_context") if _("btn_save_context") != "btn_save_context" else "Save File"))
        btn_save.setToolTip(_("tooltip_btn_save"))
        btn_save.setStyleSheet("background: #a6e3a1; color: #1e1e2e; font-weight: bold;")
        btn_save.clicked.connect(self.save_file)
        title_layout.addWidget(btn_save)
        mid_layout.addLayout(title_layout)
        
        fetch_layout = QHBoxLayout()
        fetch_layout.addWidget(QLabel("🌐 " + (_("url_topic") if _("url_topic") != "url_topic" else "URL / Topic:")))
        self.txt_url = QLineEdit()
        self.txt_url.setPlaceholderText("Paste Wiki URL OR type a lore topic...")
        fetch_layout.addWidget(self.txt_url)
        
        self.btn_fetch = QPushButton("⚡ " + (_("btn_fetch") if _("btn_fetch") != "btn_fetch" else "Fetch URL"))
        self.btn_fetch.setToolTip(_("tooltip_btn_fetch"))
        self.btn_fetch.clicked.connect(self.fetch_url)
        fetch_layout.addWidget(self.btn_fetch)
        
        self.btn_ai_gen = QPushButton("🤖 " + (_("btn_ai_generate") if _("btn_ai_generate") != "btn_ai_generate" else "AI Generate"))
        self.btn_ai_gen.setToolTip(_("tooltip_btn_ai_gen"))
        self.btn_ai_gen.clicked.connect(self.generate_lore_from_topic)
        fetch_layout.addWidget(self.btn_ai_gen)
        
        mid_layout.addLayout(fetch_layout)
        
        self.txt_content = QTextEdit()
        self.txt_content.setPlaceholderText("Paste lore, write summary, or use Fetch/AI Generate...")
        mid_layout.addWidget(self.txt_content)
        
        main_splitter.addWidget(mid_widget)
        
        # --- RIGHT PANE: AI Magic Actions & Master Context ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        lbl_ai = QLabel("✨ " + (_("ai_actions") if _("ai_actions") != "ai_actions" else "AI Magic Actions"))
        lbl_ai.setStyleSheet("font-weight: bold;")
        right_layout.addWidget(lbl_ai)
        
        # Sub-group: Master Context Cooker
        grp_master = QGroupBox(_("master_context_cooker") if _("master_context_cooker") != "master_context_cooker" else "Master Context Cooker")
        grp_master_layout = QVBoxLayout()
        
        self.txt_optimized = QTextEdit()
        self.txt_optimized.setPlaceholderText("Optimized Master Context will appear here...")
        preset = self.profile_data
        if "tlm_master_context" in preset:
            self.txt_optimized.setText(preset["tlm_master_context"])
        grp_master_layout.addWidget(self.txt_optimized)
        
        master_btn_layout = QHBoxLayout()
        self.btn_cook = QPushButton("🔥 " + (_("btn_cook_context") if _("btn_cook_context") != "btn_cook_context" else "Cook from Middle Pane"))
        self.btn_cook.setToolTip(_("tooltip_btn_cook"))
        self.btn_cook.setStyleSheet("background: #f38ba8; color: #1e1e2e; font-weight: bold;")
        self.btn_cook.clicked.connect(self.cook_context)
        master_btn_layout.addWidget(self.btn_cook)
        
        self.btn_set_ctx = QPushButton("✅ " + (_("btn_set_game_context") if _("btn_set_game_context") != "btn_set_game_context" else "Set as Game Context"))
        self.btn_set_ctx.setToolTip(_("tooltip_btn_set_ctx"))
        self.btn_set_ctx.setStyleSheet("background: #a6e3a1; color: #1e1e2e; font-weight: bold;")
        self.btn_set_ctx.clicked.connect(self.set_game_context)
        master_btn_layout.addWidget(self.btn_set_ctx)
        
        grp_master_layout.addLayout(master_btn_layout)
        grp_master.setLayout(grp_master_layout)
        right_layout.addWidget(grp_master)
        
        # Sub-group: Multi-file AI Extraction
        grp_multi = QGroupBox(_("multi_file_ai") if _("multi_file_ai") != "multi_file_ai" else "Batch Actions (Applies to ALL checked files)")
        grp_multi_layout = QVBoxLayout()
        
        self.btn_extract = QPushButton("🧠 " + _("btn_extract_tlm"))
        self.btn_extract.setToolTip(_("tooltip_btn_extract"))
        self.btn_extract.setStyleSheet("background: #f5c2e7; color: #1e1e2e; font-weight: bold; padding: 6px;")
        self.btn_extract.clicked.connect(self.do_extract_glossary)
        grp_multi_layout.addWidget(self.btn_extract)
        
        self.btn_summarize = QPushButton("📝 " + (_("btn_generate_master_summary") if _("btn_generate_master_summary") != "btn_generate_master_summary" else "Generate Master Summary"))
        self.btn_summarize.setToolTip(_("tooltip_btn_summarize"))
        self.btn_summarize.setStyleSheet("background: #89b4fa; color: #1e1e2e; font-weight: bold; padding: 6px;")
        self.btn_summarize.clicked.connect(self.do_generate_summary)
        grp_multi_layout.addWidget(self.btn_summarize)
        
        grp_multi.setLayout(grp_multi_layout)
        right_layout.addWidget(grp_multi)
        
        main_splitter.addWidget(right_widget)
        
        # Set proportions: 20% left, 45% middle, 35% right
        main_splitter.setSizes([240, 540, 420])
        main_layout.addWidget(main_splitter)
        
        self.refresh_list()
        
    def refresh_list(self):
        self.list_files.clear()
        if not os.path.exists(self.lore_dir): return
        
        files = [f for f in os.listdir(self.lore_dir) if f.endswith(".txt")]
        for f in files:
            item = QListWidgetItem(f.replace(".txt", ""))
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.list_files.addItem(item)
            
    def new_file(self):
        self.current_editing_file = None
        self.txt_title.clear()
        self.txt_content.clear()
        self.txt_url.clear()
        
    def on_file_checked(self, item):
        if self.list_files.currentItem() != item:
            self.list_files.setCurrentItem(item)
            self.on_file_selected(item)
            
    def on_file_selected(self, item):
        title = item.text()
        filepath = os.path.join(self.lore_dir, f"{title}.txt")
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
            except OSError:
                content = ""
                QMessageBox.warning(self, _("error_title"), "Could not read file.")
            self.txt_title.setText(title)
            self.txt_content.setText(content)
            self.current_editing_file = title
            
    def save_file(self):
        title = self.txt_title.text().strip()
        title = "".join(c for c in title if c.isalnum() or c in (" ", "_", "-")).strip()
        
        if not title:
            QMessageBox.warning(self, "Warning", "Please enter a valid title.")
            return
            
        content = self.txt_content.toPlainText().strip()
        if not content:
            QMessageBox.warning(self, "Warning", "Cannot save an empty file.")
            return
            
        if self.current_editing_file and self.current_editing_file != title:
            old_path = os.path.join(self.lore_dir, f"{self.current_editing_file}.txt")
            if os.path.exists(old_path):
                os.remove(old_path)
                
        filepath = os.path.join(self.lore_dir, f"{title}.txt")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
            
        self.current_editing_file = title
        QMessageBox.information(self, "Saved", f"Lore file '{title}' saved successfully!")
        self.refresh_list()
        
    def delete_file(self):
        item = self.list_files.currentItem()
        if not item: return
        
        title = item.text()
        reply = QMessageBox.question(self, _("delete_layout_title"), f"Delete '{title}'?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            filepath = os.path.join(self.lore_dir, f"{title}.txt")
            try:
                os.remove(filepath)
            except OSError:
                pass
            self.refresh_list()
            self.new_file()
            
    def fetch_url(self):
        url = self.txt_url.text().strip()
        if not url: return
        
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        self.btn_fetch.setEnabled(False)
        self.btn_fetch.setText("Fetching...")
        
        def do_fetch():
            jina_url = "https://r.jina.ai/" + url
            req = urllib.request.Request(jina_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                return response.read().decode('utf-8')
                
        def on_success(content):
            QApplication.restoreOverrideCursor()
            self.btn_fetch.setEnabled(True)
            self.btn_fetch.setText("⚡ " + (_("btn_fetch") if _("btn_fetch") != "btn_fetch" else "Fetch URL"))
            self.txt_content.setText(content)
            if not self.txt_title.text():
                title_guess = url.split("/")[-1].replace("_", " ").split("?")[0]
                self.txt_title.setText(title_guess)
                
        def on_error(err):
            QApplication.restoreOverrideCursor()
            self.btn_fetch.setEnabled(True)
            self.btn_fetch.setText("⚡ " + (_("btn_fetch") if _("btn_fetch") != "btn_fetch" else "Fetch URL"))
            QMessageBox.warning(self, "Fetch Error", f"Failed to fetch URL.\nError: {err}")
            
        worker = ApiWorker(do_fetch)
        forwarder = ThreadSafeWorkerSignalsForwarder(on_success, on_error, self)
        worker.signals.finished.connect(forwarder.handle_finished)
        worker.signals.error.connect(forwarder.handle_error)
        QThreadPool.globalInstance().start(worker)

    def generate_lore_from_topic(self):
        topic = self.txt_url.text().strip()
        if not topic: return
        
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        self.btn_ai_gen.setEnabled(False)
        self.btn_ai_gen.setText("Generating...")
        
        def do_gen():
            cfg = TStudioCore.load_config()
            is_local = (cfg.get("provider", "") == "Local LLM" or cfg.get("model", "") == "custom-local-llm")
            prompt = f"Write a comprehensive lore summary and background information about the following topic for the game '{self.active_profile}'.\n\nTopic: {topic}\n\nProvide the lore in a clean, detailed format."
            return CoreAI.generate_content(cfg, prompt, is_local=is_local)
            
        def on_success(res):
            QApplication.restoreOverrideCursor()
            self.btn_ai_gen.setEnabled(True)
            self.btn_ai_gen.setText("🤖 " + (_("btn_ai_generate") if _("btn_ai_generate") != "btn_ai_generate" else "AI Generate"))
            self.txt_content.setText(res)
            if not self.txt_title.text():
                self.txt_title.setText(topic)
                
        def on_error(err):
            QApplication.restoreOverrideCursor()
            self.btn_ai_gen.setEnabled(True)
            self.btn_ai_gen.setText("🤖 " + (_("btn_ai_generate") if _("btn_ai_generate") != "btn_ai_generate" else "AI Generate"))
            QMessageBox.warning(self, _("ai_error_title"), f"Failed to generate lore:\n{err}")
            
        worker = ApiWorker(do_gen)
        forwarder = ThreadSafeWorkerSignalsForwarder(on_success, on_error, self)
        worker.signals.finished.connect(forwarder.handle_finished)
        worker.signals.error.connect(forwarder.handle_error)
        QThreadPool.globalInstance().start(worker)

    def cook_context(self):
        raw_text = self.txt_content.toPlainText().strip()
        if not raw_text:
            QMessageBox.warning(self, _("no_context_title"), _("no_context_msg"))
            return
            
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        self.btn_cook.setEnabled(False)
        self.btn_cook.setText("Cooking...")
        
        def do_cook():
            cfg = TStudioCore.load_config()
            is_local = (cfg.get("provider", "") == "Local LLM" or cfg.get("model", "") == "custom-local-llm")
            prompt = f"You are a lore expert. Summarize the following raw text into a highly condensed, bulleted 'Master Lore Context' specifically for a translator.\nFocus ONLY on:\n1. Core plot or background.\n2. Key characters and their roles/traits.\n3. Important factions, locations, or rules of the world.\nKeep it extremely brief and informative.\n\nRAW TEXT:\n{raw_text[:12000]}"
            return CoreAI.generate_content(cfg, prompt, is_local=is_local)
            
        def on_success(res):
            QApplication.restoreOverrideCursor()
            self.btn_cook.setEnabled(True)
            self.btn_cook.setText("🔥 " + (_("btn_cook_context") if _("btn_cook_context") != "btn_cook_context" else "Cook from Middle Pane"))
            self.txt_optimized.setText(res.strip())
            
        def on_error(err):
            QApplication.restoreOverrideCursor()
            self.btn_cook.setEnabled(True)
            self.btn_cook.setText("🔥 " + (_("btn_cook_context") if _("btn_cook_context") != "btn_cook_context" else "Cook from Middle Pane"))
            QMessageBox.warning(self, _("ai_error_title"), f"{_('failed_optimize_context')}\n{err}")
            
        worker = ApiWorker(do_cook)
        forwarder = ThreadSafeWorkerSignalsForwarder(on_success, on_error, self)
        worker.signals.finished.connect(forwarder.handle_finished)
        worker.signals.error.connect(forwarder.handle_error)
        QThreadPool.globalInstance().start(worker)

    def set_game_context(self):
        opt_text = self.txt_optimized.toPlainText().strip()
        if not opt_text:
            QMessageBox.warning(self, "Warning", "Please cook or type an optimized context first.")
            return
            
        profiles = TStudioCore.load_profiles()
        preset = profiles["presets"].get(self.active_profile, {})
        preset["tlm_master_context"] = opt_text
        profiles["presets"][self.active_profile] = preset
        TStudioCore.save_profiles(profiles)
        
        QMessageBox.information(self, "Success", f"Master Context set for {self.active_profile}!\nThis context will now be injected into AI translation prompts automatically.")
        
    def get_checked_files_content(self):
        combined = []
        for i in range(self.list_files.count()):
            item = self.list_files.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                filepath = os.path.join(self.lore_dir, f"{item.text()}.txt")
                try:
                    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                        combined.append(f"--- FILE: {item.text()} ---\n{f.read()}\n")
                except OSError:
                    pass
        return "\n".join(combined)

    def run_ai_task(self, prompt, success_callback, loading_text="Processing..."):
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        self.btn_extract.setEnabled(False)
        self.btn_summarize.setEnabled(False)
        
        def do_task():
            cfg = TStudioCore.load_config()
            is_local = (cfg.get("provider", "") == "Local LLM" or cfg.get("model", "") == "custom-local-llm")
            return CoreAI.generate_content(cfg, prompt, is_local=is_local)
            
        def on_success(res):
            QApplication.restoreOverrideCursor()
            self.btn_extract.setEnabled(True)
            self.btn_summarize.setEnabled(True)
            success_callback(res)
            
        def on_error(err):
            QApplication.restoreOverrideCursor()
            self.btn_extract.setEnabled(True)
            self.btn_summarize.setEnabled(True)
            QMessageBox.warning(self, _("ai_error_title"), f"Error:\n{err}")
            
        worker = ApiWorker(do_task)
        forwarder = ThreadSafeWorkerSignalsForwarder(on_success, on_error, self)
        worker.signals.finished.connect(forwarder.handle_finished)
        worker.signals.error.connect(forwarder.handle_error)
        QThreadPool.globalInstance().start(worker)

    def do_extract_glossary(self):
        context = self.get_checked_files_content()
        if not context:
            QMessageBox.warning(self, "Warning", "Please check at least one file to extract from.")
            return
            
        game_name = self.profile_data.get("game_title", self.active_profile)
        amount = 50
        
        prompt = f"You are a video game localization expert. Extract {amount} key terminology (names, places, items, factions, lore concepts) from the following context for the game '{game_name}'.\n\n--- CONTEXT ---\n{context[:15000]}\n---------------\n\n" \
                 "You MUST output ONLY a valid JSON array. Each object in the array must have exactly three string keys: 'en', 'th', and 'tag'.\n" \
                 "- 'en': The English word.\n" \
                 "- 'th': The Thai translation.\n" \
                 "- 'tag': MUST be exactly one of: General, Person, Location, Weapon, Item, Faction, Quest, Other.\n" \
                 "Output ONLY the JSON array. Do NOT output markdown formatting like ```json."
                 
        self.run_ai_task(prompt, self.on_extract_success)

    def on_extract_success(self, res):
        try:
            match = re.search(r'\[.*\]', res, re.DOTALL)
            if match:
                clean_res = match.group(0)
            else:
                clean_res = re.sub(r'^```[^\n]*\n?|\n?```$', '', res.strip(), flags=re.MULTILINE)
                
            new_terms = json.loads(clean_res)
            
            if isinstance(new_terms, dict):
                raise Exception("AI returned a Dictionary instead of an Array.")
            if not isinstance(new_terms, list):
                raise Exception("AI did not return an Array.")
            
            game_name = self.profile_data.get("game_title", self.active_profile)
            if not hasattr(self.main_app, 'glossary_widget'):
                self.main_app.open_glossary()
            self.main_app.glossary_widget.merge_new_terms(new_terms, game_name)
            QMessageBox.information(self, "Success", "Glossary extracted and merged successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Data parsing error: {e}\n\nRaw Response:\n{res[:200]}...")

    def do_generate_summary(self):
        context = self.get_checked_files_content()
        if not context:
            QMessageBox.warning(self, "Warning", "Please check at least one file to summarize.")
            return
            
        dlg = SummarizeSettingsDialog(self)
        if dlg.exec():
            settings = dlg.get_settings()
            
            game_name = self.profile_data.get("game_title", self.active_profile)
            
            prompt = f"You are a video game lore master writing a master summary for the game '{game_name}' based on the following source files:\n\n--- CONTEXT ---\n{context[:20000]}\n---------------\n\n"
            prompt += f"Summary Style Required: {settings['style']}\n"
            if settings['custom']:
                prompt += f"Custom User Instructions: {settings['custom']}\n"
                
            prompt += "\nPlease write the summary in Thai language. Make it highly detailed, cohesive, and easy for modders to understand the lore."
            
            self.run_ai_task(prompt, self.on_summarize_success)
            
    def on_summarize_success(self, res):
        title = "AI_Master_Summary"
        counter = 1
        while os.path.exists(os.path.join(self.lore_dir, f"{title}.txt")):
            title = f"AI_Master_Summary_{counter}"
            counter += 1
            
        filepath = os.path.join(self.lore_dir, f"{title}.txt")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(res)
            
        self.refresh_list()
        QMessageBox.information(self, "Success", f"Master summary generated and saved as '{title}.txt'!")
