# PDF Compressor 2.8 — final pre-release checklist

**Public stable version remains 2.7.1. This checklist does NOT authorize publishing 2.8.**
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

## Done — pre-sign source and build tooling

- [x] Six required pinned upstream archives (PyMuPDF, MuPDF, PySide6/Shiboken, QtBase, QtSvg, QtImageFormats) and 71 license/notice records verified in [Actions #43596777350](https://github.com/Valik2005/pdf-compressor/actions/runs/43596777350); catalog `docs/source-archives-2_8.json`.
- [x] Qt user-relink capability tested on real Windows 2.8 onefile with a resource-modified Qt DLL and offscreen startup: [Actions #43596866323](https://github.com/Valik2005/pdf-compressor/actions/runs/43596866323), documented in `docs/LGPL_RELINKING_2_8.md`.
- [x] GitHub Actions manual-only SignPath workflow, 2.8-specific PE metadata, approval-dependent artifact configuration, signature/timestamp checking and **post-sign** SHA-256 prepared.
- [x] Exact three-file signed release assembler with synthetic fail-closed tests, dedicated release-notes and a separate manual publishing workflow prepared. No automatic tag or GitHub Release.
- [x] Static release gate checker successfully verified manual-only signing/publication rules: [Actions #43597275586](https://github.com/Valik2005/pdf-compressor/actions/runs/43597275586).
- [x] Future README 2.8 download links/metadata prepared in [draft PR #18](https://github.com/Valik2005/pdf-compressor/pull/18) **but not merged** before public release.
- [x] Documentation conflict between PR #17 and current `main` resolved; public README and public signing policy still state current unsigned v2.7.1.
- [ ] **Latest exact-commit integrated test:** source archives, native bundle inventory, Windows EXE, pinned Python packages and package licenses checked *together*, and report `presign-technical-evidence.json` attached. Workflow `review-28-final-unsigned.yml` now performs this; requires final CI success at the actual release-candidate commit.

## Blocking review — not replaceable by an automated test

- [ ] Review all applicable third-party license obligations and individual native/codec attribution, AGPL/MuPDF source/producer notices, Qt LGPL user-relink rights, and the status of Microsoft runtime/system-library exceptions for the exact shipped binary. `docs/THIRD_PARTY_REVIEW_2_8.md` identifies the audit evidence and unanswered questions. **Technical provenance is not legal certification.**
- [ ] Obtain/confirm SignPath's decision on open-source eligibility, especially its prohibition on non-OSS/proprietary code and terms about dual licensing. The free application was **submitted 14 Nov 2026**, but not yet approved.
- [ ] After approval, owner configures SignPath GitHub origin, MFA, approved project and manual approver, organization, signing policy and explicit `SIGNPATH_ARTIFACT_CONFIGURATION_SLUG`. Its file restrictions must match `ProductName = PDF Compressor by Valik2005`, ProductVersion/FileVersion `2.8.0.0` and the sole EXE `PDF_Compressor_2_8.exe`.

## Steps performed only AFTER approval and final source freeze

1. [ ] Owner authorizes merging **PR #17** (not preview PR #9) into `main`. Re-run required tests at the final main commit.
2. [ ] Owner explicitly starts `sign-v2_8.yml` on `main`. GitHub-hosted trusted build re-verifies source and licenses **before signing**; each request requires human SignPath approval.
3. [ ] Validate real Windows Authenticode + timestamp + publisher and compute the **post-signing** EXE SHA-256, different from the unsigned one.
4. [ ] Assemble exactly `PDF_Compressor_2_8.exe`, `Third_Party_Sources_and_Licenses.zip`, `SHA256SUMS.txt` from the **same successful signed run** and validate source/license proof and final hashes. The package is held for review; this workflow alone cannot publish.
5. [ ] Owner separately authorizes manual `publish-v2_8-signed.yml` using that successful signed run ID and typed confirmation; verify GitHub's asset hashes, publish only after success.
6. [ ] Only after v2.8 is publicly accessible, merge bilingual README [PR #18](https://github.com/Valik2005/pdf-compressor/pull/18) so direct download links point to real assets.

**Never claim an unsigned EXE is signed, assume SignPath approval, merge 2.8.1 Testing code into stable, or ignore unsatisfied license requirements to meet a deadline.**
