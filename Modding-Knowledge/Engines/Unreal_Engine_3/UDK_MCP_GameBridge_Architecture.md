# 🎮 Unreal Engine 3 / UDK MCP GameBridge Architecture & Integration Guide

> **Engine:** Unreal Engine 3 (UDK Build September 2011 & Custom UE3 Games)  
> **Component:** THub Flagship GameBridge (`tools/flagship/GameBridges/UnrealEngine3/`)  
> **MCP Server:** `udk-mcp-editor` v1.0.0  
> **Author:** THub Modding Team (with THub AI Architecture)  
> **Last Updated:** 2026-09-27  
> **Status:** ✅ Production Ready & Fully Tested (21/21 Unit Tests Passed)

---

## 1. Overview & Problem Statement

Unreal Engine 3 games (such as *Dishonored*, *XCOM: Enemy Unknown*, *Spec Ops: The Line*, *BioShock Infinite*, *Batman: Arkham* series) rely on proprietary binary package formats (`.upk`, `.u`, `.udk`). In Thai localization modding, font generation and asset inspection require tools like the Unreal Development Kit (UDK).

However, integrating UDK with modern AI coding assistants (Claude Code, Antigravity, Cursor) presents several critical engineering challenges:
1. **Engine Version & Licensee Mismatch**: Stock UDK (September 2011, `FileVersion 845`, `LicenseeVersion 0`) crashes or corrupts data if fed cooked packages from licensed UE3 games (e.g. Dishonored uses `FileVersion 801`, `LicenseeVersion 30`).
2. **Fragile UI Automation**: Automating UDK Editor via Windows API requires strict DPI-awareness, process identification, and foreground/occlusion verification to prevent accidental clicks when dialogs or IDEs overlap.
3. **Hardcoded Environments**: Development prototypes frequently hardcode paths (e.g. `C:\UDK\UDK-2011-09`), failing on machines where UDK is installed on secondary drives or custom directories.
4. **Tool Safety & Hang Prevention**: Commandlets like `PkgInfo` or `Make` must run in isolated subprocesses with timeout wrappers, preventing UI freezes or infinite loops.

To solve this, **THub** provides the **UDK MCP GameBridge**: a clean, secure, Model Context Protocol (MCP) server with deep package preflight checks and reliable Win32 automation.

---

## 2. Architecture & Connection Diagram

```
+-----------------------------------------------------------------------------------+
|                              THub Ecosystem (PyQt6)                               |
|                                                                                   |
|  [Engine Scanner]                [AI Helper View]              [Prompt Engine]    |
|   Detects UE3 / UPK / UDKGame  -> Shows UDK MCP Option & Setup -> Injects Protocol K|
+------------------------------------------+----------------------------------------+
                                           |
                    Registers / Deploys via `_setup_udk_mcp_server`
                                           v
+-----------------------------------------------------------------------------------+
|                        Project Workspace (e.g. Dishonored)                        |
|                                                                                   |
|  05_Scripts_and_Tools/udk_mcp/                                                   |
|    |-- udk_mcp_server.py  <-- [MCP Server: JSON-RPC 2.0 stdio]                     |
|    |-- ue3_common.py      <-- [Dynamic Discovery, Header Inspection, Path Guard] |
|    `-- udk_window.py      <-- [Win32 DPI-aware Client Coordinates, Occlusion Guard]|
|  mcp_config.json                                                                  |
+------------------------------------------+----------------------------------------+
                                           |
                                  Stdio JSON-RPC 2.0
                                           v
+-----------------------------------------------------------------------------------+
|                     AI Modding Assistants (Client Consumers)                      |
|                                                                                   |
|    Antigravity IDE     |     Claude Code (CLI)     |     Cursor IDE / MCP Client   |
+------------------------------------------+----------------------------------------+
                                           |
                     Protected Subprocess & Win32 Controls
                                           v
+-----------------------------------------------------------------------------------+
|                             Target Machine Environment                            |
|                                                                                   |
|  • Dynamic UDK Discovery: Auto-locates UDK.exe (Env -> Config -> Shortcut -> Scan) |
|  • Isolated Commandlets: Runs `UDK.exe PkgInfo` with timeout protection           |
|  • Binary Header Guard: Rejects incompatible Licensee packages before commandlets |
|  • Win32 Automation: Verified UDK Editor, Content Browser, Dialog windows         |
+-----------------------------------------------------------------------------------+
```

---

## 3. Core Component Reference

### 3.1 `ue3_common.py` (Core Logic & Security)

Located at `tools/flagship/GameBridges/UnrealEngine3/ue3_common.py`:
- `find_udk_installation(custom_root=None, config_path=None)`:
  Discovers UDK via 5 fallback tiers:
  1. `custom_root` parameter
  2. `UDK_ROOT` or `UDK_EXE` environment variables
  3. THub configuration (`hub_config.json`)
  4. Windows Start Menu shortcuts (`C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Unreal Development Kit\*\UDK Editor.lnk`)
  5. Multi-drive root scan (`C:\UDK\*`, `D:\UDK\*`, `E:\UDK\*`)
- `inspect_ue3_package_header(file_path)`:
  Reads the first 64 bytes of any UPK file. Extracts:
  - Magic signature (`0x9E2A83C1`)
  - `file_version` (uint16)
  - `licensee_version` (uint16)
  - Endianness (Little Endian vs Big Endian)
  - Evaluates stock UDK compatibility:
    - `is_compatible = True` only if `licensee_version == 0`
    - Identifies Dishonored packages (`licensee_version == 30`) and issues explicit warnings.
- `validate_package_path(raw_path, allowed_roots=None)`:
  Guards against path traversal (`../`) and enforces permitted extensions (`.upk`, `.u`, `.udk`).

### 3.2 `udk_window.py` (Win32 Automation & Screen Verification)

Located at `tools/flagship/GameBridges/UnrealEngine3/udk_window.py`:
- Dynamic executable resolution via `ue3_common.find_udk_installation()`.
- DPI-aware client coordinates using `GetDpiForWindow` / `GetWindowDpiAwarenessContext`.
- Target support: `"editor"`, `"browser"`, `"new"`, `"save"`.
- Occlusion Guard: Uses `WindowFromPoint` to verify the target window is not occluded by another application before sending mouse clicks.
- Unicode typing via `WM_CHAR` without polluting the system clipboard.

### 3.3 `udk_mcp_server.py` (Standardized MCP Server)

Located at `tools/flagship/GameBridges/UnrealEngine3/mcp/udk_mcp_server.py`:
Exposes 10 standardized MCP tools:
1. `udk_status`: Report UDK install path, version, and running processes/windows.
2. `udk_inspect_package`: Fast binary header analysis (FileVersion, LicenseeVersion, compatibility).
3. `udk_package_info`: Runs `UDK.exe PkgInfo` with automatic preflight header check (blocks incompatible cooked files).
4. `udk_list_commandlets`: Discovers stock and custom commandlets safely.
5. `udk_commandlet_help`: Dumps help text for specific commandlets.
6. `udk_window_info`: Returns window handle, dimensions, client rect, and title.
7. `udk_window_screenshot`: Takes PNG screenshot encoded in Base64 or saved to disk.
8. `udk_window_click`: Clicks client coordinates with occlusion validation.
9. `udk_window_key`: Sends virtual key presses (ENTER, TAB, ESC, etc.).
10. `udk_window_type_text`: Directly types text into focused controls.

All errors return valid JSON payloads (`{"ok": False, "error": "..."}`) to prevent client JSON parser crashes when UDK is offline.

---

## 4. The Dishonored & Licensee Version Trap

> [!CAUTION]
> **Stock UDK 2011-09 CANNOT open or repack Dishonored cooked packages directly.**
> - Stock UDK package format: `FileVersion = 845`, `LicenseeVersion = 0`
> - Dishonored package format: `FileVersion = 801`, `LicenseeVersion = 30`
>
> Attempting to run `UDK.exe PkgInfo` or open `UI_Loading_SF_LOC_INT.upk` in UDK Editor will fail with assertion errors or silent package corruption.
>
> **Correct Modding Workflow:**
> 1. Use **Stock UDK** solely for generating clean Thai font assets (Canvas Fonts, MultiFonts, TrueType font textures) or inspecting standard UDK sample packages.
> 2. Use **Dishonored-specific tools** (`Decompress.exe`, custom UPK extractors, byte-level hex patchers) to inject the generated font textures into Dishonored's cooked `.upk` files.

---

## 5. THub UI & Agent Integration

### 5.1 Protocol K in Prompt Engine
When a project is identified as Unreal Engine 3 (`core/engine_scanner.py` detects `.upk`, `CookedPCConsole`, or `UDKGame`), THub automatically activates **[Protocol K] UDK 2011-09 MCP Bridge** in the prompt generation engine (`ai/prompt_engine.py`).

### 5.2 One-Click Workspace Setup
In THub's AI Helper view (`ui_pyqt6/views/ai_helper_view_qt.py`):
1. A dedicated button **"⚡ ตั้งค่า UDK MCP Server"** appears whenever a UE3 project is active.
2. Clicking it copies `udk_mcp_server.py`, `ue3_common.py`, and `udk_window.py` to the project's `05_Scripts_and_Tools/udk_mcp/` directory.
3. Automatically writes `mcp_config.json` in the workspace root and registers the server in the user's global Antigravity MCP config (`~/.gemini/config/mcp_config.json`).
4. Displays dynamic status indicating whether `UDK.exe` was discovered on the machine.

---

## 6. Verification & Automated Tests

A comprehensive test suite is provided at `tools/flagship/GameBridges/UnrealEngine3/test_ue3_bridge.py`.

Run unit tests from the THub root:
```bash
python -m unittest tools/flagship/GameBridges/UnrealEngine3/test_ue3_bridge.py
```

Test Coverage (21 tests):
- Dynamic UDK installation detection across multiple discovery channels.
- Binary package header extraction and endianness resolution.
- Licensee version incompatibility detection (Stock vs Dishonored).
- Path traversal rejection and extension allowlist validation.
- UDK window target validation and offline error handling.
- Full MCP stdio JSON-RPC handshake (`initialize`, `tools/list`, `tools/call`).
