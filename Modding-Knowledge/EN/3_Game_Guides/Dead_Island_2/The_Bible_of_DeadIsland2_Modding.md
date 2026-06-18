# The Modding Bible: Hacking the Dead Island 2 Thai Localization System

This bible (Knowledge Item - KI) compiles the **"Advanced Techniques"** used to break through the structure of the game Dead Island 2 (Unreal Engine 4.27) to force the game to display Thai perfectly. It serves as a Case Study for modding modern games that use the **IoStore** file packing system.

---

## 1. The Problem with Modern Games (IoStore System)
Games developed with later versions of Unreal Engine 4 (including UE5) abandon the standard `.pak` system for storing main game files, shifting instead to the **IoStore** system, which consists of two types of files:
- **`.utoc` (Table of Contents):** A directory that stores file locations (Offset/Length) and Chunk ID codes.
- **`.ucas` (Container):** A massive data block (often as large as 3-5 GB) that compresses and encrypts all files using **AES Encryption**.

**Problem:** Inserting a Thai font file with the `.uasset` extension into the `~mods` folder using the classic method **"will not work"**, because the engine will always pull the main font from the IoStore system first, causing players to see square boxes (Tofu) instead of Thai.

---

## 2. Technique 1: Surgical Font Injection into IoStore (Direct UCAS Injection)
To solve the issue of the game not reading the Thai font, we must directly hack the game's system files using Python with the following techniques:

1. **AES Decryption:** You must know the AES Key for Dead Island 2 to be able to read the structure.
2. **Calculate Chunk ID:** Convert the font's Path name (e.g., `DeadIsland/Content/DI2/UI/Fonts/fonts_en`) into a Hash (12 Bytes) to locate which line the index in `.utoc` points to.
3. **Append (Add to the end of the file):** Instead of overwriting the original font in `.ucas`, which risks corrupting the data, we use the method of **"taking the Thai font file (`fonts_en.uasset`) and pasting it at the very end of the `pakchunk0-WindowsNoEditor.ucas` file."**
4. **Rewrite Offset:** Go back and modify the numbers in the directory (`.utoc`) by changing the location (Offset) of the original font to jump and point to the **"end of the file"** where we just appended the Thai font instead.

*This technique prevents us from having to distribute a 3GB `.ucas` file for players to download. Instead, we only distribute a Python script a few KB in size that surgically modifies the files directly on the player's machine.*

---

## 3. Technique 2: Digital Signature Bypass
Even though we have successfully injected the font, the Thai text we translated (stored in the `Game.locres` file and packed as `.pak`) will still be rejected and not loaded by the game because the engine has a **Signature Check** system.

**Solution:**
- UE4's detection system looks for a `.sig` file whose name matches the `.pak` file.
- We use the method of **"stealing"** the game's original `.sig` file (e.g., `pakchunk_default-WindowsNoEditor_P.sig`) and **Renaming** it to match our mod file (e.g., `pakchunk_default-WindowsNoEditor_Thai_P.sig`).
- With just this, the engine is tricked into believing our Thai mod is an official update patch from the developers and allows the Thai language to load and display.

---

## 4. Technique 3: Localization Pipeline
Making Thai display perfectly in the game requires managing two different text file formats:

1. **UI and Item System (`.locres`)**
   - General game text is compressed into a Binary file with the `.locres` extension.
   - Technique: Use the `pylocres` program to unpack the file into a `.csv` -> translate it using AI (applying Masking to hide color codes and variables) -> then use `pylocres` to compress it back into `.locres` as it was.
2. **Dialogue Subtitle System (`.xml`)**
   - All subtitles in Dead Island 2 are embedded within the Tag structure of the `DialogueList.xml` file.
   - Technique: Write a Python script using the `xml.etree.ElementTree` library to search for the original Node and insert a `<String>` Node containing the Thai translation right alongside the English one, allowing the game to pull up and display Thai subtitles.

---

## 5. Technique 4: Repacking Files Back into the Game (Repacking via UnrealPak)
Once the translation files and subtitles are prepared, all files are arranged into a folder structure that matches the original (e.g., `DeadIsland/Content/Localization/...`) and then must be bundled into a `.pak` file.

- **Tool Used:** `UnrealPak.exe` (Standard tool for Unreal Engine)
- **Creating a Response File:** Instead of typing long, complex commands, we use a Python script (`pack_mod.py`) to sweep through the list of all files in the folder and generate a `response.txt` file that accurately specifies the source and destination paths (Mount Point) of the files.
- **Compression:** Run `UnrealPak.exe` by pulling data from `response.txt` along with the `-compress` parameter so the mod file is compressed to the smallest possible size.
- **Naming Convention:** For the game to agree to load the mod files and overwrite the original files, the packed file must always be named ending with `_P` (Patch Chunk), such as `DeadIsland2_TH_P.pak`.

---

## 6. Technique 5: Creating a Standalone Smart Installer
Since the process of injecting `.ucas` files is complicated and ordinary players cannot do it themselves, we employ the **PyInstaller** technique.

- **Embed files into the executable:** Use PyInstaller's `--add-data` function to pack the Thai font file, the `.pak` file containing translated text, and the surgical script together into a single `.exe` file (Standalone).
- **Auto-Detect:** Write the script to automatically locate the Dead Island 2 folder on the player's machine (supporting both Steam and Epic).
- **Result:** Turns a complex hacking process into a single Double Click by the user.

---

## Conclusion
This project is a fusion of the disciplines of **Reverse Engineering** (unpacking .ucas/.utoc structures), **Cryptography** (Bypassing .sig and AES), and **Automation** (Python + AI Translation). This results in a mod with a compact file size (20MB) that can perfectly display the Thai language in a massive AAA game.

*(This Knowledge Item was prepared by Antigravity AI - June 2026)*


---
**Created by:** [NodNuatTranslator](https://www.facebook.com/NodNuatTranslator/)
