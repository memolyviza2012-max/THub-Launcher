"""
Project Move & Cross-Drive Migration Service for THub.
Safely moves mod projects to another storage volume (e.g. HDD) with a sequential FIFO queue,
rigorous 100% integrity verification, atomic configuration sync, and automatic disk space reclamation.
"""

import os
import sys
import time
import shutil
import hashlib
import stat
import string
import threading
import tempfile
import copy
import json
from pathlib import Path
from core.project_backup import is_link
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Callable

from PyQt6.QtCore import QThread, pyqtSignal

from core.config_manager import ConfigManager
from core.project_storage_service import ProjectStorageService
from core.safe_io import write_json_atomic, update_json_atomic


class MoveTaskStatus(str, Enum):
    QUEUED = "QUEUED"              # รอคิว
    CHECKING = "CHECKING"          # ตรวจสอบพื้นที่ & สิทธิ์
    COPYING = "COPYING"            # กำลังคัดลอกไฟล์
    VERIFYING = "VERIFYING"        # ตรวจสอบความสมบูรณ์ 100%
    UPDATING = "UPDATING"          # อัปเดตพาธใน THub
    CLEANING = "CLEANING"          # ลบต้นทาง คืนพื้นที่ดิสก์
    COMPLETED = "COMPLETED"        # ย้ายสำเร็จสมบูรณ์
    FAILED = "FAILED"              # ล้มเหลว
    CANCELLED = "CANCELLED"        # ยกเลิก
    PAUSED = "PAUSED"              # หยุดชั่วคราว


@dataclass
class ProjectMoveTask:
    project_name: str
    source_path: str
    dest_parent_dir: str
    dest_path: str = ""
    total_bytes: int = 0
    moved_bytes: int = 0
    total_files: int = 0
    copied_files: int = 0
    current_file: str = ""
    status: MoveTaskStatus = MoveTaskStatus.QUEUED
    error_message: str = ""
    speed_bps: float = 0.0
    eta_seconds: float = 0.0
    allow_overwrite: bool = True
    freed_bytes: int = 0

    def __post_init__(self):
        if not self.dest_path and self.source_path and self.dest_parent_dir:
            folder_name = os.path.basename(os.path.normpath(self.source_path))
            self.dest_path = os.path.join(self.dest_parent_dir, folder_name)


class ProjectMoveService:
    """Utility methods for disk inspection, drive enumeration, and pre-flight move checks."""

    @staticmethod
    def get_available_drives() -> List[Dict]:
        """Returns all valid logical drives with total, used, free space and format info."""
        drives = []
        if sys.platform == "win32":
            for letter in string.ascii_uppercase:
                root = f"{letter}:\\"
                if os.path.exists(root):
                    try:
                        usage = shutil.disk_usage(root)
                        is_cloud = (usage.total >= 10 * 1024 * 1024 * 1024 * 1024) or (usage.free >= 10 * 1024 * 1024 * 1024 * 1024)
                        drives.append({
                            "letter": f"{letter}:",
                            "root": root,
                            "total": usage.total,
                            "used": usage.used,
                            "free": usage.free,
                            "is_cloud": is_cloud,
                            "total_str": "RaiDrive / คลาวด์" if is_cloud else ProjectStorageService.format_size(usage.total),
                            "used_str": ProjectStorageService.format_size(usage.used),
                            "free_str": "ไม่จำกัด" if is_cloud else ProjectStorageService.format_size(usage.free),
                            "percent_used": 0.0 if is_cloud else (round((usage.used / usage.total) * 100, 1) if usage.total > 0 else 0)
                        })
                    except (PermissionError, OSError):
                        continue
        else:
            try:
                usage = shutil.disk_usage("/")
                drives.append({
                    "letter": "/",
                    "root": "/",
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "total_str": ProjectStorageService.format_size(usage.total),
                    "used_str": ProjectStorageService.format_size(usage.used),
                    "free_str": ProjectStorageService.format_size(usage.free),
                    "percent_used": round((usage.used / usage.total) * 100, 1) if usage.total > 0 else 0
                })
            except Exception:
                pass
        return drives

    @staticmethod
    def get_drive_for_path(path: str) -> Optional[Dict]:
        """Gets drive information for a specific directory path."""
        if not path:
            return None
        norm = os.path.abspath(path)
        drive_prefix = os.path.splitdrive(norm)[0]
        if drive_prefix:
            root = f"{drive_prefix}\\"
        else:
            root = "/"
        try:
            usage = shutil.disk_usage(root if os.path.exists(root) else os.path.dirname(norm))
            is_cloud = (usage.total >= 10 * 1024 * 1024 * 1024 * 1024) or (usage.free >= 10 * 1024 * 1024 * 1024 * 1024)
            return {
                "letter": drive_prefix or root,
                "root": root,
                "total": usage.total,
                "used": usage.used,
                "free": usage.free,
                "is_cloud": is_cloud,
                "total_str": "RaiDrive / คลาวด์" if is_cloud else ProjectStorageService.format_size(usage.total),
                "used_str": ProjectStorageService.format_size(usage.used),
                "free_str": "ไม่จำกัด" if is_cloud else ProjectStorageService.format_size(usage.free),
                "percent_used": 0.0 if is_cloud else (round((usage.used / usage.total) * 100, 1) if usage.total > 0 else 0)
            }
        except Exception:
            return None

    @staticmethod
    def validate_preflight(source_path: str, dest_parent_dir: str, required_bytes: int = 0, allow_overwrite: bool = True) -> (bool, str):
        """
        Validates whether moving source_path to dest_parent_dir is safe:
        - Source exists and is directory
        - Destination parent exists or parent exists
        - Not circular (dest not inside source and vice-versa)
        - Sufficient free disk space on destination (+ 256MB safety headroom)
        """
        if not source_path or not os.path.isdir(source_path):
            return False, f"ไม่พบโฟลเดอร์ต้นทาง: '{source_path}'"

        if not dest_parent_dir:
            return False, "ยังไม่ได้ระบุโฟลเดอร์ปลายทาง"

        src_norm = os.path.realpath(os.path.abspath(os.path.normpath(source_path)))
        if os.path.dirname(src_norm) == src_norm or is_link(source_path):
            return False, "ไม่อนุญาตให้ย้ายรากไดรฟ์หรือโฟลเดอร์ลิงก์"
        dest_parent_norm = os.path.realpath(os.path.abspath(os.path.normpath(dest_parent_dir)))
        folder_name = os.path.basename(src_norm)
        dest_norm = os.path.join(dest_parent_norm, folder_name)

        if src_norm.lower() == dest_norm.lower():
            return False, "ตำแหน่งปลายทางเหมือนกับตำแหน่งต้นทางเดิม ไม่จำเป็นต้องย้าย"

        # Check circular containment
        try:
            common = os.path.commonpath([src_norm, dest_norm])
            if common.lower() in (src_norm.lower(), dest_norm.lower()):
                return False, "โฟลเดอร์ปลายทางอยู่ภายในโฟลเดอร์ต้นทาง ไม่สามารถย้ายได้"
        except ValueError:
            # Different drives (e.g. E: and D:) have no common path on Windows, which is expected
            pass

        # Check destination drive space
        try:
            drive_info = ProjectMoveService.get_drive_for_path(dest_parent_norm)
            if drive_info:
                headroom = 256 * 1024 * 1024  # 256 MB buffer
                if drive_info["free"] < (required_bytes + headroom):
                    needed_str = ProjectStorageService.format_size(required_bytes + headroom)
                    free_str = ProjectStorageService.format_size(drive_info["free"])
                    return False, f"พื้นที่ว่างในไดรฟ์ปลายทาง ({drive_info['letter']}) ไม่เพียงพอ (ต้องการ {needed_str} แต่มีว่าง {free_str})"
        except Exception as e:
            return False, f"ไม่สามารถตรวจสอบพื้นที่ดิสก์ปลายทางได้: {e}"

        # Check collision
        if os.path.exists(dest_norm) and not allow_overwrite:
            try:
                with os.scandir(dest_norm) as it:
                    if any(it):
                        return False, f"โฟลเดอร์ปลายทาง '{dest_norm}' มีอยู่แล้วและไม่ใช่โฟลเดอร์ว่าง กรุณาเปลี่ยนชื่อหรือลบข้อมูลเก่าก่อน"
            except Exception:
                return False, f"โฟลเดอร์ปลายทาง '{dest_norm}' มีอยู่แล้ว"

        return True, ""


class ProjectMoveWorker(QThread):
    """
    Background worker thread executing the Project Move Queue sequentially.
    Guarantees zero data loss:
    1. Pre-flight space and permission validation.
    2. Byte-by-byte copy with progress tracking and pause/cancel handling.
    3. 100% integrity verification (file count, byte sizes, checksums).
    4. Atomic THub configuration & metadata update.
    5. Clean source directory deletion ONLY after full verification.
    """

    task_status_changed = pyqtSignal(str, str, str)          # project_name, status, message
    task_progress = pyqtSignal(str, object, object, str, float, float)  # project_name, moved_bytes, total_bytes, current_file, speed_bps, eta
    task_completed = pyqtSignal(str, str, object)             # project_name, new_path, bytes_freed
    task_failed = pyqtSignal(str, str)                        # project_name, error_reason
    queue_progress = pyqtSignal(int, int, object, object)     # completed_count, total_count, total_moved_bytes, total_queue_bytes
    queue_finished = pyqtSignal(int, int, object)             # completed_count, failed_count, total_bytes_freed
    log_message = pyqtSignal(str, str)                        # level (INFO/WARNING/ERROR), text

    CHUNK_SIZE = 1024 * 1024  # 1MB per chunk

    def __init__(self, tasks: Optional[List[ProjectMoveTask]] = None, parent=None):
        super().__init__(parent)
        self._tasks: List[ProjectMoveTask] = tasks or []
        self._is_paused = False
        self._is_cancelled = False
        self._pause_cond = threading.Condition()
        self._current_task: Optional[ProjectMoveTask] = None
        self._owned_staging = set()

    def set_tasks(self, tasks: List[ProjectMoveTask]):
        self._tasks = list(tasks)

    def pause(self):
        with self._pause_cond:
            self._is_paused = True
            if self._current_task:
                self._current_task.status = MoveTaskStatus.PAUSED
                self.task_status_changed.emit(self._current_task.project_name, MoveTaskStatus.PAUSED.value, "หยุดพักชั่วคราว")

    def resume(self):
        with self._pause_cond:
            self._is_paused = False
            self._pause_cond.notify_all()
            if self._current_task:
                self._current_task.status = MoveTaskStatus.COPYING
                self.task_status_changed.emit(self._current_task.project_name, MoveTaskStatus.COPYING.value, "ดำเนินการต่อ")

    def cancel(self):
        with self._pause_cond:
            self._is_cancelled = True
            self._pause_cond.notify_all()
            if self._current_task:
                self._current_task.status = MoveTaskStatus.CANCELLED
                self.task_status_changed.emit(self._current_task.project_name, MoveTaskStatus.CANCELLED.value, "ยกเลิกโดยผู้ใช้")

    def is_paused(self) -> bool:
        return self._is_paused

    def is_cancelled(self) -> bool:
        return self._is_cancelled

    def _wait_if_paused(self):
        with self._pause_cond:
            while self._is_paused and not self._is_cancelled:
                self._pause_cond.wait(0.2)

    @staticmethod
    def _handle_remove_readonly(func, path, exc_info):
        """Error handler for shutil.rmtree to strip Windows read-only attribute and retry."""
        try:
            os.chmod(path, stat.S_IWRITE)
            func(path)
        except Exception:
            pass

    @staticmethod
    def _compute_fast_hash(file_path: str, max_sample: int = 4 * 1024 * 1024, cancelled=None) -> str:
        """Full streaming SHA-256 (legacy method name retained for callers).

        Every byte is hashed, including large archives. Sampling cannot safely
        authorize deletion of a source file after a move.
        """
        h = hashlib.sha256()
        with open(file_path, 'rb') as handle:
            for block in iter(lambda: handle.read(max_sample), b''):
                if cancelled and cancelled():
                    raise InterruptedError("Move verification cancelled")
                h.update(block)
        return h.hexdigest()

    @staticmethod
    def _source_signature(path):
        value = os.stat(path, follow_symlinks=False)
        return (value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns)

    @staticmethod
    def _assert_regular_tree(root):
        if is_link(root):
            raise ValueError(f"Filesystem links are not supported for moves: {root}")
        for directory, dirs, files in os.walk(root):
            for name in dirs + files:
                path = os.path.join(directory, name)
                if is_link(path):
                    raise ValueError(f"Filesystem links are not supported for moves: {path}")

    def _commit_staging(self, staging, destination, entries, allow_overwrite):
        """Publish verified files; retain overwritten bytes and roll back failed merges."""
        if not os.path.exists(destination):
            os.replace(staging, destination)
            return None
        self._assert_regular_tree(destination)
        with os.scandir(destination) as existing_entries:
            if not allow_overwrite and any(existing_entries):
                raise FileExistsError(f"Destination became occupied: {destination}")
        # Preserve empty directories as well as files when merging into an existing workspace.
        for directory, dirs, files in os.walk(staging):
            rel = os.path.relpath(directory, staging)
            if rel != ".":
                os.makedirs(os.path.join(destination, rel), exist_ok=True)
        previous = tempfile.mkdtemp(prefix=".thub-move-previous-", dir=os.path.dirname(destination))
        applied = []
        try:
            for rel, source, size in entries:
                incoming = os.path.join(staging, rel)
                target = os.path.join(destination, rel)
                saved = os.path.join(previous, rel)
                os.makedirs(os.path.dirname(target), exist_ok=True)
                existed = os.path.lexists(target)
                if existed:
                    if not os.path.isfile(target) or is_link(target):
                        raise ValueError(f"Destination is not a regular file: {target}")
                    if not allow_overwrite:
                        raise FileExistsError(target)
                    os.makedirs(os.path.dirname(saved), exist_ok=True)
                    os.replace(target, saved)
                applied.append((target, saved, existed))
                os.replace(incoming, target)
            write_json_atomic(previous + '.manifest.json', {
                'destination': destination,
                'overwritten_files': [os.path.relpath(saved, previous) for target, saved, existed in applied if existed]
            })
        except Exception:
            for target, saved, existed in reversed(applied):
                if existed and os.path.exists(saved):
                    os.replace(saved, target)
                elif not existed and os.path.isfile(target):
                    os.unlink(target)
            raise
        return previous

    def run(self):
        total_tasks = len(self._tasks)
        completed_tasks = 0
        failed_tasks = 0
        total_freed_bytes = 0

        # Calculate initial total queue bytes
        total_queue_bytes = sum(t.total_bytes for t in self._tasks)
        moved_queue_bytes = 0

        self.log_message.emit("INFO", f"🚀 เริ่มต้นระบบย้ายโปรเจกต์ ทั้งหมด {total_tasks} โปรเจกต์...")

        for idx, task in enumerate(self._tasks):
            if self._is_cancelled:
                task.status = MoveTaskStatus.CANCELLED
                self.task_status_changed.emit(task.project_name, MoveTaskStatus.CANCELLED.value, "ยกเลิกคิว")
                continue

            self._current_task = task
            self._wait_if_paused()
            if self._is_cancelled:
                break

            # Process single task
            success = self._execute_task(task, moved_queue_bytes, total_queue_bytes)
            if success:
                completed_tasks += 1
                total_freed_bytes += task.freed_bytes
                moved_queue_bytes += task.total_bytes
            else:
                failed_tasks += 1

            self.queue_progress.emit(completed_tasks, total_tasks, moved_queue_bytes, total_queue_bytes)

        self._current_task = None
        self.log_message.emit("INFO", f"🏁 คิวการย้ายเสร็จสิ้น: สำเร็จ {completed_tasks}, ล้มเหลว {failed_tasks}, คืนพื้นที่ทั้งหมด {ProjectStorageService.format_size(total_freed_bytes)}")
        self.queue_finished.emit(completed_tasks, failed_tasks, total_freed_bytes)

    def _execute_task(self, task: ProjectMoveTask, base_queue_moved: int, total_queue_bytes: int) -> bool:
        project_name = task.project_name
        src = os.path.abspath(os.path.normpath(task.source_path))
        dest = os.path.abspath(os.path.normpath(task.dest_path))
        destination = dest
        expected_destination = os.path.abspath(os.path.join(task.dest_parent_dir, os.path.basename(src)))
        if os.path.normcase(dest) != os.path.normcase(expected_destination):
            task.status = MoveTaskStatus.FAILED
            task.error_message = "Destination must match the selected source folder name"
            self.task_failed.emit(project_name, task.error_message)
            return False
        dest_existed_initially = os.path.exists(dest)
        source_root_signature = self._source_signature(src) if os.path.isdir(src) else None
        source_signatures = {}
        task.freed_bytes = 0

        # ----------------------------------------------------
        # STAGE 1: Pre-Flight Check & Scan
        # ----------------------------------------------------
        task.status = MoveTaskStatus.CHECKING
        self.task_status_changed.emit(project_name, MoveTaskStatus.CHECKING.value, "กำลังตรวจสอบพื้นที่ดิสก์และสิทธิ์เข้าถึง...")

        valid, err_msg = ProjectMoveService.validate_preflight(
            src, task.dest_parent_dir, task.total_bytes, allow_overwrite=task.allow_overwrite
        )
        if not valid:
            task.status = MoveTaskStatus.FAILED
            task.error_message = err_msg
            self.task_status_changed.emit(project_name, MoveTaskStatus.FAILED.value, err_msg)
            self.task_failed.emit(project_name, err_msg)
            self.log_message.emit("ERROR", f"❌ [{project_name}] ตรวจสอบไม่ผ่าน: {err_msg}")
            return False

        # Scan files and directories in source
        file_entries = []
        dir_entries = []
        actual_total_bytes = 0

        try:
            self._assert_regular_tree(src)
            for root, dirs, files in os.walk(src):
                rel_dir = os.path.relpath(root, src)
                if rel_dir != ".":
                    dir_entries.append(rel_dir)
                for f in files:
                    full_p = os.path.join(root, f)
                    rel_p = os.path.relpath(full_p, src)
                    sz = os.path.getsize(full_p)
                    file_entries.append((rel_p, full_p, sz))
                    source_signatures[rel_p] = self._source_signature(full_p)
                    actual_total_bytes += sz
        except Exception as e:
            err_msg = f"ไม่สามารถสแกนไฟล์ต้นทางได้: {e}"
            task.status = MoveTaskStatus.FAILED
            task.error_message = err_msg
            self.task_status_changed.emit(project_name, MoveTaskStatus.FAILED.value, err_msg)
            self.task_failed.emit(project_name, err_msg)
            return False

        task.total_bytes = actual_total_bytes
        task.total_files = len(file_entries)
        task.copied_files = 0
        task.moved_bytes = 0

        # Secondary free space check with actual scanned bytes
        drive_info = ProjectMoveService.get_drive_for_path(task.dest_parent_dir)
        if drive_info and drive_info["free"] < (actual_total_bytes + 256 * 1024 * 1024):
            err_msg = f"พื้นที่ว่างไม่พอ (ต้องการ {ProjectStorageService.format_size(actual_total_bytes + 256 * 1024 * 1024)} แต่ว่าง {drive_info['free_str']})"
            task.status = MoveTaskStatus.FAILED
            task.error_message = err_msg
            self.task_status_changed.emit(project_name, MoveTaskStatus.FAILED.value, err_msg)
            self.task_failed.emit(project_name, err_msg)
            return False

        # ----------------------------------------------------
        # STAGE 2: Safe Copying
        # ----------------------------------------------------
        task.status = MoveTaskStatus.COPYING
        self.task_status_changed.emit(project_name, MoveTaskStatus.COPYING.value, "กำลังคัดลอกไฟล์ไปยังปลายทาง...")
        self.log_message.emit("INFO", f"📦 [{project_name}] เริ่มคัดลอก {task.total_files} ไฟล์ ({ProjectStorageService.format_size(task.total_bytes)}) -> {dest}")

        try:
            # Copy into an owned staging tree; failure never truncates existing destination files.
            os.makedirs(task.dest_parent_dir, exist_ok=True)
            dest = tempfile.mkdtemp(prefix=".thub-move-staging-", dir=task.dest_parent_dir)
            self._owned_staging.add(os.path.realpath(dest))
            dest_existed_initially = False
            os.makedirs(dest, exist_ok=True)
            for d in dir_entries:
                os.makedirs(os.path.join(dest, d), exist_ok=True)
        except Exception as e:
            err_msg = f"ไม่สามารถสร้างโฟลเดอร์ปลายทางได้: {e}"
            task.status = MoveTaskStatus.FAILED
            task.error_message = err_msg
            self.task_status_changed.emit(project_name, MoveTaskStatus.FAILED.value, err_msg)
            self.task_failed.emit(project_name, err_msg)
            return False

        # Speed and ETA tracking
        start_time = time.time()
        last_metric_time = start_time
        last_metric_bytes = 0

        for rel_p, src_file, sz in file_entries:
            self._wait_if_paused()
            if self._is_cancelled:
                self._cleanup_partial_dest(dest, dest_existed_initially)
                task.status = MoveTaskStatus.CANCELLED
                self.task_status_changed.emit(project_name, MoveTaskStatus.CANCELLED.value, "ยกเลิกการคัดลอก")
                return False

            dst_file = os.path.join(dest, rel_p)
            task.current_file = rel_p

            try:
                # Ensure destination directory exists
                os.makedirs(os.path.dirname(dst_file), exist_ok=True)

                # Chunked copy with progress tracking
                if self._source_signature(src_file) != source_signatures[rel_p]:
                    raise OSError(f"Source changed before copying: {rel_p}")
                with open(src_file, 'rb') as f_in, open(dst_file, 'xb') as f_out:
                    while True:
                        self._wait_if_paused()
                        if self._is_cancelled:
                            break
                        chunk = f_in.read(self.CHUNK_SIZE)
                        if not chunk:
                            break
                        f_out.write(chunk)
                        task.moved_bytes += len(chunk)

                        # Update metrics every ~250ms
                        now = time.time()
                        dt = now - last_metric_time
                        if dt >= 0.25:
                            bytes_delta = task.moved_bytes - last_metric_bytes
                            speed = bytes_delta / dt if dt > 0 else 0
                            task.speed_bps = speed
                            rem_bytes = max(0, task.total_bytes - task.moved_bytes)
                            task.eta_seconds = (rem_bytes / speed) if speed > 0 else 0

                            last_metric_time = now
                            last_metric_bytes = task.moved_bytes

                            self.task_progress.emit(
                                project_name,
                                task.moved_bytes,
                                task.total_bytes,
                                rel_p,
                                task.speed_bps,
                                task.eta_seconds
                            )

                            current_queue_moved = base_queue_moved + task.moved_bytes
                            self.queue_progress.emit(
                                0,  # completed in caller
                                len(self._tasks),
                                current_queue_moved,
                                total_queue_bytes
                            )

                if self._is_cancelled:
                    self._cleanup_partial_dest(dest, dest_existed_initially)
                    task.status = MoveTaskStatus.CANCELLED
                    self.task_status_changed.emit(project_name, MoveTaskStatus.CANCELLED.value, "ยกเลิกการคัดลอก")
                    return False

                if self._source_signature(src_file) != source_signatures[rel_p]:
                    raise OSError(f"Source changed while copying: {rel_p}")
                # Copy file timestamps and permissions
                shutil.copystat(src_file, dst_file)
                task.copied_files += 1

            except Exception as e:
                err_msg = f"ข้อผิดพลาดขณะคัดลอกไฟล์ '{rel_p}': {e}"
                self._cleanup_partial_dest(dest, dest_existed_initially)
                task.status = MoveTaskStatus.FAILED
                task.error_message = err_msg
                self.task_status_changed.emit(project_name, MoveTaskStatus.FAILED.value, err_msg)
                self.task_failed.emit(project_name, err_msg)
                self.log_message.emit("ERROR", f"❌ [{project_name}] คัดลอกล้มเหลว: {err_msg}")
                return False

        # Final progress emit for copying
        self.task_progress.emit(project_name, task.total_bytes, task.total_bytes, "คัดลอกเสร็จสิ้น", 0, 0)

        # ----------------------------------------------------
        # STAGE 3: 100% Integrity Verification
        # ----------------------------------------------------
        task.status = MoveTaskStatus.VERIFYING
        self.task_status_changed.emit(project_name, MoveTaskStatus.VERIFYING.value, "กำลังตรวจสอบความถูกต้องของไฟล์ 100%...")
        self.log_message.emit("INFO", f"🔍 [{project_name}] กำลังตรวจสอบความสมบูรณ์ ({task.total_files} ไฟล์)...")

        try:
            for rel_p, src_file, expected_sz in file_entries:
                self._wait_if_paused()
                if self._is_cancelled:
                    self._cleanup_partial_dest(dest, dest_existed_initially)
                    task.status = MoveTaskStatus.CANCELLED
                    return False

                dst_file = os.path.join(dest, rel_p)
                if not os.path.exists(dst_file):
                    raise OSError(f"ไม่พบไฟล์ปลายทางหลังคัดลอก: {rel_p}")

                actual_sz = os.path.getsize(dst_file)
                if actual_sz != expected_sz:
                    raise OSError(f"ขนาดไฟล์ไม่ตรงกันสำหรับ '{rel_p}': ต้นทาง={expected_sz}, ปลายทาง={actual_sz}")

                # Full-file checksum validation; large files are not sampled.
                src_hash = self._compute_fast_hash(src_file, cancelled=lambda: self._is_cancelled)
                dst_hash = self._compute_fast_hash(dst_file, cancelled=lambda: self._is_cancelled)
                if self._source_signature(src_file) != source_signatures[rel_p]:
                    raise OSError(f"Source changed while verifying: {rel_p}")
                if src_hash != dst_hash:
                    raise OSError(f"ผลรวมการตรวจสอบ (Checksum) ไม่ตรงกันสำหรับ '{rel_p}'")

        except Exception as e:
            err_msg = f"การตรวจสอบความสมบูรณ์ล้มเหลว: {e}"
            self._cleanup_partial_dest(dest, dest_existed_initially)
            task.status = MoveTaskStatus.FAILED
            task.error_message = err_msg
            self.task_status_changed.emit(project_name, MoveTaskStatus.FAILED.value, err_msg)
            self.task_failed.emit(project_name, err_msg)
            self.log_message.emit("ERROR", f"❌ [{project_name}] {err_msg} (โฟลเดอร์ต้นทางยังคงปลอดภัย 100%)")
            return False

        self.log_message.emit("INFO", f"✅ [{project_name}] ตรวจสอบความถูกต้องผ่าน 100% สมบูรณ์แบบ!")

        # ----------------------------------------------------
        # STAGE 4: Update THub Configuration & Workspace Metadata
        # ----------------------------------------------------
        task.status = MoveTaskStatus.UPDATING
        self.task_status_changed.emit(project_name, MoveTaskStatus.UPDATING.value, "กำลังอัปเดตการตั้งค่า THub และพาธใหม่...")

        try:
            # Publish only after full verification. Existing destination files are retained
            # in a separate recovery directory before overwrite; unrelated files stay put.
            previous = self._commit_staging(dest, destination, file_entries, task.allow_overwrite)
            if previous:
                self.log_message.emit("INFO", f"Previous destination files retained: {previous}")
            if os.path.isdir(dest):
                self._cleanup_partial_dest(dest, False)
            dest = destination
            # 1. Update hub_config.json
            cfg = ConfigManager()
            with cfg._lock:
                projects = copy.deepcopy(cfg.get_projects())
                target_proj = None
                for p in projects:
                    if p.get("name") == project_name and os.path.normcase(os.path.abspath(p.get("path", ""))) == os.path.normcase(src):
                        p["path"] = dest
                        # Update cover path if inside old workspace
                        cover_p = p.get("_cached_cover_path")
                        try:
                            local_cover = bool(cover_p) and os.path.commonpath([src, os.path.abspath(cover_p)]).lower() == src.lower()
                        except ValueError:
                            local_cover = False
                        if local_cover:
                            rel_c = os.path.relpath(cover_p, src)
                            new_cover = os.path.join(dest, rel_c)
                            if os.path.exists(new_cover):
                                p["_cached_cover_path"] = new_cover
                        target_proj = p
                        break
                if target_proj is None:
                    raise ValueError("The source project registration changed during the move")
                cfg.save_projects(projects)
    
                # 2. Update thub_project.json inside the new workspace
                meta_path = os.path.join(dest, "thub_project.json")
                if os.path.exists(meta_path):
                    try:
                        update_json_atomic(meta_path, {"project_name": project_name})
                    except Exception:
                        pass
    
                # 3. Update ProjectStorageService cache key
                cache = ProjectStorageService.get_cached_sizes()
                cached_data = cache.pop(src, None)
                if cached_data:
                    cache[dest] = cached_data
                    ProjectStorageService.save_cached_sizes(cache)

        except Exception as e:
            err_msg = f"ไม่สามารถอัปเดตการตั้งค่า THub: {e}"
            # A failed merge can leave only this worker's staging files; never clean the real destination.
            self._cleanup_partial_dest(dest, True if os.path.normcase(dest) == os.path.normcase(destination) else False)
            # Even if config fails, destination is verified. But we do NOT delete source!
            task.status = MoveTaskStatus.FAILED
            task.error_message = err_msg
            self.task_status_changed.emit(project_name, MoveTaskStatus.FAILED.value, err_msg)
            self.task_failed.emit(project_name, err_msg)
            return False

        # ----------------------------------------------------
        # STAGE 5: Clean Source (Reclaim Disk Space)
        # ----------------------------------------------------
        task.status = MoveTaskStatus.CLEANING
        self.task_status_changed.emit(project_name, MoveTaskStatus.CLEANING.value, "กำลังลบโฟลเดอร์ต้นทางเพื่อคืนพื้นที่ฮาร์ดดิสก์...")
        self.log_message.emit("INFO", f"🧹 [{project_name}] ลบต้นทาง {src} เพื่อคืนพื้นที่ {ProjectStorageService.format_size(task.total_bytes)}...")

        try:
            # Revalidate the exact source tree before deleting any original. Never
            # recursively remove a workspace: files created during the move must survive.
            current_paths = set()
            self._assert_regular_tree(src)
            for directory, dirs, files in os.walk(src):
                current_paths.update(os.path.relpath(os.path.join(directory, name), src) for name in files)
            if self._source_signature(src)[:2] != source_root_signature[:2] or current_paths != set(source_signatures):
                raise OSError("Source tree changed during the move; originals retained")
            for rel, src_file, expected_sz in file_entries:
                if self._source_signature(src_file) != source_signatures[rel]:
                    raise OSError(f"Source changed during the move: {rel}; originals retained")
            for rel, src_file, expected_sz in file_entries:
                self._wait_if_paused()
                if self._is_cancelled:
                    raise OSError("Cleanup cancelled; remaining originals retained")
                if self._source_signature(src_file) != source_signatures[rel]:
                    raise OSError(f"Source changed before deletion: {rel}")
                os.unlink(src_file)
                task.freed_bytes += expected_sz
            for rel_dir in sorted(dir_entries, key=lambda value: value.count(os.sep), reverse=True):
                try:
                    os.rmdir(os.path.join(src, rel_dir))
                except OSError:
                    pass  # New or changed files are deliberately retained.
            try:
                os.rmdir(src)
            except OSError:
                pass
        except Exception as e:
            self.log_message.emit("WARNING", f"⚠️ [{project_name}] เก็บต้นทางที่เปลี่ยนแปลงไว้: {e}")

        # Mark COMPLETED
        task.status = MoveTaskStatus.COMPLETED
        self.task_status_changed.emit(project_name, MoveTaskStatus.COMPLETED.value, f"ย้ายสำเร็จ! คืนพื้นที่ {ProjectStorageService.format_size(task.freed_bytes)}")
        self.task_completed.emit(project_name, dest, task.freed_bytes)
        self.log_message.emit("INFO", f"🎉 [{project_name}] ย้ายโปรเจกต์ไปยัง '{dest}' สำเร็จสมบูรณ์!")
        return True

    def _cleanup_partial_dest(self, dest: str, existed_initially: bool = False):
        """Safely cleans up incomplete files from destination if interrupted or failed."""
        if existed_initially or os.path.realpath(dest) not in self._owned_staging:
            self.log_message.emit("INFO", f"🛡️ โฟลเดอร์ปลายทางมีข้อมูลเดิมอยู่แล้ว จึงคงข้อมูลเดิมไว้: {dest}")
            return
        try:
            if os.path.exists(dest):
                checked = os.path.realpath(dest)
                if checked not in self._owned_staging or is_link(dest):
                    raise ValueError("Refusing to clean an unowned or linked destination")
                shutil.rmtree(checked, onerror=self._handle_remove_readonly)
                self._owned_staging.discard(checked)
                self.log_message.emit("INFO", f"🧹 ล้างข้อมูลปลายทางที่ไม่สมบูรณ์เรียบร้อย: {dest}")
        except Exception as e:
            self.log_message.emit("WARNING", f"⚠️ ล้างข้อมูลปลายทางล้มเหลว: {e}")
