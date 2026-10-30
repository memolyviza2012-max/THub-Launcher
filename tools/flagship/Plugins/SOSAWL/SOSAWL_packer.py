import os
import struct
import csv
import lz4.block

def pack_dcmp(orig_bin_path, csv_dir, out_bin_path):
    with open(orig_bin_path, 'rb') as f:
        orig_data = f.read()
        
    file_count = struct.unpack('<H', orig_data[0:2])[0]
    
    out_dir_data = bytearray(orig_data[:4]) # Keep header
    out_files_data = bytearray()
    
    current_file_offset = 4 + (file_count * 64)
    
    for i in range(file_count):
        entry_offset = 4 + (i * 64)
        name = orig_data[entry_offset+12:entry_offset+60].split(b'\x00')[0].decode('ascii')
        
        orig_file_offset = struct.unpack('<I', orig_data[entry_offset:entry_offset+4])[0]
        orig_file_size = struct.unpack('<I', orig_data[entry_offset+4:entry_offset+8])[0]
        
        csv_path = os.path.join(csv_dir, name.replace('.bin', '.csv'))
        
        if not os.path.exists(csv_path):
            print(f"Warning: {csv_path} not found. Using original file data.")
            new_file_data = orig_data[orig_file_offset:orig_file_offset+orig_file_size]
        else:
            # Read CSV
            entries = []
            with open(csv_path, 'r', encoding='utf-8-sig', newline='') as f:
                reader = csv.reader(f)
                header = next(reader, None)
                for row in reader:
                    if len(row) >= 3:
                        key = row[0]
                        orig_val = row[1]
                        trans_val = row[2]
                        # Use Translation if available, else use Original
                        val = trans_val if trans_val.strip() else orig_val
                        entries.append((key, val))
                    elif len(row) >= 2:
                        entries.append((row[0], row[1]))
                        
            # Rebuild file
            # Header size: len(entries) * 16
            header_size = len(entries) * 16
            
            structs_data = bytearray()
            strings_data = bytearray()
            
            # To match the game's formatting closely, we'll store all Values, then all Keys, or just append them sequentially.
            # We'll just append them as we go to the strings_data, starting at offset = header_size
            
            # Dictionary to avoid duplicating strings
            string_pool = {}
            
            def add_string(s):
                if not s: return 0
                if s in string_pool: return string_pool[s]
                offset = header_size + len(strings_data)
                string_pool[s] = offset
                strings_data.extend(s.encode('utf-16le') + b'\x00\x00')
                return offset
                
            for key, val in entries:
                val_off = add_string(val)
                key_off = add_string(key)
                
                structs_data.extend(struct.pack('<IIII', val_off, key_off, 0, 0))
                
            new_file_data = structs_data + strings_data
            
        # Add to directory
        out_dir_data.extend(struct.pack('<I', current_file_offset))
        out_dir_data.extend(struct.pack('<I', len(new_file_data)))
        out_dir_data.extend(orig_data[entry_offset+8:entry_offset+64])
        
        out_files_data.extend(new_file_data)
        current_file_offset += len(new_file_data)
        
    with open(out_bin_path, 'wb') as f:
        f.write(out_dir_data)
        f.write(out_files_data)
        
    print(f"Packed {file_count} files into {out_bin_path}")

def compress_lzs(in_bin_path, out_lzs_path):
    with open(in_bin_path, 'rb') as f:
        data = f.read()
        
    # Standard LZ4 block compression
    compressed = lz4.block.compress(data, store_size=False)
    
    with open(out_lzs_path, 'wb') as f:
        f.write(b'\xC3\xF0\x00\x00')
        f.write(struct.pack('<I', len(data)))
        f.write(compressed)
        
    print(f"Compressed to {out_lzs_path}")

def main():
    import sys
    if len(sys.argv) < 4:
        print("Usage: python SOSAWL_packer.py [original_lzs_or_bin] [input_csv_dir] [output_lzs]")
        sys.exit(1)
        
    orig_path = sys.argv[1]
    csv_dir = sys.argv[2]
    out_lzs = sys.argv[3]
    
    # We need the original .bin to read the header structures
    temp_orig_bin = orig_path
    cleanup_temp = False
    
    if orig_path.endswith('.lzs'):
        print("Decompressing original LZS to get template...")
        temp_orig_bin = orig_path + '.dec.bin'
        cleanup_temp = True
        
        with open(orig_path, 'rb') as f:
            magic = f.read(4)
            if magic == b'\xC3\xF0\x00\x00' or magic[0] == 0xC3:
                orig_size = int.from_bytes(f.read(4), 'little')
                decomp = lz4.block.decompress(f.read(), uncompressed_size=orig_size)
                with open(temp_orig_bin, 'wb') as out_f:
                    out_f.write(decomp)
            else:
                print("Original is not LZ4, assuming it is already a BIN.")
                temp_orig_bin = orig_path
                cleanup_temp = False

    temp_new_bin = out_lzs + '.tmp.bin'
    print("Packing CSV to DCMP...")
    pack_dcmp(temp_orig_bin, csv_dir, temp_new_bin)
    
    print("Compressing DCMP to LZS...")
    compress_lzs(temp_new_bin, out_lzs)
    
    if os.path.exists(temp_new_bin):
        os.remove(temp_new_bin)
    if cleanup_temp and os.path.exists(temp_orig_bin):
        os.remove(temp_orig_bin)
        
    print("Done!")

if __name__ == '__main__':
    main()
