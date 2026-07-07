import os
import csv
import sys

def unpack_txt_to_csv(input_txt, output_csv):
    """
    Unpacks a Wasteland 2 localization TXT file into a TStudio CSV format.
    """
    entries = []
    
    with open(input_txt, 'r', encoding='utf-16') as f:
        lines = f.readlines()
        
    current_key = None
    
    for line in lines:
        # We use lstrip to handle potential leading spaces, but usually they start exactly at index 0.
        # We don't want to lose trailing spaces if they exist in the value, but standard split handles \n.
        if line.startswith('*') or not line.strip():
            continue
            
        if line.startswith('#'):
            current_key = line.rstrip('\r\n')
        elif line.startswith('=') and current_key is not None:
            source_text = line[1:].rstrip('\r\n') # remove '=' and newline
            entries.append((current_key, source_text))
            current_key = None # reset for next pair
            
    if not entries:
        print(f"No valid #Key and =Value pairs found in {input_txt}")
        return False
        
    with open(output_csv, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Source", "Translation", "AI_Reference"])
        for key, source in entries:
            writer.writerow([key, source, "", ""])
            
    print(f"Successfully unpacked {len(entries)} strings to {output_csv}")
    return True

if __name__ == "__main__":
    print("--- Wasteland 2 Unpacker ---")
    if len(sys.argv) < 2:
        print("Usage: python Wasteland2_unpacker.py <input.txt> [output.csv]")
        sys.exit(1)
        
    input_file = sys.argv[1]
    
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        output_file = os.path.splitext(input_file)[0] + "_tstudio.csv"
        
    if not os.path.exists(input_file):
        print(f"File not found: {input_file}")
        sys.exit(1)
        
    unpack_txt_to_csv(input_file, output_file)
