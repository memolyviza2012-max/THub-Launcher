# Detailed Steps for XCOM: Enemy Unknown & Within Thai Modding

This document outlines the step-by-step process from start to finish for extracting content, translating, editing fonts, and creating an installer for XCOM (Unreal Engine 3 + Scaleform).

## 1. Tools Preparation
- **JPEXS Free Flash Decompiler (FFDec):** Used to open and edit .gfx and .swf files (extracting UI fonts from the gfxfonts_ch_SF.upk file).
- **UDK (Unreal Development Kit):** Used to build cutscene fonts (creating .upk files).
- **Python 3:** Used for writing scripts to extract text, translate, convert PUA vowels, and build the installer.

## 2. Extracting and Editing UI Fonts (Scaleform)
The main UI font file of the game is `XComGame/CookedPCConsole/gfxfonts_ch_SF.upk`.
1. Use a Python script (`inject_swf.py`) to extract the `gfxfonts_ch_SF.swf` file from the .upk.
2. Open the .swf file with JPEXS.
3. Take a Thai font (e.g., DB Helvethaica) with a modified PUA table (moving floating vowels to empty Unicode slots) and Replace the original font (e.g., Alpha Mack, FPF).
4. Embed all Thai characters into the font (Embed Characters).
5. Save the .swf file and use the Python script to restore the .swf file back into the .upk.

## 3. Creating Fonts for Subtitles (Cutscenes)
Cutscene subtitles use fonts from Unreal Engine, not Scaleform.
1. Open UDK and create a Texture from the Thai PUA font (using UDK's Font Creation system).
2. Create a new Package file named `XcomThaiFont.upk` and set the font name inside as `SubtitleThai`.
3. Save it and place it in the game's `CookedPCConsole` folder.

## 4. Extracting Text and Translating (Localization)
All text files are located in `XComGame/Localization/INT` with the .int extension.
1. Write a script to scan for all .int files and extract the English text to store in a CSV format.
2. **Translation:** Send the text to be translated via the DeepSeek API, ensuring the AI strictly maintains code structures and variables (e.g., `%s`, `\n`, `<font>`).
3. **PUA Conversion:** Once translated, the Python code must immediately run the text through the `apply_pua_mapping` function to convert overlapping vowels and tone marks into PUA codes, matching the font we created in step 2.

## 5. Forcing Cutscene Fonts (Engine.ini)
Even with translated files, the game will still pull original fonts for cutscenes.
- You must edit `DefaultEngine.ini` (in the Steam folder) and `XComEngine.ini` (in Documents).
- Change the line value: `SubtitleFontName=XcomThaiFont.SubtitleThai`

## 6. Creating a One-Click Installer
XCOM has a complex behavior where it loads language files from the `Documents/My Games/XCOM...` folder before loading from the game folder in Steam.
- Write the `installer_gui.py` script so the program automatically finds the game's location from the Steam Registry.
- Automatically locate the Documents folder.
- Copy the translated .int files and font files to overwrite both the Steam folder and the Documents folder.
- Write a command in Python to penetrate and automatically edit the `SubtitleFontName=` value in both .ini files.
- Use PyInstaller to package all files and source code into a single, complete .exe file.


---
**Created by:** [NodNuatTranslator](https://www.facebook.com/NodNuatTranslator/)
