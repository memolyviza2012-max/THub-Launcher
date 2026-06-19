import sys
import re

file_path = r'E:\Mod_Workspace\Tool\2_Studio_translation\Translation_Studio_Template.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace specific GOTG strings
content = content.replace('PROJECT CONFIGURATION - GOTG SPECIFIC', 'PROJECT CONFIGURATION')
content = content.replace('- Star-Lord / Peter Quill = สตาร์-ลอร์ด / ปีเตอร์ ควิลล์', '- Character A = Name A')
content = content.replace(r'retail_path = r"F:\Epic Games\MarvelGOTG\retail\strings_th.json"', 'retail_path = r"C:\\path\\to\\your\\game\\strings_th.json"')
content = content.replace('# Save as utf-8-sig as required by GOTG', '# Save as utf-8-sig if required by the game engine')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Template fully generalized.")
