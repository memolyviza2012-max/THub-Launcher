import os
import re
import json
import csv
import UnityPy

class TBundleManager:
    @staticmethod
    def is_unity_bundle(file_path):
        if not os.path.exists(file_path):
            return False
        try:
            with open(file_path, 'rb') as f:
                header = f.read(8)
                if header.startswith(b'UnityFS') or header.startswith(b'UnityWeb') or header.startswith(b'UnityRaw'):
                    return True
        except:
            pass
        return False

    @staticmethod
    def extract_video(bundle_path, out_dir):
        """Extracts the first VideoClip from the bundle into out_dir, returns the extracted file path."""
        env = UnityPy.load(bundle_path)
        for obj in env.objects:
            if obj.type.name == 'VideoClip':
                data = obj.read()
                res = data.m_ExternalResources
                source_name = res.m_Source.split('/')[-1]
                res_file = env.file.files.get(source_name)
                
                if not os.path.exists(out_dir):
                    os.makedirs(out_dir)
                
                if res_file:
                    res_file.Position = res.m_Offset
                    video_bytes = res_file.read_bytes(res.m_Size)
                    
                    # Detect format
                    ext = "mp4"
                    if video_bytes.startswith(b'\x1aE\xdf\xa3'):
                        ext = "webm"
                        
                    out_path = os.path.join(out_dir, f"{os.path.basename(bundle_path)}_temp.{ext}")
                    with open(out_path, 'wb') as f:
                        f.write(video_bytes)
                    return out_path
        return None

    @staticmethod
    def extract_text_to_csv(bundle_path):
        """Extracts text from TextAsset or Fantasian MonoBehaviour to CSV."""
        env = UnityPy.load(bundle_path)
        
        srt_text = ""
        text_asset_name = ""
        
        # 1. Try TextAsset (EvilSchool format)
        for obj in env.objects:
            if obj.type.name == 'TextAsset':
                data = obj.read()
                srt_text = getattr(data, 'm_Script', getattr(data, 'text', ''))
                text_asset_name = getattr(data, 'm_Name', getattr(data, 'name', ''))
                break
                
        if srt_text:
            blocks = re.split(r'\n\s*\n', srt_text.strip().replace('\r', ''))
            original_data = {}
            standard_rows = []
            for block in blocks:
                lines = block.split('\n')
                if len(lines) >= 3:
                    idx = lines[0].strip()
                    if idx.startswith('\ufeff'):
                        idx = idx.replace('\ufeff', '')
                    timestamp = lines[1].strip()
                    text = "\n".join(lines[2:]).strip()
                    
                    row_id = idx
                    original_data[row_id] = {
                        "idx": idx,
                        "timestamp": timestamp,
                        "text": text
                    }
                    standard_rows.append([row_id, "", text, ""])
                    
            base_dir = os.path.dirname(bundle_path)
            csv_path = os.path.join(base_dir, f"{os.path.basename(bundle_path)}.csv")
            with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Source", "Translation", "AI_Reference"])
                writer.writerows(standard_rows)
                
            json_path = os.path.join(base_dir, f"{os.path.basename(bundle_path)}_meta.json")
            wrapper = {
                "format": "EvilSchool_TextAsset",
                "bundle_path": bundle_path,
                "text_asset_name": text_asset_name,
                "data": original_data
            }
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(wrapper, f, indent=4, ensure_ascii=False)
                
            return csv_path

        # 2. Try Fantasian MonoBehaviour
        for obj in env.objects:
            if obj.type.name == 'MonoBehaviour':
                try:
                    tree = obj.read_typetree()
                    if 'messageDictionary' in tree and 'entries' in tree['messageDictionary']:
                        entries = tree['messageDictionary']['entries']
                        standard_rows = []
                        for entry in entries:
                            key = entry.get('key', '')
                            val = entry.get('value', {})
                            message = val.get('Message', '')
                            standard_rows.append([key, message, "", ""])
                            
                        base_dir = os.path.dirname(bundle_path)
                        csv_path = os.path.join(base_dir, f"{os.path.basename(bundle_path)}.csv")
                        with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
                            writer = csv.writer(f)
                            writer.writerow(["ID", "Source", "Translation", "AI_Reference"])
                            writer.writerows(standard_rows)
                            
                        json_path = os.path.join(base_dir, f"{os.path.basename(bundle_path)}_meta.json")
                        wrapper = {
                            "format": "Fantasian_MonoBehaviour",
                            "bundle_path": bundle_path,
                            "original_tree": tree
                        }
                        with open(json_path, 'w', encoding='utf-8') as f:
                            json.dump(wrapper, f, indent=4, ensure_ascii=False)
                            
                        return csv_path
                except Exception as e:
                    print(f"Error parsing MonoBehaviour: {e}")
                    
        return None

    @staticmethod
    def deploy_csv_to_bundle(csv_path):
        """Reads the CSV, updates the structure, and repacks it back into the original bundle."""
        base_dir = os.path.dirname(csv_path)
        json_path = os.path.join(base_dir, f"{os.path.basename(csv_path).replace('.csv', '')}_meta.json")
        
        if not os.path.exists(json_path):
            return False, "Metadata file missing. Cannot deploy."
            
        with open(json_path, 'r', encoding='utf-8') as f:
            wrapper = json.load(f)
            
        bundle_path = wrapper.get("bundle_path")
        if not bundle_path or not os.path.exists(bundle_path):
            return False, "Original bundle not found."
            
        fmt = wrapper.get("format", "EvilSchool_TextAsset")
        
        # Load CSV Translations
        translations = {}
        with open(csv_path, 'r', encoding='utf-8-sig', errors='replace') as f:
            reader = csv.reader(f)
            next(reader, None) # Skip header
            for row in reader:
                if len(row) >= 3:
                    row_id = row[0]
                    trans = row[2] if str(row[2]).strip() else row[1] # fallback to source if empty
                    translations[row_id] = trans

        try:
            env = UnityPy.load(bundle_path)
            
            if fmt == "EvilSchool_TextAsset":
                original_data = wrapper.get("data", {})
                for row_id, trans in translations.items():
                    if row_id in original_data:
                        original_data[row_id]["text"] = trans

                new_srt_blocks = []
                is_first = True
                for row_id, data in original_data.items():
                    idx = data["idx"]
                    if is_first:
                        idx = '\ufeff' + idx
                        is_first = False
                    block = f"{idx}\r\n{data['timestamp']}\r\n{data['text']}\r\n"
                    new_srt_blocks.append(block)
                    
                new_srt_text = "\r\n".join(new_srt_blocks)
                
                for obj in env.objects:
                    if obj.type.name == 'TextAsset':
                        data = obj.read()
                        data.m_Script = new_srt_text
                        data.save()
                        break
                        
            elif fmt == "Fantasian_MonoBehaviour":
                tree = wrapper.get("original_tree", {})
                if 'messageDictionary' in tree and 'entries' in tree['messageDictionary']:
                    entries = tree['messageDictionary']['entries']
                    for entry in entries:
                        key = entry.get('key', '')
                        if key in translations:
                            entry['value']['Message'] = translations[key]
                            
                for obj in env.objects:
                    if obj.type.name == 'MonoBehaviour':
                        try:
                            # Verify if it's the target MonoBehaviour
                            check_tree = obj.read_typetree()
                            if 'messageDictionary' in check_tree:
                                obj.save_typetree(tree)
                                break
                        except Exception as e:
                            pass
                            
            with open(bundle_path, 'wb') as f:
                f.write(env.file.save())
                
            return True, bundle_path
        except Exception as e:
            return False, str(e)
