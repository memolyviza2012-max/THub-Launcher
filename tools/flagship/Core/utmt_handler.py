import os
import subprocess
import shutil

class UTMTHandler:
    BIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "bin"))
    UTMT_DIR = os.path.join(BIN_DIR, "UTMT")
    CLI_EXE = os.path.join(UTMT_DIR, "UndertaleModCli.exe")

    @classmethod
    def is_installed(cls):
        return os.path.exists(cls.CLI_EXE)
        
    @classmethod
    def install(cls, progress_callback=None):
        setup_script = os.path.join(cls.BIN_DIR, "setup_utmt.py")
        if os.path.exists(setup_script):
            subprocess.run(["python", setup_script], check=True)
        return cls.is_installed()

    @classmethod
    def extract_strings_to_csv(cls, win_file_path):
        """
        Extracts strings from data.win and formats them to a TStudio compatible CSV.
        """
        if not cls.is_installed():
            if not cls.install():
                raise Exception("UTMT could not be installed.")
                
        # The script we want to run
        script_name = "TStudioExportStrings.csx"
        script_path = os.path.join(cls.UTMT_DIR, "Scripts", script_name)
        if not os.path.exists(script_path):
            raise Exception(f"Script not found: {script_path}")
            
        # UndertaleModCli.exe typically puts exported files in the same directory as data.win
        # or we might need to change dir
        working_dir = os.path.dirname(win_file_path)
        
        # Call UTMT CLI
        # Usage: UndertaleModCli.exe <data.win> -s <script.csx>
        import subprocess
        creationflags = 0
        if os.name == 'nt':
            creationflags = subprocess.CREATE_NEW_CONSOLE
            
        try:
            result = subprocess.run(
                [cls.CLI_EXE, "load", win_file_path, "-s", script_path],
                cwd=working_dir,
                creationflags=creationflags,
                check=True
            )
        except subprocess.CalledProcessError as e:
            raise Exception(f"UTMT Extract Error: Process failed with code {e.returncode}")
            
        # The script ExportAllStrings.csx usually generates strings.txt or Export_Strings.txt
        # We need to find what it generated and convert to CSV.
        exported_txt = os.path.join(working_dir, "Export_Strings.txt")
        # UTMT might name it something else, check common names:
        possible_outputs = ["Export_Strings.txt", "strings.txt", "ExportedStrings.txt"]
        found_txt = None
        for po in possible_outputs:
            p = os.path.join(working_dir, po)
            if os.path.exists(p):
                found_txt = p
                break
                
        if not found_txt:
            # Maybe it created a folder
            raise Exception(f"Could not find exported txt file in {working_dir}. UTMT Output: {result.stdout}")
            
        # Convert TXT to CSV
        import csv
        csv_path = os.path.join(working_dir, "translation_utmt.csv")
        
        with open(found_txt, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
            
        with open(csv_path, 'w', encoding='utf-8-sig', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["ID", "SourceText", "TranslatedText"])
            # Format in Export_Strings.txt is usually:
            # stringId: text
            # or just text line by line. UTMT's default ExportAllStrings.csx exports just lines.
            for i, line in enumerate(lines):
                clean_line = line.strip('\n').strip('\r')
                writer.writerow([f"String_{i}", clean_line, ""])
                
        return csv_path

    @classmethod
    def repack_strings_from_csv(cls, win_file_path, csv_path):
        """
        Packs translations from CSV back into data.win.
        """
        working_dir = os.path.dirname(win_file_path)
        
        # Read CSV and recreate the text file UTMT expects (Import_Strings.txt)
        import csv
        import_txt_path = os.path.join(working_dir, "Import_Strings.txt")
        
        with open(csv_path, 'r', encoding='utf-8-sig') as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None)  # skip header
            lines = []
            for row in reader:
                if not row:
                    continue
                if len(row) >= 3:
                    src = row[1]
                    trans = row[2]
                    lines.append(trans if trans.strip() else src)
                elif len(row) >= 2:
                    lines.append(row[1])
                elif len(row) >= 1:
                    lines.append(row[0])

                
        with open(import_txt_path, 'w', encoding='utf-8', newline='\n') as f:
            for line in lines:
                f.write(f"{line}\n")
                
        script_name = "TStudioImportStrings.csx"
        script_path = os.path.join(cls.UTMT_DIR, "Scripts", script_name)
        if not os.path.exists(script_path):
            raise Exception(f"Script not found: {script_path}")
            
        import subprocess
        creationflags = 0
        if os.name == 'nt':
            creationflags = subprocess.CREATE_NEW_CONSOLE
            
        try:
            result = subprocess.run(
                [cls.CLI_EXE, "load", win_file_path, "-s", script_path],
                cwd=working_dir,
                creationflags=creationflags,
                check=True
            )
        except subprocess.CalledProcessError as e:
            raise Exception(f"UTMT Inject Error: Process failed with code {e.returncode}")
            
        # The script usually modifies data.win and saves it as data_modded.win or overwrites.
        modded_win = os.path.join(working_dir, "data_modded.win")
        if os.path.exists(modded_win):
            return modded_win
            
        return win_file_path

