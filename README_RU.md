# PDF Compressor 2.6

**Бесплатная программа с открытым исходным кодом для сжатия и обработки PDF на Windows 10/11 (64 бит).**  
Работает **без интернета**, поддерживает русский и английский язык.

[English README](README.md) · [Все релизы](https://github.com/Valik2005/pdf-compressor/releases) · [Лицензия](LICENSE)

[![Скачать PDF Compressor 2.6](https://img.shields.io/badge/Скачать%20для%20Windows-PDF%20Compressor%202.6-567CF5?style=for-the-badge&logo=windows)](https://github.com/Valik2005/pdf-compressor/releases/download/v2.6.0/PDF_Compressor_2_6.exe)

**[⬇ Скачать PDF_Compressor_2_6.exe](https://github.com/Valik2005/pdf-compressor/releases/download/v2.6.0/PDF_Compressor_2_6.exe)** · [Открыть релиз](https://github.com/Valik2005/pdf-compressor/releases/tag/v2.6.0)

Готовая программа находится в разделе **Releases → Assets**, а не среди исходных файлов. Для её запуска **не нужен Python**. EXE не имеет цифровой подписи, поэтому Windows SmartScreen может показать предупреждение.

## Возможности

- Пакетное сжатие PDF с четырьмя режимами: до заданного размера, максимальное качество, сбалансированный и максимальное сжатие
- Сначала оптимизация без потерь, затем при необходимости JPEG-сжатие изображений
- Индикатор выполнения, отмена, размеры исходного и готового PDF, процент экономии
- Сравнение страниц до и после, масштабирование и навигация
- Объединение и разделение PDF, извлечение страниц, поворот
- Перетаскивание файлов, сохранение настроек, светлая и тёмная темы
- Переключение русского и английского языка
- Обработка на твоём компьютере; исходные файлы не перезаписываются

**Важно:** указанный размер (например, 1 МБ) — цель, а не гарантия. Сжатие может ухудшить изображения. Изменение подписанного PDF может нарушить электронную подпись.

## Установка

1. [Скачай готовый EXE](https://github.com/Valik2005/pdf-compressor/releases/download/v2.6.0/PDF_Compressor_2_6.exe).
2. Запусти `PDF_Compressor_2_6.exe` на Windows 10/11 x64.
3. Выбери язык и добавь PDF.

Дополнительно устанавливать Python или библиотеки не нужно.

## Исходный код

| Файл | Назначение |
| --- | --- |
| `app.pyw` | Интерфейс программы и переводы |
| `pdf_engine.py` | Алгоритмы обработки PDF |
| `requirements.txt` | Зависимости Python |
| `app_icon.ico` | Иконка |
| `tests/` | Тесты |
| [`BUILDING.md`](BUILDING.md) | Инструкция по сборке |

Для запуска из исходного кода (Python 3.11+):

```powershell
python -m pip install -r requirements.txt
python app.pyw
```

Тестирование:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

## Open Source и лицензии

Исходный код PDF Compressor распространяется по [**AGPL-3.0-only**](LICENSE). Его можно изучать, изменять и распространять в рамках условий этой лицензии.

Программа использует **PyMuPDF** (AGPLv3 или коммерческая лицензия), **PySide6 / Qt** (LGPL/GPL или коммерческая лицензия) и Pillow. При распространении EXE нужно также соблюдать лицензии включённых библиотек; одного наличия исходников может быть недостаточно. Подробнее — в [DEPENDENCIES_AND_LICENSING.md](DEPENDENCIES_AND_LICENSING.md).

Программа не связана с разработчиками Artifex, PyMuPDF и Qt. EXE не подписан цифровым сертификатом; его контрольная сумма SHA-256 указана в [примечаниях к релизу](RELEASE_NOTES.md).
