@echo off
title SSD Lifespan Analyzer
color 0A

echo ========================================
echo    Starting SSD Lifespan Analyzer
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo.
    echo Please install Python from:
    echo https://python.org
    echo.
    echo Make sure to check "Add Python to PATH"
    pause
    exit /b 1
)

REM Install required packages if missing
echo Checking dependencies...
pip show requests >nul 2>&1
if errorlevel 1 (
    echo Installing requests...
    pip install requests
)
pip show psutil >nul 2>&1
if errorlevel 1 (
    echo Installing psutil...
    pip install psutil
)

echo.
echo Running SSD Analyzer...
echo.
python ssd_analyzer.py

pause