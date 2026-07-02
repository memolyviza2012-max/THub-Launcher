import argparse
import subprocess
import os
import csv
import sys
import tempfile
import shutil
from collections import defaultdict

UNREAL_LOCRES_TOOL = r"E:\Mod_Workspace\Tool\UnrealLocres.exe"
REPAK_TOOL = r"E:\Mod_Workspace\Tool\repak_cli\repak.exe"

# List of all primary and fallback fonts used by the game
FONT_OVERRIDES = [
    r"U01\Content\MainAsset\TextLibrary\Fonts\NotoSansSC-Bold.ufont",
    r"U01\Content\MainAsset\TextLibrary\Fonts\NotoSansSC-Regular.ufont",
    r"U01\Content\MainAsset\TextLibrary\Fonts\NotoSansSC-Medium.ufont",
    r"U01\Content\MainAsset\TextLibrary\Fonts\NotoSansSC-Light.ufont",
    r"U01\Content\MainAsset\TextLibrary\Fonts\NotoSansSC-Thin.ufont",
    r"U01\Content\MainAsset\TextLibrary\Fonts\NotoSansSC-Black.ufont",
    r"U01\Content\MainAsset\TextLibrary\Fonts\ZiTiQuanXinYiGuanHeiTi3_0-2.ufont",
    r"Engine\Content\EngineFonts\Faces\RobotoBold.ufont",
    r"Engine\Content\EngineFonts\Faces\RobotoRegular.ufont",
    r"Engine\Content\EngineFonts\Faces\RobotoLight.ufont",
    r"Engine\Content\EngineFonts\Faces\RobotoItalic.ufont",
    r"Engine\Content\EngineFonts\Faces\DroidSansFallback.ufont",
    r"Engine\Content\Slate\Fonts\DroidSansFallback.ttf"
]

def pack_mod(csv_path, base_locres_dir, thai_font_path, output_pak):
    if not os.path.exists(UNREAL_LOCRES_TOOL):
        print(f"Error: UnrealLocres not found at {UNREAL_LOCRES_TOOL}")
        sys.exit(1)
        
    if not os.path.exists(REPAK_TOOL):
        print(f"Error: repak.exe not found at {REPAK_TOOL}")
        sys.exit(1)
        
    if not os.path.exists(base_locres_dir):
        print(f"Error: Base locres dir not found at {base_locres_dir}")
        sys.exit(1)
        
    if not os.path.exists(csv_path):
        print(f"Error: Translated CSV not found at {csv_path}")
        sys.exit(1)
        
    if not os.path.exists(thai_font_path):
        print(f"Error: Thai font not found at {thai_font_path}")
        sys.exit(1)

    print("Step 1: Grouping TStudio CSV by target...")
    target_data = defaultdict(list)
    try:
        with open(csv_path, 'r', encoding='utf-8-sig', errors='replace') as infile:
            reader = csv.reader(infile)
            headers = next(reader, None)
            for row in reader:
                if len(row) < 3:
                    continue
                
                combined_id = row[0]
                source = row[1]
                translation = row[2]
                
                parts = combined_id.split("||", 1)
                if len(parts) == 2:
                    target_name = parts[0]
                    key = parts[1]
                else:
                    target_name = "Game"
                    key = combined_id
                    
                if not translation.strip():
                    translation = source
                    
                target_data[target_name].append([key, source, translation])
    except Exception as e:
        print(f"Error parsing TStudio CSV: {e}")
        sys.exit(1)

    temp_dir = tempfile.mkdtemp(prefix="outpost_build_")
    
    print("Step 2: Injecting translated text into locres...")
    for target_name, rows in target_data.items():
        print(f"Processing target: {target_name}")
        ue4loc_csv = os.path.join(temp_dir, f"import_{target_name}.csv")
        with open(ue4loc_csv, 'w', encoding='utf-8-sig', newline='\r\n') as outfile:
            writer = csv.writer(outfile, lineterminator='\r\n')
            writer.writerow(["key", "source", "target"])
            writer.writerows(rows)
            
        # Find base locres file for this target
        import glob
        pattern = os.path.join(base_locres_dir, "**", f"{target_name}.locres")
        found_bases = glob.glob(pattern, recursive=True)
        if not found_bases:
            print(f"Warning: Could not find base locres for {target_name} in {base_locres_dir}. Skipping.")
            continue
            
        base_locres = found_bases[0]
        
        # Determine the relative path to mount properly
        # E.g. base_locres is ...\U01\Content\Localization\StoryLevel_L0\en\StoryLevel_L0.locres
        # We need to construct U01\Content\Localization\StoryLevel_L0\en inside temp_dir
        rel_path_part = base_locres.split("01_Original_Backup\\")[-1] 
        build_locres_dir = os.path.join(temp_dir, os.path.dirname(rel_path_part))
        os.makedirs(build_locres_dir, exist_ok=True)
        
        out_locres = os.path.join(build_locres_dir, f"{target_name}.locres")
        temp_base_locres = os.path.join(build_locres_dir, f"{target_name}.locres.base")
        shutil.copy2(base_locres, temp_base_locres)
        
        cmd = [UNREAL_LOCRES_TOOL, "import", temp_base_locres, ue4loc_csv]
        result = subprocess.run(cmd, cwd=build_locres_dir, capture_output=True, text=True)
        
        generated_new_locres = temp_base_locres + ".new"
        if result.returncode != 0 or not os.path.exists(generated_new_locres):
            print(f"Error during locres import for {target_name}:\n{result.stderr}\n{result.stdout}")
            continue
            
        os.rename(generated_new_locres, out_locres)
        os.remove(temp_base_locres)

    print("Step 3: Setting up UMG Font Spoofing structure...")
    for rel_path in FONT_OVERRIDES:
        full_dest = os.path.join(temp_dir, rel_path)
        os.makedirs(os.path.dirname(full_dest), exist_ok=True)
        shutil.copy2(thai_font_path, full_dest)

    print("Step 4: Packing mod with repak...")
    os.makedirs(os.path.dirname(os.path.abspath(output_pak)), exist_ok=True)
    
    cmd_repak = [REPAK_TOOL, "pack", temp_dir, output_pak, "--mount-point", "../../../", "--version", "V11"]
    result_repak = subprocess.run(cmd_repak, capture_output=True, text=True)
    
    if result_repak.returncode != 0:
        print(f"Error packing mod:\n{result_repak.stderr}")
        sys.exit(1)

    print(f"Success! Mod successfully built at: {output_pak}")
    
    try:
        shutil.rmtree(temp_dir)
    except:
        pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pack TStudio CSV and Thai font into a playable Outpost pak mod")
    parser.add_argument("--csv", required=True, help="Path to TStudio translated CSV")
    parser.add_argument("--base-locres-dir", required=True, help="Path to Original Backup root directory containing locres files")
    parser.add_argument("--thai-font", required=True, help="Path to the Thai TTF font to be injected")
    parser.add_argument("--output-pak", required=True, help="Path to the output .pak file")
    
    args = parser.parse_args()
    pack_mod(args.csv, args.base_locres_dir, args.thai_font, args.output_pak)

