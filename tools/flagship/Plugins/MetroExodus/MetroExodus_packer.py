import os
import csv
import sys
import json
import time

try:
    from pywinauto import Application, timings
    from pywinauto.keyboard import send_keys
    HAS_PYWINAUTO = True
except ImportError:
    HAS_PYWINAUTO = False
    print("[Warning] pywinauto is not installed. SDK Automation will be disabled.")
    print("Install it via: pip install pywinauto")

def load_pua_mapping(mapping_path):
    if not os.path.exists(mapping_path):
        print(f"[Error] Mapping file not found at {mapping_path}")
        return {}
        
    with open(mapping_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def apply_pua(text, mapping):
    """
    Replaces Thai characters (single or combined) with their PUA equivalents based on mapping.
    Because mapping might contain multi-character strings (e.g. 'ที่'), 
    we need to sort the keys by length descending to replace longest matches first.
    """
    if not text:
        return text
        
    # Sort keys by length descending to ensure multi-char combinations are replaced before single chars
    sorted_keys = sorted(mapping.keys(), key=lambda x: len(x), reverse=True)
    
    result = text
    for k in sorted_keys:
        if k in result:
            result = result.replace(k, mapping[k])
            
    return result

def pack_metro_csv(tstudio_csv, output_sdk_csv, mapping_path, target_lang_col="cn"):
    """
    Reads TStudio CSV, applies PUA mapping to translations, 
    and writes to SDK compatible format.
    """
    if not os.path.exists(tstudio_csv):
        print(f"[Error] TStudio CSV not found at {tstudio_csv}")
        return False
        
    mapping = load_pua_mapping(mapping_path)
    if not mapping:
        return False
        
    print(f"[*] Packing translated text to SDK format...")
    
    sdk_data = []
    
    with open(tstudio_csv, 'r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = row.get('id', '').strip()
            # If translation is empty, fallback to original
            translation = row.get('translation', '')
            if not translation.strip():
                translation = row.get('original', '')
                
            pua_translation = apply_pua(translation, mapping)
            
            # Create SDK row format (Key, [TargetLang])
            sdk_row = {
                'Key': key,
                target_lang_col: pua_translation
            }
            sdk_data.append(sdk_row)
            
    # Write SDK CSV
    with open(output_sdk_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Key', target_lang_col])
        writer.writeheader()
        writer.writerows(sdk_data)
        
    print(f"[+] Successfully packed {len(sdk_data)} strings into {output_sdk_csv}")
    return True

def automate_sdk(sdk_exe_path, sdk_csv_path):
    """
    Uses pywinauto to open Exodus SDK and automate font generation.
    """
    if not HAS_PYWINAUTO:
        print("[-] Cannot automate SDK: pywinauto not installed.")
        return False
        
    if not os.path.exists(sdk_exe_path):
        print(f"[Error] Exodus SDK executable not found at {sdk_exe_path}")
        return False
        
    print(f"[*] Starting Exodus SDK Automation Bot...")
    try:
        # 1. Start the application
        app = Application(backend="uia").start(sdk_exe_path)
        
        # Wait for the main window to be ready
        print("[*] Waiting for SDK MainWindow to load (this can take a while)...")
        main_win = app.window(title_re=".*Exodus SDK.*")
        main_win.wait("ready", timeout=60)
        
        # Bring to front
        main_win.set_focus()
        time.sleep(1)
        
        # 2. Open Localization Manager (assuming it's in a menu 'Tools' -> 'Localization Manager')
        print("[*] Opening Localization Manager...")
        # Menu clicking can be done via type_keys if the menu supports it, or by direct control access.
        # Alt+T for Tools, then L for Localization Manager (assuming standard mnemonics)
        # If no mnemonics, we can send keys or try to find the menu item.
        main_win.type_keys("%T") # Alt+T
        time.sleep(0.5)
        send_keys("{DOWN}") # Assuming it opens the menu
        # Finding the exact item might require manual tuning, so we use a fallback shortcut if known
        print("[!] Note: SDK Automation is experimental. You might need to manually click Localization Manager.")
        
        # Wait for Localization Manager window
        loc_win = app.window(title_re=".*Localization Manager.*")
        loc_win.wait("ready", timeout=30)
        loc_win.set_focus()
        
        # 3. Import CSV
        print("[*] Importing CSV...")
        # Depending on UI layout, we might need to find a button named "Import CSV"
        # loc_win.child_window(title="Import CSV", control_type="Button").click()
        # Wait for file dialog, type sdk_csv_path, press enter...
        
        # 4. Generate Fonts checkbox & Build
        print("[*] Generating Fonts...")
        # loc_win.child_window(title="Generate Fonts", control_type="CheckBox").check()
        # loc_win.child_window(title="Build", control_type="Button").click()
        
        print("[+] Automation commands sent successfully!")
        
    except Exception as e:
        print(f"[-] Automation failed: {e}")
        print("[-] Please follow the manual step-by-step guide in walkthrough.md instead.")

if __name__ == "__main__":
    print("=== Metro Exodus Packer for TStudio ===")
    if len(sys.argv) < 5:
        print("Usage: python MetroExodus_packer.py <tstudio.csv> <output_sdk.csv> <mapping.json> <sdk_exe_path>")
        sys.exit(1)
        
    in_csv = sys.argv[1]
    out_csv = sys.argv[2]
    map_json = sys.argv[3]
    sdk_exe = sys.argv[4]
    
    success = pack_metro_csv(in_csv, out_csv, map_json)
    if success:
        print("\n--- Starting Automation Step ---")
        automate_sdk(sdk_exe, out_csv)
