# Suicide Squad: Kill the Justice League — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

## 1. Overview
Thai mod v1.2 for game 4.8.40 uses a transactional byte-range installer for existing UE IoStore containers, plus an optional EAC bypass deployment.

## 2. Technical Stack
| Item | Detail |
|---|---|
| Engine | Unreal Engine 4 IoStore |
| Architecture | Hybrid: transactional range patch + optional EAC bypass |
| Containers | `pakchunk0` PAK and `pakchunk0/51` UCAS |
| AES | Not determinable from payload-only distribution |
| Compression | Existing game IoStore compression retained; payloads are range replacements |
| Font | Chakra Petch named by mod docs; raw font absent |
| Text | Patched packaged localization in game containers |
| Complexity | ★★★★★ — exact base hashes and byte ranges required |

## 3. File Architecture
`installer_manifest.json` validates three base SHA-256 values, deletes obsolete sidecar UCAS/UTOC, then applies three transactional range payloads. Payloads: PAK 43,598,253 B; chunk0 UCAS 94,428,192 B; chunk51 UCAS 31,736,656 B.

## 4. Font Analysis
The installer notes Chakra Petch, but no raw TTF/OTF is included. A candidate TTF signature at PAK payload offset `0x17` fails font parsing, so it was not extracted. See `Assets/Fonts/EXTRACTION_NOTE.txt`.

## 5. Text Analysis
Text is not loose JSON/CSV: it is altered in range patches for UE containers. The release notes report 655,052 Thai words and 553 English words. Preserve container bytes, range manifest offsets, hashes, and string/package schema.

## 6. Cross-Engine Comparison
Unlike ordinary UE PAK override mods, this mod patches original IoStore files in place. It is therefore more version-sensitive than the RPKG patch model used by HITMAN 3.

## 7. Pipeline — ขั้นตอนสร้างม็อด
1. Confirm game version and base SHA-256. 2. Apply ranges transactionally with before/after checks. 3. Validate post hashes. 4. Test boot, menus, dialogue, and font rendering.

## 8. Troubleshooting
| Symptom | Resolution |
|---|---|
| Installer rejects game | Restore/update to tested 4.8.40 base hashes. |
| Game fails boot | Restore originals and reapply transactional ranges. |
| Old dialogue shadows patch | Remove documented obsolete sidecar UCAS/UTOC. |
| Font missing | Do not inject arbitrary TTF; identify actual UE font asset first. |

## 9. Required Tools
| Tool | Purpose |
|---|---|
| Python installer | Validated transactional range writes |
| SHA-256 tool | Base/post verification |
| FModel/UE tools | Inspect real game IoStore font/localization assets |

## 10. Extracted Assets
No valid installable font was available. `EXTRACTION_NOTE.txt` documents the failed verified carve attempt.
