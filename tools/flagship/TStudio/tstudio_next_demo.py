# -*- coding: utf-8 -*-
"""
tstudio_next_demo.py
Launcher for the Masterpiece Edition of Translation Studio.
Connects to the full flagship engine from tstudio_app.py with all menus, AI workers, and tools.
"""

import sys
import os

# Set search paths
curr_dir = os.path.dirname(os.path.abspath(__file__))
flagship_dir = os.path.abspath(os.path.join(curr_dir, '..'))
sys.path.insert(0, os.path.join(flagship_dir, 'Core'))
sys.path.insert(0, os.path.join(flagship_dir, 'TStudio'))
sys.path.insert(0, os.path.join(flagship_dir, 'TRun'))

from PyQt6.QtWidgets import QApplication
from tstudio_app import TranslationStudio, TStudioCore

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('project', nargs='?', type=str, help='Path to THub project or CSV', default=None)
    parser.add_argument('--mode', '-m', type=str, default='studio', choices=['studio', 'trun'], help='Workspace mode')
    args, unknown = parser.parse_known_args()

    app = QApplication.instance() or QApplication(sys.argv)
    from PyQt6.QtGui import QFont
    f = app.font()
    f.setFamily('Segoe UI')
    app.setFont(f)
    app.setStyle('Fusion')

    if args.project:
        TStudioCore.set_project_path(args.project)

    win = TranslationStudio(project_path=args.project, default_mode=args.mode)
    
    # If no CSV loaded, check if translation.csv exists
    if win.model.rowCount() == 0:
        sample_path = os.path.join(curr_dir, 'translation.csv')
        if os.path.exists(sample_path):
            win.csv_path = sample_path
            win._load_csv()

    win.show()
    sys.exit(app.exec())
