"""THub Universal Unity Thai Localization Engine.

Unified entry point and high-level workflow coordinator for Unity Thai localization mods.
Covers asset discovery, coverage reporting, TStudio CSV generation, TMP font preparation,
tone-mark tuning, queue-based native repacking, independent validation, and safe deployment.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from .unity_common import CSV_COLUMNS, read_tstudio_csv, write_tstudio_csv, sha256_file
    from .unity_extractor import UnityExtractor, generate_coverage_markdown
    from .unity_font_pipeline import ThaiFontMapper, UnityFontPipeline
    from .unity_native_packer import UnityNativePacker
    from .unity_native_validator import UnityNativeValidator
    from .unity_deployer import UnityDeployer
except ImportError:
    from unity_common import CSV_COLUMNS, read_tstudio_csv, write_tstudio_csv, sha256_file
    from unity_extractor import UnityExtractor, generate_coverage_markdown
    from unity_font_pipeline import ThaiFontMapper, UnityFontPipeline
    from unity_native_packer import UnityNativePacker
    from unity_native_validator import UnityNativeValidator
    from unity_deployer import UnityDeployer


class UnityThaiEngine:
    """Master workflow coordinator for Unity Thai Localization."""

    def __init__(
        self,
        mapping_path: Optional[Path | str] = None,
        unity_version: str = "2020.3.22f1",
        dummy_dlls_dir: Optional[Path | str] = None,
        session_log_path: Optional[Path | str] = None
    ):
        self.mapper = ThaiFontMapper(mapping_path)
        self.font_pipeline = UnityFontPipeline(self.mapper)
        self.extractor = UnityExtractor()
        self.packer = UnityNativePacker(self.mapper, unity_version, dummy_dlls_dir)
        self.validator = UnityNativeValidator(self.mapper)
        self.deployer = UnityDeployer(session_log_path)

    # 1. Extraction & Coverage Scanning
    def scan_and_extract(
        self,
        input_path: Path | str,
        output_csv: Path | str,
        report_json: Optional[Path | str] = None,
        report_md: Optional[Path | str] = None
    ) -> Dict[str, Any]:
        """Scans Unity assets, generates TStudio CSV, and reports coverage."""
        rows, manifest = self.extractor.scan_path(Path(input_path))
        cleaned = [{c: r.get(c, "") for c in CSV_COLUMNS} for r in rows]
        write_tstudio_csv(output_csv, cleaned)

        if report_json:
            import json
            p = Path(report_json)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

        if report_md:
            p = Path(report_md)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(generate_coverage_markdown(manifest), encoding="utf-8")

        return manifest

    # 2. Font Pipeline: Character Subset
    def build_charset(
        self,
        translated_csv: Path | str,
        output_charset: Path | str
    ) -> Tuple[str, Dict[str, int]]:
        """Generates ASCII + Thai PUA character set from translated CSV."""
        charset, stats = self.font_pipeline.build_character_subset(translated_csv)
        p = Path(output_charset)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(charset, encoding="utf-8", newline="")
        return charset, stats

    # 3. Font Pipeline: Tone Mark Tuning
    def tune_font(
        self,
        input_font: Path | str,
        output_font: Path | str,
        raise_units: int = 160
    ) -> Dict[str, Any]:
        """Elevates Thai tone mark components in PUA composite glyphs."""
        return UnityFontPipeline.tune_tone_marks(input_font, output_font, raise_units)

    # 4. Native Repacking
    def pack(
        self,
        input_asset: Path | str,
        output_asset: Path | str,
        csv_path: Path | str,
        target_fields: Optional[List[str]] = None,
        font_bundle: Optional[Path | str] = None,
        target_font_pathid: Optional[int] = None,
        target_material_pathid: Optional[int] = None,
        target_atlas_pathid: Optional[int] = None
    ) -> Dict[str, Any]:
        """Performs native repacking with queue-based context preservation."""
        return self.packer.pack_assets(
            input_asset=input_asset,
            output_asset=output_asset,
            csv_path=csv_path,
            target_fields=target_fields,
            font_bundle=font_bundle,
            target_font_pathid=target_font_pathid,
            target_material_pathid=target_material_pathid,
            target_atlas_pathid=target_atlas_pathid
        )

    # 5. Independent Validation
    def validate(
        self,
        original_asset: Path | str,
        packed_asset: Path | str,
        manifest_output: Optional[Path | str] = None
    ) -> Dict[str, Any]:
        """Performs independent read-back inspection and produces SHA-256 hash manifest."""
        return self.validator.validate_asset(
            original_asset=original_asset,
            packed_asset=packed_asset,
            manifest_output=manifest_output
        )

    # 6. Safe Deployment
    def deploy(
        self,
        packed_asset: Path | str,
        game_destination_file: Path | str,
        game_exe_names: Optional[List[str]] = None,
        backup_dir: Optional[Path | str] = None
    ) -> Dict[str, Any]:
        """Checks game process, ensures immutable backup, and deploys validated asset."""
        return self.deployer.deploy(
            packed_asset=packed_asset,
            game_destination_file=game_destination_file,
            game_exe_names=game_exe_names,
            backup_dir=backup_dir
        )

    # 7. Safe Rollback
    def rollback(
        self,
        game_destination_file: Path | str,
        backup_dir: Optional[Path | str] = None
    ) -> Dict[str, Any]:
        """Restores original asset from immutable backup."""
        return self.deployer.rollback(
            game_destination_file=game_destination_file,
            backup_dir=backup_dir
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="THub Unity Thai Localization Engine CLI.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Scan command
    p_scan = subparsers.add_parser("scan", help="Scan Unity assets & export TStudio CSV")
    p_scan.add_argument("input", type=Path, help="Input asset file or *_Data directory")
    p_scan.add_argument("-o", "--output", type=Path, required=True, help="Output TStudio CSV file")
    p_scan.add_argument("--report", type=Path, help="Optional JSON coverage report output")
    p_scan.add_argument("--report-md", type=Path, help="Optional Markdown coverage report output")

    # Subset command
    p_sub = subparsers.add_parser("subset", help="Build character set from translated CSV")
    p_sub.add_argument("csv", type=Path, help="Translated TStudio CSV file")
    p_sub.add_argument("-o", "--output", type=Path, required=True, help="Output charset.txt")

    # Tune-font command
    p_tune = subparsers.add_parser("tune-font", help="Raise Thai tone marks in TTF font")
    p_tune.add_argument("font", type=Path, help="Input TTF font file")
    p_tune.add_argument("-o", "--output", type=Path, required=True, help="Output shifted TTF font file")
    p_tune.add_argument("--raise-units", type=int, default=160, help="Vertical raise offset (default: 160)")

    # Pack command
    p_pack = subparsers.add_parser("pack", help="Repack Unity assets using AssetsTools")
    p_pack.add_argument("--input", required=True, type=Path, help="Input original asset file")
    p_pack.add_argument("--output", required=True, type=Path, help="Output packed asset file")
    p_pack.add_argument("--csv", required=True, type=Path, help="Translated TStudio CSV")
    p_pack.add_argument("--dummy-dlls", type=Path, help="DummyDll directory for MonoCecil")
    p_pack.add_argument("--unity-version", default="2020.3.22f1", help="Unity version")
    p_pack.add_argument("--font-bundle", type=Path, help="Optional TMP Font bundle")
    p_pack.add_argument("--target-font-pathid", type=int, help="Target FontAsset PathID")
    p_pack.add_argument("--target-material-pathid", type=int, help="Target Material PathID")
    p_pack.add_argument("--target-atlas-pathid", type=int, help="Target Atlas Texture2D PathID")

    # Validate command
    p_val = subparsers.add_parser("validate", help="Validate packed asset and generate hash manifest")
    p_val.add_argument("--original", required=True, type=Path, help="Original asset file")
    p_val.add_argument("--packed", required=True, type=Path, help="Packed asset file")
    p_val.add_argument("--manifest", type=Path, help="Output hash_manifest.json")

    # Deploy command
    p_dep = subparsers.add_parser("deploy", help="Deploy packed asset to game directory safely")
    p_dep.add_argument("--packed", required=True, type=Path, help="Validated packed asset file")
    p_dep.add_argument("--destination", required=True, type=Path, help="Target file in game directory")
    p_dep.add_argument("--game-exe", action="append", help="Game executable name(s) to verify closed")
    p_dep.add_argument("--backup-dir", type=Path, help="Custom immutable backup directory")

    # Rollback command
    p_roll = subparsers.add_parser("rollback", help="Restore original asset from immutable backup")
    p_roll.add_argument("--destination", required=True, type=Path, help="Target file in game directory")
    p_roll.add_argument("--backup-dir", type=Path, help="Custom immutable backup directory")

    args = parser.parse_args()

    engine = UnityThaiEngine(
        dummy_dlls_dir=getattr(args, "dummy_dlls", None),
        unity_version=getattr(args, "unity_version", "2020.3.22f1")
    )

    if args.command == "scan":
        manifest = engine.scan_and_extract(args.input, args.output, args.report, args.report_md)
        print(f"[UnityThaiEngine] Extracted {manifest['total_extracted_rows']:,} rows across {manifest['total_tables']} table(s).")

    elif args.command == "subset":
        _, stats = engine.build_charset(args.csv, args.output)
        print(f"[UnityThaiEngine] Generated charset: {stats['unique_characters']} unique chars (PUA: {stats['pua_characters']}).")

    elif args.command == "tune-font":
        res = engine.tune_font(args.font, args.output, args.raise_units)
        print(f"[UnityThaiEngine] Tuned tone marks: {res['changed_pua_glyphs']} PUA composite glyphs updated.")

    elif args.command == "pack":
        res = engine.pack(
            input_asset=args.input,
            output_asset=args.output,
            csv_path=args.csv,
            font_bundle=args.font_bundle,
            target_font_pathid=args.target_font_pathid,
            target_material_pathid=args.target_material_pathid,
            target_atlas_pathid=args.target_atlas_pathid
        )
        print(f"[UnityThaiEngine] Native pack completed: {res['output_asset']}")

    elif args.command == "validate":
        res = engine.validate(args.original, args.packed, args.manifest)
        print(f"[UnityThaiEngine] Validation result: {res['validation']['status']} ({res['validation']['total_pua_strings_confirmed']} PUA strings verified).")

    elif args.command == "deploy":
        res = engine.deploy(args.packed, args.destination, args.game_exe, args.backup_dir)
        print(f"[UnityThaiEngine] Deployed successfully to: {res['target_file']}")

    elif args.command == "rollback":
        res = engine.rollback(args.destination, args.backup_dir)
        print(f"[UnityThaiEngine] Rollback completed for: {res['target_file']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
