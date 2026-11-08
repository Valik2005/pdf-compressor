## PDF Compressor 2.7.0 — Windows

Free and open-source **offline PDF compressor and document tools** for Windows 10/11 (64-bit). Download `PDF_Compressor_2_7.exe` in **Assets** and run it directly. **No Python installation is required.** The EXE is unsigned; Windows SmartScreen may warn on first launch.

### What's new in 2.7
- **SmartFit:** analyzes the document structure and tries conservative combinations to approach a selected target size.
- Optional image downscaling (under your control); better handling of images shared by different pages and sizes.
- Faster candidate-quality searches that avoid redundant passes.
- Better maximized-window file-list layout and clearer messages when a target cannot be achieved.
- Batch compression, cancellation, side-by-side comparison and PDF merge/extract/rotate retained.
- Russian and English user interface, light and dark themes, fully offline processing.

### Limits
A target file size is not guaranteed: compression must not silently sacrifice all visual quality to meet it. No OCR, PDF text editing or password creation. Always visually inspect scanned, small-print or official documents when quality is important.

### Source code, licenses and modified Qt libraries
This release is published under **GNU AGPL-3.0-only**. The repository's source archive at this tag contains the application code, tests and build scripts. This release also includes the **six version-pinned upstream source archives** used for review (PyMuPDF 1.27.2.3, MuPDF 1.27.2, Qt 6.12.0 QtBase/QtSvg/QtImageFormats and PySide6/Shiboken 6.12.0), plus full applicable license documents, third-party attributions and correspondence audit reports.

To rebuild a single EXE using your own compatible modified Qt libraries, see `LGPL_RELINKING_2_7.md` among the release assets. GitHub Actions validates that a resource-modified Qt6Widgets DLL can be placed into a fresh single EXE and launched on Windows.

Third-party notices and source archives are supplied separately rather than embedded in the EXE. Check `THIRD_PARTY_NOTICES_2_7.zip`, `license-evidence.zip`, and the source archives in Assets. Applicable Windows runtime redistribution conditions and other third-party licenses still apply. Source-correspondence reports are technical verification evidence, not legal advice.

### Checksums
Verify downloads against `SHA256SUMS.txt`. The accompanying `build-manifest.json` identifies the exact Windows build commit and dependency versions, while `bundle-audit.json` and `native-source-mapping.json` record the embedded libraries.

### Русский
PDF Compressor 2.7 — офлайн-программа для Windows с новым режимом **SmartFit**. Сжимает PDF с подбором качества под заданный размер, поддерживает пакетную обработку, отмену заданий, объединение, извлечение и поворот страниц. Исходники, лицензии и контрольные суммы включены в материалы этого выпуска. Просто скачай `PDF_Compressor_2_7.exe`, установка Python не требуется.
