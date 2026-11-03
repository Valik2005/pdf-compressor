"""SmartFit v2.7: content triage, conservative output and shared-image DPI."""
from io import BytesIO
from pathlib import Path
import threading

import pymupdf
import pytest
from PIL import Image

from pdf_engine import (
    Cancelled, _all_image_placements, _required_scaled_size,
    analyze_pdf, build_candidate, compress_pdf,
)


def raster_data(size=(600, 800)) -> bytes:
    img = Image.effect_noise(size, 110).convert("RGB")
    output = BytesIO()
    img.save(output, "PNG")
    return output.getvalue()


def create_pdf(path: Path, *, text: bool, image: bool, mixed: bool = False) -> Path:
    with pymupdf.open() as doc:
        page = doc.new_page(width=595, height=842)
        if image:
            page.insert_image(pymupdf.Rect(0, 0, 595, 842), stream=raster_data())
        if text:
            page.insert_text((48, 40), "Selectable digital text", fontsize=12)
        if mixed:
            page.insert_text((48, 80), "Additional label", fontsize=12)
        doc.save(path)
    return path


@pytest.mark.parametrize("has_text,has_image,expected", [
    (True, False, "text"),
    (False, True, "scan"),
    (True, True, "mixed"),
    (False, False, "other"),
])
def test_analysis_classes(tmp_path, has_text, has_image, expected):
    path = create_pdf(tmp_path / f"{expected}.pdf", text=has_text, image=has_image)
    analysis = analyze_pdf(path)
    assert analysis.pages == 1
    assert analysis.kind == expected
    assert analysis.text_pages == int(has_text)
    assert analysis.image_pages == int(has_image)
    assert analysis.source_bytes == path.stat().st_size


def test_smartfit_size_and_structure(tmp_path):
    path = create_pdf(tmp_path / "scanned.pdf", text=False, image=True)
    result = compress_pdf(path, tmp_path / "done", mode="smartfit", target_mb=0.35)
    assert result.analysis is not None
    assert result.analysis.kind == "scan"
    assert result.target_met == (Path(result.output).stat().st_size <= 350_000)
    assert result.candidates_tried >= 0
    assert result.original_bytes == path.stat().st_size
    with pymupdf.open(result.output) as pdf:
        assert len(pdf) == 1
        assert pdf[0].get_images()
    assert path.exists()  # Original was not overwritten.


def test_smartfit_reports_unreachable_target(tmp_path):
    path = create_pdf(tmp_path / "text.pdf", text=True, image=False)
    result = compress_pdf(path, tmp_path / "out", mode="smartfit", target_mb=0.01)
    # If the generated tiny digital PDF happens to fit 10kB, use a much larger
    # one by generating multiple pages for the truly unreachable case.
    if result.target_met:
        with pymupdf.open(path) as doc:
            for i in range(300):
                page = doc.new_page()
                page.insert_text((72, 72), f"Vector text on page {i}")
            doc.save(tmp_path / "bigger.pdf")
        result = compress_pdf(tmp_path / "bigger.pdf", tmp_path / "out", mode="smartfit", target_mb=0.01)
    assert result.target_met is False
    assert result.analysis.raster_images == 0
    assert result.candidates_tried == 0
    assert any("сжатие может не помочь" in note for note in result.recommendations)


def test_shared_images_keep_resolution_needed_later(tmp_path):
    picture = raster_data((900, 1200))
    source = tmp_path / "shared.pdf"
    with pymupdf.open() as doc:
        tiny = doc.new_page(width=595, height=842)
        xref = tiny.insert_image(pymupdf.Rect(30, 30, 100, 125), stream=picture)
        big = doc.new_page(width=595, height=842)
        big.insert_image(pymupdf.Rect(20, 30, 550, 790), xref=xref)
        doc.save(source)
    with pymupdf.open(source) as doc:
        usage = _all_image_placements(doc)
        assert usage[xref] is not None
        # At 150dpi the later large placement needs full source resolution.
        assert _required_scaled_size(usage, xref, (900, 1200), 150) is None
    out = tmp_path / "candidate.pdf"
    build_candidate(source, out, quality=62, max_dpi=150)
    with pymupdf.open(out) as doc:
        assert len(doc) == 2
        assert doc[0].get_images()[0][0] == doc[1].get_images()[0][0]
        assert doc[1].get_images()[0][2:4] == (900, 1200)


def test_shared_images_can_downscale_when_both_small(tmp_path):
    picture = raster_data((900, 1200))
    source = tmp_path / "small-shared.pdf"
    with pymupdf.open() as doc:
        tiny = doc.new_page(width=595, height=842)
        xref = tiny.insert_image(pymupdf.Rect(30, 30, 100, 125), stream=picture)
        second = doc.new_page(width=595, height=842)
        second.insert_image(pymupdf.Rect(50, 30, 165, 180), xref=xref)
        doc.save(source)
    with pymupdf.open(source) as doc:
        usage = _all_image_placements(doc)
        size = _required_scaled_size(usage, xref, (900, 1200), 150)
        assert size is not None
        assert size[0] < 900
        assert size[1] < 1200


def test_cancel_during_smartfit_analysis(tmp_path):
    path = create_pdf(tmp_path / "page.pdf", text=True, image=False)
    cancelled = threading.Event()
    cancelled.set()
    with pytest.raises(Cancelled):
        analyze_pdf(path, cancel=cancelled)
    with pytest.raises(Cancelled):
        compress_pdf(path, tmp_path / "out", mode="smartfit", cancel=cancelled)


def test_smartfit_preserves_selectable_text(tmp_path):
    """Image recompression must not alter searchable text on mixed pages."""
    source = create_pdf(tmp_path / "mixed.pdf", text=True, image=True)
    result = compress_pdf(
        source, tmp_path / "output", mode="smartfit", target_mb=0.15
    )
    with pymupdf.open(source) as original, pymupdf.open(result.output) as output:
        assert len(original) == len(output)
        assert [page.get_text("text") for page in original] == [
            page.get_text("text") for page in output
        ]


def test_smartfit_does_not_downscale_without_permission(tmp_path):
    """Target-size pressure alone must never reduce image pixel dimensions."""
    source = create_pdf(tmp_path / "scan.pdf", text=False, image=True)
    result = compress_pdf(
        source, tmp_path / "output", mode="smartfit",
        target_mb=0.01, allow_downscale=False
    )
    assert result.downscaled is False
    with pymupdf.open(source) as original, pymupdf.open(result.output) as output:
        source_xref = original[0].get_images(full=True)[0][0]
        result_xref = output[0].get_images(full=True)[0][0]
        assert original.extract_image(source_xref)["width"] == output.extract_image(result_xref)["width"]
        assert original.extract_image(source_xref)["height"] == output.extract_image(result_xref)["height"]


def test_unhelpful_dpi_stages_are_skipped(tmp_path):
    """Low-resolution pages must not trigger redundant JPEG recompression."""
    from pdf_engine import _useful_dpi_stages
    source = create_pdf(tmp_path / "lowdpi.pdf", text=True, image=True)
    assert _useful_dpi_stages(source, [220, 180, 150]) == set()

    normal = compress_pdf(
        source, tmp_path / "normal", mode="smartfit",
        target_mb=0.01, allow_downscale=False
    )
    opt_in = compress_pdf(
        source, tmp_path / "opt-in", mode="smartfit",
        target_mb=0.01, allow_downscale=True
    )
    assert not normal.target_met
    assert not opt_in.target_met
    assert normal.candidates_tried == opt_in.candidates_tried
    assert normal.quality == opt_in.quality
    assert not opt_in.downscaled


def test_useful_dpi_stages_remain_available(tmp_path):
    """High-resolution images must still be eligible for downscaling."""
    from pdf_engine import _useful_dpi_stages
    source = tmp_path / "highdpi.pdf"
    with pymupdf.open() as doc:
        page = doc.new_page(width=595, height=842)
        page.insert_image(
            pymupdf.Rect(20, 20, 120, 160),
            stream=raster_data((900, 1200))
        )
        page.insert_text((150, 80), "Selectable text", fontsize=16)
        doc.save(source)

    assert _useful_dpi_stages(source, [220, 180, 150]) == {220, 180, 150}
    normal = compress_pdf(
        source, tmp_path / "normal", mode="smartfit",
        target_mb=0.15, allow_downscale=False
    )
    opt_in = compress_pdf(
        source, tmp_path / "opt-in", mode="smartfit",
        target_mb=0.15, allow_downscale=True
    )
    assert not normal.target_met
    assert opt_in.target_met
    assert opt_in.downscaled
    with pymupdf.open(source) as original, pymupdf.open(opt_in.output) as output:
        assert output[0].get_text("text") == original[0].get_text("text")
        before_image = original[0].get_images(full=True)[0]
        after_image = output[0].get_images(full=True)[0]
        assert after_image[2] < before_image[2]
        assert after_image[3] < before_image[3]
