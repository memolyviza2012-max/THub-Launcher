# Metro: Last Light - Thai Localization Modding Bible

## 1. Overview
This document details the reverse-engineered localization pipeline for the Thai translation mod of **Metro: Last Light**. The game utilizes the **4A Engine**, which employs a highly modular Virtual File System (VFS). The localization is achieved by providing a patch archive containing translated texts and fonts, along with a modified index file to load them.

## 2. Technical Stack
* **Game Engine:** 4A Engine (Proprietary engine used in the Metro series)
* **Archive Format:** `.vfs0` / `.vfx` (4A Engine Virtual File System)
* **Localization Approach:** Archive Patching (Asset override)

## 3. Localization Pipeline and Mechanisms
Unlike Unity games which can easily support code injection via BepInEx, the 4A Engine relies heavily on packed archives. The mod achieves localization by overriding the game's base assets using the engine's built-in patching mechanism.

The provided mod directory contains two crucial files:

### 3.1. `content.vfx` (Virtual File System Index)
* **Function:** This file acts as the master index or table of contents for the game's file system. It contains the directory structure, filenames, file sizes, and the exact byte offsets pointing to where the data is stored in the large data archives (e.g., `content.vfs0`).
* **Modification:** The modded `content.vfx` has been altered to instruct the engine to prioritize and load custom files (fonts and texts) from the new `patch_001` archive instead of the base game archives. 

### 3.2. `patch_001` (Patch Data Archive)
* **Function:** This is a raw data chunk archive (structurally similar to a `.vfs0` file). The 4A Engine is designed to load archives sequentially. Files found in later archives (like patches) will override files with the same name in the base archives.
* **Contents (Internal):** Inside this patch archive, the modders have packed the specific assets required for the Thai localization. Although we cannot see inside it without a 4A Engine extraction tool, it typically contains:
  * **Text Strings (`texts\us.bin` or similar):** The localized string tables containing the translated Thai dialogues, menus, and subtitles.
  * **Fonts (`content\fonts\`):** Modified bitmap fonts (usually consisting of `.fnt` config files and `.dds` texture atlases) that include Thai characters. Without these, the Thai text in the `.bin` files would display as unreadable characters or boxes.

## 4. Required Tools for Modding
To extract, modify, and repack the localization files for Metro: Last Light, specialized 4A Engine modding tools are required:
1. **MetroEX / 4A Engine Extractor:** A tool required to unpack the `.vfx` and `patch_001` archives to view or extract the raw `texts.bin` and `.dds` font textures.
2. **Text Editor / Hex Editor:** For modifying strings. Sometimes specialized Metro text tools are needed to properly serialize the `.bin` string tables back into the format the engine expects.
3. **Image Editor (Photoshop / GIMP):** Equipped with a DDS plugin to edit the font texture atlases and draw the Thai glyphs.
4. **VFS Repacker:** A tool capable of generating a valid `patch_001` archive and rebuilding the `content.vfx` index with the correct new file offsets and sizes.

## 5. Conclusion
The Metro: Last Light Thai localization uses a classic "Asset Override" technique native to the 4A Engine. By supplying a modified VFS index (`content.vfx`) and a compiled patch archive (`patch_001`), the mod safely injects the Thai language strings and fonts without destructively overwriting the massive base game `.vfs0` files.
