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

import sys

path = 'E:/Mod_Workspace/Modder_project/modder-hub/tools/TStudio/tstudio_app.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find where retranslate_local starts
idx = content.find('    def retranslate_local(self):')
if idx == -1:
    sys.exit('retranslate_local not found')

clean_code = content[:idx] + r'''    def retranslate_local(self):
        if self.current_source_row < 0: return
        item = self.model._data[self.current_source_row]
        if not item["source"].strip(): return
        _, _, local_url = self._load_api_config()
        if not local_url:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Error", "Please set Local API URL in Settings first!")
            return
        if not local_url.endswith("/completions"):
            if local_url.endswith("/"):
                local_url += "v1/chat/completions"
            else:
                local_url += "/v1/chat/completions"
                
        self.statusBar().showMessage("Translating with Local AI...")
        from PyQt6.QtWidgets import QApplication, QMessageBox
        import requests
        import re
        QApplication.processEvents()
        source_text = item["source"].replace('\\n', '\n')
        
        s_prompt, _ = load_current_prompts()
        prompt = s_prompt.replace('{id}', item["id"]).replace('{source_text}', source_text)

        try:
            res = requests.post(local_url,
                json={"model": "local-model", "messages": [{"role": "user", "content": prompt}], "temperature": 0.3, "max_tokens": 1000},
                headers={"Content-Type": "application/json"}, timeout=120)
            if res.status_code == 200:
                translated = self._apply_glossary(re.sub(r'^"|"$', '', res.json()['choices'][0]['message']['content'].strip()))
                self.txt_trans.setPlainText(translated)
                self.statusBar().showMessage("Re-translated with Local AI!", 3000)
            else:
                QMessageBox.warning(self, "API Error", f"Code {res.status_code}\\n{res.text}")
        except Exception as e:
            QMessageBox.critical(self, "Failed", f"Is your Local LLM running at {local_url}?\\n\\nError: {e}")

    def save_csv(self):
        from PyQt6.QtWidgets import QMessageBox
        if not self.csv_path:
            QMessageBox.warning(self, "Error", "CSV_PATH is not set in project config.")
            return
        try:
            import csv
            with open(self.csv_path, 'w', encoding=self.csv_encoding, newline='') as f:
                writer = csv.writer(f)
                if hasattr(self.model, 'headers_row') and self.model.headers_row:
                    writer.writerow(self.model.headers_row)
                    headers_len = len(self.model.headers_row)
                else:
                    headers_len = max(COL_ID, COL_SOURCE, COL_TRANS, COL_AI_REF) + 1
                    
                for item in self.model._data:
                    row = [""] * headers_len
                    if COL_ID < headers_len: row[COL_ID] = item["id"]
                    if COL_SOURCE < headers_len: row[COL_SOURCE] = item["source"]
                    if COL_TRANS < headers_len: row[COL_TRANS] = item["trans"]
                    if COL_AI_REF < headers_len: row[COL_AI_REF] = item["ai_ref"]
                    writer.writerow(row)
            self.statusBar().showMessage('CSV Saved Successfully!', 3000)
            QMessageBox.information(self, "Success", "Saved CSV successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save CSV: {e}")

    def deploy_to_game(self):
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Deploy to Game", "ระบบ Deploy ไปยังตัวเกมกำลังอยู่ในระหว่างการพัฒนาครับ!")

    def guess_speaker(self, is_local=False):
        if self.current_source_row < 0: return
        item = self.model._data[self.current_source_row]
        if not item["source"].strip(): return
        
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Guess Speaker", "ฟีเจอร์คาดเดาผู้พูด (Guess Speaker) กำลังอยู่ในระหว่างการเชื่อมต่อ API เชิงลึกครับ!")

if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = TranslationStudio()
    window.show()
    sys.exit(app.exec())
'''

with open(path, 'w', encoding='utf-8') as f:
    f.write(clean_code)

path2 = 'E:/Mod_Workspace/Tool/2_Studio_translation/TStudio_Template.py'
with open(path2, 'w', encoding='utf-8') as f:
    f.write(clean_code)

print("Files fixed successfully!")
