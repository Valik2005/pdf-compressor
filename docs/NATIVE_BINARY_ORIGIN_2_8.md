# PDF Compressor 2.8 — exact Windows DLL/PYD origin audit

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
