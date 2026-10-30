"""Unity Native Asset Validator & Cryptographic Hash Manifest Generator.

Performs independent read-back inspection on packed Unity assets to confirm re-readability,
verifies presence of mapped Thai/PUA characters in target PathIDs, and produces
reproducible SHA-256 before/after hash manifests.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

try:
    from .unity_common import load_unitypy, sha256_file
    from .unity_font_pipeline import ThaiFontMapper
except ImportError:
    from unity_common import load_unitypy, sha256_file
    from unity_font_pipeline import ThaiFontMapper


class UnityNativeValidator:
    """Validates packed asset integrity and checks for valid PUA/Thai string insertion."""

    def __init__(self, mapper: Optional[ThaiFontMapper] = None):
        self.mapper = mapper or ThaiFontMapper()
        self.UnityPy = load_unitypy()

    def validate_asset(
        self,
        original_asset: Path | str,
        packed_asset: Path | str,
        target_path_ids: Optional[List[int | str]] = None,
        manifest_output: Optional[Path | str] = None
    ) -> Dict[str, Any]:
        """Performs full integrity check on packed asset against original."""
        orig_p = Path(original_asset).resolve()
        pack_p = Path(packed_asset).resolve()

        if not orig_p.is_file():
            raise FileNotFoundError(f"Original asset not found: {orig_p}")
        if not pack_p.is_file():
            raise FileNotFoundError(f"Packed asset not found: {pack_p}")

        orig_hash = sha256_file(orig_p)
        pack_hash = sha256_file(pack_p)
        orig_size = orig_p.stat().st_size
        pack_size = pack_p.stat().st_size

        if orig_hash == pack_hash:
            print("[UnityNativeValidator] Warning: Packed file has identical hash to original file (no changes made).")

        # Independent Read-back test via UnityPy
        print(f"[UnityNativeValidator] Loading packed asset: {pack_p.name} ...")
        try:
            env = self.UnityPy.load(str(pack_p))
            objects_by_path_id = {obj.path_id: obj for obj in env.objects}
        except Exception as exc:
            raise RuntimeError(f"Packed asset failed read-back inspection: {exc}") from exc

        print(f"[UnityNativeValidator] Successfully read-back {len(objects_by_path_id):,} objects.")

        verified_tables: Dict[str, Dict[str, Any]] = {}
        total_pua_strings_found = 0
        pua_samples: List[str] = []

        # Convert target_path_ids to ints if provided
        pids_to_check = [int(p) for p in (target_path_ids or [])]
        if not pids_to_check:
            # Check all MonoBehaviours
            pids_to_check = [
                obj.path_id for obj in env.objects
                if obj.type.name in ("MonoBehaviour", "TextAsset")
            ]

        for pid in pids_to_check:
            if pid not in objects_by_path_id:
                continue

            obj = objects_by_path_id[pid]
            strings_in_table = []
            pua_in_table = []

            try:
                tree = obj.read_typetree()
                if isinstance(tree, dict):
                    strings_in_table = self._extract_all_strings(tree)
            except Exception:
                # If typetree read fails, check raw data
                raw = obj.get_raw_data()
                # Check for PUA UTF-8 bytes (PUA 0xF000-0xF8FF is 3-byte UTF-8: \xEF\x80\x80 .. \xEF\xA2\xBF)
                if b"\xef\x80" in raw or b"\xef\x81" in raw or b"\xef\x82" in raw:
                    pua_in_table.append(f"<Found PUA byte sequences in raw binary, length {len(raw)}>")

            for s in strings_in_table:
                # Check if string contains PUA characters
                if any(0xF000 <= ord(c) <= 0xF8FF for c in s):
                    pua_in_table.append(s)
                    if len(pua_samples) < 10:
                        # Decode sample to readable Thai for manifest preview
                        decoded = self.mapper.decode_text(s)
                        pua_samples.append(decoded[:60])

            if pua_in_table:
                total_pua_strings_found += len(pua_in_table)
                verified_tables[str(pid)] = {
                    "path_id": pid,
                    "type": obj.type.name,
                    "pua_string_count": len(pua_in_table),
                    "sample": pua_in_table[0][:50]
                }

        is_valid = total_pua_strings_found > 0 or len(pids_to_check) == 0

        manifest = {
            "schema": "thub-unity-native-manifest/v1",
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "original_asset": {
                "file_name": orig_p.name,
                "path": str(orig_p),
                "sha256": orig_hash,
                "size_bytes": orig_size
            },
            "packed_asset": {
                "file_name": pack_p.name,
                "path": str(pack_p),
                "sha256": pack_hash,
                "size_bytes": pack_size
            },
            "validation": {
                "readable": True,
                "total_objects_indexed": len(objects_by_path_id),
                "verified_tables_count": len(verified_tables),
                "total_pua_strings_confirmed": total_pua_strings_found,
                "status": "PASS" if is_valid else "WARNING",
                "sample_decoded_texts": pua_samples
            },
            "tables": verified_tables
        }

        if manifest_output:
            out_p = Path(manifest_output).resolve()
            out_p.parent.mkdir(parents=True, exist_ok=True)
            out_p.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"[UnityNativeValidator] Saved Before/After Hash Manifest to: {out_p}")

        return manifest

    def _extract_all_strings(self, data: Any) -> List[str]:
        """Recursively extracts all string values from deserialized typetree dictionary."""
        results = []
        if isinstance(data, dict):
            for v in data.values():
                results.extend(self._extract_all_strings(v))
        elif isinstance(data, (list, tuple)):
            for item in data:
                results.extend(self._extract_all_strings(item))
        elif isinstance(data, str):
            results.append(data)
        return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate packed Unity assets and generate SHA-256 hash manifest.")
    parser.add_argument("--original", required=True, type=Path, help="Path to original asset file")
    parser.add_argument("--packed", required=True, type=Path, help="Path to packed asset file")
    parser.add_argument("--manifest", type=Path, help="Path to save output hash_manifest.json")
    parser.add_argument("--pathids", help="Comma-separated PathIDs to inspect (optional)")
    args = parser.parse_args()

    validator = UnityNativeValidator()
    pids = [p.strip() for p in args.pathids.split(",")] if args.pathids else None

    report = validator.validate_asset(
        original_asset=args.original,
        packed_asset=args.packed,
        target_path_ids=pids,
        manifest_output=args.manifest
    )

    print(f"\n--- Validation Summary ---")
    print(f"Status: {report['validation']['status']}")
    print(f"Original SHA-256: {report['original_asset']['sha256']}")
    print(f"Packed SHA-256:   {report['packed_asset']['sha256']}")
    print(f"PUA Strings Confirmed: {report['validation']['total_pua_strings_confirmed']}")
    return 0 if report['validation']['status'] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
