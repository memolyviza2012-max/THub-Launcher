# Knowledge Base: In-Memory Font Replacement (Dead Space Case Study)

## Overview
This technique is another form of creating Thai localization Mods, focusing on dynamic **"In-Memory Font Replacement"**. It aims to solve the problem of games that do not support Thai fonts and have font file structures that are difficult to modify directly.

Unlike Translation Hooking (such as in the GOTG project), which intercepts and changes text before it is displayed, this method targets the **Font Asset** loaded directly in the RAM.

## The Mechanism
This technique relies on Proxy DLL architecture and Inline Hooking (MinHook).

1. **Proxy DLL Loading:** 
   Create a fake DLL (e.g., `dxgi.dll`) for the game to load before the real one. When the game calls it, the system will forward all functions back to the real System DLL.
2. **Asset Preparation:** 
   Read the Thai font file (e.g., Jura font `System.App.Control.dll`) from the disk and store it in a variable in memory.
3. **Module Scanning:** 
   Find the Base Address and size of the Game Executable (`GetModuleHandleA` + `K32GetModuleInformation`).
4. **Safe Environment Setup:** 
   Freeze the execution of all other Threads in the game (`SuspendThread`) to prevent the game from crashing while we are modifying memory.
5. **Memory Patching:** 
   Change memory access permissions (`VirtualProtect` to RWX) at the target location. Then, copy (memcpy) the Thai font data to overwrite the original game font.
6. **Cleanup & Resume:** 
   Clear the CPU instruction cache (`FlushInstructionCache`) and wake all Threads to resume execution (`ResumeThread`).

## Comparison: Dead Space (Font Hook) vs GOTG (Translation Hook)

Both techniques have similarities and differences that can be integrated together:

### Shared Core Architecture
Both knowledge bases can **use the same boilerplate structure**:
* **Proxy DLL Wrapper**: Code for creating a fake `dxgi.dll` or `dinput8.dll` and loading the real functions.
* **MinHook Implementation**: Code for Inline Hooking and safe Suspend/Resume Thread techniques.
* **Memory Management**: Using `VirtualProtect` and `FlushInstructionCache`.

### Different Execution Targets
* **Dead Space (Font Replacement)**
  * **Target:** Binary Asset
  * **Method:** Specify the Memory Offset of the original font, then copy the new font to overwrite it directly (often requires modifying the size/structure Header to match or relying on the game's flexibility).
  * **Challenge:** The Offset location usually shifts every time the game updates (Hardcoded offsets).

* **GOTG (Translation Hook)**
  * **Target:** Render function code or text loading functions.
  * **Method:** Search for the Pattern (AOB Scan) of the function, Detour it to intervene with text parameters, match the original language with Thai in the Dictionary, and pass it back to the game.
  * **Challenge:** You must find the String object structure, and sometimes deal with memory allocation for longer text strings.

## Precautions and Extensions
1. **Finding Offsets:** The Dead Space technique uses a fixed (Hardcoded) Offset table, which breaks immediately upon a game update. This should be improved by implementing **AOB Pattern Scanning** to find font locations automatically.
2. **Text Shaping:** This technique **does not** perform Text Shaping (adjusting stacked vowels/tone marks). If used on a game engine that lacks a manager for this (like HarfBuzz), it will result in floating vowels. It must be combined with Hook techniques on the character drawing function to manually adjust the X/Y axis positions of each Glyph.


---
**Created by:** [NodNuatTranslator](https://www.facebook.com/NodNuatTranslator/)
