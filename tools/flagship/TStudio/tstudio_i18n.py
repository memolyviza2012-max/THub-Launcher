
import os
import json
from pathlib import Path
import sys

def get_base_path(file_path, module_name):
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS) / 'tools' / 'flagship' / module_name
    return Path(os.path.abspath(file_path)).parent

_LOCALES = get_base_path(__file__, 'TStudio') / 'locales'
_cache = {}

def _(key, **kw):
    lang = os.environ.get('THUB_LANG', 'th')
    if lang not in _cache:
        p = _LOCALES / f'{lang}.json'
        if not p.exists():
            p = _LOCALES / 'th.json'
        try:
            with open(p, encoding='utf-8') as f:
                _cache[lang] = json.load(f)
        except Exception:
            _cache[lang] = {}
            
    val = _cache[lang].get(key, key)
    try:
        return val.format(**kw) if kw else val
    except Exception:
        return val
