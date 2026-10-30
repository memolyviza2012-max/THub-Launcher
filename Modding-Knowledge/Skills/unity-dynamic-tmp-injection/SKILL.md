---
name: unity-dynamic-tmp-injection
description: Guides the agent on how to create a BepInEx plugin that dynamically loads a .ttf font file from the OS at runtime and injects it into Unity's TextMeshPro global fallback list.
---

# Unity Dynamic TextMeshPro Font Injection

Use this skill when you need to add custom fonts (like Thai, Chinese, or Arabic) to a Unity game that uses TextMeshPro, WITHOUT needing to build an AssetBundle through the Unity Editor.

## 🌟 Concept

Normally, adding a new font to TextMeshPro requires opening Unity Editor, generating a \TMP_FontAsset\, and packing it into an AssetBundle. 
This skill uses a **BepInEx plugin** to bypass that completely by generating the \TMP_FontAsset\ dynamically at runtime directly from a raw \.ttf\ file.

## 🛠️ Step-by-Step Instructions

1. **Create a BepInEx Plugin Project**
   Set up a standard C# class library targeting .NET Framework (usually 4.6+ or .NET Standard 2.0).
   Reference the following assemblies from the game's \Managed\ folder:
   - \UnityEngine.dll\
   - \UnityEngine.CoreModule.dll\
   - \UnityEngine.TextRenderingModule.dll\
   - \Unity.TextMeshPro.dll\
   - \BepInEx.dll\

2. **Write the Injection Logic**
   The plugin needs to execute logic during \Awake()\. Use the following logic flow:
   - Determine the plugin's directory path.
   - Load the raw font file (e.g., \custom_font.ttf\) using \
ew Font(fontPath)\.
   - Convert the OS Font to a TMP Font Asset using \TMP_FontAsset.CreateFontAsset(osFont)\.
   - Prevent the font from being destroyed on scene load using \DontDestroyOnLoad()\.
   - Inject the new TMP Font Asset into the global fallback list: \TMP_Settings.fallbackFontAssets.Add(fontAsset)\.

3. **Provide the C# Code Template**
   Use the provided C# template located in \examples/Plugin.cs\ to generate the plugin for the user.

4. **Font Requirements**
   Inform the user that the \.ttf\ file must be placed in the same directory as the compiled \.dll\.
   For Thai language, remind the user that the font must be a **PUA-encoded** font if the game's text uses PUA for floating vowels.

## ⚠️ Limitations & Notes
- This technique relies on \TMP_FontAsset.CreateFontAsset(Font)\, which creates a dynamic font atlas at runtime.
- It is highly compatible with most modern Unity games using TMP.
- Some games might aggressively clear \TMP_Settings.fallbackFontAssets\ on scene loads. If this happens, instruct the agent to hook into \SceneManager.sceneLoaded\ to re-inject the font.
