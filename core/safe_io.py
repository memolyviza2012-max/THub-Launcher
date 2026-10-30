"""Atomic THub metadata writes; never repair unreadable metadata by overwriting it."""
import json
import os
import tempfile
import threading
from functools import wraps

_metadata_lock = threading.RLock()

def _serialized(function):
    @wraps(function)
    def locked(*args, **kwargs):
        with _metadata_lock:
            return function(*args, **kwargs)
    return locked


@_serialized
def write_json_atomic(path, data):
    directory = os.path.dirname(os.path.abspath(path))
    os.makedirs(directory, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.thub-', suffix='.tmp', dir=directory)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as handle:
            json.dump(data, handle, indent=4, ensure_ascii=False)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


@_serialized
def update_json_atomic(path, updates):
    data = {}
    if os.path.exists(path):
        with open(path, encoding='utf-8-sig') as handle:
            data = json.load(handle)
        if not isinstance(data, dict):
            raise ValueError(f'Invalid metadata object: {path}')
    data.update(updates)
    write_json_atomic(path, data)
