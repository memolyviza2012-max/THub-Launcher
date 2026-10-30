# Endzone: A World Apart — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer) · verified 2026-07-20

---

## 1. Overview

This Endzone: A World Apart Thai mod is a Unity 2019.4.33f1 Mono runtime-injection package. It uses **Unity Doorstop 4.5.0** (`winhttp.dll` proxy) to start BepInEx 6, loads `EndzoneThaiFont.dll`, and replaces the English localization file with Thai text.

The complete package has a bootstrap chain absent from the earlier Bible: `winhttp.dll` → Doorstop configuration → `BepInEx.Unity.Mono.Preloader.dll` → BepInEx chainloader → Thai TMP font plugin. The supplied log confirms this sequence completed successfully.

---

## 2. Technical Stack

| Item | Detail |
|---|---|
| **Game Engine** | Unity 2019.4.33f1 Mono |
| **Developer** | Gentlymad Studios |
| **Mod Architecture** | Runtime Injection — Doorstop + BepInEx 6 Mono + TMP hook |
| **Archive Format** | None in delivered mod: loose UTF-16 JSON, managed DLL, raw TTF |
| **AES Encryption** | N/A |
| **Compression** | None |
| **Bootstrap** | Doorstop 4.5.0, `winhttp.dll` proxy, target `BepInEx\\core\\BepInEx.Unity.Mono.Preloader.dll` |
| **Font System** | TMP runtime `CreateFontAsset` and fallback-font-table injection |
| **Thai Fonts** | TH Sarabun New Bold, Leelawadee UI, Noto Sans Thai Regular |
| **Text System** | `English.json` structured localization replacement |
| **Text Encoding** | UTF-16 LE with BOM |
| **Mod Complexity** | ★★★☆☆ — editable text/font inputs, but bootstrap and TMP hook must match Unity Mono. |

---

## 3. โครงสร้างไฟล์ (File Architecture)

```text
Game root/
├── winhttp.dll                                26,112 B  Doorstop proxy (PE `MZ`)
├── mono/
│   ├── .doorstop_version                         5 B  `4.5.0`
│   ├── doorstop_config.ini                    1,451 B  bootstrap configuration
│   └── BepInEx/core/                         duplicate runtime dependency set
├── BepInEx/
│   ├── core/                                 BepInEx 6 Mono runtime
│   ├── plugins/EndzoneThaiFont.dll            10,240 B  font/TMP hook
│   └── plugins/ThaiFont/{thai0..thai3}.ttf
└── Localizations/English.json              2,241,938 B  Thai localization
```

`doorstop_config.ini` has `enabled=true`, directs Doorstop to the Mono preloader, and overrides the Mono DLL search path to `BepInEx\\core`. The nested `mono/BepInEx/core` copy is byte-identical to the root BepInEx core set in sampled hashes; it is deployment redundancy, not a second independent plugin stack.

---

## 4. Font Analysis

`EndzoneThaiFont.dll` is a PE/.NET assembly and exposes TMP symbols including `TMP_FontAsset`, `CreateFontAsset`, `get_fallbackFontAssetTable`, `set_fallbackFontAssetTable`, `CreateThaiFonts`, and `AttachThaiFonts`. The log proves it loads `thai3.ttf` and `thai1.ttf`, generates 161 characters each, hooks `TMP_Text.set_text`, and reaches `Ready! Thai fonts: OK, OK`.

| File | Shell-verified family | Size | SHA-256 |
|---|---|---:|---|
| `thai0.ttf` | TH Sarabun New Bold | 96,240 B | `1F036E5B9E7164203B4475B58210FDAB5862107438E1BF2870FF3FE8BE05E7AF` |
| `thai1.ttf` | Leelawadee UI | 393,764 B | `796DC7E97B357F9C2AD10044D01A86D3FB49CF80E3693011EB055C466C995DE0` |
| `thai2.ttf` | Noto Sans Thai Regular | 217,004 B | `974C4519BB0321CCDD283EA75F44FF0D8F8C969F2FF6460B62DA171D8C2CE95F` |
| `thai3.ttf` | TH Sarabun New Bold | 96,240 B | duplicate of `thai0.ttf` |

The log only proves active use of `thai3` and `thai1`; do not assume `thai2` is actively attached without further runtime inspection.

---

## 5. Text Analysis

`Localizations/English.json` begins `FF FE` and parses as UTF-16 LE JSON. It has a `languageID` and a `translations` list with 9,109 records; raw scanning finds 649,073 Thai UTF-16 LE code units. The English filename is intentional: it replaces the original English locale at the loader's expected path.

Preserve JSON structure, IDs/order, placeholders, and UTF-16 LE BOM. Re-saving as UTF-8 or renaming the file prevents expected localization resolution.

---

## 6. Cross-Engine Comparison

The approach is the same broad Unity Mono/BepInEx pattern as other loose-file runtime mods, but its Doorstop layer is essential: unlike a game with BepInEx preinstalled, Endzone requires a proxy DLL to invoke the preloader before managed game code starts. Compared with UE PAK mods, no archive is rebuilt; the update risk lies in Doorstop, BepInEx, Unity Mono, or TMP API compatibility.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด

### Font pipeline

1. Deploy `winhttp.dll`, `mono/doorstop_config.ini`, and the matching BepInEx core set.
2. Keep raw Thai TTFs in `BepInEx/plugins/ThaiFont/`.
3. Load font bytes, create TMP FontAssets, generate required glyphs, then add them to fallback tables.
4. Validate boot and font-hook log lines before UI testing.

### Text pipeline

1. Parse `English.json` as UTF-16 LE with BOM.
2. Translate fields in `translations` only; preserve schema/IDs/placeholders.
3. Serialize UTF-16 LE with BOM and validate JSON.
4. Test menus, tooltips, all text classes, and Thai combining marks after a full Doorstop/BepInEx boot.

---

## 8. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| No BepInEx log | Doorstop proxy/config missing or wrong | Restore `winhttp.dll`, `mono/doorstop_config.ini`, and target preloader path. |
| Preloader starts but plugin absent | Plugin/core path mismatch | Verify root `BepInEx/plugins/EndzoneThaiFont.dll` and dependency set. |
| Thai boxes | TMP hook/font creation failed | Check for `TMP_Text.set_text HOOKED!`; restore active `thai3.ttf` and `thai1.ttf`. |
| Garbled localization | Wrong encoding | Save `English.json` as UTF-16 LE with BOM. |
| Crash after update | Unity Mono/TMP/BepInEx compatibility changed | Read LogOutput, update matching bootstrap/runtime, and inspect plugin API bindings. |

---

## 9. Required Tools

| Tool | Purpose | Source |
|---|---|---|
| Unity Doorstop | Bootstrap BepInEx through proxy DLL | https://github.com/NeighTools/UnityDoorstop |
| BepInEx 6 Mono | Runtime plugin host | https://github.com/BepInEx/BepInEx |
| dnSpyEx/ILSpy | Inspect managed plugin/API references | https://github.com/dnSpyEx/dnSpy |
| Python/.NET JSON tooling | Validate UTF-16 localization JSON | https://www.python.org/ |

---

## 10. Extracted Assets

| Asset | Result |
|---|---|
| `Assets/Fonts/THSarabunNew-Bold.ttf` | Copied and Shell-verified, 96,240 B. |
| `Assets/Fonts/LeelawadeeUI.ttf` | Copied and Shell-verified, 393,764 B. |
| `Assets/Fonts/NotoSansThai-Regular.ttf` | Copied and Shell-verified, 217,004 B. |

The font files are installable TTFs; confirm original redistribution licences before publishing a repackaged mod.
