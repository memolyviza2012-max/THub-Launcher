import os
import sys

with open('qicon_out.txt', 'w') as f:
    try:
        from PyQt6.QtGui import QIcon
        from PyQt6.QtWidgets import QApplication
        f.write("Imports ok\n")
        app = QApplication(sys.argv)
        path = os.path.abspath(os.path.join("dist", "THub", "_internal", "assets", "TPUA.png"))
        f.write(f"Path: {path}\n")
        f.write(f"Path exists: {os.path.exists(path)}\n")
        icon = QIcon(path)
        f.write(f"Icon is null: {icon.isNull()}\n")
    except Exception as e:
        f.write(f"Error: {e}\n")
