# 🛠️ Chapter 2: Tools of the Trade

As a modder, you need a personal "toolbox". Here are the programs that every game hacker must know and have installed:

## 1. Hex Editor
Some games read text based on a "Byte Count" value. If you edit the file directly, the game will crash. You must use **HxD** or **010 Editor** to view the raw data.
- **Trick:** Use HxD to look at the Header to see what Engine created this package file (for example, if you see the word `PK`, it means it's just a normal `.zip` file with a changed extension).

## 2. Extractors
When a game bundles files into a single archive (like `.pak`), you need engine-specific programs:
- **Unreal Engine:** Use **UnrealPak** or **FModel** to unpack and view the files.
- **Unity Engine:** Use **UABE (Unity Asset Bundle Extractor)** or **AssetStudio** to extract text and font assets.
- **Other/Custom Engines:** Use a magical scripting engine called **QuickBMS**. This program can run community-written scripts to unlock game files for almost any game in the world.

## 3. UI and Flash Font Tools
Older games (like Dishonored 1, Skyrim, Fallout) often render their menus using the Adobe Flash system (Scaleform GFx).
- You need to use **JPEXS Free Flash Decompiler** to open `.swf` or `.gfx` files to view the menu layout and inject TrueType (`.ttf`) fonts into them.

## 4. THub Command Center
And of course, the indispensable tool is **THub Launcher** (the program you have open right now!), which is the centralized hub for all your weapons, including AI translation tools and font conversion tools.


---
**Created by:** [NodNuatTranslator](https://www.facebook.com/NodNuatTranslator/)
