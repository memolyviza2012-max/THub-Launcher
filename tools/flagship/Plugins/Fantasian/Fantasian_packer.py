import os
import sys
import csv
import json

def pack_fantasian_json(input_csv, original_json, output_json=None):
    if not output_json:
        output_json = os.path.splitext(original_json)[0] + "_patched.json"

    print(f"Loading translations from {input_csv}...")
    translations = {}
    with open(input_csv, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = row.get("ID", "").strip()
            translation = row.get("Translation", "").strip()
            source = row.get("Source", "").strip()
            if key:
                translations[key] = translation if translation else source
                
    if not translations:
        print("Error: No translations found in CSV.")
        return False

    print(f"Loading JSON bundle {original_json}...")
    with open(original_json, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    modified_count = 0
    
    if 'original_tree' in data and 'messageDictionary' in data['original_tree']:
        entries = data['original_tree']['messageDictionary'].get('entries', [])
        
        for entry in entries:
            key = entry.get('key', '')
            if key in translations:
                val_dict = entry.get('value', {})
                original_msg = val_dict.get('Message', '')
                new_msg = translations[key]
                
                if original_msg != new_msg:
                    entry['value']['Message'] = new_msg
                    modified_count += 1
    else:
        print("Error: Invalid JSON structure. Missing original_tree or messageDictionary.")
        return False
                    
    if modified_count == 0:
        print("Warning: No strings were replaced. Did the IDs match?")
    else:
        print(f"Replaced {modified_count} strings.")
        print(f"Saving to {output_json}...")
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("Successfully saved!")
        
    return True

if __name__ == '__main__':
    print("--- Fantasian Packer (JSON Mode) ---")
    if len(sys.argv) < 3:
        print("Usage: python Fantasian_packer.py <translated.csv> <original_meta.json> [output_meta.json]")
        sys.exit(1)
        
    input_csv = sys.argv[1]
    original_json = sys.argv[2]
    output_json = sys.argv[3] if len(sys.argv) > 3 else None
    
    if not os.path.exists(input_csv):
        print(f"File not found: {input_csv}")
        sys.exit(1)
        
    if not os.path.exists(original_json):
        print(f"File not found: {original_json}")
        sys.exit(1)
        
    pack_fantasian_json(input_csv, original_json, output_json)
