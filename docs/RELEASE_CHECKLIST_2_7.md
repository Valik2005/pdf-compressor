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
- [ ] Build and smoke-test the experimental Virtual Keyboard-free candidate; compare new archive and checksum.
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

The successful GitHub Actions runs test source code; they do not build or audit the executable. The preview test does not validate a future rebuild.
