"""Optional quality checking via the actual PySide6 worker and GUI (offscreen)."""
from __future__ import annotations

import os
from pathlib import Path
import runpy
import time

import pymupdf
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtWidgets import QApplication  # noqa: E402

from pdf_quality import QualityReport


APP = Path(__file__).resolve().parents[1] / "app.pyw"


@pytest.mark.parametrize("enabled", [False, True])
def test_gui_quality_review_is_explicit_and_does_not_damage_output(tmp_path, enabled, monkeypatch):
    app = QApplication.instance() or QApplication([])
    ui = runpy.run_path(str(APP), run_name="qa_preview")
    win = ui["MainWindow"]()
    source = tmp_path / "source.pdf"
    with pymupdf.open() as document:
        page = document.new_page()
        page.insert_text((50, 50), "2.8 optional quality GUI check")
        document.save(source)
    original = source.read_bytes()
    try:
        win.show()
        app.processEvents()
        win.quality_check.setChecked(enabled)
        win.folder_edit.setText(str(tmp_path / "output"))
        win.mode.setCurrentIndex(win.mode.findData("balanced"))
        win.add_files([str(source)])
        assert len(win.entries) == 1
        win.start_btn.click()
        assert win.busy
        deadline = time.monotonic() + 45
        while win.busy and time.monotonic() < deadline:
            app.processEvents()
            time.sleep(0.02)
        assert not win.busy
        app.processEvents()
        entry = win.entries[0]
        output = Path(entry["result_path"])
        assert output.is_file()
        assert source.read_bytes() == original
        assert entry["status"] == "Готово"
        if enabled:
            assert isinstance(entry["quality_report"], QualityReport)
            assert entry["quality_report"].text_checked_pages == 1
            assert "Проверка качества: без замечаний" in entry["result"]
            assert win.export_quality_btn.isEnabled()
            html_path = tmp_path / "manual-quality.html"
            monkeypatch.setattr(ui["QFileDialog"], "getSaveFileName",
                                lambda *_args: (str(html_path), "HTML (*.html)"))
            win.export_quality_btn.click()
            assert html_path.is_file()
            assert "PDF Compressor 2.8" in html_path.read_text(encoding="utf-8")
            json_path = tmp_path / "manual-quality.json"
            monkeypatch.setattr(ui["QFileDialog"], "getSaveFileName",
                                lambda *_args: (str(json_path), "JSON (*.json)"))
            win.export_quality_btn.click()
            assert json_path.is_file()
            assert "\"no_issues_detected\"" in json_path.read_text(encoding="utf-8")
        else:
            assert entry["quality_report"] is None
            assert "Проверка качества" not in entry["result"]
            assert not win.export_quality_btn.isEnabled()
    finally:
        win.close()
        app.processEvents()



def test_target_miss_uses_short_status_and_exact_overage_tooltip(tmp_path):
    app = QApplication.instance() or QApplication([])
    ui = runpy.run_path(str(APP), run_name="target_overage_gui")
    win = ui["MainWindow"]()
    source = tmp_path / "large-text.pdf"
    with pymupdf.open() as document:
        for i in range(120):
            page = document.new_page()
            page.insert_text((60, 70), f"Repeated text page {i:04d} with details", fontsize=12)
        document.save(source)
    try:
        win.show()
        app.processEvents()
        folder = tmp_path / "very" / "long" / "output" / "folder"
        win.folder_edit.setText(str(folder))
        assert win.folder_edit.toolTip() == str(folder)
        win.mode.setCurrentIndex(win.mode.findData("target"))
        win.target.setText("0,01")
        win.quality_check.setChecked(False)
        win.add_files([str(source)])
        win.start_btn.click()
        deadline = time.monotonic() + 45
        while win.busy and time.monotonic() < deadline:
            app.processEvents()
            time.sleep(0.02)
        assert not win.busy
        app.processEvents()
        entry = win.entries[0]
        assert entry["status"] == "Цель не достигнута"
        assert entry["result_path"] and Path(entry["result_path"]).is_file()
        assert win.table.item(0, 2).text() == "Выше лимита"
        assert "выше лимита на" in entry["result"]
        assert "выше лимита на" in win.table.item(0, 2).toolTip()
        assert "выше лимита на" in win.compare_status.toolTip()
        win.language_box.setCurrentIndex(win.language_box.findData("en"))
        app.processEvents()
        assert win.table.item(0, 2).text() == "Over target"
        assert "over target by" in win.table.item(0, 2).toolTip()
        assert win.folder_edit.toolTip() == str(folder)
    finally:
        win.close()
        app.processEvents()



def test_gui_flags_small_scan_detail_risk_without_discarding_output(tmp_path):
    from io import BytesIO
    from PIL import Image

    app = QApplication.instance() or QApplication([])
    ui = runpy.run_path(str(APP), run_name="scan_quality_gui")
    win = ui["MainWindow"]()
    source = tmp_path / "scan-source.pdf"
    image = Image.effect_noise((650, 850), 80).convert("RGB")
    buffer = BytesIO()
    image.save(buffer, "PNG")
    with pymupdf.open() as doc:
        page = doc.new_page(width=595, height=842)
        page.insert_image(page.rect, stream=buffer.getvalue())
        doc.save(source)
    unchanged = source.read_bytes()

    try:
        win.show()
        app.processEvents()
        win.quality_check.setChecked(True)
        win.folder_edit.setText(str(tmp_path / "results"))
        win.mode.setCurrentIndex(win.mode.findData("smallest"))
        win.add_files([str(source)])
        win.start_btn.click()
        deadline = time.monotonic() + 60
        while win.busy and time.monotonic() < deadline:
            app.processEvents()
            time.sleep(0.02)
        assert not win.busy
        app.processEvents()
        entry = win.entries[0]
        assert entry["status"] == "Проверьте PDF"
        assert Path(entry["result_path"]).is_file()
        assert source.read_bytes() == unchanged
        report = entry["quality_report"]
        assert isinstance(report, QualityReport)
        assert report.status == "review"
        assert report.raster_only_pages == 1
        assert report.jpeg_quality_hint == 48
        assert any(issue.code == "raster_detail_needs_review" for issue in report.issues)
        assert any(issue.code == "low_jpeg_detail_risk" for issue in report.issues)
        assert win.export_quality_btn.isEnabled()
    finally:
        win.close()
        app.processEvents()
