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

try:
    from tpua_font import TPUAFontEngine
except ImportError:
    TPUAFontEngine = None

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
        self.setWindowTitle("TPUA: Universal PUA Hybrid Converter")
        self.resize(750, 550)
        self.setStyleSheet(DARK_SS)
        
        logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "assets", "TPUA.png"))
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))
        
        self.engine = TPUAEngine() if TPUAEngine else None
        self.font_engine = None
        if TPUAFontEngine:
            self.font_engine = TPUAFontEngine()
            
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
        
        # --- TAB 1: Text Converter ---
        self.tab_text = QWidget()
        self.init_text_tab()
        self.tabs.addTab(self.tab_text, "Text Converter")
        
        # --- TAB 2: Font Generator ---
        self.tab_font = QWidget()
        self.init_font_tab()
        self.tabs.addTab(self.tab_font, "Font Generator")
        
        # Log Window (Shared)
        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setStyleSheet("background: #181825; color: #a6adc8; font-family: Consolas, monospace;")
        main_layout.addWidget(self.txt_log)
        
        if self.engine:
            self.log(f"TPUA Engine Loaded. Standard Map: {len(self.engine.standard)} | Contextual: {len(self.engine.contextual)}", "#a6e3a1")
        if self.font_engine:
            self.log("TPUA Font Engine Loaded.", "#a6e3a1")
            if self.font_engine.mapping:
                self.log(f"Default Font Mapping loaded: {len(self.font_engine.mapping)} entries.", "#89b4fa")

    def init_text_tab(self):
        layout = QVBoxLayout(self.tab_text)
        
        # File Group
        grp_file = QGroupBox("File Selection")
        l_file = QVBoxLayout(grp_file)
        
        h_in = QHBoxLayout()
        self.txt_input = QLineEdit()
        self.txt_input.setPlaceholderText("Select Input File (.txt, .csv, .json)...")
        btn_in = QPushButton("Browse")
        btn_in.clicked.connect(self.browse_input)
        h_in.addWidget(self.txt_input)
        h_in.addWidget(btn_in)
        l_file.addLayout(h_in)
        
        h_out = QHBoxLayout()
        self.txt_output = QLineEdit()
        self.txt_output.setPlaceholderText("Select Output File...")
        btn_out = QPushButton("Browse")
        btn_out.clicked.connect(self.browse_output)
        h_out.addWidget(self.txt_output)
        h_out.addWidget(btn_out)
        l_file.addLayout(h_out)
        
        layout.addWidget(grp_file)
        
        # Action Group
        grp_action = QGroupBox("Action")
        l_action = QHBoxLayout(grp_action)
        
        self.btn_encode = QPushButton("Encode (Thai -> PUA)")
        self.btn_encode.setStyleSheet("background: #cba6f7; color: #1e1e2e; font-size: 14px;")
        self.btn_encode.clicked.connect(self.encode_file)
        if not self.engine: self.btn_encode.setEnabled(False)
        
        self.btn_decode = QPushButton("Decode (PUA -> Thai)")
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
        grp_file = QGroupBox("Font Settings")
        l_file = QVBoxLayout(grp_file)
        
        # Mapping file
        h_map = QHBoxLayout()
        self.txt_font_map = QLineEdit()
        self.txt_font_map.setPlaceholderText("Select Mapping.json (Optional, defaults to Noonetranslator map)")
        if self.font_engine and self.font_engine.mapping:
            self.txt_font_map.setText(self.default_mapping_path)
            
        btn_map = QPushButton("Browse")
        btn_map.clicked.connect(self.browse_font_map)
        h_map.addWidget(self.txt_font_map)
        h_map.addWidget(btn_map)
        l_file.addLayout(h_map)
        
        # Source Font
        h_in = QHBoxLayout()
        self.txt_font_in = QLineEdit()
        self.txt_font_in.setPlaceholderText("Select Source Font File (.ttf)...")
        btn_in = QPushButton("Browse")
        btn_in.clicked.connect(self.browse_font_in)
        h_in.addWidget(self.txt_font_in)
        h_in.addWidget(btn_in)
        l_file.addLayout(h_in)
        
        # Output Font
        h_out = QHBoxLayout()
        self.txt_font_out = QLineEdit()
        self.txt_font_out.setPlaceholderText("Select Output File...")
        btn_out = QPushButton("Browse")
        btn_out.clicked.connect(self.browse_font_out)
        h_out.addWidget(self.txt_font_out)
        h_out.addWidget(btn_out)
        l_file.addLayout(h_out)
        
        layout.addWidget(grp_file)
        
        # Action Group
        grp_action = QGroupBox("Action")
        l_action = QHBoxLayout(grp_action)
        
        self.btn_generate_font = QPushButton("Generate PUA Fonts")
        self.btn_generate_font.setStyleSheet("background: #f38ba8; color: #1e1e2e; font-size: 14px;")
        self.btn_generate_font.clicked.connect(self.generate_font)
        if not self.font_engine:
            self.btn_generate_font.setEnabled(False)
            self.btn_generate_font.setText("Font Engine Not Available (Missing fontTools)")
            
        l_action.addWidget(self.btn_generate_font)
        layout.addWidget(grp_action)
        layout.addStretch()

    def log(self, text, color="#cdd6f4"):
        self.txt_log.append(f'<span style="color:{color};">{text}</span>')

    # --- TEXT CONVERTER METHODS ---
    def browse_input(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Input File", "", "All Files (*.*)")
        if path:
            self.txt_input.setText(path)
            if not self.txt_output.text():
                base, ext = os.path.splitext(path)
                self.txt_output.setText(f"{base}_pua{ext}")
                
    def browse_output(self):
        path, _ = QFileDialog.getSaveFileName(self, "Select Output File", "", "All Files (*.*)")
        if path:
            self.txt_output.setText(path)

    def read_file(self):
        path = self.txt_input.text()
        if not path or not os.path.exists(path):
            QMessageBox.warning(self, "Error", "Input file not found!")
            return None
        try:
            with open(path, 'r', encoding='utf-8-sig') as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Cannot read file:\n{e}")
                return None
        except OSError as e:
            QMessageBox.critical(self, "Error", f"Could not read file:\n{e}")
            return None

    def save_file(self, content):
        path = self.txt_output.text()
        if not path: return False
        try:
            with open(path, 'w', encoding='utf-8-sig') as f:
                f.write(content)
            self.log(f"Saved to: {path}", "#a6e3a1")
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
        self.log("Encoding Thai to PUA... Please wait...", "#89b4fa")
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
            self.log(f"Error encoding: {err}", "#f38ba8")
            self._set_buttons_enabled(True)
        worker = Worker(run_encode)
        worker.signals.finished.connect(on_success)
        worker.signals.error.connect(on_error)
        QThreadPool.globalInstance().start(worker)

    def decode_file(self):
        if not self.engine: return
        text = self.read_file()
        if text is None: return
        self.log("Decoding PUA to Thai... Please wait...", "#cba6f7")
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
            self.log(f"Error decoding: {err}", "#f38ba8")
            self._set_buttons_enabled(True)
        worker = Worker(run_decode)
        worker.signals.finished.connect(on_success)
        worker.signals.error.connect(on_error)
        QThreadPool.globalInstance().start(worker)

    # --- FONT GENERATOR METHODS ---
    def browse_font_map(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Mapping.json", "", "JSON Files (*.json);;All Files (*.*)")
        if path:
            self.txt_font_map.setText(path)
            try:
                self.font_engine.load_mapping(path)
                self.log(f"Custom Font Mapping loaded: {len(self.font_engine.mapping)} entries.", "#89b4fa")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def browse_font_in(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Source Font File", "", "Font Files (*.ttf *.otf);;All Files (*.*)")
        if path:
            self.txt_font_in.setText(path)
            if not self.txt_font_out.text():
                base, ext = os.path.splitext(path)
                self.txt_font_out.setText(f"{base}_PUA{ext}")

    def browse_font_out(self):
        path, _ = QFileDialog.getSaveFileName(self, "Select Output Font File", "", "Font Files (*.ttf *.otf);;All Files (*.*)")
        if path:
            self.txt_font_out.setText(path)

    def generate_font(self):
        if not self.font_engine:
            return
            
        in_path = self.txt_font_in.text()
        out_path = self.txt_font_out.text()
        
        if not os.path.exists(in_path):
            QMessageBox.warning(self, "Error", "Source font file not found.")
            return
            
        if not out_path:
            QMessageBox.warning(self, "Error", "Please specify an output path.")
            return

        self.log("Starting Font PUA Generation... Please wait...", "#f38ba8")
        self._set_buttons_enabled(False)
        
        def run_generate(callback=None):
            return self.font_engine.process_font(in_path, out_path, callback=callback)
            
        def on_progress(msg):
            self.log(msg, "#89b4fa")
            
        def on_success(res):
            self.log("Font Generation Completed Successfully!", "#a6e3a1")
            self._set_buttons_enabled(True)
            
        def on_error(err):
            self.log(f"Error generating font: {err}", "#f38ba8")
            self._set_buttons_enabled(True)
            
        worker = Worker(run_generate)
        worker.signals.progress.connect(on_progress)
        worker.signals.finished.connect(on_success)
        worker.signals.error.connect(on_error)
        QThreadPool.globalInstance().start(worker)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TPUAApp()
    window.show()
    sys.exit(app.exec())
