# PDF Compressor 2.7 — recombining the Windows one-file EXE with modified Qt

**This is a practical rebuild route, not a certification of LGPL/AGPL compliance.**

The default Windows distribution target remains a **single EXE**, including Python, PySide6 and Qt. A recipient who wants to use their own compatible rebuilt Qt libraries can independently recreate that EXE from the published application source using `tools/rebuild_onefile_with_qt.py`. This is a **relink/recombine** method rather than runtime sidecar DLL substitution.

## Requirements

- Windows 10/11 x64, Python **3.14**, Git and network access for Python wheels.
- Complete application source for the exact release commit (`release_windows_review.spec`, `app.pyw`, `pdf_engine.py`, `tools/`, `LICENSE`).
- Source and build instructions for Qt 6.12.0 and PySide6/Shiboken 6.12.0; all applicable libraries and notices. **The project has not yet established a complete, controlled corresponding-source package.**
- Your replacement `Qt6*.dll` or Qt plugin DLLs must be ABI-compatible with PySide6 6.12.0, Windows x64 and the toolchain. Modifying/compiling them is outside this script.

## Baseline reproducible rebuild

From a complete checked-out source tree, in PowerShell:

```powershell
py -3.14 tools\rebuild_onefile_with_qt.py --work-dir .\local-relink-build
```

This creates a fresh isolated virtual environment, installs exactly `PyMuPDF==1.27.2.3`, `PySide6==6.12.0`, `Pillow==12.3.0`, `pyinstaller==6.22.3`, rebuilds the same PyInstaller onefile spec, and checks the EXE archive.

The resulting EXE is `local-relink-build\dist\PDF_Compressor_2_7_license_review.exe`. The `build-manifest.json`, `bundle-audit.json` and `qt-relink-build-report.json` are next to it.

## Rebuild with recipient-compiled modified Qt DLLs

1. Obtain the matching Qt and Qt for Python source releases and apply your changes, complying with their licenses.
2. Build compatible Windows x64 Qt libraries (e.g., a replacement `Qt6Widgets.dll`) using the appropriate official Qt build instructions and compatible compiler.
3. Put the replacement DLLs in a folder mirroring their relative paths **within the installed `PySide6` package**, such as:

```text
my-modified-qt/
    Qt6Widgets.dll
    plugins/
        platforms/
            qwindows.dll
```

4. Rebuild:

```powershell
py -3.14 tools\rebuild_onefile_with_qt.py --qt-overrides .\my-modified-qt --work-dir .\modified-qt-rebuild
```

The tool refuses unknown or unmatched paths, empty replacements, non-DLL/PYD files and symlinks. It records the original and replacement SHA-256 for each overwritten library, then builds a **new single EXE** including the user's replacement binary. The isolated Python environment is recreated on each run so old modifications cannot silently persist.

5. Run the newly built EXE on Windows to verify the modified Qt library behaves as intended. You may distribute or use that rebuilt binary only under the applicable source/binary licenses.

**Limitations:** This script does not compile Qt, make an incompatible DLL compatible, provide all corresponding source archives, or prove source-code-modified Qt compatibility for arbitrary changes. The project must publish an exact matching source-and-notices package under its own control before certifying release readiness. A GitHub Actions test with stock libraries is not proof that every user modification will work.

Qt's official guidance: https://www.qt.io/development/open-source-lgpl-obligations and https://www.qt.io/faq/qt-open-source-licensing

## Current Windows build observations

The Windows onefile CI audit on commit `94eb41b6e852c167e96919983b168ecb170c4ac8` passed on [run 42477162772](https://github.com/Valik2005/pdf-compressor/actions/runs/42477162772). It excluded unused Qt PDF/QML/Quick and Virtual Keyboard DLLs, left the essential Qt Widgets/Core/Gui/Network/OpenGL/Svg libraries and started the UI headlessly. It does not exercise modification/rebuild behavior.

**Before public release, do not omit corresponding source, complete license texts, third-party native notices, replacement/relinking rights, installation information, or AGPL obligations for MuPDF.**

## Verified resource-modified library recombination (2026-11-08)

[Windows CI #42479642467](https://github.com/Valik2005/pdf-compressor/actions/runs/42479642467) **passed** on branch head `979a13290b7b554e6d05ded2debbe4e782727e47`:

1. Copied stock PySide6 6.12.0 `Qt6Widgets.dll` to an override directory.
2. Added an inert Windows PE `RCDATA` resource, yielding a *different real DLL file*; stock SHA-256 `2f62cbe2869fff4e20df7369c2786e1ec7ec290d5a63d1371b7f70cf06909c3f`, modified SHA-256 `a8f9cf537438f6f9e29c45bd75f97b06450db4fd61f347a23485296c70f1d431`.
3. Rebuilt PyInstaller onefile in a clean environment using `tools/rebuild_onefile_with_qt.py --qt-overrides`; resulting test EXE SHA-256 `50f38b09f50c7719a54cb72501dbd6cbd8dcb3a8c6c920a190c32035d271845f`.
4. Decompressed `PySide6/Qt6Widgets.dll` from the actual onefile CArchive and verified byte-for-byte SHA-256 match with the modified DLL.
5. Launched the repackaged EXE on Windows with Qt's offscreen platform; process stayed running through the smoke check.

**Scope of proof:** actual onefile repackaging, embedded DLL replacement and loading of an ABI-preserving resource-edited Qt DLL **are demonstrated**. This deliberately does **not** test recompiled Qt source changes, the full range of users' modifications, or independently establish LGPL licensing sufficiency. No altered DLL/EXE was published.
