# PDF Compressor 2.7.1 — faster SmartFit and responsive cancellation

**Download:** [PDF_Compressor_2_7_1.exe](https://github.com/Valik2005/pdf-compressor/releases/download/v2.7.1/PDF_Compressor_2_7_1.exe)

A maintenance update for Windows 10/11 (64-bit). One standalone EXE, fully offline; no Python installation required.

## Changes since 2.7.0

- **SmartFit avoids unnecessary JPEG quality passes** when a PDF contains only images that the compressor cannot change (e.g. tiny icons or PDF images with transparency masks). This avoids repeated document scans and encoding attempts without reducing quality.
- Better explanation when the selected target is unreachable because those embedded images are ineligible for JPEG recompression. Advice is translated into both Russian and English.
- **More responsive cancellation while saving large PDF results:** final copies use bounded 1 MiB blocks and check for cancellation between them. For small documents (up to 1 MiB), the original fast system copy remains.
- Failure or cancellation during final copying cleans up partial output files. Original PDFs remain unchanged.
- Application title, version indicator, and settings identity consistently show **2.7.1**. Existing PDF compression modes and page tools remain available.

## Downloads

The release has **only three attached files** (plus the two source-code archives GitHub creates automatically):

1. **`PDF_Compressor_2_7_1.exe`** — the application; the only file regular users need.
2. **`Third_Party_Sources_and_Licenses.zip`** — six pinned Qt/PySide6/PyMuPDF/MuPDF source archives, complete notices, Windows license evidence, matching binary/source reports and Qt relinking instructions.
3. **`SHA256SUMS.txt`** — checksums for both downloads.

## Notes

A requested target file size is a goal, not a guarantee. Check small text, stamps and scanned pages after image compression. Windows SmartScreen may warn about this unsigned EXE.

The application is licensed under GNU AGPL-3.0-only. The included source and third-party license archives match the reviewed Qt 6.12.0, PySide6 6.12.0 and PyMuPDF 1.27.2.3/MuPDF 1.27.2 dependency set. The source repository provides the matching app code and onefile rebuild tooling.

---

### Русский

**PDF Compressor 2.7.1** — обновление с исправлениями и оптимизацией SmartFit.

- Не выполняются бесполезные пробы JPEG для документов, содержащих только мелкие картинки или изображения с масками прозрачности.
- Уточнены подсказки, когда сжатие таких картинок невозможно.
- Большие готовые PDF копируются частями, поэтому отмена операции обрабатывается между блоками. Для небольших PDF сохранён быстрый способ копирования.
- При отмене или ошибке неполные результаты удаляются. Исходные документы не изменяются.
- Исправлено отображение версии 2.7.1.

**Для работы достаточно скачать один `PDF_Compressor_2_7_1.exe`.** Второй файл содержит исходники и лицензии, третий — контрольные суммы.
