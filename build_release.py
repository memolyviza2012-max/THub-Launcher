import os
import zipfile
import shutil

def zipdir(path, ziph, arc_prefix=""):
    for root, dirs, files in os.walk(path):
        for file in files:
            filepath = os.path.join(root, file)
            # Create a path relative to the target directory (e.g., THub folder)
            rel_path = os.path.relpath(filepath, path)
            # Prefix with arc_prefix to keep the root folder name in zip
            arcname = os.path.join(arc_prefix, rel_path)
            ziph.write(filepath, arcname)

if not os.path.exists('Releases'):
    os.makedirs('Releases')

source_dir = os.path.join('dist', 'THub')
output_zip = os.path.join('Releases', 'THub_1.1.0.zip')

print(f"Creating {output_zip} from {source_dir}...")
if not os.path.exists(source_dir):
    print(f"Error: {source_dir} does not exist. Please run PyInstaller first.")
else:
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipdir(source_dir, zipf, arc_prefix="THub")
    print(f"Successfully created {output_zip}")
