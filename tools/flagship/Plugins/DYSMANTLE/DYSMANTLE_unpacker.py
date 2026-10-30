import xml.etree.ElementTree as ET
import csv
import sys
import os

def unpack_xml(input_xml):
    if not os.path.exists(input_xml):
        print(f"Error: Could not find {input_xml}")
        sys.exit(1)

    output_csv = os.path.splitext(input_xml)[0] + "_translation.csv"
    
    print(f"Parsing {input_xml}...")
    try:
        tree = ET.parse(input_xml)
        root = tree.getroot()
    except Exception as e:
        print(f"Error parsing XML: {e}")
        sys.exit(1)

    nodes = root.findall(".//node")
    if not nodes:
        print("Error: No <node> tags found in the XML.")
        sys.exit(1)

    rows = []
    for node in nodes:
        node_id = node.get("id", "")
        # Original text is stored in the 'to' attribute in the English file
        source_text = node.get("to", "")
        
        # We skip nodes that don't have text to translate
        if not source_text:
            continue
            
        rows.append([node_id, source_text, "", ""])
        
    print(f"Extracted {len(rows)} translatable strings.")
    
    with open(output_csv, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Source", "Translation", "AI_Reference"])
        writer.writerows(rows)
        
    print(f"Successfully exported to: {output_csv}")
    print("You can now open this CSV in TStudio or TRun for translation.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python DYSMANTLE_unpacker.py <path_to_language.xml>")
        sys.exit(1)
        
    unpack_xml(sys.argv[1])
