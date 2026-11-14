# PDF Compressor 2.8 — final pre-release checklist

**Public stable version remains 2.7.1. This checklist does NOT authorize publishing 2.8.**

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

1. [ ] Independently clear the remaining exact-binary Qt/PySide6 LGPL, MuPDF AGPL, OpenSSL `-x64`, Mesa/LLVM, libffi and Microsoft runtime redistribution obligations. Pillow 12.3.0 wheel codec/font notices are already verified; only newly introduced codec dependencies would reopen that specific check.
2. [ ] Obtain explicit owner authorization **before merging PR #17** into `main` (after the release-branch six-job tests and manual license review). Then run the complete acceptance workflow on that exact `main` commit, verify Windows `NotSigned` and all three hashes, and separately obtain explicit owner authorization **before publishing**.
3. [x] Implement a **separate manual unsigned** three-asset packaging/publishing workflow with matching source commit, Windows Authenticode NotSigned evidence, source/license reports and SHA-256. One-run proof: [Actions #43619807237](https://github.com/Valik2005/pdf-compressor/actions/runs/43619807237). The workflow remains dormant until owner explicitly authorizes publication and applicable license obligations are cleared.
4. [x] Prepare bilingual unsigned release notes in docs/RELEASE_NOTES_2_8_UNSIGNED.md and future unsigned README in [PR #29](https://github.com/Valik2005/pdf-compressor/pull/29); do **not merge #29** until actual v2.8 assets are published.

**Never claim an unsigned EXE is signed, assume SignPath approval, merge 2.8.1 Testing code into stable, or ignore unsatisfied license requirements to meet a deadline.**
