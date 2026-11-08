"""Fault-injection tests for safe PyInstaller one-file CArchive inspection."""
import importlib.util
from pathlib import Path

import pytest


def load_auditor():
    src = Path(__file__).resolve().parents[1] / "tools" / "audit_pyinstaller_bundle.py"
    spec = importlib.util.spec_from_file_location("audit_pyinstaller_bundle", src)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fake_archive(path, filenames):
    auditor = load_auditor()
    payload = b"file-payload"
    toc = bytearray()
    for filename in filenames:
        name = filename.encode("utf-8") + b"\x00"
        length = auditor.TOC_ENTRY.size + len(name)
        toc += auditor.TOC_ENTRY.pack(length, 0, len(payload), len(payload), 0, b"b") + name
    cookie = auditor.COOKIE.pack(
        auditor.MAGIC,
        len(payload) + len(toc) + auditor.COOKIE.size,
        len(payload),
        len(toc),
        314,
        b"python314.dll",
    )
    path.write_bytes(b"MZ" + payload + toc + cookie)
    return path


def test_virtual_keyboard_detection(tmp_path):
    auditor = load_auditor()
    path = fake_archive(tmp_path / "sample.exe", [
        "PySide6/Qt6VirtualKeyboard.dll",
        "PySide6\\plugins\\platforminputcontexts\\qtvirtualkeyboardplugin.dll",
        "PySide6/Qt6Core.dll",
    ])
    result = auditor.inspect_executable(path)
    assert len(result["included_virtual_keyboard_files"]) == 2
    assert result["archive_items"] == 3
    assert "PySide6/Qt6Core.dll" in result["qt_dlls"]


def test_clean_archive_has_no_virtual_keyboard(tmp_path):
    auditor = load_auditor()
    path = fake_archive(tmp_path / "sample.exe", ["PySide6/Qt6Core.dll"])
    assert auditor.inspect_executable(path)["included_virtual_keyboard_files"] == []


def test_corrupted_archive_is_rejected(tmp_path):
    auditor = load_auditor()
    path = tmp_path / "bad.exe"
    path.write_bytes(b"MZ" * 300)
    with pytest.raises(ValueError, match="cookie"):
        auditor.inspect_executable(path)
