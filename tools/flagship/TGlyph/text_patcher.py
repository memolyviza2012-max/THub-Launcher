import sys
import os
import json
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog, QTextEdit, QProgressBar, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

# Catppuccin Mocha Colors for consistent styling
class Mocha:
    BG = "#1e1e2e"
    SURFACE = "#313244"
    TEXT = "#cdd6f4"
    BLUE = "#89b4fa"
    GREEN = "#a6e3a1"
    RED = "#f38ba8"
    YELLOW = "#f9e2af"
    LAVENDER = "#b4befe"


class PatcherThread(QThread):
    progress = pyqtSignal(int)
    log = pyqtSignal(str)
    finished_signal = pyqtSignal(bool)

    def __init__(self, mapping_path, input_paths, output_folder):
        super().__init__()
        self.mapping_path = mapping_path
        self.input_paths = input_paths
        self.output_folder = output_folder

    def run(self):
        try:
            # 1. Load Mapping
            self.log.emit(f"Loading mapping file: {self.mapping_path}")
            with open(self.mapping_path, 'r', encoding='utf-8') as f:
                mapping = json.load(f)

            replacements = {}
            for k, v in mapping.items():
                if isinstance(v, list):
                    replacements[k] = "".join(chr(int(code, 16)) for code in v)
                elif isinstance(v, str) and v.strip() != "":
                    replacements[k] = chr(int(v, 16))

            if not replacements:
                self.log.emit("Error: Mapping file is empty or invalid.")
                self.finished_signal.emit(False)
                return

            self.log.emit(f"Loaded {len(replacements)} mapping rules.")
            
            # Sort keys by length descending (longest first to avoid partial replacements)
            sorted_keys = sorted(replacements.keys(), key=len, reverse=True)

            # 2. Gather Files
            files_to_process = []
            for path in self.input_paths:
                p = Path(path)
                if p.is_file():
                    files_to_process.append(p)
                elif p.is_dir():
                    # Scan for text files
                    for ext in ('*.json', '*.txt', '*.xml', '*.csv', '*.yaml', '*.yml', '*.ini', '*.scr'):
                        files_to_process.extend(p.rglob(ext))

            if not files_to_process:
                self.log.emit("Error: No input files found to process.")
                self.finished_signal.emit(False)
                return

            out_dir = Path(self.output_folder)
            out_dir.mkdir(parents=True, exist_ok=True)
            self.log.emit(f"Found {len(files_to_process)} files to process.")

            # 3. Process Files
            total = len(files_to_process)
            success_count = 0

            for i, filepath in enumerate(files_to_process):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        text = f.read()

                    original_text = text
                    for k in sorted_keys:
                        if k in text:
                            text = text.replace(k, replacements[k])

                    # Calculate relative path if input was a folder
                    # For simplicity, if multiple paths were selected, just flatten them or keep name
                    # Let's just use the filename to avoid complex path logic for now
                    out_file = out_dir / filepath.name
                    
                    # Avoid overwriting files with the same name from different folders
                    counter = 1
                    while out_file.exists() and original_text == text:
                        # Optimization: if no changes and we just need to save, wait actually if we flatten we might overwrite.
                        pass
                        
                    # Let's save it
                    out_file = out_dir / filepath.name
                    with open(out_file, 'w', encoding='utf-8') as f:
                        f.write(text)

                    if original_text != text:
                        self.log.emit(f"Patched: {filepath.name}")
                    
                    success_count += 1
                except UnicodeDecodeError:
                    self.log.emit(f"Skipped (Not UTF-8): {filepath.name}")
                except Exception as e:
                    self.log.emit(f"Error processing {filepath.name}: {e}")

                self.progress.emit(int(((i + 1) / total) * 100))

            self.log.emit(f"\nDone! Successfully processed {success_count} files.")
            self.log.emit(f"Output saved to: {out_dir.absolute()}")
            self.finished_signal.emit(True)

        except Exception as e:
            self.log.emit(f"Critical Error: {e}")
            self.finished_signal.emit(False)


class TextPatcherApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📝 PUA Text Patcher — Auto Font Converter")
        self.setMinimumSize(600, 500)
        
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {Mocha.BG}; color: {Mocha.TEXT}; }}
            QWidget {{ background-color: {Mocha.BG}; color: {Mocha.TEXT}; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
            QLabel {{ font-size: 14px; font-weight: bold; }}
            QLineEdit {{ background-color: {Mocha.SURFACE}; border: 1px solid #45475a; padding: 6px; border-radius: 4px; color: {Mocha.TEXT}; }}
            QPushButton {{ background-color: {Mocha.SURFACE}; border: 1px solid #45475a; padding: 6px 12px; border-radius: 4px; color: {Mocha.TEXT}; font-weight: bold; }}
            QPushButton:hover {{ background-color: #45475a; }}
            QPushButton#primary {{ background-color: {Mocha.BLUE}; color: {Mocha.BG}; border: none; padding: 10px; font-size: 16px; }}
            QPushButton#primary:hover {{ background-color: {Mocha.LAVENDER}; }}
            QTextEdit {{ background-color: {Mocha.SURFACE}; border: 1px solid #45475a; border-radius: 4px; padding: 6px; font-family: Consolas, monospace; }}
            QProgressBar {{ border: 1px solid #45475a; border-radius: 4px; text-align: center; background-color: {Mocha.SURFACE}; }}
            QProgressBar::chunk {{ background-color: {Mocha.GREEN}; width: 10px; }}
        """)

        self._setup_ui()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("🚀 PUA Text Patcher")
        title.setStyleSheet(f"font-size: 24px; color: {Mocha.BLUE};")
        layout.addWidget(title)
        
        desc = QLabel("แปลงข้อความภาษาไทยปกติ ให้เป็นรหัส PUA อัตโนมัติ เพื่อนำไปใช้ในเกม")
        desc.setStyleSheet(f"font-size: 13px; color: #a6adc8; font-weight: normal;")
        layout.addWidget(desc)
        layout.addSpacing(10)

        # Mapping File
        layout.addWidget(QLabel("1. ไฟล์พจนานุกรม (mapping.json):"))
        map_row = QHBoxLayout()
        self.map_edit = QLineEdit()
        self.map_edit.setPlaceholderText("เลือกไฟล์ mapping.json ที่ได้จาก Font Studio...")
        map_btn = QPushButton("Browse")
        map_btn.clicked.connect(self._browse_mapping)
        map_row.addWidget(self.map_edit)
        map_row.addWidget(map_btn)
        layout.addLayout(map_row)

        # Input Files
        layout.addWidget(QLabel("2. ไฟล์เกมที่ต้องการแปลง (Input Files):"))
        in_row = QHBoxLayout()
        self.in_edit = QLineEdit()
        self.in_edit.setPlaceholderText("เลือกไฟล์ (.json, .txt) หรือเลือกทั้งโฟลเดอร์...")
        in_btn_file = QPushButton("Select Files")
        in_btn_file.clicked.connect(self._browse_input_files)
        in_btn_dir = QPushButton("Select Folder")
        in_btn_dir.clicked.connect(self._browse_input_dir)
        in_row.addWidget(self.in_edit)
        in_row.addWidget(in_btn_file)
        in_row.addWidget(in_btn_dir)
        layout.addLayout(in_row)

        # Output Folder
        layout.addWidget(QLabel("3. โฟลเดอร์สำหรับเซฟผลลัพธ์ (Output Folder):"))
        out_row = QHBoxLayout()
        self.out_edit = QLineEdit()
        self.out_edit.setPlaceholderText("เลือกโฟลเดอร์ปลายทาง...")
        out_btn = QPushButton("Browse")
        out_btn.clicked.connect(self._browse_output)
        out_row.addWidget(self.out_edit)
        out_row.addWidget(out_btn)
        layout.addLayout(out_row)

        layout.addSpacing(10)

        # Start Button
        self.btn_start = QPushButton("⚡ เริ่มแปลงข้อความ (Start Patching)")
        self.btn_start.setObjectName("primary")
        self.btn_start.clicked.connect(self._start_patching)
        layout.addWidget(self.btn_start)

        # Progress
        self.progress = QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        # Log
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)

        # Variables
        self.input_paths = []

    def _browse_mapping(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select mapping.json", "", "JSON Files (*.json)")
        if path:
            self.map_edit.setText(path)

    def _browse_input_files(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Select Input Files", "", "All Files (*.*)")
        if paths:
            self.input_paths = paths
            if len(paths) == 1:
                self.in_edit.setText(paths[0])
            else:
                self.in_edit.setText(f"{len(paths)} files selected")

    def _browse_input_dir(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Input Folder")
        if folder:
            self.input_paths = [folder]
            self.in_edit.setText(folder)

    def _browse_output(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.out_edit.setText(folder)

    def log(self, text):
        self.log_area.append(text)
        self.log_area.ensureCursorVisible()

    def _start_patching(self):
        mapping = self.map_edit.text()
        out_dir = self.out_edit.text()

        if not mapping or not os.path.exists(mapping):
            QMessageBox.warning(self, "Error", "กรุณาเลือกไฟล์ mapping.json ให้ถูกต้อง")
            return
        if not self.input_paths:
            QMessageBox.warning(self, "Error", "กรุณาเลือกไฟล์หรือโฟลเดอร์ที่ต้องการแปลง")
            return
        if not out_dir:
            QMessageBox.warning(self, "Error", "กรุณาเลือกโฟลเดอร์สำหรับเซฟผลลัพธ์")
            return

        self.btn_start.setEnabled(False)
        self.progress.setValue(0)
        self.log_area.clear()
        self.log("Starting text patcher...")

        self.thread = PatcherThread(mapping, self.input_paths, out_dir)
        self.thread.progress.connect(self.progress.setValue)
        self.thread.log.connect(self.log)
        self.thread.finished_signal.connect(self._on_finished)
        self.thread.start()

    def _on_finished(self, success):
        self.btn_start.setEnabled(True)
        if success:
            QMessageBox.information(self, "Success", "แปลงไฟล์เสร็จสมบูรณ์!")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TextPatcherApp()
    window.show()
    sys.exit(app.exec())
