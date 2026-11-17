"""Preserve upstream libyuv sources by immutable Git commit AND Git tree.

libavif 1.4.2's ext/libyuv.cmd explicitly pins this revision. Git object IDs,
not tag labels or filenames, establish the exact original source tree.
The GitHub repository is a mirror of Chromium's official libyuv Git source;
the expected commit is independently referenced by Chromium's own DEPS.
This does not prove the vendor-built Pillow library used unmodified libyuv.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile
import tempfile

REVISION = "644251f252a84bf8ce91ff0aca86a9b16b069ab8"
TREE = "ba22b636166dc16532fcc9d5a9524117432d1782"
MIRROR = "https://github.com/lemenkov/libyuv.git"
FILENAME = "libyuv-" + REVISION + ".tar"
REPORT = "libyuv-git-source-report.json"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def git(cwd: Path, *args: str) -> str:
    p = subprocess.run(
        ["git", "-C", str(cwd), *args],
        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, timeout=120
    )
    return p.stdout.strip()


def archive_review(path: Path) -> int:
    if not path.is_file() or path.is_symlink() or path.stat().st_size < 40_000:
        raise ValueError("Missing or abnormally small pinned libyuv source archive")
    with tarfile.open(path, "r:") as tar:
        members = tar.getmembers()
        names = {m.name for m in members if m.isfile()}
        if (len(names) < 50 or not any(n.endswith("LICENSE") for n in names)
                or not any(n.startswith("source/") for n in names)):
            raise ValueError("Pinned libyuv source archive lacks the expected source/license tree")
    return len(names)


def acquire(outdir: Path) -> dict:
    outdir.mkdir(parents=True, exist_ok=True)
    final = outdir / FILENAME
    if final.exists():
        raise ValueError("Refusing to overwrite pinned Git source archive")
    with tempfile.TemporaryDirectory() as tmp:
        checkout = Path(tmp)
        git(checkout, "init", "-q")
        git(checkout, "remote", "add", "origin", MIRROR)
        git(checkout, "-c", "protocol.version=2", "fetch", "-q", "--no-tags", "--depth=1", "origin", REVISION)
        git(checkout, "checkout", "-q", "--detach", "FETCH_HEAD")
        if git(checkout, "rev-parse", "HEAD") != REVISION:
            raise ValueError("libyuv source revision mismatch")
        if git(checkout, "rev-parse", "HEAD^{tree}") != TREE:
            raise ValueError("libyuv original Git tree mismatch")
        git(checkout, "archive", "--format=tar", "--output=" + str(final), REVISION)
    count = archive_review(final)
    report = {
        "schema_version": 1,
        "source": "Chromium libyuv Git; commit-verified mirror snapshot",
        "upstream_git_url": "https://chromium.googlesource.com/libyuv/libyuv",
        "mirror": MIRROR,
        "git_commit_sha1": REVISION,
        "git_tree_sha1": TREE,
        "archive": FILENAME,
        "archive_sha256": digest(final),
        "archive_source_file_count": count,
        "source_correspondence_to_vendor_binary_proven": False,
        "legal_compliance_certified": False,
    }
    (outdir / REPORT).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def verify_prepared(outdir: Path) -> dict:
    r = json.loads((outdir / REPORT).read_text(encoding="utf-8"))
    if (r.get("schema_version") != 1 or r.get("git_commit_sha1") != REVISION
            or r.get("git_tree_sha1") != TREE or r.get("archive") != FILENAME
            or r.get("source_correspondence_to_vendor_binary_proven") is not False
            or r.get("legal_compliance_certified") is not False):
        raise ValueError("Incorrect upstream libyuv Git identity or certification claim")
    p = outdir / FILENAME
    if digest(p) != r.get("archive_sha256"):
        raise ValueError("Pinned libyuv source archive SHA-256 mismatch")
    if archive_review(p) != r.get("archive_source_file_count"):
        raise ValueError("Pinned libyuv file list mismatches source report")
    return r


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out-dir", required=True, type=Path)
    args = p.parse_args()
    r = acquire(args.out_dir)
    print("Verified original libyuv Git source tree:", r["git_tree_sha1"])
    print("Pinned libyuv source archive SHA-256:", r["archive_sha256"])


if __name__ == "__main__":
    main()
