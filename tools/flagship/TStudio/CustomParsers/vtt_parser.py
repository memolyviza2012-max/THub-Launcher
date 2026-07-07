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
        
    # Remove WEBVTT header if present
    if content.startswith('WEBVTT'):
        content = content.replace('WEBVTT', '', 1).strip()
        
    blocks = re.split(r'\n\s*\n', content.strip())
    
    block_index = 1
    for i, block in enumerate(blocks):
        lines = block.strip().split('\n')
        if not lines: continue
        
        # Check if first line is timestamp or ID
        if '-->' in lines[0]:
            timestamp = lines[0].strip()
            text = '\n'.join(lines[1:]).strip()
            idx = str(block_index)
            block_index += 1
        elif len(lines) >= 2 and '-->' in lines[1]:
            idx = lines[0].strip()
            timestamp = lines[1].strip()
            text = '\n'.join(lines[2:]).strip()
        else:
            continue # Skip non-subtitle blocks like NOTE
            
        if text:
            # VTT uses . instead of , for milliseconds. We can normalize to , for internal TVox if needed
            timestamp = timestamp.replace('.', ',')
            row_id = f"vtt_{idx}_{i}"
            entries.append((row_id, text))
            meta_data[row_id] = {"timestamp": timestamp}
            
    if not entries:
        raise ValueError(f"No valid VTT subtitle blocks found in {filepath}")
        
    with open(csv_out, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Source", "Translation", "AI_Reference"])
        for row_id, text in entries:
            writer.writerow([row_id, text, "", ""])
            
    with open(meta_out, 'w', encoding='utf-8') as f:
        json.dump({"original_data": meta_data}, f, ensure_ascii=False, indent=2)
        
    return csv_out
