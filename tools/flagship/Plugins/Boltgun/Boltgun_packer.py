import sys
import os
import csv

try:
    import pylocres
except ImportError:
    print("Error: pylocres is not installed. Please install it using 'pip install pylocres'")
    sys.exit(1)

def pack_locres(original_locres, translated_csv, output_locres):
    if not os.path.exists(original_locres):
        print(f"Error: Original locres file '{original_locres}' not found.")
        return
    if not os.path.exists(translated_csv):
        print(f"Error: Translated CSV file '{translated_csv}' not found.")
        return

    # 1. Read translated CSV
    print(f"Reading translations from {translated_csv}...")
    translations = {}
    try:
        with open(translated_csv, 'r', encoding='utf-8-sig', errors='replace') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Standard TStudio format has "ID" and "Translation"
                row_id = row.get("ID", "").strip()
                translated_text = row.get("Translation", "")
                # Only use translation if it is not empty
                if row_id and translated_text:
                    translations[row_id] = translated_text
    except Exception as e:
        print(f"Failed to read CSV: {e}")
        return

    print(f"Loaded {len(translations)} translated strings.")

    # 2. Load original Locres
    print(f"Loading original locres {original_locres}...")
    locres = pylocres.LocresFile()
    try:
        locres.read(original_locres)
    except Exception as e:
        print(f"Failed to read locres file: {e}")
        return

    # 3. Apply translations
    changed = 0
    for ns_key, ns in locres.namespaces.items():
        for str_key, entry in ns.entrys.items():
            row_id = f"{ns_key}::{str_key}"
            if row_id in translations:
                entry.translation = translations[row_id]
                changed += 1

    # 4. Save new Locres
    os.makedirs(os.path.dirname(output_locres) if os.path.dirname(output_locres) else '.', exist_ok=True)
    try:
        locres.write(output_locres)
        print(f"Successfully modified {changed} strings and saved to '{output_locres}'")
    except Exception as e:
        print(f"Failed to write output locres: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python Boltgun_packer.py <original.locres> <translated.csv> <output.locres>")
        sys.exit(1)
        
    pack_locres(sys.argv[1], sys.argv[2], sys.argv[3])
