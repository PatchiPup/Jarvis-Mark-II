@echo off
setlocal EnableDelayedExpansion

REM ===============================================================
REM Capture Original Directory and Request Elevation if Not Admin
REM ===============================================================
if "%~1"=="" (
    set "ORIGINAL_PATH=%CD%"
) else (
    set "ORIGINAL_PATH=%~1"
)

REM Check for admin privileges using NET SESSION (only works when elevated)
net session >nul 2>&1
if %errorlevel% NEQ 0 (
    echo Requesting administrative privileges...
    powershell -Command "Start-Process '%~f0' -ArgumentList '%ORIGINAL_PATH%' -Verb runAs"
    exit /b
)

REM Change directory to the original folder from which the script was launched
cd /d "%~dp0"

REM ================================================
REM Jarvis Mark 2.1 - Marvel Rivals AI Assistant
REM Modularized by ifBars (based on Patchi's Mark 2)
REM ================================================

echo ================================================
echo Jarvis Mark 2.1 - Marvel Rivals AI Assistant
echo Modularized by ifBars (based on Patchi's Mark 2)
echo ================================================

python main.py
pause