"""
MetroExodus_lng_tool.py v3 - CLI tool for Metro Exodus .lng files
Bypasses the Exodus SDK entirely.

Usage:
  python MetroExodus_lng_tool.py unpack <input.lng> <output.csv>
  python MetroExodus_lng_tool.py pack <original.lng> <translations.csv> <output.lng> [--mapping mapping.json]
  python MetroExodus_lng_tool.py search <input.lng> <keyword>
  python MetroExodus_lng_tool.py replace <input.lng> <output.lng> <search_text> <replace_text>

Format: [header(20B)][char_table(N*2B)][entries...]
Entry: [encoded_value][0x00][ascii_key][0x00]
NOTE: Key-value pairs in .lng are SCRAMBLED by the compiler. 
      The game uses an internal hash map for lookup, so sequential 
      key-value pairs in the file do NOT correspond to each other logically.
      This tool matches entries by searching for VALUE text, not by key.
"""

import struct
import csv
import json
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

class MetroLngFile:
    def __init__(self):
        self.header = [0, 4, 0, 1, 0]
        self.entries = []  # list of (decoded_value_str, key_str)
    
    def load(self, filepath):
        with open(filepath, 'rb') as f:
            data = f.read()
        
        self.header = list(struct.unpack_from('<5I', data, 0))
        num_chars = self.header[4]
        
        char_table = []
        for i in range(num_chars):
            ch = struct.unpack_from('<H', data, 20 + i * 2)[0]
            char_table.append(ch)
        
        char_table_end = 20 + num_chars * 2
        
        self.entries = []
        offset = char_table_end
        
        while offset < len(data) - 1:
            val_start = offset
            while offset < len(data) and data[offset] != 0x00:
                offset += 1
            encoded_value = data[val_start:offset]
            offset += 1
            
            if offset >= len(data):
                break
            
            key_start = offset
            while offset < len(data) and data[offset] != 0x00:
                offset += 1
            key = data[key_start:offset].decode('ascii', errors='replace')
            offset += 1
            
            # Decode using original char_table
            decoded = ''.join(chr(char_table[b]) if b < len(char_table) else f'[{b}]' for b in encoded_value)
            self.entries.append((decoded, key))
        
        return len(self.entries)
    
    def save(self, filepath):
        # 1. Rebuild char table dynamically from all used characters
        used_chars = set()
        for value, key in self.entries:
            for ch in value:
                used_chars.add(ord(ch))
        
        char_table = sorted(list(used_chars))
        if len(char_table) > 255:
            print(f'[WARNING] Char table exceeds 255 limit ({len(char_table)} chars). Text may be truncated/corrupted.')
        
        reverse = {cp: idx for idx, cp in enumerate(char_table)}
        
        # 2. Write out
        out = bytearray()
        header = list(self.header)
        header[4] = len(char_table)
        out += struct.pack('<5I', *header)
        
        for cp in char_table:
            out += struct.pack('<H', cp)
        
        for value, key in self.entries:
            # Encode value using new char table
            encoded_value = bytearray()
            for ch in value:
                idx = reverse.get(ord(ch), 0)
                if idx > 255: idx = 0  # clamp
                encoded_value.append(idx)
            
            out += encoded_value
            out += b'\x00'
            out += key.encode('ascii', errors='replace')
            out += b'\x00'
        
        with open(filepath, 'wb') as f:
            f.write(out)
        
        print(f'[*] Rebuilt char table with {len(char_table)} unique characters.')
        return len(out)
    
    def to_csv(self, filepath):
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'original', 'translation'])
            for value, key in self.entries:
                writer.writerow([key, value, value])
        return len(self.entries)
    
    def replace_by_value(self, search_text, replace_text):
        count = 0
        new_entries = []
        for value, key in self.entries:
            if value == search_text:
                new_entries.append((replace_text, key))
                count += 1
                print(f'  Replaced: [{key}] "{search_text}" -> "{replace_text}"')
            else:
                new_entries.append((value, key))
        self.entries = new_entries
        return count
    
    def apply_translations_by_value(self, csv_filepath, mapping_json=None):
        pua_map = {}
        if mapping_json and os.path.exists(mapping_json):
            with open(mapping_json, 'r', encoding='utf-8') as f:
                pua_map = json.load(f)
            print(f'[*] Loaded PUA mapping with {len(pua_map)} entries')
        
        translations = {}
        with open(csv_filepath, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                orig = row.get('original', '').strip()
                trans = row.get('translation', '').strip()
                if orig and trans and orig != trans:
                    translations[orig] = trans
        
        print(f'[*] Loaded {len(translations)} unique translations')
        
        if pua_map:
            sorted_keys = sorted(pua_map.keys(), key=lambda x: len(x), reverse=True)
            for orig in translations:
                text = translations[orig]
                for pk in sorted_keys:
                    if pk in text:
                        text = text.replace(pk, pua_map[pk])
                translations[orig] = text
        
        updated = 0
        new_entries = []
        for value, key in self.entries:
            if value in translations:
                new_entries.append((translations[value], key))
                updated += 1
            else:
                new_entries.append((value, key))
        self.entries = new_entries
        print(f'[+] Updated {updated} entries')
        return updated
    
    def search(self, keyword):
        results = []
        kw_lower = keyword.lower()
        for value, key in self.entries:
            if kw_lower in key.lower() or kw_lower in value.lower():
                results.append((key, value))
        return results


def cmd_unpack(args):
    if len(args) < 2:
        print('Usage: python MetroExodus_lng_tool.py unpack <input.lng> <output.csv>')
        return
    lng = MetroLngFile()
    count = lng.load(args[0])
    print(f'[*] Loaded {count} entries from {args[0]}')
    exported = lng.to_csv(args[1])
    print(f'[+] Exported {exported} entries to {args[1]}')


def cmd_pack(args):
    if len(args) < 3:
        print('Usage: python MetroExodus_lng_tool.py pack <original.lng> <translations.csv> <output.lng> [--mapping mapping.json]')
        return
    mapping = None
    for i, a in enumerate(args):
        if a == '--mapping' and i + 1 < len(args):
            mapping = args[i + 1]
    
    lng = MetroLngFile()
    count = lng.load(args[0])
    print(f'[*] Loaded {count} entries from {args[0]}')
    
    updated = lng.apply_translations_by_value(args[1], mapping)
    
    size = lng.save(args[2])
    print(f'[+] Saved {size} bytes to {args[2]}')


def cmd_search(args):
    if len(args) < 2:
        print('Usage: python MetroExodus_lng_tool.py search <input.lng> <keyword>')
        return
    lng = MetroLngFile()
    count = lng.load(args[0])
    print(f'[*] Loaded {count} entries')
    results = lng.search(args[1])
    print(f'[*] Found {len(results)} matches for "{args[1]}":')
    for key, value in results:
        val_preview = value[:120].replace('\n', '\\n')
        print(f'  [{key}] = "{val_preview}"')


def cmd_replace(args):
    if len(args) < 4:
        print('Usage: python MetroExodus_lng_tool.py replace <input.lng> <output.lng> <search_text> <replace_text>')
        return
    lng = MetroLngFile()
    count = lng.load(args[0])
    print(f'[*] Loaded {count} entries from {args[0]}')
    
    replaced = lng.replace_by_value(args[2], args[3])
    print(f'[*] Replaced {replaced} entries')
    
    size = lng.save(args[1])
    print(f'[+] Saved {size} bytes to {args[1]}')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('=== Metro Exodus LNG Tool v3 (CLI) ===')
        print('Commands:')
        print('  unpack   <input.lng> <output.csv>')
        print('  pack     <original.lng> <translations.csv> <output.lng> [--mapping mapping.json]')
        print('  search   <input.lng> <keyword>')
        print('  replace  <input.lng> <output.lng> <search_text> <replace_text>')
        sys.exit(1)
    
    cmd = sys.argv[1]
    if cmd == 'unpack':
        cmd_unpack(sys.argv[2:])
    elif cmd == 'pack':
        cmd_pack(sys.argv[2:])
    elif cmd == 'search':
        cmd_search(sys.argv[2:])
    elif cmd == 'replace':
        cmd_replace(sys.argv[2:])
    else:
        print(f'Unknown command: {cmd}')
