@echo off
cd /d "%~dp0"
python tglyph_app.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo =======================================================
    echo [ERROR] TGlyph exited with error code %ERRORLEVEL%
    echo =======================================================
    pause
)
