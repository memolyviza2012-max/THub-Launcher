# Encased — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Encased is a classic isometric sci-fi post-apocalyptic RPG. The game runs on the Unity Engine and utilizes Unity's Asset Bundle system for core resources along with a custom localization loading system (`.locale` files) stored in the `StreamingAssets` directory. The mod architecture pattern is a **Hybrid (Asset Replacement + Streaming File Swap)**.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Unity |
| **Developer** | Dark Crystal Games |
| **Project Codename** | N/A |
| **Archive Format** | `.assets` (Unity) and custom `.locale` |
| **AES Encryption** | No |
| **Compression** | LZ4 (Unity Standard) |
| **Font System** | Font Swap inside `resources.assets` |
| **Thai Font Used** | ChakraPetch-Regular (TTF) |
| **Text System** | Custom Binary `.locale` / `.fontlocale` |
| **Text Encoding** | UTF-8 (without BOM) |
| **Mod Complexity** | ★★☆☆☆ (Simple Unity extraction/repack + loose file text modding) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```text
Encased_Data/
├── resources.assets (Unity Asset Bundle containing the injected Thai font)
└── StreamingAssets/
    └── Localization/
        ├── En.fontlocale (Original font config)
        ├── En.locale (Original English text database)
        ├── En_MOD.fontlocale (Modded font config pointing to Thai font)
        └── En_MOD.locale (Modded Thai text database, 6.6MB)
```

---

## 4. Font Analysis
- **Font Identification:** The mod injects `ChakraPetch-Regular.ttf` (an open-source Google Font).
- **Storage Strategy:** The TTF is directly packed into the main `resources.assets` file using a tool like Unity Assets Bundle Extractor (UABEA) or UnityPy.
- **Font Swap Mapping:** The game uses `.fontlocale` files in `StreamingAssets` to map the loaded font to the language. The modder created `En_MOD.fontlocale` to force the game to load the injected Thai font when English is selected.
- **Thai Rendering Considerations:** Since it is a raw TTF, the game's internal Unity UI renderer handles basic text displaying. Complex shaping (สระลอย) might not be fully supported unless handled by the TextMeshPro SDF (which is not used here) or manual pre-shaping in the `.locale` file.

---

## 5. Text Analysis
- **File Format:** Custom `.locale` format. It contains mixed binary structures with embedded XML-like tags (e.g., `<nr>`, `<LRCronus>`) and raw string sequences.
- **Encoding:** UTF-8 without BOM. A scan of the first 10KB of `En_MOD.locale` revealed over 2,600 Thai UTF-8 sequences.
- **Approximate String Count / File Size:** The modded `En_MOD.locale` file is approximately 6.6MB, containing tens of thousands of dialogue and UI strings.
- **Organization:** Strings are stored sequentially with binary delimiters and tags indicating speaker/context (e.g., `- User`, `- Admin`).

---

## 6. Cross-Engine Comparison
Unlike typical Unity games that use `BepInEx` for runtime injection (e.g., Hardspace Shipbreaker, Disco Elysium), Encased has a built-in localization override system via `StreamingAssets/Localization/`. This makes it exceptionally easy to mod the text (just drop in a new `.locale` file). However, because the game doesn't load external fonts dynamically from `StreamingAssets`, the modder still had to hard-repack `resources.assets` to inject the Thai TTF.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
**Font Pipeline:**
1. Use UABEA (Unity Asset Bundle Extractor) or UnityPy to open `Encased_Data\resources.assets`.
2. Locate the main UI `Font` object.
3. Import `ChakraPetch-Regular.ttf` to replace the existing font data.
4. Save and overwrite `resources.assets`.

**Text Pipeline:**
1. Create a script or use a community tool to parse the `.locale` binary format.
2. Dump strings to CSV/JSON.
3. Translate the text into Thai (UTF-8).
4. Repack the text back into the `.locale` binary format, ensuring offsets and lengths are updated if the tool requires it.
5. Create `En_MOD.locale` and `En_MOD.fontlocale` in `StreamingAssets\Localization\`.

---

## 8. Troubleshooting
- **Text displays as boxes (□□□):** Ensure that `resources.assets` was properly repacked and that `En_MOD.fontlocale` correctly references the injected font name.
- **Game hangs on launch:** If `resources.assets` is corrupted during repack (e.g., using an incompatible UABEA version), the game will fail to boot. Use the exact Unity version (2019/2020) that the game was built with when repacking.
- **Encoding Corruption:** Ensure your text packer outputs UTF-8 without BOM.

---

## 9. Required Tools
| Tool Name | Purpose | Source |
|---|---|---|
| UABEA / UnityPy | Extracting and repacking Unity `resources.assets` | [GitHub - UABEA] |
| Custom Locale Parser | Unpacking and repacking `.locale` files | [Community / Modder's Custom Script] |
| Notepad++ | Verifying UTF-8 encoding | [Notepad++] |

---

## 10. Extracted Assets
- [ChakraPetch-Regular.ttf](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unity/Games/Encased/Assets/Fonts/ChakraPetch-Regular.ttf) (Successfully extracted via UnityPy)

---

## 11. M2M Protocol
**(สำหรับ AI Agent ที่ต้องการนำคัมภีร์ไปรันสร้างม็อดอัตโนมัติ)**

เนื่องจากเอนจิน Unity ในเกม Encased รองรับไฟล์ TTF โดยตรง (ไม่ต้องแปลงเป็น Bitmap) AI สามารถใช้ UnityPy ในการแพ็กไฟล์ฟอนต์กลับเข้า `resources.assets` ได้ทันทีดังนี้:

```python
import UnityPy

def inject_font_unitypy(assets_path, ttf_path, target_font_name):
    # Load the Unity assets file
    env = UnityPy.load(assets_path)
    
    # Read the new TTF bytes
    with open(ttf_path, "rb") as f:
        new_font_data = f.read()
        
    # Iterate and replace
    for obj in env.objects:
        if obj.type.name == "Font":
            data = obj.read()
            if getattr(data, "m_Name", "") == target_font_name:
                data.m_FontData = new_font_data
                data.save()
                break
                
    # Save the modified assets file
    with open(assets_path, "wb") as f:
        f.write(env.file.save())
```
AI สามารถรันสคริปต์นี้เพื่อทำ Font Swap โดยอัตโนมัติโดยไม่ต้องเปิดโปรแกรม UABEA เลย!
