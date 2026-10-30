# Zombie Army Trilogy — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

> Analysis date: 2026-08-30. This record separates verified evidence from README claims because the sole installer is blocked by the host malware policy and cannot be byte-read.

---

## 1. Overview

Zombie Army Trilogy is a Rebellion title built on the in-house Asura engine; Rebellion’s own PlayStation Blog describes the title as using its Asura engine. The supplied Thai mod is documented by its README as a **file-replacement** installer: it backs up original files to `_ThaiMod_Backup`, then replaces text and font files used when the game runs in English. The installer was not executed and its payload could not be extracted because Windows Defender blocked all reads.

## 2. Technical Stack

| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Asura Engine (Rebellion proprietary; externally confirmed, not inferred from inaccessible mod bytes) |
| **Developer** | Rebellion |
| **Project Codename** | ไม่พบหลักฐาน |
| **Archive Format** | ไม่ทราบ—installer ถูก OS บล็อกก่อนอ่าน header/payload |
| **AES Encryption** | N/A: ไม่ใช่ UE archive ที่เข้าถึงได้ |
| **Compression** | ไม่ทราบ; ไม่มี byte-level evidence |
| **Font System** | README ระบุการแทนฟอนต์/bitmap glyph slots; ต้องตรวจ payload ก่อนยืนยัน |
| **Thai Font Used** | “Sarabun SemiBold” ตาม README เท่านั้น, ยังไม่ยืนยันจาก font metadata |
| **Text System** | ไฟล์ข้อความเฉพาะ Asura ที่ถูกแทนที่ (README claim); format/encoding ยังไม่พิสูจน์ |
| **Text Encoding** | ไม่ทราบ; ไม่สามารถทำ BOM/Thai UTF-8 scan ได้ |
| **Mod Complexity** | ★★★★☆ — proprietary engine resources และ font glyph remapping; การแกะจริงถูกระงับโดย security block |

## 3. โครงสร้างไฟล์ (File Architecture)

```text
ZombieArmyTrilogy ThaiMod .../
├── อ่านก่อนติดตั้ง.txt                         4,546 B  [plain UTF-8 text; read successfully]
└── ZombieArmyTrilogy_ThaiMod_Setup.exe    43,353,235 B  [access denied by Defender]
    └── payload: NOT INSPECTED / NOT EXECUTED
```

Magic-byte result:

| File | Result |
|---|---|
| `อ่านก่อนติดตั้ง.txt` | Begins `5A 6F 6D 62 69 65...`; plain text containing UTF-8 Thai bytes |
| `ZombieArmyTrilogy_ThaiMod_Setup.exe` | **No magic available**. Defender denied `ReadAllBytes` and `Get-FileHash`; do not assume PE layout merely from extension. |

## 4. Font Analysis

README states that the mod uses **Sarabun SemiBold**, tuned for Thai vowel and tone-mark placement in the game’s actual drawing bounds. It also says existing Greek, Cyrillic, Japanese, and Chinese character positions are used as Thai glyph addresses. This indicates an atlas/character-map replacement strategy is plausible, but it is not proof of bitmap versus embedded vector font.

No installable TTF/OTF was extracted. The OS denied access before any file could be searched for `00 01 00 00` (TTF) or `4F 54 54 4F` (OTF), so no family, size, foundry, licence, glyph coverage, or font name can be verified. See [EXTRACTION_NOTE.txt](Assets/Fonts/EXTRACTION_NOTE.txt).

Thai rendering risk: repurposed slots make a locale switch to Greek/Cyrillic/Japanese/Chinese incompatible with this mod; test combining vowels and tone marks in menu, HUD, subtitle, and long wrapping strings after any rebuild.

## 5. Text Analysis

The README claims 3,959 hand-translated lines: menus/options/controls/statistics/loading hints (1,793); objectives (480); results/level names/character and weapon descriptions (427); cutscene and in-level dialogue (658); opening narration/biographies (93); credits/system/Steam text (508), including Left 4 Dead character DLC. These counts are scope claims, not parsed record counts.

No binary text file was accessible, so the key-value/table layout, filenames, record count, placeholder tokens, control codes, compression, and encoding remain unknown. In particular, a Thai-looking README does **not** demonstrate that the game text uses UTF-8. A future analysis must scan the recovered text assets before editing and preserve all keys/tokens and ordering.

## 6. Cross-Engine Comparison

The existing [Zombie Army 4: Dead War Bible](../Zombie_Army_4_Dead_War/Zombie_Army_4_Dead_War_Thai_Localization_Bible.md) is the closest internal comparison. It has byte-verified Asura headers: `RSFL` font libraries, `HTXT` text tables, and `DLET`/`DLLT` environment resources. Zombie Army Trilogy shares the engine family, but **must not** be assumed to share those exact tags or layouts—the current installer’s payload was inaccessible.

Reusable practice: keep raw assets, record magic bytes and hashes before unpacking, validate any font through its table directory, and test Thai glyph metrics in every UI context. Reusing the Zombie Army 4 parser or binary offsets for Trilogy without proof is unsafe.

## 7. Pipeline — ขั้นตอนสร้างม็อด

### Font pipeline

1. Obtain a trusted, security-readable installer or an already-extracted payload; do not disable endpoint protection merely to inspect it.
2. Scan every recovered archive and embedded stream for TTF/OTF magic; parse the table directory before carving a candidate font.
3. If the font is an atlas/map resource, identify glyph index, advance, bearing, UV and kerning records from a verified parser.
4. Map Thai glyphs consistently in every target language slot and rebuild all related metrics/atlases.
5. Verify the resulting TTF/OTF with font metadata if one exists; otherwise document that the font is bitmap-only.

### Text pipeline

1. Identify each actual Asura text container with magic bytes and determine compression/record boundaries.
2. Dump keys and source strings with a parser; retain identifiers, format placeholders, tags and ordering.
3. Encode Thai only after proving the required encoding, then repack with the same verified tool.
4. Install into an English-language test copy, validate all stated content groups and retain a clean-file backup.

## 8. Troubleshooting

| อาการ | สาเหตุที่เป็นไปได้ | แนวทางที่ปลอดภัย |
|---|---|---|
| Defender blocks installer | Source is classified virus/PUA by host policy | Do not run/bypass it; obtain a trusted, readable payload and analyse that copy |
| Thai letters missing | Glyph mapping/atlas not installed or wrong language selected | Verify the exact resource mapping; README expects English game language |
| สระ/วรรณยุกต์ลอย | Incorrect glyph metrics, bearing or shaping rules | Compare Thai samples in all UI surfaces; rebuild metrics together with atlas |
| Game crash after installation | Version mismatch, invalid repack, or corrupt offsets | Restore `_ThaiMod_Backup`; compare byte hashes; repack only via proven parser |
| ข้อความเพี้ยน | Wrong encoding or modified control tokens | Identify encoding from recovered bytes and preserve every formatting token |

## 9. Required Tools

| Tool | Purpose | Source |
|---|---|---|
| Windows Defender / endpoint policy | Establish whether source is safe/readable | Host operating system |
| Hex viewer or Python | Inspect magic bytes, encoding and offsets after source is readable | Local tooling |
| Asura-specific extractor/repacker | Required to parse real Trilogy resource records | Must be validated against original files before use |
| FontTools | Validate a recovered TTF/OTF table directory and naming metadata | Python `fonttools` project |
| Hash utility | Record SHA-256 before/after extraction and installation | PowerShell `Get-FileHash` |

## 10. Extracted Assets

No game asset can be extracted from the current source because the 43,353,235-byte installer is blocked before byte access. The outcome and safe resumption conditions are documented in [EXTRACTION_NOTE.txt](Assets/Fonts/EXTRACTION_NOTE.txt). The only readable source artifact is the 4,546-byte README; it is not an extracted game asset and is not copied as a font substitute.

---

### Evidence and external references

- [Rebellion’s Zombie Army Trilogy development post](https://blog.playstation.com/archive/2015/02/06/zombie-army-trilogy-marches-onto-ps4-march/) identifies Asura as its in-house engine.
- [Zombie Army 4: Dead War internal Bible](../Zombie_Army_4_Dead_War/Zombie_Army_4_Dead_War_Thai_Localization_Bible.md) supplies the byte-verified comparison only; it is not evidence of Trilogy’s inaccessible file layout.
