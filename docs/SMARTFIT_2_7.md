# PDF Compressor 2.7 SmartFit — released engine, 2.7.1 maintenance

**Status:** PDF Compressor 2.7.0 was released on 2026-11-08. The 2.7.1 maintenance update improves cancellation while copying large PDF outputs and avoids ineffective JPEG quality trials for documents containing only tiny/masked images.

## Added in 2.7

- **SmartFit mode**: enter a target size in MB, then select **Prepare PDF for sending**.
- **Document triage** without page rasterization: text-based, scanned, mixed, or other; detected using extractable text and visible image placement. This is a **heuristic**, not optical text recognition or a quality certificate.
- **Conservative quality search**: scanned and mixed documents have a higher minimum JPEG quality than the original aggressive target-size mode. When a PDF cannot reasonably reach the requested size, the program reports the missed target rather than forcing unlimited loss of quality.
- **Optional downscaling** remains an explicit checkbox, not a hidden action. DPI stages that cannot reduce the dimensions of any eligible image are skipped to avoid redundant compression passes.
- **Shared-image protection**: when an image object is reused in several pages, downscaling uses its **largest placement across the entire document**, not just the first page.
- **Output advice**: hints about scans, images, missed targets and visual inspection.
- **Bounded preview rendering** to limit RAM/CPU usage for huge pages.
- Original modes and PDF tools remain available.

## Boundaries of this release

- SmartFit checks that extractable text is unchanged page by page after compression, but **does not automatically verify visual readability** (especially scanned text, seals, and fine details). Deeper integrity and visual checks remain planned for 2.8.
- No OCR, AI chatbot, PDF text editor or password-creation features.
- A requested file size is **a target, not a guarantee**.
- Source PDFs are not overwritten. The result is saved with a non-conflicting name.
- The source PDF is never overwritten. Previous release assets remain unchanged.

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

Build the official Windows onefile from the verified release workflow; see [BUILDING.md](../BUILDING.md). Local builds are separate preview artifacts and must not be misrepresented as official release downloads.

## Test coverage

The automated test suite covers document classification, target-size reporting, scan output, cancellation, page-preserving operations, text preservation in existing modes and reused image objects across multiple pages.

## Roadmap

- **2.8**: compare text and document integrity, visual-change detection and quality reporting.
- **2.9**: PDF space-use diagnosis and actionable recommendations.
- **3.0**: protecting selected pages and highlighting likely quality regressions.

This work uses the AGPLv3-licensed application source. The official release includes a separate source/license archive and Qt onefile relinking instructions.
