import json
import re

def main():
    with open('locales/th.json', 'r', encoding='utf-8') as f:
        th_json = json.load(f)
    with open('locales/en.json', 'r', encoding='utf-8') as f:
        en_json = json.load(f)
        
    str_to_key = {}
    for k, v in th_json.items():
        str_to_key[v] = k
    for k, v in en_json.items():
        str_to_key[v] = k
        
    with open('tglyph_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
        
    strings = sorted(str_to_key.keys(), key=len, reverse=True)
    
    for val in strings:
        key = str_to_key[val]
        
        # We want to replace "val" with _("key")
        # And we want to handle f"val" -> _("key")
        # And 'val' -> _("key")
        # And f'val' -> _("key")
        
        def escape(s): return re.escape(s)
        
        # Match optionally f or F before the quote
        # (f|F)?("val"|'val')
        pattern = r"(f|F)?(\"" + escape(val) + r"\"|'" + escape(val) + r"')"
        content = re.sub(pattern, f'_("{key}")', content)
        
    content = content.replace('from i18n import I18n, PRESET_TEXTS', 'from i18n import I18n, PRESET_TEXTS, _')
    
    with open('tglyph_app.py', 'w', encoding='utf-8') as f:
        f.write(content)
        
if __name__ == '__main__':
    main()
