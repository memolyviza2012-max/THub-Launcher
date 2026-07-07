import os
import csv
import re

def convert_to_csv(filepath, parent_widget=None):
    base = os.path.splitext(filepath)[0]
    csv_out = base + '_parsed.csv'
    
    entries = []
    
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('//'):
                continue
                
            # Match Key=Value or Key: Value
            m = re.match(r'^([^=:]+)[=:](.*)$', line)
            if m:
                key = m.group(1).strip()
                val = m.group(2).strip()
                # Remove surrounding quotes if present
                if val.startswith('"') and val.endswith('"') and len(val) >= 2:
                    val = val[1:-1]
                entries.append((key, val))
            else:
                # If no key is found, just use the line index as key
                entries.append((f"line_{i}", line))
                
    if not entries:
        raise ValueError(f"No valid language strings found in {filepath}")
        
    with open(csv_out, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Source", "Translation", "AI_Reference"])
        for k, v in entries:
            writer.writerow([k, v, '', ''])
            
    return csv_out
