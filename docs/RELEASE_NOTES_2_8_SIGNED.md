# PDF Compressor 2.8 — Windows (x64)

**Stable release · Free and open source · Offline PDF processing**

## Download

- **`PDF_Compressor_2_8.exe`** — the Windows application. No Python installation needed.
- **`Third_Party_Sources_and_Licenses.zip`** — third-party source archives, license notices, Qt LGPL relinking instructions and audit evidence.
- **`SHA256SUMS.txt`** — SHA-256 for the **final signed EXE** and the matching archive.

Only these three files are official release assets.

## New in 2.8

- **Optional quality review after compression.** Check whether PDF page counts, page geometry and selectable text remained intact. Examine a bounded sample of small page previews for major visual changes, possible blank scans and changed raster content.
- **Honest quality warnings.** Strong JPEG reduction, downscaled images and scanned pages needing zoomed inspection are reported as *manual review* rather than incorrectly described as error-free.
- **HTML/JSON quality reports** saved only when requested by the user. Exports show file names rather than absolute directory paths; they do not send documents to servers.
- **Clearer target-size outcome:** reports when the desired size could not be reached, even if the PDF itself was saved correctly.
- All previous functionality retained: SmartFit, four compression modes, batch processing, before/after preview, stop/cancel, merge, split/extract, rotate, RU/EN and light/dark themes.

## Digital signing and safety

This release is published only through a **manually approved SignPath Foundation signing request** followed by independent Windows Authenticode and SHA-256 verification. The certificate publisher is **SignPath Foundation** and does not claim a personal certificate for the maintainer. Verify the EXE's **Properties → Digital Signatures** and compare its checksum against `SHA256SUMS.txt` from this release.

**Code signing policy:** https://github.com/Valik2005/pdf-compressor/blob/main/docs/CODE_SIGNING_POLICY.md

A valid publisher signature verifies origin and integrity; it does not guarantee Microsoft SmartScreen will never display a warning. Unsigned testing and preview builds, including **2.8.1 Testing**, are never official public release files.

## Quality limits

Quality review is **not OCR and not a visual-equivalence certificate**. It checks text and page geometry across corresponding pages, and samples some pages at limited rendering resolution. Especially with JPEG compression of 27–48%, tiny raster text, thin lines, stamps, signatures and photographic texture can change significantly. Inspect the result at **200% zoom** when detail matters. Achieving a requested size does not mean lossless compression.

Documents stay on your computer; PDF content is never uploaded for processing. The optional review adds CPU/RAM work and is not enabled by default.

---

# PDF Compressor 2.8 — Windows (64 бита)

Бесплатная программа с открытым исходным кодом, обрабатывающая PDF **на компьютере пользователя, без загрузки документов в облако**.

**Файлы релиза:** `PDF_Compressor_2_8.exe` — программа; `Third_Party_Sources_and_Licenses.zip` — исходники и лицензии сторонних компонентов; `SHA256SUMS.txt` — контрольные суммы **подписанного** EXE и ZIP.

**Новое:** необязательная проверка качества после сжатия, контроль страниц и выделяемого текста, предупреждения о сильных изменениях JPEG, экспорт отчётов в HTML/JSON без полных локальных путей, более понятное сообщение о недостижимом целевом размере. Все прежние инструменты и режимы сохранены.

**Подпись:** опубликованный EXE проходит проверку Authenticode и подписи SignPath Foundation до публикации. Подлинность файла можно проверить в свойствах Windows, а его целостность — по `SHA256SUMS.txt`. Встроенный отчётчик из **2.8.1 Testing** в публичный релиз не включён.

**Ограничение:** автоматическая проверка качества не использует OCR и не гарантирует неизменность каждого изображения. При сильном JPEG-сжатии сравните текст на картинках, тонкие линии, цвета и печати с оригиналом при масштабе **200%**.
