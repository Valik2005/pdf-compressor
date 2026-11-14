# PDF Compressor 2.8 — component license audit (verified artifacts)

**Date:** 14 November 2026  
**Binary audited:** Windows x64 PyInstaller onefile, UNSIGNED, SHA-256
`1c403790119f2ca8389efe360578e963e3f95e3b4b68d7c6e73ecfbaae95c39b`,
source commit `09e1b73b74c7dbf04fddd8a576f0c78fae50365d`.
GitHub Actions: [successful same-commit run #43599279025](https://github.com/Valik2005/pdf-compressor/actions/runs/43599279025)
([Windows artifact](https://github.com/Valik2005/pdf-compressor/actions/runs/43599279025/artifacts/14116470122),
[upstream source/notice artifact](https://github.com/Valik2005/pdf-compressor/actions/runs/43599279025/artifacts/14116270695),
[pre-sign evidence](https://github.com/Valik2005/pdf-compressor/actions/runs/43599279025/artifacts/14115826992)).
This SHA refers **only** to the reviewed, unsigned build. **Re-run every check after changes and again for the final main revision**.

This report is a technical bill-of-materials and obligations review, **not a legal opinion or redistribution compliance certificate**.

## Verified facts, not assumptions

- Actual onefile inventory: **118 native DLL/PYD entries**. Group counts: QtBase 18, QtSvg 3, QtImageFormats 5, PySide6/Shiboken 7, PyMuPDF 1, MuPDF 2, Pillow codecs 6, OpenSSL 4, Mesa software renderer 1, libffi 1, Python 17, and Microsoft runtime **53**.
- Of those 53 Microsoft entries, **42** are `api-ms-win-*.dll` API sets, **10** are MSVCP/VCRUNTIME copies inside root/PySide6/shiboken6, and **1** is `ucrtbase.dll`. API-set attribution **does not establish redistributability** for the 11 other files.
- Four separate OpenSSL native libraries found: `libcrypto-3-x64.dll`, `libcrypto-3.dll`, `libssl-3-x64.dll`, `libssl-3.dll`. Their **precise runtime build origins and applicable OpenSSL notices have not been verified**.
- The following were **not** present in the inspected native DLL/PYD bundle: QtPdf, PDFium, QtQuick, QtQml, QtVirtualKeyboard, Chromium/WebEngine. Do **not** require PDFium or Chromium source/notice as a condition for *this* trimmed build unless a future final audit detects their return.
- Six upstream archives are present and SHA-256 checked: PyMuPDF 1.27.2.3, MuPDF 1.27.2, Qt for Python 6.12.0, QtBase 6.12.0, QtSvg 6.12.0, QtImageFormats 6.12.0. **SHA-256 of an upstream source archive is not proof of the binary being compiled from that exact archive.**
- `THIRD_PARTY_NOTICES_2_8.zip` currently contains **73 entries**, including full project **AGPLv3**, MuPDF `COPYING`, full Qt/PySide6 **LGPLv3 and GPLv3** texts, QtBase/QtSvg/QtImageFormats third-party texts, and libffi notice. `license-evidence.zip` separately contains Windows-builder installed-wheel documentation for Pillow, Python, PyInstaller, PyMuPDF and PySide6/Shiboken. For the Qt wheels, only `LicenseRef-Qt-Commercial.txt` was directly extractable from the installed wheel metadata: the Qt **open-source** full-text licenses are in the **other** notice archive, not in those wheel metadata records.
- Exact original→compressed sample PDFs #04 and #10 retain their original Creator metadata, but both original and result PDF `Producer` values were empty. This **does not by itself prove an AGPL violation**; Artifex producer/copyright notice requirements should be confirmed and guarded by a dedicated test before changing the compression pipeline.

## Obligation matrix

| Component | Evidence established | Remains before distribution |
| --- | --- | --- |
| PDF Compressor source | GNU AGPLv3 in public repository and release notice archive | Maintain source for the **exact final tag**, license/copyright and "no warranty" notice, and any applicable source obligations for modifying covered works |
| PyMuPDF/MuPDF AGPLv3 | Full PyMuPDF/MuPDF source, full AGPL text and 2 native engine components identified | Check Artifex producer notices and relevant PDF metadata, maintain full corresponding source, copyright notices and compatibility of actual shipped native binaries |
| Qt/PySide6/Shiboken LGPLv3/GPLv3 alternatives | Full texts and upstream sources in notice/source artifacts; Windows CI demonstrated an ABI-preserving Qt DLL replacement inside rebuilt v2.8 onefile | Clear prominent Qt/LGPL notice in app + distribution, ensure users can compile/relink **genuinely modified compatible Qt** and execute modified result (onefile), preserve third-party notices and user rights |
| Pillow/codecs | Wheel license present; six Pillow native extensions audited | Attribute actual bundled libjpeg/libwebp/AVIF/other codecs by module and native build, include necessary notices; verify wheel-source correspondence |
| OpenSSL 3.x | Four libraries named; Apache-2.0 **generic license text** available in QtBase source | Obtain exact DLL versions/origins and **OpenSSL's own** copyright/Apache-2.0 notices; generic Apache license text is not an attribution to OpenSSL |
| Mesa/LLVM | `PySide6/opengl32sw.dll` found | Verify Mesa/LLVM components actually built in Qt's software rasterizer and their license/notice obligations; generic MIT is insufficient |
| libffi | One `libffi-8.dll` found, full libffi permissive notice present | Identify original build/source and confirm notice matches actual binary |
| Python/PyInstaller | Python PSF license and PyInstaller notice present, Python runtime inventory identified | Confirm included bootloader exception, CPython dynamic extensions and redistribution/source completeness |
| Microsoft runtime | 42 API sets + 10 MSVCP/VCRUNTIME + 1 UCRTBase | Check [Microsoft redistributable terms](https://learn.microsoft.com/cpp/windows/redistributing-visual-cpp-files) and whether the actual DLLs qualify as *System Libraries* under applicable AGPL/GPL and SignPath Foundation rules |

## SignPath Foundation eligibility — explicit dependency, not presumed accepted

[SignPath Foundation OSS conditions](https://signpath.org/terms) state that all components must use an OSI-approved license **without commercial dual-licensing**, prohibit proprietary components except qualifying System Libraries, and require a previously released product, active maintenance, controlled authors/reviewers/approvers and MFA. **Both upstream Qt and PyMuPDF advertise commercial as well as open-source licensing alternatives.** It is therefore necessary to ask SignPath whether the specific **open-source distributions of these dual-licensed dependencies** satisfy its stated policy; no assumption or reinterpretation of the rule substitutes for their answer. Separately clarify whether the redistributed MSVC/UCRT files in this exact binary satisfy their System Library exception. This is a potential **signing-eligibility blocker**, not merely a missing certificate.

SignPath's approval would authorize *its own signing workflow*, not certify third-party AGPL/LGPL or Microsoft redistribution rights.

## Concrete actions already taken in the audit patch

- Correct all v2.8 public notice references so they name the actual **`THIRD_PARTY_NOTICES_2_8.zip`**, not v2.7.
- Ensure full GPL/LGPL texts and source archives are identified as bundled **separately** from incomplete Windows wheel license metadata. Do not conceal the missing metadata from the raw wheel report.
- Provide an obvious, bilingual **Licenses** control inside the application, including GPL/LGPL/AGPL, lack of warranty, Qt user modification/relinking rights and the exact source/license archive path. GUI test verifies both languages.
- Clarify in license evidence tooling that excluded PDFium/Chromium modules are not falsely treated as shipped; note that source and Qt relinking proofs are separate CI artifacts rather than falsely claiming them missing from the project.

## Unresolved and retained as release gates

1. Obtain explicit SignPath response about **dual-licensed upstream Qt/PyMuPDF** and **Microsoft runtime exception**; review with an OSS licensing professional if SignPath's answer or applicable license terms remain uncertain.
2. Document exact copyright/producer metadata behavior of all output code paths using PyMuPDF (compress, merge, split, rotate). Do not silently modify PDF metadata or invalidate signed PDFs to add notices; seek upstream Artifex clarification on producer notice requirements.
3. Validate the actual licenses/origin of the **four OpenSSL DLLs**, Mesa/LLVM rasterizer, Pillow codecs, and **11 non-API-set Microsoft DLL entries**; provide full corresponding notices and sources as applicable.
4. Once the changes are merged, rerun *all* Windows GUI/metadata/CI checks on both release and testing branches, repeat same-commit cross-audit for final build, and maintain a verified signed checksum only after SignPath approval.

**No release, digital signature or replacement of `main` is authorized by this review.**