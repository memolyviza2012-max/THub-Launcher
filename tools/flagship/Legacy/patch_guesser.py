import sys
import re

file_path = r'E:\Mod_Workspace\Tool\2_Studio_translation\TStudio_Template.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Insert the new button in UI
ui_target = '''        btn_special.setMenu(menu)
        btn_row.addWidget(btn_special)'''

new_button = '''        btn_special.setMenu(menu)
        btn_row.addWidget(btn_special)
        
        btn_guess = QPushButton('🤔 เดาคนพูด (AI)')
        btn_guess.setStyleSheet("background:#f38ba8; color:#1e1e2e; font-size:12px; padding:4px 8px; font-weight:bold;")
        guess_menu = QMenu(self)
        action_guess_ds = guess_menu.addAction("🧠 เดาด้วย DeepSeek")
        action_guess_ds.triggered.connect(lambda: self.guess_speaker(False))
        action_guess_loc = guess_menu.addAction("💻 เดาด้วย Local LLM")
        action_guess_loc.triggered.connect(lambda: self.guess_speaker(True))
        btn_guess.setMenu(guess_menu)
        btn_row.addWidget(btn_guess)'''

content = content.replace(ui_target, new_button)

# 2. Add the guess_speaker method
guess_method = '''
    def guess_speaker(self, use_local):
        if self.current_source_row < 0: return
        
        api_key, model = self._load_api_config()
        if not use_local and not api_key:
            QMessageBox.warning(self, "API Key Missing", "Please set DeepSeek API Key in Settings first.")
            return
            
        local_url = self.config.get("local_url", "http://localhost:11434")
        if use_local and not local_url:
            QMessageBox.warning(self, "API URL Missing", "Please set Local API URL in Settings first.")
            return

        # Get context (3 lines before, 3 lines after)
        idx = self.current_source_row
        data = self.model._data
        
        context_str = ""
        for i in range(max(0, idx - 3), idx):
            context_str += f"Line {- (idx - i)}: {data[i]['source']}\\n"
            
        context_str += f"TARGET SENTENCE: {data[idx]['source']}\\n"
        
        for i in range(idx + 1, min(len(data), idx + 4)):
            context_str += f"Line +{i - idx}: {data[i]['source']}\\n"
            
        prompt = f"You are an expert game script analyst for '{GAME_NAME}'.\\nRead the following sequence of dialogues and deduce who is speaking the TARGET SENTENCE. Also guess who they are speaking to.\\n\\nContext:\\n{context_str}\\n\\nWho is speaking the TARGET SENTENCE? Answer with the character's name and a very brief 1-sentence reasoning."
        
        msg = QMessageBox(self)
        msg.setWindowTitle("AI Thinking...")
        msg.setText("กำลังวิเคราะห์บริบทแวดล้อม โปรดรอสักครู่...")
        msg.setStandardButtons(QMessageBox.StandardButton.NoButton)
        msg.show()
        QApplication.processEvents()

        try:
            if not use_local:
                import requests
                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                payload = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": "Analyze the speaker."}
                    ],
                    "temperature": 0.3
                }
                res = requests.post("https://api.deepseek.com/chat/completions", json=payload, headers=headers, timeout=30)
                if res.status_code == 200:
                    answer = res.json()['choices'][0]['message']['content'].strip()
                else:
                    answer = f"Error {res.status_code}: {res.text}"
            else:
                import requests
                payload = {
                    "model": self.config.get("local_model", "llama3"),
                    "messages": [
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": "Analyze the speaker."}
                    ],
                    "stream": False,
                    "temperature": 0.3
                }
                res = requests.post(f"{local_url.rstrip('/')}/api/chat", json=payload, headers={"Content-Type": "application/json"}, timeout=60)
                if res.status_code == 200:
                    answer = res.json()['message']['content'].strip()
                else:
                    answer = f"Error {res.status_code}: {res.text}"
                    
            msg.accept()
            
            # Show result
            res_msg = QMessageBox(self)
            res_msg.setWindowTitle("ผลวิเคราะห์คนพูด (Speaker Analysis)")
            res_msg.setText(f"ประโยค: {data[idx]['source']}\\n\\n{answer}")
            res_msg.exec()
            
        except Exception as e:
            msg.accept()
            QMessageBox.critical(self, "Failed", f"Error: {e}")
'''

content = content.replace('    def save_csv(self):', guess_method + '\n    def save_csv(self):')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Added AI Speaker Guesser feature to Template.")
