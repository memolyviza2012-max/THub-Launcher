#!/usr/bin/env python3
"""
Generate Retro Thai PUA Fonts
=============================
Generates complete 2,208 PUA composite glyphs (U+F000 - U+F89F) for:
- Mitr (6 styles)
- Pattaya (1 style)
- Fahkwang (12 styles)
- Trirong (12 styles)
- SyDi Ume Pixel (1 style)

Applies tone mark elevation (.small / pixel offset) and left shift (.narrow)
to completely eliminate tone mark collisions and clipping.
"""

import os
import sys
import json
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphComponent
from fontTools.pens.boundsPen import BoundsPen

TALL_CONSONANTS = {0x0E1B, 0x0E1D, 0x0E1F} # ป ฝ ฟ
UPPER_VOWELS = {0x0E31, 0x0E34, 0x0E35, 0x0E36, 0x0E37, 0x0E47, 0x0E4D}
TONE_MARKS = {0x0E48, 0x0E49, 0x0E4A, 0x0E4B, 0x0E4C}

def get_exact_bounds(font, glyph_name):
    try:
        glyf_table = font['glyf']
        pen = BoundsPen(glyf_table)
        glyf_table[glyph_name].draw(pen, glyf_table)
        return pen.bounds
    except Exception:
        return None

def calc_auto_y_raise(font):
    cmap = font.getBestCmap()
    upm = font['head'].unitsPerEm
    max_upper = 0
    for cp in UPPER_VOWELS:
        g = cmap.get(cp)
        if g:
            b = get_exact_bounds(font, g)
            if b and b[3] > max_upper:
                max_upper = b[3]
    min_tone = 9999
    for cp in TONE_MARKS:
        g = cmap.get(cp)
        if g:
            b = get_exact_bounds(font, g)
            if b and b[1] < min_tone:
                min_tone = b[1]
    if max_upper > 0 and min_tone < 9999:
        overlap = max_upper - min_tone
        padding = int(upm * 0.05)
        return max(int(upm * 0.10), overlap + padding)
    return int(upm * 0.20)

def process_single_font(src_path, out_path, mapping, is_pixel=False):
    print(f"Processing: {os.path.basename(src_path)} -> {os.path.basename(out_path)}")
    font = TTFont(src_path)
    cmap = font.getBestCmap()
    glyf = font['glyf']
    hmtx = font['hmtx']
    
    is_trirong = "trirong" in os.path.basename(src_path).lower()
    y_raise = calc_auto_y_raise(font)
    max_shifted_ymax = -9999
    added = 0
    
    for thai_str, pua_val in mapping.items():
        if thai_str.startswith('_'):
            continue
        pua_char = pua_val[0]
        pua_cp = ord(pua_char)
        if not (0xF000 <= pua_cp <= 0xF8FF):
            continue
            
        raw_cps = [ord(c) for c in thai_str]
        norm_cps = [0x0E4D if cp == 0x0E33 else cp for cp in raw_cps]
        has_upper = any(cp in UPPER_VOWELS for cp in norm_cps)
        is_tall = raw_cps[0] in TALL_CONSONANTS
        
        components = []
        base_name = None
        base_adv = 0
        
        has_am = (0x0E33 in raw_cps)
        skip_am = False
        
        for i, cp in enumerate(norm_cps):
            if i == 0:
                base_name = cmap.get(cp)
                if not base_name:
                    break
                base_adv = hmtx[base_name][0]
                components.append((base_name, 0, 0))
                continue
                
            if skip_am and cp == 0x0E4D:
                continue
                
            gname = cmap.get(cp)
            if not gname:
                continue
                
            comp_name = gname
            dx = base_adv
            dy = 0
            
            if is_pixel:
                # Specialized pixel art grid logic for SyDi Ume Pixel
                if cp in TONE_MARKS:
                    if has_upper:
                        dx = base_adv - (340 if is_tall else 170)
                        dy = 0  # stays at Level 2 height
                    else:
                        dx = base_adv - (340 if is_tall else 0)
                        dy = -512  # drops down to Level 1 height
                elif cp in UPPER_VOWELS and is_tall:
                    dx = base_adv - 170
                    dy = 0
            else:
                # Vector typography logic with OpenType variant lookup
                if cp in TONE_MARKS:
                    if has_am:
                        combo = f'uni0E4D{cp:04X}'
                        if is_tall:
                            combo += '.narrow'
                        if combo in glyf:
                            comp_name = combo
                            skip_am = True
                            if is_trirong:
                                dx += -153 if is_tall else -70
                            components.append((comp_name, dx, dy))
                            continue
                            
                    if has_upper:
                        cand = f'{gname}.small'
                        if cand in glyf:
                            comp_name = cand
                        else:
                            dy = y_raise
                        if is_trirong:
                            if is_tall:
                                dx += -153  # OpenType GPOS shift over narrow vowel
                            else:
                                if cp in (0x0E49, 0x0E4A):  # ไม้โท, ไม้ตรี
                                    dx += -80
                                elif cp in (0x0E48, 0x0E4B, 0x0E4C):  # ไม้เอก, ไม้จัตวา, การันต์
                                    dx += -70
                        elif is_tall:
                            dx += -150
                    elif is_tall:
                        cand = f'{gname}.narrow'
                        if cand in glyf:
                            comp_name = cand
                        if is_trirong:
                            if cp in (0x0E49, 0x0E4A):  # ไม้โท, ไม้ตรี narrow
                                dx += -60
                            elif cp in (0x0E48, 0x0E4B, 0x0E4C):
                                dx += -30
                    else:
                        if is_trirong:
                            if cp in (0x0E49, 0x0E4A):  # ไม้โท, ไม้ตรี
                                dx += -80
                            elif cp in (0x0E48, 0x0E4B, 0x0E4C):  # ไม้เอก, ไม้จัตวา, การันต์
                                dx += -60
                elif cp in UPPER_VOWELS and is_tall:
                    cand = f'{gname}.narrow'
                    if cand in glyf:
                        comp_name = cand
                        
            components.append((comp_name, dx, dy))
                
        if not base_name:
            continue
            
        new_glyph = Glyph()
        new_glyph.components = []
        for gname, dx, dy in components:
            if gname not in glyf:
                continue
            comp = GlyphComponent()
            comp.glyphName = gname
            comp.x = dx
            comp.y = dy
            comp.flags = 0x1000 # USE_MY_METRICS (matches Noonetranslator)
            new_glyph.components.append(comp)
        new_glyph.numberOfContours = -1
        
        pua_hex = f'{pua_cp:04X}'
        pua_gname = f'uni{pua_hex}'
        glyf[pua_gname] = new_glyph
        hmtx[pua_gname] = hmtx[base_name]
        
        for table in font['cmap'].tables:
            if table.isUnicode():
                table.cmap[pua_cp] = pua_gname
        added += 1

    # Map missing bullet point U+2022 if absent
    if 0x2022 not in cmap:
        dot_name = cmap.get(0x00B7) or cmap.get(0x002E) or 'period'
        for table in font['cmap'].tables:
            if table.isUnicode():
                table.cmap[0x2022] = dot_name

    # Safe vertical metrics adjustment to prevent clipping
    # Calculate global max yMax
    for gname in glyf.glyphs.keys():
        g = glyf[gname]
        if hasattr(g, 'yMax') and g.yMax and g.yMax > max_shifted_ymax:
            max_shifted_ymax = g.yMax
            
    if max_shifted_ymax > 0:
        if 'OS/2' in font:
            os2 = font['OS/2']
            if hasattr(os2, 'usWinAscent') and os2.usWinAscent < max_shifted_ymax:
                os2.usWinAscent = int(max_shifted_ymax + 15)
        if 'hhea' in font:
            hhea = font['hhea']
            if hasattr(hhea, 'ascent') and hhea.ascent < max_shifted_ymax:
                hhea.ascent = int(max_shifted_ymax + 15)

    # Set glyph order
    glyph_order = font.getGlyphOrder()
    for table in font['cmap'].tables:
        if table.isUnicode():
            for code, name in table.cmap.items():
                if name not in glyph_order:
                    glyph_order.append(name)
    font.setGlyphOrder(glyph_order)
    
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    font.save(out_path)
    print(f"  -> Successfully generated {out_path} ({added} PUA glyphs, yMax={max_shifted_ymax})")
    return True

def main():
    base_dir = Path(__file__).resolve().parent
    mapping_path = base_dir / "mapping" / "Mapping.json"
    with open(mapping_path, 'r', encoding='utf-8') as f:
        mapping = json.load(f)
        
    lib_dir = base_dir / "library"
    targets = [
        ("mitr", False),
        ("pattaya", False),
        ("fahkwang", False),
        ("trirong", False),
        ("sydi_ume_pixel", True),
    ]
    
    total_processed = 0
    for folder, is_pixel in targets:
        target_dir = lib_dir / folder
        if not target_dir.exists():
            print(f"Warning: {target_dir} not found")
            continue
        print(f"\n=== Processing Family: {folder} ===")
        for f in os.listdir(target_dir):
            if f.endswith('.ttf') and not f.endswith('_PUA.ttf') and not f.endswith('_TEST_PUA.ttf'):
                src = target_dir / f
                out_name = f.replace('.ttf', '_PUA.ttf')
                out = target_dir / out_name
                process_single_font(str(src), str(out), mapping, is_pixel=is_pixel)
                total_processed += 1
                
    print(f"\nAll Done! Successfully created PUA variants for {total_processed} font files.")

if __name__ == '__main__':
    main()
