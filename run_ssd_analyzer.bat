@echo off
title SSD Lifespan Analyzer - Launcher
color 0A

REM Get the directory where this batch file is located
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo ========================================
echo    SSD Lifespan Analyzer - Launcher
echo ========================================
echo.
echo This launcher helps you find and run ssd_analyzer.py
echo from any location on your computer.
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    echo.
    echo Please install Python from: https://python.org
    echo.
    pause
    exit /b 1
)

echo [✓] Python is installed
echo.

:MENU
echo ========================================
echo   Choose an option:
echo ========================================
echo.
echo   1. Run ssd_analyzer.py from current folder
echo   2. Navigate to folder containing ssd_analyzer.py
echo   3. Drag and drop ssd_analyzer.py file here
echo   4. Type the full path to ssd_analyzer.py
echo   5. Exit
echo.
set /p "option=Enter choice (1-5): "

if "%option%"=="1" goto RUN_CURRENT
if "%option%"=="2" goto NAVIGATE
if "%option%"=="3" goto DRAG_DROP
if "%option%"=="4" goto TYPE_PATH
if "%option%"=="5" goto EXIT

echo Invalid choice. Please try again.
timeout /t 2 >nul
goto MENU

:RUN_CURRENT
echo.
echo Checking current folder: %CD%
if exist "%CD%\ssd_analyzer.py" (
    echo [✓] Found ssd_analyzer.py in current folder
    echo.
    echo Running SSD Analyzer...
    echo.
    python "%CD%\ssd_analyzer.py"
    goto DONE
) else (
    echo [ERROR] ssd_analyzer.py not found in current folder!
    echo.
    echo Current folder contents:
    dir /b *.py 2>nul
    echo.
    echo Please select option 2, 3, or 4 to locate the file.
    echo.
    pause
    goto MENU
)

:NAVIGATE
echo.
echo Opening file explorer...
echo Please navigate to the folder containing ssd_analyzer.py
echo.
start explorer.exe
echo.
echo After finding the folder, right-click on ssd_analyzer.py
echo and select "Copy as path" (or hold Shift + right-click)
echo.
set /p "file_path=Paste the full path here: "
set "file_path=%file_path:"=%"
goto CHECK_FILE

:DRAG_DROP
echo.
echo Drag and drop your ssd_analyzer.py file into this window
echo and press Enter.
echo.
set /p "file_path="
set "file_path=%file_path:"=%"
goto CHECK_FILE

:TYPE_PATH
echo.
echo Enter the full path to ssd_analyzer.py
echo Example: C:\Users\YourName\Desktop\SSD_Analyzer\ssd_analyzer.py
echo.
set /p "file_path=Path: "
set "file_path=%file_path:"=%"
goto CHECK_FILE

:CHECK_FILE
echo.
if "%file_path%"=="" (
    echo [ERROR] No path provided!
    pause
    goto MENU
)

if not exist "%file_path%" (
    echo [ERROR] File not found: %file_path%
    echo.
    echo Please check the path and try again.
    pause
    goto MENU
)

REM Check if it's a .py file
if /i not "%file_path:~-3%"==".py" (
    echo [ERROR] Please select a .py file (ssd_analyzer.py)
    pause
    goto MENU
)

REM Get the directory of the script
for %%i in ("%file_path%") do set "SCRIPT_FOLDER=%%~dpi"
set "SCRIPT_FOLDER=%SCRIPT_FOLDER:~0,-1%"

echo [✓] Script found: %file_path%
echo [✓] Script folder: %SCRIPT_FOLDER%
echo.
echo Running SSD Analyzer from: %SCRIPT_FOLDER%
echo.
cd /d "%SCRIPT_FOLDER%"
python "%file_path%"

:DONE
echo.
echo ========================================
echo   Analyzer finished
echo ========================================
echo.
echo Press any key to exit...
pause >nul
goto END

:EXIT
echo.
echo Exiting...
timeout /t 1 >nul
exit /b

:END