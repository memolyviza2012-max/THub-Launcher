# Seeds of Chaos — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer) · verified 2026-07-21

---

## 1. Overview

ม็อดภาษาไทยของ **Seeds of Chaos** เป็นม็อด **File Replacement** สำหรับ Ren'Py: ผู้ใช้คัดลอกโฟลเดอร์ `game/` ลงทับโฟลเดอร์ `game/` ของเกม ไม่ใช้ archive, DLL injector หรือ runtime loader ภายนอก. ม็อดเปิด locale `thai` ที่ init priority `-1`, โหลด `translate thai` blocks แบบมาตรฐานของ Ren'Py และแทนที่ฟอนต์เดิมด้วย TrueType ที่รองรับภาษาไทย.

ตัวม็อดระบุเวอร์ชัน `v1.0` และวันที่กรกฎาคม 2026 ใน `README.txt`; project/domain reference ที่ตรวจพบคือ `soc.venusnoiregames.org`, จึงระบุผู้พัฒนาเป็น **Venus Noire** ตามหลักฐานในชุดม็อดเท่านั้น. ไม่ได้ให้ executable/game distribution มาด้วย จึงไม่อ้างหมายเลข Ren'Py runtime หรือเวอร์ชันเกมที่ตรวจสอบไม่ได้.

---

## 2. Technical Stack

| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Ren'Py (เวอร์ชัน runtime ไม่อยู่ในไฟล์ที่ได้รับ) |
| **Developer** | Venus Noire — อ้างอิงจากโดเมน `soc.venusnoiregames.org` ที่ปรากฏใน translation payload |
| **Project Codename** | `soc` — จาก MultiPersistent key `soc.venusnoiregames.org` |
| **Mod Architecture** | File Replacement: loose `game/` tree; `thai_activate.rpy` เปิด locale และ map ฟอนต์ |
| **Archive Format** | ไม่มี archive ในชุดม็อด: ทั้งหมดเป็น `.rpy`, `.ttf`, และ README แบบ loose files |
| **AES Encryption** | N/A — ไม่พบ Unreal PAK/IoStore หรือ encrypted container |
| **Compression** | None — ไฟล์ที่ส่งเป็นข้อมูลดิบ; ไม่พบ zlib/LZ4/Oodle header หรือ archive |
| **Font System** | Ren'Py `renpy.config.font_replacement_map` + `translate thai style default` |
| **Thai Font Used** | Noto Sans Thai Regular (variable TrueType; default `wght=400`, `wdth=100`) |
| **Text System** | Ren'Py `translate thai strings:` blocks, `old` → `new` string mapping |
| **Text Encoding** | UTF-8 without BOM; `common.rpy`/`dialogue.rpy` use CRLF, activation script uses LF |
| **Mod Complexity** | ★★☆☆☆ — text and font are loose, human-readable files; riskอยู่ที่ preserving Ren'Py syntax, interpolation, escapes, and exact install path |

---

## 3. โครงสร้างไฟล์ (File Architecture)

```text
Seeds of Chaos Thai Mod/                            43,439,988 B total source payload
├── README.txt                                  3,277 B  UTF-8 text; install/status notes
└── game/
    ├── thai_activate.rpy                      1,085 B  LF UTF-8; sets `config.language = "thai"`
    ├── fonts/
    │   └── NotoSansThai.ttf                 218,652 B  TrueType, `00 01 00 00`
    └── tl/thai/
        ├── common.rpy                     31,809,171 B  CRLF UTF-8; 98,740 old/new pairs
        ├── dialogue.rpy                   11,406,973 B  CRLF UTF-8; 13,491 old/new pairs
        ├── fonts.rpy                              482 B  default-style font assignment
        └── language.rpy                           348 B  Thai language display name
```

Magic-byte inspection covered every supplied file. The font starts `00 01 00 00 00 14 01 00 00 04 00 40 …`, the TrueType sfnt header with 20 table-directory entries; the five `.rpy` files begin ASCII `#` comments and `README.txt` begins `=`. No file begins `UnityFS`, `PK`, `KPKA`, `E1 12 6F 5A`, `78 9C`, or `78 DA`; this is evidence for a loose Ren'Py payload rather than an inferred archive format.

`thai_activate.rpy` executes at `init -1` so the locale exists before normal script initialization. It maps `KinesisStd-Regular.otf`, `kinesis.otf`, `Kinesis_Std_Italic.otf`, and `DejaVuSans.ttf` to `fonts/NotoSansThai.ttf`; `fonts.rpy` additionally maps a `thai_font` alias and assigns the same file to `translate thai style default`.

---

## 4. Font Analysis

The active supplied asset is a real installable font, copied without conversion to `Assets/Fonts/NotoSansThai-Regular.ttf`. Shell font metadata identifies it as **Noto Sans Thai Regular**. FontTools reads sfnt version `0x00010000`, 467 glyphs, 426 best-cmap entries, 1,000 units-per-em, 20 physical font tables, and variable axes `wght` 100–900 (default 400) and `wdth` 62.5–100 (default 100).

| Property | Verified value |
|---|---|
| Source / active path | `game/fonts/NotoSansThai.ttf` / `fonts/NotoSansThai.ttf` |
| Family / PostScript name | Noto Sans Thai Regular / `NotoSansThai-Regular` |
| Format / magic | TTF / `00 01 00 00` at offset `0x00` |
| Size / SHA-256 | 218,652 B / `5A1C559BB539583C8A1FD99D1C5B9491E5E14478C9CD2BD0970D5C3096CC9EF8` |
| Foundry / version | Monotype Imaging Inc.; version 2.002; vendor `GOOG` |
| License / embedding | SIL Open Font License 1.1 in name-table metadata; `OS/2 fsType=0` (no restricted embedding bit) |
| Thai coverage check | 87 mapped Thai-block code points; U+0E01 (ก) and U+0E48 (่) are present |

Font swap mapping is direct: each of the four original Kinesis/DejaVu filenames resolves to one Thai-capable TTF. This can flatten intentional italic/bold differences because the supplied mapping always targets the same default face; use named or variable-font instances only after verifying the target Ren'Py build supports them. The font carries `GDEF`, `GPOS`, and `GSUB`, so combining-mark positioning data exists, but it must be tested in the game at each UI size. Test consonant + upper vowel + tone (`กี่`), lower vowels, Thai digits, long tooltip wrapping, and italic-origin dialogs; never reorder Thai Unicode marks merely to hide a layout problem.

---

## 5. Text Analysis

Localization is source-level Ren'Py mapping, not `.rpyc`, `.locres`, CSV, or JSON. Each `translate thai strings:` stanza contains ordered `old "…"` and `new "…"` entries; Ren'Py resolves the original string against `old`, then displays the corresponding `new` text when `config.language` is `thai`. The supplied README states 112,231 of 112,339 strings are translated (99.9%); direct parse confirms exactly **112,231 paired entries**: 98,740 in `common.rpy` and 13,491 in `dialogue.rpy`.

| File | Size | Pairs | Thai Unicode code points | Role |
|---|---:|---:|---:|---|
| `common.rpy` | 31,809,171 B | 98,740 | 6,692,480 | UI, menu, system, item/scene strings, and miscellaneous source mappings |
| `dialogue.rpy` | 11,406,973 B | 13,491 | 2,491,293 | narrative/dialogue strings; 270 repeated translation headers |
| `fonts.rpy` + `language.rpy` | 830 B | 0 | 3 | style mapping and display label `ไทย (Thai)` |

Both large files decode strictly as UTF-8 with no BOM. `common.rpy` has 2,433 bracketed interpolation-like tokens and 4,077 escaped-newline sequences; `dialogue.rpy` has 1,148 and 5,363 respectively. Preserve `[]` substitutions, `\\n`, quotation escaping, Ren'Py/Python literals, and the exact `old` side. Some entries are source/code-like strings rather than prose, so do not translate identifiers, save keys, paths, or Python syntax unless the original `new` mapping deliberately does so. The files are organized by broad UI/common versus narrative/dialogue payload, not by one file per quest.

---

## 6. Cross-Engine Comparison

`MASTER_INDEX.md` contained no existing Ren'Py Bible at analysis time, so there is no same-engine implementation to claim as a direct precedent. The closest useful comparison is the knowledge-base Bible for **Space Haven**: it also ships a real Noto Sans Thai TTF and loose UTF-8 localization data, but its Java/LibGDX loader resolves XML `<TH>` fields and FreeType font IDs, whereas Seeds of Chaos uses Ren'Py locale selection plus exact-source `old` → `new` mappings.

The transferable rule is preserving the loader contract rather than only preserving Thai glyphs. Space Haven requires stable XML IDs/`TH` fields inside a JAR; Seeds of Chaos requires the literal `game/tl/thai/` tree, valid Ren'Py syntax, unchanged source keys, and `config.language = "thai"`. In both cases a valid TTF alone cannot activate Thai text.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด

### Font pipeline

1. Place the candidate Thai TTF at `game/fonts/`; verify bytes `00 01 00 00` at offset `0` (or `OTTO` for OTF only after runtime testing).
2. Inspect its name table, Thai cmap, and combining-mark coverage before mapping it. Baseline is Noto Sans Thai Regular, 218,652 B, SHA-256 listed in §4.
3. Update `thai_activate.rpy` mappings for every original filename actually used by the game, and preserve init priority `-1`; keep `fonts.rpy` default style aligned with that filename.
4. Launch through a clean game install and test normal, Kinesis italic-origin, DejaVu fallback, menus, dialogs, and mark-heavy Thai strings. Adjust font choice/size/style rather than editing character order.

### Text pipeline

1. Copy the game’s generated/maintained translation source into `game/tl/thai/`; edit as UTF-8 without BOM while retaining the existing newline convention (CRLF for the two large baseline files).
2. Keep every `translate thai strings:` header plus the `old` entry byte-for-character at the source-string level. Edit only `new` strings and preserve `[]`, `{}` text tags, `\\n`, escaped quotes, and Ren'Py/Python literals.
3. Validate strict UTF-8 and compare pair counts before packaging. Current baseline: 98,740 `common` + 13,491 `dialogue` pairs = 112,231.
4. Deliver the folder whose root contains `game/`, not an extra parent directory. Install by merging it into the game root; remove `game/thai_activate.rpy` (or rename it `.bak`) to disable the locale as the supplied README specifies.

---

## 8. Troubleshooting

| Symptom | Cause / resolution |
|---|---|
| Thai stays English | Confirm `game/thai_activate.rpy` is at the installed game root, is not inside an extra archive folder, and still sets `config.language = "thai"` at `init -1`. |
| Squares / fallback glyphs | Confirm `game/fonts/NotoSansThai.ttf` exists and each mapped source filename points to `fonts/NotoSansThai.ttf`. Verify the final file begins `00 01 00 00`. |
| Tone marks or vowels collide | Test the actual UI size and style. Use a Thai font with GPOS/GSUB; do not normalize/reorder Thai marks. Recheck Kinesis italic-origin text because it is mapped to the same regular file. |
| Game errors at startup | A `.rpy` indentation, quote, backslash, or translation-block syntax was changed. Restore the affected file and validate each modified `old/new` pair. |
| Text becomes mojibake | The script was saved as ANSI/Windows-874 or UTF-16. Restore strict UTF-8 without BOM; retain CRLF in `common.rpy`/`dialogue.rpy`. |
| A string no longer translates | Its `old` source text, placeholder, escape, or header changed. Restore the exact original `old` string and preserve `[variable]`, `\\n`, and text tags. |
| Font style looks wrong | The replacement map intentionally routes regular, italic, and fallback names to one regular TTF. Add verified style-specific mappings only when all files are present and tested. |

---

## 9. Required Tools

| Tool | Purpose | Source |
|---|---|---|
| Ren'Py SDK | Parse/run the game and validate translation scripts in the target runtime | Ren'Py distribution |
| Python 3 | Deterministic UTF-8, pair-count, and placeholder checks | Python standard library |
| FontTools | Read name/cmap/OS/2/OpenType tables and verify Thai coverage | `fonttools` Python package |
| 7-Zip | Inspect the distributable without altering its folder layout | 7-Zip |
| PowerShell / hex viewer | Verify magic bytes and SHA-256 before copying assets | Windows built-ins / trusted viewer |

---

## 10. Extracted Assets

| Asset | Destination | Verification |
|---|---|---|
| Noto Sans Thai Regular TTF | `Assets/Fonts/NotoSansThai-Regular.ttf` | Direct copy of active `game/fonts/NotoSansThai.ttf`; valid TTF, 218,652 B, Shell family **Noto Sans Thai Regular**, SHA-256 `5A1C559BB539583C8A1FD99D1C5B9491E5E14478C9CD2BD0970D5C3096CC9EF8`. |

No atlas, bitmap font, or opaque font bundle exists in the supplied payload. A separate failure note is unnecessary because the installable active TTF was successfully extracted and verified.
