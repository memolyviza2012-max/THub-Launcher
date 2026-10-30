# Sea of Stars — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Sea of Stars is a retro-inspired turn-based RPG developed by **Sabotage Studio** using the **Unity Engine** with the **Addressable Asset System**. The Thai localization mod (by **Artdekdok** / เพจ "ไม่พร้อมไม่แจก") replaces **19 AssetBundle files** — a massive mod covering the game's entire content including UI, scenes, animations, sprites, and text. The font system uses **TextMeshPro** with pixel-art-style bitmap fonts modified to include 87 Thai characters each. This is a distinctive pixel-art RPG mod where the Thai font style must match the game's retro 8-bit aesthetic.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Unity Engine (with Addressable Asset System) |
| **Developer** | Sabotage Studio |
| **Mod Author** | Artdekdok (ไม่พร้อมไม่แจก) |
| **Game Version** | 1.0.48412 |
| **Archive Format** | `.bundle` (Unity AssetBundle, magic `UnityFS\x00`) |
| **AES Encryption** | No |
| **Compression** | Unity LZ4 |
| **Font System** | TextMeshPro (TMP) — Bitmap + SDF mixed |
| **Thai Fonts** | 3 pixel-art fonts: mono 08_55, copy 10_56, kroeger 05_55 (87 Thai each) |
| **Font Atlas** | 256×256 pixels (small — pixel art style) |
| **Text System** | MonoBehaviour objects (structured data) |
| **Text Encoding** | UTF-8 (standard Unity) |
| **Total Bundles** | 19 files (192 MB total) |
| **Mod Complexity** | ★★★☆☆ (Addressable bundle replacement, TMP pixel font creation) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```text
SeaOfStars_Data/StreamingAssets/aa/StandaloneWindows64/
│
├── 3110f03d...bundle     (385 KB — FONT BUNDLE: 4 TMP FontAssets + 5 atlas textures)
│   ├── TMP Font: 'mono 08_55'    (280 glyphs, 87 Thai, Bitmap 256×256)
│   ├── TMP Font: 'copy 10_56'    (198 glyphs, 87 Thai, SDF 256×256)
│   ├── TMP Font: 'kroeger 05_55' (280 glyphs, 87 Thai, Bitmap 256×256)
│   ├── TMP Font: 'orpheus-40'    (10 glyphs, 0 Thai — display/title font only)
│   └── Textures: 5 atlas PNGs + gradient
│
├── 1bbf0837...bundle     (3.1 MB — 420 MonoBehaviours, 131,990 Thai chars — MAIN TEXT)
├── 713087dc...bundle     (1.2 MB — 156 MonoBehaviours, 54,772 Thai chars)
├── 5608dae2...bundle     (928 KB — 72 MonoBehaviours, 42,862 Thai chars)
├── 8b4e6fb8...bundle     (655 KB — 96 MonoBehaviours, 30,259 Thai chars)
├── f30a27b6...bundle     (489 KB — 96 MonoBehaviours, 22,737 Thai chars)
├── be594216...bundle     (452 KB — 72 MonoBehaviours, 20,356 Thai chars)
├── 33076ec7...bundle     (529 KB — 24 MonoBehaviours, 13,204 Thai chars)
├── 42e2a41d...bundle     (240 KB — 48 MonoBehaviours, 10,941 Thai chars)
├── 2efa5572...bundle     (88 KB — 36 MonoBehaviours, 3,679 Thai chars)
├── 2354a5b9...bundle     (36 KB — 12 MonoBehaviours, 1,359 Thai chars)
├── 0c4c9ab3...bundle     (21 KB — 12 MonoBehaviours, 756 Thai chars)
├── 04fffc73...bundle     (14 KB — 12 MonoBehaviours, 322 Thai chars)
├── b2756c2b...bundle     (15 KB — 12 MonoBehaviours, 309 Thai chars)
├── 3ad88e5a...bundle     (14 KB — 12 MonoBehaviours, 268 Thai chars)
├── 3742516f...bundle     (11 KB — 12 MonoBehaviours, 141 Thai chars)
│
├── 4bb9c63b...bundle     (31 MB — UI bundle: Canvas, Sprites, Animators)
├── 6d3223da...bundle     (90 MB — Scene bundle: GameObjects, Meshes, Animations)
└── 89bada85...bundle     (61 MB — Sprite atlas: 1,137 sprites/textures)
```

---

## 4. Font Analysis

### 4.1 Pixel Art Font System — เอกลักษณ์ของ Retro RPG
Sea of Stars ใช้ฟอนต์แบบ **pixel art** (bitmap) ที่ออกแบบมาให้เข้ากับสไตล์ retro 8-bit/16-bit ของเกม — ฟอนต์ทั้ง 3 ตัวมี point size เพียง **8 pixels** และ atlas ขนาดเล็กแค่ **256×256**:

| Font Name | Glyphs | Thai | Type | Atlas Size | Usage |
|---|---|---|---|---|---|
| **mono 08_55** | 280 | 87 | Bitmap | 256×256 | Monospace (dialogue?) |
| **copy 10_56** | 198* | 87 | SDF | 256×256 | Main text |
| **kroeger 05_55** | 280 | 87 | Bitmap | 256×256 | UI labels |
| orpheus-40 | 10 | 0 | SDF | 128×128 | Title/display only |

*copy 10_56 มี 198 glyphs แต่ 280 characters — บางตัวอักษรแชร์ glyph เดียวกัน (aliased)

### 4.2 Thai Coverage
ฟอนต์ทั้ง 3 ตัวมี **87 Thai characters** (U+0E01–U+0E5B) ครบทั้ง:
- พยัญชนะ 44 ตัว (ก-ฮ)
- สระ 18 ตัว
- วรรณยุกต์ 4 ตัว
- เลขไทย 10 ตัว (๐-๙)
- เครื่องหมายพิเศษ (ๆ, ฯ, etc.)

### 4.3 Pixel Art Font Challenge
การสร้างฟอนต์ไทยแบบ pixel art ที่ pointSize = 8 เป็นความท้าทายมาก — อักษรไทยมีสระลอยและวรรณยุกต์ที่ต้อง render ภายใน grid ขนาดเล็กมาก ม็อดเดอร์ต้องออกแบบ Thai pixel glyphs ทีละตัวด้วยมือ

---

## 5. Text Analysis
- **Format:** MonoBehaviour objects ภายใน AssetBundles (structured data)
- **Distribution:** กระจายอยู่ใน **15 bundles** (จาก 19 ทั้งหมด)
- **สถิติ:**
  - **333,955 อักษรไทย** ทั้งหมด
  - Bundle หลัก `1bbf0837...` มี 131,990 Thai chars (39.5% ของทั้งหมด)
  - 1,100+ MonoBehaviour objects มีข้อความไทย

---

## 6. Cross-Engine Comparison
เปรียบเทียบกับเกม Unity Addressable อื่น:

| Feature | Sea of Stars | SOS: Grand Bazaar | Warhammer: Rogue Trader |
|---|---|---|---|
| **Font System** | TMP Bitmap (pixel art) | TMP SDF | TMP SDF (PUA) |
| **Atlas Size** | 256×256 (tiny!) | 4096×4096 | Custom |
| **Font Style** | Pixel art (8pt) | Sans-serif (30pt) | Serif (varies) |
| **Thai Glyphs** | 87 per font | 87 per font | PUA-mapped |
| **Bundle Count** | 19 bundles | 3 bundles | Multiple |
| **Thai Chars** | 334K | 887K | ~200K |
| **Total Size** | 192 MB | 72 MB | Varies |
| **Complexity** | ★★★☆☆ | ★★★☆☆ | ★★★★☆ |

---

## 7. Pipeline — ขั้นตอนสร้างม็อด

### Font Pipeline:
1. **ออกแบบ Thai pixel font:** ใช้ pixel art editor (Aseprite, Piskel) ออกแบบ glyphs ขนาด 8×8 หรือ 8×16
2. **สร้าง TMP FontAsset:** Import pixel font TTF/BDF → Unity TMP Font Asset Creator
   - Atlas: 256×256
   - Rendering: Bitmap (ไม่ใช่ SDF สำหรับ pixel fonts)
   - Characters: Thai range U+0E01–U+0E5B
3. **Build AssetBundle:** ใช้ Addressable system build
4. **ตั้งชื่อ hash:** ต้องตรงกับชื่อเดิม `3110f03daa2d3bfb83d051ce6920e75b.bundle`

### Text Pipeline:
1. **แตก bundle:** ใช้ UnityPy
2. **อ่าน MonoBehaviour:** `read_typetree()`
3. **แปล text fields**
4. **เขียนกลับ:** `save_typetree()` → build bundle

### Deployment:
```
GameFolder/SeaOfStars_Data/StreamingAssets/aa/StandaloneWindows64/
└── (replace all 19 bundle files)
```

---

## 8. Troubleshooting
- **ฟอนต์ไทยเป็นกล่อง:** ตรวจว่า font bundle (`3110f03d...`) ถูกแทนที่และ TMP FontAssets มี Thai character map ครบ 87 ตัว
- **ข้อความยังเป็นอังกฤษ:** ต้องแทนที่ text bundles ทั้งหมด (15 bundles) ไม่ใช่แค่ font bundle
- **ตัวอักษรซ้อนทับ/ตำแหน่งผิด:** Pixel font ขนาด 8pt อาจมีปัญหากับสระลอย — ต้องปรับ glyph metrics ใน TMP FontAsset
- **เกมแครช:** ชื่อ hash ของ bundle ต้องตรงกับ Addressable catalog — อย่าเปลี่ยนชื่อไฟล์

---

## 9. Required Tools
| Tool Name | Purpose | Source |
|---|---|---|
| Unity Editor + TMP | สร้าง TMP FontAsset | [Unity Hub] |
| UnityPy | แตก/แก้ AssetBundles | [UnityPy PyPI] |
| UABEA | GUI tool สำหรับ AssetBundle | [UABEA GitHub] |
| Aseprite / Piskel | ออกแบบ Thai pixel font glyphs | [Aseprite.org] |

---

## 10. Extracted Assets
- **Font Atlas Images (TMP Bitmap/SDF):**
  - [copy1056-webfontBitmap Atlas](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unity_Engine/Games/Sea_of_Stars/Assets/SDF_Atlas/sos2_copy1056-webfontBitmap_Atlas.png) — 256×256 (copy 10_56)
  - [MonoSDF Atlas](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unity_Engine/Games/Sea_of_Stars/Assets/SDF_Atlas/sos2_MonoSDF_Atlas.png) — 256×256 (mono 08_55)
  - [kroegerBitmap Atlas](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unity_Engine/Games/Sea_of_Stars/Assets/SDF_Atlas/sos2_kroegerBitmap_Atlas.png) — 256×256 (kroeger 05_55)
  - [orpheus-40 SDF Atlas](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unity_Engine/Games/Sea_of_Stars/Assets/SDF_Atlas/sos2_orpheus-40_SDF_Atlas.png) — 128×128 (display font, no Thai)
- **Note:** No standalone TTF/OTF extractable. Pixel fonts are bitmap-only within TMP.

---

## 11. M2M Protocol
**(สำหรับ AI Agent ที่ต้องการนำคัมภีร์ไปรันสร้างม็อดอัตโนมัติ)**

### 1. Automated Text Extractor
```python
import os, json
import UnityPy

def extract_all_thai_text(bundle_dir):
    """Extract Thai text from all Sea of Stars bundles"""
    all_texts = []
    
    for fname in os.listdir(bundle_dir):
        if not fname.endswith('.bundle'):
            continue
        fpath = os.path.join(bundle_dir, fname)
        env = UnityPy.load(fpath)
        
        for obj in env.objects:
            if obj.type.name == 'MonoBehaviour':
                try:
                    tree = obj.read_typetree()
                    tree_str = json.dumps(tree, ensure_ascii=False, default=str)
                    if any('\u0e00' <= c <= '\u0e7f' for c in tree_str):
                        all_texts.append({
                            'bundle': fname,
                            'path_id': obj.path_id,
                            'data': tree
                        })
                except:
                    pass
    
    return all_texts
```

### 2. ข้อจำกัดสำหรับ AI
- **Text Pipeline:** ⚠️ AI อ่านได้ผ่าน UnityPy แต่การเขียนกลับ 19 bundles ต้องทดสอบ compatibility
- **Font Pipeline:** ❌ ต้องออกแบบ Thai pixel glyphs ด้วยมือ + Unity Editor
- **Scale:** ต้องแทนที่ **19 bundles** (192 MB) — ม็อดขนาดใหญ่มาก
