# Building PDF Compressor from source

The project ships the Windows executable through [GitHub Releases](https://github.com/Valik2005/pdf-compressor/releases). The source repository intentionally does **not** contain `.exe` or `.bat` files.

## Run from source

Requires Python **3.11+**, Windows 10/11 x64, and internet access to install Python packages.

```powershell
python -m pip install -r requirements.txt
python app.pyw
```

Run the checks:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

## Build your own EXE (on Windows)

Install PyInstaller:

```powershell
python -m pip install -r requirements.txt
python -m pip install "pyinstaller>=6.16,<8"
```

Then run in **PowerShell** from the project folder:

```powershell
python -m PyInstaller --noconfirm --clean --onefile --windowed --name PDF_Compressor_2_6 --icon app_icon.ico --add-data "app_icon.ico;." --collect-all pymupdf --hidden-import PySide6.QtCore --hidden-import PySide6.QtGui --hidden-import PySide6.QtWidgets app.pyw
```

Result: `dist\PDF_Compressor_2_6.exe`. On Windows, `--windowed` prevents a console window.

The release executable currently comes from a **local Windows build**. The old GitHub Actions EXE workflow was removed because GitHub Actions could not start in this repository due to account billing restrictions.

**Before redistributing a built executable:** review [third-party licensing and notices](DEPENDENCIES_AND_LICENSING.md). For fully reproducible releases, pin dependency versions, record hashes, and retain the build environment. This guide is not proof that a particular bundled EXE meets all licensing requirements.

---

## Сборка на русском

Исходники запускаются через `python app.pyw` после установки зависимостей командой `python -m pip install -r requirements.txt`. Для получения одного Windows EXE установи PyInstaller и выполни команду выше из PowerShell. Готовый файл появится в `dist\PDF_Compressor_2_6.exe`. Для скачивания программы без Python используй [Releases](https://github.com/Valik2005/pdf-compressor/releases).
