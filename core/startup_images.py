"""Shared, bounded QImage decoding for cold THub Dashboard startup.

The owner supplies its BackgroundTasks manager so normal shutdown drains or
cancels image work alongside other Dashboard jobs. Only QImage crosses threads;
rounding/progress overlays and QPixmap construction stay on the GUI thread.
"""
import logging
import math
import os
from collections import OrderedDict
from PyQt6.QtCore import QObject, QThread, QSize, Qt, pyqtSignal
from PyQt6.QtGui import QImage, QImageReader
from core.qt_tasks import BackgroundTasks


class StartupImageService(QObject):
    idle = pyqtSignal()
    MAX_CACHE_ENTRIES = 128
    MAX_CACHE_BYTES = 32 * 1024 * 1024

    def __init__(self, tasks=None, parent=None):
        super().__init__(parent)
        self.tasks = tasks if tasks is not None else BackgroundTasks(self, max_workers=4)
        self._cache = OrderedDict()
        self._cache_bytes = 0
        self._waiting = {}
        self._closed = False
        self._generation = 0
        self.tasks.idle.connect(self._tasks_idle)

    @staticmethod
    def key_for(path, width, height, offset_x=0, offset_y=0, zoom=1.0):
        """Fingerprint plus exact crop/output identity; this never decodes an image."""
        width, height = max(1, int(width)), max(1, int(height))
        if width > 4096 or height > 4096:
            raise ValueError('Dashboard output dimensions exceed 4096 pixels')
        zoom = float(zoom)
        if not math.isfinite(zoom):
            zoom = 1.0
        zoom = max(1.0, min(4.0, zoom))
        offset_x = max(-100, min(100, int(offset_x)))
        offset_y = max(-100, min(100, int(offset_y)))
        normalized = os.path.normcase(os.path.abspath(path)) if path else ''
        try:
            info = os.stat(normalized)
            fingerprint = (info.st_mtime_ns, info.st_size)
        except OSError:
            fingerprint = None
        return normalized, fingerprint, width, height, offset_x, offset_y, zoom

    @property
    def pending_count(self):
        return len(self._waiting)

    @property
    def generation(self):
        return self._generation

    @property
    def is_closed(self):
        return self._closed

    @property
    def cache_bytes(self):
        return self._cache_bytes

    def is_idle(self):
        """All requested images have been delivered, including failed-image placeholders."""
        return not self._waiting

    def request(self, path, width, height, offset_x=0, offset_y=0, zoom=1.0, on_ready=None):
        """Return cached final QImage or None while pending; callbacks run on the owner thread.

        A failed/missing image is a null QImage (a completed request), allowing a
        caller to distinguish image-ready placeholders from work still running.
        Cache hits are returned directly and do not call on_ready a second time.
        """
        if QThread.currentThread() != self.thread():
            raise RuntimeError('StartupImageService.request must run on its owner thread')
        if self._closed or self.tasks.closing:
            return QImage()
        key = self.key_for(path, width, height, offset_x, offset_y, zoom)
        image = self._cache.get(key)
        if image is not None:
            self._cache.move_to_end(key)
            return image
        if key in self._waiting:
            if on_ready is not None and on_ready not in self._waiting[key]:
                self._waiting[key].append(on_ready)
            return None
        self._waiting[key] = [on_ready] if on_ready is not None else []
        generation = self._generation
        self.tasks.submit(('startup-image', id(self), generation, key), lambda: self.decode(key),
                          lambda result: self._complete(key, result, generation),
                          lambda error: self._complete(key, QImage(), generation))
        return None

    @staticmethod
    def decode(key):
        """Worker-only rectangular cover crop; no widgets, QPixmap or shared painter state."""
        path, fingerprint, width, height, offset_x, offset_y, zoom = key
        if not path or fingerprint is None or QThread.currentThread().isInterruptionRequested():
            return QImage()
        reader = QImageReader(path)
        size = reader.size()
        target = None
        if size.isValid() and size.width() > 0 and size.height() > 0:
            scale = max(width / size.width(), height / size.height()) * zoom
            target = QSize(max(width, int(size.width() * scale)), max(height, int(size.height() * scale)))
            reader.setScaledSize(target)
        image = reader.read()
        # Preserve the existing Pillow fallback for formats/plugins unavailable
        # in a packaged Qt build, while keeping its expensive work off the UI.
        if image.isNull():
            try:
                from PIL import Image
                with Image.open(path) as source:
                    source = source.convert('RGBA')
                    data = source.tobytes('raw', 'RGBA')
                    image = QImage(data, source.width, source.height, QImage.Format.Format_RGBA8888).copy()
            except Exception:
                return QImage()
        if image.isNull() or QThread.currentThread().isInterruptionRequested():
            return QImage()
        if target is None:
            scale = max(width / image.width(), height / image.height()) * zoom
            target = QSize(max(width, int(image.width() * scale)), max(height, int(image.height() * scale)))
        if image.size() != target:
            image = image.scaled(target, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
        center_x, center_y = (target.width() - width) / 2.0, (target.height() - height) / 2.0
        crop_x = max(0, min(int(center_x + (offset_x / 100.0) * center_x), target.width() - width))
        crop_y = max(0, min(int(center_y + (offset_y / 100.0) * center_y), target.height() - height))
        return image.copy(crop_x, crop_y, width, height)

    def _complete(self, key, image, generation):
        if self._closed or generation != self._generation:
            return
        callbacks = self._waiting.pop(key, [])
        previous = self._cache.pop(key, None)
        if previous is not None:
            self._cache_bytes -= previous.sizeInBytes()
        self._cache[key] = image
        self._cache_bytes += image.sizeInBytes()
        while self._cache and (len(self._cache) > self.MAX_CACHE_ENTRIES or self._cache_bytes > self.MAX_CACHE_BYTES):
            removed_key, removed = self._cache.popitem(last=False)
            self._cache_bytes -= removed.sizeInBytes()
        for callback in callbacks:
            try:
                callback(image)
            except RuntimeError:
                # A card/label may have been destroyed while its decode finished.
                pass
            except Exception:
                logging.exception('Dashboard image callback failed')
        if not self._waiting:
            self.idle.emit()

    def _tasks_idle(self):
        if self.tasks.closing:
            self._waiting.clear()
            self.idle.emit()

    def close(self):
        """Detach pending consumers; manager cancellation/draining belongs to the owner."""
        self._closed = True
        for key in list(self._waiting):
            self.tasks.cancel(('startup-image', id(self), self._generation, key))
        self._generation += 1
        self._waiting.clear()
        self._cache.clear()
        self._cache_bytes = 0

    def reopen(self):
        """Resume after an aborted window close; old-generation callbacks stay invalid."""
        self._closed = False
