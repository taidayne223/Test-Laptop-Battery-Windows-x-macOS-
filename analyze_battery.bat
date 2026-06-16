@echo off
cd /d "%~dp0"
title Laptop Battery Test - Log Analyzer
echo ===================================================
echo     Laptop Battery Test - Log Analyzer
echo ===================================================
echo.
echo Running from directory: %CD%
echo.

if exist "battery_test_env\Scripts\activate.bat" (
    call battery_test_env\Scripts\activate.bat
)
if exist "battery_test_env\Scripts\python.exe" (
    battery_test_env\Scripts\python.exe datetime_calculator.py
) else (
    python datetime_calculator.py
)

echo.
echo ===================================================
pause
