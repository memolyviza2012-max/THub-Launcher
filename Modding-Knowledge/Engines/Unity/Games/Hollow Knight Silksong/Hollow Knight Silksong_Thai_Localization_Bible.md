# Hollow Knight Silksong — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Hollow Knight: Silksong uses the Unity engine. The localization mod attempts to replace or inject fonts into the game's AssetBundles, but the developer has encrypted the asset bundles natively, restricting direct extraction and modification without the decryption key.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Unity |
| **Developer** | Team Cherry |
| **Project Codename** | N/A |
| **Archive Format** | `.bundle` (Unity AssetBundle) and `.assets` |
| **AES Encryption** | Yes (AssetBundle encrypted, key unknown) |
| **Compression** | LZ4/LZMA (within UnityFS) |
| **Font System** | Unity TextMesh Pro (TMP) in AssetBundle |
| **Thai Font Used** | Unknown (Failed to extract due to encryption) |
| **Text System** | Likely StringTable inside encrypted `.bundle` |
| **Text Encoding** | UTF-8 |
| **Mod Complexity** | ★★★★★ (Requires memory dump to brute-force decryption key) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```
D:\Mods games\Thai Mods\0_Rivet Engineer\Hollow Knight Silksong\
└── Hollow Knight Silksong_Data\
    ├── resources.assets (14.9 MB)
    └── StreamingAssets\
        └── aa\
            └── StandaloneWindows64\
                └── fonts_assets_english.bundle (15.3 MB) [ENCRYPTED]
```

---

## 4. Font Analysis
- Font identification: The `fonts_assets_english.bundle` was targeted for extraction using UnityPy.
- **Extraction failed**: The `BundleFile` is encrypted natively by Unity. UnityPy threw the following error: `The BundleFile is encrypted, but no key was provided!`
- The font is likely a TextMesh Pro SDF Atlas because the game uses Addressables (`aa/StandaloneWindows64`), which typically packs TMP fonts.

---

## 5. Text Analysis
- `resources.assets` was scanned for Thai UTF-8 characters (`0xE0 0xB8`/`0xB9`). Only 3 sequences were found, implying that the main game text is not in `resources.assets`.
- The text is likely located inside another Addressable `.bundle` which is also encrypted.

---

## 6. Cross-Engine Comparison
Most Unity games (like those using BepInEx or standard AssetBundles) do not encrypt their bundles. Hollow Knight: Silksong actively uses Unity's bundle encryption (or a custom derivative). Modders will need to perform a memory dump (`global-metadata.dat`) or hook `set_assetbundle_decrypt_key(key)` at runtime via Il2Cpp dumpers to extract the AES key before modding can begin.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
**Decryption Pipeline (Required First):**
1. Launch the game and attach a memory dumper (e.g., Cheat Engine or Il2CppDumper).
2. Extract the decryption key used for AssetBundles.
3. Feed the key into UnityPy or AssetStudio to unpack the `fonts_assets_english.bundle`.
4. Create a TMP SDF Atlas with Thai characters.
5. Repack the bundle and encrypt it back (or patch the game to load unencrypted bundles).

---

## 8. Troubleshooting
- **Cannot open `.bundle`**: AssetStudio and UnityPy will fail with "Encrypted" error. You must find the key first.
- **Thai characters showing as boxes**: TMP SDF Atlas does not have Thai glyphs. You must generate a new SDF Atlas using Unity Editor with the exact same TMP settings as the original game.

---

## 9. Required Tools
| Tool Name | Purpose | Download Source |
|---|---|---|
| Il2CppDumper | Dumping Il2Cpp to find decryption key | GitHub |
| UnityPy | Extracting / Repacking (once key is found) | PyPI |
| Unity Editor | Generating TMP SDF Atlas | Unity Hub |

---

## 10. Extracted Assets
Extraction failed due to Unity AssetBundle encryption. See `EXTRACTION_NOTE.txt`.
