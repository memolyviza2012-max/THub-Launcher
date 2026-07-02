"""
tstudio_i18n.py — TStudio Internationalization Helper (Isolated)
======================================================
Provides the _() function for translating UI strings.
"""

import os
import json
from pathlib import Path

_LOCALES = Path(os.path.abspath(__file__)).parent / "locales"
_cache: dict = {}


def _(key: str, **kw) -> str:
    """Return the localized string for *key*, optionally formatting with keyword args."""
    lang = os.environ.get("THUB_LANG", "th")

    if lang not in _cache:
        p = _LOCALES / f"{lang}.json"
        if not p.exists():
            p = _LOCALES / "th.json"
        try:
            with open(p, encoding="utf-8") as f:
                _cache[lang] = json.load(f)
        except Exception:
            _cache[lang] = {}

    # Load English cache for fallback
    if "en" not in _cache:
        try:
            with open(_LOCALES / "en.json", encoding="utf-8") as f:
                _cache["en"] = json.load(f)
        except Exception:
            _cache["en"] = {}

    # Load Thai cache for fallback
    if "th" not in _cache:
        try:
            with open(_LOCALES / "th.json", encoding="utf-8") as f:
                _cache["th"] = json.load(f)
        except Exception:
            _cache["th"] = {}

    val = _cache[lang].get(key)
    if val is None:
        val = _cache["en"].get(key)
    if val is None:
        val = _cache["th"].get(key, key)

    try:
        return val.format(**kw) if kw else val
    except (KeyError, ValueError):
        return val


def set_language(lang: str) -> None:
    """Programmatically change the active language (bypasses env var)."""
    os.environ["THUB_LANG"] = lang
    # Clear cache so next call reloads
    _cache.clear()


def get_available_languages() -> list:
    """Return list of available language codes based on locale JSON files."""
    if not _LOCALES.exists():
        return ["th"]
    return sorted(
        p.stem for p in _LOCALES.glob("*.json")
    )
