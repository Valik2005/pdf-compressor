"""Acquire optional v2.8 *verified original* sources for bundled native runtimes.

This supplies full CPython/OpenSSL/libffi source archives beside their licenses.
Matching an upstream SHA-256 is NOT proof of wheel compiler flags or legal
compliance. All connections must begin at a pinned official HTTPS URL.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import urllib.parse
import urllib.request

ALLOWED_HOSTS = frozenset({"www.python.org", "github.com", "files.pythonhosted.org", "storage.googleapis.com"})
SHA256 = re.compile(r"^[a-f0-9]{64}$")
MAX_FILE_SIZE = 110 * 1024 * 1024


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def validate_catalog(catalog: dict) -> list[dict]:
    if catalog.get("schema_version") != 1:
        raise ValueError("Invalid supplemental source catalog schema")
    rows = catalog.get("entries")
    if not isinstance(rows, list) or not rows:
        raise ValueError("No supplemental source entries")
    seen = set()
    for row in rows:
        ident, name, url, sha = (
            row.get("id"), row.get("filename"), row.get("url"), row.get("sha256")
        )
        if not isinstance(ident, str) or not ident or ident in seen:
            raise ValueError("Missing/duplicate supplemental source component id")
        if (not isinstance(name, str) or not name
                or Path(name).name != name or "/" in name or "\\" in name
                or name.startswith(".")):
            raise ValueError("Unsafe supplemental source archive filename")
        if not isinstance(sha, str) or not SHA256.fullmatch(sha):
            raise ValueError("Supplemental source lacks published SHA-256")
        parsed = urllib.parse.urlsplit(url) if isinstance(url, str) else None
        if (parsed is None or parsed.scheme != "https"
                or parsed.hostname not in ALLOWED_HOSTS
                or parsed.path.rsplit("/", 1)[-1] != name
                or parsed.username or parsed.password or parsed.query):
            raise ValueError("Unapproved supplemental source origin: " + str(url))
        seen.add(ident)
    return rows


def acquire(catalog_path: Path, dest: Path) -> dict:
    rows = validate_catalog(json.loads(catalog_path.read_text(encoding="utf-8")))
    dest.mkdir(parents=True, exist_ok=True)
    results = []
    for row in rows:
        file = dest / row["filename"]
        wanted = row["sha256"]
        if file.exists() and (file.is_symlink() or not file.is_file()):
            raise ValueError("Invalid previously downloaded source file: " + file.name)
        if file.is_file() and sha256_file(file) != wanted:
            raise ValueError("Existing supplemental source archive has wrong digest: " + file.name)
        if not file.exists():
            temporary = dest / (file.name + ".part")
            if temporary.is_symlink():
                raise ValueError("Unsafe temporary source download")
            try:
                request = urllib.request.Request(
                    row["url"], headers={"User-Agent":"PDFCompressor-source-integrity/2.8"}
                )
                h = hashlib.sha256()
                size = 0
                with urllib.request.urlopen(request, timeout=90) as response:
                    if urllib.parse.urlsplit(response.url).scheme != "https":
                        raise ValueError("Insecure upstream source redirect")
                    with temporary.open("wb") as out:
                        while block := response.read(2 * 1024 * 1024):
                            size += len(block)
                            if size > MAX_FILE_SIZE:
                                raise ValueError("Unexpectedly large supplemental source")
                            h.update(block)
                            out.write(block)
                if size == 0 or h.hexdigest() != wanted:
                    raise ValueError("Supplemental source does not match official SHA-256")
                temporary.replace(file)
            finally:
                temporary.unlink(missing_ok=True)
        results.append({
            "id": row["id"], "version": row["version"],
            "filename": file.name, "sha256": sha256_file(file),
            "status": "verified_original_upstream_release",
            "exact_binary_build_correspondence_verified": False,
        })
    return {
        "schema_version": 1,
        "archives": results,
        "source_archives_verified": len(results),
        "all_hashes_verified": True,
        "exact_native_build_correspondence_verified": False,
        "license_compliance_certified": False,
    }



def verify_prepared(catalog_path: Path, dest: Path) -> list[dict]:
    """Independently verify downloaded source bytes and preflight inventory.

    This is used again by the packaging and native-coverage audit, not merely
    accepted because a download earlier printed an OK message.
    """
    rows = validate_catalog(json.loads(catalog_path.read_text(encoding="utf-8")))
    report_path = dest / "supplemental-source-report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    recorded = report.get("archives")
    if (report.get("schema_version") != 1
            or report.get("all_hashes_verified") is not True
            or report.get("license_compliance_certified") is not False
            or not isinstance(recorded, list)
            or len(recorded) != len(rows)):
        raise ValueError("Invalid supplemental source download report")
    by_id = {item.get("id"): item for item in recorded}
    if len(by_id) != len(rows):
        raise ValueError("Repeated supplemental source records")
    for row in rows:
        path = dest / row["filename"]
        record = by_id.get(row["id"], {})
        if (not path.is_file() or path.is_symlink()
                or sha256_file(path) != row["sha256"]
                or record.get("sha256") != row["sha256"]
                or record.get("filename") != row["filename"]
                or record.get("version") != row["version"]
                or record.get("status") != "verified_original_upstream_release"
                or record.get("exact_binary_build_correspondence_verified") is not False):
            raise ValueError("Supplemental source archive/report mismatch: " + row["id"])
    return rows


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--catalog", required=True, type=Path)
    p.add_argument("--out-dir", required=True, type=Path)
    p.add_argument("--out-report", required=True, type=Path)
    args = p.parse_args()
    report = acquire(args.catalog, args.out_dir)
    args.out_report.parent.mkdir(parents=True, exist_ok=True)
    args.out_report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("Verified supplemental source archives:", report["source_archives_verified"])


if __name__ == "__main__":
    main()
