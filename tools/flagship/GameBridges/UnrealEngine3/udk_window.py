"""Narrow Windows UI bridge for the verified UDK Editor window only.

Ensures:
- Target window strictly belongs to the verified UDK executable PID.
- Fails closed if another window occludes the click target or focus cannot be acquired.
- Uses DPI-aware client coordinates for screenshot and click alignment.
- Handles dynamic UDK executable paths rather than hardcoding prototype paths.
"""

from __future__ import annotations

import base64
import ctypes
import io
import os
import time
from ctypes import wintypes
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

try:
    from ue3_common import find_udk_installation
except ImportError:
    from .ue3_common import find_udk_installation

user32 = ctypes.WinDLL("user32", use_last_error=True) if os.name == "nt" else None
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True) if os.name == "nt" else None

if user32 is not None:
    user32.SetProcessDPIAware()
    user32.EnumWindows.argtypes = [ctypes.c_void_p, wintypes.LPARAM]
    user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
    user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
    user32.GetClientRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
    user32.ClientToScreen.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.POINT)]
    user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
    user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    user32.IsWindowVisible.argtypes = [wintypes.HWND]
    user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
    user32.SetForegroundWindow.argtypes = [wintypes.HWND]
    user32.GetForegroundWindow.restype = wintypes.HWND
    user32.AttachThreadInput.argtypes = [wintypes.DWORD, wintypes.DWORD, wintypes.BOOL]
    user32.SetCursorPos.argtypes = [ctypes.c_int, ctypes.c_int]
    user32.WindowFromPoint.argtypes = [wintypes.POINT]
    user32.WindowFromPoint.restype = wintypes.HWND
    user32.SendInput.argtypes = [wintypes.UINT, ctypes.c_void_p, ctypes.c_int]
    user32.SendInput.restype = wintypes.UINT

if kernel32 is not None:
    kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel32.OpenProcess.restype = wintypes.HANDLE
    kernel32.QueryFullProcessImageNameW.argtypes = [
        wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)
    ]
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]


WINDOW_TITLES = {
    "editor": "Unreal Development Kit",
    "browser": "Content Browser",
    "new": "New",
    "save": "Save Package",
}

KEYS = {
    "ENTER": 0x0D, "ESC": 0x1B, "TAB": 0x09, "SPACE": 0x20,
    "BACKSPACE": 0x08, "DELETE": 0x2E, "UP": 0x26, "DOWN": 0x28,
    "LEFT": 0x25, "RIGHT": 0x27, "HOME": 0x24, "END": 0x23,
    "A": 0x41, "C": 0x43, "S": 0x53, "V": 0x56
}


def _resolve_udk_exe(udk_exe: Optional[Union[str, Path]] = None) -> Path:
    if udk_exe:
        pe = Path(udk_exe).resolve()
        if pe.is_file():
            return pe
    detection = find_udk_installation()
    if detection["installed"] and detection["udk_exe"]:
        return Path(detection["udk_exe"])
    raise RuntimeError("UDK executable could not be resolved on this system.")


def _process_path(pid: int) -> Optional[Path]:
    if kernel32 is None:
        return None
    handle = kernel32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
    if not handle:
        return None
    try:
        buffer = ctypes.create_unicode_buffer(32768)
        length = wintypes.DWORD(len(buffer))
        if kernel32.QueryFullProcessImageNameW(handle, 0, buffer, ctypes.byref(length)):
            return Path(buffer.value)
        return None
    finally:
        kernel32.CloseHandle(handle)


def _title(hwnd: int) -> str:
    if user32 is None:
        return ""
    length = user32.GetWindowTextLengthW(hwnd)
    buffer = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buffer, len(buffer))
    return buffer.value


def find_udk_window(target: str = "editor", udk_exe: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
    """Locate a visible UDK Editor window by target role and verify process executable path."""
    if user32 is None:
        raise RuntimeError("UDK window control requires Windows OS")
    if target not in WINDOW_TITLES:
        raise ValueError(f"target must be one of {list(WINDOW_TITLES.keys())}")

    resolved_exe = _resolve_udk_exe(udk_exe)
    found: list[dict[str, Any]] = []
    callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

    def visit(hwnd: int, _unused: int) -> bool:
        if not user32.IsWindowVisible(hwnd):
            return True
        title = _title(hwnd)
        expected = WINDOW_TITLES[target]
        if (expected not in title if target == "editor" else title != expected):
            return True
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        path = _process_path(pid.value)
        if path is None or str(path).casefold() != str(resolved_exe).casefold():
            return True
        rect = wintypes.RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(rect))
        found.append({
            "handle": int(hwnd),
            "pid": pid.value,
            "title": title,
            "exe": str(path),
            "rect": {
                "left": rect.left,
                "top": rect.top,
                "right": rect.right,
                "bottom": rect.bottom,
                "width": rect.right - rect.left,
                "height": rect.bottom - rect.top,
            }
        })
        return True

    callback = callback_type(visit)
    user32.EnumWindows(callback, 0)
    if not found:
        raise RuntimeError(f"No visible UDK Editor window found for target '{target}' matching {resolved_exe.name}")
    return found[0]


def window_info(target: str = "editor", udk_exe: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
    """Return window information or structured failure if not running."""
    try:
        win = find_udk_window(target, udk_exe=udk_exe)
        return {"ok": True, "window": win}
    except Exception as exc:
        return {"ok": False, "error": str(exc), "target": target}


def window_screenshot(target: str = "editor", udk_exe: Optional[Union[str, Path]] = None) -> Tuple[Dict[str, Any], str]:
    """Capture client area of the verified UDK window as PNG base64."""
    from PIL import ImageGrab

    win = find_udk_window(target, udk_exe=udk_exe)
    hwnd = win["handle"]
    image = ImageGrab.grab(window=hwnd)
    if image.width <= 0 or image.height <= 0:
        raise RuntimeError("UDK window has invalid or minimized bounds.")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    b64 = base64.b64encode(buffer.getvalue()).decode("ascii")
    return {
        "ok": True,
        "window": win,
        "width": image.width,
        "height": image.height,
    }, b64


def _activate(hwnd: int) -> None:
    """Foreground and focus the UDK window safely."""
    user32.ShowWindow(hwnd, 9)  # SW_RESTORE
    if not user32.SetForegroundWindow(hwnd):
        foreground = user32.GetForegroundWindow()
        foreground_thread = user32.GetWindowThreadProcessId(foreground, None)
        current_thread = kernel32.GetCurrentThreadId()
        if foreground_thread and user32.AttachThreadInput(current_thread, foreground_thread, True):
            try:
                user32.SetForegroundWindow(hwnd)
            finally:
                user32.AttachThreadInput(current_thread, foreground_thread, False)
    if user32.GetForegroundWindow() != hwnd:
        raise RuntimeError("Could not focus the UDK Editor window. Bring UDK to foreground manually.")
    time.sleep(0.15)


def window_click(
    x: int,
    y: int,
    button: str = "left",
    target: str = "editor",
    udk_exe: Optional[Union[str, Path]] = None
) -> Dict[str, Any]:
    """Click at client-relative coordinates inside the verified UDK window with occlusion check."""
    if button not in {"left", "right"}:
        raise ValueError("button must be 'left' or 'right'")
    resolved_exe = _resolve_udk_exe(udk_exe)
    win = find_udk_window(target, udk_exe=resolved_exe)
    hwnd = win["handle"]
    client = wintypes.RECT()
    user32.GetClientRect(hwnd, ctypes.byref(client))
    if not (0 <= x < client.right and 0 <= y < client.bottom):
        raise ValueError(
            f"Click coordinates ({x}, {y}) outside UDK client area ({client.right}x{client.bottom})"
        )
    point = wintypes.POINT(x, y)
    user32.ClientToScreen(hwnd, ctypes.byref(point))
    _activate(hwnd)
    
    # Occlusion check: ensure window under cursor belongs to UDK
    target_hwnd = user32.WindowFromPoint(point)
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(target_hwnd, ctypes.byref(pid))
    path = _process_path(pid.value)
    if path is None or str(path).casefold() != str(resolved_exe).casefold():
        raise RuntimeError(
            f"Another application ({path.name if path else 'Unknown'}) occludes the UDK click target at ({x}, {y}). "
            "Please bring UDK Editor to the front."
        )

    user32.SetCursorPos(point.x, point.y)
    down, up = (0x0002, 0x0004) if button == "left" else (0x0008, 0x0010)
    user32.mouse_event(down, 0, 0, 0, 0)
    user32.mouse_event(up, 0, 0, 0, 0)
    return {"ok": True, "window": win, "x": x, "y": y, "button": button}


def window_key(
    key: str,
    ctrl: bool = False,
    shift: bool = False,
    alt: bool = False,
    target: str = "editor",
    udk_exe: Optional[Union[str, Path]] = None
) -> Dict[str, Any]:
    """Send a restricted key or key combination to the verified UDK window."""
    key_upper = key.upper()
    if key_upper not in KEYS:
        raise ValueError(f"Unsupported key '{key}'. Allowed keys: {sorted(KEYS.keys())}")
    win = find_udk_window(target, udk_exe=udk_exe)
    _activate(win["handle"])
    modifiers = [(0x11, ctrl), (0x10, shift), (0x12, alt)]
    pressed = [vk for vk, enabled in modifiers if enabled]
    for vk in pressed:
        user32.keybd_event(vk, 0, 0, 0)
    user32.keybd_event(KEYS[key_upper], 0, 0, 0)
    user32.keybd_event(KEYS[key_upper], 0, 0x0002, 0)
    for vk in reversed(pressed):
        user32.keybd_event(vk, 0, 0x0002, 0)
    return {
        "ok": True,
        "window": win,
        "key": key_upper,
        "ctrl": ctrl,
        "shift": shift,
        "alt": alt,
    }


class _KeyInput(ctypes.Structure):
    _fields_ = [
        ("vk", wintypes.WORD),
        ("scan", wintypes.WORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("extra", ctypes.c_size_t),
    ]


class _InputUnion(ctypes.Union):
    _fields_ = [("ki", _KeyInput), ("padding", ctypes.c_byte * 32)]


class _Input(ctypes.Structure):
    _fields_ = [("type", wintypes.DWORD), ("data", _InputUnion)]


def window_type_text(
    value: str,
    target: str = "editor",
    udk_exe: Optional[Union[str, Path]] = None
) -> Dict[str, Any]:
    """Type Unicode text into the focused UDK Editor control without modifying the clipboard."""
    if not value or len(value) > 10000:
        raise ValueError("Text length must be between 1 and 10000 characters.")
    if any(ord(char) < 32 for char in value):
        raise ValueError("Text must not contain control characters (< ASCII 32).")
    win = find_udk_window(target, udk_exe=udk_exe)
    _activate(win["handle"])

    encoded = value.encode("utf-16-le")
    units = [int.from_bytes(encoded[i:i + 2], "little") for i in range(0, len(encoded), 2)]
    for unit in units:
        for flags in (0x0004, 0x0004 | 0x0002):  # KEYEVENTF_UNICODE, KEYEVENTF_KEYUP
            item = _Input()
            item.type = 1  # INPUT_KEYBOARD
            item.data.ki = _KeyInput(0, unit, flags, 0, 0)
            if user32.SendInput(1, ctypes.byref(item), ctypes.sizeof(item)) != 1:
                raise RuntimeError("Windows rejected Unicode SendInput to UDK window.")
    return {"ok": True, "window": win, "characters": len(value)}
