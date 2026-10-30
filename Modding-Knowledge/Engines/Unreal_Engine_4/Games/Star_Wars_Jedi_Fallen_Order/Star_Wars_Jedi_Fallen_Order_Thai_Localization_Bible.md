# STAR WARS Jedi: Fallen Order — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
STAR WARS Jedi: Fallen Order is a Respawn Entertainment action-adventure built on Unreal Engine 4. The supplied Thai mod is a **file-replacement PAK overlay**: place its higher-suffix PAK in `SwGame\Content\Paks\` so Unreal resolves its localization and font resources over the English game assets.

The archive was listed and unpacked successfully without an AES key. It replaces one complete game localization resource and floods six UI font slots with one identical Thai-enabled OpenType font.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Unreal Engine 4 |
| **Developer** | Respawn Entertainment |
| **Mod architecture** | File replacement / PAK overlay |
| **Archive Format** | UE4 PAK version 3; footer magic `E1 12 6F 5A` at offset `0xFC6CF` (1,033,903) |
| **AES Encryption** | **No AES encryption** — index and all entries list/extract through repak without a key |
| **Compression** | Zlib (UE4 PAK compression method 1); 1,033,947 B PAK expands to 3,161,294 B of payload |
| **Font System** | UE4 `.ufont` slot replacement; files are raw OpenType CFF data |
| **Thai Font Used** | CS PraKas FD Bold / `CSPraKasFD-Bold` |
| **Text System** | UE `FTextLocalizationResource` / `.locres` |
| **Text Encoding** | UTF-16 LE strings in the binary LocRes container |
| **Mod Complexity** | ★★★☆☆ — one structured LocRes plus direct OTF substitution; rebuild discipline is essential |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```text
pakchunk0-WindowsNoEditor_9_P.pak                         1,033,947 B
├── SwGame/Content/Localization/Game/en/Game.locres       2,902,046 B
│   └── Thai game text; LocRes header GUID at 0x00,
│       version byte 0x01 at 0x10
└── SwGame/Content/UI/Fonts/
    ├── ITCAvantGardePro-Bk.ufont                          43,208 B
    ├── ITCAvantGardePro-BkObl.ufont                       43,208 B
    ├── ITCAvantGardePro-Demi.ufont                        43,208 B
    ├── ITCAvantGardePro-Demi_2.ufont                      43,208 B
    ├── ITCAvantGardePro-Md.ufont                          43,208 B
    └── SerifGothicStd-ExtraBold.ufont                     43,208 B
        └── all six are byte-identical `CSPraKasFD-Bold` OTF files
```

The PAK has no useful header magic at offset `0x00` (the PAK index is stored at the end). Its canonical UE4 signature is in the footer. The footer declares PAK version `03 00 00 00`; the archive contains exactly seven entries and `repak` extracts all of them.

---

## 4. Font Analysis
Each `.ufont` begins with `4F 54 54 4F` (`OTTO`) at offset `0x00`: it is an unwrapped OpenType CFF font despite the Unreal-oriented filename. All six have SHA-256 `26BF992F0CEC937B9F33F54774CF1BA6D4CB1EA921852A92E263BD00CFF729F0`, confirming deliberate font flooding rather than six independent font faces.

Font metadata verified from the embedded OpenType name/cmap tables and with Windows Shell after extraction:

| Field | Verified value |
|---|---|
| Family | CS PraKas FD |
| Style | Bold |
| PostScript name | `CSPraKasFD-Bold` |
| Format | OTF / CFF |
| Size | 43,208 B |
| Glyphs | 222 total; 87 Thai-block glyphs (`U+0E00`–`U+0E7F`) |
| Foundry metadata | BoonUni / Chanok Samiti |

Font mapping is every listed original UI slot → the same Thai OTF. This makes coverage consistent across menus and subtitles, but collapses italic/medium/extra-bold visual distinctions into one Bold face. Test tone marks and floating vowels (`่ ้ ๊ ๋`, `ิ ี ึ ื`) in dense UI labels; glyph presence is proven, while final placement depends on UE4 shaping and widget layout.

---

## 5. Text Analysis
`Game.locres` is a binary `FTextLocalizationResource`, not a CSV/JSON file. Its first 16 bytes are the UE LocRes magic GUID `0E 14 74 75 67 4A 03 FC 4A 15 90 9D C3 37 7F 1B`; byte `0x10` is version `0x01`. Decoding the string payload as UTF-16 LE finds **254,188 Thai code points** in **14,389 runs** of three or more Thai characters.

The resource is a single game-wide table of namespace/key/string tuples. Preserve its header, namespace/key hashes, string table order and all UTF-16 length fields. A plain-text replacement or a byte-length-only edit can invalidate offsets and cause missing strings or a startup failure.

---

## 6. Cross-Engine Comparison
The existing **The Outer Worlds** UE4 Bible is the closest knowledge-base comparison: it also uses raw fonts hidden behind `.ufont` names and UTF-16 LE game text, but its localization lives in `.uasset`/`.uexp` string tables. Fallen Order is simpler for text tooling because it uses one `.locres`, but its PAK load order still has the same UE4 overlay risk.

Compared with UE5 IoStore games such as Titan Quest II, Fallen Order has no `.utoc`/`.ucas` companion containers and no Oodle/IoStore mount metadata. A standard version-3 PAK plus LocRes-aware tooling is the correct workflow.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
### Font pipeline
1. Extract the PAK with `repak.exe unpack` and retain the original relative paths.
2. Start from a Thai-capable OTF/TTF with correct combining-mark shaping; verify its magic and name table.
3. If retaining the mod's flooding strategy, copy the identical verified font to all six `.ufont` destination names.
4. Build the PAK with a UE4-compatible PAK tool and validate its footer signature/version before deployment.
5. Copy the output to `SwGame\Content\Paks\` with a suffix that loads after the base PAK; test menus, subtitles and small HUD text.

### Text pipeline
1. Export `Game.locres` with a LocRes-aware tool such as UnrealLocres/FModel-compatible exporter.
2. Translate only string values; retain namespaces, keys, placeholders, rich-text tokens and escaped newlines.
3. Import/rebuild with the same LocRes version (`0x01`) and validate UTF-16 LE output.
4. Repack it at exactly `SwGame/Content/Localization/Game/en/Game.locres`.
5. Test dialogue, menus, objectives and cutscenes; restore the original PAK immediately if text is corrupt.

---

## 8. Troubleshooting
| อาการ | สาเหตุที่เป็นไปได้ | วิธีแก้ |
|---|---|---|
| ม็อดไม่ถูกโหลด | PAK อยู่ผิดโฟลเดอร์หรือชื่อ/ลำดับไม่ชนะไฟล์เดิม | วางใน `SwGame\Content\Paks\` และใช้ suffix ที่โหลดหลัง base PAK |
| เกมเปิดแล้ว crash | PAK footer/index หรือ LocRes offsets เสีย | แตกจากไฟล์เดิมใหม่, rebuild ด้วย PAK/LocRes-aware tool, ตรวจ footer `E1 12 6F 5A` |
| อักษรไทยเป็นกล่อง | มีการใช้ font slot ที่ไม่ได้ flood หรือ font output ไม่ใช่ OTF จริง | ตรวจทั้งหก `.ufont` และตรวจ `OTTO` offset 0 |
| สระ/วรรณยุกต์ซ้อนผิด | Font shaping หรือ layout widget จำกัด | ทดสอบข้อความรวมสระลอย, ปรับคำให้สั้นและใช้ font ที่มี GPOS Thai shaping |
| ข้อความเพี้ยน/หาย | แก้ LocRes เป็น plain text หรือผิด UTF-16 lengths | นำเข้าใหม่ด้วย LocRes tool; ห้ามแก้ byte string ตรง ๆ |

---

## 9. Required Tools
| เครื่องมือ | วัตถุประสงค์ | แหล่งที่มา |
|---|---|---|
| repak_cli | list/unpack/repack standard UE PAK | `E:\Mod_Workspace\Tool\repak_cli\repak.exe` |
| UnrealLocres / FModel | export/import or inspect `.locres` safely | Unreal localization tooling |
| FontTools | inspect OTF name/cmap and Thai glyph coverage | Python package `fonttools` |
| Windows Shell / hex viewer | verify installed font name and magic/footer bytes | Windows built-in / hex viewer |

---

## 10. Extracted Assets
| Asset | Knowledge-base path | Verification |
|---|---|---|
| CS PraKas FD Bold | `Assets/Fonts/CSPraKasFD-Bold.otf` | Raw `OTTO` OTF, 43,208 B; Shell name `CSPraKasFD-Bold` |
| Thai LocRes | `Assets/Localization/Game.locres` | 2,902,046 B; LocRes GUID and UTF-16 LE Thai payload verified |
| Source PAK | `Assets/Raw/pakchunk0-WindowsNoEditor_9_P.pak` | 1,033,947 B; UE4 PAK v3 footer verified |
