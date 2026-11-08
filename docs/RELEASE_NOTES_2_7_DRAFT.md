# PDF Compressor 2.7.0 — DRAFT release notes (not published)

**Status: pre-release candidate work in `develop/2.7-smartfit`. The stable public release is still 2.6.0.**

## New features and improvements
- SmartFit mode analyzes text/scans/mixed document structure and searches for a conservative output size.
- Optional image downscaling; user chooses whether to allow it.
- Preserves higher image resolution for an image object reused at different sizes across pages.
- Faster candidate-quality search and avoidance of redundant DPI passes in relevant scenarios.
- More adaptive file-list height when the application window is maximized.
- PDF operations: merge, extract pages and rotate; cleaner error/cancellation handling under review.

## Constraints
- Target file size is not guaranteed; when impossible at allowed quality, the interface reports that the target was not reached.
- SmartFit compares extractable text page by page, but does not automatically certify scanned text, stamps or image readability.
- Original PDFs are kept unchanged; outputs use collision-safe names.
- No OCR, password creation or general-purpose PDF text editing.

## Validation so far
- Windows 11 local preview EXE built and launched; preview SHA-256: `D9495B8D6C6D4EDD1C5EC952DD0E65D59EED78A785C1635621B13CCB3483D985`.
- GitHub Actions on commit `4424feef`: 40 tests passed under each of Python 3.13 and 3.14.
- Manual sample tests include multiple SmartFit targets, batch processing, tool operations and cancellation.
- Any change to code, build dependencies or packaging requires a **new** validated EXE and checksum.

## Release blockers
- Complete third-party license/source/relinking verification for the actual distributable EXE, especially Qt one-file packaging.
- Final integration CI, final-binary smoke test, release checklist and maintainer approval.

Do not copy this draft into a published GitHub Release until it is updated for the final commit and package.
