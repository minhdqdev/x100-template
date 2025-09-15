@echo off
setlocal enabledelayedexpansion
set SCRIPT_DIR=%~dp0

where uv >nul 2>nul
if errorlevel 1 (
  echo Error: 'uv' not found on PATH.
  echo Install uv via: winget install Astral-sh.UV ^|^| choco install uv
  exit /b 127
)

set VENV_DIR=%SCRIPT_DIR%\.venv
if not exist "%VENV_DIR%" (
  echo Creating virtual environment with uv at %VENV_DIR%
  uv venv "%VENV_DIR%"
)

if exist "%SCRIPT_DIR%requirements.txt" (
  echo Installing dependencies with uv pip
  uv pip install -p "%VENV_DIR%" -r "%SCRIPT_DIR%requirements.txt"
)

set PY=%VENV_DIR%\Scripts\python.exe
"%PY%" "%SCRIPT_DIR%main.py" %*
