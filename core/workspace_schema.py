"""Resolve modern and adopted THub folders without moving existing projects."""
import os


class WorkspaceSchema:
    ALIASES = {
        '01_Original_Backup': ('01_Original_Backup', '01_Original_Files'),
        '02_Translation_Workspace': ('02_Translation_Workspace', '03_Translated_Text', '02_Extracted_Text', '02_Translation'),
        '03_Font_and_UI': ('03_Font_and_UI', '04_Font_Assets'),
        '04_Packed_Mod': ('04_Packed_Mod', '05_Packed_Mod'),
        '05_Scripts_and_Tools': ('05_Scripts_and_Tools',),
        '06_Releases': ('06_Releases', '06_Release'),
        '07_Image_Resources': ('07_Image_Resources',),
    }

    @classmethod
    def folders(cls, project, logical_folder):
        root = project.get('path', '')
        names = cls.ALIASES.get(logical_folder, (logical_folder,))
        # Adopted projects can also have an accidentally-created empty modern folder.
        if project.get('adopted_from_legacy'):
            names = tuple(n for n in names if n != logical_folder) + (logical_folder,)
        return [os.path.join(root, n) for n in names if os.path.isdir(os.path.join(root, n))]

    @classmethod
    def folder(cls, project, logical_folder):
        paths = cls.folders(project, logical_folder)
        return paths[0] if paths else os.path.join(project.get('path', ''), logical_folder)
