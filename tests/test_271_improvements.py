"""PDF Compressor 2.7.1: no-op SmartFit work and responsive final-copy cancellation."""
from __future__ import annotations

from io import BytesIO
from pathlib import Path
import hashlib
import threading

from PIL import Image
import pymupdf
import pytest

import pdf_engine
from pdf_engine import Cancelled, _copy_with_cancel, analyze_pdf, compress_pdf, merge_pdfs


def make_pdf(path: Path, *, with_small_image: bool, pages: int = 2) -> Path:
    image_bytes = BytesIO()
    Image.new("RGB", (64, 64), (72, 113, 190)).save(image_bytes, format="PNG")
    with pymupdf.open() as doc:
        for page_no in range(pages):
            page = doc.new_page()
            page.insert_text((72, 80), f"Searchable vector text page {page_no + 1}")
            if with_small_image and page_no == 0:
                page.insert_image(pymupdf.Rect(100, 150, 140, 190),
                                  stream=image_bytes.getvalue())
        doc.save(path)
    return path


def test_tiny_images_skip_wasteful_smartfit_quality_trials(tmp_path):
    """The engine cannot resize or recompress 64 px icons in any candidate."""
    src = make_pdf(tmp_path / "tiny-icons.pdf", with_small_image=True, pages=90)
    analysis = analyze_pdf(src)
    assert analysis.raster_images == 1
    assert analysis.recompressible_images == 0

    result = compress_pdf(src, tmp_path / "out", mode="smartfit",
                          target_mb=0.01, allow_downscale=True)
    assert result.candidates_tried == 0
    assert result.downscaled is False
    assert result.target_met is False
    assert result.analysis is not None
    assert result.analysis.raster_images == 1
    assert any("JPEG-сжатие не затронет изображения" in note
               for note in result.recommendations)
    with pymupdf.open(result.output) as saved:
        assert len(saved) == 90
        assert "Searchable vector text" in saved[0].get_text("text")
        assert saved[0].get_images(full=True)


def test_regular_embedded_raster_remains_eligible(tmp_path):
    src = tmp_path / "large.png"
    buf = BytesIO()
    Image.new("RGB", (256, 256), (100, 140, 180)).save(buf, format="PNG")
    with pymupdf.open() as doc:
        for _ in range(2):
            p = doc.new_page()
            p.insert_image(pymupdf.Rect(100, 100, 300, 300), stream=buf.getvalue())
        doc.save(src.with_suffix(".pdf"))
    result = analyze_pdf(src.with_suffix(".pdf"))
    assert result.raster_images >= 1
    assert result.recompressible_images >= 1


def test_copy_with_cancel_preserves_bytes_when_complete(tmp_path):
    original = tmp_path / "source.dat"
    output = tmp_path / "copy.dat"
    original.write_bytes(b"PDF compressed payload" * 120_000)
    _copy_with_cancel(original, output)
    assert hashlib.sha256(original.read_bytes()).digest() == hashlib.sha256(output.read_bytes()).digest()


def test_copy_with_cancel_aborts_between_chunks(tmp_path):
    original = tmp_path / "source.dat"
    output = tmp_path / "partial.dat"
    original.write_bytes(b"x" * (3 * 1024 * 1024))

    class FlipAfterFirstChunk:
        calls = 0

        def is_set(self):
            self.calls += 1
            return self.calls >= 3

    with pytest.raises(Cancelled):
        _copy_with_cancel(original, output, FlipAfterFirstChunk())

    assert output.exists()
    assert 0 < output.stat().st_size < original.stat().st_size


@pytest.mark.parametrize("operation", ["compress", "merge"])
def test_interrupted_final_copy_leaves_no_output(tmp_path, monkeypatch, operation):
    source = make_pdf(tmp_path / "source.pdf", with_small_image=False)
    out_dir = tmp_path / "output"

    def interrupt_after_partial_copy(_source, dest, _cancel):
        Path(dest).write_bytes(b"partial")
        raise Cancelled("Interrupted during final copy")

    monkeypatch.setattr(pdf_engine, "_copy_with_cancel", interrupt_after_partial_copy)
    with pytest.raises(Cancelled):
        if operation == "compress":
            compress_pdf(source, out_dir, mode="balanced")
        else:
            merge_pdfs([source, source], out_dir)
    assert not list(out_dir.glob("*.pdf")), "Partial/corrupted output must be removed"


def test_271_gui_version_and_noop_advice_translation():
    # Validate these without requiring a running Qt desktop session.
    from pathlib import Path
    ui = (Path(__file__).parents[1] / "app.pyw").read_text(encoding="utf-8")
    assert 'APP_VERSION = "2.8-preview"' in ui
    assert 'version = QLabel(APP_VERSION)' in ui
    assert 'app.setApplicationName(f"PDF Compressor {APP_VERSION}")' in ui
    assert 'JPEG compression cannot affect these images:' in ui
