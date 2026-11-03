# Build PDF Compressor 2.7 SmartFit locally on Windows

**Prerequisites:** Windows 10/11 x64, Python 3.11+ and an internet connection to install packages. This 2.7 build has not been tested on Windows yet.

Open PowerShell in this folder and run:

```powershell
python -m pip install -r requirements.txt
python -m pip install "pyinstaller>=6.16,<8"
python -m PyInstaller --noconfirm --clean --onefile --windowed --name PDF_Compressor_2_7_preview --icon app_icon.ico --add-data "app_icon.ico;." --collect-all pymupdf --hidden-import PySide6.QtCore --hidden-import PySide6.QtGui --hidden-import PySide6.QtWidgets app.pyw
```

The resulting file will be at `dist\PDF_Compressor_2_7_preview.exe`. Do not publish it as a stable release before Windows verification and checking the bundled dependency license notices.

To run from source without building an EXE:

```powershell
python -m pip install -r requirements.txt
python app.pyw
```

To run automated tests:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
```
