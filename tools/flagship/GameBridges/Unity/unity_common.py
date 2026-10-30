"""Shared, robust utilities for THub's Unity Thai Localization Engine.

Provides cryptographic hashing, TStudio CSV schema definition, protected token
validation, UnityPy loader fallback, and JSON pointer utilities.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Iterator, Tuple, List, Dict, Optional

# TStudio Standard 5-column CSV Specification
CSV_COLUMNS = ["key", "source", "translation", "context", "file_path"]

# Recognized protected tokens in game translation strings
PROTECTED_TOKEN_PATTERN = re.compile(
    r"(?:"
    r"%(?:\d+\$)?[+-]?(?:0|\'.)?-?\d*(?:\.\d+)?[a-zA-Z%]"  # printf format specifiers e.g. %s, %d, %1$s, %0.2f
    r"|\{\d+(?:,[^}:]+)?(?::[^}]+)?\}"                     # C# / .NET composite format specifiers e.g. {0}, {1:N2}
    r"|<[^>]+>"                                            # Rich text / XML / TMP tags e.g. <color=#FF0000>, </color>, <b>, </b>
    r"|\\[nrtfvb0]"                                        # Escape sequences e.g. \n, \r, \t
    r"|\\u[0-9a-fA-F]{4}"                                  # Unicode escapes e.g. \u00A0
    r")"
)

# Common Unity asset extensions containing localized texts
UNITY_TEXT_EXTENSIONS = {
    ".assets",
    ".bundle",
    ".unity3d",
    ".resource",
    ".bytes",
    ".dat",
    ""
}

# Known vendor locations for UnityPy
VENDOR_PACKAGE_PATHS = [
    Path(r"E:\Mod_Workspace\Tool\python_packages"),
    Path(os.path.dirname(os.path.abspath(__file__))) / "vendor",
]


def load_unitypy() -> Any:
    """Safely loads UnityPy with automated discovery in workspace package paths."""
    try:
        import UnityPy
        return UnityPy
    except ImportError:
        pass

    for vendor_path in VENDOR_PACKAGE_PATHS:
        if vendor_path.exists() and str(vendor_path) not in sys.path:
            sys.path.insert(0, str(vendor_path))
            try:
                import UnityPy
                return UnityPy
            except ImportError:
                continue

    raise RuntimeError(
        "UnityPy is not installed in the Python environment or found in workspace paths. "
        f"Checked paths: {[str(p) for p in VENDOR_PACKAGE_PATHS]}"
    )


def sha256_bytes(data: bytes) -> str:
    """Calculate SHA-256 hash of bytes."""
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: str | Path) -> str:
    """Calculate SHA-256 hash of a file efficiently with chunking."""
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"File not found for hashing: {path}")
    hasher = hashlib.sha256()
    with p.open("rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def stable_key(file_path: str, path_id: int | str, selector: str) -> str:
    """Generates a deterministic, collision-resistant 16-char hex key.
    
    Formula: UNITY_{SHA1(file_path|path_id|selector)[:16].upper()}
    """
    clean_file = file_path.replace("\\", "/").strip().lower()
    raw = f"{clean_file}|{path_id}|{selector}"
    digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16].upper()
    return f"UNITY_{digest}"


def extract_protected_tokens(text: str) -> List[str]:
    """Extracts all format tokens, variable placeholders, and rich text tags."""
    if not text:
        return []
    normalized = text.replace("\r\n", r"\n").replace("\n", r"\n").replace("\t", r"\t")
    return PROTECTED_TOKEN_PATTERN.findall(normalized)


def validate_token_preservation(source: str, translation: str, key: str = "") -> Tuple[bool, str]:
    """Validates that translation preserves all protected tokens from source."""
    if not translation:
        return True, ""
    src_tokens = extract_protected_tokens(source)
    trans_tokens = extract_protected_tokens(translation)
    if src_tokens != trans_tokens:
        msg = f"Token mismatch in key '{key}': expected {src_tokens}, got {trans_tokens}"
        return False, msg
    return True, ""


def decode_text_safe(raw: bytes) -> Optional[Tuple[str, str]]:
    """Safely decodes raw bytes into text with detected encoding, skipping binary blobs."""
    if not raw or b"\x00\x00\x00" in raw[:16]:
        return None
    for enc in ("utf-8-sig", "utf-8", "utf-16", "utf-16-le", "utf-16-be"):
        try:
            val = raw.decode(enc)
        except UnicodeDecodeError:
            continue
        if not val:
            continue
        # Check printable character ratio to avoid binary false-positives
        printable_count = sum(ch.isprintable() or ch in "\r\n\t" for ch in val)
        if printable_count / len(val) >= 0.95:
            return val, enc
    return None


def read_tstudio_csv(path: str | Path) -> List[Dict[str, str]]:
    """Reads a standard TStudio CSV file into a list of row dicts."""
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"CSV file not found: {p}")
    
    csv.field_size_limit(2_147_483_647)
    with p.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError(f"CSV {p.name} is empty.")
        missing = set(CSV_COLUMNS) - set(reader.fieldnames)
        if missing:
            raise ValueError(f"CSV {p.name} is missing standard TStudio columns: {missing}")
        return list(reader)


def write_tstudio_csv(path: str | Path, rows: List[Dict[str, str]]) -> None:
    """Writes row dicts to a standard TStudio CSV file."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for r in rows:
            writer.writerow({col: r.get(col, "") for col in CSV_COLUMNS})


def pointer_escape(part: str) -> str:
    """Escapes JSON pointer token according to RFC 6901."""
    return part.replace("~", "~0").replace("/", "~1")


def pointer_unescape(part: str) -> str:
    """Unescapes RFC 6901 JSON pointer token."""
    return part.replace("~1", "/").replace("~0", "~")


def json_string_leaves(value: Any, pointer: str = "") -> Iterator[Tuple[str, str]]:
    """Yields (json_pointer, string_value) for every string leaf in a serialized object tree."""
    if isinstance(value, dict):
        for k, v in value.items():
            yield from json_string_leaves(v, f"{pointer}/{pointer_escape(str(k))}")
    elif isinstance(value, (list, tuple)):
        for idx, item in enumerate(value):
            yield from json_string_leaves(item, f"{pointer}/{idx}")
    elif isinstance(value, str):
        yield pointer or "/", value
