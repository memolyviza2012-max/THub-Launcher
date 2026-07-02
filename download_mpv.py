import urllib.request
import py7zr
import os
import shutil

url = "https://ghproxy.net/https://github.com/shinchiro/mpv-winbuild-cmake/releases/download/20260610/mpv-dev-x86_64-20260610-git-304426c.7z"
archive_path = "mpv_dev.7z"
target_dir = r"E:\Mod_Workspace\Modder_project\modder-hub\tools\flagship\TVox"

print(f"Downloading MPV Engine from {url}...")
urllib.request.urlretrieve(url, archive_path)

print("Extracting...")
with py7zr.SevenZipFile(archive_path, mode='r') as z:
    for name in z.getnames():
        if "libmpv-2.dll" in name:
            print(f"Extracting {name}...")
            z.extract(targets=[name], path=".")
            # Move it to target directory
            extracted_path = name
            target_path = os.path.join(target_dir, "libmpv-2.dll")
            if os.path.exists(target_path):
                os.remove(target_path)
            shutil.move(extracted_path, target_path)
            print(f"Successfully placed libmpv-2.dll in {target_dir}")
            break

# Cleanup
try:
    os.remove(archive_path)
    if os.path.exists('mpv-dev-x86_64-20260610-git-304426c'):
        shutil.rmtree('mpv-dev-x86_64-20260610-git-304426c', ignore_errors=True)
except Exception as e:
    print(f"Cleanup error: {e}")

print("Done.")
