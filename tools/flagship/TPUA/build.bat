@echo off
echo Building TPUA with PyInstaller...
pyinstaller --noconsole --onefile --add-data "locales;locales" --add-data "assets;assets" --icon="assets/TPUA.png" tpua_app.py
echo Build complete!
pause
