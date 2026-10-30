import os
import sys
import json
import csv
import tempfile
import shutil
import re
csv.field_size_limit(2147483647)
import requests

# Use a session for HTTP keep-alive (dramatically speeds up API calls)
from requests.adapters import HTTPAdapter
_session = requests.Session()
_adapter = HTTPAdapter(pool_connections=100, pool_maxsize=100)
_session.mount('http://', _adapter)
_session.mount('https://', _adapter)

if getattr(sys, 'frozen', False) and os.path.basename(sys.executable).lower() in ("tstudio.exe", "tstudio_app.exe", "core.exe"):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_PATH  = os.path.join(BASE_DIR, "config.json")
GLOSSARY_PATH = os.path.join(BASE_DIR, "glossary.json")
PROMPTS_PATH = os.path.join(BASE_DIR, "prompts.json")

# ── CJK Detection & Sanitizer Patterns ──
# Covers CJK Unified Ideographs, Extension A, Compatibility Ideographs, and Symbols/Punctuation
RE_CJK = re.compile(r'[\u4E00-\u9FFF\u3400-\u4DBF\uF900-\uFAFF]')
RE_CJK_ALL = re.compile(r'[\u4E00-\u9FFF\u3400-\u4DBF\uF900-\uFAFF\u3000-\u303F\uFF01-\uFF5E]')
# Covers CJK Ideographs, Japanese Kana (Hiragana & Katakana), Korean Hangul, and Thai
RE_ASIAN_SCRIPTS = re.compile(r'[\u4E00-\u9FFF\u3400-\u4DBF\uF900-\uFAFF\u3040-\u309F\u30A0-\u30FF\u31F0-\u31FF\uAC00-\uD7AF\u1100-\u11FF\u3130-\u318F\u0E00-\u0E7F]')

# Regex patterns for stripping known Chinese AI annotation wrappers
RE_CJK_ANNOTATIONS = [
    re.compile(r'（(?:注|说明|翻译|参考|提示|暂译|解释)[：:][^）]*?）'),
    re.compile(r'\((?:注|说明|翻译|参考|提示|暂译|解释)[：:][^)]*?\)'),
    re.compile(r'【(?:注|说明|翻译|参考|提示|暂译|解释)[：:][^】]*?】'),
    re.compile(r'（[^）]*?[\u4E00-\u9FFF]{2,}[^）]*?）'),  # Parentheses with primarily Chinese text
    re.compile(r'\([^)]*?[\u4E00-\u9FFF]{2,}[^)]*?\)'),
    re.compile(r'【[^】]*?[\u4E00-\u9FFF]{2,}[^】]*?】'),
    re.compile(r'^\s*注[：:].*?$', re.MULTILINE),
]

DEFAULT_SINGLE_PROMPT = """You are a Master-Level Video Game Localization Specialist translating the source language into natural Thai.
Translate this line. ID: '{id}'. Return ONLY the pure Thai string, no quotes, no explanations.
CRITICAL: If the text is short (e.g. less than 5 words), do NOT explain it, do NOT add quotes, do NOT add markdown. ONLY return the direct translation.
STRICT LANGUAGE PURITY & ZERO-ENGLISH RESIDUAL: Return 100% pure Thai. NEVER leave untranslated English words, Chinese characters (汉字), or Japanese Kana in your output. If an English term, slang, or proper noun is not in the glossary, phonetically transliterate it into Thai script (e.g. 'Quest' -> 'เควสต์', 'Night City' -> 'ไนท์ซิตี้', 'Attack' -> 'โจมตี', 'Inventory' -> 'ช่องเก็บของ'). NEVER mix English words into Thai text (no code-switching).
EXCEPTION FOR MILITARY, WEAPONS & VEHICLE NOMENCLATURE:
- DO NOT translate or phonetically transliterate alphanumeric firearm models, military vehicles, calibers, and weapon class acronyms into Thai script.
- KEEP them in original Latin/alphanumeric script:
  * Firearms & Models: 'M16' (NEVER 'เอ็ม 16'), 'M4A1', 'AK-47' (NEVER 'เอเค-47'), 'MP5', 'RPG-7', 'Glock 19', 'AWM', 'Barrett .50'.
  * Weapon Class Acronyms: 'SMG' (NEVER 'เอสเอ็มจี' or literal 'ปืนกลเบา' when referring to the acronym; use 'SMG' or 'ปืน SMG'), 'AR', 'LMG', 'DMR', 'SR', 'SG', 'PDW'.
  * Military Vehicles & Hardware: 'Humvee' (or 'รถ Humvee'), 'APC' (or 'รถหุ้มเกราะ APC'), 'VTOL', 'UAV', 'BTR-80', 'T-72', 'F-16'.
  * Calibers: '9mm', '5.56mm', '7.62mm', '.50 Cal', '12 Gauge'.
EXCEPTION FOR KEYBOARD KEYS, MOUSE & CONTROLLER INPUTS:
- DO NOT translate or phonetically transliterate PC keyboard keys, mouse buttons, and gamepad controls into Thai script.
- Keep standard keybind names in original Latin script:
  * Keyboard Keys: 'Spacebar' or 'Space' (NEVER 'สเปคบรา', NEVER 'สเปซบาร์', NEVER literal 'เว้นวรรค' or 'คานอวกาศ'), 'Enter' (NEVER 'เอ็นเทอ', NEVER 'เอนเทอร์', NEVER literal 'ป้อน' or 'เข้าไป'), 'Shift' (NEVER 'ชิฟต์'), 'Ctrl' (NEVER 'คอนโทรล'), 'Alt' (NEVER 'อัลต์'), 'Tab' (NEVER 'แท็บ'), 'Esc' / 'Escape' (NEVER 'เอสเคป'), 'Backspace' (NEVER 'แบ็กสเปซ'), 'Delete' / 'Del', 'Insert' / 'Ins' (NEVER 'แทรก'), 'Caps Lock', 'Num Lock', 'Scroll Lock', 'Page Up', 'Page Down', 'Home', 'End' (NEVER 'จบ'), 'Pause' (NEVER 'หยุดชั่วคราว'), 'Print Screen' (NEVER 'พิมพ์หน้าจอ'), 'WASD'.
  * Mouse & Gamepad: 'LMB', 'RMB', 'MMB', 'Mouse Wheel', 'Mouse 1'-'Mouse 8', 'D-pad', 'RT', 'LT', 'RB', 'LB', 'R3', 'L3'.
  * In Thai sentences, use standard gaming notation e.g. "กด [Spacebar] เพื่อกระโดด", "กด [Enter] เพื่อยืนยัน", "กดปุ่ม [Shift] ซ้าย".

[GLOSSARY TO USE]

Text: {source_text}"""

DEFAULT_OPTIONS_PROMPT = """You are a Master-Level Video Game Localization Specialist translating the source language into natural Thai.
Translate this into 3 distinct styles:
1. Literal/Direct (แปลตรงตัว)
2. Casual/Slang (ภาษาพูด/สแลง)
3. Polite/Formal (สุภาพ/ทางการ)
ID: '{id}'.
STRICT LANGUAGE PURITY & ZERO-ENGLISH RESIDUAL: Return 100% pure Thai across all 3 options. NEVER leave untranslated English words, Chinese characters (汉字), or Japanese Kana. If an English term, slang, or proper noun is not in the glossary, phonetically transliterate it into Thai script (e.g. 'Quest' -> 'เควสต์', 'Night City' -> 'ไนท์ซิตี้'). NEVER mix English words into Thai text (no code-switching).
EXCEPTION FOR MILITARY, WEAPONS & VEHICLE NOMENCLATURE:
- DO NOT translate or phonetically transliterate alphanumeric firearm models, military vehicles, calibers, and weapon class acronyms into Thai script. Keep them intact in original Latin/alphanumeric (e.g. 'M16' NEVER 'เอ็ม 16', 'AK-47', 'SMG' NEVER 'เอสเอ็มจี'/'ปืนกลเบา', 'RPG-7', 'Humvee', 'APC', '9mm').
EXCEPTION FOR KEYBOARD KEYS, MOUSE & CONTROLLER INPUTS:
- DO NOT translate or phonetically transliterate PC keyboard keys, mouse buttons, and gamepad controls into Thai script (e.g. 'Spacebar' NEVER 'สเปคบรา', 'Enter' NEVER 'เอ็นเทอ'/'ป้อน', 'Shift', 'Ctrl', 'Alt', 'Tab', 'Esc', 'Backspace', 'WASD', 'LMB', 'RMB'). Keep them in original Latin script.

[GLOSSARY TO USE]

Return ONLY a valid JSON array of 3 strings: ["option1", "option2", "option3"]
Text: {source_text}"""

class TStudioCore:
    _PROJECT_PATH = None

    @classmethod
    def set_project_path(cls, path):
        cls._PROJECT_PATH = path

    @classmethod
    def get_project_path(cls):
        return cls._PROJECT_PATH

    @classmethod
    def get_project_source_lang(cls):
        """Get source language from thub_project.json if available, default to None."""
        if cls._PROJECT_PATH:
            thub_meta = os.path.join(cls._PROJECT_PATH, "thub_project.json")
            if os.path.exists(thub_meta):
                try:
                    with open(thub_meta, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                    return meta.get("source_lang")
                except Exception:
                    pass
        return None
    
    @staticmethod
    def has_cjk(text):
        """Check if string contains any Chinese/CJK characters."""
        if not text or not isinstance(text, str):
            return False
        return bool(RE_CJK.search(text))

    @staticmethod
    def has_cjk_or_kana(text):
        """Check if string contains Chinese (Hanzi/Kanji), Japanese (Hiragana/Katakana), Korean, or Thai characters."""
        if not text or not isinstance(text, str):
            return False
        return bool(RE_ASIAN_SCRIPTS.search(text))

    @staticmethod
    def extract_cjk(text):
        """Return list of unique CJK characters found in text."""
        if not text or not isinstance(text, str):
            return []
        return list(dict.fromkeys(RE_CJK.findall(text)))

    @staticmethod
    def clean_cjk_leak(text):
        """Safely strip known AI commentary wrappers in Chinese (e.g. （注：...）, (注: ...))."""
        if not text or not isinstance(text, str):
            return "" if text is None else text
        cleaned = re.sub(r'[（\(]\s*(?:注|註|说明|說明|翻译|翻譯|注意)[\s\S]*?[）\)]', '', text)
        return cleaned.strip() if cleaned.strip() else text

    COMMON_ALLOWED_GAMING_ACRONYMS = {
        # Core Gaming Stats & UI
        "hp", "mp", "sp", "exp", "xp", "ap", "cp", "dp", "lv", "lvl",
        "ui", "hud", "id", "ok", "cd", "fps", "npc", "ai", "dps", "pvp", "pve",
        "fov", "ads", "aoe", "dot", "cc", "rng", "buff", "debuff", "mod", "mods",
        # Firearms, Weapons & Military Hardware
        "smg", "ar", "lmg", "dmr", "sr", "sg", "pdw", "rpg", "atgm",
        "apc", "ifv", "uav", "vtol", "emp", "c4", "atv", "ied", "sam",
        "flak", "ciws", "humvee", "glock", "beretta", "remington", "colt",
        # Standard PC & Console Input Controls (Keyboard, Mouse, Gamepad)
        "spacebar", "space", "enter", "shift", "ctrl", "alt", "tab", "esc", "escape",
        "backspace", "delete", "del", "insert", "ins", "capslock", "caps", "numlock",
        "scrolllock", "pageup", "pagedown", "pgup", "pgdn", "home", "end", "pause",
        "prtscr", "printscreen", "wasd", "lmb", "rmb", "mmb", "mouse1", "mouse2",
        "mouse3", "mouse4", "mouse5", "mouse6", "mouse7", "mouse8", "dpad", "lb", "rb",
        "lt", "rt", "l1", "r1", "l2", "r2", "l3", "r3"
    }

    @classmethod
    def extract_english_leaks(cls, text, allowed_words=None):
        """
        Extract standalone English words (>= 2 letters) that leaked into translated text,
        ignoring standard game tags, placeholders, URLs, universal game acronyms (HP, MP, LV, etc.),
        and alphanumeric firearm/model/caliber designations (M16, AK-47, MP5, BTR-80, 9mm, 5.56mm).
        """
        if not text or not isinstance(text, str):
            return []
        # 1. Strip URLs
        cleaned = re.sub(r'https?://\S+', ' ', text)
        # 2. Strip game tags (<...>, {...}, [...], %s, \n, [TAG_...])
        cleaned = re.sub(r'\[TAG_\d+\]|<[^>]+>|\{[^}]*\}|\[\[[^\]]*\]\]|%[a-zA-Z]|\\[nrt]', ' ', cleaned)
        # 3. Strip alphanumeric firearm models, vehicles, and calibers (e.g. M16, AK-47, MP5, BTR-80, 9mm, 5.56mm)
        cleaned = re.sub(r'(?:\b|\.)(?=[A-Za-z0-9\-_\.]*\d)[A-Za-z0-9]+(?:[-_\.][A-Za-z0-9]+)*\b', ' ', cleaned)
        # 4. Find alphabetic words with length >= 2
        words = re.findall(r'\b[A-Za-z]{2,}\b', cleaned)
        if not words:
            return []
        # 5. Filter against universal acronyms and explicit allowed terms
        allowed = set(cls.COMMON_ALLOWED_GAMING_ACRONYMS)
        if allowed_words:
            for w in allowed_words:
                if isinstance(w, str) and w.strip():
                    allowed.add(w.strip().lower())
        leaked = [w for w in words if w.lower() not in allowed]
        return list(dict.fromkeys(leaked))

    @classmethod
    def has_english_leak(cls, text, allowed_words=None, min_words=1):
        """Check if text contains untranslated English words outside tags."""
        return len(cls.extract_english_leaks(text, allowed_words)) >= min_words

    # Phonetic mappings for dynamic alphanumeric model code restoration (e.g. X-99, V-77, ARC-9, Mk.IV, M16)
    THAI_LETTER_MAP = {
        'A': r'(?:เอ|แอลฟา|อัลฟา|A)', 'B': r'(?:บี|เบตา|เบต้า|B)', 'C': r'(?:ซี|C)', 'D': r'(?:ดี|เดลตา|เดลต้า|D)',
        'E': r'(?:อี|E)', 'F': r'(?:เอฟ|F)', 'G': r'(?:จี|แกมมา|G)', 'H': r'(?:เอช|เฮช|H)',
        'I': r'(?:ไอ|I)', 'J': r'(?:เจ|J)', 'K': r'(?:เค|K)', 'L': r'(?:แอล|L)',
        'M': r'(?:เอ็ม|เอม|M)', 'N': r'(?:เอ็น|เอน|N)', 'O': r'(?:โอ|โอเมกา|โอเมก้า|O)', 'P': r'(?:พี|P)',
        'Q': r'(?:คิว|Q)', 'R': r'(?:อาร์|อาร|R)', 'S': r'(?:เอส|ซิกมา|S)', 'T': r'(?:ที|เธตา|ทีตา|T)',
        'U': r'(?:ยู|U)', 'V': r'(?:วี|V)', 'W': r'(?:ดับบลิว|ดับเบิลยู|W)',
        'X': r'(?:เอ็กซ์|เอกซ์|เอ๊กซ์|เอ็กซ|X)', 'Y': r'(?:วาย|Y)', 'Z': r'(?:แซด|ซี|เซด|Z)'
    }
    THAI_DIGIT_MAP = {
        '0': r'(?:0|ศูนย์|๐)', '1': r'(?:1|หนึ่ง|เอ็ด|๑)', '2': r'(?:2|สอง|โท|๒)', '3': r'(?:3|สาม|๓)',
        '4': r'(?:4|สี่|๔)', '5': r'(?:5|ห้า|๕)', '6': r'(?:6|หก|๖)', '7': r'(?:7|เจ็ด|๗)',
        '8': r'(?:8|แปด|๘)', '9': r'(?:9|เก้า|๙)'
    }

    @classmethod
    def _int_to_thai_words(cls, num):
        if not (0 <= num <= 99):
            return None
        units = ["ศูนย์", "หนึ่ง", "สอง", "สาม", "สี่", "ห้า", "หก", "เจ็ด", "แปด", "เก้า"]
        if num < 10:
            return units[num]
        tens = num // 10
        rem = num % 10
        ten_str = "สิบ" if tens == 1 else ("ยี่สิบ" if tens == 2 else units[tens] + "สิบ")
        unit_str = "เอ็ด" if rem == 1 else (units[rem] if rem > 0 else "")
        return ten_str + unit_str

    @classmethod
    def build_thai_phonetic_regex_for_code(cls, code_str):
        """
        Dynamically constructs a high-precision regex matching how Thai LLMs/translators
        transliterated ANY futuristic or military alphanumeric code (e.g. X-99, V-77, ARC-9, Mk.IV, M16).
        """
        code_str = code_str.strip()
        mk_match = re.match(r'^(?:Mk|Mark)\.?\s*([IVXLCDM\d]+)$', code_str, re.IGNORECASE)
        if mk_match:
            val = mk_match.group(1)
            num_map = {'1':'หนึ่ง|1|๑|I', '2':'สอง|2|๒|II', '3':'สาม|3|๓|III', '4':'สี่|4|๔|IV', '5':'ห้า|5|๕|V',
                       'I':'1|หนึ่ง|๑|I', 'II':'2|สอง|๒|II', 'III':'3|สาม|๓|III', 'IV':'4|สี่|๔|IV', 'V':'5|ห้า|๕|V'}
            th_val = num_map.get(val.upper(), re.escape(val))
            return rf'(?:มาร์ก|มาร์ค|มาร์กเกอร์|มาร์คเกอร์)\s*(?:\.|\s)*\s*(?:{th_val})'

        parts = re.split(r'([-_./\s])', code_str)
        regex_parts = []
        for p in parts:
            if not p:
                continue
            if p in '-_./':
                regex_parts.append(r'\s*[-_./–—]?\s*')
            elif p.isalpha():
                th_letters = [cls.THAI_LETTER_MAP.get(ch, re.escape(ch)) for ch in p.upper()]
                combo = r'\s*'.join(th_letters)
                regex_parts.append(rf'(?:{combo}|{re.escape(p)})')
            elif p.isdigit():
                th_digits = [cls.THAI_DIGIT_MAP.get(d, d) for d in p]
                digit_seq = r'\s*'.join(th_digits)
                variants = [digit_seq, re.escape(p)]
                if len(p) <= 2:
                    tw = cls._int_to_thai_words(int(p))
                    if tw:
                        variants.append(tw)
                regex_parts.append(rf'(?:{"|".join(variants)})')
            else:
                regex_parts.append(re.escape(p))
        return ''.join(regex_parts)

    MILITARY_RETROFIT_RULES = [
        # category, src_pattern, trans_pattern, rep_func, desc
        # 1. Firearm Models
        ('weapons', r'\bM16(?:A\d)?\b', r'เอ็ม\s*-?\s*16(?:\s*เอ\s*\d)?|เอ็มสิบหก', lambda m, src: re.search(r'\bM16(?:A\d)?\b', src, re.I).group(0), 'M16'),
        ('weapons', r'\bAK-?47\b', r'เอเค\s*-?\s*47|เอเคสี่สิบเจ็ด|อาก้า\s*47', lambda m, src: 'AK-47', 'AK-47'),
        ('weapons', r'\bAK-?74\b', r'เอเค\s*-?\s*74|เอเคเจ็ดสิบสี่', lambda m, src: 'AK-74', 'AK-74'),
        ('weapons', r'\bM4(?:A1)?\b', r'เอ็ม\s*-?\s*4(?:\s*เอ\s*1)?|เอ็มสี่\s*(?:เอวัน)?|เอ็มโฟร์', lambda m, src: re.search(r'\bM4(?:A1)?\b', src, re.I).group(0), 'M4'),
        ('weapons', r'\bMP5\b', r'เอ็มพี\s*-?\s*5|เอ็มพีห้า', lambda m, src: 'MP5', 'MP5'),
        ('weapons', r'\bMP7\b', r'เอ็มพี\s*-?\s*7|เอ็มพีเจ็ด', lambda m, src: 'MP7', 'MP7'),
        ('weapons', r'\bRPG(?:-?7)?\b', r'อาร์พีจี\s*-?\s*7|อาร์พีจีเจ็ด', lambda m, src: re.search(r'\bRPG(?:-?7)?\b', src, re.I).group(0), 'RPG-7'),
        ('weapons', r'\bP90\b', r'พี\s*-?\s*90|พีเก้าสิบ', lambda m, src: 'P90', 'P90'),
        ('weapons', r'\bUMP(?:45|9|40)?\b', r'ยูเอ็มพี\s*(?:45|9|40)?', lambda m, src: re.search(r'\bUMP(?:45|9|40)?\b', src, re.I).group(0), 'UMP'),
        ('weapons', r'\bUZI\b', r'อูซี่|อูซี', lambda m, src: 'UZI', 'UZI'),
        ('weapons', r'\bDesert\s*Eagle\b', r'ดีเซิร์[ทต]อีเกิล|เดสเสิร์[ทต]อีเกิล|อินทรีทะเลทราย', lambda m, src: 'Desert Eagle', 'Desert Eagle'),
        ('weapons', r'\bAWM\b', r'เอดับบลิวเอ็ม', lambda m, src: 'AWM', 'AWM'),
        ('weapons', r'\bAWP\b', r'เอดับบลิวพี', lambda m, src: 'AWP', 'AWP'),
        ('weapons', r'\bBarrett\b', r'บาร์เร็ตต์|บาเร็ตต์', lambda m, src: 'Barrett', 'Barrett'),
        ('weapons', r'\bGlock(?:\s*\d+)?\b', r'กล็อก(?:\s*\d+)?', lambda m, src: re.search(r'\bGlock(?:\s*\d+)?\b', src, re.I).group(0), 'Glock'),
        ('weapons', r'\bSCAR(?:-[HL])?\b', r'สการ์(?:\s*-[HLhl])?', lambda m, src: re.search(r'\bSCAR(?:-[HL])?\b', src, re.I).group(0), 'SCAR'),
        ('weapons', r'\bM249\b', r'เอ็ม\s*249', lambda m, src: 'M249', 'M249'),
        ('weapons', r'\bM60\b', r'เอ็ม\s*60', lambda m, src: 'M60', 'M60'),
        ('weapons', r'\bM24\b', r'เอ็ม\s*24', lambda m, src: 'M24', 'M24'),
        ('weapons', r'\bSVD\b', r'เอสวีดี', lambda m, src: 'SVD', 'SVD'),
        ('weapons', r'\bHK-?416\b', r'เอชเค\s*-?\s*416', lambda m, src: 'HK416', 'HK416'),

        # 2. Weapon Class Acronyms
        ('acronyms', r'\bSMG\b', r'ปืน\s*ปืนกลเบา|ปืนกลเบา|เอสเอ็มจี', lambda m, src: 'ปืน SMG' if not m.group(0).startswith('ปืน') else 'SMG', 'SMG'),
        ('acronyms', r'\bLMG\b', r'แอลเอ็มจี|ปืนกลเบาหนัก', lambda m, src: 'LMG', 'LMG'),
        ('acronyms', r'\bDMR\b', r'ดีเอ็มอาร์', lambda m, src: 'DMR', 'DMR'),
        ('acronyms', r'\bAR\b', r'เออาร์', lambda m, src: 'AR', 'AR'),

        # 3. Military Vehicles & Hardware
        ('vehicles', r'\b(?:Humvee|HMMWV)\b', r'รถ\s*ฮัมวี|ฮัมวี|ฮัมวี่', lambda m, src: 'รถ Humvee', 'Humvee'),
        ('vehicles', r'\bAPC\b', r'รถเกราะ\s*เอพีซี|เอพีซี|ยานเกราะลำเลียงพล|รถลำเลียงพลหุ้มเกราะ', lambda m, src: 'รถเกราะ APC', 'APC'),
        ('vehicles', r'\bIFV\b', r'ไอเอฟวี|ยานเกราะต่อสู้ทหารราบ', lambda m, src: 'รถรบ IFV', 'IFV'),
        ('vehicles', r'\bTank\s*Destroyer\b', r'ผู้ทำลายรถถัง', lambda m, src: 'รถถังพิฆาต', 'Tank Destroyer'),
        ('vehicles', r'\bGunship\b', r'เรือปืน', lambda m, src: 'กันชิป', 'Gunship'),
        ('vehicles', r'\bVTOL\b', r'ยาน\s*วีทอล|วีทอล|วีท็อล', lambda m, src: 'ยาน VTOL', 'VTOL'),
        ('vehicles', r'\bUAV\b', r'โดรน\s*ยูเอวี|ยูเอวี', lambda m, src: 'โดรน UAV', 'UAV'),
        ('vehicles', r'\bBTR-?(\d+)\b', r'บีทีอาร์\s*-?\s*(\d+)?', lambda m, src: re.search(r'\bBTR-?\d+\b', src, re.I).group(0), 'BTR'),
        ('vehicles', r'\bAbrams\b', r'รถถัง\s*เอบรามส์|เอบรามส์', lambda m, src: 'รถถัง Abrams', 'Abrams'),

        # 4. Calibers / Ammo
        ('calibers', r'\b9mm\b', r'๙\s*มม\.?|เก้ามิลลิเมตร', lambda m, src: '9mm', '9mm'),
        ('calibers', r'\b5\.56mm\b', r'๕\.๕๖\s*มม\.?|ห้าจุดห้าหกมิลลิเมตร', lambda m, src: '5.56mm', '5.56mm'),
        ('calibers', r'\b7\.62mm\b', r'๗\.๖๒\s*มม\.?|เจ็ดจุดหกสองมิลลิเมตร', lambda m, src: '7.62mm', '7.62mm'),
        ('calibers', r'\b\.50(?:\s*cal)?\b', r'จุดห้าศูนย์(?:\s*แคล)?|จุดห้าสิบ', lambda m, src: '.50 Cal', '.50 Cal'),

        # 5. Futuristic, Sci-Fi Weapons & Vehicles
        ('scifi', r'\bRailgun\b', r'ปืนราง|ปืนเรล(?!กัน)', lambda m, src: 'ปืนเรลกัน', 'Railgun ➔ ปืนเรลกัน'),
        ('scifi', r'\bCoilgun\b', r'ปืนขดลวด|ปืนคอยล์(?!กัน)', lambda m, src: 'ปืนคอยล์กัน', 'Coilgun ➔ ปืนคอยล์กัน'),
        ('scifi', r'\bPulse\s*Cannon\b', r'(?:ปืนใหญ่|แคนนอน)\s*ชีพจร', lambda m, src: 'ปืนใหญ่พัลส์', 'Pulse Cannon ➔ ปืนใหญ่พัลส์'),
        ('scifi', r'\bPulse\s*Rifle\b', r'(?:ปืนไรเฟิล|ปืนยาว)\s*ชีพจร', lambda m, src: 'พัลส์ไรเฟิล', 'Pulse Rifle ➔ พัลส์ไรเฟิล'),
        ('scifi', r'\bPulse\s*Laser\b', r'เลเซอร์\s*ชีพจร', lambda m, src: 'พัลส์เลเซอร์', 'Pulse Laser ➔ พัลส์เลเซอร์'),
        ('scifi', r'\bPlasma\s*Rifle\b', r'ปืนไรเฟิลพลาสมา', lambda m, src: 'ปืนพลาสมาไรเฟิล', 'Plasma Rifle ➔ ปืนพลาสมาไรเฟิล'),
        ('scifi', r'\bIon\s*Blaster\b', r'ปืนระเบิดไอออน|เครื่องยิงไอออน|ปืนบลาสเตอร์ไอออน', lambda m, src: 'ไอออนบลาสเตอร์', 'Ion Blaster ➔ ไอออนบลาสเตอร์'),
        ('scifi', r'\bLaser\s*Carbine\b', r'ปืนสั้นเลเซอร์', lambda m, src: 'เลเซอร์คาร์ไบน์', 'Laser Carbine ➔ เลเซอร์คาร์ไบน์'),
        ('scifi', r'\b(?:Heavy\s*)?Bolter\b', r'ปืนยิงสลักเกลียวหนัก', lambda m, src: 'ปืนโบลเตอร์หนัก', 'Heavy Bolter ➔ ปืนโบลเตอร์หนัก'),
        ('scifi', r'\b(?:Heavy\s*)?Bolter\b', r'ปืนยิงสลักเกลียว|ปืนสลักเกลียว|ปืนสลัก', lambda m, src: 'ปืนโบลเตอร์', 'Bolter ➔ ปืนโบลเตอร์'),
        ('scifi', r'\bDropship\b', r'เรือทิ้ง|ยานทิ้ง|ยานหย่อน', lambda m, src: 'ยานดรอปชิป', 'Dropship ➔ ยานดรอปชิป'),
        ('scifi', r'\bHovertank\b', r'รถถังเลื่อนลอย|รถถังลอย', lambda m, src: 'รถถังโฮเวอร์', 'Hovertank ➔ รถถังโฮเวอร์'),
        ('scifi', r'\b(?:Mecha|Mech)\b', r'เครื่องจักรกลรบ|เครื่องจักรกล(?!รบ)|เครื่องจักร(?!กล)', lambda m, src: 'หุ่นรบเมคา', 'Mecha ➔ หุ่นรบเมคา'),
        ('scifi', r'\bExosuit\b', r'ชุดสูทภายนอก|ชุดคลุมภายนอก', lambda m, src: 'ชุดเกราะเอ็กโซสูท', 'Exosuit ➔ ชุดเกราะเอ็กโซสูท'),
        ('scifi', r'\bDreadnought\b', r'ผู้ไร้ความกลัว|เรือประจัญบานเดรดนอต', lambda m, src: 'หุ่นรบเดรดนอต์', 'Dreadnought ➔ หุ่นรบเดรดนอต์'),
        ('scifi', r'\bDisruptor\b', r'เครื่องรบกวน|ตัวก่อกวน|เครื่องทำลายล้าง', lambda m, src: 'ดิสรัปเตอร์', 'Disruptor ➔ ดิสรัปเตอร์'),
        ('scifi', r'\bBlaster\b', r'ปืนระเบิด(?!ขวด)|เครื่องยิงระเบิด', lambda m, src: 'บลาสเตอร์', 'Blaster ➔ บลาสเตอร์'),
        ('scifi', r'\bScattergun\b', r'ปืนกระจาย', lambda m, src: 'สแคตเตอร์กัน', 'Scattergun ➔ สแคตเตอร์กัน'),
        ('scifi', r'\bArc\s*(?:Thrower|Rifle)\b', r'เครื่องขว้างส่วนโค้ง|ปืนส่วนโค้ง', lambda m, src: 'อาร์กโทรเวอร์', 'Arc Thrower ➔ อาร์กโทรเวอร์'),
        ('scifi', r'\bGauss\s*(?:Rifle|Cannon)\b', r'ปืนไรเฟิลเกาส์|ปืนใหญ่เกาส์|ปืนเกาส์เซียน', lambda m, src: 'เกาส์ไรเฟิล', 'Gauss Rifle ➔ เกาส์ไรเฟิล'),
        ('scifi', r'\bSmart\s*(?:Gun|Pistol)\b', r'ปืนฉลาด|ปืนพกฉลาด', lambda m, src: 'สมาร์ตกัน', 'Smart Gun ➔ สมาร์ตกัน'),

        # 6. Keyboard, Mouse & Gamepad Input Controls
        ('keys', r'\b(?:space\s*bar|spacebar)\b', r'(?<![ก-๙])(?:สเปคบรา|สเปซบรา|สเปซบาร์|สเปซบาร|สเปซ|คานอวกาศ)(?![ก-๙])', lambda m, src: 'Spacebar', 'Spacebar ➔ Spacebar'),
        ('keys', r'^\s*SPACE\s*$', r'^.*$', lambda m, src: 'Space', 'SPACE ➔ Space'),
        ('keys', r'\bSpace\b', r'(?<![ก-๙])(?:สเปคบรา|สเปซบรา)(?![ก-๙])', lambda m, src: 'Space', 'Space ➔ Space'),

        # Enter
        ('keys', r'^\s*ENTER\s*$', r'^.*$', lambda m, src: 'Enter', 'ENTER ➔ Enter'),
        ('keys', r'^\s*ENTER\s*\(\s*KEYPAD\s*\)\s*$', r'^.*$', lambda m, src: 'Enter (แป้นตัวเลข)', 'ENTER (KEYPAD) ➔ Enter (แป้นตัวเลข)'),
        ('keys', r'\bEnter\b', r'(?<![ก-๙])(?:เอ็นเทอ|เอ็นเทอร์|เอนเทอร์)(?![ก-๙])', lambda m, src: 'Enter', 'Enter ➔ Enter'),

        # Escape
        ('keys', r'^\s*(?:ESCAPE|ESC)\s*$', r'^.*$', lambda m, src: 'Esc', 'ESCAPE ➔ Esc'),
        ('keys', r'\b(?:Escape|Esc)\b', r'(?<![ก-๙])เอสเคป(?![ก-๙])', lambda m, src: 'Esc' if 'esc' in src.lower() else 'Escape', 'Escape ➔ Esc/Escape'),

        # Backspace
        ('keys', r'^\s*BACKSPACE\s*$', r'^.*$', lambda m, src: 'Backspace', 'BACKSPACE ➔ Backspace'),
        ('keys', r'\bBackspace\b', r'(?<![ก-๙])แบ็กสเปซ(?![ก-๙])', lambda m, src: 'Backspace', 'Backspace ➔ Backspace'),

        # Shift / Ctrl / Alt
        ('keys', r'^\s*LEFT\s*SHIFT\s*$', r'^.*$', lambda m, src: 'Left Shift', 'LEFT SHIFT ➔ Left Shift'),
        ('keys', r'^\s*RIGHT\s*SHIFT\s*$', r'^.*$', lambda m, src: 'Right Shift', 'RIGHT SHIFT ➔ Right Shift'),
        ('keys', r'^\s*LEFT\s*(?:CONTROL|CTRL)\s*$', r'^.*$', lambda m, src: 'Left Ctrl', 'LEFT CONTROL ➔ Left Ctrl'),
        ('keys', r'^\s*RIGHT\s*(?:CONTROL|CTRL)\s*$', r'^.*$', lambda m, src: 'Right Ctrl', 'RIGHT CONTROL ➔ Right Ctrl'),
        ('keys', r'^\s*LEFT\s*ALT\s*$', r'^.*$', lambda m, src: 'Left Alt', 'LEFT ALT ➔ Left Alt'),
        ('keys', r'^\s*RIGHT\s*ALT\s*$', r'^.*$', lambda m, src: 'Right Alt', 'RIGHT ALT ➔ Right Alt'),
        ('keys', r'^\s*LWIN\s*$', r'^.*$', lambda m, src: 'Left Win', 'LWIN ➔ Left Win'),
        ('keys', r'^\s*RWIN\s*$', r'^.*$', lambda m, src: 'Right Win', 'RWIN ➔ Right Win'),
        ('keys', r'\bLeft\s*Shift\b', r'ชิฟต์ซ้าย|ชิฟท์ซ้าย', lambda m, src: 'Shift ซ้าย', 'Left Shift ➔ Shift ซ้าย'),
        ('keys', r'\bRight\s*Shift\b', r'ชิฟต์ขวา|ชิฟท์ขวา', lambda m, src: 'Shift ขวา', 'Right Shift ➔ Shift ขวา'),
        ('keys', r'\bShift\b', r'(?<![ก-๙])(?:ชิฟต์|ชิฟท์)(?![ก-๙])', lambda m, src: 'Shift', 'Shift ➔ Shift'),
        ('keys', r'\bLeft\s*(?:Control|Ctrl)\b', r'คอนโทรลซ้าย', lambda m, src: 'Ctrl ซ้าย', 'Left Control ➔ Ctrl ซ้าย'),
        ('keys', r'\bRight\s*(?:Control|Ctrl)\b', r'คอนโทรลขวา', lambda m, src: 'Ctrl ขวา', 'Right Control ➔ Ctrl ขวา'),
        ('keys', r'\b(?:Control|Ctrl)\b', r'(?<![ก-๙])คอนโทรล(?![ก-๙])', lambda m, src: 'Ctrl', 'Control ➔ Ctrl'),
        ('keys', r'\bLeft\s*Alt\b', r'อัลต์ซ้าย|อัลท์ซ้าย', lambda m, src: 'Alt ซ้าย', 'Left Alt ➔ Alt ซ้าย'),
        ('keys', r'\bRight\s*Alt\b', r'อัลต์ขวา|อัลท์ขวา', lambda m, src: 'Alt ขวา', 'Right Alt ➔ Alt ขวา'),
        ('keys', r'\bAlt\b', r'(?<![ก-๙])(?:อัลต์|อัลท์)(?![ก-๙])', lambda m, src: 'Alt', 'Alt ➔ Alt'),
        ('keys', r'^\s*TAB\s*$', r'^.*$', lambda m, src: 'Tab', 'TAB ➔ Tab'),
        ('keys', r'\bTab\b', r'(?<![ก-๙])แท็บ(?![ก-๙])', lambda m, src: 'Tab', 'Tab ➔ Tab'),

        # Del / Ins
        ('keys', r'^\s*DEL\s*\(\s*KEYPAD\s*\)\s*$', r'^.*$', lambda m, src: 'Del (แป้นตัวเลข)', 'DEL (KEYPAD) ➔ Del (แป้นตัวเลข)'),
        ('keys', r'^\s*DEL(?:ETE)?\s*$', r'^.*$', lambda m, src: 'Delete', 'DELETE ➔ Delete'),
        ('keys', r'\bDelete\b', r'(?<![ก-๙])ดีลีต(?![ก-๙])', lambda m, src: 'Delete', 'Delete ➔ Delete'),
        ('keys', r'^\s*INS(?:ERT)?\s*\(\s*KEYPAD\s*\)\s*$', r'^.*$', lambda m, src: 'Insert (แป้นตัวเลข)', 'INS (KEYPAD) ➔ Insert (แป้นตัวเลข)'),
        ('keys', r'^\s*INS(?:ERT)?\s*$', r'^.*$', lambda m, src: 'Insert', 'INSERT ➔ Insert'),
        ('keys', r'\bInsert\b', r'(?<![ก-๙])อินเสิร์ต(?![ก-๙])', lambda m, src: 'Insert', 'Insert ➔ Insert'),

        # End / Home
        ('keys', r'^\s*END\s*\(\s*KEYPAD\s*\)\s*$', r'^.*$', lambda m, src: 'End (แป้นตัวเลข)', 'END (KEYPAD) ➔ End (แป้นตัวเลข)'),
        ('keys', r'^\s*END\s*$', r'^.*$', lambda m, src: 'End', 'END ➔ End'),
        ('keys', r'^\s*HOME\s*\(\s*KEYPAD\s*\)\s*$', r'^.*$', lambda m, src: 'Home (แป้นตัวเลข)', 'HOME (KEYPAD) ➔ Home (แป้นตัวเลข)'),
        ('keys', r'^\s*HOME\s*$', r'^.*$', lambda m, src: 'Home', 'HOME ➔ Home'),

        # Page Up / Down
        ('keys', r'^\s*PAGE\s*UP\s*\(\s*KEYPAD\s*\)\s*$', r'^.*$', lambda m, src: 'Page Up (แป้นตัวเลข)', 'PAGE UP (KEYPAD) ➔ Page Up (แป้นตัวเลข)'),
        ('keys', r'^\s*PAGE\s*UP\s*$', r'^.*$', lambda m, src: 'Page Up', 'PAGE UP ➔ Page Up'),
        ('keys', r'^\s*PAGE\s*DOWN\s*\(\s*KEYPAD\s*\)\s*$', r'^.*$', lambda m, src: 'Page Down (แป้นตัวเลข)', 'PAGE DOWN (KEYPAD) ➔ Page Down (แป้นตัวเลข)'),
        ('keys', r'^\s*PAGE\s*DOWN\s*$', r'^.*$', lambda m, src: 'Page Down', 'PAGE DOWN ➔ Page Down'),

        # Locks & Pause & Print
        ('keys', r'^\s*CAPS\s*LOCK\s*$', r'^.*$', lambda m, src: 'Caps Lock', 'CAPS LOCK ➔ Caps Lock'),
        ('keys', r'\bCaps\s*Lock\b', r'(?<![ก-๙])แคปส์ล็อก(?![ก-๙])', lambda m, src: 'Caps Lock', 'Caps Lock ➔ Caps Lock'),
        ('keys', r'^\s*NUM\s*LOCK\s*$', r'^.*$', lambda m, src: 'Num Lock', 'NUM LOCK ➔ Num Lock'),
        ('keys', r'\bNum\s*Lock\b', r'ล็อกตัวเลข|นัมล็อก', lambda m, src: 'Num Lock', 'Num Lock ➔ Num Lock'),
        ('keys', r'^\s*SCROLL(?:\s*LOCK)?\s*$', r'^.*$', lambda m, src: 'Scroll Lock', 'SCROLL ➔ Scroll Lock'),
        ('keys', r'^\s*PAUSE\s*$', r'^.*$', lambda m, src: 'Pause', 'PAUSE ➔ Pause'),
        ('keys', r'^\s*PRINT\s*SCREEN\s*$', r'^.*$', lambda m, src: 'Print Screen', 'PRINT SCREEN ➔ Print Screen'),
        ('keys', r'\bPrint\s*Screen\b', r'พิมพ์หน้าจอ|พรินต์สกรีน', lambda m, src: 'Print Screen', 'Print Screen ➔ Print Screen'),

        # Keypad Symbols & Numbers
        ('keys', r'(\d+)\s*\(\s*KEYPAD\s*\)', r'(\d+)\s*\(\s*คีย์แพด\s*\)', lambda m, src: f"{m.group(1)} (แป้นตัวเลข)", 'Keypad digits ➔ แป้นตัวเลข'),
        ('keys', r'([+\-*/=])\s*\(\s*KEYPAD\s*\)', r'([+\-*/=])\s*\(\s*คีย์แพด\s*\)', lambda m, src: f"{m.group(1)} (แป้นตัวเลข)", 'Keypad symbols ➔ แป้นตัวเลข'),
        ('keys', r'((?:DOWN|UP|LEFT|RIGHT)\s*ARROW)\s*\(\s*KEYPAD\s*\)', r'(ลูกศร(?:ลง|ขึ้น|ซ้าย|ขวา))\s*\(\s*คีย์แพด\s*\)', lambda m, src: f"{m.group(1)} (แป้นตัวเลข)", 'Keypad arrows ➔ แป้นตัวเลข'),

        # F-Keys
        ('keys', r'^\s*F(\d{1,2})\s*$', r'^(?:เอฟ\s*\d{1,2}|F\d{1,2})$', lambda m, src: 'F' + re.search('F(\\d{1,2})', src, re.I).group(1), 'F1-F12 ➔ F1-F12'),
        ('keys', r'\bF(\d{1,2})\b', r'(?<![ก-๙])เอฟ\s*(\d{1,2})(?![ก-๙])', lambda m, src: f"F{m.group(1)}", 'F1-F12 ➔ F1-F12'),

        # Mouse & Wheel
        ('keys', r'^\s*MOUSE(\d)\s*$', r'^(?:เมาส์\s*\d|MOUSE\s*\d)$', lambda m, src: 'Mouse ' + re.search('MOUSE(\\d)', src, re.I).group(1), 'Mouse N ➔ Mouse N'),
        ('keys', r'^\s*MWHEELDOWN\s*$', r'^.*$', lambda m, src: 'Mouse Wheel ลง', 'MWHEELDOWN ➔ Mouse Wheel ลง'),
        ('keys', r'^\s*MWHEELUP\s*$', r'^.*$', lambda m, src: 'Mouse Wheel ขึ้น', 'MWHEELUP ➔ Mouse Wheel ขึ้น'),
    ]

    MODEL_CODE_SCAN_PATTERN = re.compile(
        r'\b(?:[A-Za-z]{1,5}[-_]\d{1,4}[A-Za-z0-9]?|(?:Mk|Mark)\.?\s*(?:[IVXLCDM]+|\d+)|Type[- ]\d+[A-Za-z]?|[A-Z]{1,3}\d{2,4}[A-Z0-9]?)\b',
        re.IGNORECASE
    )

    @classmethod
    def retrofit_military_text(cls, source_text, trans_text, options=None, custom_rules=None):
        """
        Scan and repair awkward translations of firearms, sci-fi weapons, model codes, and vehicles (0 tokens).
        options dict can toggle: 'model_codes', 'scifi', 'weapons', 'acronyms', 'vehicles', 'calibers', 'keys', 'glossary'
        custom_rules: optional list of dicts [{'src':..., 'trans':..., 'rep':..., 'desc':...}]
        Returns: (repaired_text, list_of_changes)
        """
        if not source_text or not trans_text:
            return trans_text, []
        
        opts = options or {'model_codes': True, 'scifi': True, 'weapons': True, 'acronyms': True, 'vehicles': True, 'calibers': True, 'keys': True}
        current_trans = trans_text
        changes = []

        # 1. Custom User Rules (Highest Priority)
        if custom_rules and isinstance(custom_rules, list):
            for crule in custom_rules:
                c_src = crule.get('src', '').strip()
                c_trans = crule.get('trans', '').strip()
                c_rep = crule.get('rep', '')
                c_desc = crule.get('desc', f"Custom: {c_src} ➔ {c_rep}")
                if not c_src or not c_trans:
                    continue
                # If source text contains the source pattern
                if re.search(c_src, source_text, re.IGNORECASE):
                    if re.search(c_trans, current_trans, re.IGNORECASE):
                        def _repl_custom(m):
                            if c_rep.strip() != m.group(0).strip():
                                changes.append((m.group(0), c_rep, c_desc))
                            return c_rep
                        current_trans = re.sub(c_trans, _repl_custom, current_trans, flags=re.IGNORECASE)

        # 2. Built-in Retrofit Rules (Sci-Fi, Weapons, Acronyms, Vehicles, Calibers)
        for category, src_pattern, trans_pattern, rep_func, desc in cls.MILITARY_RETROFIT_RULES:
            if not opts.get(category, True):
                continue
            if re.search(src_pattern, source_text, re.IGNORECASE):
                    def _repl(m):
                        rep = rep_func(m, source_text)
                        if rep.strip() != m.group(0).strip():
                            changes.append((m.group(0), rep, desc))
                        return rep
                    current_trans = re.sub(trans_pattern, _repl, current_trans, flags=re.IGNORECASE)

        # 3. Dynamic Futuristic & Alphanumeric Model Code Restoration (Zero-Token)
        if opts.get('model_codes', True):
            for m in cls.MODEL_CODE_SCAN_PATTERN.finditer(source_text):
                code = m.group(0).strip()
                if len(code) < 2 or code.lower() in {'is', 'in', 'on', 'at', 'to', 'it', 'if', 'or', 'an', 'as', 'no', 'so', 'by', 'up', 'of'}:
                    continue
                code_regex = cls.build_thai_phonetic_regex_for_code(code)
                match_th = re.search(code_regex, current_trans, re.IGNORECASE)
                if match_th and match_th.group(0).strip().lower() != code.lower():
                    old_str = match_th.group(0)
                    current_trans = re.sub(code_regex, code, current_trans, flags=re.IGNORECASE)
                    changes.append((old_str, code, f"Model Code: {code}"))

        # 4. Optional: Project Glossary Retrofit
        glossary = opts.get('glossary')
        if glossary and isinstance(glossary, dict):
            for eng_term, target_val in glossary.items():
                if not eng_term:
                    continue
                th_term = target_val[0] if isinstance(target_val, list) and target_val else str(target_val)
                if not th_term:
                    continue
                if re.search(r'\b' + re.escape(eng_term) + r'\b', source_text, re.IGNORECASE):
                    if re.search(r'\b' + re.escape(eng_term) + r'\b', current_trans, re.IGNORECASE) and eng_term.lower() != th_term.lower():
                        current_trans = re.sub(r'\b' + re.escape(eng_term) + r'\b', th_term, current_trans, flags=re.IGNORECASE)
                        changes.append((eng_term, th_term, f"Glossary: {eng_term} ➔ {th_term}"))

        return current_trans, changes

    retrofit_terminology_text = retrofit_military_text

    @classmethod
    def extract_game_entities(cls, model_data, stop_words=None):
        """
        Scans all rows of a loaded file to automatically discover potential weapon names,
        sci-fi units, vehicles, and model codes.
        Returns a list of dicts: [{'term': str, 'count': int, 'samples': [(src, trans)]}]
        """
        stops = stop_words or {
            'the', 'a', 'an', 'this', 'that', 'these', 'those', 'your', 'my', 'our', 'their', 'his', 'her',
            'equip', 'select', 'use', 'with', 'and', 'or', 'at', 'in', 'on', 'to', 'from', 'deploy', 'pilot',
            'fire', 'watch', 'out', 'for', 'is', 'are', 'was', 'were', 'into', 'before', 'after', 'enemy',
            'allied', 'allies', 'squad', 'squads', 'item', 'items', 'weapon', 'weapons'
        }
        weapon_pattern = re.compile(
            r'\b(?:[A-Z][a-zA-Z0-9\'-]*(?:\s+[A-Z0-9][a-zA-Z0-9\'-]*)*\s+)?'
            r'(?:Rifle|Blaster|Cannon|Gun|Pistol|Shotgun|Launcher|Carbine|SMG|LMG|DMR|Bolter|Boltgun|Railgun|Coilgun|Disruptor|Scattergun)\b',
            re.IGNORECASE
        )
        vehicle_pattern = re.compile(
            r'\b(?:[A-Z][a-zA-Z0-9\'-]*(?:\s+[A-Z0-9][a-zA-Z0-9\'-]*)*\s+)?'
            r'(?:Tank|Dropship|Gunship|Hovertank|Mecha|Mech|Walker|Cruiser|Starfighter|Exosuit|Dreadnought|Skiff|Corvette|APC|IFV|Humvee)\b',
            re.IGNORECASE
        )

        def _clean_term(term):
            words = term.strip().split()
            while words and words[0].lower() in stops:
                words.pop(0)
            while words and words[-1].lower() in stops:
                words.pop()
            return ' '.join(words)

        results = {}
        for row in model_data:
            src = str(row.get('source', '') if isinstance(row, dict) else getattr(row, 'source', ''))
            trans = str(row.get('trans', '') if isinstance(row, dict) else getattr(row, 'trans', ''))
            if not src:
                continue

            matches = set()
            for p in [weapon_pattern, vehicle_pattern, cls.MODEL_CODE_SCAN_PATTERN]:
                for m in p.finditer(src):
                    t = _clean_term(m.group(0))
                    if len(t) >= 2 and not t.isdigit() and t.lower() not in stops:
                        matches.add(t)

            for term in matches:
                if term not in results:
                    results[term] = {'term': term, 'count': 0, 'samples': []}
                results[term]['count'] += 1
                if len(results[term]['samples']) < 2:
                    results[term]['samples'].append((src, trans))

        return sorted(results.values(), key=lambda x: x['count'], reverse=True)
    @staticmethod
    def get_row_tag(id_str, source_str):
        """
        High-precision row category classifier for game localization.
        Classifies rows into:
        - ⚙️ Sys: System, UI, Menus, Options, Keybinds
        - 💬 Talk: Dialogues, Voice lines, Subtitles, Conversations
        - ✨ Skill: Skills, Abilities, Perks, Talents, Spells, Passives, Force Powers
        - 🎒 Item: Items, Equipment, Weapons, Armor, Relics, Consumables, Materials
        - 📜 Quest: Quests, Missions, Tasks, Objectives, Contracts
        - 👤 Char: Character Names, NPCs, Heroes, Companions, Speakers
        - 🗺️ Loc: Locations, Maps, Zones, Cities, Planets
        - ❓: Unclassified
        """
        id_lower = str(id_str or "").lower()
        src_clean = str(source_str or "").strip()
        src_lower = src_clean.lower()

        # 1. SYSTEM / UI / SETTINGS / CONTROLS
        if any(k in id_lower for k in ['settings', 'config', 'option', 'video', 'audio', 'keybind', 'control', 'slider', 'button', 'btn_', '_btn', 'tooltip', 'hotkey', 'pause', 'resolution']):
            return '⚙️ Sys'
        if any(k in id_lower for k in ['targeting_', '_targeting', 'hud_', '_hud', 'actiontype', 'gameplay_tip', 'prompt_']):
            return '⚙️ Sys'
        if any(k in id_lower for k in ['company', 'brand', 'studio', 'copyright', 'gameby', 'title_agame', 'license', 'credits', 'gamecredit', 'staff', 'legal']):
            return '⚙️ Sys'
        if len(src_clean) <= 25 and any(k in src_lower for k in ['press ', 'select ', 'cancel', 'back', 'confirm', 'apply', 'restart', 'save game', 'load game', 'quit game', 'exit to ']):
            return '⚙️ Sys'
        if src_clean in ['OK', 'Cancel', 'Yes', 'No', 'Back', 'Next', 'Apply', 'Close', 'Pause', 'Continue', 'Resume', 'Save', 'Load', 'Exit', 'Quit', 'Default', 'Reset', 'Options', 'Settings']:
            return '⚙️ Sys'

        # 2. QUESTS / MISSIONS / CAMPAIGN / OPERATIONS (Checked early to protect mission headers & crisis operations)
        is_quest = False
        if src_lower.startswith(('launch operation', 'launch mission', 'mission:', 'operation:', 'objective:', 'primary objective:', 'secondary objective:')):
            is_quest = True
        elif any(k in id_lower for k in ['crisisoperation', 'crisis_operation', 'strategy_objective', 'primaryobjective', 'secondaryobjective', 'mainquest', 'subquest', 'sidequest', 'questline', 'mission_briefing', 'missionbriefing', 'bountytask', 'hunt_target']):
            is_quest = True
        elif bool(re.search(r'\b(ot|op)_[a-z0-9_]+', id_lower)):
            is_quest = True
        elif any(k in id_lower for k in ['quest', 'mission', 'task', 'objective', 'journal', 'bounty', 'hunt', '_log', 'log_', 'contract', 'chapter_', 'campaign_']):
            if not any(k in id_lower for k in ['dialogue', 'dialog', 'speech', 'voice', 'conv_', '_conv', 'cutscene', 'cinematic', 'subtitle', 'chatter', 'banter']):
                is_quest = True

        if is_quest:
            # If line is explicitly marked as voice/dialogue script inside a quest, classify as Talk
            if any(k in id_lower for k in ['dialogue', 'dialog', 'speech', 'voice', 'conv_', '_conv', 'cutscene', 'cinematic', 'subtitle', 'chatter', 'banter']):
                return '💬 Talk'
            return '📜 Quest'

        # 3. DIALOGUES (Check before skills/items so dialogue lines with quote marks or speaker tags are caught)
        if any(k in id_lower for k in ['dialogue', 'dialog', 'voice', 'speech', 'conv_', '_conv', 'cutscene', 'cinematic', 'subtitle', 'chatter', 'banter']) or ('narrat' in id_lower and 'crisis' not in id_lower):
            return '💬 Talk'
        if (src_clean.startswith(('"', '“', '「')) and len(src_clean) >= 6) or bool(re.search(r'["\'“”][^"\'“”]{6,}["\'“”]', src_clean)):
            return '💬 Talk'
        m_spk = re.match(r'^([A-Z][a-zA-Z\s]{1,18}):\s', src_clean)
        if m_spk:
            prefix_word = m_spk.group(1).strip().lower()
            if prefix_word not in ['launch mission', 'launch operation', 'mission', 'operation', 'objective', 'warning', 'notice', 'caution', 'hint', 'tip', 'note', 'memo', 'target', 'requirement', 'reward']:
                return '💬 Talk'
        if len(src_clean) > 30 and any(p in src_clean for p in ['. ', '? ', '! ', '...']):
            return '💬 Talk'

        # 4. SKILLS / ABILITIES / PERKS / POWERS
        skill_indicators = ['ga_', 'ability', 'skill', 'spell', 'magic', 'perk', 'talent', 'passive', 
                            'ultimate', 'buff', 'debuff', 'technique', 'combo', 'stance', 'force_power', 
                            'forcepower', 'special_atk', 'actionpoint', 'action_point', 'cooldown', 'cast_time', 
                            'ap_cost', 'mp_cost', 'stamina_cost']
        if any(k in id_lower for k in skill_indicators):
            return '✨ Skill'
        if any(k in source_str for k in ['Cooldown:', 'Cooldown ', 'Mana Cost', 'Action Points', 'Stamina Cost', 'AP Cost', 'Force Cost', 'Cast Time:']):
            return '✨ Skill'
        if len(src_clean) <= 45 and any(k in src_lower for k in ['cooldown', 'cast time', 'passive:', 'active:', 'deals damage', 'inflicts ']):
            return '✨ Skill'

        # 5. ITEMS / WEAPONS / GEAR / INVENTORY
        item_indicators = ['item', 'wpn', 'weapon', 'armor', 'equip', 'relic', 'artifact', 'shield', 'helmet', 
                           'boots', 'ring', 'necklace', 'potion', 'consumable', 'material', 'craft', 'ingredient', 
                           'loot', 'gear', 'lightsaber', 'blaster', 'grenade', 'medpac', 'implant', 'accessory', 'prop_']
        if any(k in id_lower for k in item_indicators):
            return '🎒 Item'
        if any(k in source_str for k in ['Weight:', 'Durability:', 'Sell Price:', 'Buy Price:']):
            return '🎒 Item'

        # 6. CHARACTERS / NPC / HEROES
        char_exact_keys = ['charactername', 'charname', 'npc_name', 'actor_name', 'hero_name', 'speaker_name',
                           'speaker', 'consequencedatabasecharactername', 'character_name', 'npcname']
        if any(k in id_lower for k in char_exact_keys):
            return '👤 Char'

        char_id_patterns = ['npc', 'actor_', '_actor', 'hero', 'companion', 'villain', 'unit_', '_unit', 'pilot', 'droid', 'trooper']
        if any(k in id_lower for k in char_id_patterns):
            if not any(bad in id_lower for bad in ['desc', 'description', 'tooltip', 'header', 'targeting', 'objective', 'icon']):
                return '👤 Char'

        # Source-based character recognition
        if '<' not in src_clean and '>' not in src_clean:
            honorifics = ['mr.', 'mrs.', 'ms.', 'dr.', 'lord ', 'lady ', 'darth ', 'master ', 'general ', 'captain ', 
                          'commander ', 'sir ', 'count ', 'princess ', 'prince ', 'king ', 'queen ', 'senator ', 'officer ', 'agent ']
            if any(src_lower.startswith(h) for h in honorifics) and len(src_clean) <= 30:
                return '👤 Char'

            if 2 <= len(src_clean) <= 25 and not src_clean.isupper() and not re.search(r'[0-9!?:;,.\-+=\(\)\[\]\{\}<>/@#$%^&*]', src_clean):
                words = src_clean.split()
                if 1 <= len(words) <= 3 and all(w.istitle() for w in words):
                    if any(k in id_lower for k in ['name', 'char', 'who', 'speaker', 'person']):
                        if not any(bad in id_lower for bad in ['gameby', 'title_', 'company', 'brand', 'studio', 'copyright']):
                            return '👤 Char'

        # 7. LOCATIONS / MAPS
        loc_keys = ['map', 'loc_', '_loc', 'zone', 'town', 'city', 'area', 'place', 'dungeon', 'room', 'stage', 'level', 'world', 'planet', 'sector', 'system', 'galaxy']
        if any(k in id_lower for k in loc_keys):
            return '🗺️ Loc'

        return '❓'

    @staticmethod
    def extract_translation_options(reply):
        """
        Robustly extracts 3 translation options from an LLM response.
        Handles:
        - Raw JSON array: ["opt1", "opt2", "opt3"]
        - Markdown fenced JSON: ```json [...] ```
        - DeepSeek reasoning tags: <think>...</think>
        - Conversational preamble and postamble
        - Numbered lists: 1. ... 2. ... 3. ...
        - Trailing commas or single-quote syntax
        """
        if not reply or not isinstance(reply, str):
            return []
            
        import ast
        text = reply.strip()
        
        # 1. Strip DeepSeek / Qwen reasoning tags: <think>...</think>
        text = re.sub(r'<think>[\s\S]*?</think>', '', text).strip()
        
        # 2. Try direct json.loads after removing markdown blocks
        clean = re.sub(r'^```[a-zA-Z]*\n?|\n?```$', '', text, flags=re.MULTILINE).strip()
        try:
            data = json.loads(clean)
            if isinstance(data, list) and len(data) > 0:
                return [str(x).strip() for x in data if str(x).strip()]
        except Exception:
            pass

        # 3. Find outer [ ... ] in the text
        m = re.search(r'\[\s*([\s\S]*?)\s*\]', text)
        if m:
            candidate = m.group(0)
            try:
                data = json.loads(candidate)
                if isinstance(data, list) and len(data) > 0:
                    return [str(x).strip() for x in data if str(x).strip()]
            except Exception:
                pass
            try:
                data = ast.literal_eval(candidate)
                if isinstance(data, list) and len(data) > 0:
                    return [str(x).strip() for x in data if str(x).strip()]
            except Exception:
                pass
                
            # Extract quoted strings inside the bracket
            strings = re.findall(r'"([^"\\]*(?:\\.[^"\\]*)*)"', candidate)
            if len(strings) >= 2:
                return [s.replace('\\"', '"').replace('\\n', '\n').strip() for s in strings if s.strip()]

        # 4. Try numbered list pattern: 1. ... 2. ... 3. ...
        lines = text.splitlines()
        numbered = []
        num_pattern = re.compile(r'^\s*(?:\d+[\.\:\)\-]|Option\s*\d+[\.\:\-]|สไตล์\s*\d+[\.\:\-]|\d+\s*[\.\:\-])\s*(.*)', re.IGNORECASE)
        for line in lines:
            line_s = line.strip()
            if not line_s: continue
            nm = num_pattern.match(line_s)
            if nm:
                val = nm.group(1).strip()
                val = re.sub(r'^(?:Literal|Casual|Polite|Formal|Game|แปลตรงตัว|ภาษาพูด|สุภาพ|ทางการ|สไตล์เกม|สบายๆ)\s*[\(\)\/\w\s]*[\:\-]\s*', '', val, flags=re.IGNORECASE).strip()
                val = val.strip('"\'')
                if val:
                    numbered.append(val)
                    
        if len(numbered) >= 2:
            return numbered

        # 5. Fallback: split by newlines if 2-4 non-empty lines
        non_empty = [l.strip().strip('"\'') for l in lines if l.strip() and not l.strip().startswith('```')]
        if 2 <= len(non_empty) <= 4:
            return non_empty

        return []

    @classmethod
    def set_project_path(cls, path):
        if path and os.path.exists(path):
            cls._PROJECT_PATH = os.path.normpath(os.path.abspath(path))
        else:
            cls._PROJECT_PATH = None

    @classmethod
    def get_project_path(cls):
        return cls._PROJECT_PATH
            
    @classmethod
    def get_profile_dir(cls, preset_name="Default"):
        if cls._PROJECT_PATH:
            p = os.path.join(cls._PROJECT_PATH, ".thub", "profile")
            if not os.path.exists(p):
                os.makedirs(p, exist_ok=True)
            return p
        return os.path.join(BASE_DIR, "profiles", preset_name)

    @classmethod
    def get_prompts_path(cls):
        return PROMPTS_PATH
    @staticmethod
    def load_config():
        data = {}
        try:
            if os.path.exists(CONFIG_PATH):
                with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            
        # Apply defaults for core settings
        data.setdefault("google_key", "")
        data.setdefault("anthropic_key", "")
        if "api_key" in data and "deepseek_key" not in data:
            data["deepseek_key"] = data["api_key"]
        data.setdefault("deepseek_key", "")
        data.setdefault("openai_key", "")
        data.setdefault("openrouter_key", "")
        data.setdefault("model", "deepseek-chat")
        data.setdefault("provider", "DeepSeek")
        # Sanitize deprecated or typo model names
        m_curr = str(data.get("model", "")).strip()
        if m_curr in ("deepseek-v3", "deepseek"):
            data["model"] = "deepseek-chat"
        elif m_curr in ("gemini-2.5-flash", "gemini-1.0-pro", "gemini-pro"):
            data["model"] = "gemini-2.0-flash"
        elif m_curr in ("gemini-2.5-pro",):
            data["model"] = "gemini-2.0-pro-exp-02-05"
        elif m_curr in ("claude-sonnet-4.6", "claude-3-5-sonnet"):
            data["model"] = "claude-3-5-sonnet-20241022"
        elif m_curr in ("claude-opus-4.8",):
            data["model"] = "claude-3-opus-20240229"
        elif m_curr in ("gpt-3.5-turbo", "gpt-4-turbo"):
            data["model"] = "gpt-4o-mini"
        data.setdefault("local_url", "http://localhost:1234/v1/chat/completions")
        data.setdefault("base_url", "")
        
        # Ensure correct types
        try:
            data["temperature"] = float(data.get("temperature", 0.3))
        except:
            data["temperature"] = 0.3
            
        try:
            data["max_tokens"] = int(data.get("max_tokens", 4096))
        except:
            data["max_tokens"] = 4096
            
        try:
            data["timeout"] = int(data.get("timeout", 30))
        except:
            data["timeout"] = 30
            
        return data

    @staticmethod
    def save_config(cfg):
        try:
            path = CONFIG_PATH
            tmp_fd, tmp_path = tempfile.mkstemp(
                dir=os.path.dirname(os.path.abspath(path)),
                suffix='.tmp'
            )
            try:
                with os.fdopen(tmp_fd, 'w', encoding='utf-8') as f:
                    json.dump(cfg, f, ensure_ascii=False, indent=4)
                shutil.move(tmp_path, path)
            except Exception:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
                raise
        except Exception as e:
            print(f"Error saving config: {e}")

    @staticmethod
    def is_internal_path(path):
        """Returns True if the path is an internal modder-hub or tool development directory."""
        if not path or not isinstance(path, str):
            return True
        p = os.path.normpath(path).lower()
        bad_tokens = ['modder-hub', 'tools\\flagship', 'tools/flagship', 'locales', '.git', '__pycache__', 'python3']
        return any(tok in p for tok in bad_tokens)

    @classmethod
    def get_translation_workspace_dir(cls, hint_path=None, profile_name=None, create_if_missing=True):
        """
        Intelligently resolves the active game's '02_Translation_Workspace' folder.
        Prioritizes:
        1. hint_path (e.g. current CSV path, loaded project path, or provided file/folder)
        2. cls._PROJECT_PATH (active project path set by launcher or CLI)
        3. profile_name / active preset mapped to THub projects or E:\\Mod_Workspace
        4. Valid last_dir / origin_file from config.json (filtering out internal code directories)
        5. Active/pinned project from hub_config.json
        6. Default workspace directory (e.g. E:\\Mod_Workspace)
        """
        def _has_csv(dir_path):
            if not dir_path or not os.path.isdir(dir_path):
                return False
            for root, dirs, files in os.walk(dir_path):
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                if any(f.lower().endswith('.csv') and not f.lower().endswith('_backup.csv') and not f.lower().endswith('.glossary.csv') and not f.startswith('~$') for f in files):
                    return True
            return False

        # 1. Check hint_path
        if hint_path and not cls.is_internal_path(hint_path):
            p = os.path.normpath(os.path.abspath(hint_path))
            if os.path.isfile(p):
                p = os.path.dirname(p)
            for folder_candidate in ['02_Translation_Workspace', '03_Translated_Text', '02_Translation', '02_Extracted_Text']:
                if os.path.basename(p).lower() == folder_candidate.lower() and os.path.isdir(p):
                    return p
            # Check candidate folders containing CSVs first
            for folder_candidate in ['02_Translation_Workspace', '02_Translation', '03_Translated_Text', '02_Extracted_Text']:
                ws = os.path.join(p, folder_candidate)
                if _has_csv(ws):
                    return ws
            for folder_candidate in ['02_Translation_Workspace', '02_Translation', '03_Translated_Text', '02_Extracted_Text']:
                ws = os.path.join(p, folder_candidate)
                if os.path.isdir(ws):
                    return ws
            # Walk up to find game root containing translation folder
            curr = p
            for _ in range(4):
                parent = os.path.dirname(curr)
                if parent == curr:
                    break
                for folder_candidate in ['02_Translation_Workspace', '02_Translation', '03_Translated_Text', '02_Extracted_Text']:
                    cand_ws = os.path.join(curr, folder_candidate)
                    if _has_csv(cand_ws):
                        return cand_ws
                for folder_candidate in ['02_Translation_Workspace', '02_Translation', '03_Translated_Text', '02_Extracted_Text']:
                    cand_ws = os.path.join(curr, folder_candidate)
                    if os.path.isdir(cand_ws):
                        return cand_ws
                curr = parent

        # 2. Strict Project Context: Check cls._PROJECT_PATH (if set, NEVER fall back to other games!)
        if cls._PROJECT_PATH and not cls.is_internal_path(cls._PROJECT_PATH):
            p = os.path.normpath(os.path.abspath(cls._PROJECT_PATH))
            if os.path.isfile(p):
                p = os.path.dirname(p)
            for folder_candidate in ['02_Translation_Workspace', '03_Translated_Text', '02_Translation', '02_Extracted_Text']:
                if os.path.basename(p).lower() == folder_candidate.lower() and os.path.isdir(p):
                    return p
            for folder_candidate in ['02_Translation_Workspace', '02_Translation', '03_Translated_Text', '02_Extracted_Text']:
                ws = os.path.join(p, folder_candidate)
                if _has_csv(ws):
                    return ws
            for folder_candidate in ['02_Translation_Workspace', '02_Translation', '03_Translated_Text', '02_Extracted_Text']:
                ws = os.path.join(p, folder_candidate)
                if os.path.isdir(ws):
                    return ws
            if os.path.isdir(p):
                default_target = os.path.join(p, '02_Translation_Workspace')
                if create_if_missing:
                    try:
                        os.makedirs(default_target, exist_ok=True)
                    except Exception:
                        pass
                return default_target if os.path.isdir(default_target) else p

        # 3. Locate hub_config.json & default workspace dir (Only reached if no active project context)
        hub_projects = []
        default_ws_dir = 'E:\\Mod_Workspace'
        possible_hub_cfgs = [
            os.path.join(BASE_DIR, '..', '..', '..', 'hub_config.json'),
            os.path.join(BASE_DIR, '..', '..', 'hub_config.json'),
            os.path.join(BASE_DIR, '..', 'hub_config.json'),
            os.path.join(BASE_DIR, 'hub_config.json'),
            'E:\\Mod_Workspace\\Modder_project\\modder-hub\\hub_config.json'
        ]
        for cfg_path in possible_hub_cfgs:
            norm_cfg = os.path.normpath(cfg_path)
            if os.path.exists(norm_cfg):
                try:
                    with open(norm_cfg, 'r', encoding='utf-8') as f:
                        hdata = json.load(f)
                    hub_projects = hdata.get('projects', [])
                    default_ws_dir = hdata.get('default_workspace_dir', default_ws_dir)
                    break
                except Exception:
                    pass

        # 4. Match explicit profile_name against hub_projects or E:\\Mod_Workspace
        prof_to_check = profile_name
        is_explicit_profile = bool(profile_name and profile_name.strip() and profile_name.strip().lower() != 'default')
        if not prof_to_check or prof_to_check.strip().lower() == 'default':
            try:
                prof_data = cls.load_profiles()
                active = prof_data.get('active_preset')
                if active and active.strip().lower() != 'default':
                    prof_to_check = active
            except Exception:
                pass

        if prof_to_check and prof_to_check.strip() and prof_to_check.strip().lower() != 'default':
            pn = prof_to_check.strip().lower().replace(' ', '').replace('_', '').replace('-', '').replace(':', '')

            def _resolve_candidate_ws(base_dir):
                if not base_dir or not os.path.isdir(base_dir):
                    return None
                for folder_cand in ['02_Translation_Workspace', '02_Translation', '03_Translated_Text', '02_Extracted_Text']:
                    ws = os.path.join(base_dir, folder_cand)
                    if _has_csv(ws):
                        return os.path.normpath(ws)
                for folder_cand in ['02_Translation_Workspace', '02_Translation', '03_Translated_Text', '02_Extracted_Text']:
                    ws = os.path.join(base_dir, folder_cand)
                    if os.path.isdir(ws):
                        return os.path.normpath(ws)
                return None

            # PASS 1: Strict Exact Matching (Prevents collision e.g. Dead island vs DeadIsland2)
            for proj in hub_projects:
                p_name = proj.get('name', '').lower().replace(' ', '').replace('_', '').replace('-', '').replace(':', '')
                p_prof = proj.get('profile_name', '').lower().replace(' ', '').replace('_', '').replace('-', '').replace(':', '')
                if pn == p_name or (p_prof and pn == p_prof):
                    ppath = proj.get('path')
                    if ppath and os.path.isdir(ppath):
                        ws = _resolve_candidate_ws(ppath)
                        if ws: return ws
                        if create_if_missing:
                            ws_default = os.path.join(ppath, '02_Translation_Workspace')
                            try:
                                os.makedirs(ws_default, exist_ok=True)
                            except Exception:
                                pass
                            return os.path.normpath(ws_default)

            if os.path.isdir(default_ws_dir):
                try:
                    for sub in os.listdir(default_ws_dir):
                        sub_path = os.path.join(default_ws_dir, sub)
                        if os.path.isdir(sub_path) and not cls.is_internal_path(sub_path):
                            sub_clean = sub.lower().replace(' ', '').replace('_', '').replace('-', '').replace(':', '')
                            if pn == sub_clean:
                                ws = _resolve_candidate_ws(sub_path)
                                if ws: return ws
                                if create_if_missing:
                                    ws_default = os.path.join(sub_path, '02_Translation_Workspace')
                                    try:
                                        os.makedirs(ws_default, exist_ok=True)
                                    except Exception:
                                        pass
                                    return os.path.normpath(ws_default)
                except Exception:
                    pass

            # PASS 2: Prefix Matching (Only if Pass 1 exact match fails and not a sequel mismatch)
            def _is_sequel_mismatch(a, b):
                d1 = re.findall(r'\d+', a)
                d2 = re.findall(r'\d+', b)
                return d1 != d2

            for proj in hub_projects:
                p_name = proj.get('name', '').lower().replace(' ', '').replace('_', '').replace('-', '').replace(':', '')
                p_prof = proj.get('profile_name', '').lower().replace(' ', '').replace('_', '').replace('-', '').replace(':', '')
                matched = False
                if pn and p_name and (p_name.startswith(pn) or pn.startswith(p_name)) and not _is_sequel_mismatch(pn, p_name):
                    matched = True
                elif p_prof and (p_prof.startswith(pn) or pn.startswith(p_prof)) and not _is_sequel_mismatch(pn, p_prof):
                    matched = True
                if matched:
                    ppath = proj.get('path')
                    if ppath and os.path.isdir(ppath):
                        ws = _resolve_candidate_ws(ppath)
                        if ws: return ws

            if os.path.isdir(default_ws_dir):
                try:
                    for sub in os.listdir(default_ws_dir):
                        sub_path = os.path.join(default_ws_dir, sub)
                        if os.path.isdir(sub_path) and not cls.is_internal_path(sub_path):
                            sub_clean = sub.lower().replace(' ', '').replace('_', '').replace('-', '').replace(':', '')
                            if pn and (sub_clean.startswith(pn) or pn.startswith(sub_clean)) and not _is_sequel_mismatch(pn, sub_clean):
                                ws = _resolve_candidate_ws(sub_path)
                                if ws: return ws
                except Exception:
                    pass

            # Check candidate folder by profile name directly
            safe_name = re.sub(r'[\\/*?:"<>|]', '_', prof_to_check.strip())
            cand_folder = os.path.join(default_ws_dir, safe_name)
            if os.path.isdir(cand_folder):
                ws = _resolve_candidate_ws(cand_folder)
                if ws: return ws
            cand_ws = os.path.join(default_ws_dir, safe_name, '02_Translation_Workspace')
            if os.path.isdir(cand_ws):
                return os.path.normpath(cand_ws)
            if create_if_missing:
                try:
                    os.makedirs(cand_ws, exist_ok=True)
                    return os.path.normpath(cand_ws)
                except Exception:
                    pass

            # If an explicit profile was requested and not found, NEVER fall back to unrelated projects!
            if is_explicit_profile:
                return None

        # 5. Check config.json origin_file and last_dir (Only for general standalone launch)
        try:
            if os.path.exists(CONFIG_PATH):
                with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                    cdata = json.load(f)
                orig = cdata.get('origin_file')
                if orig and not cls.is_internal_path(orig):
                    p = os.path.normpath(os.path.abspath(orig))
                    if os.path.isfile(p):
                        p = os.path.dirname(p)
                    if os.path.basename(p).lower() == '02_translation_workspace' and os.path.isdir(p):
                        return p
                    ws = os.path.join(p, '02_Translation_Workspace')
                    if os.path.isdir(ws):
                        return ws
                last_dir = cdata.get('last_dir')
                if last_dir and not cls.is_internal_path(last_dir) and os.path.isdir(last_dir):
                    if os.path.basename(last_dir).lower() == '02_translation_workspace':
                        return os.path.normpath(last_dir)
                    ws = os.path.join(last_dir, '02_Translation_Workspace')
                    if os.path.isdir(ws):
                        return ws
        except Exception:
            pass

        # 6. Check pinned or first project in hub_config.json
        for proj in hub_projects:
            if proj.get('is_pinned'):
                ppath = proj.get('path')
                if ppath:
                    ws = os.path.join(ppath, '02_Translation_Workspace')
                    if os.path.isdir(ws):
                        return os.path.normpath(ws)
                    if os.path.isdir(ppath):
                        if create_if_missing:
                            try:
                                os.makedirs(ws, exist_ok=True)
                            except Exception:
                                pass
                        return os.path.normpath(ws)
        if hub_projects:
            ppath = hub_projects[0].get('path')
            if ppath:
                ws = os.path.join(ppath, '02_Translation_Workspace')
                if os.path.isdir(ws):
                    return os.path.normpath(ws)
                if os.path.isdir(ppath):
                    if create_if_missing:
                        try:
                            os.makedirs(ws, exist_ok=True)
                        except Exception:
                            pass
                    return os.path.normpath(ws)

        # 7. Fallback to default_ws_dir
        if os.path.isdir(default_ws_dir):
            return os.path.normpath(default_ws_dir)

        return BASE_DIR

    @classmethod
    def get_last_dir(cls, hint_path=None, profile_name=None):
        """Returns the game's 02_Translation_Workspace directory, avoiding internal code directories."""
        return cls.get_translation_workspace_dir(hint_path=hint_path, profile_name=profile_name)

    @classmethod
    def set_last_dir(cls, file_path):
        """Saves the directory of the given file_path to config.json (ignoring internal code paths)."""
        try:
            if not file_path or not isinstance(file_path, str):
                return
            d = os.path.dirname(os.path.abspath(file_path)) if os.path.isfile(file_path) else os.path.abspath(file_path)
            if cls.is_internal_path(d):
                return
            data = {}
            if os.path.exists(CONFIG_PATH):
                with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            data["last_dir"] = d
            with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error saving last_dir: {e}")

    @classmethod
    def load_profiles(cls):
        data = {
            "active_preset": "Default",
            "presets": {
                "Default": {
                    "single": "",
                    "opt": "",
                    "batch": "", # Added for TRun
                    "glossary": {},
                    "max_bytes_limit": 63
                }
            }
        }
        # 1. Master PROMPTS_PATH
        target_paths = [PROMPTS_PATH]
        # 2. If project path exists, also check project local prompts.json
        if cls._PROJECT_PATH:
            proj_p = os.path.join(cls._PROJECT_PATH, ".thub", "profile", "prompts.json")
            if os.path.exists(proj_p) and os.path.abspath(proj_p) != os.path.abspath(PROMPTS_PATH):
                target_paths.append(proj_p)

        for target_path in target_paths:
            try:
                if os.path.exists(target_path):
                    with open(target_path, 'r', encoding='utf-8-sig') as f:
                        loaded = json.load(f)
                        if "single_prompt" in loaded:
                            data["presets"]["Default"]["single"] = loaded.get("single_prompt", DEFAULT_SINGLE_PROMPT)
                            data["presets"]["Default"]["opt"] = loaded.get("opt_prompt", DEFAULT_OPTIONS_PROMPT)
                            data["presets"]["Default"]["batch"] = loaded.get("batch_prompt", DEFAULT_SINGLE_PROMPT)
                        else:
                            active_candidate = loaded.get("active_preset")
                            if active_candidate and active_candidate != "Default":
                                data["active_preset"] = active_candidate
                            for k, v in loaded.get("presets", {}).items():
                                p_entry = dict(v) if isinstance(v, dict) else {}
                                p_entry.setdefault("single", "")
                                p_entry.setdefault("opt", "")
                                p_entry.setdefault("batch", p_entry.get("single", ""))
                                p_entry.setdefault("glossary", {})
                                p_entry.setdefault("max_bytes_limit", 63)
                                data["presets"][k] = p_entry
            except json.JSONDecodeError as e:
                print(f"Failed to parse prompts.json at {target_path}: {e}")
            except Exception as e:
                print(f"Error reading prompts.json at {target_path}: {e}")
        
        # Legacy glossary migration
        try:
            if os.path.exists(GLOSSARY_PATH):
                with open(GLOSSARY_PATH, 'r', encoding='utf-8') as f:
                    old_glossary = json.load(f)
                    if old_glossary and not data["presets"]["Default"]["glossary"]:
                        data["presets"]["Default"]["glossary"] = old_glossary
                try:
                    if os.path.exists(GLOSSARY_PATH + ".bak"):
                        os.remove(GLOSSARY_PATH + ".bak")
                    os.rename(GLOSSARY_PATH, GLOSSARY_PATH + ".bak")
                except Exception as e:
                    print(f"Failed to backup glossary.json: {e}")
        except Exception as e:
            print(f"Error reading legacy glossary.json: {e}")
            
        if data["active_preset"] not in data["presets"]:
            data["active_preset"] = "Default"
            if "Default" not in data["presets"]:
                data["presets"]["Default"] = {"single": "", "opt": "", "batch": "", "glossary": {}}
                
        # If we have a project path, ensure project preset exists and is ACTIVATED
        if cls._PROJECT_PATH:
            proj_name = None
            thub_meta = os.path.join(cls._PROJECT_PATH, "thub_project.json")
            if os.path.exists(thub_meta):
                try:
                    with open(thub_meta, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                    proj_name = meta.get("profile_name") or meta.get("project_name", "")
                except Exception as e:
                    print(f"Error reading thub_project.json: {e}")

            if not proj_name:
                try:
                    hub_cfg_p = os.path.normpath(os.path.join(BASE_DIR, '..', '..', '..', 'hub_config.json'))
                    if os.path.exists(hub_cfg_p):
                        with open(hub_cfg_p, 'r', encoding='utf-8') as f:
                            hdata = json.load(f)
                        norm_cur = os.path.normpath(cls._PROJECT_PATH).lower()
                        for p in hdata.get("projects", []):
                            if os.path.normpath(p.get("path", "")).lower() == norm_cur:
                                proj_name = p.get("profile_name") or p.get("name", "")
                                break
                except Exception:
                    pass

            if not proj_name:
                proj_name = os.path.basename(cls._PROJECT_PATH)

            if proj_name:
                # Match existing preset with flexible naming (case-insensitive, underscore vs space, stripping special chars)
                found_preset = None
                p_clean = re.sub(r'[^a-zA-Z0-9]', '', proj_name).lower()
                for k in data["presets"].keys():
                    k_clean = re.sub(r'[^a-zA-Z0-9]', '', k).lower()
                    if k_clean and (k_clean == p_clean or k_clean == re.sub(r'[^a-zA-Z0-9]', '', os.path.basename(cls._PROJECT_PATH)).lower()):
                        found_preset = k
                        break

                target_key = found_preset or proj_name
                if target_key not in data["presets"]:
                    data["presets"][target_key] = {"single": "", "opt": "", "batch": "", "glossary": {}, "max_bytes_limit": 63}
                # Always activate the target project's preset when _PROJECT_PATH is set
                data["active_preset"] = target_key

        # Auto-create the file if it doesn't exist
        if not os.path.exists(PROMPTS_PATH):
            cls.save_profiles(data)
            
        return data

    @classmethod
    def save_profiles(cls, data):
        target_paths = [PROMPTS_PATH]
        proj_p = None
        if cls._PROJECT_PATH:
            proj_p = os.path.join(cls._PROJECT_PATH, ".thub", "profile", "prompts.json")
            if os.path.abspath(proj_p) != os.path.abspath(PROMPTS_PATH):
                target_paths.append(proj_p)

        for path in target_paths:
            try:
                os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
                
                # Project Profile Isolation: save only this project's preset to project-local prompts.json
                if cls._PROJECT_PATH and proj_p and os.path.abspath(path) == os.path.abspath(proj_p):
                    proj_name = None
                    thub_meta = os.path.join(cls._PROJECT_PATH, "thub_project.json")
                    if os.path.exists(thub_meta):
                        try:
                            with open(thub_meta, "r", encoding="utf-8") as f_meta:
                                meta = json.load(f_meta)
                            proj_name = meta.get("profile_name") or meta.get("project_name", "")
                        except Exception:
                            pass
                    if not proj_name:
                        proj_name = os.path.basename(cls._PROJECT_PATH)

                    found_preset = None
                    if proj_name:
                        p_clean = re.sub(r'[^a-zA-Z0-9]', '', proj_name).lower()
                        for k in data.get("presets", {}).keys():
                            k_clean = re.sub(r'[^a-zA-Z0-9]', '', k).lower()
                            if k_clean and (k_clean == p_clean or k_clean == re.sub(r'[^a-zA-Z0-9]', '', os.path.basename(cls._PROJECT_PATH)).lower()):
                                found_preset = k
                                break

                    target_key = found_preset or proj_name or data.get("active_preset", "Default")
                    save_data = {
                        "active_preset": target_key,
                        "presets": {}
                    }
                    if target_key in data.get("presets", {}):
                        save_data["presets"][target_key] = data["presets"][target_key]
                    if "Default" in data.get("presets", {}):
                        save_data["presets"]["Default"] = data["presets"]["Default"]
                else:
                    save_data = data

                tmp_fd, tmp_path = tempfile.mkstemp(
                    dir=os.path.dirname(os.path.abspath(path)),
                    suffix='.tmp'
                )
                try:
                    with os.fdopen(tmp_fd, 'w', encoding='utf-8') as f:
                        json.dump(save_data, f, ensure_ascii=False, indent=4)
                    shutil.move(tmp_path, path)
                except Exception:
                    try:
                        os.unlink(tmp_path)
                    except OSError:
                        pass
                    raise
            except Exception as e:
                print(f"Error saving profiles to {path}: {e}")

    @classmethod
    def get_current_profile_data(cls, preset_name=None):
        profiles = cls.load_profiles()
        active = preset_name or profiles.get("active_preset", "Default")
        data = profiles.get("presets", {}).get(active)
        if not data or not isinstance(data, dict):
            data = {}
        res = dict(data)
        res["single"] = data.get("single") or DEFAULT_SINGLE_PROMPT
        res["opt"] = data.get("opt") or DEFAULT_OPTIONS_PROMPT
        res["batch"] = data.get("batch") or data.get("single") or DEFAULT_SINGLE_PROMPT
        res["glossary"] = data.get("glossary", {}) if isinstance(data.get("glossary"), dict) else {}
        res["max_bytes_limit"] = data.get("max_bytes_limit", 0)
        raw_tlm = data.get("tlm")
        raw_lore = data.get("tlm_lore")
        if isinstance(raw_tlm, dict):
            tlm_dict = dict(raw_tlm)
        elif isinstance(raw_lore, dict):
            tlm_dict = dict(raw_lore)
        elif isinstance(raw_lore, str) and raw_lore.strip():
            tlm_dict = {"lore_notes": raw_lore.strip(), "universe_tone": ""}
        elif isinstance(raw_tlm, str) and raw_tlm.strip():
            tlm_dict = {"lore_notes": raw_tlm.strip(), "universe_tone": ""}
        else:
            tlm_dict = {}
        res["tlm"] = tlm_dict
        return res

    @classmethod
    def save_profile_data(cls, preset_name, profile_dict):
        """Save or update a specific profile preset directly."""
        profiles = cls.load_profiles()
        profiles.setdefault("presets", {})[preset_name] = profile_dict
        profiles["active_preset"] = preset_name
        cls.save_profiles(profiles)
        return profiles

class CoreAI:

    @classmethod
    def _send_request_with_retry(cls, session, url, json_payload, headers, timeout_val, provider_name="API", max_retries=4):
        """
        Robust HTTP POST with automatic retry, exponential backoff, and jitter.
        Handles Rate Limits (HTTP 429), Concurrency Spikes, and Server Overload (HTTP 500, 502, 503, 504).
        """
        import time
        import random
        last_res = None
        last_err = None

        for attempt in range(max_retries + 1):
            try:
                res = session.post(url, json=json_payload, headers=headers, timeout=timeout_val)
                last_res = res
                if res.status_code == 200:
                    return res

                # Check if retryable status code (429 Rate Limit / Concurrency, 5xx Server Error)
                if res.status_code in (429, 500, 502, 503, 504) and attempt < max_retries:
                    retry_after = res.headers.get("Retry-After")
                    try:
                        delay = float(retry_after) if retry_after else (1.5 * (2 ** attempt) + random.uniform(0.3, 1.0))
                    except Exception:
                        delay = 1.5 * (2 ** attempt) + random.uniform(0.3, 1.0)
                    # If 429 error message mentions concurrency, wait at least 2.5s for other concurrent threads to finish
                    if res.status_code == 429:
                        delay = max(delay, 2.5)
                    delay = min(delay, 25.0)
                    time.sleep(delay)
                    continue
                else:
                    raise Exception(f"{provider_name} API Error {res.status_code}: {res.text}")
            except requests.exceptions.RequestException as req_e:
                last_err = req_e
                if attempt < max_retries:
                    delay = 1.5 * (2 ** attempt) + random.uniform(0.3, 1.0)
                    time.sleep(min(delay, 20.0))
                    continue
                raise Exception(f"Network Connection Error ({provider_name}): {req_e}")

        if last_res is not None:
            raise Exception(f"{provider_name} API Error {last_res.status_code}: {last_res.text}")
        if last_err is not None:
            raise Exception(f"Network Connection Error ({provider_name}): {last_err}")

    @classmethod
    def generate_content(cls, cfg, prompt, is_local=False, use_search_grounding=False):
        content = ""  # Ensure content is always defined (guard against UnboundLocalError)
        model = cfg.get("model", "deepseek-chat")
        provider = cfg.get("provider", "")
        if is_local:
            if not provider:
                provider = "Local LLM"
            if not model:
                model = "custom-local-llm"

        base_url = cfg.get("base_url", "").rstrip("/")
        # Critical Safeguard: If base_url points to localhost/127.0.0.1, it belongs ONLY to Local LLM!
        # Do NOT let a local server hijack official cloud API endpoints (DeepSeek, Gemini, Claude, OpenAI).
        is_local_base_url = bool(base_url and any(h in base_url for h in ("localhost", "127.0.0.1", ":1234", ":11434")))
        cloud_base_url = base_url if (base_url and not is_local_base_url) else ""

        is_openrouter = (provider == "OpenRouter") or ("openrouter.ai" in base_url) or ("/" in model and not model.startswith("http"))
        is_local_llm = (provider == "Local LLM") or (model in ("custom-local-llm", "Local LLM")) or model.startswith("qwen") or model.startswith("llama") or model.startswith("qwq") or is_local

        if not is_local_llm:
            if is_openrouter:
                if not cfg.get("openrouter_key") and not cfg.get("openai_key") and not cfg.get("api_key"):
                    raise Exception("OpenRouter API Key is missing! Please configure it in Settings.")
            elif model.startswith("gemini"):
                if not cfg.get("google_key"):
                    raise Exception("Google Gemini API Key is missing! Please configure it in Settings.")
            elif model.startswith("claude"):
                if not cfg.get("anthropic_key"):
                    raise Exception("Anthropic Claude API Key is missing! Please configure it in Settings.")
            elif model.startswith("deepseek"):
                if not cfg.get("deepseek_key") and not cfg.get("api_key"):
                    raise Exception("DeepSeek API Key is missing! Please configure it in Settings.")
            elif not cfg.get("openai_key"):
                raise Exception("OpenAI API Key is missing! Please configure it in Settings.")

        try:
            timeout_val = float(cfg.get("timeout", 30) or 30)
        except Exception:
            timeout_val = 30.0

        try:
            temp_val = float(cfg.get("temperature", 0.3) or 0.3)
        except Exception:
            temp_val = 0.3

        try:
            max_tokens_val = int(cfg.get("max_tokens", 4096) or 4096)
        except Exception:
            max_tokens_val = 4096

        if model.startswith("deepseek") and max_tokens_val < 8192:
            max_tokens_val = 8192

        if is_openrouter:
            url = cloud_base_url if cloud_base_url else "https://openrouter.ai/api/v1/chat/completions"
            if not url.endswith("/chat/completions"):
                url = f"{url.rstrip('/')}/chat/completions"
            key = cfg.get("openrouter_key") or cfg.get("openai_key") or cfg.get("api_key", "")
            headers = {
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/memolyviza2012-max/THub-Launcher",
                "X-Title": "TStudio"
            }
            payload = {
                "model": model, "temperature": temp_val, "max_tokens": max_tokens_val,
                "messages": [{"role": "user", "content": prompt}]
            }
            res = cls._send_request_with_retry(_session, url, payload, headers, timeout_val, "OpenRouter")
            if res.status_code == 200:
                content = res.json()["choices"][0]["message"]["content"].strip()
            else:
                raise Exception(f"OpenRouter API Error {res.status_code}: {res.text}")

        elif model.startswith("gemini"):
            api_model = model
            if model in ("gemini-2.5-flash", "gemini-1.0-pro", "gemini-pro"):
                api_model = "gemini-2.0-flash"
            elif model in ("gemini-2.5-pro",):
                api_model = "gemini-2.0-pro-exp-02-05"

            url = f"https://generativelanguage.googleapis.com/v1beta/models/{api_model}:generateContent?key={cfg['google_key']}"
            if cloud_base_url: 
                c_url = cloud_base_url.rstrip("/")
                if "generateContent" not in c_url:
                    url = f"{c_url}/v1beta/models/{api_model}:generateContent?key={cfg['google_key']}"
                else:
                    url = f"{c_url}?key={cfg['google_key']}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": temp_val, "maxOutputTokens": max_tokens_val}
            }
            if use_search_grounding:
                payload["tools"] = [{"google_search": {}}]
            res = cls._send_request_with_retry(_session, url, payload, {"Content-Type": "application/json"}, timeout_val, "Gemini")
            if res.status_code == 200:
                try:
                    parts = res.json()["candidates"][0]["content"]["parts"]
                    text_parts = [p.get("text", "") for p in parts if "text" in p]
                    content = "\n".join(text_parts).strip()
                except (KeyError, IndexError) as e:
                    j_data = res.json()
                    finish_reason = j_data.get("candidates", [{}])[0].get("finishReason", "UNKNOWN")
                    raise Exception(f"Gemini API Error: Missing content (Safety block?). FinishReason: {finish_reason}, Data: {j_data}")
            else:
                raise Exception(f"Gemini API Error {res.status_code}: {res.text}")

        elif model.startswith("claude"):
            api_model = model
            if model in ("claude-sonnet-4.6", "claude-3-5-sonnet"):
                api_model = "claude-3-5-sonnet-20241022"
            elif model in ("claude-3-7-sonnet",):
                api_model = "claude-3-7-sonnet-20250219"
            elif model in ("claude-3-5-haiku",):
                api_model = "claude-3-5-haiku-20241022"
            elif model in ("claude-opus-4.8", "claude-3-opus"):
                api_model = "claude-3-opus-20240229"

            url = "https://api.anthropic.com/v1/messages"
            if cloud_base_url: 
                url = cloud_base_url if cloud_base_url.endswith("/messages") else f"{cloud_base_url.rstrip('/')}/v1/messages" if not cloud_base_url.rstrip("/").endswith("/v1") else f"{cloud_base_url.rstrip('/')}/messages"
            headers = {"x-api-key": cfg["anthropic_key"], "anthropic-version": "2023-06-01", "content-type": "application/json"}
            payload = {
                "model": api_model, "max_tokens": max_tokens_val, "temperature": temp_val,
                "messages": [{"role": "user", "content": prompt}]
            }
            res = cls._send_request_with_retry(_session, url, payload, headers, timeout_val, "Claude")
            if res.status_code == 200:
                content = res.json()["content"][0]["text"].strip()
            else:
                raise Exception(f"Claude API Error {res.status_code}: {res.text}")
            
        elif model.startswith("deepseek"):
            url = "https://api.deepseek.com/chat/completions"
            if cloud_base_url:
                url = cloud_base_url if cloud_base_url.endswith("/chat/completions") else f"{cloud_base_url.rstrip('/')}/chat/completions"
            key = cfg.get("deepseek_key") or cfg.get("api_key", "")
            headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

            # Map aliases to official deepseek-chat
            api_model = model
            if model in ("deepseek-v3", "deepseek"):
                api_model = "deepseek-chat"

            payload = {
                "model": api_model, "temperature": temp_val, "max_tokens": max_tokens_val,
                "messages": [{"role": "user", "content": prompt}]
            }
            res = cls._send_request_with_retry(_session, url, payload, headers, timeout_val, f"DeepSeek ({api_model})")
            if res.status_code == 200:
                j = res.json()
                choice = j.get("choices", [{}])[0]
                msg = choice.get("message", {})
                content = str(msg.get("content") or "").strip()
                if not content and "reasoning_content" in msg:
                    reasoning = str(msg.get("reasoning_content") or "").strip()
                    if "{" in reasoning or "[" in reasoning:
                        content = reasoning
                    else:
                        raise Exception(
                            f"DeepSeek ({api_model}) ใช้โควตาโทเค็นในการคิดวิเคราะห์ (Reasoning) จนหมด ({choice.get('finish_reason', 'length')}) "
                            f"ทำให้ไม่มีคำตอบออกมา กรุณาสลับโมเดลเป็น DeepSeek-V3 (deepseek-chat) หรือเพิ่ม Max Tokens ในการตั้งค่า"
                        )
            else:
                raise Exception(f"DeepSeek API Error {res.status_code}: {res.text}")
            
        elif is_local_llm:
            # Ollama / LM Studio defaults (prioritize local base_url or explicit local_url, fallback to LM Studio :1234 or Ollama :11434)
            raw_url = (base_url if is_local_base_url else "") or cfg.get("local_url", "").strip() or "http://localhost:1234/v1/chat/completions"
            if not raw_url.endswith("/chat/completions"):
                url = f"{raw_url.rstrip('/')}/chat/completions"
            else:
                url = raw_url
            headers = {"Content-Type": "application/json"}
            target_model = model if (model and model not in ("custom-local-llm", "Local LLM")) else "local-model"
            payload = {
                "model": target_model, "temperature": temp_val, "max_tokens": max_tokens_val,
                "messages": [{"role": "user", "content": prompt}]
            }
            try:
                res = _session.post(url, json=payload, headers=headers, timeout=timeout_val)
                if res.status_code == 200:
                    content = res.json()["choices"][0]["message"]["content"].strip()
                else:
                    raise Exception(f"Local API Error {res.status_code}: {res.text}")
            except requests.exceptions.ConnectionError:
                raise Exception(f"Could not connect to Local LLM at {url}. Make sure your local server (LM Studio or Ollama) is running.")
                
        else:
            # Assume OpenAI standard
            url = "https://api.openai.com/v1/chat/completions"
            if cloud_base_url:
                url = cloud_base_url if cloud_base_url.endswith("/chat/completions") else f"{cloud_base_url.rstrip('/')}/chat/completions"
            headers = {"Authorization": f"Bearer {cfg['openai_key']}", "Content-Type": "application/json"}
            
            api_model = model
            if model in ("gpt-3.5-turbo", "gpt-4-turbo", "gpt-4"):
                api_model = "gpt-4o-mini"

            # OpenAI o1/o3 reasoning models do not accept custom temperature, and use max_completion_tokens
            if api_model.startswith("o1") or api_model.startswith("o3") or api_model.startswith("o4"):
                payload = {
                    "model": api_model, "max_completion_tokens": max_tokens_val,
                    "messages": [{"role": "user", "content": prompt}]
                }
            else:
                payload = {
                    "model": api_model, "temperature": temp_val, "max_tokens": max_tokens_val,
                    "messages": [{"role": "user", "content": prompt}]
                }
            res = cls._send_request_with_retry(_session, url, payload, headers, timeout_val, "OpenAI")
            if res.status_code == 200:
                content = res.json()["choices"][0]["message"]["content"].strip()
            else:
                raise Exception(f"OpenAI API Error {res.status_code}: {res.text}")
                
        # Post-process 1: Auto-clean known CJK annotation wrappers if leaking from LLM
        content = TStudioCore.clean_cjk_leak(content)
        if not content:
            content = ""

        # Post-process 2: Convert Thai numerals to Arabic numerals
        thai_to_arabic = str.maketrans('๑๒๓๔๕๖๗๘๙๐', '1234567890')
        return content.translate(thai_to_arabic)

    @staticmethod
    def generate_format_parser(cfg, sample_text, ext):
        prompt = f"""You are an expert Python developer.
I need a Python script to parse a custom file format ({ext}) into a TStudio CSV.
The script MUST contain a function `convert_to_csv(filepath, parent_widget=None)`.
It should read the file at `filepath`, extract translatable strings, and write them to a new CSV file in the same directory.
The CSV MUST use `utf-8-sig` encoding and have exactly these columns: ['ID', 'Source', 'Translation', 'AI_Reference'].
If successful, the function MUST return the absolute path to the generated CSV file.

Here is a sample of the {ext} file:
{sample_text}

Return ONLY valid Python code. Do not include markdown code blocks like ```python. Just the code."""
        
        raw_code = CoreAI.generate_content(cfg, prompt)
        
        # Strip markdown if AI still adds it
        if raw_code.startswith("```"):
            lines = raw_code.split('\n')
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            raw_code = "\n".join(lines)
            
        return raw_code.strip()


    @classmethod
    def should_skip_translation(cls, source_text):
        if not source_text or not source_text.strip():
            return True
        import re
        import unicodedata
        # Check for pure numbers and basic symbols only
        if re.match(r'^[\d\s\+\-\*\/\%\.\,\:\;\!\@\#\$\^\&\(\)\[\]\{\}\<\>\_]+$', source_text):
            return True
        
        # Strip out all tag-like tokens: <...>, {...}, [...]
        text_no_tags = re.sub(r'<[^>]*>', '', source_text)       # <Header_NPC>, </>
        text_no_tags = re.sub(r'\{[^}]*\}', '', text_no_tags)   # {Speaker}, {Text}
        text_no_tags = re.sub(r'\[[^\]]*\]', '', text_no_tags)  # [color=red]
        text_no_tags = text_no_tags.strip()
        
        # If nothing remains (or only whitespace/symbols), skip translation
        # Use Unicode letter check to support all natural languages (English, Japanese, Chinese, Korean, Russian, Thai, etc.)
        has_letters = any(unicodedata.category(c).startswith('L') or c.isalpha() for c in text_no_tags)
        if not has_letters:
            return True
            
        return False

    @staticmethod
    def has_cjk(text):
        """Proxy to TStudioCore.has_cjk."""
        return TStudioCore.has_cjk(text)

    @staticmethod
    def extract_cjk(text):
        """Proxy to TStudioCore.extract_cjk."""
        return TStudioCore.extract_cjk(text)

    @staticmethod
    def clean_cjk_leak(text):
        """Proxy to TStudioCore.clean_cjk_leak."""
        return TStudioCore.clean_cjk_leak(text)

    @classmethod
    def clean_ai_translation(cls, source_text, translated_text):
        if not translated_text:
            return translated_text
            
        try:
            import re
            # 1. Pure numbers and basic symbols check
            if re.match(r'^[\d\s\+\-\*\/\%\.\,\:\;\!\@\#\$\^\&\(\)\[\]\{\}\<\>\_]+$', source_text):
                return source_text
                
            cleaned = translated_text.strip()
            
            # Remove Markdown code blocks
            if cleaned.startswith("```"):
                lines = cleaned.split('\n')
                if len(lines) > 1:
                    if lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines[-1].strip() == "```":
                        lines = lines[:-1]
                    cleaned = "\n".join(lines).strip()
                    
            # Remove surrounding quotes if the source didn't have them
            if not (source_text.startswith('"') and source_text.endswith('"')):
                if cleaned.startswith('"') and cleaned.endswith('"'):
                    cleaned = cleaned[1:-1].strip()
            if not (source_text.startswith("'") and source_text.endswith("'")):
                if cleaned.startswith("'") and cleaned.endswith("'"):
                    cleaned = cleaned[1:-1].strip()
                    
            # Hallucination check for short texts
            # CJK (Chinese, Japanese, Korean) characters convey high semantic density in very few characters.
            # For instance, 2 Japanese characters (e.g. 攻撃) translate into 10+ Thai characters (การโจมตี).
            # We adapt the threshold so legitimate CJK translations are never falsely discarded.
            is_cjk = TStudioCore.has_cjk(source_text) or bool(re.search(r'[\u3040-\u30ff\uac00-\ud7af]', source_text))
            if is_cjk:
                if len(source_text) <= 8 and len(cleaned) >= 45 and len(cleaned) > len(source_text) * 10:
                    # Extreme hallucination detected for CJK. Better to return original text than random sentences.
                    return source_text
            else:
                if len(source_text) <= 15:
                    # If translated text is suspiciously long
                    if len(cleaned) >= 20 and len(cleaned) > len(source_text) * 4:
                        # Extreme hallucination detected. Better to return original text than random sentences.
                        return source_text

            return cleaned
        except Exception:
            return translated_text.strip() if isinstance(translated_text, str) else translated_text

class TFormatManager:
    @staticmethod
    def is_standard_csv(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                headers = next(reader, [])
                if len(headers) >= 3 and headers[0].lower() in ['id', 'key'] and 'source' in headers[1].lower():
                    return True
                return False
        except:
            return False

    @staticmethod
    def get_headers(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8-sig', errors='replace') as f:
                reader = csv.reader(f)
                return next(reader, [])
        except:
            return []

    @staticmethod
    def format_to_standard(file_path, mapping, output_path=None):
        original_data = {}
        standard_rows = []
        
        with open(file_path, 'r', encoding='utf-8-sig', errors='replace') as f:
            reader = csv.DictReader(f)
            for row in reader:
                row_id = str(row.get(mapping['id'], '')).strip()
                if not row_id:
                    continue
                    
                src_text = str(row.get(mapping['source'], ''))
                trans_text = str(row.get(mapping['trans'], '')) if mapping['trans'] else ''
                
                original_data[row_id] = row
                standard_rows.append([row_id, src_text, trans_text, ""])

        # Always compute base_dir before using it (BUG 1 fix)
        base_dir = os.path.dirname(output_path) if output_path else os.path.dirname(file_path)

        if output_path is None:
            standard_path = os.path.join(base_dir, "translation.csv")
        else:
            standard_path = output_path
        
        try:
            with open(standard_path, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Source", "Translation", "AI_Reference"])
                writer.writerows(standard_rows)
        except (PermissionError, OSError) as e:
            raise RuntimeError(f'Cannot write to {standard_path}. Is the file open in another program?') from e

        # Use stem-based meta filename instead of hardcoded 'original_data.json' (BUG 1 fix)
        stem = os.path.splitext(os.path.basename(file_path))[0]
        json_path = os.path.join(base_dir, f'{stem}_meta.json')
        wrapper = {
            "mapping": mapping,
            "data": original_data
        }
        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(wrapper, f, indent=4, ensure_ascii=False)
        except (PermissionError, OSError) as e:
            raise RuntimeError(f'Cannot write to {json_path}. Is the file open in another program?') from e
            
        return standard_path

    @staticmethod
    def export_original(translation_csv_path, original_meta_path=None):
        base_dir = os.path.dirname(translation_csv_path)
        stem = os.path.splitext(os.path.basename(translation_csv_path))[0]
        
        if original_meta_path and os.path.exists(original_meta_path):
            json_path = original_meta_path
        else:
            # Fallback for single-file mode: remove '_translated' or similar suffixes if needed
            possible_stem = stem.replace('_translated', '')
            json_path = os.path.join(base_dir, f'{possible_stem}_meta.json')
            if not os.path.exists(json_path):
                json_path = os.path.join(base_dir, f'{stem}_meta.json')
        
        if not os.path.exists(json_path):
            return False, f"No meta json found at {json_path}. Cannot export back to original format."
            
        with open(json_path, 'r', encoding='utf-8') as f:
            wrapper = json.load(f)
            
        mapping = wrapper.get("mapping", {})
        original_data = wrapper.get("data", {})
            
        if not original_data:
            return False, f"{stem}_meta.json is empty."
            
        with open(translation_csv_path, 'r', encoding='utf-8-sig', errors='replace') as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                if len(row) >= 3:
                    row_id = row[0]
                    trans = row[2]
                    if row_id in original_data:
                        if mapping.get('trans'):
                            original_data[row_id][mapping['trans']] = trans
                        else:
                            original_data[row_id]['Translation'] = trans
                            
        first_key = list(original_data.keys())[0]
        original_headers = list(original_data[first_key].keys())
        if not mapping.get('trans') and 'Translation' not in original_headers:
            original_headers.append('Translation')

        # Use stem-based output filename instead of hardcoded 'Translated_Original.csv' (BUG 2 fix)
        output_path = os.path.join(base_dir, f'{stem}_exported.csv')
        try:
            with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=original_headers)
                writer.writeheader()
                for row_id, row_data in original_data.items():
                    writer.writerow(row_data)
        except (PermissionError, OSError) as e:
            raise RuntimeError(f'Cannot write to {output_path}. Is the file open in another program?') from e
                
        return True, output_path


class TPakManager:
    @staticmethod
    def extract_pak_to_csv(filepath):
        import struct
        try:
            with open(filepath, 'rb') as f:
                pdata = f.read()
            
            if len(pdata) < 12:
                return None
                
            version, encoding, padding, resource_count, alias_count = struct.unpack('<IB3sHH', pdata[:12])
            if version != 5:
                return None
                
            # Parse resource index
            resources = []
            offset = 12
            for _ in range(resource_count + 1):
                r_id, r_offset = struct.unpack('<HI', pdata[offset:offset+6])
                resources.append((r_id, r_offset))
                offset += 6
                
            # Extract data and filter text
            entries = []
            for i in range(resource_count):
                r_id, r_offset = resources[i]
                next_offset = resources[i+1][1]
                res_bytes = pdata[r_offset:next_offset]
                
                try:
                    dec_enc = 'utf-16' if encoding == 2 else 'utf-8'
                    val = res_bytes.decode(dec_enc)
                    if len(val) > 0 and all(32 <= ord(c) <= 126 or ord(c) > 127 or c in '\r\n\t' for c in val[:50]):
                        entries.append((f"{r_id}", val))
                except Exception:
                    pass
                    
            if entries:
                base = os.path.splitext(filepath)[0]
                csv_out = base + '_parsed.csv'
                with open(csv_out, 'w', encoding='utf-8-sig', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["ID", "Source", "Translation", "AI_Reference"])
                    for lid, text in entries:
                        writer.writerow([lid, text, '', ''])
                return csv_out
        except Exception as e:
            print(f"Error parsing pak: {e}")
        return None

    @staticmethod
    def reconstruct_pak_file(original_pak_path, csv_path, output_pak_path):
        import struct
        
        with open(original_pak_path, 'rb') as f:
            data = f.read()
            
        version, encoding, padding, resource_count, alias_count = struct.unpack('<IB3sHH', data[:12])
        if version != 5:
            raise ValueError(f"Only Chromium PAK version 5 is supported (got version {version})")
            
        # Parse resource index
        resources = []
        offset = 12
        for _ in range(resource_count + 1):
            r_id, r_offset = struct.unpack('<HI', data[offset:offset+6])
            resources.append((r_id, r_offset))
            offset += 6
            
        # Parse alias index
        aliases = []
        for _ in range(alias_count):
            r_id, entry_idx = struct.unpack('<HH', data[offset:offset+4])
            aliases.append((r_id, entry_idx))
            offset += 4
            
        # Extract original resource bytes
        res_data = {}
        for i in range(resource_count):
            r_id, r_offset = resources[i]
            next_offset = resources[i+1][1]
            res_data[r_id] = data[r_offset:next_offset]
            
        # Read the translated CSV
        translations = {}
        with open(csv_path, 'r', encoding='utf-8-sig', errors='replace') as f:
            reader = csv.reader(f)
            next(reader, None) # skip header
            for row in reader:
                if len(row) >= 3:
                    r_id_str = row[0].strip()
                    trans_text = row[2]
                    if trans_text.strip():
                        try:
                            translations[int(r_id_str)] = trans_text
                        except ValueError:
                            pass
                            
        # Replace resource bytes with translated ones
        dec_enc = 'utf-16' if encoding == 2 else 'utf-8'
        for r_id, trans_val in translations.items():
            if r_id in res_data:
                res_data[r_id] = trans_val.encode(dec_enc)
                
        # Pack back
        start_data_offset = 12 + (resource_count + 1) * 6 + alias_count * 4
        
        packed_data = b''
        offsets = {}
        current_offset = start_data_offset
        
        original_ids = [r_id for r_id, _ in resources[:-1]]
        for r_id in original_ids:
            offsets[r_id] = current_offset
            r_bytes = res_data[r_id]
            packed_data += r_bytes
            current_offset += len(r_bytes)
            
        sentinel_offset = current_offset
        
        res_index_bytes = b''
        for r_id in original_ids:
            res_index_bytes += struct.pack('<HI', r_id, offsets[r_id])
        res_index_bytes += struct.pack('<HI', 0, sentinel_offset)
        
        alias_bytes = b''
        for r_id, entry_idx in aliases:
            alias_bytes += struct.pack('<HH', r_id, entry_idx)
            
        final_data = struct.pack('<IB3sHH', version, encoding, padding, resource_count, alias_count) + res_index_bytes + alias_bytes + packed_data
        
        with open(output_pak_path, 'wb') as f:
            f.write(final_data)


