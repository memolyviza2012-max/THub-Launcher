import struct
import os
import csv
import re

# =====================================================================
# landb_parser.py - TStudio Plugin for Telltale .landb files
# Handles: Telltale Walking Dead, Wolf Among Us, GOTG, etc.
# Format: Binary file with length-prefixed UTF-8 strings
# =====================================================================

PLUGIN_NAME = "Telltale LangDB Parser"
SUPPORTED_EXTENSIONS = [".landb"]

def _detect_and_read_landb(filepath):
    """
    Read a .landb file and extract all text strings.
    Returns list of (offset_id, text) tuples.
    """
    entries = []
    base_name = os.path.basename(filepath)

    with open(filepath, 'rb') as f:
        data = f.read()

    i = 0
    seen_offsets = set()
    while i < len(data) - 4:
        try:
            length = struct.unpack('<I', data[i:i+4])[0]
        except struct.error:
            i += 1
            continue

        # Plausible string length: 1 to 4096 bytes
        if 1 <= length <= 4096 and i + 4 + length <= len(data):
            text_bytes = data[i+4: i+4+length]
            try:
                text = text_bytes.decode('utf-8')
                # Check if text looks like a real sentence (printable ratio)
                printable_ratio = sum(1 for c in text if c.isprintable() or c in '\n\r\t') / len(text)
                # Must have at least one letter/space and be > 90% printable
                has_content = any(c.isalpha() or c == ' ' for c in text)
                if printable_ratio > 0.90 and has_content and len(text.strip()) > 0:
                    offset_id = f"{base_name}:{i}"
                    if offset_id not in seen_offsets:
                        seen_offsets.add(offset_id)
                        entries.append((offset_id, text.strip()))
                    i += 4 + length - 1  # Jump past this string
            except UnicodeDecodeError:
                pass
        i += 1

    return entries


def convert_to_csv(filepath, parent_widget=None):
    """
    Main entry point called by TStudio when opening a .landb file.
    """
    base = os.path.splitext(filepath)[0]
    csv_out = base + '_parsed.csv'

    entries = _detect_and_read_landb(filepath)

    if not entries:
        raise ValueError(
            f"ไม่พบข้อความในไฟล์ .landb นี้\n"
            f"อาจเป็นไฟล์ที่ไม่มีข้อความ หรือโครงสร้างไม่รองรับ"
        )

    with open(csv_out, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Source", "Translation", "AI_Reference"])
        for offset_id, text in entries:
            writer.writerow([offset_id, text, "", ""])

    return csv_out
