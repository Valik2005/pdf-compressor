# PDF Compressor 2.8 — visual-review calibration against 2.7.1 PC results

**Status:** experimental validation, not a legal or visual certificate. Stable 2.7.1 was not modified or republished. No user-provided PDF content or screenshots are stored in this repository.

## Evidence

Independent read-only analysis of **38 matching input/output PDF pairs** from the 2.7.1 user-PC test pack. The full uploaded set also contained reruns and page tools; this calibration intentionally excludes tools and unmatched variants. It includes text, raster scans, color photographs, vector-only documents, precompressed JPEG and mixed content.

For each pair, compare the first, middle and last page where available using RGB thumbnail rendering, constrained to a **256px maximum side**, similar to the opt-in 2.8 GUI. Reference test environment: local Linux Python 3.13, **PyMuPDF 1.26.7 / Pillow 12.3.0**; official Windows EXE uses different, pinned binaries. Results are indicative, not benchmark guarantees.

| Test type | Example result | Mean RGB absolute error on first/middle/last previews |
| --- | --- | ---: |
| Text-only, vector-only unchanged | Recompressed without replacing images | 0.00000 |
| Tiny-printed 4-page scans, JPEG 95% | 2.32 MB → 1.30 MB | 0.00511 |
| Tiny-printed scans, JPEG 48% | 2.32 MB → 326 KB | **0.00699** |
| Color photo 3 pages, aggressive target | 5.52 MB → 635 KB | 0.00285 |
| Color control 3 pages, JPEG 30% | 11.57 MB → 1.06 MB | 0.00480 |
| Stamped scan 2 pages, JPEG 48% | 2.62 MB → 325 KB | 0.00602 |

**Important failure of the original 2.8 prototype:** not a single one of these 38 PDFs exceeded the initial `mean_difference >= 0.08` visual-warning threshold; also, the share of 256px pixels differing by more than 32 RGB levels was zero in all 38 cases. A low thumbnail difference can therefore **miss JPEG-induced softening of fine text**, especially in scans whose characters are part of a bitmap rather than selectable text. Do not classify an unchanged page count and low 256px MAE as proof that fine text was preserved.

## Mitigation implemented in the 2.8 branch

- **Scan-only page identification** from each page's selectable-text presence and embedded-image metadata; no OCR and no full-image decoding required.
- After a raster-only page is recompressed, if the sampled preview changes by more than 0.002 mean RGB difference, show **`raster_detail_needs_review`**. This is *not* a corruption error: read its small letters, stamps and signatures at 200% zoom.
- If there are additional raster-only pages which were not visually sampled (normal in a 14-page scan with a four-page sample) and output size fell by over 10%, show **`unreviewed_raster_pages`** to prevent false reassurance.
- GUI passes the compressor's **actual JPEG quality** and **downscaling flag** to the audit. JPEG quality at or below 35% with major file-size reduction (or at/below 55% for raster-only scans) generates **`low_jpeg_detail_risk`**. Downscaling generates **`image_resolution_reduced`**, regardless of other heuristics.
- Risks are **warnings**, not structural corruption reports. The completed PDF stays available. Errors still cover actual page loss, geometry mismatch, lost selectable text and apparently blank pages.
- Identical scans that were not altered **do not** generate false warnings, even when only a sample was visually rendered.
- Reports include sampled page numbers, JPEG-quality hint, raster-only page count, source and output sizes, known resolution changes and warnings. The GUI remains opt-in and off by default.

## Resource-conscious design

On the above local environment (not the user's Windows PC), independent 256px preview and selectable-text validation took approximately:

| PDF case | Pages | Previewed pages | Approx. elapsed |
| --- | ---: | ---: | ---: |
| Four-page scanned small print | 4 | 4 | 0.06 s |
| Three-page color control | 3 | 3 | 0.14 s |
| Eight-page vector diagram | 8 | 4 | 0.03 s |
| Fourteen-page large scan (identity comparison) | 14 | 4 | 0.08 s |

The timings are **not Windows app measurements** and exclude startup, file-picker interaction, compression and reporting UI. Do not turn them into production promises. Default GUI checks remain capped at four 256px previews with full text/geometry checks on each page, processed in the existing worker thread.

## Next acceptance gates

1. On the user's own PC, run opt-in QA on the existing 2.7.1 test pack and review the HTML/JSON reports.
2. Compare warnings against actual cropped scan samples at **200% zoom**. Neither a warning nor a silent thumbnail guarantees character readability.
3. Confirm UI responsiveness, cancellations and RAM/CPU on typical and long scanned documents.
4. Run latest Windows tests, real single-EXE build/smoke, and third-party source/license checks before a candidate is considered.
5. Do not merge or publish v2.8 until the user has accepted on-device testing.
