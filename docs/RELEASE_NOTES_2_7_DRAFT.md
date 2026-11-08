# PDF Compressor 2.7.0 — release notes (prepared; NOT published)

**Status:** Release candidate preparation. The public stable version remains 2.6.0. This document is not permission to distribute an EXE.

## Improvements since 2.6

- SmartFit analyzes document structure (digital text, scans, mixed pages) and selects conservative compression attempts.
- Optional image downscaling only when explicitly enabled; shared image placements are taken into account.
- Reduced redundant JPEG quality and DPI passes in relevant cases.
- More responsive document-list layout when maximized.
- PDF merge, page extraction and rotation, cancellation and output naming improvements.
- Russian and English UI, offline processing, and original-file preservation.

## Known limitations

- A requested target file size may be impossible without unacceptable image loss; the application reports when the target is not achieved.
- Text extraction checks do not guarantee visual fidelity of scanned handwriting, seals, or tiny print.
- No OCR or full PDF text editing.

## Verified candidate evidence (2026-11-08)

- Windows source tests [#42474009443](https://github.com/Valik2005/pdf-compressor/actions/runs/42474009443) passed at commit `31e32c7` (Python 3.13 and 3.14).
- Experimental **onedir** Windows build and headless GUI smoke [#42474004817](https://github.com/Valik2005/pdf-compressor/actions/runs/42474004817) passed at commit `31e32c7`.
- That onedir run uploaded artifact `onedir-layout-audit` ID `13614118024`, with native SHA-256 inventory and no Qt Virtual Keyboard. This is **not** the requested one-file release build.
- Recovered and independently SHA-256-verified the maintainer-supplied Windows onefile candidate `PDF_Compressor_2_7_license_review.exe` (74,600,755 bytes; SHA-256 `8b65cdaf950b8ca1598ee26791e69194a4979f5dd601738f732224d489b7bdca`). Its matching archive audit reports 304 PyInstaller entries and no Virtual Keyboard. This is an **existing review candidate**, not a newly built final release binary.
- Recovered the matching `license-evidence-not-for-release.zip`: its report explicitly states `INCOMPLETE EVIDENCE ONLY; NOT approved for redistribution`; short Qt commercial reference files and a short PyMuPDF notice do not replace the required full license/source materials.
- Earlier local Windows preview EXE, PDF operations, batch behavior and cancellation were manually checked. These are historical tests of a preview, **not** certification of a new final executable.

## Mandatory conditions before public v2.7.0

1. Select and document a legally supportable **single-EXE** Qt LGPL replacement/relinking mechanism, or explicitly agree on a different distribution format.
2. Complete applicable third-party license texts, notices and matching corresponding-source delivery for the exact final package, including PySide6/Qt, Qt PDF/PDFium, PyMuPDF/MuPDF and transitive components.
3. Build the actual final binary from a frozen environment and final source commit; capture a matching manifest and SHA-256.
4. Confirm that the actual final executable launches and loads its bundled libraries on a clean Windows installation.
5. Review integration into `main` and authorize GitHub Release publication only after the blockers are closed.

**No official 2.7 EXE, tag or GitHub Release has been published by this document.**
