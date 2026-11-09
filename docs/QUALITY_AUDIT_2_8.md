# PDF Compressor 2.8 — Quality Review (development preview)

## Status

**2.8 is NOT released.** Stable public Windows EXE remains [2.7.1](https://github.com/Valik2005/pdf-compressor/releases/tag/v2.7.1). This branch prepares the first 2.8 feature and must not replace a public EXE before acceptance testing on the user's Windows PC.

## Purpose

After compression, offer an **optional automatic quality review** for each result. Results are diagnostic, not a claim that small print, scanned seals, signatures, fine details or all images have been preserved. Do not silently discard a PDF just because a visual warning appears.

## Current implementation

- `pdf_quality.py` — pure offline quality-review engine with **no Qt GUI dependency**. It never modifies its original or output PDF.
- `app.pyw` — an opt-in checkbox labelled **«Проверять качество после сжатия (дополнительное время)»**, off by default until the CPU/RAM cost is measured on low-end hardware. The analysis runs in the existing worker thread after successful compression and does not freeze the GUI.
- In the GUI the automatic review examines all pages for selectable-text and page-geometry integrity and renders **at most four pages** at **256-pixel maximum edge** to flag large color/content changes. A completed PDF is retained even when its quality review is cancelled or fails.
- The full standalone command-line review can sample at most 32 pages with thumbnails up to 640 pixels along the longest edge. Default is eight pages at 320 pixels, sampled evenly including first and last.
- Reports include page and file counts, results of selectable text/geometry checks, sampled page numbers and color-sensitive difference metrics, issues grouped into `error` or `warning`, and counts of suppressed issues.

## Checks

| Check | Coverage | Interpretation |
| --- | --- | --- |
| Page count mismatch | Entire document | Potential missing/extra pages (error) |
| Page dimensions/rotation changed | Every paired page | Potential layout integrity problem (error) |
| Selectable text changed/disappeared | Every paired page | Potential lost/changed text (error) |
| Scan apparently becomes blank | Bounded visual sample | High-priority warning/error; not a proof of page damage |
| Large RGB/pixel differences | Bounded visual sample | Manual visual review recommended (warning) |
| No reported issues | Structure checked + visual samples | **Not a certificate**; small visual defects may escape sampling |

### What is *not* proved

- OCR is **not** run. Text embedded only in scanned pixels cannot be compared linguistically.
- Sampled thumbnails **cannot detect all** missing details or changes on unrendered pages.
- Size, OCR confidence, font glyph rasterization and digitally signed-document verification are not automatic guarantees.
- JPEG recompression often creates acceptable visual changes. A warning is a prompt to **inspect**, not an automatic failure.
- The total CPU/RAM cost still needs profiling on the user's Windows system and representative multi-page scans.

## Command line review (with Python)

```powershell
python -m pip install -r requirements.txt
python pdf_quality.py "original.pdf" "compressed.pdf" --json "quality-report.json"
```

For faster structure/text-only checks:

```powershell
python pdf_quality.py "original.pdf" "compressed.pdf" --samples 0 --json "quality-report.json"
```

For a broader, still bounded preview check:

```powershell
python pdf_quality.py "original.pdf" "compressed.pdf" --samples 16 --max-edge 384
```

Exit code **1** means potentially serious integrity problems. A visual warning alone exits 0, but should be inspected by a human. Disabling visual checks generates an explicit `visual_check_disabled` warning. All reports use local paths and do not upload documents.

## Tests and acceptance gates

- Run all automated tests on Windows Python 3.13 and 3.14.
- Verify unchanged, multi-page, empty-text, changed-text, removed-page, page-rotation, swapped-color-image and scan-becomes-blank cases.
- Test deterministic bounded preview sampling and cancellation.
- Exercise the real Qt worker with checking on and off, and confirm output/source integrity.
- Benchmark on the user's PC and several representative scans. Check UI responsiveness, progress, false-positive warnings, batch processing and memory/CPU impact.
- **Only after acceptance** should a separate 2.8 release candidate be created; no automatic public-release workflow on this branch.

## Future work

- Local HTML and CSV reports suitable for non-technical users.
- Optional side-by-side visualization for suspicious sampled pages in the GUI.
- Tune visual thresholds against the user's test-pack PDF outputs, rather than guessing universal quality scores.
- Explicit final confirmation before stable 2.8 release.
