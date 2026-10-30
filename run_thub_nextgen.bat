@echo off
cd /d "%~dp0"
title THub Launcher 2.2 (Next-Gen)
python app_nextgen.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo THub crashed with error code %ERRORLEVEL%
    pause
)
