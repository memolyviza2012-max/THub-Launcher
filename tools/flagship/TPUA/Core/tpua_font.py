import os
import json
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphComponent

class TPUAFontEngine:
    def __init__(self, mapping_path=None):
        self.mapping = {}
        if mapping_path and os.path.exists(mapping_path):
            self.load_mapping(mapping_path)

    def load_mapping(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.mapping = json.load(f)
        except Exception as e:
            raise Exception(f"Failed to load mapping JSON: {e}")

    def process_font(self, font_path, out_path, callback=None):
        if not self.mapping:
            raise Exception("No mapping data loaded. Please provide a Mapping.json.")
            
        if callback: callback(f"Processing: {os.path.basename(font_path)}")
        
        try:
            font = TTFont(font_path)
        except Exception as e:
            raise Exception(f"Error loading font '{os.path.basename(font_path)}': {e}")

        cmap = font.getBestCmap()
        if 'glyf' not in font:
            raise Exception(f"Font '{os.path.basename(font_path)}' does not have a 'glyf' table. Only TrueType (.ttf) outlines are supported, not CFF (.otf).")
            
        glyf_table = font['glyf']
        hmtx_table = font['hmtx']

        added_count = 0

        for thai_str, pua_val in self.mapping.items():
            if thai_str.startswith('_'): continue
            
            # Determine target PUA codepoint
            if isinstance(pua_val, list):
                pua_char = pua_val[0]
            else:
                pua_char = pua_val[0]
                
            pua_cp = ord(pua_char)
            
            # Only process if it's actually in the PUA range
            if not (0xF000 <= pua_cp <= 0xF8FF):
                continue
                
            pua_hex = f"{pua_cp:04X}"
            
            # Build component list
            chars = list(thai_str)
            components = []
            base_name = None
            base_advance = 0
            
            for i, char in enumerate(chars):
                cp = ord(char)
                # Handle Sara Am (0E33) -> Nikhahit (0E4D) for the composite
                if cp == 0x0E33:
                    cp = 0x0E4D
                    
                glyph_name = cmap.get(cp)
                if not glyph_name:
                    continue
                    
                if i == 0:
                    base_name = glyph_name
                    base_advance = hmtx_table.metrics[base_name][0]
                    components.append((glyph_name, 0, 0))
                else:
                    # All non-base characters (vowels, tone marks, etc.)
                    # Shift x by base_advance
                    components.append((glyph_name, base_advance, 0))

            if not base_name:
                continue

            # Create Composite Glyph
            new_glyph = Glyph()
            new_glyph.components = []
            valid_components = True
            for gname, dx, dy in components:
                if gname not in glyf_table:
                    valid_components = False
                    break
                comp = GlyphComponent()
                comp.glyphName = gname
                comp.x = dx
                comp.y = dy
                # Use 0x1000 (USE_MY_METRICS)
                comp.flags = 0x1000
                new_glyph.components.append(comp)

            if not valid_components or not new_glyph.components:
                continue

            new_glyph.numberOfContours = -1
            
            # Add to tables
            pua_glyph_name = f"uni{pua_hex.upper()}"
            glyf_table[pua_glyph_name] = new_glyph
            hmtx_table[pua_glyph_name] = hmtx_table[base_name] # Same advance width as base consonant
            
            # Update Cmap
            for table in font['cmap'].tables:
                if table.isUnicode():
                    table.cmap[pua_cp] = pua_glyph_name
                    
            added_count += 1

        # Add missing glyphs to glyph order
        glyph_order = font.getGlyphOrder()
        for table in font['cmap'].tables:
            if table.isUnicode():
                for code, name in table.cmap.items():
                    if name not in glyph_order:
                        glyph_order.append(name)
        font.setGlyphOrder(glyph_order)

        # Save
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        font.save(out_path)
        if callback: callback(f"Success: {os.path.basename(out_path)} (+{added_count} PUA glyphs)")
        return added_count
