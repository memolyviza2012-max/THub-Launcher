# Knowledge Base: Creating Thai Localization Mod for Mass Effect: Andromeda (Frostbite Engine)

This document summarizes all the Reverse Engineering techniques and processes used to hack the game system and fix the "black screen" or "game freeze" bugs, enabling games on the Frostbite Engine to display Thai language and perform word-wrapping perfectly 100%.

---

## 1. Frostbite Engine's Problem with Thai Language

The game was not programmed to support characters in the Thai Unicode range (`U+0E00` - `U+0E7F`). When we try to insert Thai directly, the following issues occur:
1. **Memory Overflow:** The engine lacks Kerning/Metrics data for Thai characters in the system, causing memory read errors and game crashes.
2. **Word-Wrap Bug:** The Thai language has no spaces between words. The game's line-breaking system will search for a space to start a new line. When it cannot find one, it enters an infinite loop or cuts words in the middle of a vowel (e.g., cutting between a consonant and the vowel 'ำ'), causing floating vowels and game crashes when a sentence is too long.

---

## 2. The Solutions

To overcome the Engine's limitations, we utilized the following 4 main techniques:

### 💡 Technique 1: Glyph Swapping into the Chinese (CJK) Base
Instead of using Thai directly, we **trick the game** into displaying another language it already supports.
- **Why Chinese?**: Initially, we tested Russian, but found that Russian requires spaces for word-wrapping, otherwise the game crashes. Japanese has "Kinsoku Shori" rules (no spaces before punctuation marks), which caused word-wrapping bugs. We ultimately settled on **Chinese (CJK Unified Ideographs - `U+4E00`)**, which allows the game to break lines anywhere without bugs.
- **How to do it**: Use the Python `fonttools` library (`font_swapper.py`) to modify the `.ttf` font file by copying the Glyphs of all Thai characters and overwriting them into the Chinese Unicode slots.

### 💡 Technique 2: Smart Word-Wrap with ZWSP
To solve the issue where the game often cuts words incorrectly (such as separating consonants from vowels).
- We use a **Thai AI word-wrapper (PyThaiNLP)** to read all 104,000 Thai sentences.
- Insert a **Zero-Width Space (`U+200B`)** between words, for example: `กำหนด[ZWSP]ไว้`.
- **Preventing Game Code Breakage**: We wrote Regular Expressions (Regex) so the AI only splits "pure Thai text blocks". This prevents it from splitting the game's HTML codes (like `<font color='#FF0000'>`), which is the main reason games crash immediately upon entering the menu.

### 💡 Technique 3: Font Y-Shifting
English fonts were not designed to have overlapping characters top and bottom like Thai. This causes upper vowels (like ิ  ี) and tone marks (like ่  ้) to sink and overlap with consonants.
- We use Python (`shift_vowels.py`) to directly modify the `Y-axis` coordinates of all target vowels and tone marks in the `glyf` table of the `.ttf` file.
- Lift upper vowels and tone marks up by **50 Units (UPM)**, which is an aesthetically pleasing distance and not overly floating.

### 💡 Technique 4: Binary Level Encoding (Bypass Frosty Plugin)
The Frosty Editor tool includes a `BiowareLocalizationPlugin` which has limitations in supporting large localization Mods.
- We Reverse Engineered the game's `.res` file structure (which is encoded with Huffman Trees and 32-bit Pointers in LSB-first format).
- Wrote a Python script (`process_all_res.py`) to build `.res` files 100% from scratch. This allows us to inject Thai text encoded as Chinese + invisible spaces into all 61 `.res` files to replace English within seconds.

---

## 3. Tools Created

Keep these scripts for future use (located in `Tools\Localization_Scripts\`):
1. **`process_all_res.py`**: The main script to process text from CSV -> word-wrap with AI -> convert to Chinese characters -> encode into `.res` files.
2. **`font_swapper.py`**: Script to overlay Thai fonts onto Chinese slots in a `.ttf` file.
3. **`shift_vowels.py`**: Script to raise vowels and tone marks higher.
4. **`mea_loc_decoder.py`** / **`mea_loc_encoder.py`**: Tools for decoding/encoding individual .res files to inspect internal data.

> [!TIP]
> **Future Applications**
> This knowledge can be applied to translate almost any other EA games that use the **Frostbite Engine** (such as Dragon Age, Dead Space Remake, Battlefield) because the structures of their Font Resources and Localization Resources use the exact same methods!


---
**Created by:** [NodNuatTranslator](https://www.facebook.com/NodNuatTranslator/)
