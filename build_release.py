import os
import zipfile

def is_excluded(path):
    exclusions = [
        '.git', '__pycache__', '.vscode', 'temp', 'Releases', 'THub_1.0.9.zip',
        'build_release.py', '.bak', 'scratch', 'recovered'
    ]
    basename = os.path.basename(path)
    # Exclude files by extension
    for ext in ['.patch', '.qml', '.psd', '.bat', '.bak']:
        if basename.endswith(ext): return True
        
    # Exclude standalone patch scripts, tests, and debug scripts
    if basename.startswith('patch_') and basename.endswith('.py'): return True
    if basename.startswith('test_') and basename.endswith('.py'): return True
    if basename.startswith('scratch_'): return True
    
    # Exclude directory matches
    for ex in exclusions:
        if ex in path.split(os.sep) or ex in basename:
            return True
            
    return False

def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        # Filter directories in-place to avoid traversing them
        dirs[:] = [d for d in dirs if not is_excluded(os.path.join(root, d))]
        for file in files:
            filepath = os.path.join(root, file)
            if not is_excluded(filepath):
                arcname = os.path.relpath(filepath, path)
                ziph.write(filepath, arcname)

if not os.path.exists('Releases'):
    os.makedirs('Releases')

output_zip = os.path.join('Releases', 'THub_1.0.9.zip')
print(f"Creating {output_zip}...")
with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
    zipdir('.', zipf)
print(f"Successfully created {output_zip}")
