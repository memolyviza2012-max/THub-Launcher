# Code Vein II — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview

Code Vein II uses Unreal Engine 5 and the supplied Thai mod is a **hybrid overlay/patch**: a traditional Unreal PAK replaces the English LocRes, while an IoStore `.utoc`/`.ucas` pair supplies the font packages. The three patch files are installed under `CodeVein2/Content/Paks/~mods/` and use the `_P` suffix, so all three must remain together.

This revision was rebuilt from the supplied containers rather than relying on filenames: the PAK was unpacked successfully, the LocRes was exported with `pylocres`, and every saved TTF/OTF was validated by magic bytes, Windows font metadata, and its cmap.

---

## 2. Technical Stack

| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Unreal Engine 5 |
| **Developer** | Bandai Namco Studios (not encoded in the mod container) |
| **Mod pattern** | Hybrid overlay: traditional PAK for text + IoStore for font packages |
| **Archive format** | PAK v3 (`pakchunk0-Windows_P.pak`) and IoStore v6 (`.utoc` + `.ucas`) |
| **AES encryption** | **No** — `repak info` reports `encrypted index: false`, encryption GUID `None` |
| **Compression** | PAK payload: Zlib; the expanded LocRes is 3,073,954 B versus a 1,609,179-B PAK. IoStore compression cannot be inferred from a magic byte; treat it as UE5 IoStore-managed. |
| **Font system** | UE font-face/composite packages in IoStore, carrying raw embedded TTF/OTF font programs |
| **Thai font used** | Sarabun ExtraBold, TrueType, 82,632 B; 87 of 128 Thai-block code points in cmap |
| **Text system** | Unreal `WindowsGame.locres`, English locale-slot override (`en`) |
| **Text encoding** | UE LocRes binary string serialization; extracted content contains UTF-16LE Thai code units (no text-file BOM) |
| **Mod complexity** | ★★★★☆ — text and fonts are split across two different UE container systems; rebuilding either incorrectly prevents the patch from loading. |

---

## 3. โครงสร้างไฟล์ (File Architecture)

```
CODE VEIN II/
├─ โดเนท.png                                         1,493,156 B  PNG (89 50 4E 47)
└─ CodeVein2/Content/Paks/~mods/
   ├─ pakchunk0-Windows_P.pak                        1,609,179 B  PAK v3 / Zlib / no AES
   │  └─ ../../../CodeVein2/Content/Localization/WindowsGame/en/
   │     └─ WindowsGame.locres                       3,073,954 B  extracted text asset
   ├─ pakchunk0-Windows_P.utoc                           8,022 B  IoStore TOC v6
   └─ pakchunk0-Windows_P.ucas                      31,636,247 B  IoStore payload / font packages
```

### Binary evidence

| File | Magic / offset | Verified result |
|---|---|---|
| PAK | footer `E1 12 6F 5A` at `0x188DAF` (40 bytes before EOF) | UE PAK v3; one entry; mount point `../../../CodeVein2/Content/Localization/WindowsGame/en/` |
| UTOC | `2D 3D 3D 2D 2D 3D 3D 2D 2D 3D 3D 2D 2D 3D 3D 2D` at `0x0` | IoStore TOC; version field `06 00 00 00` at `0x10` |
| UCAS | starts `00 00 00 00`; no container magic is expected | payload is indexed by the companion UTOC, not standalone by header |
| LocRes | `0E 14 74 75 67 4A 03 FC 4A 15 90 9D C3 37 7F 1B` at `0x0` | Unreal LocRes magic, successfully decoded/exported |

The UTOC names 16 UE packages, including `ChronosFontSet.uasset`, `CHRONOS_SHAPE.uasset`, `CHRONOSSHAPEGAMEPAD.uasset`, and face packages such as `FOT-NEWRODINPRO-M.uasset`, `FOT-TsukuAVintageMinSPro-R.uasset`, and `KALIBERPRO-BOLD.uasset`. This is the link between the UE composite font system and the raw font programs carved from the UCAS.

---

## 4. Font Analysis

Twelve installable fonts were recovered and verified. Their files begin with either TrueType `00 01 00 00` or OpenType CFF `4F 54 54 4F` (`OTTO`); Windows Shell identifies each as a real font file, not an SDF atlas or a renamed binary blob.

| Extracted font | Format / size | Family verified from font metadata | Thai cmap |
|---|---:|---|---:|
| `Sarabun_ExtraBold.ttf` | TTF / 82,632 B | Sarabun ExtraBold | **87/128** |
| `BankGothic_Lt_BT_Light.ttf` | TTF / 40,132 B | BankGothic Lt BT Light | 0 |
| `BioPlasm_Com.ttf` | TTF / 93,048 B | BioPlasm Com | 0 |
| `Cavalero_BT_Roman.ttf` | TTF / 54,392 B | Cavalero BT Roman | 0 |
| `Chronos_BloodFont.ttf` | TTF / 32,956 B | Chronos_BloodFont | 0 |
| `KaliberPro-Bold.otf` | OTF / 47,700 B | Kaliber Pro Bold | 0 |
| `Linotype_Go_Tekk_Black.otf` | OTF / 33,256 B | Linotype Go Tekk Black | 0 |
| `NewCinemaAStd-D.otf` | OTF / 4,697,300 B | FOT-NewCinemaA Std D | 0 |
| `NewRodinPro-B.otf` | OTF / 3,645,060 B | FOT-NewRodin Pro B | 0 |
| `NewRodinPro-M.otf` | OTF / 3,446,496 B | FOT-NewRodin Pro M | 0 |
| `TsukuAVintageMinSPro-R.otf` | OTF / 8,712,592 B | FOT-TsukuAVintageMinS Pro R | 0 |
| `UDKakugoC80Pro-R.otf` | OTF / 3,508,644 B | FOT-UDKakugoC80 Pro R | 0 |

Only Sarabun is a Thai-capable recovered face. UCAS bytes near the Sarabun program include OpenType `thai`, `mark`, and `mkmk` layout tags plus glyph names `uni0E01`–`uni0E59`; those are direct evidence that the font contains Thai shaping/mark-positioning data. Use Sarabun for any composite-font fallback that needs Thai. Do not substitute a Latin or Fontworks face: their cmap checks contain zero Thai-block glyphs.

Sarabun is SIL Open Font License software; the other supplied display/Fontworks faces may be commercially licensed. Preserve their provenance and do not redistribute them separately unless their licence permits it. The Thai character coverage is not a visual-layout guarantee: test above-base vowels and tone marks (for example `กี่`, `ปี่`, `เก่ง`) in the target UI after rebuilding.

---

## 5. Text Analysis

`WindowsGame.locres` is the only PAK entry. It is mounted in `Localization/WindowsGame/en/`, deliberately replacing the English locale rather than adding a native `th` culture. This means players must select English for this patch to be selected.

The extracted file is 3,073,954 B. `pylocres to-csv` successfully produced a 4,215,756-B UTF-16LE CSV with **20,225 parsable namespace/key/hash/source records**; raw scanning finds **296,534 Thai Unicode code points** in the binary. The keys show namespaces organised by game system, including `ColorPalette`, `PhotoFlame`, and `PhotoMenuTextTable`; they are not plain sequential dialogue lines. Preserve namespace, key, hash, placeholders (`{…}`, `%…`), markup, and line breaks when editing.

The LocRes header begins at `0x0` with the 16-byte UE localization magic. It has no UTF-8/UTF-16 text-file BOM because the container serializes strings itself; do not convert the raw `.locres` with a text editor. Export to CSV, edit in Unicode, then rebuild with a LocRes-aware writer.

---

## 6. Cross-Engine Comparison

This follows the same UE5 principle documented for **Frostpunk 2** and **Lords of the Fallen (2023)** in this knowledge base: text is a binary LocRes and font support must be shipped separately from translated strings. Code Vein II differs because its translation PAK is an older **PAK v3 with Zlib and no AES**, while its font assets are supplied as **IoStore v6**. A PAK-only workflow that works for a standard UE game will therefore update text here but leave font assets unchanged; conversely, dropping only the `.ucas` without its matching `.utoc` leaves IoStore unable to index the font payload.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด

### Text pipeline

1. Back up the original game containers and the three mod files as one set.
2. Verify the PAK first: `repak info pakchunk0-Windows_P.pak` must report v3, one entry, Zlib, and `encrypted index: false`.
3. Extract with `repak unpack`; edit only `WindowsGame.locres` through `pylocres` or another LocRes-aware tool.
4. Preserve all namespace/key/hash relationships, UTF-16 text values, format placeholders, rich-text tags, and newline semantics.
5. Rebuild a PAK with the exact mount path `../../../CodeVein2/Content/Localization/WindowsGame/en/`; name it `pakchunk0-Windows_P.pak` only after validating its footer and mount point.

### Font pipeline

1. Start with `Sarabun_ExtraBold.ttf` from `Assets/Fonts`; validate `00 01 00 00`, family name, and Thai glyph coverage before use.
2. Update the UE5 font-face/composite asset that routes fallback glyphs to Sarabun. Do not merely replace a raw byte range: UE assets have package metadata and are indexed by UTOC.
3. Build the matching IoStore output with the game-compatible UE5 toolchain, producing both `.utoc` and `.ucas` together. Keep the same patch base name and `_P` suffix.
4. Install PAK, UTOC, and UCAS in `CodeVein2/Content/Paks/~mods/`, choose English in-game, then test menus, multiline descriptions, variables, Thai vowels, tone marks, and missing-glyph boxes.

---

## 8. Troubleshooting

| Symptom | Cause / fix |
|---|---|
| Thai text is absent | Confirm English is selected and the PAK mount path ends in `WindowsGame/en/`; a `th` folder is not what this patch overrides. |
| Text appears as squares | The LocRes loaded but the Thai fallback font did not. Install matching `.utoc` and `.ucas` alongside the PAK and verify the composite-font mapping targets Sarabun. |
| Tone marks or upper vowels overlap | Ensure the chosen face is Sarabun, retain OpenType shaping tables, and test at the game’s actual UI scale. Avoid Latin Fontworks/BT replacements because they have no Thai glyph coverage. |
| Game fails to load after a font change | Treat `.utoc` and `.ucas` as an inseparable pair. Rebuild with compatible IoStore settings; do not mix a new UCAS with the old TOC. |
| PAK is ignored | Check `_P` suffix, `~mods` location, PAK v3 mount point, and the footer magic `E1 12 6F 5A` at EOF−40. |
| Corrupted Thai | Do not save binary LocRes directly in an editor. Round-trip through a LocRes parser/writer and retain Unicode values and placeholders. |

---

## 9. Required Tools

| Tool | Purpose |
|---|---|
| `repak_cli` | Inspect and unpack/repack the unencrypted traditional PAK |
| `pylocres` | Export/import UE LocRes without treating it as raw text |
| UE5-compatible IoStore/UnrealPak toolchain | Build matching `.utoc`/`.ucas` and package UE font assets |
| FModel | Inspect UE packages and cross-check asset paths/container contents |
| FontTools / Windows Shell font metadata | Verify extracted TTF/OTF validity, family names, and Thai cmap coverage |

---

## 10. Extracted Assets

All files below were checked against format magic before being recorded.

| Asset | Location | Evidence |
|---|---|---|
| 12 verified raw fonts | `Assets/Fonts/` | Five TTF (`00 01 00 00`) and seven OTF (`OTTO`); Sarabun is Thai-capable |
| Expanded localization | `Assets/Texts/WindowsGame.locres` | 3,073,954 B; UE LocRes magic; extracted with `repak` |
| Original text PAK | `Assets/Raw/pakchunk0-Windows_P.pak` | 1,609,179 B; PAK v3 footer; no AES; Zlib |
| Original IoStore TOC | `Assets/Raw/pakchunk0-Windows_P.utoc` | 8,022 B; IoStore v6 header |
| UTOC package inventory | `Assets/Configs/UTOC_Content_Listing.txt` | 16 named UE font/composite packages |
| Mod preview | `Assets/Configs/mod_preview.png` | PNG magic `89 50 4E 47` |

No `EXTRACTION_NOTE.txt` is required for fonts because the recovered deliverables are installable TTF/OTF files, successfully verified as described in section 4.
