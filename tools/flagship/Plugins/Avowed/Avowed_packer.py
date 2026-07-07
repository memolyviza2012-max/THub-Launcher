import os
import sys
import subprocess
import csv
import shutil

def pack_locres(input_csv, original_locres, output_locres):
    # Path to UnrealLocres
    unreal_locres_exe = r"E:\Mod_Workspace\Tool\UnrealLocres.exe"
    
    if not os.path.exists(unreal_locres_exe):
        print(f"Error: {unreal_locres_exe} not found.")
        sys.exit(1)
        
    temp_csv = output_locres + ".temp.csv"
    
    # 1. Convert from TStudio Format to UnrealLocres format
    # TStudio CSV format: ID, Original, Translation, Context
    # UnrealLocres CSV format: key, source, target
    print("[*] Converting from TStudio CSV to UnrealLocres format...")
    
    with open(input_csv, 'r', encoding='utf-8-sig') as infile, open(temp_csv, 'w', encoding='utf-8-sig', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        
        # Read header
        header = next(reader, None)
        
        # Write UnrealLocres header
        writer.writerow(["key", "source", "target"])
        
        for row in reader:
            if len(row) >= 3:
                key = row[0]
                source = row[1]
                target = row[2]
                
                # Use source if target is empty
                if not target.strip():
                    target = source
                    
                writer.writerow([key, source, target])
                
    # 2. Import using UnrealLocres
    print("[*] Packing into .locres...")
    # unrealLocres import syntax: import <LocresInputPath> <TranslationInputPath> -f csv -o <Output>
    cmd = [unreal_locres_exe, "import", original_locres, temp_csv, "-f", "csv", "-o", output_locres]
    print(f"[*] Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    
    # Clean up temp
    if os.path.exists(temp_csv):
        os.remove(temp_csv)
        
    print(f"[+] Successfully packed translated {output_locres}")
    print("\nNext steps:")
    print("1. Pack the new .locres into a .utoc/.ucas using UnrealReZen")
    print("2. Create a dummy .pak file")
    print("3. Install to Avowed/Alabama/Content/Paks/~mods")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python Avowed_packer.py <input_tstudio_csv> <original_locres> <output_locres>")
        sys.exit(1)
        
    pack_locres(sys.argv[1], sys.argv[2], sys.argv[3])
