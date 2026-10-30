# Tempest Rising — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer) · verified 2026-07-19

---

## 1. Overview

This is a Thai localization mod for **Tempest Rising 1.9.x**, credited by its README to Lung Dear. It uses a UE5 **hybrid IoStore patch** design: a UI/font container and a separate campaign dialogue/cinematic container are placed in `Tempest/Content/Paks/`; both require their same-basename PAK companions to mount.

The mod overrides immediately on launch—there is no locale setting or UE4SS injection. Its author documents coverage of UI, units, buildings, doctrines, codex, and GDF/Dynasty/Veti campaign content.

---

## 2. Technical Stack

| Item | Detail |
|---|---|
| **Game Engine** | Unreal Engine 5 (README and verified IoStore v6 containers) |
| **Developer** | Slipgate Ironworks / 3D Realms (not independently verified from package) |
| **Project Codename** | `Tempest` (mount/project paths) |
| **Archive Format** | UE5 IoStore: two `.utoc`/`.ucas` pairs with PAK v11 companions |
| **AES Encryption** | **No AES encryption**: both PAK indexes report false/all-zero GUID; UTOC key-guid area is zero. |
| **Compression** | PAK companions: None. UTOC has zero named compression methods; precise IoStore block codec not asserted without block decoding. |
| **Font System** | UE FontFace assets with inline raw TTF in the UI IoStore container |
| **Thai Font Used** | IBM Plex Sans Thai Regular, SemiBold, Bold (TTF; SIL Open Font License 1.1 metadata) |
| **Text System** | UE binary localization/string assets inside IoStore; campaign resource paths are visible in UCAS |
| **Text Encoding** | UTF-16 LE Thai payload evidence: 119,900 Thai code units in UI container; 202,510 in campaign container, sampled on even byte offsets. |
| **Mod Complexity** | ★★★★☆ — two coordinated IoStore containers, binary text, and embedded FontFace assets. |

---

## 3. โครงสร้างไฟล์ (File Architecture)

```text
Tempest/Content/Paks/
├── Tempest-Windows_Thai_P.pak                 347 B  PAK v11 companion, 0 entries
├── Tempest-Windows_Thai_P.ucas           1,155,024 B  UI/text/font IoStore data
├── Tempest-Windows_Thai_P.utoc               8,392 B  IoStore v6 TOC: 73 entries, 78 blocks
├── Tempest-Windows_ThaiCampaign_P.pak         347 B  PAK v11 companion, 0 entries
├── Tempest-Windows_ThaiCampaign_P.ucas  431,851,019 B  campaign dialogue/cinematic data
└── Tempest-Windows_ThaiCampaign_P.utoc      144,314 B  IoStore v6 TOC: 591 entries, 7,137 blocks
```

All six files are required. Both PAKs start with mount path `../../../` and carry UE PAK magic `E1 12 6F 5A` in their footers; repak confirms 0 entries, v11, no index encryption, and no compression. The UTOCs begin with IoStore magic `2D 3D 3D 2D` ×4, version 6, header size `0x90`, 12-byte compressed-block records, 64 KiB block size, one partition, and no named compression methods.

---

## 4. Font Analysis

Three valid raw TTFs were carved from the UI UCAS after validating each sfnt table directory (`cmap`, `head`, `maxp`, and `name` required; all table offsets in bounds). Windows font metadata verification returned:

| Font | UCAS offset | Size | SHA-256 |
|---|---:|---:|---|
| IBM Plex Sans Thai Bold | `0xCCE` | 117,388 B | `64451229916CFBFA8BB1BBDF3674B8BA96C00E04D3BC81D148B7BFB8330D8FD8` |
| IBM Plex Sans Thai Regular | `0x35783` | 116,728 B | `83E1DB8E8BAD06BB760981F1DD528F5F209D20DFADEBAC12B21BF2F12453C8C6` |
| IBM Plex Sans Thai SemiBold | `0x72DD6` | 117,344 B | `C0D88539AA6117A845A19EA4E83C2C0EFC56DC43EBE41935B54D316AD2D6C7D5` |

UCAS strings identify the source files as `IBMPlexSansThai-*.ttf`, UE assets such as `FontFace_IBMPlexThai_Bold`, and SIL OFL 1.1 license text. The font declares Thai/Latin script support. Pair each original UI weight with its equivalent Thai weight; mixing weights changes layout and can cause wrapping. Test stacked vowels/tone marks in every UMG/Slate size.

---

## 5. Text Analysis

The supplied files contain no loose CSV/JSON/LocRes. Text is cooked into IoStore payloads, with Thai UTF-16 LE evidence in both UCAS files. Campaign path strings identify mission dialogue namespaces including `/Game/Tempest/Maps/Campaign/GDF/.../MissionDialogue/` and Dynasty dialogue paths; the campaign container therefore holds narrative and cinematic material, while the small UI container carries common UI content and the FontFace assets.

An exact string count cannot be safely inferred from raw UTF-16 code units because the cooked resource format contains metadata and repeated tables. Use FModel or a UE5 IoStore-aware extractor against the matching game build, then parse the extracted localization/string assets before counting or editing entries.

---

## 6. Cross-Engine Comparison

The structure matches the UE5 companion-PAK pattern recorded for Avowed and Titan Quest II: a 347-byte, zero-entry PAK registers the mount while the `.utoc`/`.ucas` pair holds the real data. Tempest Rising differs by splitting UI/font and campaign content into two separate IoStore pairs, so installing only one gives partial localization.

Like Avowed, the font is stored as raw TTF embedded in UE FontFace data and is safely recoverable by table-directory validation. Unlike Titan Quest II’s native-font plus ICU approach, Tempest Rising explicitly supplies a complete Thai font-weight set.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด

### Font pipeline

1. Extract UI FontFace assets with an IoStore-aware UE5 tool.
2. Keep Regular/SemiBold/Bold mapping consistent; use licensed TTFs with Thai combining-mark support.
3. Create UE FontFace/Font assets with inline loading, cook them for the target build, and verify raw TTF signatures after cooking.
4. Build `Tempest-Windows_Thai_P.{pak,utoc,ucas}` together; retain its 347-byte companion PAK.

### Text pipeline

1. Extract the UI and campaign localization resources separately from the matching base-game build.
2. Preserve keys, namespaces, markup, format placeholders, and UTF-16 serialization when translating.
3. Re-cook UI/text into `Thai_P` and campaign dialogue/cinematics into `ThaiCampaign_P`.
4. Rebuild both IoStore triplets with exact names, deploy all six files, and test GDF, Dynasty, Veti, UI, and cinematics.

---

## 8. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| No Thai at all | Missing companion PAK or wrong folder | Deploy all six files to `Tempest/Content/Paks/`; do not rename them. |
| UI Thai but campaign English | Campaign triplet absent/mismatched | Install `Tempest-Windows_ThaiCampaign_P.*` as a matching set. |
| Campaign Thai but UI tofu | UI container/font assets absent | Install `Tempest-Windows_Thai_P.*` and verify FontFace references. |
| Floating marks collide | Wrong font weight/metrics or missing glyphs | Restore matching IBM Plex Thai weight and test stacked marks. |
| Crash after game update | Cooked assets/IoStore metadata no longer match | Re-extract from the new build and recook/repack; never reuse stale TOC data. |
| Garbled text | Raw binary edited as UTF-8 | Use a format-aware extractor and preserve UE serialization/encoding. |

---

## 9. Required Tools

| Tool | Purpose | Source |
|---|---|---|
| repak | Verify/list conventional companion PAKs | https://github.com/trumank/repak |
| FModel / UE5 IoStore extractor | Browse/extract cooked UCAS/UTOC content | Official project/community distribution matching UE build |
| Unreal Engine toolchain | Cook/repack matching IoStore assets | Epic Games Unreal Engine distribution |
| Python | Validate/carve TTF table directories and hashes | https://www.python.org/ |

---

## 10. Extracted Assets

| Asset | Result |
|---|---|
| `Assets/Fonts/IBMPlexSansThai-Regular.ttf` | Extracted and Shell-verified: IBM Plex Sans Thai; 116,728 B. |
| `Assets/Fonts/IBMPlexSansThai-SemiBold.ttf` | Extracted and Shell-verified: IBM Plex Sans Thai SmBld; 117,344 B. |
| `Assets/Fonts/IBMPlexSansThai-Bold.ttf` | Extracted and Shell-verified: IBM Plex Sans Thai Bold; 117,388 B. |

License evidence embedded in each font identifies SIL Open Font License 1.1; confirm redistribution terms in the original font package before distribution.
