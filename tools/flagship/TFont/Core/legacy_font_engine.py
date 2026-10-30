import os
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.ttGlyphPen import TTGlyphPen

class LegacyFontEngine:
    def __init__(self):
        pass

    def get_exact_bounds(self, font, glyph_name):
        try:
            glyf_table = font['glyf']
            pen = BoundsPen(glyf_table)
            glyf_table[glyph_name].draw(pen, glyf_table)
            return pen.bounds # (xMin, yMin, xMax, yMax)
        except Exception:
            return None

    def _shift_glyph(self, font, gname, dx, dy):
        """Flattens and shifts a glyph, returning the new glyph object."""
        glyf_table = font['glyf']
        if gname not in glyf_table:
            return None
        
        g_orig = glyf_table[gname]
        pen = TTGlyphPen(glyf_table)
        g_orig.draw(pen, glyf_table)
        g_flat = pen.glyph()

        if hasattr(g_flat, 'coordinates'):
            for i in range(len(g_flat.coordinates)):
                x, y = g_flat.coordinates[i]
                g_flat.coordinates[i] = (x + dx, y + dy)
            g_flat.recalcBounds(glyf_table)
        return g_flat

    def build_default_offsets(self, font):
        """Builds a 10-parameter dictionary for F700 plus 3 for Base Shift."""
        return {
            # Base Shifts (modify original glyphs directly)
            'base_tone_y': 160,      # Lift tone marks up by 160 units to prevent overlapping ั or ี
            'base_upper_vowel_y': 0, # e.g., move all upper vowels up
            'base_lower_vowel_y': 0, # e.g., move all lower vowels down

            # PUA Shifts (F700 generation)
            'upper_vowel_left_x': -150,
            'upper_vowel_left_y': 0,
            
            'tone_raised_x': 0,
            'tone_raised_y': 350,  # Will be auto-calculated if left at 0, but UI defaults to something
            
            'tone_left_x': -150,
            'tone_left_y': 0,
            
            'tone_left_raised_x': -150,
            'tone_left_raised_y': 350,
            
            'lower_vowel_down_x': 0,
            'lower_vowel_down_y': -150
        }

    def _auto_calc_y_raise(self, font, offsets, callback=None):
        """Auto-calculates Y Raise scanning worst-case overlap."""
        cmap = font.getBestCmap()
        upm = font['head'].unitsPerEm
        glyphSet = font.getGlyphSet()

        # Upper vowels that can sit under a tone mark
        upper_vowel_cps = [0x0E34, 0x0E35, 0x0E36, 0x0E37, 0x0E31, 0x0E4D, 0x0E47]
        tone_mark_cps   = [0x0E48, 0x0E49, 0x0E4A, 0x0E4B, 0x0E4C]

        def get_b(cp):
            g = cmap.get(cp)
            if not g: return None
            return self.get_exact_bounds(font, g)

        max_upper = 0
        for cp in upper_vowel_cps:
            b = get_b(cp)
            if b and b[3] > max_upper: max_upper = b[3]

        min_tone = 9999
        for cp in tone_mark_cps:
            b = get_b(cp)
            if b and b[1] < min_tone: min_tone = b[1]

        if max_upper > 0 and min_tone < 9999:
            overlap = max_upper - min_tone
            padding = int(upm * 0.05)
            y_raise = max(int(upm * 0.10), overlap + padding)
            if callback: callback(f"Auto Y Raise (worst-case): overlap={overlap}, pad={padding} => {y_raise}")
        else:
            y_raise = int(upm * 0.20)
            if callback: callback(f"Auto Y Raise (fallback): {y_raise}")

        if offsets['tone_raised_y'] <= 0: offsets['tone_raised_y'] = y_raise
        if offsets['tone_left_raised_y'] <= 0: offsets['tone_left_raised_y'] = y_raise
        return offsets

    def process_font(self, font_path, out_path, offsets=None, callback=None,
                     # Legacy fallback
                     y_raise=0, x_left=-150, y_down=-100):
        if callback: callback(f"Loading font: {os.path.basename(font_path)}")
        try:
            font = TTFont(font_path)
        except Exception as e:
            raise Exception(f"Failed to load font: {e}")

        cmap = font.getBestCmap()
        if 'glyf' not in font:
            raise Exception("Font must be TrueType (.ttf) with a 'glyf' table.")

        glyf_table = font['glyf']
        hmtx_table = font['hmtx']
        upm = font['head'].unitsPerEm

        if not offsets:
            if callback: callback("Using legacy 3-param fallback mode.")
            offsets = self.build_default_offsets(font)
            offsets['upper_vowel_left_x'] = x_left
            offsets['tone_left_x'] = x_left
            offsets['tone_left_raised_x'] = x_left
            offsets['lower_vowel_down_y'] = y_down
            offsets['tone_raised_y'] = y_raise
            offsets['tone_left_raised_y'] = y_raise

        if offsets['tone_raised_y'] <= 0 or offsets['tone_left_raised_y'] <= 0:
            offsets = self._auto_calc_y_raise(font, offsets, callback)

        added_count = 0
        base_shifted_count = 0

        # === 1. BASE UNICODE SHIFT ===
        # If user wants to permanently move all normal tone marks / vowels
        base_shifts = {
            'base_tone_y': [0x0E48, 0x0E49, 0x0E4A, 0x0E4B, 0x0E4C],
            'base_upper_vowel_y': [0x0E34, 0x0E35, 0x0E36, 0x0E37, 0x0E31, 0x0E4D, 0x0E47],
            'base_lower_vowel_y': [0x0E38, 0x0E39, 0x0E3A]
        }
        
        for key, cps in base_shifts.items():
            dy = offsets.get(key, 0)
            if dy != 0:
                for cp in cps:
                    gname = cmap.get(cp)
                    if gname:
                        new_g = self._shift_glyph(font, gname, 0, dy)
                        if new_g:
                            glyf_table[gname] = new_g
                            base_shifted_count += 1
        
        if base_shifted_count > 0 and callback:
            callback(f"Base Unicode Shift applied to {base_shifted_count} standard glyphs.")

        # === 2. PUA F700 GENERATION ===
        uv_lx = offsets['upper_vowel_left_x']
        uv_ly = offsets['upper_vowel_left_y']
        
        tr_x = offsets['tone_raised_x']
        tr_y = offsets['tone_raised_y']
        
        tl_x = offsets['tone_left_x']
        tl_y = offsets['tone_left_y']
        
        tlr_x = offsets['tone_left_raised_x']
        tlr_y = offsets['tone_left_raised_y']
        
        ld_x = offsets['lower_vowel_down_x']
        ld_y = offsets['lower_vowel_down_y']

        mapping = {
            0xF700: (0x0E10, 0, 0),     # ฐ base flat
            0xF701: (0x0E34, uv_lx, uv_ly), # ิ left
            0xF702: (0x0E35, uv_lx, uv_ly), # ี left
            0xF703: (0x0E36, uv_lx, uv_ly), # ึ left
            0xF704: (0x0E37, uv_lx, uv_ly), # ื left
            
            0xF705: (0x0E48, tr_x, tr_y),   # ่ raised
            0xF706: (0x0E49, tr_x, tr_y),   # ้ raised
            0xF707: (0x0E4A, tr_x, tr_y),   # ๊ raised
            0xF708: (0x0E4B, tr_x, tr_y),   # ๋ raised
            0xF709: (0x0E4C, tr_x, tr_y),   # ์ raised
            
            0xF70A: (0x0E48, tl_x, tl_y),   # ่ left
            0xF70B: (0x0E49, tl_x, tl_y),   # ้ left
            0xF70C: (0x0E4A, tl_x, tl_y),   # ๊ left
            0xF70D: (0x0E4B, tl_x, tl_y),   # ๋ left
            0xF70E: (0x0E4C, tl_x, tl_y),   # ์ left
            
            0xF70F: (0x0E0D, 0, 0),     # ญ base flat
            0xF710: (0x0E31, uv_lx, uv_ly), # ั left
            0xF711: (0x0E4D, uv_lx, uv_ly), # ํ left
            0xF712: (0x0E47, uv_lx, uv_ly), # ็ left
            
            0xF713: (0x0E48, tlr_x, tlr_y), # ่ left-raised
            0xF714: (0x0E49, tlr_x, tlr_y), # ้ left-raised
            0xF715: (0x0E4A, tlr_x, tlr_y), # ๊ left-raised
            0xF716: (0x0E4B, tlr_x, tlr_y), # ๋ left-raised
            0xF717: (0x0E4C, tlr_x, tlr_y), # ์ left-raised
            
            0xF718: (0x0E38, ld_x, ld_y),   # ุ down
            0xF719: (0x0E39, ld_x, ld_y),   # ู down
            0xF71A: (0x0E3A, ld_x, ld_y),   # ฺ down
        }

        for pua_cp, (base_cp, dx, dy) in mapping.items():
            base_gname = cmap.get(base_cp)
            if not base_gname or base_gname not in glyf_table:
                if callback: callback(f"Warning: Base {hex(base_cp)} not found, skipping {hex(pua_cp)}.")
                continue

            new_g = self._shift_glyph(font, base_gname, dx, dy)
            if not new_g: continue
            
            pua_hex = f"{pua_cp:04X}"
            pua_glyph_name = f"uni{pua_hex.upper()}"
            glyf_table[pua_glyph_name] = new_g
            
            if pua_cp in (0xF700, 0xF70F):
                orig_adv = hmtx_table.metrics[base_gname][0]
                hmtx_table[pua_glyph_name] = (orig_adv, 0)
            else:
                hmtx_table[pua_glyph_name] = (0, 0)
            
            for table in font['cmap'].tables:
                if table.isUnicode():
                    table.cmap[pua_cp] = pua_glyph_name
                    
            added_count += 1

        glyph_order = font.getGlyphOrder()
        for table in font['cmap'].tables:
            if table.isUnicode():
                for code, name in table.cmap.items():
                    if name not in glyph_order:
                        glyph_order.append(name)
        font.setGlyphOrder(glyph_order)

        if callback: callback("Saving font...")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        font.save(out_path)
        if callback: callback(f"Success! Added {added_count} PUA Glyphs. Saved to {os.path.basename(out_path)}")
        return added_count
