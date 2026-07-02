import json
import ast

def main():
    json_path = 'locales/en.json'
    py_path = 'tglyph_app.py'
    
    with open(json_path, 'r', encoding='utf-8') as f:
        translations = json.load(f)
        
    with open(py_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    str_to_key = {v: k for k, v in translations.items()}
    # Also strip emojis and spaces maybe? Let's just do exact match first
    
    tree = ast.parse(content)
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            val = node.value
            if val in str_to_key:
                key = str_to_key[val]
                safe_val = repr(val).encode('ascii', 'backslashreplace').decode('ascii')
                print(f"Line {node.lineno}: {safe_val} -> _('{key}')")

if __name__ == '__main__':
    main()
