# 📚 Knowledge Item (KI): Thai Language Techniques for Older Unreal Engine 4 (UE 4.14 and similar)

**Discovered Project:** Space Hulk: Deathwing - Enhanced Edition
**Engine Version:** Unreal Engine 4.14.3
**Issues Encountered:** Older games do not natively support the Thai language. Attempting to cook a `.uasset` font via older UE4 Editors is difficult, often leading to Engine Crashes or mismatched file structures, and the game refuses to read mod files from the `~mods` folder.

---

## 🛠️ Technique 1: Using Slate Font Fallback Trick

This technique is the "ultimate move" for injecting Thai into older UE4 games without touching a single original font file of the game.

### 💡 How it works:
Every version of Unreal Engine 4 has an emergency font system called "Slate Font Fallback", which the engine immediately calls upon when the game's primary font file does not support a particular character (e.g., Thai characters). By default, the engine looks for a file named `DroidSansFallback.ttf`.

### 📝 How to do it:
1. Find a font file that supports Thai (e.g., Tahoma, DB Helvethaica) and rename the file to **`DroidSansFallback.ttf`**.
2. Create a folder structure for packing the mod files like this:
   ```text
   Pack/
   └── Engine/
       └── Content/
           └── Slate/
               └── Fonts/
                   └── DroidSansFallback.ttf
   ```
3. You can pack this `Engine` folder together with our localization file (`.locres`).
4. **Result:** English characters will display with the game's normal, beautiful font, but when the game encounters Thai text, it will instantly pull our `DroidSansFallback.ttf` font to display instead!

---

## 🛠️ Technique 2: Forcing the Game to Read Mod Files using `_P.pak` (Patch File)

Older Unreal Engine games (such as 4.14) **do not yet have a system supporting the `~mods` folder**. Therefore, simply tossing mod files into the `Paks` or `~mods` folder will result in the game refusing to load them and displaying English as usual.

### 💡 How it works:
UE4 has a Patching System where the engine is hardcoded to always load `.pak` files with names ending in `_P` last. This allows that file to "Override" the core game files.

### 📝 How to do it:
1. When finished compressing files using the `repak` tool (must use `--version V3` for UE 4.14).
2. **Always rename the mod's .pak file to end with `_P`**.
   - ❌ *Incorrect:* `SpaceHulkGame-WindowsNoEditor_TH.pak` (The game will not load it)
   - ✅ *Correct:* **`SpaceHulkGame-WindowsNoEditor_P.pak`** (The game will 100% load and override)
3. Place the `_P.pak` file alongside the game's original `.pak` file in the `Content/Paks/` folder, without creating any subfolders.

---

## 🛠️ Technique 3: Packing Command for UE 4.14

To ensure that the generated `.pak` file has the original structure that the game can read (Legacy V3), we must specifically state the version when using the `repak` tool via Command Line like this:

### 📝 How to pack:
1. Open Command Prompt or create a `.bat` file.
2. Use this command to pack our `Pack` folder:
   ```cmd
   repak.exe pack Pack SpaceHulkGame-WindowsNoEditor_P.pak --version V3
   ```
   *Explanation:*
   - `pack`: Command to compress.
   - `Pack`: The source folder containing the entire mod folder structure.
   - `SpaceHulkGame-WindowsNoEditor_P.pak`: The destination file name set immediately as a Patch.
   - `--version V3`: **Forces** the use of the older Pak file pattern supported by UE 4.14.

---

## 📌 Summary
If you have to deal with translating early generation Unreal Engine 4 games (below 4.19), always use this proven formula:
1. Sneak the `DroidSansFallback.ttf` font into `Engine/Content/Slate/Fonts/`.
2. Pack the files to match the original version (e.g., `--version V3`).
3. Rename the mod file to end with `_P.pak` and overwrite directly in the Paks folder.


---
**Created by:** [NodNuatTranslator](https://www.facebook.com/NodNuatTranslator/)
