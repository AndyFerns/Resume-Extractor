@echo off
REM ===========================================================================
REM  run.bat — Quick launcher for the Resume Extractor application (Windows)
REM  Usage:   run.bat              (starts server on default port 5000)
REM           run.bat --port 8080  (starts server on custom port)
REM ===========================================================================

echo ============================================
echo   Resume Extractor - Quick Start
echo ============================================
echo.

REM --- Check if virtual environment exists ---
if not exist ".venv\Scripts\python.exe" (
    echo [1/3] Creating virtual environment...
    python -m venv .venv
    echo       Done.
) else (
    echo [1/3] Virtual environment already exists.
)

REM --- Install / update dependencies ---
echo [2/3] Installing dependencies...
.venv\Scripts\pip.exe install -q -r requirements.txt

REM --- Start the application ---
echo [3/3] Starting Resume Extractor server...
echo.
echo       Open http://localhost:5000 in your browser.
echo       Press Ctrl+C to stop.
echo.
.venv\Scripts\python.exe app.py %*
