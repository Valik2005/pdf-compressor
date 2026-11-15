# PDF Compressor 2.8 — exact-commit license closeout review (15 Nov 2026)

> **Review status: TECHNICAL EVIDENCE REVIEWED; FINAL DISTRIBUTION RIGHTS NOT ATTESTED.** This is an evidence-based maintainer aid, not counsel's opinion, a copyright grant, or the owner's `LICENSE_OBLIGATIONS_REVIEWED` attestation. Keep release publication fail-closed until a responsible person checks the remaining items and personally approves the precise release. This document is deliberately isolated from `main` to avoid changing the accepted source SHA or triggering the public publisher.

## Evidence frozen at current `main`

- Commit: `aef0d42b42072611cf519920ef8ff205cf3a3779`.
- [Final six-job Windows acceptance #43758344901](https://github.com/Valik2005/pdf-compressor/actions/runs/43758344901): 223/223 tests on Python 3.13 and 223/223 on 3.14; actual unsigned Windows EXE built and started; exact Git/EXE/source cross-audit and three-file private staging passed.
- Actual private candidate [artifact #14179183620](https://github.com/Valik2005/pdf-compressor/actions/runs/43758344901/artifacts/14179183620) is *not* a public release. Its independent `presign-technical-evidence.json` reports EXE SHA-256 `2c499d814a7121e62e5bf7f610ef70f2175b9a3c0b3146a35ae32751f6a5cd40`, nine verified upstream archives, 81 notices, 62 native members (42 wheel, 20 Python installation), 62 byte-matched installed origins, and `license_compliance_certified=false`. It **does not** establish original compiler/patch correspondence of every third-party binary.
- The release is **unsigned**. This 62-native candidate does not redistribute Microsoft MSVC/UCRT/API-set DLLs and requires an independently installed official Microsoft VC++ Redistributable x64. Historical 115-native issues must not be transferred to this candidate.
- `app.pyw` and `pdf_engine.py` are not changed by this review.

## 1. Qt 6.12 / PySide6 / Shiboken — LGPLv3 / GPLv3

**Requirements:** actual library source including applicable modifications; full LGPL/GPL terms and prominent notice; corresponding application source/relink ingredients, right to recombine and run an ABI-compatible modified Qt; no restriction on LGPL reverse engineering for debugging. See [Qt LGPL obligations](https://www.qt.io/development/open-source-lgpl-obligations) and [LGPLv3 §4](https://www.gnu.org/licenses/lgpl-3.0.en.html).

**Evidence already present:** pinned QtBase, QtSvg, QtImageFormats and Qt-for-Python upstream source archives; full LGPLv3/GPLv3 texts and component notices in the companion archive; a prominent bilingual Licenses dialog in the application; `docs/LGPL_RELINKING_2_8.md` and `tools/rebuild_onefile_with_qt.py`; Windows [Qt DLL onefile replacement / GUI-start proof #43658575876](https://github.com/Valik2005/pdf-compressor/actions/runs/43658575876). An exact output-EXE hash match after independent compilation is **not** an LGPL requirement.

**Still check:** whether the version-matched *upstream* source archives also cover any relevant vendor-wheel Qt/PySide6 patches and build/recombination materials for **the actual shipped Qt binary**, not only its official source version; whether recipient relinking/running works without a maintainer-controlled key, and the prominent notice/complete license text really *accompany* copies obtained via the standalone EXE download. ABI-preserving PE-resource modification demonstrates replacement plumbing but does not exercise arbitrary source-compiled Qt or guarantee full LGPL compliance.

**Disposition:** substantial required materials present; no identified need to rewrite PDF engine. Final component/source and recipient-rights assessment is still a maintainer decision.

## 2. Mesa 11.2.2 / LLVM 3.6.2 embedded in Qt `opengl32sw.dll`

**Requirements:** preserve actual component copyright statements and applicable conditions. Historical LLVM 3.6.2 uses University of Illinois/NCSA license; do **not** substitute current LLVM Apache 2.0-with-exception text as its license. Mesa components include MIT and other component-specific terms. [Mesa licensing](https://docs.mesa3d.org/license.html); [LLVM 3.6.2 developer/licensing policy](https://releases.llvm.org/3.6.2/docs/DeveloperPolicy.html).

**Evidence already present:** the wheel-matched DLL `PySide6/opengl32sw.dll` SHA-256 `18aedc7a4b610f53bcc7b7a5c5ed9293c7e86f030e3273ad54ed3bb1ebd36702` was inspected and contains Mesa/LLVM historical version strings; both exact-version upstream source tarballs (SHA-256 checked), original Mesa `docs/license.html`, historical LLVM `LICENSE.TXT`, Qt Mesa MIT/Boost texts and extra upstream attribution are included in the source/notice pack.

**Clarification:** the permissive Mesa/LLVM licenses do not generally demand a *byte-for-byte reproducible* binary build or a universal source-code offer merely for redistributing their unmodified binary components. Lack of a matching build SHA **alone** is not proof of noncompliance. However the supplier's exact included/modified subcomponents and license notices still must be covered, and any LGPL covered-work source obligations for Qt remain separate.

**Still check:** reconcile the Qt wheel's Mesa/LLVM compiled-in parts and any third-party patches/extra licenses against actual component provenance, not version strings alone. Obtain vendor build/patch evidence if the Qt corresponding-source obligation demands it.

**Disposition:** legacy licensing mismatch corrected; additional component-attribution/source-mapping confidence remains open.

## 3. Pillow 12.3.0 and image codecs

**Requirements:** distribute the applicable Pillow MIT-CMU and bundled third-party copyright/license notices, including notices for native codecs actually present. The mere presence of a permissively licensed codec in an AGPL app does **not** automatically make every separate codec subject to a stand-alone AGPL source-offer obligation. Review actual copyleft terms if identified. [Pillow license](https://pillow.readthedocs.io/en/stable/about.html); [Pillow 12.3.0 release and embedded SBOM note](https://pillow.readthedocs.io/en/stable/releasenotes/12.3.0.html).

**Evidence already present:** complete ~78 KB LICENSE from the exact installed Pillow wheel in `license-evidence.zip`; independent source tar archive pinned by SHA-256; six Pillow native `.pyd` files matched the installed 12.3.0 wheel; release checks require notices for libavif, libjpeg-turbo, libpng, libwebp, OpenJPEG, TIFF, FreeType, lcms2, HarfBuzz, Brotli and zlib-ng.

**Still check:** identify the *effective native dependency set* (including transitive AV1/WebP codecs, where applicable) using the wheel's software bill of materials and exact six `.pyd` dependencies. Compare all required notices/copyright lines to the **unmodified** installed wheel LICENSE; inspect any extra copyleft or unusual license not captured by name-marker tests.

**Disposition:** most permissive-license notice work is present. Missing exact source-compiler hash for a permissive codec is not by itself a release blocker; an actual missing required notice/license would be.

## 4. PyMuPDF 1.27.2.3 / MuPDF 1.27.2 — AGPLv3

**Requirements:** application must comply with AGPLv3, provide machine-readable corresponding source of the *distributed* covered work (including build/control scripts) with binary distribution, preserve licenses/notices and respect applicable modified-source rules. See [GNU AGPLv3 §6](https://www.gnu.org/licenses/agpl-3.0.en.html) and [PyMuPDF licensing](https://pymupdf.io/licensing).

**Evidence already present:** complete application repo is licensed AGPL-3.0-only; full AGPL text, pinned PyMuPDF/MuPDF sources, native provenance and rebuild instructions are prepared. The publisher targets the **exact accepted main commit** for `v2.8`, accompanied by the matching source/license ZIP. `pdf_engine.py` marks producer for newly created merged/extracted PDFs and intentionally preserves creator/producer information during compression or rotation.

**Clarification:** Artifex's public producer-line guidance says this *ideally* should be retained in PDFs created/modified using its open source code. This is not a sufficient basis to overwrite arbitrary users' existing PDF metadata or call unchanged blank producer values a proven AGPL violation. See [Artifex licensing](https://artifex.com/licensing).

**Still check:** the exact final tag exposes all required application corresponding-source files, recipes, notices and applicable dependencies *at the same time as* EXE publication, and downloadable license/source material is clearly identified with the binary.

**Disposition:** no known AGPL/GPL incompatibility identified in the selected open-source licensing route; final exact-tag source delivery must be verified as an actual completed publication event.

## Required pre-publication decision (not an automated CI result)

1. Review whether Qt/PySide6 wheel-specific source/patch materials and actual LGPL recipient modification rights are sufficiently covered.
2. Review the exact Mesa/LLVM and Pillow codec notice/attribution set, including third-party components that the named-marker tests may miss; add genuinely missing material if found.
3. Ensure complete applicable source and license text *accompany* downloads of the standalone EXE, and the final `v2.8` tag and source bundle really match its commit.
4. A responsible human maintainer independently decides whether this specific, unsigned Windows 62-native package can be redistributed. **Do not send `LICENSE_OBLIGATIONS_REVIEWED` as an AI-authored representation of human review** or mark `license_compliance_certified=true` in a mechanical provenance JSON.

**No source-code change to the compression engine is suggested by this audit.** This review branch should remain separate from `main` until release coordination; merging it before publication changes the main commit and requires a fresh exact-main six-stage release acceptance. Keeping it isolated preserves the already-accepted candidate.
