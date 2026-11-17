"""Source coverage is reviewed from actual native member identity, never licenses alone."""
import hashlib
import io
import json
import tarfile
from pathlib import Path
import zipfile

import pytest

from tools.audit_source_coverage_28 import (
    PILLOW_CANDIDATES, PILLOW_LICENSE, analyze,
)


def make_fixture(tmp_path: Path):
    windows, sources = tmp_path / "win", tmp_path / "sources"
    windows.mkdir()
    sources.mkdir()
    source_sha = "a" * 40
    exe_sha = "b" * 64
    rows = [
        ("PIL/_imaging.pyd", "Pillow codecs", "Pillow", "12.3.0"),
        ("libssl-3.dll", "OpenSSL", None, None),
        ("module_000.pyd", "Python runtime", None, None),
    ]
    (windows / "build-manifest.json").write_text(json.dumps({
        "source_git_commit": source_sha, "exe_sha256": exe_sha,
    }))
    (windows / "native-source-mapping.json").write_text(json.dumps({
        "exe_sha256": exe_sha,
        "native_file_count": len(rows),
        "native_component_mapping": [
            {"path": x[0], "component": x[1]} for x in rows
        ],
    }))
    (windows / "native-collection-sources.json").write_text(json.dumps({
        "source_git_commit": source_sha,
        "native_file_count": len(rows),
        "entries": [{
            "path": name, "source_sha256": hashlib.sha256(name.encode()).hexdigest(),
            "source_scope": "installed-wheel" if package else "python-installation",
            "distribution": package, "distribution_version": version,
        } for name, _, package, version in rows],
    }))
    build_script = (
        "from pathlib import Path\n"
        "V = json.loads((Path(__file__).parents[1] / "
        "'.github' / 'dependencies.json').read_text())\n"
    ).encode()
    with tarfile.open(sources / "pillow-12.3.0.tar.gz", "w:gz") as tar:
        entry = tarfile.TarInfo("pillow-12.3.0/winbuild/build_prepare.py")
        entry.size = len(build_script)
        tar.addfile(entry, io.BytesIO(build_script))
    catalog = tmp_path / "catalog.json"
    catalog.write_text(json.dumps({"entries": [{
        "id": "pillow-12.3.0", "filename": "pillow-12.3.0.tar.gz",
        "required": True,
    }]}))
    with zipfile.ZipFile(windows / "license-evidence.zip", "w") as z:
        license_text = "Pillow wheel license\n"
        license_text += "\n".join(
            k + "-" + v for k, v in PILLOW_CANDIDATES.items()
        )
        z.writestr(PILLOW_LICENSE, license_text)
    return windows, sources, catalog


def test_exact_member_report_is_honest_and_explicit(tmp_path):
    win, src, cat = make_fixture(tmp_path)
    report = analyze(win, src, cat)
    assert report["native_file_count"] == 3
    assert {x["member"] for x in report["native_members"]} == {
        "PIL/_imaging.pyd", "libssl-3.dll", "module_000.pyd"
    }
    assert report["complete_corresponding_source_verified"] is False
    assert report["legal_compliance_certified"] is False
    assert report["component_groups_without_separate_source_archives"] == [
        "OpenSSL", "Python runtime"
    ]
    assert len(report["pillow_native_candidate_sources"]) == len(PILLOW_CANDIDATES) + 4
    assert report["native_members"][0]["upstream_source_archive_ids"] == ["pillow-12.3.0"]
    assert report["native_members"][1]["upstream_source_archive_ids"] == []
    assert all(x["full_corresponding_source_verified"] is False
               for x in report["native_members"])


@pytest.mark.parametrize("fault", [
    "missing_source", "bad_component", "bad_native_sha", "duplicate_member",
    "wrong_exe", "wrong_commit", "wheel_notice_missing", "pillow_notice_removed",
    "pillow_source_catalog_missing",
])
def test_source_coverage_refuses_bad_or_unverifiable_evidence(tmp_path, fault):
    win, src, cat = make_fixture(tmp_path)
    if fault == "missing_source":
        (src / "pillow-12.3.0.tar.gz").unlink()
    elif fault == "bad_component":
        p = win / "native-source-mapping.json"
        j = json.loads(p.read_text())
        j["native_component_mapping"][0]["component"] = "QtBase"
        p.write_text(json.dumps(j))
    elif fault == "bad_native_sha":
        p = win / "native-collection-sources.json"
        j = json.loads(p.read_text())
        j["entries"][0]["source_sha256"] = "garbage"
        p.write_text(json.dumps(j))
    elif fault == "duplicate_member":
        p = win / "native-collection-sources.json"
        j = json.loads(p.read_text())
        j["entries"][1]["path"] = j["entries"][0]["path"]
        p.write_text(json.dumps(j))
    elif fault == "wrong_exe":
        p = win / "native-source-mapping.json"
        j = json.loads(p.read_text())
        j["exe_sha256"] = "0" * 64
        p.write_text(json.dumps(j))
    elif fault == "wrong_commit":
        p = win / "native-collection-sources.json"
        j = json.loads(p.read_text())
        j["source_git_commit"] = "0" * 40
        p.write_text(json.dumps(j))
    elif fault == "pillow_source_catalog_missing":
        (src / "pillow-12.3.0.tar.gz").write_bytes(b"bad-source-tar")
    elif fault == "wheel_notice_missing":
        with zipfile.ZipFile(win / "license-evidence.zip", "w") as z:
            z.writestr(PILLOW_LICENSE, "incomplete")
    elif fault == "pillow_notice_removed":
        with zipfile.ZipFile(win / "license-evidence.zip", "w") as z:
            z.writestr("fake/README.txt", "not a license")
    with pytest.raises((ValueError, FileNotFoundError, KeyError, zipfile.BadZipFile, tarfile.TarError)):
        analyze(win, src, cat)


def test_python_only_inventory_does_not_invent_pillow_linkage(tmp_path):
    win, src, cat = make_fixture(tmp_path)
    p = win / "native-source-mapping.json"
    j = json.loads(p.read_text())
    j["native_component_mapping"] = [j["native_component_mapping"][2]]
    j["native_file_count"] = 1
    p.write_text(json.dumps(j))
    p = win / "native-collection-sources.json"
    j = json.loads(p.read_text())
    j["entries"] = [j["entries"][2]]
    j["native_file_count"] = 1
    p.write_text(json.dumps(j))
    (win / "license-evidence.zip").unlink()
    report = analyze(win, src, cat)
    assert report["pillow_native_candidate_sources"] == []
    assert report["native_component_groups"] == ["Python runtime"]


def test_vendor_build_catalog_git_blob_is_required(tmp_path, monkeypatch):
    import tools.audit_source_coverage_28 as coverage
    win, src, cat = make_fixture(tmp_path)
    monkeypatch.setattr(coverage, "PILLOW_UPSTREAM_DEPENDENCY_BLOB", "0" * 40)
    with pytest.raises(ValueError, match="Git blob"):
        analyze(win, src, cat)
