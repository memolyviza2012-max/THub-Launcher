import re
import os

path = r'E:\Mod_Workspace\Modder_project\modder-hub\tools\flagship\TStudio\tstudio_app.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update open_tlm_library and toggle_tlm_dock
old_open_tlm = r'''    def open_tlm_library\(self\):.*?except Exception as e:.*?QMessageBox\.critical\(self, _\("error_title"\), f"Could not open TLM Library:\\n\{e\}"\)'''

new_open_tlm = '''    def toggle_tlm_dock(self):
        if self.tlm_dock.isVisible():
            self.tlm_dock.hide()
        else:
            self.open_tlm_library()

    def open_tlm_library(self):
        try:
            from tstudio_tlm_library import TLMLoreLibrary
            if not hasattr(self, 'tlm_widget'):
                if not hasattr(self, 'glossary_widget'):
                    self.open_glossary()
                self.tlm_widget = TLMLoreLibrary(self.glossary_widget, self)
                self.tlm_dock.setWidget(self.tlm_widget)
                self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.tlm_dock)
            
            self.tlm_dock.show()
            self.tlm_dock.raise_()
        except Exception as e:
            import traceback
            traceback.print_exc()
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, _("error_title"), f"Could not open TLM Library:\\n{e}")'''

# First remove the old toggle_tlm_dock
text = re.sub(r'    def toggle_tlm_dock\(self\):\s+self\.open_tlm_library\(\)\s+', '', text)
text = re.sub(old_open_tlm, new_open_tlm, text, flags=re.DOTALL)

# 2. Add tlm_dock to layout_compact_tabbed but NOT tabified. 
# Just make sure it shows if it was created, or let it be handled dynamically.
# Actually, if we just call open_tlm_library, it adds it to RightDockWidgetArea. We don't need to force it into layout_compact_tabbed unless we want to. But the layout methods should probably restore it if it's visible.

layout_compact_pattern = r"self\.addDockWidget\(Qt\.DockWidgetArea\.RightDockWidgetArea, self\.glossary_dock\)"
new_layout_compact = '''self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.glossary_dock)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.tlm_dock)'''
text = text.replace(layout_compact_pattern, new_layout_compact)

layout_split_pattern = r"self\.addDockWidget\(Qt\.DockWidgetArea\.RightDockWidgetArea, self\.dock_trans\)"
new_layout_split = '''self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock_trans)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.tlm_dock)'''
text = text.replace(layout_split_pattern, new_layout_split)

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
print("Patched tstudio_app.py for TLM dock separation")
