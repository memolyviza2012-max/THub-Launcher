# 🇹🇭 Space Hulk: Deathwing - Thai Localization Mod Workflow & Techniques

A repository for collecting techniques, tools, and code to create a Thai localization mod for **Space Hulk: Deathwing - Enhanced Edition** (Unreal Engine 4.14.3).

## 📌 Discovered Techniques (Knowledge Items - KI)

### 1. Font Fallback Technique (No need to Cook .uasset fonts)
Games developed with Unreal Engine 4 feature the Slate UI system, which natively supports Font Fallback. If the system cannot find Thai characters in the game's primary font, it will fall back to a secondary font configured at `Engine\Content\Slate\Fonts\DroidSansFallback.ttf`.
- **Method:** Take a standard Thai font with a `.ttf` extension, rename it to `DroidSansFallback.ttf`, and pack it into the Mod following the folder structure above.
- **Result:** The game can display Thai immediately without the hassle of loading Unreal Engine to Cook older composite fonts (`.uasset`), reducing the risk of crashes due to engine version mismatches.

### 2. Fixing the Pylocres Bug (Integer Hash Bug)
When importing a `CSV` file back into `.locres` using the `pylocres from-csv` command, you often encounter the error `struct.error: required argument is not an integer`.
- **Cause:** This happens because the `hash` field in the CSV file is read as String data, but the C++ structure's packing command requires Integer data.
- **Solution:** You must directly edit the code in the pylocres library (`cli.py`). On the line that retrieves `source_hash`, force it to convert to an Integer immediately:
  ```python
  # Code after fixing the bug
  source_hash = int(row.get("hash", 0)) if row.get("hash") else 0
  ```

### 3. AI Translation System (DeepSeek) & Glossary Injection
Since the Warhammer 40,000 series contains highly complex terminology, we created the script `run_translation_SHDW.py` which works with the DeepSeek API, featuring:
- **Glossary Injection:** Strictly embeds a specific terminology dictionary into the System Prompt (e.g., Space Marine = สเปซมารีน, Heretic = พวกนอกรีต, Genestealer = จีนสตีลเลอร์).
- **Tag Masking:** Prevents the AI from breaking the code by replacing codes like `<span color="...">` or formula variables with special Tags (e.g., `[TAG_0]`) before sending it to the AI for translation, and swapping them back once translation is complete.
- **Checkpoint System:** Translates the file row by row and saves to CSV immediately, preventing issues from power outages or API crashes midway.

## 📂 Workspace Structure

- `/Extracted/` - Folder storing the extracted original game files.
- `/Pack/` - Folder simulating the game's structure, prepared for packing into a .pak.
- `/Translation/` - Folder for storing exported CSV files and Thai translations.
- `/Tools/` - Folder for storing helper programs like `repak.exe`.
- `1_export_csv.bat` - Script to extract English text into a CSV.
- `2_import_csv.bat` - Script to assemble Thai text back into the .locres format.
- `3_pack_mod.bat` - Script to pack the final Mod files.
- `run_translation_SHDW.py` - AI translation script.

## 🚀 How to Use

1. Run `1_export_csv.bat` to extract the text.
2. Run `run_translation_SHDW.py` to command the AI to translate to Thai (or translate manually via Excel).
3. Once you are sure the Thai translation is fully correct, run the bug-fixing Python or Batch script to import the CSV back into Locres.
4. Run the command `repak pack Pack SpaceHulkGame-WindowsNoEditor_TH.pak -v 4.14` (or via script).
5. Place the resulting `.pak` file alongside the original game files in the Paks folder!

---
*Created and optimized for Thai Modding Community by Antigravity (AI Modding Assistant).*


---
**Created by:** [NodNuatTranslator](https://www.facebook.com/NodNuatTranslator/)
