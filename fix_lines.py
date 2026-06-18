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

path = 'E:/Mod_Workspace/Modder_project/modder-hub/tools/TStudio/tstudio_app.py'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

def set_line(num, text):
    lines[num-1] = text + '\n'

set_line(26, r'# ╔═════════════════════════════════════════════════════════════════╗')
set_line(27, r'# ║           PROJECT CONFIGURATION — GOTG SPECIFIC                 ║')
set_line(28, r'# ╚═════════════════════════════════════════════════════════════════╝')
set_line(51, r'# ═════════════════════════════════════════════════════════════════')
set_line(61, r'# - Gamora = กาโมร่า')
set_line(62, r'# - Drax = แดร็กซ์')
set_line(63, r'# - Rocket = ร็อคเก็ต')
set_line(64, r'# - Groot = กรู๊ท')
set_line(65, r'# - Mantis = แมนทิส')
set_line(66, r'# - Milano = ยานมิลาโน่')
set_line(67, r'# - Nova Corps = โนวาคอร์ปส')
set_line(68, r'# - Lady Hellbender = เลดี้เฮลเบนเดอร์')
set_line(69, r'# - Knowhere = โนว์แวร์')
set_line(70, r'# - Cosmo = คอสโม่')
set_line(71, r'# - Universal Church of Truth = คริสตจักรแห่งสัจธรรมสากล')
set_line(72, r'# - Grand Unifier Raker = แกรนด์ยูนิฟายเออร์เรกเกอร์')
set_line(73, r'# - Worldmind = เวิลด์มายด์')
set_line(74, r'# - Flark = ฟลาร์ก')
set_line(75, r'# - Scut = สคัท')
set_line(81, r'# 1. Literal/Direct (แปลตรงตัว)')
set_line(82, r'# 2. Casual/Slang (ภาษาพูด/สแลง)')
set_line(83, r'# 3. Polite/Formal (สุภาพ/ทางการ)')
set_line(88, r'# - Gamora = กาโมร่า')
set_line(89, r'# - Drax = แดร็กซ์')
set_line(90, r'# - Rocket = ร็อคเก็ต')
set_line(91, r'# - Groot = กรู๊ท')
set_line(92, r'# - Mantis = แมนทิส')
set_line(93, r'# - Milano = ยานมิลาโน่')
set_line(94, r'# - Nova Corps = โนวาคอร์ปส')
set_line(95, r'# - Lady Hellbender = เลดี้เฮลเบนเดอร์')
set_line(96, r'# - Knowhere = โนว์แวร์')
set_line(97, r'# - Cosmo = คอสโม่')
set_line(98, r'# - Universal Church of Truth = คริสตจักรแห่งสัจธรรมสากล')
set_line(99, r'# - Grand Unifier Raker = แกรนด์ยูนิฟายเออร์เรกเกอร์')
set_line(100, r'# - Worldmind = เวิลด์มายด์')
set_line(101, r'# - Flark = ฟลาร์ก')
set_line(102, r'# - Scut = สคัท')
set_line(147, r'        self.setWindowTitle("⚙️ Settings (API & Model)")')
set_line(157, r'        btn_save = QPushButton("💾 Save Settings")')
set_line(190, r'        self.setWindowTitle("⚙️ Prompt Settings (ตั้งค่าบุคลิก AI)")')
set_line(222, r'        btn_save = QPushButton("💾 Save Prompts")')
set_line(275, r'        self.setWindowTitle("📖 Glossary Editor (คำศัพท์บังคับ)")')
set_line(279, r'        self.table.setHorizontalHeaderLabels(["Wrong Word (คำผิด)", "Correct Word (คำถูก)"])')
set_line(283, r'        btn_add = QPushButton("➕ Add Row")')
set_line(285, r'        btn_del = QPushButton("🗑️ Delete Row")')
set_line(287, r'        btn_save = QPushButton("💾 Save Glossary")')
set_line(334, r'        self.setWindowTitle("🔍 Find & Replace")')
set_line(375, r'        self.setWindowTitle("🎯 Select Translation Style")')
set_line(379, r'        layout.addWidget(QLabel("เลือกสไตล์คำแปลที่ต้องการ:"))')
set_line(385, r'        labels = ["1️⃣ ตรงตัว (Literal)", "2️⃣ ภาษาพูด/สแลง (Casual)", "3️⃣ สุภาพ/ทางการ (Formal)"]')
set_line(397, r'        btn_ok = QPushButton("✅ Use Selected")')
set_line(498, r'            has_quote = bool(re.search(r\'["“”][^"“”]+["“”]\', src))')
set_line(516, r'        self.setWindowTitle(f\'Translation Studio — {GAME_NAME}\')')
set_line(533, r'        # ── Top Bar ──')
set_line(536, r"        self.search_input.setPlaceholderText('🔍 Search...')")
set_line(543, r"        btn_fr = QPushButton('🔍 Find/Replace')")
set_line(548, r"        self.filter_combo.addItems(['All Rows', '🔴 Missing', '🟢 Translated', '👽 AI Hallucinations', '💬 Quotes/Idioms'])")
set_line(553, r"        btn_glos = QPushButton('📖 Glossary')")
set_line(557, r"        btn_set = QPushButton('⚙️ Settings')")
set_line(561, r"        btn_save = QPushButton('💾 Save CSV (Ctrl+S)')")
set_line(566, r'        # ── NEW: Deploy Button ──')
set_line(567, r"        btn_deploy = QPushButton('🚀 Deploy to Game')")
set_line(575, r'        # ── Splitter ──')
set_line(592, r'        # ── Right Panel ──')
set_line(597, r'        grp1 = QGroupBox("🇬🇧 1. Original Source")')
set_line(605, r'        grp2 = QGroupBox("🤖 2. AI Translation (Reference)")')
set_line(613, r'        grp3 = QGroupBox("✍️ 3. My Translation (Edit Here)")')
set_line(616, r"        btn_prompts = QPushButton('⚙️ AI Prompts')")
set_line(622, r"        btn_opt = QPushButton('🎯 Re-translate (3 Options)')")
set_line(627, r"        btn_local = QPushButton('🖥️ Re-translate (Local AI)')")
set_line(632, r"        btn_re = QPushButton('🤖 Re-translate (DeepSeek)')")
set_line(637, r"        btn_special = QPushButton('✨ แปลพิเศษ...')")
set_line(641, r'        deepseek_menu = menu.addMenu("🧠 DeepSeek AI")')
set_line(642, r'        action_idiom_ds = deepseek_menu.addAction("แปลเป็น วลี/สำนวน (Idiom)")')
set_line(643, r'        action_poem_ds = deepseek_menu.addAction("แปลเป็น กลอน (Poem)")')
set_line(644, r'        action_quote_ds = deepseek_menu.addAction("แปลเป็น คำพูดบุคคลสำคัญ (Quote)")')
set_line(650, r'        local_menu = menu.addMenu("💻 Local LLM")')
set_line(651, r'        action_idiom_loc = local_menu.addAction("แปลเป็น วลี/สำนวน (Idiom)")')
set_line(652, r'        action_poem_loc = local_menu.addAction("แปลเป็น กลอน (Poem)")')
set_line(653, r'        action_quote_loc = local_menu.addAction("แปลเป็น คำพูดบุคคลสำคัญ (Quote)")')
set_line(662, r"        btn_guess = QPushButton('🤔 เดาคนพูด (AI)')")
set_line(665, r'        action_guess_ds = guess_menu.addAction("🧠 เดาด้วย DeepSeek")')
set_line(667, r'        action_guess_loc = guess_menu.addAction("💻 เดาด้วย Local LLM")')
set_line(684, r"        self.statusBar().showMessage('Ready — Configure PROJECT CONFIGURATION then load CSV.')")
set_line(699, r"        self.statusBar().showMessage('⚠️ กรุณาตั้งค่า CSV_PATH ใน PROJECT CONFIGURATION ก่อนใช้งาน')")
set_line(702, r"        self.setWindowTitle(f'Translation Studio — {GAME_NAME}')")
set_line(793, r'            mode_text = "Analyze the underlying meaning of this phrase carefully. It is likely an idiom or metaphor. Translate it into a natural-sounding, contextually appropriate Thai idiom or phrase (วลี/สำนวน), rather than a literal word-for-word translation."')
set_line(795, r'            mode_text = "This text is a poem, song, or rhythmic chant. Translate it into an elegant Thai poetic form (กลอน/คำคล้องจอง) with appropriate rhyming and literary vocabulary, while preserving the original meaning."')
set_line(797, r'            mode_text = "This text is a profound quote or proverb. Translate it into formal, philosophical, and impactful Thai language (คำคม/คำพูดบุคคลสำคัญ), similar to how a famous historical figure would speak."')

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

with open('E:/Mod_Workspace/Tool/2_Studio_translation/TStudio_Template.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Line-based fixes applied.")
