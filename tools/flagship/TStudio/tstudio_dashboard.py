import os
import csv
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QTableWidget, QTableWidgetItem, QHeaderView, 
    QFileDialog, QProgressBar, QMessageBox, QAbstractItemView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from tstudio_core import TStudioCore

class ProjectDashboardDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Project Dashboard")
        self.resize(800, 500)
        self.setStyleSheet("""
            QDialog { background-color: #1e1e2e; color: #cdd6f4; }
            QLabel { color: #cdd6f4; font-size: 14px; font-weight: bold; }
            QPushButton { background-color: #89b4fa; color: #1e1e2e; font-weight: bold; padding: 6px 12px; border-radius: 4px; }
            QPushButton:hover { background-color: #b4befe; }
            QTableWidget { background-color: #181825; color: #cdd6f4; gridline-color: #313244; border: 1px solid #313244; }
            QHeaderView::section { background-color: #313244; color: #cdd6f4; font-weight: bold; padding: 4px; border: 1px solid #45475a; }
            QProgressBar { text-align: center; color: #1e1e2e; font-weight: bold; border: 1px solid #313244; border-radius: 4px; background-color: #313244; }
            QProgressBar::chunk { background-color: #a6e3a1; border-radius: 4px; }
        """)

        layout = QVBoxLayout(self)

        # Top Bar
        top_layout = QHBoxLayout()
        self.lbl_folder = QLabel("No folder selected.")
        self.lbl_folder.setStyleSheet("font-weight: normal; font-size: 12px; color: #a6adc8;")
        btn_select = QPushButton(_("btn_select_folder"))
        btn_select.setToolTip(_("tooltip_select"))
        btn_select.clicked.connect(self.select_folder)
        
        top_layout.addWidget(btn_select)
        top_layout.addWidget(self.lbl_folder, 1)
        layout.addLayout(top_layout)

        # Summary
        self.lbl_summary = QLabel("Total Progress: 0% (0 / 0 rows)")
        layout.addWidget(self.lbl_summary)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(20)
        layout.addWidget(self.progress_bar)

        # Table
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Filename", "Total Rows", "Translated", "Completion"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)

        # Bottom Bar
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        btn_close = QPushButton(_("btn_close"))
        btn_close.setToolTip(_("tooltip_close"))
        btn_close.setStyleSheet("background-color: #45475a; color: #cdd6f4;")
        btn_close.clicked.connect(self.close)
        bottom_layout.addWidget(btn_close)
        layout.addLayout(bottom_layout)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Project Folder containing CSV files")
        if folder:
            self.lbl_folder.setText(f"Folder: {folder}")
            self.scan_folder(folder)

    def scan_folder(self, folder):
        self.table.setRowCount(0)
        total_rows = 0
        total_translated = 0
        
        csv_files = [f for f in os.listdir(folder) if f.lower().endswith('.csv')]
        if not csv_files:
            QMessageBox.information(self, "Dashboard", "No CSV files found in the selected folder.")
            return
            
        import re
        thai_pattern = re.compile(r'[ก-๙เแไใโ]')
            
        for file in csv_files:
            filepath = os.path.join(folder, file)
            try:
                # Try UTF-8-sig first
                enc = 'utf-8-sig'
                with open(filepath, 'r', encoding=enc, errors='ignore') as f:
                    reader = csv.reader(f)
                    try:
                        headers = next(reader)
                        
                        col_trans = 2 # Assuming ID, Source, Trans, AI
                        for i, h in enumerate(headers):
                            if 'trans' in h.lower() or 'thai' in h.lower():
                                col_trans = i
                                break
                                
                        file_total = 0
                        file_trans = 0
                        for row in reader:
                            if len(row) > 1: # At least ID and Source
                                file_total += 1
                                if len(row) > col_trans and row[col_trans].strip() and thai_pattern.search(row[col_trans]):
                                    file_trans += 1
                                    
                        total_rows += file_total
                        total_translated += file_trans
                        
                        completion = (file_trans / file_total * 100) if file_total > 0 else 0
                        
                        r = self.table.rowCount()
                        self.table.insertRow(r)
                        self.table.setItem(r, 0, QTableWidgetItem(file))
                        
                        i_total = QTableWidgetItem(f"{file_total:,}")
                        i_total.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        self.table.setItem(r, 1, i_total)
                        
                        i_trans = QTableWidgetItem(f"{file_trans:,}")
                        i_trans.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        self.table.setItem(r, 2, i_trans)
                        
                        i_comp = QTableWidgetItem(f"{completion:.1f}%")
                        i_comp.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        if completion >= 100:
                            i_comp.setForeground(QColor('#a6e3a1')) # Green
                        elif completion == 0:
                            i_comp.setForeground(QColor('#f38ba8')) # Red
                        else:
                            i_comp.setForeground(QColor('#f9e2af')) # Yellow
                        self.table.setItem(r, 3, i_comp)
                        
                    except StopIteration:
                        pass
            except Exception as e:
                print(f"Error scanning {file}: {e}")
                
        # Update summary
        if total_rows > 0:
            total_completion = (total_translated / total_rows) * 100
        else:
            total_completion = 0
            
        self.lbl_summary.setText(f"Total Progress: {total_completion:.1f}% ({total_translated:,} / {total_rows:,} rows)")
        self.progress_bar.setValue(int(total_completion))
