"""Regression tests: PDF tools must never leave a partial output after failure/cancel."""
from pathlib import Path
import threading

import pymupdf
import pytest

import pdf_engine
from pdf_engine import Cancelled, merge_pdfs, rotate_pdf, split_pdf


@pytest.fixture
def source(tmp_path):
    path = tmp_path / "source.pdf"
    with pymupdf.open() as doc:
        for page_no in range(3):
            doc.new_page().insert_text((72, 72), f"Page {page_no + 1}")
        doc.save(path)
    return path


def test_merge_removes_partial_copy_on_write_error(tmp_path, source, monkeypatch):
    folder = tmp_path / "merged"
    original = source.read_bytes()
    real_copy = pdf_engine.shutil.copyfile

    def fail_final_copy(src, dst):
        if Path(dst).parent == folder:
            Path(dst).write_bytes(b"%PDF-partial")
            raise OSError("simulated destination write failure")
        return real_copy(src, dst)

    monkeypatch.setattr(pdf_engine.shutil, "copyfile", fail_final_copy)
    with pytest.raises(OSError, match="simulated"):
        merge_pdfs([source, source], folder)
    assert list(folder.glob("*.pdf")) == []
    assert source.read_bytes() == original


def test_merge_removes_output_if_cancelled_during_copy(tmp_path, source, monkeypatch):
    folder = tmp_path / "merged"
    cancel = threading.Event()
    real_copy = pdf_engine.shutil.copyfile

    def cancel_after_copy(src, dst):
        result = real_copy(src, dst)
        if Path(dst).parent == folder:
            cancel.set()
        return result

    monkeypatch.setattr(pdf_engine.shutil, "copyfile", cancel_after_copy)
    with pytest.raises(Cancelled):
        merge_pdfs([source, source], folder, cancel=cancel)
    assert list(folder.glob("*.pdf")) == []


def test_split_removes_current_partial_and_previous_outputs(tmp_path, source, monkeypatch):
    folder = tmp_path / "splits"
    original = source.read_bytes()
    real_save = pdf_engine._save_pdf
    calls = 0

    def fail_second_save(doc, target):
        nonlocal calls
        calls += 1
        if calls == 2:
            Path(target).write_bytes(b"%PDF-partial")
            raise OSError("simulated split write failure")
        return real_save(doc, target)

    monkeypatch.setattr(pdf_engine, "_save_pdf", fail_second_save)
    with pytest.raises(OSError, match="simulated"):
        split_pdf(source, folder, pages="1-3", each_page=True)
    assert calls == 2
    assert list(folder.glob("*.pdf")) == []
    assert source.read_bytes() == original


def test_split_removes_output_if_cancelled_after_save(tmp_path, source, monkeypatch):
    folder = tmp_path / "splits"
    cancel = threading.Event()
    real_save = pdf_engine._save_pdf

    def cancel_after_save(doc, target):
        size = real_save(doc, target)
        cancel.set()
        return size

    monkeypatch.setattr(pdf_engine, "_save_pdf", cancel_after_save)
    with pytest.raises(Cancelled):
        split_pdf(source, folder, pages="1-3", each_page=True, cancel=cancel)
    assert list(folder.glob("*.pdf")) == []


def test_rotate_removes_partial_output_on_write_error(tmp_path, source, monkeypatch):
    folder = tmp_path / "rotated"
    original = source.read_bytes()

    def fail_save(doc, target):
        Path(target).write_bytes(b"%PDF-partial")
        raise OSError("simulated rotate write failure")

    monkeypatch.setattr(pdf_engine, "_save_pdf", fail_save)
    with pytest.raises(OSError, match="simulated"):
        rotate_pdf(source, folder, degrees=90)
    assert list(folder.glob("*.pdf")) == []
    assert source.read_bytes() == original


def test_rotate_removes_output_if_cancelled_after_save(tmp_path, source, monkeypatch):
    folder = tmp_path / "rotated"
    cancel = threading.Event()
    real_save = pdf_engine._save_pdf

    def cancel_after_save(doc, target):
        size = real_save(doc, target)
        cancel.set()
        return size

    monkeypatch.setattr(pdf_engine, "_save_pdf", cancel_after_save)
    with pytest.raises(Cancelled):
        rotate_pdf(source, folder, degrees=90, cancel=cancel)
    assert list(folder.glob("*.pdf")) == []
