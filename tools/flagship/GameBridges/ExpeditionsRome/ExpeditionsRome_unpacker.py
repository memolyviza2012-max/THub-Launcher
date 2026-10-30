import os
import sys
import subprocess
import csv

UNREAL_LOCRES_PATH = r"E:\Mod_Workspace\Tool\UnrealLocres.exe"

def unpack_locres(locres_path):
    if not os.path.exists(locres_path):
        print(f"Error: File not found - {locres_path}")
        return

    base_dir = os.path.dirname(locres_path)
    base_name = os.path.splitext(os.path.basename(locres_path))[0]
    
    temp_csv = os.path.join(base_dir, f"{base_name}_temp.csv")
    tstudio_csv = os.path.join(base_dir, f"{base_name}.csv")

    # 1. Export using UnrealLocres
    print(f"Exporting {locres_path} using UnrealLocres...")
    cmd = [UNREAL_LOCRES_PATH, "export", locres_path, "-o", temp_csv]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running UnrealLocres: {result.stderr}")
        return

    # 2. Convert to TStudio format
    print("Converting to TStudio CSV format...")
    entries = []
    try:
        with open(temp_csv, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader) # Skip header
            for row in reader:
                if len(row) >= 2:
                    key = row[0]
                    source = row[1]
                    translated = row[2] if len(row) > 2 else ""
                    entries.append([key, source, translated, ""])
    except Exception as e:
        print(f"Failed to read exported CSV: {e}")
        return

    with open(tstudio_csv, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Source", "Translation", "AI_Reference"])
        writer.writerows(entries)

    # Cleanup temp file
    if os.path.exists(temp_csv):
        os.remove(temp_csv)

    print(f"Success! TStudio compatible file created at: {tstudio_csv}")
    print("You can now open this file in TStudio.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ExpeditionsRome_unpacker.py <path_to_locres>")
    else:
        unpack_locres(sys.argv[1])
