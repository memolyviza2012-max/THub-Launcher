import csv
import sys
import os

def migrate(old_translated_csv, new_input_csv, output_merged_csv):
    translations = {}
    print(f"Reading old translated CSV: {old_translated_csv}")
    try:
        with open(old_translated_csv, 'r', encoding='utf-8-sig', errors='replace') as f:
            reader = csv.reader(f)
            headers = next(reader, None)
            for row in reader:
                if len(row) < 3:
                    continue
                old_id = row[0]
                # old_id format: Namespace,Key::Hash
                # new format: Namespace/Key
                if "::" in old_id:
                    old_id = old_id.split("::")[0]
                old_id = old_id.replace(",", "/")
                
                trans = row[2]
                if trans.strip():
                    translations[old_id] = trans
    except Exception as e:
        print(f"Error reading old CSV: {e}")
        sys.exit(1)
        
    print(f"Loaded {len(translations)} translated lines.")
    
    merged_rows = []
    print(f"Reading new multi-target CSV: {new_input_csv}")
    matched_count = 0
    try:
        with open(new_input_csv, 'r', encoding='utf-8-sig', errors='replace') as f:
            reader = csv.reader(f)
            headers = next(reader, None)
            for row in reader:
                if len(row) < 2:
                    continue
                new_id = row[0]
                source = row[1]
                trans = row[2] if len(row) > 2 else ""
                
                parts = new_id.split("||", 1)
                base_id = parts[1] if len(parts) == 2 else new_id
                
                if base_id in translations:
                    trans = translations[base_id]
                    matched_count += 1
                    
                merged_rows.append([new_id, source, trans, ""])
                
    except Exception as e:
        print(f"Error reading new CSV: {e}")
        sys.exit(1)
        
    print(f"Matched and injected {matched_count} translations.")
    
    print(f"Writing merged CSV to {output_merged_csv}")
    try:
        with open(output_merged_csv, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Source", "Translation", "AI_Reference"])
            writer.writerows(merged_rows)
    except Exception as e:
        print(f"Error writing merged CSV: {e}")
        sys.exit(1)
        
    print("Migration complete!")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python migrate_translations.py <old_translated.csv> <new_input.csv> <output.csv>")
        sys.exit(1)
    migrate(sys.argv[1], sys.argv[2], sys.argv[3])
