import os
import sys
import json
import csv
import sys
csv.field_size_limit(2147483647)
import requests

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_PATH  = os.path.join(BASE_DIR, "config.json")
GLOSSARY_PATH = os.path.join(BASE_DIR, "glossary.json")
PROMPTS_PATH = os.path.join(BASE_DIR, "prompts.json")

DEFAULT_SINGLE_PROMPT = """You are a Master-Level English-to-Thai Video Game Localization Specialist.
Translate this line. ID: '{id}'. Return ONLY the pure Thai string, no quotes, no explanations.
[GLOSSARY TO USE]

Text: {source_text}"""

DEFAULT_OPTIONS_PROMPT = """You are a Master-Level English-to-Thai Video Game Localization Specialist.
Translate this into 3 distinct styles:
1. Literal/Direct (แปลตรงตัว)
2. Casual/Slang (ภาษาพูด/สแลง)
3. Polite/Formal (สุภาพ/ทางการ)
ID: '{id}'.

[GLOSSARY TO USE]

Return ONLY a valid JSON array of 3 strings: ["option1", "option2", "option3"]
Text: {source_text}"""

class TStudioCore:
    @staticmethod
    def load_config():
        data = {}
        try:
            if os.path.exists(CONFIG_PATH):
                with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            
        return {
            "google_key": data.get("google_key", ""),
            "anthropic_key": data.get("anthropic_key", ""),
            "deepseek_key": data.get("deepseek_key", data.get("api_key", "")),
            "openai_key": data.get("openai_key", ""),
            "model": data.get("model", "deepseek-chat"),
            "provider": data.get("provider", "DeepSeek"),
            "local_url": data.get("local_url", "http://localhost:1234/v1/chat/completions")
        }

    @staticmethod
    def save_config(cfg):
        try:
            with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(cfg, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    @staticmethod
    def load_profiles():
        data = {
            "active_preset": "Default",
            "presets": {
                "Default": {
                    "single": "",
                    "opt": "",
                    "batch": "", # Added for TRun
                    "glossary": {}
                }
            }
        }
        try:
            if os.path.exists(PROMPTS_PATH):
                with open(PROMPTS_PATH, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    if "single_prompt" in loaded:
                        data["presets"]["Default"]["single"] = loaded.get("single_prompt", DEFAULT_SINGLE_PROMPT)
                        data["presets"]["Default"]["opt"] = loaded.get("opt_prompt", DEFAULT_OPTIONS_PROMPT)
                        data["presets"]["Default"]["batch"] = loaded.get("batch_prompt", DEFAULT_SINGLE_PROMPT)
                    else:
                        data["active_preset"] = loaded.get("active_preset", "Default")
                        for k, v in loaded.get("presets", {}).items():
                            data["presets"][k] = {
                                "single": v.get("single", ""),
                                "opt": v.get("opt", ""),
                                "batch": v.get("batch", v.get("single", "")),
                                "glossary": v.get("glossary", {})
                            }
        except json.JSONDecodeError as e:
            print(f"Failed to parse prompts.json: {e}")
        except Exception as e:
            print(f"Error reading prompts.json: {e}")
        
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
                
        return data

    @staticmethod
    def save_profiles(data):
        try:
            with open(PROMPTS_PATH, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error saving profiles: {e}")

    @staticmethod
    def get_current_profile_data():
        profiles = TStudioCore.load_profiles()
        active = profiles.get("active_preset", "Default")
        return profiles["presets"].get(active, {"single": "", "opt": "", "batch": "", "glossary": {}})

class CoreAI:
    _session = requests.Session()


    @staticmethod
    def generate_content(cfg, prompt, is_local=False):
        model = cfg.get("model", "deepseek-chat")
        if is_local:
            model = "custom-local-llm"
            
        if model != "custom-local-llm" and model != "Local LLM":
            if model.startswith("gemini") and not cfg.get("google_key"):
                raise Exception("Google Gemini API Key is missing! Please configure it in Settings.")
            elif model.startswith("claude") and not cfg.get("anthropic_key"):
                raise Exception("Anthropic Claude API Key is missing! Please configure it in Settings.")
            elif model.startswith("deepseek") and not cfg.get("deepseek_key"):
                raise Exception("DeepSeek API Key is missing! Please configure it in Settings.")
            elif not model.startswith("gemini") and not model.startswith("claude") and not model.startswith("deepseek") and not cfg.get("openai_key"):
                raise Exception("OpenAI API Key is missing! Please configure it in Settings.")

        if model.startswith("gemini"):
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={cfg['google_key']}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.3}
            }
            res = CoreAI._session.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=30)
            if res.status_code == 200:
                content = res.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
            else:
                raise Exception(f"Gemini API Error {res.status_code}: {res.text}")

        elif model.startswith("claude"):
            url = "https://api.anthropic.com/v1/messages"
            headers = {"x-api-key": cfg["anthropic_key"], "anthropic-version": "2023-06-01", "content-type": "application/json"}
            payload = {
                "model": model, "max_tokens": 4096, "temperature": 0.3,
                "messages": [{"role": "user", "content": prompt}]
            }
            res = CoreAI._session.post(url, json=payload, headers=headers, timeout=30)
            if res.status_code == 200:
                content = res.json()["content"][0]["text"].strip()
            else:
                raise Exception(f"Claude API Error {res.status_code}: {res.text}")
            
        elif model.startswith("deepseek"):
            url = "https://api.deepseek.com/chat/completions"
            headers = {"Authorization": f"Bearer {cfg['deepseek_key']}", "Content-Type": "application/json"}
            payload = {
                "model": model, "temperature": 0.3,
                "messages": [{"role": "user", "content": prompt}]
            }
            res = CoreAI._session.post(url, json=payload, headers=headers, timeout=30)
            if res.status_code == 200:
                content = res.json()["choices"][0]["message"]["content"].strip()
            else:
                raise Exception(f"DeepSeek API Error {res.status_code}: {res.text}")
            
        elif model == "custom-local-llm" or model == "Local LLM":
            # LM Studio / Ollama defaults
            url = "http://localhost:1234/v1/chat/completions"
            headers = {"Content-Type": "application/json"}
            payload = {
                "model": "local-model", "temperature": 0.3,
                "messages": [{"role": "user", "content": prompt}]
            }
            try:
                res = CoreAI._session.post(url, json=payload, headers=headers, timeout=30)
                if res.status_code == 200:
                    content = res.json()["choices"][0]["message"]["content"].strip()
                else:
                    raise Exception(f"Local API Error {res.status_code}: {res.text}")
            except requests.exceptions.ConnectionError:
                raise Exception("Could not connect to Local LLM at http://localhost:1234/v1. Make sure your server (e.g., LM Studio) is running.")
                
        else:
            # Assume OpenAI standard
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {cfg['openai_key']}", "Content-Type": "application/json"}
            payload = {
                "model": model, "temperature": 0.3,
                "messages": [{"role": "user", "content": prompt}]
            }
            res = CoreAI._session.post(url, json=payload, headers=headers, timeout=30)
            if res.status_code == 200:
                content = res.json()["choices"][0]["message"]["content"].strip()
            else:
                raise Exception(f"OpenAI API Error {res.status_code}: {res.text}")
                
        # Post-process: Convert Thai numerals to Arabic numerals
        thai_to_arabic = str.maketrans('๑๒๓๔๕๖๗๘๙๐', '1234567890')
        return content.translate(thai_to_arabic)


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
    def format_to_standard(file_path, mapping):
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

        base_dir = os.path.dirname(file_path)
        standard_path = os.path.join(base_dir, "translation.csv")
        
        with open(standard_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Source", "Translation", "AI_Reference"])
            writer.writerows(standard_rows)
            
        json_path = os.path.join(base_dir, "original_data.json")
        wrapper = {
            "mapping": mapping,
            "data": original_data
        }
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(wrapper, f, indent=4, ensure_ascii=False)
            
        return standard_path

    @staticmethod
    def export_original(translation_csv_path):
        base_dir = os.path.dirname(translation_csv_path)
        json_path = os.path.join(base_dir, "original_data.json")
        
        if not os.path.exists(json_path):
            return False, "No original_data.json found. Cannot export back to original format."
            
        with open(json_path, 'r', encoding='utf-8') as f:
            wrapper = json.load(f)
            
        mapping = wrapper.get("mapping", {})
        original_data = wrapper.get("data", {})
            
        if not original_data:
            return False, "original_data.json is empty."
            
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
            
        output_path = os.path.join(base_dir, "Translated_Original.csv")
        with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=original_headers)
            writer.writeheader()
            for row_id, row_data in original_data.items():
                writer.writerow(row_data)
                
        return True, output_path

