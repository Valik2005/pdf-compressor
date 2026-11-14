# PDF Compressor 2.8 — third-party supply-chain release review

**Scope:** Windows x64 onefile from `release_windows_2_8.spec` with pinned
PyMuPDF 1.27.2.3 / MuPDF 1.27.2, Qt and PySide6 6.12.0,
Pillow 12.3.0 and PyInstaller 6.22.3.

**Status: technical collection and integrity evidence established; full third-party legal compliance NOT certified.**
This is a maintainer pre-release review document, **not legal advice** or a license to redistribute missing software.

## Audits already performed

| Review | Verified technical evidence | Residual limit |
| --- | --- | --- |
| Windows application acceptance | [Run #43597586127](https://github.com/Valik2005/pdf-compressor/actions/runs/43597586127): both Python 3.13 and 3.14 Windows tests passed; final-version unsigned EXE built, metadata validated and GUI started | Not a signed binary, build SHA changes whenever the source changes |
| Source archive integrity | [Run #43596777350](https://github.com/Valik2005/pdf-compressor/actions/runs/43596777350): six pinned upstream tar archives downloaded and SHA-256 verified; 71 separate license/notice entries extracted | A source tarball matching a package version does not automatically prove matching compiler flags, dependencies or binary correspondence |
| LGPL DLL replacement | [Run #43596866323](https://github.com/Valik2005/pdf-compressor/actions/runs/43596866323): Qt6Widgets.dll altered in a PE resource, packed into the 2.8 onefile, extracted bytes verified, GUI launched | Resource changes are not the same as recompiling Qt after arbitrary source modifications |
| Windows native inventory | PyInstaller onefile archive audited; all DLL/PYD names classified; Qt Virtual Keyboard/PDF/QML/Quick omitted | Mapping categories by path cannot establish licenses for all codec/transitive code |
| Cross-commit pre-sign verification | `tools/verify_presign_evidence_28.py` validates exact Windows EXE SHA, clean source revision, builder package pins, six source archives, applicable NOTICE ZIP and the installed-package license report | Must pass for **the final main commit** again; no certificate was used during preflight |

## Components and documentation to preserve

- **Application:** `LICENSE` (GNU AGPL-3.0-only) and the complete public application source from the exact published tag. PDF documents processed locally; no user PDFs should be sent with the code-signing artifact.
- **PyMuPDF/MuPDF:** `pymupdf-1.27.2.3.tar.gz`, `mupdf-1.27.2-source.tar.gz`, AGPL terms, copyright and producer notices. Source and native engine versions should match the wheel actually shipped. Review Artifex licensing as applicable.
- **QtBase / QtSvg / QtImageFormats:** Qt 6.12.0 source archives, LGPL/GPL notices and third-party `src/3rdparty` notices. Published release contains `docs/LGPL_RELINKING_2_8.md` and `tools/rebuild_onefile_with_qt.py`, which let a recipient repack a onefile EXE with compatible changed Qt DLLs without the SignPath signing key.
- **PySide6/Shiboken:** Qt for Python 6.12.0 source release plus applicable LGPL/GPL text, not just the short commercial license reference in its pip wheel.
- **Pillow / codecs:** Pillow 12.3.0 wheel license and notices. Determine whether vendored JPEG/WebP/TIFF/PNG/codecs in the actual wheel require additional notices or corresponding sources.
- **Python runtime, PyInstaller bootloader, OpenSSL, Mesa and libffi:** include their license texts and attributable upstream source versions as applicable. Distinguish *system libraries* from independently bundled native redistributables.
- **Microsoft runtime:** determine the exact DLLs present and whether they fall within the GPLv3 system-library exception and applicable Microsoft redistribution terms. Do not characterize an unresolved proprietary DLL as eligible by default.

## Legal and SignPath requirements still requiring human confirmation

1. **LGPL 3 library replacement rights.** Confirm the release contains complete corresponding LGPL library sources, notices, and effective instructions to replace/recombine and run modified compatible Qt versions. The current automated test checks a resource-modified DLL, not a source-built modified Qt. See [Qt obligations](https://www.qt.io/development/open-source-lgpl-obligations).
2. **AGPL and other license compatibility.** Verify all required application/MuPDF notices, producer notices where applicable, corresponding source and license obligations for the precise shipped binary.
3. **Third-party embedded code.** Inspect the native inventory, upstream build options and individual license texts for every Qt/Pillow/OpenSSL/Mesa codec and plugin actually included; confirm any proprietary components qualify as bona fide system libraries or are excluded.
4. **SignPath eligibility.** SignPath's [OSS rules](https://signpath.org/terms) require qualifying open-source licensing, no prohibited proprietary payload, reproducible trusted build origin and manual signing approval. The terms also address commercially dual-licensed components. **Do not assume SignPath will accept Qt/PyMuPDF dependency licensing; SignPath itself must determine eligibility.**
5. **Product restrictions:** After approval, configure the **explicit** `SIGNPATH_ARTIFACT_CONFIGURATION_SLUG`; enforce `ProductName = PDF Compressor by Valik2005`, `ProductVersion = FileVersion = 2.8.0.0`, and the exclusive official `PDF_Compressor_2_8.exe` filename in SignPath.
6. **Final approval:** Re-run Windows acceptance + source notices + cross-commit provenance on the final source revision; inspect the actual signed EXE and SHA-256 after SignPath. Get maintainer's separate authorization before a public tag/release.

**Update 14 November 2026:** SignPath Foundation declined the free OSS signing application on public-recognition grounds. The current planned 2.8 release is **unsigned**. A SignPath eligibility determination is no longer a prerequisite for publishing unsigned software, but all independent third-party redistribution/license obligations remain mandatory.

**No paid certificate, legal certification or publisher identity is inferred from successful CI tests.** If any applicable license requirement remains unresolved, hold the public release and request competent OSS licensing review; do not waive it to meet a date.
