"""Control-audit regression tests for PDF Compressor 2.7."""
from pathlib import Path
import threading

import pymupdf
import pytest

import pdf_engine
from pdf_engine import Cancelled, _required_scaled_size, compress_pdf, parse_pages


def _text_pdf(path):
    with pymupdf.open() as doc:
        doc.new_page().insert_text((72, 72), "Preserve selectable text")
        doc.save(path)
    return path


def test_page_selection_preserves_order_and_removes_duplicates():
    assert parse_pages("5,1-3,2,5,4", 5) == [4, 0, 1, 2, 3]


def test_scaled_dimensions_never_fall_below_required_pixel_count():
    # A shared image stretched across both axes needs a conservative
    # integer pixel count after uniform resizing.
    width, height = 1000, 999
    usage = (240.1, 239.1)
    scaled = _required_scaled_size({9: usage}, 9, (width, height), 150)
    assert scaled is not None
    assert scaled[0] >= __import__("math").ceil(usage[0] * 150 / 72)
    assert scaled[1] >= __import__("math").ceil(usage[1] * 150 / 72)


def test_partial_output_removed_if_copy_fails(tmp_path, monkeypatch):
    source = _text_pdf(tmp_path / "source.pdf")
    original_copy = pdf_engine.shutil.copyfile

    def fail_after_partial_copy(src, dst):
        if Path(dst).parent == tmp_path / "out":
            Path(dst).write_bytes(b"%PDF-partial")
            raise OSError("simulated disk write failure")
        return original_copy(src, dst)

    monkeypatch.setattr(pdf_engine.shutil, "copyfile", fail_after_partial_copy)
    with pytest.raises(OSError, match="simulated"):
        compress_pdf(source, tmp_path / "out", mode="smartfit", target_mb=1)
    assert list((tmp_path / "out").glob("*.pdf")) == []


def test_cancellation_during_final_copy_removes_output(tmp_path, monkeypatch):
    source = _text_pdf(tmp_path / "source.pdf")
    cancel = threading.Event()
    original_copy = pdf_engine.shutil.copyfile

    def cancel_after_copy(src, dst):
        result = original_copy(src, dst)
        if Path(dst).parent == tmp_path / "out":
            cancel.set()
        return result

    monkeypatch.setattr(pdf_engine.shutil, "copyfile", cancel_after_copy)
    with pytest.raises(Cancelled):
        compress_pdf(source, tmp_path / "out", mode="smartfit", target_mb=1, cancel=cancel)
    assert list((tmp_path / "out").glob("*.pdf")) == []
