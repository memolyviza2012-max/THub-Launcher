# 🤖 AI Agent Workflow: Modding Knowledge Upload Protocol (KI)

**Knowledge Item (KI):** Standard Operating Procedure (SOP) for the AI Assistant to upload modding knowledge data to your GitHub repository `memolyviza2012-max` upon the completion of any game project.

## 🎯 Purpose
To provide the AI with clear instructions for gathering technical documentation files (README), AI translation scripts (Python), and various Batch Scripts, and organizing them neatly into the `Modding-Knowledge` repository without requiring step-by-step commands from the user.

## 🛠️ AI Action Plan

When the user types commands along the lines of: *"Upload to github now"*, *"Save KI to Github"*, or *"Project finished, upload data"*, the AI must immediately follow these steps:

1. **Prepare the Destination Repository:**
   - Check if the folder `E:\Mod_Workspace\Modding-Knowledge` already exists.
   - If not, run the command `git clone https://github.com/memolyviza2012-max/Modding-Knowledge.git E:\Mod_Workspace\Modding-Knowledge`
   - If it exists, `cd` into it and run the `git pull` command to update to the latest data.

2. **Organize Folder Structure for the New Game:**
   - Create a new folder under `Games/[Game_Name_Without_Spaces]` (e.g., `Games/SpaceHulk_Deathwing`).

3. **Copy Knowledge and Script Files (Knowledge Extraction):**
   - Copy the following files from the specific game project's Workspace folder to the newly created folder:
     - `README.md` (which summarizes all KI techniques discovered in the project)
     - `*.py` (the active translation scripts)
     - `*.bat` (Workflow scripts such as 1_export, 2_import, 3_pack)
   - **🛑 CRITICAL SECURITY RULE:** Before performing `git commit` and `git push`, the AI MUST inspect every `*.py` file and **completely remove all API Keys (e.g., `sk-...`)**, replacing them with `"YOUR_DEEPSEEK_API_KEY"` every time. Never upload scripts containing active keys to the internet!
   - **Additional Caution:** Do not copy large files or directories such as the `Extracted` folder, `.pak` files, `.locres` files, or large image files under any circumstances.

4. **Account Configuration (If necessary):**
   - Run the commands `git config user.name "Antigravity"` and `git config user.email "antigravity@gemini.com"` (or use system defaults if already set).

5. **Commit & Push:**
   - Run the commands:
     ```bash
     git add .
     git commit -m "Add [Game Name] modding techniques and scripts"
     git push
     ```

6. **Report Results to the User:**
   - Notify the user that the Knowledge Item (KI) has been successfully stored into the GitHub arsenal, attaching the URL if possible.


---
**Created by:** [NodNuatTranslator](https://www.facebook.com/NodNuatTranslator/)
