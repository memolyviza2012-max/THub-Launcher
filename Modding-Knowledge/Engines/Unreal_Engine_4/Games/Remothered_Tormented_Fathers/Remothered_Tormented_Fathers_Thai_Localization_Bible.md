# Remothered: Tormented Fathers — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview

Remothered: Tormented Fathers (Stormind Games) uses an **Unreal Engine 4-era** content layout.  The inspected Thai mod is a conventional **patch-PAK overlay**: `RTF-Thai-by-Artdekdok_P.pak` is mounted over the base game and replaces six assets at their original virtual paths.

It is unusually useful as a reference mod because its complete pre-pack tree is supplied beside the PAK.  The archive inventory and SHA-256 hashes prove that the six source files are exactly the six files packed into the release; no hidden DLL, runtime injector, image asset, or companion encryption key was found.

---

## 2. Technical Stack

| Item | Verified detail |
|---|---|
| **Game Engine** | Unreal Engine 4 era; UE PAK **v3** (`CompressionEncryption` generation) |
| **Developer** | Stormind Games |
| **Project Codename** | Not identified from the supplied mod |
| **Mod architecture** | Patch/overlay PAK (`_P.pak`), file replacement at original UE virtual paths |
| **Archive format** | UE PAK v3; footer magic `E1 12 6F 5A`; 6 entries; mount point `../../../` |
| **PAK footer** | magic at file offset `0xF205D`; version `3`; index offset `0xF20C5` (991,429); index size `0x598` (1,432) |
| **AES encryption** | **No AES encryption.** `repak info` reports `encrypted index: false`, no encryption GUID, and the archive lists/extracts without a key. |
| **Compression** | **Zlib** (reported by `repak`); PAK size 992,905 B versus 2,609,690 B of source payload, consistent with compressed storage. |
| **Font system** | Raw TrueType replacement at UE Slate fallback path, not a `.ufont` wrapper |
| **Thai font used** | `CS ChatThaiUI`, Regular; internal foundry `BoonUni`, designer `Chanok Samiti` |
| **Text system** | UE `LocRes` plus four serialized UE DataTable-like `.uasset` localization assets |
| **Text encoding** | UTF-16LE `FString` payloads; no UTF-8 Thai sequences found in any inspected localization asset |
| **Mod complexity** | ★★★☆☆ — PAK is unlocked and font is raw TTF, but changing the four serialized DataTables requires version-compatible UE asset tooling. |

> Use `repak info` and `repak hash-list` rather than PAK size alone to validate a rebuild.  The authoritative observed facts are the compression method, six paths, and hashes in §3.

---

## 3. File Architecture

### 3.1 Release layout and binary signatures

```text
RTF-Thai-by-Artdekdok_P.pak                                   992,905 B
├─ Engine/Content/Slate/Fonts/DroidSansFallback.ttf            76,284 B  raw TTF
├─ Remothered/Content/Localization/Game/en/Game.locres        250,640 B  UE LocRes
├─ Remothered/Content/LocalizationSystem/
│  ├─ DATA_LocalizationCinematic.uasset                        905,638 B  UE package
│  ├─ DATA_LocalizationContent.uasset                          844,768 B  UE package
│  ├─ DATA_LocalizationGUI.uasset                              274,096 B  UE package
│  └─ DATA_LocalizationGame.uasset                             258,264 B  UE package
└─ supplied unpacked tree mirrors these exact six paths
```

| File type | Magic / position | Interpretation |
|---|---|---|
| PAK | footer `E1 12 6F 5A 03 00 00 00` at `0xF205D` | UE PAK v3, not guessed from extension |
| TTF | `00 01 00 00 00 12 01 00` at offset `0x00` | valid sfnt TrueType; 18 tables |
| LocRes | `BE 00 00 00 FF FF FF FF` at offset `0x00` | UE localization binary, not a text file |
| each `.uasset` | `C1 83 2A 9E F9 FF FF FF` at offset `0x00` | UE package tag `0x9E2A83C1`, little-endian |

### 3.2 Integrity inventory

`repak hash-list` produced the following SHA-256 digests, identical to the corresponding supplied unpacked files:

| Packed path | SHA-256 |
|---|---|
| `Engine/Content/Slate/Fonts/DroidSansFallback.ttf` | `31AFC16CDFBA6A3A097824C9FBB681BAA18FF0DD4A403B0C47A4448C38277A6A` |
| `Remothered/.../Game/en/Game.locres` | `BA5FFBB2AEB9B3307D5C162339D4BF701ACF54C92F91863D4D98E6499D32049D` |
| `DATA_LocalizationCinematic.uasset` | `59A8D207E375703745C882E002591E15E91170763315D56B02D251A2A90B9B67` |
| `DATA_LocalizationContent.uasset` | `80DB844009387036227C2055143DF3C7347F3AF626A2D02AEDCFC77C8129A2C4` |
| `DATA_LocalizationGUI.uasset` | `807E8C7270EAF2A50B1FC1508BDB5DB8CDC0CEB0D936544AC02FD1C31518C85A` |
| `DATA_LocalizationGame.uasset` | `483D8558B39CF1BE1C0903C5A52BD4C154A17798A506C4EA5C2B332AD3302E04` |

The PAK itself has SHA-256 `4F9920CD51E67851D6962E8C97E0A00A71E96CD8E6DFEDAABCEEA6740416E8B5`.

---

## 4. Font Analysis

The mod replaces the engine-wide Slate fallback filename, `Engine/Content/Slate/Fonts/DroidSansFallback.ttf`, with a genuine raw TTF.  It does **not** merely rename a bitmap atlas or embed a font inside an opaque `.ufont`; the file starts with the sfnt magic and was parsed successfully by both Windows font APIs and `fontTools`.

| Property | Verified value |
|---|---|
| Delivered filename / original target | `DroidSansFallback.ttf` |
| Internal family / style | `CS ChatThaiUI` / Regular |
| Internal version | `Version v1` |
| Foundry / designer fields | `BoonUni` / `Chanok Samiti` |
| Format / size | TTF, 76,284 B, SHA-256 `31AFC…77A6A` |
| Metrics | 2,560 units/em; 201 glyphs |
| Thai coverage | 87 mapped code points in U+0E00–U+0E7F; tested present: consonants, `ะ`, `ั`, upper vowels, tone mark `่`, `์`, Thai digits, and `๛` |
| License | **Not embedded/verified in the file.** Treat redistribution as unlicensed until confirmed with the font rightsholder; do not infer an open-source license from its presence in this mod. |

**Swap mapping:** UE resolves the original `DroidSansFallback.ttf` path to `CS ChatThaiUI`.  Keeping the original path is essential: changing only the filename makes the game continue loading its original fallback.  The supplied font includes common Thai combining marks, but final visual QA is still required for stacked sequences such as `กิ่`, `ปี้`, and punctuation at the game’s smallest UI scale.  Glyph presence does not prove UE4’s kerning, baseline, or clipping settings are correct in every widget.

The installable verified asset is at `Assets/Fonts/CS_ChatThaiUI-Regular.ttf`.

---

## 5. Text Analysis

This mod has two text channels rather than one:

1. `Game.locres` (250,640 B) is the standard UE binary localization resource at the English culture path `Game/en`.  It contains namespace/key-to-localized-string data and wide Thai `FString` content.  A byte scan found **439** Thai UTF-16LE code units and **zero** UTF-8 Thai triplets in the first and full inspected payload.  It must be edited with a LocRes-aware tool, never a generic text editor.
2. Four UE package files under `LocalizationSystem` carry dialogue/content/UI localization in serialized DataTable-like assets.  Their package tags confirm they are UE assets, not JSON/CSV.  Wide-string scanning found Thai runs in all four: Cinematic ~580, Content ~125, Game ~161, GUI ~173.  These are reconnaissance counts of distinct readable runs, **not** a guaranteed row count, because UE package names/exports are binary structures.

| Asset | Role indicated by name | Size | Thai UTF-16LE code units | Safe edit method |
|---|---:|---:|---:|---|
| `DATA_LocalizationCinematic.uasset` | cutscenes/dialogue | 905,638 B | 10,052 | compatible UE asset/DataTable workflow |
| `DATA_LocalizationContent.uasset` | documents/world content | 844,768 B | 14,205 | compatible UE asset/DataTable workflow |
| `DATA_LocalizationGame.uasset` | gameplay/prompts | 258,264 B | 2,422 | compatible UE asset/DataTable workflow |
| `DATA_LocalizationGUI.uasset` | menus/settings | 274,096 B | 2,754 | compatible UE asset/DataTable workflow |
| `Game.locres` | standard localized resources | 250,640 B | 439 | LocRes editor/export-import workflow |

**Encoding rule:** UE wide strings use little-endian code units (`ก` = `01 0E`).  Preserve the `FString` length fields and use UTF-16LE; inserting UTF-8 bytes, changing values in-place without updating serialized lengths, or changing table names will corrupt the package.

---

## 6. Cross-Engine Comparison

The knowledge-base Bible for **Ghostrunner** (Unreal Engine 4) demonstrates the same broad recipe: a `_P.pak` override, UE PAK v3 footer, Zlib, and a `LocRes` language resource.  Remothered differs in three practical ways:

| Topic | Ghostrunner reference | Remothered result |
|---|---|---|
| Font storage | `.ufont` wrapper(s), requiring a search/carve for raw sfnt data | direct raw TTF at a Slate fallback path; copy/verify is sufficient |
| Localization breadth | principally a LocRes replacement | LocRes **plus four** serialized localization `.uasset` files |
| Signing/encryption | its documented distribution includes a `.sig` companion | no `.sig` in the supplied mod and no AES-encrypted index |

Therefore, reuse the unlocked UE4 PAK/LocRes techniques from Ghostrunner, but do not assume that a successful `Game.locres` edit covers Remothered’s cinematics, documents, gameplay prompts, or GUI.  Those channels are separately replaced by the four package assets.

---

## 7. Pipeline — Building or Updating the Mod

### Font pipeline

1. Work in a staging directory whose top-level folders are exactly `Engine` and `Remothered`; retain every directory name and case from §3.
2. Replace `Engine/Content/Slate/Fonts/DroidSansFallback.ttf` with a licensed TTF that includes Thai base characters and combining marks.  Verify the candidate starts `00 01 00 00` or `OTTO`, inspect its family name, and check U+0E00–U+0E7F coverage before packing.
3. Preserve the target filename `DroidSansFallback.ttf`.  This filename/path is the established lookup hook; using a correctly named internal font family alone is insufficient.
4. Test dialogue, menu, documents, Thai digits, and stacked vowels/tone marks in game.  If clipping appears, solve the UE font/widget metrics in the original asset pipeline rather than padding text with spaces.

### Text pipeline

1. Make a full copy of all five localization files before editing.  Export `Game.locres` with a UE-compatible LocRes tool, translate values while preserving namespace/key/source identity, then import/compile back as UTF-16LE LocRes.
2. Open each `DATA_Localization*.uasset` only with a tool or UE editor build compatible with this game’s UE package version.  Export the DataTable rows when supported; preserve row names, property types, table schema, and `FString` serialization on reimport.
3. Do **not** use search/replace or a hex editor to change variable-length strings in `.uasset`; the change moves later offsets and invalidates UE export data.
4. Pack the staging root as an unencrypted UE PAK with `repak` or the matching UnrealPak version.  Its mount point must resolve to `../../../` and the archive must contain exactly the intended relative paths (not an extra `staging/` folder).
5. Name the final archive with the patch suffix, e.g. `RTF-Thai-by-Author_P.pak`, place it beside the game’s PAKs according to the user’s installation method, and load-test.
6. Validate before release: `repak info output.pak` must say version/format readable and `encrypted index: false`; `repak list output.pak` must show the six expected paths; compare `hash-list` for assets intentionally unchanged.

---

## 8. Troubleshooting

| Symptom | Likely cause | Corrective action |
|---|---|---|
| Thai displays as squares or English fallback | wrong virtual path, filename changed, or font lacks Thai glyphs | restore `Engine/Content/Slate/Fonts/DroidSansFallback.ttf`; verify `CS ChatThaiUI` coverage and package list |
| Tone marks / upper vowels overlap or are clipped | combining-mark positioning or Slate widget ascent/clip rectangle | test `กิ่`, `ปี้`, `น้ำ`, Thai digits in each UI; adjust the source font/widget asset rather than add spaces |
| Main menus translated but cutscenes/documents remain English | only `Game.locres` was replaced | rebuild and include the appropriate `DATA_LocalizationCinematic` / `Content` package assets |
| Crash or PAK ignored | wrong mount path, incompatible UE package serialization, malformed PAK, or missing `_P` suffix | list the PAK, remove extra top-level folder, use matching UE asset tooling, and restore suffix |
| Garbled Thai | UTF-8 was written into UE `FString` / LocRes or lengths were damaged | re-export/reimport through a LocRes/DataTable-aware tool; use UTF-16LE and preserve binary structure |
| Rebuilt PAK requires a key | encryption was enabled accidentally | recreate with no AES key/encryption; the original’s index is explicitly unencrypted |

---

## 9. Required Tools

| Tool | Purpose | Source / use |
|---|---|---|
| `repak_cli` | inspect, list, hash, unpack and repack unlocked UE PAKs | local `E:/Mod_Workspace/Tool/repak_cli/repak.exe` |
| UnrealPak (matching UE generation) | alternate official PAK packer | local `E:/Mod_Workspace/Tool/RePak/RePak.exe`; match game version when possible |
| UE LocRes editor / UnrealLocres | export/edit/import `Game.locres` safely | use a version compatible with UE4 LocRes |
| UAssetGUI or compatible UE editor | inspect/export/reimport the four serialized localization DataTables | select a UE package version compatible with the game |
| `fontTools` / Windows Font API | validate TTF names, tables and Thai cmap coverage | used for the verified font findings in §4 |
| Hex viewer / Python | magic-byte, encoding and hash checks | inspection only; not for in-place `.uasset` string edits |

---

## 10. Extracted Assets

| Asset | Knowledge-base location | Verification |
|---|---|---|
| Installable Thai font | `Assets/Fonts/CS_ChatThaiUI-Regular.ttf` | raw TTF; 76,284 B; SHA-256 `31AFC16CDFBA6A3A097824C9FBB681BAA18FF0DD4A403B0C47A4448C38277A6A`; internal family `CS ChatThaiUI` |
| Original patch archive | `Assets/Packages/RTF-Thai-by-Artdekdok_P.pak` | 992,905 B; UE PAK v3, Zlib, unencrypted index; SHA-256 `4F9920CD51E67851D6962E8C97E0A00A71E96CD8E6DFEDAABCEEA6740416E8B5` |
| LocRes reference | `Assets/Text/Game.locres` | 250,640 B; SHA-256 `BA5FFBB2AEB9B3307D5C162339D4BF701ACF54C92F91863D4D98E6499D32049D` |

No image/texture asset exists in the released PAK, so no image was extracted.  Font extraction succeeded; an `EXTRACTION_NOTE.txt` is not applicable.
