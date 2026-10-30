# Digimon Story: Time Stranger — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer) · verified 2026-07-20

---

## 1. Overview

This Thai-mod payload for **Digimon Story: Time Stranger** consists of two DirectX 11 Media.Vision archive files, `app_text01.dx11.mvgl` and `patch_text01.dx11.mvgl`, both beginning with `MDB1`. It is a file-replacement / patch-override architecture: the larger file carries shared resources while the smaller patch has direct Thai text evidence.

The previous Bible incorrectly described Cyber Sleuth/Hacker's Memory. That claim is removed: these files are documented only as the supplied Time Stranger mod.

---

## 2. Technical Stack

| Item | Detail |
|---|---|
| **Game Engine** | Media.Vision proprietary engine (inferred from MVGL format; version not exposed) |
| **Developer** | Not established from supplied files |
| **Archive Format** | `.mvgl`, `MDB1` magic at offset `0x0` |
| **AES Encryption** | N/A — not UE |
| **Compression** | Undetermined; signatures alone did not validate a stream |
| **Font System** | Indexed `bin font\\commonfont` resource with non-portable OTF data |
| **Thai Font Used** | Undetermined; no valid installable TTF/OTF was recovered |
| **Text System** | Indexed `mbe text\\...` and `mbe message\\...` binary resources |
| **Text Encoding** | Per-resource undetermined; patch has 8,602 Thai UTF-8 triples and 11,349 Thai UTF-16 LE code units at even offsets |
| **Mod Complexity** | ★★★★☆ — proprietary MDB1 records and non-contiguous font data |

SHA-256: `app_text01.dx11.mvgl` = `89d8f23a0045753f32c943493300758ab44a62653357a53bb959b3220790fbb7`; `patch_text01.dx11.mvgl` = `4a6ba1fa8954d59316256b77623a7a6fe6261e649c22615e3fd3d3e9c13f6154`.

---

## 3. โครงสร้างไฟล์ (File Architecture)

```text
Digimon Story Time Stranger/
├── app_text01.dx11.mvgl      9,272,774 B  MDB1; header count 255; region offset 0xA760
│   └── paths: bin font\commonfont, mbe text\..., mbe message\...
└── patch_text01.dx11.mvgl    1,931,530 B  MDB1; header count 223; region offset 0x9260
    └── more than 200 visible MBE text/message identifiers plus Thai byte evidence
```

The first eight little-endian fields are `MDB1,255,255,254,42848,0,9272774,0` and `MDB1,223,223,222,37472,0,1931530,0`. This proves indexed records but not an exact tree schema; no unverified format description is asserted.

---

## 4. Font Analysis

`app_text01` indexes `bin font\\commonfont` at visible string offset `0x1090`. It has `OTTO` byte markers at `0xA762` and `0x544D48`, but neither passes an OpenType table-directory bounds test as a contiguous font.

The prior `commonfont.otf` carve (6,601,936 B) starts with `OTTO` but fontTools reports malformed name-table offsets and Windows returns no family name. It is forensic evidence, not an installable font. A MVGL-aware extractor must reconstruct record/relocation data before family, foundry, licence, or Thai coverage can be stated.

Do not replace bytes at an `OTTO` marker: the resource is non-contiguous or relocated, and raw carving corrupts table layout.

---

## 5. Text Analysis

Visible resource identifiers include `mbe text\\battle_info_message`, `mbe message\\battle`, mission-style `mbe message\\s010_001`, and many `mbe message\\m...` records. The patch has Thai byte evidence, making it the strongest candidate for translated message/table payloads.

MBE's row schema and exact encoding are not yet decoded. Treat it as opaque binary until a compatible parser extracts it; preserve record names, IDs, token/control bytes, lengths, and relocation metadata.

---

## 6. Cross-Engine Comparison

Unlike UE PAK/LocRes titles such as Borderlands 3, this MDB1 archive does not expose independently valid font payloads. Unlike Unity/BepInEx mods such as Rune Factory 5, text and TTF are not loose editable files. The transferable rule is to validate extracted assets before naming their format/family or editing them.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด

### Font pipeline

1. Use an MVGL/MDB1-aware extractor/repacker; never raw-carve `OTTO`.
2. Extract `bin font\\commonfont` with all associated record/relocation data.
3. Validate the reconstruction with fontTools and Windows metadata.
4. Replace only with a licensed Thai-capable font, preserving metrics and shaping tables.
5. Repack with the MDB1 tool and verify header/index invariants before game testing.

### Text pipeline

1. Extract each `mbe text\\...` / `mbe message\\...` record with a format-aware tool.
2. Establish per-record encoding/layout from an original/translated pair.
3. Preserve IDs, controls, tokens, and lengths; translate only payload fields.
4. Repack under the original `patch_text01.dx11.mvgl` name and test dialogue, battle, menus, and missions.

---

## 8. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Game fails after replacement | MDB1 offsets invalid | Restore originals; rebuild only with an MVGL-aware repacker. |
| Thai garbles/question marks | Wrong encoding or length metadata | Extract a known-good record pair and preserve all controls. |
| Font will not install | OTF raw carve is malformed/non-contiguous | Use a proper extractor; do not install the carve. |
| Text remains original | Wrong patch/archive placement | Verify target build paths and patch override behavior. |
| Some dialogue untranslated | Some MBE records omitted | Inventory every relevant `mbe message\\...` resource before packing. |

---

## 9. Required Tools

| Tool | Purpose | Source |
|---|---|---|
| MVGL/MDB1-aware extractor/repacker | Decode/rebuild records while preserving offsets | Required; trusted Media.Vision-compatible tool |
| Hex viewer | Verify magic bytes/offsets read-only | Any read-only hex viewer |
| fontTools | Validate reconstructed fonts | https://fonttools.readthedocs.io/ |
| Python | Hash/signature/text validation | https://www.python.org/ |

---

## 10. Extracted Assets

| Asset | Result |
|---|---|
| `Assets/Fonts/commonfont.otf` | **Not a valid installable font**; retained as forensic evidence only. |
| `Assets/Fonts/EXTRACTION_NOTE.txt` | Documents failed extraction and the required format-aware next step. |
| `Assets/Configs/MVGL_Content_Listing.txt` | Resource-name discovery aid; not a decoded schema. |

No installable font was produced; Shell font-family verification is not applicable.
