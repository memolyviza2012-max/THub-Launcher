import os
import json
import re

APPS = ["TStudio", "TRun", "TVox", "TGlyph", "TPUA"]
BASE_DIR = r"E:\Mod_Workspace\Modder_project\modder-hub\tools\flagship"

for app in APPS:
    app_dir = os.path.join(BASE_DIR, app)
    locales_dir = os.path.join(app_dir, "locales")
    th_json = os.path.join(locales_dir, "th.json")
    
    if not os.path.exists(th_json):
        print(f"Skipping {app}, no th.json")
        continue
        
    with open(th_json, "r", encoding="utf-8") as f:
        strings = json.load(f)
        
    # We want to replace occurrences of these strings in the .py files
    py_files = [f for f in os.listdir(app_dir) if f.endswith(".py") and f != "i18n_helper.py"]
    
    for py_file in py_files:
        py_path = os.path.join(app_dir, py_file)
        with open(py_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        original_content = content
        
        # Sort by length descending to avoid partial matches
        for k, v in sorted(strings.items(), key=lambda x: len(x[1]), reverse=True):
            if not v:
                continue
            # Escape for regex
            v_esc = re.escape(v)
            # Match both "..." and '...'
            pattern = r'(["\'])' + v_esc + r'\1'
            replacement = r'_("\2")'.replace(r'\2', k) # Just replace with _("key")
            content = re.sub(pattern, replacement, content)
            
        if content != original_content:
            # Ensure from i18n_helper import _ is present
            if 'from i18n_helper import _' not in content:
                content = 'from i18n_helper import _\n' + content
                
            with open(py_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Wrapped {py_file} in {app}")
