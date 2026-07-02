from i18n_helper import _
"""
i18n.py — Internationalization module for FONT PPFS
Supports English (default) and Thai language switching.
"""

STRINGS = {
    "en": {
        # Window
        "app_title": "🔤 FONT PPFS — Thai PUA Font Studio",
        "app_subtitle": _("app_subtitle"),
        
        # Toolbar
        "load_font": _("load_font"),
        "load_project": _("load_project"),
        "save_project": _("save_project"),
        "export": _("export"),
        "export_png": _("export_png"),
        "settings": _("settings"),
        "compare": _("compare"),
        "language": _("language"),
        
        # Glyph Table
        "glyph_table": _("glyph_table"),
        "filter_all": _("filter_all"),
        "filter_consonants": _("filter_consonants"),
        "filter_vowels_above": _("filter_vowels_above"),
        "filter_vowels_below": _("filter_vowels_below"),
        "filter_tone_marks": _("filter_tone_marks"),
        "filter_symbols": _("filter_symbols"),
        "filter_numbers": _("filter_numbers"),
        "filter_latin": _("filter_latin"),
        "filter_pua": _("filter_pua"),
        "filter_problems": _("filter_problems"),
        "search_placeholder": _("search_placeholder"),
        "col_char": _("col_char"),
        "col_unicode": _("col_unicode"),
        "col_category": _("col_category"),
        "col_fill": _("col_fill"),
        "col_status": _("col_status"),
        
        # Preview
        "preview_title": _("preview_title"),
        "preview_input": _("preview_input"),
        "preset_texts": _("preset_texts"),
        "atlas_title": _("atlas_title"),
        "zoom_in": _("zoom_in"),
        "zoom_out": _("zoom_out"),
        "zoom_fit": _("zoom_fit"),
        "grid_overlay": _("grid_overlay"),
        
        # Adjust Panel
        "adjust_title": _("adjust_title"),
        "x_offset": _("x_offset"),
        "y_offset": _("y_offset"),
        "scale": _("scale"),
        "width_override": _("width_override"),
        "height_override": _("height_override"),
        "advance_override": _("advance_override"),
        "reset": _("reset"),
        "apply_category": _("apply_category"),
        "quality": _("quality"),
        "fill_w": _("fill_w"),
        "fill_h": _("fill_h"),
        "status_ok": _("status_ok"),
        "status_warn": _("status_warn"),
        "status_error": _("status_error"),
        
        # Export Dialog
        "export_title": _("export_title"),
        "export_profile": _("export_profile"),
        "profile_dl2": _("profile_dl2"),
        "profile_bmfont": _("profile_bmfont"),
        "profile_json": _("profile_json"),
        "export_path": _("export_path"),
        "export_browse": _("export_browse"),
        "export_start": _("export_start"),
        "export_cancel": _("export_cancel"),
        "export_base_image": _("export_base_image"),
        "export_base_img_ph": _("export_base_img_ph"),
        
        # Project
        "project_filter": _("project_filter"),
        "font_filter": _("font_filter"),
        "mapping_filter": _("mapping_filter"),
        "charset_filter": _("charset_filter"),
        
        # Status Bar
        "status_ready": _("status_ready"),
        "status_font": _("status_font"),
        "status_glyphs": _("status_glyphs"),
        "status_quality": _("quality"),
        "status_no_font": _("status_no_font"),
        
        # Messages
        "msg_font_loaded": _("msg_font_loaded"),
        "msg_project_saved": _("msg_project_saved"),
        "msg_project_loaded": _("msg_project_loaded"),
        "msg_export_done": _("msg_export_done"),
        "msg_export_error": _("msg_export_error"),
        "msg_quality_ok": _("msg_quality_ok"),
        "msg_quality_warn": _("msg_quality_warn"),
        "msg_atlas_overflow": _("msg_atlas_overflow"),
        
        # Undo/Redo
        "undo": _("undo"),
        "redo": _("redo"),
        
        # Categories
        "cat_consonant": _("cat_consonant"),
        "cat_vowel_above": _("cat_vowel_above"),
        "cat_vowel_below": _("cat_vowel_below"),
        "cat_tone_mark": _("cat_tone_mark"),
        "cat_symbol": _("cat_symbol"),
        "cat_number": _("cat_number"),
        "cat_pua": _("cat_pua"),
        "cat_latin": _("cat_latin"),
        "cat_other": _("cat_other"),
        
        # Preset text labels
        "preset_general": _("preset_general"),
        "preset_sara_ue": _("preset_sara_ue"),
        "preset_sara_am": _("preset_sara_am"),
        "preset_mai_tri": _("preset_mai_tri"),
        "preset_consonants": _("preset_consonants"),
        "preset_english": _("preset_english"),
        "preset_mixed": _("preset_mixed"),
    },
    "th": {
        # Window
        "app_title": "🔤 FONT PPFS — สตูดิโอสร้างฟอนต์ PUA ไทย",
        "app_subtitle": _("app_subtitle"),
        
        # Toolbar
        "load_font": _("load_font"),
        "load_project": _("load_project"),
        "save_project": _("save_project"),
        "export": _("export"),
        "export_png": _("export_png"),
        "settings": _("settings"),
        "compare": _("compare"),
        "language": _("language"),
        
        # Glyph Table
        "glyph_table": _("glyph_table"),
        "filter_all": _("filter_all"),
        "filter_consonants": _("filter_consonants"),
        "filter_vowels_above": _("filter_vowels_above"),
        "filter_vowels_below": _("filter_vowels_below"),
        "filter_tone_marks": _("filter_tone_marks"),
        "filter_symbols": _("filter_symbols"),
        "filter_numbers": _("filter_numbers"),
        "filter_latin": _("filter_latin"),
        "filter_pua": _("filter_pua"),
        "filter_problems": _("filter_problems"),
        "search_placeholder": _("search_placeholder"),
        "col_char": _("col_char"),
        "col_unicode": _("col_unicode"),
        "col_category": _("col_category"),
        "col_fill": _("col_fill"),
        "col_status": _("col_status"),
        
        # Preview
        "preview_title": _("preview_title"),
        "preview_input": _("preview_input"),
        "preset_texts": _("preset_texts"),
        "atlas_title": _("atlas_title"),
        "zoom_in": _("zoom_in"),
        "zoom_out": _("zoom_out"),
        "zoom_fit": _("zoom_fit"),
        "grid_overlay": _("grid_overlay"),
        
        # Adjust Panel
        "adjust_title": _("adjust_title"),
        "x_offset": _("x_offset"),
        "y_offset": _("y_offset"),
        "scale": _("scale"),
        "width_override": _("width_override"),
        "height_override": _("height_override"),
        "advance_override": _("advance_override"),
        "reset": _("reset"),
        "apply_category": _("apply_category"),
        "quality": _("quality"),
        "fill_w": _("fill_w"),
        "fill_h": _("fill_h"),
        "status_ok": _("status_ok"),
        "status_warn": _("status_warn"),
        "status_error": _("status_error"),
        
        # Export Dialog
        "export_title": _("export_title"),
        "export_profile": _("export_profile"),
        "profile_dl2": _("profile_dl2"),
        "profile_bmfont": _("profile_bmfont"),
        "profile_json": _("profile_json"),
        "export_path": _("export_path"),
        "export_browse": _("export_browse"),
        "export_start": _("export_start"),
        "export_cancel": _("export_cancel"),
        "export_base_image": _("export_base_image"),
        "export_base_img_ph": _("export_base_img_ph"),
        
        # Project
        "project_filter": _("project_filter"),
        "font_filter": _("font_filter"),
        "mapping_filter": _("mapping_filter"),
        "charset_filter": _("charset_filter"),
        
        # Status Bar
        "status_ready": _("status_ready"),
        "status_font": _("status_font"),
        "status_glyphs": _("status_glyphs"),
        "status_quality": _("quality"),
        "status_no_font": _("status_no_font"),
        
        # Messages
        "msg_font_loaded": _("msg_font_loaded"),
        "msg_project_saved": _("msg_project_saved"),
        "msg_project_loaded": _("msg_project_loaded"),
        "msg_export_done": _("msg_export_done"),
        "msg_export_error": _("msg_export_error"),
        "msg_quality_ok": _("msg_quality_ok"),
        "msg_quality_warn": _("msg_quality_warn"),
        "msg_atlas_overflow": _("msg_atlas_overflow"),
        
        # Undo/Redo
        "undo": _("undo"),
        "redo": _("redo"),
        
        # Categories
        "cat_consonant": _("filter_consonants"),
        "cat_vowel_above": _("filter_vowels_above"),
        "cat_vowel_below": _("filter_vowels_below"),
        "cat_tone_mark": _("filter_tone_marks"),
        "cat_symbol": _("cat_symbol"),
        "cat_number": _("filter_numbers"),
        "cat_pua": _("cat_pua"),
        "cat_latin": _("cat_latin"),
        "cat_other": _("cat_other"),
        
        # Preset text labels
        "preset_general": _("preset_general"),
        "preset_sara_ue": _("preset_sara_ue"),
        "preset_sara_am": _("preset_sara_am"),
        "preset_mai_tri": _("preset_mai_tri"),
        "preset_consonants": _("preset_consonants"),
        "preset_english": _("preset_english"),
        "preset_mixed": _("preset_mixed"),
    }
}

# Preset test strings (shared across languages)
PRESET_TEXTS = {
    "preset_general": "สวัสดีครับ ยินดีต้อนรับสู่เกม",
    "preset_sara_ue": "เรื่องราวเบื้องหลัง ชื่อ มื้อ ลื่น ซื่อ",
    "preset_sara_am": "น้ำ ถ้ำ ซ้ำ ย้ำ ทำ คำ จำ ดำ สำ",
    "preset_mai_tri": "ปิ๊ง ติ๊ก ตุ๊กตา จ๊ะ ค๊ะ",
    "preset_consonants": "กขฃคฅฆงจฉชซฌญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรฤลฦวศษสหฬอฮ",
    "preset_english": "ABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789 !@#$%",
    "preset_mixed": "เลเวล Level 42 — ค่าพลังชีวิต HP: 380/380",
}


class I18n:
    """Internationalization manager for FONT PPFS."""
    
    def __init__(self, lang: str = "en"):
        self._lang = lang
    
    @property
    def lang(self) -> str:
        return self._lang
    
    @lang.setter
    def lang(self, value: str):
        if value in STRINGS:
            self._lang = value
        else:
            raise ValueError(f"Unsupported language: {value}. Use 'en' or 'th'.")
    
    def t(self, key: str) -> str:
        """Translate a key to the current language."""
        return STRINGS.get(self._lang, STRINGS["en"]).get(key, key)
    
    def switch(self):
        """Toggle between EN and TH."""
        self._lang = "th" if self._lang == "en" else "en"
        return self._lang
    
    def get_presets(self) -> dict[str, tuple[str, str]]:
        """Returns {key: (label, text)} for preset test strings."""
        return {
            k: (self.t(k), v) for k, v in PRESET_TEXTS.items()
        }


_global_i18n = I18n()
def _(key: str) -> str:
    return _global_i18n.t(key)
