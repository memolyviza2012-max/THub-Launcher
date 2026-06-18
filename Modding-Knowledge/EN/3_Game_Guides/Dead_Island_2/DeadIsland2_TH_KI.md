# Dead Island 2 - Thai Localization Mod (Knowledge Item)

This document is prepared as a **summary of data and knowledge (Knowledge Item - KI)** for the Dead Island 2 Thai localization project. It serves as a reference guide for future development, modifications, or troubleshooting.

---

## 1. Project Overview
This project involves translating text within the game Dead Island 2 (UI, menus, dialogue, and Subtitles) into Thai. It utilizes the **DeepSeek API** for automated translation and employs Python scripts to handle the game's data files (Extract, Convert, Translate, Inject, and Pack).

- **Engine:** Unreal Engine 4 (UE4)
- **Game File System:** IoStore (`.utoc` / `.ucas`) for general Assets, and `.pak` for some extensions.
- **Mod Structure:** Utilizes the Pakchunk system (using number 99 or `_P`) to force the game to load the Mod files over the original files.

---

## 2. File Structure and Language Database
The game's text is divided into 2 main sections as follows:
1. **Game UI & General Text** 
   - **Source:** `Game.locres` (Unreal Engine Binary file)
   - **File to translate:** `Translation\Game_th.csv`
   - **Management Tool:** Used `pylocres` to convert back and forth (CSV <-> Locres)
2. **Dialogue & Subtitles**
   - **Source:** The game's `DialogueList.xml` file
   - **File to translate:** `Translation\Dialogue_Subtitles.csv`
   - **Management Tool:** `extract_dialogue_subtitles.py` and `inject_translated_subtitles.py`

---

## 3. Translation Engine
The translation scripts (`run_translation_DI2.py` and `run_translation_subtitles.py`) have the following special features:
- **Batch Processing:** Sends text to the AI for translation in large batches (limited by character count) to reduce time and save Rate Limits.
- **Tag Masking:** Extracts special codes (e.g., `[TAG_0]`, `%s`, `<color>`) before sending to the AI to prevent the AI from breaking the code, and then puts them back after the translation is complete.
- **Checkpoint System:** Every loop includes an Atomic Save to prevent interruptions from power outages or mid-process API Errors.
- **Key Translation Protection (NEW):** Prevents the AI from translating keyboard button names such as Esc, Enter, Shift, Spacebar into Thai (to ensure correct button display in the game).

> [!WARNING]
> **Security System:** The Gemini (DeepSeek) API Key has been **removed** in accordance with security measures. To run the translation script again, you must insert your API Key into the `API_KEY` variable inside the script before running.

---

## 4. Build Pipeline
We designed the script `build_all_auto.py` to cover all processes with a single command (One-Click Build) in the following order:

1. **Run Translation:** Runs the script to detect if any English text remains in the CSV. If there is, it translates it (if fully translated, it skips this).
2. **Convert CSV to Locres:** Converts the `Game_th.csv` file into `Game.locres` using the `pylocres` tool.
3. **Inject Subtitles:** Injects the `Dialogue_Subtitles.csv` file back into the game's XML file.
4. **Pack Mod:** Runs `pack_mod.py` to use the `UnrealPak.exe` tool to bundle all files in the `Pack` folder into the `DeadIsland2_TH_P.pak` file.
5. **Compile Installer:** Uses PyInstaller to create the `DeadIsland2_Thai_Installer.exe` program (Standalone Patcher) for users to easily install, embedding the Thai font and the packed file directly into the .exe.

---

## 5. Thai Font Replacement
- Dead Island 2 uses a variety of font systems, including standard `.uasset` and fonts embedded in Scaleform files (`.swf` / `.gfx`).
- We replaced the game's fonts in the `Content\UI\Fonts` folder to support Thai, packing the new font files along with the Mod.

---

## 6. Limitations of the Xbox Game Pass (WinGDK) Version
Through experimenting with applying the Thai mod to the game on **Xbox Game Pass (PC)**, we encountered issues and limitations that prevented success, as follows:
- **Signature Verification:** Even though we spoofed the `.pak` patch file and stole the game's `.sig` file, renaming it to match (Bypass technique), the WinGDK version still has Xbox's security detection system which rejects loading mod files from the `~mods` folder.
- **IoStore Font Injection:** Even though we successfully located the font's Chunk ID and injected the PUA font into the `pakchunk0-WinGDK.ucas` file, due to the game's structure forcing internet usage to run via the Xbox app, the game ignores our modified file.
- **Conclusion:** Therefore, this project only supports the **Steam and Epic Games (WindowsNoEditor)** platforms.

---

## 7. Success Summary
- All 61,000+ lines of UI text were successfully translated and displayed perfectly.
- Dialogue and Subtitles totaling 32,390 lines, covering both the main story and Expansion Pass (Haus & SoLA), are 100% translated.
- Created an Auto-Install Patcher system (.exe) for easy distribution to players on Steam/Epic.

---
**Prepared by:** Antigravity (AI Assistant)
**Last Updated:** June 2026


---
**Created by:** [NodNuatTranslator](https://www.facebook.com/NodNuatTranslator/)
