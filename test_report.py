# -*- coding: utf-8 -*-
"""Offline test-session recorder embedded in PDF Compressor 2.8.1 Testing.

Only *filenames* and numerical processing metadata are stored, never PDF
contents, screenshots, full input/output paths, or document text. No network.
"""
from __future__ import annotations

import csv
from datetime import datetime
from html import escape
from io import StringIO
import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
import uuid
import zipfile

SCHEMA_VERSION = 1
REPORT_ID = "pdf-compressor-test-session"
MAX_RECORDS_EXPORT = 100_000
FIELDS = (
    "run_id", "session_id", "version",
    "started_at", "finished_at",
    "source_name", "result_name", "source_pages",
    "mode", "target_bytes", "target_met", "over_target_bytes",
    "source_bytes", "result_bytes", "saved_bytes", "saving_percent",
    "elapsed_seconds", "quality_elapsed_seconds",
    "jpeg_quality", "downscaled", "candidate_attempts",
    "quality_status", "quality_issue_codes", "status", "error_type",
)


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def fresh_id() -> str:
    return uuid.uuid4().hex


def _basename(value) -> str:
    # Windows paths on a Linux test runner are parsed as well.
    return str(value or "").replace("\\", "/").rsplit("/", 1)[-1][:180]


def sanitize_record(record: dict) -> dict:
    """Allowlist only report fields; refuse embedding absolute paths or PDF."""
    output = {key: record.get(key) for key in FIELDS}
    output["source_name"] = _basename(output["source_name"])
    output["result_name"] = _basename(output["result_name"])
    output["quality_issue_codes"] = sorted(set(
        str(code)[:80] for code in (output["quality_issue_codes"] or [])
    ))
    output["error_type"] = (
        str(output["error_type"])[:80] if output["error_type"] else None
    )
    # Exact numbers are needed to avoid rounding mistakes in target checks.
    for key in ("source_bytes", "result_bytes", "target_bytes",
                "over_target_bytes", "saved_bytes", "source_pages",
                "jpeg_quality", "candidate_attempts"):
        if output[key] is not None:
            output[key] = int(output[key])
    for key in ("elapsed_seconds", "quality_elapsed_seconds", "saving_percent"):
        if output[key] is not None:
            output[key] = round(float(output[key]), 6)
    if output["target_met"] is not None:
        output["target_met"] = bool(output["target_met"])
    if output["downscaled"] is not None:
        output["downscaled"] = bool(output["downscaled"])
    return output


def _summary(rows: list[dict]) -> dict:
    counts: dict[str, int] = {}
    for row in rows:
        key = row.get("status") or "unknown"
        counts[key] = counts.get(key, 0) + 1
    return {
        "runs": len(rows),
        "by_status": counts,
        "total_input_bytes": sum(row["source_bytes"] or 0 for row in rows),
        "total_output_bytes": sum(row["result_bytes"] or 0 for row in rows),
        "total_compression_seconds": round(
            sum(row["elapsed_seconds"] or 0 for row in rows), 6),
    }


def _csv_data(rows: list[dict]) -> bytes:
    stream = StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\r\n")
    writer.writeheader()
    for record in rows:
        row = dict(record)
        row["quality_issue_codes"] = "; ".join(record["quality_issue_codes"])
        for key in FIELDS:
            if row[key] is None:
                row[key] = ""  # empty is N/A; false is the literal False
        # Excel treats untrusted names beginning =, +, - or @ as
        # formulas. Prefix the displayed CSV cell only; JSON preserves
        # the real filename unchanged for programmatic comparison.
        for key in ("source_name", "result_name"):
            val = row[key]
            if isinstance(val, str) and val.lstrip().startswith(("=", "+", "-", "@")):
                row[key] = "'" + val
        writer.writerow(row)
    return stream.getvalue().encode("utf-8-sig")


def _html_data(rows: list[dict], summary: dict) -> bytes:
    columns = ("source_name", "mode", "source_bytes", "result_bytes",
               "saving_percent", "target_bytes", "target_met",
               "elapsed_seconds", "quality_status", "status")
    labels = ("Исходный PDF", "Режим", "До (байт)", "После (байт)",
              "Сжатие (%)", "Цель (байт)", "Цель достигнута",
              "Время (сек)", "Качество", "Статус")
    head = "".join("<th>"+escape(label)+"</th>" for label in labels)
    rows_html = "".join(
        "<tr>" + "".join(
            "<td>" + escape("—" if record[k] is None else str(record[k]))
            + "</td>" for k in columns
        ) + "</tr>" for record in rows
    )
    page = (
        '<!doctype html><html lang="ru"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>PDF Compressor — отчёт тестирования</title>'
        '<style>body{font:14px Segoe UI,Arial,sans-serif;max-width:1400px;'
        'margin:35px auto;padding:0 20px;color:#223}table{border-collapse:'
        'collapse;width:100%}td,th{border:1px solid #ccd;padding:7px;'
        'text-align:left}th{background:#eef}tr:nth-child(even){background:'
        '#f8f9fc}p{line-height:1.5}</style>'
        '<h1>PDF Compressor — отчёт тестирования</h1>'
        f'<p>Всего обработок: {summary["runs"]}. '
        'Данные записаны локально. Размеры — в байтах, время — в секундах. '
        'Отчёт не включает текст и изображения PDF, полные пути или пароли.</p>'
        '<div style="overflow-x:auto"><table><thead><tr>'
        + head + '</tr></thead><tbody>' + rows_html + '</tbody></table></div>'
        '</html>'
    )
    return page.encode("utf-8")


class TestReportStore:
    """An append-only history, independent of GUI and compression engine."""
    __test__ = False  # pytest must not collect a helper from test_report.py

    def __init__(self, directory: str | Path):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.journal = self.directory / "test_history.jsonl"
        self.session_id = fresh_id()

    def append(self, record: dict) -> None:
        """Write one terminal result using a single buffered append operation."""
        sanitized = sanitize_record(record)
        data = json.dumps(sanitized, ensure_ascii=False, separators=(",", ":"))
        with self.journal.open("a+b") as writer:
            # A power outage may leave an incomplete final line. Keep that
            # line separate so the next valid run remains recoverable.
            writer.seek(0, os.SEEK_END)
            if writer.tell():
                writer.seek(-1, os.SEEK_END)
                if writer.read(1) != b"\n":
                    writer.write(b"\n")
            writer.write((data + "\n").encode("utf-8"))

    def records(self) -> list[dict]:
        if not self.journal.is_file():
            return []
        result: list[dict] = []
        with self.journal.open(encoding="utf-8") as reader:
            for line in reader:
                try:
                    obj = json.loads(line)
                    if isinstance(obj, dict) and obj.get("run_id"):
                        result.append(sanitize_record(obj))
                except (ValueError, TypeError):
                    # A crash during the final write may leave a partial line.
                    # Preserve all earlier valid records without losing history.
                    continue
        return result

    def clear(self) -> None:
        """Explicit user action only. Never silently clear on launch/export."""
        self.journal.unlink(missing_ok=True)

    def export(self, destination: str | Path) -> int:
        rows = self.records()
        if not rows:
            raise ValueError("История тестов пуста")
        if len(rows) > MAX_RECORDS_EXPORT:
            raise ValueError("Слишком много записей для одного архива")
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        document = {
            "schema": REPORT_ID,
            "schema_version": SCHEMA_VERSION,
            "exported_at": now_iso(),
            "summary": _summary(rows),
            "runs": rows,
        }
        archive_bytes = (
            json.dumps(document, ensure_ascii=False, indent=2) + "\n"
        ).encode("utf-8")
        with NamedTemporaryFile(prefix=".report-", suffix=".zip",
                                dir=destination.parent, delete=False) as temp:
            staged = Path(temp.name)
        try:
            with zipfile.ZipFile(staged, "w", zipfile.ZIP_DEFLATED) as archive:
                archive.writestr("test_report.json", archive_bytes)
                archive.writestr("test_report.csv", _csv_data(rows))
                archive.writestr("test_report.html",
                                 _html_data(rows, document["summary"]))
                archive.writestr("README.txt",
                                 "PDF Compressor 2.8.1 Testing\n"
                                 "The exported ZIP contains automatic, local "
                                 "test metadata only.\n"
                                 "CSV uses UTF-8 BOM for Excel; numeric sizes "
                                 "are exact bytes, time is seconds.\n")
            os.replace(staged, destination)
        finally:
            staged.unlink(missing_ok=True)
        return len(rows)
