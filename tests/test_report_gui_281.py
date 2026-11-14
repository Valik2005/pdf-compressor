"""2.8.1 in-app test report export, persistence, target and QA details."""
from __future__ import annotations

import csv
from io import StringIO
import json
import os
from pathlib import Path
import runpy
import time
import zipfile

import pymupdf
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtWidgets import QApplication  # noqa: E402

from test_report import TestReportStore

APP = Path(__file__).resolve().parents[1] / "app.pyw"


def _text_pdf(path: Path, content: str):
    with pymupdf.open() as doc:
        page = doc.new_page()
        page.insert_text((70, 80), content)
        doc.save(path)
    return path


def _wait(app, win):
    deadline = time.monotonic() + 50
    while win.busy and time.monotonic() < deadline:
        app.processEvents()
        time.sleep(0.02)
    app.processEvents()
    assert not win.busy


def test_gui_auto_log_batch_csv_json_zip_and_reload(tmp_path, monkeypatch):
    monkeypatch.setenv("PDF_COMPRESSOR_REPORT_DIR", str(tmp_path / "history"))
    app = QApplication.instance() or QApplication([])
    ui = runpy.run_path(str(APP), run_name="test_session_gui")
    source_a = _text_pdf(tmp_path / "a.pdf", "First test PDF")
    source_b = _text_pdf(tmp_path / "b.pdf", "Second test PDF")
    output = tmp_path / "outputs"
    win = ui["MainWindow"]()
    try:
        win.show()
        app.processEvents()
        win.quality_check.setChecked(True)
        win.folder_edit.setText(str(output))
        win.mode.setCurrentIndex(win.mode.findData("balanced"))
        win.add_files([str(source_a), str(source_b)])
        assert not win.export_test_btn.isEnabled()
        win.start_btn.click()
        _wait(app, win)
        rows = win.test_report_store.records()
        assert len(rows) == 2
        assert {r["source_name"] for r in rows} == {"a.pdf", "b.pdf"}
        assert {r["status"] for r in rows} == {"success"}
        assert {r["target_met"] for r in rows} == {None}
        assert all(r["elapsed_seconds"] is not None for r in rows)
        assert all(r["quality_elapsed_seconds"] is not None for r in rows)
        assert all(r["quality_status"] == "no_issues_detected" for r in rows)
        assert all(r["result_bytes"] > 0 for r in rows)
        assert all(r["result_name"].endswith(".pdf") for r in rows)
        assert all(r["mode"] == "balanced" for r in rows)
        assert all(r["source_pages"] == 1 for r in rows)
        assert all(r["version"] == "2.8.1-testing" for r in rows)
        assert win.export_test_btn.isEnabled()
        zip_path = tmp_path / "all_tests.zip"
        monkeypatch.setattr(
            ui["QFileDialog"], "getSaveFileName",
            lambda *_args: (str(zip_path), "ZIP (*.zip)"))
        messages = []
        win.info = lambda *args: messages.append(args)
        win.export_test_btn.click()
        assert zip_path.is_file()
        with zipfile.ZipFile(zip_path) as archive:
            assert archive.testzip() is None
            payload = json.loads(archive.read("test_report.json"))
            assert len(payload["runs"]) == 2
            assert payload["summary"]["by_status"]["success"] == 2
            csv_rows = list(csv.DictReader(StringIO(
                archive.read("test_report.csv").decode("utf-8-sig"))))
            assert len(csv_rows) == 2
        assert source_a.read_bytes() and source_b.read_bytes()
    finally:
        win.close()
        app.processEvents()

    # History is retained when the app is closed and reopened.
    again = ui["MainWindow"]()
    try:
        assert len(again.test_report_store.records()) == 2
        assert again.export_test_btn.isEnabled()
    finally:
        again.close()
        app.processEvents()


def test_in_app_reports_multiple_runs_same_pdf_without_overwrite(tmp_path, monkeypatch):
    monkeypatch.setenv("PDF_COMPRESSOR_REPORT_DIR", str(tmp_path / "report"))
    app = QApplication.instance() or QApplication([])
    ui = runpy.run_path(str(APP), run_name="report_repeat_gui")
    win = ui["MainWindow"]()
    source = _text_pdf(tmp_path / "same.pdf", "Same document retested")
    try:
        win.show()
        app.processEvents()
        win.quality_check.setChecked(False)
        win.mode.setCurrentIndex(win.mode.findData("balanced"))
        win.folder_edit.setText(str(tmp_path / "output"))
        win.add_files([str(source)])
        win.start_btn.click()
        _wait(app, win)
        win.start_btn.click()
        _wait(app, win)
        rows = win.test_report_store.records()
        assert len(rows) == 2
        assert rows[0]["source_name"] == rows[1]["source_name"] == "same.pdf"
        assert rows[0]["run_id"] != rows[1]["run_id"]
        assert rows[0]["result_name"] != rows[1]["result_name"]
        assert all(r["quality_status"] == "not_checked" for r in rows)
        assert all(r["elapsed_seconds"] is not None for r in rows)
    finally:
        win.close()
        app.processEvents()


def test_in_app_report_logs_failed_file_and_cancelled_unstarted(tmp_path, monkeypatch):
    monkeypatch.setenv("PDF_COMPRESSOR_REPORT_DIR", str(tmp_path / "report"))
    app = QApplication.instance() or QApplication([])
    ui = runpy.run_path(str(APP), run_name="report_failure_gui")
    win = ui["MainWindow"]()
    src = _text_pdf(tmp_path / "source.pdf", "Simple")
    try:
        win.add_files([str(src)])
        win.active_paths = [str(src.resolve())]
        win._active_action = "compress"
        win._test_runs = {0: {
            "run_id": "manual-failure", "session_id": "S", "version": "2.8.1-testing",
            "started_at": "2026-11-14T12:00:00+02:00", "finished_at": None,
            "source_name": src.name, "result_name": None, "source_pages": 1,
            "mode": "target", "target_bytes": 10_000,
            "target_met": None, "over_target_bytes": None,
            "source_bytes": src.stat().st_size, "result_bytes": None,
            "saved_bytes": None, "saving_percent": None,
            "elapsed_seconds": 0.2, "quality_elapsed_seconds": None,
            "jpeg_quality": None, "downscaled": None,
            "candidate_attempts": None, "quality_status": "pending",
            "quality_issue_codes": [], "status": "processing",
            "error_type": None, "_written": False,
        }}
        win.record_result(0, ValueError("secret local path C:\\Users\\Name\\bad.pdf"))
        rows = win.test_report_store.records()
        assert len(rows) == 1
        assert rows[0]["status"] == "error"
        assert rows[0]["error_type"] == "ValueError"
        assert rows[0]["quality_status"] == "not_checked"
        assert "secret" not in json.dumps(rows)
        win._test_runs = {1: {
            **win._test_runs[0], "run_id": "manual-cancel",
            "started_at": None, "status": "queued", "_written": False,
        }}
        win.pending_end_message = "Операция отменена. Успешно завершено: 0."
        # finalize_thread owns Qt state: use its cancellation branch without
        # accidentally touching the tracked source/output files.
        win.finalize_thread()
        rows = win.test_report_store.records()
        assert len(rows) == 2
        assert rows[1]["status"] == "cancelled"
        assert rows[1]["quality_status"] == "interrupted"
    finally:
        win.close()
        app.processEvents()
