# Avatar: Frontiers of Pandora — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer) · verified 2026-07-20

---

## 1. Overview

This Thai mod is a Snowdrop-engine hybrid deployment: a `version.dll` loader enables mods/scripts, while loose `blue/` files replace UI fonts and English localization packages. It is a direct override layout, not a packed archive mod.

---

## 2. Technical Stack

| Item | Detail |
|---|---|
| Engine | Ubisoft Snowdrop |
| Developer | Massive Entertainment / Ubisoft |
| Architecture | Hybrid loader + loose `blue/` override files |
| Bootstrap | `version.dll` PE proxy, `version.ini` has `EnableMods=true` and `EnableScripts=true` |
| Archives | None in delivered mod; loose `.locpackbin` localization packages |
| AES | N/A |
| Font system | Raw TrueType fonts mapped to original font filenames |
| Text system | Snowdrop binary `.locpackbin` packages |
| Encoding | Binary container; no BOM/plain-text encoding inferred |
| Complexity | ★★★☆☆ — files are loose, but localization package schema is proprietary |

---

## 3. File Architecture

```text
version.dll                                  194,048 B  PE `MZ`
version.ini                                      719 B  loader configuration
blue/baked/ui/fonts/                         9 font aliases
blue/localization/packages/english/
├── menus.locpackbin                       5,051,203 B
├── subtitles.locpackbin                   8,599,698 B
└── subtitles_nocc.locpackbin              8,539,874 B
```

The mod supplies three distinct binaries under nine requested names. `.otf` aliases are not OpenType-CFF: their magic is `00 01 00 00`, so they are TrueType data with a filename alias.

---

## 4. Font Analysis

| Canonical file | Shell-verified family | Size | Thai glyphs |
|---|---|---:|---:|
| `dinnextltarabic-bold.ttf` | DIN Next LT Arabic Bold | 298,316 B | 87 |
| `dinnextltarabic-regular.ttf` | DIN Next LT Arabic Regular | 284,592 B | 87 |
| `dinnextltarabic-light.ttf` | DIN Next LT Arabic Light | 316,512 B | 87 |

FontTools confirms U+0E00–U+0E7F coverage count 87 for every canonical font. Hashes prove aliases reuse these bytes: bold alias SHA-256 `E7C92A83…`, regular `FF353B93…`, light `18689668…`. Keep all nine filename aliases because UI resources may resolve each original Snowdrop font name separately. License/redistribution status is not established by this package; treat the supplied font files as mod assets.

---

## 5. Text Analysis

The three `.locpackbin` files are binary localization containers. Their headers differ by package: menus begins `06 00 00 00 9F 78 00 00`; subtitles/subtitles_nocc begin `07 00 00 00 1D 00 01 00`. They are not safe to edit as UTF-8/UTF-16 text; use a Snowdrop localization-aware extractor and preserve keys, placeholders, and package header/schema.

---

## 6. Cross-Engine Comparison

Unlike the Glacier RPKG approach used by HITMAN 3, Avatar supplies loose named override files after loader initialization. Like other proprietary localization containers, the editable-looking file names do not imply plain text: `.locpackbin` needs schema-aware tooling.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด

1. Deploy `version.dll`, `version.ini`, and `blue/` at game root.
2. Preserve all font aliases; replace each canonical TTF only with a Thai-capable TrueType file tested at all UI weights.
3. Extract/rebuild `.locpackbin` using Snowdrop-aware tooling; never save the raw file from a text editor.
4. Validate menus, subtitles, closed-caption variant, controller labels, Thai marks, and loader boot.

---

## 8. Troubleshooting

| Symptom | Resolution |
|---|---|
| Mod does not load | Confirm `version.dll`/`version.ini` are at game root and `EnableMods=true`. |
| Some UI uses wrong font | Restore all nine aliases; an omitted alias can fall back to the original font. |
| Thai characters garble | Restore original binary package; edit only through a locpack-aware workflow. |
| Subtitles differ from CC | Update both `subtitles.locpackbin` and `subtitles_nocc.locpackbin` as required. |

---

## 9. Required Tools

| Tool | Purpose |
|---|---|
| FontTools | Verify names/cmap/glyph coverage |
| Snowdrop localization tool | Extract/rebuild `.locpackbin` |
| Hash tool | Verify aliases and deployment outputs |
| PE viewer | Inspect loader DLL if troubleshooting bootstrap |

---

## 10. Extracted Assets

`Assets/Fonts/` contains the three verified raw TTF files: Bold, Regular, and Light. The source aliases are byte-identical copies under Snowdrop UI font names; use the mod source for the complete nine-name deployment set.
