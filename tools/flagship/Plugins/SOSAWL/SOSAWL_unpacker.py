import os
import struct
import csv
import lz4.block

def decompress_lzs(in_path, out_path):
    with open(in_path, 'rb') as f:
        magic = f.read(4)
        if magic != b'\xC3\xF0\x00\x00' and magic[0] != 0xC3:
            print("Not LZ4 Block format, assuming uncompressed DCMP.")
            f.seek(0)
            data = f.read()
            with open(out_path, 'wb') as out_f:
                out_f.write(data)
            return True
            
        orig_size = int.from_bytes(f.read(4), 'little')
        compressed_data = f.read()
        try:
            decomp = lz4.block.decompress(compressed_data, uncompressed_size=orig_size)
            with open(out_path, 'wb') as out_f:
                out_f.write(decomp)
            return True
        except Exception as e:
            print(f"LZ4 Decompression error: {e}")
            return False

def extract_string(data, offset):
    if offset == 0 or offset >= len(data):
        return ""
    end = data.find(b'\x00\x00', offset)
    if end == -1:
        end = len(data)
    # Ensure even length for UTF-16
    if (end - offset) % 2 != 0:
        end += 1
    return data[offset:end].decode('utf-16le', errors='ignore').strip('\x00')

def unpack_dcmp(in_path, out_csv_dir):
    os.makedirs(out_csv_dir, exist_ok=True)
    
    with open(in_path, 'rb') as f:
        data = f.read()
        
    file_count = struct.unpack('<H', data[0:2])[0]
    
    for i in range(file_count):
        entry_offset = 4 + (i * 64)
        file_offset = struct.unpack('<I', data[entry_offset:entry_offset+4])[0]
        file_size = struct.unpack('<I', data[entry_offset+4:entry_offset+8])[0]
        name = data[entry_offset+12:entry_offset+60].split(b'\x00')[0].decode('ascii')
        
        file_data = data[file_offset:file_offset+file_size]
        
        # Parse the message file
        # Format: Array of 16-byte structs: (Value_Offset, Key_Offset, Unk1, Unk2)
        
        strings = []
        
        if len(file_data) >= 16:
            first_offset = struct.unpack('<I', file_data[0:4])[0]
            second_offset = struct.unpack('<I', file_data[4:8])[0]
            
            min_offset = len(file_data)
            if 0 < first_offset < min_offset: min_offset = first_offset
            if 0 < second_offset < min_offset: min_offset = second_offset
            
            entry_count = min_offset // 16
            
            for j in range(entry_count):
                val_off, key_off, unk1, unk2 = struct.unpack('<IIII', file_data[j*16:j*16+16])
                
                key = extract_string(file_data, key_off)
                val = extract_string(file_data, val_off)
                
                if key or val:
                    strings.append((key, val))
                    
        if strings:
            csv_path = os.path.join(out_csv_dir, name.replace('.bin', '.csv'))
            with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Key', 'Original', 'Translation'])
                for k, v in strings:
                    writer.writerow([k, v, ""])
                    
    print(f"Extracted {file_count} files to {out_csv_dir}")

def main():
    import sys
    if len(sys.argv) < 3:
        print("Usage: python SOSAWL_unpacker.py [input_lzs_or_bin] [output_csv_dir]")
        sys.exit(1)
        
    in_path = sys.argv[1]
    out_dir = sys.argv[2]
    
    if in_path.endswith('.lzs'):
        temp_bin = in_path + '.dec.bin'
        print("Decompressing LZS...")
        if decompress_lzs(in_path, temp_bin):
            print("Unpacking DCMP to CSV...")
            unpack_dcmp(temp_bin, out_dir)
            if os.path.exists(temp_bin):
                os.remove(temp_bin)
    else:
        print("Unpacking DCMP to CSV...")
        unpack_dcmp(in_path, out_dir)

if __name__ == '__main__':
    main()
