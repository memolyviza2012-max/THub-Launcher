# Borderlands 3 — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer) · verified 2026-07-20

---

## 1. Overview

This Thai mod for **Borderlands 3** is a UE4 PAK override. A single `_999_P.pak` replaces five English LocRes domains and several UI/experience font assets; the supplied README describes 630,629 Thai words and fixes for Thai cinematic subtitles.

Its `_999_P` priority suffix allows the game to load replacement assets without modifying original archives. The mod targets the English (`en`) locale, so the game’s standard English selection resolves Thai strings.

---

## 2. Technical Stack

| Item | Detail |
|---|---|
| **Game Engine** | Unreal Engine 4 (UE PAK v6 and UE LocRes assets) |
| **Developer** | Gearbox Software |
| **Archive Format** | Standard UE PAK v6; 15 entries; mount `../../../` |
| **AES Encryption** | **No AES encryption** — index is not encrypted; no key GUID. |
| **Compression** | Zlib (repak verification) |
| **Font System** | Raw TrueType `.ufont`/`.ttf` asset replacement |
| **Thai Font Used** | Google Sans Regular, Bold, Bold Italic; 87 Thai cmap code points |
| **Text System** | UE LocRes across Engine, Game, Matchmaking, Presence, and TMS domains |
| **Text Encoding** | UE LocRes binary with Thai UTF-16 LE payload evidence |
| **Mod Complexity** | ★★★☆☆ — conventional PAK/LocRes pipeline; multiple text domains and font mappings require care. |

---

## 3. โครงสร้างไฟล์ (File Architecture)

```text
OakGame/Content/Paks/
└── pakchunk0-WindowsNoEditor_999_P.pak      12,554,417 B
    ├── Engine/Content/Localization/Engine/en/Engine.locres
    ├── OakGame/Content/Localization/{Game,Matchmaking,Presence,TMS}/en/*.locres
    ├── OakGame/Content/UI/_Shared/Fonts/*.ufont
    └── OakGame/Content/UX/experience/fonts/*.ttf
```

The archive footer contains `E1 12 6F 5A` (UE PAK magic), version 6, index offset `0xBF7C41`, index size `0x1443`, and 15 entries. RePak reports the index as unencrypted and the payload compression as Zlib.

---

## 4. Font Analysis

Four UI FontFace `.ufont` files and three Experience TTF paths carry raw TrueType data at offset 0 (`00 01 00 00`), not UE wrapper headers. Each inspected file has a valid 17-table directory including `cmap`, `GDEF`, `GPOS`, `GSUB`, `glyf`, `head`, `name`, and `maxp`.

| UE path | Actual font identity | Size | Thai cmap coverage |
|---|---|---:|---:|
| `FF_OAK_BODY.ufont` | Google Sans Regular | 1,974,592 B | 87 code points |
| `FF_OAK_HEADER.ufont` | Google Sans Bold Italic | 2,035,496 B | 87 code points |
| `FF_WILLOWHEAD_1.ufont` | Google Sans Bold | 1,976,672 B | 87 code points |

The mod preserves original UE asset paths but swaps their raw font payloads. This maintains UI references while supplying Thai glyphs. Use matching weight/style replacements and test combining vowels/tone marks; a body/header mismatch changes wrapping and visual hierarchy.

---

## 5. Text Analysis

Five LocRes assets were extracted: Engine (580,097 B), Game (10,939,548 B), Matchmaking (1,041 B), Presence (5,316 B), and TMS (32,010 B). All begin the standard UE LocRes GUID `0E 14 74 75 67 4A 03 FC 4A 15 90 9D C3 37 7F 1B`.

Observed Thai UTF-16 LE code units include Game 1,457,451, Engine 53,111, TMS 8,142, Presence 1,201, and Matchmaking 1. Use a LocRes-aware parser for exact strings/keys; raw byte scanning is evidence of Thai payload, not a safe entry count.

---

## 6. Cross-Engine Comparison

This is simpler than UE5 IoStore mods such as Tempest Rising: all runtime content is in one inspectable traditional PAK rather than paired UTOC/UCAS containers. Its strategy parallels Frostpunk 2’s PAK override model—replace LocRes and raw FontFace payloads under original paths—while Borderlands 3 uses Zlib PAK v6 and its own multiple localization domains.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด

### Font pipeline

1. Extract original FontFace assets and keep their paths unchanged.
2. Supply a licensed Thai TTF that supports required Thai combining marks; validate sfnt tables/cmap.
3. Map body, header, and Willow styles to suitable Thai weights.
4. Repack as `pakchunk0-WindowsNoEditor_999_P.pak`; verify PAK magic, Zlib handling, and no accidental encryption.

### Text pipeline

1. Extract all five English LocRes domains and preserve namespace/key/format tokens.
2. Translate with a LocRes serializer; never write raw UTF-8 into LocRes binary.
3. Repack to the same `en` paths and test game UI, matchmaking/presence, and TMS strings.
4. Install under `OakGame/Content/Paks`; retain `_999_P` priority. Test cinematics after the subtitle fixes described by the README.

---

## 8. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Thai does not load | PAK path/name/priority wrong | Place it under `OakGame/Content/Paks/` as `pakchunk0-WindowsNoEditor_999_P.pak`. |
| Some systems remain English | A LocRes domain was omitted | Include Engine, Game, Matchmaking, Presence, and TMS. |
| Boxes or bad Thai marks | Font asset mapping/coverage problem | Restore all FontFace paths and use Thai-capable fonts for each UI role. |
| Game crashes after update | PAK/asset version mismatch | Re-extract the updated base assets and rebuild against that version. |
| Corrupted text | LocRes serialized incorrectly | Rebuild with a LocRes-aware tool; preserve keys and format tokens. |

---

## 9. Required Tools

| Tool | Purpose | Source |
|---|---|---|
| repak | Inspect, unpack, and repack UE PAK v6 | https://github.com/trumank/repak |
| UnrealLocres/FModel | Inspect and serialize LocRes | Trusted UE modding distribution |
| fontTools | Validate TTF tables and Thai cmap | https://fonttools.readthedocs.io/ |

---

## 10. Extracted Assets

| Asset | Result |
|---|---|
| `Assets/Fonts/FF_OAK_BODY.ttf` | Raw TTF extracted from `.ufont`; Shell-verified Google Sans Regular; 1,974,592 B. |
| `Assets/Fonts/FF_OAK_HEADER.ttf` | Raw TTF extracted from `.ufont`; Shell-verified Google Sans Bold Italic; 2,035,496 B. |
| `Assets/Extracted/.../*.locres` | All five LocRes domains extracted and magic-verified. |

Confirm Google Sans redistribution terms before publishing a repackaged mod.
