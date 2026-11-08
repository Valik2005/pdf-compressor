"""Fetch version-pinned upstream source archives for later release review.

No publishing. Only pinned HTTPS origins. A downloaded archive alone is not
proof it is complete corresponding source for the binary that was packaged.
"""
from __future__ import annotations

import argparse
import hashlib
from html import unescape
import json
from pathlib import Path
import re
import urllib.parse
import urllib.request

ALLOWED_HOSTS = {"download.qt.io", "files.pythonhosted.org"}
SHA256_RE = re.compile(r"SHA-256\s+Hash\s*:\s*([a-fA-F0-9]{64})", re.I)
MAX_SIZE = 600 * 1024 * 1024


def fetch(url: str, dest: Path, *, max_bytes: int = MAX_SIZE) -> str:
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
        raise ValueError(f"Untrusted source host: {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "PDFCompressor-release-source-audit/2.7"})
    h = hashlib.sha256()
    total = 0
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urllib.request.urlopen(req, timeout=150) as response, dest.open("wb") as out:
            redirected = urllib.parse.urlsplit(response.geturl())
            # Qt's official mirror redirects are permitted for binary archives;
            # the exact SHA-256 still must match a trusted upstream value.
            if redirected.scheme != "https":
                raise ValueError("Source download redirected to non-HTTPS")
            for chunk in iter(lambda: response.read(1024 * 1024), b""):
                total += len(chunk)
                if total > max_bytes:
                    raise ValueError("Archive exceeds maximum expected size")
                h.update(chunk)
                out.write(chunk)
    except Exception:
        dest.unlink(missing_ok=True)
        raise
    if not total:
        dest.unlink(missing_ok=True)
        raise ValueError("Empty source archive")
    return h.hexdigest()


def parse_qt_mirrorlist_sha256(text: str) -> str | None:
    cleaned = re.sub(r"<[^>]+>", " ", unescape(text))
    found = SHA256_RE.search(cleaned)
    return found.group(1).lower() if found else None


def official_digest(url: str, temp: Path) -> str | None:
    parsed = urllib.parse.urlsplit(url)
    if parsed.hostname != "download.qt.io" or not parsed.path.endswith(".mirrorlist"):
        return None
    fetch(url, temp, max_bytes=256_000)
    return parse_qt_mirrorlist_sha256(temp.read_text(encoding="utf-8", errors="replace"))


def acquire(catalog_path: Path, out_dir: Path) -> dict:
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    entries = catalog.get("entries", [])
    out_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for entry in entries:
        if not entry.get("required"):
            continue
        filename = entry["filename"]
        if Path(filename).name != filename or filename in (".", ".."):
            raise ValueError(f"Unsafe filename: {filename}")
        record = {"id": entry["id"], "filename": filename, "url": entry["url"],
                  "expected_sha256": entry.get("expected_sha256"), "status": "pending"}
        try:
            digest = entry.get("expected_sha256")
            if not digest and entry.get("checksum_source"):
                digest = official_digest(entry["checksum_source"], out_dir / "_qt-mirrorlist.tmp")
            record["trusted_expected_sha256"] = digest
            actual = fetch(entry["url"], out_dir / filename)
            record["downloaded_sha256"] = actual
            if not digest:
                record["status"] = "UNVERIFIED_NO_OFFICIAL_CHECKSUM"
            elif actual.lower() != digest.lower():
                (out_dir / filename).unlink(missing_ok=True)
                record["status"] = "HASH_MISMATCH"
            else:
                record["status"] = "hash_matches_official_source"
        except Exception as exc:
            record["status"] = "DOWNLOAD_OR_CHECKSUM_ERROR"
            record["error"] = str(exc)[:300]
        finally:
            (out_dir / "_qt-mirrorlist.tmp").unlink(missing_ok=True)
        results.append(record)
    report = {
        "schema_version": 1,
        "all_required_archives_verified": bool(results) and all(
            item["status"] == "hash_matches_official_source" for item in results),
        "full_binary_correspondence_or_legal_compliance_established": False,
        "archives": results,
    }
    (out_dir / "source-download-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--catalog", type=Path, default=Path("docs/source-archives-2_7.json"))
    p.add_argument("--out-dir", type=Path, default=Path("dist/source-candidates"))
    p.add_argument("--require-all", action="store_true")
    args = p.parse_args()
    report = acquire(args.catalog, args.out_dir)
    for entry in report["archives"]:
        print(entry["id"], entry["status"])
    if args.require_all and not report["all_required_archives_verified"]:
        p.exit(2, "Required source archive acquisition/verification is incomplete.\n")


if __name__ == "__main__":
    main()
