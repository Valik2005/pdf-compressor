<div align="center">

# 📄 PDF Compressor 2.7

**Offline PDF compression and page tools — everything stays on your computer.**

English and Russian UI · Windows 10/11 · Free and open source

<p>
  <img alt="Release 2.7.0" src="https://img.shields.io/badge/Release-2.7.0-2563eb?style=flat-square" />
  <img alt="Windows 10/11" src="https://img.shields.io/badge/Windows-10%20%7C%2011-0078d4?style=flat-square&amp;logo=windows11&amp;logoColor=white" />
  <img alt="Offline" src="https://img.shields.io/badge/Processing-Offline-238636?style=flat-square" />
  <img alt="AGPL-3.0" src="https://img.shields.io/badge/License-AGPL--3.0-8250df?style=flat-square" />
</p>

<a href="https://github.com/Valik2005/pdf-compressor/releases/download/v2.7.0/PDF_Compressor_2_7.exe">
  <img alt="⬇ Download PDF Compressor 2.7 EXE" src="https://img.shields.io/static/v1?label=%E2%AC%87%20DOWNLOAD&amp;message=PDF%20Compressor%202.7%20EXE&amp;color=238636&amp;style=for-the-badge&amp;logo=windows11&amp;logoColor=white" />
</a>

**One EXE · No Python installation · 69.99 MB**

[Direct EXE download](https://github.com/Valik2005/pdf-compressor/releases/download/v2.7.0/PDF_Compressor_2_7.exe) · [Release page](https://github.com/Valik2005/pdf-compressor/releases/tag/v2.7.0) · [SHA-256](https://github.com/Valik2005/pdf-compressor/releases/download/v2.7.0/SHA256SUMS.txt)

[Русская версия README](README_RU.md)

</div>

---

> 🔒 **Privacy:** all PDF files are processed locally. Documents are never uploaded to a cloud service.

## ✨ Features

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

## ⬇️ Download the Windows EXE (no Python required)

Use the green **DOWNLOAD** button at the top of this page. It links **directly** to the official `PDF_Compressor_2_7.exe` release asset.

| Detail | Value |
| :-- | :-- |
| **Version** | 2.7.0 (stable) |
| **System** | Windows 10/11, 64-bit |
| **Package** | Single EXE, no installer or Python |
| **File size** | 69.99 MB |

[**Direct EXE download**](https://github.com/Valik2005/pdf-compressor/releases/download/v2.7.0/PDF_Compressor_2_7.exe) · [All release assets and licenses](https://github.com/Valik2005/pdf-compressor/releases/tag/v2.7.0) · [Verify SHA-256](https://github.com/Valik2005/pdf-compressor/releases/download/v2.7.0/SHA256SUMS.txt)

> The EXE is unsigned, so Windows SmartScreen may show a warning. You can verify the hash against `SHA256SUMS.txt` before running it.

## 🖥️ Windows installation from source

Requires Python **3.11 or newer**; the official Windows release build uses Python 3.14 and pinned dependencies.

1. Download the source repository (**Code → Download ZIP**) and extract it, or clone it with Git.
2. In PowerShell or CMD, from the repository directory run:

   ```bat
   python -m pip install -r requirements.txt
   python app.pyw
   ```

3. Select **Русский / English** in the top toolbar. The preference is saved.

For subsequent launches without a console, open `app.pyw` with Python installed.

## 🛠️ Build a standalone Windows EXE

The official v2.7.0 executable is produced and verified by [the Windows release workflow](.github/workflows/release-v2_7.yml). For a local review build on Windows, install the pinned packages and run:

```bat
python -m pip install "PyMuPDF==1.27.2.3" "PySide6==6.12.0" "Pillow==12.3.0" "pyinstaller==6.22.3"
python -m PyInstaller --noconfirm --clean release_windows_review.spec
```

Local output: `dist\PDF_Compressor_2_7_license_review.exe`. The official release workflow renames the verified build to `PDF_Compressor_2_7.exe` and attaches its checksums and source archives to the release. Building a Windows EXE requires Windows. See [BUILDING.md](BUILDING.md) and the [Qt relinking guide](docs/LGPL_RELINKING_2_7.md).

## ✅ Run tests

```bat
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Tests cover PDF processing, SmartFit regression cases and translation integrity. GUI appearance depends on Windows and display scaling; the official release workflow additionally verifies EXE startup on Windows.

## 📂 Repository layout

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

## 📜 Licensing note

The application is distributed under **GNU AGPL-3.0-only**. PyMuPDF/MuPDF are AGPL or commercially licensed, and Qt/PySide6 include LGPL/GPL/commercial licensing options. The [v2.7.0 release](https://github.com/Valik2005/pdf-compressor/releases/tag/v2.7.0) groups the applicable upstream sources, license notices, build reports and Qt onefile relinking instructions into **`Third_Party_Sources_and_Licenses.zip`**. See [DEPENDENCIES_AND_LICENSING.md](DEPENDENCIES_AND_LICENSING.md) and [third-party notices](docs/THIRD_PARTY_NOTICES_RELEASE_2_7.md).

## ℹ️ Disclaimer

Keep backups of important documents. JPEG image compression is lossy even if page resolution is preserved. Always inspect output quality, particularly for scans and small print. The project is not affiliated with PyMuPDF, Artifex or Qt.
