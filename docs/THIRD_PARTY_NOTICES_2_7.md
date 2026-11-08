# PDF Compressor 2.7 — draft third-party notices / Уведомления о сторонних компонентах

**Draft for release preparation; NOT a complete redistribution-compliance certificate.**
This inventory must be reconciled with the exact final bundled binary and `dist/build-manifest.json`.

The application source is licensed under **GNU AGPL-3.0-only**. See the repository `LICENSE`.

| Component | Use in PDF Compressor | License / official source |
| --- | --- | --- |
| PyMuPDF and MuPDF (Artifex) | PDF reading, compression and editing | GNU AGPLv3 **or commercial license**; https://pymupdf.io/licensing |
| PySide6, Qt, PySide6_Essentials, PySide6_Addons, shiboken6 | Windows user interface | Qt libraries and bindings are offered under LGPL/GPL or commercial terms; exact module licenses vary. https://www.qt.io/development/open-source-lgpl-obligations and https://doc.qt.io/qt-6/licensing.html |
| Pillow | Raster image processing | HPND-like historical license; https://github.com/python-pillow/Pillow/blob/main/LICENSE |
| Python runtime | Application runtime | Python Software Foundation License; https://docs.python.org/3/license.html |
| PyInstaller bootloader/runtime | Freezing and bootstrapping executable | GPL with bootloader exception; https://pyinstaller.org/en/stable/license.html |

## Required release work / Обязательные действия перед публикацией

1. Record **the exact package versions** and inspect the contents of the final EXE (including Qt plugins, codecs and transitive native libraries).
2. Preserve license and copyright notices and make applicable **complete license texts** and source-code access / written offers available with the distributed binary. This inventory alone does not replace them.
3. Review the exact AGPL obligations, availability of Corresponding Source and preservation of any required MuPDF/PyMuPDF producer/copyright notices.
4. For every Qt library and plugin, identify its actual license. Confirm obligations concerning modification, replacement/relinking, reverse engineering for debugging LGPL modifications and corresponding library sources. A self-extracting `--onefile` distribution needs explicit review; the project source being published is **not automatically sufficient**.
5. Include notices for Python, Pillow, PyInstaller and all transitive dependencies actually bundled, not only the table above.
6. Confirm the distribution method meets these conditions; otherwise consider `--onedir` packaging with replaceable DLLs or a properly licensed commercial route. **Neither route is automatically certified by this document.**

Useful official documents: [Qt LGPL obligations](https://www.qt.io/development/open-source-lgpl-obligations), [PyMuPDF](https://pymupdf.io/licensing), [GNU AGPLv3](https://www.gnu.org/licenses/agpl-3.0.html), [PyInstaller](https://pyinstaller.org/en/stable/license.html).

## Current status / Текущий статус

As of 2026-11-08, notices have been **drafted**, but complete distribution-ready license text/source packages and the Qt `--onefile` replacement/relinking compliance path have **not** been verified. Do not label the EXE compliant or release-ready on this basis alone.

## Verified preview-bundle observations (2026-11-08)

The exact preview EXE SHA-256 `06c4a7fb17bf8747c7294cb9de5029cb9b430444d9adc0124d848f5ef81ce7fc` contains **Qt6VirtualKeyboard.dll**, **qtvirtualkeyboardplugin.dll** (Qt Virtual Keyboard: GPLv3/commercial), and **Qt6Pdf.dll** (PDFium and additional third-party notices). The only embedded notice-like filename observed is `pymupdf-1.27.2.3.dist-info/COPYING`; this is NOT a complete license inventory. See [actual binary audit](EXE_BUNDLE_AUDIT_2_7_PREVIEW.md) for technical evidence and release blockers.

