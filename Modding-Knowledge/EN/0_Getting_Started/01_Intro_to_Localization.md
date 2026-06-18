# 📖 Chapter 1: Introduction to Game Localization

Welcome to the world of Game Localization! Changing the language in a game isn't just about translating files with Google Translate and overwriting them. It involves **Reverse Engineering** to find out exactly where the text is hidden.

## 1. Where is the text hidden in games?
Different games are built with different Engines, which means the methods of storing text vary:
- **The Easy Way:** Text is stored directly in the game folders with human-readable file extensions such as `.json`, `.xml`, `.csv`, `.ini`, `.yaml`. You can open these files with Notepad or VSCode and translate them right away!
- **The Hard Way:** Text is compressed together with 3D models and images, forming giant files such as `.pak`, `.arc`, `.upk`, `.ba2`. You will need specialized programs (Extractors) to "unpack" the files first.
- **The Hardcore Way:** Text is embedded deep within the game's code files like `.exe` or `.dll` directly. This requires advanced techniques (Memory Hook) to extract the text while the game is running.

## 2. Standard Workflow
Regardless of whether the game is easy or hard, the workflow is always similar:
1. **Unpack:** Use extraction tools to get the text files out from the game archives.
2. **Translate:** Translate those files (either manually or using our AI tools like TStudio/TRun).
3. **Font Creation:** Modify the in-game font images to include Thai consonants and vowels.
4. **Pack:** Compress the translated files and fonts back into the original format that the game recognizes.
5. **Playtest:** Launch the game to check for floating vowels or text overflowing the UI boundaries.


---
**Created by:** [NodNuatTranslator](https://www.facebook.com/NodNuatTranslator/)
