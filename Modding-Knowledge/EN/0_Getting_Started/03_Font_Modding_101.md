# 🔠 Chapter 3: Font Modding 101

The problem that causes 90% of game translation projects to be abandoned isn't the translation itself, but the inability to "get Thai fonts into the game", resulting in issues like "tofu characters (squares)" and "floating vowels".

## 1. What is a Font Atlas?
Most game engines do not pull `.ttf` fonts directly from Windows. Instead, they render every character onto a "large image" (Texture Atlas), and the game calculates coordinates (X, Y) to crop and paste the letters onto the screen one by one.
- **SDF (Signed Distance Field):** This is a modern image font technique that blurs the edges of characters. When the game scales them up, they remain sharp without pixelating.

## 2. Why do vowels float/sink?
Western games are designed to print text sequentially from left to right (A B C). However, the Thai language features "vertical stacking" (for example, the word "ที่" has a consonant, an upper vowel, and a tone mark stacked in 3 layers).
When a Western game tries to print Thai, it places the vowel to the right of the consonant (ก ิ) instead of stacking it on top, causing vowels to float and scatter.

## 3. PUA (Private Use Area) Technique
To solve the floating vowel problem, the Thai modding community invented the **PUA** technique.
In the computer character encoding system (Unicode), there is an empty zone called PUA (starting from code `E000` onwards), which is an unassigned area not used by any language.
- **How it works:** We write scripts to merge "consonant + vowel + tone mark" into a single block (a single character), and then hide that combined image in the PUA space.
- **The result:** When the game encounters the word "ที่", it won't print `ท` + `สระอี` + `ไม้เอก`. Instead, our script will swap it out to fetch the image at code `E001` (the pre-assembled image) to display. This ensures vowels do not float, looking 100% perfect.

> [!TIP]
> The **TPUA** and **TGlyph** tools in THub automatically handle the PUA system and draw the Font Atlas images for you!


---
**Created by:** [NodNuatTranslator](https://www.facebook.com/NodNuatTranslator/)
