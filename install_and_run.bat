@echo off
title SSD Lifespan Analyzer - Installer
color 0E

REM Get the directory where this batch file is located
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo ========================================
echo   SSD Lifespan Analyzer - Installer
echo ========================================
echo.
echo Working directory: %CD%
echo.

REM Check if running as administrator
net session >nul 2>&1
if errorlevel 1 (
    echo [ERROR] This script must be run as Administrator!
    echo.
    echo Please right-click this file and select "Run as Administrator"
    echo.
    pause
    exit /b 1
)

echo [✓] Running with Administrator privileges
echo.

REM Check Python installation
echo [1/4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    echo.
    echo Please install Python from: https://python.org
    echo IMPORTANT: Check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

python --version
echo [✓] Python found
echo.

REM Upgrade pip
echo [2/4] Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1
echo [✓] Pip upgraded
echo.

REM Install required packages globally
echo [3/4] Installing required packages...
pip install requests psutil >nul 2>&1
echo [✓] Packages installed (requests, psutil)
echo.

REM Check if ssd_analyzer.py exists
echo [4/4] Checking for ssd_analyzer.py...
if not exist "%SCRIPT_DIR%ssd_analyzer.py" (
    echo [WARNING] ssd_analyzer.py not found in current folder!
    echo.
    echo Please make sure ssd_analyzer.py is in the same folder.
    echo Current folder: %SCRIPT_DIR%
    echo.
    dir "%SCRIPT_DIR%*.py" 2>nul
    echo.
    pause
    exit /b 1
)
echo [✓] ssd_analyzer.py found
echo.

echo ========================================
echo   INSTALLATION COMPLETE!
echo ========================================
echo.
echo Python packages have been installed globally.
echo You can now run the SSD analyzer from ANY folder.
echo.
echo Choose an option:
echo   1. Run the SSD analyzer now (from current folder)
echo   2. Exit - I will run it manually later
echo.
set /p choice="Enter 1 or 2: "

if "%choice%"=="1" (
    echo.
    echo Starting SSD Lifespan Analyzer...
    echo.
    timeout /t 2 >nul
    python "%SCRIPT_DIR%ssd_analyzer.py"
) else (
    echo.
    echo To run the analyzer later:
    echo   1. Navigate to any folder containing ssd_analyzer.py
    echo   2. Run: python ssd_analyzer.py
    echo.
    echo Or use the run_ssd_analyzer.bat file
    echo.
    pause
)