# Rune Factory 5 — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer) · verified 2026-07-19

---

## 1. Overview

The Thai mod for **Rune Factory 5**, credited by its README to **com2hand**, is a Unity **IL2CPP runtime-injection** mod. It does not supply Unity bundles or altered game archives: two BepInEx plugins load a translation dictionary and build TMP fallback fonts at runtime.

The package is intentionally partial: its README requires the player to install BepInEx IL2CPP x64 separately and run the game once before copying these plugins. That explains why no BepInEx core/preloader files are included in the delivered mod folder.

---

## 2. Technical Stack

| Item | Detail |
|---|---|
| **Game Engine** | Unity IL2CPP (verified from plugin references) |
| **Developer** | Marvelous Inc. (README) |
| **Mod Architecture** | Runtime Injection — BepInEx 6 IL2CPP + Harmony |
| **Archive Format** | None in package: loose managed DLL, raw TTF, UTF-8 text |
| **AES Encryption** | N/A |
| **Compression** | None |
| **Font System** | TMP runtime `CreateFontAsset` plus fallback-font-table injection |
| **Thai Fonts** | TH Sarabun New Bold, Leelawadee UI, Noto Sans Thai Regular |
| **Text System** | In-memory `Dictionary<string,string>` built from `translations.txt` |
| **Text Encoding** | UTF-8 **without BOM** (first bytes `23 20 52`, a comment); Thai UTF-8 sequences: 2,298,835 |
| **Mod Complexity** | ★★★★☆ — stable text source, but hooks bind to IL2CPP/TMP runtime APIs and can break after game updates. |

---

## 3. โครงสร้างไฟล์ (File Architecture)

```text
BepInEx/plugins/
├── RF5ThaiTranslator.dll                         9,216 B  BepInEx IL2CPP/Harmony translator
├── ThaiFontOverride.dll                          10,240 B  TMP fallback-font injector
└── ThaiFont/
    ├── translations.txt                      10,352,319 B  UTF-8 translation dictionary
    ├── thai0.ttf                                  96,240 B  TH Sarabun New Bold
    ├── thai1.ttf                                 393,764 B  Leelawadee UI
    ├── thai2.ttf                                 217,004 B  Noto Sans Thai Regular
    └── thai3.ttf                                  96,240 B  byte-identical thai0 duplicate
```

Binary evidence: both plugins begin `4D 5A` (PE); each font begins TrueType magic `00 01 00 00`; `translations.txt` begins `# Rune Factory 5 - Thai Translations`, proving no BOM. The package has no `.bundle`, `.assets`, PAK, UTOC, or UCAS file.

---

## 4. Font Analysis

`ThaiFontOverride.dll` references `BepInEx.Unity.IL2CPP`, `Unity.TextMeshPro`, `0Harmony`, `TMP_FontAsset`, `CreateFontAsset`, `get_fallbackFontAssetTable`, and `set_fallbackFontAssetTable`. Its embedded strings name methods `CreateFonts`, `MakeFont`, `UpdateFontAssetData`, and `AllThaiChars`: direct evidence for runtime TMP FontAsset construction and fallback attachment.

Shell font verification:

| Source file | Family returned by Windows | Size | SHA-256 |
|---|---|---:|---|
| `thai0.ttf` | TH Sarabun New Bold | 96,240 B | `1F036E5B9E7164203B4475B58210FDAB5862107438E1BF2870FF3FE8BE05E7AF` |
| `thai1.ttf` | Leelawadee UI | 393,764 B | `796DC7E97B357F9C2AD10044D01A86D3FB49CF80E3693011EB055C466C995DE0` |
| `thai2.ttf` | Noto Sans Thai Regular | 217,004 B | `974C4519BB0321CCDD283EA75F44FF0D8F8C969F2FF6460B62DA171D8C2CE95F` |
| `thai3.ttf` | TH Sarabun New Bold | 96,240 B | identical to `thai0.ttf` |

The plugin uses aliases `Thai1` and `Thai2`, but without IL-level method bodies no exact original-font-to-fallback mapping is claimed. Verify vowels, tone marks, and all active TMP styles in-game after any font replacement.

---

## 5. Text Analysis

`RF5ThaiTranslator.dll` references `BepInEx.Unity.IL2CPP`, `0Harmony`, `Dictionary` and methods/identifiers `BuildThaiDictionary`, `ThaiDict`, `InstallHooks`, and `Load`. This is direct metadata/string evidence that the plugin loads a dictionary then hooks text at runtime.

`translations.txt` has 61,378 physical lines: 10 comments and **61,368 translation records**. Every non-comment record contains `=`. Most records have one equals sign, but 959 have multiple, so parse by splitting only on the **first** `=`; later equals signs belong to source or translation text. It is UTF-8 without BOM, has 2,298,835 Thai UTF-8 sequences, and SHA-256 `FFB6BEC05C54FAC654A197C44697E1BA62B7292594C20C5F6AD3722FE5663306`.

The first record is `Yes=ใช่`; duplicate source keys exist, so preserve ordering and use the plugin’s observed overwrite behavior when changing a key. Do not save as UTF-16 or add a BOM unless the plugin parser is changed and tested.

---

## 6. Cross-Engine Comparison

This follows the Unity IL2CPP + BepInEx pattern used by Endzone, but the mechanisms differ: Endzone replaces a structured UTF-16 JSON localization file and hooks TMP text/fallbacks, while Rune Factory 5 loads a 61k-line UTF-8 first-`=` dictionary through a dedicated translation plugin. Both avoid editing game bundles and are therefore easier to distribute, but both depend on runtime APIs rather than stable serialized assets.

Compared with Unity bundle/StringTable mods, this is more editable but less update-resilient: a change to an IL2CPP method, TMP API, or the game text path can disable translation without corrupting any game files.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด

### Font pipeline

1. Keep the raw TTF files in `BepInEx/plugins/ThaiFont/` and use only fonts licensed for redistribution.
2. Load bytes through the IL2CPP-compatible BepInEx API; create TMP FontAssets and attach them to existing fallback tables.
3. Log successful font creation and the text hook. Test UI, dialogue, item names, floating vowels, and tone marks.
4. When replacing a font, preserve file names unless the plugin code is updated to match.

### Text pipeline

1. Read `translations.txt` as UTF-8 without BOM; preserve comment lines.
2. Split each record at the first `=` only. Keep source key exact, including whitespace and control tokens.
3. Translate the value; retain placeholders, rich-text markup, escaped characters, and line-break semantics.
4. Validate 61,368 non-comment records and UTF-8 output, then deploy with both DLLs and all referenced fonts.
5. Inspect BepInEx logs after a game update; rebuild hooks with IL2CPP inspection tooling if the target methods changed.

---

## 8. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Plugin does not load | Mono BepInEx or incomplete IL2CPP bootstrap | Install BepInEx 6 IL2CPP x64, launch once, then add the mod files. |
| Thai shows tofu boxes | Font plugin failed or a referenced file is missing | Check plugin log; restore all TTFs and `ThaiFontOverride.dll`. |
| Text stays English | Translator hook failed or key mismatch | Verify `RF5ThaiTranslator.dll`, use exact source keys, and check IL2CPP method changes after updates. |
| Translation missing/truncated | Parser split an embedded `=` incorrectly | Split on first `=` only; retain the remainder verbatim. |
| Garbled Thai | Wrong encoding/BOM change | Save UTF-8 without BOM. |
| Crash after update | Game IL2CPP/TMP API changed | Reinspect metadata/dumps and rebuild the Harmony hooks; do not edit game archives blindly. |

---

## 9. Required Tools

| Tool | Purpose | Source |
|---|---|---|
| BepInEx 6 IL2CPP | Runtime host required by this mod | https://builds.bepinex.dev/projects/bepinex_be |
| Il2CppInspector or Cpp2IL | Recover IL2CPP type/method metadata after game updates | Official project distributions |
| dnSpyEx/ILSpy | Inspect managed plugin metadata and references | https://github.com/dnSpyEx/dnSpy |
| Python/.NET | Validate UTF-8 dictionary counts and first-`=` parsing | https://www.python.org/ |

---

## 10. Extracted Assets

| Asset | Result |
|---|---|
| `Assets/Fonts/thai0.ttf` | TTF verified: TH Sarabun New Bold, 96,240 B. |
| `Assets/Fonts/thai1.ttf` | TTF verified: Leelawadee UI, 393,764 B. |
| `Assets/Fonts/thai2.ttf` | TTF verified: Noto Sans Thai Regular, 217,004 B. |
| `Assets/Fonts/thai3.ttf` | Verified duplicate of `thai0.ttf`; retained for plugin filename compatibility. |

Font files are extractable and installable. Confirm the original fonts’ redistribution licences before publishing a package.
