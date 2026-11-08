# Third-party licenses / Лицензии сторонних библиотек

PDF Compressor application sources are provided under the [GNU AGPL v3](LICENSE), SPDX identifier **AGPL-3.0-only**.

The application depends on the following separate projects:

| Dependency | Role | Upstream license and source |
| --- | --- | --- |
| [PyMuPDF](https://pymupdf.io/licensing) | PDF parsing, optimization and editing | AGPLv3 **or** Artifex commercial licensing |
| [PySide6 / Qt](https://pypi.org/project/PySide6/) | Desktop GUI | LGPLv3, GPLv2/GPLv3, or commercial; individual Qt modules may differ |
| [Pillow](https://github.com/python-pillow/Pillow/blob/main/LICENSE) | Image processing | HPND-like historical permission license |
| Python runtime / packages bundled by PyInstaller | Execution of Windows EXE | Their respective upstream notices and licensing terms |

## Redistributing the Windows EXE

- The project is open source under AGPL-3.0-only, but **third-party libraries retain their own licenses**.
- If you distribute a bundled EXE, comply with PyMuPDF's AGPL obligations, including applicable source-code and copyright/producer-notice requirements. A commercial license is an alternative.
- For LGPL-licensed Qt components, review notices, license texts, user rights to replace or modify the LGPL components, and any corresponding relinking/reverse-engineering requirements relevant to your packaging method. A PyInstaller **one-file** bundle may need additional compliance work.
- Check the exact versions and licenses of dependencies **actually packaged** in each EXE, preserve attribution and distribute any required license texts and source/offer information.
- The currently published v2.6.0 EXE was produced locally before this license documentation update. Its binary content is **unchanged** by this repository cleanup. This update alone does **not** certify its binary redistribution compliance.

Official references: [AGPL-3.0](https://www.gnu.org/licenses/agpl-3.0.html), [PyMuPDF licensing](https://pymupdf.io/licensing), [Qt licensing](https://doc.qt.io/qt-6/licensing.html).

## По-русски

Исходный код приложения распространяется по **AGPL-3.0-only**. Сторонние библиотеки сохраняют собственные лицензии.

При публичном распространении готового EXE необходимо проверить соответствие условиям AGPL для PyMuPDF, условиям LGPL/GPL для PySide6/Qt и включить обязательные уведомления. Особенно важно проверить особенности упаковки Qt-библиотек в **один EXE** через PyInstaller. Публикация исходников сама по себе не гарантирует выполнения всех условий.

Для юридически значимого распространения рекомендуется отдельная проверка лицензий и состава собранного бинарника.

## Version 2.7 release preparation

- Draft third-party notices: [docs/THIRD_PARTY_NOTICES_2_7.md](docs/THIRD_PARTY_NOTICES_2_7.md).
- Release gate checklist: [docs/RELEASE_CHECKLIST_2_7.md](docs/RELEASE_CHECKLIST_2_7.md).
- Use `tools/release_manifest.py` to record exact builder versions and final EXE hash. This is **not** proof of complete binary licensing compliance.
- Source availability, LGPL Qt replacement/relinking rights and full component license texts still require review before public v2.7 distribution.
