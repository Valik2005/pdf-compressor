"""Unit tests for source checksum extraction and pinned source URL trust."""
from pathlib import Path
import pytest

from tools.fetch_required_sources import parse_qt_mirrorlist_sha256, fetch


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
