# GameMaker Studio Modding & Translation Guide

## 1. Engine Overview
GameMaker Studio (GMS) is a popular 2D game engine. 
Games built with GMS typically pack all of their assets (Graphics, Audio, Code, Strings, Fonts) into a single large binary archive file, usually named `data.win` (on Windows) or `game.ios` / `game.unx` on other platforms.

## 2. Translation Mechanism
Because all strings are baked into `data.win`, you **cannot** simply open the game folder and find text files like `.json` or `.csv`.
To translate a GameMaker game (like *Stoneshard*, *Undertale*, *Katana Zero*), you must:
1. Extract the strings from `data.win`.
2. Translate the extracted strings.
3. Repack (Import) the translated strings back into `data.win`.
4. (Optional but often necessary) Modify the game's embedded fonts to support your target language (e.g., Thai fonts).

## 3. Essential Tools
The standard and most powerful tool for this process is **UndertaleModTool (UTMT)**.
- **UTMT GUI**: Allows you to open `data.win`, view all assets, edit code, and manually run scripts.
- **UTMT Scripts**: UTMT comes with built-in scripts specifically for translation:
  - `ExportAllStrings.csx`: Exports all game text to a `.txt` or `.csv` file.
  - `ImportAllStrings.csx`: Imports your translated text back into the `data.win`.
  - `ExportFontData.csx` / `ImportFontData.csx`: Used for modifying sprite-based fonts.

## 4. Step-by-Step Translation Workflow (Manual)
1. Open UndertaleModTool.
2. File -> Open -> select `data.win`.
3. Go to the **Scripts** menu at the top.
4. Run `ExportAllStrings.csx`. It will prompt you to save a text/csv file.
5. Open the exported file in **TStudio** or any translation tool.
6. Translate the text (Do not modify the string IDs or format structure).
7. Save the translated file.
8. Back in UTMT, run `Scripts` -> `ImportAllStrings.csx` and select your translated file.
9. File -> Save -> overwrite `data.win` or save as a modded version.

## 5. Automation Potential
For advanced modding hubs (like TStudio), UTMT provides a command-line interface (`UndertaleModCli.exe`). 
Modding tools can call this CLI silently in the background to automatically run the export/import scripts without the user having to touch UTMT directly.
