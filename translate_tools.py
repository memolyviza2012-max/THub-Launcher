import os
import json
import requests

API_KEY = "sk-50d1975e48464ad98f0d31281b67ce5e"
URL = "https://api.deepseek.com/v1/chat/completions"

def translate_file(path_en, path_th):
    print(f"Translating {path_en}...")
    with open(path_en, 'r', encoding='utf-8') as f:
        en_data = json.load(f)
        
    prompt = f"""You are a professional Thai translator for a game modding tool called 'Thub'.
Please translate the following JSON values from English to Thai. 
Keep the JSON keys exactly the same. Do not translate the keys.
Keep placeholders like {{e}}, {{err}}, {{std}}, {{ctx}}, {{count}}, {{orig}}, {{final}}, {{diff}}, {{path}} exactly as they are.
Output ONLY the raw valid JSON, without any markdown formatting like ```json or anything else.

English JSON:
{json.dumps(en_data, indent=2)}
"""

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a professional software translator."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1
    }
    
    response = requests.post(URL, headers=headers, json=payload)
    if response.status_code == 200:
        result = response.json()
        translated_text = result["choices"][0]["message"]["content"].strip()
        if translated_text.startswith("```json"):
            translated_text = translated_text[7:]
        if translated_text.endswith("```"):
            translated_text = translated_text[:-3]
        
        translated_text = translated_text.strip()
        
        # Verify it's valid JSON
        try:
            th_data = json.loads(translated_text)
            with open(path_th, 'w', encoding='utf-8') as f:
                json.dump(th_data, f, ensure_ascii=False, indent=2)
            print(f"Successfully saved {path_th}")
        except Exception as e:
            print(f"Failed to parse JSON for {path_th}: {e}")
            print(translated_text)
    else:
        print(f"API Error: {response.status_code}")
        print(response.text)

def main():
    base_dir = "E:/Mod_Workspace/Modder_project/modder-hub/tools/flagship"
    
    tpua_en = os.path.join(base_dir, "TPUA", "locales", "en.json")
    tpua_th = os.path.join(base_dir, "TPUA", "locales", "th.json")
    
    tfont_en = os.path.join(base_dir, "TFont", "locales", "en.json")
    tfont_th = os.path.join(base_dir, "TFont", "locales", "th.json")
    
    translate_file(tpua_en, tpua_th)
    translate_file(tfont_en, tfont_th)

if __name__ == "__main__":
    main()
