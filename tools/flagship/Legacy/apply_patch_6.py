import sys
import re
import os
import shutil

source_file = r'E:\Mod_Workspace\Tool\2_Studio_translation\Translation_Studio_Template.py'
target_file = r'E:\Mod_Workspace\Tool\2_Studio_translation\TStudio_Template.py'

shutil.copy2(source_file, target_file)

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add resource_path helper function and QIcon import
content = content.replace('from PyQt6.QtGui import QColor, QKeySequence, QShortcut', 'from PyQt6.QtGui import QColor, QKeySequence, QShortcut, QIcon')

resource_path_func = '''
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
'''
content = content.replace('GAME_NAME    = "Your_Game_Name_Here"', resource_path_func + '\nGAME_NAME    = "Your_Game_Name_Here"')

# 2. Window Title & Icon
content = content.replace('self.setWindowTitle(f\'Translation Studio Template - {GAME_NAME}\')', 'self.setWindowIcon(QIcon(resource_path("TStudioLOGO.png")))\n        self.setWindowTitle(f\'TStudio_Template - {GAME_NAME}\')')

# 3. Add Credits Label
credits_label = '''
        lbl_credits = QLabel("พัฒนาโดย หน๊ด หนวด translator")
        lbl_credits.setStyleSheet("color: #a6adc8; font-size: 10px; font-style: italic;")
        lbl_credits.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(lbl_credits)
        
        widget = QWidget()
'''
content = content.replace('widget = QWidget()', credits_label)

# 4. Update deploy_to_game
old_deploy = '''    def deploy_to_game(self):
        retail_path = r"C:\\path\\to\\your\\game\\strings_th.json"
        
        reply = QMessageBox.question(self, "Deploy", f"Are you sure you want to deploy to:\\n{retail_path}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.save_csv()  # Save CSV first
            
            # Export to JSON dictionary for the game
            game_dict = {}
            for item in self.model._data:
                # Need to convert escaped \\n back to actual newlines for the game
                key = item["id"].replace('\\n', '\\n')
                trans = item["trans"].replace('\\n', '\\n')
                ai_ref = item["ai_ref"].replace('\\n', '\\n')
                source = item["source"].replace('\\n', '\\n')
                
                # Use human translation if available, else AI reference
                final_text = trans if trans.strip() else ai_ref
                
                # Fallback to original English if neither is available
                if not final_text.strip():
                    final_text = source
                    
                game_dict[key] = final_text
                
            try:
                # Save as utf-8-sig if required by the game engine
                tmp_file = retail_path + ".tmp"
                with open(tmp_file, 'w', encoding='utf-8-sig') as f:
                    json.dump(game_dict, f, ensure_ascii=False, indent=4)
                if os.path.exists(retail_path):
                    os.remove(retail_path)
                os.rename(tmp_file, retail_path)
                QMessageBox.information(self, "Success", f"Deployed successfully to {retail_path}!")
            except Exception as e:
                QMessageBox.critical(self, "Deploy Error", f"Failed to deploy: {e}")'''

new_deploy = '''    def deploy_to_game(self):
        retail_path = r"C:\\path\\to\\your\\game\\strings_th.json"
        
        target_path = retail_path
        if not os.path.exists(os.path.dirname(retail_path)):
            options = QFileDialog.Option.DontUseNativeDialog
            fileName, _ = QFileDialog.getSaveFileName(self, "หาโฟลเดอร์เกมไม่เจอ กรุณาเลือกที่เก็บไฟล์ JSON ด้วยตัวเอง", "strings_th.json", "JSON Files (*.json)", options=options)
            if not fileName:
                return
            target_path = fileName
            
        reply = QMessageBox.question(self, "Deploy", f"Are you sure you want to deploy to:\\n{target_path}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.save_csv()  # Save CSV first
            
            # Export to JSON dictionary for the game
            game_dict = {}
            for item in self.model._data:
                # Need to convert escaped \\n back to actual newlines for the game
                key = item["id"].replace('\\n', '\\n')
                trans = item["trans"].replace('\\n', '\\n')
                ai_ref = item["ai_ref"].replace('\\n', '\\n')
                source = item["source"].replace('\\n', '\\n')
                
                # Use human translation if available, else AI reference
                final_text = trans if trans.strip() else ai_ref
                
                # Fallback to original English if neither is available
                if not final_text.strip():
                    final_text = source
                    
                game_dict[key] = final_text
                
            try:
                # Save as utf-8-sig if required by the game engine
                tmp_file = target_path + ".tmp"
                with open(tmp_file, 'w', encoding='utf-8-sig') as f:
                    json.dump(game_dict, f, ensure_ascii=False, indent=4)
                if os.path.exists(target_path):
                    os.remove(target_path)
                os.rename(tmp_file, target_path)
                QMessageBox.information(self, "Success", f"Deployed successfully to {target_path}!")
            except Exception as e:
                QMessageBox.critical(self, "Deploy Error", f"Failed to deploy: {e}")'''

content = content.replace(old_deploy, new_deploy)

with open(target_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("Patch applied to TStudio_Template.py")
