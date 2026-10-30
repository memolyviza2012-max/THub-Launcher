#!/usr/bin/env python3
"""Export a Remnant 2 UE5 .locres file to Modder Hub's standard TStudio CSV."""
import argparse
import csv
import struct
from pathlib import Path

HEADERS = ["ID", "Source", "Translation", "AI_Reference"]


def read_locres_strings(path: Path) -> list[str]:
    """Read UE locres string-array entries without using UnrealLocres.exe.

    The original byte sequence is not changed here; this only exports text.
    """
    with path.open("rb") as handle:
        header = handle.read(25)  # magic (16), version (1), string-array offset (8)
        if len(header) != 25:
            raise ValueError("Not a valid UE locres file: header is too short.")
        offset = int.from_bytes(header[17:25], "little")
        if offset < 25 or offset >= path.stat().st_size:
            raise ValueError(f"Invalid locres string-array offset: {offset}")
        handle.seek(offset)
        count_bytes = handle.read(4)
        if len(count_bytes) != 4:
            raise ValueError("The locres string-array count is missing.")
        count = struct.unpack("<I", count_bytes)[0]
        values = []
        for index in range(count):
            raw_length = handle.read(4)
            if len(raw_length) != 4:
                raise ValueError(f"Truncated string length at entry {index}.")
            length = struct.unpack("<i", raw_length)[0]
            if length == 0:
                value = ""
            elif length > 0:
                data = handle.read(length)
                if len(data) != length:
                    raise ValueError(f"Truncated ANSI string at entry {index}.")
                value = data[:-1].decode("utf-8", errors="replace")
            else:
                byte_length = -length * 2
                data = handle.read(byte_length)
                if len(data) != byte_length:
                    raise ValueError(f"Truncated UTF-16 string at entry {index}.")
                value = data[:-2].decode("utf-16-le", errors="replace")
            # Every string array entry ends with its reference count.
            if len(handle.read(4)) != 4:
                raise ValueError(f"Truncated reference count at entry {index}.")
            values.append(value)
    return values


def export_to_tstudio(locres: Path, output: Path) -> None:
    strings = read_locres_strings(locres)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(HEADERS)
        for index, source in enumerate(strings):
            # Keep duplicates: UE references a shared string table, and TStudio's
            # row count then matches the source locres exactly for review/auditing.
            writer.writerow([f"locres-string-{index:06d}", source, "", ""])
    unique = len(set(strings))
    print(f"Exported {len(strings):,} rows ({unique:,} unique strings) to: {output}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("locres", type=Path, help="Original Remnant2.locres, never a previously translated copy.")
    parser.add_argument("--output", type=Path, help="Default: <locres stem>_TStudio.csv")
    args = parser.parse_args()
    if not args.locres.is_file():
        parser.error(f"File not found: {args.locres}")
    output = args.output or args.locres.with_name(args.locres.stem + "_TStudio.csv")
    export_to_tstudio(args.locres, output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
