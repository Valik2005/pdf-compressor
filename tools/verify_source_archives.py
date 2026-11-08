"""Verify locally acquired source archives against a reviewed source catalog.

No network requests and no claims of redistribution compliance.
An archive can have a valid hash yet still be INSUFFICIENT corresponding
source for the exact binary; the status always retains that warning.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as src:
        for chunk in iter(lambda: src.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_catalog(catalog: dict) -> None:
    if catalog.get("schema_version") != 1:
        raise ValueError("Unsupported source catalog version")
    seen_names = set()
    seen_ids = set()
    entries = catalog.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ValueError("No source catalog entries")
    for entry in entries:
        name = entry.get("filename")
        ident = entry.get("id")
        url = entry.get("url", "")
        if (not isinstance(name, str) or not name or Path(name).name != name
                or "/" in name or "\\" in name or name in (".", "..")):
            raise ValueError(f"Unsafe source filename: {name}")
        if not isinstance(ident, str) or not ident or ident in seen_ids:
            raise ValueError("Duplicate or missing source id")
        seen_ids.add(ident)
        if name in seen_names:
            raise ValueError("Duplicate source filename")
        seen_names.add(name)
        parsed = urlparse(url)
        if parsed.scheme != "https" or not parsed.netloc or parsed.path.rsplit("/", 1)[-1] != name:
            raise ValueError(f"Unverified source origin for {name}")
        expected = entry.get("expected_sha256")
        if expected is not None and (not isinstance(expected, str) or len(expected) != 64
                                     or any(c not in "0123456789abcdef" for c in expected.lower())):
            raise ValueError(f"Invalid SHA-256 in catalog for {name}")
        if not isinstance(entry.get("required"), bool):
            raise ValueError(f"Source archive required flag missing for {name}")


def audit_sources(catalog: dict, source_dir: Path) -> dict:
    validate_catalog(catalog)
    items = []
    for entry in catalog["entries"]:
        name = entry["filename"]
        path = source_dir / name
        exists = path.is_file() and not path.is_symlink()
        digest = sha256(path) if exists else None
        expected = entry.get("expected_sha256")
        if not exists:
            status = "not_acquired"
        elif expected is None:
            status = "hash_recorded_but_not_authoritatively_verified"
        elif digest != expected.lower():
            status = "HASH_MISMATCH"
        else:
            status = "hash_matches_published_value"
        items.append({
            "id": entry["id"], "version": entry["version"],
            "filename": name, "required": entry["required"],
            "present": exists, "local_sha256": digest,
            "published_expected_sha256": expected, "status": status,
            "original_source_url": entry["url"],
            "source_completeness_and_binary_correspondence_verified": False,
        })
    return {
        "schema_version": 1,
        "status": "TECHNICAL SOURCE ARCHIVE EVIDENCE; LICENSE COMPLIANCE UNVERIFIED",
        "archives": items,
        "all_required_with_published_hashes": all(
            item["status"] == "hash_matches_published_value"
            for item in items if item["required"]
        ),
        "blocking_review_items": [
            "Obtain/verify checksums for every required upstream source archive.",
            "Audit applicability of Qt PDF/PDFium, native MuPDF and other transitive sources to bundled DLLs.",
            "Maintain copies/control of corresponding sources or implement a legally sufficient offer.",
            "Provide full LGPL/GPL/AGPL license notices, modification/relinking instructions and compliance review.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=Path("docs/source-archives-2_7.json"))
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=Path("dist/source-evidence-report.json"))
    parser.add_argument("--require-all-verified", action="store_true")
    args = parser.parse_args()
    try:
        catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
        result = audit_sources(catalog, args.source_dir)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.exit(1, f"Source evidence audit error: {exc}\n")
    for item in result["archives"]:
        print(item["filename"], ":", item["status"])
    print("All required hashes verified:", result["all_required_with_published_hashes"])
    print("Warning: matching hashes DO NOT prove source-code or license compliance.")
    return 2 if args.require_all_verified and not result["all_required_with_published_hashes"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
