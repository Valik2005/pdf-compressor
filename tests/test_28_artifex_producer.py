"""PyMuPDF AGPL producer acknowledgement without changing original source metadata."""
from pathlib import Path

import pymupdf

from pdf_engine import compress_pdf, merge_pdfs, rotate_pdf, split_pdf


def _make_pdf(path: Path, name: str) -> None:
    with pymupdf.open() as doc:
        page = doc.new_page()
        page.insert_text((70, 100), "Producer notice test", fontsize=14)
        doc.set_metadata({
            "creator": "Original document editor",
            "producer": name,
            "title": "Preserve metadata",
        })
        doc.save(path)


def test_newly_generated_merge_and_extraction_credit_mupdf(tmp_path):
    one, two = tmp_path / "one.pdf", tmp_path / "two.pdf"
    _make_pdf(one, "Original One Producer")
    _make_pdf(two, "Original Two Producer")
    originals = {p: p.read_bytes() for p in (one, two)}

    merged = merge_pdfs((one, two), tmp_path / "merge")
    extracted = split_pdf(one, tmp_path / "extract", "1")
    for name in [merged, *extracted]:
        with pymupdf.open(name) as doc:
            assert doc.metadata["producer"] == "MuPDF (via PyMuPDF); PDF Compressor 2.8"
            assert doc.metadata["creator"] == "PDF Compressor 2.8"
            assert "Producer notice test" in doc[0].get_text()
    assert all(src.read_bytes() == data for src, data in originals.items())


def test_compression_and_rotation_keep_upstream_producer_creator(tmp_path):
    src = tmp_path / "original.pdf"
    _make_pdf(src, "Original Author Application")
    before = src.read_bytes()
    original = {}
    with pymupdf.open(src) as doc:
        original = {key: doc.metadata[key] for key in ("producer", "creator", "title")}

    compressed = compress_pdf(src, tmp_path / "compress", mode="balanced")
    rotated = rotate_pdf(src, tmp_path / "rotate", degrees=90)
    for result in [compressed.output, rotated]:
        with pymupdf.open(result) as doc:
            assert {key: doc.metadata[key] for key in original} == original
            assert doc[0].get_text() == "Producer notice test\n"
    assert src.read_bytes() == before


def test_empty_existing_producer_not_replaced_in_compression(tmp_path):
    """An existing input document is not a new PDF created by merge/split."""
    src = tmp_path / "blank_source_metadata.pdf"
    with pymupdf.open() as doc:
        doc.new_page()
        doc.save(src)
    compressed = compress_pdf(src, tmp_path / "out", mode="quality")
    with pymupdf.open(compressed.output) as result:
        assert result.metadata["producer"] == ""
