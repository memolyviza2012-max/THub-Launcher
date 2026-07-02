import os
base = r'E:\Mod_Workspace\Modder_project\modder-hub\tools\flagship'
for root, dirs, files in os.walk(base):
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
            if 'f_("' in content or "f_('" in content:
                content = content.replace('f_("', '_("')
                content = content.replace("f_('", "_('")
                with open(path, 'w', encoding='utf-8') as file:
                    file.write(content)
                print(f'Fixed f_ in {f}')
