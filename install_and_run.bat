@echo off
title SSD Lifespan Analyzer - Installer
color 0E

echo ========================================
echo   SSD Lifespan Analyzer - Setup
echo ========================================
echo.

REM Check admin rights (recommended for SMART data)
net session >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Not running as Administrator
    echo For best results (full SMART access), run as Admin
    echo.
)

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    echo.
    echo Download Python from: https://python.org
    echo IMPORTANT: Check "Add Python to PATH" during install
    echo.
    echo After installing Python, run this script again.
    pause
    exit /b 1
)

echo [✓] Python found

REM Upgrade pip
echo [1/3] Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1

REM Install packages
echo [2/3] Installing required packages...
pip install requests psutil >nul 2>&1
echo [✓] Packages installed

REM Create desktop shortcut
echo [3/3] Creating desktop shortcut...
set SCRIPT_DIR=%~dp0
set DESKTOP=%USERPROFILE%\Desktop
set SHORTCUT="%DESKTOP%\SSD Analyzer.lnk"

powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut(%SHORTCUT%); $Shortcut.TargetPath = '%SCRIPT_DIR%run_ssd_analyzer.bat'; $Shortcut.WorkingDirectory = '%SCRIPT_DIR%'; $Shortcut.Save()" >nul 2>&1
echo [✓] Desktop shortcut created

echo.
echo ========================================
echo   SETUP COMPLETE!
echo ========================================
echo.
echo To use SSD Lifespan Analyzer:
echo   1. Double-click "run_ssd_analyzer.bat"
echo      OR click the desktop shortcut
echo.
echo For best results on Windows:
echo   Right-click run_ssd_analyzer.bat
echo   Select "Run as Administrator"
echo.
echo Press any key to launch the analyzer now...
pause >nul

call run_ssd_analyzer.bat