"""scr_parser.py – Read and write .scr font definition files (C-Engine / Dying Light 2).

SCR files are plain-text lists of ``Char(codepoint, bw, bh, ax, ay, ox, oy, adv, page)``
entries together with ``Texture("…")`` references.  This module provides helpers to:

* **parse** SCR text into a codepoint→metrics dictionary,
* **patch** specific codepoints inside existing SCR text,
* **extract / save** SCR files from/to PAK archives (ZIP format),
* **generate** individual ``Char(…)`` lines.
"""

from __future__ import annotations

import re
import zipfile
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------------------------

# Matches: Char(3585, 14, 40, 120, 8, 0, -38, 13.0, 0)
_CHAR_RE = re.compile(
    r"Char\(\s*"
    r"(?P<cp>-?\d+)\s*,\s*"       # codepoint
    r"(?P<bw>-?\d+)\s*,\s*"       # bitmap width
    r"(?P<bh>-?\d+)\s*,\s*"       # bitmap height
    r"(?P<ax>-?\d+)\s*,\s*"       # atlas x
    r"(?P<ay>-?\d+)\s*,\s*"       # atlas y
    r"(?P<ox>-?\d+)\s*,\s*"       # x offset
    r"(?P<oy>-?\d+)\s*,\s*"       # y offset
    r"(?P<adv>-?[\d.]+)\s*,\s*"   # x advance (float)
    r"(?P<page>-?\d+)\s*"         # page
    r"\)"
)

# Matches: Texture("common_fonts_0_pc_uif")
_TEXTURE_RE = re.compile(r'Texture\(\s*"([^"]+)"\s*\)')


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse_scr(scr_text: str) -> dict[int, dict[str, Any]]:
    """Parse SCR text and return a mapping of *codepoint* → glyph metrics.

    Returns
    -------
    dict[int, dict]
        ``{codepoint: {'bw': int, 'bh': int, 'ax': int, 'ay': int,
        'ox': int, 'oy': int, 'adv': float, 'page': int}}``
    """
    result: dict[int, dict[str, Any]] = {}
    for m in _CHAR_RE.finditer(scr_text):
        cp = int(m.group("cp"))
        result[cp] = {
            "bw":   int(m.group("bw")),
            "bh":   int(m.group("bh")),
            "ax":   int(m.group("ax")),
            "ay":   int(m.group("ay")),
            "ox":   int(m.group("ox")),
            "oy":   int(m.group("oy")),
            "adv":  float(m.group("adv")),
            "page": int(m.group("page")),
        }
    return result


def patch_scr(original_scr: str, updates: dict[int, dict[str, Any]]) -> str:
    """Return *original_scr* with selected codepoints replaced by *updates*.

    Only the codepoints present in *updates* are modified; every other line
    (including ``Texture(…)`` references and comments) is kept verbatim.

    Parameters
    ----------
    original_scr:
        Full SCR file text.
    updates:
        ``{codepoint: {field: value, …}}``.  Each inner dict may contain any
        subset of ``bw, bh, ax, ay, ox, oy, adv, page``; missing keys are
        filled from the original entry.
    """

    # Build a lookup of original metrics so we can fall back for missing keys.
    originals = parse_scr(original_scr)

    def _replace_char(m: re.Match[str]) -> str:
        cp = int(m.group("cp"))
        if cp not in updates:
            return m.group(0)  # untouched

        # Merge: start from original, overlay with caller's updates.
        base = originals.get(cp, {})
        merged = {**base, **updates[cp]}

        return generate_char_entry(
            codepoint=cp,
            bw=int(merged["bw"]),
            bh=int(merged["bh"]),
            ax=int(merged["ax"]),
            ay=int(merged["ay"]),
            ox=int(merged["ox"]),
            oy=int(merged["oy"]),
            adv=float(merged["adv"]),
            page=int(merged.get("page", 0)),
        )

    return _CHAR_RE.sub(_replace_char, original_scr)


def extract_scr_from_pak(
    pak_path: str,
    scr_name: str = "gui/common_pc/din_pro_medium_16_pc.scr",
) -> str:
    """Open a ``.pak`` file (ZIP format) and return the SCR entry as text.

    Parameters
    ----------
    pak_path:
        Path to the ``.pak`` archive.
    scr_name:
        Internal ZIP member path of the SCR file.

    Returns
    -------
    str
        The decoded SCR text (UTF-8).
    """
    with zipfile.ZipFile(pak_path, "r") as zf:
        raw = zf.read(scr_name)
    return raw.decode("utf-8")


def save_scr_to_pak(
    pak_path: str,
    scr_name: str,
    scr_text: str,
    output_pak: str,
) -> None:
    """Create a new PAK (ZIP) containing the modified SCR file.

    If *pak_path* exists and *output_pak* differs from *pak_path*, all
    other members of the original archive are copied across unchanged.
    If *output_pak* equals *pak_path*, the archive is rewritten in-place.

    Parameters
    ----------
    pak_path:
        Path to the **original** ``.pak`` archive (may not exist yet).
    scr_name:
        Internal ZIP member path for the SCR file.
    scr_text:
        The full SCR text to write.
    output_pak:
        Path for the resulting ``.pak`` archive.
    """
    src = Path(pak_path)
    dst = Path(output_pak)

    members: dict[str, bytes] = {}

    # Carry over existing members (if any).
    if src.exists():
        with zipfile.ZipFile(src, "r") as zf:
            for name in zf.namelist():
                if name != scr_name:
                    members[name] = zf.read(name)

    # Insert / replace the SCR entry.
    members[scr_name] = scr_text.encode("utf-8")

    with zipfile.ZipFile(dst, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, data in members.items():
            zf.writestr(name, data)


def generate_char_entry(
    codepoint: int,
    bw: int,
    bh: int,
    ax: int,
    ay: int,
    ox: int,
    oy: int,
    adv: float,
    page: int = 0,
) -> str:
    """Return a formatted ``Char(…)`` string.

    The *adv* value is formatted to one decimal place when it has a
    fractional part, or as an integer-style float (``13.0``) otherwise.

    Example
    -------
    >>> generate_char_entry(3585, 14, 40, 120, 8, 0, -38, 13.0, 0)
    'Char(3585, 14, 40, 120, 8, 0, -38, 13.0, 0)'
    """
    # Format advance: keep one decimal so "13.0" stays "13.0".
    if adv == int(adv):
        adv_str = f"{adv:.1f}"
    else:
        # Strip trailing zeros but keep at least one decimal digit.
        adv_str = f"{adv:.4f}".rstrip("0")
        if adv_str.endswith("."):
            adv_str += "0"

    return (
        f"Char({codepoint}, {bw}, {bh}, {ax}, {ay}, "
        f"{ox}, {oy}, {adv_str}, {page})"
    )


def parse_textures(scr_text: str) -> list[str]:
    """Return all ``Texture("…")`` names found in the SCR text."""
    return _TEXTURE_RE.findall(scr_text)


# ---------------------------------------------------------------------------
# Quick self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    sample = (
        'Texture("common_fonts_0_pc_uif")\r\n'
        "Char(3585, 14, 40, 120, 8, 0, -38, 13.0, 0)\n"
        "Char(3586, 15, 28, 134, 8, 0, -26, 14.0, 0)\n"
    )

    glyphs = parse_scr(sample)
    assert 3585 in glyphs
    assert glyphs[3585]["bw"] == 14
    assert glyphs[3585]["adv"] == 13.0

    textures = parse_textures(sample)
    assert textures == ["common_fonts_0_pc_uif"]

    patched = patch_scr(sample, {3585: {"ax": 200, "ay": 50}})
    patched_glyphs = parse_scr(patched)
    assert patched_glyphs[3585]["ax"] == 200
    assert patched_glyphs[3585]["ay"] == 50
    # Unmodified fields preserved.
    assert patched_glyphs[3585]["bw"] == 14
    # Unmodified codepoints preserved.
    assert patched_glyphs[3586]["bw"] == 15

    entry = generate_char_entry(3585, 14, 40, 120, 8, 0, -38, 13.0, 0)
    assert entry == "Char(3585, 14, 40, 120, 8, 0, -38, 13.0, 0)"

    print("All self-tests passed.")
