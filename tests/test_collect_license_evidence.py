"""Check binary/manifest integrity and evidence-archive disclaimers."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import json
import zipfile

import pytest


def module():
    src = Path(__file__).resolve().parents[1] / "tools" / "collect_license_evidence.py"
    spec = spec_from_file_location("collect_license_evidence", src)
    obj = module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def test_hash_mismatch_is_rejected(tmp_path):
    mod = module()
    exe = tmp_path / "test.exe"
    exe.write_bytes(b"test exe")
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"exe_sha256": "0" * 64, "exe_size_bytes": 8}))
    with pytest.raises(ValueError, match="does not match"):
        mod.collect(exe, tmp_path / "LICENSE", manifest, tmp_path / "out.zip")


def test_report_is_explicitly_incomplete(tmp_path, monkeypatch):
    mod = module()
    exe = tmp_path / "test.exe"
    exe.write_bytes(b"test exe")
    lic = tmp_path / "LICENSE"
    lic.write_text("AGPL test contents")
    def missing(name):
        raise mod.metadata.PackageNotFoundError(name)
    monkeypatch.setattr(mod.metadata, "distribution", missing)
    out = tmp_path / "evidence.zip"
    result = mod.collect(exe, lic, None, out)
    assert result["status"].startswith("INCOMPLETE")
    with zipfile.ZipFile(out) as z:
        assert "application/LICENSE" in z.namelist()
        assert "README.txt" in z.namelist()
        assert json.loads(z.read("evidence-report.json"))["exe_sha256"] == mod.sha256_file(exe)


def test_reject_unsafe_notice_paths():
    mod = module()
    assert not mod.notice_file("../LICENSE")
    assert not mod.notice_file("/licenses/COPYING")
    assert mod.notice_file("abc.dist-info/licenses/LICENSE.md")
