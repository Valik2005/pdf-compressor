"""Unit checks for exact PyInstaller Analysis collection origin evidence."""
import hashlib
import json
from pathlib import Path

import pytest

from tools.audit_native_collection_sources_28 import capture, load_recipient_qt_replacements


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


@pytest.mark.parametrize(("relative", "scope"), [
    ("Git/mingw64/bin/libcrypto-3-x64.dll", "installed-program"),
    ("Windows Kits/10/Redist/ucrt/DLLs/x64/ucrtbase.dll", "windows-sdk"),
])
def test_provenance_preserves_only_safe_program_files_relative_path(
        tmp_path, monkeypatch, relative, scope):
    program_files = tmp_path / "Program Files"
    file = program_files / relative
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_bytes(b"MZ" + bytes(range(32)))
    monkeypatch.setenv("ProgramFiles", str(program_files))
    monkeypatch.setenv("ProgramFiles(x86)", str(tmp_path / "unused-x86"))
    out = tmp_path / "provenance.json"
    info = capture([(file.name, str(file), "BINARY")], [], out, known={})
    row = info["entries"][0]
    assert row["source_scope"] == scope
    assert row["source_relative_path"] == relative
    assert str(tmp_path) not in out.read_text(encoding="utf-8")
    assert "Program Files" not in row["source_relative_path"]


def test_recipient_qt_override_is_explicit_and_sha_pinned(tmp_path):
    qt_file = native(tmp_path, name="Qt6Widgets.dll", data=b"MZ-modified-Qt-resource")
    modified_sha = hashlib.sha256(qt_file.read_bytes()).hexdigest()
    original_sha = hashlib.sha256(b"MZ-original-Qt-wheel").hexdigest()
    wheel = {qt_file.resolve(): {
        "scope": "installed-wheel", "distribution": "PySide6_Essentials",
        "version": "6.12.0", "relative_path": "PySide6/Qt6Widgets.dll",
        "record_sha256": original_sha,
    }}
    entry = ("PySide6/Qt6Widgets.dll", str(qt_file), "BINARY")
    out = tmp_path / "native-collection.json"
    with pytest.raises(ValueError, match="RECORD"):
        capture([entry], [], out, known=wheel)
    manifest = {
        "schema_version": 1, "scope": "recipient-relink",
        "recipient_modified_qt_libraries": [
            {"path": "PySide6/Qt6Widgets.dll",
             "original_sha256": original_sha,
             "replacement_sha256": modified_sha}
        ],
    }
    manifest_file = tmp_path / "recipient-qt.json"
    manifest_file.write_text(json.dumps(manifest), encoding="utf-8")
    approved = load_recipient_qt_replacements(manifest_file)
    result = capture([entry], [], out, known=wheel,
                     recipient_qt_replacements=approved)
    assert result["recipient_qt_relink"] is True
    assert result["recipient_modified_qt_count"] == 1
    assert result["entries"][0]["recipient_modified_qt"] is True
    assert result["entries"][0]["wheel_record_matched"] is False
    assert result["entries"][0]["source_sha256"] == modified_sha
    assert result["redistribution_rights_verified"] is False
    assert str(tmp_path) not in out.read_text(encoding="utf-8")

    tampered = dict(approved["PySide6/Qt6Widgets.dll"])
    tampered["replacement_sha256"] = "f" * 64
    with pytest.raises(ValueError, match="replacement mismatch"):
        capture([entry], [], out, known=wheel,
                recipient_qt_replacements={"PySide6/Qt6Widgets.dll": tampered})
    tampered = dict(approved["PySide6/Qt6Widgets.dll"])
    tampered["original_sha256"] = "f" * 64
    with pytest.raises(ValueError, match="replacement mismatch"):
        capture([entry], [], out, known=wheel,
                recipient_qt_replacements={"PySide6/Qt6Widgets.dll": tampered})
    with pytest.raises(ValueError, match="missing native members"):
        capture([entry], [], out, known=wheel, recipient_qt_replacements={
            **approved,
            "PySide6/Qt6Missing.dll": {"original_sha256": original_sha,
                                         "replacement_sha256": modified_sha},
        })


@pytest.mark.parametrize("bad_path", [
    "Qt6Widgets.dll", "PySide6/../other.dll",
    "PySide6/Qt6Widgets.txt", "PySide6/Qt6Widgets\\\\.dll",
])
def test_relink_override_manifest_rejects_unsafe_locations(tmp_path, bad_path):
    manifest = {
        "schema_version": 1, "scope": "recipient-relink",
        "recipient_modified_qt_libraries": [{
            "path": bad_path, "original_sha256": "a" * 64,
            "replacement_sha256": "b" * 64
        }],
    }
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError, match="Unsafe"):
        load_recipient_qt_replacements(path)


def test_relink_manifest_rejects_false_shas_and_duplicates(tmp_path):
    good = {"path": "PySide6/Qt6Widgets.dll",
            "original_sha256": "a" * 64,
            "replacement_sha256": "b" * 64}
    for records in [
        [dict(good, replacement_sha256="z" * 64)],
        [dict(good, original_sha256="b" * 64)],
        [good, good],
    ]:
        doc = {"schema_version": 1, "scope": "recipient-relink",
               "recipient_modified_qt_libraries": records}
        path = tmp_path / "manifest.json"
        path.write_text(json.dumps(doc), encoding="utf-8")
        with pytest.raises(ValueError):
            load_recipient_qt_replacements(path)
