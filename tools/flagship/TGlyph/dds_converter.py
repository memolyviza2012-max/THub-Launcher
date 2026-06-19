"""
dds_converter.py — PNG ↔ DDS (BC4) converter for FONT PPFS
Converts grayscale PNG to DDS BC4_UNORM format used by C-Engine (Dying Light 2).
DDS format: 148-byte header (128 standard + 20 DX10 extension) + BC4 compressed pixel data.
"""

import struct
import numpy as np
from PIL import Image
from pathlib import Path


# DDS Constants
DDS_MAGIC = 0x20534444  # "DDS "
DDSD_CAPS = 0x1
DDSD_HEIGHT = 0x2
DDSD_WIDTH = 0x4
DDSD_PIXELFORMAT = 0x1000
DDSD_LINEARSIZE = 0x80000
DDPF_FOURCC = 0x4
DDSCAPS_TEXTURE = 0x1000

# DX10 extension
DXGI_FORMAT_BC4_UNORM = 80
D3D10_RESOURCE_DIMENSION_TEXTURE2D = 3


def _compress_bc4_block(block: np.ndarray) -> bytes:
    """Compress a 4x4 block of uint8 values into 8 bytes of BC4."""
    flat = block.flatten()
    alpha0 = int(flat.max())
    alpha1 = int(flat.min())
    
    if alpha0 == alpha1:
        # All same value — encode trivially
        return struct.pack('<BB6s', alpha0, alpha1, b'\x00' * 6)
    
    # Build palette
    if alpha0 > alpha1:
        # 8-value palette (interpolated)
        palette = [alpha0, alpha1]
        for i in range(1, 7):
            palette.append(((7 - i) * alpha0 + i * alpha1 + 3) // 7)
    else:
        # 6-value palette + transparent/opaque (not used for BC4, but handle anyway)
        palette = [alpha0, alpha1]
        for i in range(1, 5):
            palette.append(((5 - i) * alpha0 + i * alpha1 + 2) // 5)
        palette.append(0)
        palette.append(255)
    
    # Find best index for each pixel
    indices = []
    for val in flat:
        best_idx = 0
        best_dist = abs(int(val) - palette[0])
        for idx, p in enumerate(palette[1:], 1):
            dist = abs(int(val) - p)
            if dist < best_dist:
                best_dist = dist
                best_idx = idx
        indices.append(best_idx)
    
    # Pack 16 indices (3 bits each) into 6 bytes (48 bits)
    bits = 0
    for i, idx in enumerate(indices):
        bits |= (idx & 0x7) << (i * 3)
    
    index_bytes = struct.pack('<Q', bits)[:6]
    return struct.pack('<BB', alpha0, alpha1) + index_bytes


def _decompress_bc4_block(data: bytes) -> np.ndarray:
    """Decompress 8 bytes of BC4 into a 4x4 block of uint8 values."""
    alpha0 = data[0]
    alpha1 = data[1]
    
    # Build palette
    if alpha0 > alpha1:
        palette = [alpha0, alpha1]
        for i in range(1, 7):
            palette.append(((7 - i) * alpha0 + i * alpha1 + 3) // 7)
    else:
        palette = [alpha0, alpha1]
        for i in range(1, 5):
            palette.append(((5 - i) * alpha0 + i * alpha1 + 2) // 5)
        palette.append(0)
        palette.append(255)
    
    # Unpack indices
    index_bits = int.from_bytes(data[2:8], 'little')
    result = np.zeros(16, dtype=np.uint8)
    for i in range(16):
        idx = (index_bits >> (i * 3)) & 0x7
        if idx < len(palette):
            result[i] = palette[idx]
        else:
            result[i] = 0
    
    return result.reshape(4, 4)


def png_to_dds_bc4(png_path: str, dds_path: str) -> None:
    """
    Convert a grayscale PNG to DDS BC4_UNORM format.
    
    Args:
        png_path: Path to input PNG file (grayscale)
        dds_path: Path to output DDS file
    """
    img = Image.open(png_path).convert('L')
    width, height = img.size
    pixels = np.array(img)
    
    # Pad to multiple of 4
    pad_h = (4 - height % 4) % 4
    pad_w = (4 - width % 4) % 4
    if pad_h > 0 or pad_w > 0:
        pixels = np.pad(pixels, ((0, pad_h), (0, pad_w)), mode='constant', constant_values=0)
    
    padded_h, padded_w = pixels.shape
    
    # Compress blocks
    blocks = []
    for by in range(0, padded_h, 4):
        for bx in range(0, padded_w, 4):
            block = pixels[by:by+4, bx:bx+4]
            blocks.append(_compress_bc4_block(block))
    
    bc4_data = b''.join(blocks)
    linear_size = len(bc4_data)
    
    # Build DDS header (128 bytes)
    header = struct.pack('<I', DDS_MAGIC)  # Magic
    header += struct.pack('<I', 124)  # Header size
    header += struct.pack('<I', DDSD_CAPS | DDSD_HEIGHT | DDSD_WIDTH | DDSD_PIXELFORMAT | DDSD_LINEARSIZE)  # Flags
    header += struct.pack('<I', height)  # Height
    header += struct.pack('<I', width)   # Width
    header += struct.pack('<I', linear_size)  # Linear size
    header += struct.pack('<I', 0)  # Depth
    header += struct.pack('<I', 0)  # Mip count
    header += b'\x00' * 44  # Reserved (11 DWORDs)
    
    # Pixel format (32 bytes)
    header += struct.pack('<I', 32)  # PF size
    header += struct.pack('<I', DDPF_FOURCC)  # PF flags
    header += b'DX10'  # FourCC
    header += struct.pack('<I', 0)  # RGB bit count
    header += struct.pack('<I', 0)  # R mask
    header += struct.pack('<I', 0)  # G mask
    header += struct.pack('<I', 0)  # B mask
    header += struct.pack('<I', 0)  # A mask
    
    # Caps
    header += struct.pack('<I', DDSCAPS_TEXTURE)  # Caps1
    header += struct.pack('<III', 0, 0, 0)  # Caps2-4
    
    # DX10 extension header (20 bytes)
    dx10 = struct.pack('<I', DXGI_FORMAT_BC4_UNORM)  # DXGI format
    dx10 += struct.pack('<I', D3D10_RESOURCE_DIMENSION_TEXTURE2D)  # Resource dimension
    dx10 += struct.pack('<I', 0)  # Misc flag
    dx10 += struct.pack('<I', 1)  # Array size
    dx10 += struct.pack('<I', 0)  # Misc flags 2
    
    with open(dds_path, 'wb') as f:
        f.write(header)
        f.write(dx10)
        f.write(bc4_data)
    
    print(f"  DDS saved: {dds_path} ({width}x{height}, {len(bc4_data)} bytes BC4)")


def dds_to_png(dds_path: str, png_path: str) -> None:
    """
    Convert a DDS BC4_UNORM file to grayscale PNG.
    
    Args:
        dds_path: Path to input DDS file
        png_path: Path to output PNG file
    """
    with open(dds_path, 'rb') as f:
        data = f.read()
    
    # Parse header
    magic = struct.unpack('<I', data[0:4])[0]
    if magic != DDS_MAGIC:
        raise ValueError(f"Not a DDS file (magic: 0x{magic:08X})")
    
    height = struct.unpack('<I', data[12:16])[0]
    width = struct.unpack('<I', data[16:20])[0]
    
    # Check for DX10 header
    fourcc = data[84:88]
    if fourcc == b'DX10':
        pixel_data_start = 148  # 128 + 20
    else:
        pixel_data_start = 128
    
    bc4_data = data[pixel_data_start:]
    
    # Decompress
    padded_w = (width + 3) // 4 * 4
    padded_h = (height + 3) // 4 * 4
    
    pixels = np.zeros((padded_h, padded_w), dtype=np.uint8)
    
    block_idx = 0
    for by in range(0, padded_h, 4):
        for bx in range(0, padded_w, 4):
            offset = block_idx * 8
            if offset + 8 <= len(bc4_data):
                block = _decompress_bc4_block(bc4_data[offset:offset+8])
                pixels[by:by+4, bx:bx+4] = block
            block_idx += 1
    
    # Crop to original size
    pixels = pixels[:height, :width]
    
    img = Image.fromarray(pixels, mode='L')
    img.save(png_path)
    print(f"  PNG saved: {png_path} ({width}x{height})")


def inject_dds_into_rpack(dds_path: str, rpack_path: str, offset: int) -> None:
    """
    Inject DDS pixel data (skipping header) into an rpack file at a specific offset.
    
    Args:
        dds_path: Path to DDS file to inject
        rpack_path: Path to rpack file to modify
        offset: Byte offset in rpack where pixel data should be written
    """
    with open(dds_path, 'rb') as f:
        data = f.read()
    
    # Skip header
    fourcc = data[84:88]
    header_size = 148 if fourcc == b'DX10' else 128
    pixel_data = data[header_size:]
    
    with open(rpack_path, 'r+b') as f:
        f.seek(offset)
        f.write(pixel_data)
    
    print(f"  Injected {len(pixel_data)} bytes into {rpack_path} at offset {offset}")


if __name__ == '__main__':
    print("DDS Converter module ready.")
    print("Use png_to_dds_bc4() to convert PNG -> DDS")
    print("Use dds_to_png() to convert DDS -> PNG")
