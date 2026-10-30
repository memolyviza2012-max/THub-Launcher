"""Unity TextMeshPro Thai Font Pipeline & Tone-Mark Elevation Tuner.

Generates character subsets from translated TStudio CSVs, applies precomposed PUA
mapping to eliminate mark clipping/detachment, tunes vertical component offsets for
Thai tone marks (U+0E48–U+0E4B), and prepares character lists for TextMeshPro FontAsset
and texture atlas generation.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Support large game string fields in CSV
csv.field_size_limit(2_147_483_647)

# Try importing fontTools
try:
    from fontTools.ttLib import TTFont
except ImportError:
    TTFont = None

# Known Thai tone mark glyph component names in standard TrueType fonts
TONE_COMPONENTS: Set[str] = {
    "uni0E48",  # MAI EK
    "uni0E49",  # MAI THO
    "uni0E4A",  # MAI TRI
    "uni0E4B",  # MAI CHATTAWA
    "glyph03656", # Variant name in some legacy fonts
    "glyph03657",
    "glyph03658",
    "glyph03659",
}

# Standard locations to locate Mapping.json
DEFAULT_MAPPING_PATHS = [
    Path(os.path.dirname(os.path.abspath(__file__))) / "mapping.json",
    Path(os.path.dirname(os.path.abspath(__file__))).parents[2] / "Core" / "mapping.json",
    Path(r"E:\Mod_Workspace\Tool\1_ThaiFont\ThaiFontMappingKit\Mapping.json"),
    Path(r"E:\Mod_Workspace\Tool\1_ThaiFont\Mapping.json"),
]

# Unicode Thai combining marks for audit
THAI_COMBINING_CODEPOINTS = {0x0E31} | set(range(0x0E34, 0x0E3B)) | set(range(0x0E47, 0x0E4F))


def normalize_thai_text(text: str) -> str:
    """Canonicalize decomposed SARA AM (ํ + า) to precomposed ำ and NFC normalize."""
    if not text:
        return ""
    normalized = unicodedata.normalize("NFC", text)
    return normalized.replace("\u0e4d\u0e32", "\u0e33")


def normalize_rare_symbols(text: str) -> str:
    """Replaces rare/full-width characters with standard ASCII equivalents."""
    return (
        text.replace("Ⅱ", "II")
            .replace("Ⅰ", "I")
            .replace("Ⅲ", "III")
            .replace("○", "O")
            .replace("　", " ")
            .replace("└", "L")
            .replace("、", ",")
            .replace("！", "!")
            .replace("？", "?")
    )


class ThaiFontMapper:
    """Handles mapping of Thai strings into precomposed Private Use Area (PUA) glyphs."""

    def __init__(self, mapping_path: Optional[Path | str] = None):
        self.mapping_path = self._resolve_mapping_path(mapping_path)
        self.mapping: Dict[str, str] = self._load_mapping(self.mapping_path)
        self.pattern = self._build_regex_pattern(self.mapping)
        # Reverse mapping for decoding
        self.reverse_mapping = {v: k for k, v in self.mapping.items()}

    @staticmethod
    def _resolve_mapping_path(custom_path: Optional[Path | str] = None) -> Path:
        if custom_path:
            p = Path(custom_path)
            if p.is_file():
                return p
        for p in DEFAULT_MAPPING_PATHS:
            if p.is_file():
                return p
        raise FileNotFoundError(
            f"Mapping.json could not be found. Checked standard paths: {[str(p) for p in DEFAULT_MAPPING_PATHS]}"
        )

    @staticmethod
    def _load_mapping(path: Path) -> Dict[str, str]:
        with path.open("r", encoding="utf-8") as f:
            raw = json.load(f)
        mapping: Dict[str, str] = {}
        for k, v in raw.items():
            if k.startswith("_"):
                continue
            # If value is a hex string (e.g. "F700") convert to char
            if isinstance(v, str):
                if len(v) == 4 and all(c in "0123456789abcdefABCDEF" for c in v):
                    try:
                        mapping[k] = chr(int(v, 16))
                        continue
                    except ValueError:
                        pass
                mapping[k] = v
            elif isinstance(v, list) and len(v) > 0:
                # Contextual array of hex codes
                chars = []
                for h in v:
                    try:
                        chars.append(chr(int(h, 16)))
                    except (ValueError, TypeError):
                        chars.append(str(h))
                mapping[k] = "".join(chars)
        return mapping

    @staticmethod
    def _build_regex_pattern(mapping: Dict[str, str]) -> re.Pattern[str]:
        # Sort by descending length so longer composite combinations match first
        sorted_keys = sorted(mapping.keys(), key=lambda k: (-len(k), k))
        return re.compile("|".join(re.escape(k) for k in sorted_keys))

    def map_text(self, text: str) -> str:
        """Applies longest-match-first Thai PUA glyph replacement."""
        if not text:
            return ""
        normalized = normalize_rare_symbols(normalize_thai_text(text))
        return self.pattern.sub(lambda m: self.mapping[m.group(0)], normalized)

    def decode_text(self, text: str) -> str:
        """Restores PUA glyphs back to standard Unicode Thai."""
        if not text:
            return ""
        result = text
        # Longest replacement first
        for pua_char, original in sorted(self.reverse_mapping.items(), key=lambda item: -len(item[0])):
            result = result.replace(pua_char, original)
        return result


class UnityFontPipeline:
    """Orchestrates character subset generation and tone-mark vertical tuning."""

    def __init__(self, mapper: Optional[ThaiFontMapper] = None):
        self.mapper = mapper or ThaiFontMapper()

    def build_character_subset(
        self,
        csv_path: Path | str,
        include_ascii: bool = True,
        include_source_latin: bool = True
    ) -> Tuple[str, Dict[str, int]]:
        """Extracts required character set from translated CSV and encodes Thai to PUA."""
        csv_path = Path(csv_path)
        if not csv_path.is_file():
            raise FileNotFoundError(f"Translated CSV not found: {csv_path}")

        chars_set: Set[str] = set()

        # Always include printable ASCII for numbers, English, TMP tags (<color=...>), brackets, etc.
        if include_ascii:
            for cp in range(0x20, 0x7F):
                chars_set.add(chr(cp))

        translated_rows = 0
        total_rows = 0

        with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                total_rows += 1
                trans = (row.get("translation") or "").strip()
                source = (row.get("source") or "").strip()

                if trans:
                    translated_rows += 1
                    mapped = self.mapper.map_text(trans)
                    chars_set.update(mapped)
                elif include_source_latin and source:
                    # Fallback to source characters if unlocalized
                    chars_set.update(source)

        # Sort: ASCII first, then standard Thai, then PUA
        def sort_key(ch: str) -> Tuple[int, int]:
            cp = ord(ch)
            if cp < 0x80:
                tier = 0
            elif 0x0E00 <= cp <= 0x0E7F:
                tier = 1
            elif 0xF000 <= cp <= 0xF8FF:
                tier = 2
            else:
                tier = 3
            return (tier, cp)

        ordered_chars = "".join(sorted(chars_set, key=sort_key))

        stats = {
            "total_rows": total_rows,
            "translated_rows": translated_rows,
            "unique_characters": len(ordered_chars),
            "ascii_characters": sum(1 for c in ordered_chars if ord(c) < 0x80),
            "thai_standard_characters": sum(1 for c in ordered_chars if 0x0E00 <= ord(c) <= 0x0E7F),
            "pua_characters": sum(1 for c in ordered_chars if 0xF000 <= ord(c) <= 0xF8FF),
        }
        return ordered_chars, stats

    @staticmethod
    def tune_tone_marks(
        input_font_path: Path | str,
        output_font_path: Path | str,
        raise_units: int = 160
    ) -> Dict[str, Any]:
        """Raises vertical component offset for Thai tone marks in PUA composite glyphs.
        
        Preserves base consonants, lower vowels, and standard ASCII intact.
        """
        if TTFont is None:
            raise RuntimeError(
                "fontTools package is required for tone mark tuning. Run: pip install fonttools"
            )

        input_p = Path(input_font_path)
        output_p = Path(output_font_path)
        if not input_p.is_file():
            raise FileNotFoundError(f"Input font not found: {input_p}")

        font = TTFont(str(input_p))
        if "glyf" not in font:
            raise ValueError(f"Font {input_p.name} does not have a TrueType 'glyf' table (CFF/OTF not supported for component offset editing).")

        glyf = font["glyf"]
        cmap = font.getBestCmap()
        if not cmap:
            raise ValueError(f"Font {input_p.name} has no valid Unicode cmap table.")

        changed_glyphs = 0
        changed_components = 0

        # Scan all glyphs in PUA range (0xF000 - 0xF89F)
        for codepoint, glyph_name in cmap.items():
            if not (0xF000 <= codepoint <= 0xF8FF):
                continue
            if glyph_name not in glyf:
                continue

            glyph = glyf[glyph_name]
            if not glyph.isComposite():
                continue

            glyph_modified = False
            for comp in glyph.components:
                # Check if component is a tone mark
                if comp.glyphName in TONE_COMPONENTS:
                    comp.y += raise_units
                    glyph_modified = True
                    changed_components += 1

            if glyph_modified:
                changed_glyphs += 1

        output_p.parent.mkdir(parents=True, exist_ok=True)
        font.save(str(output_p))

        return {
            "input_font": str(input_p),
            "output_font": str(output_p),
            "raise_units": raise_units,
            "changed_pua_glyphs": changed_glyphs,
            "changed_tone_components": changed_components
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="Unity TextMeshPro Thai Font Pipeline.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: subset
    p_subset = subparsers.add_parser("subset", help="Build unique character set from translated CSV.")
    p_subset.add_argument("csv", type=Path, help="Translated TStudio CSV")
    p_subset.add_argument("-o", "--output", type=Path, required=True, help="Output characters.txt file")
    p_subset.add_argument("--mapping", type=Path, help="Optional custom Mapping.json path")

    # Subcommand: tune
    p_tune = subparsers.add_parser("tune", help="Raise Thai tone marks in PUA composite glyphs.")
    p_tune.add_argument("font", type=Path, help="Input TTF font file")
    p_tune.add_argument("-o", "--output", type=Path, required=True, help="Output shifted TTF font file")
    p_tune.add_argument("--raise-units", type=int, default=160, help="Vertical raise offset in font units (default: 160)")

    args = parser.parse_args()

    if args.command == "subset":
        mapper = ThaiFontMapper(args.mapping)
        pipeline = UnityFontPipeline(mapper)
        charset, stats = pipeline.build_character_subset(args.csv)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(charset, encoding="utf-8", newline="")
        print(f"[FontPipeline] Wrote {len(charset):,} unique characters to {args.output}")
        for k, v in stats.items():
            print(f"  {k}: {v:,}")

    elif args.command == "tune":
        print(f"[FontPipeline] Tuning tone marks with vertical offset +{args.raise_units}...")
        results = UnityFontPipeline.tune_tone_marks(args.font, args.output, args.raise_units)
        print(f"[FontPipeline] Successfully created: {results['output_font']}")
        print(f"  Changed PUA composite glyphs: {results['changed_pua_glyphs']}")
        print(f"  Changed tone components: {results['changed_tone_components']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
