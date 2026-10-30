# Pathologic 2 — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
**Pathologic 2** is a dramatic narrative-driven survival-thriller RPG developed by **Ice-Pick Lodge** and published by **tinyBuild**, released in May 2019 on the **Unity Engine** (Unity 2018.2.14f1 64-bit Mono). The game takes place in a secluded steppe town stricken by a fatal plague where time is strictly limited and choices carry irreversible consequences.

The modding architecture pattern is classified as **Hybrid (Binary Resource Patching + Direct Engine Font Injection)**:
1. **Font System:** Binary font replacement inside `sharedassets0.assets` via AssetsTools.NET, substituting the 5 core game fonts with a customized Thai TrueType font (`Prompt-Bold`) specially modified with a **+150 Design Unit Tone Mark Elevation** and GPOS stripping to natively bypass Unity's legacy Canvas Text mark clashing limitations.
2. **Text System:** Dual-tier text storage consisting of binary-serialized Unity string tables within `resources.assets` (covering UI, HUD, menus, and voice subtitles) and plain text key-value databases in `Data/VirtualMachine/*/Localizations/english.txt` (covering narrative dialogues, quest trees, and character interactions).

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Title** | Pathologic 2 |
| **Developer** | Ice-Pick Lodge |
| **Publisher** | tinyBuild |
| **Game Engine** | Unity 2018.2.14f1 (64-bit Mono) |
| **Project Codename** | PathologicSandbox |
| **Archive Formats** | Unity Assets Archives (`.assets`: `sharedassets0.assets`, `resources.assets`) + Plain Text (`.txt`) |
| **AES Encryption** | None (Unencrypted Unity serialized files) |
| **Compression** | LZ4 / None (Assets file blocks uncompressed) |
| **Font Rendering Engine** | `UnityEngine.UI.Text` (Legacy Canvas Text) backed by FreeType / OS Font Parser |
| **Original Fonts** | `libertinussans-regular` (PathID 2327), `libertinussans-bold` (PathID 2333), `Vollkorn-Bold` (PathID 2334), `NotoSans-Condensed` (PathID 2335), `NotoSans-CondensedBold` (PathID 2336) |
| **Thai Font Injected** | Prompt-Bold (+150 Glyph Y-Shift, GPOS table removed, 270,780 bytes) |
| **Text System Architecture** | Dual Tier: Binary String Tables in `resources.assets` + Flat TSV in `VirtualMachine` |
| **Text Encoding** | UTF-8 / UTF-8 BOM |
| **Total Strings / Words** | 26,199 strings / 263,787 English words across 4 major partitions |
| **Mod Complexity** | ★★★☆☆ (Moderate: Required TrueType binary glyph engineering to overcome Unity Canvas mark-to-mark overlap bug, paired with multi-file assets unpacking/repacking) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```
Pathologic 2/
├── Pathologic 2.exe                                    [639 KB] Main executable
├── UnityPlayer.dll                                     [22.4 MB] Unity 2018 engine runtime
├── MonoBleedingEdge/                                   Mono C# scripting subsystem
└── Pathologic_Data/
    ├── app.info
    ├── boot.config
    ├── globalgamemanagers                              [108 KB] Engine settings
    ├── level0                                          [1.4 MB] Initial scene
    ├── sharedassets0.assets                            [156 MB] Core UI & Font Data
    │   ├── libertinussans-regular  (Font, PathID: 2327, Size: 1.35 MB)
    │   ├── libertinussans-bold     (Font, PathID: 2333, Size: 1.34 MB)
    │   ├── Vollkorn-Bold           (Font, PathID: 2334, Size: 172 KB)
    │   ├── NotoSans-Condensed      (Font, PathID: 2335, Size: 279 KB)
    │   └── NotoSans-CondensedBold  (Font, PathID: 2336, Size: 290 KB)
    ├── resources.assets                                [1.35 GB] Master Localized Resources
    │   ├── English                 (TextAsset, PathID: 17621, Size: 37.9 KB) -> UI strings
    │   ├── English_Quest           (TextAsset, PathID: 17622, Size: 2.1 KB) -> Quest headers
    │   ├── SubTitles_English       (TextAsset, PathID: 17626, Size: 184 KB) -> Voice subtitles
    │   ├── English_Days            (TextAsset, PathID: 17627, Size: 1.5 KB) -> Day markers
    │   └── ... (67 additional English localization chunks)
    └── Data/
        └── VirtualMachine/                             [Narrative scripts & quest database]
            ├── PathologicSandbox/
            │   └── Localizations/
            │       ├── english.txt                     [4.8 MB, 22,093 narrative dialogue lines]
            │       └── russian.txt                     [5.2 MB, 22,093 narrative dialogue lines]
            └── ... (Other story modules)
```

---

## 4. Font Analysis

### 4.1 Root Cause of Unity Canvas Thai Rendering Failure
During initial reverse-engineering tests, injecting standard Thai fonts (such as Sarabun, Prompt, or Noto Sans Thai) resulted in a critical rendering bug:
- In `UnityEngine.UI.Text` (Canvas Text), vowels and tone marks at level 1 rendered normally.
- However, when a tone mark (ไม้เอก `Uni0E48`, ไม้โท `Uni0E49`, ไม้ตรี `Uni0E4A`, ไม้จัตวา `Uni0E4B`, ไม้ทัณฑฆาต `Uni0E4C`) occurred above an upper vowel (สระอิ `Uni0E34`, สระอี `Uni0E35`, สระอึ `Uni0E36`, สระอือ `Uni0E37`, ไม้หันอากาศ `Uni0E31`):
  1. Standard font design placed both upper vowels and base tone marks at identical vertical baselines (`yMin ≈ 595`).
  2. `UnityEngine.UI.Text` lacks HarfBuzz or modern OpenType GPOS (`mark-to-mark`) positioning on PC builds without TextMeshPro.
  3. Consequently, the tone marks clashed with the upper vowels, and Unity's rasterizer either dropped the tone mark or created black clipping artifacts.

### 4.2 The Binary Font Elevation Solution (+150 Design Units)
To permanently resolve this without needing runtime code hooks or PUA shaper scripts, we engineered a custom TrueType binary transformation using Python's `fontTools`:
1. **Target Glyphs Identified (21 Thai Tone & Diacritic Glyphs):**
   - Standard tones: `uni0E48` (Mai Ek), `uni0E49` (Mai Tho), `uni0E4A` (Mai Tri), `uni0E4B` (Mai Chattawa), `uni0E4C` (Thanthakhat), `uni0E4D` (Nikhahit), `uni0E4E` (Yamakkan).
   - Narrow / Left-shifted variants: `uni0E48.narrow`, `uni0E49.narrow`, `uni0E4A.narrow`, `uni0E4B.narrow`, `uni0E4C.narrow`, `uni0E4D.narrow`, `uni0E4E.narrow`.
   - PUA shifted variants: `uniF70A` through `uniF714`.
2. **Vertical Transformation:**
   All 21 glyph outlines were elevated upwards along the Y-axis by **+150 Font Design Units**:
   $$\Delta Y = +150 \implies yMin: 595 \to 745, \quad yMax: 885 \to 1035$$
3. **GPOS Stripping:**
   The `GPOS` table was stripped from the TrueType font. This prevented any partial OpenType engines from attempting to recalculate mark offsets, locking the elevated positions into the raw glyph geometry.
4. **Result:**
   Words with complex vowel-tone stacking such as **"เริ่ม"**, **"ตั้ง"**, **"น้ำ"**, **"ผู้จัดทำ"** render with pristine typographic hierarchy natively in standard UTF-8 Unicode, requiring zero runtime text shaping!

### 4.3 Injected Font Mapping Table
The modified font `Prompt-Bold_PUA_Shifted.ttf` (270,780 bytes) is injected directly into `m_FontData` of all 10 UI and dialogue fonts in `sharedassets0.assets`, as well as 3 fallback fonts in `resources.assets`:

#### `sharedassets0.assets` Fonts (UI & In-Game Dialogues):
| Asset Name | PathID | Type | Injected Font | Role / Location | Status |
|---|---|---|---|---|---|
| `libertinussans-regular` | 2327 | Font (0x80) | Prompt-Bold (+150 Shifted) | Main UI & Menu Buttons | Replaced |
| `Gentium Plus Regular` | 2328 | Font (0x80) | Prompt-Bold (+150 Shifted) | Secondary In-game Serif | Replaced |
| `LiberationSerif-Italic` | 2329 | Font (0x80) | Prompt-Bold (+150 Shifted) | In-game Italic Dialogue | Replaced |
| `NotoSans-CondensedItalic` | 2330 | Font (0x80) | Prompt-Bold (+150 Shifted) | Secondary UI Italic | Replaced |
| `LiberationSerif-Regular` | 2331 | Font (0x80) | Prompt-Bold (+150 Shifted) | **Primary In-Game Dialogue (Mark Immortell, NPCs)** | Replaced |
| `LiberationSerif-Bold` | 2332 | Font (0x80) | Prompt-Bold (+150 Shifted) | **Speaker Names & Emphasis** | Replaced |
| `libertinussans-bold` | 2333 | Font (0x80) | Prompt-Bold (+150 Shifted) | Main UI Bold Headers | Replaced |
| `Vollkorn-Bold` | 2334 | Font (0x80) | Prompt-Bold (+150 Shifted) | Chapter & Journal Headers | Replaced |
| `NotoSans-Condensed` | 2335 | Font (0x80) | Prompt-Bold (+150 Shifted) | Inventory & Status Indicators | Replaced |
| `NotoSans-CondensedBold` | 2336 | Font (0x80) | Prompt-Bold (+150 Shifted) | Inventory & Item Titles | Replaced |

#### `resources.assets` Fonts:
| Asset Name | PathID | Type | Injected Font | Role / Location | Status |
|---|---|---|---|---|---|
| `verdana` | 28904 | Font (0x80) | Prompt-Bold (+150 Shifted) | System Fallback | Replaced |
| `verdana_11` | 28905 | Font (0x80) | Prompt-Bold (+150 Shifted) | Small System Fallback | Replaced |
| `LiberationSans` | 28906 | Font (0x80) | Prompt-Bold (+150 Shifted) | UI Fallback | Replaced |

### 4.4 TextMeshPro Dynamic Injection (`Pathologic2FontPlugin`)
For components using TextMeshProUGUI (such as `[Text] Tooltip View` for loading hints `{LoadingHint.*}` and tutorial action tooltips `{Tooltip.*}`):
1. **Dynamic Font Creation:** The BepInEx plugin dynamically creates `DynamicFontAsset = TMP_FontAsset.CreateFontAsset(sourceFont, 48, 4, GlyphRenderMode.SDFAA, 2048, 2048, AtlasPopulationMode.Dynamic)`.
2. **Pre-population (`Char.txt`):** Immediately invokes `DynamicFontAsset.TryAddCharacters(allChars)` with `Char.txt` containing all Thai (0x0E00–0x0E7F) and PUA codes, eliminating missing-glyph fallback to Russian Cyrillic `NotoSans-Condensed SDF`.
3. **Direct Font Binding:** Harmony postfix patches on `TextMeshProUGUI.Awake`, `TextMeshProUGUI.OnEnable`, and `TextStringView.ApplyStringValue` assign `__instance.font = DynamicFontAsset` and `__instance.fontSharedMaterial = DynamicFontAsset.material`, guaranteeing 100% Thai rendering with zero Cyrillic mojibake.

---

## 5. Text Analysis

### 5.1 Storage Architecture & Categorization
Text in Pathologic 2 is partitioned into four distinct logical domains:

| Category | File Location | Format | Rows | Word Count | Description |
|---|---|---|---|---|---|
| **UI & Menus** | `resources.assets` (`English`, `English_Quest`) | Binary Unity StringTable | 695 | 3,085 words | Main menu, pause menu, options, inventory UI, item names, descriptions, tooltips |
| **Subtitles** | `resources.assets` (`SubTitles_English`) | Binary Unity StringTable | 3,411 | 30,213 words | In-game spoken voiceover lines, town announcer calls, ambient voices |
| **Narrative / Quests** | `Pathologic_Data/Data/VirtualMachine/*/Localizations/english.txt` | Tab-delimited key-value (`ID \t Text`) | 22,093 | 230,489 words | Deep branching dialogues, NPC inquiries, thoughts, theater interludes |
| **Total Master** | Unified Workspace CSV | TStudio standard CSV | **26,199** | **263,787 words** | Complete game text corpus |

### 5.2 Formatting Tags & Preservation Rules
The following system tags and format tokens must be preserved verbatim during translation:
1. **Rich Text Formatting:** `<b>...</b>`, `<i>...</i>`, `<color=#HEX>...</color>`, `<size=N>...</size>`.
2. **Variable Braces:** `{0}`, `{1}`, `{Building.Name}`, `{SubTitles.English...}`.
3. **Custom Game State Tokens:** `<deaths>`, `</deaths>`, `<saves>`, `</saves>`, `<gamename>`, `<line>`.
4. **Escape Sequences:** `\n` (soft line breaks in dialogue and tooltips), `\t` (column separators).

---

## 6. Cross-Engine Comparison

| Dimension | Pathologic 2 (Unity 2018) | Disco Elysium (Unity 2019) | Hardspace Shipbreaker (Unity 2020) | Wasteland 3 (Unity 2019) |
|---|---|---|---|---|
| **UI Framework** | `UnityEngine.UI.Text` (Canvas Text) | TextMesh Pro (TMP) | TextMesh Pro (TMP) | TextMesh Pro (Addressables) |
| **Font Mechanism** | Embedded TrueType `m_FontData` | Dynamic TMP Fallback Asset | BepInEx Font Replacement | Injected TMP Font AssetBundle |
| **Thai Tone Handling** | **+150 Glyph Y-Shift Elevation** | PUA Shaper / Custom TMP Shader | PUA Shaper Plugin | Fallback Font List Injection |
| **Text Storage** | `resources.assets` + Flat `.txt` | SQLite DB / Language Bundles | Localization CSV / Bundles | Addressables StringTables |
| **Mod Complexity** | ★★★☆☆ (Moderate) | ★★★★☆ (High) | ★★★☆☆ (Moderate) | ★★★★☆ (High) |

---

## 7. Pipeline — ขั้นตอนการสร้างม็อด

### 7.1 Font Pipeline: Tone Elevation & GPOS Removal
Create `03_Font_and_UI/shift_tone_marks.py`:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Thai Font Tone Elevation Script (+150 Design Units)
Elevates tone marks and diacritics to solve Unity UI.Text vowel-tone overlap.
"""
from fontTools.ttLib import TTFont
import sys

TONE_GLYPHS = [
    'uni0E48', 'uni0E49', 'uni0E4A', 'uni0E4B', 'uni0E4C', 'uni0E4D', 'uni0E4E',
    'uni0E48.narrow', 'uni0E49.narrow', 'uni0E4A.narrow', 'uni0E4B.narrow',
    'uni0E4C.narrow', 'uni0E4D.narrow', 'uni0E4E.narrow',
    'uniF70A', 'uniF70B', 'uniF70C', 'uniF70D', 'uniF70E', 'uniF70F', 'uniF710',
    'uniF711', 'uniF712', 'uniF713', 'uniF714'
]

def shift_font(input_path, output_path, shift_y=150):
    print(f"Loading font: {input_path}")
    font = TTFont(input_path)
    glyf = font['glyf']
    
    shifted_count = 0
    for name in TONE_GLYPHS:
        if name in glyf:
            glyph = glyf[name]
            if hasattr(glyph, 'coordinates') and glyph.coordinates:
                shifted_coords = []
                for x, y in glyph.coordinates:
                    shifted_coords.append((x, y + shift_y))
                glyph.coordinates = glyph.coordinates.__class__(shifted_coords)
                if hasattr(glyph, 'yMin'):
                    glyph.yMin += shift_y
                if hasattr(glyph, 'yMax'):
                    glyph.yMax += shift_y
                shifted_count += 1
                print(f"  [+] Shifted glyph: {name} by +{shift_y} units")

    # Strip GPOS to prevent layout engines from resetting positions
    if 'GPOS' in font:
        del font['GPOS']
        print("  [+] Removed GPOS table.")

    font.save(output_path)
    print(f"[SUCCESS] Saved shifted font ({shifted_count} glyphs modified) -> {output_path}")

if __name__ == '__main__':
    src = r"E:\Mod_Workspace\Pathologic_2\03_Font_and_UI\Prompt\Prompt-Bold_PUA.ttf"
    dst = r"E:\Mod_Workspace\Pathologic_2\03_Font_and_UI\Prompt\Prompt-Bold_PUA_Shifted.ttf"
    shift_font(src, dst, 150)
```

### 7.2 Font Injection Engine (C# / AssetsTools.NET)
In `05_Scripts_and_Tools/AssetHelper/Program.cs`:

```csharp
using System;
using System.IO;
using AssetsTools.NET;
using AssetsTools.NET.Extra;

namespace AssetHelper
{
    class Program
    {
        static void Main(string[] args)
        {
            if (args.Length < 5 || args[0] != "replace-font")
            {
                Console.WriteLine("Usage: AssetHelper replace-font <assetsFile> <fontPathId> <ttfFile> <outputAssets>");
                return;
            }

            string assetsPath = args[1];
            long pathId = long.Parse(args[2]);
            string ttfPath = args[3];
            string outputPath = args[4];

            var am = new AssetsManager();
            var inst = am.LoadAssetsFile(assetsPath, true);
            am.LoadClassPackage("classdata.tpk");

            var baseField = am.GetBaseField(inst, inst.file.GetAssetInfo(pathId));
            byte[] ttfBytes = File.ReadAllBytes(ttfPath);

            var fontDataField = baseField.Get("m_FontData");
            fontDataField.GetValue().Set(new AssetTypeByteArray { data = ttfBytes });

            inst.file.GetAssetInfo(pathId).SetNewData(baseField);

            using (var writer = new AssetsFileWriter(outputPath))
            {
                inst.file.Write(writer);
            }
            Console.WriteLine($"[SUCCESS] Font injected into PathID {pathId} -> {outputPath}");
        }
    }
}
```

### 7.3 Text Extraction & Packing Pipeline
Full extraction script (`Pathologic_2_unpacker.py`) and packing script (`Pathologic_2_packer.py`) are located in `05_Scripts_and_Tools/`.
Command to unpack all text to CSV:
```bash
python 05_Scripts_and_Tools/Pathologic_2_unpacker.py
```
Command to pack translated CSV back to assets and game folder:
```bash
python 05_Scripts_and_Tools/Pathologic_2_packer.py --csv 02_Translation_Workspace/Pathologic_2_ui_strings.csv --game-dir "C:\Program Files\GOG Galaxy\Games\Games\Pathologic 2"
```

---

## 8. Troubleshooting

| Symptom | Cause | Solution |
|---|---|---|
| **Tone marks overlap upper vowels (สระลอย/จม)** | Unity Canvas Text lacks OpenType GPOS support | Apply `shift_tone_marks.py` to elevate tone glyphs by `+150` units and remove `GPOS` table before font injection |
| **Text shows square boxes (ToFu □)** | Font does not contain Thai Unicode range (0E01-0E5B) | Inject a full Thai Unicode font (Prompt, Sarabun, or Noto Sans Thai) into all 5 font assets |
| **Main Menu fonts look stretched or misaligned** | Injected font metrics (`Ascender`/`Descender`) differ radically from original | Use `Prompt-Bold` whose line height and bounding box align closely with `libertinussans-bold` and `Vollkorn-Bold` |
| **Game hangs on loading screen** | Corrupted `.assets` file or incorrect file alignment | Ensure AssetsTools.NET writes using proper serialization and uncompressed stream alignment |
| **Dialogue text reverts to English** | Game reading `VirtualMachine/PathologicSandbox/Localizations/english.txt` directly from disk | Ensure translated strings are written directly to `english.txt` within `Pathologic_Data/Data/VirtualMachine/` |

---

## 9. Required Tools

| Tool | Version / Type | Purpose | Source |
|---|---|---|---|
| **AssetsTools.NET** | v3.0.0 (NuGet / .NET 6) | Read, modify, and serialize Unity `.assets` binary files | [GitHub AssetTools.NET](https://github.com/nesrak1/AssetsTools.NET) |
| **fontTools** | Python 3.10+ package | TrueType glyph vector coordinates inspection and Y-axis elevation | `pip install fonttools` |
| **Dotnet SDK** | 6.0.428 (x64) | Compile AssetHelper CLI bridge tools | Microsoft .NET Portal |
| **TStudio / TRun** | THub Flagship Suite | Computer-Aided Translation (CAT) tool for games | THub Toolchain |
| **UnityPy** | v1.20+ (Python) | High-speed asset extraction and byte structure analysis | `pip install unitypy` |

---

## 10. Extracted Assets & Releases

- **Shifted Thai Master Font:**
  - File: `Prompt-Bold_PUA_Shifted.ttf` (270,780 bytes)
  - PostScript Name: `Prompt-Bold`
  - Elevation: +150 Units on 21 tone mark glyphs, GPOS table removed
  - Archive Location: `E:\Mod_Workspace\Modding-Knowledge\Engines\Unity\Games\Pathologic_2\Assets\Fonts\Prompt-Bold_PUA_Shifted.ttf`
- **Official Mod Release Packages (2 Editions):**
  1. **Lite Patcher Edition (Recommended — Only ~2.05 MB Zip / ~7.2 MB Extracted):**
     - Folder: `06_Releases\Pathologic_2_Thai_Mod_v1.0.0_Lite\`
     - Archive: `06_Releases\Pathologic_2_Thai_Mod_v1.0.0_Lite.zip`
     - Features: Standalone `AssetHelper.exe` + `classdata.tpk` (no .NET SDK required). Automatically patches local `sharedassets0.assets` and `resources.assets` in 10–15 seconds. Includes `_Backup_Original` safety rollback.
  2. **Full Monolithic Edition (~908 MB Zip / ~1.5 GB Extracted):**
     - Folder: `06_Releases\Pathologic_2_Thai_Mod_v1.0.0\`
     - Archive: `06_Releases\Pathologic_2_Thai_Mod_v1.0.0.zip`
     - Features: Complete pre-patched `resources.assets` and `sharedassets0.assets`. Direct copy-paste without runtime patching.

---

## 11. M2M Protocol (Machine-to-Machine Automated Rebuild)
For autonomous AI agents rebuilding or updating this mod in continuous integration pipelines:
1. **Step 1 (Font Preparation):** Run `python 03_Font_and_UI/shift_tone_marks.py` to generate the shifted font.
2. **Step 2 (Font Asset Replacement):** Execute `AssetHelper.exe replace-font` for PathIDs `2327`, `2333`, `2334`, `2335`, `2336` targeting `sharedassets0.assets`.
3. **Step 3 (Text Re-injection):** Execute `python 05_Scripts_and_Tools/Pathologic_2_packer.py --csv 02_Translation_Workspace/Pathologic_2_all_strings.csv --game-dir "<TargetGameDir>"`.
4. **Step 4 (Validation):** Execute `python 05_Scripts_and_Tools/Pathologic_2_validator.py --all` to verify zero broken tags or unescaped formatting strings.
