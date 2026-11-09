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
