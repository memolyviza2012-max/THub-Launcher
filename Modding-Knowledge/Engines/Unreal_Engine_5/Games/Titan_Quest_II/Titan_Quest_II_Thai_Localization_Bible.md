# Titan Quest II — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer) · verified 2026-07-19

---

## 1. Overview

This Thai localization mod targets **Titan Quest II** and is credited in its README to **Lung Dear**. It uses a **hybrid UE5 replacement/patch architecture**: loose localization CSV, LocRes, and SRT files replace the `zh-Hans` (Simplified Chinese) slot; an IoStore container supplies UE assets; and a separate traditional PAK adds Thai ICU word-breaking data.

The installer copies `ModFiles` into the game root and creates `.modbak` backups only for the original Chinese CSV overrides. In-game, the user selects Simplified Chinese; the locale slot is deliberately reused rather than adding an unsupported `th` locale.

---

## 2. Technical Stack

| Item | Detail |
|---|---|
| **Game Engine** | Unreal Engine 5 — established by IoStore `.utoc`/`.ucas` and UE LocRes magic |
| **Developer** | Grimlore Games / THQ Nordic (as stated by the supplied README) |
| **Project Codename** | `TQ2` (folder and asset namespace) |
| **Archive Format** | IoStore v6: `.utoc` + `.ucas` + companion `.pak`; separate UE PAK for ICU data |
| **AES Encryption** | **No AES-encrypted PAK index**: both PAKs report `encrypted index: false`, all-zero encryption GUID. The UTOC header’s encryption-key GUID area at `0x40–0x4F` is zero. |
| **Compression** | ICU PAK: **None** (verified by repak). IoStore UTOC lists 0 compression-method names; do not claim Oodle/Zlib without decoding its block table. |
| **Font System** | Native game typeface (not redistributed) plus ICU Thai dictionary for Thai line breaking |
| **Thai Font Used** | Not identifiable from supplied files; no `.ttf`, `.otf`, `.ufont`, `.woff`, or `.woff2` exists in the mod |
| **Text System** | UE LocRes plus source CSV string tables and UTF-8 SRT subtitles |
| **Text Encoding** | CSV/SRT: UTF-8 (one CSV has UTF-8 BOM; all show Thai UTF-8 sequences). LocRes: UE binary localization resource; decode with a LocRes-aware tool. |
| **Mod Complexity** | ★★★★☆ — requires coordinated Chinese-slot overrides, IoStore companions, LocRes generation, and ICU dictionary deployment. |

---

## 3. โครงสร้างไฟล์ (File Architecture)

```text
Titan Quest II/
├── ModFiles/
│   ├── Engine/Content/Internationalization/icudt64l/brkitr/
│   │   └── thaidict.dict                                  126,135 B  ICU Thai word dictionary
│   └── TQ2/Content/
│       ├── Localization/
│       │   ├── CSVTranslations/ExportForGame/
│       │   │   ├── EngineOverrides_zh-Hans.csv                 121 B  1 translation row
│       │   │   ├── TQ2_zh-Hans.csv                       2,423,199 B  10,216 rows including header
│       │   │   └── TQ2Dialogues_zh-Hans.csv              1,976,843 B  7,601 rows including header
│       │   ├── TQ2/zh-Hans/TQ2.locres                      151,469 B  UE LocRes
│       │   └── TQ2Dialogues/zh-Hans/TQ2Dialogues.locres  1,311,258 B  UE LocRes
│       ├── Paks/
│       │   ├── pakchunkThai-Windows_P.pak                      347 B  PAK v11, 0 entries, IoStore companion
│       │   ├── pakchunkThai-Windows_P.ucas                3,356,527 B  IoStore payload
│       │   ├── pakchunkThai-Windows_P.utoc                    7,876 B  IoStore v6 TOC
│       │   └── pakchunkThaiICU-Windows_P.pak                126,673 B  PAK v11, one ICU entry
│       └── TQ2/Data/Text/TimedSubtitles/*_zh-Hans.srt       9 files / 54 cues
├── INSTALL.bat                                               2,892 B
└── UNINSTALL.bat                                             2,235 B
```

Archive magic and structure were verified from bytes, not extensions:

| File | Direct evidence |
|---|---|
| `pakchunkThai-Windows_P.pak` | UE PAK magic `E1 12 6F 5A` at `0x8F`; footer version 11; index offset 0, index size 114; repak reports 0 entries, mount `../../../`. |
| `pakchunkThaiICU-Windows_P.pak` | UE PAK magic at `0x1EDD5`; footer version 12; repak identifies one file, mount `../../../Engine/Content/Internationalization/icudt64l/brkitr/`, compression None. |
| `pakchunkThai-Windows_P.utoc` | IoStore magic `2D 3D 3D 2D` repeated four times at `0x00`; version 6; header size `0x90`; 63 TOC entries; 69 compressed-block records of 12 bytes; 64 KiB block size; directory index size 3,439 B; one partition. |
| `TQ2.locres`, `TQ2Dialogues.locres` | UE LocRes GUID magic `0E 14 74 75 67 4A 03 FC 4A 15 90 9D C3 37 7F 1B` at offset 0. |
| `thaidict.dict` | ICU binary header beginning `90 00 DA 27 14 00 00 00 00 00 02 00 44 69 63 74`; `Dict` appears at offset `0x0C`. |

---

## 4. Font Analysis

No redistributable vector font is present. A recursive inventory found no `.ttf`, `.otf`, `.ufont`, `.woff`, or `.woff2`; neither PAK contains font entries. Consequently, there is no valid file for the mandatory Windows font-family query, and no font family, designer, licence, or Thai glyph coverage can be asserted from this package.

The README’s “Thai font + Thai line breaking” claim is supported in part by a concrete asset: `thaidict.dict`, an ICU dictionary for Thai segmentation. Thai has no spaces between many words, so this dictionary enables Unicode line-break decisions; it does **not** contain glyph outlines or replace a font. The plausible architecture is that Titan Quest II’s base UE font already contains Thai glyphs, while this mod supplies localization, ICU break data, and a Chinese-slot override. Treat that as an evidence-based inference, not proof of a specific base font.

Do not convert `thaidict.dict` into a font or edit it as text. If glyphs render as tofu, inspect the base game’s Slate/UMG font assets; if words overflow despite correct glyphs, verify this ICU file is installed at the exact Engine-relative path.

---

## 5. Text Analysis

The human-editable source layer is four-column UTF-8 CSV: `Namespace`, `Key`, `SourceString`, `LocalizedString`. It contains 17,816 translation records: 1 EngineOverride, 10,215 TQ2 records, and 7,600 dialogue records (the three files have 2, 10,216, and 7,601 rows respectively when their headers are included). The dialogue table uses the `ARTICY` namespace, consistent with quest/dialogue graph content; ordinary UI/game strings use multiple namespaces in `TQ2_zh-Hans.csv`.

Two compiled binary LocRes files mirror the main and dialogue tables in the `zh-Hans` locale. Their byte stream does not contain Thai UTF-8 triplets because LocRes is binary and must be parsed with a UE LocRes-aware reader; raw container decoding is not a valid encoding test. Nine loose UTF-8 SRT files supply 54 timed cinematic subtitle cues, again under the Chinese locale suffix.

This split is intentional: CSV is a source/import representation, LocRes is runtime localization data, and SRT is timed subtitle data. Keeping their keys, placeholders (`{0}` etc.), namespaces, locale name, and file suffixes unchanged is essential for lookups to resolve.

---

## 6. Cross-Engine Comparison

This mod most closely resembles the UE5 hybrid pattern documented for **Avowed** in the same knowledge base: a tiny companion PAK is paired with `.utoc`/`.ucas` so the engine mounts the IoStore container. Titan Quest II confirms this pattern with a 347-byte PAK v11 that has zero entries but shares the `pakchunkThai-Windows_P` basename with the UTOC/UCAS pair.

The difference is the font strategy. Avowed packages raw TTF within font assets; Titan Quest II packages **no font** and instead ships a raw ICU Thai dictionary in a separate, uncompressed PAK. It is also closer to a source-driven localization pipeline than a pure IoStore-only mod because its CSV and SRT overrides remain loose, readable UTF-8 files. Therefore, transfer the companion-PAK/IoStore mounting technique from Avowed, but transfer font assets only if the base TQ2 typeface actually lacks Thai coverage.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด

### Font and line-break pipeline

1. Inspect the base game’s actual UMG/Slate font asset before adding a font; do not assume a replacement is needed merely because Thai is being localized.
2. If the native font has Thai glyphs, retain it and deploy `thaidict.dict` exactly to `Engine/Content/Internationalization/icudt64l/brkitr/` through the ICU PAK.
3. If glyphs are missing, package a licensed Thai TTF/OTF as UE Font Face/Font assets in the same container system, then verify every UI weight/style and combining-mark placement.
4. Rebuild the ICU PAK with mount point `../../../Engine/Content/Internationalization/icudt64l/brkitr/`; verify PAK footer magic and index encryption status after packing.

### Text pipeline

1. Export baseline Chinese-slot strings to the exact four-column CSV schema. Keep `Namespace` and `Key` immutable and retain placeholders/markup.
2. Translate only `LocalizedString` in UTF-8. Use CSV quoting correctly for commas, quotes, and newlines.
3. Compile/import the main and dialogue CSV tables into their matching `zh-Hans/*.locres` files with a UE-compatible localization workflow; confirm the LocRes GUID after output.
4. Translate SRT text while preserving cue numbers and timestamp syntax. Keep filenames and `_zh-Hans` suffixes unchanged.
5. Build the IoStore trio with matching basenames: `.pak`, `.utoc`, `.ucas`. Keep the 347-byte PAK companion even though it has zero entries, because it establishes the mount/patch relationship.
6. Install by copying files to the game root, select Simplified Chinese in settings, and test menus, items, skills, quests, dialogue, and all cinematics. Preserve the installer’s `.modbak` backup behaviour.

---

## 8. Troubleshooting

| Symptom | Likely cause | Corrective action |
|---|---|---|
| Game stays Chinese | Wrong locale selected or missing `zh-Hans` files | Choose Simplified Chinese; verify every CSV/LocRes/SRT path and suffix. |
| Game ignores IoStore content | Companion PAK missing or basename mismatch | Deploy `.pak`, `.utoc`, and `.ucas` together as `pakchunkThai-Windows_P.*`; do not delete the zero-entry PAK. |
| Thai shows tofu boxes | Base font lacks glyphs or replacement font package is incomplete | Inspect native fonts; package a licensed Thai font only when needed, including all UI weights. |
| Thai text overflows/no natural wrapping | ICU dictionary not mounted at the Engine-relative path | Verify the extracted `thaidict.dict` path and rebuild the ICU PAK without compression/path changes. |
| Vowels/tone marks collide | Font metrics/shaping issue, not a CSV encoding issue | Test stacked Thai marks with the active runtime font; correct UE font metrics/fallback setup. |
| Garbled text or missing entries | CSV quoting, namespace/key, placeholder, or LocRes compilation changed | Restore keys and tokens, save UTF-8, rebuild LocRes using the compatible tool. |
| Launch crash with UE4SS | The README identifies `dwmapi.dll` injection as incompatible with this build | Disable/rename the injected DLL as the installer does, then retest. |

---

## 9. Required Tools

| Tool | Purpose | Source |
|---|---|---|
| repak | Inspect/list/unpack conventional UE PAK files and verify encryption/compression | https://github.com/trumank/repak |
| Unreal Engine localization tooling / LocRes parser | Compile, inspect, and validate CSV ↔ LocRes without corrupting IDs | Unreal Engine tools / trusted UE localization tooling |
| IoStore-aware UnrealPak or compatible packer | Build matching `.utoc`/`.ucas` containers | Unreal Engine distribution matching the game |
| Python 3 | Count/validate CSV, SRT, hashes, and binary signatures | https://www.python.org/ |
| ICU tooling | Validate dictionary placement/segmentation in an authorised workflow | https://icu.unicode.org/ |

---

## 10. Extracted Assets

| Asset | Result | Metadata |
|---|---|---|
| `Assets/Internationalization/Engine/Content/Internationalization/icudt64l/brkitr/thaidict.dict` | Extracted from `pakchunkThaiICU-Windows_P.pak` | One uncompressed PAK entry; 126,135 B; ICU `Dict` header; SHA-256 `04A9C7F7AB10F7F2123A3782CCB300310EA3A601DBAC09A8173D540E01C2E949`. |
| `Assets/Fonts/EXTRACTION_NOTE.txt` | Font extraction documented | No valid installable font supplied; explains why family verification is not applicable and points to the ICU asset. |

---

## 11. M2M Protocol

This game’s delivered mod does not expose a bitmap-font atlas, so no `.dds`/mapping injector can be truthfully derived. Automation should target its real source formats instead: CSV, SRT, LocRes, PAK, and IoStore.

```python
# validate_csv.py — preserve lookup identity and placeholders before LocRes compilation
import csv, re
with open('TQ2_zh-Hans.csv', encoding='utf-8-sig', newline='') as f:
    for row in csv.DictReader(f):
        assert row['Namespace'] and row['Key']
        assert set(re.findall(r'\{\d+\}', row['SourceString'])) <= set(re.findall(r'\{\d+\}', row['LocalizedString']))
```

```python
# validate_srt.py — timestamps must survive translation intact
import re, pathlib
stamp = re.compile(r'^\d\d:\d\d:\d\d,\d\d\d --> \d\d:\d\d:\d\d,\d\d\d$')
for p in pathlib.Path('TimedSubtitles').glob('*_zh-Hans.srt'):
    assert all(stamp.match(x) for x in p.read_text(encoding='utf-8').splitlines() if ' --> ' in x)
```

Automated release gate: validate CSV/SRT, compile LocRes with the matched UE toolchain, build the IoStore trio, run `repak info` on both PAKs, confirm the ICU file’s mounted path, then launch-test with Simplified Chinese selected. Do not invent a bitmap mapping structure when none is present.
