# Coral Island — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Coral Island is a farming simulation game developed by Stairway Games using Unreal Engine 4/5. The mod architecture pattern typically involves File Replacement (replacing `.pak` or loose files like `.locres` and `.ufont`).

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Unreal Engine 4 |
| **Developer** | Stairway Games |
| **Project Codename** | ProjectCoral |
| **Archive Format** | .pak (loose files found in dump) |
| **AES Encryption** | No |
| **Compression** | None (Unpacked) |
| **Font System** | Font Swap (.ufont) |
| **Thai Font Used** | Noto Sans Thai Looped (Black, Bold, Regular, SemiBold) |
| **Text System** | LocRes |
| **Text Encoding** | UTF-8 / UTF-16 LE |
| **Mod Complexity** | ★★☆☆☆ (Standard UE4 replacement) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```
Coral Island/
└── Content/
    └── ProjectCoralGDK/
        └── Content/
            └── ProjectCoral/
                └── UI/
                    └── Fonts/
                        ├── Noto/Sans/Thai/
                        │   ├── NotoSansThaiLooped-Black.ufont (63 KB)
                        │   ├── NotoSansThaiLooped-Bold.ufont (66 KB)
                        │   ├── NotoSansThaiLooped-Regular.ufont (77 KB)
                        │   └── NotoSansThaiLooped-SemiBold.ufont (63 KB)
                        └── Piazzolla-*.ufont
```

---

## 4. Font Analysis
- **Font Family**: Noto Sans Thai Looped
- **Format**: .ufont (containing raw TTF/OTF data)
- **Swap Mapping**: Replaces the game's default fonts like Piazzolla or QTVagaRound with Noto Sans Thai Looped.
- **Thai rendering**: Needs standard UE4 Thai glyph handling for floating vowels and tone marks. Noto Sans Thai Looped usually handles these reasonably well if mapped correctly in the engine.

---

## 5. Text Analysis
- **Format**: `.locres` standard UE4 format.
- **Encoding**: UTF-16 LE typically used by UE4 for LocRes.
- **Organization**: Text strings are organized into namespaces and keys.

---

## 6. Cross-Engine Comparison
Like other standard UE4 games (e.g., Remnant 2), Coral Island uses `.locres` for strings and `.ufont` for fonts. The process of unpacking the `.pak`, editing the `.locres` with UnrealLocres, and packing it back is standard.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
**Font Pipeline:**
1. Unpack original `.pak` using UnrealPak or repak_cli.
2. Locate the `.ufont` files in `Content/ProjectCoral/UI/Fonts`.
3. Replace them with Thai-supporting `.ufont` files (or inject TTF into `.ufont`).
4. Repack using UnrealPak.

**Text Pipeline:**
1. Extract `.locres` from `.pak`.
2. Edit using UnrealLocres.
3. Save and repack.

---

## 8. Troubleshooting
- **Font not displaying**: Ensure the font replacement includes all weights (Regular, Bold, etc.).
- **Thai vowels/tone marks misaligned (สระลอย)**: This is common in UE4. If Noto Sans Thai Looped doesn't render perfectly, manual Font Forge adjustment or a UE4 plugin might be needed.
- **Game crash after mod installation**: Check if the `.pak` is packed correctly without compression if the game doesn't support it, or with the correct UE version flag.

---

## 9. Required Tools
| Tool | Purpose | Source |
|---|---|---|
| repak_cli / UnrealPak | Unpack/Pack .pak files | repak github / Epic Games |
| UnrealLocres | Edit .locres files | GitHub |

---

## 10. Extracted Assets
- [NotoSansThaiLooped-Black.ttf](Assets/Fonts/NotoSansThaiLooped-Black.ttf)
- [NotoSansThaiLooped-Bold.ttf](Assets/Fonts/NotoSansThaiLooped-Bold.ttf)
- [NotoSansThaiLooped-Regular.ttf](Assets/Fonts/NotoSansThaiLooped-Regular.ttf)
- [NotoSansThaiLooped-SemiBold.ttf](Assets/Fonts/NotoSansThaiLooped-SemiBold.ttf)
