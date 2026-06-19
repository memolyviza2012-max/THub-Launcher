import os
import sys
import urllib.request
import zipfile
import shutil
import subprocess
from PyQt6.QtWidgets import QMessageBox, QProgressDialog
from PyQt6.QtCore import Qt

def get_ffmpeg_path():
    """Returns the path to ffmpeg.exe if available, else None."""
    # 1. Check tools/bin
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        # We are in tools/flagship/Core or TVox, so base project is 3 levels up from Core?
        # Core is in modder-hub/tools/flagship/Core
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    
    local_ffmpeg = os.path.join(base_dir, "tools", "bin", "ffmpeg.exe")
    if os.path.exists(local_ffmpeg):
        return local_ffmpeg

    # 2. Check system PATH
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return "ffmpeg"
    except FileNotFoundError:
        pass
    
    return None

def ensure_ffmpeg(parent_widget):
    """Ensures FFmpeg is available. If not, prompts user to download it."""
    path = get_ffmpeg_path()
    if path:
        return path
        
    reply = QMessageBox.question(
        parent_widget,
        "FFmpeg Required",
        "ระบบต้องใช้โปรแกรม FFmpeg ในการสร้างคลื่นเสียงและระบบ AI แกะซับ\n\nต้องการให้ระบบดาวน์โหลดและติดตั้งให้โดยอัตโนมัติหรือไม่? (ขนาดประมาณ 30MB)",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    
    if reply != QMessageBox.StandardButton.Yes:
        return None
        
    # Proceed to download
    try:
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
            
        bin_dir = os.path.join(base_dir, "tools", "bin")
        os.makedirs(bin_dir, exist_ok=True)
        
        zip_path = os.path.join(bin_dir, "ffmpeg.zip")
        
        # Use Github API to get the fastest CDN link for GyanD's ffmpeg essentials build
        import json
        req = urllib.request.Request("https://api.github.com/repos/GyanD/codexffmpeg/releases/latest", headers={"User-Agent": "TVox-App"})
        url = None
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read())
                for asset in data.get("assets", []):
                    if "essentials_build.zip" in asset.get("name", ""):
                        url = asset["browser_download_url"]
                        break
        except Exception as e:
            print(f"Failed to fetch from github API: {e}")
            
        if not url:
            url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        
        progress = QProgressDialog("Downloading FFmpeg...", "Cancel", 0, 100, parent_widget)
        progress.setWindowTitle("Downloading")
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.show()
        
        def reporthook(blocknum, blocksize, totalsize):
            from PyQt6.QtCore import QCoreApplication
            QCoreApplication.processEvents()
            if progress.wasCanceled():
                raise Exception("Download cancelled")
            readsofar = blocknum * blocksize
            if totalsize > 0:
                percent = int((readsofar * 100) / totalsize)
                progress.setValue(percent)
                
        urllib.request.urlretrieve(url, zip_path, reporthook)
        progress.setLabelText("Extracting...")
        progress.setValue(0)
        
        # Extract ffmpeg.exe from the zip
        with zipfile.ZipFile(zip_path, 'r') as z:
            for file_info in z.infolist():
                if file_info.filename.endswith('bin/ffmpeg.exe'):
                    # Extract this specific file to bin_dir
                    source = z.open(file_info)
                    target_path = os.path.join(bin_dir, "ffmpeg.exe")
                    with open(target_path, "wb") as target:
                        shutil.copyfileobj(source, target)
                    break
                    
        # Cleanup
        if os.path.exists(zip_path):
            os.remove(zip_path)
            
        progress.setValue(100)
        QMessageBox.information(parent_widget, "Success", "ติดตั้ง FFmpeg เรียบร้อยแล้ว!")
        return os.path.join(bin_dir, "ffmpeg.exe")
        
    except Exception as e:
        QMessageBox.critical(parent_widget, "Download Failed", f"การดาวน์โหลดผิดพลาด:\n{e}")
        if os.path.exists(zip_path):
            try: os.remove(zip_path)
            except: pass
        return None