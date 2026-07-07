import json
import os

locales_dir = r"E:\Mod_Workspace\Modder_project\modder-hub\tools\flagship\TRun\locales"

translations = {
    "en": {
        "btn_file_add": "📄 Add File(s)",
        "btn_folder_add": "📁 Add Folder...",
        "btn_remove_sel": "🗑️ Remove Selected",
        "btn_clear_all": "🧹 Clear All",
        "lbl_file_path": "📂 File Path",
        "lbl_profile": "⚙️ Profile"
    },
    "th": {
        "btn_file_add": "📄 เพิ่มไฟล์",
        "btn_folder_add": "📁 เพิ่มโฟลเดอร์...",
        "btn_remove_sel": "🗑️ ลบที่เลือก",
        "btn_clear_all": "🧹 ล้างทั้งหมด",
        "lbl_file_path": "📂 เส้นทางไฟล์",
        "lbl_profile": "⚙️ โปรไฟล์"
    },
    "ja": {
        "btn_file_add": "📄 ファイル追加",
        "btn_folder_add": "📁 フォルダ追加...",
        "btn_remove_sel": "🗑️ 選択削除",
        "btn_clear_all": "🧹 すべてクリア",
        "lbl_file_path": "📂 ファイルパス",
        "lbl_profile": "⚙️ プロファイル"
    },
    "zh": {
        "btn_file_add": "📄 添加文件",
        "btn_folder_add": "📁 添加文件夹...",
        "btn_remove_sel": "🗑️ 删除所选",
        "btn_clear_all": "🧹 清除全部",
        "lbl_file_path": "📂 文件路径",
        "lbl_profile": "⚙️ 配置文件"
    },
    "ru": {
        "btn_file_add": "📄 Добавить файл(ы)",
        "btn_folder_add": "📁 Добавить папку...",
        "btn_remove_sel": "🗑️ Удалить выбранное",
        "btn_clear_all": "🧹 Очистить всё",
        "lbl_file_path": "📂 Путь к файлу",
        "lbl_profile": "⚙️ Профиль"
    }
}

for lang, data in translations.items():
    file_path = os.path.join(locales_dir, f"{lang}.json")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            j = json.load(f)
        
        for k, v in data.items():
            j[k] = v
            
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(j, f, ensure_ascii=False, indent=4)
        print(f"Updated {lang}.json")
    else:
        print(f"File {file_path} not found.")
