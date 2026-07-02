import json
import ast
import tokenize
from io import BytesIO

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
        
    with open('tglyph_app.py', 'rb') as f:
        tokens = list(tokenize.tokenize(f.readline))
        
    # We will modify the tokens in place where type is STRING
    
    # Track if we imported _
    # We will just inject it manually later if needed.
    
    new_tokens = []
    for tok in tokens:
        if tok.type == tokenize.STRING:
            # Safely evaluate string literal
            try:
                val = ast.literal_eval(tok.string)
                if isinstance(val, str) and val in str_to_key:
                    key = str_to_key[val]
                    # Replace token string with _("key")
                    new_str = f'_("{key}")'
                    # We need to construct a new token or just patch the string
                    new_tokens.append((tokenize.STRING, new_str))
                    continue
            except Exception:
                pass
        
        new_tokens.append((tok.type, tok.string))
        
    out = tokenize.untokenize(new_tokens).decode('utf-8')
    
    # inject import
    # Find 'from i18n import I18n, PRESET_TEXTS'
    if 'from i18n import I18n, PRESET_TEXTS' in out:
        out = out.replace('from i18n import I18n, PRESET_TEXTS', 'from i18n import I18n, PRESET_TEXTS, _')
    elif 'from i18n import' in out:
        pass # Handle manually if not found exactly
        
    with open('tglyph_app.py', 'w', encoding='utf-8') as f:
        f.write(out)

if __name__ == '__main__':
    main()
