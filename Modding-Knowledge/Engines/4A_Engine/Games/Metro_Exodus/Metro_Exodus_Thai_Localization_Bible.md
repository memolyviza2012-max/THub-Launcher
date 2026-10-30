# Metro Exodus — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer) · verified 2026-07-19

---

## 1. Overview

This is a Thai localization mod for **Metro Exodus Enhanced Edition 2.0.0.1** (Steam), credited by its README to **Lung Dear**. Metro Exodus uses 4A Games’ proprietary **4A Engine** and the mod follows a **file-replacement / VFS-patch** architecture: it replaces the game's `content.vfx` master index and adds `patch_th.vfs0` beside it.

The evidence is the supplied installer itself: it backs up `content.vfx` as `content.vfx.orig_bak`, copies the modded index in its place, then copies `patch_th.vfs0`; removal restores the index and deletes the patch archive. This is not an Unreal or Unity package.

---

## 2. Technical Stack

| Item | Detail |
|---|---|
| **Game Engine** | 4A Engine (proprietary; Metro Exodus Enhanced Edition) |
| **Developer** | 4A Games |
| **Project Codename** | Not discovered in supplied mod files |
| **Archive Format** | 4A virtual-file-system index: `.vfx`; 4A patch data archive: `.vfs0` |
| **AES Encryption** | N/A — not an Unreal Engine archive |
| **Compression** | Custom/undetermined at container level. `78 9C`/`78 DA` byte sequences occur, but no candidate completed a zlib stream validation; do not label the archive zlib-compressed on signature alone. |
| **Font System** | Bitmap-font resources and texture atlases addressed through VFS paths; no raw vector font shipped |
| **Thai Font Used** | Family/weight not recoverable from this package; 101 unique `font\\...` / `ui\\ui_font...` resource paths were indexed |
| **Text System** | Custom serialized localization resources within `patch_th.vfs0`; no standalone CSV/JSON/LOCRES/LNG file is exposed |
| **Text Encoding** | Not safely identifiable at whole-file level. Raw-file decoding creates false positives because this is binary; extract individual text resources first. |
| **Mod Complexity** | ★★★★☆ — proprietary VFS index/data coupling, opaque serialized text, and bitmap-font metrics require a format-aware extractor/repacker. |

SHA-256: `content.vfx` = `54a19d8f0285666287b59daa9d2ecec7e34e71171ac8bc0860a839af2d59a708`; `patch_th.vfs0` = `4d872a8444c3b218490386091f5d090d2be4814a9f75ab4db4579ffa4b395540`.

---

## 3. โครงสร้างไฟล์ (File Architecture)

```text
Metro Exodus/                                      26,609,176 bytes supplied
├── content.vfx                             14,004,865 B  replacement VFS index
│   ├── offset 0x000000: 03 00 00 00 01 00 00 00 …
│   └── ASCII archive references: content_ui_textures.vfs0 … content_52.vfs0,
│       then patch_th.vfs0 (the mount/index connection)
├── patch_th.vfs0                            12,593,426 B  Thai patch VFS data
│   ├── offset 0x000000: 00 00 00 00 EE C4 C1 00 00 00 00 00 04 00 00 00 …
│   ├── 101 unique named bitmap-font/UI-font resources
│   ├── 32,012 `voices\\...` path records (resource namespace evidence, not text count)
│   └── offset 0xBFE866: `DDS `, valid 128×128 DX10 DDS payload
├── INSTALL.bat                                3,037 B  backs up/replaces index; copies patch
├── UNINSTALL.bat                              2,465 B  restores index; deletes patch
└── README.txt                                 5,383 B  Thai mod instructions and compatibility
```

Magic-byte observations were taken from every binary file in the delivered folder, not inferred from extensions. `content.vfx` contains `patch_th.vfs0` as an ASCII archive-name reference; that is the direct linkage allowing the replacement index to make the patch available to the game. `patch_th.vfs0` has no `UnityFS`, UE PAK footer signature, or valid embedded TTF/OTF table directory.

---

## 4. Font Analysis

The patch exposes named resources such as `font\\font_console`, `font\\font_metro_for_menu_pt`, `font\\font_metro_for_map_pt`, `font\\font_font_regular_pt`, `font\\font_symbol`, and `ui\\ui_font_hud_01`. Locale-suffixed variants (`_us`, `_ru`, `_jp`, `_cn`, `_tw`, etc.) establish that fonts are selected as engine resources rather than loaded as an installable Windows font.

The mod README explicitly says it includes a Thai font and adjusts Thai vowel/tone positioning. However, a complete raw scan found no valid font file: every apparent `00 01 00 00`/`OTTO` candidate failed the OpenType table-directory bounds test. Therefore no real family, weight, designer, licence, or glyph coverage can be responsibly asserted. The observed system is a **bitmap/SDF-like atlas + proprietary metrics/resource data**, not a `.ttf`/`.otf` swap.

One embedded image was carved after validation: `Assets/Textures/embedded_texture_128x128_dx10.dds` starts at `0xBFE866`, has `DDS ` magic, a 124-byte DDS header, 128×128 dimensions, one mip, `DX10` pixel-format marker, and 16,384 bytes of image payload (16,532 bytes including headers). Its internal resource name cannot be established without a VFS extractor, so it is intentionally not claimed to be a font atlas.

Thai rendering consequence: do not overwrite arbitrary atlas cells. Thai base letters, combining vowels, and tone marks require matching glyph mapping and advance/bearing/vertical-offset metrics. A visually correct atlas with stale metric records will produce boxes, clipping, or mispositioned marks.

---

## 5. Text Analysis

No plaintext translation table is present as a separate file. The archive contains binary data and resource names including `$lang_text`, `$lang_sound`, `$lang_sound_downloaded`, `$localizable_signs`, and many dialogue/voice namespaces such as `voices\\universal_m3\\factions\\...`. The README states that the translation covers dialogue, subtitles, diary, menus, and weapon descriptions; this is author documentation, not a string count.

Whole-container UTF-8/UTF-16/Windows-874 decoding is invalid evidence because binary payload bytes can resemble Thai code units. The safe workflow is: use a 4A-capable VFS extractor to recover each text resource, identify its per-resource header/encoding, preserve IDs and control tokens, then count decoded entries. Until then, string count, individual text-file offsets, and exact encoding remain **undetermined**, rather than guessed.

---

## 6. Cross-Engine Comparison

The existing Metro 2033 and Metro Last Light Bibles in the 4A Engine knowledge base describe the same broad pattern: a modified `.vfx` index selects a companion `.vfs0` archive carrying replacement localization/font assets. Metro Exodus confirms this pattern with stronger package-level evidence—its actual installer replaces `content.vfx` and adds `patch_th.vfs0`, while the index contains that exact archive name.

Unlike an Unreal `.locres` workflow or Unity StringTable bundle, there is no engine-generic text editor path here: index references, payload offsets, resource metadata, and repacking must stay mutually consistent. As with the other Metro titles, font work is texture/metric work rather than a raw TTF swap; the safe transferable technique is VFS override, not blind binary replacement.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด

### Font pipeline

1. Back up the original game `content.vfx`; never use the modded one as the only source.
2. Extract the original and patch VFS with a 4A-aware extractor that preserves paths, offsets, and metadata.
3. Identify the font resource set actually selected by the locale/UI screens being changed. Export its bitmap atlas and its paired engine metric/resource records together.
4. Render Thai glyphs into unused/extended atlas space, preserving texture format and dimensions. Update glyph-to-codepoint mapping, UVs, advance, bearings, line height, and Thai combining-mark offsets in the paired data.
5. Rebuild `patch_th.vfs0` with the extractor/repacker; update or regenerate `content.vfx` so the exact patch filename and offsets are registered.
6. Test menus, subtitles, map, diary, HUD, and credits separately. Each can use a different font resource.

### Text pipeline

1. Extract the individual text resources from the original archive and decode only after identifying their resource header.
2. Export a reversible table containing stable key/ID, original text, translation, and control tokens. Do not translate or remove placeholders, markup, voice IDs, or line-break commands.
3. Encode and serialize using the exact original resource format; do not paste UTF-8 into an opaque binary payload.
4. Pack replacements into a new patch VFS and register that VFS from the copied/modded `content.vfx`.
5. Install by backing up `content.vfx`, replacing it, and copying the patch archive to the folder containing `MetroExodus.exe`; test on the stated 2.0.0.1 target before release.

---

## 8. Troubleshooting

| Symptom | Likely cause | Corrective action |
|---|---|---|
| Thai shows boxes or no text | The index does not register the patch, or glyph mappings are absent | Verify `patch_th.vfs0` is beside the executable and referenced by the deployed `content.vfx`; rebuild font mapping and atlas as a pair. |
| Floating vowels/tone marks misalign | Atlas pixels changed without per-glyph bearings/vertical metrics | Adjust combining-mark metrics in the paired font resource; test stacked marks, not only base glyphs. |
| Crash at launch | Index/archive mismatch, changed offsets, wrong target build, or malformed repack | Restore the backed-up `content.vfx`, remove patch, confirm base game launches, then repack with a format-aware tool for the same game build. |
| Garbled Thai | Text resource was encoded/serialized incorrectly | Re-extract and identify per-resource encoding; preserve original control bytes and write through the correct serializer. |
| Font looks right in menus but wrong in HUD/credits | Different `font\\...` resource is selected | Map the failing screen to its resource and patch that atlas/metrics set too. |
| Mod stops working after Steam update | `content.vfx`/payload layout changed | Rebase on the updated originals; do not reuse old offsets or an old index blindly. |

---

## 9. Required Tools

| Tool | Purpose | Source |
|---|---|---|
| 4A Engine VFS extractor/repacker (format-aware) | Extract and rebuild `.vfx`/`.vfs0` while preserving metadata | Obtain from a trusted Metro/4A modding community; validate on copies first |
| Hex viewer | Verify magic bytes, offsets, and headers | Any read-only hex viewer |
| Python 3 | Validate font signatures, carve known embedded payloads, automate atlas/mapping work | https://www.python.org/ |
| Pillow | Render a source Thai TTF into an atlas for automation | https://pillow.readthedocs.io/ |
| DDS-capable library/tool | Inspect/export DDS payloads without changing format | DirectXTex or equivalent |
| Exodus SDK (where compatible) | Reference/build tooling for authorised Metro Exodus content workflows | Steam Tools / official SDK distribution |

The UE `repak` tools in the common tool directory are deliberately not used: this archive is 4A VFS, not UE PAK.

---

## 10. Extracted Assets

| Asset | Result | Metadata |
|---|---|---|
| `Assets/Textures/embedded_texture_128x128_dx10.dds` | Successfully carved | Source `patch_th.vfs0` offset `0xBFE866`; DDS DX10; 128×128; 16,532 B; SHA-256 `5880144a0834b09d92dd729494a27aa5b4df9c34e79e4b5c62e08e0169d8ab17` |
| `Assets/Fonts/EXTRACTION_NOTE.txt` | Font extraction documented | No valid installable TTF/OTF. Named bitmap-font resources exist; DDS/vector conversion is technically invalid because vector outlines and font tables are absent. |

The required Shell font-name verification is **not applicable**: no `.ttf`/`.otf` passed validation, so there is no installable font file to query.

---

## 11. M2M Protocol (Bitmap Font)

The following is a template for an automated rebuild after a format-aware extractor has supplied a bitmap atlas and a documented glyph-metric table. It does **not** guess the proprietary `.vfs0` file layout; the `pack_metric_record` structure must be set from an extracted reference record.

```python
# render_thai_atlas.py — render selected Thai code points into a known atlas grid
from PIL import Image, ImageDraw, ImageFont

font = ImageFont.truetype('SourceThai.ttf', 48)
atlas = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
draw = ImageDraw.Draw(atlas)
mapping = {}
for index, cp in enumerate(range(0x0E01, 0x0E5C)):
    x, y = (index % 16) * 64, (index // 16) * 64
    draw.text((x, y), chr(cp), font=font, fill='white', anchor='lt')
    mapping[cp] = (x, y, 64, 64)
atlas.save('thai_atlas.png')  # convert to the original DDS format before packing
```

```python
# shape_thai.py — retain code points; only map to PUA if the target font format requires it
import re
TOP_MARKS = re.compile(r'([\u0E01-\u0E2E])([\u0E34-\u0E37\u0E47-\u0E4E]+)')
def encode_for_target(text, pua_map):
    # The map must be derived from the extracted font records, never invented.
    return TOP_MARKS.sub(lambda m: pua_map.get(m.group(0), m.group(0)), text)
```

```python
# inject_metrics.py — example only; establish offsets/endianness from a real extracted record
import struct
def pack_metric_record(codepoint, x, y, width, height, advance, bearing_y):
    # Placeholder schema: <I H H H H h h. Do not use until validated against 4A data.
    return struct.pack('<IHHHHhh', codepoint, x, y, width, height, advance, bearing_y)
```

Automated acceptance gate: parse the rebuilt metric table, verify every code point has in-bounds UVs, rebuild VFS/index with the same toolchain that extracted them, and smoke-test the target game build. Never inject these bytes directly into a `.vfs0` without a validated container map.
