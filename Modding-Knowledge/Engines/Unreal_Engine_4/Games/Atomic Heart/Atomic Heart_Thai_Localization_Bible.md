# Atomic Heart — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Atomic Heart runs on Unreal Engine 4 and implements Thai localization via standard file replacement mod architecture. It replaces standard `.locres` files and swaps font assets using raw TTFs renamed to `.ufont`.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Unreal Engine 4 |
| **Developer** | Mundfish |
| **Project Codename** | AtomicHeart |
| **Archive Format** | .pak (Standard UE4) |
| **AES Encryption** | No |
| **Compression** | Zlib / None |
| **Font System** | Font Swap (Raw TTF renamed to .ufont) |
| **Thai Font Used** | Noto Sans Thai Looped Regular |
| **Text System** | LocRes (Unreal Engine String Tables) |
| **Text Encoding** | UTF-16 LE |
| **Mod Complexity** | ★★☆☆☆ (Standard Locres modding with raw TTF injection) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```text
pakchunk16-WindowsNoEditor_P.pak (2.9 MB)
├── AtomicHeart/Content/Development/UI/Fonts/MultiLanguage/
│   └── AnekBangla-Bold.ufont (Noto Sans Thai Looped injected here)
├── AtomicHeart/Content/Localization/
│   ├── Academy_Dialogues/
│   ├── CUTSCENES/
│   ├── Misc/
│   └── (Multiple dialogue and UI .locres files)
```

---

## 4. Font Analysis
- **Font Identification**: The mod uses `Noto Sans Thai Looped Regular` injected directly into a `.ufont` file.
- **How fonts are stored**: In this specific mod, the `.ufont` file contains raw TTF data. The magic header `00 01 00 00` starts at offset 0, meaning the file is simply a `.ttf` file renamed to `.ufont`. This is a common hack in UE4 when custom font composite configuration isn't strictly required by the game UI.
- **Font swap mapping**: The font `AnekBangla-Bold` was likely replaced to serve as a multi-language fallback that includes Thai glyphs.
- **Thai rendering considerations**: Since Noto Sans Thai Looped provides standard spacing, any สระลอย or clipping issues would require either pre-shaping the text in Locres, or relying on UE4's text renderer if it supports complex text layout for this game.

---

## 5. Text Analysis
- **File format and encoding**: Text is stored in standard Unreal Engine `.locres` binary files. UE4 uses UTF-16 LE encoding for strings containing non-ASCII characters like Thai.
- **Text Structure**: Standard namespace/key/value string tuples used by UE4 Localization.
- **String Count**: Highly segmented into multiple files (Academy_Dialogues, CUTSCENES, Misc, etc.).
- **Quest/dialogue organization**: Categorized neatly by location and DLCs.

---

## 6. Cross-Engine Comparison
Atomic Heart's approach is extremely standard for Unreal Engine 4 mods. Like *ACE COMBAT 7*, it does not employ AES encryption on its mod PAKs. However, unlike *ACE COMBAT 7* which uses custom `.dat` files for strings, *Atomic Heart* uses the native Unreal Engine localization format (`.locres`), making it fully compatible with tools like FModel or UnrealLocres. Replacing raw `.ttf` disguised as `.ufont` is also a known shortcut in UE4 modding.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
**Font Pipeline:**
1. Choose an appropriate Thai TTF font (e.g., Noto Sans Thai Looped).
2. Rename the `.ttf` extension to `.ufont` for the target fallback font (e.g., `AnekBangla-Bold.ufont`).
3. Place in the correct directory path mirroring the game's extracted content.

**Text Pipeline:**
1. Use `UnrealLocres` or `FModel` to convert original game `.locres` files into `.csv` or `.json`.
2. Translate the text into Thai.
3. Repack back to `.locres` format using `UnrealLocres`.
4. Pack all modified fonts and `.locres` files into a `_P.pak` file using `repak_cli`.

---

## 8. Troubleshooting
- **Font not displaying**: If the renamed `.ttf` hack fails on certain updates, you may need to use UE4 Editor to create a proper Font Face asset and cook it into a valid `.ufont` container.
- **Missing translations**: Ensure all keys match the original `.locres` file, as missing keys can cause default English text to appear.

---

## 9. Required Tools
| Tool | Purpose | Download Source |
|---|---|---|
| **repak_cli** | Unpack and repack UE4 .pak files | [GitHub - repak](https://github.com/trumank/repak) |
| **UnrealLocres** | Convert .locres to editable text and back | GitHub |
| **FModel** | Extracting original .locres files from base game | FModel.app |

---

## 10. Extracted Assets
- [NotoSansThaiLooped-Regular.ttf](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/UnrealEngine4/Games/Atomic%20Heart/Assets/Fonts/NotoSansThaiLooped-Regular.ttf)

---

## 11. M2M Protocol
**Automated Font Rendering Script (Python):**
```python
# N/A for standard UE4 - TTF is supported natively
pass
```
**Automated Text Shaping Script (Regex):**
```python
import re
def shape_thai(text):
    return text # Placeholder for shaping logic if needed
```
**Automated FNT/Mapping Injector (Struct):**
```python
# N/A
pass
```
