import os
import re
from pathlib import Path

# --- 1. Modify TFont ---
tfont_app = Path(r'E:\Mod_Workspace\Modder_project\modder-hub\tools\flagship\TFont\tfont_app.py')
content = tfont_app.read_text('utf-8')
# Remove text tab init
content = re.sub(r'def init_text_tab\(self\):.*?def init_font_tab\(self\):', 'def init_font_tab(self):', content, flags=re.DOTALL)
# Remove tab insertion
content = re.sub(r'# --- TAB 3: Text Converter ---.*?# Log Window \(Shared\)', '# Log Window (Shared)', content, flags=re.DOTALL)
# Remove engine init block
content = re.sub(r'try:\s*from tfont_engine import TFontEngine.*?TFontEngine = None', '', content, flags=re.DOTALL)
# Remove engine instantiation
content = re.sub(r'self\.engine = TFontEngine\(\) if TFontEngine else None', 'self.engine = None', content)
content = re.sub(r'if self\.engine:.*?#a6e3a1"\)', '', content, flags=re.DOTALL)
tfont_app.write_text(content, 'utf-8')

# --- 2. Modify TPUA ---
tpua_app = Path(r'E:\Mod_Workspace\Modder_project\modder-hub\tools\flagship\TPUA\tpua_app.py')
content = tpua_app.read_text('utf-8')
# Replace TFont back to TPUA in tpua_app.py
replacements = {
    'tfont_app': 'tpua_app',
    'TFontApp': 'TPUAApp',
    'TFontEngine': 'TPUAEngine',
    'tfont_engine': 'tpua_engine',
    'TFONT.png': 'TPUA.png',
    'flagship.tfont': 'flagship.tpua'
}
for k, v in replacements.items():
    content = content.replace(k, v)

# Remove Font Generator and Visual Tuner init
content = re.sub(r'def init_font_tab\(self\):.*?def browse_in\(self\):', 'def browse_in(self):', content, flags=re.DOTALL)

# Remove tab insertion for fonts
content = re.sub(r'# --- TAB 1: Font Generator ---.*?# --- TAB 3: Text Converter ---', '# --- TAB 1: Text Converter ---', content, flags=re.DOTALL)

# Remove font imports
content = re.sub(r'try:\s*from tfont_generator import TFontGenerator.*?VisualTunerWidget = None', '', content, flags=re.DOTALL)

tpua_app.write_text(content, 'utf-8')

# Update manifest.json for TPUA
tpua_manifest = Path(r'E:\Mod_Workspace\Modder_project\modder-hub\tools\flagship\TPUA\manifest.json')
tpua_manifest.write_text('''{
    "id": "flagship.tpua",
    "name": "TPUA Text Converter",
    "version": "1.2.0",
    "description": "Text encoding/decoding tool for PUA ecosystem.",
    "author": "THub",
    "main": "tpua_app.py",
    "executable": "run_tpua.bat",
    "type": "flagship_tool"
}''', 'utf-8')

# Update manifest.json for TFont
tfont_manifest = Path(r'E:\Mod_Workspace\Modder_project\modder-hub\tools\flagship\TFont\manifest.json')
manifest_content = tfont_manifest.read_text('utf-8').replace('"name": "TFont: Universal PUA Hybrid Converter"', '"name": "TFont Generator"')
tfont_manifest.write_text(manifest_content, 'utf-8')

# Cleanup unneeded files
tfont_files_to_remove = [
    r'E:\Mod_Workspace\Modder_project\modder-hub\tools\flagship\TFont\Core\tfont_engine.py',
    r'E:\Mod_Workspace\Modder_project\modder-hub\tools\flagship\TFont\Core\tpua_engine.py'
]
tpua_files_to_remove = [
    r'E:\Mod_Workspace\Modder_project\modder-hub\tools\flagship\TPUA\Core\tfont_generator.py',
    r'E:\Mod_Workspace\Modder_project\modder-hub\tools\flagship\TPUA\Core\visual_font_engine.py',
    r'E:\Mod_Workspace\Modder_project\modder-hub\tools\flagship\TPUA\Core\visual_tuner_widget.py',
    r'E:\Mod_Workspace\Modder_project\modder-hub\tools\flagship\TPUA\Core\legacy_font_engine.py'
]

for f in tfont_files_to_remove + tpua_files_to_remove:
    p = Path(f)
    if p.exists():
        p.unlink()

print('Split processed.')
