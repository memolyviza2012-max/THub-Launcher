@echo off
echo ==============================================
echo TStudio Launch Diagnostic
echo ==============================================
echo.
echo Launching TStudio and capturing all output to tstudio_crash.log...

cd /d "%~dp0tools\flagship\TStudio"
python tstudio_app.py --project "%~dp0" > "%~dp0tstudio_crash.log" 2>&1

echo.
echo TStudio closed or crashed!
echo Please check modder-hub\tstudio_crash.log for any errors.
pause
