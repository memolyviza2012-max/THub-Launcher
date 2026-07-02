import os
import json
from pathlib import Path

_LOCALES = Path(__file__).parent / 'locales'
_TSTUDIO_LOCALES = Path(__file__).parent.parent / 'TStudio' / 'locales'
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
        # Load TStudio fallback dictionary first
        base_dict = _load_lang(_TSTUDIO_LOCALES, lang)
        
        # Load local tool dictionary and overwrite base
        local_dict = _load_lang(_LOCALES, lang)
        
        merged = base_dict.copy()
        merged.update(local_dict)
        _cache[lang] = merged
        
    # Preload English for fallback
    if 'en' not in _cache:
        base_en = _load_lang(_TSTUDIO_LOCALES, 'en')
        local_en = _load_lang(_LOCALES, 'en')
        merged_en = base_en.copy()
        merged_en.update(local_en)
        _cache['en'] = merged_en

    # Preload Thai for fallback
    if 'th' not in _cache:
        base_th = _load_lang(_TSTUDIO_LOCALES, 'th')
        local_th = _load_lang(_LOCALES, 'th')
        merged_th = base_th.copy()
        merged_th.update(local_th)
        _cache['th'] = merged_th

    val = _cache[lang].get(key)
    if val is None:
        val = _cache['en'].get(key)
    if val is None:
        val = _cache['th'].get(key, key)

    try:
        return val.format(**kw) if kw else val
    except Exception:
        return val
