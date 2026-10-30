"""Unity Native Asset Packing Engine with Queue-Based Context Preservation.

Prepares and executes native serialized asset repacking for Unity IL2CPP and Mono games.
Maintains serialized queue ordering per PathID so identical English source strings receive
their appropriate contextual Thai translations without collision.
Leverages AssetsTools.NET NativeAssetPacker to replace MonoBehaviour records and TMP FontAssets
without corrupting engine allocator tables or memory alignments.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from .unity_common import CSV_COLUMNS, read_tstudio_csv, sha256_file
    from .unity_font_pipeline import ThaiFontMapper
except ImportError:
    from unity_common import CSV_COLUMNS, read_tstudio_csv, sha256_file
    from unity_font_pipeline import ThaiFontMapper

# Path to NativeAssetPacker compiled executable
NATIVE_PACKER_DIR = Path(__file__).resolve().parent / "AssetsToolsBridge" / "bin" / "Release" / "net6.0"
NATIVE_PACKER_EXE = NATIVE_PACKER_DIR / "NativeAssetPacker.exe"
NATIVE_PACKER_DLL = NATIVE_PACKER_DIR / "NativeAssetPacker.dll"
PORTABLE_DOTNET = Path(r"E:\Mod_Workspace\Tool\dotnet-sdk-6.0.428\dotnet.exe")


class UnityNativePacker:
    """Orchestrates asset repacking with PUA conversion and queue-based context preservation."""

    def __init__(
        self,
        mapper: Optional[ThaiFontMapper] = None,
        unity_version: str = "2020.3.22f1",
        dummy_dlls_dir: Optional[Path | str] = None
    ):
        self.mapper = mapper or ThaiFontMapper()
        self.unity_version = unity_version
        self.dummy_dlls_dir = Path(dummy_dlls_dir) if dummy_dlls_dir else None

    def build_translation_queues_from_csv(
        self,
        csv_path: Path | str,
        filter_file_path: Optional[str] = None
    ) -> Dict[str, List[Dict[str, str]]]:
        """Reads translated TStudio CSV and groups translations by PathID into ordered queues."""
        rows = read_tstudio_csv(csv_path)
        tables: Dict[str, List[Dict[str, str]]] = defaultdict(list)

        for row in rows:
            f_path = row.get("file_path", "").strip()
            if filter_file_path:
                norm_filter = filter_file_path.replace("\\", "/").lower()
                norm_row_file = f_path.replace("\\", "/").lower()
                if norm_filter not in norm_row_file and Path(norm_filter).name != Path(norm_row_file).name:
                    continue

            source = row.get("source", "")
            translation = (row.get("translation") or "").strip()
            context = row.get("context", "")
            key = row.get("key", "")

            # If translation is empty, skip packing so original source is preserved
            if not translation or not source:
                continue

            # Extract PathID from context
            path_id = self._extract_path_id(context)
            if not path_id:
                continue

            # Apply Thai PUA mapping
            pua_translation = self.mapper.map_text(translation)

            tables[path_id].append({
                "key": key,
                "source": source,
                "translation": pua_translation,
                "context": context
            })

        return dict(tables)

    @staticmethod
    def _extract_path_id(context: str) -> Optional[str]:
        """Extracts PathID from context string (e.g. 'PathID: 2751')."""
        if "PathID:" in context:
            parts = context.split("PathID:", 1)[1].strip().split()
            if parts:
                return parts[0].strip("|,; ")
        return None

    def pack_assets(
        self,
        input_asset: Path | str,
        output_asset: Path | str,
        translation_map_json: Optional[Path | str] = None,
        csv_path: Optional[Path | str] = None,
        target_fields: Optional[List[str]] = None,
        font_bundle: Optional[Path | str] = None,
        target_font_pathid: Optional[int] = None,
        target_material_pathid: Optional[int] = None,
        target_atlas_pathid: Optional[int] = None,
        force: bool = True
    ) -> Dict[str, Any]:
        """Runs NativeAssetPacker using AssetsTools.NET to pack translations safely."""
        input_asset = Path(input_asset).resolve()
        output_asset = Path(output_asset).resolve()

        if not input_asset.is_file():
            raise FileNotFoundError(f"Input asset file does not exist: {input_asset}")

        # Prepare translation JSON if CSV is provided
        temp_json_created = False
        if csv_path and not translation_map_json:
            queues = self.build_translation_queues_from_csv(csv_path, filter_file_path=input_asset.name)
            if not queues:
                # Try without file filter if empty
                queues = self.build_translation_queues_from_csv(csv_path)

            if not queues:
                raise ValueError(f"No valid translated rows found in {csv_path} with PathID context.")

            temp_json_path = output_asset.parent / f"_temp_pack_map_{input_asset.name}.json"
            temp_json_path.parent.mkdir(parents=True, exist_ok=True)
            temp_json_path.write_text(json.dumps({"tables": queues}, ensure_ascii=False, indent=2), encoding="utf-8")
            translation_map_json = temp_json_path
            temp_json_created = True

        translation_map_json = Path(translation_map_json).resolve()

        # Build runner command
        cmd: List[str] = []
        if NATIVE_PACKER_EXE.is_file():
            cmd = [str(NATIVE_PACKER_EXE)]
        elif NATIVE_PACKER_DLL.is_file() and PORTABLE_DOTNET.is_file():
            cmd = [str(PORTABLE_DOTNET), str(NATIVE_PACKER_DLL)]
        elif NATIVE_PACKER_DLL.is_file():
            cmd = ["dotnet", str(NATIVE_PACKER_DLL)]
        else:
            raise FileNotFoundError(
                f"NativeAssetPacker executable not found at: {NATIVE_PACKER_EXE}"
            )

        cmd.extend([
            "--input", str(input_asset),
            "--output", str(output_asset),
            "--translations", str(translation_map_json),
            "--unity-version", self.unity_version,
        ])

        if self.dummy_dlls_dir and self.dummy_dlls_dir.is_dir():
            cmd.extend(["--dummy-dlls", str(self.dummy_dlls_dir)])

        if target_fields:
            cmd.extend(["--target-fields", ",".join(target_fields)])

        if font_bundle:
            f_bundle_p = Path(font_bundle).resolve()
            if f_bundle_p.is_file() and target_font_pathid and target_material_pathid and target_atlas_pathid:
                cmd.extend([
                    "--font-bundle", str(f_bundle_p),
                    "--target-font-pathid", str(target_font_pathid),
                    "--target-material-pathid", str(target_material_pathid),
                    "--target-atlas-pathid", str(target_atlas_pathid)
                ])

        if force:
            cmd.append("--force")

        print(f"[UnityNativePacker] Executing repacker: {' '.join(cmd[:4])} ...")
        proc = subprocess.run(cmd, capture_output=True, text=True)

        # Clean up temp JSON
        if temp_json_created and translation_map_json.is_file():
            try:
                translation_map_json.unlink()
            except Exception:
                pass

        if proc.returncode != 0:
            err_msg = proc.stderr.strip() or proc.stdout.strip()
            raise RuntimeError(f"Native repacker failed (code {proc.returncode}): {err_msg}")

        print(proc.stdout.strip())

        return {
            "success": True,
            "input_asset": str(input_asset),
            "output_asset": str(output_asset),
            "input_hash": sha256_file(input_asset),
            "output_hash": sha256_file(output_asset),
            "log": proc.stdout.strip()
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="Unity Native Serialized Asset Repacker.")
    parser.add_argument("--input", required=True, type=Path, help="Input original .assets / level file")
    parser.add_argument("--output", required=True, type=Path, help="Output packed .assets file")
    parser.add_argument("--csv", type=Path, help="Translated TStudio CSV file")
    parser.add_argument("--translations", type=Path, help="Direct translation mapping JSON file")
    parser.add_argument("--dummy-dlls", type=Path, help="Directory containing DummyDlls (for MonoCecil)")
    parser.add_argument("--unity-version", default="2020.3.22f1", help="Unity version (default: 2020.3.22f1)")
    parser.add_argument("--target-fields", help="Comma-separated target fields e.g. EN,m_StringEN")
    parser.add_argument("--font-bundle", type=Path, help="Optional TMP Font AssetBundle to transplant")
    parser.add_argument("--target-font-pathid", type=int, help="Target FontAsset PathID")
    parser.add_argument("--target-material-pathid", type=int, help="Target Material PathID")
    parser.add_argument("--target-atlas-pathid", type=int, help="Target Atlas Texture2D PathID")
    parser.add_argument("--force", action="store_true", help="Force overwrite output")
    args = parser.parse_args()

    packer = UnityNativePacker(
        unity_version=args.unity_version,
        dummy_dlls_dir=args.dummy_dlls
    )

    t_fields = args.target_fields.split(",") if args.target_fields else None

    result = packer.pack_assets(
        input_asset=args.input,
        output_asset=args.output,
        translation_map_json=args.translations,
        csv_path=args.csv,
        target_fields=t_fields,
        font_bundle=args.font_bundle,
        target_font_pathid=args.target_font_pathid,
        target_material_pathid=args.target_material_pathid,
        target_atlas_pathid=args.target_atlas_pathid,
        force=args.force
    )

    print(f"[UnityNativePacker] Output Hash (SHA-256): {result['output_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
