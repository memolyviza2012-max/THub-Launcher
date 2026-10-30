# Warhammer 40,000: Rogue Trader — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Warhammer 40,000: Rogue Trader is a CRPG developed by **Owlcat Games** using the **Unity Engine (IL2CPP)**. The Thai localization mod uses an exceptionally sophisticated architecture — **Owlcat Modification Framework** — a first-party modding API built by the developer. This is the most "developer-friendly" mod architecture encountered in the entire Knowledge Base. The mod consists of three components working in harmony: a custom C# DLL for runtime font injection, a TextMeshPro (TMP) SDF font bundle, and a massive JSON localization override.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Unity (IL2CPP) |
| **Developer** | Owlcat Games |
| **Project Codename** | RogueTrader |
| **Archive Format** | `.bundle` (Unity AssetBundle) + loose JSON |
| **AES Encryption** | No |
| **Compression** | LZ4 (Unity Standard) |
| **Font System** | Runtime Injection via Owlcat Modification Framework + TextMeshPro SDF Atlas |
| **Thai Font Used** | Chakra Petch StackedPUA Regular (TTF, modified with PUA vowel stacking) |
| **Text System** | JSON key-value localization (`enGB.json`) |
| **Text Encoding** | UTF-8 (without BOM) |
| **Mod Complexity** | ★★★★☆ (Requires C# DLL compilation, TMP SDF Atlas generation, and understanding of Owlcat's mod framework) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```text
WarhammerRogueTrader/
├── OwlcatModificationManagerSettings.json         (190B - Mod manager config, enables the mod)
├── IntroductoryTextOverrides/
│   ├── IntroductoryText.json                      (2.4KB - Title screen text, multi-locale with Thai in enGB slot)
│   ├── ConsoleIntroductoryText.json               (1.7KB)
│   ├── ConsoleXboxIntroductoryText.json           (3.0KB)
│   └── MsStoreIntroductoryText.json               (2.6KB)
└── Modifications/
    └── ProjectModThaiRogueTrader/
        ├── OwlcatModificationManifest.json        (294B - Mod metadata: name, version, author)
        ├── OwlcatModificationSettings.json        (142B - Bundle/blueprint config)
        ├── Assemblies/
        │   └── ProjectModThaiRogueTraderFont.dll  (12KB - C# runtime font bridge)
        ├── Bundles/
        │   └── projectmodthai_roguetrader_chakrapetch_tmp.bundle (478KB - TMP SDF Font Atlas)
        └── Localization/
            └── enGB.json                          (33.6MB - Complete Thai translation, ~6,585 Thai sequences per 50KB)
```

---

## 4. Font Analysis
- **Font Identification:** The mod uses a custom-modified version of **Chakra Petch** (Google Font, open-source) renamed to **"Chakra Petch StackedPUA"**.
- **"StackedPUA" Technique:** This is the most advanced Thai font rendering technique found in the Knowledge Base. The modder has pre-processed the font using **Private Use Area (PUA)** Unicode codepoints to handle สระลอย (floating vowels) and วรรณยุกต์ (tone marks). When a vowel needs to stack above another vowel (e.g., สระอี + ไม้เอก on a tall consonant), the text pipeline substitutes the standard Unicode tone mark with a PUA codepoint that maps to a glyph drawn at a higher vertical offset. This completely bypasses Unity's lack of native Thai complex text shaping.
- **Storage Strategy:** The font is delivered as a **TextMeshPro SDF (Signed Distance Field) Atlas** inside a Unity AssetBundle (`.bundle`). The bundle contains:
  - `TMP_FontAsset` (MonoBehaviour): SDF atlas metadata, glyph lookup table, kerning pairs — familyName: "Chakra Petch StackedPUA", pointSize: 96
  - `Texture2D` atlas: 4MB SDF texture (the actual rendered glyph images)
  - `Font` object: Raw TTF backup (72KB) — this is the installable font file we extracted
  - `Material`: TMP rendering material with SDF shader
- **Runtime Bridge (DLL Analysis):** The `ProjectModThaiRogueTraderFont.dll` (12KB, .NET managed DLL) performs the following at runtime:
  - `FontRuntimeBridge` class: Loads the TMP font bundle via `AssetBundle.LoadFromFile()`
  - `OnTmpTextChanged` event handler: Intercepts every `TMP_Text` component change event
  - `ContainsThaiOrStackedPua()`: Detects Thai text and automatically swaps the font to the injected Chakra Petch SDF atlas
  - `CharacterSpacingZeroed`: Adjusts character spacing for Thai rendering
  - `DontDestroyOnLoad`: Ensures the font bridge persists across scene transitions

---

## 5. Text Analysis
- **File Format:** Standard JSON with UUID keys mapping to translated strings.
- **Encoding:** UTF-8 without BOM. Contains massive Thai content (6,585 Thai sequences in just the first 50KB).
- **File Size:** 33.6 MB — this is a **complete game translation** covering all dialogue, UI, items, lore, tooltips, and quest text.
- **Structure:** `{ "strings": { "<uuid>": { "Key": "<readable_key>", "Value": "<thai_text>" } } }`
- **Locale Override Strategy:** The mod overrides the `enGB` locale slot with Thai text, so when the player selects "English (UK)" in-game, they see Thai instead. This clever trick avoids needing to register a new locale in Unity's localization system.
- **IntroductoryTextOverrides:** Separate JSON files override the title screen / EULA text. These use a multi-locale array format where the `enGB` slot contains Thai text.

---

## 6. Cross-Engine Comparison
This mod represents the **gold standard** of Unity Thai localization modding:

| Feature | Rogue Trader (Owlcat) | Encased (Unity) | Plague Inc (Unity) | Hardspace Shipbreaker (Unity/BepInEx) |
|---|---|---|---|---|
| **Mod Framework** | Owlcat Official API | None (raw asset swap) | None (raw asset swap) | BepInEx (3rd party) |
| **Font Method** | TMP SDF + Runtime DLL | TTF in resources.assets | TTF in sharedassets0 | TTF in BepInEx/plugins/ |
| **Thai Shaping** | StackedPUA (pre-processed) | None | Font-level GPOS | None |
| **Text Format** | JSON (UUID keys) | Binary .locale | TextAsset/XML | .bundle StringTable |
| **Complexity** | ★★★★☆ | ★★☆☆☆ | ★★☆☆☆ | ★★☆☆☆ |

The Owlcat framework is unique because it allows loading custom C# DLLs without needing BepInEx — the game natively supports it. However, this means mod creation requires C# compilation knowledge and TMP font asset generation (via Unity Editor + TMP Font Asset Creator).

---

## 7. Pipeline — ขั้นตอนสร้างม็อด

### Font Pipeline:
1. **Prepare Thai TTF:** Obtain or create a Thai-supporting TTF font (e.g., Chakra Petch from Google Fonts).
2. **PUA Stacking (Optional but Recommended):** Use a font editor (FontForge) to duplicate tone marks/vowels to PUA codepoints with adjusted vertical offsets for stacking scenarios.
3. **Generate TMP SDF Atlas:** Open Unity Editor with TextMeshPro package installed. Use `Window > TextMeshPro > Font Asset Creator` to generate an SDF atlas from the TTF at point size 96.
4. **Build AssetBundle:** Create a Unity project, add the TMP FontAsset, and build it as an AssetBundle named `projectmodthai_roguetrader_chakrapetch_tmp.bundle`.
5. **Create Runtime Bridge DLL:** Write a C# class that:
   - Loads the font bundle via `AssetBundle.LoadFromFile()`
   - Subscribes to `TMPro.TMPro_EventManager.TEXT_CHANGED_EVENT`
   - Swaps fonts on any `TMP_Text` component containing Thai characters
6. **Compile DLL** against the game's managed assemblies (`Kingmaker.GameCore.dll`, `Unity.TextMeshPro.dll`).

### Text Pipeline:
1. **Extract** the original `enGB.json` from the game's localization data.
2. **Translate** all `"Value"` fields from English to Thai (UTF-8).
3. **Apply PUA substitution:** Run a regex/script to replace stacked vowel+tone combinations with PUA codepoints matching the font.
4. **Place** the translated `enGB.json` in `Modifications/ProjectModThaiRogueTrader/Localization/`.

---

## 8. Troubleshooting
- **Font not loading / Default font shown:** Check that `OwlcatModificationManagerSettings.json` has the mod listed in both `EnabledModifications` and `ActiveModifications`. Also verify the bundle file path matches what `FontRuntimeBridge` expects.
- **Thai vowels/tone marks overlap (สระลอย):** The PUA substitution script did not process all edge cases. Check consonant+vowel+tone combinations against the PUA mapping table in the font.
- **Game crash on scene load:** The DLL may reference a wrong assembly version. Recompile `ProjectModThaiRogueTraderFont.dll` against the current game version's managed assemblies.
- **Encoding corruption in JSON:** Ensure the JSON file is saved as UTF-8 without BOM. Some text editors add a BOM which can corrupt the first entry.
- **Text not appearing after game update:** Owlcat updates may change UUID keys. Re-extract the base `enGB.json` and merge translations.

---

## 9. Required Tools
| Tool Name | Purpose | Source |
|---|---|---|
| Unity Editor (2021.3 LTS) | Generating TMP SDF Font Atlas and building AssetBundles | [Unity Hub] |
| TextMeshPro Package | Creating SDF font assets with proper atlas settings | [Unity Package Manager] |
| Visual Studio / Rider | Compiling the C# runtime bridge DLL | [Visual Studio] |
| FontForge | Modifying TTF to add PUA stacking glyphs | [FontForge.org] |
| UnityPy | Extracting/inspecting `.bundle` contents programmatically | [pip install UnityPy] |

---

## 10. Extracted Assets
- [ChakraPetch-Regular-StackedPUA.ttf](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unity/Games/WarhammerRogueTrader/Assets/Fonts/ChakraPetch-Regular-StackedPUA.ttf) — Successfully extracted from TMP bundle via UnityPy. Font family: "Chakra Petch StackedPUA Regular". Contains pre-processed PUA glyphs for Thai vowel stacking.

---

## 11. M2M Protocol
**(สำหรับ AI Agent ที่ต้องการนำคัมภีร์ไปรันสร้างม็อดอัตโนมัติ)**

เกมนี้ใช้ระบบ **Owlcat Modification Framework** ซึ่งเป็น Official Modding API ดังนั้น AI Agent สามารถสร้างม็อดได้โดยใช้ขั้นตอนดังนี้:

### 1. Automated JSON Translation Pipeline
```python
import json

def translate_enGB(input_json_path, output_json_path, translate_func):
    """
    translate_func: callable that takes English text and returns Thai text
    """
    with open(input_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for uuid, entry in data.get('strings', {}).items():
        if 'Value' in entry:
            entry['Value'] = translate_func(entry['Value'])
    
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
```

### 2. Automated PUA Vowel Stacking
```python
import re

# PUA mapping for stacked Thai characters
# When a tone mark appears above a vowel that's already above a tall consonant,
# substitute with PUA codepoint that has higher vertical offset in the font
TALL_CONSONANTS = 'ปฝฟฬ'
ABOVE_VOWELS = '\u0e34\u0e35\u0e36\u0e37'  # สระ อิ อี อึ อื
TONE_MARKS = '\u0e48\u0e49\u0e4a\u0e4b'     # ไม้เอก โท ตรี จัตวา

# PUA base for shifted tone marks (example mapping)
PUA_BASE = 0xF100

def apply_pua_stacking(text):
    pattern = '([' + TALL_CONSONANTS + '])([' + ABOVE_VOWELS + '])([' + TONE_MARKS + '])'
    def replace_match(m):
        consonant, vowel, tone = m.group(1), m.group(2), m.group(3)
        pua_tone = chr(PUA_BASE + ord(tone) - ord(TONE_MARKS[0]))
        return consonant + vowel + pua_tone
    return re.sub(pattern, replace_match, text)
```

### 3. Automated Mod Scaffold Generation
```python
import json
import os

def create_owlcat_mod_scaffold(mod_name, author, output_dir):
    os.makedirs(os.path.join(output_dir, mod_name, 'Assemblies'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, mod_name, 'Bundles'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, mod_name, 'Localization'), exist_ok=True)
    
    manifest = {
        "UniqueName": mod_name,
        "Version": "0.1.0",
        "DisplayName": mod_name,
        "Description": "Thai localization mod",
        "Author": author,
        "Repository": "",
        "HomePage": "",
        "Dependencies": []
    }
    with open(os.path.join(output_dir, mod_name, 'OwlcatModificationManifest.json'), 'w') as f:
        json.dump(manifest, f, indent=2)
    
    manager = {
        "SourceDirectories": [],
        "EnabledModifications": [mod_name],
        "ActiveModifications": [mod_name],
        "DisabledModifications": []
    }
    with open(os.path.join(output_dir, 'OwlcatModificationManagerSettings.json'), 'w') as f:
        json.dump(manager, f, indent=2)
```

**ข้อจำกัดสำหรับ AI:** การสร้าง TMP SDF Atlas และคอมไพล์ DLL ต้องใช้ Unity Editor และ C# Compiler ซึ่ง AI Agent ทั่วไปไม่มีเครื่องมือเหล่านี้ในตัว อย่างไรก็ตาม AI สามารถ:
1. แปลข้อความ JSON ได้ 100%
2. รัน PUA substitution ได้ 100%
3. สร้างโครงสร้างโฟลเดอร์ม็อดได้ 100%
4. **ใช้ซ้ำ** ไฟล์ DLL และ Bundle จากม็อดที่มีอยู่แล้วได้ (เนื่องจากเป็น generic font bridge)
