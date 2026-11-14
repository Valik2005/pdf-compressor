# PDF Compressor 2.8 — Qt LGPL user replacement and recombination

**This document is a practical technical route, not a legal-compliance certificate.**
It applies to the *public v2.8* Windows one-file EXE only after that release is approved and built from the reviewed, public source commit.

PDF Compressor v2.8 uses Qt 6.12.0 and PySide6/Shiboken 6.12.0 through LGPL/GPL licensing alternatives. A PyInstaller one-file EXE unpacks its native Qt binaries at runtime, but ordinary side-by-side DLL replacement may not work. Instead, the recipient can **rebuild the one-file EXE** with their own ABI-compatible Qt DLLs using this project's public source and the exact same versioned build recipe. This does not require the publisher's digital-signing key; the *modified EXE is expected to be unsigned*.

## Requirements

- Windows 10/11 x64; Python 3.14; Git, a working compiler if changing Qt's source, and access to Python wheels.
- Application source from **the exact final GitHub v2.8 release tag**, including `app.pyw`, `pdf_engine.py`, `pdf_quality.py`, `release_windows_2_8.spec`, `tools/windows_version_info_2_8.txt`, all `tools/`, the `LICENSE`, and relevant notices.
- Matching component source archives in the **same release's** `Third_Party_Sources_and_Licenses.zip`: QtBase, QtSvg, QtImageFormats, PySide6/Shiboken, PyMuPDF and MuPDF. Their SHA-256 values are pinned by the archive's manifest.
- For compiling modified Qt source, follow [official Qt 6 open-source obligations](https://www.qt.io/development/open-source-lgpl-obligations) and build instructions. Replacement DLLs **must be compatible** with the stock PySide6 6.12.0 bindings, Windows x64 and the toolchain.

## Rebuild without modifications (baseline)

In a PowerShell window from the complete source directory:

```powershell
py -3.14 tools\rebuild_onefile_with_qt.py --release-version 2.8 --work-dir .\rebuild-28
```

The script creates an isolated virtual environment, pins `PyMuPDF==1.27.2.3`, `PySide6==6.12.0`, `Pillow==12.3.0`, `pyinstaller==6.22.3`, and runs `release_windows_2_8.spec`. The rebuilt EXE is `rebuild-28\dist\PDF_Compressor_2_8.exe`. Audit files `bundle-audit.json`, `build-manifest.json` and `qt-relink-build-report.json` are created next to it.

A locally rebuilt binary is not expected to have a byte-identical SHA-256 to the SignPath-signed official release; signing and timestamping alter bytes, and build environments can vary.

## Rebuild with modified Qt libraries

1. Obtain and compile modified, ABI-compatible Qt DLLs/Qt plugins for the version above.
2. Place DLL/PYD files in a directory that mirrors their relative paths under the installed PySide6 package, for example:

```text
my-modified-qt/
  Qt6Widgets.dll
  plugins/
    platforms/
      qwindows.dll
```

3. Run:

```powershell
py -3.14 tools\rebuild_onefile_with_qt.py --release-version 2.8 --qt-overrides .\my-modified-qt --work-dir .\modified-rebuild-28
```

4. Inspect `modified-rebuild-28\dist\qt-relink-build-report.json` for replaced binary SHA-256 values and `bundle-audit.json` for the final native archive; run the EXE and test its UI and PDF functions.

The tool refuses unknown paths, symlinks, empty files and non-DLL/PYD overrides. It does not compile Qt for you. Qt 6.12 bindings and native plugin compatibility cannot be guaranteed for arbitrary changes.

## Prior technical evidence and limits

The historical Qt 6.12.0 one-file resource-edit replacement test, with replacement SHA-256 checks and Windows offscreen launch, succeeded in [GitHub Actions #42479642467](https://github.com/Valik2005/pdf-compressor/actions/runs/42479642467). This demonstrates PyInstaller recombination with an ABI-preserving native DLL change, **not** end-to-end recompilation from modified Qt source.

The corresponding-source/license pack for v2.8 must be independently audited before public distribution. Neither replacing library files nor these scripts alone establish compliance with every LGPL, GPL, AGPL, copyright, distribution or installation-information requirement. Users retain their applicable LGPL rights to modify and debug the Qt libraries.
