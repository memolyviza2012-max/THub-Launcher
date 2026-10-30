"""Owned Qt tasks with latest-request-wins results and cooperative shutdown."""
from PyQt6.QtCore import QObject, QThread, pyqtSignal, pyqtSlot


class TaskThread(QThread):
    returned = pyqtSignal(object)
    failed = pyqtSignal(str)

    def __init__(self, function):
        super().__init__()
        self.function = function

    def run(self):
        try:
            value = self.function()
            if not self.isInterruptionRequested():
                self.returned.emit(value)
        except Exception as exc:
            if not self.isInterruptionRequested():
                self.failed.emit(str(exc))


class BackgroundTasks(QObject):
    """Keep workers alive until finished; dispatch callbacks only on the GUI thread."""
    idle = pyqtSignal()
    _live = set()

    def __init__(self, parent=None, max_workers=4):
        super().__init__(parent)
        self.jobs = {}
        self.pending = {}
        self.closing = False
        self.max_workers = max(1, int(max_workers))
        self._running = set()

    def submit(self, key, function, success=None, failure=None):
        if self.closing:
            return
        if key in self.jobs:
            if key not in self._running:
                # Replace a queued request before starting its thread at all.
                self.jobs[key][0].function = function
                self.jobs[key] = (self.jobs[key][0], success, failure)
                return
            self.pending[key] = (function, success, failure)
            self.jobs[key][0].requestInterruption()
            return
        worker = TaskThread(function)
        worker.task_key = key
        self.jobs[key] = (worker, success, failure)
        worker.returned.connect(self._returned)
        worker.failed.connect(self._failed)
        worker.finished.connect(self._finished)
        self._start_available()

    def _start_available(self):
        if self.closing:
            return
        for key, (worker, *_callbacks) in list(self.jobs.items()):
            if len(self._running) >= self.max_workers:
                break
            if key not in self._running:
                self._running.add(key)
                self._live.add(worker)
                worker.start()

    def run_task(self, function, callback=None, err_callback=None, key=None):
        """Universal convenience method: executes function in worker thread with optional callbacks."""
        task_key = key or f"task_{id(function)}"
        self.submit(task_key, function, success=callback, failure=err_callback)


    def _entry(self):
        worker = self.sender()
        key = getattr(worker, 'task_key', None)
        entry = self.jobs.get(key)
        return (key, entry) if entry and entry[0] is worker else (None, None)

    @pyqtSlot(object)
    def _returned(self, value):
        key, entry = self._entry()
        if (entry and key not in self.pending and not self.closing
                and not entry[0].isInterruptionRequested() and entry[1]):
            entry[1](value)

    @pyqtSlot(str)
    def _failed(self, message):
        key, entry = self._entry()
        if (entry and key not in self.pending and not self.closing
                and not entry[0].isInterruptionRequested() and entry[2]):
            entry[2](message)

    @pyqtSlot()
    def _finished(self):
        key, entry = self._entry()
        if not entry:
            return
        self.jobs.pop(key)
        self._running.discard(key)
        self._live.discard(entry[0])
        entry[0].deleteLater()
        pending = self.pending.pop(key, None)
        if pending and not self.closing:
            self.submit(key, *pending)
        self._start_available()
        if not self.jobs:
            self.idle.emit()

    def busy(self):
        return bool(self.jobs)

    def cancel(self, key):
        """Cancel one owned task without cancelling unrelated saves on this manager."""
        self.pending.pop(key, None)
        entry = self.jobs.get(key)
        if not entry:
            return
        if key in self._running:
            entry[0].requestInterruption()
        else:
            self.jobs.pop(key)
            entry[0].deleteLater()
            self._start_available()
        if not self.jobs:
            self.idle.emit()

    def cancel_all(self):
        self.closing = True
        self.pending.clear()
        for key in list(self.jobs):
            worker = self.jobs[key][0]
            if key in self._running:
                worker.requestInterruption()
            else:
                self.jobs.pop(key)
                worker.deleteLater()
        if not self.jobs:
            self.idle.emit()


class TaskDialogMixin:
    """Defer dialog destruction while owned work finishes, without blocking Qt."""
    def done(self, result):
        tasks = getattr(self, 'tasks', None)
        if tasks and tasks.busy():
            self._deferred_result = result
            if not getattr(self, '_waiting_for_tasks', False):
                self._waiting_for_tasks = True
                self.setEnabled(False)
                tasks.idle.connect(self._finish_deferred_close)
                tasks.cancel_all()
            return
        super().done(result)

    def _finish_deferred_close(self):
        self.setEnabled(True)
        super().done(self._deferred_result)
