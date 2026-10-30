#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Retrofit CLI: Zero-Token Terminology & Keyboard Key Repair Tool
--------------------------------------------------------------
Scans translated game files (CSV, JSON, etc.) and automatically fixes:
1. Keyboard & Controller inputs (Spacebar, Enter, Backspace, Keypad, Mouse, etc.)
2. Firearms & Real-world military nomenclature (M16, AK-47, RPG-7, SMG, etc.)
3. Sci-Fi & Futuristic weapon terms (Railgun, Plasma, Pulse Rifle, etc.)
4. Dynamic alphanumeric model codes (B-2, D-7, MG-46, Mk.IV, X-99, etc.)

Zero API token cost, 100% offline, with automatic backup.
"""

import sys
import os
import argparse
import csv
import json
import shutil

# Add Core to path
_DIR = os.path.dirname(os.path.abspath(__file__))
_CORE_DIR = os.path.abspath(os.path.join(_DIR, "..", "Core"))
if _CORE_DIR not in sys.path:
    sys.path.insert(0, _CORE_DIR)

try:
    from tstudio_core import TStudioCore
except ImportError:
    print("[ERROR] Could not import TStudioCore. Ensure tstudio_core.py exists in tools/flagship/Core/")
    sys.exit(1)


def repair_csv(file_path, options, preview=False, create_backup=True):
    with open(file_path, 'r', encoding='utf-8-sig', errors='replace', newline='') as f:
        reader = list(csv.reader(f))

    if not reader:
        print(f"[!] File is empty: {file_path}")
        return 0

    header = reader[0]
    rows = reader[1:]

    # Detect column indices
    src_idx = 1
    trans_idx = 2
    for idx, col_name in enumerate(header):
        low = col_name.lower().strip()
        if low in ['source', 'english', 'src', 'original', 'text']:
            src_idx = idx
        elif low in ['translation', 'thai', 'trans', 'target']:
            trans_idx = idx

    print(f"[*] Detected Columns: Source = '{header[src_idx]}' (col {src_idx}), Translation = '{header[trans_idx]}' (col {trans_idx})")

    changed_records = []
    for row_num, row in enumerate(rows, start=2):
        if len(row) > max(src_idx, trans_idx):
            src = row[src_idx]
            trans = row[trans_idx]
            new_trans, changes = TStudioCore.retrofit_military_text(src, trans, options=options)
            if changes:
                changed_records.append((row_num, row[0] if len(row) > 0 else f"Row {row_num}", src, trans, new_trans, changes))
                if not preview:
                    row[trans_idx] = new_trans

    if not changed_records:
        print(f"[OK] No terms need retrofitting in {file_path} (Already 100% clean).")
        return 0

    print(f"\n[+] Found {len(changed_records)} rows requiring repair:")
    print("-" * 90)
    for rec in changed_records[:35]:
        row_id = rec[1][:25]
        print(f"Line {rec[0]:4d} [{row_id}]:")
        print(f"   SRC  : {rec[2][:65]}")
        print(f"   OLD  : {rec[3][:65]}")
        print(f"   FIXED: {rec[4][:65]}")
        rules_str = ", ".join([c[2] for c in rec[5]])
        print(f"   RULES: {rules_str}")
    if len(changed_records) > 35:
        print(f"   ... and {len(changed_records) - 35} more rows.")
    print("-" * 90)

    if preview:
        print(f"[PREVIEW ONLY] No changes were written to {file_path}.")
        return len(changed_records)

    if create_backup:
        bak_path = file_path + ".bak"
        shutil.copyfile(file_path, bak_path)
        print(f"[*] Backup created: {bak_path}")

    with open(file_path, 'w', encoding='utf-8-sig', errors='replace', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)

    print(f"[SUCCESS] Successfully updated {len(changed_records)} rows in: {file_path}")
    return len(changed_records)


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description="TStudio Zero-Token Terminology & Keyboard Key Retrofit CLI")
    parser.add_argument("file", nargs="?", help="Path to CSV / translation file to retrofit")
    parser.add_argument("--keys-only", action="store_true", help="Only fix keyboard keys, keypad numbers, mouse controls")
    parser.add_argument("--preview", action="store_true", help="Dry run: show what would change without modifying file")
    parser.add_argument("--no-backup", action="store_true", help="Skip creating .bak backup file")

    args = parser.parse_args()

    target_file = args.file
    if not target_file:
        print("=" * 80)
        print("  🎖️ TStudio Zero-Token Retrofit CLI (Keyboard Keys & Military Terms)")
        print("=" * 80)
        target_file = input("Enter path to CSV file (or drag & drop here): ").strip().strip('"').strip("'")
        if not target_file:
            print("[!] No file provided. Exiting.")
            sys.exit(0)

    if not os.path.exists(target_file):
        print(f"[ERROR] File not found: {target_file}")
        sys.exit(1)

    if args.keys_only:
        opts = {
            'model_codes': False,
            'scifi': False,
            'weapons': False,
            'acronyms': False,
            'vehicles': False,
            'calibers': False,
            'keys': True
        }
    else:
        opts = {
            'model_codes': True,
            'scifi': True,
            'weapons': True,
            'acronyms': True,
            'vehicles': True,
            'calibers': True,
            'keys': True
        }

    repair_csv(target_file, opts, preview=args.preview, create_backup=not args.no_backup)


if __name__ == "__main__":
    main()
