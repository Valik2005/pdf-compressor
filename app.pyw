# -*- coding: utf-8 -*-
"""PDF Compressor 2.7 SmartFit - offline desktop GUI (Qt6)."""
from __future__ import annotations

import os
import sys
import threading
from time import perf_counter
from pathlib import Path

from PySide6.QtCore import Qt, QSettings, QThread, QObject, Signal, QUrl, QTimer, QRegularExpression, QRectF
from PySide6.QtGui import QDesktopServices, QPixmap, QFont, QIcon, QIntValidator, QRegularExpressionValidator, QTransform, QPainter, QColor, QPen, QBrush
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QComboBox, QDoubleSpinBox, QCheckBox, QFileDialog,
    QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget,
    QProgressBar, QSplitter, QScrollArea, QSpinBox, QGroupBox, QFrame,
    QAbstractItemView, QSizePolicy, QAbstractSpinBox, QStackedWidget, QLayout
)

import pymupdf
from pdf_engine import (
    Cancelled, compress_pdf, file_info, human_size, merge_pdfs,
    rotate_pdf, split_pdf
)

APP_VERSION = "2.7"


# Text is keyed by the original Russian UI copy. No external translation file is
# required, so updating the installed app still only needs app.pyw.
I18N_EN = {
    "⇩  Перетащите сюда PDF-файлы": "⇩  Drop PDF files here",
    "Или нажмите «Добавить файлы» · несколько документов сразу": "Or select Add files · multiple PDFs at once",
    "●  Документы остаются на компьютере": "●  Your documents stay on this computer",
    "Светлая тема": "Light theme",
    "Тёмная тема": "Dark theme",
    "☀  Светлая тема": "☀  Light theme",
    "☾  Тёмная тема": "☾  Dark theme",
    "Сжатие и просмотр": "Compress & preview",
    "Документы": "Documents",
    "+ Добавить файлы": "+ Add files",
    "Удалить": "Remove",
    "Очистить": "Clear",
    "PDF-файл": "PDF file",
    "Размер": "Size",
    "Статус": "Status",
    "Параметры сжатия": "Compression settings",
    "Режим": "Mode",
    "До заданного размера": "Target file size",
    "SmartFit · автоматически": "SmartFit · automatic",
    "▶  Подготовить PDF к отправке": "▶  Prepare PDF for sending",
    "SmartFit анализирует тип PDF и подбирает сжатие. После обработки проверьте документ в предпросмотре.": "SmartFit analyzes PDF content and selects compression settings. Check the preview before sending.",
    "Тип документа:": "Document type:",
    "Текстовый PDF": "Text-based PDF",
    "Скан": "Scanned PDF",
    "Смешанный PDF": "Mixed PDF",
    "Другой PDF": "Other PDF",
    "страниц": "pages",
    "SmartFit": "SmartFit",
    "Рекомендации:": "Suggestions:",
    "Размер достигнут. Просмотрите страницы перед отправкой.": "Target met. Check the pages before sending.",
    "В PDF почти нет встроенных изображений: сжатие может не помочь.": "There are few embedded images; compression may not help.",
    "Размер не достигнут. Можно разрешить уменьшение разрешения изображений.": "Target not met. You can allow image downscaling.",
    "Размер не достигнут без более сильной потери качества. Увеличьте лимит.": "Target not met without greater quality loss. Increase the limit.",
    "Документ похож на скан: проверьте мелкий текст и печати.": "This looks like a scan: check small text and stamps.",
    "Смешанный PDF: проверьте изображения и мелкие детали.": "Mixed PDF: check images and fine details.",
    "Анализ документа": "Analyzing document",
    "Максимальное качество": "Highest quality",
    "Сбалансированный": "Balanced",
    "Максимальное сжатие": "Maximum compression",
    "МБ": "MB",
    "Целевой размер в мегабайтах, например 1 или 0,5": "Target size in megabytes, for example 1 or 0.5",
    "Разрешить уменьшение разрешения при необходимости": "Allow image downscaling if necessary",
    "Если размер недостижим без изменения числа пикселей, можно уменьшить разрешение изображений.": "Allow lower image resolution when the target cannot otherwise be reached.",
    "Сохранение результата": "Save results",
    "Папка для результатов": "Output folder",
    "Новые PDF сохраняются сюда, оригиналы не изменяются": "Save new PDFs here, without changing the originals",
    "Обзор…": "Browse…",
    "Имя": "Name",
    "{name} заменяется именем исходного файла; совпадения получают суффикс _2, _3…": "{name} becomes the original filename; duplicate names get _2, _3, etc.",
    "▶  Сжать все PDF": "▶  Compress all PDFs",
    "■ Отменить": "■ Cancel",
    "Открыть готовый PDF": "Open output PDF",
    "Готов к работе · исходные файлы не изменяются": "Ready · original files will not be changed",
    "Просмотр PDF": "PDF preview",
    "Автоматически": "Automatic",
    "До и после": "Before & after",
    "Только оригинал": "Original only",
    "Только результат": "Output only",
    "Авто: большой оригинал до сжатия, два документа после": "Auto: show original before compression, compare side-by-side afterwards",
    "Добавьте PDF, чтобы открыть его здесь": "Add a PDF to preview it here",
    "Вписать": "Fit page",
    "↻  Повернуть": "↻  Rotate",
    "Повернуть только просмотр на 90°; сам PDF не меняется": "Rotate preview 90° only; the PDF is not changed",
    "Добавьте PDF, чтобы увидеть страницу": "Add a PDF to preview the page",
    "ОРИГИНАЛ": "ORIGINAL",
    "ПОСЛЕ СЖАТИЯ": "AFTER COMPRESSION",
    "Выберите документ": "Select a document",
    "Результат появится после сжатия": "Output will appear after compression",
    "Результат": "Result",
    "Нет обработанных файлов": "No files processed",
    "До сжатия будет показан оригинал в полном размере области.": "The original will fill the preview area before compression.",
    "Инструменты PDF": "PDF tools",
    "Инструменты для PDF": "PDF tools",
    "Объединяйте документы, извлекайте страницы и поворачивайте PDF. Файлы берутся из списка на вкладке «Сжатие и просмотр».": "Merge documents, extract pages and rotate PDFs. Files come from the list in Compress & preview.",
    "Объединить PDF": "Merge PDFs",
    "Соединить все файлы из списка в один PDF": "Combine all queued files into one PDF",
    "Имя итогового файла": "Output filename",
    "Объединить все PDF": "Merge all PDFs",
    "Разделить PDF / извлечь страницы": "Split PDF / extract pages",
    "Из выбранного документа в очереди": "Use the selected PDF in the queue",
    "Страницы:": "Pages:",
    "1-3,5,8 или все": "1-3,5,8 or all",
    "Каждую страницу отдельно": "Each page as a separate PDF",
    "Извлечь страницы": "Extract pages",
    "Пример: 1-3,5 объединит выбранные страницы в один новый PDF; галочка создаст отдельный файл для каждой.": "Example: 1-3,5 saves the selected pages as one PDF; enable the checkbox to save each page separately.",
    "Повернуть страницы": "Rotate pages",
    "Поворот без перекодирования изображений": "Rotate without recompressing images",
    "все или 1-3,6": "all or 1-3,6",
    "Угол:": "Angle:",
    "Повернуть PDF": "Rotate PDF",
    "Открыть папку": "Open folder",
    "PDF успешно объединены": "PDFs merged successfully",
    "Страницы успешно извлечены": "Pages extracted successfully",
    "PDF успешно повёрнут": "PDF rotated successfully",
    "Создан файл:": "File created:",
    "Папка:": "Folder:",
    "Не найдена папка результата.": "Output folder not found.",
    "Без интернета · Без загрузки в облако · Исходные файлы не изменяются": "Works offline · No cloud uploads · Original files are unchanged",
    "Укажите корректный размер PDF, например 1 или 0,5 МБ": "Enter a valid PDF size, such as 1 or 0.5 MB",
    "Добавить PDF": "Add PDF",
    "В очереди": "Queued",
    "Не удалось добавить PDF": "Could not add PDF",
    "Готово": "Done",
    "Инструмент: готово": "Completed",
    "Ошибка": "Error",
    "Цель не достигнута": "Target not reached",
    "Выберите PDF": "Select a PDF",
    "Пока нет обработанного PDF.": "No processed PDF yet.",
    "Папка для сохранения": "Choose output folder",
    "В PDF нет выбранной страницы": "The selected page is not in this PDF",
    "Не удалось загрузить страницу": "Could not load page",
    "Не найден оригинал": "Original PDF not found",
    "После сжатия здесь появится результат": "The compressed PDF will appear here",
    "Сначала сожмите документ": "Compress the document first",
    "Сжатие завершено. Откройте результат, чтобы проверить качество.": "Compression complete. Open the result to check image quality.",
    "Выберите режим и нажмите «Сжать все PDF». Для скана боком используйте кнопку «Повернуть» — только для просмотра.": "Choose a mode and click Compress all PDFs. Use Rotate for sideways scans (preview only).",
    "Укажите папку для результата": "Choose an output folder",
    "Сначала добавьте хотя бы один PDF": "Add at least one PDF first",
    "Файлы": "Files",
    "Настройки": "Settings",
    "Выделите документ в таблице вкладки «Сжатие PDF».": "Select a document in the Compress & preview file list.",
    "Добавьте минимум два PDF.": "Add at least two PDFs.",
    "Объединение": "Merge PDFs",
    "Папка": "Folder",
    "Ошибка операции": "Operation failed",
    "Обработка": "Processing",
    "Сначала нажмите «Отменить» и дождитесь завершения текущей операции.": "Click Cancel and wait for the current operation to finish before closing.",
    "Отмена запрошена. Завершается текущий этап…": "Cancel requested. Finishing the current step…",
    "Операция завершена": "Operation finished",
    "Оптимизация без потерь": "Lossless optimization",
    "Без изменений (файл уже оптимизирован)": "Unchanged (file already optimized)",
    "Проверка и оптимизация без потерь": "Checking and optimizing losslessly",
    "Обработка страниц": "Processing pages",
    "Цель достигнута без потерь изображения": "Target achieved without image quality loss",
    "Объединение файлов": "Merging files",
    "Извлечение страниц": "Extracting pages",
    "PDF защищён паролем": "PDF is password-protected",
    "PDF защищён паролем. Сначала создайте незашифрованную копию.": "PDF is password-protected. First create an unencrypted copy.",
    "В документе нет страниц": "The document has no pages",
    "PDF содержит поля цифровой подписи. Изменение файла может нарушить подпись; обработка заблокирована.": "PDF contains digital signature fields. Editing can invalidate signatures, so this operation is blocked.",
    "Документ пуст": "The document is empty",
    "Диапазон должен идти по возрастанию": "Page ranges must increase",
    "Не выбраны страницы": "No pages selected",
    "Укажите существующий PDF-файл": "Select an existing PDF file",
    "Целевой размер должен быть от 0,01 до 100000 МБ": "Target size must be between 0.01 and 100000 MB",
    "Неизвестный режим сжатия": "Unknown compression mode",
    "Число страниц изменилось после сжатия": "Page count changed after compression",
    "Для объединения нужно минимум два PDF": "At least two PDFs are required to merge",
    "Допустимый поворот: 90, 180 или 270 градусов": "Valid rotation angles are 90, 180 or 270 degrees",
    "Операция отменена пользователем": "Operation cancelled by user",
    "Локальная обработка": "Local processing",
    "Готов к работе · исходные файлы не изменяются": "Ready · original PDFs remain unchanged",
    "Оригинал:": "Original:",
    "Файл": "File",
    "Созданы:": "Created:",
    "Создано файлов:": "Files created:",
    "Ошибка предпросмотра:": "Preview error:",
    "Цель не достигнута": "Target not achieved",
    " · цель не достигнута": " · target not achieved",
    "Обработано": "Processed",
    "Страница": "Page",
    "страница": "page",
    "Результат появится после обработки": "Output will appear after processing",
    "Нет файла": "File not found",
    "Добавьте PDF, чтобы увидеть страницу": "Add a PDF to preview it",
    "Ошибка предпросмотра": "Preview error",
    "Неверный диапазон страниц": "Invalid page range",
    "Все страницы": "All pages",
    "Операция отменена": "Operation cancelled",
    "Успешно": "Completed",
    "Ошибок": "Errors",
    "Готово.": "Done.",
    "MB": "MB",
    "все": "all",
    "объединённый": "merged",
    "{name}_сжатый": "{name}_compressed",
}

ENGINE_PARTS_EN = (
    ("Неверный диапазон страниц:", "Invalid page range:"),
    ("Страница ", "Page "),
    (" вне диапазона ", " outside range "),
    (". Пример:", ". Example:"),
    ("Подбор качества ", "Trying JPEG quality "),
    (", исходное разрешение", ", original resolution"),
    (", до ", ", up to "),
    ("Создано файлов:", "Files created:"),
    ("Ошибка предпросмотра:", "Preview error:"),
    ("Не удалось создать папку:", "Could not create folder:"),
    ("Файл ", "File "),
    (" • страница ", " • page "),
    (" • страницы ", " • pages "),
    ("  •  страница ", "  •  page "),
    ("Готово. Успешно:", "Done. Completed:"),
    ("Ошибок:", "Errors:"),
    ("Операция отменена. Успешно завершено:", "Cancelled. Completed:"),
    ("Оригинал:", "Original:"),
    ("Цель не достигнута", "Target not reached"),
    ("Готово", "Done"),
    ("В очереди", "Queued"),
    ("Инструмент: готово", "Tool completed"),
    ("Ошибка", "Error"),
    ("JPEG, исходное разрешение", "JPEG, original resolution"),
    ("Успешно:", "Completed:"),
    ("Поворот страниц", "Rotating pages"),
    (" · цель не достигнута", " · target not reached"),
    (" МБ", " MB"),
    (" КБ", " KB"),
    (" ГБ", " GB"),
)


def tr(text: str, language: str) -> str:
    """Translate a fixed UI message, preserving Russian as the reference copy."""
    return I18N_EN.get(text, text) if language == "en" else text


def tr_engine(text: str, language: str) -> str:
    """Translate engine messages without modifying the PDF engine or its files."""
    if language != "en":
        return text
    text = I18N_EN.get(text, text)
    for ru, en in ENGINE_PARTS_EN:
        text = text.replace(ru, en)
    return text


def display_size(byte_count: int, language: str) -> str:
    """Keep unit labels consistent with the selected language."""
    result = human_size(byte_count)
    if language == "en":
        for ru, en in (("ГБ", "GB"), ("МБ", "MB"), ("КБ", "KB"), ("Б", "B")):
            if result.endswith(" " + ru):
                return result[: -len(ru)] + en
    return result



def only_pdf(path: str) -> bool:
    return Path(path).is_file() and Path(path).suffix.lower() == ".pdf"


def open_file(path: str):
    QDesktopServices.openUrl(QUrl.fromLocalFile(str(Path(path).resolve())))


class RoundedCard(QFrame):
    """A single anti-aliased border and background (no QGroupBox title cut-outs).

    Content is inset by its layout, so child widgets never overlap the rounded corners.
    """
    def __init__(self, parent=None, radius=13):
        super().__init__(parent)
        self.radius = radius
        self._fill = "#1b2230"
        self._stroke = "#344157"
        self.setFrameShape(QFrame.NoFrame)
        self.setAutoFillBackground(False)

    def set_card_colors(self, fill: str, stroke: str):
        self._fill, self._stroke = fill, stroke
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(QColor(self._stroke), 1.0))
        painter.setBrush(QColor(self._fill))
        painter.drawRoundedRect(QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5),
                                self.radius, self.radius)


class DropArea(QFrame):
    files_dropped = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("DropArea")
        self.setAcceptDrops(True)
        self.setMinimumHeight(56)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(2)
        title = QLabel("⇩  Перетащите сюда PDF-файлы")
        title.setObjectName("DropTitle")
        title.setAlignment(Qt.AlignCenter)
        subtitle = QLabel("Или нажмите «Добавить файлы» · несколько документов сразу")
        subtitle.setObjectName("Muted")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        layout.addWidget(subtitle)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() and any(u.toLocalFile().lower().endswith(".pdf") for u in event.mimeData().urls()):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        paths = [u.toLocalFile() for u in event.mimeData().urls() if u.isLocalFile()]
        self.files_dropped.emit(paths)
        event.acceptProposedAction()


class PreviewPane(QScrollArea):
    """Fit-to-panel preview, with zoom relative to the fitted page."""

    def __init__(self, empty_text: str, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(False)
        self.setAlignment(Qt.AlignCenter)
        self.setFrameShape(QFrame.NoFrame)
        self.setObjectName("PreviewPane")
        self.setMinimumSize(200, 200)
        self._base_pixmap = QPixmap()
        self._zoom = 1.0
        self.label = QLabel(empty_text)
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setObjectName("Preview")
        self.label.setFixedSize(240, 240)
        self.setWidget(self.label)

    def set_zoom(self, zoom: float):
        self._zoom = max(1.0, float(zoom or 1.0))
        self._update_view()

    def clear_message(self, text: str):
        self._base_pixmap = QPixmap()
        self.label.setPixmap(QPixmap())
        self.label.setText(text)
        self.label.setFixedSize(max(180, self.viewport().width()-10),
                                max(180, self.viewport().height()-10))

    def set_preview(self, pixmap: QPixmap):
        self._base_pixmap = pixmap
        self._update_view()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._base_pixmap.isNull():
            self.label.setFixedSize(max(180, self.viewport().width()-10),
                                    max(180, self.viewport().height()-10))
        else:
            self._update_view()

    def _update_view(self):
        if self._base_pixmap.isNull():
            return
        # Keep zoom anchored to fit size, so 100% always shows the entire page.
        viewport = self.viewport().size()
        if viewport.width() < 50 or viewport.height() < 50:
            return
        fit_factor = min((viewport.width()-18)/self._base_pixmap.width(),
                         (viewport.height()-18)/self._base_pixmap.height())
        scale = min(4.0, fit_factor * self._zoom)
        target_w = max(1, round(self._base_pixmap.width() * scale))
        target_h = max(1, round(self._base_pixmap.height() * scale))
        scaled = self._base_pixmap.scaled(target_w, target_h,
                                          Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.label.setPixmap(scaled)
        self.label.setFixedSize(scaled.size())



class JobWorker(QObject):
    progress = Signal(str, int, int)
    result = Signal(int, object)
    timing = Signal(int, float)
    finished = Signal(str)

    def __init__(self, action: str, inputs: list[str], options: dict):
        super().__init__()
        self.action = action
        self.inputs = inputs
        self.options = options
        self.cancel = threading.Event()

    def stop(self):
        self.cancel.set()

    def run(self):
        errors = 0
        completed = 0
        try:
            if self.action == "compress":
                reserved: set[str] = set()
                for idx, src in enumerate(self.inputs):
                    if self.cancel.is_set():
                        raise Cancelled()
                    self.progress.emit(f"Файл {idx + 1}/{len(self.inputs)}: {Path(src).name}", 0, 1)
                    started_at = perf_counter()
                    try:
                        result = compress_pdf(src, self.options["folder"],
                            mode=self.options["mode"], target_mb=self.options["target"],
                            allow_downscale=self.options["downscale"],
                            name_template=self.options["template"], reserved=reserved,
                            cancel=self.cancel,
                            progress=lambda stage, cur, total, idx=idx:
                                self.progress.emit(f"{idx + 1}/{len(self.inputs)} • {stage}", cur, total))
                        self.timing.emit(idx, perf_counter() - started_at)
                        self.result.emit(idx, result)
                        completed += 1
                    except Cancelled:
                        raise
                    except Exception as e:
                        self.timing.emit(idx, perf_counter() - started_at)
                        self.result.emit(idx, e)
                        errors += 1
            elif self.action == "merge":
                output = merge_pdfs(self.inputs, self.options["folder"],
                    self.options["name"], cancel=self.cancel, progress=self.progress.emit)
                self.result.emit(-1, str(output))
                completed = 1
            elif self.action == "split":
                for idx, src in enumerate(self.inputs):
                    if self.cancel.is_set():
                        raise Cancelled()
                    try:
                        outputs = split_pdf(src, self.options["folder"],
                            pages=self.options["pages"], each_page=self.options["each"],
                            cancel=self.cancel, progress=lambda stage, cur, total, idx=idx:
                                self.progress.emit(f"{idx+1}/{len(self.inputs)} • {stage}", cur, total))
                        self.result.emit(idx, outputs)
                        completed += 1
                    except Cancelled:
                        raise
                    except Exception as e:
                        self.result.emit(idx, e)
                        errors += 1
            elif self.action == "rotate":
                for idx, src in enumerate(self.inputs):
                    if self.cancel.is_set():
                        raise Cancelled()
                    try:
                        output = rotate_pdf(src, self.options["folder"],
                            degrees=self.options["degrees"], pages=self.options["pages"],
                            cancel=self.cancel, progress=lambda stage, cur, total, idx=idx:
                                self.progress.emit(f"{idx+1}/{len(self.inputs)} • {stage}", cur, total))
                        self.result.emit(idx, str(output))
                        completed += 1
                    except Cancelled:
                        raise
                    except Exception as e:
                        self.result.emit(idx, e)
                        errors += 1
        except Cancelled:
            self.finished.emit(f"Операция отменена. Успешно завершено: {completed}.")
            return
        except Exception as e:
            self.result.emit(-1, e)
            errors += 1
        self.finished.emit(f"Готово. Успешно: {completed}. Ошибок: {errors}.")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("LocalPDF", "PDFCompressor2")
        self.entries: list[dict] = []
        self.active_paths: list[str] = []
        self.last_created_path: str | None = None
        self.thread: QThread | None = None
        self.worker: JobWorker | None = None
        self.busy = False
        self._active_action: str | None = None
        self._tool_focus_button: QPushButton | None = None
        self._tool_outputs: list[str] = []
        self._tool_errors: list[str] = []
        self._tool_feedback_state: dict | None = None
        self.selected_source: str | None = None
        self.preview_cache: dict[tuple[str, int], QPixmap] = {}
        self.preview_rotation = 0
        self.dark = str(self.settings.value("dark", "true")).lower() == "true"
        self.language = str(self.settings.value("language", "ru"))
        if self.language not in ("ru", "en"):
            self.language = "ru"
        self._original_texts = []
        self._status_ru = "Готов к работе · исходные файлы не изменяются"
        self.setWindowTitle("PDF Compressor 2.7  •  Локальная обработка")
        asset_folder = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
        icon_path = asset_folder / "app_icon.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        self.setMinimumSize(960, 650)
        self.resize(1360, 800)
        self.setAcceptDrops(True)
        self.build_ui()
        self.capture_texts()
        self.restore_settings()
        self.apply_language()
        self.apply_theme()

    def build_ui(self):
        central = QWidget()
        central.setObjectName("Central")
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(18, 13, 18, 13)
        root.setSpacing(11)

        header = QHBoxLayout()
        header.setSpacing(9)
        brand = QLabel("▣")
        brand.setObjectName("AccentIcon")
        header.addWidget(brand)
        title = QLabel("PDF Compressor")
        title.setObjectName("Title")
        header.addWidget(title)
        version = QLabel("2.7")
        version.setObjectName("Badge")
        header.addWidget(version)
        header.addStretch(1)
        privacy = QLabel("●  Документы остаются на компьютере")
        privacy.setObjectName("Muted")
        header.addWidget(privacy)
        self.language_box = QComboBox()
        self.language_box.setObjectName("LanguageBox")
        self.language_box.addItem("Русский", "ru")
        self.language_box.addItem("English", "en")
        self.language_box.setToolTip("Язык интерфейса / Interface language")
        self.language_box.setMinimumWidth(102)
        self.language_box.setCurrentIndex(1 if self.language == "en" else 0)
        self.language_box.currentIndexChanged.connect(self.change_language)
        header.addWidget(self.language_box)
        self.theme_btn = QPushButton("Светлая тема")
        self.theme_btn.setObjectName("Secondary")
        self.theme_btn.clicked.connect(self.toggle_theme)
        header.addWidget(self.theme_btn)
        root.addLayout(header)

        self.tabs = QTabWidget()
        root.addWidget(self.tabs, 1)
        compression = QWidget()
        compression.setObjectName("TabBody")
        self.tabs.addTab(compression, "Сжатие и просмотр")
        page_layout = QVBoxLayout(compression)
        page_layout.setContentsMargins(6, 6, 6, 6)
        page_layout.setSpacing(0)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setObjectName("MainSplit")
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(7)
        page_layout.addWidget(splitter, 1)
        self.main_split = splitter

        # LEFT — file queue, parameters and persistent actions.
        left = QWidget()
        left.setObjectName("LeftPanel")
        left.setMinimumWidth(395)
        left_outer = QVBoxLayout(left)
        left_outer.setContentsMargins(7, 7, 13, 8)
        left_outer.setSpacing(7)
        splitter.addWidget(left)

        # Only the upper content scrolls when a screen is too short.
        # The compression actions remain visible below it.
        self.left_scroll = QScrollArea()
        self.left_scroll.setObjectName("LeftScroll")
        self.left_scroll.setWidgetResizable(True)
        self.left_scroll.setFrameShape(QFrame.NoFrame)
        self.left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.left_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.left_scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        left_content = QWidget()
        left_content.setObjectName("LeftContent")
        ll = QVBoxLayout(left_content)
        ll.setContentsMargins(0, 0, 3, 3)
        ll.setSpacing(7)
        ll.setSizeConstraint(QLayout.SetMinimumSize)
        self.left_scroll.setWidget(left_content)
        left_outer.addWidget(self.left_scroll, 1)

        row_heading = QHBoxLayout()
        h = QLabel("Документы")
        h.setObjectName("SectionTitle")
        row_heading.addWidget(h)
        row_heading.addStretch()
        self.count = QLabel("0 PDF")
        self.count.setObjectName("Badge")
        row_heading.addWidget(self.count)
        ll.addLayout(row_heading)

        self.drop = DropArea()
        self.drop.setFixedHeight(58)
        self.drop.files_dropped.connect(self.add_files)
        ll.addWidget(self.drop)

        actions_files = QHBoxLayout()
        actions_files.setSpacing(7)
        self.add_btn = QPushButton("+ Добавить файлы")
        self.add_btn.setObjectName("Primary")
        self.add_btn.clicked.connect(self.pick_files)
        self.remove_btn = QPushButton("Удалить")
        self.remove_btn.clicked.connect(self.remove_selected)
        self.clear_btn = QPushButton("Очистить")
        self.clear_btn.clicked.connect(self.clear_files)
        actions_files.addWidget(self.add_btn, 1)
        actions_files.addWidget(self.remove_btn)
        actions_files.addWidget(self.clear_btn)
        ll.addLayout(actions_files)

        table_card = RoundedCard(radius=13)
        table_card.setObjectName("FileTableCard")
        table_layout = QVBoxLayout(table_card)
        # The table/header is inset: the square native header can no longer
        # paint over the rounded outer border.
        table_layout.setContentsMargins(8, 8, 8, 8)
        table_layout.setSpacing(0)
        self.table = QTableWidget(0, 3)
        self.table.setObjectName("FileTable")
        self.table.setHorizontalHeaderLabels(["PDF-файл", "Размер", "Статус"])
        self.table.verticalHeader().hide()
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.table.setColumnWidth(1, 79)
        self.table.setColumnWidth(2, 128)
        self.table.horizontalHeader().setFixedHeight(36)
        self.table.verticalHeader().setDefaultSectionSize(35)
        self.table.horizontalHeaderItem(1).setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table.horizontalHeaderItem(2).setTextAlignment(Qt.AlignCenter)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setWordWrap(False)
        self.table.setTextElideMode(Qt.ElideMiddle)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setFrameShape(QFrame.NoFrame)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.setMinimumHeight(110)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.table.cellDoubleClicked.connect(self.on_double_clicked)
        table_layout.addWidget(self.table)
        table_card.setFixedHeight(137)
        ll.addWidget(table_card)

        controls_card = RoundedCard()
        controls_card.setObjectName("SettingsCard")
        cl = QVBoxLayout(controls_card)
        cl.setContentsMargins(13, 11, 13, 12)
        cl.setSpacing(6)
        heading = QLabel("Параметры сжатия")
        heading.setObjectName("CardCaption")
        cl.addWidget(heading)
        mode_line = QHBoxLayout()
        mode_line.setSpacing(8)
        mode_line.addWidget(QLabel("Режим"))
        self.mode = QComboBox()
        self.mode.addItem("SmartFit · автоматически", "smartfit")
        self.mode.addItem("До заданного размера", "target")
        self.mode.addItem("Максимальное качество", "quality")
        self.mode.addItem("Сбалансированный", "balanced")
        self.mode.addItem("Максимальное сжатие", "smallest")
        self.mode.currentIndexChanged.connect(self.on_mode_changed)
        mode_line.addWidget(self.mode, 1)
        self.target_label = QLabel("МБ")
        mode_line.addWidget(self.target_label)
        self.target = QLineEdit("1,00")
        self.target.setValidator(QRegularExpressionValidator(
            QRegularExpression(r"[0-9]{1,6}(?:[,.][0-9]{0,2})?"), self))
        self.target.setAlignment(Qt.AlignCenter)
        self.target.setFixedWidth(64)
        self.target.setToolTip("Целевой размер в мегабайтах, например 1 или 0,5")
        mode_line.addWidget(self.target)
        cl.addLayout(mode_line)
        self.downscale = QCheckBox("Разрешить уменьшение разрешения при необходимости")
        self.downscale.setToolTip("Если размер недостижим без изменения числа пикселей, можно уменьшить разрешение изображений.")
        cl.addWidget(self.downscale)
        self.smartfit_note = QLabel("SmartFit анализирует тип PDF и подбирает сжатие. После обработки проверьте документ в предпросмотре.")
        self.smartfit_note.setObjectName("Muted")
        self.smartfit_note.setWordWrap(True)
        self.smartfit_note.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        cl.addWidget(self.smartfit_note)
        label = QLabel("Сохранение результата")
        label.setObjectName("CardCaption")
        cl.addWidget(label)
        folder_line = QHBoxLayout()
        folder_line.setSpacing(6)
        self.folder_edit = QLineEdit()
        self.folder_edit.setPlaceholderText("Папка для результатов")
        self.folder_edit.setToolTip("Новые PDF сохраняются сюда, оригиналы не изменяются")
        folder_line.addWidget(self.folder_edit, 1)
        browse = QPushButton("Обзор…")
        browse.setObjectName("Quiet")
        browse.clicked.connect(self.pick_folder)
        folder_line.addWidget(browse)
        cl.addLayout(folder_line)
        name_line = QHBoxLayout()
        name_line.setSpacing(7)
        name_line.addWidget(QLabel("Имя"))
        self.template = QLineEdit("{name}_сжатый")
        self.template.setToolTip("{name} заменяется именем исходного файла; совпадения получают суффикс _2, _3…")
        name_line.addWidget(self.template, 1)
        cl.addLayout(name_line)
        # Avoid squashing the last row of inputs against the rounded border.
        # The scroll area will provide overflow instead on low-height screens.
        controls_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        controls_card.setMinimumHeight(213)
        self.controls_card = controls_card
        ll.addWidget(controls_card)
        ll.addStretch(0)

        command_line = QHBoxLayout()
        command_line.setSpacing(7)
        self.start_btn = QPushButton("▶  Сжать все PDF")
        self.start_btn.setObjectName("Primary")
        self.start_btn.clicked.connect(self.start_compression)
        command_line.addWidget(self.start_btn, 3)
        self.cancel_btn = QPushButton("■ Отменить")
        self.cancel_btn.setObjectName("Danger")
        self.cancel_btn.clicked.connect(self.cancel_operation)
        self.cancel_btn.setEnabled(False)
        command_line.addWidget(self.cancel_btn, 1)
        left_outer.addLayout(command_line)
        self.open_btn = QPushButton("Открыть готовый PDF")
        self.open_btn.setObjectName("Quiet")
        self.open_btn.clicked.connect(self.open_selected_result)
        left_outer.addWidget(self.open_btn)
        self.progressbar = QProgressBar()
        self.progressbar.setRange(0, 100)
        self.progressbar.setValue(0)
        self.progressbar.setTextVisible(True)
        left_outer.addWidget(self.progressbar)
        self.status = QLabel("Готов к работе · исходные файлы не изменяются")
        self.status.setObjectName("Muted")
        self.status.setWordWrap(True)
        left_outer.addWidget(self.status)

        # RIGHT — a single large page before compression; automatic A/B after.
        right = QWidget()
        right.setObjectName("RightPanel")
        right.setMinimumWidth(475)
        rl = QVBoxLayout(right)
        rl.setContentsMargins(15, 7, 7, 8)
        rl.setSpacing(10)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([480, 860])

        right_title = QHBoxLayout()
        text_title = QLabel("Просмотр PDF")
        text_title.setObjectName("SectionTitle")
        right_title.addWidget(text_title)
        right_title.addStretch(1)
        self.view_mode = QComboBox()
        self.view_mode.addItem("Автоматически", "auto")
        self.view_mode.addItem("До и после", "compare")
        self.view_mode.addItem("Только оригинал", "original")
        self.view_mode.addItem("Только результат", "result")
        self.view_mode.setToolTip("Авто: большой оригинал до сжатия, два документа после")
        self.view_mode.setMinimumWidth(160)
        self.view_mode.currentIndexChanged.connect(self.update_preview)
        right_title.addWidget(self.view_mode)
        rl.addLayout(right_title)
        self.document_name = QLabel("Добавьте PDF, чтобы открыть его здесь")
        self.document_name.setObjectName("Muted")
        self.document_name.setTextInteractionFlags(Qt.TextSelectableByMouse)
        rl.addWidget(self.document_name)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(5)
        self.prev_btn = QPushButton("‹")
        self.prev_btn.setObjectName("Tiny")
        self.prev_btn.setFixedWidth(30)
        self.prev_btn.clicked.connect(lambda: self.change_page(-1))
        self.prev_btn.setEnabled(False)
        toolbar.addWidget(self.prev_btn)
        self.page_number = QLineEdit("1")
        self.page_number.setValidator(QIntValidator(1, 100000, self))
        self.page_number.setAlignment(Qt.AlignCenter)
        self.page_number.setFixedWidth(44)
        self.page_number.editingFinished.connect(self.update_preview)
        toolbar.addWidget(self.page_number)
        self.page_total = QLabel("/ 1")
        self.page_total.setObjectName("Muted")
        toolbar.addWidget(self.page_total)
        self.next_btn = QPushButton("›")
        self.next_btn.setObjectName("Tiny")
        self.next_btn.setFixedWidth(30)
        self.next_btn.clicked.connect(lambda: self.change_page(1))
        self.next_btn.setEnabled(False)
        toolbar.addWidget(self.next_btn)
        toolbar.addStretch()
        self.zoom = QComboBox()
        for factor, label in ((1.0,"Вписать"),(1.25,"125%"),(1.5,"150%"),(2.0,"200%"),(2.5,"250%"),(3.0,"300%")):
            self.zoom.addItem(label, factor)
        self.zoom.setMinimumWidth(90)
        self.zoom.currentIndexChanged.connect(self.update_preview)
        toolbar.addWidget(self.zoom)
        self.rotate_preview_btn = QPushButton("↻  Повернуть")
        self.rotate_preview_btn.setToolTip("Повернуть только просмотр на 90°; сам PDF не меняется")
        self.rotate_preview_btn.clicked.connect(self.rotate_preview)
        toolbar.addWidget(self.rotate_preview_btn)
        rl.addLayout(toolbar)

        self.preview_stack = QStackedWidget()
        self.preview_stack.setObjectName("PreviewStack")
        self.single_preview = PreviewPane("Добавьте PDF, чтобы увидеть страницу")
        self.preview_stack.addWidget(self.single_preview)
        comparison = QWidget()
        compare_layout = QHBoxLayout(comparison)
        compare_layout.setContentsMargins(0, 0, 0, 0)
        compare_layout.setSpacing(8)
        self.preview_widgets = []
        for caption, placeholder in (("ОРИГИНАЛ", "Выберите документ"),
                                     ("ПОСЛЕ СЖАТИЯ", "Результат появится после сжатия")):
            wrap = QWidget()
            inner = QVBoxLayout(wrap)
            inner.setContentsMargins(0, 0, 0, 0)
            inner.setSpacing(6)
            lbl = QLabel(caption)
            lbl.setObjectName("CardCaption")
            inner.addWidget(lbl)
            pane = PreviewPane(placeholder)
            inner.addWidget(pane, 1)
            compare_layout.addWidget(wrap, 1)
            self.preview_widgets.append(pane)
        self.preview_stack.addWidget(comparison)
        rl.addWidget(self.preview_stack, 1)

        result_card = RoundedCard()
        result_card.setObjectName("ResultCard")
        result_layout = QVBoxLayout(result_card)
        result_layout.setContentsMargins(16, 12, 16, 12)
        result_layout.setSpacing(4)
        stat_row = QHBoxLayout()
        self.result_title = QLabel("Результат")
        self.result_title.setObjectName("CardCaption")
        stat_row.addWidget(self.result_title)
        stat_row.addStretch()
        self.result_metric = QLabel("Нет обработанных файлов")
        self.result_metric.setObjectName("ResultMetric")
        stat_row.addWidget(self.result_metric)
        result_layout.addLayout(stat_row)
        self.compare_status = QLabel("До сжатия будет показан оригинал в полном размере области.")
        self.compare_status.setWordWrap(True)
        self.compare_status.setObjectName("Muted")
        result_layout.addWidget(self.compare_status)
        rl.addWidget(result_card)

        tools_page = QWidget()
        self.tools_page = tools_page
        tools_page.setObjectName("ToolsPage")
        self.tabs.addTab(tools_page, "Инструменты PDF")
        tools_outer = QHBoxLayout(tools_page)
        tools_outer.setContentsMargins(4, 0, 4, 0)
        tools_shell = QWidget()
        tools_shell.setObjectName("ToolsShell")
        tools_shell.setMaximumWidth(1040)
        tools_outer.addStretch(1)
        tools_outer.addWidget(tools_shell, 20)
        tools_outer.addStretch(1)
        tools_layout = QVBoxLayout(tools_shell)
        tools_layout.setContentsMargins(24, 24, 24, 22)
        tools_layout.setSpacing(14)
        tool_title = QLabel("Инструменты для PDF")
        tool_title.setObjectName("SectionTitle")
        tools_layout.addWidget(tool_title)
        help_label = QLabel("Объединяйте документы, извлекайте страницы и поворачивайте PDF. Файлы берутся из списка на вкладке «Сжатие и просмотр».")
        help_label.setWordWrap(True)
        help_label.setObjectName("Muted")
        tools_layout.addWidget(help_label)

        merge_group = RoundedCard()
        merge_group.setObjectName("ToolCard")
        mg_outer = QVBoxLayout(merge_group)
        mg_outer.setContentsMargins(18, 16, 18, 18)
        mg_outer.setSpacing(11)
        mg_outer.addLayout(self.make_tool_heading(
            "01", "Объединить PDF", "Соединить все файлы из списка в один PDF"))
        mg = QHBoxLayout()
        mg.setSpacing(8)
        mg.addWidget(QLabel("Имя итогового файла"))
        self.merge_name = QLineEdit("объединённый")
        mg.addWidget(self.merge_name, 1)
        self.merge_btn = QPushButton("Объединить все PDF")
        self.merge_btn.setObjectName("Primary")
        self.merge_btn.clicked.connect(self.start_merge)
        mg.addWidget(self.merge_btn)
        mg_outer.addLayout(mg)
        tools_layout.addWidget(merge_group)

        split_group = RoundedCard()
        split_group.setObjectName("ToolCard")
        sg = QVBoxLayout(split_group)
        sg.setContentsMargins(18, 16, 18, 18)
        sg.setSpacing(11)
        sg.addLayout(self.make_tool_heading(
            "02", "Разделить PDF / извлечь страницы", "Из выбранного документа в очереди"))
        sr = QHBoxLayout()
        sr.setSpacing(8)
        sr.addWidget(QLabel("Страницы:"))
        self.split_pages = QLineEdit("все")
        self.split_pages.setPlaceholderText("1-3,5,8 или все")
        sr.addWidget(self.split_pages, 1)
        self.split_each = QCheckBox("Каждую страницу отдельно")
        sr.addWidget(self.split_each)
        self.split_btn = QPushButton("Извлечь страницы")
        self.split_btn.setObjectName("Primary")
        self.split_btn.clicked.connect(self.start_split)
        sr.addWidget(self.split_btn)
        sg.addLayout(sr)
        tip = QLabel("Пример: 1-3,5 объединит выбранные страницы в один новый PDF; галочка создаст отдельный файл для каждой.")
        tip.setObjectName("Muted")
        tip.setWordWrap(True)
        sg.addWidget(tip)
        tools_layout.addWidget(split_group)

        rotate_group = RoundedCard()
        rotate_group.setObjectName("ToolCard")
        rg_outer = QVBoxLayout(rotate_group)
        rg_outer.setContentsMargins(18, 16, 18, 18)
        rg_outer.setSpacing(11)
        rg_outer.addLayout(self.make_tool_heading(
            "03", "Повернуть страницы", "Поворот без перекодирования изображений"))
        rg = QHBoxLayout()
        rg.setSpacing(8)
        rg.addWidget(QLabel("Страницы:"))
        self.rotate_pages = QLineEdit("все")
        self.rotate_pages.setPlaceholderText("все или 1-3,6")
        rg.addWidget(self.rotate_pages, 1)
        rg.addWidget(QLabel("Угол:"))
        self.degrees = QComboBox()
        for degree in (90, 180, 270):
            self.degrees.addItem(f"{degree}°", degree)
        rg.addWidget(self.degrees)
        self.rotate_btn = QPushButton("Повернуть PDF")
        self.rotate_btn.setObjectName("Primary")
        self.rotate_btn.clicked.connect(self.start_rotate)
        rg.addWidget(self.rotate_btn)
        rg_outer.addLayout(rg)
        tools_layout.addWidget(rotate_group)

        # Show results inline without opening Explorer or a modal dialog.
        self.tool_result_card = RoundedCard()
        self.tool_result_card.setObjectName("ToolCard")
        feedback_row = QHBoxLayout(self.tool_result_card)
        feedback_row.setContentsMargins(18, 14, 18, 14)
        feedback_row.setSpacing(12)
        feedback_text = QVBoxLayout()
        feedback_text.setSpacing(5)
        self.tool_result_title = QLabel("")
        self.tool_result_title.setObjectName("ToolCardTitle")
        feedback_text.addWidget(self.tool_result_title)
        self.tool_result_detail = QLabel("")
        self.tool_result_detail.setObjectName("Muted")
        self.tool_result_detail.setTextFormat(Qt.PlainText)
        self.tool_result_detail.setWordWrap(True)
        self.tool_result_detail.setTextInteractionFlags(Qt.TextSelectableByMouse)
        feedback_text.addWidget(self.tool_result_detail)
        feedback_row.addLayout(feedback_text, 1)
        self.open_tool_folder_btn = QPushButton("Открыть папку")
        self.open_tool_folder_btn.setObjectName("Secondary")
        self.open_tool_folder_btn.clicked.connect(self.open_tool_result_folder)
        feedback_row.addWidget(self.open_tool_folder_btn)
        tools_layout.addWidget(self.tool_result_card)
        self.tool_result_card.hide()
        tools_layout.addStretch()
        footer = QLabel("Без интернета · Без загрузки в облако · Исходные файлы не изменяются")
        footer.setObjectName("Muted")
        tools_layout.addWidget(footer)

    @staticmethod
    def make_tool_heading(number: str, title: str, subtitle: str):
        heading = QHBoxLayout()
        heading.setSpacing(12)
        badge = QLabel(number)
        badge.setObjectName("ToolNumber")
        badge.setAlignment(Qt.AlignCenter)
        badge.setFixedSize(36, 36)
        heading.addWidget(badge)
        labels = QVBoxLayout()
        labels.setSpacing(2)
        name = QLabel(title)
        name.setObjectName("ToolCardTitle")
        labels.addWidget(name)
        description = QLabel(subtitle)
        description.setObjectName("Muted")
        description.setWordWrap(True)
        labels.addWidget(description)
        heading.addLayout(labels, 1)
        return heading

    def t(self, ru: str) -> str:
        return tr(ru, self.language)

    def translated(self, ru: str) -> str:
        return tr_engine(str(ru), self.language)

    def capture_texts(self):
        """Capture original UI labels once; widgets aren't reconstructed on switch."""
        dynamic = {self.count, self.status, self.document_name, self.result_metric,
                   self.compare_status, self.page_total, self.theme_btn, self.start_btn,
                   self.smartfit_note, self.tool_result_title, self.tool_result_detail,
                   self.single_preview.label, *(p.label for p in self.preview_widgets)}
        for widget in self.findChildren(QWidget):
            if widget is self.language_box:
                continue
            if isinstance(widget, (QLabel, QPushButton, QCheckBox)) and widget not in dynamic:
                value = widget.text()
                if value:
                    self._original_texts.append((widget, "text", value))
            if isinstance(widget, (QLineEdit, QComboBox, QPushButton, QCheckBox)):
                tip = widget.toolTip()
                if tip:
                    self._original_texts.append((widget, "tooltip", tip))
            if isinstance(widget, QLineEdit):
                hint = widget.placeholderText()
                if hint:
                    self._original_texts.append((widget, "placeholder", hint))
            if isinstance(widget, QComboBox):
                for index in range(widget.count()):
                    self._original_texts.append((widget, "item", (index, widget.itemText(index))))
        for index in range(self.tabs.count()):
            self._original_texts.append((self.tabs, "tab", (index, self.tabs.tabText(index))))
        for index in range(self.table.columnCount()):
            self._original_texts.append((self.table, "column", (index, self.table.horizontalHeaderItem(index).text())))

    def change_language(self):
        language = self.language_box.currentData()
        if language not in ("ru", "en") or language == self.language:
            return
        self.language = language
        self.apply_language()
        self.apply_theme()
        self.save_settings()

    def apply_language(self):
        # Do not overwrite user-editable text, the file queue, or the chosen options.
        for widget, kind, original in self._original_texts:
            if kind == "text":
                widget.setText(self.t(original))
            elif kind == "tooltip":
                widget.setToolTip(self.t(original))
            elif kind == "placeholder":
                widget.setPlaceholderText(self.t(original))
            elif kind == "item":
                index, value = original
                widget.setItemText(index, self.t(value))
            elif kind == "tab":
                index, value = original
                widget.setTabText(index, self.t(value))
            elif kind == "column":
                index, value = original
                widget.horizontalHeaderItem(index).setText(self.t(value))
        # Editable page lists are valid as both 'all' and 'все' in the PDF engine.
        for field in (self.split_pages, self.rotate_pages):
            if field.text().strip().lower() in ("все", "all"):
                field.setText("all" if self.language == "en" else "все")
        # Localize default merge filename only; don't override custom filenames.
        if self.merge_name.text() in ("объединённый", "merged"):
            self.merge_name.setText("merged" if self.language == "en" else "объединённый")
        self.setWindowTitle(f"PDF Compressor {APP_VERSION}  •  {self.t('Локальная обработка')}")
        self.set_status(self._status_ru)
        if self._tool_feedback_state is not None:
            self.render_tool_feedback()
        self.on_mode_changed()
        old_page = self.page_number.text()
        if self.entries:
            self.refresh_table()
            self.page_number.setText(old_page)
            self.update_preview()
        else:
            self.count.setText("0 PDF")
            self.document_name.setText(self.t("Добавьте PDF, чтобы открыть его здесь"))
            self.result_metric.setText(self.t("Нет обработанных файлов"))
            self.compare_status.setText(self.t("До сжатия будет показан оригинал в полном размере области."))
            self.single_preview.clear_message(self.t("Добавьте PDF, чтобы увидеть страницу"))
            self.preview_widgets[0].clear_message(self.t("Выберите документ"))
            self.preview_widgets[1].clear_message(self.t("Результат появится после сжатия"))

    def set_status(self, text_ru: str):
        self._status_ru = str(text_ru)
        self.status.setText(self.translated(self._status_ru))

    def info(self, title: str, message: str):
        QMessageBox.information(self, self.t(title), self.translated(message))

    def warn(self, title: str, message: str):
        QMessageBox.warning(self, self.t(title), self.translated(message))

    def default_folder(self):
        return str(Path.home() / "Documents" / "PDF Compressor")

    def target_value(self):
        try:
            value = float(self.target.text().strip().replace(",", "."))
            if not 0.01 <= value <= 100000:
                raise ValueError
            return value
        except ValueError:
            raise ValueError(self.t("Укажите корректный размер PDF, например 1 или 0,5 МБ"))

    def selected_page(self):
        try:
            value = int(self.page_number.text())
        except ValueError:
            value = 1
        entry = self.selected_entry()
        return max(1, min(value, entry["pages"] if entry else 1))

    def restore_settings(self):
        folder = str(self.settings.value("folder", self.default_folder()))
        self.folder_edit.setText(folder)
        self.template.setText(str(self.settings.value("template", "{name}_сжатый")))
        saved_target = float(self.settings.value("target", 1.0))
        self.target.setText(f"{saved_target:.2f}".replace(".", ","))
        self.downscale.setChecked(str(self.settings.value("downscale", "false")).lower() == "true")
        wanted = str(self.settings.value("mode", "smartfit"))
        index = self.mode.findData(wanted)
        self.mode.setCurrentIndex(max(0, index))
        self.on_mode_changed()

    def save_settings(self):
        self.settings.setValue("folder", self.folder_edit.text().strip())
        self.settings.setValue("template", self.template.text())
        try:
            target = self.target_value()
        except ValueError:
            target = 1.0
        self.settings.setValue("target", target)
        self.settings.setValue("downscale", self.downscale.isChecked())
        self.settings.setValue("mode", self.mode.currentData())
        self.settings.setValue("dark", self.dark)
        self.settings.setValue("language", self.language)
        self.settings.sync()

    def on_mode_changed(self):
        mode = self.mode.currentData()
        active = mode in ("target", "smartfit")
        self.target.setVisible(active)
        self.target_label.setVisible(active)
        self.start_btn.setText(self.t("▶  Подготовить PDF к отправке" if mode == "smartfit"
                                      else "▶  Сжать все PDF"))
        self.update_smartfit_note()

    def update_smartfit_note(self):
        if not hasattr(self, "smartfit_note"):
            return
        active = self.mode.currentData() == "smartfit"
        self.smartfit_note.setVisible(active)
        if not active:
            return
        entry = self.selected_entry() if hasattr(self, "table") else None
        analysis = entry.get("analysis") if entry else None
        if analysis is None:
            self.smartfit_note.setText(self.t(
                "SmartFit анализирует тип PDF и подбирает сжатие. После обработки проверьте документ в предпросмотре."))
            self.smartfit_note.setToolTip("")
            return
        kinds = {"text": "Текстовый PDF", "scan": "Скан",
                 "mixed": "Смешанный PDF", "other": "Другой PDF"}
        text = f"{self.t('Тип документа:')} {self.t(kinds.get(analysis.kind, 'Другой PDF'))} · {analysis.pages} {self.t('страниц')}"
        advice = entry.get("recommendations", ())
        if advice:
            text += "\n" + self.t(advice[0])
        self.smartfit_note.setText(text)
        self.smartfit_note.setToolTip("\n".join(self.t(message) for message in advice))

    def apply_theme(self):
        if self.dark:
            bg, panel, text, muted, border, accent, input_bg, alt = (
                "#0f121a", "#1b2230", "#f4f6ff", "#a4afc5", "#344157", "#5e88fa", "#131a26", "#243044")
        else:
            bg, panel, text, muted, border, accent, input_bg, alt = (
                "#f4f6fb", "#ffffff", "#1b2535", "#64718a", "#d6dfeb", "#3b63df", "#f9fbff", "#edf2fb")
        self.theme_btn.setText(self.t("☀  Светлая тема" if self.dark else "☾  Тёмная тема"))
        # Custom card painting avoids the disconnected/bleeding corners caused
        # by QSS on native QGroupBox and table widgets.
        for card in self.findChildren(RoundedCard):
            card.set_card_colors(panel, border)
        self.setStyleSheet(f"""
            QWidget {{color:{text};font-family:'Segoe UI';font-size:13px;}}
            QMainWindow, QWidget#Central, QWidget#TabBody, QWidget#LeftPanel,
            QWidget#RightPanel, QWidget#ToolsPage {{background:{bg};}}
            QWidget#ToolsShell, QWidget#LeftContent {{background:transparent;}}
            QScrollArea#LeftScroll {{background:transparent;border:0;}}
            QScrollArea#LeftScroll > QWidget > QWidget {{background:transparent;}}
            QLabel {{background:transparent;}}
            QTabWidget::pane {{border:1px solid {border};border-radius:11px;background:{bg};}}
            QTabBar::tab {{background:transparent;color:{muted};padding:10px 20px;margin-right:5px;
                           border:0;border-bottom:2px solid transparent;}}
            QTabBar::tab:hover {{color:{text};background:{alt};}}
            QTabBar::tab:selected {{color:{text};border-bottom:3px solid {accent};font-weight:700;}}
            QLabel#Title {{font-size:22px;font-weight:700;}}
            QLabel#SectionTitle {{font-size:18px;font-weight:700;}}
            QLabel#Muted {{color:{muted};font-size:12px;}}
            QLabel#Badge {{color:{accent};font-size:12px;font-weight:700;padding:3px 7px;}}
            QLabel#AccentIcon {{color:{accent};font-size:25px;}}
            QLabel#DropTitle {{font-size:13px;font-weight:700;}}
            QLabel#CardCaption {{font-size:12px;font-weight:700;color:{muted};}}
            QLabel#ToolCardTitle {{font-size:15px;font-weight:700;color:{text};}}
            QLabel#ToolNumber {{background:{alt};border:1px solid {border};border-radius:9px;
                                color:{accent};font-size:12px;font-weight:700;}}
            QLabel#ResultMetric {{font-size:15px;font-weight:700;color:{accent};}}
            QFrame#DropArea {{background:{panel};border:1px dashed {accent};border-radius:11px;}}
            QComboBox#LanguageBox {{min-width:98px;}}
            QLineEdit,QComboBox {{background:{input_bg};color:{text};border:1px solid {border};
                                  border-radius:8px;min-height:25px;padding:2px 9px;
                                  selection-background-color:{accent};}}
            QLineEdit:hover,QComboBox:hover {{border-color:{'#61718e' if self.dark else '#aab8d2'};}}
            QLineEdit:focus,QComboBox:focus {{border:1px solid {accent};}}
            QLineEdit:disabled,QComboBox:disabled {{color:{muted};background:{alt};}}
            QComboBox::drop-down {{border:0;width:20px;}}
            QComboBox QAbstractItemView {{background:{panel};color:{text};selection-background-color:{accent};}}
            QCheckBox {{background:transparent;spacing:8px;}}
            QPushButton {{background:{alt};color:{text};border:1px solid {border};
                          border-radius:8px;padding:3px 10px;font-weight:600;min-height:26px;}}
            QPushButton#Tiny {{padding:2px;min-height:27px;font-size:18px;}}
            QPushButton:hover {{border-color:{accent};background:{'#2d3b53' if self.dark else '#e2eafb'};}}
            QPushButton:pressed {{background:{'#344c7e' if self.dark else '#d4e0fb'};}}
            QPushButton:disabled {{color:{muted};background:{panel};border-color:{border};}}
            QPushButton#Primary {{background:{accent};border:1px solid {accent};color:white;}}
            QPushButton#Primary:hover {{background:{'#779aff' if self.dark else '#2a51c6'};}}
            QPushButton#Danger {{background:#8a2949;border:1px solid #8a2949;color:white;}}
            QPushButton#Danger:disabled {{background:{alt};border-color:{border};color:{muted};}}
            QTableWidget#FileTable {{background:{panel};alternate-background-color:{alt};color:{text};
                           border:0;selection-background-color:{'#37517e' if self.dark else '#d7e4ff'};
                           selection-color:{text};outline:0;}}
            QTableWidget#FileTable::item {{padding:4px 7px;border:0;}}
            QHeaderView {{background:{panel};border:0;}}
            QHeaderView::section {{background:{alt};color:{muted};border:0;
                                  border-bottom:1px solid {border};padding:7px 7px;
                                  font-weight:700;}}
            QProgressBar {{background:{input_bg};border:1px solid {border};border-radius:7px;
                           min-height:15px;text-align:center;color:{text};}}
            QProgressBar::chunk {{background:{accent};border-radius:6px;}}
            QScrollArea#PreviewPane {{background:{input_bg};border:1px solid {border};border-radius:11px;}}
            QLabel#Preview {{background:{input_bg};color:{muted};}}
            QScrollBar:vertical {{background:transparent;width:9px;border:0;}}
            QScrollBar::handle:vertical {{background:{border};border-radius:4px;min-height:32px;}}
            QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical {{height:0;}}
            QScrollBar:horizontal {{background:transparent;height:9px;border:0;}}
            QScrollBar::handle:horizontal {{background:{border};border-radius:4px;min-width:30px;}}
            QScrollBar::add-line:horizontal,QScrollBar::sub-line:horizontal {{width:0;}}
            QSplitter::handle {{background:{border};}}
        """)

    def toggle_theme(self):
        self.dark = not self.dark
        self.apply_theme()
        self.refresh_table()
        self.save_settings()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() and any(u.toLocalFile().lower().endswith(".pdf") for u in event.mimeData().urls()):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        self.add_files([u.toLocalFile() for u in event.mimeData().urls() if u.isLocalFile()])
        event.acceptProposedAction()

    def pick_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, self.t("Добавить PDF"), "", "PDF (*.pdf)")
        self.add_files(files)

    def add_files(self, paths):
        if self.busy:
            return
        known = {e["path"].lower() for e in self.entries}
        errors = []
        for path in paths:
            if not only_pdf(path):
                continue
            absolute = str(Path(path).resolve())
            if absolute.lower() in known:
                continue
            try:
                size, pages = file_info(absolute)
                self.entries.append(dict(path=absolute, size=size, pages=pages,
                                         status="В очереди", result="", result_path=""))
                known.add(absolute.lower())
            except Exception as error:
                errors.append(f"{Path(path).name}: {error}")
        self.refresh_table()
        if self.entries and self.table.currentRow() < 0:
            self.table.selectRow(0)
        if errors:
            self.warn("Не удалось добавить PDF", "\n".join(errors[:10]))

    def refresh_table(self):
        previous = self.table.currentRow()
        self.table.blockSignals(True)
        self.table.setRowCount(len(self.entries))
        for idx, entry in enumerate(self.entries):
            summary = entry["status"]
            detail = summary + (" · " + entry["result"] if entry["result"] else "")
            values = [Path(entry["path"]).name, display_size(entry["size"], self.language), self.translated(summary)]
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setToolTip(entry["path"] if col == 0 else self.translated(detail))
                if col == 1:
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                elif col == 2:
                    item.setTextAlignment(Qt.AlignCenter)
                    if summary in ("Готово", "Инструмент: готово"):
                        item.setForeground(QBrush(QColor("#71d1a4" if self.dark else "#147a53")))
                    elif summary == "Ошибка":
                        item.setForeground(QBrush(QColor("#ff8795" if self.dark else "#b83248")))
                    elif summary == "Цель не достигнута":
                        item.setForeground(QBrush(QColor("#eac17e" if self.dark else "#99600f")))
                self.table.setItem(idx, col, item)
        if self.entries:
            self.table.selectRow(max(0, min(previous, len(self.entries) - 1)))
        self.table.blockSignals(False)
        self.count.setText(f"{len(self.entries)} PDF")
        self.on_selection_changed()

    def remove_selected(self):
        if self.busy:
            return
        idx = self.table.currentRow()
        if 0 <= idx < len(self.entries):
            del self.entries[idx]
            self.refresh_table()

    def clear_files(self):
        if self.busy:
            return
        self.entries = []
        self.selected_source = None
        self.refresh_table()
        for idx, pane in enumerate(self.preview_widgets):
            pane.clear_message("Выберите PDF" if idx == 0 else "Результат появится после сжатия")
        self.single_preview.clear_message(self.t("Добавьте PDF, чтобы увидеть страницу"))
        self.preview_stack.setCurrentIndex(0)
        self.result_metric.setText(self.t("Нет обработанных файлов"))
        self.document_name.setText(self.t("Добавьте PDF, чтобы открыть его здесь"))
        self.page_total.setText("/ 1")
        self.prev_btn.setEnabled(False)
        self.next_btn.setEnabled(False)
        self.compare_status.setText(self.t("До сжатия будет показан оригинал в полном размере области."))
        self.preview_rotation = 0

    def pick_folder(self):
        path = QFileDialog.getExistingDirectory(self, self.t("Папка для сохранения"), self.folder_edit.text())
        if path:
            self.folder_edit.setText(path)
            self.save_settings()

    def selected_entry(self):
        idx = self.table.currentRow()
        return self.entries[idx] if 0 <= idx < len(self.entries) else None

    def on_selection_changed(self):
        entry = self.selected_entry()
        if entry:
            self.selected_source = entry["path"]
            self.page_number.blockSignals(True)
            self.page_number.setValidator(QIntValidator(1, max(1, entry["pages"]), self))
            self.page_number.setText("1")
            self.page_number.blockSignals(False)
            self.update_preview()
        self.update_smartfit_note()

    def on_double_clicked(self, row, col):
        if 0 <= row < len(self.entries):
            e = self.entries[row]
            open_file(e["result_path"] or e["path"])

    def open_selected_result(self):
        entry = self.selected_entry()
        selected_path = entry["result_path"] if entry else None
        path = selected_path or self.last_created_path
        if path and Path(path).is_file():
            open_file(path)
        else:
            self.info("Результат", "Пока нет обработанного PDF.")

    def change_page(self, delta: int):
        if not self.selected_entry():
            return
        self.page_number.setText(str(max(1, self.selected_page() + delta)))
        self.update_preview()

    def rotate_preview(self):
        self.preview_rotation = (self.preview_rotation + 90) % 360
        self.update_preview()

    def get_page_pixmap(self, path: str, page_index: int) -> QPixmap:
        key = (path, page_index)
        if key not in self.preview_cache:
            with pymupdf.open(path) as pdf:
                if page_index >= len(pdf):
                    raise ValueError(self.t("В PDF нет выбранной страницы"))
                # Render previews at a bounded pixel size to keep RAM and CPU
                # usage predictable, especially on 4 GB Windows machines.
                page = pdf[page_index]
                max_dimension = max(page.rect.width, page.rect.height)
                scale = min(1.9, 1600.0 / max(1.0, max_dimension))
                pix = page.get_pixmap(matrix=pymupdf.Matrix(scale, scale),
                                      colorspace=pymupdf.csRGB, alpha=False)
                picture = QPixmap()
                if not picture.loadFromData(pix.tobytes("png"), "PNG"):
                    raise ValueError(self.t("Не удалось загрузить страницу"))
            if len(self.preview_cache) >= 6:
                self.preview_cache.clear()
            self.preview_cache[key] = picture
        picture = self.preview_cache[key]
        if self.preview_rotation:
            return picture.transformed(QTransform().rotate(self.preview_rotation),
                                       Qt.SmoothTransformation)
        return picture

    def update_preview(self):
        entry = self.selected_entry()
        if not entry:
            return
        page_index = self.selected_page() - 1
        self.page_number.setText(str(page_index + 1))
        self.page_total.setText(f"/ {entry['pages']}")
        self.prev_btn.setEnabled(page_index > 0)
        self.next_btn.setEnabled(page_index < entry["pages"] - 1)
        self.document_name.setText(Path(entry["path"]).name)
        self.document_name.setToolTip(entry["path"])
        factor = float(self.zoom.currentData() or 1.0)
        for pane in [self.single_preview, *self.preview_widgets]:
            pane.set_zoom(factor)

        result = entry.get("result_path", "")
        valid_result = bool(result and Path(result).is_file())
        mode = self.view_mode.currentData()
        comparison = (mode == "compare" or (mode == "auto" and valid_result))
        self.preview_stack.setCurrentIndex(1 if comparison else 0)

        def render(pane, path, fallback):
            if not path or not Path(path).is_file():
                pane.clear_message(self.t(fallback))
                return
            try:
                pane.set_preview(self.get_page_pixmap(path, page_index))
            except Exception as e:
                pane.clear_message(self.translated(f"Ошибка предпросмотра: {e}"))

        if comparison:
            render(self.preview_widgets[0], entry["path"], "Не найден оригинал")
            render(self.preview_widgets[1], result, "После сжатия здесь появится результат")
        else:
            show_result = mode == "result"
            render(self.single_preview, result if show_result else entry["path"],
                   "Сначала сожмите документ" if show_result else "Не найден оригинал")

        if valid_result:
            old_size = entry["size"]
            new_size = Path(result).stat().st_size
            saved = 100.0 * (old_size - new_size) / old_size if old_size else 0.0
            self.result_metric.setText(f"{display_size(old_size, self.language)}  →  {display_size(new_size, self.language)}  ·  {saved:.1f}%")
            self.compare_status.setText(self.translated(entry.get("result", "Сжатие завершено. Откройте результат, чтобы проверить качество.")))
        else:
            self.result_metric.setText(f"{self.t('Оригинал:')} {display_size(entry['size'], self.language)}")
            self.compare_status.setText(self.t("Выберите режим и нажмите «Сжать все PDF». Для скана боком используйте кнопку «Повернуть» — только для просмотра."))

    def options(self):
        folder = self.folder_edit.text().strip()
        if not folder:
            raise ValueError(self.t("Укажите папку для результата"))
        try:
            Path(folder).mkdir(parents=True, exist_ok=True)
        except OSError as error:
            raise ValueError(f"{self.t('Не удалось создать папку:')} {error}")
        target = self.target_value() if self.mode.currentData() in ("target", "smartfit") else 1.0
        self.save_settings()
        return {"folder": folder, "mode": self.mode.currentData(),
                "target": target, "downscale": self.downscale.isChecked(),
                "template": self.template.text().strip() or "{name}_сжатый"}

    def begin(self, action: str, paths: list[str], opts: dict):
        if self.busy:
            return
        self._active_action = action
        self._tool_focus_button = {
            "merge": self.merge_btn, "split": self.split_btn,
            "rotate": self.rotate_btn,
        }.get(action)
        if self._tool_focus_button is not None:
            self._tool_outputs = []
            self._tool_errors = []
            self._tool_feedback_state = None
            self.tool_result_card.hide()
        self.busy = True
        self.active_paths = list(paths)
        self.progressbar.setValue(0)
        self.cancel_btn.setEnabled(True)
        for btn in (self.start_btn, self.add_btn, self.remove_btn, self.clear_btn,
                    self.merge_btn, self.split_btn, self.rotate_btn):
            btn.setEnabled(False)
        # Disabling the clicked button makes Qt move focus to the next control.
        # Clear that transient focus; restore the originating button on finish.
        if self._tool_focus_button is not None:
            focused = QApplication.focusWidget()
            if focused is not None and self.tools_page.isAncestorOf(focused):
                focused.clearFocus()
        self.worker = JobWorker(action, paths, opts)
        self.thread = QThread(self)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.update_progress)
        self.worker.timing.connect(self.record_timing)
        self.worker.result.connect(self.record_result)
        self.worker.finished.connect(self.receive_end_message)
        self.worker.finished.connect(self.thread.quit)
        self.thread.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.finalize_thread)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def start_compression(self):
        if not self.entries:
            self.info("Файлы", "Сначала добавьте хотя бы один PDF")
            return
        try:
            opts = self.options()
        except ValueError as error:
            self.warn("Настройки", str(error))
            return
        for entry in self.entries:
            entry.update(status="В очереди", result="", result_path="", elapsed_seconds=None)
        self.refresh_table()
        self.begin("compress", [e["path"] for e in self.entries], opts)

    def current_path(self):
        entry = self.selected_entry()
        if not entry:
            self.info("Выберите PDF", "Выделите документ в таблице вкладки «Сжатие PDF».")
            return None
        return entry["path"]

    def start_merge(self):
        if len(self.entries) < 2:
            self.info("Объединение", "Добавьте минимум два PDF.")
            return
        try:
            opts = self.options()
        except ValueError as error:
            self.warn("Папка", str(error))
            return
        opts["name"] = self.merge_name.text().strip() or "объединённый"
        self.begin("merge", [e["path"] for e in self.entries], opts)

    def start_split(self):
        path = self.current_path()
        if not path:
            return
        try:
            opts = self.options()
        except ValueError as error:
            self.warn("Папка", str(error))
            return
        opts["pages"] = self.split_pages.text()
        opts["each"] = self.split_each.isChecked()
        self.begin("split", [path], opts)

    def start_rotate(self):
        path = self.current_path()
        if not path:
            return
        try:
            opts = self.options()
        except ValueError as error:
            self.warn("Папка", str(error))
            return
        opts["pages"] = self.rotate_pages.text()
        opts["degrees"] = int(self.degrees.currentData())
        self.begin("rotate", [path], opts)

    def open_tool_result_folder(self):
        state = self._tool_feedback_state
        if not state or not state["outputs"]:
            return
        folder = Path(state["outputs"][0]).parent
        if folder.is_dir():
            open_file(str(folder))
        else:
            self.warn("Папка", "Не найдена папка результата.")

    def render_tool_feedback(self):
        state = self._tool_feedback_state
        if state is None:
            self.tool_result_card.hide()
            return
        action, message = state["action"], state["message"]
        outputs, errors = state["outputs"], state["errors"]
        if errors:
            title = self.t("Ошибка операции")
            detail = self.translated(errors[0])
            can_open = False
        elif message.startswith("Операция отменена"):
            title = self.t("Операция отменена")
            detail = self.translated(message)
            can_open = False
        elif outputs and message.startswith("Готово."):
            titles = {
                "merge": "PDF успешно объединены",
                "split": "Страницы успешно извлечены",
                "rotate": "PDF успешно повёрнут",
            }
            title = self.t(titles[action])
            if len(outputs) == 1:
                detail = f"{self.t('Создан файл:')} {outputs[0]}"
            else:
                detail = (f"{self.t('Создано файлов:')} {len(outputs)}\n"
                          f"{self.t('Папка:')} {Path(outputs[0]).parent}")
            can_open = True
        else:
            title = self.t("Ошибка операции")
            detail = self.translated(message)
            can_open = False
        self.tool_result_title.setText(title)
        self.tool_result_detail.setText(detail)
        self.open_tool_folder_btn.setVisible(can_open)
        self.tool_result_card.show()

    def update_progress(self, stage: str, current: int, total: int):
        self.set_status(stage + (f"  •  страница {current}/{total}" if total > 1 else ""))
        self.progressbar.setValue(round(100 * current / max(1, total)))

    def record_timing(self, index: int, seconds: float):
        if 0 <= index < len(self.active_paths):
            source = self.active_paths[index]
            for entry in self.entries:
                if entry["path"] == source:
                    entry["elapsed_seconds"] = seconds
                    break

    def record_result(self, index: int, outcome):
        source = self.active_paths[index] if 0 <= index < len(self.active_paths) else None
        row_idx = next((i for i, e in enumerate(self.entries) if e["path"] == source), -1)
        if isinstance(outcome, Exception):
            if self._active_action in ("merge", "split", "rotate"):
                self._tool_errors.append(str(outcome))
            if row_idx >= 0:
                self.entries[row_idx]["status"] = "Ошибка"
                self.entries[row_idx]["result"] = str(outcome)
            else:
                self.warn("Ошибка операции", str(outcome))
            self.refresh_table()
            return
        if hasattr(outcome, "saving_percent"):
            if row_idx >= 0:
                e = self.entries[row_idx]
                e["status"] = "Готово" if outcome.target_met is not False else "Цель не достигнута"
                suffix = " · цель не достигнута" if outcome.target_met is False else ""
                elapsed = e.get("elapsed_seconds")
                timing_text = (f" · Время: {elapsed:.1f} с" if elapsed is not None else "")
                e["result"] = (f"{human_size(outcome.result_bytes)}  (−{outcome.saving_percent:.1f}%)"
                               f" · {outcome.description}{suffix}{timing_text}")
                e["result_path"] = outcome.output
                e["analysis"] = outcome.analysis
                e["recommendations"] = outcome.recommendations
                self.last_created_path = outcome.output
        else:
            files = outcome if isinstance(outcome, list) else [outcome]
            if self._active_action in ("merge", "split", "rotate"):
                self._tool_outputs.extend(str(path) for path in files)
            if row_idx >= 0:
                self.entries[row_idx]["status"] = "Инструмент: готово"
                self.entries[row_idx]["result"] = f"Создано файлов: {len(files)}"
                self.entries[row_idx]["result_path"] = str(files[0])
            self.last_created_path = str(files[0])
            self.set_status("Созданы: " + "; ".join(Path(p).name for p in files[:4]))
        self.refresh_table()

    def receive_end_message(self, message: str):
        self.pending_end_message = message

    def finalize_thread(self):
        message = getattr(self, "pending_end_message", "Операция завершена")
        self.set_status(message)
        self.busy = False
        self.thread = None
        self.worker = None
        self.cancel_btn.setEnabled(False)
        for btn in (self.start_btn, self.add_btn, self.remove_btn, self.clear_btn,
                    self.merge_btn, self.split_btn, self.rotate_btn):
            btn.setEnabled(True)
        self.progressbar.setValue(100 if message.startswith("Готово") else 0)
        if self._tool_focus_button is not None:
            self._tool_feedback_state = {
                "action": self._active_action, "message": message,
                "outputs": list(self._tool_outputs),
                "errors": list(self._tool_errors),
            }
            self.render_tool_feedback()
            # Preserve Tab navigation without leaving focus on the next tool.
            focused = QApplication.focusWidget()
            if (self.tabs.currentWidget() is self.tools_page and
                    (focused is None or focused in
                     (self.merge_btn, self.split_btn, self.rotate_btn))):
                self._tool_focus_button.setFocus(Qt.OtherFocusReason)
        self._tool_focus_button = None
        self._active_action = None
        self.update_preview()

    def cancel_operation(self):
        if self.worker is not None:
            self.worker.stop()
            self.set_status("Отмена запрошена. Завершается текущий этап…")
            self.cancel_btn.setEnabled(False)

    def closeEvent(self, event):
        if self.busy:
            self.info("Обработка", "Сначала нажмите «Отменить» и дождитесь завершения текущей операции.")
            event.ignore()
        else:
            self.save_settings()
            event.accept()


def run_app():
    app = QApplication(sys.argv)
    app.setApplicationName("PDF Compressor 2.7")
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 10))
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run_app()
