# THub Unity Thai Localization Engine

A generic, high-performance Thai localization engine and bridge for Unity (Mono and IL2CPP) games.

---

## 🌟 Key Architecture & Capabilities

1. **Native IL2CPP Serialized Asset Packing**:
   - Built on **AssetsTools.NET** (`NativeAssetPacker`) with `MonoCecilTempGenerator` and `classdata.tpk`.
   - Modifies specific MonoBehaviour and FontAsset records directly in memory using `AssetsReplacerFromMemory`.
   - **Zero Allocator Crashes**: Preserves memory alignments, type tree hashes, and allocator headers without throwing `Size overflow in allocator`.

2. **Multi-Table Scanner & Explicit Locale Field Filtering**:
   - Recursively discovers localized MonoBehaviour tables and TextAssets across `.assets`, `level*`, and `.bundle` files.
   - **Strict Non-English Rejection**: Distinguishes English fields (`m_StringEN`, `m_NameEN`, `m_CommentEN`, `*EN`) and rejects non-English Latin text (French `*FR`, German `*DE`, Spanish `*ES`, Portuguese `*PT`, Italian `*IT`).
   - Generates coverage reports categorized by domain: UI/Menus, Items, Skills, Quests, Dialogues, System.

3. **Standard TStudio CSV Workflow**:
   - Native 5-column schema: `key | source | translation | context | file_path`.
   - Deterministic collision-free keys: `UNITY_{SHA1(file_path|path_id|selector)[:16].upper()}`.
   - Context preserves full object metadata: `MonoBehaviour: {ClassName} | PathID: {path_id} | Field: {field_name} | Order: {order}`.

4. **Queue-Based Duplicate Source Preservation**:
   - Resolves the classic Unity localization bug where duplicate English words (e.g. "None", "Attack", "Normal", "Back") share the same English string but require different contextual Thai translations.
   - Organizes translations into FIFO queues per `(PathID, source)` so each occurrence deterministically receives its correct contextual translation.

5. **TextMeshPro Thai Font & Elevation Pipeline**:
   - Minimal character subset builder (printable ASCII + mapped Thai PUA).
   - Precomposed PUA mapping (`Mapping.json`) eliminating combining mark clipping and floating tone marks.
   - **Tone Mark Component Elevation**: Automatically raises Thai tone marks (`uni0E48`–`uni0E4B`) in PUA composite glyphs (configurable, default `+160` units) via TrueType `glyf` component manipulation.

6. **Independent Read-Back Validation & Hash Manifests**:
   - Independent verification via `UnityPy` confirming repacked assets open cleanly and contain valid PUA text in target PathIDs.
   - Cryptographic SHA-256 Before/After Hash Manifest (`hash_manifest.json`).

7. **Deployment Checkpoints & Safety Enforcements**:
   - **Process Check**: Automatically verifies the game executable is closed before any file copy.
   - **Immutable Original Backup**: Creates read-only backup (`.orig`) and **never overwrites** an existing backup.
   - **Audit Logging**: Appends all actions, source/target hashes, and status to `session_log.md`.
   - **Atomic Rollback**: Restores original game files instantly from immutable backups.
   - **Fallback Hook Policy**: Runtime hooks (BepInEx / MelonLoader) are reserved strictly as secondary fallbacks when assets are encrypted.

---

## 🚀 CLI Usage Guide

```bash
# 1. Scan game assets and export TStudio CSV + coverage report
python unity_thai_engine.py scan "E:/Games/MyGame/MyGame_Data" -o "translations.csv" --report "coverage.json" --report-md "coverage.md"

# 2. Build character subset from translated CSV
python unity_thai_engine.py subset "translations.csv" -o "characters.txt"

# 3. Tune Thai tone marks (+160 units) on your PUA font
python unity_thai_engine.py tune-font "Prompt-Bold_PUA.ttf" -o "Prompt-Bold_PUA_shifted.ttf" --raise-units 160

# 4. Repack native serialized assets with queue-based translations & TMP font
python unity_thai_engine.py pack \
    --input "E:/Games/MyGame/MyGame_Data/resources.assets" \
    --output "packed_output/resources.assets" \
    --csv "translations.csv" \
    --dummy-dlls "E:/Games/MyGame/DummyDll" \
    --unity-version "2020.3.22f1" \
    --font-bundle "thai_font.bundle" \
    --target-font-pathid 2755 \
    --target-material-pathid 13 \
    --target-atlas-pathid 138

# 5. Independently validate repacked asset & generate SHA-256 manifest
python unity_thai_engine.py validate \
    --original "E:/Games/MyGame/MyGame_Data/resources.assets" \
    --packed "packed_output/resources.assets" \
    --manifest "hash_manifest.json"

# 6. Safely deploy to game directory (with process check and immutable backup)
python unity_thai_engine.py deploy \
    --packed "packed_output/resources.assets" \
    --destination "E:/Games/MyGame/MyGame_Data/resources.assets" \
    --game-exe "MyGame.exe"

# 7. Safe Rollback to original if needed
python unity_thai_engine.py rollback \
    --destination "E:/Games/MyGame/MyGame_Data/resources.assets"
```
