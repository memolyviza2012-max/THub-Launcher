# -*- coding: utf-8 -*-
"""
pua_engine.py — PUA (Private Use Area) Mapping Generator for Thai Characters
=============================================================================

Generates PUA codepoints that fuse a Thai consonant with one or more
above/below modifiers (vowels, tone marks, thanthakhat) into a single
glyph slot inside a PUA font.

PUA Formula
-----------
    code = 0xF000 + (block_index × 47) + consonant_index

*   **block_index** — modifier combination (0-47, see ``MODIFIER_BLOCKS``).
*   **consonant_index** — position of the consonant in ``THAI_CONSONANTS``
    (0-45, 46 consonants from U+0E01 ก through U+0E2E ฮ).
*   **stride = 47** — the Noonetranslator convention reserves 47 slots per
    block even though only 46 consonants are used (index 46 is unused).

Resulting PUA range: U+F000 … U+F8CE  (2 208 active codepoints, all inside
the BMP Private Use Area U+E000–U+F8FF).

Quick start::

    >>> from pua_engine import generate_full_mapping, get_combo_for_pua
    >>> m = generate_full_mapping()
    >>> m["กั"]              # block 0, consonant 0
    'F000'
    >>> m["กำ"]              # contextual ำ → [PUA, า]
    ['F263', '0E32']
    >>> get_combo_for_pua(0xF000)
    'กั'
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Union


# =========================================================================== #
#  Constants                                                                   #
# =========================================================================== #

PUA_BASE: int = 0xF000
"""Base codepoint for the Private Use Area mappings (U+F000)."""

CONSONANT_STRIDE: int = 47
"""Slots reserved per modifier block.

The Noonetranslator mapping uses 47 as the stride even though there are
only 46 consonants; the extra slot (index 46) is left unused in every block.
"""

THAI_CONSONANTS: list[str] = [chr(cp) for cp in range(0x0E01, 0x0E2F)]
"""All 46 Thai consonant codepoints (ก–ฮ), U+0E01 … U+0E2E.

Includes obsolete consonants ฃ (U+0E03) and ฅ (U+0E05), as well as
ฤ (U+0E24), ฦ (U+0E26), and ฬ (U+0E2C).
"""

SARA_AA: int = 0x0E32
"""Sara Aa (า) — appended after the PUA glyph in contextual ำ decompositions.

When ำ (sara am, U+0E33) is decomposed, the nikkhahit part merges with the
consonant into a PUA glyph, and า (sara aa) follows as a separate character.
"""


# =========================================================================== #
#  Modifier block definitions                                                  #
# =========================================================================== #

# Each entry is a 2-tuple ``(suffix_chars, is_contextual)``:
#
# * **suffix_chars** — the modifier character(s) appended after the consonant
#   to form the mapping key.
# * **is_contextual** — if ``True`` the mapping value is a list
#   ``[pua_hex, "0E32"]`` instead of a plain hex string, because the ำ
#   decomposes into PUA + า.

MODIFIER_BLOCKS: list[tuple[str, bool]] = [
    # ── Single modifiers (blocks 0-12) ────────────────────────────────────
    ("\u0E31", False),   #  0: ั   sara am mai han akat (upper vowel shortener)
    ("\u0E34", False),   #  1: ิ   sara i
    ("\u0E35", False),   #  2: ี   sara ii
    ("\u0E36", False),   #  3: ึ   sara ue
    ("\u0E37", False),   #  4: ื   sara uee
    ("\u0E38", False),   #  5: ุ   sara u
    ("\u0E39", False),   #  6: ู   sara uu
    ("\u0E47", False),   #  7: ็   mai tai khu
    ("\u0E48", False),   #  8: ่   mai ek      (tone 1)
    ("\u0E49", False),   #  9: ้   mai tho     (tone 2)
    ("\u0E4A", False),   # 10: ๊   mai tri     (tone 3)
    ("\u0E4B", False),   # 11: ๋   mai chattawa (tone 4)
    ("\u0E4C", False),   # 12: ์   thanthakhat (silent mark)

    # ── Contextual: ำ (block 13) → [PUA, า] ───────────────────────────────
    ("\u0E33", True),    # 13: ำ   sara am → decomposes to nikkhahit + sara aa

    # ── Double modifiers: ั + tones (blocks 14-17) ────────────────────────
    ("\u0E31\u0E48", False),  # 14: ั่
    ("\u0E31\u0E49", False),  # 15: ั้
    ("\u0E31\u0E4A", False),  # 16: ั๊
    ("\u0E31\u0E4B", False),  # 17: ั๋

    # ── Double modifiers: ิ + tones/thanthakhat (blocks 18-22) ────────────
    ("\u0E34\u0E48", False),  # 18: ิ่
    ("\u0E34\u0E49", False),  # 19: ิ้
    ("\u0E34\u0E4A", False),  # 20: ิ๊
    ("\u0E34\u0E4B", False),  # 21: ิ๋
    ("\u0E34\u0E4C", False),  # 22: ิ์

    # ── Double modifiers: ี + tones (blocks 23-26) ────────────────────────
    ("\u0E35\u0E48", False),  # 23: ี่
    ("\u0E35\u0E49", False),  # 24: ี้
    ("\u0E35\u0E4A", False),  # 25: ี๊
    ("\u0E35\u0E4B", False),  # 26: ี๋

    # ── Double modifiers: ึ + tones (blocks 27-30) ────────────────────────
    ("\u0E36\u0E48", False),  # 27: ึ่
    ("\u0E36\u0E49", False),  # 28: ึ้
    ("\u0E36\u0E4A", False),  # 29: ึ๊
    ("\u0E36\u0E4B", False),  # 30: ึ๋

    # ── Double modifiers: ื + tones (blocks 31-34) ────────────────────────
    ("\u0E37\u0E48", False),  # 31: ื่
    ("\u0E37\u0E49", False),  # 32: ื้
    ("\u0E37\u0E4A", False),  # 33: ื๊
    ("\u0E37\u0E4B", False),  # 34: ื๋

    # ── Double modifiers: ุ + tones/thanthakhat (blocks 35-39) ────────────
    ("\u0E38\u0E48", False),  # 35: ุ่
    ("\u0E38\u0E49", False),  # 36: ุ้
    ("\u0E38\u0E4A", False),  # 37: ุ๊
    ("\u0E38\u0E4B", False),  # 38: ุ๋
    ("\u0E38\u0E4C", False),  # 39: ุ์

    # ── Double modifiers: ู + tones (blocks 40-43) ────────────────────────
    ("\u0E39\u0E48", False),  # 40: ู่
    ("\u0E39\u0E49", False),  # 41: ู้
    ("\u0E39\u0E4A", False),  # 42: ู๊
    ("\u0E39\u0E4B", False),  # 43: ู๋

    # ── Contextual: tone + ำ (blocks 44-47) → [PUA, า] ───────────────────
    ("\u0E48\u0E33", True),   # 44: ่ำ
    ("\u0E49\u0E33", True),   # 45: ้ำ
    ("\u0E4A\u0E33", True),   # 46: ๊ำ
    ("\u0E4B\u0E33", True),   # 47: ๋ำ
]
"""Ordered list of 48 modifier blocks (index 0-47).

Each block defines a modifier suffix and whether the mapping is contextual.
The block index is used directly in the PUA formula.
"""


# =========================================================================== #
#  Internal helpers                                                            #
# =========================================================================== #

# Lazily-populated reverse lookup cache
_pua_to_combo: dict[int, str] | None = None


def _build_reverse_lookup() -> dict[int, str]:
    """Build the reverse PUA-codepoint → Thai-combo lookup table.

    Returns:
        Dictionary mapping each PUA integer codepoint to its Thai
        consonant + modifier string.
    """
    table: dict[int, str] = {}
    for block_idx, (suffix, _contextual) in enumerate(MODIFIER_BLOCKS):
        for con_idx, consonant in enumerate(THAI_CONSONANTS):
            code = PUA_BASE + block_idx * CONSONANT_STRIDE + con_idx
            table[code] = consonant + suffix
    return table


# =========================================================================== #
#  Public API                                                                  #
# =========================================================================== #

def generate_full_mapping() -> dict[str, Union[str, list[str]]]:
    """Generate the complete PUA mapping for all consonant + modifier combos.

    Iterates over every combination of 46 consonants × 48 modifier blocks
    and computes the PUA codepoint using the formula::

        code = 0xF000 + block_index * 47 + consonant_index

    Returns:
        A dictionary keyed by the Thai character combination string.

        * **Non-contextual entries** — value is a hex string:
          ``{"กั": "F000", ...}``
        * **Contextual entries** (blocks containing ำ) — value is a two-
          element list ``[pua_hex, "0E32"]``, where ``0E32`` is sara aa (า):
          ``{"กำ": ["F263", "0E32"], ...}``

    Examples::

        >>> m = generate_full_mapping()
        >>> m["กั"]          # block 0, consonant 0 → 0xF000
        'F000'
        >>> m["ขั"]          # block 0, consonant 1 → 0xF001
        'F001'
        >>> m["กิ"]          # block 1, consonant 0 → 0xF02F
        'F02F'
        >>> m["กำ"]          # block 13, contextual
        ['F263', '0E32']
        >>> m["กั่"]         # block 14, consonant 0 → 0xF292
        'F292'
        >>> m["ก่ำ"]         # block 44, contextual
        ['F814', '0E32']
        >>> len(m)
        2208
    """
    mapping: dict[str, Union[str, list[str]]] = {}

    for block_idx, (suffix, contextual) in enumerate(MODIFIER_BLOCKS):
        for con_idx, consonant in enumerate(THAI_CONSONANTS):
            code = PUA_BASE + block_idx * CONSONANT_STRIDE + con_idx
            key = consonant + suffix
            hex_str = f"{code:04X}"

            if contextual:
                mapping[key] = [hex_str, f"{SARA_AA:04X}"]
            else:
                mapping[key] = hex_str

    return mapping


def load_external_mapping(path: Union[str, Path]) -> dict[str, str]:
    """Load a Noonetranslator-style ``Mapping.json`` file.

    The expected JSON format is an object whose keys are Thai character
    combinations (e.g. ``"กั"``) and whose values are either:

    * an empty string ``""`` — meaning *"needs a PUA code"*, or
    * a non-empty string like ``"า"`` — meaning *"already resolved"*.

    Args:
        path: Filesystem path to the JSON mapping file (UTF-8 encoded).

    Returns:
        The parsed dictionary ``{combo_str: value_str, ...}``.

    Raises:
        FileNotFoundError: If *path* does not exist.
        json.JSONDecodeError: If the file is not valid JSON.

    Example::

        >>> ext = load_external_mapping("Mapping.json")
        >>> ext["กั"]        # empty → needs PUA code
        ''
        >>> ext["กำ"]        # non-empty → already mapped
        'า'
    """
    filepath = Path(path)
    with filepath.open("r", encoding="utf-8") as fh:
        data: dict[str, str] = json.load(fh)
    return data


def merge_mappings(
    generated: dict[str, Union[str, list[str]]],
    external: dict[str, str],
) -> dict[str, Union[str, list[str]]]:
    """Fill empty values in an external mapping with generated PUA codes.

    For every key in *external* whose value is an empty string ``""``, the
    corresponding value from *generated* is substituted.  Keys that already
    carry a non-empty value are preserved as-is.

    Args:
        generated: Mapping produced by :func:`generate_full_mapping`.
        external:  Mapping loaded by :func:`load_external_mapping`.

    Returns:
        A **new** dictionary with the same keys as *external*, but with
        formerly-empty values now populated from *generated*.

    Examples::

        >>> gen = generate_full_mapping()
        >>> ext = {"กั": "", "กำ": "า", "ขิ": ""}
        >>> merged = merge_mappings(gen, ext)
        >>> merged["กั"]     # was empty → filled with PUA hex
        'F000'
        >>> merged["กำ"]     # was non-empty → kept original value
        'า'
        >>> merged["ขิ"]     # was empty → filled with PUA hex
        'F030'
    """
    merged: dict[str, Union[str, list[str]]] = {}
    for key, value in external.items():
        if value == "":
            # Fill from generated mapping; fall back to empty string if the
            # key doesn't exist in the generated mapping either.
            merged[key] = generated.get(key, "")
        else:
            merged[key] = value
    return merged


def get_all_pua_codepoints() -> list[int]:
    """Return a sorted list of every PUA codepoint used by the mapping.

    The returned list contains one entry per consonant × block combination
    (46 consonants × 48 blocks = 2 208 codepoints).

    Returns:
        Sorted list of integer codepoints in the Private Use Area
        (U+F000 … U+F8CE).

    Examples::

        >>> pts = get_all_pua_codepoints()
        >>> hex(pts[0])
        '0xf000'
        >>> hex(pts[-1])
        '0xf8ce'
        >>> len(pts)
        2208
    """
    codepoints: list[int] = []
    for block_idx in range(len(MODIFIER_BLOCKS)):
        for con_idx in range(len(THAI_CONSONANTS)):
            codepoints.append(PUA_BASE + block_idx * CONSONANT_STRIDE + con_idx)
    return sorted(codepoints)


def get_combo_for_pua(pua_code: int) -> str:
    """Reverse-lookup: find the Thai combination for a given PUA codepoint.

    The lookup table is built lazily on first call and cached for subsequent
    lookups.

    Args:
        pua_code: An integer PUA codepoint (e.g. ``0xF000``).

    Returns:
        The Thai character combination string (e.g. ``"กั"``).

    Raises:
        KeyError: If *pua_code* does not correspond to any mapping entry.

    Examples::

        >>> get_combo_for_pua(0xF000)
        'กั'
        >>> get_combo_for_pua(0xF001)
        'ขั'
        >>> get_combo_for_pua(0xF263)
        'กำ'
        >>> get_combo_for_pua(0xFFFF)
        Traceback (most recent call last):
            ...
        KeyError: 'PUA codepoint U+FFFF is not in the mapping'
    """
    global _pua_to_combo
    if _pua_to_combo is None:
        _pua_to_combo = _build_reverse_lookup()

    if pua_code not in _pua_to_combo:
        raise KeyError(
            f"PUA codepoint U+{pua_code:04X} is not in the mapping"
        )
    return _pua_to_combo[pua_code]


def load_charset(path: Union[str, Path]) -> list[str]:
    """Load a character set from a ``message.txt`` file.

    Each non-empty line in the file is treated as one character entry.
    Leading and trailing whitespace is stripped; blank lines are skipped.

    This is useful for loading the set of glyphs that a font is expected
    to render, so that only the relevant PUA mappings need to be generated
    or verified.

    Args:
        path: Filesystem path to the character-set text file (UTF-8).

    Returns:
        List of character strings read from the file, in file order.

    Raises:
        FileNotFoundError: If *path* does not exist.

    Example::

        >>> # Given a message.txt with lines: ก\\nข\\nค
        >>> chars = load_charset("message.txt")
        >>> chars
        ['ก', 'ข', 'ค']
    """
    filepath = Path(path)
    with filepath.open("r", encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    return [line.strip() for line in lines if line.strip()]


# =========================================================================== #
#  CLI quick-test                                                              #
# =========================================================================== #

if __name__ == "__main__":
    print("=" * 60)
    print("  PUA Engine — Thai PUA Mapping Generator")
    print("=" * 60)

    mapping = generate_full_mapping()
    all_pts = get_all_pua_codepoints()

    print(f"\n  Consonants         : {len(THAI_CONSONANTS)}")
    print(f"  Modifier blocks    : {len(MODIFIER_BLOCKS)}")
    print(f"  Consonant stride   : {CONSONANT_STRIDE}")
    print(f"  Total entries      : {len(mapping)}")
    print(f"  Total PUA codes    : {len(all_pts)}")
    print(f"  PUA range          : U+{all_pts[0]:04X} … U+{all_pts[-1]:04X}")

    # Spot-check a selection of entries
    print("\n  ── Sample mappings ──")
    samples = [
        ("กั",  "block  0, con 0"),
        ("ขั",  "block  0, con 1"),
        ("กิ",  "block  1, con 0"),
        ("กำ",  "block 13, contextual"),
        ("กั่", "block 14, con 0"),
        ("กิ้", "block 19, con 0"),
        ("ฮู้", "block 41, con 45"),
        ("ก่ำ", "block 44, contextual"),
    ]
    for combo, description in samples:
        val = mapping.get(combo, "— not found —")
        print(f"    {combo!r:8s} → {str(val):20s}  ({description})")

    # Reverse lookup
    print("\n  ── Reverse lookup ──")
    for code in [0xF000, 0xF001, 0xF263, 0xF8CE]:
        try:
            combo = get_combo_for_pua(code)
            print(f"    U+{code:04X} → {combo!r}")
        except KeyError as exc:
            print(f"    U+{code:04X} → {exc}")

    print()
