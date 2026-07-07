import os
import json
from pathlib import Path
import sys

def get_base_path(module_name):
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS) / 'tools' / 'flagship' / module_name
    return Path(os.path.abspath(__file__)).parent

_LOCALES = get_base_path('TVox') / 'locales'
_TSTUDIO_LOCALES = get_base_path('TStudio') / 'locales'
_cache = {}

def _load_lang(locales_path, lang):
    p = locales_path / f'{lang}.json'
    if not p.exists():
        p = locales_path / 'th.json'
    try:
        with open(p, encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def _(key, **kw):
    lang = os.environ.get('THUB_LANG', 'th')
    if lang not in _cache:
        base_dict = _load_lang(_TSTUDIO_LOCALES, lang)
        local_dict = _load_lang(_LOCALES, lang)
        merged = base_dict.copy()
        merged.update(local_dict)
        _cache[lang] = merged
        
    val = _cache[lang].get(key, key)
    try:
        return val.format(**kw) if kw else val
    except Exception:
        return val
