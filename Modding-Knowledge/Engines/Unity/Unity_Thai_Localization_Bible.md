# Unity Thai Localization Bible (Master Technical Specification)

> **Canonical Engine Guide**: High-reliability workflow for translating Unity games (IL2CPP and Mono) into Thai using native serialized asset replacement, TextMeshPro PUA typography, and safety-critical release pipelines.

---

## 1. Architectural Foundations

### 1.1 Unity Engine Serialization Model
Unity stores game objects in serialized archives (`.assets`, `level*`, `resources.assets`, and asset bundles). Every asset file contains:
- **File Header**: Engine version, endianness, type tree presence, metadata offset, and total asset size.
- **Type Tree Dictionary**: Schema definitions describing every field and byte layout for standard engine types and custom `MonoBehaviour` classes.
- **Object Table (Metadata)**: Maps a unique 64-bit `PathID` to byte offset, data length, and `TypeId` (e.g., 114 for `MonoBehaviour`, 128 for `Font`, 114 for `TextMeshPro FontAsset`, 28 for `Texture2D`, 21 for `Material`).

### 1.2 The Allocator Pitfall: Why Full-File Repacking Crashes
In IL2CPP games, deserializing and reserializing an entire `.assets` file using general-purpose tools (such as naive UnityPy reserialization) frequently causes runtime crashes with errors like:
```text
Size overflow in allocator
Fatal error in Unity Player: Object allocation failed
```
**Root Cause**: Unity pre-allocates internal memory pools and calculates strict memory alignments based on object tables, type hashes, and script metadata. Modifying unneeded objects or corrupting alignment tables breaks the engine's internal allocator.

**The Solution: AssetsTools.NET Targeted In-Memory Replacement**
Instead of reserializing the entire file:
1. Load the original asset using **AssetsTools.NET** with `classdata.tpk` (matching the target Unity version, e.g., `2020.3.22f1`).
2. Supply `MonoCecilTempGenerator` pointing to Il2CppDumper DummyDlls or Managed assemblies.
3. Modify **only** the targeted localized `MonoBehaviour` tables and TMP `FontAsset`/`Texture2D` records.
4. Inject these modified records using `AssetsReplacerFromMemory`.
5. Write the container without modifying untouched objects, ensuring 100% preservation of file alignment, container headers, and allocator tables.

---

## 2. Discovery & Explicit Locale Extraction

### 2.1 Multi-Table Discovery
Localized text in Unity rarely lives in a single file. Text is commonly split across:
- `globalgamemanagers.assets`: System messages, language selector strings, graphics settings.
- `resources.assets`: Shared item tables, inventory names, skill parameters, quest databases.
- `level0` / `level13`: Main menu scene objects, HUD elements, canvas static labels.
- `sharedassets*.assets`: Dialogue trees, scenario scripts, character status descriptions.

### 2.2 Rejection of Non-English Latin Scripts
Many international games store translations side-by-side in serialized arrays:
- `m_StringJP`: Japanese source.
- `m_StringEN`: English target.
- `m_StringFR`: French.
- `m_StringDE`: German.
- `m_StringES`: Spanish.
- `m_StringPT`: Portuguese.

**CRITICAL RULE**: Do **NOT** extract or overwrite text based purely on regex checks for Latin script (`[A-Za-z]`). French, German, Spanish, and Portuguese use Latin script and will be corrupted if treated as English.
Always verify explicit field names:
```python
ENGLISH_FIELDS = ("en", "english", "m_stringen", "m_nameen", "m_commenten", "m_descen", "m_titleen")
REJECT_FIELDS = ("fr", "french", "de", "german", "es", "spanish", "it", "italian", "pt", "portuguese", "ja", "ko", "zh")
```

### 2.3 Standard TStudio CSV Schema
All extracted strings must conform to the 5-column standard:
```text
key | source | translation | context | file_path
```
- **Deterministic Key**: `UNITY_{SHA1(file_path|path_id|selector)[:16].upper()}`.
- **Context Format**: `MonoBehaviour: {ClassName} | PathID: {path_id} | Field: {field_name} | Order: {order}`.

---

## 3. Context Preservation: Queue-Based Duplicate Source Matching

In game tables, the identical English word appears repeatedly with completely different gameplay meanings. For example:
- `None` (in Equipment slot) -> Thai: `ไม่มี` (Empty)
- `None` (in Category filter) -> Thai: `ไม่ระบุ` / `ทั้งหมด` (Unspecified / All)
- `Back` (in UI navigation) -> Thai: `ย้อนกลับ` (Return)
- `Back` (in Combat targeting) -> Thai: `ด้านหลัง` (Rear)

**Flaw of Legacy Systems**: Storing translations in a `dict[source, translation]` keyed by the English string overwrites the translation, corrupting one or more contexts.

**The Architecture Solution**:
1. Group translations by `PathID`.
2. Within each `PathID`, store translations in a **FIFO Queue** keyed by source:
   ```csharp
   Dictionary<long, Dictionary<string, Queue<string>>> translationQueues;
   ```
3. During packing, as the engine traverses the serialized table in native order, it calls `queue.Dequeue()`.
4. This preserves 100% of contextual distinctions across repeated source strings.

---

## 4. TextMeshPro Thai Typography Pipeline

### 4.1 The Thai Rendering Problem in Unity
Unity's default TextMeshPro renderer does not contain a complex OpenType shaping engine for Thai by default. Consequently:
- Thai tone marks (ไม้เอก, ไม้โท, ไม้ตรี, ไม้จัตวา) and upper vowels (อิ, อี, อึ, อือ) detach, float too high, or clash with tall consonants (ป, ผ, ฝ, ฟ).
- Lower vowels (อุ, อู) clash with descending consonants (ญ, ฎ, ฏ, ฐ).

### 4.2 Precomposed PUA Mapping
To achieve flawless typography:
1. Map Thai consonant-vowel-tone combinations to Private Use Area (PUA) codepoints (`0xF000`–`0xF89F`).
2. Use longest-match-first replacement: composite combinations (e.g. `กิ่`, `กิ้`, `ปิ่`) are replaced before individual vowels or tone marks.
3. Normalize canonical forms: replace decomposed Sara Am (`\u0E4D\u0E32`) with canonical `ำ` (`\u0E33`).

### 4.3 Vertical Tone Mark Offset Tuning (+160 Units)
Even in precomposed PUA fonts, games often render tone marks slightly too low or clipped by bounding boxes.
- Using `fontTools.ttLib.TTFont`, inspect the TrueType `glyf` table.
- For all composite glyphs in the PUA range (`0xF000`–`0xF89F`), detect tone components:
  `{"uni0E48", "uni0E49", "uni0E4A", "uni0E4B"}`
- Elevate vertical offset:
  ```python
  component.y += raise_units  # Default: +160 font units
  ```
- Re-save the TrueType font (e.g. `Prompt-Bold_PUA_shifted.ttf`).

### 4.4 Minimal Character Subset Generation
Rather than replacing a game's massive multi-lingual font (which inflates memory and crashes atlas allocators):
1. Extract printable ASCII (`0x20`–`0x7E`) for numbers, English text, tags (`<color=...>`, `{0}`).
2. Collect all mapped PUA characters present in non-empty translations.
3. Collect unmapped base Thai consonants.
4. Feed this minimal set (`characters.txt`) into Unity's TextMeshPro Font Asset Creator to generate a single clean 2048x2048 or 4096x4096 texture atlas.

---

## 5. TMP Font Asset Transplantation

To replace the game's font without modifying code:
1. Create a TMP FontAsset bundle in a blank Unity project matching the game's Unity version (e.g. `2020.3.22f1`).
2. In the target asset file, locate:
   - Target TMP FontAsset (`TypeId 114`, e.g. PathID `2755`).
   - Target Font Material (`TypeId 21`, e.g. PathID `13`).
   - Target Atlas Texture2D (`TypeId 28`, e.g. PathID `138`).
3. During repacking with `AssetsTools.NET`:
   - Keep target FontAsset's local `m_GameObject` and `m_Script` pointers.
   - Redirect source FontAsset's `material` PPtr to target Material PathID.
   - Redirect source FontAsset's `atlas` and `m_AtlasTextures` to target Texture2D Atlas PathID.
   - Inject source Texture2D byte array directly into target Atlas.

---

## 6. Safety Verification & Deployment Protocol

### 6.1 Independent Read-Back Validation
Never deploy packed assets directly to the game directory without independent verification:
1. Load packed asset using `UnityPy`.
2. Confirm asset parses without EOF or byte misalignment exceptions.
3. Confirm target `PathID` objects contain readable Thai/PUA text.
4. Generate `hash_manifest.json` recording original vs packed SHA-256 hashes and file sizes.

### 6.2 Deployment Checkpoints
1. **Game Process Check**: Check `tasklist` to ensure the game executable is closed before attempting file copy.
2. **Immutable Backup**: Ensure an original backup exists (e.g. `resources.assets.orig`). Set it read-only (`chmod 0444`). **NEVER overwrite an existing backup.**
3. **Verified Copy**: Copy packed file to destination. Verify destination SHA-256 matches validated packed output.
4. **Audit Logging**: Append checkpoint entry to `session_log.md`.
5. **Rollback**: Provide one-command restore from immutable backup if game fails to boot.

### 6.3 Runtime Hook / BepInEx Policy
- **Primary Method**: Native asset repacking is the gold standard for release builds.
- **Fallback Only**: Runtime hooks (BepInEx / MelonLoader) should only be used if assets are encrypted, packed in proprietary archives, or if text is dynamically constructed in managed code.

---

## 7. Workflow Quick Reference

| Stage | Command | Key Output |
| :--- | :--- | :--- |
| **1. Scan** | `python unity_thai_engine.py scan <assets_dir> -o trans.csv` | TStudio CSV + Coverage Report |
| **2. Subset** | `python unity_thai_engine.py subset trans.csv -o chars.txt` | Minimal Character Set |
| **3. Tune Font** | `python unity_thai_engine.py tune-font font.ttf -o font_shifted.ttf` | TrueType Font (+160 units) |
| **4. Repack** | `python unity_thai_engine.py pack --input orig.assets --output packed.assets --csv trans.csv` | Native Serialized Asset |
| **5. Validate** | `python unity_thai_engine.py validate --original orig.assets --packed packed.assets --manifest hash.json` | Verification & SHA-256 Manifest |
| **6. Deploy** | `python unity_thai_engine.py deploy --packed packed.assets --destination <game_path>` | Process-Safe Installation & Audit Log |
| **7. Rollback** | `python unity_thai_engine.py rollback --destination <game_path>` | 100% Original Restoration |
