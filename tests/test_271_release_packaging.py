"""Dry-run the three-file patch release packager with tiny synthetic inputs."""
import hashlib
import json
from pathlib import Path
import zipfile

import pytest

from tools.assemble_patch_release import assemble, BUNDLE_NAME, digest


def fixture_assets(tmp_path: Path):
    sources = tmp_path / "sources"
    windows = tmp_path / "windows"
    out = tmp_path / "release"
    sources.mkdir()
    windows.mkdir()
    commit = "a" * 40
    exe_name = "PDF_Compressor_2_7_1.exe"
    exe = windows / exe_name
    exe.write_bytes(b"PDFCOMPRESSOR onefile test fixture" * 128)
    sha = digest(exe)

    catalog = {"entries": []}
    for i in range(6):
        name = f"source-library-{i}.tar.gz"
        archive = sources / name
        archive.write_bytes((f"library-{i}-source" * 50).encode())
        catalog["entries"].append({
            "filename": name, "expected_sha256": digest(archive),
            "required": True,
        })
    catalog_file = tmp_path / "catalog.json"
    catalog_file.write_text(json.dumps(catalog), encoding="utf-8")

    (windows / "build-manifest.json").write_text(json.dumps({
        "exe_name": exe_name, "exe_sha256": sha,
        "exe_size_bytes": exe.stat().st_size,
        "source_git_commit": commit, "source_has_local_changes": False,
    }), encoding="utf-8")
    (windows / "native-source-mapping.json").write_text(json.dumps({
        "exe_sha256": sha, "native_file_count": 118,
        "unmapped_native_files": [], "missing_required_source_entries": [],
    }), encoding="utf-8")
    (windows / "bundle-audit.json").write_text(json.dumps({
        "sha256": sha, "included_virtual_keyboard_files": [],
    }), encoding="utf-8")
    (sources / "source-archive-audit.json").write_text(json.dumps({
        "all_required_with_published_hashes": True,
    }), encoding="utf-8")
    (sources / "source-download-report.json").write_text(json.dumps({
        "all_required_archives_verified": True,
    }), encoding="utf-8")

    for name in ("LGPL_RELINKING_2_7.md", "THIRD_PARTY_NOTICES_2_7.md",
                 "libffi-LICENSE.txt"):
        (sources / name).write_text("Test license document", encoding="utf-8")
    with zipfile.ZipFile(sources / "THIRD_PARTY_NOTICES_2_7.zip", "w") as z:
        for i in range(70):
            z.writestr(f"notice-{i}.txt", "Test legal notice")
    with zipfile.ZipFile(windows / "license-evidence.zip", "w") as z:
        z.writestr("notice.txt", "License data")
        z.writestr("other.txt", "Other data")
    return sources, windows, catalog_file, out, commit


def test_assemble_preserves_third_party_sources_and_only_three_downloads(tmp_path):
    sources, windows, catalog, out, sha = fixture_assets(tmp_path)
    result = assemble(sources, windows, catalog, out, "PDF_Compressor_2_7_1.exe", sha)
    assert result["source_archives"] == 6
    assert {p.name for p in out.iterdir()} == set(result["files"])
    assert result["exe_sha256"] == digest(out / "PDF_Compressor_2_7_1.exe")
    with zipfile.ZipFile(out / BUNDLE_NAME) as z:
        assert len(z.namelist()) == result["third_party_bundle_records"]
        assert len([n for n in z.namelist() if n.startswith("sources/")]) == 6
        for n in ("licenses/THIRD_PARTY_NOTICES_2_7.zip",
                  "licenses/license-evidence.zip",
                  "licenses/LGPL_RELINKING_2_7.md",
                  "reports/build-manifest.json"):
            assert n in z.namelist()
    lines = (out / "SHA256SUMS.txt").read_text().splitlines()
    assert len(lines) == 2
    assert all(len(line.split()[0]) == 64 for line in lines)


def test_invalid_source_sha_blocks_release(tmp_path):
    sources, windows, catalog, out, commit = fixture_assets(tmp_path)
    with pytest.raises(ValueError, match="exact clean source commit"):
        assemble(sources, windows, catalog, out,
                 "PDF_Compressor_2_7_1.exe", "b" * 40)
    assert not out.exists()


def test_corrupted_library_source_blocks_release(tmp_path):
    sources, windows, catalog, out, commit = fixture_assets(tmp_path)
    (sources / "source-library-2.tar.gz").write_bytes(b"tampered")
    with pytest.raises(ValueError, match="Upstream source archive checksum mismatch"):
        assemble(sources, windows, catalog, out,
                 "PDF_Compressor_2_7_1.exe", commit)
    assert not out.exists()


def test_missing_license_blocks_release(tmp_path):
    sources, windows, catalog, out, commit = fixture_assets(tmp_path)
    (sources / "libffi-LICENSE.txt").unlink()
    with pytest.raises(ValueError, match="Required review asset missing"):
        assemble(sources, windows, catalog, out,
                 "PDF_Compressor_2_7_1.exe", commit)
    assert not out.exists()
