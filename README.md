# PDF Compressor 2.7 — SmartFit

**Free, open-source, offline PDF compression for Windows 10/11 (64-bit).** Russian and English interface.

**[Download PDF Compressor 2.7.0 for Windows](https://github.com/Valik2005/pdf-compressor/releases/tag/v2.7.0)**

Download `PDF_Compressor_2_7.exe` from the release assets and run it. It is a **single standalone EXE**, with no Python installation needed. The file is unsigned, so Windows SmartScreen may display a warning.

## Features

- **SmartFit:** analyze a text, scanned or mixed PDF and automatically try conservative compression settings for a requested file size.
- Optional image downscaling, shared-image safeguards and faster quality searches.
- Batch PDF compression, progress/cancellation, size and quality comparison.
- PDF merge, extract pages and rotate.
- Light/dark themes, Russian/English UI, fully offline operation.

A requested target size is not always achievable. Inspect the compressed output visually, especially scans and fine print.

## Source and licenses

The application is licensed under **AGPL-3.0-only**; source code, tests and build instructions are in this repository. The [v2.7.0 release](https://github.com/Valik2005/pdf-compressor/releases/tag/v2.7.0) includes checksum files, full upstream source archives for Qt/PySide6/PyMuPDF/MuPDF and required third-party notices. Users can rebuild a single EXE with compatible replacement Qt libraries; see [Qt relinking instructions](docs/LGPL_RELINKING_2_7.md) and [license notices](docs/THIRD_PARTY_NOTICES_RELEASE_2_7.md).

## Running from source

Requires Python 3.11+ on Windows:

```powershell
python -m pip install -r requirements.txt
python app.pyw
```

Tests: `python -m pip install -r requirements-dev.txt`, then `python -m pytest -q`.

See [BUILDING.md](BUILDING.md) and [SmartFit design notes](docs/SMARTFIT_2_7.md).
