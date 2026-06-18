# 🚀 Chapter 4: Mastering THub Ecosystem

The **THub Launcher** was created to eliminate the hassle of game localization through our 4 "Flagship Products":

## 1. TStudio (Crafting Translation Tool)
- **Function:** Used to translate `.json` and `.csv` files line by line.
- **Key Features:** Has a Context checking system to keep translations on track, and can check character length to prevent text from overflowing UI boundaries.
- **Best For:** Translating UI menus or items that require high precision.

## 2. TRun (Industrial-Grade Auto-Translation Bot)
- **Function:** Used to feed giant dialogue files (hundreds of thousands of lines) to the AI for bulk translation.
- **Key Features:** Has a Checkpoint saving system, so if your PC crashes, it can resume translating.
- **Best For:** Long character Dialogue files in the game.

## 3. TPUA (Thai Vowel Secret Encoder)
- **Function:** Manages swapping normal Thai text codes into PUA (Private Use Area) codes to be fed into the game.
- **Key Features:** Comes with a Hallucination Checker button to detect broken stacked vowels and tone marks.

## 4. TGlyph (Font Image Generator)
- **Function:** Takes the generated PUA codes and draws characters into a Font Atlas image file (supports both normal images and SDF).
- **Key Features:** Automatically calculates (X,Y) coordinates and exports them ready to be injected right into the game's `.pak` archive.

> [!IMPORTANT]
> After you use an Extractor to extract text files from the game's `.pak` archive, pass the files through `TStudio` ➡️ run them through `TPUA` ➡️ generate images with `TGlyph` ➡️ and then pack them back into the game... That's it, your game localization project is complete!


---
**Created by:** [NodNuatTranslator](https://www.facebook.com/NodNuatTranslator/)
