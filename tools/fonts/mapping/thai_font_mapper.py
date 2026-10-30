#!/usr/bin/env python3
"""Map Thai text to the PUA glyphs defined by Mapping.json.

The mapper deliberately chooses the longest source sequence first.  This is
required because a shorter sequence (for example กั) can be the prefix of a
longer glyph sequence (กั่).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
# U+0E32 is SARA AA: a spacing vowel deliberately retained by the ำ mappings.
THAI_COMBINING = {0x0E31} | set(range(0x0E34, 0x0E3B)) | set(range(0x0E47, 0x0E4F))


def normalize_thai(text: str) -> str:
    """Use NFC and canonicalize decomposed SARA AM (ํา) to ำ."""
    text = unicodedata.normalize("NFC", text)
    return text.replace("\u0e4d\u0e32", "\u0e33")


def load_mapping(path: Path) -> dict[str, str]:
    mapping = json.loads(path.read_text(encoding="utf-8"))
    if len(mapping) != len(set(mapping.values())):
        raise ValueError("Mapping values must be unique.")
    return mapping


def make_pattern(mapping: dict[str, str]) -> re.Pattern[str]:
    # Do not rely on JSON property order; it is an implementation detail.
    keys = sorted(mapping, key=lambda key: (-len(key), key))
    return re.compile("|".join(re.escape(key) for key in keys))


def map_text(text: str, mapping: dict[str, str], pattern: re.Pattern[str]) -> str:
    text = normalize_thai(text)
    return pattern.sub(lambda match: mapping[match.group(0)], text)


def audit(text: str, charset: set[str]) -> list[str]:
    issues: list[str] = []
    unmapped_marks = sorted({char for char in text if ord(char) in THAI_COMBINING})
    # Layout controls are handled by the game's text renderer, not by a glyph.
    allowed_controls = {"\r", "\n", "\t"}
    unsupported = sorted({char for char in text if char not in charset and char not in allowed_controls})
    if unmapped_marks:
        issues.append("unmapped Thai combining marks: " + " ".join(f"U+{ord(c):04X}" for c in unmapped_marks))
    if unsupported:
        issues.append("characters absent from Char.txt: " + " ".join(f"U+{ord(c):04X}" for c in unsupported))
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert UTF-8 Thai text to this font's PUA mapping.")
    parser.add_argument("input", nargs="?", help="UTF-8 input file; omit to read standard input")
    parser.add_argument("-o", "--output", help="UTF-8 output file; omit to write standard output")
    parser.add_argument("--mapping", type=Path, default=ROOT / "Mapping.json")
    parser.add_argument("--chars", type=Path, default=ROOT / "Char.txt")
    parser.add_argument("--audit", action="store_true", help="fail if Thai combining marks or unsupported characters remain")
    args = parser.parse_args()

    source = Path(args.input).read_text(encoding="utf-8") if args.input else sys.stdin.read()
    mapping = load_mapping(args.mapping)
    result = map_text(source, mapping, make_pattern(mapping))
    if args.audit:
        charset = set(args.chars.read_text(encoding="utf-8").rstrip("\r\n"))
        problems = audit(result, charset)
        if problems:
            print("Audit failed: " + "; ".join(problems), file=sys.stderr)
            return 2
    if args.output:
        Path(args.output).write_text(result, encoding="utf-8", newline="")
    else:
        sys.stdout.write(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
