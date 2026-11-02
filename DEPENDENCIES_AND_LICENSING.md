# Third-party licenses / Лицензии зависимостей

The source files in this repository use these runtime dependencies:

| Package | Purpose | License (upstream) |
| --- | --- | --- |
| [PyMuPDF](https://pymupdf.io/licensing) | PDF parsing, optimization, and manipulation | GNU AGPL v3 or Artifex commercial license |
| [PySide6](https://doc.qt.io/qtforpython-6/) | Qt user interface | LGPL/GPL or commercial license |
| [Pillow](https://python-pillow.github.io/) | Image processing | HPND license |

**Before making this repository public or distributing a bundled executable, decide the project license and check compatibility with PyMuPDF's AGPL obligations.** The AGPL option generally expects sharing the corresponding application source when distributing an application built using it. A proprietary distribution generally requires a commercial PyMuPDF license. Check the official license texts and seek legal advice if needed.

**Перед публикацией или распространением EXE выберите лицензию самого проекта и учитывайте AGPL-обязательства PyMuPDF.** При распространении в рамках открытой AGPL-модели необходимо соблюдать требования к доступности соответствующего исходного кода; для закрытого продукта может потребоваться коммерческая лицензия PyMuPDF.

This repository does not redistribute the external Python packages; they are installed separately by pip. When packaging with PyInstaller, include applicable third-party notices and license files in distributions where required.
