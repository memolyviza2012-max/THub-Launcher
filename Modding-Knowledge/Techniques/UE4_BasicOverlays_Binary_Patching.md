# Knowledge Item: Patching UE4 BasicOverlays for Subtitles (Size-Changing)

## Overview
In Unreal Engine (specifically v4.26/4.27), cutscene subtitles are often implemented using the `BasicOverlays` class (Media Framework). These subtitles are stored in `.uasset` and `.uexp` files.

Unlike localized `FText` strings, `BasicOverlays` stores raw `FString` arrays in the `.uexp`. When translating these strings into languages like Thai, the length of the string often changes. Simply changing the string in-place will corrupt the binary file because Unreal's serialization requires strict length tracking.

## Technical Challenge
An `FOverlayItem` inside a `BasicOverlays` array is serialized sequentially.
When the length of an `FString` changes, the following binary fields must be updated:
1. **String Length**: The 4-byte `Length` integer right before the string payload (negative for UTF-16, positive for UTF-8).
2. **StrProperty Size**: The 4-byte `Size` field in the property tag (which is `NameIndex` + `TypeIndex` + `Size` + `ArrayIndex` + `HasPropertyGuid`).
3. **ArrayProperty Size**: The overall array size field at offset `0x10` in the `.uexp` file.
4. **SerialSize in .uasset**: The size of the export inside the `FObjectExport` map. Since `BasicOverlays` usually only has 1 export, its `SerialSize` equals the `.uexp` file size minus the 4-byte package magic tag (`0x9E2A83C1`).
5. **BulkDataStartOffset in .uasset**: The offset where bulk data starts, which must be shifted by the size difference (`Delta`).

## Solution: Custom Binary Patcher
Instead of using complex `.uasset` parsers like UAssetAPI (which may not have a CLI tool available in your workspace), a custom Python script can be used to dynamically find the original strings, replace them with UTF-16 translations, calculate the length difference (`Delta`), and automatically update the respective size fields in both the `.uexp` and `.uasset` headers.

### Key Python Implementation Logic
```python
import struct

# 1. UTF-16 Pattern Matching
orig_utf16 = orig.encode('utf-16le')
len_utf16 = -(len(orig_utf16) // 2 + 1)
size_utf16 = 4 + (abs(len_utf16) * 2)
# Pattern: Size, ArrayIndex (0), HasPropertyGuid (0), Length
pat_utf16 = struct.pack('<iib', size_utf16, 0, 0) + struct.pack('<i', len_utf16) + orig_utf16 + b'\x00\x00'

# 2. Replacing and calculating Delta
idx = uexp_data.find(pat_utf16)
# ... insert new UTF-16 string and update sizes ...
delta = new_size - old_size

# 3. Update ArrayProperty size (Offset 0x10)
arr_size = struct.unpack('<i', uexp_data[0x10:0x14])[0]
struct.pack_into('<i', uexp_data, 0x10, arr_size + delta)

# 4. Update .uasset sizes
# Find old SerialSize (Original Uexp size - 4) and add delta
# Find old BulkDataStartOffset and add delta
```

## Best Practices
- Always encode non-English (e.g. Thai) strings as **UTF-16LE** (negative length) to prevent encoding corruption.
- Before repacking, ensure your script also searches for UTF-8 patterns if the original game text only contained ASCII characters, as UE4 optimizes ASCII strings to UTF-8.
- Pack the modified `.uasset` and `.uexp` in the exact original directory structure using a tool like `repak_cli` before deploying to the `~mods` folder.
