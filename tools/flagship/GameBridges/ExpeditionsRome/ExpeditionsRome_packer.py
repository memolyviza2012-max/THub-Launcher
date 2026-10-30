import os
import sys
import subprocess
import csv

UNREAL_LOCRES_PATH = r"E:\Mod_Workspace\Tool\UnrealLocres.exe"

def pack_locres(tstudio_csv_path, original_locres_path):
    if not os.path.exists(tstudio_csv_path):
        print(f"Error: File not found - {tstudio_csv_path}")
        return
    if not os.path.exists(original_locres_path):
        print(f"Error: Original locres file not found (needed for injection) - {original_locres_path}")
        return

    base_dir = os.path.dirname(tstudio_csv_path)
    base_name = os.path.splitext(os.path.basename(tstudio_csv_path))[0]
    # Remove '_translated' suffix if it exists to get original name
    if base_name.endswith('_translated'):
        out_base_name = base_name[:-11]
    else:
        out_base_name = base_name
        
    temp_csv = os.path.join(base_dir, f"{out_base_name}_temp.csv")
    new_locres = os.path.join(base_dir, f"{out_base_name}_Thai.locres")

    # 1. Read TStudio CSV and write UnrealLocres CSV format
    print("Converting TStudio CSV back to UnrealLocres format...")
    try:
        entries = []
        with open(tstudio_csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            header = next(reader, None)
            for row in reader:
                key = row[0] if len(row) > 0 else ""
                source = row[1] if len(row) > 1 else ""
                translated = row[2] if len(row) > 2 else ""
                if not translated:
                    translated = source # Fallback to source if empty
                entries.append([key, source, translated])
                
        with open(temp_csv, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Key", "SourceString", "TranslatedString"])
            writer.writerows(entries)
    except Exception as e:
        print(f"Failed to process CSV: {e}")
        return

    # 2. Pack using UnrealLocres
    print(f"Packing into {new_locres}...")
    cmd = [UNREAL_LOCRES_PATH, "import", original_locres_path, temp_csv, "-o", new_locres]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error running UnrealLocres: {result.stderr}")
    else:
        print(f"Success! New locres created at: {new_locres}")

    # Cleanup temp file
    if os.path.exists(temp_csv):
        os.remove(temp_csv)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python ExpeditionsRome_packer.py <path_to_translated_csv> <path_to_original_locres>")
    else:
        pack_locres(sys.argv[1], sys.argv[2])
