# PDF Compressor 2.7.0 — release readiness checklist (draft)

Base branch: `develop/2.7-smartfit`. Published stable version: `v2.6.0`.
Do not merge into `main`, create a public GitHub Release, or mark the EXE stable until all release blockers are resolved and authorized.

## Confirmed as of 2026-11-08

- [x] Manual compression, SmartFit target reporting and sample PDF tools exercised on Windows 11.
- [x] Cancellation was observed; no partial result left in the tested scenario.
- [x] Full-screen list-layout fix manually verified.
- [x] Local one-file preview EXE built and opened on Windows 11.
- [x] GitHub Actions CI on merged UI-fix commit `4424feef`: 40 tests passed for each of Python 3.13 and 3.14.
- [x] SHA-256 independently verified for **that preview file only**: `D9495B8D6C6D4EDD1C5EC952DD0E65D59EED78A785C1635621B13CCB3483D985`.

## Preview EXE bundle findings (2026-11-08)

- [x] Preview EXE SHA-256 and size match its build manifest; source commit `7738001` and clean tree recorded.
- [x] PyInstaller archive inventoried: 306 entries; Qt Virtual Keyboard (GPLv3 or commercial) and Qt PDF were found.
- [x] Build and smoke-test the experimental Virtual Keyboard-free candidate; compare new archive and checksum.
- [ ] Resolve required notices, corresponding-source/relinking obligations for all bundled Qt/MuPDF components (see `docs/EXE_BUNDLE_AUDIT_2_7_PREVIEW.md`).

## Pending before public release

- [ ] Merge and re-test all pending PRs with the **final** source commit, then re-run Windows CI on the resulting head.
- [ ] Rebuild the EXE from that **final** commit and smoke-test it. The older preview checksum will no longer describe the release build.
- [ ] Generate `build-manifest.json` using `tools/release_manifest.py`; archive the exact dependency versions, builder version, Git commit and binary SHA-256 with release records.
- [ ] Test on a clean Windows machine without installed Python and verify no additional files are required.
- [ ] Review all bundled Qt DLLs/plugins and their license variants. Verify compliance with LGPL replacement/relinking rights for the selected `--onefile` bundle or change packaging/licensing.
- [ ] Include applicable **full third-party license texts, notices, and source availability/offers**, including all transitive components; draft inventory: `docs/THIRD_PARTY_NOTICES_2_7.md`.
- [ ] Review AGPL distribution requirements for the application/PyMuPDF and producer notices where applicable.
- [ ] Confirm runtime functionality and integrity across text, scans, vector, shared images, cancellation, merge, split and rotate with final binary.
- [ ] Finalize 2.7 release notes, tagging, asset names, checksums and release announcement.
- [ ] Explicit maintainer approval to merge `develop/2.7-smartfit` into `main` and publish the release.

The general GitHub Actions test matrix checks source. A separate experimental Windows onedir workflow now builds and audits a one-folder candidate; that does not certify the final onefile release EXE or satisfy license requirements.

## Virtual Keyboard-free preview verification (2026-11-08)

- [x] New EXE SHA-256 independently confirmed: `8b65cdaf950b8ca1598ee26791e69194a4979f5dd601738f732224d489b7bdca`.
- [x] Bundle audit reports 304 archive entries and no Qt Virtual Keyboard; maintainer confirms Windows operation.
- [x] Locally generate matching `license-review-build-manifest.json` (command output confirms matching SHA-256); previously uploaded `build-manifest(1).json` still belongs to old binary.
- [x] Run `tools/collect_license_evidence.py` and inspect resulting 9-file archive.
- [ ] Obtain full LGPL/GPL/AGPL license texts, complete source and Qt relinking proof; the collected archive is incomplete.
- [ ] Complete all conditions documented in `docs/RELEASE_LICENSE_EVIDENCE_2_7.md` before publishing.

## Separate-DLL experimental candidate

- [x] Windows GitHub Actions run [42470112055](https://github.com/Valik2005/pdf-compressor/actions/runs/42470112055) builds the pinned-dependency onedir candidate; 40 Qt DLLs external, 0 Virtual Keyboard files.
- [x] Automated Windows offscreen GUI startup smoke test [#42470397048](https://github.com/Valik2005/pdf-compressor/actions/runs/42470397048) passed with external Qt DLLs.
- [ ] Complete manual Windows onedir smoke test before proposing the alternate packaging.
- [ ] Verify real replacement/rebuild with a compatible user-modified Qt DLL plus full source/notice obligations.

## Corresponding-source archive provenance

- [x] Document exact upstream archive names/official URLs for Qt 6.12.0, PySide6 6.12.0 and PyMuPDF 1.27.2.3 (`docs/source-archives-2_7.json`).
- [x] Pin publicly published SHA-256 for PyMuPDF sdist and optional QtBase subset, with fail-closed source verifier.
- [ ] Acquire required full Qt, Qt for Python and PyMuPDF sources under maintainer control and independently verify their checksums; Qt full and PySide6 published SHA-256 still need confirming.
- [ ] Verify the archives contain the actual corresponding source for all native libraries/plugins in the final bundle, not merely matching version labels.
