# Build PDF Compressor 2.7 SmartFit locally on Windows

**Prerequisites:** Windows 10/11 x64; Python 3.11+; Git; internet access to install packages.

A 2.7 **preview** EXE was successfully built and launched on Windows 11 on 2026-11-08. This does **not** constitute an official stable release, a clean-machine certification, or third-party license compliance. The published stable version remains v2.6.0.

## 1. Checkout and dependencies

Run in PowerShell from the repository directory:

```powershell
git switch develop/2.7-smartfit
git pull --ff-only origin develop/2.7-smartfit
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pip install "pyinstaller>=6.16,<8"
```

## 2. Tests

```powershell
New-Item -ItemType Directory -Force "$env:LOCALAPPDATA\PDFCompressorTests" | Out-Null
.\.venv\Scripts\python.exe -m pytest -q --basetemp "$env:LOCALAPPDATA\PDFCompressorTests\pytest-run"
```

This explicit pytest path avoids failures caused by Windows access restrictions on a pre-existing pytest temporary directory. GitHub Actions tests Windows Python 3.13 and 3.14, but does not itself build or smoke-test the EXE.

## 3. Build the preview EXE

```powershell
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --onefile --windowed --name PDF_Compressor_2_7_preview --icon app_icon.ico --add-data "app_icon.ico;." --collect-all pymupdf --hidden-import PySide6.QtCore --hidden-import PySide6.QtGui --hidden-import PySide6.QtWidgets app.pyw
```

Result: `dist\PDF_Compressor_2_7_preview.exe`.

## 4. Record the exact build environment and binary checksum

```powershell
git status --short
.\.venv\Scripts\python.exe tools\release_manifest.py --exe .\dist\PDF_Compressor_2_7_preview.exe --out .\dist\build-manifest.json
Get-FileHash .\dist\PDF_Compressor_2_7_preview.exe -Algorithm SHA256
```

The JSON manifest records the EXE SHA-256/size, Python version, installed package versions, Git commit and whether the source tree has local changes. It intentionally excludes local usernames and machine-specific paths. Keep the manifest with release review materials and compare the checksum with the exact binary selected for release.

**Limit:** an environment manifest does not cryptographically prove the contents or complete dependency licenses of the bundled EXE. Versions in `requirements.txt` are ranges, not an exact lock file. For a repeatable release, freeze and review the build environment and inspect the packaged binary.

## 5. Smoke test and redistribution gate

Run the EXE directly (without invoking Python); load, compress, merge, extract and rotate test PDF files; verify output integrity, cancellation and light/dark themes. A local preview smoke test was reported successful on Windows 11.

**Do not publish the preview as stable v2.7.0 until** the release checklist and third-party license review are satisfied, especially AGPL obligations for PyMuPDF and LGPL obligations for Qt / PySide6 `--onefile` distribution. See [release checklist](docs/RELEASE_CHECKLIST_2_7.md) and [third-party notices](docs/THIRD_PARTY_NOTICES_2_7.md).
