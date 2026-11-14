"""Unit checks for exact PyInstaller Analysis collection origin evidence."""
import hashlib
import json
from pathlib import Path

import pytest

from tools.audit_native_collection_sources_28 import capture


def native(tmp_path, name="Qt6Gui.dll", data=b"MZ-Qt-test-dll"):
    f = tmp_path / name
    f.write_bytes(data)
    return f


def test_capture_real_analysis_file_bytes_without_absolute_paths(tmp_path):
    f = native(tmp_path)
    out = tmp_path / "native-collection-sources.json"
    report = capture([("PySide6/Qt6Gui.dll", str(f), "BINARY")], [], out,
                     "a" * 40, known={})
    assert report["native_file_count"] == 1
    assert report["redistribution_rights_verified"] is False
    row = report["entries"][0]
    assert row["source_sha256"] == hashlib.sha256(f.read_bytes()).hexdigest()
    assert row["size_bytes"] == f.stat().st_size
    assert row["source_scope"] == "unclassified-builder-path"
    assert str(tmp_path) not in out.read_text(encoding="utf-8")
    assert json.loads(out.read_text(encoding="utf-8")) == report


def test_capture_checks_installed_wheel_record_source_bytes(tmp_path):
    f = native(tmp_path)
    expected = hashlib.sha256(f.read_bytes()).hexdigest()
    wheel = {f.resolve(): {
        "scope": "installed-wheel", "distribution": "PySide6_Essentials",
        "version": "6.12.0", "relative_path": "PySide6/Qt6Gui.dll",
        "record_sha256": expected,
    }}
    out = tmp_path / "report.json"
    data = capture([("PySide6/Qt6Gui.dll", str(f), "BINARY")], [], out,
                   "b" * 40, known=wheel)
    assert data["entries"][0]["wheel_record_matched"] is True
    assert data["source_scope_counts"] == {"installed-wheel": 1}
    wheel[f.resolve()]["record_sha256"] = "f" * 64
    with pytest.raises(ValueError, match="RECORD"):
        capture([("PySide6/Qt6Gui.dll", str(f), "BINARY")], [], out,
                "b" * 40, known=wheel)


@pytest.mark.parametrize("bad_dest", ["/root/evil.dll", "../evil.dll", "a/../evil.dll"])
def test_capture_rejects_unsafe_archive_member(tmp_path, bad_dest):
    f = native(tmp_path)
    with pytest.raises(ValueError, match="unsafe"):
        capture([(bad_dest, str(f), "BINARY")], [], tmp_path / "r.json",
                known={})


def test_capture_rejects_duplicate_and_missing_source(tmp_path):
    f = native(tmp_path)
    data = [("Qt6Gui.dll", str(f), "BINARY")]
    with pytest.raises(ValueError, match="Duplicate"):
        capture(data, data, tmp_path / "r.json", known={})
    with pytest.raises(ValueError, match="Invalid collected"):
        capture([("missing.dll", str(tmp_path / "absent.dll"), "BINARY")],
                [], tmp_path / "r.json", known={})
