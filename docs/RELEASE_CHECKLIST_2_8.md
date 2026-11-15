# PDF Compressor 2.8 — final pre-release checklist

**Public stable version remains 2.7.1. This checklist does NOT authorize publishing 2.8.**

**CURRENT OWNER-SELECTED v2.8 (15 Nov 2026):** The isolated release branch now contains the **62-native** Windows x64 version (no embedded Microsoft MSVC/UCRT/API-set DLLs). Source ancestor `392ddd30`; merged release branch `8317b588`. The owner independently ran the exact Windows 2025 artifact EXE SHA-256 `00a878796abad875546c556db63e9bb18af3137e3f7226c6610b1deb91a4b166` on Windows 11 build 26200: official Microsoft VC++ Redistributable x64 v14.51.36247.00 present, GUI smoke passed, Licenses dialog opened. User acceptance of the functional PDF compression engine was recorded separately on 14 Nov using 2.8.1 Testing; no compression-code change is part of this packaging. The `ca56a3e2...` sibling same-source review EXE had all 62 DLL/PYD bytes equal to the user-tested EXE but a different whole-file SHA; never represent one as the other. Current release-branch commits after `392ddd` require same-commit CI before publication. No merge into `main`, no public tag, and no legal license approval is implied. 115-native and older inventories below are **historical, not current candidate contents**. The EXE requires the *separately installed* official Microsoft VC++ Redistributable x64; this build does **not** redistribute Microsoft runtime DLLs. Third-party LGPL/AGPL/Mesa/LLVM/other obligations and separate owner authorization remain prerequisites to a public release. Smart App Control may block unsigned EXEs; do not weaken user security to bypass it.

## Exact 62-native licensing inventory review — 15 Nov 2026

- [x] The seven required upstream source archives for Qt/PySide6, PyMuPDF/MuPDF, and Pillow 12.3.0 were independently downloaded and checked with their pinned SHA-256 digests. Release-branch 6/6 run: [#43710767759](https://github.com/Valik2005/pdf-compressor/actions/runs/43710767759).
- [x] Application GPL-family licensing route selected: `AGPL-3.0-only`; full license text is in the candidate's third-party notices package, and complete application source is available from the private release branch (a public release must point at the **exact** tag).
- [x] The archived Qt LGPLv3/GPLv3 texts and module source versions cover the identified QtCore/Gui/Widgets/Network/OpenGL/Svg/ImageFormats and PySide6/Shiboken modules; no known GPL-only Qt add-on from the official 6.12 list appears among the actual 62 native members.
- [x] Qt user-repack route documented; ABI-preserving replacement via the PyInstaller onefile build spec passed on Windows ancestor. Full source-ABI/general installation compliance still requires owner review, not just byte equivalence.
- [x] The actual Pillow wheel license (including native codecs), Python PSF license, Python OpenSSL 3.5.9 license/authors, libffi license and PyInstaller bootloader exception are bundled in notices/evidence.
- [x] This selected 62-native EXE has **zero Microsoft runtime DLLs**; separate official VC++ x64 installation is required. Historical Microsoft DLL redistribution questions should not block *this exact* candidate.
- [ ] Match all remaining third-party/codec and `opengl32sw.dll` Mesa/LLVM license/build notices to applicable exact native components, including a responsible assessment of whether further corresponding source is required for the combined AGPL distribution.
- [ ] Approve the application-source availability at the **final published source tag** and recipient LGPL Qt replacement/relinking instructions for that same binary after final `main` build.
- [ ] Record the responsible maintainer's **personal, affirmative license-rights/compliance decision** after reviewing the evidence. No technical system or assistant can grant another copyright holder's permission or impersonate a legal reviewer.

See the detailed [exact candidate license decision](FINAL_THIRD_PARTY_LICENSE_REVIEW_2_8.md). **HOLD** publication until unchecked items are addressed and the owner separately authorizes public distribution.

## Distribution identity and zero-cost licensing path — confirmed 15 Nov 2026

- [x] The maintainer specified a release **as a private individual / independent developer**, not an organization. Do not request or invent company/legal-entity details.
- [x] Microsoft's official [Community licensing](https://www.microsoft.com/licensing/guidance/Visual-Studio) permits an eligible individual to build their own free or paid applications without purchasing Visual Studio Professional or Enterprise. The [VS 2022 REDIST page](https://learn.microsoft.com/en-us/visualstudio/releases/2022/redistribution) covers validly licensed Community 2022 users, subject to listed file/term restrictions.
- [x] Maintainer reports **VS Code** as their editor, which is NOT Visual Studio Community and does not grant Microsoft REDIST rights ([official distinction](https://code.visualstudio.com/docs/supporting/faq)).
- [ ] Confirm a distinct, applicable Microsoft distribution license (free individual Community may be eligible but is **not claimed installed/licensed**) and exact authorized Microsoft REDIST/SDK provenance of bundled MSVC/UCRT DLL copies; OR build and separately test a version that relies on an official, independently installed Microsoft runtime. **VS Code and individual-developer status alone do not grant runtime redistribution rights.**
- [ ] Independently clear the unchanged LGPL Qt, AGPL MuPDF and other third-party obligations. The accidental MySQL OpenSSL dependencies were removed and excluded by source-level guards; the retained Python/OpenSSL notices remain.
- [ ] Explicit owner approval to merge PR #17 into `main` and a **separate** owner approval to publish unsigned v2.8, after the applicable compliance checks. Neither approval is implied by confirming individual-developer status.

**No paid certificate or paid Visual Studio purchase is a prerequisite of the currently selected unsigned individual-developer plan.** See `docs/MICROSOFT_RUNTIME_REVIEW_2_8.md` for exact vendor requirements.

## Current Qt LGPL user-modification audit — verified 15 Nov 2026

- [x] [Windows v2.8 Qt onefile recipient rebuild #43658575876](https://github.com/Valik2005/pdf-compressor/actions/runs/43658575876) **PASS**: injected ABI-preserving modified `Qt6Widgets.dll`, checked its exact SHA-256 inside the EXE and launched the rebuilt GUI.
- [x] The recipient script declares original-wheel plus replacement DLL SHA-256 in an isolated manifest; unrelated wheel changes are not accepted. The **official release** same-source/EXE auditor rejects recipient-modified entries, preserving release-chain integrity.
- [ ] The above does NOT certify arbitrary compiled source modifications or full LGPL compliance. Keep official Qt matching-source notices, relinking instructions and independent license/legal verification.
- [ ] Complete same-commit six-job acceptance on the latest release-branch commit and separately on the exact owner-authorized `main` revision before any unsigned release.

## SignPath Foundation decision — 14 November 2026

**The free OSS signing application was declined.** The Foundation cited insufficient independent recognition/usage (GitHub stars, forks, contributors, third-party discussions/articles and other public trust signals), **not a failed technical/security audit**. It invited reapplication after broader adoption. Do **not** wait for an approval of this completed application, claim the release is signed or use the existing signed-only publication workflow.

**The maintainer selected the unsigned v2.8 preparation path.** This is approval to **prepare and test**, not permission to merge into main or publish. A separate gated unsigned three-file assembler, Windows Authenticode NotSigned evidence and manual-only release workflow are prepared. Current signed-only workflows and old PR #18 wording must not be used for this release.

**The release remains blocked by applicable third-party licensing questions regardless of the signature decision.** See `docs/OSS_LICENSE_AUDIT_2_8.md`. A paid signing subscription is not planned.
Public release candidate: [draft PR #17](https://github.com/Valik2005/pdf-compressor/pull/17) from `release/2.8-ready-for-signpath` into `main`.
Normal development: `develop/2.8-quality-audit` (still `2.8-preview`).
Private testing line: `testing/2.8.1-automatic-test-report` (still `2.8.1-testing`, with its own `test_report.py`).

## Done — product behavior and user-provided acceptance

- [x] User tested 2.8.1 Testing with 18 first-pass actions (11 successes, 4 honest over-target results, 3 cancelled), and 2 subsequent successful actions with visual warnings.
- [x] Original-vs-result PDF #04/#10 comparison across six pages: page count, page geometry, extractable text and image dimensions preserved; aggressive JPEG 48%/27% visibly degrades fine raster details, so warnings must remain.
- [x] 2.8 HTML/JSON quality export redacts full local directories, retains escaped basenames, and preserves functionality; integrated through [PR #14](https://github.com/Valik2005/pdf-compressor/pull/14).
- [x] Public release branch frozen with `APP_VERSION = "2.8"`; preview branch and private 2.8.1 testing version are not renamed.
- [x] Confirmed no `test_report.py` embedded in public release source; no test reporter merges into `main`.
- [x] Public v2.8 RC passed Windows Python 3.13/3.14 tests (141/141 on 3.14) and Windows onefile metadata/native audit, offscreen startup: [Actions #43597586127](https://github.com/Valik2005/pdf-compressor/actions/runs/43597586127). This proof applies to that run's specific source commit; any subsequent code change needs fresh CI.
- [x] Safe one-way sync from development into the private 2.8.1 Testing branch succeeded, preserving the private reporter: [Actions #43597742514](https://github.com/Valik2005/pdf-compressor/actions/runs/43597742514).

## Done — source checks and historical signing tooling (signing path is dormant)

- [x] Six required pinned upstream archives (PyMuPDF, MuPDF, PySide6/Shiboken, QtBase, QtSvg, QtImageFormats) and 71 license/notice records verified in [Actions #43596777350](https://github.com/Valik2005/pdf-compressor/actions/runs/43596777350); catalog `docs/source-archives-2_8.json`.
- [x] Qt user-relink capability tested on real Windows 2.8 onefile with a resource-modified Qt DLL and offscreen startup: [Actions #43596866323](https://github.com/Valik2005/pdf-compressor/actions/runs/43596866323), documented in `docs/LGPL_RELINKING_2_8.md`.
- [x] **Historical only:** GitHub Actions manual SignPath workflow, PE metadata, signature/timestamp checks and post-sign SHA-256 were prepared before the Foundation declined. Do **not** run them for unsigned v2.8.
- [x] **Historical only:** Three-file signed-release assembler and associated tests were prepared. The **different unsigned** packager and manual-only publishing workflow below are the active v2.8 path. No automatic tag or GitHub Release.
- [x] Static release gate checker successfully verified manual-only signing/publication rules: [Actions #43597275586](https://github.com/Valik2005/pdf-compressor/actions/runs/43597275586).
- [x] Obsolete signed-only README [PR #18](https://github.com/Valik2005/pdf-compressor/pull/18) was **closed**; unsigned post-publication README [draft PR #29](https://github.com/Valik2005/pdf-compressor/pull/29) is prepared but must stay unmerged until v2.8 assets are publicly available.
- [x] Documentation conflict between PR #17 and current `main` resolved; public README and public signing policy still state current unsigned v2.7.1.
- [ ] **Latest exact-commit integrated test:** source archives, native bundle inventory, Windows EXE, pinned Python packages and package licenses checked *together*, and report `presign-technical-evidence.json` attached. Workflow `review-28-final-unsigned.yml` now performs this; requires final CI success at the actual release-candidate commit.

## Unsigned release CI (not a publication)

- [x] Implemented tools/assemble_unsigned_release_28.py: exactly three files, mandatory six archives, Windows NotSigned check, license/notice ZIPs, reproducible cross-job source/EXE checksums; rejects prior signed evidence.
- [x] Added tests/test_28_unsigned_release_packaging.py covering correct unsigned packaging and fail-closed tamper cases.
- [x] Added the stage-unsigned-three-files job to .github/workflows/review-28-final-unsigned.yml; uploads review-only GitHub Actions artifact after all earlier checks succeed.
- [x] Prepared owner-only, manual .github/workflows/publish-v2_8-unsigned.yml; it demands successful **main** same-commit acceptance plus explicit release and completed license review confirmations, validates three asset hashes, and never uses SignPath.
- [x] Completed six-job same-commit staging on [Actions #43619807237](https://github.com/Valik2005/pdf-compressor/actions/runs/43619807237): **168/168 Windows tests on Python 3.13 and 3.14**, six upstream source hashes, 73 notices (including exact OpenSSL 3.5.9 LICENSE/AUTHORS), NotSigned EXE, integrity report and precisely three review-only assets. [ ] Recheck these gates on the eventual final **main** commit after owner-approved merge.
- [x] Rechecked the updated release-candidate HEAD `42038072c7a0f36142d5b3be8249a502043a18de` using the complete [six-job unsigned Windows + source/archive acceptance #43620339052](https://github.com/Valik2005/pdf-compressor/actions/runs/43620339052): **168/168 tests** on each Python 3.13 and 3.14, correct Windows NotSigned status, intact hash/source cross-audit, six upstream sources, updated OpenSSL attribution and three exact private review assets [artifact #14124111415](https://github.com/Valik2005/pdf-compressor/actions/runs/43620339052/artifacts/14124111415). **Still NOT released; must retest any later final main revision.**

## Updated proof — exact Windows native collection-source audit

- [x] [Six-job release-branch acceptance #43645438667](https://github.com/Valik2005/pdf-compressor/actions/runs/43645438667) on commit `2495e0b40fa77450cdec0691e343fc551a58b545`: Windows Python 3.13 and 3.14, real versioned unsigned Windows onefile, original six-source notices, independent native byte-origin PLUS new actual PyInstaller collection-source SHA/size check, and exact three staged private unsigned assets. **Technical success is not a legal signoff or public release.**
- [x] New evidence `native-collection-sources.json` is included in the private Windows candidate and the packaged source/license ZIP. Source-scope counts: 51 verified wheel sources, 22 Python-installation sources, two installed-program OpenSSL `-x64` DLLs, and 43 unclassified-builder-path UCRT/API-set components. Review exact Microsoft and OpenSSL redistribution rights independently.
- [ ] Re-run full six-job acceptance on the **latest merged release-branch commit** if documentation or source changes again. This will also be required after an owner-authorized merge into `main`.
- [ ] Independent applicable third-party license review and **explicit owner approval** are separate from successful CI; owner approval before merge to `main`, and another approval before public unsigned publication.

## Removed accidental OpenSSL dependencies — v2.8 candidate

- [x] Enhanced provenance identified `libcrypto-3-x64.dll` and `libssl-3-x64.dll` as unrelated copies from **MySQL Server 8.4** installed on the hosted Windows runner (not pinned dependencies). [PR #42](https://github.com/Valik2005/pdf-compressor/pull/42) deliberately omits these and unused `PySide6/plugins/tls/qopensslbackend.dll`, while retaining Python OpenSSL and Qt Schannel backend.
- [x] [Windows Server 2022/2025 experiment #43650917328](https://github.com/Valik2005/pdf-compressor/actions/runs/43650917328): 205/205 regression tests on each runner, genuine unsigned EXE metadata and startup, 115/115 native members audited, no ambient MySQL/OpenSSL DLLs.
- [ ] After merging the explicit no-ambient-TLS verification gate, repeat the entire six-job acceptance on its **exact final release-branch commit**, then again on `main` after separately authorized merge. The old 118-native ZIP/hashes do not identify the new candidate.

## Blocking review — not replaceable by an automated test

- [ ] Review all applicable third-party license obligations and individual native/codec attribution, AGPL/MuPDF source/producer notices, Qt LGPL user-relink rights, and the status of Microsoft runtime/system-library exceptions for the exact shipped binary. `docs/THIRD_PARTY_REVIEW_2_8.md` identifies the audit evidence and unanswered questions. **Technical provenance is not legal certification.**
- [x] SignPath Foundation decision received: **declined for insufficient independent public recognition** (14 Nov 2026). No free signing access currently available. A future reapplication requires greater adoption; SignPath-specific license/dual-licensing eligibility remains unresolved until a future approval, and general AGPL/LGPL obligations apply regardless.
- [x] **SignPath configuration is not a blocking task for unsigned v2.8.** The old setup requirements are historical; a different future signing application would require its own approval and separate maintainer decision. Never configure or run the signing workflow as part of this unsigned release.

## Signed-release path — dormant until a DIFFERENT future SignPath approval

**Do not execute any of these steps for the declined application.** All conditions below are contingent on a later successful application and separate maintainer release authorization.

1. [ ] Owner authorizes merging **PR #17** (not preview PR #9) into `main`. Re-run required tests at the final main commit.
2. [ ] Owner explicitly starts `sign-v2_8.yml` on `main`. GitHub-hosted trusted build re-verifies source and licenses **before signing**; each request requires human SignPath approval.
3. [ ] Validate real Windows Authenticode + timestamp + publisher and compute the **post-signing** EXE SHA-256, different from the unsigned one.
4. [ ] Assemble exactly `PDF_Compressor_2_8.exe`, `Third_Party_Sources_and_Licenses.zip`, `SHA256SUMS.txt` from the **same successful signed run** and validate source/license proof and final hashes. The package is held for review; this workflow alone cannot publish.
5. [ ] Owner separately authorizes manual `publish-v2_8-signed.yml` using that successful signed run ID and typed confirmation; verify GitHub's asset hashes, publish only after success.
6. [ ] This older signed path is dormant. If a future signed v2.8 were ever approved, prepare accurate signed-only docs from scratch; **PR #18 is closed** and must not be merged.

## Selected unsigned v2.8 path (preparation authorized; publishing NOT authorized)

1. [ ] Independently clear the remaining exact-binary Qt/PySide6 LGPL, MuPDF AGPL, **retained Python/OpenSSL notices**, Mesa/LLVM, libffi and Microsoft runtime redistribution obligations. The accidental MySQL OpenSSL `-x64` files are excluded from the intended v2.8 binary. Pillow 12.3.0 wheel codec/font notices are already verified; only newly introduced codec dependencies would reopen that specific check.
2. [ ] Obtain explicit owner authorization **before merging PR #17** into `main` (after the release-branch six-job tests and manual license review). Then run the complete acceptance workflow on that exact `main` commit, verify Windows `NotSigned` and all three hashes, and separately obtain explicit owner authorization **before publishing**.
3. [x] Implement a **separate manual unsigned** three-asset packaging/publishing workflow with matching source commit, Windows Authenticode NotSigned evidence, source/license reports and SHA-256. One-run proof: [Actions #43619807237](https://github.com/Valik2005/pdf-compressor/actions/runs/43619807237). The workflow remains dormant until owner explicitly authorizes publication and applicable license obligations are cleared.
4. [x] Prepare bilingual unsigned release notes in docs/RELEASE_NOTES_2_8_UNSIGNED.md and future unsigned README in [PR #29](https://github.com/Valik2005/pdf-compressor/pull/29); do **not merge #29** until actual v2.8 assets are published.

**Never claim an unsigned EXE is signed, assume SignPath approval, merge 2.8.1 Testing code into stable, or ignore unsatisfied license requirements to meet a deadline.**
