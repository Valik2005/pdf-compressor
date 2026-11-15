"""Unit tests for source checksum extraction and pinned source URL trust."""
from pathlib import Path
import hashlib
import json
import pytest

from tools.fetch_required_sources import parse_qt_mirrorlist_sha256, fetch, acquire


def test_official_qt_mirrorlist_sha256():
    digest = "a951bd163c7b80fc6b8c88d7668fb56abf91c152373e13c10666763238131307"
    snippet = f"<html><li>SHA-256 Hash: <code>{digest}</code></li></html>"
    assert parse_qt_mirrorlist_sha256(snippet) == digest


def test_qt_mirrorlist_with_missing_hash_is_unverified():
    assert parse_qt_mirrorlist_sha256("<body>No published checksum</body>") is None


@pytest.mark.parametrize("url", [
    "https://example.com/pyside.tar.xz",
    "http://download.qt.io/a.tar.xz",
    "file:///tmp/archive.tar.xz",
])
def test_untrusted_sources_rejected_before_network(tmp_path: Path, url: str):
    with pytest.raises(ValueError, match="Untrusted"):
        fetch(url, tmp_path / "archive.tar.xz")

def test_acquire_retries_transient_transfer_but_verifies_pinned_bytes(tmp_path, monkeypatch):
    payload = b"synthetic source archive fixture"
    digest = hashlib.sha256(payload).hexdigest()
    catalog = tmp_path / "catalog.json"
    catalog.write_text(json.dumps({
        "entries": [{"id": "qtimageformats", "filename": "qtimageformats.tar.xz",
                     "url": "https://download.qt.io/fixture/qtimageformats.tar.xz",
                     "expected_sha256": digest, "required": True}]
    }), encoding="utf-8")
    attempts = []

    def flaky(url, destination, **kwargs):
        attempts.append(url)
        if len(attempts) < 3:
            raise OSError("temporary source mirror connection drop")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(payload)
        return hashlib.sha256(destination.read_bytes()).hexdigest()

    monkeypatch.setattr("tools.fetch_required_sources.fetch", flaky)
    monkeypatch.setattr("tools.fetch_required_sources.time.sleep", lambda seconds: None)
    result = acquire(catalog, tmp_path / "out")
    assert result["all_required_archives_verified"] is True
    assert result["archives"][0]["status"] == "hash_matches_official_source"
    assert len(attempts) == 3


def test_acquire_never_accepts_hash_mismatch_after_retry(tmp_path, monkeypatch):
    catalog = tmp_path / "catalog.json"
    catalog.write_text(json.dumps({
        "entries": [{"id": "qtsvg", "filename": "qtsvg.tar.xz",
                     "url": "https://download.qt.io/fixture/qtsvg.tar.xz",
                     "expected_sha256": "0" * 64, "required": True}]
    }), encoding="utf-8")
    attempts = []

    def wrong_hash(url, destination, **kwargs):
        attempts.append(url)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(b"incorrect version")
        return hashlib.sha256(b"incorrect version").hexdigest()

    monkeypatch.setattr("tools.fetch_required_sources.fetch", wrong_hash)
    result = acquire(catalog, tmp_path / "out")
    assert result["all_required_archives_verified"] is False
    assert result["archives"][0]["status"] == "DOWNLOAD_OR_CHECKSUM_ERROR"
    assert len(attempts) == 1
    assert not (tmp_path / "out" / "qtsvg.tar.xz").exists()
