from tvox_i18n import _
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
    QSlider, QLabel, QComboBox, QGroupBox, QTableView,
    QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, QEvent

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
            self.setWindowTitle(_("window_title"))
            self.setGeometry(100, 100, 1400, 900)

            # --- Internal State ---
            self.is_user_seeking = False
            self.mark_a = None
            self.mark_b = None
            self.loop_active = False

            # 3. Create DockWidget for Video
            from PyQt6.QtWidgets import QDockWidget, QMainWindow
            self.video_dock = QDockWidget(_("dock_video_player"), self)
            self.video_dock.setObjectName("video_dock")
            self.video_dock.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
            self.video_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetFloatable | QDockWidget.DockWidgetFeature.DockWidgetMovable)
            self.setDockOptions(QMainWindow.DockOption.AllowNestedDocks | QMainWindow.DockOption.AllowTabbedDocks | getattr(QMainWindow.DockOption, 'AnimatedDocks', 0))
            
            # 4. Build Video Player
            self.video_container = QWidget()
            self.video_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            self.video_container.setStyleSheet("background-color: black;")
            self.video_layout = QVBoxLayout(self.video_container)
            self.video_layout.setContentsMargins(0,0,0,0)
            self.video_layout.setSpacing(0)
            
            self.video_widget = QWidget()
            self.video_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            self.video_widget.setAttribute(Qt.WidgetAttribute.WA_DontCreateNativeAncestors)
            self.video_widget.setAttribute(Qt.WidgetAttribute.WA_NativeWindow)
            self.video_widget.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
            self.video_widget.installEventFilter(self)
            self.video_layout.addWidget(self.video_widget, stretch=1)
            
            # --- Subtitle Space (Below Video) ---
            self.lbl_subtitle = QLabel()
            self.lbl_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.lbl_subtitle.setWordWrap(True)
            self.lbl_subtitle.setMinimumHeight(60) # Ensure it has space
            self.lbl_subtitle.setStyleSheet("""
                QLabel {
                    color: white;
                    font-size: 32px;
                    font-weight: bold;
                    background-color: transparent;
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
            self.video_layout.addWidget(self.lbl_subtitle, stretch=0)

            # --- Timeline & Controls Panel (Compact Mode) ---
            self.panel_widget = QWidget()
            self.panel_widget.setStyleSheet("background-color: #1e1e2e;")
            panel_layout = QHBoxLayout(self.panel_widget)
            panel_layout.setContentsMargins(5, 5, 5, 5)
            panel_layout.setSpacing(5)

            # Playback Controls
            self.btn_open_video = QPushButton("\U0001f4c2")
            self.btn_open_video.setToolTip(_("tooltip_open_video"))
            self.btn_open_video.clicked.connect(self.open_video)
            self.btn_open_video.setStyleSheet("background: transparent; font-size: 16px; border: none;")
            
            self.btn_seek_prev_sub = QPushButton("\u23ea")
            self.btn_seek_prev_sub.setToolTip(_("tooltip_prev_subtitle"))
            self.btn_seek_prev_sub.clicked.connect(self.seek_prev_sub)
            self.btn_seek_prev_sub.setStyleSheet("background: transparent; color: #a6adc8; font-size: 14px; border: none;")
            
            self.btn_seek_m1 = QPushButton("-1s")
            self.btn_seek_m1.setToolTip(_("tooltip_seek_m1"))
            self.btn_seek_m1.clicked.connect(lambda: self.seek_relative(-1.0))
            self.btn_seek_m1.setStyleSheet("background: transparent; color: #a6adc8; border: none;")
            
            self.btn_seek_m01 = QPushButton("-.1s")
            self.btn_seek_m01.setToolTip(_("tooltip_seek_m01"))
            self.btn_seek_m01.clicked.connect(lambda: self.seek_relative(-0.1))
            self.btn_seek_m01.setStyleSheet("background: transparent; color: #a6adc8; border: none;")
            
            self.btn_play_pause = QPushButton("\u25b6")
            self.btn_play_pause.setToolTip(_("tooltip_play_pause"))
            self.btn_play_pause.clicked.connect(self.toggle_play)
            self.btn_play_pause.setStyleSheet("background: transparent; color: #a6e3a1; font-weight: bold; font-size: 18px; border: none;")
            
            self.btn_seek_p01 = QPushButton("+.1s")
            self.btn_seek_p01.setToolTip(_("tooltip_seek_p01"))
            self.btn_seek_p01.clicked.connect(lambda: self.seek_relative(0.1))
            self.btn_seek_p01.setStyleSheet("background: transparent; color: #a6adc8; border: none;")
            
            self.btn_seek_p1 = QPushButton("+1s")
            self.btn_seek_p1.setToolTip(_("tooltip_seek_p1"))
            self.btn_seek_p1.clicked.connect(lambda: self.seek_relative(1.0))
            self.btn_seek_p1.setStyleSheet("background: transparent; color: #a6adc8; border: none;")
            
            self.btn_seek_next_sub = QPushButton("\u23e9")
            self.btn_seek_next_sub.setToolTip(_("tooltip_next_subtitle"))
            self.btn_seek_next_sub.clicked.connect(self.seek_next_sub)
            self.btn_seek_next_sub.setStyleSheet("background: transparent; color: #a6adc8; font-size: 14px; border: none;")
            
            self.cbo_speed = QComboBox()
            self.cbo_speed.addItems(["0.5x", "0.75x", "1.0x", "1.25x", "1.5x"])
            self.cbo_speed.setCurrentText("1.0x")
            self.cbo_speed.currentTextChanged.connect(self.change_speed)
            self.cbo_speed.setStyleSheet("background: transparent; color: #a6adc8; border: none;")
            
            panel_layout.addWidget(self.btn_open_video)
            panel_layout.addWidget(self.btn_seek_prev_sub)
            panel_layout.addWidget(self.btn_seek_m1)
            panel_layout.addWidget(self.btn_seek_m01)
            panel_layout.addWidget(self.btn_play_pause)
            panel_layout.addWidget(self.btn_seek_p01)
            panel_layout.addWidget(self.btn_seek_p1)
            panel_layout.addWidget(self.btn_seek_next_sub)
            panel_layout.addWidget(self.cbo_speed)
            
            # Waveform
            from tvox_waveform import WaveformWidget, AudioExtractorWorker
            from ffmpeg_utils import ensure_ffmpeg
            
            self.lbl_time_curr = QLabel(_("time_default"))
            self.lbl_time_curr.setStyleSheet("color: #a6adc8; font-family: monospace; font-size: 11px;")
            
            self.waveform = WaveformWidget()
            self.waveform.seek_requested.connect(self.on_waveform_seek)
            self.waveform.installEventFilter(self)
            
            self.lbl_time_total = QLabel(_("time_default"))
            self.lbl_time_total.setStyleSheet("color: #a6adc8; font-family: monospace; font-size: 11px;")
            
            panel_layout.addWidget(self.lbl_time_curr)
            panel_layout.addWidget(self.waveform, stretch=1)
            panel_layout.addWidget(self.lbl_time_total)
            
            # Loop Controls
            self.btn_mark_a = QPushButton(_("btn_mark_a"))
            self.btn_mark_a.setToolTip(_("tooltip_mark_a"))
            self.btn_mark_a.clicked.connect(self.set_mark_a)
            self.btn_mark_a.setStyleSheet("background: transparent; border: 1px solid #cba6f7; color: #cba6f7; font-weight: bold; padding: 2px 6px; border-radius: 4px;")
            
            self.btn_mark_b = QPushButton(_("btn_mark_b"))
            self.btn_mark_b.setToolTip(_("tooltip_mark_b"))
            self.btn_mark_b.clicked.connect(self.set_mark_b)
            self.btn_mark_b.setStyleSheet("background: transparent; border: 1px solid #f38ba8; color: #f38ba8; font-weight: bold; padding: 2px 6px; border-radius: 4px;")
            
            self.btn_loop = QPushButton("\U0001f501")
            self.btn_loop.setToolTip(_("tooltip_loop"))
            self.btn_loop.clicked.connect(self.toggle_loop)
            self.btn_loop.setStyleSheet("background: #45475a; color: #cdd6f4; font-weight: bold; padding: 4px; border-radius: 4px;")
            
            self.btn_auto_scroll = QPushButton(_("btn_auto_scroll"))
            self.btn_auto_scroll.setToolTip(_("tooltip_auto_scroll"))
            self.btn_auto_scroll.setCheckable(True)
            self.btn_auto_scroll.clicked.connect(self.toggle_auto_scroll)
            self.btn_auto_scroll.setStyleSheet("background: #45475a; color: #cdd6f4; padding: 4px; border-radius: 4px;")
            
            panel_layout.addWidget(self.btn_mark_a)
            panel_layout.addWidget(self.btn_mark_b)
            panel_layout.addWidget(self.btn_loop)
            panel_layout.addWidget(self.btn_auto_scroll)

            self.video_layout.addWidget(self.panel_widget)
            
            self.video_dock.setWidget(self.video_container)

            # 5. Add Dock Widget to Top
            self.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea, self.video_dock)
            
            # Ensure it has a reasonable starting size
            self.video_container.setMinimumHeight(100)
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
            self.table.installEventFilter(self)
            
            # Set initial title with profile
            active = getattr(self, '_profiles_data', {}).get("active_preset", "Default")
            self.setWindowTitle(_("window_title_profile"))
            
            # Override TStudio's large minimum size to allow DockWidget to expand
            self.setMinimumSize(600, 400)
            
            # Focus video widget by default so Spacebar works immediately
            self.video_widget.setFocus()
            
            # 8. Check Requirements on Startup
            QTimer.singleShot(500, self.check_requirements)

        def check_requirements(self):
            if not MPV_AVAILABLE:
                msg = f"MPV Engine ไม่พร้อมใช้งาน!\n\nโปรดดาวน์โหลดไฟล์ libmpv-2.dll และนำมาวางไว้ที่:\n{os.path.dirname(__file__)}\n\nรายละเอียด Error:\n{MPV_ERROR}"
                QMessageBox.critical(self, _("dlg_mpv_missing_title"), msg)

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
                QMessageBox.critical(self, _("dlg_mpv_init_error_title"), _("dlg_mpv_init_error_msg"))

        # --- MPV UI UPDATE LOGIC ---
        def eventFilter(self, obj, event):
            if event.type() == QEvent.Type.KeyPress:
                if event.key() == Qt.Key.Key_Space:
                    if hasattr(self, 'table') and obj == self.table:
                        if self.table.state() != QTableView.State.EditingState:
                            self.toggle_play()
                            return True
                    elif obj == self.video_widget or (hasattr(self, 'waveform') and obj == self.waveform):
                        self.toggle_play()
                        return True
            return super().eventFilter(obj, event)

        def format_time(self, seconds):
            if seconds is None: return _("time_default")
            m = int(seconds // 60)
            s = int(seconds % 60)
            ms = int((seconds % 1) * 1000)
            return f"{m:02d}:{s:02d}.{ms:03d}"

        def seek_prev_sub(self):
            if not self.player or not hasattr(self, 'subtitle_timing'): return
            try:
                pos = self.player.time_pos
                if pos is None: return
                target = 0.0
                for timing in reversed(self.subtitle_timing):
                    # We subtract 0.1 to avoid getting stuck on the same sub if we are exactly at its start
                    if timing["start"] < pos - 0.1:
                        target = timing["start"]
                        break
                self.player.time_pos = target
            except Exception:
                pass

        def seek_next_sub(self):
            if not self.player or not hasattr(self, 'subtitle_timing'): return
            try:
                pos = self.player.time_pos
                if pos is None: return
                target = None
                for timing in self.subtitle_timing:
                    # We add 0.1 to avoid getting stuck on the same sub
                    if timing["start"] > pos + 0.1:
                        target = timing["start"]
                        break
                if target is not None:
                    self.player.time_pos = target
            except Exception:
                pass

        def update_ui_from_mpv(self):
            if not self.player: return
            try:
                pos = getattr(self.player, 'time_pos', None)
                if pos is None: return
                dur = getattr(self.player, 'duration', 1.0) or 1.0
            except Exception:
                return

            # Update Labels
            self.lbl_time_curr.setText(self.format_time(pos))
            self.lbl_time_total.setText(self.format_time(dur))

            # Update Waveform
            if not getattr(self.waveform, 'is_dragging', False):
                self.waveform.update_position(pos, dur)

            # Subtitle Sync
            if hasattr(self, 'lbl_subtitle') and hasattr(self, 'subtitle_timing'):
                active_text = ""
                active_row_ids = []
                for timing in self.subtitle_timing:
                    if timing["start"] <= pos <= timing["end"]:
                        if timing["row_id"] not in active_row_ids:
                            active_row_ids.append(timing["row_id"])
                
                if active_row_ids and hasattr(self, 'model'):
                    active_texts = []
                    last_row_idx = -1
                    for idx, item in enumerate(self.model._data):
                        row_id = str(item.get("id", ""))
                        if row_id in active_row_ids:
                            trans = str(item.get("trans", "")).strip()
                            src = str(item.get("source", ""))
                            text = trans if trans else src
                            active_texts.append((active_row_ids.index(row_id), text, idx))
                            
                    # Sort by the order they appear in subtitle_timing
                    active_texts.sort(key=lambda x: x[0])
                    
                    final_texts = [x[1] for x in active_texts]
                    active_text = "\n".join(final_texts)
                    
                    if active_texts:
                        last_row_idx = active_texts[-1][2]
                            
                    # Auto-Scroll
                    if self.btn_auto_scroll.isChecked() and last_row_idx != -1:
                        source_index = self.model.index(last_row_idx, 0)
                        proxy_index = self.proxy.mapFromSource(source_index)
                        if proxy_index.isValid():
                            current_row = self.table.selectionModel().currentIndex().row()
                            if proxy_index.row() != current_row:
                                self.is_auto_selecting = True
                                self.table.selectRow(proxy_index.row())
                                self.table.scrollTo(proxy_index)
                                self.is_auto_selecting = False
                
                if self.lbl_subtitle.text() != active_text:
                    self.lbl_subtitle.setText(active_text)

            # Handle A-B Looping
            if self.loop_active and self.mark_a is not None and self.mark_b is not None:
                if self.mark_a < self.mark_b:
                    if pos >= self.mark_b:
                        if not getattr(self, 'is_loop_seeking', False):
                            try:
                                self.is_loop_seeking = True
                                self.player.seek(self.mark_a, reference="absolute")
                            except Exception:
                                pass
                    elif pos < self.mark_b - 0.2:
                        self.is_loop_seeking = False

        # --- UI ACTIONS ---
        def on_waveform_seek(self, target_time):
            if self.player:
                try:
                    pos = getattr(self.player, 'time_pos', None)
                    if pos is not None:
                        self.player.seek(target_time, reference="absolute")
                except Exception:
                    pass

        def _load_csv(self):
            # Let TStudio logic load the self.csv_path into self.model._data
            super()._load_csv()
            
            # Parse subtitle timings
            self.subtitle_timing = []
            
            def parse_time(t_str):
                t_parts = t_str.split(':')
                if len(t_parts) == 3:
                    h, m, s = t_parts
                    return int(h)*3600 + int(m)*60 + float(s)
                return 0.0

            if hasattr(self, 'model') and self.model._data:
                for item in self.model._data:
                    row_id = item["id"]
                    ts_str = row_id.split('|', 1)[-1] if '|' in row_id else row_id
                    
                    if "-->" in ts_str:
                        parts = ts_str.split("-->")
                        if len(parts) == 2:
                            start_str = parts[0].strip().replace(',', '.')
                            end_str = parts[1].strip().replace(',', '.')
                            
                            start_sec = parse_time(start_str)
                            end_sec = parse_time(end_str)
                            self.subtitle_timing.append({
                                "row_id": str(row_id),
                                "start": start_sec,
                                "end": end_sec
                            })

        def open_video(self):
            if not self.player: return
            file_path, _ = QFileDialog.getOpenFileName(self, _("fdlg_open_video_title"), "", _("fdlg_open_video_filter"))
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
                self.btn_play_pause.setText("\u25b6")
                
                # Refocus to video widget so spacebar works immediately
                self.video_widget.setFocus()
                
                self.mark_a = None
                self.mark_b = None
                self.btn_mark_a.setText(_("btn_mark_a"))
                self.btn_mark_b.setText(_("btn_mark_b"))
                
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
            try:
                self.player.pause = not self.player.pause
                self.btn_play_pause.setText("\u23f8" if not self.player.pause else "\u25b6")
            except Exception:
                pass

        def seek_relative(self, seconds):
            if not self.player: return
            try:
                self.player.seek(seconds, reference="relative")
            except Exception:
                pass

        def change_speed(self, text):
            if not self.player: return
            try:
                speed = float(text.replace("x", ""))
                self.player.speed = speed
            except Exception:
                pass

        def set_mark_a(self):
            if not self.player: return
            try:
                pos = getattr(self.player, 'time_pos', None)
                if pos is None: return
                self.mark_a = pos
                self.btn_mark_a.setText(f"A: {self.format_time(self.mark_a)}")
            except Exception:
                pass

        def set_mark_b(self):
            if not self.player: return
            try:
                pos = getattr(self.player, 'time_pos', None)
                if pos is None: return
                self.mark_b = pos
                self.btn_mark_b.setText(f"B: {self.format_time(self.mark_b)}")
            except Exception:
                pass


        def set_layout_mode(self, mode):
            from PyQt6.QtCore import Qt
            from PyQt6.QtWidgets import QSizePolicy
            
            # Prevent Qt crashes when re-arranging tabbed widgets
            if hasattr(self, 'workspace_dock'):
                self.workspace_dock.setFloating(True)
                self.workspace_dock.widget().setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            if hasattr(self, 'glossary_dock'):
                self.glossary_dock.setFloating(True)
                self.glossary_dock.widget().setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            if hasattr(self, 'video_dock'):
                self.video_dock.setFloating(True)
                self.video_dock.widget().setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            
            self.glossary_dock.setFloating(False)
            self.workspace_dock.setFloating(False)
            if hasattr(self, 'video_dock'):
                self.video_dock.setFloating(False)
            
            if mode == 'floating':
                self.glossary_dock.setFloating(True)
                if hasattr(self, 'video_dock'):
                    self.video_dock.setFloating(True)
            elif mode == 'subtitle' or mode == 'standard':
                # Video Top Left, Glossary Top Right, Workspace Bottom Wide
                if hasattr(self, 'video_dock'):
                    self.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea, self.video_dock)
                self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.glossary_dock)
                self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.workspace_dock)
            elif mode == 'video':
                # Video huge left, Workspace right, Glossary tabbed with Workspace
                if hasattr(self, 'video_dock'):
                    self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.video_dock)
                self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.workspace_dock)
                self.tabifyDockWidget(self.workspace_dock, self.glossary_dock)
            elif mode == 'review':
                # Video and Workspace tabbed together in center/top
                if hasattr(self, 'video_dock'):
                    self.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea, self.video_dock)
                    self.tabifyDockWidget(self.video_dock, self.workspace_dock)
                self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.glossary_dock)
            elif mode == 'compact':
                # Everything tabbed
                if hasattr(self, 'video_dock'):
                    self.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea, self.video_dock)
                    self.tabifyDockWidget(self.video_dock, self.workspace_dock)
                self.tabifyDockWidget(self.workspace_dock, self.glossary_dock)

        def toggle_loop(self):
            self.loop_active = not self.loop_active
            if self.loop_active:
                self.btn_loop.setText("\U0001f501")
                self.btn_loop.setStyleSheet("background: #a6e3a1; color: #1e1e2e; font-weight: bold; padding: 4px; border-radius: 4px;")
                # If we turn on loop but missed a mark, maybe auto set it?
                if self.mark_a is not None and self.mark_b is None:
                    if self.player:
                        try:
                            dur = getattr(self.player, 'duration', None)
                            if dur:
                                self.mark_b = dur
                        except Exception:
                            pass
            else:
                self.btn_loop.setText("\U0001f501")
                self.btn_loop.setStyleSheet("background: #45475a; color: #cdd6f4; font-weight: bold; padding: 4px; border-radius: 4px;")

        def toggle_auto_scroll(self):
            if self.btn_auto_scroll.isChecked():
                self.btn_auto_scroll.setStyleSheet("background: #a6e3a1; color: #1e1e2e; padding: 4px; border-radius: 4px;")
            else:
                self.btn_auto_scroll.setStyleSheet("background: #45475a; color: #cdd6f4; padding: 4px; border-radius: 4px;")

        def on_tvox_row_selected(self, current, previous):
            # This is called *after* TStudio's own on_row_selected
            if not current.isValid(): return
            source_idx = self.proxy.mapToSource(current)
            row = source_idx.row()
            item = self.model._data[row]
            
            # Avoid seeking video if the selection was triggered by Auto-Scroll
            if getattr(self, 'is_auto_selecting', False):
                return
                
            # Jump to start time of dialogue (only if video is playing/loaded)
            if self.player and hasattr(self, 'subtitle_timing'):
                # Check if video is loaded safely
                try:
                    pos = getattr(self.player, 'time_pos', None)
                    if pos is None:
                        return
                except Exception:
                    return
                    
                row_id = str(item["id"])
                for timing in self.subtitle_timing:
                    if timing["row_id"] == row_id:
                        try:
                            self.player.seek(timing["start"], reference="absolute")
                            self.lbl_time_curr.setText(self.format_time(timing["start"]))
                        except Exception:
                            pass
                        break

        def deploy_to_game(self):
            # For TVox (Subtitles), Deploy to Game should just export the SRT/VTT
            self.export_origin_format()

else:
    from PyQt6.QtWidgets import QMainWindow
    class TVoxApp(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle(_("window_title_error"))
            QMessageBox.critical(self, _("dlg_tstudio_missing_title"), _("dlg_tstudio_missing_msg"))

def main():
    app = QApplication(sys.argv)
    window = TVoxApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()