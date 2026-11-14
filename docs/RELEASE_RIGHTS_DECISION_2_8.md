# PDF Compressor 2.8 — verification of distribution rights (decision record)

**Prepared:** 15 November 2026. **State: unresolved; publication prohibited until reviewed.**
**Candidate:** `020b335ce88ad7ff08b353a0890d5b977b92dd4a`, [6/6 checks passing](https://github.com/Valik2005/pdf-compressor/actions/runs/43646166452).
**Windows standalone SHA-256:** `442a3e91607ee7933e7e0ada98cdf965f9b1f17f3f63457d86e78d4b825c982b`.
**Source/license bundle SHA-256:** `5bc54d813737ff685eb41b2f380e065cb4dc4c2f148f8248ad4fd6d93c8ef233`.
These two hashes were independently recalculated from the GitHub review-only archive and match its `SHA256SUMS.txt`.

This is an evidence checklist grounded in official vendor notices and the *actual bundled binary*. It is **not** a legal opinion and must **not** be treated as proof of compliance or owner authorization. The owner confirms distribution rights only after checking every applicable license requirement.

## 1. Microsoft UCRT, MSVC

**Actual archive evidence:** 42 `api-ms-win-*.dll` forwarders and one `ucrtbase.dll` are byte-for-byte present; the source-collection report says `unclassified-builder-path`. Ten `MSVCP*/VCRUNTIME*` files match installed Python/PySide6/Shiboken origins. Thus all files are identified and hashed, but the **original Windows SDK / Visual Studio REDIST installation directory and the maintainer's redistribution entitlement remain unverified**.

- Microsoft: [UCRT app-local deployment](https://learn.microsoft.com/en-us/cpp/porting/upgrade-your-code-to-the-universal-crt) explicitly discusses `ucrtbase.dll` and API-set forwarders in the Windows SDK `Redist/ucrt/DLLs` location. This is **supported** deployment, not unconditional permission to redistribute arbitrary copies from any folder.
- Microsoft: [Redistributing Visual C++ files](https://learn.microsoft.com/en-us/cpp/windows/redistributing-visual-cpp-files) requires **valid licensing** and respect for the applicable [REDIST list](https://learn.microsoft.com/en-us/visualstudio/releases/2026/redistribution). Unmodified copies from the authorized redist location are materially different from unidentified copies obtained elsewhere.
- Microsoft: [Visual Studio Community usage](https://visualstudio.microsoft.com/vs/community/) permits individual developers to create free or paid applications; [licensing guidance](https://www.microsoft.com/licensing/guidance/Visual-Studio) also describes open-source scenarios. **Do not assert that the maintainer meets the license terms without their evidence.**

**Required:** identify the actual SDK/REDIST source distribution for all 53 runtime members (or rebuild with a legally verified source); retain evidence of the maintainer's applicable Visual Studio Community/Build Tools eligibility and the permitted redistribution terms. If not possible, make a separately tested build that relies on installed, properly licensed Windows components; do not strip DLLs from the tested EXE blindly.

## 2. OpenSSL

**Actual archive evidence:** four OpenSSL DLLs present. Two Python-provided `libcrypto-3.dll` and `libssl-3.dll` are matched to installed Python. Two `-x64` libraries were captured from an `installed-program` path with no program/vendor identifier:

| Included file | SHA-256 | Exact byte size | Source classification |
| --- | --- | ---: | --- |
| `libssl-3-x64.dll` | `a2cb46897a5365a740c8f898bf1b9119ba23f01807ad0ba1efb69a9997b43ba0` | 1,296,520 | installed program, vendor not established |
| `libcrypto-3-x64.dll` | `d51f2b081e5ac0f94c2bf15650a6b55cf48da1de8c313c9f90003d9ed08ccc9e` | 6,946,448 | installed program, vendor not established |

The official [OpenSSL license page](https://openssl-library.org/source/license/index.html) establishes **Apache License 2.0 for OpenSSL 3.0+**. The v2.8 notice pack already includes the exact original OpenSSL 3.5.9 LICENSE and AUTHORS material. **Required:** identify the `-x64` DLL supplier and its additional build-specific notices/components, if any; only then attest that their source and notices are covered.

## 3. Qt / PySide6 / Shiboken

**Actual evidence:** matching installed-wheel DLLs, included full QtBase/QtSvg/QtImageFormats and Qt for Python source archives with SHA-256, LGPL/GPL notices, and a verified ability to re-pack a onefile EXE with an ABI-compatible modified Qt DLL.

Official [Qt LGPL obligations](https://www.qt.io/development/open-source-lgpl-obligations) require complete corresponding library source or a qualifying written offer **controlled by the distributor**, and users' ability to relink against modified Qt libraries. Some Qt modules are GPL-only; see [Qt 6.12 licenses](https://doc.qt.io/qt-6.12/licensing.html). **Required:** confirm the shipped subset of Qt modules has correct applicable terms, that provided sources actually cover all bundled modules and transitive attributions, and that recipient repacking rights are effective in the final distribution (not just an unchanged-source wheel test).

## 4. PyMuPDF / MuPDF (AGPL)

**Actual evidence:** the project source is publicly AGPLv3; pinned PyMuPDF/MuPDF sources and COPYING are included. Newly merged/extracted PDFs credit MuPDF as producer; compress/rotate paths preserve original input metadata, including potentially signed inputs.

Official [PyMuPDF licensing](https://pymupdf.io/licensing) requires applicable AGPL source disclosure and preservation of **relevant output producer notice**. **Required:** verify complete corresponding code and any output attribution duty for *these four document operations* against vendor policy. Do not rewrite user documents or invalidate signed PDFs merely to force a metadata string. Seek Artifex guidance if the existing preserve-input behavior is not clearly compliant.

## 5. Qt Mesa llvmpipe / possible LLVM, Pillow, libffi

`PySide6/opengl32sw.dll` is byte-identical to installed PySide6 Essentials; the relevant Mesa MIT/Boost notices and the Qt third-party source attribution material are included. See [Qt LLVMPipe attribution](https://doc.qt.io/qt-6.5/qt-attribution-llvmpipe.html). LLVM's [developer policy](https://llvm.org/docs/DeveloperPolicy.html) explains Apache-2.0-with-LLVM-exception distribution requirements, but presence/version of embedded LLVM components in **this exact Qt wheel** is not independently proven: preserve any applicable notices if present.

Pillow 12.3.0 installed-wheel codec/font LICENSE (~78 KB) is included, with each exact codec marker tested; no known missing Pillow notice remains. libffi notice is included; verify applicable binary/source correspondence, not just its filename.

## Release decision — do not auto-check

- [ ] All third-party software and native sources are matched to licensed distributors and correct copy-specific license/notice material.
- [ ] Maintainer/organization's applicable Microsoft redistribution eligibility and actual authorized REDIST/Windows SDK copies documented, or a separately tested alternate packaging plan used.
- [ ] Qt LGPL/GPL and PyMuPDF AGPL corresponding source, notices, relinking and output copyright conditions independently confirmed.
- [ ] Legal/compliance reviewer name or responsible maintainer, date, scope and references recorded. **The assistant cannot self-attest the owner's rights or manufacture an external legal opinion.**
- [ ] **Separate** owner authorization to merge PR #17 into `main`. Re-run six-job acceptance on new exact main commit and verify real unsigned EXE + two SHA256SUMS entries.
- [ ] **Separate** owner authorization to publish unsigned v2.8 using the gated manual workflow; publish exactly 3 assets, then merge README PR #29.

**Decision: HOLD.** Green CI, an AGPL public repo, and free Visual Studio Community do not automatically remove independent redistribution conditions. No SignPath signature is required for the selected unsigned variant. This record does not create a public tag, release or license approval.
