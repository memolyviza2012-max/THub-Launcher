import os
import sys
import json
from pathlib import Path

def get_resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return Path(base_path) / relative_path

_LOCALES = get_resource_path('locales')
_TSTUDIO_LOCALES = Path(os.path.abspath(__file__)).parent.parent / 'TStudio' / 'locales'
_fallback_dict = {
    "app_title": "TFont: ตัวแปลง PUA แบบไฮบริดสากล",
    "tab_text_converter": "แปลงข้อความเป็น PUA",
    "tab_font_generator": "สร้างฟอนต์",
    "grp_file_selection": "เลือกไฟล์",
    "grp_font_settings": "ตั้งค่าฟอนต์",
    "grp_action": "ดำเนินการ",
    "placeholder_input_file": "เลือกไฟล์นำเข้า (.txt, .csv, .json)...",
    "placeholder_output_file": "เลือกไฟล์ส่งออก...",
    "placeholder_font_map": "เลือก Mapping.json (ไม่บังคับ, ค่าเริ่มต้นใช้แผนที่ของ Noonetranslator)",
    "placeholder_font_in": "เลือกไฟล์ฟอนต์ต้นทาง (.ttf)...",
    "placeholder_font_out": "เลือกไฟล์ส่งออก...",
    "btn_browse": "เรียกดู",
    "btn_encode": "เข้ารหัส (ไทย -> PUA)",
    "btn_decode": "ถอดรหัส (PUA -> ไทย)",
    "btn_generate_font": "สร้างฟอนต์ PUA",
    "btn_font_engine_unavailable": "ไม่พบเอนจินฟอนต์ (ขาด fontTools)",
    "dialog_select_input": "เลือกไฟล์นำเข้า",
    "dialog_select_output": "เลือกไฟล์ส่งออก",
    "dialog_select_mapping": "เลือก Mapping.json",
    "dialog_select_font_in": "เลือกไฟล์ฟอนต์ต้นทาง",
    "dialog_select_font_out": "เลือกไฟล์ฟอนต์ส่งออก",
    "msg_input_not_found": "ไม่พบไฟล์นำเข้า!",
    "msg_cannot_read_file": "ไม่สามารถอ่านไฟล์ได้:\n{e}",
    "msg_could_not_read_file": "ไม่สามารถอ่านไฟล์ได้:\n{e}",
    "msg_source_font_not_found": "ไม่พบไฟล์ฟอนต์ต้นทาง",
    "msg_no_output_path": "โปรดระบุเส้นทางส่งออก",
    "msg_error_title": "ข้อผิดพลาด",
    "log_engine_loaded": "โหลดเอนจิน TFont แล้ว แผนที่มาตรฐาน: {std} | ตามบริบท: {ctx}",
    "log_font_engine_loaded": "โหลดเอนจินฟอนต์ TFont แล้ว",
    "log_default_mapping_loaded": "โหลดแผนที่ฟอนต์เริ่มต้น: {count} รายการ",
    "log_custom_mapping_loaded": "โหลดแผนที่ฟอนต์แบบกำหนดเอง: {count} รายการ",
    "log_encoding": "กำลังเข้ารหัสไทยเป็น PUA... โปรดรอ...",
    "log_decoding": "กำลังถอดรหัส PUA เป็นไทย... โปรดรอ...",
    "log_encoded_result": "เข้ารหัสแล้ว! PUA ต้นฉบับ: {orig} -> PUA สุดท้าย: {final} (+{diff})",
    "log_decoded_result": "ถอดรหัสแล้ว! PUA ต้นฉบับ: {orig} -> PUA สุดท้าย: {final} (-{diff})",
    "log_error_encoding": "ข้อผิดพลาดในการเข้ารหัส: {err}",
    "log_error_decoding": "ข้อผิดพลาดในการถอดรหัส: {err}",
    "log_error_saving": "ข้อผิดพลาดในการบันทึก: {err}",
    "log_saved_to": "บันทึกที่: {path}",
    "log_font_gen_start": "กำลังเริ่มสร้างฟอนต์ PUA... โปรดรอ...",
    "log_font_gen_done": "สร้างฟอนต์สำเร็จ!",
    "log_error_font_gen": "ข้อผิดพลาดในการสร้างฟอนต์: {err}",
    "tab_legacy_font": "ฟอนต์ดั้งเดิม F700"
}

_cache = {}

def _load_lang(locales_path, lang):
    p = locales_path / f'{lang}.json'
    if not p.exists():
        p = locales_path / 'th.json'
    try:
        with open(p, encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def _(key, **kw):
    lang = os.environ.get('THUB_LANG', 'th')
    if lang not in _cache:
        # Load TStudio fallback dictionary first (for dev mode in Modder-Hub)
        base_dict = _load_lang(_TSTUDIO_LOCALES, lang)
        
        # Load local tool dictionary and overwrite base
        local_dict = _load_lang(_LOCALES, lang)
        
        merged = base_dict.copy()
        merged.update(local_dict)
        _cache[lang] = merged
        
    val = _cache[lang].get(key, key)
    try:
        return val.format(**kw) if kw else val
    except Exception:
        return val
