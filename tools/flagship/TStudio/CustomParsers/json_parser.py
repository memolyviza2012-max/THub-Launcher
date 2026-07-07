import os
import csv
import json

def convert_to_csv(filepath, parent_widget=None):
    with open(filepath, 'r', encoding='utf-8') as f:
        jdata = json.load(f)
        
    entries = []
    
    # 0. Custom Unity MESG JSON
    if isinstance(jdata, dict) and "m_Script" in jdata and isinstance(jdata["m_Script"], str) and jdata["m_Script"].startswith("MESG"):
        m_script = jdata["m_Script"]
        parts = m_script.split('\u0000')
        for i, p in enumerate(parts):
            if len(p) >= 2:
                # Exclude garbage with replacement character
                if '\uFFFD' in p:
                    continue
                # Specific valid short words
                if p in ["OK", "No", "On", "Off", "Yes", "AM", "PM", "All"]:
                    entries.append((f"mesg_{i}", p))
                    continue
                # Ignore very short garbled bits
                if len(p) <= 3:
                    continue
                # Must contain at least one letter
                if not any(c.isalpha() for c in p):
                    continue
                # Must be mostly printable ASCII (or valid Thai/other characters)
                printable = sum(1 for c in p if 32 <= ord(c) < 127)
                if printable / len(p) >= 0.9:
                    entries.append((f"mesg_{i}", p))
                    
    # 1. c2dictionary (Construct 2/3)
    elif isinstance(jdata, dict) and jdata.get("c2dictionary") is True and "data" in jdata:
        for k, v in jdata["data"].items():
            entries.append((k, str(v)))
            
    # 2. Flat dict: {"key": "value"}
    elif isinstance(jdata, dict):
        for k, v in jdata.items():
            if isinstance(v, (str, int, float, bool)):
                v_str = str(v)
                # If it's a giant block of text (like corrupted binary or very long string),
                # chunk it into pieces so it "lines up" in the UI (as requested by user),
                # and allows deploying back.
                if len(v_str) > 1000:
                    chunk_size = 500
                    for i in range(0, len(v_str), chunk_size):
                        entries.append((f"{k}_part{i//chunk_size}", v_str[i:i+chunk_size]))
                else:
                    entries.append((k, v_str))
                
    # 3. List of dicts
    elif isinstance(jdata, list):
        for i, item in enumerate(jdata):
            if isinstance(item, dict):
                if "id" in item and "text" in item:
                    entries.append((str(item["id"]), str(item["text"])))
                elif "key" in item and "value" in item:
                    entries.append((str(item["key"]), str(item["value"])))
                else:
                    entries.append((f"row_{i}", json.dumps(item, ensure_ascii=False)))
            elif isinstance(item, str):
                entries.append((f"row_{i}", item))
                
    if not entries:
        raise ValueError(f"ไม่พบข้อความที่สามารถนำไปแปลได้ในไฟล์ {os.path.basename(filepath)}")
        
    base = os.path.splitext(filepath)[0]
    csv_out = base + '_parsed.csv'
    
    with open(csv_out, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        # TStudio Native Compatibility Headers
        writer.writerow(["ID", "ต้นฉบับ", "คำแปล", "AI_Reference"])
        for lid, text in entries:
            writer.writerow([lid, text, '', ''])
            
    return csv_out
