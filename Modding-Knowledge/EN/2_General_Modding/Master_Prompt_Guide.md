# 🤖 Master Prompt: Techniques for Writing Control Commands for AI Translation Assistants

This file is a professional-grade command template (System Prompt) designed to control AI (such as ChatGPT, Gemini, Claude) to act as an assistant in game localization modding projects systematically, preventing the AI from skipping steps or breaking files.

> [!TIP] How to Use
> Copy all the text in the **code box below**, modify the information within the brackets `[...]` to match the game you are currently working on, and then send it to the AI as the very first message when starting a new chat.

---

## 📋 Master Prompt Template (Copy the text below)

```text
Context & Goal: I want to create a professional-grade Thai language mod for the game: [Game Name, e.g., Dead Island 1]. We will work together step-by-step systematically. Here is the preliminary information for the project:

Environment:
Workspace: [Working folder path, e.g., E:\Mod_Workspace\DIDE\]
Game Directory: [Game installation path, e.g., F:\SteamLibrary\steamapps\common\DIDE\]
Translation Tool: [Existing translation script path, e.g., E:\Mod_Workspace\Tool\0_run_translation\run_translation_DL2_V2.py]

Milestones & Workflow: Please acknowledge all the workflow steps below. We will proceed one step at a time. When one is finished, I will tell you to move to the next:

1. Extraction, Analysis & Failsafe (Extract files and backup originals):
- Find and extract text files (dialogue, cutscenes, UI, menus).
- Ironclad Rule: Always create a Backup_Original folder in the Workspace and back up all original files first to prevent file corruption.
- Analyze the file structure (.pak, .arc, .bin, etc.) to determine what Tool is required for Unpack/Pack.

2. Font & UI Architecture (Deep dive into the font system):
- Inspect how many types of fonts the game uses, which files they are in, and what formats they are (.ttf, .otf, Sprite).
- Prepare for creating or converting fonts to Thai.

3. Pre-Translation Glossary (Analyze and extract specific terms):
- Before starting the actual translation, scan all text files to extract "proper nouns" (characters, locations, items, weapons, enemies) into a list for me to review.
- Use this list to establish standard terminology (GLOSSARY) so the translation remains consistent throughout the entire game.

4. Proof of Concept (Test translation and font on the main menu):
- Translate text specifically in the "main menu" section first (using the principle: translate concisely so the text does not overflow the UI frames).
- Pack the Thai font and menu files into the game to test if the font displays correctly, without floating vowels or rendering as "tofu" boxes. If there are issues, they must be resolved at this step.

5. Script Customization & Safety Rules (Modify the translation script):
- Modify the Translation Tool to support this game's structure by adding strict commands to "never modify tags and variables" (e.g., %s, {Item_Name}, <color=red>) to prevent game crashes.
- Important: Once the script is written, "pause and wait" so I can input the API Key and update the GLOSSARY file before running the mass translation.

6. Mass Translation & Automated QA (Mass translation and using validation scripts):
- When I give permission, run the script to translate all files.
- Before packing them back into the game, write a short script (Validator Script) to cross-check the English and Thai files for any missing color codes, brackets, or %s variables.
- Only if the script finds zero errors will we proceed to pack all files into the game.

7. Final Playtest (Quality check and project completion):
- I will playtest the game to check for bugs, leaking code, or overflowing text. Once perfect, we will conclude the project.

Instructions for AI: Now, please acknowledge that you thoroughly understand the goal and all steps, and you may begin working on Step 1 immediately (tell me which folder you will back up to and how you will extract the files).
```

---

> [!NOTE] Why use this Prompt?
> Outlining the 7 goals in advance lets the AI know the plan, preventing the bot from trying to skip steps (such as attempting to translate the entire game in a single chat, which would definitely cause the bot to hallucinate or error out). Instead, the bot will constantly check on your progress step-by-step according to the established roadmap.


---
**Created by:** [NodNuatTranslator](https://www.facebook.com/NodNuatTranslator/)
