import sys, traceback
sys.path.insert(0, r'E:\Mod_Workspace\Modder_project\modder-hub\tools\flagship\TVox')
from tvox_app import TVoxApp
from PyQt6.QtWidgets import QApplication

app = QApplication(sys.argv)
try:
    window = TVoxApp()
    print('Init OK')
except Exception as e:
    traceback.print_exc()
