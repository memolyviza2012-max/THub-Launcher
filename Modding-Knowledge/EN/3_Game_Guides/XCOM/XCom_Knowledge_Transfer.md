# XCOM Franchise Thai Modding Knowledge Transfer

This document compiles the knowledge gained from creating the Thai localization mod for XCOM: Enemy Unknown & Within, to serve as a database for the AI when modding sequels (such as XCOM 2 and XCOM: Chimera Squad).

## 1. Engine Structure and UI System
- **Engine:** The first XCOM (and XCOM 2) uses Unreal Engine 3 (or a modified version) along with the **Scaleform (Flash/ActionScript)** UI system.
- **Font System:** Fonts used in the game are compiled into .upk (Unreal Package) files, such as gfxfonts_ch_SF.upk or XcomThaiFont.upk.
- **Original Thai Issues:** Scaleform in older games often mishandles floating Thai vowels and tone marks (top/bottom vowels), causing vowels to overlap or float in the wrong positions.

## 2. Fixing Floating Vowels (PUA Mapping)
Since the game does not support standard floating Thai vowels (e.g., Mai Tho over Sara I), we must use the **PUA (Private Use Area)** technique:
1. **Font Modification:** We take a Thai font and modify its character table (Glyphs) by mapping combined vowels (e.g., ฟ + ิ + ้) to empty slots in the Unicode table (PUA range, such as E000 onwards), and then generate a new .swf or .upk file.
2. **Text Modification:** We need to write a Python script to scan all translated Thai text and convert Thai characters with overlapping vowels into Unicode PUA codes, matching the font we created.
3. *Lesson:* Never use ActionScript to convert PUA in real-time within XCOM, as the game has script execution limits, which causes text to disappear. Using Python to convert .int files in advance is the most stable method.

## 3. Localization File Structure
- Language files in Unreal Engine 3 have the .int extension (for English).
- The game uses a Priority system for loading .int files:
  - **Priority 1 (Highest):** `Documents\My Games\XCOM...\XComGame\Localization\INT` folder
  - **Priority 2:** `Steam XComGame\Localization\INT` folder
  - **Priority 3:** `Steam Engine\Localization\INT` folder
- *Caution:* You must separate system files (GFxUI.int, Engine.int) into the Engine folder, and story/subtitle files (Subtitles.int, XComGame.int) into the XComGame folder correctly. Otherwise, the game will pull the wrong file type and display the original language.

## 4. Subtitle Issues in Cutscenes (Subtitles)
- Even after translating Subtitles.int, cutscene subtitles might still turn into squares (Tofu) because the game locks the font name for subtitles.
- **Solution:** You must edit the DefaultEngine.ini (in the Steam folder) and XComEngine.ini (in the Documents folder).
- Search for `SubtitleFontName=` and change it to point to our Thai font (e.g., `SubtitleFontName=XcomThaiFont.SubtitleThai`).

## 5. Tooling Development (Installer & Translator)
- **Translation:** Use Python + DeepSeek AI (via API) to help translate .int files, which can translate tens of thousands of lines in a short time.
- **Installation:** It should be written as a .exe program using Python (Tkinter + PyInstaller) so the installer can automatically find the game's location in the Registry (Steam) and copy files to both the game folder and the Documents folder. This reduces the burden on the user (because XCOM's file system is too complex for 100% accurate manual installation).


---
**Created by:** [NodNuatTranslator](https://www.facebook.com/NodNuatTranslator/)
