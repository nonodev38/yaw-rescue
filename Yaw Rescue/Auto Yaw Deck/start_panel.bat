@echo off
echo ============================================
echo   AUTO-YAW DECK - Control Panel
echo ============================================
echo.
cd /d "%~dp0"
python panel.py %*
pause
