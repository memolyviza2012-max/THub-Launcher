#!/usr/bin/env python3
"""Model Context Protocol (MCP) Server for Unity Native Thai Font & TMP Assets.

Exposes specialized MCP tools for AI Agents (Antigravity, Claude Code, Cursor)
to discover, tune, subset, transplant, and verify TextMeshPro Thai fonts
directly within Unity serialized assets.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add parent directory to sys.path so we can import Unity engine modules
CURRENT_DIR = Path(__file__).resolve().parent
PARENT_DIR = CURRENT_DIR.parent
if str(PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(PARENT_DIR))

try:
    from unity_common import load_unitypy, sha256_file
    from unity_font_pipeline import ThaiFontMapper, UnityFontPipeline
    from unity_native_packer import UnityNativePacker
    from unity_native_validator import UnityNativeValidator
except ImportError as exc:
    # Direct import fallback
    import unity_common
    from unity_common import load_unitypy, sha256_file
    from unity_font_pipeline import ThaiFontMapper, UnityFontPipeline
    from unity_native_packer import UnityNativePacker
    from unity_native_validator import UnityNativeValidator

SERVER_NAME = "unity-native-font"
SERVER_VERSION = "1.0.0"

TOOLS_DEFINITIONS = [
    {
        "name": "scan_unity_font_references",
        "description": "Scans a Unity asset file or directory to locate existing TextMeshPro FontAsset (TypeId 114), Material (TypeId 21), and Atlas Texture2D (TypeId 28) with their PathIDs, script names, and texture dimensions.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "asset_path": {
                    "type": "string",
                    "description": "Absolute path to Unity .assets, level*, or resources.assets file"
                },
                "font_name_filter": {
                    "type": "string",
                    "description": "Optional filter for font or material names (e.g. 'SDF', 'Font', 'Prompt')"
                }
            },
            "required": ["asset_path"]
        }
    },
    {
        "name": "build_thai_subset",
        "description": "Extracts minimal unique character subset from translated CSV (ASCII + mapped Thai PUA + base Thai) for TextMeshPro Font Asset Creator.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "csv_path": {
                    "type": "string",
                    "description": "Path to translated TStudio CSV file"
                },
                "output_charset_path": {
                    "type": "string",
                    "description": "Path to save output character list (characters.txt)"
                }
            },
            "required": ["csv_path"]
        }
    },
    {
        "name": "tune_thai_tone_marks",
        "description": "Elevates vertical component offset (+160 units default) for Thai tone marks (U+0E48–U+0E4B: ไม้เอก, ไม้โท, ไม้ตรี, ไม้จัตวา) in PUA composite glyphs using TrueType glyf tables to avoid clipping and floating.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "input_font_path": {
                    "type": "string",
                    "description": "Path to input TrueType font file (.ttf)"
                },
                "output_font_path": {
                    "type": "string",
                    "description": "Path to output shifted font file (.ttf)"
                },
                "raise_units": {
                    "type": "integer",
                    "description": "Vertical offset in font units (default: 160)",
                    "default": 160
                }
            },
            "required": ["input_font_path", "output_font_path"]
        }
    },
    {
        "name": "transplant_native_font",
        "description": "Transplants TextMeshPro FontAsset and Texture2D Atlas from a Unity Font AssetBundle into a target Unity serialized asset file using AssetsTools.NET without destroying allocator tables.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "target_asset_path": {
                    "type": "string",
                    "description": "Target game .assets file (e.g. resources.assets or sharedassets0.assets)"
                },
                "output_asset_path": {
                    "type": "string",
                    "description": "Path where the repacked .assets file will be created"
                },
                "font_bundle_path": {
                    "type": "string",
                    "description": "Compiled TMP Font AssetBundle containing replacement font and texture atlas"
                },
                "target_font_pathid": {
                    "type": "integer",
                    "description": "PathID of target TMP FontAsset in target asset"
                },
                "target_material_pathid": {
                    "type": "integer",
                    "description": "PathID of target Material"
                },
                "target_atlas_pathid": {
                    "type": "integer",
                    "description": "PathID of target Atlas Texture2D"
                },
                "dummy_dlls_dir": {
                    "type": "string",
                    "description": "Optional path to Il2CppDumper DummyDll directory"
                },
                "unity_version": {
                    "type": "string",
                    "description": "Target Unity version (default: '2020.3.22f1')",
                    "default": "2020.3.22f1"
                }
            },
            "required": [
                "target_asset_path",
                "output_asset_path",
                "font_bundle_path",
                "target_font_pathid",
                "target_material_pathid",
                "target_atlas_pathid"
            ]
        }
    },
    {
        "name": "verify_native_font",
        "description": "Performs independent read-back verification on packed asset file, ensuring FontAsset and Texture2D records are intact and readable with zero crashes.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "original_asset_path": {
                    "type": "string",
                    "description": "Original unmodified asset file path"
                },
                "packed_asset_path": {
                    "type": "string",
                    "description": "Repacked asset file path to verify"
                },
                "manifest_output_path": {
                    "type": "string",
                    "description": "Optional path to save hash_manifest.json"
                }
            },
            "required": ["original_asset_path", "packed_asset_path"]
        }
    }
]


def execute_scan_unity_font_references(arguments: Dict[str, Any]) -> Dict[str, Any]:
    asset_path = Path(arguments["asset_path"]).resolve()
    name_filter = arguments.get("font_name_filter", "").lower()

    if not asset_path.exists():
        raise FileNotFoundError(f"Asset file does not exist: {asset_path}")

    UnityPy = load_unitypy()
    env = UnityPy.load(str(asset_path))

    found_fonts = []
    found_materials = []
    found_textures = []

    for obj in env.objects:
        tname = obj.type.name
        pid = obj.path_id

        if tname == "MonoBehaviour":
            try:
                tree = obj.read_typetree()
                if isinstance(tree, dict):
                    # Check if it has font-like structure or script name
                    m_script = tree.get("m_Script", {})
                    s_pid = m_script.get("m_PathID") if isinstance(m_script, dict) else None
                    is_tmp = False
                    font_name = tree.get("m_Name", "")

                    if s_pid and s_pid in env.objects:
                        try:
                            s_obj = env.objects[s_pid].read()
                            s_name = getattr(s_obj, "m_ClassName", getattr(s_obj, "m_Name", ""))
                            if "TMP" in s_name or "Font" in s_name:
                                is_tmp = True
                        except Exception:
                            pass

                    if "m_AtlasTextures" in tree or "m_fontInfo" in tree or "m_CharacterTable" in tree:
                        is_tmp = True

                    if is_tmp:
                        mat_id = None
                        if "material" in tree and isinstance(tree["material"], dict):
                            mat_id = tree["material"].get("m_PathID")

                        atlas_id = None
                        if "atlas" in tree and isinstance(tree["atlas"], dict):
                            atlas_id = tree["atlas"].get("m_PathID")
                        elif "m_AtlasTextures" in tree and isinstance(tree["m_AtlasTextures"], dict):
                            arr = tree["m_AtlasTextures"].get("Array", [])
                            if arr and isinstance(arr[-1], dict):
                                atlas_id = arr[-1].get("m_PathID")

                        if not name_filter or (name_filter in font_name.lower()):
                            found_fonts.append({
                                "path_id": pid,
                                "type": "TextMeshPro FontAsset",
                                "name": font_name or f"FontAsset_{pid}",
                                "material_path_id": mat_id,
                                "atlas_texture_path_id": atlas_id
                            })
            except Exception:
                continue

        elif tname == "Material":
            try:
                data = obj.read()
                m_name = getattr(data, "m_Name", f"Material_{pid}")
                if not name_filter or (name_filter in m_name.lower()):
                    found_materials.append({
                        "path_id": pid,
                        "type": "Material",
                        "name": m_name
                    })
            except Exception:
                continue

        elif tname == "Texture2D":
            try:
                data = obj.read()
                tex_name = getattr(data, "m_Name", f"Texture2D_{pid}")
                w = getattr(data, "m_Width", 0)
                h = getattr(data, "m_Height", 0)
                fmt = getattr(data, "m_TextureFormat", "")
                if not name_filter or (name_filter in tex_name.lower()):
                    found_textures.append({
                        "path_id": pid,
                        "type": "Texture2D Atlas",
                        "name": tex_name,
                        "dimensions": f"{w}x{h}",
                        "format": str(fmt)
                    })
            except Exception:
                continue

    return {
        "asset_file": str(asset_path),
        "total_objects_scanned": len(env.objects),
        "font_assets": found_fonts,
        "materials": found_materials[:20],
        "atlas_textures": found_textures[:20]
    }


def execute_build_thai_subset(arguments: Dict[str, Any]) -> Dict[str, Any]:
    csv_p = Path(arguments["csv_path"]).resolve()
    out_p = Path(arguments.get("output_charset_path") or (csv_p.parent / "characters.txt")).resolve()

    pipeline = UnityFontPipeline()
    charset, stats = pipeline.build_character_subset(csv_p)

    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_p.write_text(charset, encoding="utf-8", newline="")

    return {
        "output_path": str(out_p),
        "total_characters": len(charset),
        "statistics": stats
    }


def execute_tune_thai_tone_marks(arguments: Dict[str, Any]) -> Dict[str, Any]:
    in_font = Path(arguments["input_font_path"]).resolve()
    out_font = Path(arguments["output_font_path"]).resolve()
    raise_units = int(arguments.get("raise_units", 160))

    res = UnityFontPipeline.tune_tone_marks(in_font, out_font, raise_units)
    return res


def execute_transplant_native_font(arguments: Dict[str, Any]) -> Dict[str, Any]:
    target_asset = Path(arguments["target_asset_path"]).resolve()
    output_asset = Path(arguments["output_asset_path"]).resolve()
    font_bundle = Path(arguments["font_bundle_path"]).resolve()
    target_font_pathid = int(arguments["target_font_pathid"])
    target_material_pathid = int(arguments["target_material_pathid"])
    target_atlas_pathid = int(arguments["target_atlas_pathid"])
    dummy_dlls = arguments.get("dummy_dlls_dir")
    unity_version = arguments.get("unity_version", "2020.3.22f1")

    packer = UnityNativePacker(unity_version=unity_version, dummy_dlls_dir=dummy_dlls)

    # Empty dummy translation map just for font transplant
    temp_json = output_asset.parent / "_temp_font_transplant.json"
    temp_json.parent.mkdir(parents=True, exist_ok=True)
    temp_json.write_text(json.dumps({"tables": {}}, ensure_ascii=False), encoding="utf-8")

    try:
        res = packer.pack_assets(
            input_asset=target_asset,
            output_asset=output_asset,
            translation_map_json=temp_json,
            font_bundle=font_bundle,
            target_font_pathid=target_font_pathid,
            target_material_pathid=target_material_pathid,
            target_atlas_pathid=target_atlas_pathid,
            force=True
        )
    finally:
        if temp_json.is_file():
            try:
                temp_json.unlink()
            except Exception:
                pass

    return {
        "success": True,
        "output_asset": str(output_asset),
        "output_hash": res.get("output_hash")
    }


def execute_verify_native_font(arguments: Dict[str, Any]) -> Dict[str, Any]:
    orig_p = Path(arguments["original_asset_path"]).resolve()
    packed_p = Path(arguments["packed_asset_path"]).resolve()
    manifest_p = arguments.get("manifest_output_path")

    validator = UnityNativeValidator()
    res = validator.validate_asset(orig_p, packed_p, manifest_output=manifest_p)
    return res


def handle_tool_call(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Dispatches tool execution to the appropriate implementation."""
    if name == "scan_unity_font_references":
        return execute_scan_unity_font_references(arguments)
    elif name == "build_thai_subset":
        return execute_build_thai_subset(arguments)
    elif name == "tune_thai_tone_marks":
        return execute_tune_thai_tone_marks(arguments)
    elif name == "transplant_native_font":
        return execute_transplant_native_font(arguments)
    elif name == "verify_native_font":
        return execute_verify_native_font(arguments)
    else:
        raise ValueError(f"Unknown MCP tool: {name}")


def run_stdio_server():
    """Runs standard MCP stdio JSON-RPC loop."""
    sys.stderr.write(f"[{SERVER_NAME}] Starting Unity Native Font MCP Server...\n")
    sys.stderr.flush()

    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            line_str = line.strip()
            if not line_str:
                continue

            request = json.loads(line_str)
            req_id = request.get("id")
            method = request.get("method")
            params = request.get("params", {})

            if method == "initialize":
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": SERVER_NAME,
                            "version": SERVER_VERSION
                        }
                    }
                }
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()

            elif method == "notifications/initialized":
                # Client initialization confirmation
                pass

            elif method == "tools/list":
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "tools": TOOLS_DEFINITIONS
                    }
                }
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()

            elif method == "tools/call":
                t_name = params.get("name")
                t_args = params.get("arguments", {})
                try:
                    result_data = handle_tool_call(t_name, t_args)
                    response = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": json.dumps(result_data, ensure_ascii=False, indent=2)
                                }
                            ]
                        }
                    }
                except Exception as exc:
                    response = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "isError": True,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Error executing tool '{t_name}': {str(exc)}"
                                }
                            ]
                        }
                    }
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()

            elif method == "ping":
                response = {"jsonrpc": "2.0", "id": req_id, "result": {}}
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()

            else:
                # Method not found
                if req_id is not None:
                    response = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "error": {
                            "code": -32601,
                            "message": f"Method '{method}' not found."
                        }
                    }
                    sys.stdout.write(json.dumps(response) + "\n")
                    sys.stdout.flush()

        except Exception as err:
            sys.stderr.write(f"[{SERVER_NAME}] Error: {err}\n")
            sys.stderr.flush()


if __name__ == "__main__":
    run_stdio_server()
