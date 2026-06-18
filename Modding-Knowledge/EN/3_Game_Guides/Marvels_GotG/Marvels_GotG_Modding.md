# 🌌 Marvel's Guardians of the Galaxy - Modding & Localization Guide

This document compiles the techniques and tools used in the Thai localization project for **Marvel's Guardians of the Galaxy**.

## 1. Groot's Translation Problems (Groot's Translation Hallucinations)
In the AI translation process, the biggest issue is that the character Groot only says "I am Groot", which causes the AI system to experience **"Hallucination" (imagining translations on its own)**. The system therefore requires special filtering scripts:
- `find_hallucinations.py` and `clear_hallucinations.py`: Responsible for detecting translations that are unusually long or do not match the sentence "ฉันคือกรู้ท" (I am Groot).
- `search_groot.py`: Manages locking Groot's text to prevent it from being mistranslated into other sentences.

## 2. PUA Font System (Private Use Area)
The game faces obstacles regarding the display of Thai vowels and tone marks. This project uses the **PUA (Private Use Area)** technique to trick the engine:
- `generate_perfect_pua.py` and `apply_pua.py`: Used to map Thai character codes (Codepoints) to the PUA space in newly created fonts.
- `flatten_vowels.py`: Manages the levels of vowels and tone marks to prevent them from overlapping and floating or sinking too much.

## 3. Automated Update System (Automated Build System)
This project has a fairly complete scripting system for updating files, such as:
- `bump_version.py` and `update_readme.py`: Manages automated version bumping and writing patch notes when a new mod version is released.


---
**Created by:** [NodNuatTranslator](https://www.facebook.com/NodNuatTranslator/)
