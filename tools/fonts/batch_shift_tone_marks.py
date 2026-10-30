#!/usr/bin/env python3
"""
Batch Shift Tone Marks (+160 units)
===================================
Lifts Thai tone marks (วรรณยุกต์: ่ ้ ๊ ๋ ์) by +160 units
to prevent collisions and overlapping with upper vowels (ั, ิ, ี, ึ, ื, ็, ํ).

Handles:
- Base Unicode tone marks: 0x0E48, 0x0E49, 0x0E4A, 0x0E4B, 0x0E4C
- Suffix variants in glyf: .small, .alt, .shift, .up
- Font metrics adjustment: OS/2.usWinAscent and hhea.ascent
"""

import os
import sys
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates

TARGET_UNICODES = {
    0x0E48,  # MAI EK (่)
    0x0E49,  # MAI THO (้)
    0x0E4A,  # MAI TRI (๊)
    0x0E4B,  # MAI CHATTAWA (๋)
    0x0E4C,  # THANTHAKHAT (์)
}

SUFFIX_PATTERNS = ['.small', '.alt', '.shift', '.up', 'small', 'alt', 'shift', 'up']
SHIFT_Y = 160


def shift_font_tone_marks(font_path, shift_y=SHIFT_Y, backup=False):
    """Shifts all tone marks up by shift_y units."""
    try:
        font = TTFont(font_path)
    except Exception as e:
        return False, f"Cannot open font: {e}"

    if 'glyf' not in font:
        return False, "Not a TrueType font with glyf table (skipping CFF/OTF)"

    glyf = font['glyf']
    cmap = font.getBestCmap()
    if not cmap:
        return False, "No cmap found"

    # Identify target glyph names from cmap
    target_names = set()
    base_tone_names = set()
    for cp, gname in cmap.items():
        if cp in TARGET_UNICODES and gname in glyf:
            target_names.add(gname)
            base_tone_names.add(gname)

    # Also identify tone variants in glyf (e.g. uni0E48.small, etc.)
    for base_name in base_tone_names:
        for suffix in SUFFIX_PATTERNS:
            candidate = f"{base_name}{suffix}"
            if candidate in glyf:
                target_names.add(candidate)

    if not target_names:
        return False, "No Thai tone marks found in font"

    shifted_count = 0
    max_shifted_ymax = -9999

    for gname in target_names:
        g = glyf[gname]
        g.expand(glyf)

        if hasattr(g, 'coordinates') and g.coordinates:
            g.coordinates = GlyphCoordinates([(x, y + shift_y) for x, y in g.coordinates])
            if hasattr(g, 'yMin'):
                g.yMin += shift_y
            if hasattr(g, 'yMax'):
                g.yMax += shift_y
            g.recalcBounds(glyf)
            shifted_count += 1
            if hasattr(g, 'yMax') and g.yMax > max_shifted_ymax:
                max_shifted_ymax = g.yMax

        elif g.isComposite():
            for comp in g.components:
                comp.y += shift_y
            if hasattr(g, 'yMin'):
                g.yMin += shift_y
            if hasattr(g, 'yMax'):
                g.yMax += shift_y
            g.recalcBounds(glyf)
            shifted_count += 1
            if hasattr(g, 'yMax') and g.yMax > max_shifted_ymax:
                max_shifted_ymax = g.yMax

    # Safety check on vertical bounds to prevent OS / engine font clipping
    adjusted_metrics = False
    if max_shifted_ymax > 0:
        if 'OS/2' in font:
            os2 = font['OS/2']
            if hasattr(os2, 'usWinAscent') and os2.usWinAscent < max_shifted_ymax:
                os2.usWinAscent = int(max_shifted_ymax + 10)
                adjusted_metrics = True
        if 'hhea' in font:
            hhea = font['hhea']
            if hasattr(hhea, 'ascent') and hhea.ascent < max_shifted_ymax:
                hhea.ascent = int(max_shifted_ymax + 10)
                adjusted_metrics = True

    # Save
    if backup:
        bak_path = font_path + ".bak"
        if not os.path.exists(bak_path):
            import shutil
            shutil.copy2(font_path, bak_path)

    font.save(font_path)
    font.close()
    return True, f"Shifted {shifted_count} tone glyphs by +{shift_y} (Max yMax: {max_shifted_ymax}, Metrics updated: {adjusted_metrics})"


def process_directory(directory_path, shift_y=SHIFT_Y):
    print(f"Scanning directory: {directory_path}")
    count_ok = 0
    count_skip = 0
    count_err = 0

    for root, dirs, files in os.walk(directory_path):
        for f in files:
            if f.endswith('.ttf'):
                p = os.path.join(root, f)
                rel = os.path.relpath(p, directory_path)
                ok, msg = shift_font_tone_marks(p, shift_y=shift_y)
                if ok:
                    count_ok += 1
                    print(f"  [OK] {rel:50s} -> {msg}")
                else:
                    if "Not a TrueType" in msg or "No Thai tone" in msg:
                        count_skip += 1
                        print(f"  [SKIP] {rel:50s} -> {msg}")
                    else:
                        count_err += 1
                        print(f"  [ERR] {rel:50s} -> {msg}")

    print("\n" + "=" * 60)
    print(f"Summary for {directory_path}:")
    print(f"  Processed: {count_ok} fonts")
    print(f"  Skipped:   {count_skip} fonts")
    print(f"  Errors:    {count_err} fonts")
    print("=" * 60)
    return count_ok, count_skip, count_err


if __name__ == '__main__':
    target_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'library')
    shift_val = int(sys.argv[2]) if len(sys.argv) > 2 else SHIFT_Y
    process_directory(target_dir, shift_val)
