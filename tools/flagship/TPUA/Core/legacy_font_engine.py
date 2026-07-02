import os
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.ttGlyphPen import TTGlyphPen

class LegacyFontEngine:
    def __init__(self):
        pass

    def get_exact_bounds(self, glyf_table, glyph_name):
        try:
            pen = BoundsPen(glyf_table)
            glyf_table[glyph_name].draw(pen, glyf_table)
            return pen.bounds # (xMin, yMin, xMax, yMax)
        except Exception:
            return None

    def process_font(self, font_path, out_path, y_raise=0, x_left=-150, y_down=-100, callback=None):
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

        added_count = 0

        # Auto Y-Raise calculation if user inputs 0
        if y_raise <= 0:
            if callback: callback("Auto-calculating exact Y Raise using BoundsPen...")
            g_uee = cmap.get(0x0E37)
            g_tho = cmap.get(0x0E49)
            if g_uee and g_tho:
                bounds_uee = self.get_exact_bounds(glyf_table, g_uee)
                bounds_tho = self.get_exact_bounds(glyf_table, g_tho)
                if bounds_uee and bounds_tho:
                    uee_ymax = bounds_uee[3]
                    tho_ymin = bounds_tho[1]
                    padding = int(upm * 0.03)
                    calc_raise = (uee_ymax - tho_ymin) + padding
                    min_raise = int(upm * 0.1) 
                    y_raise = max(min_raise, int(calc_raise))
                    if callback: callback(f"Auto Y Raise calculated: {y_raise} (UPM: {upm}, Padding: {padding})")
                else:
                    y_raise = int(upm * 0.17)
            else:
                y_raise = int(upm * 0.17)

        mapping = {
            0xF700: (0x0E10, 0, 0, 0), # ฐ
            0xF701: (0x0E34, 1, 0, 0), # ิ left
            0xF702: (0x0E35, 1, 0, 0), # ี left
            0xF703: (0x0E36, 1, 0, 0), # ึ left
            0xF704: (0x0E37, 1, 0, 0), # ื left
            0xF705: (0x0E48, 0, 1, 0), # ่ raised
            0xF706: (0x0E49, 0, 1, 0), # ้ raised
            0xF707: (0x0E4A, 0, 1, 0), # ๊ raised
            0xF708: (0x0E4B, 0, 1, 0), # ๋ raised
            0xF709: (0x0E4C, 0, 1, 0), # ์ raised
            0xF70A: (0x0E48, 1, 0, 0), # ่ left
            0xF70B: (0x0E49, 1, 0, 0), # ้ left
            0xF70C: (0x0E4A, 1, 0, 0), # ๊ left
            0xF70D: (0x0E4B, 1, 0, 0), # ๋ left
            0xF70E: (0x0E4C, 1, 0, 0), # ์ left
            0xF70F: (0x0E0D, 0, 0, 0), # ญ
            0xF710: (0x0E31, 1, 0, 0), # ั left
            0xF711: (0x0E4D, 1, 0, 0), # ํ left
            0xF712: (0x0E47, 1, 0, 0), # ็ left
            0xF713: (0x0E48, 1, 1, 0), # ่ left-raised
            0xF714: (0x0E49, 1, 1, 0), # ้ left-raised
            0xF715: (0x0E4A, 1, 1, 0), # ๊ left-raised
            0xF716: (0x0E4B, 1, 1, 0), # ๋ left-raised
            0xF717: (0x0E4C, 1, 1, 0), # ์ left-raised
            0xF718: (0x0E38, 0, 0, 1), # ุ down
            0xF719: (0x0E39, 0, 0, 1), # ู down
            0xF71A: (0x0E3A, 0, 0, 1), # ฺ down
        }

        for pua_cp, (base_cp, mx, my, mdown) in mapping.items():
            base_gname = cmap.get(base_cp)
            if not base_gname or base_gname not in glyf_table:
                if callback: callback(f"Warning: Base glyph {hex(base_cp)} not found, skipping {hex(pua_cp)}.")
                continue

            dx = int(mx * x_left)
            dy = int((my * y_raise) + (mdown * y_down))

            # Decompose the original glyph into raw contours
            g_orig = glyf_table[base_gname]
            pen = TTGlyphPen(glyf_table)
            g_orig.draw(pen, glyf_table)
            g_flat = pen.glyph()

            # Physically shift coordinates
            if hasattr(g_flat, 'coordinates'):
                for i in range(len(g_flat.coordinates)):
                    x, y = g_flat.coordinates[i]
                    g_flat.coordinates[i] = (x + dx, y + dy)
                # Recalculate bounds manually after shifting
                g_flat.recalcBounds(glyf_table)
            
            pua_hex = f"{pua_cp:04X}"
            pua_glyph_name = f"uni{pua_hex.upper()}"
            
            glyf_table[pua_glyph_name] = g_flat
            
            # Zero Advance Width
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
        if callback: callback(f"Success! Added {added_count} Legacy PUA Glyphs to {os.path.basename(out_path)}")
        return added_count
