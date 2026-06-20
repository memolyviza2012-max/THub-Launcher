import os
import shutil

# Paths
SRC_DIR = os.path.join(os.path.dirname(__file__), "Modding-Knowledge", "TH")
DST_DIR = r"E:\Mod_Workspace\Modding-Knowledge"

# Explicit file mappings (relative to SRC_DIR -> relative to DST_DIR)
EXPLICIT_MAPPINGS = {
    # Frostbite
    os.path.join("1_Engine_Hacking", "Frostbite", "DeadSpace_Font_Replacement_Strategy.md"): 
        os.path.join("Engines", "Frostbite", "DeadSpaceRemake", "Font_Replacement_Strategy.md"),
    os.path.join("1_Engine_Hacking", "Frostbite", "MEA_Thai_Localization_Guide.md"): 
        os.path.join("Engines", "Frostbite", "MassEffectAndromeda", "MEA_Thai_Localization_Guide.md"),
    
    # Unreal / UDK -> XCOM
    os.path.join("1_Engine_Hacking", "UnrealEngine", "UDK_Thai_Font_Guide.md"): 
        os.path.join("Games", "XCOM_Enemy_Unknown_TH_Modding", "UDK_Thai_Font_Guide.md"),
    
    # Dead Island 2
    os.path.join("3_Game_Guides", "Dead_Island_2", "DeadIsland2_TH_KI.md"): 
        os.path.join("Games", "DeadIsland2_Thai_Mod", "README.md"),
    os.path.join("3_Game_Guides", "Dead_Island_2", "The_Bible_of_DeadIsland2_Modding.md"): 
        os.path.join("Games", "DeadIsland2_Thai_Mod", "The_Ultimate_Modding_Bible.md"),
        
    # Dishonored
    os.path.join("3_Game_Guides", "Dishonored_1", "Dishonored_Modding.md"): 
        os.path.join("Games", "Dishonored_1", "README.md"),
        
    # Dying Light 2
    os.path.join("3_Game_Guides", "Dying_Light_2", "Modding_Wiki.md"): 
        os.path.join("Games", "Dying Light 2", "Modding_Wiki.md"),
        
    # Space Hulk
    os.path.join("3_Game_Guides", "SpaceHulk_Deathwing", "SpaceHulk_Modding.md"): 
        os.path.join("Games", "SpaceHulk_Deathwing", "README.md"),
        
    # XCOM
    os.path.join("3_Game_Guides", "XCOM", "XCom_Knowledge_Transfer.md"): 
        os.path.join("Games", "XCOM_Enemy_Unknown_TH_Modding", "XCom_Knowledge_Transfer.md"),
    os.path.join("3_Game_Guides", "XCOM", "XCOM_Modding_Step_By_Step.md"): 
        os.path.join("Games", "XCOM_Enemy_Unknown_TH_Modding", "XCOM_Modding_Step_By_Step.md"),
        
    # MinHook
    os.path.join("2_General_Modding", "MinHook_Blueprint.md"): 
        os.path.join("Techniques", "Hooking_and_Proxy", "MinHook_Blueprint", "MinHook_Blueprint.md"),
}

def clean_name(name):
    # Replace underscores with spaces for game/folder names to match target convention
    return name.replace("_", " ")

def get_target_path(rel_src):
    # Check explicit mapping first
    if rel_src in EXPLICIT_MAPPINGS:
        return EXPLICIT_MAPPINGS[rel_src]
        
    # Otherwise, apply general fallback rules
    parts = rel_src.split(os.sep)
    category = parts[0]
    
    if category == "0_Getting_Started":
        # Put in Techniques/Getting_Started/
        return os.path.join("Techniques", "Getting_Started", parts[-1])
        
    elif category == "1_Engine_Hacking":
        if len(parts) >= 3:
            engine = parts[1]
            return os.path.join("Engines", engine, *parts[2:])
        elif len(parts) == 2:
            return os.path.join("Engines", parts[1])
            
    elif category == "2_General_Modding":
        filename = parts[-1]
        if "Prompt" in filename or "AI" in filename:
            return os.path.join("Techniques", "AI_Modding", filename)
        return os.path.join("Techniques", "General", filename)
        
    elif category == "3_Game_Guides":
        if len(parts) >= 3:
            game = clean_name(parts[1])
            return os.path.join("Games", game, *parts[2:])
            
    # Default fallback: preserve structure in Techniques/Other
    return os.path.join("Techniques", "Other", rel_src)

def sync():
    if not os.path.exists(SRC_DIR):
        print(f"Error: Source directory {SRC_DIR} not found.")
        return
        
    if not os.path.exists(DST_DIR):
        print(f"Error: Destination directory {DST_DIR} not found.")
        return

    print("Syncing Modding Knowledge to E:\\Mod_Workspace\\Modding-Knowledge\\...\n")
    
    success_count = 0
    for root, _, files in os.walk(SRC_DIR):
        for f in files:
            if not f.endswith(".md"):
                continue
                
            full_src = os.path.join(root, f)
            rel_src = os.path.relpath(full_src, SRC_DIR)
            
            rel_dst = get_target_path(rel_src)
            full_dst = os.path.join(DST_DIR, rel_dst)
            
            # Ensure target directory exists
            os.makedirs(os.path.dirname(full_dst), exist_ok=True)
            
            # Copy file
            shutil.copy2(full_src, full_dst)
            print(f"Copied:\n  Src: {rel_src}\n  Dst: {rel_dst}\n")
            success_count += 1
            
    print(f"Sync completed! Successfully copied {success_count} files.")

if __name__ == "__main__":
    sync()
