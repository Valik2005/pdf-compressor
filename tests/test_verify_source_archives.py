"""Offline tests for a fail-closed source evidence catalog."""
import hashlib
import importlib.util
from pathlib import Path

import pytest


def lib():
    path = Path(__file__).resolve().parents[1] / "tools" / "verify_source_archives.py"
    spec = importlib.util.spec_from_file_location("verify_source_archives", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def item(name, digest, required=True):
    return {
        "id": name, "version": "1.0", "filename": name,
        "url": "https://example.test/source/" + name,
        "expected_sha256": digest, "required": required,
    }


def test_catalog_required_source_valid_hash(tmp_path):
    module = lib()
    path = tmp_path / "a.tar.gz"
    contents = b"license-safe-source-fixture"
    path.write_bytes(contents)
    digest = hashlib.sha256(contents).hexdigest()
    report = module.audit_sources({"schema_version": 1, "entries": [item(path.name, digest)]}, tmp_path)
    assert report["all_required_with_published_hashes"]
    assert report["archives"][0]["status"] == "hash_matches_published_value"
    assert report["archives"][0]["source_completeness_and_binary_correspondence_verified"] is False


def test_mismatched_source_rejected(tmp_path):
    module = lib()
    path = tmp_path / "a.tar.gz"
    path.write_bytes(b"tampered")
    report = module.audit_sources({"schema_version": 1, "entries": [item(path.name, "0"*64)]}, tmp_path)
    assert report["archives"][0]["status"] == "HASH_MISMATCH"
    assert not report["all_required_with_published_hashes"]


def test_missing_checksum_is_not_verified(tmp_path):
    module = lib()
    path = tmp_path / "source.tar.xz"
    path.write_bytes(b"downloaded but no upstream hash")
    report = module.audit_sources({"schema_version": 1, "entries": [item(path.name, None)]}, tmp_path)
    assert report["archives"][0]["status"] == "hash_recorded_but_not_authoritatively_verified"
    assert not report["all_required_with_published_hashes"]


def test_missing_source_is_not_a_pass(tmp_path):
    module = lib()
    report = module.audit_sources({"schema_version": 1, "entries": [item("x.tar.xz", "0"*64)]}, tmp_path)
    assert report["archives"][0]["status"] == "not_acquired"
    assert not report["all_required_with_published_hashes"]


@pytest.mark.parametrize("name", ["../secret", "/etc/LICENSE", "..", "dir/file.tar.gz"])
def test_unsafe_names_rejected(name):
    module = lib()
    data = {"schema_version": 1, "entries": [item(name, "0"*64)]}
    with pytest.raises(ValueError):
        module.validate_catalog(data)


def test_catalog_refuses_duplicate_names(tmp_path):
    module = lib()
    a = item("x.tar.gz", "0"*64)
    b = item("x.tar.gz", "0"*64)
    b["id"] = "different-id"
    with pytest.raises(ValueError, match="Duplicate"):
        module.validate_catalog({"schema_version": 1, "entries": [a, b]})
