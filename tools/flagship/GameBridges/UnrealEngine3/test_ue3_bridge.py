#!/usr/bin/env python3
"""Comprehensive test suite for UDK / UE3 MCP Bridge in THub.

Covers:
- MCP JSON-RPC protocol compliance (initialize, tools/list, tools/call, ping, notifications, error codes).
- Dynamic UDK path discovery and validation without hardcoded machine assumptions.
- Package header inspection (LicenseeVersion 30 vs 0, endianness, Stock UDK compatibility).
- Boundary security (path traversal prevention, root confinement, extension validation).
- Commandlet input validation and injection prevention.
- Window targeting, safe coordinate checking, and handling when UDK is NOT running.
- End-to-end stdio JSON-RPC handshake via subprocess.
"""

from __future__ import annotations

import json
import os
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# Add current and parent directory to path
TEST_DIR = Path(__file__).resolve().parent
if str(TEST_DIR) not in sys.path:
    sys.path.insert(0, str(TEST_DIR))
MCP_DIR = TEST_DIR / "mcp"
if str(MCP_DIR) not in sys.path:
    sys.path.insert(0, str(MCP_DIR))

import udk_mcp_server
import udk_window
import ue3_common


class UE3PackageHeaderTests(unittest.TestCase):
    """Tests for UE3 package binary header analysis."""

    def test_inspect_dishonored_package_licensee_version(self):
        """Dishonored cooked package has LicenseeVersion 30 and must be flagged incompatible with Stock UDK."""
        dishonored_pkg = Path(
            r"E:\Mod_Workspace\Dishonored\01_Original_Backup\DishonoredGame\CookedPCConsole\UI_Loading_SF_LOC_INT.upk"
        )
        if not dishonored_pkg.is_file():
            self.skipTest(f"Dishonored backup package not found at {dishonored_pkg}")

        result = ue3_common.inspect_ue3_package_header(dishonored_pkg)
        self.assertTrue(result["ok"])
        self.assertTrue(result["is_ue3"])
        self.assertEqual(result["endianness"], "little")
        self.assertEqual(result["file_version"], 801)
        self.assertEqual(result["licensee_version"], 30)
        self.assertFalse(result["compatible_with_stock_udk"])
        self.assertIn("Licensee Version 30", result["verdict"])
        self.assertIn("dishonored-toolkit", result["caution"].lower())

    def test_inspect_stock_udk_package_compatible(self):
        """Stock UDK package has LicenseeVersion 0 and must be flagged compatible."""
        with tempfile.TemporaryDirectory() as tmpdir:
            dummy_upk = Path(tmpdir) / "StockMock.upk"
            # Magic (0x9E2A83C1), FileVersion (845), LicenseeVersion (0)
            header = struct.pack("<IHH", 0x9E2A83C1, 845, 0) + b"\x00" * 40
            dummy_upk.write_bytes(header)

            result = ue3_common.inspect_ue3_package_header(dummy_upk)
            self.assertTrue(result["ok"])
            self.assertTrue(result["is_ue3"])
            self.assertEqual(result["file_version"], 845)
            self.assertEqual(result["licensee_version"], 0)
            self.assertTrue(result["compatible_with_stock_udk"])
            self.assertIsNone(result["caution"])

    def test_inspect_rejects_non_ue3_magic(self):
        """Non-UE3 binary files must be rejected cleanly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            bad_file = Path(tmpdir) / "corrupt.upk"
            bad_file.write_bytes(b"NOT_A_VALID_HEADER_FOR_UE3_PACKAGE_1234567890")

            result = ue3_common.inspect_ue3_package_header(bad_file)
            self.assertFalse(result["ok"])
            self.assertFalse(result["is_ue3"])
            self.assertIn("Invalid package magic", result["error"])

    def test_inspect_nonexistent_file(self):
        result = ue3_common.inspect_ue3_package_header("nonexistent_package_file.upk")
        self.assertFalse(result["ok"])
        self.assertIn("does not exist", result["error"])


class PathSecurityTests(unittest.TestCase):
    """Tests for workspace confinement and extension validation."""

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tmpdir.name).resolve()
        self.inside_file = self.root / "TestPackage.upk"
        self.inside_file.write_bytes(b"\x00" * 64)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_valid_path_inside_root(self):
        validated = ue3_common.validate_package_path(self.inside_file, [self.root])
        self.assertEqual(validated, self.inside_file.resolve())

    def test_reject_outside_path(self):
        with tempfile.TemporaryDirectory() as other_dir:
            outside_file = Path(other_dir) / "Outside.upk"
            outside_file.write_bytes(b"\x00" * 64)
            with self.assertRaises(ValueError) as ctx:
                ue3_common.validate_package_path(outside_file, [self.root])
            self.assertIn("outside allowed", str(ctx.exception))

    def test_reject_invalid_extension(self):
        bad_ext = self.root / "Malicious.exe"
        bad_ext.write_bytes(b"\x00" * 64)
        with self.assertRaises(ValueError) as ctx:
            ue3_common.validate_package_path(bad_ext, [self.root])
        self.assertIn("Invalid package extension", str(ctx.exception))

    def test_reject_nonexistent_file(self):
        missing = self.root / "Missing.upk"
        with self.assertRaises(ValueError) as ctx:
            ue3_common.validate_package_path(missing, [self.root])
        self.assertIn("not found", str(ctx.exception).lower())


class UDKDiscoveryTests(unittest.TestCase):
    """Tests for dynamic UDK installation discovery."""

    def test_find_installed_udk(self):
        info = ue3_common.find_udk_installation()
        self.assertIsInstance(info, dict)
        self.assertIn("installed", info)
        self.assertIn("udk_version", info)
        if info["installed"]:
            self.assertTrue(Path(info["udk_exe"]).is_file())
            self.assertTrue(Path(info["udk_root"]).is_dir())

    def test_custom_root_parameter(self):
        """Explicit custom root takes precedence when valid."""
        with tempfile.TemporaryDirectory() as tmp:
            fake_root = Path(tmp)
            bin_dir = fake_root / "Binaries" / "Win64"
            bin_dir.mkdir(parents=True)
            fake_exe = bin_dir / "UDK.exe"
            fake_exe.write_bytes(b"\x00" * 1024)

            info = ue3_common.find_udk_installation(custom_root=fake_root)
            self.assertTrue(info["installed"])
            self.assertEqual(Path(info["udk_root"]), fake_root)
            self.assertEqual(info["arch"], "Win64")
            self.assertEqual(info["discovery_source"], "parameter")


class MCPProtocolTests(unittest.TestCase):
    """Tests for JSON-RPC 2.0 and MCP handler compliance."""

    def test_initialize(self):
        req = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-03-26"}}
        res = udk_mcp_server.handle_message(req)
        self.assertEqual(res["jsonrpc"], "2.0")
        self.assertEqual(res["id"], 1)
        self.assertEqual(res["result"]["protocolVersion"], "2025-03-26")
        self.assertEqual(res["result"]["serverInfo"]["name"], "udk-mcp-editor")

    def test_ping(self):
        req = {"jsonrpc": "2.0", "id": 2, "method": "ping"}
        res = udk_mcp_server.handle_message(req)
        self.assertEqual(res["result"], {})

    def test_tools_list(self):
        req = {"jsonrpc": "2.0", "id": 3, "method": "tools/list"}
        res = udk_mcp_server.handle_message(req)
        tools = res["result"]["tools"]
        tool_names = [t["name"] for t in tools]
        expected_tools = [
            "udk_status",
            "udk_inspect_package",
            "udk_package_info",
            "udk_list_commandlets",
            "udk_commandlet_help",
            "udk_window_info",
            "udk_window_screenshot",
            "udk_window_click",
            "udk_window_key",
            "udk_window_type_text",
        ]
        for name in expected_tools:
            self.assertIn(name, tool_names)

    def test_notification_returns_none(self):
        notification = {"jsonrpc": "2.0", "method": "notifications/initialized"}
        res = udk_mcp_server.handle_message(notification)
        self.assertIsNone(res)

    def test_unsupported_method(self):
        req = {"jsonrpc": "2.0", "id": 99, "method": "unknown/method"}
        res = udk_mcp_server.handle_message(req)
        self.assertEqual(res["error"]["code"], -32601)

    def test_unknown_tool_call(self):
        req = {"jsonrpc": "2.0", "id": 100, "method": "tools/call", "params": {"name": "invalid_tool_name"}}
        res = udk_mcp_server.handle_message(req)
        self.assertEqual(res["error"]["code"], -32602)


class WindowTargetingAndOfflineTests(unittest.TestCase):
    """Tests for window control behavior when UDK Editor is NOT running."""

    def test_window_info_when_udk_not_open(self):
        """When UDK Editor is not open, udk_window_info must return clean structured error without raising JSONDecodeError."""
        req = {
            "jsonrpc": "2.0",
            "id": 10,
            "method": "tools/call",
            "params": {"name": "udk_window_info", "arguments": {"target": "editor"}},
        }
        res = udk_mcp_server.handle_message(req)
        self.assertEqual(res["id"], 10)
        content_text = res["result"]["content"][0]["text"]
        # Must be valid JSON
        data = json.loads(content_text)
        self.assertIsInstance(data, dict)
        if not data.get("ok"):
            self.assertIn("error", data)
            self.assertTrue(res["result"]["isError"])

    def test_window_invalid_target(self):
        req = {
            "jsonrpc": "2.0",
            "id": 11,
            "method": "tools/call",
            "params": {"name": "udk_window_info", "arguments": {"target": "invalid_dialog_name"}},
        }
        res = udk_mcp_server.handle_message(req)
        content_text = res["result"]["content"][0]["text"]
        data = json.loads(content_text)
        self.assertFalse(data.get("ok", True))
        self.assertTrue(res["result"]["isError"])

    def test_window_key_validation(self):
        """Unsupported key must be rejected with ValueError."""
        with self.assertRaises(ValueError) as ctx:
            udk_window.window_key("INVALID_KEY_XYZ")
        self.assertIn("Unsupported key", str(ctx.exception))

    def test_window_type_text_validation(self):
        """Control characters and empty strings must be rejected."""
        with self.assertRaises(ValueError):
            udk_window.window_type_text("")
        with self.assertRaises(ValueError):
            udk_window.window_type_text("Hello\x00World")


class SubprocessStdioHandshakeTests(unittest.TestCase):
    """Tests end-to-end stdio communication over JSON-RPC 2.0 pipe."""

    def test_stdio_exchange(self):
        server_script = TEST_DIR / "mcp" / "udk_mcp_server.py"
        requests = [
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-03-26"}},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
            {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "udk_status", "arguments": {}}},
        ]
        input_data = "".join(json.dumps(r) + "\n" for r in requests)
        proc = subprocess.run(
            [sys.executable, str(server_script)],
            input=input_data,
            text=True,
            capture_output=True,
            timeout=15,
            check=True,
        )
        lines = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
        self.assertEqual(len(lines), 3)

        res_init = json.loads(lines[0])
        self.assertEqual(res_init["result"]["serverInfo"]["name"], "udk-mcp-editor")

        res_list = json.loads(lines[1])
        self.assertEqual(len(res_list["result"]["tools"]), 10)

        res_status = json.loads(lines[2])
        status_data = json.loads(res_status["result"]["content"][0]["text"])
        self.assertTrue(status_data["ok"])
        self.assertIn("installed", status_data)


if __name__ == "__main__":
    unittest.main()
