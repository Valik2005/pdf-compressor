# -*- coding: utf-8 -*-
"""PDF Compressor 2.8: bounded, offline quality review for original vs output.

This is a *diagnostic*, not a certificate of visual equivalence. All pages
are checked for geometry and extractable-text integrity; only a deterministic
subset is rendered at thumbnail resolution to keep RAM/CPU under control.
The module does not alter either PDF and uses no network or OCR.
"""
from __future__ import annotations

import argparse
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
    mean_difference: float  # normalized 0..1, grayscale pixel mean absolute error
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
    return sum(histogram[:221]) / max(1, gray.width * gray.height)


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
              cancel: threading.Event | None = None,
              progress: Progress | None = None) -> QualityReport:
    """Check document integrity and sample visual changes after compression.

    * Page count, page geometry, rotation and selectable text: every paired page.
    * Pixel analysis: evenly spaced preview thumbnails, at most 32 by default.
    * Large visual changes are warnings, never automatic corruption verdicts.
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
            report.text_checked_pages += 1
            if text_before != text_after:
                code = "selectable_text_lost" if text_before.strip() and not text_after.strip() \
                    else "selectable_text_changed"
                _add_issue(report, "error", code, page_no,
                           "Selectable text disappeared or changed; inspect original and result.")

            if index in indexes_to_render:
                image_before = _thumbnail(src, max_thumbnail_edge)
                image_after = _thumbnail(dst, max_thumbnail_edge)
                metrics = _visual_difference(image_before, image_after, page_no)
                report.visual_checks.append(metrics)
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
        return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline PDF 2.8 quality audit (not a certification)")
    parser.add_argument("original", type=Path)
    parser.add_argument("result", type=Path)
    parser.add_argument("--samples", type=int, default=DEFAULT_RENDER_PAGES)
    parser.add_argument("--max-edge", type=int, default=DEFAULT_MAX_EDGE)
    parser.add_argument("--json", dest="output_json", type=Path)
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
    # Exit status 1 means possible damage; warnings are reviewed by a human.
    return int(report.status == "error")


if __name__ == "__main__":
    raise SystemExit(main())
