# Warhammer 40,000: Chaos Gate - Daemonhunters (Thai Localization Bible)

## Overview
This game uses Unity Engine and stores its localization entirely within custom `MonoBehaviour` assets inside a single bundle file. The font uses TextMeshPro (SDF) and requires standard PUA mapping to fix floating Thai tone marks.

## Engine & Tools
- **Engine**: Unity
- **Font System**: TextMeshPro
- **Text Location**: `StreamingAssets/bundles/localization/english`
- **Font Location**: `StreamingAssets/bundles/textmeshpro_assets` (Asset: `IBMPlexSansThai-Regular_PUA SDF`)
- **Modding Toolkit**: UnityPy, TStudio, TRun

## Extraction & Packing Workflow (TStudio Ready)
All text in the game (including DLCs like Duty Eternal and Execution Force) is isolated within exactly 21 `MonoBehaviour` files inside the `english` localization bundle.

### 1. Unpacking Text (`ChaosGate_unpacker.py`)
- The script uses `UnityPy` to read the `english` bundle.
- It scans for `MonoBehaviour` objects with the `localizationData` field.
- It extracts all 13,673 entries and merges them into a **single unified TStudio Native CSV** (`ChaosGate_AllText.csv`).
- **Format**: `ID, Source, Translation, AI_Reference`
- **ID Structure**: `[MonoBehaviourName]||[OriginalID]` to ensure safe repacking.

### 2. Translation
- The CSV file (`ChaosGate_AllText.csv`) can be directly loaded into **TStudio** or processed by **TRun**.
- Translators do **NOT** need to manually apply PUA formatting during translation. 
- Save the finished translation as `ChaosGate_AllText_translated.csv`.

### 3. Packing & PUA Integration (`ChaosGate_packer.py`)
- The script reads the translated CSV and automatically applies the Thai PUA mapping (`Mapping.json`) to all translated text.
- It unpacks the `english` bundle, locates the exact `MonoBehaviour` using the prefixed ID, and injects the PUA-formatted Thai text into the `translation` field.
- It outputs a ready-to-play `english.patched` bundle (rename to `english` to apply).

## Font Modification
To display Thai text correctly, the original font must be replaced with a Thai font that includes PUA (Private Use Area) characters for shifting tone marks.
1. Extract `textmeshpro_assets`.
2. Find the font asset (e.g., `IBMPlex`).
3. Replace the `m_Script` atlas and character tables with a generated `IBMPlexSansThai-Regular_PUA SDF.asset` from Unity.
4. Repack the bundle.
