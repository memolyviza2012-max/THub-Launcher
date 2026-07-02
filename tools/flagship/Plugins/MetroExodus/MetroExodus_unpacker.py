import os
import csv
import sys

def unpack_metro_csv(input_csv, output_csv, source_lang_col="en"):
    """
    Converts an exported Metro Exodus SDK CSV into the standard TStudio CSV format.
    TStudio expects: id, original, translation
    """
    if not os.path.exists(input_csv):
        print(f"[Error] Could not find SDK Exported CSV at {input_csv}")
        return False

    print(f"[*] Unpacking Metro Exodus SDK CSV: {input_csv}")
    
    tstudio_data = []
    
    with open(input_csv, 'r', encoding='utf-8', newline='') as f:
        # Exodus SDK might use semicolon or comma. We'll use csv.Sniffer to detect
        sample = f.read(2048)
        f.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample)
        except csv.Error:
            dialect = csv.excel # fallback
            
        reader = csv.DictReader(f, dialect=dialect)
        
        # Determine key column
        key_col = None
        for col in reader.fieldnames:
            if col and col.lower().strip() in ['key', 'name', 'id', 'string_id']:
                key_col = col
                break
        
        if not key_col and reader.fieldnames:
            key_col = reader.fieldnames[0] # Fallback to first column
            
        # Determine source language column
        src_col = None
        for col in reader.fieldnames:
            if col and col.lower().strip() == source_lang_col.lower():
                src_col = col
                break
                
        if not src_col and reader.fieldnames:
            # Fallback to the second column if available
            if len(reader.fieldnames) > 1:
                src_col = reader.fieldnames[1]
            else:
                src_col = key_col

        print(f"[*] Detected Key Column: {key_col}")
        print(f"[*] Detected Source Language Column: {src_col}")
        
        for row in reader:
            key = row.get(key_col, "")
            if key is not None:
                key = key.strip()
            
            original = row.get(src_col, "")
            if original is not None:
                original = original.strip()
            
            if key:
                tstudio_data.append({
                    'id': key,
                    'original': original,
                    'translation': original # Init with original
                })
                
    # Write to TStudio format
    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'original', 'translation'])
        writer.writeheader()
        writer.writerows(tstudio_data)
        
    print(f"[+] Successfully unpacked {len(tstudio_data)} strings into {output_csv}")
    return True

if __name__ == "__main__":
    print("=== Metro Exodus Unpacker for TStudio ===")
    if len(sys.argv) < 3:
        print("Usage: python MetroExodus_unpacker.py <input_sdk.csv> <output_tstudio.csv> [source_lang_col]")
        sys.exit(1)
        
    in_file = sys.argv[1]
    out_file = sys.argv[2]
    lang = sys.argv[3] if len(sys.argv) > 3 else "en"
    
    unpack_metro_csv(in_file, out_file, lang)
