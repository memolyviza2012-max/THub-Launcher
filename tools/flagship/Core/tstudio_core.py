import os
import sys
import json
import csv
import tempfile
import shutil
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
    _PROJECT_PATH = None
    
    @classmethod
    def set_project_path(cls, path):
        if path and os.path.exists(path):
            cls._PROJECT_PATH = path
            
    @classmethod
    def get_prompts_path(cls):
        if cls._PROJECT_PATH:
            p = os.path.join(cls._PROJECT_PATH, "07_TLM_Lore", "project_tlm.json")
            if not os.path.exists(os.path.dirname(p)):
                os.makedirs(os.path.dirname(p), exist_ok=True)
            return p
        return PROMPTS_PATH
    @staticmethod
    def load_config():
        data = {}
        try:
            if os.path.exists(CONFIG_PATH):
                with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            
        # Apply defaults for core settings
        data.setdefault("google_key", "")
        data.setdefault("anthropic_key", "")
        if "api_key" in data and "deepseek_key" not in data:
            data["deepseek_key"] = data["api_key"]
        data.setdefault("deepseek_key", "")
        data.setdefault("openai_key", "")
        data.setdefault("model", "deepseek-chat")
        data.setdefault("provider", "DeepSeek")
        data.setdefault("local_url", "http://localhost:1234/v1/chat/completions")
        if "local_url" in data and "base_url" not in data:
            data["base_url"] = data["local_url"]
        data.setdefault("base_url", "")
        
        # Ensure correct types
        try:
            data["temperature"] = float(data.get("temperature", 0.3))
        except:
            data["temperature"] = 0.3
            
        try:
            data["max_tokens"] = int(data.get("max_tokens", 4096))
        except:
            data["max_tokens"] = 4096
            
        try:
            data["timeout"] = int(data.get("timeout", 30))
        except:
            data["timeout"] = 30
            
        return data

    @staticmethod
    def save_config(cfg):
        try:
            path = CONFIG_PATH
            tmp_fd, tmp_path = tempfile.mkstemp(
                dir=os.path.dirname(os.path.abspath(path)),
                suffix='.tmp'
            )
            try:
                with os.fdopen(tmp_fd, 'w', encoding='utf-8') as f:
                    json.dump(cfg, f, ensure_ascii=False, indent=4)
                shutil.move(tmp_path, path)
            except Exception:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
                raise
        except Exception as e:
            print(f"Error saving config: {e}")

    @classmethod
    def get_last_dir(cls):
        """Returns the last used directory, stored in config.json."""
        try:
            if os.path.exists(CONFIG_PATH):
                with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return data.get("last_dir", "")
        except Exception:
            pass
        return ""

    @classmethod
    def set_last_dir(cls, file_path):
        """Saves the directory of the given file_path to config.json."""
        try:
            data = {}
            if os.path.exists(CONFIG_PATH):
                with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            data["last_dir"] = os.path.dirname(file_path)
            with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error saving last_dir: {e}")

    @classmethod
    def load_profiles(cls):
        data = {
            "active_preset": "Default",
            "presets": {
                "Default": {
                    "single": "",
                    "opt": "",
                    "batch": "", # Added for TRun
                    "glossary": {},
                    "max_bytes_limit": 63
                }
            }
        }
        try:
            target_path = cls.get_prompts_path()
            if os.path.exists(target_path):
                with open(target_path, 'r', encoding='utf-8') as f:
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
                                "glossary": v.get("glossary", {}),
                                "max_bytes_limit": v.get("max_bytes_limit", 63)
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

    @classmethod
    def save_profiles(cls, data):
        try:
            path = cls.get_prompts_path()
            tmp_fd, tmp_path = tempfile.mkstemp(
                dir=os.path.dirname(os.path.abspath(path)),
                suffix='.tmp'
            )
            try:
                with os.fdopen(tmp_fd, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                shutil.move(tmp_path, path)
            except Exception:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
                raise
        except Exception as e:
            print(f"Error saving profiles: {e}")

    @classmethod
    def get_current_profile_data(cls):
        profiles = TStudioCore.load_profiles()
        active = profiles.get("active_preset", "Default")
        return profiles["presets"].get(active, {"single": "", "opt": "", "batch": "", "glossary": {}})

class CoreAI:


    @staticmethod
    def generate_content(cfg, prompt, is_local=False):
        content = ""  # Ensure content is always defined (guard against UnboundLocalError)
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

        timeout_val = cfg.get("timeout", 30)
        temp_val = cfg.get("temperature", 0.3)
        max_tokens_val = cfg.get("max_tokens", 4096)
        base_url = cfg.get("base_url", "").rstrip("/")

        if model.startswith("gemini"):
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={cfg['google_key']}"
            if base_url: 
                base_url = base_url.rstrip("/")
                if "generateContent" not in base_url:
                    url = f"{base_url}/v1beta/models/{model}:generateContent?key={cfg['google_key']}"
                else:
                    url = f"{base_url}?key={cfg['google_key']}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": temp_val, "maxOutputTokens": max_tokens_val}
            }
            res = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=timeout_val)
            if res.status_code == 200:
                try:
                    content = res.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                except (KeyError, IndexError) as e:
                    j_data = res.json()
                    finish_reason = j_data.get("candidates", [{}])[0].get("finishReason", "UNKNOWN")
                    raise Exception(f"Gemini API Error: Missing content (Safety block?). FinishReason: {finish_reason}, Data: {j_data}")
            else:
                raise Exception(f"Gemini API Error {res.status_code}: {res.text}")

        elif model.startswith("claude"):
            url = "https://api.anthropic.com/v1/messages"
            if base_url: 
                url = base_url if base_url.endswith("/messages") else f"{base_url.rstrip('/')}/v1/messages" if not base_url.rstrip("/").endswith("/v1") else f"{base_url.rstrip('/')}/messages"
            headers = {"x-api-key": cfg["anthropic_key"], "anthropic-version": "2023-06-01", "content-type": "application/json"}
            payload = {
                "model": model, "max_tokens": max_tokens_val, "temperature": temp_val,
                "messages": [{"role": "user", "content": prompt}]
            }
            res = requests.post(url, json=payload, headers=headers, timeout=timeout_val)
            if res.status_code == 200:
                content = res.json()["content"][0]["text"].strip()
            else:
                raise Exception(f"Claude API Error {res.status_code}: {res.text}")
            
        elif model.startswith("deepseek"):
            url = "https://api.deepseek.com/chat/completions"
            if base_url:
                url = base_url if base_url.endswith("/chat/completions") else f"{base_url.rstrip('/')}/chat/completions"
            headers = {"Authorization": f"Bearer {cfg['deepseek_key']}", "Content-Type": "application/json"}
            payload = {
                "model": model, "temperature": temp_val, "max_tokens": max_tokens_val,
                "messages": [{"role": "user", "content": prompt}]
            }
            res = requests.post(url, json=payload, headers=headers, timeout=timeout_val)
            if res.status_code == 200:
                content = res.json()["choices"][0]["message"]["content"].strip()
            else:
                raise Exception(f"DeepSeek API Error {res.status_code}: {res.text}")
            
        elif model == "custom-local-llm" or model == "Local LLM":
            # LM Studio / Ollama defaults
            url = base_url if base_url else "http://localhost:1234/v1/chat/completions"
            if not url.endswith("/chat/completions"):
                url = f"{url.rstrip('/')}/chat/completions"
            headers = {"Content-Type": "application/json"}
            payload = {
                "model": "local-model", "temperature": temp_val, "max_tokens": max_tokens_val,
                "messages": [{"role": "user", "content": prompt}]
            }
            try:
                res = requests.post(url, json=payload, headers=headers, timeout=timeout_val)
                if res.status_code == 200:
                    content = res.json()["choices"][0]["message"]["content"].strip()
                else:
                    raise Exception(f"Local API Error {res.status_code}: {res.text}")
            except requests.exceptions.ConnectionError:
                raise Exception(f"Could not connect to Local LLM at {url}. Make sure your server (e.g., LM Studio) is running.")
                
        else:
            # Assume OpenAI standard
            url = "https://api.openai.com/v1/chat/completions"
            if base_url:
                url = base_url if base_url.endswith("/chat/completions") else f"{base_url.rstrip('/')}/chat/completions"
            headers = {"Authorization": f"Bearer {cfg['openai_key']}", "Content-Type": "application/json"}
            payload = {
                "model": model, "temperature": temp_val, "max_tokens": max_tokens_val,
                "messages": [{"role": "user", "content": prompt}]
            }
            res = requests.post(url, json=payload, headers=headers, timeout=timeout_val)
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
    def format_to_standard(file_path, mapping, output_path=None):
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

        # Always compute base_dir before using it (BUG 1 fix)
        base_dir = os.path.dirname(output_path) if output_path else os.path.dirname(file_path)

        if output_path is None:
            standard_path = os.path.join(base_dir, "translation.csv")
        else:
            standard_path = output_path
        
        try:
            with open(standard_path, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Source", "Translation", "AI_Reference"])
                writer.writerows(standard_rows)
        except (PermissionError, OSError) as e:
            raise RuntimeError(f'Cannot write to {standard_path}. Is the file open in another program?') from e

        # Use stem-based meta filename instead of hardcoded 'original_data.json' (BUG 1 fix)
        stem = os.path.splitext(os.path.basename(file_path))[0]
        json_path = os.path.join(base_dir, f'{stem}_meta.json')
        wrapper = {
            "mapping": mapping,
            "data": original_data
        }
        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(wrapper, f, indent=4, ensure_ascii=False)
        except (PermissionError, OSError) as e:
            raise RuntimeError(f'Cannot write to {json_path}. Is the file open in another program?') from e
            
        return standard_path

    @staticmethod
    def export_original(translation_csv_path, original_meta_path=None):
        base_dir = os.path.dirname(translation_csv_path)
        stem = os.path.splitext(os.path.basename(translation_csv_path))[0]
        
        if original_meta_path and os.path.exists(original_meta_path):
            json_path = original_meta_path
        else:
            # Fallback for single-file mode: remove '_translated' or similar suffixes if needed
            possible_stem = stem.replace('_translated', '')
            json_path = os.path.join(base_dir, f'{possible_stem}_meta.json')
            if not os.path.exists(json_path):
                json_path = os.path.join(base_dir, f'{stem}_meta.json')
        
        if not os.path.exists(json_path):
            return False, f"No meta json found at {json_path}. Cannot export back to original format."
            
        with open(json_path, 'r', encoding='utf-8') as f:
            wrapper = json.load(f)
            
        mapping = wrapper.get("mapping", {})
        original_data = wrapper.get("data", {})
            
        if not original_data:
            return False, f"{stem}_meta.json is empty."
            
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

        # Use stem-based output filename instead of hardcoded 'Translated_Original.csv' (BUG 2 fix)
        output_path = os.path.join(base_dir, f'{stem}_exported.csv')
        try:
            with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=original_headers)
                writer.writeheader()
                for row_id, row_data in original_data.items():
                    writer.writerow(row_data)
        except (PermissionError, OSError) as e:
            raise RuntimeError(f'Cannot write to {output_path}. Is the file open in another program?') from e
                
        return True, output_path


class TPakManager:
    @staticmethod
    def extract_pak_to_csv(filepath):
        import struct
        try:
            with open(filepath, 'rb') as f:
                pdata = f.read()
            
            if len(pdata) < 12:
                return None
                
            version, encoding, padding, resource_count, alias_count = struct.unpack('<IB3sHH', pdata[:12])
            if version != 5:
                return None
                
            # Parse resource index
            resources = []
            offset = 12
            for _ in range(resource_count + 1):
                r_id, r_offset = struct.unpack('<HI', pdata[offset:offset+6])
                resources.append((r_id, r_offset))
                offset += 6
                
            # Extract data and filter text
            entries = []
            for i in range(resource_count):
                r_id, r_offset = resources[i]
                next_offset = resources[i+1][1]
                res_bytes = pdata[r_offset:next_offset]
                
                try:
                    dec_enc = 'utf-16' if encoding == 2 else 'utf-8'
                    val = res_bytes.decode(dec_enc)
                    if len(val) > 0 and all(32 <= ord(c) <= 126 or ord(c) > 127 or c in '\r\n\t' for c in val[:50]):
                        entries.append((f"{r_id}", val))
                except Exception:
                    pass
                    
            if entries:
                base = os.path.splitext(filepath)[0]
                csv_out = base + '_parsed.csv'
                with open(csv_out, 'w', encoding='utf-8-sig', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["ID", "Source", "Translation", "AI_Reference"])
                    for lid, text in entries:
                        writer.writerow([lid, text, '', ''])
                return csv_out
        except Exception as e:
            print(f"Error parsing pak: {e}")
        return None

    @staticmethod
    def reconstruct_pak_file(original_pak_path, csv_path, output_pak_path):
        import struct
        
        with open(original_pak_path, 'rb') as f:
            data = f.read()
            
        version, encoding, padding, resource_count, alias_count = struct.unpack('<IB3sHH', data[:12])
        if version != 5:
            raise ValueError(f"Only Chromium PAK version 5 is supported (got version {version})")
            
        # Parse resource index
        resources = []
        offset = 12
        for _ in range(resource_count + 1):
            r_id, r_offset = struct.unpack('<HI', data[offset:offset+6])
            resources.append((r_id, r_offset))
            offset += 6
            
        # Parse alias index
        aliases = []
        for _ in range(alias_count):
            r_id, entry_idx = struct.unpack('<HH', data[offset:offset+4])
            aliases.append((r_id, entry_idx))
            offset += 4
            
        # Extract original resource bytes
        res_data = {}
        for i in range(resource_count):
            r_id, r_offset = resources[i]
            next_offset = resources[i+1][1]
            res_data[r_id] = data[r_offset:next_offset]
            
        # Read the translated CSV
        translations = {}
        with open(csv_path, 'r', encoding='utf-8-sig', errors='replace') as f:
            reader = csv.reader(f)
            next(reader, None) # skip header
            for row in reader:
                if len(row) >= 3:
                    r_id_str = row[0].strip()
                    trans_text = row[2]
                    if trans_text.strip():
                        try:
                            translations[int(r_id_str)] = trans_text
                        except ValueError:
                            pass
                            
        # Replace resource bytes with translated ones
        dec_enc = 'utf-16' if encoding == 2 else 'utf-8'
        for r_id, trans_val in translations.items():
            if r_id in res_data:
                res_data[r_id] = trans_val.encode(dec_enc)
                
        # Pack back
        start_data_offset = 12 + (resource_count + 1) * 6 + alias_count * 4
        
        packed_data = b''
        offsets = {}
        current_offset = start_data_offset
        
        original_ids = [r_id for r_id, _ in resources[:-1]]
        for r_id in original_ids:
            offsets[r_id] = current_offset
            r_bytes = res_data[r_id]
            packed_data += r_bytes
            current_offset += len(r_bytes)
            
        sentinel_offset = current_offset
        
        res_index_bytes = b''
        for r_id in original_ids:
            res_index_bytes += struct.pack('<HI', r_id, offsets[r_id])
        res_index_bytes += struct.pack('<HI', 0, sentinel_offset)
        
        alias_bytes = b''
        for r_id, entry_idx in aliases:
            alias_bytes += struct.pack('<HH', r_id, entry_idx)
            
        final_data = struct.pack('<IB3sHH', version, encoding, padding, resource_count, alias_count) + res_index_bytes + alias_bytes + packed_data
        
        with open(output_pak_path, 'wb') as f:
            f.write(final_data)


