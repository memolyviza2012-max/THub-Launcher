#!/usr/bin/env python3
"""TStudio parser plugin for KKnD 2: Krossfire localization YAML files.

Canonical project source:
E:/Mod_Workspace/Krush_Kill_‘N_Destroy_2_Krossfire/05_Scripts_and_Tools/yaml_parser.py
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Iterable


PROJECT_ROOT = Path(r"E:\Mod_Workspace\Krush_Kill_‘N_Destroy_2_Krossfire")
WORKSPACE_DIR = PROJECT_ROOT / "02_Translation_Workspace"
CSV_COLUMNS = ("key", "source", "translation", "context", "file_path")
ENTRY_RE = re.compile(r"^([0-9A-F]{8}):[ \t]+(\"(?:[^\"\\]|\\.)*\")[ \t]*$")


def _decode_yaml_string(quoted_value: str, line_number: int, path: Path) -> str:
    try:
        value = json.loads(quoted_value)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"{path}:{line_number}: invalid quoted YAML value: {exc.msg}"
        ) from exc
    if not isinstance(value, str):
        raise ValueError(f"{path}:{line_number}: value must be a string")
    return value


def _read_entries(filepath: Path) -> Iterable[tuple[str, str]]:
    raw = filepath.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raise ValueError(f"{filepath}: expected UTF-8 without BOM, but found a BOM")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"{filepath}: expected UTF-8: {exc}") from exc

    lines = text.splitlines()
    if not lines or not re.fullmatch(r"Language:[ \t]+.+", lines[0]):
        raise ValueError(f"{filepath}: missing required 'Language: …' header")

    seen: set[str] = set()
    entries: list[tuple[str, str]] = []
    for line_number, line in enumerate(lines[1:], start=2):
        if not line.strip():
            continue
        match = ENTRY_RE.fullmatch(line)
        if not match:
            raise ValueError(f"{filepath}:{line_number}: unsupported KKnD2 YAML syntax")
        key, quoted_value = match.groups()
        if key in seen:
            raise ValueError(f"{filepath}:{line_number}: duplicate key {key}")
        seen.add(key)
        entries.append((key, _decode_yaml_string(quoted_value, line_number, filepath)))
    if not entries:
        raise ValueError(f"{filepath}: no translatable KKnD2 string entries found")
    return entries


def convert_to_csv(filepath, parent_widget=None):
    """Convert KKnD2 YAML to standard TStudio CSV and return its path."""
    del parent_widget
    source_path = Path(filepath).resolve()
    if source_path.suffix.lower() != ".yaml":
        raise ValueError(f"Expected a .yaml file, got: {source_path.name}")
    entries = _read_entries(source_path)
    WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
    output_path = WORKSPACE_DIR / f"kknd2_krossfire_{source_path.stem}_tstudio.csv"
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for key, source in entries:
            writer.writerow(
                {
                    "key": key,
                    "source": source,
                    "translation": "",
                    "context": f"KKnD 2: Krossfire > strings > {key}",
                    "file_path": f"strings/{source_path.name}",
                }
            )
    return str(output_path)
