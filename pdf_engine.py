# -*- coding: utf-8 -*-
"""Backend for PDF Compressor 2.0. No GUI dependencies.

The original PDFs are never written to. Image replacements preserve selectable
text and vector content, but lossy JPEG recompression can affect image fidelity.
"""
from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Callable, Iterable
import math
import os
import re
import shutil
import threading

import pymupdf
from PIL import Image

Progress = Callable[[str, int, int], None]


class Cancelled(Exception):
    pass


def check_cancel(cancel: threading.Event | None) -> None:
    if cancel is not None and cancel.is_set():
        raise Cancelled("Операция отменена пользователем")


def emit(progress: Progress | None, stage: str, current: int, total: int):
    if progress:
        progress(stage, current, total)


def human_size(count: int) -> str:
    value = float(count)
    for unit in ("Б", "КБ", "МБ", "ГБ"):
        if value < 1000 or unit == "ГБ":
            return f"{value:.2f} {unit}".replace(".00", "")
        value /= 1000
    return ""


def safe_name(text: str) -> str:
    result = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", text).strip(". ")
    return result[:150] or "document"


def make_output(folder: Path, proposed_stem: str, *, reserved: set[str] | None = None) -> Path:
    """Never overwrite any existing file; also disallow same name during a batch."""
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    stem = safe_name(proposed_stem)
    candidate = folder / f"{stem}.pdf"
    index = 2
    while candidate.exists() or (reserved is not None and str(candidate).lower() in reserved):
        candidate = folder / f"{stem}_{index}.pdf"
        index += 1
    if reserved is not None:
        reserved.add(str(candidate).lower())
    return candidate


def file_info(path: str | Path) -> tuple[int, int]:
    path = Path(path)
    with pymupdf.open(path) as doc:
        if doc.needs_pass:
            raise ValueError("PDF защищён паролем")
        return (path.stat().st_size, len(doc))


def validate_doc(doc: pymupdf.Document):
    if doc.needs_pass:
        raise ValueError("PDF защищён паролем. Сначала создайте незашифрованную копию.")
    if len(doc) == 0:
        raise ValueError("В документе нет страниц")
    # A save or page operation invalidates existing cryptographic signatures.
    if doc.get_sigflags() in (1, 3):
        raise ValueError("PDF содержит поля цифровой подписи. Изменение файла может нарушить подпись; обработка заблокирована.")


def parse_pages(expression: str, page_count: int) -> list[int]:
    """Parse 1-based page selectors, keeping the requested order."""
    if page_count < 1:
        raise ValueError("Документ пуст")
    text = expression.strip().lower()
    if text in ("", "all", "все", "всё", "*"):
        return list(range(page_count))
    result: list[int] = []
    for part in re.split(r"[,;]", text):
        part = part.strip()
        m = re.fullmatch(r"(\d+)\s*-\s*(\d+)", part)
        if m:
            start, stop = (int(m.group(1)), int(m.group(2)))
            if start > stop:
                raise ValueError("Диапазон должен идти по возрастанию")
            indexes = range(start, stop + 1)
        elif part.isdigit():
            indexes = [int(part)]
        else:
            raise ValueError(f"Неверный диапазон страниц: {part!r}. Пример: 1-3,5,8")
        for page_num in indexes:
            if not 1 <= page_num <= page_count:
                raise ValueError(f"Страница {page_num} вне диапазона 1–{page_count}")
            index = page_num - 1
            if index not in result:
                result.append(index)
    if not result:
        raise ValueError("Не выбраны страницы")
    return result


@dataclass
class CompressionResult:
    source: str
    output: str
    original_bytes: int
    result_bytes: int
    description: str
    quality: int | None
    target_met: bool | None
    pages: int
    downscaled: bool

    @property
    def saving_percent(self) -> float:
        return 100 * (1 - self.result_bytes / max(1, self.original_bytes))


def _save_pdf(doc: pymupdf.Document, target: Path) -> int:
    doc.save(str(target), garbage=4, deflate=True,
             deflate_images=True, deflate_fonts=True, use_objstms=1)
    return target.stat().st_size


def _required_scaled_size(page: pymupdf.Page, xref: int, dimensions: tuple[int, int], max_dpi: int) -> tuple[int, int] | None:
    """Best safe shared-image DPI based on every occurrence on a page.

    If page geometry cannot be determined, keep full resolution.
    """
    try:
        rects = page.get_image_rects(xref)
    except Exception:
        return None
    if not rects:
        return None
    w, h = dimensions
    widths = [r.width for r in rects if r.width > 0]
    heights = [r.height for r in rects if r.height > 0]
    if not widths or not heights:
        return None
    # PDF points to inches. Largest physical usage requires most pixels.
    req_w = max(1, min(w, math.ceil(max(widths) * max_dpi / 72)))
    req_h = max(1, min(h, math.ceil(max(heights) * max_dpi / 72)))
    factor = min(1, req_w / w, req_h / h)
    if factor > 0.95:
        return None
    return max(1, round(w * factor)), max(1, round(h * factor))


def build_candidate(source: Path, target: Path, quality: int | None = None,
                    max_dpi: int | None = None, cancel: threading.Event | None = None,
                    progress: Progress | None = None) -> tuple[int, bool, int]:
    """Build one candidate, preserving pages/text; optionally recompress raster images.

    Only replaces images when JPEG bytes are smaller than the source image.
    Skips masks, alpha/transparency and tiny images to avoid corrupting them.
    """
    check_cancel(cancel)
    image_changes = 0
    downscaled = False
    with pymupdf.open(source) as doc:
        validate_doc(doc)
        handled: set[int] = set()
        page_total = len(doc)
        for page_no in range(page_total):
            check_cancel(cancel)
            page = doc[page_no]
            if quality is not None:
                for info in page.get_images(full=True):
                    check_cancel(cancel)
                    xref = int(info[0])
                    smask = int(info[1])
                    if xref in handled:
                        continue
                    handled.add(xref)
                    if smask:
                        continue
                    try:
                        image_dict = doc.extract_image(xref)
                        if not image_dict or image_dict.get("smask", 0):
                            continue
                        raw = image_dict["image"]
                        with Image.open(BytesIO(raw)) as image:
                            image.load()
                            # Avoid transparent and CMYK images, line art, and small icons.
                            if image.mode not in ("RGB", "L"):
                                continue
                            if min(image.size) < 130:
                                continue
                            resized = None
                            if max_dpi is not None:
                                resized = _required_scaled_size(page, xref, image.size, max_dpi)
                                if resized:
                                    image = image.resize(resized, Image.Resampling.LANCZOS)
                            out = BytesIO()
                            # 4:4:4 avoids extra blur in colored text/seals.
                            image.save(out, "JPEG", quality=quality, optimize=True, subsampling=0)
                            jpeg = out.getvalue()
                        if len(jpeg) >= len(raw):
                            continue
                        page.replace_image(xref, stream=jpeg)
                        image_changes += 1
                        if resized:
                            downscaled = True
                    except (ValueError, OSError, RuntimeError):
                        # Unknown compression/unsupported image: leave intact.
                        continue
            emit(progress, "Обработка страниц", page_no + 1, page_total)
        check_cancel(cancel)
        result_size = _save_pdf(doc, target)
    return result_size, downscaled, image_changes


def compress_pdf(source: str | Path, out_folder: str | Path, mode: str = "target",
                 target_mb: float = 1.0, allow_downscale: bool = False,
                 name_template: str = "{name}_сжатый",
                 reserved: set[str] | None = None,
                 cancel: threading.Event | None = None,
                 progress: Progress | None = None) -> CompressionResult:
    """Compress without ever rewriting source or prematurely overwriting output.

    Modes: quality (95), balanced (85), smallest (48), target (binary search).
    """
    source = Path(source).resolve()
    if not source.is_file() or source.suffix.lower() != ".pdf":
        raise ValueError("Укажите существующий PDF-файл")
    if not (0.01 <= target_mb <= 100000):
        raise ValueError("Целевой размер должен быть от 0,01 до 100000 МБ")
    if mode not in ("target", "quality", "balanced", "smallest"):
        raise ValueError("Неизвестный режим сжатия")
    original_size = source.stat().st_size
    target_bytes = int(target_mb * 1_000_000)
    proposed = name_template.replace("{name}", source.stem)
    output = make_output(Path(out_folder), proposed, reserved=reserved)
    with TemporaryDirectory(prefix="pdfcomp2_") as tmp:
        temp = Path(tmp)
        baseline = temp / "lossless.pdf"
        emit(progress, "Проверка и оптимизация без потерь", 0, 1)
        baseline_size, _, _ = build_candidate(source, baseline, cancel=cancel, progress=progress)
        check_cancel(cancel)
        # Keep source as default if baseline increases file size.
        best_path = baseline if baseline_size < original_size else source
        best_size = min(baseline_size, original_size)
        desc = "Оптимизация без потерь" if best_path == baseline else "Без изменений (файл уже оптимизирован)"
        best_quality: int | None = None
        best_downscale = False
        fitted = mode == "target" and best_size <= target_bytes
        if mode == "target" and fitted:
            emit(progress, "Цель достигнута без потерь изображения", 1, 1)
        else:
            quality_values = {"quality": 95, "balanced": 85, "smallest": 48}
            # In target mode try full resolution first. Downscaling is an explicit opt-in.
            stages: list[int | None] = [None]
            if mode == "target" and allow_downscale:
                stages.extend([220, 180, 150, 120])
            elif mode == "smallest" and allow_downscale:
                stages = [150]
            fitted = False
            for dpi_stage in stages:
                check_cancel(cancel)
                attempts: list[int] = []
                if mode == "target":
                    low, high = 30, 97
                    while low <= high:
                        q = (low + high) // 2
                        attempts.append(q)
                        emit(progress, f"Подбор качества {q}%" + (f", до {dpi_stage} DPI" if dpi_stage else ""), 0, 1)
                        candidate = temp / "candidate.pdf"
                        size, scaled, changed = build_candidate(source, candidate, quality=q,
                                                              max_dpi=dpi_stage, cancel=cancel,
                                                              progress=progress)
                        check_cancel(cancel)
                        if size <= target_bytes:
                            # With target met, retain highest-quality candidate of this DPI stage.
                            if not fitted or q > (best_quality or 0):
                                best_path = temp / "chosen.pdf"
                                shutil.copyfile(candidate, best_path)
                                best_size = size
                                best_quality = q
                                best_downscale = scaled
                                desc = f"JPEG {q}%" + (f", до {dpi_stage} DPI" if scaled else ", исходное разрешение")
                            fitted = True
                            low = q + 1
                        else:
                            if not fitted and size < best_size:
                                best_path = temp / "chosen.pdf"
                                shutil.copyfile(candidate, best_path)
                                best_size = size
                                best_quality = q
                                best_downscale = scaled
                                desc = f"JPEG {q}%" + (f", до {dpi_stage} DPI" if scaled else ", исходное разрешение")
                            high = q - 1
                    if fitted:
                        break
                else:
                    q = quality_values[mode]
                    candidate = temp / "candidate.pdf"
                    emit(progress, f"JPEG {q}%" + (f", до {dpi_stage} DPI" if dpi_stage else ""), 0, 1)
                    size, scaled, changed = build_candidate(source, candidate, quality=q,
                                                          max_dpi=dpi_stage, cancel=cancel,
                                                          progress=progress)
                    if size < best_size:
                        best_path = candidate
                        best_size = size
                        best_quality = q
                        best_downscale = scaled
                        desc = f"JPEG {q}%" + (f", до {dpi_stage} DPI" if scaled else ", исходное разрешение")
                if mode != "target":
                    break
        check_cancel(cancel)
        shutil.copyfile(best_path, output)
    # Validate the newly written file and its page count after the source is closed.
    try:
        original_info = file_info(source)
        result_info = file_info(output)
        if original_info[1] != result_info[1]:
            raise RuntimeError("Число страниц изменилось после сжатия")
        return CompressionResult(
            str(source), str(output), original_size, result_info[0], desc,
            best_quality, (best_size <= target_bytes if mode == "target" else None),
            original_info[1], best_downscale
        )
    except Exception:
        output.unlink(missing_ok=True)
        raise


def merge_pdfs(inputs: Iterable[str | Path], out_folder: str | Path, name: str = "объединённый",
               cancel: threading.Event | None = None, progress: Progress | None = None) -> Path:
    sources = [Path(s).resolve() for s in inputs]
    if len(sources) < 2:
        raise ValueError("Для объединения нужно минимум два PDF")
    output = make_output(Path(out_folder), name)
    with TemporaryDirectory(prefix="pdfmerge2_") as work:
        tmp = Path(work) / "merged.pdf"
        with pymupdf.open() as result:
            for i, source in enumerate(sources):
                check_cancel(cancel)
                with pymupdf.open(source) as part:
                    validate_doc(part)
                    result.insert_pdf(part, links=True, annots=True)
                emit(progress, "Объединение файлов", i + 1, len(sources))
            check_cancel(cancel)
            _save_pdf(result, tmp)
        check_cancel(cancel)
        shutil.copyfile(tmp, output)
    return output


def split_pdf(source: str | Path, out_folder: str | Path, pages: str = "все",
              each_page: bool = False, cancel: threading.Event | None = None,
              progress: Progress | None = None) -> list[Path]:
    source = Path(source).resolve()
    outputs: list[Path] = []
    with pymupdf.open(source) as doc:
        validate_doc(doc)
        selected = parse_pages(pages, len(doc))
        segments = [[p] for p in selected] if each_page else [selected]
        reserved: set[str] = set()
        try:
            for i, segment in enumerate(segments):
                check_cancel(cancel)
                stem = f"{source.stem}_стр_{segment[0] + 1}" if each_page else f"{source.stem}_страницы"
                dest = make_output(Path(out_folder), stem, reserved=reserved)
                with pymupdf.open() as part:
                    for pno in segment:
                        check_cancel(cancel)
                        part.insert_pdf(doc, from_page=pno, to_page=pno, links=False, annots=True)
                    _save_pdf(part, dest)
                outputs.append(dest)
                emit(progress, "Извлечение страниц", i + 1, len(segments))
            return outputs
        except Exception:
            for output in outputs:
                output.unlink(missing_ok=True)
            raise


def rotate_pdf(source: str | Path, out_folder: str | Path, degrees: int = 90, pages: str = "все",
               cancel: threading.Event | None = None, progress: Progress | None = None) -> Path:
    source = Path(source).resolve()
    if degrees not in (90, 180, 270):
        raise ValueError("Допустимый поворот: 90, 180 или 270 градусов")
    with pymupdf.open(source) as doc:
        validate_doc(doc)
        indexes = parse_pages(pages, len(doc))
        for i, index in enumerate(indexes):
            check_cancel(cancel)
            page = doc[index]
            page.set_rotation((page.rotation + degrees) % 360)
            emit(progress, "Поворот страниц", i + 1, len(indexes))
        check_cancel(cancel)
        output = make_output(Path(out_folder), f"{source.stem}_поворот_{degrees}")
        _save_pdf(doc, output)
    return output
