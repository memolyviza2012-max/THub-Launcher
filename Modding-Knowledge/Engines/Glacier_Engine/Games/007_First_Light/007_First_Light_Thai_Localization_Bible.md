# 007 First Light - Modding Knowledge Base

## Overview
- **Game:** 007 First Light
- **Engine:** Glacier Engine (IO Interactive)
- **Mod:** 007_First_Light_Thai_v2.2

## Architecture & File Formats
The game uses the Glacier Engine, which packages its game assets into highly compressed and structured archives with the .rpkg extension.
Typical game structure involves chunk0.rpkg, chunk1.rpkg, etc.

## Localization Strategy (Rivet Engineer Approach)
To inject custom localization (e.g., Thai fonts and translated text), a direct file-replacement or appending method is required because the Glacier Engine does not easily allow external loose files.

### 1. Payload Appending (The 'rpkg_append_payload' method)
- Modders use an installer_manifest.json to define target archives (e.g., Runtime/chunk0.rpkg).
- A pre-compiled binary payload (pkg_payload.bin), built alongside an pkg_manifest.json, contains the patched blocks of localized text (LOCR) and font textures (TEXT).
- A custom Python installer script (ติดตั้ง.py) is used to surgically inject this payload into the original .rpkg files.

### 2. Implementation Steps
1. Parse the base .rpkg header and structure.
2. Locate the offsets for the target localization files inside the package.
3. Append or overwrite those specific blocks with the pkg_payload.bin data.
4. Update the package manifest and checksums if strictly enforced by the engine.
