import re

path = r'E:\Mod_Workspace\Modder_project\modder-hub\tools\flagship\TStudio\tstudio_app.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. In __init__, we need to create the tlm_dock and tabify it with glossary_dock
# Let's insert the tlm_dock creation right after glossary_dock creation.
glossary_dock_pattern = r'self\.glossary_dock = QDockWidget\(_\("dock_glossary"\), self\)\s+self\.glossary_dock\.setObjectName\("dock_glossary"\)\s+self\.glossary_dock\.setAllowedAreas\(Qt\.DockWidgetArea\.AllDockWidgetAreas\)'

tlm_dock_creation = '''self.glossary_dock = QDockWidget(_("dock_glossary"), self)
        self.glossary_dock.setObjectName("dock_glossary")
        self.glossary_dock.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        
        self.tlm_dock = QDockWidget(_("dock_tlm") if _("dock_tlm") != "dock_tlm" else "🧠 TLM Extractor", self)
        self.tlm_dock.setObjectName("dock_tlm")
        self.tlm_dock.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        
        # Instantiate TLM widget
        from tstudio_tlm_library import TLMLoreLibrary
        if not hasattr(self, 'glossary_widget'):
            from tstudio_ui_shared import GlossaryWidget
            self.glossary_widget = GlossaryWidget(self.glossary_dock)
            self.glossary_dock.setWidget(self.glossary_widget)
            self.glossary_widget.btn_toggle_tlm.clicked.connect(self.toggle_tlm_dock)
        
        self.tlm_widget = TLMLoreLibrary(self.glossary_widget, self)
        self.tlm_dock.setWidget(self.tlm_widget)
        self.tlm_dock.hide() # Hidden by default'''

text = re.sub(glossary_dock_pattern, tlm_dock_creation, text)

# 2. Modify toggle_tlm_dock method
toggle_method_pattern = r'def toggle_tlm_dock\(self\):.*?if hasattr\(self, \'tlm_window\'\).*?else:.*?self\.tlm_window = TLMLoreLibrary\(self\.glossary_widget, self\).*?self\.tlm_window\.show\(\)'

new_toggle_method = '''def toggle_tlm_dock(self):
        if hasattr(self, 'tlm_dock'):
            if self.tlm_dock.isVisible():
                self.tlm_dock.hide()
            else:
                self.tlm_dock.show()
                self.tlm_dock.raise_()'''

text = re.sub(toggle_method_pattern, new_toggle_method, text, flags=re.DOTALL)

# 3. Add to tabify calls in layout_compact_tabbed
tabify_pattern = r'self\.tabifyDockWidget\(self\.dock_ai, self\.glossary_dock\)'
new_tabify = '''self.tabifyDockWidget(self.dock_ai, self.glossary_dock)
            self.tabifyDockWidget(self.glossary_dock, self.tlm_dock)'''
text = text.replace(tabify_pattern, new_tabify)

tabify_pattern_2 = r'self\.tabifyDockWidget\(self\.dock_trans, self\.glossary_dock\)'
new_tabify_2 = '''self.tabifyDockWidget(self.dock_trans, self.glossary_dock)
            self.tabifyDockWidget(self.glossary_dock, self.tlm_dock)'''
text = text.replace(tabify_pattern_2, new_tabify_2)

# Ensure addDockWidget is called for tlm_dock in layout setups
add_dock_pattern = r'self\.addDockWidget\(Qt\.DockWidgetArea\.RightDockWidgetArea, self\.glossary_dock\)'
new_add_dock = '''self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.glossary_dock)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.tlm_dock)'''
text = text.replace(add_dock_pattern, new_add_dock)

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
print('Patched tstudio_app.py to add TLM QDockWidget')
