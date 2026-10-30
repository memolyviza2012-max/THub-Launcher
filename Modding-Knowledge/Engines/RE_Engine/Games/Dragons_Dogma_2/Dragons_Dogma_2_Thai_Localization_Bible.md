# Dragon's Dogma 2 — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

## 1. Overview
This Thai localization is an RE Engine KPKA overlay. The standalone `translation_thai.pak` is deployed by Fluffy Mod Manager with `pakcopy_reengine` as `re_chunk_000.pak.patch_018.pak`. The archive was enumerated and extracted with REtool; this document distinguishes confirmed facts from workflow guidance.

## 2. Technical Stack
| Item | Confirmed detail |
|---|---|
| Engine | RE Engine |
| Archive | KPKA; magic `4B 50 4B 41` |
| Archive version | 1.4 (KPKA header) |
| Delivery | Fluffy Mod Manager `pakcopy_reengine` patch overlay |
| Resource compression | 783 Deflate-compressed entries; 2 uncompressed entries |
| Text container | RE Engine `GMSG` message resources, extension `.msg.22` |
| Font resource | `fot-prentice.oft.1`, proprietary `FBFO` binary, not TTF/OTF |
| Complexity | ★★★★☆ |

## 3. File Architecture
The standalone archive is `44,674,972 B`. Its KPKA header contains the 32-bit value `0x312` (786); do not assume that field is a one-to-one file count. REtool enumerates and extracts **785 files**, all with known paths:

| Resource family | Count |
|---|---:|
| `message/npc` | 361 |
| `message/questlog` | 94 |
| `message/quest` | 92 |
| `message/pawn` | 91 |
| `message/ui` | 86 |
| `message/cutscene` | 57 |
| Font | 1 |
| Metadata / preview | 3 |

Non-message files are `modinfo.ini`, `screenshot.jpg`, `natives/stm/gui/ui01/font/fot-prentice.oft.1`, and `__MANIFEST/MANIFEST.TXT`. The message paths are under `natives/stm/message/`.

## 4. Font Analysis
The supplied archive contains the actual font resource:

`natives/stm/gui/ui01/font/fot-prentice.oft.1` — 95,472 B, magic `46 42 46 4F` (`FBFO`).

It contains none of the standard raw-font signatures checked (`00 01 00 00`, `OTTO`, `ttcf`, `wOFF`, `wOF2`). Treat it as a compiled RE Engine font resource, not an installable font. The original extracted resource is preserved at `Assets/Fonts/fot-prentice.oft.1`; replacing it requires a compatible RE Engine font build pipeline, not a blind TTF rename.

## 5. Text Analysis
All **781** localization resources are `.msg.22` files. A sampled extracted file begins `16 00 00 00 47 4D 53 47 ...`; `47 4D 53 47` is `GMSG`. These are structured binary message containers, not plain-text files. Preserve message IDs, control tokens, offsets, encoding and path names; changing bytes in-place is unsafe.

Coverage is split by function: NPC dialogue, pawn dialogue, quests, quest logs, UI, and cutscenes. Translate/edit through an RE Engine GMSG-aware tool or a verified importer/exporter, then retain the original relative path and `.msg.22` version when rebuilding.

## 6. Cross-Engine Comparison
| Aspect | Dragon's Dogma 2 / RE Engine | Unity loose localization | Unreal PAK localization |
|---|---|---|---|
| Packaging | KPKA resource archive | Often loose assets / bundles | PAK / IoStore container |
| Text | Binary `GMSG` `.msg.22` | Commonly JSON/CSV or serialized assets | Locres / uasset data |
| Font | Compiled `FBFO` `.oft.1` resource | TTF or TMP asset is often accessible | FontFace / composite-font assets |
| Deployment | Patch filename and load order matter | Mod loader path mapping | Mount order and container metadata matter |

## 7. Rebuild & Deployment Pipeline
1. Back up the original PAK and extract it with REtool.
2. Edit only a copy of the required `.msg.22` resource through a format-aware workflow.
3. Preserve the full relative resource path, GMSG version and resource metadata.
4. Repack with a Dragon's Dogma 2-compatible REtool KPKA build command.
5. Deploy through Fluffy Mod Manager as `re_chunk_000.pak.patch_018.pak` (`pakcopy_reengine`).
6. Test UI, dialogue, quest logs, pawn lines and cutscenes separately; verify Thai glyph rendering and line wrapping.

## 8. Troubleshooting
| Symptom | Likely cause | Resolution |
|---|---|---|
| Mod is not loaded | Wrong patch filename or profile disabled | Verify Fluffy profile and `pakcopy_reengine` target name. |
| Game crashes on launch | Invalid KPKA/GMSG metadata | Restore backup and rebuild from the extracted path tree. |
| Text is missing or corrupt | Broken GMSG offsets/tokens | Re-export from a GMSG-aware tool; do not hex-edit text bytes. |
| Thai glyphs render as boxes | Incompatible/missing compiled font glyphs | Restore or rebuild the matching `fot-prentice.oft.1` resource. |
| UI overflows | Thai expansion or UI-specific layout issue | Test the affected `message/ui` file and shorten/reflow wording. |

## 9. Required Tools
| Tool | Purpose |
|---|---|
| REtool | List, extract and rebuild compatible RE Engine KPKA archives |
| GMSG-aware editor/importer | Safely edit message content without breaking structure |
| Fluffy Mod Manager | Deploy the PAK overlay using the configured patch name |
| Hex viewer / hash tool | Confirm magic bytes and verify outputs |

## 10. Extracted Assets
| Asset | Stored path | Notes |
|---|---|---|
| Standalone KPKA | `Assets/Raw/translation_thai.pak` | Verified source package; 44,674,972 B |
| Font resource | `Assets/Fonts/fot-prentice.oft.1` | Extracted compiled `FBFO` resource; 95,472 B |
| Font note | `Assets/Fonts/EXTRACTION_NOTE.txt` | Handling and provenance note |
| Earlier manager-package sample | `Assets/Raw/DD2_TH.pak` | Separate KPKA sample supplied in the Fluffy profile |

## 11. Compiled-Font Handling Note
`fot-prentice.oft.1` is a binary compiled font resource. Keep its filename and relative path exactly when testing replacement. Before attempting Thai glyph expansion, make a reversible copy of the PAK and validate the rebuilt resource in-game; no raw TTF/OTF has been recovered from this package.
