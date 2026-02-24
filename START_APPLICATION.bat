@echo off
title EDU Toolbox MVP - Desktop Application
echo ========================================
echo    EDU TOOLBOX MVP - DESKTOP VERSION
echo ========================================
echo.
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Starting desktop application...
echo (No browser needed - opens in desktop window)
echo.
echo Login Options:
echo - Student: Select "Student" and click Login
echo - Teacher: Select "Teacher" and click Login
echo.
python app.py
echo.
echo Application closed. Press any key to exit.
pause >nul