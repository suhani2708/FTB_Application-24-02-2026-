@echo off
title Build EDU Toolbox Executable
echo ========================================
echo    BUILDING EDU TOOLBOX EXECUTABLE
echo ========================================
echo.
echo Installing build dependencies...
pip install pyinstaller
echo.
echo Building executable (this may take a few minutes)...
python build_executable.py
echo.
echo Build complete! Check the 'dist' folder for EDU_Toolbox.exe
echo.
pause