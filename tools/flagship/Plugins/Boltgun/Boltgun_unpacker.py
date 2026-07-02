import sys
import os
import csv

try:
    import pylocres
except ImportError:
    print("Error: pylocres is not installed. Please install it using 'pip install pylocres'")
    sys.exit(1)

def unpack_locres(input_file, output_csv):
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        return

    print(f"Loading {input_file}...")
    locres = pylocres.LocresFile()
    try:
        locres.read(input_file)
    except Exception as e:
        print(f"Failed to read locres file: {e}")
        return

    rows = []
    for ns_key, ns in locres.namespaces.items():
        for str_key, entry in ns.entrys.items():
            if entry.translation is not None:
                row_id = f"{ns_key}::{str_key}"
                source_text = entry.translation
                rows.append([row_id, source_text, "", ""])

    os.makedirs(os.path.dirname(output_csv) if os.path.dirname(output_csv) else '.', exist_ok=True)
    
    with open(output_csv, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Source", "Translation", "AI_Reference"])
        writer.writerows(rows)

    print(f"Successfully unpacked {len(rows)} strings to '{output_csv}'")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python Boltgun_unpacker.py <input.locres> <output.csv>")
        sys.exit(1)
        
    unpack_locres(sys.argv[1], sys.argv[2])
