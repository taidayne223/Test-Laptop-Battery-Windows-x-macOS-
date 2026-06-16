@echo off
cd /d "%~dp0"

:: Check for administrator privileges
net session >nul 2>&1
if %errorLevel% == 0 (
    goto :admin_start
) else (
    echo ===================================================
    echo  Requesting Administrator privileges to automate
    echo  brightness and CABC settings...
    echo ===================================================
    powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

:admin_start
title YouTube Battery Test Launcher
echo ===================================================
echo     YouTube Battery Test - Focus Launcher
echo ===================================================
echo.
echo Running from directory: %CD%
echo.

REM Check if virtual environment exists
if exist "battery_test_env\Scripts\activate.bat" (
    echo Activating virtual environment...
    call battery_test_env\Scripts\activate.bat
    echo Installing/Updating dependencies...
    python -m pip install -r requirements.txt
) else (
    echo Creating virtual environment battery_test_env...
    python -m venv battery_test_env
    if exist "battery_test_env\Scripts\activate.bat" (
        call battery_test_env\Scripts\activate.bat
        echo Installing dependencies...
        python -m pip install -r requirements.txt
    ) else (
        echo [WARNING] Could not create virtual environment. Trying global install...
        python -m pip install -r requirements.txt
    )
)

echo.
echo Starting YouTube-Only Battery Test...
if exist "battery_test_env\Scripts\python.exe" (
    battery_test_env\Scripts\python.exe test_youtube_only.py
) else (
    python test_youtube_only.py
)

echo.
echo ===================================================
pause
