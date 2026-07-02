import argparse
import subprocess
import os
import csv
import sys
import glob

UNREAL_LOCRES_TOOL = r"E:\Mod_Workspace\Tool\UnrealLocres.exe"

def unpack_locres_dir(locres_dir, output_csv):
    if not os.path.exists(UNREAL_LOCRES_TOOL):
        print(f"Error: UnrealLocres not found at {UNREAL_LOCRES_TOOL}")
        sys.exit(1)

    if not os.path.exists(locres_dir):
        print(f"Error: Locres directory not found at {locres_dir}")
        sys.exit(1)

    tstudio_rows = []
    
    # Find all en/*.locres files
    pattern = os.path.join(locres_dir, "**", "en", "*.locres")
    locres_files = glob.glob(pattern, recursive=True)
    
    if not locres_files:
        print(f"Error: No en/*.locres files found in {locres_dir}")
        sys.exit(1)
        
    for locres_path in locres_files:
        print(f"Processing: {locres_path}")
        target_name = os.path.basename(locres_path).replace('.locres', '')
        
        # 1. Export using UnrealLocres to a CSV
        cmd = [UNREAL_LOCRES_TOOL, "export", locres_path]
        result = subprocess.run(cmd, cwd=os.path.dirname(locres_path), capture_output=True, text=True)
        
        temp_csv = locres_path.replace('.locres', '.csv')
        if not os.path.exists(temp_csv):
            print(f"Warning: Temporary CSV was not generated at {temp_csv}, skipping...")
            continue

        # 2. Read the exported CSV and convert to TStudio format
        try:
            with open(temp_csv, 'r', encoding='utf-8-sig', errors='replace') as f:
                reader = csv.reader(f)
                headers = next(reader, None)
                
                for row in reader:
                    if len(row) < 2:
                        continue
                    key = row[0]
                    source = row[1]
                    
                    # PREFIX WITH TARGET
                    combined_id = f"{target_name}||{key}"
                    
                    translation = ""
                    if len(row) >= 3:
                        translation = row[2]
                        
                    tstudio_rows.append([combined_id, source, translation, ""])
                    
        except Exception as e:
            print(f"Error parsing temporary CSV {temp_csv}: {e}")
        
        # Clean up temp file
        try:
            os.remove(temp_csv)
        except:
            pass

    # 3. Write out the TStudio formatted CSV
    try:
        os.makedirs(os.path.dirname(os.path.abspath(output_csv)), exist_ok=True)
        with open(output_csv, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Source", "Translation", "AI_Reference"])
            writer.writerows(tstudio_rows)
            
        print(f"Successfully generated TStudio input file at: {output_csv}")
        print(f"Total lines extracted: {len(tstudio_rows)}")
    except Exception as e:
        print(f"Error writing output CSV: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Unpack Outpost Infinity Siege locres to TStudio CSV format")
    parser.add_argument("--locres-dir", required=True, help="Path to Original Backup Localization directory")
    parser.add_argument("--output", required=True, help="Path to output TStudio_Input.csv")
    
    args = parser.parse_args()
    
    unpack_locres_dir(args.locres_dir, args.output)
