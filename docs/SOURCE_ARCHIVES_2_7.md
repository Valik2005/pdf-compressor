# PDF Compressor 2.7 — corresponding-source acquisition (work in progress)

This page and the machine-readable catalog support **technical provenance tracking**, not a legal opinion, certification, or an offer to supply source code.

## Required candidate source archives for the reviewed 2.7 build

| Component | Exact release | Upstream source archive | Published SHA-256 independently captured? |
| --- | --- | --- | --- |
| PyMuPDF | 1.27.2.3 | [PyPI source distribution](https://pypi.org/project/pymupdf/1.27.2.3/) | **Yes**: 7a92faa25129e8bbec5e50eeb9214f187665428c31b05c4ef6e36c58c0b1c6d2 |
| Qt (full source) | 6.12.0 | [Qt 6.12.0 single source archive](https://www.qt.io/development/offline-installers) | **No**: hash needs independent capture/verification |
| PySide6 / Shiboken | 6.12.0 | [official source release](https://download.qt.io/official_releases/QtForPython/pyside6/) | **No**: hash needs independent capture/verification |
| QtBase (subset; optional reference) | 6.12.0 | [QtBase official checksum](https://download.qt.io/archive/qt/6.12/6.12.0/submodules/qtbase-everywhere-src-6.12.0.tar.xz.mirrorlist) | **Yes**: a951bd163c7b80fc6b8c88d7668fb56abf91c152373e13c10666763238131307 |

**Critical:** the QtBase subset is **not** complete Qt corresponding source; it does not include Qt PDF/PDFium, QML/Qt Quick and related modules. Using Qt 6.12.0 full source avoids overlooking Qt modules but is large (~423 MB compressed in .tar.xz; Qt Windows .zip ~577 MB). Even full Qt source may require additional third-party native sources and build instructions.

PyMuPDF sdist is the upstream release source; the audit must still establish that its native MuPDF code and transitive dependencies correspond to the exact wheel shipped in the EXE. A matching sdist archive alone is **not** proof of complete AGPL correspondence.

## Offline audit of local archives

Place the archives under a *private preparation folder*, not inside the EXE or the application repository. Then run:

```powershell
.\.venv\Scripts\python.exe tools\verify_source_archives.py --catalog docs\source-archives-2_7.json --source-dir .\release-source-candidates --out .\dist\source-evidence-report.json
```

To make missing/unverified required files fail with a nonzero exit code, add `--require-all-verified`.

The script checks **locally present archives only** and reads the expected SHA-256 values from the catalog. A null expected checksum is deliberately treated as *unverified*, even if the downloaded bytes appear intact. It never downloads large files silently.

## Source delivery and release obligations

Qt's official FAQ clarifies that relying only on an upstream Qt source URL does **not** automatically satisfy a distributor's obligation to provide corresponding Qt source; any offer needs to be under the distributor's control. See https://www.qt.io/faq/qt-open-source-licensing and https://www.qt.io/development/open-source-lgpl-obligations.

Before any public release:
- Collect full LGPL/GPL/AGPL license texts and appropriate notices, including Qt PDF/PDFium, native MuPDF, codecs and OpenSSL, not only short notices.
- Ensure a suitable controlled corresponding-source distribution or legally adequate written offer under the applicable licenses, including build/modification instructions and relevant changes, if any.
- Confirm a genuine path for recipients to use their own compatible modified Qt libraries, and test that method.
- Audit the exact final onedir/onefile build and reassess files if any packaged dependency version changes.

Neither a successful local hash audit nor a nonzero-exit-free run is permission to label the release license compliant.
