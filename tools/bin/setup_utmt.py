import os
import urllib.request
import json
import zipfile
import shutil

BIN_DIR = os.path.dirname(os.path.abspath(__file__))
UTMT_DIR = os.path.join(BIN_DIR, "UTMT")
CLI_EXE = os.path.join(UTMT_DIR, "UndertaleModCli.exe")

def install_utmt(progress_callback=None):
    if os.path.exists(CLI_EXE):
        if progress_callback: progress_callback("UTMT already installed.")
        return True

    if not os.path.exists(UTMT_DIR):
        os.makedirs(UTMT_DIR)

    api_url = "https://api.github.com/repos/UnderminersTeam/UndertaleModTool/releases/latest"
    if progress_callback: progress_callback("Fetching UTMT latest release info...")
    
    try:
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            
        zip_url = None
        for asset in data.get('assets', []):
            if asset['name'].endswith('.zip') and 'CLI' in asset['name'] and 'Windows' in asset['name']:
                zip_url = asset['browser_download_url']
                break
        
        # Fallback if GUI not found
        if not zip_url:
            for asset in data.get('assets', []):
                if asset['name'].endswith('.zip'):
                    zip_url = asset['browser_download_url']
                    break
        
        if not zip_url:
            raise Exception("Could not find UTMT zip release.")
            
        zip_path = os.path.join(BIN_DIR, "utmt_temp.zip")
        if progress_callback: progress_callback(f"Downloading {zip_url}...")
        
        def reporthook(blocknum, blocksize, totalsize):
            if progress_callback and totalsize > 0:
                percent = int(blocknum * blocksize * 100 / totalsize)
                if percent % 10 == 0:
                    progress_callback(f"Downloading... {min(percent, 100)}%")

        urllib.request.urlretrieve(zip_url, zip_path, reporthook)
        
        if progress_callback: progress_callback("Extracting UTMT...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(UTMT_DIR)
            
        # Clean up
        os.remove(zip_path)
        
        # Verify
        if os.path.exists(CLI_EXE):
            if progress_callback: progress_callback("UTMT installed successfully.")
            return True
        else:
            raise Exception(f"Extraction failed to produce {CLI_EXE}")
            
    except Exception as e:
        if progress_callback: progress_callback(f"Error installing UTMT: {str(e)}")
        return False

if __name__ == "__main__":
    def print_cb(msg):
        print(msg)
    install_utmt(print_cb)
