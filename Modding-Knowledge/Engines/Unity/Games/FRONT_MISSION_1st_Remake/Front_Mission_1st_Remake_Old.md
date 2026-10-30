# FRONT MISSION 1st: Remake - Modding Knowledge Base

## Overview
- **Game:** FRONT MISSION 1st: Remake
- **Engine:** Unity Engine (Mono)
- **Mod Focus:** Thai Font Injection & TextMeshPro overrides

## Architecture & File Formats
The game is built on Unity (Mono runtime) and utilizes TextMeshPro for its UI text rendering.
Standard AssetBundle.LoadFromFile might be restricted or undesirable if attempting to inject standard .unity3d font bundles due to engine configurations or Addressables.

## Localization Strategy (Rivet Engineer Approach)
To bypass the limitations of modifying raw sharedassets or building .unity3d bundles, the Thai mod community developed a **Dynamic Font Injection** technique using a custom BepInEx Plugin.

### 1. Dynamic Font Injection (FontMod.dll)
Instead of pre-packaging a TMP_FontAsset in an AssetBundle via the Unity Editor, the mod generates the TMP Font at runtime.
- A raw TrueType Font (.ttf), such as NotoSansThai-Regular.ttf, is shipped alongside the plugin in the BepInEx/plugins/font_mod folder.
- A custom C# BepInEx plugin (FontMod.dll) loads this .ttf file directly from disk into memory.

### 2. TextMeshPro Hooking
Once the .ttf is loaded into a standard Unity Font object, the plugin executes the following:
1. Calls TMP_FontAsset.CreateFontAsset(osFont) to dynamically generate the SDF (Signed Distance Field) texture and metrics required by TextMeshPro.
2. Marks the generated asset as DontDestroyOnLoad.
3. Injects the newly created TMP_FontAsset directly into TMP_Settings.fallbackFontAssets.

### Advantages
- **High Compatibility:** This globally affects all text elements in the game without needing to hook individual TextMeshProUGUI components.
- **Bypass File Locks:** It completely bypasses the Unity Addressables filesystem and any strict AssetBundle header checks.
- **Portability:** This exact technique was successfully ported to **Hardspace: Shipbreaker** to solve similar Unable to read header issues with AssetBundles.
