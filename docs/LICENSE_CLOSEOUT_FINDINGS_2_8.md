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

**Clarification:** the permissive Mesa/LLVM license terms alone generally do not demand a *byte-for-byte reproducible* binary build. Lack of a matching build SHA **alone** is not proof of noncompliance. **But** the combined executable is distributed under AGPLv3, whose corresponding-source obligation is broader than a permissive library's standalone license. When a native component is part of the covered combined work and is not an excluded System Library, its corresponding source may need to accompany the EXE **even if the component uses MIT/NCSA terms**. See GNU GPL FAQ, *AGPLv3 Corresponding Source*. A matching original source version/patch set is still an evidence question.

**Still check:** reconcile the Qt wheel's Mesa/LLVM compiled-in parts and any third-party patches/extra licenses against actual component provenance, not version strings alone. Obtain vendor build/patch evidence if the Qt corresponding-source obligation demands it.

**Disposition:** legacy licensing mismatch corrected; additional component-attribution/source-mapping confidence remains open.

## 3. Pillow 12.3.0 and image codecs

**Requirements:** distribute the applicable Pillow MIT-CMU and bundled third-party copyright/license notices, including notices for native codecs actually present. **In addition**, AGPLv3/GPLv3 corresponding-source rules must be evaluated for all non-System Library modules actually linked into the combined EXE, even if their own standalone licenses are permissive; do not mistake license-text coverage for AGPL source coverage. [GNU FAQ on AGPL corresponding source](https://www.gnu.org/licenses/gpl-faq.html#AGPLv3CorrespondingSource); [Pillow build dependency guidance](https://pillow.readthedocs.io/en/stable/installation/building-from-source.html).

**Evidence already present:** complete ~78 KB LICENSE from the exact installed Pillow wheel in `license-evidence.zip`; independent source tar archive pinned by SHA-256; six Pillow native `.pyd` files matched the installed 12.3.0 wheel; release checks require notices for libavif, libjpeg-turbo, libpng, libwebp, OpenJPEG, TIFF, FreeType, lcms2, HarfBuzz, Brotli and zlib-ng.

**Still check:** identify the *effective native dependency set* (including transitive AV1/WebP codecs, where applicable) using the wheel's software bill of materials and exact six `.pyd` dependencies. Compare all required notices/copyright lines to the **unmodified** installed wheel LICENSE; inspect any extra copyleft or unusual license not captured by name-marker tests. Then make the applicable **compiled non-System Library component sources** available in the durable, same-release corresponding-source package or document an applicable exception, rather than supplying only the Pillow sdist and notices.

**Disposition:** native codec notices are well covered, but **AGPL corresponding-source completeness remains a specific unresolved release blocker**, because the current nine-archive pack does not enumerate the separate codebases statically incorporated into Pillow wheels. Lack of an identical rebuilt SHA is not the problem; lack of a verified source-to-embedded-module inventory is.

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


## 5. New decisive source-coverage finding (16 Nov 2026)

This is a **concrete packaging/evidence gap**, not a demand to obtain a paid certificate or a generic lawyer's stamp.

- The exact release catalog `docs/source-archives-2_8.json` marks only **nine** source archives as required: PyMuPDF, MuPDF, PySide6/Shiboken, QtBase, QtSvg, QtImageFormats, Pillow, Mesa and LLVM. There are **no separately named source archives** for CPython, OpenSSL, libffi or the third-party native libraries that Pillow's Windows build incorporates. A complete license notice is not the source code.
- `tools/assemble_unsigned_release_28.py` enforces `SOURCES = 9`, copies only those nine archives under `sources/`, then packages the **different** `license-evidence.zip`. `tools/verify_presign_evidence_28.py` verifies hashes, notices and 62 exact native hashes but does **not** verify the full transitive corresponding source of statically linked image codecs.
- Official [Pillow 12.3.0 Windows build script](https://github.com/python-pillow/Pillow/blob/12.3.0/winbuild/build_prepare.py) describes separately built dependencies; its [version catalog](https://github.com/python-pillow/Pillow/blob/12.3.0/.github/dependencies.json) pins the following **upstream build-input candidates**. These are **NOT all claimed present** in the shipped binary; inclusion needs exact wheel/native confirmation:

| Upstream Pillow Windows build candidate | Version in Pillow 12.3.0 build input | What must be established |
| --- | --- | --- |
| libjpeg-turbo | 3.1.4.1 | JPEG codec linkage and source/notice |
| zlib-ng | 2.3.3 | compressed image support |
| libwebp | 1.6.0 | WebP codec linkage and source/notice |
| libtiff | 4.7.1 | TIFF codec linkage and source/notice |
| libpng | 1.6.58 | PNG codec linkage and source/notice |
| FreeType | 2.14.3 | font support and applicable license |
| Little CMS | 2.19.1 | color-profile engine |
| OpenJPEG | 2.5.4 | JPEG2000 codec linkage |
| HarfBuzz | 14.2.1 | text rendering/shaping |
| Brotli | 1.2.0 | decompression/codec dependency |
| libavif | 1.4.2 | AVIF and selected AV1 backends |
| xz / liblzma | 5.8.3 | TIFF compression, if included |

- Other candidates in that build input include FriBidi 1.0.16, BZip2 1.0.8, Zstandard 1.5.7 and libimagequant 4.4.1. The official [Pillow instructions](https://pillow.readthedocs.io/en/stable/installation/building-from-source.html) state that normal Pillow binary wheels do **not** enable GPLv3 libimagequant support; do **not** assume every build-input candidate was shipped.
- CPython 3.14.10 and two CPython-derived OpenSSL 3.x DLLs are bundled as native members and have license notices; **separate original CPython/OpenSSL source archives are not in the nine-source pack.** Whether particular components qualify as System Libraries for the GPL/AGPL definition must be evaluated, rather than assumed either way. The existing source bundle contains original upstream OpenSSL 3.5.9 `LICENSE.txt` and `AUTHORS.md`, not its whole source tree.
- Exact native origin **is** established at the wheel/Python-install layer (62/62 matches), but this does **not** establish source coverage within each compiled wheel. A wheel LICENSE and a wheel RECORD hash answer different questions.

### Technical closeout needed, with no PDF engine/UI modifications

1. At the accepted Windows build, generate a **member → vendored/native library → exact version → compiled/static/dynamic/System Library status → source location + copyright notice** table. Use actual six Pillow `.pyd` and the Qt software-renderer `opengl32sw.dll` inventories, vendor build metadata and official dependency catalog; do not blindly equate all dependency catalog candidates with shipped code.
2. For non-System Library code actually included in the AGPL-distributed combined executable, supply actual corresponding source (including applicable patches/build scripts) under the release owner's control, not just upstream source links or a permissive `LICENSE` text. Exclude unused components based on evidence.
3. Review Qt 6.12/PySide6 wheel build-specific source/patch availability and the recipient's actual ability to recompile a compatible Qt and run the relinked EXE; the verified PE-resource replacement is good evidence but not a complete Qt source-compile test.
4. Only then re-run exact-commit source/EXE acceptance, retain the no-Microsoft-DLL property, and make same-tag source and three assets available **together**. Have the responsible owner attest the specific, documented review before enabling the already-coded publisher.

**Current conclusion: NO UNSUPPORTED CLAIM OF COMPLETE COMPLIANCE.** Existing technical acceptance and licensing notices are real and valuable, but their coverage is not a one-to-one inventory of all code compiled into the distributed EXE. Merely repeating the same nine-source CI run cannot resolve this gap. No paid commercial license is inherently needed, and no changes to `pdf_engine.py` / `app.pyw` are indicated.
