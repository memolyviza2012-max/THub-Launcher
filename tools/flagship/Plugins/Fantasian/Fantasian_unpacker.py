import os
import sys
import csv
import json

def unpack_fantasian_json(input_json, output_csv=None):
    if not output_csv:
        output_csv = os.path.splitext(input_json)[0] + ".csv"

    print(f"Loading {input_json}...")
    with open(input_json, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    extracted = []
    
    # Check if it's the expected Fantasian format
    if 'original_tree' in data and 'messageDictionary' in data['original_tree']:
        entries = data['original_tree']['messageDictionary'].get('entries', [])
        for entry in entries:
            key = entry.get('key', '')
            val_dict = entry.get('value', {})
            message = val_dict.get('Message', '')
            if key and message:
                extracted.append([key, message, "", ""])
    else:
        print("Error: Invalid JSON structure. Missing original_tree or messageDictionary.")
        return False
                    
    if not extracted:
        print("Error: No messageDictionary entries found in this file.")
        return False
        
    print(f"Extracted {len(extracted)} translation strings.")
    
    with open(output_csv, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Source", "Translation", "AI_Reference"])
        for row in extracted:
            writer.writerow(row)
            
    print(f"Successfully saved to {output_csv}")
    return True

if __name__ == '__main__':
    print("--- Fantasian Unpacker (JSON Mode) ---")
    if len(sys.argv) < 2:
        print("Usage: python Fantasian_unpacker.py <input_meta.json> [output.csv]")
        sys.exit(1)
        
    input_file = sys.argv[1]
    output_csv = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(input_file):
        print(f"File not found: {input_file}")
        sys.exit(1)
        
    unpack_fantasian_json(input_file, output_csv)
