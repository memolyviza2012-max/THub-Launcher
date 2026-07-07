import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGraphicsView, 
                             QGraphicsScene, QGraphicsPathItem, QSlider, QLabel, 
                             QPushButton, QLineEdit, QFileDialog, QMessageBox, QGroupBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPen, QBrush, QColor, QTransform, QPainter
import sys

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
        
        self.y_raise = 350
        self.x_left = -150
        self.y_down = -150

        # Sample test strings
        self.test_words = ["ปี้", "ฟุ้ง", "ที่", "น้ำ", "ฎู", "ฐิ"]
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

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
        
        layout.addLayout(h_file)

        # Canvas
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setBackgroundBrush(QBrush(QColor("#1e1e2e")))
        self.view.setMinimumHeight(300)
        
        # Scale view so TTF units (usually 2048) fit in the view
        # We'll apply a scaling transform to the view later when drawing
        layout.addWidget(self.view)

        # Sliders group
        grp_sliders = QGroupBox(_("visual_tuner_realtime") if hasattr(self, '_') else "Real-time Tuning")
        l_sliders = QVBoxLayout(grp_sliders)
        
        # Y Raise
        self.lbl_y_raise = QLabel((_("visual_tuner_y_raise") if hasattr(self, '_') else "Y Raise (Tone Marks):") + f" {self.y_raise}")
        self.slider_y = QSlider(Qt.Orientation.Horizontal)
        self.slider_y.setRange(0, 800)
        self.slider_y.setValue(self.y_raise)
        self.slider_y.valueChanged.connect(self.on_y_raise_changed)
        l_sliders.addWidget(self.lbl_y_raise)
        l_sliders.addWidget(self.slider_y)

        # X Left
        self.lbl_x_left = QLabel((_("visual_tuner_x_left") if hasattr(self, '_') else "X Left (Dodge Tails):") + f" {self.x_left}")
        self.slider_x = QSlider(Qt.Orientation.Horizontal)
        self.slider_x.setRange(-400, 0)
        self.slider_x.setValue(self.x_left)
        self.slider_x.valueChanged.connect(self.on_x_left_changed)
        l_sliders.addWidget(self.lbl_x_left)
        l_sliders.addWidget(self.slider_x)
        
        # Y Down
        self.lbl_y_down = QLabel((_("visual_tuner_y_down") if hasattr(self, '_') else "Y Down (Lower Vowels):") + f" {self.y_down}")
        self.slider_d = QSlider(Qt.Orientation.Horizontal)
        self.slider_d.setRange(-400, 0)
        self.slider_d.setValue(self.y_down)
        self.slider_d.valueChanged.connect(self.on_y_down_changed)
        l_sliders.addWidget(self.lbl_y_down)
        l_sliders.addWidget(self.slider_d)

        layout.addWidget(grp_sliders)

        # Export Button
        self.btn_export = QPushButton("💾 " + (_("visual_tuner_export") if hasattr(self, '_') else "Export Tuned F700 Font"))
        self.btn_export.setStyleSheet("background: #a6e3a1; color: #11111b; font-size: 16px; padding: 12px;")
        self.btn_export.clicked.connect(self.export_font)
        layout.addWidget(self.btn_export)

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

    def on_y_raise_changed(self, val):
        self.y_raise = val
        self.lbl_y_raise.setText((_("visual_tuner_y_raise") if hasattr(self, '_') else "Y Raise (Tone Marks):") + f" {self.y_raise}")
        self.draw_preview()

    def on_x_left_changed(self, val):
        self.x_left = val
        self.lbl_x_left.setText((_("visual_tuner_x_left") if hasattr(self, '_') else "X Left (Dodge Tails):") + f" {self.x_left}")
        self.draw_preview()

    def on_y_down_changed(self, val):
        self.y_down = val
        self.lbl_y_down.setText((_("visual_tuner_y_down") if hasattr(self, '_') else "Y Down (Lower Vowels):") + f" {self.y_down}")
        self.draw_preview()

    def draw_preview(self):
        if not self.visual_engine: return
        self.scene.clear()

        # Qt's coordinate system is Y-down. TTF is Y-up.
        # We need a base transform to flip Y and scale down (e.g. by 0.1 for a 2048 UPM font)
        scale_factor = 0.08
        base_transform = QTransform().scale(scale_factor, -scale_factor)

        # Start drawing cursors
        current_x = 0
        baseline_y = 0

        # Colors for different parts
        c_base = QColor("#cdd6f4")
        c_upper = QColor("#89b4fa")
        c_tone = QColor("#f38ba8")
        c_lower = QColor("#a6e3a1")

        for word in self.test_words:
            word_start_x = current_x
            # We must group characters in a cell. 
            # Thai logic: Base -> Lower/Upper Vowel -> Tone
            
            for char in word:
                path, width = self.visual_engine.get_glyph_path_and_width(char)
                if path.isEmpty(): continue
                
                cat = self.visual_engine.get_f700_type(char)
                
                # Setup offset
                dx, dy = 0, 0
                color = c_base
                
                if cat == 'upper_vowel':
                    color = c_upper
                    # In F700, some upper vowels are left shifted (ป, ฝ, ฟ).
                    # Since our test word is 'ปี้', 'ป' has a long tail, so vowel shifts left.
                    # We will visually apply x_left to all upper vowels just for the preview to see how it looks.
                    dx = self.x_left
                elif cat == 'tone_mark':
                    color = c_tone
                    dx = self.x_left # Usually left shifted if there's a long tail
                    dy = self.y_raise
                elif cat == 'lower_vowel':
                    color = c_lower
                    dy = self.y_down

                # Position the path
                # TTF path is at (0,0). We move it to current_x + dx, baseline_y + dy
                char_transform = QTransform().translate(current_x + dx, baseline_y + dy)
                transformed_path = char_transform.map(path)
                
                # Apply global view scale and Y-flip
                final_path = base_transform.map(transformed_path)
                
                # Draw
                item = self.scene.addPath(final_path, QPen(Qt.PenStyle.NoPen), QBrush(color))
                
                # Only advance X if it's a base character (vowels/tones have 0 width in F700)
                if cat == 'base':
                    current_x += width

            # Add spacing between test words
            current_x += self.visual_engine.upm * 0.5
            
        # Adjust scene rect so it fits nicely
        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        # Center view vertically, align left horizontally
        self.view.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

    def export_font(self):
        in_path = self.txt_in.text()
        out_path = self.txt_out.text()
        if not os.path.exists(in_path):
            QMessageBox.warning(self, "Error", "Source font not found.")
            return

        self.btn_export.setEnabled(False)
        self.logger("Exporting F700 Tuned Font via Legacy Engine...", "#f38ba8")
        
        # We can run this in a thread or directly. For simplicity, directly if it's fast.
        try:
            self.legacy_engine.process_font(in_path, out_path, self.y_raise, self.x_left, self.y_down, callback=self.logger_callback)
            self.logger("Export Complete!", "#a6e3a1")
        except Exception as e:
            self.logger(f"Error exporting: {e}", "#f38ba8")
            QMessageBox.critical(self, "Error", str(e))
        finally:
            self.btn_export.setEnabled(True)

    def logger_callback(self, msg):
        self.logger(msg, "#89b4fa")
