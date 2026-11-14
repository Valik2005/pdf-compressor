# -*- coding: utf-8 -*-
"""PDF Compressor 2.8: bounded, offline quality review for original vs output.

This is a *diagnostic*, not a certificate of visual equivalence. All pages
are checked for geometry and extractable-text integrity; only a deterministic
subset is rendered at thumbnail resolution to keep RAM/CPU under control.
The module does not alter either PDF and uses no network or OCR.
"""
from __future__ import annotations

import argparse
import html
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import threading
from typing import Callable, Literal

import pymupdf
from PIL import Image, ImageChops, ImageStat

from pdf_engine import check_cancel

Severity = Literal["error", "warning"]
Progress = Callable[[str, int, int], None]

DEFAULT_RENDER_PAGES = 8
DEFAULT_MAX_EDGE = 320
MAX_RENDER_PAGES = 32
MAX_REPORTED_ISSUES = 80


@dataclass(frozen=True)
class QualityIssue:
    severity: Severity
    code: str
    page: int | None  # 1-based original page, or None for document-wide issue
    message: str


@dataclass(frozen=True)
class PageVisualCheck:
    page: int  # 1-based
    mean_difference: float  # normalized 0..1, mean RGB absolute pixel error
    changed_fraction: float  # fraction of pixels differing by more than 32/255
    before_ink_fraction: float
    after_ink_fraction: float


@dataclass
class QualityReport:
    source: str
    result: str
    source_bytes: int
    result_bytes: int
    source_pages: int
    result_pages: int
    text_checked_pages: int
    rendered_pages: tuple[int, ...]
    issues: list[QualityIssue]
    visual_checks: list[PageVisualCheck]
    suppressed_issues: int = 0
    suppressed_errors: int = 0
    raster_only_pages: int = 0
    jpeg_quality_hint: int | None = None
    images_downscaled_hint: bool = False

    @property
    def status(self) -> str:
        if self.suppressed_errors or any(issue.severity == "error" for issue in self.issues):
            return "error"
        if any(issue.severity == "warning" for issue in self.issues):
            return "review"
        # This is NOT a visual-quality certification: diagnostics are sampled.
        return "no_issues_detected"

    def as_dict(self) -> dict:
        return {"schema_version": 1, **asdict(self), "status": self.status,
                "note": ("Heuristic diagnostic only. Exact selectable text and "
                         "page geometry are checked on each matched page. Visual "
                         "differences are sampled at low resolution; unrendered "
                         "pages, tiny text and fine print require manual review.")}


def _add_issue(report: QualityReport, severity: Severity, code: str,
               page: int | None, message: str) -> None:
    if len(report.issues) < MAX_REPORTED_ISSUES:
        report.issues.append(QualityIssue(severity, code, page, message))
    else:
        report.suppressed_issues += 1
        if severity == "error":
            report.suppressed_errors += 1


def _sample_indexes(total: int, limit: int) -> tuple[int, ...]:
    """Evenly include first and last pages without choosing random state."""
    if total <= 0 or limit <= 0:
        return ()
    if limit == 1:
        return (0,)
    if total <= limit:
        return tuple(range(total))
    return tuple(round(index * (total - 1) / (limit - 1))
                 for index in range(limit))


def _thumbnail(page: pymupdf.Page, max_edge: int) -> Image.Image:
    """Render at <= max_edge per dimension, not at the source image DPI."""
    max_dimension = max(page.rect.width, page.rect.height)
    if not 0 < max_dimension:
        raise ValueError("Invalid zero-size PDF page")
    scale = min(1.0, max_edge / max_dimension)
    pixmap = page.get_pixmap(
        matrix=pymupdf.Matrix(scale, scale),
        colorspace=pymupdf.csRGB,
        alpha=False,
        annots=True,
    )
    if pixmap.width > max_edge + 2 or pixmap.height > max_edge + 2:
        raise ValueError("Rendering exceeded expected bounded thumbnail dimensions")
    return Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)


def _ink_fraction(image: Image.Image) -> float:
    histogram = image.convert("L").histogram()
    # 'Ink' includes drawings and images, not just selectable text.
    return sum(histogram[:221]) / max(1, image.width * image.height)


def _visual_difference(before: Image.Image, after: Image.Image,
                       page_number: int) -> PageVisualCheck:
    if after.size != before.size:
        # Keep the scan stable under minor PDF page dimension rounding.
        after = after.resize(before.size, Image.Resampling.BILINEAR)
    delta = ImageChops.difference(before, after)
    # Compare RGB rather than grayscale alone: drastic hue changes can
    # preserve grayscale luminance and must still be reported.
    difference = sum(ImageStat.Stat(delta).mean) / (3 * 255)
    channels = delta.split()
    max_channel_difference = ImageChops.lighter(
        ImageChops.lighter(channels[0], channels[1]), channels[2]
    )
    histogram = max_channel_difference.histogram()
    changed = sum(histogram[33:]) / max(1, before.width * before.height)
    return PageVisualCheck(
        page_number, round(difference, 6), round(changed, 6),
        round(_ink_fraction(before), 6),
        round(_ink_fraction(after), 6),
    )


def audit_pdf(source: str | Path, result: str | Path, *,
              max_render_pages: int = DEFAULT_RENDER_PAGES,
              max_thumbnail_edge: int = DEFAULT_MAX_EDGE,
              jpeg_quality_hint: int | None = None,
              images_downscaled_hint: bool = False,
              cancel: threading.Event | None = None,
              progress: Progress | None = None) -> QualityReport:
    """Check document integrity and sample visual changes after compression.

    * Page count, page geometry, rotation and selectable text: every paired page.
    * Pixel analysis: evenly spaced preview thumbnails, at most 32 by default.
    * Raster-only changed pages warrant human review: thumbnail statistics
      cannot determine whether tiny scanned text, seals or signatures survive.
    * Compression hints, when supplied, help identify risks that pixel
      thumbnails miss (e.g. JPEG 27 or downscaled images).
    * No OCR, no source writes, and no permanent preview images.
    """
    if isinstance(max_render_pages, bool) or not isinstance(max_render_pages, int):
        raise ValueError("max_render_pages must be an integer")
    if not 0 <= max_render_pages <= MAX_RENDER_PAGES:
        raise ValueError(f"max_render_pages must be 0..{MAX_RENDER_PAGES}")
    if isinstance(max_thumbnail_edge, bool) or not isinstance(max_thumbnail_edge, int):
        raise ValueError("max_thumbnail_edge must be an integer")
    if not 96 <= max_thumbnail_edge <= 640:
        raise ValueError("max_thumbnail_edge must be 96..640")
    if (jpeg_quality_hint is not None and
            (isinstance(jpeg_quality_hint, bool)
             or not isinstance(jpeg_quality_hint, int)
             or not 1 <= jpeg_quality_hint <= 100)):
        raise ValueError("jpeg_quality_hint must be 1..100 or None")
    if not isinstance(images_downscaled_hint, bool):
        raise ValueError("images_downscaled_hint must be boolean")

    before_path, after_path = Path(source).resolve(), Path(result).resolve()
    for path in (before_path, after_path):
        if not path.is_file():
            raise FileNotFoundError(str(path))
        if path.suffix.lower() != ".pdf":
            raise ValueError(f"Only PDF files can be audited: {path}")

    check_cancel(cancel)
    with pymupdf.open(before_path) as before, pymupdf.open(after_path) as after:
        if before.needs_pass or after.needs_pass:
            raise ValueError("Encrypted PDFs require decryption before quality review")
        original_pages, output_pages = len(before), len(after)
        total = min(original_pages, output_pages)
        sampled = _sample_indexes(total, max_render_pages)
        report = QualityReport(
            str(before_path), str(after_path),
            before_path.stat().st_size, after_path.stat().st_size,
            original_pages, output_pages, 0,
            tuple(index + 1 for index in sampled), [], [],
            jpeg_quality_hint=jpeg_quality_hint,
            images_downscaled_hint=images_downscaled_hint,
        )
        if original_pages != output_pages:
            _add_issue(report, "error", "page_count_changed", None,
                       f"Page count changed: {original_pages} → {output_pages}.")
        if total == 0:
            _add_issue(report, "error", "empty_document", None,
                       "One or both PDFs have no pages.")
        if max_render_pages == 0 and total:
            _add_issue(report, "warning", "visual_check_disabled", None,
                       "Visual sampling disabled; no page pixels were compared.")

        indexes_to_render = set(sampled)
        raster_changed_page: int | None = None
        raster_sampled_pages = 0
        image_pages = 0
        for index in range(total):
            check_cancel(cancel)
            page_no = index + 1
            src, dst = before[index], after[index]
            if (abs(src.rect.width - dst.rect.width) > 0.5 or
                    abs(src.rect.height - dst.rect.height) > 0.5 or
                    src.rotation != dst.rotation):
                _add_issue(report, "error", "page_geometry_changed", page_no,
                           "Page dimensions or rotation changed.")

            text_before, text_after = src.get_text("text"), dst.get_text("text")
            # Metadata-only: do not decode the full page images to classify
            # raster-only pages. Their "text" may be pixels, invisible to
            # normal selectable-text comparison and to low-res thumbnails.
            contains_raster = bool(src.get_images(full=True))
            if contains_raster:
                image_pages += 1
                if not text_before.strip():
                    report.raster_only_pages += 1
            report.text_checked_pages += 1
            if text_before != text_after:
                code = "selectable_text_lost" if text_before.strip() and not text_after.strip() \
                    else "selectable_text_changed"
                _add_issue(report, "error", code, page_no,
                           "Selectable text disappeared or changed; inspect original and result.")

            if index in indexes_to_render:
                if contains_raster and not text_before.strip():
                    raster_sampled_pages += 1
                image_before = _thumbnail(src, max_thumbnail_edge)
                image_after = _thumbnail(dst, max_thumbnail_edge)
                metrics = _visual_difference(image_before, image_after, page_no)
                report.visual_checks.append(metrics)
                if (contains_raster and not text_before.strip()
                        and metrics.mean_difference > 0.002
                        and raster_changed_page is None):
                    raster_changed_page = page_no
                if metrics.before_ink_fraction >= 0.015 and metrics.after_ink_fraction < 0.002:
                    _add_issue(report, "error", "possibly_blank_output", page_no,
                               "Page had visible content but now appears almost blank.")
                elif metrics.mean_difference >= 0.20:
                    _add_issue(report, "warning", "major_visual_difference", page_no,
                               "Large visual difference in preview; inspect scanned text and fine detail.")
                elif (metrics.mean_difference >= 0.08 and
                      metrics.changed_fraction >= 0.25):
                    _add_issue(report, "warning", "visual_difference", page_no,
                               "Substantial rendered difference; manual review recommended.")

            if progress is not None:
                progress("Проверка качества", page_no, total)

        # One informational warning per document, not per scanned page.
        # The user's real 2.7.1 test pack showed 256px thumbnail RGB MAE
        # around 0.005 on JPEG-compressed scans, even when small text became
        # visibly softer: structural + preview checks alone are insufficient.
        if raster_changed_page is not None:
            _add_issue(
                report, "warning", "raster_detail_needs_review",
                raster_changed_page,
                "A raster-only page changed after compression. Its small "
                "printed characters, stamps and signatures cannot be "
                "verified without OCR or zoomed manual inspection.")
        if (report.raster_only_pages > raster_sampled_pages
                and report.result_bytes < report.source_bytes * 0.9):
            _add_issue(
                report, "warning", "unreviewed_raster_pages", None,
                f"Only {raster_sampled_pages} of {report.raster_only_pages} "
                "raster-only pages were visually sampled. Compressed scan "
                "text on other pages cannot be checked at this resolution.")
        if image_pages and images_downscaled_hint:
            _add_issue(
                report, "warning", "image_resolution_reduced", None,
                "Images were downscaled: check fine print, seals and tiny "
                "details at 200% zoom.")
        if (image_pages and jpeg_quality_hint is not None
                and report.result_bytes <= report.source_bytes * 0.8
                and (jpeg_quality_hint <= 35
                     or (report.raster_only_pages > 0 and jpeg_quality_hint <= 55)
                     # User's 2.8.1 test pack: a photographic/mixed document
                     # lost over 85% at JPEG 48 but low-resolution thumbnails
                     # called it "no issues". At this intensity always request
                     # a high-zoom manual photo check, not a corruption verdict.
                     or (jpeg_quality_hint <= 55
                         and report.result_bytes <= report.source_bytes * 0.2))):
            _add_issue(
                report, "warning", "low_jpeg_detail_risk", None,
                f"JPEG quality {jpeg_quality_hint}% with substantial size "
                "reduction may blur fine image detail. Manually inspect "
                "scanned text, colors and seals at 200% zoom.")
        return report



def report_html(report: QualityReport) -> str:
    """Return a fully offline, escaped human-readable summary (no scripts)."""
    esc = lambda value: html.escape(str(value), quote=True)
    status_ru = {"error": "Обнаружены возможные нарушения",
                 "review": "Нужна визуальная проверка",
                 "no_issues_detected": "Замечаний в проверенных данных не найдено"}
    issue_rows = "\n".join(
        "<tr><td>" + esc(issue.page if issue.page is not None else "—") +
        "</td><td>" + esc(issue.severity) +
        "</td><td>" + esc(issue.code) +
        "</td><td>" + esc(issue.message) + "</td></tr>"
        for issue in report.issues
    ) or '<tr><td colspan="4">Замечаний не найдено.</td></tr>'
    sample_rows = "\n".join(
        f"<tr><td>{int(check.page)}</td>"
        f"<td>{check.mean_difference * 100:.2f}%</td>"
        f"<td>{check.changed_fraction * 100:.2f}%</td>"
        f"<td>{check.before_ink_fraction * 100:.2f}%</td>"
        f"<td>{check.after_ink_fraction * 100:.2f}%</td></tr>"
        for check in report.visual_checks
    ) or '<tr><td colspan="5">Визуальная проверка не проводилась.</td></tr>'
    return f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PDF Compressor 2.8 — отчёт качества</title>
<style>
body {{ font: 15px/1.5 system-ui, Segoe UI, sans-serif;
       max-width: 980px; margin: 36px auto; padding: 0 20px;
       background: #f8fafc; color: #172033; }}
h1 {{ font-size: 25px; margin: 0 0 6px; }}
h2 {{ margin-top: 34px; font-size: 19px; }}
p {{ overflow-wrap: anywhere; }}
table {{ width: 100%; border-collapse: collapse; background: white; }}
td, th {{ padding: 9px 12px; border-bottom: 1px solid #e2e8f0;
          text-align: left; vertical-align: top; }}
th {{ background: #eef2f7; }}
small, .muted {{ color: #475569; }}
footer {{ border-top: 1px solid #d8dfe8; padding-top: 16px;
          margin-top: 30px; color: #475569; }}
</style>
</head>
<body>
<h1>PDF Compressor 2.8 — проверка качества</h1>
<p class="muted">Предварительный автоматический отчёт, без OCR и подключения к сети.</p>
<p><strong>Результат: {esc(status_ru[report.status])}</strong></p>
<p><strong>Исходный PDF:</strong> {esc(report.source)}<br>
<strong>Результат:</strong> {esc(report.result)}</p>
<table><thead><tr><th>Показатель</th><th>До</th><th>После</th></tr></thead>
<tbody>
<tr><td>Размер файла</td><td>{report.source_bytes:,} Б</td>
<td>{report.result_bytes:,} Б</td></tr>
<tr><td>Страницы</td><td>{report.source_pages}</td>
<td>{report.result_pages}</td></tr>
<tr><td>Текст и геометрия проверены на страницах</td>
<td colspan="2">{report.text_checked_pages}</td></tr>
<tr><td>Растровые страницы без выделяемого текста</td>
<td colspan="2">{report.raster_only_pages}</td></tr>
<tr><td>JPEG качество, переданное компрессором</td>
<td colspan="2">{esc(str(report.jpeg_quality_hint) + '%' if report.jpeg_quality_hint is not None else 'не указано')}</td></tr>
<tr><td>Уменьшено разрешение изображений</td>
<td colspan="2">{'да' if report.images_downscaled_hint else 'нет / неизвестно'}</td></tr>
<tr><td>Визуально проверенные страницы (эскизы)</td>
<td colspan="2">{esc(", ".join(map(str, report.rendered_pages)) or "нет")}</td></tr>
</tbody></table>
<h2>Замечания</h2>
<table><thead><tr><th>Страница</th><th>Тип</th><th>Код</th><th>Описание</th></tr></thead>
<tbody>{issue_rows}</tbody></table>
<p class="muted">Дополнительных замечаний, не показанных в таблице: {report.suppressed_issues}.</p>
<h2>Сравнение небольших изображений страниц</h2>
<table><thead><tr><th>Стр.</th><th>Среднее отличие RGB</th>
<th>Изменённых пикселей</th><th>Чернила до</th><th>После</th></tr></thead>
<tbody>{sample_rows}</tbody></table>
<footer>
<strong>Важно:</strong> это не гарантия идентичности PDF и не оценка OCR.
Непроверенные визуально страницы, мелкий текст, печати, цветовые нюансы и
детали сканов требуют ручной проверки. JPEG может закономерно менять пиксели.
Исходные документы не изменялись этим анализом.
</footer>
</body></html>
"""



def main() -> int:
    parser = argparse.ArgumentParser(description="Offline PDF 2.8 quality audit (not a certification)")
    parser.add_argument("original", type=Path)
    parser.add_argument("result", type=Path)
    parser.add_argument("--samples", type=int, default=DEFAULT_RENDER_PAGES)
    parser.add_argument("--max-edge", type=int, default=DEFAULT_MAX_EDGE)
    parser.add_argument("--json", dest="output_json", type=Path)
    parser.add_argument("--html", dest="output_html", type=Path)
    args = parser.parse_args()
    report = audit_pdf(args.original, args.result,
                       max_render_pages=args.samples, max_thumbnail_edge=args.max_edge)
    content = json.dumps(report.as_dict(), indent=2, ensure_ascii=False) + "\n"
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(content, encoding="utf-8")
        print(f"Report written: {args.output_json}")
    else:
        print(content, end="")
    if args.output_html:
        args.output_html.parent.mkdir(parents=True, exist_ok=True)
        args.output_html.write_text(report_html(report), encoding="utf-8")
        print(f"HTML report written: {args.output_html}")
    # Exit status 1 means possible damage; warnings are reviewed by a human.
    return int(report.status == "error")


if __name__ == "__main__":
    raise SystemExit(main())
