# 📚 Thai Localization Bible: Bleak Faith: Forsaken

**Game Title:** Bleak Faith: Forsaken  
**Engine:** Unreal Engine 4.27.2 (Shipping Win64)  
**Text System:** UE4 Serialized DataTables (`.uasset` + `.uexp`)  
**Archive System:** Unreal Pak V11 (`Forsaken-WindowsNoEditor.pak`)  
**Patch Mechanism:** Unreal Engine Patch Pak (`Forsaken-WindowsNoEditor_P.pak`)  

---

## 1. ⚙️ Engine & Archive Specifications

| Attribute | Specification |
| :--- | :--- |
| **Engine Version** | Unreal Engine 4.27.2.0 |
| **Main Executable** | `Forsaken/Binaries/Win64/Forsaken-Win64-Shipping.exe` |
| **Primary Archive** | `Forsaken/Content/Paks/Forsaken-WindowsNoEditor.pak` (~14.7 GB) |
| **Pak Version** | V11 (`Fnv64BugFix`) |
| **Mount Point** | `../../../` |
| **Encryption** | None (AES Key not required, encrypted index = false) |
| **Compression** | None |
| **Path Hash Seed** | `0xAF0F5471` (Decimal: `2937017457`) |
| **Pak Signature Check** | Enforced by UE4 Shipping. Requires ASI SigBypasser (`dsound.dll` + `UniversalSigBypasser.asi` in `Binaries/Win64/`) |
| **Recommended Pak Tool** | `repak.exe` (`E:/Mod_Workspace/Tool/repak_cli/repak.exe`) |

---

## 2. 📝 Localization Architecture (DataTables)

Bleak Faith: Forsaken **does not** use standard Unreal `.locres` files for in-game texts. Instead, all text strings are stored in **Unreal Engine 4 DataTables** (`.uasset` + `.uexp`) under:
`Forsaken/Content/Blueprints/Localization/`

### Supported Languages (`Languages.uasset`):
* `Languages::NewEnumerator0` : `Ex-Yu` (Croatian / Serbian)
* `Languages::NewEnumerator1` : `English` (Primary Target for Thai Mod)
* `Languages::NewEnumerator2` : `null`

### Localization DataTables Inventory (Total ~2,156 entries):
1. **`User_Interface/DT_Menu_Loc`** (489 rows): Main Menu, Settings HUD, Audio/Video Options, Keybinds, Pause Menu.
2. **`User_Interface/DT_UI_Loc`** (220 rows): HUD, Prompt indicators, interaction texts, belt slots.
3. **`Items/DT_Items_Loc`** (463 rows): Weapons, Armor, Consumables, Rings, Artifacts, Item Descriptions.
4. **`Dialogues/DT_Dialogue_Loc`** (112 rows): NPC Dialogues, quest conversations, subtitles.
5. **`Combat/DT_Abilities_Loc`** (450 rows): Combat skills, magic abilities, technique descriptions.
6. **`User_Interface/DT_Fragments_Loc`** (53 rows): Lore fragments, memory excerpts.
7. **`User_Interface/DT_Help_Loc`** (108 rows): Tutorial help guides, camera and control assistance.
8. **`User_Interface/DT_Tooltip_Loc`** (213 rows): Status effects, ailment descriptions, stat tooltips.
9. **`User_Interface/DT_LoadingScreen_Loc`** (48 rows): Loading screen gameplay tips and combo mechanics.

### Serialization & Encoding Details:
* Rows in DataTables 1–8 contain a Map property `Localization_10_4489A46C46C82C136E16449048A209CF` consisting of pairs `[ByteProperty, StrProperty]`.
* English is indexed by `Languages::NewEnumerator1`.
* When string is plain ASCII, UE4 serializes length as positive integer (1 byte/char).
* When string contains Thai (Unicode), UE4 serializes `FString` with negative length and encodes as **UTF-16LE** (2 bytes/char).
* `UAssetGUI.exe` handles this conversion to JSON (`tojson ... VER_UE4_27`) and back to `.uasset` (`fromjson`) with **100% bit-perfect roundtrip fidelity**.

---

## 3. 🔤 Font Architecture & Thai Rendering

### Font Assets Location:
`Forsaken/Content/Textures/Fonts/`

### Font Files:
* `Metropolis/Metropolis-*.ufont` (OTF outlines)
* `ABeeZee-Regular.ufont` (TTF)
* `Dominican_Small_Caps_Small_Caps.ufont` (TTF)
* `Electrolize-Regular.ufont` (TTF)
* `GlacialIndifference-Regular.ufont` (OTF)

*Note:* Files with `.ufont` extension in Bleak Faith are standard TTF/OTF files with headers `0x00010000` (TTF) or `OTTO` (OTF).

### Dual-Layer Thai Font Strategy:
1. **Layer 1 - Slate Font Fallback**:
   Unreal Engine 4 has an emergency Slate fallback mechanism. By placing a Unicode-complete Thai font at:
   `Engine/Content/Slate/Fonts/DroidSansFallback.ttf`
   any Slate/UMG widget whose primary font lacks Thai glyphs will automatically fall back to this font.
2. **Layer 2 - Internal Name Patching on `.ufont` Assets**:
   The game engine verifies font internal name tables (`nameID` 1, 2, 3, 4, 6). Simply dropping a raw TTF can cause FreeType/Slate to fail validation. We use `fontTools.ttLib.TTFont` to copy genuine name records from base game fonts (Metropolis, ABeeZee, Dominican, Electrolize, GlacialIndifference) directly into Kanit TTF files, saving them into `Forsaken/Content/Textures/Fonts/`.

### Dual Main Menu Widget Architecture:
Bleak Faith uses two distinct main menu widgets:
1. **`WBP_MainMenu.uasset`** (`Forsaken/Content/Blueprints/HUD/MainHUDs/`): Dynamically reads translations from `DT_Menu_Loc`.
2. **`WBP_MainMenu_CharacterBG.uasset`** (`Forsaken/Content/Assets/MenuSystem/Widgets/`): Uses static button text properties (`ButtonLabel`).
Both widgets and `DT_Menu_Loc` must be patched in tandem for complete Thai menu rendering.

---

## 4. 🛠️ Toolchain & Automation Scripts

All scripts reside in `05_Scripts_and_Tools/`:

### 1. `bleak_faith_unpacker.py`
Exports DataTables to Standard TStudio CSV:
```bash
python bleak_faith_unpacker.py --output-csv 02_Translation_Workspace/Bleak_Faith_Forsaken_ALL.csv
```
* CSV Columns: `key,source,translation,context,file_path`
* Preserves game code tags: `%s`, `{0}`, `<color=...>`, `\n`, `\r`

### 2. `bleak_faith_packer.py`
Reads translated CSV, updates uassets, injects Thai fonts, and builds `Forsaken-WindowsNoEditor_P.pak`:
```bash
python bleak_faith_packer.py --csv 02_Translation_Workspace/poc_main_menu_thai.csv --deploy
```
* Options:
  * `--csv <path>`: Input translated CSV.
  * `--deploy`: Automatically installs to game directory `Forsaken/Content/Paks/` and copies SigBypasser to `Forsaken/Binaries/Win64/`.
  * `--backup-dir`: Destination for checkpoint backups.
  * `--font-src`: Path to Thai TTF fonts (default: `03_Font_and_UI/Kanit`).

---

## 5. 🚀 Deployment & Installation

To install the Thai mod:
1. Copy ASI SigBypasser to:
   `<GameDirectory>/Forsaken/Binaries/Win64/`
   - `dsound.dll` (Ultimate ASI Loader)
   - `UniversalSigBypasser.asi` (Bypasses UE4 pak signature verification)
2. Copy `Forsaken-WindowsNoEditor_P.pak` into:
   `<GameDirectory>/Forsaken/Content/Paks/`
3. Launch the game normally via Steam.
4. The game will automatically load `Forsaken-WindowsNoEditor_P.pak` as an official patch override!
