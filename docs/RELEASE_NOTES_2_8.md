# PDF Compressor 2.8 — draft release notes (not released)

**Status:** draft notes for maintainer review; do not publish yet. Public stable remains [v2.7.1](https://github.com/Valik2005/pdf-compressor/releases/tag/v2.7.1).

## What's new in 2.8

- **Optional post-compression quality review** in the PDF Compressor interface. The user explicitly enables it; it is off by default because it adds processing time.
- Checks all corresponding pages for changes in page count, page size/rotation and selectable text; samples a bounded set of small page previews for major visual changes, possible blank scans and risky raster-only documents.
- Reports whether a result needs manual inspection without confusing warnings with structural corruption. A completed PDF remains available even when a quality warning is raised.
- **Save quality report** on demand as an offline HTML or JSON file; default exported reports show only PDF basenames, not local directory paths (subject to final release merge/verification).
- More accurate target-size reporting: an unattainable limit is shown clearly as **«Выше лимита» / “Over target”**, with details available without hiding simultaneous quality warnings.
- Limited extra JPEG quality probes for a narrow near-target case; keeps image dimensions unless the user explicitly enables downscaling. Compression engine remains optimized for local, responsive operation.

## Existing features retained

One Windows x64 EXE, Russian/English interface, light/dark themes, batch compression, SmartFit and target file size, before/after page preview, cancellation, merge, split/extract and rotate PDF pages, selectable output folder. All document processing takes place on the computer.

## What a warning means

Automated analysis is a **diagnostic, not a visual-quality certificate**. It does not run OCR; it cannot guarantee intact scanned text, colored stamps, thin lines, photographic textures, image details or unrendered pages. For aggressive JPEG values, compare the original and compressed document at **200% zoom**, especially small raster text and signatures. Reaching a target size does not imply visually lossless compression.

## Internal testing and digital signatures

The internal `2.8.1 Testing` branch contains a local automatic test-run exporter and is **not part of the public 2.8 release**.

The maintainer has applied for **free SignPath Foundation code signing**. Application submission does not mean acceptance or an issued certificate. This release will be called **digitally signed only when** a real signed Windows EXE is independently verified; otherwise documentation must explicitly state that it is unsigned. See [Code signing policy](https://github.com/Valik2005/pdf-compressor/blob/main/docs/CODE_SIGNING_POLICY.md).

## Release packaging (pending)

Final assets, after independent testing and maintainer approval:
- `PDF_Compressor_2_8.exe`
- `Third_Party_Sources_and_Licenses.zip`
- `SHA256SUMS.txt`

No tag, download badge change or public v2.8 GitHub Release is authorized by this draft. See [RELEASE_CHECKLIST_2_8.md](RELEASE_CHECKLIST_2_8.md).
