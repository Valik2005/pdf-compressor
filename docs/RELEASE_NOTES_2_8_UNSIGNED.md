# PDF Compressor 2.8 — Windows x64 (unsigned release)

**Free and open source · Offline PDF processing · No digital signature**

## Download and verification

The official release contains exactly three assets:

- **PDF_Compressor_2_8.exe** — standalone Windows application.
- **Third_Party_Sources_and_Licenses.zip** — six matching upstream source archives, applicable license notices, Qt LGPL relinking instructions and build-integrity reports.
- **SHA256SUMS.txt** — independent SHA-256 hashes for the *final unsigned EXE* and the source/license ZIP.

**IMPORTANT:** The EXE **is not digitally signed**. SignPath Foundation did not approve the free certificate application because the project does not yet have enough independent public recognition; this was **not a security or code-quality assessment**. Windows SmartScreen or antivirus may warn about an unrecognized executable. Download only from the official project release, check its SHA-256 hash against the release's published checksum, and make your own decision about whether to run it. **SHA-256 does not prove publisher identity or guarantee that an application is safe.** Do not treat this as a SignPath-certified build.

Project source and provenance: https://github.com/Valik2005/pdf-compressor

## New in 2.8

- Optional post-compression PDF quality review with page counts, page geometry and selectable-text comparison.
- Sampled visual checks and warnings about important raster differences; strong JPEG compression can noticeably affect quality even if page geometry and selectable text remain intact.
- Export offline quality reports as HTML or JSON, showing only file basenames by default, not absolute directory paths.
- Clearer over-target messages when the maximum file size cannot be reached.
- Bilingual **Licenses / Лицензии** panel identifying the AGPL and upstream Qt/MuPDF licenses, warranty disclaimer and users' rights to rebuild with compatible modified Qt libraries.
- Existing batch compression, SmartFit, preview, cancellation, PDF merge, extraction and rotation, and Russian/English and dark/light modes remain.

## Limitations and privacy

The quality check **does not run OCR** and does not guarantee visual fidelity of scanned fine text, stamps, signatures or tiny lines. For aggressive JPEG settings compare original and processed PDFs at **200% zoom**. User PDFs are processed locally, not sent to signing services or servers. Extra quality checks use CPU and memory when enabled.

---

# PDF Compressor 2.8 — Windows (64 бита), без цифровой подписи

**Бесплатная программа с открытым исходным кодом. PDF обрабатываются локально.**

## Файлы выпуска

Официальный выпуск состоит ровно из трёх файлов:

- **PDF_Compressor_2_8.exe** — готовая программа Windows.
- **Third_Party_Sources_and_Licenses.zip** — исходники и лицензии сторонних библиотек, инструкция по замене Qt и отчёты проверок.
- **SHA256SUMS.txt** — контрольные суммы SHA-256 для **неподписанного EXE** и ZIP.

**Важно: EXE не имеет цифровой подписи.** Фонд SignPath отклонил заявку на бесплатный сертификат из-за недостаточной публичной известности проекта; это не было оценкой качества или безопасности его кода. Windows SmartScreen может показать предупреждение. Скачивай программу только с официального GitHub-релиза и сверяй SHA-256 с опубликованной контрольной суммой. **Хеш подтверждает совпадение файлов, но не личность издателя и не отсутствие вредоносного кода.**

Исходный код: https://github.com/Valik2005/pdf-compressor

## Что нового

- Необязательная проверка качества после сжатия: количество и геометрия страниц, выделяемый текст и выборочное сравнение.
- Предупреждения об изменениях изображений, особенно при сильном JPEG-сжатии.
- Экспорт отчётов в локальные HTML/JSON без раскрытия полных путей к файлам.
- Понятное уведомление, когда установленный лимит размера недостижим.
- Раздел **«Лицензии»** с информацией об AGPL, LGPL, MuPDF, отсутствии гарантий и возможности пересборки с изменёнными библиотеками Qt.
- Сохранены пакетная обработка, SmartFit, предпросмотр, отмена, объединение, извлечение и поворот страниц, русский и английский языки, светлая и тёмная темы.

**Ограничения:** автоматическая проверка не использует OCR и не гарантирует полной сохранности текстуры изображений, мелкого текста внутри сканов, печатей и подписей. При сильном сжатии сравни оригинал и результат при **200% масштабе**.
