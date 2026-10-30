"""Load Windows' ICU before Qt, avoiding unrelated ICU DLLs found on the build PATH."""
import os
if os.name == 'nt':
    import ctypes
    system_directory = ctypes.create_unicode_buffer(32768)
    if ctypes.windll.kernel32.GetSystemDirectoryW(system_directory, len(system_directory)):
        icu_path = os.path.join(system_directory.value, 'icuuc.dll')
        if os.path.isfile(icu_path):
            _thub_system_icu = ctypes.WinDLL(icu_path)
