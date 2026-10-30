# Assassin's Creed Mirage — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Assassin's Creed Mirage runs on the Scimitar/Anvil Engine by Ubisoft. This mod uses a patch-based approach modifying `.forge` files. Interestingly, it does not include any font files but includes several `.webm` videos, suggesting native Thai font support or that fonts are embedded in the patched `.forge`.

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
| **Font System** | Native or Embedded in `.forge` |
| **Thai Font Used** | Unknown |
| **Text System** | Binary within `.forge` |
| **Text Encoding** | UTF-8 |
| **Mod Complexity** | ★★☆☆☆ (Standard patch creation) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```
Assassin's Creed Mirage/
├── DataPC_patch_02.forge (2.7 MB)
├── DataPC_SharedGroup_00_patch_02.forge (2.0 MB)
└── videos/
    ├── AC15th_Logo.webm (37.7 MB)
    ├── UbisoftLogo.webm (4.1 MB)
    ├── en/
    │   ├── PC_WarningSaving.webm (100 KB)
    │   └── warning_disclaimer.webm (701 KB)
```

---

## 4. Font Analysis
No external font files (`.ttf`, `.otf`) were found in the mod structure. This implies one of two things:
1. Assassin's Creed Mirage natively supports Thai glyph rendering out of the box.
2. The custom Thai font is packed directly inside the `DataPC_patch_02.forge` or `DataPC_SharedGroup_00_patch_02.forge` files.

---

## 5. Text Analysis
- **Format**: Text is embedded inside the `.forge` binary patches.
- **Encoding**: UTF-8.
- **Content**: The `.forge` magic bytes are `73-63-69-6D-69-74-61-72` (scimitar). A scan of `DataPC_patch_02.forge` revealed 19 Thai UTF-8 sequences. The low number indicates this patch might contain localized UI elements or small text updates, while `DataPC_SharedGroup_00_patch_02.forge` likely contains more strings.

---

## 6. Cross-Engine Comparison
Compared to Assassin's Creed Shadows, Mirage's mod does not use an external `resources/` folder for fonts. Instead, everything is self-contained within the `.forge` patches and `.webm` video replacements. This makes installation cleaner but modifying fonts harder since they must be repacked into the archive if not native.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
**Text Pipeline:**
1. Unpack original `.forge` files using Forger or Blacksmith.
2. Locate localization strings.
3. Edit the UTF-8 text and save.
4. Repack the changes into `DataPC_patch_02.forge`.

**Video Pipeline:**
1. Encode localized pre-rendered videos to `.webm` format.
2. Place them in the `videos/` folder maintaining the original path structure (e.g., `videos/en/`).

---

## 8. Troubleshooting
- **Text shows as squares (Tofu)**: If Thai characters don't render, a font injection might be missing, or the game requires an updated `.forge` with a Thai-supported font.
- **Videos not playing**: Ensure the `.webm` files are encoded correctly (VP9/VP8) as expected by the engine's video player.

---

## 9. Required Tools
| Tool Name | Purpose | Download Source |
|---|---|---|
| Blacksmith / Forger | Unpacking and packing `.forge` files | GitHub (Various forks) |
| FFmpeg | Re-encoding localized videos to `.webm` | ffmpeg.org |

---

## 10. Extracted Assets
No fonts were extracted for this game as none were present in the mod files. See `EXTRACTION_NOTE.txt` for details.
