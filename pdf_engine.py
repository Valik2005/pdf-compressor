# -*- coding: utf-8 -*-
"""Backend for PDF Compressor 2.7 SmartFit. No GUI dependencies.

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
    seen: set[int] = set()
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
            if index not in seen:
                seen.add(index)
                result.append(index)
    if not result:
        raise ValueError("Не выбраны страницы")
    return result


@dataclass(frozen=True)
class PdfAnalysis:
    """Fast structural triage, NOT a guarantee of visual readability."""
    source: str
    pages: int
    source_bytes: int
    kind: str  # text, scan, mixed, other
    text_pages: int
    image_pages: int
    scan_pages: int
    mixed_pages: int
    raster_images: int


def analyze_pdf(source: str | Path, cancel: threading.Event | None = None,
                progress: Progress | None = None) -> PdfAnalysis:
    """Classify document using text and image placement without rendering pages.

    The classification is a heuristic. A page with an image covering at least
    half the page and no selectable text is considered a scan. This deliberately
    avoids loading full-resolution bitmaps into RAM during analysis.
    """
    source = Path(source).resolve()
    if not source.is_file() or source.suffix.lower() != ".pdf":
        raise ValueError("Укажите существующий PDF-файл")
    text_pages = image_pages = scan_pages = mixed_pages = 0
    unique_images: set[int] = set()
    with pymupdf.open(source) as doc:
        validate_doc(doc)
        total = len(doc)
        for index, page in enumerate(doc):
            check_cancel(cancel)
            has_text = bool(page.get_text("text").strip())
            image_info = page.get_image_info(hashes=False, xrefs=False)
            has_image = bool(image_info)
            if has_text:
                text_pages += 1
            if has_image:
                image_pages += 1
            coverage = 0.0
            page_area = page.rect.get_area()
            if has_image and page_area > 0:
                # Overlapping images may double-count; clamp to 1.0.
                for image in image_info:
                    coverage += (pymupdf.Rect(image["bbox"]) & page.rect).get_area() / page_area
                coverage = min(1.0, coverage)
            if has_image and not has_text and coverage >= 0.50:
                scan_pages += 1
            if has_text and has_image and coverage >= 0.12:
                mixed_pages += 1
            for item in page.get_images(full=True):
                unique_images.add(int(item[0]))
            emit(progress, "Анализ документа", index + 1, total)
    if text_pages and (scan_pages or mixed_pages >= max(1, text_pages // 2)):
        kind = "mixed"
    elif text_pages:
        kind = "text"
    elif image_pages:
        kind = "scan"
    else:
        kind = "other"
    return PdfAnalysis(str(source), total, source.stat().st_size, kind,
                       text_pages, image_pages, scan_pages, mixed_pages, len(unique_images))


def smartfit_recommendations(analysis: PdfAnalysis, target_met: bool,
                             allow_downscale: bool) -> tuple[str, ...]:
    """Actionable, conservative advice; not a quality certification."""
    notes: list[str] = []
    if target_met:
        notes.append("Размер достигнут. Просмотрите страницы перед отправкой.")
    elif analysis.raster_images == 0:
        notes.append("В PDF почти нет встроенных изображений: сжатие может не помочь.")
    elif not allow_downscale:
        notes.append("Размер не достигнут. Можно разрешить уменьшение разрешения изображений.")
    else:
        notes.append("Размер не достигнут без более сильной потери качества. Увеличьте лимит.")
    if analysis.kind == "scan":
        notes.append("Документ похож на скан: проверьте мелкий текст и печати.")
    elif analysis.kind == "mixed":
        notes.append("Смешанный PDF: проверьте изображения и мелкие детали.")
    return tuple(notes)


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
    analysis: PdfAnalysis | None = None
    recommendations: tuple[str, ...] = ()
    candidates_tried: int = 0

    @property
    def saving_percent(self) -> float:
        return 100 * (1 - self.result_bytes / max(1, self.original_bytes))


def _save_pdf(doc: pymupdf.Document, target: Path) -> int:
    doc.save(str(target), garbage=4, deflate=True,
             deflate_images=True, deflate_fonts=True, use_objstms=1)
    return target.stat().st_size


def _all_image_placements(doc: pymupdf.Document, cancel: threading.Event | None = None
                          ) -> dict[int, tuple[float, float] | None]:
    """Find the largest occurrence of every image across ALL PDF pages.

    Images are shared by xref: resizing based on their first occurrence can
    destroy quality where the same image is drawn larger on a later page.
    Unknown placement means the image must NOT be downscaled.
    """
    sizes: dict[int, tuple[float, float] | None] = {}
    for page in doc:
        check_cancel(cancel)
        for item in page.get_images(full=True):
            xref = int(item[0])
            try:
                rects = page.get_image_rects(xref)
            except Exception:
                sizes[xref] = None
                continue
            if not rects:
                sizes[xref] = None
                continue
            if xref in sizes and sizes[xref] is None:
                continue
            width = max((r.width for r in rects), default=0.0)
            height = max((r.height for r in rects), default=0.0)
            if width <= 0 or height <= 0:
                sizes[xref] = None
                continue
            current = sizes.get(xref, (0.0, 0.0))
            if current is not None:
                sizes[xref] = max(current[0], width), max(current[1], height)
    return sizes


def _required_scaled_size(placements: dict[int, tuple[float, float] | None], xref: int,
                          dimensions: tuple[int, int], max_dpi: int) -> tuple[int, int] | None:
    """Conservative downscale based on the largest use of the shared image."""
    usage = placements.get(xref)
    if not usage:
        return None
    w, h = dimensions
    req_w = max(1, min(w, math.ceil(usage[0] * max_dpi / 72)))
    req_h = max(1, min(h, math.ceil(usage[1] * max_dpi / 72)))
    # Keep at least the requested DPI on BOTH axes. The smaller ratio
    # would undersample a stretched or rotated placement on the other axis.
    factor = min(1.0, max(req_w / w, req_h / h))
    if factor > 0.95:
        return None
    # Rounding to nearest can drop a pixel below the requested DPI.
    return max(1, math.ceil(w * factor)), max(1, math.ceil(h * factor))


def _useful_dpi_stages(source: Path, dpi_stages: list[int],
                       cancel: threading.Event | None = None,
                       placements: dict[int, tuple[float, float] | None] | None = None) -> set[int]:
    """Only consider DPI stages that can actually resize an embedded image.

    This preflight reads image dimensions and their largest page placements,
    without decoding image pixel data. False positives are harmless; a false
    negative would skip a useful stage, so use the same scaling rule as the
    actual candidate builder.
    """
    if not dpi_stages:
        return set()
    with pymupdf.open(source) as doc:
        if placements is None:
            placements = _all_image_placements(doc, cancel)
        images: dict[int, tuple[int, int]] = {}
        for page in doc:
            check_cancel(cancel)
            for info in page.get_images(full=True):
                xref, smask, width, height = map(int, info[:4])
                if xref not in images and not smask and min(width, height) >= 130:
                    images[xref] = (width, height)
        return {
            dpi for dpi in dpi_stages
            if any(_required_scaled_size(placements, xref, dimensions, dpi) is not None
                   for xref, dimensions in images.items())
        }


def build_candidate(source: Path, target: Path, quality: int | None = None,
                    max_dpi: int | None = None, cancel: threading.Event | None = None,
                    progress: Progress | None = None,
                    image_placements: dict[int, tuple[float, float] | None] | None = None
                    ) -> tuple[int, bool, int]:
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
        # Calculate placement across the document, not just the first page.
        placements = (image_placements if image_placements is not None
                      else _all_image_placements(doc, cancel)) if max_dpi is not None else {}
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
                                resized = _required_scaled_size(placements, xref, image.size, max_dpi)
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

    Modes: quality, balanced, smallest, target, smartfit (conservative target).
    SmartFit classifies pages without rasterizing them and selects quality limits
    appropriate for scans, digital text and mixed PDFs. It cannot certify that
    every visual detail survives compression; previews remain essential.
    """
    source = Path(source).resolve()
    if not source.is_file() or source.suffix.lower() != ".pdf":
        raise ValueError("Укажите существующий PDF-файл")
    if not (0.01 <= target_mb <= 100000):
        raise ValueError("Целевой размер должен быть от 0,01 до 100000 МБ")
    if mode not in ("target", "smartfit", "quality", "balanced", "smallest"):
        raise ValueError("Неизвестный режим сжатия")
    original_size = source.stat().st_size
    smartfit = mode == "smartfit"
    target_mode = mode in ("target", "smartfit")
    analysis = None
    if smartfit:
        emit(progress, "Анализ документа", 0, 1)
        analysis = analyze_pdf(source, cancel=cancel, progress=progress)
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
        candidates_tried = 0
        fitted = target_mode and best_size <= target_bytes
        if target_mode and fitted:
            emit(progress, "Цель достигнута без потерь изображения", 1, 1)
        else:
            quality_values = {"quality": 95, "balanced": 85, "smallest": 48}
            # In target mode try full resolution first. Downscaling is an explicit opt-in.
            stages: list[int | None] = [None]
            if target_mode and allow_downscale:
                stages.extend([220, 180, 150, 120] if not smartfit else [220, 180, 150])
            elif mode == "smallest" and allow_downscale:
                stages = [150]
            # A text-only PDF has no raster images that JPEG settings could help.
            if smartfit and analysis is not None and analysis.raster_images == 0:
                stages = []
            fitted = False
            useful_dpi_stages: set[int] | None = None
            image_placements: dict[int, tuple[float, float] | None] | None = None
            for dpi_stage in stages:
                check_cancel(cancel)
                if target_mode and dpi_stage is not None:
                    # Only calculate after full-resolution attempts have failed.
                    if useful_dpi_stages is None:
                        # The same placements are needed for every JPEG-quality
                        # trial. Compute them once instead of rescanning all pages.
                        with pymupdf.open(source) as placement_doc:
                            image_placements = _all_image_placements(placement_doc, cancel)
                        useful_dpi_stages = _useful_dpi_stages(
                            source, [stage for stage in stages if stage is not None],
                            cancel, placements=image_placements
                        )
                    if dpi_stage not in useful_dpi_stages:
                        continue
                attempts: list[int] = []
                if target_mode:
                    floors = {"scan": 55, "mixed": 62, "text": 72, "other": 65}
                    low = floors[analysis.kind] if smartfit and analysis else 30
                    high = 97
                    stage_best_quality = None
                    first_trial = True
                    probe_floor = False
                    while low <= high:
                        # If the first (midpoint) trial is too large, check the
                        # minimum permitted quality immediately. When even that
                        # cannot meet the target, more JPEG trials at this DPI
                        # only waste time. Otherwise resume normal binary search.
                        q = low if probe_floor else (low + high) // 2
                        checking_floor = probe_floor
                        probe_floor = False
                        attempts.append(q)
                        emit(progress, f"Подбор качества {q}%" + (f", до {dpi_stage} DPI" if dpi_stage else ""), 0, 1)
                        candidate = temp / "candidate.pdf"
                        size, scaled, changed = build_candidate(source, candidate, quality=q,
                                                              max_dpi=dpi_stage, cancel=cancel,
                                                              progress=progress,
                                                              image_placements=image_placements)
                        candidates_tried += 1
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
                            stage_best_quality = q if stage_best_quality is None else max(q, stage_best_quality)
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
                            if first_trial and q > low:
                                probe_floor = True
                            elif checking_floor and stage_best_quality is None:
                                # No quality in the allowed range can normally
                                # beat the floor; move to the next DPI stage.
                                break
                        first_trial = False
                    if smartfit and stage_best_quality is not None:
                        # JPEG size is not always strictly monotone. Check two
                        # nearby higher-quality values before settling.
                        for q in (stage_best_quality + 1, stage_best_quality + 2):
                            if q > 97:
                                continue
                            check_cancel(cancel)
                            size, scaled, _ = build_candidate(source, candidate, quality=q,
                                                              max_dpi=dpi_stage, cancel=cancel,
                                                              progress=progress,
                                                              image_placements=image_placements)
                            candidates_tried += 1
                            if size <= target_bytes and (best_quality is None or q > best_quality):
                                best_path = temp / "chosen.pdf"
                                shutil.copyfile(candidate, best_path)
                                best_size = size
                                best_quality = q
                                best_downscale = scaled
                                desc = f"JPEG {q}%" + (f", до {dpi_stage} DPI" if scaled else ", исходное разрешение")
                    if fitted:
                        break
                else:
                    q = quality_values[mode]
                    candidate = temp / "candidate.pdf"
                    emit(progress, f"JPEG {q}%" + (f", до {dpi_stage} DPI" if dpi_stage else ""), 0, 1)
                    size, scaled, changed = build_candidate(source, candidate, quality=q,
                                                          max_dpi=dpi_stage, cancel=cancel,
                                                          progress=progress)
                    candidates_tried += 1
                    if size < best_size:
                        best_path = candidate
                        best_size = size
                        best_quality = q
                        best_downscale = scaled
                        desc = f"JPEG {q}%" + (f", до {dpi_stage} DPI" if scaled else ", исходное разрешение")
                if not target_mode:
                    break
        check_cancel(cancel)
        # Copy while temporary candidates still exist. Remove a partial output
        # if copying fails or cancellation arrives during the final copy.
        try:
            shutil.copyfile(best_path, output)
            check_cancel(cancel)
        except Exception:
            output.unlink(missing_ok=True)
            raise
    # Validate the output after temporary candidates are closed.
    try:
        original_info = file_info(source)
        result_info = file_info(output)
        if original_info[1] != result_info[1]:
            raise RuntimeError("Число страниц изменилось после сжатия")
        # SmartFit must not silently lose selectable text during image replacement.
        # Compare extracted text page by page, without rendering raster pages.
        if smartfit and analysis is not None and analysis.text_pages:
            with pymupdf.open(source) as before, pymupdf.open(output) as after:
                for page_index in range(len(before)):
                    check_cancel(cancel)
                    if before[page_index].get_text("text") != after[page_index].get_text("text"):
                        raise RuntimeError(
                            f"Извлекаемый текст изменился на странице {page_index + 1}"
                        )
        target_met = result_info[0] <= target_bytes if target_mode else None
        notes = (smartfit_recommendations(analysis, target_met, allow_downscale)
                 if smartfit and analysis else ())
        return CompressionResult(
            str(source), str(output), original_size, result_info[0], desc,
            best_quality, target_met, original_info[1], best_downscale,
            analysis, notes, candidates_tried
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
    try:
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
            check_cancel(cancel)
        return output
    except Exception:
        # The final copy can fail after creating an incomplete destination.
        output.unlink(missing_ok=True)
        raise


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
                try:
                    with pymupdf.open() as part:
                        for pno in segment:
                            check_cancel(cancel)
                            part.insert_pdf(doc, from_page=pno, to_page=pno, links=False, annots=True)
                        _save_pdf(part, dest)
                    check_cancel(cancel)
                except Exception:
                    # The current PDF may be only partly written and is not
                    # yet present in the completed-output list.
                    dest.unlink(missing_ok=True)
                    raise
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
        try:
            _save_pdf(doc, output)
            check_cancel(cancel)
        except Exception:
            output.unlink(missing_ok=True)
            raise
    return output
