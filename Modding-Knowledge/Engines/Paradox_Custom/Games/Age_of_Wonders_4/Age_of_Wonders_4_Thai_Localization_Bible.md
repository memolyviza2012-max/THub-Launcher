# Age of Wonders 4 — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Age of Wonders 4 is a 4X turn-based strategy game developed by **Triumph Studios** (a Paradox Interactive subsidiary). The game uses a **custom proprietary engine** and relies on the industry-standard **GNU gettext** localization system (`.MO` / `.PO` files). The Thai mod follows the simplest possible architecture: **File Replacement** — drop a single translated `.MO` file into the game's Language folder.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Triumph Engine (Proprietary / Paradox-published) |
| **Developer** | Triumph Studios |
| **Project Codename** | N/A |
| **Archive Format** | None (loose files in Language directory) |
| **AES Encryption** | No |
| **Compression** | None |
| **Font System** | Built-in multilingual font (no font mod required) |
| **Thai Font Used** | Game's internal font (supports Thai natively or via system fallback) |
| **Text System** | GNU gettext Binary MO (`.MO`) |
| **Text Encoding** | UTF-8 |
| **Mod Complexity** | ★☆☆☆☆ (Single file replacement — the simplest mod in the entire Knowledge Base) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```text
Age_of_Wonders/
└── Language/
    └── EN/
        └── EN.MO    (11.1 MB — GNU gettext binary, 48,625 strings, 41,035 containing Thai)
```

---

## 4. Font Analysis
- **Font Identification:** The mod does **NOT** include any font files. Age of Wonders 4 appears to use a built-in font that already supports Thai Unicode ranges (U+0E00–U+0E7F).
- **Storage Strategy:** N/A — no font modification needed.
- **Thai Rendering Considerations:** Since the game's engine handles Thai text natively, สระลอย (floating vowels) and วรรณยุกต์ (tone marks) are rendered by the engine's internal text shaper. This is the ideal scenario for localization — zero font work required.

---

## 5. Text Analysis
- **File Format:** GNU gettext MO (Binary) — Magic bytes: `DE 12 04 95` (little-endian).
- **Encoding:** UTF-8.
- **MO File Structure:**
  - Revision: 0
  - Total strings: **48,625**
  - Strings containing Thai text: **41,035** (84.4% translated)
  - Original string table offset: 28 (0x1C)
  - Translation string table offset: 389,028 (0x5EFA4)
- **Key Format:** Hierarchical key paths using `@` delimiter (e.g., `ABILITIES@ACTIVE_ABILITY_TOUCH@RELOAD_NAME` → `โหลดใหม่`).
- **Locale Override Strategy:** The translated `.MO` file replaces `Language/EN/EN.MO`, overriding the English locale with Thai text. When the player selects "English" in-game, they see Thai instead.

---

## 6. Cross-Engine Comparison
Age of Wonders 4 is dramatically simpler to mod than any other game in the Knowledge Base:

| Feature | Age of Wonders 4 | Warhammer RT (Unity) | Encased (Unity) | RE2 Remake (RE Engine) |
|---|---|---|---|---|
| **Font Required** | ❌ None | ✅ TMP SDF + DLL | ✅ TTF repack | ✅ OTF rename |
| **Text Format** | GNU gettext MO | JSON (UUID) | Custom .locale | Binary .msg |
| **File Count** | 1 file | 11 files | 6 files | ~500 files |
| **Tools Required** | `msgfmt` / `msgunfmt` | Unity Editor + C# | UABEA + Custom | REtool |
| **Complexity** | ★☆☆☆☆ | ★★★★☆ | ★★☆☆☆ | ★★☆☆☆ |

The GNU gettext system is the gold standard of open localization frameworks. It has been used in GNU/Linux software for decades and has mature, well-documented tooling (`msgfmt`, `msgunfmt`, `poedit`, Python `gettext` module).

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
**Font Pipeline:**
- ❌ Not required. The game engine renders Thai natively.

**Text Pipeline:**
1. **Decompile MO → PO:** Use `msgunfmt EN.MO -o EN.po` to convert the binary MO file into a human-readable PO (Portable Object) text file.
2. **Translate:** Open `EN.po` in Poedit or any text editor. Each entry has a `msgid` (original key) and `msgstr` (translated value). Fill in Thai translations for each `msgstr`.
3. **Compile PO → MO:** Use `msgfmt EN.po -o EN.MO` to compile back to binary.
4. **Deploy:** Copy `EN.MO` to `{GameDir}/Language/EN/EN.MO`, replacing the original.

---

## 8. Troubleshooting
- **Thai text not appearing:** Verify that `EN.MO` is placed in the correct `Language/EN/` subdirectory and that the game language is set to "English".
- **Garbled text (mojibake):** The PO file was saved with wrong encoding. Ensure UTF-8 throughout the entire pipeline.
- **Missing translations (English fallback):** Some strings (7,590 out of 48,625) are not yet translated. The game will display the original English `msgid` for untranslated entries.
- **Game update breaks mod:** After a game update, new strings may be added. Use `msgmerge` to merge the old PO with a freshly extracted PO from the updated game.

---

## 9. Required Tools
| Tool Name | Purpose | Source |
|---|---|---|
| `msgunfmt` | Decompile `.MO` binary → `.PO` text | [GNU gettext] |
| `msgfmt` | Compile `.PO` text → `.MO` binary | [GNU gettext] |
| `msgmerge` | Merge old translations with new source strings | [GNU gettext] |
| Poedit | GUI editor for PO files | [poedit.net] |
| Python `gettext` module | Programmatic reading/writing of MO/PO files | [Python stdlib] |

---

## 10. Extracted Assets
- **Font:** No font files to extract. See [EXTRACTION_NOTE.txt](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Paradox_Custom/Games/Age_of_Wonders_4/Assets/Fonts/EXTRACTION_NOTE.txt)
- **Text:** The MO file contains 48,625 key-value pairs (41,035 translated to Thai). No extraction needed — it can be read directly with `msgunfmt` or Python's `gettext` module.

---

## 11. M2M Protocol
**(สำหรับ AI Agent ที่ต้องการนำคัมภีร์ไปรันสร้างม็อดอัตโนมัติ)**

เกมนี้เป็นเกมที่ AI ทำม็อดได้ง่ายที่สุดในคลังความรู้ทั้งหมด! ไม่ต้องจัดการฟอนต์ แค่เขียนสคริปต์ Python ชุดเดียวก็ทำม็อดแปลภาษาไทยได้เบ็ดเสร็จ:

### 1. อ่านและแก้ไขไฟล์ MO ด้วย Python
```python
import struct
import os

def read_mo_file(mo_path):
    """Parse GNU gettext MO file and return dict of {key: translation}"""
    with open(mo_path, 'rb') as f:
        data = f.read()
    
    magic = struct.unpack_from('<I', data, 0)[0]
    assert magic == 0x950412DE, "Not a valid MO file"
    
    num_strings = struct.unpack_from('<I', data, 8)[0]
    orig_offset = struct.unpack_from('<I', data, 12)[0]
    trans_offset = struct.unpack_from('<I', data, 16)[0]
    
    strings = {}
    for i in range(num_strings):
        o_len, o_off = struct.unpack_from('<II', data, orig_offset + i * 8)
        t_len, t_off = struct.unpack_from('<II', data, trans_offset + i * 8)
        
        key = data[o_off:o_off+o_len].decode('utf-8', errors='replace')
        val = data[t_off:t_off+t_len].decode('utf-8', errors='replace')
        strings[key] = val
    
    return strings

def write_mo_file(strings_dict, output_path):
    """Write a dict of {key: translation} to GNU gettext MO binary format"""
    keys = sorted(strings_dict.keys())
    
    num = len(keys)
    # MO header: 7 * 4 = 28 bytes
    # orig table: num * 8 bytes
    # trans table: num * 8 bytes
    orig_table_offset = 28
    trans_table_offset = 28 + num * 8
    
    # String data starts after both tables
    string_data_offset = 28 + num * 8 * 2
    
    orig_entries = []
    trans_entries = []
    string_pool = bytearray()
    
    for key in keys:
        key_bytes = key.encode('utf-8')
        val_bytes = strings_dict[key].encode('utf-8')
        
        orig_entries.append((len(key_bytes), string_data_offset + len(string_pool)))
        string_pool.extend(key_bytes + b'\x00')
        
        trans_entries.append((len(val_bytes), string_data_offset + len(string_pool)))
        string_pool.extend(val_bytes + b'\x00')
    
    with open(output_path, 'wb') as f:
        # Header
        f.write(struct.pack('<I', 0x950412DE))  # magic
        f.write(struct.pack('<I', 0))            # revision
        f.write(struct.pack('<I', num))           # num strings
        f.write(struct.pack('<I', orig_table_offset))
        f.write(struct.pack('<I', trans_table_offset))
        f.write(struct.pack('<I', 0))            # hash table size
        f.write(struct.pack('<I', 0))            # hash table offset
        
        # Original string table
        for length, offset in orig_entries:
            f.write(struct.pack('<II', length, offset))
        
        # Translation string table
        for length, offset in trans_entries:
            f.write(struct.pack('<II', length, offset))
        
        # String data
        f.write(bytes(string_pool))
```

### 2. แปลภาษาอัตโนมัติ
```python
def translate_mo(input_mo, output_mo, translate_func):
    """
    translate_func: callable(key, english_text) -> thai_text
    """
    strings = read_mo_file(input_mo)
    
    translated = {}
    for key, val in strings.items():
        translated[key] = translate_func(key, val)
    
    write_mo_file(translated, output_mo)
```

**ข้อดีที่สุดของเกมนี้สำหรับ AI:** ไม่ต้องจัดการฟอนต์เลยแม้แต่ไบต์เดียว! AI เพียงแค่อ่าน MO → แปลข้อความ → เขียน MO กลับ ก็ได้ม็อดสำเร็จรูปออกมาทันทีครับ!
