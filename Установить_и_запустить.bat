@echo off
setlocal
cd /d "%~dp0"
title PDF Compressor 2.6 - Setup

echo ==============================================
echo PDF Compressor 2.6 - Setup and launch
echo ==============================================
echo.

set "PY=python"
python -c "import sys" >nul 2>nul
if errorlevel 1 (
    py -3 -c "import sys" >nul 2>nul
    if errorlevel 1 (
        echo [ERROR] Python was not found. Please install Python first.
        pause
        exit /b 1
    )
    set "PY=py -3"
)

echo Installing/checking required packages...
%PY% -m pip install --disable-pip-version-check -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to install packages. See messages above.
    pause
    exit /b 1
)

echo.
echo Starting PDF Compressor without a console...
%PY% -c "import os,sys,subprocess; gui=os.path.join(os.path.dirname(sys.executable),'pythonw.exe'); subprocess.Popen([gui,os.path.join(os.getcwd(),'app.pyw')],cwd=os.getcwd())"
if errorlevel 1 (
    echo [ERROR] GUI launch failed. Try: python app.pyw
    pause
    exit /b 1
)
exit /b 0
