import re

with open("E:/Mod_Workspace/Modder_project/modder-hub/main.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update registry_data
old_registry = """        registry_data = [
            {"id": "TStudio", "name": "TStudio", "desc": "สุดยอดเครื่องมือแปลภาษาด้วย AI\\n(วิเคราะห์บริบท & แก้ไขแบบ Line-by-Line)\\nรองรับการทำงานกับไฟล์ Localization หลายรูปแบบ", "color": "#89b4fa", "exe": "tstudio_app.py", "icon": "assets/TStudio.png"},
            {"id": "TRun", "name": "TRun", "desc": "เครื่องมือแปลภาษาแบบ Batch อัตโนมัติ\\n(รองรับไฟล์ขนาดใหญ่และปริมาณมหาศาล)\\nแปลทั้งโปรเจกต์ได้อย่างรวดเร็วในคลิกเดียว", "color": "#a6e3a1", "exe": "trun_app.py", "icon": "assets/TRun.png"},
            {"id": "TPUA", "name": "TPUA", "desc": "เครื่องมือจัดการอักขระพิเศษภาษาไทย\\n(เข้ารหัส/ถอดรหัส PUA แบบ Drag & Drop)\\nแก้ปัญหาสระลอย/จม ในเอนจิ้นเกมต่างๆ", "color": "#cba6f7", "exe": "tpua_app.py", "icon": "assets/TPUA.png"},
            {"id": "TGlyph", "name": "TGlyph", "desc": "เครื่องมือสร้าง Texture ฟอนต์\\n(Generate Texture และแผนที่ตัวอักษร)\\nสำหรับดัดแปลงฟอนต์ Bitmap ในเกม", "color": "#fab387", "exe": "tglyph_app.py", "icon": "assets/TGlyph.png"},
            {"id": "TVox", "name": "TVox", "desc": "เครื่องมือจัดการ FMV และซับไตเติ้ล\\n(วิดีโอเพลเยอร์ & ดึงคลื่นเสียง Waveform)\\nออกแบบมาเพื่อการแปลวิดีโอคัทซีนโดยเฉพาะ", "color": "#f38ba8", "exe": "tvox_app.py", "icon": "assets/TVox.png"}
        ]"""

new_registry = """        registry_data = [
            {"id": "TStudio", "name": "TStudio", "desc": "สุดยอดเครื่องมือแปลภาษาด้วย AI\\n(วิเคราะห์บริบท & แก้ไขแบบ Line-by-Line)\\nรองรับการทำงานกับไฟล์ Localization หลายรูปแบบ", "color": "#89b4fa", "exe": "tstudio_app.py", "icon": "assets/TStudio.png"},
            {"id": "TRun", "name": "TRun", "desc": "เครื่องมือแปลภาษาแบบ Batch อัตโนมัติ\\n(รองรับไฟล์ขนาดใหญ่และปริมาณมหาศาล)\\nแปลทั้งโปรเจกต์ได้อย่างรวดเร็วในคลิกเดียว", "color": "#a6e3a1", "exe": "trun_app.py", "icon": "assets/TRun.png"},
            {"id": "TVox", "name": "TVox", "desc": "เครื่องมือจัดการ FMV และซับไตเติ้ล\\n(วิดีโอเพลเยอร์ & ดึงคลื่นเสียง Waveform)\\nออกแบบมาเพื่อการแปลวิดีโอคัทซีนโดยเฉพาะ", "color": "#f38ba8", "exe": "tvox_app.py", "icon": "assets/TVox.png"},
            {"id": "flagship.tfont", "folder": "TFont", "name": "TFont Generator", "desc": "เครื่องมือปรับแต่งและสร้างฟอนต์ PUA", "color": "#b4befe", "exe": "run_tfont.bat", "icon": "assets/TFONT.png", "no_project": True},
            {"id": "flagship.tpua", "folder": "TPUA", "name": "TPUA Text Converter", "desc": "เครื่องมือแปลงข้อความภาษาไทยเข้าสู่ระบบ PUA", "color": "#cba6f7", "exe": "run_tpua.bat", "icon": "assets/TPUA.png", "no_project": True},
            {"id": "TGlyph", "name": "TGlyph", "desc": "เครื่องมือสร้าง Texture ฟอนต์\\n(Generate Texture และแผนที่ตัวอักษร)\\nสำหรับดัดแปลงฟอนต์ Bitmap ในเกม", "color": "#fab387", "exe": "tglyph_app.py", "icon": "assets/TGlyph.png", "no_project": True}
        ]"""

content = content.replace(old_registry, new_registry)

# 2. Update exe_path
old_exe = '        exe_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "tools", "flagship", item["id"], item["exe"]))'
new_exe = '        folder_name = item.get("folder", item["id"])\n        exe_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "tools", "flagship", folder_name, item["exe"]))'
content = content.replace(old_exe, new_exe)

# 3. Conditionally render context
old_context = """        # Context Selector
        projects = self.config.get("projects", [])
        proj_names = [_("พ่วงโปรเจกต์: ไม่มี"), _("พ่วงโปรเจกต์: เลือกโฟลเดอร์...")] + [f"พ่วง: {p['name']}" for p in projects]
        context_var = ctk.StringVar(value=_("พ่วงโปรเจกต์: ไม่มี"))

        opt_context = ctk.CTkOptionMenu(action_frame, values=proj_names, variable=context_var, width=140, fg_color="#313244", button_color="#45475a")
        opt_context.pack(side="top", pady=(0, 10))"""

new_context = """        # Context Selector
        context_var = ctk.StringVar(value=_("พ่วงโปรเจกต์: ไม่มี"))
        if not item.get("no_project", False):
            projects = self.config.get("projects", [])
            proj_names = [_("พ่วงโปรเจกต์: ไม่มี"), _("พ่วงโปรเจกต์: เลือกโฟลเดอร์...")] + [f"{_('พ่วง:')} {p['name']}" for p in projects]

            opt_context = ctk.CTkOptionMenu(action_frame, values=proj_names, variable=context_var, width=140, fg_color="#313244", button_color="#45475a")
            opt_context.pack(side="top", pady=(0, 10))"""

content = content.replace(old_context, new_context)

# 4. Replace hardcoded "พ่วง: " in do_launch and fallback_launch
content = content.replace('pname = cval.replace(_("พ่วง: "), "")', 'pname = cval.replace(f"{_(\'พ่วง:\')} ", "")')

with open("E:/Mod_Workspace/Modder_project/modder-hub/main.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Patch successful!")
