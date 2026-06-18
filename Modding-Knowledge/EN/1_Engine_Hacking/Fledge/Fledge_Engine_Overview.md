# The Surge (FLEDGE Engine) - Thai Localization Research & Post-Mortem

This repository documents the extensive reverse-engineering efforts to implement a native Thai localization mod for **The Surge**, which runs on the custom **FLEDGE Engine**. 

While the project was ultimately halted before a fully functioning visual text replacement was achieved, the research uncovered deep insights into how the FLEDGE engine handles data packing, text rendering, and memory management. This documentation is provided in hopes that future modders can pick up where we left off.

## 1. Data Structure & Packaging

### The `.dat` and `.toc` System
- Game assets are stored in `.dat` files (e.g., `data_bin_0.dat`).
- The `data_bin.toc` acts as the Table of Contents, containing hashes, offsets, and compressed sizes.
- **CRITICAL CONSTRAINT:** The TOC file is strictly integrity-protected. Any modification to `data_bin.toc` causes the game to crash on startup. This means we cannot add new files, change offsets, or change the compressed size of existing blocks.

### LZ4 Compression
- Assets inside `.dat` files are individually compressed using **LZ4 Block format** (specifically `lz4.frame` with `BLOCKSIZE_MAX256KB`).
- Because of the TOC integrity check, **in-place file replacement** is the only viable modding method. 
- You must compress the modified file, and if it is smaller than the original compressed size, you must pad the remaining space.
- **Padding Method:** Padding with zero bytes (`0x00`) works perfectly for most files (like `fonts.bin` and `english.bin`). However, attempting to pad with LZ4 Skippable Frames caused the game engine to hang/crash when processing certain files like `russian.bin`.

## 2. Text & String Management

### String Files (`.bin`)
- Localization strings are stored in binary files like `english.bin`, `russian.bin`, etc.
- The format is relatively simple: a 32-bit integer header (where the MSB `0x80000000` indicates a string, and the lower 31 bits indicate string length), followed by UTF-8 encoded text, and then padded to 4-byte alignment.
- **Modifying Strings:** We successfully wrote Python scripts (`rebuild_v15.py` and `deploy_english_cyrillic.py`) that decompress `english.bin`, inject translated UTF-8 strings (truncating or spacing out untranslated strings to maintain the strict compression size budget), recompress, and zero-pad the gap.

### The "Cipher" Approach
Because editing `fonts.bin` IDs breaks the internal indexing, the most viable path forward was a "Cipher String Patching" approach:
1. Translate English to Thai.
2. Map Thai codepoints (0x0E01+) to a supported language block (e.g., Cyrillic `0x0400+` or Japanese `0x3041+`).
3. Inject the "Ciphered" text into `english.bin` or `russian.bin`.
4. Replace the corresponding glyphs (Cyrillic/Japanese) in the font atlas with Thai shapes.

## 3. Font Rendering System (SDF)

### `fonts.bin`
- Contains the glyph metrics and UV coordinates.
- Glyphs are defined in 32-byte records: `[4-byte Codepoint] [7x 4-byte Floats for X, Y, W, H, X-Offset, Y-Offset, X-Advance]`.
- **The Indexing Problem:** Changing a codepoint ID directly in the 32-byte record causes the glyph to render as blank. This strongly implies the engine uses an earlier indexing structure (like a hash map or binary search tree) to look up codepoints. Modifying just the record ID breaks the lookup.

### Font Atlases (DDS)
- The engine uses **Signed Distance Field (SDF)** rendering for crisp text at any resolution.
- Atlases are stored as LZ4-compressed DDS files (e.g., `arial_sdf`, `fira_sans_regular_sdf`, `nanum_gothic_sdf`).
- The atlases are typically 2048x1024 or 2048x2048 in `DXT5` or `R8/A8` format.
- Replacing glyphs visually requires generating an SDF texture for the Thai font and blending it into the existing DDS atlas over the chosen target slots (e.g., Japanese or Cyrillic slots).

## 4. Failures & Roadblocks

1. **Memory Patching via DLL:** We attempted to hook `dinput8.dll` and scan the process memory to replace UTF-16 strings at runtime. While the DLL successfully found and patched the strings in memory, the game's UI text remained English. This indicates that the FLEDGE engine either rasterizes the text into texture caches very early (A8 UI surfaces) or uses an internal localized string buffer that we failed to locate.
2. **Missing Glyphs on Cipher injection:** When injecting Cyrillic or Japanese codepoints into `english.bin`, the game rendered blank text. This suggests that when the game runs in English mode, it does not load the glyphs/atlases for other language blocks into GPU memory to save VRAM. 
3. **Russian language Crash:** Attempting to inject into `russian.bin` and force the game to load Russian language via `language.ini` resulted in a crash, likely due to strict size/hash checks on that specific file, or an issue with the LZ4 zero-padding handling for that specific block.

## 5. Future Recommendations for Modders

If someone wishes to continue this project, the recommended path is:
1. **Understand `fonts.bin` indexing:** Reverse-engineer the header of `fonts.bin` to understand how codepoints are mapped to the 32-byte glyph records. If you can update the index, you can add native Thai codepoints (`0x0E01+`) directly.
2. **DDS Atlas Injection:** Build a reliable pipeline to decompress the LZ4 DDS atlas, paste Thai SDF glyphs over unused Latin/Extended glyphs (e.g., accented European characters which *are* loaded in English mode), and recompress exact-size.
3. **Cipher via Accented Latin:** Instead of mapping Thai to Cyrillic or Japanese (which get unloaded in English mode), map Thai characters to Extended Latin characters (e.g., `À, Á, Â, Ã, Ä, Å`) that are guaranteed to be loaded in the English atlas.

## Scripts Included in this Repo
- `patch_safe.py`: Safely modifies `fonts.bin` to map IDs.
- `deploy_english_cyrillic.py` & `deploy_english_japanese.py`: The cipher injection scripts that handle LZ4 exact-size repacking and zero-padding.
- `dinput8_thai.cpp`: The source code for the runtime memory string patcher attempt.

---
*Documented on May 31, 2026. Good luck to future hackers!*


---
**Created by:** [NodNuatTranslator](https://www.facebook.com/NodNuatTranslator/)
