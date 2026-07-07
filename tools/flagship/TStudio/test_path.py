import os
import sys

current_dir = r"E:\Mod_Workspace\Modder_project\modder-hub\tools\flagship\TStudio"
BASE_DIR = os.path.dirname(os.path.dirname(current_dir))
CUSTOM_PARSERS_DIR = os.path.join(BASE_DIR, "TStudio", "CustomParsers")
print(f"CUSTOM_PARSERS_DIR: {CUSTOM_PARSERS_DIR}")
