import json
import urllib.request
import os
from pathlib import Path

API_KEY = 'sk-50d1975e48464ad98f0d31281b67ce5e'
URL = 'https://api.deepseek.com/chat/completions'

LANGS = {
    'en': 'English',
    'ja': 'Japanese',
    'zh': 'Chinese (Simplified)',
    'ru': 'Russian',
    'ar': 'Arabic'
}

def translate_dict(data, target_lang):
    prompt = f"Translate the following JSON values from Thai to {target_lang}. Keep the exact same JSON keys. ONLY return the valid JSON object, do not include markdown formatting or backticks.\n\n"
    prompt += json.dumps(data, ensure_ascii=False, indent=2)
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}'
    }
    
    req_data = {
        'model': 'deepseek-chat',
        'messages': [
            {'role': 'system', 'content': 'You are a professional localization translator. Return ONLY valid JSON, no markdown formatting.'},
            {'role': 'user', 'content': prompt}
        ],
        'temperature': 0.1
    }
    
    req = urllib.request.Request(URL, json.dumps(req_data).encode('utf-8'), headers)
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            text = result['choices'][0]['message']['content'].strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            return json.loads(text.strip())
    except Exception as e:
        print(f'Error translating to {target_lang}: {e}')
        return None

def process_locales(app_dir):
    locales_dir = Path(app_dir) / 'locales'
    th_file = locales_dir / 'th.json'
    
    if not th_file.exists():
        print(f"Skipping {app_dir}, th.json not found")
        return
        
    with open(th_file, 'r', encoding='utf-8') as f:
        th_data = json.load(f)
        
    print(f"Translating {app_dir}...")
    for lang_code, lang_name in LANGS.items():
        print(f"  -> {lang_name}...")
        translated = translate_dict(th_data, lang_name)
        if translated:
            out_file = locales_dir / f"{lang_code}.json"
            with open(out_file, 'w', encoding='utf-8') as f:
                json.dump(translated, f, ensure_ascii=False, indent=2)
            print(f"  -> Saved {out_file.name}")

if __name__ == '__main__':
    tfont_dir = r'E:\Mod_Workspace\Modder_project\modder-hub\tools\flagship\TFont'
    tpua_dir = r'E:\Mod_Workspace\Modder_project\modder-hub\tools\flagship\TPUA'
    
    process_locales(tfont_dir)
    process_locales(tpua_dir)
    
    print("All translations completed.")
