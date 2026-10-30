@echo off
cd /d "%~dp0"
python ..\TStudio\tstudio_app.py --mode=trun %*
