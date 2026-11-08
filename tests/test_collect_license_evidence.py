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

def test_short_commercial_license_reference_is_not_accepted_as_lgpl(tmp_path, monkeypatch):
    mod = module()
    exe = tmp_path / "test.exe"
    exe.write_bytes(b"test exe")
    lic = tmp_path / "LICENSE"
    lic.write_text("AGPL test contents")
    class FakeDist:
        version = "6.12.0"
        files = [Path("PySide6-6.12.0.dist-info/licenses/LicenseRef-Qt-Commercial.txt")]
        def locate_file(self, path):
            return tmp_path / str(path)
    location = tmp_path / str(FakeDist.files[0])
    location.parent.mkdir(parents=True)
    location.write_text("Licensees holding valid commercial Qt licenses may use this software.")

    def fake_dist(name):
        if name == "PySide6":
            return FakeDist()
        raise mod.metadata.PackageNotFoundError(name)

    monkeypatch.setattr(mod.metadata, "distribution", fake_dist)
    result = mod.collect(exe, lic, None, tmp_path / "evidence.zip")
    assert result["packages"]["PySide6"]["documents"] == 1
    assert result["license_text_assessment"]["PySide6"]["full_gnu_copyleft_text_found_in_package"] is False
    assert any("PySide6: full community LGPL/GPL" in gap for gap in result["missing"])
    assert any("replacement/relinking" in gap for gap in result["missing"])
