# STORY OF SEASONS: Friends of Mineral Town — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer) · verified 2026-07-20

---

## 1. Overview

This BlackChick Community Thai mod (installer v1.0.4 build 24244) is a file-replacement patch for Marvelous' proprietary Ichigo game data. It updates two proprietary `.lzs` resources inside the extensionless `disc` archive: text and bitmap-font data.

---

## 2. Technical Stack

| Item | Detail |
|---|---|
| Engine | Marvelous proprietary engine (Ichigo) |
| Developer | Marvelous Inc. |
| Architecture | File replacement / ZIP injection |
| Archive | `disc` is renamed to `disc.zip` and updated by bundled Info-ZIP |
| Encryption | N/A; ZIP update workflow has no AES layer |
| Compression | Proprietary `.lzs`; do not assume zlib/LZ4 from extension |
| Font | Bitmap/DDS atlas + metrics inside `font_data.lzs` |
| Text | Binary message package, documented UTF-16LE payloads |
| Complexity | ★★★★☆ — proprietary LZS and bitmap metrics require compatible tooling |

---

## 3. File Architecture

```text
resource/
├── message/ichigo_message_all_US.lzs   3,914,554 B
├── ui/font_data.lzs                   29,014,002 B
└── zip.exe                               287,744 B
```

The installer explicitly runs `zip -u disc.zip resource/message/ichigo_message_all_US.lzs resource/ui/font_data.lzs`, then restores the `disc` name. Magic evidence: `zip.exe` is PE (`4D 5A`); message LZS starts `96 62 94 01 FF 30 00 65`; font LZS starts `94 4B B1 07 FF 18 00 1E`.

---

## 4. Font Analysis

No raw TTF/OTF is supplied. `font_data.lzs` is the 29,014,002-byte proprietary package expected to hold bitmap atlas/metrics resources. Earlier package documentation identifies DDS atlas pages and `param.bin`; that structure cannot be independently reconstructed from the compressed bytes without a format-compatible LZS decoder.

Treat the font as bitmap data: Thai vowels and tone marks require dedicated atlas glyphs and correct per-glyph metric/advance records. Do not rename an LZS or DDS blob to TTF.

---

## 5. Text Analysis

`ichigo_message_all_US.lzs` is 3,914,554 B and contains visible UTF-16LE-like string fragments, but it remains a proprietary compressed container. Existing evidence supports UTF-16LE message payloads; exact string counts must only be reported after validated LZS decompression, not from raw compressed-byte scans.

Preserve string IDs, placeholders, control codes, and UTF-16LE serialization when using a compatible decoder/repacker.

---

## 6. Cross-Engine Comparison

Unlike Sea of Stars (UnityFS/TMP) and KCD1/KCD2 (ZIP PAK + GFx), this game has two layers: ZIP `disc` injection followed by opaque LZS resource loading. All share the rule that font resources must match their metric tables; this game has no loose TTF fallback path.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด

### Font

1. Decode `font_data.lzs` with a proven, format-compatible tool.
2. Update DDS atlas pages and metric mappings together for U+0E00–U+0E7F.
3. Repack byte-compatibly as `font_data.lzs`; validate game loading.

### Text

1. Decode `ichigo_message_all_US.lzs`.
2. Edit UTF-16LE message records while preserving IDs/control tokens.
3. Repack and update `disc` with the exact installer ZIP command.

---

## 8. Troubleshooting

| Symptom | Resolution |
|---|---|
| Game fails after install | Restore `disc`; verify ZIP internal paths and compatible LZS output. |
| Thai squares/overlap | Atlas or metric mapping lacks Thai glyphs/combining-mark bearings. |
| Text garbles | Restore UTF-16LE records and control tokens; do not edit raw LZS as text. |
| Patch not applied | Ensure command runs in game root and `disc` exists before renaming. |

---

## 9. Required Tools

| Tool | Purpose |
|---|---|
| Included `zip.exe` | Update the two files in `disc` |
| Format-compatible LZS codec | Decode/repack resources |
| DDS-capable image tool | Edit bitmap atlas pages |
| Hex editor | Verify magic/header bytes |

---

## 10. Extracted Assets

| Asset | Size | SHA-256 |
|---|---:|---|
| `Assets/Raw/font_data.lzs` | 29,014,002 B | `300CFD12C96E77A2E8C41FA6618C6CA9655A1644C52CCDD296EAEF411CF133B1` |
| `Assets/Raw/ichigo_message_all_US.lzs` | 3,914,554 B | `6E11163AE03BE81C264F33E31409E6CF54F7CD3AD7B8A09317D1B45FEA1F37D1` |
| `Assets/Fonts/EXTRACTION_NOTE.txt` | — | Explains no valid TTF/OTF extraction |

---

## 11. M2M Protocol

```python
# Verify before injection; do not fabricate LZS output without a validated codec.
from pathlib import Path
assert Path('resource/ui/font_data.lzs').read_bytes()[:4] == bytes.fromhex('94 4B B1 07')
assert Path('resource/message/ichigo_message_all_US.lzs').read_bytes()[:4] == bytes.fromhex('96 62 94 01')
```

```python
# Intermediate atlas mapping for a verified packer.
import struct
record = struct.pack('<IHHHHh', codepoint, x, y, width, height, advance)
```

Render Thai glyphs with Pillow to a DDS-ready atlas, normalize input text before encoding UTF-16LE, then hand atlas/mapping to a decoder/repacker proven against these LZS headers. Generic zlib/LZ4 compression is not a substitute.
