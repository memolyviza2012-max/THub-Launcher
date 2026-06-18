# Thub - Cloud Launcher and Modding Tools
# Copyright (C) 2026 Danaiwit Kanthawong (NodNuatTranslator)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import re

path = 'E:/Mod_Workspace/Modder_project/modder-hub/tools/TStudio/tstudio_app.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

fixes = [
    (r'setPlaceholderText\(.*?Search...\)', r"setPlaceholderText('🔍 Search...')"),
    (r"QPushButton\('.*?Find/Replace'\)", r"QPushButton('🔍 Find/Replace')"),
    (r"addItems\(\['All Rows', '.*?Missing', '.*?Translated', '.*?AI Hallucinations', '.*?Quotes/Idioms'\]\)", 
     r"addItems(['All Rows', '🔴 Missing', '🟢 Translated', '👽 AI Hallucinations', '💬 Quotes/Idioms'])"),
    (r"QPushButton\('.*?Glossary'\)", r"QPushButton('📖 Glossary')"),
    (r"QPushButton\('.*?Settings'\)", r"QPushButton('⚙️ Settings')"),
    (r"QPushButton\('.*?Save CSV \(Ctrl\+S\)'\)", r"QPushButton('💾 Save CSV (Ctrl+S)')"),
    (r"QPushButton\('.*?Deploy to Game'\)", r"QPushButton('🚀 Deploy to Game')"),
    (r"QGroupBox\(\".*?1\. Original Source\"\)", r'QGroupBox("🇬🇧 1. Original Source")'),
    (r"QGroupBox\(\".*?2\. AI Translation \(Reference\)\"\)", r'QGroupBox("🤖 2. AI Translation (Reference)")'),
    (r"QGroupBox\(\".*?3\. My Translation \(Edit Here\)\"\)", r'QGroupBox("✍️ 3. My Translation (Edit Here)")'),
    (r"QPushButton\('.*?AI Prompts'\)", r"QPushButton('⚙️ AI Prompts')"),
    (r"QPushButton\('.*?Re-translate \(3 Options\)'\)", r"QPushButton('🎯 Re-translate (3 Options)')"),
    (r"QPushButton\('.*?Re-translate \(Local AI\)'\)", r"QPushButton('🖥️ Re-translate (Local AI)')"),
    (r"QPushButton\('.*?Re-translate \(DeepSeek\)'\)", r"QPushButton('🤖 Re-translate (DeepSeek)')"),
    (r"QPushButton\('.*?\.\.\.'\)", r"QPushButton('✨ แปลพิเศษ...')"),
    (r"menu\.addMenu\(\".*?DeepSeek AI\"\)", r'menu.addMenu("🧠 DeepSeek AI")'),
    (r"addAction\(\".*? \(Idiom\)\"\)", r'addAction("แปลเป็น วลี/สำนวน (Idiom)")'),
    (r"addAction\(\".*? \(Poem\)\"\)", r'addAction("แปลเป็น กลอน (Poem)")'),
    (r"addAction\(\".*? \(Quote\)\"\)", r'addAction("แปลเป็น คำพูดบุคคลสำคัญ (Quote)")'),
    (r"menu\.addMenu\(\".*?Local LLM\"\)", r'menu.addMenu("💻 Local LLM")'),
    (r"QPushButton\('.*? \(AI\)'\)", r"QPushButton('🤔 เดาคนพูด (AI)')"),
    (r"addAction\(\".*? DeepSeek\"\)", r'addAction("🧠 เดาด้วย DeepSeek")'),
    (r"addAction\(\".*? Local LLM\"\)", r'addAction("💻 เดาด้วย Local LLM")'),
    (r"setWindowTitle\(f'Translation Studio .*? \{GAME_NAME\}'\)", r"setWindowTitle(f'Translation Studio — {GAME_NAME}')"),
    
    # Also fix settings and other dialogs
    (r"setWindowTitle\(\".*?Settings \(API & Model\)\"\)", r'setWindowTitle("⚙️ Settings (API & Model)")'),
    (r"QPushButton\(\".*?Save Settings\"\)", r'QPushButton("💾 Save Settings")'),
    (r"setWindowTitle\(\".*?Prompt Settings \(.*?\)\"\)", r'setWindowTitle("⚙️ Prompt Settings (ตั้งค่าบุคลิก AI)")'),
    (r"QPushButton\(\".*?Save Prompts\"\)", r'QPushButton("💾 Save Prompts")'),
    (r"setWindowTitle\(\".*?Glossary Editor \(.*?\)\"\)", r'setWindowTitle("📖 Glossary Editor (คำศัพท์บังคับ)")'),
    (r"setHorizontalHeaderLabels\(\[\"Wrong Word \(.*?\)\", \"Correct Word \(.*?\)\"\]\)", r'setHorizontalHeaderLabels(["Wrong Word (คำผิด)", "Correct Word (คำถูก)"])'),
    (r"QPushButton\(\".*?Add Row\"\)", r'QPushButton("➕ Add Row")'),
    (r"QPushButton\(\".*?Delete Row\"\)", r'QPushButton("🗑️ Delete Row")'),
    (r"QPushButton\(\".*?Save Glossary\"\)", r'QPushButton("💾 Save Glossary")'),
    (r"setWindowTitle\(\".*?Find & Replace\"\)", r'setWindowTitle("🔍 Find & Replace")'),
    (r"setWindowTitle\(\".*?Select Translation Style\"\)", r'setWindowTitle("🎯 Select Translation Style")'),
    (r"addWidget\(QLabel\(\".*?:\"\)\)", r'addWidget(QLabel("เลือกสไตล์คำแปลที่ต้องการ:"))'),
    (r"labels = \[\".*?Literal\)\", \".*?Casual\)\", \".*?Formal\)\"\]", r'labels = ["1️⃣ ตรงตัว (Literal)", "2️⃣ ภาษาพูด/สแลง (Casual)", "3️⃣ สุภาพ/ทางการ (Formal)"]'),
    (r"QPushButton\(\".*?Use Selected\"\)", r'QPushButton("✅ Use Selected")'),
    
    # Status bar messages
    (r"showMessage\('Ready .*? CSV\.'\)", r"showMessage('Ready — Configure PROJECT CONFIGURATION then load CSV.')"),
    (r"showMessage\('.*?CSV_PATH .*?'\)", r"showMessage('⚠️ กรุณาตั้งค่า CSV_PATH ใน PROJECT CONFIGURATION ก่อนใช้งาน')")
]

for pat, repl in fixes:
    content = re.sub(pat, repl, content)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

with open('E:/Mod_Workspace/Tool/2_Studio_translation/TStudio_Template.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Regex fixes applied.")
