# SOS: AWL Font Integration Guide

This guide explains how to inject Thai fonts into *Story of Seasons: A Wonderful Life* using **TGlyph** and the custom font packing script.

## Prerequisites
Ensure the following files are available:
- **Font Master**: `E:\Mod_Workspace\Tool\1_ThaiFont\1_Font_Master\Noto_Sans_Thai\NotoSansThai-VariableFont_wdth,wght_PUA.ttf`
- **Characters List**: `E:\Mod_Workspace\Tool\1_ThaiFont\Char.txt`
- **Mapping Data**: `E:\Mod_Workspace\Tool\1_ThaiFont\Mapping.json`
- **Font Texture**: The converted PNG font texture (e.g., `FOT-PopJoyStd-B_0.png` located in `E:\Mod_Workspace\TempMessage\Fonts\`).

## Step 1: Generate Thai Glyphs with TGlyph
1. Open the Modder Hub's **TGlyph** application:
   ```cmd
   python E:\Mod_Workspace\Modder_project\modder-hub\tools\flagship\TGlyph\tglyph_app.py
   ```
2. In the **Startup Dialog**:
   - **Font File**: Select `NotoSansThai-VariableFont_wdth,wght_PUA.ttf`.
   - **Base Image**: Select the original PNG font texture (`FOT-PopJoyStd-B_0.png`).
3. Inside the TGlyph Workspace:
   - Use `Char.txt` to verify that all necessary Thai characters are present in the character list.
   - Load `Mapping.json` (if TGlyph supports direct mapping import) to align the characters to the correct coordinate offsets on the texture map.
   - Adjust font sizes and positions to ensure the glyphs fit perfectly inside the designated cells.
4. Export the modified image. Save the final image, overwriting the original PNG in `E:\Mod_Workspace\TempMessage\Fonts\FOT-PopJoyStd-B_0.png`.

## Step 2: Pack and Inject the Font
After generating the modified texture PNG, you must convert it back to the game's proprietary BC7 DDS format and inject it into the `disc` archive.

1. Open your terminal or command prompt.
2. Run the `pack_fonts.py` script:
   ```cmd
   python E:\Mod_Workspace\Tool\pack_fonts.py
   ```
3. The script will automatically:
   - Convert your modified PNG into a BC7 compressed DDS file.
   - Repack the DDS file into the `font_all_tex.bin` archive.
   - Compress the `.bin` archive into an LZ4 `.lzs` file (`font_all_tex.lzs`).
   - Copy the newly created `.lzs` file directly into your game's directory (`E:\Mod_Workspace\STORY_OF_SEASONS_A_Wonderful_Life\disc\resource\font\`).

## Step 3: Verify in Game
1. Launch *Story of Seasons: A Wonderful Life*.
2. Ensure that the text displays correctly in the main menu and during dialogue.
3. If any text overlaps or appears misaligned, return to TGlyph, adjust the mapping coordinates/scale, and repack using Step 2.
