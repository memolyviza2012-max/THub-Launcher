# 📘 Dying Light 2 Thai Localization Modding Bible (The Modding Bible)

This document gathers all the knowledge used to create a 100% successful Thai localization mod for Dying Light 2 (C-Engine), fully resolving broken English characters and floating/sinking vowel issues.

---

## Part 1: Font System Management (Font Modding)

The main issue with C-Engine is that it **does not support the display of overlapping Thai vowels** (such as Sara I, Mai Ek, Mai Tho). If left as is, vowels will float or overlap until they become unreadable. Furthermore, using old mods (like NooneTranslator) involves **"hijacking"** the original English font images, which results in certain English characters (such as `%`, parentheses) turning into Thai characters instead.

### 1. Creating a New Atlas Image (Texture)
**Never overwrite the game's original fonts.** The correct method is:
1. Use a Python script (`Pillow`) to create a brand new `4096x4096` image.
2. Draw all correct English characters onto it.
3. Draw basic Thai characters.
4. Draw **"PUA (Private Use Area) characters"**, which are characters we've already combined with vowels (e.g., ด + ํ = ดํ), and place them in the empty slots of the Unicode table (e.g., `F269`).
5. Save the image and convert it into a `.dds` (DirectDraw Surface) file in `BC3 (DXT5)` format.
6. Pack the `.dds` image into the `gui_common_pc.rpack` file using the game's packing tool.

### 2. Modifying the Game's UI Scripts (.scr)
To make the game aware of where we drew the new font image, we must modify the UI structure files in `data0.pak`:
- **`gui_default_font.scr` and `vanilla.scr`**: 
  - Command the game to create a new `Material` by pointing the coordinates to the new `.dds` file we just created (let's assume it's `common_fonts_7`).
  - **Do not** let it point to the original `common_fonts_0`, as that will cause font conflicts.
- **`font_replacements.scr`**:
  - This is the file that determines which Unicode character belongs to which coordinate (UV) on the 4096x4096 image.
  - We must specify the exact coordinates of normal English characters, normal Thai characters, and **PUA characters (starting from F000 upwards)** to perfectly match the image we drew.

---

## Part 2: Translation & PUA System

Once we have a perfectly complete vowel font (in PUA format), we must write a script to convert normal Thai text into PUA codes before injecting it into the game.

### 1. Game Text Decoding (Binsloc)
The game stores all text in the `texts/pc/pc_en_lang.binsloc` file, which is compressed inside `dataen.pak`.
- We use `binsloc_tool.py unpack` to decrypt it into a `.csv` file.
- Bring this `.csv` file into the **DyingLight2_Thai_Studio** program to bring up the UI window for convenient translation.

### 2. Character Conversion Process (PUA Conversion)
This is the heart of preventing floating vowels:
1. The `Build_DL2_Mod.py` script takes the `.csv` file translated into normal Thai.
2. The script reads the `mapping.json` file (PUA dictionary).
3. It will search for words with overlapping vowels (e.g., `ดำ`, `กั่`) and replace that character set with the **"PUA code"** we drew in Part 1 (e.g., changing `ดำ` to `\uf269`).
4. **⚠️ Crucial Trick (Sara Am):** The game's engine has a bug when drawing Sara Am (`ำ`), where it often just leaves the "top circle" (`ํ` Nikhahit). We must always write code to force adding Sara Aa after Sara Am (`text = text.replace('ำ', 'ำา')`) so that it perfectly displays the word "ทำ", instead of "ท ํ".

### 3. Packing Files Back into the Game (Deployment)
When the PUA text conversion is complete, the script will pack the `.csv` file back into `.binsloc`.
- **⚠️ Ultimate Precaution:** When injecting the `.binsloc` file into `dataen.pak` (which is a ZIP file), **do not use Append mode ('a')** on the old file!
- Appending will cause **2 duplicate files** named `pc_en_lang.binsloc` in a single ZIP!
- The C-Engine is a system that doesn't read ZIP files normally; it will always choose the "topmost" file. Thus, if there are duplicate files, it will pick up the old English version to display, and when the old English version (without PUA) meets our PUA font, it will display bizarre characters (like **"ด๋าเนิน"**).
- **The Solution:** You must completely clear and recreate the ZIP (`.pak`) file every time by copying all old files except the `.binsloc` file, and then injecting the new `.binsloc` at the end.

---

## Part 3: Real Workspace Structure (Workspace Structure)

To make the workflow systematic and standalone, we have combined everything as follows:
- **`01_Releases`**: The folder storing the completed `data0.pak` and `dataen.pak`, ready to be uploaded and distributed to players.
- **`128_Base`**: The sacred place for "creating and packing fonts" (only do this when you want to change the font style).
- **`DyingLight2_Thai_Studio`**: The translation program linked with `Deploy_Mod.py`. Translate -> Click Save -> Double-click Deploy -> Files run into the game ready for instant testing!

> *Completing the Dying Light 2 Thai Modding course perfectly* 🚀


---
**Created by:** [NodNuatTranslator](https://www.facebook.com/NodNuatTranslator/)
