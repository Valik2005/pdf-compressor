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

## Unsigned 2.8 — release obligations and independent decision record

**Current policy:** SignPath Foundation declined the free OSS certificate application on 14 November 2026. The selected v2.8 candidate is **UNSIGNED**. SignPath eligibility, MFA or signing configuration are **not** unsigned-release prerequisites. The existing signed-only workflows are historical and must not be executed. The independent software licenses below still apply, signed or unsigned.

**What CI actually proves:** The original 118-native baseline is preserved for history; after PR #42 the intended Windows candidate has **115 native DLL/PYD members** (optional Qt OpenSSL TLS backend and two MySQL-sourced DLLs removed). exact wheel and installed-runtime bytes are checked, with an independent PyInstaller CArchive SHA/size cross-audit. As of PR #37, the Windows build additionally records the **actual PyInstaller Analysis source** of each native component, with only sanitized path categories. The same-commit release packager fails if those bytes do not match the packaged EXE. Six pinned source archives and applicable extracted original notices are hash-verified. None of this is a legal-compliance certification.

| Component | Available technical/notices evidence | Required final decision before distribution |
| --- | --- | --- |
| GNU AGPLv3 application and PyMuPDF/MuPDF | Public code, complete application AGPL license, MuPDF COPYING, pinned PyMuPDF and MuPDF archives; merge/extract operations credit MuPDF in newly created PDF producer metadata, while compression/rotation retain input metadata | Confirm corresponding source at exact final tag, copyright and attribution duties and producer behavior for the intended distribution; do not modify signed/input PDFs merely to insert metadata. See [Artifex](https://artifex.com/licensing) and [PyMuPDF](https://pymupdf.io/licensing) |
| Qt/PySide6/Shiboken 6.12.0 | Full LGPL/GPL texts and Qt source archives, explicit GUI licenses, existing Windows Qt DLL-repack demo and recipient relinking instructions | Confirm complete matching source and that a recipient can replace/modify/rebuild **compatible** Qt parts and run the updated onefile build; retain Qt third-party attributions. See [Qt open-source terms](https://doc.qt.io/qt-6.12/licensing.html) |
| Pillow 12.3.0 / image codecs | Exact installed-wheel full `LICENSE` (~78 KB), JPEG/WebP/AVIF/TIFF/PNG/LCMS/FreeType/Harfbuzz notices checked against actual wheel; six Pillow native components wheel-RECORD checked | Preserve the complete wheel notices; examine any changed dependency/codec set if the final binary deviates. Not currently an identified *missing-notice* gate |
| OpenSSL 3.5.9 | Full upstream LICENSE and AUTHORS and two retained `libcrypto-3.dll` / `libssl-3.dll` from installed CPython; two incidental MySQL OpenSSL `-x64` DLLs and the optional Qt TLS plugin were removed by PR #42 | Preserve applicable original Python/OpenSSL notices and verify all remaining bundled components against the same-source release artifact, rather than including unrelated MySQL copies. See [OpenSSL 3.5.9 notes](https://www.openssl-library.org/news/openssl-3.5-notes/index.html) |
| Qt Mesa llvmpipe / possible LLVM | `PySide6/opengl32sw.dll` byte-identical to the PySide6 wheel, named llvmpipe attribution and full MIT/Boost 1.0 notices in shipped sources ZIP | Confirm that notices are sufficient for the **actual** wheel binary, including any LLVM copy if compiled in. See [Qt Mesa documentation](https://doc.qt.io/qt-6.12/windows-graphics.html) and [Qt third-party terms](https://doc.qt.io/qt-6/licenses-used-in-qt.html) |
| libffi and Python/PyInstaller | Native `libffi-8.dll` and Python runtime inventory; libffi, PSF, PyInstaller license evidence | Confirm the captured collection source and any copy-specific notice/exception requirements |
| Microsoft C++/UCRT | 42 UCRT API-set DLLs, one `ucrtbase.dll`, ten MSVCP/VCRUNTIME copies; matches for all ten copies established; the collection-source report identifies actual builder source categories | Verify applicable **Microsoft license and REDIST/Windows SDK redistribution rights** for these exact files and the maintainer's eligible license. App-local UCRT is a supported deployment option, not unrestricted permission. See [Microsoft UCRT](https://learn.microsoft.com/en-us/cpp/porting/upgrade-your-code-to-the-universal-crt), [Visual Studio REDIST](https://learn.microsoft.com/en-us/visualstudio/releases/2022/redistribution) and [licensing guidance](https://www.microsoft.com/licensing/guidance/Visual-Studio) |

### Explicit decisions still pending

- [ ] Independent component-specific redistribution review is completed and recorded, including Windows SDK/Visual Studio eligibility, OpenSSL, Qt, MuPDF and other upstream notices. Any applicable GPL/AGPL **System Library** exception is assessed independently from Microsoft's copyright permission.
- [ ] Verify the last isolated release-candidate **same-commit** Windows 3.13/3.14 tests, real onefile startup, cross-source byte hashes, six upstream archives, Qt license notices and exactly three *private* unsigned staging assets.
- [ ] The maintainer separately authorizes merging draft release PR #17 into `main`; nobody may infer this authorization from green CI.
- [ ] After the authorized merge, rerun the complete six-job acceptance on the *exact new main SHA* and independently verify final EXE `NotSigned` and SHA256SUMS. The maintainer separately authorizes publication, with the truthful `LICENSE_OBLIGATIONS_REVIEWED` confirmation.
- [ ] Only the owner's manual `publish-v2_8-unsigned.yml` may create the public release. Post-publication README PR #29 is merged **only after** all three public assets exist and hashes match.

**No paid certificate is necessary for the selected unsigned path, and no copyright permission, compliance guarantee, publisher identity or public-release authorization can be inferred from technical green checks.** Keep release on hold if any material applicable license obligation cannot be verified.
