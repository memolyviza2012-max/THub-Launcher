#!/usr/bin/env python3
"""Inject a translated TStudio CSV into Remnant 2 locres, then optionally build/deploy its V11 pak."""
import argparse
import csv
import shutil
import subprocess
import sys
from pathlib import Path

GAME_ROOT = Path(r"E:\Mod_Workspace\Remnant2")
INJECTOR = GAME_ROOT / "translate_locres.py"  # Required Thai-safe UTF-16LE writer.
REPAK = Path(r"E:\Mod_Workspace\Tool\repak_cli\repak.exe")
BUILD_ROOT = GAME_ROOT / "04_Build"
GAME_MODS = Path(r"F:\SteamLibrary\steamapps\common\Remnant2\Remnant2\Content\Paks\~mods")


def column_index(headers: list[str], expected: str) -> int:
    for index, header in enumerate(headers):
        if header.strip().casefold() == expected.casefold():
            return index
    raise ValueError(f"TStudio CSV is missing the required '{expected}' column.")


def make_injector_csv(tstudio_csv: Path, output: Path) -> tuple[int, int]:
    """Convert standard TStudio CSV to the two columns used by translate_locres.py.

    Empty translations deliberately remain English. Conflicting translations for
    an identical source are reported because UE locres shares one string value.
    """
    with tstudio_csv.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        headers = next(reader, None)
        if not headers:
            raise ValueError("TStudio CSV is empty.")
        source_col = column_index(headers, "Source")
        translation_col = column_index(headers, "Translation")
        translations: dict[str, str] = {}
        conflicts = 0
        rows = 0
        for row in reader:
            rows += 1
            source = row[source_col] if len(row) > source_col else ""
            translation = row[translation_col] if len(row) > translation_col else ""
            if not source or not translation or translation == source:
                continue
            prior = translations.get(source)
            if prior is not None and prior != translation:
                conflicts += 1
                continue  # deterministic: keep the first reviewed translation
            translations[source] = translation
    with output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["source", "translation"])
        writer.writeheader()
        writer.writerows({"source": source, "translation": translation} for source, translation in translations.items())
    return len(translations), conflicts


def run(command: list[str]) -> None:
    print("+", subprocess.list2cmdline(command))
    subprocess.run(command, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tstudio_csv", type=Path, help="CSV saved by TStudio/TRun with ID,Source,Translation,AI_Reference columns.")
    parser.add_argument("original_locres", type=Path, help="Pristine English Remnant2.locres.")
    parser.add_argument("--output", type=Path, help="Output locres; default is Remnant2_Thai.locres beside the CSV.")
    parser.add_argument("--build-pak", action="store_true", help="Copy locres to the build tree and create pakchunk99-Windows_P.pak (V11).")
    parser.add_argument("--deploy", action="store_true", help="Copy the built pak to Remnant2/Content/Paks/~mods (implies --build-pak).")
    args = parser.parse_args()
    if not args.tstudio_csv.is_file() or not args.original_locres.is_file():
        parser.error("Both the TStudio CSV and original locres must exist.")
    if not INJECTOR.is_file():
        parser.error(f"Thai-safe injector not found: {INJECTOR}")
    output = args.output or args.tstudio_csv.with_name("Remnant2_Thai.locres")
    bridge_csv = args.tstudio_csv.with_name(args.tstudio_csv.stem + "_for_locres.csv")
    translated, conflicts = make_injector_csv(args.tstudio_csv, bridge_csv)
    print(f"Prepared {translated:,} unique translated strings for injection.")
    if conflicts:
        print(f"Warning: {conflicts:,} duplicate-source conflicts; retained the first translation for each source.")
    run([sys.executable, str(INJECTOR), str(args.original_locres), str(bridge_csv), str(output)])
    if not (args.build_pak or args.deploy):
        print(f"Created locres: {output}")
        return 0
    if not REPAK.is_file():
        parser.error(f"repak.exe not found: {REPAK}")
    staged = BUILD_ROOT / "Remnant2" / "Content" / "Localization" / "Remnant2" / "en" / "Remnant2.locres"
    staged.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(output, staged)
    pak = BUILD_ROOT / "pakchunk99-Windows_P.pak"
    if pak.exists():
        pak.unlink()
    run([str(REPAK), "pack", "--version", "V11", "--mount-point", "../../../", str(BUILD_ROOT), str(pak)])
    if not pak.is_file() or pak.stat().st_size < 1024:
        raise RuntimeError("RePak did not produce a valid pak file.")
    if args.deploy:
        GAME_MODS.mkdir(parents=True, exist_ok=True)
        destination = GAME_MODS / pak.name
        shutil.copy2(pak, destination)
        print(f"Deployed: {destination}")
    else:
        print(f"Created pak: {pak}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
