import sys

file_path = r'E:\Mod_Workspace\Tool\2_Studio_translation\Translation_Studio_Template.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('GOTG_Translation_Studio_V2.py', 'Translation_Studio_Template.py')
content = content.replace('GAME_NAME    = "Marvel\'s Guardians of the Galaxy"', 'GAME_NAME    = "Your_Game_Name_Here"')
content = content.replace('"gotg_translation.csv"', '"translation.csv"')
content = content.replace('Universal Translation Studio for Marvel\'s Guardians of the Galaxy', 'Universal Translation Studio Template')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Template variables generalized.")
