"""2.8: user-verified near-miss target precision without global quality regression."""
from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pymupdf
from PIL import Image

import pdf_engine
from pdf_engine import build_candidate, compress_pdf


def color_control_pdf(path: Path) -> Path:
    """Three noisy color pages mirror the real 2.7.1 target-precision test."""
    with pymupdf.open() as document:
        for index in range(3):
            image = Image.effect_noise((640, 850), 90 + index * 4).convert("RGB")
            data = BytesIO()
            image.save(data, format="PNG")
            page = document.new_page(width=595, height=842)
            page.insert_text((35, 28), f"Editable color test page {index + 1}")
            page.insert_image(pymupdf.Rect(30, 55, 565, 760), stream=data.getvalue())
        document.save(path)
    return path


def test_precise_target_bounded_rescue_from_user_near_miss(tmp_path, monkeypatch):
    source = color_control_pdf(tmp_path / "color.pdf")
    compressed_at_floor = tmp_path / "jpeg30.pdf"
    compressed_at_rescue = tmp_path / "jpeg27.pdf"
    floor_size, _, _ = build_candidate(source, compressed_at_floor, quality=30)
    rescue_size, _, _ = build_candidate(source, compressed_at_rescue, quality=27)
    assert 0 < rescue_size < floor_size
    # Budget is unreachable at the established JPEG 30% floor but near enough
    # that an extra 2-3 JPEG quality steps might meet it.
    budget = (rescue_size + floor_size) // 2
    assert floor_size <= int(budget * 1.08)

    seen_qualities: list[int] = []
    original_build = pdf_engine.build_candidate

    def traced_candidate(*args, **kwargs):
        if kwargs.get("quality") is not None:
            seen_qualities.append(kwargs["quality"])
        return original_build(*args, **kwargs)

    monkeypatch.setattr(pdf_engine, "build_candidate", traced_candidate)
    original_bytes = source.read_bytes()
    result = compress_pdf(
        source, tmp_path / "out", mode="target",
        target_mb=budget / 1_000_000, allow_downscale=False,
    )
    assert result.target_met is True
    assert result.result_bytes <= budget
    assert result.quality in (27, 28, 29)
    assert not result.downscaled
    # Extra near-miss probes are bounded to two; never exhaustively scan 1..29.
    rescue_probes = [q for q in seen_qualities if q < 30]
    assert 1 <= len(rescue_probes) <= 2
    assert set(rescue_probes).issubset({27, 28, 29})
    assert original_bytes == source.read_bytes()
    with pymupdf.open(source) as before, pymupdf.open(result.output) as after:
        assert len(before) == len(after) == 3
        assert [page.get_text("text") for page in before] == [
            page.get_text("text") for page in after
        ]
        for i in range(3):
            src_image = before[i].get_images(full=True)[0]
            out_image = after[i].get_images(full=True)[0]
            assert src_image[2:4] == out_image[2:4]


def test_smartfit_does_not_use_aggressive_near_miss_fallback(tmp_path, monkeypatch):
    source = color_control_pdf(tmp_path / "mixed.pdf")
    floor_file = tmp_path / "jpeg30.pdf"
    floor_size, _, _ = build_candidate(source, floor_file, quality=30)
    target = floor_size / 1_000_000
    trial_q: list[int] = []
    original = pdf_engine.build_candidate

    def traced_candidate(*args, **kwargs):
        if kwargs.get("quality") is not None:
            trial_q.append(kwargs["quality"])
        return original(*args, **kwargs)

    monkeypatch.setattr(pdf_engine, "build_candidate", traced_candidate)
    result = compress_pdf(
        source, tmp_path / "out", mode="smartfit",
        target_mb=target, allow_downscale=False)
    assert result.analysis is not None
    assert result.analysis.kind == "mixed"
    assert all(q >= 62 for q in trial_q)
    assert result.quality is None or result.quality >= 62
    assert result.target_bytes == int(target * 1_000_000)


def test_large_miss_never_tries_quality_below_30(tmp_path, monkeypatch):
    source = color_control_pdf(tmp_path / "far.pdf")
    trial_q: list[int] = []
    real = pdf_engine.build_candidate

    def traced_candidate(*args, **kwargs):
        if kwargs.get("quality") is not None:
            trial_q.append(kwargs["quality"])
        return real(*args, **kwargs)

    monkeypatch.setattr(pdf_engine, "build_candidate", traced_candidate)
    result = compress_pdf(source, tmp_path / "out",
                          mode="target", target_mb=0.01)
    assert not result.target_met
    assert all(q >= 30 for q in trial_q)
    assert result.target_bytes == 10_000
