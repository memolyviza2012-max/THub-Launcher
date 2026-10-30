# Chromium PAK Modding Guide

This guide explains the Chromium Pack (`.pak`) file format and how to extract and inject localization resources for game modding and translation.

## Format Overview

Chromium `.pak` files are simple read-only archive files used by Chromium-based applications and engines (including Electron, NW.js, and CEF games) to store resources such as HTML, JS, CSS, images, and localized strings (`.pak` locales).

### File Structure (Format Version 4 / 5)

A `.pak` file consists of:
1. **Header** (Header size varies by version, typically 8 or 12 bytes):
   - **Version** (4 bytes): Typically `4` or `5`.
   - **Resource Count** (2 bytes): Number of resource entries.
   - **Encoding** (1 byte): Encoding indicator (`0` for binary/RAW, `1` for UTF-8, `2` for UTF-16).
2. **Index Table**:
   - Array of resource entries. Each entry consists of:
     - **Resource ID** (2 bytes, uint16): Unique identifier for the resource.
     - **Offset** (4 bytes, uint32): Byte offset from the start of the file where the resource payload begins.
   - Followed by a final sentinel entry:
     - **Resource ID** (2 bytes): Set to `0` or trailing resource count.
     - **End Offset** (4 bytes): Pointing to the end of the last resource.
3. **Data Payload**:
   - Consecutively stored raw bytes for each resource.

## Extraction & Injection Logic

### 1. Extraction (PAK -> CSV)
- Read the header and determine resource count and encoding.
- Read the index entries to get resource IDs and offsets.
- Slice the file data from `Offset` to `NextOffset` to extract the raw string bytes.
- Try decoding the bytes (typically UTF-8 or UTF-16, falling back to Latin-1 or other encodings if binary).
- Write to a TStudio CSV with headers `ID,Source,Translation`.

### 2. Reconstruction / Injection (CSV -> PAK)
- Read the original `.pak` file index to preserve original resource IDs and positions.
- Load the translated strings from the CSV.
- For each resource ID:
  - If a translation exists in the CSV, encode the translation.
  - If no translation exists, use the original resource bytes.
- Build the new data payload and compute new offsets for the index table.
- Write the version header, index table (with updated offsets), and data payload to the output `.pak` file.

## Integration in THub/TStudio

### TStudio Core (`tstudio_core.py`)
- `TPakManager.extract_pak_to_csv(pak_path)`: Automates PAK disassembly.
- `TPakManager.reconstruct_pak_file(original_pak, csv_path, output_pak)`: Re-assembles translated strings into a valid PAK file.

### TStudio UI (`tstudio_app.py`)
- File format filters updated to support `*.pak`.
- Open dialog detects `.pak` files and extracts them to a temp/profile CSV.
- **Deploy to Game** menu re-packs translated CSV into the target `.pak` file.

### TRun UI (`trun_app.py`)
- Browse dialog supports inputting `*.pak`.
- Batch deploy processes `.pak` files automatically using `TPakManager`.
