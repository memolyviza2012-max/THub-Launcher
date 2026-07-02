import os
import json
import locale
import threading
import shutil

LOCALE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "locales")
CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "hub_config.json")

# Map of standard Windows/OS language codes to our locale codes
LANG_MAP = {
    "th": "th", "th_th": "th",
    "en": "en", "en_us": "en", "en_gb": "en",
    "zh": "zh", "zh_cn": "zh", "zh_tw": "zh",
    "ja": "ja", "ja_jp": "ja",
    "ar": "ar", "ar_sa": "ar", "ar_ae": "ar",
    "ru": "ru", "ru_ru": "ru"
}

class I18nManager:
    _instance = None
    _lock = threading.RLock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(I18nManager, cls).__new__(cls)
                cls._instance._init()
        return cls._instance

    def _init(self):
        self.current_lang = "en"
        self.translations = {}
        self.load_settings()
        self.load_translations()
        os.environ["THUB_LANG"] = self.current_lang

    def get_system_language(self):
        try:
            # Check environment variables first (most robust cross-platform way)
            for env_var in ['LANGUAGE', 'LC_ALL', 'LC_CTYPE', 'LANG']:
                val = os.environ.get(env_var)
                if val:
                    sys_loc = val.split('.')[0].lower().replace("-", "_")
                    if sys_loc in LANG_MAP:
                        return LANG_MAP[sys_loc]
                    prefix = sys_loc.split("_")[0]
                    if prefix in LANG_MAP:
                        return LANG_MAP[prefix]

            if os.name == 'nt':
                import ctypes
                windll = ctypes.windll.kernel32
                lang = locale.windows_locale.get(windll.GetUserDefaultUILanguage())
                if lang:
                    sys_loc = lang.lower().replace("-", "_")
                    if sys_loc in LANG_MAP:
                        return LANG_MAP[sys_loc]
                    prefix = sys_loc.split("_")[0]
                    if prefix in LANG_MAP:
                        return LANG_MAP[prefix]

            # Fallback to locale.getlocale() (Python 3.11+ compliant)
            loc_tuple = locale.getlocale()
            if loc_tuple and loc_tuple[0]:
                sys_loc = loc_tuple[0].lower().replace("-", "_")
                if sys_loc in LANG_MAP:
                    return LANG_MAP[sys_loc]
                prefix = sys_loc.split("_")[0]
                if prefix in LANG_MAP:
                    return LANG_MAP[prefix]
        except Exception:
            pass
        return "en"

    def load_settings(self):
        # 1. Check environment variable (highest priority for sub-apps)
        env_lang = os.environ.get("THUB_LANG")
        if env_lang and env_lang in LANG_MAP.values():
            self.current_lang = env_lang
            return

        # 2. Check config file
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if "app_language" in config:
                        self.current_lang = config["app_language"]
                        return
            except Exception:
                pass
                
        # 3. Fallback to OS default
        self.current_lang = self.get_system_language()

    def load_translations(self):
        with self._lock:
            self.translations = {} # Explicitly clear existing translations
            
            # Load fallback (English) first
            fallback_path = os.path.join(LOCALE_DIR, "en.json")
            if os.path.exists(fallback_path):
                try:
                    with open(fallback_path, 'r', encoding='utf-8') as f:
                        self.translations = json.load(f)
                except Exception:
                    self.translations = {}
                    
            # Load current language and override
            if self.current_lang != "en":
                lang_path = os.path.join(LOCALE_DIR, f"{self.current_lang}.json")
                if os.path.exists(lang_path):
                    try:
                        with open(lang_path, 'r', encoding='utf-8') as f:
                            current_trans = json.load(f)
                            self.translations.update(current_trans)
                    except Exception:
                        pass

    def translate(self, key, **kwargs):
        with self._lock:
            text = self.translations.get(key, key)
        if kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError:
                pass
        return text
        
    def set_language(self, lang_code):
        if lang_code in LANG_MAP.values() and lang_code != self.current_lang:
            self.current_lang = lang_code
            os.environ["THUB_LANG"] = lang_code
            self.load_translations()
            
            # Save to config safely using atomic write
            with self._lock:
                config = {}
                if os.path.exists(CONFIG_FILE):
                    try:
                        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                            config = json.load(f)
                    except Exception:
                        pass # Ignore corrupted read, just overwrite
                        
                config["app_language"] = self.current_lang
                
                temp_file = CONFIG_FILE + ".tmp"
                try:
                    with open(temp_file, 'w', encoding='utf-8') as f:
                        json.dump(config, f, indent=4, ensure_ascii=False)
                    shutil.move(temp_file, CONFIG_FILE)
                except Exception:
                    if os.path.exists(temp_file):
                        try:
                            os.remove(temp_file)
                        except Exception:
                            pass

# Global instance for easy access
_i18n = I18nManager()

def _(key, **kwargs):
    return _i18n.translate(key, **kwargs)

def set_lang(lang_code):
    _i18n.set_language(lang_code)
