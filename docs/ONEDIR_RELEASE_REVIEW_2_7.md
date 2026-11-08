# Experimental onedir build with external Qt libraries (Windows)

**NOT a release-approved build.** The maintainer previously preferred a single EXE in GitHub releases, so this alternative is a trial for LGPL replacement rights, not an approved distribution change.

Qt's LGPL guidance requires prominent notices, complete corresponding source or a permissible offer, and ability to run compatible modified libraries. A one-folder EXE with external Qt DLLs can simplify replacement, but does **not by itself meet every requirement**.

Official guidance: https://www.qt.io/development/open-source-lgpl-obligations
Qt 6.12 licenses: https://doc.qt.io/qt-6.12/licensing.html

## Build and inspect on Windows 11

From the repository checkout:

```powershell
git fetch origin
git switch release/2.7-bundle-audit
git pull --ff-only origin release/2.7-bundle-audit
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean release_windows_onedir_review.spec
.\.venv\Scripts\python.exe tools\verify_onedir_bundle.py --bundle-dir .\dist\PDF_Compressor_2_7_onedir_review --out .\dist\onedir-audit.json
.\dist\PDF_Compressor_2_7_onedir_review\PDF_Compressor_2_7_onedir_review.exe
```

Expected structure, with external libraries next to the executable under _internal:

```text
dist/
  PDF_Compressor_2_7_onedir_review/
    PDF_Compressor_2_7_onedir_review.exe
    _internal/
      PySide6/
        Qt6Core.dll
        Qt6Gui.dll
        Qt6Widgets.dll
        plugins/
          platforms/
            qwindows.dll
      ...
```

The source code imports PySide6.QtCore, QtGui and QtWidgets. Other libraries (Qt PDF, QML and Qt Quick) appear in the current bundle via dependencies; do **not** delete them until separately verified on Windows.

## What is and is not proven

- Audit checks that key Qt binaries are external and that Virtual Keyboard files are absent; it also checks for PySide6 binary payloads embedded in the main EXE.
- Windows runtime must still be tested.
- This does NOT test actually loading a compatible user-modified Qt DLL. A valid replacement demonstration still requires an appropriately built compatible modified DLL and functional testing.
- This does NOT provide license texts, full corresponding source or every third-party notice.

## Corresponding source acquisition — specific versions

- **Qt 6.12.0:** official source release https://www.qt.io/development/offline-installers ; Qt source ZIP for Windows approximately 577 MB. See also https://download.qt.io/archive/qt/6.12/ .
- **PySide6 and Shiboken 6.12.0:** official source release directory https://download.qt.io/official_releases/QtForPython/pyside6/ .
- **PyMuPDF 1.27.2.3 and bundled native MuPDF:** https://github.com/pymupdf/PyMuPDF/releases ; review the bundled native version and all source obligations.
- **Qt PDF/PDFium:** Qt PDF LGPL/GPL licensing with PDFium and transitive BSD/Apache/MIT/other notices: https://doc.qt.io/qt-6/qtpdf-licensing.html .
- **Other native components:** Python runtime, Pillow codecs, OpenSSL, other Qt plugins. Their notice and corresponding source requirements depend on exact versions.

Until the entire source/notice/relinking requirement is reviewed, the onedir candidate is **only a technical experiment**, not a legally approved release. Do not merge to main or publish without explicit maintainer authorization.

## First automated Windows build check

GitHub Actions run [42470112055](https://github.com/Valik2005/pdf-compressor/actions/runs/42470112055) successfully built the onedir candidate on Windows with the pinned reviewed versions. Its external-DLL audit found **40 Qt DLLs** and **zero Qt Virtual Keyboard components**. The build-runner EXE is not the same file or SHA-256 as the locally reviewed onefile EXE; this run uploaded only an audit JSON, not an executable distribution. An additional automated GUI-startup smoke check is now being added to the workflow; Windows user-facing runtime checks remain separate.

## Automated Windows status and native-file provenance (2026-11-08)

- [Windows onedir build and offscreen GUI startup #42470397048](https://github.com/Valik2005/pdf-compressor/actions/runs/42470397048) passed: 40 external Qt DLLs, no Virtual Keyboard files, and GUI process stayed alive for four seconds. No PDF processing was exercised in this check.
- [Source tests #42470402192](https://github.com/Valik2005/pdf-compressor/actions/runs/42470402192) passed: 59 tests on each of Python 3.13 and 3.14.
- The updated read-only onedir audit (schema 2) records relative path, size, and SHA-256 for each external native DLL/PYD/EXE and separately reports Qt PDF, QML and Quick module observations. This makes the actual binary contents traceable; it is **not** an SBOM, source-code delivery, license verification, or proof that a modified Qt DLL can run.
- Re-run the Windows workflow on the updated commit before relying on schema 2 results. No final release binary is approved.

### Manual release gate

1. Build the exact reviewed commit and preserve the full folder tree. A one-folder build is **not** a single standalone EXE; do not distribute only its EXE.
2. On Windows 10/11, test text/scanned/mixed PDF compression, strict target size, batch jobs, cancellation, merge, extract, rotate, themes and RU/EN. Check generated PDFs and source-file integrity.
3. Demonstrate that a compatible rebuilt/modified Qt DLL can be substituted and that the program still functions, recording exact build instructions and before/after SHA-256 values. Merely placing DLLs outside the EXE does not prove this.
4. Reconcile the per-file native manifest with full notices, matching corresponding sources, license texts and all Qt PDF/PDFium and MuPDF dependencies.
5. Decide whether changing the previously requested **single-EXE** release format is acceptable. If not, the onefile compliance path remains a separate unresolved gate.

Do not publish or merge into stable until the above conditions and maintainer approval are satisfied.
