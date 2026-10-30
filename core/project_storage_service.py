import os
import json
import time
import stat
from PyQt6.QtCore import QThread, pyqtSignal
from core.config_manager import ConfigManager


class ProjectStorageService:
    """
    Service for calculating, formatting, and caching disk storage usage of mod projects.
    Executes background folder scans without blocking the Qt event loop.
    """

    CACHE_KEY = "project_disk_storage_cache"
    CACHE_TTL_SECONDS = 3600 * 6  # 6 hours cache validity

    @classmethod
    def format_size(cls, bytes_val):
        """Formats bytes into human-readable string (GB, MB, KB, B)."""
        if bytes_val is None or bytes_val <= 0:
            return "0 B"
        if bytes_val >= 1024 * 1024 * 1024:
            return f"{bytes_val / (1024 * 1024 * 1024):.2f} GB"
        elif bytes_val >= 1024 * 1024:
            return f"{bytes_val / (1024 * 1024):.1f} MB"
        elif bytes_val >= 1024:
            return f"{bytes_val / 1024:.0f} KB"
        return f"{bytes_val} B"

    @classmethod
    def get_dir_size_fast(cls, folder_path, cancelled=None):
        """Recursively calculates directory size in bytes avoiding symlinks."""
        total = 0
        if not folder_path:
            return total
        pending = [folder_path]
        while pending:
            if cancelled and cancelled():
                break
            directory = pending.pop()
            try:
                with os.scandir(directory) as entries:
                    for entry in entries:
                        if cancelled and cancelled():
                            return total
                        try:
                            if entry.is_symlink():
                                continue
                            info = entry.stat(follow_symlinks=False)
                            if getattr(info, 'st_file_attributes', 0) & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0):
                                continue
                            if stat.S_ISREG(info.st_mode):
                                total += info.st_size
                            elif stat.S_ISDIR(info.st_mode):
                                # Skip virtual environments or git packs if nested deep
                                if entry.name not in ('.git', '__pycache__', '.idea', 'node_modules'):
                                    pending.append(entry.path)
                        except (PermissionError, FileNotFoundError, OSError):
                            continue
            except (PermissionError, FileNotFoundError, OSError):
                continue
        return total

    @classmethod
    def get_cached_sizes(cls):
        """Retrieves cached project sizes from ConfigManager."""
        cfg = ConfigManager()
        return cfg.get(cls.CACHE_KEY, {})

    @classmethod
    def save_cached_sizes(cls, cache_dict):
        """Persists project sizes cache to ConfigManager."""
        cfg = ConfigManager()
        cfg.set(cls.CACHE_KEY, cache_dict)

    @classmethod
    def get_size_for_project(cls, project, force_refresh=False):
        """
        Gets size for a single project, using cached value if available.
        Returns size in bytes.
        """
        path = project.get("path", "")
        if not path or not os.path.exists(path):
            return 0

        cache = cls.get_cached_sizes()
        cached_entry = cache.get(path)

        now = time.time()
        if not force_refresh and cached_entry:
            ts = cached_entry.get("timestamp", 0)
            if now - ts < cls.CACHE_TTL_SECONDS:
                return cached_entry.get("size", 0)

        # Calculate fresh
        sz = cls.get_dir_size_fast(path)
        cache[path] = {
            "size": sz,
            "timestamp": now,
            "name": project.get("name", "")
        }
        cls.save_cached_sizes(cache)
        return sz


class StorageScanWorker(QThread):
    """Background worker thread to calculate storage sizes for all projects."""
    progress_updated = pyqtSignal(int, int)   # current, total
    project_scanned = pyqtSignal(str, object)  # path, size (object prevents 32-bit integer overflow)
    scan_failed = pyqtSignal(str)
    scan_finished = pyqtSignal(dict)          # {path: size}

    def __init__(self, projects, force_refresh=False, parent=None):
        super().__init__(parent)
        self.projects = [dict(project) for project in (projects or [])]
        self.force_refresh = force_refresh
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        self._results = {}
        try:
            self._scan()
        except Exception as error:
            self.scan_failed.emit(str(error))
        finally:
            self.scan_finished.emit(self._results)

    def _scan(self):
        results = self._results
        total = len(self.projects)
        cache = ProjectStorageService.get_cached_sizes()
        now = time.time()
        updated_cache = dict(cache)
        dirty = False
        last_saved = time.monotonic()

        for i, p in enumerate(self.projects):
            if self._is_cancelled:
                break

            path = p.get("path", "")
            if not path or not os.path.exists(path):
                results[path] = 0
                self.project_scanned.emit(path, 0)
                self.progress_updated.emit(i + 1, total)
                continue

            # Check cache
            cached_entry = cache.get(path)
            if not self.force_refresh and cached_entry:
                ts = cached_entry.get("timestamp", 0)
                if now - ts < ProjectStorageService.CACHE_TTL_SECONDS:
                    sz = cached_entry.get("size", 0)
                    results[path] = sz
                    self.project_scanned.emit(path, sz)
                    self.progress_updated.emit(i + 1, total)
                    continue

            # Compute size
            sz = ProjectStorageService.get_dir_size_fast(path, lambda: self._is_cancelled)
            if self._is_cancelled:
                break
            results[path] = sz
            updated_cache[path] = {
                "size": sz,
                "timestamp": now,
                "name": p.get("name", "")
            }
            dirty = True
            self.project_scanned.emit(path, sz)
            self.progress_updated.emit(i + 1, total)

            # Persist cache incrementally every 4 projects
            if (i + 1) % 4 == 0 and time.monotonic() - last_saved >= 1.0:
                ProjectStorageService.save_cached_sizes(updated_cache)
                dirty = False
                last_saved = time.monotonic()

        if dirty:
            ProjectStorageService.save_cached_sizes(updated_cache)
