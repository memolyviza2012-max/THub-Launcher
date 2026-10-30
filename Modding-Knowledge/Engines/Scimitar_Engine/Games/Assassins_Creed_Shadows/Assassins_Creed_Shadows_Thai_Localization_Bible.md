# Assassin's Creed Shadows — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Assassin's Creed Shadows uses the Scimitar/Anvil Engine by Ubisoft. The localization mod uses an Overlay/Patch approach, replacing `.forge` archives directly and injecting `.ttf` font files in a resources folder for rendering Thai texts.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Scimitar/Anvil Engine |
| **Developer** | Ubisoft |
| **Project Codename** | Unknown |
| **Archive Format** | `.forge` |
| **AES Encryption** | No |
| **Compression** | Unknown |
| **Font System** | TrueType Fonts (.ttf) placed in `resources/` |
| **Thai Font Used** | AvenirNextWorld (multiple weights, Regular=640KB, Italic=558KB) |
| **Text System** | Binary within `.forge` |
| **Text Encoding** | UTF-8 |
| **Mod Complexity** | ★★☆☆☆ (Patching forge files and replacing TTFs is standard) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```
Assassin's Creed shadows/
├── DataPC_boot_patch_03.forge (10.9 MB - Patch forge หลัก)
├── dlc_20/
│   └── DataPC_boot_20_dlc_patch_02.forge (688 KB - DLC patch)
└── resources/
    ├── AvenirNextWorld-Black.ttf (640 KB)
    ├── AvenirNextWorld-BlackIt.ttf (558 KB)
    ├── AvenirNextWorld-Bold.ttf (640 KB)
    ├── ... (รวม 20 ไฟล์ ฟอนต์ 2 ขนาด Regular/Italic)
```

---

## 4. Font Analysis
- **Font Family**: Avenir Next World (Modified for Thai)
- **Format**: `.ttf`
- **Storage**: The fonts are stored directly as `.ttf` files inside a `resources/` directory, rather than being packed inside the `.forge` archive. This implies the engine or a hook is loading fonts externally from the file system.
- **Weights**: The mod includes 20 different font files representing various weights and italics. Interestingly, non-italic weights are 640KB while italic weights are 558KB.
- **Thai Glyph Support**: Full support for Thai characters, likely with proper positioning for floating vowels and tone marks.

---

## 5. Text Analysis
- **Format**: Inside `.forge` archives.
- **Encoding**: UTF-8.
- **Content**: Magic bytes for the `.forge` are `73-63-69-6D-69-74-61-72` which is ASCII for `scimitar`. Scanning the `.forge` file reveals 147 Thai UTF-8 sequences. The texts are stored within the binary structure of the patch file.

---

## 6. Cross-Engine Comparison
Compared to Assassin's Creed Mirage, Shadows employs a similar `.forge` file patching method. However, Shadows loads `.ttf` fonts externally via a `resources/` folder, whereas Mirage may handle text differently or use pre-existing fonts. This external font loading is much more modder-friendly than games that bake SDF atlas textures (like Luminous Engine).

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
**Font Pipeline:**
1. Create or modify a TrueType Font (.ttf) with proper Thai glyphs.
2. Rename the font to match the game's expected fonts (e.g., `AvenirNextWorld-Regular.ttf`).
3. Place them in the `resources/` directory in the game root.

**Text Pipeline:**
1. Extract `.forge` using a tool like Blacksmith or Forger.
2. Locate the localization files.
3. Edit the UTF-8 text strings to Thai.
4. Repack into a patch `.forge` file (e.g., `DataPC_boot_patch_03.forge`).

---

## 8. Troubleshooting
- **Font not displaying**: Ensure the `.ttf` files are named exactly as the original `AvenirNextWorld` fonts and placed in the correct `resources/` path.
- **Thai vowels/tone marks misaligned (สระลอย)**: The `.ttf` might lack correct GPOS/GSUB tables. Edit the font using FontForge to adjust anchor points.
- **Game crash after mod installation**: Ensure `.forge` files are properly packed and not corrupted.

---

## 9. Required Tools
| Tool Name | Purpose | Download Source |
|---|---|---|
| Blacksmith / Forger | Unpacking and packing `.forge` files | GitHub (Various forks) |
| FontForge | Editing `.ttf` for Thai vowel alignment | fontforge.org |

---

## 10. Extracted Assets
- [AvenirNextWorld-Regular.ttf](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Scimitar_Engine/Games/Assassins_Creed_Shadows/Assets/Fonts/AvenirNextWorld-Regular.ttf)
- [AvenirNextWorld-Bold.ttf](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Scimitar_Engine/Games/Assassins_Creed_Shadows/Assets/Fonts/AvenirNextWorld-Bold.ttf)
- And 18 other weights extracted to the `Assets/Fonts/` folder.
