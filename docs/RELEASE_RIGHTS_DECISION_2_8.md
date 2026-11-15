## CURRENT SELECTED 62-NATIVE RELEASE-CANDIDATE RIGHTS STATUS (15 Nov 2026)

**CURRENT OWNER-SELECTED v2.8 (15 Nov 2026):** The isolated release branch now contains the **62-native** Windows x64 version (no embedded Microsoft MSVC/UCRT/API-set DLLs). Source ancestor `392ddd30`; merged release branch `8317b588`. The owner independently ran the exact Windows 2025 artifact EXE SHA-256 `00a878796abad875546c556db63e9bb18af3137e3f7226c6610b1deb91a4b166` on Windows 11 build 26200: official Microsoft VC++ Redistributable x64 v14.51.36247.00 present, GUI smoke passed, Licenses dialog opened. User acceptance of the functional PDF compression engine was recorded separately on 14 Nov using 2.8.1 Testing; no compression-code change is part of this packaging. The `ca56a3e2...` sibling same-source review EXE had all 62 DLL/PYD bytes equal to the user-tested EXE but a different whole-file SHA; never represent one as the other. Current release-branch commits after `392ddd` require same-commit CI before publication. No merge into `main`, no public tag, and no legal license approval is implied. 115-native and older inventories below are **historical, not current candidate contents**. The EXE requires the *separately installed* official Microsoft VC++ Redistributable x64; this build does **not** redistribute Microsoft runtime DLLs. Third-party LGPL/AGPL/Mesa/LLVM/other obligations and separate owner authorization remain prerequisites to a public release. Smart App Control may block unsigned EXEs; do not weaken user security to bypass it.

**Historical per-115-native and exploratory 62-native evidence below is retained for audit only.** Check the exact source commit and EXE SHA for each observation; unresolved 53-copy Microsoft licensing conditions in the historical section do not describe the selected MS-DLL-free binary.

---

# PDF Compressor 2.8 — verification of distribution rights (decision record)

**Prepared:** 15 November 2026. **State: unresolved; publication prohibited until reviewed.**
**Candidate:** `020b335ce88ad7ff08b353a0890d5b977b92dd4a`, [6/6 checks passing](https://github.com/Valik2005/pdf-compressor/actions/runs/43646166452).
**Windows standalone SHA-256:** `442a3e91607ee7933e7e0ada98cdf965f9b1f17f3f63457d86e78d4b825c982b`.
**Source/license bundle SHA-256:** `5bc54d813737ff685eb41b2f380e065cb4dc4c2f148f8248ad4fd6d93c8ef233`.
These two hashes were independently recalculated from the GitHub review-only archive and match its `SHA256SUMS.txt`.

This is an evidence checklist grounded in official vendor notices and the *actual bundled binary*. It is **not** a legal opinion and must **not** be treated as proof of compliance or owner authorization. The owner confirms distribution rights only after checking every applicable license requirement.

## Clarification: VS Code is the editor, not a Visual Studio license

The maintainer has now specified **VS Code**, not Visual Studio Community,
as their development editor. [Microsoft's VS Code FAQ](https://code.visualstudio.com/docs/supporting/faq)
states that VS Code and Visual Studio IDE are distinct products. Microsoft's
[redistribution terms](https://learn.microsoft.com/en-us/cpp/windows/redistributing-visual-cpp-files)
tie redistribution of Microsoft VC runtime DLLs to an appropriately licensed
Visual Studio software edition/toolchain and its applicable terms, **not**
to VS Code. We must **not** mark the Community REDIST entitlement as met.

Continuing to develop in VS Code is fine: we need only resolve the
independent **redistribution and DLL provenance** question before publishing.
Possible routes are a valid no-cost individual Community license with
permitted, unmodified official REDIST copies (after verifying eligibility and
actual source) **or** a separately tested app that leaves system runtime
installation to Microsoft/the user. Neither choice is completed by the
user's report of their editor. Do not automatically swap out Microsoft
DLLs, require paid Visual Studio, or consider licensing solved.

## Maintainer licensing status: individual developer (15 Nov 2026)

- [x] **Development/distribution role:** the maintainer confirmed a **personal independent-developer** release rather than distribution by a company or other organization. No identifying name, billing data or employer details are required for this classification.
- [x] **Eligible no-cost licensing route:** Microsoft officially allows individuals to use **Visual Studio Community** to create their own free or commercial apps. Its [REDIST 2022 list](https://learn.microsoft.com/en-us/visualstudio/releases/2022/redistribution) explicitly includes properly licensed Community 2022 users, subject to the specific software license terms, original unmodified file eligibility and excluded Debug/nonredist paths.
- [ ] **Not yet substantiated:** the developer's actual possession/use of a qualifying Visual Studio license agreement (**VS Code is not one**), or a different permitted redistributable source, and whether **the exact Microsoft DLL copies included by PyInstaller from the Python/Qt wheels** are eligible for redistribution. An individual may qualify without paying, but eligibility alone is not a legal clearance or an assertion about what licenses have been accepted.
- [ ] **Independent Qt LGPL/MuPDF AGPL and vendor notices review** remains unchanged. All applicable redistribution obligations must still be satisfied before publication.

The latest source candidate is [PR #17](https://github.com/Valik2005/pdf-compressor/pull/17). Historical hashes recorded below are intentionally labelled to their **older** candidate and must never be used as the final EXE checksum. Publish only after the current head's same-commit acceptance, separate owner authorization and confirmed rights.

## After PR #42: accidental MySQL OpenSSL removed

The hashes at the top of this file identify the **historical candidate at
`020b335c`**. They are NOT valid hashes for the later release binary.
The enhanced collection audit identified the two previously unclassified
OpenSSL `-x64` DLLs as byte-for-byte copies from
`MySQL/MySQL Server 8.4/bin` in the hosted Windows runner.
PR #42 excludes both DLLs and the optional Qt
`PySide6/plugins/tls/qopensslbackend.dll` (an offline PDF app does not
require this Qt OpenSSL TLS backend). Python's `libssl-3.dll`,
`libcrypto-3.dll` and `_ssl.pyd` remain, with the existing
OpenSSL/Python notices.

Both [Windows experiment jobs #43650917328](https://github.com/Valik2005/pdf-compressor/actions/runs/43650917328)
passed **205 tests each**, Qt GUI startup and byte-origin verification of
**115 native members**. The final six-job release-branch review and fresh
EXE/ZIP hashes are required after integrating all changes. The earlier
MySQL-specific distribution question is resolved by **not shipping those
binaries**, not by claiming rights to them. The independent Microsoft and
LGPL/AGPL obligations below remain.

## 1. Microsoft UCRT, MSVC

**Actual archive evidence:** 42 `api-ms-win-*.dll` forwarders and one `ucrtbase.dll` are byte-for-byte present; the source-collection report says `unclassified-builder-path`. Ten `MSVCP*/VCRUNTIME*` files match installed Python/PySide6/Shiboken origins. Thus all files are identified and hashed, but the **original Windows SDK / Visual Studio REDIST installation directory and the maintainer's redistribution entitlement remain unverified**.

- Microsoft: [UCRT app-local deployment](https://learn.microsoft.com/en-us/cpp/porting/upgrade-your-code-to-the-universal-crt) explicitly discusses `ucrtbase.dll` and API-set forwarders in the Windows SDK `Redist/ucrt/DLLs` location. This is **supported** deployment, not unconditional permission to redistribute arbitrary copies from any folder.
- Microsoft: [Redistributing Visual C++ files](https://learn.microsoft.com/en-us/cpp/windows/redistributing-visual-cpp-files) requires **valid licensing** and respect for the applicable [REDIST list](https://learn.microsoft.com/en-us/visualstudio/releases/2026/redistribution). Unmodified copies from the authorized redist location are materially different from unidentified copies obtained elsewhere.
- Microsoft: [Visual Studio Community usage](https://visualstudio.microsoft.com/vs/community/) permits individual developers to create free or paid applications; [licensing guidance](https://www.microsoft.com/licensing/guidance/Visual-Studio) also describes open-source scenarios. **Do not assert that the maintainer meets the license terms without their evidence.**

**Required:** identify the actual SDK/REDIST source distribution for all 53 runtime members (or rebuild with a legally verified source); retain evidence of the maintainer's applicable Visual Studio Community/Build Tools eligibility and the permitted redistribution terms. If not possible, make a separately tested build that relies on installed, properly licensed Windows components; do not strip DLLs from the tested EXE blindly.

## 2. OpenSSL

**Historical pre-PR42 archive evidence:** four OpenSSL DLLs were present. Two Python-provided `libcrypto-3.dll` and `libssl-3.dll` are matched to installed Python. Two `-x64` libraries were captured from an `installed-program` path with no program/vendor identifier:

| Included file | SHA-256 | Exact byte size | Source classification |
| --- | --- | ---: | --- |
| `libssl-3-x64.dll` | `a2cb46897a5365a740c8f898bf1b9119ba23f01807ad0ba1efb69a9997b43ba0` | 1,296,520 | installed program, vendor not established |
| `libcrypto-3-x64.dll` | `d51f2b081e5ac0f94c2bf15650a6b55cf48da1de8c313c9f90003d9ed08ccc9e` | 6,946,448 | installed program, vendor not established |

The official [OpenSSL license page](https://openssl-library.org/source/license/index.html) establishes **Apache License 2.0 for OpenSSL 3.0+**. The v2.8 notice pack already includes the exact original OpenSSL 3.5.9 LICENSE and AUTHORS material. **Current disposition:** the `-x64` DLL supplier was determined to be MySQL Server 8.4 on the build runner. PR #42 removes those DLLs and the unused Qt TLS backend; their separate supplier-specific redistribution issue no longer applies to the current candidate. Confirm only the actual retained Python/OpenSSL notices and avoid reviving ambient DLL imports in future builds.

## 3. Qt / PySide6 / Shiboken

**Actual evidence:** matching installed-wheel DLLs, included full QtBase/QtSvg/QtImageFormats and Qt for Python source archives with SHA-256 and LGPL/GPL notices. The **current** [Windows v2.8 recipient Qt relink run #43658575876](https://github.com/Valik2005/pdf-compressor/actions/runs/43658575876) passed: precisely declared stock and modified `Qt6Widgets.dll` hashes, modified bytes embedded in onefile, and offscreen GUI startup. The official release verifier explicitly refuses recipient-relinked DLL entries. This is a technical LGPL replacement demonstration only, not proof of full corresponding-source/reverse-engineering or other legal compliance.

Official [Qt LGPL obligations](https://www.qt.io/development/open-source-lgpl-obligations) require complete corresponding library source or a qualifying written offer **controlled by the distributor**, and users' ability to relink against modified Qt libraries. Some Qt modules are GPL-only; see [Qt 6.12 licenses](https://doc.qt.io/qt-6.12/licensing.html). **Required:** confirm the shipped subset of Qt modules has correct applicable terms, that provided sources actually cover all bundled modules and transitive attributions, and that recipient repacking rights are effective in the final distribution (not just an unchanged-source wheel test).

## 4. PyMuPDF / MuPDF (AGPL)

**Actual evidence:** the project source is publicly AGPLv3; pinned PyMuPDF/MuPDF sources and COPYING are included. Newly merged/extracted PDFs credit MuPDF as producer; compress/rotate paths preserve original input metadata, including potentially signed inputs.

Official [PyMuPDF licensing](https://pymupdf.io/licensing) describes corresponding-source obligations and retaining relevant copyright/producer metadata in generated documents. [Artifex's own AGPL guidance](https://artifex.com/licensing) phrases this as **ideally** mentioning AGPL and preserving the producer line in PDFs created **or modified** with its open-source software; do not replace that nuanced language with an invented universal mandate to rewrite input metadata.

**Verified current behavior in `pdf_engine.py`:** merge/extract call `_mark_new_pdf_producer()` for a new PDF **only when producer metadata is absent**; compression and rotation preserve incoming producer metadata. Consequently, a compressed/rotated PDF can retain a third-party producer without adding MuPDF. This is a real attribution-policy question, **not** evidence that the output is necessarily non-compliant. The AGPL software source/license notices are provided in the release companion ZIP.

**Required:** confirm corresponding source and the appropriate producer/copyright handling for merge, extract, compression and rotation, including signed/user originals, before publication. Do not rewrite or invalidate existing user PDFs merely to add a producer string without a deliberate and technically verified policy. Artifex's FAQ/guidance is not a substitute for a complete license-specific review.

## 5. Qt Mesa llvmpipe / possible LLVM, Pillow, libffi

`PySide6/opengl32sw.dll` is byte-identical to installed PySide6 Essentials; the relevant Mesa MIT/Boost notices and the Qt third-party source attribution material are included. See [Qt LLVMPipe attribution](https://doc.qt.io/qt-6.5/qt-attribution-llvmpipe.html). LLVM's [developer policy](https://llvm.org/docs/DeveloperPolicy.html) explains Apache-2.0-with-LLVM-exception distribution requirements, but presence/version of embedded LLVM components in **this exact Qt wheel** is not independently proven: preserve any applicable notices if present.

Pillow 12.3.0 installed-wheel codec/font LICENSE (~78 KB) is included, with each exact codec marker tested; no known missing Pillow notice remains. libffi notice is included; verify applicable binary/source correspondence, not just its filename.

## Release decision — do not auto-check

- [ ] All third-party software and native sources are matched to licensed distributors and correct copy-specific license/notice material.
- [x] Maintainer confirmed the project is distributed as an **individual developer**, not on behalf of an organization (15 Nov 2026); free Community license route is potentially applicable.
- [ ] Actual individual license/accepted terms and permitted Microsoft REDIST/Windows SDK **copies in the exact EXE** documented, or a separately tested alternate packaging plan used.
- [ ] Qt LGPL/GPL and PyMuPDF AGPL corresponding source, notices, relinking and output copyright conditions independently confirmed.
- [ ] Legal/compliance reviewer name or responsible maintainer, date, scope and references recorded. **The assistant cannot self-attest the owner's rights or manufacture an external legal opinion.**
- [ ] **Separate** owner authorization to merge PR #17 into `main`. Re-run six-job acceptance on new exact main commit and verify real unsigned EXE + two SHA256SUMS entries.
- [ ] **Separate** owner authorization to publish unsigned v2.8 using the gated manual workflow; publish exactly 3 assets, then merge README PR #29.

**Decision: HOLD.** Green CI, an AGPL public repo, and free Visual Studio Community do not automatically remove independent redistribution conditions. No SignPath signature is required for the selected unsigned variant. This record does not create a public tag, release or license approval.
