"""Regression tests for external Qt library layout checks."""
import importlib.util
from pathlib import Path
import sys

import pytest


def load():
    path = Path(__file__).resolve().parents[1] / "tools" / "verify_onedir_bundle.py"
    spec = importlib.util.spec_from_file_location("verify_onedir_bundle", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def fake_bundle(tmp_path, monkeypatch):
    v = load()
    root = tmp_path / v.BUNDLE_NAME
    qt = root / "_internal" / "PySide6"
    qt.mkdir(parents=True)
    (root / (v.BUNDLE_NAME + ".exe")).write_bytes(b"synthetic PE fixture")
    for dll in v.REQUIRED_DLLS:
        (qt / dll).write_bytes(b"synthetic dll")
    plugin = qt / "plugins" / "platforms"
    plugin.mkdir(parents=True)
    (plugin / "qwindows.dll").write_bytes(b"synthetic plugin")
    class FakeAuditor:
        @staticmethod
        def inspect_executable(path):
            return {"all_entries": [{"name": "base_library.zip"}]}
    monkeypatch.setitem(sys.modules, "audit_pyinstaller_bundle", FakeAuditor)
    return root, v


def test_valid_external_dlls_reported(tmp_path, monkeypatch):
    root, v = fake_bundle(tmp_path, monkeypatch)
    result = v.verify(root)
    assert result["external_qt_dll_count"] == 4
    assert result["virtual_keyboard_files"] == []
    assert "NOT CERTIFIED" in result["status"]
    assert result["schema_version"] == 2
    assert result["native_binary_count"] == 5
    manifest = result["native_binary_manifest"]
    assert len({item["path"] for item in manifest}) == 5
    assert all(len(item["sha256"]) == 64 for item in manifest)
    assert all(item["size_bytes"] > 0 for item in manifest)
    assert result["optional_qt_module_observations"]["qt_qml"] == []


def test_missing_qt_core_fails(tmp_path, monkeypatch):
    root, v = fake_bundle(tmp_path, monkeypatch)
    (root / "_internal" / "PySide6" / "Qt6Core.dll").unlink()
    with pytest.raises(ValueError, match="Qt6Core.dll"):
        v.verify(root)


def test_virtual_keyboard_fails(tmp_path, monkeypatch):
    root, v = fake_bundle(tmp_path, monkeypatch)
    (root / "_internal" / "PySide6" / "Qt6VirtualKeyboard.dll").write_bytes(b"x")
    with pytest.raises(ValueError, match="Virtual Keyboard"):
        v.verify(root)


def test_embedded_pyside_binary_fails(tmp_path, monkeypatch):
    root, v = fake_bundle(tmp_path, monkeypatch)
    class FakeAuditor:
        @staticmethod
        def inspect_executable(path):
            return {"all_entries": [{"name": "PySide6/Qt6Core.dll"}]}
    monkeypatch.setitem(sys.modules, "audit_pyinstaller_bundle", FakeAuditor)
    with pytest.raises(ValueError, match="inside EXE"):
        v.verify(root)


def test_native_inventory_hash_changes_with_dll_content(tmp_path, monkeypatch):
    root, v = fake_bundle(tmp_path, monkeypatch)
    before = v.verify(root)
    target = "_internal/PySide6/Qt6Core.dll"
    first = next(item for item in before["native_binary_manifest"] if item["path"] == target)
    (root / target).write_bytes(b"modified compatible dll fixture")
    after = v.verify(root)
    second = next(item for item in after["native_binary_manifest"] if item["path"] == target)
    assert first["sha256"] != second["sha256"]
    assert first["size_bytes"] != second["size_bytes"]
    assert before["exe_sha256"] == after["exe_sha256"]


def test_native_inventory_records_nested_pyd(tmp_path, monkeypatch):
    root, v = fake_bundle(tmp_path, monkeypatch)
    binding = root / "_internal" / "extension" / "native.pyd"
    binding.parent.mkdir(parents=True)
    binding.write_bytes(b"native binding fixture")
    result = v.verify(root)
    assert result["native_binary_count"] == 6
    assert any(item["path"] == "_internal/extension/native.pyd"
               for item in result["native_binary_manifest"])
