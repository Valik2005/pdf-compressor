# PDF Compressor 2.7 — audit of the 2026-11-08 preview EXE

**Technical inventory, not legal advice or an approved public-release certificate.**

The binary was inspected directly, without running it, using the PyInstaller cookie and TOC format.

- **SHA-256:** 06c4a7fb17bf8747c7294cb9de5029cb9b430444d9adc0124d848f5ef81ce7fc
- **Size:** 74,773,982 bytes
- **Source commit (builder manifest):** 7738001f2476226c4ea10efb7ee27d705df4cd86; dirty = false
- **Python:** 3.14.10; PyMuPDF 1.27.2.3; PySide6 6.12.0; Pillow 12.3.0; PyInstaller 6.22.3.
- **Archive:** 306 TOC entries, 54 DLLs and 28 PYDs.

## Exact findings

The archive contains both of these:

- `PySide6/Qt6VirtualKeyboard.dll`
- `PySide6/plugins/platforminputcontexts/qtvirtualkeyboardplugin.dll`

**Qt Virtual Keyboard uses GPLv3 or commercial licensing** (not the LGPL variant for common Qt widgets). This does not establish a license violation: a GPL-compatible open-source application can potentially distribute it while satisfying the relevant terms. It is unnecessary for this desktop application and we should avoid shipping it if exclusion does not break the executable. See [official Qt Virtual Keyboard documentation](https://doc.qt.io/qt-6/qtvirtualkeyboard-index.html).

The bundled archive also contains `PySide6/Qt6Pdf.dll` and `qpdf.dll`; Qt PDF contains PDFium and relevant third-party license notices. See [Qt PDF licensing](https://doc.qt.io/qt-6/qtpdf-licensing.html).

The only notice-like filename in the archive was `pymupdf-1.27.2.3.dist-info/COPYING`. This does not prove that all license texts are absent from the **distribution** (they could be provided separately), but the uploaded pair of files did not include a complete separate notices/source package.

## Experimental rebuild — NOT for publication

```powershell
git switch release/2.7-bundle-audit
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean release_windows_review.spec
.\.venv\Scripts\python.exe tools\\audit_pyinstaller_bundle.py --exe .\dist\PDF_Compressor_2_7_license_review.exe --reject-virtual-keyboard --out .\dist\bundle-audit.json
```

The spec only removes Qt Virtual Keyboard library/plugin assets and leaves other dependencies unchanged. It has **not been Windows-built or runtime-tested**. A successful audit confirms file absence, not runtime or license compliance; smoke-test the new binary separately before accepting the recipe.

## Remaining blockers

1. Supply complete applicable notices and license texts for all **actually bundled** Qt modules/plugins, Qt PDF/PDFium/third-party components, MuPDF, Python/Pillow/PyInstaller and native libraries.
2. Verify rights for user replacement/relinking of LGPL libraries in the chosen `--onefile` distribution, or document and provide a compliant rebuild path with corresponding source/application code and installation information.
3. Provide adequate corresponding source or maintainer-controlled offers as required by applicable AGPL/GPL/LGPL terms. A bare upstream link may be insufficient.
4. Perform final Windows tests, record final versions and a **new** binary SHA-256 after any rebuild.
5. Obtain explicit maintainer approval before merging into `main` or publishing v2.7.0.

Official docs: [Qt licensing](https://doc.qt.io/qt-6/licensing.html), [Qt LGPL obligations](https://www.qt.io/development/open-source-lgpl-obligations), [PyMuPDF licensing](https://pymupdf.io/licensing), [PyInstaller spec files](https://pyinstaller.org/en/latest/spec-files.html).
