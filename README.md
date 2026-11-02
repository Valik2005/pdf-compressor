# PDF Compressor 2.6

**Offline PDF compression and page tools for Windows 10/11 (64-bit).**  
**Open source · English / Русский · No account or cloud uploads**

[Русская документация](README_RU.md) · [All releases](https://github.com/Valik2005/pdf-compressor/releases) · [Source license](LICENSE)

[![Download PDF Compressor 2.6 for Windows](https://img.shields.io/badge/Download%20for%20Windows-PDF%20Compressor%202.6-567CF5?style=for-the-badge&logo=windows)](https://github.com/Valik2005/pdf-compressor/releases/download/v2.6.0/PDF_Compressor_2_6.exe)

**[⬇ Download PDF_Compressor_2_6.exe](https://github.com/Valik2005/pdf-compressor/releases/download/v2.6.0/PDF_Compressor_2_6.exe)** · [View release notes](https://github.com/Valik2005/pdf-compressor/releases/tag/v2.6.0)

The Windows executable is provided under **Releases → Assets**, not in the source-code folder. You do **not** need Python to run the EXE. The binary is unsigned; Windows SmartScreen may display a warning.

## Features

- Batch PDF compression with four modes: target size, highest quality, balanced, and maximum compression
- Lossless optimization first; optional JPEG recompression of embedded images
- Progress indicator, cancellation, resulting size and savings
- Side-by-side original/output page comparison, navigation, zoom, and preview rotation
- Merge PDF documents; split or extract pages; rotate document pages
- Drag and drop, saved settings, light and dark themes
- Russian and English interface
- Local processing; original PDF files are not overwritten

**Quality note:** A target size such as 1 MB is a goal, not a guarantee. Some PDFs cannot be reduced that far without lowering image quality or resolution. Operations affecting a digitally signed PDF may invalidate the signature.

## Install

1. [Download the Windows EXE](https://github.com/Valik2005/pdf-compressor/releases/download/v2.6.0/PDF_Compressor_2_6.exe).
2. Run `PDF_Compressor_2_6.exe` on Windows 10/11 x64.
3. Select English or Русский and start processing documents.

No installation wizard or Python runtime is required. Processing takes place on your own PC.

## Source code

| File | Purpose |
| --- | --- |
| `app.pyw` | PySide6 desktop GUI and translations |
| `pdf_engine.py` | PDF compression and document operations |
| `requirements.txt` | Python runtime dependencies |
| `app_icon.ico` | Application icon |
| `tests/` | PDF engine and translation tests |
| [`BUILDING.md`](BUILDING.md) | Build from source and create your own EXE |

To run from source (Python 3.11+):

```powershell
python -m pip install -r requirements.txt
python app.pyw
```

To run tests:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

## Open-source license and dependencies

The **application source code** is distributed under the [GNU Affero General Public License, version 3 (AGPL-3.0-only)](LICENSE). Contributions and redistributions must follow its terms.

This project uses **PyMuPDF** (AGPLv3 or commercial) and **PySide6 / Qt** (LGPL/GPL or commercial), along with Pillow. These components retain their own copyrights and license terms. Read [Third-party licenses and redistribution notes](DEPENDENCIES_AND_LICENSING.md) before redistributing a bundled EXE. Source availability alone does not necessarily satisfy all third-party binary distribution requirements.

The app is not affiliated with Artifex, PyMuPDF, or Qt.

**Security note:** The executable is unsigned and was locally built for the v2.6.0 release. Only run files you trust. Its SHA-256 appears in [release notes](RELEASE_NOTES.md).
