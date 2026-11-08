# PDF Compressor 2.7

[Русская версия README](README_RU.md)

**Offline PDF compressor and page toolkit for Windows**, written in Python and PySide6. The interface supports **English and Russian**, dark/light themes and batch processing.

> All files are processed locally. The application does not upload documents to a cloud service.

## Features

- Compress one or multiple PDFs with four modes: target size (**SmartFit**), highest quality, balanced and maximum compression.
- **SmartFit (new in 2.7):** classify text, scanned and mixed documents to select conservative compression attempts.
- Try lossless optimization before recompressing embedded images; optionally reduce image resolution only when enabled by the user.
- Preserve selectable/vector PDF text where possible; improve handling of images shared between pages.
- Show processing progress, support cancellation and summarize resulting file sizes.
- Preview original and output pages side by side (zoom, page navigation, preview rotation).
- Merge PDFs; split/extract selected pages; rotate document pages without unnecessarily recompressing page images.
- Choose output directory and file naming; remember language, theme and settings.
- Keep original PDFs unchanged by writing results to separate files.

**Important:** A requested size such as 1 MB is a **goal, not a guarantee**. Already optimized or complex PDFs may not reach it without image quality loss. Image recompression can be lossy; editing a PDF may invalidate digital signatures, and the application has safeguards for signed documents.

## Download the Windows EXE (no Python required)

**[Download PDF Compressor 2.7.0 from GitHub Releases](https://github.com/Valik2005/pdf-compressor/releases/tag/v2.7.0).**

1. Open the release page and expand **Assets**.
2. Download **`PDF_Compressor_2_7.exe`**.
3. Run it on **Windows 10/11 (64-bit)**. This is **one standalone EXE**: you do not need to install Python, unpack a program folder or use an installer.

The executable is unsigned, so Windows SmartScreen may display a warning. The release also provides `SHA256SUMS.txt`, a build manifest, third-party license notices and the sources for bundled libraries.

## Windows installation from source

Requires Python **3.11 or newer**; the official Windows release build uses Python 3.14 and pinned dependencies.

1. Download the source repository (**Code → Download ZIP**) and extract it, or clone it with Git.
2. In PowerShell or CMD, from the repository directory run:

   ```bat
   python -m pip install -r requirements.txt
   python app.pyw
   ```

3. Select **Русский / English** in the top toolbar. The preference is saved.

For subsequent launches without a console, open `app.pyw` with Python installed.

## Build a standalone Windows EXE

The official v2.7.0 executable is produced and verified by [the Windows release workflow](.github/workflows/release-v2_7.yml). For a local review build on Windows, install the pinned packages and run:

```bat
python -m pip install "PyMuPDF==1.27.2.3" "PySide6==6.12.0" "Pillow==12.3.0" "pyinstaller==6.22.3"
python -m PyInstaller --noconfirm --clean release_windows_review.spec
```

Local output: `dist\PDF_Compressor_2_7_license_review.exe`. The official release workflow renames the verified build to `PDF_Compressor_2_7.exe` and attaches its checksums and source archives to the release. Building a Windows EXE requires Windows. See [BUILDING.md](BUILDING.md) and the [Qt relinking guide](docs/LGPL_RELINKING_2_7.md).

## Run tests

```bat
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Tests cover PDF processing, SmartFit regression cases and translation integrity. GUI appearance depends on Windows and display scaling; the official release workflow additionally verifies EXE startup on Windows.

## Repository layout

```text
app.pyw                       Desktop application and bilingual Qt UI
pdf_engine.py                 PDF compression and page operations
app_icon.ico                  Windows application icon
requirements.txt              Runtime dependencies
tests/                        Engine, SmartFit, packaging and localization tests
tools/                        Release audits, manifests and Qt relinking tools
release_windows_review.spec   PyInstaller one-file build specification
BUILDING.md                   Windows build and audit instructions
README_RU.md                  Русская инструкция
.github/workflows/release-v2_7.yml   Version 2.7 release workflow
```

## Licensing note

The application is distributed under **GNU AGPL-3.0-only**. PyMuPDF/MuPDF are AGPL or commercially licensed, and Qt/PySide6 include LGPL/GPL/commercial licensing options. The [v2.7.0 release](https://github.com/Valik2005/pdf-compressor/releases/tag/v2.7.0) includes the applicable source archives, notices, hashes and instructions for rebuilding the one-file EXE with compatible modified Qt libraries. See [DEPENDENCIES_AND_LICENSING.md](DEPENDENCIES_AND_LICENSING.md) and [third-party notices](docs/THIRD_PARTY_NOTICES_RELEASE_2_7.md).

## Disclaimer

Keep backups of important documents. JPEG image compression is lossy even if page resolution is preserved. Always inspect output quality, particularly for scans and small print. The project is not affiliated with PyMuPDF, Artifex or Qt.
