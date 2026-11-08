"""Release manifest reproducibility and privacy smoke tests."""
import hashlib
import importlib.util
from pathlib import Path

import pytest


def _module():
    script = Path(__file__).resolve().parents[1] / "tools" / "release_manifest.py"
    spec = importlib.util.spec_from_file_location("release_manifest", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_manifest_records_binary_checksum_and_environment(tmp_path):
    module = _module()
    exe = tmp_path / "preview.exe"
    payload = b"fake-exe-test-payload"
    exe.write_bytes(payload)

    result = module.make_manifest(exe, tmp_path)
    assert result["exe_name"] == exe.name
    assert result["exe_size_bytes"] == len(payload)
    assert result["exe_sha256"] == hashlib.sha256(payload).hexdigest()
    assert "PyMuPDF" in result["installed_builder_package_versions"]
    assert "builder_python" in result
    assert "source_dir" not in result
    assert "username" not in result


def test_manifest_rejects_missing_executable(tmp_path):
    with pytest.raises(FileNotFoundError):
        _module().make_manifest(tmp_path / "missing.exe", tmp_path)
