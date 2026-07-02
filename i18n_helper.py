"""
i18n_helper.py — TStudio Internationalization Helper
======================================================
Provides the _() function for translating UI strings.

Usage:
    from i18n_helper import _
    label = _("save_project")           # → "บันทึกโปรเจกต์" (th) or localized string
    msg   = _("tm_autofill_success", count=5)  # → "เติมคำแปลอัตโนมัติจาก TM สำเร็จ 5 บรรทัด!"

Locale is controlled by the THUB_LANG environment variable.
Supported codes: th, en, zh, ja, ar, ru
Falls back to th.json if the requested locale file does not exist.
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

    val = _cache[lang].get(key, key)
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
