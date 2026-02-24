@echo off
echo Cleaning temporary lock files...
powershell -Command "Get-ChildItem -Path . -Include '~$*' -Recurse -Force | Remove-Item -Force -Verbose"
echo Building EDU Toolbox Final Executable...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if PyInstaller is installed
python -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

REM Build the executable
echo Building executable...
python -m PyInstaller --onefile --windowed --add-data "ui;ui" --name "EDU_Toolbox_Final" app.py

if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo SUCCESS: Build completed!
echo Executable location: dist\EDU_Toolbox_Final.exe
echo.
pause