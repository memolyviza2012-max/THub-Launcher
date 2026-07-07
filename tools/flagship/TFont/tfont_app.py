from i18n_helper import _
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'Core')))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QGroupBox, QFileDialog, QMessageBox, QTextEdit,
    QTabWidget
)
from PyQt6.QtCore import Qt, QThreadPool, QRunnable, QObject, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QIcon



try:
    from tfont_generator import TFontGenerator
except ImportError:
    TFontGenerator = None

try:
    from legacy_font_engine import LegacyFontEngine
except ImportError:
    LegacyFontEngine = None

try:
    from visual_tuner_widget import VisualTunerWidget
except ImportError:
    VisualTunerWidget = None

DARK_SS = """
QMainWindow, QWidget, QDialog { background: #1e1e2e; color: #cdd6f4; }
QLineEdit, QTextEdit { background: #313244; color: #cdd6f4; border: 1px solid #45475a; border-radius: 4px; padding: 6px; font-size: 14px; }
QPushButton { background: #45475a; color: #cdd6f4; border: none; border-radius: 4px; padding: 8px 16px; font-size: 13px; font-weight: bold; }
QPushButton:hover { background: #585b70; }
QPushButton:disabled { background: #313244; color: #a6adc8; }
QGroupBox { border: 1px solid #45475a; border-radius: 6px; margin-top: 10px; padding-top: 14px; font-weight: bold; color: #89b4fa; }
QTabWidget::pane { border: 1px solid #45475a; border-radius: 4px; }
QTabBar::tab { background: #313244; color: #a6adc8; padding: 8px 20px; margin-right: 2px; border-top-left-radius: 4px; border-top-right-radius: 4px; }
QTabBar::tab:selected { background: #45475a; color: #cdd6f4; font-weight: bold; }
QTabBar::tab:hover { background: #585b70; }
"""

class WorkerSignals(QObject):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)

class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        try:
            # Check if function accepts a callback for progress
            import inspect
            sig = inspect.signature(self.fn)
            if 'callback' in sig.parameters:
                self.kwargs['callback'] = self.signals.progress.emit
                
            result = self.fn(*self.args, **self.kwargs)
            self.signals.finished.emit(result)
        except Exception as e:
            self.signals.error.emit(str(e))

class TFontApp(QMainWindow):
    def __init__(self):
        super().__init__()
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('flagship.tfont.app.1.0')
        except:
            pass
        self.setWindowTitle(_("app_title"))
        self.resize(750, 550)
        self.setStyleSheet(DARK_SS)
        
        logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "assets", "TFONT.png"))
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))
        
        self.engine = None
        self.font_engine = None
        if TFontGenerator:
            self.font_engine = TFontGenerator()
            
        self.legacy_engine = None
        if LegacyFontEngine:
            self.legacy_engine = LegacyFontEngine()
            
        # Try to load default mapping if available
        self.default_mapping_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'Core', 'Mapping.json'))
        if self.font_engine and os.path.exists(self.default_mapping_path):
            try:
                self.font_engine.load_mapping(self.default_mapping_path)
            except:
                pass
                
        self.init_ui()
        
    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # --- TAB 1: Font Generator ---
        self.tab_font = QWidget()
        self.init_font_tab()
        self.tabs.addTab(self.tab_font, _("tab_font_generator"))
        
        # --- TAB 2: Visual F700 Font Tuner (Replaces legacy static tab) ---
        if VisualTunerWidget:
            self.visual_tuner_tab = VisualTunerWidget(self.legacy_engine, self.log)
            self.tabs.addTab(self.visual_tuner_tab, _("tab_legacy_font") if hasattr(sys.modules[__name__], '_') else "F700 Legacy Font")
            
        # Log Window (Shared)
        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setStyleSheet("background: #181825; color: #a6adc8; font-family: Consolas, monospace;")
        main_layout.addWidget(self.txt_log)
        
        
        if self.font_engine:
            self.log(_("log_font_engine_loaded"), "#a6e3a1")
            if self.font_engine.mapping:
                self.log(f"Default Font Mapping loaded: {len(self.font_engine.mapping)} entries.", "#89b4fa")
        if self.legacy_engine:
            self.log("Legacy F700 Font Engine Loaded.", "#a6e3a1")

    def init_font_tab(self):
        layout = QVBoxLayout(self.tab_font)
        
        # File Group
        grp_file = QGroupBox(_("grp_font_settings"))
        l_file = QVBoxLayout(grp_file)
        
        # Mapping file
        h_map = QHBoxLayout()
        self.txt_font_map = QLineEdit()
        self.txt_font_map.setPlaceholderText(_("placeholder_font_map"))
        if self.font_engine and self.font_engine.mapping:
            self.txt_font_map.setText(self.default_mapping_path)
            
        btn_map = QPushButton(_("btn_browse"))
        btn_map.setToolTip(_("tooltip_map"))
        btn_map.clicked.connect(self.browse_font_map)
        h_map.addWidget(self.txt_font_map)
        h_map.addWidget(btn_map)
        l_file.addLayout(h_map)
        
        # Source Font
        h_in = QHBoxLayout()
        self.txt_font_in = QLineEdit()
        self.txt_font_in.setPlaceholderText(_("placeholder_font_in"))
        btn_in = QPushButton(_("btn_browse"))
        btn_in.setToolTip(_("tooltip_in"))
        btn_in.clicked.connect(self.browse_font_in)
        h_in.addWidget(self.txt_font_in)
        h_in.addWidget(btn_in)
        l_file.addLayout(h_in)
        
        # Output Font
        h_out = QHBoxLayout()
        self.txt_font_out = QLineEdit()
        self.txt_font_out.setPlaceholderText(_("placeholder_output_file"))
        btn_out = QPushButton(_("btn_browse"))
        btn_out.setToolTip(_("tooltip_out"))
        btn_out.clicked.connect(self.browse_font_out)
        h_out.addWidget(self.txt_font_out)
        h_out.addWidget(btn_out)
        l_file.addLayout(h_out)
        
        layout.addWidget(grp_file)
        
        # Action Group
        grp_action = QGroupBox(_("grp_action"))
        l_action = QHBoxLayout(grp_action)
        
        self.btn_generate_font = QPushButton(_("btn_generate_font"))
        self.btn_generate_font.setToolTip(_("tooltip_generate_font"))
        self.btn_generate_font.setStyleSheet("background: #f38ba8; color: #1e1e2e; font-size: 14px;")
        self.btn_generate_font.clicked.connect(self.generate_font)
        if not self.font_engine:
            self.btn_generate_font.setEnabled(False)
            self.btn_generate_font.setText(_("btn_font_engine_unavailable"))
            
        l_action.addWidget(self.btn_generate_font)
        layout.addWidget(grp_action)
        layout.addStretch()

    def log(self, text, color="#cdd6f4"):
        self.txt_log.append(f'<span style="color:{color};">{text}</span>')

    # --- TEXT CONVERTER METHODS ---
    def browse_input(self):
        path, _ext = QFileDialog.getOpenFileName(self, _("dialog_select_input"), "", "All Files (*.*)")
        if path:
            self.txt_input.setText(path)
            if not self.txt_output.text():
                base, ext = os.path.splitext(path)
                self.txt_output.setText(f"{base}_pua{ext}")
                
    def browse_output(self):
        path, _ext = QFileDialog.getSaveFileName(self, _("dialog_select_output"), "", "All Files (*.*)")
        if path:
            self.txt_output.setText(path)

    def read_file(self):
        path = self.txt_input.text()
        if not path or not os.path.exists(path):
            QMessageBox.warning(self, _("msg_error_title"), _("msg_input_not_found"))
            return None
        try:
            with open(path, 'r', encoding='utf-8-sig') as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                QMessageBox.critical(self, _("msg_error_title"), f"Cannot read file:\n{e}")
                return None
        except OSError as e:
            QMessageBox.critical(self, _("msg_error_title"), f"Could not read file:\n{e}")
            return None

    def save_file(self, content):
        path = self.txt_output.text()
        if not path: return False
        try:
            with open(path, 'w', encoding='utf-8-sig') as f:
                f.write(content)
            self.log(_("log_saved_to"), "#a6e3a1")
            return True
        except Exception as e:
            self.log(f"Error saving: {e}", "#f38ba8")
            return False

    def _set_buttons_enabled(self, enabled):
        self.btn_encode.setEnabled(enabled)
        self.btn_decode.setEnabled(enabled)
        self.btn_generate_font.setEnabled(enabled)

    def encode_file(self):
        if not self.engine: return
        text = self.read_file()
        if text is None: return
        self.log(_("log_encoding"), "#89b4fa")
        self._set_buttons_enabled(False)
        def run_encode():
            original_pua = sum(1 for c in text if 0xF000 <= ord(c) <= 0xF8FF)
            encoded = self.engine.encode(text)
            final_pua = sum(1 for c in encoded if 0xF000 <= ord(c) <= 0xF8FF)
            return encoded, original_pua, final_pua
        def on_success(res):
            encoded, original_pua, final_pua = res
            self.log(f"Encoded! Original PUA: {original_pua} -> Final PUA: {final_pua} (+{final_pua - original_pua})", "#f9e2af")
            self.save_file(encoded)
            self._set_buttons_enabled(True)
        def on_error(err):
            self.log(_("log_error_encoding"), "#f38ba8")
            self._set_buttons_enabled(True)
        worker = Worker(run_encode)
        worker.signals.finished.connect(on_success)
        worker.signals.error.connect(on_error)
        QThreadPool.globalInstance().start(worker)

    def decode_file(self):
        if not self.engine: return
        text = self.read_file()
        if text is None: return
        self.log(_("log_decoding"), "#cba6f7")
        self._set_buttons_enabled(False)
        def run_decode():
            original_pua = sum(1 for c in text if 0xF000 <= ord(c) <= 0xF8FF)
            decoded = self.engine.decode(text)
            final_pua = sum(1 for c in decoded if 0xF000 <= ord(c) <= 0xF8FF)
            return decoded, original_pua, final_pua
        def on_success(res):
            decoded, original_pua, final_pua = res
            self.log(f"Decoded! Original PUA: {original_pua} -> Final PUA: {final_pua} (-{original_pua - final_pua})", "#f9e2af")
            self.save_file(decoded)
            self._set_buttons_enabled(True)
        def on_error(err):
            self.log(_("log_error_decoding"), "#f38ba8")
            self._set_buttons_enabled(True)
        worker = Worker(run_decode)
        worker.signals.finished.connect(on_success)
        worker.signals.error.connect(on_error)
        QThreadPool.globalInstance().start(worker)

    # --- FONT GENERATOR METHODS ---
    def browse_font_map(self):
        path, _ext = QFileDialog.getOpenFileName(self, _("dialog_select_mapping"), "", "JSON Files (*.json);;All Files (*.*)")
        if path:
            self.txt_font_map.setText(path)
            try:
                self.font_engine.load_mapping(path)
                self.log(f"Custom Font Mapping loaded: {len(self.font_engine.mapping)} entries.", "#89b4fa")
            except Exception as e:
                QMessageBox.critical(self, _("msg_error_title"), str(e))

    def browse_font_in(self):
        path, _ext = QFileDialog.getOpenFileName(self, _("dialog_select_font_in"), "", "Font Files (*.ttf *.otf);;All Files (*.*)")
        if path:
            self.txt_font_in.setText(path)
            if not self.txt_font_out.text():
                base, ext = os.path.splitext(path)
                self.txt_font_out.setText(f"{base}_PUA{ext}")

    def browse_font_out(self):
        path, _ext = QFileDialog.getSaveFileName(self, _("dialog_select_font_out"), "", "Font Files (*.ttf *.otf);;All Files (*.*)")
        if path:
            self.txt_font_out.setText(path)

    def generate_font(self):
        if not self.font_engine:
            return
            
        in_path = self.txt_font_in.text()
        out_path = self.txt_font_out.text()
        
        if not os.path.exists(in_path):
            QMessageBox.warning(self, _("msg_error_title"), _("msg_source_font_not_found"))
            return
            
        if not out_path:
            QMessageBox.warning(self, _("msg_error_title"), _("msg_no_output_path"))
            return

        self.log(_("log_font_gen_start"), "#f38ba8")
        self._set_buttons_enabled(False)
        
        def run_generate(callback=None):
            return self.font_engine.process_font(in_path, out_path, callback=callback)
            
        def on_progress(msg):
            self.log(msg, "#89b4fa")
            
        def on_success(res):
            self.log(_("log_font_gen_done"), "#a6e3a1")
            self._set_buttons_enabled(True)
            
        def on_error(err):
            self.log(_("log_error_font_gen"), "#f38ba8")
            self._set_buttons_enabled(True)
            
        worker = Worker(run_generate)
        worker.signals.progress.connect(on_progress)
        worker.signals.finished.connect(on_success)
        worker.signals.error.connect(on_error)
        QThreadPool.globalInstance().start(worker)

    # --- LEGACY FONT (F700) METHODS ---
    def init_legacy_tab(self):
        layout = QVBoxLayout(self.tab_legacy)
        
        # Info Group
        h_info = QHBoxLayout()
        btn_info = QPushButton("❓ What is this tool?")
        btn_info.setStyleSheet("background: #f9e2af; color: #1e1e2e; font-size: 14px;")
        btn_info.clicked.connect(self.show_legacy_info)
        h_info.addWidget(btn_info)
        layout.addLayout(h_info)

        # File Group
        grp_file = QGroupBox("Legacy Font Settings")
        l_file = QVBoxLayout(grp_file)
        
        h_in = QHBoxLayout()
        self.txt_legacy_in = QLineEdit()
        self.txt_legacy_in.setPlaceholderText("Select Standard Source Font (.ttf)...")
        btn_in = QPushButton(_("btn_browse"))
        btn_in.clicked.connect(self.browse_legacy_in)
        h_in.addWidget(self.txt_legacy_in)
        h_in.addWidget(btn_in)
        l_file.addLayout(h_in)
        
        h_out = QHBoxLayout()
        self.txt_legacy_out = QLineEdit()
        self.txt_legacy_out.setPlaceholderText("Select Output Font File...")
        btn_out = QPushButton(_("btn_browse"))
        btn_out.clicked.connect(self.browse_legacy_out)
        h_out.addWidget(self.txt_legacy_out)
        h_out.addWidget(btn_out)
        l_file.addLayout(h_out)
        layout.addWidget(grp_file)

        # Offsets Group
        grp_off = QGroupBox("Coordinate Offsets (Units)")
        l_off = QHBoxLayout(grp_off)
        
        l_off.addWidget(QLabel("Y Raise (0=Auto):"))
        self.num_y_raise = QLineEdit("0")
        l_off.addWidget(self.num_y_raise)
        
        l_off.addWidget(QLabel("X Left:"))
        self.num_x_left = QLineEdit("-150")
        l_off.addWidget(self.num_x_left)
        
        l_off.addWidget(QLabel("Y Down:"))
        self.num_y_down = QLineEdit("-100")
        l_off.addWidget(self.num_y_down)
        
        layout.addWidget(grp_off)
        
        # Action Group
        grp_action = QGroupBox(_("grp_action"))
        l_action = QHBoxLayout(grp_action)
        
        self.btn_gen_legacy = QPushButton("Generate Legacy F700 Font")
        self.btn_gen_legacy.setStyleSheet("background: #f38ba8; color: #1e1e2e; font-size: 14px;")
        self.btn_gen_legacy.clicked.connect(self.generate_legacy_font)
        if not self.legacy_engine:
            self.btn_gen_legacy.setEnabled(False)
            self.btn_gen_legacy.setText("Legacy Engine Not Available")
            
        l_action.addWidget(self.btn_gen_legacy)
        layout.addWidget(grp_action)
        layout.addStretch()

    def show_legacy_info(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("About Legacy F700 Font Generator")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText(
            "<b>What is this tool?</b><br><br>"
            "This tool takes a standard Thai font and creates an additional 33 characters mapped to the "
            "<b>MacThai/Microsoft PUA standard (U+F700 - U+F71A)</b>.<br><br>"
            "<b>What does it do?</b><br>"
            "1. It clones standard vowels and tone marks.<br>"
            "2. It shifts them based on the offset parameters you provide (e.g. shifts Mai Ek UP by 250 units, or LEFT by -150 units).<br>"
            "3. It sets their width to 0 (Zero-width combining marks).<br><br>"
            "<b>When to use this?</b><br>"
            "Use this if you are modding a Unity game that already has a TextMeshPro Thai fixer script installed. "
            "These scripts expect the font to have F700 characters. If your game doesn't have such a script, use the standard TFont Font Generator instead."
        )
        msg.exec()

    def browse_legacy_in(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Standard Font", "", "Font Files (*.ttf *.otf);;All Files (*.*)")
        if path:
            self.txt_legacy_in.setText(path)
            if not self.txt_legacy_out.text():
                base, ext = os.path.splitext(path)
                self.txt_legacy_out.setText(f"{base}_F700{ext}")

    def browse_legacy_out(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save F700 Font", "", "Font Files (*.ttf *.otf);;All Files (*.*)")
        if path:
            self.txt_legacy_out.setText(path)

    def generate_legacy_font(self):
        if not self.legacy_engine: return
        in_path = self.txt_legacy_in.text()
        out_path = self.txt_legacy_out.text()
        if not os.path.exists(in_path):
            QMessageBox.warning(self, "Error", "Input font not found!")
            return
        
        try:
            y_r = int(self.num_y_raise.text())
            x_l = int(self.num_x_left.text())
            y_d = int(self.num_y_down.text())
        except ValueError:
            QMessageBox.warning(self, "Error", "Offsets must be integers.")
            return

        self.log("Starting Legacy F700 Generation... Please wait...", "#f38ba8")
        self._set_buttons_enabled(False)
        self.btn_gen_legacy.setEnabled(False)
        
        def run_generate(callback=None):
            return self.legacy_engine.process_font(in_path, out_path, y_r, x_l, y_d, callback=callback)
            
        def on_progress(msg):
            self.log(msg, "#89b4fa")
            
        def on_success(res):
            self.log("Legacy Font Generation Completed!", "#a6e3a1")
            self._set_buttons_enabled(True)
            self.btn_gen_legacy.setEnabled(True)
            
        def on_error(err):
            self.log(f"Error generating legacy font: {err}", "#f38ba8")
            self._set_buttons_enabled(True)
            self.btn_gen_legacy.setEnabled(True)
            
        worker = Worker(run_generate)
        worker.signals.progress.connect(on_progress)
        worker.signals.finished.connect(on_success)
        worker.signals.error.connect(on_error)
        QThreadPool.globalInstance().start(worker)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TFontApp()
    window.show()
    sys.exit(app.exec())
