@echo off
setlocal

cd /d "%~dp0"

set "VENV_PY=venv312\Scripts\python.exe"

if "%LLM_PROVIDER%"=="" set "LLM_PROVIDER=gemini"
if "%GEMINI_MODEL%"=="" set "GEMINI_MODEL=gemini-2.5-flash"

if not exist "%VENV_PY%" (
    echo [ERROR] Virtual environment Python not found: %VENV_PY%
    echo Create it with:
    echo   python -m venv venv312
    echo Then install dependencies:
    echo   %VENV_PY% -m pip install -r requirements.txt
    pause
    exit /b 1
)

"%VENV_PY%" capp_app.py
exit /b %errorlevel%
