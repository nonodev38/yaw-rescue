@echo off
setlocal EnableDelayedExpansion
title Yaw Rescue - Control Panel

echo ============================================
echo   YAW RESCUE - Control Panel
echo ============================================
echo.

rem ---------------------------------------------------------------
rem  Go to the folder that contains this batch file
rem ---------------------------------------------------------------
cd /d "%~dp0" 2>nul
if errorlevel 1 (
    echo [ERROR] Cannot access the Auto Yaw Deck folder:
    echo         %~dp0
    goto :fail
)

rem ---------------------------------------------------------------
rem  Sanity check: the Python files must be in the same folder
rem ---------------------------------------------------------------
if not exist "panel.py" (
    echo [ERROR] panel.py not found next to start_panel.bat.
    echo.
    echo   Make sure the WHOLE "Auto Yaw Deck" folder was copied into:
    echo     X-Plane 12\Resources\plugins\FlyWithLua\Scripts\Auto Yaw Deck\
    goto :fail
)
if not exist "server.py" (
    echo [ERROR] server.py not found next to start_panel.bat.
    echo         The folder seems incomplete - copy it again from the archive.
    goto :fail
)

rem ---------------------------------------------------------------
rem  Find a working Python 3.7+ interpreter.
rem  Tries, in order:  py -3   python   python3
rem  Each candidate is actually executed and version-checked, so a
rem  broken install or a Microsoft Store stub is skipped.
rem ---------------------------------------------------------------
set "PYTHON_CMD="

where py >nul 2>nul
if not errorlevel 1 (
    py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 7) else 1)" >nul 2>nul
    if not errorlevel 1 set "PYTHON_CMD=py -3"
)

if not defined PYTHON_CMD (
    where python >nul 2>nul
    if not errorlevel 1 (
        python -c "import sys; sys.exit(0 if sys.version_info >= (3, 7) else 1)" >nul 2>nul
        if not errorlevel 1 set "PYTHON_CMD=python"
    )
)

if not defined PYTHON_CMD (
    where python3 >nul 2>nul
    if not errorlevel 1 (
        python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 7) else 1)" >nul 2>nul
        if not errorlevel 1 set "PYTHON_CMD=python3"
    )
)

if not defined PYTHON_CMD goto :no_python

echo [OK] Using Python: %PYTHON_CMD%
%PYTHON_CMD% --version
echo.

rem ---------------------------------------------------------------
rem  tkinter is required for the GUI panel
rem ---------------------------------------------------------------
%PYTHON_CMD% -c "import tkinter" >nul 2>nul
if errorlevel 1 goto :no_tkinter

rem ---------------------------------------------------------------
rem  Friendly warning if the default port is already in use
rem  (skipped when a custom --port argument was passed)
rem ---------------------------------------------------------------
echo %* | findstr /I "port" >nul 2>nul
if errorlevel 1 (
    powershell -NoProfile -Command "if (Get-NetTCPConnection -LocalPort 8443 -State Listen -ErrorAction SilentlyContinue) { exit 1 } else { exit 0 }" >nul 2>nul
    if errorlevel 1 (
        echo [WARNING] Port 8443 is already in use.
        echo           Another instance may already be running - if it is,
        echo           simply scan its QR code. Otherwise use:
        echo             start_panel.bat --port 9000
        echo.
    )
)

rem ---------------------------------------------------------------
rem  Launch the control panel (passes through any extra arguments)
rem ---------------------------------------------------------------
echo Opening the control panel... look for the "Yaw Rescue" window.
echo The console will minimize by itself - that is normal.
echo.
%PYTHON_CMD% panel.py %*
set "EXIT_CODE=!ERRORLEVEL!"

if not "!EXIT_CODE!"=="0" (
    echo.
    echo [ERROR] The control panel exited with code !EXIT_CODE!.
    echo         Scroll up to read the Python error message above.
    goto :fail
)

echo.
echo Control panel closed. Goodbye!
exit /b 0

rem ===============================================================
rem  Error messages
rem ===============================================================

:no_python
echo [ERROR] Python 3.7 or newer was not found on this system.
echo.
echo   Yaw Rescue needs Python to start the control panel.
echo.
echo   To fix this:
echo     1. Download Python from   https://www.python.org/downloads/
echo     2. During installation, tick  "Add python.exe to PATH"
echo     3. Close this window, then double-click start_panel.bat again
echo.
echo   Note: if a "python" command exists but opens the Microsoft Store,
echo   that is a Store stub, not a real Python - use python.org instead.
goto :fail

:no_tkinter
echo [ERROR] Python was found, but tkinter is missing.
echo   The GUI control panel needs tkinter.
echo.
echo   Fix: reinstall Python from python.org and keep the
echo   "tcl/tk and IDLE" option selected during installation.
goto :fail

:fail
echo.
echo ============================================
echo   Something went wrong - see messages above.
echo ============================================
pause
exit /b 1