import os
import csv
import json
import re

def parse_as_srt(filepath, raw_text, parent_widget=None):
    base = os.path.splitext(filepath)[0]
    csv_out = base + '_parsed.csv'
    meta_out = base + '_parsed_meta.json'
    
    entries = []
    meta_data = {}
    
    blocks = re.split(r'\n\s*\n', raw_text.strip())
    
    for i, block in enumerate(blocks):
        lines = block.strip().split('\n')
        if len(lines) >= 3:
            idx = lines[0].strip()
            timestamp = lines[1].strip()
            text = '\n'.join(lines[2:]).strip()
            
            row_id = f"row_{idx}_{i}"
            entries.append((row_id, text))
            meta_data[row_id] = {"timestamp": timestamp}
            
    if not entries:
        raise ValueError(f"No valid SRT subtitle blocks found in {filepath}")
        
    with open(csv_out, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Source", "Translation", "AI_Reference"])
        for row_id, text in entries:
            writer.writerow([row_id, text, "", ""])
            
    with open(meta_out, 'w', encoding='utf-8') as f:
        json.dump({"original_data": meta_data}, f, ensure_ascii=False, indent=2)
        
    return csv_out

def parse_as_alien_isolation(filepath, raw_text, parent_widget=None):
    base = os.path.splitext(filepath)[0]
    csv_out = base + '_parsed.csv'
    
    entries = []
    
    # Alien Isolation format:
    # [KEY]
    # {VALUE}
    keys = re.findall(r'\[(.*?)\]', raw_text)
    values = re.findall(r'\{(.*?)\}', raw_text, re.DOTALL)
    
    if len(keys) > 0 and len(keys) == len(values):
        for i in range(len(keys)):
            entries.append((keys[i].strip(), values[i].strip()))
    
    if not entries:
        raise ValueError(f"No valid Alien: Isolation texts found in {filepath}")
        
    with open(csv_out, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Source", "Translation", "AI_Reference"])
        for key, value in entries:
            writer.writerow([key, value, "", ""])
            
    return csv_out

def convert_to_csv(filepath, parent_widget=None):
    base = os.path.splitext(filepath)[0]
    csv_out = base + '_parsed.csv'
    
    # Determine encoding by sniffing BOM
    with open(filepath, 'rb') as f:
        raw_bytes = f.read(4)
        
    if raw_bytes.startswith(b'\xff\xfe'):
        encoding = 'utf-16-le'
    elif raw_bytes.startswith(b'\xfe\xff'):
        encoding = 'utf-16-be'
    else:
        encoding = 'utf-8-sig'
        
    with open(filepath, 'r', encoding=encoding, errors='replace') as f:
        raw_text = f.read()
        
    # Heuristic 0: Is it Alien Isolation format?
    if re.search(r'^\[.*?\]\s*\n\s*\{.*?\}', raw_text, re.MULTILINE | re.DOTALL):
        # Additional check to be sure
        keys = re.findall(r'\[(.*?)\]', raw_text)
        values = re.findall(r'\{(.*?)\}', raw_text, re.DOTALL)
        if len(keys) > 0 and len(keys) == len(values):
            return parse_as_alien_isolation(filepath, raw_text, parent_widget)
        
    # Heuristic 1: Is it SRT? (Look for index followed by timestamp)
    if re.search(r'\d+\n\d{2}:\d{2}:\d{2}', raw_text):
        return parse_as_srt(filepath, raw_text, parent_widget)
        
    # Heuristic 2: Telltale format (N) Character \n Text)
    lines = raw_text.split('\n')
    id_pattern = re.compile(r'^(\d+)\)\s*(.*)')
    entries = []
    
    i = 0
    while i < len(lines):
        m = id_pattern.match(lines[i].strip())
        if m:
            line_id = m.group(1)
            character = m.group(2).strip()
            text = ''
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line and not id_pattern.match(next_line):
                    text = next_line
                    i += 1
            entries.append((line_id, character, text))
        i += 1
        
    if len(entries) >= 5:
        with open(csv_out, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Source", "Translation", "AI_Reference"])
            for (lid, char, text) in entries:
                if text:
                    row_id = f"{lid}_{char.replace(' ', '_')}" if char else str(lid)
                    writer.writerow([row_id, text, "", char])
        return csv_out
        
    raise ValueError(f"ไม่พบรูปแบบข้อความที่รองรับในไฟล์ .txt นี้ (รองรับ SRT, Telltale, หรือ Alien: Isolation)")
