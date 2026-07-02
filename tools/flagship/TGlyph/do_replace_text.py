import json

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
        
    # We will do text replacement for all keys, prioritizing longer strings first
    # Sort strings by length descending to prevent partial match replacement
    strings = sorted(str_to_key.keys(), key=len, reverse=True)
    
    for val in strings:
        key = str_to_key[val]
        
        # We need to replace exactly the string literal
        # It could be single quoted or double quoted
        # Try both
        
        # Double quotes
        literal_double = '"' + val + '"'
        new_str = f'_("{key}")'
        content = content.replace(literal_double, new_str)
        
        # Single quotes
        literal_single = "'" + val + "'"
        content = content.replace(literal_single, new_str)
        
    # Also inject the import
    content = content.replace('from i18n import I18n, PRESET_TEXTS', 'from i18n import I18n, PRESET_TEXTS, _')
    
    with open('tglyph_app.py', 'w', encoding='utf-8') as f:
        f.write(content)
        
if __name__ == '__main__':
    main()
