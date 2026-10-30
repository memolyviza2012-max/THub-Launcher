"""Verified file snapshots and non-overwriting transfers for THub adoption."""
import hashlib
import json
import os
import shutil
import stat
import uuid
from pathlib import Path
from core.safe_io import write_json_atomic


def digest(path):
    value = hashlib.sha256()
    with open(path, 'rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def is_link(path):
    return os.path.islink(path) or bool(getattr(os.lstat(path), 'st_file_attributes', 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT)


def contained(root, path):
    try:
        resolved_root = os.path.normcase(os.path.realpath(root))
        resolved_path = os.path.normcase(os.path.realpath(path))
        return os.path.commonpath([resolved_root, resolved_path]) == resolved_root
    except ValueError:
        # Windows paths on different drives cannot contain each other.
        return False


def create_snapshot(root):
    """Copy and hash every regular source file; never traverse reparse points."""
    root = Path(root).resolve()
    snapshot = root / '_thub_legacy_snapshot' / uuid.uuid4().hex
    snapshot.mkdir(parents=True)
    entries = []
    for folder, dirs, files in os.walk(root):
        dirs[:] = [name for name in dirs if name != '_thub_legacy_snapshot']
        for name in dirs + files:
            if is_link(Path(folder) / name):
                raise ValueError(f'Snapshot does not follow links: {Path(folder) / name}')
        for name in files:
            src = Path(folder) / name
            rel = src.relative_to(root)
            dst = snapshot / 'files' / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            original_hash = digest(src)
            shutil.copy2(src, dst)
            if digest(dst) != original_hash or digest(src) != original_hash:
                raise OSError(f'File changed or backup verification failed: {src}')
            entries.append({'path': rel.as_posix(), 'sha256': original_hash, 'size': src.stat().st_size})
    manifest = {'version': 1, 'source_folder': str(root), 'files': entries, 'verified': True}
    write_json_atomic(snapshot / 'snapshot_manifest.json', manifest)
    return str(snapshot)


def restore_snapshot(snapshot, target=None):
    """Restore verified originals; retain newly-created files for manual review."""
    snapshot = Path(snapshot).resolve()
    with (snapshot / 'snapshot_manifest.json').open(encoding='utf-8') as handle:
        manifest = json.load(handle)
    if not manifest.get('verified'):
        raise ValueError('Snapshot is not verified')
    root = Path(target or manifest['source_folder']).resolve()
    # Verify the whole backup before changing a single destination file.
    for entry in manifest['files']:
        src = snapshot / 'files' / entry['path']
        dst = root / entry['path']
        if not contained(snapshot / 'files', src) or not contained(root, dst):
            raise ValueError('Invalid snapshot path')
        if digest(src) != entry['sha256']:
            raise OSError(f'Backup checksum mismatch: {src}')
    for entry in manifest['files']:
        src = snapshot / 'files' / entry['path']
        dst = root / entry['path']
        dst.parent.mkdir(parents=True, exist_ok=True)
        temporary = dst.with_name(dst.name + '.restore-' + uuid.uuid4().hex)
        try:
            shutil.copy2(src, temporary)
            os.replace(temporary, dst)
        finally:
            if temporary.exists():
                temporary.unlink()
    return len(manifest['files'])


def transfer_unique(source, destination, copy_only=True):
    """Reserve a unique destination and verify bytes before removing any source."""
    source, destination = Path(source), Path(destination)
    if is_link(source):
        raise ValueError(f'Cannot transfer a link: {source}')
    destination.parent.mkdir(parents=True, exist_ok=True)
    stem, suffix = destination.stem, destination.suffix
    attempt = 0
    while True:
        dest = destination if attempt == 0 else destination.with_name(f'{stem}_legacy{attempt}{suffix}')
        attempt += 1
        directory = source.is_dir()
        try:
            if directory:
                dest.mkdir()
                out = None
            else:
                out = dest.open('xb')
        except FileExistsError:
            continue
        if directory:
            # Reserve the directory; recurse without merging existing directories.
            for child in source.iterdir():
                transfer_unique(child, dest / child.name, copy_only)
            if not copy_only:
                source.rmdir()
        else:
            with out:
                with source.open('rb') as inp:
                    shutil.copyfileobj(inp, out, 1024 * 1024)
                out.flush()
                os.fsync(out.fileno())
            if digest(source) != digest(dest):
                raise OSError(f'Transfer checksum mismatch: {source}')
            shutil.copystat(source, dest)
            if not copy_only:
                source.unlink()
        return str(dest)
