<div align="center">

# 📄 PDF Compressor 2.8

**Удобное сжатие PDF и работа со страницами — прямо на вашем компьютере.**

Русский и английский интерфейс · Windows 10/11 · Бесплатно и с открытым кодом

<p>
  <img alt="Release 2.8" src="https://img.shields.io/badge/Release-2.8-2563eb?style=flat-square" />
  <img alt="Windows 10/11" src="https://img.shields.io/badge/Windows-10%20%7C%2011-0078d4?style=flat-square&amp;logo=windows11&amp;logoColor=white" />
  <img alt="Offline" src="https://img.shields.io/badge/Processing-Offline-238636?style=flat-square" />
  <img alt="AGPL-3.0" src="https://img.shields.io/badge/License-AGPL--3.0-8250df?style=flat-square" />
</p>

<a href="https://github.com/Valik2005/pdf-compressor/releases/download/v2.8/PDF_Compressor_2_8.exe">
  <img alt="⬇ Скачать PDF Compressor 2.8 EXE" src="https://img.shields.io/static/v1?label=%E2%AC%87%20%D0%A1%D0%9A%D0%90%D0%A7%D0%90%D0%A2%D0%AC&amp;message=PDF%20Compressor%202.8%20EXE&amp;color=238636&amp;style=for-the-badge&amp;logo=windows11&amp;logoColor=white" />
</a>

**Один EXE · Без установки Python · ≈70 МБ**

[Прямая ссылка на EXE](https://github.com/Valik2005/pdf-compressor/releases/download/v2.8/PDF_Compressor_2_8.exe) · [Страница релиза](https://github.com/Valik2005/pdf-compressor/releases/tag/v2.8) · [SHA-256](https://github.com/Valik2005/pdf-compressor/releases/download/v2.8/SHA256SUMS.txt)

[English README](README.md)

</div>

---

> 🔒 **Конфиденциальность:** все PDF обрабатываются локально. Документы никуда не загружаются.

**Code signing policy / Политика цифровой подписи:** [правила подписи SignPath Foundation](docs/CODE_SIGNING_POLICY.md). **PDF Compressor 2.8 официально подписан SignPath Foundation:** проверяй цифровую подпись Windows и SHA-256 из релиза. Подпись не гарантирует отсутствие предупреждений SmartScreen.

## ✨ Возможности

- Сжатие одного или нескольких PDF за раз.
- Четыре режима: до заданного размера (**SmartFit**), максимальное качество, сбалансированный и максимальное сжатие.
- **Новое в 2.7 — SmartFit:** анализ текстовых, сканированных и смешанных PDF с осторожным подбором параметров сжатия.
- **Новое в 2.8:** проверка качества после сжатия по желанию, предупреждения о сильной потере деталей JPEG, экспорт HTML/JSON без полных путей и улучшенная индикация целевого размера.
- **Новое в 2.7.1:** пропуск бесполезных попыток JPEG-сжатия мелких изображений и возможность отменить копирование больших PDF с удалением неполного результата.
- Сначала оптимизация без потерь, затем при необходимости JPEG-сжатие; уменьшение разрешения изображений — только с разрешения пользователя.
- По возможности сохраняется выделяемый текст; улучшена обработка изображений, используемых на нескольких страницах.
- Прогресс обработки, отмена операций, статистика размера.
- Сравнение страниц до/после с масштабированием, переключением страниц и поворотом предпросмотра.
- Объединение PDF, разделение/извлечение страниц, поворот документа.
- Выбор папки и шаблона имени, сохранение настроек и смена языка без перезапуска.
- Исходные PDF не перезаписываются: результат сохраняется отдельно.

**Важно:** указанный размер (например, 1 МБ) — **цель, а не гарантия**. Не каждый PDF можно уменьшить до такого размера без потери качества. Изменение PDF может нарушать цифровые подписи, поэтому предусмотрены ограничения для подписанных документов.

## ⬇️ Скачать EXE без Python

Нажми зелёную кнопку **«СКАЧАТЬ»** в начале страницы — она ведёт **сразу на файл** `PDF_Compressor_2_8.exe` из официального GitHub Release.

| Параметр | Значение |
| :-- | :-- |
| **Версия** | 2.8 (стабильная, цифровая подпись) |
| **ОС** | Windows 10/11, 64-бит |
| **Формат** | Один EXE, без установщика и Python |
| **Размер** | ≈70 МБ |

[**Скачать EXE напрямую**](https://github.com/Valik2005/pdf-compressor/releases/download/v2.8/PDF_Compressor_2_8.exe) · [Все файлы релиза и лицензии](https://github.com/Valik2005/pdf-compressor/releases/tag/v2.8) · [Проверить SHA-256](https://github.com/Valik2005/pdf-compressor/releases/download/v2.8/SHA256SUMS.txt)

> Официальный EXE 2.8 имеет проверенную подпись SignPath Foundation. Сверь её в свойствах Windows и SHA-256 из `SHA256SUMS.txt`. SmartScreen всё равно может показывать предупреждение о репутации.

## 🖥️ Установка на Windows из исходников

Нужен Python **3.11 или новее**. Официальный релизный EXE собирается на Python 3.14 с закреплёнными версиями зависимостей.

1. Нажми **Code → Download ZIP** на GitHub и распакуй исходники или клонируй репозиторий.
2. Открой CMD или PowerShell в папке проекта и выполни:

   ```bat
   python -m pip install -r requirements.txt
   python app.pyw
   ```

3. Выбери **Русский / English** в верхней части программы. Настройка сохраняется.

Для дальнейшего запуска без консоли можно открывать `app.pyw` через установленный Python.

## 🛠️ Сборка EXE

Официальная версия 2.8 собирается и подписывается в [ручном workflow SignPath](.github/workflows/sign-v2_8.yml), затем публикуется через [отдельный workflow выпуска](.github/workflows/publish-v2_8-signed.yml). Для локальной сборки Windows:

```bat
python -m pip install "PyMuPDF==1.27.2.3" "PySide6==6.12.0" "Pillow==12.3.0" "pyinstaller==6.22.3"
python -m PyInstaller --noconfirm --clean release_windows_2_8.spec
```

Результат: `dist\PDF_Compressor_2_8.exe` (без подписи). Официальный EXE публикуется только после SignPath, с лицензиями и SHA-256. Подробнее: [BUILDING.md](BUILDING.md), [пересборка Qt](docs/LGPL_RELINKING_2_8.md).

## ✅ Тесты

```bat
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Тесты проверяют PDF-движок, сценарии SmartFit, сборочные инструменты и переводы. Реальное отображение интерфейса и масштабирование Windows зависят от системы; в релизном workflow дополнительно проверяется запуск EXE.

## 📂 Структура репозитория

```text
app.pyw                       Приложение с интерфейсом RU/EN
pdf_engine.py                 Сжатие PDF и работа со страницами
app_icon.ico                  Значок приложения
requirements.txt              Зависимости для запуска
tests/                        Тесты PDF, SmartFit и перевода
tools/                        Проверки релиза, манифесты и пересборка Qt
release_windows_2_8.spec    Настройки PyInstaller для одного EXE
BUILDING.md                   Инструкция по сборке
README.md                     English README
.github/workflows/sign-v2_8.yml   Подпись 2.8
.github/workflows/publish-v2_8-signed.yml   Проверка и публикация 2.8
```

## 📜 Лицензии зависимостей

Исходный код приложения распространяется по **GNU AGPL-3.0-only**. PyMuPDF/MuPDF используют AGPL или коммерческое лицензирование, Qt/PySide6 — LGPL/GPL или коммерческие варианты. В [релизе 2.8](https://github.com/Valik2005/pdf-compressor/releases/tag/v2.8) исходники сторонних библиотек, лицензии, отчёты и инструкция по пересборке одного EXE с совместимыми изменёнными Qt-библиотеками находятся внутри **`Third_Party_Sources_and_Licenses.zip`**. Подробнее: [DEPENDENCIES_AND_LICENSING.md](DEPENDENCIES_AND_LICENSING.md) и [уведомления](docs/THIRD_PARTY_NOTICES_RELEASE_2_8.md).

## ℹ️ Примечание

JPEG-сжатие изображений не полностью без потерь. Проверяй качество итоговых PDF и сохраняй резервные копии важных документов. Программа не связана с разработчиками PyMuPDF, Artifex и Qt.
