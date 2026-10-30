# Youtubers Life 2 — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Youtubers Life 2 is a life simulation game developed by U-Play Online and built on the Unity Engine. This Thai localization mod uses a simple File Replacement architecture to replace the game's original localization text file (`locales_EN.txt`) inside the `StreamingAssets` directory.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Unity |
| **Developer** | U-Play Online |
| **Project Codename** | Unknown |
| **Archive Format** | Base64 Encoded Text (Likely Custom Encrypted) |
| **AES Encryption** | Yes (Custom encryption/encoding applied before Base64) |
| **Compression** | Unknown / Encrypted |
| **Font System** | Native (No font replacement provided in this mod, likely uses fallback or built-in fonts) |
| **Thai Font Used** | Unknown (No font extracted) |
| **Text System** | Custom / Encrypted Text File |
| **Text Encoding** | Base64 (Decoded payload is binary encrypted) |
| **Mod Complexity** | ★★☆☆☆ (Simple file replacement for users, but text requires decryption to edit) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```
Youtubers Life 2/
├── วิธีติดตั้ง.txt (220 bytes)
└── Youtubers Life 2_Data/
    └── StreamingAssets/
        └── locales/
            └── locales_EN.txt (3.3 MB)
```

---

## 4. Font Analysis
- This mod does not include any font files (e.g., no `.ttf`, no `.asset` or `.bundle`).
- It relies entirely on the game's existing fonts (potentially a system fallback font) or the developers might have included Thai glyphs natively.
- No font extraction is possible because there are no font files present in the mod package.

---

## 5. Text Analysis
- The text is stored in `Youtubers Life 2_Data\StreamingAssets\locales\locales_EN.txt`.
- Opening the file reveals a single continuous line of Base64 encoded string (`CS1W2tolFxHbt...`).
- When decoded from Base64, the magic bytes are `09 2D 56 DA DA 25 17 11 DB B4 74 FD 83 85 36 65`, which does not match any standard format (like UTF-8, JSON, XML). This implies the developers used a custom encryption algorithm (like AES or DES) before encoding it to Base64.
- Because it is encrypted, we cannot count the exact number of Thai strings or determine the internal string structure without the decryption key.

---

## 6. Cross-Engine Comparison
Unlike typical Unity games that use `resources.assets` or AssetBundles for `StringTable` (e.g., games using Unity Localization package), Youtubers Life 2 uses a custom approach by placing encrypted text files directly into the `StreamingAssets` folder. This is similar to how some indie games protect their text assets from simple modifications, requiring modders to either memory-dump the decrypted text at runtime or reverse-engineer the decryption key from the `Assembly-CSharp.dll` using tools like dnSpy or ILSpy.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
**Text Pipeline:**
1. Use dnSpy/ILSpy to decompile `Youtubers Life 2_Data\Managed\Assembly-CSharp.dll`.
2. Search for the class handling `locales_EN.txt` (often related to Localization or IO reading from `StreamingAssets`).
3. Identify the decryption algorithm (e.g., AES/DES) and extract the key/IV.
4. Write a script (e.g., Python) to decode Base64 and decrypt the payload to a readable format (like JSON or CSV).
5. Translate the text.
6. Encrypt the translated text and encode it back to Base64, then save it as `locales_EN.txt`.

---

## 8. Troubleshooting
- **Game Crash / Stuck on Loading Screen:** The encryption key or padding might be incorrect when repacking `locales_EN.txt`. Ensure the exact same encryption algorithm and block size are used.
- **Missing Text / Boxes:** If the game doesn't natively support Thai fonts, boxes (□□□) will appear. A font replacement mod via BepInEx or Unity AssetBundle extractor would be needed.

---

## 9. Required Tools
| Tool | Purpose | Source |
|---|---|---|
| dnSpy / ILSpy | Decompile Assembly-CSharp.dll to find encryption key | GitHub |
| Python | Scripting decryption/encryption | python.org |

---

## 10. Extracted Assets
- No assets could be extracted because the mod only contains an encrypted text file.
- See `EXTRACTION_NOTE.txt` in the Assets folder (if applicable) for details.
