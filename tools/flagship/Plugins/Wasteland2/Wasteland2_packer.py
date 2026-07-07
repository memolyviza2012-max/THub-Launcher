import os
import csv
import sys

def pack_csv_to_txt(input_csv, original_txt, output_txt):
    """
    Packs a TStudio translated CSV back into the Wasteland 2 TXT format,
    maintaining all original comments and formatting.
    """
    translations = {}
    
    with open(input_csv, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = row.get("ID", "").strip()
            translation = row.get("Translation", "").strip()
            source = row.get("Source", "").strip()
            
            if key:
                # Use translation if available, otherwise fallback to source
                translations[key] = translation if translation else source

    if not translations:
        print(f"Error: No translations found in {input_csv}")
        return False
        
    with open(original_txt, 'r', encoding='utf-16') as f:
        lines = f.readlines()
        
    new_lines = []
    current_key = None
    replaced_count = 0
    
    for line in lines:
        if line.startswith('#'):
            current_key = line.rstrip('\r\n')
            new_lines.append(line)
        elif line.startswith('=') and current_key is not None:
            if current_key in translations:
                # Ensure we handle multiline translations by keeping it simple
                # Wasteland 2 values are single line in the file
                val = translations[current_key].replace('\n', ' ')
                new_lines.append(f"={val}\n")
                replaced_count += 1
            else:
                new_lines.append(line) # Keep original if not in CSV
            current_key = None
        else:
            new_lines.append(line)
            
    with open(output_txt, 'w', encoding='utf-16') as f:
        f.writelines(new_lines)
        
    print(f"Successfully packed {replaced_count} translated strings to {output_txt}")
    return True

if __name__ == "__main__":
    print("--- Wasteland 2 Packer ---")
    if len(sys.argv) < 3:
        print("Usage: python Wasteland2_packer.py <translated.csv> <original.txt> [output.txt]")
        sys.exit(1)
        
    input_csv = sys.argv[1]
    original_txt = sys.argv[2]
    
    if len(sys.argv) >= 4:
        output_txt = sys.argv[3]
    else:
        output_txt = os.path.splitext(original_txt)[0] + "_patched.txt"
        
    if not os.path.exists(input_csv):
        print(f"File not found: {input_csv}")
        sys.exit(1)
        
    if not os.path.exists(original_txt):
        print(f"File not found: {original_txt}")
        sys.exit(1)
        
    pack_csv_to_txt(input_csv, original_txt, output_txt)
