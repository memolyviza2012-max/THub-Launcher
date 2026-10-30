import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGraphicsView, 
                             QGraphicsScene, QGraphicsPathItem, QSlider, QLabel, 
                             QPushButton, QLineEdit, QFileDialog, QMessageBox, QGroupBox, QSpinBox,
                             QScrollArea, QGridLayout, QCheckBox)
from PyQt6.QtCore import Qt, QThreadPool, QRunnable, QObject, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QPen, QBrush, QColor, QTransform, QPainter
import sys

class _WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str)
    progress = pyqtSignal(str)

class _Worker(QRunnable):
    def __init__(self, fn):
        super().__init__()
        self.fn = fn
        self.signals = _WorkerSignals()
    @pyqtSlot()
    def run(self):
        try:
            self.fn()
            self.signals.finished.emit()
        except Exception as e:
            import traceback
            self.signals.error.emit(traceback.format_exc())

# Ensure parent path is in sys.path for tfont_i18n
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    from tfont_i18n import _
except ImportError:
    _ = lambda x: x

try:
    from visual_font_engine import VisualFontEngine
except ImportError:
    VisualFontEngine = None

class VisualTunerWidget(QWidget):
    def __init__(self, legacy_font_engine, logger_callback):
        super().__init__()
        self.legacy_engine = legacy_font_engine
        self.logger = logger_callback
        self.visual_engine = None
        
        # Base Offsets (modify original glyphs directly)
        self.base_tone_y = 160 # Lift tone marks up by 160 units to prevent overlapping ั or ี
        self.base_upper_vowel_y = 0
        self.base_lower_vowel_y = 0
        
        # PUA Offsets
        self.upper_vowel_left_x = -150
        self.upper_vowel_left_y = 0
        
        self.tone_raised_x = 0
        self.tone_raised_y = 286 # New default based on typical worst-case
        
        self.tone_left_x = -150
        self.tone_left_y = 0
        
        self.tone_left_raised_x = -150
        self.tone_left_raised_y = 286
        
        self.lower_vowel_down_x = 0
        self.lower_vowel_down_y = -150

        # Sample test strings (showing normal words and complex combinations)
        self.test_words = ["ปี้", "ฟุ้ง", "ที่", "น้ำ", "ฎู", "ฐิ", "กั้", "ย้ำ"]
        
        self.preview_f700 = False # Default to normal preview to show base shift effect
        
        self.init_ui()

    def create_slider_row(self, label_text, var_name, min_val=-2048, max_val=2048):
        h = QHBoxLayout()
        lbl = QLabel(label_text)
        lbl.setMinimumWidth(180)
        
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(min_val, max_val)
        current_val = getattr(self, var_name)
        slider.setValue(current_val)
        
        spin = QSpinBox()
        spin.setRange(min_val, max_val)
        spin.setValue(current_val)
        
        slider.valueChanged.connect(spin.setValue)
        spin.valueChanged.connect(slider.setValue)
        
        def on_change(val, name=var_name):
            setattr(self, name, val)
            self.draw_preview()
            
        spin.valueChanged.connect(on_change)
        
        h.addWidget(lbl)
        h.addWidget(slider)
        h.addWidget(spin)
        return h

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # File Selection
        h_file = QHBoxLayout()
        self.txt_in = QLineEdit()
        self.txt_in.setPlaceholderText(_("startup_font_placeholder") if hasattr(self, '_') else "Select Source Font (.ttf)...")
        btn_browse_in = QPushButton(_("btn_browse") if hasattr(self, '_') else "Browse")
        btn_browse_in.clicked.connect(self.browse_in)
        h_file.addWidget(self.txt_in)
        h_file.addWidget(btn_browse_in)

        self.txt_out = QLineEdit()
        self.txt_out.setPlaceholderText(_("gen_font_output_placeholder") if hasattr(self, '_') else "Output Font File...")
        btn_browse_out = QPushButton(_("btn_browse") if hasattr(self, '_') else "Browse")
        btn_browse_out.clicked.connect(self.browse_out)
        h_file.addWidget(self.txt_out)
        h_file.addWidget(btn_browse_out)
        
        main_layout.addLayout(h_file)

        # Canvas
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setBackgroundBrush(QBrush(QColor("#1e1e2e")))
        self.view.setMinimumHeight(200)
        main_layout.addWidget(self.view)
        
        # Preview Controls
        h_prev = QHBoxLayout()
        self.chk_f700 = QCheckBox("Preview as F700 (simulate game text replacement)")
        self.chk_f700.setChecked(self.preview_f700)
        self.chk_f700.toggled.connect(self.on_preview_mode_changed)
        h_prev.addWidget(self.chk_f700)
        main_layout.addLayout(h_prev)

        # Scroll Area for sliders
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # Base Unicode Shift Group
        grp_base = QGroupBox("Base Unicode Shift (Permanent Shift)")
        l_base = QVBoxLayout(grp_base)
        l_base.addLayout(self.create_slider_row("Tone Marks Y (่ ้ ๊ ๋ ์):", "base_tone_y"))
        l_base.addLayout(self.create_slider_row("Upper Vowels Y (ิ ี ึ ื ั ํ ็):", "base_upper_vowel_y"))
        l_base.addLayout(self.create_slider_row("Lower Vowels Y (ุ ู ฺ):", "base_lower_vowel_y"))
        scroll_layout.addWidget(grp_base)

        # PUA F700 Group
        grp_pua = QGroupBox("PUA F700 Shift (Requires game replacement)")
        l_pua = QGridLayout(grp_pua)
        
        # Left side
        l_l = QVBoxLayout()
        l_l.addLayout(self.create_slider_row("Upper Vowel Left (X):", "upper_vowel_left_x"))
        l_l.addLayout(self.create_slider_row("Tone Raised (Y):", "tone_raised_y"))
        l_l.addLayout(self.create_slider_row("Tone Left (X):", "tone_left_x"))
        l_l.addLayout(self.create_slider_row("Tone L+R (X):", "tone_left_raised_x"))
        l_l.addLayout(self.create_slider_row("Lower Down (Y):", "lower_vowel_down_y"))
        l_pua.addLayout(l_l, 0, 0)
        
        # Right side
        l_r = QVBoxLayout()
        l_r.addLayout(self.create_slider_row("Upper Vowel Left (Y):", "upper_vowel_left_y"))
        l_r.addLayout(self.create_slider_row("Tone Raised (X):", "tone_raised_x"))
        l_r.addLayout(self.create_slider_row("Tone Left (Y):", "tone_left_y"))
        l_r.addLayout(self.create_slider_row("Tone L+R (Y):", "tone_left_raised_y"))
        l_r.addLayout(self.create_slider_row("Lower Down (X):", "lower_vowel_down_x"))
        l_pua.addLayout(l_r, 0, 1)
        
        scroll_layout.addWidget(grp_pua)
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        # Export Button
        self.btn_export = QPushButton("💾 " + (_("visual_tuner_export") if hasattr(self, '_') else "Export Tuned Font"))
        self.btn_export.setStyleSheet("background: #a6e3a1; color: #11111b; font-size: 16px; padding: 12px;")
        self.btn_export.clicked.connect(self.export_font)
        main_layout.addWidget(self.btn_export)

    def browse_in(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Font", "", "Font Files (*.ttf *.otf);;All Files (*.*)")
        if path:
            self.txt_in.setText(path)
            if not self.txt_out.text():
                base, ext = os.path.splitext(path)
                self.txt_out.setText(f"{base}_TunedF700{ext}")
            self.load_font(path)

    def browse_out(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Font", "", "Font Files (*.ttf *.otf);;All Files (*.*)")
        if path:
            self.txt_out.setText(path)

    def load_font(self, path):
        if not VisualFontEngine:
            QMessageBox.warning(self, "Error", "VisualFontEngine module not loaded.")
            return
        try:
            if self.visual_engine:
                self.visual_engine.close()
            self.visual_engine = VisualFontEngine(path)
            self.logger("Loaded font for Visual Tuner.", "#89b4fa")
            self.draw_preview()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load font: {e}")

    def on_preview_mode_changed(self, checked):
        self.preview_f700 = checked
        self.draw_preview()

    def get_offsets(self):
        return {
            'base_tone_y': self.base_tone_y,
            'base_upper_vowel_y': self.base_upper_vowel_y,
            'base_lower_vowel_y': self.base_lower_vowel_y,
            'upper_vowel_left_x': self.upper_vowel_left_x,
            'upper_vowel_left_y': self.upper_vowel_left_y,
            'tone_raised_x': self.tone_raised_x,
            'tone_raised_y': self.tone_raised_y,
            'tone_left_x': self.tone_left_x,
            'tone_left_y': self.tone_left_y,
            'tone_left_raised_x': self.tone_left_raised_x,
            'tone_left_raised_y': self.tone_left_raised_y,
            'lower_vowel_down_x': self.lower_vowel_down_x,
            'lower_vowel_down_y': self.lower_vowel_down_y
        }

    def draw_preview(self):
        if not self.visual_engine: return
        self.scene.clear()

        scale_factor = 0.08
        base_transform = QTransform().scale(scale_factor, -scale_factor)

        current_x = 0
        baseline_y = 0

        c_base = QColor("#cdd6f4")
        c_upper = QColor("#89b4fa")
        c_tone = QColor("#f38ba8")
        c_lower = QColor("#a6e3a1")

        for word in self.test_words:
            word_start_x = current_x
            has_long_tail = False
            has_lower_tail = False
            has_upper_vowel = False
            
            for char in word:
                if char in ['ป', 'ฝ', 'ฟ']: has_long_tail = True
                elif char in ['ฎ', 'ฏ']: has_lower_tail = True
                elif char in ['ิ', 'ี', 'ึ', 'ื', 'ั', 'ํ', '็', 'ำ']: has_upper_vowel = True
                
                path, width = self.visual_engine.get_glyph_path_and_width(char)
                if path.isEmpty(): continue
                
                cat = self.visual_engine.get_f700_type(char)
                
                dx, dy = 0, 0
                color = c_base
                
                # Apply shifts based on preview mode
                if cat == 'upper_vowel':
                    color = c_upper
                    if self.preview_f700 and has_long_tail:
                        dx, dy = self.upper_vowel_left_x, self.upper_vowel_left_y
                    else:
                        dy = self.base_upper_vowel_y
                        
                elif cat == 'tone_mark':
                    color = c_tone
                    if self.preview_f700:
                        if has_long_tail and has_upper_vowel:
                            dx, dy = self.tone_left_raised_x, self.tone_left_raised_y
                        elif has_long_tail:
                            dx, dy = self.tone_left_x, self.tone_left_y
                        elif has_upper_vowel:
                            dx, dy = self.tone_raised_x, self.tone_raised_y
                        else:
                            dy = self.base_tone_y # If no F700 trigger, falls back to base shift
                    else:
                        dy = self.base_tone_y
                        
                elif cat == 'lower_vowel':
                    color = c_lower
                    if self.preview_f700 and has_lower_tail:
                        dx, dy = self.lower_vowel_down_x, self.lower_vowel_down_y
                    else:
                        dy = self.base_lower_vowel_y

                char_transform = QTransform().translate(current_x + dx, baseline_y + dy)
                transformed_path = char_transform.map(path)
                final_path = base_transform.map(transformed_path)
                
                item = self.scene.addPath(final_path, QPen(Qt.PenStyle.NoPen), QBrush(color))
                
                if cat == 'base':
                    current_x += width

            current_x += self.visual_engine.upm * 0.5
            
        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        self.view.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

    def export_font(self):
        in_path = self.txt_in.text()
        out_path = self.txt_out.text()
        if not os.path.exists(in_path):
            QMessageBox.warning(self, "Error", "Source font not found.")
            return
        if not out_path:
            QMessageBox.warning(self, "Error", "No output path specified.")
            return

        self.btn_export.setEnabled(False)
        self.logger("Exporting Advanced Font via Legacy Engine...", "#f38ba8")
        
        offsets = self.get_offsets()
        
        def run_export():
            # Emit progress signal safely instead of directly updating GUI
            self.legacy_engine.process_font(in_path, out_path, offsets=offsets, callback=worker.signals.progress.emit)
        
        def on_done():
            self.logger("Export Complete!", "#a6e3a1")
            self.btn_export.setEnabled(True)
            self._export_worker = None
        
        def on_error(err):
            self.logger(f"Error exporting: {err}", "#f38ba8")
            self.btn_export.setEnabled(True)
            self._export_worker = None
            
        def on_progress(msg):
            self.logger_callback(msg)
        
        worker = _Worker(run_export)
        self._export_worker = worker  # Keep reference to prevent GC
        worker.signals.progress.connect(on_progress)
        worker.signals.finished.connect(on_done)
        worker.signals.error.connect(on_error)
        QThreadPool.globalInstance().start(worker)

    def logger_callback(self, msg):
        self.logger(msg, "#89b4fa")
