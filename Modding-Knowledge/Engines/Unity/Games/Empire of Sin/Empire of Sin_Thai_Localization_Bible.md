# Empire of Sin — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Empire of Sin is a strategy game running on the Unity engine, developed by Romero Games. The mod architecture uses a File Replacement pattern for the JSON localization files and a Unity Asset Bundle Replacement (or injection) for the fonts.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Unity 2019.4.41f1 |
| **Developer** | Romero Games |
| **Project Codename** | N/A |
| **Archive Format** | `.bundle` (UnityFS) |
| **AES Encryption** | No |
| **Compression** | LZ4 (UnityFS standard) |
| **Font System** | SDF Injection (TMP Asset Bundle) |
| **Thai Font Used** | SDF Atlas (Texture2D + MonoBehaviour) |
| **Text System** | JSON (Key-Value pairs) |
| **Text Encoding** | UTF-8 without BOM |
| **Mod Complexity** | ★★★☆☆ (Requires Unity asset replacement for SDF fonts and direct JSON editing) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```text
Empire of Sin\
├── StreamingAssets\
│   ├── Bundles~\
│   │   └── gamedata_mainfont_assets_all_ba6bffddeda9d2840b22ede8e00d639e.bundle (4.8MB) - Contains TMP Font Atlas
│   ├── Raw~\
│   │   └── Localization\
│   │       ├── GameData_en.json (7.9MB) - Main text
│   │       └── GameData_en_Asia.json (65KB)
│   └── EmbeddedDLC~\
│       ├── DLC4\
│       │   └── Raw~\Localization\DLC4_en.json (1.3MB)
│       └── DLC5\
│           └── Raw~\Localization\DLC5_en.json (400KB)
```

---

## 4. Font Analysis
- The game uses TextMesh Pro (TMP) for its fonts, packed into `gamedata_mainfont_assets_all_ba6bffddeda9d2840b22ede8e00d639e.bundle`.
- The font is stored as a TMP SDF Atlas (Texture2D + Material + MonoBehaviour font data). The raw TTF/OTF vector data is stripped, meaning the font cannot be easily extracted as a usable TTF.
- Thai rendering considerations (สระลอย, วรรณยุกต์) will require proper text shaping before injecting into the JSON or utilizing a font that has pre-adjusted vertical metrics if no runtime shaper is available.
- Font swap mapping will require replacing the SDF texture and the MonoBehaviour glyph data.

---

## 5. Text Analysis
- **Format:** Plain text `.json` format with key-value pairs (e.g., `"key": "value"`).
- **Encoding:** UTF-8 without BOM.
- **Approximate String Count / File Size:** The main file `GameData_en.json` is massive (7.9MB), containing tens of thousands of strings.
- **Organization:** Strings are organized linearly with prefixes denoting context (e.g., `$_ANIMATION_TEST_SITDOWN_Quote_Intro_say`). DLCs have their own separate JSON files.

---

## 6. Cross-Engine Comparison
Like *Encased* and *Two Point Campus*, this game uses Unity and TextMesh Pro. However, unlike games that allow dropping raw `.ttf` files via BepInEx (such as *Hardspace Shipbreaker*), *Empire of Sin* relies on pre-built Unity Asset Bundles with TMP SDF Atlases. Modders will need to use Unity Asset Bundle Extractor (UABEA) or UnityPy to inject the modified Texture2D and MonoBehaviour data, similar to the process used in *Sea of Stars*.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
**Font Pipeline:**
1. Generate a new TMP Font Asset in Unity (matching the version 2019.4.41f1) with Thai characters.
2. Export the new Font Asset as a bundle.
3. Extract the new bundle using UABEA.
4. Replace the target Font MonoBehaviour, Material, and Texture2D in `gamedata_mainfont_assets_all_ba6bffddeda9d2840b22ede8e00d639e.bundle` with the newly generated ones.
5. Save the modified `.bundle` back to the game directory.

**Text Pipeline:**
1. Open the `.json` files in `StreamingAssets\Raw~\Localization\`.
2. Translate the values corresponding to the keys. Do not modify the keys.
3. Save the file with UTF-8 without BOM encoding.
4. If the game does not support runtime text shaping, apply a regex shaping script to the Thai text before saving the JSON.

---

## 8. Troubleshooting
- **Font not displaying (Square boxes):** The TMP SDF Atlas was incorrectly injected or the MonoBehaviour mapping doesn't match the new texture.
- **Thai vowels/tone marks misaligned (สระลอย):** The game does not support complex text rendering. You must pre-shape the text in the JSON using a shaping script to use specific Unicode replacements for shifted tones/vowels.
- **Game crash after mod installation:** The JSON might have a syntax error (missing comma, unescaped quotes). Validate the JSON before launching.
- **Encoding corruption:** Ensure the JSON is saved as UTF-8 without BOM, not ANSI or UTF-16.

---

## 9. Required Tools
| Tool Name | Purpose | Download Source |
|---|---|---|
| UnityAssetBundleExtractor (UABEA) | Inject SDF Atlas and MonoBehaviour into `.bundle` | GitHub |
| Unity 2019.4.41f1 | Generate new TMP Font Asset | Unity Hub |
| VS Code / Notepad++ | Edit JSON localization files | Official Sites |

---

## 10. Extracted Assets
[EXTRACTION_NOTE.txt](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unity/Games/Empire_of_Sin/Assets/Fonts/EXTRACTION_NOTE.txt)
*Font extraction failed because the font is a TMP SDF Atlas (rasterized texture), so vector data is missing.*

---

## 11. M2M Protocol
**(สำหรับ AI Agent ที่ต้องการนำคัมภีร์ไปรันสร้างม็อดอัตโนมัติ)**

1. **Automated Font Rendering Script (Python):** 
```python
# Create an SDF atlas texture using Pillow and freetype
from PIL import Image, ImageFont, ImageDraw
def create_sdf_atlas(ttf_path, out_path, size=1024, font_size=32):
    # This is a placeholder for actual SDF generation.
    # In a full M2M script, use a library like 'msdfgen' or similar python bindings to generate SDF.
    font = ImageFont.truetype(ttf_path, font_size)
    img = Image.new('L', (size, size), 0)
    draw = ImageDraw.Draw(img)
    # Draw all required Thai glyphs to the atlas...
    img.save(out_path)
```

2. **Automated Text Shaping Script (Regex):**
```python
import re
def shape_thai_text(text):
    # วรรณยุกต์หลบหาง (e.g., ป, ฝ, ฟ)
    text = re.sub(r'([ปฝฟ])([่-๋])', r'\1\2_shifted', text) # Needs custom mapping
    # สระอุ/อู หลบหาง (e.g., ฤ, ญ, ฐ)
    text = re.sub(r'([ญฐ])([ุู])', r'\1_no_tail\2', text)
    return text
```

3. **Automated FNT/Mapping Injector (Struct):**
```python
import struct
import UnityPy
def inject_tmp_monobehaviour(bundle_path, glyph_data_dict):
    env = UnityPy.load(bundle_path)
    for obj in env.objects:
        if obj.type.name == "MonoBehaviour":
            data = obj.read()
            # Serialize and pack the glyph_data_dict back into the MonoBehaviour
            # using struct.pack and the specific TMP schema for Unity 2019.4
            pass
    # Save bundle
```
