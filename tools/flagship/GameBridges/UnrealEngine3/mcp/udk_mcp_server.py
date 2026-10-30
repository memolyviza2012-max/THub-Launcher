#!/usr/bin/env python3
"""Model Context Protocol (MCP) Server for Unreal Development Kit (UDK / UE3).

Provides:
- Dynamic discovery of UDK installation without hardcoding prototype machine paths.
- Read-only commandlet execution with isolated logs.
- UE3 package binary header inspection (FileVersion, LicenseeVersion, Stock UDK compatibility).
- Window targeting with process verification and occlusion protection.
- Safe execution boundaries preventing arbitrary code execution or file overwrite.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add parent directory to sys.path so we can import ue3_common and udk_window
CURRENT_DIR = Path(__file__).resolve().parent
PARENT_DIR = CURRENT_DIR.parent
if str(PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(PARENT_DIR))

try:
    import udk_window
    from ue3_common import (
        find_udk_installation,
        get_running_udk_processes,
        inspect_ue3_package_header,
        validate_package_path,
    )
except ImportError:
    from . import udk_window
    from .ue3_common import (
        find_udk_installation,
        get_running_udk_processes,
        inspect_ue3_package_header,
        validate_package_path,
    )

SERVER_NAME = "udk-mcp-editor"
SERVER_VERSION = "1.0.0"
SUPPORTED_PROTOCOLS = {"2024-11-05", "2025-03-26", "2025-06-18"}
COMMANDLET_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_.]{0,79}$")
SUCCESS_LINE_RE = re.compile(r"\bSuccess - \d+ error\(s\)", re.IGNORECASE)


def _hidden_flags() -> int:
    return getattr(subprocess, "CREATE_NO_WINDOW", 0)


class UDKBridgeContext:
    """Encapsulates UDK runtime context, configuration, and allowed boundaries."""

    def __init__(
        self,
        custom_udk_root: Optional[Path] = None,
        custom_workspace_roots: Optional[List[Path]] = None,
    ):
        self.udk_info = find_udk_installation(custom_root=custom_udk_root)
        self.udk_root = Path(self.udk_info["udk_root"]) if self.udk_info["udk_root"] else None
        self.udk_exe = Path(self.udk_info["udk_exe"]) if self.udk_info["udk_exe"] else None

        # Build allowed package roots
        self.allowed_roots: List[Path] = []
        if self.udk_root and self.udk_root.is_dir():
            self.allowed_roots.append(self.udk_root.resolve())

        if custom_workspace_roots:
            for root in custom_workspace_roots:
                p = Path(root).resolve()
                if p.is_dir():
                    self.allowed_roots.append(p)

        # Environment workspace root
        env_ws = os.environ.get("WORKSPACE_ROOT") or os.environ.get("MOD_ROOT")
        if env_ws:
            p_ws = Path(env_ws).resolve()
            if p_ws.is_dir() and p_ws not in self.allowed_roots:
                self.allowed_roots.append(p_ws)

        # Default Mod_Workspace if present
        default_mod_ws = Path(r"E:\Mod_Workspace")
        if default_mod_ws.is_dir() and default_mod_ws not in self.allowed_roots:
            self.allowed_roots.append(default_mod_ws.resolve())

    def run_commandlet(self, commandlet: str, arguments: List[str], timeout: int = 90) -> Dict[str, Any]:
        """Execute a read-only UDK commandlet in a separate hidden process."""
        if not self.udk_exe or not self.udk_exe.is_file():
            raise RuntimeError(
                f"UDK executable not found or not configured: {self.udk_exe}. "
                "Ensure UDK is installed or set UDK_ROOT / UDK_EXE environment variable."
            )

        if not COMMANDLET_NAME_RE.fullmatch(commandlet):
            raise ValueError(f"Invalid commandlet name '{commandlet}'.")

        logs_dir = self.udk_root / "UDKGame" / "Logs" if self.udk_root else self.udk_exe.parents[2] / "UDKGame" / "Logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        log_name = f"THub_UDK_{uuid.uuid4().hex[:12]}.log"
        log_path = logs_dir / log_name

        argv = [
            str(self.udk_exe),
            commandlet,
            *arguments,
            "-unattended",
            "-nopause",
            f"-log={log_name}",
        ]

        try:
            process = subprocess.run(
                argv,
                cwd=self.udk_exe.parent,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout,
                creationflags=_hidden_flags(),
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(f"UDK commandlet '{commandlet}' timed out after {timeout}s.") from exc

        if not log_path.is_file():
            stderr_tail = process.stderr[-1000:] if process.stderr else "No stderr output"
            raise RuntimeError(
                f"UDK did not create its commandlet log (exit code {process.returncode}): {stderr_tail}"
            )

        log_content = log_path.read_text(encoding="utf-8-sig", errors="replace")
        success = (process.returncode == 0) and bool(SUCCESS_LINE_RE.search(log_content))

        return {
            "ok": success,
            "exit_code": process.returncode,
            "commandlet": commandlet,
            "arguments": arguments,
            "log_path": str(log_path),
            "log": log_content,
        }

    def relevant_log(self, log: str, limit: int = 30000) -> str:
        """Strip engine startup preamble and return relevant commandlet log tail."""
        lines = log.splitlines()
        start = next(
            (index for index, line in enumerate(lines) if "Executing Class " in line or "Log: Executing" in line),
            0,
        )
        tail = "\n".join(lines[start:])
        return tail[-limit:] if len(tail) > limit else tail


# Global server context
_CONTEXT: Optional[UDKBridgeContext] = None


def get_context() -> UDKBridgeContext:
    global _CONTEXT
    if _CONTEXT is None:
        _CONTEXT = UDKBridgeContext()
    return _CONTEXT


# ---------------------------------------------------------------------------
# Tool Implementations
# ---------------------------------------------------------------------------

def tool_udk_status() -> Dict[str, Any]:
    ctx = get_context()
    running = get_running_udk_processes(ctx.udk_exe)
    return {
        "ok": True,
        "installed": ctx.udk_info.get("installed", False),
        "udk_version": ctx.udk_info.get("udk_version", "Unknown"),
        "root": ctx.udk_info.get("udk_root"),
        "executable": ctx.udk_info.get("udk_exe"),
        "arch": ctx.udk_info.get("arch"),
        "discovery_source": ctx.udk_info.get("discovery_source"),
        "running_udk_processes": running,
        "running_count": len(running),
        "allowed_roots": [str(r) for r in ctx.allowed_roots],
        "connection_type": "independent commandlet process & Win32 target-verified window bridge",
        "package_writes_enabled": False,
    }


def tool_udk_inspect_package(path: str) -> Dict[str, Any]:
    """Inspect UE3 binary package header for LicenseeVersion & Stock UDK compatibility."""
    ctx = get_context()
    pkg_path = validate_package_path(path, ctx.allowed_roots)
    return inspect_ue3_package_header(pkg_path)


def tool_udk_package_info(path: str, section: str = "exports", force: bool = False) -> Dict[str, Any]:
    """Inspect a package using UDK's PkgInfo commandlet, checking header compatibility first."""
    if section not in {"summary", "exports", "imports", "names", "all"}:
        raise ValueError("section must be one of: summary, exports, imports, names, all")

    ctx = get_context()
    pkg_path = validate_package_path(path, ctx.allowed_roots)

    # Preflight check package header
    header = inspect_ue3_package_header(pkg_path)
    if not header.get("ok"):
        return header

    if not header.get("compatible_with_stock_udk") and not force:
        return {
            "ok": False,
            "error": "Package incompatibility detected before PkgInfo execution.",
            "header": header,
            "caution": header.get("caution"),
            "advice": (
                "Stock UDK cannot load this cooked licensee package directly. "
                "Use a game-specific unpacker (e.g. dishonored-toolkit) or pass force=True to attempt anyway."
            ),
        }

    flags = [] if section == "summary" else [f"-{section}"]
    if section == "exports":
        flags.append("-simple")

    run = ctx.run_commandlet("UnrealEd.PkgInfo", [str(pkg_path), *flags], timeout=120)
    return {
        "ok": run["ok"],
        "package": str(pkg_path),
        "section": section,
        "header": header,
        "output": ctx.relevant_log(run["log"], 60000),
        "log_path": run["log_path"],
    }


def tool_udk_list_commandlets() -> Dict[str, Any]:
    ctx = get_context()
    run = ctx.run_commandlet("Core.HelpCommandlet", ["list"])
    entries = []
    for line in run["log"].splitlines():
        match = re.search(r"Log:\s+([A-Za-z][A-Za-z0-9_.]+)\s+-\s*(.*)$", line)
        if match and "." in match.group(1):
            entries.append({"name": match.group(1), "description": match.group(2).strip()})
    return {
        "ok": run["ok"],
        "count": len(entries),
        "commandlets": entries,
        "log_path": run["log_path"],
        "diagnostics": ctx.relevant_log(run["log"], 3000) if not run["ok"] else "",
    }


def tool_udk_commandlet_help(name: str) -> Dict[str, Any]:
    ctx = get_context()
    if not COMMANDLET_NAME_RE.fullmatch(name):
        raise ValueError(f"Invalid commandlet name: {name}")
    run = ctx.run_commandlet("Core.HelpCommandlet", [name])
    return {
        "ok": run["ok"],
        "name": name,
        "output": ctx.relevant_log(run["log"]),
        "log_path": run["log_path"],
    }


def tool_udk_window_info(target: str = "editor") -> Dict[str, Any]:
    ctx = get_context()
    return udk_window.window_info(target=target, udk_exe=ctx.udk_exe)


def tool_udk_window_screenshot(target: str = "editor") -> Tuple[Dict[str, Any], str]:
    ctx = get_context()
    return udk_window.window_screenshot(target=target, udk_exe=ctx.udk_exe)


def tool_udk_window_click(x: int, y: int, button: str = "left", target: str = "editor") -> Dict[str, Any]:
    ctx = get_context()
    return udk_window.window_click(x=x, y=y, button=button, target=target, udk_exe=ctx.udk_exe)


def tool_udk_window_key(
    key: str, ctrl: bool = False, shift: bool = False, alt: bool = False, target: str = "editor"
) -> Dict[str, Any]:
    ctx = get_context()
    return udk_window.window_key(key=key, ctrl=ctrl, shift=shift, alt=alt, target=target, udk_exe=ctx.udk_exe)


def tool_udk_window_type_text(text: str, target: str = "editor") -> Dict[str, Any]:
    ctx = get_context()
    return udk_window.window_type_text(value=text, target=target, udk_exe=ctx.udk_exe)


TOOLS_DEFINITIONS: List[Dict[str, Any]] = [
    {
        "name": "udk_status",
        "description": "Check the installed UDK executable, version, discovery source, running processes, and allowed workspace boundaries. The bridge runs isolated headless commandlets or safe window automation; it never writes to game directories.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "udk_inspect_package",
        "description": "Inspect Unreal Engine 3 package binary header (FileVersion, LicenseeVersion, endianness, Stock UDK compatibility). Essential preflight before attempting to open with Stock UDK.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to .upk, .u, or .udk package within allowed workspace roots"}
            },
            "required": ["path"],
            "additionalProperties": False,
        },
    },
    {
        "name": "udk_package_info",
        "description": "Inspect a package using UDK's PkgInfo commandlet (read-only). Performs preflight header checks to block incompatible licensee packages (e.g. Dishonored licensee version 30).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to package file within allowed roots"},
                "section": {"type": "string", "enum": ["summary", "exports", "imports", "names", "all"], "default": "exports"},
                "force": {"type": "boolean", "description": "Bypass licensee incompatibility warning", "default": False},
            },
            "required": ["path"],
            "additionalProperties": False,
        },
    },
    {
        "name": "udk_list_commandlets",
        "description": "Query UDK's internal commandlet catalog (read-only).",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "udk_commandlet_help",
        "description": "Query usage parameters of a specific UDK commandlet (read-only).",
        "inputSchema": {
            "type": "object",
            "properties": {"name": {"type": "string", "description": "Commandlet class name (e.g. 'UnrealEd.PkgInfo')"}},
            "required": ["name"],
            "additionalProperties": False,
        },
    },
    {
        "name": "udk_window_info",
        "description": "Locate a visible UDK Editor window, verifying that its process matches the verified UDK executable.",
        "inputSchema": {
            "type": "object",
            "properties": {"target": {"type": "string", "enum": ["editor", "browser", "new", "save"], "default": "editor"}},
            "additionalProperties": False,
        },
    },
    {
        "name": "udk_window_screenshot",
        "description": "Capture the visible UDK Editor window client area as a PNG image in DPI-aware coordinates.",
        "inputSchema": {
            "type": "object",
            "properties": {"target": {"type": "string", "enum": ["editor", "browser", "new", "save"], "default": "editor"}},
            "additionalProperties": False,
        },
    },
    {
        "name": "udk_window_click",
        "description": "Click within the verified UDK window using DPI-aware client coordinates, with target process and occlusion verification.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "x": {"type": "integer", "minimum": 0},
                "y": {"type": "integer", "minimum": 0},
                "button": {"type": "string", "enum": ["left", "right"], "default": "left"},
                "target": {"type": "string", "enum": ["editor", "browser", "new", "save"], "default": "editor"},
            },
            "required": ["x", "y"],
            "additionalProperties": False,
        },
    },
    {
        "name": "udk_window_key",
        "description": "Send a verified key or shortcut to the UDK Editor window.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "Key name (e.g. ENTER, ESC, TAB, S, A, C, V)"},
                "ctrl": {"type": "boolean", "default": False},
                "shift": {"type": "boolean", "default": False},
                "alt": {"type": "boolean", "default": False},
                "target": {"type": "string", "enum": ["editor", "browser", "new", "save"], "default": "editor"},
            },
            "required": ["key"],
            "additionalProperties": False,
        },
    },
    {
        "name": "udk_window_type_text",
        "description": "Type Unicode text into the focused UDK Editor control without replacing or modifying the Windows clipboard.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "minLength": 1, "maxLength": 10000},
                "target": {"type": "string", "enum": ["editor", "browser", "new", "save"], "default": "editor"},
            },
            "required": ["text"],
            "additionalProperties": False,
        },
    },
]

HANDLERS = {
    "udk_status": lambda args: tool_udk_status(),
    "udk_inspect_package": lambda args: tool_udk_inspect_package(args["path"]),
    "udk_package_info": lambda args: tool_udk_package_info(args["path"], args.get("section", "exports"), args.get("force", False)),
    "udk_list_commandlets": lambda args: tool_udk_list_commandlets(),
    "udk_commandlet_help": lambda args: tool_udk_commandlet_help(args["name"]),
    "udk_window_info": lambda args: tool_udk_window_info(args.get("target", "editor")),
    "udk_window_click": lambda args: tool_udk_window_click(args["x"], args["y"], args.get("button", "left"), args.get("target", "editor")),
    "udk_window_key": lambda args: tool_udk_window_key(args["key"], args.get("ctrl", False), args.get("shift", False), args.get("alt", False), args.get("target", "editor")),
    "udk_window_type_text": lambda args: tool_udk_window_type_text(args["text"], args.get("target", "editor")),
}


def _result(request_id: Any, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _error(request_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def handle_message(message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    request_id = message.get("id")
    method = message.get("method")
    if request_id is None:
        return None  # Notifications have no response

    if method == "initialize":
        requested = message.get("params", {}).get("protocolVersion", "2025-03-26")
        protocol = requested if requested in SUPPORTED_PROTOCOLS else "2025-03-26"
        return _result(
            request_id,
            {
                "protocolVersion": protocol,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            },
        )

    if method == "ping":
        return _result(request_id, {})

    if method == "tools/list":
        return _result(request_id, {"tools": TOOLS_DEFINITIONS})

    if method == "tools/call":
        params = message.get("params", {})
        name = params.get("name")
        args = params.get("arguments") or {}

        if name == "udk_window_screenshot":
            try:
                metadata, png_b64 = tool_udk_window_screenshot(args.get("target", "editor"))
                return _result(
                    request_id,
                    {
                        "content": [
                            {"type": "image", "data": png_b64, "mimeType": "image/png"},
                            {"type": "text", "text": json.dumps(metadata, ensure_ascii=False)},
                        ],
                        "isError": False,
                    },
                )
            except Exception as exc:
                return _result(
                    request_id,
                    {
                        "content": [{"type": "text", "text": json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)}],
                        "isError": True,
                    },
                )

        if name not in HANDLERS:
            return _error(request_id, -32602, f"Unknown tool: '{name}'")

        try:
            data = HANDLERS[name](args)
            payload = json.dumps(data, ensure_ascii=False)
            return _result(
                request_id,
                {"content": [{"type": "text", "text": payload}], "isError": not data.get("ok", True)},
            )
        except Exception as exc:
            err_dict = {"ok": False, "error": str(exc), "tool": name}
            return _result(
                request_id,
                {"content": [{"type": "text", "text": json.dumps(err_dict, ensure_ascii=False)}], "isError": True},
            )

    return _error(request_id, -32601, f"Unsupported method: {method}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--udk-root", type=Path, help="Override path to UDK root directory")
    parser.add_argument("--workspace-root", type=Path, action="append", help="Allow additional workspace root")
    args = parser.parse_args()

    global _CONTEXT
    _CONTEXT = UDKBridgeContext(
        custom_udk_root=args.udk_root,
        custom_workspace_roots=args.workspace_root,
    )

    sys.stderr.write(f"[{SERVER_NAME}] Starting UDK MCP Server (v{SERVER_VERSION})...\n")
    sys.stderr.write(f"[{SERVER_NAME}] UDK Root: {_CONTEXT.udk_root}\n")
    sys.stderr.write(f"[{SERVER_NAME}] Allowed roots: {[str(r) for r in _CONTEXT.allowed_roots]}\n")
    sys.stderr.flush()

    for line in sys.stdin.buffer:
        try:
            message = json.loads(line)
            response = handle_message(message)
        except (json.JSONDecodeError, TypeError) as exc:
            response = _error(None, -32700, f"Parse error: {exc}")
        if response is not None:
            sys.stdout.buffer.write((json.dumps(response, ensure_ascii=False) + "\n").encode("utf-8"))
            sys.stdout.buffer.flush()


if __name__ == "__main__":
    main()
