"""Core Unreal Engine 3 / UDK common utilities for THub.

Provides:
- Dynamic UDK installation detection across config, environment, shortcuts, and disk.
- UE3 package binary header analysis (FileVersion, LicenseeVersion, endianness, Stock UDK compatibility).
- Safe path resolution and workspace boundary validation.
- Running UDK process monitoring.
"""

from __future__ import annotations

import csv
import io
import json
import os
import re
import struct
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# Common UDK executables and folder patterns
UE3_PACKAGE_MAGIC_LE = 0x9E2A83C1  # Little-Endian: C1 83 2A 9E
UE3_PACKAGE_MAGIC_BE = 0xC1832A9E  # Big-Endian: 9E 2A 83 C1
VALID_PACKAGE_EXTENSIONS = {".upk", ".u", ".udk"}


def _hidden_flags() -> int:
    """Return creation flags to hide child process windows on Windows."""
    return getattr(subprocess, "CREATE_NO_WINDOW", 0)


def find_udk_installation(
    custom_root: Optional[Union[str, Path]] = None,
    config_path: Optional[Union[str, Path]] = None
) -> Dict[str, Any]:
    """Dynamically discover installed UDK (Unreal Development Kit).
    
    Search order:
    1. Explicit custom_root parameter
    2. Environment variables (UDK_ROOT, UDK_EXE)
    3. THub configuration (hub_config.json)
    4. Start Menu shortcuts
    5. Standard drive roots (C:\\UDK, D:\\UDK, E:\\UDK, Program Files)
    """
    candidates: List[Tuple[Path, str]] = []

    # 1. Custom root
    if custom_root:
        p = Path(custom_root).resolve()
        if p.exists():
            candidates.append((p, "parameter"))

    # 2. Environment variables
    env_exe = os.environ.get("UDK_EXE")
    if env_exe:
        pe = Path(env_exe).resolve()
        if pe.is_file():
            root = pe.parents[2] if len(pe.parents) >= 3 else pe.parent
            candidates.append((root, "env_udk_exe"))

    env_root = os.environ.get("UDK_ROOT")
    if env_root:
        pr = Path(env_root).resolve()
        if pr.is_dir():
            candidates.append((pr, "env_udk_root"))

    # 3. THub configuration
    cfg_file = Path(config_path) if config_path else Path(__file__).resolve().parents[4] / "hub_config.json"
    if cfg_file.is_file():
        try:
            with cfg_file.open("r", encoding="utf-8") as f:
                cfg_data = json.load(f)
            cfg_udk = cfg_data.get("tools", {}).get("udk_path") or cfg_data.get("udk_root")
            if cfg_udk:
                p_cfg = Path(cfg_udk).resolve()
                if p_cfg.exists():
                    candidates.append((p_cfg, "hub_config"))
        except Exception:
            pass

    # 4. Start Menu shortcuts
    start_menu_roots = [
        Path(os.environ.get("ProgramData", r"C:\ProgramData")) / r"Microsoft\Windows\Start Menu\Programs\Unreal Development Kit",
        Path(os.environ.get("APPDATA", r"C:\Users\Default\AppData\Roaming")) / r"Microsoft\Windows\Start Menu\Programs\Unreal Development Kit",
    ]
    for sm_root in start_menu_roots:
        if sm_root.is_dir():
            for folder in sm_root.glob("UDK*"):
                if folder.is_dir():
                    folder_name = folder.name
                    for drive in ("C", "D", "E"):
                        target_cand = Path(f"{drive}:\\UDK") / folder_name
                        if target_cand.is_dir():
                            candidates.append((target_cand, f"shortcut_{folder_name}"))

    # 5. Standard drive roots
    for drive in ("C", "D", "E"):
        drive_udk = Path(f"{drive}:\\UDK")
        if drive_udk.is_dir():
            for sub in sorted(drive_udk.glob("UDK*"), reverse=True):
                if sub.is_dir():
                    candidates.append((sub, "drive_scan"))

    # Check candidates
    for root_cand, source in candidates:
        if root_cand.is_file() and root_cand.name.casefold() == "udk.exe":
            exe_path = root_cand
            actual_root = exe_path.parents[2] if len(exe_path.parents) >= 3 else exe_path.parent
            version = _extract_udk_version(actual_root)
            arch = "Win64" if "win64" in str(exe_path).casefold() else "Win32"
            return {
                "installed": True,
                "udk_root": str(actual_root),
                "udk_exe": str(exe_path),
                "udk_version": version,
                "arch": arch,
                "discovery_source": source,
                "error": None,
            }

        exe_64 = root_cand / "Binaries" / "Win64" / "UDK.exe"
        if exe_64.is_file():
            version = _extract_udk_version(root_cand)
            return {
                "installed": True,
                "udk_root": str(root_cand),
                "udk_exe": str(exe_64),
                "udk_version": version,
                "arch": "Win64",
                "discovery_source": source,
                "error": None,
            }

        exe_32 = root_cand / "Binaries" / "Win32" / "UDK.exe"
        if exe_32.is_file():
            version = _extract_udk_version(root_cand)
            return {
                "installed": True,
                "udk_root": str(root_cand),
                "udk_exe": str(exe_32),
                "udk_version": version,
                "arch": "Win32",
                "discovery_source": source,
                "error": None,
            }

    return {
        "installed": False,
        "udk_root": None,
        "udk_exe": None,
        "udk_version": "Unknown",
        "arch": None,
        "discovery_source": "none",
        "error": "No verified UDK installation found on this system.",
    }


def _extract_udk_version(root: Path) -> str:
    """Extract version tag from folder name or UDK build properties."""
    folder_match = re.search(r"UDK-(\d{4}-\d{2})", root.name, re.IGNORECASE)
    if folder_match:
        return folder_match.group(1)

    build_prop = root / "UDKGame" / "Build" / "Build.properties"
    if build_prop.is_file():
        try:
            content = build_prop.read_text(encoding="utf-8", errors="ignore")
            m = re.search(r"BuildDate\s*=\s*(\d{4}-\d{2})", content)
            if m:
                return m.group(1)
        except Exception:
            pass

    return root.name


def inspect_ue3_package_header(file_path: Union[str, Path]) -> Dict[str, Any]:
    """Inspect Unreal Engine 3 package binary header without loading the package."""
    path = Path(file_path).resolve()
    if not path.is_file():
        return {
            "ok": False,
            "error": f"File does not exist: {path}",
            "file_path": str(path),
        }

    try:
        with path.open("rb") as f:
            header_bytes = f.read(64)
    except Exception as exc:
        return {
            "ok": False,
            "error": f"Failed to read file header: {exc}",
            "file_path": str(path),
        }

    if len(header_bytes) < 8:
        return {
            "ok": False,
            "error": "File is too small to contain a valid UE3 package header.",
            "file_path": str(path),
        }

    magic_le, = struct.unpack_from("<I", header_bytes, 0)
    magic_be, = struct.unpack_from(">I", header_bytes, 0)

    if magic_le == UE3_PACKAGE_MAGIC_LE:
        endianness = "little"
        file_version, licensee_version = struct.unpack_from("<HH", header_bytes, 4)
    elif magic_be == UE3_PACKAGE_MAGIC_LE:
        endianness = "big"
        file_version, licensee_version = struct.unpack_from(">HH", header_bytes, 4)
    else:
        return {
            "ok": False,
            "error": f"Invalid package magic: {hex(magic_le)} (expected {hex(UE3_PACKAGE_MAGIC_LE)}). Not a valid UE3 package.",
            "file_path": str(path),
            "endianness": "unknown",
            "is_ue3": False,
        }

    is_stock_compatible = (licensee_version == 0) and (endianness == "little")

    if is_stock_compatible:
        verdict = "COMPATIBLE: Stock UDK can inspect and load this package (Licensee Version 0)."
        caution = None
    elif licensee_version == 30:
        verdict = "INCOMPATIBLE: Dishonored custom package format (Licensee Version 30)."
        caution = (
            "Stock UDK expects Licensee Version 0. Loading this package directly in Stock UDK "
            "PkgInfo or Editor will fail. Use game-specific unpacker (e.g. dishonored-toolkit) "
            "for extraction and repacking."
        )
    else:
        verdict = f"INCOMPATIBLE: Custom engine licensee package (Licensee Version {licensee_version})."
        caution = (
            f"Stock UDK expects Licensee Version 0, but this package uses Licensee Version {licensee_version}. "
            "Direct Stock UDK PkgInfo or Editor loading is not supported."
        )

    file_size = path.stat().st_size

    return {
        "ok": True,
        "file_name": path.name,
        "file_path": str(path),
        "file_size": file_size,
        "is_ue3": True,
        "endianness": endianness,
        "file_version": file_version,
        "licensee_version": licensee_version,
        "compatible_with_stock_udk": is_stock_compatible,
        "verdict": verdict,
        "caution": caution,
    }


def validate_package_path(raw_path: Union[str, Path], allowed_roots: List[Union[str, Path]]) -> Path:
    """Validate that package path exists, is a valid UE3 extension, and lies strictly within allowed roots."""
    try:
        resolved = Path(raw_path).resolve(strict=True)
    except FileNotFoundError:
        raise ValueError(f"Package file not found: {raw_path}")
    except Exception as exc:
        raise ValueError(f"Invalid package path '{raw_path}': {exc}")

    if not resolved.is_file():
        raise ValueError(f"Package path is not a file: {resolved}")

    if resolved.suffix.lower() not in VALID_PACKAGE_EXTENSIONS:
        raise ValueError(
            f"Invalid package extension '{resolved.suffix}'. Expected one of {sorted(VALID_PACKAGE_EXTENSIONS)}"
        )

    normalized_roots = [Path(root).resolve() for root in allowed_roots if root]
    if not any(resolved.is_relative_to(root) for root in normalized_roots):
        raise ValueError(
            f"Access denied: Package path '{resolved}' is outside allowed workspace/UDK roots: "
            f"{[str(r) for r in normalized_roots]}"
        )

    return resolved


def get_running_udk_processes(udk_exe: Optional[Union[str, Path]] = None) -> List[Dict[str, Any]]:
    """Scan running processes for UDK.exe instances."""
    if os.name != "nt":
        return []

    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq UDK.exe", "/FO", "CSV", "/NH"],
            capture_output=True,
            text=True,
            errors="replace",
            timeout=10,
            creationflags=_hidden_flags(),
            check=False,
        )
        if result.returncode != 0:
            return []

        rows = csv.reader(io.StringIO(result.stdout))
        processes = []
        for row in rows:
            if len(row) >= 2 and row[0].casefold() == "udk.exe" and row[1].isdigit():
                pid = int(row[1])
                processes.append({"image": row[0], "pid": pid})
        return processes
    except Exception:
        return []
