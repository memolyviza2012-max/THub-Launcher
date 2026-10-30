# Space Haven — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer) · verified 2026-07-20

---

## 1. Overview

ม็อดภาษาไทยของ **Space Haven** เป็นการแทนที่ไฟล์ทรัพยากรของเกม Java/LibGDX โดยตรง ไม่ได้ใช้ Unity, Unreal, BepInEx หรือ DLL injector. ชุดที่ตรวจเป็นเนื้อหาจาก JAR ที่คลายแล้ว: Java bytecode, XML library และ native LibGDX/Steam libraries สำหรับหลายระบบปฏิบัติการ

ข้อความไทยอยู่ใน XML เดียว ส่วนระบบฟอนต์ระบุ TTF ไทยดิบใน XML อีกไฟล์ จึงแก้ไขและตรวจสอบได้โดยไม่ต้องสร้าง atlas bitmap ใหม่.

---

## 2. Technical Stack

| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Java 7 class format (major version `0x33`) + LibGDX/LWJGL |
| **Developer** | Bugbyte Ltd. |
| **Project / data version** | `library/haven`: `1.0.4_steam_4`; root `version.txt`: `1.0.4` |
| **Mod Architecture** | File Replacement — extracted/repacked game JAR resources |
| **Archive Format** | ชุดที่ส่งมาเป็นต้นไม้ที่คลายแล้ว; ไม่พบ JAR/ZIP/Pak ในโฟลเดอร์นี้ |
| **AES Encryption** | N/A — ไม่พบ Unreal container หรือ encrypted archive |
| **Compression** | `.cim` ทั้ง 33 ไฟล์เริ่ม `78 9C` = zlib; XML และ TTF เป็นข้อมูลดิบ |
| **Font System** | LibGDX FreeType runtime generation from raw TTF, configured by `library/fonts` |
| **Thai Font Used** | Noto Sans Thai Light (`NotoSansThai-Light.ttf`) |
| **Text System** | XML record table: `<t id="…" pid="…">` with language child elements including `<TH>` |
| **Text Encoding** | UTF-8 without BOM; CRLF line endings |
| **Mod Complexity** | ★★☆☆☆ — แก้ XML/TTF ได้ตรง ๆ แต่ต้องคงโครงสร้าง JAR และ zlib `.cim` เดิมไว้ |

---

## 3. โครงสร้างไฟล์ (File Architecture)

```text
Space Haven/                                      extracted JAR root
├── fi/bugbyte/.../*.class                         9,948 Java classes; `CA FE BA BE`
├── com/badlogic/gdx/...                            LibGDX runtime classes
├── library/
│   ├── texts                         8,455,523 B  UTF-8 XML Thai localization
│   ├── fonts                             31,902 B  XML font definitions/mappings
│   ├── NotoSansThai-Light.ttf             47,556 B  active Thai TTF
│   ├── haven                          21,899,983 B  raw XML game data (`<data libVersion=...>`)
│   └── 0.cim … 32.cim                 17.70 MiB  zlib-compressed binary/resource blocks
├── windows/, linux/, macos/                         platform native dependencies
├── gdx*.dll / libgdx*.so / *.dylib                 LibGDX FreeType/native libraries
└── strings.xml                                      launcher metadata XML
```

Magic-byte evidence: `LibraryParser.class` begins `CA FE BA BE 00 00 00 33`; `library/texts` begins `3C 74 3E` (`<t>`); `library/fonts` begins `3C 66 3E` (`<f>`); each `.cim` begins `78 9C`; and every supplied `.ttf` begins `00 01 00 00`. `0.cim` zlib-decompresses successfully to 16,777,228 bytes, confirming zlib rather than assuming it from its extension.

---

## 4. Font Analysis

`library/fonts` maps the language code `TH` to Thai font ID `98009`, and defines twelve `thai*` entries, IDs `98001`–`98012`, all pointing to `NotoSansThai-Light.ttf`. Sizes cover 14, 15, 16, 17, 18, 19, 20, 21, and 30 px; `thaiFont1` has a deliberate vertical offset `y=2`, while the other inspected Thai entries use `y=0`.

| Property | Verified value |
|---|---|
| File / format | `NotoSansThai-Light.ttf`, TrueType; magic `00 01 00 00` |
| Family / PostScript | Noto Sans Thai Light / `NotoSansThai-Light` |
| Size / SHA-256 | 47,556 B / `A60DB4E297974176042D09D3F066BD3670AE3A091F3A04DB747450E43C1E425C` |
| Font data | 459 glyphs, 1,000 UPM, 87 mapped Thai-block code points |
| Combining support check | has U+0E01, U+0E34, U+0E48, U+0E50 (base, vowel, tone, Thai digit) |
| License | Noto fonts are distributed under SIL Open Font License 1.1; retain license notice when redistributing |

The `finc="1"` setting and FreeType native libraries (`gdx-freetype*.dll/.so/.dylib`) indicate runtime TTF rasterization. Thai marks should be tested in every target size because a light face plus outlined/shadow parameters can visually collide even when the font has correct OpenType shaping tables (`GPOS`, `GSUB`).

---

## 5. Text Analysis

`library/texts` is an 8,455,523-byte UTF-8 XML document without BOM. It contains **6,829** `<t id="…">` records and exactly **6,829** `<TH>` elements, with 300,153 Thai Unicode code points. A record has stable numeric `id`, an optional parent/category `pid`, then parallel language tags such as `EN`, `DE`, `JA`, and `TH`; for example, ID 54 translates `Crate` to `ลัง`.

Preserve every record ID, `pid`, language tag, XML escape, placeholder, and newline. Do not translate or re-encode the binary/zlib `.cim` files as localization text. Quest, item, UI, and dialogue strings share this central table rather than being split into individual locale files.

---

## 6. Cross-Engine Comparison

Compared with the Endzone: A World Apart Bible in this knowledge base, both mods supply real TTF assets and loose editable localization data. Endzone needs Doorstop/BepInEx/TMP runtime hooks and UTF-16 JSON; Space Haven directly resolves a `TH` XML field and a LibGDX/FreeType font definition, so it has no injector startup risk and uses UTF-8 XML instead.

The important shared discipline is to preserve the loader contract: Endzone needs its expected JSON path/BOM, while Space Haven needs stable XML IDs, the `TH` language tag, and the exact `library/` path inside the game JAR.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด

### Font pipeline

1. Copy a Thai-capable TTF into `library/` and validate its first four bytes are `00 01 00 00` (or `OTTO` for OTF only if the runtime accepts it).
2. In `library/fonts`, point every required `thai*` definition to that filename; preserve the Thai IDs and `lang="TH"` mapping.
3. Tune `s`, `y`, border, and shadow parameters per UI class. Start with the proven Noto mapping rather than replacing all font IDs globally.
4. Test base consonants with upper/lower vowels, tones, numbers, long tooltips, and 14/16/30 px screens.

### Text pipeline

1. Parse and write `library/texts` as UTF-8 without BOM.
2. Edit only `<TH>` contents while retaining each `<t id>` and `pid`; escape `&`, `<`, and `>` correctly.
3. Validate XML and count records before/after; the analyzed build baseline is 6,829 records and 6,829 Thai entries.
4. Rebuild the JAR with the same internal paths. Do not accidentally ZIP an extra parent directory, and keep `.cim` byte streams unchanged unless deliberately regenerating their zlib payloads.

---

## 8. Troubleshooting

| Symptom | Cause / resolution |
|---|---|
| Thai text shows fallback squares | Confirm `<l lang="TH"><font fid="98009"/></l>` and the referenced TTF are present at `library/` root in the final JAR. |
| Vowels or tone marks overlap | Test the affected `thai*` font size; adjust `y`, padding, outline/shadow, or select a Thai face with appropriate GPOS anchors. Do not alter Thai Unicode order. |
| Game fails on launch after packaging | The JAR was built with a wrong root directory or resource path. Inspect the archive and ensure it contains `library/texts`, not `Space Haven/library/texts`. |
| Thai becomes mojibake | The file was saved in a legacy code page or UTF-16. Restore UTF-8 without BOM and validate XML. |
| Missing UI text after editing | A numeric `id`, `pid`, language tag, placeholder, or XML escape was changed. Diff against the baseline and restore the record shape. |
| `.cim` refuses to load | These are zlib streams (`78 9C`), not XML. Restore the original unless the modified payload was recompressed using zlib. |

---

## 9. Required Tools

| Tool | Purpose | Source |
|---|---|---|
| JDK `jar` | Extract/rebuild and list JAR contents | OpenJDK |
| XML validator / Python `xml.etree` | Validate `library/texts` after changes | Python standard library |
| FontTools | Verify family, cmap, OpenType tables, and glyph coverage | https://github.com/fonttools/fonttools |
| 7-Zip | Non-destructive archive inspection | https://www.7-zip.org/ |
| Python `zlib` | Verify/decompress `.cim` payloads programmatically | Python standard library |

---

## 10. Extracted Assets

| Asset | Destination | Verification |
|---|---|---|
| `NotoSansThai-Light.ttf` | `Assets/Fonts/NotoSansThai-Light.ttf` | Real TTF; Shell metadata reports **Noto Sans Thai Light**; 47,556 B; SHA-256 above. |

The asset was copied directly from the mod's active `library/` font reference, not carved from a texture or renamed from an unverified blob.
