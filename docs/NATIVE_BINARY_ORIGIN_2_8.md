# PDF Compressor 2.8 — exact Windows DLL/PYD origin audit

**CURRENT OWNER-SELECTED v2.8 (15 Nov 2026):** The isolated release branch now contains the **62-native** Windows x64 version (no embedded Microsoft MSVC/UCRT/API-set DLLs). Source ancestor `392ddd30`; merged release branch `8317b588`. The owner independently ran the exact Windows 2025 artifact EXE SHA-256 `00a878796abad875546c556db63e9bb18af3137e3f7226c6610b1deb91a4b166` on Windows 11 build 26200: official Microsoft VC++ Redistributable x64 v14.51.36247.00 present, GUI smoke passed, Licenses dialog opened. User acceptance of the functional PDF compression engine was recorded separately on 14 Nov using 2.8.1 Testing; no compression-code change is part of this packaging. The `ca56a3e2...` sibling same-source review EXE had all 62 DLL/PYD bytes equal to the user-tested EXE but a different whole-file SHA; never represent one as the other. Current release-branch commits after `392ddd` require same-commit CI before publication. No merge into `main`, no public tag, and no legal license approval is implied. 115-native and older inventories below are **historical, not current candidate contents**. The EXE requires the *separately installed* official Microsoft VC++ Redistributable x64; this build does **not** redistribute Microsoft runtime DLLs. Third-party LGPL/AGPL/Mesa/LLVM/other obligations and separate owner authorization remain prerequisites to a public release. Smart App Control may block unsigned EXEs; do not weaken user security to bypass it.

**Purpose:** verify the binary identity of native code packed in the *unsigned*
onefile EXE against the exact Windows builder's installed Python wheels or
CPython installation. The final ZIP contains
`reports/native-binary-origin.json`.

The GitHub Actions Windows stage runs
`tools/audit_native_binary_origin_28.py` **after** the isolated unsigned
PyInstaller 6.22.3 build and **before** source/archive and publication checks.
It independently decompresses each native CArchive DLL/PYD (without executing
it), recomputes SHA-256, then searches installed package distribution records
for the exact same file hash. Packages: PyMuPDF, PySide6,
PySide6_Essentials, PySide6_Addons, shiboken6 and Pillow. When the package has
a wheel RECORD SHA-256 entry, that hash is checked too.

- Files from installed wheel directories (PySide6, Shiboken, Pillow,
  PyMuPDF) **must match** the corresponding build-installed package bytes
  or the candidate is rejected.
- Root-level CPython runtime DLLs are compared against the runner's Python
  installation. Root-level OpenSSL and Windows DLLs with no matched source are
  explicitly retained as **unverified-build-origin**, not called system
  libraries or licensed redistributables.
- Results include relative archive member name, SHA-256, byte length, matching
  package and package version, and whether its wheel RECORD hash matches.
  No absolute directory paths from the builder are written.
- One-commit `verify_presign_evidence_28.py` binds this report to the exact
  release EXE and revision. The unsigned three-file packager and manual-only
  release publisher also demand the report.

## OpenSSL dependency correction in v2.8

The enhanced source collection audit traced two previously unclassified
OpenSSL `-x64` DLLs to the Windows GitHub runner's
`MySQL/MySQL Server 8.4/bin` tree. Those were not pinned application
dependencies. The release PyInstaller spec now excludes exactly
`libssl-3-x64.dll`, `libcrypto-3-x64.dll` and the unused Qt
`PySide6/plugins/tls/qopensslbackend.dll`; this is a deliberate offline
application trim, **not a waiver of their licenses**. Python's OpenSSL
`libssl-3.dll`, `libcrypto-3.dll` and `_ssl.pyd` remain.

The new baseline is **115 native entries** rather than 118. A
two-Windows-runner integration check verified every remaining member,
all PDF/GUI tests and EXE startup:
[Actions #43650917328](https://github.com/Valik2005/pdf-compressor/actions/runs/43650917328).
The final release-branch six-job acceptance must still pass at the exact
post-change SHA, then separately on the owner-authorized `main` commit.

## Independent collection-source audit (v2.8 unsigned)

Before packaging the EXE, `release_windows_2_8.spec` runs
`tools/audit_native_collection_sources_28.py` against **actual PyInstaller
Analysis records after Qt pruning**. It computes the source bytes' SHA-256
and size and records whether each source came from a named, versioned wheel
(with wheel RECORD verification where present), Python installation,
Windows system, Windows SDK, another installed program or an unclassified
builder path.

Its `native-collection-sources.json` is shipped within the audited source
and license evidence ZIP and remains available in private CI artifacts.
Absolute Windows account/build paths are not included. The independent
release verifier decomposes the final EXE again and requires **every native
member** to be present exactly once with identical name, bytes, size and
source Git commit. The isolated unsigned staging and manual publish gates
both refuse an incomplete or mismatched collection-source report.

Collection-source evidence helps identify which Windows/Qt/OpenSSL files
the build actually copied. It **cannot establish a copyright license**,
a full reproducible third-party build or vendor permission for
redistribution. The official runtime and upstream license reviews stay
separate.

**IMPORTANT:** Matching bytes to an installed pip wheel establishes **how the
builder obtained those bytes**. It is not proof of binary-to-upstream-source
correspondence, permission to redistribute Microsoft's proprietary runtimes,
the complete obligations for bundled OpenSSL/Mesa/LLVM/Pillow codecs,
AGPL/MuPDF producer notices, or LGPL Qt recipient-relinking rights.

For unresolved Microsoft rights, see
`docs/MICROSOFT_RUNTIME_REVIEW_2_8.md`.
For the broader license audit, see `docs/OSS_LICENSE_AUDIT_2_8.md`.
These remaining obligations must be reviewed on the actual final build before
the owner can authorize publication. **No signing key or certificate is involved.**
