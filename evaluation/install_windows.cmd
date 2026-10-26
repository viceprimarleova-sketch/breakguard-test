@echo off
setlocal
cd /d "%~dp0"
py -3 verify_kit.py
if errorlevel 1 exit /b 1
py -3 -m venv .venv
if errorlevel 1 exit /b 1
".venv\Scripts\python.exe" -m pip --disable-pip-version-check install --force-reinstall --no-index --find-links "wheels" breakguard=={{VERSION}}
if errorlevel 1 exit /b 1
".venv\Scripts\breakguard.exe" --version
