"""Offline verification of exact Git commit/tree source material for libyuv."""
from __future__ import annotations

import io
import json
from pathlib import Path
import tarfile

import pytest

from tools.prepare_libyuv_git_source_28 import (
    FILENAME, REPORT, REVISION, TREE, archive_review, digest, verify_prepared,
)


def make_source(tmp_path: Path) -> tuple[Path, dict]:
    file = tmp_path / FILENAME
    with tarfile.open(file, "w") as out:
        for i in range(65):
            name = "LICENSE" if i == 0 else f"source/file_{i:04d}.cc"
            contents = (name + "\n" + "example source content " * 25).encode()
            info = tarfile.TarInfo(name)
            info.size = len(contents)
            out.addfile(info, io.BytesIO(contents))
    manifest = {
        "schema_version": 1, "git_commit_sha1": REVISION,
        "git_tree_sha1": TREE, "archive": FILENAME,
        "archive_sha256": digest(file),
        "archive_source_file_count": 65,
        "source_correspondence_to_vendor_binary_proven": False,
        "legal_compliance_certified": False,
    }
    (tmp_path / REPORT).write_text(json.dumps(manifest))
    return file, manifest


def test_pinned_git_tree_archive_and_manifest(tmp_path):
    _, manifest = make_source(tmp_path)
    assert verify_prepared(tmp_path)["archive_sha256"] == manifest["archive_sha256"]


@pytest.mark.parametrize("fault", [
    "bad_sha", "wrong_commit", "wrong_tree", "legal_claim",
    "not_corresponding_source", "truncated", "missing_license"
])
def test_reject_forged_or_incomplete_git_source_evidence(tmp_path, fault):
    file, manifest = make_source(tmp_path)
    if fault == "bad_sha":
        manifest["archive_sha256"] = "0" * 64
    elif fault == "wrong_commit":
        manifest["git_commit_sha1"] = "0" * 40
    elif fault == "wrong_tree":
        manifest["git_tree_sha1"] = "0" * 40
    elif fault == "legal_claim":
        manifest["legal_compliance_certified"] = True
    elif fault == "not_corresponding_source":
        manifest["source_correspondence_to_vendor_binary_proven"] = True
    elif fault == "truncated":
        file.write_bytes(b"bad")
    elif fault == "missing_license":
        file.unlink()
        with tarfile.open(file, "w") as tar:
            for i in range(65):
                payload = b"some-contents" * 50
                entry = tarfile.TarInfo(f"source/file_{i:04d}.cc")
                entry.size = len(payload)
                tar.addfile(entry, io.BytesIO(payload))
        manifest["archive_sha256"] = digest(file)
    (tmp_path / REPORT).write_text(json.dumps(manifest))
    with pytest.raises(ValueError):
        verify_prepared(tmp_path)
