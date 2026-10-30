import json
import xml.etree.ElementTree as ET
import csv
import sys
import os

def load_pua_mapping(mapping_file):
    try:
        with open(mapping_file, 'r', encoding='utf-8') as f:
            mapping = json.load(f)
        # Sort keys by length descending to replace longest patterns first
        sorted_keys = sorted(mapping.keys(), key=len, reverse=True)
        return mapping, sorted_keys
    except Exception as e:
        print(f"Error loading PUA mapping: {e}")
        return None, None

def apply_pua(text, mapping, sorted_keys):
    if not text or not mapping:
        return text
    
    # Iterate through sorted keys and replace occurrences
    for k in sorted_keys:
        if k in text:
            text = text.replace(k, mapping[k])
    return text

def pack_xml(input_csv, template_xml, mapping_file):
    if not os.path.exists(input_csv):
        print(f"Error: Could not find {input_csv}")
        sys.exit(1)
    if not os.path.exists(template_xml):
        print(f"Error: Could not find template XML at {template_xml}")
        sys.exit(1)

    mapping, sorted_keys = load_pua_mapping(mapping_file)
    if not mapping:
        sys.exit(1)

    output_xml = os.path.splitext(template_xml)[0] + "_th.xml"
    
    # Load translations from CSV
    translations = {}
    print(f"Loading translations from {input_csv}...")
    try:
        with open(input_csv, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                uid = row.get("ID", "")
                trans = row.get("Translation", "").strip()
                source = row.get("Source", "").strip()
                
                # Use Translation if available, else fallback to Source
                final_text = trans if trans else source
                if uid:
                    # Apply PUA mapping to the final text
                    pua_text = apply_pua(final_text, mapping, sorted_keys)
                    translations[uid] = pua_text
    except Exception as e:
        print(f"Error reading CSV: {e}")
        sys.exit(1)
        
    print(f"Loaded {len(translations)} translation entries.")
    
    # Load and update XML
    print(f"Patching XML template {template_xml}...")
    try:
        tree = ET.parse(template_xml)
        root = tree.getroot()
        
        nodes = root.findall(".//node")
        replaced_count = 0
        for node in nodes:
            node_id = node.get("id", "")
            if node_id in translations:
                node.set("to", translations[node_id])
                replaced_count += 1
                
        # Save output
        tree.write(output_xml, encoding='utf-8', xml_declaration=True)
        print(f"Successfully packed {replaced_count} translated strings with PUA applied.")
        print(f"Saved packed XML to: {output_xml}")
        
    except Exception as e:
        print(f"Error patching XML: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python DYSMANTLE_packer.py <path_to_translation.csv> <path_to_base_language.xml> <path_to_mapping.json>")
        sys.exit(1)
        
    pack_xml(sys.argv[1], sys.argv[2], sys.argv[3])
