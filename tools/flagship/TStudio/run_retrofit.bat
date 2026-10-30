@echo off
chcp 65001 > nul
title TStudio Zero-Token Retrofit Tool
echo =====================================================================
echo   TStudio Zero-Token Retrofit Tool (Keyboard Keys & Military Terms)
echo =====================================================================
echo.

if "%~1"=="" (
    python "%~dp0retrofit_cli.py"
) else (
    python "%~dp0retrofit_cli.py" "%~1"
)

echo.
pause
