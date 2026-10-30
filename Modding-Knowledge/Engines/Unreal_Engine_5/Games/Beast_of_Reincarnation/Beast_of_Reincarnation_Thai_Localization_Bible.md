# Beast of Reincarnation — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Beast of Reincarnation is delivered here as a **hybrid Unreal Engine 5 localization mod**. The mod uses a standard PAK overlay to replace all non-English UI font slots with one Thai-capable font, plus an IoStore (`.utoc`/`.ucas`) container for the encrypted package/text payload and a `dsound.dll`/Lua runtime compatibility patch for both Steam/Win64 and WinGDK paths.

The PAK is completely inspectable and carries the font swap. The IoStore content is Zlib-compressed and encrypted, so the supplied files establish the text container’s shape but cannot expose localization records without the matching game AES key.

---

## 2. Technical Stack
| รายการ | รายละเอียดที่ยืนยันจากม็อด |
|---|---|
| **Game Engine** | Unreal Engine 5 (PAK v11 + IoStore Toc v3) |
| **Mod Architecture** | Hybrid: PAK font overlay + IoStore package replacement + runtime pattern patch |
| **PAK** | `pakchunk0-Windows_P.pak`, 1,155,405 B, 14 entries |
| **PAK Encryption** | No AES key required; repak lists and extracts all entries |
| **PAK Compression** | Zlib declared in PAK v11 footer; payload compresses 14 × 156,688-B font files into 1,155,405 B |
| **IoStore** | `.utoc` 18,863 B + `.ucas` 8,018,576 B |
| **IoStore Encryption** | Encrypted flag present in container flags `0x0B`; encryption GUID is all-zero; no AES key supplied |
| **IoStore Compression** | Zlib, 655 compressed blocks, 65,536-B block size |
| **Font System** | Raw TrueType files distributed as `.ufont` replacements |
| **Thai Font Used** | Bai Jamjuree Medium / `BaiJamjuree-Medium` |
| **Text System** | UE5 IoStore package payload; inaccessible in supplied encrypted UCAS without key |
| **Text Encoding** | Not determinable from encrypted package content; do not infer UTF-8/UTF-16 from random compressed/encrypted bytes |
| **Mod Complexity** | ★★★★★ — working font overlay is simple; rebuilding encrypted IoStore text requires correct game key and compatible UE5 tooling |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```text
BeastOfReincarnation/
├── Binaries/
│   ├── Win64/dsound.dll                  1,202,688 B
│   ├── Win64/bitfix/bor.lua              1,655 B
│   ├── WinGDK/dsound.dll                 1,202,688 B (same loader path for GDK)
│   └── WinGDK/bitfix/bor.lua             1,655 B
└── Content/Paks/
    ├── pakchunk0-Windows_P.pak           1,155,405 B — 14 raw `.ufont` slots
    ├── pakchunk0-Windows_P.utoc             18,863 B — IoStore Toc v3
    └── pakchunk0-Windows_P.ucas          8,018,576 B — compressed/encrypted bulk packages
```

Binary evidence:

| File | Magic / offset evidence | Interpretation |
|---|---|---|
| PAK | footer magic `E1 12 6F 5A` at `0x11A1C1` (1,155,201); version `0B 00 00 00` | UE PAK version 11 |
| UTOC | `2D 3D 3D 2D ...` (`-==--==--==--==-`) at `0x00`; version `3` at `0x10` | UE IoStore Toc v3 |
| UCAS | high-entropy block data; no raw LocRes GUID | encrypted/compressed IoStore payload, not plain assets |
| `.ufont` | `00 01 00 00 00 12 01 00 ...` at `0x00` | valid raw SFNT TTF, 18 tables |
| `dsound.dll` | `4D 5A` | Windows PE proxy/runtime loader |
| `bor.lua` | `local WIN_P = ...` | pattern-based runtime patch definition |

The UTOC explicitly reports header size 144 B, 101 logical entries, 655 compressed blocks, one compression method name (`Zlib` stored at offset `0x27F2`), directory-index size 5,272 B, one partition, and container ID `0x27469CBB972B1CC0`.

---

## 4. Font Analysis
The PAK contains 14 font slots across `efigsp`, Simplified Chinese, Traditional Chinese, Japanese and Korean font folders. Every file is byte-identical (SHA-256 `CABC15B3FE0A91AD9F5F91C956BCFE63559A10FC28D63E207CC222A25F0F4C79`) and is a raw TTF despite the `.ufont` extension.

| Field | Verified value |
|---|---|
| Family | Bai Jamjuree Medium |
| Style | Regular |
| PostScript name | `BaiJamjuree-Medium` |
| Format | TrueType SFNT |
| Size | 156,688 B |
| Tables | 18, including `cmap`, `glyf`, `GPOS`, `GSUB`, `DSIG` |
| Glyph coverage | 723 cmap entries; 87 Thai-block code points |
| Designer/foundry metadata | Cadson Demak Co., Ltd. / Katatrad Aksorn Co., Ltd. |
| Shell.Application name | `Bai Jamjuree Medium` |

The mod uses **font flooding**: all 14 original CJK/Latin font filenames retain their expected paths but contain the same Thai font. This provides Thai coverage for language-specific UI widgets. It also intentionally loses the visual distinctions of the original Cronos, Garamond, Noto, Klee, Rift, Zen and Gowun faces. Test floating vowels and tone marks in menus, subtitle overlays and narrow CJK-designed widgets.

No license file is included in this mod source; preserve the font’s original licensing requirements before redistributing a modified copy.

---

## 5. Text Analysis
Localization/package content resides in the IoStore payload, not in loose `.locres` files. The UCAS’s raw scan finds no UE LocRes magic GUID `0E147475674A03FC4A15909DC3377F1B`; this is expected for encrypted and Zlib-compressed blocks, not proof that LocRes is absent.

The mod’s UTOC has container flag `0x0B`, which includes the encrypted-container bit. Each recorded compressed block uses compression method index 1 (`Zlib`); attempting to decode the data as Zlib without decryption fails at the first header, consistent with the encryption state. The zero encryption GUID does not make the data unencrypted or provide an AES key. Obtain the matching key only through authorized game/modding workflows before attempting a package inventory.

The runtime `bor.lua` contains two Windows byte-pattern patch rules. One modifies a conditional byte to `0x75`; the other writes three `0x90` NOP bytes after its match. Treat it as build-sensitive compatibility logic and preserve it unchanged unless the game executable version is verified.

---

## 6. Cross-Engine Comparison
Like **CODE VEIN II** and **Frostpunk 2** in the knowledge base, this is a UE5 mod with a PAK companion and IoStore data. Its critical difference is that the PAK itself is unencrypted and contains all font slots, while the 101-entry IoStore container is encrypted. This allows font preservation/extraction without a key but blocks safe localization-text extraction.

Like **STAR WARS Jedi: Fallen Order**, the mod uses raw SFNT data behind `.ufont` filenames. Fallen Order uses a standard PAK-only overlay; Beast of Reincarnation adds IoStore plus a runtime patch, so a simple repak-only rebuild is insufficient for text changes.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
### Font pipeline
1. Extract the PAK with a UE PAK-aware tool and verify every `.ufont` begins `00 01 00 00`.
2. Start with a Thai font that has verified `cmap`, `GPOS` and `GSUB` support for Thai combining marks.
3. Copy the same validated TTF to all 14 original relative `.ufont` paths if retaining the flooding strategy.
4. Repack as UE PAK v11 with Zlib-compatible metadata; preserve PAK mount path and patch suffix.
5. Test Win64 and WinGDK builds separately if distributing both runtime folders.

### Text pipeline
1. Back up `pak`, `utoc` and `ucas` as an indivisible set.
2. Obtain the authorized AES key for the exact game build and decrypt before attempting Zlib decompression.
3. Enumerate the 101 IoStore entries and identify actual LocRes/uasset text resources with UE5-aware tooling.
4. Export/import text with its original namespace/key/order/encoding; rebuild compatible IoStore metadata and compression.
5. Keep `bor.lua` and matching `dsound.dll` loader path in place, then test startup, menus, dialogue and glyph rendering.

---

## 8. Troubleshooting
| อาการ | สาเหตุที่เป็นไปได้ | วิธีแก้ |
|---|---|---|
| Thai glyphs are boxes | one of the 14 expected font paths is missing or invalid | restore the complete PAK and verify raw TTF magic for all slots |
| UI style/weight looks wrong | flooding intentionally maps every face to Bai Jamjuree Medium | build per-weight replacements only after testing each original slot |
| IoStore tool reports Zlib error | payload is encrypted before decompression | supply the correct AES key for this game build; do not treat it as corrupt Zlib |
| Game fails at launch | PAK/UTOC/UCAS versions are mixed or runtime patch is incompatible | restore the three-container set and matching `bor.lua`; test the correct platform folder |
| Text remains English | encrypted text container was not rebuilt/mounted correctly | verify IoStore output, mount order and game-build key |
| Patch fails after game update | byte signatures in `bor.lua` no longer match | obtain an updated, trusted patch definition; never blindly apply the old offsets |

---

## 9. Required Tools
| เครื่องมือ | วัตถุประสงค์ | แหล่งที่มา |
|---|---|---|
| repak_cli | enumerate/extract/rebuild the unencrypted UE PAK font layer | `E:\Mod_Workspace\Tool\repak_cli\repak.exe` |
| FModel / UE5 IoStore-aware tool | inspect decrypted UTOC/UCAS package paths and assets | local UE tooling |
| Authorized AES key source | decrypt this exact game-build IoStore payload | game/modding authorization required |
| fontTools + Windows Shell | inspect TTF metadata/cmap and verify the extracted font name | Python / Windows |
| Hex/hash tool | verify PAK footer, UTOC fields, encryption metadata and output hashes | binary verification tool |

---

## 10. Extracted Assets
| Asset | Stored path | Verification |
|---|---|---|
| Bai Jamjuree Medium | `Assets/Fonts/BaiJamjuree-Medium.ttf` | installable TTF, 156,688 B; Shell name verified |
| 14 original slot files | `Assets/Fonts/Slots/` | raw `.ufont` source paths preserved; identical source hash |
| Source PAK | `Assets/Raw/pakchunk0-Windows_P.pak` | v11, unencrypted index, 14 font entries |
| Source UTOC | `Assets/Raw/pakchunk0-Windows_P.utoc` | IoStore v3 metadata, 101 entries, Zlib configuration |
| Source UCAS | `Assets/Raw/pakchunk0-Windows_P.ucas` | encrypted/compressed package payload; SHA-256 `938F48239C8DBA5B608DA81168AA2CFF004ADBB41DC52236AABDDA9D97E2DE28` |
| Runtime patch | `Assets/Runtime/bor.lua` | original Windows pattern patch definition |
