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
    from tpua_engine import TPUAEngine
except ImportError:
    TPUAEngine = None



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

class TPUAApp(QMainWindow):
    def __init__(self):
        super().__init__()
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('flagship.tpua.app.1.0')
        except:
            pass
        self.setWindowTitle(_("app_title"))
        self.resize(750, 550)
        self.setStyleSheet(DARK_SS)
        
        logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "assets", "TPUA.png"))
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))
        
        self.engine = TPUAEngine() if TPUAEngine else None
                
        self.init_ui()
        
    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # --- TAB 1: Text Converter ---
        self.tab_text = QWidget()
        self.init_text_tab()
        tpua_logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "assets", "TPUA.png"))
        if os.path.exists(tpua_logo_path):
            self.tabs.addTab(self.tab_text, QIcon(tpua_logo_path), _("tab_text_converter"))
        else:
            self.tabs.addTab(self.tab_text, _("tab_text_converter"))
        
        # Log Window (Shared)
        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setStyleSheet("background: #181825; color: #a6adc8; font-family: Consolas, monospace;")
        main_layout.addWidget(self.txt_log)
        
        if self.engine:
            self.log(f"TFont Engine Loaded. Standard Map: {len(self.engine.standard)} | Contextual: {len(self.engine.contextual)}", "#a6e3a1")

    def init_text_tab(self):
        layout = QVBoxLayout(self.tab_text)
        
        # File Group
        grp_file = QGroupBox(_("grp_file_selection"))
        l_file = QVBoxLayout(grp_file)
        
        h_in = QHBoxLayout()
        self.txt_input = QLineEdit()
        self.txt_input.setPlaceholderText(_("placeholder_input_file"))
        btn_in = QPushButton(_("btn_browse"))
        btn_in.setToolTip(_("tooltip_in"))
        btn_in.clicked.connect(self.browse_input)
        h_in.addWidget(self.txt_input)
        h_in.addWidget(btn_in)
        l_file.addLayout(h_in)
        
        h_out = QHBoxLayout()
        self.txt_output = QLineEdit()
        self.txt_output.setPlaceholderText(_("placeholder_output_file"))
        btn_out = QPushButton(_("btn_browse"))
        btn_out.setToolTip(_("tooltip_out"))
        btn_out.clicked.connect(self.browse_output)
        h_out.addWidget(self.txt_output)
        h_out.addWidget(btn_out)
        l_file.addLayout(h_out)
        
        layout.addWidget(grp_file)
        
        # Action Group
        grp_action = QGroupBox(_("grp_action"))
        l_action = QHBoxLayout(grp_action)
        
        self.btn_encode = QPushButton(_("btn_encode"))
        self.btn_encode.setToolTip(_("tooltip_encode"))
        self.btn_encode.setStyleSheet("background: #cba6f7; color: #1e1e2e; font-size: 14px;")
        self.btn_encode.clicked.connect(self.encode_file)
        if not self.engine: self.btn_encode.setEnabled(False)
        
        self.btn_decode = QPushButton(_("btn_decode"))
        self.btn_decode.setToolTip(_("tooltip_decode"))
        self.btn_decode.setStyleSheet("background: #a6e3a1; color: #1e1e2e; font-size: 14px;")
        self.btn_decode.clicked.connect(self.decode_file)
        if not self.engine: self.btn_decode.setEnabled(False)
        
        l_action.addWidget(self.btn_encode)
        l_action.addWidget(self.btn_decode)
        layout.addWidget(grp_action)
        layout.addStretch()

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TPUAApp()
    window.show()
    sys.exit(app.exec())
