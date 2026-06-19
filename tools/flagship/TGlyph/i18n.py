"""
i18n.py — Internationalization module for FONT PPFS
Supports English (default) and Thai language switching.
"""

STRINGS = {
    "en": {
        # Window
        "app_title": "🔤 FONT PPFS — Thai PUA Font Studio",
        "app_subtitle": "Universal Game Font Generator",
        
        # Toolbar
        "load_font": "📂 Load Font",
        "load_project": "📦 Load Project",
        "save_project": "💾 Save Project",
        "export": "🚀 Export",
        "export_png": "📸 Export PNG Only",
        "settings": "⚙️ Settings",
        "compare": "👁️ Compare",
        "language": "🌐 Language",
        
        # Glyph Table
        "glyph_table": "📋 Glyph Table",
        "filter_all": "All",
        "filter_consonants": "Consonants",
        "filter_vowels_above": "Vowels Above",
        "filter_vowels_below": "Vowels Below",
        "filter_tone_marks": "Tone Marks",
        "filter_symbols": "Symbols / Punctuation",
        "filter_numbers": "Numbers",
        "filter_latin": "Latin / English",
        "filter_pua": "PUA Composites",
        "filter_problems": "⚠️ Problems Only",
        "search_placeholder": "Search (Unicode / Character)...",
        "col_char": "Char",
        "col_unicode": "Unicode",
        "col_category": "Category",
        "col_fill": "Fill %",
        "col_status": "Status",
        
        # Preview
        "preview_title": "👁️ Real-Time Preview",
        "preview_input": "Type text to preview...",
        "preset_texts": "📝 Preset Texts",
        "atlas_title": "🗺️ Atlas Preview",
        "zoom_in": "🔍+",
        "zoom_out": "🔍-",
        "zoom_fit": "Fit",
        "grid_overlay": "Grid",
        
        # Adjust Panel
        "adjust_title": "🔧 Adjust Panel",
        "x_offset": "X Offset",
        "y_offset": "Y Offset",
        "scale": "Scale",
        "width_override": "Width",
        "height_override": "Height",
        "advance_override": "Advance",
        "reset": "↩️ Reset",
        "apply_category": "Apply to All Same Category",
        "quality": "Quality",
        "fill_w": "Fill W",
        "fill_h": "Fill H",
        "status_ok": "✅ OK",
        "status_warn": "⚠️ Warning",
        "status_error": "❌ Problem",
        
        # Export Dialog
        "export_title": "Export Settings",
        "export_profile": "Export Profile",
        "profile_dl2": "Dying Light 2 / The Beast",
        "profile_bmfont": "BMFont (Unity / Unreal)",
        "profile_json": "JSON Atlas (Generic)",
        "export_path": "Output Folder",
        "export_browse": "Browse...",
        "export_start": "🚀 Start Export",
        "export_cancel": "Cancel",
        "export_base_image": "Base Image",
        "export_base_img_ph": "Optional: Path to existing atlas image...",
        
        # Project
        "project_filter": "PPFS Project Files (*.ppfs)",
        "font_filter": "Font Files (*.ttf *.otf)",
        "mapping_filter": "Mapping Files (*.json)",
        "charset_filter": "Character Set (*.txt)",
        
        # Status Bar
        "status_ready": "Ready",
        "status_font": "Font",
        "status_glyphs": "Glyphs",
        "status_quality": "Quality",
        "status_no_font": "No font loaded",
        
        # Messages
        "msg_font_loaded": "Font loaded: {}",
        "msg_project_saved": "Project saved: {}",
        "msg_project_loaded": "Project loaded: {}",
        "msg_export_done": "Export complete! Files saved to: {}",
        "msg_export_error": "Export error: {}",
        "msg_quality_ok": "All {} glyphs passed quality check!",
        "msg_quality_warn": "{} glyphs have quality issues",
        "msg_atlas_overflow": "Atlas overflow! Not enough space for all glyphs.",
        
        # Undo/Redo
        "undo": "Undo",
        "redo": "Redo",
        
        # Categories
        "cat_consonant": "Consonant",
        "cat_vowel_above": "Vowel Above",
        "cat_vowel_below": "Vowel Below",
        "cat_tone_mark": "Tone Mark",
        "cat_symbol": "Symbol",
        "cat_number": "Number",
        "cat_pua": "PUA",
        "cat_latin": "Latin",
        "cat_other": "Other",
        
        # Preset text labels
        "preset_general": "General Test",
        "preset_sara_ue": "Sara Ue + Tones",
        "preset_sara_am": "Sara Am + Tones",
        "preset_mai_tri": "Mai Tri Test",
        "preset_consonants": "All Consonants",
        "preset_english": "English + Numbers",
        "preset_mixed": "Mixed Thai-English",
    },
    "th": {
        # Window
        "app_title": "🔤 FONT PPFS — สตูดิโอสร้างฟอนต์ PUA ไทย",
        "app_subtitle": "เครื่องมือสร้างฟอนต์เกมสากล",
        
        # Toolbar
        "load_font": "📂 โหลดฟอนต์",
        "load_project": "📦 เปิดโปรเจกต์",
        "save_project": "💾 บันทึกโปรเจกต์",
        "export": "🚀 ส่งออก",
        "export_png": "📸 ส่งออก PNG เท่านั้น",
        "settings": "⚙️ ตั้งค่า",
        "compare": "👁️ เปรียบเทียบ",
        "language": "🌐 ภาษา",
        
        # Glyph Table
        "glyph_table": "📋 ตารางอักษร",
        "filter_all": "ทั้งหมด",
        "filter_consonants": "พยัญชนะ",
        "filter_vowels_above": "สระบน",
        "filter_vowels_below": "สระล่าง",
        "filter_tone_marks": "วรรณยุกต์",
        "filter_symbols": "สัญลักษณ์ / เครื่องหมาย",
        "filter_numbers": "ตัวเลข",
        "filter_latin": "ละติน / อังกฤษ",
        "filter_pua": "PUA ผสม",
        "filter_problems": "⚠️ เฉพาะที่มีปัญหา",
        "search_placeholder": "ค้นหา (Unicode / ตัวอักษร)...",
        "col_char": "อักษร",
        "col_unicode": "Unicode",
        "col_category": "หมวด",
        "col_fill": "Fill %",
        "col_status": "สถานะ",
        
        # Preview
        "preview_title": "👁️ พรีวิวแบบ Real-Time",
        "preview_input": "พิมพ์ข้อความเพื่อทดสอบ...",
        "preset_texts": "📝 ข้อความทดสอบ",
        "atlas_title": "🗺️ พรีวิว Atlas",
        "zoom_in": "🔍+",
        "zoom_out": "🔍-",
        "zoom_fit": "พอดี",
        "grid_overlay": "ตาราง",
        
        # Adjust Panel
        "adjust_title": "🔧 แผงปรับแต่ง",
        "x_offset": "เลื่อน X",
        "y_offset": "เลื่อน Y",
        "scale": "ขนาด",
        "width_override": "ความกว้าง",
        "height_override": "ความสูง",
        "advance_override": "ระยะห่าง",
        "reset": "↩️ รีเซ็ต",
        "apply_category": "ใช้กับอักษรหมวดเดียวกัน",
        "quality": "คุณภาพ",
        "fill_w": "Fill W",
        "fill_h": "Fill H",
        "status_ok": "✅ ผ่าน",
        "status_warn": "⚠️ เตือน",
        "status_error": "❌ มีปัญหา",
        
        # Export Dialog
        "export_title": "ตั้งค่าการส่งออก",
        "export_profile": "โปรไฟล์การส่งออก",
        "profile_dl2": "Dying Light 2 / The Beast",
        "profile_bmfont": "BMFont (Unity / Unreal)",
        "profile_json": "JSON Atlas (ทั่วไป)",
        "export_path": "โฟลเดอร์ปลายทาง",
        "export_browse": "เรียกดู...",
        "export_start": "🚀 เริ่มส่งออก",
        "export_cancel": "ยกเลิก",
        "export_base_image": "ภาพต้นฉบับ (Base Image)",
        "export_base_img_ph": "ถ้ามี: เลือกภาพฟอนต์เดิมของเกม...",
        
        # Project
        "project_filter": "ไฟล์โปรเจกต์ PPFS (*.ppfs)",
        "font_filter": "ไฟล์ฟอนต์ (*.ttf *.otf)",
        "mapping_filter": "ไฟล์ Mapping (*.json)",
        "charset_filter": "ไฟล์ชุดอักขระ (*.txt)",
        
        # Status Bar
        "status_ready": "พร้อมใช้งาน",
        "status_font": "ฟอนต์",
        "status_glyphs": "จำนวนอักษร",
        "status_quality": "คุณภาพ",
        "status_no_font": "ยังไม่ได้โหลดฟอนต์",
        
        # Messages
        "msg_font_loaded": "โหลดฟอนต์แล้ว: {}",
        "msg_project_saved": "บันทึกโปรเจกต์แล้ว: {}",
        "msg_project_loaded": "เปิดโปรเจกต์แล้ว: {}",
        "msg_export_done": "ส่งออกเสร็จสมบูรณ์! ไฟล์อยู่ที่: {}",
        "msg_export_error": "เกิดข้อผิดพลาดในการส่งออก: {}",
        "msg_quality_ok": "อักษรทั้ง {} ตัวผ่านการตรวจสอบคุณภาพ!",
        "msg_quality_warn": "มีอักษร {} ตัวที่มีปัญหาคุณภาพ",
        "msg_atlas_overflow": "Atlas เต็ม! พื้นที่ไม่พอสำหรับอักษรทั้งหมด",
        
        # Undo/Redo
        "undo": "เลิกทำ",
        "redo": "ทำซ้ำ",
        
        # Categories
        "cat_consonant": "พยัญชนะ",
        "cat_vowel_above": "สระบน",
        "cat_vowel_below": "สระล่าง",
        "cat_tone_mark": "วรรณยุกต์",
        "cat_symbol": "สัญลักษณ์",
        "cat_number": "ตัวเลข",
        "cat_pua": "PUA",
        "cat_latin": "ละติน",
        "cat_other": "อื่นๆ",
        
        # Preset text labels
        "preset_general": "ทดสอบทั่วไป",
        "preset_sara_ue": "สระ ื + วรรณยุกต์",
        "preset_sara_am": "สระ ำ + วรรณยุกต์",
        "preset_mai_tri": "ทดสอบไม้ตรี",
        "preset_consonants": "พยัญชนะทั้งหมด",
        "preset_english": "อังกฤษ + ตัวเลข",
        "preset_mixed": "ไทย-อังกฤษผสม",
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
