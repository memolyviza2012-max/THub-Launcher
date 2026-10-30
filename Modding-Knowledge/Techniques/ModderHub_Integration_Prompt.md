# MISSION: Game Translation Integration
You are tasked with integrating translation support for a specific game into the existing "Modder Hub" ecosystem.

## ECOSYSTEM OVERVIEW
The Modder Hub relies on a highly stable, production-ready translation engine located at `E:\Mod_Workspace\Modder_project\modder-hub\tools\flagship\`.
- **TStudio** (`TStudio/tstudio_app.py`): The GUI workspace for manual translation review and deployment.
- **TRun** (`TRun/trun_app.py`): The automated batch translation engine.
- **Core Modules** (`Core/tstudio_core.py`, `TStudio/file_converter.py`): Handles API requests, directory memory, and format conversions to a standard TStudio CSV format.

## ⛔ CRITICAL CONSTRAINTS (DO NOT BREAK THE CORE)
1. **DO NOT modify the core files** (`trun_app.py`, `tstudio_app.py`, `tstudio_core.py`, `file_converter.py`) to add game-specific logic. These files are highly stable.
2. **The Standardized Workflow:** Your scripts must act as a bridge. They should:
   - **Unpack:** Extract the game's text into the standard `TStudio CSV` format (or a standard TXT/JSON).
   - **Translate:** Let the user use the existing `TRun` or `TStudio` to translate the CSV. Do NOT write your own LLM translation loop.
   - **Pack:** Read the translated CSV and pack it back into the game's proprietary format.

## IMPLEMENTATION STRATEGY (Choose One)
- **APPROACH A (For simple text or easy proprietary formats):** Write a Custom Parser Plugin. Create a Python script intended for `TStudio/CustomParsers/` (e.g., `[GameName]_parser.py`) containing a `convert_to_csv(filepath)` function. This allows TStudio to natively load the file through its UI Plugin Manager.
- **APPROACH B (For heavy archive files like .pak, .dat, .arc):** Write Standalone CLI Scripts (`[GameName]_unpacker.py` and `[GameName]_packer.py`) that extract the inner text files, convert them to CSV for TStudio, and repack them.

## INSTRUCTIONS FOR YOUR TASK
1. Analyze the specific game's file structure and text formats.
2. Choose Approach A or B based on complexity, and write the extraction and packing scripts.
3. Provide the user with a clear step-by-step guide on how to install and run your scripts with TRun/TStudio.
