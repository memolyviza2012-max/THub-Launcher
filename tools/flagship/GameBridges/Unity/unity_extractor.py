"""High-Performance Unity Locale Scanner & Coverage Reporter.

Extracts localized English strings from Unity MonoBehaviour tables, TextAssets, and
serialized assets into standard TStudio CSV format. Prevents false-positive extraction
of French, German, Spanish, Portuguese, and other Latin languages by strictly enforcing
explicit locale field naming conventions and structural language slot detection.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Import shared engine utilities
try:
    from .unity_common import (
        CSV_COLUMNS,
        load_unitypy,
        stable_key,
        write_tstudio_csv,
        pointer_escape,
    )
except ImportError:
    from unity_common import (
        CSV_COLUMNS,
        load_unitypy,
        stable_key,
        write_tstudio_csv,
        pointer_escape,
    )

# Regular expressions for script validation
RE_LATIN = re.compile(r"[A-Za-z]")
RE_NON_ENGLISH_SCRIPT = re.compile(r"[\u3040-\u30ff\u3400-\u9fff\uac00-\ud7af\u0400-\u04ff\u0e00-\u0e7f]")
RE_HAN = re.compile(r"[\u3400-\u9fff]")
RE_KOREAN = re.compile(r"[\uac00-\ud7af]")

# Explicit English target field suffixes and names
DEFAULT_ENGLISH_FIELD_SUFFIXES = ("en", "english", "_en", "_english")
DEFAULT_ENGLISH_EXACT_FIELDS = {
    "m_stringen",
    "m_nameen",
    "m_commenten",
    "m_descen",
    "m_titleen",
    "m_detailen",
    "m_texten",
    "stringen",
    "nameen",
    "commenten",
    "descen",
    "titleen",
    "english",
}

# Non-English field suffixes to strictly reject (even if they contain Latin characters)
REJECT_FIELD_SUFFIXES = (
    "fr", "french", "_fr",
    "de", "german", "_de",
    "es", "spanish", "_es",
    "it", "italian", "_it",
    "pt", "portuguese", "_pt", "ptbr",
    "ru", "russian", "_ru",
    "ja", "jp", "japanese", "_ja", "_jp",
    "ko", "korean", "_ko",
    "zh", "cn", "tw", "chinese", "_zh", "_cn", "_tw"
)


class UnityExtractor:
    """Extracts localized text tables and produces coverage metrics from Unity assets."""

    def __init__(
        self,
        target_suffixes: Optional[Tuple[str, ...]] = None,
        target_exact_fields: Optional[Set[str]] = None,
        min_length: int = 1,
        include_text_assets: bool = True
    ):
        self.target_suffixes = tuple(s.lower() for s in (target_suffixes or DEFAULT_ENGLISH_FIELD_SUFFIXES))
        self.target_exact_fields = {f.lower() for f in (target_exact_fields or DEFAULT_ENGLISH_EXACT_FIELDS)}
        self.min_length = min_length
        self.include_text_assets = include_text_assets
        self.UnityPy = load_unitypy()

    def is_english_field(self, field_name: str) -> bool:
        """Determines if a field name explicitly denotes English localized text.
        
        Strictly rejects French, German, Spanish, Portuguese, Italian, and Asian fields.
        """
        fn_lower = field_name.lower().strip()
        
        # Check explicit reject suffixes first
        for reject in REJECT_FIELD_SUFFIXES:
            if fn_lower.endswith(reject):
                return False
            # Also check if wrapped in underscores e.g. text_fr_raw
            if f"_{reject}_" in fn_lower or f"_{reject}" in fn_lower:
                return False

        # Check exact field matches
        if fn_lower in self.target_exact_fields:
            return True

        # Check target English suffixes
        for suffix in self.target_suffixes:
            if fn_lower.endswith(suffix):
                return True

        return False

    def is_valid_english_text(self, text: str) -> bool:
        """Verifies text content has valid English letters and no foreign Asian/Cyrillic scripts."""
        if not text or len(text.strip()) < self.min_length:
            return False
        # Must contain at least one Latin letter or digit
        if not RE_LATIN.search(text) and not any(ch.isdigit() for ch in text):
            return False
        # Must not contain dominant non-English scripts (Japanese, Chinese, Korean, Thai, Russian)
        if RE_NON_ENGLISH_SCRIPT.search(text):
            return False
        return True

    def scan_monobehaviour_fields(
        self,
        data: Any,
        path_id: int,
        script_name: str,
        file_path: str,
        pointer: str = "",
        field_order_counter: Optional[List[int]] = None
    ) -> List[Dict[str, str]]:
        """Recursively scans a deserialized MonoBehaviour tree for English fields."""
        if field_order_counter is None:
            field_order_counter = [0]

        extracted: List[Dict[str, str]] = []

        if isinstance(data, dict):
            for k, v in data.items():
                child_ptr = f"{pointer}/{pointer_escape(str(k))}"
                if isinstance(v, str):
                    if self.is_english_field(k) and self.is_valid_english_text(v):
                        idx = field_order_counter[0]
                        field_order_counter[0] += 1
                        selector = child_ptr.lstrip("/")
                        key = stable_key(file_path, path_id, f"{selector}:{idx}")
                        context = f"MonoBehaviour: {script_name} | PathID: {path_id} | Field: {k} | Order: {idx} | Ptr: {selector}"
                        extracted.append({
                            "key": key,
                            "source": v,
                            "translation": "",
                            "context": context,
                            "file_path": file_path,
                            "_path_id": str(path_id),
                            "_order": idx,
                            "_field_name": k
                        })
                else:
                    extracted.extend(
                        self.scan_monobehaviour_fields(
                            v, path_id, script_name, file_path, child_ptr, field_order_counter
                        )
                    )
        elif isinstance(data, (list, tuple)):
            for idx, item in enumerate(data):
                child_ptr = f"{pointer}/{idx}"
                extracted.extend(
                    self.scan_monobehaviour_fields(
                        item, path_id, script_name, file_path, child_ptr, field_order_counter
                    )
                )

        return extracted

    def scan_asset_file(self, full_path: Path, relative_path: str) -> Tuple[List[Dict[str, str]], Dict[str, Any]]:
        """Parses a single Unity serialized asset or bundle and returns extracted rows + metadata."""
        env = self.UnityPy.load(str(full_path))
        extracted_rows: List[Dict[str, str]] = []
        
        table_coverage: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "path_id": "",
            "script_name": "",
            "type": "",
            "strings_count": 0,
            "unique_sources": set(),
            "sample_sources": []
        })

        for obj in env.objects:
            type_name = obj.type.name
            path_id = obj.path_id

            if type_name == "MonoBehaviour":
                try:
                    tree = obj.read_typetree()
                    if not tree or not isinstance(tree, dict):
                        continue
                except Exception:
                    # Typetree reading without type database can fail on some versions
                    continue

                # Determine MonoBehaviour script class name if available
                script_name = "MonoBehaviour"
                if "m_Script" in tree and isinstance(tree["m_Script"], dict):
                    script_ptr = tree["m_Script"].get("m_PathID")
                    if script_ptr and script_ptr in env.objects:
                        try:
                            script_obj = env.objects[script_ptr].read()
                            script_name = getattr(script_obj, "m_ClassName", getattr(script_obj, "m_Name", "MonoBehaviour"))
                        except Exception:
                            pass

                # Scan for English fields
                rows = self.scan_monobehaviour_fields(
                    data=tree,
                    path_id=path_id,
                    script_name=script_name,
                    file_path=relative_path
                )

                if rows:
                    extracted_rows.extend(rows)
                    t_info = table_coverage[str(path_id)]
                    t_info["path_id"] = str(path_id)
                    t_info["script_name"] = script_name
                    t_info["type"] = type_name
                    t_info["strings_count"] += len(rows)
                    for r in rows:
                        src = r["source"]
                        t_info["unique_sources"].add(src)
                        if len(t_info["sample_sources"]) < 5:
                            t_info["sample_sources"].append(src[:60])

            elif self.include_text_assets and type_name == "TextAsset":
                try:
                    text_obj = obj.read()
                    name = getattr(text_obj, "m_Name", f"TextAsset_{path_id}")
                    raw_bytes = bytes(getattr(text_obj, "m_Script", b""))
                    if not raw_bytes:
                        continue
                    
                    # Check if it's text
                    from .unity_common import decode_text_safe
                    decoded = decode_text_safe(raw_bytes)
                    if decoded:
                        text_val, enc = decoded
                        if self.is_valid_english_text(text_val) and not name.lower().endswith(REJECT_FIELD_SUFFIXES):
                            key = stable_key(relative_path, path_id, "text_content")
                            context = f"TextAsset: {name} | PathID: {path_id} | Encoding: {enc}"
                            extracted_rows.append({
                                "key": key,
                                "source": text_val,
                                "translation": "",
                                "context": context,
                                "file_path": relative_path,
                                "_path_id": str(path_id),
                                "_order": 0,
                                "_field_name": name
                            })
                            t_info = table_coverage[str(path_id)]
                            t_info["path_id"] = str(path_id)
                            t_info["script_name"] = name
                            t_info["type"] = type_name
                            t_info["strings_count"] += 1
                            t_info["unique_sources"].add(text_val)
                            t_info["sample_sources"].append(text_val[:60])
                except Exception:
                    continue

        # Format coverage metadata (converting sets to counts for JSON serialization)
        formatted_coverage = {}
        for pid, info in table_coverage.items():
            formatted_coverage[pid] = {
                "path_id": info["path_id"],
                "script_name": info["script_name"],
                "type": info["type"],
                "total_strings": info["strings_count"],
                "unique_strings": len(info["unique_sources"]),
                "sample_preview": info["sample_sources"]
            }

        return extracted_rows, formatted_coverage

    def scan_path(
        self,
        target_path: Path,
        recursive: bool = True
    ) -> Tuple[List[Dict[str, str]], Dict[str, Any]]:
        """Scans a directory or specific asset file, extracting rows and generating coverage metrics."""
        target_path = Path(target_path).resolve()
        all_rows: List[Dict[str, str]] = []
        coverage_manifest: Dict[str, Any] = {
            "scan_target": str(target_path),
            "files": {},
            "total_extracted_rows": 0,
            "total_tables": 0,
            "domains": defaultdict(int)
        }

        if target_path.is_file():
            files_to_scan = [(target_path, target_path.name)]
        elif target_path.is_dir():
            files_to_scan = []
            pattern = "**/*" if recursive else "*"
            for p in target_path.glob(pattern):
                if p.is_file():
                    ext = p.suffix.lower()
                    name = p.name.lower()
                    if ext in (".assets", ".bundle", ".unity3d", ".resource") or "level" in name or "resources" in name:
                        rel = str(p.relative_to(target_path)).replace("\\", "/")
                        files_to_scan.append((p, rel))
        else:
            raise FileNotFoundError(f"Target path does not exist: {target_path}")

        for file_p, rel_name in files_to_scan:
            try:
                rows, table_info = self.scan_asset_file(file_p, rel_name)
                if rows:
                    all_rows.extend(rows)
                    coverage_manifest["files"][rel_name] = {
                        "file_path": str(file_p),
                        "row_count": len(rows),
                        "tables": table_info
                    }
                    coverage_manifest["total_tables"] += len(table_info)

                    # Estimate domains based on script / file names
                    for t in table_info.values():
                        s_name = t["script_name"].lower()
                        if any(k in s_name for k in ("ui", "menu", "title", "hud", "dialog")):
                            coverage_manifest["domains"]["UI / Menus"] += t["total_strings"]
                        elif any(k in s_name for k in ("item", "weapon", "equip", "armor")):
                            coverage_manifest["domains"]["Items / Equipment"] += t["total_strings"]
                        elif any(k in s_name for k in ("skill", "magic", "ability", "talent")):
                            coverage_manifest["domains"]["Skills / Abilities"] += t["total_strings"]
                        elif any(k in s_name for k in ("quest", "mission", "scenario", "story")):
                            coverage_manifest["domains"]["Quests / Scenario"] += t["total_strings"]
                        else:
                            coverage_manifest["domains"]["System / Other"] += t["total_strings"]

            except Exception as exc:
                print(f"[UnityExtractor] Warning: Failed to scan {rel_name}: {exc}", file=sys.stderr)

        coverage_manifest["total_extracted_rows"] = len(all_rows)
        coverage_manifest["domains"] = dict(coverage_manifest["domains"])
        return all_rows, coverage_manifest


def generate_coverage_markdown(manifest: Dict[str, Any]) -> str:
    """Renders a clear human-readable Markdown coverage summary."""
    lines = [
        "# Unity Thai Localization: Asset Coverage Report",
        "",
        f"- **Scan Target**: `{manifest.get('scan_target', '')}`",
        f"- **Total Extracted English Rows**: `{manifest.get('total_extracted_rows', 0):,}`",
        f"- **Total Localized Tables (PathIDs)**: `{manifest.get('total_tables', 0):,}`",
        "",
        "## Domain Distribution",
        "",
        "| Domain | Total Extracted Strings |",
        "| :--- | :--- |"
    ]
    for domain, count in manifest.get("domains", {}).items():
        lines.append(f"| **{domain}** | {count:,} |")

    lines.extend([
        "",
        "## Localized Tables by Asset File",
        "",
        "| File | PathID | Table / Script | Strings | Unique | Sample English |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |"
    ])

    for file_rel, fdata in manifest.get("files", {}).items():
        for pid, tinfo in fdata.get("tables", {}).items():
            sample = tinfo.get("sample_preview", [""])[0] if tinfo.get("sample_preview") else ""
            clean_sample = sample.replace("\n", " ").replace("|", "\\|")[:45]
            lines.append(
                f"| `{file_rel}` | `{pid}` | `{tinfo.get('script_name', '')}` | "
                f"{tinfo.get('total_strings', 0)} | {tinfo.get('unique_strings', 0)} | \"{clean_sample}...\" |"
            )

    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract English localization tables from Unity assets into TStudio CSV.")
    parser.add_argument("input", type=Path, help="Input Unity asset file or *_Data directory")
    parser.add_argument("-o", "--output", type=Path, required=True, help="Output TStudio CSV file")
    parser.add_argument("--report", type=Path, help="Optional JSON coverage report output path")
    parser.add_argument("--report-md", type=Path, help="Optional Markdown coverage report output path")
    parser.add_argument("--min-len", type=int, default=1, help="Minimum string character length")
    args = parser.parse_args()

    extractor = UnityExtractor(min_length=args.min_len)
    print(f"[UnityExtractor] Scanning {args.input}...")
    rows, manifest = extractor.scan_path(args.input)

    # Clean rows to match exact TStudio 5-column CSV schema
    cleaned_rows = [
        {col: r.get(col, "") for col in CSV_COLUMNS}
        for r in rows
    ]

    write_tstudio_csv(args.output, cleaned_rows)
    print(f"[UnityExtractor] Successfully wrote {len(cleaned_rows):,} rows to {args.output}")

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[UnityExtractor] Saved coverage report JSON to {args.report}")

    if args.report_md:
        args.report_md.parent.mkdir(parents=True, exist_ok=True)
        args.report_md.write_text(generate_coverage_markdown(manifest), encoding="utf-8")
        print(f"[UnityExtractor] Saved coverage report Markdown to {args.report_md}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
