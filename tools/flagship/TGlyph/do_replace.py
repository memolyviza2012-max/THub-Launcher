import json
import ast

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
    replacements = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            val = node.value
            if val in str_to_key:
                key = str_to_key[val]
                replacements.append({
                    'lineno': node.lineno - 1,
                    'col_offset': node.col_offset,
                    'end_col_offset': node.end_col_offset,
                    'new_str': f'_("{key}")'
                })
                
    lines = content.splitlines()
    
    # group by line
    by_line = {}
    for r in replacements:
        by_line.setdefault(r['lineno'], []).append(r)
        
    for lineno, reps in by_line.items():
        reps.sort(key=lambda x: x['col_offset'], reverse=True)
        line = lines[lineno]
        for r in reps:
            line = line[:r['col_offset']] + r['new_str'] + line[r['end_col_offset']:]
        lines[lineno] = line
        
    out = '\n'.join(lines)
    
    # Fix import
    out = out.replace('from i18n import I18n, PRESET_TEXTS', 'from i18n import I18n, PRESET_TEXTS, _')
    
    with open('tglyph_app.py', 'w', encoding='utf-8') as f:
        f.write(out)
        
if __name__ == '__main__':
    main()
