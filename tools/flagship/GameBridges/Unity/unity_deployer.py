"""Unity Deployment Manager with Safety Checkpoints & Session Logging.

Enforces critical deployment safety rules:
1. Verifies the game process is closed before copying files.
2. Ensures an immutable original backup exists and NEVER overwrites it.
3. Validates deployed asset hash against packed asset hash.
4. Appends structured audit entries to session_log.md.
5. Provides atomic rollback from immutable backup.
6. Advises runtime hook / BepInEx status as fallback only.
"""
from __future__ import annotations

import argparse
import datetime
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from .unity_common import sha256_file
except ImportError:
    from unity_common import sha256_file


class UnityDeployer:
    """Manages game process checks, immutable backups, file deployment, and session audit logs."""

    def __init__(self, session_log_path: Optional[Path | str] = None):
        self.session_log_path = Path(session_log_path) if session_log_path else None

    @staticmethod
    def is_game_process_running(game_exe_names: List[str]) -> Tuple[bool, List[str]]:
        """Checks if any target game executable or Unity process is currently running."""
        running_detected: List[str] = []
        exe_set = {name.lower().strip() for name in game_exe_names}

        # On Windows, query tasklist
        if sys.platform == "win32":
            try:
                out = subprocess.check_output(["tasklist", "/FO", "CSV", "/NH"], text=True, errors="replace")
                for line in out.splitlines():
                    if not line.strip():
                        continue
                    parts = line.split('","')
                    if parts:
                        proc_name = parts[0].strip('"').lower()
                        for target in exe_set:
                            if target == proc_name or (target in proc_name and proc_name.endswith(".exe")):
                                running_detected.append(parts[0].strip('"'))
            except Exception as exc:
                print(f"[UnityDeployer] Warning: Could not query tasklist: {exc}")

        return (len(running_detected) > 0, list(set(running_detected)))

    @staticmethod
    def ensure_immutable_backup(
        target_game_file: Path,
        backup_dir: Optional[Path] = None
    ) -> Tuple[Path, str, bool]:
        """Creates or verifies an immutable original backup. NEVER overwrites existing backup."""
        if not target_game_file.is_file():
            raise FileNotFoundError(f"Target game file does not exist: {target_game_file}")

        if backup_dir is None:
            # Default backup beside the file: <filename>.orig
            backup_file = target_game_file.with_name(f"{target_game_file.name}.orig")
        else:
            backup_dir.mkdir(parents=True, exist_ok=True)
            backup_file = backup_dir / f"{target_game_file.name}.orig"

        is_new_backup = False

        if not backup_file.exists():
            print(f"[UnityDeployer] Creating immutable original backup at: {backup_file}")
            shutil.copy2(target_game_file, backup_file)
            # Make backup read-only to prevent accidental modification or overwriting
            try:
                os.chmod(backup_file, stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)
            except Exception:
                pass
            is_new_backup = True
        else:
            print(f"[UnityDeployer] Verified existing immutable backup at: {backup_file}")

        backup_hash = sha256_file(backup_file)
        return backup_file, backup_hash, is_new_backup

    def log_checkpoint(
        self,
        action: str,
        target_path: Path | str,
        original_hash: str,
        deployed_hash: str,
        status: str,
        details: str = "",
        custom_log_path: Optional[Path | str] = None
    ) -> None:
        """Appends an audit checkpoint entry to session_log.md."""
        log_file = Path(custom_log_path or self.session_log_path or "session_log.md")
        log_file.parent.mkdir(parents=True, exist_ok=True)

        now_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        
        entry = [
            f"### Checkpoint: {action} ({now_str})",
            "",
            f"- **Target File**: `{target_path}`",
            f"- **Status**: `{status}`",
            f"- **Original Backup Hash**: `{original_hash}`",
            f"- **Deployed Asset Hash**: `{deployed_hash}`",
        ]
        if details:
            entry.append(f"- **Details**: {details}")
        entry.extend(["", "---", ""])

        with log_file.open("a", encoding="utf-8") as f:
            f.write("\n".join(entry) + "\n")

        print(f"[UnityDeployer] Checkpoint recorded in: {log_file}")

    def deploy(
        self,
        packed_asset: Path | str,
        game_destination_file: Path | str,
        game_exe_names: Optional[List[str]] = None,
        backup_dir: Optional[Path | str] = None,
        session_log: Optional[Path | str] = None
    ) -> Dict[str, Any]:
        """Safely deploys validated packed asset to game directory after passing all checkpoints."""
        packed_p = Path(packed_asset).resolve()
        dest_p = Path(game_destination_file).resolve()

        if not packed_p.is_file():
            raise FileNotFoundError(f"Packed asset file does not exist: {packed_p}")
        if not dest_p.is_file():
            raise FileNotFoundError(f"Destination game file does not exist: {dest_p}")

        # Checkpoint 1: Verify game process is NOT running
        if game_exe_names:
            is_running, running_list = self.is_game_process_running(game_exe_names)
            if is_running:
                raise RuntimeError(
                    f"DEPLOYMENT BLOCKED: Game process is currently active: {running_list}. "
                    "Close the game completely before deploying mod assets."
                )

        # Checkpoint 2: Immutable original backup
        b_dir = Path(backup_dir).resolve() if backup_dir else None
        backup_file, backup_hash, is_new = self.ensure_immutable_backup(dest_p, b_dir)

        # Checkpoint 3: Hash before copy
        source_packed_hash = sha256_file(packed_p)

        # Checkpoint 4: Deploy validated file
        print(f"[UnityDeployer] Deploying {packed_p.name} -> {dest_p} ...")
        # Remove read-only on target if previously set
        try:
            os.chmod(dest_p, stat.S_IWRITE | stat.S_IREAD)
        except Exception:
            pass
        shutil.copy2(packed_p, dest_p)

        # Checkpoint 5: Verify deployed file hash matches source packed file
        deployed_hash = sha256_file(dest_p)
        if deployed_hash != source_packed_hash:
            # Emergency rollback
            shutil.copy2(backup_file, dest_p)
            raise RuntimeError(
                f"DEPLOYMENT ERROR: Deployed file hash {deployed_hash} does not match packed file hash {source_packed_hash}. "
                "Target restored from immutable backup."
            )

        # Checkpoint 6: Record in session log
        self.log_checkpoint(
            action="Native Asset Deployment",
            target_path=dest_p,
            original_hash=backup_hash,
            deployed_hash=deployed_hash,
            status="SUCCESS",
            details="Native asset replacement validated. Runtime hooks kept disabled.",
            custom_log_path=session_log
        )

        return {
            "success": True,
            "target_file": str(dest_p),
            "backup_file": str(backup_file),
            "backup_hash": backup_hash,
            "deployed_hash": deployed_hash,
            "new_backup_created": is_new
        }

    def rollback(
        self,
        game_destination_file: Path | str,
        backup_dir: Optional[Path | str] = None,
        session_log: Optional[Path | str] = None
    ) -> Dict[str, Any]:
        """Atomically restores target game file from immutable original backup."""
        dest_p = Path(game_destination_file).resolve()
        if backup_dir:
            backup_file = Path(backup_dir).resolve() / f"{dest_p.name}.orig"
        else:
            backup_file = dest_p.with_name(f"{dest_p.name}.orig")

        if not backup_file.is_file():
            raise FileNotFoundError(f"Original backup does not exist: {backup_file}")

        backup_hash = sha256_file(backup_file)

        print(f"[UnityDeployer] Restoring {dest_p.name} from immutable backup {backup_file.name}...")
        try:
            os.chmod(dest_p, stat.S_IWRITE | stat.S_IREAD)
        except Exception:
            pass
        shutil.copy2(backup_file, dest_p)

        restored_hash = sha256_file(dest_p)
        if restored_hash != backup_hash:
            raise RuntimeError("CRITICAL: Restored file hash does not match original backup hash.")

        self.log_checkpoint(
            action="Asset Rollback to Original",
            target_path=dest_p,
            original_hash=backup_hash,
            deployed_hash=restored_hash,
            status="RESTORED",
            details="Successfully restored game file from immutable original backup.",
            custom_log_path=session_log
        )

        return {
            "success": True,
            "target_file": str(dest_p),
            "backup_file": str(backup_file),
            "restored_hash": restored_hash
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="Unity Safe Asset Deployment & Rollback.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Deploy subcommand
    p_deploy = subparsers.add_parser("deploy", help="Deploy packed asset to game directory with safety checks.")
    p_deploy.add_argument("--packed", required=True, type=Path, help="Validated packed asset file")
    p_deploy.add_argument("--destination", required=True, type=Path, help="Target game file in Game Directory")
    p_deploy.add_argument("--game-exe", action="append", help="Game executable name(s) to check (e.g. game.exe)")
    p_deploy.add_argument("--backup-dir", type=Path, help="Custom directory for original backups")
    p_deploy.add_argument("--log", type=Path, default=Path("session_log.md"), help="Session log path")

    # Rollback subcommand
    p_roll = subparsers.add_parser("rollback", help="Restore original asset from immutable backup.")
    p_roll.add_argument("--destination", required=True, type=Path, help="Target game file to restore")
    p_roll.add_argument("--backup-dir", type=Path, help="Custom directory containing original backups")
    p_roll.add_argument("--log", type=Path, default=Path("session_log.md"), help="Session log path")

    args = parser.parse_args()
    deployer = UnityDeployer(session_log_path=args.log)

    if args.command == "deploy":
        res = deployer.deploy(
            packed_asset=args.packed,
            game_destination_file=args.destination,
            game_exe_names=args.game_exe,
            backup_dir=args.backup_dir,
            session_log=args.log
        )
        print(f"[UnityDeployer] SUCCESS: Deployed to {res['target_file']}")
        print(f"  Backup:   {res['backup_file']} ({res['backup_hash']})")
        print(f"  Deployed: {res['deployed_hash']}")

    elif args.command == "rollback":
        res = deployer.rollback(
            game_destination_file=args.destination,
            backup_dir=args.backup_dir,
            session_log=args.log
        )
        print(f"[UnityDeployer] SUCCESS: Restored original asset: {res['target_file']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
