# HITMAN 3 — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer) · verified 2026-07-20

---

## 1. Overview

This HITMAN 3 Thai mod v1.1 targets game version 3.270.1.0 and is a Glacier engine file-replacement patch. It deploys 29 RPKG patch containers into `Runtime`, replacing localized resources without runtime injection.

---

## 2. Technical Stack

| Item | Detail |
|---|---|
| Engine | IO Interactive Glacier engine |
| Architecture | File Replacement — `chunk*patch*.rpkg` containers |
| Archive | Glacier RPKG; checked files begin `GKPR` (`47 4B 50 52`) |
| AES | N/A; not Unreal PAK |
| Compression | Glacier resource/container compression; requires RPKG-aware tooling |
| Font system | Glacier packaged font resources; no loose TTF/OTF in supplied mod |
| Text system | Packaged localization resources distributed over patch RPKGs |
| Complexity | ★★★★☆ — resource hashes/dependencies and multi-chunk patch ordering matter |

---

## 3. File Architecture

```text
Runtime/
├── chunk0patch5.rpkg     19,341,927 B  GKPR
├── chunk1patch5.rpkg        148,548 B  GKPR
├── chunk3..27patch5.rpkg                 GKPR patch resources
├── chunk28patch2.rpkg      680,984 B  GKPR
├── chunk29patch2.rpkg      137,540 B  GKPR
└── packagedefinition.txt     90,172 B  binary/packed definition data
```

There are 29 RPKG files, not conventional ZIP/PAK archives. `chunk0patch5.rpkg` magic is `47 4B 50 52 FE 07 00 00`; its SHA-256 is `7A4E0B956789F46557F460AF1D32AD07F2ED11A0DEF21898619CB8E4E0B9CD70`.

---

## 4. Font Analysis

No file in the delivered mod has TTF (`00 01 00 00`) or OTF (`OTTO`) magic. The font is packaged as Glacier resources and cannot be carved reliably from a raw RPKG without its resource table and decompression handling. `Assets/Fonts/EXTRACTION_NOTE.txt` records this limitation.

Thai vowel/tone support must be validated only after identifying the active font resource with RPKG Tool; do not assume a font from a resource name or rename raw container bytes as TTF.

---

## 5. Text Analysis

The mod author reports 791,470 Thai words and no remaining English words, with controller/key labels intentionally retained under a translation rule. Text is not a loose CSV/JSON file; it is packaged localization content within multiple RPKG patches. Preserve resource hashes, IDs, placeholders, and patch chunk placement when editing.

---

## 6. Cross-Engine Comparison

Compared with Sea of Stars Unity bundles, both games require engine-aware asset tooling and preserve hashed container identities. Glacier RPKG differs from UnityFS: dependencies and resource hashes are handled through RPKG metadata rather than Unity serialized object IDs.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด

1. Use RPKG Tool to import/list each patch RPKG and identify localization/font resource hashes.
2. Extract a resource and preserve its original hash, type, dependency list, and chunk destination.
3. Edit text/font only with a compatible Glacier workflow; validate placeholders and Thai shaping.
4. Rebuild/deploy under the same `Runtime/chunk*patch*.rpkg` names and test game boot plus NVIDIA Overlay.

---

## 8. Troubleshooting

| Symptom | Resolution |
|---|---|
| Mod ignored | Deploy all patch RPKGs under `Runtime`, not an extra parent folder. |
| Game fails at boot | Restore matching chunk versions; rebuild with compatible RPKG metadata/dependencies. |
| Thai text missing | Verify active localization resource and patch precedence with RPKG Tool. |
| Thai glyphs fail | Identify the real font resource; loose TTF copies are not a supported replacement. |

---

## 9. Required Tools

| Tool | Purpose |
|---|---|
| RPKG Tool | List, extract, edit, and rebuild Glacier resources |
| Hex editor | Confirm `GKPR` headers and resource output |
| Hash tool | Track original/rebuilt RPKG outputs |

---

## 10. Extracted Assets

No installable font was extractable from the supplied RPKG-only package. See `Assets/Fonts/EXTRACTION_NOTE.txt`; extraction requires an RPKG-aware pass over identified font resources.
