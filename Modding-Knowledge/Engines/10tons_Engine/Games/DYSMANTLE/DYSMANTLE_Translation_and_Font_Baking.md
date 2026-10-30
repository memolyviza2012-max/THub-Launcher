# DYSMANTLE (10tons Engine) Modding & Translation Bible

## 1. Engine Archive Structure (.pak)
DYSMANTLE uses the **10tons Engine**, which packages files into custom `.pak` archives (e.g., `data-localizations.pak`, `data-windows.pak`).

### PAK V11 Header Format (16 Bytes)
- **Magic**: `PAK\x00` (4 bytes)
- **Version**: `V11\x00` (4 bytes)
- **Index Offset**: (4 bytes, Little Endian) - Offset where the file index starts.
- **Total Size**: (4 bytes, Little Endian) - Total file size (or size up to the end of index).

### Index Format
- Located at `Index Offset`.
- Starts with `num_entries` (4 bytes).
- Followed by `num_entries` records. Each record consists of:
  - Null-terminated UTF-8 string for the relative file path.
  - `File Offset` (4 bytes)
  - `File Size` (4 bytes)
  - `Timestamp` (4 bytes)
  - `Padding/Unknown` (4 bytes)

### Modding Rule: Packing `.pak` Files
If you repack a `.pak` file, **the header's Total Size must exactly match the physical size of the file**. If the header size is incorrect (e.g. `0` or mismatched), the game engine will instantly crash with an error `Pak size doesn't match the file size`.

---

## 2. Localization & Font Baking (`nx-rescaler`)

10tons engine uses **MSDF (Multi-channel Signed Distance Field)** fonts in the `.mft` format. 
To convert standard `.ttf` fonts into `.mft` fonts, the official **Modding Kit** provides a tool called `nx-rescaler`.

### The Font Baking Dependency Loop
The `nx-rescaler` tool does **not** bake every single glyph available in a `.ttf` file. Instead, it **scans a target XML file for used characters** and only bakes the glyphs it finds.

In `small.mft.xml`, the configuration looks like this:
```xml
<node id="INPUT" 
    ttf="Tahoma.ttf" size_px="20" 
    strings="../../../../data-localizations/localizations/th/language.xml"
    ttf_fallback="Tahoma.ttf" />
```

### CRITICAL: PUA (Private Use Area) Mapping Requirements for Thai
Thai fonts usually require PUA (Private Use Area) mapping to prevent floating vowels and tone marks from overlapping (สระลอย/จม).
Because `nx-rescaler` only bakes glyphs present in `language.xml`, **you MUST apply the PUA mapping to the XML strings BEFORE you bake the font**.

1. **Failure Case ("ไม่เข้า PUA"):**
   - If you inject standard Thai text into `language.xml`, the Font Baker will only bake standard Thai glyphs (the resulting MSDF font will be small, e.g. `355KB`).
   - When the game loads, it renders standard Thai text with standard Thai glyphs. Without Harfbuzz layout logic in the engine, the vowels will overlap incorrectly.
2. **Success Case:**
   - If you apply PUA mapping (using `Mapping.json`) to the translated text *before* saving to `language.xml`, the file will contain PUA-encoded characters.
   - The Font Baker will see these PUA characters, extract them from your `Prompt-Regular_PUA.ttf`, and bake them into the `.mft` (the resulting MSDF font will be large, e.g. `1.7MB`).
   - The game will render beautifully with perfectly aligned vowels.

---

## 3. PUA Packing Workflow (Python)
When mapping Thai standard text to PUA, always **sort the mapping dictionary keys by length (longest to shortest)**. This ensures that compound vowels/tones (e.g. `0E01 0E31 0E48`) are replaced correctly before smaller subsets (e.g. `0E01 0E31`).

```python
# Example: Correct PUA Mapping Logic
import json
with open('Mapping.json', 'r', encoding='utf-8') as f:
    mapping = json.load(f)

# Sort keys by length descending to replace longest patterns first
sorted_keys = sorted(mapping.keys(), key=len, reverse=True)

def apply_pua(text):
    for k in sorted_keys:
        if k in text:
            text = text.replace(k, mapping[k])
    return text
```

---

## 4. Packing/Unpacking Python Scripts

### unpack_10tons_pak.py
```python
import os
import struct

def unpack_pak(file_path, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    with open(file_path, 'rb') as f:
        header = f.read(16)
        magic, ver, index_offset, unk_size = struct.unpack('<4s4sII', header)
        
        if magic != b'PAK\x00' or ver != b'V11\x00':
            return
            
        f.seek(index_offset)
        num_entries = struct.unpack('<I', f.read(4))[0]
        entries = []
        
        for _ in range(num_entries):
            chars = []
            while True:
                c = f.read(1)
                if c == b'\x00': break
                chars.append(c)
            filename = b''.join(chars).decode('utf-8')
            meta = f.read(16)
            offset, size, ts, pad = struct.unpack('<IIII', meta)
            entries.append((filename, offset, size))
            
        for filename, offset, size in entries:
            out_path = os.path.join(out_dir, filename)
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            f.seek(offset)
            with open(out_path, 'wb') as out_f:
                out_f.write(f.read(size))
```

### pack_10tons_pak.py
```python
import os
import struct
import time

def pack_pak(in_dir, out_file):
    entries = []
    for root, dirs, files in os.walk(in_dir):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, in_dir).replace('\\', '/')
            entries.append((rel_path, full_path))
    
    entries.sort(key=lambda x: x[0])
    
    with open(out_file, 'wb') as f:
        f.write(b'\x00' * 16) # Placeholder header
        file_metadata = []
        
        for rel_path, full_path in entries:
            current_offset = f.tell()
            size = os.path.getsize(full_path)
            ts = int(os.path.getmtime(full_path))
            
            with open(full_path, 'rb') as in_f:
                f.write(in_f.read())
            
            file_metadata.append((rel_path, current_offset, size, ts))
            
        index_offset = f.tell()
        f.write(struct.pack('<I', len(file_metadata)))
        for rel_path, offset, size, ts in file_metadata:
            f.write(rel_path.encode('utf-8') + b'\x00')
            f.write(struct.pack('<IIII', offset, size, ts, 0))
            
        total_size = f.tell()
        
        f.seek(0)
        f.write(struct.pack('<4s4sII', b'PAK\x00', b'V11\x00', index_offset, total_size))
```
