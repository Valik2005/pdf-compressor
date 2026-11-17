"""Offline tests for extra CPython/OpenSSL original-source integrity."""
from __future__ import annotations

import hashlib
import json

import pytest

from tools.fetch_supplemental_sources_28 import (
    acquire, validate_catalog, verify_prepared,
)


def fixture(tmp_path):
    folder = tmp_path / "sources"
    folder.mkdir()
    source_bytes = b"upstream-source-test" * 30
    name = "original-source.tar.gz"
    url = "https://github.com/owner/project/releases/download/test/" + name
    hash_value = hashlib.sha256(source_bytes).hexdigest()
    catalog = tmp_path / "supplemental-catalog.json"
    data = {"schema_version": 1, "entries": [{
        "id": "original-test-source", "version": "1.0.0",
        "filename": name, "url": url, "sha256": hash_value,
    }]}
    catalog.write_text(json.dumps(data))
    (folder / name).write_bytes(source_bytes)
    return catalog, folder, data


def test_uses_locally_hashed_upstream_source_without_network(tmp_path):
    cat, dest, _ = fixture(tmp_path)
    proof = acquire(cat, dest)
    assert proof["source_archives_verified"] == 1
    assert proof["license_compliance_certified"] is False
    (dest / "supplemental-source-report.json").write_text(json.dumps(proof))
    assert verify_prepared(cat, dest)[0]["id"] == "original-test-source"


@pytest.mark.parametrize("fault", [
    "bad_digest", "wrong_report", "no_source", "duplicate",
    "http", "other_host", "traversal", "forged_identity",
])
def test_missing_or_untrusted_supplemental_sources_fail_closed(tmp_path, fault):
    cat, dest, data = fixture(tmp_path)
    report = acquire(cat, dest)
    (dest / "supplemental-source-report.json").write_text(json.dumps(report))
    if fault == "bad_digest":
        (dest / "original-source.tar.gz").write_bytes(b"modified")
    elif fault == "wrong_report":
        report["archives"][0]["sha256"] = "0" * 64
        (dest / "supplemental-source-report.json").write_text(json.dumps(report))
    elif fault == "no_source":
        (dest / "original-source.tar.gz").unlink()
    elif fault == "duplicate":
        data["entries"].append(data["entries"][0].copy())
    elif fault == "http":
        data["entries"][0]["url"] = data["entries"][0]["url"].replace("https:", "http:")
    elif fault == "other_host":
        data["entries"][0]["url"] = data["entries"][0]["url"].replace(
            "github.com", "untrusted.example.com"
        )
    elif fault == "traversal":
        data["entries"][0]["filename"] = "../original-source.tar.gz"
    elif fault == "forged_identity":
        report["archives"][0]["id"] = "other-library"
        (dest / "supplemental-source-report.json").write_text(json.dumps(report))
    cat.write_text(json.dumps(data))
    with pytest.raises((ValueError, FileNotFoundError)):
        verify_prepared(cat, dest)


def test_catalog_only_accepts_pinned_https_official_sources(tmp_path):
    _, _, data = fixture(tmp_path)
    assert len(validate_catalog(data)) == 1
    data["entries"][0]["sha256"] = "unknown"
    with pytest.raises(ValueError):
        validate_catalog(data)


def test_git_tag_url_basename_can_differ_from_local_source_archive(tmp_path):
    _, _, source = fixture(tmp_path)
    entry = source["entries"][0]
    entry["filename"] = "zlib-ng-2.3.3.tar.gz"
    entry["url"] = "https://github.com/zlib-ng/zlib-ng/archive/refs/tags/2.3.3.tar.gz"
    entry["url_filename"] = "2.3.3.tar.gz"
    assert len(validate_catalog(source)) == 1
    entry["url_filename"] = "../2.3.3.tar.gz"
    with pytest.raises(ValueError, match="upstream source URL filename"):
        validate_catalog(source)
    entry["url_filename"] = "another-version.tar.gz"
    with pytest.raises(ValueError, match="Unapproved supplemental source origin"):
        validate_catalog(source)
