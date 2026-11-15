# PDF Compressor 2.8 — Qt LGPL user replacement and recombination

**This document is a practical technical route, not a legal-compliance certificate.**
It applies to the *public v2.8* Windows one-file EXE only after that release is approved and built from the reviewed, public source commit.

PDF Compressor v2.8 uses Qt 6.12.0 and PySide6/Shiboken 6.12.0 through LGPL/GPL licensing alternatives. A PyInstaller one-file EXE unpacks its native Qt binaries at runtime, but ordinary side-by-side DLL replacement may not work. Instead, the recipient can **rebuild the one-file EXE** with their own ABI-compatible Qt DLLs using this project's public source and the exact same versioned build recipe. This does not require a code-signing key; **both the planned official 2.8 release and user-rebuilt EXEs are unsigned**.

## Requirements

- Windows 10/11 x64; Python 3.14; Git, a working compiler if changing Qt's source, and access to Python wheels.
- **Selected 62-native Windows release candidate:** the **official Microsoft Visual C++ Redistributable x64 is required separately**. The original candidate contains zero Microsoft MSVC/UCRT/API-set DLLs and the recipient rebuild process must preserve that same packaging property. The maintainer successfully launched the selected build on Windows 11 build 26200 with the official VC++ x64 runtime installed.
- Application source from **the exact final GitHub v2.8 release tag**, including `app.pyw`, `pdf_engine.py`, `pdf_quality.py`, `release_windows_2_8.spec`, `tools/windows_version_info_2_8.txt`, all `tools/`, the `LICENSE`, and relevant notices.
- Matching component source archives in the **same release's** `Third_Party_Sources_and_Licenses.zip`: QtBase, QtSvg, QtImageFormats, PySide6/Shiboken, PyMuPDF and MuPDF. Their SHA-256 values are pinned by the archive's manifest.
- For compiling modified Qt source, follow [official Qt 6 open-source obligations](https://www.qt.io/development/open-source-lgpl-obligations) and build instructions. Replacement DLLs **must be compatible** with the stock PySide6 6.12.0 bindings, Windows x64 and the toolchain.

## Rebuild without modifications (baseline)

In a PowerShell window from the complete source directory:

```powershell
py -3.14 tools\rebuild_onefile_with_qt.py --release-version 2.8 --work-dir .\rebuild-28
```

The script creates an isolated virtual environment, pins `PyMuPDF==1.27.2.3`, `PySide6==6.12.0`, `Pillow==12.3.0`, `pyinstaller==6.22.3`, and runs `release_windows_2_8.spec`. The rebuilt EXE is `rebuild-28\dist\PDF_Compressor_2_8.exe`. Audit files `bundle-audit.json`, `build-manifest.json` and `qt-relink-build-report.json` are created next to it.

A locally rebuilt binary is not guaranteed to have an identical SHA-256 to the official **unsigned** build because compiler, packaging environment and embedded build metadata may differ. The official release SHA-256 refers only to the published build, not to all compatible rebuilt copies.

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

4. Inspect `modified-rebuild-28\recipient-qt-relink-manifest.json` for the **original wheel SHA-256 and exact replacement SHA-256 of every modified Qt DLL**. The build script generates this manifest automatically after copying your specified modified DLL into an isolated virtual environment; you do **not** need to edit Qt's installed wheel RECORD or hand-write a legal waiver. Then inspect `modified-rebuild-28\dist\qt-relink-build-report.json` and `bundle-audit.json` for the final onefile bytes; run the EXE and test its UI and PDF functions.

The tool refuses unknown paths, symlinks, empty files and non-DLL/PYD overrides. It does not compile Qt for you. Qt 6.12 bindings and native plugin compatibility cannot be guaranteed for arbitrary changes.

**Integrity guarantees:** The normal release builder still requires every installed-wheel DLL to match its original `dist-info/RECORD`. A **recipient rebuild only** passes an extra manifest to the PyInstaller source auditor for the exact DLL names and original/replacement hashes declared by the user; unrelated DLL changes are still rejected. That source audit explicitly records `recipient_qt_relink=true` and `recipient_modified_qt_count`. Conversely, the official unsigned release cross-check **rejects** any `recipient_qt_relink` or `recipient_modified_qt` value, so the official three-file release can never silently include a modified-wheel exception. The changed EXE is a user rebuild, not an official authenticated release.

## Prior technical evidence and limits

**Recipient Qt replacement proof for the same spec (historical ancestor; not a proof of source-code-modified Qt ABI):** [GitHub Actions run #43658575876](https://github.com/Valik2005/pdf-compressor/actions/runs/43658575876) on isolated release-branch commit `8d65e64808c04b93cc8e4fec41de2744ee5af6c4` **passed** on Windows: a PE-resource-modified `Qt6Widgets.dll` was injected into the isolated Qt 6.12.0 wheel; the declared original/replacement SHA manifest allowed that exact recipient override, the actual onefile embedded modified DLL SHA-256 matched `a8f9cf537438f6f9e29c45bd75f97b06450db4fd61f347a23485296c70f1d431`, and the Qt GUI launched offscreen. The unsigned EXE's overall SHA-256 was recorded independently in CI. The original strict release-source/EXE audit remains separately tested; **this verifies ABI-preserving recombination, not source-code-modified Qt compatibility or legal compliance**.

For historical comparison, [GitHub Actions #42479642467](https://github.com/Valik2005/pdf-compressor/actions/runs/42479642467) previously tested similar ABI-preserving replacement on an older branch. The latest run above specifically uses the current `release_windows_2_8.spec`.

The corresponding-source/license pack for v2.8 must be independently audited before public distribution. Neither replacing library files nor these scripts alone establish compliance with every LGPL, GPL, AGPL, copyright, distribution or installation-information requirement. Users retain their applicable LGPL rights to modify and debug the Qt libraries.

## Current selected release-candidate limitations (15 November 2026)

The selected candidate has **62** native DLL/PYD members, not 115. Before relying on these instructions for a final published `v2.8`, verify the final source tag, compiler/wheel versions, package manifest and full license/source archive are identical in scope to the published EXE. A user-built replacement Qt DLL requires an ABI-compatible Qt 6.12.0 and must not be prevented from running or debugging with the changed DLL. Never treat a complete-EXE SHA mismatch on a rebuilt EXE as a reason to suppress the recipient's LGPL rights. Standard Windows application-security policies may block unknown unsigned executables; this is not a license to weaken device security. Public distribution requires a separately authorized corresponding-source/compliance review.
