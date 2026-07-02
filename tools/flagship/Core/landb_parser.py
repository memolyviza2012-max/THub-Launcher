import struct
import os
import csv

class LandbParser:
    """
    Experimental parser for Telltale .landb files.
    Reads binary strings and reconstructs the file.
    Supports merging multiple .landb files into one CSV.
    """
    
    @staticmethod
    def extract_to_csv(landb_paths, csv_path):
        if isinstance(landb_paths, str):
            landb_paths = [landb_paths]
            
        all_strings = []
        for landb_path in landb_paths:
            base_name = os.path.basename(landb_path)
            with open(landb_path, 'rb') as f:
                data = f.read()

            i = 0
            while i < len(data) - 4:
                length = struct.unpack('<I', data[i:i+4])[0]
                if 0 < length < 5000 and i + 4 + length <= len(data):
                    text_bytes = data[i+4 : i+4+length]
                    try:
                        text = text_bytes.decode('utf-8')
                        if sum(1 for c in text if c.isprintable() or c in '\n\r\t') > len(text) * 0.9:
                            if len(text.strip()) > 0:
                                all_strings.append({
                                    'offset': f"{base_name}:{i}",
                                    'length': length,
                                    'original_text': text
                                })
                                i += 4 + length - 1
                    except UnicodeDecodeError:
                        pass
                i += 1
            
        # Write to CSV
        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Offset', 'Original', 'Translation'])
            for s in all_strings:
                writer.writerow([s['offset'], s['original_text'], ''])
                
        return len(all_strings)

    @staticmethod
    def pack_from_csv(csv_path, input_dir):
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            translations = list(reader)
            
        # Group by file_name
        grouped = {}
        for row in translations:
            translated = row['Translation'].strip()
            if not translated:
                continue
                
            offset_str = row['Offset']
            if ':' in offset_str:
                file_name, offset = offset_str.split(':')
            else:
                # Fallback for old single-file format (if any)
                file_name = os.path.basename(input_dir) # hacky fallback
                offset = offset_str
                
            offset = int(offset)
            if file_name not in grouped:
                grouped[file_name] = []
            grouped[file_name].append({'offset': offset, 'translated': translated})
            
        # Process each file
        for file_name, items in grouped.items():
            landb_path = os.path.join(input_dir, file_name)
            if not os.path.exists(landb_path):
                print(f"Warning: {landb_path} not found for packing.")
                continue
                
            with open(landb_path, 'rb') as f:
                data = bytearray(f.read())
                
            # Sort from back to front
            items.sort(key=lambda x: x['offset'], reverse=True)
            
            for item in items:
                offset = item['offset']
                translated = item['translated']
                
                orig_len = struct.unpack('<I', data[offset:offset+4])[0]
                new_bytes = translated.encode('utf-8')
                new_len = len(new_bytes)
                
                # Replace length
                data[offset:offset+4] = struct.pack('<I', new_len)
                # Replace string bytes
                data[offset+4 : offset+4+orig_len] = new_bytes
                
            with open(landb_path, 'wb') as f:
                f.write(data)
                
        return True
