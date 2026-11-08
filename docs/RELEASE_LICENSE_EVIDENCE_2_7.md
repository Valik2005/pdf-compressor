# PDF Compressor 2.7 — license evidence for Windows review EXE

**Technical inventory, NOT legal advice or an authorization to distribute.** Updated 2026-11-08.

## Verified file

- `PDF_Compressor_2_7_license_review.exe`: 74,600,755 bytes
- SHA-256: `8b65cdaf950b8ca1598ee26791e69194a4979f5dd601738f732224d489b7bdca`
- PyInstaller archive: **304 entries; zero Virtual Keyboard components**.
- Maintainer reports Windows 11 application functions correctly.
- Bundled libraries still include Qt PDF, Qt Quick, Qt QML and supporting plugins as well as Qt Widgets.

**Manifest mismatch:** the uploaded `build-manifest(1).json` describes the **older** `PDF_Compressor_2_7_preview.exe` (SHA-256 `06c4a7fb...`, 74,773,982 bytes). It does **not** describe this newer executable. A freshly generated manifest is a builder-state inventory, not cryptographic proof of how an old EXE was compiled.

## Generate a matching audit and preliminary license evidence

Run PowerShell in the checkout with installed project dependencies:

```powershell
.\.venv\Scripts\python.exe tools\release_manifest.py --exe .\dist\PDF_Compressor_2_7_license_review.exe --out .\dist\license-review-build-manifest.json
.\.venv\Scripts\python.exe tools\audit_pyinstaller_bundle.py --exe .\dist\PDF_Compressor_2_7_license_review.exe --reject-virtual-keyboard --out .\dist\bundle-audit.json
.\.venv\Scripts\python.exe tools\collect_license_evidence.py --exe .\dist\PDF_Compressor_2_7_license_review.exe --manifest .\dist\license-review-build-manifest.json --out .\dist\license-evidence-not-for-release.zip
```

The collector gathers **only available local license-like files** from installed packages and the project license; it does not obtain corresponding library sources or prove rights to replace or relink Qt. It refuses to accept a manifest whose EXE hash/size do not match.

## Results of the actual evidence archive (2026-11-08)

The maintainer generated and supplied `license-evidence-not-for-release.zip`; the report matches the Virtual Keyboard-free EXE (SHA-256 `8b65cdaf950b8ca1598ee26791e69194a4979f5dd601738f732224d489b7bdca`, size 74,600,755 bytes).

The archive contains **9 collected files**, plus `README.txt` and `evidence-report.json`:

- Application: complete AGPLv3 license text (34,255 bytes).
- Python: `LICENSE.txt` (35,407 bytes).
- Pillow 12.3.0: package `LICENSE` (78,016 bytes; license and attribution material).
- PyInstaller 6.22.3: `COPYING.txt` (32,604 bytes; includes bootloader exception).
- PyMuPDF 1.27.2.3: `COPYING` **only 64 bytes**, stating dual licensing; no complete component-specific license/source documentation is supplied by that file.
- Four Qt for Python 6.12.0 distributions (`PySide6`, `PySide6_Essentials`, `PySide6_Addons`, `shiboken6`): each supplies the same **470-byte `LicenseRef-Qt-Commercial.txt`** text. None of those four collected files contains the complete applicable open-source LGPL/GPL license terms.

**Audit-tool defect found:** the initial evidence report showed `missing: []` because the collector counted short documents by filename and did not validate whether full license texts were present. This has now been corrected in the collector and covered by a test; its remaining obligations should be read as *missing compliance evidence*, not evidence of a violation.

The commercial reference file does **not** prove that these pip wheels require a paid Qt license; Qt for Python is available under open-source LGPL/GPL and commercial choices, depending on modules and obligations. See https://doc.qt.io/qtforpython-6/ and https://doc.qt.io/qt-6/licensing.html.

## Unresolved obligations before public release

1. **LGPL Qt components:** full applicable license terms, prominent notices, complete corresponding source/any modifications, and a practical user-compatible-library replacement/relinking method for the actual `--onefile` distribution. Merely pointing to a dynamic DLL inside the self-extracting archive is not conclusive. https://www.qt.io/development/open-source-lgpl-obligations
2. **Qt PDF / PDFium:** since Qt6Pdf.dll and qpdf.dll remain bundled, review their native PDFium/Chromium/codec third-party attributions. https://doc.qt.io/qt-6/qtpdf-licensing.html
3. **MuPDF / PyMuPDF (AGPL):** corresponding source for the relevant version, required producer/copyright notices and redistribution terms. https://pymupdf.io/licensing
4. **Additional native code:** OpenSSL, Python, Pillow codecs, Qt plugins and transitive libraries. The license text embedded in one package is not the complete set of notices.
5. **Final build:** freeze builder packages, rebuild on approved final source commit, capture SHA-256 and Windows smoke tests, and secure explicit approval before merging into `main` or publishing a GitHub Release.

**Status:** Virtual Keyboard removal is verified, but license compliance remains **unverified**. Do not label this release ready.
