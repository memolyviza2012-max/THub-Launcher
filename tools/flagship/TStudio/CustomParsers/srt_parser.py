import os
import csv
import json
import re

def convert_to_csv(filepath, parent_widget=None):
    base = os.path.splitext(filepath)[0]
    csv_out = base + '_parsed.csv'
    meta_out = base + '_parsed_meta.json'
    
    entries = []
    meta_data = {}
    
    with open(filepath, 'r', encoding='utf-8-sig', errors='replace') as f:
        content = f.read()
        
    # Split by double newline (blocks)
    blocks = re.split(r'\n\s*\n', content.strip())
    
    for i, block in enumerate(blocks):
        lines = block.strip().split('\n')
        if len(lines) >= 3:
            # line 0: index
            # line 1: timestamp
            # line 2+: text
            idx = lines[0].strip()
            timestamp = lines[1].strip()
            text = '\n'.join(lines[2:]).strip()
            
            row_id = f"row_{idx}_{i}"
            entries.append((row_id, text))
            meta_data[row_id] = {"timestamp": timestamp}
            
    if not entries:
        raise ValueError(f"No valid SRT subtitle blocks found in {filepath}")
        
    # Write CSV
    with open(csv_out, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        # Assuming header columns for TStudio: ID, Source, Translation, AI_Reference
        writer.writerow(["ID", "Source", "Translation", "AI_Reference"])
        for row_id, text in entries:
            writer.writerow([row_id, text, "", ""])
            
    # Write Meta JSON for TVox
    with open(meta_out, 'w', encoding='utf-8') as f:
        json.dump({"original_data": meta_data}, f, ensure_ascii=False, indent=2)
        
    return csv_out
