@echo off
setlocal

cd /d "%~dp0"

if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] No se encontro "venv\Scripts\activate.bat".
    echo Crea el entorno virtual con: python -m venv venv
    exit /b 1
)

call "venv\Scripts\activate.bat"

if not exist "run.py" (
    echo [ERROR] No se encontro "run.py" en "%CD%".
    exit /b 1
)

python run.py %*
set "EXIT_CODE=%ERRORLEVEL%"
endlocal & exit /b %EXIT_CODE%
