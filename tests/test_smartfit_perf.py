"""Regression checks for SmartFit's strict-target search optimizations."""
from io import BytesIO

import pymupdf
from PIL import Image

from pdf_engine import compress_pdf


def _high_dpi_pdf(path):
    noise = Image.effect_noise((900, 1200), 110).convert("RGB")
    data = BytesIO()
    noise.save(data, "PNG")
    with pymupdf.open() as doc:
        page = doc.new_page()
        page.insert_image(pymupdf.Rect(20, 20, 120, 160), stream=data.getvalue())
        doc.save(path)
    return path


def test_unreachable_target_skips_redundant_quality_trials(tmp_path):
    source = _high_dpi_pdf(tmp_path / "unreachable.pdf")
    result = compress_pdf(source, tmp_path / "out", mode="smartfit",
                          target_mb=0.01, allow_downscale=True)
    assert result.target_met is False
    # Four stages (original, 220, 180, 150), at most midpoint + floor each.
    assert result.candidates_tried <= 8
    with pymupdf.open(result.output) as doc:
        assert len(doc) == 1
        assert doc[0].get_images()


def test_placements_computed_once_for_dpi_search(tmp_path, monkeypatch):
    import pdf_engine

    source = _high_dpi_pdf(tmp_path / "highdpi.pdf")
    original = pdf_engine._all_image_placements
    calls = []

    def count_calls(doc, cancel=None):
        calls.append(len(doc))
        return original(doc, cancel)

    monkeypatch.setattr(pdf_engine, "_all_image_placements", count_calls)
    result = compress_pdf(source, tmp_path / "out", mode="smartfit",
                          target_mb=0.01, allow_downscale=True)
    assert result.target_met is False
    assert calls == [1]
