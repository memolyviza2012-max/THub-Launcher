#!/usr/bin/env python3
"""Validate mapping integrity and regression cases for ThaiFontMappingKit."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from thai_font_mapper import audit, load_mapping, make_pattern, map_text

ROOT = Path(__file__).resolve().parent


def main() -> int:
    mapping = load_mapping(ROOT / "Mapping.json")
    charset = set((ROOT / "Char.txt").read_text(encoding="utf-8").rstrip("\r\n"))
    errors: list[str] = []
    outputs = set("".join(mapping.values()))
    missing = outputs - charset
    if missing:
        errors.append("mapping output absent from Char.txt")
    if len(mapping) != 2208:
        errors.append(f"expected 2208 mapping entries, found {len(mapping)}")
    if len(mapping.values()) != len(set(mapping.values())):
        errors.append("mapping values are not one-to-one")
    cases = json.loads((ROOT / "test_cases.json").read_text(encoding="utf-8"))
    pattern = make_pattern(mapping)
    for case in cases:
        actual = map_text(case["input"], mapping, pattern)
        if actual != case["expected"]:
            errors.append(f"regression failed: {case['name']}")
        errors.extend(f"{case['name']}: {issue}" for issue in audit(actual, charset))
    if errors:
        print("FAILED\n- " + "\n- ".join(errors))
        return 1
    print(f"OK: {len(mapping)} mappings, {len(cases)} regression cases, all outputs in Char.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
