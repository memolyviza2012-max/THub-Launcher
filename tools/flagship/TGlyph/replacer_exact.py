import json
import ast
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
        
    tree = ast.parse(content)
    
    # Collect all exact replacements: (start_pos, end_pos, new_string)
    # But ast node positions are not character offsets in python 3.7. 
    # In 3.8+ we have end_col_offset. But in UTF-8, col_offset is by unicode character or bytes?
    # It's by unicode character. So we can split by lines and replace by character offset!
    
    replacements_by_line = {}
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            val = node.value
            if val in str_to_key:
                lineno = node.lineno - 1
                col_offset = node.col_offset
                end_col_offset = node.end_col_offset
                key = str_to_key[val]
                
                if lineno not in replacements_by_line:
                    replacements_by_line[lineno] = []
                replacements_by_line[lineno].append({
                    'start': col_offset,
                    'end': end_col_offset,
                    'new_str': f'_("{key}")'
                })
                
    lines = content.splitlines()
    for lineno, reps in replacements_by_line.items():
        # Sort backwards to not mess up offsets
        reps.sort(key=lambda x: x['start'], reverse=True)
        line = lines[lineno]
        for r in reps:
            start = r['start']
            end = r['end']
            line = line[:start] + r['new_str'] + line[end:]
        lines[lineno] = line
        
    out = '\n'.join(lines)
    
    # Now replace the import
    out = out.replace('from i18n import I18n, PRESET_TEXTS', 'from i18n import I18n, PRESET_TEXTS, _')
    
    with open('tglyph_app.py', 'w', encoding='utf-8') as f:
        f.write(out)

if __name__ == '__main__':
    main()
