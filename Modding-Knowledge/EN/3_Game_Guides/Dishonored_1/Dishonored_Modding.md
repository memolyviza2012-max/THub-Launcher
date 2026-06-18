# 🎮 Dishonored 1 (2012) - Modding & Localization Guide

This repository contains the accumulated knowledge, tools, and scripts required to successfully mod and localize **Dishonored 1 (PC, Steam)**. 
Dishonored utilizes a highly modified **Unreal Engine 3** framework that presents unique challenges for modders, particularly regarding byte order and UI fonts.

---

## 🏗️ 1. Technical Constraints & Engine Specifications

The primary hurdle in modding Dishonored is that its package files (`.upk`) are compiled using a **Big-Endian Byte Order**. Standard UE3 modding tools (which assume Little-Endian architecture) will fail to read or unpack these files correctly.

* **Impact:** Custom Python scripts (like `binary_be.py` and `upkreader_be.py` included in the `Tools` folder) must be used to handle byte-swapping when reading or writing strings to the `.upk` files.

---

## 🔤 2. Localization Structure (Text Injection)

In-game text, subtitles, and object names are embedded inside `.upk` packages within the `CookedPCConsole` and `DLC` directories.

- **String Format:** The engine expects **UTF-16LE** encoding.
- **String Length Rule:** In Unreal Engine 3, if a string uses 2 bytes per character (which is required for non-Latin characters like Thai, Russian, or Asian languages), the engine's internal String Length integer **must be a negative number** (e.g., a 10-character string will have a length integer of `-11` to account for the Null Terminator).
- **Tooling:** The provided `subedit.py` (inside `Tools/dishonored-toolkit`) automatically calculates this negative length and safely writes the binary data back into the UPK.

### ⚠️ Common Issue: "??????" Corrupted Text
If a text editor saves your extracted `.yaml` translation files in the wrong encoding (e.g., ANSI instead of UTF-8), or if your extraction script encounters unrecognized characters, the game text will render as `?????`.
* **Fix:** You must replace the corrupted lines with the original English text (or a clean backup) in the `.yaml` file before packing again. Packing a corrupted file will cause the game to crash or render gibberish permanently in that package.

---

## 🎨 3. UI and Font Modification (Scaleform GFx)

Dishonored uses **Scaleform GFx (Flash/SWF)** to render its menus, UI, and fonts.
While you can open the `.upk` or `.gfx` files in **JPEXS Free Flash Decompiler** to view the internal `.swf` structure, **you cannot simply click "Save" in JPEXS**. JPEXS does not natively understand the proprietary Big-Endian UE3 container and will throw a saving error.

### How to Inject Custom Fonts
There are two primary methods to inject new TrueType (`.ttf`) fonts into the game:

1. **The Automated Method (Recommended):**
   Use the `fontEdit.py` script provided in `Tools/dishonored-toolkit`. This tool bypasses JPEXS entirely. It reads your `.ttf` font, generates a Texture2D atlas (`.dds`), calculates the glyph mapping, and injects it directly into the game's UI `.upk` files.
   
2. **The Manual Extract & Patch Method:**
   - Run `unpack.py` to extract the `.upk` container into individual files.
   - Find the extracted `.SwfMovie` file and open it in **JPEXS**.
   - Make your font or UI modifications, then use JPEXS's "Save As" feature to save a new file (e.g., append `_patched` to the name).
   - Run `python patch.py [Original_File.upk]` to recalculate byte offsets and safely re-inject your patched `.SwfMovie` back into the UPK container.

---

## 📁 4. Provided Tools and Scripts

Included in this directory are two folders that contain everything needed to build a complete mod:

### 🛠️ `Tools/`
Contains the core low-level utilities:
- **`decompress.exe`**: A standalone executable used to decompress LZO-compressed UPK files before any hex editing can take place.
- **`dishonored-toolkit`**: A comprehensive suite of Python scripts designed specifically for this game. It handles Big-Endian binary parsing, font generation (`fontEdit.py`), and YAML-based text injection (`subedit.py`).

### 💻 `Scripts/`
Contains automation scripts used for bulk processing during a full localization project:
- **`pack_all.py`**: A macro script that crawls through your entire translation workspace, decompresses the original `.upk` files, runs `subedit.py` to inject your translated `.yaml` files, and outputs the final, game-ready `.upk` files into a release folder.
- **`check_yaml_all.py`**: A validation script that scans all `.yaml` translation files for YAML syntax errors or corrupted encoding (like `?????`) before you initiate the lengthy build process.


---
**Created by:** [NodNuatTranslator](https://www.facebook.com/NodNuatTranslator/)
