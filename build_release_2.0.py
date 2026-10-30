import os
import sys
import shutil
import zipfile
import subprocess
import hashlib
from pathlib import Path
import datetime
import tempfile
import json

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

def get_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def zipdir(path, ziph, arc_prefix=""):
    total_files = sum(len(files) for _, _, files in os.walk(path))
    processed = 0
    for root, dirs, files in os.walk(path):
        for file in files:
            filepath = os.path.join(root, file)
            rel_path = os.path.relpath(filepath, path)
            arcname = os.path.join(arc_prefix, rel_path)
            ziph.write(filepath, arcname)
            processed += 1
            if processed % 200 == 0 or processed == total_files:
                print(f"Compressing: {processed}/{total_files} files...", end='\r')
    print()

def sync_thub_sources(base_dir, dist_dir):
    """Sync only THub-owned modules; never touch Flagship source or shared Core."""
    base = Path(base_dir)
    internal = Path(dist_dir) / "_internal"
    files = [base / "app_pyqt6.py", base / "i18n_helper.py"]
    files += [p for name in ("core", "ui_pyqt6", "ai") for p in (base / name).rglob("*.py")]
    for source in files:
        destination = internal / source.relative_to(base)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if not destination.exists() or source.read_bytes() != destination.read_bytes():
            shutil.copy2(source, destination)


def promote_runtime(staged_dir, dist_dir, backup_dir):
    """Merge a staged runtime, backing up changes and retaining installed tools/config."""
    staged, target, backup = Path(staged_dir), Path(dist_dir), Path(backup_dir)
    for source in staged.rglob("*"):
        if not source.is_file():
            continue
        rel = source.relative_to(staged)
        if "tools" in rel.parts or rel.name == "hub_config.json":
            continue
        destination = target / rel
        if destination.exists() and get_sha256(source) == get_sha256(destination):
            continue
        if destination.exists():
            saved = backup / rel
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(destination, saved)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def smoke_runtime(exe_path):
    """Require a clean frozen startup/shutdown using an isolated registry."""
    with tempfile.TemporaryDirectory(prefix='thub-release-smoke-') as directory:
        result_path = Path(directory) / 'result.json'
        environment = dict(os.environ, QT_QPA_PLATFORM='offscreen',
                           THUB_CONFIG_PATH=str(Path(directory) / 'config.json'),
                           THUB_SMOKE_RESULT=str(result_path))
        result = subprocess.run([str(exe_path), '--smoke-test'], env=environment, timeout=30,
                                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)
        if result.returncode or not result_path.exists():
            raise RuntimeError('Frozen THub smoke test failed; production was not promoted')
        data = json.loads(result_path.read_text(encoding='utf-8'))
        if not data.get('ok') or not data.get('frozen'):
            raise RuntimeError('Frozen THub did not shut down cleanly')
        return data


def main():
    args = sys.argv[1:]
    skip_build = "--skip-build" in args
    filtered_args = [a for a in args if a != "--skip-build"]
    version = filtered_args[0] if filtered_args else "2.2.0"

    base_dir = os.path.dirname(os.path.abspath(__file__))
    releases_dir = os.path.join(base_dir, "Releases")
    dist_thub_dir = os.path.join(base_dir, "dist", "THub")
    output_zip = os.path.join(releases_dir, f"THub_v{version}.zip")

    os.makedirs(releases_dir, exist_ok=True)

    print("=" * 60)
    print(f"BUILDING THUB v{version} (The Flagship Suite / PyQt6 60 FPS)")
    print("=" * 60)

    # 1. Run PyInstaller
    exe_path = os.path.join(dist_thub_dir, "THub.exe")
    if skip_build and os.path.exists(exe_path):
        print(f"\n[1/4] Skipping PyInstaller compilation (--skip-build). Existing binary: {exe_path}")
    else:
        spec_file = os.path.join(base_dir, "THub.spec")
        print(f"\n[1/4] Running PyInstaller with {spec_file}...")
        staging = os.path.join(base_dir, "workspace", "builds", datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f"))
        cmd = [sys.executable, "-m", "PyInstaller", spec_file, "--noconfirm", "--clean",
               "--distpath", os.path.join(staging, "dist"), "--workpath", os.path.join(staging, "build")]
        environment = dict(os.environ, THUB_BUILD_RUNTIME_ONLY="1")
        res = subprocess.run(cmd, cwd=base_dir, env=environment,
                             creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
        if res.returncode != 0:
            print("\n[!] PyInstaller compilation failed!")
            sys.exit(res.returncode)
        smoke_runtime(Path(staging) / 'dist' / 'THub' / 'THub.exe')
        # Promote only THub runtime files. Preserve protected tools and the live registry.
        promote_runtime(os.path.join(staging, "dist", "THub"), dist_thub_dir,
                        os.path.join(staging, "previous-runtime"))

    sync_thub_sources(base_dir, dist_thub_dir)
    # 2. Post-Build File Injection
    print("\n[2/4] Injecting root release files into dist/THub...")
    default_cfg = os.path.join(base_dir, "hub_config.default.json")
    target_cfg = os.path.join(dist_thub_dir, "hub_config.json")
    if os.path.exists(default_cfg) and not os.path.exists(target_cfg):
        shutil.copy2(default_cfg, target_cfg)
        print("  [+] Injected clean hub_config.json")

    for f in ["README.md", "LICENSE", "run_thub.bat", "run_thub_pyqt6.bat", "run_thub_silent.vbs", "ai_instructions.md"]:
        src_f = os.path.join(base_dir, f)
        if os.path.exists(src_f):
            shutil.copy2(src_f, os.path.join(dist_thub_dir, f))
            print(f"  [+] Injected {f}")

    # 3. Create Release ZIP
    print(f"\n[3/4] Creating distribution archive: {output_zip}...")
    if os.path.exists(output_zip):
        os.remove(output_zip)

    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
        zipdir(dist_thub_dir, zipf, arc_prefix="THub")

    # 4. Final Summary
    zip_size_mb = os.path.getsize(output_zip) / (1024 * 1024)
    sha256 = get_sha256(output_zip)

    print("\n[4/4] Release Build Complete!")
    print("=" * 60)
    print(f"Archive:  {output_zip}")
    print(f"Size:     {zip_size_mb:.2f} MB")
    print(f"SHA-256:  {sha256}")
    print("=" * 60)

if __name__ == "__main__":
    main()
