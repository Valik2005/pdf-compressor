"""2.8.1 local report history/ZIP export: precise, private, persistent."""
from __future__ import annotations

import csv
from io import StringIO
import json
from pathlib import Path
import zipfile

import pytest

from test_report import FIELDS, TestReportStore, fresh_id, now_iso, sanitize_record


def fake_record(**kwargs):
    return {
        "run_id": fresh_id(),
        "session_id": "session-1",
        "version": "2.8.1-testing",
        "started_at": now_iso(), "finished_at": now_iso(),
        "source_name": r"C:\Secret\Accounting\01_Текст.pdf",
        "result_name": "/home/person/private/result.pdf",
        "source_pages": 12,
        "mode": "target",
        "target_bytes": 1_000_000,
        "target_met": True,
        "over_target_bytes": 0,
        "source_bytes": 5_520_000,
        "result_bytes": 999_000,
        "saved_bytes": 4_521_000,
        "saving_percent": 81.902173913,
        "elapsed_seconds": 0.31415926,
        "quality_elapsed_seconds": 0.13,
        "jpeg_quality": 28,
        "downscaled": False,
        "candidate_attempts": 5,
        "quality_status": "review",
        "quality_issue_codes": ["raster_detail_needs_review"],
        "status": "success",
        "error_type": None,
        "_private_internal_input_path": "TOP SECRET PDF BYTES AND PATH",
        **kwargs,
    }


def test_history_persists_between_app_restarts_and_exports_three_formats(tmp_path):
    store = TestReportStore(tmp_path / "history")
    store.append(fake_record())
    store.append(fake_record(run_id=fresh_id(), result_bytes=1_123_456,
                             target_met=False, over_target_bytes=123456,
                             status="target_not_met"))
    after_restart = TestReportStore(tmp_path / "history")
    rows = after_restart.records()
    assert len(rows) == 2
    assert rows[0]["source_name"] == "01_Текст.pdf"
    assert rows[0]["result_name"] == "result.pdf"
    assert rows[0]["target_met"] is True
    assert rows[1]["target_met"] is False
    assert set(rows[0]) == set(FIELDS)
    assert rows[0]["elapsed_seconds"] == 0.314159
    exported = tmp_path / "REPORT.zip"
    assert after_restart.export(exported) == 2
    with zipfile.ZipFile(exported) as z:
        assert z.testzip() is None
        assert set(z.namelist()) == {"test_report.json", "test_report.csv",
                                    "test_report.html", "README.txt"}
        raw = z.read("test_report.json")
        assert b"TOP SECRET" not in raw
        assert b"Accounting" not in raw
        data = json.loads(raw)
        assert data["schema_version"] == 1
        assert data["summary"]["by_status"]["success"] == 1
        assert data["summary"]["by_status"]["target_not_met"] == 1
        assert data["runs"][0]["target_bytes"] == 1_000_000
        assert data["runs"][1]["over_target_bytes"] == 123456
        csv_bytes = z.read("test_report.csv")
        assert csv_bytes.startswith(b"\xef\xbb\xbf")
        with StringIO(csv_bytes.decode("utf-8-sig")) as stream:
            parsed = list(csv.DictReader(stream))
        assert len(parsed) == 2
        assert parsed[0]["target_met"] == "True"
        assert parsed[1]["target_met"] == "False"
        assert parsed[0]["result_bytes"] == "999000"
        assert "<table>" in z.read("test_report.html").decode("utf-8")


def test_missing_target_and_cancelled_kept_distinct(tmp_path):
    store = TestReportStore(tmp_path)
    store.append(fake_record(run_id="cancelled-run", result_name=None,
                             status="cancelled", result_bytes=None,
                             target_met=None, elapsed_seconds=0.15,
                             error_type=None, quality_status="interrupted"))
    row = store.records()[0]
    assert row["target_met"] is None
    assert row["result_bytes"] is None
    assert row["status"] == "cancelled"
    with zipfile.ZipFile(tmp_path / "cancelled.zip", "w") as tmp_zip:
        pass
    store.export(tmp_path / "cancelled.zip")
    with zipfile.ZipFile(tmp_path / "cancelled.zip") as z:
        csv_row = list(csv.DictReader(
            StringIO(z.read("test_report.csv").decode("utf-8-sig"))))[0]
        assert csv_row["target_met"] == ""
        assert csv_row["result_bytes"] == ""
        assert csv_row["status"] == "cancelled"


def test_empty_export_does_not_create_zip_and_clear_is_explicit(tmp_path):
    store = TestReportStore(tmp_path / "history")
    with pytest.raises(ValueError, match="пуста"):
        store.export(tmp_path / "empty.zip")
    assert not (tmp_path / "empty.zip").exists()
    store.append(fake_record())
    assert len(TestReportStore(tmp_path / "history").records()) == 1
    store.clear()
    assert store.records() == []


def test_incomplete_journal_line_preserves_previous_completed_runs(tmp_path):
    store = TestReportStore(tmp_path)
    store.append(fake_record())
    with store.journal.open("a", encoding="utf-8") as out:
        out.write('{"run_id":"incomplete",')
    assert len(TestReportStore(tmp_path).records()) == 1


def test_html_and_json_escaped_privacy_and_no_source_text(tmp_path):
    store = TestReportStore(tmp_path)
    store.append(fake_record(source_name=r"C:\secret\<img src=x onerror=alert(1)>.pdf",
                             result_name=r"D:\logs\<script>alert(1)</script>.pdf",
                             error_type="PermissionError"))
    store.export(tmp_path / "safe.zip")
    with zipfile.ZipFile(tmp_path / "safe.zip") as z:
        html = z.read("test_report.html").decode()
        assert "<script>" not in html
        assert "<img src=x" not in html
        assert "&lt;img src=x onerror=alert(1)&gt;" in html
        assert r"C:\secret" not in html
        assert "D:\\logs" not in z.read("test_report.json").decode()


def test_windows_and_posix_basename_and_allowlist():
    obj = sanitize_record(fake_record(
        source_name=r"C:\Users\Somebody\secret\sample.pdf",
        result_name="/home/runner/tmp/compressed.pdf"))
    assert obj["source_name"] == "sample.pdf"
    assert obj["result_name"] == "compressed.pdf"
    assert "_private_internal_input_path" not in obj
