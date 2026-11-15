"""Record the actual PyInstaller Analysis source file for every bundled native entry.

Run INSIDE the spec after Qt pruning, before EXE creation. Keep sensitive
absolute builder paths out of artifacts. Source-file identity does not grant
permission to redistribute a binary or prove corresponding-source equivalence.
"""
from __future__ import annotations

from collections import Counter
import base64
import hashlib
from importlib import metadata
import json
import os
from pathlib import Path
import sys


WHEELS = ("PyMuPDF", "PySide6", "PySide6_Essentials", "PySide6_Addons",
          "shiboken6", "Pillow")


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def wheel_locations() -> dict[Path, dict]:
    """Use dist-info RECORD *paths*, not guessed DLL file name ownership."""
    known = {}
    for package in WHEELS:
        try:
            dist = metadata.distribution(package)
        except metadata.PackageNotFoundError:
            continue
        for item in dist.files or ():
            rel = str(item).replace("\\", "/")
            if not rel.lower().endswith((".dll", ".pyd")):
                continue
            path = Path(dist.locate_file(item)).resolve()
            record_sha = None
            if item.hash and item.hash.mode == "sha256":
                encoded = item.hash.value
                record_sha = base64.urlsafe_b64decode(
                    encoded + "=" * (-len(encoded) % 4)
                ).hex()
            known[path] = {"scope": "installed-wheel", "distribution": package,
                           "version": dist.version, "relative_path": rel,
                           "record_sha256": record_sha}
    return known


def scope_for(path: Path, known: dict) -> dict:
    if path in known:
        return dict(known[path])
    for base in (sys.base_prefix, sys.prefix):
        root = Path(base).resolve()
        if path.is_relative_to(root):
            return {"scope": "python-installation",
                    "relative_path": path.relative_to(root).as_posix()}
    windir = os.environ.get("SystemRoot") or os.environ.get("WINDIR")
    if windir and path.is_relative_to(Path(windir).resolve()):
        return {"scope": "windows-system",
                "relative_path": path.name}
    for key in ("ProgramFiles(x86)", "ProgramFiles"):
        root = os.environ.get(key)
        if root and path.is_relative_to(Path(root).resolve()):
            parts = path.relative_to(Path(root).resolve()).parts
            # Program Files paths are machine-wide and contain no account
            # names. Keep the *relative* path so a reviewer can distinguish
            # e.g. Git/OpenSSL/Visual Studio and the actual SDK Redist tree.
            # Never emit the absolute Program Files root.
            relative = "/".join(parts)
            if len(parts) >= 2 and parts[0].lower() == "windows kits":
                return {"scope": "windows-sdk", "relative_path": relative}
            return {"scope": "installed-program", "relative_path": relative}
    return {"scope": "unclassified-builder-path", "relative_path": path.name}


def load_recipient_qt_replacements(manifest_path: Path) -> dict[str, dict]:
    """Only permit separately declared, SHA-verified recipient Qt wheel changes.

    This is an exception for rebuilding with LGPL-modified compatible libraries.
    Never used by the official unsigned release; normal wheel RECORD checks
    remain fail closed. The manifest must be written by the recipient rebuild
    tool after copying the verified override bytes into its isolated wheel.
    """
    data = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    rows = data.get("recipient_modified_qt_libraries")
    if (data.get("schema_version") != 1 or data.get("scope") != "recipient-relink"
            or not isinstance(rows, list) or not rows):
        raise ValueError("Invalid recipient Qt override manifest")
    expected = {}
    hexdigits = set("0123456789abcdef")
    for row in rows:
        if not isinstance(row, dict) or set(row) != {
                "path", "original_sha256", "replacement_sha256"}:
            raise ValueError("Invalid recipient Qt override record")
        path = row["path"]
        if (not isinstance(path, str) or not path.startswith("PySide6/")
                or chr(92) in path or ".." in path.split("/")
                or not path.lower().endswith((".dll", ".pyd"))
                or path in expected):
            raise ValueError("Unsafe or duplicate recipient Qt override path")
        for key in ("original_sha256", "replacement_sha256"):
            hash_value = row[key]
            if (not isinstance(hash_value, str) or len(hash_value) != 64
                    or any(ch not in hexdigits for ch in hash_value)):
                raise ValueError("Invalid recipient Qt override SHA-256")
        if row["original_sha256"] == row["replacement_sha256"]:
            raise ValueError("Recipient Qt override must change exact bytes")
        expected[path] = dict(row)
    return expected


def capture(binaries, datas, out: Path, source_sha: str | None = None,
            known: dict | None = None,
            recipient_qt_replacements: dict[str, dict] | None = None) -> dict:
    wheel_index = wheel_locations() if known is None else known
    approved = recipient_qt_replacements or {}
    if recipient_qt_replacements is not None and not isinstance(approved, dict):
        raise ValueError("Recipient Qt override inventory must be a mapping")
    seen_approved = set()
    rows = {}
    for entry in list(binaries) + list(datas):
        if len(entry) < 2:
            raise ValueError("Invalid PyInstaller Analysis item")
        destination = str(entry[0]).replace("\\", "/")
        if not destination.lower().endswith((".dll", ".pyd")):
            continue
        if (not destination or destination.startswith("/")
                or ".." in destination.split("/") or destination in rows):
            raise ValueError(f"Duplicate or unsafe PyInstaller native member: {destination}")
        path = Path(entry[1])
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"Invalid collected native source: {destination}")
        path = path.resolve()
        origin = scope_for(path, wheel_index)
        sha = digest(path)
        wheel_record = origin.pop("record_sha256", None)
        is_relinked = False
        wheel_scope = origin["scope"] == "installed-wheel"
        if destination in approved:
            candidate = approved[destination]
            if (not wheel_scope
                    or not destination.startswith("PySide6/")
                    or not origin["relative_path"].replace(chr(92), "/") == destination
                    or not wheel_record
                    or wheel_record != candidate.get("original_sha256")
                    or sha != candidate.get("replacement_sha256")
                    or origin.get("distribution") not in {
                        "PySide6", "PySide6_Essentials", "PySide6_Addons"
                    }
                    or wheel_record == sha):
                raise ValueError(f"Recipient Qt source/RECORD replacement mismatch: {destination}")
            is_relinked = True
            seen_approved.add(destination)
        elif wheel_scope and wheel_record is not None and wheel_record != sha:
            raise ValueError(f"Installed wheel RECORD disagrees for {destination}")
        rows[destination] = {
            "path": destination,
            "source_sha256": sha,
            "size_bytes": path.stat().st_size,
            "source_scope": origin["scope"],
            "source_relative_path": origin["relative_path"],
            "distribution": origin.get("distribution"),
            "distribution_version": origin.get("version"),
            "wheel_record_matched": wheel_record == sha if wheel_record else None,
            "recipient_modified_qt": is_relinked,
        }
    if not rows:
        raise ValueError("No native files in collected PyInstaller Analysis")
    if seen_approved != set(approved):
        raise ValueError("Recipient Qt replacement manifest includes missing native members")
    report = {
        "schema_version": 1,
        "source_git_commit": source_sha,
        "native_file_count": len(rows),
        "source_scope_counts": dict(sorted(Counter(
            row["source_scope"] for row in rows.values()
        ).items())),
        "entries": list(rows.values()),
        "redistribution_rights_verified": False,
        "recipient_qt_relink": bool(seen_approved),
        "recipient_modified_qt_count": len(seen_approved),
        "note": "Actual build-stage source SHA/relative scope only. Not an OSS legal certification.",
    }
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("Native collection source scopes:", report["source_scope_counts"])
    return report
