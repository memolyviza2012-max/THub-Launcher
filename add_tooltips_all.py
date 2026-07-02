import os
import re

APPS = ['TStudio', 'TRun', 'TVox', 'TGlyph', 'TPUA']
BASE_DIR = r'E:\Mod_Workspace\Modder_project\modder-hub\tools\flagship'

for app in APPS:
    app_dir = os.path.join(BASE_DIR, app)
    if not os.path.exists(app_dir): continue
    for py_file in os.listdir(app_dir):
        if not py_file.endswith('.py') or py_file == 'i18n_helper.py': continue
        path = os.path.join(app_dir, py_file)
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
            
        lines = text.split('\n')
        new_lines = []
        i = 0
        changed = False
        while i < len(lines):
            line = lines[i]
            new_lines.append(line)
            
            m = re.match(r'^(\s+)([\w\.]+)\s*=\s*(QPushButton|QAction)\(', line)
            if m:
                indent = m.group(1)
                var_name = m.group(2)
                
                has_tooltip = False
                for j in range(1, 6):
                    if i + j < len(lines):
                        if f'{var_name}.setToolTip' in lines[i+j]:
                            has_tooltip = True
                            break
                
                if not has_tooltip and 'action' not in var_name.lower():
                    clean_name = var_name.replace('self.', '').replace('btn_', '')
                    tooltip_code = f'{indent}{var_name}.setToolTip(_("tooltip_{clean_name}"))'
                    new_lines.append(tooltip_code)
                    changed = True
            i += 1
            
        if changed:
            with open(path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines))
            print(f'Added Tooltips to {app}/{py_file}')
