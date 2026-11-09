"""2.8 quality audit: integrity, visual differences, limits and cancellation."""
from __future__ import annotations

from io import BytesIO
import json
from pathlib import Path
import threading

from PIL import Image
import pymupdf
import pytest

import pdf_quality
from pdf_engine import Cancelled, compress_pdf
from pdf_quality import audit_pdf, _sample_indexes


def text_pdf(path: Path, pages: int = 2, *, label: str = "Original",
             rotation: int = 0) -> Path:
    with pymupdf.open() as doc:
        for n in range(pages):
            page = doc.new_page(width=595, height=842)
            page.insert_text((65, 90), f"{label} page {n + 1}", fontsize=12)
            page.insert_text((65, 125), "Select this text", fontsize=12)
            if rotation:
                page.set_rotation(rotation)
        doc.save(path)
    return path


def solid_scan(path: Path, color: str) -> Path:
    stream = BytesIO()
    Image.new("RGB", (450, 450), color).save(stream, format="PNG")
    with pymupdf.open() as doc:
        page = doc.new_page(width=500, height=500)
        page.insert_image(page.rect, stream=stream.getvalue(), keep_proportion=False)
        doc.save(path)
    return path


def test_identical_pdf_has_no_issues_and_does_not_modify_source(tmp_path):
    source = text_pdf(tmp_path / "source.pdf", pages=3)
    contents = source.read_bytes()
    report = audit_pdf(source, source)
    assert report.status == "no_issues_detected"
    assert report.text_checked_pages == 3
    assert report.rendered_pages == (1, 2, 3)
    assert all(v.mean_difference == 0 for v in report.visual_checks)
    assert report.source_bytes == report.result_bytes == len(contents)
    assert source.read_bytes() == contents
    assert json.loads(json.dumps(report.as_dict()))["status"] == "no_issues_detected"


def test_missing_page_is_critical(tmp_path):
    before = text_pdf(tmp_path / "before.pdf", pages=3)
    after = text_pdf(tmp_path / "after.pdf", pages=2)
    result = audit_pdf(before, after)
    assert result.status == "error"
    assert any(x.code == "page_count_changed" for x in result.issues)


def test_changed_selectable_text_is_critical(tmp_path):
    before = text_pdf(tmp_path / "before.pdf", label="Original")
    after = text_pdf(tmp_path / "after.pdf", label="Modified")
    result = audit_pdf(before, after)
    assert result.status == "error"
    assert {x.page for x in result.issues if x.code == "selectable_text_changed"} == {1, 2}


def test_text_removed_entirely_is_critical(tmp_path):
    before = text_pdf(tmp_path / "before.pdf", pages=1)
    after = tmp_path / "blank.pdf"
    with pymupdf.open() as doc:
        doc.new_page(width=595, height=842)
        doc.save(after)
    result = audit_pdf(before, after)
    assert result.status == "error"
    assert any(issue.code == "selectable_text_lost" for issue in result.issues)


def test_rotation_change_is_critical(tmp_path):
    before = text_pdf(tmp_path / "before.pdf", pages=1)
    after = text_pdf(tmp_path / "rotated.pdf", pages=1, rotation=90)
    result = audit_pdf(before, after)
    assert result.status == "error"
    assert any(issue.code == "page_geometry_changed" for issue in result.issues)


def test_major_image_change_warns_without_claiming_corruption(tmp_path):
    before = solid_scan(tmp_path / "before.pdf", "red")
    after = solid_scan(tmp_path / "after.pdf", "blue")
    result = audit_pdf(before, after)
    assert result.status == "review"
    assert result.text_checked_pages == 1
    assert result.visual_checks[0].mean_difference > 0.20
    assert any(issue.code == "major_visual_difference" for issue in result.issues)
    assert all(issue.severity != "error" for issue in result.issues)


def test_nonempty_scanned_page_becoming_blank_is_critical(tmp_path):
    before = solid_scan(tmp_path / "scan.pdf", "black")
    after = tmp_path / "blank.pdf"
    with pymupdf.open() as doc:
        doc.new_page(width=500, height=500)
        doc.save(after)
    result = audit_pdf(before, after)
    assert result.status == "error"
    assert any(issue.code == "possibly_blank_output" for issue in result.issues)


def test_bounded_visual_sampling_but_all_page_text_checked(tmp_path, monkeypatch):
    before = text_pdf(tmp_path / "before.pdf", pages=50)
    after = text_pdf(tmp_path / "after.pdf", pages=50)
    actual = pdf_quality._thumbnail
    calls = []

    def count_render(page, edge):
        calls.append((page.number, edge))
        return actual(page, edge)

    monkeypatch.setattr(pdf_quality, "_thumbnail", count_render)
    report = audit_pdf(before, after, max_render_pages=5, max_thumbnail_edge=220)
    assert report.status == "no_issues_detected"
    assert report.text_checked_pages == 50
    assert report.rendered_pages[0] == 1
    assert report.rendered_pages[-1] == 50
    assert len(report.rendered_pages) == 5
    assert len(calls) == 10   # two bounded thumbnails per sampled page
    assert all(edge == 220 for _, edge in calls)


def test_no_visual_sampling_is_explicitly_uncertain(tmp_path):
    src = text_pdf(tmp_path / "source.pdf")
    report = audit_pdf(src, src, max_render_pages=0)
    assert report.status == "review"
    assert report.rendered_pages == ()
    assert report.text_checked_pages == 2
    assert any(x.code == "visual_check_disabled" for x in report.issues)


def test_cancelled_audit_raises_standard_engine_exception(tmp_path):
    before = text_pdf(tmp_path / "source.pdf")
    cancel = threading.Event()
    cancel.set()
    with pytest.raises(Cancelled):
        audit_pdf(before, before, cancel=cancel)


def test_invalid_sample_configuration_rejected(tmp_path):
    src = text_pdf(tmp_path / "source.pdf")
    for n in (-1, 33, True, "8"):
        with pytest.raises(ValueError):
            audit_pdf(src, src, max_render_pages=n)
    for edge in (0, 50, 700, True):
        with pytest.raises(ValueError):
            audit_pdf(src, src, max_thumbnail_edge=edge)


def test_missing_or_invalid_file_rejected(tmp_path):
    src = text_pdf(tmp_path / "source.pdf")
    with pytest.raises(FileNotFoundError):
        audit_pdf(src, tmp_path / "missing.pdf")
    bad = tmp_path / "not-pdf.txt"
    bad.write_text("not a pdf", encoding="utf-8")
    with pytest.raises(ValueError, match="Only PDF"):
        audit_pdf(src, bad)


def test_even_sampling_bounds_first_and_last():
    assert _sample_indexes(0, 8) == ()
    assert _sample_indexes(2, 8) == (0, 1)
    assert _sample_indexes(10, 1) == (0,)
    assert _sample_indexes(1000, 8)[0] == 0
    assert _sample_indexes(1000, 8)[-1] == 999
    assert len(set(_sample_indexes(1000, 8))) == 8


def test_real_smartfit_output_stays_selectable_and_audit_noncritical(tmp_path):
    before = text_pdf(tmp_path / "text.pdf", pages=5)
    compression = compress_pdf(before, tmp_path / "results",
                               mode="smartfit", target_mb=0.01)
    result = audit_pdf(before, compression.output)
    assert result.status == "no_issues_detected"
    assert len(result.issues) == 0
    assert result.text_checked_pages == 5


def test_issue_collection_is_bounded_for_large_damaged_documents(tmp_path):
    before = text_pdf(tmp_path / "before.pdf", pages=100, label="Original")
    after = text_pdf(tmp_path / "after.pdf", pages=100, label="Changed")
    report = audit_pdf(before, after, max_render_pages=0)
    assert report.status == "error"
    assert len(report.issues) <= pdf_quality.MAX_REPORTED_ISSUES
    assert report.suppressed_issues > 0
