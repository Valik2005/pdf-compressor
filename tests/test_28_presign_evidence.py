"""Synthetic pre-sign audit fixtures; never assume an unsigned EXE is signed."""
import hashlib
import json
import zipfile
import zlib

import pytest

from tools.audit_native_binary_origin_28 import MAGIC, COOKIE, TOC
from tools.verify_presign_evidence_28 import PINS, NOTICES, validate


def dump(folder, name, data):
    (folder / name).write_text(json.dumps(data), encoding="utf-8")


def native_fixture_exe(path):
    """Build a small but structurally valid CArchive with 120 native files."""
    payload, toc, records = bytearray(), bytearray(), []
    for i in range(120):
        name = f"module_{i:03d}.pyd"
        original = b"MZ" + bytes([i]) * (i % 7 + 5)
        compressed = zlib.compress(original)
        name_bytes = name.encode("utf-8") + bytes([0])
        toc.extend(TOC.pack(TOC.size + len(name_bytes), len(payload),
                            len(compressed), len(original), 1, b"b"))
        toc.extend(name_bytes)
        payload.extend(compressed)
        records.append({
            "name": name, "sha256": hashlib.sha256(original).hexdigest(),
            "size_bytes": len(original), "matched_installed_origins": [],
            "status": "unverified-build-origin",
        })
    size = len(payload) + len(toc) + COOKIE.size
    cookie = COOKIE.pack(MAGIC, size, len(payload), len(toc), 314,
                         b"python314.dll".ljust(64, bytes([0])))
    path.write_bytes(b"MZ" + bytes(500) + payload + toc + cookie)
    return records


def fixture(tmp_path):
    windows, sources = tmp_path / "windows", tmp_path / "sources"
    windows.mkdir()
    sources.mkdir()
    commit = "a" * 40
    exe = windows / "PDF_Compressor_2_8.exe"
    native_records = native_fixture_exe(exe)
    digest = hashlib.sha256(exe.read_bytes()).hexdigest()
    dump(windows, "build-manifest.json", {
        "source_git_commit": commit, "source_has_local_changes": False,
        "exe_name": exe.name, "exe_size_bytes": exe.stat().st_size,
        "exe_sha256": digest, "builder_os": "Windows", "builder_python": "3.14.10",
        "installed_builder_package_versions": PINS,
    })
    dump(windows, "bundle-audit.json", {
        "sha256": digest, "included_virtual_keyboard_files": [],
        "all_entries": [{"name": r["name"]} for r in native_records],
    })
    dump(windows, "native-source-mapping.json", {
        "exe_sha256": digest, "native_file_count": 120,
        "unmapped_native_files": [], "missing_required_source_entries": [],
        "component_counts": {"Python runtime": 120},
        "native_component_mapping": [
            {"path": r["name"], "component": "Python runtime"} for r in native_records
        ],
        "open_manual_review_components": [{"component": "Python runtime", "review": "Manual"}],
    })
    dump(windows, "native-binary-origin.json", {
        "schema_version": 1, "source_git_commit": commit,
        "exe_sha256": digest, "native_file_count": 120,
        "matched_count": 0, "unmatched_wheel_entries": [],
        "installed_wheel_record_mismatches": [],
        "redistribution_rights_verified": False, "entries": native_records,
    })
    with zipfile.ZipFile(windows / "license-evidence.zip", "w") as z:
        pillow_codec_sections = (
            "libavif-1.4.2 libjpeg-turbo-3.1.4.1 libpng-1.6.58 "
            "libwebp-1.6.0 openjpeg-2.5.4 tiff-4.7.1 "
            "freetype-2.14.3 lcms2-2.19.1 harfbuzz-14.2.1 "
            "brotli-1.2.0 zlib-ng-2.3.3"
        )
        z.writestr(
            "packages/Pillow/12.3.0/pillow-12.3.0.dist-info/licenses/LICENSE",
            (pillow_codec_sections + "\n") * 450,
        )
        z.writestr("evidence-report.json", json.dumps({
            "exe_name": exe.name, "exe_sha256": digest,
            "missing": ["Third-party relinking rights require final review"]
        }))
    entries, downloaded, audited = [], [], []
    for i in range(6):
        name = f"test{i}.tar.gz"
        contents = (f"source-file-{i}").encode() * 100
        (sources / name).write_bytes(contents)
        h = hashlib.sha256(contents).hexdigest()
        key = f"component-{i}"
        entries.append({"id": key, "required": True, "filename": name, "expected_sha256": h})
        downloaded.append({"id": key, "status": "hash_matches_official_source",
                           "trusted_expected_sha256": h, "downloaded_sha256": h})
        audited.append({"id": key, "status": "hash_matches_published_value",
                        "local_sha256": h})
    catalog = tmp_path / "source-catalog.json"
    catalog.write_text(json.dumps({"schema_version": 1, "release": "PDF Compressor 2.8",
                                   "entries": entries}))
    dump(sources, "source-download-report.json", {
        "all_required_archives_verified": True, "archives": downloaded})
    dump(sources, "source-archive-audit.json", {
        "all_required_with_published_hashes": True, "archives": audited})
    with zipfile.ZipFile(sources / "THIRD_PARTY_NOTICES_2_8.zip", "w") as z:
        for name in NOTICES:
            if name != "notice-manifest.json":
                z.writestr(name, b"fixture")
        for i in range(65):
            z.writestr(f"components/other/{i}.txt", b"fixture")
        z.writestr("notice-manifest.json", json.dumps({
            "matching_archive_hashes_verified": True,
            "source_archives": [{"component": r["id"], "sha256": r["expected_sha256"]}
                                for r in entries],
        }))
    for name in ("LGPL_RELINKING_2_8.md", "THIRD_PARTY_NOTICES_2_8.md",
                 "libffi-LICENSE.txt"):
        (sources / name).write_text("License fixture")
    return windows, sources, catalog, commit


def test_complete_presign_evidence_is_technical_not_legal_certification(tmp_path):
    win, source, cat, commit = fixture(tmp_path)
    result = validate(win, source, cat, commit)
    assert result["technical_integrity_checks_passed"] is True
    assert result["license_compliance_certified"] is False
    assert result["source_archives_verified"] == 6
    assert result["third_party_license_records"] >= 65
    assert result["installed_package_evidence_missing_or_incomplete"]


@pytest.mark.parametrize("change", [
    "alter_windows", "alter_archive", "wrong_version", "bad_license_proof",
    "no_notice", "wrong_source_revision", "unmapped_native", "bad_download",
    "native_origin_wrong_sha", "native_origin_unmatched_wheel",
    "native_origin_empty_entries", "native_origin_forged_member_hash",
    "native_origin_repeated_member", "native_origin_forged_match_count",
    "native_source_mapping_missing_member", "bundle_inventory_member_missing",
    "native_origin_false_wheel_match", "missing_pillow_notices",
])
def test_fail_closed_on_bad_real_component_evidence(tmp_path, change):
    win, source, cat, commit = fixture(tmp_path)
    if change == "alter_windows":
        (win / "PDF_Compressor_2_8.exe").write_bytes(b"tamper")
    elif change == "alter_archive":
        (source / "test2.tar.gz").write_bytes(b"tamper")
    elif change == "wrong_version":
        p=win / "build-manifest.json"
        j=json.loads(p.read_text())
        j["installed_builder_package_versions"]["PySide6"] = "6.11.0"
        p.write_text(json.dumps(j))
    elif change == "bad_license_proof":
        p=win / "license-evidence.zip"
        with zipfile.ZipFile(p,"w") as z:
            z.writestr("evidence-report.json", json.dumps({"exe_sha256":"0"*64}))
    elif change == "no_notice":
        (source / "THIRD_PARTY_NOTICES_2_8.zip").unlink()
    elif change == "wrong_source_revision":
        commit="b"*40
    elif change == "missing_pillow_notices":
        p = win / "license-evidence.zip"
        with zipfile.ZipFile(p, "w") as z:
            z.writestr("evidence-report.json", json.dumps({
                "exe_name": "PDF_Compressor_2_8.exe", "exe_sha256":
                hashlib.sha256((win / "PDF_Compressor_2_8.exe").read_bytes()).hexdigest(),
            }))
    elif change.startswith("native_origin_"):
        p = win / "native-binary-origin.json"
        j = json.loads(p.read_text())
        if change == "native_origin_wrong_sha":
            j["exe_sha256"] = "f" * 64
        elif change == "native_origin_unmatched_wheel":
            j["unmatched_wheel_entries"] = ["PySide6/Qt6Core.dll"]
        elif change == "native_origin_empty_entries":
            j["entries"] = []
        elif change == "native_origin_forged_member_hash":
            j["entries"][0]["sha256"] = "f" * 64
        elif change == "native_origin_repeated_member":
            j["entries"][1]["name"] = j["entries"][0]["name"]
        elif change == "native_origin_forged_match_count":
            j["matched_count"] = 20
        else:
            j["entries"][0]["status"] = "byte-identical"
            j["entries"][0]["matched_installed_origins"] = [
                {"sha256": "f" * 64, "wheel_record_matches_installed_file": True}
            ]
            j["matched_count"] = 1
        p.write_text(json.dumps(j))
    elif change == "native_source_mapping_missing_member":
        p = win / "native-source-mapping.json"
        j = json.loads(p.read_text())
        j["native_component_mapping"].pop()
        p.write_text(json.dumps(j))
    elif change == "bundle_inventory_member_missing":
        p = win / "bundle-audit.json"
        j = json.loads(p.read_text())
        j["all_entries"].pop()
        p.write_text(json.dumps(j))
    elif change == "unmapped_native":
        p=win / "native-source-mapping.json"
        j=json.loads(p.read_text())
        j["unmapped_native_files"]=["unknown.dll"]
        p.write_text(json.dumps(j))
    else:
        p=source/"source-download-report.json"
        j=json.loads(p.read_text())
        j["archives"][0]["trusted_expected_sha256"]="f"*64
        p.write_text(json.dumps(j))
    with pytest.raises((ValueError, FileNotFoundError, KeyError, zipfile.BadZipFile)):
        validate(win, source, cat, commit)
