# Frostpunk 2 — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer) · verified 2026-07-19

---

## 1. Overview

This Thai mod for **Frostpunk 2** is a UE5 standard PAK patch, delivered as `Frostpunk2_EASYMODS1.1.1_P.pak` plus a loose replacement `intro_en.srt`. The PAK overrides English (`en` and `en-US-POSIX`) localization resources and replaces UI FontFace payloads with Thai-capable font data; the SRT separately replaces the intro movie subtitles.

Installation evidence from the supplied instructions places the PAK under `Frostpunk2/Content/Paks/~mods/` and the SRT under `Frostpunk2/Content/Movies/`. This is a hybrid file-replacement/PAK-override workflow.

---

## 2. Technical Stack

| Item | Detail |
|---|---|
| **Game Engine** | Unreal Engine 5 (UE PAK, UE LocRes, `.uasset`/`.uexp`/`.ufont`) |
| **Developer** | 11 bit studios |
| **Archive Format** | UE PAK v3, 550 entries, mount point `../../../` |
| **AES Encryption** | **No AES encryption** — repak reports `encrypted index: false`; no encryption GUID. |
| **Compression** | None at PAK-entry level (repak report) |
| **Font System** | UE FontFace `.ufont` raw OTF replacement |
| **Thai Font Used** | CS PraJad Bold, OTF, 87 Thai cmap code points in sampled payloads |
| **Text System** | UE LocRes (`Game.locres`) plus UTF-8 SRT subtitle replacement |
| **Text Encoding** | LocRes binary with Thai UTF-16 LE evidence; SRT is UTF-8 Thai text |
| **Mod Complexity** | ★★★★☆ — two locale resources, 180 FontFace assets, and a separate cinematic subtitle override. |

---

## 3. โครงสร้างไฟล์ (File Architecture)

```text
Frostpunk 2 mod/
├── ~mods/Frostpunk2_EASYMODS1.1.1_P.pak       489,967,684 B
│   ├── Frostpunk2/Content/Localization/Game/en/Game.locres
│   ├── Frostpunk2/Content/Localization/Game/en-US-POSIX/Game.locres
│   └── 180 `.ufont` FontFace payloads + matching `.uasset`/`.uexp`
├── intro_en.srt                                  1,853 B  loose intro subtitles
└── วิธีติดตั้ง_Intro_en.txt                         652 B  installation instructions
```

The PAK begins with binary entry data and its footer holds UE magic `E1 12 6F 5A`; the signature is 44 bytes from EOF. RePak verifies version 3, 550 entries, no encryption, no compression, and mount `../../../`. Both extracted LocRes files begin UE localization GUID `0E 14 74 75 67 4A 03 FC 4A 15 90 9D C3 37 7F 1B`.

---

## 4. Font Analysis

The archive lists 180 `.ufont` assets across Barlow, Barlow Condensed, Barlow Semi Condensed, Crimson Pro, and international font variants. Three independent representative FontFace payloads were extracted and validated at offset zero as OpenType (`OTTO`), each with 13 valid tables including `CFF `, `GDEF`, `GPOS`, `GSUB`, `cmap`, `head`, `maxp`, and `name`.

| Original UE asset path | Extracted payload identity | Size | Thai cmap code points |
|---|---|---:|---:|
| `Barlow/Barlow-Regular.ufont` | CS PraJad Bold | 33,104 B | 87 |
| `BarlowCondensed/BarlowCondensed-Regular.ufont` | CS PraJad Bold | 33,104 B | 87 |
| `CrimsonPro/CrimsonPro-Regular.ufont` | CS PraJad Bold | 33,104 B | 87 |

This proves a filename-preserving Font Swap: the game continues requesting its original Barlow/Crimson paths, but receives Thai-capable CS PraJad Bold OTF data. The sampled payloads are byte-identical in size/family; do not assume every one of the 180 assets is identical without a full hash comparison. Test headings, condensed UI, italics, and dialogue carefully because substituting one bold face for many source weights can alter layout and Thai combining-mark spacing.

---

## 5. Text Analysis

The PAK contains two compiled LocRes resources: `en/Game.locres` (3,609,977 B; 388,963 Thai UTF-16 LE code units observed) and `en-US-POSIX/Game.locres` (3,687,462 B; 530,497 observed). The dual locale override is intentional: the game can select either generic English or the POSIX regional fallback.

The LocRes files are binary; apparent `00 01 00 00` sequences inside them are not valid font headers and must not be carved. Decode/count strings only with a UE LocRes-aware reader. `intro_en.srt` contains 15 timed intro cues and must retain its cue numbering and timestamp syntax while translating.

---

## 6. Cross-Engine Comparison

Like other UE5 PAK localization mods, this uses `_P.pak` override priority and standard LocRes rather than runtime injection. Unlike IoStore-based Tempest Rising, Frostpunk 2 has a single traditional PAK v3 with an accessible index, making `repak` extraction viable without UTOC/UCAS pairing.

Its strategy resembles a conventional font-swap mod: original UE asset paths are retained while raw OTF payloads are replaced. This is more direct than Titan Quest II’s native-font/ICU approach, but broad replacement across many source families increases UI-layout risk.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด

### Font pipeline

1. Unpack the PAK with repak and preserve every original asset path.
2. Place licensed Thai OTF/TTF data into UE FontFace `.ufont` payloads; validate table directories and cmap Thai coverage.
3. Maintain a tested mapping for regular, condensed, heading, and italic UI assets rather than blindly copying one weight everywhere.
4. Repack as a UE PAK patch with `_P.pak` suffix, matching mount `../../../`; verify footer magic, index encryption, and entry list.

### Text pipeline

1. Extract both English LocRes variants and use a LocRes tool to preserve namespaces, keys, and placeholders.
2. Translate/save using the exact UE serialization; test both `en` and `en-US-POSIX` language selection paths.
3. Translate SRT text while preserving 15 cue IDs and timestamps; deploy it separately to `Content/Movies`.
4. Place the finished PAK in `Content/Paks/~mods/`, then test menus, laws, factions, scenario text, and the intro cinematic.

---

## 8. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Mod does not load | PAK is outside `~mods` or has wrong suffix | Install at `Frostpunk2/Content/Paks/~mods/` with its original `_P.pak` name. |
| Some text stays English | Only one English locale resource was edited | Update/test both `en` and `en-US-POSIX` LocRes files. |
| Intro remains English | SRT not installed separately | Back up and replace `Content/Movies/intro_en.srt`. |
| Thai boxes or wrong font | FontFace payload/path mismatch | Restore the exact `.ufont` asset path and validate OTF cmap. |
| UI clipping or mark collision | One bold Thai face replaced multiple original weights/styles | Provide weight-appropriate Thai faces and test every UI class. |
| Crash after update | PAK/asset version mismatch | Re-extract the updated base assets, rebuild the PAK, and retest. |

---

## 9. Required Tools

| Tool | Purpose | Source |
|---|---|---|
| repak | Inspect, list, unpack, and repack UE PAK v3 | https://github.com/trumank/repak |
| FModel / UnrealLocres | Inspect/correctly serialize UE LocRes and assets | Trusted UE modding distribution |
| fontTools | Validate OTF tables and Thai cmap coverage | https://fonttools.readthedocs.io/ |
| Subtitle editor or UTF-8 text editor | Preserve SRT timing while translating | Any standards-compliant editor |

---

## 10. Extracted Assets

| Asset | Result |
|---|---|
| `Assets/Fonts/Barlow-Regular.otf` | Raw OTF extracted from `.ufont`; Windows family CS PraJad Bold; 33,104 B; 87 Thai cmap points. |
| `Assets/Fonts/BarlowCondensed-Regular.otf` | Raw OTF extracted and verified as CS PraJad Bold; 33,104 B. |
| `Assets/Fonts/CrimsonPro-Regular.otf` | Raw OTF extracted and verified as CS PraJad Bold; 33,104 B. |
| `Assets/Extracted/.../Game.locres` | Both English LocRes variants extracted for format analysis. |

The font payloads are technically extractable; check the original CS PraJad licence before redistributing a repackaged mod.
