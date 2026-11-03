# PDF Compressor 2.7 SmartFit — development preview

**Status:** source-only preview. Windows GUI / PyInstaller EXE not yet verified; **v2.6.0** remains the published stable release. Do not redistribute this preview as a finished v2.7.0 release.

## Added in 2.7

- **SmartFit mode**: enter a target size in MB, then select **Prepare PDF for sending**.
- **Document triage** without page rasterization: text-based, scanned, mixed, or other; detected using extractable text and visible image placement. This is a **heuristic**, not optical text recognition or a quality certificate.
- **Conservative quality search**: scanned and mixed documents have a higher minimum JPEG quality than the original aggressive target-size mode. When a PDF cannot reasonably reach the requested size, the program reports the missed target rather than forcing unlimited loss of quality.
- **Optional downscaling** remains an explicit checkbox, not a hidden action.
- **Shared-image protection**: when an image object is reused in several pages, downscaling uses its **largest placement across the entire document**, not just the first page.
- **Output advice**: hints about scans, images, missed targets and visual inspection.
- **Bounded preview rendering** to limit RAM/CPU usage for huge pages.
- Original modes and PDF tools remain available.

## Boundaries of this release

- SmartFit **does not yet automatically verify visual readability or text preservation**. That is planned for 2.8.
- No OCR, AI chatbot, PDF text editor or password-creation features.
- A requested file size is **a target, not a guarantee**.
- Source PDFs are not overwritten. The result is saved with a non-conflicting name.
- The already-published 2.6 Windows EXE has **not changed**.

## Run from source

Requires Python 3.11+ and dependencies from `requirements.txt`.

```powershell
python -m pip install -r requirements.txt
python app.pyw
```

Run automated checks:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Build on Windows (Python + PyInstaller): see [BUILDING.md](../BUILDING.md) in the repository main branch. The new v2.7 executable has **not been compiled or tested on Windows**.

## Test coverage (source preview)

The automated test suite covers document classification, target-size reporting, scan output, cancellation, page-preserving operations, text preservation in existing modes and reused image objects across multiple pages.

## Roadmap

- **2.8**: compare text and document integrity, visual-change detection and quality reporting.
- **2.9**: PDF space-use diagnosis and actionable recommendations.
- **3.0**: protecting selected pages and highlighting likely quality regressions.

This work uses the existing AGPLv3-licensed application source. Third-party package licenses remain separate; binary distribution requires another compliance review.
