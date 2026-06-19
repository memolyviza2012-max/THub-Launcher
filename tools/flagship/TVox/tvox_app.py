import sys
import os

# Append paths
flagship_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(flagship_dir, 'Core'))
sys.path.append(os.path.join(flagship_dir, 'TStudio'))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QSplitter, QFileDialog, QMessageBox,
    QSlider, QLabel, QComboBox, QGroupBox
)
from PyQt6.QtCore import Qt, QTimer

# Prepend TVox dir to PATH so libmpv-2.dll is found automatically
os.environ["PATH"] = os.path.dirname(os.path.abspath(__file__)) + os.pathsep + os.environ["PATH"]

try:
    import mpv
    MPV_AVAILABLE = True
    MPV_ERROR = ""
except OSError as e:
    MPV_AVAILABLE = False
    MPV_ERROR = str(e)
except Exception as e:
    MPV_AVAILABLE = False
    MPV_ERROR = str(e)

# Import TranslationStudio to inherit all its AI/Glossary/Table features!
try:
    from tstudio_app import TranslationStudio
    HAS_TSTUDIO = True
except ImportError as e:
    HAS_TSTUDIO = False
    print(f"Failed to import TStudio: {e}")

if HAS_TSTUDIO:
    class TVoxApp(TranslationStudio):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("TVox - FMV Modding Studio (Powered by TStudio Engine)")
            self.setGeometry(100, 100, 1400, 900)

            # --- Internal State ---
            self.is_user_seeking = False
            self.mark_a = None
            self.mark_b = None
            self.loop_active = False

            # 1. Capture the existing UI that TStudio built
            tstudio_widget = self.centralWidget()
            tstudio_widget.setParent(None) # Detach from window
            
            # 2. Re-attach tstudio_widget as the main central widget
            self.setCentralWidget(tstudio_widget)
            
            # 3. Create DockWidget for Video
            from PyQt6.QtWidgets import QDockWidget, QMainWindow
            self.video_dock = QDockWidget(" ⠿ TVox Video Player ", self)
            self.video_dock.setAllowedAreas(Qt.DockWidgetArea.TopDockWidgetArea | Qt.DockWidgetArea.BottomDockWidgetArea | Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
            self.video_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetFloatable | QDockWidget.DockWidgetFeature.DockWidgetMovable)
            self.setDockOptions(self.dockOptions() | QMainWindow.DockOption.AllowNestedDocks)
            
            # 4. Build Video Player
            self.video_container = QWidget()
            self.video_container.setStyleSheet("background-color: black;")
            self.video_layout = QVBoxLayout(self.video_container)
            self.video_layout.setContentsMargins(0,0,0,0)
            self.video_layout.setSpacing(0)
            
            self.video_widget = QWidget()
            self.video_widget.setAttribute(Qt.WidgetAttribute.WA_DontCreateNativeAncestors)
            self.video_widget.setAttribute(Qt.WidgetAttribute.WA_NativeWindow)
            self.video_widget.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
            self.video_widget.installEventFilter(self)
            self.video_layout.addWidget(self.video_widget, stretch=1)
            
            # --- Subtitle Overlay ---
            self.lbl_subtitle = QLabel(self.video_container)
            self.lbl_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.lbl_subtitle.setWordWrap(True)
            self.lbl_subtitle.setStyleSheet("""
                QLabel {
                    color: white;
                    font-size: 32px;
                    font-weight: bold;
                    background-color: transparent;
                    /* Basic shadow effect */
                    text-shadow: 2px 2px 4px #000000;
                }
            """)
            # Create a simple drop shadow effect
            from PyQt6.QtWidgets import QGraphicsDropShadowEffect
            shadow = QGraphicsDropShadowEffect(self.lbl_subtitle)
            shadow.setBlurRadius(8)
            shadow.setColor(Qt.GlobalColor.black)
            shadow.setOffset(2, 2)
            self.lbl_subtitle.setGraphicsEffect(shadow)
            self.lbl_subtitle.setText("") # Start empty
            self.lbl_subtitle.hide()

            # --- Timeline & Controls Panel (Compact Mode) ---
            self.panel_widget = QWidget()
            self.panel_widget.setStyleSheet("background-color: #1e1e2e;")
            panel_layout = QHBoxLayout(self.panel_widget)
            panel_layout.setContentsMargins(5, 5, 5, 5)
            panel_layout.setSpacing(5)

            # Playback Controls
            self.btn_open_video = QPushButton("📂")
            self.btn_open_video.setToolTip("Open Video")
            self.btn_open_video.clicked.connect(self.open_video)
            self.btn_open_video.setStyleSheet("background: transparent; font-size: 16px; border: none;")
            
            self.btn_seek_m1 = QPushButton("-1s")
            self.btn_seek_m1.clicked.connect(lambda: self.seek_relative(-1.0))
            self.btn_seek_m1.setStyleSheet("background: transparent; color: #a6adc8; border: none;")
            
            self.btn_seek_m01 = QPushButton("-.1s")
            self.btn_seek_m01.clicked.connect(lambda: self.seek_relative(-0.1))
            self.btn_seek_m01.setStyleSheet("background: transparent; color: #a6adc8; border: none;")
            
            self.btn_play_pause = QPushButton("▶")
            self.btn_play_pause.setToolTip("Play / Pause")
            self.btn_play_pause.clicked.connect(self.toggle_play)
            self.btn_play_pause.setStyleSheet("background: transparent; color: #a6e3a1; font-weight: bold; font-size: 18px; border: none;")
            
            self.btn_seek_p01 = QPushButton("+.1s")
            self.btn_seek_p01.clicked.connect(lambda: self.seek_relative(0.1))
            self.btn_seek_p01.setStyleSheet("background: transparent; color: #a6adc8; border: none;")
            
            self.btn_seek_p1 = QPushButton("+1s")
            self.btn_seek_p1.clicked.connect(lambda: self.seek_relative(1.0))
            self.btn_seek_p1.setStyleSheet("background: transparent; color: #a6adc8; border: none;")
            
            self.cbo_speed = QComboBox()
            self.cbo_speed.addItems(["0.5x", "0.75x", "1.0x", "1.25x", "1.5x"])
            self.cbo_speed.setCurrentText("1.0x")
            self.cbo_speed.currentTextChanged.connect(self.change_speed)
            self.cbo_speed.setStyleSheet("background: transparent; color: #a6adc8; border: none;")
            
            panel_layout.addWidget(self.btn_open_video)
            panel_layout.addWidget(self.btn_seek_m1)
            panel_layout.addWidget(self.btn_seek_m01)
            panel_layout.addWidget(self.btn_play_pause)
            panel_layout.addWidget(self.btn_seek_p01)
            panel_layout.addWidget(self.btn_seek_p1)
            panel_layout.addWidget(self.cbo_speed)
            
            # Waveform
            from tvox_waveform import WaveformWidget, AudioExtractorWorker
            from ffmpeg_utils import ensure_ffmpeg
            
            self.lbl_time_curr = QLabel("00:00.000")
            self.lbl_time_curr.setStyleSheet("color: #a6adc8; font-family: monospace; font-size: 11px;")
            
            self.waveform = WaveformWidget()
            self.waveform.seek_requested.connect(self.on_waveform_seek)
            self.waveform.installEventFilter(self)
            
            self.lbl_time_total = QLabel("00:00.000")
            self.lbl_time_total.setStyleSheet("color: #a6adc8; font-family: monospace; font-size: 11px;")
            
            panel_layout.addWidget(self.lbl_time_curr)
            panel_layout.addWidget(self.waveform, stretch=1)
            panel_layout.addWidget(self.lbl_time_total)
            
            # Loop Controls
            self.btn_mark_a = QPushButton("[A]")
            self.btn_mark_a.clicked.connect(self.set_mark_a)
            self.btn_mark_a.setStyleSheet("background: transparent; border: 1px solid #cba6f7; color: #cba6f7; font-weight: bold; padding: 2px 6px; border-radius: 4px;")
            
            self.btn_mark_b = QPushButton("[B]")
            self.btn_mark_b.clicked.connect(self.set_mark_b)
            self.btn_mark_b.setStyleSheet("background: transparent; border: 1px solid #f38ba8; color: #f38ba8; font-weight: bold; padding: 2px 6px; border-radius: 4px;")
            
            self.btn_loop = QPushButton("🔁")
            self.btn_loop.clicked.connect(self.toggle_loop)
            self.btn_loop.setStyleSheet("background: #45475a; color: #cdd6f4; font-weight: bold; padding: 4px; border-radius: 4px;")
            
            panel_layout.addWidget(self.btn_mark_a)
            panel_layout.addWidget(self.btn_mark_b)
            panel_layout.addWidget(self.btn_loop)

            self.video_layout.addWidget(self.panel_widget)
            
            self.video_dock.setWidget(self.video_container)

            # 5. Add Dock Widget to Top
            self.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea, self.video_dock)
            
            # Ensure it has a reasonable starting size
            self.video_container.setMinimumHeight(300)
            # Try to force the dock to take half the height initially (window is 900 tall)
            self.resizeDocks([self.video_dock], [450], Qt.Orientation.Vertical)

            # 6. Initialize MPV and Timer
            self.player = None
            self.init_mpv()
            
            self.update_timer = QTimer(self)
            self.update_timer.setInterval(30) # ~33fps updates
            self.update_timer.timeout.connect(self.update_ui_from_mpv)
            self.update_timer.start()

            # 7. Hook into TStudio's table row selection
            self.table.selectionModel().currentChanged.connect(self.on_tvox_row_selected)
            
            # Set initial title with profile
            active = getattr(self, '_profiles_data', {}).get("active_preset", "Default")
            self.setWindowTitle(f"TVox - FMV Modding Studio [{active}]")
            
            # Override TStudio's large minimum size to allow DockWidget to expand
            self.setMinimumSize(1000, 600)
            
            # Focus video widget by default so Spacebar works immediately
            self.video_widget.setFocus()
            
            # 8. Check Requirements on Startup
            QTimer.singleShot(500, self.check_requirements)

        def check_requirements(self):
            if not MPV_AVAILABLE:
                msg = f"MPV Engine ไม่พร้อมใช้งาน!\n\nโปรดดาวน์โหลดไฟล์ libmpv-2.dll และนำมาวางไว้ที่:\n{os.path.dirname(__file__)}\n\nรายละเอียด Error:\n{MPV_ERROR}"
                QMessageBox.critical(self, "MPV Engine Missing", msg)

        def on_profile_changed(self, text):
            super().on_profile_changed(text)
            self.setWindowTitle(f"TVox - FMV Modding Studio [{text}]")

        def init_mpv(self):
            if not MPV_AVAILABLE:
                return

            try:
                # osc=False because we built our own UI now!
                self.player = mpv.MPV(wid=int(self.video_widget.winId()), osc=False, input_default_bindings=True, input_vo_keyboard=True, keep_open=True)
            except Exception as e:
                QMessageBox.critical(self, "MPV Error", f"Failed to initialize MPV player: {e}")

        # --- MPV UI UPDATE LOGIC ---
        def resizeEvent(self, event):
            super().resizeEvent(event)
            if hasattr(self, 'lbl_subtitle'):
                # Position subtitle at bottom center of video_container
                w = self.video_container.width()
                h = self.video_container.height()
                lbl_w = w - 40 # 20px padding on each side
                lbl_h = 100 # ample height for 2-3 lines
                self.lbl_subtitle.setGeometry(20, h - lbl_h - 20, lbl_w, lbl_h)

        def eventFilter(self, obj, event):
            if event.type() == event.Type.KeyPress:
                is_target = (obj == self.video_widget) or (hasattr(self, 'waveform') and obj == self.waveform)
                if is_target and event.key() == Qt.Key.Key_Space:
                    self.toggle_play()
                    return True
            return super().eventFilter(obj, event)

        def format_time(self, seconds):
            if seconds is None: return "00:00.000"
            m = int(seconds // 60)
            s = int(seconds % 60)
            ms = int((seconds % 1) * 1000)
            return f"{m:02d}:{s:02d}.{ms:03d}"

        def update_ui_from_mpv(self):
            if not self.player or not hasattr(self.player, 'time_pos') or self.player.time_pos is None:
                return

            pos = self.player.time_pos
            dur = self.player.duration or 1.0

            # Update Labels
            self.lbl_time_curr.setText(self.format_time(pos))
            self.lbl_time_total.setText(self.format_time(dur))

            # Update Waveform
            if not getattr(self.waveform, 'is_dragging', False):
                self.waveform.update_position(pos, dur)

            # Subtitle Sync
            if hasattr(self, 'lbl_subtitle') and hasattr(self, 'subtitle_timing'):
                active_text = ""
                active_row_id = None
                for timing in self.subtitle_timing:
                    if timing["start"] <= pos <= timing["end"]:
                        active_row_id = timing["row_id"]
                        break
                
                if active_row_id is not None and hasattr(self, 'model'):
                    # Find the text in the table model by matching row_id to col 0
                    # For performance, could cache row index, but this is fast enough for small sets
                    for row in self.model._data:
                        if str(row[0]) == active_row_id:
                            # Use Translation (col 3) if available, else Source (col 2)
                            active_text = row[3] if len(row) > 3 and str(row[3]).strip() else row[2]
                            break
                
                if active_text:
                    if self.lbl_subtitle.text() != active_text:
                        self.lbl_subtitle.setText(active_text)
                    if self.lbl_subtitle.isHidden():
                        self.lbl_subtitle.show()
                        self.lbl_subtitle.raise_()
                else:
                    if not self.lbl_subtitle.isHidden():
                        self.lbl_subtitle.hide()

            # Handle A-B Looping
            if self.loop_active and self.mark_a is not None and self.mark_b is not None:
                if self.mark_a < self.mark_b:
                    if pos >= self.mark_b:
                        if not getattr(self, 'is_loop_seeking', False):
                            try:
                                self.is_loop_seeking = True
                                self.player.time_pos = self.mark_a
                            except Exception:
                                pass
                    elif pos < self.mark_b - 0.2:
                        self.is_loop_seeking = False

        # --- UI ACTIONS ---
        def on_waveform_seek(self, target_sec):
            if self.player:
                self.lbl_time_curr.setText(self.format_time(target_sec))
                try:
                    self.player.time_pos = target_sec
                except Exception as e:
                    print(f"Seek error: {e}")

        def _load_csv(self):
            # Let TStudio logic load the self.csv_path into self.model._data
            super()._load_csv()
            
            # Parse subtitle timings
            self.subtitle_timing = []
            if hasattr(self, 'csv_path') and self.csv_path:
                try:
                    import json, os
                    base_dir = os.path.dirname(self.csv_path)
                    json_path = os.path.join(base_dir, f"{os.path.basename(self.csv_path).replace('.csv', '')}_meta.json")
                    if os.path.exists(json_path):
                        with open(json_path, 'r', encoding='utf-8') as f:
                            meta = json.load(f)
                            for row_id, data in meta.get("original_data", {}).items():
                                ts_str = data.get("timestamp", "")
                                if "-->" in ts_str:
                                    parts = ts_str.split("-->")
                                    if len(parts) == 2:
                                        start_str = parts[0].strip().replace(',', '.')
                                        end_str = parts[1].strip().replace(',', '.')
                                        
                                        def parse_time(t_str):
                                            t_parts = t_str.split(':')
                                            if len(t_parts) == 3:
                                                h, m, s = t_parts
                                                return int(h)*3600 + int(m)*60 + float(s)
                                            return 0.0
                                            
                                        start_sec = parse_time(start_str)
                                        end_sec = parse_time(end_str)
                                        self.subtitle_timing.append({
                                            "row_id": str(row_id),
                                            "start": start_sec,
                                            "end": end_sec
                                        })
                except Exception as e:
                    print(f"Failed to load subtitle timing metadata: {e}")

        def open_video(self):
            if not self.player: return
            file_path, _ = QFileDialog.getOpenFileName(self, "Open Video File", "", "Video Files (*.mp4 *.mkv *.avi *.webm *.mov *.bundle)")
            if file_path:
                try:
                    from tbundle_manager import TBundleManager
                    if TBundleManager.is_unity_bundle(file_path):
                        out_dir = os.path.join(os.path.dirname(file_path), "_tvox_cache")
                        extracted_video = TBundleManager.extract_video(file_path, out_dir)
                        if extracted_video:
                            file_path = extracted_video
                except Exception as e:
                    print(f"Bundle extract error: {e}")

                self.player.play(file_path)
                
                # Default to paused state
                self.player.pause = True
                self.btn_play_pause.setText("▶")
                
                # Refocus to video widget so spacebar works immediately
                self.video_widget.setFocus()
                
                self.mark_a = None
                self.mark_b = None
                self.btn_mark_a.setText("[A]")
                self.btn_mark_b.setText("[B]")
                
                # Check for FFmpeg and start extracting audio
                from ffmpeg_utils import ensure_ffmpeg
                from tvox_waveform import AudioExtractorWorker
                ffmpeg_path = ensure_ffmpeg(self)
                if ffmpeg_path:
                    if hasattr(self, 'audio_worker') and self.audio_worker.isRunning():
                        self.audio_worker.is_cancelled = True
                        self.audio_worker.wait()
                    
                    self.audio_worker = AudioExtractorWorker(ffmpeg_path, file_path)
                    self.audio_worker.finished.connect(self.waveform.set_audio_data)
                    self.audio_worker.error.connect(lambda msg: print(f"Audio Extractor Error: {msg}"))
                    self.audio_worker.start()

        def toggle_play(self):
            if not self.player: return
            self.player.pause = not self.player.pause

        def seek_relative(self, seconds):
            if not self.player: return
            self.player.seek(seconds, reference="relative")

        def change_speed(self, text):
            if not self.player: return
            try:
                speed = float(text.replace("x", ""))
                self.player.speed = speed
            except ValueError:
                pass

        def set_mark_a(self):
            if not self.player or self.player.time_pos is None: return
            self.mark_a = self.player.time_pos
            self.btn_mark_a.setText(f"A: {self.format_time(self.mark_a)}")

        def set_mark_b(self):
            if not self.player or self.player.time_pos is None: return
            self.mark_b = self.player.time_pos
            self.btn_mark_b.setText(f"B: {self.format_time(self.mark_b)}")

        def toggle_loop(self):
            self.loop_active = not self.loop_active
            if self.loop_active:
                self.btn_loop.setText("🔁")
                self.btn_loop.setStyleSheet("background: #a6e3a1; color: #1e1e2e; font-weight: bold; padding: 4px; border-radius: 4px;")
                # If we turn on loop but missed a mark, maybe auto set it?
                if self.mark_a is not None and self.mark_b is None:
                    if self.player.duration:
                        self.mark_b = self.player.duration
            else:
                self.btn_loop.setText("🔁")
                self.btn_loop.setStyleSheet("background: #45475a; color: #cdd6f4; font-weight: bold; padding: 4px; border-radius: 4px;")

        def on_tvox_row_selected(self, current, previous):
            # This is called *after* TStudio's own on_row_selected
            if not current.isValid(): return
            source_idx = self.proxy.mapToSource(current)
            row = source_idx.row()
            item = self.model._data[row]
            # Future feature: jump to start time of dialogue
            pass

else:
    from PyQt6.QtWidgets import QMainWindow
    class TVoxApp(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("TVox - Error")
            QMessageBox.critical(self, "Error", "TStudio engine not found!")

def main():
    app = QApplication(sys.argv)
    window = TVoxApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()