> **CURRENT OWNER-SELECTED v2.8 (15 Nov 2026):** The isolated release branch now contains the **62-native** Windows x64 version (no embedded Microsoft MSVC/UCRT/API-set DLLs). Source ancestor `392ddd30`; merged release branch `8317b588`. The owner independently ran the exact Windows 2025 artifact EXE SHA-256 `00a878796abad875546c556db63e9bb18af3137e3f7226c6610b1deb91a4b166` on Windows 11 build 26200: official Microsoft VC++ Redistributable x64 v14.51.36247.00 present, GUI smoke passed, Licenses dialog opened. User acceptance of the functional PDF compression engine was recorded separately on 14 Nov using 2.8.1 Testing; no compression-code change is part of this packaging. The `ca56a3e2...` sibling same-source review EXE had all 62 DLL/PYD bytes equal to the user-tested EXE but a different whole-file SHA; never represent one as the other. Current release-branch commits after `392ddd` require same-commit CI before publication. No merge into `main`, no public tag, and no legal license approval is implied. 115-native and older inventories below are **historical, not current candidate contents**. The EXE requires the *separately installed* official Microsoft VC++ Redistributable x64; this build does **not** redistribute Microsoft runtime DLLs. Third-party LGPL/AGPL/Mesa/LLVM/other obligations and separate owner authorization remain prerequisites to a public release. Smart App Control may block unsigned EXEs; do not weaken user security to bypass it.

# PDF Compressor 2.8 — component license audit (verified artifacts)

**Date:** 14 November 2026  
**Historical baseline binary (NOT the current release candidate):** Windows x64 PyInstaller onefile, UNSIGNED, SHA-256
`1c403790119f2ca8389efe360578e963e3f95e3b4b68d7c6e73ecfbaae95c39b`,
source commit `09e1b73b74c7dbf04fddd8a576f0c78fae50365d`.
The release candidate has since changed; do **not** use this historical SHA or source commit for publication. The final three release files must be generated and reverified from the exact accepted `main` commit.
GitHub Actions: [successful same-commit run #43599279025](https://github.com/Valik2005/pdf-compressor/actions/runs/43599279025)
([Windows artifact](https://github.com/Valik2005/pdf-compressor/actions/runs/43599279025/artifacts/14116470122),
[upstream source/notice artifact](https://github.com/Valik2005/pdf-compressor/actions/runs/43599279025/artifacts/14116270695),
[pre-sign evidence](https://github.com/Valik2005/pdf-compressor/actions/runs/43599279025/artifacts/14115826992)).
This SHA refers **only** to the reviewed, unsigned build. **Re-run every check after changes and again for the final main revision**.

This report is a technical bill-of-materials and obligations review, **not a legal opinion or redistribution compliance certificate**.

## Updated release-candidate contents after PR #42 (no MySQL OpenSSL)

The older inventory below is a **historical 118-member baseline**. It is not the
binary planned for the final unsigned v2.8 release.

On [PR #42](https://github.com/Valik2005/pdf-compressor/pull/42), the
GitHub runner's accidental `MySQL/MySQL Server 8.4/bin/libssl-3-x64.dll`
and `libcrypto-3-x64.dll` were traced by SHA-256 and **excluded**, along
with unused `PySide6/plugins/tls/qopensslbackend.dll`. The application
is offline; the Python-provided `libssl-3.dll`, `libcrypto-3.dll` and
`_ssl.pyd` remain, as do Qt's other TLS backends.

Two independently built Windows Server 2022/2025 experimental EXEs each
had **115 native DLL/PYD entries**, zero MySQL-sourced OpenSSL DLLs,
**205/205 regression tests passing**, 115/115 per-member provenance
verification and a successful GUI startup:
[Actions #43650917328](https://github.com/Valik2005/pdf-compressor/actions/runs/43650917328).

The current isolated release branch must also pass complete **six-job**
same-commit source/archive/native cross-audit and three-file staging after
PR #42 and its fail-closed verification change are merged. These technical
results do not establish Microsoft MSVC/UCRT redistribution eligibility,
MuPDF AGPL or Qt LGPL legal compliance, or grant permission to publish.

## Historical pre-PR42 facts (preserved for audit traceability)

- Actual onefile inventory: **118 native DLL/PYD entries**. Group counts: QtBase 18, QtSvg 3, QtImageFormats 5, PySide6/Shiboken 7, PyMuPDF 1, MuPDF 2, Pillow codecs 6, OpenSSL 4, Mesa software renderer 1, libffi 1, Python 17, and Microsoft runtime **53**.
- Of those 53 Microsoft entries, **42** are `api-ms-win-*.dll` API sets, **10** are MSVCP/VCRUNTIME copies inside root/PySide6/shiboken6, and **1** is `ucrtbase.dll`. API-set attribution **does not establish redistributability** for the 11 other files.
- Four separate OpenSSL native libraries found: `libcrypto-3-x64.dll`, `libcrypto-3.dll`, `libssl-3-x64.dll`, `libssl-3.dll`. Exact original OpenSSL 3.5.9 license and authors files are now added to the next notice pack; the four DLLs' **precise build origins and any additional copyright obligations remain unverified**.
- The following were **not** present in the inspected native DLL/PYD bundle: QtPdf, PDFium, QtQuick, QtQml, QtVirtualKeyboard, Chromium/WebEngine. Do **not** require PDFium or Chromium source/notice as a condition for *this* trimmed build unless a future final audit detects their return.
- Six upstream archives are present and SHA-256 checked: PyMuPDF 1.27.2.3, MuPDF 1.27.2, Qt for Python 6.12.0, QtBase 6.12.0, QtSvg 6.12.0, QtImageFormats 6.12.0. **SHA-256 of an upstream source archive is not proof of the binary being compiled from that exact archive.**
- The verified unsigned run [#43618672798](https://github.com/Valik2005/pdf-compressor/actions/runs/43618672798) included **71 entries**; after adding original OpenSSL 3.5.9 LICENSE and AUTHORS, the same-commit run [#43619807237](https://github.com/Valik2005/pdf-compressor/actions/runs/43619807237) included **73 entries**, including full project **AGPLv3**, MuPDF `COPYING`, full Qt/PySide6 **LGPLv3 and GPLv3** texts, QtBase/QtSvg/QtImageFormats third-party texts, and libffi notice. `license-evidence.zip` separately contains Windows-builder installed-wheel documentation for Pillow, Python, PyInstaller, PyMuPDF and PySide6/Shiboken. For the Qt wheels, only `LicenseRef-Qt-Commercial.txt` was directly extractable from the installed wheel metadata: the Qt **open-source** full-text licenses are in the **other** notice archive, not in those wheel metadata records.
- Exact original→compressed sample PDFs #04 and #10 retain their original Creator metadata, but both original and result PDF `Producer` values were empty. This **does not by itself prove an AGPL violation**; Artifex producer/copyright notice requirements should be confirmed and guarded by a dedicated test before changing the compression pipeline.

## Exact Windows library byte-origin results (new audit)

The dedicated [six-job review-only run #43628766396](https://github.com/Valik2005/pdf-compressor/actions/runs/43628766396) independently read **all 118 DLL/PYD members from the EXE** and compared their uncompressed SHA-256 values with the Windows builder's installed wheels/CPython:
- **73/118** native members are *byte-identical* to installed PySide6 Essentials 6.12.0, Shiboken6 6.12.0, Pillow 12.3.0, PyMuPDF 1.27.2.3 and/or CPython 3.14.10. **No wheel mismatch and no wheel RECORD hash failure.**
- All ten PySide6/Shiboken/CPython **MSVCP/VCRUNTIME copies** match the builder's installed package/runtime bytes. This answers *where those bytes came from*, not *whether the maintainer has permission to redistribute the runtime*.
- The **exact remaining 45** unmatched names consist of **42** Windows `api-ms-win-*.dll` compatibility/API-set DLLs, `ucrtbase.dll` and **two** `libcrypto-3-x64.dll`/`libssl-3-x64.dll` OpenSSL DLLs. The plain `libcrypto-3.dll` and `libssl-3.dll` match installed CPython. The -x64 DLLs report OpenSSL 3.5.9 in earlier binary inspection but exact supplier path is not yet established.
- `PySide6/opengl32sw.dll` (Qt software Mesa) is byte-identical to **PySide6 Essentials 6.12.0**, and its upstream copyright/Boost/MIT notices have been added. Source-built-binary identity and all transitive LLVM notices remain a separate question.
- See `reports/native-binary-origin.json` in the corresponding review bundle and `docs/NATIVE_BINARY_ORIGIN_2_8.md`. The build now **rejects mismatching wheel DLL/PYD bytes**; technical hashes are not an OSS licensing certificate.

## Current build-stage byte collection audit — 14 November 2026

The [complete six-job unsigned acceptance run #43645438667](https://github.com/Valik2005/pdf-compressor/actions/runs/43645438667) on release-candidate commit `2495e0b40fa77450cdec0691e343fc551a58b545` passed Windows Python 3.13/3.14, actual executable construction, original component source checks, *a second independently compared PyInstaller Analysis source report*, and exact three-file private staging.

The new `native-collection-sources.json` records these **118 actual binary collection sources**, all with exact SHA-256 and byte-size equality to the onefile EXE:

- **51 installed-wheel files**, all with source-relative package location;
- **22 Python-installation files** (including Python-provided OpenSSL DLLs and some C runtime files);
- **2 files from an installed program:** `libcrypto-3-x64.dll` and `libssl-3-x64.dll`, which report the OpenSSL 3.5.9 version. Source program scope is known, but the precise vendor/build/redistribution notice chain is **not** yet independently established;
- **43 unclassified builder source paths**, consisting of the 42 `api-ms-win-*.dll` forwarders and `ucrtbase.dll`. They are hashed and matched exactly to the final EXE, but source folder/license category is **not yet confirmed**. Microsoft's UCRT guidance explains their common app-local deployment role; that does not prove these copies' redistribution permission.

**Technical origin and compliance are different:** matching a builder source file answers where the precise bytes were collected but does not establish that a covered Microsoft file is in an applicable REDIST list, that Qt/MuPDF source obligations are satisfied, or that the maintainer is a validly licensed redistributor.

## Obligation matrix

| Component | Evidence established | Remains before distribution |
| --- | --- | --- |
| PDF Compressor source | GNU AGPLv3 in public repository and release notice archive | Maintain source for the **exact final tag**, license/copyright and "no warranty" notice, and any applicable source obligations for modifying covered works |
| PyMuPDF/MuPDF AGPLv3 | Full PyMuPDF/MuPDF source, full AGPL text and 2 native engine components identified | Check Artifex producer notices and relevant PDF metadata, maintain full corresponding source, copyright notices and compatibility of actual shipped native binaries |
| Qt/PySide6/Shiboken LGPLv3/GPLv3 alternatives | Full texts and upstream sources in notice/source artifacts; Windows CI demonstrated an ABI-preserving Qt DLL replacement inside rebuilt v2.8 onefile | Clear prominent Qt/LGPL notice in app + distribution, ensure users can compile/relink **genuinely modified compatible Qt** and execute modified result (onefile), preserve third-party notices and user rights |
| Pillow/codecs | Six native Pillow extensions are now confirmed byte-identical to Pillow 12.3.0 installed-wheel files, with no wheel RECORD failures. The wheel's full ~78 KB LICENSE includes copyright/license sections for AVIF, JPEG Turbo, WebP, PNG, TIFF, OpenJPEG, FreeType, lcms2, HarfBuzz and other bundled components. The release pipeline now validates each named notice. | Component source-build equivalence is not independently certified (permissive codecs generally require preserved notices rather than a compiled-source offer). Keep wheel license notices intact and investigate any newly introduced native codec in future releases. |
| OpenSSL 3.x | Four libraries named. Newly added upstream `openssl-3.5.9` LICENSE.txt and AUTHORS.md included in the v2.8 license pack; both libcrypto variants report OpenSSL 3.5.9 | Verify precise origin/build of all four DLLs and whether other binary-specific copyright attributions apply; original license text alone is not proof of binary provenance |
| Mesa/LLVM | `PySide6/opengl32sw.dll` found; Qt's official llvmpipe attribution identifies Brian Paul, Khronos and yohhoy (MIT and Boost 1.0). The next 2.8 license pack will include these named credits and complete license texts extracted from verified QtBase 6.12.0 source | Verify the actual Qt wheel's Mesa/LLVM binary components, build provenance, optional codec dependencies and any further notices; generic/partial attribution does not certify the final DLL |
| libffi | One `libffi-8.dll` found, full libffi permissive notice present | Identify original build/source and confirm notice matches actual binary |
| Python/PyInstaller | Python PSF license and PyInstaller notice present, Python runtime inventory identified | Confirm included bootloader exception, CPython dynamic extensions and redistribution/source completeness |
| Microsoft runtime | 42 API sets + 10 MSVCP/VCRUNTIME + 1 UCRTBase. Microsoft allows qualified individuals and open-source contributors to use Visual Studio Community free of charge | Confirm the maintainer's applicable Visual Studio license, each exact DLL against Microsoft's REDIST list, and separate applicable AGPL/GPL *System Library* exceptions. See [runtime review](MICROSOFT_RUNTIME_REVIEW_2_8.md); the free Community license does not automatically certify redistributed binaries |

## SignPath Foundation eligibility — historical review, not a gate for unsigned 2.8

**Update (14 November 2026):** SignPath Foundation declined the free signing application for insufficient independent public recognition, not on the technical license analysis below. The planned 2.8 is **unsigned**; SignPath's proprietary/dual-licensing program conditions do not themselves prevent an independent unsigned GitHub release, but applicable Qt LGPL, MuPDF AGPL and all third-party redistribution obligations still apply.

[SignPath Foundation OSS conditions](https://signpath.org/terms) state that all components must use an OSI-approved license **without commercial dual-licensing**, prohibit proprietary components except qualifying System Libraries, and require a previously released product, active maintenance, controlled authors/reviewers/approvers and MFA. **Both upstream Qt and PyMuPDF advertise commercial as well as open-source licensing alternatives.** These would have been questions about **dual-licensed** Qt/PyMuPDF components for the **historical signing application**. Because SignPath declined that application and the v2.8 plan is explicitly **unsigned**, further SignPath eligibility correspondence is **not** an acceptance condition for this release. The Microsoft runtime redistribution analysis still applies independently of SignPath; do not confuse certification eligibility with legal distribution rights.

SignPath's approval would authorize *its own signing workflow*, not certify third-party AGPL/LGPL or Microsoft redistribution rights.

## Concrete actions already taken in the audit patch

- Correct all v2.8 public notice references so they name the actual **`THIRD_PARTY_NOTICES_2_8.zip`**, not v2.7.
- Ensure full GPL/LGPL texts and source archives are identified as bundled **separately** from incomplete Windows wheel license metadata. Do not conceal the missing metadata from the raw wheel report.
- Provide an obvious, bilingual **Licenses** control inside the application, including GPL/LGPL/AGPL, lack of warranty, Qt user modification/relinking rights and the exact source/license archive path. GUI test verifies both languages.
- Clarify in license evidence tooling that excluded PDFium/Chromium modules are not falsely treated as shipped; note that source and Qt relinking proofs are separate CI artifacts rather than falsely claiming them missing from the project.

## Unresolved and retained as UNSIGNED release gates

1. **Legal/compliance review:** Independently verify the exact shipped native binaries and redistribution obligations for Microsoft UCRT/MSVC (11 non-API-set entries), the **two retained Python-distributed OpenSSL DLLs**, Qt/Mesa/LLVM and libffi. The two accidental MySQL `-x64` OpenSSL DLLs have been excluded since PR #42. Review AGPL/MuPDF corresponding-source and output-producer requirements and the practical LGPL Qt relinking rights in the onefile distribution. The exact Pillow 12.3.0 wheel codec/font notices are now included and checked by CI; do not incorrectly list them as still missing. Build/hash checks do not replace this review.
2. **PDF metadata:** Newly **merged/extracted** PDFs now identify `MuPDF (via PyMuPDF); PDF Compressor 2.8` as Producer (release PR #32); **compression and rotation preserve the original metadata**, including potentially signed PDF content. Confirm with Artifex whether any further producer/copyright notice steps are legally required; do not rewrite user documents just to force a notice.
3. **Current exact revision:** After the native DLL-byte gate and any other reviewed changes reach the isolated release candidate, rerun Windows 3.13/3.14 tests, real onefile launch, six-source verification and three-file staging on **that same head SHA**. Keep 2.8.1 Testing separate from the public candidate.
4. **Owner-authorized unsigned publication only:** An explicit owner decision is required **before merging the draft candidate PR #17 to `main`**, and a second separate decision is required before the manual unsigned publish workflow. Verify the resulting **main-SHA** EXE's `NotSigned` status, exact source and release ZIP hashes; publish exactly three SHA-256-checked assets, no signing claim. A checksum detects changes but does not authenticate the publisher. Merge future README links (PR #29) **only after** real v2.8 release assets exist.

**SignPath Foundation declined this application. Its approval or signature is not awaited for the unsigned plan. No v2.8 release, digital signature, or merge into `main` is authorized by this audit.**