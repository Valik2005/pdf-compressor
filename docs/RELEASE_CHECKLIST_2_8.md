# PDF Compressor v2.8 — release gate (NOT FOR RELEASE yet)

**Status: preparation only; v2.7.1 remains the public stable release.**
Owner: [Valik2005](https://github.com/Valik2005). Release branch: `develop/2.8-quality-audit`; PR [#9](https://github.com/Valik2005/pdf-compressor/pull/9). Internal instrumentation: `testing/2.8.1-automatic-test-report`, **must never merge into public release**.

## Current engineering evidence (14 November 2026)

- [x] Two complete user test archives of the **separate 2.8.1 Testing** program: the first had 18 operations (11 successful, 4 honest target misses, 3 cancelled); the second had 2 additional successful operations with quality warnings.
- [x] Original and output PDF #04 / #10 checked side by side across all 6 pages: intact page count, page geometry, selectable text and image dimensions. **Lossy JPEG 48%/27% visibly degraded fine raster details**; the warning is appropriate and is **not** an assurance of unmodified images.
- [x] Candidate 2.8 and 2.8.1 ran automated Windows Python 3.13/3.14 tests and onefile launch smoke, with separate documented runs in PR #9 and Issue #10. **Each later change needs its own fresh check; historical CI is not final release evidence.**
- [ ] QA export privacy: defaults must remove absolute local directories from both HTML/JSON. Track [PR #14](https://github.com/Valik2005/pdf-compressor/pull/14); verify tests, merge only into normal development, let existing automatic *one-way* sync carry the change to Testing.
- [ ] Recheck final branch with Windows 3.13/3.14 tests, GUI offscreen smoke, sample PDFs and a verified Windows onefile artifact. Measure no unreasonable regressions in responsiveness/RAM for 2.8's opt-in extra QA step.
- [ ] Replace `APP_VERSION = "2.8-preview"` only for the approved final stable version; do not silently rename prerelease builds.
- [ ] Confirm the test reporter, export history, or any testing-only module is **absent** from official release source and EXE. No merge from `testing/*` into `develop/*` or `main`.

## Required licensing and supply-chain checks — build-specific

- [ ] Obtain final onefile binary and exact `build-manifest.json`, `bundle-audit.json`, `native-source-mapping.json` from the **same** source revision and pinned build dependencies.
- [ ] Check every embedded native component's actual license, required notices and corresponding source, including PyMuPDF/MuPDF (AGPL), Qt/PySide6/Shiboken (LGPL/GPL, Qt plugins), OpenSSL, Pillow/codecs, libffi and Python; no proprietary redistributables incompatible with SignPath Foundation's conditions. A source category assignment by filename is only an inventory.
- [ ] Verify all six pinned source archives in `docs/source-archives-2_7.json` against authoritative upstream hashes; versions may only be reused from 2.7.1 if the **final v2.8 binary** really bundles the same components. Preserve notices and full license texts.
- [ ] Recheck Qt LGPL requirements for the actual **onefile** packaging and the documented user-replacement/relinking instructions; do not equate onedir tests or archive mapping to a legal conclusion.
- [ ] Confirm final source/package distribution fulfils AGPL/LGPL and any applicable corresponding-source obligations. Explicitly resolve ambiguities instead of declaring the audit legally certified.
- [ ] Check privacy and GUI export on disk. User PDFs must stay offline; no automatic network diagnostics.

## Free signing — optional external gate, not already achieved

- [x] Maintainer submitted a SignPath Foundation OSS application on **14 Nov 2026** (confirmation screen: 'Form submitted'). No approval or certificate is implied.
- [x] Public policy published in `main` as `docs/CODE_SIGNING_POLICY.md` after PR #13. **Signed builds do not yet exist.**
- [ ] Wait for SignPath approval, then configure repo origin, approved signing policy, artifact restrictions for product name/version, GitHub Actions secret/variables, MFA and manual per-release approval. Test only from `main`.
- [ ] Use [draft PR #12](https://github.com/Valik2005/pdf-compressor/pull/12) as the starting point for the future signing workflow. Review it against current SignPath docs and pin stable actions where practical. Ensure a PE VERSIONINFO product name and version in the EXE that match restrictions.
- [ ] After SignPath approval and final approved merge into `main`, build a final EXE, sign it, verify certificate subject and timestamp with Authenticode / signtool, verify signed SHA-256, and check `signature-verification.json`. Signing modifies EXE bytes, so never copy the **unsigned** hash into public checksums.
- [ ] If SignPath is not approved, do not claim a signature or purchase a paid certificate without the maintainer's permission. Decide explicitly whether to proceed unsigned.

## Final *three* public assets (after authorization)

1. `PDF_Compressor_2_8.exe` — final signed Windows x64 executable **only if real signature verified**; do not upload 2.8.1 Testing.
2. `Third_Party_Sources_and_Licenses.zip` — exact sources, licenses, notices, build audits and LGPL relinking instructions corresponding to the final binary.
3. `SHA256SUMS.txt` — checksums for the **final signed EXE** and license/source ZIP.

- [ ] Adapt the previously proven 2.7.1 3-file assembly gate for **2.8**; the current `tools/assemble_patch_release.py` intentionally refuses names other than 2.7.1, and its binary audit hashes are for the unsigned file. Do not bypass either invariant just to package a file.
- [ ] Use `docs/RELEASE_NOTES_2_8.md`, verify the complete README download link still points to the published stable release until 2.8 exists.
- [ ] Ask for **explicit maintainer approval** before merging PR #9, creating tag v2.8, updating the public download badge, or publishing a GitHub Release. Passing CI alone is not release approval.

## Optional QA limitations that must be conveyed to end users

PDF Compressor 2.8 can compare PDF page count, geometry and selectable text, and sample thumbnails at bounded resolution. It performs **no OCR** and cannot certify fine print, image textures, signatures, seals or all unrendered pages. Strong JPEG compression may preserve document structure while visibly lowering raster quality; it should warn the user and keep the completed file. The opt-in quality check costs extra time and memory.
