@echo off
setlocal
cd /d "%~dp0"
title PDF Compressor 2.6 - Build EXE

echo ==============================================
echo PDF Compressor 2.6 - Windows EXE builder
echo ==============================================
echo.

set "PY=python"
python -c "import sys" >nul 2>nul
if errorlevel 1 (
    py -3 -c "import sys" >nul 2>nul
    if errorlevel 1 (
        echo [ERROR] Python not found.
        pause
        exit /b 1
    )
    set "PY=py -3"
)

echo Installing build dependencies...
%PY% -m pip install --disable-pip-version-check -r requirements.txt "pyinstaller>=6.16,<8"
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo Building a single EXE without a console...
%PY% -m PyInstaller --noconfirm --clean --onefile --windowed --name "PDF_Compressor_2_6" --icon "app_icon.ico" --add-data "app_icon.ico;." --collect-all pymupdf --hidden-import PySide6.QtCore --hidden-import PySide6.QtGui --hidden-import PySide6.QtWidgets app.pyw
if errorlevel 1 (
    echo [ERROR] Build failed. Check the messages above.
    pause
    exit /b 1
)

echo.
echo ==============================================
echo [OK] EXE is located in: dist\PDF_Compressor_2_6.exe
echo ==============================================
pause
exit /b 0
