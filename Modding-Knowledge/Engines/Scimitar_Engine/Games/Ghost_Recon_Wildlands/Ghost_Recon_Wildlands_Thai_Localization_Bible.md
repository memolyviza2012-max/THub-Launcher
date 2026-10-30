# Ghost Recon Wildlands — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Tom Clancy's Ghost Recon Wildlands is an open-world tactical shooter developed by **Ubisoft Paris** using the **Scimitar Engine** (also known as AnvilNext 2.0). The Thai localization mod uses a **Binary Patch (Forge Injection)** architecture — the modder extracts specific data entries from `.forge` archives using QuickBMS, modifies the font and text data, then injects the modified data back into a patch forge (`DataPC_patch_02.forge`). This is one of the most technically demanding mod architectures in the Knowledge Base.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Scimitar Engine (AnvilNext 2.0) |
| **Developer** | Ubisoft Paris |
| **Project Codename** | GRW |
| **Archive Format** | `.forge` (Scimitar proprietary container, magic: `scimitar\x00`) |
| **AES Encryption** | No (but uses proprietary binary structure) |
| **Compression** | Scimitar internal (mixed LZ/custom blocks) |
| **Font System** | Embedded OTF inside `.data` entries within `.forge` archive |
| **Thai Font Used** | Modified DynaFont CJK Gothic (DFPHSGothicJapaneseGR / DFGHSGothic-W5) |
| **Text System** | Binary `.data` entries (proprietary Scimitar text format) |
| **Text Encoding** | UTF-8 (embedded within binary containers) |
| **Mod Complexity** | ★★★★★ (Requires QuickBMS extraction, binary font surgery, forge re-injection) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```text
Wildlands/
├── DataPC_patch_02.forge          (2.8 MB — Scimitar forge archive, magic: "scimitar\x00")
├── GRW.bms                       (617B — QuickBMS script for extracting .data from forge)
├── quickbms_4gb_files.exe         (20 MB — QuickBMS extraction tool)
├── วิธีติดตั้ง.bat                 (149B — Batch script for re-injection)
└── ModTH/
    ├── Font/
    │   ├── 546.data               (2.0 MB — OTF: DFPHSGothicJapaneseGR-Regular, OTTO at offset 400)
    │   ├── 6674.data              (2.1 MB — OTF: DFGHSGothic-W5, OTTO at offset 412)
    │   ├── 6680.data              (2.1 MB — OTF: DFPHSGothic-W5, OTTO at offset 412)
    │   └── 9418.data              (2.1 MB — OTF: DFGHSGothic-W5 + DIN, OTTO at offset 391)
    └── Text/
        ├── 2.data                 (706 KB — Game text strings, proprietary binary)
        └── 3.data                 (556 KB — Game text strings, proprietary binary)
```

---

## 4. Font Analysis
- **Font Identification:** The mod uses **DynaFont (DF) CJK Gothic** font family — commercial Japanese/CJK fonts originally licensed by Ubisoft for Asian language support:
  - `546.data` → **DFPHSGothicJapaneseGR-Regular** (Proportional Japanese Gothic, General Release)
  - `6674.data` → **DFGHSGothic-W5-Regular** (Full-width Gothic Weight 5)
  - `6680.data` → **DFPHSGothic-W5-Regular** (Proportional Gothic Weight 5)
  - `9418.data` → **DFGHSGothic-W5-Regular** + DIN variant
- **Storage Strategy:** Each font is stored as an OTF file wrapped inside a Scimitar `.data` container. The container adds a ~400-byte proprietary header before the OTTO magic bytes. Critically, the OTF table directory offsets are **relative to the container file start**, NOT the font data start — making simple offset-based carving impossible without offset rewriting.
- **Modification Approach:** The modder modified the DynaFont CJK fonts to include Thai Unicode glyphs (U+0E00–U+0E7F), keeping the original Japanese/CJK coverage intact. This allows the game to display both Thai and Japanese text simultaneously.
- **Thai Rendering:** Since the fonts are OTF with CFF outlines and contain proper `cmap` tables mapping Thai codepoints, the Scimitar engine renders Thai text using its built-in text layout engine. No PUA stacking is needed — the engine likely handles complex script layout natively.

---

## 5. Text Analysis
- **File Format:** Proprietary Scimitar binary format. Text data files (`2.data`, `3.data`) share the same container magic (`33 AA FB 57 99 FA 04 10`) as the font files.
- **Encoding:** UTF-8 embedded within the binary structure.
- **Thai Content:** Only 8 Thai sequences detected per file in full-file scan, suggesting the text data may be:
  1. Partially translated (work-in-progress mod), or
  2. Using a different encoding/compression that obscures the Thai bytes, or
  3. The Thai text is injected at runtime from a different source
- **Injection Method:** The BAT script reveals the workflow:
  ```batch
  quickbms_4gb_files.exe -w -r -r -r GRW.bms DataPC_patch_02.forge ModTH/Text
  quickbms_4gb_files.exe -w -r -r -r GRW.bms DataPC_extra.forge ModTH/Font
  ```
  The `-w` flag means **write mode** — QuickBMS is injecting the modified `.data` files back INTO the `.forge` archives, overwriting the originals at their exact byte positions.

---

## 6. Cross-Engine Comparison
The Scimitar/AnvilNext 2.0 engine is the most closed and difficult-to-mod engine in the entire Knowledge Base:

| Feature | Ghost Recon Wildlands (Scimitar) | Deathloop (Void) | RE2 (RE Engine) | Encased (Unity) |
|---|---|---|---|---|
| **Archive Format** | `.forge` (proprietary) | `.index` + `.resources` | Loose files | `.assets` |
| **Extraction Tool** | QuickBMS + custom BMS script | Custom patcher | REtool | UABEA / UnityPy |
| **Font Container** | OTF inside `.data` with header | Proprietary | Raw OTF renamed | Raw TTF |
| **Re-injection** | QuickBMS write-back | Binary patch | File copy | Asset repack |
| **Complexity** | ★★★★★ | ★★★★★ | ★★☆☆☆ | ★★☆☆☆ |

The key differentiator is the **QuickBMS write-back** technique. Unlike most engines where you replace files, Scimitar requires you to inject modified data at the exact byte offset within the forge archive.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด

### Font Pipeline:
1. **Extract fonts from forge:** 
   ```batch
   quickbms_4gb_files.exe GRW.bms DataPC_extra.forge output_folder
   ```
2. **Identify font .data files:** Look for files containing OTF magic `OTTO` (`4F 54 54 4F`) at offsets 390-420.
3. **Modify fonts:** Use FontForge to open the extracted OTF (skip the container header bytes) and add Thai glyphs. Save the modified OTF.
4. **Re-wrap in container:** Reconstruct the `.data` container by prepending the original header bytes back onto the modified OTF.
5. **Re-inject into forge:**
   ```batch
   quickbms_4gb_files.exe -w -r -r -r GRW.bms DataPC_extra.forge ModTH/Font
   ```

### Text Pipeline:
1. **Extract text .data from forge:**
   ```batch
   quickbms_4gb_files.exe GRW.bms DataPC_patch_02.forge output_folder
   ```
2. **Parse binary text format:** The `.data` files use a proprietary structure that requires reverse-engineering to locate string tables.
3. **Translate strings:** Replace English/other language strings with Thai UTF-8 text.
4. **Re-inject:**
   ```batch
   quickbms_4gb_files.exe -w -r -r -r GRW.bms DataPC_patch_02.forge ModTH/Text
   ```

---

## 8. Troubleshooting
- **Game crashes after forge injection:** The injected `.data` file must be the EXACT same size as the original. QuickBMS write-back does not resize entries. If the modified data is larger, it will overflow into adjacent entries and corrupt the forge.
- **Font not displaying Thai:** Verify that the modified OTF's `cmap` table properly maps the Thai Unicode range (U+0E00–U+0E7F).
- **QuickBMS "file too large" error:** Use `quickbms_4gb_files.exe` (the 4GB-capable version), not the standard `quickbms.exe`.
- **Wrong .data file selected:** The numerical filenames (`546`, `6674`, etc.) are internal Scimitar resource IDs. They may change between game versions.

---

## 9. Required Tools
| Tool Name | Purpose | Source |
|---|---|---|
| QuickBMS (4GB version) | Extracting and re-injecting `.data` from `.forge` archives | [QuickBMS] |
| GRW.bms script | Scimitar forge parsing script (included with mod) | [Modder-provided] |
| FontForge | Modifying OTF fonts to add Thai glyph coverage | [FontForge.org] |
| Hex Editor (HxD) | Inspecting container headers and verifying OTF offsets | [HxD] |

---

## 10. Extracted Assets
- **Font files:** Embedded OTF fonts could not be cleanly extracted as standalone installable files due to the Scimitar container's offset-relative table directory structure. See [EXTRACTION_NOTE.txt](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Scimitar_Engine/Games/Ghost_Recon_Wildlands/Assets/Fonts/EXTRACTION_NOTE.txt) for details.
- **Identified fonts:** DFPHSGothicJapaneseGR-Regular, DFGHSGothic-W5, DFPHSGothic-W5 (DynaFont CJK Gothic family, commercial)

---

## 11. M2M Protocol
**(สำหรับ AI Agent ที่ต้องการนำคัมภีร์ไปรันสร้างม็อดอัตโนมัติ)**

> ⚠️ **ข้อจำกัดสำคัญ:** เอนจิน Scimitar เป็นหนึ่งในเอนจินที่ AI ทำม็อดได้ยากที่สุด เนื่องจากต้องพึ่งเครื่องมือ `quickbms_4gb_files.exe` ซึ่งเป็นโปรแกรม Windows native ที่ต้องรันจริง

### 1. Automated Font Container Parser
```python
import struct

def find_otf_in_data(data_path):
    """Find OTTO magic in a Scimitar .data container and return its offset"""
    with open(data_path, 'rb') as f:
        data = f.read()
    
    # Search for OTTO magic in first 500 bytes (header area)
    for i in range(min(500, len(data) - 4)):
        if data[i:i+4] == b'OTTO':
            num_tables = struct.unpack_from('>H', data, i + 4)[0]
            if 5 <= num_tables <= 30:  # Sanity check
                return i, num_tables
    return None, None

def extract_container_header(data_path, otto_offset):
    """Extract the Scimitar container header (bytes before OTTO)"""
    with open(data_path, 'rb') as f:
        return f.read(otto_offset)

def rebuild_data_container(header_bytes, modified_otf_bytes):
    """Rebuild a .data container by combining header + modified OTF"""
    return header_bytes + modified_otf_bytes
```

### 2. Automated QuickBMS Injection Pipeline
```python
import subprocess
import os

def inject_into_forge(quickbms_path, bms_script, forge_path, mod_folder):
    """Re-inject modified .data files back into a .forge archive"""
    cmd = [
        quickbms_path,
        '-w', '-r', '-r', '-r',  # Write mode with overwrite
        bms_script,
        forge_path,
        mod_folder
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0, result.stdout, result.stderr
```

### 3. ข้อจำกัดสำคัญสำหรับ AI
1. **ขนาดไฟล์ต้องตรง:** ไฟล์ `.data` ที่แก้ไขแล้วต้องมีขนาดเท่ากับต้นฉบับทุกประการ (byte-exact) ไม่งั้น forge จะพัง
2. **ต้องมี QuickBMS:** AI ต้องตรวจสอบว่ามี `quickbms_4gb_files.exe` และ `GRW.bms` อยู่ในเครื่องก่อนเริ่มทำงาน
3. **ฟอนต์เป็นลิขสิทธิ์:** DynaFont เป็นฟอนต์เชิงพาณิชย์ ห้ามแจกจ่ายซ้ำ
