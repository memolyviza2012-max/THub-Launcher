import os
import subprocess
import csv
from PyQt6.QtWidgets import QMessageBox

def auto_convert_to_csv(filepath, parent_widget=None):
    ext = os.path.splitext(filepath)[1].lower()
    if ext in ['.locres', '.lor']:
        return convert_locres_to_tstudio_csv(filepath, parent_widget)
    elif ext == '.csv':
        return filepath # Already a CSV
    else:
        raise ValueError(f"ยังไม่รองรับไฟล์นามสกุล: {ext}")

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
            QMessageBox.information(parent_widget, "Success", f"แปลงไฟล์ {os.path.basename(filepath)} สำเร็จ!\nได้ทั้งหมด {row_count} บรรทัด")
            
        return tstudio_csv
        
    except subprocess.CalledProcessError as e:
        if parent_widget:
            QMessageBox.critical(parent_widget, "pylocres Error", f"Command failed with exit status {e.returncode}")
        raise e
    except Exception as e:
        if parent_widget:
            QMessageBox.critical(parent_widget, "Error", f"ไม่สามารถแปลงไฟล์ได้:\n{str(e)}")
        raise e
    finally:
        # Clean up temporary dump file
        if os.path.exists(pylocres_csv):
            try:
                os.remove(pylocres_csv)
            except:
                pass
