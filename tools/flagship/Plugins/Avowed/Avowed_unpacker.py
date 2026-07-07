import os
import sys
import subprocess
import csv

def unpack_locres(input_locres, output_csv):
    # Path to UnrealLocres
    unreal_locres_exe = r"E:\Mod_Workspace\Tool\UnrealLocres.exe"
    
    if not os.path.exists(unreal_locres_exe):
        print(f"Error: {unreal_locres_exe} not found.")
        sys.exit(1)
        
    temp_csv = input_locres + ".temp.csv"
    
    # 1. Export using UnrealLocres
    cmd = [unreal_locres_exe, "export", input_locres, "-f", "csv", "-o", temp_csv]
    print(f"[*] Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    
    # 2. Convert to TStudio Format
    # UnrealLocres CSV format: key, source, target
    # TStudio CSV format: ID, Original, Translation, Context
    print("[*] Converting to TStudio CSV format...")
    
    with open(temp_csv, 'r', encoding='utf-8-sig') as infile, open(output_csv, 'w', encoding='utf-8-sig', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        
        # Read header
        header = next(reader, None)
        
        # Write TStudio header
        writer.writerow(["ID", "Original", "Translation", "Context"])
        
        for row in reader:
            if len(row) >= 3:
                key = row[0]
                source = row[1]
                target = row[2]
                writer.writerow([key, source, target, "Avowed Text"])
                
    # Clean up temp
    if os.path.exists(temp_csv):
        os.remove(temp_csv)
        
    print(f"[+] Successfully unpacked {input_locres} to {output_csv}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python Avowed_unpacker.py <input_locres> <output_csv>")
        sys.exit(1)
        
    unpack_locres(sys.argv[1], sys.argv[2])
