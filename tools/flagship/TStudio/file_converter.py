from tstudio_i18n import _
import os
import subprocess
import csv
import importlib.util
import requests
import sys
from PyQt6.QtWidgets import QMessageBox, QProgressDialog
from PyQt6.QtCore import Qt

current_dir = os.path.dirname(os.path.abspath(__file__))
if "_internal" in current_dir:
    BASE_DIR = current_dir.split("_internal")[0].rstrip("\\/")
elif getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(current_dir))
    
if "_internal" in current_dir or getattr(sys, 'frozen', False):
    CUSTOM_PARSERS_DIR = os.path.join(BASE_DIR, "TStudio", "CustomParsers")
else:
    CUSTOM_PARSERS_DIR = os.path.join(current_dir, "CustomParsers")
os.makedirs(CUSTOM_PARSERS_DIR, exist_ok=True)

GITHUB_REPO_URL = "https://raw.githubusercontent.com/memolyviza2012-max/TFormat-Plugins/main/"

def auto_convert_to_csv(filepath, parent_widget=None):
    ext = os.path.splitext(filepath)[1].lower()
    
    # 1. Built-in parsers
    if ext in ['.locres', '.lor']:
        return convert_locres_to_tstudio_csv(filepath, parent_widget)
    elif ext == '.pak':
        from tstudio_core import TPakManager
        csv_out = TPakManager.extract_pak_to_csv(filepath)
        if csv_out:
            return csv_out
        raise ValueError("ไม่พบข้อความที่สามารถแปลได้ในไฟล์ .pak นี้ หรือไม่ใช่ Chromium PAK v5")
    elif ext == '.csv':
        return filepath # Already a CSV
        
    # 2. Dynamic Custom Parsers
    ext_clean = ext.replace('.', '')
    parser_filename = f"{ext_clean}_parser.py"
    parser_path = os.path.join(CUSTOM_PARSERS_DIR, parser_filename)
    
    if os.path.exists(parser_path):
        try:
            return load_and_run_parser(parser_path, filepath, parent_widget)
        except Exception as local_e:
            import traceback
            traceback.print_exc()
            if parent_widget:
                QMessageBox.warning(parent_widget, _("plugin_error_title"), _("plugin_old_err_retry", msg=str(local_e)))
            raise local_e
        
    # 3. Check Cloud Repository
    import time
    cloud_url = f"{GITHUB_REPO_URL}{parser_filename}?t={int(time.time())}"
    progress = None
    try:
        if parent_widget:
            progress = QProgressDialog(_("plugin_cloud_searching", ext=ext), _("btn_cancel"), 0, 0, parent_widget)
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.show()
            
        res = requests.get(cloud_url, timeout=10)
        
        if progress:
            progress.close()
            
        if res.status_code == 200:
            with open(parser_path, 'w', encoding='utf-8') as f:
                f.write(res.text)
            return load_and_run_parser(parser_path, filepath, parent_widget)
        elif res.status_code != 404:
            print(f"Cloud download failed with status {res.status_code}")
    except Exception as e:
        if progress:
            progress.close()
        print(f"Network error while fetching plugin: {e}")
            
    # 4. Ask AI to Generate
    if parent_widget:
        reply = QMessageBox.question(parent_widget, _("Unsupported Format"), 
            f"ไม่รู้จักไฟล์นามสกุล '{ext}' และไม่พบปลั๊กอินบน Cloud.\nคุณต้องการให้ AI วิเคราะห์ไฟล์และพยายามเขียนสคริปต์ตัวอ่านไฟล์นี้ให้หรือไม่?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
        if reply == QMessageBox.StandardButton.Yes:
            return generate_and_run_ai_parser(filepath, ext, parser_path, parent_widget)

    raise ValueError(f"ยังไม่รองรับไฟล์นามสกุล: {ext}\nหากคุณมีปลั๊กอิน กรุณานำไปใส่ในโฟลเดอร์ CustomParsers")

def load_and_run_parser(parser_path, filepath, parent_widget):
    try:
        spec = importlib.util.spec_from_file_location("custom_parser", parser_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        if hasattr(module, 'convert_to_csv'):
            return module.convert_to_csv(filepath, parent_widget)
        else:
            raise ValueError(f"ปลั๊กอิน {os.path.basename(parser_path)} ไม่มีฟังก์ชัน convert_to_csv")
    except Exception as e:
        raise ValueError(f"เกิดข้อผิดพลาดในการรันปลั๊กอิน {os.path.basename(parser_path)}: {e}")

def generate_and_run_ai_parser(filepath, ext, parser_path, parent_widget):
    from tstudio_core import TStudioCore, CoreAI
    
    # Read sample
    sample_text = ""
    try:
        with open(filepath, 'rb') as f:
            raw = f.read(3000)
            sample_text = raw.decode('utf-8', errors='replace')
    except Exception as e:
        raise ValueError(f"ไม่สามารถอ่านไฟล์เพื่อส่งให้ AI ได้: {e}")
        
    cfg = TStudioCore.load_config()
    
    progress = QProgressDialog(f"AI กำลังวิเคราะห์และเขียนสคริปต์สำหรับไฟล์ {ext}...", "ยกเลิก", 0, 0, parent_widget)
    progress.setWindowModality(Qt.WindowModality.WindowModal)
    progress.show()
    
    try:
        code = CoreAI.generate_format_parser(cfg, sample_text, ext)
        progress.close()
        
        if not code or "convert_to_csv" not in code:
             raise ValueError("AI ไม่สามารถสร้างโค้ดที่ถูกต้องได้")
             
        with open(parser_path, 'w', encoding='utf-8') as f:
            f.write(code)
            
        QMessageBox.information(parent_widget, "AI Generator", "AI สร้างปลั๊กอินสำเร็จ! กำลังพยายามเปิดไฟล์...")
        return load_and_run_parser(parser_path, filepath, parent_widget)
        
    except Exception as e:
        if progress:
            progress.close()
        raise ValueError(f"AI Generator Error: {e}")

def convert_locres_to_tstudio_csv(filepath, parent_widget=None):
    base_dir = os.path.dirname(filepath)
    name = os.path.splitext(os.path.basename(filepath))[0]
    pylocres_csv = os.path.join(base_dir, f"{name}_pylocres_dump.csv")
    tstudio_csv = os.path.join(base_dir, f"{name}_tstudio.csv")
    
    try:
        env = os.environ.copy()
        env['PYTHONUTF8'] = '1'
        # Call pylocres to dump
        subprocess.run(['pylocres', 'to-csv', '-p', filepath, '-o', pylocres_csv], check=True, env=env, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        
        # Convert pylocres dump to TStudio format
        row_count = 0
        with open(pylocres_csv, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader, None)
            
            if header is None:
                raise ValueError("pylocres extracted an empty file (No data found).")
            
            with open(tstudio_csv, 'w', encoding='utf-8-sig', newline='') as out_f:
                writer = csv.writer(out_f)
                
                for row in reader:
                    # pylocres typical output: namespace, key, hash, source_string
                    if len(row) >= 4:
                        namespace, key, hsh, val = row[0], row[1], row[2], row[3]
                        # Pack metadata into ID column
                        uid = f"{namespace}::{key}::{hsh}"
                        writer.writerow([uid, val, "", ""])
                        row_count += 1
                    elif len(row) >= 2:
                        uid, val = row[0], row[1]
                        writer.writerow([uid, val, "", ""])
                        row_count += 1
                        
        if row_count == 0:
            if os.path.exists(tstudio_csv):
                os.remove(tstudio_csv)
            raise ValueError("No valid translation strings found in the .locres file.")
        
        if parent_widget:
            QMessageBox.information(parent_widget, _("success_title"), f"แปลงไฟล์ {os.path.basename(filepath)} สำเร็จ!\nได้ทั้งหมด {row_count} บรรทัด")
            
        return tstudio_csv
        
    except subprocess.CalledProcessError as e:
        if parent_widget:
            QMessageBox.critical(parent_widget, "pylocres Error", f"Command failed with exit status {e.returncode}")
        raise e
    except Exception as e:
        if parent_widget:
            QMessageBox.critical(parent_widget, _("error_title"), f"ไม่สามารถแปลงไฟล์ได้:\n{str(e)}")
        raise e
    finally:
        # Clean up temporary dump file
        if os.path.exists(pylocres_csv):
            try:
                os.remove(pylocres_csv)
            except:
                pass
