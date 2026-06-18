# 🦾 Deus Ex: Mankind Divided - Modding Guide

This document provides an overview of the Thai localization project for **Deus Ex: Mankind Divided**, which runs on the **Dawn Engine**.

## 1. Modifying the Dawn Engine
The Dawn Engine is a game engine developed as an evolution of the Glacier 2 Engine (used in Hitman). Modifying text is therefore complex:
- Patching files requires deep binary-level manipulation, as text files are usually compiled into the game's resource-level files.
- If package files cannot be penetrated directly, we can use a **Hook** technique via `MinHook` to intercept text in memory (reference methods can be found in the `MinHook_Blueprint.md` document in the 02_Techniques folder).

## 2. Workspace Structure
The management of translation files in this project is proportionally divided to ensure data safety:
- `1_Thai_Project`: A dedicated folder for managing Thai texts and translations.
- `2_backup`: Stores original data before any modifications are made.
- `3_work`: The main workspace for text extraction and file merging.
- `6_mod`: The folder where files are packed and ready to be placed into the game.
- `cleanup.py` script: Used for cleaning up temporary files (Temp files) before building a new mod version, preventing leftover files that could cause issues with the game.


---
**Created by:** [NodNuatTranslator](https://www.facebook.com/NodNuatTranslator/)
