# PDF Compressor 2.6

[Русская версия README](README_RU.md)

**Offline PDF compressor and page toolkit for Windows**, written in Python and PySide6. The interface supports **English and Russian**, dark/light themes, and batch processing.

> All files are processed locally. The application does not upload documents to a cloud service.

## Features

- Compress one or multiple PDFs with four presets: target file size, highest quality, balanced, and maximum compression.
- Try lossless optimization before recompressing embedded images.
- Preserve selectable/vector PDF text where possible; page images may undergo lossy JPEG recompression.
- Display processing progress, support cancellation, and summarize resulting file sizes.
- Preview source and output pages side by side (zoom, page navigation, preview rotation).
- Merge PDFs; split/extract selected pages; rotate document pages without recompressing page images.
- Select output directory and filename template; remember language, theme, and settings.
- Preserve original documents: output is written to new files.

**Important:** A requested size such as 1 MB is a goal, **not a guarantee**. PDFs already optimized or containing complex content may not reach the goal without reducing image quality/resolution. Modifying a PDF may invalidate digital signatures; the program includes safeguards for signed documents.

## Download the Windows EXE (no Python required)

After the first Windows build has completed, go to **Actions → Windows EXE and Release → latest successful run → Artifacts** and download `PDF_Compressor_2_6-Windows-x64`. Extract the ZIP to get **`PDF_Compressor_2_6.exe`**.

To distribute the EXE through **Releases**, run **Actions → Windows EXE and Release → Run workflow**, specify `v2.6.0`, and inspect the **draft Release**. Once third-party license obligations have been reviewed, the draft can be published so users can download the EXE directly from **Releases → Assets**. The workflow builds the EXE on Windows; it is not checked in as source code.

[Русская инструкция по EXE и публикации](EXE_RELEASE_GUIDE_RU.md)

## Windows installation

Requires Python **3.11 or newer**; Python 3.14 is supported by the pinned dependency ranges.

1. Download the repository as a ZIP (Code → Download ZIP) and extract it.
2. Run **`Установить_и_запустить.bat`** to install dependencies and start the app.
3. Alternatively, in PowerShell or CMD run:

   ```bat
   python -m pip install -r requirements.txt
   python app.pyw
   ```

4. Choose language (**Русский / English**) from the top toolbar. Your preference persists after restart.

For later GUI launches without a console, double-click `app.pyw` (with `.pyw` associated with Python).

## Build a standalone Windows EXE

Double-click **`Собрать_EXE.bat`**, or use PyInstaller manually. The batch script installs its dependencies and creates:

```text
dist\PDF_Compressor_2_6.exe
```

Build on Windows to produce a Windows EXE. The executable is not included in the source repository; GitHub Actions builds it and can attach it to a release.

## Run tests

```bat
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Tests cover PDF manipulation and translation dictionary integrity. GUI appearance is platform- and DPI-dependent and should be checked manually on Windows.

## Repository layout

```text
app.pyw                   Desktop application and bilingual UI
pdf_engine.py             PDF optimization and page operations
app_icon.ico              Windows application icon
requirements.txt          Runtime dependencies
tests/                    Engine and localization tests
Установить_и_запустить.bat  Windows installer / launcher
Собрать_EXE.bat           Windows EXE build script
README_RU.md              Русская инструкция
Publish_to_GitHub.bat     Guided GitHub publisher
.github/workflows/windows-exe.yml  Automatic Windows EXE build and draft release
```

## Licensing note

**PyMuPDF uses AGPL-3.0 or a commercial license**, so distributing an application built on its open-source version has corresponding obligations. PySide6 uses LGPL/GPL/commercial licensing options. Review these obligations before releasing redistributed binaries or declaring the application proprietary. See [DEPENDENCIES_AND_LICENSING.md](DEPENDENCIES_AND_LICENSING.md). The repository does not include third-party library source code.

## Disclaimer

Use backups of important documents. Compression with JPEG is lossy for images, even if the page resolution is preserved. This project is not affiliated with PyMuPDF, Artifex or Qt.
