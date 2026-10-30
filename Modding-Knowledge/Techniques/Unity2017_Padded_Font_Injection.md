# Unity 2017 Deep Font Injection (Padded Assets + Minimal Hook)

## The Problem
When replacing fonts in Unity 2017 games (especially Japanese games like *Harvest Moon: Light of Hope*), standard BepInEx/Harmony hooks (like `Text.font = CustomFont`) may fail to render custom fonts (especially Thai PUA fonts). 
Instead of rendering the font or showing missing character blocks ("Tofu"), the game silently falls back to a Windows system font like Tahoma or Leelawadee.
This occurs because:
1. Unity's `Font.CreateDynamicFontFromOSFont` has bugs handling PUA mappings or non-standard TTF tables.
2. Even if dynamically installed via `AddFontResourceExW`, Unity's Freetype engine may fail to build the font atlas texture at runtime.
3. Overwriting `resources.assets` with `UnityPy` using a font of a different size shifts the asset offsets, causing the engine to crash instantly.

## The Ultimate Solution
To bypass all Unity dynamic rendering bugs and engine crashes:
1. **Asset Padding:** Use a Python script to pad the custom `.ttf` file with null bytes (`\x00`) so its exact byte size matches the original font inside `resources.assets`.
2. **Raw Injection:** Inject the padded TTF directly into `resources.assets` overriding the `m_FontData` of the original font object using UnityPy. Because the size matches perfectly, `UnityPy` replaces the byte array without shifting offsets, preventing crashes.
3. **Minimal Hooking:** Write a BepInEx Harmony plugin to intercept any game-specific scripts that try to force the font (e.g., Natsume's `FontAttach`). The plugin should simply return `false` on Prefix to completely disable the script. 
4. **Natural Loading:** Do NOT set `Text.font` manually. Let the Unity Scene load the font naturally. The engine will request the original font from `resources.assets`, but will actually load the padded Custom Font. Since it is loaded statically from the bundle, Freetype builds the atlas without the dynamic OS lookup bugs.

This ensures 100% stability and flawless rendering of complex fonts like Thai PUA.
