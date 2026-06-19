import os
import subprocess
import numpy as np
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen, QPainterPath

class AudioExtractorWorker(QThread):
    finished = pyqtSignal(object, object) # min_amps, max_amps
    error = pyqtSignal(str)

    def __init__(self, ffmpeg_path, video_path):
        super().__init__()
        self.ffmpeg_path = ffmpeg_path
        self.video_path = video_path
        self.is_cancelled = False

    def run(self):
        temp_raw = os.path.join(os.path.dirname(self.video_path), "temp_tvox_audio.raw")
        try:
            # Extract mono 8kHz s16le audio
            cmd = [
                self.ffmpeg_path,
                "-i", self.video_path,
                "-vn", # no video
                "-ac", "1", # mono
                "-ar", "8000", # 8kHz
                "-f", "s16le", # raw 16-bit little-endian
                "-y", temp_raw
            ]
            
            # Hide console window on Windows
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, startupinfo=startupinfo)
            process.wait()

            if self.is_cancelled:
                return

            if not os.path.exists(temp_raw):
                self.error.emit("Failed to extract audio track.")
                return

            # Read raw data
            with open(temp_raw, 'rb') as f:
                raw_data = f.read()

            if len(raw_data) == 0:
                self.error.emit("Audio track is empty.")
                return

            audio_array = np.frombuffer(raw_data, dtype=np.int16)
            
            # Downsample to 100 samples per second
            samples_per_window = 8000 // 100 # 80 samples per 10ms window
            num_windows = len(audio_array) // samples_per_window
            
            if num_windows == 0:
                self.error.emit("Audio too short.")
                return

            reshaped = audio_array[:num_windows * samples_per_window].reshape((num_windows, samples_per_window))
            
            # Calculate min and max for each window (envelope)
            min_amps = np.min(reshaped, axis=1)
            max_amps = np.max(reshaped, axis=1)

            # Cleanup temp file
            try: os.remove(temp_raw)
            except: pass

            if not self.is_cancelled:
                self.finished.emit(min_amps, max_amps)

        except Exception as e:
            if not self.is_cancelled:
                self.error.emit(str(e))
            try:
                if os.path.exists(temp_raw): os.remove(temp_raw)
            except: pass

class WaveformWidget(QWidget):
    # Signals for syncing with MPV
    seek_requested = pyqtSignal(float)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(20)
        self.setStyleSheet("background-color: #1e1e2e; border: 1px solid #45475a; border-radius: 4px;")
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)  # Allow receiving spacebar events
        
        self.min_amps = None
        self.max_amps = None
        self.time_pos = 0.0
        self.duration = 1.0
        
        self.zoom = 100.0 # Pixels per second
        self.samples_per_sec = 100.0
        
        self.is_dragging = False
        self.drag_start_x = 0
        self.drag_start_time = 0.0
        
        # Colors (Catppuccin theme)
        self.bg_color = QColor("#1e1e2e")
        self.wave_color = QColor("#89b4fa")
        self.cursor_color = QColor("#f38ba8")
        self.grid_color = QColor("#313244")

    def set_audio_data(self, min_amps, max_amps):
        self.min_amps = min_amps
        self.max_amps = max_amps
        self.update()

    def update_position(self, time_pos, duration):
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        # Safety catch: if we think we're dragging but the left button is actually not pressed
        if self.is_dragging and not (QApplication.mouseButtons() & Qt.MouseButton.LeftButton):
            self.is_dragging = False
            
        if not self.is_dragging:
            self.time_pos = time_pos
        self.duration = duration if duration > 0 else 1.0
        self.update()

    def wheelEvent(self, event):
        # Zoom in/out
        delta = event.angleDelta().y()
        if delta > 0:
            self.zoom *= 1.2
        elif delta < 0:
            self.zoom /= 1.2
        
        # Clamp zoom
        self.zoom = max(10.0, min(self.zoom, 1000.0))
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.drag_start_x = event.position().x()
            self.drag_start_time = self.time_pos
            # Optional: if you want to jump to the clicked point instead of panning:
            # But the user complained it moves too fast, panning is much better!

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            current_x = event.position().x()
            dx = current_x - self.drag_start_x
            
            # Panning: drag right -> move back in time (time decreases)
            # drag left -> move forward in time (time increases)
            dt = -(dx / self.zoom)
            
            new_time = self.drag_start_time + dt
            new_time = max(0.0, min(new_time, self.duration))
            
            self.time_pos = new_time
            self.seek_requested.emit(new_time)
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
            # Final seek
            self.seek_requested.emit(self.time_pos)
            self.update()

    def paintEvent(self, event):
        from PyQt6.QtGui import QLinearGradient, QColor, QPen, QPainterPath
        from PyQt6.QtCore import Qt

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Fill background
        painter.fillRect(self.rect(), self.bg_color)
        
        w = self.width()
        h = self.height()
        center_x = w / 2.0
        center_y = h / 2.0
        
        # Draw Grid (Subtle 1 second marks)
        painter.setPen(QPen(QColor(255, 255, 255, 10), 1))
        left_time = self.time_pos - (center_x / self.zoom)
        right_time = self.time_pos + (center_x / self.zoom)
        
        first_sec = int(np.floor(left_time))
        last_sec = int(np.ceil(right_time))
        for sec in range(first_sec, last_sec + 1):
            if sec < 0 or sec > self.duration: continue
            x = center_x + (sec - self.time_pos) * self.zoom
            painter.drawLine(int(x), 0, int(x), int(h))
        
        # Draw Waveform as continuous polygon
        if self.min_amps is not None and self.max_amps is not None:
            first_idx = int(left_time * self.samples_per_sec)
            last_idx = int(right_time * self.samples_per_sec)
            
            first_idx = max(0, first_idx)
            last_idx = min(len(self.min_amps) - 1, last_idx)
            
            if first_idx < last_idx:
                path = QPainterPath()
                
                amp_scale = (h / 2.0) / 32768.0
                
                start_x = center_x + ((first_idx / self.samples_per_sec) - self.time_pos) * self.zoom
                path.moveTo(start_x, center_y - self.max_amps[first_idx] * amp_scale)
                
                for i in range(first_idx + 1, last_idx + 1):
                    x = center_x + ((i / self.samples_per_sec) - self.time_pos) * self.zoom
                    y = center_y - self.max_amps[i] * amp_scale
                    path.lineTo(x, y)
                    
                for i in range(last_idx, first_idx - 1, -1):
                    x = center_x + ((i / self.samples_per_sec) - self.time_pos) * self.zoom
                    y = center_y - self.min_amps[i] * amp_scale
                    path.lineTo(x, y)
                    
                path.closeSubpath()
                
                gradient = QLinearGradient(0, 0, w, 0)
                gradient.setColorAt(0.0, QColor("#4ade80")) # Greenish
                gradient.setColorAt(1.0, QColor("#2dd4bf")) # Cyan
                
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(gradient)
                painter.drawPath(path)
                
        # Draw Cursor (Center playhead)
        ph_gradient = QLinearGradient(0, 0, 0, h)
        ph_gradient.setColorAt(0.0, QColor("#a6e3a1"))
        ph_gradient.setColorAt(1.0, QColor("#94e2d5"))
        
        painter.setOpacity(1.0)
        painter.setPen(QPen(ph_gradient, 2))
        painter.drawLine(int(center_x), 0, int(center_x), int(h))
