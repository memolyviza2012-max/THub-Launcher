# Plague Inc: Evolved — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Plague Inc: Evolved is a popular strategy simulation game developed by Ndemic Creations using the Unity Engine. The Thai localization mod architecture utilizes a **File Replacement (Asset Override)** approach, replacing the main `.assets` files to inject Thai-compatible fonts, while the text strings are likely handled by the game's built-in custom scenario/localization system or injected TextAssets.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Unity |
| **Developer** | Ndemic Creations |
| **Project Codename** | N/A |
| **Archive Format** | `.assets` (Unity) |
| **AES Encryption** | No |
| **Compression** | LZ4 (Unity Standard) |
| **Font System** | Font Swap inside `sharedassets0.assets` |
| **Thai Font Used** | Modified Google Sans (TTF) |
| **Text System** | TextAssets / XML (Custom) |
| **Text Encoding** | UTF-8 |
| **Mod Complexity** | ★★☆☆☆ (Standard Unity Asset repack) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```text
PlagueIncEvolved_Data/
└── sharedassets0.assets (158 MB - Contains main game fonts and core text assets)

ScenarioCreator/
└── PlagueIncSC_Data/
    ├── resources.assets (199 KB)
    └── sharedassets0.assets (124 MB - Contains fonts for the Scenario Creator tool)
```

---

## 4. Font Analysis
- **Font Identification:** The game originally uses "Google Sans" (Regular, Medium, Bold) as its UI font. 
- **Storage Strategy:** The fonts are stored as raw `.ttf` files inside Unity's `sharedassets0.assets` bundle.
- **Font Swap Mapping:** To bypass potential font name whitelisting or hardcoded references, the modder replaced the font data inside the asset bundle but **kept the internal metadata name as "Google Sans"**. The extracted fonts report their name as "Google Sans Regular", but their file sizes and glyph tables have likely been modified (via FontForge or similar tools) to include Thai glyphs.
- **Thai Rendering Considerations:** Unity's internal TrueType renderer displays the text. Any complex text shaping (สระลอย) must be handled by the font's internal GPOS/GSUB tables or pre-shaped in the text files, as standard Unity UI Text does not natively support advanced Thai shaping without TextMeshPro.

---

## 5. Text Analysis
- **File Format:** Plague Inc uses multiple methods for text. The `sharedassets0.assets` contains several `TextAsset` objects (e.g., `hell_on_earth.strings`, `xenolith_type.strings`).
- **External Text:** The game also officially supports custom scenarios and localizations via XML/TXT files placed in the `StreamingAssets/Localisation` or workshop folders.
- **Organization:** The mod provided to Rivet Engineer only contained `.assets` files, indicating that this specific package is primarily a **"Font Fix / Enabler Mod"** designed to allow the game to display Thai text properly, while the actual translation strings might be distributed separately or via Steam Workshop.

---

## 6. Cross-Engine Comparison
Unlike *Encased* which allowed placing external `.locale` files but still required an asset repack for fonts, Plague Inc: Evolved follows a very traditional Unity Modding path. Because the game UI is strictly bound to `GoogleSans` inside `sharedassets0.assets`, the only way to support Thai is to perform a direct byte-replacement of the Font object in the asset bundle. This is identical to how early Unity games (e.g., Hardspace Shipbreaker before BepInEx) were modded.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
**Font Pipeline:**
1. Create a Thai-supporting TTF font and rename its internal metadata (using FontForge) to match "Google Sans".
2. Open `PlagueIncEvolved_Data\sharedassets0.assets` using UABEA (Unity Asset Bundle Extractor) or UnityPy.
3. Search for the `Font` objects: `GoogleSans-Regular`, `GoogleSans-Medium`, `GoogleSans-Bold`.
4. Import the custom Thai TTF over the original font data.
5. Save and overwrite the `.assets` file.
6. Repeat for `ScenarioCreator\PlagueIncSC_Data\sharedassets0.assets`.

**Text Pipeline:**
1. Modify the `TextAsset` strings inside the bundle if needed, OR
2. Place translated XML/TXT files into the game's supported `Localisation` directory.

---

## 8. Troubleshooting
- **Text displays as boxes (□□□):** The game is attempting to use a font weight (e.g., Italic or Black) that was not replaced in the `.assets` file, or the replacement font lacks the necessary Thai Unicode range.
- **Game crashes on startup:** The `sharedassets0.assets` file was repacked with an incorrect Unity version in UABEA. Ensure you use the exact Unity version the game was compiled with.

---

## 9. Required Tools
| Tool Name | Purpose | Source |
|---|---|---|
| UABEA / UnityPy | Extracting and repacking Unity `.assets` | [GitHub - UABEA] |
| FontForge | Modifying TTF internal names and merging Thai glyphs | [FontForge.org] |

---

## 10. Extracted Assets
- [GoogleSans-Regular.ttf](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unity/Games/PlagueInc/Assets/Fonts/GoogleSans-Regular.ttf)
- [GoogleSans-Medium.ttf](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unity/Games/PlagueInc/Assets/Fonts/GoogleSans-Medium.ttf)
- [GoogleSans-Bold.ttf](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unity/Games/PlagueInc/Assets/Fonts/GoogleSans-Bold.ttf)
*(Note: These contain the injected Thai glyphs)*

---

## 11. M2M Protocol
**(สำหรับ AI Agent ที่ต้องการนำคัมภีร์ไปรันสร้างม็อดอัตโนมัติ)**

การสลับฟอนต์ใน Unity แบบ Hard-repack สามารถทำได้อัตโนมัติผ่าน Python Script โดยไม่ต้องใช้ UABEA:

```python
import UnityPy

def inject_plagueinc_fonts(assets_path, custom_regular_ttf, custom_medium_ttf, custom_bold_ttf):
    env = UnityPy.load(assets_path)
    
    font_map = {
        "GoogleSans-Regular": custom_regular_ttf,
        "GoogleSans-Medium": custom_medium_ttf,
        "GoogleSans-Bold": custom_bold_ttf
    }
    
    for obj in env.objects:
        if obj.type.name == "Font":
            data = obj.read()
            font_name = getattr(data, "m_Name", "")
            
            if font_name in font_map:
                with open(font_map[font_name], "rb") as f:
                    data.m_FontData = f.read()
                data.save()
                
    with open(assets_path, "wb") as f:
        f.write(env.file.save())
```
AI สามารถรันคำสั่งนี้เพื่อแทนที่ Font ทั้ง 3 น้ำหนักได้ในครั้งเดียว!
