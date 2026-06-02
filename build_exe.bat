@echo off
title SSD Analyzer - Executable Builder
echo ========================================
echo   Building SSD Lifespan Analyzer .EXE
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python from https://python.org
    echo Make sure to check "Add Python to PATH"
    pause
    exit /b 1
)

echo [1/4] Installing required packages...
pip install pyinstaller requests psutil >nul 2>&1
echo       Done.

echo [2/4] Creating standalone executable...
pyinstaller --onefile --name "SSD_Lifespan_Analyzer" --console --noconfirm ssd_analyzer.py >nul 2>&1

if errorlevel 1 (
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

echo [3/4] Cleaning up...
del /q *.spec >nul 2>&1
rmdir /s /q build >nul 2>&1

echo [4/4] Build complete!
echo.
echo ========================================
echo   SUCCESS! Executable created:
echo   dist\SSD_Lifespan_Analyzer.exe
echo ========================================
echo.
echo You can now:
echo   1. Run SSD_Lifespan_Analyzer.exe directly
echo   2. Copy it to any Windows computer
echo   3. No Python installation needed!
echo.

pause