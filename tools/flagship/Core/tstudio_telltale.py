import os
import subprocess
import shutil
import tempfile
import csv
import json

class TelltaleManager:
    """
    Manages extraction and packing of Telltale Games archives (.ttarch2)
    and compilation/decompilation of Localization databases (.landb).
    """
    def __init__(self, tools_dir=None):
        if tools_dir is None:
            # Assume tools are placed in a 'telltale_tools' folder inside 'Core'
            self.tools_dir = os.path.join(os.path.dirname(__file__), 'telltale_tools')
        else:
            self.tools_dir = tools_dir
            
        self.ttarchext_exe = os.path.join(self.tools_dir, 'ttarchext.exe')
        self.ttg_tools_exe = os.path.join(self.tools_dir, 'TTG_Tools.exe')  # or similar CLI tool for landb
        
    def check_tools(self):
        """Checks if the required CLI tools are present."""
        missing = []
        if not os.path.exists(self.ttarchext_exe):
            missing.append('ttarchext.exe')
        # if not os.path.exists(self.ttg_tools_exe):
        #     missing.append('TTG_Tools.exe')
        return missing

    def extract_ttarch2(self, archive_path, output_dir):
        """Extracts a .ttarch2 archive to the specified output directory."""
        if not os.path.exists(self.ttarchext_exe):
            raise FileNotFoundError(f"Cannot find ttarchext.exe at {self.ttarchext_exe}\nPlease download it and place it in the telltale_tools folder.")
            
        os.makedirs(output_dir, exist_ok=True)
        # ttarchext uses specific IDs for games, 67 = The Walking Dead Definitive Series (works for S3)
        game_id = "67" 
        cmd = [self.ttarchext_exe, "-o", game_id, archive_path, output_dir]
        
        try:
            # subprocess.CREATE_NO_WINDOW prevents command prompt flashing
            creationflags = 0x08000000 if os.name == 'nt' else 0
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, creationflags=creationflags)
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, f"Extraction failed:\n{e.stderr or e.stdout}"

    def pack_ttarch2(self, input_dir, output_archive_path):
        """Packs a directory back into a .ttarch2 archive."""
        if not os.path.exists(self.ttarchext_exe):
            raise FileNotFoundError(f"Cannot find ttarchext.exe at {self.ttarchext_exe}\nPlease download it and place it in the telltale_tools folder.")
            
        game_id = "67"
        cmd = [self.ttarchext_exe, "-b", game_id, output_archive_path, input_dir]
        
        try:
            creationflags = 0x08000000 if os.name == 'nt' else 0
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, creationflags=creationflags)
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, f"Packing failed:\n{e.stderr or e.stdout}"
            
    def convert_landb_to_csv(self, landb_paths, csv_path):
        """Converts .landb to a standard TStudio CSV."""
        from landb_parser import LandbParser
        return LandbParser.extract_to_csv(landb_paths, csv_path)

    def convert_csv_to_landb(self, csv_path, input_dir):
        """Converts TStudio CSV back to multiple .landb files."""
        from landb_parser import LandbParser
        return LandbParser.pack_from_csv(csv_path, input_dir)
