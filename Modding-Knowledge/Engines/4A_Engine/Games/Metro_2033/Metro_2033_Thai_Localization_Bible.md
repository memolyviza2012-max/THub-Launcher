# Metro 2033 - Thai Localization Modding Bible

## 1. Overview
This document outlines the reverse-engineered Thai localization mod for **Metro 2033**. Like its sequel Metro: Last Light, this game is built upon the **4A Engine**. The core mechanism for injecting translated assets (fonts, strings) involves overriding the base archives via the Virtual File System (VFS). This mod was developed by the creator "Ni TouchzZ".

## 2. Technical Stack
* **Game Engine:** 4A Engine
* **Archive Format:** `.vfs0` (Data Archive) / `.vfx` (VFS Index)
* **Localization Approach:** Archive Patching (Asset override)

## 3. Localization Pipeline and Mechanisms
The 4A Engine uses a structured file system packed into massive `.vfs0` chunks. Instead of modifying the original game archives, modders can append new archives and instruct the engine to load them. The engine will prioritize files found in the appended archives over the base files.

This mod is composed of two primary components:

### 3.1. `content.vfx` (Virtual File System Index)
* **Function:** This file serves as the master lookup table. It maps the directory paths and filenames to their specific byte offsets within the various `.vfs0` archives.
* **Modification:** The index has been modified to register a new archive (`content99.vfs0`) and redirect the pointers for localization and font files to this new archive. When the game asks for a text or font file, `content.vfx` tells it to read from `content99.vfs0` instead of the original archives.

### 3.2. `content99.vfs0` (Localization Data Archive)
* **Function:** This is the custom-built archive containing the localized assets. By using a high numbering scheme (`99`), it ensures that the 4A Engine treats it as a patch and prioritizes its contents over the base archives (e.g., `content.vfs0`, `content01.vfs0`).
* **Contents (Internal):** Inside this `.vfs0` archive, the standard 4A Engine localization files are present:
  * **Text Strings:** Serialized string tables (`texts\us.bin` or similar) containing the translated Thai text.
  * **Fonts:** Font textures (`.dds`) and configuration files (`.fnt` or `.vfx` font definitions) modified to include Thai glyphs. Without these, the engine cannot render Thai characters.

## 4. Required Tools for Modding
To replicate, modify, or update this mod, the following tools are necessary:
1. **4A Engine Extractor (MetroEX):** To unpack the `.vfx` and `.vfs0` files and extract the raw `texts.bin` and font `.dds` images.
2. **Text / Hex Editor:** Specialized tools designed for Metro's `.bin` text formats are usually required to safely translate and re-serialize the string tables.
3. **Image Editor:** Software like Photoshop or GIMP (with DDS support) for adding Thai characters to the font atlas.
4. **VFS Repacker:** A tool to bundle the modified fonts and texts into a new `content99.vfs0` archive and correctly update the `content.vfx` index with the new sizes and offsets.

## 5. Conclusion
The Metro 2033 Thai localization employs the standard 4A Engine patching technique. By supplying a custom `.vfs0` archive and modifying the `.vfx` index, the mod achieves full localization cleanly without destroying the original game files. This approach makes installation a simple drag-and-drop process for the end user.
